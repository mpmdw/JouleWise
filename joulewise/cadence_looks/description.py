"""Energy-blind admission and census for the three registered description looks."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
import csv
from datetime import datetime
from hashlib import sha1, sha256
import io
import json
import math
import os
from pathlib import Path
import re
import socket
import stat
from statistics import mean, stdev
import subprocess
import sys
from types import ModuleType
from zoneinfo import ZoneInfo


IDS = ("lm-inst-01", "lm-stab-01", "lm-stab-02")
CONTROL = "docs/process/cadence/looks"
CAMPAIGN = "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign"
CODE_ROOT = Path(__file__).resolve().parents[2]
CHANNELS = ("gpu_rail", "rail_sum", "dc_in")
RAILS = ("cpu_power", "gpu_power", "ane_power")
RAIL_CHANNELS = {"cpu_rail": "cpu_power", "gpu_rail": "gpu_power", "ane_rail": "ane_power"}
WIDTHS = (10, 40, 128)
MIN_SAMPLE_COVERAGE = 0.99  # RL-166 Q7, applied to each description print by RL-181.
VALUE_FILES = ("support.json", "power_trace.csv", "dc_points.csv")
LOCAL = ZoneInfo("America/Los_Angeles")
SHA = re.compile(r"[0-9a-f]{64}")
OID = re.compile(r"[0-9a-f]{40}")
LEG = re.compile(r"L00[1-9]|L01[0-2]")
STABILITY_KIT = re.compile(r"f2-stab-[0-9]{2}")
LEDGER_SCHEMA = "joulewise.cadence_look_ledger.v1"
POSITION_FIELDS = ("leg_id", "prefill_tokens", "decode_tokens", "start_band", "g0_shape")
SPAN_FIELDS = ("kit_id", "kit_sha256", "span_id", "attempt", "runner_pin", "legs")
DESK_RECORDS = ("hand_table", "q1", "desk_final")
FINISHED = {"completed", "coalesced", "failed", "interrupted"}
AUTHORITY = {
    "first_native": "authority/native.json",
    "piece1": "authority/piece1.json",
    "freeze": "authority/freeze.json",
    "cold": "authority/cold.json",
    "copy": "authority/copy.json",
    "events": "authority/events.json",
    "host_closes": "ops/host-closes.json",
}


class Refusal(ValueError):
    """An absent, inconsistent or unauthorized description binding."""


def require(condition, message):
    if not condition:
        raise Refusal(message)


def digest(payload):
    return sha256(payload).hexdigest()


def token(value, expression):
    return type(value) is str and expression.fullmatch(value) is not None


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def canonical(document):
    return (json.dumps(document, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _unique(pairs):
    obj = {}
    for name, value in pairs:
        require(name not in obj, "duplicate JSON field")
        obj[name] = value
    return obj


def _invalid_constant(_value):
    raise Refusal("nonfinite JSON token")


def decode(payload):
    return json.loads(payload.decode("utf-8"), object_pairs_hook=_unique,
                      parse_constant=_invalid_constant)


def relative(name):
    require(type(name) is str and bool(name) and "\\" not in name, "invalid relative path")
    path = Path(name)
    require(not path.is_absolute() and path.as_posix() == name and path.parts
            and all(part not in (".", "..") and part.casefold() != ".git"
                    for part in path.parts), "noncanonical relative path")
    return path


def public_path(path):
    require(all(part.casefold() != "restricted" for part in path.parts),
            "custody component in public input path")
    return path


def exact_path(path, *, directory=False, absent=False):
    """Reject symlinks in any component, including a final dangling symlink."""
    require(path.is_absolute() and ".." not in path.parts, "path outside canonical root")
    cursor = Path(path.anchor)
    for component in path.parts[1:-1]:
        cursor /= component
        require(stat.S_ISDIR(cursor.lstat().st_mode), "non-directory path component")
    if absent and not os.path.lexists(path):
        return path
    mode = path.lstat().st_mode
    require((stat.S_ISDIR if directory else stat.S_ISREG)(mode), "unexpected path type")
    return path


def _absolute(root, value):
    require(type(value) is str and bool(value), "missing registered path")
    path = Path(value)
    return path if path.is_absolute() else root / relative(value)


def _disjoint(*roots):
    return all(not a.is_relative_to(b) and not b.is_relative_to(a)
               for i, a in enumerate(roots) for b in roots[:i])


def _git_environment():
    # Do not let a calling shell replace the repository, object store or index.
    return {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}


class Book:
    """The local index and working files must agree with origin/main's objects."""

    def __init__(self, root):
        self.root = exact_path(root, directory=True)
        require(self.git("rev-parse", "--show-toplevel").decode().strip() == str(root),
                "the requested book is not a repository root")
        self.head = self.git("rev-parse", "--verify", "refs/remotes/origin/main^{commit}").decode().strip()
        require(token(self.head, OID), "invalid authoritative commit")
        self.tree_cache = {}
        self.index = {}
        for row in self.git("ls-files", "--stage", "-z").split(b"\0"):
            if row:
                info, name = row.split(b"\t", 1)
                mode, oid, stage = info.decode().split()
                if stage == "0" and mode in ("100644", "100755"):
                    self.index[os.fsdecode(name)] = oid

    def git(self, *args):
        return subprocess.check_output(
            ["git", "--no-replace-objects", "-C", str(self.root), *args],
            env=_git_environment(), stderr=subprocess.PIPE,
        )

    def tree(self, commit):
        require(token(commit, OID), "invalid source commit")
        if commit not in self.tree_cache:
            entries = {}
            for row in self.git("ls-tree", "-rz", commit).split(b"\0"):
                if row:
                    info, name = row.split(b"\t", 1)
                    mode, _, oid = info.decode().split()
                    if mode in ("100644", "100755"):
                        entries[os.fsdecode(name)] = oid
            self.tree_cache[commit] = entries
        return self.tree_cache[commit]

    def ancestor(self, before, after):
        require(token(before, OID) and token(after, OID), "invalid ancestry binding")
        try:
            self.git("merge-base", "--is-ancestor", before, after)
        except subprocess.CalledProcessError as error:
            require(error.returncode == 1, "ancestry lookup failed")
            return False
        return True

    def history(self, commit, path):
        return self.git("log", "--first-parent", "--format=%H", commit, "--", path).decode().splitlines()

    def blob(self, commit, name):
        relative(name)
        oid = self.tree(commit).get(name)
        require(oid is not None, "uncommitted source path")
        return self.git("cat-file", "blob", oid)

    def working(self, name, commit, expected=None):
        path = public_path(self.root / relative(name))
        oid = self.tree(commit).get(name)
        require(oid is not None and self.index.get(name) == oid, "source differs in index")
        raw = exact_path(path).read_bytes()
        actual_oid = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(actual_oid == oid and (expected is None or digest(raw) == expected),
                "source differs from its commit")
        return raw


def _select_row(ledger, look):
    require(ledger["schema"] == LEDGER_SCHEMA and type(ledger["looks"]) is list,
            "invalid authority ledger")
    matches = [row for row in ledger["looks"] if row.get("look_id") == look]
    require(len(matches) == 1, "look must have one committed ledger row")
    return matches[0]


def _binding_commit(book, ledger_path, row):
    """Find the original commit of this row on the authoritative main line."""
    look, status = row["look_id"], row["status"]
    bound = None
    seen = set()
    for commit in reversed(book.history(book.head, ledger_path)):
        current = decode(book.blob(commit, ledger_path))
        matches = [item for item in current["looks"] if item.get("look_id") == look]
        require(len(matches) <= 1, "duplicate look in ledger history")
        if not matches:
            require(bound is None, "look removed from ledger after binding")
            continue
        item = matches[0]
        require(item.get("status") not in FINISHED, "ledger already spent the look")
        if item.get("status") == status:
            # Stage 1 may follow revised blind prerequisite snapshots. Once
            # stage 1 is committed the reservation identity is immutable.
            if status == "stage1_committed":
                require(item == row, "stage-1 binding changed after commitment")
            if item == row and bound is None:
                bound = commit
        seen.add(item.get("status"))
    require(bound is not None and (status != "committed" or "stage1_committed" not in seen),
            "unbound or already committed stage-1 row")
    return bound


