"""Pre-session evidence: physics waits, record flags, and certain exclusions.

No collection or ledger writes. Hardware and process actions are injectable.
"""
from __future__ import annotations

import copy
import dataclasses
from fractions import Fraction
import json
import os
from pathlib import Path
import re
import signal
import stat as stat_module
import statistics
from typing import Any, Callable

from joulewise.b5 import chain, plan
from joulewise.b6 import fingerprint, plan_inputs
from joulewise.b6.acceptance_interface import (
    CaptureEvidence, MemberEvidence, StageEvidence, SessionEvidence, load_acceptance,
)
from joulewise.hazards import arm, battery, clock, contention, disk, instrument, smc, thermal
from joulewise.hazards.base import Context, PASS, canonical_json, write_create_once
from scripts import fixture_orphan_census

# Stage-1 integration: the block-6 registration directory (acceptance.json,
# identity_pins.json, sizing_b5.json), the same one the smoke desk and the
# session harvest read; see joulewise.b6.registration.DEFAULT_DIR_RELATIVE.
REGISTRATION_RELATIVE = "configs/b6/registration"
PENDING = ("closing_capture", "sleep", "clock_steps_in_runs", "actual_losses")
HID_ARGV = ("/usr/sbin/ioreg", "-c", "IOHIDSystem", "-d", "4", "-r", "-k", "HIDIdleTime")
ASSERTIONS_ARGV = ("/usr/bin/pmset", "-g", "assertions")
POWER_CUSTOM_ARGV = ("/usr/bin/pmset", "-g", "custom")
ANALYSIS_ARGV = ("/bin/ps", "-Ao", "pid,ppid,%cpu,comm")
ANALYSIS_NAMES = {"mediaanalysisd", "photoanalysisd", "corespotlightd", "mds_stores", "mdworker", "photolibraryd"}
PRECHECK_DEFAULTS = {
    "clock": {**clock.DEFAULT_THRESHOLDS, **plan_inputs.CLOCK_THRESHOLDS,
              "series_min_s": 60, "retry_after_s": 600},
    "battery": {**battery.DEFAULT_THRESHOLDS, "limit_ma": 200},
    "thermal": {**thermal.DEFAULT_THRESHOLDS, "max_level": 0},
    "contention": {**contention.DEFAULT_THRESHOLDS, "cpu_limit_s_per_s": 0.05,
                   "interval_s": 30, "clean_s": 180, "cap_s": 600},
    "agents": {"hid_idle_min_s": 600},
    "disk": {"largest_session_bytes": 43 * disk.GIB, "headroom_bytes": 20 * disk.GIB,
             "smoke_bytes": 6 * 190_840_832 * 2},
    "instrument": dict(instrument.DEFAULT_THRESHOLDS),
    "capture_median_count": 24, "margin_loss_runs": 8, "retry_after_s": 300,
}


def thresholds_for(measurement_root, pack_id, registration_dir, overrides=None):
    result = copy.deepcopy(PRECHECK_DEFAULTS)
    sizing = Path(registration_dir) / "sizing_b5.json"
    try:
        packs = json.loads(sizing.read_text())["packs"]
        aliases = {"d117_floor_qwen3-1p7b_v5": "ALPHA", "d117_floor_qwen3-8b_v5": "BETA",
                   "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5": "GAMMA"}
        sized = packs.get(pack_id, packs.get(aliases.get(pack_id), {}))["T_stream_max_s"]
        result["clock"]["t_stream_max_s"] = sized
    except (OSError, ValueError, KeyError, TypeError):
        pass
    registered = Path(registration_dir) / "precheck_thresholds.json"
    layers = []
    if registered.exists():
        layers.append(json.loads(registered.read_text()))
    layers.append(overrides or {})
    for layer in layers:
        for key, value in layer.items():
            if key not in result:
                raise ValueError(f"unknown precheck threshold {key}")
            if isinstance(result[key], dict):
                if not isinstance(value, dict) or set(value) - set(result[key]):
                    raise ValueError(f"unknown or malformed {key} thresholds")
                result[key].update(value)
            else:
                result[key] = value
    return result


