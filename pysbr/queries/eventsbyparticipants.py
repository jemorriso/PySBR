from typing import Optional, List, Union, Tuple, Dict
from datetime import datetime

from pysbr.queries.query import Query
import pysbr.utils as utils


class EventsByParticipants(Query):
    """Get events for a number of participants over a given date range.

    The query returns all events in the date range in which at least one of the
    participants in the participant id list competed in.

    This query makes two requests to the server; one to get all the event and
    participant ids over the date range, and then another to get the full event
    information for matching events.

    Because of the first query, either a league or sport id must be provided.

    All event queries return information about matching events including date and time,
    location, participants, and associated ids.

    Args:
        participant_ids: SBR participant id or list of participant ids. A participant
            id may refer to a team or an individual.
        start: Python datetime object representing the start date to search.
        end: Python datetime object representing the end date to search.
        league_id: SBR league id.
        sport_id: SBR sport id.
    """

    @Query.typecheck
    def __init__(
        self,
        participant_ids: Union[List[int], int],
        start: datetime,
        end: datetime,
        league_id: Optional[int] = None,
        sport_id: Optional[int] = None,
    ):
        if league_id is None and sport_id is None:
            raise ValueError("Either league_id or sport_id must not be None.")

        super().__init__()
        utils.make_list(participant_ids)
        event_ids = self._filter_events(
            participant_ids, start, end, league_id, sport_id
        )
        if not event_ids:
            return None

        self.name = "eventsV2"
        self.arg_str = self._get_args("event_ids")
        # TODO
        self.args = {"eids": event_ids}
        self.fields = self._get_fields("event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["events"]
        self._sublist_keys = ["participants", "scores"]
        self._id_key = "event id"

    def _league_args(
        self, start: datetime, end: datetime, league_id: int
    ) -> Tuple[str, Dict[str, Union[List[int], int]]]:
        """Get the arguments needed to query by league."""
        q_arg_str = self._get_args("date_range")
        q_args = {
            "lids": [league_id],
            "start": utils.datetime_to_timestamp(start),
            "end": utils.datetime_to_timestamp(end),
        }
        return q_arg_str, q_args

    def _sport_args(
        self, start: datetime, end: datetime, sport_id: int
    ) -> Tuple[str, Dict[str, Union[List[int], int]]]:
        """Get the arguments needed to query by sport."""
        q_arg_str = self._get_args("date_range_sport")
        q_args = {
            "spids": [sport_id],
            "start": utils.datetime_to_timestamp(start),
            "end": utils.datetime_to_timestamp(end),
        }
        return q_arg_str, q_args

    def _filter_events(
        self,
        participant_ids: List[int],
        start: datetime,
        end: datetime,
        league_id: int,
        sport_id: int,
    ) -> List[int]:
        """Make a query to get all events, and then filter out the relevant ones.

        The query gets all the events for a league or a sport over the given date range,
        and then a list of ids of events including at least one participant in the list
        is returned.
        """
        q_name = "eventsV2"
        q_arg_str, q_args = (
            self._league_args(start, end, league_id)
            if league_id is not None
            else self._sport_args(start, end, sport_id)
        )
        q_fields = self._get_fields("event_2")
        raw = self._build_and_execute_query(q_name, q_fields, q_arg_str, q_args)

        # filter out relevant events
        ids = []
        for e in raw["eventsV2"]["events"]:
            try:
                event_pids = [p["partid"] for p in e["participants"]]
                for pid in participant_ids:
                    if pid in event_pids:
                        ids.append(e["eid"])
            except KeyError:
                pass

        return ids
