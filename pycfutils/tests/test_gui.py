import sys
import unittest

from pycfutils import gui


# @TODO - cfati: Dummy
class GUITestCase(unittest.TestCase):
    def test_message_box(self):
        message_box = getattr(gui, "message_box", None)
        if sys.platform[:3].lower() == "win":
            self.assertIsNotNone(message_box)
        else:
            self.assertIsNone(message_box)
