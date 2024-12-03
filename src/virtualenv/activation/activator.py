from __future__ import annotations
import os
from abc import ABC, abstractmethod

class Activator(ABC):
    """Generates activate script for the virtual environment."""

    def __init__(self, options) -> None:
        """
        Create a new activator generator.

        :param options: the parsed options as defined within :meth:`add_parser_arguments`
        """
        self.flag_prompt = os.path.basename(os.getcwd()) if options.prompt == '.' else options.prompt

    @classmethod
    def supports(cls, interpreter):
        """
        Check if the activation script is supported in the given interpreter.

        :param interpreter: the interpreter we need to support
        :return: ``True`` if supported, ``False`` otherwise
        """
        return True  # By default, assume all interpreters are supported

    @classmethod
    def add_parser_arguments(cls, parser, interpreter):
        """
        Add CLI arguments for this activation script.

        :param parser: the CLI parser
        :param interpreter: the interpreter this virtual environment is based of
        """
        parser.add_argument(
            '--prompt',
            default='.',
            help='Provides an alternative prompt prefix for this environment'
        )

    @abstractmethod
    def generate(self, creator):
        """
        Generate activate script for the given creator.

        :param creator: the creator (based of :class:`virtualenv.create.creator.Creator`) we used to create this         virtual environment
        """
        raise NotImplementedError("Subclasses must implement the generate method")
__all__ = ['Activator']