def ledger_rows(path, *, flags=None) -> list:
    """The sole adapter to the current ledger; observations only, never custody reads."""
    from joulewise import calibration_ledger
    try:
        receipts, errors = calibration_ledger._parse_ledger(Path(path).read_bytes())
        if errors and flags is not None:
            flags.append({"code": "precheck.ledger_unreadable", "source": "ledger",
                          "observed": ", ".join(sorted(errors))})
        observations, sessions, _ = calibration_ledger._attempts_and_observations(receipts)
        return sorted(calibration_ledger._custody_observations(observations, sessions),
                      key=lambda row: row.sequence)
    except Exception as exc:
        if flags is not None:
            flags.append({"code": "precheck.ledger_unreadable", "source": "ledger",
                          "observed": f"{type(exc).__name__}: {exc}"})
        return []


def _value(row, key, default=None):
    return row.get(key, default) if isinstance(row, dict) else getattr(row, key, default)


def restore_evicted(rows, measurement_root, *, ctx, lstat=os.lstat,
                    poll_s=5, cap_s=600) -> tuple[dict, list[dict]]:
    files = set()
    for row in rows:
        locator = Path(_value(row, "custody_locator", ""))
        if not locator.is_absolute():
            locator = Path(measurement_root) / locator
        for relative in _value(row, "artifact_sha256", {}):
            files.add(locator / relative)

    missing = set()

    def unavailable(path):
        try:
            item = lstat(path)
            return bool(getattr(item, "st_flags", 0) & 0x40000000)
        except OSError:
            missing.add(path)
            return True

    pending = set()
    unavailable_files = set()
    downloads = []
    for path in sorted(files):
        try:
            item = lstat(path)
        except OSError:
            missing.add(path)
            continue
        if getattr(item, "st_flags", 0) & 0x40000000:
            unavailable_files.add(path)
            if not stat_module.S_ISDIR(getattr(item, "st_mode", 0)):
                result = ctx.run(("/usr/bin/brctl", "download", str(path)), ctx.probe_timeout_s)
                ctx.keep_raw(f"eviction-{len(downloads)}.txt", result.stdout)
                downloads.append({"file": str(path), "returncode": result.returncode,
                                  "error": result.error, "timed_out": result.timed_out})
                pending.add(path)
    elapsed = 0
    downloaded = set(pending)
    pending = {path for path in pending if unavailable(path) and path not in missing}
    while pending and elapsed < cap_s:
        duration = min(poll_s, cap_s - elapsed)
        ctx.clocks.sleep(duration)
        elapsed += duration
        pending = {path for path in pending if unavailable(path) and path not in missing}
    pending |= missing | (unavailable_files - downloaded)
    flags = ([{"code": "calibration.historical_custody_unmeasured", "source": "evicted_captures",
               "observed": {"count": len(pending), "files": sorted(map(str, pending))}}] if pending else [])
    return {"files_checked": len(files), "downloads": downloads,
            "unavailable": sorted(map(str, pending)), "missing": sorted(map(str, missing)), "elapsed_s": elapsed}, flags


def _process_uid(ctx, pid):
    result = ctx.run(("/bin/ps", "-o", "uid=", "-p", str(pid)), ctx.probe_timeout_s)
    return int(result.stdout.strip()) if result.ok and result.stdout.strip().isdigit() else None


