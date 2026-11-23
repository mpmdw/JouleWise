#!/usr/bin/env python3.13
"""Synthetic-only registrar and observer for the frozen ctl bundle driver."""

from dataclasses import replace
from contextlib import contextmanager
from hashlib import sha256
from importlib import import_module, util
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from traceback import print_exc


ROOT = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

from joulewise.cadence_looks import controls_book as book, controls_manifest as manifest
from joulewise.cadence_looks import controls_layout
from joulewise.cadence_looks.custody_pins import SCHEMA as PINS_SCHEMA, span_pins


LOOK = "lm-ctl-01"
INST = "lm-inst-01"
RUNNER = "043b972f999913d248769237f1901d78119ceb72"


def read(path):
    return json.loads(path.read_bytes())


def digest(raw):
    return sha256(raw).hexdigest()


def put(path, data, mode=0o644):
    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_bytes(data if isinstance(data, bytes) else manifest.canonical(data))
    path.chmod(mode)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE).decode().strip()


def commit(root, title):
    git(root, "add", "--all")
    git(root, "-c", "user.email=ctl-fixture@example.invalid", "-c", "user.name=ctl synthetic registrar", "commit",
        "--quiet", "-m", title, "-m", "Co-Authored-By: Sol 6.2 <noreply@openai.com>")
    revision = git(root, "rev-parse", "HEAD")
    git(root, "update-ref", book.REF, revision)
    return revision


def add_event(root, kind, *, look=LOOK, **values):
    path = root / book.LOOKS
    ledger = read(path)
    ledger["events"].append(dict(kind=kind, look_id=look, **values))
    put(path, ledger)
    return commit(root, "Synthetic " + kind)


def pin_layout(path):
    info = path.stat()
    return dict(path=str(path), device=info.st_dev, inode=info.st_ino)


def _source_paths():
    for path in manifest.CODE_PATHS.values():
        if path.startswith("joulewise/") and path.endswith(".py"):
            import_module(path.removesuffix(".py").replace("/", "."))
    return {Path(origin).relative_to(ROOT).as_posix()
            for module in tuple(sys.modules.values())
            if (origin := getattr(module, "__file__", None)) is not None
            and Path(origin).is_relative_to(ROOT/"joulewise")}


