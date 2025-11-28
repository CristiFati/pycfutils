import calendar
import copy
import datetime
import json
import math
import operator
import random
import sys
import time
from enum import Enum
from pprint import pprint
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Reversible,
    Sequence,
    Tuple,
    Union,
)


class DictMergeOverlapPolicy(Enum):
    JOIN_LIST = 0
    JOIN_TUPLE = 1
    DELETE = 2
    LEFT = 3
    RIGHT = 4
    DEFAULT = JOIN_LIST


Numeric = Union[int, float]

if sys.version_info[:2] >= (3, 9):
    TimestampStringCallable = Callable[[Any, ...], datetime.datetime]
else:
    TimestampStringCallable = Callable[..., datetime.datetime]


def dimensions_2d(n: int) -> Tuple:
    if n <= 0:
        return 0, 0
    sq = round(math.sqrt(n))
    return sq, math.ceil(n / sq)


def int_format(limit: int) -> str:
    sgn = 1 if limit < 0 else 0
    return f"{{:0{math.ceil(math.log10(max(abs(limit), 2))) + sgn:d}d}}"


def timestamp_string(
    timestamp: Union[None, Sequence, datetime.datetime, int, float] = None,
    human_readable: bool = False,
    date_separator: str = "-",
    time_separator: str = ":",
    separator: str = " ",
    microseconds: bool = False,
    timezone: bool = False,
    local: bool = False,
    # Convert to datetime.datetime
    convert_function: TimestampStringCallable = lambda arg, *args: arg,
    convert_function_extra_args: Tuple = (),
) -> str:
    tz = None if local else datetime.timezone.utc
    if timestamp is None:
        tm = datetime.datetime.now(tz=tz)
    elif isinstance(timestamp, (int, float)):
        tm = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    elif isinstance(timestamp, time.struct_time):
        convert_func = time.mktime if local else calendar.timegm
        tm = datetime.datetime.fromtimestamp(convert_func(timestamp), tz=tz)
    elif isinstance(timestamp, (tuple, list)):
        tm = datetime.datetime(*timestamp, tzinfo=tz)
    elif callable(convert_function):
        tm = convert_function(timestamp, *convert_function_extra_args)
    else:
        tm = timestamp
    if timezone:
        if tm.tzinfo is None:
            tm = tm.astimezone(tz=tz)
        secs = tm.tzinfo.utcoffset(None).seconds
        negative = True if secs < 0 else False
        tz_info = divmod(divmod(abs(secs), 60)[0], 60)
        if negative:
            tz_info = -tz_info[0], tz_info[1]
    else:
        tz_info = None
    if human_readable:
        ret = (
            f"{tm.year:04d}{date_separator}"
            f"{tm.month:02d}{date_separator}"
            f"{tm.day:02d}{separator}"
            f"{tm.hour:02d}{time_separator}"
            f"{tm.minute:02d}{time_separator}"
            f"{tm.second:02d}"
        )
        if microseconds:
            ret = f"{ret}.{tm.microsecond:06d}"
        if tz_info:
            ret = f"{ret}{tz_info[0]:+03d}:{tz_info[1]:02d}"
    else:
        ret = (
            f"{tm.year:04d}{tm.month:02d}{tm.day:02d}"
            f"{tm.hour:02d}{tm.minute:02d}{tm.second:02d}"
        )
        if microseconds:
            ret = f"{ret}{tm.microsecond:06d}"
    return ret


def _callable_string(callable_: Callable, *args: Tuple, **kwargs: Dict) -> str:
    arg_sep = ", "
    args_str = arg_sep.join(["{}"] * len(args)).format(*args) if args else ""
    kwargs_str = (
        arg_sep.join(["{}={}".format(k, v) for k, v in kwargs.items()])
        if kwargs
        else ""
    )
    return (
        f"{callable_.__name__}({args_str}"
        f"{arg_sep if args_str and kwargs_str else ''}{kwargs_str})"
    )