def _pin_paths(look):
    family = "lm-inst-01" if look == IDS[0] else "lm-stab-01"
    return {
        "reader": "joulewise/cadence_looks/description.py",
        "manifest_schema": f"{CONTROL}/look_manifest.v2.schema.json",
        "stage1_schema": f"{CONTROL}/{family}.stage1.schema.json",
        "output_schema": f"{CONTROL}/{family}.output.schema.json",
        "restricted_schema": f"{CONTROL}/{family}.restricted.schema.json",
        "validator": "joulewise/cadence_looks/manifest_dispatch.py",
        "schema_validator": "joulewise/cadence_looks/qualification_manifest.py",
        "kit_commitments": f"{CONTROL}/look-kit-commitments.v2.json",
    }


def private_names(instrument):
    return ("hold.json", "turn.json", *(("gain.json", "edges.json") if instrument
                                      else ("date_spreads.json", "context.json")),
            "stdout", "stderr")


class Snapshot:
    def __init__(self, root, look, stage):
        self.book = Book(root)
        self.look = look
        self.instrument = look == IDS[0]
        production_ledger = f"{CONTROL}/LOOKS.json"
        self.native = production_ledger in self.book.tree(self.book.head)
        self.ledger_path = production_ledger if self.native else "LOOKS.json"
        self.ledger = decode(self.book.working(self.ledger_path, self.book.head))
        self.row = _select_row(self.ledger, look)
        require(self.row["status"] == ("committed" if stage == "stage1" else "stage1_committed"),
                "wrong look ledger status")
        require(self.row["execution_host"] == socket.gethostname(), "wrong execution host")
        self.commit = _binding_commit(self.book, self.ledger_path, self.row)
        self.registration = self.row["registration_commit"]
        require(self.registration != self.commit and self.book.ancestor(self.registration, self.commit),
                "registration must precede this read")
        self.stage_name = (f"{CONTROL}/stage1/" if self.native else "stage1/") + look + ".json"
        self.manifest_name = (f"{CAMPAIGN}/looks/{look}.manifest.json" if self.native
                              else f"manifests/{look}.json")
        require(self.row["manifest_path"] == self.manifest_name, "wrong registered manifest path")
        self.hashes = self.row["input_hashes"]
        require(type(self.hashes) is dict and bool(self.hashes), "missing source inventory")
        for name, bound_hash in self.hashes.items():
            public_path(root / relative(name))
            require(token(bound_hash, SHA), "invalid source digest")
        self.cache = {}
        self.manifest = self._manifest(self.manifest_name, look)
        require(self.hashes[self.manifest_name] == self.row["sha256"], "wrong manifest ledger digest")
        self.copy = self.doc(AUTHORITY["copy"])
        self._destinations(root)
        self.step3_code = _validate_executables(integrated=self.native)
        self.validate_manifest(self.manifest_name, look)
        self.roster = self.doc("roster.json")
        self.receipts = self.roster["receipt_commit"]
        # The manifest and receipts independently bind to this pre-read
        # commit. The collection may have closed before final registration.
        require(self.book.ancestor(self.receipts, self.commit), "unproven receipt chronology")

    def read(self, name):
        if name not in self.cache:
            self.cache[name] = self.book.working(name, self.commit, self.hashes[name])
        return self.cache[name]

    def doc(self, name):
        return decode(self.read(name))

    def _manifest(self, name, look):
        payload = self.read(name)
        require(payload == self.book.blob(self.registration, name),
                "manifest differs from its initial commitment")
        doc = decode(payload)
        require(doc["look_id"] == look and doc["look_kind"] == "description"
                and doc["status"] == "committed", "wrong manifest route or status")
        return doc

    def validate_manifest(self, name, look):
        doc = self.manifest if name == self.manifest_name else self._manifest(name, look)
        expected_paths = _pin_paths(look)
        require(doc["code_pins"].keys() == expected_paths.keys(), "wrong manifest pin inventory")
        for role, path in expected_paths.items():
            pin = doc["code_pins"][role]
            require(pin["path"] == path and token(pin["sha256"], SHA), "wrong manifest pin")
            require(digest(self.read(path)) == pin["sha256"]
                    and exact_path(CODE_ROOT / path).read_bytes() == self.read(path),
                    "executing code differs from its manifest pin")
        registry = f"{CONTROL}/filler-kit-registry.json"
        require(exact_path(CODE_ROOT / registry).read_bytes() == self.read(registry),
                "filler registry differs from the executing registry")
        # The final validator sets up its standard descriptors. A spent look
        # must refuse before starting that child, including when checking a peer.
        self._require_unspent_destinations()
        result = subprocess.run(
            [sys.executable, "-B", "-m", "joulewise.cadence_looks.manifest_dispatch",
             "validate", str(self.book.root / name), "--final"],
            cwd=CODE_ROOT, capture_output=True, check=False,
        )
        expected_notice = f"ok {look} (committed)\n".encode()
        require((result.returncode, result.stdout, result.stderr) == (0, expected_notice, b""),
                "final manifest validator refused")
        require(self.book.working(name, self.commit, self.hashes[name]) == self.read(name),
                "manifest changed during final validation")
        require(doc["channels"] == list(CHANNELS) and doc["rail_sum_columns"] == list(RAILS),
                "wrong ordered channel or rail inventory")
        require(len(doc["prints"]) == 4 and doc["outputs"]["custody_names"] ==
                list(private_names(look == IDS[0])), "wrong print inventory")
        if look == IDS[2]:
            expected_index = f"{CAMPAIGN}/f2-stab/KITS.json" if self.native else "f2-stab/KITS.json"
            require(doc["kit_index_path"] == expected_index, "wrong later-kit index")
        return doc

    def source(self, name):
        raw = self.read(name)
        require(self.book.tree(self.receipts).get(name) == self.book.tree(self.commit).get(name),
                "input does not belong to the closed source snapshot")
        return decode(raw)

    def _destinations(self, root):
        public_root = _absolute(root, self.row["public_root"])
        custody_root = _absolute(root, self.row["custody_root"])
        copy_root = _absolute(root, self.copy["root"])
        require(custody_root.is_absolute() and copy_root.is_absolute()
                and Path(self.row["custody_root"]).is_absolute() and Path(self.copy["root"]).is_absolute(),
                "custody and copy must have host-absolute bindings")
        if self.native:
            require(Path(self.row["public_root"]).is_absolute(),
                    "the native public destination must be host-absolute")
        for directory in (public_root, custody_root, copy_root):
            exact_path(directory, directory=True)
        require(_disjoint(public_root, custody_root, copy_root)
                and _disjoint(root, copy_root, custody_root), "overlapping source and destination roots")
        self.copy_root = copy_root
        self.restricted = custody_root / self.look / "RESTRICTED"
        self.public = public_path(public_root / self.look / "PUBLIC.json")
        for path in (self.restricted, self.public):
            exact_path(path.parent, directory=True)
        self._require_unspent_destinations()
        require(self.restricted.parent.stat().st_dev == self.public.parent.stat().st_dev,
                "publication requires one filesystem")

    def _require_unspent_destinations(self):
        require(not os.path.lexists(self.restricted) and not os.path.lexists(self.public),
                "look already reserved or published")

    def public_record(self, census):
        return {
            "look_id": self.look, "manifest_sha256": self.row["sha256"],
            "commit": self.commit, "stage1_sha256": self.row["stage1_sha256"],
            **census["counts"],
        }

    def validate_public(self, candidate, expected):
        require(type(candidate) is dict and candidate.keys() == expected.keys(),
                "unexpected public record fields")
        require(all(type(candidate[key]) is type(value) and candidate[key] == value
                    for key, value in expected.items()), "public record disagrees with its source")
        return canonical(candidate)

    def check_stage1(self, census):
        require(self.row["stage1_path"] == self.stage_name
                and token(self.row["stage1_sha256"], SHA), "invalid stage-1 binding")
        raw = self.book.working(self.stage_name, self.commit, self.row["stage1_sha256"])
        require(raw == canonical(census), "stage 1 disagrees with its source snapshot")


