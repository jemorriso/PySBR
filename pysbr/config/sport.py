from collections import OrderedDict
import itertools
from typing import Dict, List, Union

import pysbr.utils as utils
from pysbr.config.config import Config


class Sport(Config):
    """Provides access to sport and league config files.

    These files hold query-relevant information about a given sport.

    This is a base class not meant to be directly instantiated; see subclasses for each
    league and sport.

    Attributes:
        market_names (Dict[int, str]): Map market id to name. Used by Query.list() and
            Query.dataframe() in order to translate from id to name.
        sport_id (int): The sport's id in SBR's database.
        default_market_id (int): The sport's default betting market id, where the id
            number is from SBR.
        consensus_market_ids (List[int]): Available markets for consensus history query.
    """

    def __init__(self, sport_config: Dict):
        super().__init__()

        self._search_translations = utils.load_yaml(
            utils.build_yaml_path("search_dictionary")
        )

        self._sport = self._translate_dict(
            utils.load_yaml(utils.build_yaml_path(sport_config))
        )

        self._market_ids = self._build_market_ids()

        self.market_names = self._build_market_names(self._sport["markets"])
        self.market_periods = self._build_market_periods(self._sport["markets"])
        self.market_types = self._build_market_types(self._sport["markets"])

        self.sport_id = self._sport["sport id"]
        self.default_market_id = self._sport["default market id"]
        self.consensus_market_ids = self._sport["consensus market ids"]

    def _build_market_ids(self) -> Dict[str, int]:
        """Build the dictionary that is used for searching available betting markets.

        Keys are market group information strings concatenated with market information
        strings, values are market ids.

        Example keys with same value:
            'full game point spreads'
            'full-game pointspread'
            'point spread (including ot)'
        """
        market_ids = {}
        m = self._sport["markets"]
        for x in m:
            keys_a = [v.lower() for v in x.values() if isinstance(v, str)]
            for y in x["market types"]:
                id = y["market id"]
                keys_b = [v.lower() for v in y.values() if isinstance(v, str)]
                keys = [
                    " ".join(el).strip()
                    for el in list(itertools.product(keys_a, keys_b))
                ]
                # Add name on its own for markets other than full game (the
                # concatenated version will not make sense).
                keys.append(y["name"].lower())
                market_ids.update({k: id for k in keys})
        return market_ids

    def _build_market_names(self, m: List[Dict]) -> Dict[int, str]:
        """Build the dictionary that is used to translate from market ids to names."""
        markets = {}
        for x in m:
            for y in x["market types"]:
                markets[y["market id"]] = y["name"]
        return markets

    def _build_market_periods(self, m: List[Dict]) -> Dict[int, List[int]]:
        """Build the dictionary that is used to translate from market ids to periods.

        The periods refer to the parts of a game that a market is active for. For
        example, a 1st quarter or 1st period market will have a value of [1,2].
        """
        markets = {}
        for x in m:
            for y in x["market types"]:
                try:
                    markets[y["market id"]] = x["periods"]
                except KeyError:
                    pass
        return markets

    def _build_market_types(self, m):
        market_types = {}
        name_map = {
            "money-line": "moneyline",
            "pointspread": "spread",
            "totals": "total",
        }
        for x in m:
            for y in x["market types"]:
                try:
                    market_types[y["market id"]] = name_map[y["url"]]
                except KeyError:
                    # futures
                    market_types[y["market id"]] = x["url"]
        return market_types

    def market_id(self, term: Union[int, str]) -> int:
        """Given provided search term, return matching market id.

        If search term is string, search for matching betting market. If search term is
        int, assume that it is the ID, and return it.

        This method is provided as a convenience so that you don't need to
        remember market id numbers. Case is ignored for search terms.

        A search dictionary is utilized so that you can use common abbrevations /
        spelling variants for markets instead of typing them out / worrying about
        format.

        Example search terms, which all point to the same market id:
            '1st half over/under'
            '1st-half totals'
            '1st half o/u'
            'first half totals'
            'first-half ou'
            '1hou'
            '1htot'
            '1h ou'
            '1h tot'
            '1H OU'
            '1H TOT'
            '1HOU'

        Raises:
            TypeError:
                If a provided search term is not an int or str.
            ValueError:
                If a provided search term string cannot be matched with a market.
        """
        return self.market_ids(term)[0]

    def market_ids(self, terms: Union[List[Union[int, str]], int, str]) -> List[int]:
        """Given provided search terms, return a list of matching market ids.

        If search term is string, search for matching betting market. If search term is
        int, assume that it is the ID, and insert it into the list to be returned.

        This method is provided as a convenience so that you don't need to
        remember market id numbers. Case is ignored for search terms.

        A search dictionary is utilized so that you can use common abbrevations /
        spelling variants for markets instead of typing them out / worrying about
        format.

        Example search terms, which all point to the same market id:
            '1st half over/under'
            '1st-half totals'
            '1st half o/u'
            'first half totals'
            'first-half ou'
            '1hou'
            '1htot'
            '1h ou'
            '1h tot'
            '1H OU'
            '1H TOT'
            '1HOU'

        Raises:
            TypeError:
                If a provided search term is not an int or str.
            ValueError:
                If a provided search term string cannot be matched with a market.
        """

        def try_translate(term: str) -> str:
            """Attempt to translate a given search term using the search dictionary.

            If there is no translation for the given string, the original value is
            returned.
            """
            words = term.split(" ")
            translated_words = []
            for w in words:
                try:
                    translated_words.append(search_dict[w])
                except KeyError:
                    translated_words.append(w)
            return " ".join(translated_words)

        def try_match_and_append(term: str, ids: List[int]) -> bool:
            """Attempt to match the search term with a market id.

            If match, append the id to the ids list.
            """
            id = self._market_ids.get(term)
            if id is not None:
                ids.append(id)
                return True
            return False

        def split_word(word: str) -> List[str]:
            """Split a word at index 2 and 3, and join parts with space.

            Split only at index 2 and 3 because the abbreviations in the search
            dictionary are never longer than 3 characters.

            Returned list may be empty for invalid inputs.
            """
            splits = []
            for i in range(2, 4):
                try:
                    splits.append(" ".join([word[:i], word[i:]]))
                except IndexError:
                    pass
            return splits

        def match_term(term: Union[int, str], ids: List[int]) -> bool:
            """Try and match a given search term with a market id."""
            if isinstance(term, int):
                ids.append(term)
                return True
            try:
                term = term.lower().strip()
            except AttributeError:
                raise TypeError("Search terms must be ints or strings.")
            translated_term = try_translate(term)
            if try_match_and_append(translated_term, ids):
                return True
            # The term may be abbreviations concatenated together without a space, for
            # example, '1hou'.
            if len(term.split(" ")) == 1:
                splits = split_word(term)
                for t_split in splits:
                    translated_term = try_translate(t_split)
                    if try_match_and_append(translated_term, ids):
                        return True
            return False

        terms = utils.make_list(terms)
        search_dict = self._search_translations
        ids = []
        for term in terms:
            if not match_term(term, ids):
                raise ValueError(f"Could not find market {term}.")

        return list(OrderedDict.fromkeys(ids))

    def sport_config(
        self,
    ) -> Dict[
        str, Union[int, List[Dict[str, Union[str, List[Dict[str, Union[int, str]]]]]]]
    ]:
        """Get the dictionary created from the sport's config file.

        The dict holds values for 'sport id' and 'default market id', as well as a list
        of all markets available on the sport.
        """
        return self._sport

    def search_translations(self) -> Dict[str, str]:
        """Get the dict containing translations for search abbreviatons / spelling variants.

        This is the dict that is used Sport.market_ids().
        """
        return self._search_translations


