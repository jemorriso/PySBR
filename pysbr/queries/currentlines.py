from typing import List, Union

from pysbr.queries.lines import Lines
from pysbr.queries.query import Query
import pysbr.utils as utils


class CurrentLines(Lines):
    """Get the current lines offered by sportsbooks for a number of events and markets.

    For each sportsbook, event, participant and market combination, the most recent
    line offered by the book is in the response. Both American and decimal odds are
    included.

    Args:
        event_ids: SBR event id or list of event ids.
        market_ids: SBR betting market id or list of market ids.
        sportsbook_ids: SBR sportsbook id or list of sportsbook ids.
    """

    @Query.typecheck
    def __init__(
        self,
        event_ids: Union[List[int], int],
        market_ids: Union[List[int], int],
        sportsbook_ids: Union[List[int], int],
    ):
        super().__init__()
        event_ids = utils.make_list(event_ids)
        market_ids = utils.make_list(market_ids)
        sportsbook_ids = utils.make_list(sportsbook_ids)
        self.name = "currentLines"
        self.arg_str = self._get_args("lines_3")
        self.args = {
            "eids": event_ids,
            "mtids": market_ids,
            "paids": sportsbook_ids,
        }
        self.fields = None
        self._raw = self._build_and_execute_query(
            self.name, q_arg_str=self.arg_str, q_args=self.args
        )
