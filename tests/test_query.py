import requests
from datetime import datetime

from pytest import mark
from pytest_lazyfixture import lazy_fixture
from gql import gql


class TestQuery:
    def test_cassete(self, use_cassette):
        with use_cassette("test_cassette"):
            r = requests.get("https://api.github.com/users/JeMorriso")
            assert (
                r.headers["X-Github-Request-Id"] == "D3E6:3C26:1160E7:2D5DC3:5F98DDF3"
            )

    def test_cassette_gql(self, utils, use_cassette, countries):
        with use_cassette("test_cassette_gql"):
            query = utils.str_format(
                """
                    query {
                        country(code: "CA") {
                                name
                        }
                    }
                    """
            )
            result = countries.execute(gql(query))
            assert result["country"]["name"] == "Canada"

    def test_build_query(self, utils, query):
        events = utils.str_format(
            """
            {
                events {
                    des
                    cit
                    cou
                    es
                    dt
                    eid
                    st
                    participants {
                        partid
                        ih
                        source {
                            ... on Team {
                                nam
                                nn
                                sn
                                abbr
                            }
                        }
                    }
                }
            }
        """
        )
        args = utils.str_format(
            """
            "lid": $ lids,
            "startDate: $dt,
            "hoursRange": 24
            """
        )
        q_string = query._build_query_string("eventsByDateNew", events, args)
        assert q_string == utils.str_format(
            """
            query {
                eventsByDateNew(
                    "lid": $ lids,
                    "startDate: $dt,
                    "hoursRange": 24
                ) {
                    events {
                        des
                        cit
                        cou
                        es
                        dt
                        eid
                        st
                        participants {
                            partid
                            ih
                            source {
                                ... on Team {
                                    nam
                                    nn
                                    sn
                                    abbr
                                }
                            }
                        }
                    }
                }
            }
            """
        )

    @mark.parametrize("dt_str", ["2020-10-29"])
    def test_execute_query(self, utils, query, patched_execute, dt_str):
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        q_fields = utils.str_format(
            """
            {
                events {
                    eid
                }
            }
        """
        )
        q_arg_str = utils.str_format(
            """
            lid: $lids,
            startDate: $timestamp,
            hoursRange: 24
            """
        )
        q_arg_str = query._build_args(
            q_arg_str,
            {
                "lids": [16],
                "timestamp": utils.datetime_to_timestamp_aware(dt),
            },
        )
        result = patched_execute(
            query._build_query_string("eventsByDateNew", q_fields, q_arg_str),
            "test_execute_query",
            query,
        )
        assert result["eventsByDateNew"]["events"][0]["eid"] == 4143517

    @mark.parametrize(
        ("fn", "k", "expected"),
        [("args", "date", True), ("fields", "event", True), ("fields", "foo", False)],
    )
    def test_get_yaml(self, query, fn, k, expected):
        is_key = True
        try:
            if fn == "args":
                query._get_args(k)
            else:
                query._get_fields(k)
        except KeyError:
            is_key = False
        assert is_key == expected

    @mark.parametrize(
        ("league_id", "dt_str", "cassette_name", "expected"),
        [(16, "2020-10-29", "test_events_by_date1", 1)],
    )
    def test_events_by_date(
        self, events_by_date, league_id, dt_str, cassette_name, expected
    ):
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        e = events_by_date(league_id, dt, cassette_name)

        assert len(e._raw) == expected

    @mark.parametrize(
        "league, cassette_name, expected",
        [
            # expected len is double teams because playoffs, then +1 for some
            # mystery reason
            (lazy_fixture("nfl"), "test_league_hierarchy_nfl1", 65),
            # this one is weird too, length is 1024, where 507 seasonIds == 5627, and
            # 517 seasonIds == 8583, but there are only 130 teams
            (lazy_fixture("ncaaf"), "test_league_hierarchy_ncaaf1", 1024),
            (lazy_fixture("atp"), "test_league_hierarchy_atp1", 0),
        ],
    )
    def test_league_hierarchy(self, league_hierarchy, league, cassette_name, expected):
        id = league.league_id
        lh = league_hierarchy(id, cassette_name)

        assert len(lh._raw["leagueHierarchy"]) == expected

    @mark.parametrize(
        "league, teams, cassette_name, expected",
        [
            (lazy_fixture("nfl"), ["pit"], "test_team_nfl1", "Steelers"),
            (lazy_fixture("ncaaf"), ["fre"], "test_team_ncaaf1", "Bulldogs"),
        ],
    )
    def test_team(self, team, league, teams, cassette_name, expected):
        id = league.team_ids(teams)[0]
        t = team(id, cassette_name)

        assert t._raw["team"]["nn"] == expected

    @mark.parametrize(
        "sportsbook_names, cassette_name, expected",
        [
            (
                ["pinnacle", "bet365"],
                "test_sportbook1",
                ["Pinnacle", "Bet365"],
            ),
        ],
    )
    def test_sportsbooks(
        self, sportsbooks, sportsbook, sportsbook_names, cassette_name, expected
    ):
        ids = sportsbook.sportsbook_ids(sportsbook_names)
        s = sportsbooks(ids, cassette_name)
        for i, x in enumerate(s._raw["sportsbooks"]):
            assert x["nam"] in expected
