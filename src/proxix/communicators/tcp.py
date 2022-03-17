import socket
import struct
from io import BytesIO
from typing import IO, BinaryIO, Generator, Tuple, Type

from ..communicator import BinaryCommunicator


class TCPCommunicator(BinaryCommunicator):
    def __init__(self, sock, internal_buffer_size=4096, buffer_factory=BytesIO):
        # type: (socket.socket, int, Type[IO[bytes]]) -> None
        self.sock = sock
        self.internal_buffer_size = internal_buffer_size
        self.buffer_factory = buffer_factory

    @classmethod
    def connect(cls, host, port=2611):
        # type: (str, int) -> TCPCommunicator
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return cls(s)

    def send(self, fd, length):
        # type: (IO[bytes], int) -> Generator[IO[bytes], Tuple[IO[bytes], int], None]
        while True:
            assert isinstance(fd, BinaryIO)
            recv_buffer = self.buffer_factory()
            self.sock.sendall(struct.pack(u"I", length))
            self.sock.sendfile(fd)
            response_length = struct.unpack(u"I", self.sock.recv(4))[0]
            while response_length > 0:
                cur_len = min(response_length, self.internal_buffer_size)
                recv_buffer.write(self.sock.recv(cur_len))
                response_length -= cur_len
            ret = yield recv_buffer
            if ret is None:
                break
            fd, length = ret

    def receive(self):
        # type: () -> Generator[IO[bytes], Tuple[IO[bytes], int], None]
        while True:
            recv_buffer = self.buffer_factory()
            request_length = struct.unpack(u"I", self.sock.recv(4))[0]
            while request_length > 0:
                cur_len = min(request_length, self.internal_buffer_size)
                recv_buffer.write(self.sock.recv(cur_len))
                request_length -= cur_len
            ret = yield recv_buffer
            if ret is None:
                break
            fd, length = ret
            assert isinstance(fd, BinaryIO)
            self.sock.sendall(struct.pack(u"I", length))
            self.sock.sendfile(fd)
