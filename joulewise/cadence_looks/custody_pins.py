"""Content-addressed admission of a look's custody inputs (RL-194).

``lm-interim-01`` reads a closed set: the roster's collected spans. Its manifest pins one inputs file, and that file
pins every file of every roster span by sha256 and size. The pins are not hashes of today's copy. Each span's pins
are the lines of the span's offload manifest (``<sha256>  ./<path>``, the SHA256SUMS the offload tooling wrote at the
span's Check) in their order, so the offload manifest's own sha256 is recomputed from the pins themselves, and that
digest is the one the span's public RUN_STATE Check item names. A pin that was changed, added or dropped breaks the
chain here, with no other file to consult.

Who hashes what (RL-194 conditions 1 to 3, as RL-194a amends them for the energy streams):

* A separate, hash-only verifier process (``scripts/cadence_look_verify_inputs.py``) runs first, before a stage parses
  anything and before the reservation. It reads every pinned file as opaque bytes and writes ``pass`` or ``fail`` with
  the pinned and observed digests. A stage is never the process that hashes an energy stream (RL-179 F-12).
* ``PinnedCustody.verify`` is then the stage's own act on the operational files it parses (the receipt, the soak
  reference, the leg records and summaries and the bundles' journals): each is read once into memory, hashed and
  compared, and every later read of one is served from those bytes, so the bytes hashed are the bytes parsed. It also
  checks each span directory by name: a missing file, a file that is not pinned or a symlink refuses.
* A stream is opened only if it is pinned. Stage 1 reads its time fields from disk after the verifier's pass. Stage 2
  re-checks a stream's pin at each open, immediately before it is decoded, and decodes those bytes; a mismatch there
  is inside the reservation. An open of a roster path outside the pin list refuses in both.

Nothing here decodes a measurement.
"""
from __future__ import annotations

import builtins
import contextlib
import hashlib
import io
import json
import os
from pathlib import PurePosixPath
import re
import stat
import sys

SCHEMA = "joulewise.cadence_look_input_pins.v1"
VERIFICATION_SCHEMA = "joulewise.cadence_look_input_verification.v1"
_HEX64 = re.compile(r"[0-9a-f]{64}")
_COMMIT = re.compile(r"[0-9a-f]{40}")
_SPAN = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]*")
_OFFLOAD_LINE = re.compile(r"([0-9a-f]{64})  \./(.+)")
_ITEM_HEAD = re.compile(r"^([0-9]+)\. \*\*", re.M)
# A digest as a Check item prints one: all 64 hex digits, or a prefix, an ellipsis and an optional suffix.
_PRINTED = re.compile(r"(?<![0-9a-f])(?:([0-9a-f]{64})|([0-9a-f]{1,63})(?:…|\.\.\.)([0-9a-f]{0,63}))(?![0-9a-f])")
# What may stand between a digest and the word that labels it: punctuation, "sha256" and a file count.
_BETWEEN = frozenset(" \t\r\n`'\"()[]*,;:=")
_FILLER = re.compile(r"sha-?256|files?|[0-9][0-9.,]*", re.I)
_MANIFEST_LABEL = re.compile(r"manifest(?:[_-]sha-?256)?|sha256sums", re.I)      # the sums file by its own name
_LABEL_REACH = 200          # characters before a digest in which its label is looked for
_OUTER_REACH = 40           # a digest with "outer" this close before it is never the binding manifest digest
SPAN_KEYS = ("span_id", "runner_commit", "close_item", "check_item", "check_corrected_from",
             "offload_manifest_sha256", "files")
FILE_KEYS = ("path", "sha256", "size")
# The span paths a stage parses whole and the look reuses: the receipt, the soak reference, each leg's record and
# summary and a bundle's journals. Every other pinned file is a stream: bound by its hash, never hashed by stage 1.
_OPERATIONAL = re.compile(
    r"runner_receipt\.json|soak/soak_reference\.json"
    r"|legs/[^/]+/leg_(?:record|summary)\.json"
    r"|legs/[^/]+/runtime/(?:[^/]+/)*(?:events\.jsonl|config\.json|align_runtime_events\.jsonl"
    r"|align_(?:turns|thermal|runtime_events)\.jsonl)")


def is_operational_path(rel):
    """Whether a span-relative POSIX path is one of the operational sources, never an energy-bearing file."""
    return _OPERATIONAL.fullmatch(rel) is not None


