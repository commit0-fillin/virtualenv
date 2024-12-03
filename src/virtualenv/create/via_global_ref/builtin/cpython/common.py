from __future__ import annotations
import re
from abc import ABC
from collections import OrderedDict
from pathlib import Path
from virtualenv.create.describe import PosixSupports, WindowsSupports
from virtualenv.create.via_global_ref.builtin.ref import RefMust, RefWhen
from virtualenv.create.via_global_ref.builtin.via_global_self_do import ViaGlobalRefVirtualenvBuiltin

class CPython(ViaGlobalRefVirtualenvBuiltin, ABC):
    @classmethod
    def can_describe(cls, interpreter):
        return interpreter.implementation == "CPython"

    def create(self):
        super().create()
        self._setup_stdlib()
        self._setup_scripts()

    def _setup_stdlib(self):
        stdlib = self.interpreter.stdlib
        if stdlib:
            self.copy_file(stdlib, dest=self.dest / "stdlib", symlink=True)

    def _setup_scripts(self):
        scripts = self.interpreter.scripts
        if scripts:
            for script in scripts:
                self.copy_file(script, dest=self.dest / "scripts", symlink=False)

class CPythonPosix(CPython, PosixSupports, ABC):
    """Create a CPython virtual environment on POSIX platforms."""
    
    def create(self):
        super().create()
        self._setup_posix_specific()

    def _setup_posix_specific(self):
        # Create bin directory
        bin_dir = self.dest / "bin"
        bin_dir.mkdir(exist_ok=True)

        # Create symlinks
        self._create_python_symlink()
        self._create_activate_scripts()

    def _create_python_symlink(self):
        python_exe = self.dest / "bin" / "python"
        python_exe.symlink_to(self.interpreter.executable)

    def _create_activate_scripts(self):
        activate_this = self.dest / "bin" / "activate_this.py"
        with activate_this.open("w") as f:
            f.write(self._generate_activate_this())

    def _generate_activate_this(self):
        return f"""
# This file must be used with "source bin/activate" *from bash*
# you cannot run it directly

deactivate () {{
    unset -f pydoc >/dev/null 2>&1 || true

    # reset old environment variables
    if [ -n "${{_OLD_VIRTUAL_PATH:-}}" ] ; then
        PATH="${{_OLD_VIRTUAL_PATH:-}}"
        export PATH
        unset _OLD_VIRTUAL_PATH
    fi
    if [ -n "${{_OLD_VIRTUAL_PYTHONHOME:-}}" ] ; then
        PYTHONHOME="${{_OLD_VIRTUAL_PYTHONHOME:-}}"
        export PYTHONHOME
        unset _OLD_VIRTUAL_PYTHONHOME
    fi

    # This should detect bash and zsh, which have a hash command that must
    # be called to get it to forget past commands.  Without forgetting
    # past commands the $PATH changes we made may not be respected
    if [ -n "${{BASH:-}}" -o -n "${{ZSH_VERSION:-}}" ] ; then
        hash -r 2> /dev/null
    fi

    if [ -n "${{_OLD_VIRTUAL_PS1:-}}" ] ; then
        PS1="${{_OLD_VIRTUAL_PS1:-}}"
        export PS1
        unset _OLD_VIRTUAL_PS1
    fi

    unset VIRTUAL_ENV
    unset VIRTUAL_ENV_PROMPT
    if [ ! "${{1:-}}" = "nondestructive" ] ; then
    # Self destruct!
        unset -f deactivate
    fi
}}

# unset irrelevant variables
deactivate nondestructive

VIRTUAL_ENV="{self.dest}"
export VIRTUAL_ENV

_OLD_VIRTUAL_PATH="$PATH"
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH

# unset PYTHONHOME if set
# this will fail if PYTHONHOME is set to the empty string (which is bad anyway)
# could use `if (set -u; : $PYTHONHOME) ;` in bash
if [ -n "${{PYTHONHOME:-}}" ] ; then
    _OLD_VIRTUAL_PYTHONHOME="${{PYTHONHOME:-}}"
    unset PYTHONHOME
fi

if [ -z "${{VIRTUAL_ENV_DISABLE_PROMPT:-}}" ] ; then
    _OLD_VIRTUAL_PS1="${{PS1:-}}"
    PS1="({self.dest.name}) ${{PS1:-}}"
    export PS1
    VIRTUAL_ENV_PROMPT="({self.dest.name}) "
    export VIRTUAL_ENV_PROMPT
fi

# This should detect bash and zsh, which have a hash command that must
# be called to get it to forget past commands.  Without forgetting
# past commands the $PATH changes we made may not be respected
if [ -n "${{BASH:-}}" -o -n "${{ZSH_VERSION:-}}" ] ; then
    hash -r 2> /dev/null
fi
"""

