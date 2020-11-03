import pytest
from pytest import mark
from pytest_lazyfixture import lazy_fixture


class TestSport:
    @mark.parametrize(
        "league",
        [
            lazy_fixture("nfl"),
            lazy_fixture("ncaaf"),
            lazy_fixture("atp"),
        ],
    )
    def test_init(self, league):
        pass

    @mark.parametrize(
        "league, terms, expected",
        [
            (lazy_fixture("nfl"), [("fg", "ml"), ("fg", "ps")], [83, 401]),
            (lazy_fixture("nfl"), ["ml", "ps"], [83, 401]),
            (lazy_fixture("ncaaf"), ["money lines", "ps"], [83, 401]),
            (lazy_fixture("ncaaf"), "foo", None),
            (lazy_fixture("ncaaf"), [["fg", "foo"]], None),
            (lazy_fixture("ncaaf"), [["1H", "1st half - american total"]], [398]),
            (lazy_fixture("atp"), [["FUT", "us open winner"]], [721]),
        ],
    )
    def test_market_ids(self, league, terms, expected):
        if expected is None:
            with pytest.raises(ValueError):
                league.market_ids(terms)

        else:
            assert league.market_ids(terms) == expected

    @mark.parametrize(
        "league, terms, expected",
        [
            (lazy_fixture("nfl"), ["pit", "bal"], [1519, 1521]),
            (lazy_fixture("nfl"), ["Pittsburgh Steelers", "Ravens"], [1519, 1521]),
            (lazy_fixture("nfl"), ["foo Steelers", "Ravens"], None),
            # there are 2 teams called the mountaineers!
            # (lazy_fixture("ncaaf"), ["WVU", "Mountaineers"], [407, 407]),
            (
                lazy_fixture("ncaaf"),
                ["WVU", "West Virginia Mountaineers", "West Virginia"],
                [407, 407, 407],
            ),
            (
                lazy_fixture("ncaaf"),
                ["WVU", "Rutgers"],
                [407, 410],
            ),
        ],
    )
    def test_team_ids(self, league, terms, expected):
        if expected is None:
            with pytest.raises(ValueError):
                league.team_ids(terms)

        else:
            assert league.team_ids(terms) == expected
