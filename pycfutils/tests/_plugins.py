import sys

from pycfutils.miscellaneous import plugin

dummy_int = 0


def dummy_function():
    pass


class DummyPlugin0(plugin.BasePlugin):
    @staticmethod
    def dummy_static_method():
        pass

    @classmethod
    def dummy_class_method(cls):
        pass

    def dummy_method(self):
        pass


class DummyPlugin1(plugin.BasePlugin):
    pass


dummy_class_method = DummyPlugin0.dummy_class_method
dummy_static_method = DummyPlugin0.dummy_static_method
dummy_plugin0 = DummyPlugin0()
dummy_method = dummy_plugin0.dummy_method


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
