import multiprocessing
import os
import sys
import time
from os import PathLike
from os.path import dirname
from typing import AnyStr, Union

__all__ = (
    "path_ancestor",
    "cpu_stress",
)


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
    procs = []
    for _ in range(min(count, os.cpu_count())):
        procs.append(
            multiprocessing.Process(target=_cpu_stress, kwargs={"duration": duration})
        )
    for p in procs:
        p.start()
    for p in procs:
        p.join()


# FILESYSTEM


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


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
