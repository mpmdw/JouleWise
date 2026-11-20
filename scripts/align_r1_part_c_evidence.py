"""In-process evidence binding for Part C (RL-183c). No native reads at import."""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
from secrets import token_hex
from stat import S_ISDIR, S_ISREG
from subprocess import run

LEDGER_NAME = "evidence_ledger.jsonl"
MANIFEST_NAME = "runtime_custody.json"
MANIFEST_SCHEMA = "joulewise.align.r1_runtime_custody.v1"
SOAK_SEGMENT = "idle_soak"
SOAK_DIRECTORY = "soak"
SOAK_ROW = "soak_row.json"
SOAK_REFERENCE = "soak_reference.json"
BATTERY_SOURCE = "battery.jsonl"
SOAK_FILES = ("runtime_result.json", "sensors/align_thermal.jsonl", "load_journal.json", BATTERY_SOURCE)
D = re.compile(r"[0-9a-f]{64}\Z")
# RL-189 1.2: the member row's witness of <model.source>/config.json.
DESCRIPTOR_FIELD = "model_descriptor_sha256"
DESCRIPTOR_WORDS = ("absent", "unreadable")
DESCRIPTOR_SOURCE = "model.source/config.json"
KINDS = {
    "capture-predecessor-30b": "capture_predecessor_30b",
    "step-d": "step_D_prefill_10k_decode_4096",
    "d-bank-benign-s1": "D_bank_benign_s1_gated_held",
    "x-g": "X_G_contrast",
}


class EvidenceFailure(ValueError):
    def __init__(self, reason, role, source, *, index=None, field=None, peer=None):
        super().__init__(reason)
        self.reason = reason
        self.role = role
        self.source = source
        self.index = index
        self.field = field
        self.peer = peer

    def finding(self, verdict="other_failure"):
        return {"verdict": verdict, "reason": self.reason, "role": self.role,
                "file_or_stream": self.source, "row_or_index": self.index,
                "field": self.field, "peer": self.peer}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def _unique_members(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON field")
    return obj


def _reject_constant(_):
    raise ValueError("non-finite JSON constant")


def _finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("JSON number overflows")
    return value


def parse_json(text):
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="strict")
    return json.loads(text, object_pairs_hook=_unique_members, parse_constant=_reject_constant,
                      parse_float=_finite_float)


def stdout_payload(text, kind):
    """Check the frozen transport's text before interpreting JSON."""
    if (not isinstance(text, str) or
            (text and (not text.endswith("\n") or any(not 32 <= ord(c) <= 126 for c in text[:-1])))):
        raise EvidenceFailure("stdout_receipt", kind, "stdout", field="invalid")
    if not text:
        return None
    try:
        value = parse_json(text)
    except (ValueError, TypeError, RecursionError) as error:
        raise EvidenceFailure("stdout_receipt", kind, "stdout", field="invalid") from error
    if not isinstance(value, dict):
        raise EvidenceFailure("stdout_receipt", kind, "stdout", field="invalid")
    return value


def _parts(relative):
    path = Path(relative)
    if path.is_absolute() or not path.parts or path.as_posix() != relative or ".." in path.parts:
        raise ValueError("invalid relative evidence path")
    return path.parts


