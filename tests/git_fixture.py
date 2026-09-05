"""Shared construction for disposable Git repositories used by tests."""

from __future__ import annotations

import subprocess
from pathlib import Path


GIT_MAINTENANCE_CONTROLS = (
    ("maintenance.auto", "false"),
    ("gc.auto", "0"),
    ("maintenance.autoDetach", "false"),
    ("gc.autoDetach", "false"),
)


def init_git_fixture(repository: Path, *init_arguments: str) -> None:
    """Initialize a disposable repository with detached writers disabled.

    Git may otherwise start auto-maintenance after a fixture commit and let the
    detached child outlive that commit.  A test's temporary-directory cleanup
    can then race the child while it writes below ``.git``.
    """

    subprocess.run(
        ("git", "-C", str(repository), "init", *init_arguments),
        check=True,
        capture_output=True,
        text=True,
    )
    for key, value in GIT_MAINTENANCE_CONTROLS:
        subprocess.run(
            ("git", "-C", str(repository), "config", "--local", key, value),
            check=True,
            capture_output=True,
            text=True,
        )
