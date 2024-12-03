from __future__ import annotations
import os.path
from virtualenv.util.lock import NoOpFileLock
from .via_disk_folder import AppDataDiskFolder, PyInfoStoreDisk

class ReadOnlyAppData(AppDataDiskFolder):
    can_update = False

    def __init__(self, folder: str) -> None:
        if not os.path.isdir(folder):
            msg = f'read-only app data directory {folder} does not exist'
            raise RuntimeError(msg)
        super().__init__(folder)
        self.lock = NoOpFileLock(folder)
        self.folder = folder
        self.py_info_store = _PyInfoStoreDiskReadOnly(os.path.join(folder, 'py'))

class _PyInfoStoreDiskReadOnly(PyInfoStoreDisk):
    pass
__all__ = ['ReadOnlyAppData']
