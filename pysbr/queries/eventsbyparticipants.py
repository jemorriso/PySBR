from pysbr.queries.query import Query


class EventsByParticipants(Query):
    def __init__(self, participant_ids):
        # this query only gets the 5 most recent events for a participant.
        super().__init__()
        self.name = "eventsInfoByParticipant"
        self.arg_str = self._get_args("participants")
        self.args = {"partids": participant_ids}
        self.fields = self._get_fields("event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )
