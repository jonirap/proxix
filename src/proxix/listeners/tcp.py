import socket
from builtins import bytes
from io import BytesIO
from typing import BinaryIO, Generator, Type

from ..communicators.tcp import TCPCommunicator
from ..listener import Listener


class TCPListener(Listener[bytes]):
    def __init__(self, sock, internal_buffer_size=4096, buffer_factory=BytesIO):
        # type: (socket.socket, int, Type[BinaryIO]) -> None
        self.sock = sock
        self.internal_buffer_size = internal_buffer_size
        self.buffer_factory = buffer_factory

    @classmethod
    def create(cls, host, port=2611):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen()
        return cls(s)

    @property
    def communicator_cls(self):
        # type: () -> Type[TCPCommunicator]
        return TCPCommunicator

    def listen(self):
        # type: () -> Generator[TCPCommunicator, None, None]
        while True:
            try:
                client_sock, _ = self.sock.accept()
                yield self.communicator_cls(
                    client_sock,
                    internal_buffer_size=self.internal_buffer_size,
                    buffer_factory=self.buffer_factory,
                )
            except KeyboardInterrupt:
                break
