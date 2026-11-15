"""Desk-final from the automatic table (RL-172 section (c), on Sol's conditions; RL-149 section 2.8 line 9).

The frozen desk (``joulewise.cadence.desk``) builds a table from whatever leg summaries it finds. Sol's
probe showed that clean status and meter metadata with zero leg rows raise no named stop, that the row
loader skips a missing summary, and that ``build_desk`` takes no expected roster. "The automatic table
builds with no stop" is therefore not finality. ``judge_span`` is: it builds the same table from an
authenticated bundle, against the queue entry's roster and the kit's identities, and writes a
machine-readable verdict that the queue controller reads for the k+2 rule. The wire format (bundle,
signed commits, verdict) is ``docs/process/cadence_desk_format.md``; ``desk_transport`` moves it.

A span is desk-final only when all of these hold (RL-172 section (c) items 1-4; Sol; the #799 gate):

1. **Roster.** The leg ids, their order and count equal the queue entry's ``legs`` and the span plan's; every
   leg's attempts are numbered 1..n, every redo kept as ``legs/<id>/runtime.rejected<k>`` and the accepted
   attempt as ``legs/<id>/runtime``. No leg record is missing or duplicated, and zero leg rows is a stop.
2. **Identities, by hash.** The kit file hashes as the queue pins it; the receipt and the manifest name
   that kit sha256, its campaign and its frozen commit; the manifest names the plan id, queue, span and
   attempt; the span plan is the kit's (campaign, runner kind, roster, seeds, budgets, redo quota); every
   leg's seed, band, size and G0 shape are the kit's; every consumer's span reference is the roster's first
   leg (the capture leg) at its accepted attempt, names that attempt's run as its source, and carries the
   one reference record hash (the manifest's, when the producer supplies it). A receipt already judged
   under another plan id is refused.
3. **An authenticated receipt.** The bundle arrives as an SSH-signed commit by the controller's key
   (``desk_transport.extract_bundle``), whose trailer names the manifest's sha256; every file the manifest
   lists hashes as listed, nothing else is in the bundle, and the receipt's hash is the one the manifest
   names. A negative or error result is also a receipt: a verdict is written for every outcome.
4. **Feeds.** ``feeds_proven_stopped`` comes from every feed's own stop proof in the receipt (agents,
   meter, volumes), not from the meter's alone. A missing proof is an integrity stop; a proof that says
   not stopped is the named stop INSTRUMENT_FAULT.

**Command results** (the #799 gate, Sol 9). A receipt with a non-zero rc or an error, a missing or failed
restore, or any failed stage (other than a refused soak that was retried, or the runner's non-fatal display
step) is a REFUSAL, which holds the next arm. A span result that contradicts the receipt is not final.

**The soak** (RL-171; Mythos #794 F3). Receipts from the pins with the retry carry ``soak_attempts``: a
refused first soak followed by an accepted retry is a completed soak, never a stop; no accepted soak is a
REFUSAL. Receipts from the development pins (``b4b6aeb19``, ``2d347f721``) carry no such field: one ``soak``
stage with rc 0 is one accepted soak. The refusal text and its kind are kept wherever the receipt gives them.

**The hand table.** It is mandatory on a redo, an exclusion, a retried soak (RL-172a), a schema change, or
when the seeded stratified draw (``hand_sample``) selects the span; until it is supplied the span is not
final (HAND_TABLE_DUE). It must carry every comparable field for every leg; an incomplete or malformed one
is HAND_TABLE_INVALID, and one that disagrees is HAND_TABLE_DISAGREES. Both hold the next arm.

**Hand gates are kept and gate as they do now** (RL-172 section (c)): the class A smoke hand-read of a new
kit's first span, the L002 and L005 consumer gates, and RL-158 Q1's reference print on every v1.1 span.
The desk does not clear them. It prints what each hand check needs and marks it ``hand gate required``.

**Operational finality only.** Inclusion at a look is still RL-166 Q7's interval checks.

**Blinding.** Only ``ALLOWED_BASENAMES`` are ever read, each once (hashed and parsed from the same bytes).
A bundle path outside the bundle layout is refused unread. No energy, power, meter-sample, powermetrics,
transcript or slot file is opened; leg summaries carrying such keys are refused, and the finished text,
summary and verdict are scanned for denied words before anything is written.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import time

from joulewise.cadence import desk
from joulewise.cadence import queue as queuemod
from joulewise.cadence import stops as stopsmod
from joulewise.cadence.stops import evaluate_named_stops

BUNDLE_SCHEMA = "joulewise.cadence_desk_bundle.v1"
VERDICT_SCHEMA = "joulewise.cadence_desk_verdict.v1"
HAND_TABLE_SCHEMA = "joulewise.cadence_hand_table.v1"
RECEIPT_SCHEMA = "joulewise.cadence_span_receipt.v1"      # scripts/cadence_legs_runner.RECEIPT_SCHEMA
PLAN_SCHEMAS = ("joulewise.cadence_span_plan.v1",)         # joulewise.cadence.legs.plan_span
MANIFEST_NAME = "BUNDLE_MANIFEST.json"
RECEIPT_NAME = "runner_receipt.json"
PLAN_NAME = "span_plan.json"
VERDICT_NAME = "desk_verdict.json"
SUMMARY_NAME = "desk_summary.json"
HAND_TABLE_NAME = "hand_table.json"
ALLOWED_BASENAMES = frozenset({MANIFEST_NAME, RECEIPT_NAME, PLAN_NAME, "leg_summary.json", "result.json",
                               "meter.json", HAND_TABLE_NAME, VERDICT_NAME, SUMMARY_NAME})
LEG_ID = r"[A-Za-z0-9][A-Za-z0-9_-]{0,31}"
BUNDLE_PATH_RE = re.compile(rf"{re.escape(RECEIPT_NAME)}|{re.escape(PLAN_NAME)}|legs/({LEG_ID})/leg_summary\.json|"
                            rf"span/result\.json|span/meter\.json")
HEX64 = re.compile(r"[0-9a-f]{64}")
# The runner's production feeds (run_align_r1_smoke.AgentFeed, MeterFeed, VolumeFeed; the mock's FakeFeeds).
EXPECTED_FEEDS = ("agents", "meter", "volumes")
MANIFEST_KEYS = {"schema", "plan_id", "queue_id", "span_id", "attempt", "kit", "receipt", "files", "reference"}
MANIFEST_OPTIONAL = {"producer", "controller"}
KIT_IDENTITY_KEYS = {"path", "sha256", "campaign_id", "frozen_commit"}
REFERENCE_KEYS = {"capture_leg", "attempt", "record_sha256"}
V11_KEYS = {"prefill_tokens", "g0_shape", "g0_role", "span_reference"}
V1_REQUIRED = desk.LEG_SUMMARY_KEYS - V11_KEYS
V11_SCHEMA = "joulewise.cadence_campaign_kit.v1.1"
SOAK_RETRIES = 1     # scripts/cadence_legs_runner.SOAK_RETRIES (RL-171): one retry after a settle or quiet refusal
NON_FATAL_STEPS = ("display",)   # the runner calls display with fatal=False

# Named stops this module adds. "integrity": the automatic table cannot be trusted as final.
INTEGRITY_CODES = ("DESK_DENIED_CONTENT", "DESK_UNAUTHENTICATED", "DESK_IDENTITY", "DESK_ROSTER", "DESK_NO_LEG_ROWS", "DESK_DUPLICATE",
                   "DESK_ATTEMPTS", "DESK_SCHEMA", "DESK_FEED_PROOF", "DESK_REFUSAL", "DESK_ERROR")
HAND_CODES = ("HAND_TABLE_DISAGREES", "HAND_TABLE_INVALID")
PENDING_CODES = ("HAND_TABLE_DUE",)
GATE_REQUIRED = "hand gate required"

# Consumer gates RL-172 keeps by name: (campaign, leg) -> the ruling and what the lead's record decides.
# The controller imports this table (consumer_gates) so that the gate is derived, never typed (Mythos F2).
CONSUMER_GATES = {
    ("cl-dev-03", "L002"): ("L002 consumer gate", "RL-158 section 2 (the pilot's gate on the remainder)",
                            "dev-03's remainder arms on the lead's record only if L002 released its G0; if it "
                            "timed out, nothing span-shaped arms and Q1's print goes to the research lead"),
    ("cl-dev-04", "L005"): ("L005 consumer gate", "RL-163 section 6, amended by RL-165 section 4 and RL-167 "
                            "section 5", "dev-04's second span arms on the lead's record if L005 released its "
                            "G0; if it timed out, it arms only if dev-03 ended with at least four of its five "
                            "consumers released"),
}

# The hand table (Sol 7): every row carries every one of these; seconds compare within the tolerance.
HAND_REQUIRED_V1 = ("leg_id", "attempts", "contaminated_redos", "g0_outcome", "g0_s", "wall_s", "band_reached",
                    "admitted")
HAND_REQUIRED_V11 = HAND_REQUIRED_V1 + ("g0_role", "span_reference")
HAND_TOP_REQUIRED = ("schema", "plan_id", "legs", "named_stops", "soak_attempts")
SECONDS_TOLERANCE = 1.0

# The seeded stratified hand-sample draw (RL-172 section (c); Sol). Fixed here, before any span it selects
# has run. v2 (gate 2, Mythos N13, Sol R11): each span's draw depends only on its own plan id, its kit sha and
# its G0 shape, so appending to a queue never changes an earlier span's draw, and queues of any size draw at
# the same rate. v1's blocks of four were sized by the queue's current length and were not append-stable.
HAND_SAMPLE_LAW = "sha256-hand-sample-v2"
HAND_SAMPLE_SEED = 2026111501
HAND_SAMPLE_RATE = 4       # one span in four per stratum, in expectation

# desk._guard_text's words (whole words, so "joulewise" is not one), plus the leg-summary deny list's names.
_DENIED_WORD = re.compile(r"(?i)\b(\w*energy\w*|joules?|\w*power_w\w*|watts?|slots?|slot_\w+|\w*transcripts?|"
                          r"\w*meter_samples\w*|\w*samples_w\w*|\w*token_ids\w*|\w*output_text\w*|"
                          r"\w*prompt_text\w*|\w*_j|j_\w+)\b")


class _Fatal(Exception):
    """Nothing further can be judged (the expected roster or the bundle is unreadable)."""


# The deny list every bundle file is key-scanned against, on both sides (Mythos N1, Sol R1). The controller
# imports DENYLIST and denied_content() and runs them before it signs; pack_bundle runs them before it writes;
# the Air runs them on every file of the signed tree before it trusts or parses anything else in it.
DENYLIST = desk.DENIED_KEY_RE


class DeniedContent(desk.DeskRefusal):
    """A bundle file carries a denied key (energy, power, meter samples, slot, transcript, token ids)."""


def denied_content(raw, where):
    """Every denied key anywhere in the JSON document ``raw`` (bytes), sorted. A file that is not JSON is
    refused outright (DeniedContent): a bundle carries JSON only, and a non-JSON file cannot be key-scanned."""
    try:
        doc = json.loads(raw)
    except ValueError:
        raise DeniedContent(f"{where}: not JSON, so it cannot be key-scanned") from None
    return sorted({k for k in desk._keys(doc) if DENYLIST.search(k)})


def refuse_denied_content(files):
    """``files`` is {relative path: bytes}. Raises DeniedContent naming each file with a denied key."""
    hits = {rel: denied_content(raw, rel) for rel, raw in sorted(files.items())}
    hits = {rel: keys for rel, keys in hits.items() if keys}
    if hits:
        raise DeniedContent("denied keys in " + "; ".join(f"{rel}: {len(keys)} key(s)" for rel, keys in hits.items()))


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def _sanitize(text, limit=400):
    return _DENIED_WORD.sub("[denied]", str(text))[:limit]


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
        return _loads(raw, Path(path).name), digest


def _unique(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f"duplicate key {k!r}")
        out[k] = v
    return out


def _loads(raw, where):
    try:
        return json.loads(raw, object_pairs_hook=_unique)
    except ValueError as error:
        raise desk.DeskRefusal(f"{where}: not JSON ({_sanitize(error)})") from None


class _Findings:
    def __init__(self):
        self.items = {}

    def add(self, code, detail):
        self.items.setdefault(code, [])
        if detail not in self.items[code]:
            self.items[code].append(detail)

    def stops(self, kind):
        return [{"code": c, "kind": kind, "detail": "; ".join(d)[:2000]} for c, d in self.items.items()]


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


# --------------------------------------------------------------------------
# The bundle: reference packer (what the controller publishes) and the walk
# --------------------------------------------------------------------------
def reference_identity(receipt_doc, roster, record_sha256=None):
    """The manifest's ``reference``: the capture leg (the roster's first), its accepted attempt, and the
    capture's reference record sha256 if the producer has it. None when no leg consumed a span reference."""
    legs = [leg for leg in receipt_doc.get("legs") or [] if isinstance(leg, dict)]
    if not roster or not any(isinstance(leg.get("span_reference"), dict) for leg in legs):
        return None
    capture = next((leg for leg in legs if leg.get("leg_id") == roster[0]), {})
    return {"capture_leg": roster[0], "attempt": len(capture.get("attempts") or []), "record_sha256": record_sha256}


