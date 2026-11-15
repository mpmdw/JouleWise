"""Desk-final from the automatic table (RL-172 section (c), on Sol's conditions; RL-149 section 2.8 line 9).

The frozen desk (``joulewise.cadence.desk``) builds a table from whatever leg summaries it finds. Sol's
probe showed that clean status and meter metadata with zero leg rows raise no named stop, that the row
loader skips a missing summary, and that ``build_desk`` takes no expected roster. "The automatic table
builds with no stop" is therefore not finality. ``judge_span`` is: it builds the same table from an
authenticated bundle, against the queue entry's roster and the kit's identities, and writes a
machine-readable verdict that the queue controller reads for the k+2 rule.

A span is desk-final only when all of these hold (RL-172 section (c) items 1-4; Sol):

1. **Roster.** The leg ids, their order and count equal the queue entry's ``legs``; every leg's attempts
   are numbered 1..n, every redo kept as ``legs/<id>/runtime.rejected<k>`` and the accepted attempt as
   ``legs/<id>/runtime``. No leg record is missing or duplicated, and zero leg rows is a stop.
2. **Identities, by hash.** The kit file hashes as the queue pins it; the receipt and the manifest name
   that kit sha256, its campaign and its frozen commit; the manifest names the plan id, queue, span and
   attempt; every leg's seed, band, size and G0 shape are the kit's; every consumer's span reference is
   the roster's first leg (the capture leg) at its accepted attempt, and all consumers carry one
   reference record hash.
3. **An authenticated receipt.** ``BUNDLE_MANIFEST.json`` hashes to the anchor the controller published
   in its per-span record; every file it lists hashes as listed, nothing else is in the bundle, and the
   receipt's hash is the one the manifest names. A negative or error result is also a receipt: a verdict
   is written for every outcome, including a refusal.
4. **Feeds.** ``feeds_proven_stopped`` comes from every feed's own stop proof in the receipt (agents,
   meter, volumes), not from the meter's alone. A missing proof is an integrity stop; a proof that says
   not stopped is the named stop INSTRUMENT_FAULT.

Also: a sampled hand table that disagrees with the automatic table holds the next arm
(HAND_TABLE_DISAGREES); a hand table that RL-172 makes mandatory (a redo, an exclusion, a schema change,
or the lead's seeded draw) keeps the span from being final until it is supplied (HAND_TABLE_DUE).

**Hand gates are kept and gate as they do now** (RL-172 section (c)): the class A smoke hand-read of a
new kit's first span, the L002 and L005 consumer gates, and RL-158 Q1's reference print on every v1.1
span. The desk does not clear them. It prints what each hand check needs and marks it
``hand gate required``.

**Operational finality only.** Inclusion at a look is still RL-166 Q7's interval checks.

**Blinding.** Only ``ALLOWED_BASENAMES`` are ever read, each once (hashed and parsed from the same bytes).
A bundle path outside the bundle layout is refused unread. No energy, power, meter-sample,
powermetrics, transcript or slot file is opened; leg summaries carrying such keys are refused, and the
finished text, summary and verdict are scanned for denied words before anything is written.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import time

from joulewise.cadence import desk
from joulewise.cadence import queue as queuemod
from joulewise.cadence import stops as stopsmod
from joulewise.cadence.stops import evaluate_named_stops

BUNDLE_SCHEMA = "joulewise.cadence_desk_bundle.v1"
VERDICT_SCHEMA = "joulewise.cadence_desk_verdict.v1"
HAND_TABLE_SCHEMA = "joulewise.cadence_hand_table.v1"
RECEIPT_SCHEMA = "joulewise.cadence_span_receipt.v1"      # scripts/cadence_legs_runner.RECEIPT_SCHEMA
RUNNER_KINDS = ("cadence-legs-v1", "cadence-legs-v1.1")
MANIFEST_NAME = "BUNDLE_MANIFEST.json"
RECEIPT_NAME = "runner_receipt.json"
VERDICT_NAME = "desk_verdict.json"
HAND_TABLE_NAME = "hand_table.json"
ALLOWED_BASENAMES = frozenset({MANIFEST_NAME, RECEIPT_NAME, "leg_summary.json", "result.json", "meter.json",
                               HAND_TABLE_NAME})
LEG_ID = r"[A-Za-z0-9][A-Za-z0-9_-]{0,31}"
BUNDLE_PATH_RE = re.compile(rf"{re.escape(RECEIPT_NAME)}|legs/({LEG_ID})/leg_summary\.json|span/result\.json|"
                            rf"span/meter\.json")
HEX64 = re.compile(r"[0-9a-f]{64}")
HEX40 = re.compile(r"[0-9a-f]{40}")
# The runner's production feeds (run_align_r1_smoke.AgentFeed, MeterFeed, VolumeFeed; the mock's FakeFeeds).
EXPECTED_FEEDS = ("agents", "meter", "volumes")
MANIFEST_KEYS = {"schema", "plan_id", "queue_id", "span_id", "attempt", "kit", "receipt", "files"}
MANIFEST_OPTIONAL = {"producer"}
KIT_IDENTITY_KEYS = {"path", "sha256", "campaign_id", "frozen_commit"}
V11_KEYS = {"prefill_tokens", "g0_shape", "g0_role", "span_reference"}
V1_REQUIRED = desk.LEG_SUMMARY_KEYS - V11_KEYS
V11_SCHEMA = "joulewise.cadence_campaign_kit.v1.1"

# Named stops this module adds. "integrity": the automatic table cannot be trusted as final.
INTEGRITY_CODES = ("DESK_UNAUTHENTICATED", "DESK_IDENTITY", "DESK_ROSTER", "DESK_NO_LEG_ROWS", "DESK_DUPLICATE",
                   "DESK_ATTEMPTS", "DESK_SCHEMA", "DESK_FEED_PROOF", "DESK_REFUSAL", "DESK_ERROR")
HAND_CODES = ("HAND_TABLE_DISAGREES",)
PENDING_CODES = ("HAND_TABLE_DUE",)
GATE_REQUIRED = "hand gate required"

# Consumer gates RL-172 keeps by name: (campaign, leg) -> the ruling and what the lead's record decides.
CONSUMER_GATES = {
    ("cl-dev-03", "L002"): ("L002 consumer gate", "RL-158 section 2 (the pilot's gate on the remainder)",
                            "dev-03's remainder arms on the lead's record only if L002 released its G0; if it "
                            "timed out, nothing span-shaped arms and Q1's print goes to the research lead"),
    ("cl-dev-04", "L005"): ("L005 consumer gate", "RL-163 section 6, amended by RL-165 section 4 and RL-167 "
                            "section 5", "dev-04's second span arms on the lead's record if L005 released its "
                            "G0; if it timed out, it arms only if dev-03 ended with at least four of its five "
                            "consumers released"),
}

# Hand-table fields compared with the automatic table, and the tolerance on seconds (rounding in the
# hand table's journal reads).
HAND_COMPARE = ("attempts", "contaminated_redos", "redo_reasons", "g0_outcome", "band_reached", "admitted",
                "start_band", "seed", "budget_s", "os_level_max", "pm_nominal", "prefill_tokens", "g0_shape",
                "g0_role", "g0_s", "wall_s", "span_reference")
SECONDS_TOLERANCE = 1.0
# desk._guard_text's words (whole words, so "joulewise" is not one), plus the leg-summary deny list's names.
_DENIED_WORD = re.compile(r"(?i)\b(\w*energy\w*|joules?|\w*power_w\w*|watts?|slots?|slot_\w+|\w*transcripts?|"
                          r"\w*meter_samples\w*|\w*samples_w\w*|\w*token_ids\w*|\w*output_text\w*|"
                          r"\w*prompt_text\w*|\w*_j|j_\w+)\b")


class _Fatal(Exception):
    """Nothing further can be judged (the expected roster or the bundle is unreadable)."""


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def _sanitize(text):
    return _DENIED_WORD.sub("[denied]", str(text))[:400]


class _Reader:
    """Every read goes through here: allowlisted basenames only, each file read once, hashed and parsed
    from the same bytes. ``opened`` is the audit list."""

    def __init__(self):
        self.opened = []

    def read(self, path):
        path = Path(path)
        if path.name not in ALLOWED_BASENAMES:
            raise desk.DeskRefusal(f"{path.name} is not a desk-final input")
        if path.is_symlink():
            raise desk.DeskRefusal(f"{path.name}: a symlink is not a desk input")
        self.opened.append(str(path))
        raw = path.read_bytes()
        return raw, sha256_bytes(raw)

    def json(self, path):
        raw, digest = self.read(path)
        try:
            return json.loads(raw, object_pairs_hook=_unique), digest
        except ValueError as error:
            raise desk.DeskRefusal(f"{Path(path).name}: not JSON ({_sanitize(error)})") from None


def _unique(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f"duplicate key {k!r}")
        out[k] = v
    return out


class _Findings:
    def __init__(self):
        self.items = {}

    def add(self, code, detail):
        self.items.setdefault(code, [])
        if detail not in self.items[code]:
            self.items[code].append(detail)

    def stops(self, kind):
        return [{"code": c, "kind": kind, "detail": "; ".join(d)[:2000]} for c, d in self.items.items()]


# --------------------------------------------------------------------------
# The bundle: reference packer (what the controller publishes) and the walk
# --------------------------------------------------------------------------
def pack_bundle(span_dir, bundle_dir, *, plan_id, queue_id, span_id, attempt, kit, producer=None):
    """The reference packer: copy the runner's ``runner_receipt.json`` and its ``desk-bundle/`` files into
    ``bundle_dir`` and write ``BUNDLE_MANIFEST.json``. ``kit`` is the queue entry's identity
    ({path, sha256, campaign_id, frozen_commit}). Returns the manifest's sha256 (the anchor the controller
    publishes in its per-span record). Opens only allowlisted basenames."""
    span_dir, bundle_dir = Path(span_dir), Path(bundle_dir)
    reader = _Reader()
    bundle_dir.mkdir(parents=True, exist_ok=False)
    files = {}
    sources = [(span_dir / RECEIPT_NAME, RECEIPT_NAME)]
    source_root = span_dir / "desk-bundle"
    for path in sorted(source_root.rglob("*")):
        if path.is_file() or path.is_symlink():
            rel = path.relative_to(source_root).as_posix()
            if not BUNDLE_PATH_RE.fullmatch(rel):
                raise desk.DeskRefusal(f"desk-bundle/{rel} is not in the bundle layout")
            sources.append((path, rel))
    for path, rel in sources:
        raw, digest = reader.read(path)
        target = bundle_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        files[rel] = digest
    manifest = {"schema": BUNDLE_SCHEMA, "plan_id": plan_id, "queue_id": queue_id, "span_id": span_id,
                "attempt": attempt, "kit": dict(kit), "receipt": {"path": RECEIPT_NAME, "sha256": files[RECEIPT_NAME]},
                "files": dict(sorted(files.items()))}
    if producer is not None:
        manifest["producer"] = producer
    raw = (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode()
    (bundle_dir / MANIFEST_NAME).write_bytes(raw)
    return sha256_bytes(raw)


def _walk(bundle_dir, find):
    """Relative paths of every file in the bundle except the manifest, without opening any."""
    out = []
    for root, dirs, names in os.walk(bundle_dir, followlinks=False):
        for d in dirs:
            if (Path(root) / d).is_symlink():
                find.add("DESK_UNAUTHENTICATED", f"{(Path(root) / d).relative_to(bundle_dir).as_posix()}: symlink")
        for name in names:
            rel = (Path(root) / name).relative_to(bundle_dir).as_posix()
            if rel != MANIFEST_NAME:
                out.append(rel)
    return sorted(out)


# --------------------------------------------------------------------------
# Expected identities: the queue entry and the kit
# --------------------------------------------------------------------------
def expected_identity(queue_doc, plan_id, kit, kit_sha256, find):
    """The queue entry for ``plan_id`` and the kit, as the desk's expectation. Raises _Fatal when there is
    no roster to judge against."""
    try:
        queuemod.validate_queue(queue_doc)
    except queuemod.QueueError as error:
        find.add("DESK_IDENTITY", f"queue does not validate: {_sanitize(error)}")
        raise _Fatal() from None
    spans = [s for s in queue_doc["spans"] if queuemod.plan_id(s) == plan_id]
    if len(spans) != 1:
        find.add("DESK_IDENTITY", f"plan id {plan_id} is {'not in' if not spans else 'repeated in'} queue "
                                  f"{queue_doc.get('queue_id')}")
        raise _Fatal()
    span = spans[0]
    if span["kit"]["sha256"] != kit_sha256:
        find.add("DESK_IDENTITY", f"kit file sha256 {kit_sha256[:12]} is not the queue's pin "
                                  f"{span['kit']['sha256'][:12]}")
    kit_ids = [leg["leg_id"] for leg in kit["legs"]]
    unknown = [x for x in span["legs"] if x not in kit_ids]
    if unknown:
        find.add("DESK_IDENTITY", f"queue roster legs not in the kit: {unknown[:5]}")
    return {"plan_id": plan_id, "queue_id": queue_doc["queue_id"], "span_id": span["span_id"],
            "attempt": span["attempt"], "roster": list(span["legs"]),
            "kit": {"path": span["kit"]["path"], "sha256": span["kit"]["sha256"], "campaign_id": kit["campaign_id"],
                    "frozen_commit": kit["frozen"]["commit"]},
            "kit_schema": kit["schema"], "runner_kind": kit["runner"]["kind"],
            "redo_quota": kit["span_template"]["redo_quota"], "kit_first_leg": kit_ids[0] if kit_ids else None,
            "kit_legs": {leg["leg_id"]: leg for leg in kit["legs"]}}


# --------------------------------------------------------------------------
# Condition 3: authentication
# --------------------------------------------------------------------------
def authenticate(bundle_dir, manifest_sha256, expected, reader, find):
    """Verify the manifest against the anchor and every file against the manifest. Returns
    {rel: (raw-sha256 verified bool)} for the files present and allowlisted."""
    bundle_dir = Path(bundle_dir)
    if not (bundle_dir / MANIFEST_NAME).is_file():
        find.add("DESK_UNAUTHENTICATED", f"no {MANIFEST_NAME}")
        raise _Fatal()
    manifest, digest = reader.json(bundle_dir / MANIFEST_NAME)
    if not (isinstance(manifest_sha256, str) and HEX64.fullmatch(manifest_sha256)):
        find.add("DESK_UNAUTHENTICATED", "no manifest anchor (the controller's per-span record carries it)")
    elif digest != manifest_sha256:
        find.add("DESK_UNAUTHENTICATED", f"manifest sha256 {digest[:12]} is not the anchor {manifest_sha256[:12]}")
    if not isinstance(manifest, dict):
        find.add("DESK_UNAUTHENTICATED", "manifest: not an object")
        raise _Fatal()
    keys = set(manifest)
    if keys - MANIFEST_KEYS - MANIFEST_OPTIONAL or MANIFEST_KEYS - keys:
        find.add("DESK_UNAUTHENTICATED", f"manifest keys: missing {sorted(MANIFEST_KEYS - keys)}, "
                                         f"unknown {sorted(keys - MANIFEST_KEYS - MANIFEST_OPTIONAL)}")
    if manifest.get("schema") != BUNDLE_SCHEMA:
        find.add("DESK_UNAUTHENTICATED", f"manifest schema {manifest.get('schema')!r}")
    for key in ("plan_id", "queue_id", "span_id", "attempt"):
        if manifest.get(key) != expected[key]:
            find.add("DESK_IDENTITY", f"manifest {key} {manifest.get(key)!r} is not the queue's {expected[key]!r}")
    kit = manifest.get("kit")
    if not (isinstance(kit, dict) and set(kit) == KIT_IDENTITY_KEYS):
        find.add("DESK_IDENTITY", "manifest kit: {path, sha256, campaign_id, frozen_commit}")
    else:
        for key in sorted(KIT_IDENTITY_KEYS):
            if kit[key] != expected["kit"][key]:
                find.add("DESK_IDENTITY", f"manifest kit.{key} {str(kit[key])[:16]!r} is not the expected "
                                          f"{str(expected['kit'][key])[:16]!r}")
    files = manifest.get("files")
    if not (isinstance(files, dict) and all(isinstance(k, str) and isinstance(v, str) and HEX64.fullmatch(v)
                                            for k, v in files.items())):
        find.add("DESK_UNAUTHENTICATED", "manifest files: {relative path: sha256}")
        raise _Fatal()
    receipt = manifest.get("receipt")
    if not (isinstance(receipt, dict) and receipt.get("path") == RECEIPT_NAME
            and receipt.get("sha256") == files.get(RECEIPT_NAME) and files.get(RECEIPT_NAME)):
        find.add("DESK_UNAUTHENTICATED", "manifest receipt: {path: runner_receipt.json, sha256} equal to its "
                                         "files entry")
    present = _walk(bundle_dir, find)
    verified = {}
    for rel in sorted(set(present) | set(files)):
        if not BUNDLE_PATH_RE.fullmatch(rel):
            find.add("DESK_UNAUTHENTICATED", f"{rel}: not in the bundle layout (not opened)")
            continue
        if rel not in files:
            find.add("DESK_UNAUTHENTICATED", f"{rel}: in the bundle, not in the manifest")
            continue
        if rel not in present:
            find.add("DESK_UNAUTHENTICATED", f"{rel}: in the manifest, not in the bundle")
            continue
        raw, got = reader.read(bundle_dir / rel)
        if got != files[rel]:
            find.add("DESK_UNAUTHENTICATED", f"{rel}: sha256 {got[:12]} is not the manifest's {files[rel][:12]}")
        verified[rel] = raw
    if RECEIPT_NAME not in verified:
        find.add("DESK_UNAUTHENTICATED", "no runner receipt in the bundle")
        raise _Fatal()
    return manifest, digest, verified


def _loads(raw, where):
    try:
        return json.loads(raw, object_pairs_hook=_unique)
    except ValueError as error:
        raise desk.DeskRefusal(f"{where}: not JSON ({_sanitize(error)})") from None


# --------------------------------------------------------------------------
# The receipt, projected (operational fields only)
# --------------------------------------------------------------------------
_ATTEMPT_KEYS = ("attempt", "redone", "contaminated", "output_dir", "leg_status", "redo_reason")
_LEG_RESULT_KEYS = ("leg_id", "g0_role", "g0_shape", "g0_outcome", "leg_status", "g0_reference_source",
                    "g0_reference_record_sha256")


def project_receipt(doc):
    if not isinstance(doc, dict):
        raise desk.DeskRefusal("runner_receipt.json: not an object")
    legs = []
    for leg in doc.get("legs") or []:
        if not isinstance(leg, dict):
            legs.append({"leg_id": None, "attempts": [], "summary": None})
            continue
        legs.append({"leg_id": leg.get("leg_id"), "budget_s": leg.get("budget_s"),
                     "attempts": [{k: a.get(k) for k in _ATTEMPT_KEYS} if isinstance(a, dict) else {}
                                  for a in leg.get("attempts") or []],
                     "span_reference": leg.get("span_reference"), "summary": leg.get("summary")})
    steps = []
    for step in doc.get("steps") or []:
        if not isinstance(step, dict):
            continue
        row = {"name": step.get("name"), "rc": step.get("rc")}
        result = step.get("result") if isinstance(step.get("result"), dict) else {}
        if step.get("name") == "restore":
            row["action"] = result.get("action")
        if "g0_role" in result:
            row["leg"] = {k: result.get(k) for k in _LEG_RESULT_KEYS}
        steps.append(row)
    feeds = {}
    for name, feed in (doc.get("feeds") or {}).items():
        stop = feed.get("stop") if isinstance(feed, dict) else None
        feeds[name] = ({"rc": stop.get("rc"), "proven_stopped": stop.get("proven_stopped")}
                       if isinstance(stop, dict) else None)
    error = doc.get("error")
    out = {"schema": doc.get("schema"), "runner_kind": doc.get("runner_kind"), "mock": doc.get("mock"),
           "kit": doc.get("kit"), "roster": doc.get("roster"), "rc": doc.get("rc"),
           "error_type": str(error).split(":", 1)[0][:80] if error else None,
           "span_result": doc.get("span_result"), "meter": doc.get("meter"),
           "legs_finished": doc.get("legs_finished"), "legs_planned": doc.get("legs_planned"),
           "load_redos_used": doc.get("load_redos_used"), "legs": legs, "steps": steps, "feeds": feeds,
           "soak_attempts": [{"attempt": a.get("attempt"), "refused": bool(a.get("refused")),
                              "output_dir": a.get("output_dir")}
                             for a in doc.get("soak_attempts") or [] if isinstance(a, dict)],
           "desk_bundle_error": bool(doc.get("desk_bundle_error"))}
    bad = [k for k in desk._keys(out) if desk.DENIED_KEY_RE.search(k)]
    if bad:
        raise desk.DeskRefusal(f"runner_receipt.json projection carries denied keys {sorted(set(bad))[:5]}")
    return out


# --------------------------------------------------------------------------
# Conditions 1, 2 and 4 on the parsed bundle
# --------------------------------------------------------------------------
def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def check_receipt_identity(receipt, expected, allow_mock, find):
    if receipt["schema"] != RECEIPT_SCHEMA:
        find.add("DESK_IDENTITY", f"receipt schema {receipt['schema']!r}")
    if receipt["runner_kind"] != expected["runner_kind"]:
        find.add("DESK_IDENTITY", f"receipt runner kind {receipt['runner_kind']!r} is not the kit's "
                                  f"{expected['runner_kind']!r}")
    kit = receipt["kit"] if isinstance(receipt["kit"], dict) else {}
    for key in ("sha256", "campaign_id", "frozen_commit"):
        if kit.get(key) != expected["kit"][key]:
            find.add("DESK_IDENTITY", f"receipt kit.{key} {str(kit.get(key))[:16]!r} is not the expected "
                                      f"{str(expected['kit'][key])[:16]!r}")
    if receipt["mock"] is not False and not (allow_mock and receipt["mock"] is True):
        find.add("DESK_IDENTITY", f"receipt mock={receipt['mock']!r}: a mock span is never desk-final")


def load_rows(verified, find):
    """Leg rows from ``legs/<dir>/leg_summary.json``: refused on a denied or unknown key; a summary whose
    leg_id is not its directory, or a leg id recorded twice, is DESK_DUPLICATE."""
    rows = {}
    for rel, raw in sorted(verified.items()):
        m = BUNDLE_PATH_RE.fullmatch(rel)
        if not (m and m.group(1)):
            continue
        doc = desk._project(_loads(raw, rel), desk.LEG_SUMMARY_KEYS, rel, True)
        leg_id = doc.get("leg_id")
        if leg_id != m.group(1):
            find.add("DESK_DUPLICATE", f"{rel} records leg {leg_id!r}")
        rows.setdefault(leg_id, []).append(doc)
    for leg_id, docs in rows.items():
        if len(docs) > 1:
            find.add("DESK_DUPLICATE", f"leg {leg_id} has {len(docs)} records")
    return rows


def check_roster(rows, receipt, expected, find):
    roster = expected["roster"]
    if receipt["roster"] != roster:
        find.add("DESK_ROSTER", f"receipt roster {receipt['roster']} is not the queue's {roster}")
    receipt_ids = [leg["leg_id"] for leg in receipt["legs"]]
    dupes = sorted({x for x in receipt_ids if receipt_ids.count(x) > 1}, key=str)
    if dupes:
        find.add("DESK_DUPLICATE", f"receipt records legs {dupes} more than once")
    if receipt_ids != roster:
        find.add("DESK_ROSTER", f"receipt legs {receipt_ids} are not the queue's roster {roster} (ids, order, count)")
    if not rows:
        find.add("DESK_NO_LEG_ROWS", f"no leg rows (the queue's roster has {len(roster)})")
    missing = [x for x in roster if x not in rows]
    extra = sorted((x for x in rows if x not in roster), key=str)
    if missing:
        find.add("DESK_ROSTER", f"missing leg records {missing}")
    if extra:
        find.add("DESK_ROSTER", f"leg records not on the roster {extra}")
    for key in ("legs_planned", "legs_finished"):
        if receipt[key] != len(roster):
            find.add("DESK_ROSTER", f"receipt {key} {receipt[key]} is not the roster's {len(roster)}")
    ordered = [rows[x][0] for x in roster if x in rows]
    starts = [r.get("started_epoch_s") for r in ordered]
    if not all(_num(s) for s in starts) or starts != sorted(starts):
        find.add("DESK_ROSTER", "leg start stamps are missing or out of roster order")
    return ordered


def check_schema(ordered, receipt, expected, find):
    required = desk.LEG_SUMMARY_KEYS if expected["kit_schema"] == V11_SCHEMA else V1_REQUIRED
    copies = {leg["leg_id"]: leg for leg in receipt["legs"]}
    for row in ordered:
        missing = sorted(required - set(row))
        if missing:
            find.add("DESK_SCHEMA", f"{row['leg_id']}: missing fields {missing}")
        copy = copies.get(row["leg_id"])
        if copy is None or copy.get("summary") != row:
            find.add("DESK_SCHEMA", f"{row['leg_id']}: the bundle's leg summary is not the receipt's copy")


def check_attempts(ordered, receipt, expected, find):
    by_id = {leg["leg_id"]: leg for leg in receipt["legs"]}
    redone_total = 0
    for row in ordered:
        leg_id = row["leg_id"]
        attempts = (by_id.get(leg_id) or {}).get("attempts") or []
        if not attempts:
            find.add("DESK_ATTEMPTS", f"{leg_id}: no attempt records in the receipt")
            continue
        n = len(attempts)
        for k, a in enumerate(attempts, start=1):
            last = k == n
            want_dir = f"legs/{leg_id}/runtime" if last else f"legs/{leg_id}/runtime.rejected{k}"
            if a.get("attempt") != k:
                find.add("DESK_ATTEMPTS", f"{leg_id}: attempt {k} is numbered {a.get('attempt')!r}")
            if a.get("output_dir") != want_dir:
                find.add("DESK_ATTEMPTS", f"{leg_id} attempt {k}: kept as {a.get('output_dir')!r}, not {want_dir}")
            if a.get("redone") is not (not last):
                find.add("DESK_ATTEMPTS", f"{leg_id} attempt {k}: redone={a.get('redone')!r}")
            if not last and a.get("contaminated") is not True:
                find.add("DESK_ATTEMPTS", f"{leg_id} attempt {k}: a redo of an attempt that was not contaminated")
        redone_total += n - 1
        if row.get("attempts") != n:
            find.add("DESK_ATTEMPTS", f"{leg_id}: summary attempts {row.get('attempts')!r}, receipt {n}")
        contaminated = sum(1 for a in attempts if a.get("contaminated") is True)
        if row.get("contaminated_redos") != contaminated:
            find.add("DESK_ATTEMPTS", f"{leg_id}: summary contaminated_redos {row.get('contaminated_redos')!r}, "
                                      f"receipt {contaminated}")
    if receipt["load_redos_used"] != redone_total:
        find.add("DESK_ATTEMPTS", f"receipt load_redos_used {receipt['load_redos_used']!r}, kept redos {redone_total}")
    if redone_total > expected["redo_quota"]:
        find.add("DESK_ATTEMPTS", f"{redone_total} redos over the kit's quota {expected['redo_quota']}")


def check_kit_legs(ordered, receipt, expected, find):
    """Each row is the kit's leg (seed, band, budget, size, G0 shape and role); each consumer's reference is
    the roster's first leg at its accepted attempt; consumers carry one reference record hash."""
    v11 = expected["kit_schema"] == V11_SCHEMA
    roster = expected["roster"]
    capture = roster[0] if roster else None
    rows = {r["leg_id"]: r for r in ordered}
    receipt_legs = {leg["leg_id"]: leg for leg in receipt["legs"]}
    for row in ordered:
        leg_id, kit_leg = row["leg_id"], expected["kit_legs"].get(row["leg_id"]) or {}
        for key in ("seed", "start_band"):
            if row.get(key) != kit_leg.get(key):
                find.add("DESK_IDENTITY", f"{leg_id}: {key} {row.get(key)!r} is not the kit's {kit_leg.get(key)!r}")
        if row.get("budget_s") != (receipt_legs.get(leg_id) or {}).get("budget_s"):
            find.add("DESK_IDENTITY", f"{leg_id}: budget_s is not the receipt's")
        if not v11:
            continue
        shape = kit_leg.get("g0_shape")
        role = "consume" if (shape == "span" and leg_id != capture) else "capture"
        if row.get("prefill_tokens") != kit_leg.get("prefill_tokens"):
            find.add("DESK_IDENTITY", f"{leg_id}: prefill_tokens is not the kit's")
        if row.get("g0_shape") != shape or row.get("g0_role") != role:
            find.add("DESK_IDENTITY", f"{leg_id}: G0 {row.get('g0_shape')}/{row.get('g0_role')} is not the kit's "
                                      f"{shape}/{role} (capture leg {capture})")
        ref = row.get("span_reference")
        if role == "capture":
            if ref is not None:
                find.add("DESK_IDENTITY", f"{leg_id}: a capture leg names a span reference")
            continue
        first = rows.get(capture)
        n = len((receipt_legs.get(capture) or {}).get("attempts") or [])
        want = {"leg_id": capture, "attempt": n, "redone": n > 1,
                "excluded": None if first is None else first.get("admitted") is not True}
        if not isinstance(ref, dict) or ref != want:
            find.add("DESK_IDENTITY", f"{leg_id}: span reference {ref!r} is not the capture leg's accepted "
                                      f"attempt {want!r}")
        rref = (receipt_legs.get(leg_id) or {}).get("span_reference")
        if not isinstance(rref, dict) or rref.get("dir") != f"legs/{capture}/runtime":
            find.add("DESK_IDENTITY", f"{leg_id}: receipt reference dir is not legs/{capture}/runtime")
    if v11:
        hashes = {}
        for step in receipt["steps"]:
            leg = step.get("leg")
            if leg and leg.get("g0_role") == "consume" and step.get("rc") == 0:
                hashes[leg.get("leg_id")] = leg.get("g0_reference_record_sha256")
        consumers = [r["leg_id"] for r in ordered if r.get("g0_role") == "consume"]
        values = {hashes.get(c) for c in consumers}
        if consumers and (len(values) != 1 or not all(isinstance(v, str) and HEX64.fullmatch(v) for v in values)):
            find.add("DESK_IDENTITY", f"consumers do not carry one reference record sha256 ({len(values)} values)")


