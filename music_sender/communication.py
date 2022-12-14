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
        self.sock: socket.socket = None

    def send(self, message: bytes):
        """Sends bytes to a remote socket following a structured
        model.

        Returns:
            A bytes object containing the world 'ACK', indicating that
            the given message was successfully sent.

        Raises:
            BrokenPipeError:
                The remote tried to send data to a remote closed
                socket.

            ConnectionResetError:
                When the remote doesn't closes connection properly.
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
            ack += ack_data

        return ack

    def recv(self) -> bytes:
        """Receives bytes from a remote socket.

        Returns:
            The bytes received from a remote socket.

        Raises:
            BrokenPipeError:
                As it is with Communicator.send() method, the recv
                method implemented here will also send (ACK) data to a
                remote socket, therefore, bringing the risk of failing
                if the remote socket from which the (ACK) data is
                being sent to is closed.

            ConnectionResetError:
                When the remote doesn't closes connection properly.
        """

        try:
            msg_size = int(self.sock.recv(Communicator.BUFFER_SIZE))
        except ValueError:
            # This happens when the remote socket had closed the
            # connection
            return b""

        # Send the ACK header
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

        Raises:
            BrokenPipeError:
                Raised by the Communicator.send method utilised in
                this method. It commonly happens when the remote
                socket closes the connection.
            
            ConnectionResetError:
                When the remote doesn't closes connection properly.
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
        """Receives bytes of a file from a remote socket and write
        them into a file.

        Raises:
            IndexError:
                recvfile() is only called (i.e in the context
                of the music sender client) when the client requests a
                file from a given index in the server. Therefore, if
                the client tries to request a non-existent index to
                the server, the client will receive a 'out-of-bounds'
                message from the server.

            BrokenPipeError:
                When the remote closes connection to this remote.
            
            ConnectionResetError:
                When the remote doesn't closes connection properly.
        """

        data = self.recv().decode()

        # The only way of getting this reply from the server is by
        # the client requesting a song from an out of bounds index.
        if data == "out-of-bounds":
            raise IndexError

        filename, filesize = data.split(":")

        rcvd_len = 0
        with open(filename, "wb") as file:
            while rcvd_len != int(filesize):
                data = self.sock.recv(Communicator.BUFFER_SIZE)
                file.write(data)
                rcvd_len += len(data)


def connection(request):
    """Decorator function which executes essential code before making
    a request.

    Args:
        request: The method (MusicSenderClient) going to be called.
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

    ip_str = None

    if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):

        host_info = subprocess.run(["hostname", "-I"], capture_output=True)

        # The hostname command output follows the format:
        #   <IP> <MAC> <newline>.
        # Therefore, retrive the first value in the list.
        ip_str = host_info.stdout.split(b" ")[0].decode()
    elif sys.platform.startswith("win32"):
        ip_str = socket.gethostbyname(socket.gethostname())
    return ip_str
