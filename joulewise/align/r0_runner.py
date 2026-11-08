"""Unattended R0 CLI: bounded checks, exclusive output, incremental receipts."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time

from joulewise.align import r0
from joulewise.align.r0_host import (
    QuietGuard, Refused, command, disk_census, display_census, host_snapshot, host_identity, inventory,
    smc_enumeration,
    ProfileRefused, profile_config, step_budget,
)

CHECKS = ("host", "disk", "load", "template", "generated", "memory", "smc", "ladder", "long-decode")
ACCEPTED_OUTCOMES = {"checkpoint": {"required", "not_required"}, "ladder": {"pass", "fallback"},
                     "template": {"diagnostic"}, "disk": {"diagnostic"},
                     # Erratum 2: SMC selection is independent of host,
                     # disk and model checks. Record inconclusive and proceed.
                     "smc": {"pass", "inconclusive"}}
REPO = Path(__file__).resolve().parents[2]
LOAD_REFERENCE_NOTE = "docs/align/v4/R0-LOAD-REFERENCE-NOTE.md"
LOAD_REFERENCE_BASIS = ("lead ruling 2026-11-06 under RUN_STATE items 181/183 (Ed: approve changes "
                        "that speed the science and harm nothing)")


def git_blob_sha1(path):
    """The git blob id of a file's bytes (what `git hash-object` prints)."""
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


class DeadlineExpired(BaseException):
    """Bypass endpoint/native Exception handlers so a timeout cannot be retried."""


class _StopChecks(Exception):
    """The failed receipt is already saved; unwind and close the backend."""


def _path(value):
    # Reject lexical restricted components before resolving or stat'ing anything.
    path = Path(value)
    if "restricted" in path.parts or ".." in path.parts or not path.is_absolute():
        raise ValueError("paths must be absolute, without '..' or restricted components")
    return str(path)


def validate_config(config):
    if set(config) - {"schema", "models", "shade_cache", "disk_path", "custody_parents", "offloads", "measurement_hw_model", "anchor_source", "smc_step"}:
        raise ValueError("unknown R0 config field")
    if config.get("schema") != "joulewise.align.r0.config.v1" or set(config.get("models", {})) != {"D"}:
        raise ValueError("R0 config requires schema v1 and D only (Amendment 1)")
    if not isinstance(config.get("measurement_hw_model"), str) or not config["measurement_hw_model"].strip():
        raise ValueError("measurement_hw_model must pin the measurement Mac's hw.model")
    for entry in config["models"].values():
        if set(entry) != {"source"}:
            raise ValueError("model entries contain only source; council pins cannot be overridden")
        _path(entry["source"])
    for key in ("shade_cache", "disk_path", "anchor_source"):
        _path(config[key])
    if not isinstance(config.get("custody_parents"), list):
        raise ValueError("custody_parents must list any extras to the shared default parents")
    for path in config["custody_parents"]:
        _path(path)
    if not isinstance(config.get("offloads", []), list):
        raise ValueError("offloads must list configured W1 offload receipts")
    labels = set()
    for row in config.get("offloads", []):
        if (not isinstance(row, dict) or set(row) != {"label", "inventory", "destination"}
                or not isinstance(row["label"], str) or not row["label"].strip() or row["label"] in labels):
            raise ValueError("offloads require unique nonempty labels, inventory and destination")
        labels.add(row["label"])
        _path(row["inventory"])
        _path(row["destination"])
    return {**config, "smc_step": profile_config(config.get("smc_step"))}


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


DISPLAY_PREP_ENV = "JOULEWISE_R0_DISPLAY_PREP"


