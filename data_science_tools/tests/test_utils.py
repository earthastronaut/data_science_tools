""" Test utilities
"""
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=invalid-name,no-self-use
import unittest

from data_science_tools import utils


class TestDotDict(unittest.TestCase):
    def test_set_attribute(self):
        d = utils.DotDict()
        d.hello = "world"
        self.assertEqual(d, {"hello": "world"})
        self.assertTrue("hello" in d)
        self.assertEqual(d["hello"], "world")

    def test_set_item(self):
        d = utils.DotDict()
        d["hello"] = "world"
        self.assertTrue(hasattr(d, "hello"))
        self.assertEqual(d.__dict__, {"hello": "world"})
        self.assertEqual(d.hello, "world")

    def test_del_attribute(self):
        d = utils.DotDict()
        d.hello = "world"
        self.assertEqual(d, {"hello": "world"})

        del d.hello
        self.assertEqual(d, {})
        self.assertEqual(d.__dict__, {})
        self.assertFalse(hasattr(d, "hello"))

    def test_del_item(self):
        d = utils.DotDict()
        d.hello = "world"
        self.assertEqual(d, {"hello": "world"})

        del d["hello"]
        self.assertEqual(d, {})
        self.assertEqual(d.__dict__, {})
        self.assertFalse(hasattr(d, "hello"))
