#!/usr/bin/env python3
"""Run one gated unattended G2-a night, or its reporting courier."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from joulewise.night_gate import (
    RESULT_SCHEMA,
    SCHEMA,
    NightPlan,
    ProbeResult,
    Probes,
    agent_census,
    evaluate_night,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PROBE_TIMEOUT_S = 30
CENSUS_INTERVAL_S = 30
COURIER_DEADLINE_S = 600
COURIER_BACKOFF_S = (60, 180, 600)
COURIER_ALLOWED_TOOLS = (
    "Read,Glob,Grep,Bash,Edit,Write,mcp__claude_ai_Gmail__send_message"
)
COURIER_ARGV = (
    "/usr/bin/env",
    "claude",
    "-p",
    "{prompt}",
    "--output-format",
    "text",
    "--allowedTools",
    COURIER_ALLOWED_TOOLS,
)


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_bytes(_json_bytes(value))


def _append_log(custody_root: Path, message: str) -> None:
    stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    with (custody_root / "night.log").open("a", encoding="utf-8") as handle:
        handle.write(f"{stamp} {message}\n")


def _refusal_mapping(reason: str, detail: str, evidence: Any = None) -> dict[str, Any]:
    return {"reason": reason, "detail": detail, "evidence": evidence}


def _refusal_from_object(refusal: Any) -> dict[str, Any] | None:
    if refusal is None:
        return None
    if isinstance(refusal, Mapping):
        return dict(refusal)
    return {
        "reason": getattr(refusal, "reason", None),
        "detail": getattr(refusal, "detail", None),
        "evidence": getattr(refusal, "evidence", None),
    }


def _write_driver_refusal(
    path: Path, plan: NightPlan, reason: str, detail: str, evidence: Any = None
) -> dict[str, Any]:
    refusal = _refusal_mapping(reason, detail, evidence)
    _write_json(
        path,
        {
            "schema": SCHEMA,
            "receipt_class": plan.receipt_class,
            "plan_id": plan.plan_id,
            "verdict": "REFUSED",
            "refusal": refusal,
        },
    )
    return refusal


def _write_gate_refusal(path: Path, receipt: Any) -> None:
    raw = receipt.to_json_bytes()
    path.write_bytes(raw)


def _probe_runner(argv: tuple[str, ...] | list[str]) -> ProbeResult:
    """Run a gate probe without allowing an unbounded child process."""

    started = time.monotonic_ns()
    command = tuple(str(part) for part in argv)
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=PROBE_TIMEOUT_S,
            check=False,
        )
        return ProbeResult(
            argv=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            monotonic_ns=time.monotonic_ns(),
        )
    except subprocess.TimeoutExpired as error:
        return ProbeResult(
            argv=command,
            exit_code=124,
            stdout=error.stdout or "",
            stderr=(error.stderr or "") + f"ProbeError: timeout after {PROBE_TIMEOUT_S} s",
            monotonic_ns=time.monotonic_ns(),
        )
    except OSError as error:
        return ProbeResult(
            argv=command,
            exit_code=127,
            stdout="",
            stderr=f"ProbeError: {error}",
            monotonic_ns=max(started, time.monotonic_ns()),
        )


def make_probes() -> Probes:
    """Build the production probe bundle used by the pure night gate."""

    def checkout_head() -> str:
        result = _probe_runner(("git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"))
        if result.exit_code != 0:
            raise RuntimeError(f"checkout head probe failed: {result.stderr.strip()}")
        return result.stdout.strip()

    return Probes(
        run=_probe_runner,
        now_epoch_s=time.time,
        monotonic_ns=time.monotonic_ns,
        read_text=lambda path: Path(path).read_text(encoding="utf-8"),
        checkout_head=checkout_head,
    )


def _census_record(probe: ProbeResult, refusal: Any) -> dict[str, Any]:
    return {
        "argv": list(probe.argv),
        "exit_code": probe.exit_code,
        "stdout": probe.stdout,
        "stderr": probe.stderr,
        "monotonic_ns": probe.monotonic_ns,
        "refusal": _refusal_from_object(refusal),
    }


def _append_census(path: Path, probe: ProbeResult, refusal: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_census_record(probe, refusal), sort_keys=True) + "\n")


def _terminate_process_group(process: subprocess.Popen[Any]) -> int | None:
    """Stop a child session, leaving no retry path for the measurement chain."""

    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        return process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            return process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            return process.poll()


def _run_chain_once(
    chain_path: Path,
    plan: NightPlan,
    probes: Probes,
    night_dir: Path,
    *,
    command: list[str] | None = None,
) -> tuple[int | None, dict[str, Any] | None, int]:
    """Run one chain and abort it if a later agent census refuses the night."""

    census_path = night_dir / "censuses.jsonl"
    stdout_path = night_dir / "chain.stdout.log"
    stderr_path = night_dir / "chain.stderr.log"
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        environment = os.environ.copy()
        environment["NIGHT_PLAN_ID"] = plan.plan_id
        process = subprocess.Popen(
            command if command is not None else ["/bin/zsh", str(chain_path)],
            stdout=stdout,
            stderr=stderr,
            env=environment,
            start_new_session=True,
        )
        census_count = 0
        next_census = time.monotonic()
        while process.poll() is None:
            now = time.monotonic()
            if now >= next_census:
                probe, refusal = agent_census(probes)
                _append_census(census_path, probe, refusal)
                census_count += 1
                if refusal is not None:
                    return (
                        _terminate_process_group(process),
                        _refusal_mapping(
                            "night_aborted_agent_present",
                            "agent census refused while the chain was running",
                            _census_record(probe, refusal),
                        ),
                        census_count,
                    )
                next_census = now + CENSUS_INTERVAL_S
            time.sleep(min(1.0, max(0.01, next_census - time.monotonic())))
        return process.wait(), None, census_count


def _artifact_list(custody_root: Path, night_dir: Path) -> list[dict[str, str]]:
    paths = [
        custody_root / "night.log",
        night_dir / "receipt.json",
        night_dir / "refusal.json",
        night_dir / "result.json",
        night_dir / "censuses.jsonl",
        night_dir / "chain.stdout.log",
        night_dir / "chain.stderr.log",
    ]
    return [
        {"path": str(path.relative_to(custody_root)), "sha256": _sha256_path(path)}
        for path in paths
        if path.is_file()
    ]


def _night_date(plan: NightPlan) -> str:
    return datetime.fromtimestamp(plan.t0_epoch_s, timezone.utc).strftime("%Y%m%d")


def _durable_record(custody_root: Path, night_dir: Path, plan: NightPlan) -> None:
    """Best-effort results-branch publish; failure is logged but never fatal."""

    try:
        origin = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout.strip()
        clone = custody_root / "results-clone"
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", "main", origin, str(clone)],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        branch = f"night-results/{_night_date(plan)}"
        subprocess.run(
            ["git", "-C", str(clone), "checkout", "-B", branch],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        destination = clone / "docs" / "process_traces" / "night-results" / _night_date(plan)
        destination.mkdir(parents=True, exist_ok=True)
        for source in (
            night_dir / "receipt.json",
            night_dir / "refusal.json",
            night_dir / "result.json",
            night_dir / "censuses.jsonl",
            custody_root / "night.log",
        ):
            if source.exists():
                shutil.copy2(source, destination / source.name)
        subprocess.run(
            ["git", "-C", str(clone), "add", str(destination.relative_to(clone))],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(clone), "commit", "-m", f"record night {_night_date(plan)}"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(clone), "push", "origin", f"HEAD:{branch}"],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        _append_log(custody_root, f"durable record pushed branch={branch}")
    except (OSError, subprocess.SubprocessError) as error:
        _append_log(custody_root, f"durable record failed: {error}")


def _courier_argv(custody_root: Path, plan: NightPlan) -> tuple[str, ...]:
    prompt = (REPO_ROOT / "docs" / "process" / "NIGHT_COURIER_PROMPT.md").read_text(
        encoding="utf-8"
    )
    prompt = prompt.replace("{custody_root}", str(custody_root)).replace(
        "{plan_id}", plan.plan_id
    )
    return tuple(prompt if item == "{prompt}" else item for item in COURIER_ARGV)


def _wait_for_heartbeat(path: Path) -> bool:
    deadline = time.monotonic() + COURIER_DEADLINE_S
    while time.monotonic() < deadline:
        if path.is_file():
            return True
        time.sleep(1)
    return path.is_file()


def run_courier(custody_root: Path, plan: NightPlan) -> bool:
    """Start the courier until its first-action heartbeat proves liveness."""

    night_dir = custody_root / "night"
    night_dir.mkdir(parents=True, exist_ok=True)
    heartbeat = night_dir / "courier.heartbeat"
    attempts_path = night_dir / "courier.attempts.jsonl"
    for attempt in range(3):
        heartbeat.unlink(missing_ok=True)
        started_epoch_s = time.time()
        try:
            process = subprocess.Popen(
                _courier_argv(custody_root, plan),
                start_new_session=True,
            )
        except OSError as error:
            process = None
            error_text = str(error)
        else:
            error_text = None
        proved = process is not None and _wait_for_heartbeat(heartbeat)
        if process is not None and not proved:
            _terminate_process_group(process)
        attempt_record = {
            "attempt": attempt + 1,
            "started_epoch_s": started_epoch_s,
            "heartbeat": proved,
            "error": error_text,
        }
        with attempts_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(attempt_record, sort_keys=True) + "\n")
        _append_log(custody_root, f"courier attempt={attempt + 1} heartbeat={proved}")
        if proved:
            return True
        if attempt < 2:
            time.sleep(COURIER_BACKOFF_S[attempt])
    return False


def _write_result(
    custody_root: Path,
    night_dir: Path,
    plan: NightPlan,
    verdict: str,
    chain_exit_code: int | None,
    aborted_reason: str | None,
    started_epoch_s: float,
    started_monotonic_ns: int,
    chain_sha256: str | None,
    census_count: int,
) -> None:
    ended_epoch_s = time.time()
    ended_monotonic_ns = time.monotonic_ns()
    _write_json(
        night_dir / "result.json",
        {
            "schema": RESULT_SCHEMA,
            "plan_id": plan.plan_id,
            "receipt_class": plan.receipt_class,
            "verdict": verdict,
            "chain_exit_code": chain_exit_code,
            "aborted_reason": aborted_reason,
            "started_epoch_s": started_epoch_s,
            "ended_epoch_s": ended_epoch_s,
            "started_monotonic_ns": started_monotonic_ns,
            "ended_monotonic_ns": ended_monotonic_ns,
            "chain_sha256": chain_sha256,
            "census_count": census_count,
            "artifacts": _artifact_list(custody_root, night_dir),
        },
    )


def _load_plan(path: Path) -> NightPlan:
    return NightPlan.from_mapping(json.loads(path.read_text(encoding="utf-8")))


def run_night(plan_path: Path, *, rehearsal: bool = False) -> int:
    plan = _load_plan(plan_path)
    custody_root = Path(plan.custody_root)
    night_dir = custody_root / "night"
    night_dir.mkdir(parents=True, exist_ok=True)
    (night_dir / "censuses.jsonl").touch(exist_ok=True)
    started_epoch_s = time.time()
    started_monotonic_ns = time.monotonic_ns()
    _append_log(custody_root, "night driver started")
    probes = make_probes()
    receipt = evaluate_night(plan, probes)
    receipt_path = night_dir / "receipt.json"
    receipt_path.write_bytes(receipt.to_json_bytes())
    _append_log(custody_root, f"night gate verdict={receipt.verdict}")

    if rehearsal and plan.receipt_class != "REHEARSAL_STUB":
        refusal = _write_driver_refusal(
            night_dir / "refusal.json",
            plan,
            "night_receipt_class_invalid",
            "rehearsal requires receipt class REHEARSAL_STUB",
        )
        _write_result(
            custody_root,
            night_dir,
            plan,
            "REFUSED",
            None,
            refusal["reason"],
            started_epoch_s,
            started_monotonic_ns,
            None,
            0,
        )
        _durable_record(custody_root, night_dir, plan)
        run_courier(custody_root, plan)
        return 3

    if receipt.verdict != "GO" and not rehearsal:
        _write_gate_refusal(night_dir / "refusal.json", receipt)
        refusal = _refusal_from_object(receipt.refusal) or {}
        _write_result(
            custody_root,
            night_dir,
            plan,
            str(receipt.verdict),
            None,
            str(refusal.get("reason")) if refusal.get("reason") is not None else None,
            started_epoch_s,
            started_monotonic_ns,
            None,
            0,
        )
        _append_log(custody_root, "night gate refused")
        _durable_record(custody_root, night_dir, plan)
        run_courier(custody_root, plan)
        return 3

    if rehearsal:
        chain_path = Path("/dev/null")
        chain_sha256 = None
        command_path = None
    else:
        chain_path = Path(plan.chain_path)
        chain_sha256 = _sha256_path(chain_path) if chain_path.is_file() else None
        sidecar_path = Path(plan.chain_sha256_path)
        sidecar_text = sidecar_path.read_text(encoding="utf-8") if sidecar_path.is_file() else ""
        expected = (
            f"{chain_sha256}  {chain_path.name}\n" if chain_sha256 is not None else ""
        )
        if chain_sha256 is None or sidecar_text != expected:
            refusal = _write_driver_refusal(
                night_dir / "refusal.json",
                plan,
                "night_chain_digest_mismatch",
                "chain bytes do not match the arm-time SHA-256 sidecar",
                {"actual": chain_sha256, "expected": expected, "sidecar": sidecar_text},
            )
            _write_result(
                custody_root,
                night_dir,
                plan,
                "REFUSED",
                None,
                refusal["reason"],
                started_epoch_s,
                started_monotonic_ns,
                chain_sha256,
                0,
            )
            _append_log(custody_root, "night chain digest refused")
            _durable_record(custody_root, night_dir, plan)
            run_courier(custody_root, plan)
            return 3
        command_path = chain_path
        _append_log(custody_root, "night chain digest verified")

    if rehearsal:
        command = ["/bin/zsh", "-c", "sleep 2; echo REHEARSAL"]
    else:
        command = ["/bin/zsh", str(command_path)]

    # _run_chain_once centralizes the no-retry rule.  Rehearsal only changes
    # the command, never the single-spawn accounting or census behavior.
    chain_exit_code, abort, census_count = _run_chain_once(
        chain_path, plan, probes, night_dir, command=command
    )

    if abort is not None:
        _write_driver_refusal(
            night_dir / "refusal.json",
            plan,
            str(abort["reason"]),
            str(abort["detail"]),
            abort["evidence"],
        )
        verdict = "ABORTED"
        exit_code = 4
        aborted_reason = str(abort["reason"])
    elif rehearsal:
        _write_driver_refusal(
            night_dir / "refusal.json",
            plan,
            "night_rehearsal_only",
            "rehearsal chains do not produce a GO result",
        )
        verdict = "REHEARSAL_ONLY"
        exit_code = 3
        aborted_reason = None
    else:
        verdict = "GO"
        exit_code = 0 if chain_exit_code == 0 else 5
        aborted_reason = None
    _write_result(
        custody_root,
        night_dir,
        plan,
        verdict,
        chain_exit_code,
        aborted_reason,
        started_epoch_s,
        started_monotonic_ns,
        chain_sha256,
        census_count,
    )
    _append_log(custody_root, f"night result verdict={verdict}")
    _append_log(custody_root, f"night chain completed exit_code={chain_exit_code}")
    _durable_record(custody_root, night_dir, plan)
    run_courier(custody_root, plan)
    return exit_code


def dead_man(plan_path: Path) -> int:
    plan = _load_plan(plan_path)
    custody_root = Path(plan.custody_root)
    sent = custody_root / "night" / "courier.sent"
    if sent.exists():
        _append_log(custody_root, "dead-man skipped: courier already sent")
        return 0
    _append_log(custody_root, "dead-man starting courier")
    run_courier(custody_root, plan)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Exit 0: GO chain succeeded; 3: refusal; 4: census abort; 5: chain failure.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "dead-man", "rehearse"):
        command = subcommands.add_parser(name)
        command.add_argument("--plan", required=True, type=Path, metavar="PLAN.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        return run_night(args.plan)
    if args.command == "rehearse":
        return run_night(args.plan, rehearsal=True)
    return dead_man(args.plan)


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