def display_summary(report, probe, started_epoch, finished_epoch):
    """R0-L3 display ruling (RUN_STATE 206): record display state; a wake
    during the SMC capture is a flag, never a refusal."""
    raw = os.environ.get(DISPLAY_PREP_ENV)
    try:
        prep = json.loads(raw) if raw else None
    except ValueError:
        prep = {"unparsed": raw}
    display = {"rule": "docs/align/r0/R0-L3-contention-rule.md (RUN_STATE 206)", "launcher_prep": prep,
               "smc_display_wakes": None, "smc_display_wake_flag": None}
    if probe is None:
        display["probed"] = False
    else:
        try:
            display.update(probe(started_epoch, finished_epoch), probed=True)
            windows = [r["wall_window_epoch_s"] for r in report["checks"]
                       if r["check"] == "smc" and r.get("wall_window_epoch_s")]
            wakes = [t for t in display.get("transitions", ()) if t["state"] == "on"
                     and any(begin <= t["epoch_s"] <= end for begin, end in windows)]
            if "pmset_log_error" not in display:
                display.update(smc_display_wakes=wakes, smc_display_wake_flag=bool(wakes))
        except Exception as exc:
            display.update(probed=True, error=f"{type(exc).__name__}: {exc}")
    report["display"] = display


def execute(config, output, checks, models, *, guard, backend_factory, per_check_timeout=7200,
            keep_going=False, long_decode_attempts=2, display_probe=None):
    started_run = time.monotonic()
    started_epoch = time.time()
    # --checks selects a subset, never overrides the fail-fast phase order.
    checks = (["smc"] if "smc" in checks else []) + [name for name in CHECKS if name in checks and name != "smc"]
    report = {"schema": "joulewise.align.r0.report.v1", "status": "running",
              "created_utc": datetime.now(timezone.utc).isoformat(),
              "config": config, "pins": r0.PINS, "checks": [], "complete_r0": False,
              "evidence_kind": "live_desk" if backend_factory.__module__ == "joulewise.align.r0_mlx" else "injected_backend",
              "selected_checks": checks, "selected_models": models,
              "keep_going": keep_going, "long_decode_max_attempts": long_decode_attempts,
              "authority": ("origin/lane/2026-11-05-align-window-council:docs/align/council-2026-11-05/FINAL-DESIGN.md "
                            "§§2.1,2.2,2.8; load NLL bar: authority_load_reference"),
              "authority_commit": "219fb151515383cbbcde887d096837a829c67396",
              "authority_blob": "0a802a3097a20c9f4dd5e8823d858302ae596785",
              "authority_amendment_commit": "6eb1ff5be31bec330ae5af262c2b4c7601e7755e",
              "authority_amendment": "docs/align/council-2026-11-05/FINAL-DESIGN-AMENDMENT-1.md §§A1,A3,A5",
              "authority_step_ruling": "docs/align/r0_step_test_ruling.md (laptop lead, 2026-11-05)",
              # The load NLL bar is per-model reference equivalence, not §2.1's absolute limit.
              "authority_load_reference": LOAD_REFERENCE_NOTE,
              "authority_load_reference_basis": LOAD_REFERENCE_BASIS,
              "limitations": ["Selection data, not R1 thermal or arm validation.",
                              "R1 must freeze token budgets, intercepts and thermal slots.",
                              "Local inventories do not independently authenticate the remote revision."]}
    def contention_summary():
        # R0-L3: contention is recorded, never fatal. Guard flags (every check)
        # and the SMC capture's ruling-8 flag are collected for report.md.
        flags = getattr(guard, "contention_flags", [])
        smc = [r for r in report["checks"] if r["check"] == "smc"]
        report["contention"] = {
            "rule": "docs/align/r0/R0-L3-contention-rule.md",
            "guard_flags": len(flags),
            "flagged_checks": [{"check": r["check"], "model": r.get("model"), "flags": len(r["contention_flags"])}
                               for r in report["checks"] if r.get("contention_flags")],
            "smc_contended": any(r.get("contended") for r in smc),
            "smc_redo": sum(len(r.get("contention_redo") or ()) for r in smc),
            "smc_flagged_intervals": sum(len((r.get("contention") or {}).get("flags", ())) for r in smc)}
    def receipt(name, model, fn, *, incremental=False):
        started = time.monotonic()
        row = {"check": name, **({"model": model} if model else {}), "status": "running"}
        report["checks"].append(row)
        unserializable = []
        flags_before = len(getattr(guard, "contention_flags", []))
        wall_start = time.time()
        def progress(data):
            row.update(data)
            row["check_seconds"] = time.monotonic() - started
            flags = getattr(guard, "contention_flags", [])[flags_before:]
            if flags:
                row["contention_flags"] = list(flags)
            contention_summary()
            report["total_seconds"] = time.monotonic() - started_run
            report["census"] = guard.receipts
            if not unserializable:
                try:
                    save_report(output, report)
                    return
                except (TypeError, ValueError) as exc:  # e.g. NaN/inf under allow_nan=False
                    unserializable.append(f"{type(exc).__name__}: {exc}")
            # The row cannot be recorded as strict JSON: record a fail, never crash or
            # leave the report at running. Stays failed for the rest of this check.
            seconds = row["check_seconds"]
            row.clear()
            row.update({"check": name, **({"model": model} if model else {}), "status": "fail",
                        "reason": "report_serialization_error", "error": unserializable[0],
                        "check_seconds": seconds})
            save_report(output, report)
        def run_unit(fn):
            guard.check(force=True)
            with deadline(per_check_timeout):
                return fn()
        try:
            guard.check(force=True)
            progress({})
            result = fn(progress, run_unit) if incremental else run_unit(fn)
            row.update(result)
            guard.check(force=True)
        except Refused as exc:
            row.update(status="refused", refusal=str(exc))
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
        finally:
            if name == "smc":
                row["wall_window_epoch_s"] = [wall_start, time.time()]
            progress({})
        if name == "smc":
            report["smc_selection_missing"] = row["status"] != "pass"
        if not keep_going and row["status"] not in ACCEPTED_OUTCOMES.get(name, {"pass"}):
            report["stopped_after"] = {"check": name, "model": model, "outcome": row["status"]}
            raise _StopChecks
        return row
    try:
        if long_decode_attempts not in (1, 2):
            raise ValueError("long_decode_attempts must be 1 or 2")
        config = validate_config(config)
        report["config"] = config
        report["smc_step_budget"] = step_budget(config["smc_step"])
        # This guard precedes host probes, file inventories, optional SMC and
        # lazy imports. No model can be opened after a refused initial census.
        guard.check(force=True)
        report["implementation_sha256"] = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), Path(r0.__file__), REPO / "joulewise/align/r0_host.py",
                         REPO / "joulewise/align/r0_mlx.py", REPO / "joulewise/align/r0_step.py",
                         REPO / "scripts/align_r0_checks.py", r0.NLL_REFERENCE_PATH)}
        report["authority_load_reference_blob"] = git_blob_sha1(REPO / LOAD_REFERENCE_NOTE)
        report["config_sha256"] = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
        report["checkout_head"] = command(("git", "-C", str(REPO), "rev-parse", "HEAD")).strip()
        # D3: SMC needs no model and must precede disk's weights hash as
        # well as every model import/load, independently of CHECKS ordering.
        if "smc" in checks:
            receipt("smc", None, lambda: smc_enumeration(REPO, output / "smc", config["smc_step"]))
        for name, fn in (("host", host_snapshot), ("disk", lambda: disk_census(config, r0.PINS, guard.check))):
            if name in checks:
                receipt(name, None, fn)
        model_checks = [c for c in checks if c not in {"host", "disk", "smc"}]
        host_ok = (not model_checks or receipt("host-identity", None,
                   lambda: host_identity(config["measurement_hw_model"]))["status"] == "pass")
        for tag in models:
            backend = None
            model_loaded = False
            try:
                def load_backend():
                    nonlocal backend
                    backend = backend_factory(tag, config["models"][tag]["source"], config["shade_cache"], guard)
                    return backend.device_info()
                functions = {"load": lambda: r0.load_coherence(backend),
                             "template": lambda: r0.template_rewrites(backend),
                             "generated": lambda: r0.generated_rewrites(backend),
                             "ladder": lambda: r0.ladder(backend, tag),
                             "long-decode": lambda: r0.long_decode(backend, max_attempts=long_decode_attempts),
                             "memory": lambda: r0.memory_peak(backend, tag)}
                loaded = None
                for name in (c for c in checks if c not in {"host", "disk", "smc"}):
                    if not host_ok:
                        receipt(name, tag, lambda: {"status": "blocked", "reason": "measurement host identity/capacity gate failed"})
                        continue
                    if loaded is None:
                        loaded = receipt("model-load", tag, load_backend)
                    if loaded["status"] != "pass":
                        receipt(name, tag, lambda: {"status": "blocked", "reason": "model-load prerequisite failed"})
                        continue
                    model_loaded = True
                    composites = {
                        "load": lambda p, u: u(lambda: r0.load_coherence(backend, progress=p)),
                        "generated": lambda p, u: r0.generated_rewrites(backend, progress=p, run_unit=u),
                        "ladder": lambda p, u: r0.ladder(backend, tag, progress=p, run_unit=u),
                        "long-decode": lambda p, u: r0.long_decode(
                            backend, max_attempts=long_decode_attempts, progress=p, run_unit=u),
                    }
                    result = receipt(name, tag, composites.get(name, functions[name]), incremental=name in composites)
                    if name == "generated" and "transitions" in result:
                        receipt("checkpoint", tag, lambda: r0.checkpoint_verdict(tag, result))
                if model_loaded and tag == "D" and any(c in checks for c in ("load", "generated", "ladder")):
                    receipt("tool-envelopes", tag, lambda: r0.tool_envelopes(
                        [row for row in report["checks"] if row.get("model") == "D"]))
            finally:
                if backend is not None:
                    backend.close()
        bad = [r for r in report["checks"] if r["status"] not in ACCEPTED_OUTCOMES.get(r["check"], {"pass"})]
        report["status"] = "fail" if bad else "pass"
        report["complete_r0"] = (set(checks) == set(CHECKS) and set(models) == {"D"}
                                  and not bad and report["evidence_kind"] == "live_desk"
                                  and any(r["check"] == "smc" and r["status"] == "pass"
                                          for r in report["checks"]))
    except _StopChecks:
        report["status"] = "fail"
    except ProfileRefused as exc:
        report.update(status="refused", refusal=str(exc), refusal_code=exc.code)
    except Refused as exc:
        report.update(status="refused", refusal=str(exc))
    except Exception as exc:
        report.update(status="fail", error=f"{type(exc).__name__}: {exc}")
    finally:
        report["decisions_pending_lead_action"] = [
            {"check": row["check"], "model": row.get("model"), "outcome": row["status"]}
            for row in report["checks"] if row["status"] in {"required", "fallback"}]
        report["census"] = guard.receipts
        contention_summary()
        display_summary(report, display_probe, started_epoch, time.time())
        report["total_seconds"] = time.monotonic() - started_run
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        save_report(output, report)
    return report


