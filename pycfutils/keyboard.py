#!/usr/bin/env python

import functools
import sys
import time
from typing import Any, Callable, Optional

__all__ = ("read_key",)


def _read_key(
    interval: float = 0.5,
    poll_interval: float = 0.1,
    kp_func: Optional[Callable[[], bool]] = None,
    rk_func: Optional[Callable[[], int]] = None,
    start_func: Optional[Callable[[], Any]] = None,
    end_func: Optional[Callable[[Any], None]] = None,
):
    ctx = start_func() if start_func is not None else None
    try:
        poll_interval = (
            interval / 2.0 if poll_interval > interval / 2.0 else poll_interval
        )
        time_end = time.time() + interval
        while True:
            if kp_func is not None and kp_func():
                return rk_func() if rk_func is not None else None
            if time.time() >= time_end:
                break
            time.sleep(poll_interval)
        return None
    finally:
        if end_func is not None:
            end_func(ctx)


if sys.platform[:3].lower() == "win":
    import msvcrt

    def _key_pressed_func() -> bool:
        return msvcrt.kbhit()

    def _read_key_func() -> int:
        return ord(msvcrt.getch())

    _start_func = None
    _end_func = None


else:  # Nix
    import select
    import termios
    import tty

    def _key_pressed_func() -> bool:
        return sys.stdin in select.select([sys.stdin], [], [], 0)[0]

    def _read_key_func() -> int:
        return ord(sys.stdin.read(1))

    def _start_func() -> Any:
        attrs = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno(), when=termios.TCSAFLUSH)
        return attrs

    def _end_func(attrs) -> None:
        if attrs is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, attrs)


read_key = functools.partial(
    _read_key,
    kp_func=_key_pressed_func,
    rk_func=_read_key_func,
    start_func=_start_func,
    end_func=_end_func,
)

del _end_func
del _start_func
del _read_key_func
del _key_pressed_func


if __name__ == "__main__":
    exit_char = 0x1B  # Esc
    print(f"Looping till 0x{exit_char:02X} is pressed")
    while 1:
        k = read_key()
        if k is not None:
            print(f"Pressed: 0x{k:02X} ({k:c})")
            if k == exit_char:
                print("Exit\n")
                break
