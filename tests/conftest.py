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
from pysbr.sports.nfl import NFL
from pysbr.sports.ncaaf import NCAAF
from pysbr.sports.atp import ATP


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


@fixture
def nfl():
    return NFL()


@fixture
def ncaaf():
    return NCAAF()


@fixture
def atp():
    return ATP()


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
