""" Unit tests for quantize

Quantize was written as a stand along python file so it's tests are
self contained within that file. They're added here for package testing.
"""
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=invalid-name,no-self-use

from data_science_tools.quantize import QuantizeTest

if __name__ == "__main__":
    test = QuantizeTest()
    test.run()
