from pysbr.queries.lines import Lines
import pysbr.utils as utils


class BestLines(Lines):
    def __init__(self, event_ids, market_ids):
        super().__init__()
        event_ids = utils.make_list(event_ids)
        market_ids = utils.make_list(market_ids)
        self.name = "bestLines"
        self.arg_str = self._get_args("lines")
        self.args = {"eids": event_ids, "mtids": market_ids}
        self.fields = None
        self._raw = self._build_and_execute_query(
            self.name, q_arg_str=self.arg_str, q_args=self.args
        )
