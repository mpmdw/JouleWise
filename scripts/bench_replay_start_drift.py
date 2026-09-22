#!/usr/bin/env python3
"""The ruled daytime bench replay: real chain, real collector, replayed frames.

Cold gate #3 ruling 10 Q7 (P7.1) and A269 ruling 10 Q3's replacement R6 clause
make one thing a precondition of preparing the pilot-night re-run: a daytime
bench replay -- "real ``execute`` and real collector with an injected recorder
replaying an archived plist, no sudo, no measurement, never labeled R6
evidence" -- must show chain-level ``start_drift_s`` <= 0.5 s on EVERY slot.
This script is that replay.

WHAT IT MEASURES, and why 0.5 s is the bar.  Under registration v2 the
schedule pitch is 620 s and the capture is 600 s, so each slot is followed by
a 20 s GAP in which the collector exits and is reaped, its process groups are
censused (``cleanup_groups``, budget 15 s) and the clock-discipline
attestation runs (``log show``, timeout 5 s).  Spawn instants are ABSOLUTE
(``first + (i-1) * pitch``), so drift never accumulates: slot i's
``start_drift_s`` is exactly how far its predecessor's finalisation tail
overran the 20 s gap.  The pilot night of 2026-09-22 ran that tail at 7.6-10.1 s
on ten of twelve slots under the old cadence; this bench is the first
measurement of it under the cured one, and of the attestation's own wall cost
(the residual the A267 execution lens raised as B1).

WHY IT IS NEVER EVIDENCE.  Three independent points refuse it (brief D6):
at ARM, ``run_night._chain_environment`` RAISES if the replay variable is in
the environment, so no armed night can carry it; at RUN, every
``session.json`` records ``power.recorder_kind: "replay"``, the outcome
document records the same, the plan id is prefixed ``bench-replay-`` and the
custody root is under ``~/night-bench/`` and never ``~/night-custody/``; at
HARVEST, ``pilot_summary`` admits only ``recorder_kind == "powermetrics"`` and
otherwise writes ``REPLAY_NEVER_EVIDENCE`` with ``retained: []`` and
``s_upper: null``, and ``execute`` returns 2 (``refused``,
``replay_recorder``) -- while ``evidence_envelopes.jsonl`` keeps every slot's
row, which is where the drift numbers live.  A refused night is exactly what a
correct bench run looks like.

WHAT IS REAL AND WHAT IS NOT.  Real: ``execute`` itself (the schedule, the
abort rule, the teardown, the attestation), the collector, its rounds, its
hard probes, its censuses, ``establish_network_time_off`` and
``restore_network_time`` including receipt writing and the imported
exact-stdout comparison, and the ``log show`` attestation against the live
unified log.  Not real: the recorder (a frame feeder replaying an archived
plist) and the ``systemsetup`` executable (a variable-gated stub that toggles
nothing).  No sudo runs at any point.

USAGE

    python3 -B scripts/bench_replay_start_drift.py --archive <harvest root> --smoke
    python3 -B scripts/bench_replay_start_drift.py --archive <harvest root> \\
        --expect-sha <merge sha> --artifact <path>.md --raw <path>.json

``--smoke`` runs a scaled protocol copy (envelope 60 s, pitch 80 s, settle 5 s,
three slots, ~5 min) to prove the plumbing -- writer cadence, anchor status,
the attestation running in the gap, every fail-closed marker -- and stamps
``kind: "smoke"`` into its output.  A smoke is NOT the artifact: the bar is
produced by the 20 s gap, and scaling changes the gap, so ``--smoke`` refuses
to write a file named like the ruled artifact.  The full run uses
``frozen_protocol()`` verbatim (600 + 11*620 + 600 = 8020 s = 2 h 13 m 40 s).
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import night_gate, quiet_predicate_campaign as campaign
from scripts import gen_evidence_night
from scripts.gen_derivation_night import GenerationRefusal
from scripts import sample_quiet_predicate_evidence as harness

SCHEMA = "joulewise.bench_replay_start_drift.v1"
# The ruled bar (A269 ruling 10 Q3 replacement R6 clause, via cold gate #3
# Q7): chain-level start drift on EVERY slot.  It is NOT the night's 2 s
# in-chain abort threshold -- the two bars are sequential, not alternatives,
# and comparing against 2 s here would pass a bench the ruling fails (R7).
START_DRIFT_BAR_S = 0.5
# A269 ruling 10 A1: the session-level figure runs ~0.12-0.16 s above the
# chain-level one, and it is the figure R6's own precondition sentence names.
# A chain-level pass with a session-level figure over the bar is ESCALATED to
# the magistrate, never quietly passed.
SESSION_BAR_S = 0.5
BENCH_ROOT = Path.home() / "night-bench"
CUSTODY_ROOT_FORBIDDEN = Path.home() / "night-custody"
PLAN_ID_PREFIX = "bench-replay-"
RULED_ARTIFACT_SUFFIX = "-bench-replay-start-drift.md"
STUB = "scripts/bench_replay_systemsetup_stub.py"
LAUNCHD_LABEL_PREFIX = "com.joulewise.night"
SMOKE_PROTOCOL = {"envelope_s": 60, "slot_pitch_s": 80, "settle_s": 5, "envelopes": 3,
                  "interior_offset_s": 10, "interior_s": 40}


class BenchRefusal(Exception):
    """The bench refuses to start, or refuses to write what it was asked to."""


def run_text(argv, timeout=30):
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    return completed.returncode, completed.stdout


def git(*arguments):
    completed = subprocess.run(["/usr/bin/git", "-C", str(REPO_ROOT), *arguments],
                               capture_output=True, text=True, timeout=60)
    if completed.returncode != 0:
        raise BenchRefusal(f"git {' '.join(arguments)} failed: {completed.stderr.strip()}")
    return completed.stdout


def require_clean_head(expect_sha=None):
    """P7.1 pins the replay to a SHA, and a dirty tree is not that sha's bytes."""
    status = git("status", "--porcelain")
    if status.strip():
        raise BenchRefusal("working tree is not clean; the replay's sha would not name its bytes:\n" + status)
    head = git("rev-parse", "HEAD").strip()
    if expect_sha and not head.startswith(expect_sha):
        raise BenchRefusal(f"HEAD is {head}, not the expected {expect_sha}")
    return head


