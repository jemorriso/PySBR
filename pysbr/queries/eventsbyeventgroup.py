from pysbr.queries.query import Query


class EventsByEventGroup(Query):
    """Get events for a particular league and event group.

    All event queries return information about matching events including date and time,
    location, participants, and associated ids.

    season_id is a required argument because event group ids are not unique to a season.
    market_id is a required argument to the query object on the SBR server.

    Args:
        league_id: SBR league id.
        event_group_id: SBR event group id.
        season_id: SBR season id. The easiest way to find a season id is by making an
            event query about an event that belongs to the season in question, and
            getting the season id from that event.
        market_id: SBR market id. You can use a league's config class to get the
            default market id for a given sport.
    """

    @Query.typecheck
    def __init__(
        self, league_id: int, event_group_id: int, season_id: int, market_id: int
    ):
        super().__init__()
        self.name = "eventsByEventGroupV2"
        self.arg_str = self._get_args("event_group")
        self.args = {
            # breaks without league id
            "lid": league_id,
            # returns multiple seasons if not provided
            "seid": season_id,
            "egid": event_group_id,
            # mtid is a required argument for EventsByEventGroupV2
            "mtid": market_id,
        }
        self.fields = self._get_fields("event")
        self._raw = self._build_and_execute_query(
            self.name, self.fields, self.arg_str, self.args
        )

        self._subpath_keys = ["events"]
        self._sublist_keys = ["participants", "scores"]
        self._id_key = "event id"
