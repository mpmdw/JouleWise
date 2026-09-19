"""Frozen QPE-01 executor and descriptive reduction; never cutoff authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from joulewise import night_gate

PROTOCOL_PATH = night_gate.QPE01_PILOT_REGISTRATION_PATH
CHAIN_PATH = night_gate.EVIDENCE_CHAIN_PATH
HARNESS_PATHS = ("scripts/sample_quiet_predicate_evidence.py", "joulewise/quiet_admission.py")
MANIFEST_PATHS = (PROTOCOL_PATH, CHAIN_PATH, *HARNESS_PATHS,
                  "joulewise/quiet_predicate_campaign.py", "joulewise/night_gate.py",
                  "joulewise/night_agent_install.py", "scripts/run_night.py")
MANIFEST_SCHEMA = "joulewise.night_evidence_manifest.v1"
RECEIPT_SCHEMA = "joulewise.night_evidence_probe_receipt.v1"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tracked_bytes(root, head, name):
    """A digest attests HEAD's bytes only when the executable file matches too."""
    data = subprocess.run(["/usr/bin/git", "-C", str(root), "show", f"{head}:{name}"],
                          check=True, capture_output=True, timeout=15).stdout
    if (Path(root) / name).read_bytes() != data:
        raise ValueError(f"tracked file differs from measurement_head: {name}")
    return data


def validate_protocol(protocol, source_digest):
    fixed = {"schema": "joulewise.quiet_predicate_pilot.v1", "receipt_class": "DIAGNOSTIC_NO_PACK",
             "window_max_s": 9000, "settle_s": 600, "envelopes": 12, "envelope_s": 600,
             "interior_offset_s": 60, "interior_s": 480, "sample_interval_s": 30,
             "minimum_retained": 8, "load_generator": False,
             "recorder_journal": "evidence_busy_cores.jsonl", "busy_cores_role": "covariate_only",
             "chain_source_sha256": source_digest}
    if not isinstance(protocol, dict) or any(protocol.get(k) != v for k, v in fixed.items()):
        raise ValueError("frozen pilot protocol mismatch; CLI overrides are forbidden")
    return protocol


def manifest_for(plan):
    files = {name: digest(tracked_bytes(plan.measurement_root, plan.measurement_head, name))
             for name in MANIFEST_PATHS}
    raw = (Path(plan.measurement_root) / PROTOCOL_PATH).read_bytes()
    if files[PROTOCOL_PATH] != night_gate.QPE01_PILOT_REGISTRATION_SHA256:
        raise ValueError("protocol is not the ruled pilot registration")
    validate_protocol(json.loads(raw), files[CHAIN_PATH])
    registration = Path(plan.registration_path)
    if not registration.is_absolute():
        registration = Path(plan.measurement_root) / registration
    if registration.resolve() != (Path(plan.measurement_root) / PROTOCOL_PATH).resolve():
        raise ValueError("evidence registration must be the tracked pilot protocol")
    if plan.receipt_class != "DIAGNOSTIC_NO_PACK" or plan.quiet_admission is not None:
        raise ValueError("evidence pilot requires v2 DIAGNOSTIC_NO_PACK")
    if plan.window_max_s != 9000:
        raise ValueError("window_max_s must equal the frozen protocol's 9000 s")
    return {"schema": MANIFEST_SCHEMA, "plan_id": plan.plan_id,
            "measurement_head": plan.measurement_head, "files": files}


def verify_manifest(plan, chain_text):
    if night_gate.probe_payload_kind(chain_text) != "quiet_predicate_evidence":
        raise ValueError("probe receipt kind does not match payload kind")
    manifest_path = Path(night_gate.chain_literal(chain_text, "EVIDENCE_MANIFEST_PATH"))
    if not manifest_path.is_absolute():
        raise ValueError("evidence manifest must be an absolute literal path")
    data = manifest_path.read_bytes()
    sha = digest(data)
    if sha != night_gate.chain_literal(chain_text, "EVIDENCE_MANIFEST_SHA256"):
        raise ValueError("manifest_sha256 mismatch")
    manifest = json.loads(data)
    expected = manifest_for(plan)
    if manifest != expected:
        raise ValueError("manifest per-file digests differ from measurement_head")
    if night_gate.chain_literal(chain_text, "EVIDENCE_CHAIN_SOURCE_SHA256") != expected["files"][CHAIN_PATH]:
        raise ValueError("chain_source_sha256 mismatch")
    return manifest_path, manifest, sha


def verify_environment():
    plan_path = Path(os.environ["EVIDENCE_PLAN_PATH"])
    plan = night_gate.NightPlan.from_mapping(json.loads(plan_path.read_text()))
    if (os.environ.get("NIGHT_PLAN_ID") != plan.plan_id or
            os.environ.get("MEASUREMENT_ROOT") != plan.measurement_root or
            os.environ.get("MEASUREMENT_HEAD") != plan.measurement_head):
        raise ValueError("evidence wrapper environment differs from plan")
    _, manifest, sha = verify_manifest(plan, Path(plan.chain_path).read_text())
    if os.environ.get("EVIDENCE_MANIFEST_SHA256") != sha:
        raise ValueError("evidence manifest environment mismatch")
    # Import checks are read-only; no power, sampler, load or hard probes run.
    from scripts import sample_quiet_predicate_evidence  # noqa: F401
    from joulewise import quiet_admission  # noqa: F401
    return plan, manifest, sha


def append_event(path, event):
    raw = (json.dumps(event, sort_keys=True, allow_nan=False) + "\n").encode()
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        if os.write(descriptor, raw) != len(raw):
            raise OSError("short evidence journal write")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def journal_process(kind, pgid):
    path = os.environ.get("EVIDENCE_PROCESS_JOURNAL")
    if path:
        append_event(Path(path), {"kind": kind, "pgid": pgid, "epoch_s": time.time()})


def group_absent(pgid):
    from scripts.run_night import _group_census
    return _group_census(pgid, timeout_s=.2)[0]


def process_groups(path):
    if not path.exists():
        raise ValueError("evidence process journal missing")
    groups = set()
    for line in path.read_text().splitlines():
        row = json.loads(line)
        pgid = row["pgid"]
        if type(pgid) is not int or pgid <= 1 or pgid == os.getpgrp():
            raise ValueError("unsafe evidence process group identity")
        if row.get("state") == "absent":
            groups.discard(pgid)
        else:
            groups.add(pgid)
    return groups


def cleanup_groups(path, children=(), budget_s=30, exclude=()):
    """One budget for TERM, KILL, reaping and all group censuses; fail closed."""
    deadline = time.monotonic() + budget_s
    term_until = min(deadline, time.monotonic() + min(20, budget_s * .67))
    known, checked, errors = set(), set(), []
    pending = set()
    while time.monotonic() < deadline:
        for child in children:
            child.poll()
        try:
            pending = process_groups(path) - set(exclude)
        except (OSError, ValueError, KeyError) as exc:
            errors.append(str(exc))
            break
        known.update(pending)
        for pgid in sorted(pending):
            if time.monotonic() >= deadline:
                break
            if group_absent(pgid):
                append_event(path, {"kind": "cleanup", "pgid": pgid, "state": "absent"})
                checked.add(pgid)
            else:
                try:
                    os.killpg(pgid, signal.SIGTERM if time.monotonic() < term_until else signal.SIGKILL)
                except ProcessLookupError:
                    pass
                except PermissionError as exc:
                    errors.append(str(exc))
        if pending <= checked:
            # New groups journaled during teardown must be included too.
            if not (process_groups(path) - set(exclude)):
                break
        time.sleep(min(.05, max(0, deadline - time.monotonic())))
    residue = sorted((known - checked) | (process_groups(path) - set(exclude)))
    return {"budget_s": budget_s, "groups": sorted(known), "residue": residue,
            "errors": sorted(set(errors)), "cleanup_proven": not residue and not errors}


def record_covariates(protocol, night_dir):
    from joulewise.quiet_admission import sample_interval
    from scripts.sample_quiet_predicate_evidence import cpu_total
    stop = False
    def stopping(_signum, _frame):
        nonlocal stop
        stop = True
    signal.signal(signal.SIGTERM, stopping)
    journal = night_dir / protocol["recorder_journal"]
    while not stop:
        cpu, began = cpu_total(), time.monotonic()
        try:
            value = sample_interval(protocol["sample_interval_s"])
            row = {"observation": value, "error": None}
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            row = {"observation": None, "error": str(exc)}
        row.update(evidence_status="PROVISIONAL", role="covariate_only", admits_nothing=True,
                   observer_cpu_s=cpu_total() - cpu, monotonic_start=began, monotonic_end=time.monotonic())
        append_event(journal, row)
    return 0