class PinRefusal(Exception):
    """An input that is not its pin. The message names a span and a path, never a value read from the file.
    Not a ValueError or an OSError: a reader that treats those as "this optional file is unreadable" must not
    absorb a refusal."""


def safe_relative(name):
    """Whether ``name`` is a relative POSIX path of plain components (no empty, ``.`` or ``..`` part)."""
    return (isinstance(name, str) and bool(name) and not PurePosixPath(name).is_absolute() and "\0" not in name
            and "\\" not in name and all(part not in ("", ".", "..") for part in name.split("/")))


def _whole(value):
    return type(value) is int and value >= 0


def pin_list_problems(doc, *, complete):
    """Structural problems of a pin list. ``complete`` refuses the empty list a draft may still carry."""
    if not isinstance(doc, dict) or set(doc) != {"schema", "spans"} or doc.get("schema") != SCHEMA:
        return [f"inputs: an object with exactly schema {SCHEMA!r} and spans"]
    spans = doc["spans"]
    if not isinstance(spans, list):
        return ["inputs.spans: a list"]
    problems, seen = [], set()
    if complete and not spans:
        problems.append("inputs.spans: empty; a committed look pins every roster span")
    for index, span in enumerate(spans):
        at = f"inputs.spans[{index}]"
        if not isinstance(span, dict) or set(span) != set(SPAN_KEYS):
            problems.append(f"{at}: exactly the members {', '.join(SPAN_KEYS)}")
            continue
        sid = span["span_id"]
        if not isinstance(sid, str) or not _SPAN.fullmatch(sid) or sid in seen:
            problems.append(f"{at}.span_id: a span id, once")
        seen.add(sid if isinstance(sid, str) else index)
        if not isinstance(span["runner_commit"], str) or not _COMMIT.fullmatch(span["runner_commit"]):
            problems.append(f"{at}.runner_commit: a full commit id")
        for key in ("close_item", "check_item"):
            if type(span[key]) is not int or span[key] < 1:
                problems.append(f"{at}.{key}: a RUN_STATE item number")
        corrected = span["check_corrected_from"]
        if corrected is not None and (type(corrected) is not int or corrected < 1 or corrected == span["check_item"]):
            problems.append(f"{at}.check_corrected_from: null, or the item number the pin table cited before the "
                            "correction (RL-195 section 2.1)")
        if not isinstance(span["offload_manifest_sha256"], str) or not _HEX64.fullmatch(span["offload_manifest_sha256"]):
            problems.append(f"{at}.offload_manifest_sha256: a sha256")
        files = span["files"]
        if not isinstance(files, list) or not files:
            problems.append(f"{at}.files: a non-empty list")
            continue
        paths, before = set(), len(problems)
        for number, entry in enumerate(files):
            where = f"{at}.files[{number}]"
            if not isinstance(entry, dict) or set(entry) != set(FILE_KEYS):
                problems.append(f"{where}: exactly path, sha256 and size")
                continue
            if not safe_relative(entry["path"]) or entry["path"] in paths:
                problems.append(f"{where}.path: a relative path of plain components, once")
            paths.add(entry["path"] if isinstance(entry["path"], str) else number)
            if not isinstance(entry["sha256"], str) or not _HEX64.fullmatch(entry["sha256"]):
                problems.append(f"{where}.sha256: a sha256")
            if not _whole(entry["size"]):
                problems.append(f"{where}.size: a byte count")
        if (len(problems) == before and isinstance(span["offload_manifest_sha256"], str)
                and offload_manifest_bytes_sha256(span) != span["offload_manifest_sha256"]):
            problems.append(f"{at}: its pins are not the lines of the offload manifest it names "
                            "(a pin was changed, added, dropped or reordered)")
    return problems


def offload_manifest_bytes(span):
    """The span's offload manifest as its pins rebuild it: one ``<sha256>  ./<path>`` line per pin, in order."""
    return "".join(f"{entry['sha256']}  ./{entry['path']}\n" for entry in span["files"]).encode("utf-8")


def offload_manifest_bytes_sha256(span):
    return hashlib.sha256(offload_manifest_bytes(span)).hexdigest()


