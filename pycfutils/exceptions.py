import sys


class CFUtilsException(Exception):
    def __str__(self):
        if self.__cause__:
            return f"{super().__str__()} ({self.__cause__})"
        return super().__str__()


class ModuleException(CFUtilsException):
    pass


class NetworkException(CFUtilsException):
    pass


__all__ = ("CFUtilsException", "ModuleException", "NetworkException")


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