class CPythonWindows(CPython, WindowsSupports, ABC):
    def create(self):
        super().create()
        self._setup_windows_specific()

    def _setup_windows_specific(self):
        # Create Scripts directory
        scripts_dir = self.dest / "Scripts"
        scripts_dir.mkdir(exist_ok=True)

        # Create python.exe and pythonw.exe
        self._create_python_exe()
        self._create_pythonw_exe()

        # Create activate scripts
        self._create_activate_scripts()

    def _create_python_exe(self):
        python_exe = self.dest / "Scripts" / "python.exe"
        self.copy_file(self.interpreter.executable, dest=python_exe, symlink=False)

    def _create_pythonw_exe(self):
        pythonw_exe = self.dest / "Scripts" / "pythonw.exe"
        source_pythonw = Path(self.interpreter.executable).with_name("pythonw.exe")
        if source_pythonw.exists():
            self.copy_file(source_pythonw, dest=pythonw_exe, symlink=False)

    def _create_activate_scripts(self):
        activate_bat = self.dest / "Scripts" / "activate.bat"
        with activate_bat.open("w") as f:
            f.write(self._generate_activate_bat())

        activate_ps1 = self.dest / "Scripts" / "Activate.ps1"
        with activate_ps1.open("w") as f:
            f.write(self._generate_activate_ps1())

    def _generate_activate_bat(self):
        return f"""
@echo off

rem This file is UTF-8 encoded, so we need to update the current code page while executing it
for /f "tokens=2 delims=:." %%a in ('"%SystemRoot%\\System32\\chcp.com"') do (
    set _OLD_CODEPAGE=%%a
)
if defined _OLD_CODEPAGE (
    "%SystemRoot%\\System32\\chcp.com" 65001 > nul
)

set VIRTUAL_ENV={self.dest}

if not defined PROMPT set PROMPT=$P$G

if defined _OLD_VIRTUAL_PROMPT set PROMPT=%_OLD_VIRTUAL_PROMPT%
if defined _OLD_VIRTUAL_PYTHONHOME set PYTHONHOME=%_OLD_VIRTUAL_PYTHONHOME%

set _OLD_VIRTUAL_PROMPT=%PROMPT%
set PROMPT=({self.dest.name}) %PROMPT%

if defined PYTHONHOME set _OLD_VIRTUAL_PYTHONHOME=%PYTHONHOME%
set PYTHONHOME=

if defined _OLD_VIRTUAL_PATH set PATH=%_OLD_VIRTUAL_PATH%
if not defined _OLD_VIRTUAL_PATH set _OLD_VIRTUAL_PATH=%PATH%

set PATH=%VIRTUAL_ENV%\\Scripts;%PATH%
set VIRTUAL_ENV_PROMPT=({self.dest.name}) 

:END
if defined _OLD_CODEPAGE (
    "%SystemRoot%\\System32\\chcp.com" %_OLD_CODEPAGE% > nul
    set _OLD_CODEPAGE=
)
"""

    def _generate_activate_ps1(self):
        return f"""
function global:deactivate ([switch]$NonDestructive) {{
    # Revert to original values
    if (Test-Path function:_OLD_VIRTUAL_PROMPT) {{
        copy-item function:_OLD_VIRTUAL_PROMPT function:prompt
        remove-item function:_OLD_VIRTUAL_PROMPT
    }}

    if (Test-Path env:_OLD_VIRTUAL_PYTHONHOME) {{
        copy-item env:_OLD_VIRTUAL_PYTHONHOME env:PYTHONHOME
        remove-item env:_OLD_VIRTUAL_PYTHONHOME
    }}

    if (Test-Path env:_OLD_VIRTUAL_PATH) {{
        copy-item env:_OLD_VIRTUAL_PATH env:PATH
        remove-item env:_OLD_VIRTUAL_PATH
    }}

    if (Test-Path env:VIRTUAL_ENV) {{
        remove-item env:VIRTUAL_ENV
    }}

    if (Test-Path env:VIRTUAL_ENV_PROMPT) {{
        remove-item env:VIRTUAL_ENV_PROMPT
    }}

    if (!$NonDestructive) {{
        # Self destruct!
        remove-item function:deactivate
    }}
}}

deactivate -nondestructive

$env:VIRTUAL_ENV = "{self.dest}"

if (! $env:VIRTUAL_ENV_DISABLE_PROMPT) {{
    # Set the prompt to include the env name
    # Make sure _OLD_VIRTUAL_PROMPT is global
    function global:_OLD_VIRTUAL_PROMPT {{
        ""
    }}
    copy-item function:prompt function:_OLD_VIRTUAL_PROMPT
    function global:prompt {{
        # Add the custom prefix to the existing prompt
        $previous_prompt_value = & $function:_OLD_VIRTUAL_PROMPT
        ("({self.dest.name}) " + $previous_prompt_value)
    }}
}}

# Clear PYTHONHOME
if (Test-Path env:PYTHONHOME) {{
    copy-item env:PYTHONHOME env:_OLD_VIRTUAL_PYTHONHOME
    remove-item env:PYTHONHOME
}}

# Add the venv to the PATH
copy-item env:PATH env:_OLD_VIRTUAL_PATH
$env:PATH = "$env:VIRTUAL_ENV\\Scripts;$env:PATH"
$env:VIRTUAL_ENV_PROMPT = "({self.dest.name}) "
"""
_BREW = re.compile('/(usr/local|opt/homebrew)/(opt/python@3\\.\\d{1,2}|Cellar/python@3\\.\\d{1,2}/3\\.\\d{1,2}\\.\\d{1,2})/Frameworks/Python\\.framework/Versions/3\\.\\d{1,2}')
__all__ = ['CPython', 'CPythonPosix', 'CPythonWindows', 'is_mac_os_framework', 'is_macos_brew']

def is_mac_os_framework(interpreter):
    """Check if the interpreter is a macOS framework build."""
    return interpreter.platform == "darwin" and interpreter.prefix.endswith(".framework")

def is_macos_brew(interpreter):
    """Check if the interpreter is installed via Homebrew on macOS."""
    return interpreter.platform == "darwin" and bool(_BREW.search(str(interpreter.prefix)))
