from typing import List, Union

from pysbr.queries.query import Query
import pysbr.utils as utils


class Sportsbooks(Query):
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
