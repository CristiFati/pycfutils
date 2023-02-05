
# Common utilities script by (pussious) cfati

import math
import sys
import time


def int_fmt(limit):
    return "{{:0{:d}d}}".format(math.ceil(math.log10(max(limit, 1))))


def ts_str(timestamp=None, human_readable=False):
    tm = (time.gmtime(timestamp) if isinstance(timestamp, (int, float, None.__class__)) else timestamp)[:6]
    if human_readable:
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*tm)
    return "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}".format(*tm)


def dims_2d(n):
    if n <= 0:
        return 0, 0
    sq = round(math.sqrt(n))
    return sq, math.ceil(n / sq)


def uniques(seq):
    ret = []
    handled = set()
    for e in seq:
        if e not in handled:
            ret.append(e)
            handled.add(e)
    return tuple(ret)


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)