def pack_bundle(span_dir, bundle_dir, *, plan_id, queue_id, span_id, attempt, kit, roster, reference_record_sha256=None,
                producer=None, controller=None):
    """The reference packer: copy the runner's ``runner_receipt.json``, ``span_plan.json`` and its
    ``desk-bundle/`` files into ``bundle_dir`` and write ``BUNDLE_MANIFEST.json``. ``kit`` is the queue entry's
    identity ({path, sha256, campaign_id, frozen_commit}); ``roster`` the queue entry's legs. Returns the
    manifest's sha256. Opens only allowlisted basenames; a desk-bundle path outside the layout is refused
    before anything is read or written."""
    span_dir, bundle_dir = Path(span_dir), Path(bundle_dir)
    reader = _Reader()
    if span_dir.is_symlink() or (span_dir / "desk-bundle").is_symlink():
        raise desk.DeskRefusal("the span output or its desk-bundle is a symlink (not followed)")
    sources = [(span_dir / RECEIPT_NAME, RECEIPT_NAME)]
    if (span_dir / PLAN_NAME).is_file():
        sources.append((span_dir / PLAN_NAME, PLAN_NAME))
    source_root = span_dir / "desk-bundle"
    for root, dirs, names in os.walk(source_root, followlinks=False):
        for d in dirs:
            if (Path(root) / d).is_symlink():
                raise desk.DeskRefusal(f"desk-bundle/{(Path(root) / d).relative_to(source_root).as_posix()} is a "
                                       "symlinked directory (not followed)")
        for name in sorted(names):
            path = Path(root) / name
            rel = path.relative_to(source_root).as_posix()
            if path.is_symlink() or not BUNDLE_PATH_RE.fullmatch(rel) or rel in (RECEIPT_NAME, PLAN_NAME):
                raise desk.DeskRefusal(f"desk-bundle/{rel} is not in the bundle layout (not read)")
            sources.append((path, rel))
    raws = {}
    for path, rel in sources:
        raws[rel] = reader.read(path)[0]
    refuse_denied_content(raws)          # Mythos N1, Sol R1: nothing with a denied key is written or shipped
    bundle_dir.mkdir(parents=True, exist_ok=False)
    files = {}
    receipt_doc = _loads(raws[RECEIPT_NAME], RECEIPT_NAME)
    for rel, raw in raws.items():
        target = bundle_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        files[rel] = sha256_bytes(raw)
    manifest = {"schema": BUNDLE_SCHEMA, "plan_id": plan_id, "queue_id": queue_id, "span_id": span_id,
                "attempt": attempt, "kit": dict(kit), "receipt": {"path": RECEIPT_NAME, "sha256": files[RECEIPT_NAME]},
                "files": dict(sorted(files.items())),
                "reference": reference_identity(receipt_doc or {}, list(roster), reference_record_sha256)}
    if producer is not None:
        manifest["producer"] = producer
    if controller is not None:
        manifest["controller"] = controller
    raw = (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode()
    try:
        refuse_denied_content({MANIFEST_NAME: raw})     # producer/controller objects are free text
    except DeniedContent:
        shutil.rmtree(bundle_dir, ignore_errors=True)    # created above by this call (exist_ok=False)
        raise
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
def span_shape(kit, roster):
    """``span`` when a leg after the roster's first is span-shaped (a consumer), else ``own``."""
    shapes = {leg["leg_id"]: leg.get("g0_shape", "own") for leg in kit["legs"]}
    return "span" if any(shapes.get(x) == "span" for x in roster[1:]) else "own"


def hand_sample(queue_doc, plan_id, kit, kit_sha256):
    """The seeded stratified draw (``sha256-hand-sample-v2``). The stratum is (kit sha256, G0 shape of the
    span); the span is selected when sha256 of the law, the seed, the stratum and its plan id is 0 modulo
    HAND_SAMPLE_RATE. It reads only the span's own committed queue entry and kit, so it is prospective
    (``cadence_desk.py sample-plan`` prints it at READY) and an append never changes it (Mythos N13, Sol R11)."""
    span = next((s for s in queue_doc["spans"] if queuemod.plan_id(s) == plan_id), None)
    if span is None or span["kit"]["sha256"] != kit_sha256:
        return None
    shape = span_shape(kit, span["legs"])
    digest = hashlib.sha256(f"{HAND_SAMPLE_LAW}|{HAND_SAMPLE_SEED}|{kit_sha256}|{shape}|{plan_id}".encode()).hexdigest()
    value = int(digest, 16) % HAND_SAMPLE_RATE
    return {"law": HAND_SAMPLE_LAW, "seed": HAND_SAMPLE_SEED, "stratum": {"kit_sha256": kit_sha256, "shape": shape},
            "rate": HAND_SAMPLE_RATE, "value": value, "selected": value == 0}


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
            "kit_legs": {leg["leg_id"]: leg for leg in kit["legs"]},
            "sample": hand_sample(queue_doc, plan_id, kit, span["kit"]["sha256"])}


# --------------------------------------------------------------------------
# Condition 3: authentication
# --------------------------------------------------------------------------
def authenticate(bundle_dir, manifest_sha256, expected, reader, find):
    """Verify the manifest against the anchor and every file against the manifest. Returns
    (manifest, manifest sha256, {rel: verified bytes})."""
    bundle_dir = Path(bundle_dir)
    if not (bundle_dir / MANIFEST_NAME).is_file():
        find.add("DESK_UNAUTHENTICATED", f"no {MANIFEST_NAME}")
        raise _Fatal()
    raw_manifest, digest = reader.read(bundle_dir / MANIFEST_NAME)
    if denied_content(raw_manifest, MANIFEST_NAME):
        find.add("DESK_DENIED_CONTENT", f"{MANIFEST_NAME} carries denied keys (nothing else is read)")
        raise _Fatal()
    manifest = _loads(raw_manifest, MANIFEST_NAME)
    if not (isinstance(manifest_sha256, str) and HEX64.fullmatch(manifest_sha256)):
        find.add("DESK_UNAUTHENTICATED", "no manifest anchor (the signed bundle commit's Manifest-SHA256 trailer)")
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
    ref = manifest.get("reference")
    if ref is not None and not (isinstance(ref, dict) and set(ref) == REFERENCE_KEYS
                                and (ref["record_sha256"] is None or (isinstance(ref["record_sha256"], str)
                                                                      and HEX64.fullmatch(ref["record_sha256"])))):
        find.add("DESK_IDENTITY", "manifest reference: null or {capture_leg, attempt, record_sha256}")
    for key in MANIFEST_OPTIONAL:
        bad = [k for k in desk._keys(manifest.get(key) or {}) if desk.DENIED_KEY_RE.search(k)]
        if bad:
            raise desk.DeskRefusal(f"manifest {key} carries denied keys")
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
    denied = {rel: denied_content(raw, rel) for rel, raw in verified.items()}
    denied = {rel: keys for rel, keys in denied.items() if keys}
    if denied:   # Mythos N1, Sol R1: refuse before any file is parsed, projected or printed
        find.add("DESK_DENIED_CONTENT", "denied keys in " + ", ".join(sorted(denied)) + " (not parsed)")
        raise _Fatal()
    if RECEIPT_NAME not in verified:
        find.add("DESK_UNAUTHENTICATED", "no runner receipt in the bundle")
        raise _Fatal()
    return manifest, digest, verified


# --------------------------------------------------------------------------
# The receipt, projected (operational fields only)
# --------------------------------------------------------------------------
_ATTEMPT_KEYS = ("attempt", "redone", "contaminated", "output_dir", "leg_status", "redo_reason")
_LEG_RESULT_KEYS = ("leg_id", "bundle", "g0_role", "g0_shape", "g0_outcome", "leg_status", "g0_reference_source",
                    "g0_reference_record_sha256")