def hard_exclusions(rows):
    """Named mechanisms only. This function never reads busy-core values."""
    import re
    excluded = set()
    if not rows or any(row.get("census_clean") is not True for row in rows):
        excluded.add("census_not_clean_or_unknown")
    for row in rows:
        batches = row.get("hard_probes") or []
        probes = [probe for batch in batches for probe in batch.get("result", [])]
        ac = [p for p in probes if tuple(p.get("argv", [])) == night_gate.PMSET_BATT_ARGV]
        thermal = [p for p in probes if tuple(p.get("argv", [])) == night_gate.THERMAL_ARGV]
        if (row.get("hard_probe_errors") or not ac or any(p.get("exit_code") != 0 or
                "AC Power" not in p.get("stdout", "") for p in ac)):
            excluded.add("ac_not_AC_Power_or_probe_error")
        if row.get("hard_probe_errors") or not thermal:
            excluded.add("CPU_Speed_Limit_below_100_or_thermal_probe_error")
        for probe in thermal:
            limits = [line.strip() for line in probe.get("stdout", "").splitlines()
                      if line.strip().startswith("CPU_Speed_Limit")]
            if probe.get("exit_code") != 0 or any(
                    re.fullmatch(r"CPU_Speed_Limit\s*=\s*\d+", line) is None or
                    int(line.split("=")[1]) < 100 for line in limits):
                excluded.add("CPU_Speed_Limit_below_100_or_thermal_probe_error")
    return sorted(excluded)


def size_block_two(s_upper, delta_j=1):
    import math
    if type(s_upper) not in (float, int) or not math.isfinite(s_upper) or s_upper < 0:
        raise ValueError("s_upper must be a finite nonnegative upper confidence bound")
    return max(3, math.ceil(8 * s_upper ** 2 / delta_j ** 2))


def stop_branch(*, s_upper=None, observer_floor=None, smallest_share=.05, block_two_upper_j=None):
    """Apply only ruled stop conditions; absent evidence is never a pass."""
    import math
    for value in (s_upper, observer_floor, smallest_share, block_two_upper_j):
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
            raise ValueError("stop-branch evidence must be finite and nonnegative")
    causes = []
    pairs = None if s_upper is None else size_block_two(s_upper)
    if pairs is not None and pairs > 24:
        causes.append("sized_pairs_above_24")
    if observer_floor is not None and observer_floor > smallest_share:
        causes.append("observer_floor_above_smallest_holdable_share")
    if block_two_upper_j is not None and block_two_upper_j > 1:
        causes.append("block_two_upper_bound_above_1_J")
    return {"outcome": "no cutoff qualifies" if causes else "no decision", "causes": causes, "pairs": pairs}


