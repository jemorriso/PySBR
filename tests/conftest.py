from unittest.mock import patch

from pytest import fixture
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import vcr

from pysbr.queries.query import Query
from pysbr.utils import Utils
from pysbr.queries.eventsbydate import EventsByDate
from pysbr.queries.leaguehierarchy import LeagueHierarchy
from pysbr.queries.team import Team
from pysbr.queries.sportsbooks import Sportsbooks
from pysbr.queries.eventgroupsbyleague import EventGroupsByLeague
from pysbr.queries.marketsbymarketids import MarketsByMarketIds
from pysbr.queries.leaguemarkets import LeagueMarkets
from pysbr.queries.leaguesbyleagueids import LeaguesByLeagueIds
from pysbr.queries.searchevents import SearchEvents
from pysbr.queries.searchsports import SearchSports
from pysbr.queries.searchleagues import SearchLeagues
from pysbr.queries.eventmarkets import EventMarkets
from pysbr.queries.eventsbyeventids import EventsByEventIds
from pysbr.queries.eventsbyparticipants import EventsByParticipants
from pysbr.queries.eventsbydaterange import EventsByDateRange
from pysbr.queries.eventsbyeventgroup import EventsByEventGroup
from pysbr.queries.eventsbymatchup import EventsByMatchup
from pysbr.queries.openinglines import OpeningLines
from pysbr.queries.currentlines import CurrentLines
from pysbr.queries.bestlines import BestLines
from pysbr.queries.consensus import Consensus
from pysbr.config.nfl import NFL
from pysbr.config.ncaaf import NCAAF
from pysbr.config.atp import ATP
from pysbr.config.sportsbook import Sportsbook


class TestEventsByDate(EventsByDate):
    def __init__(self, league_id, dt, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(league_id, dt)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestLeagueHierarchy(LeagueHierarchy):
    def __init__(self, league_id, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(league_id)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestTeam(Team):
    def __init__(self, team_id, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(team_id)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestSportsbooks(Sportsbooks):
    def __init__(self, sportsbook_ids, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(sportsbook_ids)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestEventGroupsByLeague(EventGroupsByLeague):
    def __init__(self, league_id, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(league_id)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestMarketsByMarketIds(MarketsByMarketIds):
    def __init__(self, market_ids, sport_id, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(market_ids, sport_id)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestLeagueMarkets(LeagueMarkets):
    def __init__(self, league_id, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(league_id)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestLeaguesByLeagueIds(LeaguesByLeagueIds):
    def __init__(self, league_ids, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(league_ids)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestSearchEvents(SearchEvents):
    def __init__(self, search_term, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(search_term)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestSearchSports(SearchSports):
    def __init__(self, search_term, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(search_term)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestSearchLeagues(SearchLeagues):
    def __init__(self, search_term, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(search_term)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestEventMarkets(EventMarkets):
    def __init__(self, event_id, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(event_id)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestEventsByEventIds(EventsByEventIds):
    def __init__(self, event_ids, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(event_ids)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestEventsByParticipants(EventsByParticipants):
    def __init__(self, participant_ids, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(participant_ids)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestEventsByDateRange(EventsByDateRange):
    def __init__(self, league_id, start, end, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(league_id, start, end)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestEventsByEventGroup(EventsByEventGroup):
    def __init__(
        self, league_id, event_group_id, season_id, market_id, patch_fn, cassette_name
    ):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(league_id, event_group_id, season_id, market_id)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestEventsByMatchup(EventsByMatchup):
    def __init__(
        self,
        participant_id1,
        participant_id2,
        count,
        patch_fn,
        cassette_name,
    ):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(participant_id1, participant_id2, count)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestOpeningLines(OpeningLines):
    def __init__(
        self,
        event_ids,
        market_ids,
        patch_fn,
        cassette_name,
    ):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(event_ids, market_ids)

    def _build_and_execute_query(self, *args, **kwargs):
        return self.patch_fn(self)


class TestCurrentLines(CurrentLines):
    def __init__(
        self,
        event_ids,
        market_ids,
        patch_fn,
        cassette_name,
    ):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(event_ids, market_ids)

    def _build_and_execute_query(self, *args, **kwargs):
        return self.patch_fn(self)


class TestBestLines(BestLines):
    def __init__(
        self,
        event_ids,
        market_ids,
        patch_fn,
        cassette_name,
    ):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(event_ids, market_ids)

    def _build_and_execute_query(self, *args, **kwargs):
        return self.patch_fn(self)


class TestConsensus(Consensus):
    def __init__(
        self,
        event_ids,
        market_ids,
        patch_fn,
        cassette_name,
    ):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(event_ids, market_ids)

    def _build_and_execute_query(self, *args, **kwargs):
        return self.patch_fn(self)


@fixture
def nfl():
    return NFL()


@fixture
def ncaaf():
    return NCAAF()


@fixture
def atp():
    return ATP()


@fixture
def sportsbook():
    return Sportsbook()


def gql_client(url):
    _transport = RequestsHTTPTransport(url=url)
    # client = Client(transport=_transport, fetch_schema_from_transport=True)
    client = Client(transport=_transport, fetch_schema_from_transport=False)
    return client


@fixture
def use_cassette():
    # factory function pattern mentioned in Pytest.fixture docs
    def fn(name):
        return vcr.use_cassette(f"tests/cassettes/{name}.yaml")

    return fn


@fixture
def execute_with_cassette(use_cassette):
    def fn(q, client, cassette_name):
        with use_cassette(cassette_name):
            result = client.execute(gql(q))
        path = Utils.build_yaml_path(cassette_name, "tests/graphql_responses")
        if not path.exists():
            Utils.dump_yaml(result, path)
        return result

    return fn


@fixture
def patched_execute(execute_with_cassette):
    def fn(q, cassette_name, obj):
        with patch.object(obj, "_execute_query", execute_with_cassette):
            result = obj._execute_query(q, obj.client, cassette_name)
            return result

    return fn


@fixture
def build_and_execute_with_cassette(execute_with_cassette):
    # this is implictly working as a patch function for Query._build_and_execute()
    def fn(obj):
        q_string = obj._build_query_string(
            obj.name, obj.fields, obj._build_args(obj.arg_str, obj.args)
        )
        return execute_with_cassette(q_string, obj.client, obj.cassette_name)

    return fn


@fixture
def query():
    return Query()


@fixture
def utils():
    return Utils()


@fixture
def countries():
    return gql_client("https://countries.trevorblades.com/")


@fixture
def sbr_client():
    return gql_client("https://www.sportsbookreview.com/ms-odds-v2/odds-v2-service")


@fixture
def events_by_date(build_and_execute_with_cassette):
    def fn(league_id, dt, cassette_name):
        return TestEventsByDate(
            league_id, dt, build_and_execute_with_cassette, cassette_name
        )

    return fn


@fixture
def league_hierarchy(build_and_execute_with_cassette):
    def fn(league_id, cassette_name):
        return TestLeagueHierarchy(
            league_id, build_and_execute_with_cassette, cassette_name
        )

    return fn


@fixture
def team(build_and_execute_with_cassette):
    def fn(team_id, cassette_name):
        return TestTeam(team_id, build_and_execute_with_cassette, cassette_name)

    return fn


@fixture
def sportsbooks(build_and_execute_with_cassette):
    def fn(sportsbook_ids, cassette_name):
        return TestSportsbooks(
            sportsbook_ids, build_and_execute_with_cassette, cassette_name
        )

    return fn


@fixture
def event_groups_by_league(build_and_execute_with_cassette):
    def fn(league_id, cassette_name):
        return TestEventGroupsByLeague(
            league_id,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def markets_by_market_ids(build_and_execute_with_cassette):
    def fn(market_ids, sport_id, cassette_name):
        return TestMarketsByMarketIds(
            market_ids,
            sport_id,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def league_markets(build_and_execute_with_cassette):
    def fn(league_id, cassette_name):
        return TestLeagueMarkets(
            league_id,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def leagues_by_league_ids(build_and_execute_with_cassette):
    def fn(league_ids, cassette_name):
        return TestLeaguesByLeagueIds(
            league_ids,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def search_events(build_and_execute_with_cassette):
    def fn(search_term, cassette_name):
        return TestSearchEvents(
            search_term,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def search_sports(build_and_execute_with_cassette):
    def fn(search_term, cassette_name):
        return TestSearchSports(
            search_term,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def search_leagues(build_and_execute_with_cassette):
    def fn(search_term, cassette_name):
        return TestSearchLeagues(
            search_term,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def event_markets(build_and_execute_with_cassette):
    def fn(event_id, cassette_name):
        return TestEventMarkets(
            event_id,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def events_by_event_ids(build_and_execute_with_cassette):
    def fn(event_ids, cassette_name):
        return TestEventsByEventIds(
            event_ids,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def events_by_participants(build_and_execute_with_cassette):
    def fn(participant_ids, cassette_name):
        return TestEventsByParticipants(
            participant_ids,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def events_by_date_range(build_and_execute_with_cassette):
    def fn(league_id, start, end, cassette_name):
        return TestEventsByDateRange(
            league_id,
            start,
            end,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def events_by_event_group(build_and_execute_with_cassette):
    def fn(league_id, event_group_id, season_id, market_id, cassette_name):
        return TestEventsByEventGroup(
            league_id,
            event_group_id,
            season_id,
            market_id,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def events_by_matchup(build_and_execute_with_cassette):
    def fn(participant_id1, participant_id2, count, cassette_name):
        return TestEventsByMatchup(
            participant_id1,
            participant_id2,
            count,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def opening_lines(build_and_execute_with_cassette):
    def fn(event_ids, market_ids, cassette_name):
        return TestOpeningLines(
            event_ids,
            market_ids,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def current_lines(build_and_execute_with_cassette):
    def fn(event_ids, market_ids, cassette_name):
        return TestCurrentLines(
            event_ids,
            market_ids,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def best_lines(build_and_execute_with_cassette):
    def fn(event_ids, market_ids, cassette_name):
        return TestBestLines(
            event_ids,
            market_ids,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn


@fixture
def consensus(build_and_execute_with_cassette):
    def fn(event_ids, market_ids, cassette_name):
        return TestConsensus(
            event_ids,
            market_ids,
            build_and_execute_with_cassette,
            cassette_name,
        )

    return fn