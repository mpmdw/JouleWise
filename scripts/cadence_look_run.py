#!/usr/bin/env python3
"""The interim look's two-stage CLI (RL-166 Q1, Q2, Q8; the analyst seat runs it).

    host-id
    stage1 --out STAGE1.json  (--input LOOK_INPUT.json
                               | --roster ROSTER.json --custody ROOT --rules-3-4 VERDICTS.json
                                 [--span-dir SPAN_ID=PATH ...] [--write-input LOOK_INPUT.json])
           --manifest MANIFEST.json [--allow-draft]   (both stages; checked first, before any input opens)
    stage2 --manifest MANIFEST.json --stage1 STAGE1.json --stage1-sha256 HEX
           --custody ROOT [--span-dir SPAN_ID=PATH ...]


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
import hashlib
import importlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
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


def _stamp(out, a):
    """Provenance and run mode on a stage output: the manifest verify_pins checked, and allow_draft. Before writing,
    refuse if any repository module loaded in this process is not pinned (manifest.unpinned_loaded_modules)."""
    doc, mpath = _VERIFIED[0]
    _guard_loaded(doc)
    out["manifest_sha256"] = sha256_file(mpath)
    out["allow_draft"] = bool(a.allow_draft)
    # what satisfied the committed-ledger gate (Sol NEW-2 / Mythos N3); none under --allow-draft
    out["ledger_gate"] = None if a.allow_draft else M.ledger_gate(ROOT, getattr(a, "ledger_ref", None))
    return out


def _jsonl(path):
    with open(path) as f:
        return [M.strict_json(x) for x in f if x.strip()]


def _json(path):
    with open(path) as f:
        return M.strict_json(f.read())


def write_canonical(path, obj):
    data = F.dump(obj)
    with open(path, "wb") as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()


def span_dirs(custody, pairs):
    m = {}
    for p in pairs or []:
        sid, _, path = p.partition("=")
        if not sid or not path:
            raise F.LookInputError("--span-dir wants SPAN_ID=PATH")
        m[sid] = Path(path)
    return lambda sid: m.get(sid, Path(custody) / sid)


def stage_archive(span_id, archive, manifest, marker, staging_root):
    """RL-174 D.3: expand a pulled, decrypted #804 archive; hash bytes, decode no measurement.

    The existing marker binds the exact SHA256SUMS bytes (``hash  ./relative/path``) and the archive.
    Publish a new span directory only after all files match. The supplied marker is the upstream
    custody handoff; this offline step neither contacts the provider nor decrypts ciphertext.
    """
    import tarfile
    from pathlib import PurePosixPath

    def refuse(reason):
        raise F.LookInputError(f"staging: {span_id}: {reason}")

    def relative(name):
        p = PurePosixPath(name)
        if not name or p.is_absolute() or any(x in ("", ".", "..") for x in name.split("/")):
            refuse("unsafe archive or manifest path")
        return p

    if not isinstance(span_id, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", span_id):
        refuse("invalid span id")
    try:
        mraw, kraw = Path(manifest).read_bytes(), Path(marker).read_bytes()
        mark = json.loads(kraw)
        msha = hashlib.sha256(mraw).hexdigest()
        if (mark.get("schema") != "joulewise.span_offload_marker.v1"
                or mark.get("provider_confirmed") is not True or mark.get("manifest_sha256") != msha):
            refuse("manifest does not match the verified marker")
        top = mark.get("span_name")
        if not isinstance(top, str) or len(relative(top).parts) != 1 or top != span_id:
            refuse("marker span name differs from the roster span")
        expected = {}
        for line in mraw.decode("utf-8").splitlines():
            match = re.fullmatch(r"([0-9a-f]{64})  \./(.+)", line)
            if not match:
                refuse("invalid per-file manifest")
            digest, name = match.groups()
            relative(name)
            if name in expected:
                refuse("duplicate manifest file")
            expected[name] = digest
        if not expected or mark.get("manifest_files") != len(expected):
            refuse("manifest file count differs from the marker")
        root = Path(staging_root)
        root.mkdir(parents=True, exist_ok=True)
        destination = root / span_id
        if destination.exists() or destination.is_symlink():
            refuse("staged span already exists; use a fresh staging root")
        with tempfile.TemporaryDirectory(prefix=".look-stage-", dir=root) as tmp:
            tmp = Path(tmp)
            # Hash the same open archive later expanded. No time-field reader sees compressed bytes.
            with open(archive, "rb") as source:
                archive_sha = hashlib.file_digest(source, "sha256").hexdigest()
                if archive_sha != mark.get("archive_sha256"):
                    refuse("archive does not match the marker")
                source.seek(0)
                with tarfile.open(fileobj=source, mode="r:*") as tar:
                    seen, files = set(), set()
                    for member in tar:
                        parts = relative(member.name).parts
                        if parts[0] != top or member.name in seen:
                            refuse("unexpected or duplicate archive member")
                        seen.add(member.name)
                        path = tmp.joinpath(*parts)
                        if member.isdir():
                            path.mkdir(parents=True, exist_ok=True)
                        elif member.isfile():
                            name = "/".join(parts[1:])
                            if name not in expected:
                                refuse("archive file absent from the manifest")
                            path.parent.mkdir(parents=True, exist_ok=True)
                            with tar.extractfile(member) as src, path.open("xb") as dst:
                                shutil.copyfileobj(src, dst)
                            files.add(name)
                        else:
                            refuse("archive member is not a regular file or directory")
            if files != set(expected):
                refuse("archive file set differs from the manifest")
            for name, digest in expected.items():
                if sha256_file(tmp / top / name) != digest:
                    refuse("staged file sha256 differs from the manifest")
            (tmp / top).rename(destination)
        return {"span_id": span_id, "archive_sha256": archive_sha, "manifest_sha256": msha,
                "marker_sha256": hashlib.sha256(kraw).hexdigest(), "files_verified": len(expected)}
    except (OSError, ValueError, KeyError, TypeError, tarfile.TarError, UnicodeError) as exc:
        if isinstance(exc, F.LookInputError):
            raise
        refuse(f"cannot verify or expand archive ({type(exc).__name__})")


def stage_custody(a, roster):
    """Optional stage-1 plan: [{span_id, archive, manifest, marker}]. Paths are local pulled copies."""
    if not getattr(a, "stage_archives", None):
        return []
    plan = _json(a.stage_archives)
    allowed = {span["span_id"] for span in roster}
    seen = {p.partition("=")[0] for p in a.span_dir or []}
    records = []
    if not isinstance(plan, list) or not plan:
        raise F.LookInputError("staging plan: expected a nonempty list")
    for entry in plan:
        if not isinstance(entry, dict) or set(entry) != {"span_id", "archive", "manifest", "marker"}:
            raise F.LookInputError("staging plan: expected span_id, archive, manifest and marker")
        sid = entry["span_id"]
        if sid not in allowed or sid in seen:
            raise F.LookInputError("staging plan: duplicate, overridden or unrostered span")
        seen.add(sid)
        records.append(stage_archive(sid, entry["archive"], entry["manifest"], entry["marker"], a.staging_root))
        a.span_dir = list(a.span_dir or []) + [f"{sid}={Path(a.staging_root) / sid}"]
    return records


# =============================================================================================== stage-1 reader
_RICH_TS = re.compile(rb'"timestamp_s":\s*(-?[0-9][0-9.eE+-]*)')
_RICH_EL = re.compile(rb'"elapsed_ns":\s*([0-9]+)')
_PL_TP = re.compile(rb"<key>thermal_pressure</key>\s*<string>([^<]*)</string>")
_PL_EL = re.compile(rb"<key>elapsed_ns</key>\s*<integer>([0-9]+)</integer>")


def native_states(bundle, lo, hi):
    """[(row end epoch, state)] for rows ending in [lo, hi]. Pattern extraction only (module docstring)."""
    ends = []
    with open(bundle / "rich_telemetry.jsonl", "rb") as f:
        for line in f:
            if not line.strip():
                continue
            m, e = _RICH_TS.search(line), _RICH_EL.search(line)
            if not m or not e:
                raise F.LookInputError("rich_telemetry: a row without timestamp_s or elapsed_ns")
            ends.append((float(m.group(1)), int(e.group(1))))
            del line
    with open(bundle / "raw/powermetrics.plist", "rb") as f:
        frames = [p for p in f.read().split(b"\0") if p.strip()]
    if not (len(frames) == len(ends) or len(frames) == len(ends) + 1):
        raise F.LookInputError("plist/rich frame count mismatch")
    out = []
    for i, (end, el) in enumerate(ends):
        if not (lo <= end <= hi):
            continue
        fr = frames[i]
        me = _PL_EL.search(fr)
        if not me or int(me.group(1)) != el:
            raise F.LookInputError("plist/rich elapsed mismatch")
        mt = _PL_TP.search(fr)
        out.append({"t_end_s": end, "state": mt.group(1).decode() if mt else None})
    del frames
    return out


def journal_readings(bundle, lo, hi, fan_keys):
    out = []
    for r in _jsonl(bundle / "outputs/align_thermal.jsonl"):
        if r.get("kind") != "reading" or r.get("error"):
            continue
        t = r["finished"]["wall_ns"] / 1e9
        if not (lo <= t <= hi):
            continue
        v = r.get("values") or {}
        st = v.get("status") or {}
        sen = v.get("sensors") or {}
        pmo = st.get("pm_observed_ns")
        fresh = type(pmo) is int and (r["started"]["monotonic_ns"] - pmo) <= PM_FRESH_S * 1e9
        fans = [sen.get(k) for k in fan_keys]
        fan = (sum(float(x) for x in fans) / len(fans)) if fans and all(x is not None for x in fans) else None  # R-7
        lvl = st.get("os_level")
        out.append({"t_s": t, "os_level": lvl if type(lvl) is int else None,
                    "pm_state": st.get("pm_state") if isinstance(st.get("pm_state"), str) else None,
                    "pm_fresh": bool(fresh),
                    "tf08_c": None if sen.get("Tf08") is None else float(sen["Tf08"]), "fan_rpm": fan,
                    "tv0h_c": None if sen.get("TV0h") is None else float(sen["TV0h"])})
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
                toks.append((int(md["index"]), float(e["timestamp_s"])))
            del e
    toks.sort()
    if [i for i, _ in toks] != list(range(len(toks))):
        raise F.LookInputError("events: token indices not contiguous")
    t = [s for _, s in toks]
    if any(b < a for a, b in zip(t, t[1:])):
        raise F.LookInputError("events: token stamps not monotone")
    return t


def build_turn(bundle, result, fan_keys):
    turns = _jsonl(bundle / "outputs/align_turns.jsonl")
    if len(turns) != 1:
        raise F.LookInputError("align_turns: not one turn")
    tr = turns[0]
    ts = float(tr["start_stamp"]["epoch_s"])
    n_out = len(tr["generation"]["output_token_ids"])          # LENGTH only
    P = tr["generation"].get("prefill_tokens", result.get("prefill_tokens"))
    del turns, tr
    tok = token_stamps(bundle)
    if len(tok) != n_out or not tok:
        raise F.LookInputError("token count differs from the output length")
    N = len(tok)
    segs = [{"seg": 0, "kind": "prefill", "n_tokens": int(P), "edge_lo": None, "edge_hi": None, "tok_first": None,
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
    return {"prefill_tokens": int(P), "decode_tokens": N, "turn_start_s": ts, "first_token_s": tok[0],
            "last_token_s": tok[-1], "segments": segs, "prefix_tails": tails,
            "journal": journal_readings(bundle, ts - JOURNAL_PRE_S, tok[-1] + JOURNAL_POST_S, fan_keys),
            "native_pm": native_states(bundle, ts, tok[-1])}


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
    except TF.TimeFieldError as exc:
        raise F.LookInputError(f"custody: {exc}") from None
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
    except TF.CompressedCustody as exc:               # Mythos r5 N8: as a compressed stream, the look refuses
        raise F.LookInputError(f"GPU rail: {leg_key}: {exc}") from None
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


def read_span(sdir, entry, rules34, fan_keys, ruled=None):
    """(span, legs) of one roster span, in level-R shape. Opens no energy value: power_trace.csv and the meter
    streams only through the time reader (RL-173 E.1). ``ruled``: {leg_key: (rule, ruling)}, the research lead's
    named exclusions for a stage 1 run once more (RL-173 E.1 item 4)."""
    ruled = ruled or {}
    receipt = _json(sdir / "runner_receipt.json")
    epoch_s = receipt["started"]["epoch_s"]
    day = F.span_day(epoch_s, entry["t0_local_date"], entry["span_id"])
    files = {"runner_receipt.json": TF.file_sha256(sdir / "runner_receipt.json")}
    sm, sm_why = span_meter(sdir)                 # preserves the field-only compressed-custody refusal
    # A committed verdict hashes the decision file, not the source copy. Replay the same blind rules on
    # this custody before admission; a stale true can never override a current failure. Committed false
    # decisions remain exclusions. The later trace clauses can only exclude further.
    selected = I34.keys(_json(ROOT / I34.RUNTIME_CONFIG)["sensors"])
    replayed, _, _ = I34.judge_span(sdir, entry["span_id"], selected)
    try:
        soak = float(_json(sdir / "soak/soak_reference.json")["sensors_c"]["TV0h"])
    except (OSError, KeyError, TypeError, ValueError):
        soak = None
    power = "high_power" if entry["block_id"].startswith("hp-") else "automatic"
    span = {"span_id": entry["span_id"], "block_id": entry["block_id"],
            "phase": "extension" if entry["role"] == "describe" else "development", "role": entry["role"],
            "power_mode": power, "t0_epoch_s": float(epoch_s),
            "t0_local_date": day, "soak_reference_tv0h_c": soak, "marks": [],
            "meter_offsets_ns": dict(zip(("header", "end"), meter_offsets(sm) if sm else (None, None))),
            "soak_receipt": I34.soak_fields(receipt),
            "custody": {"files_sha256": files, "meter_time_sha256": sm.digest() if sm else None,
                        "meter_streams": sm.summary() if sm else [], "meter_unreadable": sm_why}}
    legs, marks, suppliers = [], set(), set()
    for leg_id in receipt["roster"]:
        key = f"{entry['span_id']}/{leg_id}"
        ldir = sdir / "legs" / leg_id
        v34 = rules34.get(key)
        if v34 is None:
            raise F.LookInputError("rules 3 and 4: no verdict for a roster leg")
        if not (ldir / "leg_record.json").is_file():          # the span stopped before this leg (R-21)
            legs.append({"leg_key": key, "span_id": entry["span_id"], "leg_id": leg_id, "leg_type": "A",
                         "cell_prompt_tokens": None, "g0_role": None,
                         "inclusion": {r: False for r in F.RULES}, "turn": None, "trace_holes": None,
                         "ruled_exclusion": None})
            continue
        rec = _json(ldir / "leg_record.json")
        files[f"legs/{leg_id}/leg_record.json"] = TF.file_sha256(ldir / "leg_record.json")
        spec, attempts, result = rec["spec"], rec["attempts"], rec.get("result") or {}
        summ = _json(ldir / "leg_summary.json") if (ldir / "leg_summary.json").is_file() else {}
        ref = summ.get("span_reference")
        if isinstance(ref, dict):
            if isinstance(ref.get("leg_id"), str):
                suppliers.add(ref["leg_id"])
            if ref.get("redone"):
                marks.add("reference from a redo")
            if ref.get("excluded"):
                marks.add("reference from an excluded leg")
        leg_type = "T" if spec.get("leg_type") == "T" else "A"          # R-21: spec.leg_type only
        inc = {"ran_to_cap": result.get("leg_status") == "complete" and result.get("decode_cap_reached") is True,
               "g0_released": result.get("g0_released") is True,
               "sidecar_coverage": v34["sidecar_coverage"] is True, "km003c_clean": v34["km003c_clean"] is True,
               "not_a_contaminated_attempt": bool(attempts) and not attempts[-1].get("contaminated"),
               "block_power_mode": _mode(result) == MODE_BY_POWER[power]}
        if leg_type == "A":                     # type-T runtime is never read or rejudged at this look
            for rule in I34.VERDICT_KEYS:
                inc[rule] = inc[rule] and replayed[key][rule]
            if entry["role"] == "fit" and sm is None:   # RL-174 A.4: every fit leg, even without a turn
                inc["km003c_clean"] = False
        turn = None
        bundle = M.runtime_bundle(sdir, leg_id, rec)
        if bundle is not None:
            try:
                turn = build_turn(bundle, result, fan_keys)
            except M.ManifestError:
                raise
            except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
                # A G0 timeout (cadence_leg.py: a bundle and no turn) is a ruled exclusion (rules 1 and 2), not a
                # refusal: a leg the six verdicts already exclude carries no turn. An included leg refuses.
                if all(inc.values()):
                    raise F.LookInputError(f"an included leg's bundle has no readable turn ({type(exc).__name__})")
                turn = None
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
        legs.append({"leg_key": key, "span_id": entry["span_id"], "leg_id": leg_id, "leg_type": leg_type,
                     "cell_prompt_tokens": int(spec["prefill_tokens"]), "g0_role": spec.get("g0_role"),
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


def read_look_input(roster, sdir_of, rules34, fan_keys=FAN_KEYS, ruled=None):
    """Level R from the custody copy. `synthetic` is true only when every span's runner receipt says so
    (the synthetic generator writes it; a real runner never does)."""
    if not isinstance(roster, list):                # one shape: validate --roster-out's JSON list
        raise F.LookInputError("roster: not a list of spans")
    validate_runtime_bundles(roster, sdir_of)
    spans, legs, synth = [], [], []
    ruled = dict(ruled or {})
    for entry in roster:
        sdir = sdir_of(entry["span_id"])
        synth.append(_json(sdir / "runner_receipt.json").get("synthetic") is True)
        s, ls = read_span(sdir, entry, rules34, fan_keys, ruled)
        spans.append(s)
        legs += ls
    if ruled:
        raise F.LookInputError(f"a ruled exclusion names a leg with no record on the roster: {sorted(ruled)[0]}")
    return {"schema": F.INPUT_SCHEMA, "look_id": F.LOOK_ID, "synthetic": bool(synth) and all(synth),
            "spans": spans, "legs": legs}


_WRITER_PHASES = {"tokenize", "generation_setup", "prefill", "decode", "align_thermal_gate", "align_thermal_hold",
                  "align_context_check", "align_context_stop_observation", "align_g0_unreleased_stop_observation"}


def validate_runtime_bundles(roster, sdir_of):
    for span in roster:
        receipt, bundles = M.check_runtime_bundles(sdir_of(span["span_id"]))
        try:
            I34.check_writer_receipt(receipt)
        except ValueError as exc:
            raise F.LookInputError(str(exc)) from None
        for bundle in bundles:
            events = bundle / "events.jsonl"
            if not events.is_file():
                continue  # an uncompleted bundle may have no events
            for event in _jsonl(events):
                kind = event.get("event_type")
                if "timestamp_s" in event or kind in ("token", "phase_start", "phase_end"):
                    stamp = event.get("timestamp_s")
                    if type(stamp) not in (int, float) or not math.isfinite(stamp):
                        raise F.LookInputError("events: invalid writer timestamp")
                if not isinstance(kind, str) or not kind.startswith("phase_"):
                    continue
                phase, metadata = event.get("phase"), event.get("metadata")
                if (kind not in ("phase_start", "phase_end") or not isinstance(phase, str)
                        or (phase not in _WRITER_PHASES
                            and not re.fullmatch(r"align_tool_(0|[1-9][0-9]*)_(0|[1-9][0-9]*)", phase))
                        or (metadata is not None and not isinstance(metadata, dict))):
                    raise F.LookInputError("events: invalid writer phase")


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
            raise F.LookInputError(f"stage-2 preflight: {L['leg_key']} has no power_trace.csv")
        if not TF.span_streams(sdir):
            raise F.LookInputError(f"stage-2 preflight: {L['leg_key']}'s span has no meter stream")
        th = L.get("trace_holes")
        if not th or th["gpu_rail"]["excluded"] or th["dc_in"]["excluded"]:
            raise F.LookInputError(f"stage-2 preflight: {L['leg_key']} is in the energy fit without both trace clauses")


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


def superseded_source(a, row):
    """Authenticate the kept stage-1 and level-R files before a ruled rerun reads custody."""
    if not (getattr(a, "superseded_stage1", None) and getattr(a, "superseded_input", None)):
        raise F.LookInputError("a ruled rerun needs --superseded-stage1 and --superseded-input (the kept level R)")
    last = row["stage1_superseded"][-1]
    raw = Path(a.superseded_stage1).read_bytes()
    if hashlib.sha256(raw).hexdigest() != last["stage1_sha256"]:
        raise F.LookInputError("the kept stage-1 file is not the superseded commitment")
    previous = json.loads(raw)
    if previous.get("manifest_sha256") != sha256_file(a.manifest):
        raise F.LookInputError("a stage 1 run once more takes the replaced commitment's manifest unchanged")
    raw = Path(a.superseded_input).read_bytes()
    if hashlib.sha256(raw).hexdigest() != previous.get("input_sha256"):
        raise F.LookInputError("the kept level-R file is not the superseded stage-1 input")
    old_input = json.loads(raw)
    old_ruled = {leg["leg_key"]: (leg["ruled_exclusion"]["rule"], leg["ruled_exclusion"]["ruling"])
                 for leg in old_input.get("legs", []) if leg.get("ruled_exclusion")}
    return old_input, old_ruled


def cmd_stage1(a):
    staging = []
    if a.input and not a.allow_draft:
        raise F.LookInputError("--input (level R) runs only with --allow-draft; a committed look reads custody")
    if a.input:
        with open(a.input, "rb") as f:
            raw = f.read()
        look_input = json.loads(raw)
        input_sha = hashlib.sha256(raw).hexdigest()
        extra = {"roster_sha256": input_sha}        # a level-R run has no roster: its input file stands in
    else:
        ruled = ruled_exclusions(a.ruled_exclusion)
        if not a.allow_draft:
            # Mythos r3 N8: the committed ledger names this manifest, roster and verdict file before custody opens;
            # RL-173 E.1 item 4: a stage 1 run once more names the research lead's ruled exclusions, nothing else
            row = M.require_inputs_committed(ROOT, F.LOOK_ID, sha256_file(a.manifest), roster_sha256=sha256_file(a.roster),
                                       verdicts_sha256=sha256_file(a.rules_3_4), ledger_ref=a.ledger_ref,
                                       ruled_exclusions={k: list(v) for k, v in ruled.items()})
        roster = _json(a.roster)
        staging = stage_custody(a, roster)
        rules34 = _json(a.rules_3_4)
        if ruled and not a.allow_draft:
            old_input, old_ruled = superseded_source(a, row)
            before = read_look_input(roster, span_dirs(a.custody, a.span_dir), rules34, ruled=old_ruled)
            if F.dump(before) != F.dump(old_input):
                raise F.LookInputError("a ruled rerun changes the superseded level-R source; only the named exclusions may change")
        look_input = read_look_input(roster, span_dirs(a.custody, a.span_dir), rules34, ruled=ruled)
        if ruled and not a.allow_draft:
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
                raise F.LookInputError("a ruled rerun changes sources beyond the named exclusions")
        data = F.dump(look_input)
        input_sha = hashlib.sha256(data).hexdigest()
        if a.write_input:
            with open(a.write_input, "wb") as f:
                f.write(data)
        extra = {"roster_sha256": sha256_file(a.roster), "rules_3_4_sha256": sha256_file(a.rules_3_4)}
    if a.allow_draft and look_input.get("synthetic") is not True:
        raise F.LookInputError("--allow-draft runs on synthetic input only (Mythos N2)")
    out = F.stage1(look_input, input_sha, code_hashes())    # RL-172a's soak-retry print is level R's (F.stage1)
    out["staging"] = staging
    if not a.input:
        stage2_preflight(out, span_dirs(a.custody, a.span_dir))
    if extra:
        out["code_sha256"].update({f"input:{k}": v for k, v in extra.items()})
    return _stamp(out, a)


def cmd_stage2(a, *, keep_redirected=False):
    with open(a.stage1, "rb") as f:
        raw = f.read()
    if hashlib.sha256(raw).hexdigest() != a.stage1_sha256:
        raise F.LookInputError("stage 2: the stage-1 file does not match --stage1-sha256")
    s1 = json.loads(raw)
    if F.dump(s1) != raw:
        raise F.LookInputError("stage 2: the stage-1 file is not in canonical form")
    if a.allow_draft and s1.get("synthetic") is not True:
        raise F.LookInputError("--allow-draft runs on synthetic input only (Mythos N2)")
    if a.energy and not a.allow_draft:
        raise F.LookInputError("--energy (level E) runs only with --allow-draft; a committed look reads custody")
    # committed: the repository's LOOKS.json row names this stage-1 file's sha256 (Mythos cold seat 8; N1), before any
    # energy opens. A caller-named ledger is accepted for synthetic (--allow-draft) runs only.
    if a.looks and not a.allow_draft:
        raise F.LookInputError("--looks names a ledger other than the repository's; only with --allow-draft")
    doc, manifest_path = _VERIFIED[0]
    if a.allow_draft:
        row = draft_ledger_check(_json(a.looks) if a.looks else _json(ROOT / M.LOOK_LEDGER_PATH), a.stage1_sha256)
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
    validate_execution_row(row, s1, a.custody)
    twin_path = require_twin_runner(doc)
    try:
        restricted, public = release.destinations(ROOT, row)
    except (OSError, ValueError) as exc:
        raise F.LookInputError(str(exc)) from None
    overrides = stage2_overrides(a.span_dir, s1)
    sdir_of = span_dirs(a.custody, (f"{sid}={path}" for sid, path in overrides)) if a.custody else None
    if sdir_of is not None:
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


def validate_execution_row(row, stage1, custody):
    host = row.get("execution_host")
    if not host:
        raise F.LookInputError("stage 2: register the execution_host before reservation")
    if host != M.execution_host():
        raise F.LookInputError("stage 2: execution_host does not match this host")
    if not row.get("custody_root") or not row.get("public_root"):
        raise F.LookInputError("stage 2: register both look roots in the ledger")
    if custody is not None and Path(custody).resolve() != Path(row["custody_root"]):
        raise F.LookInputError("stage 2: --custody differs from the registered custody root")
    holds = M.STAGE2_HOLD_FLAGS["interim"]
    raised = {flag for flag in holds if stage1[flag.split(".")[0]].get(flag.split(".")[1]) is True}
    if raised != set(row.get("holds_cleared", {})):
        raise F.LookInputError("stage 2: the committed stage-1 flags and ledger clearing rulings differ")


def stage2_overrides(pairs, stage1):
    registered = {span["span_id"] for span in stage1["roster"]["spans"]}
    overrides = {}
    for pair in pairs:
        sid, separator, location = pair.partition("=")
        if not separator or not location or sid not in registered or sid in overrides:
            raise F.LookInputError("stage 2: each span override must name a distinct roster span and directory")
        overrides[sid] = Path(location).resolve()
    if len(set(overrides.values())) != len(overrides):
        raise F.LookInputError("stage 2: span overrides must identify distinct directories")
    return tuple(sorted(overrides.items()))


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
    return interim_twin.run(twin_path, manifest=a.manifest, manifest_sha=manifest_sha, commit=commit,
                            stage1_path=a.stage1, stage1_sha=a.stage1_sha256, custody=a.custody, overrides=overrides,
                            restricted=restricted, coefficient_sha=coefficient_sha, deadline=deadline,
                            stage1=stage1, coefficients=coefficients, fit=fit, step3=step3)


def finish_stage2(a, stage1, prepared, doc, commit, manifest_sha, restricted, public, public_schema,
                  coefficients_schema, sdir_of, twin_path, *, ledger_gate=None, overrides=(), deadline=None):
    """The fit, Step 3, coefficient commitment, and comparison share the same reservation."""
    from joulewise.cadence_looks import step3_roster as S3

    if sdir_of is None:
        energy, custody = _json(a.energy), None   # synthetic level E only
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
    comparison = run_twin(twin_path, a, stage1, fit, step3, coefficients, doc=doc, commit=commit,
                          manifest_sha=manifest_sha, coefficient_sha=coefficient_sha, restricted=restricted,
                          deadline=deadline, overrides=overrides)
    if sha256_file(coefficient_path) != coefficient_sha:
        raise F.LookInputError("the stored coefficient bytes changed during the twin comparison")
    if comparison["agreement"] == "no":
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
                                     verdict, drift, comparison["agreement"])
    release.write_public(public, restricted, expected, public_schema, expected=expected)


def stage2_energy_preflight(s1, a):
    """Everything stage 2 can refuse on without energy, checked before the first energy file opens:
    - a stage-1 file made under --allow-draft is refused by a run without it (Mythos r3 N2);
    - the stage-1 file names the manifest this run verified (N2);
    - under --allow-draft, every span the custody run opens has a runner receipt saying "synthetic": true (N1);
    - stage 2's whole module set (the meter decoder, the step 3 file) is imported now and the unpinned-module and
      cached-bytecode checks run on it (N2, N10)."""
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
    if s1["synthetic"] is True and a.custody:
        sdir_of = span_dirs(a.custody, a.span_dir)
        for sp in s1["roster"]["spans"]:
            if _json(sdir_of(sp["span_id"]) / "runner_receipt.json").get("synthetic") is not True:
                raise F.LookInputError("--allow-draft opens synthetic custody only: a span's receipt is not synthetic")
    importlib.import_module("joulewise.external.km003c_parse")
    importlib.import_module("joulewise.cadence_looks.step3_energy_ratios")
    importlib.import_module("joulewise.cadence_looks.step3_roster")
    importlib.import_module("joulewise.cadence_looks.interim_twin")
    _guard_loaded(doc)


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
    root = str(ROOT.resolve())
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if not f or not str(Path(f).resolve()).startswith(root):
            continue
        cached = getattr(mod, "__cached__", None)
        if f.endswith((".pyc", ".pyo")) or (cached and os.path.exists(cached)):
            raise F.LookInputError(f"a repository module may have run from cached bytecode: {Path(f).name}")


def main(argv=None, *, keep_redirected=False):
    ap = argparse.ArgumentParser(description="The interim look's two stages (RL-166 Q8).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("host-id", help="print this machine's RL-184 execution host token")
    review = sub.add_parser("post-no-maxima", help="print the two private RL-184 prediction differences")
    review.add_argument("--twin", type=Path, required=True)
    p1 = sub.add_parser("stage1")
    p1.add_argument("--out", required=True)
    g = p1.add_mutually_exclusive_group(required=True)
    g.add_argument("--input")
    g.add_argument("--roster")
    p1.add_argument("--custody")
    p1.add_argument("--rules-3-4")
    p1.add_argument("--span-dir", action="append")
    p1.add_argument("--write-input")
    p1.add_argument("--stage-archives", help="RL-174 D.3: JSON list of local span_id/archive/manifest/marker records")
    p1.add_argument("--staging-root", help="fresh raw span destinations for --stage-archives")
    p1.add_argument("--superseded-stage1", help="kept stage-1 file authenticated to the replaced ledger commitment")
    p1.add_argument("--superseded-input", help="kept level-R input authenticated to the superseded stage-1 file")
    p1.add_argument("--ruled-exclusion", action="append", metavar="LEG_KEY=RULE=RL-n",
                    help="RL-173 E.1 item 4: a leg the research lead excluded by name after a stage-2 refusal; the "
                         "committed LOOKS.json row's stage1_superseded must name it")
    p1.add_argument("--ledger-ref", help="the ref HEAD must be an ancestor of (default: upstream, else origin/main)")
    p2 = sub.add_parser("stage2")
    p2.add_argument("--stage1", required=True)
    p2.add_argument("--stage1-sha256", required=True)
    g2 = p2.add_mutually_exclusive_group(required=True)
    g2.add_argument("--energy")
    g2.add_argument("--custody")
    p2.add_argument("--span-dir", action="append", default=[])
    p2.add_argument("--looks", help="with --allow-draft only: a scratch LOOKS.json in place of the repository's")
    p2.add_argument("--ledger-ref", help="the ref HEAD must be an ancestor of (default: upstream, else origin/main)")
    for p in (p1, p2):
        p.add_argument("--manifest", required=True, help="the look manifest whose pins the running code must match")
        p.add_argument("--allow-draft", action="store_true", help="synthetic runs: accept a draft manifest")
    a = ap.parse_args(argv)
    if a.cmd == "stage1" and a.roster and not (a.custody and a.rules_3_4):
        ap.error("--roster needs --custody and --rules-3-4")
    if a.cmd == "stage1" and (bool(a.stage_archives) != bool(a.staging_root) or (a.stage_archives and a.input)):
        ap.error("--stage-archives and --staging-root must be used together with --roster")
    try:
        if a.cmd == "host-id":
            print(M.execution_host())
            return 0
        if a.cmd == "post-no-maxima":
            path = a.twin
            if not path.is_absolute() or path.resolve() != path or path.name != "twin.json" or path.parent.name != "RESTRICTED":
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
        # FIRST, before any input is opened: the running code must be the pinned code (Mythos cold seat 3; Sol 9)
        doc = M.verify_pins(a.manifest, ROOT, allow_draft=a.allow_draft, running=RUNNING,
                            ledger_ref=getattr(a, "ledger_ref", None))
        if doc["look_id"] != F.LOOK_ID:
            raise F.LookInputError(f"this look runner executes only {F.LOOK_ID}")
        _VERIFIED[:] = [(doc, a.manifest)]
        if a.cmd == "stage2":
            return cmd_stage2(a, keep_redirected=keep_redirected)
        out = cmd_stage1(a)
        probs = M.stage1_problems(ROOT, doc, out, sha256_file(a.manifest), allow_draft=a.allow_draft)
        if probs:
            raise F.LookInputError("stage 1's own output: " + "; ".join(probs))
        sha = write_canonical(a.out, out)
    except F.LookInputError as exc:
        print(f"REFUSED {exc}", file=sys.stderr)
        return 2
    except M.ManifestError as exc:
        print(f"REFUSED {'; '.join(exc.problems)}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - no message: it could carry a value
        tb = exc.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        print(f"FAILED {type(exc).__name__} at {os.path.basename(tb.tb_frame.f_code.co_filename)}:{tb.tb_lineno}",
              file=sys.stderr)
        return 2
    print(f"wrote {a.out} sha256={sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main(keep_redirected=True))
