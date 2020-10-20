import json
from datetime import datetime

from pytz import timezone


class Utils:
    @staticmethod
    def dict_to_json(d, path):
        with open(path, "w") as f:
            json.dump(d, f, indent=2)

    @staticmethod
    def json_to_dict(path):
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def date_to_epoch_time(date_, timezone_="US/Eastern"):
        """Convert python date object to epoch time.

        Note:
            The datetime object is in UTC, so convert to timezone to ensure that the 24
            hour period covers all the events for the given region.

        Args:
            date_ (datetime.date): The date.
            timezone_ (str, optional): The timezone to use (see pytz documentation).
            Defaults to 'US/Eastern'.

        Returns:
            float: Timestamp representing midnight on the given date, for the given
            timezone.
        """
        dt = datetime(date_.year, date_.month, date_.day)

        return timezone(timezone_).localize(dt).timestamp() * 1000
