from pysbr.queries.query import Query


class LeaguesByLeagueIds(Query):
    def __init__(self, league_ids):
        super().__init__()
        self.name = "leagues"
        self.arg_str = self._get_args("league_ids")
        self.args = {"lids": league_ids}
        self.fields = self._get_fields("leagues")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )
