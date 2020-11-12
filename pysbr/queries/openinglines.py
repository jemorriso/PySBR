from pysbr.queries.lines import Lines


class OpeningLines(Lines):
    def __init__(self, event_ids, market_ids, provider_account_id=None):
        super().__init__()
        self.name = "openingLines"
        if provider_account_id is None:
            self.arg_str = self._get_args("lines")
            self.args = {"eids": event_ids, "mtids": market_ids}
        else:
            self.arg_str = self._get_args("lines_2")
            self.args = {
                "eids": event_ids,
                "mtids": market_ids,
                "paid": provider_account_id,
            }
        self.fields = None
        self._raw = self._build_and_execute_query(
            self.name, q_arg_str=self.arg_str, q_args=self.args
        )
