import sys
import unittest

from pycfutils import gui


# @TODO - cfati: Dummy
class GUITestCase(unittest.TestCase):
    def test_message_box(self):
        message_box_name = "message_box"
        if sys.platform[:3].lower() == "win":
            self.assertIsNotNone(getattr(gui, message_box_name, None))
        else:
            self.assertIsNone(getattr(gui, message_box_name, None))
