from io import BytesIO, StringIO
from typing import Any, BinaryIO, Generator, Optional, TextIO, Type, Union
from urllib import response

from .communicator import Communicator
from .dispatcher import Dispatcher
from .format import Format
from .manager import ProxyManager
from .processor import Processor
from .proxy import Proxy
from .request import Request
from .response import Response
from .serializer import BinarySerializer, Serializer


class Worker(object):
    def __init__(
        self,
        communicator,
        serializer_cls,
        format_cls,
        proxy_manager,
        buffer_factory=None,
    ):
        # type: (Communicator, Type[Serializer], Type[Format], ProxyManager, Optional[Type[Union[TextIO, BinaryIO]]]) -> None
        self.communicator = communicator
        self.serializer_cls = serializer_cls
        self.proxy_manager = proxy_manager
        self.dispatcher = Dispatcher(self.send_request)
        self.format = format_cls(
            proxy_manager=self.proxy_manager,
            proxy_creation_func=lambda obj_id: Proxy(self.dispatcher, obj_id=obj_id),
        )
        self.processor = Processor(proxy_manager=self.proxy_manager)
        self.buffer_factory = buffer_factory or (
            BytesIO if self.is_binary else StringIO
        )
        self._open_channel = self._communication_generator()

    @property
    def is_binary(self):
        return issubclass(self.serializer_cls, BinarySerializer)

    def _handle_response(self, response):
        # type: (Union[Request, Response]) -> Response
        if isinstance(response, Request):
            return self._handle_response(
                self._open_channel.send(self.processor.handle(response))
            )
        return response

    def send_request(self, request):
        # type: (Request) -> Response
        return self._handle_response(self._open_channel.send(request))

    def start(self):
        # type: (Request) -> Any
        request = next(self._open_channel)
        while request is not None:
            try:
                request = self._open_channel.send(self.processor.handle(response))
            except KeyboardInterrupt:
                break

    def _communication_generator(self):
        # type: () -> Generator[Union[Response, Request], Union[Response, Request], None]
        channel = self.communicator.receive()
        data = next(channel)
        while data is not None:
            response = yield self.format.translate_from_builtins(
                self.serializer_cls.load(data)
            )
            try:
                data = channel.send(self._get_buffer_and_length_from_obj(response))
            except StopIteration:
                break

    def _get_buffer_and_length_from_obj(self, obj):
        # type: (Any) -> Union[TextIO, BinaryIO]
        buffer = self.buffer_factory()
        size = self.serializer_cls.dump(
            self.format.translate_to_builtins(obj),
            buffer,
        )
        buffer.seek(0)
        return buffer, size
