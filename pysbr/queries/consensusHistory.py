from typing import List, Union

from pysbr.queries.lines import Lines
from pysbr.queries.query import Query
import pysbr.utils as utils


class ConsensusHistory(Lines):
    """Get the consensus amongst SBR members for selected markets on an event.

    For events in some leagues and markets, SBR members can simulate a wager on the
    current line. The query response includes the number of wagers made on a line at a
    given price, and percentage of wagers made on each side of a bet. For certain
    markets volume' and 'total volume' are recorded where 'volume' refers to the average
    wager size, and 'total volume' is just volume multiplied by the # of wagers. For
    certain markets the number of whale bets made on a line is available.

    Note that the line available for members to make a wager is always from 5Dimes.
    The markets available for consensus history can be gotten from a league's config
    class, if it exists. In general, the 3 available markets are the moneyline, point
    spread, and total (all full-time).

    Args:
        event_id: SBR event id.
        market_ids: SBR betting market ids.
    """

    @Query.typecheck
    def __init__(self, event_id: int, market_ids: Union[List[int], int]):
        super().__init__()
        market_ids = utils.make_list(market_ids)
        self.name = "consensusHistory"
        self.arg_str = self._get_args("consensus_history")
        self.args = {"eid": event_id, "mtids": market_ids}
        self.fields = self._get_fields("consensus_history")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )
