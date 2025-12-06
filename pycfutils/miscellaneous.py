import calendar
import copy
import datetime
import inspect
import json
import math
import operator
import os
import random
import sys
import time
from enum import Enum
from pathlib import Path
from pprint import pprint
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
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
    local_auto_timezone: bool = False,  # Or UTC
    timezone_offset_minutes=0,  # Will not alter the actual time
) -> str:
    tz = None if local_auto_timezone else datetime.timezone.utc
    if timestamp is None:
        tm = datetime.datetime.now(tz=tz)
    elif isinstance(timestamp, (int, float)):
        tm = datetime.datetime.fromtimestamp(timestamp, tz=tz)
    elif isinstance(timestamp, time.struct_time):
        convert_func = time.mktime if local_auto_timezone else calendar.timegm
        tm = datetime.datetime.fromtimestamp(convert_func(timestamp), tz=tz)
    elif isinstance(timestamp, (tuple, list)):
        tm = datetime.datetime(*timestamp, tzinfo=tz)
    elif isinstance(timestamp, datetime.datetime):
        tm = timestamp
    else:
        return ""
    if timezone:
        if tm.tzinfo is None:
            tm = tm.astimezone(tz=tz)
        secs = tm.tzinfo.utcoffset(None).seconds
        if timezone_offset_minutes:
            negative = True if timezone_offset_minutes < 0 else False
            max_mins = 720 if negative else 840
            offset = abs(timezone_offset_minutes) % max_mins
            offset = round((offset or max_mins) / 30) * 30
            secs += offset * 60 * (-1 if negative else 1)
        negative = secs < 0
        tz_info = (negative,) + divmod(divmod(abs(secs), 60)[0], 60)
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
        if tz_info is not None:
            ret = f"{ret}{'-' if tz_info[0] else '+'}{tz_info[1]:02d}:{tz_info[2]:02d}"
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


def whoami(depth: int = 0) -> Tuple[str, int, str]:
    frame = sys._getframe(depth + 1)
    code = frame.f_code
    p = Path(code.co_filename)
    file = str(p.absolute()) if p.exists() else code.co_filename
    return file, frame.f_lineno, code.co_name  # , code.co_firstlineno


def call_stack(depth: int = 0, max_levels: int = 0) -> Tuple[Tuple[str, int, str]]:
    ret = []
    depth += 1
    while True:
        try:
            ret.append(whoami(depth=depth))
        except ValueError:
            break
        if 0 < max_levels <= depth:
            break
        depth += 1
    return tuple(reversed(ret))


def _bind_arguments_to_callable(
    callable_: Callable,
    *callable_args,
    callable_path_argument_target: Optional[Union[str, int]] = None,
    **callable_kwargs,
) -> Tuple[inspect.BoundArguments, str]:
    # print("++++++", callable_, callable_path_argument_target, callable_args, callable_kwargs)
    sig = inspect.signature(callable_)
    params = tuple(sig.parameters.items())
    if isinstance(callable_path_argument_target, str):
        if callable_path_argument_target not in sig.parameters:
            raise ValueError(
                f"Callable has no parameter named '{callable_path_argument_target}'"
            )
        path_argument_target = callable_path_argument_target
    elif isinstance(callable_path_argument_target, int):
        real_params = tuple(
            name
            for name, p in params
            if p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
        )
        if callable_path_argument_target < 0 or callable_path_argument_target >= len(
            real_params
        ):
            raise IndexError("Callable path argument index out of range")
        path_argument_target = real_params[callable_path_argument_target]
    elif callable_path_argument_target is None:
        for name, p in params:
            if p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
                path_argument_target = name
                break
        else:
            raise TypeError("No valid argument found for path")
    else:
        raise TypeError("Callable path argument target must be str, int, or None")
    bound = sig.bind_partial(*callable_args, **callable_kwargs)
    return bound, path_argument_target


def _process_path_items(
    path: Path,
    processor: Callable[..., Any],
    processor_bound_arguments: inspect.BoundArguments,
    processor_path_argument_target: str,
    processing_filter: Callable[[Path], bool],
    traversing_filter: Callable[[Path, int], bool],
    exception_handler: Optional[Callable[[Exception], None]],
    level: int,
) -> Generator:
    try:
        if processing_filter(path):
            processor_bound_arguments.arguments[processor_path_argument_target] = path
            yield str(path), processor(
                *processor_bound_arguments.args,
                **processor_bound_arguments.kwargs,
            )
        if path.is_dir() and traversing_filter(path, level):
            for item in path.glob("*"):
                yield from _process_path_items(
                    path=Path(item),
                    processor=processor,
                    processor_bound_arguments=processor_bound_arguments,
                    processor_path_argument_target=processor_path_argument_target,
                    processing_filter=processing_filter,
                    traversing_filter=traversing_filter,
                    exception_handler=exception_handler,
                    level=level + 1,
                )
    except Exception as e:
        if exception_handler:
            exception_handler(e)


def process_path_items(
    path: Union[str, bytes, os.PathLike],
    processor: Callable[..., Any],
    *processor_args,
    processor_path_argument_target: Optional[Union[str, int]] = None,
    processing_filter: Callable[[Path], bool] = lambda arg: True,
    traversing_filter: Callable[[Path, int], bool] = lambda arg0, arg1: not (
        arg0.is_symlink() and arg0.is_dir()
    ),
    exception_handler: Optional[Callable[[Exception], None]] = None,
    **processor_kwargs,
) -> Generator:
    # print("++++++", path, processor, processor_path_argument_target, processing_filter, traversing_filter, exception_handler, processor_args, processor_kwargs)
    if not isinstance(path, Path):
        path = Path(path)
    if not path.exists():
        if exception_handler:
            exception_handler(OSError("Path does not exist"))
        return None
    try:
        bound_args, path_target = _bind_arguments_to_callable(
            *processor_args,
            callable_=processor,
            callable_path_argument_target=processor_path_argument_target,
            **processor_kwargs,
        )
    except Exception as e:
        if exception_handler:
            exception_handler(e)
        return None
    else:
        yield from _process_path_items(
            path=path,
            processor=processor,
            processor_bound_arguments=bound_args,
            processor_path_argument_target=path_target,
            processing_filter=processing_filter,
            traversing_filter=traversing_filter,
            exception_handler=exception_handler,
            level=1,  # Item processed before depth check
        )


__all__ = (
    "process_path_items",
    "call_stack",
    "dimensions_2d",
    "int_format",
    "merge_dicts",
    "nest_object",
    "nested_dict_item",
    "pretty_print",
    "progression",
    "randomize",
    "timed_execution",
    "timestamp_string",
    "uniques",
    "whoami",
    "write_json_to_file",
)


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
