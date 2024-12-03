"""A Python specification is an abstract requirement definition of an interpreter."""
from __future__ import annotations
import os
import re
PATTERN = re.compile('^(?P<impl>[a-zA-Z]+)?(?P<version>[0-9.]+)?(?:-(?P<arch>32|64))?$')

class PythonSpec:
    """Contains specification about a Python Interpreter."""

    def __init__(self, str_spec: str, implementation: str | None, major: int | None, minor: int | None, micro: int | None, architecture: int | None, path: str | None) -> None:
        self.str_spec = str_spec
        self.implementation = implementation
        self.major = major
        self.minor = minor
        self.micro = micro
        self.architecture = architecture
        self.path = path

    def generate_re(self, *, windows: bool) -> re.Pattern:
        """Generate a regular expression for matching against a filename."""
        impl = self.implementation or r'[a-zA-Z]+'
        version = rf'{self.major or r"\d+"}\.{self.minor or r"\d+"}\.{self.micro or r"\d+"}'
        arch = rf'(32|64)' if self.architecture is None else str(self.architecture)
        
        if windows:
            pattern = rf'{impl}-{version}(-{arch})?\.exe'
        else:
            pattern = rf'{impl}{version}'
        
        return re.compile(pattern, re.IGNORECASE)

    def satisfies(self, spec):
        """Called when there's a candidate metadata spec to see if compatible - e.g. PEP-514 on Windows."""
        if self.implementation and spec.implementation and self.implementation.lower() != spec.implementation.lower():
            return False
        
        if self.major is not None and spec.major is not None and self.major != spec.major:
            return False
        
        if self.minor is not None and spec.minor is not None and self.minor != spec.minor:
            return False
        
        if self.micro is not None and spec.micro is not None and self.micro != spec.micro:
            return False
        
        if self.architecture is not None and spec.architecture is not None and self.architecture != spec.architecture:
            return False
        
        if self.path is not None and spec.path is not None and self.path != spec.path:
            return False
        
        return True

    def __repr__(self) -> str:
        name = type(self).__name__
        params = ('implementation', 'major', 'minor', 'micro', 'architecture', 'path')
        return f'{name}({', '.join((f'{k}={getattr(self, k)}' for k in params if getattr(self, k) is not None))})'
__all__ = ['PythonSpec']
