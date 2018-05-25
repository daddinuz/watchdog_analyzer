import typing

from watchdog_analyzer.filtering import filter_dict
from watchdog_analyzer.trace import Trace


def get_all(trace: Trace) -> typing.Mapping:
    return trace


def get_leaks(trace: Trace) -> typing.Mapping:
    return filter_dict(trace, lambda p, k, v: isinstance(v, list) and len(v) > 0 and v[0]['size'] != 0)
