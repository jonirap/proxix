from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Generic, TypeVar, Union

from six import add_metaclass

from .manager import ProxyManager
from .proxy import Proxy
from .request import Request
from .response import Response


class FormatError(Exception):
    pass


B = TypeVar(u"B")


@add_metaclass(ABCMeta)
class Format(Generic[B]):
    def __init__(self, proxy_manager, proxy_creation_func):
        # type: (ProxyManager, Callable[[int], Proxy]) -> None
        self.proxy_manager = proxy_manager
        self.proxy_creation_func = proxy_creation_func

    @abstractmethod
    def translate_to_builtins(self, obj):
        # type: (Union[Any, Request, Response, Exception]) -> B
        pass

    @abstractmethod
    def translate_from_builtins(self, obj):
        # type: (B) -> Union[Any, Request, Response, Exception]
        pass
