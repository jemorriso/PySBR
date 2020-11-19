from typing import List, Union

from pysbr.queries.query import Query
import pysbr.utils as utils


class EventsByEventIds(Query):
    @Query.typecheck
    def __init__(self, event_ids: Union[List[int], int]):
        super().__init__()
        utils.make_list(event_ids)
        self.name = "eventsV2"
        self.arg_str = self._get_args("event_ids")
        self.args = {"eids": event_ids}
        self.fields = self._get_fields("event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["events"]
        self._sublist_keys = ["participants"]
        self._id_key = "event id"
