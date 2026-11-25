#!/usr/bin/env python3
"""The interim look's two-stage CLI (RL-166 Q1, Q2, Q8; the analyst seat runs it).

    host-id
    post-no-maxima
    stage1 [--allow-draft] [--ruled-exclusion LEG_KEY=RULE=RL-n ...] [--stage-archives] [--level-r]
    stage2 --stage1-sha256 HEX [--allow-draft] [--level-e]

No command takes a path (audit 2, lead ruling), and a committed run reads every public record (the ledger, the
RUN_STATE the pins chain to) from origin/main after a fetch, never from a ref or a file a caller names (audit 3,
rule P3). The manifest is the repository's
docs/process/cadence/looks/lm-interim-01.json; it registers the look's root (``custody.root``) and carries the pin
list. Every other path is that root and the look id (``manifest.LookLayout``):

    <root>/<span id>/                          each roster span's custody copy
    <root>/lm-interim-01/roster.json            the roster (validate --span-ledger --roster-out)
    <root>/lm-interim-01/rules_3_4.json         inclusion_34.py's verdict file
    <root>/lm-interim-01/stage1.json            stage 1's output, created once; stage 2's input
    <root>/lm-interim-01/level_r.json           stage 1's level-R input, created once beside it
    <root>/lm-interim-01/superseded_stage1.json, superseded_level_r.json    a ruled rerun's kept files
    <root>/lm-interim-01/archives/<span id>.tar, .SHA256SUMS, .marker.json   pulled archives (--stage-archives)
    <root>/lm-interim-01/RESTRICTED/            stage 2's reservation; the public report goes to the ledger's
                                                registered public root, by the reservation step only

Each path is checked before use: its own realpath, no symlink component, inside its root, and no name beside it
that differs only in case. An archive is expanded into a fresh private directory outside every registered root and
the repository. ``--level-r`` and ``--level-e`` (synthetic ``--allow-draft`` runs only) read
input_level_r.json and input_level_e.json from the look's directory.

Stage 1 reads time fields and sample counters only from energy-bearing files. In custody mode it opens, per span: `runner_receipt.json`,
`soak/soak_reference.json`, and per leg `leg_record.json`; per accepted attempt's bundle: `events.jsonl`
(token index and stamp), `outputs/align_turns.jsonl` (stamps, prompt count, the LENGTH of the output ids),
`outputs/align_thermal.jsonl` (journal readings), `config.json` (sampling period), and the optional G0 event
fallbacks `outputs/align_runtime_events.jsonl` and `align_runtime_events.jsonl` when replaying rules 3 and 4.
For the native power-management state only it reads
`rich_telemetry.jsonl` and `raw/powermetrics.plist`, from which it extracts by pattern the row end stamp,
`elapsed_ns` and `thermal_pressure` and nothing else: no line or frame of those two files is parsed as a whole,
so no power or energy value is decoded. Of the energy files it reads TIME FIELDS only, through
`joulewise/cadence_looks/time_fields.py` (RL-173 E.1): each development leg's `power_trace.csv` gpu_power row stamps,
and each span's meter streams' header and trailer keys, poll stamps and counts and each sample's 16-bit device
counter. From them come the two trace clauses (rules 3 and 4 at the look), R-20's clock print and the custody digests
stage 2 checks before energy. No power, voltage, current or SMC value is converted.

Stage 2 takes the stage-1 file by its sha256 as its only roster. In custody mode it computes the level-E object
in memory (GPU rail through the committed step 3 module's `load_gpu_trace` and `Trace`; DC-in by the trapezoid
between consecutive KM003C samples, through `joulewise.external.km003c_parse`) and never writes it.

The stage-2 destinations and execution host are registered in LOOKS.json. After reservation, only the
closed public report or the fixed two-line failure notice leaves custody.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import importlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import sys
import tempfile
import threading
import uuid
import time

sys.dont_write_bytecode = True
# An unused cache prefix forces source compilation, and -B prevents writes there.
ROOT = Path(__file__).resolve().parents[1]
sys.pycache_prefix = str(ROOT / f".jw-look-pyc-{uuid.uuid4().hex}")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.cadence_looks import fit_interim as F  # noqa: E402
from joulewise.cadence_looks import interim_release as release  # noqa: E402
from joulewise.cadence_looks import manifest as M  # noqa: E402
from joulewise.cadence_looks import inclusion_34 as I34  # noqa: E402
from joulewise.cadence_looks import time_fields as TF  # noqa: E402
from joulewise.cadence_looks import admission as ADM  # noqa: E402
from joulewise.cadence_looks import custody_pins as PINS  # noqa: E402
# the reader runs the pinned decoder's unwrap and clock fit on counters (RL-173 E.1): loaded up front, so every stage-1
# run records one code set (manifest.STAGE1_CODE) whatever its input
from joulewise.external import km003c_parse as _kp  # noqa: E402,F401

STEP3_SHA256 = "84a1a5530ab06e688b000c84f248b2c4e561e8330f37d3132ec47aa2572eb173"
FAN_KEYS = ("F0Ac", "F1Ac")          # configs/align/v4/r1_runtime.json sensors.fan_keys
PM_FRESH_S = 2.0
NS = 1_000_000_000
METER_MAX_GAP_S = 2.0                # RL-166 Q7: no gap over 2 s between meter sample stamps in the leg's interval
MODE_BY_POWER = {"automatic": 0, "high_power": 2}
JOURNAL_PRE_S, JOURNAL_POST_S = 60.0, 5.0
CODE_PATHS = ("joulewise/cadence_looks/fit_interim.py", "scripts/cadence_look_run.py")
RUNNING = tuple(ROOT / p for p in CODE_PATHS)          # the files verify_pins requires to be pinned


# =============================================================================================== helpers
def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def code_hashes():
    """Every repository source file this process has loaded, with its sha256 (M.loaded_repo_files; Sol N2 /
    Mythos 3). Taken when the stage's output is built, after everything it ran has been imported."""
    return M.loaded_repo_files(ROOT)


_VERIFIED = []
ADMITTED = []          # RL-194: the custody each stage of this process admitted by its pins; its reads are listed there


def _stamp(out, a):
    """Provenance and run mode on a level-R stage-1 output (no custody, no protected source): the manifest
    verify_pins checked, and allow_draft. Before writing, refuse if any repository module loaded in this process is
    not pinned (manifest.unpinned_loaded_modules)."""
    doc, _ = _VERIFIED[0]
    _guard_loaded(doc)
    gate = None if a.allow_draft else M.ledger_gate(ROOT, getattr(a, "ledger_ref", None))
    return _provenance(out, a, gate)


def _stamp_protected(out, a):
    """``_stamp`` for a custody stage 1, in its protected phase: the loaded-code check and the ledger gate ran in the
    preflight (``a.ledger_gate_record``); a change of the loaded code since then is a breach, never a refusal."""
    doc, _ = _VERIFIED[0]
    if M.unpinned_loaded_modules(doc, ROOT) or _cached_source() is not None:
        raise PreflightBreach("the loaded repository code changed after the preflight's check")
    return _provenance(out, a, a.ledger_gate_record)


def _provenance(out, a, gate):
    _, mpath = _VERIFIED[0]
    out["manifest_sha256"] = sha256_file(mpath)
    out["allow_draft"] = bool(a.allow_draft)
    # what satisfied the committed-ledger gate (Sol NEW-2 / Mythos N3); none under --allow-draft
    out["ledger_gate"] = gate
    return out


def _jsonl(path):
    with open(path) as f:
        return [M.strict_json(x) for x in f if x.strip()]


def _json(path):
    with open(path) as f:
        return M.strict_json(f.read())


class WriterShape(F.LookInputError):
    """A value no pinned writer serializes (RL-184 section 3.3). The look refuses on it whatever the leg's verdicts:
    it is never read as a leg without a turn."""


# Stage 1 runs in two phases (lead's engineering ruling, PR #795 round 8, C1). ``stage1_preflight`` decides every
# refusal that needs no protected file, for the whole roster, and returns before the first protected source (a trace,
# telemetry, powermetrics or meter stream) opens. ``stage1_protected`` then reads the protected time fields. After
# the first protected open the only refusals are ``ContentRefusal``s whose code is in POST_OPEN_REASONS: each is a
# condition on protected content. Anything else that stops the protected phase is a ``PreflightBreach``: a fault in
# the preflight, reported as FAILED and never as a refusal (``main``).
POST_OPEN_REASONS = {
    "native_states": "an included leg's native power-management states (rich_telemetry.jsonl and "
                     "raw/powermetrics.plist) cannot be read, paired or placed in its turn",
    "no_leg_enters_fit": "the rules-3/4 replay, the trace clauses or the native states leave none of the "
                         "preflight's fit candidates in the fit",
    "zero_rate_seconds": "the legs the protected reads leave in the fit, or in one cell, have zero prefill or decode "
                         "seconds",
    "ruled_rerun_changed": "a ruled rerun's read of the protected sources differs from the superseded read beyond "
                           "the named exclusions",
    "no_fit_candidate": "Known limitation (lead ruling N1(a), PR #795, 2026-11-24): a roster with no fit candidate "
                        "opens protected files before refusing; no value is printed. The preflight knows the fit "
                        "candidates, but this CLI is both the production entry and the frozen admission matrix's "
                        "driver, whose negative-arena control (101,605 cases) must reach a protected open with every "
                        "verdict false",
}
KNOWN_LIMITATION_REASONS = frozenset({"no_fit_candidate"})
_PHASE = {"protected": False}


class ContentRefusal(F.LookInputError):
    """A refusal after the first protected open: its condition is on protected content (POST_OPEN_REASONS)."""

    def __init__(self, code, message):
        if code not in POST_OPEN_REASONS:
            raise ValueError(f"not a post-open reason: {code}")
        super().__init__(message)
        self.code = code


class PreflightBreach(F.LookInputError):
    """A check the preflight owns, failing in the protected phase: the preflight missed it. Never a refusal."""


def _finite(value):
    """Whether a decoded JSON value is a finite number: an int or a float, never a boolean or text."""
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(float(value))
    except OverflowError:
        return False


def _real(value, what):
    """A JSON number as the pinned writers serialize one. Text, a boolean or a container is refused, never
    converted: ``float`` and ``int`` accept digits outside ASCII, signs, spaces and underscores in a string."""
    if not _finite(value):
        raise WriterShape(f"{what}: not a finite number as the pinned writers serialize it")
    return float(value)


def _whole(value, what):
    """A JSON integer as the pinned writers serialize one (a count or an index), at least zero."""
    if type(value) is not int or value < 0:
        raise WriterShape(f"{what}: not a count as the pinned writers serialize it")
    return value


def write_canonical(path, obj):
    data = F.dump(obj)
    with open(path, "wb") as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()


def manifest_path():
    """The look manifest, at its one fixed place in this repository."""
    return ROOT / M.INTERIM_MANIFEST_PATH


def ledger_path():
    """LOOKS.json in this checkout: a synthetic --allow-draft stage 2's stand-in for the committed ledger."""
    return ROOT / M.LOOK_LEDGER_PATH


def run_state_text(allow_draft):
    """The RUN_STATE the pins chain to: RUN_STATE.md on origin/main (already fetched by ``main``); a synthetic
    --allow-draft run, which may never touch a real look's custody, reads this checkout's own RUN_STATE.md."""
    if allow_draft:
        return (ROOT / "RUN_STATE.md").read_text(encoding="utf-8")
    return M.public_run_state(ROOT, fetch=False)


def layout_of(doc):
    try:
        return M.LookLayout(ROOT, doc)
    except M.ManifestError as error:
        raise F.LookInputError("layout: " + "; ".join(error.problems)) from None


@contextlib.contextmanager
def _verifier_sigterm():
    """Unwind the verifier's temporary directory on CLI SIGTERM. SIGKILL cannot run cleanup."""
    if threading.current_thread() is not threading.main_thread():
        yield
        return

    def terminate(signum, _frame):
        raise SystemExit(128 + signum)

    previous = signal.signal(signal.SIGTERM, terminate)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


