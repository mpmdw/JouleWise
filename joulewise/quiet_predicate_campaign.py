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
from joulewise.night_kinds import kind_row
from joulewise.arm_readiness import EXPECTED_NETWORK_TIME_OFF_STDOUT

PROTOCOL_PATH = night_gate.QPE01_PILOT_REGISTRATION_PATH
CHAIN_PATH = night_gate.EVIDENCE_CHAIN_PATH
# Absolute executables, resolved through module constants (cold gate
# 2026-09-22, ruling 10 Q1 rules 1 and 4, 14 R4).  The production argv strings
# are exactly the NOPASSWD sudoers slice's two set forms and the unified-log
# reader.  The SUDOERS SLICE is the whole of what the machine's NOPASSWD entry
# grants this chain without a password: ``systemsetup -setusingnetworktime on``
# and ``... off``, and nothing else -- no read form, no other subcommand.  The
# zsh ``log`` builtin shadows /usr/bin/log and returns nothing, so
# the absolute path is load-bearing, not cosmetic.  A test substitutes its own
# executables by rebinding these names -- PATH cannot fake an absolute path --
# and a regression pins the production values.
SUDO = "/usr/bin/sudo"
SYSTEMSETUP = "/usr/sbin/systemsetup"
LOG = "/usr/bin/log"
NETWORK_TIME_CONTROL_SCHEMA = "joulewise.network_time_control.v1"
# One `systemsetup` toggle answers in milliseconds; thirty seconds is the
# bound past which it is not going to answer at all.  Named here so a
# regression can shorten it without a fake clock.
NETWORK_TIME_SET_TIMEOUT_S = 30
NETWORK_TIME_CONTROL_BASENAME = "network_time_control.json"
# Where the restore receipt goes when the control record cannot be read or
# is not an object: a sibling file, so the original bytes survive.
NETWORK_TIME_RESTORE_BASENAME = "network_time_control.restore.json"
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
# The bench replay's harvest-side verdict (cold gate #3 ruling 10 Q7; brief
# D6).  It is a SUMMARY STATUS, never an exclusion reason: A269 ruling 10 Q2
# byte-pins the registration's `exclusions` list, and emitting a reason the
# pinned list does not carry is precisely the defect that ruling forbids.
REPLAY_NEVER_EVIDENCE = "REPLAY_NEVER_EVIDENCE"
REPLAY_REFUSAL_REASON = "replay_recorder"


def replay_refusal_error(error):
    """The replay refusal, KEEPING whatever more specific error came first.

    Both replay refusal points used to assign `REPLAY_REFUSAL_REASON` over
    `error`, and on the bench the switch is ALWAYS set, so a night that
    aborted on `start_drift_abort` -- the exact failure the bench replay
    exists to detect -- or whose summary crashed reached
    `evidence_outcome.json` and `write_refusal` reading `replay_recorder`
    and nothing else (delta lenses: execution SHOULD-FIX 1, contract N1).
    The specific text leads, the marker is appended, and the marker is never
    appended twice (a night both points fire on is the ordinary bench case).
    """

    if not error:
        return REPLAY_REFUSAL_REASON
    if REPLAY_REFUSAL_REASON in error:
        return error
    return f"{error}; {REPLAY_REFUSAL_REASON}"
