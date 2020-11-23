from pysbr.queries.query import Query


class SearchLeagues(Query):
    """Get up to 5 leagues matching a given search term.

    The search term can be part of a league's full name or abbreviation. Case is
    ignored. The max number of upcoming events returned is enforced by the server.

    The query response includes league name, region, and id, as well as sport id.

    Example search terms:
        'NFL'
        'National Football League'
        'National'
        'nfl'

    Args:
        search_term: String referring to the league of interest.
    """

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
