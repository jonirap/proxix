from typing import BinaryIO, TextIO, Type, Union

from .format import Format
from .listener import Listener
from .manager import ProxyManager
from .processor import Processor
from .serializer import Serializer


class Server(object):
    def __init__(self, listener, serializer_cls, format_cls, buffer_factory=None):
        # type: (Type[Listener], Type[Serializer], Type[Format], Type[Union[TextIO, BinaryIO]]) -> None
        self.proxy_manager = ProxyManager()
        self.processor = Processor(self.proxy_manager)
        self.listener = listener
        self.serializer = serializer_cls
        self.format_cls = format_cls
