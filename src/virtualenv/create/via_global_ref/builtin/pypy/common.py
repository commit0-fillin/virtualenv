from __future__ import annotations
import abc
from pathlib import Path
from virtualenv.create.via_global_ref.builtin.ref import PathRefToDest, RefMust, RefWhen
from virtualenv.create.via_global_ref.builtin.via_global_self_do import ViaGlobalRefVirtualenvBuiltin

class PyPy(ViaGlobalRefVirtualenvBuiltin, abc.ABC):
    @classmethod
    def can_describe(cls, interpreter):
        return interpreter.implementation == "PyPy" and interpreter.version_info[0] >= 3

    def sources(self):
        for src in super().sources():
            yield src
        yield PathRefToDest(self.interpreter.system_prefix / "lib-python", dest=self.dest / "lib-python", must_exist=RefMust.FILE, when=RefWhen.ANY)
        yield PathRefToDest(self.interpreter.system_prefix / "lib_pypy", dest=self.dest / "lib_pypy", must_exist=RefMust.FILE, when=RefWhen.ANY)

    @property
    def stdlib(self):
        return self.dest / "lib-python" / f"{self.interpreter.version_info[0]}.{self.interpreter.version_info[1]}"

    @property
    def stdlib_platform(self):
        return self.dest / "lib_pypy"

    @property
    def bin_dir(self):
        return self.dest / ("Scripts" if self.interpreter.platform == "win32" else "bin")

    @classmethod
    def exe_stem(cls):
        return "pypy3"

    def create(self):
        super().create()
        self._setup_pypy_specific()

    def _setup_pypy_specific(self):
        # Create bin/Scripts directory
        self.bin_dir.mkdir(parents=True, exist_ok=True)

        # Copy PyPy executable
        pypy_exe = self.interpreter.executable
        dest_exe = self.bin_dir / (pypy_exe.name if self.interpreter.platform == "win32" else "pypy3")
        self.copy_file(pypy_exe, dest=dest_exe, symlink=False)

        # Create symlinks/copies for python executables
        self._create_python_executables()

    def _create_python_executables(self):
        pypy_exe = self.bin_dir / (f"pypy3.exe" if self.interpreter.platform == "win32" else "pypy3")
        python_exe = self.bin_dir / ("python.exe" if self.interpreter.platform == "win32" else "python")
        python3_exe = self.bin_dir / (f"python3.exe" if self.interpreter.platform == "win32" else "python3")

        if self.interpreter.platform == "win32":
            self.copy_file(pypy_exe, dest=python_exe, symlink=False)
            self.copy_file(pypy_exe, dest=python3_exe, symlink=False)
        else:
            python_exe.symlink_to(pypy_exe.name)
            python3_exe.symlink_to(pypy_exe.name)
__all__ = ['PyPy']
