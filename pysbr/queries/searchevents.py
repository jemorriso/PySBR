from pysbr.queries.query import Query


# only returns five first results, and only for upcoming events
# cannot search by location, league etc. Only by event participants
class SearchEvents(Query):
    def __init__(self, search_term):
        super().__init__()
        self.name = "searchEvent"
        self.arg_str = self._get_args("search_event")
        self.args = {"search_term": [search_term]}
        self.fields = self._get_fields("search_event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )
