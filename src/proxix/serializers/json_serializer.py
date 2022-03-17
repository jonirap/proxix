import json
from builtins import str
from typing import IO, Any

from ..serializer import TextSerializer


class JSONSerializer(TextSerializer):
    @classmethod
    def load(cls, fd):
        # type: (IO[str]) -> Any
        return json.load(fd)

    @classmethod
    def dump(cls, obj, fd):
        # type: (Any, IO[str]) -> int
        start = fd.tell()
        json.dump(obj, fd)
        return fd.tell() - start