def refusal_kind(text):
    """The soak refusal's kind, as far as the receipt's text gives it (RL-172a's look print)."""
    t = str(text or "").lower()
    if "slope" in t:
        return "slope"
    if "load" in t:
        return "load"
    if "no retry" in t:
        return "settle_or_quiet; no retry budget"
    if "settle or quiet" in t:
        return "settle_or_quiet"
    return "unspecified"


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
            row["has_result"] = isinstance(step.get("result"), dict)
        if "leg_id" in result:     # a leg runtime's result (v1 legs carry no g0_role)
            row["leg"] = {k: result.get(k) for k in _LEG_RESULT_KEYS}
        steps.append(row)
    feeds = {}
    for name, feed in (doc.get("feeds") or {}).items():
        stop = feed.get("stop") if isinstance(feed, dict) else None
        feeds[name] = ({"rc": stop.get("rc"), "proven_stopped": stop.get("proven_stopped")}
                       if isinstance(stop, dict) else None)
    error = doc.get("error")
    soak = None
    if "soak_attempts" in doc:   # absent on the development pins' runners (b4b6aeb19, 2d347f721)
        soak = [{"attempt": a.get("attempt"), "refused": bool(a.get("refused")), "output_dir": a.get("output_dir"),
                 "refusal": _sanitize(a.get("refused"), 200) if a.get("refused") else None,
                 "refusal_kind": refusal_kind(a.get("refused")) if a.get("refused") else None}
                if isinstance(a, dict) else {} for a in (doc.get("soak_attempts") or [])]
    out = {"schema": doc.get("schema"), "runner_kind": doc.get("runner_kind"), "mock": doc.get("mock"),
           "kit": doc.get("kit"), "roster": doc.get("roster"), "rc": doc.get("rc"),
           "error_type": str(error).split(":", 1)[0][:80] if error else None,
           "span_result": doc.get("span_result"), "meter": doc.get("meter"),
           "legs_finished": doc.get("legs_finished"), "legs_planned": doc.get("legs_planned"),
           "load_redos_used": doc.get("load_redos_used"), "legs": legs, "steps": steps, "feeds": feeds,
           "soak_attempts": soak, "soak_field": "soak_attempts" in doc,
           "desk_bundle_error": bool(doc.get("desk_bundle_error"))}
    bad = [k for k in desk._keys(out) if desk.DENIED_KEY_RE.search(k)]
    if bad:
        raise desk.DeskRefusal(f"runner_receipt.json projection carries denied keys {sorted(set(bad))[:5]}")
    return out


# --------------------------------------------------------------------------
# Conditions 1, 2 and 4 on the parsed bundle
# --------------------------------------------------------------------------
def check_receipt_identity(receipt, receipt_sha, expected, allow_mock, history, find):
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
    # Mythos F17: the receipt does not name its plan id, so a receipt already judged under another plan id
    # (a span output relabelled as a re-run) is refused.
    for past in history or ():
        if isinstance(past, dict) and past.get("receipt_sha256") == receipt_sha and past.get("plan_id") != expected[
                "plan_id"]:
            find.add("DESK_IDENTITY", f"this receipt was already judged under {past.get('plan_id')}")


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


def check_plan(verified, expected, find):
    """The span plan (``span_plan.json``) binds the plan identity: the kit's campaign and runner kind, the
    roster, each leg's seed, band, size and budget, and the redo quota."""
    if PLAN_NAME not in verified:
        find.add("DESK_IDENTITY", f"no {PLAN_NAME} in the bundle")
        return None
    plan = _loads(verified[PLAN_NAME], PLAN_NAME)
    if not isinstance(plan, dict) or not isinstance(plan.get("legs"), list):
        find.add("DESK_IDENTITY", f"{PLAN_NAME}: not a span plan")
        return None
    bad = [k for k in desk._keys(plan) if desk.DENIED_KEY_RE.search(k)]
    if bad:
        raise desk.DeskRefusal(f"{PLAN_NAME} carries denied keys")
    if plan.get("schema") not in PLAN_SCHEMAS:
        find.add("DESK_IDENTITY", f"{PLAN_NAME} schema {plan.get('schema')!r}")
    for key, want in (("campaign_id", expected["kit"]["campaign_id"]), ("runner_kind", expected["runner_kind"]),
                      ("redo_quota", expected["redo_quota"])):
        if plan.get(key) != want:
            find.add("DESK_IDENTITY", f"{PLAN_NAME} {key} {plan.get(key)!r} is not the kit's {want!r}")
    ids = [leg.get("leg_id") if isinstance(leg, dict) else None for leg in plan["legs"]]
    if ids != expected["roster"]:
        find.add("DESK_ROSTER", f"{PLAN_NAME} legs {ids} are not the queue's roster {expected['roster']}")
    for leg in plan["legs"]:
        if not isinstance(leg, dict):
            continue
        kit_leg = expected["kit_legs"].get(leg.get("leg_id")) or {}
        for key in ("seed", "start_band", "prefill_tokens"):
            if key in kit_leg and leg.get(key) != kit_leg.get(key):
                find.add("DESK_IDENTITY", f"{PLAN_NAME} {leg.get('leg_id')}.{key} is not the kit's")
    return {leg.get("leg_id"): leg for leg in plan["legs"] if isinstance(leg, dict)}


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
        for k in range(1, n + 1):     # Sol R5: every attempt has exactly one command result, rc 0, for this leg
            stages = [s for s in receipt["steps"] if s.get("name") == f"{leg_id}.a{k}"]
            if len(stages) != 1:
                find.add("DESK_ATTEMPTS", f"{leg_id} attempt {k}: {len(stages)} {leg_id}.a{k} stages in the receipt")
            elif stages[0].get("rc") != 0 or (stages[0].get("leg") or {}).get("leg_id") != leg_id:
                find.add("DESK_ATTEMPTS", f"{leg_id} attempt {k}: the {leg_id}.a{k} stage is not this leg's clean result")
        redone_total += n - 1
        if row.get("attempts") != n:
            find.add("DESK_ATTEMPTS", f"{leg_id}: summary attempts {row.get('attempts')!r}, receipt {n}")
        contaminated = sum(1 for a in attempts if a.get("contaminated") is True)
        if row.get("contaminated_redos") != contaminated:
            find.add("DESK_ATTEMPTS", f"{leg_id}: summary contaminated_redos {row.get('contaminated_redos')!r}, "
                                      f"receipt {contaminated}")
    known = {f"{r['leg_id']}.a{k}" for r in ordered
             for k in range(1, len((by_id.get(r["leg_id"]) or {}).get("attempts") or []) + 1)}
    stray = sorted(s["name"] for s in receipt["steps"] if isinstance(s.get("name"), str)
                   and re.fullmatch(rf"{LEG_ID}\.a\d+", s["name"]) and not s["name"].startswith("soak")
                   and s["name"] not in known)
    if stray:
        find.add("DESK_ATTEMPTS", f"leg stages with no attempt record: {stray[:5]}")
    if receipt["load_redos_used"] != redone_total:
        find.add("DESK_ATTEMPTS", f"receipt load_redos_used {receipt['load_redos_used']!r}, kept redos {redone_total}")
    if redone_total > expected["redo_quota"]:
        find.add("DESK_ATTEMPTS", f"{redone_total} redos over the kit's quota {expected['redo_quota']}")


