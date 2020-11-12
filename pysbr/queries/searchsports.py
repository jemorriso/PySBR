from pysbr.queries.query import Query


# only returns five first results, and only for upcoming events
class SearchSports(Query):
    def __init__(self, search_term):
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
