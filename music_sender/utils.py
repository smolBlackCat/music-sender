"""Utilities module."""

import io
import os


class Communicator:
    """Mixin class responsible for implementing basic socket
    communication tasks like receiving and sending bytes.
    """

    BUFFER_SIZE = 4096

    def __init__(self) -> None:
        pass

    def send(self, message: bytes, sock):
        """Sends bytes to a remote socket."""

        msg_len_header = f"{len(message):<{Communicator.BUFFER_SIZE}}"
        sock.send(msg_len_header.encode())

        buf_msg = io.BytesIO(message)
        while True:
            data = buf_msg.read(Communicator.BUFFER_SIZE)
            if data == b"":
                break
            sock.send(data)

    def recv(self, sock) -> bytes:
        """Receives bytes from a remote socket.

        Returns:
            The bytes received from a remote socket.
        """
        msg_len = 0

        # The client might send nothing, therefore, return nothing as
        # well.
        try:
            msg_len = int(sock.recv(Communicator.BUFFER_SIZE).decode())
        except ValueError:
            return b""

        rcvd_len = 0
        msg = b""
        while rcvd_len != msg_len:
            data = sock.recv(Communicator.BUFFER_SIZE)
            msg += data
            rcvd_len += len(data)

        return msg

    def sendfile(self, filename: str, sock):
        """Sends bytes from a file to a remote socket.

        Args:
            filename: The file where the bytes come from to be
            sent.
        """

        with open(filename, "rb") as file:
            file_size = os.stat(file.name).st_size
            header = f"{filename}:{file_size}"
            header = f"{header:<{Communicator.BUFFER_SIZE}}"
            sock.send(header.encode())
            while True:
                data = file.read(Communicator.BUFFER_SIZE)
                if data == b"":
                    break
                sock.send(data)

    def recvfile(self, sock):
        """Receives bytes of a file from a remote socket."""

        file_header = sock.recv(Communicator.BUFFER_SIZE).decode() \
            .split(":")

        rcvd_len = 0
        with open(file_header[0], "wb") as file:
            while rcvd_len != int(file_header[1]):
                data = sock.recv(Communicator.BUFFER_SIZE)
                file.write(data)
                rcvd_len += len(data)


def is_music_file(filename: str) -> bool:
    """Validates the filename by checking if the filename given is a
    music file.
    """

    music_exts = [".mp3", ".m4a", ".ogg", ".opus", ".flac"]
    return any(list(filter(lambda ext: ext in filename, music_exts)))
