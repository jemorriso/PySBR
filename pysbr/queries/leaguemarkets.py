from pysbr.queries.query import Query


class LeagueMarkets(Query):
    """Get the betting markets available for a particular league.

    Only market ids are returned by the query, without market names. For some leagues,
    this query returns many more market ids than the markets found on SBR.

    Args:
        league_id: SBR league id.
    """

    @Query.typecheck
    def __init__(self, league_id: int):
        super().__init__()
        self.name = "leagueMarkets"
        self.arg_str = self._get_args("league_id")
        self.args = {"lid": [league_id]}
        self.fields = self._get_fields("league_market")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._id_key = "market id"
