"""General utilities module."""


def is_music_file(filename: str) -> bool:
    """Validates the filename by checking if the filename given is a
    music file.
    """

    music_exts = [".mp3", ".m4a", ".ogg", ".opus", ".flac"]
    return any(list(filter(lambda ext: ext in filename, music_exts)))
