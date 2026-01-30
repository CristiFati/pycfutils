import pathlib
import unittest

from pycfutils.miscellaneous.plugin import BasePlugin


class MiscellaneousPluginTestCase(unittest.TestCase):
    _PLUGINS_FILE = "_plugins.py"
    _PLUGIN_COUNT = 2  # BasePlugin derived classes from _PLUGINS_FILE

    @classmethod
    def filter_file(cls, item):
        return item.name == cls._PLUGINS_FILE

    def setUp(self):
        self.this_file = pathlib.Path(__file__).absolute()
        self.this_dir = self.this_file.parent
        self.plugins_file = self.this_dir / self._PLUGINS_FILE

    def test_load_plugins(self):
        res = BasePlugin.load(self.this_dir)
        self.assertEqual(self._PLUGIN_COUNT, len(res))
        res = BasePlugin.load(str(self.this_dir))
        self.assertEqual(self._PLUGIN_COUNT, len(res))
        res = BasePlugin.load(str(self.plugins_file))
        self.assertEqual(self._PLUGIN_COUNT, len(res))
        res = BasePlugin.load(
            self.this_dir, filesystem_filter_function=lambda arg: False
        )
        self.assertEqual((), res)
        res = BasePlugin.load(
            self.this_dir,
            filesystem_filter_function=lambda arg: arg.name == "_manual.py",
        )
        self.assertEqual((), res)
        res = BasePlugin.load(
            self.this_dir, filesystem_filter_function=self.filter_file
        )
        self.assertEqual(self._PLUGIN_COUNT, len(res))
        res = BasePlugin.load(
            self.this_dir,
            filesystem_filter_function=self.filter_file,
            name_filter_function=lambda arg: arg[1:5] == "ummy",
        )
        self.assertEqual(self._PLUGIN_COUNT, len(res))
        res = BasePlugin.load(
            self.this_dir,
            filesystem_filter_function=self.filter_file,
            name_filter_function=lambda arg: arg[:5] == "dummy",
        )
        self.assertEqual((), res)
        res = BasePlugin.load(
            self.this_dir,
            filesystem_filter_function=self.filter_file,
            name_filter_function=lambda arg: arg.endswith("0"),
        )
        self.assertEqual(1, len(res))
        res = BasePlugin.load(
            self.this_dir,
            filesystem_filter_function=self.filter_file,
            item_filter_function=lambda arg: "invalid" in dir(arg),
        )
        self.assertEqual((), res)
        res = BasePlugin.load(
            self.this_dir,
            filesystem_filter_function=self.filter_file,
            item_filter_function=lambda arg: issubclass(arg, BasePlugin),
        )
        self.assertEqual(self._PLUGIN_COUNT, len(res))
