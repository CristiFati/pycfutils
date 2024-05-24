import os
import pathlib
import threading
import time
import unittest

try:
    from psutil import cpu_percent
except ImportError:
    cpu_percent = None

from pycfutils import system


class SystemTestCase(unittest.TestCase):
    def setUp(self):
        self.cd = os.getcwd()
        self.cds = (self.cd, self.cd.encode(), pathlib.Path(self.cd))

    def test_path_ancestor(self):
        for cd in self.cds:
            self.assertEqual(system.path_ancestor(cd, level=1), os.path.dirname(cd))
        self.assertEqual(system.path_ancestor(self.cd, 0), self.cd)
        self.assertEqual(system.path_ancestor(""), "")
        self.assertEqual(system.path_ancestor(os.path.sep, level=3), os.path.sep)
        idx = self.cd.rfind(os.path.sep)
        level = 1
        while True:
            part = self.cd[:idx]
            # print(idx, part, level, system.path_ancestor(self.cd, level))
            if os.path.dirname(part) == part:
                break
            self.assertEqual(system.path_ancestor(self.cd, level), part)
            level += 1
            idx = self.cd.rfind(os.path.sep, 0, idx)

    @staticmethod
    def _cpu_data(duration=1, intervals=5):
        reads = []
        interval = duration / intervals
        for _ in range(intervals):
            reads.append(cpu_percent() / 100)
            time.sleep(interval)
        reads.append(cpu_percent() / 100)
        return sum(reads) / len(reads), max(reads)

    def test_stress_cpu(self):
        if cpu_percent is None:
            return
        duration = 1
        avg, mx = self._cpu_data(duration=duration)
        cnt = os.cpu_count()
        cpu_load = 1 / cnt
        free_cpus = int(cnt * (1 - mx))
        ignore_cpu_count = 1  # Should be 0, but tests fail due to noise
        for cpus in range(1, free_cpus, 2):
            t = threading.Thread(
                target=system.cpu_stress, kwargs={"duration": duration, "count": cpus}
            )
            t.start()
            cpu_avg, _ = self._cpu_data(duration=duration)
            t.join()
            self.assertTrue(cpu_avg >= avg + (cpus - ignore_cpu_count) * cpu_load)
