""" Test utilities
"""
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=invalid-name,no-self-use

# standard
import os
import unittest
import tempfile
import json

# internal
from .. import serializers


TEST_CASE_DICT_BASIC_TYPES = {
    "hello": "world",
    "other": 1,
    "variable": 3.2443,
    "bool": True,
    "none": None,
    "nested": {
        "other": "nest",
    },
    "list": [
        1,
        2,
        "list",
    ],
}


class SerializerMixin:
    def test_dump_load(self, expected=None):
        serializer = self.serializer
        expected = expected or TEST_CASE_DICT_BASIC_TYPES
        actual_bytes = serializer.dump(expected)
        self.assertIsInstance(actual_bytes, str)
        actual = serializer.load(actual_bytes)
        self.assertEqual(expected, actual)

    def test_dump_load_buffer(self, expected=None):
        serializer = self.serializer
        expected = expected or TEST_CASE_DICT_BASIC_TYPES

        write_mode = "wb" if serializer.uses_bytes_stream else "w"
        read_mode = "rb" if serializer.uses_bytes_stream else "r"

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, f"test_dump_load_buffer.{serializer.ext}")
            with open(filepath, mode=write_mode) as buffer:
                serializer.dump(expected, buffer)
            with open(filepath, mode=read_mode) as buffer:
                actual = serializer.load(buffer)

        self.assertEqual(actual, expected)

    def test_dump_load_filepath(self, expected=None):
        serializer = self.serializer
        expected = expected or TEST_CASE_DICT_BASIC_TYPES
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, f"test_dump_load_filepath.{serializer.ext}")
            serializer.dump(expected, filepath)
            actual = serializer.load(filepath)
        self.assertEqual(actual, expected)

    def test_dump_load_bytes(self, expected=None):
        serializer = self.serializer
        expected = expected or TEST_CASE_DICT_BASIC_TYPES
        actual_bytes = serializer.dumpb(expected)
        self.assertIsInstance(actual_bytes, bytes)
        actual = serializer.loadb(actual_bytes)
        self.assertEqual(expected, actual)

    def test_dump_load_bytes_buffer(self, expected=None):
        serializer = self.serializer
        expected = expected or TEST_CASE_DICT_BASIC_TYPES

        write_mode = "wb" if serializer.uses_bytes_stream else "w"
        read_mode = "rb" if serializer.uses_bytes_stream else "r"

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(
                tmpdir, f"test_dump_load_bytes_buffer.{serializer.ext}"
            )
            with open(filepath, mode=write_mode) as buffer:
                serializer.dumpb(expected, buffer)
            with open(filepath, mode=read_mode) as buffer:
                actual = serializer.loadb(buffer)
        self.assertEqual(actual, expected)

    def test_dump_load_bytes_filepath(self, expected=None):
        serializer = self.serializer
        expected = expected or TEST_CASE_DICT_BASIC_TYPES
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(
                tmpdir, f"test_dump_load_bytes_filepath.{serializer.ext}"
            )
            serializer.dumpb(expected, filepath)
            actual = serializer.loadb(filepath)
            self.assertEqual(actual, expected)


class TestSerializerJson(SerializerMixin, unittest.TestCase):
    serializer = serializers.json_basic


class TestSerializerJsonPlus(SerializerMixin, unittest.TestCase):
    serializer = serializers.json


class TestSerializerYaml(SerializerMixin, unittest.TestCase):
    serializer = serializers.yaml


class TestSerializerGeneral(SerializerMixin, unittest.TestCase):
    def setUp(self):
        self.serializer = serializers.Serializer(
            load=json.load,
            dump=json.dump,
        )
