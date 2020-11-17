from pysbr.queries.query import Query
import pysbr.utils as utils


class EventsByParticipantsRecent(Query):
    def __init__(self, participant_ids):
        # this query only gets the 5 most recent events for a participant.
        super().__init__()
        utils.make_list(participant_ids)
        self.name = "eventsInfoByParticipant"
        self.arg_str = self._get_args("participants")
        self.args = {"partids": participant_ids}
        self.fields = self._get_fields("event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["events"]
        self._sublist_keys = ["participants"]
        self._id_key = "event id"

    def _find_data(self):
        data = self._raw[self.name]
        cleaned_data = []
        for participant in data:
            cleaned_data.extend(participant["events"])

        return cleaned_data