def reap_orphans(ctx, *, collect=fixture_orphan_census.collect, kill=os.kill,
                 process_uid=None, uid=None) -> dict:
    """Only registered ppid-1 fixtures owned by this uid may be signalled."""
    rows = []
    try:
        matches = collect()
    except Exception as exc:
        return {"rows": [], "error": f"{type(exc).__name__}: {exc}"}
    owner = os.getuid() if uid is None else uid
    process_uid = process_uid or (lambda pid: _process_uid(ctx, pid))
    for row in matches:
        if row.get("ppid") != 1 or process_uid(row["pid"]) != owner:
            continue
        entry = {"pid": row["pid"], "signature": row["signature"], "outcome": "gone"}
        try:
            kill(row["pid"], signal.SIGTERM)
            ctx.clocks.sleep(5)
            try:
                again = collect()
            except Exception as exc:
                entry["outcome"] = f"sigterm_sent; recensus failed: {type(exc).__name__}: {exc}"
                rows.append(entry)
                continue
            if any(match.get("pid") == row["pid"] and match.get("signature") == row["signature"]
                   and match.get("ppid") == 1 for match in again):
                kill(row["pid"], signal.SIGKILL)
                entry["outcome"] = "sigkill_sent"
        except ProcessLookupError:
            pass
        except OSError as exc:
            entry["outcome"] = f"{type(exc).__name__}: {exc}"
        rows.append(entry)
    return {"rows": rows, "error": None}


def model_files(tree, measurement_root, pins, *, identity=None) -> tuple[dict, list[str]]:
    from joulewise.provenance import model_artifact_identity
    identity = identity or model_artifact_identity
    expected = {_value(unit, "model_source"): _value(unit, "model_artifact_sha256")
                for unit in pins.get("units", {}).values() if _value(unit, "model_source")}
    sources = set()
    errors = []
    for dispatch in plan.resolve_stage_dispatches(tree, measurement_root):
        if dispatch.error:
            errors.append(f"plan.dispatch_unresolved: {dispatch.stage_id}: {dispatch.error}")
            continue
        manifest = json.loads((Path(measurement_root) / dispatch.config_dir / "order_manifest.json").read_text())
        for entry in manifest["executed_order"]:
            config = json.loads((Path(measurement_root) / dispatch.config_dir / entry["config"]).read_text())
            source = config.get("model", {}).get("source")
            if source:
                sources.add(source)
    measured = {}
    for source in sorted(sources):
        try:
            artifact = identity(source)
            measured[source] = artifact.get("folded_sha256") or artifact.get("sha256")
        except Exception:
            measured[source] = None
        if measured[source] is None:
            errors.append(f"model.identity_unmeasured: {source}")
        elif not expected.get(source):
            errors.append(f"model.source_unpinned: {source}")
        elif measured[source] != expected[source]:
            errors.append(f"model.hash_mismatch: {source}")
    return {"expected": expected, "measured": measured}, errors


def runtime_versions(measurement_root, pins, *, ctx) -> dict:
    packages = sorted(pins.get("runtime_versions", {}).get("packages", {}))
    source = ("import importlib.metadata as m,json,platform,sys\n"
              "versions={}\n"
              "for name in json.loads(sys.argv[1]):\n"
              " try: versions[name]=m.version(name)\n"
              " except m.PackageNotFoundError: versions[name]=None\n"
              "print(json.dumps({'python':platform.python_version(),'packages':versions}))\n")
    result = ctx.run((str(Path(measurement_root) / ".venv/bin/python"), "-I", "-c", source,
                      json.dumps(packages)), ctx.probe_timeout_s)
    ctx.keep_raw("runtime-versions.json", result.stdout)
    try:
        versions = json.loads(result.stdout) if result.ok else None
        if not isinstance(versions, dict) or not isinstance(versions.get("packages"), dict):
            raise ValueError("runtime probe malformed")
        return {"python": versions.get("python"),
                "packages": {name: versions["packages"].get(name) for name in packages}}
    except ValueError:
        return {"python": None, "packages": {name: None for name in packages}}


