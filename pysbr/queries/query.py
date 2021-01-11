from string import Template
import copy
import typing
from typing import Callable, Any, Dict, Optional, List, Union
from functools import wraps

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import pandas as pd

import pysbr.utils as utils
from pysbr.config.config import Config


class Query:
    """Base class for making queries on the SBR GraphQL endpoint.

    This class should not be directly instantiated; use the subclasses defined for each
    query.
    """

    def __init__(self):
        self._config = Config()

        self._raw = None
        self._subpath_keys = None
        self._sublist_keys = None
        self._id_key = None

        self._translated = None

        self._arguments = utils.load_yaml((utils.build_yaml_path("arguments")))
        self._fields = utils.load_yaml((utils.build_yaml_path("fields")))

        transport = RequestsHTTPTransport(
            url="https://www.sportsbookreview.com/ms-odds-v2/odds-v2-service"
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=False)

    def typecheck(f: Callable) -> Callable:
        """Decorator for type checking arguments passed to subclass __init__ methods.

        The purpose of decorating the subclass __init__ methods is to avoid making
        invalid queries on the GraphQL endpoint.

        This method is only verified to work with List, Union, and primitive types.

        Raises:
            TypeError: If argument does not match expected type.
        """

        def recurse(a: Any, t: Dict) -> bool:
            """Method for recursively validating nested types."""
            t_origin = typing.get_origin(t)
            t_args = typing.get_args(t)

            if t_origin is None and len(t_args) == 0:
                if not isinstance(a, t):
                    return False

            elif isinstance(t_origin, type(list)):
                if not isinstance(a, list):
                    return False
                if len(t_args) > 0:
                    try:
                        for x in a:
                            for arg in t_args:
                                if not recurse(x, arg):
                                    return False
                    except TypeError:
                        return False
                else:
                    if not isinstance(a, t_origin):
                        return False

            elif isinstance(t_origin, typing._SpecialForm):
                for arg in t_args:
                    is_arg = recurse(a, arg)
                    if is_arg:
                        return True
                return False

            return True

        @wraps(f)
        def wrapper(*args: Any) -> Any:
            """Wrapper returned by the decorator, wrapping the function argument."""
            types = list(typing.get_type_hints(f).values())
            # first argument is self, ignore it
            for a, t in zip(args[1:], types):
                valid = recurse(a, t)
                if not valid:
                    raise TypeError(f"Expected {t}, got {a}")

            f(*args)

        return wrapper

    def _build_args(self, arg_str: str, args: Dict[str, Any]) -> Optional[str]:
        """Build the argument string that gets inserted into a query string.

        arg_str should be a string with substitution placeholders matching each arg in
        args.

        Raises:
            KeyError: If keys in args do not match placeholders in arg_str.
            ValueError: If arg_str is not a valid Template string.
        """
        if arg_str is not None and args is not None:
            return Template(arg_str).substitute(args)
        else:
            return None

    def _build_query_string(
        self, q_name: str, q_fields: Optional[str] = None, q_args: Optional[str] = None
    ) -> str:
        """Build up the GraphQL query string from given parameters.

        q_args should be the arguments to the query, with the values already filled in
        (i.e. query._build_args() should be called first).

        Returns:
            The completed query string ready to be executed.
        """
        return (
            Template(
                utils.str_format(
                    """
                query {
                    $q_name(
                        $q_args
                    ) $q_fields
                }
            """
                )
            ).substitute(
                {
                    "q_name": q_name,
                    "q_args": ""
                    if q_args is None
                    else utils.str_format(q_args, indent_=2, dedent_l1=True),
                    "q_fields": ""
                    if q_fields is None
                    else utils.str_format(q_fields, indent_=1, dedent_l1=True),
                }
            )
            # graphql query will not accept single quotes, but Template string by
            # default uses single quotes
            .replace("'", '"')
        )

    def _get_args(self, k: str) -> str:
        """Get the value of key k from the arguments dictionary.

        Raises:
            KeyError: If k is not a key in the arguments dict.
        """
        return self._arguments[k]

    def _get_fields(self, k: str) -> str:
        """Get the value of key k from the fields dictionary.

        Raises:
            KeyError: If k is not a key in the fields dict.
        """
        return self._fields[k]

    def _execute_query(self, q: str) -> Dict:
        """Execute the GraphQL query specified by the string q.

        Raises:
            gql.GraphQLSyntaxError: If the query string is structured improperly.
            gql.Exception: If the server raises an error during execution of the query.
        """
        return self.client.execute(gql(q))

    def _build_and_execute_query(
        self,
        q_name: str,
        q_fields: Optional[str] = None,
        q_arg_str: Optional[str] = None,
        q_args: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """Build query out of parameters, then execute it.

        Raises:
            gql.GraphQLSyntaxError: If the query string is structured improperly.
            gql.Exception: If the server raises an error during execution of the query.
            KeyError: If keys in q_args do not match placeholders in q_arg_str.
            ValueError: If q_arg_str is not a valid Template string.
        """
        q_string = self._build_query_string(
            q_name, q_fields, self._build_args(q_arg_str, q_args)
        )
        return self._execute_query(q_string)

    def _find_data(self):
        """Return a reference to to the relevant part of the query response.

        self._subpath_keys is a list of strings, which are a sequence of keys pointing
        to the data.
        """
        data = self._raw[self.name]
        if self._subpath_keys is not None:
            for k in self._subpath_keys:
                data = data[k]

        return data

    def _translate_dict(self, d: Dict) -> Dict:
        """Use translations from Config class to translate GraphQL response.

        This method is used by self.list() and self.dataframe() in order to translate
        field names from SBR into English words. Timestamps are converted into ISO
        strings.
        """

        def _recurse(el):
            """Recursive method used to iterate over all dict keys."""
            if isinstance(el, dict):
                # MUST cast to list to avoid RuntimeError because d.pop()
                for k in list(el.keys()):
                    try:
                        old_k = k
                        # raises KeyError if no translation available
                        k = t[k]

                        v = el.pop(old_k)
                        try:
                            # Sometimes values that should be integers are returned as
                            # strings. Need to make sure we're not truncating floats,
                            # however.
                            if isinstance(v, str):
                                v = int(v)
                        except ValueError:
                            pass
                        if k in ["datetime", "start datetime", "end datetime"]:
                            try:
                                # SearchEvents returns Zulu time iso string for value of
                                # 'date'.
                                v = utils.iso_str_to_timestamp(
                                    utils.iso_zulu_to_offset(v)
                                )
                            except (AttributeError, ValueError):
                                # AttributeError raised by iso_zulu_to_offset if v is a
                                # timestamp. ValueError raised by iso_str_to_timestamp
                                # if v is invalid isoformat string.
                                pass
                            try:
                                el[k] = utils.timestamp_to_iso_str(v)
                            except TypeError:
                                el[k] = v
                        else:
                            el[k] = v
                    except KeyError:
                        pass
                    v = el[k]
                    if isinstance(v, dict) or isinstance(v, list):
                        _recurse(v)
            elif isinstance(el, list):
                for x in el:
                    _recurse(x)

        t = self._config.translations()
        _recurse(d)
        return d

    def _copy_and_translate_data(self) -> List[Dict]:
        """Translate SBR fields in GraphQL response, and return a copy.

        This method is used by self.list() and self.dataframe(). self._translated
        caches the translated data.
        """
        if self._translated is None:
            data = copy.deepcopy(self._find_data())
            self._translated = self._translate_dict(data)
        return copy.deepcopy(self._translated)

    def arguments(self) -> Dict[str, str]:
        """Get the arguments dictionary, containing templates for all subqueries."""
        return self._arguments

    def fields(self) -> Dict[str, str]:
        """Get the fields dictionary, containing templates for all subqueries."""
        return self._fields

    def raw(self) -> Dict:
        """Get the raw GraphQL response, without any data processing."""
        return self._raw

    def id(self) -> Optional[int]:
        """Get the first id returned from the query response.

        The type of id returned depends on the Query implementation. For example,
        calling this method on queries returning events will return a list of event ids.

        If there are no ids, None is returned.

        Raises:
            NotImplementedError: If the Query object does not have a default return id
                type.
        """
        try:
            # TODO: This is slow since it iterates over all ids needlessly.
            return self.ids()[0]
        except IndexError:
            return None

    def ids(self) -> List[int]:
        """Get a list of ids from the query response.

        The type of id returned depends on the Query implementation. For example,
        calling this method on queries returning events will return a list of event ids.

        This method is useful for queries accepting lists of ids as arguments.

        Raises:
            NotImplementedError: If the Query object does not have a default return id
                type.
        """
        if self._id_key is None:
            raise NotImplementedError(
                f"{type(self).__name__} does not have a default return id type."
            )

        translated = self.list()
        ids = []
        for el in translated:
            ids.append(el[self._id_key])

        return list(set(ids))

    def list(self) -> List[Dict[str, Union[str, List, Dict]]]:
        """Get a list of translated elements returned from the query.

        Each element in the response is a dict with fields requested in the query and
        the element's values for those fields. The fields are translated.
        """
        data = self._copy_and_translate_data()
        # Some queries return dictionaries. Enforce this method returning a list.
        if isinstance(data, dict):
            data = [data]
        return data

    def dataframe(self) -> pd.DataFrame:
        """Get a dataframe of elements returned from the query.

        Each element in the response is a dict with fields requested in the query and
        the element's values for those fields. The fields are translated, and if the
        elements are nested, it is attempted to flatten them using self._sublist_keys,
        which is a list of keys expected to be in each element that have values that
        are lists.

        If the elements cannot be flattened, a dataframe of the nested elements is
        returned.
        """
        data = self._copy_and_translate_data()

        # Using sublist_keys instead of recursive method because there is a possibility
        # of overwriting keys without realizing it if using recursive method.
        # The idea is that pd.json_normalize() doesn't work on sublists.
        if self._sublist_keys is not None:
            for k in self._sublist_keys:
                for el in data:
                    try:
                        for i, subel in enumerate(el.get(k)):
                            new_key = f"{k}.{i+1}"
                            el[new_key] = subel
                        el.pop(k)
                    except TypeError:
                        pass
                    except AttributeError:
                        pass
        try:
            return pd.json_normalize(data)
        except AttributeError:
            return pd.DataFrame(data)
