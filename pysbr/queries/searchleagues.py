from pysbr.queries.query import Query


# only returns five first results, and only for upcoming events
class SearchLeagues(Query):
    @Query.typecheck
    def __init__(self, search_term: str):
        super().__init__()
        self.name = "multipleSearch"
        self.arg_str = self._get_args("multiple_search")
        self.args = {"search_term": [search_term]}
        self.fields = self._get_fields("search_league")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["searchLeague"]
        self._id_key = "league id"
