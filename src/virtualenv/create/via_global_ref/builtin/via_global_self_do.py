from __future__ import annotations
from abc import ABC
from virtualenv.create.via_global_ref.api import ViaGlobalRefApi, ViaGlobalRefMeta
from virtualenv.create.via_global_ref.builtin.ref import ExePathRefToDest, RefMust, RefWhen
from virtualenv.util.path import ensure_dir
from .builtin_way import VirtualenvBuiltin

class BuiltinViaGlobalRefMeta(ViaGlobalRefMeta):

    def __init__(self) -> None:
        super().__init__()
        self.sources = []

class ViaGlobalRefVirtualenvBuiltin(ViaGlobalRefApi, VirtualenvBuiltin, ABC):

    def __init__(self, options, interpreter) -> None:
        super().__init__(options, interpreter)
        self._sources = getattr(options.meta, 'sources', None)

    @classmethod
    def can_create(cls, interpreter):
        """By default, all built-in methods assume that if we can describe it we can create it."""
        return cls.can_describe(interpreter)

    def set_pyenv_cfg(self):
        """
        We directly inject the base prefix and base exec prefix to avoid site.py needing to discover these
        from home (which usually is done within the interpreter itself).
        """
        super().set_pyenv_cfg()
        py_version = self.interpreter.version_info
        base_prefix = self.interpreter.system_prefix
        base_exec_prefix = self.interpreter.system_exec_prefix
        
        self.pyvenv_cfg["base-prefix"] = base_prefix
        self.pyvenv_cfg["base-exec-prefix"] = base_exec_prefix
        
        if py_version.major == 3 and py_version.minor >= 4:
            self.pyvenv_cfg["base-executable"] = self.interpreter.system_executable
__all__ = ['BuiltinViaGlobalRefMeta', 'ViaGlobalRefVirtualenvBuiltin']