def check_span_files(verified, receipt, find):
    result = meter = None
    if "span/result.json" in verified:
        result = desk._project(_loads(verified["span/result.json"], "span/result.json"), desk.RESULT_KEYS,
                               "span/result.json", False)
        if result != receipt["span_result"]:
            find.add("DESK_SCHEMA", "span/result.json is not the receipt's span_result")
    else:
        find.add("DESK_SCHEMA", "no span/result.json")
    if "span/meter.json" in verified:
        meter = desk._project(_loads(verified["span/meter.json"], "span/meter.json"), desk.METER_KEYS,
                              "span/meter.json", True)
        if meter != receipt["meter"]:
            find.add("DESK_SCHEMA", "span/meter.json is not the receipt's meter")
    else:
        find.add("DESK_SCHEMA", "no span/meter.json")
    return result, meter or {}


def feed_proofs(receipt, meter, find):
    """Condition 4: every feed's own stop proof. Returns (feeds_proven_stopped, per-feed proof)."""
    proofs = {}
    step_rc = {s["name"]: s["rc"] for s in receipt["steps"]}
    names = list(EXPECTED_FEEDS) + sorted(n for n in receipt["feeds"] if n not in EXPECTED_FEEDS)
    for name in names:
        stop = receipt["feeds"].get(name)
        if not isinstance(stop, dict):
            find.add("DESK_FEED_PROOF", f"feed {name}: no stop proof in the receipt")
            proofs[name] = {"proven_stopped": False, "rc": None, "proof": "missing"}
            continue
        proven = stop.get("proven_stopped") is True and stop.get("rc") == 0 and step_rc.get(f"stop-{name}") == 0
        proofs[name] = {"proven_stopped": proven, "rc": stop.get("rc"), "proof": "receipt"}
    meter_stop = (receipt["feeds"].get("meter") or {}).get("proven_stopped")
    if meter.get("proven_stopped") != meter_stop:
        find.add("DESK_SCHEMA", "span/meter.json proven_stopped is not the meter feed's own stop proof")
    return all(p["proven_stopped"] for p in proofs.values()), proofs


SOAK_RETRIES = 1     # scripts/cadence_legs_runner.SOAK_RETRIES (RL-171): one retry after a settle or quiet refusal


def check_soak(receipt, find):
    """The soak retry (RL-171; Mythos #794 F3). Attempts are numbered 1..n with n <= 1 + SOAK_RETRIES; a refused
    attempt that was retried is kept as ``soak.rejected<k>`` and its stage (``soak``, ``soak.a<k>``) has a non-zero
    rc; the accepted attempt is ``soak`` with rc 0. A refused first soak followed by an accepted retry is a
    completed soak, never a stopped span. Returns (accepted attempt or None, detail for the print)."""
    attempts = receipt["soak_attempts"]
    step_rc = {}
    for step in receipt["steps"]:
        step_rc.setdefault(step.get("name"), step.get("rc"))
    if not attempts:
        return None, "no soak attempt recorded"
    if len(attempts) > 1 + SOAK_RETRIES:
        find.add("DESK_ATTEMPTS", f"{len(attempts)} soak attempts; the runner allows {1 + SOAK_RETRIES}")
    accepted = None
    for k, a in enumerate(attempts, start=1):
        last = k == len(attempts)
        stage = "soak" if k == 1 else f"soak.a{k}"
        if a.get("attempt") != k:
            find.add("DESK_ATTEMPTS", f"soak attempt {k} is numbered {a.get('attempt')!r}")
        if not last and (a.get("refused") is not True or a.get("output_dir") != f"soak.rejected{k}"):
            find.add("DESK_ATTEMPTS", f"soak attempt {k} was retried but is not kept as a refused soak.rejected{k}")
        if stage in step_rc and (step_rc[stage] == 0) == bool(a.get("refused")):
            find.add("DESK_ATTEMPTS", f"soak attempt {k}: stage {stage} rc {step_rc[stage]} disagrees with "
                                      f"refused={a.get('refused')}")
        if last and not a.get("refused"):
            if a.get("output_dir") != "soak":
                find.add("DESK_ATTEMPTS", f"the accepted soak is kept as {a.get('output_dir')!r}, not soak")
            accepted = k
    refused = sum(1 for a in attempts if a.get("refused"))
    if accepted is None:
        return None, f"no soak accepted ({refused} refused)"
    return accepted, (f"accepted attempt {accepted} after {refused} refused (retry)" if refused
                      else "accepted attempt 1")


# --------------------------------------------------------------------------
# Hand table and hand gates
# --------------------------------------------------------------------------
def hand_table_triggers(ordered, expected, history, hand_sample):
    """RL-172 section (c): the hand table is always taken on a span with a redo, an exclusion or a schema
    change; otherwise by the lead's seeded draw (``hand_sample``)."""
    out = []
    redos = [r["leg_id"] for r in ordered if (r.get("attempts") or 1) > 1]
    if redos:
        out.append(f"redo ({', '.join(redos)})")
    excluded = [r["leg_id"] for r in ordered if r.get("admitted") is not True]
    if excluded:
        out.append(f"exclusion ({', '.join(excluded)})")
    keys = sorted(set().union(*(set(r) for r in ordered))) if ordered else []
    previous = next((h for h in reversed(list(history or [])) if isinstance(h, dict)), None)
    if previous is None:
        out.append("schema change (no earlier desk summary in the history)")
    elif previous.get("kit_schema") != expected["kit_schema"] or previous.get("leg_keys") != keys:
        out.append("schema change (kit schema or leg-summary fields differ from the previous span's)")
    if hand_sample:
        out.append("sampled (the lead's seeded draw)")
    return out, keys


def _same(key, a, b):
    if key in ("g0_s", "wall_s") and _num(a) and _num(b):
        return abs(a - b) <= SECONDS_TOLERANCE
    if key == "span_reference" and isinstance(a, dict) and isinstance(b, dict):
        return all(a.get(k) == b.get(k) for k in ("leg_id", "attempt"))
    return a == b


