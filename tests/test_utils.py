from datetime import datetime

from pytz import timezone
from pytest import mark
from tzlocal import get_localzone

import pysbr.utils as utils


class TestUtils:
    @mark.parametrize(
        ("dt_str", "tz", "expected"),
        [
            ("2020-10-20, 9:00", "Canada/Pacific", 1603209600),
            ("2020-10-20, 9:00", "Canada/Eastern", 1603198800),
            ("2020-10-21, 21:15", "Canada/Pacific", 1603340100),
        ],
    )
    def test_datetime_to_timestamp_aware(self, dt_str, tz, expected):
        dt = datetime.strptime(dt_str, "%Y-%m-%d, %H:%M")
        timestamp = utils.datetime_to_timestamp_aware(dt, tz)
        assert int(timestamp / 1000) == expected

    @mark.parametrize(
        ("expected_str", "tz", "ts"),
        [
            ("2020-10-20, 9:00", "Canada/Pacific", 1603209600),
            ("2020-10-20, 9:00", "Canada/Eastern", 1603198800),
            ("2020-10-21, 21:15", "Canada/Pacific", 1603340100),
        ],
    )
    def test_timestamp_to_datetime_aware(self, ts, tz, expected_str):
        e_naive = datetime.strptime(expected_str, "%Y-%m-%d, %H:%M")
        if tz is None:
            tz = str(get_localzone())
        expected = timezone(tz).localize(e_naive)
        dt = utils.timestamp_to_datetime_aware(ts * 1000)
        assert dt == expected

    @mark.parametrize(
        ("dt_str", "tz", "expected"),
        [
            ("2020-10-20, 9:00", "Canada/Pacific", 1603209600),
            ("2020-10-20, 9:00", "Canada/Eastern", 1603198800),
            ("2020-10-21, 21:15", "Canada/Pacific", 1603340100),
        ],
    )
    def test_datetime_to_timestamp(self, dt_str, tz, expected):
        dt = timezone(tz).localize(datetime.strptime(dt_str, "%Y-%m-%d, %H:%M"))
        timestamp = utils.datetime_to_timestamp(dt)
        assert int(timestamp / 1000) == expected

    @mark.parametrize(
        ("expected_str", "tz", "ts"),
        [
            ("2020-10-20, 9:00", "Canada/Pacific", 1603209600),
            ("2020-10-21, 21:15", "Canada/Pacific", 1603340100),
        ],
    )
    def test_timestamp_to_datetime(self, ts, tz, expected_str):
        expected = timezone(tz).localize(
            datetime.strptime(expected_str, "%Y-%m-%d, %H:%M")
        )
        dt = utils.timestamp_to_datetime(ts * 1000).astimezone(timezone(tz))
        assert dt == expected

    @mark.parametrize(("fname", "expected"), [("arguments", True), ("foo", False)])
    def test_load_yaml(self, fname, expected):
        found = False
        path = utils.build_yaml_path(fname)
        try:
            utils.load_yaml(path)
            found = True
        except FileNotFoundError:
            pass
        assert found == expected
