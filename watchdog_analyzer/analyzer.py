import typing

from filter_dict import filter_dict

from watchdog_analyzer.trace import Trace


def get_all(trace: Trace) -> typing.Mapping:
    return trace


def get_leaks(trace: Trace) -> typing.Mapping:
    return filter_dict(lambda p, k, v: isinstance(v, list) and len(v) > 0 and v[-1]['size'] != 0, trace)
