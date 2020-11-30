from pysbr.queries.query import Query


class EventsByMatchup(Query):
    """Get events where two participants matched up against one another.

    This query returns up to n previous head-to-head matches between two participants,
    where n is equal to the count argument. It works with teams or individuals.

    Example:
        EventsByMatchup(1548, 1547, 5) returns from the server the last 5 games between
        the Seahawks and the 49ers.

    All event queries return information about matching events including date and time,
    location, participants, and associated ids.

    Args:
        participant_id1: SBR participant id of one of the participants in the matchup.
            It may refer to a team or an individual.
        participant_id2: SBR participant id of the other participant in the matchup. It
            may refer to a team or an individual.
        count: The max number of events to return, counting in reverse chronological
            order from present.
    """

    @Query.typecheck
    def __init__(self, participant_id1: int, participant_id2: int, count: int):
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
        self._sublist_keys = ["participants", "scores"]
        self._id_key = "event id"