def _kit_path(snapshot, kit_id):
    if not snapshot.native:
        return f"kits/{kit_id}.json"
    candidates = [path for path in snapshot.hashes if path.startswith(f"{CAMPAIGN}/")
                  and Path(path).name in (f"{kit_id}.json", f"{kit_id}.v1.1.json",
                                          f"{kit_id}.v1.1a.json", f"{kit_id}.qual-pin.v1.1.json")]
    require(len(candidates) == 1,
            "native kit path was not uniquely committed")
    return candidates[0]


def _row_pairs(rows):
    require(type(rows) is list, "invalid kit index")
    pairs = {}
    for row in rows:
        require(row.keys() == {"kit_id", "sha256"} and token(row["sha256"], SHA)
                and type(row["kit_id"]) is str and row["kit_id"] not in pairs,
                "invalid or repeated kit commitment")
        pairs[row["kit_id"]] = row["sha256"]
    return pairs


def _positions(kit):
    return [tuple(leg[name] for name in POSITION_FIELDS) for leg in kit["legs"]]


def _mode_rule(kit):
    rules = [item["text"] for item in kit["inclusion_rules"] if item["id"] == "block_power_mode"]
    require(len(rules) == 1 and "Automatic (pmset powermode 0)" in rules[0],
            "kit does not require Automatic power mode")
    return rules[0]


def _kit(snapshot, kit_id, expected, parallel=None):
    path = _kit_path(snapshot, kit_id)
    require(snapshot.hashes[path] == expected, "wrong kit bytes")
    kit = snapshot.source(path)
    require(kit["campaign_id"] == kit_id and token(kit["frozen"]["commit"], OID),
            "wrong kit identity")
    positions = _positions(kit)
    require([row[0] for row in positions] == [f"L{i:03}" for i in range(1, 13)]
            and all(row[1] in (256, 2000, 19458) and row[3:] == ("q600", "own")
                    for row in positions), "wrong nominal kit cells")
    mode_rule = _mode_rule(kit)
    if parallel is not None:
        require(positions == _positions(parallel) and mode_rule == _mode_rule(parallel),
                "stability kit changes positional work")
    else:
        cap = {"f2-inst-01": 512, "f2-inst-02": 128, "f2-inst-03": 256}[kit_id]
        require(all(row[2] == cap for row in positions), "wrong instrument cap")
    return kit


def _later_member(snapshot, index_path, kit_id, expected, receipt_paths):
    # Each receipt path has a separately proved first appearance. A strict
    # ancestor must already name this exact ID and hash on the main line.
    first_receipts = []
    for path in receipt_paths:
        history = snapshot.book.history(snapshot.receipts, path)
        require(bool(history), "later kit has no receipt provenance")
        first_receipts.append(history[-1])
    for commit in snapshot.book.history(snapshot.receipts, index_path):
        if index_path not in snapshot.book.tree(commit):
            continue
        if _row_pairs(decode(snapshot.book.blob(commit, index_path))).get(kit_id) == expected:
            if all(commit != receipt and snapshot.book.ancestor(commit, receipt)
                   for receipt in first_receipts):
                return
    raise Refusal("index did not name the exact kit before its first receipt")


def _admitted_kits(snapshot, rows):
    commitments = snapshot.doc(f"{CONTROL}/look-kit-commitments.v2.json")
    series = IDS[0] if snapshot.instrument else IDS[1]
    required = commitments[series]["kit_sha256_by_id"]
    require(_row_pairs(snapshot.manifest["kits"]) == required, "wrong description population")
    registry = snapshot.doc(f"{CONTROL}/filler-kit-registry.json")["kit_sha256_by_id"]
    require(all(registry.get(kit_id) == bound for kit_id, bound in required.items()),
            "base kit does not match filler registry")

    base = None if snapshot.instrument else _kit(
        snapshot, "f2-inst-01", commitments[IDS[0]]["kit_sha256_by_id"]["f2-inst-01"])
    kits = {kit_id: _kit(snapshot, kit_id, bound, base) for kit_id, bound in required.items()}
    if snapshot.look == IDS[2]:
        index_path = snapshot.manifest["kit_index_path"]
        index = _row_pairs(snapshot.doc(index_path))
        require(all(token(kit_id, STABILITY_KIT) and int(kit_id[-2:]) > 14
                    for kit_id in index), "invalid later stability kit ID")
        receipt_paths = defaultdict(set)
        for row in rows:
            kit_id = row["key"].split("/", 1)[0]
            if kit_id not in kits and "receipt" in row:
                receipt_paths[kit_id].add(row["receipt"])
        for kit_id, paths in receipt_paths.items():
            expected = index[kit_id]
            _later_member(snapshot, index_path, kit_id, expected, paths)
            kits[kit_id] = _kit(snapshot, kit_id, expected, base)
    return kits


def _disposition(op, receipt, cap):
    if op["g0_outcome"] != "released":
        return "unreleased"
    if op["leg_status"] != "complete":
        return "incomplete"
    if not any(end - start >= 600_000_000_000 for start, end in op["quiet_spans_ns"]):
        return "short_hold"
    if receipt["power_mode"] != "Automatic":
        return "wrong_mode"
    if op["decode_tokens"] != cap:
        return "short"
    if not op["decode_cap_reached"]:
        return "cap_not_reached"
    return "qualified"


def _predecessor(snapshot, receipt, closes):
    pointer = receipt.get("predecessor")
    if pointer is None:
        return None
    previous = closes[pointer["entry_id"]]
    require(previous == dict(pointer, host=snapshot.row["execution_host"], proven=True)
            and previous["proven"] is True and number(previous["close_epoch_s"])
            and type(previous["kind"]) is str and bool(previous["kind"]),
            "unproven host predecessor")
    return previous


def _token_row(snapshot, references, kit, plan, closes):
    require(references.keys() == {"key", "issue", "receipt", "leg_record", *DESK_RECORDS},
            "invalid position source inventory")
    issue = snapshot.source(references["issue"])
    receipt = snapshot.source(references["receipt"])
    op = snapshot.source(references["leg_record"])
    key = references["key"]
    kit_id, leg_id = key.split("/")
    kit_sha = snapshot.hashes[_kit_path(snapshot, kit_id)]
    span_id, attempt, roster = receipt["span_id"], receipt["attempt"], receipt["legs"]
    require(receipt["closed"] is True and receipt["kit_id"] == kit_id
            and receipt["kit_sha256"] == kit_sha and type(span_id) is str and bool(span_id)
            and integer(attempt, 1) and receipt["runner_pin"] == kit["frozen"]["commit"]
            and type(roster) is list and 1 <= len(roster) <= (3 if snapshot.instrument else 1)
            and all(token(item, LEG) for item in roster) and len(set(roster)) == len(roster)
            and leg_id in roster and issue == {field: receipt[field] for field in SPAN_FIELDS},
            "receipt does not close its issued roster")
    require(receipt["fresh_soak"] is True, "no fresh soak for the issued span")
    prefix = str(relative(references["receipt"]).parent)
    require(references["issue"] == f"{prefix}/issue.json"
            and references["leg_record"] == f"{prefix}/legs/{leg_id}/leg_record.json"
            and op["leg_id"] == leg_id, "position is not physically bound to its issue")
    for role in DESK_RECORDS:
        require(references[role] == f"{prefix}/{role}.json", "wrong desk evidence source")
        evidence = snapshot.source(references[role])
        require(evidence["span_id"] == span_id and type(evidence["attempt"]) is int
                and evidence["attempt"] == attempt and evidence["record"] == role
                and evidence["passed"] is True, "desk evidence does not prove this attempt")

    require(type(op["decode_cap_reached"]) is bool and type(op["loaded_flag"]) is bool
            and integer(op["decode_tokens"])
            and (op["prefill_tokens"] is None or integer(op["prefill_tokens"]))
            and type(op["quiet_spans_ns"]) is list
            and all(type(span) is list and len(span) == 2 and all(integer(t) for t in span)
                    and span[0] <= span[1] for span in op["quiet_spans_ns"])
            and number(receipt["t0_epoch_s"]), "malformed operational count or stamp")
    require(type(op["leg_status"]) is str and type(op["g0_outcome"]) is str
            and type(receipt["power_mode"]) is str, "invalid operational disposition input")
    disposition = _disposition(op, receipt, plan["decode_tokens"])
    instant = datetime.fromtimestamp(receipt["t0_epoch_s"], LOCAL)
    token_row = {
        "kit_id": kit_id, "kit_sha256": kit_sha, "span_id": span_id, "attempt": attempt,
        "position": int(leg_id[1:]), "leg_id": leg_id,
        "nominal_prefill_tokens": plan["prefill_tokens"], "decode_cap": plan["decode_tokens"],
        "realised_prefill_tokens": op["prefill_tokens"], "realised_decode_tokens": op["decode_tokens"],
        "local_t0_date": instant.date().isoformat(), "leg_status": op["leg_status"],
        "decode_cap_reached": op["decode_cap_reached"], "loaded_flag": op["loaded_flag"],
        "disposition": disposition,
        "missing_count_reason": (op["leg_status"] if op["prefill_tokens"] is None else None),
    }
    position = {
        "disposition": disposition, "loaded_flag": op["loaded_flag"],
        "receipt": references["receipt"], "span_id": span_id, "attempt": attempt,
    }
    predecessor = None if snapshot.instrument else _predecessor(snapshot, receipt, closes)
    detail = (op, receipt, instant, predecessor, token_row)
    return position, token_row, detail


