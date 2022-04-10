import socket
import struct
from io import BytesIO
from typing import IO, Generator, Tuple, Type

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
            self.sock.sendall(struct.pack(u"I", length))
            self.sock.sendfile(fd)  # type: ignore
            response_length = struct.unpack(u"I", self.sock.recv(4))[0]
            ret = yield self._write_into_buffer(response_length)
            if ret is None:
                break
            fd, length = ret

    def _write_into_buffer(self, length):
        # type: (int) -> IO[bytes]
        recv_buffer = self.buffer_factory()
        start = recv_buffer.tell()
        while length > 0:
            cur_len = min(length, self.internal_buffer_size)
            recv_buffer.write(self.sock.recv(cur_len))
            recv_buffer.flush()
            length -= cur_len
        recv_buffer.seek(start)
        return recv_buffer

    def receive(self):
        # type: () -> Generator[IO[bytes], Tuple[IO[bytes], int], None]
        while True:
            try:
                request_length = struct.unpack(u"I", self.sock.recv(4))[0]
            except struct.error:
                break
            ret = yield self._write_into_buffer(request_length)
            if ret is None:
                break
            fd, length = ret
            self.sock.sendall(struct.pack(u"I", length))
            self.sock.sendfile(fd)  # type: ignore