def parse_offload_manifest(raw):
    """[(path, sha256)] in file order from SHA256SUMS bytes, or PinRefusal. The file must be exactly what its pins
    rebuild: ``<sha256>  ./<path>`` lines, each ended by one line feed, no path twice."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise PinRefusal("offload manifest: not UTF-8") from None
    if not text or not text.endswith("\n") or "\r" in text:
        raise PinRefusal("offload manifest: not line-feed-terminated '<sha256>  ./<path>' lines")
    rows, seen = [], set()
    for line in text[:-1].split("\n"):
        match = _OFFLOAD_LINE.fullmatch(line)
        if not match or not safe_relative(match.group(2)) or match.group(2) in seen:
            raise PinRefusal("offload manifest: a line that is not '<sha256>  ./<relative path>', or a path twice")
        seen.add(match.group(2))
        rows.append((match.group(2), match.group(1)))
    return rows


def span_pins(span_id, offload_manifest_raw, sizes, *, runner_commit, close_item, check_item, check_corrected_from=None):
    """One span's pin entry from its offload manifest bytes. ``sizes`` maps each path to its byte count (read from
    the custody copy's directory entries, never by hashing it). No digest is computed from a custody file."""
    rows = parse_offload_manifest(offload_manifest_raw)
    missing = [path for path, _ in rows if path not in sizes]
    if missing or len(sizes) != len(rows):
        raise PinRefusal(f"{span_id}: the custody copy's files are not the offload manifest's "
                         f"({len(missing)} listed but absent, {len(set(sizes) - {p for p, _ in rows})} present but unlisted)")
    span = {"span_id": span_id, "runner_commit": runner_commit, "close_item": close_item, "check_item": check_item,
            "check_corrected_from": check_corrected_from,
            "offload_manifest_sha256": hashlib.sha256(offload_manifest_raw).hexdigest(),
            "files": [{"path": path, "sha256": digest, "size": sizes[path]} for path, digest in rows]}
    if offload_manifest_bytes(span) != offload_manifest_raw:
        raise PinRefusal(f"{span_id}: the offload manifest is not rebuilt byte for byte by its own lines")
    return span


def run_state_item(text, number):
    """The text of RUN_STATE item ``number`` (from its ``N. **`` head to the next item's head), or None."""
    heads = [(int(match.group(1)), match.start()) for match in _ITEM_HEAD.finditer(text)]
    found = [index for index, (n, _) in enumerate(heads) if n == number]
    if len(found) != 1:
        return None
    start = heads[found[0]][1]
    end = heads[found[0] + 1][1] if found[0] + 1 < len(heads) else len(text)
    return text[start:end]


def _label_words(item, at, count=2):
    """The words before the digest printed at ``at`` that label it, nearest first, skipping punctuation, ``sha256``
    and a file count; at most ``count`` of them. The scan stops at any other character (so ``outer.sha256`` gives no
    word) and within ``_LABEL_REACH`` characters. One pass backwards."""
    low, end, words = max(0, at - _LABEL_REACH), at, []
    while len(words) < count:
        while end > low and item[end - 1] in _BETWEEN:
            end -= 1
        start = end
        while start > low:
            char = item[start - 1]
            inside_number = (char in ".," and start < end and item[start].isdigit()
                             and start - 2 >= low and item[start - 2].isdigit())
            if not (char.isalnum() or char in "_-" or inside_number):
                break
            start -= 1
        if start == end or (start == low and low > 0):
            break                       # another character, or the label lies beyond the reach
        word = item[start:end]
        end = start
        if not _FILLER.fullmatch(word):
            words.append(word)
    return words


def _manifest_labelled(item, at):
    """Whether the digest printed at ``at`` is labelled as a manifest's: the nearest word before it, past
    punctuation, ``sha256`` and a file count, is ``manifest`` (or ``manifest_sha256``, or the sums file's own name,
    ``SHA256SUMS``). A digest under any other label (an archive's, a marker's, a commit's) is not the offload
    manifest's, whatever its characters. Nor is an ``outer`` one: the close-time ``outer.sha256`` file is a
    custody-side record with no public, dated witness, so it is cited as a second record and never binds (RL-195
    section 2.2)."""
    words = _label_words(item, at)
    if not words or _MANIFEST_LABEL.fullmatch(words[0]) is None:
        return False
    return "outer" not in item[max(0, at - _OUTER_REACH):at].lower()     # "outer manifest", "outer.sha256 (manifest)"


def _mentions(item, span_ids):
    """[(position, span id)] of each pinned span id the item names, longest id first where one contains another.
    ``cq-<id>-a1`` names ``<id>``; a longer word that merely contains the characters does not."""
    names = "|".join(re.escape(name) for name in sorted(span_ids, key=len, reverse=True))
    return [(match.start(), match.group(0))
            for match in re.finditer(rf"(?<![A-Za-z0-9])(?:{names})(?![A-Za-z0-9])", item)]