def pilot_summary(directory, protocol, envelopes, observer_cpu_s=None):
    """Retain exclusions and unfiltered values; do not infer a confidence model."""
    import statistics
    from scripts import sample_quiet_predicate_evidence as harness
    values, all_rows = [], []
    for entry in envelopes:
        out = directory / f"envelope-{entry['index']:02d}"
        try:
            session = json.loads((out / "session.json").read_text())
            rows = [json.loads(line) for line in (out / "rounds.jsonl").read_text().splitlines() if line]
        except (OSError, ValueError) as exc:
            values.append({**entry, "excluded": ["incomplete_interior_support"], "error": str(exc), "joules": None})
            continue
        all_rows.extend(rows)
        excluded = hard_exclusions(rows)
        interior = session.get("interior", {})
        if (session.get("power") or {}).get("anchor", {}).get("status") != "bounded":
            excluded.append("clock_anchor_unresolved")
        if not interior.get("complete_support"):
            excluded.append("incomplete_interior_support")
        entry = {**entry, "collector_start_drift_s": session.get("start_drift_s")}
        if max(abs(entry["start_drift_s"]), abs(session.get("start_drift_s") or 0)) > protocol["start_drift_max_s"]:
            excluded.append("envelope_start_drift_above_5_s")
        if any(row.get("os_build_valid") is not True or row.get("os_build") != session.get("os_build") or
               row.get("session") != session.get("session") for row in rows):
            raise ValueError("pilot row/session identity mismatch")
        energy = (interior.get("power") or {}).get("energy_j", {})
        values.append({**entry, "excluded": sorted(set(excluded)), "interior": interior,
                       "joules": energy.get("rail_sum_w"), "combined_joules": energy.get("combined_w"),
                       "boot_id": session.get("boot_id"), "os_build": session.get("os_build"),
                       "sw_vers": session.get("sw_vers"), "powermetrics_identity": session.get("powermetrics_identity"),
                       "whole_envelope_observer_cpu_s": session.get("whole_envelope_observer_cpu_s"),
                       "observer_cpu_s": sum(row.get("observer_cpu_s") or 0 for row in rows),
                       "censuses": [{"round": r["round"], "clean": r.get("census_clean")} for r in rows]})
    retained = [v for v in values if not v["excluded"] and v["joules"] is not None]
    deltas = [{"left": a["index"], "right": b["index"], "delta_j": b["joules"] - a["joules"]}
              for a, b in zip(values, values[1:]) if not a["excluded"] and not b["excluded"]
              and a.get("boot_id") == b.get("boot_id") and a.get("os_build") == b.get("os_build")
              and a["joules"] is not None and b["joules"] is not None]
    sufficient = len(retained) >= protocol["minimum_retained"] and len(deltas) >= protocol["minimum_adjacent_pairs"]
    busy = [(r.get("observation") or {}).get("metrics", {}).get("busy_cores") for r in all_rows]
    report = {"schema": "joulewise.quiet_predicate_pilot_summary.v1", "evidence_status": "PROVISIONAL",
        "status": "SPREAD_RECORDED" if sufficient else "INCONCLUSIVE", "envelopes": values,
        "retained": len(retained), "adjacent_pairs": deltas,
        "pair_sd_j": statistics.stdev(d["delta_j"] for d in deltas) if len(deltas) >= 2 else None,
        "single_envelope_sd_j": statistics.stdev(v["joules"] for v in retained) if len(retained) >= 2 else None,
        "max_abs_delta_j": max((abs(d["delta_j"]) for d in deltas), default=None),
        "busy_cores": harness.quantiles(busy), "busy_cores_role": "covariate_only; never excluded",
        "s_upper": None, "s_upper_reason": "confidence construction for dependent adjacent differences requires lead ruling",
        "block_two_pairs": None, "block_two_pairs_reason": "requires the ruled upper 90% confidence bound; no plug-in sizing",
        "whole_campaign_observer_cpu_s": observer_cpu_s,
        "observer_definition": "SELF + reaped CHILDREN, including collector, recorder, sampler and census; never subtracted",
        "cutoff_authority": False, "top_up": False}
    harness.write_json(directory / "summary.json", report)
    (directory / "summary.md").write_text(
        "# QPE-01 pilot (PROVISIONAL, descriptive)\n\n" +
        f"Status: {report['status']}. Retained {len(retained)}/{protocol['envelopes']} envelopes; {len(deltas)} adjacent differences.\n\n" +
        f"Adjacent-pair SD: {report['pair_sd_j']} J. Busy cores are recorded covariates and never an exclusion input.\n\n" +
        "Every exclusion and partial interior is retained in summary.json. No top-up, cutoff or activation authority. " +
        "Block two cannot be sized until the upper 90% confidence construction is ruled.\n")
    return report