def require_no_night_agent():
    """Refuse while any night label is loaded (brief D6).

    A bench that runs beside a loaded ``com.joulewise.night*`` agent risks the
    agent firing into the same machine, and would in any case be measuring a
    tail the real night will not have.
    """

    code, text = run_text(["/bin/launchctl", "list"])
    if code != 0:
        raise BenchRefusal(f"launchctl list failed (exit {code}); cannot prove no night agent is loaded")
    loaded = sorted({field for line in text.splitlines() for field in line.split()
                     if field.startswith(LAUNCHD_LABEL_PREFIX)})
    if loaded:
        raise BenchRefusal("night agent labels are loaded; the bench never runs beside one: " + ", ".join(loaded))
    return loaded


def machine_state():
    """Load at the moment of asking, so a FAIL under load can be told apart.

    macOS `pgrep` has no `-c`, so the count is the line count of the match
    list; exit 1 means no match, which is a count of zero, and any other
    non-zero exit is an unanswered census and is recorded as null rather than
    as zero -- a failed census is not a claim of an empty machine.
    """

    _, uptime = run_text(["/usr/bin/uptime"])
    code, census = run_text(["/usr/bin/pgrep", "claude"])
    lines = [line for line in census.splitlines() if line.strip()]
    return {"epoch_s": time.time(), "uptime": uptime.strip(),
            "pgrep_claude": len(lines) if code == 0 else (0 if code == 1 else None),
            "platform": platform.platform()}


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_plan(plan_id, head, custody_root):
    now = time.time()
    return night_gate.NightPlan(
        plan_id=plan_id, receipt_class="DIAGNOSTIC_NO_PACK", t0_epoch_s=now,
        window_max_s=int(campaign.frozen_protocol()["window_max_s"]), authored_epoch_s=now,
        repo_head=head, measurement_root=str(REPO_ROOT), measurement_head=head,
        chain_path=str(custody_root / "chain.zsh"),
        chain_sha256_path=str(custody_root / "chain.zsh.sha256"),
        custody_root=str(custody_root),
        registration_path=str(REPO_ROOT / campaign.PROTOCOL_PATH))


