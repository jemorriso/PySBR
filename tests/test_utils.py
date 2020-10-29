from datetime import datetime

from pytz import timezone

from pytest import mark


class TestUtils:
    @mark.parametrize(
        ("dt_str", "tz", "expected"),
        [
            ("2020-10-20, 9:00", "Canada/Pacific", 1603209600),
            ("2020-10-20, 9:00", "Canada/Eastern", 1603198800),
            ("2020-10-20, 9:00", None, 1603209600),
            ("2020-10-21, 21:15", "Canada/Pacific", 1603340100),
        ],
    )
    def test_datetime_to_timestamp(self, utils, dt_str, tz, expected):
        dt = datetime.strptime(dt_str, "%Y-%m-%d, %H:%M")
        timestamp = utils.datetime_to_timestamp(dt, tz)
        assert int(timestamp / 1000) == expected

    @mark.parametrize(
        ("expected_str", "tz", "ts"),
        [
            ("2020-10-20, 9:00", "Canada/Pacific", 1603209600),
            ("2020-10-20, 9:00", "Canada/Eastern", 1603198800),
            ("2020-10-20, 9:00", None, 1603209600),
            ("2020-10-21, 21:15", "Canada/Pacific", 1603340100),
        ],
    )
    def test_timestamp_to_datetime(self, utils, ts, tz, expected_str):
        e_naive = datetime.strptime(expected_str, "%Y-%m-%d, %H:%M")
        expected = (
            timezone(tz).localize(e_naive) if tz is not None else e_naive.astimezone()
        )
        dt = utils.timestamp_to_datetime(ts * 1000)
        assert dt == expected

    @mark.parametrize(("fname", "expected"), [("arguments", True), ("foo", False)])
    def test_load_yaml(self, utils, fname, expected):
        found = False
        path = utils.build_yaml_path(fname)
        try:
            utils.load_yaml(path)
            found = True
        except FileNotFoundError:
            pass
        assert found == expected
