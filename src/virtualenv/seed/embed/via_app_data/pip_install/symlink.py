from __future__ import annotations
import os
from stat import S_IREAD, S_IRGRP, S_IROTH
from subprocess import PIPE, Popen
from virtualenv.util.path import safe_delete, set_tree
from .base import PipInstall

class SymlinkPipInstall(PipInstall):
    def __init__(self, wheel, creator, symlinks):
        super().__init__(wheel, creator)
        self.symlinks = symlinks

    @property
    def symlink_meta(self):
        return os.path.join(self.creator.purelib, self.wheel.name + ".virtualenv")

    def _install(self):
        self._create_symlinks()
        self._generate_meta()

    def _create_symlinks(self):
        for src, rel_dst in self.symlinks:
            dst = os.path.join(self.creator.purelib, rel_dst)
            if not os.path.exists(os.path.dirname(dst)):
                os.makedirs(os.path.dirname(dst))
            if os.path.exists(dst):
                if os.path.islink(dst) and os.readlink(dst) == src:
                    continue  # Skip if the symlink already exists and points to the correct source
                safe_delete(dst)
            os.symlink(src, dst)

    def _generate_meta(self):
        with open(self.symlink_meta, "w") as file_handler:
            file_handler.write("\n".join(f"{s}\t{d}" for s, d in self.symlinks))
        self._make_file_readonly(self.symlink_meta)

    def _make_file_readonly(self, file_path):
        os.chmod(file_path, S_IREAD | S_IRGRP | S_IROTH)

    def clear(self):
        if os.path.exists(self.symlink_meta):
            with open(self.symlink_meta, "r") as file_handler:
                for line in file_handler:
                    _src, dst = line.strip().split("\t")
                    dst = os.path.join(self.creator.purelib, dst)
                    if os.path.exists(dst):
                        safe_delete(dst)
            safe_delete(self.symlink_meta)

    @classmethod
    def can_be_applied(cls, interpreter):
        return interpreter.platform == "win32" or not cls._windows_no_symlink(interpreter)

    @classmethod
    def _windows_no_symlink(cls, interpreter):
        if interpreter.platform != "win32":
            return False
        # Windows may support symlinks, let's verify
        with Popen(
            [interpreter.executable, "-c", "import os; os.symlink('a', 'b')"],
            stderr=PIPE,
            stdout=PIPE,
            cwd=interpreter.system_stdlib,
        ) as process:
            _, stderr = process.communicate()
        return b"AttributeError: module 'os' has no attribute 'symlink'" in stderr
__all__ = ['SymlinkPipInstall']
