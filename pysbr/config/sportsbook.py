from typing import Dict, List, Union, Optional
from collections import OrderedDict

import pysbr.utils as utils
from pysbr.config.config import Config


class Sportsbook(Config):
    """Provides access to sportsbook config file.

    In the config file there is information provided for the 27 sportsbooks found on
    SBR.

    Note that the id returned from lines-related queries is called 'sportsbook id' by
    this application, which is translated from 'paid', the name returned from SBR.
    There is another sportsbook id that is only used by the 'Sportsbooks' query, that
    is called 'system sportsbook id' by this application, which is translated from
    'sbid', the name returned from SBR. The system sportsbook id is not used by other
    parts of the application.

    Attributes:
        names (Dict[int, str]): Map sportsbook id to name. Used by Query.list() and
            Query.dataframe() in order to translate from id to name.
    """

    def __init__(self):
        super().__init__()

        self._sportsbooks = self._translate_dict(
            utils.load_yaml(utils.build_yaml_path("sportsbooks"))
        )
        self._sportsbook_ids = self._build_sportsbook_ids()

        self.names = {
            x["sportsbook id"]: x["name"] for x in self._sportsbooks["sportsbooks"]
        }

    def _build_sportsbook_ids(self) -> Dict[str, Dict[str, int]]:
        """Build sportsbook id search dictionary."""

        s = self._sportsbooks["sportsbooks"]
        sportsbooks = {}
        for k in ["name", "alias"]:
            sportsbooks[k] = {}
            for x in s:
                sportsbooks[k][x[k].lower()] = x["sportsbook id"]

        return sportsbooks

    def sportsbook_config(self) -> List[Dict[str, Union[str, int]]]:
        """Get sportsbook config list.

        Each list element is a dict representing a sportsbook, with 'name',
        n 'short name', 'sportsbook id' and 'system sportsbook id' as keys.
        """
        return self._sportsbooks

    def id(self, term: Union[int, str]) -> Optional[int]:
        """Take provided search term and return matching sportsbook id.

        If search term is string, search for matching sportsbook. If search term is
        int, assume that it is the ID, and return it.

        This method is provided as a convenience so that you don't need to
        remember sportsbook id numbers. Case is ignored for search terms.

        Example search terms:
            'pinnacle'
            'PINNACLE'
            'bodog'
            'bodog sportsbook'
            20

        Raises:
            TypeError:
                If a provided search term is not an int or str.
            ValueError:
                If a provided search term string cannot be matched with a sportsbook.
        """
        return self.ids(term)[0]

    def ids(self, terms: Union[List[Union[int, str]], int, str]) -> List[int]:
        """Take provided search terms and return list of matching sportsbook ids.

        If search term is string, search for matching sportsbook. If search term is
        int, assume that it is the ID, and insert it into the list to be returned.

        This method is provided as a convenience so that you don't need to
        remember sportsbook id numbers. Case is ignored for search terms.

        Example search terms:
            'pinnacle'
            'PINNACLE'
            'bodog'
            'bodog sportsbook'
            20

        Raises:
            TypeError:
                If a provided search term is not an int or str.
            ValueError:
                If a provided search term string cannot be matched with a sportsbook.
        """
        terms = utils.make_list(terms)
        ids = []
        for t in terms:
            if isinstance(t, int):
                ids.append(t)
            else:
                old_t = t
                try:
                    t = t.lower()
                except AttributeError:
                    raise TypeError("Search terms must be ints or strings.")
                try:
                    id = [v[t] for k, v in self._sportsbook_ids.items() if t in v][0]
                    ids.append(id)
                except IndexError:
                    raise ValueError(f"Could not find sportsbook {old_t}.")

        return list(OrderedDict.fromkeys(ids))
