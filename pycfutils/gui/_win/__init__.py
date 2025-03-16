import atexit
import ctypes as cts
import os
import sys
from ctypes import wintypes as wts
from typing import Optional

import pycfutils
from pycfutils.system import path_ancestor

_DLL_NAME = os.path.join(
    path_ancestor(os.path.abspath(__file__), level=3),
    "hopa.dll",
)

try:
    _DLL = cts.CDLL(_DLL_NAME)
except:
    if pycfutils.__test_mode:
        _DLL = None

        def message_box(_0, _1, _2, _3, _4):
            return -1

    else:
        raise
else:
    _MessageBoxXY = _DLL.MessageBoxXY
    _MessageBoxXY.argtypes = (
        wts.HWND,
        wts.LPCWSTR,
        wts.LPCWSTR,
        wts.UINT,
        cts.c_int,
        cts.c_int,
    )
    _MessageBoxXY.restype = cts.c_int

    def message_box(
        title: str,
        text: str,
        x: Optional[int] = None,
        y: Optional[int] = None,
        style: int = 0,
        hwnd: Optional[wts.HWND] = None,
    ) -> int:
        return _MessageBoxXY(
            hwnd,
            text,
            title,
            style,
            x if x is not None else 0x80000000,
            y if y is not None else 0x80000000,
        )

    _clearHooks = _DLL.clearHooks
    _clearHooks.argtypes = ()
    _clearHooks.restype = cts.c_int
    atexit.register(_clearHooks)
    del _clearHooks

del _DLL
del _DLL_NAME


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
