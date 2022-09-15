"""Music Sender Server module."""

import os
import re
from socketserver import BaseRequestHandler, ThreadingTCPServer

from .utils import Communicator, is_music_file


class MusicSenderHandler(Communicator, BaseRequestHandler):
    """Music Sender request handler."""

    REQUEST_CODE = 0

    def __init__(self, request, client_address, server) -> None:
        super().__init__()
        BaseRequestHandler.__init__(self, request, client_address, server)

    def handle(self) -> None:

        print(f"{f'REQUEST {self.REQUEST_CODE}':=^60}")
        print(f"[*] CONNECTION FROM {self.client_address}")

        # The mixin class Communicator needs access to the socket.
        self.sock = self.request

        while True:
            message = self.recv()

            if message == b"":
                break

            print(f"[*] REQUEST FROM CLIENT IS \"{message.decode()}\" TYPE.")

            if message == b"list":
                print("[*] PROCESSING \"list\" REQUEST")
                self.list_request()
                print("[*] PROCESSING \"list\" REQUEST FINISHED")
            elif re.match(r"request \d+", message.decode()):
                index = int(message[8:])
                song_name = self._get_songs(index)
                print(f"[*] SENDING {song_name} TO CLIENT")
                self.song_request(index)
                print(f"[*] {song_name} WAS SENT TO THE CLIENT")
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

    os.chdir("/home/moura/Music")

    with ThreadingTCPServer(("127.0.0.1", 5000), MusicSenderHandler) as server:
        print("Server Started")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("", end="\r")
    print("Server process terminated")


if __name__ == "__main__":
    main()
