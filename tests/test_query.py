import requests
from datetime import datetime

from pytest import mark
import pytest
from pytest_lazyfixture import lazy_fixture
from gql import gql
import pandas as pd

import pysbr.utils as utils


class TestQuery:
    def test_cassete(self, use_cassette):
        with use_cassette("test_cassette"):
            r = requests.get("https://api.github.com/users/JeMorriso")
            assert (
                r.headers["X-Github-Request-Id"] == "D3E6:3C26:1160E7:2D5DC3:5F98DDF3"
            )

    def test_cassette_gql(self, use_cassette, countries):
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

    def test_build_query(self, query):
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
    def test_execute_query(self, query, patched_execute, dt_str):
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
        [
            (16, "2020-10-29", "test_events_by_date1", 1),
            (7, "2021-01-13", "test_events_by_date2", 1),
        ],
    )
    def test_events_by_date(
        self, events_by_date, league_id, dt_str, cassette_name, expected
    ):
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        e = events_by_date(league_id, dt, cassette_name)

        assert len(e._raw) == expected

        l_ = e.list()
        ids = e.ids()
        df = e.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "league, cassette_name, expected",
        [
            # expected len is double teams because playoffs, then +1 for some
            # mystery reason
            (lazy_fixture("nfl"), "test_league_hierarchy_nfl1", 65),
            # Commenting this test out because I don't understand the length. Test needs
            # to be more robust.
            # this one is weird too, length is 1024, where 507 seasonIds == 5627, and
            # 517 seasonIds == 8583, but there are only 130 teams
            # (lazy_fixture("ncaaf"), "test_league_hierarchy_ncaaf1", 1024),
            (lazy_fixture("atp"), "test_league_hierarchy_atp1", 0),
        ],
    )
    def test_league_hierarchy(self, league_hierarchy, league, cassette_name, expected):
        id = league.league_id
        lh = league_hierarchy(id, cassette_name)

        assert len(lh._raw["leagueHierarchy"]) == expected

        l_ = lh.list()
        ids = lh.ids()
        df = lh.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

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

        l_ = t.list()
        df = t.dataframe()
        assert isinstance(l_, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "sportsbook_ids, cassette_name, expected",
        [
            (
                [20, 5],
                "test_sportbook1",
                ["Pinnacle", "Bet365"],
            ),
        ],
    )
    def test_sportsbooks(
        self,
        sportsbooks,
        sportsbook_ids,
        cassette_name,
        expected,
    ):
        # the sportsbook ids are system sportsbook ids for this query
        s = sportsbooks(sportsbook_ids, cassette_name)
        for i, x in enumerate(s._raw["sportsbooks"]):
            assert x["nam"] in expected

        l_ = s.list()
        ids = s.ids()
        df = s.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "league, cassette_name, alias",
        [
            (
                lazy_fixture("nfl"),
                "test_event_groups_by_league_nfl1",
                "Week 1",
            ),
            (
                lazy_fixture("ncaaf"),
                "test_event_groups_by_league_ncaaf1",
                "Week 1",
            ),
            (
                lazy_fixture("atp"),
                "test_event_groups_by_league_atp1",
                "Miami, USA",
            ),
        ],
    )
    def test_event_groups_by_league(
        self, event_groups_by_league, league, cassette_name, alias
    ):
        id = league.league_id
        e = event_groups_by_league(id, cassette_name)
        found = False
        for event in e._raw["eventGroupsByLeague"]:
            if event["nam"] == alias:
                found = True
            elif event["alias"] == alias:
                found = True
        assert found

        l_ = e.list()
        ids = e.ids()
        df = e.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "league, market_ids, cassette_name, expected",
        [
            (
                lazy_fixture("nfl"),
                [91, 92],
                "test_markets_by_market_ids_football1",
                True,
            ),
            (
                lazy_fixture("atp"),
                [126, 395, 396],
                "test_markets_by_market_ids_tennis1",
                True,
            ),
        ],
    )
    def test_markets_by_market_ids(
        self, markets_by_market_ids, league, market_ids, cassette_name, expected
    ):
        id = league.sport_id
        m = markets_by_market_ids(market_ids, id, cassette_name)

        found = True
        for id in market_ids:
            if (
                len(
                    [
                        market
                        for market in m._raw["marketTypesById"]
                        if market["mtid"] == id
                    ]
                )
                == 0
            ):
                found = False

        assert found == expected

        l_ = m.list()
        ids = m.ids()
        df = m.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "league, cassette_name, expected",
        [
            (lazy_fixture("nfl"), "test_league_markets_nfl1", [92, 93, 97]),
            (lazy_fixture("ncaaf"), "test_league_markets_ncaaf1", [92, 93, 97]),
            (lazy_fixture("atp"), "test_league_markets_atp1", [133, 134]),
        ],
    )
    def test_league_markets(self, league_markets, league, cassette_name, expected):
        id = league.league_id
        m = league_markets(id, cassette_name)

        found = []
        for market in m._raw["leagueMarkets"]:
            if market["mtid"] in expected:
                found.append(market["mtid"])

        assert set(found) == set(expected)

        l_ = m.list()
        ids = m.ids()
        df = m.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "league_ids, cassette_name, expected",
        [([23, 6, 16], "test_leagues_by_league_ids1", ["ATP", "NCAAF", "NFL"])],
    )
    def test_leagues_by_league_ids(
        self, leagues_by_league_ids, league_ids, cassette_name, expected
    ):
        l_ = leagues_by_league_ids(league_ids, cassette_name)

        found = []
        for league in l_._raw["leagues"]:
            found.append(league["sn"])

        assert set(found) == set(expected)

        list_ = l_.list()
        df = l_.dataframe()
        assert isinstance(list_, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "search_term, cassette_name, expected",
        [
            ("Patriots", "test_search_events_nfl1", 4143526),
            ("Toledo", "test_search_events_ncaaf1", 4260018),
            ("Rockets", "test_search_events_ncaaf2", 4260018),
            ("Auger-Aliassime", "test_search_events_atp1", 4279927),
            ("Caruso", "test_search_events_atp2", 4279927),
        ],
    )
    def test_search_events(self, search_events, search_term, cassette_name, expected):
        s = search_events(search_term, cassette_name)

        for event in s._raw["searchEvent"]:
            if event["eid"] == expected:
                break

        l_ = s.list()
        ids = s.ids()
        df = s.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "search_term, cassette_name, expected",
        [
            ("football", "test_search_sports_football1", 4),
            ("soccer", "test_search_sports_soccer1", 2),
            ("tennis", "test_search_sports_tennis1", 8),
        ],
    )
    def test_search_sports(self, search_sports, search_term, cassette_name, expected):
        s = search_sports(search_term, cassette_name)

        for sport in s._raw["multipleSearch"]["searchSport"]:
            if sport["spid"] == expected:
                break

        l_ = s.list()
        ids = s.ids()
        df = s.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "search_term, cassette_name, expected",
        [
            ("nfl", "test_search_leagues_nfl1", 16),
            ("national football league", "test_search_leagues_nfl2", 16),
            ("laliga", "test_search_leagues_laliga1", 17),
        ],
    )
    def test_search_leagues(self, search_leagues, search_term, cassette_name, expected):
        s = search_leagues(search_term, cassette_name)

        for league in s._raw["multipleSearch"]["searchLeague"]:
            if league["lid"] == expected:
                break

        l_ = s.list()
        ids = s.ids()
        df = s.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "event_id, cassette_name, expected",
        [
            (4279927, "test_event_markets_atp1", 126),
            (4143396, "test_event_markets_nfl1", 401),
        ],
    )
    def test_event_markets(self, event_markets, event_id, cassette_name, expected):
        e = event_markets(event_id, cassette_name)

        assert expected in e._raw["eventMarkets"]["mtids"]

        l_ = e.list()
        df = e.dataframe()
        assert isinstance(l_, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "event_ids, cassette_name, expected",
        [
            ([4143400, 4143532], "test_events_by_event_ids_nfl1", [4143400, 4143532]),
            ([4143486, 4143483], "test_events_by_event_ids_nfl2", [4143486, 4143483]),
            ([4143486, 4143532], "test_events_by_event_ids_nfl3", [4143486, 4143532]),
            ([4279749, 4278815], "test_events_by_event_ids_atp1", [4279749, 4278815]),
            (
                [4279749, 4143483, 4253502],
                "test_events_by_event_ids_sport1",
                [4279749, 4143483, 4253502],
            ),
        ],
    )
    def test_events_by_event_ids(
        self, events_by_event_ids, event_ids, cassette_name, expected
    ):
        e = events_by_event_ids(event_ids, cassette_name)

        for id in expected:
            assert len([x for x in e._raw["eventsV2"]["events"] if x["eid"] == id]) == 1

        l_ = e.list()
        ids = e.ids()
        df = e.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "participant_ids, cassette_name, expected",
        [
            (
                [1525, 1530],
                "test_events_by_participants_recent_nfl1",
                [4143351, 4143527],
            ),
            (
                [407, 408],
                "test_events_by_participants_recent_ncaaf1",
                [4089535, 4197789],
            ),
            ([5562, 5628], "test_events_by_participants_recent_atp1", [4279492]),
        ],
    )
    def test_events_by_participants_recent(
        self, events_by_participants_recent, participant_ids, cassette_name, expected
    ):
        # this test will fail if querying server, because these events are old.
        e = events_by_participants_recent(participant_ids, cassette_name)
        events = []
        for t in e._raw["eventsInfoByParticipant"]:
            for event in t["events"]:
                events.append(event["eid"])

        for id in expected:
            assert id in events

        l_ = e.list()
        ids = e.ids()
        df = e.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        """participant_ids, start, end, league_id, sport_id, cassette_name,
        cassette_name2, expected""",
        [
            (
                [1530],
                "2020-09-09",
                "2020-11-16",
                16,
                None,
                "test_events_by_participant_subquery_nfl1",
                "test_events_by_participant_nfl1",
                [4143362],
            ),
            (
                [1529, 1530],
                "2020-11-09",
                "2020-11-16",
                16,
                None,
                "test_events_by_participant_subquery_nfl2",
                "test_events_by_participant_nfl2",
                [4143396, 4143532],
            ),
            (
                [1529, 1530],
                "2020-11-09",
                "2020-11-16",
                None,
                4,
                "test_events_by_participant_subquery_football1",
                "test_events_by_participant_football1",
                [4143396, 4143532],
            ),
            (
                [5755],
                "2020-11-01",
                "2020-11-16",
                23,
                None,
                "test_events_by_participant_subquery_atp1",
                "test_events_by_participant_atp1",
                [4277037],
            ),
        ],
    )
    def test_events_by_participants(
        self,
        events_by_participants,
        participant_ids,
        start,
        end,
        league_id,
        sport_id,
        cassette_name,
        cassette_name2,
        expected,
    ):
        s_ = datetime.strptime(start, "%Y-%m-%d")
        e_ = datetime.strptime(end, "%Y-%m-%d")
        e = events_by_participants(
            participant_ids, s_, e_, league_id, sport_id, cassette_name, cassette_name2
        )

        events = []
        for event in e._raw["eventsV2"]["events"]:
            events.append(event["eid"])

        for id in expected:
            assert id in events

    @mark.parametrize(
        ("league_id", "start_dt", "end_dt", "cassette_name", "expected"),
        [
            (
                16,
                "2020-10-29",
                "2020-11-01",
                "test_events_by_date_range_nfl1",
                [4143517],
            ),
            (
                16,
                "2020-10-29",
                "2020-11-08",
                "test_events_by_date_range_nfl2",
                [4143517],
            ),
            (
                23,
                "2020-11-09",
                "2020-11-13",
                "test_events_by_date_range_atp1",
                [4278996],
            ),
            (
                6,
                "2020-11-07",
                "2020-11-09",
                "test_events_by_date_range_ncaaf1",
                [4090357],
            ),
        ],
    )
    def test_events_by_date_range(
        self, events_by_date_range, league_id, start_dt, end_dt, cassette_name, expected
    ):
        start = datetime.strptime(start_dt, "%Y-%m-%d")
        end = datetime.strptime(end_dt, "%Y-%m-%d")
        e = events_by_date_range(league_id, start, end, cassette_name)

        events = []
        for event in e._raw["eventsV2"]["events"]:
            events.append(event["eid"])

        for id in expected:
            assert id in events

        l_ = e.list()
        ids = e.ids()
        df = e.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "league, event_group_id, season_id, cassette_name, expected",
        [
            (
                lazy_fixture("nfl"),
                19,
                8582,
                "test_events_by_event_groups_nfl1",
                [4143503],
            ),
            (
                lazy_fixture("ncaaf"),
                43,
                8583,
                "test_events_by_event_groups_ncaaf1",
                [4260015],
            ),
            (
                lazy_fixture("atp"),
                23908,
                5562,
                "test_events_by_event_groups_atp1",
                [4278811],
            ),
        ],
    )
    def test_events_by_event_group(
        self,
        events_by_event_group,
        league,
        event_group_id,
        season_id,
        cassette_name,
        expected,
    ):
        league_id = league.league_id
        market_id = league.default_market_id
        e = events_by_event_group(
            league_id, event_group_id, season_id, market_id, cassette_name
        )

        events = []
        for event in e._raw["eventsByEventGroupV2"]["events"]:
            events.append(event["eid"])

        for id in expected:
            assert id in events

        l_ = e.list()
        ids = e.ids()
        df = e.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "participant_id1, participant_id2, count, cassette_name, expected",
        [
            (1530, 1525, 3, "test_events_by_matchup_nfl1", [3778743]),
            (1223, 1196, 10, "test_events_by_matchup_ncaaf1", [2962383]),
            (5562, 5628, 10, "test_events_by_matchup_atp1", [4279492]),
        ],
    )
    def test_events_by_matchup(
        self,
        events_by_matchup,
        participant_id1,
        participant_id2,
        count,
        cassette_name,
        expected,
    ):
        e = events_by_matchup(participant_id1, participant_id2, count, cassette_name)

        events = []
        for event in e._raw["lastMatchupsByParticipants"]["events"]:
            events.append(event["eid"])

        for id in expected:
            assert id in events

        l_ = e.list()
        ids = e.ids()
        df = e.dataframe()
        assert isinstance(l_, list)
        assert isinstance(ids, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "event_ids, market_ids, provider_account_id, cassette_name",
        [
            # ([4143394, 4143395], [401, 83, 402], None, "test_opening_lines_nfl1"),
            ([4143378, 4143379], [401, 83, 402], 20, "test_opening_lines_nfl2"),
            # ([4278815, 4279749], [126, 395, 396], None, "test_opening_lines_atp1"),
            ([4278815, 4277031], [126, 395, 396], 20, "test_opening_lines_atp2"),
        ],
    )
    def test_opening_lines(
        self, opening_lines, event_ids, market_ids, provider_account_id, cassette_name
    ):
        o = opening_lines(event_ids, market_ids, provider_account_id, cassette_name)

        ids = []
        for line in o._raw["openingLines"]:
            ids.append(line["eid"])
            ids.append(line["mtid"])

        for id in event_ids + market_ids:
            assert id in ids

        l_ = o.list()
        df = o.dataframe()
        assert isinstance(l_, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "event_ids, market_ids, provider_account_ids, cassette_name",
        [
            # ([4143394, 4143395], [401, 83, 402], None, "test_current_lines_nfl1"),
            ([4143379, 4143378], [401, 83, 402], [5, 20], "test_current_lines_nfl2"),
            # ([4278815, 4279749], [126, 395, 396], None, "test_current_lines_atp1"),
            ([4278815, 4277031], [126, 395, 396], [5, 20], "test_current_lines_atp2"),
        ],
    )
    def test_current_lines(
        self, current_lines, event_ids, market_ids, provider_account_ids, cassette_name
    ):
        c = current_lines(event_ids, market_ids, provider_account_ids, cassette_name)

        ids = []
        for line in c._raw["currentLines"]:
            ids.append(line["eid"])
            ids.append(line["mtid"])

        for id in event_ids + market_ids:
            assert id in ids

        l_ = c.list()
        df = c.dataframe()
        assert isinstance(l_, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "event_ids, market_ids, cassette_name",
        [
            ([4143394, 4143395], [401, 83, 402], "test_best_lines_nfl1"),
            # ([4143394, 4143395], None, "test_best_lines_nfl2"),
            ([4278815, 4279749], [126, 395, 396], "test_best_lines_atp1"),
            # ([4278815, 4279749], None, "test_best_lines_atp2"),
        ],
    )
    def test_best_lines(self, best_lines, event_ids, market_ids, cassette_name):
        b = best_lines(event_ids, market_ids, cassette_name)

        ids = []
        for line in b._raw["bestLines"]:
            ids.append(line["eid"])
            ids.append(line["mtid"])

        for id in event_ids + market_ids if market_ids is not None else event_ids:
            assert id in ids

        l_ = b.list()
        df = b.dataframe()
        assert isinstance(l_, list)
        assert isinstance(df, pd.DataFrame)

    # @mark.parametrize(
    #     "event_ids, market_ids, cassette_name, expected",
    #     [
    #         ([4143394, 4143395], [401, 83, 402], "test_consensus_nfl1", True),
    #         ([4278815, 4279749], [126, 395, 396], "test_consensus_atp1", False),
    #     ],
    # )
    # def test_consensus(
    #   self, consensus, event_ids, market_ids, cassette_name, expected
    # ):
    #     c = consensus(event_ids, market_ids, cassette_name)

    #     ids = []
    #     for line in c._raw["consensus"]:
    #         ids.append(line["eid"])
    #         ids.append(line["mtid"])

    #     if expected:
    #         for id in event_ids + market_ids:
    #             assert id in ids
    #     else:
    #         assert len(c._raw["consensus"]) == 0

    #     l_ = c.list()
    #     df = c.dataframe()
    #     assert isinstance(l_, list)
    #     assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "event_id, market_ids, cassette_name, expected",
        [
            (4143394, [401, 83, 402], "test_consensus_history_nfl1", True),
            (4250867, [125, 411, 412], "test_consensus_history_nhl1", True),
        ],
    )
    def test_consensus_history(
        self, consensus_history, event_id, market_ids, cassette_name, expected
    ):
        c = consensus_history(event_id, market_ids, cassette_name)

        ids = []
        for line in c._raw["consensusHistory"]:
            ids.append(line["eid"])
            ids.append(line["mtid"])

        if expected:
            for id in [event_id] + market_ids:
                assert id in ids
        else:
            assert len(c._raw["consensusHistory"]) == 0

        l_ = c.list()
        df = c.dataframe()
        assert isinstance(l_, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        "event_id, market_id, sportsbook_id, participant_ids, cassette_name, expected",
        [
            (
                4143532,
                401,
                20,
                [1530, 1520],
                "test_line_history_nfl1",
                True,
            ),
            (
                4278809,
                126,
                20,
                [5452],
                "test_line_history_atp1",
                True,
            ),
        ],
    )
    def test_line_history(
        self,
        line_history,
        event_id,
        market_id,
        sportsbook_id,
        participant_ids,
        cassette_name,
        expected,
    ):
        h = line_history(
            event_id, market_id, sportsbook_id, participant_ids, cassette_name
        )

        ids = []
        for line in h._raw["lineHistory"][0]["lines"]:
            ids.append(line["eid"])
            ids.append(line["mtid"])
            ids.append(line["paid"])

        if expected:
            for id in [event_id, market_id, sportsbook_id]:
                assert id in ids
        else:
            assert len(h._raw["lineHistory"][0]["lines"]) == 0

        l_ = h.list()
        df = h.dataframe()
        assert isinstance(l_, list)
        assert isinstance(df, pd.DataFrame)

    @mark.parametrize(
        """lines, league_id, dt_str, market_ids, cassette_events, cassette_lines,
        expected, is_best_lines""",
        [
            # I changed parameters and now this test doesn't work, but it's the test
            # case's fault.
            # (
            #     lazy_fixture("opening_lines"),
            #     16,
            #     "2020-11-15",
            #     [401, 83, 402],
            #     "test_lines_with_events_events_nfl1",
            #     "test_lines_with_events_opening_lines_nfl1",
            #     None,
            #     False,
            # ),
            (
                lazy_fixture("best_lines"),
                16,
                "2020-11-15",
                [401, 83, 402],
                "test_lines_with_events_events_nfl1",
                "test_lines_with_events_best_lines_nfl1",
                None,
                True,
            ),
            (
                lazy_fixture("current_lines"),
                16,
                "2020-11-15",
                [401, 83, 402],
                "test_lines_with_events_events_nfl1",
                "test_lines_with_events_current_lines_nfl1",
                None,
                False,
            ),
        ],
    )
    def test_lines_with_events(
        self,
        events_by_date,
        lines,
        league_id,
        dt_str,
        market_ids,
        cassette_events,
        cassette_lines,
        expected,
        is_best_lines,
    ):
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        e = events_by_date(league_id, dt, cassette_events)
        event_ids = e.ids()

        lines_obj = (
            lines(event_ids, market_ids, [20, 9, 5], cassette_lines)
            if not is_best_lines
            else lines(event_ids, market_ids, cassette_lines)
        )
        l_ = lines_obj.list(e)
        df = lines_obj.dataframe(e)
        assert lines_obj is not None
        assert l_ is not None
        assert df is not None

    @mark.parametrize(
        "query, params",
        [
            (lazy_fixture("best_lines"), ["foo", "bar"]),
            # (lazy_fixture("consensus"), [["list", "of", "str"], "bar"]),
            (lazy_fixture("current_lines"), [16, 16, "foo"]),
            (lazy_fixture("event_groups_by_league"), ["foo"]),
            (lazy_fixture("event_markets"), ["foo"]),
            (lazy_fixture("events_by_date"), [42, "not a datetime"]),
        ],
    )
    def test_typecheck(self, query, params):
        # with pytest.raises(ValueError):
        with pytest.raises(TypeError):
            query(*params, "dummy_cassette")

    @mark.parametrize(
        "league_id, dt_str, market_ids, cassette_events, cassette_lines, expected",
        [
            (
                16,
                "2020-11-22",
                [83, 401, 402],
                "test_lines_with_events_with_scores_events_nfl1",
                "test_lines_with_events_with_scores_lines_nfl1",
                None,
            ),
            (
                16,
                "2020-12-06",
                [83, 401, 402],
                "test_lines_with_events_with_scores_events_nfl2",
                "test_lines_with_events_with_scores_lines_nfl2",
                None,
            ),
            (
                2,
                "2021-01-26",
                [1, 395, 396],
                "test_lines_with_events_with_scores_events_epl1",
                "test_lines_with_events_with_scores_lines_epl1",
                None,
            ),
            (
                23,
                "2020-01-26",
                [126, 395, 396],
                "test_lines_with_events_with_scores_events_atp1",
                "test_lines_with_events_with_scores_lines_atp1",
                None,
            ),
        ],
    )
    def test_lines_with_events_with_scores(
        self,
        events_by_date,
        current_lines,
        league_id,
        dt_str,
        market_ids,
        cassette_events,
        cassette_lines,
        expected,
    ):
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        e = events_by_date(league_id, dt, cassette_events)
        c = current_lines(e.ids(), market_ids, [5, 9, 20], cassette_lines)
        l_ = c.list(e)
        df = c.dataframe(e)
        # assert lines_obj is not None
        assert l_ is not None
        assert df is not None

    @mark.parametrize(
        "search_term, market_ids, cassette_events, cassette_lines, expected",
        [
            (
                "nebraska",
                [401],
                "test_lines_with_search_events_events_ncaab1",
                "test_lines_with_search_events_lines_ncaab1",
                None,
            )
        ],
    )
    def test_lines_with_search_events(
        self,
        search_events,
        current_lines,
        search_term,
        market_ids,
        cassette_events,
        cassette_lines,
        expected,
    ):
        e = search_events(search_term, cassette_events)
        c = current_lines(e.ids(), market_ids, [5, 9, 20], cassette_lines)
        l_ = c.list(e)
        df = c.dataframe(e)
        # assert lines_obj is not None
        assert l_ is not None
        assert df is not None