def run_verifier(doc, pins, pins_sha, span_ids, sdir_of):
    """RL-194a section 1: the hash-only verifier, as its own process, before this stage parses anything. It reads
    every pinned file as opaque bytes; this process reads back only its result file (``pass`` or ``fail``, and for
    each path the pinned and observed digests) and refuses unless that covers exactly the pinned files and every
    one matches. A stage never hashes an energy stream itself (RL-179 F-12)."""
    import subprocess
    verifier = ROOT / M.VERIFIER_PATH
    pinned = {path: sha for _, path, sha in M.code_refs(doc)}
    if verifier.resolve() != verifier or not verifier.is_file() or sha256_file(verifier) != pinned.get(M.VERIFIER_PATH):
        raise F.LookInputError("custody pins: the verifier is not at its manifest pin")
    result = None
    # The result is read back from a directory this process made and removes. No caller names where it goes: a
    # refused run leaves no file anywhere (audit 1 on 2082c1a51: a result written at the public destination made
    # the next registered execution refuse, with no reservation taken).
    with _verifier_sigterm(), tempfile.TemporaryDirectory(prefix="jw-look-verify-", ignore_cleanup_errors=True) as tmp:
        out = Path(tmp) / "verification.json"
        pins_path = Path(tmp) / "pins.json"         # the manifest's own list, as the bytes its sha256 names
        pins_path.write_bytes(PINS.pin_list_bytes(pins))
        argv = [sys.executable, "-I", "-B", str(verifier), "--pins", str(pins_path), "--pins-sha256", pins_sha,
                "--out", str(out)]
        for sid in span_ids:
            argv += ["--span", f"{sid}={Path(sdir_of(sid)).absolute()}"]
        try:
            done = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL, check=False)
            if done.returncode in (0, 1):
                result = json.loads(out.read_bytes())
        except (OSError, ValueError):
            result = None
    if result is None:
        raise F.LookInputError("custody pins: the verifier process did not produce its result")
    problems = PINS.verification_problems(pins, result)
    if problems or done.returncode != 0:
        raise F.LookInputError("custody pins: " + (problems[0] if problems else "the verifier did not pass"))


def load_pins(a, span_ids):
    """RL-194 condition 2, before anything of custody is touched (a span directory, an archive): the pin list is the
    manifest's own and no other (audit 2, lead ruling: one source of pins), it names exactly the roster's spans, and
    each span's RUN_STATE Check item names its offload manifest (``run_state_text``). Returns (the pin list, the
    sha256 of its canonical bytes)."""
    doc, _ = _VERIFIED[0]
    try:
        pins, pins_sha = M.input_pins(ROOT, doc, complete=True)
        PINS.require_roster(pins, span_ids)
        try:
            text = run_state_text(a.allow_draft)
        except OSError:
            raise F.LookInputError("custody pins: no RUN_STATE to chain the pins to") from None
        unchained = PINS.check_chain_problems(pins, text)
        if unchained:
            raise F.LookInputError("custody pins: " + "; ".join(unchained[:4]))
    except PINS.PinRefusal as exc:
        raise F.LookInputError(f"custody pins: {exc}") from None
    return pins, pins_sha


def admit_custody(a, span_ids, sdir_of, stack, *, streams, loaded=None):
    """RL-194 conditions 1 to 3 as RL-194a amends them, the first act of stage 1 and of stage 2 on custody, before
    any roster file is parsed and before the reservation:

    1. the pin list is admitted (``load_pins``; ``loaded`` when the stage has already done so);
    2. the separate hash-only verifier process checks every pinned file (``run_verifier``);
    3. this process then reads each operational file once, checks its pin and keeps those bytes, and checks each
       span directory by name (``PinnedCustody.verify``). It opens no stream for that.

    For the rest of the stage every read of a roster path goes through the pins (``stack`` holds the guard open):
    an operational file is served from its verified bytes, and a stream is read from disk (``streams="pass"``,
    stage 1) or re-checked against its pin at each open, immediately before it is decoded (``"verify"``, stage 2).
    Returns (the admitted custody, the pin list's sha256)."""
    doc, _ = _VERIFIED[0]
    pins, pins_sha = loaded if loaded is not None else load_pins(a, span_ids)
    try:
        custody = PINS.PinnedCustody(pins, span_ids, sdir_of, streams=streams)
        run_verifier(doc, pins, pins_sha, span_ids, sdir_of)
        custody.verify()
    except PINS.PinRefusal as exc:
        raise F.LookInputError(f"custody pins: {exc}") from None
    stack.enter_context(custody.guard())
    ADMITTED.append(custody)
    return custody, pins_sha


_STAGING_REASON = re.compile(r"[A-Za-z0-9 ;,()'-]{1,120}")


