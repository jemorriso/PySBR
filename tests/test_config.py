import pytest
from pytest import mark
from pytest_lazyfixture import lazy_fixture


class TestConfig:
    @mark.parametrize(
        "league",
        [
            lazy_fixture("nfl"),
            lazy_fixture("ncaaf"),
            lazy_fixture("epl"),
            lazy_fixture("mlb"),
            lazy_fixture("nba"),
            lazy_fixture("nhl"),
            lazy_fixture("atp"),
            lazy_fixture("ncaab"),
            lazy_fixture("ufc"),
            lazy_fixture("sportsbook"),
        ],
    )
    def test_init(self, league):
        pass

    @mark.parametrize(
        "league, terms, expected",
        [
            (lazy_fixture("nfl"), ["2q money lines", "2q tot", "2qou"], [97, 408]),
            (lazy_fixture("nfl"), ["ml", "ps"], [83, 401]),
            (
                lazy_fixture("nfl"),
                ["first half spread", "1q spread", "4th-quarter over/under"],
                [397, 403, 410],
            ),
            (lazy_fixture("ncaaf"), ["money lines", "ps"], [83, 401]),
            (lazy_fixture("ncaaf"), "foo", None),
            (lazy_fixture("ncaaf"), ["fg foo"], None),
            (lazy_fixture("ncaaf"), ["1h total"], [398]),
            (lazy_fixture("atp"), ["us open winner"], [721]),
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
            (lazy_fixture("nfl"), ["New York"], None),
            # there are 2 teams called the mountaineers!
            (lazy_fixture("ncaaf"), ["WVU", "Mountaineers"], None),
            (
                lazy_fixture("ncaaf"),
                ["WVU", "West Virginia Mountaineers", "West Virginia"],
                [407],
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

    @mark.parametrize(
        "terms, expected",
        [
            (["pinnacle", "bodog", "bet365"], [20, 9, 5]),
            (["pinnacle", "bodog sportsbook", "bet365"], [20, 9, 5]),
            ("foo", None),
        ],
    )
    def test_sportsbook_ids(self, sportsbook, terms, expected):
        if expected is None:
            with pytest.raises(ValueError):
                sportsbook.ids(terms)
        else:
            assert sportsbook.ids(terms) == expected
