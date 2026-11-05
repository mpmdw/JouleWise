"""Unattended R0 CLI: bounded checks, exclusive output, incremental receipts."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import signal
import sys
import time

from joulewise.align import r0
from joulewise.align.r0_host import (
    QuietGuard, Refused, command, disk_census, host_snapshot, inventory, smc_enumeration,
)

CHECKS = ("host", "disk", "smc", "load", "template", "generated", "ladder", "long-decode", "memory")
REPO = Path(__file__).resolve().parents[2]


class DeadlineExpired(BaseException):
    """Bypass endpoint/native Exception handlers so a timeout cannot be retried."""


def _path(value):
    # Reject lexical restricted components before resolving or stat'ing anything.
    path = Path(value)
    if "restricted" in path.parts or ".." in path.parts or not path.is_absolute():
        raise ValueError("paths must be absolute, without '..' or restricted components")
    return str(path)


def validate_config(config):
    if set(config) - {"schema", "models", "shade_cache", "disk_path", "custody_parents", "offloads"}:
        raise ValueError("unknown R0 config field")
    if config.get("schema") != "joulewise.align.r0.config.v1" or set(config.get("models", {})) != {"N", "D"}:
        raise ValueError("R0 config requires schema v1 and models N and D")
    for entry in config["models"].values():
        if set(entry) != {"source"}:
            raise ValueError("model entries contain only source; council pins cannot be overridden")
        _path(entry["source"])
    for key in ("shade_cache", "disk_path"):
        _path(config[key])
    if not isinstance(config.get("custody_parents"), list):
        raise ValueError("custody_parents must list any extras to the shared default parents")
    for path in config["custody_parents"]:
        _path(path)
    labels = set()
    for row in config.get("offloads", []):
        if set(row) != {"label", "inventory", "destination"} or row["label"] not in {"pilot8", "pilot9"} or row["label"] in labels:
            raise ValueError("offloads require unique pilot8/pilot9 labels, inventory and destination")
        labels.add(row["label"])
        _path(row["inventory"])
        _path(row["destination"])
    return config


@contextmanager
def deadline(seconds):
    def expired(signum, frame):
        raise DeadlineExpired(f"R0 check exceeded {seconds} seconds")
    old = signal.signal(signal.SIGALRM, expired)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


def save_report(output, report):
    # A run directory is exclusive; intermediate reports may be replaced only
    # by their owning runner. Final records are never reused by another run.
    for name, text in (("report.json", json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"),
                       ("report.md", r0.markdown(report))):
        temp = output / (name + ".tmp")
        temp.write_text(text)
        temp.replace(output / name)


def execute(config, output, checks, models, *, guard, backend_factory, per_check_timeout=7200):
    report = {"schema": "joulewise.align.r0.report.v1", "status": "running",
              "created_utc": datetime.now(timezone.utc).isoformat(),
              "config": config, "pins": r0.PINS, "checks": [], "complete_r0": False,
              "evidence_kind": "live_desk" if backend_factory.__module__ == "joulewise.align.r0_mlx" else "injected_backend",
              "selected_checks": checks, "selected_models": models,
              "authority": "origin/lane/2026-11-05-align-window-council:docs/align/council-2026-11-05/FINAL-DESIGN.md §§2.1,2.2,2.8",
              "authority_commit": "219fb151515383cbbcde887d096837a829c67396",
              "authority_blob": "0a802a3097a20c9f4dd5e8823d858302ae596785",
              "limitations": ["Selection data, not R1 thermal or arm validation.",
                              "R1 must freeze token budgets, intercepts and thermal slots.",
                              "Local inventories do not independently authenticate the remote revision."]}
    def receipt(name, model, fn, *, incremental=False):
        guard.check(force=True)
        started = time.monotonic()
        row = {"check": name, **({"model": model} if model else {}), "status": "running"}
        report["checks"].append(row)
        def progress(data):
            row.update(data)
            report["census"] = guard.receipts
            save_report(output, report)
        def run_unit(fn):
            guard.check(force=True)
            with deadline(per_check_timeout):
                return fn()
        progress({})
        try:
            result = fn(progress, run_unit) if incremental else run_unit(fn)
            row.update(result)
            guard.check(force=True)
        except Refused:
            raise
        except (Exception, DeadlineExpired) as exc:
            def interrupt(value):
                if isinstance(value, dict):
                    if value.get("status") == "running":
                        value["status"] = "interrupted"
                    for child in value.values():
                        interrupt(child)
                elif isinstance(value, list):
                    for child in value:
                        interrupt(child)
            interrupt(row)
            row.update(status="fail", error=f"{type(exc).__name__}: {exc}")
        row["check_seconds"] = time.monotonic() - started
        report["census"] = guard.receipts
        save_report(output, report)
        return row
    try:
        # This guard precedes host probes, file inventories, optional SMC and
        # lazy imports. No model can be opened after a refused initial census.
        guard.check(force=True)
        report["implementation_sha256"] = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), Path(r0.__file__), REPO / "joulewise/align/r0_host.py",
                         REPO / "joulewise/align/r0_mlx.py", REPO / "scripts/align_r0_checks.py")}
        report["config_sha256"] = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
        report["checkout_head"] = command(("git", "-C", str(REPO), "rev-parse", "HEAD")).strip()
        for name, fn in (("host", host_snapshot), ("disk", lambda: disk_census(config, r0.PINS, guard.check)),
                         ("smc", lambda: smc_enumeration(REPO, output / "smc"))):
            if name in checks:
                receipt(name, None, fn)
        for tag in models:
            wanted = [c for c in checks if c not in {"host", "disk", "smc"}]
            if not wanted:
                continue
            backend = None
            try:
                def load_backend():
                    nonlocal backend
                    backend = backend_factory(tag, config["models"][tag]["source"], config["shade_cache"], guard)
                    return backend.device_info()
                loaded = receipt("model-load", tag, load_backend)
                if loaded["status"] != "pass":
                    for name in wanted:
                        receipt(name, tag, lambda: {"status": "blocked", "reason": "model-load prerequisite failed"})
                    continue
                functions = {"load": lambda: r0.load_coherence(backend),
                             "template": lambda: r0.template_rewrites(backend),
                             "generated": lambda: r0.generated_rewrites(backend),
                             "ladder": lambda: r0.ladder(backend, tag),
                             "long-decode": lambda: r0.long_decode(backend),
                             "memory": lambda: r0.memory_peak(backend, tag)}
                for name in wanted:
                    composites = {
                        "load": lambda p, u: u(lambda: r0.load_coherence(backend, progress=p)),
                        "generated": lambda p, u: r0.generated_rewrites(backend, progress=p, run_unit=u),
                        "ladder": lambda p, u: r0.ladder(backend, tag, progress=p, run_unit=u),
                        "long-decode": lambda p, u: r0.long_decode(backend, progress=p, run_unit=u),
                    }
                    result = receipt(name, tag, composites.get(name, functions[name]), incremental=name in composites)
                    if name == "generated" and "transitions" in result:
                        receipt("checkpoint", tag, lambda: r0.checkpoint_verdict(tag, result))
                if tag == "D" and any(c in checks for c in ("load", "generated", "ladder")):
                    receipt("tool-envelopes", tag, lambda: r0.tool_envelopes(
                        [row for row in report["checks"] if row.get("model") == "D"]))
            finally:
                if backend is not None:
                    backend.close()
        bad = [r for r in report["checks"] if r["status"] not in {"pass", "not_required"}]
        report["status"] = "fail" if bad else "pass"
        report["complete_r0"] = (set(checks) == set(CHECKS) and set(models) == {"N", "D"}
                                  and not bad and report["evidence_kind"] == "live_desk")
    except Refused as exc:
        report.update(status="refused", refusal=str(exc))
    except Exception as exc:
        report.update(status="fail", error=f"{type(exc).__name__}: {exc}")
    finally:
        report["census"] = guard.receipts
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        save_report(output, report)
    return report


def main(argv=None, *, backend_factory=None, guard_factory=QuietGuard):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new exclusive record directory")
    parser.add_argument("--checks", default=",".join(CHECKS), help="comma-separated: " + ",".join(CHECKS))
    parser.add_argument("--models", default="N,D")
    parser.add_argument("--timeout", type=int, default=7200,
                        help="seconds per check, or per decode attempt / ladder episode / generated turn")
    parser.add_argument("--inventory", type=Path, help="hash this root only, before offload; output is a new JSON file")
    args = parser.parse_args(argv)
    checks, models = args.checks.split(","), args.models.split(",")
    if (not set(checks) <= set(CHECKS) or not set(models) <= {"N", "D"}
            or len(checks) != len(set(checks)) or len(models) != len(set(models)) or args.timeout <= 0):
        parser.error("invalid checks, models or timeout")
    config = validate_config(json.loads(args.config.read_text()))
    guard = guard_factory(config["custody_parents"])
    # One per-machine lock, not per output directory. An agent ancestor still
    # refuses: the lock never grants a census exemption.
    lock_path = Path("/private/tmp/joulewise-align-r0.lock")
    with lock_path.open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.exit(2, "Another R0 runner owns the machine lock\n")
        if args.inventory:
            guard.check(force=True)
            rows = inventory(_path(str(args.inventory)), guard.check)
            with args.output.open("x") as handle:
                json.dump(rows, handle, indent=2, sort_keys=True)
                handle.write("\n")
            return 0
        args.output.mkdir(parents=True, exist_ok=False)
        if backend_factory is None:
            # Importing this module imports no MLX; the backend loads lazily
            # after the first guard and Stage-1 readiness checks.
            from joulewise.align.r0_mlx import MlxBackend
            backend_factory = MlxBackend
        report = execute(config, args.output, checks, models, guard=guard,
                         backend_factory=backend_factory, per_check_timeout=args.timeout)
        print(f"{report['status']}: {args.output / 'report.json'}; complete_r0={report['complete_r0']}")
        return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
