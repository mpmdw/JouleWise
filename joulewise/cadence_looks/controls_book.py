"""Immutable first-parent authority and installed byte projections for ctl-01."""

from hashlib import sha1, sha256
import os
from pathlib import Path
import subprocess
import sys

from .controls_layout import GateRefusal, plain_bytes
from .controls_manifest import CODE_PATHS, INSTRUMENT_ID, LOOK_DIR, validate_manifest
from .controls_print import LOOK_ID, _hex_pin
from .custody_pins import safe_relative
from .qualification_manifest import _decode


REF = "refs/remotes/origin/main"
ORIGIN = "https://github.com/mpmdw/JouleWise.git"
LOOKS = LOOK_DIR + "LOOKS.json"
MANIFEST = LOOK_DIR + "lm-ctl-01.json"
SOURCES = LOOK_DIR + "lm-ctl-01.sources.json"
BYTE_RECEIPT = LOOK_DIR + "lm-ctl-01.byte-pass.json"
INSTRUMENT_STAGE1 = LOOK_DIR + "stage1/lm-inst-01.json"
SUITE = "tests/contracts/cadence_looks/look_path/"
SUITE_NAMES = ("SUITE.sha256", "SUITE-v2.sha256", "SUITE-v3.sha256")
INSTALLED_BUNDLE_RESULT = ("75 raw + 4 superseded "
                           "(RL-202a §2.4; lead record audit branch 1850d6930 SUPERSESSION-v2.md)")
SUPERSESSION_SHA256 = "1c4b7086a03487e1059748364e56061d1175614bf4a4d0c5ff304c542009325d"
KERNEL_ROLES = (
    "print_code/phase", "print_code/attribution", "print_code/records", "print_code/windows",
    "print_code/powermetrics_adapter", "print_code/trace_point", "print_code/integrator",
)
AUDITED_KERNEL = (
    "a924b1f4fe5e4e3d7dee719027e57cdb7548f4d66ec7705ad249d5d6b2ff18f8",
    "805d5d5e0dde33ab54ed943b883f95e5f738bf2391a8c21300f569a0cabb014d",
    "d5b8f8583716ba5419c0c84710ffec30735128a31b056830767dca6d13cccf93",
    "e8a3d5ecaecda79f9214f0569d7a36f47bb3a0237a8721474888332721870391",
    "70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4",
    "8eeae4f575d59447d372ac7184362365cce3b118125791465069ae1a14218403",
    "7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc",
)
GATE_KINDS = (
    "pilot_close", "pilot_hand_read", "remainder_close", "disclosure",
    "split_hand_read", "instrument_read", "freezing_line",
)


def _require(condition):
    if not condition:
        raise GateRefusal("FREEZE")


def _sha(raw):
    return sha256(raw).hexdigest()


def _blob_id(raw):
    return sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def _path(name):
    _require(safe_relative(name) and all(part.casefold() not in (".git", "restricted")
                                         for part in name.split("/")))
    return name


class Book:
    """The #868 tree, history and working checks scoped to authoritative main."""

    def __init__(self, root):
        self.root = root
        self.trees = {}
        self.index = {}
        _require(self.git("rev-parse", "--show-toplevel").decode().rstrip("\n") == str(root))
        _require(self.git("remote", "get-url", "origin").decode().strip() == ORIGIN)
        self.tip = self.head()
        self.first_parents = frozenset(self.git(
            "rev-list", "--first-parent", self.tip
        ).decode().splitlines())
        for row in self.git("ls-files", "--stage", "-z").split(b"\0"):
            if row:
                info, name = row.split(b"\t", 1)
                mode, oid, stage = info.decode().split()
                if stage == "0" and mode in ("100644", "100755"):
                    self.index[os.fsdecode(name)] = oid

    def git(self, *args):
        environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        return subprocess.check_output(["git", "--no-replace-objects", "-C", str(self.root), *args],
                                       env=environment, stderr=subprocess.PIPE)

    def head(self):
        tip = self.git("rev-parse", "--verify", REF + "^{commit}").decode().strip()
        _require(_hex_pin(tip, 40))
        return tip

    def recheck(self):
        _require(self.tip == self.head() == self.public_tip())

    @staticmethod
    def public_tip():
        environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")
        raw = subprocess.check_output(["git", "ls-remote", "--exit-code", ORIGIN, "refs/heads/main"],
                                      cwd="/", env=environment, stderr=subprocess.PIPE, timeout=15)
        revision, ref = raw.decode("ascii").split()
        _require(ref == "refs/heads/main")
        return revision

    def tree(self, revision):
        _require(revision in self.first_parents)
        if revision not in self.trees:
            self.trees[revision] = entries = {}
            for row in self.git("ls-tree", "-rz", revision).split(b"\0"):
                if row:
                    info, name = row.split(b"\t", 1)
                    mode, _, oid = info.decode().split()
                    if mode in ("100644", "100755"):
                        entries[os.fsdecode(name)] = oid
        return self.trees[revision]

    def blob(self, revision, name):
        oid = self.tree(revision).get(_path(name))
        _require(oid is not None)
        return self.git("cat-file", "blob", oid)

    def working(self, name, revision, expected=None):
        oid = self.tree(revision).get(_path(name))
        _require(oid is not None and self.index.get(name) == oid)
        raw = plain_bytes(self.root / name)
        _require(_blob_id(raw) == oid and (expected is None or _sha(raw) == expected))
        return raw

    def history(self, path):
        return tuple(reversed(self.git(
            "log", "--first-parent", "--format=%H", self.tip, "--", _path(path)
        ).decode().splitlines()))

    def reject_private_blobs(self, inputs):
        public = set(self.tree(self.tip).values())
        _require(all(_blob_id(raw) not in public for raw in inputs.values()))


