from pysbr.queries.query import Query


class LeagueHierarchy(Query):
    """Get the league hierarchy for a particular league.

    The query returns a list of dicts, each representing a team in the league. Each
    dict contains the team id, and information about what conference and division the
    team belongs to.

    Many leagues return an empty list, for example, ATP and many soccer leagues.

    Args:
        league_id: SBR league id.
    """

    @Query.typecheck
    def __init__(self, league_id: int):
        super().__init__()
        self.name = "leagueHierarchy"
        self.arg_str = self._get_args("league_hierarchy")
        self.args = {"lids": [league_id]}
        self.fields = self._get_fields("league_hierarchy")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._id_key = "team id"