def check_binding(span, run_state_text, span_ids=()):
    """How a span's public Check item names its offload manifest (RL-194a section 2). The full digest is the sha256
    of the offload manifest file as custody holds it. The Check's digests for the span are the ones it prints as the
    span's manifest: after each place the item names the span, the first digest labelled ``manifest`` before the
    item names another pinned span (``span_ids``). A digest under another label, and a digest printed for another
    span, bind nothing.

    The span binds when the Check prints at least one such digest and every hex character of every one matches:
    all 64, or an abbreviation's prefix and suffix exactly as printed, however many they are. Returns the item
    number, the text as printed and the form: ``full``, ``abbreviated``, ``mismatch`` (the Check prints a manifest
    digest for the span with a character that does not match; ``as_printed`` is that digest) or ``absent`` (it
    prints none; ``as_printed`` is None). ``mismatch`` and ``absent`` hold the span."""
    digest, number, sid = span["offload_manifest_sha256"], span["check_item"], span["span_id"]
    out = {"check_item": number, "as_printed": None, "form": "absent"}
    item = run_state_item(run_state_text, number)
    if item is None:
        return out
    mentions = _mentions(item, set(span_ids) | {sid})
    printed = [match for match in _PRINTED.finditer(item) if _manifest_labelled(item, match.start())]
    claimed = []
    for index, (at, name) in enumerate(mentions):
        if name != sid:
            continue
        end = mentions[index + 1][0] if index + 1 < len(mentions) else len(item)
        first = next((match for match in printed if at <= match.start() < end), None)
        if first is not None:
            claimed.append(first)
    if not claimed:
        return out

    def matches(match):
        whole, prefix, suffix = match.groups()
        if whole is not None:
            return whole == digest
        return len(prefix) + len(suffix) < 64 and digest.startswith(prefix) and digest.endswith(suffix)
    for match in claimed:
        if not matches(match):
            return dict(out, as_printed=match.group(0), form="mismatch")
    if any(match.group(1) for match in claimed):
        return dict(out, as_printed=digest, form="full")
    longest = max(claimed, key=lambda match: len(match.group(2)) + len(match.group(3)))
    return dict(out, as_printed=longest.group(0), form="abbreviated")


def check_chain_problems(doc, run_state_text):
    """Problems chaining each span's offload manifest to its public Check item. A span whose Check prints no
    manifest digest for it, or prints one with a character that does not match, is held and returns to the
    research lead."""
    problems, ids = [], [span["span_id"] for span in doc["spans"]]
    for span in doc["spans"]:
        if run_state_item(run_state_text, span["check_item"]) is None:
            problems.append(f"{span['span_id']}: RUN_STATE has no single item {span['check_item']}")
            continue
        form = check_binding(span, run_state_text, ids)["form"]
        if form == "mismatch":
            problems.append(f"{span['span_id']}: Check item {span['check_item']} prints a manifest digest for the "
                            "span that is not its offload manifest's sha256; the span is held")
        elif form == "absent":
            problems.append(f"{span['span_id']}: Check item {span['check_item']} does not name its offload "
                            "manifest's sha256; the span is held")
    return problems


def chain_link(doc, run_state_text):
    """Per span, how its Check item names the offload manifest: ``full``, ``abbreviated``, ``mismatch`` or
    ``absent``."""
    ids = [span["span_id"] for span in doc["spans"]]
    return {span["span_id"]: check_binding(span, run_state_text, ids)["form"] for span in doc["spans"]}


BOUND, HELD = "bound", "held"


def check_states(doc, run_state_text):
    """Per span, its state against the public RUN_STATE (RL-194 condition 2; RL-194a section 2; RL-195 section 2):
    ``bound`` when its Check item prints its offload manifest's digest as the span's and every printed character
    matches, else ``held``. A HELD span keeps the look's manifest from being final and is never dropped from the
    roster: it stays in the pin list, and every stage refuses to run while it is held. Each value carries the state,
    the binding's form, the item number, the text as printed and the item the pin table cited before a correction."""
    ids = [span["span_id"] for span in doc["spans"]]
    out = {}
    for span in doc["spans"]:
        binding = check_binding(span, run_state_text, ids)
        out[span["span_id"]] = {"state": BOUND if binding["form"] in ("full", "abbreviated") else HELD,
                                "form": binding["form"], "check_item": span["check_item"],
                                "as_printed": binding["as_printed"],
                                "corrected_from": span["check_corrected_from"]}
    return out


