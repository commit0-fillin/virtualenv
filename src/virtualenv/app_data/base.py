"""Application data stored by virtualenv."""
from __future__ import annotations
from abc import ABC, abstractmethod
from contextlib import contextmanager
from virtualenv.info import IS_ZIPAPP

class AppData(ABC):
    """Abstract storage interface for the virtualenv application."""

    @abstractmethod
    def close(self):
        """Called before virtualenv exits."""
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def reset(self):
        """Called when the user passes in the reset app data."""
        raise NotImplementedError("Subclasses must implement this method")

    @contextmanager
    def ensure_extracted(self, path, to_folder=None):
        """Some paths might be within the zipapp, unzip these to a path on the disk."""
        if IS_ZIPAPP:
            import tempfile
            import zipfile
            import shutil
            import os

            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                extracted_path = os.path.join(temp_dir, os.path.basename(path))
                
                if to_folder:
                    os.makedirs(to_folder, exist_ok=True)
                    final_path = os.path.join(to_folder, os.path.basename(path))
                    shutil.copy2(extracted_path, final_path)
                else:
                    final_path = extracted_path

                try:
                    yield final_path
                finally:
                    if to_folder:
                        os.remove(final_path)
        else:
            yield path

class ContentStore(ABC):
    pass
__all__ = ['AppData', 'ContentStore']
