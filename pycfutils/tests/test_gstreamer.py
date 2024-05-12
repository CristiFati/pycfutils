import unittest

try:
    from pycfutils.gstreamer import RegistryAccess
except Exception:
    RegistryAccess = None


# @TODO - cfati: Dummy
class GStreamerTestCase(unittest.TestCase):
    if RegistryAccess is None:  # Mock (PyGObject not installed)

        def test_registry_access(self):
            import sys
            from types import ModuleType

            class GstDummy:
                Bin = None
                Pipeline = None

                @staticmethod
                def is_initialized():
                    return False

                @staticmethod
                def init():
                    pass

            print("PyGObject not installed. Run dummy test")

            gi = ModuleType("gi")
            sys.modules["gi"] = gi
            gi.repository = ModuleType("gi.repository")
            gi.repository.Gst = GstDummy
            gi.require_version = lambda ns, ver: None
            sys.modules["gi.repository"] = gi.repository

            from pycfutils.gstreamer import RegistryAccess

            ra = RegistryAccess()
            self.assertIsNotNone(ra)

    else:  # Real test (although dummy)

        def test_registry_access(self):
            ra = RegistryAccess()
            self.assertIsInstance(ra.contents(), dict)
