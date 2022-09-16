"""Music Sender Server module."""

import argparse
import os
import re
from socketserver import BaseRequestHandler, ThreadingTCPServer

import colorama

from .communication import Communicator, get_machine_local_ip
from .utils import is_music_file, set_working_directory


class MusicSenderHandler(Communicator, BaseRequestHandler):
    """Music Sender request handler."""

    REQUEST_CODE = 0

    def __init__(self, request, client_address, server) -> None:
        super().__init__()
        BaseRequestHandler.__init__(self, request, client_address, server)

    def handle(self) -> None:

        print(f"{f'REQUEST {self.REQUEST_CODE}':=^60}")
        print(colorama.Fore.YELLOW + colorama.Style.BRIGHT
            + f"[*] CONNECTION FROM {self.client_address}")

        # The mixin class Communicator needs access to the socket.
        self.sock = self.request

        while True:
            message = self.recv()

            if message == b"":
                break

            print(colorama.Fore.YELLOW
                + f"[*] REQUEST FROM CLIENT IS \"{message.decode()}\" TYPE.")

            if message == b"list":
                print(colorama.Fore.YELLOW + "[*] PROCESSING \"list\" REQUEST")
                self.list_request()
                print(colorama.Fore.GREEN
                    + "[*] PROCESSING \"list\" REQUEST FINISHED")
            elif re.match(r"request \d+", message.decode()):
                index = int(message[8:])
                try:
                    song_name = self._get_songs(index)
                except IndexError:
                    print(colorama.Fore.RED + "INDEX IS OUT OF BOUNDS")
                    self.send(b"out-of-bounds")
                    break

                print(colorama.Fore.YELLOW
                    + f"[*] SENDING {song_name} TO CLIENT")
                self.song_request(index)
                print(colorama.Fore.GREEN
                    + f"[*] {song_name} WAS SENT TO THE CLIENT")

        MusicSenderHandler.REQUEST_CODE += 1

    def list_request(self):
        """Process a 'list' request from the client."""

        songs = "$sep".join(self._get_songs())
        self.send(songs.encode())

    def song_request(self, index: int):
        """Process a 'request <index>' request from the client. It
        sends the requested file bytes.

        Args:
            index: The index of the music.
        """

        self.sendfile(self._get_songs(index))

    def _get_songs(self, index: int = None) -> list[str] or str:
        if index is not None:
            return list(filter(is_music_file, os.listdir(".")))[index]
        return list(filter(is_music_file, os.listdir(".")))


def main():
    """Main Server Program."""

    colorama.init(True)

    argp = argparse.ArgumentParser()

    argp.add_argument("-p", "--port", type=int, default=5000,
        help="Server port")
    argp.add_argument("-d", "--directory", default=".")

    args = argp.parse_args()

    if not set_working_directory(args.directory):
        # Exit the application if the function failed to change directory
        return

    host, port = get_machine_local_ip(), args.port

    with ThreadingTCPServer((host, port), MusicSenderHandler) as server:
        print(colorama.Fore.GREEN + colorama.Style.BRIGHT
            + f"[*] SERVER RUNNING AT {host}:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("", end="\r")
    print(colorama.Fore.GREEN + colorama.Style.BRIGHT
        + "Server process terminated")


if __name__ == "__main__":
    main()
