from abc import ABCMeta, abstractmethod
from typing import Any, Generic, TypeVar, Union

from six import add_metaclass

from .dispatcher import Dispatcher
from .generated_manager import GeneratedManager
from .proxy_manager import ProxyManager
from .request import Request
from .response import Response


class FormatError(Exception):
    pass


B = TypeVar(u"B")


@add_metaclass(ABCMeta)
class Format(Generic[B]):
    def __init__(self, proxy_manager, generated_manager, dispatcher):
        # type: (ProxyManager, GeneratedManager, Dispatcher) -> None
        self.proxy_manager = proxy_manager
        self.generated_manager = generated_manager
        self.dispatcher = dispatcher

    @abstractmethod
    def translate_to_builtins(self, obj):
        # type: (Union[Any, Request, Response, Exception]) -> B
        pass

    @abstractmethod
    def translate_from_builtins(self, obj):
        # type: (B) -> Union[Any, Request, Response, Exception]
        pass
