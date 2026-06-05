"""Exception classes for pycfutils."""

import sys


class CFUtilsException(Exception):
    """Base exception for pycfutils, includes cause in string representation."""

    def __str__(self) -> str:
        if self.__cause__:
            return f"{super().__str__()} ({self.__cause__})"
        return super().__str__()


class ModuleException(CFUtilsException):
    """Exception raised by module-related operations."""


class NetworkException(CFUtilsException):
    """Exception raised by network-related operations."""


__all__ = ("CFUtilsException", "ModuleException", "NetworkException")


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
