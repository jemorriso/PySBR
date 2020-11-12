from string import Template
import copy

# from graphql import build_ast_schema, parse
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import pandas as pd

from pysbr.utils import Utils


# base query class
class Query:
    # with open("schema.graphql") as source:
    #     document = parse(source.read())
    # schema = build_ast_schema(document)

    def __init__(self):
        self._raw = None
        self._subpath_keys = None
        self._sublist_keys = None
        self._id_key = None

        transport = RequestsHTTPTransport(
            url="https://www.sportsbookreview.com/ms-odds-v2/odds-v2-service"
        )
        # client = Client(transport=_transport, fetch_schema_from_transport=True)
        self.client = Client(transport=transport, fetch_schema_from_transport=False)

    @staticmethod
    def _build_args(arg_str, args):
        """Build the argument string that gets inserted into a query.

        Args:
            arg_str (str): The arguments template string.
            args (dict): The substitutions to make. Each key must match a template
                placeholder, with the value being what gets substituted into the string.

        Returns:
            str: The argument string, with values inserted for each argument.
        """
        if arg_str is not None and args is not None:
            return Template(arg_str).substitute(args)
        else:
            return None

    @staticmethod
    def _build_query_string(q_name, q_fields=None, q_args=None):
        """Build up the GraphQL query string.

        Args:
            q_name (str): The name of the query object to be queried.
            q_fields (str): The fields to return.
            q_args (str, optional): The arg names to pass to the query. Defaults to
                None.

        Returns:
            str: The query string ready to be substituted using Template.substitute()
        """
        return (
            Template(
                Utils.str_format(
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
                    else Utils.str_format(q_args, indent_=2, dedent_l1=True),
                    "q_fields": ""
                    if q_fields is None
                    else Utils.str_format(q_fields, indent_=1, dedent_l1=True),
                }
            )
            # graphql query will not accept single quotes, but Template string by
            # default uses single quotes
            .replace("'", '"')
        )

    @staticmethod
    def _get_val_from_yaml(fname, k):
        """[summary]

        Args:
            fname ([type]): [description]
            type ([type]): [description]

        Returns:
            [type]: [description]

        Raises:
            NameError: If value of k is not a key in the loaded dictionary.
        """
        return Utils.load_yaml((Utils.build_yaml_path(fname)))[k]

    def _get_args(self, k):
        return self._get_val_from_yaml("arguments", k)

    def _get_fields(self, k):
        return self._get_val_from_yaml("fields", k)

    def _execute_query(self, q):
        """Execute a graphql query.

        Args:
            q (str): The query string.

        Returns:
            dict: The result of the query.
        """
        return self.client.execute(gql(q))

    def _build_and_execute_query(
        self, q_name, q_fields=None, q_arg_str=None, q_args=None
    ):
        q_string = self._build_query_string(
            q_name, q_fields, self._build_args(q_arg_str, q_args)
        )
        return self._execute_query(q_string)

    def _find_data(self):
        data = self._raw[self.name]
        if self._subpath_keys is not None:
            for k in self._subpath_keys:
                data = data[k]

        return data

    def _translate_dict(self, data):
        Utils.translate_dict(data, Utils.translation_dict())
        return data

    def _copy_and_translate_data(self):
        data = copy.deepcopy(self._find_data())
        return self._translate_dict(data)

    # for queries returning ids call this function to process _raw and return ids only
    def ids(self):
        if self._id_key is None:
            raise NotImplementedError(
                f"{type(self).__name__} does not have a default return id type"
            )

        translated = self.list()
        ids = []
        for el in translated:
            ids.append(el[self._id_key])

        return list(set(ids))

    def list(self):
        data = self._copy_and_translate_data()
        # Some queries return dictionaries. Enforce this method returning a list.
        if isinstance(data, dict):
            data = [data]
        return data

    def dataframe(self):
        data = self._copy_and_translate_data()

        # Using sublist_keys instead of recursive method because there is a possibility
        # of overwriting keys without realizing it if using recursive method
        # The idea is that pd.json_normalize() doesn't work on sublists
        if self._sublist_keys is not None:
            for k in self._sublist_keys:
                for el in data:
                    for i, subel in enumerate(el[k]):
                        new_key = f"{k}.{i+1}"
                        el[new_key] = subel
                    el.pop(k)

        return pd.json_normalize(data)
