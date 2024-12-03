"""Inspect a target Python interpreter virtual environment wise."""
from __future__ import annotations
import sys

def run():
    """Print debug data about the virtual environment."""
    print("Virtual Environment Debug Information:")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"sys.prefix: {sys.prefix}")
    print(f"sys.base_prefix: {sys.base_prefix}")
    print(f"sys.exec_prefix: {sys.exec_prefix}")
    print(f"sys.base_exec_prefix: {sys.base_exec_prefix}")
    print(f"sys.path:")
    for path in sys.path:
        print(f"  - {path}")
    print(f"Environment Variables:")
    for key, value in sorted(sys.environ.items()):
        print(f"  {key}: {value}")
if __name__ == '__main__':
    run()
