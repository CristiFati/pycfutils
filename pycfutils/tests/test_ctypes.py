import ctypes as cts
import unittest

from pycfutils import ctypes

FloatArr10 = cts.c_float * 10


class S0(ctypes.Structure):
    _fields_ = (
        ("i", cts.c_int),
        ("s", cts.c_char_p),
        ("fa", FloatArr10),
        ("pi", cts.POINTER(cts.c_int)),
    )


# @TODO - cfati: Dummy-ish
class CTypesTestCase(unittest.TestCase):
    def test_to_string(self):
        self.assertEqual(ctypes.to_string(1), "\n1\n")

    def test_structure(self):
        i = cts.c_int(1234)
        s0 = S0(
            -32,
            b"dummy text",
            FloatArr10(*(float(e) for e in range(20, 30))),
            cts.pointer(i),
        )
        s = s0.to_string(suffix=None)
        # print(s)
        self.assertIn("-32", s)
        self.assertIn("dummy text", s)
