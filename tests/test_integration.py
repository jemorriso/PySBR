from pysbr.config.sport import NFL, NCAAF, ATP
from datetime import datetime


class TestIntegration:
    def test_last_year_group_nfl(
        self,
        events_by_date,
        event_groups_by_league,
        events_by_event_group,
        current_lines,
    ):
        dt = datetime.strptime("2019-09-05", "%Y-%m-%d")
        nfl = NFL()
        league_id = nfl.league_id

        # get last year season by using events by date
        e1 = events_by_date(league_id, dt, "integration_test_last_year_group_nfl1")
        e1list = e1.list()
        season_id = e1list[0].get("season id")

        # get season's event groups
        e2 = event_groups_by_league(league_id, "integration_test_last_year_group_nfl2")
        e2list = e2.list()

        # get week 10
        week10_id = [
            x.get("event group id") for x in e2list if x.get("alias") == "Week 10"
        ].pop()

        market_id = nfl.market_ids("1hou")[0]
        e3 = events_by_event_group(
            league_id,
            week10_id,
            season_id,
            market_id,
            "integration_test_last_year_group_nfl3",
        )

        cl = current_lines(
            e3.ids(), [market_id], [20], "integration_test_last_year_group_nfl4"
        )
        df = cl.dataframe(e3)
        assert df is not None

    def test_team_lines_ncaaf(self, events_by_participants, best_lines):
        ncaaf = NCAAF()
        lid = ncaaf.league_id
        spid = ncaaf.sport_id
        bama = ncaaf.team_ids(["alabama"])

        sdt = datetime.strptime("2019-09-05", "%Y-%m-%d")
        edt = datetime.strptime("2019-10-30", "%Y-%m-%d")

        e = events_by_participants(
            bama,
            sdt,
            edt,
            lid,
            spid,
            "integration_test_team_lines_ncaaf1",
            "integration_test_team_lines_ncaaf2",
        )

        market_ids = ncaaf.market_ids(["fgps", "ml"])
        b = best_lines(e.ids(), market_ids, "integration_test_team_lines_ncaaf3")
        df = b.dataframe(e)
        assert df is not None

    def test_rivalry_nfl(self, events_by_matchup, opening_lines):
        nfl = NFL()
        ids = nfl.team_ids(["chicago", "packers"])
        market_ids = nfl.market_ids(["1qou", "4qml", "2qml", "2hps"])
        e = events_by_matchup(ids[0], ids[1], 10, "integration_test_rivalry_nfl1")
        o = opening_lines(e.ids(), market_ids, 20, "integration_test_rivalry_nfl2")

        df = o.dataframe(e)
        assert df is not None

    def test_search_atp(
        self,
        search_events,
        events_by_participants_recent,
        current_lines,
    ):
        # This test will fail if querying server if Nadal does not have any upcoming
        # events.
        e = search_events("Nadal", "integration_test_search_atp1")

        nadal = None
        for x in e.list():
            for y in x.get("participants"):
                try:
                    if y["source"]["last name"] == "Nadal":

                        nadal = y["participant id"]
                except KeyError:
                    pass

        e2 = None
        if nadal is not None:
            e2 = events_by_participants_recent([nadal], "integration_test_search_atp2")

        df = e2.dataframe()

        atp = ATP()
        market_ids = atp.market_ids(["ou", "ps", "ml"])

        c = current_lines(
            e2.ids(), market_ids, [5, 20, 9], "integration_test_search_atp3"
        )
        df = c.dataframe(e2)

        assert df is not None

    def test_epl(
        self,
        search_leagues,
        league_hierarchy,
        events_by_date,
        league_markets,
        current_lines,
    ):
        # 'epl' fails
        s = search_leagues("premier league", "integration_test_epl1")

        assert s is not None

        league_id = 2
        # sport_id = 2

        # league hierarchy is empty for EPL!
        lh = league_hierarchy(league_id, "integration_test_epl2")
        df = lh.dataframe()

        dt = datetime.strptime("2020-11-21", "%Y-%m-%d")
        e = events_by_date(league_id, dt, "integration_test_epl3")

        # lm = league_markets(2, "integration_test_epl4")

        # I got these from inspecting in Chrome, league_markets returns too many
        market_ids = [1, 395, 396]
        c = current_lines(e.ids(), market_ids, 20, "integration_test_epl5")

        df = c.dataframe(e)
        assert df is not None


#       try and get odds for the election
#
#
#       try horse racing

#       get odds for jake paul vs nate robinson - do line history
#
