from pysbr.queries.query import Query


class EventsByEventGroup(Query):
    @Query.typecheck
    def __init__(
        self, league_id: int, event_group_id: int, season_id: int, market_id: int
    ):
        super().__init__()
        self.name = "eventsByEventGroupV2"
        self.arg_str = self._get_args("event_group")
        self.args = {
            # breaks without league id
            "lid": league_id,
            # returns multiple seasons if not provided
            "seid": season_id,
            "egid": event_group_id,
            # mtid is a required argument for EventsByEventGroupV2
            "mtid": market_id,
        }
        self.fields = self._get_fields("event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["events"]
        self._sublist_keys = ["participants"]
        self._id_key = "event id"
