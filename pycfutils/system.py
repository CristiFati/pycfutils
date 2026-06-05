"""System-level utilities."""

import multiprocessing
import os
import sys
import time
from os.path import dirname
from typing import AnyStr, Union

from pycfutils import common

# CPU

_CPU_BATCH_CYCLES = 25000000


def _cpu_stress(duration: float) -> None:
    start_time = time.time()
    try:
        while 1:
            i = 0
            for _ in range(_CPU_BATCH_CYCLES):
                i += 1
            if 0 < duration <= time.time() - start_time:
                break
    except KeyboardInterrupt:
        pass


def cpu_stress(duration: float, count: int = 1) -> None:
    """Spawn processes that busy-loop for a given duration to stress CPUs."""
    procs = []
    for _ in range(min(count, os.cpu_count() or -1)):
        procs.append(
            multiprocessing.Process(target=_cpu_stress, kwargs={"duration": duration})
        )
    for p in procs:
        p.start()
    for p in procs:
        p.join()


# FILESYSTEM


# pathlib.Path.parents equivalent
def path_ancestor(path: common.PathLike, level: int = 1) -> AnyStr:
    """Return the ancestor directory of a path at a given depth level."""
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


__all__ = (
    "cpu_stress",
    "path_ancestor",
)


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
