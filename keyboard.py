#!/usr/bin/env python

# Keyboard utility script by (pussious) cfati

import functools as fts
import sys
import time


__all__ = (
    "read_key",
)

plat = sys.platform[:3].lower()


def __read_key(interval=0.5, poll_interval=0.1, kp_func=None, rk_func=None, start_func=None, end_func=None):
    ctx = start_func() if start_func is not None else None
    try:
        poll_interval = interval / 2.0 if poll_interval > interval / 2.0 else poll_interval
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


if plat == "win":
    import msvcrt

    def __key_pressed_func():
        return msvcrt.kbhit()

    def __read_key_func():
        return ord(msvcrt.getch())

    __start_func = None
    __end_func = None
 
 
else:  # Nix
    import select
    import termios
    import tty

    def __key_pressed_func():
        return sys.stdin in select.select([sys.stdin], [], [], 0)[0]

    def __read_key_func():
        return ord(sys.stdin.read(1))

    def __start_func():
        attrs = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno(), when=termios.TCSAFLUSH)
        return attrs

    def __end_func(attrs):
        if attrs is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, attrs)


read_key = fts.partial(__read_key, kp_func=__key_pressed_func, rk_func=__read_key_func, start_func=__start_func, end_func=__end_func)


if __name__ == "__main__":
    exit_char = 0x1B  # Esc
    print("Looping till 0x{:02X} is pressed".format(exit_char))
    while 1:
        k = read_key()
        if k is not None:
            print("Pressed: 0x{:02X} ({:c})".format(k, k))
            if k == exit_char:
                print("Exit\n")
                break

