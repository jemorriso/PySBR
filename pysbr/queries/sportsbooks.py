from pysbr.queries.query import Query


class Sportsbooks(Query):
    def __init__(self, sportsbook_ids):
        super().__init__()
        self.name = "sportsbooks"
        self.arg_str = self._get_args("sportsbooks")
        self.args = {"sbids": sportsbook_ids}
        self.fields = self._get_fields("sportsbooks")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )
