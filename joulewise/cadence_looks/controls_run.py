"""Fixed host ctl-01 launcher operations."""

from contextlib import ExitStack, contextmanager
from hashlib import sha256
import os
from pathlib import Path
import socket
import subprocess
import sys

from .controls_book import Authority, Book
from .controls_layout import (
    DIR_FLAGS, GateRefusal, absolute, held_lock, open_directory, open_file, probe_link,
    registered_directories, require_fresh, require_private, require_unspent_history,
)
from .controls_manifest import verify_freeze, verify_stage1
from .controls_print import LOOK_ID, ControlsRefusal, Refusal, _hex_pin
from .custody_pins import check_chain_problems, load_pin_list, run_state_item
from .qualification_manifest import _decode


OPERATIONS = ("validate-final", "stage1", "preflight", "stage2", "status")


def _require(condition, token="FREEZE"):
    if not condition:
        raise GateRefusal(token)


def _private(path, expected=None, *, token="INPUT_BINDING"):
    try:
        with open_file(path) as stream:
            require_private(stream.fileno(), directory=False)
            raw = stream.read()
        _require(expected is None or sha256(raw).hexdigest() == expected, token)
        return raw
    except (OSError, ValueError) as error:
        raise GateRefusal(token) from error


def _binding(authorization, private):
    execution = authorization.document["execution"]
    _require(execution["host"] == socket.gethostname() and execution["uid"] == os.geteuid(), "LAYOUT")
    raw = _private(private / "bindings.v1.json", execution["bindings_sha256"], token="FREEZE")
    binding = _decode(raw)
    _require(binding.keys() == {"schema", "source_root", "instrument_root",
                               "runner_commit", "kit_sha256", "input_pins_sha256", "checks_commit",
                               "observations_sha256", "gates"}
             and binding["schema"] == "joulewise.cadence_ctl_bindings.v1"
             and all(_hex_pin(binding[key], 40) for key in ("runner_commit", "checks_commit"))
             and all(_hex_pin(binding[key], 64) for key in (
                 "kit_sha256", "input_pins_sha256", "observations_sha256")))
    # The source locators never appear in the public registration.
    source = absolute(binding["source_root"])
    instrument = absolute(binding["instrument_root"])
    _require(instrument.name == "lm-inst-01", "LAYOUT")
    _require(not source.is_relative_to(instrument) and not instrument.is_relative_to(source)
             and not source.is_relative_to(private) and not private.is_relative_to(source)
             and not instrument.is_relative_to(private) and not private.is_relative_to(instrument), "LAYOUT")
    return binding, source, instrument


def _check_inputs(authorization, binding, private, source):
    from .controls_inputs import make_inputs

    check_revision = binding["checks_commit"]
    book = authorization.book
    _require(check_revision in book.git("rev-list", "--first-parent", authorization.revision).decode().splitlines())
    pins_raw = _private(private / "input-pins.json", binding["input_pins_sha256"])
    pins = load_pin_list(pins_raw)
    checks = book.blob(check_revision, "RUN_STATE.md").decode("utf-8")
    _require(not check_chain_problems(pins, checks))
    for span in pins["spans"]:
        close = run_state_item(checks, span["close_item"])
        check = run_state_item(checks, span["check_item"])
        _require(close is not None and check is not None and span["span_id"] in close and span["span_id"] in check)
    kit_raw = _private(private / "issued-kit.json", binding["kit_sha256"])
    inputs = make_inputs(source, private, kit_raw, pins["spans"], binding["runner_commit"])
    authorization.verify_authorized_prerequisites(binding, inputs)
    return inputs


def _disposition(authorization, private):
    rows = [row for row in authorization.history
            if row["look_id"] == LOOK_ID and row["kind"] == "dc_disposition"]
    stage = authorization.stage_entry()
    if not rows:
        _require(not os.path.lexists(private / "disposition.json"), "INPUT_CHANNELS")
        return None
    _require(len(rows) == 1 and (stage is None or authorization.history.index(rows[0])
                                < authorization.history.index(stage)), "INPUT_CHANNELS")
    return _private(private / "disposition.json", rows[0]["sha256"], token="INPUT_CHANNELS")