def stage_archive(span_id, archive, manifest, marker, staging_root, *, manifest_sha256, doc=None):
    """RL-174 D.3: expand a pulled, decrypted #804 archive into a new span directory, by the pinned hash-only
    staging process (``scripts/cadence_look_stage_archive.py``). The archive holds the span's traces, telemetry and
    meter streams, so this process never opens it, hashes it or writes a member (RL-179 F-12; RL-194a section 1).

    ``manifest_sha256`` is the span's pinned offload manifest digest. The staging process refuses unless the
    supplied SHA256SUMS has exactly that digest, before it reads anything else: staging follows the pins, it does
    not come before them. It then checks the marker and the archive, hashes each member as it is written and
    publishes the span directory only after every file matches. Stage 1's ordinary first act (the verifier, then
    the operational files) reads the copy back afterwards. Returns the staging record: three digests and a count."""
    import subprocess

    def refuse(reason):
        raise F.LookInputError(f"staging: {span_id}: {reason}")

    if not isinstance(span_id, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", span_id):
        refuse("invalid span id")
    if not isinstance(manifest_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", manifest_sha256):
        refuse("no pinned offload manifest digest")
    stager = ROOT / M.STAGER_PATH
    if doc is not None:
        pinned = {path: sha for _, path, sha in M.code_refs(doc)}
        if stager.resolve() != stager or not stager.is_file() or sha256_file(stager) != pinned.get(M.STAGER_PATH):
            refuse("the staging process is not at its manifest pin")
    result = None
    with tempfile.TemporaryDirectory(prefix="jw-look-stage-") as tmp:
        out = Path(tmp) / "staging.json"
        argv = [sys.executable, "-I", "-B", str(stager), "--span-id", span_id, "--archive", str(archive),
                "--manifest", str(manifest), "--marker", str(marker), "--manifest-sha256", manifest_sha256,
                "--staging-root", str(staging_root), "--out", str(out)]
        try:
            done = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL, check=False)
            if done.returncode in (0, 1):
                result = json.loads(out.read_bytes())
        except (OSError, ValueError):
            result = None
    if (not isinstance(result, dict) or set(result) != {"schema", "result", "reason", "record"}
            or result["schema"] != "joulewise.cadence_look_staging.v1"):
        refuse("the staging process did not produce its result")
    if result["result"] != "staged" or done.returncode != 0:
        reason = result["reason"]
        refuse(reason if isinstance(reason, str) and _STAGING_REASON.fullmatch(reason) else "refused")
    record = result["record"]
    digests = ("archive_sha256", "manifest_sha256", "marker_sha256")
    if (not isinstance(record, dict) or set(record) != {"span_id", "files_verified", *digests}
            or record["span_id"] != span_id or record["manifest_sha256"] != manifest_sha256
            or type(record["files_verified"]) is not int
            or not all(isinstance(record[key], str) and re.fullmatch(r"[0-9a-f]{64}", record[key]) for key in digests)):
        refuse("the staging process did not produce its result")
    return record


def stage_custody(a, roster, pins, layout, stack):
    """--stage-archives: each roster span that has a pulled archive under the look's ``archives`` directory is
    expanded, against the offload manifest digest its pins carry, by the staging process into a fresh private
    directory outside every registered root and the repository; it is removed when the stage ends. A span with both
    an archive and a custody copy refuses. Returns (the staging records, {span id: staged directory})."""
    if not getattr(a, "stage_archives", False):
        return [], {}
    pinned = {span["span_id"]: span["offload_manifest_sha256"] for span in pins["spans"]}
    try:
        plan = [(span["span_id"], layout.archive(span["span_id"])) for span in roster]
        plan = [(sid, paths) for sid, paths in plan if paths is not None]
        if not plan:
            raise F.LookInputError("--stage-archives: the look's archives directory holds no roster span's archive")
        for sid, _ in plan:
            if os.path.lexists(layout.span(sid)):
                raise F.LookInputError(f"--stage-archives: {sid} has both an archive and a custody copy")
        private = layout.private_temp("jw-look-staging-")
    except M.ManifestError as error:
        raise F.LookInputError("staging: " + "; ".join(error.problems)) from None
    stack.callback(shutil.rmtree, private, True)
    records, staged = [], {}
    for sid, paths in plan:             # every span is checked above before the first archive is expanded
        records.append(stage_archive(sid, paths["archive"], paths["manifest"], paths["marker"], private,
                                     manifest_sha256=pinned[sid], doc=_VERIFIED[0][0]))
        staged[sid] = private / sid
    return records, staged


# =============================================================================================== stage-1 reader
_RICH_TS = re.compile(rb'"timestamp_s":\s*(-?[0-9][0-9.eE+-]*)')
_RICH_EL = re.compile(rb'"elapsed_ns":\s*([0-9]+)')
_PL_TP = re.compile(rb"<key>thermal_pressure</key>\s*<string>([^<]*)</string>")
_PL_EL = re.compile(rb"<key>elapsed_ns</key>\s*<integer>([0-9]+)</integer>")


def native_states(bundle, lo, hi):
    """[(row end epoch, state)] for rows ending in [lo, hi]. Pattern extraction only (module docstring). Read only in
    stage 1's protected phase: a fault in the protected files is a ContentRefusal (``native_states``)."""
    ends = []
    with open(bundle / "rich_telemetry.jsonl", "rb") as f:
        for line in f:
            if not line.strip():
                continue
            m, e = _RICH_TS.search(line), _RICH_EL.search(line)
            if not m or not e:
                raise ContentRefusal("native_states", "rich_telemetry: a row without timestamp_s or elapsed_ns")
            end = float(m.group(1))
            if not math.isfinite(end):
                raise ContentRefusal("native_states", "rich_telemetry: a row with a non-finite timestamp_s")
            ends.append((end, int(e.group(1))))
            del line
    with open(bundle / "raw/powermetrics.plist", "rb") as f:
        frames = [p for p in f.read().split(b"\0") if p.strip()]
    if not (len(frames) == len(ends) or len(frames) == len(ends) + 1):
        raise ContentRefusal("native_states", "plist/rich frame count mismatch")
    out = []
    for i, (end, el) in enumerate(ends):
        if not (lo <= end <= hi):
            continue
        fr = frames[i]
        me = _PL_EL.search(fr)
        if not me or int(me.group(1)) != el:
            raise ContentRefusal("native_states", "plist/rich elapsed mismatch")
        mt = _PL_TP.search(fr)
        out.append({"t_end_s": end, "state": mt.group(1).decode() if mt else None})
    del frames
    return out


def journal_readings(bundle, lo, hi, fan_keys):
    out = []
    for r in _jsonl(bundle / "outputs/align_thermal.jsonl"):
        if r.get("kind") != "reading" or r.get("error"):
            continue
        t = _real(r["finished"]["wall_ns"], "align_thermal: finished.wall_ns") / 1e9
        if not (lo <= t <= hi):
            continue
        v = r.get("values") or {}
        st = v.get("status") or {}
        sen = v.get("sensors") or {}
        pmo = st.get("pm_observed_ns")
        fresh = type(pmo) is int and (r["started"]["monotonic_ns"] - pmo) <= PM_FRESH_S * 1e9
        fans = [sen.get(k) for k in fan_keys]
        fan = ((sum(_real(x, "align_thermal: fan reading") for x in fans) / len(fans))
               if fans and all(x is not None for x in fans) else None)  # R-7
        lvl = st.get("os_level")
        out.append({"t_s": t, "os_level": lvl if type(lvl) is int else None,
                    "pm_state": st.get("pm_state") if isinstance(st.get("pm_state"), str) else None,
                    "pm_fresh": bool(fresh),
                    "tf08_c": None if sen.get("Tf08") is None else _real(sen["Tf08"], "align_thermal: Tf08"),
                    "fan_rpm": fan,
                    "tv0h_c": None if sen.get("TV0h") is None else _real(sen["TV0h"], "align_thermal: TV0h")})
    out.sort(key=lambda x: x["t_s"])
    return out


def token_stamps(bundle):
    toks = []
    with open(bundle / "events.jsonl") as f:
        for line in f:
            if not line.strip():
                continue
            e = M.strict_json(line)
            if e.get("event_type") == "token":
                md = e.get("metadata") or {}
                if md.get("align_turn_index", 0) not in (0, None):
                    raise F.LookInputError("events: a multi-turn leg")
                toks.append((_whole(md["index"], "events: token index"),
                             _real(e["timestamp_s"], "events: token timestamp_s")))
            del e
    toks.sort()
    if [i for i, _ in toks] != list(range(len(toks))):
        raise F.LookInputError("events: token indices not contiguous")
    t = [s for _, s in toks]
    if any(b < a for a, b in zip(t, t[1:])):
        raise F.LookInputError("events: token stamps not monotone")
    return t


def build_turn(bundle, result, fan_keys):
    """A leg's level-R turn: its operational half (``turn_operational``), then the native power-management states
    from rich_telemetry.jsonl and raw/powermetrics.plist, the turn's only protected sources."""
    turn = turn_operational(bundle, result, fan_keys)
    turn["native_pm"] = native_states(bundle, turn["turn_start_s"], turn["last_token_s"])
    return turn


def turn_operational(bundle, result, fan_keys):
    """The turn as the bundle's journals give it (align_turns.jsonl, events.jsonl, align_thermal.jsonl), with no
    native states: no trace, telemetry, powermetrics or meter file is opened. The preflight (``plan_leg``) builds it
    for every leg before the first protected source opens; the protected phase adds the native states."""
    turns = _jsonl(bundle / "outputs/align_turns.jsonl")
    if len(turns) != 1:
        raise F.LookInputError("align_turns: not one turn")
    tr = turns[0]
    ts = _real(tr["start_stamp"]["epoch_s"], "align_turns: start_stamp.epoch_s")
    if type(tr["generation"]["output_token_ids"]) is not list:
        raise WriterShape("align_turns: output_token_ids is not a list")
    n_out = len(tr["generation"]["output_token_ids"])          # LENGTH only
    P = tr["generation"].get("prefill_tokens", result.get("prefill_tokens"))
    if P is None:
        raise KeyError("prefill_tokens")          # no recorded prefill: the leg has no readable turn
    P = _whole(P, "align_turns: prefill_tokens")
    del turns, tr
    tok = token_stamps(bundle)
    if len(tok) != n_out or not tok:
        raise F.LookInputError("token count differs from the output length")
    N = len(tok)
    segs = [{"seg": 0, "kind": "prefill", "n_tokens": P, "edge_lo": None, "edge_hi": None, "tok_first": None,
             "tok_last": None, "wall_start_s": ts, "wall_end_s": tok[0], "first_token_s": None}]
    for k in range(N // F.BLOCK):
        lo = 0 if k == 0 else F.BLOCK * k - 1
        hi = F.BLOCK * k + F.BLOCK - 1
        segs.append({"seg": k + 1, "kind": "decode", "block": k, "n_tokens": F.BLOCK, "tok_first": F.BLOCK * k,
                     "tok_last": hi, "edge_lo": lo, "edge_hi": hi, "wall_start_s": tok[lo], "wall_end_s": tok[hi],
                     "first_token_s": tok[F.BLOCK * k]})
    tails = []
    for L in sorted(F.PREFIX.values(), reverse=True):
        if L >= N:
            continue
        nb = L // F.BLOCK
        a, lo, hi = F.BLOCK * nb, F.BLOCK * nb - 1, L - 1
        tails.append({"prefix_len": L, "kind": "prefix_tail", "tok_first": a, "tok_last": hi, "n_tokens": L - a,
                      "edge_lo": lo, "edge_hi": hi, "wall_start_s": tok[lo], "wall_end_s": tok[hi],
                      "first_token_s": tok[a]})
    return {"prefill_tokens": P, "decode_tokens": N, "turn_start_s": ts, "first_token_s": tok[0],
            "last_token_s": tok[-1], "segments": segs, "prefix_tails": tails,
            "journal": journal_readings(bundle, ts - JOURNAL_PRE_S, tok[-1] + JOURNAL_POST_S, fan_keys)}


def meter_offsets(sm):
    """RL-167 R-20: (header wall-minus-raw offset, end-of-span offset) in ns, from the span's streams through the time
    reader (``time_fields``): the header offset of the first stream whose header carries both stamps (the header the
    stage-2 decoder applies; Mythos round-5 N1: the monitor writes it with sorted keys, which the reader takes as any
    other key order), and rt - rx of the last poll line carrying both, over the streams in order. (None, None) with no
    stream; end None when no poll carries both stamps."""
    header_off, end_off = None, None
    for v in sm.views:
        h = v["header"] or {}
        if header_off is None and type(h.get("start_raw_ns")) is int and type(h.get("start_real_ns")) is int:
            header_off = h["start_real_ns"] - h["start_raw_ns"]
        for p in reversed(v["polls"]):
            if type(p.get("rx")) is int and type(p.get("rt")) is int:
                end_off = p["rt"] - p["rx"]
                break
    return header_off, end_off


def draft_ledger_check(looks_doc, stage1_sha256):
    """Synthetic runs (--allow-draft) only: a scratch ledger's row for this look names this stage-1 hash at
    stage1_committed or later. A real look uses manifest.require_stage1_committed on the committed ledger."""
    M.validate_look_ledger(looks_doc)
    row = next((r for r in looks_doc["looks"] if r.get("look_id") == F.LOOK_ID), None)
    if row and row["status"] in release.SPENT_STATUSES:
        raise F.LookInputError("draft ledger: the manifest id is already spent")
    if row is None or row.get("status") != "stage1_committed":
        raise F.LookInputError("draft ledger: the look's row is not at stage1_committed or later")
    if row.get("stage1_sha256") != stage1_sha256:
        raise F.LookInputError("draft ledger: the row does not name this stage-1 file's sha256")
    return row


def _mode(result):
    m = result.get("ac_powermode")
    return m.get("value") if isinstance(m, dict) else m


def span_meter(sdir):
    """(TF.SpanMeter or None, why). A ``.zst`` sibling refuses the look (Mythos round-5 N8: decompress the custody
    copy); a stream the decoder could not read gives None and the reason, and every leg of the span is excluded by
    rule 4's trace clause, so stage 2 never opens it (RL-173 E.1: one bad stream costs its span's legs, not the look)."""
    try:
        TF.span_streams(sdir)
    except TF.TimeFieldError as exc:          # the preflight refused a desk-compressed stream before any open
        raise PreflightBreach(f"custody: {exc}") from None
    try:
        return TF.SpanMeter(sdir), None
    except TF.TimeFieldError as exc:
        return None, str(exc)


def trace_holes(L_turn, bundle, sm, sm_why, leg_key="(leg)"):
    """RL-173 E.1 items 1 and 2, the two time-stamp clauses (rule 3 for the GPU rail, rule 4 for DC-in), on the
    leg's energy-fit intervals (its segments and prefix tails), from time fields only (``time_fields``):
    * GPU rail: the longest stretch of an interval with no power_trace.csv gpu_power row over 2 s excludes the leg;
    * DC-in: an interval not bracketed by decoded meter samples, a gap over 2 s between consecutive decoded samples
      in one, or a clock-fit excess over 2 s on a stream whose samples reach the leg, excludes the leg.
    The numbers are the ones stage 2 would compute (its backstop calls the same functions)."""
    ivs = TF.connected_intervals([(x["wall_start_s"], x["wall_end_s"])
                                  for x in L_turn["segments"] + L_turn["prefix_tails"]])
    gpu = {"max_gap_s": None, "rows_sha256": None, "excluded": True, "reason": None}
    try:
        rows = TF.gpu_rows(bundle)
        ss, ee = [r[0] for r in rows], [r[1] for r in rows]
        gpu["max_gap_s"] = max(TF.gpu_max_uncovered(ss, ee, a, b) for a, b in ivs)
        gpu["rows_sha256"] = TF.rows_digest(rows)
        gpu["excluded"] = gpu["max_gap_s"] > TF.MAX_GAP_S
        gpu["reason"] = "a stretch over 2 s with no power_trace row" if gpu["excluded"] else None
    except FileNotFoundError:
        gpu["reason"] = "no power_trace.csv"
    except TF.CompressedCustody as exc:               # Mythos r5 N8: the preflight refuses it before any open
        raise PreflightBreach(f"GPU rail: {leg_key}: {exc}") from None
    except TF.TimeFieldError as exc:
        gpu["reason"] = str(exc)
    dc = {"max_gap_s": None, "bracketed": False, "clock_fit_excess_s": None, "excluded": True, "reason": None}
    if sm is None:
        dc["reason"] = f"a meter stream the decoder cannot read ({sm_why})"
    else:
        sup = [TF.support(sm.t, a, b) for a, b in ivs]
        dc["bracketed"] = all(x is not None for x in sup)
        gaps = [x[2] for x in sup if x is not None]
        dc["max_gap_s"] = max(gaps) if gaps else None
        dc["clock_fit_excess_s"] = sm.excess_over(min(a for a, _ in ivs), max(b for _, b in ivs))
        if not dc["bracketed"]:
            dc["reason"] = "an energy-fit interval not bracketed by decoded meter samples"
        elif dc["max_gap_s"] > TF.MAX_GAP_S:
            dc["reason"] = "a gap over 2 s between decoded meter samples"
        elif dc["clock_fit_excess_s"] is not None and dc["clock_fit_excess_s"] > TF.CLOCK_FIT_EXCESS_MAX_S:
            dc["reason"] = "a meter clock-fit excess over 2 s"
        dc["excluded"] = dc["reason"] is not None
    return {"gpu_rail": gpu, "dc_in": dc}


RULED_RULES = ("sidecar_coverage", "km003c_clean")


def power_of(entry):
    return "high_power" if entry["block_id"].startswith("hp-") else "automatic"


def soak_reference(sdir):
    """The span's soak reference TV0h, or None when the file or the field is absent."""
    try:
        soak = _json(sdir / "soak/soak_reference.json")["sensors_c"]["TV0h"]
    except M.ManifestError:
        raise                                     # duplicate keys or a nonfinite number: never an absent reference
    except (OSError, KeyError, TypeError, ValueError):
        soak = None
    if soak is not None:
        soak = _real(soak, "soak_reference: sensors_c.TV0h")
    return soak


def operational_inclusion(result, attempts, v34, power):
    """A leg's six verdicts as its record and the committed rules-3/4 verdict file give them, before the replay and
    the trace clauses read any protected source. Those later reads can only exclude further."""
    return {"ran_to_cap": result.get("leg_status") == "complete" and result.get("decode_cap_reached") is True,
            "g0_released": result.get("g0_released") is True,
            "sidecar_coverage": v34["sidecar_coverage"] is True, "km003c_clean": v34["km003c_clean"] is True,
            "not_a_contaminated_attempt": bool(attempts) and not attempts[-1].get("contaminated"),
            "block_power_mode": _mode(result) == MODE_BY_POWER[power]}


def read_span(sdir, entry, rules34, fan_keys, ruled=None):
    """(span, legs) of one roster span, in level-R shape: the span's preflight plan (``plan_span``), then its
    protected read (``protected_span``). Opens no energy value: power_trace.csv and the meter streams only through
    the time reader (RL-173 E.1). ``ruled``: {leg_key: (rule, ruling)}, the research lead's named exclusions for a
    stage 1 run once more (RL-173 E.1 item 4)."""
    return protected_span(plan_span(sdir, entry, rules34, fan_keys), fan_keys, {} if ruled is None else ruled)


def read_look_input(roster, sdir_of, rules34, fan_keys=FAN_KEYS, ruled=None, *, synthetic_only=False):
    """Level R from the custody copy: ``stage1_preflight`` over the whole roster, then ``read_protected``.
    `synthetic` is true only when every span's runner receipt says so (the synthetic generator writes it; a real
    runner never does)."""
    plan = stage1_preflight(roster, sdir_of, rules34, fan_keys, ruled, synthetic_only=synthetic_only)
    return read_protected(plan, fan_keys, ruled)


# =============================================================================================== stage 1, phase 1
ROSTER_ENTRY_KEYS = ("span_id", "block_id", "role", "t0_local_date")
ROSTER_ROLES = ("fit", "describe")
_ROSTER_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")      # the stage-1 schema's t0_local_date pattern, as its checker reads it
_LEG_ID = re.compile(r"[LH]\d{3}")                    # the leg part of the stage-1 schema's leg_key pattern


def check_roster(roster):
    """The roster's shape, every entry, before any custody file is read: a list of objects, each exactly the four
    fields ``validate --roster-out`` writes as text, the span id and block id as the registry's patterns
    (``manifest.SPAN_ID_RE``, ``manifest.BLOCK_ID_RE``: the stage-1 file's ``counts.by_block`` keys), the role fit or
    describe, the day a calendar date, and each span once."""
    if not isinstance(roster, list):                # one shape: validate --roster-out's JSON list
        raise F.LookInputError("roster: not a list of spans")
    seen = set()
    for entry in roster:
        if (not isinstance(entry, dict) or set(entry) != set(ROSTER_ENTRY_KEYS)
                or any(not isinstance(entry[k], str) for k in ROSTER_ENTRY_KEYS)):
            raise F.LookInputError("roster: a span entry is not exactly span_id, block_id, role and t0_local_date as "
                                   "text")
        if not M.SPAN_ID_RE.fullmatch(entry["span_id"]):
            raise F.LookInputError("roster: a span_id is not a registered span id")
        if not M.BLOCK_ID_RE.fullmatch(entry["block_id"]):
            raise F.LookInputError("roster: a block_id is not a registered block id")
        if entry["role"] not in ROSTER_ROLES:
            raise F.LookInputError("roster: a role is neither fit nor describe")
        if not _ROSTER_DATE.fullmatch(entry["t0_local_date"]):
            raise F.LookInputError("roster: a t0_local_date is not a calendar date")
        if entry["span_id"] in seen:
            raise F.LookInputError("roster: a span appears twice")
        seen.add(entry["span_id"])


def stage1_preflight(roster, sdir_of, rules34, fan_keys=FAN_KEYS, ruled=None, *, also_ruled=None,
                     synthetic_only=False, outputs=()):
    """Phase 1 of stage 1: the ONE function where every refusal that needs no protected file is made, for the whole
    roster, before the first protected source (a trace, telemetry, powermetrics or meter stream) opens (lead, PR #795
    round 8, C1; the merge audits on c3a0dd9f8 and 5a7a3eae0). In order:

    * the roster (``check_roster``);
    * admission: each span's operational files are a shape one pinned writer issues (``validate_runtime_bundles``);
    * the rules-3/4 verdict file is an object;
    * per span (``plan_span``): the run mode, the receipt against the roster entry, the soak fields, the soak reference,
      the meter streams' names, the receipt's leg ids; per leg (``plan_leg``): a verdict of two booleans, the record
      and summary, the cell, the G0 role, the bundle locator, the operational turn and the GPU trace's name;
    * the ruled exclusions (``ruled``, and a ruled rerun's superseded ones, ``also_ruled``) name recorded legs;
    * the soak-retry print's receipt fields;
    * the fit candidates: fit-role type-A legs that the records, the committed verdicts and the ruled exclusions
      include, with an operational turn and a start reading. If every development candidate has zero prefill seconds,
      or every one zero decode seconds, or no cell holding a fit candidate can supply both rates, stage 1 refuses
      whatever the protected reads give;
    * ``outputs``: each directory stage 1 writes into after the protected reads is a writable directory.

    Returns the plan ``stage1_protected`` reads. The reads here are the operational files the pin guard verified and
    directory names; nothing protected is opened."""
    check_roster(roster)
    validate_runtime_bundles(roster, sdir_of)
    if not isinstance(rules34, dict):
        raise F.LookInputError("rules 3 and 4: the verdict file is not an object of leg verdicts")
    spans = [plan_span(sdir_of(entry["span_id"]), entry, rules34, fan_keys, synthetic_only=synthetic_only)
             for entry in roster]
    recorded = {leg["key"] for span in spans for leg in span["legs"] if leg["recorded"]}
    for named in (ruled, also_ruled):
        unknown = sorted(set(named or {}) - recorded)
        if unknown:
            raise F.LookInputError(f"a ruled exclusion names a leg with no record on the roster: {unknown[0]}")
    try:
        I34.soak_retries_from({span["entry"]["span_id"]: span["soak_receipt"] for span in spans})
    except ValueError as exc:
        raise F.LookInputError(str(exc)) from None
    development, candidates = [], []
    for span in spans:
        if span["entry"]["role"] != "fit":
            continue
        for leg in span["legs"]:
            if (not leg["recorded"] or leg["leg_type"] != "A" or leg["turn"] is None or leg["key"] in (ruled or {})
                    or not all(leg["inclusion"].values())):
                continue
            development.append(leg)
            if F.start_reading(leg["turn"], span["soak"])[0] == "ok":
                candidates.append(leg["key"])
    for begin, end in (("turn_start_s", "first_token_s"), ("first_token_s", "last_token_s")):
        if development and all(leg["turn"][end] - leg["turn"][begin] <= 0 for leg in development):
            raise F.LookInputError("stage 1: zero prefill or decode seconds on every development leg that can enter "
                                   "the fit")
    # fit_interim.stage1 takes both rates over each cell's included development legs. The protected reads can only
    # exclude legs, so a fit exists only if some cell holding a fit candidate has a development leg with prefill
    # seconds and one with decode seconds (lead closing decision F4; final confirm audit on 2a3752363).
    cells = {}
    for leg in development:
        cells.setdefault(leg["cell"], []).append(leg)
    if candidates and not any(
            any(leg["key"] in candidates for leg in legs)
            and any(leg["turn"]["first_token_s"] - leg["turn"]["turn_start_s"] > 0 for leg in legs)
            and any(leg["turn"]["last_token_s"] - leg["turn"]["first_token_s"] > 0 for leg in legs)
            for legs in cells.values()):
        raise F.LookInputError("stage 1: zero prefill or decode seconds in every cell that holds a fit candidate")
    for directory in outputs:
        # F2: the private directory stage 1 writes level_r.json and stage1.json into after the protected reads
        if (os.path.islink(directory) or not os.path.isdir(directory)
                or not os.access(directory, os.W_OK | os.X_OK)):
            raise F.LookInputError("the look's private directory cannot be written: stage 1 writes its two files "
                                   "there after the protected reads")
    return {"spans": spans, "fit_candidates": candidates,
            "synthetic": bool(spans) and all(span["synthetic"] for span in spans)}


def plan_span(sdir, entry, rules34, fan_keys, *, synthetic_only=False):
    """One span's part of the preflight: every check on its receipt, soak files, stream names and legs."""
    sid = entry["span_id"]
    receipt = _json(sdir / "runner_receipt.json")
    synthetic = receipt.get("synthetic") is True
    if synthetic_only and not synthetic:
        raise F.LookInputError("--allow-draft runs on synthetic input only (Mythos N2)")
    epoch_s = receipt["started"]["epoch_s"]
    day = F.span_day(epoch_s, entry["t0_local_date"], sid)
    t0 = _real(epoch_s, "runner receipt: started.epoch_s")
    soak_receipt = I34.soak_fields(receipt)
    soak = soak_reference(sdir)
    try:
        TF.span_streams(sdir)                    # names only: a desk-compressed stream refuses the look
    except TF.TimeFieldError as exc:
        raise F.LookInputError(f"custody: {exc}") from None
    power = power_of(entry)
    leg_ids = receipt["roster"]
    if len(set(leg_ids)) != len(leg_ids):
        raise F.LookInputError(f"{sid}: runner receipt: a leg appears twice on the roster")
    if any(not _LEG_ID.fullmatch(leg_id) for leg_id in leg_ids):
        raise F.LookInputError(f"{sid}: runner receipt: a leg id is not L or H and three digits")
    legs = [plan_leg(sdir, entry, leg_id, rules34, power, fan_keys) for leg_id in leg_ids]
    return {"sdir": sdir, "entry": entry, "receipt": receipt, "synthetic": synthetic, "t0": t0, "day": day,
            "soak": soak, "soak_receipt": soak_receipt, "power": power, "legs": legs}


def plan_leg(sdir, entry, leg_id, rules34, power, fan_keys):
    """One leg's part of the preflight. Its turn is built here from the bundle's journals alone and checked as level R
    checks a turn (``fit_interim._validate_turn``, without the native states). A turn the journals cannot give on a
    leg its record and committed verdicts include refuses; on any other leg the leg carries no turn (a G0 timeout,
    cadence_leg.py: a bundle and no turn, is a ruled exclusion, rules 1 and 2). The replay and the trace clauses read
    protected sources later and can only exclude further."""
    key = f"{entry['span_id']}/{leg_id}"
    v34 = rules34.get(key)
    if v34 is None:
        raise F.LookInputError("rules 3 and 4: no verdict for a roster leg")
    if (not isinstance(v34, dict) or set(v34) != set(I34.VERDICT_KEYS)
            or any(type(v34[k]) is not bool for k in I34.VERDICT_KEYS)):
        raise F.LookInputError("rules 3 and 4: a roster leg's verdict is not sidecar_coverage and km003c_clean as "
                               "booleans")
    ldir = sdir / "legs" / leg_id
    if not (ldir / "leg_record.json").is_file():          # the span stopped before this leg (R-21)
        return {"key": key, "leg_id": leg_id, "recorded": False}
    rec = _json(ldir / "leg_record.json")
    spec, attempts, result = rec["spec"], rec["attempts"], rec.get("result") or {}
    summary = _json(ldir / "leg_summary.json") if (ldir / "leg_summary.json").is_file() else {}
    cell = _whole(spec["prefill_tokens"], "leg record: spec.prefill_tokens")
    if cell not in F.CELLS:
        raise F.LookInputError(f"{key}: cell_prompt_tokens is not a registered cell")
    if spec.get("g0_role") not in (None, "capture", "consume"):
        raise F.LookInputError(f"{key}: g0_role")
    inc = operational_inclusion(result, attempts, v34, power)
    bundle = M.runtime_bundle(sdir, leg_id, rec)
    turn = None
    if bundle is not None:
        try:
            turn = turn_operational(bundle, result, fan_keys)
            F._validate_turn(dict(turn, native_pm=[]), f"{key}.turn")
        except (M.ManifestError, WriterShape):
            raise
        except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
            if all(inc.values()):
                raise F.LookInputError(f"an included leg's bundle has no readable turn ({type(exc).__name__})")
            turn = None
        if turn is not None and entry["role"] != "describe" and TF.compressed_siblings([bundle / "power_trace.csv"]):
            raise F.LookInputError(f"GPU rail: {key}: power_trace.csv.zst is desk-compressed; the look reads a "
                                   "decompressed custody copy")
    return {"key": key, "leg_id": leg_id, "recorded": True, "spec": spec, "result": result, "summary": summary,
            "leg_type": "T" if spec.get("leg_type") == "T" else "A",          # R-21: spec.leg_type only
            "cell": cell, "g0_role": spec.get("g0_role"), "inclusion": inc, "bundle": bundle, "turn": turn}


# =============================================================================================== stage 1, phase 2
def read_protected(plan, fan_keys=FAN_KEYS, ruled=None):
    """Phase 2 of stage 1: level R from the preflight's plan and the protected time fields. From here on a refusal is
    a ContentRefusal (POST_OPEN_REASONS); any other stop is a PreflightBreach."""
    _PHASE["protected"] = True
    ruled = dict(ruled or {})
    spans, legs = [], []
    for span_plan in plan["spans"]:
        span, span_legs = protected_span(span_plan, fan_keys, ruled)
        spans.append(span)
        legs += span_legs
    return {"schema": F.INPUT_SCHEMA, "look_id": F.LOOK_ID, "synthetic": plan["synthetic"], "spans": spans,
            "legs": legs}


def protected_span(plan, fan_keys, ruled):
    """(span, legs) in level-R shape from one span's plan: the meter streams' time fields (``span_meter``), the
    rules-3/4 replay (``inclusion_34.judge_span``), each turn's native states (``native_states``) and the trace
    clauses (``trace_holes``). The operational values are the plan's."""
    sdir, entry = plan["sdir"], plan["entry"]
    files = {"runner_receipt.json": TF.file_sha256(sdir / "runner_receipt.json")}
    sm, sm_why = span_meter(sdir)
    # A committed verdict hashes the decision file, not the source copy. Replay the same blind rules on
    # this custody before admission; a stale true can never override a current failure. Committed false
    # decisions remain exclusions. The later trace clauses can only exclude further.
    selected = I34.keys(_json(ROOT / I34.RUNTIME_CONFIG)["sensors"])
    replayed, _, _ = I34.judge_span(sdir, entry["span_id"], selected)
    span = {"span_id": entry["span_id"], "block_id": entry["block_id"],
            "phase": "extension" if entry["role"] == "describe" else "development", "role": entry["role"],
            "power_mode": plan["power"], "t0_epoch_s": plan["t0"],
            "t0_local_date": plan["day"], "soak_reference_tv0h_c": plan["soak"], "marks": [],
            "meter_offsets_ns": dict(zip(("header", "end"), meter_offsets(sm) if sm else (None, None))),
            "soak_receipt": plan["soak_receipt"],
            "custody": {"files_sha256": files, "meter_time_sha256": sm.digest() if sm else None,
                        "meter_streams": sm.summary() if sm else [], "meter_unreadable": sm_why}}
    legs, marks, suppliers = [], set(), set()
    for leg in plan["legs"]:
        key, leg_id = leg["key"], leg["leg_id"]
        if not leg["recorded"]:
            legs.append({"leg_key": key, "span_id": entry["span_id"], "leg_id": leg_id, "leg_type": "A",
                         "cell_prompt_tokens": None, "g0_role": None,
                         "inclusion": {r: False for r in F.RULES}, "turn": None, "trace_holes": None,
                         "ruled_exclusion": None})
            continue
        files[f"legs/{leg_id}/leg_record.json"] = TF.file_sha256(sdir / "legs" / leg_id / "leg_record.json")
        ref = leg["summary"].get("span_reference")
        if isinstance(ref, dict):
            if isinstance(ref.get("leg_id"), str):
                suppliers.add(ref["leg_id"])
            if ref.get("redone"):
                marks.add("reference from a redo")
            if ref.get("excluded"):
                marks.add("reference from an excluded leg")
        inc = dict(leg["inclusion"])
        if leg["leg_type"] == "A":              # type-T runtime is never read or rejudged at this look
            for rule in I34.VERDICT_KEYS:
                inc[rule] = inc[rule] and replayed[key][rule]
            if entry["role"] == "fit" and sm is None:   # RL-174 A.4: every fit leg, even without a turn
                inc["km003c_clean"] = False
        turn, bundle = None, leg["bundle"]
        if leg["turn"] is not None:
            operational = copy.deepcopy(leg["turn"])
            try:
                native = native_states(bundle, operational["turn_start_s"], operational["last_token_s"])
            except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
                if all(inc.values()):
                    raise ContentRefusal("native_states", f"an included leg's bundle has no readable turn "
                                                          f"({type(exc).__name__})") from None
                native = None
            if native is not None:
                turn = dict(operational, native_pm=native)
        holes = None
        if turn is not None and entry["role"] != "describe":
            # RL-173 E.1: the two time-stamp clauses, on every development leg with a turn (hp-01's are never read)
            holes = trace_holes(turn, bundle, sm, sm_why, key)
            inc["sidecar_coverage"] = inc["sidecar_coverage"] and not holes["gpu_rail"]["excluded"]
            inc["km003c_clean"] = inc["km003c_clean"] and not holes["dc_in"]["excluded"]
        ruled_x = None
        if key in ruled:
            rule, ruling = ruled.pop(key)
            inc[rule] = False
            ruled_x = {"rule": rule, "ruling": ruling}
        legs.append({"leg_key": key, "span_id": entry["span_id"], "leg_id": leg_id, "leg_type": leg["leg_type"],
                     "cell_prompt_tokens": leg["cell"], "g0_role": leg["g0_role"],
                     "inclusion": inc, "turn": turn, "trace_holes": holes, "ruled_exclusion": ruled_x})
    # RL-161 §4 (Mythos cold seats 7 and N3): the leg that supplied the span's reference, excluded AT THE LOOK (any of
    # the six verdicts, rules 3 and 4 included), marks the span when a consumer is on its roster. The supplier is
    # named by each consumer's leg_summary span_reference.leg_id (the runner takes the span's first leg, whatever
    # its shape: an own-shaped first leg supplies dev-03's first span); a capture-role leg also counts.
    consumers = any(leg["g0_role"] == "consume" for leg in legs)
    supplier_ids = suppliers | {leg["leg_id"] for leg in legs if leg["g0_role"] == "capture"}
    if consumers and any(not all(leg["inclusion"].values()) for leg in legs if leg["leg_id"] in supplier_ids):
        marks.add("reference from an excluded leg")
    span["marks"] = sorted(marks)
    span["custody"]["files_sha256"] = M.nonenergy_files(sdir)
    span["custody"]["native_pm_sha256"] = M.native_pm_files(sdir)
    return span, legs


# The fit's refusals by their text (fit_interim.stage1), each a condition on what the protected reads leave in the fit.
# Every other refusal of fit_interim.stage1 after the first open is a check the preflight owns: a breach.
FIT_CONTENT_REASONS = (("no_leg_enters_fit", re.compile(r"stage 1: no leg enters the fit")),
                       ("zero_rate_seconds", re.compile(r"stage 1: zero prefill or decode seconds")),
                       ("native_states", re.compile(r"legs\[\d+\]\.turn\.native_pm\[\d+\]: .*")))


def fit_stage1(look_input, input_sha, plan):
    """fit_interim.stage1 on a custody look input, in the protected phase: its refusals as POST_OPEN_REASONS."""
    try:
        return F.stage1(look_input, input_sha, code_hashes())
    except F.LookInputError as exc:
        text = str(exc)
        for code, pattern in FIT_CONTENT_REASONS:
            if pattern.fullmatch(text):
                if code == "no_leg_enters_fit" and not plan["fit_candidates"]:
                    raise ContentRefusal("no_fit_candidate", text) from None
                raise ContentRefusal(code, text) from None
        raise PreflightBreach(f"fit_interim: {text}") from None


def validate_runtime_bundles(roster, sdir_of):
    """RL-184 section 3.3, the one admission check of both stages, before any trace, telemetry or meter file opens
    and before the reservation: every rostered span's receipt, soak reference, leg records and summaries and each
    selected runtime bundle's journals are a shape one pinned writer revision issues
    (``joulewise.cadence_looks.admission``). Then each bundle locator stays inside its leg's runtime directory."""
    spans = [(span["span_id"], ADM.SpanFiles(sdir_of(span["span_id"]))) for span in roster]
    try:
        ADM.validate_roster(spans)
    except ADM.Refusal as exc:
        raise F.LookInputError(f"admission: {exc}") from None
    for span in roster:
        M.check_runtime_bundles(Path(sdir_of(span["span_id"])))


def stage2_preflight(stage1_out, sdir_of):
    """Structural checks of every file stage 2 will open, by presence only (stat, never a read): each
    energy-fit leg's power_trace.csv, and a meter stream in its span. Run by stage 1, so a layout fault refuses
    before any energy file is opened (Mythos cold seat 4). Every energy-fit leg passed both trace clauses (RL-173
    E.1); stage 2 judges the decoded samples again as the backstop."""
    for L in stage1_out["legs"]:
        if not L["in_energy_fit"]:
            continue
        sdir = sdir_of(L["span_id"])
        leg_id = L["leg_key"].split("/", 1)[1]
        rec = _json(sdir / "legs" / leg_id / "leg_record.json")
        bundle = M.runtime_bundle(sdir, leg_id, rec)
        if bundle is None or not (bundle / "power_trace.csv").is_file():
            raise PreflightBreach(f"stage-2 preflight: {L['leg_key']} has no power_trace.csv")
        if not TF.span_streams(sdir):
            raise PreflightBreach(f"stage-2 preflight: {L['leg_key']}'s span has no meter stream")
        th = L.get("trace_holes")
        if not th or th["gpu_rail"]["excluded"] or th["dc_in"]["excluded"]:
            raise PreflightBreach(f"stage-2 preflight: {L['leg_key']} is in the energy fit without both trace clauses")


# =============================================================================================== stage-2 reader
def load_step3(path=None):
    if path is None:
        mod = importlib.import_module("joulewise.cadence_looks.step3_energy_ratios")
        path = mod.__file__
    if sha256_file(path) != STEP3_SHA256:
        raise F.LookInputError("the step 3 module is not the committed bytes")
    spec = importlib.util.spec_from_file_location("_step3_pinned", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, path


class MeterSpan:
    """KM003C samples of a span on wall-clock epoch seconds; Vbus x Ibus; in memory only. ``expected_t``: the time
    reader's decoded sample times for the span (stage 1 judged the trace clauses on them); the decoder's times must
    be exactly these, or the span refuses (a backstop on the reader: no energy is printed)."""

    def __init__(self, sdir, expected_t=None, leg_key=None):
        from joulewise.external import km003c_parse as kp
        identity = leg_key or Path(sdir).name
        paths = TF.span_streams(sdir)
        if not paths:
            raise F.LookInputError(f"DC-in: {identity}: no meter stream in the span")
        t, w, steps = [], [], []
        for p in paths:
            try:
                st = kp.parse(p)
            except (ValueError, TypeError, KeyError, IndexError, OverflowError, OSError):
                raise F.LookInputError(f"DC-in: {identity}: meter stream {Path(p).name}: decoder fault; "
                                       "sample support and gap unavailable") from None
            if not st.present or not st.aligned:     # contributes no sample; a fit interval it alone spans refuses
                del st
                continue
            steps.append(kp.STEP_MS[st.header["rate_idx"]] / 1000.0)
            off = int(st.header["start_real_ns"]) - int(st.header["start_raw_ns"])    # RAW -> REALTIME (R-20)
            t += [(h + off) / 1e9 for h in st.host_ns]
            w += list(st.watts)
            del st
        if not t:
            raise F.LookInputError(f"DC-in: {identity}: no meter stream in the span has aligned samples")
        order = sorted(range(len(t)), key=t.__getitem__)
        self.t = [t[i] for i in order]
        self.w = [w[i] for i in order]
        self.step_s = max(steps)
        if expected_t is not None and self.t != list(expected_t):
            raise F.LookInputError(f"DC-in: {identity}: the decoder's sample times differ from the time "
                                   "reader's, on which stage 1 judged the trace clauses")

    def _support(self, a, b, leg_key):
        """(i0, i1): the DECODED samples bracketing [a, b], with no two consecutive decoded samples between them more
        than 2 s apart (RL-166 Q7's gap, on the series that is integrated; ``time_fields.support``, the function
        stage 1's DC-in clause calls). Otherwise refuse, naming the leg and the gap (RL-173 E.1 items 3 and 4: the
        backstop; stage 1 has already excluded every leg this could refuse)."""
        if b < a:
            raise F.LookInputError(f"{leg_key}: a segment with its end before its start")
        sup = TF.support(self.t, a, b)
        if sup is None:
            raise F.LookInputError(f"DC-in: {leg_key}: an energy-fit interval is not bracketed by meter samples")
        i0, i1, gap = sup
        if gap > METER_MAX_GAP_S:
            raise F.LookInputError(f"DC-in: {leg_key}: a gap of {gap:.3f} s between meter samples inside an "
                                   "energy-fit interval")
        return i0, i1

    def _at(self, x, i):
        t0, t1 = self.t[i], self.t[i + 1]
        return self.w[i] + (self.w[i + 1] - self.w[i]) * (x - t0) / (t1 - t0) if t1 > t0 else self.w[i]

    def coverage(self, a, b):
        """Fraction of [a, b] within half a nominal sample period of a sample (a print; decides nothing)."""
        if b <= a:
            return None
        h = 0.5 * self.step_s
        import bisect
        i = max(0, bisect.bisect_left(self.t, a - h))
        cov, edge = 0.0, a
        while i < len(self.t) and self.t[i] - h < b:
            lo, hi = max(edge, self.t[i] - h, a), min(b, self.t[i] + h)
            if hi > lo:
                cov += hi - lo
                edge = hi
            i += 1
        return cov / (b - a)

    def energy(self, a, b, leg_key="(leg)"):
        """Trapezoid between consecutive decoded samples, cut at a and b (linear value at the cuts), on supported
        intervals only (see _support). No value is held past the last sample."""
        i, _ = self._support(a, b, leg_key)
        tot = 0.0
        while i < len(self.t) - 1 and self.t[i] < b:
            lo, hi = max(a, self.t[i]), min(b, self.t[i + 1])
            if hi > lo:
                tot += 0.5 * (self._at(lo, i) + self._at(hi, i)) * (hi - lo)
            i += 1
        return tot


def gpu_max_uncovered_s(trace, a, b):
    """The longest stretch of [a, b] that no power_trace row covers (time_fields.gpu_max_uncovered, the one
    definition stage 1's GPU clause also calls)."""
    return TF.gpu_max_uncovered(trace.s, trace.e, a, b)


def gpu_gap_rule(doc):
    """RL-173 E.1 item 3, the backstop: refuse a GPU-rail segment with an uncovered stretch over max_gap_s. Read from
    the manifest's fit.gpu_trace_hole_refusal {"enabled": bool, "max_gap_s": number}; absent or disabled, the GPU rail
    integrates the rows present, as step 3 does."""
    sw = ((doc or {}).get("fit") or {}).get("gpu_trace_hole_refusal") or {}
    return float(sw.get("max_gap_s", METER_MAX_GAP_S)) if sw.get("enabled") is True else None


def custody_check(stage1_out, sdir_of):
    """Mythos round-5 N6, before any energy file opens: the custody stage 2 is about to read is the custody stage 1
    judged. Per span with an energy-fit leg, the runner receipt's and each energy-fit leg's leg_record.json sha256,
    and the digest of every meter time field (``time_fields.SpanMeter.digest``); per energy-fit leg, the digest of
    its power_trace.csv gpu rows' stamps. All from the time reader and operational files: no energy value. Returns
    {span_id: SpanMeter} for the decoder backstop."""
    problems = M.nonenergy_problems(stage1_out, sdir_of,
                                   [L["span_id"] for L in stage1_out["legs"] if L["in_energy_fit"]])
    if problems:
        raise F.LookInputError("; ".join(problems))
    meters = {}
    spans = {sp["span_id"]: sp for sp in stage1_out["roster"]["spans"]}
    for L in stage1_out["legs"]:
        if not L["in_energy_fit"]:
            continue
        sid = L["span_id"]
        sdir = sdir_of(sid)
        cust = spans[sid].get("custody") or {}
        files = cust.get("files_sha256") or {}
        leg_id = L["leg_key"].split("/", 1)[1]
        for rel in ("runner_receipt.json", f"legs/{leg_id}/leg_record.json"):
            if files.get(rel) is None or TF.file_sha256(sdir / rel) != files[rel]:
                raise F.LookInputError(f"custody: {sid}/{rel} is not the file stage 1 read")
        if sid not in meters:
            try:
                sm = TF.SpanMeter(sdir)
            except TF.TimeFieldError as exc:
                raise F.LookInputError(f"custody: {sid}: {exc}") from None
            if sm.digest() != cust.get("meter_time_sha256"):
                raise F.LookInputError(f"custody: {sid}'s meter streams are not the ones stage 1 read (time fields)")
            meters[sid] = sm
        rec = _json(sdir / "legs" / leg_id / "leg_record.json")
        bundle = M.runtime_bundle(sdir, leg_id, rec)
        if bundle is None:
            raise F.LookInputError("custody: an energy-fit leg has no bundle")
        try:
            rows = TF.gpu_rows(bundle)
        except (OSError, TF.TimeFieldError) as exc:
            raise F.LookInputError(f"custody: {L['leg_key']}'s power_trace.csv: {type(exc).__name__}") from None
        if TF.rows_digest(rows) != ((L.get("trace_holes") or {}).get("gpu_rail") or {}).get("rows_sha256"):
            raise F.LookInputError(f"custody: {L['leg_key']}'s power_trace.csv is not the one stage 1 read "
                                   "(row stamps)")
    return meters


def read_segment_energy(stage1_out, sdir_of, step3_path=None, gpu_max_gap_s=None, span_times=None):
    """(the level-E object, in memory and never written in production; the custody record). gpu_max_gap_s: see
    gpu_gap_rule. span_times: custody_check's SpanMeters, whose decoded times the decoder must reproduce. The
    custody record names every energy file opened by sha256 (a hash of bytes, not a value)."""
    s3, _ = load_step3(step3_path)
    meters = {}
    fit_spans = {L["span_id"] for L in stage1_out["legs"] if L["in_energy_fit"]}
    opened = {f"{sp['span_id']}/{rel}": sha
              for sp in (stage1_out.get("roster") or {}).get("spans") or [] if sp["span_id"] in fit_spans
              for rel, sha in ((sp.get("custody") or {}).get("files_sha256") or {}).items()}
    out = {"schema": F.ENERGY_SCHEMA, "look_id": F.LOOK_ID, "synthetic": False,
           "input_sha256": stage1_out["input_sha256"], "legs": {}}
    for L in stage1_out["legs"]:
        if not L["in_energy_fit"]:                  # RL-167 §3: no hp-01 energy is opened
            continue
        key = L["leg_key"]
        sdir = sdir_of(L["span_id"])
        leg_id = key.split("/", 1)[1]
        rec = _json(sdir / "legs" / leg_id / "leg_record.json")
        bundle = M.runtime_bundle(sdir, leg_id, rec)
        if bundle is None:
            raise F.LookInputError("custody: an energy-fit leg has no bundle")
        opened[f"{L['span_id']}/legs/{leg_id}/runtime/{rec['result']['bundle']}/power_trace.csv"] = \
            TF.file_sha256(bundle / "power_trace.csv")
        try:
            trace = s3.Trace(s3.load_gpu_trace(str(bundle)))
        except (ValueError, TypeError, KeyError, IndexError, OverflowError, OSError):
            raise F.LookInputError(f"GPU rail: {key}: power_trace.csv: trace reader fault; "
                                   "row support and gap unavailable") from None
        # Check the connected fitted support before integrating any segment: a single hole may straddle
        # arbitrarily many block cuts, each of which would otherwise shorten the reported gap.
        if gpu_max_gap_s is not None:
            ivs = TF.connected_intervals([(x["wall_start_s"], x["wall_end_s"])
                                          for x in L["segments"] + L["prefix_tails"]])
            gap = max(gpu_max_uncovered_s(trace, a, b) for a, b in ivs)
            if gap > gpu_max_gap_s:
                raise F.LookInputError(f"GPU rail: {key}: {gap:.3f} s with no power_trace row inside an "
                                       "energy-fit interval")
        if L["span_id"] not in meters:
            sm = (span_times or {}).get(L["span_id"])
            meters[L["span_id"]] = MeterSpan(sdir, expected_t=sm.t if sm is not None else None, leg_key=key)
            for p in TF.span_streams(sdir):
                opened[f"{L['span_id']}/hazards/meter/{Path(p).name}"] = TF.file_sha256(p)
        m = meters[L["span_id"]]
        entry = {}

        def gpu_energy(a, b, trace=trace, key=key):
            if gpu_max_gap_s is not None:
                gap = gpu_max_uncovered_s(trace, a, b)
                if gap > gpu_max_gap_s:
                    raise F.LookInputError(f"GPU rail: {key}: {gap:.3f} s with no power_trace row inside an "
                                           "energy-fit interval")
            return trace.energy(a, b)

        def dc_energy(a, b, m=m, key=key):
            return m.energy(a, b, key)
        for ch, fn, cov in (("gpu_rail", gpu_energy, trace.coverage), ("dc_in", dc_energy, m.coverage)):
            segs = [fn(s["wall_start_s"], s["wall_end_s"]) for s in L["segments"]]
            tails = {str(t["prefix_len"]): fn(t["wall_start_s"], t["wall_end_s"]) for t in L["prefix_tails"]}
            covs = [c for c in (cov(s["wall_start_s"], s["wall_end_s"]) for s in L["segments"]) if c is not None]
            entry[ch] = {"segments": segs, "prefix_tails": tails, "coverage_min": min(covs) if covs else 1.0}
        out["legs"][key] = entry
        del trace
    return out, [{"path": k, "sha256": v} for k, v in sorted(opened.items())]


# =============================================================================================== main
def ruled_exclusions(pairs):
    """--ruled-exclusion LEG_KEY=RULE=RL-n (RL-173 E.1 item 4): {leg_key: (rule, ruling)}; RULE is sidecar_coverage
    (rule 3's GPU clause) or km003c_clean (rule 4's DC-in clause)."""
    out = {}
    for p in pairs or []:
        parts = p.split("=")
        if len(parts) != 3 or parts[1] not in RULED_RULES or not re.fullmatch(r"RL-\d+[a-z]?", parts[2]) \
                or parts[0] in out:
            raise F.LookInputError("--ruled-exclusion wants LEG_KEY=sidecar_coverage|km003c_clean=RL-n, once per leg")
        out[parts[0]] = (parts[1], parts[2])
    return out


def superseded_source(row, layout):
    """Authenticate the kept stage-1 and level-R files (superseded_stage1.json, superseded_level_r.json in the
    look's directory) before a ruled rerun reads custody."""
    try:
        raw = layout.read("superseded_stage1")
        kept_input = layout.read("superseded_level_r")
    except M.ManifestError as error:
        raise F.LookInputError("a ruled rerun needs the kept stage-1 and level-R files: " + "; ".join(error.problems)) from None
    last = row["stage1_superseded"][-1]
    if hashlib.sha256(raw).hexdigest() != last["stage1_sha256"]:
        raise F.LookInputError("the kept stage-1 file is not the superseded commitment")
    previous = json.loads(raw)
    if previous.get("manifest_sha256") != sha256_file(_VERIFIED[0][1]):
        raise F.LookInputError("a stage 1 run once more takes the replaced commitment's manifest unchanged")
    if hashlib.sha256(kept_input).hexdigest() != previous.get("input_sha256"):
        raise F.LookInputError("the kept level-R file is not the superseded stage-1 input")
    old_input = json.loads(kept_input)
    old_ruled = {leg["leg_key"]: (leg["ruled_exclusion"]["rule"], leg["ruled_exclusion"]["ruling"])
                 for leg in old_input.get("legs", []) if leg.get("ruled_exclusion")}
    return old_input, old_ruled


def cmd_stage1(a):
    with contextlib.ExitStack() as stack:
        return _stage1(a, stack)


def _stage1(a, stack):
    staging = []
    if a.level_r and not a.allow_draft:
        raise F.LookInputError("--level-r runs only with --allow-draft; a committed look reads custody")
    doc, mpath = _VERIFIED[0]
    layout = layout_of(doc)
    for key in ("stage1", "level_r"):                 # created once, never replaced: refuse before reading anything
        if layout.exists(key):
            raise F.LookInputError(f"{M.LOOK_FILES[key]} already exists in the look's directory")
    if a.level_r:
        raw = layout.read("input_level_r")
        look_input = json.loads(raw)
        input_sha = hashlib.sha256(raw).hexdigest()
        extra = {"roster_sha256": input_sha}        # a level-R run has no roster: its input file stands in
        sdir_of = None
    else:
        ruled = ruled_exclusions(a.ruled_exclusion)
        try:
            roster_raw, rules_raw = layout.read("roster"), layout.read("rules_3_4")
        except M.ManifestError as error:
            raise F.LookInputError("; ".join(error.problems)) from None
        roster_sha, rules_sha = hashlib.sha256(roster_raw).hexdigest(), hashlib.sha256(rules_raw).hexdigest()
        if not a.allow_draft:
            # Mythos r3 N8: the committed ledger names this manifest, roster and verdict file before custody opens;
            # RL-173 E.1 item 4: a stage 1 run once more names the research lead's ruled exclusions, nothing else
            row = M.require_inputs_committed(ROOT, F.LOOK_ID, sha256_file(mpath), roster_sha256=roster_sha,
                                             verdicts_sha256=rules_sha, ledger_ref=a.ledger_ref,
                                             ruled_exclusions={k: list(v) for k, v in ruled.items()})
        roster = M.strict_json(roster_raw)
        if not isinstance(roster, list) or not all(isinstance(s, dict) and isinstance(s.get("span_id"), str) for s in roster):
            raise F.LookInputError("roster: not a list of spans")
        # RL-194 and RL-194a, in this order. (1) The pin list is admitted before anything of custody is touched.
        # (2) A staged span is expanded by the staging process, against the offload manifest digest its pins
        # carry, into a private directory. (3) The verifier process checks every pinned file and this process the
        # operational ones it parses. Stage 1 opens and hashes no energy stream and no archive (RL-179 F-12) and
        # records nothing of the pin list: its output stays a function of time fields and operational files alone,
        # and a committed run's manifest hash already names the list.
        ids = [span["span_id"] for span in roster]
        loaded = load_pins(a, ids)
        staging, staged = stage_custody(a, roster, loaded[0], layout, stack)

        def sdir_of(sid):
            if sid in staged:
                return staged[sid]
            try:
                return layout.span(sid)
            except M.ManifestError as error:
                raise F.LookInputError("layout: " + "; ".join(error.problems)) from None
        admit_custody(a, ids, sdir_of, stack, streams="pass", loaded=loaded)
        rules34 = M.strict_json(rules_raw)
        superseded = (None, None)
        if ruled and not a.allow_draft:
            superseded = superseded_source(row, layout)
        # Phase 1 (C1): every refusal that needs no protected file, for the whole roster, then the loaded code and
        # the ledger gate the output records. Nothing protected has been opened.
        plan = stage1_preflight(roster, sdir_of, rules34, ruled=ruled, also_ruled=superseded[1],
                                synthetic_only=a.allow_draft,
                                outputs=sorted({layout.file(key).parent for key in ("stage1", "level_r")}))
        _guard_loaded(doc)
        a.ledger_gate_record = None if a.allow_draft else M.ledger_gate(ROOT, a.ledger_ref)
        extra = {"roster_sha256": roster_sha, "rules_3_4_sha256": rules_sha}
        return stage1_protected(a, layout, plan, ruled, superseded, extra, staging, sdir_of)
    if a.allow_draft and look_input.get("synthetic") is not True:
        raise F.LookInputError("--allow-draft runs on synthetic input only (Mythos N2)")
    out = F.stage1(look_input, input_sha, code_hashes())    # RL-172a's soak-retry print is level R's (F.stage1)
    out["staging"] = staging
    out["code_sha256"].update({f"input:{k}": v for k, v in extra.items()})
    a.layout = layout
    return _stamp(out, a)


def stage1_protected(a, layout, plan, ruled, superseded, extra, staging, sdir_of):
    """Phase 2 of a custody stage 1 (C1): the protected reads (``read_protected``), the fit (``fit_stage1``), the
    stage-2 layout backstop and the provenance. Every refusal here is a ContentRefusal (POST_OPEN_REASONS); every
    other stop is a PreflightBreach. ``tests/cadence/test_merge_audit_c3a0dd9f8.py`` (PostOpenAllowlist) enumerates
    the raise sites of this function and of every function of this module it reaches."""
    old_input, old_ruled = superseded
    if old_input is not None:
        before = read_protected(plan, ruled=old_ruled)
        if F.dump(before) != F.dump(old_input):
            raise ContentRefusal("ruled_rerun_changed", "a ruled rerun changes the superseded level-R source; only "
                                                        "the named exclusions may change")
    look_input = read_protected(plan, ruled=ruled)
    if old_input is not None:
        # The exclusion-aware read may change only named flags and their derived span marks. Verify the
        # second read too, so a changed source between reads cannot enter the new fit.
        projection = json.loads(F.dump(look_input))
        old_legs = {leg["leg_key"]: leg for leg in before["legs"]}
        for leg in projection["legs"]:
            if leg["leg_key"] in ruled:
                rule = ruled[leg["leg_key"]][0]
                leg["inclusion"][rule] = old_legs[leg["leg_key"]]["inclusion"][rule]
                leg["ruled_exclusion"] = old_legs[leg["leg_key"]]["ruled_exclusion"]
        old_spans = {span["span_id"]: span for span in before["spans"]}
        changed_spans = {key.rsplit("/", 1)[0] for key in ruled}
        for span in projection["spans"]:
            if span["span_id"] in changed_spans:
                span["marks"] = old_spans[span["span_id"]]["marks"]
        if F.dump(projection) != F.dump(before):
            raise ContentRefusal("ruled_rerun_changed", "a ruled rerun changes sources beyond the named exclusions")
    data = F.dump(look_input)
    input_sha = hashlib.sha256(data).hexdigest()
    a.look_input_bytes = data       # level_r.json is written with stage1.json, after every check has passed
    out = fit_stage1(look_input, input_sha, plan)    # RL-172a's soak-retry print is level R's (F.stage1)
    out["staging"] = staging
    stage2_preflight(out, sdir_of)
    out["code_sha256"].update({f"input:{k}": v for k, v in extra.items()})
    a.layout = layout
    return _stamp_protected(out, a)


def cmd_stage2(a, *, keep_redirected=False):
    with contextlib.ExitStack() as stack:
        return _stage2(a, stack, keep_redirected=keep_redirected)


def _stage2(a, stack, *, keep_redirected=False):
    if a.level_e and not a.allow_draft:
        raise F.LookInputError("--level-e runs only with --allow-draft; a committed look reads custody")
    doc, manifest_path_ = _VERIFIED[0]
    layout = layout_of(doc)
    try:
        raw = layout.read("stage1")
    except M.ManifestError as error:
        raise F.LookInputError("stage 2: " + "; ".join(error.problems)) from None
    if hashlib.sha256(raw).hexdigest() != a.stage1_sha256:
        raise F.LookInputError("stage 2: the stage-1 file does not match --stage1-sha256")
    s1 = json.loads(raw)
    if F.dump(s1) != raw:
        raise F.LookInputError("stage 2: the stage-1 file is not in canonical form")
    if a.allow_draft and s1.get("synthetic") is not True:
        raise F.LookInputError("--allow-draft runs on synthetic input only (Mythos N2)")
    # committed: the repository's LOOKS.json row names this stage-1 file's sha256 (Mythos cold seat 8; N1), before any
    # energy opens. A synthetic (--allow-draft) run reads this checkout's LOOKS.json in its place.
    manifest_path = manifest_path_
    if a.allow_draft:
        row = draft_ledger_check(_json(ledger_path()), a.stage1_sha256)
        rc, head, _ = M._git(ROOT, "rev-parse", "HEAD")
        if rc:
            raise F.LookInputError("stage 2: cannot resolve the synthetic checkout's commit")
        commit = head.decode("ascii").strip()
        ledger_gate = None
    else:
        ledger_ref = a.ledger_ref
        if s1.get("synthetic") is not True:
            if ledger_ref not in (None, "origin/main", "refs/remotes/origin/main"):
                raise F.LookInputError("stage 2: campaign execution requires the row on origin/main")
            ledger_ref = "origin/main"
        commit, row = M.require_stage1_committed(ROOT, F.LOOK_ID, a.stage1_sha256, stage1_doc=s1,
                                               ledger_ref=ledger_ref, for_execution=True)
        ref, ref_commit = M.shared_ref(ROOT, ledger_ref)
        ledger_gate = {"commit": commit, "ref": ref, "ref_commit": ref_commit}
        if row["sha256"] != sha256_file(manifest_path):
            raise F.LookInputError("stage 2: the execution row names a different manifest")
    prepared = F.stage2_preflight(s1)
    stage2_energy_preflight(s1, a)
    validate_execution_row(row, s1, layout)
    twin_path = require_twin_runner(doc)
    try:
        restricted, public = release.destinations(ROOT, row)
    except (OSError, ValueError) as exc:
        raise F.LookInputError(str(exc)) from None
    overrides = ()                      # no span is read from anywhere but <root>/<span id> (audit 2, lead ruling)
    a.custody = None if a.level_e else str(layout.root)
    a.span_dir = []
    a.stage1 = str(layout.file("stage1"))      # the twin's child reads the same file, by the same derived path

    def sdir_of(sid):
        try:
            return layout.span(sid)
        except M.ManifestError as error:
            raise F.LookInputError("layout: " + "; ".join(error.problems)) from None
    if a.level_e:
        sdir_of = None
    if sdir_of is not None:
        # RL-194: stage 2's first act on custody, before any roster file is read and before the reservation
        # (a committed stage 2 runs under the manifest stage 1 names, so under the same pin list). From here on a
        # stream's pin is checked again at each open, immediately before it is decoded (RL-194a section 1 item 5).
        _, a.custody_pins_sha256 = admit_custody(a, [span["span_id"] for span in s1["roster"]["spans"]], sdir_of,
                                                 stack, streams="verify")
        synthetic_custody_only(s1, sdir_of)
        validate_runtime_bundles(s1["roster"]["spans"], sdir_of)
        ids = [leg["span_id"] for leg in s1["legs"] if leg["included"] and leg["role"] == "fit" and
               leg["leg_type"] == "A"]
        problems = M.nonenergy_problems(s1, sdir_of, ids, include_native_pm=False)
        if problems:
            raise F.LookInputError("; ".join(problems))
    _, public_schema = M.look_schemas(ROOT)
    coefficients_schema = M.coefficients_schema(ROOT)
    manifest_sha = sha256_file(manifest_path)

    def execute():
        finish_stage2(a, s1, prepared, doc, commit, manifest_sha, restricted, public, public_schema,
                      coefficients_schema, sdir_of, twin_path, ledger_gate=ledger_gate, overrides=overrides,
                      deadline=deadline)

    deadline = time.monotonic() + doc["stages"]["stage2"]["time_budget_s"]
    try:
        return release.run_reserved(restricted, execute, linear_algebra_error=F.np.linalg.LinAlgError,
                                    keep_redirected=keep_redirected)
    except FileExistsError:
        raise F.LookInputError("the manifest id already has an execution reservation") from None


def validate_execution_row(row, stage1, layout):
    try:
        public = ROOT / M.public_report_path(row)
    except M.ManifestError as error:
        raise F.LookInputError(f"stage 2: {error}") from None
    host = row.get("execution_host")
    if not host:
        raise F.LookInputError("stage 2: register the execution_host before reservation")
    if host != M.execution_host():
        raise F.LookInputError("stage 2: execution_host does not match this host")
    if not row.get("custody_root"):
        raise F.LookInputError("stage 2: register the custody_root in the ledger")
    try:                                # physical identity, never the spelling (audit 3, rule P1)
        same = os.path.samefile(row["custody_root"], layout.root)
    except (OSError, TypeError):
        same = False
    if not same:
        raise F.LookInputError("stage 2: the ledger's custody_root is not the root the manifest registers")
    # the reservation's two names, compared case-insensitively: a differently-cased file is the same file on a
    # case-insensitive volume, and may stand for it on any other (audit 2, lead ruling)
    for parent, name in ((layout.look, "RESTRICTED"), (public.parent, public.name)):
        if M.name_collision(parent, name) is not None:
            raise F.LookInputError(f"stage 2: a file beside the registered {name} differs from it only in case")
    holds = M.STAGE2_HOLD_FLAGS["interim"]
    raised = {flag for flag in holds if stage1[flag.split(".")[0]].get(flag.split(".")[1]) is True}
    if raised != set(row.get("holds_cleared", {})):
        raise F.LookInputError("stage 2: the committed stage-1 flags and ledger clearing rulings differ")


def require_twin_runner(doc):
    """Bind the child to the exact repository path and manifest digest before reservation."""
    pin = doc["fit"].get("twin")
    if not pin:
        raise F.LookInputError("stage 2: RL-180 requires the independent twin path and sha256")
    path = ROOT / pin["path"]
    if path.resolve() != path or not path.is_relative_to(ROOT) or not path.is_file():
        raise F.LookInputError("stage 2: the pinned twin script is missing from its canonical repository path")
    if sha256_file(path) != pin["sha256"]:
        raise F.LookInputError("stage 2: the twin sha256 differs from the manifest pin")
    # RL-194 condition 4: the wrapper that checks the pins for the twin, at its own canonical path and pin
    wrapper = ROOT / M.TWIN_WRAPPER_PATH
    pinned = {rel: sha for _, rel, sha in M.code_refs(doc)}
    if wrapper.resolve() != wrapper or not wrapper.is_file() or sha256_file(wrapper) != pinned.get(M.TWIN_WRAPPER_PATH):
        raise F.LookInputError("stage 2: the twin's pin-checking wrapper is not at its manifest pin")
    return path


def _bind_override_files(inventory, overrides):
    """Use the same overridden spans in the child's inventory and its reader."""
    for entry in inventory["files"]:
        sid, _, relative = entry["path"].partition("/")
        if sid in overrides:
            entry["path"] = str(overrides[sid] / relative)


def run_twin(twin_path, a, stage1, fit, step3, coefficients, *, doc, commit, manifest_sha, coefficient_sha,
             restricted, deadline, overrides):
    from joulewise.cadence_looks import interim_twin

    if fit["custody"] is None:
        return {"agreement": "not_evaluable"}  # the synthetic level-E fixture has no raw inputs for the twin
    if twin_path.resolve() != twin_path or not twin_path.is_file() or sha256_file(twin_path) != doc["fit"]["twin"]["sha256"]:
        return {"agreement": "not_evaluable"}
    wrapper = ROOT / M.TWIN_WRAPPER_PATH
    pinned = {rel: sha for _, rel, sha in M.code_refs(doc)}
    if wrapper.resolve() != wrapper or not wrapper.is_file() or sha256_file(wrapper) != pinned.get(M.TWIN_WRAPPER_PATH):
        return {"agreement": "not_evaluable"}
    return interim_twin.run(twin_path, wrapper=wrapper, manifest=a.manifest, manifest_sha=manifest_sha, commit=commit,
                            stage1_path=a.stage1, stage1_sha=a.stage1_sha256, custody=a.custody, overrides=overrides,
                            restricted=restricted, coefficient_sha=coefficient_sha, deadline=deadline,
                            stage1=stage1, coefficients=coefficients, fit=fit, step3=step3)


def finish_stage2(a, stage1, prepared, doc, commit, manifest_sha, restricted, public, public_schema,
                  coefficients_schema, sdir_of, twin_path, *, ledger_gate=None, overrides=(), deadline=None):
    """The fit, Step 3, coefficient commitment, and comparison share the same reservation."""
    from joulewise.cadence_looks import step3_roster as S3

    if sdir_of is None:
        energy, custody = M.strict_json(layout_of(doc).read("input_level_e")), None   # synthetic level E only
    else:
        # Even energy-blind scans of trace bytes run under the reservation and descriptor redirection.
        span_times = custody_check(stage1, sdir_of)
        problems = S3.custody_problems(stage1, sdir_of)
        if problems:
            raise F.LookInputError("; ".join(problems))
        energy, files = read_segment_energy(stage1, sdir_of, gpu_max_gap_s=gpu_gap_rule(doc), span_times=span_times)
        custody = {"root": str(Path(a.custody).resolve()),
                   "span_dirs": [{"span_id": sid, "path": str(Path(path).resolve())}
                                 for sid, path in overrides],
                   "files": files}
        _bind_override_files(custody, dict(overrides))
    fit = F.stage2(stage1, a.stage1_sha256, energy, code_hashes(), _prepared=prepared)
    fit.update(custody=custody, soak_retries=stage1["soak_retries"], manifest_sha256=manifest_sha,
               allow_draft=ledger_gate is None, ledger_gate=ledger_gate)
    release.write_private(restricted / "fit.json", F.dump(fit))
    entries = S3.entries_from_stage1(stage1, sdir_of) if sdir_of is not None else []
    threshold = next(d["threshold"] for d in doc["decisions"] if d["id"] == "drift_tripwire")
    step3 = S3.run_roster(entries, threshold=threshold)
    if sdir_of is not None:
        step3["custody"] = S3.custody_record(a.custody, a.span_dir, entries, sdir_of, stage1)
        _bind_override_files(step3["custody"], dict(overrides))
        step3_files = {entry["path"]: entry["sha256"] for entry in step3["custody"]["files"]}
        for entry in custody["files"]:
            path = entry["path"]
            if path.endswith("/power_trace.csv") and step3_files.get(path) != entry["sha256"]:
                raise F.LookInputError("the primary fit and Step 3 read different GPU trace bytes")
    release.write_private(restricted / "step3.json", F.dump(step3))
    coefficients = F.write_coefficients(stage1, a.stage1_sha256, fit, manifest_sha, _prepared=prepared)
    if release.schema_check.errors(coefficients, coefficients_schema):
        raise F.LookInputError("the coefficient file violates its pinned schema")
    coefficient_path = restricted / "coefficients.json"
    release.write_private(coefficient_path, F.dump(coefficients))
    coefficient_sha = sha256_file(coefficient_path)
    verdict = fit["qualified_interim_half"]["verdict"]
    drift = step3["tripwire"]["decision"]
    try:
        comparison = run_twin(twin_path, a, stage1, fit, step3, coefficients, doc=doc, commit=commit,
                              manifest_sha=manifest_sha, coefficient_sha=coefficient_sha, restricted=restricted,
                              deadline=deadline, overrides=overrides)
        agreement = comparison["agreement"]
    except Exception:  # RL-180: failure of the independent comparison leaves the primary fit evaluable.
        comparison = {"agreement": "not_evaluable"}
        agreement = comparison["agreement"]
    if sha256_file(coefficient_path) != coefficient_sha:
        raise F.LookInputError("the stored coefficient bytes changed during the twin comparison")
    if agreement == "no":
        from joulewise.cadence_looks import interim_twin

        try:
            comparison["post_no"] = interim_twin.post_no(stage1, fit, energy, comparison)
        except (ArithmeticError, KeyError, TypeError, ValueError):
            comparison["post_no"] = None
    release.write_private(restricted / "twin.json", F.dump(comparison))
    if {child.name for child in restricted.iterdir()} != release.PRIVATE_NAMES:
        raise F.LookInputError("stage 2: unexpected private artifact names")
    release.sync_directory(restricted)
    expected = release.public_record(doc["look_id"], manifest_sha, commit, stage1, a.stage1_sha256, coefficient_sha,
                                     verdict, drift, agreement)
    release.write_public(public, restricted, expected, public_schema, expected=expected)


def stage2_energy_preflight(s1, a):
    """Everything stage 2 can refuse on without energy, checked before the first energy file opens:
    - a stage-1 file made under --allow-draft is refused by a run without it (Mythos r3 N2);
    - the stage-1 file names the manifest this run verified (N2);
    - stage 2's whole module set (the meter decoder, the step 3 file) is imported now and the unpinned-module and
      cached-bytecode checks run on it (N2, N10).
    It reads no roster file: the receipts' synthetic flag (N1) is read after the pin check
    (``synthetic_custody_only``; RL-194 has no read of a roster file before every file equals its pin)."""
    if s1.get("numpy_version") != F.np.__version__:
        raise F.LookInputError("stage 2: numpy version differs from committed stage 1")
    if s1.get("allow_draft") is True and not a.allow_draft:
        raise F.LookInputError("the stage-1 file was made under --allow-draft; a run without it refuses it")
    doc, mpath = _VERIFIED[0]
    if s1.get("manifest_sha256") != sha256_file(mpath):
        raise F.LookInputError("the stage-1 file was made under another manifest")
    # Sol r4 NEW-3: the shared pre-energy check of the stage-1 file (schema, manifest, run mode, exact code at the
    # pins, roster hash), before the reservation
    problems = M.stage1_problems(ROOT, doc, s1, sha256_file(mpath), allow_draft=a.allow_draft)
    if problems:
        raise F.LookInputError("the stage-1 file: " + "; ".join(problems))
    importlib.import_module("joulewise.external.km003c_parse")
    importlib.import_module("joulewise.cadence_looks.step3_energy_ratios")
    importlib.import_module("joulewise.cadence_looks.step3_roster")
    importlib.import_module("joulewise.cadence_looks.interim_twin")
    _guard_loaded(doc)


def synthetic_custody_only(s1, sdir_of):
    """Mythos r3 N1: a stage-1 file marked synthetic opens synthetic custody only. Every span the run opens has a
    runner receipt saying "synthetic": true. Called after the pin check, on the verified bytes."""
    if s1["synthetic"] is True:
        for sp in s1["roster"]["spans"]:
            if _json(sdir_of(sp["span_id"]) / "runner_receipt.json").get("synthetic") is not True:
                raise F.LookInputError("--allow-draft opens synthetic custody only: a span's receipt is not synthetic")


def _guard_loaded(doc):
    """Refuse on any loaded repository module the manifest does not pin (M.unpinned_loaded_modules), or one whose
    code did not come from its source under this run's fresh pycache prefix (Mythos N10)."""
    loose = M.unpinned_loaded_modules(doc, ROOT)
    if loose:
        raise F.LookInputError(f"modules loaded but not pinned: {sorted(loose)}")
    _check_sources()


def _check_sources():
    """No loaded repository module may have a bytecode file at its cache path. This run writes none (-B, and a
    fresh empty prefix), so a file there is one Python may have run in place of the pinned source."""
    name = _cached_source()
    if name is not None:
        raise F.LookInputError(f"a repository module may have run from cached bytecode: {name}")


def _cached_source():
    """The file name of a loaded repository module that may have run from cached bytecode, or None."""
    root = str(ROOT.resolve())
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if not f or not str(Path(f).resolve()).startswith(root):
            continue
        cached = getattr(mod, "__cached__", None)
        if f.endswith((".pyc", ".pyo")) or (cached and os.path.exists(cached)):
            return Path(f).name
    return None


def finish_stage1(a, doc, out):
    """The rest of the stage-1 entry point: the shared check of stage 1's own file, then stage 1's only writes, both
    at fixed names in the look's private directory, and only now (a refused run has created no file; each is created
    once and never replaced). After a custody stage 1's protected reads a failed check is a breach: the preflight
    owns every refusal that needs no protected file."""
    probs = M.stage1_problems(ROOT, doc, out, sha256_file(a.manifest), allow_draft=a.allow_draft)
    if probs:
        raise owned_refusal("stage 1's own output: " + "; ".join(probs))
    if getattr(a, "look_input_bytes", None) is not None:
        a.layout.create("level_r", a.look_input_bytes)
    return a.layout.create("stage1", F.dump(out))


def owned_refusal(message):
    """A check the preflight owns: a refusal before stage 1's first protected open, a PreflightBreach after it."""
    return PreflightBreach(message) if _PHASE["protected"] else F.LookInputError(message)


def _refusal_text(exc):
    return "; ".join(exc.problems) if isinstance(exc, M.ManifestError) else str(exc)


def main(argv=None, *, keep_redirected=False):
    # allow_abbrev=False: no former path option is taken as an abbreviation of one that remains
    ap = argparse.ArgumentParser(description="The interim look's two stages (RL-166 Q8). No command takes a path: "
                                             "the manifest registers the look's root, and every file is a fixed name "
                                             "under it (manifest.LookLayout).", allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("host-id", help="print this machine's RL-184 execution host token", allow_abbrev=False)
    sub.add_parser("post-no-maxima", help="print the two private RL-184 prediction differences", allow_abbrev=False)
    p1 = sub.add_parser("stage1", allow_abbrev=False)
    p1.add_argument("--level-r", action="store_true",
                    help="with --allow-draft only: read input_level_r.json in place of custody")
    p1.add_argument("--stage-archives", action="store_true",
                    help="RL-174 D.3: expand each roster span's pulled archive under the look's archives directory "
                         "into a private directory, and read the span from there")
    p1.add_argument("--ruled-exclusion", action="append", metavar="LEG_KEY=RULE=RL-n",
                    help="RL-173 E.1 item 4: a leg the research lead excluded by name after a stage-2 refusal; the "
                         "committed LOOKS.json row's stage1_superseded must name it")
    p2 = sub.add_parser("stage2", allow_abbrev=False)
    p2.add_argument("--stage1-sha256", required=True)
    p2.add_argument("--level-e", action="store_true",
                    help="with --allow-draft only: read input_level_e.json in place of custody")
    for p in (p1, p2):
        p.add_argument("--allow-draft", action="store_true", help="synthetic runs: accept a draft manifest")
    a = ap.parse_args(argv)
    if a.cmd == "stage1" and a.stage_archives and a.level_r:
        ap.error("--stage-archives reads custody; --level-r does not")
    _PHASE["protected"] = False                 # set by read_protected at stage 1's first protected read
    try:
        if a.cmd == "host-id":
            print(M.execution_host())
            return 0
        if a.cmd == "post-no-maxima":
            layout = layout_of(M.load_json(manifest_path()))
            path = layout.look / "RESTRICTED" / "twin.json"
            if not path.is_file() or path.is_symlink():
                raise F.LookInputError("post-no: the registered private twin.json is required")
            comparison = _json(path)
            diagnostic = comparison.get("post_no")
            if comparison.get("agreement") != "no" or not isinstance(diagnostic, dict):
                raise F.LookInputError("post-no: the private diagnostics are unavailable")
            maxima = [diagnostic.get(key) for key in ("fitted_values_max_relative_difference",
                                                       "predicted_onsets_max_relative_difference")]
            if any(type(value) not in (int, float) or not math.isfinite(value) or value < 0 for value in maxima):
                raise F.LookInputError("post-no: both private maxima must be evaluable")
            sys.stdout.buffer.write(release.dump(maxima))
            return 0
        # A committed run reads its public records from origin/main only, fetched now (audit 3, rule P3)
        a.ledger_ref = None if a.allow_draft else "origin/main"
        if not a.allow_draft:
            M.fetch_public(ROOT)
        # FIRST, before any input is opened: the running code must be the pinned code (Mythos cold seat 3; Sol 9)
        a.manifest = str(manifest_path())
        doc = M.verify_pins(a.manifest, ROOT, allow_draft=a.allow_draft, running=RUNNING, ledger_ref=a.ledger_ref)
        if doc["look_id"] != F.LOOK_ID:
            raise F.LookInputError(f"this look runner executes only {F.LOOK_ID}")
        _VERIFIED[:] = [(doc, a.manifest)]
        if a.cmd == "stage2":
            return cmd_stage2(a, keep_redirected=keep_redirected)
        sha = finish_stage1(a, doc, cmd_stage1(a))
    except ContentRefusal as exc:           # stage 1's protected phase: a condition on protected content
        print(f"REFUSED {exc}", file=sys.stderr)
        return 2
    except (F.LookInputError, M.ManifestError, PINS.PinRefusal) as exc:
        if _PHASE["protected"] or isinstance(exc, PreflightBreach):
            # C1: after stage 1's first protected open the only refusals are POST_OPEN_REASONS; anything else is a
            # check the preflight should have made, reported as a fault and never as a refusal
            print(f"FAILED preflight breach: {type(exc).__name__}: {_refusal_text(exc)}", file=sys.stderr)
            return 2
        prefix = "custody pins: " if isinstance(exc, PINS.PinRefusal) else ""
        print(f"REFUSED {prefix}{_refusal_text(exc)}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - no message: it could carry a value
        tb = exc.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        # F2: after stage 1's first protected open an unexpected failure (an I/O error included) is a breach of the
        # preflight; its type and place only, never its message
        kind = "FAILED preflight breach:" if _PHASE["protected"] else "FAILED"
        print(f"{kind} {type(exc).__name__} at {os.path.basename(tb.tb_frame.f_code.co_filename)}:{tb.tb_lineno}",
              file=sys.stderr)
        return 2
    print(f"wrote {M.LOOK_FILES['stage1']} sha256={sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main(keep_redirected=True))
