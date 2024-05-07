import unittest
from datetime import datetime

from pycfutils import common


class CommonTestCase(unittest.TestCase):
    def test_int_format(self):
        self.assertEqual(common.int_format(-101), "{:04d}")
        self.assertEqual(common.int_format(-100), "{:03d}")
        self.assertEqual(common.int_format(-11), "{:03d}")
        self.assertEqual(common.int_format(-10), "{:02d}")
        self.assertEqual(common.int_format(-1), "{:02d}")
        self.assertEqual(common.int_format(0), "{:01d}")
        self.assertEqual(common.int_format(1), "{:01d}")
        self.assertEqual(common.int_format(10), "{:01d}")
        self.assertEqual(common.int_format(11), "{:02d}")
        self.assertEqual(common.int_format(100), "{:02d}")
        self.assertEqual(common.int_format(101), "{:03d}")

    def test_timestamp_string(self):
        ts = (2024, 5, 6, 12, 34, 56)
        self.assertEqual(
            common.timestamp_string(timestamp=ts, human_readable=False),
            "20240506123456",
        )
        self.assertEqual(
            common.timestamp_string(timestamp=ts, human_readable=True),
            "2024-05-06 12:34:56",
        )
        self.assertTrue(common.timestamp_string(datetime.now()))

    def test_uniques(self):
        l0 = [1, 2, 3, 1, 4, 3, 5, 1, 1, 2, 6, 0, 0]
        l1 = [1, 2, 3, 4, 5, 6, 0]
        self.assertEqual(common.uniques([]), [])
        self.assertEqual(common.uniques(()), ())
        self.assertEqual(common.uniques(range(3)), (0, 1, 2))
        self.assertEqual(common.uniques(l0), l1)
        self.assertEqual(common.uniques((e for e in l0)), tuple(l1))
        self.assertEqual(set(common.uniques(set(l0))), set(l0))

    def test_dimensions2d(self):
        self.assertEqual(common.dimensions_2d(-3), (0, 0))
        self.assertEqual(common.dimensions_2d(0), (0, 0))
        self.assertEqual(common.dimensions_2d(1), (1, 1))
        self.assertEqual(common.dimensions_2d(2), (1, 2))
        self.assertEqual(common.dimensions_2d(3), (2, 2))
        self.assertEqual(common.dimensions_2d(4), (2, 2))
        self.assertEqual(common.dimensions_2d(5), (2, 3))
        self.assertEqual(common.dimensions_2d(6), (2, 3))
        self.assertEqual(common.dimensions_2d(7), (3, 3))
        self.assertEqual(common.dimensions_2d(8), (3, 3))
        self.assertEqual(common.dimensions_2d(9), (3, 3))
        self.assertEqual(common.dimensions_2d(10), (3, 4))
        self.assertEqual(common.dimensions_2d(13), (4, 4))
        self.assertEqual(common.dimensions_2d(20), (4, 5))