def _operands(authorization, binding, private, instrument, stage_snapshot):
    from .controls_analysis import withheld_reason

    pins = authorization.document["pins"]
    operands = {role: _private(instrument / (role + ".json"), pins[role],
                               token="INSTRUMENT_HOLD_BINDING" if role == "hold" else "FREEZE")
                for role in ("hold", "edges")}
    freeze_inputs = authorization.freeze_inputs(private=operands, stage1_snapshot=stage_snapshot)
    freeze = verify_freeze(**freeze_inputs)
    observations = _decode(_private(private / "instrument-observations.json",
                                    binding["observations_sha256"], token="FREEZE"))
    _require(observations.keys() == {"gpu_token_floors", "dc_token_floors", "qualified_prefills"}
             and withheld_reason(observations["gpu_token_floors"], observations["dc_token_floors"],
                                 observations["qualified_prefills"]) is None)
    edges = _decode(operands["edges"])
    _require(type(edges) is dict and edges.keys() == _decode(operands["hold"]).keys()
             and all(type(value) is dict for value in edges.values()), "INSTRUMENT_HOLD_BINDING")
    return freeze_inputs, freeze


def _stat_registered_entries(source, inventory):
    """Check for missing expected roles before testing mismatched hashes."""
    from .custody_pins import safe_relative

    def check(span, entry):
        path = entry["path"]
        _require(safe_relative(span) and "/" not in span and safe_relative(path))
        try:
            with open_file(source / span / path):
                pass
        except FileNotFoundError as error:
            raise GateRefusal("INPUT_CHANNELS") from error
        except (OSError, ValueError) as error:
            raise GateRefusal("INPUT_BINDING") from error

    for span, fields in inventory["spans"].items():
        for entry in fields["streams"]:
            check(span, entry)
    for row in inventory["positions"].values():
        for entry in row["files"].values():
            check(row["span_id"], entry)


def _schema(raw, schema):
    from .controls_release import validate_shape

    document = _decode(schema)
    validate_shape(_decode(raw), document, document["$defs"])


def _stage_files(private, freeze, freeze_inputs, source):
    from .controls_inputs import load_canonical

    stage_raw = _private(private / "stage1.json")
    try:
        stage = verify_stage1(freeze, freeze_inputs["committed"], stage_raw)
    except (ValueError, TypeError, KeyError) as error:
        raise GateRefusal("INPUT_BINDING") from error
    _require(stage.inventory_sha256 is not None, "INPUT_BINDING")
    inputs_raw = _private(private / "inputs.v1.json", stage.inventory_sha256)
    document = load_canonical(inputs_raw)
    snapshot = freeze_inputs["committed"][freeze.revision]
    _schema(stage_raw, snapshot["stage1_schema"])
    _schema(inputs_raw, snapshot["inventory_schema"])
    _stat_registered_entries(source, document)
    return stage_raw, stage, inputs_raw


def _certificates(private_fd, inputs, *, create=False):
    from .controls_inputs import write_or_compare

    if create:
        try:
            os.mkdir("certificates", mode=0o700, dir_fd=private_fd)
            os.fsync(private_fd)
        except FileExistsError:
            pass
    fd = os.open("certificates", DIR_FLAGS, dir_fd=private_fd)
    try:
        require_private(fd, directory=True)
        _require(set(os.listdir(fd)) <= {leg + ".json" for leg in inputs.certificates}, "INPUT_BINDING")
        for leg, raw in inputs.certificates.items():
            if create:
                write_or_compare(fd, leg + ".json", raw)
            else:
                _private(inputs.private / "certificates" / (leg + ".json"),
                         sha256(raw).hexdigest())
    finally:
        os.close(fd)


