"""The Apple Framework builds require their own customization."""
from __future__ import annotations
import logging
import os
import struct
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from textwrap import dedent
from virtualenv.create.via_global_ref.builtin.ref import ExePathRefToDest, PathRefToDest, RefMust
from virtualenv.create.via_global_ref.builtin.via_global_self_do import BuiltinViaGlobalRefMeta
from .common import CPython, CPythonPosix, is_mac_os_framework, is_macos_brew
from .cpython3 import CPython3

class CPythonmacOsFramework(CPython, ABC):
    pass

class CPython3macOsFramework(CPythonmacOsFramework, CPython3, CPythonPosix):
    pass

def fix_mach_o(exe, current, new, max_size):
    """
    Fix the Mach-O header of the executable to update the interpreter path.

    :param exe: The path to the executable file.
    :param current: The current interpreter path.
    :param new: The new interpreter path.
    :param max_size: The maximum size allowed for the new interpreter path.
    """
    import struct
    import os

    with open(exe, 'rb+') as f:
        # Read the Mach-O header
        magic = f.read(4)
        if magic != b'\xcf\xfa\xed\xfe':  # MH_MAGIC_64
            raise ValueError("Not a 64-bit Mach-O file")

        # Skip to the number of load commands
        f.seek(16)
        num_cmds = struct.unpack('<I', f.read(4))[0]

        # Iterate through load commands
        for _ in range(num_cmds):
            cmd_start = f.tell()
            cmd, cmd_size = struct.unpack('<II', f.read(8))

            if cmd == 0x0C:  # LC_LOAD_DYLINKER
                # Found the interpreter load command
                f.seek(cmd_start + 8)
                offset = struct.unpack('<I', f.read(4))[0]
                f.seek(cmd_start + offset)
                old_path = f.read(max_size).decode('utf-8').rstrip('\0')

                if old_path == current:
                    # Update the interpreter path
                    if len(new) > max_size:
                        raise ValueError(f"New interpreter path is too long (max {max_size} bytes)")

                    f.seek(cmd_start + offset)
                    f.write(new.encode('utf-8').ljust(max_size, b'\0'))
                    return True

            f.seek(cmd_start + cmd_size)

    return False

class CPython3macOsBrew(CPython3, CPythonPosix):
    pass
__all__ = ['CPython3macOsBrew', 'CPython3macOsFramework', 'CPythonmacOsFramework']
