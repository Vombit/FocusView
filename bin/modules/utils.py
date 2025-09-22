# pylint: disable=broad-exception-caught, protected-access
"""pass"""
import os
import sys


def resource_path(relative_path: str) -> str:
    """Returns the absolute path"""
    if sys.platform == "darwin":  # macOS
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(sys.executable), "..", "..", "..")
        )
    else:  # Windows or Linux
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

    base_path = os.path.abspath(os.path.join(base_path, "..", ".."))

    return os.path.join(base_path, relative_path)
