#!/usr/bin/python3 -E
"""Root-owned fixed-command helper for the inactive quiet-guard install.

Only ``status`` and ``recover`` are exposed through sudoers.  The
``install-inactive`` command is invoked directly by the interactive setup
script while already root and is not granted NOPASSWD authority.  No command
in this commit launches or signals a process.
"""

from __future__ import annotations

import os
import sys

# This must run before any non-bootstrap import.  The kernel-selected system
# interpreter ignores PYTHON* variables via ``-E``; an installed NOPASSWD
# helper then admits only the root-owned private library plus the interpreter's
# standard-library roots.  In particular, neither cwd nor a repository path is
# ever added for installed code resolution.
_INSTALLED_HELPER = "/usr/local/libexec/joulewise-quiet-guard"
_INSTALLED_LIBRARY = "/Library/Application Support/JouleWise/quiet-guard-install/lib"
if os.path.realpath(__file__) == _INSTALLED_HELPER:
    _base = os.path.realpath(sys.base_prefix)
    _stdlib = [
        entry
        for entry in sys.path
        if entry
        and os.path.realpath(entry).startswith(_base + os.sep)
        and "site-packages" not in os.path.realpath(entry).split(os.sep)
    ]
    sys.path[:] = [_INSTALLED_LIBRARY, *_stdlib]
    os.environ.pop("PYTHONPATH", None)
    os.environ.pop("PYTHONHOME", None)

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import pwd
from typing import Mapping, Sequence

INSTALLED_LIBRARY = Path(_INSTALLED_LIBRARY)

from joulewise.quiet_guard import (  # noqa: E402
    GuardEngine,
    GuardError,
    PRODUCTION_STATE_ROOT,
    RECOVERY_ACKNOWLEDGMENT,
    failure_mapping,
)
from joulewise.quiet_guard_process import (  # noqa: E402
    PsProcessSource,
    Revalidation,
    revalidate_identity,
    validate_identity_mapping,
)


ALLOWED_COMMANDS = ("install-inactive", "status", "recover")
SAFE_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"
EXIT_REFUSED = 2
EXIT_ERROR = 3


@dataclass(frozen=True)
class InvocationIdentity:
    uid: int
    gid: int
    groups: tuple[int, ...]
    user: str
    home: str
    shell: str
    cwd: Path


def sanitized_environment(identity: InvocationIdentity, source: Mapping[str, str]) -> dict[str, str]:
    """Build a credential-free environment for a future agent child."""

    result = {
        "HOME": identity.home,
        "USER": identity.user,
        "LOGNAME": identity.user,
        "SHELL": identity.shell or "/bin/zsh",
        "PATH": SAFE_PATH,
        "JOULEWISE_QUIET_GUARD": "1",
    }
    for name in ("LANG", "LC_ALL", "LC_CTYPE", "TERM", "TMPDIR"):
        value = source.get(name)
        if value and "\x00" not in value:
            result[name] = value
    return result


def drop_privileges(identity: InvocationIdentity, source_environment: Mapping[str, str]) -> dict[str, str]:
    """Drop groups/gid/uid before any future agent child can execute.

    Commit 1 exposes no agent-exec command; this function pins and tests the
    privilege boundary that a later launcher commit must call before exec.
    """

    if os.geteuid() != 0:
        raise GuardError("privileged_command_refused", "privilege drop requires root")
    if identity.uid <= 0 or identity.gid <= 0 or not identity.groups:
        raise GuardError("privileged_command_refused", "invalid invoking identity")
    environment = sanitized_environment(identity, source_environment)
    os.setgroups(list(identity.groups))
    os.setgid(identity.gid)
    os.setuid(identity.uid)
    os.chdir(identity.cwd)
    os.environ.clear()
    os.environ.update(environment)
    return environment


def invoking_identity(cwd: Path) -> InvocationIdentity:
    """Resolve SUDO_UID to root-observed account and group data."""

    try:
        uid = int(os.environ["SUDO_UID"])
    except (KeyError, ValueError) as exc:
        raise GuardError("privileged_command_refused", "SUDO_UID is required") from exc
    if uid <= 0:
        raise GuardError("privileged_command_refused", "root may not be an agent child")
    account = pwd.getpwuid(uid)
    groups = tuple(sorted(set(os.getgrouplist(account.pw_name, account.pw_gid))))
    return InvocationIdentity(
        uid=uid,
        gid=account.pw_gid,
        groups=groups,
        user=account.pw_name,
        home=account.pw_dir,
        shell=account.pw_shell,
        cwd=cwd,
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="joulewise-quiet-guard")
    subcommands = result.add_subparsers(dest="command", required=True)
    subcommands.add_parser("install-inactive")
    subcommands.add_parser("status")
    recover = subcommands.add_parser("recover")
    recover.add_argument("--ack", required=True)
    return result


def _emit(value: object) -> None:
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _recovery_inputs(engine: GuardEngine) -> tuple[PsProcessSource, tuple]:
    """Independently re-observe every exact registered identity.

    The later T3-family commit will broaden this census with its dynamically
    derived family manifest.  Commit 1 has no production registration path,
    so the exact registry is the complete inactive-installation census basis.
    """

    source = PsProcessSource()
    state = engine.status()["state"]
    still_present = []
    for raw in state["registry"]["entries"]:
        expected = validate_identity_mapping(raw)
        result, observed = revalidate_identity(expected, source)
        if result == Revalidation.MATCH and observed is not None:
            still_present.append(observed)
    return source, tuple(still_present)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    if arguments.command not in ALLOWED_COMMANDS:
        _emit(failure_mapping("privileged_command_refused", "command is not allowlisted"))
        return EXIT_REFUSED
    if os.geteuid() != 0:
        _emit(failure_mapping("privileged_command_refused", "helper must run as root"))
        return EXIT_REFUSED
    engine = GuardEngine(PRODUCTION_STATE_ROOT)
    try:
        if arguments.command == "install-inactive":
            state = engine.initialize_inactive(privileged_setup=True)
            _emit(state)
            return 0
        if arguments.command == "status":
            _emit(engine.status())
            return 0
        if arguments.ack != RECOVERY_ACKNOWLEDGMENT:
            raise GuardError("recovery_acknowledgment_missing", "exact acknowledgment required")
        source, census = _recovery_inputs(engine)
        state = engine.recover(
            acknowledgment=arguments.ack,
            acknowledged_by=os.environ.get("SUDO_USER", "operator"),
            source=source,
            independent_census_rows=census,
        )
        _emit(state)
        return 0
    except GuardError as exc:
        _emit(exc.to_mapping())
        return EXIT_REFUSED
    except OSError as exc:
        _emit(failure_mapping("privileged_command_refused", str(exc)))
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
