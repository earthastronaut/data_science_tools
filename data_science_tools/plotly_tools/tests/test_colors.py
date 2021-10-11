# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=reimported
# pylint: disable=missing-class-docstring
# pylitn: disable=no-self-use

# standard
import unittest

# relative
from .._colors import (
    format_color,
    format_colors,
)


class TestFormatColor(unittest.TestCase):
    def test_format_color(self):
        """Test default inference"""
        expected = "rgba(192,192,192,1)"
        actual = format_color((192, 192, 192))
        self.assertEqual(actual, expected)

        actual = format_color("#C0C0C0")
        self.assertEqual(actual, expected)

        actual = format_color("silver")
        self.assertEqual(actual, expected)

    def test_format_color_with_default_alpha(self):
        """Test default inference with an alpha included"""
        expected = "rgba(192,192,192,0.5)"
        actual = format_color((192, 192, 192, 0.5))
        self.assertEqual(actual, expected)

        actual = format_color("#C0C0C032")
        self.assertEqual(actual, expected)

    def test_format_color_alpha(self):
        """Test default inference force an alpha"""
        expected = "rgba(192,192,192,0.1)"
        actual = format_color((192, 192, 192), alpha=0.1)
        self.assertEqual(actual, expected)

        actual = format_color("#C0C0C0", alpha=0.1)
        self.assertEqual(actual, expected)

        actual = format_color("silver", alpha=0.1)
        self.assertEqual(actual, expected)

        actual = format_color((192, 192, 192, 0.5), alpha=0.1)
        self.assertEqual(actual, expected)

        actual = format_color("#C0C0C032", alpha=0.1)
        self.assertEqual(actual, expected)

    def test_format_colors(self):
        expected = "rgba(192,192,192,0.2)"
        colors = [
            (192, 192, 192),
            "#C0C0C0",
            "silver",
            (192, 192, 192, 0.5),
            "#C0C0C032",
            "rgb(192,192,192)",
            "rgba(192,192,192,0.6334)",
        ]
        for actual in format_colors(colors, alpha=0.2):
            self.assertEqual(actual, expected)