def _ledger(document):
    _require(type(document) is dict and {"schema", "looks"} <= document.keys()
             <= {"schema", "looks", "events"}
             and document["schema"] == "joulewise.cadence_look_ledger.v1"
             and type(document["looks"]) is list
             and type(document.get("events", [])) is list)
    return document


def _look(ledger, look_id, *, required=True):
    rows = [row for row in ledger["looks"] if row["look_id"] == look_id]
    _require(len(rows) == 1 if required else len(rows) <= 1)
    return next(iter(rows), None)


def _valid_look(row):
    _require(row.keys() == {"look_id", "manifest_path", "sha256", "status"}
             and _hex_pin(row["sha256"], 64) and row["status"] == "registered")


def _event(row):
    common = {"kind", "look_id"}
    _require(type(row) is dict and common <= row.keys())
    kind = row["kind"]
    keys = {
        "design_pass": set(), "byte_pass": {"manifest_sha256", "receipt_sha256", "hand_vectors_passed"},
        "receipt": {"manifest_sha256", "revision"}, "stage1": {"stage1_sha256", "n_legs", "manifest_sha256"},
        "dc_disposition": {"sha256", "issuer"},
        "ctl01_withheld": {"reason"}, "reserved": {"manifest_sha256", "stage1_sha256"},
        "first_ctl_read": {"manifest_sha256", "stage1_sha256"}, "published": {"manifest_sha256", "stage1_sha256"},
        **dict.fromkeys(GATE_KINDS, {"sha256"}),
    }
    _require(kind in keys and row.keys() == common | keys[kind])
    for name in keys[kind]:
        if name.endswith("sha256"):
            _require(_hex_pin(row[name], 64))
    if kind == "stage1":
        _require(type(row["n_legs"]) is int and 0 <= row["n_legs"] <= 12)
    if kind == "ctl01_withheld":
        _require(row["reason"] in ("no_dc_in_floor", "no_prefill_size", "dose_under_floor_at_k2"))
    if kind == "dc_disposition":
        _require(row["issuer"] == "research_lead")


