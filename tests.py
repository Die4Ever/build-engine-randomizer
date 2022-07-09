from BuildLibs.grp import *
import BuildLibs.gui
import cProfile, pstats
import unittest

class BaseTestCase(unittest.TestCase):
    def test_example(self):
        self.assertEqual(1, 1, 'placeholder test')

def runtests():
    unittest.main(verbosity=9, warnings="error")#, failfast=True)

cProfile.run("runtests()", sort="cumtime")
