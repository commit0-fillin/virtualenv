from __future__ import annotations
from contextlib import suppress
from .convert import convert

def get_env_var(key, as_type, env):
    """
    Get the environment variable option.

    :param key: the config key requested
    :param as_type: the type we would like to convert it to
    :param env: environment variables to use
    :return: The converted value of the environment variable, or None if not found
    """
    with suppress(KeyError):
        value = env[key]
        return convert(value, as_type, f"env var {key}")
    return None
__all__ = ['get_env_var']
