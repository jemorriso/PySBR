from pysbr.queries.lines import Lines
import pysbr.utils as utils


class Consensus(Lines):
    def __init__(self, event_ids, market_ids):
        super().__init__()
        event_ids = utils.make_list(event_ids)
        market_ids = utils.make_list(market_ids)
        self.name = "consensus"
        self.arg_str = self._get_args("lines")
        self.args = {"eids": event_ids, "mtids": market_ids}
        self.fields = self._get_fields("consensus")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

    def _clean_lines(self, *args):
        pass