def synthetic_session(pack_root, measurement_root, rows, runtime, *, capture_median_count=24):
    tree = json.loads((Path(pack_root) / "plan_tree.json").read_text())
    dispatches = {row.stage_id: row for row in plan.resolve_stage_dispatches(tree, measurement_root)}
    stages = []
    for stage in chain.stage_plan(tree):
        members = ()
        if stage.kind == "campaign_collection":
            dispatch = dispatches[stage.stage_id]
            if dispatch.error or dispatch.run_ids is None:
                raise ValueError(f"plan.dispatch_unresolved: {dispatch.stage_id}: {dispatch.error}")
            members = tuple(MemberEvidence(stage.stage_id, run_id, "succeeded")
                            for run_id in dispatch.run_ids[:stage.expected_count])
        stages.append(StageEvidence(stage.stage_id, stage.kind, stage.expected_count, members))
    valid = sorted((row for row in rows if _value(row, "disposition") == "valid"),
                   key=lambda row: _value(row, "sequence"))[-capture_median_count:]
    bounds = [Fraction(str(_value(row, "exact_bound_lexeme_s"))) * 1000 for row in valid]
    bound = float(statistics.median(bounds)) if bounds else None
    captures = tuple(CaptureEvidence(slot, bound, "valid" if bounds else "absent", True)
                     for slot in ("pre", "post"))
    return SessionEvidence(Path(pack_root).name, tuple(stages), captures, runtime, True, PENDING)


def acceptance_checks(acceptance, prepared, evidence, *, margin_loss_runs=8):
    nominal = acceptance.evaluate(prepared, evidence)
    flags = [{"code": code, "source": "acceptance_nominal", "observed": None} for code in nominal.flags]
    if nominal.verdict == "UNAVAILABLE":
        flags.append({"code": "precheck.acceptance_unavailable", "source": "acceptance", "observed": None})
        return {"status": "unavailable"}, None, None, flags
    exclusion = ({"source": "acceptance_nominal", "reasons": list(nominal.reasons)}
                 if nominal.verdict == "EXCLUDE" else None)
    flat = [member for stage in evidence.stages for member in stage.members]
    offset = 0
    excluding = []
    placements = 0
    for stage in evidence.stages:
        if stage.kind != "campaign_collection":
            continue
        lost = {(member.stage_id, member.run_id) for member in flat[offset:offset + margin_loss_runs]}
        altered = dataclasses.replace(evidence, stages=tuple(dataclasses.replace(
            item, members=tuple(dataclasses.replace(member, status="failed")
                                if (member.stage_id, member.run_id) in lost else member
                                for member in item.members)) for item in evidence.stages))
        result = acceptance.evaluate(prepared, altered)
        if result.verdict == "EXCLUDE":
            excluding.append(stage.stage_id)
        offset += len(stage.members)
        placements += 1
    return ({"status": "available", "nominal": dataclasses.asdict(nominal)},
            {"status": "thin" if excluding else "ok", "excluding_placements": excluding,
             "placements": placements}, exclusion, flags)


