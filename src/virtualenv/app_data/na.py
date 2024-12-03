from __future__ import annotations
from contextlib import contextmanager
from .base import AppData, ContentStore

class AppDataDisabled(AppData):
    """No application cache available (most likely as we don't have write permissions)."""
    transient = True
    can_update = False

    def __init__(self) -> None:
        """Initialize the AppDataDisabled instance."""
        super().__init__()
    error = RuntimeError('no app data folder available, probably no write access to the folder')

    def close(self):
        """Do nothing as there's no app data to close."""
        return

    def reset(self):
        """Do nothing as there's no app data to reset."""
        return

    @contextmanager
    def locked(self, path):
        """
        Do nothing as there's no locking mechanism needed.
        
        This is a context manager that yields control and then returns.
        """
        yield

    def py_info_clear(self):
        """Do nothing as there's no Python info to clear."""
        return

class ContentStoreNA(ContentStore):

    def read(self):
        """Return None as there's nothing to read."""
        return None

    def write(self, content):
        """Do nothing as there's nowhere to write."""
        return

    def remove(self):
        """Do nothing as there's nothing to remove."""
        return
__all__ = ['AppDataDisabled', 'ContentStoreNA']
