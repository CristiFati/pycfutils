import sys
from os import PathLike
from os.path import dirname
from typing import AnyStr, Union

__all__ = ("path_ancestor",)


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