# @Decorator
def timed_execution(
    print_time: bool = True,
    print_arguments: bool = False,
    return_time: bool = False,
) -> Callable:
    def callable_wrapper0(callable_: Callable) -> Callable:
        def callable_wrapper1(*args: Tuple, **kwargs: Dict) -> Any:
            start_time = time.time()
            ret = callable_(*args, **kwargs)
            dt = time.time() - start_time
            if print_time:
                text = (
                    _callable_string(callable_, *args, **kwargs)
                    if print_arguments
                    else callable_.__name__
                )
                print(f"Execution of {text} took {dt:.3f} seconds")
            if return_time:
                return ret, dt
            return ret

        return callable_wrapper1

    return callable_wrapper0


def uniques(sequence: Iterable[Any]) -> Iterable[Any]:
    handled = set()
    for e in sequence:
        if e not in handled:
            handled.add(e)
            yield e


def progression(
    *,
    ratio: Numeric,
    first: Numeric = 1,
    count: int = 16,
    op: Callable[[Numeric, Numeric], Numeric] = operator.mul,
    stop_function: Optional[Callable[[Numeric], bool]] = None,
) -> Iterable[Numeric]:
    idx = 0
    val = float(first) if isinstance(ratio, float) else first
    while True:
        yield val
        val = op(val, ratio)
        idx += 1
        if 0 < count <= idx:
            break
        if stop_function is not None and stop_function(val):
            break


def pretty_print(
    obj: Any,
    head: Any = None,
    tail: Any = None,
    indent: int = 2,
    sort_dicts: bool = False,
):
    if head is not None:
        print(head)
    pprint(obj, indent=indent, sort_dicts=sort_dicts)
    if tail is not None:
        print(tail)


def nested_dict_item(data: Dict, keys: Iterable[Any]):
    for key in keys:
        data = data[key]
    return data


def nest_object(keys: Reversible[Any], value: Any):
    for key in reversed(keys):
        value = {key: value}
    return value


def _merge_dicts(
    left: Dict,
    right: Dict,
    overlap_policy: DictMergeOverlapPolicy,
):
    ret = {}
    for k, v in left.items():
        ret[k] = v
    for k, v in right.items():
        if k in ret:
            dk = ret[k]
            if isinstance(dk, dict) and isinstance(v, dict):
                ret[k] = merge_dicts(dk, v, overlap_policy)
            else:
                if overlap_policy == DictMergeOverlapPolicy.JOIN_TUPLE:
                    ret[k] = (dk, v)
                elif overlap_policy == DictMergeOverlapPolicy.RIGHT:
                    ret[k] = v
                elif overlap_policy == DictMergeOverlapPolicy.DELETE:
                    del ret[k]
                elif overlap_policy == DictMergeOverlapPolicy.LEFT:
                    pass
                else:
                    ret[k] = [dk, v]
        else:
            ret[k] = v
    return ret


def merge_dicts(
    left: Dict,
    right: Dict,
    overlap_policy: DictMergeOverlapPolicy = DictMergeOverlapPolicy.DEFAULT,
):
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise TypeError("One of the supplied arguments is not a dict")
    return copy.deepcopy(_merge_dicts(left, right, overlap_policy))


def write_json_to_file(json_obj, file_name, newline="", indent=2):
    with open(file_name, mode="w", newline=newline) as f:
        json.dump(json_obj, f, indent=indent)


def randomize(
    value: float,
    left_deviation_percent: int = 10,
    right_deviation_percent: int = 10,
    round_result: bool = False,
    round_digits: Optional[int] = None,
) -> float:
    if left_deviation_percent <= 0 and right_deviation_percent <= 0:
        return round(value, ndigits=round_digits) if round_result else value
    upper_dev = abs(value) * max(right_deviation_percent, 0) / 100
    lower_dev = abs(value) * max(left_deviation_percent, 0) / 100
    ret = random.uniform(value - lower_dev, value + upper_dev)
    return round(ret, ndigits=round_digits) if round_result else ret


__all__ = (
    "dimensions_2d",
    "int_format",
    "merge_dicts",
    "nest_object",
    "nested_dict_item",
    "pretty_print",
    "progression",
    "timed_execution",
    "timestamp_string",
    "uniques",
    "write_json_to_file",
    "randomize",
)


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
