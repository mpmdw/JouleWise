"""Read-only pre-publication arm census; never a night gate probe."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from joulewise.night_gate import AGENT_CENSUS_ARGV, NightPlan, PlanError
from joulewise.quiet_guard_process import (
    DarwinProcessReader,
    DarwinProcessRecord,
    KernelProcessTable,
    ProcessObservationError,
    SysctlDarwinProcessReader,
)

# Same discovery population as the night gate, but PID-only output prevents
# multiline argv text from being mistaken for additional process hits.
# Do not add -a: own ancestors are read separately, preserving that population.
ARM_DISCOVERY_ARGV = (AGENT_CENSUS_ARGV[0], "-f", *AGENT_CENSUS_ARGV[2:])


@dataclass(frozen=True)
class Observation:
    inventory: KernelProcessTable
    records: tuple[DarwinProcessRecord, ...]
    hit_pids: tuple[int, ...]
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class Session:
    root_pid: int
    descendant_pids: tuple[int, ...]
    workloads: tuple[tuple[int, str], ...]
    exempt: bool


@dataclass(frozen=True)
class Verdict:
    receipt_class: str
    own_pids: tuple[int, ...]
    sessions: tuple[Session, ...]
    foreign_pids: tuple[int, ...]
    workloads: tuple[tuple[int, str], ...]
    diagnostics: tuple[str, ...]

    @property
    def publication_blocked(self) -> bool:
        return self.receipt_class == "REHEARSAL_STUB" and bool(
            self.foreign_pids or self.workloads
        )


def _ancestors(inventory: KernelProcessTable, pid: int) -> set[int]:
    rows = inventory.by_pid
    result: set[int] = set()
    while pid in rows and pid > 1 and pid not in result:
        result.add(pid)
        pid = rows[pid].ppid
    return result


def _operand(argv: tuple[str, ...], *, python: bool = False) -> tuple[str, tuple[str, ...], bool]:
    """Find an interpreter's executed operand, never a shell command string."""
    index = 1
    value_options = {"-W", "-X"} if python else {
        "-r", "--require", "--loader", "--experimental-loader", "--import",
        "--conditions", "-C", "--inspect-port",
    }
    while index < len(argv):
        arg = argv[index]
        if arg in {"-c", "-e", "--eval", "-p", "--print", "-"}:
            return "", (), False
        if python and arg.startswith("-c"):
            return "", (), False
        if python and arg == "-m":
            return (argv[index + 1], argv[index + 2:], True) if index + 1 < len(argv) else ("", (), False)
        if python and arg.startswith("-m"):
            return arg[2:], argv[index + 1:], True
        if arg == "--":
            index += 1
            break
        if arg in value_options:
            index += 2
        elif arg.startswith("-"):
            index += 1
        else:
            break
    return (argv[index], argv[index + 1:], False) if index < len(argv) else ("", (), False)


def _command(row: DarwinProcessRecord) -> tuple[str, tuple[str, ...], bool]:
    name = os.path.basename(row.executable)
    if re.fullmatch(r"python(?:\d+(?:\.\d+)*)?", name):
        return _operand(row.argv, python=True)
    if name in {"sh", "bash", "zsh"}:
        for arg in row.argv[1:]:
            if arg == "--" or not arg.startswith("-"):
                break
            if not arg.startswith("--") and "c" in arg[1:]:
                return "", (), False
        return _operand(row.argv)
    if name in {"node", "nodejs"}:
        return _operand(row.argv)
    return row.executable, row.argv[1:], False


def _interactive_root(row: DarwinProcessRecord) -> bool:
    name = os.path.basename(row.executable)
    if name == "claude":
        # _is_interactive_claude semantics (magistrate_watchdog), with the
        # executable-basename guard and actual argv rather than display text.
        args = tuple(arg.casefold() for arg in row.argv[1:])
        role = args[0] if args else ""
        return role not in {"daemon", "bg-pty-host", "--bg-pty-host", "bg-spare", "--bg-spare"} and not any(
            arg == "-p" or arg.startswith("--print") for arg in args
        )
    if name in {"node", "nodejs"}:
        script, _, _ = _command(row)
        return script.endswith("/t3-code/dist/cli.js")
    return False


def _own_root(inventory: KernelProcessTable, records: dict[int, DarwinProcessRecord],
              caller_pid: int, hit_pids: set[int]) -> int | None:
    """Select the outermost own-chain agent root, readable or unreadable."""
    own = _ancestors(inventory, caller_pid)
    rows = inventory.by_pid
    root = None
    pid = caller_pid
    while pid in own:
        own.remove(pid)
        row = records.get(pid)
        if row is not None and (_interactive_root(row) or (
            os.path.basename(row.executable) == "claude" and any(
                arg == "-p" or arg.startswith("--print") for arg in row.argv[1:]
            )
        )):
            root = pid
        elif row is None:
            # Unknown applies to this process, not its readable descendants.
            # Darwin pgrep never lists the caller's own ancestors, so hit
            # membership cannot be required of an unreadable own ancestor.
            root = pid
        pid = rows[pid].ppid
    return root


def _codex_exec(args: tuple[str, ...]) -> bool:
    value_options = {"-m", "--model", "-c", "--config", "-C", "--cd", "-p", "--profile", "-s", "--sandbox", "-a", "--ask-for-approval", "--enable", "--disable", "--add-dir", "-i", "--image"}
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in value_options:
            index += 2
        elif arg.startswith("-"):
            index += 1
        else:
            return arg == "exec"
    return False


def _workload(row: DarwinProcessRecord) -> str | None:
    operand, args, module = _command(row)
    name = os.path.basename(operand)
    if module:
        if operand == "unittest" or operand.startswith("unittest."):
            return "unittest"
        if operand == "pytest" or operand.startswith("pytest."):
            return "pytest"
        if operand == "joulewise" or operand.startswith("joulewise."):
            return "joulewise"
        if operand.startswith(("vllm", "mlx")):
            return "model"
        return None
    if name == "unittest":
        return "unittest"
    if name in {"pytest", "py.test"} or name.startswith("pytest-"):
        return "pytest"
    if operand == "scripts/shard_tests.py" or operand.endswith("/scripts/shard_tests.py"):
        return "shard"
    if name in {"powermetrics", "nvidia-smi"}:
        return "telemetry"
    if any(operand == path or operand.endswith("/" + path) for path in (
        "scripts/run_night.py", "scripts/run_campaign.py", "scripts/capture_t0_step.py",
    )) or name == "chain.zsh":
        return "capture"
    if name in {"vllm", "mlx"} and "serve" in args:
        return "model"
    if name == "codex" and _codex_exec(args):
        return "codex_exec"
    if name == "claude" and any(arg == "-p" or arg.startswith("--print") for arg in args):
        return "claude_print"
    # D-180 cl.3 / A173 R1: unknown work is IDLE at arm time only.
    return None


def classify_arm_census(plan: NightPlan, observation: Observation, *, caller_pid: int) -> Verdict:
    """Classify one observation without process reads, effects or night policy."""
    own = _ancestors(observation.inventory, caller_pid)
    records = {row.pid: row for row in observation.records}
    relevant = set().union(*(
        _ancestors(observation.inventory, pid) for pid in observation.hit_pids
    )) if observation.hit_pids else set()
    roots = {pid for pid in relevant if pid in records and _interactive_root(records[pid])}
    # Exact ancestry finds roots even when discovery omits them; an unreadable
    # own-chain discovery hit still anchors descendant workload scanning.
    own_root = _own_root(observation.inventory, records, caller_pid, set(observation.hit_pids))
    if own_root is not None:
        roots.add(own_root)
    workloads: dict[int, str] = {}
    sessions = []
    exempt = set(own)
    for pid in sorted(roots):
        descendants = observation.inventory.descendants(pid)
        work = tuple(
            (child, category)
            for child in sorted(descendants - own)
            if child in records and (category := _workload(records[child])) is not None
        )
        workloads.update(work)
        idle_exemption = plan.receipt_class == "REHEARSAL_STUB" and not work and (
            pid in own or (pid in records and _interactive_root(records[pid]))
        )
        if idle_exemption:
            exempt.update(descendants | {pid})
        sessions.append(Session(pid, tuple(sorted(descendants)), work, idle_exemption))
    # Missing/unreadable exact records are unknown, hence idle, with diagnostics.
    foreign = (set(observation.hit_pids) & records.keys()) - exempt
    return Verdict(plan.receipt_class, tuple(sorted(own)), tuple(sessions),
                   tuple(sorted(foreign)), tuple(sorted(workloads.items())), observation.diagnostics)


def observe_arm_census(*, caller_pid: int, reader: DarwinProcessReader | None = None) -> Observation:
    """One discovery and kernel inventory; unknown observations remain diagnostic."""
    reader = reader if reader is not None else SysctlDarwinProcessReader()
    diagnostics: list[str] = []
    hits: set[int] = set()
    try:
        probe = subprocess.run(ARM_DISCOVERY_ARGV, capture_output=True, text=True, check=False, timeout=30)
        if probe.returncode not in {0, 1}:
            diagnostics.append(f"discovery unknown: exit={probe.returncode} stderr={probe.stderr!r}")
        else:
            unknown_rows = 0
            for line in probe.stdout.splitlines():
                pid = line.strip()
                if pid.isdecimal() and int(pid) > 1:
                    hits.add(int(pid))
                else:
                    unknown_rows += 1
            if unknown_rows:
                diagnostics.append(f"discovery unknown row: count={unknown_rows}")
    except (OSError, subprocess.TimeoutExpired) as exc:
        diagnostics.append(f"discovery unknown: {exc}")
    try:
        inventory = reader.inventory()
    except (ProcessObservationError, OSError) as exc:
        return Observation(KernelProcessTable(()), (), tuple(sorted(hits)), tuple(diagnostics + [f"inventory unknown: {exc}"]))
    pids = _ancestors(inventory, caller_pid)
    for pid in hits:
        pids.update(_ancestors(inventory, pid))
    records: dict[int, DarwinProcessRecord] = {}
    rows = inventory.by_pid

    def read(pid: int) -> None:
        try:
            row = reader.read_exact(rows[pid]) if pid in rows else None
            if row is None:
                diagnostics.append(f"pid={pid} unknown: no exact record")
            else:
                records[pid] = row
        except (ProcessObservationError, OSError) as exc:
            diagnostics.append(f"pid={pid} unknown: {exc}")

    for pid in sorted(pids | hits):
        read(pid)
    descendants: set[int] = set()
    roots = {pid for pid, row in records.items() if _interactive_root(row)}
    own_root = _own_root(inventory, records, caller_pid, hits)
    if own_root is not None:
        roots.add(own_root)
    for pid in roots:
        descendants.update(inventory.descendants(pid))
    for pid in sorted(descendants - pids - hits):
        read(pid)
    return Observation(inventory, tuple(records.values()), tuple(sorted(hits)), tuple(diagnostics))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        raw = args.plan.read_bytes()
        plan = NightPlan.from_mapping(json.loads(raw))
    except (OSError, ValueError, PlanError) as exc:
        print(f"arm census invalid plan: {exc}", file=sys.stderr)
        return 2
    caller_pid = os.getpid()
    observation = observe_arm_census(caller_pid=caller_pid)
    verdict = classify_arm_census(plan, observation, caller_pid=caller_pid)
    print(json.dumps({"plan_sha256": hashlib.sha256(raw).hexdigest(),
                      "discovery_argv": ARM_DISCOVERY_ARGV, **asdict(verdict)}, sort_keys=True))
    print("publication blocked" if verdict.publication_blocked else
          "arm census clear/idle-only" if plan.receipt_class == "REHEARSAL_STUB" else
          "diagnostic only; existing all-agents-closed rule still applies")
    return 3 if verdict.publication_blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
