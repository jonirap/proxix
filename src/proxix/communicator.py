from abc import ABCMeta, abstractmethod
from typing import IO, Generator, Generic, Tuple

from six import with_metaclass

from .generics import D


class Communicator(with_metaclass(ABCMeta, Generic[D])):
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
