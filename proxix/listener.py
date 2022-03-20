from abc import ABCMeta, abstractmethod
from typing import Generator, Generic, Type

from six import add_metaclass

from .communicator import Communicator
from .generics import D


@add_metaclass(ABCMeta)
class Listener(Generic[D]):
    @abstractmethod
    def listen(self):
        # type: () -> Generator[Communicator[D], None, None]
        pass

    @property
    @abstractmethod
    def communicator_cls(cls):
        # type: () -> Type[Communicator[D]]
        pass
