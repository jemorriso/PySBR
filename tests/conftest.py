from unittest.mock import patch
import time
import random

from pytest import fixture
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import vcr

import pysbr.utils as utils
from pysbr.queries.query import Query
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
from pysbr.queries.eventsbyparticipantsrecent import EventsByParticipantsRecent
from pysbr.queries.eventsbyparticipants import EventsByParticipants
from pysbr.queries.eventsbydaterange import EventsByDateRange
from pysbr.queries.eventsbyeventgroup import EventsByEventGroup
from pysbr.queries.eventsbymatchup import EventsByMatchup
from pysbr.queries.openinglines import OpeningLines
from pysbr.queries.currentlines import CurrentLines
from pysbr.queries.bestlines import BestLines

# from pysbr.queries.consensus import Consensus
from pysbr.queries.consensusHistory import ConsensusHistory
from pysbr.queries.linehistory import LineHistory
from pysbr.config.sport import (
    ATP,
    NFL,
    NCAAF,
    NBA,
    NCAAB,
    MLB,
    NHL,
    EPL,
    UCL,
    LaLiga,
    Bundesliga,
    UEFANationsLeague,
    UFC,
)
from pysbr.config.sportsbook import Sportsbook


QUERY_SERVER = False
WAIT_MEAN = 69
WAIT_DEVIATION = 42
# QUERY_SERVER = True
# WAIT_MEAN = 1
# WAIT_DEVIATION = 1


class TestEventsByDate(EventsByDate):
    def __init__(self, league_ids, dt, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(league_ids, dt)

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


class TestEventsByParticipantsRecent(EventsByParticipantsRecent):
    def __init__(self, participant_ids, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(participant_ids)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self)


class TestEventsByParticipants(EventsByParticipants):
    def __init__(
        self,
        participant_ids,
        start,
        end,
        league_id,
        sport_id,
        patch_fn,
        cassette_name,
        cassette_name2,
    ):
        self.cassette_name = cassette_name
        self.cassette_name2 = cassette_name2
        self.calls = 0
        self.patch_fn = patch_fn
        super().__init__(participant_ids, start, end, league_id, sport_id)

    def _build_and_execute_query(self, *args):
        return self.patch_fn(self, *args)


class TestEventsByDateRange(EventsByDateRange):
    def __init__(self, league_ids, start, end, patch_fn, cassette_name):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(league_ids, start, end)

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
        provider_account_id,
        patch_fn,
        cassette_name,
    ):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(event_ids, market_ids, provider_account_id)

    def _build_and_execute_query(self, *args, **kwargs):
        return self.patch_fn(self)


class TestCurrentLines(CurrentLines):
    def __init__(
        self,
        event_ids,
        market_ids,
        provider_account_ids,
        patch_fn,
        cassette_name,
    ):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(
            event_ids,
            market_ids,
            provider_account_ids,
        )

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


# class TestConsensus(Consensus):
#     def __init__(
#         self,
#         event_ids,
#         market_ids,
#         patch_fn,
#         cassette_name,
#     ):
#         self.cassette_name = cassette_name
#         self.patch_fn = patch_fn
#         super().__init__(event_ids, market_ids)

#     def _build_and_execute_query(self, *args, **kwargs):
#         return self.patch_fn(self)


class TestConsensusHistory(ConsensusHistory):
    def __init__(
        self,
        event_id,
        market_ids,
        patch_fn,
        cassette_name,
    ):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(event_id, market_ids)

    def _build_and_execute_query(self, *args, **kwargs):
        return self.patch_fn(self)


class TestLineHistory(LineHistory):
    def __init__(
        self,
        event_id,
        market_id,
        sportsbook_id,
        participant_ids,
        patch_fn,
        cassette_name,
    ):
        self.cassette_name = cassette_name
        self.patch_fn = patch_fn
        super().__init__(event_id, market_id, sportsbook_id, participant_ids)

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
def mlb():
    return MLB()


@fixture
def ncaab():
    return NCAAB()


@fixture
def nba():
    return NBA()


@fixture
def nhl():
    return NHL()


@fixture
def epl():
    return EPL()


@fixture
def ucl():
    return UCL()


@fixture
def laliga():
    return LaLiga()


@fixture
def bundesliga():
    return Bundesliga()


@fixture
def uefanationsleague():
    return UEFANationsLeague()


@fixture
def ufc():
    return UFC()


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
        path = utils.build_yaml_path(cassette_name, "tests/graphql_responses")
        if not path.exists():
            utils.dump_yaml(result, path)
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
    def fn(obj, *args):
        # This try block is because of EventsByParticipants, which requires 2 separate
        # server calls. In the first one, name, args, fields, arg_str attributes are
        # not assigned yet, and not what we want. So catch attribute error and use the
        # args passed in (like how it is done in EventsByParticipants).
        # See _filter_events() method.
        try:
            q_string = obj._build_query_string(
                obj.name, obj.fields, obj._build_args(obj.arg_str, obj.args)
            )
        except AttributeError:
            q_string = obj._build_query_string(
                args[0], args[1], obj._build_args(args[2], args[3])
            )
        try:
            if obj.calls > 0:
                cassette = obj.cassette_name2
            else:
                cassette = obj.cassette_name

            obj.calls += 1
        except AttributeError:
            cassette = obj.cassette_name
        return execute_with_cassette(q_string, obj.client, cassette)

    return fn


