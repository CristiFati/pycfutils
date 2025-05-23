import contextlib
import operator
import time
import unittest
from datetime import datetime
from io import StringIO
from unittest import mock

from pycfutils import miscellaneous


class MiscellaneousTestCase(unittest.TestCase):
    def test_dimensions_2d(self):
        self.assertEqual(miscellaneous.dimensions_2d(-3), (0, 0))
        self.assertEqual(miscellaneous.dimensions_2d(0), (0, 0))
        self.assertEqual(miscellaneous.dimensions_2d(1), (1, 1))
        self.assertEqual(miscellaneous.dimensions_2d(2), (1, 2))
        self.assertEqual(miscellaneous.dimensions_2d(3), (2, 2))
        self.assertEqual(miscellaneous.dimensions_2d(4), (2, 2))
        self.assertEqual(miscellaneous.dimensions_2d(5), (2, 3))
        self.assertEqual(miscellaneous.dimensions_2d(6), (2, 3))
        self.assertEqual(miscellaneous.dimensions_2d(7), (3, 3))
        self.assertEqual(miscellaneous.dimensions_2d(8), (3, 3))
        self.assertEqual(miscellaneous.dimensions_2d(9), (3, 3))
        self.assertEqual(miscellaneous.dimensions_2d(10), (3, 4))
        self.assertEqual(miscellaneous.dimensions_2d(13), (4, 4))
        self.assertEqual(miscellaneous.dimensions_2d(20), (4, 5))

    def test_int_format(self):
        self.assertEqual(miscellaneous.int_format(-101), "{:04d}")
        self.assertEqual(miscellaneous.int_format(-100), "{:03d}")
        self.assertEqual(miscellaneous.int_format(-11), "{:03d}")
        self.assertEqual(miscellaneous.int_format(-10), "{:02d}")
        self.assertEqual(miscellaneous.int_format(-1), "{:02d}")
        self.assertEqual(miscellaneous.int_format(0), "{:01d}")
        self.assertEqual(miscellaneous.int_format(1), "{:01d}")
        self.assertEqual(miscellaneous.int_format(10), "{:01d}")
        self.assertEqual(miscellaneous.int_format(11), "{:02d}")
        self.assertEqual(miscellaneous.int_format(100), "{:02d}")
        self.assertEqual(miscellaneous.int_format(101), "{:03d}")

    def test_timestamp_string(self):
        ts = (2024, 5, 6, 12, 34, 56)
        self.assertEqual(
            miscellaneous.timestamp_string(timestamp=ts, human_readable=False),
            "20240506123456",
        )
        self.assertEqual(
            miscellaneous.timestamp_string(timestamp=ts, human_readable=True),
            "2024-05-06 12:34:56",
        )
        self.assertTrue(miscellaneous.timestamp_string(datetime.now()))

    def test_uniques(self):
        l0 = [1, 2, 3, 1, 4, 3, 5, 1, 1, 2, 6, 0, 0]
        l1 = [1, 2, 3, 4, 5, 6, 0]
        self.assertEqual(list(miscellaneous.uniques([])), [])
        self.assertEqual(tuple(miscellaneous.uniques(range(3))), (0, 1, 2))
        self.assertEqual(list(miscellaneous.uniques(l0)), l1)
        self.assertEqual(list(miscellaneous.uniques(l0)), l1)
        self.assertEqual(list(miscellaneous.uniques(e for e in l0)), l1)

    def test_progression(self):
        self.assertEqual(list(miscellaneous.progression(ratio=2, count=3)), [1, 2, 4])
        self.assertEqual(
            list(
                miscellaneous.progression(ratio=3, stop_function=lambda arg: arg > 80)
            ),
            [1, 3, 9, 27],
        )
        self.assertEqual(
            list(miscellaneous.progression(ratio=-2, count=4)), [1, -2, 4, -8]
        )
        self.assertEqual(
            list(
                miscellaneous.progression(
                    ratio=-1,
                    op=operator.add,
                    count=0,
                    stop_function=lambda arg: arg <= -3,
                )
            ),
            [1, 0, -1, -2],
        )
        self.assertEqual(
            list(
                miscellaneous.progression(ratio=0.5, first=0, count=4, op=operator.add)
            ),
            [0.0, 0.5, 1, 1.5],
        )
        self.assertEqual(
            list(miscellaneous.progression(ratio=0, first=0, count=9, op=operator.add)),
            [0] * 9,
        )

    def test_timed_execution(self):
        bools = (False, True)
        sleep_val = 0.2
        ret_val = 1618
        suppress_stdout = 1  # @TODO - cfati: Set to 0 to visualize decorator output
        for pt in bools:
            for pa in bools:
                for rt in bools:
                    with (
                        mock.patch("sys.stdout", new=StringIO())
                        if suppress_stdout
                        else contextlib.nullcontext()
                    ):

                        @miscellaneous.timed_execution(
                            print_time=pt, print_arguments=pa, return_time=rt
                        )
                        def dummy_function0():
                            pass

                        @miscellaneous.timed_execution(
                            print_time=pt, print_arguments=pa, return_time=rt
                        )
                        def dummy_function1(arg0, arg1, arg2, kw0=-3, kw1="dummy"):
                            time.sleep(sleep_val)
                            return ret_val

                        dummy_function0()
                        ret = dummy_function1({b"1": 2}, 0.5, arg2=(2, "3", []), kw0=55)
                        if rt:
                            self.assertEqual(ret[0], ret_val)
                            self.assertGreater(0.1, abs(sleep_val - ret[1]))
                        else:
                            self.assertEqual(ret, ret_val)

    def test_nested_dict_item(self):
        d = {1: {2: {3: {4: 5, 6: 7}}, 8: {9: 0}}}
        self.assertEqual(miscellaneous.nested_dict_item(d, ()), d)
        self.assertEqual(miscellaneous.nested_dict_item(d, (1,)), d[1])
        self.assertEqual(miscellaneous.nested_dict_item(d, [1, 2]), d[1][2])
        self.assertEqual(miscellaneous.nested_dict_item(d, (1, 2, 3, 4)), d[1][2][3][4])
        self.assertEqual(miscellaneous.nested_dict_item(d, {1: 69}), d[1])
        self.assertRaises(TypeError, miscellaneous.nested_dict_item, d, None)
        self.assertRaises(KeyError, miscellaneous.nested_dict_item, d, (69,))
        self.assertRaises(KeyError, miscellaneous.nested_dict_item, d, (1, 69))
        self.assertRaises(KeyError, miscellaneous.nested_dict_item, d, [1, 2, 69])
        self.assertRaises(KeyError, miscellaneous.nested_dict_item, d, (1, 2, 3, 69))
        self.assertRaises(KeyError, miscellaneous.nested_dict_item, d, ("1",))
        self.assertRaises(KeyError, miscellaneous.nested_dict_item, d, {"1": 1})
        self.assertRaises(TypeError, miscellaneous.nested_dict_item, d, (1, 2, 3, 4, 5))
        self.assertRaises(TypeError, miscellaneous.nested_dict_item, None, (1,))

    def test_nest_object(self):
        self.assertEqual(miscellaneous.nest_object((), None), None)
        self.assertEqual(miscellaneous.nest_object((), 1), 1)
        self.assertEqual(miscellaneous.nest_object((1,), 1), {1: 1})
        self.assertEqual(miscellaneous.nest_object((1, 2), 1), {1: {2: 1}})
        self.assertEqual(
            miscellaneous.nest_object((1, 1, 1), None), {1: {1: {1: None}}}
        )
        self.assertEqual(miscellaneous.nest_object((1, 2, "3"), 1), {1: {2: {"3": 1}}})
        self.assertEqual(
            miscellaneous.nest_object([1, 2, "3"], [1]), {1: {2: {"3": [1]}}}
        )
        self.assertEqual(
            miscellaneous.nest_object(tuple({1: 2, 2: 2, "2": 2}), [1]),
            {1: {2: {"2": [1]}}},
        )
        self.assertRaises(TypeError, miscellaneous.nest_object, None, None)

    def test_merge_dicts(self):
        d0 = {1: 2}
        d1 = {2: 3, 3: 4}
        d2 = {1: 2, 2: 3, 3: 4}
        d3 = {2: 5, 4: 5}
        d13jl = {2: [3, 5], 3: 4, 4: 5}
        d13jt = {k: tuple(v) if isinstance(v, list) else v for k, v in d13jl.items()}
        d13d = {3: 4, 4: 5}
        d13l = {2: 3, 3: 4, 4: 5}
        d13r = {2: 5, 3: 4, 4: 5}
        self.assertEqual(miscellaneous.merge_dicts({}, {}), {})
        self.assertEqual(miscellaneous.merge_dicts(d0, {}), d0)
        self.assertEqual(miscellaneous.merge_dicts({}, d0), d0)
        self.assertEqual(miscellaneous.merge_dicts(d0, d1), d2)
        self.assertEqual(miscellaneous.merge_dicts(d1, d0), d2)
        funcs = (lambda arg: arg, lambda arg: {1: arg}, lambda arg: {1: {2: arg}})
        for func in funcs:
            self.assertEqual(miscellaneous.merge_dicts(func(d1), func(d3)), func(d13jl))
            self.assertEqual(
                miscellaneous.merge_dicts(func(d3), func(d1)),
                func(
                    {k: v[::-1] if isinstance(v, list) else v for k, v in d13jl.items()}
                ),
            )
            pol = miscellaneous.DictMergeOverlapPolicy.JOIN_LIST
            self.assertEqual(
                miscellaneous.merge_dicts(func(d1), func(d3), overlap_policy=pol),
                func(d13jl),
            )
            self.assertEqual(
                miscellaneous.merge_dicts(func(d3), func(d1), overlap_policy=pol),
                func(
                    {k: v[::-1] if isinstance(v, list) else v for k, v in d13jl.items()}
                ),
            )
            pol = miscellaneous.DictMergeOverlapPolicy.JOIN_TUPLE
            self.assertEqual(
                miscellaneous.merge_dicts(func(d1), func(d3), overlap_policy=pol),
                func(d13jt),
            )
            self.assertEqual(
                miscellaneous.merge_dicts(func(d3), func(d1), overlap_policy=pol),
                func(
                    {
                        k: v[::-1] if isinstance(v, tuple) else v
                        for k, v in d13jt.items()
                    }
                ),
            )
            pol = miscellaneous.DictMergeOverlapPolicy.DELETE
            self.assertEqual(
                miscellaneous.merge_dicts(func(d1), func(d3), overlap_policy=pol),
                func(d13d),
            )
            self.assertEqual(
                miscellaneous.merge_dicts(func(d3), func(d1), overlap_policy=pol),
                func(d13d),
            )
            pol = miscellaneous.DictMergeOverlapPolicy.LEFT
            self.assertEqual(
                miscellaneous.merge_dicts(func(d1), func(d3), overlap_policy=pol),
                func(d13l),
            )
            self.assertEqual(
                miscellaneous.merge_dicts(func(d3), func(d1), overlap_policy=pol),
                func(d13r),
            )
            pol = miscellaneous.DictMergeOverlapPolicy.RIGHT
            self.assertEqual(
                miscellaneous.merge_dicts(func(d1), func(d3), overlap_policy=pol),
                func(d13r),
            )
            self.assertEqual(
                miscellaneous.merge_dicts(func(d3), func(d1), overlap_policy=pol),
                func(d13l),
            )
        self.assertRaises(TypeError, miscellaneous.merge_dicts, d0, None)
        self.assertRaises(TypeError, miscellaneous.merge_dicts, [], d0)
