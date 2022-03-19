from abc import ABCMeta, abstractmethod
from builtins import bytes, str
from io import BytesIO, StringIO
from typing import IO, Any, Generic

from six import add_metaclass

from .generics import D


@add_metaclass(ABCMeta)
class Serializer(Generic[D]):
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


@add_metaclass(ABCMeta)
class BinarySerializer(Serializer[bytes]):
    def loads(self, data):
        # type: (bytes) -> Any
        return self.load(BytesIO(data))

    def dumps(self, obj):
        # type: (Any) -> bytes
        fd = BytesIO()
        self.dump(obj, fd)
        return fd.getvalue()


@add_metaclass(ABCMeta)
class TextSerializer(Serializer[str]):
    def loads(self, data):
        # type: (str) -> Any
        return self.load(StringIO(data))

    def dumps(self, obj):
        # type: (Any) -> str
        fd = StringIO()
        self.dump(obj, fd)
        return fd.getvalue()
