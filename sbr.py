import json
from string import Template
from inspect import cleandoc

from gql import gql, Client
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

    # @staticmethod
    # def _build_fields_str(d, i=0):
    #     # f-string expression part cannot include a backslash
    #     tab = "    "
    #     s = ""

    #     def _recurse(x, i):
    #         if type(x) is dict:
    #             for k, v in x.items():
    #                 # I don't know why it is forcing me to use 'nonlocal' keyword
    #                 nonlocal s
    #                 s += f"{tab*i}{k} {{\n"
    #                 _recurse(v, i + 1)
    #                 s += f"{tab*i}}}\n"
    #         elif type(x) is list:
    #             for el in x:
    #                 if type(el) is dict:
    #                     _recurse(el, i)
    #                 else:
    #                     s += f"{tab*i}{el}\n"

    #     _recurse(d, i)
    #     # trim first and last newline
    #     return s.strip()

    # @staticmethod
    # def _build_args_str(d, i=0):
    #     # f-string expression part cannot include a backslash
    #     tab = "    "
    #     s = ""

    #     def _recurse(x, i):
    #         if type(x) is dict:
    #             nonlocal s
    #             s += "{\n"
    #             for k, v in x.items():
    #                 s += f"{tab*i}{k}: "
    #                 if type(v) is dict or type(v) is list:
    #                     _recurse(v, i + 1)
    #                 else:
    #                     s += f"{v}\n"
    #             s += f"{tab*i}}}\n"
    #         elif type(x) is list:
    #             s += "[\n"
    #             for el in x:
    #                 if type(el) is dict or type(el) is list:
    #                     _recurse(el, i)
    #                 else:
    #                     s += f"{tab*i}{el}\n"
    #             s += f"{tab*i}]\n"

    #     _recurse(d, i)
    #     # trim whitespace, and then first and last lines, which contain unnecessary
    #     # braces... then remove unnecessary first tab :(
    #     return "\n".join(s.rstrip().split("\n")[1:-1]).lstrip()

    @staticmethod
    def _detailed_event_fields():
        return """
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

    @staticmethod
    def _simple_event_fields():
        return """
            events {
                eid
            }
        """

    @staticmethod
    def _build_query_string(q_name, q_fields, q_args=None):
        return Template(
            cleandoc(
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
                "q_args": "" if q_args is None else q_args,
                "q_fields": q_fields,
            }
        )

    @classmethod
    def _execute_query(cls):
        return SBR.client.execute(gql(q))

    # @classmethod
    # def _events_range_execute(cls, lid, s, e, fields):
    #     return SBR.client.execute(
    #         gql(
    #             Template(
    #                 """
    #             query getEventsV2 {
    #                 eventsV2(
    #                     lid: $lids
    #                     dt: {
    #                         between: [$start, $end]
    #                     }
    #                 ) {
    #                     $fields
    #                 }
    #             }
    #             """
    #             ).substitute(
    #                 **{
    #                     "lids": [lid],
    #                     "start": s,
    #                     "end": e,
    #                     "fields": fields,
    #                 }
    #             )
    #         )
    #     )

    @classmethod
    def get_events_by_date_range_detailed(cls, league_id, start_dt, end_dt):
        q = SBR._build_query_string(
            "eventsV2",
            SBR._detailed_event_fields(),
            q_args=Template(
                """
                "lid:": $lids,
                "dt:": {
                    "between": {
                        [
                            $start,
                            $end
                        ]
                    }
                }
            """
            ).substitute(
                {
                    "lids": [league_id],
                    "start": Utils.datetime_to_timestamp(start_dt),
                    "end": Utils.datetime_to_timestamp(end_dt),
                }
            ),
        )
        result = SBR._execute_query(q)
        return result["eventsV2"]

    @classmethod
    def get_events_by_date_range(cls, league_id, start_dt, end_dt):
        result = SBR._execute_query(
            "eventsV2",
            SBR._simple_event_fields(),
            q_args={
                "lid": [league_id],
                "dt": {
                    "between": [
                        Utils.datetime_to_timestamp(start_dt),
                        Utils.datetime_to_timestamp(end_dt),
                    ]
                },
            },
        )
        # result = SBR._events_range_execute(
        #     league_id, start_dt, end_dt, SBR._simple_event_fields()
        # )
        return result["eventsV2"]

    @classmethod
    def get_league_markets(cls, league_id):
        """Get the market type ids available on a particular league.

        Args:
            league_id (int): The SBR league id

        Returns:
            list of int: The market ids for the league.
        """
        q = Template(
            """
            query getLeagueMarketIds {
                leagueMarkets(lid: $lids) {
                    mtid
                }
            }
        """
        )
        result = SBR.client.execute(gql(q.substitute(lids=[league_id])))
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
            (list of dict): Each dictionary contains information about each market.
        """
        q = Template(
            """
            query getMarketTypesById {
                marketTypesById(mtid: $mtids, spid: $spids) {
                    mtid
                    spid
                    nam
                    des
                }
            }
            """
        )
        result = SBR.client.execute(
            gql(q.substitute(**{"mtids": market_ids, "spids": [sport_id]}))
        )
        return result["marketTypesById"]
