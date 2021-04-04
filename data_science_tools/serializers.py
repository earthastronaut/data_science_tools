""" Tools for reading and writing
"""
# standard
import abc
from collections import OrderedDict
import decimal
import datetime
import json as pyjson
import logging
import io
import os
import importlib
from typing import Any, Union, IO, Optional, Dict, Callable
import pickle

# external
import numpy as np
import yaml as pyyaml

logger = logging.getLogger(__name__)


Stream = Optional[Union[str, IO]]

__all__ = [
    "json_basic",
    "json",
    "yaml",
    "serializers",
    "Serializer",
    "SerializerJson",
    "SerializerJsonPlus",
    "SerializerYaml",
]


class SerializerBase(abc.ABC):
    """ Abstrack classifier """

    ext = ""
    default_encoding = "utf-8"
    uses_bytes_stream = False
    _default_load_kws = None
    _default_dump_kws = None

    @abc.abstractmethod
    def _load(self, stream: Stream, **kws) -> Any:
        """ _load """

    @abc.abstractmethod
    def _dump(self, obj: Any, stream: Stream, **kws):
        """ _dump """

    def dumpb(self, obj: Any, stream: Stream = None, **kws) -> Optional[bytes]:
        """Dump data bytes.

        Parameters:
            obj: (Any) python object.
            stream:
                None: Return a default streams.
                str: use this as a filename to write to
                buffer: Has "write" method passed to.

        Returns:
            bytes: if no stream is provided
        """
        kwargs = (self._default_dump_kws or {}).copy()
        kwargs.update(kws)

        if stream is None:
            if self.uses_bytes_stream:
                buffer = io.BytesIO()
                self._dump(obj, buffer, **kwargs)
                buffer.seek(0)
                return buffer.read()
            else:
                buffer = io.StringIO()
                encoding = kwargs.pop("encoding", cls.default_encoding)
                self._dump(obj, buffer, **kwargs)
                buffer.seek(0)
                return buffer.read().encode(encoding)
        elif isinstance(stream, str):
            mode = "wb" if self.uses_bytes_stream is None else "w"
            with open(stream, mode=mode) as buffer:
                self._dump(obj, buffer, **kwargs)
        else:
            self._dump(obj, stream, **kwargs)
        return None

    def dump(self, obj: Any, stream: Stream = None, **kws) -> Optional[str]:
        """Dump data.

        Parameters:
            obj: (Any) python object.
            stream:
                None: Return a default streams.
                str: use this as a filename to write to
                buffer: Has "write" method passed to.

        Returns:
            str: if no stream is provided
        """
        kwargs = (self._default_dump_kws or {}).copy()
        kwargs.update(kws)
        if stream is None:
            if self.uses_bytes_stream:
                buffer = io.BytesIO()
                encoding = kwargs.pop("encoding", self.default_encoding)
                self._dump(obj, buffer, **kwargs)
                buffer.seek(0)
                return buffer.read().decode(encoding)
            else:
                buffer = io.StringIO()
                self._dump(obj, buffer, **kwargs)
                buffer.seek(0)
                return buffer.read()
        elif isinstance(stream, str):
            mode = "wb" if self.uses_bytes_stream is None else "w"
            with open(stream, mode=mode) as buffer:
                self._dump(obj, buffer, **kwargs)
        else:
            self._dump(obj, stream, **kwargs)
        return None

    def loadb(self, stream: Stream, **kws) -> Any:
        """ Load data from bytes."""
        kwargs = (self._default_load_kws or {}).copy()
        kwargs.update(kws)

        if isinstance(stream, str):
            # filepath
            mode = "rb" if self.uses_bytes_stream is None else "r"
            with open(stream, mode=mode) as buffer:
                return self._load(buffer, **kwargs)
        elif isinstance(stream, bytes):
            if self.uses_bytes_stream:
                buffer = io.BytesIO(stream)
                return self._load(buffer, **kwargs)
            else:
                encoding = kwargs.pop("encoding", self.default_encoding)
                buffer = io.StringIO(stream.decode(encoding))
                return self._load(buffer, **kwargs)
        else:
            return self._load(stream, **kwargs)

    def load(self, stream: Stream, **kws) -> Any:
        """ Load data from string. """
        kwargs = (self._default_load_kws or {}).copy()
        kwargs.update(kws)

        if isinstance(stream, str):
            # filepath
            if os.path.exists(stream):
                mode = "rb" if self.uses_bytes_stream is None else "r"
                with open(stream, mode=mode) as buffer:
                    return self._load(buffer, **kwargs)
            # directly
            else:
                if self.uses_bytes_stream:
                    encoding = kwargs.pop("encoding", self.default_encoding)
                    buffer = io.BytesIO(stream.encode(encoding))
                    return self._load(buffer, **kwargs)
                else:
                    buffer = io.StringIO(stream)
                    return self._load(buffer, **kwargs)
        else:
            return self._load(stream, **kwargs)


