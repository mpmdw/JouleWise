"""Single-use controls output boundary with a blind public projection."""

from contextlib import suppress
from dataclasses import dataclass, replace
from hashlib import sha256
from importlib.util import find_spec
import math
import os
from pathlib import Path
import re
import sys
import traceback

from . import controls_analysis as analysis
from .controls_manifest import CODE_PATHS, canonical, verify_freeze, verify_stage1
from .controls_print import LOOK_ID, LegBinding, encode_public_projection
from .qualification_manifest import _decode


PUBLIC_NAME = "PUBLIC.json"
PRIVATE_NAMES = frozenset({"controls.json", "stdout", "stderr"})
_PHASE_SOURCES = (
    "print_code/phase", "print_code/attribution", "print_code/records", "print_code/windows",
    "print_code/powermetrics_adapter", "print_code/trace_point", "print_code/integrator",
)


def validate_shape(value, schema, definitions, *, instrument_reasons=()):
    """Check the closed schema vocabulary used by the controls artifacts."""
    if schema is False:
        raise ValueError("controls_output_schema")
    if "$ref" in schema:
        reference = schema["$ref"].removeprefix("#/$defs/")
        if reference == "instrumentReason":
            if type(value) is str and value in instrument_reasons:
                return
            raise ValueError("controls_output_schema")
        return validate_shape(value, definitions[reference], definitions, instrument_reasons=instrument_reasons)
    if "anyOf" in schema:
        for branch in schema["anyOf"]:
            try:
                validate_shape(value, branch, definitions, instrument_reasons=instrument_reasons)
            except ValueError:
                continue
            return
        raise ValueError("controls_output_schema")
    kind = schema["type"]
    types = {"object": (dict,), "array": (list, tuple), "number": (int, float), "integer": (int,),
             "boolean": (bool,), "string": (str,), "null": (type(None),)}
    if type(value) not in types[kind]:
        raise ValueError("controls_output_schema")
    if "const" in schema and value != schema["const"] or "enum" in schema and value not in schema["enum"]:
        raise ValueError("controls_output_schema")
    if kind == "object":
        fields = schema["properties"]
        if value.keys() - fields.keys() or set(schema["required"]) - value.keys():
            raise ValueError("controls_output_schema")
        for name, item in value.items():
            validate_shape(item, fields[name], definitions, instrument_reasons=instrument_reasons)
    elif kind == "array":
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", len(value)):
            raise ValueError("controls_output_schema")
        for item in value:
            validate_shape(item, schema["items"], definitions, instrument_reasons=instrument_reasons)
    elif kind in ("number", "integer"):
        if not math.isfinite(value) or "minimum" in schema and value < schema["minimum"]:
            raise ValueError("controls_output_schema")
    elif kind == "string" and "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
        raise ValueError("controls_output_schema")


def prepare_public(blind, schema_bytes, *, committed=None):
    schema = _decode(schema_bytes)
    validate_shape(blind, schema, schema.get("$defs", {}))
    return encode_public_projection(blind, blind if committed is None else committed)


def prepare_private(scientific, schema_bytes, *, instrument_reasons=()):
    schema = _decode(schema_bytes)
    validate_shape(scientific, schema, schema["$defs"], instrument_reasons=instrument_reasons)
    return canonical(scientific)


def _write(path, data, mode):
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def reserve_outputs(restricted, public):
    if (restricted.name != "RESTRICTED" or public.name != PUBLIC_NAME
            or restricted.parent.name != LOOK_ID or public.parent.name != LOOK_ID
            or restricted.parent.resolve() == public.parent.resolve()
            or not restricted.parent.is_dir() or not public.parent.is_dir()
            or restricted.parent.is_symlink() or public.parent.is_symlink()):
        raise ValueError("controls_destination")
    reserve_directory(restricted, public)


def reserve_directory(directory, public):
    """Reserve a directory for the writer after the caller binds its paths."""
    if os.path.lexists(public):
        raise ValueError("controls_destination")
    # The directory creation selects the sole winner even if two workers
    # completed the prior blind checks concurrently.
    directory.mkdir(mode=0o700)


def write_outputs(restricted, public, private_bytes, public_bytes):
    """Write confined scientific bytes, then publish the prebound blind bytes."""
    _write(restricted / "controls.json", private_bytes, 0o600)
    if {path.name for path in restricted.iterdir()} != PRIVATE_NAMES:
        raise ValueError("controls_inventory")
    pending = restricted / ".publication"
    _write(pending, public_bytes, 0o644)
    try:
        # The temporary file stays in the reservation. An existing public file
        # wins rather than being replaced by a competing writer.
        os.link(pending, public, follow_symlinks=False)
    finally:
        pending.unlink()