def held_spans(doc, run_state_text):
    """The span ids that are HELD, in pin-list order."""
    return [sid for sid, state in check_states(doc, run_state_text).items() if state["state"] == HELD]


def correct_check(doc, span_id, item, run_state_text):
    """The pin list with one span's ``check_item`` corrected to ``item`` (RL-195 section 2.1, the lead's rule). Only
    where item ``item`` itself names that span's offload manifest under a manifest label and every printed hex
    character matches: anything else raises PinRefusal and the span stays HELD. ``check_corrected_from`` keeps the
    item the pin table cited first, through any later correction; correcting back to it clears it. A close-time
    ``outer.sha256`` file cannot be the route: it is cited only as a second record (section 2.2)."""
    out = json.loads(json.dumps(doc))
    spans = [span for span in out["spans"] if span["span_id"] == span_id]
    if len(spans) != 1:
        raise PinRefusal(f"{span_id}: not a span of this pin list")
    span = spans[0]
    if type(item) is not int or item < 1:
        raise PinRefusal(f"{span_id}: a RUN_STATE item number")
    if item == span["check_item"]:
        raise PinRefusal(f"{span_id}: Check item {item} is already the span's check_item")
    ids = [entry["span_id"] for entry in out["spans"]]
    trial = dict(span, check_item=item)
    if run_state_item(run_state_text, item) is None:
        raise PinRefusal(f"{span_id}: RUN_STATE has no single item {item}; the span stays HELD")
    binding = check_binding(trial, run_state_text, ids)
    if binding["form"] not in ("full", "abbreviated"):
        raise PinRefusal(f"{span_id}: item {item} does not name the span's offload manifest with every printed "
                         f"character matching ({binding['form']}); the span stays HELD")
    first = span["check_corrected_from"] if span["check_corrected_from"] is not None else span["check_item"]
    span["check_item"], span["check_corrected_from"] = item, (None if first == item else first)
    return out


_ANY_DIGEST = re.compile(r"(?<![0-9a-f])(?:[0-9a-f]{64}|[0-9a-f]{1,63}(?:…|\.\.\.)[0-9a-f]{0,63})(?![0-9a-f])")


def digest_labels(span_id, run_state_text, span_ids=()):
    """[(item number, label)] for every digest printed after an item names the span and before it names another
    pinned span, in RUN_STATE order: the labels and item numbers RL-195 section 2.4 asks for, so that a HELD span can
    go to the research lead without a digest. ``label`` is the nearest labelling word, or None."""
    heads = [(int(match.group(1)), match.start()) for match in _ITEM_HEAD.finditer(run_state_text)]
    ids = set(span_ids) | {span_id}
    out = []
    for index, (number, start) in enumerate(heads):
        item = run_state_text[start:heads[index + 1][1] if index + 1 < len(heads) else len(run_state_text)]
        mentions = _mentions(item, ids)
        if not any(name == span_id for _, name in mentions):
            continue
        for position, (at, name) in enumerate(mentions):
            if name != span_id:
                continue
            end = mentions[position + 1][0] if position + 1 < len(mentions) else len(item)
            for match in _ANY_DIGEST.finditer(item, at, end):
                words = _label_words(item, match.start(), count=1)
                entry = (number, words[0] if words else None)
                if entry not in out:
                    out.append(entry)
    return out


def pin_list_sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def load_pin_list(raw, *, complete=True):
    """The pin list decoded from its file's bytes, or PinRefusal listing its first problems."""
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("duplicate member")
            out[key] = value
        return out
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=float)
    except (UnicodeDecodeError, ValueError):
        raise PinRefusal("inputs: not one strict JSON document") from None
    problems = pin_list_problems(doc, complete=complete)
    if problems:
        raise PinRefusal("; ".join(problems[:4]))
    return doc


def require_roster(doc, roster_span_ids):
    """The pinned spans are exactly the roster's, each once; PinRefusal otherwise."""
    ids = list(roster_span_ids)
    pinned = [span["span_id"] for span in doc["spans"]]
    if sorted(ids) != sorted(pinned) or len(set(ids)) != len(ids):
        raise PinRefusal(f"the pin list names {len(pinned)} span(s) and the roster {len(ids)}; "
                         "they are not the same spans")
    return ids


