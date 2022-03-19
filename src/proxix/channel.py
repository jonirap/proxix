from typing import IO, Any, Generator, Generic, Optional, Tuple, Type, Union

from .communicator import Communicator
from .dispatcher import Dispatcher
from .format import Format
from .generics import D
from .manager import ProxyManager
from .processor import Processor
from .proxy import Proxy
from .request import Request
from .response import Response
from .serializer import Serializer


class Channel(Generic[D]):
    def __init__(
        self,
        communicator,
        serializer_cls,
        format_cls,
        proxy_manager,
        buffer_factory,
    ):
        # type: (Communicator[D], Serializer[D], Type[Format], ProxyManager, Type[IO[D]]) -> None
        self.communicator = communicator  # type: Communicator[D]
        self.serializer_cls = serializer_cls  # type: Serializer[D]
        self.proxy_manager = proxy_manager
        self.buffer_factory = buffer_factory  # type: Type[IO[D]]
        self.processor = Processor(proxy_manager=self.proxy_manager)
        self.dispatcher = Dispatcher(self.send_request)
        self.format = format_cls(
            proxy_manager=self.proxy_manager,
            proxy_creation_func=lambda obj_id: Proxy(self.dispatcher, obj_id=obj_id),
        )
        self._open_channel = (
            None
        )  # type: Optional[Generator[Union[Request, Response], Union[Request, Response], None]]

    def _handle_response(self, response):
        # type: (Union[Request, Response]) -> Response
        if isinstance(response, Request):
            if self._open_channel is None:
                raise EnvironmentError("Bad method call. No open channel")
            return self._handle_response(
                self._open_channel.send(self.processor.handle(response))
            )
        return response

    def send_request(self, request):
        # type: (Request) -> Any
        if not self._open_channel:
            self._open_channel = self._communication_generator(request)
            response = next(self._open_channel)
        else:
            response = self._open_channel.send(request)
        response = self._handle_response(response)
        if response.error is not None:
            raise response.error
        return response.value

    def listen(self):
        # type: () -> Any
        if not self._open_channel:
            self._open_channel = self._communication_generator()
        request = next(self._open_channel)
        while request is not None:
            try:
                assert isinstance(request, Request)
                request = self._open_channel.send(self.processor.handle(request))
            except KeyboardInterrupt:
                break

    def _communication_generator(self, request=None):
        # type: (Optional[Request]) -> Generator[Union[Response, Request], Union[Response, Request], None]
        if request is not None:
            channel = self.communicator.send(
                *self._get_buffer_and_length_from_obj(request)
            )
        else:
            channel = self.communicator.receive()
        data = next(channel)
        while data is not None:
            message = self.format.translate_from_builtins(
                self.serializer_cls.load(data)
            )
            assert isinstance(message, (Request, Response))
            response = yield message
            try:
                data = channel.send(self._get_buffer_and_length_from_obj(response))
            except StopIteration:
                break

    def _get_buffer_and_length_from_obj(self, obj):
        # type: (Any) -> Tuple[IO[D], int]
        buffer = self.buffer_factory()
        size = self.serializer_cls.dump(
            self.format.translate_to_builtins(obj),
            buffer,
        )
        buffer.seek(0)
        return buffer, size
