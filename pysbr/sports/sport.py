from pysbr.utils import Utils


class Sport:
    def __init__(self, sport_config, league_config):

        t = self._get_translation_dict()

        d = Utils.load_yaml(Utils.build_yaml_path(sport_config))
        self._translate_dict(d, t)
        self._sport = d

        self.sport_id = d["sport id"]
        self.default_market_id = d["default market id"]
        self._markets = self._build_markets(d["markets"])

        d = Utils.load_yaml(Utils.build_yaml_path(league_config))
        self._translate_dict(d, t)
        self._league = d

        # assign instance variables for each of the top level dictionary elements
        # in the yaml config file
        self.league_id = d["league id"]
        self.league_name = d["name"]
        self.abbr = d["alias"]

    def _get_translation_dict(self):
        return Utils.load_yaml(Utils.build_yaml_path("dictionary"))

    def _translate_dict(self, d, t):
        def _recurse(el):
            if isinstance(el, dict):
                # MUST cast to list to avoid RuntimeError because d.pop()
                for k in list(el.keys()):
                    try:
                        old_k = k
                        k = t[k]

                        el[k] = el.pop(old_k)
                    except KeyError:
                        pass
                    v = el[k]
                    if isinstance(v, dict) or isinstance(v, list):
                        _recurse(v)
                    elif isinstance(v, str):
                        el[k] = v.lower()
            elif isinstance(el, list):
                for x in el:
                    _recurse(x)

        _recurse(d)

    def _build_markets(self, m):
        markets = {}
        for x in m:
            markets[x["url"]] = {}
            markets[x["name"]] = {}
            for y in x["market types"]:
                id = [v for k, v in y.items() if k == "market id"][0]
                for k in ["alias", "name", "url"]:
                    v = [v for list_key, v in y.items() if list_key == k][0]
                    markets[x["url"]][v] = id
                    markets[x["name"]][v] = id
        return markets

    def market_ids(self, terms):
        search_dict = Utils.load_yaml(Utils.build_yaml_path("search_dictionary"))
        ids = []
        for t in terms:
            if isinstance(t, int):
                ids.append(t)
            else:
                old_t = t
                if isinstance(t, str):
                    t = ["full game", t]
                t = list(t)
                try:
                    t = [x.lower() for x in t]
                except AttributeError:
                    raise AttributeError("Search components must be ints or strings.")
                try:
                    t[0] = search_dict[t[0]]
                except KeyError:
                    pass
                try:
                    t[1] = search_dict[t[1]]
                except KeyError:
                    pass

                try:
                    ids.append(self._markets[t[0]][t[1]])
                except KeyError:
                    raise ValueError(f"Could not find market {old_t}")
        # TODO: need to handle case where they resolve to same ID, because I don't
        # think it will work for the query?
        return ids


class TeamSport(Sport):
    def __init__(self, sport_config, league_config):
        super().__init__(sport_config, league_config)

        t = self._get_translation_dict()
        d = Utils.load_yaml(Utils.build_yaml_path(league_config))
        self._translate_dict(d, t)

        self._teams = self._build_teams(d["teams"])

    def _build_teams(self, t):
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
                    teams[k][x[k]] = x["team id"]
            else:
                for x in t:
                    full_name = " ".join([x["location"], x["nickname"]])
                    teams[k][full_name] = x["team id"]

        return teams

    def team_ids(self, terms):
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
                for k, v in self._teams.items():
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

        return ids