def read_regular(root, relative, *, compressed=False):
    """Read only a regular file beneath a real directory, without following links."""
    *parents, basename = _parts(relative)
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    file_flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW
    with ExitStack() as stack:
        directory = os.open(root, directory_flags)
        stack.callback(os.close, directory)
        for parent in parents:
            directory = os.open(parent, directory_flags, dir_fd=directory)
            stack.callback(os.close, directory)
        try:
            fd = os.open(basename, file_flags, dir_fd=directory)
        except FileNotFoundError:
            if not compressed:
                raise
            fd = os.open(basename + ".zst", file_flags, dir_fd=directory)
            is_compressed = True
        else:
            is_compressed = False
        stack.callback(os.close, fd)
        if not S_ISREG(os.fstat(fd).st_mode):
            raise ValueError("not a regular evidence file")
        if not is_compressed:
            try:
                os.stat(basename + ".zst", dir_fd=directory, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise ValueError("ambiguous plain and compressed evidence")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            if is_compressed:
                from joulewise.desk_compress import zstd_path

                proc = run([zstd_path(), "-dqc"], stdin=stream, capture_output=True)
                if proc.returncode != 0:
                    raise ValueError("invalid compressed evidence")
                return proc.stdout
            return stream.read()


def observe_descriptor(source):
    """Observe the bytes frozen ``prepare`` reads for the native limit (WL:265-268).

    Returns the witness (a sha256, ``absent`` or ``unreadable``) and the bytes.
    The read follows links exactly as the frozen ``read_text`` does. It never raises.
    """
    try:
        if not isinstance(source, str) or not source:
            return "unreadable", None
        raw = (Path(source).expanduser() / "config.json").read_bytes()
    except (FileNotFoundError, NotADirectoryError):
        return "absent", None
    except (OSError, ValueError, RuntimeError):
        return "unreadable", None
    return digest(raw), raw


def native_limit(raw):
    """WL:268-272 applied to descriptor bytes: a positive integer, or None for an unread limit."""
    if raw is None:
        return None
    try:
        # ``Path.read_text()`` decodes with the default text layer; json.loads is the frozen parser.
        value = json.loads(io.TextIOWrapper(io.BytesIO(raw)).read()).get("max_position_embeddings")
        if type(value) is not int or value <= 0:
            raise ValueError("max_position_embeddings must be a positive integer")
    except (OSError, ValueError, AttributeError):
        return None
    return value


def is_descriptor_witness(value):
    return isinstance(value, str) and (value in DESCRIPTOR_WORDS or D.fullmatch(value) is not None)


def _hash_text(value):
    # An unavailable stream has no observation. Its digest is distinct from
    # the empty stream, whose SHA-256 is still recorded.
    return digest(value.encode("utf-8", errors="surrogatepass")) if isinstance(value, str) else None


class EvidenceLedger:
    """Append the exact observed rows and keep the trusted copy in memory."""

    def __init__(self, output, producer_revision, runtime_config, soak_reference=None, *,
                 mode="native", soak=None):
        self.root = Path(output)
        self.path = self.root / LEDGER_NAME
        self.attempt = {"run": self.root.parent.name, "nonce": token_hex(16)}
        self._lines = []
        self._members = {}
        self._bound_members = {}
        self._descriptors = {}
        self.mode = mode
        self._kinds = {"idle": SOAK_SEGMENT} if mode == "soak" else KINDS
        self.runtime_config = Path(runtime_config)
        self._soak = soak
        self.config_sha = self._input_digest(self.runtime_config)
        start = {"attempt": self.attempt, "mode": mode, "producer_revision": producer_revision,
                 "runtime_config": {"path": str(self.runtime_config), "sha256": self.config_sha}}
        if mode == "native":
            self.soak_reference = Path(soak_reference)
            self.soak_sha = self._input_digest(self.soak_reference)
            start["soak_reference"] = {"path": str(self.soak_reference), "sha256": self.soak_sha}
            if soak is not None:
                if (self.config_sha, self.soak_sha) != (soak.config_sha, soak.reference_sha):
                    raise EvidenceFailure("source_integrity", "idle", LEDGER_NAME)
                start.update(soak_ledger={"path": str(soak.path), "sha256": soak.sha256},
                             soak_attempt_nonce=soak.nonce)
        self._append(start)

    @staticmethod
    def _input_digest(path):
        try:
            return digest(read_regular(path.parent, path.name))
        except (OSError, ValueError) as error:
            raise EvidenceFailure("evidence_unverifiable", "attempt", "issued_inputs") from error

    def _append(self, row):
        row = {**row, "previous_sha256": digest(self._lines[-1]) if self._lines else None}
        data = canonical(row) + b"\n"
        if self._lines:
            self.verify_chain()
        try:
            flags = os.O_WRONLY | os.O_NOFOLLOW | os.O_NONBLOCK
            flags |= os.O_APPEND if self._lines else os.O_CREAT | os.O_EXCL
            fd = os.open(self.path, flags, 0o600)
            with os.fdopen(fd, "wb") as stream:
                if not S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise ValueError("ledger must be regular")
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        except (OSError, ValueError) as error:
            raise EvidenceFailure("source_integrity", "attempt", LEDGER_NAME) from error
        self._lines.append(data)
        return row

    def verify_chain(self):
        try:
            actual = read_regular(self.root, LEDGER_NAME)
        except FileNotFoundError as error:
            raise EvidenceFailure("evidence_unverifiable", "attempt", LEDGER_NAME) from error
        except (OSError, ValueError) as error:
            raise EvidenceFailure("source_integrity", "attempt", LEDGER_NAME) from error
        if actual != b"".join(self._lines):
            raise EvidenceFailure("source_integrity", "attempt", LEDGER_NAME)

    def verify_inputs(self):
        self.verify_chain()
        if (self._input_digest(self.runtime_config) != self.config_sha
                or (self.mode == "native" and self._input_digest(self.soak_reference) != self.soak_sha)):
            raise EvidenceFailure("source_integrity", "attempt", "issued_inputs")
        if self._soak is not None:
            self._soak.verify_reads()

    def member_return(self, kind, output, argv, *, process=None, error=None, spawned=None,
                      model_descriptor=None):
        """Bind a return before interpreting its streams or opening a member file.

        ``model_descriptor`` is the judged invoker's RL-189 witness for a member
        that was launched. It joins this row and no other.
        """
        segment = self._kinds.get(kind)
        if segment is None or Path(output) != self.root / segment:
            raise EvidenceFailure("sequence", kind if kind in self._kinds else "attempt", LEDGER_NAME)
        if tuple(self._members) != tuple(self._kinds)[:list(self._kinds).index(kind)]:
            raise EvidenceFailure("sequence", kind, LEDGER_NAME)
        relative = f"{segment}/{MANIFEST_NAME}"
        unreadable = False
        try:
            terminal = {"path": relative, "sha256": digest(read_regular(self.root, relative))}
        except FileNotFoundError:
            terminal = "absent"
        except (OSError, ValueError):
            terminal, unreadable = "absent", True
        if process is None:
            outcome = {"spawned": spawned, "exception": type(error).__name__}
            stdout = stderr = None
        else:
            outcome = {"spawned": True, "exit_status": process.returncode}
            stdout, stderr = process.stdout, getattr(process, "stderr", None)
        row = self._append({"attempt": self.attempt, "kind": kind, "argv_sha256": digest(canonical(argv)),
                            **outcome, "stdout_sha256": _hash_text(stdout), "stderr_sha256": _hash_text(stderr),
                            "segment": segment, "manifest": terminal,
                            **({} if model_descriptor is None else {DESCRIPTOR_FIELD: model_descriptor})})
        self._members[kind] = row
        if unreadable:
            raise EvidenceFailure("source_integrity", kind, MANIFEST_NAME)
        if process is not None and (not isinstance(stdout, str) or not isinstance(stderr, str)):
            raise EvidenceFailure("stdout_receipt", kind, "stdout", field="invalid")

    def member(self, kind):
        self.verify_chain()
        row = self._members.get(kind)
        if row is None or row["manifest"] == "absent":
            raise EvidenceFailure("evidence_unverifiable", kind, MANIFEST_NAME)
        if row["spawned"] is not True or type(row.get("exit_status")) is not int or row["exit_status"] != 0:
            raise EvidenceFailure("process_exit", kind, "stdout")
        if kind not in self._bound_members:
            self._bound_members[kind] = BoundMember(self.root / row["segment"], kind, self.config_sha,
                                                   manifest_sha=row["manifest"]["sha256"], status="complete")
        return self._bound_members[kind]

    @staticmethod
    def descriptor_witness(source):
        """RL-189 1.2: what the judged invoker writes in a launched member's row."""
        return observe_descriptor(source)[0]

    def model_descriptor(self, kind, source):
        """RL-189 D1 and D2: the row's witness must exist and equal the evaluator's own read.

        Returns the bytes behind the attested limit, or None for a bound
        ``absent`` or ``unreadable`` descriptor. The source stays registered
        for the final recheck.
        """
        self.verify_chain()
        row = self._members.get(kind)
        if row is None or not is_descriptor_witness(row.get(DESCRIPTOR_FIELD)):
            raise EvidenceFailure("evidence_unverifiable", kind, LEDGER_NAME, field=DESCRIPTOR_FIELD)
        witness, raw = observe_descriptor(source)
        if witness != row[DESCRIPTOR_FIELD]:
            raise EvidenceFailure("source_integrity", kind, DESCRIPTOR_SOURCE, peer=LEDGER_NAME)
        self._descriptors[kind] = source
        return raw

    def verify_descriptor(self, kind):
        row, source = self._members.get(kind), self._descriptors.get(kind)
        if row is None or source is None or observe_descriptor(source)[0] != row.get(DESCRIPTOR_FIELD):
            raise EvidenceFailure("source_integrity", kind, DESCRIPTOR_SOURCE, peer=LEDGER_NAME)

    def refusal(self, kind):
        self.verify_chain()
        row = self._members.get(kind)
        if row is None:
            raise EvidenceFailure("evidence_unverifiable", kind, LEDGER_NAME)
        pre_exec = row.get("spawned") is False and row.get("exception") == "RuntimeAdmissionRefusal"
        if not pre_exec and (row.get("exit_status") != 2 or row["stdout_sha256"] != _hash_text("")):
            raise EvidenceFailure("x_g_unrun_unproven", kind, "stdout")
        root = self.root / row["segment"]
        try:
            if not S_ISDIR(root.lstat().st_mode):
                raise ValueError("segment is not a real directory")
            entries = {entry.name for entry in root.iterdir()}
        except FileNotFoundError:
            entries = set()
        except (OSError, ValueError) as error:
            raise EvidenceFailure("x_g_unrun_unproven", kind, "segment") from error
        if entries - {MANIFEST_NAME}:
            raise EvidenceFailure("x_g_launch_conflict", kind, "segment")
        if entries:
            if pre_exec:
                raise EvidenceFailure("x_g_launch_conflict", kind, MANIFEST_NAME)
            if row["manifest"] == "absent":
                raise EvidenceFailure("evidence_unverifiable", kind, MANIFEST_NAME)
            proof = BoundMember(root, kind, self.config_sha, manifest_sha=row["manifest"]["sha256"],
                                status="refused")
            if proof.files:
                raise EvidenceFailure("x_g_launch_conflict", kind, MANIFEST_NAME)
        elif row["manifest"] != "absent":
            raise EvidenceFailure("source_integrity", kind, MANIFEST_NAME)

    def finish(self, verdict, copies):
        if not self._lines or b'"verdict":' in self._lines[-1]:
            raise EvidenceFailure("verdict_binding", "attempt", LEDGER_NAME)
        self._append({"verdict": verdict, "emitted_sha256": dict(copies)})
        self.verify_chain()

    def finish_soak(self, outcome):
        if self.mode != "soak" or len(self._lines) != 2 or outcome not in ("accepted", "refused"):
            raise EvidenceFailure("evidence_unverifiable", "idle", LEDGER_NAME)
        digests = {}
        for file in (SOAK_ROW, SOAK_REFERENCE):
            try:
                digests[Path(file).stem + "_sha256"] = digest(read_regular(self.root, file))
            except FileNotFoundError as error:
                if outcome == "accepted":
                    raise EvidenceFailure("evidence_unverifiable", "idle", file) from error
                digests[Path(file).stem + "_sha256"] = "absent"
        if outcome == "accepted":
            self.verify_final_sources()
        self._append({"outcome": outcome, **digests})
        self.verify_chain()

    def verify_final_sources(self):
        self.verify_inputs()
        for bound in self._bound_members.values():
            bound.verify_reads()
        for kind in self._descriptors:
            self.verify_descriptor(kind)
        contrast = self._members.get("x-g")
        if contrast is not None and "x-g" not in self._bound_members:
            self.refusal("x-g")


class BoundMember:
    """Validate one manifest and bind each consumed byte stream to it."""
    def __init__(self, root, kind, config_sha, *, manifest_sha, status="complete", archived=False):
        self.root, self.kind = Path(root), kind
        self.archived = archived
        raw = self._read(MANIFEST_NAME, MANIFEST_NAME)
        self.manifest_sha = manifest_sha if manifest_sha is not None else digest(raw)
        if digest(raw) != self.manifest_sha:
            raise EvidenceFailure("source_integrity", kind, MANIFEST_NAME)
        manifest = self._object(raw, MANIFEST_NAME)
        begin, end = manifest.get("started_epoch_s"), manifest.get("ended_epoch_s")
        valid_times = all(type(value) in (int, float) and math.isfinite(value) for value in (begin, end))
        expected_config = manifest.get("config_sha256")
        valid_config = expected_config == config_sha or (status == "refused" and "config_sha256" not in manifest)
        if (manifest.get("schema") != MANIFEST_SCHEMA or manifest.get("kind") != kind
                or manifest.get("status") != status or not valid_times or begin > end
                or not valid_config or manifest.get("teardown_errors")
                or not isinstance(manifest.get("files"), dict)):
            raise EvidenceFailure("terminal_evidence", kind, MANIFEST_NAME)
        self.started_epoch_s, self.ended_epoch_s = begin, end
        self.files = manifest["files"]
        self._read_files = {}

    def _read(self, relative, source):
        try:
            return read_regular(self.root, relative, compressed=self.archived)
        except (OSError, TypeError, ValueError) as error:
            raise EvidenceFailure("source_integrity", self.kind, source) from error

    def _object(self, raw, source):
        try:
            value = parse_json(raw)
        except (ValueError, TypeError, RecursionError) as error:
            raise EvidenceFailure("terminal_evidence", self.kind, source, field="invalid") from error
        if not isinstance(value, dict):
            raise EvidenceFailure("terminal_evidence", self.kind, source, field="invalid")
        return value

    def read(self, relative, source):
        expected = self.files.get(relative)
        if not isinstance(expected, str) or D.fullmatch(expected) is None:
            raise EvidenceFailure("evidence_unverifiable", self.kind, source)
        data = self._read(relative, source)
        if digest(data) != expected:
            raise EvidenceFailure("source_integrity", self.kind, source)
        self._read_files[relative] = source
        return data

    def verify_reads(self):
        if digest(self._read(MANIFEST_NAME, MANIFEST_NAME)) != self.manifest_sha:
            raise EvidenceFailure("source_integrity", self.kind, MANIFEST_NAME)
        for relative, source in self._read_files.items():
            if digest(self._read(relative, source)) != self.files[relative]:
                raise EvidenceFailure("source_integrity", self.kind, source)


def _is_digest(value):
    return isinstance(value, str) and D.fullmatch(value) is not None


class BoundSoak:
    """The launcher-bound soak observation required before the native row 0."""

    def __init__(self, output, soak_reference, ledger_sha, producer_revision, runtime_config):
        output = Path(output)
        self.root = output.parent / SOAK_DIRECTORY
        self.path = self.root / LEDGER_NAME
        self.sha256 = ledger_sha

        # 1. The launcher's digest must be present and must bind the ledger.
        if not _is_digest(ledger_sha):
            raise EvidenceFailure("evidence_unverifiable", "idle", LEDGER_NAME)
        raw = self._read(LEDGER_NAME, ledger_sha, missing="evidence_unverifiable")

        # 2. The three complete rows must show a successful idle invocation.
        physical = raw.split(b"\n")
        if len(physical) < 4:
            raise EvidenceFailure("evidence_unverifiable", "idle", LEDGER_NAME, field="missing")
        invalid = EvidenceFailure("fresh_soak", "idle", LEDGER_NAME, field="invalid")
        if len(physical) != 4 or physical[-1]:
            raise invalid
        try:
            start, returned, closed = (parse_json(row) for row in physical[:3])
        except (ValueError, TypeError, RecursionError) as error:
            raise invalid from error
        shapes = (
            {"attempt", "mode", "producer_revision", "runtime_config"},
            {"attempt", "kind", "argv_sha256", "spawned", "exit_status",
             "stdout_sha256", "stderr_sha256", "segment", "manifest"},
            {"outcome", "soak_row_sha256", "soak_reference_sha256"},
        )
        for index, (row, shape) in enumerate(zip((start, returned, closed), shapes, strict=True)):
            previous = digest(physical[index - 1] + b"\n") if index else None
            if not isinstance(row, dict) or set(row) - {"previous_sha256"} != shape:
                raise invalid
            if "previous_sha256" not in row:
                raise EvidenceFailure("evidence_unverifiable", "idle", LEDGER_NAME, index=index, field="missing")
            if row["previous_sha256"] != previous:
                raise EvidenceFailure("source_integrity", "idle", LEDGER_NAME, index=index)
        if (start["mode"] != "soak" or returned["kind"] != "idle"
                or returned["segment"] != SOAK_SEGMENT or closed["outcome"] != "accepted"
                or returned["spawned"] is not True or type(returned["exit_status"]) is not int
                or returned["exit_status"] != 0
                or not all(_is_digest(returned[key]) for key in ("stdout_sha256", "stderr_sha256", "argv_sha256"))):
            raise invalid

        # 3. The kit and soak must refer to this attempt and these issued inputs.
        self.config_sha = EvidenceLedger._input_digest(Path(runtime_config))
        attempt = start["attempt"]
        if (not isinstance(attempt, dict) or set(attempt) != {"run", "nonce"}
                or attempt["run"] != output.parent.name or attempt != returned["attempt"]
                or not isinstance(attempt["nonce"], str) or re.fullmatch(r"[0-9a-f]{32}", attempt["nonce"]) is None
                or start["producer_revision"] != producer_revision
                or start["runtime_config"] != {"path": str(runtime_config), "sha256": self.config_sha}
                or output.name != "part-c" or soak_reference is None
                or Path(soak_reference) != self.root / SOAK_REFERENCE):
            raise EvidenceFailure("fresh_soak", "idle", LEDGER_NAME, field="disagrees", peer="issued_inputs")
        self.nonce = attempt["nonce"]

        # 4. Bind both outer files before parsing either one.
        self.row_sha, self.reference_sha = closed["soak_row_sha256"], closed["soak_reference_sha256"]
        outer_row = self._read(SOAK_ROW, self.row_sha)
        outer_reference = self._read(SOAK_REFERENCE, self.reference_sha)

        # 5. Bind the segment's manifest and each required file through it.
        manifest = returned["manifest"]
        if not isinstance(manifest, dict) or not _is_digest(manifest.get("sha256")):
            raise EvidenceFailure("evidence_unverifiable", "idle", MANIFEST_NAME)
        if set(manifest) != {"path", "sha256"} or manifest["path"] != f"{SOAK_SEGMENT}/{MANIFEST_NAME}":
            raise EvidenceFailure("fresh_soak", "idle", MANIFEST_NAME, field="disagrees", peer=LEDGER_NAME)
        self.member = BoundMember(self.root / SOAK_SEGMENT, "idle", self.config_sha,
                                  manifest_sha=manifest["sha256"])
        self.sources = {name: self.member.read(name, name) for name in SOAK_FILES}

        # 6. The outer row, saved receipt and stdout must be the same observation.
        self.row = self._object(outer_row, SOAK_ROW)
        self.reference = self._object(outer_reference, SOAK_REFERENCE)
        result = self._object(self.sources[SOAK_FILES[0]], SOAK_FILES[0])
        segment = self.root / SOAK_SEGMENT
        reported_output = self.row.get("output_dir")
        if (self.row.get("name") != SOAK_SEGMENT or type(self.row.get("attempt")) is not int
                or self.row["attempt"] != 0 or not isinstance(reported_output, str)
                or Path(reported_output).resolve() != segment.resolve()
                or self.reference.get("source_segment") != SOAK_SEGMENT
                or self.reference.get("source_output") != reported_output
                or type(self.reference.get("attempt")) is not int or self.reference["attempt"] != 0):
            raise EvidenceFailure("fresh_soak", "idle", SOAK_ROW, field="disagrees", peer=SOAK_REFERENCE)
        if canonical(self.row.get("result")) != canonical(result):
            raise EvidenceFailure("receipt_pair", "idle", SOAK_ROW, field="disagrees", peer=SOAK_FILES[0])
        line = json.dumps(result, sort_keys=True, allow_nan=False) + "\n"
        if _hash_text(line) != returned["stdout_sha256"]:
            raise EvidenceFailure("receipt_pair", "idle", SOAK_FILES[0], field="disagrees", peer="stdout")
        self.verify_reads()

    def _read(self, filename, expected, *, missing="source_integrity"):
        if not _is_digest(expected):
            raise EvidenceFailure("evidence_unverifiable", "idle", filename)
        try:
            raw = read_regular(self.root, filename)
        except FileNotFoundError as error:
            raise EvidenceFailure(missing, "idle", filename) from error
        except (OSError, ValueError) as error:
            raise EvidenceFailure("source_integrity", "idle", filename) from error
        if digest(raw) != expected:
            raise EvidenceFailure("source_integrity", "idle", filename)
        return raw

    @staticmethod
    def _object(raw, source):
        try:
            result = parse_json(raw)
        except (ValueError, TypeError, RecursionError) as error:
            raise EvidenceFailure("fresh_soak", "idle", source, field="invalid") from error
        if not isinstance(result, dict):
            raise EvidenceFailure("fresh_soak", "idle", source, field="invalid")
        return result

    def verify_reads(self):
        self._read(LEDGER_NAME, self.sha256, missing="evidence_unverifiable")
        self._read(SOAK_ROW, self.row_sha)
        self._read(SOAK_REFERENCE, self.reference_sha)
        self.member.verify_reads()


def verify_part_c_publication(run_root, soak_ledger_sha256, soak_reference_sha256):
    """Verify a zero-exit kit's two verdict copies, terminal ledger row and stdout."""
    root = Path(run_root)
    output = root / "part-c"
    role = "attempt"

    def require(condition, source):
        if not condition:
            raise EvidenceFailure("verdict_binding", role, source)

    def read(directory, source):
        try:
            return read_regular(directory, source)
        except (OSError, ValueError) as error:
            raise EvidenceFailure("verdict_binding", role, source) from error

    def obj(raw, source):
        try:
            value = parse_json(raw)
        except (ValueError, TypeError, RecursionError) as error:
            raise EvidenceFailure("verdict_binding", role, source, field="invalid") from error
        require(isinstance(value, dict), source)
        return value

    physical = read(output, LEDGER_NAME).split(b"\n")
    require(len(physical) == len(KINDS) + 3 and physical[-1] == b"", LEDGER_NAME)
    previous = None
    rows = []
    for line in physical[:-1]:
        row = obj(line, LEDGER_NAME)
        require("previous_sha256" in row and row["previous_sha256"] == previous, LEDGER_NAME)
        rows.append(row)
        previous = digest(line + b"\n")

    start, *members, final = rows
    attempt = start.get("attempt")
    require(isinstance(attempt, dict) and attempt.get("run") == root.name
            and isinstance(attempt.get("nonce"), str) and re.fullmatch(r"[0-9a-f]{32}", attempt["nonce"])
            and start.get("mode") == "native", LEDGER_NAME)
    require(_is_digest(soak_ledger_sha256) and _is_digest(soak_reference_sha256)
            and start.get("soak_ledger") == {"path": str(root / SOAK_DIRECTORY / LEDGER_NAME),
                                              "sha256": soak_ledger_sha256}
            and start.get("soak_reference") == {"path": str(root / SOAK_DIRECTORY / SOAK_REFERENCE),
                                                 "sha256": soak_reference_sha256}, LEDGER_NAME)
    soak = root / SOAK_DIRECTORY
    require(digest(read(soak, LEDGER_NAME)) == soak_ledger_sha256, LEDGER_NAME)
    require(digest(read(soak, SOAK_REFERENCE)) == soak_reference_sha256, SOAK_REFERENCE)
    for row, (kind, path) in zip(members, KINDS.items(), strict=True):
        require(row.get("attempt") == attempt and row.get("kind") == kind and row.get("segment") == path,
                LEDGER_NAME)
        require(_is_digest(row.get("argv_sha256")), LEDGER_NAME)
        code, manifest = row.get("exit_status"), row.get("manifest")
        # RL-189: a judged member's row carries its descriptor witness.
        completed = (type(code) is int and code == 0 and row.get("spawned") is True
                     and isinstance(manifest, dict) and manifest.get("path") == f"{path}/{MANIFEST_NAME}"
                     and _is_digest(manifest.get("sha256")) and _is_digest(row.get("stdout_sha256"))
                     and _is_digest(row.get("stderr_sha256"))
                     and is_descriptor_witness(row.get(DESCRIPTOR_FIELD)))
        refused = (kind == "x-g" and (
            type(code) is int and code == 2 and row.get("spawned") is True
            and row.get("stdout_sha256") == _hash_text("") and _is_digest(row.get("stderr_sha256"))
            or row.get("spawned") is False and row.get("exception") == "RuntimeAdmissionRefusal"
            and manifest == "absent"
        ) and (DESCRIPTOR_FIELD not in row or is_descriptor_witness(row[DESCRIPTOR_FIELD])))
        require(completed or refused, LEDGER_NAME)

    names = ("smoke_part_c.json", "smoke.json")
    copies = {name: read(output, name) for name in names}
    require(copies[names[0]] == copies[names[1]], "smoke.json")
    require(final.get("verdict") == "pass" and final.get("emitted_sha256") == {
        name: digest(raw) for name, raw in copies.items()}, LEDGER_NAME)
    published = obj(copies[names[0]], names[0])
    judged = published.get("evaluation")
    require(published.get("part") == "C" and published.get("slots_entered") is False
            and isinstance(judged, dict) and judged.get("schema") == "joulewise.align.r1_part_c.v1"
            and judged.get("verdict") == "pass" and judged.get("pass") is True
            and judged.get("evidence_failures") == {} and judged.get("slots_entered") is False, names[0])
    stream = "part-c.stdout.log"
    stdout = read(root, stream)
    lines = stdout.splitlines(keepends=True)
    announcement = b"Part C verdict: pass (pass: True)\n"
    require(lines and lines[-1] == announcement
            and sum(line.startswith(b"Part C verdict:") for line in lines) == 1, stream)
