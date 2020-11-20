from collections import OrderedDict
import itertools

import pysbr.utils as utils
from pysbr.config.config import Config


class Sport(Config):
    def __init__(self, sport_config, league_config):
        super().__init__()

        self._search_translations = utils.load_yaml(
            utils.build_yaml_path("search_dictionary")
        )

        self._sport = self._translate_dict(
            utils.load_yaml(utils.build_yaml_path(sport_config))
        )
        self._league = self._translate_dict(
            utils.load_yaml(utils.build_yaml_path(league_config))
        )

        self._market_ids = self._build_market_ids()

        self.market_names = self._build_market_names(self._sport["markets"])

        self.sport_id = self._sport["sport id"]
        self.default_market_id = self._sport["default market id"]
        self.league_id = self._league["league id"]
        self.league_name = self._league["name"]
        self.abbr = self._league["abbreviation"]

    def _build_market_ids(self):
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

    def _build_market_names(self, m):
        markets = {}
        for x in m:
            for y in x["market types"]:
                markets[y["market id"]] = y["name"]
        return markets

    def market_ids(self, terms):
        def try_translate(term):
            words = term.split(" ")
            translated_words = []
            for w in words:
                try:
                    translated_words.append(search_dict[w])
                except KeyError:
                    translated_words.append(w)
            return " ".join(translated_words)

        def try_match_and_append(term, ids):
            id = self._market_ids.get(term)
            if id is not None:
                ids.append(id)
                return True
            return False

        def split_word(word):
            splits = []
            for i in range(2, 4):
                try:
                    splits.append(" ".join([word[:i], word[i:]]))
                except IndexError:
                    pass
            return splits

        def match_term(term, ids):
            if isinstance(term, int):
                ids.append(term)
                return True

            try:
                term = term.lower().strip()
            except AttributeError:
                raise AttributeError("Search terms must be ints or strings.")
            translated_term = try_translate(term)
            if try_match_and_append(translated_term, ids):
                return True
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
                raise ValueError(f"Could not find market {term}")

        return list(OrderedDict.fromkeys(ids))

    def sport_config(self):
        return self._sport

    def league_config(self):
        return self._league

    def search_translations(self):
        return self._search_translations


class TeamSport(Sport):
    def __init__(self, sport_config, league_config):
        super().__init__(sport_config, league_config)

        self._team_ids = self._build_team_ids(self._league["teams"])

    def _build_team_ids(self, t):
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
                    teams[k][x[k].lower()] = x["team id"]
            else:
                for x in t:
                    full_name = " ".join([x["location"].lower(), x["nickname"].lower()])
                    teams[k][full_name] = x["team id"]

        return teams

    def team_ids(self, terms):
        terms = utils.make_list(terms)
        ids = []
        for t in terms:
            if isinstance(t, int):
                ids.append(t)
            else:
                old_t = t
                t = t.lower()
                found = False
                # Pylance error 'id is possibly unbound' if I don't set id to None here
                id = None
                for k, v in self._team_ids.items():
                    if t in v:
                        if not found:
                            found = True
                            id = v[t]
                        else:
                            # TODO - could I raise a warning instead?
                            # raise ValueError(f"Search term {old_t} is ambiguous")
                            pass
                if not found:
                    raise ValueError(f"Could not find team {old_t}")
                else:
                    ids.append(id)

        return list(OrderedDict.fromkeys(ids))


class NFL(TeamSport):
    def __init__(self):
        super().__init__("football", "nfl")


class NCAAF(TeamSport):
    def __init__(self):
        super().__init__("football", "ncaaf")


class MLB(Sport):
    def __init__(self):
        super().__init__("baseball", "mlb")


class NBA(Sport):
    def __init__(self):
        super().__init__("basketball", "nba")


class NCAAB(Sport):
    def __init__(self):
        super().__init__("basketball", "ncaab")


class NHL(Sport):
    def __init__(self):
        super().__init__("hockey", "nhl")


class EPL(Sport):
    def __init__(self):
        super().__init__("soccer", "epl")


class UCL(Sport):
    def __init__(self):
        super().__init__("soccer", "ucl")


class LaLiga(Sport):
    def __init__(self):
        super().__init__("soccer", "laliga")


class Bundesliga(Sport):
    def __init__(self):
        super().__init__("soccer", "bundesliga")


class UEFANationsLeague(Sport):
    def __init__(self):
        super().__init__("soccer", "uefanationsleague")


class ATP(Sport):
    def __init__(self):
        super().__init__("tennis", "atp")
