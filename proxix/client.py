from typing import IO, Any, Dict, Generic, Optional, Type

from six import text_type

from .channel import Channel
from .communicator import Communicator
from .format import B, Format
from .generics import D
from .proxy_manager import ProxyManager
from .serializer import Serializer


class Client(Generic[D]):
    def __init__(self, communicator, serializer, format_cls, buffer_factory):
        # type: (Communicator[D], Serializer[D], Type[Format[B]], Type[IO[D]]) -> None
        self.channel = Channel(
            communicator=communicator,
            serializer=serializer,
            format_cls=format_cls,
            buffer_factory=buffer_factory,
            proxy_manager=ProxyManager(),
        )  # type: Channel[D]

    def eval(self, source, globals=None, locals=None):
        # type: (text_type, Optional[Dict[str, Any]], Optional[Dict[str, Any]]) -> Any
        return self.channel.dispatcher.eval(source, globals, locals)

    def module(self, name):
        # type: (text_type) -> Any
        return self.channel.dispatcher.import_module(name)
