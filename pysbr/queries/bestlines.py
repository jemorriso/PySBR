from typing import List, Union

from pysbr.queries.lines import Lines
from pysbr.queries.query import Query
import pysbr.utils as utils


class BestLines(Lines):
    """Get the best lines offered by any sportsbook for a number of events and markets.

    For each event, participant and market combination, the best line offered by any of
    sportsbooks tracked by SBR is in the response. The date and time that the line was
    offered is also recorded. Both American and decimal odds are included.

    Sometimes the best line returned is from a sportsbook that is not active on SBR. In
    this case it is not easy to figure out which book it came from.

    Args:
        event_ids: SBR event id or list of event ids.
        market_ids: SBR betting market id or list of market ids.
    """

    @Query.typecheck
    def __init__(
        self, event_ids: Union[List[int], int], market_ids: Union[List[int], int]
    ):
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