MACHINE_LOCK = Path("/private/tmp/joulewise-align-r0.lock")


def main(argv=None, *, backend_factory=None, guard_factory=QuietGuard, lock_path=None,
         display_probe=display_census):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new exclusive record directory")
    parser.add_argument("--checks", default=",".join(CHECKS), help="comma-separated: " + ",".join(CHECKS))
    parser.add_argument("--models", default="D", help="D only under Amendment 1")
    parser.add_argument("--timeout", type=int, default=7200,
                        help="seconds per check, or per decode attempt / ladder episode / generated turn")
    parser.add_argument("--keep-going", action="store_true", help="continue after failed checks; prerequisite gates still apply")
    parser.add_argument("--long-decode-attempts", type=int, choices=(1, 2), default=2,
                        help="maximum attempts: one normally, optional metadata retry only after failure (default: 2)")
    parser.add_argument("--inventory", type=Path, help="hash this root only, before offload; output is a new JSON file")
    args = parser.parse_args(argv)
    checks, models = args.checks.split(","), args.models.split(",")
    if (not set(checks) <= set(CHECKS) or set(models) != {"D"}
            or len(checks) != len(set(checks)) or len(models) != len(set(models)) or args.timeout <= 0):
        parser.error("invalid checks, models or timeout")
    try:
        config = validate_config(json.loads(args.config.read_text()))
    except ValueError as exc:
        parser.error(str(exc))
    guard = guard_factory(config["custody_parents"])
    # One per-machine lock, not per output directory. An agent ancestor still
    # refuses: the lock never grants a census exemption.
    lock_path = MACHINE_LOCK if lock_path is None else Path(lock_path)
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
                         backend_factory=backend_factory, per_check_timeout=args.timeout,
                         keep_going=args.keep_going, long_decode_attempts=args.long_decode_attempts,
                         display_probe=display_probe)
        print(f"{report['status']}: {args.output / 'report.json'}; complete_r0={report['complete_r0']}")
        return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
