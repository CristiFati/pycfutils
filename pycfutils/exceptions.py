import sys


class CFUtilsException(Exception):
    pass


class ModuleException(CFUtilsException):
    pass


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
