#!/usr/bin/env python3
"""Unprivileged quiet-guard client for the inactive Commit-1 installation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.quiet_guard import (  # noqa: E402
    GuardEngine,
    GuardError,
    TEST_STATE_ROOT_PREFIX,
    failure_mapping,
    validate_test_state_root,
)


PRIVILEGED_HELPER = "/usr/local/libexec/joulewise-quiet-guard"
EXIT_OK = 0
EXIT_REFUSED = 2
EXIT_ERROR = 3
TEST_SANDBOX_PREFIX = TEST_STATE_ROOT_PREFIX


def canonical_output(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def privileged_command(arguments: Sequence[str]) -> tuple[str, ...]:
    """Build the only runtime privilege route: noninteractive sudo."""

    return ("/usr/bin/sudo", "-n", PRIVILEGED_HELPER, *arguments)


def run_privileged(arguments: Sequence[str]) -> int:
    result = subprocess.run(privileged_command(arguments), check=False)
    return result.returncode


def validated_test_state_root(requested: Path) -> Path:
    """Return an explicit test sandbox below this process's temp directory."""

    return validate_test_state_root(requested)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="quiet_guard")
    subcommands = result.add_subparsers(dest="command", required=True)
    subcommands.add_parser("status", help="read the root-owned guard status")
    subcommands.add_parser("arm", help="request handoff (disabled in Commit 1)")
    recover = subcommands.add_parser("recover", help="invoke the non-agent recovery path")
    recover.add_argument("--ack", required=True)

    # This command is intentionally fixture-only.  It is the sole client-side
    # initializer and refuses the production root even when explicitly named.
    initialize = subcommands.add_parser("initialize-test", help=argparse.SUPPRESS)
    initialize.add_argument("--state-root", type=Path, required=True)
    initialize.add_argument("--host-id", required=True)
    initialize.add_argument("--boot-id", required=True)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    if arguments.command == "status":
        return run_privileged(("status",))
    if arguments.command == "recover":
        return run_privileged(("recover", "--ack", arguments.ack))
    if arguments.command == "arm":
        # Arm refuses before sudo: Commit 1 has neither the ratified verdict
        # reference nor a production promotion path.
        print(
            canonical_output(
                failure_mapping(
                    "t3_char_pair_verdict_missing",
                    "a lead-installed passing T3-CHAR-PAIR-01 verdict is required",
                )
            )
        )
        return EXIT_REFUSED
    if arguments.command == "initialize-test":
        try:
            state_root = validated_test_state_root(arguments.state_root)
            state = GuardEngine(
                state_root,
                host_id=arguments.host_id,
                boot_id=arguments.boot_id,
                test_mode=True,
            ).initialize_inactive()
        except GuardError as exc:
            print(canonical_output(exc.to_mapping()))
            return EXIT_REFUSED
        print(canonical_output(state))
        return EXIT_OK
    raise AssertionError("argparse admitted an unknown command")


if __name__ == "__main__":
    raise SystemExit(main())
