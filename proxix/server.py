from abc import ABCMeta, abstractmethod
from typing import IO, Generator, Generic, Type

from six import add_metaclass

from .channel import Channel
from .format import B, Format
from .generics import D
from .listener import Listener
from .proxy_manager import ProxyManager
from .serializer import Serializer


@add_metaclass(ABCMeta)
class Server(Generic[D]):
    def __init__(self, listener, serializer, format_cls, buffer_factory):
        # type: (Listener[D], Serializer[D], Type[Format[B]], Type[IO[D]]) -> None
        self.listener = listener  # type: Listener[D]
        self.serializer = serializer  # type: Serializer[D]
        self.format_cls = format_cls
        self.buffer_factory = buffer_factory  # type: Type[IO[D]]

    def _get_channels(self):
        # type: () -> Generator[Channel[D], None, None]
        for communicator in self.listener.listen():
            yield Channel(
                communicator=communicator,
                serializer=self.serializer,
                format_cls=self.format_cls,
                buffer_factory=self.buffer_factory,
                proxy_manager=ProxyManager(),
            )

    @abstractmethod
    def start(self):
        # type: () -> None
        pass