def compare_hand_table(doc, ordered, operational_stops, plan_id):
    """Field-by-field comparison of a hand table with the automatic table. Returns differences."""
    diffs = []
    if not isinstance(doc, dict) or doc.get("schema") != HAND_TABLE_SCHEMA:
        return [f"hand table schema is not {HAND_TABLE_SCHEMA}"]
    if doc.get("plan_id") != plan_id:
        return [f"hand table is for {doc.get('plan_id')!r}, not {plan_id}"]
    bad = [k for k in desk._keys(doc) if desk.DENIED_KEY_RE.search(k)]
    if bad:
        raise desk.DeskRefusal("hand_table.json carries denied keys")
    hand = doc.get("legs") if isinstance(doc.get("legs"), list) else []
    hand_ids = [h.get("leg_id") for h in hand if isinstance(h, dict)]
    auto_ids = [r["leg_id"] for r in ordered]
    if hand_ids != auto_ids:
        diffs.append(f"legs: hand {hand_ids}, automatic {auto_ids}")
    auto = {r["leg_id"]: r for r in ordered}
    for h in hand:
        if not isinstance(h, dict) or h.get("leg_id") not in auto:
            continue
        a = auto[h["leg_id"]]
        for key in HAND_COMPARE:
            if key in h and not _same(key, h[key], a.get(key)):
                diffs.append(f"{h['leg_id']}.{key}: hand {h[key]!r}, automatic {a.get(key)!r}")
    if "named_stops" in doc:
        hand_codes = sorted(doc.get("named_stops") or [])
        auto_codes = sorted(s["code"] for s in operational_stops)
        if hand_codes != auto_codes:
            diffs.append(f"named stops: hand {hand_codes}, automatic {auto_codes}")
    return diffs


