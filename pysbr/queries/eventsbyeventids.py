from pysbr.queries.query import Query


class EventsByEventIds(Query):
    def __init__(self, event_ids):
        super().__init__()
        self.name = "eventsV2"
        self.arg_str = self._get_args("event_ids")
        self.args = {"eids": event_ids}
        self.fields = self._get_fields("event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )
