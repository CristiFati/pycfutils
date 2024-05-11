import unittest

try:
    from pycfutils.gstreamer import RegistryAccess
except Exception:
    RegistryAccess = None


# @TODO - cfati: Dummy
class GStreamerTestCase(unittest.TestCase):
    def test_registry_access(self):
        if RegistryAccess is None:
            return
        ra = RegistryAccess()
        self.assertIsInstance(ra.contents(), dict)
