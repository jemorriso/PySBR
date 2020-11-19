from typing import List, Union

from pysbr.queries.lines import Lines
from pysbr.queries.query import Query
import pysbr.utils as utils


class OpeningLines(Lines):
    @Query.typecheck
    def __init__(
        self,
        event_ids: Union[List[int], int],
        market_ids: Union[List[int], int],
        sportsbook_id: int,
    ):
        super().__init__()
        event_ids = utils.make_list(event_ids)
        market_ids = utils.make_list(market_ids)
        self.name = "openingLines"
        self.arg_str = self._get_args("lines_2")
        self.args = {
            "eids": event_ids,
            "mtids": market_ids,
            "paid": sportsbook_id,
        }
        self.fields = None
        self._raw = self._build_and_execute_query(
            self.name, q_arg_str=self.arg_str, q_args=self.args
        )
