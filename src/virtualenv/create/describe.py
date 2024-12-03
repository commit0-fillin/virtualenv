from __future__ import annotations
from abc import ABC
from collections import OrderedDict
from pathlib import Path
from virtualenv.info import IS_WIN

class Describe:
    """Given a host interpreter tell us information about what the created interpreter might look like."""
    suffix = '.exe' if IS_WIN else ''

    def __init__(self, dest, interpreter) -> None:
        self.interpreter = interpreter
        self.dest = dest
        self._stdlib = None
        self._stdlib_platform = None
        self._system_stdlib = None
        self._conf_vars = None

    @classmethod
    def can_describe(cls, interpreter):
        """Knows means it knows how the output will look."""
        return True  # Assuming this class can describe any interpreter

    @classmethod
    def exe_stem(cls):
        """Executable name without suffix - there seems to be no standard way to get this without creating it."""
        return 'python'  # Assuming the default executable name is 'python'

class Python3Supports(Describe, ABC):
    pass

class PosixSupports(Describe, ABC):
    pass

class WindowsSupports(Describe, ABC):
    pass
__all__ = ['Describe', 'PosixSupports', 'Python3Supports', 'WindowsSupports']
