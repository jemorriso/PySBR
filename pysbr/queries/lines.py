import copy

from pysbr.queries.query import Query
from pysbr.config.nfl import NFL
from pysbr.config.ncaaf import NCAAF
from pysbr.config.atp import ATP
from pysbr.config.sportsbook import Sportsbook


class Lines(Query):
    def __init__(self):
        self._events = None
        self._event_descriptions = {}
        self._event_leagues = {}
        self._participants = {}
        self._leagues = {16: NFL, 6: NCAAF, 23: ATP}
        self._league_markets = {}
        self._sportsbooks = None

        self._with_ids_translated = None

        super().__init__()

    def _clean_lines(self, data):
        to_remove = [
            "boid",
            "lineid",
            "sequence",
            "dp",
            "bs",
            "iof",
            "sbid",
            "sid",
            "fpd",
            "fpn",
            "sort",
        ]
        for term in to_remove:
            for line in data:
                line.pop(term, None)
        return data

    def _init_config(self, data):
        if self._sportsbooks is None:
            self._sportsbooks = Sportsbook().names

        league_ids = [e.get("league id") for e in self._events.list()]
        for id in set(league_ids):
            if id not in self._league_markets:
                try:
                    self._league_markets[id] = self._leagues[id]().market_names
                except KeyError:
                    pass

        if (
            not self._event_descriptions
            or not self._event_leagues
            or not self._participants
        ):
            for e in self._events.list():
                self._event_descriptions[e.get("event id")] = e.get("description")
                self._event_leagues[e.get("event id")] = e.get("league id")
                for p in e["participants"]:
                    participant_id = p.get("participant id")
                    source = p.get("source")
                    if "last name" in source:
                        self._participants[participant_id] = source.get("last name")
                    elif "abbreviation" in source:
                        self._participants[participant_id] = source.get("abbreviation")

    def _translate_ids(self, data):
        if self._events is None:
            return data

        if self._with_ids_translated is not None:
            return self._with_ids_translated

        self._init_config(data)

        for line in data:
            line["event"] = self._event_descriptions.get(line.get("event id"))
            try:
                line["market"] = self._league_markets.get(
                    self._event_leagues.get(line.get("event id"))
                ).get(line.get("market id"))
            # if somehow got None.get(None)
            except AttributeError:
                pass
            line["sportsbook"] = self._sportsbooks.get(line.get("provider account id"))
            line["participant"] = self._participants.get(line.get("participant id"))

        self._with_ids_translated = data
        return data

    def _copy_and_translate_data(self):
        data = copy.deepcopy(self._find_data())
        self._clean_lines(data)
        self._translate_dict(data)
        return self._translate_ids(data)

    def list(self, events=None):
        self._events = events
        return super().list()

    def dataframe(self, events=None):
        self._events = events
        return super().dataframe()
