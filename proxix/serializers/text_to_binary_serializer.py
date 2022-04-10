from builtins import bytes, str
from io import TextIOWrapper
from typing import IO, Any

from ..serializer import BinarySerializer, TextSerializer


class NoCloseTextIOWrapper(TextIOWrapper):
    def close(self):
        # type: () -> None
        pass


class TextToBinarySerializer(BinarySerializer):
    def __init__(self, serializer, encoding=u"utf-8"):
        # type: (TextSerializer, str) -> None
        self._text_serializer = serializer
        self._encoding = encoding

    def load(self, fd):
        # type: (IO[bytes]) -> Any
        return self._text_serializer.load(
            NoCloseTextIOWrapper(fd, encoding=self._encoding)
        )

    def dump(self, obj, fd):
        # type: (Any, IO[bytes]) -> int
        return self._text_serializer.dump(
            obj, NoCloseTextIOWrapper(fd, encoding=self._encoding)
        )
