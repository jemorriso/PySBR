from typing import Optional, List, Union
from datetime import datetime

from pysbr.queries.query import Query
import pysbr.utils as utils


class EventsByParticipants(Query):
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
        self._sublist_keys = ["participants"]
        self._id_key = "event id"

    def _league_args(self, start, end, league_id):
        q_arg_str = self._get_args("date_range")
        q_args = {
            "lids": [league_id],
            "start": utils.datetime_to_timestamp(start),
            "end": utils.datetime_to_timestamp(end),
        }
        return q_arg_str, q_args

    def _sport_args(self, start, end, sport_id):
        q_arg_str = self._get_args("date_range_sport")
        q_args = {
            "spids": [sport_id],
            "start": utils.datetime_to_timestamp(start),
            "end": utils.datetime_to_timestamp(end),
        }
        return q_arg_str, q_args

    def _filter_events(self, participant_ids, start, end, league_id, sport_id):
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