class Authority:
    def __init__(self, book):
        self.book = book
        self.revision = None
        self.instrument_revision = None
        self.events = []
        prefix = []
        ctl = instrument = None
        for revision in book.history(LOOKS):
            if LOOKS not in book.tree(revision):
                _require(self.revision is None and not prefix)
                continue
            ledger = _ledger(_decode(book.blob(revision, LOOKS)))
            current = ledger.get("events", [])
            _require(current[:len(prefix)] == prefix)
            ctl_row = _look(ledger, LOOK_ID, required=False)
            instrument_row = _look(ledger, INSTRUMENT_ID, required=False)
            if self.revision is not None:
                _require(ctl == ctl_row)
            elif ctl_row is not None:
                _valid_look(ctl_row)
                _require(ctl_row["manifest_path"] == MANIFEST)
                self.revision, ctl = revision, ctl_row
            if self.instrument_revision is not None:
                _require(instrument == instrument_row)
            elif instrument_row is not None:
                _require(_hex_pin(instrument_row["sha256"], 64))
                self.instrument_revision, instrument = revision, instrument_row
            for row in current[len(prefix):]:
                if row["look_id"] not in (LOOK_ID, INSTRUMENT_ID):
                    continue
                _event(row)
                event = dict(row)
                if row["kind"] == "stage1":
                    event.update(revision=revision, status="committed")
                self.events.append((revision, event))
            prefix = current
        _require(self.revision is not None and self.instrument_revision is not None)
        self.ledger = _ledger(_decode(book.blob(book.tip, LOOKS)))
        _require(self.ledger.get("events", []) == prefix and _look(self.ledger, LOOK_ID) == ctl
                 and _look(self.ledger, INSTRUMENT_ID) == instrument)
        self.manifest = book.blob(self.revision, MANIFEST)
        self.manifest_sha = _sha(self.manifest)
        _require(self.manifest_sha == ctl["sha256"])
        self.document = validate_manifest(self.manifest)
        _require("execution" in self.document)
        self.instrument_row = instrument
        self.history = tuple(row for _, row in self.events)

    def stage_entry(self):
        rows = [row for row in self.history if row["look_id"] == LOOK_ID and row["kind"] == "stage1"]
        _require(len(rows) <= 1)
        return next(iter(rows), None)

    def runtime_sources(self):
        book = self.book
        raw = book.working(SOURCES, self.revision, self.document["execution"]["sources_sha256"])
        document = _decode(raw)
        _require(document.keys() == {"schema", "paths", "python"}
                 and document["schema"] == "joulewise.cadence_ctl_sources.v1"
                 and document["python"] == {
                     "implementation": sys.implementation.name,
                     "version": list(sys.version_info[:3]),
                 })
        pins = document["paths"]
        for name, expected in pins.items():
            _require(name.endswith(".py") and _hex_pin(expected, 64)
                     and name.startswith(("joulewise/", "scripts/")))
            book.working(name, self.revision, expected)
        _require({path for path in CODE_PATHS.values() if path.endswith(".py")} <= pins.keys())
        for module in tuple(sys.modules.values()):
            origin = getattr(module, "__file__", None)
            if origin and Path(origin).is_relative_to(book.root / "joulewise"):
                _require(os.fspath(Path(origin).relative_to(book.root)) in pins)
        return pins

    def verify_authorized_prerequisites(self, bindings, inputs=None):
        gate_events = [(revision, event) for revision, event in self.events
                       if event["look_id"] == LOOK_ID and event["kind"] in GATE_KINDS]
        _require(tuple(row["kind"] for _, row in gate_events) == GATE_KINDS
                 and len({revision for revision, _ in gate_events}) == len(GATE_KINDS))
        gate_hashes = {row["kind"]: row["sha256"] for _, row in gate_events}
        _require(gate_hashes == bindings["gates"])
        final = gate_events[-1][0]
        final_parent = self.book.git("rev-list", "--first-parent", self.revision).decode().splitlines()
        _require(final in final_parent)
        if inputs is not None:
            spans = sorted(inputs.spans.values(), key=lambda span: span["layout_index"])
            _require([row["close_receipt"]["sha256"] for row in spans]
                     == [gate_hashes["pilot_close"], gate_hashes["remainder_close"]])

    def _verify_byte_pass(self):
        book = self.book
        manifest_pins = self.document["pins"]
        _require(tuple(manifest_pins[role] for role in KERNEL_ROLES) == AUDITED_KERNEL)
        rows = [(rev, row) for rev, row in self.events
                if row["kind"] == "byte_pass" and row["look_id"] == LOOK_ID
                and row["manifest_sha256"] == self.manifest_sha]
        _require(len(rows) == 1)
        revision, row = rows[0]
        raw = book.blob(revision, BYTE_RECEIPT)
        _require(_sha(raw) == row["receipt_sha256"])
        receipt = _decode(raw)
        expected = {
            "schema": "joulewise.cadence_ctl_byte_pass.v1",
            "manifest_sha256": self.manifest_sha,
            "sources_sha256": self.document["execution"]["sources_sha256"],
            "kernel_sha256": dict(zip(KERNEL_ROLES, AUDITED_KERNEL, strict=True)),
            "suite_sha256": {name: _sha(book.working(SUITE + name, self.revision)) for name in SUITE_NAMES},
            "v3_1_count": 846,
            "installed_bundle_cases": INSTALLED_BUNDLE_RESULT,
            "supersession_sha256": SUPERSESSION_SHA256,
            "h_output_bytes_equal": True,
        }
        _require(receipt == expected)

    def freeze_inputs(self, *, private, stage1_snapshot=None):
        book = self.book
        self.runtime_sources()
        self._verify_byte_pass()
        working = {"manifest": book.working(MANIFEST, self.revision, self.manifest_sha)}
        current = {"manifest": self.manifest}
        for role, name in CODE_PATHS.items():
            current[role] = book.blob(self.revision, name)
            working[role] = book.working(name, self.revision, self.document["pins"][role])

        floor = self.document["instrument_output_schema"]
        _require(floor["commit"] in book.git("rev-list", "--first-parent", self.revision).decode().splitlines())
        instrument_path = self.instrument_row["manifest_path"]
        current["instrument_manifest"] = book.blob(self.instrument_revision, instrument_path)
        current["instrument_floor_schema"] = book.blob(floor["commit"], floor["path"])
        working["instrument_manifest"] = book.working(instrument_path, self.instrument_revision,
                                                       self.instrument_row["sha256"])
        working["instrument_floor_schema"] = book.working(floor["path"], floor["commit"], floor["sha256"])
        committed = {self.revision: current}
        committed.setdefault(floor["commit"], {})[floor["path"]] = current["instrument_floor_schema"]
        instrument_stage = self.document["instrument_stage1"]["ledger_commit"]
        committed.setdefault(instrument_stage, {})["instrument_stage1"] = book.blob(
            instrument_stage, INSTRUMENT_STAGE1)
        for row in self.history:
            if row["look_id"] == LOOK_ID and row["kind"] == "receipt" and row["revision"] != self.revision:
                committed.setdefault(row["revision"], {})["manifest"] = book.blob(row["revision"], MANIFEST)
        if stage1_snapshot is not None:
            stage = self.stage_entry()
            _require(stage is not None)
            committed.setdefault(stage["revision"], {})["stage1"] = stage1_snapshot
        book.reject_private_blobs(private)
        return dict(current_revision=self.revision, committed=committed, working=working,
                    history=self.history, private=private)
