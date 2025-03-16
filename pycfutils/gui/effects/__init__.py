import sys

plat = sys.platform.lower()
if plat == "win32":
    from pycfutils.gui.effects._win import (
        set_window_transparency,
        track_modified_windows,
    )

    __all__ = (
        "set_window_transparency",
        "track_modified_windows",
    )
else:
    __all__ = ()


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
