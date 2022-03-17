from abc import ABCMeta, abstractmethod
from builtins import bytes, str
from typing import Any, Callable, Dict, List, Set, Tuple, Union

from six import with_metaclass

from .manager import ProxyManager
from .proxy import Proxy
from .request import Request
from .response import Response


class FormatError(Exception):
    pass


class Format(with_metaclass(ABCMeta, object)):
    def __init__(self, proxy_manager, proxy_creation_func):
        # type: (ProxyManager, Callable[[int], Proxy]) -> None
        self.proxy_manager = proxy_manager
        self.proxy_creation_func = proxy_creation_func

    @abstractmethod
    def translate_to_builtins(self, obj):
        # type: (Union[Any, Request, Response, Exception]) -> Union[Dict, List, Tuple, Set, int, float, str, bytes]
        pass

    @abstractmethod
    def translate_from_builtins(self, obj):
        # type: (Union[Dict, List, Tuple, Set, int, float, str, bytes]) -> Any
        pass
