"""Music Sender Client module."""

import argparse
import os

import colorama

from .communication import Communicator, connection
from .utils import address_valid, set_working_directory


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

        Raises:
            BrokenPipeError:
                When the remote closes connection to this remote.

            ConnectionResetError:
                When the remote doesn't closes connection properly.
        """

        self.send(b"list")

        raw_songs_msg = self.recv().decode()
        if raw_songs_msg == "no-song-available":
            return [(0, "")]

        songs = raw_songs_msg.split("$sep")
        return list(enumerate(songs))

    def missing_songs_list(self) -> list[tuple[int, str]]:
        """Make a 'list' request to the server and returns only the
        songs that aren't in the client current directory.

        Returns:
            A list containing tuples that contains respectively the
            song's index and name.

        Raises:
            BrokenPipeError:
                When the remote closes connection to this remote.

            ConnectionResetError:
                When the remote doesn't closes connection properly.
        """

        songs = self.songs_list()
        return list(filter(lambda song: song[1] not in os.listdir("."), songs))

    @connection
    def request_song(self, index: int):
        """Makes a 'request <index>' request to the server.

        Args:
            index: The requested index from which the song comes from.

        Raises:
            IndexError: When the user requests a song from an out of
                        bounds index.

            BrokenPipeError:
                When the remote closes connection to this remote.

            ConnectionResetError:
                When the remote doesn't closes connection properly.
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
        if not song:
            print(colorama.Fore.RED + colorama.Style.BRIGHT
                  + "There are no musics in the server")
            break

        print(colorama.Fore.BLUE + colorama.Style.BRIGHT + f"({index}) "
              + colorama.Fore.WHITE + "->" + colorama.Fore.GREEN + f" {song}")
    print(colorama.Fore.GREEN + "=-" * 30)


def request_song_out(s_index: str, client: MusicSenderClient) -> bool:
    """Requests a song and prints its progress. It also shows errors
    if any.

    Args:
        s_index:
            A alphanumeric string representing the index from where
            the music is located in the server.
        client:
            A simple MusicSenderClient instance used for making the
            requesst.

    Raises:
        ConnectionRefusedError:
            It happens when the given address isn't listening and the
            client tries to requests something.

        ConnectionResetError:
            It happens when, in the middle of contact, the server
            crashes.

    Returns:
        A boolean value indicating success or failure in requesting a
        song.
    """

    try:
        index = int(s_index)
    except ValueError:
        print(colorama.Fore.RED + colorama.Style.BRIGHT
              + f"{s_index} is not a valid music index")
        return False

    if index < 0:
        print(colorama.Fore.RED + colorama.Style.BRIGHT
              + "Indexes should not be negative!")
        return False

    print(colorama.Fore.YELLOW + colorama.Style.BRIGHT
          + "Requesting song...")
    try:
        client.request_song(index)
    except IndexError:
        print(colorama.Fore.RED + colorama.Style.BRIGHT
              + f"There's no {index} index in the server!")
        return False
    except ConnectionError:
        print(colorama.Fore.RED + colorama.Style.BRIGHT
              + f"Failed to download. An error has occurred")
        return False
    else:
        print(colorama.Fore.GREEN + colorama.Style.BRIGHT
              + "Song downloaded successfully!")
        return True


def request_missing_out(client: MusicSenderClient):
    """Requests all the musics that are not in the client current
    directory and prints the progress of the request. It also shows
    errors if any.

    Args:
        client:
            A MusicSenderClient instance used to make the requests.
    Raises:
        ConnectionRefusedError:
            It happens when the given address isn't listening and the
            client tries to requests something.

        ConnectionResetError:
            It happens when, in the middle of contact, the server
            crashes.
    """

    print(colorama.Fore.GREEN + "-=" * 30)
    for index, song in client.missing_songs_list():
        if not song:
            print(colorama.Fore.RED + colorama.Style.BRIGHT
                  + "There are no musics to be downloaded!")
            break

        print(colorama.Fore.YELLOW + colorama.Style.BRIGHT
              + f"Downloading {song}")
        try:
            client.request_song(index)
        except ConnectionError:
            print(colorama.Fore.RED + colorama.Style.BRIGHT
                  + f"Failed to download {song}. An error has occurred")
        else:
            print(colorama.Fore.GREEN + colorama.Style.BRIGHT
                  + f"{song} Downloaded successfully")
        print(colorama.Fore.GREEN + "-=" * 30)


def handle_client_requests(args: argparse.Namespace, client: MusicSenderClient):
    """Executes each request the user has made.

    Args:
        client: MusicSenderClient instance used for making the
                requests.

        args: Namespace object returned by the parse_args() method
              containing the arguments given by the user.

    Raises:
        ConnectionRefusedError:
            It happens when the given address isn't listening and the
            client tries to requests something.

        ConnectionResetError:
            It happens when, in the middle of contact, the server
            crashes.
    """

    if args.list:
        songs_list_out(client.songs_list())
    if args.list_missing:
        songs_list_out(client.missing_songs_list(), "Missing Songs List")

    if args.request_song and args.request_missing:
        print(colorama.Fore.RED + colorama.Style.BRIGHT
              + "request-song and request-missing should not be used together.")
        return

    if args.request_song:
        request_song_out(args.request_song, client)
    elif args.request_missing:
        request_missing_out(client)

# TODO: Look for ways to refactoring this code


def main():
    """Main Client Program."""

    colorama.init(True)

    argp = argparse.ArgumentParser()

    argp.add_argument("-hs", "--host", help="The server's host IP",
                      required=True)
    argp.add_argument("-p", "--port", type=int, help="The server's port",
                      required=True)
    argp.add_argument(
        "-d", "--directory", default=".",
        help="Directory where the client will put the musics in.")
    argp.add_argument(
        "-l", "--list", action="store_true",
        help="Returns a list of songs available in the server.")
    argp.add_argument(
        "-r", "--request-song", default="",
        help="Request a song from a given index of the server's catalog.")
    argp.add_argument(
        "-lm", "--list-missing", action="store_true",
        help="Returns a list of musics that aren't in the client.")
    argp.add_argument(
        "-rm", "--request-missing", action="store_true",
        help="Requests all the missing songs.")

    args = argp.parse_args()

    if not (set_working_directory(args.directory)
            and address_valid((args.host, args.port))):
        return

    client = MusicSenderClient((args.host, args.port))

    try:
        handle_client_requests(args, client)
    except ConnectionResetError:
        print(colorama.Fore.RED + colorama.Style.BRIGHT
              + "Music Sender crashed!")
    except ConnectionRefusedError:
        print(colorama.Fore.RED + colorama.Style.BRIGHT
              + "There's no server listening in this port!")


if __name__ == "__main__":
    main()
