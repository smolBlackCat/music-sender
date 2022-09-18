import setuptools

setuptools.setup(
    name="music-sender",
    version="v1.0",
    description="music-sender is a project that aims to easy the process of "
        "transferring files between computers through terminal.",
    author="De Moura",
    author_email="m0ur4@protonmail.com",
    packages=["music_sender"],
    install_requires = ["colorama"],
    entry_points= {
        "console_scripts": [
            "ms-server = music_sender.server:main",
            "ms-client = music_sender.client:main"
        ]
    }
)
