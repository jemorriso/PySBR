import json
import copy

from pysbr.queries.query import Query


# only returns five first results, and only for upcoming events
# cannot search by location, league etc. Only by event participants
class SearchEvents(Query):
    """Get up to 5 upcoming events matching a given search term.

    The search term should be a string referring to a team or participant's name. Case
    is ignored. The max number of upcoming events returned is enforced by the server.

    This query response has a different structure than other event queries, but still
    includes information about date and time, participants, description, and associated
    ids.

    Example search terms:
        'Seattle' (this will return information about all Seattle-based teams)
        'Seahawks'
        'Federer'
        'federer'
        'roger federer'
        'tiz the law' (horse racing)

    Args:
        search_term: String referring to team or participant of interest.

    """

    @Query.typecheck
    def __init__(self, search_term: str):
        super().__init__()
        self.name = "searchEvent"
        self.arg_str = self._get_args("search_event")
        self.args = {"search_term": [search_term]}
        self.fields = self._get_fields("search_event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._sublist_keys = ["participants"]
        self._id_key = "event id"

    def _string_to_json(self, data, key):
        for el in data:
            try:
                el[key] = json.loads(el[key])
            except TypeError:
                pass

    def _copy_and_translate_data(self):
        data = copy.deepcopy(self._find_data())
        self._string_to_json(data, "eventParticipants")
        return self._translate_dict(data)