def plan_mapping(plan):
    return {"schema": night_gate.PLAN_SCHEMA, "schema_version": night_gate.PLAN_SCHEMA_VERSION,
            **{k: v for k, v in asdict(plan).items() if k not in ("pack_night", "quiet_admission")}}


def stage_custody(plan, custody_root):
    """Render the sealed wrapper and manifest the covariate recorder verifies.

    ``execute`` launches ``joulewise.quiet_predicate_campaign record`` as a
    subprocess, and that entry point runs the full ``verify_environment``
    before it records anything: plan identity, manifest digests against
    ``measurement_head``'s tracked bytes, chain source digest.  The bench
    therefore stages a REAL wrapper through the production renderer -- the
    same ``gen_evidence_night.generate`` an arm would use -- rather than
    faking the four exports, so what the recorder verifies is what a night
    verifies.
    """

    custody_root.mkdir(parents=True, exist_ok=False)
    plan_path = custody_root / "night_plan.json"
    plan_path.write_text(json.dumps(plan_mapping(plan), sort_keys=True, indent=2) + "\n")
    chain = Path(gen_evidence_night.generate(plan_path))
    text = chain.read_text()
    exports = {name: night_gate.chain_literal(text, name) for name in
               ("EVIDENCE_PLAN_PATH", "EVIDENCE_MANIFEST_PATH",
                "EVIDENCE_MANIFEST_SHA256", "EVIDENCE_CHAIN_SOURCE_SHA256")}
    return plan_path, chain, exports


def bench_environment(plan, exports, night_dir, archive, label_shift):
    """Exactly what the collectors and the covariate recorder inherit.

    ``NIGHT_DIR`` is here for the same reason the four sealed exports are: the
    covariate recorder is a subprocess of ``execute`` running
    ``quiet_predicate_campaign record``, which reads its journal directory
    from that variable.  Without it the recorder refuses at its first line,
    ``execute`` sees a dead recorder at the end of slot 01 and ends the night
    -- which is exactly what the first smoke attempt did.
    """

    return {**exports, "NIGHT_PLAN_ID": plan.plan_id, "MEASUREMENT_ROOT": plan.measurement_root,
            "MEASUREMENT_HEAD": plan.measurement_head, "NIGHT_DIR": str(night_dir),
            "PYTHONPATH": str(REPO_ROOT), "PYTHONDONTWRITEBYTECODE": "1",
            harness.REPLAY_ENV: str(archive), harness.REPLAY_LABEL_SHIFT_ENV: label_shift}


def protocol_for(smoke):
    """The frozen registration, validated, then scaled ONLY for a smoke."""
    chain_digest = campaign.digest((REPO_ROOT / campaign.CHAIN_PATH).read_bytes())
    protocol = campaign.validate_protocol(campaign.frozen_protocol(), chain_digest)
    if not smoke:
        return dict(protocol)
    scaled = {**protocol, **SMOKE_PROTOCOL}
    # The cadence invariants are re-checked on the scaled copy: a smoke that
    # overlapped its captures would prove nothing about the real gap.
    campaign.cadence_fields(scaled)
    return scaled


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def slot_rows(night_dir, protocol):
    """One row per slot, from the chain journal and the collector's own record."""
    journal = night_dir / "evidence_envelopes.jsonl"
    rows = [json.loads(line) for line in journal.read_text().splitlines() if line] \
        if journal.exists() else []
    out = []
    for row in rows:
        directory = night_dir / "evidence" / f"envelope-{row['index']:02d}"
        session = read_json(directory / "session.json", {}) or {}
        power = session.get("power") or {}
        anchor = power.get("anchor") or {}
        replay = power.get("replay") or {}
        sidecar = read_json(replay.get("sidecar"), {}) or {}
        end_stamp = session.get("end_stamp") or {}
        deadline = session.get("deadline_mono_s")
        tail = (end_stamp.get("monotonic_after_s") - deadline
                if end_stamp.get("monotonic_after_s") is not None and deadline is not None else None)
        out.append({
            "index": row["index"], "scheduled_mono_s": row.get("scheduled_mono_s"),
            "actual_mono_s": row.get("actual_mono_s"),
            "chain_start_drift_s": row.get("start_drift_s"),
            "session_start_drift_s": session.get("start_drift_s"),
            "collector_exit": row.get("collector_exit"), "abort": row.get("abort"),
            "cleanup_proven": (row.get("cleanup") or {}).get("cleanup_proven"),
            "cleanup_wall_s": row.get("cleanup_wall_s"),
            "cleanup_budget_s": (row.get("cleanup") or {}).get("budget_s"),
            "attestation_state": row.get("network_time_attestation"),
            "network_time_attestation_wall_s": row.get("network_time_attestation_wall_s"),
            "anchor_status": anchor.get("status"),
            "anchor_detail": anchor.get("detail") or anchor.get("reason"),
            "recorder_kind": power.get("recorder_kind"),
            "recorder_argv_0": (power.get("argv") or [None])[0],
            "source_plist_sha256": replay.get("source_plist_sha256"),
            "written_stream_sha256": sidecar.get("written_stream_sha256"),
            "label_shift": sidecar.get("label_shift", replay.get("label_shift")),
            "label_shift_s": sidecar.get("label_shift_s", replay.get("label_shift_s")),
            "frames_written": sidecar.get("frames_written"),
            "interior_complete_support": (session.get("interior") or {}).get("complete_support"),
            "tail_s": tail, "session_error": session.get("error")})
    return out


