from __future__ import annotations
import logging
from tempfile import mkdtemp
from virtualenv.util.path import safe_delete
from .via_disk_folder import AppDataDiskFolder

class TempAppData(AppDataDiskFolder):
    transient = True
    can_update = False

    def __init__(self) -> None:
        super().__init__(folder=mkdtemp())
        logging.debug('created temporary app data folder %s', self.lock.path)

    def reset(self):
        """
        Reset the temporary folder by deleting its contents and recreating it.
        """
        safe_delete(self.lock.path)
        self.lock.path.mkdir(parents=True, exist_ok=True)
        logging.debug('reset temporary app data folder %s', self.lock.path)
__all__ = ['TempAppData']
