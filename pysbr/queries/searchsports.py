from pysbr.queries.query import Query


class SearchSports(Query):
    """Get up to 5 sports matching a given search term.

    Case is ignored. The max number of upcoming events returned is enforced by the
    server.

    The query response includes sport name and id.

    Args:
        search_term: String referring to the league of interest.
    """

    @Query.typecheck
    def __init__(self, search_term: str):
        super().__init__()
        self.name = "multipleSearch"
        self.arg_str = self._get_args("search_sport")
        self.args = {"search_term": [search_term]}
        self.fields = self._get_fields("search_sport")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["searchSport"]
        self._id_key = "sport id"
