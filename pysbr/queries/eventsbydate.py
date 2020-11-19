from datetime import datetime
from typing import List, Union

from pysbr.queries.query import Query
import pysbr.utils as utils


# TODO: add by league to title?
class EventsByDate(Query):
    @Query.typecheck
    def __init__(self, league_id: Union[List[int], int], dt: datetime):
        super().__init__()
        self.name = "eventsByDateNew"
        self.arg_str = self._get_args("date")
        self.args = {"lids": [league_id], "timestamp": utils.datetime_to_timestamp(dt)}
        self.fields = self._get_fields("event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["events"]
        self._sublist_keys = ["participants"]
        self._id_key = "event id"
