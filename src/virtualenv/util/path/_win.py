from __future__ import annotations

import ctypes
from ctypes import wintypes

def get_short_path_name(long_name):
    """Gets the short path name of a given long path - http://stackoverflow.com/a/23598461/200291."""
    buffer_size = 256
    buffer = ctypes.create_unicode_buffer(buffer_size)
    get_short_path_name_w = ctypes.windll.kernel32.GetShortPathNameW
    get_short_path_name_w.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    get_short_path_name_w.restype = wintypes.DWORD
    
    result = get_short_path_name_w(long_name, buffer, buffer_size)
    if result == 0:
        return long_name  # If function fails, return the original path
    elif result > buffer_size:
        # If the buffer is too small, resize it and try again
        buffer = ctypes.create_unicode_buffer(result)
        get_short_path_name_w(long_name, buffer, result)
    
    return buffer.value

__all__ = ['get_short_path_name']
