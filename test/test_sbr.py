import json
from datetime import datetime, timedelta

from utils import Utils


def test_init(sbr):
    pass


def test_get_league_markets(sbr):
    assert len(sbr.get_league_markets(16)) > 0


def test_parse_response(sbr):
    with open("json_test/nfl_league_market_ids.json") as f:
        d = json.load(f)
    assert len(sbr._parse_response(d)) > 0


def test_build_query_string(sbr):
    assert sbr._build_query_string(
        "eventsByDateNew",
        sbr._detailed_event_fields(),
        q_args=Utils.str_format(
            """
            lid: $lids,
            startDate: 1602979200000,
            hoursRange: 24
        """
        ),
    )


# def test_query_execute(sbr):
#     q_name = "eventsByDateNew"
#     q_args = {"lid": [16], "startDate": 1602979200000, "hoursRange": 25}
#     q_fields = {
#         "events": [
#             "des",
#             "cit",
#             "cou",
#             "es",
#             "dt",
#             "eid",
#             "st",
#             {
#                 "participants": [
#                     "partid",
#                     "ih",
#                     {"source": {"...on Team": ["nam", "nn", "sn", "abbr"]}},
#                 ]
#             },
#         ]
#     }

#     assert sbr._query_execute(q_name, q_fields, q_args) is not None


def test_get_events_by_date_range_detailed(sbr):
    sbr.get_events_by_date_range_detailed(
        16, datetime.today(), datetime.today() + timedelta(days=3)
    )


def test_get_market_types_by_id(sbr, nfl):
    d = Utils.json_to_dict("json_test/nfl_league_market_ids.json")
    ids = sbr._parse_response(d)["mtid"]
    assert len(sbr.get_market_types_by_id(ids, nfl.sport_id)) > 0


def test_get_events_by_date(sbr):
    sbr.get_events_by_date(None, None, None)
