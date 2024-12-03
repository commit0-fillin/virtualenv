"""
A rough layout of the current storage goes as:

virtualenv-app-data
├── py - <version> <cache information about python interpreters>
│  └── *.json/lock
├── wheel <cache wheels used for seeding>
│   ├── house
│   │   └── *.whl <wheels downloaded go here>
│   └── <python major.minor> -> 3.9
│       ├── img-<version>
│       │   └── image
│       │           └── <install class> -> CopyPipInstall / SymlinkPipInstall
│       │               └── <wheel name> -> pip-20.1.1-py2.py3-none-any
│       └── embed
│           └── 3 -> json format versioning
│               └── *.json -> for every distribution contains data about newer embed versions and releases
└─── unzip <in zip app we cannot refer to some internal files, so first extract them>
     └── <virtualenv version>
         ├── py_info.py
         ├── debug.py
         └── _virtualenv.py
"""
from __future__ import annotations
import json
import logging
from abc import ABC
from contextlib import contextmanager, suppress
from hashlib import sha256
from virtualenv.util.lock import ReentrantFileLock
from virtualenv.util.path import safe_delete
from virtualenv.util.zipapp import extract
from virtualenv.version import __version__
from .base import AppData, ContentStore

class AppDataDiskFolder(AppData):
    """Store the application data on the disk within a folder layout."""
    transient = False
    can_update = True

    def __init__(self, folder) -> None:
        self.lock = ReentrantFileLock(folder)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.lock.path})'

    def __str__(self) -> str:
        return str(self.lock.path)

    def close(self):
        """Close the file lock."""
        self.lock.release()

    def py_info_clear(self):
        """Clear Python interpreter information."""
        py_info_folder = self.lock.path / "py"
        if py_info_folder.exists():
            for file in py_info_folder.iterdir():
                if file.is_file() and file.suffix in ('.json', '.lock'):
                    safe_delete(file)

class JSONStoreDisk(ContentStore, ABC):

    def __init__(self, in_folder, key, msg, msg_args) -> None:
        self.in_folder = in_folder
        self.key = key
        self.msg = msg
        self.msg_args = (*msg_args, self.file)

class PyInfoStoreDisk(JSONStoreDisk):

    def __init__(self, in_folder, path) -> None:
        key = sha256(str(path).encode('utf-8')).hexdigest()
        super().__init__(in_folder, key, 'python info of %s', (path,))

class EmbedDistributionUpdateStoreDisk(JSONStoreDisk):

    def __init__(self, in_folder, distribution) -> None:
        super().__init__(in_folder, distribution, 'embed update of distribution %s', (distribution,))
__all__ = ['AppDataDiskFolder', 'JSONStoreDisk', 'PyInfoStoreDisk']