def _paper_wording(table):
    contributing = [row for row in table if row["disposition"] == "qualified"]
    per_kit = defaultdict(dict)
    for row in contributing:
        per_kit[row["kit_id"]][row["position"]] = (
            row["realised_prefill_tokens"], row["realised_decode_tokens"])
    pairs = list(per_kit.values())
    same_work = (bool(pairs) and len(pairs[0]) == 12
                 and all(None not in pair for pair in pairs[0].values())
                 and all(kit == pairs[0] for kit in pairs))
    return "the same work" if same_work else "the same cell of work"


def _check_schedule(snapshot, dates):
    other = IDS[2] if snapshot.look == IDS[1] else IDS[1]
    name = snapshot.manifest_name.replace(snapshot.look, other)
    snapshot.validate_manifest(name, other)
    event = snapshot.doc(AUTHORITY["events"])
    require(event["first_proven_close"] == snapshot.receipts, "no identified due close")
    lock = [row for row in snapshot.ledger["looks"] if row.get("event") == "paper1_data_lock"]
    require(len(lock) <= 1 and event["paper1_data_lock"] is bool(lock)
            and (not lock or lock[0]["receipt_commit"] == snapshot.receipts),
            "data lock is not committed for this cut")
    peer = [row.get("status") for row in snapshot.ledger["looks"] if row.get("look_id") == other]
    if snapshot.look == IDS[1]:
        if lock:
            require(peer == ["coalesced"] and event["coalesced"] == [IDS[2]],
                    "early lock requires a committed coalescence")
        else:
            require(dates >= 14 and not event["coalesced"], "first stability read is not due")
    else:
        require(lock and not event["coalesced"] and event["previous_read"] == IDS[1]
                and event["previous_status"] == "completed" and peer == ["completed"],
                "second stability read is not due")


def census(snapshot):
    rows = snapshot.roster["rows"]
    require(type(rows) is list and all(type(row["key"]) is str for row in rows),
            "malformed commitment roster")
    kits = _admitted_kits(snapshot, rows)
    closes = {} if snapshot.instrument else snapshot.source(AUTHORITY["host_closes"])
    positions, details, table = {}, {}, []
    counts_by_kit = defaultdict(Counter)
    spans = defaultdict(set)
    issued = {}
    for row in sorted(rows, key=lambda entry: entry["key"]):
        key = row["key"]
        require(key not in positions and key.count("/") == 1, "duplicate or malformed position")
        kit_id, leg_id = key.split("/")
        require(kit_id in kits and token(leg_id, LEG), "unregistered position")
        kit = kits[kit_id]
        plan = kit["legs"][int(leg_id[1:]) - 1]
        if "drop" in row:
            drop = snapshot.source(row["drop"])
            require(row.keys() == {"key", "drop"} and drop["key"] == key
                    and drop["status"] == "dropped" and type(drop["authority"]) is str
                    and bool(drop["authority"]), "unproven terminal drop")
            position = {"disposition": "dropped", "loaded_flag": None, "drop": row["drop"]}
        else:
            position, token_row, detail = _token_row(snapshot, row, kit, plan, closes)
            table.append(token_row)
            details[key] = detail
            identity = (kit_id, position["span_id"])
            binding = (position["attempt"], position["receipt"], tuple(detail[1]["legs"]))
            require(issued.setdefault(identity, binding) == binding, "conflicting span attempts")
            spans[identity].add(leg_id)
        positions[key] = position
        counts_by_kit[kit_id][position["disposition"]] += 1
    require(all(spans[identity] == set(binding[2]) for identity, binding in issued.items()),
            "receipt names positions absent from the snapshot")
    if snapshot.instrument:
        require(len(positions) == 36, "instrument population is not terminal")
    qualified = [row for row in table if row["disposition"] == "qualified"]
    counts = {"n_legs": len(qualified)}
    result = {
        "look_id": snapshot.look,
        "source_snapshot": {"receipt_commit": snapshot.receipts,
                            "input_hashes_sha256": digest(canonical(snapshot.hashes))},
        "counts": counts, "positions": positions,
        "by_kit": {kit: dict(counts) for kit, counts in counts_by_kit.items()},
    }
    if not snapshot.instrument:
        dates = len({row["local_t0_date"] for row in qualified})
        _check_schedule(snapshot, dates)
        counts["n_local_dates"] = dates
        result.update(token_table=table, paper_wording=_paper_wording(table))
        if snapshot.look == IDS[2]:
            result["source_snapshot"]["kit_index_sha256"] = snapshot.hashes[
                snapshot.manifest["kit_index_path"]]
    return result, {key: detail for key, detail in details.items()
                    if positions[key]["disposition"] == "qualified"}


def verify_gates(snapshot, qualified):
    manifest_hash = snapshot.row["sha256"]
    cold = snapshot.doc(AUTHORITY["cold"])
    require(cold["look_id"] == snapshot.look and cold["manifest_sha256"] == manifest_hash
            and cold["passed"] is True, "missing exact-manifest cold pass")
    freeze = snapshot.doc(AUTHORITY["freeze"])
    effective = freeze["freeze2_sha256"]
    ruling = freeze.get("ruling", {})
    require(freeze["look_id"] == "lm-interim-01" and token(effective, SHA)
            and (freeze["twin_agrees"] == "yes"
                 or (type(ruling.get("id")) is str and bool(ruling["id"])
                     and ruling["effective_sha256"] == effective)), "no effective freeze")
    native = snapshot.doc(AUTHORITY["first_native"])
    require(native["gate"] == "native" and native["passed"] is True, "native hand-read pending")
    if snapshot.instrument:
        piece = snapshot.doc(AUTHORITY["piece1"])
        require(piece["gate"] == "piece1" and piece["passed"] is True, "piece-1 hand-read pending")

    attestation = snapshot.copy
    require(attestation["verified"] is True and attestation["receipt_commit"] == snapshot.receipts
            and attestation["execution_host"] == snapshot.row["execution_host"],
            "copy verification does not bind this snapshot and host")
    entries = attestation["files"]
    for name, sha in entries.items():
        relative(name)
        require(token(sha, SHA), "malformed copy attestation entry")
    sources = {}
    for key in qualified:
        sources[key] = {}
        for filename in VALUE_FILES:
            name = f"{key}/{filename}"
            require(name in entries, "copy verification omits a per-leg input")
            sources[key][filename] = exact_path(snapshot.copy_root / relative(name))
    return sources


