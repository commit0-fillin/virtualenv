from __future__ import annotations
import logging
import os
import textwrap
from abc import ABC
from pathlib import Path
from virtualenv.create.creator import Creator, CreatorMeta
from virtualenv.info import fs_supports_symlink

class ViaGlobalRefMeta(CreatorMeta):

    def __init__(self) -> None:
        super().__init__()
        self.copy_error = None
        self.symlink_error = None
        if not fs_supports_symlink():
            self.symlink_error = 'the filesystem does not supports symlink'

class ViaGlobalRefApi(Creator, ABC):

    def __init__(self, options, interpreter) -> None:
        super().__init__(options, interpreter)
        self.symlinks = self._should_symlink(options)
        self.enable_system_site_package = options.system_site

    def env_patch_text(self):
        """Patch the distutils package to not be derailed by its configuration files."""
        return textwrap.dedent(
            """
            import os
            import sys
            import re
            
            def _patch_dist():
                # we cannot allow the distutils configuration files to screw us up
                import distutils.dist
                old_parse_config_files = distutils.dist.Distribution.parse_config_files
            
                def _parse_config_files(self, filenames=None):
                    if filenames is None:
                        filenames = self.find_config_files()
                    # We don't want to process any config files from the base system
                    return old_parse_config_files(self, [])
            
                distutils.dist.Distribution.parse_config_files = _parse_config_files
            
            _patch_dist()
            """
        )
__all__ = ['ViaGlobalRefApi', 'ViaGlobalRefMeta']
