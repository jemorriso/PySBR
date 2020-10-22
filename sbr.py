import json
from string import Template

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from utils import Utils


class SBR:
    """Functions for querying the SportsBookReview GraphQL endpoint.

    Note:
        Queries are using Python Template strings rather than gql
        variables due to issues passing in certain variables, where
        they work when they are constants.

    """

    _transport = RequestsHTTPTransport(
        url="https://www.sportsbookreview.com/ms-odds-v2/odds-v2-service"
    )
    # client = Client(transport=_transport, fetch_schema_from_transport=True)
    client = Client(transport=_transport, fetch_schema_from_transport=False)

    with open("json/sportsbooks.json") as f:
        sportsbooks = json.load(f)

    def __init__(self):
        """Initialize SBR class with user settings."""

        with open("json/user.json") as f:
            self.user = json.load(f)

    @staticmethod
    def _parse_response(response):
        """Take query result and parse it into a dictionary of lists.

        Args:
            response (dict of str: list): the result of the query executed by the client

        Returns:
            (dict of list): For each key in the response dict, add a corresponding
            entry in parsed with the list of values
        """

        def _recurse(d):
            for k, v in d.items():
                if type(v) is list:
                    if type(v[0]) is dict:
                        for k1 in v[0].keys():
                            parsed[k1] = [x[k1] for x in v]
                elif type(v) is dict:
                    _recurse(v)

        parsed = {}
        _recurse(response)
        return parsed

    @staticmethod
    def _detailed_event_fields():
        return Utils.str_format(
            """
            events {
                des
                cit
                cou
                es
                dt
                eid
                st
                participants {
                    partid
                    ih
                    source {
                        ... on Team {
                            nam
                            nn
                            sn
                            abbr
                        }
                    }
                }
            }
        """
        )

    #     @staticmethod
    #     def _simple_event_fields():
    #         return Utils.str_format(
    #             """
    #             events {
    #                 eid
    #             }
    #         """
    #         )

    @staticmethod
    def _build_query_string(q_name, q_fields, q_args=None):
        """Build up the GraphQL query string.

        Args:
            q_name (str): The name of the query object to be queried.
            q_fields (str): The fields to return.
            q_args (str, optional): The arg names to pass to the query. Defaults to
                None.

        Returns:
            str: The query string ready to be substituted using Template.substitute()
        """
        return Template(
            Utils.str_format(
                """
                query {
                    $q_name(
                        $q_args
                    ) {
                        $q_fields
                    }
                }
            """
            )
        ).substitute(
            **{
                "q_name": q_name,
                "q_args": ""
                if q_args is None
                else Utils.str_format(q_args, indent_=2, dedent_l1=True),
                "q_fields": Utils.str_format(q_fields, indent_=2, dedent_l1=True),
            }
        )

    @classmethod
    def _execute_query(cls, q, subs):
        """Execute a GraphQL query.

        Args:
            q (str): The query string.
            subs (dict): The substitutions to make. Each key must match a Template
                placeholder, with the value being what gets substituted into the string.

        Returns:
            dict: The result of the query.
        """
        return SBR.client.execute(gql(Template(q).substitute(subs)))

    @classmethod
    def get_league_markets(cls, league_id):
        """Get the market type ids available on a particular league.

        Args:
            league_id (int): The SBR league id

        Returns:
            list of int: The market ids for the league.
        """
        result = SBR._execute_query(
            SBR._build_query_string("leagueMarkets", "mtid", "lid: $lids"),
            {"lids": [league_id]},
        )
        parsed = SBR._parse_response(result)
        return parsed["mtid"]

    @classmethod
    def get_market_types_by_id(cls, market_ids, sport_id):
        """Get information about market types for a particular sport.

        Args:
            market_ids (list of int): Market ids to get information about.
            sport_id (int): The sport id for the sport you are interested in. This
            is necessary because market ids are the same across sports.

        Returns:
            list of dict: Each dictionary contains information about each market.
        """
        result = SBR._execute_query(
            SBR._build_query_string(
                "marketTypesById", "mtid, spid, nam, des", "mtid: $mtids, spid: $spids"
            ),
            {"mtids": market_ids, "spids": [sport_id]},
        )
        return result["marketTypesById"]

    #     @classmethod
    #     def get_events_by_date_range_detailed(cls, league_id, start_dt, end_dt):
    #         q = SBR._build_query_string(
    #             "eventsV2",
    #             SBR._detailed_event_fields(),
    #             q_args=Template(
    #                 """
    #                 "lid:": $lids,
    #                 "dt:": {
    #                     "between": {
    #                         [
    #                             $start,
    #                             $end
    #                         ]
    #                     }
    #                 }
    #             """
    #             ).substitute(
    #                 {
    #                     "lids": [league_id],
    #                     "start": Utils.datetime_to_timestamp(start_dt),
    #                     "end": Utils.datetime_to_timestamp(end_dt),
    #                 }
    #             ),
    #         )
    #         result = SBR._execute_query(q)
    #         return result["eventsV2"]

    #     @classmethod
    #     def get_events_by_date_range(cls, league_id, start_dt, end_dt):
    #         result = SBR._execute_query(
    #             "eventsV2",
    #             SBR._simple_event_fields(),
    #             q_args={
    #                 "lid": [league_id],
    #                 "dt": {
    #                     "between": [
    #                         Utils.datetime_to_timestamp(start_dt),
    #                         Utils.datetime_to_timestamp(end_dt),
    #                     ]
    #                 },
    #             },
    #         )
    #         # result = SBR._events_range_execute(
    #         #     league_id, start_dt, end_dt, SBR._simple_event_fields()
    #         # )
    #         return result["eventsV2"]