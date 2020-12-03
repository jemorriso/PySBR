import json
from inspect import cleandoc
from textwrap import indent
from datetime import datetime
from pathlib import Path
import pathlib
from typing import Dict, Any, List

from pytz import timezone, utc
import yaml


def dump_json(d, path: str):
    """Write json to file specified by path.

    Raises:
        FileNotFoundError
    """
    with open(path, "w") as f:
        json.dump(d, f, indent=2)


def load_json(path) -> Dict:
    """Read json from file specified by path.

    Raises:
        FileNotFoundError
    """
    with open(path) as f:
        return json.load(f)


def load_yaml(path: str) -> Dict:
    """Read yaml from file specified by path.

    Raises:
        FileNotFoundError
    """
    with open(path) as f:
        return yaml.full_load(f)


def dump_yaml(d, path):
    """Write yaml to file specified by path.

    Raises:
        FileNotFoundError
    """
    with open(path, "w") as f:
        yaml.dump(d, f)


def get_project_root() -> pathlib.PosixPath:
    """Get pathlib representation of project's root folder."""
    return Path(__file__).parent.parent


def build_yaml_path(fname: str, subpath: str = "pysbr/config") -> pathlib.PosixPath:
    """Build an absolute path to the .yaml file specified by fname and subpath."""
    return get_project_root().joinpath(f"{subpath}/{fname}.yaml")


def str_format(
    s: str, indent_: int = 0, dedent_l1: bool = False, squish: bool = False
) -> str:
    """Format and return string s.

    Args:
        indent_: The number of tabs to indent each line of the string with.
        dedent_l1: Dedent line 1. This is added as an argument because if inserting a
            multiline string into a template string, only the first line gets the
            indentation from the template string.
        squish: If true, compress the string into one line.
    """
    tab = "    "
    s = indent(cleandoc(s), tab * indent_)
    if dedent_l1:
        lines = s.split("\n")
        lines[0] = lines[0].lstrip()
        s = "\n".join(lines)
    return s if not squish else s.replace("\n", " ")


def make_list(item: Any) -> List:
    """Return item inside a list, if it isn't already a list."""

    if not isinstance(item, list):
        return [item]
    else:
        return item


def datetime_to_timestamp_aware(dt: datetime, tz: str = None) -> int:
    """**DEPRECATED** Convert datetime object to Unix timestamp, in milliseconds.

    tz refers to the timezone to use (see pytz documentation for list of
            available timezones). If None, uses system timezone.
    """
    if dt.tzinfo is None:
        dt = timezone(tz).localize(dt) if tz is not None else dt.astimezone()
    return int(dt.timestamp() * 1000)


def timestamp_to_datetime_aware(ts: int, tz: str = None) -> datetime:
    """**DEPRECATED** Convert Unix timestamp ts to timezone aware datetime object.

    tz refers to the timezone to use (see pytz documentation for list of
            available timezones). If None, uses system timezone.
    """
    utc_dt = utc.localize(datetime.utcfromtimestamp(ts / 1000))
    return utc_dt.astimezone(timezone(tz) if tz is not None else None)


def datetime_to_timestamp(dt: datetime) -> int:
    """Convert datetime to Unix timestamp in milliseconds"""
    return int(dt.timestamp() * 1000)


def timestamp_to_datetime(ts: int) -> datetime:
    """Convert Unix timestamp (in milliseconds) to datetime.

    The returned datetime object is aware, and uses the system timezone.
    """
    return datetime.fromtimestamp(ts / 1000).astimezone()


def timestamp_to_iso_str(ts: int) -> str:
    """Convert Unix timestamp (in milliseconds) to ISO string."""

    return timestamp_to_datetime(ts).replace(microsecond=0).isoformat()


def iso_str_to_timestamp(iso_str: str) -> int:
    """Convert iso str to Unix timestamp in milliseconds."""
    return datetime.fromisoformat(iso_str).timestamp() * 1000


def iso_zulu_to_offset(iso_str: str) -> str:
    """Convert ISO string in Zulu time to UTC offset.

    Does not check the contents of the ISO string - assumes it is a correctly formatted
    ISO string in Zulu time.
    """
    return iso_str.replace("Z", "+00:00")