MEASURES = ("mean_w", "sd10_w", "sd40_w", "sd128_w", "turn_j")
# Crossing timestamps and the shared recovery grid follow RL-188 §4.
RAIL_CROSSING_STAMP = "interval_start"
DC_CROSSING_STAMP = "interpolated"
RECOVERY_WINDOW_STRIDE_S = 10
RECOVERY_WINDOW_S = 10
STEP3_COMMIT = "eb449af6404ad302fd8e659fa733f97665044c5f"
STEP3_PATH = "joulewise/cadence_looks/step3_energy_ratios.py"
STEP3_SHA256 = "84a1a5530ab06e688b000c84f248b2c4e561e8330f37d3132ec47aa2572eb173"


def missing(reason, bound=None):
    null = {"value": None, "reason": reason}
    if bound is not None:
        null["bound_s"] = bound
    return null


def _quality_null(*operands):
    for reason in ("rail_manifest", "coverage", "meter_gap", "crossed_before_span",
                   "meter_absent", "meter_contaminated"):
        for operand in operands:
            if isinstance(operand, dict) and operand["reason"] == reason:
                return operand
    return None


def difference(left, right):
    if number(left) and number(right):
        return left - right
    return _quality_null(left, right) or missing("missing_operand")


def deviation(samples):
    return stdev(samples) if len(samples) >= 2 else missing("fewer_than_two")


def _ratios(levels):
    numerator = levels["dc_in"]
    ratios = {}
    for channel in CHANNELS[:2]:
        denominator = levels[channel]
        ratio = {"numerator": numerator, "denominator": denominator}
        if number(numerator) and number(denominator) and denominator > 0:
            ratio["value"] = numerator / denominator
        elif refused := _quality_null(numerator, denominator):
            ratio.update(missing(refused["reason"]))
        else:
            reason = ("nonpositive_denominator" if number(denominator) and denominator <= 0
                      else "missing_operand")
            ratio.update(missing(reason))
        ratios[channel] = ratio
    return ratios


def _step3_code(*, integrated):
    path = CODE_ROOT / STEP3_PATH
    if integrated or os.path.lexists(path):
        source = exact_path(path).read_bytes()
    else:
        # Development can use the owner's immutable Git blob while the two
        # accepted revisions are still on separate lines.
        source = subprocess.check_output(
            ["git", "--no-replace-objects", "-C", str(CODE_ROOT),
             "show", f"{STEP3_COMMIT}:{STEP3_PATH}"],
            env=_git_environment(), stderr=subprocess.PIPE,
        )
    require(digest(source) == STEP3_SHA256, "pinned step-3 reader has different bytes")
    return compile(source, STEP3_PATH, "exec")


def _load_step3(code):
    mod = ModuleType("_description_pinned_step3")
    exec(code, mod.__dict__)
    return mod


def step3_reader():
    """Load the pinned reader for the invented row comparator."""
    return _load_step3(_step3_code(integrated=False))


def _max_gap(intervals, start, stop):
    edge, gap = start, 0.0
    for left, right in intervals:
        if right <= start:
            continue
        if left >= stop:
            break
        gap = max(gap, left - edge)
        edge = max(edge, min(right, stop))
    return max(gap, stop - edge)


def _sample_count(times, a, b):
    return bisect_left(times, b) - bisect_left(times, a)


def _series(values):
    require(type(values) is list and all(number(t) for t in values)
            and all(a < b for a, b in zip(values, values[1:])), "invalid ordered sample stamps")
    return values


def _period(value):
    require(number(value) and value > 0, "invalid sample period")
    return value


def _meter_slice(times, a, b):
    left = bisect_right(times, a) - 1
    right = bisect_left(times, b)
    return (left, right) if left >= 0 and right < len(times) else None


def _float(text):
    value = float(text)
    require(math.isfinite(value), "invalid numeric stream value")
    return value


def _rail_rows(stream):
    """Yield a row with its structural identity and stamp."""
    reader = csv.DictReader(stream)
    fields = ("interval_start_s", "interval_end_s", "timestamp_s", "source", "rail", "power_w")
    require(reader.fieldnames == list(fields), "wrong rail file columns")
    for row in reader:
        if row["source"] != "powermetrics" or row["rail"] not in RAILS:
            continue
        left, right, stamp = (_float(row[key]) for key in fields[:3])
        require(left < right and left <= stamp <= right, "invalid rail interval")
        yield ((left, right), row["rail"]), stamp, row


_JSON_STRUCTURE = re.compile(rb'"(?:[^"\\]|\\.)*"|[{}\[\],:]')
_JSON_CLOSERS = {ord("{"): ord("}"), ord("["): ord("]")}


def _support_metadata(stream):
    """Decode timing and health fields and keep only the sensor byte offsets."""
    payload = stream.read()
    stack = []
    expect_key, sensor_key = True, False
    sensor_start = sensor_span = None
    for token in _JSON_STRUCTURE.finditer(payload):
        start = token.start()
        symbol = payload[start]
        if len(stack) == 1 and stack[0] == ord("}"):
            if expect_key and symbol == ord('"'):
                sensor_key = decode(payload[start:token.end()]) == "sensors"
                expect_key = False
            elif sensor_key and symbol == ord(":") and sensor_start is None:
                sensor_start = token.end()
            elif symbol in (ord(","), ord("}")):
                if sensor_start is not None:
                    require(sensor_span is None, "duplicate JSON field")
                    sensor_span = (sensor_start, start)
                    sensor_start = None
                expect_key, sensor_key = True, False
        if symbol in _JSON_CLOSERS:
            stack.append(_JSON_CLOSERS[symbol])
        elif symbol in (ord("]"), ord("}")):
            require(bool(stack) and stack.pop() == symbol, "unbalanced support JSON")
    require(not stack, "unbalanced support JSON")
    if sensor_span is not None:
        start, end = sensor_span
        payload = payload[:start] + b"null" + payload[end:]
    metadata = decode(payload)
    require(type(metadata) is dict, "support metadata is not a JSON object")
    return metadata, sensor_span