def install(world, bench, fault, legacy):
    from tests.git_fixture import init_git_fixture

    repo = bench / "checkout"
    repo.mkdir()
    init_git_fixture(repo, "--quiet")
    git(repo, "remote", "add", "origin", book.ORIGIN)
    for path in set(manifest.CODE_PATHS.values()) | _source_paths():
        put(repo/path, (ROOT/path).read_bytes())
    for name in book.SUITE_NAMES:
        put(repo/book.SUITE/name, (ROOT/book.SUITE/name).read_bytes())

    private = bench/"private"/LOOK
    public = bench/"public"/LOOK
    instrument = bench/"instrument"/INST
    if fault == "other_worktree_parent":
        put(repo/"fixture.txt", b"synthetic\n")
        commit(repo, "Synthetic initial tree")
        git(repo, "worktree", "add", "--detach", "--no-checkout", str(bench/"second"))
        private = bench/"second"/LOOK
        private.mkdir(mode=0o700)
    instrument.mkdir(mode=0o700, parents=True)
    put(private/controls_layout.CONTROL_NAME, b"", mode=0o600)
    source = world/"spans"
    source.chmod(0o700)
    for role in ("hold", "edges"):
        put(instrument/(role+".json"), (world/"instrument"/(role+".json")).read_bytes(), mode=0o600)
    if fault == "tracked_hold_blob":
        put(repo/"synthetic-misplaced-input.json", (instrument/"hold.json").read_bytes())

    floor_path = manifest.LOOK_DIR + "lm-inst-01.restricted.schema.json"
    schema = read(ROOT/"tests/contracts/cadence_looks/fixtures/lm-inst-01.restricted.schema.draft.json")
    if legacy:
        vocab = read(ROOT/manifest.CODE_PATHS["hold_reasons"])
        schema["$defs"]["undefined"]["properties"]["reason"]["enum"] = (
            vocab["leaf_reasons"] + vocab["whole_member_reasons"])
    put(repo/floor_path, schema)
    floor_sha = digest((repo/floor_path).read_bytes())
    instrument_manifest_path = manifest.LOOK_DIR + "lm-inst-01.json"
    inst_manifest = dict(schema="joulewise.cadence_look_manifest.v2", look_kind="description",
                         look_id=INST, status="committed", kits=[dict(kit_id="f2-inst-01", sha256="a"*64)],
                         code_pins={"restricted_schema": {"path": floor_path, "sha256": floor_sha}})
    put(repo/instrument_manifest_path, inst_manifest)
    instrument_sha = digest((repo/instrument_manifest_path).read_bytes())
    put(repo/book.LOOKS, dict(schema="joulewise.cadence_look_ledger.v1", events=[],
                             looks=[dict(look_id=INST, manifest_path=instrument_manifest_path,
                                         sha256=instrument_sha, status="registered")]))
    instrument_revision = commit(repo, "Synthetic instrument registration")
    positions = {f"f2-inst-01/L00{index}": {"disposition": "qualified"} for index in (1, 2)}
    put(repo/book.INSTRUMENT_STAGE1, dict(look_id=INST, status="committed", positions=positions, counts={"n_legs": 2}))
    instrument_stage_sha = digest((repo/book.INSTRUMENT_STAGE1).read_bytes())
    instrument_stage = add_event(repo, "stage1", look=INST, stage1_sha256=instrument_stage_sha,
                                 n_legs=2, manifest_sha256=instrument_sha)

    fixture_authority = read(world/"authority/check.json")
    pin_rows = []
    check_lines = []
    for index, (span_id, committed) in enumerate(sorted(fixture_authority.items()), 1):
        span = source/span_id
        inventory = {}
        for path in sorted(span.rglob("*")):
            if path.is_file():
                name = path.relative_to(span).as_posix()
                inventory[name] = (digest(path.read_bytes()), path.stat().st_size)
        if any(inventory[name][0] != expected for name, expected in committed.items()):
            raise ValueError("synthetic close differs from its fixture authority")
        raw = "".join(f"{pin}  ./{name}\n" for name, (pin, _) in inventory.items()).encode()
        pins = span_pins(span_id, raw, {k: n for k, (_, n) in inventory.items()}, runner_commit=RUNNER,
                         close_item=index*2-1, check_item=index*2)
        pin_rows.append(pins)
        check_lines.extend((f"{index*2-1}. **Synthetic close {span_id}**",
                            f"{index*2}. **Synthetic Check {span_id} {pins['offload_manifest_sha256']}**"))
    put(repo/"RUN_STATE.md", "\n\n".join(check_lines).encode() + b"\n")
    checks_revision = commit(repo, "Synthetic independent Check commitments")
    put(private/"input-pins.json", dict(schema=PINS_SCHEMA, spans=pin_rows), mode=0o600)
    put(private/"issued-kit.json", (world/"authority/kit.json").read_bytes(), mode=0o600)
    put(private/"instrument-observations.json", dict(gpu_token_floors=[10], dc_token_floors=[10],
                                                    qualified_prefills=[2000]), mode=0o600)
    gates = {kind: digest(kind.encode()) for kind in book.GATE_KINDS}
    for kind, row in zip(("pilot_close", "remainder_close"), pin_rows, strict=True):
        gates[kind] = fixture_authority[row["span_id"]]["runner_receipt.json"]
    for kind, pin in gates.items():
        add_event(repo, kind, sha256=pin)
    bindings = dict(schema="joulewise.cadence_ctl_bindings.v1", source_root=str(source),
                    instrument_root=str(instrument), runner_commit=RUNNER, checks_commit=checks_revision, gates=gates,
                    kit_sha256=digest((private/"issued-kit.json").read_bytes()),
                    input_pins_sha256=digest((private/"input-pins.json").read_bytes()),
                    observations_sha256=digest((private/"instrument-observations.json").read_bytes()))
    put(private/"bindings.v1.json", bindings, mode=0o600)
    if fault == "kernel_matches_manifest_but_not_byte_pass":
        path = repo/manifest.CODE_PATHS["print_code/attribution"]
        put(path, path.read_bytes() + b"\n")
    source_paths = {p.relative_to(repo).as_posix(): digest(p.read_bytes()) for p in (repo/"joulewise").rglob("*.py")}
    source_paths["scripts/cadence_controls_run.py"] = digest((repo/"scripts/cadence_controls_run.py").read_bytes())
    put(repo/book.SOURCES, dict(schema="joulewise.cadence_ctl_sources.v1", paths=source_paths,
                               python=dict(implementation=sys.implementation.name, version=list(sys.version_info[:3]))))
    execution = dict(host=socket.gethostname(), uid=os.geteuid(),
                     sources_sha256=digest((repo/book.SOURCES).read_bytes()),
                     bindings_sha256=digest((private/"bindings.v1.json").read_bytes()))
    pins = {role: digest((repo/path).read_bytes()) for role, path in manifest.CODE_PATHS.items()}
    pins.update(instrument_manifest=instrument_sha, instrument_floor_schema=floor_sha,
                hold=digest((instrument/"hold.json").read_bytes()), edges=digest((instrument/"edges.json").read_bytes()))
    put(repo/book.MANIFEST, dict(schema=manifest.SCHEMA_ID, status="final", look_id=LOOK, look_kind="controls",
                                kit_id="cl-ctl-01", pins=pins, execution=execution,
                                instrument_output_schema=dict(commit=instrument_revision, path=floor_path, sha256=floor_sha),
                                instrument_stage1=dict(ledger_commit=instrument_stage, stage1_sha256=instrument_stage_sha),
                                release_layout=dict(private=pin_layout(private), public=pin_layout(public))))
    manifest_sha = digest((repo/book.MANIFEST).read_bytes())
    ledger = read(repo/book.LOOKS)
    ledger["looks"].append(dict(look_id=LOOK, manifest_path=book.MANIFEST, sha256=manifest_sha, status="registered"))
    put(repo/book.LOOKS, ledger)
    revision = commit(repo, "Synthetic controls registration")
    add_event(repo, "design_pass")
    prior = git(repo, "rev-parse", "HEAD")
    put(repo/book.BYTE_RECEIPT, dict(schema="joulewise.cadence_ctl_byte_pass.v1",
                                    manifest_sha256=manifest_sha, sources_sha256=execution["sources_sha256"],
                                    kernel_sha256=dict(zip(book.KERNEL_ROLES, book.AUDITED_KERNEL, strict=True)),
                                    suite_sha256={name: digest((repo/book.SUITE/name).read_bytes())
                                                  for name in book.SUITE_NAMES},
                                    v3_1_count=846, installed_bundle_cases=book.INSTALLED_BUNDLE_RESULT,
                                    supersession_sha256=book.SUPERSESSION_SHA256, h_output_bytes_equal=True))
    receipt_sha = digest((repo/book.BYTE_RECEIPT).read_bytes())
    add_event(repo, "byte_pass", manifest_sha256=manifest_sha, receipt_sha256=receipt_sha, hand_vectors_passed=True)
    add_event(repo, "receipt", revision=revision, manifest_sha256=manifest_sha)
    if fault == "sibling_ledger_only":
        git(repo, "branch", "test-untrusted-receipt")
        git(repo, "checkout", "--detach", prior)
        git(repo, "update-ref", book.REF, prior)


