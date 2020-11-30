from datetime import datetime
from typing import List, Union

from pysbr.queries.query import Query
import pysbr.utils as utils


class EventsByDateRange(Query):
    """Get events for selected leagues over a range of dates.

    All event queries return information about matching events including date and time,
    location, participants, and associated ids.

    Args:
        league_ids: SBR league id or list of league ids.
        start: Python datetime object representing the start date to search.
        end: Python datetime object representing the end date to search.
    """

    @Query.typecheck
    def __init__(
        self, league_ids: Union[List[int], int], start: datetime, end: datetime
    ):
        super().__init__()
        league_ids = utils.make_list(league_ids)
        self.name = "eventsV2"
        self.arg_str = self._get_args("date_range")
        self.args = {
            "lids": league_ids,
            "start": utils.datetime_to_timestamp(start),
            "end": utils.datetime_to_timestamp(end),
        }
        self.fields = self._get_fields("event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["events"]
        self._sublist_keys = ["participants", "scores"]
        self._id_key = "event id"
