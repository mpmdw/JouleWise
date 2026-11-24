"""Field and variant coverage for rebound synthetic native inputs."""

from contextlib import contextmanager, nullcontext
from functools import cache, lru_cache
import json
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.cadence_looks import controls_inputs as inputs
from joulewise.cadence_looks import controls_reader as reader
from joulewise.cadence_looks import controls_release as release
from joulewise.cadence_looks import controls_run as worker
from joulewise.cadence_looks import controls_time_fields as wire
from joulewise.cadence_looks.custody_pins import offload_manifest_bytes
from tests.contracts.cadence_looks import look_path_driver as registrar


OPERATIONS = ("stage1", "preflight", "stage2")
FINITE_MIDPOINT = 2**1024 - 2**970


class ShapeAccepted(Exception):
    """Stop a positive probe after the bound record passes its wire shape."""


def wrong_type(schema):
    if isinstance(schema, wire.Nullable):
        return wrong_type(schema.fields)
    if isinstance(schema, wire.TokenForms):
        return {} if "{" not in schema.variants else False
    return [] if schema in (wire.BOOLEAN, wire.OPAQUE_BOOLEAN) else False


def numeric_boundary(schema):
    if isinstance(schema, wire.Nullable):
        return numeric_boundary(schema.fields)
    if schema is wire.INT64:
        return 2**63 - 1, 2**63
    if schema in (wire.INTEGER, wire.OPAQUE_INTEGER, wire.OPAQUE_NONNEGATIVE_INTEGER):
        return 9007199254740993, 1.0
    if schema in (wire.NUMBER, wire.OPAQUE_FINITE_NUMBER, wire.OPAQUE_NONNEGATIVE_NUMBER):
        return FINITE_MIDPOINT - 1, FINITE_MIDPOINT
    if schema is wire.OPAQUE_PERCENT:
        return 100, 101
    return None


def sample(schema):
    if isinstance(schema, wire.Nullable):
        return None
    if isinstance(schema, wire.TaggedFields):
        tag, variant = next(iter(schema.fields.items()))
        return {**sample(variant), schema.tag: tag}
    if isinstance(schema, wire.TokenForms):
        return sample(next(iter(schema.variants.values())))
    if isinstance(schema, wire.DigestFields):
        return {}
    if isinstance(schema, dict):
        required = schema if isinstance(schema, wire.RequiredRecordFields) else schema.required
        return {key: sample(value) for key, value in schema.items() if key in required}
    if isinstance(schema, list):
        return []
    if schema is wire.EMPTY_ARRAY:
        return []
    if schema is wire.OPAQUE_OBJECT or isinstance(schema, wire.KeyedFields):
        return {}
    if schema in (wire.BOOLEAN, wire.OPAQUE_BOOLEAN):
        return True
    if schema in (wire.STRING, wire.OPAQUE_STRING, wire.OPAQUE_NONBLANK_STRING, wire.OPAQUE_STRING_OR_INTEGER):
        return "synthetic"
    return 0


def records(schema, value, path=(), variant=()):
    """Yield each reachable record with a witness for its enclosing variant."""
    if isinstance(schema, wire.Nullable):
        yield from records(schema.fields, sample(schema.fields) if value is None else value, path, variant)
    elif isinstance(schema, wire.TaggedFields):
        for kind, fields in schema.fields.items():
            current = value if value.get(schema.tag) == kind else {**sample(fields), schema.tag: kind}
            yield from records(fields, current, path, (*variant, (path, kind)))
    elif isinstance(schema, wire.TokenForms):
        for form, fields in schema.variants.items():
            yield from records(fields, sample(fields), path, (*variant, (path, form)))
    elif isinstance(schema, list):
        row = value[0] if value else sample(schema[0])
        for label, fields, nested, replace in records(schema[0], row, (*path, 0), variant):
            yield label, fields, nested, lambda item, replace=replace: [replace(item), *value[1:]]
    elif isinstance(schema, wire.RecordFields):
        yield (path, variant), schema, value, lambda row: row
        for key, child in schema.items():
            current = value[key] if key in value else sample(child)
            for label, fields, nested, replace in records(child, current, (*path, key), variant):
                yield label, fields, nested, lambda row, key=key, replace=replace: {**value, key: replace(row)}


