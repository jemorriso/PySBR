from pysbr.queries.query import Query


class LeagueHierarchy(Query):
    def __init__(self, league_id):
        # TODO: season id?
        super().__init__()
        self.name = "leagueHierarchy"
        self.arg_str = self._get_args("league_hierarchy")
        self.args = {"lids": [league_id]}
        self.fields = self._get_fields("league_hierarchy")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._id_key = "team id"