def _retried_soak(step, receipt):
    attempts = receipt["soak_attempts"]
    name = step.get("name") or ""
    k = 1 if name == "soak" else int(name[6:]) if re.fullmatch(r"soak\.a\d+", name) else None
    return k is not None and k < len(attempts) and bool(attempts[k - 1].get("refused"))


def hand_gates(ordered, receipt, expected, mark):
    """The hand gates RL-172 keeps, with what each hand check needs. The desk never clears one."""
    gates = []
    campaign = expected["kit"]["campaign_id"]
    roster = expected["roster"]
    steps = receipt["steps"]
    if expected["kit_first_leg"] in roster:
        gates.append({
            "gate": "class A smoke hand-read", "status": GATE_REQUIRED,
            "ruling": "RL-150 R5; RL-149 section 2.9 item 3; RL-172 section (c)",
            "holds": f"kit:{campaign}",
            "why": f"this span runs the kit's first leg {expected['kit_first_leg']} (the new kit's first span)",
            "print": {"steps": len(steps),
                      "steps_nonzero": [s["name"] + (" (refused soak, retried)" if _retried_soak(s, receipt) else "")
                                        for s in steps if s.get("rc") != 0],
                      "soak_attempts": receipt["soak_attempts"],
                      "restore": next(({"rc": s.get("rc"), "action": s.get("action")} for s in steps
                                       if s.get("name") == "restore"), None),
                      "feeds": receipt["feeds"], "result": receipt["span_result"]}})
    rows = {r["leg_id"]: r for r in ordered}
    for (gate_campaign, leg_id), (name, ruling, rule) in CONSUMER_GATES.items():
        kit_leg = expected["kit_legs"].get(leg_id) or {}
        if campaign == gate_campaign and leg_id in roster and kit_leg.get("g0_shape") == "span":
            row = rows.get(leg_id) or {}
            gates.append({"gate": name, "status": GATE_REQUIRED, "ruling": ruling, "holds": f"kit:{campaign}",
                          "why": rule,
                          "print": {"leg_id": leg_id, "g0_role": row.get("g0_role"),
                                    "g0_outcome": row.get("g0_outcome"), "g0_s": row.get("g0_s"),
                                    "admitted": row.get("admitted")}})
    if expected["kit_schema"] == V11_SCHEMA:
        capture = roster[0] if roster else None
        accepted = next((s.get("output_dir") for s in reversed(receipt["soak_attempts"]) if not s.get("refused")),
                        None)
        gates.append({
            "gate": "RL-158 Q1 reference print", "status": GATE_REQUIRED, "ruling": "RL-158 Q1; RL-172 section (c)",
            "holds": None,
            "why": "every v1.1 span: the leg summary does not carry the readings (thermal journal values, as "
                   "RL-150 R1 part 3); it becomes automatic only on the research lead's ruling",
            "print": {"soak_reference": {"dir": accepted, "attempts": len(receipt["soak_attempts"])},
                      "capture": None if capture is None else {
                          "leg_id": capture, "dir": f"legs/{capture}/runtime",
                          "attempt": len(next((leg["attempts"] for leg in receipt["legs"]
                                               if leg["leg_id"] == capture), [])),
                          "marks": (mark or {}).get("marks", [])},
                      "consumers": [{"leg_id": r["leg_id"], "g0_outcome": r.get("g0_outcome"), "g0_s": r.get("g0_s"),
                                     "admitted": r.get("admitted")}
                                    for r in ordered if r.get("g0_role") == "consume"],
                      "hand_reads": ["soak reference (TV0h, TV1h, Tf08)", "the capture leg's own reference reading",
                                     "each consumer's release reading"]}})
    return gates