def _production_modules(repo):
    # Start a fresh process before this method. The deployed bootstrap supplies
    # verified module bodies. The registrar above runs in a separate process.
    from importlib.machinery import SourceFileLoader

    for name in tuple(sys.modules):
        if name == "joulewise" or name.startswith("joulewise."):
            del sys.modules[name]
    path = repo/"scripts/cadence_controls_run.py"
    loader = SourceFileLoader("synthetic_bootstrap", str(path))
    spec = util.spec_from_loader(loader.name, loader)
    launcher = util.module_from_spec(spec)
    loader.exec_module(launcher)
    launcher._public_tip = lambda: git(repo, "rev-parse", book.REF)
    try:
        inventory = launcher._registration(repo)
    except launcher.Spent:
        os.write(2, b"REFUSE SPENT\n")
        return False
    sys.path.insert(0, str(repo))
    sys.meta_path.insert(0, launcher.RegisteredModules(repo, inventory))
    return True


def run(operation, world, bench, fault):
    repo = bench/"checkout"
    private = bench/"private"/LOOK
    if operation in ("install", "install-v2"):
        install(world, bench, fault, operation == "install")
        return 0
    if operation == "attest-disposition":
        raw = (world/"authority/disposition.json").read_bytes()
        put(private/"disposition.json", raw, mode=0o600)
        add_event(repo, "dc_disposition", issuer="research_lead", sha256=digest(raw))
        return 0
    if operation == "commit-stage1":
        raw = (private/"stage1.json").read_bytes()
        put(private/"stage1.committed.json", raw, mode=0o600)
        manifest_sha = digest((repo/book.MANIFEST).read_bytes())
        count = json.loads(raw)["n_legs"]
        revision = add_event(repo, "stage1", stage1_sha256=digest(raw), n_legs=count, manifest_sha256=manifest_sha)
        put(bench/"registered-public.json", dict(look_id=LOOK, manifest_sha256=manifest_sha, commit=revision,
                                                 stage1_sha256=digest(raw), n_legs=count))
        return 0
    if operation == "clone-fresh":
        from look_path_pair import clone_fresh

        return clone_fresh(world, bench)
    if fault == "observe_zero_h":
        from look_path_pair import run_zero

        return run_zero(str(Path(__file__).resolve()), world, bench)
    if fault == "installed_kernel_drift":
        path = repo/manifest.CODE_PATHS["print_code/attribution"]
        put(path, path.read_bytes() + b"\n")
    if not _production_modules(repo):
        return 3
    from joulewise.cadence_looks import controls_inputs as inputs, controls_layout as layout, controls_reader as reader
    from joulewise.cadence_looks import controls_run as worker
    from joulewise.cadence_looks.controls_book import Authority, Book

    Book.public_tip = staticmethod(lambda: git(repo, "rev-parse", book.REF))
    make_inputs = inputs.make_inputs
    inputs.make_inputs = lambda *args: make_inputs(*args, synthetic=True)

    if fault == "guard_blind_values":
        from joulewise.cadence_looks import controls_time_fields as fields

        forbidden = ("91827.375", "19.8375")
        original_loads, original_convert = json.loads, fields._convert

        def guarded_loads(raw, *args, **kwargs):
            text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
            assert not any(value in text for value in forbidden), "unprojected blind JSON decode"
            return original_loads(raw, *args, **kwargs)

        def guarded_convert(kind, text):
            assert not any(value in text for value in forbidden), "blind observation conversion"
            return original_convert(kind, text)

        json.loads, fields._convert = guarded_loads, guarded_convert

    if operation == "project":
        authority = Authority(Book(repo))
        binding, source, _ = worker._binding(authority, private)
        projection = worker._check_inputs(authority, binding, private, source)
        fd, _ = layout.open_directory(private)
        try:
            worker._certificates(fd, projection, create=True)
        finally:
            os.close(fd)
        return 0

    def event(value):
        with (bench/"events.jsonl").open("ab") as stream:
            stream.write(manifest.canonical(value) + b"\n")

    os_mkdir, os_fsync, original_claim = os.mkdir, os.fsync, layout.claim
    claim_parent = None

    def mkdir(path, *args, **kwargs):
        nonlocal claim_parent
        if path == layout.PRIVATE_NAME and fault == "mkdir_denied":
            raise PermissionError("synthetic reservation mkdir denial")
        result = os_mkdir(path, *args, **kwargs)
        if path == layout.PRIVATE_NAME:
            claim_parent = kwargs["dir_fd"]
            event("claim")
        return result

    def fsync(fd):
        nonlocal claim_parent
        if fault == "mkdir_sync_once" and fd == claim_parent:
            claim_parent = None
            raise OSError("synthetic reservation directory sync")
        return os_fsync(fd)

    def claim(*args):
        restricted = original_claim(*args)
        event("start")
        return restricted

    os.mkdir, os.fsync, layout.claim = mkdir, fsync, claim
    if fault == "ownership_disabled":
        layout.ownership_enabled = lambda fd: False
    original_read = reader.first_read
    original_decode = reader.meter.parse_bytes
    if fault == "reader_corrupt_leg_bytes":
        from joulewise.cadence_looks import description_inputs

        original_file = description_inputs._regular_file
        started = False

        @contextmanager
        def corrupt_file(path):
            with original_file(path) as stream:
                if started and path.name == "align_episode.json" and "L002" in path.parts:
                    with io.BytesIO(stream.read() + b" ") as corrupted:
                        yield corrupted
                else:
                    yield stream

        description_inputs._regular_file = corrupt_file
    else:
        started = False

    def decode(raw):
        event("ctl_value_decode")
        value = original_decode(raw)
        if fault == "decoder_one_stamp" and value.host_ns and value.host_ns[0] < 12_000_000_000_000:
            # Move one sample on L002's actual episode. Sample identities and
            # support endpoints are unchanged.
            from bisect import bisect_left

            bundle = next((world/"spans").glob("*/legs/L002/runtime/runs/*/outputs/align_episode.json"))
            ep = read(bundle)
            stamp = (ep["start_ns"] + ep["end_ns"]) // 2 + 7_000_000_000
            i = bisect_left(value.host_ns, stamp)
            if 0 < i < len(value.host_ns)-1:
                value.host_ns[i] += 1
        return value

    def first_read(native_inputs, stage1):
        nonlocal started
        if fault == "post_marker_oserror":
            raise OSError("synthetic post-marker error")
        event("first_read")
        started = True
        positions = original_read(native_inputs, stage1)
        observed = {}
        for leg in positions:
            if not isinstance(leg.episode, reader.Episode):
                continue
            for trace in leg.episode.power_traces:
                if (trace.source, trace.channel) == ("wall_meter", "dc_in"):
                    mapping, = (m for m in leg.episode.clock_mappings if m.trace_domain == trace.clock_domain)
                    observed[leg.leg_id] = dict(method=mapping.method, offset_ns=mapping.offset_ns,
                                                uncertainty_ns=mapping.uncertainty_ns,
                                                dc_times_sha256=reader._times_digest(trace.t_ns, -mapping.offset_ns))
        put(bench/"joined-observed.json", observed)
        return positions

    reader.meter.parse_bytes, reader.first_read = decode, first_read
    if fault in ("observe_ruled_h", "observe_zero_h_on_clone"):
        observe_kernel(reader, bench, force_zero=fault == "observe_zero_h_on_clone")
    try:
        return worker.run(operation, repo)
    except layout.GateRefusal as error:
        if os.environ.get("CTL_BENCH_DEBUG"):
            with (bench/"driver-debug.txt").open("a") as stream:
                print_exc(file=stream)
        os.write(2, error.notice.encode())
        return error.status


