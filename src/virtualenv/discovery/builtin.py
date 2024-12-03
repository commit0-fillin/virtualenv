from __future__ import annotations
import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Callable
from virtualenv.info import IS_WIN, fs_path_id
from .discover import Discover
from .py_info import PythonInfo
from .py_spec import PythonSpec
if TYPE_CHECKING:
    from argparse import ArgumentParser
    from collections.abc import Generator, Iterable, Mapping, Sequence
    from virtualenv.app_data.base import AppData

class Builtin(Discover):
    python_spec: Sequence[str]
    app_data: AppData
    try_first_with: Sequence[str]

    def __init__(self, options) -> None:
        super().__init__(options)
        self.python_spec = options.python or [sys.executable]
        self.app_data = options.app_data
        self.try_first_with = options.try_first_with

    def __repr__(self) -> str:
        spec = self.python_spec[0] if len(self.python_spec) == 1 else self.python_spec
        return f'{self.__class__.__name__}(python_spec={spec!r}, app_data={self.app_data!r}, try_first_with={self.try_first_with!r})'

class LazyPathDump:

    def __init__(self, pos: int, path: Path, env: Mapping[str, str]) -> None:
        self.pos = pos
        self.path = path
        self.env = env

    def __repr__(self) -> str:
        content = f'discover PATH[{self.pos}]={self.path}'
        if self.env.get('_VIRTUALENV_DEBUG'):
            content += ' with =>'
            for file_path in self.path.iterdir():
                try:
                    if file_path.is_dir() or not file_path.stat().st_mode & os.X_OK:
                        continue
                except OSError:
                    pass
                content += ' '
                content += file_path.name
        return content

def path_exe_finder(spec: PythonSpec) -> Callable[[Path], Generator[tuple[Path, bool], None, None]]:
    """Given a spec, return a function that can be called on a path to find all matching files in it."""
    def finder(path: Path) -> Generator[tuple[Path, bool], None, None]:
        if not path.exists():
            return

        pattern = spec.generate_re(windows=sys.platform.startswith('win'))
        for item in path.iterdir():
            if item.is_file() and pattern.match(item.name):
                yield item, True
            elif item.is_dir():
                yield item, False

    return finder

class PathPythonInfo(PythonInfo):
    """python info from path."""
__all__ = ['Builtin', 'PathPythonInfo', 'get_interpreter']