def _accepted_step(receipt, leg_id, n):
    return next((s for s in receipt["steps"] if s.get("name") == f"{leg_id}.a{n}"), None)


def check_kit_legs(ordered, receipt, expected, plan_legs, manifest_ref, find):
    """Each row is the kit's leg (seed, band, budget, size, G0 shape and role); each consumer's reference is
    the roster's first leg at its accepted attempt and names that attempt's run as its source; consumers
    carry one reference record hash, the manifest's when it gives one (Sol 1)."""
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
        if plan_legs is not None and row.get("budget_s") != (plan_legs.get(leg_id) or {}).get("budget_s"):
            find.add("DESK_IDENTITY", f"{leg_id}: budget_s is not the span plan's")
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
    if not v11:
        return
    consumers = [r["leg_id"] for r in ordered if r.get("g0_role") == "consume"]
    if not consumers:
        if manifest_ref is not None:
            find.add("DESK_IDENTITY", "the manifest names a span reference but no leg consumed one")
        return
    n = len((receipt_legs.get(capture) or {}).get("attempts") or [])
    capture_step = _accepted_step(receipt, capture, n)
    capture_run = Path(((capture_step or {}).get("leg") or {}).get("bundle") or "").name or None
    hashes, sources = {}, {}
    for c in consumers:
        step = _accepted_step(receipt, c, len((receipt_legs.get(c) or {}).get("attempts") or []))
        leg = (step or {}).get("leg") or {}
        hashes[c], sources[c] = leg.get("g0_reference_record_sha256"), leg.get("g0_reference_source")
    values = set(hashes.values())
    if len(values) != 1 or not all(isinstance(v, str) and HEX64.fullmatch(v) for v in values):
        find.add("DESK_IDENTITY", f"consumers do not carry one reference record sha256 ({len(values)} values)")
    if capture_run is None or any(s != capture_run for s in sources.values()):
        find.add("DESK_IDENTITY", f"consumers' reference source {sorted(set(map(str, sources.values())))} is not the "
                                  f"capture's accepted run {capture_run!r}")
    if manifest_ref is None:
        find.add("DESK_IDENTITY", "consumers ran but the manifest names no span reference")
        return
    if manifest_ref.get("capture_leg") != capture or manifest_ref.get("attempt") != n:
        find.add("DESK_IDENTITY", f"manifest reference {manifest_ref.get('capture_leg')} attempt "
                                  f"{manifest_ref.get('attempt')} is not the capture leg {capture} attempt {n}")
    if manifest_ref.get("record_sha256") is not None and values != {manifest_ref["record_sha256"]}:
        find.add("DESK_IDENTITY", "consumers' reference record sha256 is not the capture's record in the manifest")


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


def _soak_stage(k):
    return "soak" if k == 1 else f"soak.a{k}"


def check_soak(receipt, find):
    """The soak (RL-171; Mythos #794 F3, #799 F3; Sol 9 and 13). Returns (accepted attempt or None, attempts as
    judged, note). With ``soak_attempts`` (the pins with the retry): attempts are numbered 1..n, n <= 1 +
    SOAK_RETRIES; each has its stage (``soak``, ``soak.a<k>``) with rc 0 exactly when it was accepted; a refused
    attempt that was retried is kept as ``soak.rejected<k>``; the accepted one as ``soak``. Without the field
    (the development pins): exactly one ``soak`` stage and no retry stage; rc 0 is one accepted soak."""
    step_rc = {}
    for step in receipt["steps"]:
        step_rc.setdefault(step.get("name"), step.get("rc"))
    stages = sorted(n for n in step_rc if isinstance(n, str) and re.fullmatch(r"soak(\.a\d+)?", n))
    attempts = receipt["soak_attempts"]
    if attempts is None:
        if any(n != "soak" for n in stages):
            find.add("DESK_ATTEMPTS", f"soak retry stages {stages} but no soak_attempts in the receipt")
        if "soak" not in step_rc:
            return None, [], "no soak stage (legacy receipt: no soak_attempts field)"
        ok = step_rc["soak"] == 0
        judged = [{"attempt": 1, "refused": not ok, "output_dir": "soak", "refusal": None if ok else
                   f"soak stage rc {step_rc['soak']}", "refusal_kind": None if ok else "unspecified"}]
        return (1, judged, "accepted attempt 1 (legacy receipt: no soak_attempts field)") if ok else \
            (None, judged, f"no soak accepted (legacy receipt: soak stage rc {step_rc['soak']})")
    if not attempts:
        return None, [], "no soak attempt recorded"
    if len(attempts) > 1 + SOAK_RETRIES:
        find.add("DESK_ATTEMPTS", f"{len(attempts)} soak attempts; the runner allows {1 + SOAK_RETRIES}")
    extra = [n for n in stages if n not in {_soak_stage(k) for k in range(1, len(attempts) + 1)}]
    if extra:
        find.add("DESK_ATTEMPTS", f"soak stages {extra} have no soak attempt record")
    accepted = None
    for k, a in enumerate(attempts, start=1):
        last = k == len(attempts)
        stage = _soak_stage(k)
        if a.get("attempt") != k:
            find.add("DESK_ATTEMPTS", f"soak attempt {k} is numbered {a.get('attempt')!r}")
        if not last and (a.get("refused") is not True or a.get("output_dir") != f"soak.rejected{k}"):
            find.add("DESK_ATTEMPTS", f"soak attempt {k} was retried but is not kept as a refused soak.rejected{k}")
        if stage not in step_rc:
            find.add("DESK_ATTEMPTS", f"soak attempt {k}: no {stage} stage in the receipt")
        elif (step_rc[stage] == 0) == bool(a.get("refused")):
            find.add("DESK_ATTEMPTS", f"soak attempt {k}: stage {stage} rc {step_rc[stage]} disagrees with "
                                      f"refused={a.get('refused')}")
        if last and not a.get("refused"):
            if a.get("output_dir") != "soak":
                find.add("DESK_ATTEMPTS", f"the accepted soak is kept as {a.get('output_dir')!r}, not soak")
            if step_rc.get(stage) == 0:
                accepted = k
    refused = [a for a in attempts if a.get("refused")]
    kinds = ", ".join(str(a.get("refusal_kind")) for a in refused)
    if accepted is None:
        return None, attempts, f"no soak accepted ({len(refused)} refused: {kinds})"
    return accepted, attempts, (f"accepted attempt {accepted} after {len(refused)} refused ({kinds}; retry)"
                                if refused else "accepted attempt 1")


def _retried_soak(step, receipt):
    attempts = receipt["soak_attempts"] or []
    name = step.get("name") or ""
    k = 1 if name == "soak" else int(name[6:]) if re.fullmatch(r"soak\.a\d+", name) else None
    return k is not None and k < len(attempts) and bool(attempts[k - 1].get("refused"))


def command_failures(receipt, result, soak_accepted, soak_note, find):
    """Sol 9: the receipt's own command results. Returns REFUSAL details (each holds the next arm)."""
    out = []
    if receipt["rc"] != 0:
        out.append(f"receipt rc {receipt['rc']!r}" + (f" ({receipt['error_type']})" if receipt["error_type"] else ""))
    elif receipt["error_type"]:
        out.append(f"receipt error ({receipt['error_type']}) with rc 0")
    if receipt["desk_bundle_error"]:
        out.append("the runner could not write its desk bundle")
    restore = [s for s in receipt["steps"] if s.get("name") == "restore"]
    if len(restore) != 1:
        find.add("DESK_SCHEMA", f"{len(restore)} restore steps in the receipt (one is required)")
        out.append("restore unproven (no restore step)")
    elif restore[0].get("rc") != 0 or not restore[0].get("has_result"):
        out.append(f"restore unproven (rc {restore[0].get('rc')!r})")
    for s in receipt["steps"]:
        name, rc = s.get("name"), s.get("rc")
        if rc == 0 or name == "restore" or _retried_soak(s, receipt):
            continue
        if name in NON_FATAL_STEPS:
            continue
        out.append(f"step {name} rc {rc!r}")
    if soak_accepted is None:
        out.append(soak_note)
    if isinstance(result, dict) and result.get("chain_exit_code") != receipt["rc"]:
        find.add("DESK_SCHEMA", f"span result chain_exit_code {result.get('chain_exit_code')!r} contradicts the "
                                f"receipt rc {receipt['rc']!r}")
    return out


def check_transition(transition, expected, verified, queue_path, find):
    """The controller's signed per-span transition record (FORMAT section 1): it names this span, its kit, the
    queue bytes it armed from, and the span plan's sha256. Returns REFUSAL details (a close that was not
    CLOSED_OK)."""
    for key in ("plan_id", "queue_id", "span_id", "attempt"):
        if transition.get(key) != expected[key]:
            find.add("DESK_IDENTITY", f"transition {key} {transition.get(key)!r} is not the queue's {expected[key]!r}")
    if (transition.get("kit") or {}).get("sha256") != expected["kit"]["sha256"]:
        find.add("DESK_IDENTITY", "transition kit sha256 is not the queue's pin")
    queue_sha = sha256_bytes(Path(queue_path).read_bytes())
    if (transition.get("queue") or {}).get("sha256") != queue_sha:
        find.add("DESK_IDENTITY", "the queue file is not the one the transition record armed from")
    plan_raw = verified.get(PLAN_NAME)
    if plan_raw is None or transition.get("plan_sha256") != sha256_bytes(plan_raw):
        find.add("DESK_IDENTITY", "span_plan.json is not the plan the transition record names")
    status = transition.get("status")
    return [] if status == "CLOSED_OK" else [f"controller close status {_sanitize(status, 40)}"]


# --------------------------------------------------------------------------
# Hand table and hand gates
# --------------------------------------------------------------------------
def hand_table_triggers(ordered, expected, history, hand_sample_flag, soak_attempts):
    """RL-172 section (c) and RL-172a: the hand table is always taken on a span with a redo, an exclusion, a
    retried soak or a schema change, and on a span the seeded draw (or the lead) selects."""
    out = []
    redos = [r["leg_id"] for r in ordered if (r.get("attempts") or 1) > 1]
    if redos:
        out.append(f"redo ({', '.join(redos)})")
    excluded = [r["leg_id"] for r in ordered if r.get("admitted") is not True]
    if excluded:
        out.append(f"exclusion ({', '.join(excluded)})")
    refused = [a for a in soak_attempts or [] if a.get("refused")]
    if refused:
        out.append(f"retried soak ({', '.join(str(a.get('refusal_kind')) for a in refused)}; RL-172a)")
    keys = sorted(set().union(*(set(r) for r in ordered))) if ordered else []
    previous = next((h for h in reversed(list(history or [])) if isinstance(h, dict)), None)
    if previous is None:
        out.append("schema change (no earlier desk summary in the history)")
    elif previous.get("kit_schema") != expected["kit_schema"] or previous.get("leg_keys") != keys:
        out.append("schema change (kit schema or leg-summary fields differ from the previous span's)")
    sample = expected.get("sample")
    if sample and sample["selected"]:
        out.append(f"sampled (seeded draw {HAND_SAMPLE_LAW})")
    if hand_sample_flag:
        out.append("sampled (the lead's selection)")
    return out, keys


def _same(key, a, b):
    if key in ("g0_s", "wall_s") and _num(a) and _num(b):
        return abs(a - b) <= SECONDS_TOLERANCE
    if key == "span_reference":
        if isinstance(a, dict) and isinstance(b, dict):
            return all(a.get(k) == b.get(k) for k in ("leg_id", "attempt", "redone", "excluded"))
        return a is None and b is None
    return a == b


def _hand_value_ok(key, v):
    if key in ("attempts",):
        return type(v) is int and v >= 1
    if key == "contaminated_redos":
        return type(v) is int and v >= 0
    if key in ("g0_s", "wall_s"):
        return v is None or _num(v)
    if key in ("band_reached", "admitted"):
        return type(v) is bool
    if key in ("g0_outcome", "g0_role", "leg_id"):
        return isinstance(v, str) and v != ""
    if key == "span_reference":
        return v is None or (isinstance(v, dict) and set(v) == {"leg_id", "attempt", "redone", "excluded"}
                             and isinstance(v.get("leg_id"), str) and type(v.get("attempt")) is int
                             and type(v.get("redone")) is bool and type(v.get("excluded")) is bool)
    return True


def validate_hand_table(doc, plan_id, v11):
    """Sol 7: a hand table carries every comparable field for every leg; anything less is invalid."""
    problems = []
    if not isinstance(doc, dict):
        return ["hand table: not an object"]
    missing = [k for k in HAND_TOP_REQUIRED if k not in doc]
    if missing:
        problems.append(f"hand table: missing {missing}")
    if doc.get("schema") != HAND_TABLE_SCHEMA:
        problems.append(f"hand table schema is not {HAND_TABLE_SCHEMA}")
    if doc.get("plan_id") != plan_id:
        problems.append(f"hand table is for {doc.get('plan_id')!r}, not {plan_id}")
    if not (isinstance(doc.get("named_stops"), list) and all(isinstance(x, str) for x in doc["named_stops"])):
        problems.append("hand table named_stops: a list of codes")
    if type(doc.get("soak_attempts")) is not int or doc.get("soak_attempts", 0) < 0:
        problems.append("hand table soak_attempts: the count of soak attempts")
    legs = doc.get("legs")
    if not (isinstance(legs, list) and legs):
        return problems + ["hand table legs: a non-empty list"]
    required = HAND_REQUIRED_V11 if v11 else HAND_REQUIRED_V1
    seen = set()
    for i, row in enumerate(legs):
        if not isinstance(row, dict):
            problems.append(f"hand row {i}: not an object")
            continue
        lid = row.get("leg_id")
        if lid in seen:
            problems.append(f"hand row {lid}: duplicate")
        seen.add(lid)
        absent = [k for k in required if k not in row]
        if absent:
            problems.append(f"hand row {lid}: missing {absent}")
        bad = [k for k in required if k in row and not _hand_value_ok(k, row[k])]
        if bad:
            problems.append(f"hand row {lid}: invalid {bad}")
    return problems