# The slot fields a verdict is allowed to be taken over, and the value each
# must hold (execution lens 17b B2).  The bench exists to time the
# inter-slot TAIL -- collector exit, plist parse, anchor derivation, group
# teardown, interior reduction -- so a slot whose tail did not actually run
# is not a measurement of it, however small its drift figure looks.  In the
# lens's live smoke all three slots came back `anchor_status: "unknown"`
# (`clock_fit_span_insufficient`) with `interior_complete_support: False`:
# `align_frames` returned nothing, the expensive part of the tail never ran,
# and the bench returned PASS anyway.
ADMISSIBLE_SLOT = (("collector_exit", 0), ("cleanup_proven", True),
                   ("anchor_status", "bounded"), ("interior_complete_support", True))
# A 60 s smoke envelope is too short for the clock fit the anchor needs, so
# the anchor and the interior reduction that depends on it CANNOT resolve
# there.  Those two fields are therefore not admissible input under
# `--smoke`, and the smoke's own artifact says so.  Nothing else is exempt.
SMOKE_EXEMPT_FIELDS = ("anchor_status", "interior_complete_support")
# The attestation states a BENCH slot may hold (execution lens 17b S3).  The
# bench never turns network time off -- the `systemsetup` stub toggles
# nothing -- so `timed` goes on applying corrections for the whole run and a
# slot whose capture window contains one comes back `slew_attested`.  On a
# NIGHT that is an exclusion; here it is the expected state of a machine
# whose clock is still being disciplined, and it is not a bench failure.
# `asserted` is: it means the query failed, was blocked or timed out, so the
# `log show` whose wall cost this bench exists to measure did not run.
BENCH_ATTESTATION_STATES = ("authenticated", "slew_attested")


