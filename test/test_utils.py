from datetime import datetime

from pytest import mark


@mark.parametrize(
    ("dt_str", "tz", "expected"),
    [
        ("2020-10-20, 9:00", "Canada/Pacific", 1603209600),
        ("2020-10-20, 9:00", "Canada/Eastern", 1603198800),
        ("2020-10-21, 21:15", "Canada/Pacific", 1603340100),
    ],
)
def test_datetime_to_timestamp(utils, dt_str, tz, expected):
    dt = datetime.strptime(dt_str, "%Y-%m-%d, %H:%M")
    timestamp = utils.datetime_to_timestamp(dt, tz=tz)
    assert int(timestamp / 1000) == expected
