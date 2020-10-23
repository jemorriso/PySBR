from pytest import fixture

from sbr import SBR
from nfl import NFL
from utils import Utils


@fixture
def sbr():
    return SBR()


@fixture
def nfl():
    return NFL()


@fixture
def utils():
    return Utils()