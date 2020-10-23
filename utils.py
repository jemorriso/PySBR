import json
from inspect import cleandoc
from textwrap import indent
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
    def str_format(s, indent_=0, dedent_l1=False):
        """Format multiline string.

        Args:
            s (str): The string to format.
            indent_ (int, optional): Number of tabs to indent. Defaults to 0.
            dedent_l1 (bool, optional): Set line 1 indentation to 0. Defaults to False.

        Returns:
            str: The formatted string.
        """
        tab = "    "
        s = indent(cleandoc(s), tab * indent_)
        if dedent_l1:
            lines = s.split("\n")
            lines[0] = lines[0].lstrip()
            s = "\n".join(lines)
        return s

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

        # TODO: make sure it still works
        return int(timezone(tz).localize(dt).timestamp() * 1000)

    @staticmethod
    def timestamp_to_datetime(ts, tz="US/Eastern"):
        return timezone(tz).localize(datetime.fromtimestamp(ts / 1000))
