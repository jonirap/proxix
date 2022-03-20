import array
import ctypes
import mmap
from builtins import bytes, str
from io import BufferedReader, BufferedWriter, RawIOBase
from typing import IO, Any, Optional

from _typeshed import ReadableBuffer

from ..serializer import BinarySerializer, TextSerializer


class BinaryIOWrapper(RawIOBase):
    def __init__(self, buffer):
        # type: (IO[str]) -> None
        self._buffer = buffer

    def read(self, __size=-1):
        # type: (int) -> Optional[bytes]
        return bytes.fromhex(self._buffer.read(__size))

    def write(self, __b):
        # type: (ReadableBuffer) -> Optional[int]
        if isinstance(__b, ctypes._CData):
            return None
        elif isinstance(__b, (memoryview, array.array)):
            __b = __b.tobytes()
        elif isinstance(__b, mmap.mmap):
            __b = __b.read()
        return self._buffer.write(__b.hex())


class BinaryToTextSerializer(TextSerializer):
    def __init__(self, serializer, buffer_size):
        # type: (BinarySerializer, int) -> None
        self._binary_serializer = serializer
        self._buffer_size = buffer_size

    def load(self, fd):
        # type: (IO[str]) -> Any
        return self._binary_serializer.load(
            BufferedReader(
                BinaryIOWrapper(fd),
                buffer_size=self._buffer_size,
            )
        )

    def dump(self, obj, fd):
        # type: (Any, IO[str]) -> int
        return self._binary_serializer.dump(
            obj,
            BufferedWriter(
                BinaryIOWrapper(fd),
                buffer_size=self._buffer_size,
            ),
        )
