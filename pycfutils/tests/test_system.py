import os
import pathlib
import unittest

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
