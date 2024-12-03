from __future__ import annotations
import abc
from pathlib import Path
from virtualenv.create.describe import PosixSupports, Python3Supports, WindowsSupports
from virtualenv.create.via_global_ref.builtin.ref import PathRefToDest
from .common import PyPy

class PyPy3(PyPy, Python3Supports, abc.ABC):
    @classmethod
    def can_describe(cls, interpreter):
        return super().can_describe(interpreter) and interpreter.version_info[0] == 3

    def env_patch_text(self):
        return super().env_patch_text() + "\n" + textwrap.dedent(
            f"""
            import sys
            sys.executable = {str(self.exe)!r}
            """
        )

class PyPy3Posix(PyPy3, PosixSupports):
    """PyPy 3 on POSIX."""
    
    @property
    def exe(self):
        return self.bin_dir / f"pypy{self.interpreter.version_info[0]}"

    def symlinks(self):
        yield self.exe, "python"
        yield self.exe, f"python{self.interpreter.version_info[0]}"
        yield self.exe, f"python{self.interpreter.version_info[0]}.{self.interpreter.version_info[1]}"

class Pypy3Windows(PyPy3, WindowsSupports):
    """PyPy 3 on Windows."""
    
    @property
    def exe(self):
        return self.bin_dir / f"pypy{self.interpreter.version_info[0]}.exe"

    def symlinks(self):
        yield self.exe, "python.exe"
        yield self.exe, f"python{self.interpreter.version_info[0]}.exe"
        yield self.exe, f"python{self.interpreter.version_info[0]}{self.interpreter.version_info[1]}.exe"
__all__ = ['PyPy3', 'PyPy3Posix', 'Pypy3Windows']
