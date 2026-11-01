"""Resolve the fixture world's data from the active upstream root."""

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]


def set_project_root(path):
    global _ROOT
    _ROOT = Path(path)


def resolve_path(path):
    return _ROOT / path
