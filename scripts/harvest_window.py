#!/usr/bin/env python3
"""Harvest finished derivation evidence, without inspecting capture bounds.

Publish one archive directory containing custody-root/, measurement-runs/ and
harvest.json. No source, ledger pin, verdict file or Git metadata is changed.
Every window must have an authenticated committed battery verdict before harvest.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import issue_calibration_acceptance_generation as issuer
from scripts import cap_replay_harness
from scripts.calibration_cadence_report import native_intervals_ms, STOP_THRESHOLD_MS
from joulewise import battery_float
from joulewise.calibration_ledger import artifact_hashes, load_calibration_ledger_snapshot
from joulewise.measurement_liveness import census as measurement_census
from joulewise.night_gate import NightPlan, PlanError


class HarvestRefusal(ValueError):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def inventory(root):
    """Do not follow symlinks; retain original mode and nanosecond timestamps."""
    rows = {}
    for path in [root, *sorted(root.rglob("*"))]:
        st = path.lstat()
        row = {"mode": st.st_mode, "size": st.st_size, "mtime_ns": st.st_mtime_ns}
        if path.is_symlink():
            row["link"] = os.readlink(path)
        elif path.is_file():
            row["sha256"] = digest(path.read_bytes())
        elif not path.is_dir():
            raise HarvestRefusal("unsupported evidence file type")
        rows[path.relative_to(root).as_posix()] = row
    return rows


def copy_matches(original, copied):
    # Directory sizes are filesystem dependent; file sizes, modes, timestamps
    # and bytes (and literal symlink targets) must survive the courier.
    def comparable(rows):
        return {name: {k: v for k, v in row.items()
                       if k != "size" or "sha256" in row or "link" in row}
                for name, row in rows.items()}
    return comparable(original) == comparable(copied)


def coordinates(plan, night_root):
    wrapper = Path(plan.chain_path)
    raw = wrapper.read_bytes()
    sidecar = Path(plan.chain_sha256_path).read_text().split()
    if len(sidecar) != 2 or sidecar[0] != digest(raw) or sidecar[1] != wrapper.name:
        raise HarvestRefusal("wrapper authentication failed")
    exports = {}
    for line in raw.decode().splitlines():
        if line.startswith("export "):
            parts = shlex.split(line)
            if len(parts) != 2 or "=" not in parts[1]:
                raise HarvestRefusal("nonliteral wrapper export")
            key, value = parts[1].split("=", 1)
            if key in exports:
                raise HarvestRefusal("duplicate wrapper export")
            exports[key] = value
    for name in ("SESSION_ID", "PLAN", "PLAN_ID", "PLAN_SHA256", "RUNS_ROOT",
                 "CALIBRATION_LEDGER", "LEDGER_HEAD_PIN", "WINDOW_CUSTODY_ROOT"):
        if not exports.get(name):
            raise HarvestRefusal("wrapper coordinates incomplete")
    if Path(exports["WINDOW_CUSTODY_ROOT"]) != night_root:
        raise HarvestRefusal("wrapper custody root mismatch")
    calibration_raw = Path(exports["PLAN"]).read_bytes()
    if (digest(calibration_raw) != exports["PLAN_SHA256"]
            or json.loads(calibration_raw).get("plan_id") != exports["PLAN_ID"]):
        raise HarvestRefusal("calibration plan authentication failed")
    return exports


def r9_window(session, battery_status, *, ledger_reasons=None):
    """Replay blind work fields; ledger disposition remains the count authority."""
    counting = battery_status == "pass"
    captures = []
    stops = set()
    for number, slot in enumerate(session.declared_slots, 1):
        observation = session.finalized_slots.get(slot)
        if observation is None:
            continue  # An unused slot has no capture identity or recording.
        recording = bool(observation.artifact_sha256.get("raw/powermetrics.plist"))
        replay = {"cells": None, "median_frame_ms": None, "ratio": None,
                  "disposition": "not_replayed", "trigger": None}
        if recording:
            for attempt in range(3):
                replay = cap_replay_harness.replay_capture(
                    Path(observation.custody_locator), "REPORT", compare_stored_bound=False)
                if replay["trigger"] != "wall_deadline":
                    break
            else:
                raise HarvestRefusal("wall-deadline replay failed after three attempts; no capture finding")
            if replay.get("replay_failed") and replay["median_frame_ms"] is not None:
                raise HarvestRefusal("capture replay failed; no capture finding")
        cells, frame, ratio = (replay[key] for key in ("cells", "median_frame_ms", "ratio"))
        if not recording:
            cells, frame, ratio = None, None, None
        frame_reported = (not isinstance(frame, bool) and isinstance(frame, (int, float))
                          and math.isfinite(frame) and frame > 0)
        if not frame_reported:
            frame = None
        search_ran = isinstance(cells, int) and not isinstance(cells, bool) and cells >= 1
        trigger = replay["trigger"] if recording else None
        if recording and not frame_reported:
            stops.add("STOP-R9-FRAME")
        captures.append({"slot": number, "capture_id": observation.attempt_id,
                         "content_id": observation.content_id, "has_recording": recording,
                         "cells": cells, "median_frame_ms": frame, "ratio": ratio,
                         "disposition": observation.classification_disposition,
                         "replay_disposition": replay["disposition"],
                         "ledger_reason": (ledger_reasons or {}).get(observation.attempt_id),
                         "cap_trigger": trigger,
                         "median_frame_reported": frame_reported,
                         "counted": bool(counting and recording and search_ran
                                         and frame_reported and 100 <= frame <= 150)})
    record = {"schema": "joulewise.revision6.r9_window.v1", "session_id": session.session_id,
            "slots": len(session.declared_slots), "captures": captures,
            "counted": sum(row["counted"] for row in captures),
            "valid": sum(row.classification_disposition == "valid"
                         for row in session.finalized_slots.values()) if counting else 0,
            "harness_sha256": digest(Path(cap_replay_harness.__file__).read_bytes()),
            "rule_ref": "CAP-COUNCIL-25G83-01 R9 as amended; Revision 6 §4"}
    if not session.finalized_slots:
        record["abort_reason"] = session.abort_reason
    return record, sorted(stops)


def window_end(raw):
    """Amendment T uses the chain exit instant, never harvest write time."""
    exit_record = json.loads(raw)
    if not isinstance(exit_record, dict):
        raise HarvestRefusal("chain exit timing is malformed")
    epoch, monotonic_ns = exit_record.get("epoch_s"), exit_record.get("monotonic_ns")
    if (isinstance(epoch, bool) or not isinstance(epoch, (int, float))
            or not math.isfinite(epoch) or epoch < 0
            or isinstance(monotonic_ns, bool) or not isinstance(monotonic_ns, int)
            or monotonic_ns < 0):
        raise HarvestRefusal("chain exit timing is malformed")
    return {"epoch_s": float(epoch), "monotonic_s": monotonic_ns / 1_000_000_000,
            "source": {"path": "night/chain.exited", "sha256": digest(raw)}}


def capture_rows(session, *, battery, r9_captures=None):
    """Authenticate all finalized captures, including non-valid dispositions.

    Call the issuer's primary-byte and clock seams and the battery-verdict
    replay. Never access the ledger's bound lexeme or any evidence bound field.
    """
    if session.session_kind != "derivation" or session.state not in {"finalized", "aborted"}:
        raise HarvestRefusal("session is not a finished derivation window")
    if not session.finalized_slots:
        raise HarvestRefusal("window has no finalized captures")
    if session.state == "finalized" and set(session.finalized_slots) != set(session.declared_slots):
        raise HarvestRefusal("finalized capture inventory is incomplete")
    battery_by_slot = {row.slot: row for row in battery.slots}
    captures = []
    seen = set()
    for slot, observation in session.finalized_slots.items():
        path = Path(observation.custody_locator)
        if path in seen:
            raise HarvestRefusal("duplicate capture custody")
        seen.add(path)
        evidence, manifest = issuer._read_member_evidence(observation)
        hashes = artifact_hashes(path)
        # Revision 6 reports sampler loss/mismatch through STOP-R9-FRAME;
        # all other primary evidence still has to authenticate normally.
        sampler = "raw/powermetrics.plist"
        if any(hashes.get(name) != expected for name, expected in observation.artifact_sha256.items()
               if r9_captures is None or name != sampler):
            raise HarvestRefusal("capture authentication failed")
        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, dict) or not artifacts:
            raise HarvestRefusal("capture manifest lacks artifact fingerprints")
        for name, expected in artifacts.items():
            if (not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts
                    or ((r9_captures is None or name != sampler) and hashes.get(name) != expected)
                    or observation.artifact_sha256.get(name) != expected):
                raise HarvestRefusal("manifest authentication failed")
        if ("instrument_evidence.json" not in artifacts
                or (r9_captures is None and sampler not in artifacts)):
            raise HarvestRefusal("capture manifest is incomplete")
        if r9_captures is None:
            median_frame = statistics.median(native_intervals_ms((path / sampler).read_bytes()))
        else:
            median_frame = r9_captures[observation.attempt_id]["median_frame_ms"]
        resolved, _ = issuer.anchor_v3_replay_outcome(evidence)
        # Independent check of the recorded booleans omitted by the frozen
        # battery validator. Replay and compare, rather than trusting passed.
        checks = []
        stored_battery = evidence.get("battery_float", {})
        for phase in ("pre", "post"):
            stored = stored_battery.get(phase, {})
            checks.append(stored.get("probe_error") is False and stored.get("passed") is True)
        valid = observation.classification_disposition == "valid"
        retained = (valid and resolved
                 and battery.status == "pass" and all(checks))
        if r9_captures is not None:
            retained = retained and median_frame is not None and 100 <= median_frame <= 150
        captures.append({"slot": slot, "attempt_id": observation.attempt_id,
                         "cadence": ("UNREPORTED" if median_frame is None else
                                     "STOP" if median_frame > STOP_THRESHOLD_MS else "CONTINUE"),
                         "median_native_frame_ms": median_frame,
                         "clock": "resolved" if resolved else "unresolved",
                         "battery": battery_by_slot[slot].verdict,
                         "battery_raw_sha256": {"pre": battery_by_slot[slot].pre_raw_sha256,
                                                "post": battery_by_slot[slot].post_raw_sha256},
                         "probe_error_false": [stored_battery.get(p, {}).get("probe_error") is False for p in ("pre", "post")],
                         "passed_true": [stored_battery.get(p, {}).get("passed") is True for p in ("pre", "post")],
                         "manual_crosscheck": "pass" if all(checks) else "fail",
                         "valid": valid, "retained": retained})
    return captures, battery.status


def next_window(plan, preregistration, sessions):
    """Only apply Revision 5's existing prose rule when the plan names it.

    Current diagnostic night plans point to D-166, which has no derivation
    count rule. Do not infer a rule from a caller's registration argument.
    """
    registered = Path(plan.registration_path) if plan.registration_path else None
    if registered is not None and not registered.is_absolute():
        registered = Path(plan.measurement_root) / registered
    if registered is None or registered.resolve() != preregistration.resolve():
        if registered is not None:
            registration = json.loads(registered.read_bytes())
            if not isinstance(registration, dict):
                raise HarvestRefusal("plan registration is not an object")
            if any("count_rule" in key or "stopping_rule" in key for key in registration):
                raise HarvestRefusal("plan registration count rule is unsupported; lead ruling required")
        return {"verdict": "COUNTS_ONLY", "reason": "plan_has_no_derivation_count_rule"}
    text = preregistration.read_text()
    revision = text.split("# Revision 5 (", 1)[-1].split("# Revision 5 — Amendment", 1)[0]
    minimum = re.search(r"fewer than (\d+) valid of (\d+), stop: no W2", revision)
    target = re.search(r"W3 is permitted only if .*?after W2 shows fewer than (\d+) valid", revision)
    threshold = re.search(r"per-capture median native frame lengths is above (\d+) ms, stop: no W2", revision)
    if not all((minimum, target, threshold)):
        raise HarvestRefusal("plan registration count rule is unsupported; lead ruling required")
    if any(row["battery"] != "pass" or row["manual_crosscheck"] != "pass" for row in sessions):
        return {"verdict": "NO_GO", "reason": "battery_replacement_ruling_required"}
    if len(sessions) == 1:
        row = sessions[0]
        go = (row["declared"] == int(minimum[2]) and row["valid"] >= int(minimum[1])
              and row["median_of_capture_medians_ms"] <= int(threshold[1]))
        return {"verdict": "GO" if go else "NO_GO", "next": "W2"}
    if len(sessions) == 2:
        return {"verdict": "GO" if sum(row["valid"] for row in sessions) < int(target[1]) else "NO_GO",
                "next": "W3"}
    return {"verdict": "COUNTS_ONLY", "reason": "no_registered_post_W3_count_rule"}


def harvest(args, *, runner=subprocess.run, census=measurement_census, now=time.time):
    plan_path = args.plan.resolve()
    plan_raw = plan_path.read_bytes()
    plan = NightPlan.from_mapping(json.loads(plan_raw))
    night_root = Path(plan.custody_root)
    root = Path(plan.measurement_root)
    destination = args.custody.resolve()
    sources = (night_root, root / "runs")
    if any(destination == source or source in destination.parents or destination in source.parents
           for source in sources):
        raise HarvestRefusal("archive overlaps source evidence")
    if plan_path.parent != night_root or now() <= plan.t0_epoch_s + plan.window_max_s + 300:
        raise HarvestRefusal("window completion boundary has not passed")
    if not (night_root / "night/courier.sent").is_file():
        raise HarvestRefusal("window delivery or termination evidence missing")
    if not census(parents=[night_root.parent]).clear:
        raise HarvestRefusal("measurement ownership is not clear")
    source_inventories = {name: inventory(source) for name, source in zip(("custody-root", "measurement-runs"), sources)}
    exports = coordinates(plan, night_root)
    runs_root = Path(exports["RUNS_ROOT"])
    if not any(runs_root == source or source in runs_root.parents for source in sources):
        raise HarvestRefusal("window captures fall outside archived evidence roots")
    head = runner(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False, timeout=10)
    if head.returncode or head.stdout.strip() != plan.measurement_head:
        raise HarvestRefusal("measurement HEAD mismatch")
    preregistration = args.preregistration.resolve()
    if digest(preregistration.read_bytes()) != args.preregistration_sha256:
        raise HarvestRefusal("pre-registration authentication failed")
    start_path = night_root / "night/start_conditions.json"
    revision6 = "# Revision 6 (" in preregistration.read_text()
    declaration = issuer.revision_six_declaration(preregistration.read_text()) if revision6 else None
    if plan.registration_path:
        registered = Path(plan.registration_path)
        if not registered.is_absolute():
            registered = root / registered
        registered_raw = registered.read_bytes()
        if ("# Revision 6 (" in registered_raw.decode() or revision6) and digest(registered_raw) != args.preregistration_sha256:
            raise HarvestRefusal("Revision 6 plan registration digest disagrees with harvest")
    start_raw = None
    start = {}
    end = None
    r9_record, stop_flags = None, []
    if start_path.is_file() and revision6:
        start_raw = start_path.read_bytes()
        if digest(start_raw) != source_inventories["custody-root"]["night/start_conditions.json"].get("sha256"):
            raise HarvestRefusal("window timing evidence changed during authentication")
        start = json.loads(start_raw)
        if (not isinstance(start, dict)
                or start.get("schema") != "joulewise.revision6.start_conditions.v1"
                or start.get("session_id") != exports["SESSION_ID"]
                or start.get("result") not in {"admitted", "refused"}):
            raise HarvestRefusal("Revision 6 start conditions disagree with window")
    exit_path = night_root / "night/chain.exited"
    if exit_path.is_file():
        end_raw = exit_path.read_bytes()
        if digest(end_raw) != source_inventories["custody-root"]["night/chain.exited"].get("sha256"):
            raise HarvestRefusal("window timing evidence changed during authentication")
        end = window_end(end_raw) if revision6 else None
    elif not revision6:
        raise HarvestRefusal("window termination evidence missing")
    snapshot = load_calibration_ledger_snapshot(
        Path(exports["CALIBRATION_LEDGER"]), Path(exports["LEDGER_HEAD_PIN"]),
        require_committed_pin=True, verify_custody=False, mode="read_replay", repo_root=root)
    issuer.refuse_ledger(snapshot)
    ids = args.session_ids or [exports["SESSION_ID"]]
    if len(ids) != len(set(ids)) or ids[-1] != exports["SESSION_ID"]:
        raise HarvestRefusal("session inventory must end with this window and contain no duplicates")
    if all(session_id in snapshot.bracket_session_by_id for session_id in ids) and ids != sorted(
            ids, key=lambda session_id: snapshot.bracket_session_by_id[session_id].capability_sequence):
        raise HarvestRefusal("registration sessions are not in ledger order")
    if revision6:
        ordered = issuer.revision_six_sessions(snapshot, ids, declaration)
        prior_sessions = [session for session in ordered if session.session_id != exports["SESSION_ID"]]
        count_records = issuer.revision_six_records(getattr(args, "prior_harvest_record", ()),
            prior_sessions, declaration, repo_root=root) if prior_sessions else {}
        ledger_reasons = {row.attempt_id: snapshot.receipts[row.sequence - 1].get("reason_code",
                          snapshot.receipts[row.sequence - 1].get("disposition")) for row in snapshot.observations}
    session_rows = []
    adverse_ids = set()
    for session_id in ids:
        session = snapshot.bracket_session_by_id.get(session_id)
        if session is None:
            raise HarvestRefusal("registered session missing")
        if session_id == exports["SESSION_ID"] and (
                session.plan_id != exports["PLAN_ID"] or session.plan_sha256 != exports["PLAN_SHA256"]
                or session.runs_root != exports["RUNS_ROOT"]):
            raise HarvestRefusal("window ledger bindings mismatch")
        if any(Path(row.custody_locator).parent != Path(session.runs_root) / "instrument_validation"
               for row in session.finalized_slots.values()):
            raise HarvestRefusal("capture custody locator disagrees with session")
        # The committed verdict governs counts; harvest is a consumer, not
        # another producer. Authenticate before replaying any window capture.
        null = revision6 and not session.finalized_slots
        if revision6 and session_id == exports["SESSION_ID"] and not null:
            if not start_raw or start.get("result") != "admitted" or end is None:
                raise HarvestRefusal("recorded window requires admitted start and chain exit")
        if null:
            authenticated_battery = None
            battery_record = {"status": "null_session"}
            captures, battery = [], "null_session"
        else:
            authenticated_battery = battery_float.authenticate_committed_verdict(
                root, session=session, preregistration_sha256=args.preregistration_sha256)
            battery_record = json.loads(json_bytes(asdict(authenticated_battery)))
            if battery_record["status"] != "pass":
                adverse_ids.add(session_id)
        r9_captures = None
        if revision6:
            if session_id == exports["SESSION_ID"]:
                r9_record, stop_flags = r9_window(session, battery_record["status"], ledger_reasons=ledger_reasons)
                count_records[session_id] = {"r9": r9_record}
            r9_captures = {row["capture_id"]: row for row in count_records[session_id]["r9"]["captures"]}
        if not null:
            captures, battery = capture_rows(session, battery=authenticated_battery, r9_captures=r9_captures)
        disposition_valid = sum(row["valid"] for row in captures)
        # Independently count the snapshot's observation inventory, rather
        # than relying solely on the capture traversal's accumulator.
        ledger_valid = len([row for row in snapshot.observations
                            if row.bracket_session_id == session_id
                            and row.classification_disposition == "valid"])
        if ledger_valid != disposition_valid:
            raise HarvestRefusal("independent ledger arithmetic disagrees")
        medians = [row["median_native_frame_ms"] for row in captures
                   if row["median_native_frame_ms"] is not None]
        session_rows.append({"session_id": session_id, "declared": len(session.declared_slots),
                             "filled": len(captures), "valid": disposition_valid if battery == "pass" else 0,
                             "disposition_valid": disposition_valid, "independent_count_check": "pass",
                             "retained": sum(row["retained"] for row in captures),
                             "battery": battery, "captures": captures,
                             "battery_verdict": battery_record,
                             "manual_crosscheck": "pass" if all(row["manual_crosscheck"] == "pass" for row in captures) else "fail",
                             "median_of_capture_medians_ms": statistics.median(medians) if medians else None})
    # Reuse the exact count-only path behind check --session-ids, including
    # the committed-verdict gate; never call candidate/statistics code.
    if revision6:
        replay = issuer.revision_six_count_replay(ordered, count_records, declaration, adverse_ids)
        decision = {"verdict": replay["decision"], "sessions": replay["sessions"],
                    "counted": replay["counted"], "members": replay["members"]}
        stop_flags = replay["sessions"][-1]["stops"]
        code, lines = (0 if replay["decision"] in {"NEXT_WINDOW", "CLOSE_AND_DERIVE"} else 5), []
    else:
        code, lines = issuer.registration_dry_run(snapshot, ids, repo_root=root,
                                                 preregistration_sha256=args.preregistration_sha256)
    for row in session_rows:
        pattern = re.compile(re.escape(row["session_id"]) + r": kind=\S+ state=\S+ terminal=yes declared=(\d+) filled=(\d+) valid=(\d+)")
        matches = [pattern.match(line) for line in lines if pattern.match(line)]
        if matches and tuple(map(int, matches[0].groups())) != (row["declared"], row["filled"], row["valid"]):
            raise HarvestRefusal("independent count cross-check disagrees")
    if any(inventory(source) != source_inventories[name] for name, source in zip(source_inventories, sources)):
        raise HarvestRefusal("source changed during authentication")
    record = {"schema": "joulewise.harvest_window.v1", "plan_id": plan.plan_id,
              "harvest_tool_sha256": digest(Path(__file__).read_bytes()),
              "plan_sha256": digest(plan_raw), "measurement_head": plan.measurement_head,
              "preregistration_sha256": args.preregistration_sha256,
              "ledger_head": {"sequence": snapshot.head_sequence, "head_digest": snapshot.head_digest},
              "sessions": session_rows, "valid_captures": sum(row["valid"] for row in session_rows),
              "retained_captures": sum(row["retained"] for row in session_rows),
              "registration_check": {"exit_code": code, "admissible": code == 0},
              "next_window": (next_window(plan, preregistration, session_rows) if not revision6 else
                              decision),
              "inventory": source_inventories, "uninstall": {"exit_code": 0}}
    if revision6:
        r9_raw = json_bytes(r9_record)
        record.update(custody_root=str(destination / "custody-root"),
                      r9_window={"path": "harvest/r9_window.json", "sha256": digest(r9_raw)},
                      window_end=end, boot_id=start.get("boot_id"), stop_flags=stop_flags,
                      next_window_sha256=digest(json_bytes(decision)))
        if start_raw is not None:
            record["start_conditions"] = {"path": "night/start_conditions.json", "sha256": digest(start_raw)}
        if not snapshot.bracket_session_by_id[exports["SESSION_ID"]].finalized_slots:
            record["abort_reason"] = snapshot.bracket_session_by_id[exports["SESSION_ID"]].abort_reason
    # A completed retry validates the immutable archive rather than rerunning
    # the installer or overwriting a record.
    if destination.exists():
        if revision6 and (destination / "custody-root/harvest/r9_window.json").read_bytes() != r9_raw:
            raise HarvestRefusal("existing R9 record differs; refusing overwrite")
        if (destination / "harvest.json").read_bytes() != json_bytes(record) or any(
                not copy_matches(rows, {path: row for path, row in inventory(destination / name).items()
                                       if not revision6 or name != "custody-root" or
                                       (path in rows or path not in {"harvest", "harvest/r9_window.json"})})
                for name, rows in source_inventories.items()):
            raise HarvestRefusal("existing harvest differs; refusing overwrite")
        return record
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Reserve a sibling lock before staging; two harvests cannot both uninstall
    # and then race publication. Only this session's temporary data is removed.
    lock = destination.with_name(destination.name + ".harvest-lock")
    lock.mkdir()
    try:
        with tempfile.TemporaryDirectory(prefix=".harvest-", dir=destination.parent) as temporary:
            stage = Path(temporary) / "archive"
            stage.mkdir()
            for name, source in zip(source_inventories, sources):
                shutil.copytree(source, stage / name, symlinks=True)
                if (inventory(source) != source_inventories[name]
                        or not copy_matches(source_inventories[name], inventory(stage / name))):
                    raise HarvestRefusal("source changed or courier copy disagrees")
            if revision6:
                r9_path = stage / "custody-root/harvest/r9_window.json"
                if r9_path.parent.is_symlink():
                    raise HarvestRefusal("R9 directory escapes staged custody")
                r9_path.parent.mkdir(exist_ok=True)
                with open(r9_path, "xb") as handle:
                    handle.write(r9_raw)
                    handle.flush()
                    os.fsync(handle.fileno())
                # Adding derived evidence must preserve copied source directory
                # timestamps, including the root used by immutable retry checks.
                for directory in (r9_path.parent, stage / "custody-root"):
                    relative = directory.relative_to(stage / "custody-root")
                    source = night_root / relative
                    if source.is_dir():
                        st = source.stat()
                        os.utime(directory, ns=(st.st_atime_ns, st.st_mtime_ns))
            with open(stage / "harvest.json", "xb") as handle:
                handle.write(json_bytes(record))
                handle.flush()
                os.fsync(handle.fileno())
            if not census(parents=[night_root.parent]).clear:
                raise HarvestRefusal("measurement ownership changed before uninstall")
            result = runner([str(root / "scripts/install_night_agent.sh"), "--plan", str(plan_path), "--uninstall"],
                            cwd=root, capture_output=True, text=True, check=False, timeout=120)
            if result.returncode:
                raise HarvestRefusal("existing uninstall path failed; harvest not published")
            os.rename(stage, destination)
    finally:
        lock.rmdir()
    return record


def main(argv=None, **injected):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--custody", type=Path, required=True, help="new archive directory outside watchdog discovery")
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--preregistration-sha256", required=True)
    parser.add_argument("--prior-harvest-record", type=Path, action="append", default=[],
                        help="committed harvest record for each preceding Revision 6 session")
    parser.add_argument("--session-ids", action="append", help="ordered cumulative sessions; repeat flag; current window last")
    args = parser.parse_args(argv)
    try:
        record = harvest(args, **injected)
    except HarvestRefusal as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 3
    except (OSError, ValueError, PlanError, issuer.PrepareRefusal, battery_float.CustodyFailure,
            battery_float.BatteryVerdictRefusal, subprocess.SubprocessError):
        # Primary-file parse errors may include measured content. Never echo it.
        print("REFUSED: harvest authentication, completion, custody or uninstall failed", file=sys.stderr)
        return 3
    print(f"valid_captures={record['valid_captures']} next_window={record['next_window']['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