def observe_kernel(reader, bench, *, force_zero):
    from joulewise.align.attribution import _Trace
    from joulewise.cadence_looks import controls_release

    calculate = controls_release.calculate_private

    def observed_calculation(positions, **kwargs):
        mappings = {}
        input_legs = []
        for leg in positions:
            clocks = []
            for clock in leg.episode.clock_mappings:
                if clock.method == reader.METHOD:
                    if force_zero:
                        clock = replace(clock, uncertainty_ns=0)
                    mappings[leg.leg_id] = dict(method=clock.method, offset_ns=clock.offset_ns,
                                                uncertainty_ns=clock.uncertainty_ns)
                clocks.append(clock)
            input_legs.append(replace(leg, episode=replace(leg.episode, clock_mappings=tuple(clocks))))
        target, = (leg for leg in input_legs if leg.leg_id == "L002")
        stop = json.loads(target.work_bytes)["steps"][-1]["ended_ns"] - 40_000_000_000
        original_kernel = kwargs["kernel"]
        target_trace, _ = original_kernel.phases.selected_trace(target.episode, ("wall_meter", "dc_in"))
        interval = {}

        def observed_energy(trace, start, end, *, mapping=None, **other):
            value = original_kernel.trace_energy(trace, start, end, mapping=mapping, **other)
            if trace is target_trace and (start, end) == (stop - 40_000_000_000, stop):
                reconstruction = _Trace(trace, mapping)
                interval.update(leg_id=target.leg_id, source=trace.source, channel=trace.channel,
                                start_ns=start, end_ns=end, joules=value.joules, half_width_j=value.half_width_j,
                                flags=value.flags, adjacent_peak_w=[reconstruction._adjacent_peak(stamp)
                                                                    for stamp in (start, end)])
            return value

        kwargs["kernel"] = replace(original_kernel, trace_energy=observed_energy)
        output = calculate(input_legs, **kwargs)
        put(bench/"kernel-observed.json", dict(dc_mappings=mappings, interval=interval))
        return output

    controls_release.calculate_private = observed_calculation


if __name__ == "__main__":
    command, source, destination, injected = sys.argv[1:]
    try:
        raise SystemExit(run(command, Path(source), Path(destination), injected))
    except Exception as error:
        if "CTL_PAIR_MOUNT" in os.environ:
            diagnostic = Path(os.environ["CTL_PAIR_MOUNT"]).parent / "pair-failure.txt"
            with diagnostic.open("a") as stream:
                print_exc(file=stream)
                if isinstance(error, subprocess.CalledProcessError):
                    print(error.stdout, error.stderr, file=stream)
        raise
