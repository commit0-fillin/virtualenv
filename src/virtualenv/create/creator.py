from __future__ import annotations
import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from argparse import ArgumentTypeError
from ast import literal_eval
from collections import OrderedDict
from pathlib import Path
from virtualenv.discovery.cached_py_info import LogCmd
from virtualenv.util.path import safe_delete
from virtualenv.util.subprocess import run_cmd
from virtualenv.version import __version__
from .pyenv_cfg import PyEnvCfg
HERE = Path(os.path.abspath(__file__)).parent
DEBUG_SCRIPT = HERE / 'debug.py'

class CreatorMeta:

    def __init__(self) -> None:
        self.error = None

class Creator(ABC):
    """A class that given a python Interpreter creates a virtual environment."""

    def __init__(self, options, interpreter) -> None:
        """
        Construct a new virtual environment creator.

        :param options: the CLI option as parsed from :meth:`add_parser_arguments`
        :param interpreter: the interpreter to create virtual environment from
        """
        self.interpreter = interpreter
        self._debug = None
        self.dest = Path(options.dest)
        self.clear = options.clear
        self.no_vcs_ignore = options.no_vcs_ignore
        self.pyenv_cfg = PyEnvCfg.from_folder(self.dest)
        self.app_data = options.app_data
        self.env = options.env
        self.system_site_packages = options.system_site_packages

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({', '.join((f'{k}={v}' for k, v in self._args()))})'

    @classmethod
    def can_create(cls, interpreter):
        """
        Determine if we can create a virtual environment.

        :param interpreter: the interpreter in question
        :return: ``None`` if we can't create, any other object otherwise that will be forwarded to                   :meth:`add_parser_arguments`
        """
        if interpreter and interpreter.executable:
            return cls()
        return None

    @classmethod
    def add_parser_arguments(cls, parser, interpreter, meta, app_data):
        """
        Add CLI arguments for the creator.

        :param parser: the CLI parser
        :param app_data: the application data folder
        :param interpreter: the interpreter we're asked to create virtual environment for
        :param meta: value as returned by :meth:`can_create`
        """
        parser.add_argument('--dest', help='Directory to create the virtual environment in', type=cls.validate_dest)
        parser.add_argument('--clear', action='store_true', help='Clear the virtual environment directory if it already exists')
        parser.add_argument('--no-vcs-ignore', action='store_true', help='Don\'t create VCS ignore files')
        parser.add_argument('--system-site-packages', action='store_true', help='Give the virtual environment access to the system site-packages dir')

    @abstractmethod
    def create(self):
        """Perform the virtual environment creation."""
        if self.dest.exists() and self.clear:
            safe_delete(self.dest)
        
        self.dest.mkdir(parents=True, exist_ok=True)
        
        self.create_configuration()
        self.setup_python()
        self.setup_scripts()
        
        if not self.no_vcs_ignore:
            self.setup_ignore_vcs()
        
        return self.dest

    @classmethod
    def validate_dest(cls, raw_value):
        """No path separator in the path, valid chars and must be write-able."""
        value = Path(raw_value)
        if not value.parent.exists():
            raise ArgumentTypeError(f"The parent directory {value.parent} does not exist")
        if value.exists() and not os.access(value, os.W_OK):
            raise ArgumentTypeError(f"The destination {value} is not writable")
        return value

    def setup_ignore_vcs(self):
        """Generate ignore instructions for version control systems."""
        vcs_ignore_contents = {
            '.gitignore': '# created by virtualenv automatically\n*\n',
            '.hgignore': 'syntax: glob\n# created by virtualenv automatically\n*\n',
        }
        
        for filename, content in vcs_ignore_contents.items():
            ignore_file = self.dest / filename
            if not ignore_file.exists():
                ignore_file.write_text(content)

    @property
    def debug(self):
        """:return: debug information about the virtual environment (only valid after :meth:`create` has run)"""
        if self._debug is None:
            self._debug = self._get_debug_info()
        return self._debug

    def _get_debug_info(self):
        debug_info = OrderedDict()
        debug_info['creator'] = self.__class__.__name__
        debug_info['interpreter'] = self.interpreter.executable
        debug_info['dest'] = str(self.dest)
        debug_info['app_data'] = str(self.app_data)
        debug_info['env'] = self.env
        debug_info['system_site_packages'] = self.system_site_packages
        return debug_info
__all__ = ['Creator', 'CreatorMeta']