def calculate_private(positions, *, kernel, pooled, instrument_manifest_sha256, schema_bytes,
                      instrument_reasons=(), gap_limits_ns=None):
    report = analysis.print_controls(positions, kernel=kernel, pooled=pooled, gap_limits_ns=gap_limits_ns,
                                     instrument_manifest_sha256=instrument_manifest_sha256)
    return prepare_private(report, schema_bytes, instrument_reasons=instrument_reasons)


def publish_reserved(restricted, public, public_bytes, positions, **calculation):
    """Calculate and serialize within a reservation, then perform the write."""
    private_bytes = calculate_private(positions, **calculation)
    sys.stdout.flush()
    sys.stderr.flush()
    write_outputs(restricted, public, private_bytes, public_bytes)


def _verified_kernel(pins):
    """Bind the worker's fixed numerical imports to the registered source bytes."""
    for role in _PHASE_SOURCES:
        module = CODE_PATHS[role].removesuffix(".py").replace("/", ".")
        spec = find_spec(module)
        if spec is None or spec.origin is None:
            raise ValueError("controls_kernel_source")
        origin = Path(spec.origin)
        if origin.suffix != ".py" or sha256(origin.read_bytes()).hexdigest() != pins[role]:
            raise ValueError("controls_kernel_source")
    return analysis.PhaseKernel.frozen()


@dataclass(frozen=True)
class LegRead:
    """Exact member bytes and the reader's claimed committed identity."""

    binding: LegBinding
    kind: str
    admitted: bool
    g0_released: bool
    episode_bytes: bytes | None
    work_bytes: bytes | None


def _verify_member_bytes(payload, expected_digest):
    if expected_digest is None:
        valid = payload is None
    else:
        valid = type(payload) is bytes and sha256(payload).hexdigest() == expected_digest
    if not valid:
        raise ValueError("controls_member_digest")


def _bound_positions(expected, received):
    from joulewise.align.records import Episode, from_json

    positions = []
    for committed, read in zip(expected, received, strict=True):
        if (type(read) is not LegRead or type(read.binding) is not LegBinding
                or type(read.binding.span) is not int or type(read.binding.attempt) is not int
                or read.binding != committed.binding or type(read.kind) is not str or read.kind != committed.kind
                or read.admitted is not committed.admitted or read.g0_released is not committed.g0_released):
            raise ValueError("controls_member_binding")

        _verify_member_bytes(read.episode_bytes, committed.episode_sha256)
        _verify_member_bytes(read.work_bytes, committed.script_sha256)
        episode = None
        if read.episode_bytes is not None:
            episode = from_json(Episode, read.episode_bytes)
            if episode.episode_id != committed.episode_id:
                raise ValueError("controls_episode_identity")
            for trace in episode.power_traces:
                if trace.source == "powermetrics":
                    analysis.registered_u1_ns(trace, trace.channel)

        positions.append(analysis.LegInput(committed.binding.leg_id, committed.kind, committed.admitted,
                                           committed.g0_released, episode, read.work_bytes, committed.script_sha256))
    return tuple(positions)


def run_controls_worker(*, freeze_inputs, stage1_bytes, blind, execution_host, local_host, restricted: Path,
                        public: Path, first_read):
    """Run once, with the first reader given the committed stage-1 bindings."""
    from .manifest_dispatch import PRE_READ_REFUSAL
    from .transfer_release import POST_READ_FAILURE, _failure_type, _redirect, _sync_directory

    saved_stderr = None
    confined = False
    read_started = False
    try:
        freeze = verify_freeze(**freeze_inputs)
        stage1 = verify_stage1(freeze, freeze_inputs["committed"], stage1_bytes)
        if not execution_host or execution_host != local_host:
            raise ValueError("controls_blind_gate")
        public_bytes = prepare_public(blind, freeze.output_schema, committed=stage1.public)
        kernel = _verified_kernel(freeze.pins)
        sys.stdout.flush()
        sys.stderr.flush()
        saved_stderr = os.dup(2)
        reserve_outputs(restricted, public)
        _redirect(restricted)
        confined = True
        _sync_directory(restricted.parent)
        read_started = True
        requests = tuple(replace(leg, binding=replace(leg.binding)) for leg in stage1.legs)
        positions = _bound_positions(stage1.legs, first_read(requests))
        publish_reserved(restricted, public, public_bytes, positions, kernel=kernel, pooled=freeze.instrument_pool,
                         instrument_manifest_sha256=freeze.instrument_manifest_sha256,
                         schema_bytes=freeze.restricted_schema, instrument_reasons=freeze.instrument_pool.reason_enum)
    except BaseException as error:
        if confined:
            with suppress(BaseException):
                traceback.print_exception(error)
        notice = f"stage2_error\n{_failure_type(error)}\n" if read_started else "REFUSE controls look before read\n"
        with suppress(BaseException):
            os.write(saved_stderr if saved_stderr is not None else 2, notice.encode("ascii"))
        os._exit(POST_READ_FAILURE if read_started else PRE_READ_REFUSAL)
    os._exit(0)
