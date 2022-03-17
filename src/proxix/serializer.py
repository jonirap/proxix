from abc import ABCMeta, abstractmethod
from builtins import bytes, str
from io import BytesIO, StringIO
from typing import IO, Any, Generic

from six import with_metaclass

from .generics import D


class Serializer(with_metaclass(ABCMeta, Generic[D])):
    @abstractmethod
    def load(self, fd):
        # type: (IO[D]) -> Any
        pass

    @abstractmethod
    def loads(self, data):
        # type: (D) -> Any
        pass

    @abstractmethod
    def dump(self, obj, fd):
        # type: (Any, IO[D]) -> int
        pass

    @abstractmethod
    def dumps(self, obj):
        # type: (Any) -> D
        pass


class BinarySerializer(with_metaclass(ABCMeta, Serializer[bytes])):
    def loads(self, data):
        # type: (bytes) -> Any
        return self.load(BytesIO(data))

    @abstractmethod
    def dumps(self, obj):
        # type: (Any) -> bytes
        fd = BytesIO()
        self.dump(obj, fd)
        return fd.getvalue()


class TextSerializer(with_metaclass(ABCMeta, Serializer[str])):
    def loads(self, data):
        # type: (str) -> Any
        return self.load(StringIO(data))

    @abstractmethod
    def dumps(self, obj):
        # type: (Any) -> str
        fd = StringIO()
        self.dump(obj, fd)
        return fd.getvalue()
