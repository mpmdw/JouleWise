"""Single-use controls output boundary with a blind public projection."""

from contextlib import suppress
from hashlib import sha256
import math
import os
from pathlib import Path
import re
import sys
import traceback

from . import controls_analysis as analysis
from .controls_manifest import canonical, verify_freeze
from .controls_print import LOOK_ID, encode_public_projection
from .qualification_manifest import _decode


PUBLIC_NAME = "PUBLIC.json"
PRIVATE_NAMES = frozenset({"controls.json", "stdout", "stderr"})


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


def prepare_public(blind, schema_bytes):
    schema = _decode(schema_bytes)
    validate_shape(blind, schema, schema.get("$defs", {}))
    return encode_public_projection(blind, blind)


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


def calculate_private(positions, *, kernel, pooled, gap_limits_ns, instrument_manifest_sha256, schema_bytes,
                      instrument_reasons=()):
    report = analysis.print_controls(positions, kernel=kernel, pooled=pooled, gap_limits_ns=gap_limits_ns,
                                     instrument_manifest_sha256=instrument_manifest_sha256)
    return prepare_private(report, schema_bytes, instrument_reasons=instrument_reasons)


def publish_reserved(restricted, public, public_bytes, positions, **calculation):
    """Calculate and serialize within a reservation, then perform the write."""
    private_bytes = calculate_private(positions, **calculation)
    sys.stdout.flush()
    sys.stderr.flush()
    write_outputs(restricted, public, private_bytes, public_bytes)


def run_controls_worker(*, freeze_inputs, stage1_bytes, blind, execution_host, local_host, restricted: Path,
                        public: Path, first_read, kernel, pooled, gap_limits_ns):
    """Run in a dedicated process after the lead binds the host and roots."""
    from .manifest_dispatch import PRE_READ_REFUSAL
    from .transfer_release import POST_READ_FAILURE, _failure_type, _redirect, _sync_directory

    saved_stderr = None
    confined = False
    read_started = False
    try:
        freeze = verify_freeze(**freeze_inputs)
        stage1 = _decode(stage1_bytes)
        if (not execution_host or execution_host != local_host
                or freeze.manifest_sha256 != blind["manifest_sha256"] or freeze.revision != blind["commit"]
                or sha256(stage1_bytes).hexdigest() != blind["stage1_sha256"]
                or type(stage1) is not dict or type(stage1.get("n_legs")) is not int
                or stage1["n_legs"] != blind["n_legs"]
                or type(pooled) is not analysis.HoldPool or pooled.reason_enum != freeze.instrument_reasons):
            raise ValueError("controls_blind_gate")
        public_bytes = prepare_public(blind, freeze.output_schema)
        sys.stdout.flush()
        sys.stderr.flush()
        saved_stderr = os.dup(2)
        reserve_outputs(restricted, public)
        _redirect(restricted)
        confined = True
        _sync_directory(restricted.parent)
        read_started = True
        positions = first_read()
        publish_reserved(restricted, public, public_bytes, positions, kernel=kernel, pooled=pooled,
                         gap_limits_ns=gap_limits_ns, instrument_manifest_sha256=freeze.instrument_manifest_sha256,
                         schema_bytes=freeze.restricted_schema, instrument_reasons=freeze.instrument_reasons)
    except BaseException as error:
        if confined:
            with suppress(BaseException):
                traceback.print_exception(error)
        notice = f"stage2_error\n{_failure_type(error)}\n" if read_started else "REFUSE controls look before read\n"
        with suppress(BaseException):
            os.write(saved_stderr if saved_stderr is not None else 2, notice.encode("ascii"))
        os._exit(POST_READ_FAILURE if read_started else PRE_READ_REFUSAL)
    os._exit(0)