def compare_hand_table(doc, ordered, operational_stops, soak_attempts, plan_id, v11):
    """Returns (problems, differences). Problems make the table invalid; differences are disagreements."""
    if not isinstance(doc, dict):
        return ["hand table: not an object"], []
    if [k for k in desk._keys(doc) if desk.DENIED_KEY_RE.search(k)]:
        raise desk.DeskRefusal("hand_table.json carries denied keys")
    problems = validate_hand_table(doc, plan_id, v11)
    if problems:
        return problems, []
    diffs = []
    hand_ids = [h.get("leg_id") for h in doc["legs"]]
    auto_ids = [r["leg_id"] for r in ordered]
    if hand_ids != auto_ids:
        diffs.append(f"legs: hand {hand_ids}, automatic {auto_ids}")
    auto = {r["leg_id"]: r for r in ordered}
    for h in doc["legs"]:
        a = auto.get(h["leg_id"])
        if a is None:
            continue
        for key in (HAND_REQUIRED_V11 if v11 else HAND_REQUIRED_V1)[1:]:
            if not _same(key, h[key], a.get(key)):
                diffs.append(f"{h['leg_id']}.{key}: hand {h[key]!r}, automatic {a.get(key)!r}")
    hand_codes = sorted(doc["named_stops"])
    auto_codes = sorted(s["code"] for s in operational_stops)
    if hand_codes != auto_codes:
        diffs.append(f"named stops: hand {hand_codes}, automatic {auto_codes}")
    if doc["soak_attempts"] != len(soak_attempts or []):
        diffs.append(f"soak attempts: hand {doc['soak_attempts']}, automatic {len(soak_attempts or [])}")
    return [], diffs


def consumer_gates(campaign_id, kit_legs, roster):
    """The consumer gates that apply to a span: [(name, leg_id, ruling, rule)]. For the controller too (F2)."""
    out = []
    for (gate_campaign, leg_id), (name, ruling, rule) in CONSUMER_GATES.items():
        if campaign_id == gate_campaign and leg_id in roster and (kit_legs.get(leg_id) or {}).get("g0_shape") == "span":
            out.append((name, leg_id, ruling, rule))
    return out


