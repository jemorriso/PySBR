from pysbr.queries.query import Query


class LeagueMarkets(Query):
    def __init__(self, league_id):
        super().__init__()
        self.name = "leagueMarkets"
        self.arg_str = self._get_args("league_id")
        self.args = {"lid": [league_id]}
        self.fields = self._get_fields("league_market")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )
