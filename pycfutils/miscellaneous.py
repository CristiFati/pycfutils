import math
import sys
import time
from datetime import datetime
from os import PathLike
from os.path import dirname
from typing import AnyStr, Sequence, Tuple, Union

__all__ = (
    "dimensions_2d",
    "int_format",
    "path_ancestor",
    "timestamp_string",
    "uniques",
)


def dimensions_2d(n: int) -> Tuple:
    if n <= 0:
        return 0, 0
    sq = round(math.sqrt(n))
    return sq, math.ceil(n / sq)


def int_format(limit: int) -> str:
    sgn = 1 if limit < 0 else 0
    return f"{{:0{math.ceil(math.log10(max(abs(limit), 2))) + sgn:d}d}}"


# pathlib.Path.parents equivalent
def path_ancestor(path: Union[PathLike, AnyStr], level: int = 1) -> AnyStr:
    pass
    if level <= 0:
        return path if isinstance(path, (str, bytes)) else str(path)
    ret = dirname(path)
    while level > 1:
        path = ret
        ret = dirname(path)
        if ret == path:
            break
        level -= 1
    return ret


def timestamp_string(
    timestamp: Union[None, int, float, Sequence] = None,
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


def uniques(sequence: Sequence) -> Sequence:
    ret = []
    handled = set()
    for e in sequence:
        if e not in handled:
            ret.append(e)
            handled.add(e)
    return ret if isinstance(sequence, list) else tuple(ret)


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
