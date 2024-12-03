from __future__ import annotations
import abc
import fnmatch
from itertools import chain
from operator import methodcaller as method
from pathlib import Path
from textwrap import dedent
from virtualenv.create.describe import Python3Supports
from virtualenv.create.via_global_ref.builtin.ref import PathRefToDest
from virtualenv.create.via_global_ref.store import is_store_python
from .common import CPython, CPythonPosix, CPythonWindows, is_mac_os_framework, is_macos_brew

class CPython3(CPython, Python3Supports, abc.ABC):
    """CPython 3 or later."""

class CPython3Posix(CPythonPosix, CPython3):
    pass

class CPython3Windows(CPythonWindows, CPython3):
    """CPython 3 on Windows."""

    @classmethod
    def python_zip(cls, interpreter):
        """
        "python{VERSION}.zip" contains compiled *.pyc std lib packages, where
        "VERSION" is `py_version_nodot` var from the `sysconfig` module.
        :see: https://docs.python.org/3/using/windows.html#the-embeddable-package
        :see: `discovery.py_info.PythonInfo` class (interpreter).
        :see: `python -m sysconfig` output.

        :note: The embeddable Python distribution for Windows includes
        "python{VERSION}.zip" and "python{VERSION}._pth" files. User can
        move/rename *zip* file and edit `sys.path` by editing *_pth* file.
        Here the `pattern` is used only for the default *zip* file name!
        """
        version = interpreter.version_info
        py_version_nodot = f"{version.major}{version.minor}"
        return f"python{py_version_nodot}.zip"
__all__ = ['CPython3', 'CPython3Posix', 'CPython3Windows']
