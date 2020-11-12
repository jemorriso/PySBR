from pysbr.queries.query import Query


class EventsByMatchup(Query):
    def __init__(self, participant_id1, participant_id2, count):
        super().__init__()
        self.name = "lastMatchupsByParticipants"
        self.arg_str = self._get_args("matchup")
        self.args = {
            "partid1": participant_id1,
            "partid2": participant_id2,
            "limit": count,
        }
        self.fields = self._get_fields("event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["events"]
        self._sublist_keys = ["participants"]
        self._id_key = "event id"
