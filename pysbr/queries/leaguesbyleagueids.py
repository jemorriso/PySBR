from typing import List, Union

from pysbr.queries.query import Query
import pysbr.utils as utils


class LeaguesByLeagueIds(Query):
    """Get information about a number of leagues from their league ids.

    League name, abbreviation, and sport id are included in the response.

    Args:
        league_ids: SBR league id or list of league ids.
    """

    @Query.typecheck
    def __init__(self, league_ids: Union[List[int], int]):
        super().__init__()
        league_ids = utils.make_list(league_ids)
        self.name = "leagues"
        self.arg_str = self._get_args("league_ids")
        self.args = {"lids": league_ids}
        self.fields = self._get_fields("leagues")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )
