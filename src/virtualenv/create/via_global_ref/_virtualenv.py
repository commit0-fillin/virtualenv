"""Patches that are applied at runtime to the virtual environment."""
from __future__ import annotations
import os
import sys
VIRTUALENV_PATCH_FILE = os.path.join(__file__)

def patch_dist(dist):
    """
    Distutils allows user to configure some arguments via a configuration file:
    https://docs.python.org/3/install/index.html#distutils-configuration-files.

    Some of this arguments though don't make sense in context of the virtual environment files, let's fix them up.
    """
    # Reset the prefix and exec_prefix to empty strings
    # This ensures that the virtual environment's paths are used instead of the global ones
    dist.prefix = ""
    dist.exec_prefix = ""

    # Reset the install directories to None
    # This allows the virtual environment to use its default locations
    dist.install_headers = None
    dist.install_lib = None
    dist.install_scripts = None
    dist.install_data = None

    # Clear any predefined build directories
    dist.script_name = None
    dist.script_args = None
    dist.command_packages = None

    # Ensure that the home directory is not set
    # This prevents interference with the user's home directory outside the virtual environment
    dist.home = None

    # Clear any custom installation schemes
    dist.install_schemes = {}

    # Reset the config files to prevent reading from global locations
    dist.find_config_files = lambda: []
_DISTUTILS_PATCH = ('distutils.dist', 'setuptools.dist')

class _Finder:
    """A meta path finder that allows patching the imported distutils modules."""
    fullname = None
    lock = []
sys.meta_path.insert(0, _Finder())