class NativeGateMatrix:
    """Reuse the synthetic stage commitment while rebinding each changed leaf.

    The full staged-fixture tests cover the registration, Git ancestry and
    launcher bootstrap. Here the published Check and freeze are provided by
    a synthetic authority snapshot. Layout is verified once and held open.
    Each updated pin is verified before its bytes reach the role validator,
    which runs at each normal entry point. Freshness is checked on disk.
    """

    def __init__(self, world, bench):
        self.repo = bench / "checkout"
        self.private = bench / "private" / registrar.LOOK
        self.public = bench / "public" / registrar.LOOK
        self.source = world / "spans"
        self.pins = registrar.read(self.private / "input-pins.json")
        self.binding = registrar.read(self.private / "bindings.v1.json")
        self.document = registrar.read(self.repo / registrar.book.MANIFEST)
        self.git_book = worker.Book(self.repo)
        self.authority = worker.Authority(self.git_book)
        # Build the real preflight freeze once with the valid synthetic stage.
        snapshot = (self.private / "stage1.committed.json").read_bytes()
        self.instrument = bench / "instrument" / registrar.INST
        self.frozen = worker._operands(self.authority, self.binding, self.private, self.instrument, snapshot)
        self.stage = worker._stage_files(self.private, self.frozen[1], self.frozen[0], self.source)
        revision = self.authority.revision
        self.checks_revision = self.binding["checks_commit"]
        original_blob = self.git_book.blob

        def blob(commit, name):
            if (commit, name) == (self.checks_revision, "RUN_STATE.md"):
                return self.checks
            return original_blob(commit, name)

        self.git_book.blob = blob
        self.git_book.git = cache(self.git_book.git)
        self.git_book.recheck = lambda: None
        self.authority = SimpleNamespace(
            book=self.git_book, revision=revision, document=self.document,
            history=self.authority.history, verify_authorized_prerequisites=lambda *_: None,
            stage_entry=self.authority.stage_entry,
        )

    @contextmanager
    def member(self, span, path, role, runtime=None, *, linked=None):
        self.span, self.path, self.role = span, path, role
        self.runtime = runtime
        self.linked = linked or {}
        self.originals = {}
        try:
            yield
        finally:
            self._rebind(self.originals)

    def _rebind(self, updated):
        for path, raw in updated.items():
            self.originals.setdefault(path, path.read_bytes())
            path.write_bytes(raw)
        target = next(row for row in self.pins["spans"] if row["span_id"] == self.span.name)
        relative = {path.relative_to(self.span).as_posix(): raw for path, raw in updated.items()}
        for entry in target["files"]:
            raw = relative.get(entry["path"])
            if raw is not None:
                entry.update(size=len(raw), sha256=registrar.digest(raw))
        target["offload_manifest_sha256"] = registrar.digest(offload_manifest_bytes(target))
        raw = registrar.manifest.canonical(self.pins)
        registrar.put(self.private / "input-pins.json", raw, mode=0o600)
        self.binding["input_pins_sha256"] = registrar.digest(raw)
        raw = registrar.manifest.canonical(self.binding)
        registrar.put(self.private / "bindings.v1.json", raw, mode=0o600)
        self.document["execution"]["bindings_sha256"] = registrar.digest(raw)
        self.checks = "".join(
            f"{row['close_item']}. **Synthetic close {row['span_id']}**\n"
            f"{row['check_item']}. **Synthetic Check {row['span_id']} {row['offload_manifest_sha256']}**\n"
            for row in self.pins["spans"]
        ).encode()

    def _baseline(self, path):
        return registrar.read(path) if path not in self.originals else json.loads(self.originals[path])

    def bind(self, payload):
        encode = registrar.manifest.canonical
        updated = {**self.linked, self.path: payload}
        digest = registrar.digest(payload)
        if self.role == "stream":
            receipt_path = self.span / "runner_receipt.json"
            receipt = self._baseline(receipt_path)
            stream = next(row for row in receipt["feeds"]["meter"]["files"]
                          if row["path"] == self.path.relative_to(self.span).as_posix())
            stream["sha256"] = digest
            updated[receipt_path] = encode(receipt)
        if self.role == "script":
            result_path = self.runtime / "runtime_result.json"
            copy_path = self.runtime.parent / "leg_record.json"
            result, copy = self._baseline(result_path), self._baseline(copy_path)
            result["script_record_sha256"] = copy["result"]["script_record_sha256"] = digest
            updated[result_path], updated[copy_path] = encode(result), encode(copy)
        if self.role == "config":
            metadata_path = self.path.parent / "metadata.json"
            metadata = self._baseline(metadata_path)
            metadata["config_sha256"] = digest
            updated[metadata_path] = encode(metadata)
        if self.runtime is not None:
            terminal_path = self.runtime / "runtime_custody.json"
            terminal = self._baseline(terminal_path)
            for path, raw in updated.items():
                if path.is_relative_to(self.runtime):
                    member = path.relative_to(self.runtime).as_posix()
                    terminal["files"][member] = registrar.digest(raw)
            updated[terminal_path] = encode(terminal)
        self._rebind(updated)

    @contextmanager
    def entrypoints(self, *, synthetic):
        original_make_inputs = inputs.make_inputs
        original_projection = inputs.binding_projection
        original_layout = worker._layout
        original_project_json = wire.project_json
        inputs_read = inputs._read
        inputs_rail_timing = inputs.rail_timing
        inputs_select_dc = inputs.select_dc
        inputs_terminal = inputs._terminal
        stable_rails, stable_dc = {}, {}
        self.accepted_payload = None

        @lru_cache(maxsize=128)
        def verified_bytes(path, sha256, size):
            return inputs_read(path, {"sha256": sha256, "size": size})

        def make_inputs(*args):
            try:
                return original_make_inputs(*args, synthetic=True)
            except worker.GateRefusal as error:
                self.cause = error.__cause__
                raise

        def projection(episode, config, metadata, **fields):
            # Only the subject metadata varies by producer profile. The
            # other source records retain the pinned synthetic format.
            if self.role == "metadata" and metadata == self.path.read_bytes():
                fields["synthetic"] = synthetic
            return original_projection(episode, config, metadata, **fields)

        def read(path, entry):
            raw = verified_bytes(path, entry["sha256"], entry["size"])
            if path == self.path:
                self.reached = True
            return raw

        def rail_timing(payload, timing, period, evidence):
            if self.reached:
                return inputs_rail_timing(payload, timing, period, evidence)
            if timing.episode_id not in stable_rails:
                stable_rails[timing.episode_id] = inputs_rail_timing(payload, timing, period, evidence)
            return stable_rails[timing.episode_id]

        def select_dc(timing, streams):
            if self.reached:
                return inputs_select_dc(timing, streams)
            if timing.episode_id not in stable_dc:
                stable_dc[timing.episode_id] = inputs_select_dc(timing, streams)
            return stable_dc[timing.episode_id]

        def terminal(root, check, close_leg, kit_leg, ordinal, *, synthetic):
            if self.linked and root == self.span and kit_leg["leg_id"] == self.runtime.parent.name:
                synthetic = False
            return inputs_terminal(root, check, close_leg, kit_leg, ordinal, synthetic=synthetic)

        def project_json(raw, schema, **flags):
            projected = original_project_json(raw, schema, **flags)
            if self.accepted_payload is not None and self.reached:
                original = raw.encode() if isinstance(raw, str) else raw
                if original.rstrip() == self.accepted_payload:
                    raise ShapeAccepted
            return projected

        def operands(*args):
            return self.frozen if args[-1] is not None else ({}, SimpleNamespace(stage1_entry=None))

        def private(path, expected=None, *, token="INPUT_BINDING"):
            raw = path.read_bytes()
            worker._require(expected is None or registrar.digest(raw) == expected, token)
            return raw

        with (
            original_layout(self.git_book, self.document["release_layout"],
                            (self.source, self.instrument), lock=True) as directories,
            patch.object(worker, "Book", return_value=self.git_book),
            patch.object(worker, "Authority", return_value=self.authority),
            patch.object(worker, "_operands", side_effect=operands),
            patch.object(worker, "_stage_files", return_value=self.stage),
            patch.object(worker, "_layout", new=lambda *_args, **_kwargs: nullcontext(directories)),
            patch.object(worker, "_private", new=private),
            patch.object(worker, "load_pin_list", lru_cache(maxsize=8)(worker.load_pin_list)),
            patch.object(inputs, "make_inputs", new=make_inputs),
            patch.object(inputs, "binding_projection", new=projection),
            patch.object(inputs, "_read", new=read),
            patch.object(inputs, "blind_stream", lru_cache(maxsize=8)(inputs.blind_stream)),
            patch.object(inputs, "project_json", new=project_json),
            patch.object(reader, "project_json", new=project_json),
            patch.object(wire, "project_json", new=project_json),
            patch.object(inputs, "rail_timing", new=rail_timing),
            patch.object(inputs, "select_dc", new=select_dc),
            patch.object(inputs, "_terminal", new=terminal),
            patch.object(release, "run_controls_worker") as claim,
        ):
            self.claim = claim
            yield

    def run(self, operation):
        self.cause = None
        self.reached = False
        with patch.object(worker.os, "write") as write:
            exit_code = worker.main([operation], self.repo)
        stderr = b"".join(call.args[1] for call in write.call_args_list if call.args[0] == 2)
        stdout = b"".join(call.args[1] for call in write.call_args_list if call.args[0] == 1)
        return exit_code, stdout, stderr

    def probe_accepted_shape(self, operation, payload):
        self.reached = False
        self.accepted_payload = payload.rstrip()
        if self.role == "stream":
            inputs.blind_stream.cache_clear()
        try:
            worker.run(operation, self.repo)
        finally:
            self.accepted_payload = None
