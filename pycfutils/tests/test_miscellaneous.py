import contextlib
import datetime
import operator
import os
import pathlib
import random
import shutil
import time
import unittest
from io import StringIO
from unittest import mock

from pycfutils import miscellaneous


class MiscellaneousTestCase(unittest.TestCase):
    def setUp(self):
        self.this_file = str(pathlib.Path(__file__).absolute())
        self.test_dir = pathlib.Path("test_dir")
        self.test_dir_file_texts = [b"00", b"111", b"2222", b"33333"]
        shutil.rmtree(self.test_dir, ignore_errors=True)
        self.test_dir.mkdir(parents=True, exist_ok=True)
        f00 = self.test_dir / ".00.txt"
        f00.touch()
        (self.test_dir / f"sl_{f00.parts[-1]}").symlink_to(f00.absolute())
        with f00.open(mode="wb") as f:
            f.write(self.test_dir_file_texts[0])
        d00 = self.test_dir / "00"
        d00.mkdir(parents=True, exist_ok=True)
        (d00 / "sl_00_self").symlink_to(".", target_is_directory=True)
        d0100 = self.test_dir / "01" / "00"
        (d0100 / "00").mkdir(parents=True, exist_ok=True)
        f010000 = d0100 / "00.txt"
        f010000.touch()
        with f010000.open(mode="wb") as f:
            f.write(self.test_dir_file_texts[1])
        d0200 = self.test_dir / "02" / "00"
        d0200.mkdir(parents=True, exist_ok=True)
        f020000 = d0200 / "00.txt"
        f020000.touch()
        with f020000.open(mode="wb") as f:
            f.write(self.test_dir_file_texts[2])
        f020001 = d0200 / "01.txt"
        f020001.touch()
        with f020001.open(mode="wb") as f:
            f.write(self.test_dir_file_texts[3])
        # Files and dirs under test_dir (included)
        self.test_dir_dir_count = 8
        self.test_dir_file_count = len(self.test_dir_file_texts) + 1

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

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
        us = (7890,)
        self.assertEqual(
            miscellaneous.timestamp_string(timestamp=ts, human_readable=False),
            "20240506123456",
        )
        self.assertEqual(
            miscellaneous.timestamp_string(
                timestamp=ts + us, human_readable=False, microseconds=True
            ),
            "20240506123456007890",
        )
        self.assertEqual(
            miscellaneous.timestamp_string(timestamp=ts, human_readable=True),
            "2024-05-06 12:34:56",
        )
        self.assertEqual(
            miscellaneous.timestamp_string(
                timestamp=ts + us,
                human_readable=True,
                microseconds=True,
            ),
            "2024-05-06 12:34:56.007890",
        )
        self.assertEqual(
            miscellaneous.timestamp_string(
                timestamp=ts,
                human_readable=False,
                local=True,
            ),
            "20240506123456",
        )
        self.assertEqual(
            miscellaneous.timestamp_string(
                timestamp=ts + us,
                human_readable=True,
                separator="T",
                microseconds=True,
                timezone=True,
            ),
            "2024-05-06T12:34:56.007890+00:00",
        )
        self.assertEqual(
            miscellaneous.timestamp_string(
                timestamp=datetime.datetime(*ts),
                human_readable=False,
                local=True,
            ),
            "20240506123456",
        )
        ts = 1762981433.405951  # 2025 11 12 21 03 53 405951 GMT
        self.assertEqual(
            miscellaneous.timestamp_string(
                timestamp=ts,
                human_readable=False,
                local=False,
            ),
            "20251112210353",
        )
        self.assertEqual(
            miscellaneous.timestamp_string(
                timestamp=ts,
                human_readable=False,
                microseconds=True,
                local=False,
            ),
            "20251112210353405951",
        )
        self.assertEqual(
            miscellaneous.timestamp_string(
                timestamp=int(ts),
                human_readable=False,
                microseconds=True,
                local=False,
            ),
            "20251112210353000000",
        )
        self.assertEqual(
            miscellaneous.timestamp_string(
                timestamp=str(int(ts)),
                human_readable=False,
                microseconds=True,
                local=False,
                convert_function=lambda arg, *args: datetime.datetime.fromtimestamp(
                    int(arg, args[0]),
                    tz=args[1],
                ),
                convert_function_extra_args=(10, datetime.timezone.utc),
            ),
            "20251112210353000000",
        )
        ts = datetime.datetime.now()
        self.assertEqual(
            miscellaneous.timestamp_string(
                timestamp=ts,
                separator="T",
                human_readable=True,
                microseconds=True,
                local=True,
            ),
            ts.isoformat(),
        )
        ts = time.time()
        if time.gmtime(ts) == time.localtime(ts):
            self.assertEqual(
                miscellaneous.timestamp_string(
                    timestamp=ts,
                    human_readable=False,
                    local=False,
                ),
                miscellaneous.timestamp_string(
                    timestamp=ts,
                    human_readable=False,
                    local=True,
                ),
            )
        else:
            self.assertNotEqual(
                miscellaneous.timestamp_string(
                    timestamp=ts,
                    human_readable=False,
                    local=False,
                ),
                miscellaneous.timestamp_string(
                    timestamp=ts,
                    human_readable=False,
                    local=True,
                ),
            )
        self.assertTrue(miscellaneous.timestamp_string(datetime.datetime.now()))

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

    def test_randomize(self):
        v = random.uniform(-100, 100)
        self.assertEqual(
            miscellaneous.randomize(
                v, left_deviation_percent=-10, right_deviation_percent=0
            ),
            v,
        )
        for d in (None, 0, 1, 2, 3, 4, 6, -1, -2):
            self.assertEqual(
                miscellaneous.randomize(
                    v,
                    left_deviation_percent=-10,
                    right_deviation_percent=0,
                    round_result=True,
                    round_digits=d,
                ),
                round(v, ndigits=d),
            )
        lol = 1
        hil = 500
        for lop, hip in (
            (random.randint(lol, hil), random.randint(lol, hil)),
            (random.randint(lol, hil), 0),
            (0, random.randint(lol, hil)),
        ):
            self.assertTrue(
                isinstance(
                    miscellaneous.randomize(
                        v,
                        left_deviation_percent=lop,
                        right_deviation_percent=hip,
                        round_result=True,
                        round_digits=None,
                    ),
                    int,
                )
            )
            lo = v - abs(v) * lop / 100
            hi = v + abs(v) * hip / 100
            # print(lop, hip, v, lo, hi)
            vs = []
            for _ in range(500):
                vs.append(
                    miscellaneous.randomize(
                        v, left_deviation_percent=lop, right_deviation_percent=hip
                    )
                )
                self.assertGreaterEqual(vs[-1], lo)
                self.assertLessEqual(vs[-1], hi)
            lovp = len([e for e in vs if e < v]) / len(vs)
            hivp = len([e for e in vs if e > v]) / len(vs)
            # print(len([e for e in vs if e < v]), len([e for e in vs if e > v]))
            # print(lovp, hivp)
            p = 1
            self.assertAlmostEqual(hip / (lop + hip), hivp, places=p)
            self.assertAlmostEqual(lop / (lop + hip), lovp, places=p)

    def test_call_stack_whoami(self):
        this = miscellaneous.whoami(depth=0)
        self.assertEqual(self.this_file, this[0])
        stack1 = miscellaneous.call_stack(depth=0, max_levels=1)
        stack = miscellaneous.call_stack(depth=0, max_levels=0)
        self.assertGreater(len(stack), len(stack1))
        self.assertEqual(stack[-1], (stack1[-1][0], stack1[-1][1] + 1) + stack1[-1][2:])
        self.assertEqual(self.this_file, stack[-1][0])

    def test_process_items_in_path(self):

        def exc_none(e):
            print(e)

        def exc_raise(e):
            print(e)
            raise e

        def exc_raise_ni(e):
            raise NotImplementedError(e)

        def proc_raise_ni(path):
            raise NotImplementedError(proc_raise_ni.__name__)

        def proc_raise_ni_kwarg(path, processor=None):
            if processor is None:
                raise NotImplementedError(proc_raise_ni_kwarg.__name__)

        def proc_args(file_list, misleading_arg_name, dummy_kwarg=None):
            if dummy_kwarg is None:
                raise NotImplementedError(proc_args.__name__)
            file_list.append(misleading_arg_name)

        def flt_proc_raise_ni(path):
            raise NotImplementedError(flt_proc_raise_ni.__name__)

        def flt_trav_raise_ni_noarg(path):
            raise NotImplementedError(flt_trav_raise_ni_noarg.__name__)

        def flt_trav_raise_ni(path, level):
            raise NotImplementedError(flt_trav_raise_ni.__name__)

        pinv = pathlib.Path(str(self.test_dir) + "invalid")
        res = tuple(
            miscellaneous.process_path_items(
                path=pinv,
                processor=lambda arg: None,
            )
        )
        self.assertEqual(res, ())
        res = tuple(
            miscellaneous.process_path_items(
                path=pinv,
                processor=lambda arg: None,
                exception_handler=exc_none,
            )
        )
        self.assertEqual(res, ())
        res = miscellaneous.process_path_items(
            path=pinv,
            processor=lambda arg: None,
            exception_handler=exc_raise,
        )
        with self.assertRaises(OSError):
            tuple(res)
        res = miscellaneous.process_path_items(
            path=pinv,
            processor=lambda arg: None,
            exception_handler=exc_raise_ni,
        )
        with self.assertRaises(NotImplementedError):
            tuple(res)
        res = miscellaneous.process_path_items(
            path=self.test_dir,
            processor=proc_raise_ni,
            exception_handler=exc_raise,
        )
        with self.assertRaises(NotImplementedError):
            tuple(res)
        res = miscellaneous.process_path_items(
            path=self.test_dir,
            processor=lambda arg: None,
            processing_filter=flt_proc_raise_ni,
            exception_handler=exc_raise,
        )
        with self.assertRaises(NotImplementedError):
            tuple(res)
        res = miscellaneous.process_path_items(
            path=self.test_dir,
            processor=lambda arg: None,
            traversing_filter=flt_trav_raise_ni_noarg,
            exception_handler=exc_raise,
        )
        with self.assertRaises(TypeError):
            tuple(res)
        res = miscellaneous.process_path_items(
            path=self.test_dir,
            processor=lambda arg: None,
            traversing_filter=flt_trav_raise_ni,
            exception_handler=exc_raise,
        )
        with self.assertRaises(NotImplementedError):
            tuple(res)
        res = miscellaneous.process_path_items(
            path=self.test_dir,
            processor=proc_raise_ni_kwarg,
            exception_handler=exc_raise,
        )
        with self.assertRaises(NotImplementedError):
            tuple(res)
        res = miscellaneous.process_path_items(
            path=self.test_dir,
            processor=lambda arg: None,
            processor_path_argument_target="notexisting",
            exception_handler=exc_raise,
        )
        with self.assertRaises(ValueError):
            tuple(res)
        res = miscellaneous.process_path_items(
            path=self.test_dir,
            processor=lambda arg: None,
            processor_path_argument_target=1000,
            exception_handler=exc_raise,
        )
        with self.assertRaises(IndexError):
            tuple(res)
        res = miscellaneous.process_path_items(
            path=self.test_dir,
            processor=lambda arg: None,
            processor_path_argument_target=("Invalid type",),
            exception_handler=exc_raise,
        )
        with self.assertRaises(TypeError):
            tuple(res)
        res = miscellaneous.process_path_items(
            path=self.test_dir,
            processor=lambda: None,
            exception_handler=exc_raise,
        )
        with self.assertRaises(TypeError):
            tuple(res)
        res = miscellaneous.process_path_items(
            path=self.test_dir,
            processor=proc_args,
            processor_path_argument_target="misleading_arg_name",
            exception_handler=exc_raise,
        )
        with self.assertRaises(TypeError):
            tuple(res)
        items = []
        res = miscellaneous.process_path_items(
            path=self.test_dir,
            processor=proc_args,
            processor_path_argument_target="misleading_arg_name",
            exception_handler=exc_raise,
            file_list=items,
        )
        with self.assertRaises(NotImplementedError):
            tuple(res)
        items = []
        # Can't use *args here
        res = miscellaneous.process_path_items(
            self.test_dir,
            proc_args,
            items,
            "Not None",
            processor_path_argument_target="misleading_arg_name",
            exception_handler=exc_raise,
        )
        with self.assertRaises(TypeError):
            tuple(res)
        items = []
        res = tuple(
            miscellaneous.process_path_items(
                path=self.test_dir,
                processor=proc_args,
                processor_path_argument_target="misleading_arg_name",
                exception_handler=exc_raise,
                file_list=items,
                dummy_kwarg="Not None",
            )
        )
        item_count = self.test_dir_dir_count + self.test_dir_file_count
        self.assertEqual(len(items), item_count)
        self.assertEqual(len(items), len(res))
        items = []
        res = tuple(
            miscellaneous.process_path_items(
                path=self.test_dir,
                processor=proc_args,
                processor_path_argument_target=1,
                exception_handler=exc_raise,
                file_list=items,
                dummy_kwarg="Not None",
            )
        )
        self.assertEqual(len(items), item_count)
        self.assertEqual(len(items), len(res))
        res = tuple(
            miscellaneous.process_path_items(
                path=self.test_dir,
                processor=lambda arg: None,
                exception_handler=exc_raise,
            )
        )
        self.assertEqual(item_count, len(res))
        res = tuple(
            miscellaneous.process_path_items(
                path=str(self.test_dir),
                processor=lambda arg: None,
                exception_handler=exc_raise,
            )
        )
        self.assertEqual(item_count, len(res))
        res = tuple(
            miscellaneous.process_path_items(
                path=self.test_dir,
                processor=lambda arg: None,
                processing_filter=lambda arg: arg.is_dir(),
                exception_handler=exc_raise,
            )
        )
        self.assertEqual(self.test_dir_dir_count, len(res))
        res = tuple(
            miscellaneous.process_path_items(
                path=self.test_dir,
                processor=lambda arg: None,
                processing_filter=lambda arg: arg.is_file(),
                exception_handler=exc_raise,
            )
        )
        self.assertEqual(self.test_dir_file_count, len(res))
        res = tuple(
            miscellaneous.process_path_items(
                path=self.test_dir,
                processor=lambda arg: None,
                traversing_filter=lambda arg0, arg1: arg1 < 1,
                exception_handler=exc_raise,
            )
        )
        self.assertEqual(1, len(res))
        res = tuple(
            miscellaneous.process_path_items(
                path=self.test_dir,
                processor=lambda arg: None,
                processing_filter=lambda arg: arg.is_file(),
                traversing_filter=lambda arg0, arg1: arg1 < 2,
                exception_handler=exc_raise,
            )
        )
        self.assertEqual(2, len(res))
        res = tuple(
            miscellaneous.process_path_items(
                path=self.test_dir,
                processor=lambda arg: None,
                processing_filter=lambda arg: arg.is_dir(),
                traversing_filter=lambda arg0, arg1: not arg0.is_symlink() and arg1 < 3,
                exception_handler=exc_raise,
            )
        )
        self.assertEqual(7, len(res))
        res = tuple(
            miscellaneous.process_path_items(
                path=self.test_dir,
                processor=lambda arg: os.stat(arg).st_size,
                processing_filter=lambda arg: arg.is_file(),
                exception_handler=exc_raise,
            )
        )
        self.assertEqual(
            sum(e[1] for e in res),
            sum(len(e) for e in self.test_dir_file_texts)
            + len(self.test_dir_file_texts[0]),
        )
        if 0:
            # No recursion error ???
            res = tuple(
                miscellaneous.process_path_items(
                    path=self.test_dir,
                    processor=lambda arg: None,
                    processing_filter=lambda arg: arg.is_dir(),
                    traversing_filter=lambda arg0, arg1: True,
                    exception_handler=exc_raise,
                )
            )
            print(res, len(res))

            p = os.path.abspath(max((e[0] for e in res), key=len))
            print(len(p), len(p.split("\\")))
