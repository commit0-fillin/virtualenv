from __future__ import annotations
from abc import ABC, abstractmethod

class Seeder(ABC):
    """A seeder will install some seed packages into a virtual environment."""

    def __init__(self, options, enabled) -> None:
        """
        Create.

        :param options: the parsed options as defined within :meth:`add_parser_arguments`
        :param enabled: a flag weather the seeder is enabled or not
        """
        self.enabled = enabled
        self.env = options.env

    @classmethod
    def add_parser_arguments(cls, parser, interpreter, app_data):
        """
        Add CLI arguments for this seed mechanisms.

        :param parser: the CLI parser
        :param app_data: the CLI parser
        :param interpreter: the interpreter this virtual environment is based of
        """
        parser.add_argument(
            "--seed",
            dest="seed_packages",
            metavar="package_name",
            nargs="*",
            help="Specify packages to install in the created virtual environment.",
        )
        parser.add_argument(
            "--no-seed",
            dest="no_seed",
            action="store_true",
            help="Do not install seed packages in the created virtual environment.",
        )

    @abstractmethod
    def run(self, creator):
        """
        Perform the seed operation.

        :param creator: the creator (based of :class:`virtualenv.create.creator.Creator`) we used to create this         virtual environment
        """
        if not self.enabled:
            return

        if hasattr(self.env, 'no_seed') and self.env.no_seed:
            return

        seed_packages = getattr(self.env, 'seed_packages', [])
        if not seed_packages:
            return

        pip_exe = creator.bin_dir / 'pip'
        if not pip_exe.exists():
            raise RuntimeError(f"pip not found in {creator.bin_dir}")

        for package in seed_packages:
            try:
                creator.popen([str(pip_exe), 'install', package])
            except Exception as e:
                print(f"Failed to install {package}: {e}")
__all__ = ['Seeder']
