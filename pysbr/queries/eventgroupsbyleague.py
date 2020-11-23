from pysbr.queries.query import Query


class EventGroupsByLeague(Query):
    """Get the event groups available on a particular league.

    Event groups refer to things like Week 1 of the NFL season, or the US Open, so you
    can use this in conjunction with EventsByEventGroups to get information about a
    group of events. Event group id, name, start date and end date are included in the
    query response.

    Args:
        league_id: SBR league id.
    """

    @Query.typecheck
    def __init__(self, league_id: int):
        super().__init__()
        self.name = "eventGroupsByLeague"
        self.arg_str = self._get_args("league_id")
        self.args = {"lid": league_id}
        self.fields = self._get_fields("event_group")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._id_key = "event group id"
