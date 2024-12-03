"""Bootstrap."""
from __future__ import annotations
import logging
import sys
from operator import eq, lt
from pathlib import Path
from subprocess import PIPE, CalledProcessError, Popen
from .bundle import from_bundle
from .periodic_update import add_wheel_to_update_log
from .util import Version, Wheel, discover_wheels
from .bundle import from_dir
from .download import download_wheel

def get_wheel(distribution, version, for_py_version, search_dirs, download, app_data, do_periodic_update, env):
    """Get a wheel with the given distribution-version-for_py_version trio, by using the extra search dir + download."""
    # First, try to get the wheel from the bundle
    wheel = from_bundle(distribution, version, for_py_version, search_dirs, app_data, do_periodic_update, env)
    if wheel:
        return wheel

    # If not found in bundle, search in the provided directories
    for directory in search_dirs:
        wheel = from_dir(distribution, version, for_py_version, [directory])
        if wheel:
            return wheel

    # If still not found, try to download the wheel
    if download:
        return download_wheel(distribution, version, for_py_version, app_data, env)

    # If all attempts fail, return None
    return None
__all__ = ['download_wheel', 'get_wheel', 'pip_wheel_env_run']
