from __future__ import annotations
import abc
from pathlib import Path
from virtualenv.create.describe import PosixSupports, Python3Supports, WindowsSupports
from virtualenv.create.via_global_ref.builtin.ref import PathRefToDest
from .common import PyPy

import textwrap

class PyPy3(PyPy, Python3Supports, abc.ABC):
    @classmethod
    def can_describe(cls, interpreter):
        return super().can_describe(interpreter) and interpreter.version_info[0] == 3

    def env_patch_text(self):
        return super().env_patch_text() + "\n" + textwrap.dedent(
            f"""
            import sys
            sys.executable = {str(self.exe)!r}
            """
        )

    def _setup_pypy_specific(self):
        super()._setup_pypy_specific()
        self._create_activate_scripts()

    def _create_activate_scripts(self):
        # Implementation depends on the OS, so it's left to the subclasses
        pass

class PyPy3Posix(PyPy3, PosixSupports):
    """PyPy 3 on POSIX."""
    
    @property
    def exe(self):
        return self.bin_dir / f"pypy{self.interpreter.version_info[0]}"

    def symlinks(self):
        yield self.exe, "python"
        yield self.exe, f"python{self.interpreter.version_info[0]}"
        yield self.exe, f"python{self.interpreter.version_info[0]}.{self.interpreter.version_info[1]}"

    def _create_activate_scripts(self):
        activate_this = self.bin_dir / "activate_this.py"
        with activate_this.open("w") as f:
            f.write(self._generate_activate_this())

        activate_sh = self.bin_dir / "activate"
        with activate_sh.open("w") as f:
            f.write(self._generate_activate_sh())

    def _generate_activate_this(self):
        return textwrap.dedent(f"""
            import os
            import sys

            old_os_path = os.environ.get('PATH', '')
            os.environ['PATH'] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + old_os_path
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if sys.platform == 'win32':
                site_packages = os.path.join(base, 'Lib', 'site-packages')
            else:
                site_packages = os.path.join(base, 'lib', 'python{sys.version_info[0]}.{sys.version_info[1]}', 'site-packages')
            prev_sys_path = list(sys.path)
            import site
            site.main()
            sys.path[:] = prev_sys_path
            site.main()
        """)

    def _generate_activate_sh(self):
        return textwrap.dedent(f"""
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
        """)

class Pypy3Windows(PyPy3, WindowsSupports):
    """PyPy 3 on Windows."""
    
    @property
    def exe(self):
        return self.bin_dir / f"pypy{self.interpreter.version_info[0]}.exe"

    def symlinks(self):
        executables = self.executables_for_win_pypy_less_v37()
        if executables:
            for exe in executables:
                yield exe, exe.name
        else:
            yield self.exe, "python.exe"
            yield self.exe, f"python{self.interpreter.version_info[0]}.exe"
            yield self.exe, f"python{self.interpreter.version_info[0]}{self.interpreter.version_info[1]}.exe"

    def executables_for_win_pypy_less_v37(self):
        """
        PyPy <= 3.6 (v7.3.3) for Windows contains only pypy3.exe and pypy3w.exe
        This method handles the non-existing exe sources for older PyPy versions.
        """
        if self.interpreter.version_info[:2] <= (3, 6):
            return [
                self.bin_dir / "pypy3.exe",
                self.bin_dir / "pypy3w.exe"
            ]
        return super().executables()

    def _create_activate_scripts(self):
        activate_bat = self.bin_dir / "activate.bat"
        with activate_bat.open("w") as f:
            f.write(self._generate_activate_bat())

        activate_ps1 = self.bin_dir / "Activate.ps1"
        with activate_ps1.open("w") as f:
            f.write(self._generate_activate_ps1())

    def _generate_activate_bat(self):
        return textwrap.dedent(f"""
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
        """)

    def _generate_activate_ps1(self):
        return textwrap.dedent(f"""
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
        """)
__all__ = ['PyPy3', 'PyPy3Posix', 'Pypy3Windows']
