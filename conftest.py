from pytest import fixture

from sbr import SBR
from nfl import NFL


@fixture
def sbr():
    return SBR()


@fixture
def nfl():
    return NFL()