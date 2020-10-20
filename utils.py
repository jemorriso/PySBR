import json

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
    def datetime_to_timestamp(dt, tz="US/Eastern"):
        """Convert python datetime object to epoch time.

        Note:
            The datetime object is naive, so localize using timezone.

        Args:
            dt (datetime.datetime): The datetime object.
            tz (str, optional): The timezone to use (see pytz documentation for list of
                available timezones). Defaults to 'US/Eastern'.

        Returns:
            float: Timestamp for the given datetime, for the given timezone.
        """

        return timezone(tz).localize(dt).timestamp() * 1000
