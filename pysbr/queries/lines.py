import copy
from typing import List, Dict, Union, Tuple

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
    UFC,
)
from pysbr.config.sport import (
    Football,
    Basketball,
    Baseball,
    Hockey,
    Soccer,
    Tennis,
    Fighting,
)
from pysbr.config.sport import Sport
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
        self._event_sports = {}
        self._event_scores = {}
        self._event_statuses = {}
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
            26: UFC,
        }
        self._leagues_init = {}

        self._sports = {
            4: Football,
            5: Basketball,
            3: Baseball,
            6: Hockey,
            1: Soccer,
            8: Tennis,
            9: Fighting,
        }
        self._sports_init = {}

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
                try:
                    # ConsensusHistory has 'line' as a key, instead of being the
                    # top-level dictionary.
                    line = line["line"]
                except KeyError:
                    pass
                try:
                    # The earliest (time-wise) lines in consensusHistory may not have
                    # 'line' as a key.
                    line.pop(term, None)
                except AttributeError:
                    pass
        return data

    def _init_config(self, data: List[Dict]) -> None:
        """Initialize private instance variables.

        There is a lot of data that needs to be initialized in order to translate from
        ids to information. This method does that.

        self._leagues and self._sports map league and sport ids to their configuration
        classes. Other private instance variables map event and participant ids to their
        translations.
        """
        if self._sportsbooks is None:
            self._sportsbooks = Sportsbook().names

        league_ids = [e.get("league id") for e in self._events.list()]
        for id in set(league_ids):
            try:
                self._leagues_init[id] = self._leagues[id]()
            except KeyError:
                pass

        sport_ids = [e.get("sport id") for e in self._events.list()]
        for id in set(sport_ids):
            try:
                self._sports_init[id] = self._sports[id]()
            except KeyError:
                pass

        for e in self._events.list():
            self._event_descriptions[e.get("event id")] = e.get("description")
            self._event_leagues[e.get("event id")] = e.get("league id")
            self._event_sports[e.get("event id")] = e.get("sport id")
            self._event_scores[e.get("event id")] = e.get("scores")
            self._event_statuses[e.get("event id")] = e.get("event status")
            try:
                for p in e["participants"]:
                    participant_id = p.get("participant id")
                    source = p.get("source")
                    if "last name" in source and source.get("last name") is not None:
                        self._participants[participant_id] = source.get("last name")
                    elif (
                        "abbreviation" in source
                        and source.get("abbreviation") is not None
                    ):
                        self._participants[participant_id] = source.get("abbreviation")
                    elif "name" in source and source.get("name") is not None:
                        self._participants[participant_id] = source.get("name")

            except KeyError:
                # Should not reach here; e['participants'] should be empty list at
                # least.
                pass

    def _get_config(self, line: List[Dict]) -> Sport:
        """Get league or sport config class.

        If neither the league nor the sport has a configuration class, then the market
        name and bet result will not appear in the Query.list() or Query.dataframe().
        """
        try:
            # League needs to be before sport because it may override some attributes.
            # E.g. NCAAB market periods.
            return self._leagues_init[self._event_leagues.get(line.get("event id"))]
        except KeyError:
            try:
                return self._sports_init[self._event_sports.get(line.get("event id"))]
            except KeyError:
                # neither league nor sport has a config file
                return None

    def _resolve_market(self, line: List[Dict]) -> str:
        """Attempt to get the name of the market from its id."""
        try:
            return self._get_config(line).market_names.get(line.get("market id"))
        except AttributeError:
            return None

    def _tally_points(
        self,
        line: List[Dict],
        period_scores: List[Dict[str, int]],
        market_range: List[int],
    ) -> Tuple[int, int]:
        """Sum up the points scored over the range of interest, according to the market
        in question.

        If the market is a total, the return is of the form (total, []). Otherwise, the
        return looks like (points_scored_by_team, points_scored_by_other_team).
        """
        scores = copy.deepcopy(period_scores)
        # TODO: check that len scores == market range (current and future events)
        if market_range is not None:
            scores = [s for s in period_scores if s.get("period") in market_range]

        participant_id = line.get("participant id")
        o_scores = []
        if participant_id not in [15143, 15144]:
            scores = [
                s for s in period_scores if s.get("participant id") == participant_id
            ]
            o_scores = [
                s for s in period_scores if s.get("participant id") != participant_id
            ]

        try:
            return sum([s.get("points scored") for s in scores]), sum(
                [s.get("points scored") for s in o_scores]
            )
        except TypeError:
            return None, None

    def _evaluate_bet(self, line: List[Dict], points, o_points):
        """Evaluate whether the bet won or lost.

        Given a line, market, and point totals, determine whether the bet won or lost,
        returning True if win, and False if lose.
        """
        try:
            market_type = self._get_config(line).market_types.get(line.get("market id"))
        except AttributeError:
            return None

        participant_id = line.get("participant id")
        spread_or_total = line["spread / total"]
        if market_type == "total":
            # participant ids for o/u
            over = 15143
            under = 15144
            if (
                participant_id == over
                and points > spread_or_total
                or participant_id == under
                and points < spread_or_total
            ):
                return True
            else:
                return False
        else:
            try:
                if points + spread_or_total > o_points:
                    return True
                else:
                    return False
            except ValueError:
                return None

    def _resolve_bet(self, line: List[Dict]) -> Tuple[str, float]:
        """Given a line, determine what the result of the bet was.

        Utilizes event scores list which is part of an event query response. This
        method calculates the point totals for the team of the line in question vs. the
        other team, over the periods / quarters that the bet is evaluated, in order to
        determine the result of the bet.

        Returns a tuple where the first value is 'W' or 'L', and the second value is
        the amount of profit the bet would return on a $100 bet. If some step fails,
        (None, None) is returned and the bet result / profit are not included for that
        particular line. Errors are not raised.
        """
        event_status = self._event_statuses.get(line.get("event id"))
        scores = self._event_scores.get(line.get("event id"))
        # Event query didn't have scores, or the game hasn't been played yet (query
        # returns empty list), or event is in progress.
        if not scores or event_status != "complete":
            return None, None, None

        try:
            market_periods = self._get_config(line).market_periods.get(
                line.get("market id")
            )
        except AttributeError:
            return

        try:
            market_range = list(range(market_periods[0], market_periods[-1]))
        except TypeError:
            market_range = None

        points, o_points = self._tally_points(line, scores, market_range)
        if points is None or o_points is None:
            return None, None, None

        is_win = self._evaluate_bet(line, points, o_points)
        if is_win is None:
            return None, None, None

        try:
            profit = (
                round((line.get("decimal odds") - 1) * 100, 2) if is_win else -100.0
            )
        except ValueError:
            return None, None, None

        return ("W" if is_win else "L", profit, points)

    def _translate_ids(self, data: List[Dict]) -> List[Dict]:
        """Add new entries to each element in the list for the element's id fields.

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
            bet result information (whether it won or lost; only for completed events)

        self._with_ids_translated caches the returned list.
        """
        if self._events is None:
            return data

        if self._with_ids_translated is not None:
            return self._with_ids_translated

        self._init_config(data)

        for line in data:
            line["event"] = self._event_descriptions.get(line.get("event id"))
            market = self._resolve_market(line)
            if market is not None:
                line["market"] = market
            result, profit, points = self._resolve_bet(line)
            if result is not None:
                line["result"] = result
            if profit is not None:
                line["profit"] = profit
            if points is not None:
                line["participant score"] = points
            line["sportsbook"] = self._sportsbooks.get(line.get("sportsbook id"))
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
