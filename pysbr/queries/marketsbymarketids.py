from typing import List, Union

from pysbr.queries.query import Query
import pysbr.utils as utils


class MarketsByMarketIds(Query):
    """Get information about a number of leagues from their league ids.

    Market name, description, and market type id are included in the response.

    Args:
        market_ids: SBR market id or list of market ids.
        sport_id: SBR sport id.
    """

    @Query.typecheck
    def __init__(self, market_ids: Union[List[int]], sport_id: int):
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
