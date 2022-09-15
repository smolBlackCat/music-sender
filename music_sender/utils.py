"""Utilities module."""

import io
import os


class Communicator:
    """Mixin class responsible for implementing basic socket
    communication tasks like receiving and sending bytes.
    """

    BUFFER_SIZE = 4096

    def __init__(self) -> None:
        self.sock = None
    # TODO: Implement a better socket protocol. In this new protocol,
    # send or recv should not be repeated twice, one should come after
    # the another

    def send(self, message: bytes):
        """Sends bytes to a remote socket following a structured
        model.
        """

        msg_header = f"{len(message)}"
        self.sock.send(msg_header.encode())

        ack_size = int(self.sock.recv(Communicator.BUFFER_SIZE))

        msg_buffer = io.BytesIO(message)
        while True:
            data = msg_buffer.read(Communicator.BUFFER_SIZE)
            if data == b"":
                break
            self.sock.send(data)

        rcvd_size = 0
        ack = b""
        while rcvd_size != ack_size:
            ack_data = self.sock.recv(Communicator.BUFFER_SIZE)
            rcvd_size += len(ack_data)

        return ack

    def recv(self) -> bytes:
        """Receives bytes from a remote socket.

        Returns:
            The bytes received from a remote socket.
        """
        try:
            msg_size = int(self.sock.recv(Communicator.BUFFER_SIZE))
        except ValueError:
            # This happens when the remote socket had closed the
            # connection
            return b""
        self.sock.send(b"3")

        rcvd_size = 0
        msg = b""
        while rcvd_size != msg_size:
            data = self.sock.recv(Communicator.BUFFER_SIZE)
            rcvd_size += len(data)
            msg += data

        self.sock.send(b"ACK")

        return msg

    def sendfile(self, filename: str):
        """Sends bytes from a file to a remote socket.

        Args:
            filename: The file where the bytes come from to be
            sent.
        """

        with open(filename, "rb") as file:
            file_size = os.stat(file.name).st_size
            self.send(f"{filename}:{file_size}".encode())

            while True:
                data = file.read(Communicator.BUFFER_SIZE)
                if data == b"":
                    break
                self.sock.send(data)

    def recvfile(self):
        """Receives bytes of a file from a remote socket."""

        filename, filesize = self.recv().decode().split(":")

        rcvd_len = 0
        with open(filename, "wb") as file:
            while rcvd_len != int(filesize):
                data = self.sock.recv(Communicator.BUFFER_SIZE)
                file.write(data)
                rcvd_len += len(data)


def is_music_file(filename: str) -> bool:
    """Validates the filename by checking if the filename given is a
    music file.
    """

    music_exts = [".mp3", ".m4a", ".ogg", ".opus", ".flac"]
    return any(list(filter(lambda ext: ext in filename, music_exts)))
