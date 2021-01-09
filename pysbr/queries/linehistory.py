from typing import List, Union

from pysbr.queries.lines import Lines
from pysbr.queries.query import Query
import pysbr.utils as utils


class LineHistory(Lines):
    """Get the line history of an event and market for a particular sportsbook.

    The complete history of line movement for an event, market, and sportsbook is
    returned by the query. Both American and decimal odds are included.

    The query to the server does not work without at least one participant id of a
    participant in the event. If you only include 1 participant id, the query will only
    return the history for the side of the bet relevant to that participant id.

    Args:
        event_id: SBR event id.
        market_id: SBR betting market id.
        sportsbook_id: SBR sportsbook id.
        participant_ids: List of participant ids of participants in the event, or just
        one participant id.
    """

    @Query.typecheck
    def __init__(
        self,
        event_id: int,
        market_id: int,
        sportsbook_id: int,
        participant_ids: Union[List[int], int],
    ):
        # only need 1 participant id, it's dumb
        super().__init__()
        utils.make_list(participant_ids)
        self.name = "lineHistory"
        self.arg_str = self._get_args("line_history")
        self.args = {
            "eid": event_id,
            "mtid": market_id,
            "paid": sportsbook_id,
            # partids is required by the lineHistory query
            "partids": participant_ids,
        }
        self.fields = self._get_fields("line_history")

        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

    def _find_data(self):
        lines = self._raw[self.name]
        cleaned_lines = []
        for el in lines:
            cleaned_lines.extend(el["lines"])

        return cleaned_lines
