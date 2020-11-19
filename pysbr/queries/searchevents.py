import json
import copy

from pysbr.queries.query import Query


# only returns five first results, and only for upcoming events
# cannot search by location, league etc. Only by event participants
class SearchEvents(Query):
    @Query.typecheck
    def __init__(self, search_term: str):
        super().__init__()
        self.name = "searchEvent"
        self.arg_str = self._get_args("search_event")
        self.args = {"search_term": [search_term]}
        self.fields = self._get_fields("search_event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._sublist_keys = ["event participants"]
        self._id_key = "event id"

    def _string_to_json(self, data, key):
        for el in data:
            try:
                el[key] = json.loads(el[key])
            except TypeError:
                pass

    def _copy_and_translate_data(self):
        data = copy.deepcopy(self._find_data())
        self._string_to_json(data, "eventParticipants")
        return self._translate_dict(data)