class Serializer(SerializerBase):
    """ Serializer with Callable """

    def __init__(
        self,
        load: Callable = None,
        dump: Callable = None,
        uses_bytes_stream: Optional[bool] = None,
        default_encoding: Optional[str] = None,
        default_dump_kws=None,
        default_load_kws=None,
        ext: Optional[str] = None,
    ):  # pylint: disable=unused-argument
        arguments_with_class_default = (
            ("default_encoding", "default_encoding"),
            ("uses_bytes_stream", "uses_bytes_stream"),
            ("ext", "ext"),
            ("default_dump_kws", "_default_dump_kws"),
            ("default_load_kws", "_default_load_kws"),
        )
        for arg_name, attr_name in arguments_with_class_default:
            value_in = locals()[arg_name]
            if value_in is not None:
                # if provided, overwrite class default
                setattr(self, attr_name, value_in)
    
        

        if self._load is None:
            raise TypeError("serializer must have load method")
        if self._dump is None:
            raise TypeError("serializer must have dump method")


class PlusEncoder(pyjson.JSONEncoder):
    """ Enhanced encoding """

    @staticmethod
    def obj_to_dict(obj: Any, *args, **kws) -> Dict:
        """Generic object serialize"""
        if callable(obj):
            return {
                "__module__": obj.__module__,
                "__name__": obj.__name__,
            }
        else:
            base = {
                "__module__": obj.__class__.__module__,
                "__class__": obj.__class__.__name__,
            }
            if len(args):
                base["args"] = args
            if len(kws):
                base["kws"] = kws
            return base

    @classmethod
    def dict_to_obj(cls, data: Dict) -> Any:
        """ Generic deserialize object """
        module_name = data.get("__module__", None)
        if module_name is None:
            return data
        else:
            module = importlib.import_module(module_name)
            function_name = data.get("__name__", None)
            if function_name is None:
                class_name = data["__class__"]
                args = data.get("args", [])
                kws = data.get("kws", data.get("kwargs", {}))

                for key, value in kws.items():
                    if isinstance(value, dict):
                        kws[key] = cls.dict_to_obj(value)

                for i, value in enumerate(args):
                    if isinstance(value, dict):
                        args[i] = cls.dict_to_obj(value)

                klass = getattr(module, class_name)
                return klass(*args, **kws)
            else:
                return getattr(module, function_name)

    @classmethod
    def to_dict_datetime(cls, obj: datetime.datetime):
        """datetime(year, month, day[, hour[, minute[,
        second[, microsecond[,tzinfo]]]]])"""
        tzinfo = obj.tzinfo
        if tzinfo is not None:
            tzinfo = cls.obj_to_dict(
                tzinfo,
                args=str(tzinfo),
            )
        return cls.obj_to_dict(
            obj,
            year=obj.year,
            month=obj.month,
            day=obj.day,
            hour=obj.hour,
            minute=obj.minute,
            second=obj.second,
            microsecond=obj.microsecond,
            tzinfo=tzinfo,
        )

    @classmethod
    def to_dict_timedelta(cls, obj: datetime.timedelta):
        """datetime(year, month, day[, hour[, minute[,
        second[, microsecond[,tzinfo]]]]])"""
        return cls.obj_to_dict(
            obj,
            seconds=obj.total_seconds(),
        )

    @classmethod
    def to_dict_numpy_ndarray(cls, obj: np.ndarray):
        """ serialize_numpy_ndarray """
        return cls.obj_to_dict(
            obj,
            args=obj.tolist(),
        )

    @classmethod
    def to_dict_numpy_dtype(cls, obj: np.dtype):
        """ serialize_numpy_dtype """
        return cls.obj_to_dict(
            obj,
            args=obj.tolist(),
        )

    @classmethod
    def to_dict_decimal(cls, obj: decimal.Decimal):
        """ serialize_numpy_dtype """
        return cls.obj_to_dict(obj, args=str(obj))

    converters = OrderedDict(
        (
            (datetime.datetime, "to_dict_datetime"),
            (datetime.timedelta, "to_dict_timedelta"),
            (np.ndarray, "to_dict_numpy_ndarray"),
            (np.dtype, "to_dict_numpy_dtype"),
            (decimal.Decimal, "to_dict_decimal"),
        )
    )
    converters_types = tuple(converters.keys())

    @classmethod
    def _super_default(cls, obj):
        return pyjson.JSONEncoder.default(pyjson.JSONEncoder, obj)

    @classmethod
    def default(cls, obj):  # pylint: disable=arguments-differ
        """ Call default """
        if isinstance(obj, cls.converters_types):
            for pytype, to_dict in cls.converters.items():
                if isinstance(obj, pytype):
                    to_dict = getattr(cls, to_dict)
                    return to_dict(obj)
        elif callable(obj):
            return cls.obj_to_dict(obj)
        return cls._super_default(obj)


class SerializerJson(Serializer):
    """ Serialize with json.{dump, load}"""

    ext = "json"
    _load = pyjson.load
    _dump = pyjson.dump
    uses_bytes_stream = False


class SerializerJsonPlus(SerializerJson):
    """Serialize with json.{dump, load}
    with enhancements for particular python classees
    """

    ext = "json"
    _default_load_kws = dict(
        object_hook=PlusEncoder.dict_to_obj,
    )
    _default_dump_kws = dict(
        cls=PlusEncoder,
    )


class SerializerYaml(Serializer):
    """ Serialize with yaml.{safe_dump, safe_load}"""

    ext = "yaml"
    _load = pyyaml.safe_load
    _dump = pyyaml.safe_dump
    uses_bytes_stream = False


serializers = {
    SerializerJsonPlus.ext: SerializerJsonPlus(),
    SerializerYaml.ext: SerializerYaml(),
}


json_basic = SerializerJson()
json = SerializerJsonPlus()
yaml = SerializerYaml()