def _build_stage(private_fd, inputs, freeze_inputs):
    from .controls_inputs import write_or_compare

    freeze = freeze_inputs["committed"][freeze_inputs["current_revision"]]
    stage_raw, inputs_raw = inputs.stage1_bytes()
    _schema(stage_raw, freeze["stage1_schema"])
    _schema(inputs_raw, freeze["inventory_schema"])
    write_or_compare(private_fd, "inputs.v1.json", inputs_raw)
    write_or_compare(private_fd, "stage1.json", stage_raw)


@contextmanager
def _layout(book, layout, protected=(), *, lock=False):
    with ExitStack() as stack:
        try:
            directories = stack.enter_context(registered_directories(book, layout, protected))
            if lock:
                stack.enter_context(held_lock(directories[0]))
        except (OSError, ValueError) as error:
            raise GateRefusal("LAYOUT") from error
        yield directories


def run(operation, root):
    book = Book(root)
    book.recheck()
    authority = Authority(book)
    require_unspent_history(authority.history)
    layout = authority.document["release_layout"]
    execution = authority.document["execution"]
    private = absolute(layout["private"]["path"])
    # Check durable state before newly failing scientific prerequisites.
    try:
        with _layout(book, layout, lock=True) as directories:
            require_fresh(*directories, authority.history)
            if operation == "status":
                return 0
            binding, source, instrument = _binding(authority, private)
            authority.verify_authorized_prerequisites(binding)
            with _layout(book, layout, (source, instrument)):
                _run_fresh(operation, authority, binding, private, source, instrument, directories, execution)
    except ControlsRefusal as error:
        if error.reason is Refusal.INSTRUMENT_HOLD_BINDING:
            raise GateRefusal("INSTRUMENT_HOLD_BINDING") from error
        raise GateRefusal("FREEZE") from error
    return 0


def _run_fresh(operation, authority, binding, private, source, instrument, directories, execution):
    from .controls_inputs import apply_disposition
    from .controls_release import run_controls_worker

    private_fd, public_fd = directories
    stage_snapshot = None
    if operation in ("preflight", "stage2"):
        stage_snapshot = _private(private / "stage1.committed.json")
    freeze_inputs, freeze = _operands(authority, binding, private, instrument, stage_snapshot)
    if operation == "stage1":
        _require(freeze.stage1_entry is None)
    if stage_snapshot is not None:
        stage_raw, stage, inputs_raw = _stage_files(private, freeze, freeze_inputs, source)
    inputs = _check_inputs(authority, binding, private, source)
    if operation == "stage1":
        _certificates(private_fd, inputs, create=True)
    # An eligible exception is represented only by an independently committed
    # disposition tied to the exact bytes of the freshly derived certificate.
    apply_disposition(inputs, _disposition(authority, private))
    if stage_snapshot is not None:
        _certificates(private_fd, inputs)
        _require(inputs.stage1_bytes() == (stage_raw, inputs_raw), "INPUT_BINDING")
        inputs.verify_stage1(stage)
    probe_link(private_fd, public_fd)
    authority.book.recheck()
    require_fresh(*directories, authority.history)
    if operation == "stage1":
        _build_stage(private_fd, inputs, freeze_inputs)
    elif operation == "stage2":
        run_controls_worker(freeze_inputs=freeze_inputs, stage1_bytes=stage_raw, blind=stage.public,
                            execution_host=execution["host"], local_host=socket.gethostname(),
                            native_inputs=inputs, directories=directories)


def main(argv, root):
    try:
        if len(argv) != 1 or argv[0] not in OPERATIONS:
            raise GateRefusal("FREEZE")
        return run(argv[0], root)
    except GateRefusal as error:
        os.write(2, error.notice.encode("ascii"))
        return error.status
    except (KeyError, ValueError, TypeError, OSError, subprocess.SubprocessError):
        os.write(2, b"REFUSE PREFLIGHT FREEZE\n")
        return 2