def verdict(rows, protocol, *, bar_s=START_DRIFT_BAR_S, session_bar_s=SESSION_BAR_S,
            smoke=False):
    """PASS only when EVERY slot is admissible and its chain drift is at or under the bar.

    Four failure shapes are distinguished, because they mean different
    things: a slot whose finalisation tail did not run (`ADMISSIBLE_SLOT`;
    its drift figure is not a measurement of the thing the bar is about); a
    slot over the bar (the tail still does not fit the gap); a slot that
    produced no chain-level figure at all (the journal is incomplete, so the
    bar is not evidenced); and a chain-level pass whose session-level figure
    is over the bar, which A269 ruling 10 A1 makes an ESCALATION rather than
    a pass or a fail.
    """

    chain = [r["chain_start_drift_s"] for r in rows if r["chain_start_drift_s"] is not None]
    session = [r["session_start_drift_s"] for r in rows if r["session_start_drift_s"] is not None]
    missing = [r["index"] for r in rows if r["chain_start_drift_s"] is None]
    expected = protocol["envelopes"]
    over = sorted(r["index"] for r in rows
                  if r["chain_start_drift_s"] is not None and r["chain_start_drift_s"] > bar_s)
    session_over = sorted(r["index"] for r in rows
                          if r["session_start_drift_s"] is not None and r["session_start_drift_s"] > session_bar_s)
    required = [(field, value) for field, value in ADMISSIBLE_SLOT
                if not (smoke and field in SMOKE_EXEMPT_FIELDS)]
    defects = []
    for r in rows:
        for field, value in required:
            if r.get(field) != value:
                defects.append({"index": r["index"], "field": field,
                                "value": r.get(field), "required": value})
        if r.get("attestation_state") not in BENCH_ATTESTATION_STATES:
            defects.append({"index": r["index"], "field": "attestation_state",
                            "value": r.get("attestation_state"),
                            "required": " or ".join(BENCH_ATTESTATION_STATES)})
    complete = len(rows) == expected and not missing
    if defects or not complete or over:
        status = "FAIL"
    elif session_over:
        # A THIRD status, neither PASS nor FAIL (execution lens 17b B1).  The
        # split was recorded as a separate boolean beside `status: "PASS"`,
        # the headline printed PASS and the process exited 0 -- and the
        # lens's own live smoke produced exactly that: chain max 0.479 s
        # under the bar, session max 0.734 s over it, exit 0.  The full run
        # is launched detached and unattended, so a reader of the exit code
        # and the headline would have proceeded to arm on a split.
        status = "ESCALATE"
    else:
        status = "PASS"
    escalate = status == "ESCALATE"
    # The SPLIT -- a chain figure at or under its bar beside a session figure
    # over its own -- reported independently of `status` (delta execution lens
    # SHOULD-FIX 2).  `escalate_chain_pass_session_fail` is by construction
    # `status == "ESCALATE"`, so a run that is over the session bar AND has an
    # inadmissible slot came back FAIL with that flag FALSE and a statement
    # that never mentioned the session figure: a reader of `slot_defects` plus
    # that boolean concluded the session-level figure had been fine.
    # `session_bar_exceeded` is true whenever `session_slots_over_bar` is
    # non-empty, whatever the status, and the statement says so too.
    session_bar_exceeded = bool(session_over)
    if status == "PASS" and chain:
        statement = (f"max(chain start_drift_s) = {max(chain):.3f} s <= {bar_s} s over "
                     f"{len(rows)}/{expected} slots")
    elif status == "ESCALATE":
        statement = (f"the chain-level bar is met ({max(chain):.3f} s <= {bar_s} s) but the "
                     f"session-level figure is not (max {max(session):.3f} s > {session_bar_s} s "
                     f"on slots {session_over}): a split verdict is ESCALATED to the "
                     "magistrate, never passed")
    else:
        statement = (f"max <= {bar_s} s NOT shown: over={over} missing={missing} "
                     f"recorded={len(rows)}/{expected}"
                     + "".join(f"; slot {d['index']} {d['field']}={d['value']!r} "
                               f"(required {d['required']!r})" for d in defects)
                     + (f"; the session-level bar is exceeded too (max "
                        f"{max(session):.3f} s > {session_bar_s} s on slots {session_over})"
                        if session_bar_exceeded else ""))
    return {"bar_s": bar_s, "session_bar_s": session_bar_s, "slots_expected": expected,
            "slots_recorded": len(rows), "slots_missing_chain_drift": missing,
            "max_chain_start_drift_s": max(chain) if chain else None,
            "max_session_start_drift_s": max(session) if session else None,
            "slots_over_bar": over, "session_slots_over_bar": session_over,
            "slot_defects": defects, "smoke_exempt_fields": list(SMOKE_EXEMPT_FIELDS) if smoke else [],
            "status": status, "escalate_chain_pass_session_fail": escalate,
            "session_bar_exceeded": session_bar_exceeded, "statement": statement}


