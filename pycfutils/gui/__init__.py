import sys

__all__ = ()

plat = sys.platform.lower()
if plat == "win32":
    from pycfutils.gui._win import constants, message_box

    __all__ += (
        "message_box",
        "constants",
    )


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
