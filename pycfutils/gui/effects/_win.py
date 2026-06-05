import atexit
import ctypes as cts
import sys
from ctypes import wintypes as wts

track_modified_windows: bool = False

COLORREF = wts.DWORD

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x00000002

kernel32 = cts.WinDLL("Kernel32.dll")
user32 = cts.WinDLL("User32.dll")

GetLastError = kernel32.GetLastError
GetLastError.argtypes = ()
GetLastError.restype = wts.DWORD

SetLastError = kernel32.SetLastError
SetLastError.argtypes = (wts.DWORD,)
SetLastError.restype = None

GetWindowLong = user32.GetWindowLongA
GetWindowLong.argtypes = (wts.HWND, cts.c_int)
GetWindowLong.restype = wts.LONG

SetWindowLong = user32.SetWindowLongA
SetWindowLong.argtypes = (wts.HWND, cts.c_int, wts.LONG)
SetWindowLong.restype = wts.LONG

SetLayeredWindowAttributes = user32.SetLayeredWindowAttributes
SetLayeredWindowAttributes.argtypes = (wts.HWND, COLORREF, wts.BYTE, wts.DWORD)
SetLayeredWindowAttributes.restype = wts.BOOL


__global_modified_windows = set()
# @TODO - cfati:
#   Used to keep track of all windows that were added the WS_EX_LAYERED flag
#   - Might generate Out Of Memory (if ran many many times for a very very long time)


def set_window_transparency(hwnd: int, percent: int) -> int:
    SetLastError(0)
    style = GetWindowLong(hwnd, GWL_EXSTYLE)
    if style == 0:
        err = GetLastError()
        if err != 0:
            return err
    if style & WS_EX_LAYERED:
        modified = False
    else:
        SetLastError(0)
        if not SetWindowLong(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED):
            err = GetLastError()
            if err != 0:
                return err
        modified = True
    percent = max(0, min(percent, 100))
    opaque_percent = 100 - percent
    res = SetLayeredWindowAttributes(hwnd, 0, opaque_percent * 0xFF // 100, LWA_ALPHA)
    if not res:
        ret = GetLastError()
        if modified:
            SetWindowLong(hwnd, GWL_EXSTYLE, style & wts.DWORD(~WS_EX_LAYERED).value)
        return ret
    if track_modified_windows:
        if percent == 0:
            if hwnd in __global_modified_windows:
                SetLastError(0)
                if (
                    SetWindowLong(
                        hwnd, GWL_EXSTYLE, style & wts.DWORD(~WS_EX_LAYERED).value
                    )
                    == 0
                ):
                    err = GetLastError()
                    if err != 0:
                        return err
                __global_modified_windows.remove(hwnd)
        else:
            if modified:
                __global_modified_windows.add(hwnd)
    return 0


def _clear_flag():
    for hwnd in __global_modified_windows:
        style = GetWindowLong(hwnd, GWL_EXSTYLE)
        if style != 0:
            SetWindowLong(hwnd, GWL_EXSTYLE, style & wts.DWORD(~WS_EX_LAYERED).value)
    __global_modified_windows.clear()


atexit.register(_clear_flag)
del _clear_flag


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
