"""Music Sender Client module."""

import os
import socket

from .utils import Communicator


class MusicSenderClient(Communicator):
    """Music Sender Client class."""

    def __init__(self, address: tuple[str, int]):
        super().__init__()
        self.address = address
        self.sock = None

    def _connection_decorator(f):

        def connection(self, *args, **kwargs):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
                self.sock.connect(self.address)
                return f(self, *args, **kwargs)
        return connection

    @_connection_decorator
    def songs_list(self) -> list[tuple[int, str]]:
        """Makes a 'list' request to the server.

        Returns:
            A list containing tuples that contains respectively the
            song's index and name.
        """

        self.send(b"list")

        songs = self.recv().decode().split("$sep")
        return [(index, name) for index, name in enumerate(songs)]

    def missing_songs_list(self) -> list[tuple[int, str]]:
        """Make a 'list' request to the server and returns only the
        songs that aren't in the client current directory.
        """

        songs = self.songs_list()
        return list(filter(lambda song: song[1] not in os.listdir("."), songs))

    @_connection_decorator
    def request_song(self, index: int):
        """Makes a 'request <index>' request to the server.

        Args:
            index: The requested index from which the song comes from.
        """

        self.send(f"request {index}".encode())
        self.recvfile()


def songs_list_out(songs_list: list[tuple[int, str]]) -> None:
    """Prints out to the user the list of musics.

    Args:
        songs_list: list of tuples containing an int and a str, that
                    is, the song's index and the song's name
                    respectively, that's going to be iterated.
    """

    print("=-" * 30)
    print(f"{'Songs List':^60}")
    print("=-" * 30)
    for index, song in songs_list:
        print(f"({index}) -> {song}")
    print("=-" * 30)


def main():
    """Main Client Program."""

    os.chdir("dummy/")

    client = MusicSenderClient(("127.0.0.1", 5000))

    songs_list_out(client.missing_songs_list())


if __name__ == "__main__":
    main()
