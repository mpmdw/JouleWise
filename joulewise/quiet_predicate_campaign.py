"""Frozen QPE-01 executor and descriptive reduction; never cutoff authority."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

from joulewise import night_gate
from joulewise.arm_readiness import EXPECTED_NETWORK_TIME_OFF_STDOUT

PROTOCOL_PATH = night_gate.QPE01_PILOT_REGISTRATION_PATH
CHAIN_PATH = night_gate.EVIDENCE_CHAIN_PATH
# Absolute executables, resolved through module constants (cold gate
# 2026-09-22, ruling 10 Q1 rules 1 and 4, 14 R4).  The production argv strings
# are exactly the NOPASSWD sudoers slice's two set forms and the unified-log
# reader; the zsh ``log`` builtin shadows /usr/bin/log and returns nothing, so
# the absolute path is load-bearing, not cosmetic.  A test substitutes its own
# executables by rebinding these names -- PATH cannot fake an absolute path --
# and a regression pins the production values.
SUDO = "/usr/bin/sudo"
SYSTEMSETUP = "/usr/sbin/systemsetup"
LOG = "/usr/bin/log"
NETWORK_TIME_CONTROL_SCHEMA = "joulewise.network_time_control.v1"
NETWORK_TIME_CONTROL_BASENAME = "network_time_control.json"
NETWORK_TIME_RECORD_ENV = "EVIDENCE_NETWORK_TIME_RECORD"
TIMED_LOG_BASENAME = "timed-log.txt"
TIMED_LOG_ATTESTATION_METHOD = "timed_log_show_predicate_v1"
# ``timed`` writes one of these whenever it APPLIES a correction: a slewed
# frequency/offset adjustment (``cmd,apply,src,``), the adjtime syscall, or a
# hard step.  They are emitted at level Df, which plain ``log show`` drops --
# hence ``--info --debug`` (ruling 14 R4 NIT: without them the scanner would
# silently attest every envelope).
TIMED_LOG_MARKERS = ("cmd,apply,src,", "ntp_adjtime", "settimeofday")
TIMED_LOG_PREDICATE = 'process == "timed"'
NETWORK_TIME_SLEW_EXCLUSION = "network_time_slew_attested"
NETWORK_TIME_UNATTESTED_EXCLUSION = "network_time_unattested"
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


def frozen_protocol(raw=None):
    """The byte-pinned registration is the single source of protocol values."""
    if raw is None:
        raw = (Path(__file__).resolve().parents[1] / PROTOCOL_PATH).read_bytes()
    if digest(raw) != night_gate.QPE01_PILOT_REGISTRATION_SHA256:
        raise ValueError("protocol is not the ruled pilot registration")
    return json.loads(raw)


def cadence_fields(protocol):
    """Refuse a registration that cannot express the ruled cadence.

    Cure 2 (A269 ruling 10 Q1(c)) separates the SCHEDULE PITCH from the
    CAPTURE LENGTH: each envelope is spawned ``slot_pitch_s`` after the last,
    captures for ``envelope_s``, and the difference is the gap in which the
    collector exits, its groups are reaped and the clock attestation runs.  A
    pitch shorter than the capture would schedule the next spawn inside the
    running one, which is the defect A269 cures; a spawn whose drift exceeds
    ``start_drift_abort_s`` aborts the night, so an abort threshold above the
    exclusion bar ``start_drift_max_s`` would let a night run past the point
    where every envelope it produced is already excluded.  Both are refused
    here, fail-closed, before any collector exists.
    """

    for name in ("slot_pitch_s", "start_drift_abort_s", "envelope_s", "start_drift_max_s"):
        value = protocol.get(name)
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"frozen pilot protocol needs a positive {name}")
    if protocol["slot_pitch_s"] < protocol["envelope_s"]:
        raise ValueError("slot_pitch_s is shorter than envelope_s: the schedule would overlap captures")
    if protocol["start_drift_abort_s"] > protocol["start_drift_max_s"]:
        raise ValueError("start_drift_abort_s above start_drift_max_s: the night would run on excluded envelopes")
    return protocol


def validate_protocol(protocol, source_digest):
    cadence_fields(protocol)
    if protocol != frozen_protocol() or protocol.get("chain_source_sha256") != source_digest:
        raise ValueError("frozen pilot protocol mismatch; CLI overrides are forbidden")
    return protocol


def manifest_for(plan):
    contents = {name: tracked_bytes(plan.measurement_root, plan.measurement_head, name)
                for name in MANIFEST_PATHS}
    files = {name: digest(raw) for name, raw in contents.items()}
    protocol = frozen_protocol(contents[PROTOCOL_PATH])
    validate_protocol(protocol, files[CHAIN_PATH])
    registration = Path(plan.registration_path)
    if not registration.is_absolute():
        registration = Path(plan.measurement_root) / registration
    if registration.resolve() != (Path(plan.measurement_root) / PROTOCOL_PATH).resolve():
        raise ValueError("evidence registration must be the tracked pilot protocol")
    if plan.receipt_class != "DIAGNOSTIC_NO_PACK" or plan.quiet_admission is not None:
        raise ValueError("evidence pilot requires v2 DIAGNOSTIC_NO_PACK")
    if plan.window_max_s != protocol["window_max_s"]:
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


def groups_absent(pgids):
    """Absence for every journaled group from ONE census (A269 brief 7).

    The teardown used to spawn one ``pgrep`` per journaled group; after
    twelve envelopes that is 113 spawns, ~1.6 s of the 20 s inter-envelope
    gap, for a question one ``pgrep -g a,b,c`` answers in 14 ms.  A single
    group still takes the single-group path, so nothing about the one-group
    case changes.  Returns {pgid: absent}; a census that could not answer
    reports False (present), never absence.
    """

    pgids = sorted(set(pgids))
    if len(pgids) <= 1:
        return {pgid: group_absent(pgid) for pgid in pgids}
    from scripts.run_night import _group_census_batch
    return {pgid: absent for pgid, (absent, _) in
            _group_census_batch(pgids, timeout_s=.2).items()}


def process_groups(path):
    if not path.exists():
        return set()  # A pre-execute refusal launched no supervised children.
    groups = set()
    for line in path.read_text().splitlines():
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError("invalid evidence process journal row")
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
    known, checked, errors, signal_errors = set(), set(), [], []
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
        # ONE census for the whole sweep (A269 brief 7): the kill decision for
        # every group in this pass reads the same answer, and a group that
        # exits between the census and its own kill is proven absent by the
        # next sweep, exactly as a per-group census would have proven it.
        census = groups_absent(pending)
        for pgid in sorted(pending):
            if time.monotonic() >= deadline:
                break
            try:
                if census.get(pgid, False):
                    append_event(path, {"kind": "cleanup", "pgid": pgid, "state": "absent"})
                    checked.add(pgid)
                else:
                    os.killpg(pgid, signal.SIGTERM if time.monotonic() < term_until else signal.SIGKILL)
            except ProcessLookupError:
                pass  # Only the next census can prove absence.
            except PermissionError as exc:
                signal_errors.append(f"pgid={pgid}: {exc}")
            except OSError as exc:
                errors.append(str(exc))
        if pending <= checked:
            # New groups journaled during teardown must be included too.
            try:
                if not (process_groups(path) - set(exclude)):
                    break
            except (OSError, ValueError, KeyError) as exc:
                errors.append(str(exc))
                break
        time.sleep(min(.05, max(0, deadline - time.monotonic())))
    try:
        pending = process_groups(path) - set(exclude)
    except (OSError, ValueError, KeyError) as exc:
        errors.append(str(exc))
    residue = sorted((known - checked) | pending)
    return {"budget_s": budget_s, "groups": sorted(known), "residue": residue,
            "signal_errors": sorted(set(signal_errors)),
            "errors": sorted(set(errors)), "cleanup_proven": not residue and not errors}


def cleanup_record(night_dir, children=()):
    """Executor or courier writes once; every later reader uses that outcome."""
    import fcntl
    from scripts.sample_quiet_predicate_evidence import write_json
    path = night_dir / "evidence_cleanup.json"
    with (night_dir / "evidence_cleanup.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not path.exists():
            write_json(path, cleanup_groups(night_dir / "evidence_processes.jsonl", children, budget_s=30))
        return json.loads(path.read_text())


def write_refusal(night_dir, plan, detail):
    from scripts.run_night import _write_driver_refusal
    night_dir.mkdir(parents=True, exist_ok=True)
    return _write_driver_refusal(night_dir / "refusal.json", plan, "night_probe_error",
                                 "evidence chain refused: " + detail)


def network_time_argv(state):
    """The exact set form of the NOPASSWD sudoers slice; nothing is inferred."""
    return (SUDO, "-n", SYSTEMSETUP, "-setusingnetworktime", state)


def set_network_time(state):
    """Run one set form and return its receipt: argv, code, stdout, both clocks."""
    argv = network_time_argv(state)
    completed = subprocess.run(list(argv), capture_output=True, text=True, timeout=30)
    return {"argv": list(argv), "exit_code": completed.returncode, "stdout": completed.stdout,
            "epoch_s": time.time(), "monotonic_s": time.monotonic()}


def establish_network_time_off(night_dir):
    """Turn network time OFF before settle, or refuse the night (Q1 rules 1-3).

    The method identity of the evidence anchor makes network-time-OFF the
    structural exclusion of the one window in which the wall clock can move
    non-affinely; a capture taken with it ON or unknown is validation-only
    material, not evidence.  The receipt is written BEFORE the verdict so a
    refused attempt is still on the record, and the exact stdout comparator is
    imported from ``joulewise.arm_readiness``, never retyped.  Returns the
    path of the receipt for the collectors' environment.
    """

    path = night_dir / NETWORK_TIME_CONTROL_BASENAME
    off = set_network_time("off")
    write_control_record(path, {"schema": NETWORK_TIME_CONTROL_SCHEMA, "off": off, "on": None})
    if off["exit_code"] != 0 or off["stdout"] != EXPECTED_NETWORK_TIME_OFF_STDOUT:
        raise ValueError("network time OFF not established: "
                         f"exit {off['exit_code']}, stdout {off['stdout']!r}")
    return path


def write_control_record(path, control):
    path.write_text(json.dumps(control, sort_keys=True, indent=2, allow_nan=False) + "\n")


def restore_network_time(night_dir):
    """Turn network time back ON, on every path; report, never hide, failure.

    Runs as the first action of the executor's ``finally`` (after the signal
    handlers are neutralised), so a refusal, an exception and a SIGTERM all
    leave the machine as they found it.  The READ form is outside the sudoers
    slice, so the prior state is unknowable without a password and ON is the
    ruled end state.  A failed restore does NOT invalidate the envelopes
    already captured under a proven OFF: it is reported as
    ``network_time_restored: false`` and a distinct exit code.
    """

    path = night_dir / NETWORK_TIME_CONTROL_BASENAME
    try:
        control = json.loads(path.read_text())
    except (OSError, ValueError):
        control = {"schema": NETWORK_TIME_CONTROL_SCHEMA, "off": None}
    try:
        on = set_network_time("on")
    except Exception as exc:  # noqa: BLE001 - see below
        # This runs in the executor's ``finally``.  Whatever the restore hits,
        # the night's outcome document and refusal must still be written and
        # the condition reported; a traceback escaping here would replace a
        # measured outcome with no outcome at all.
        on = {"argv": list(network_time_argv("on")), "exit_code": None, "stdout": None,
              "error": f"{type(exc).__name__}: {exc}", "epoch_s": None, "monotonic_s": None}
    control["on"] = on
    try:
        write_control_record(path, control)
    except OSError:
        pass  # The exit code still reports the restore; never mask it here.
    # Success is the set form's own exit code: no READ form exists in the
    # slice to confirm the state, and no stdout comparator for ON is ruled.
    return on["exit_code"] == 0


def timed_log_argv(start_epoch_s, end_epoch_s):
    """``log show`` over one envelope's capture window, timed process only.

    ``log show`` takes LOCAL wall time as ``YYYY-MM-DD HH:MM:SS``.
    """

    def local(epoch_s):
        return datetime.fromtimestamp(epoch_s).strftime("%Y-%m-%d %H:%M:%S")

    return (LOG, "show", "--info", "--debug", "--style", "syslog",
            "--predicate", TIMED_LOG_PREDICATE,
            "--start", local(start_epoch_s), "--end", local(end_epoch_s))


def timed_log_marker_lines(text):
    """Raw count of log lines carrying any applied-correction marker."""
    return sum(any(marker in line for marker in TIMED_LOG_MARKERS)
               for line in text.splitlines())


def timed_log_moment(line):
    """Seconds since the epoch of a syslog-style line, or None."""
    match = re.match(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+", line)
    if match is None:
        return None
    try:
        return datetime.strptime(match.group(0), "%Y-%m-%d %H:%M:%S.%f").timestamp()
    except ValueError:
        return None


# One applied correction is logged three times within a millisecond or two:
# ``cmd,ntp_adjtime:in``, ``:out``, then the ``cmd,apply,src,`` receipt.  The
# receipt is therefore the event, and a bare syscall line counts only when no
# receipt sits beside it -- which is how a log without receipt lines (another
# macOS build, or a hard ``settimeofday`` step) still attests.  This window is
# a GROUPING tolerance, never an admission tolerance: any nonzero count
# excludes the envelope, so mis-grouping can only change a diagnostic number.
TIMED_LOG_EVENT_WINDOW_S = 1.0


def timed_log_matches(text):
    """Count the clock corrections ``timed`` APPLIED (ruling 14 R4).

    Calibrated on the packet's own exhibit D, which the cold gate read as ten
    applied corrections: 10 ``cmd,apply,src,`` receipts, 20 ``ntp_adjtime``
    lines (an in/out pair per receipt, one pair straddling a millisecond
    boundary), 0 ``settimeofday``, 30 marker lines in total -- and 10 events.
    """

    applied, syscalls = [], []
    for line in text.splitlines():
        if TIMED_LOG_MARKERS[0] in line:
            applied.append(timed_log_moment(line))
        elif any(marker in line for marker in TIMED_LOG_MARKERS[1:]):
            syscalls.append(timed_log_moment(line))
    events = len(applied)
    for moment in syscalls:
        if moment is None or not any(
                other is not None and abs(other - moment) <= TIMED_LOG_EVENT_WINDOW_S
                for other in applied):
            events += 1
    return events


def capture_still_live(cleanup):
    """A reason the attestation must not run yet, or None.

    The teardown proves every supervised group of this envelope gone.  While
    one is unproven a ``powermetrics`` recorder may still be sampling, and
    ``log show``'s work in ``logd`` would land inside a recorded window as
    observer energy no one can attribute (A269 ruling 10 Q4 ii).
    """

    if cleanup.get("residue"):
        return "supervised capture groups still present: " + ", ".join(
            str(pgid) for pgid in cleanup["residue"])
    if cleanup.get("errors"):
        return "group teardown could not prove the capture ended: " + "; ".join(cleanup["errors"])
    return None


def attestation_window(stamps):
    """The capture window in wall time, union of both clocks (ruling 10 Q4 i).

    Each end stamp carries the same instant on two clocks: ``epoch_s`` (wall,
    which a step can move) and ``monotonic_before_s`` (which no step moves).
    The monotonic pair gives the capture's true LENGTH; each wall stamp gives
    a candidate position.  If a step displaced the start stamp, the end stamp
    minus the length is the truer start, and the other way round for the end,
    so the window is the union of both readings -- widened by one second on
    each side for the stamps' own resolution.

    The worked case a plain +-1 s window loses: a 600 s capture starts at wall
    1000 and the clock is stepped BACK 30 s partway through, so the stop stamp
    reads 1570.  Entries written just before the step carry wall timestamps up
    to 1600, outside [999, 1571] -- the +-1 s window around the two wall
    stamps -- so a slew applied in that stretch goes unseen and the envelope
    is authenticated on an incomplete log.  The union window is
    [min(1000, 970) - 1, max(1570, 1600) + 1] = [969, 1601] and holds both
    readings of the capture's extent.  (A step FORWARD widens the wall
    interval instead, and there the two forms agree.)
    """

    started, stopped = stamps["sampling_started"], stamps["sampling_stopped"]
    span = float(stopped["monotonic_before_s"]) - float(started["monotonic_before_s"])
    start_epoch, stop_epoch = float(started["epoch_s"]), float(stopped["epoch_s"])
    return [min(start_epoch, stop_epoch - span) - 1, max(stop_epoch, start_epoch + span) + 1]


ATTESTATION_WINDOW_METHOD = "epoch_monotonic_union_v1"


def attest_network_time(out, blocked=None):
    """Authenticate one envelope's clock discipline from the ``timed`` log.

    A set-command receipt proves an instruction was accepted; it does not
    prove no correction was applied during the capture.  The unified log does:
    ``timed`` records every applied slew or step.  Zero matched lines over the
    capture window (:func:`attestation_window`) is an AUTHENTICATED envelope;
    any match is ``slew_attested`` and excluded; a failed query, or one that
    must not run because the capture is not provably over (``blocked``), is
    ``asserted`` and excluded.  Run immediately after the collector exits and
    its groups are reaped, because the log store is rotated -- never deferred
    to harvest.
    """

    attestation = {"state": "asserted", "method": TIMED_LOG_ATTESTATION_METHOD,
                   "window_epoch_s": None, "window_method": ATTESTATION_WINDOW_METHOD,
                   "log": None, "log_sha256": None,
                   "matched_lines": None, "exit_code": None, "argv": None,
                   "attested_epoch_s": time.time()}
    if blocked:
        attestation["reason"] = "attestation not run beside a live capture: " + blocked
        return attestation
    try:
        session = json.loads((out / "session.json").read_text())
        stamps = session["power"]["anchor"]["clock_stamps"]
        window = attestation_window(stamps)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        attestation["reason"] = f"capture window unavailable: {type(exc).__name__}: {exc}"
        return attestation
    argv = timed_log_argv(*window)
    attestation.update(window_epoch_s=window, argv=list(argv))
    try:
        completed = subprocess.run(list(argv), capture_output=True, text=True, timeout=300)
        path = out / TIMED_LOG_BASENAME
        path.write_text(completed.stdout)
    except (OSError, subprocess.SubprocessError) as exc:
        attestation["reason"] = f"timed log query failed: {type(exc).__name__}: {exc}"
        return attestation
    matched = timed_log_matches(completed.stdout)
    attestation.update(exit_code=completed.returncode, log=path.name,
                       log_sha256=digest(path.read_bytes()), matched_lines=matched,
                       matched_marker_lines=timed_log_marker_lines(completed.stdout))
    if completed.returncode != 0:
        attestation["reason"] = f"timed log query exited {completed.returncode}"
    elif matched:
        attestation.update(state="slew_attested",
                           reason=f"{matched} applied clock corrections inside the capture window")
    else:
        attestation.update(state="authenticated",
                           reason="no applied clock correction inside the capture window")
    return attestation


def record_attestation(out, attestation):
    """Add the attestation to the envelope's own provenance, atomically.

    The collector has exited, so the chain owns this write; temp plus rename
    means a reader never sees a half-written session record.  The attestation
    carries ``session_sha256_before`` -- the digest of the file this rewrite
    replaced -- so the one edit made after the collector exits is auditable
    from the record itself (A269 ruling 10 Q4 iii).  Nothing else rewrites
    ``session.json`` after the collector exits: under cure 2 there is no
    finaliser pass, so this digest can only ever name the collector's own
    bytes.
    """

    path = out / "session.json"
    try:
        raw = path.read_bytes()
        session = json.loads(raw)
    except (OSError, ValueError):
        return False
    attestation["session_sha256_before"] = digest(raw)
    provenance = session.get("network_time_provenance")
    if not isinstance(provenance, dict):
        provenance = {"state": "unknown",
                      "reason": "collector recorded no network-time provenance"}
    provenance["attestation"] = attestation
    session["network_time_provenance"] = provenance
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(session, sort_keys=True, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)
    return True


def attestation_exclusions(state):
    """The ruled vocabulary: only an authenticated envelope is claim-bearing."""
    if state == "authenticated":
        return []
    if state == "slew_attested":
        return [NETWORK_TIME_SLEW_EXCLUSION]
    return [NETWORK_TIME_UNATTESTED_EXCLUSION]


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


def chi_square_lower_decile(df):
    """Invert regularized lower gamma P(df/2, x/2), using only stdlib.

    The pilot needs df=3..5; support 3..11 for diagnostic cross-checks.
    At the lower decile x/2 < df/2, so the positive gamma series converges
    quickly without subtracting a nearly-one upper-tail probability.
    """
    if type(df) is not int or not 3 <= df <= 11:
        raise ValueError("chi-square degrees of freedom must be in 3..11")
    shape = df / 2
    low, high = 0., float(df)
    for _ in range(80):
        mid = (low + high) / 2
        x = mid / 2
        term = total = 1 / shape
        for k in range(1, 1000):
            term *= x / (shape + k)
            total += term
            if term <= total * 1e-15:
                break
        else:
            raise ArithmeticError("lower gamma series did not converge")
        probability = total * math.exp(-x + shape * math.log(x) - math.lgamma(shape))
        if probability < .10:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def size_block_two(s_upper, protocol=None):
    if type(s_upper) not in (float, int) or not math.isfinite(s_upper) or s_upper < 0:
        raise ValueError("s_upper must be a finite nonnegative upper confidence bound")
    sizing = (frozen_protocol() if protocol is None else protocol)["sizing"]
    return max(sizing["minimum_pairs"], math.ceil(sizing["multiplier"] * s_upper ** 2 / sizing["delta_j"] ** 2))


def stop_branch(*, s_upper=None, observer_floor=None, block_two_upper_j=None, protocol=None):
    """Apply only ruled stop conditions; absent evidence is never a pass."""
    protocol = frozen_protocol() if protocol is None else protocol
    smallest_share = protocol["block_two"]["smallest_holdable_share"]
    for value in (s_upper, observer_floor, smallest_share, block_two_upper_j):
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
            raise ValueError("stop-branch evidence must be finite and nonnegative")
    causes = []
    pairs = None if s_upper is None else size_block_two(s_upper, protocol)
    if pairs is not None and pairs > protocol["sizing"]["maximum_pairs"]:
        causes.append("sized_pairs_above_24")
    if observer_floor is not None and observer_floor > smallest_share:
        causes.append("observer_floor_above_smallest_holdable_share")
    if block_two_upper_j is not None and block_two_upper_j > protocol["sizing"]["delta_j"]:
        causes.append("block_two_upper_bound_above_1_J")
    return {"outcome": protocol["stop_branches"][causes[0]] if causes else "no decision", "causes": causes, "pairs": pairs}


def pilot_summary(directory, protocol, envelopes, observer_cpu_s=None):
    """Apply ruling 46b to fixed pairs; preserve unfiltered diagnostics."""
    import statistics
    from scripts import sample_quiet_predicate_evidence as harness
    values, all_rows = [], []
    journal = directory.parent / protocol["recorder_journal"]
    covariates = [json.loads(line) for line in journal.read_text().splitlines() if line] if journal.exists() else []
    clean_busy = []
    for entry in envelopes:
        excluded = []
        if entry.get("collector_exit", 0) != 0:
            excluded.append("collect_error")
        if entry.get("cleanup", {}).get("cleanup_proven") is False:
            excluded.append("cleanup_unproven")
        scheduled = entry.get("scheduled_mono_s")
        support = [r for r in covariates if scheduled is not None and
                   r["monotonic_start"] >= scheduled and
                   r["monotonic_end"] <= scheduled + protocol["envelope_s"]]
        busy = [(r.get("observation") or {}).get("metrics", {}).get("busy_cores") for r in support]
        distribution = harness.quantiles(busy)
        entry = {**entry, "busy_cores": {**distribution, "median": distribution["p50"]},
                 "busy_cores_samples": len([v for v in busy if harness.number(v) is not None]),
                 "recorder_observer_cpu_s": sum(r.get("observer_cpu_s") or 0 for r in support)}
        out = directory / f"envelope-{entry['index']:02d}"
        try:
            session = json.loads((out / "session.json").read_text())
            rows = [json.loads(line) for line in (out / "rounds.jsonl").read_text().splitlines() if line]
        except (OSError, ValueError) as exc:
            values.append({**entry, "excluded": excluded + ["incomplete_interior_support"], "error": str(exc), "joules": None})
            continue
        all_rows.extend(rows)
        hard = hard_exclusions(rows)
        excluded.extend(hard)
        if not hard:
            clean_busy.extend(busy)
        interior = session.get("interior", {})
        # Clock-discipline attestation (ruling 14 R4): only an envelope whose
        # capture window carries no applied correction in the ``timed`` log is
        # claim-bearing.  A slew inside the window and a failed or missing
        # query are both HARD exclusions; the session record is authoritative
        # and the executor's own envelope entry is the fallback, so a summary
        # re-derived from disk reaches the same verdict.
        provenance = session.get("network_time_provenance")
        attestation = provenance.get("attestation") if isinstance(provenance, dict) else None
        state = (attestation.get("state") if isinstance(attestation, dict)
                 else entry.get("network_time_attestation"))
        excluded.extend(attestation_exclusions(state))
        if (session.get("power") or {}).get("anchor", {}).get("status") != "bounded":
            excluded.append("clock_anchor_unresolved")
        if not interior.get("complete_support"):
            excluded.append("incomplete_interior_support")
        entry = {**entry, "collector_start_drift_s": session.get("start_drift_s")}
        if max(abs(entry["start_drift_s"]), abs(session.get("start_drift_s") or 0)) > protocol["start_drift_max_s"]:
            excluded.append("start_drift")
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
    # Index identity, not position in a filtered list, fixes the original pairs.
    by_index = {v["index"]: v for v in values}
    overlapping = []
    for index in range(1, protocol["envelopes"]):
        a, b = by_index.get(index), by_index.get(index + 1)
        if a is None or b is None or a["joules"] is None or b["joules"] is None:
            continue
        overlapping.append({"left": index, "right": index + 1,
            "delta_j": b["joules"] - a["joules"],
            "retained": not a["excluded"] and not b["excluded"]
                and a.get("boot_id") == b.get("boot_id") and a.get("os_build") == b.get("os_build")})
    deltas = [d for d in overlapping if d["retained"] and d["left"] % 2 == 1]
    sufficient = len(retained) >= protocol["minimum_retained"] and len(deltas) >= protocol["minimum_adjacent_pairs"]
    pair_sd = statistics.stdev(d["delta_j"] for d in deltas) if len(deltas) >= 2 else None
    df = len(deltas) - 1 if len(deltas) >= 2 else None
    factor = math.sqrt(df / chi_square_lower_decile(df)) if sufficient else None
    s_upper = pair_sd * factor if sufficient else None
    # Whole-round measured cost, including rejected envelopes; never subtract
    # it from energy or use it as an envelope retention input.
    observer_rows = [r for r in all_rows if harness.number(r.get("observer_cpu_s")) is not None
                     and harness.number(r.get("round_mono_start_s")) is not None
                     and harness.number(r.get("round_mono_end_s")) is not None
                     and r["round_mono_end_s"] > r["round_mono_start_s"]]
    observer_support_s = sum(r["round_mono_end_s"] - r["round_mono_start_s"] for r in observer_rows)
    observer_floor = sum(r["observer_cpu_s"] for r in observer_rows) / observer_support_s if observer_support_s else None
    stop = stop_branch(s_upper=s_upper, observer_floor=observer_floor, protocol=protocol)
    unfiltered = [v["joules"] for v in values if v["joules"] is not None]
    large_pairs = [d for d in overlapping if pair_sd is not None and abs(d["delta_j"]) > 3 * pair_sd]
    report = {"schema": "joulewise.quiet_predicate_pilot_summary.v1", "evidence_status": "PROVISIONAL",
        "status": "SPREAD_RECORDED" if sufficient else "INCONCLUSIVE", "envelopes": values,
        "retained": len(retained), "sizing_pairs": deltas, "retained_pairs": len(deltas),
        "adjacent_pairs": overlapping, "adjacent_pairs_role": "diagnostic_only; never used for sizing",
        "adjacent_pair_sd_j": statistics.stdev(d["delta_j"] for d in overlapping) if len(overlapping) >= 2 else None,
        "pair_sd_j": pair_sd, "pair_df": df, "s_upper_factor": factor,
        "single_envelope_sd_j": statistics.stdev(v["joules"] for v in retained) if len(retained) >= 2 else None,
        "unfiltered_single_envelope_sd_j": statistics.stdev(unfiltered) if len(unfiltered) >= 2 else None,
        "single_envelope_role": "diagnostic_only; never used for sizing",
        "first_to_last_retained_drift_j": retained[-1]["joules"] - retained[0]["joules"] if len(retained) >= 2 else None,
        "pairs_above_3_pair_sd": large_pairs,
        "pairs_above_3_pair_sd_role": "overlapping adjacent differences; diagnostic only",
        "max_abs_delta_j": max((abs(d["delta_j"]) for d in overlapping), default=None),
        "busy_cores": harness.quantiles(clean_busy), "busy_cores_role": "covariate_only; never excluded",
        "busy_cores_source": protocol["recorder_journal"],
        "busy_cores_support": "recorder intervals fully within each scheduled envelope",
        "clean_machine_busy_cores": harness.quantiles(clean_busy),
        "clean_machine_definition": "envelopes passing census, AC and thermal hard probes; independent of energy retention",
        "observer_floor_cores": observer_floor, "observer_support_s": observer_support_s,
        "s_upper": s_upper,
        "s_upper_reason": "one-sided upper 90% chi-square bound; independent normal pair differences assumed"
            if sufficient else "fewer than four retained disjoint pairs or eight retained envelopes; no top-up",
        "block_two_pairs": stop["pairs"], "block_two_stop": stop,
        "block_two_pairs_reason": "ruling 46b: " + protocol["sizing"]["formula"] +
            f"; delta_j={protocol['sizing']['delta_j']}; stop above {protocol['sizing']['maximum_pairs']} pairs"
            if sufficient else "INCONCLUSIVE; no sizing",
        "whole_campaign_observer_cpu_s": observer_cpu_s,
        "observer_definition": "SELF + reaped CHILDREN, including collector, recorder, sampler and census; never subtracted",
        "cutoff_authority": False, "top_up": False}
    harness.write_json(directory / "summary.json", report)
    (directory / "summary.md").write_text(
        "# QPE-01 pilot (PROVISIONAL, descriptive)\n\n" +
        f"Status: {report['status']}. Retained {len(retained)}/{protocol['envelopes']} envelopes; {len(deltas)} disjoint pairs.\n\n" +
        f"Disjoint-pair sample SD: {pair_sd} J (df={df}); upper 90% bound: {s_upper} J. " +
        "This chi-square construction assumes independent, normally distributed pair differences.\n\n" +
        f"Block-two pairs: {stop['pairs']}; sizing stop: {stop['outcome']}. No sizing when INCONCLUSIVE.\n\n" +
        f"Diagnostics only: {len(overlapping)} overlapping differences (SD {report['adjacent_pair_sd_j']} J); " +
        f"single-envelope SD {report['unfiltered_single_envelope_sd_j']} J; " +
        f"first-to-last retained drift {report['first_to_last_retained_drift_j']} J. " +
        f"Overlapping adjacent pairs with |delta| > 3 * s_pair: {large_pairs}. Values are in summary.json.\n\n" +
        "Busy cores are recorded covariates and never an exclusion input. " +
        "Every exclusion and partial interior is retained in summary.json. No top-up, cutoff or activation authority. " +
        "Block two is not authored by this summary.\n")
    return report


# The gap between the end of one capture and the next spawn (20 s under v2:
# slot_pitch_s 620 - envelope_s 600) holds the collector's exit, the plist
# parse, the anchor derivation, the group teardown and the clock attestation.
# The teardown's budget is the gap minus a reserve that the attestation's
# `log show` fits in (worst observed 1.45 s; A269 gate C4 measured 0.70/0.84 s),
# so a teardown can never eat the attestation's time or run into the next
# spawn.  Derived from the registration at the call site, never a literal.
CLEANUP_BUDGET_RESERVE_S = 5


def cleanup_budget_s(protocol):
    """The per-slot teardown budget: the gap, less the attestation reserve."""
    gap = protocol["slot_pitch_s"] - protocol["envelope_s"]
    return max(1, gap - CLEANUP_BUDGET_RESERVE_S)


def window_budget_ok(plan, protocol):
    """Does the whole frozen schedule fit inside the night's window?

    Cure 2 spawns envelope i at ``settle_s + (i-1) * slot_pitch_s`` and the
    last one captures for ``envelope_s``, so the schedule needs
    ``settle_s + (envelopes-1) * slot_pitch_s + envelope_s`` seconds of the
    window.  Under v2 that is 600 + 11*620 + 600 = 8020 s against
    ``window_max_s`` 9000.  A pitch that does not fit is refused BEFORE any
    collector is launched (A269 ruling 10 Q1 amendment A2), because the
    alternative is discovering it at envelope 12, after eleven captures.
    """

    needed = (protocol["settle_s"] + (protocol["envelopes"] - 1) * protocol["slot_pitch_s"]
              + protocol["envelope_s"])
    return needed <= min(plan.window_max_s, protocol["window_max_s"]), needed


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
    consecutive_cleanup_failures = 0
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
        # The whole frozen schedule must fit the window BEFORE anything is
        # launched (A269 ruling 10 Q1 A2); a pitch that overruns is a
        # registration defect, not a night to discover at envelope 12.
        fits, needed = window_budget_ok(plan, protocol)
        if not fits:
            raise ValueError(f"window_budget_exceeded: the frozen schedule needs {needed} s "
                             f"of a {min(plan.window_max_s, protocol['window_max_s'])} s window")
        # Network time OFF is established BEFORE the settle, so the settle also
        # absorbs any in-flight slew the daemon had already started (a 20 ms
        # adjtime slew completes in seconds).  Failure refuses the night here:
        # no recorder, no envelope, no capture under an unknown clock regime.
        control_path = establish_network_time_off(night_dir)
        env[NETWORK_TIME_RECORD_ENV] = str(control_path)
        print(f"evidence_network_time off record={control_path}", flush=True)
        # Settle belongs inside GO; verify-only never reaches this call.
        print(f"evidence_settle seconds={protocol['settle_s']}", flush=True)
        time.sleep(protocol["settle_s"])
        first = go + protocol["settle_s"]
        recorder = launch("recorder", [sys.executable, "-B", "-m", "joulewise.quiet_predicate_campaign", "record"])
        for index in range(1, protocol["envelopes"] + 1):
            # The SCHEDULE runs on the pitch; the CAPTURE keeps its own length.
            # Every slot therefore starts from a quiet machine like envelope 01
            # did (chain drift 0.160 s, session 0.318 s on the 2026-09-22 pilot)
            # instead of inheriting its predecessor's finalisation tail.
            scheduled = first + (index - 1) * protocol["slot_pitch_s"]
            time.sleep(max(0, scheduled - time.monotonic()))
            if time.time() + protocol["envelope_s"] > plan.t0_epoch_s + plan.window_max_s:
                raise ValueError("evidence window exhausted; no compressed envelope or top-up")
            actual = time.monotonic()
            # Pre-registered in-chain abort (A269 ruling 10 Q3, amended to every
            # envelope): a spawn later than start_drift_abort_s after its
            # scheduled instant means the tail is back, and the night ends
            # REFUSED here -- before this slot's capture, never as an
            # INCONCLUSIVE data verdict afterwards.  `top_up: false` in the
            # registration forbids pooling an aborted night's envelopes, so
            # stopping costs nothing that a later night could have reused.
            # Envelope 01 follows the settle and tests no pitch, so it is exempt.
            drift = actual - scheduled
            if index >= 2 and drift > protocol["start_drift_abort_s"]:
                append_event(night_dir / "evidence_envelopes.jsonl",
                             {"index": index, "scheduled_mono_s": scheduled,
                              "actual_mono_s": actual, "start_drift_s": drift,
                              "abort": "start_drift_abort"})
                raise ValueError(f"start_drift_abort: envelope {index} would start {drift:.3f} s "
                                 f"after its scheduled instant (bar {protocol['start_drift_abort_s']} s)")
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
            # The budget is the gap this registration leaves, never a literal.
            cleanup = cleanup_groups(journal, children, budget_s=cleanup_budget_s(protocol),
                                     exclude={recorder.pid})
            # Authenticate this envelope's clock discipline now, while the log
            # store still holds the window (ruling 14 R4); the state joins the
            # envelope's own provenance and the exclusion vocabulary.  It runs
            # HERE -- after the teardown, before the next slot's sleep -- so
            # `log show`'s work inside `logd` can never land in a recorded
            # window as unattributable observer energy (A269 ruling 10 Q4 ii).
            # If the teardown did not prove every supervised group gone, a
            # recorder may still be sampling, and the query is refused rather
            # than run beside it: the envelope becomes `asserted`.
            attestation = attest_network_time(out, blocked=capture_still_live(cleanup))
            record_attestation(out, attestation)
            envelopes.append({"index": index, "scheduled_mono_s": scheduled, "actual_mono_s": actual,
                              "start_drift_s": actual - scheduled, "collector_exit": code, "cleanup": cleanup,
                              "network_time_attestation": attestation["state"],
                              "network_time_attestation_matched_lines": attestation["matched_lines"]})
            append_event(night_dir / "evidence_envelopes.jsonl", envelopes[-1])
            print(f"envelope_end index={index} rc={code} cleanup_proven={cleanup['cleanup_proven']}"
                  f" clock_attestation={attestation['state']}", flush=True)
            consecutive_cleanup_failures = 0 if cleanup["cleanup_proven"] else consecutive_cleanup_failures + 1
            if consecutive_cleanup_failures >= 2:
                raise ValueError("two consecutive cleanup_unproven envelopes")
            if recorder.poll() is not None:
                raise ValueError("evidence covariate recorder exited early")
        outcome = "partial" if any(e["collector_exit"] != 0 or not e["cleanup"]["cleanup_proven"] for e in envelopes) else "complete"
    except (OSError, ValueError, KeyboardInterrupt, subprocess.SubprocessError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        for signum in old:
            signal.signal(signum, signal.SIG_IGN)
        network_time_restored = restore_network_time(night_dir)
        cleanup = cleanup_record(night_dir, children)
        try:
            pilot_summary(directory, protocol, envelopes,
                          harness.cpu_total() - cpu_start if cleanup["cleanup_proven"] else None)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            outcome, error = "refused", "pilot summary failed: " + str(exc)
        if not cleanup["cleanup_proven"]:
            outcome, error = "refused", error or "final evidence cleanup unproven"
        if outcome == "refused":
            write_refusal(night_dir, plan, error or "evidence execution aborted")
        harness.write_json(night_dir / "evidence_outcome.json", {"outcome": outcome, "error": error,
            "envelopes_attempted": len(envelopes), "cleanup_proven": cleanup["cleanup_proven"],
            "network_time_restored": network_time_restored})
        for signum, handler in old.items():
            signal.signal(signum, handler)
    print(f"evidence_end outcome={outcome} cleanup_proven={cleanup['cleanup_proven']}"
          f" network_time_restored={network_time_restored}", flush=True)
    # A failed restore leaves the machine, not the measurement, in the wrong
    # state: the captured envelopes were taken under a proven OFF and stay
    # valid.  It gets its own code (3, distinct from the refusal 2) so the
    # harvester re-attempts the restore and surfaces it.
    if not network_time_restored:
        return 3
    return 0 if outcome in {"complete", "partial"} and cleanup["cleanup_proven"] else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "run", "record", "refuse"))
    parser.add_argument("--reason", default="evidence wrapper refused before execution")
    args = parser.parse_args(argv)
    try:
        if args.command == "refuse":
            raise ValueError(args.reason)
        plan, manifest, sha = verify_environment()
        if args.command == "verify":
            print(f"VERIFY_ONLY_OK manifest={sha}")
            return 0
        if os.environ.get("NIGHT_VERIFY_ONLY") == "1":
            raise ValueError("verify-only mode refuses execution")
        raw = (Path(plan.measurement_root) / PROTOCOL_PATH).read_bytes()
        if digest(raw) != manifest["files"][PROTOCOL_PATH]:
            raise ValueError("protocol changed after manifest verification")
        protocol = validate_protocol(frozen_protocol(raw), manifest["files"][CHAIN_PATH])
        if args.command == "record":
            return record_covariates(protocol, Path(os.environ["NIGHT_DIR"]))
        return execute(plan, protocol, Path(os.environ["NIGHT_DIR"]))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        if args.command != "verify":
            # The plan was admitted by the driver; refuse even if manifest
            # verification failed before execute could create a journal.
            try:
                plan = night_gate.NightPlan.from_mapping(json.loads(Path(os.environ["EVIDENCE_PLAN_PATH"]).read_text()))
                write_refusal(Path(os.environ["NIGHT_DIR"]), plan, str(exc))
            except (OSError, ValueError, KeyError) as refusal_error:
                print(f"EVIDENCE_REFUSAL_TRANSPORT_FAILED {refusal_error}", file=sys.stderr)
        print(f"EVIDENCE_REFUSED {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
