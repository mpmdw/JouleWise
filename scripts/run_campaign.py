#!/usr/bin/env python3
"""Run a generated Slice 2M config directory sequentially.

The JouleWise CLI has two bundle layouts. A config with
``workload_profile.repetitions == 1`` creates one bundle at
``<runs_dir>/<run_id>/``. A config with repetitions greater than one dispatches
to the experiment runner and creates one member bundle per repetition at
``<runs_dir>/<run_id>__r1`` ... ``<runs_dir>/<run_id>__rN`` plus an incremental
manifest at ``<runs_dir>/experiments/<run_id>.json``.

The manifest is not a completion marker. Completion is detected only from each
member bundle's ``summary_metrics.json``. If a process is interrupted after some
members have been created, a later campaign sees those partial members as
``incomplete_existing`` and does not re-run; the operator must inspect or move
the member bundles before retrying because the real CLI would collide on the
existing run IDs.

Dry-run mode prints the exact plan and invokes nothing. It also writes no
campaign log entries; JSONL logging is reserved for actual campaign attempts.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.bundle import sanitize_id_component  # noqa: E402


STATUSES = ("ok", "failed", "skipped", "incomplete_existing", "config_error", "dry_run")


@dataclass(frozen=True)
class ConfigInfo:
    path: Path
    run_id: str
    raw_run_id: str
    repetitions: int


@dataclass(frozen=True)
class ConfigError:
    path: Path
    message: str
    run_id: str | None = None


@dataclass(frozen=True)
class ExistingState:
    action: str
    members_succeeded: int | None = None
    members_total: int | None = None
    non_succeeded_members: tuple[str, ...] = ()
    inspect_members: tuple[str, ...] = ()
    malformed_summaries: tuple[str, ...] = ()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config_dir", help="Directory containing generated JSON configs")
    parser.add_argument("--runs-dir", default="runs", help="Bundle output directory")
    parser.add_argument("--log", help="JSONL campaign log path")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without invoking benchmarks")
    parser.add_argument(
        "--backup",
        nargs="?",
        const="",
        help="Run scripts/backup_runs.sh, or a supplied backup command path, after each success",
    )
    parser.add_argument("--max-failures", type=int, default=1, help="Stop after this many failures")
    parser.add_argument(
        "--cli-cmd",
        help="Command prefix replacing '<python> -m joulewise'; 'run <config> --runs-dir <dir>' is appended",
    )
    return parser.parse_args(argv)


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def best_effort_run_id(config_path: Path) -> str | None:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    run_id = data.get("run_id")
    return run_id if isinstance(run_id, str) else None


def load_config_info(config_path: Path) -> ConfigInfo:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"failed to read config {config_path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"config is not valid JSON: {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"config must be a JSON object: {config_path}")
    run_id = data.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError(f"config missing non-empty run_id: {config_path}")
    sanitized_run_id = sanitize_id_component(run_id)
    if sanitized_run_id != run_id:
        print(
            f"note: sanitized run_id for {config_path}: {run_id!r} -> {sanitized_run_id!r}",
            file=sys.stderr,
        )
    workload_profile = data.get("workload_profile", {})
    if workload_profile is None:
        workload_profile = {}
    if not isinstance(workload_profile, dict):
        raise ValueError(f"workload_profile must be an object: {config_path}")
    repetitions = workload_profile.get("repetitions", 1)
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or repetitions < 1:
        raise ValueError(f"workload_profile.repetitions must be a positive integer: {config_path}")
    return ConfigInfo(path=config_path, run_id=sanitized_run_id, raw_run_id=run_id, repetitions=repetitions)


def command_for(config_path: Path, runs_dir: Path, cli_cmd: str | None) -> list[str]:
    prefix = shlex.split(cli_cmd) if cli_cmd else [sys.executable, "-m", "joulewise"]
    return prefix + ["run", str(config_path), "--runs-dir", str(runs_dir)]


def shell_quote(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def append_log(log_path: Path, row: dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists() and log_path.stat().st_size > 0:
        with log_path.open("rb+") as handle:
            handle.seek(-1, os.SEEK_END)
            if handle.read(1) != b"\n":
                handle.write(b"\n")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def log_row(
    *,
    config_path: Path,
    run_id: str | None,
    status: str,
    exit_code: int | None,
    duration_s: float | None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = {
        "timestamp": utc_timestamp(),
        "config": str(config_path),
        "run_id": run_id,
        "status": status,
        "exit_code": exit_code,
        "duration_s": duration_s,
    }
    if extra:
        row.update(extra)
    return row


def print_quiet_machine_warning() -> None:
    print("WARNING: This campaign needs a quiet machine with no other workloads.")
    print("WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap.")


def discover_configs(config_dir: Path) -> list[Path]:
    if not config_dir.is_dir():
        raise ValueError(f"config_dir is not a directory: {config_dir}")
    return sorted(config_dir.glob("*.json"))


def print_config_file_list(configs: list[Path]) -> None:
    print("Config files to execute:")
    if not configs:
        print("  <none>")
        return
    for config in configs:
        print(f"  {config}")


def backup_script_path(backup_arg: str) -> Path:
    if backup_arg:
        return Path(backup_arg)
    return Path(__file__).resolve().parent / "backup_runs.sh"


def backup_runs(runs_dir: Path, script: Path) -> None:
    result = subprocess.run([str(script), str(runs_dir)], check=False)
    if result.returncode != 0:
        print(
            f"warning: backup command failed with exit {result.returncode}: {script} {runs_dir}",
            file=sys.stderr,
        )


def member_bundle_dirs(runs_dir: Path, run_id: str, repetitions: int) -> list[Path]:
    return [runs_dir / f"{run_id}__r{rep}" for rep in range(1, repetitions + 1)]


def summary_status(summary_path: Path) -> tuple[str | None, str | None]:
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"{summary_path}: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"{summary_path}: malformed JSON ({exc.msg})"
    if not isinstance(summary, dict):
        return None, f"{summary_path}: summary_metrics.json is not a JSON object"
    status = summary.get("status")
    if not isinstance(status, str):
        return None, f"{summary_path}: summary_metrics.json lacks string status"
    return status, None


def existing_state(info: ConfigInfo, runs_dir: Path) -> ExistingState:
    if info.repetitions == 1:
        bundle_dir = runs_dir / info.run_id
        summary_path = bundle_dir / "summary_metrics.json"
        if summary_path.is_file():
            status, malformed = summary_status(summary_path)
            if malformed is not None:
                return ExistingState(
                    action="incomplete existing",
                    inspect_members=(bundle_dir.name,),
                    malformed_summaries=(malformed,),
                )
            return ExistingState(action="skip complete")
        if bundle_dir.exists():
            return ExistingState(action="incomplete existing", inspect_members=(bundle_dir.name,))
        return ExistingState(action="would run")

    members = member_bundle_dirs(runs_dir, info.run_id, info.repetitions)
    summary_paths = [member / "summary_metrics.json" for member in members]
    malformed_summaries: list[str] = []
    statuses: list[str | None] = []
    for summary_path in summary_paths:
        if summary_path.is_file():
            status, malformed = summary_status(summary_path)
            statuses.append(status)
            if malformed is not None:
                malformed_summaries.append(malformed)
        else:
            statuses.append(None)
    if malformed_summaries:
        inspect = tuple(member.name for member in members if member.exists())
        return ExistingState(
            action="incomplete existing",
            inspect_members=inspect,
            malformed_summaries=tuple(malformed_summaries),
        )
    if all(summary_path.is_file() for summary_path in summary_paths):
        non_succeeded = tuple(
            member.name
            for member, status in zip(members, statuses, strict=True)
            if status != "succeeded"
        )
        return ExistingState(
            action="skip complete",
            members_succeeded=sum(status == "succeeded" for status in statuses),
            members_total=len(members),
            non_succeeded_members=non_succeeded,
        )
    if any(member.exists() for member in members):
        inspect = tuple(member.name for member in members if member.exists())
        return ExistingState(action="incomplete existing", inspect_members=inspect)
    return ExistingState(action="would run")


def read_config_infos(config_paths: list[Path]) -> list[ConfigInfo | ConfigError]:
    items: list[ConfigInfo | ConfigError] = []
    for config_path in config_paths:
        try:
            items.append(load_config_info(config_path))
        except Exception as exc:
            items.append(
                ConfigError(
                    path=config_path,
                    message=str(exc),
                    run_id=best_effort_run_id(config_path),
                )
            )
    return items


def duplicate_run_id_error(items: list[ConfigInfo | ConfigError]) -> str | None:
    by_run_id: dict[str, list[Path]] = {}
    for item in items:
        if isinstance(item, ConfigInfo):
            by_run_id.setdefault(item.run_id, []).append(item.path)
    collisions = {run_id: paths for run_id, paths in by_run_id.items() if len(paths) > 1}
    if not collisions:
        return None
    parts = [
        f"{run_id}: {', '.join(str(path) for path in paths)}"
        for run_id, paths in sorted(collisions.items())
    ]
    return "duplicate sanitized run_id(s): " + "; ".join(parts)


def acquire_campaign_lock(runs_dir: Path) -> Path:
    runs_dir.mkdir(parents=True, exist_ok=True)
    lock_path = runs_dir / "campaign.lock"
    content = f"pid={os.getpid()} created_at={utc_timestamp()}\n"
    try:
        fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        try:
            existing = lock_path.read_text(encoding="utf-8").strip()
        except OSError:
            existing = "<unreadable>"
        raise RuntimeError(
            f"another campaign appears to be running (lock {lock_path}, created {existing}); "
            "if no campaign is running, delete the lock file and retry"
        ) from exc
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    return lock_path


def skipped_log_extra(state: ExistingState) -> dict[str, Any] | None:
    if state.members_total is None:
        return None
    return {
        "members_succeeded": state.members_succeeded,
        "members_total": state.members_total,
    }


def run_campaign(args: argparse.Namespace) -> int:
    config_dir = Path(args.config_dir)
    runs_dir = Path(args.runs_dir)
    log_path = Path(args.log) if args.log else runs_dir / "campaign_log.jsonl"

    if args.max_failures < 1:
        raise ValueError("--max-failures must be >= 1")

    configs = discover_configs(config_dir)
    print_config_file_list(configs)
    items = read_config_infos(configs)
    config_errors = [item for item in items if isinstance(item, ConfigError)]
    if config_errors:
        for item in config_errors:
            print(f"error: {item.message}", file=sys.stderr)
        return 2
    duplicate_error = duplicate_run_id_error(items)
    if duplicate_error is not None:
        print(f"error: {duplicate_error}", file=sys.stderr)
        return 2

    counts: Counter[str] = Counter()
    failures = 0
    lock_path: Path | None = None

    print_quiet_machine_warning()
    if args.dry_run:
        print("Dry run: no commands will be invoked and no campaign log will be written.")
    else:
        try:
            lock_path = acquire_campaign_lock(runs_dir)
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    try:
        for item in items:
            if isinstance(item, ConfigError):
                if args.dry_run:
                    counts["dry_run"] += 1
                    print(f"dry_run {item.path}: config error: {item.message}", file=sys.stderr)
                    continue
                failures += 1
                print(f"error: {item.message}", file=sys.stderr)
                append_log(
                    log_path,
                    log_row(
                        config_path=item.path,
                        run_id=item.run_id,
                        status="config_error",
                        exit_code=None,
                        duration_s=None,
                        extra={"error": item.message},
                    ),
                )
                counts["config_error"] += 1
                if failures >= args.max_failures:
                    break
                continue

            info = item
            config_path = info.path
            state = existing_state(info, runs_dir)
            command = command_for(config_path, runs_dir, args.cli_cmd)

            if args.dry_run:
                counts["dry_run"] += 1
                print(f"dry_run {info.run_id}: {state.action}: {shell_quote(command)}")
                continue

            if state.action == "skip complete":
                status = "skipped"
                exit_code = None
                duration_s = None
                if state.members_total is None:
                    print(f"skipped {info.run_id}: complete bundle already exists")
                else:
                    print(
                        f"skipped {info.run_id}: complete experiment already exists "
                        f"({state.members_succeeded}/{state.members_total} members succeeded)"
                    )
                    if state.non_succeeded_members:
                        print(
                            f"note: skipped experiment {info.run_id} contains non-succeeded "
                            f"members; inspect: {', '.join(state.non_succeeded_members)}",
                            file=sys.stderr,
                        )
                append_log(
                    log_path,
                    log_row(
                        config_path=config_path,
                        run_id=info.run_id,
                        status=status,
                        exit_code=exit_code,
                        duration_s=duration_s,
                        extra=skipped_log_extra(state),
                    ),
                )
                counts[status] += 1
                continue

            if state.action == "incomplete existing":
                status = "incomplete_existing"
                exit_code = None
                duration_s = None
                failures += 1
                inspect = ", ".join(state.inspect_members) if state.inspect_members else info.run_id
                if state.malformed_summaries:
                    detail = "malformed summary_metrics.json: " + "; ".join(state.malformed_summaries)
                elif info.repetitions == 1:
                    detail = f"{inspect} lacks summary_metrics.json"
                else:
                    detail = f"partial experiment members exist: {inspect}"
                print(
                    f"incomplete_existing {info.run_id}: {detail}; inspect or move those "
                    "bundle(s) before retrying",
                    file=sys.stderr,
                )
                append_log(
                    log_path,
                    log_row(
                        config_path=config_path,
                        run_id=info.run_id,
                        status=status,
                        exit_code=exit_code,
                        duration_s=duration_s,
                    ),
                )
                counts[status] += 1
                if failures >= args.max_failures:
                    break
                continue

            start = time.monotonic()
            result = subprocess.run(command, check=False)
            duration_s = time.monotonic() - start
            exit_code = result.returncode
            status = "ok" if exit_code == 0 else "failed"
            if status == "failed":
                failures += 1
            append_log(
                log_path,
                log_row(
                    config_path=config_path,
                    run_id=info.run_id,
                    status=status,
                    exit_code=exit_code,
                    duration_s=duration_s,
                ),
            )
            counts[status] += 1
            print(f"{status} {info.run_id}: exit={exit_code} duration_s={duration_s:.3f}")

            if status == "ok" and args.backup is not None:
                backup_runs(runs_dir, backup_script_path(args.backup))

            if failures >= args.max_failures:
                break
    finally:
        if lock_path is not None:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass

    print("Summary:")
    for status in STATUSES:
        if counts[status]:
            print(f"  {status}: {counts[status]}")
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return run_campaign(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