HARNESS_PATHS = ("scripts/sample_quiet_predicate_evidence.py", "joulewise/quiet_admission.py")
MANIFEST_PATHS = (PROTOCOL_PATH, CHAIN_PATH, *HARNESS_PATHS,
                  "joulewise/quiet_predicate_campaign.py", "joulewise/night_gate.py",
                  "joulewise/night_kinds.py",
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
    row = kind_row("quiet_predicate_evidence")
    contents = {name: tracked_bytes(plan.measurement_root, plan.measurement_head, name)
                for name in MANIFEST_PATHS}
    files = {name: digest(raw) for name, raw in contents.items()}
    protocol = frozen_protocol(contents[PROTOCOL_PATH])
    validate_protocol(protocol, files[CHAIN_PATH])
    registration = Path(plan.registration_path)
    if not registration.is_absolute():
        registration = Path(plan.measurement_root) / registration
    if registration.resolve() != (Path(plan.measurement_root) / row.protocol_path).resolve():
        raise ValueError("evidence registration must be the tracked pilot protocol")
    if plan.receipt_class != row.receipt_class or plan.quiet_admission is not None:
        raise ValueError("evidence pilot requires v2 DIAGNOSTIC_NO_PACK")
    if plan.window_max_s != protocol["window_max_s"] or plan.window_max_s != row.window_max_s:
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


def write_refusal(night_dir, plan, detail, reason="night_probe_error"):
    """One typed refusal document.  `reason` is a REGISTERED code, never free text.

    The non-observer abort writes `non_observer_process_busy` (cold gate 10,
    2026-09-23, Q2) rather than the generic probe error, so a reader of
    `refusal.json` alone can tell the machine-state abort from a failed probe.
    """

    from scripts.run_night import _write_driver_refusal
    if reason not in night_gate.NIGHT_DRIVER_REASON_CODES | night_gate.NIGHT_GATE_REASON_CODES:
        raise ValueError("evidence refusal reason is not registered: " + str(reason))
    night_dir.mkdir(parents=True, exist_ok=True)
    return _write_driver_refusal(night_dir / "refusal.json", plan, reason,
                                 "evidence chain refused: " + detail)


def network_time_argv(state):
    """The exact set form of the NOPASSWD sudoers slice; nothing is inferred."""
    return (SUDO, "-n", SYSTEMSETUP, "-setusingnetworktime", state)


def set_network_time(state):
    """Run one set form and return its receipt: argv, code, stdout, both clocks."""
    argv = network_time_argv(state)
    completed = subprocess.run(list(argv), capture_output=True, text=True,
                               timeout=NETWORK_TIME_SET_TIMEOUT_S)
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
    try:
        off = set_network_time("off")
    except Exception as exc:  # noqa: BLE001 - every class refuses the night
        # A toggle that timed out, or could not be run at all, is still an
        # ATTEMPT that leaves the machine's network-time state unknown.  The
        # receipt for it is written BEFORE the refusal for the same reason the
        # exit-1 receipt is: a night that stopped here must say on its own
        # record what it did to the machine, and `off: null` says nothing.
        off = {"argv": list(network_time_argv("off")), "exit_code": None, "stdout": None,
               "error": f"{type(exc).__name__}: {exc}",
               "epoch_s": time.time(), "monotonic_s": time.monotonic()}
        write_control_record(path, {"schema": NETWORK_TIME_CONTROL_SCHEMA, "off": off, "on": None})
        raise ValueError("network time OFF not established: " + off["error"]) from exc
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
    slice -- the two ``systemsetup`` set forms the NOPASSWD entry grants -- so
    the prior state is unknowable without a password and ON is the ruled end
    state.  A failed restore does NOT invalidate the envelopes already
    captured under a proven OFF: it is reported as
    ``network_time_restored: false`` and a distinct exit code.

    Two rules hold the receipt itself.  (1) The ON receipt is added to the
    control record ONLY when that record is absent (nothing was established
    yet, so there are no bytes to protect) or reads back as an object.  A record
    that is unreadable, or parses to a list, a string, a number or ``null``,
    keeps its bytes and the receipt goes to a sibling
    ``network_time_control.restore.json``: rewriting it as ``{"off": null,
    ...}`` would leave an artifact asserting OFF was never established for a
    night whose every envelope carries the digest of the original bytes.
    (2) Nothing raises out of here.  This is the ``finally``; an exception
    escaping it replaces a measured outcome -- the outcome document, the
    refusal, the summary -- with no outcome at all, which is precisely what a
    control record parsing to ``null`` used to do (``TypeError`` on item
    assignment, caught by no except tuple in the call chain).
    """

    try:
        path = night_dir / NETWORK_TIME_CONTROL_BASENAME
        if not path.exists():
            # Nothing was ever established (a refusal before the toggle): no
            # bytes to protect, so the restore opens the record itself.
            control = {"schema": NETWORK_TIME_CONTROL_SCHEMA, "off": None}
        else:
            try:
                control = json.loads(path.read_text())
            except (OSError, ValueError):
                control = None
        try:
            on = set_network_time("on")
        except Exception as exc:  # noqa: BLE001 - see rule (2) above
            on = {"argv": list(network_time_argv("on")), "exit_code": None, "stdout": None,
                  "error": f"{type(exc).__name__}: {exc}", "epoch_s": None, "monotonic_s": None}
        try:
            if isinstance(control, dict):
                control["on"] = on
                write_control_record(path, control)
            else:
                write_control_record(night_dir / NETWORK_TIME_RESTORE_BASENAME,
                                     {"schema": NETWORK_TIME_CONTROL_SCHEMA,
                                      "off": {"state": "unreadable",
                                              "reason": f"{NETWORK_TIME_CONTROL_BASENAME} is "
                                                        "not a readable control record",
                                              "record": NETWORK_TIME_CONTROL_BASENAME},
                                      "on": on})
        except Exception as exc:  # noqa: BLE001
            # The exit code still reports the restore; never mask it here.
            # But a receipt that could not be written is a hole in the
            # night's record, and the only place that hole was visible was
            # the absent file itself: say so on the executor's own stdout,
            # which the night log keeps.
            print(f"restore receipt write failed: {type(exc).__name__}: {exc}", flush=True)
        # Success is the set form's own exit code: no READ form exists in the
        # slice to confirm the state, and no stdout comparator for ON is ruled.
        return on["exit_code"] == 0
    except Exception as exc:  # noqa: BLE001 - rule (2): the finally is sacred
        try:
            write_control_record(night_dir / NETWORK_TIME_RESTORE_BASENAME,
                                 {"schema": NETWORK_TIME_CONTROL_SCHEMA, "off": None,
                                  "on": {"argv": list(network_time_argv("on")),
                                         "exit_code": None, "stdout": None,
                                         "error": f"{type(exc).__name__}: {exc}",
                                         "epoch_s": None, "monotonic_s": None}})
        except Exception:  # noqa: BLE001
            pass
        return False


def timed_log_argv(start_epoch_s, end_epoch_s):
    """``log show`` over one envelope's capture window, timed process only.

    ``log show`` takes LOCAL wall time as ``YYYY-MM-DD HH:MM:SS``.
    """

    def local(epoch_s):
        return datetime.fromtimestamp(epoch_s).strftime("%Y-%m-%d %H:%M:%S")

    return (LOG, "show", "--info", "--debug", "--style", "syslog",
            "--predicate", TIMED_LOG_PREDICATE,
            "--start", local(start_epoch_s), "--end", local(end_epoch_s))


# `log show --style syslog` (the argv ruled by A267 ruling 14 R4) prints this
# exact column header before any entry, and prints it when nothing matched
# (live zero-match capture 07c-exhibit-D3, one line).  The `--style compact`
# header is `Timestamp               Ty Process[PID:TID]` and is REJECTED:
# the guard pins the ruled argv's output, not any header.
TIMED_LOG_SYSLOG_HEADER = "Timestamp                       (process)[PID]"


def timed_log_has_header(text):
    """Did this body come from the ruled ``log show --style syslog`` query?"""
    first = text.splitlines()[0] if text else ""
    return first.rstrip() == TIMED_LOG_SYSLOG_HEADER


def timed_log_window_epoch_s(argv):
    """The epochs the ``--start``/``--end`` strings actually name.

    ``timed_log_argv`` formats local wall time to whole seconds, so the query
    really runs over the union window TRUNCATED at both ends (wider at the
    start, and still past ``sampling_stopped`` at the end because of the one
    second of pad).  ``window_epoch_s`` keeps the float union window the
    envelope was placed by; this is what the argv strings say, parsed back
    from those same strings, so an auditor reading the record never has to
    re-derive the truncation to know what was queried.

    One ambiguity is inherited, not introduced.  The strings carry no UTC
    offset, and ``.timestamp()`` on a naive datetime reads it in the
    machine's local zone.  On the night the clock goes back an hour at the
    end of daylight saving, one wall-clock hour happens TWICE, so a string
    inside it names two different epochs; Python resolves such a string to
    the FIRST of the two (the still-daylight-saving one).  How `log show`
    resolves the same fold-ambiguous string is NOT established -- nothing in
    this project has tested it -- so the record and the query cannot be
    assumed to agree on which of the two epochs was meant (ruling 18 Q3 C5).
    A capture window that straddles the repeated hour is an hour wider or an
    hour narrower than the envelope intended, and the drift and window pins
    are what would show it.
    """

    return [datetime.strptime(argv[argv.index(flag) + 1], "%Y-%m-%d %H:%M:%S").timestamp()
            for flag in ("--start", "--end")]


def timed_log_marker_lines(text):
    """Raw count of log lines carrying any applied-correction marker."""
    return sum(any(marker in line for marker in TIMED_LOG_MARKERS)
               for line in text.splitlines())


def timed_log_moment(line):
    """Seconds since the epoch of a syslog-style line, or None.

    The pattern matches ``YYYY-MM-DD HH:MM:SS.ffffff`` and nothing after it,
    so the ``-0700`` offset that ``--style syslog`` prints is DISCARDED and
    the stamp is read in the machine's local zone, exactly as
    :func:`timed_log_window_epoch_s` reads the argv strings (``--style
    compact`` prints no offset at all).  The repeated hour at the end of
    daylight saving is therefore ambiguous here too, and resolves the same
    way: to the first of its two occurrences.  This value only GROUPS the
    three log lines of one applied correction inside
    ``TIMED_LOG_EVENT_WINDOW_S``; every nonzero count excludes the envelope
    whatever the grouping, so the ambiguity cannot buy an envelope its
    claim-bearing state.
    """
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
# The smallest query bound worth attempting.  A `log show` over one envelope's
# window took 0.70-1.45 s on this machine (A269 gate C4), so five seconds is
# already generous; it exists only so a registration with a tiny gap asks for a
# real query rather than one guaranteed to time out.
ATTESTATION_TIMEOUT_FLOOR_S = 5


def attestation_timeout_s(protocol):
    """Bound the clock query by the GAP it runs in, never by a literal.

    The query runs between the end of one capture and the next spawn, and that
    inter-slot gap is ``slot_pitch_s - envelope_s`` (20 s under v2).  The
    retired literal of 300 s was thirty times the 10 s drift exclusion and a
    hundred and fifty times the 2 s abort bar: one slow `logd` would have
    pushed every later envelope off its schedule, and nothing measured the
    cost.  The bound here is what the gap has LEFT once the teardown's own
    budget (:func:`cleanup_budget_s`) is taken out of it, floored at
    ``ATTESTATION_TIMEOUT_FLOOR_S``: 5 s under v2.  A timeout is not a
    failure of the night -- the envelope becomes ``asserted`` and excluded,
    which is the state a missing query already has.

    Subtracting the teardown's BUDGET rather than the reserve that budget was
    sized from is what makes the pair fit inside one gap.  The invariant is

        attestation_timeout_s(p) + cleanup_budget_s(p) <= gap

    and it holds -- with equality -- for every gap of
    ``ATTESTATION_TIMEOUT_FLOOR_S + 1`` (6 s) or more, where the teardown
    takes ``gap - CLEANUP_BUDGET_RESERVE_S`` and this query takes the 5 s
    that leaves.  Below 6 s the two FLOORS (the teardown's 1 s and this
    function's 5 s) add to 6 and overrun the gap: a teardown and a query that
    each spend their whole floor push the next spawn late by exactly
    ``6 - gap`` seconds.

    That per-slot lateness does NOT compound.  The schedule is absolute
    (``first + (i-1) * slot_pitch_s``) and so is the collector's own deadline
    (``scheduled + duration_s``), so a spawn that is ``6 - gap`` late
    captures for that much less and still ends at its scheduled end: the next
    slot inherits the same ``6 - gap`` and no more.  Whether the residual is
    ever DETECTED therefore depends on one comparison, not on how many slots
    run.  When ``6 - gap`` exceeds ``start_drift_abort_s`` the night ends
    REFUSED at the first spawn the pitch governs (envelope 02), at a named
    abort, instead of producing envelopes nobody can place on the wall
    timeline.  When it does not, every slot is quietly late by that same
    constant and only ``start_drift_max_s`` -- the per-envelope exclusion,
    10 s under v2 -- would ever act on it.  Both halves are executed in
    ``test_a_gap_under_six_seconds_pushes_every_spawn_late_by_six_minus_gap``
    (3 s gap: refused at envelope 02; 5 s gap: twelve slots each 1 s late,
    no abort).  No registration this project runs is in that band -- v2's
    gap is 20 s.
    """

    gap = protocol["slot_pitch_s"] - protocol["envelope_s"]
    return max(ATTESTATION_TIMEOUT_FLOOR_S, gap - cleanup_budget_s(protocol))


def attest_network_time(out, blocked=None, *, timeout):
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

    ``timeout`` is keyword-only and has NO default: the bound belongs to the
    registration the night is running (:func:`attestation_timeout_s` derives
    it from the inter-slot gap), and a default here would let a new call site
    bind the 5 s floor silently while believing it had asked for the gap.
    """

    attestation = {"state": "asserted", "method": TIMED_LOG_ATTESTATION_METHOD,
                   "window_epoch_s": None, "window_argv_epoch_s": None,
                   "window_method": ATTESTATION_WINDOW_METHOD,
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
        if not all(math.isfinite(moment) for moment in window):
            raise ValueError(f"capture window is not finite: {window}")
        # Formatting the window is inside the guard too: an absurd but finite
        # epoch (1e300) raises OverflowError out of `datetime.fromtimestamp`,
        # and an envelope whose window cannot even be written down is
        # `asserted`, never a traceback that ends the night.
        argv = timed_log_argv(*window)
        window_argv = timed_log_window_epoch_s(argv)
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        attestation["reason"] = f"capture window unavailable: {type(exc).__name__}: {exc}"
        return attestation
    attestation.update(window_epoch_s=window, argv=list(argv),
                       window_argv_epoch_s=window_argv)
    try:
        completed = subprocess.run(list(argv), capture_output=True, text=True, timeout=timeout)
        path = out / TIMED_LOG_BASENAME
        path.write_text(completed.stdout)
    except subprocess.TimeoutExpired:
        # The query is abandoned at the gap's edge, not at 300 s: the envelope
        # loses its claim-bearing state, the night keeps its schedule.
        attestation["reason"] = f"timed log query timed out after {timeout:g} s"
        return attestation
    except (OSError, subprocess.SubprocessError) as exc:
        attestation["reason"] = f"timed log query failed: {type(exc).__name__}: {exc}"
        return attestation
    matched = timed_log_matches(completed.stdout)
    attestation.update(exit_code=completed.returncode, log=path.name,
                       log_sha256=digest(path.read_bytes()), matched_lines=matched,
                       matched_marker_lines=timed_log_marker_lines(completed.stdout))
    if completed.returncode != 0:
        attestation["reason"] = f"timed log query exited {completed.returncode}"
    elif not timed_log_has_header(completed.stdout):
        attestation["reason"] = "timed log query returned no header"
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
    means a reader never sees a half-written session record, and a write that
    cannot land is reported in the attestation rather than raised (an
    unwritable envelope directory used to refuse the whole night from here).
    The attestation carries ``session_sha256_before`` -- the digest of the
    file this rewrite replaced -- so the one edit made after the collector
    exits is auditable from the record itself (A269 ruling 10 Q4 iii).
    Nothing else rewrites ``session.json`` after the collector exits:
    under cure 2 there is no finaliser pass, so this digest can only ever
    name the collector's own bytes.
    """

    path = out / "session.json"
    try:
        raw = path.read_bytes()
        session = json.loads(raw)
    except (OSError, ValueError) as exc:
        # The annotation could not even read the record it annotates, so it
        # cannot say the collector's bytes were the ones attested: the
        # envelope loses its claim-bearing state and says why, exactly as a
        # failed rewrite below does.
        attestation["state"] = "asserted"
        attestation["reason"] = f"session record unreadable: {type(exc).__name__}: {exc}"
        return False
    attestation["session_sha256_before"] = digest(raw)
    provenance = session.get("network_time_provenance")
    if not isinstance(provenance, dict):
        provenance = {"state": "unknown",
                      "reason": "collector recorded no network-time provenance"}
    provenance["attestation"] = attestation
    session["network_time_provenance"] = provenance
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(json.dumps(session, sort_keys=True, indent=2, allow_nan=False) + "\n")
        os.replace(temporary, path)
    except (OSError, ValueError) as exc:
        # `ValueError` is caught beside `OSError` (ruling 18 C8) for one
        # pre-existing reason: `json.loads` ACCEPTS the non-standard `NaN`
        # token and `json.dumps(allow_nan=False)` then refuses to write it
        # back, so a collector that recorded a NaN anywhere in its session
        # record used to refuse the whole night from `execute`'s outer
        # handler.  It is the same class of defect as the unlink above: a
        # single envelope's annotation failing, costing twelve.
        #
        # One envelope's annotation must never refuse the NIGHT.  The write is
        # an annotation on a capture that is already complete and already on
        # disk; if it cannot land, the envelope loses its claim-bearing state
        # and says why.  `pilot_summary` reads the executor's own envelope
        # entry whenever the session record carries no attestation, so the
        # `asserted` state set here is the state the summary sees.
        #
        # The withdrawal comes FIRST: nothing below may raise before the
        # envelope has lost its claim-bearing state (cold gate #3 rebuttal
        # ruling 18 Q1).  Cleaning up before withdrawing meant a cleanup that
        # itself raised -- an immutable or root-owned `.tmp` raises
        # `PermissionError`, an `OSError` this handler does not re-enter --
        # left the state `authenticated` and refused the whole night from
        # `execute`'s outer handler.
        attestation["state"] = "asserted"
        attestation["reason"] = f"session rewrite failed: {type(exc).__name__}: {exc}"
        # A landed write and a failed rename leave a COMPLETE session.json.tmp
        # carrying the state just withdrawn; remove it, and if that fails too,
        # say so in the reason rather than refuse the night.
        try:
            temporary.unlink(missing_ok=True)
        except OSError as unlink_exc:
            attestation["reason"] += (f"; stale {temporary.name} not removed: "
                                      f"{type(unlink_exc).__name__}: {unlink_exc}")
        return False
    return True


def attestation_exclusions(state):
    """The ruled vocabulary: only an authenticated envelope is claim-bearing."""
    if state == "authenticated":
        return []
    if state == "slew_attested":
        return [NETWORK_TIME_SLEW_EXCLUSION]
    return [NETWORK_TIME_UNATTESTED_EXCLUSION]


def record_covariates(protocol, night_dir, observer_pid=None):
    """Journal one interval observation per sample, MARKING the observer tree.

    ``observer_pid`` is the chain root -- the executor's own pid, handed down
    by ``execute`` (cold gate 10 QPE01-DAEMON-CONTAMINATION-01, 2026-09-23,
    Q2 BLOCKER).  Without it ``sample_interval`` defaults the observer root to
    the RECORDER's pid, and the recorder is a SIBLING of the collector, so
    `powermetrics`, `top`, `sudo` and the census -- every process the
    measurement itself runs -- were journalled as non-observer consumers:
    every row of both archived nights reads ``observer: false``, and the clean
    night's own power sampler reads 0.111-0.115 busy cores as if it were the
    machine.  With the chain root, ancestry marks the whole tree.
    """

    from joulewise.quiet_admission import sample_interval
    from scripts.sample_quiet_predicate_evidence import cpu_total
    if type(observer_pid) is not int or observer_pid <= 0:
        raise ValueError("record_covariates needs the chain root pid; an unmarked "
                         "observer tree journals the measurement as the machine")
    stop = False
    def stopping(_signum, _frame):
        nonlocal stop
        stop = True
    signal.signal(signal.SIGTERM, stopping)
    journal = night_dir / protocol["recorder_journal"]
    while not stop:
        cpu, began = cpu_total(), time.monotonic()
        try:
            value = sample_interval(protocol["sample_interval_s"], observer_pid=observer_pid)
            row = {"observation": value, "error": None}
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            row = {"observation": None, "error": str(exc)}
        row.update(evidence_status="PROVISIONAL", role="covariate_only", admits_nothing=True,
                   observer_cpu_s=cpu_total() - cpu, monotonic_start=began, monotonic_end=time.monotonic())
        append_event(journal, row)
    return 0


NON_OBSERVER_EXCLUSION = night_gate.NON_OBSERVER_EXCLUSION


class NonObserverAbort(ValueError):
    """Two consecutive envelopes lost to a busy non-observer process.

    Its own type so the executor's refusal document can carry the RULED reason
    (`non_observer_process_busy`) instead of the generic probe error every
    other in-chain abort writes.
    """


def non_observer_rule(protocol):
    """The registration's per-envelope rule, or None when it does not carry one.

    v2 has no such rule and `exclusions` is byte-pinned, so a v2 night must
    never emit the reason (the defect A269 ruling 10 Q2 forbids).  When the
    rule IS present it must be complete: a half-written rule is a registration
    defect, and refusing here is cheaper than discovering it at envelope 12.
    """

    rule = protocol.get("non_observer_process_busy")
    if rule is None:
        return None
    bar = rule.get("bar_core_seconds") if isinstance(rule, dict) else None
    consecutive = rule.get("abort_after_consecutive") if isinstance(rule, dict) else None
    if (type(bar) not in (int, float) or type(bar) is bool or not math.isfinite(bar) or bar <= 0
            or type(consecutive) is not int or consecutive < 1):
        raise ValueError("non_observer_process_busy needs a positive bar_core_seconds "
                         "and an integer abort_after_consecutive")
    if NON_OBSERVER_EXCLUSION not in protocol["exclusions"]:
        raise ValueError("non_observer_process_busy rule without its exclusion reason")
    return rule


# The summary's `observer_definition` (fix round 1, lens N5): registration
# v3's ruled `observer_floor.definition` sentence, verbatim, followed by the
# sibling fact.  The ruled sentence's "including ... load recorder" is left as
# ruled; the magistrate holds its inaccuracy for the block-two consult.
OBSERVER_DEFINITION = ("SELF + all reaped CHILDREN, including collector, power recorder, load recorder "
                       "and census; never subtracted, with the 30 s load recorder a sibling process "
                       "reported beside it (see observer_floor_components_role)")
EXECUTOR_NON_OBSERVER_VERDICT = "executor_non_observer_process_busy"
NON_OBSERVER_DISAGREEMENT = "non_observer_verdict_disagreement"


def non_observer_verdict_key(hits):
    """What two non-observer verdicts must share to agree.

    Process, pid, start identity and core-seconds (to 1e-6 core-s, so a
    JSON round trip of the executor's floats never reads as disagreement).
    Anything that is not a list of hit objects is its own key, so a malformed
    stored verdict disagrees rather than refusing the whole summary.
    """

    if not isinstance(hits, list) or not all(isinstance(hit, dict) for hit in hits):
        return ("unreadable", repr(hits))
    return sorted((str(hit.get("process")), repr(hit.get("pid")), repr(hit.get("start_identity")),
                   f"{float(hit['core_seconds']):.6f}"
                   if type(hit.get("core_seconds")) in (int, float) else repr(hit.get("core_seconds")))
                  for hit in hits)


UNMARKED_JOURNAL = ("recorder journal carries no observer-marked consumer; "
                    "ancestry marking failed")


def require_observer_marked(support):
    """Refuse a v3 envelope whose journal rows name processes but mark none.

    Under registration v3 the recorder runs with the chain root's pid, so the
    measurement's own processes -- at least `powermetrics`, a full-time
    consumer -- carry `observer: true` in every envelope.  Rows that name
    consumers yet mark none mean the ancestry marking failed, and the
    per-envelope rule would then exclude every envelope while blaming the
    power sampler, hiding the real cause (Fable lens N8, adopted by the
    magistrate as an evidence-quality guard in fix round 1).  Rows with no
    consumers at all say nothing either way and pass.
    """

    named = False
    for row in support:
        metrics = (row.get("observation") or {}).get("metrics")
        consumers = metrics.get("top_consumers") if isinstance(metrics, dict) else None
        if isinstance(consumers, list) and consumers:
            named = True
            if any(isinstance(c, dict) and c.get("observer") is True for c in consumers):
                return
    if named:
        raise ValueError(UNMARKED_JOURNAL)


def non_observer_busy(rule, support):
    """Per non-observer process identity, the busy-core-seconds at or over the bar.

    The statistic is an INTEGRAL, not a median (cold gate 10, 2026-09-23, Q2
    MATERIAL): an eight-sample burst at 1.5 busy cores costs about 270 J and
    passes a twenty-sample median, while 30 core-seconds -- the registered
    `smallest_holdable_share` 0.05 held for the whole 600 s envelope -- is
    about 7.7 J of the 480 s interior, above the 5 J claim bar.  Identity is
    (pid, start identity), so a recycled pid is a different process.

    `support` is the envelope's journal rows, already joined by the
    registration's own monotonic-support rule.  A row whose observation failed
    carries no consumers at all and is skipped; a row that HAS metrics and no
    readable `top_consumers` is a corrupt journal, and refuses.
    """

    totals, names = {}, {}
    for row in support:
        observation = row.get("observation")
        metrics = (observation or {}).get("metrics")
        if not isinstance(metrics, dict):
            continue
        interval_s = observation.get("interval_s")
        consumers = metrics.get("top_consumers")
        if (not isinstance(consumers, list) or type(interval_s) not in (int, float)
                or type(interval_s) is bool or not math.isfinite(interval_s) or interval_s <= 0):
            raise ValueError("recorder journal row carries metrics without usable "
                             "top_consumers and interval_s")
        for consumer in consumers:
            if (not isinstance(consumer, dict) or type(consumer.get("observer")) is not bool
                    or type(consumer.get("pid")) is not int or type(consumer.get("pid")) is bool
                    or not isinstance(consumer.get("command"), str)
                    or type(consumer.get("busy_cores")) not in (int, float)
                    or type(consumer.get("busy_cores")) is bool
                    or not math.isfinite(consumer["busy_cores"]) or consumer["busy_cores"] < 0):
                raise ValueError("malformed recorder journal consumer")
            if consumer["observer"]:
                continue
            identity = (consumer["pid"], consumer.get("start_identity"))
            totals[identity] = totals.get(identity, 0.0) + consumer["busy_cores"] * interval_s
            names[identity] = consumer["command"]
    hits = [{"process": os.path.basename(names[identity]), "pid": identity[0],
             "start_identity": identity[1], "core_seconds": total,
             "bar_core_seconds": rule["bar_core_seconds"]}
            for identity, total in totals.items() if total >= rule["bar_core_seconds"]]
    return sorted(hits, key=lambda hit: (-hit["core_seconds"], hit["pid"]))


def envelope_support(covariates, scheduled, protocol):
    """The registration's join: recorder intervals fully inside the envelope."""

    if scheduled is None:
        return []
    return [row for row in covariates
            if row.get("monotonic_start") is not None and row.get("monotonic_end") is not None
            and row["monotonic_start"] >= scheduled
            and row["monotonic_end"] <= scheduled + protocol["envelope_s"]]


def envelope_span_s(session):
    """The collector's own monotonic span, from its two clock stamps.

    Returns None when either stamp is missing, so the caller can refuse by
    name with the envelope index rather than raise a KeyError here.
    """

    stamps = [session.get("start_stamp"), session.get("end_stamp")]
    if any(not isinstance(stamp, dict) for stamp in stamps):
        return None
    start, end = (stamp.get("monotonic_before_s") for stamp in stamps)
    if any(type(value) not in (int, float) or type(value) is bool or not math.isfinite(value)
           for value in (start, end)):
        return None
    return end - start


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
    values, all_rows, replay_recorders = [], [], []
    journal = directory.parent / protocol["recorder_journal"]
    covariates = [json.loads(line) for line in journal.read_text().splitlines() if line] if journal.exists() else []
    clean_busy = []
    rule = non_observer_rule(protocol)
    for entry in envelopes:
        excluded = []
        if entry.get("collector_exit", 0) != 0:
            excluded.append("collect_error")
        if entry.get("cleanup", {}).get("cleanup_proven") is False:
            excluded.append("cleanup_unproven")
        scheduled = entry.get("scheduled_mono_s")
        support = envelope_support(covariates, scheduled, protocol)
        busy = [(r.get("observation") or {}).get("metrics", {}).get("busy_cores") for r in support]
        distribution = harness.quantiles(busy)
        entry = {**entry, "busy_cores": {**distribution, "median": distribution["p50"]},
                 "busy_cores_samples": len([v for v in busy if harness.number(v) is not None]),
                 "recorder_observer_cpu_s": sum(r.get("observer_cpu_s") or 0 for r in support)}
        # The registered per-envelope rule (cold gate 10, 2026-09-23, Q2): a
        # non-observer process that held the machine for `bar_core_seconds`
        # costs this envelope its claim, and the offenders are NAMED on the
        # row so the reason can be read without the journal.
        #
        # The summary ALWAYS writes its own list, re-derived from the journal
        # on disk, under `non_observer_process_busy` (empty when there is no
        # offender).  The executor's in-chain verdict -- the list it decided
        # the abort on -- is kept beside it under
        # `executor_non_observer_process_busy`, and the two are compared.
        # Before fix round 1 (lens S2) the executor's list passed through
        # whenever the summary found nothing, so a row could name an offender
        # while its `excluded` lacked the reason, and a test comparing the two
        # compared the executor with itself.
        if rule is not None:
            require_observer_marked(support)
            offenders = non_observer_busy(rule, support)
            if offenders:
                excluded.append(NON_OBSERVER_EXCLUSION)
            executor_verdict = entry.get(NON_OBSERVER_EXCLUSION)
            entry = {k: v for k, v in entry.items() if k != NON_OBSERVER_EXCLUSION}
            entry[NON_OBSERVER_EXCLUSION] = offenders
            if executor_verdict is not None:
                entry[EXECUTOR_NON_OBSERVER_VERDICT] = executor_verdict
                entry[NON_OBSERVER_DISAGREEMENT] = (non_observer_verdict_key(offenders)
                                                    != non_observer_verdict_key(executor_verdict))
        out = directory / f"envelope-{entry['index']:02d}"
        # The session record is read FIRST and kept even when the rest of the
        # envelope is unreadable, because the replay check below must see
        # every session that exists.  Reading both inside one `try` meant a
        # missing or unparseable `rounds.jsonl` skipped the envelope before
        # the check, and a replay night whose journals were all lost failed
        # OPEN -- INCONCLUSIVE, `partial`, rc 0 (execution lens 17b S1).
        session, rows, unreadable = None, None, None
        try:
            session = json.loads((out / "session.json").read_text())
            rows = [json.loads(line) for line in (out / "rounds.jsonl").read_text().splitlines() if line]
        except (OSError, ValueError) as exc:
            unreadable = exc
        # HARVEST-side fail-closed point of the bench replay (cold gate #3
        # ruling 10 Q7; brief D6).  Every session this summary reads must say,
        # in its own record, that a real `powermetrics` produced its frames.
        # An absent key is not a claim of production provenance either: the
        # bench replay writes "replay", and a session predating the key cannot
        # attest to anything, so both refuse.  The refusal is the SUMMARY's,
        # not an exclusion reason -- A269 byte-pins the registration's
        # exclusion list, and a new reason would force a registration v3.
        # `power: null` is NOT a contradicted claim of production provenance:
        # the collector initialises it to null and only fills it once a
        # recorder was BUILT, so a null is an envelope that refused before any
        # recorder existed -- the network-time provenance refusal path, which
        # excludes itself on its own terms.  Refusing a whole REAL night as a
        # "replay" because one envelope refused early is a false record, and
        # it was reachable (lane contract lens 17a S1).  Anything else -- a
        # power record that exists and does not say `powermetrics` -- refuses.
        power = session.get("power") if session is not None else None
        if session is not None and power is not None:
            recorder_kind = power.get("recorder_kind") if isinstance(power, dict) else None
            if recorder_kind != harness.RECORDER_KIND_PRODUCTION:
                replay_recorders.append({"index": entry["index"], "recorder_kind": recorder_kind})
        if unreadable is not None:
            values.append({**entry, "excluded": excluded + ["incomplete_interior_support"],
                           "error": str(unreadable), "joules": None})
            continue
        all_rows.extend(rows)
        hard = hard_exclusions(rows)
        excluded.extend(hard)
        # Clock-discipline attestation (ruling 14 R4): only an envelope whose
        # capture window carries no applied correction in the ``timed`` log is
        # claim-bearing.  A slew inside the window and a failed or missing
        # query are both HARD exclusions; the session record is authoritative
        # and the executor's own envelope entry is the fallback, so a summary
        # re-derived from disk reaches the same verdict.
        #
        # It is computed BEFORE the clean busy-core diagnostic below because
        # that diagnostic describes the machine an envelope was captured on:
        # an envelope whose clock was slewed, or whose discipline could not be
        # attested at all, is not a clean-machine observation either, and
        # feeding its covariates into the "clean" distribution would let an
        # excluded envelope shape the number the paper reports.
        provenance = session.get("network_time_provenance")
        attestation = provenance.get("attestation") if isinstance(provenance, dict) else None
        state = (attestation.get("state") if isinstance(attestation, dict)
                 else entry.get("network_time_attestation"))
        unattested = attestation_exclusions(state)
        excluded.extend(unattested)
        if not hard and not unattested:
            clean_busy.extend(busy)
        interior = session.get("interior", {})
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
                       # The accounting window of `whole_envelope_observer_cpu_s`:
                       # the collector's own monotonic span, not the nominal 600 s
                       # and not the recorder's support (cold gate round 3,
                       # ruling 31 MATERIAL -- dividing by either of those two is
                       # what the round-2 charge and exhibit G each got wrong).
                       "envelope_span_s": envelope_span_s(session),
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
    # WHOLE-ENVELOPE observer cost, including rejected envelopes; never
    # subtracted from energy, never a retention input (cold gate round 3,
    # synthesis 35, adopting ruling 31's reporting limbs).
    #
    # What this replaces and why: until 2026-09-23 the floor summed each
    # ROUND's `observer_cpu_s` -- the sampler's worker/census block only --
    # over the rounds' own support, and never read the
    # `whole_envelope_observer_cpu_s` the session had already recorded two
    # lines above.  The 100 ms power recorder is reaped by the collector
    # AFTER the round block ends, so two thirds of the apparatus was missing:
    # both archived nights reported ~0.053 cores where the whole envelope
    # costs 0.176 and 0.159.
    #
    # What "whole" holds, and what it does not (magistrate ruling on lens S1,
    # fix round 1, 2026-09-23): `whole_envelope_observer_cpu_s` is the
    # COLLECTOR's own CPU plus the CPU of every child the collector reaped
    # (RUSAGE_SELF + RUSAGE_CHILDREN, scripts/sample_quiet_predicate_evidence.py
    # `cpu_total`).  The 30 s load recorder is launched by the EXECUTOR, as a
    # sibling of the collector, and journals its own CPU per row; it is
    # therefore NOT inside whole.  So the components split in two:
    #   - inside whole: `round_block` (the sampler's worker/census block) and
    #     `power_recorder_residue` = whole - round_block, which is everything
    #     else the collector reaped -- the 100 ms power recorder, unattributed
    #     by PID at this revision.  These two sum to whole by definition.
    #   - outside whole: `load_recorder`, the sibling's own journaled CPU.
    # The ruled floor stays sum(whole) / sum(span).  The companion
    # `observer_floor_including_load_recorder_cores` adds the sibling back
    # ((sum(whole) + sum(load_recorder)) / sum(span)); it is REPORTED only and
    # never feeds a stop.
    readable = [v for v in values if v.get("error") is None]
    shares = []
    for value in readable:
        whole, span = value.get("whole_envelope_observer_cpu_s"), value.get("envelope_span_s")
        if harness.number(whole) is None or harness.number(span) is None or span <= 0:
            raise ValueError(f"envelope {value['index']}: whole_envelope_observer_cpu_s or "
                             "envelope span missing; absent evidence is never a pass")
        shares.append(whole / span)
        round_block = value.get("observer_cpu_s")
        value["observer_floor_components"] = {
            "round_block": {"cpu_s": round_block, "inside_whole": True},
            "power_recorder_residue": {"cpu_s": whole - (round_block or 0), "inside_whole": True},
            "load_recorder": {"cpu_s": value.get("recorder_observer_cpu_s"), "inside_whole": False},
            "whole_envelope_observer_cpu_s": whole, "envelope_span_s": span}
    observer_support_s = sum(v["envelope_span_s"] for v in readable)
    observer_whole_s = sum(v["whole_envelope_observer_cpu_s"] for v in readable)
    observer_floor = observer_whole_s / observer_support_s if observer_support_s else None
    observer_floor_including_load_recorder = (
        (observer_whole_s + sum(v.get("recorder_observer_cpu_s") or 0 for v in readable))
        / observer_support_s if observer_support_s else None)
    observer_variation = statistics.stdev(shares) if len(shares) >= 2 else None
    # The stop branch keeps its v2 FORM and cause name (synthesis 35 §3): it is
    # now fed the corrected statistic, and a clean pilot is EXPECTED to stop on
    # it (0.16-0.18 cores of apparatus against a 0.05-core smallest level).
    # That is the honest registered result, not a defect to soften.
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
        "observer_variation_cores": observer_variation,
        "observer_floor_including_load_recorder_cores": observer_floor_including_load_recorder,
        "observer_floor_components_role": "per envelope, on envelopes[*].observer_floor_components, "
            "each component with its cpu_s and an explicit inside_whole flag: round_block (the "
            "sampler's worker/census block) and power_recorder_residue (whole_envelope_observer_cpu_s "
            "minus round_block: everything else the collector reaped, the 100 ms power recorder's "
            "cost, unattributed by PID at this revision) are inside whole_envelope_observer_cpu_s and "
            "sum to it; load_recorder (the 30 s covariate recorder) is a sibling process of the "
            "collector, launched by the executor, so its CPU is outside whole_envelope_observer_cpu_s "
            "and outside observer_floor_cores; observer_floor_including_load_recorder_cores = "
            "(sum of whole_envelope_observer_cpu_s + sum of load_recorder) / sum of spans over the "
            "same readable envelopes, reported only, never a stop input",
        "s_upper": s_upper,
        "s_upper_reason": "one-sided upper 90% chi-square bound; independent normal pair differences assumed"
            if sufficient else "fewer than four retained disjoint pairs or eight retained envelopes; no top-up",
        "block_two_pairs": stop["pairs"], "block_two_stop": stop,
        "block_two_pairs_reason": "ruling 46b: " + protocol["sizing"]["formula"] +
            f"; delta_j={protocol['sizing']['delta_j']}; stop above {protocol['sizing']['maximum_pairs']} pairs"
            if sufficient else "INCONCLUSIVE; no sizing",
        "whole_campaign_observer_cpu_s": observer_cpu_s,
        "observer_definition": OBSERVER_DEFINITION,
        "cutoff_authority": False, "top_up": False}
    if replay_recorders:
        # Nothing this night produced is a measurement.  The status, the
        # retained set and the spread bound are replaced outright rather than
        # annotated -- and so is EVERY energy number the document would
        # otherwise carry: the per-envelope joules and interiors, the sizing
        # and adjacent pairs, and every spread or drift statistic derived
        # from them (lane contract lens 17a N2 -- the claim below that no
        # reader can lift a number was false while `sizing_pairs` and
        # `envelopes[*].joules` survived the override).  What stays is the
        # SCHEDULE side: index, scheduled and actual instants, start drift,
        # collector exit, cleanup, attestation and busy-core covariates --
        # the figures the bench replay exists to produce, none of which is an
        # energy.
        energy_blanked = [{**v, "joules": None, "combined_joules": None, "interior": None}
                          for v in report["envelopes"]]
        report.update({
            "status": REPLAY_NEVER_EVIDENCE, "evidence_status": REPLAY_NEVER_EVIDENCE,
            "retained": [], "s_upper": None,
            "s_upper_reason": "replay recorder: no envelope of this night is a measurement",
            "envelopes": energy_blanked,
            "sizing_pairs": [], "retained_pairs": 0, "adjacent_pairs": [],
            "adjacent_pair_sd_j": None, "pair_sd_j": None, "pair_df": None,
            "s_upper_factor": None, "single_envelope_sd_j": None,
            "unfiltered_single_envelope_sd_j": None,
            "first_to_last_retained_drift_j": None, "pairs_above_3_pair_sd": [],
            "max_abs_delta_j": None, "block_two_pairs": None, "block_two_stop": None,
            "block_two_pairs_reason": "replay recorder: no sizing, no spread, no energy",
            "replay_recorder_envelopes": replay_recorders,
            "replay_recorder_reason": "one or more session.json records do not carry "
                                      f"power.recorder_kind == {harness.RECORDER_KIND_PRODUCTION!r}"})
    harness.write_json(directory / "summary.json", report)
    if replay_recorders:
        (directory / "summary.md").write_text(
            f"# QPE-01 {REPLAY_NEVER_EVIDENCE}\n\n"
            f"Status: {REPLAY_NEVER_EVIDENCE}. Envelopes "
            f"{', '.join(str(r['index']) for r in replay_recorders)} were produced by a recorder "
            f"that is not `powermetrics`, so this night is a BENCH REPLAY and none of it is a "
            "measurement: no envelope is retained, no spread bound is computed, and the executor "
            "refuses the night. Every energy number is blanked with it: no per-envelope "
            "joules or interior, no sizing or adjacent pairs, no spread or drift statistic "
            "derived from them. The per-envelope SCHEDULE, cleanup, attestation and "
            "start-drift diagnostics in summary.json remain, because measuring the "
            "inter-slot tail is what the replay is for.\n")
        return report
    (directory / "summary.md").write_text(
        "# QPE-01 pilot (PROVISIONAL, descriptive)\n\n" +
        f"Status: {report['status']}. Retained {len(retained)}/{protocol['envelopes']} envelopes; {len(deltas)} disjoint pairs.\n\n" +
        f"Disjoint-pair sample SD: {pair_sd} J (df={df}); upper 90% bound: {s_upper} J. " +
        "This chi-square construction assumes independent, normally distributed pair differences.\n\n" +
        f"Block-two pairs: {stop['pairs']}; sizing stop: {stop['outcome']}. No sizing when INCONCLUSIVE.\n\n" +
        f"Diagnostics only: {len(overlapping)} overlapping differences (SD {report['adjacent_pair_sd_j']} J); " +
        f"unfiltered single-envelope SD (every envelope with a readable energy value, excluded envelopes included) {report['unfiltered_single_envelope_sd_j']} J; " +
        f"first-to-last retained drift {report['first_to_last_retained_drift_j']} J. " +
        f"Overlapping adjacent pairs with |delta| > 3 * s_pair: {large_pairs}. Values are in summary.json.\n\n" +
        ((f'Busy cores are recorded covariates. A process outside the measurement apparatus using '
          f'{rule["bar_core_seconds"]:g} or more core-seconds inside an envelope excludes that envelope. ')
         if rule else "Busy cores are recorded covariates and never an exclusion input. ") +
        "Every exclusion and partial interior is retained in summary.json. No top-up, cutoff or activation authority. " +
        "Block two is not authored by this summary.\n")
    return report


# The gap between the end of one capture and the next spawn (20 s under v2:
# slot_pitch_s 620 - envelope_s 600) holds the collector's exit, the plist
# parse, the anchor derivation, the group teardown and the clock attestation.
# The teardown's budget is the gap minus a reserve that the attestation's
# `log show` fits in (worst observed 1.45 s; A269 gate C4 measured 0.70/0.84 s),
# so a teardown can never eat the attestation's time or run into the next
# spawn.  `attestation_timeout_s` is the function that spends that reserve,
# and it asks for exactly what this budget leaves of the gap -- the two are
# the two parts of one gap, never two claims on the same seconds.  Derived
# from the registration at the call site, never a literal.
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
    consecutive_non_observer = 0
    refusal_reason = "night_probe_error"
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
        recorder = launch("recorder", [sys.executable, "-B", "-m", "joulewise.quiet_predicate_campaign",
                                       "record", "--observer-pid", str(os.getpid())])
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
            cleanup_began = time.monotonic()
            cleanup = cleanup_groups(journal, children, budget_s=cleanup_budget_s(protocol),
                                     exclude={recorder.pid})
            cleanup_wall_s = time.monotonic() - cleanup_began
            # Authenticate this envelope's clock discipline now, while the log
            # store still holds the window (ruling 14 R4); the state joins the
            # envelope's own provenance and the exclusion vocabulary.  It runs
            # HERE -- after the teardown, before the next slot's sleep -- so
            # `log show`'s work inside `logd` can never land in a recorded
            # window as unattributable observer energy (A269 ruling 10 Q4 ii).
            # If the teardown did not prove every supervised group gone, a
            # recorder may still be sampling, and the query is refused rather
            # than run beside it: the envelope becomes `asserted`.
            # The query's bound is this registration's gap, and its WALL COST
            # is journaled: an unmeasured second on the inter-slot path is how
            # the drift A269 cures got in, and the next night's budget is read
            # off these numbers, not guessed.
            attestation_began = time.monotonic()
            attestation = attest_network_time(out, blocked=capture_still_live(cleanup),
                                              timeout=attestation_timeout_s(protocol))
            attestation_wall_s = time.monotonic() - attestation_began
            record_attestation(out, attestation)
            # This envelope's registered non-observer verdict, taken from the
            # recorder journal as it stands now -- the same rows, the same
            # join and the same integral the summary re-derives from disk
            # (cold gate 10, 2026-09-23, Q2).  It is computed HERE because the
            # abort is in-chain: two consecutive envelopes lost to a busy
            # non-observer process end the night about 31 minutes after t0
            # rather than three hours later.
            non_observer = []
            if non_observer_rule(protocol) is not None:
                # The recorder writes this file on its first sample, so it may
                # not exist yet when envelope 01 ends; no rows is no exclusion.
                journal_path = night_dir / protocol["recorder_journal"]
                journal_rows = [json.loads(line) for line
                                in (journal_path.read_text().splitlines()
                                    if journal_path.exists() else [])
                                if line]
                support = envelope_support(journal_rows, scheduled, protocol)
                # The summary's evidence-quality guard, run HERE too (fix
                # round 2, delta re-audit D1): a journal whose consumers carry
                # no observer mark means the ancestry marking failed, and the
                # rule below would then count the measurement's own processes
                # and abort as `non_observer_process_busy` -- a busy-machine
                # reason for a broken measurement.  The guard raises a plain
                # ValueError, so the refusal carries `night_probe_error` and
                # the marking failure's own text.
                require_observer_marked(support)
                non_observer = non_observer_busy(non_observer_rule(protocol), support)
            envelopes.append({"index": index, "scheduled_mono_s": scheduled, "actual_mono_s": actual,
                              NON_OBSERVER_EXCLUSION: non_observer,
                              "start_drift_s": actual - scheduled, "collector_exit": code, "cleanup": cleanup,
                              # The teardown's own wall cost, beside the
                              # attestation's, for the same reason: the gap is
                              # 20 s and the next night's budget is read off
                              # these numbers rather than guessed.
                              "cleanup_wall_s": cleanup_wall_s,
                              "network_time_attestation": attestation["state"],
                              # The attestation's own account of itself, on the
                              # row (ruling 18 C7).  A rewrite that could not
                              # land leaves `session.json` unannotated, so
                              # WITHOUT this key the reason -- which names the
                              # failure that cost the envelope its claim --
                              # exists only in the executor's memory and dies
                              # with the process.
                              "network_time_attestation_reason": attestation.get("reason"),
                              "network_time_attestation_wall_s": attestation_wall_s,
                              "network_time_attestation_matched_lines": attestation["matched_lines"]})
            append_event(night_dir / "evidence_envelopes.jsonl", envelopes[-1])
            print(f"envelope_end index={index} rc={code} cleanup_proven={cleanup['cleanup_proven']}"
                  f" clock_attestation={attestation['state']}", flush=True)
            consecutive_cleanup_failures = 0 if cleanup["cleanup_proven"] else consecutive_cleanup_failures + 1
            if consecutive_cleanup_failures >= 2:
                raise ValueError("two consecutive cleanup_unproven envelopes")
            consecutive_non_observer = consecutive_non_observer + 1 if non_observer else 0
            rule = non_observer_rule(protocol)
            if rule is not None and consecutive_non_observer >= rule["abort_after_consecutive"]:
                raise NonObserverAbort(
                    f"{consecutive_non_observer} consecutive envelopes excluded "
                    f"{NON_OBSERVER_EXCLUSION}; last: "
                    + ", ".join(f"{hit['process']} pid {hit['pid']} "
                                f"{hit['core_seconds']:.1f} core-s "
                                f"(bar {hit['bar_core_seconds']})" for hit in non_observer))
            if recorder.poll() is not None:
                raise ValueError("evidence covariate recorder exited early")
        outcome = "partial" if any(e["collector_exit"] != 0 or not e["cleanup"]["cleanup_proven"] for e in envelopes) else "complete"
    except (OSError, ValueError, KeyboardInterrupt, subprocess.SubprocessError) as exc:
        error = f"{type(exc).__name__}: {exc}"
        if isinstance(exc, NonObserverAbort):
            refusal_reason = NON_OBSERVER_EXCLUSION
    finally:
        for signum in old:
            signal.signal(signum, signal.SIG_IGN)
        network_time_restored = restore_network_time(night_dir)
        cleanup = cleanup_record(night_dir, children)
        # Read off the SESSIONS as well as the environment (execution lens
        # 17b NIT): the outcome document's `recorder_kind` was derived from
        # the executor's own environment alone, and the two can disagree --
        # a session that says `replay` under an executor that was not told to
        # replay is the disagreement that matters, and it wins.
        replay_sessions = False
        try:
            report = pilot_summary(directory, protocol, envelopes,
                                   harness.cpu_total() - cpu_start if cleanup["cleanup_proven"] else None)
            replay_sessions = any(row.get("recorder_kind") == harness.RECORDER_KIND_REPLAY
                                  for row in report.get("replay_recorder_envelopes") or [])
            if report.get("status") == REPLAY_NEVER_EVIDENCE:
                # Brief D6: a night any replay recorder touched is REFUSED
                # here, at the harvest boundary, with rc 2 -- while every
                # slot's row stays in `evidence_envelopes.jsonl`, appended
                # inside the loop above, because those rows are the drift
                # measurement the bench replay exists to take.
                outcome, error = "refused", replay_refusal_error(error)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            outcome, error = "refused", "pilot summary failed: " + str(exc)
        # The harvest-side refusal above reads the SESSIONS, so it is silent
        # when none of them can be read -- a feeder that crashes on a
        # malformed archive kills every collector before it writes, and the
        # night then ends `partial`/rc 0 with `recorder_kind: "replay"` as the
        # only tell (lane contract lens 17a S2).  This point reads the
        # executor's OWN environment instead: the process that was told to
        # replay refuses, whatever its children managed to write.
        if os.environ.get(harness.REPLAY_ENV):
            outcome, error = "refused", replay_refusal_error(error)
        if not cleanup["cleanup_proven"]:
            outcome, error = "refused", error or "final evidence cleanup unproven"
        if outcome == "refused":
            write_refusal(night_dir, plan, error or "evidence execution aborted",
                          reason=refusal_reason)
        harness.write_json(night_dir / "evidence_outcome.json", {"outcome": outcome, "error": error,
            "envelopes_attempted": len(envelopes), "cleanup_proven": cleanup["cleanup_proven"],
            # RUN-side marker (brief D6): the outcome document names the
            # recorder the collectors were told to use, so a reader holding
            # only this file can tell a bench replay from a night.
            "recorder_kind": harness.RECORDER_KIND_REPLAY
                             if os.environ.get(harness.REPLAY_ENV) or replay_sessions
                             else harness.RECORDER_KIND_PRODUCTION,
            "network_time_restored": network_time_restored})
        for signum, handler in old.items():
            signal.signal(signum, handler)
    print(f"evidence_end outcome={outcome} cleanup_proven={cleanup['cleanup_proven']}"
          f" network_time_restored={network_time_restored}", flush=True)
    # A failed restore leaves the machine, not the measurement, in the wrong
    # state: the captured envelopes were taken under a proven OFF and stay
    # valid.  It gets its own code (3, distinct from the refusal 2) so the
    # harvester re-attempts the restore and surfaces it.
    #
    # PRECEDENCE: the refusal wins.  Code 3 means "the envelopes are valid,
    # the machine is not", so a harvester acting on that documented meaning
    # must never be handed a night that refused and produced no valid
    # envelopes -- which is what returning 3 for a refused night whose restore
    # also failed did.  The restore's own verdict is on
    # `evidence_outcome.json` (`network_time_restored`) on every path, so
    # nothing is hidden by giving 2 the precedence.
    base = 0 if outcome in {"complete", "partial"} and cleanup["cleanup_proven"] else 2
    return 3 if base == 0 and not network_time_restored else base


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "run", "record", "refuse"))
    parser.add_argument("--reason", default="evidence wrapper refused before execution")
    # The chain root, handed to `record` by `execute`; see `record_covariates`.
    parser.add_argument("--observer-pid", type=int)
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
            return record_covariates(protocol, Path(os.environ["NIGHT_DIR"]),
                                     observer_pid=args.observer_pid)
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