class League(Sport):
    """Provides access to league config files.

    These files hold query-relevant information about a given league.

    This is a base class not meant to be directly instantiated; see subclasses for each
    league.

    Attributes:
        league_id (int): The league's id in SBR's database.
        league_name (str): The league's name. May differ from the name given by SBR.
        abbr (str): The standard abbreviation for the league. May differ from the
            abbreviation given by SBR.
    """

    def __init__(self, sport_config, league_config):
        super().__init__(sport_config)

        self._league = self._translate_dict(
            utils.load_yaml(utils.build_yaml_path(league_config))
        )
        self.league_id = self._league["league id"]
        self.league_name = self._league["name"]
        self.abbr = self._league["abbreviation"]

    def league_config(
        self,
    ) -> Dict[str, Union[int, str, List[Dict[str, Union[int, str]]]]]:
        """Get the dictionary created from the league's config file.

        The dict holds values for 'league id', 'name', 'abbreviation'. For leagues
        inheriting from TeamSport, it also holds a list of all teams in the league.
        """
        return self._league


class TeamLeague(League):
    """Additional methods for leagues with team information in their config files.

    Class must be initialized with given sport and league config files.

    This class should not be directly instantiated; use league subclasses.

    'id', 'abbreviation', 'sbr abbreviation', 'name', 'nickname', and 'location' are
    keys provided for each team in the league config file.
    """

    def __init__(self, sport_config, league_config):
        super().__init__(sport_config, league_config)

        self._team_ids = self._build_team_ids()

    def _build_team_ids(self) -> Dict[str, Dict[str, Union[int, List[int]]]]:
        """Build team id search dictionary.

        Values are market ids or list of market ids. If list, the search term is
        ambiguous. For example, if NFL, 'New York' is the value for 'location' in the
        config dictionary for 2 teams (Jets and Giants).
        """

        t = self._league["teams"]
        teams = {}
        for k in [
            "abbreviation",
            "sbr abbreviation",
            "name",
            "nickname",
            "location",
            "full name",
        ]:
            teams[k] = {}
            if not k == "full name":
                for x in t:
                    id_ = x["team id"]
                    k2 = x[k].lower()
                    if k2 in teams[k]:
                        v = teams[k][k2]
                        try:
                            v.append(id_)
                        except AttributeError:
                            teams[k][k2] = [v, id_]
                    else:
                        teams[k][k2] = id_
            else:
                for x in t:
                    full_name = " ".join([x["location"].lower(), x["nickname"].lower()])
                    teams[k][full_name] = x["team id"]

        return teams

    def team_id(self, term: Union[int, str]) -> int:
        """Given provided search term, return matching team id.

        If search term is string, search for matching team. If search term is
        int, assume that it is the ID, and return it.

        This method is provided as a convenience so that you don't need to
        remember team id numbers. Case is ignored for search terms.

        Example search terms:
            Seattle
            Seahawks
            Seattle Seahawks
            sea
            SEA

        Raises:
            TypeError:
                If a search term is not an int or str.
            ValueError:
                If a search term is ambiguous, or cannot be matched with a team.
        """
        return self.team_ids(term)[0]

    def team_ids(self, terms: Union[int, str, List[Union[int, str]]]) -> List[int]:
        """Given provided search terms, return a list of matching team ids.

        If search term is string, search for matching team. If search term is
        int, assume that it is the ID, and insert it into the list to be returned.

        This method is provided as a convenience so that you don't need to
        remember team id numbers. Case is ignored for search terms.

        Example search terms:
            Seattle
            Seahawks
            Seattle Seahawks
            sea
            SEA

        Raises:
            TypeError:
                If a search term is not an int or str.
            ValueError:
                If a search term is ambiguous, or cannot be matched with a team.
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
                    match = [v[t] for k, v in self._team_ids.items() if t in v][0]
                    ids.append(match)
                except IndexError:
                    raise ValueError(f"Could not find team {old_t}.")
                if isinstance(match, list):
                    raise ValueError(
                        utils.str_format(
                            f"""Search term '{old_t}' is ambiguous.
                            Matching ids: {', '.join([str(m) for m in match])}.
                        """,
                            squish=True,
                        )
                    )
        return list(OrderedDict.fromkeys(ids))


class Football(Sport):
    """Provides access to football config files."""

    def __init__(self):
        super().__init__("football")


class Basketball(Sport):
    """Provides access to basketball config files."""

    def __init__(self):
        super().__init__("basketball")


class Baseball(Sport):
    """Provides access to baseball config files."""

    def __init__(self):
        super().__init__("baseball")


class Hockey(Sport):
    """Provides access to hockey config files."""

    def __init__(self):
        super().__init__("hockey")


class Soccer(Sport):
    """Provides access to soccer config files."""

    def __init__(self):
        super().__init__("soccer")


class Tennis(Sport):
    """Provides access to tennis config files."""

    def __init__(self):
        super().__init__("tennis")


class Fighting(Sport):
    """Provides access to tennis config files."""

    def __init__(self):
        super().__init__("fighting")


class NFL(TeamLeague):
    """Provides access to NFL config files."""

    def __init__(self):
        super().__init__("football", "nfl")


class NCAAF(TeamLeague):
    """Provides access to NCAAF config files."""

    def __init__(self):
        super().__init__("football", "ncaaf")


class MLB(League):
    """Provides access to MLB config files."""

    def __init__(self):
        super().__init__("baseball", "mlb")


class NBA(TeamLeague):
    """Provides access to NBA config files."""

    def __init__(self):
        super().__init__("basketball", "nba")


class NCAAB(TeamLeague):
    """Provides access to NCAAB config files."""

    def __init__(self):
        super().__init__("basketball", "ncaab")

        self._market_ids = self._build_market_ids()

        self.market_names = self._build_market_names(self._league["markets"])
        self.market_periods = self._build_market_periods(self._league["markets"])
        self.market_types = self._build_market_types(self._league["markets"])


class NHL(TeamLeague):
    """Provides access to NHL config files."""

    def __init__(self):
        super().__init__("hockey", "nhl")


class EPL(League):
    """Provides access to EPL config files."""

    def __init__(self):
        super().__init__("soccer", "epl")


class UCL(League):
    """Provides access to UCL config files."""

    def __init__(self):
        super().__init__("soccer", "ucl")


class LaLiga(League):
    """Provides access to La Liga config files."""

    def __init__(self):
        super().__init__("soccer", "laliga")


class Bundesliga(League):
    """Provides access to Bundesliga config files."""

    def __init__(self):
        super().__init__("soccer", "bundesliga")


class UEFANationsLeague(League):
    """Provides access to UEFA Nations League config files."""

    def __init__(self):
        super().__init__("soccer", "uefanationsleague")


class ATP(League):
    """Provides access to ATP config files."""

    def __init__(self):
        super().__init__("tennis", "atp")


class UFC(League):
    """Provides access to UFC config files."""

    def __init__(self):
        super().__init__("fighting", "ufc")