class PinnedCustody:
    """The roster's span directories under their pins, for one stage.

    ``streams`` says what the stage does when it opens a pinned stream (any pinned file that is not operational):
    ``"pass"`` reads it from disk (stage 1, which never hashes energy: the verifier process has checked it);
    ``"verify"`` reads it once, checks its pin and serves those bytes (stage 2, immediately before decoding)."""

    def __init__(self, doc, roster_span_ids, sdir_of, *, streams):
        ids = require_roster(doc, roster_span_ids)
        if streams not in ("pass", "verify"):
            raise ValueError("streams: 'pass' or 'verify'")
        self.spans = {span["span_id"]: span for span in doc["spans"]}
        self.order, self.streams = ids, streams
        self.roots = {sid: os.path.abspath(os.fspath(sdir_of(sid))) for sid in ids}
        self.pins = {(sid, entry["path"]): entry for sid in ids for entry in self.spans[sid]["files"]}
        self._bytes = {}                # (span id, relative path) -> an operational file's verified bytes
        self._real = {}                 # realpath of a span directory -> span id
        self._own_read = False
        self._guarded = False
        self.opened = []                # (span id, relative path) of every read the stage made, in order

    # ------------------------------------------------------------------------------------- the stage's own act
    def verify(self):
        """Refuse unless every span directory holds exactly its pinned files (by name; nothing is opened for that)
        and every operational file has its pinned bytes. Returns the number of operational files and bytes read.
        No stream is opened here."""
        for sid in self.order:
            self._inventory(sid)
        count = total = 0
        for (sid, rel), entry in self.pins.items():
            if is_operational_path(rel):
                self._bytes[(sid, rel)] = self._pinned_bytes(sid, rel)
                count, total = count + 1, total + entry["size"]
        for sid in self.order:
            self._real[os.path.realpath(self.roots[sid])] = sid
        return count, total

    def _inventory(self, sid):
        """The span directory's entries against the pins, by name and kind only: nothing is opened here."""
        root = self.roots[sid]
        try:
            top = os.lstat(root)
        except OSError:
            raise PinRefusal(f"{sid}: no span directory") from None
        if not stat.S_ISDIR(top.st_mode):
            raise PinRefusal(f"{sid}: the span directory is a symlink or not a directory")
        present, pending = set(), [""]
        while pending:
            prefix = pending.pop()
            try:
                entries = sorted(os.scandir(os.path.join(root, prefix) if prefix else root), key=lambda e: e.name)
            except OSError:
                raise PinRefusal(f"{sid}/{prefix}: a directory that cannot be listed") from None
            for entry in entries:
                rel = f"{prefix}/{entry.name}" if prefix else entry.name
                if entry.is_symlink():
                    raise PinRefusal(f"{sid}/{rel}: a symlink")
                if entry.is_dir(follow_symlinks=False):
                    pending.append(rel)
                elif entry.is_file(follow_symlinks=False):
                    present.add(rel)
                else:
                    raise PinRefusal(f"{sid}/{rel}: neither a regular file nor a directory")
        pinned = {entry["path"] for entry in self.spans[sid]["files"]}
        for rel in sorted(pinned - present)[:1]:
            raise PinRefusal(f"{sid}/{rel}: a pinned file is missing")
        for rel in sorted(present - pinned)[:1]:
            raise PinRefusal(f"{sid}/{rel}: a file that is not pinned")

    def _pinned_bytes(self, sid, rel):
        """One pinned file read once, hashed and compared; the bytes are returned only if they are the pin's."""
        entry = self.pins[(sid, rel)]
        path = os.path.join(self.roots[sid], *rel.split("/"))
        self._own_read = True
        try:
            descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            try:
                if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                    raise PinRefusal(f"{sid}/{rel}: not a regular file")
                with os.fdopen(descriptor, "rb", closefd=False) as handle:
                    data = handle.read()
            finally:
                os.close(descriptor)
        except OSError:
            raise PinRefusal(f"{sid}/{rel}: a pinned file is missing, a symlink or unreadable") from None
        finally:
            self._own_read = False
        if len(data) != entry["size"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise PinRefusal(f"{sid}/{rel}: its bytes are not its pin")
        return data

    # ----------------------------------------------------------------------------------- reads during the stage
    def locate(self, file):
        """(span id, relative path) of a path inside a roster span directory, or None for any other path."""
        if not isinstance(file, (str, bytes, os.PathLike)):
            return None
        path = os.path.abspath(os.fsdecode(file))
        for candidate in (path, os.path.realpath(path)):
            for root, sid in ((self.roots[s], s) for s in self.order):
                if candidate == root or candidate.startswith(root + os.sep):
                    return sid, candidate[len(root) + 1:].replace(os.sep, "/")
            for root, sid in self._real.items():
                if candidate == root or candidate.startswith(root + os.sep):
                    return sid, candidate[len(root) + 1:].replace(os.sep, "/")
        return None

    def read(self, sid, rel):
        """The verified bytes of one operational file; any other path refuses."""
        data = self._bytes.get((sid, rel))
        if data is None:
            raise PinRefusal(f"{sid}/{rel}: an open of a roster file outside the verified operational files")
        self.opened.append((sid, rel))
        return data

    def _open(self, real_open, file, mode="r", buffering=-1, encoding=None, errors=None, newline=None,
              closefd=True, opener=None):
        hit = self.locate(file)
        if hit is None:
            return real_open(file, mode, buffering, encoding, errors, newline, closefd, opener)
        sid, rel = hit
        if set(mode) - set("rbt"):
            raise PinRefusal(f"{sid}/{rel}: a roster file opened for writing")
        if (sid, rel) not in self.pins:
            path = os.path.abspath(os.fsdecode(file))
            if rel and os.path.isdir(path):
                raise IsADirectoryError(21, "Is a directory", path)
            if not os.path.lexists(path):
                raise FileNotFoundError(2, "No such file or directory", path)
            raise PinRefusal(f"{sid}/{rel}: an open of a roster file outside the pin list")
        sys.audit("joulewise.custody_pins.read", os.fsdecode(file), mode)      # an observer sees what is parsed
        if (sid, rel) in self._bytes:
            data = self.read(sid, rel)
        elif self.streams == "pass":
            # Stage 1 and a stream: the verifier process hashed it; this process reads its time fields from disk
            # and never holds or hashes the whole file (RL-179 F-12; RL-194a section 1).
            self.opened.append((sid, rel))
            self._own_read = True
            try:
                return real_open(file, mode, buffering, encoding, errors, newline, closefd, opener)
            finally:
                self._own_read = False
        else:
            # Stage 2 and a stream: its pin is checked on this read, immediately before it is decoded
            data = self._pinned_bytes(sid, rel)
            self.opened.append((sid, rel))
        if "b" in mode:
            return io.BytesIO(data)
        return io.TextIOWrapper(io.BytesIO(data), encoding=encoding, errors=errors, newline=newline)

    def _audit(self, event, args):
        """The backstop: a real open of a roster path that this object did not make itself refuses. Reads served
        from memory open nothing, so they raise no event."""
        if not self._guarded or self._own_read or event != "open" or not args:
            return
        if self.locate(args[0]) is not None:
            sid, rel = self.locate(args[0])
            raise PinRefusal(f"{sid}/{rel}: a roster file opened outside the pinned reads")

    @contextlib.contextmanager
    def guard(self):
        """Route every read of a roster path through the pins for the duration of the stage."""
        real_open = builtins.open

        def guarded(file, mode="r", buffering=-1, encoding=None, errors=None, newline=None, closefd=True,
                    opener=None):
            return self._open(real_open, file, mode, buffering, encoding, errors, newline, closefd, opener)
        if not getattr(self, "_hooked", False):
            sys.addaudithook(self._audit)
            self._hooked = True
        builtins.open, io.open, self._guarded = guarded, guarded, True
        try:
            yield self
        finally:
            builtins.open, io.open, self._guarded = real_open, real_open, False


def verification_problems(doc, result):
    """Problems of the verifier process's result file against the pin list: it must say ``pass`` and carry, for
    exactly the pinned files, an observed digest equal to the pin. Returns the first problems, naming paths."""
    expected = [(span["span_id"], entry["path"], entry["sha256"]) for span in doc["spans"] for entry in span["files"]]
    if (not isinstance(result, dict) or set(result) != {"schema", "result", "files"}
            or result.get("schema") != VERIFICATION_SCHEMA or not isinstance(result.get("files"), list)):
        return ["the verifier's result is not a joulewise.cadence_look_input_verification.v1 file"]
    problems, seen = [], []
    for row in result["files"]:
        if not isinstance(row, dict) or set(row) != {"span_id", "path", "pinned", "observed", "state"}:
            return ["the verifier's result carries a row that is not span_id, path, pinned, observed and state"]
        seen.append((row["span_id"], row["path"], row["pinned"]))
        if row["state"] != "match" or row["observed"] != row["pinned"] or row["pinned"] is None:
            words = {"mismatch": "its bytes are not its pin", "size": "its byte count is not its pin",
                     "missing": "a pinned file is missing", "not_pinned": "a file that is not pinned",
                     "symlink": "a symlink"}
            problems.append(f"{row['span_id']}/{row['path']}: {words.get(row['state'], 'not verified')}")
    if not problems and sorted(seen) != sorted(expected):
        problems.append("the verifier did not check exactly the pinned files")
    if not problems and result["result"] != "pass":
        problems.append("the verifier did not pass")
    return problems


# ------------------------------------------------------------------------- operational JSON, energy members shielded
_ENERGY_PARTS = ("joule", "watt", "power_w", "gpu_power", "energy_j", "_mj", "_wh")


def energy_named(name):
    """Whether a member name is one that carries energy or power: the rule step 3's output check and the twin apply
    to names (``step3_energy_ratios.custody_check``)."""
    lower = name.lower()
    return lower == "e" or lower.endswith(("_j", "_w")) or any(part in lower for part in _ENERGY_PARTS)


class _Shielded:
    """The value of an energy-named member in an operational file, as a stage outside the reservation holds it:
    the fact that a number was there, and nothing of the number."""
    __slots__ = ()

    def __repr__(self):
        return "<shielded number>"

    def __reduce__(self):
        return "SHIELDED"


SHIELDED = _Shielded()


class _Integer(str):
    __slots__ = ()


class _Real(str):
    __slots__ = ()


class OperationalJSONError(ValueError):
    """``reason`` is ``duplicate``, ``nonfinite`` or ``malformed``; the message carries no value."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def _unique(items):
    if len({key for key, _ in items}) != len(items):
        raise OperationalJSONError("duplicate")
    return dict(items)


def _finite(token):
    number = float(token)
    if number != number or number in (float("inf"), float("-inf")):
        raise OperationalJSONError("nonfinite")
    return number


def _no_constant(token):
    raise OperationalJSONError("nonfinite")


# Text in which no member can be energy-named has none of these: a name part, a name's ending before its closing
# quote, the one-letter name, or an escape (a name may be spelled with one).
_MAYBE_ENERGY = ("\\", *_ENERGY_PARTS, '_j"', '_w"', '"e"')


def operational_json(text, *, strict=True, object_pairs_hook=None, _settle_always=False):
    """Decode one JSON document of an operational file. A number under an energy-named member (at any depth below
    it) is never converted: its place is taken by ``SHIELDED``. Every other number is the ``int`` or ``float``
    ``json.loads`` gives. An operational journal may carry one measured mean (the pinned controller writes the idle
    baseline's ``power_w_mean`` into ``events.jsonl``); the stages parse that journal for its time fields before
    the reservation, and the cold review parses it too, so the one decoder they all use does not make the number.

    ``strict`` refuses a repeated member and a nonfinite number (``OperationalJSONError``); without it they are
    kept as ``json.loads`` keeps them. ``object_pairs_hook`` builds each object from its pairs. A document whose
    text cannot spell an energy-named member is decoded directly: there is nothing in it to shield."""
    def settle(value, shielded):
        kind = type(value)
        if kind is dict:
            return {key: settle(item, shielded or energy_named(key)) for key, item in value.items()}
        if kind is list:
            return [settle(item, shielded) for item in value]
        if kind is _Integer or kind is _Real:
            if shielded:
                return SHIELDED
            if kind is _Integer:
                return int(value)
            return _finite(value) if strict else float(value)
        return value

    def both(items):
        _unique(items)
        return object_pairs_hook(items)
    pairs = object_pairs_hook if not strict else _unique if object_pairs_hook is None else both
    constant = _no_constant if strict else None
    try:
        if isinstance(text, (bytes, bytearray)):
            text = bytes(text).decode(json.detect_encoding(text), "surrogatepass")       # as json.loads reads bytes
        lower = text.lower()
        if not _settle_always and not any(part in lower for part in _MAYBE_ENERGY):
            return json.loads(text, object_pairs_hook=pairs, parse_float=_finite if strict else None,
                              parse_constant=constant)
        return settle(json.loads(text, object_pairs_hook=pairs, parse_int=_Integer, parse_float=_Real,
                                 parse_constant=constant), False)
    except OperationalJSONError:
        raise
    except (ValueError, RecursionError):
        raise OperationalJSONError("malformed") from None