@fixture
def build_and_execute_with_wait():
    def fn(obj, *args):
        wait_time = random.randrange(
            WAIT_MEAN - WAIT_DEVIATION, WAIT_MEAN + WAIT_DEVIATION
        )
        print(f"Waiting for {wait_time} seconds before executing query...")
        time.sleep(wait_time)
        try:
            return super(type(obj), obj)._build_and_execute_query(
                obj.name, obj.fields, obj.arg_str, obj.args
            )
        except AttributeError:
            return super(type(obj), obj)._build_and_execute_query(
                args[0], args[1], args[2], args[3]
            )

    return fn


# Factory fixture that wraps build_and_execute_with_cassette, and adds the ability
# to run test suite without VCR. So when it gets called it either does
# build_and_excute_with_cassette or it performs a wait, and then calls the original
# execute function
@fixture
def execute_factory(build_and_execute_with_cassette, build_and_execute_with_wait):
    def fn(obj, *args):

        if QUERY_SERVER:
            return build_and_execute_with_wait(obj, *args)
        else:
            return build_and_execute_with_cassette(obj, *args)

    return fn


@fixture
def query():
    return Query()


@fixture
def countries():
    return gql_client("https://countries.trevorblades.com/")


@fixture
def sbr_client():
    return gql_client("https://www.sportsbookreview.com/ms-odds-v2/odds-v2-service")


@fixture
def events_by_date(execute_factory):
    def fn(league_ids, dt, cassette_name):
        return TestEventsByDate(league_ids, dt, execute_factory, cassette_name)

    return fn


@fixture
def league_hierarchy(execute_factory):
    def fn(league_id, cassette_name):
        return TestLeagueHierarchy(league_id, execute_factory, cassette_name)

    return fn


@fixture
def team(execute_factory):
    def fn(team_id, cassette_name):
        return TestTeam(team_id, execute_factory, cassette_name)

    return fn


@fixture
def sportsbooks(execute_factory):
    def fn(sportsbook_ids, cassette_name):
        return TestSportsbooks(sportsbook_ids, execute_factory, cassette_name)

    return fn


@fixture
def event_groups_by_league(execute_factory):
    def fn(league_id, cassette_name):
        return TestEventGroupsByLeague(
            league_id,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def markets_by_market_ids(execute_factory):
    def fn(market_ids, sport_id, cassette_name):
        return TestMarketsByMarketIds(
            market_ids,
            sport_id,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def league_markets(execute_factory):
    def fn(league_id, cassette_name):
        return TestLeagueMarkets(
            league_id,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def leagues_by_league_ids(execute_factory):
    def fn(league_ids, cassette_name):
        return TestLeaguesByLeagueIds(
            league_ids,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def search_events(execute_factory):
    def fn(search_term, cassette_name):
        return TestSearchEvents(
            search_term,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def search_sports(execute_factory):
    def fn(search_term, cassette_name):
        return TestSearchSports(
            search_term,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def search_leagues(execute_factory):
    def fn(search_term, cassette_name):
        return TestSearchLeagues(
            search_term,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def event_markets(execute_factory):
    def fn(event_id, cassette_name):
        return TestEventMarkets(
            event_id,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def events_by_event_ids(execute_factory):
    def fn(event_ids, cassette_name):
        return TestEventsByEventIds(
            event_ids,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def events_by_participants_recent(execute_factory):
    def fn(participant_ids, cassette_name):
        return TestEventsByParticipantsRecent(
            participant_ids,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def events_by_participants(execute_factory):
    def fn(
        participant_ids, start, end, league_id, sport_id, cassette_name, cassette_name2
    ):
        return TestEventsByParticipants(
            participant_ids,
            start,
            end,
            league_id,
            sport_id,
            execute_factory,
            cassette_name,
            cassette_name2,
        )

    return fn


@fixture
def events_by_date_range(execute_factory):
    def fn(league_ids, start, end, cassette_name):
        return TestEventsByDateRange(
            league_ids,
            start,
            end,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def events_by_event_group(execute_factory):
    def fn(league_id, event_group_id, season_id, market_id, cassette_name):
        return TestEventsByEventGroup(
            league_id,
            event_group_id,
            season_id,
            market_id,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def events_by_matchup(execute_factory):
    def fn(participant_id1, participant_id2, count, cassette_name):
        return TestEventsByMatchup(
            participant_id1,
            participant_id2,
            count,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def opening_lines(execute_factory):
    def fn(event_ids, market_ids, provider_account_id, cassette_name):
        return TestOpeningLines(
            event_ids,
            market_ids,
            provider_account_id,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def current_lines(execute_factory):
    def fn(event_ids, market_ids, provider_account_ids, cassette_name):
        return TestCurrentLines(
            event_ids,
            market_ids,
            provider_account_ids,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def best_lines(execute_factory):
    def fn(event_ids, market_ids, cassette_name):
        return TestBestLines(
            event_ids,
            market_ids,
            execute_factory,
            cassette_name,
        )

    return fn


# @fixture
# def consensus(build_and_execute_with_cassette):
#     def fn(event_ids, market_ids, cassette_name):
#         return TestConsensus(
#             event_ids,
#             market_ids,
#             build_and_execute_with_cassette,
#             cassette_name,
#         )

#     return fn


@fixture
def consensus_history(execute_factory):
    def fn(event_id, market_ids, cassette_name):
        return TestConsensusHistory(
            event_id,
            market_ids,
            execute_factory,
            cassette_name,
        )

    return fn


@fixture
def line_history(execute_factory):
    def fn(event_id, market_id, sportsbook_id, participant_ids, cassette_name):
        return TestLineHistory(
            event_id,
            market_id,
            sportsbook_id,
            participant_ids,
            execute_factory,
            cassette_name,
        )

    return fn