# --------------------------------------------------------------------------
# The judge
# --------------------------------------------------------------------------
def _gate_lines(gates):
    out = ["", "## Hand gates (RL-172 section (c): kept; the desk prints, the lead reads)", ""]
    if not gates:
        return out + ["- none for this span"]
    for g in gates:
        out.append(f"- **{g['status'].upper()}: {g['gate']}** ({g['ruling']}). {g['why']}."
                   + (f" Holds `{g['holds']}` until the lead's record." if g["holds"] else " Gates nothing by itself."))
        out.append(f"  - print: `{json.dumps(g['print'], sort_keys=True)}`")
    return out


def _finish(verdict):
    body = {k: v for k, v in verdict.items() if k != "verdict_sha256"}
    verdict["verdict_sha256"] = sha256_bytes(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())
    return verdict


def _code_identity():
    out = {}
    for mod in (desk, queuemod, stopsmod):
        path = Path(mod.__file__)
        out[f"joulewise/cadence/{path.name}"] = sha256_bytes(path.read_bytes())
    out["joulewise/cadence/desk_final.py"] = sha256_bytes(Path(__file__).read_bytes())
    return out


def _write(path, text):
    tmp = path.with_name("." + path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def judge_span(*, plan_id, bundle_dir, manifest_sha256, queue_path, kit_path, out_dir, history=(),
               hand_table_path=None, hand_sample=False, allow_mock=False, now=None):
    """Judge one span's bundle. Always writes ``desk_verdict.json`` to ``out_dir`` (a negative or error
    result is also a receipt); writes ``JOURNAL-TABLE.md``, ``desk_summary.json`` and ``stops.json`` when the
    bundle could be read. Returns the verdict."""
    from joulewise.cadence import kit as kitmod
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    find, reader = _Findings(), _Reader()
    expected, operational, gates, hand = None, [], [], {"required": False, "triggers": [], "supplied": False,
                                                         "agrees": None, "differences": []}
    identities, error, mock = {"manifest_sha256": None, "receipt_sha256": None}, None, None
    text = summary = summary_text = None
    try:
        try:
            kit, kit_sha = kitmod.load_kit(kit_path)
        except kitmod.KitError as e:
            find.add("DESK_IDENTITY", f"kit does not load: {_sanitize('; '.join(e.problems[:3]))}")
            raise _Fatal() from None
        try:
            queue_doc = json.loads(Path(queue_path).read_text(encoding="utf-8"), object_pairs_hook=_unique)
        except (OSError, ValueError) as e:
            find.add("DESK_IDENTITY", f"queue does not load: {_sanitize(e)}")
            raise _Fatal() from None
        if kit["desk"]["adapter"] != "leg-summary-v1":
            find.add("DESK_IDENTITY", f"adapter {kit['desk']['adapter']}: desk-final is defined for leg-summary-v1")
            raise _Fatal()
        expected = expected_identity(queue_doc, plan_id, kit, kit_sha, find)
        identities.update(kit_sha256=kit_sha, campaign_id=kit["campaign_id"], frozen_commit=kit["frozen"]["commit"],
                          roster=expected["roster"], capture_leg=expected["roster"][0] if expected["roster"] else None)
        manifest, manifest_digest, verified = authenticate(bundle_dir, manifest_sha256, expected, reader, find)
        identities.update(manifest_sha256=manifest_digest,
                          receipt_sha256=sha256_bytes(verified[RECEIPT_NAME]))
        receipt = project_receipt(_loads(verified[RECEIPT_NAME], RECEIPT_NAME))
        mock = receipt["mock"]
        check_receipt_identity(receipt, expected, allow_mock, find)
        rows = load_rows(verified, find)
        ordered = check_roster(rows, receipt, expected, find)
        check_schema(ordered, receipt, expected, find)
        check_attempts(ordered, receipt, expected, find)
        check_kit_legs(ordered, receipt, expected, find)
        result, meter = check_span_files(verified, receipt, find)
        proven, proofs = feed_proofs(receipt, meter, find)
        triggers, leg_keys = hand_table_triggers(ordered, expected, history, hand_sample)
        mark = desk.span_reference_marks(ordered)
        summary = {"plan_id": plan_id, "adapter": "leg-summary-v1", "result": result, "meter": meter,
                   "feeds_proven_stopped": proven, "feeds": proofs, "legs": ordered,
                   "kit_schema": expected["kit_schema"], "leg_keys": leg_keys}
        if mark is not None:
            summary["span_reference"] = mark
        soak_accepted, soak_note = check_soak(receipt, find)
        summary["soak"] = {"attempts": len(receipt["soak_attempts"]), "accepted_attempt": soak_accepted,
                           "note": soak_note}
        operational = [{**s, "kind": "operational"} for s in evaluate_named_stops(kit["stop_rules"], summary, history)]
        if soak_accepted is None:   # every soak refused: the span stopped before any leg (a REFUSAL)
            refusal = next((s for s in operational if s["code"] == "REFUSAL"), None)
            if refusal is None:
                operational.insert(0, {"code": "REFUSAL", "detail": soak_note, "kind": "operational"})
            else:
                refusal["detail"] += f"; {soak_note}"
        hand.update(required=bool(triggers), triggers=triggers)
        if hand_table_path is not None:
            doc, _ = reader.json(hand_table_path)
            hand.update(supplied=True)
            diffs = compare_hand_table(doc, ordered, operational, plan_id)
            hand.update(agrees=not diffs, differences=diffs[:50])
            if diffs:
                find.add("HAND_TABLE_DISAGREES", "; ".join(diffs[:10]))
        elif triggers:
            find.add("HAND_TABLE_DUE", f"a hand table is required: {', '.join(triggers)}")
        gates = hand_gates(ordered, receipt, expected, mark)
        lines = [f"# Desk table: {plan_id}", "",
                 f"Built automatically on the Air at {time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(now))} "
                 "by joulewise.cadence.desk_final (leg-summary-v1, authenticated bundle). Operational fields only.",
                 "", "## Legs", ""] + desk.leg_table(ordered, kit["stop_rules"]) + desk.cell_table(ordered, mark)
        lines += ["", "## Desk-final checks (RL-172 section (c))", "",
                  f"- roster (queue {expected['queue_id']}, span {expected['span_id']} attempt {expected['attempt']}): "
                  f"{', '.join(expected['roster'])}",
                  f"- kit {kit['campaign_id']} sha256 {kit_sha[:12]}, frozen {kit['frozen']['commit'][:12]}",
                  f"- manifest sha256 {manifest_digest[:12]}; receipt sha256 {identities['receipt_sha256'][:12]}",
                  f"- soak (RL-171 retry): {soak_note}",
                  "- feeds (each feed's own stop proof): "
                  + ", ".join(f"{n} {'proven' if p['proven_stopped'] else 'NOT proven'}" for n, p in proofs.items()),
                  f"- hand table: {'required (' + '; '.join(triggers) + ')' if triggers else 'not required'}"
                  f"{'; supplied, ' + ('agrees' if hand['agrees'] else 'DISAGREES') if hand['supplied'] else ''}"]
        lines += _gate_lines(gates)
        lines += ["", "## Receipt", "",
                  f"- rc {receipt['rc']}{'; error ' + receipt['error_type'] if receipt['error_type'] else ''}; "
                  f"steps {len(receipt['steps'])}, non-zero: "
                  f"{', '.join(s['name'] + (' (refused soak, retried)' if _retried_soak(s, receipt) else '') for s in receipt['steps'] if s.get('rc') != 0) or 'none'}",
                  f"- soak: {soak_note}; attempts {json.dumps(receipt['soak_attempts'], sort_keys=True)}",
                  f"- result: {json.dumps(result, sort_keys=True)}",
                  f"- KM003C: {json.dumps(meter, sort_keys=True)}"]
        text = "\n".join(lines) + "\n"
        desk._guard_text(text)
        summary_text = json.dumps(summary, sort_keys=True, indent=1)
        bad = [k for k in desk._keys(summary) if desk.DENIED_KEY_RE.search(k)]
        if bad:
            raise desk.DeskRefusal(f"summary carries denied keys {sorted(set(bad))[:5]}")
    except _Fatal:
        pass
    except desk.DeskRefusal as e:
        find.add("DESK_REFUSAL", _sanitize(e))
        error, text, summary = _sanitize(e), None, None
    except Exception as e:  # noqa: BLE001 - an error result is also a receipt
        find.add("DESK_ERROR", f"{type(e).__name__}: {_sanitize(e)}")
        error, text, summary = f"{type(e).__name__}: {_sanitize(e)}", None, None

    integrity = [s for s in find.stops("integrity") if s["code"] in INTEGRITY_CODES]
    hand_stops = [s for s in find.stops("hand") if s["code"] in HAND_CODES]
    pending = [s for s in find.stops("pending") if s["code"] in PENDING_CODES]
    named = integrity + operational + hand_stops
    holds = [{"code": s["code"], "scope": "queue", "cleared_by": "the lead (named stop)"} for s in named]
    holds += [{"code": "HAND_GATE", "scope": g["holds"], "gate": g["gate"], "cleared_by": "the lead's record"}
              for g in gates if g["holds"]]
    desk_final = not integrity and not hand_stops and not pending and expected is not None
    reasons = [f"{s['code']}: {s['detail']}" for s in integrity + hand_stops + pending]
    verdict = _finish(_clean({
        "schema": VERDICT_SCHEMA, "plan_id": plan_id,
        "queue_id": expected and expected["queue_id"], "span_id": expected and expected["span_id"],
        "attempt": expected and expected["attempt"],
        "desk_final": desk_final, "reasons": reasons, "named_stops": named, "pending": pending,
        "next_arm_hold": any(h["scope"] == "queue" for h in holds), "holds": holds,
        "hand_gates": gates, "hand_table": hand, "identities": identities, "mock": mock,
        "opened": [Path(p).name for p in reader.opened], "error": error,
        "desk_code": _code_identity(),
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(now))}))
    for name in ("JOURNAL-TABLE.md", "desk_summary.json", "stops.json"):   # no stale table beside a new verdict
        if text is None and (out / name).exists():
            (out / name).unlink()
    if text is not None:
        named_lines = [f"- **{s['code']}** ({s['kind']}): {s['detail']}" for s in verdict["named_stops"]]
        tail = (["", "## Named stops", ""] + (named_lines or ["- none (no page)"])
                + ["", "## Verdict", "", f"- **desk_final: {str(desk_final).lower()}**; next arm held: "
                   f"{str(verdict['next_arm_hold']).lower()}"] + [f"- {r}" for r in verdict["reasons"]])
        _write(out / "JOURNAL-TABLE.md", text + "\n".join(tail) + "\n")
        _write(out / "desk_summary.json", summary_text + "\n")
        _write(out / "stops.json", json.dumps(verdict["named_stops"], sort_keys=True, indent=1) + "\n")
    _write(out / VERDICT_NAME, json.dumps(verdict, sort_keys=True, indent=1) + "\n")
    return verdict


def _clean(node):
    """Free text in a verdict never carries a denied word (details quote values read from the bundle)."""
    if isinstance(node, dict):
        return {k: _clean(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_clean(v) for v in node]
    if isinstance(node, str):
        return _DENIED_WORD.sub("[denied]", node)
    return node


def verify_verdict(doc):
    """True when a verdict's ``verdict_sha256`` matches its content (the controller's first check)."""
    if not isinstance(doc, dict) or doc.get("schema") != VERDICT_SCHEMA:
        return False
    body = {k: v for k, v in doc.items() if k != "verdict_sha256"}
    return doc.get("verdict_sha256") == sha256_bytes(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())