def hand_gates(ordered, receipt, expected, mark):
    """The hand gates RL-172 keeps, with what each hand check needs. The desk never clears one."""
    gates = []
    campaign = expected["kit"]["campaign_id"]
    roster = expected["roster"]
    steps = receipt["steps"]
    soak = receipt["soak_attempts"] or []
    if expected["kit_first_leg"] in roster:
        gates.append({
            "gate": "class A smoke hand-read", "status": GATE_REQUIRED,
            "ruling": "RL-150 R5; RL-149 section 2.9 item 3; RL-172 section (c)",
            "holds": f"kit:{campaign}",
            "why": f"this span runs the kit's first leg {expected['kit_first_leg']} (the new kit's first span)",
            "print": {"steps": len(steps),
                      "steps_nonzero": [s["name"] + (" (refused soak, retried)" if _retried_soak(s, receipt) else "")
                                        for s in steps if s.get("rc") != 0],
                      "soak_attempts": soak,
                      "restore": next(({"rc": s.get("rc"), "action": s.get("action")} for s in steps
                                       if s.get("name") == "restore"), None),
                      "feeds": receipt["feeds"], "result": receipt["span_result"]}})
    rows = {r["leg_id"]: r for r in ordered}
    for name, leg_id, ruling, rule in consumer_gates(campaign, expected["kit_legs"], roster):
        row = rows.get(leg_id) or {}
        gates.append({"gate": name, "status": GATE_REQUIRED, "ruling": ruling, "holds": f"kit:{campaign}",
                      "why": rule,
                      "print": {"leg_id": leg_id, "g0_role": row.get("g0_role"),
                                "g0_outcome": row.get("g0_outcome"), "g0_s": row.get("g0_s"),
                                "admitted": row.get("admitted")}})
    if expected["kit_schema"] == V11_SCHEMA:
        capture = roster[0] if roster else None
        accepted = next((s.get("output_dir") for s in reversed(soak) if not s.get("refused")), None)
        gates.append({
            "gate": "RL-158 Q1 reference print", "status": GATE_REQUIRED, "ruling": "RL-158 Q1; RL-172 section (c)",
            "holds": None,
            "why": "every v1.1 span: the leg summary does not carry the readings (thermal journal values, as "
                   "RL-150 R1 part 3); it becomes automatic only on the research lead's ruling",
            "print": {"soak_reference": {"dir": accepted, "attempts": len(soak),
                                         "refusals": [a.get("refusal_kind") for a in soak if a.get("refused")]},
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


def canonical_sha256(doc):
    return sha256_bytes(json.dumps(doc, sort_keys=True, separators=(",", ":")).encode())


def _finish(verdict):
    verdict["verdict_sha256"] = canonical_sha256({k: v for k, v in verdict.items() if k != "verdict_sha256"})
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
               hand_table_path=None, hand_sample=False, allow_mock=False, transport=None, allow_unsigned=False,
               history_source="file", refusal=None, refusal_code="DESK_UNAUTHENTICATED", now=None):
    """Judge one span's bundle. Always writes ``desk_verdict.json`` to ``out_dir`` (a negative or error
    result is also a receipt); writes ``JOURNAL-TABLE.md``, ``desk_summary.json`` and ``stops.json`` when the
    bundle could be read. ``transport`` is ``desk_transport.extract_bundle``'s record of the signed commit;
    without one the bundle is unsigned and never final unless ``allow_unsigned`` (synthetic tests only).
    Returns the verdict."""
    from joulewise.cadence import kit as kitmod
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    find, reader = _Findings(), _Reader()
    expected, operational, gates, hand = None, [], [], {"required": False, "triggers": [], "supplied": False,
                                                         "agrees": None, "problems": [], "differences": [],
                                                         "sample": None}
    identities, error, mock = {"manifest_sha256": None, "receipt_sha256": None}, None, None
    text = summary = summary_text = None
    transport = dict(transport) if transport else {"signed": False, "bundle_commit": None, "signer": None}
    if not transport.get("signed") and not allow_unsigned:
        find.add("DESK_UNAUTHENTICATED", "the bundle is not a verified signed commit (desk_transport.extract_bundle)")
    if history_source != "signed-records" and not allow_unsigned:   # Mythos N11, Sol R8
        find.add("DESK_UNAUTHENTICATED", f"history from {history_source!r}, not the signed verdict records "
                                         "(--history-prefix): receipt replay cannot be checked")
    if refusal is not None:     # the signed transport refused: nothing in the bundle is read
        find.add(refusal_code if refusal_code in INTEGRITY_CODES else "DESK_UNAUTHENTICATED", _sanitize(refusal))
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
        hand["sample"] = expected["sample"]
        identities.update(kit_sha256=kit_sha, campaign_id=kit["campaign_id"], frozen_commit=kit["frozen"]["commit"],
                          roster=expected["roster"], capture_leg=expected["roster"][0] if expected["roster"] else None)
        if refusal is not None:
            raise _Fatal()
        manifest, manifest_digest, verified = authenticate(bundle_dir, manifest_sha256, expected, reader, find)
        receipt_sha = sha256_bytes(verified[RECEIPT_NAME])
        identities.update(manifest_sha256=manifest_digest, receipt_sha256=receipt_sha)
        receipt = project_receipt(_loads(verified[RECEIPT_NAME], RECEIPT_NAME))
        mock = receipt["mock"]
        check_receipt_identity(receipt, receipt_sha, expected, allow_mock, history, find)
        plan_legs = check_plan(verified, expected, find)
        rows = load_rows(verified, find)
        ordered = check_roster(rows, receipt, expected, find)
        check_schema(ordered, receipt, expected, find)
        check_attempts(ordered, receipt, expected, find)
        check_kit_legs(ordered, receipt, expected, plan_legs, manifest.get("reference"), find)
        result, meter = check_span_files(verified, receipt, find)
        proven, proofs = feed_proofs(receipt, meter, find)
        soak_accepted, soak_attempts, soak_note = check_soak(receipt, find)
        failures = command_failures(receipt, result, soak_accepted, soak_note, find)
        controller = manifest.get("controller") if isinstance(manifest.get("controller"), dict) else {}
        if controller.get("status") not in (None, "CLOSED_OK"):
            failures.append(f"controller close status {_sanitize(controller.get('status'), 40)}")
        transition = transport.get("transition")
        if transition is not None:
            failures += check_transition(transition, expected, verified, queue_path, find)
        triggers, leg_keys = hand_table_triggers(ordered, expected, history, hand_sample, soak_attempts)
        mark = desk.span_reference_marks(ordered)
        summary = {"plan_id": plan_id, "adapter": "leg-summary-v1", "result": result, "meter": meter,
                   "feeds_proven_stopped": proven, "feeds": proofs, "legs": ordered,
                   "kit_schema": expected["kit_schema"], "leg_keys": leg_keys,
                   "receipt_sha256": receipt_sha, "manifest_sha256": manifest_digest,
                   "campaign_id": kit["campaign_id"],
                   "first_leg_start_epoch_s": ordered[0].get("started_epoch_s") if ordered else None,
                   "soak": {"attempts": soak_attempts, "accepted_attempt": soak_accepted, "note": soak_note,
                            "field": receipt["soak_field"]}}
        if mark is not None:
            summary["span_reference"] = mark
        operational = [{**s, "kind": "operational"} for s in evaluate_named_stops(kit["stop_rules"], summary, history)]
        if failures:
            refusal = next((s for s in operational if s["code"] == "REFUSAL"), None)
            if refusal is None:
                operational.insert(0, {"code": "REFUSAL", "detail": "; ".join(failures), "kind": "operational"})
            else:
                refusal["detail"] += "; " + "; ".join(failures)
        hand.update(required=bool(triggers), triggers=triggers)
        if hand_table_path is not None:
            doc, _ = reader.json(hand_table_path)
            hand.update(supplied=True)
            problems, diffs = compare_hand_table(doc, ordered, operational, soak_attempts, plan_id,
                                                 expected["kit_schema"] == V11_SCHEMA)
            hand.update(agrees=None if problems else not diffs, problems=problems[:50], differences=diffs[:50])
            if problems:
                find.add("HAND_TABLE_INVALID", "; ".join(problems[:10]))
            elif diffs:
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
                  f"- bundle commit {str(transport.get('bundle_commit'))[:12]} signed by {transport.get('signer')}; "
                  f"manifest sha256 {manifest_digest[:12]}; receipt sha256 {receipt_sha[:12]}",
                  f"- soak (RL-171 retry): {soak_note}",
                  "- feeds (each feed's own stop proof): "
                  + ", ".join(f"{n} {'proven' if p['proven_stopped'] else 'NOT proven'}" for n, p in proofs.items()),
                  f"- hand table: {'required (' + '; '.join(triggers) + ')' if triggers else 'not required'}"
                  + (f"; supplied, {'INVALID' if hand['problems'] else 'agrees' if hand['agrees'] else 'DISAGREES'}"
                     if hand["supplied"] else ""),
                  f"- seeded draw: {json.dumps(expected['sample'], sort_keys=True)}"]
        lines += _gate_lines(gates)
        lines += ["", "## Receipt", "",
                  f"- rc {receipt['rc']}{'; error ' + receipt['error_type'] if receipt['error_type'] else ''}; "
                  f"steps {len(receipt['steps'])}, non-zero: "
                  + (', '.join(s['name'] + (' (refused soak, retried)' if _retried_soak(s, receipt) else '')
                               for s in receipt['steps'] if s.get('rc') != 0) or 'none'),
                  f"- soak: {soak_note}; attempts {json.dumps(soak_attempts, sort_keys=True)}",
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
        "transport": {**{k: transport.get(k) for k in ("signed", "bundle_commit", "signer")},
                      "queue_commit": ((transport.get("transition") or {}).get("queue") or {}).get("commit")},
        "history_source": history_source,
        "summary_sha256": canonical_sha256(summary) if summary is not None else None,
        "opened": [Path(p).name for p in reader.opened], "error": error,
        "desk_code": _code_identity(),
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(now))}))
    for name in ("JOURNAL-TABLE.md", SUMMARY_NAME, "stops.json"):   # no stale table beside a new verdict
        if text is None and (out / name).exists():
            (out / name).unlink()
    if text is not None:
        named_lines = [f"- **{s['code']}** ({s['kind']}): {s['detail']}" for s in verdict["named_stops"]]
        tail = (["", "## Named stops", ""] + (named_lines or ["- none (no page)"])
                + ["", "## Verdict", "", f"- **desk_final: {str(desk_final).lower()}**; next arm held: "
                   f"{str(verdict['next_arm_hold']).lower()}"] + [f"- {r}" for r in verdict["reasons"]])
        _write(out / "JOURNAL-TABLE.md", text + "\n".join(tail) + "\n")
        _write(out / SUMMARY_NAME, summary_text + "\n")
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
    return doc.get("verdict_sha256") == canonical_sha256({k: v for k, v in doc.items() if k != "verdict_sha256"})


def counts_as_final(doc, *, plan_id, queue_id, span_id, attempt, manifest_sha256, allow_mock=False):
    """FORMAT section 4 item 1, as one function the controller can import: a verdict counts for k+2 only if
    it verifies, is signed-transport and non-mock, was judged against the signed history, names exactly this
    span and bundle, and is final.
    ``allow_mock`` is for synthetic runs only (the controller's synthetic switch); it admits ``mock: true``."""
    return (verify_verdict(doc) and doc.get("desk_final") is True
            and (doc.get("mock") is False or (allow_mock is True and doc.get("mock") is True))
            and doc.get("history_source") == "signed-records"
            and (doc.get("transport") or {}).get("signed") is True
            and (doc.get("plan_id"), doc.get("queue_id"), doc.get("span_id"), doc.get("attempt"))
            == (plan_id, queue_id, span_id, attempt)
            and (doc.get("identities") or {}).get("manifest_sha256") == manifest_sha256)
