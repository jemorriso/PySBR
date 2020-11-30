from datetime import datetime
from typing import List, Union

from pysbr.queries.query import Query
import pysbr.utils as utils


class EventsByDate(Query):
    """Get events for selected leagues on a certain date.

    All event queries return information about matching events including date and time,
    location, participants, and associated ids.

    Args:
        league_ids: SBR league id or list of league ids.
        dt: Python datetime object representing the date of interest. Events searched
            are those in the range [dt, dt + 24 hours].
    """

    @Query.typecheck
    def __init__(self, league_ids: Union[List[int], int], dt: datetime):
        super().__init__()
        league_ids = utils.make_list(league_ids)
        self.name = "eventsByDateNew"
        self.arg_str = self._get_args("date")
        self.args = {"lids": league_ids, "timestamp": utils.datetime_to_timestamp(dt)}
        self.fields = self._get_fields("event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["events"]
        self._sublist_keys = ["participants", "scores"]
        self._id_key = "event id"
