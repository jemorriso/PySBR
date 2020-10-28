from pytest import fixture

from pysbr.queries.query import Query
from pysbr.utils import Utils


@fixture
def query():
    return Query()


@fixture
def utils():
    return Utils()
