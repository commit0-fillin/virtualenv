from __future__ import annotations
import os
from pathlib import Path
from virtualenv.util.path import copy
from .base import PipInstall

class CopyPipInstall(PipInstall):
    def __init__(self, wheel):
        super().__init__(wheel)
        self.copy_source = None

    def _sync(self, src, dst):
        self.copy_source = src
        if src != dst:
            self.sync(src, dst)

    @staticmethod
    def sync(src, dst):
        src_path = Path(src)
        dst_path = Path(dst)
        if not dst_path.exists():
            dst_path.mkdir(parents=True, exist_ok=True)
        for src_file in src_path.rglob('*'):
            if src_file.is_file():
                rel_path = src_file.relative_to(src_path)
                dst_file = dst_path / rel_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                copy(str(src_file), str(dst_file))

    def _generate_new_files(self):
        pass  # No new files need to be generated for copy installation

    def install(self, creator):
        base = creator.purelib
        for filename in self.distribution.list_installed_files():
            dest = os.path.join(base, filename)
            source = os.path.join(self.copy_source, filename)
            if os.path.exists(source):
                copy(source, dest)

__all__ = ['CopyPipInstall']
