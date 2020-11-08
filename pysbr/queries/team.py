from pysbr.queries.query import Query


class Team(Query):
    def __init__(self, team_id):
        super().__init__()
        self.name = "team"
        self.arg_str = self._get_args("team_id")
        self.args = {"tmid": team_id}
        self.fields = self._get_fields("team")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )
