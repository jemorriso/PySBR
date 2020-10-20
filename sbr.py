import json

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from utils import Utils


class SBR:
    """Functions for querying the SportsBookReview GraphQL endpoint."""

    _transport = RequestsHTTPTransport(
        url="https://www.sportsbookreview.com/ms-odds-v2/odds-v2-service"
    )
    # client = Client(transport=_transport, fetch_schema_from_transport=True)
    client = Client(transport=_transport, fetch_schema_from_transport=False)

    with open("json/sportsbooks.json") as f:
        sportsbooks = json.load(f)

    def __init__(self, odds_type="decimal"):
        """Initialize SBR class with convenience parameters.

        Args:
            odds_type (str, optional): 'decimal', 'american', or 'fractional' supported.
            Defaults to 'decimal'.
        """
        self.odds_type = odds_type

    @classmethod
    def _parse_response(cls, response):
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

    @classmethod
    def get_league_markets(cls, league_id):
        """Get the market type ids available on a particular league.

        Args:
            league_id (int): The SBR league id

        Returns:
            list of int: The market ids for the league.
        """
        query = gql(
            """
            query getLeagueMarketIds($lids: [Int]) {
                leagueMarkets(lid: $lids) {
                    mtid
                }
            }
        """
        )
        result = SBR.client.execute(query, variable_values={"lids": [league_id]})
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
        query = gql(
            """
            query getMarketTypesById($mtids: [Int], $spids: [Int]) {
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
            query, variable_values={"mtids": market_ids, "spids": [sport_id]}
        )
        return result["marketTypesById"]

    @classmethod
    def get_events_by_date(cls, market_ids, league_id, date_):
        # can't get float parameter to work, so use f-string instead
        query = gql(
            f"""
            query getEventsByLeagueGroup {{
                eventsByDateByLeagueGroup(
                    leagueGroups: [{{ mtid: 91, lid: 16, spid: 4 }}]
                    hoursRange: 24
                    showEmptyEvents: true
                    startDate: {1603004400000}
                    timezoneOffset: 0
                ) {{
                    events {{
                        eid
                    }}
                }}
            }}
        """
        )
        # params = {"date": 1603004400000}
        # result = SBR.client.execute(query, variable_values=params)
        result = SBR.client.execute(query)
        pass