def clock_rate(samples, boot_start, boot_end, thresholds):
    """Fit measured anchors with exact rational arithmetic; f is diagnostic only."""
    usable = [item["anchor"] for item in samples if not item.get("error") and item.get("anchor")
              and 0 <= item["anchor"].get("read_skew_ns", -1) <= clock.WINDOW_SKEW_MAX_NS]
    codes = []
    reading = {"samples": samples, "boot_start": boot_start, "boot_end": boot_end,
               "rate_ppm": None, "kernel_frequency_ppm": None, "rate_minus_frequency_ppm": None}
    if boot_start is None or boot_end is None:
        codes.append("clock.unmeasured")
    elif boot_start != boot_end:
        codes.append("clock.boot_changed")
    if len(usable) < 50 or (usable[-1]["monotonic_raw_ns"] - usable[0]["monotonic_raw_ns"]
                            < Fraction(str(thresholds["series_min_s"])) * 10**9):
        return reading, list(dict.fromkeys([*codes, "clock.unmeasured"]))
    origin = usable[0]["monotonic_raw_ns"]
    xs = [Fraction(item["monotonic_raw_ns"] - origin) for item in usable]
    ys = [Fraction(item["anchor_ns"]) for item in usable]
    xm, ym = sum(xs) / len(xs), sum(ys) / len(ys)
    slope = sum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / sum((x - xm)**2 for x in xs)
    rate = slope * 10**6
    residuals = [y - ym - slope * (x - xm) for x, y in zip(xs, ys)]
    # Registration §8.6: 5 ms / T_stream_max - 0.25 ppm, using the
    # same exact hold arithmetic as hazards.clock.frequency_bound.
    bound = Fraction(str(thresholds["h_ms"])) + (abs(rate) + Fraction(
        str(thresholds["frequency_margin_ppm"]))) * Fraction(str(thresholds["t_stream_max_s"])) / 1000
    if bound > Fraction(str(thresholds["limit_ms"])):
        codes.append("clock.rate")
    elif thresholds["h_ms"] == 0 and (bound + Fraction(str(clock.DEFAULT_THRESHOLDS["h_ms"]))
                                        > Fraction(str(thresholds["limit_ms"]))):
        codes.append("clock.rate_above_budget")
    if max(map(abs, residuals)) > thresholds["residual_max_ns"]:
        codes.append("clock.linearity")
    if any(abs(b - a) > thresholds["step_ns"] for a, b in zip(residuals, residuals[1:])):
        codes.append("clock.step")
    frequency = next((item["frequency"] for item in samples if item.get("frequency")), None)
    f = Fraction(frequency["raw_word"], clock.FREQUENCY_SCALE) if frequency else None
    reading.update(rate_ppm=float(rate), bound_ms=float(bound), residual_max_ns=float(max(map(abs, residuals))),
                   kernel_frequency_ppm=float(f) if f is not None else None,
                   rate_minus_frequency_ppm=float(rate - f) if f is not None else None)
    return reading, list(dict.fromkeys(codes))


def power_and_idle(ctx):
    readings = {}
    for key, argv in (("assertions", ASSERTIONS_ARGV), ("custom", POWER_CUSTOM_ARGV), ("hid", HID_ARGV)):
        result = ctx.run(argv, ctx.probe_timeout_s)
        ctx.keep_raw(f"power-{key}.txt", result.stdout)
        readings[key] = {"stdout": result.stdout.decode("utf-8", errors="replace"), "ok": result.ok}
    assertion = readings["assertions"]
    readings["assertion_held"] = assertion["ok"] and bool(re.search(
        r'\b(?:PreventSystemSleep|PreventUserIdleSystemSleep)\s+1\b', assertion["stdout"]))
    idle = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', readings["hid"]["stdout"])
    readings["hid_idle_s"] = int(idle.group(1)) / 1e9 if idle and readings["hid"]["ok"] else None
    return readings


@dataclasses.dataclass
class Seams:
    lstat: Callable = os.lstat
    statvfs: Callable = os.statvfs
    stat: Callable = os.stat
    kill: Callable = os.kill
    orphan_collect: Callable = fixture_orphan_census.collect
    process_uid: Callable | None = None
    smc_read: Callable | None = smc.read_once
    frequency_reader: Callable = clock.read_frequency
    boot_reader: Callable = clock.read_boot_session
    host_reader: Callable | None = contention.read_host_cpu
    instrument_executable: str = instrument.POWERMETRICS
    instrument_privilege_prefix: tuple = instrument.PRIVILEGE_PREFIX
    fingerprint_collect: Callable = fingerprint.collect
    model_identity: Callable | None = None


def decision(result):
    return "DO_NOT_START" if result["certain_exclusion"] else "WAIT" if result["would_refuse"] else "START"


def exit_code(result):
    return {"START": 0, "WAIT": 10, "DO_NOT_START": 20}[result["decision"]]


