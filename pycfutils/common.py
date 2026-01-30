import os
import sys
from typing import Any, AnyStr, Callable, Tuple, Union

PathLike = Union[os.PathLike, AnyStr]
PathFilter = Callable[[PathLike], bool]
StringFilter = Callable[[AnyStr], bool]
GenericFilter = Callable[[Any], bool]

GenericTuple = Tuple[Any, ...]


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
