from unittest.mock import patch

from pytest import fixture
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import vcr

from pysbr.queries.query import Query
from pysbr.utils import Utils


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
            return client.execute(gql(q))

    return fn


@fixture
def patched_execute(execute_with_cassette, query):
    def fn(q, cassette_name):
        with patch.object(query, "_execute_query", execute_with_cassette):
            result = query._execute_query(q, query.client, cassette_name)
            return result

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