class Signals:
    """A leg's timed intervals and single gateway to scoring values."""

    def __init__(self, support, paths, mark_read, pinned, *, sensor_source=None):
        self.meta = support
        self.paths = paths
        self.mark_read = mark_read
        self.pinned = pinned
        self._sensor_source = sensor_source
        self.sum_admitted = support["rail_manifest"] == list(RAILS)
        self._read_started = False
        self._rail_stamps = None
        self._observed_rails = None
        self._rail_end = None
        self._meter_verified = False
        self._rail_values = {}
        self._meter_values = {}
        self.periods = support["sample_period_s"]
        for name in ("hold", "rail_edge", "dc_edge"):
            _period(self.periods[name])
        self.sidecar = _series(support["sidecar_times"])
        self.meter = _series(support["meter_times"])
        counts = support["meter_counts"]
        # RL-166 Q7. The clean flag describes the stream's lifecycle. Its
        # trailer counters describe the span. Each print judges its own stamps.
        self.meter_clean = (
            support["meter_present"] is True and support["meter_clean"] is True
            and integer(counts["decoded"], 2) and counts["decoded"] == len(self.meter)
            and integer(counts["bad"]) and integer(counts["usb_errors"])
        )
        self.bounds = [tuple(row) for row in support["rail_intervals"]]
        require(all(len(row) == 2 and all(number(t) for t in row) and row[0] < row[1]
                    for row in self.bounds)
                and all(first[1] <= second[0] for first, second in zip(self.bounds, self.bounds[1:])),
                "invalid support interval ledger")
        missing_rails = support.get("rail_missing", {})
        for rail, gaps in missing_rails.items():
            require(rail in RAILS and all(len(row) == 2 and all(number(x) for x in row)
                                         and row[0] < row[1] for row in gaps),
                    "invalid missing-rail support")
        self._declared_rails = self._rail_support({
            channel: [(a, b) for a, b in self.bounds
                      if not any(a < end and b > start for start, end in missing_rails.get(rail, ()))]
            for channel, rail in RAIL_CHANNELS.items()
        })

    @staticmethod
    def _rail_support(individual):
        # Every component must supply the same start and end for a sum sample.
        common = sorted(set.intersection(*(set(intervals) for intervals in individual.values())))
        return {channel: ([a for a, _ in bounds], bounds)
                for channel, bounds in {**individual, "rail_sum": common}.items()}

    def _expected_samples(self, a, b, edge_period):
        split = min(b, max(a, self.meta["turn_start_s"]))
        return (split - a) / self.periods["hold"] + (b - split) / self.periods[edge_period]

    def _coverage_passes(self, channel, a, b, rail_support):
        if channel == "dc_in":
            minimum = MIN_SAMPLE_COVERAGE * self._expected_samples(a, b, "dc_edge")
            if _sample_count(self.meter, a, b) < minimum:
                return False
        elif rail_support:
            minimum = MIN_SAMPLE_COVERAGE * self._expected_samples(a, b, "rail_edge")
            if any(_sample_count(starts, a, b) < minimum for starts, _ in rail_support):
                return False
        minimum = MIN_SAMPLE_COVERAGE * ((b - a) / self.periods["hold"])
        return _sample_count(self.sidecar, a, b) >= minimum

    def _interval_refusal(self, channel, a, b, rail_support):
        if not self._coverage_passes(channel, a, b, rail_support):
            return "coverage"

        lo = max(0, bisect_right(self.sidecar, a) - 1)
        hi = bisect_left(self.sidecar, b)
        sidecar = self.sidecar[lo:hi + 1]
        if (not sidecar or sidecar[0] - a > 2 or b - sidecar[-1] > 2
                or any(end - start > 2 for start, end in zip(sidecar, sidecar[1:]))):
            return "meter_gap"
        if channel == "dc_in":
            limits = _meter_slice(self.meter, a, b)
            if limits is None:
                return "meter_gap"
            lo, hi = limits
            if any(self.meter[i + 1] - self.meter[i] > 2 for i in range(lo, hi)):
                return "meter_gap"
        elif rail_support:
            period = "rail_edge" if b > self.meta["turn_start_s"] else "hold"
            if any(_max_gap(bounds, a, b) > max(1.0, 5 * self.periods[period])
                   for _, bounds in rail_support):
                return "meter_gap"
        return None

    def _start_read(self):
        if not self._read_started:
            self.mark_read()
            self._read_started = True

    def _open_signal(self, name):
        self._start_read()
        return self.paths[name].open(encoding="utf-8", newline="")

    def _index_rails(self):
        if self._rail_stamps is not None:
            return
        stamps = {}
        with self._open_signal("power_trace.csv") as stream:
            for key, stamp, _ in _rail_rows(stream):
                require(key not in stamps, "repeated rail in the same interval")
                stamps[key] = stamp
        self._observed_rails = self._rail_support({
            name: [bounds for bounds in self._declared_rails[name][1] if (bounds, rail) in stamps]
            for name, rail in RAIL_CHANNELS.items()
        })
        # The rail channels share one capture. A dropped component at its
        # end changes that channel's coverage, not the observed capture end.
        observed_intervals = {bounds for bounds, _ in stamps}
        self._rail_end = max((b for a, b in self.bounds if (a, b) in observed_intervals),
                             default=None)
        self._rail_stamps = stamps

    def recovery_start(self, sampling):
        self._index_rails()
        observed = [self._observed_rails[channel][0][0] for channel in CHANNELS[:2]
                    if (channel != "rail_sum" or self.sum_admitted)
                    and self._observed_rails[channel][0]]
        if self.meter_clean:
            observed.append(self.meter[0])
        return max([sampling, *observed])

    def stream_end(self, channel):
        if channel == "dc_in":
            return self.meter[-1] if self.meter else None
        self._index_rails()
        return self._rail_end

    def _admitted_rails(self, channel, a, b):
        selected = [bounds for bounds in self._observed_rails[channel][1]
                    if bounds[1] > a and bounds[0] < b]
        names = RAILS if channel == "rail_sum" else (RAIL_CHANNELS[channel],)
        pending = {(bounds, rail) for bounds in selected for rail in names
                   if (bounds, rail) not in self._rail_values}
        if pending:
            with self._open_signal("power_trace.csv") as stream:
                for key, stamp, row in _rail_rows(stream):
                    if key in pending:
                        require(self._rail_stamps[key] == stamp, "rail stamp changed after admission")
                        self._rail_values[key] = _float(row["power_w"])
                        pending.remove(key)
                        if not pending:
                            break
            require(not pending, "rail row disappeared after admission")

        stamp_rail = "gpu_power" if channel == "rail_sum" else names[0]
        rows = [(left, right, sum(self._rail_values[((left, right), rail)] for rail in names),
                 self._rail_stamps[((left, right), stamp_rail)]) for left, right in selected]
        if channel != "gpu_rail":
            return rows

        # The immutable loader sees only rows admitted for this print.
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(("interval_start_s", "interval_end_s", "timestamp_s", "source",
                         "rail", "power_w"))
        for left, right, value, stamp in rows:
            writer.writerow((left, right, stamp, "powermetrics", "gpu_power", value))
        buffer.seek(0)
        self.pinned.open = lambda *_args, **_kwargs: buffer
        try:
            return self.pinned.load_gpu_trace(".")
        finally:
            del self.pinned.open

    def _admitted_meter(self, a, b):
        if not self._meter_verified:
            with self._open_signal("dc_points.csv") as stream:
                rows = csv.DictReader(stream)
                require(rows.fieldnames == ["epoch_s", "watts"], "wrong decoded point columns")
                stamps = [_float(row["epoch_s"]) for row in rows]
            require(stamps == self.meter, "decoder stamps disagree with the copy's support")
            self._meter_verified = True
        lo, hi = _meter_slice(self.meter, a, b)
        pending = {i for i in range(lo, hi + 1) if i not in self._meter_values}
        if pending:
            with self._open_signal("dc_points.csv") as stream:
                for i, row in enumerate(csv.DictReader(stream)):
                    if i in pending:
                        require(self.meter[i] == _float(row["epoch_s"]),
                                "decoder stamp changed after admission")
                        self._meter_values[i] = _float(row["watts"])
                        pending.remove(i)
                        if not pending:
                            break
            require(not pending, "decoder point disappeared after admission")
        return [(self.meter[i], self.meter[i + 1], self._meter_values[i],
                 self._meter_values[i + 1]) for i in range(lo, hi)]

    def _interval_quality(self, channel, a, b):
        require(number(a) and number(b) and a < b, "invalid print interval")
        require(channel in (*RAIL_CHANNELS, "rail_sum", "dc_in", "sidecar"), "unknown channel")
        if channel == "rail_sum" and not self.sum_admitted:
            return "rail_manifest"

        if channel == "rail_sum":
            rail_channels = (*RAIL_CHANNELS, "rail_sum")
        else:
            rail_channels = (channel,) if channel in RAIL_CHANNELS else ()
        if rail_channels:
            # The declared support can prove a deficit. Only the observed
            # identities can establish that coverage passed before the gap checks.
            if not self._coverage_passes(channel, a, b,
                                        [self._declared_rails[name] for name in rail_channels]):
                return "coverage"
            self._index_rails()
        reason = self._interval_refusal(
            channel, a, b, [self._observed_rails[name] for name in rail_channels],
        )
        if reason is None and channel == "dc_in" and not self.meter_clean:
            return "meter_absent" if self.meta["meter_present"] is False else "meter_contaminated"
        return reason

    def interval_values(self, channel, interval):
        """Admit sample counts and gaps before interpreting the interval's values."""
        a, b = interval
        reason = self._interval_quality(channel, a, b)
        if reason:
            return missing(reason)
        if channel == "sidecar":
            if self._sensor_source is None:
                return self.meta["sensors"]
            stream, (start, end) = self._sensor_source
            self._start_read()
            stream.seek(start)
            return decode(stream.read(end - start))
        if channel == "dc_in":
            return self._admitted_meter(a, b)
        return self._admitted_rails(channel, a, b)

    def energy(self, channel, a, b):
        rows = self.interval_values(channel, (a, b))
        if isinstance(rows, dict):
            return rows
        if channel != "dc_in":
            return self.pinned.Trace(rows).energy(a, b)
        total = 0.0
        for left, right, low, high in rows:
            lo, hi = max(left, a), min(right, b)
            p0 = low + (high - low) * (lo - left) / (right - left)
            p1 = low + (high - low) * (hi - left) / (right - left)
            total += (p0 + p1) * 0.5 * (hi - lo)
        return total

    def average(self, channel, a, b):
        energy = self.energy(channel, a, b)
        return energy / (b - a) if number(energy) else energy

    def cross(self, channel, a, b, threshold, *, falls=False):
        rows = self.interval_values(channel, (a, b))
        if isinstance(rows, dict):
            return rows
        if channel == "dc_in":
            return _dc_crossing(rows, a, b, threshold, falls)
        for index, (left, _, watts, stamp) in enumerate(rows):
            if (watts <= threshold if falls else watts >= threshold):
                if index == 0:
                    return missing("crossed_before_span")
                return left if RAIL_CROSSING_STAMP == "interval_start" else stamp
        return missing("crossing_unobserved")


