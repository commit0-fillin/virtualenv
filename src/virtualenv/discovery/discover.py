from __future__ import annotations
from abc import ABC, abstractmethod

class Discover(ABC):
    """Discover and provide the requested Python interpreter."""

    @classmethod
    def add_parser_arguments(cls, parser):
        """
        Add CLI arguments for this discovery mechanisms.

        :param parser: the CLI parser
        """
        parser.add_argument(
            "--python",
            dest="python",
            metavar="py",
            help="interpreter based on which new virtual environment will be created",
        )

    def __init__(self, options) -> None:
        """
        Create a new discovery mechanism.

        :param options: the parsed options as defined within :meth:`add_parser_arguments`
        """
        self._has_run = False
        self._interpreter = None
        self._env = options.env

    @abstractmethod
    def run(self):
        """
        Discovers an interpreter.

        :return: the interpreter ready to use for virtual environment creation
        """
        if self._env.get("VIRTUAL_ENV"):
            raise RuntimeError("Cannot run virtualenv from within a virtual environment")

        python_path = self._env.get("VIRTUALENV_PYTHON") or self._env.get("PYTHON")
        if python_path:
            self._interpreter = self._get_interpreter_from_path(python_path)
        else:
            self._interpreter = self._discover_system_interpreter()

        self._has_run = True
        return self._interpreter

    @property
    def interpreter(self):
        """:return: the interpreter as returned by :meth:`run`, cached"""
        if not self._has_run:
            self.run()
        return self._interpreter
__all__ = ['Discover']
