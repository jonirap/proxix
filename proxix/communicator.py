from abc import ABCMeta, abstractmethod
from typing import IO, Generator, Generic, Tuple

from six import add_metaclass

from .generics import D


@add_metaclass(ABCMeta)
class Communicator(Generic[D]):
    @abstractmethod
    def send(self, fd, length):
        # type: (IO[D], int) -> Generator[IO[D], Tuple[IO[D], int], None]
        pass

    @abstractmethod
    def receive(self):
        # type: () -> Generator[IO[D], Tuple[IO[D], int], None]
        pass


BinaryCommunicator = Communicator[bytes]
TextCommunicator = Communicator[str]
