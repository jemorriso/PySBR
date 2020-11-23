import copy
from typing import List, Dict, Union

import pandas as pd

from pysbr.queries.query import Query
from pysbr.config.sport import (
    NFL,
    NCAAF,
    ATP,
    Bundesliga,
    EPL,
    LaLiga,
    MLB,
    NBA,
    NCAAB,
    NHL,
    UCL,
    UEFANationsLeague,
)
from pysbr.config.sportsbook import Sportsbook


class Lines(Query):
    """Implements methods particular to queries about betting lines.

    This class should not be directly instantiated; use the subclasses defined for each
    lines-related query.
    """

    def __init__(self):
        self._events = None
        self._event_descriptions = {}
        self._event_leagues = {}
        # these are the participant ids for Over/Under lines for all sports I checked
        self._participants = {15143: "over", 15144: "under"}
        self._leagues = {
            16: NFL,
            6: NCAAF,
            23: ATP,
            11: Bundesliga,
            2: EPL,
            17: LaLiga,
            5: NBA,
            3: MLB,
            14: NCAAB,
            7: NHL,
            8: UCL,
            1911: UEFANationsLeague,
        }
        self._league_markets = {}
        self._sportsbooks = None

        self._with_ids_translated = None

        super().__init__()

    def _clean_lines(self, data: List[Dict]) -> List[Dict]:
        """Remove unneeded keys from the query response.

        This is necessary for lines-related queries because they don't accept any
        fields, so some unneeded fields are returned.
        """
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

    def _init_config(self, data: List[Dict]) -> None:
        """"""
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
                for p in e.get("participants"):
                    participant_id = p.get("participant id")
                    source = p.get("source")
                    if "last name" in source:
                        self._participants[participant_id] = source.get("last name")
                    elif "abbreviation" in source:
                        self._participants[participant_id] = source.get("abbreviation")

    def _translate_ids(self, data: List[Dict]) -> List[Dict]:
        """Add new entries to each element in the list for element's id fields.

        The response for lines-related queries has many ids without associated
        information, making it hard to remember which line is related to which event.
        This method adds that related information to each element in the list as long
        as a list of events has been passed in when calling self.list() or
        self.dataframe().

        If a list of events (that the lines come from) is not passed to self.list() or
        self.dataframe(), this method has no effect. Otherwise, it adds the following
        to each element:
            event description
            betting market name
            sportsbook name
            participant information

        self._with_ids_translated caches the returned list.
        """
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

    def _copy_and_translate_data(self) -> List[Dict]:
        """Translate SBR fields in GraphQL response, and return a copy.

        This method is used by self.list() and self.dataframe(). Overrides Query.
        _copy_and_translate_data() in order to add steps for cleaning the response and
        translating the ids in the response.
        """
        data = copy.deepcopy(self._find_data())
        self._clean_lines(data)
        self._translate_dict(data)
        return self._translate_ids(data)

    def list(self, events=None) -> List[Dict[str, Union[str, List, Dict]]]:
        """Get a list of translated elements returned from the query.

        If a list of events the lines are for is passed in, extra information about
        each line will be added to each element of the returned list, including event
        description, participant information, and betting market name.
        """
        self._events = events
        return super().list()

    def dataframe(self, events=None) -> pd.DataFrame:
        """Get a dataframe of elements returned from the query.

        If a list of events the lines are for is passed in, extra information about
        each line will be added to each row of the returned dataframe, including event
        description, participant information, and betting market name.
        """
        self._events = events
        return super().dataframe()
