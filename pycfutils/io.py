#!/usr/bin/env python

import sys
import time
from typing import Any

__all__ = ("read_key",)


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


def read_key(
    timeout: float = 0.5,
    poll_interval: float = 0.1,
):
    ctx = _start_func() if _start_func is not None else None
    if timeout < 0:
        return _read_key_func() if _read_key_func is not None else None
    try:
        poll_interval = (
            timeout / 2.0 if poll_interval > timeout / 2.0 else poll_interval
        )
        time_end = time.time() + timeout
        while True:
            if _key_pressed_func is not None and _key_pressed_func():
                return _read_key_func() if _read_key_func is not None else None
            if time.time() >= time_end:
                break
            time.sleep(poll_interval)
        return None
    finally:
        if _end_func is not None:
            _end_func(ctx)


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
