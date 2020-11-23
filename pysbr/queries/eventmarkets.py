from pysbr.queries.query import Query


class EventMarkets(Query):
    """Get the event markets available on a particular event.

    The response contains only the market ids, not their names.

    Args:
        event_id: SBR event id.
    """

    @Query.typecheck
    def __init__(self, event_id: int):
        super().__init__()
        self.name = "eventMarkets"
        self.arg_str = self._get_args("event_id")
        self.args = {"eid": event_id}
        self.fields = self._get_fields("market_types")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["mtids"]
