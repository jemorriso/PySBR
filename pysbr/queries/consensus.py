from pysbr.queries.query import Query


class Consensus(Query):
    def __init__(self, event_ids, market_ids):
        super().__init__()
        self.name = "consensus"
        self.arg_str = self._get_args("lines")
        self.args = {"eids": event_ids, "mtids": market_ids}
        self.fields = self._get_fields("consensus")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )