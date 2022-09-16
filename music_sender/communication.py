"""Communication utilies module"""

import io
import os
import socket
import subprocess
import sys


class Communicator:
    """Mixin class responsible for implementing basic socket
    communication tasks like receiving and sending bytes.
    """

    BUFFER_SIZE = 4096

    def __init__(self) -> None:
        self.sock = None

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


def connection(request):
    """Decorator function which executes essential code before making
    a request.
    """

    def wrapper(self, *args, **kwargs):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
            self.sock.connect(self.address)
            return request(self, *args, **kwargs)
    return wrapper


def get_machine_local_ip() -> str:
    """Retrieves Machine current local IP address.
    
    Returns:
        A str representing a full IPV4 local IP.
    """

    ip = None

    if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):

        host_info = subprocess.run(["hostname", "-I"] ,capture_output=True)

        # The hostname command output follows the format:
        #   <IP> <MAC> <newline>.
        # Therefore, retrive the first value in the list.
        ip = host_info.stdout.split(b" ")[0].decode()
    elif sys.platform.startswith("win32"):
        ip = socket.gethostbyname(socket.gethostname())
    return ip