def execute(plan, protocol, night_dir):
    """No schedule knobs: all quantities come from the authenticated protocol."""
    from scripts import sample_quiet_predicate_evidence as harness
    night_dir.mkdir(parents=True, exist_ok=True)
    directory = night_dir / "evidence"
    directory.mkdir()  # no overwrite/retry
    journal = night_dir / "evidence_processes.jsonl"
    journal.touch(exist_ok=False)
    env = {**os.environ, "EVIDENCE_PROCESS_JOURNAL": str(journal)}
    children, envelopes = [], []
    outcome, error = "refused", None
    cpu_start = harness.cpu_total()
    go = time.monotonic()
    def interrupted(signum, _frame):
        raise InterruptedError(f"evidence chain signal {signum}")
    old = {s: signal.signal(s, interrupted) for s in (signal.SIGTERM, signal.SIGINT)}
    def launch(kind, argv):
        process = subprocess.Popen(argv, env=env, stdin=subprocess.DEVNULL, start_new_session=True)
        children.append(process)
        append_event(journal, {"kind": kind, "pgid": process.pid, "epoch_s": time.time()})
        return process
    try:
        # Settle belongs inside GO; verify-only never reaches this call.
        print(f"evidence_settle seconds={protocol['settle_s']}", flush=True)
        time.sleep(protocol["settle_s"])
        first = go + protocol["settle_s"]
        recorder = launch("recorder", [sys.executable, "-B", "-m", "joulewise.quiet_predicate_campaign", "record"])
        for index in range(1, protocol["envelopes"] + 1):
            scheduled = first + (index - 1) * protocol["envelope_s"]
            time.sleep(max(0, scheduled - time.monotonic()))
            if time.time() + protocol["envelope_s"] > plan.t0_epoch_s + plan.window_max_s:
                raise ValueError("evidence window exhausted; no compressed envelope or top-up")
            actual = time.monotonic()
            out = directory / f"envelope-{index:02d}"
            collector = launch("collector", [sys.executable, "-B", str(Path(plan.measurement_root) / HARNESS_PATHS[0]),
                "collect", "--state", "idle", "--repeat", str(index), "--duration-s", str(protocol["envelope_s"]),
                "--sample-interval-s", str(protocol["sample_interval_s"]), "--interior-offset-s", str(protocol["interior_offset_s"]),
                "--interior-s", str(protocol["interior_s"]), "--envelope-start-mono-s", str(scheduled), "--power-interval-ms", str(protocol["power_interval_ms"]), "--out", str(out)])
            print(f"envelope_start index={index} collector_pgid={collector.pid} recorder_pgid={recorder.pid}", flush=True)
            try:
                code = collector.wait(timeout=protocol["envelope_s"] + 30)
            except subprocess.TimeoutExpired:
                code = 124
            # The covariate recorder spans all envelopes. Each collector and
            # its independent sampler/power groups must be reaped between slots.
            cleanup = cleanup_groups(journal, children, budget_s=30, exclude={recorder.pid})
            envelopes.append({"index": index, "scheduled_mono_s": scheduled, "actual_mono_s": actual,
                              "start_drift_s": actual - scheduled, "collector_exit": code, "cleanup": cleanup})
            append_event(night_dir / "evidence_envelopes.jsonl", envelopes[-1])
            print(f"envelope_end index={index} rc={code} cleanup_proven={cleanup['cleanup_proven']}", flush=True)
            if not cleanup["cleanup_proven"]:
                raise ValueError("collector/recorder/sampler cleanup unproven")
            if recorder.poll() is not None:
                raise ValueError("evidence covariate recorder exited early")
            if code != 0:
                raise ValueError(f"collector failed with exit {code}; evidence retained")
        outcome = "complete"
    except (OSError, ValueError, KeyboardInterrupt, subprocess.SubprocessError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        for signum in old:
            signal.signal(signum, signal.SIG_IGN)
        cleanup = cleanup_groups(journal, children, budget_s=30)
        try:
            pilot_summary(directory, protocol, envelopes,
                          harness.cpu_total() - cpu_start if cleanup["cleanup_proven"] else None)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            outcome, error = "refused", "pilot summary failed: " + str(exc)
        harness.write_json(night_dir / "evidence_cleanup.json", cleanup)
        harness.write_json(night_dir / "evidence_outcome.json", {"outcome": outcome, "error": error,
            "envelopes_attempted": len(envelopes), "cleanup_proven": cleanup["cleanup_proven"]})
        for signum, handler in old.items():
            signal.signal(signum, handler)
    print(f"evidence_end outcome={outcome} cleanup_proven={cleanup['cleanup_proven']}", flush=True)
    return 0 if outcome == "complete" and cleanup["cleanup_proven"] else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "run", "record"))
    args = parser.parse_args(argv)
    try:
        plan, manifest, sha = verify_environment()
        if args.command == "verify":
            print(f"VERIFY_ONLY_OK manifest={sha}")
            return 0
        if os.environ.get("NIGHT_VERIFY_ONLY") == "1":
            raise ValueError("verify-only mode refuses execution")
        protocol = json.loads((Path(plan.measurement_root) / PROTOCOL_PATH).read_text())
        if args.command == "record":
            return record_covariates(protocol, Path(os.environ["NIGHT_DIR"]))
        return execute(plan, protocol, Path(os.environ["NIGHT_DIR"]))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f"EVIDENCE_REFUSED {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
