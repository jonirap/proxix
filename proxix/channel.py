from typing import IO, Any, Generator, Generic, Optional, Tuple, Type, Union

from .communicator import Communicator
from .dispatcher import Dispatcher
from .format import B, Format
from .generated_manager import GeneratedManager
from .generics import D
from .processor import Processor
from .proxy import Proxy
from .proxy_manager import ProxyManager
from .request import Request
from .response import Response
from .serializer import Serializer


class IOOperationOnClosedChannel(Exception):
    pass


class Channel(Generic[D]):
    def __init__(
        self,
        communicator,
        serializer,
        format_cls,
        buffer_factory,
        proxy_manager=None,
        generated_manager=None,
    ):
        # type: (Communicator[D], Serializer[D], Type[Format[B]], Type[IO[D]], Optional[ProxyManager], Optional[GeneratedManager]) -> None
        self.communicator = communicator  # type: Communicator[D]
        self.serializer = serializer  # type: Serializer[D]
        self.proxy_manager = proxy_manager or ProxyManager()
        self.generated_manager = generated_manager or GeneratedManager()
        self.buffer_factory = buffer_factory  # type: Type[IO[D]]
        self.processor = Processor(proxy_manager=self.proxy_manager)
        self.dispatcher = Dispatcher(self.send_request)
        self.format = format_cls(
            proxy_manager=self.proxy_manager,
            generated_manager=self.generated_manager,
            dispatcher=self.dispatcher,
        )
        self._open_channel = (
            None
        )  # type: Optional[Generator[Union[Request, Response], Optional[Union[Request, Response]], None]]

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
        print(request.request_type, request.obj_id, request.args, request.kwds)
        created_channel = False  # type: bool
        try:
            if not self._open_channel:
                created_channel = True
                self._open_channel = self._communication_generator(request)
                response = next(self._open_channel)
            else:
                response = self._open_channel.send(request)
        except StopIteration:
            raise IOOperationOnClosedChannel()
        response = self._handle_response(response)
        if created_channel:
            try:
                self._open_channel.send(None)
            except StopIteration:
                pass
            self._open_channel = None
        if response.remote_exception is not None:
            raise response.remote_exception
        if isinstance(response.value, Proxy):
            print("Returned proxy {}".format(response.value))
        return response.value

    def listen(self):
        # type: () -> Any
        is_first = True
        self._open_channel = self._communication_generator()
        request = None
        while request is not None or is_first:
            try:
                if is_first:
                    request = next(self._open_channel)
                    is_first = False
                assert isinstance(request, Request)
                request = self._open_channel.send(self.processor.handle(request))
            except (KeyboardInterrupt, StopIteration):
                try:
                    self._open_channel.send(None)
                except StopIteration:
                    pass
                self._open_channel = None
                break

    def _communication_generator(self, request=None):
        # type: (Optional[Request]) -> Generator[Union[Response, Request], Optional[Union[Response, Request]], None]
        if request is not None:
            channel = self.communicator.send(
                *self._get_buffer_and_length_from_obj(request)
            )
        else:
            channel = self.communicator.receive()
        data = next(channel)
        while data is not None:
            message = self.format.translate_from_builtins(self.serializer.load(data))
            assert isinstance(message, (Request, Response))
            response = yield message
            if response is None:
                break
            try:
                data = channel.send(self._get_buffer_and_length_from_obj(response))
            except StopIteration:
                break

    def _get_buffer_and_length_from_obj(self, obj):
        # type: (Any) -> Tuple[IO[D], int]
        buffer = self.buffer_factory()
        size = self.serializer.dump(
            self.format.translate_to_builtins(obj),
            buffer,
        )
        buffer.seek(0)
        return buffer, size
