"""General utilities module."""

import os
import re

import colorama


def is_music_file(filename: str) -> bool:
    """Validates the filename by checking if the filename given is a
    music file.
    """

    music_exts = [".mp3", ".m4a", ".ogg", ".opus", ".flac"]
    return any(list(filter(lambda ext: ext in filename, music_exts)))


def set_working_directory(path: str) -> bool:
    """Sets the working directory from where cient or server will
    work in. It also prints if an error appears.

    Returns:
        True if everything is fine, otherwise False.
    """

    try:
        os.chdir(path)
    except FileNotFoundError:
        print(colorama.Fore.RED + "Directory not found!")
        return False
    except PermissionError:
        print(colorama.Fore.RED
              + "You're accessing a forbidden directory. try run it as an admin"
              + colorama.Style.BRIGHT + " (NOT RECOMMENDED)")
        return False
    except NotADirectoryError:
        print(colorama.Fore.RED
              + "Directory given is not actually a directory!")
        return False
    return True


def address_valid(addr: tuple[str, int]) -> bool:
    """Checks if the address given is valid. It also prints on the
    terminal.
    """

    host_valid = re.match(r"(192.168.\d{1,3}.\d{1,3}|127.0.0.1)", addr[0])
    port_valid = 1024 <= addr[1] <= 65432

    if not host_valid:
        print(colorama.Fore.RED + "The given host IP is not valid.")
    if not port_valid:
        print(colorama.Fore.RED + "Port given is out of range.")

    return host_valid and port_valid
