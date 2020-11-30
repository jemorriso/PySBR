from typing import List, Union

from pysbr.queries.query import Query
import pysbr.utils as utils


class EventsByParticipantsRecent(Query):
    """Get the 5 most recent events for a number of participants.

    5 is an arbitrary number enforced by the query on the server side.

    All event queries return information about matching events including date and time,
    location, participants, and associated ids.

    Args:
        participant_ids: SBR participant id or list of participant ids.
    """

    @Query.typecheck
    def __init__(self, participant_ids: Union[List[int]]):
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
        self._sublist_keys = ["participants", "scores"]
        self._id_key = "event id"

    def _find_data(self):
        """Return a reference to to the relevant part of the query response.

        Overrides Query._find_data() because the structure of the returned data is
        different than most other queries.
        """
        data = self._raw[self.name]
        cleaned_data = []
        for participant in data:
            cleaned_data.extend(participant["events"])

        return cleaned_data
