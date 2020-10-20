import json

from utils import Utils


def test_init(sbr):
    pass


def test_get_league_markets(sbr):
    assert len(sbr.get_league_markets(16)) > 0


def test_parse_response(sbr):
    with open("json/nfl_league_market_ids.json") as f:
        d = json.load(f)
    assert len(sbr._parse_response(d)) > 0


def test_get_market_types_by_id(sbr, nfl):
    d = Utils.json_to_dict("json/nfl_league_market_ids.json")
    ids = sbr._parse_response(d)["mtid"]
    assert len(sbr.get_market_types_by_id(ids, nfl.sport_id)) > 0


def test_get_events_by_date(sbr):
    sbr.get_events_by_date(None, None, None)
