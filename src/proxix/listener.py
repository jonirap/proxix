from abc import ABCMeta, abstractmethod
from typing import Generator, Generic, Type

from six import with_metaclass

from .communicator import Communicator
from .generics import D


class Listener(with_metaclass(ABCMeta, Generic[D])):
    @abstractmethod
    def listen(self):
        # type: () -> Generator[Communicator[D], None, None]
        pass

    @abstractmethod
    @property
    def communicator_cls(cls):
        # type: () -> Type[Communicator[D]]
        pass
