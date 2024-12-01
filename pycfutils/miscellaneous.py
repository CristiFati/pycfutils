import math
import operator
import sys
import time
from datetime import datetime
from pprint import pprint
from typing import Any, Callable, Dict, Iterable, Optional, Sequence, Tuple, Union

Numeric = Union[int, float]


def dimensions_2d(n: int) -> Tuple:
    if n <= 0:
        return 0, 0
    sq = round(math.sqrt(n))
    return sq, math.ceil(n / sq)


def int_format(limit: int) -> str:
    sgn = 1 if limit < 0 else 0
    return f"{{:0{math.ceil(math.log10(max(abs(limit), 2))) + sgn:d}d}}"


def timestamp_string(
    timestamp: Union[None, Sequence, datetime, int, float] = None,
    human_readable: bool = False,
    date_separator: str = "-",
    time_separator: str = ":",
    separator: str = " ",
) -> str:
    tm = (
        time.gmtime(timestamp)
        if timestamp is None or isinstance(timestamp, (int, float))
        else timestamp.timetuple() if isinstance(timestamp, datetime) else timestamp
    )[:6]
    if human_readable:
        return (
            f"{tm[0]:04d}{date_separator}"
            f"{tm[1]:02d}{date_separator}"
            f"{tm[2]:02d}{separator}"
            f"{tm[3]:02d}{time_separator}"
            f"{tm[4]:02d}{time_separator}{tm[5]:02d}"
        )
    return f"{tm[0]:04d}{tm[1]:02d}{tm[2]:02d}{tm[3]:02d}{tm[4]:02d}{tm[5]:02d}"


def _callable_string(callable_: Callable, *args: Tuple, **kwargs: Dict) -> str:
    arg_sep = ", "
    args_str = arg_sep.join(["{}"] * len(args)).format(*args) if args else ""
    kwargs_str = (
        arg_sep.join(["{}={}".format(k, v) for k, v in kwargs.items()])
        if kwargs
        else ""
    )
    return f"{callable_.__name__}({args_str}{arg_sep if args_str and kwargs_str else ''}{kwargs_str})"


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


def pretty_print(obj, head=None, indent=2, sort_dicts=False):
    if head is not None:
        print(head)
    pprint(obj, indent=indent, sort_dicts=sort_dicts)


__all__ = (
    "dimensions_2d",
    "int_format",
    "pretty_print",
    "progression",
    "timed_execution",
    "timestamp_string",
    "uniques",
)


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
