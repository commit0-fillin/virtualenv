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
__all__ = ['PyPy']