def _dc_crossing(rows, a, b, threshold, falls):
    def crossed(value):
        return value <= threshold if falls else value >= threshold

    # RL-188 §4.1 uses observations in the search span. The integration
    # brackets carried by these rows can extend outside that span.
    for left, right, low, high in rows:
        if a <= left <= b and crossed(low):
            return missing("crossed_before_span")
        if right > b:
            break
        if right < a or not crossed(high):
            continue
        if left < a:
            return missing("crossed_before_span")
        if DC_CROSSING_STAMP == "first_sample":
            return right
        return left + (threshold - low) * (right - left) / (high - low)
    return missing("crossing_unobserved")


def _hold(signal, start, instrument):
    result = {}
    for channel in CHANNELS:
        printed = {"mean_w": signal.average(channel, start, start + 600), "kept": [], "dropped": []}
        for width in WIDTHS:
            windows = []
            reasons = []
            for index in range(600 // width):
                a = start + index * width
                value = signal.average(channel, a, a + width)
                if number(value):
                    windows.append((a + width / 2, value))
                else:
                    reasons.append(value["reason"])
            if reasons:
                printed.setdefault("drop_reasons", {})[str(width)] = reasons
            printed[f"sd{width}_w"] = deviation([value for _, value in windows])
            printed["kept"].append(len(windows))
            printed["dropped"].append(600 // width - len(windows))
            if instrument and width == 10:
                printed["drift_w_per_600s"] = _drift(windows)
        result[channel] = printed
    return result


def _drift(windows):
    if len(windows) < 2:
        return missing("fewer_than_two")
    x_mid = mean(x for x, _ in windows)
    y_mid = mean(y for _, y in windows)
    numerator = sum((x - x_mid) * (y - y_mid) for x, y in windows)
    denominator = sum((x - x_mid) ** 2 for x, _ in windows)
    return 600 * numerator / denominator


def _above_hold(signal, channel, hold, start, stop, *, average):
    if not number(hold):
        reason = signal._interval_quality(channel, start, stop)
        return missing(reason) if reason else hold
    energy = signal.energy(channel, start, stop)
    if not number(energy):
        return energy
    if average:
        return energy / (stop - start) - hold
    return energy - hold * (stop - start)


def _sensors(keys, readings):
    if isinstance(readings, dict):
        return readings, {}
    rpm = []
    sensors = defaultdict(list)
    for record in readings:
        fans = record["fan_keys"]
        if keys and all(key in fans and number(fans[key]) for key in keys):
            rpm.append(mean(fans[key] for key in keys))
        for name, value in record.items():
            if name != "fan_keys" and number(value):
                sensors[name].append(value)
    fan = mean(rpm) if rpm else missing("no_complete_fan_reading")
    return fan, {name: mean(values) for name, values in sensors.items()}


def _recovery(signal, channel, start, origin, hold, spread, stop):
    reasons = []
    if not number(hold) or not number(spread):
        return missing("hold_or_sd_undefined"), reasons
    threshold = hold + 2 * spread
    complete = max(0, 1 + math.floor((stop - start - RECOVERY_WINDOW_S)
                                    / RECOVERY_WINDOW_STRIDE_S))
    last_end = start
    for index in range(complete):
        a = start + index * RECOVERY_WINDOW_STRIDE_S
        last_end = a + RECOVERY_WINDOW_S
        value = signal.average(channel, a, last_end)
        if not number(value):
            reason = value["reason"]
            reasons.append("gap_over_u1" if reason == "meter_gap" else reason)
        elif value <= threshold:
            elapsed = a - origin
            return (missing("under", elapsed) if index == 0 else elapsed), reasons
    return missing("not returned", last_end - origin), reasons


def _edge_prints(signal, hold, decode, turn, first, last, quiet_start, prompt):
    meta = signal.meta
    clock = meta["clock"]
    real_shift = clock["trace_anchor_s"] - clock["raw_anchor_s"]
    fallback = meta["completion_log_raw_s"] is None
    stage = meta["warmup_stage_raw_s"] + real_shift
    origin = stage - 5 if fallback else meta["completion_log_raw_s"] + real_shift
    sampling = meta["sampling_started_raw_s"] + real_shift
    gap = missing("no_completion_log") if fallback else stage - origin
    anchor = signal.recovery_start(sampling)
    return_times, rise, onsets, offsets, censored = {}, {}, {}, {}, {}
    skip_counts, skip_reasons = {}, {}
    end = last + 1
    for channel in CHANNELS:
        baseline = hold[channel]["mean_w"]
        stream_end = signal.stream_end(channel)
        recovery_stop = min(quiet_start + 600, stream_end) if stream_end is not None else anchor
        return_times[channel], reasons = _recovery(
            signal, channel, anchor, origin, baseline, hold[channel]["sd10_w"], recovery_stop,
        )
        skip_counts[channel] = len(reasons)
        if reasons:
            skip_reasons[channel] = reasons
        if prompt == 256:
            rise[channel] = onsets[channel] = missing("prefill shorter than the level window")
        else:
            level = _above_hold(signal, channel, baseline, (turn + first) / 2, first, average=True)
            if number(level) and level > 0:
                crosses = [signal.cross(channel, turn, first, baseline + fraction * level)
                           for fraction in (0.1, 0.5, 0.9)]
                rise[channel] = difference(crosses[2], crosses[0])
                onsets[channel] = crosses[1]
            else:
                rise[channel] = onsets[channel] = (
                    level if isinstance(level, dict) else missing("prefill_level_undefined")
                )
        plateau = decode[channel]
        if number(baseline) and number(plateau) and plateau > 0:
            offsets[channel] = signal.cross(channel, last, end, baseline + plateau / 2, falls=True)
        else:
            offsets[channel] = plateau if isinstance(plateau, dict) else missing("decode_plateau_undefined")
        if channel != "dc_in":
            if number(baseline) and stream_end is not None and stream_end > last:
                rail_return = signal.cross(channel, last, stream_end, baseline, falls=True)
                if number(rail_return):
                    censored[channel] = rail_return - last
                elif rail_return["reason"] == "crossing_unobserved":
                    censored[channel] = missing("stream_end", stream_end - last)
                elif rail_return["reason"] in ("coverage", "meter_gap"):
                    censored[channel] = missing(rail_return["reason"], stream_end - last)
                else:
                    censored[channel] = rail_return
            else:
                censored[channel] = baseline if isinstance(baseline, dict) else missing("rail_return_undefined")
    decode_lags = {}
    for channel in CHANNELS[:2]:
        lag = difference(offsets["dc_in"], offsets[channel])
        if not number(lag):
            reasons = {value.get("reason") for value in (offsets["dc_in"], offsets[channel])
                       if isinstance(value, dict)}
            if reasons == {"crossing_unobserved"}:
                lag = missing("over 1 s", 1.0)
        decode_lags[channel] = lag
    onset_lags = {channel: difference(onsets["dc_in"], onsets[channel]) for channel in CHANNELS[:2]}
    if prompt == 256:
        onset_lags = {channel: onsets[channel] for channel in CHANNELS[:2]}
    result = {
        "fallback": fallback, "gap_outside": not fallback and not 4.5 <= gap <= 5.5,
        "completion_to_stage_s": gap, "unobserved_s": anchor - origin,
        "recovery_s": return_times, "rail_return_censor_s": censored,
        "recovery_resolution_s": dict.fromkeys(CHANNELS, RECOVERY_WINDOW_S),
        "recovery_skipped_windows": skip_counts,
        "resolution_s": dict(zip(CHANNELS, (signal.periods["rail_edge"], signal.periods["rail_edge"],
                                           signal.periods["dc_edge"]))),
        "rise_s": rise, "onset_lag_s": onset_lags, "decode_end_lag_s": decode_lags,
    }
    if skip_reasons:
        result["recovery_skip_reasons"] = skip_reasons
    return result


def print_leg(signal, detail, instrument):
    op, _, _, _, row = detail
    meta = signal.meta
    start, first, last = (meta[name] for name in ("turn_start_s", "first_token_s", "last_token_s"))
    require(all(number(t) for t in (start, first, last)) and start < first < last,
            "invalid projected turn stamps")
    # The operational record supplies the hold interval for every print.
    quiet = next(lo for lo, hi in op["quiet_spans_ns"] if hi - lo >= 600_000_000_000) / 1e9
    hold = _hold(signal, quiet, instrument)
    baseline = {channel: hold[channel]["mean_w"] for channel in CHANNELS}
    energy = {channel: _above_hold(signal, channel, baseline[channel], start, last + 1, average=False)
              for channel in CHANNELS}
    turn = {"energy_j": energy, "dc_tail_cut": True}
    result = {"hold": hold, "turn": turn}
    if not instrument:
        return result
    prompt = row["nominal_prefill_tokens"]
    turn["ratios"] = _ratios(energy)
    decode_w = {channel: _above_hold(signal, channel, baseline[channel], first, last, average=True)
                for channel in CHANNELS}
    prefill_w = missing("not_long_prefill")
    prefill_gain = missing("not_long_prefill")
    if prompt == 19458:
        prefill_w = {channel: _above_hold(signal, channel, baseline[channel], start, first, average=True)
                     for channel in CHANNELS}
        prefill_gain = _ratios(prefill_w)
    floors = {}
    for channel, watts in decode_w.items():
        floors[channel] = []
        for width in WIDTHS:
            sd = hold[channel][f"sd{width}_w"]
            value = _quality_null(watts, sd) or missing("decode_or_sd_undefined")
            if number(sd) and number(watts) and watts > 0:
                value = sd * width * row["realised_decode_tokens"] / (watts * (last - first))
            floors[channel].append(value)
    readings = signal.interval_values("sidecar", (quiet, quiet + 600))
    fan, sensors = _sensors(meta["host_fan_keys"], readings)
    result["gain"] = {
        "decode_w": decode_w, "long_prefill_w": prefill_w, "decode_gain": _ratios(decode_w),
        "long_prefill_gain": prefill_gain, "idle_dc_minus_sum_w": difference(baseline["dc_in"],
                                                                            baseline["rail_sum"]),
        "mean_fan_rpm": fan, "mean_start_c": sensors, "floor_tokens": floors,
    }
    result["edges"] = _edge_prints(signal, hold, decode_w, start, first, last, quiet, prompt)
    return result


def _date_summaries(context):
    spreads = {}
    for cell, items in context.items():
        grouped = defaultdict(list)
        failures = Counter()
        for detail in items.values():
            value = detail["value"]
            if number(value):
                grouped[detail["date"]].append(value)
            else:
                failures[value["reason"]] += 1
        dates = {day: {"n": len(values), "mean": mean(values), "sd": deviation(values)}
                 for day, values in grouped.items()}
        df = sum(len(values) - 1 for values in grouped.values())
        variance = sum((value - dates[day]["mean"]) ** 2 for day, values in grouped.items()
                       for value in values)
        spread = {
            "dates": dates, "singleton_dates": sum(row["n"] == 1 for row in dates.values()),
            "sd_date_means": deviation([row["mean"] for row in dates.values()]),
            "pooled_within_sd": math.sqrt(variance / df) if df else missing("no_within_date_df"),
        }
        if failures:
            spread["missing"] = dict(failures)
        spreads[cell] = spread
    return spreads


def _context(hold, turn, qualified):
    context = {f"{prompt}/{channel}/{measure}": {} for prompt in (256, 2000, 19458)
               for channel in CHANNELS for measure in MEASURES}
    for key, (_, receipt, instant, predecessor, row) in qualified.items():
        gap = receipt["t0_epoch_s"] - predecessor["close_epoch_s"] if predecessor else None
        location = {
            "date": instant.date().isoformat(), "hour": instant.hour,
            "utc_offset_s": int(instant.utcoffset().total_seconds()),
            "predecessor_kind": predecessor["kind"] if predecessor else None, "gap_s": gap,
            "status": "unknown" if gap is None else "negative_gap" if gap < 0 else "known",
        }
        for channel in CHANNELS:
            values = [hold[key][channel][measure] for measure in MEASURES[:-1]]
            values.append(turn[key]["energy_j"][channel])
            for measure, value in zip(MEASURES, values):
                cell = f'{row["nominal_prefill_tokens"]}/{channel}/{measure}'
                context[cell][key] = dict(location, value=value)
    return context


def score(snapshot, sources, qualified, mark_read):
    files = {name.removesuffix(".json"): {} for name in private_names(snapshot.instrument)
             if name.endswith(".json")}
    # Reuse preflight's verified code. Scoring must not resolve a different
    # dependency after the worker has spent the one-use reservation.
    pinned = _load_step3(snapshot.step3_code) if qualified else None
    for key, detail in qualified.items():
        paths = sources[key]
        with paths["support.json"].open("rb") as stream:
            support, sensor_span = _support_metadata(stream)
            sensor_source = (stream, sensor_span) if snapshot.instrument and sensor_span else None
            signal = Signals(support, paths, mark_read, pinned, sensor_source=sensor_source)
            for name, value in print_leg(signal, detail, snapshot.instrument).items():
                files[name][key] = value
    if not snapshot.instrument:
        files["context"] = _context(files["hold"], files["turn"], qualified)
        files["date_spreads"] = _date_summaries(files["context"])
    return files


# The final manifest pins this inventory through the reader SHA-256.
EXECUTABLE_DEPENDENCIES = {
    "scripts/cadence_description_run.py":
        "6a16157e3e071518c78d71b1f1e01b3818d8008c32a76339ff764346ab9ad60c",
    "joulewise/cadence_looks/description_worker.py":
        "d152d6841ace94104893907f7300918efe6ba505b5c1e444c5450be1b4a85c1a",
    "joulewise/cadence_looks/transfer_release.py":
        "9f826ee253b4f4039d5172c3e3535b6003e9499593bf3166907bb15d4776d953",
    "joulewise/__init__.py":
        "df98d6ea46fd21ec24bb8fc4c208e4e01f5167e6c7f2af36490781779d5710cc",
    "joulewise/schemas.py":
        "f47fbf68c2c4a931854995d1258425b476c4bc8a686dfccf011d9caef092cc3b",
    "joulewise/axi_decode_config.py":
        "fab53ea66a636458bb8c36f0c5f5f3f014478db8351e246746c9b6bc7c62dd93",
    "joulewise/idle_admission.py":
        "9dc6b5d45c1dc138a13195b64cd1ca23eac0427c864063f26e274775b5a5a79e",
    "joulewise/validation.py":
        "82bb03f3aed626446298d186e845b7fe75b3371ca6cbabd7160946bd8e7bfcfd",
}


def _validate_executables(*, integrated):
    for path, expected in EXECUTABLE_DEPENDENCIES.items():
        require(digest(exact_path(CODE_ROOT / path).read_bytes()) == expected,
                "executing dependency differs from its reader inventory")
    return _step3_code(integrated=integrated)
