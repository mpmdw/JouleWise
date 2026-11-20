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
_ABBREVIATED = re.compile(r"(?<![0-9a-f])([0-9a-f]{1,63})(?:…|\.\.\.)([0-9a-f]{0,63})(?![0-9a-f])")
SPAN_KEYS = ("span_id", "runner_commit", "close_item", "check_item", "offload_manifest_sha256", "files")
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


def span_pins(span_id, offload_manifest_raw, sizes, *, runner_commit, close_item, check_item):
    """One span's pin entry from its offload manifest bytes. ``sizes`` maps each path to its byte count (read from
    the custody copy's directory entries, never by hashing it). No digest is computed from a custody file."""
    rows = parse_offload_manifest(offload_manifest_raw)
    missing = [path for path, _ in rows if path not in sizes]
    if missing or len(sizes) != len(rows):
        raise PinRefusal(f"{span_id}: the custody copy's files are not the offload manifest's "
                         f"({len(missing)} listed but absent, {len(set(sizes) - {p for p, _ in rows})} present but unlisted)")
    span = {"span_id": span_id, "runner_commit": runner_commit, "close_item": close_item, "check_item": check_item,
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


def check_binding(span, run_state_text):
    """How a span's public Check item names its offload manifest (RL-194a section 2). The full digest is the sha256
    of the offload manifest file as custody holds it. It binds to the Check when the item prints it in full, or
    prints an abbreviation every character of which matches: the prefix and the suffix exactly as printed (at least
    eight hex digits in all). Returns the item number, the text as printed (None when nothing binds) and the form:
    ``full``, ``abbreviated`` or ``absent``."""
    digest, number = span["offload_manifest_sha256"], span["check_item"]
    item = run_state_item(run_state_text, number)
    out = {"check_item": number, "as_printed": None, "form": "absent"}
    if item is None:
        return out
    if digest in item:
        return dict(out, as_printed=digest, form="full")
    for match in _ABBREVIATED.finditer(item):
        prefix, suffix = match.group(1), match.group(2)
        if len(prefix) + len(suffix) >= 8 and digest.startswith(prefix) and digest.endswith(suffix):
            return dict(out, as_printed=match.group(0), form="abbreviated")
    return out


def check_chain_problems(doc, run_state_text):
    """Problems chaining each span's offload manifest to its public Check item. A span whose Check prints no
    matching digest is held and returns to the research lead."""
    problems = []
    for span in doc["spans"]:
        if run_state_item(run_state_text, span["check_item"]) is None:
            problems.append(f"{span['span_id']}: RUN_STATE has no single item {span['check_item']}")
        elif check_binding(span, run_state_text)["form"] == "absent":
            problems.append(f"{span['span_id']}: Check item {span['check_item']} does not name its offload "
                            "manifest's sha256; the span is held")
    return problems


def chain_link(doc, run_state_text):
    """Per span, how its Check item names the offload manifest: ``full``, ``abbreviated`` or ``absent``."""
    return {span["span_id"]: check_binding(span, run_state_text)["form"] for span in doc["spans"]}


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


class PinnedCustody:
    """The roster's span directories under their pins, for one stage.

    ``streams`` says what the stage does when it opens a pinned stream (any pinned file that is not operational):
    ``"pass"`` reads it from disk (stage 1, which never hashes energy: the verifier process has checked it);
    ``"verify"`` reads it once, checks its pin and serves those bytes (stage 2, immediately before decoding)."""

    def __init__(self, doc, roster_span_ids, sdir_of, *, streams):
        ids = list(roster_span_ids)
        pinned = [span["span_id"] for span in doc["spans"]]
        if sorted(ids) != sorted(pinned) or len(set(ids)) != len(ids):
            raise PinRefusal(f"the pin list names {len(pinned)} span(s) and the roster {len(ids)}; "
                             "they are not the same spans")
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
            words = {"mismatch": "its bytes are not its pin", "missing": "a pinned file is missing",
                     "not_pinned": "a file that is not pinned", "symlink": "a symlink"}
            problems.append(f"{row['span_id']}/{row['path']}: {words.get(row['state'], 'not verified')}")
    if not problems and sorted(seen) != sorted(expected):
        problems.append("the verifier did not check exactly the pinned files")
    if not problems and result["result"] != "pass":
        problems.append("the verifier did not pass")
    return problems
