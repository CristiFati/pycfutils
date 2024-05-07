import time
import unittest

from pycfutils import keyboard


class KwyboardTestCase(unittest.TestCase):
    def test_read_key(self):
        itv = 0.5
        pitv = 0.1
        margin = 0.05
        ts = time.time()
        k = keyboard.read_key(interval=itv, poll_interval=pitv)
        self.assertTrue(k is not None or abs(time.time() - ts - itv) < pitv + margin)