def _default_disk_measurement(ctx, measurement, state_root, seams):
    # largest_session_bytes is the total writes (including copies), not a
    # per-copy bundle allowance. Budget it once on each destination volume.
    targets = []
    for target in (Path(measurement), Path(state_root) / "runs-parent", Path(state_root) / "custody",
                   Path(state_root) / "backup-claim", Path(state_root) / "backup-bound"):
        while True:
            try:
                seams.stat(str(target))
                break
            except FileNotFoundError:
                if target.parent == target:
                    break
                target = target.parent
        targets.append({"path": str(target), "copies": 0})
    reading = disk.measure(ctx, targets=targets, statvfs=seams.statvfs, stat=seams.stat)
    seen = set()
    rows = []
    for row in reading.values["targets"]:
        row = dict(row)
        device = row.get("device")
        if device is not None and device not in seen:
            row["copies"] = 1
            seen.add(device)
        rows.append(row)
    return dataclasses.replace(reading, values={"targets": rows})


def run_precheck(pack_id, measurement_root, state_root, *, out=None, ledger=None,
                 registration_dir=None, thresholds=None, ctx=None, seams=None, acceptance=None,
                 disk_targets=None, reap=True):
    measurement = Path(measurement_root)
    registration = Path(registration_dir or measurement / REGISTRATION_RELATIVE)
    ledger = Path(ledger or measurement / plan.DEFAULT_LEDGER_RELATIVE)
    pack_root = measurement / "configs/campaigns" / pack_id
    if out is not None and Path(out).exists():
        raise FileExistsError(out)
    ctx = ctx or Context(raw_dir=Path(out).parent / "precheck-raw" if out else None,
                         label=Path(out).stem if out else "")
    if ctx.raw_dir is not None:
        original_run = ctx.run
        probe_index = 0

        def recorded_run(argv, timeout_s):
            nonlocal probe_index
            index = probe_index
            probe_index += 1
            probe = original_run(argv, timeout_s)
            ctx.keep_raw(f"probe-{index:04d}.stdout", probe.stdout)
            ctx.keep_raw(f"probe-{index:04d}.stderr", probe.stderr)
            return probe

        ctx = dataclasses.replace(ctx, run=recorded_run)
    seams = seams or Seams()
    limits = thresholds_for(measurement, pack_id, registration, thresholds)
    started = ctx.stamp()
    tree = json.loads((pack_root / "plan_tree.json").read_text())
    pin_error = None
    try:
        from joulewise.b6.registration import load_identity_pins
        pins = load_identity_pins(registration)
    except (OSError, ValueError) as exc:
        pins, pin_error = {}, type(exc).__name__
    # These values feed the fingerprint and disk smoke budget, so obtain them
    # before that decision; all slow work remains ahead of the physics dwell.
    models, model_errors = model_files(tree, measurement, pins, identity=seams.model_identity)
    runtime = runtime_versions(measurement, pins, ctx=ctx)
    fp = seams.fingerprint_collect(measurement, pack_id, models["measured"], runtime, ctx=ctx)
    smoke, reason = fingerprint.smoke_required(fp, Path(state_root) / "smoke-passes.jsonl")
    result = {"schema": "joulewise.b6_precheck.v1", "pack_id": pack_id, "started": started.to_json(),
              "would_refuse": [], "certain_exclusion": None, "margin": None, "acceptance": {},
              "predicted_flags": [], "pending": list(PENDING), "fingerprint": fp,
              "fingerprint_sha256": fingerprint.digest(fp), "smoke_required": smoke,
              "smoke_reason": reason, "readings": {"model_files": models}}
    flags, readings = result["predicted_flags"], result["readings"]
    if pin_error:
        flags.append({"code": "model.identity_unpinned", "source": "identity_pins", "observed": pin_error})

    def wait(code, hazard, observed, limit, remedy="wait_and_remeasure", retry=None):
        result["would_refuse"].append({"code": code, "hazard": hazard, "observed": observed,
                                      "limit": limit, "retry_after_s": limits["retry_after_s"] if retry is None else retry,
                                      "remedy": remedy})

    def judged(module, measurement, threshold, code, remedy="wait_and_remeasure"):
        verdict = module.judge(measurement, threshold)
        readings[module.MODULE] = {"measurement": measurement.to_json(), "verdict": verdict.to_json()}
        if verdict.status != PASS:
            wait(code, module.MODULE, verdict.to_json(), threshold, remedy)
        for flag in verdict.observed.get("flags", []):
            flags.append({"code": flag["code"], "source": module.MODULE, "observed": flag})

    if fp.get("code_dirty"):
        flags.append({"code": "code.executed_differs_from_sealed", "source": "fingerprint", "observed": True})
    if fp.get("meter_device") is None:
        flags.append({"code": "meter.absent", "source": "fingerprint", "observed": None})
    rows = ledger_rows(ledger, flags=flags)
    readings["evicted_captures"], eviction_flags = restore_evicted(rows, measurement, ctx=ctx, lstat=seams.lstat)
    flags.extend(eviction_flags)
    disk_limits = {"planned_bytes": limits["disk"]["largest_session_bytes"] + (
        limits["disk"]["smoke_bytes"] if smoke else 0), "headroom_bytes": limits["disk"]["headroom_bytes"]}
    disk_reading = (disk.measure(ctx, targets=disk_targets, statvfs=seams.statvfs, stat=seams.stat)
                    if disk_targets is not None else _default_disk_measurement(ctx, measurement, state_root, seams))
    judged(disk, disk_reading,
           disk_limits, "disk.low", "wake_orchestrator")
    if reap:
        readings["orphans_killed"] = reap_orphans(ctx, collect=seams.orphan_collect, kill=seams.kill,
                                                process_uid=seams.process_uid)
    else:
        try:
            readings["orphans_observed"] = {"rows": seams.orphan_collect(), "error": None}
        except Exception as exc:
            readings["orphans_observed"] = {"rows": [], "error": type(exc).__name__}
    mismatches = [reason for reason in model_errors if reason.startswith(
        ("model.hash_mismatch:", "plan.dispatch_unresolved:"))]
    if mismatches:
        result["certain_exclusion"] = {"source": "plan" if any(reason.startswith("plan.")
            for reason in mismatches) else "model_hash", "reasons": mismatches}
    for reason in model_errors:
        if reason not in mismatches:
            code = reason.split(":", 1)[0]
            flags.append({"code": "roster.dispatch_unresolved" if code == "plan.dispatch_unresolved" else code,
                          "source": "model_files", "observed": reason})
    try:
        evidence = synthetic_session(pack_root, measurement, rows,
                                     {"model_hashes": models["measured"], "runtime_versions": runtime},
                                     capture_median_count=limits["capture_median_count"])
    except ValueError as exc:
        if not str(exc).startswith("plan.dispatch_unresolved:"):
            raise
        result["acceptance"] = {"status": "skipped", "reason": str(exc)}
    else:
        if evidence.captures[0].bound_ms is None:
            flags.append({"code": "precheck.no_valid_capture", "source": "ledger", "observed": 0})
        acceptance = acceptance or load_acceptance()
        # Stage-1 integration: the harvest lane's acceptance reads the block-6
        # acceptance registration (<registration_dir>/acceptance.json and
        # identity_pins.json) and compares the executed commit with the
        # registered one. A registration it cannot read is a record condition,
        # not physics: the precheck records it and goes on, as with the stub.
        code_identity = {**fp, "repo_root": str(measurement), "executed_head": fp.get("code_commit")}
        try:
            prepared = acceptance.prepare(ledger_path=ledger, plan_tree=tree, registration_dir=registration,
                                          code_identity=code_identity, pack_root=pack_root)
        except Exception as exc:  # noqa: BLE001 - recorded; the precheck never stops on a record
            result["acceptance"] = {"status": "unavailable",
                                    "reason": f"acceptance registration unreadable: {type(exc).__name__}"}
            flags.append({"code": "precheck.acceptance_unavailable", "source": "acceptance",
                          "observed": {"error": type(exc).__name__, "registration_dir": str(registration)}})
        else:
            result["acceptance"], result["margin"], exclusion, acceptance_flags = acceptance_checks(
                acceptance, prepared, evidence, margin_loss_runs=limits["margin_loss_runs"])
            flags.extend(acceptance_flags)
            result["certain_exclusion"] = result["certain_exclusion"] or exclusion
    judged(battery, battery.measure(ctx, smc_read=seams.smc_read), limits["battery"], "battery.float")
    judged(thermal, thermal.measure(ctx), limits["thermal"], "thermal.pressure")
    first = arm.agent_census(ctx)
    readings["agents"] = {"initial": first}
    if not first["clean"]:
        wait("agents.present", "agents", first, "empty")
    readings["power"] = power_and_idle(ctx)
    power = readings["power"]
    if power["hid_idle_s"] is None or power["hid_idle_s"] < limits["agents"]["hid_idle_min_s"]:
        # HID inactivity has no joule derivation; measured idle admission judges the hazard.
        flags.append({"code": "agents.hid_recent", "source": "agents", "observed": power["hid_idle_s"]})
    if not power["assertion_held"]:
        wait("power.no_sleep_assertion_absent", "power", power["assertions"], "assertion held")
    readings["time_server"] = []
    for server in ("time.apple.com", "pool.ntp.org"):
        probe = ctx.run(("/usr/bin/sntp", "-t", "5", server), 6)
        ctx.keep_raw(f"time-{server}.txt", probe.stdout)
        readings["time_server"].append({"argv": list(probe.argv), "returncode": probe.returncode,
                                       "stdout": probe.stdout.decode("utf-8", errors="replace"),
                                       "stderr": probe.stderr.decode("utf-8", errors="replace"),
                                       "error": probe.error, "timed_out": probe.timed_out})
    analysis = ctx.run(ANALYSIS_ARGV, ctx.probe_timeout_s)
    ctx.keep_raw("analysis-agents.txt", analysis.stdout)
    readings["analysis_agents"] = {"ok": analysis.ok, "rows": [line for line in analysis.stdout.decode(
        "utf-8", errors="replace").splitlines() if line.split() and Path(line.split()[-1]).name in ANALYSIS_NAMES]}
    judged(instrument, instrument.measure(ctx, executable=seams.instrument_executable,
                                          privilege_prefix=seams.instrument_privilege_prefix),
           limits["instrument"], "instrument.cadence", "relaunch_in_production_context")
    samples = []

    def boot():
        try:
            return seams.boot_reader(ctx)
        except (OSError, ValueError):
            return None

    boot_start = boot()
    try:
        kernel_frequency = dict(seams.frequency_reader())
    except (OSError, ValueError):
        kernel_frequency = None
    dwell = contention.run_dwell(ctx, limits["contention"], tree_roots=(os.getpid(),),
                                on_tick=lambda: samples.append(clock.sample(
                                    ctx, frequency_reader=None)), host_reader=seams.host_reader)
    if samples:
        samples[0]["frequency"] = kernel_frequency
    judged(contention, dwell, limits["contention"], "contention.dwell")
    readings["clock"], clock_codes = clock_rate(samples, boot_start, boot(), limits["clock"])
    ctx.keep_raw("clock-series.json", canonical_json(readings["clock"]))
    for code in clock_codes:
        if code == "clock.rate_above_budget":
            flags.append({"code": code, "source": "clock", "observed": readings["clock"]})
        elif code == "clock.rate":
            flags.append({"code": "clock.rate_hold", "source": "clock", "observed": readings["clock"]})
            wait("clock.rate_hold", "clock", readings["clock"], limits["clock"],
                 remedy="wake_orchestrator", retry=0)
        else:
            wait(code, "clock", readings["clock"], limits["clock"], retry=limits["clock"]["retry_after_s"])
    final = arm.agent_census(ctx)
    readings["agents"]["final"] = final
    if not final["clean"]:
        wait("agents.present", "agents", final, "empty")
    result["finished"] = ctx.stamp().to_json()
    result["decision"] = decision(result)
    if out is not None:
        write_create_once(Path(out), canonical_json(result) + b"\n")
    return result