def markdown(report):
    rows = report["slots"]
    v = report["verdict"]
    lines = [f"# Bench replay — chain-level `start_drift_s` ({report['kind']})", "",
             f"Schema `{report['schema']}`. Merged sha `{report['head']}`"
             f" (clean tree: {report['clean_tree']}).",
             f"Protocol: envelope {report['protocol']['envelope_s']} s, pitch "
             f"{report['protocol']['slot_pitch_s']} s, settle {report['protocol']['settle_s']} s, "
             f"{report['protocol']['envelopes']} slots; gap "
             f"{report['protocol']['slot_pitch_s'] - report['protocol']['envelope_s']} s; "
             f"cleanup budget {report['cleanup_budget_s']} s; attestation timeout "
             f"{report['attestation_timeout_s']} s.",
             f"Registration sha256 `{report['registration_sha256']}`; bench script sha256 "
             f"`{report['bench_script_sha256']}`.", ""]
    if report.get("transaction_merge"):
        lines += [f"Transaction merge `{report['transaction_merge']}` is an ancestor: "
                  f"{report['transaction_merge_is_ancestor']}.", ""]
    lines += ["## Verdict", "",
              f"**{v['status']}** — {v['statement']}.",
              *(["", "`ESCALATE` is neither a pass nor a fail: the chain-level bar is met and "
                 "the session-level figure is not, which A269 ruling 10 A1 sends to the "
                 "magistrate. The process exits 3.", ""]
                if v['status'] == "ESCALATE" else []),
              f"max(session `start_drift_s`) = {v['max_session_start_drift_s']} s "
              f"(bar {v['session_bar_s']} s; over: {v['session_slots_over_bar'] or 'none'}).",
              f"Session bar exceeded (true whatever the status): "
              f"{v.get('session_bar_exceeded', bool(v['session_slots_over_bar']))}.",
              f"Chain-pass/session-fail split requiring escalation (this is "
              f"`status == ESCALATE`; a FAIL over the session bar reads False here "
              f"and True on the line above): {v['escalate_chain_pass_session_fail']}.",
              f"Inadmissible slots (the finalisation tail did not run): "
              f"{v.get('slot_defects') or 'none'}.",
              *(["A 60 s smoke envelope is too short for the clock fit the anchor needs, so "
                 "`anchor_status` CANNOT resolve at this envelope length and the interior "
                 "reduction that depends on it cannot run either. Those two fields are "
                 "exempt from admission HERE and only here; the full run at 600 s admits no "
                 "such slot."] if report["kind"] == "smoke" else []), "",
              "## Per slot", "",
              "| slot | scheduled_mono_s | actual_mono_s | chain drift s | session drift s | "
              "collector exit | cleanup proven | cleanup wall s | attestation | attest wall s | "
              "anchor | tail s |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        def show(value, digits=3):
            return f"{value:.{digits}f}" if isinstance(value, (int, float)) else str(value)
        lines.append(f"| {r['index']} | {show(r['scheduled_mono_s'])} | {show(r['actual_mono_s'])} | "
                     f"{show(r['chain_start_drift_s'])} | {show(r['session_start_drift_s'])} | "
                     f"{r['collector_exit']} | {r['cleanup_proven']} | {show(r['cleanup_wall_s'])} | "
                     f"{r['attestation_state']} | {show(r['network_time_attestation_wall_s'])} | "
                     f"{r['anchor_status']} | {show(r['tail_s'])} |")
    lines += ["", "## Replay provenance (never evidence)", "",
              "| slot | recorder_kind | label shift | K s | frames | source plist sha256 | written stream sha256 |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['index']} | {r['recorder_kind']} | {r['label_shift']} | {r['label_shift_s']} | "
                     f"{r['frames_written']} | `{r['source_plist_sha256']}` | `{r['written_stream_sha256']}` |")
    lines += ["",
              "The bench NEVER turns network time off: the `systemsetup` stub toggles nothing, "
              "it only prints the exact stdout the chain's comparator demands. `timed` "
              "therefore goes on applying clock corrections for the whole run, and a slot "
              "whose capture window contains one comes back `slew_attested`. On a night that "
              "is an exclusion; here it is the EXPECTED state of a machine whose clock is "
              "still being disciplined, and it is not a bench failure — the verdict treats "
              "`slew_attested` and `authenticated` alike. Only `asserted` (the query failed, "
              "was blocked, or timed out) is a named slot defect, because then the `log show` "
              "whose wall cost this bench exists to measure did not run. The attestation "
              "walls in the table above are the cost of a LIVE `log show` over a log that is "
              "still receiving `timed` entries.", "",
              "Under `--label-shift auto` the plist the feeder writes carries LIVE-LOOKING "
              "dates: every `<date>` label is the archived one moved forward by one constant "
              "whole number of seconds K, so the file cannot be told from a fresh capture by "
              "reading it. Nothing in the plist marks it. The provenance is entirely "
              "OUT-OF-BAND, in three places that all survive the run: the feeder's sidecar "
              "(`source_sha256`, `written_stream_sha256`, `label_shift_s` = K), the envelope's "
              "`session.json` (`power.recorder_kind: \"replay\"`, `power.replay.*`, including "
              "K read back from the sidecar), and the custody root itself (`~/night-bench/`, "
              "plan id `bench-replay-…`). Under `--label-shift none` the labels are the "
              "archived ones and K is 0.", "",
              f"Archive (read-only, never copied): `{report['archive']}`.",
              f"Outcome: `{report['outcome']}` (rc {report['returncode']}); summary status "
              f"`{report['summary_status']}`; `evidence_outcome.json` recorder_kind "
              f"`{report['outcome_recorder_kind']}`; plan id `{report['plan_id']}`; custody root "
              f"`{report['custody_root']}`.",
              "", "A refused outcome with `REPLAY_NEVER_EVIDENCE` is the CORRECT result: the "
              "harvest-side interlock is what proves these frames can never be labelled evidence. "
              "Every slot's row survives the refusal in `evidence_envelopes.jsonl`, which is where "
              "the drift figures above come from.", "",
              "## Machine state", "",
              f"- at start: uptime `{report['machine_start']['uptime']}`, "
              f"`pgrep claude` = {report['machine_start']['pgrep_claude']}",
              f"- at end: uptime `{report['machine_end']['uptime']}`, "
              f"`pgrep claude` = {report['machine_end']['pgrep_claude']}", "",
              "Extra daytime load LENGTHENS the inter-slot tail, so a pass taken under load is a "
              "fortiori evidence for a quiet night; a FAIL under load is inconclusive and is "
              "retried on a census-clean machine.", ""]
    return "\n".join(lines)


def execute_bench(args):
    head = require_clean_head(args.expect_sha)
    require_no_night_agent()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    plan_id = f"{PLAN_ID_PREFIX}{stamp}"
    custody_root = BENCH_ROOT / plan_id
    if CUSTODY_ROOT_FORBIDDEN == custody_root or str(custody_root).startswith(str(CUSTODY_ROOT_FORBIDDEN)):
        raise BenchRefusal("the bench never writes under the night custody root")
    archive = Path(args.archive).expanduser().resolve()
    if not archive.is_dir():
        raise BenchRefusal(f"archive root {archive} is not a directory")
    protocol = protocol_for(args.smoke)
    plan = build_plan(plan_id, head, custody_root)
    plan_path, chain, exports = stage_custody(plan, custody_root)
    night_dir = custody_root / "night"
    machine_start = machine_state()
    environment = bench_environment(plan, exports, night_dir, archive, args.label_shift)
    stub = str(REPO_ROOT / STUB)
    started = time.time()
    previous = {key: os.environ.get(key) for key in environment}
    os.environ.update(environment)
    sudo, systemsetup = campaign.SUDO, campaign.SYSTEMSETUP
    # Brief D2: the module's own documented rebinding seam.  BOTH constants
    # move, because ``network_time_argv`` prefixes ``sudo -n`` and the hard
    # limit on this lane is that no sudo runs at all; with both bound to the
    # stub, the receipt's own argv contains neither `/usr/bin/sudo` nor
    # `/usr/sbin/systemsetup`, which makes the control record self-identifying
    # as a bench record.
    campaign.SUDO, campaign.SYSTEMSETUP = stub, stub
    try:
        returncode = campaign.execute(plan, protocol, night_dir)
    finally:
        campaign.SUDO, campaign.SYSTEMSETUP = sudo, systemsetup
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    machine_end = machine_state()
    rows = slot_rows(night_dir, protocol)
    outcome = read_json(night_dir / "evidence_outcome.json", {}) or {}
    summary = read_json(night_dir / "evidence" / "summary.json", {}) or {}
    control = read_json(night_dir / campaign.NETWORK_TIME_CONTROL_BASENAME, {}) or {}
    report = {
        "schema": SCHEMA, "kind": "smoke" if args.smoke else "full",
        "head": head, "clean_tree": True, "expect_sha": args.expect_sha,
        "transaction_merge": args.transaction_merge,
        "transaction_merge_is_ancestor": (
            subprocess.run(["/usr/bin/git", "-C", str(REPO_ROOT), "merge-base",
                            "--is-ancestor", args.transaction_merge, head]).returncode == 0
            if args.transaction_merge else None),
        "bench_script": str(Path(__file__).resolve()),
        "bench_script_sha256": sha256_file(__file__),
        "bench_argv": sys.argv,
        "feeder_sha256": sha256_file(REPO_ROOT / harness.REPLAY_FEEDER),
        "stub_sha256": sha256_file(stub),
        "registration_sha256": night_gate.QPE01_PILOT_REGISTRATION_SHA256,
        "chain_source_sha256": exports["EVIDENCE_CHAIN_SOURCE_SHA256"],
        "manifest_sha256": exports["EVIDENCE_MANIFEST_SHA256"],
        "protocol": {k: protocol[k] for k in
                     ("envelope_s", "slot_pitch_s", "settle_s", "envelopes", "interior_offset_s",
                      "interior_s", "sample_interval_s", "power_interval_ms",
                      "start_drift_abort_s", "start_drift_max_s", "window_max_s")},
        "cleanup_budget_s": campaign.cleanup_budget_s(protocol),
        "attestation_timeout_s": campaign.attestation_timeout_s(protocol),
        "archive": str(archive), "label_shift": args.label_shift,
        "plan_id": plan_id, "custody_root": str(custody_root), "night_dir": str(night_dir),
        "plan_path": str(plan_path), "chain_path": str(chain),
        "returncode": returncode, "outcome": outcome.get("outcome"),
        "outcome_error": outcome.get("error"),
        "outcome_recorder_kind": outcome.get("recorder_kind"),
        "network_time_restored": outcome.get("network_time_restored"),
        "network_time_control_argv": ((control.get("off") or {}).get("argv")),
        "summary_status": summary.get("status"),
        "summary_evidence_status": summary.get("evidence_status"),
        "summary_retained": summary.get("retained"), "summary_s_upper": summary.get("s_upper"),
        "wall_s": time.time() - started,
        "machine_start": machine_start, "machine_end": machine_end,
        "slots": rows}
    report["verdict"] = verdict(rows, protocol, smoke=args.smoke)
    return report


def write_outputs(report, args):
    raw = Path(args.raw) if args.raw else Path(report["night_dir"]).parent / "bench-replay.json"
    artifact = Path(args.artifact) if args.artifact else \
        Path(report["night_dir"]).parent / "bench-replay-smoke.md"
    if report["kind"] == "smoke" and artifact.name.endswith(RULED_ARTIFACT_SUFFIX):
        # D7: a scaled run changes the gap, and the gap is what produces the
        # bar.  A smoke may never be filed under the ruled artifact's name.
        raise BenchRefusal(f"a smoke never writes the ruled artifact name {artifact.name!r}")
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n")
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(markdown(report))
    return raw, artifact


def parser():
    ap = argparse.ArgumentParser(description="The ruled daytime bench replay; never evidence.")
    ap.add_argument("--archive", required=True, help="archived harvest root, read-only, never copied")
    ap.add_argument("--smoke", action="store_true", help="scaled plumbing proof, ~5 min; never the artifact")
    ap.add_argument("--label-shift", choices=("none", "auto"), default="none")
    ap.add_argument("--expect-sha", default=None, help="refuse unless HEAD is this sha")
    ap.add_argument("--transaction-merge", default=None,
                    help="the D-138 transaction merge sha, recorded with an ancestry check")
    ap.add_argument("--artifact", default=None, help="markdown output path")
    ap.add_argument("--raw", default=None, help="bench-replay.json output path")
    return ap


def main(argv=None):
    args = parser().parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = execute_bench(args)
        raw, artifact = write_outputs(report, args)
    except (BenchRefusal, GenerationRefusal, OSError, ValueError, KeyError,
            subprocess.SubprocessError) as exc:
        print(f"BENCH_REPLAY_REFUSED {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report["verdict"], sort_keys=True, indent=2))
    print(f"raw={raw}")
    print(f"artifact={artifact}")
    # Three statuses, three codes: 0 a pass, 1 a fail, 3 a split that only the
    # magistrate can resolve.  2 is already taken by `BENCH_REPLAY_REFUSED`.
    return {"PASS": 0, "ESCALATE": 3}.get(report["verdict"]["status"], 1)


if __name__ == "__main__":
    raise SystemExit(main())
