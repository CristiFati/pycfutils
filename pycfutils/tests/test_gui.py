import sys
import unittest

from pycfutils import gui
from pycfutils.gui import effects

plat = sys.platform.lower()
_IS_WIN = plat == "win32"


# @TODO - cfati: Dummy
class GUITestCase(unittest.TestCase):
    def test_message_box(self):
        message_box = getattr(gui, "message_box", None)
        if _IS_WIN:
            self.assertIsNotNone(message_box)
        else:
            self.assertIsNone(message_box)

    def test_effects(self):
        for e in getattr(effects, "__all__", ()):
            self.assertIsNotNone(getattr(effects, e))
