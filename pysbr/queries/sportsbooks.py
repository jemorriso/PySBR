from typing import List, Union

from pysbr.queries.query import Query
import pysbr.utils as utils


class Sportsbooks(Query):
    """Get information about a number of sportsbooks from their system ids.

    Note that the id returned from lines-related queries is called 'sportsbook id' by
    this application, which is translated from 'paid', the name returned from SBR.
    There is another sportsbook id that is only used by the 'Sportsbooks' query, that
    is called 'system sportsbook id' by this application, which is translated from
    'sbid', the name returned from SBR. The system sportsbook id is not used by other
    parts of the application.

    Sportsbook name, id (paid), and system id (sbid) are included in the response.

    Args:
        system_sportsbook_ids:  The system ids of the sportsbooks of interest.
    """

    @Query.typecheck
    def __init__(self, system_sportsbook_ids: Union[List[int], int]):
        super().__init__()
        system_sportsbook_ids = utils.make_list(system_sportsbook_ids)
        self.name = "sportsbooks"
        self.arg_str = self._get_args("sportsbooks")
        self.args = {"sbids": system_sportsbook_ids}
        self.fields = self._get_fields("sportsbooks")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._id_key = "sportsbook id"
