"""Music Sender Client module."""

import argparse
import os

import colorama

from .utils import address_valid, set_working_directory

from .communication import Communicator, connection


class MusicSenderClient(Communicator):
    """Music Sender Client class."""

    def __init__(self, address: tuple[str, int]):
        super().__init__()
        self.address = address
        self.sock = None

    @connection
    def songs_list(self) -> list[tuple[int, str]]:
        """Makes a 'list' request to the server.

        Returns:
            A list containing tuples that contains respectively the
            song's index and name.
        """

        self.send(b"list")

        songs = self.recv().decode().split("$sep")
        return list(enumerate(songs))

    def missing_songs_list(self) -> list[tuple[int, str]]:
        """Make a 'list' request to the server and returns only the
        songs that aren't in the client current directory.

        Returns:
            A list containing tuples that contains respectively the
            song's index and name.
        """

        songs = self.songs_list()
        return list(filter(lambda song: song[1] not in os.listdir("."), songs))

    @connection
    def request_song(self, index: int):
        """Makes a 'request <index>' request to the server.

        Args:
            index: The requested index from which the song comes from.
        """

        self.send(f"request {index}".encode())
        self.recvfile()


def songs_list_out(songs_list: list[tuple[int, str]], title="Songs List") \
        -> None:
    """Prints out to the user the list of musics.

    Args:
        songs_list: list of tuples containing an int and a str, that
                    is, the song's index and the song's name
                    respectively, that's going to be iterated.
    """

    print(colorama.Fore.GREEN + "=-" * 30)
    print(colorama.Fore.YELLOW + f"{title:^60}")
    print(colorama.Fore.GREEN + "=-" * 30)
    for index, song in songs_list:
        print(colorama.Fore.BLUE + colorama.Style.BRIGHT + f"({index}) "
              + colorama.Fore.WHITE + "->" + colorama.Fore.GREEN + f" {song}")
    print(colorama.Fore.GREEN + "=-" * 30)


def main():
    """Main Client Program."""

    colorama.init(True)

    argp = argparse.ArgumentParser()

    argp.add_argument("-hs", "--host", help="The server's host IP")
    argp.add_argument("-p", "--port", type=int, help="The server's port")
    argp.add_argument("-d", "--directory", default=".",
                      help="Directory where the client will put the musics in.")
    argp.add_argument("-l", "--list", action="store_true",
                      help="Returns a list of songs available in the server.")
    argp.add_argument("-r", "--request-song", default="",
                      help="Request a song from a given index of the server's catalog.")
    argp.add_argument("-lm", "--list-missing", action="store_true",
                      help="Returns a list of musics that aren't in the client but in the "
                      "server.")
    argp.add_argument("-rm", "--request-missing", action="store_true",
                      help="Requests all the missing songs.")

    args = argp.parse_args()

    if not set_working_directory(args.directory):
        return
    if not address_valid((args.host, args.port)):
        return

    client = MusicSenderClient((args.host, args.port))

    if args.list:
        songs_list_out(client.songs_list())
    if args.list_missing:
        songs_list_out(client.missing_songs_list(), "Missing Songs List")
    if args.request_song:
        client.request_song(int(args.request_song))
        print(colorama.Fore.GREEN + colorama.Style.BRIGHT
              + "Song downloaded successfully!")


if __name__ == "__main__":
    main()
