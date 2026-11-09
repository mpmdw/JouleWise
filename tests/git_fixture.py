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


def clone_git_fixture(source: Path, destination: Path, *clone_arguments: str) -> None:
    """Clone a disposable repository with detached writers disabled.

    The same race as ``init_git_fixture``: a commit in the clone may start a
    detached ``git maintenance run --auto`` whose writes outlive the commit and
    race the enclosing temporary-directory cleanup.  Hosted run 42000523184
    (job 127154452928) failed that way in
    tests/test_receipt_histsem.py with ``[Errno 39] Directory not empty``
    on the clone's root after a commit.

    Install the controls with clone's --config option: Git writes these before
    fetching/checking out, so the clone itself (including checkout hooks) is
    fenced too. Configuring the repository after clone returns is too late.
    """

    controls = tuple(
        argument
        for key, value in GIT_MAINTENANCE_CONTROLS
        for argument in ("--config", f"{key}={value}")
    )
    subprocess.run(
        ("git", "clone", *controls, *clone_arguments, str(source), str(destination)),
        check=True,
        capture_output=True,
        text=True,
    )
