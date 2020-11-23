from typing import List, Union

from pysbr.queries.lines import Lines
from pysbr.queries.query import Query
import pysbr.utils as utils


class OpeningLines(Lines):
    """Get the opening lines offered by a sportsbook for a number of events and markets.

    The date and time that the line was offered is also recorded. Both American and
    decimal odds are included.

    Args:
        event_ids: SBR event id or list of event ids.
        market_ids: SBR betting market id or list of market ids.
        sportsbook_id: SBR sportsbook id.
    """

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
