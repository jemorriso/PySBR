from pysbr.queries.query import Query
import pysbr.utils as utils


class MarketsByMarketIds(Query):
    def __init__(self, market_ids, sport_id):
        super().__init__()
        market_ids = utils.make_list(market_ids)
        self.name = "marketTypesById"
        self.arg_str = self._get_args("market_ids")
        self.args = {"mtids": market_ids, "spids": [sport_id]}
        self.fields = self._get_fields("markets_by_id")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._id_key = "market id"
