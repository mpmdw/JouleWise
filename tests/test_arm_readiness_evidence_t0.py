from __future__ import annotations
from tests import receipt_factory

import contextlib
import hashlib
import importlib.machinery
import importlib.util
import inspect
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Mapping
from unittest import mock

from joulewise.hazards import network_time as network_time_off; from joulewise import kernel_clock
from tests.test_kernel_clock import frequency_probe
import joulewise.receipt_readers as readiness
import joulewise.evidence_replay as generic_evidence
import joulewise.physical_checks as t0
import joulewise.adapters.mlx_runtime as mlx_runtime
import joulewise.calibration_ledger as ledger
import joulewise.identity_pins as identity_pins
from tests.t0_factory import author_arm_readiness_evidence_t0; from joulewise.physical_checks import T0EvidenceAuthoringError
pass
from tests.fixtures.arm_clock import REALTIME_OFFSET_NS, coherent_clock_anchor
from tests.test_arm_readiness_dry_run import install_passing_freeze
from tests.receipt_integration_fixtures import (
    clear_initial_arm,
    install_passing_dry_run,
    synthetic_identity_verifier,
)
from tests.test_identity_pins import declared_identity, synthetic_config
from tests.test_arm_readiness_lifecycle import (
    git,
    make_go_fixture,
    synthetic_family_publication_verification,
)
from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID, arm_context


ROOT = Path(__file__).resolve().parents[1]
OTHER_BOOT_SESSION_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
SYNTHETIC_MONOTONIC_NS = 1_000_000_000_000
SYNTHETIC_UTC_NOW = "2026-08-13T20:30:00Z"
SYNTHETIC_REALTIME_OFFSET_NS = REALTIME_OFFSET_NS


def _sntp_line(server: str, *, offset: str = "+0.010000", uncertainty: str = "0.020000") -> str:
    peers = {
        "time.apple.com": "17.253.4.45",
        "pool.ntp.org": "192.0.2.20",
        "time.nist.gov": "129.6.15.28",
    }
    return f"{offset} +/- {uncertainty} {server} {peers[server]}"


def _clock_reference_value(
    *,
    boot_session_id: str,
    anchor_monotonic_raw_ns: int,
    anchor_realtime_ns: int | None = None,
    anchor_read_skew_ns: int = 1_000,
    legs: Mapping[str, tuple[int, str]] | None = None,
) -> dict[str, object]:
    selected = legs or {
        server: (0, _sntp_line(server)) for server in t0._clock_reference.SERVER_ROSTER
    }
    batch_started = anchor_monotonic_raw_ns + 10
    samples = []
    cursor = batch_started + 10
    for server in t0._clock_reference.SERVER_ROSTER:
        exit_code, stdout = selected[server]
        parsed = (
            t0._clock_reference.parse_sntp_stdout(stdout, server=server)
            if exit_code == 0
            else None
        )
        samples.append(
            {
                "server": server,
                "argv": t0._clock_reference.build_sntp_argv(server),
                "exit_code": exit_code,
                "started_monotonic_raw_ns": cursor,
                "finished_monotonic_raw_ns": cursor + 1,
                "stdout": stdout,
                "stderr": "" if exit_code == 0 else "failed",
                "parsed": parsed is not None,
                "offset_s": None if parsed is None else float(parsed.offset_s),
                "uncertainty_s": (
                    None if parsed is None else float(parsed.uncertainty_s)
                ),
                "peer_address": None if parsed is None else parsed.peer_address,
                "raw_line": None if parsed is None else parsed.raw_line,
            }
        )
        cursor += 2
    return {
        "schema_version": t0._clock_reference.SCHEMA_VERSION,
        "sample_policy_id": t0._clock_reference.SAMPLE_POLICY_ID,
        "boot_session_id": boot_session_id,
        "anchor_realtime_ns": (
            SYNTHETIC_REALTIME_OFFSET_NS + anchor_monotonic_raw_ns
            if anchor_realtime_ns is None
            else anchor_realtime_ns
        ),
        "anchor_monotonic_raw_ns": anchor_monotonic_raw_ns,
        "anchor_read_skew_ns": anchor_read_skew_ns,
        "batch_started_monotonic_raw_ns": batch_started,
        "batch_finished_monotonic_raw_ns": cursor,
        "samples": samples,
    }


def _copy(repository: Path, relative: str) -> None:
    target = repository / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(_historical_fixture_source(relative))


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(readiness.render_json(value))


def _capture(
    step: str,
    argv: list[str],
    cwd: Path,
    start: int,
    finish: int,
    *,
    stdout: str = "",
    stderr: str = "",
    exit_code: int = 0,
    boot_session_id: str = TEST_BOOT_SESSION_ID,
) -> dict:
    return {
        "schema_version": t0._COMMAND_SCHEMA,
        "step_id": step,
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "started_monotonic_ns": start,
        "finished_monotonic_ns": finish,
        "boot_session_id": boot_session_id,
    }


def _valid_session_receipt(context: dict, plan_sha256: str, tree: dict) -> dict:
    epoch = {name: f"epoch-{name}" for name in ledger.IDENTITY_EPOCH_FIELDS}
    t1 = {name: f"t1-{name}" for name in ledger.T1_FIELDS}
    slots = {
        role: {
            "attempt_id": context[f"{role}_attempt_id"],
            "custody_locator": str(
                Path(context["claim_runs_root"])
                / "instrument_validation"
                / context[f"{role}_attempt_id"]
            ),
            "identity_epoch": epoch,
            "t1_bindings": t1,
            "expected_time_role": role,
        }
        for role in ("pre", "post")
    }
    session_identity = {
        "session_id": context["bracket_session_id"],
        "window_id": tree["window_identity"]["window_id"],
        "plan_id": tree["plan"]["plan_id"],
        "plan_sha256": plan_sha256,
        "evidence_root_id": tree["window_identity"]["evidence_root_id"],
        "runs_root": context["claim_runs_root"],
    }
    return ledger._new_bracket_session_record(
        sequence=1,
        predecessor_digest=ledger.GENESIS_DIGEST,
        event=ledger.BRACKET_SESSION_OPEN_EVENT,
        session_identity=session_identity,
        fields={"slots": slots},
    )


def _fixture_child_environment(repository: Path) -> dict[str, str]:
    """Environment for the fixture's freeze and arm child processes.

    The synthetic identity is frozen by one child process, re-derived in this
    test process by the T-0 author, and re-derived again by the arm child.
    The runtime identity includes installed distribution versions (the mlx
    adapter reads ``importlib.metadata.version("mlx")``), so all three must
    see the same Python path. Putting only the fixture repository on a
    child's PYTHONPATH dropped whatever this process was given there: with
    the project venv's site-packages on PYTHONPATH, the author saw mlx 0.31.2
    and the freeze child saw no mlx, and the author correctly refused
    "live U11 input derivation differs from the frozen projection". The
    fixture repository stays first, so its synthetic ``mlx_lm`` and its copy
    of ``joulewise`` still shadow any installed ones.
    """

    inherited = os.environ.get("PYTHONPATH")
    entries = [str(repository)]
    if inherited:
        entries.append(inherited)
    return {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(entries),
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def _install_synthetic_identity_inputs(
    repository: Path,
    pack: Path,
    tree: dict,
    *,
    boot_session_override: str | None,
    clock_override: tuple[int, str] | None,
    clock_anchor_override: t0._clock_reference.ClockAnchor | None = None,
) -> None:
    shutil.rmtree(pack / "identity_pin_projection.receipts")
    model = pack / "synthetic-model"
    model.mkdir()
    (model / "weights.safetensors").write_bytes(b"synthetic-weight-bytes")
    configs = [
        synthetic_config(model, "synthetic-r1"),
        synthetic_config(model, "synthetic-r2"),
    ]
    inventory = []
    for index, config in enumerate(configs, start=1):
        relative = f"identity-configs/member-{index}.json"
        raw = readiness.render_json(config)
        path = pack / relative
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(raw)
        inventory.append({"path": relative, "sha256": hashlib.sha256(raw).hexdigest()})
    tree["arm_attachments"]["identity_pin_projection"] = {
        "work_order": identity_pins.IDENTITY_PIN_PROJECTION_WORK_ORDER,
        "mode": "derive_never_operator_enter",
        "state": "unprojected",
        "required_before_arm": True,
        "derivation_contract": identity_pins.IDENTITY_PIN_DERIVATION_CONTRACT,
        "identity_units": [
            {
                "identity_unit_id": "synthetic/decode",
                "producer_plan_reference": {
                    "plan_id": "plan-test",
                    "path": "calibration_plan.json",
                },
                "consumer_bindings": [
                    {
                        "arm": "A",
                        "family": "synthetic-family",
                        "measurement_arm": "decode",
                    }
                ],
                "declared_identity": declared_identity(configs[0]),
                "config_inventory": inventory,
                "model_runtime_config": {
                    "model_artifact_sha256": None,
                    "runtime_identity_sha256": None,
                    "config_set_sha256": None,
                },
            }
        ],
        "projection_receipt": None,
        "supersedes": [],
    }
    (repository / "mlx_lm.py").write_text(
        """\
__version__ = "synthetic-mlx-lm-v1"

class SyntheticTokenizer:
    def __init__(self, source):
        self.name_or_path = source
        self.vocab_size = 256

def load(source, revision=None, return_config=False):
    return object(), SyntheticTokenizer(source), {"model_type": "synthetic", "eos_token_id": 2}

def make_sampler(temp=0.0, temperature=None):
    return ("synthetic-greedy", temp if temperature is None else temperature)

def stream_generate(model, tokenizer, prompt, *, max_tokens=1, sampler=None):
    if False:
        yield None
""",
        encoding="utf-8",
    )
    customization = (
        "from joulewise import receipt_readers as arm_readiness\n"
        "arm_readiness.verify_family_publication_marker = lambda *args, **kwargs: {"
        f"'schema_version': {readiness.FAMILY_PUBLICATION_VERIFICATION_SCHEMA!r},"
        "'receipt_kind': 'family_publication_verification',"
        "'phase': 'pre-arm', 'lane': 'published', 'gate_admissible': True,"
        "'publication_authorized': True, 'status': 'PASS'}\n"
    )
    if boot_session_override is not None:
        customization += (
            "arm_readiness._current_boot_session_id = "
            f"lambda: {boot_session_override!r}\n"
        )
    if clock_override is not None:
        monotonic_ns, utc_now = clock_override
        if clock_anchor_override is None:
            clock_anchor_override = coherent_clock_anchor(raw_ns=monotonic_ns)
        customization += (
            "arm_readiness.time.monotonic_ns = "
            f"lambda: {monotonic_ns!r}\n"
            "arm_readiness._utc_now = "
            f"lambda: {utc_now!r}\n"
        )
    if clock_anchor_override is not None:
        # Observation-only override: launch capability deadlines still use
        # ordinary monotonic time unless clock_override explicitly freezes it.
        live_anchor = {
            "boot_session_id": boot_session_override,
            "realtime_ns": clock_anchor_override.realtime_ns,
            "monotonic_raw_ns": clock_anchor_override.monotonic_raw_ns,
            "read_skew_ns": clock_anchor_override.read_skew_ns,
            "kernel_frequency": frequency_probe(),
        }
        customization += (
            "arm_readiness._sample_live_clock_anchor = "
            f"lambda: {live_anchor!r}\n"
        )
    customization += (
        "from joulewise import kernel_clock, qualification_readers as _q\n"
        "from joulewise import qualification_readers as _writer\n"
        "from pathlib import Path as _Path\n"
        "from unittest import mock as _mock\n"
        f"kernel_clock.read_kernel_frequency = lambda: {frequency_probe()!r}\n"
        "_clock_budget = _q.authenticated_clock_budget\n"
        "def _fixture_budget(inputs, pack):\n"
        "    repo = _Path(pack).parents[2]\n"
        "    def checkout(value):\n"
        "        if _Path(value) != repo: raise ValueError('fixture clock checkout mismatch')\n"
        "        return repo\n"
        "    with _mock.patch.object(_writer, 'pack_roster', return_value=([], [], ['pre', 'post'], [])), _mock.patch.object(arm_readiness, '_authenticate_launcher_identity', side_effect=checkout):\n"
        "        return _clock_budget(inputs, pack)\n"
        "_q.authenticated_clock_budget = _fixture_budget\n"
    )
    (repository / "sitecustomize.py").write_text(
        customization,
        encoding="utf-8",
    )


def _load_synthetic_mlx(repository: Path):
    spec = importlib.util.spec_from_file_location(
        "mlx_lm", repository / "mlx_lm.py"
    )
    if spec is None or spec.loader is None:
        raise AssertionError("synthetic mlx_lm module is unloadable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def _patched_sys_module(name: str, module: object):
    missing = object()
    previous = sys.modules.get(name, missing)
    sys.modules[name] = module
    try:
        yield
    finally:
        if previous is missing:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous


from joulewise import qualification_readers as _qualification
_REAL_CLOCK_BUDGET = _qualification.authenticated_clock_budget


def fixture_clock_budget(inputs, pack):
    """Replay real sizing/custody; specify only this small fixture's roster/checkout."""
    from tests import qualification_plan_factory as writer
    repository = Path(pack).parents[2]
    def checkout(value):
        if Path(value) != repository:
            raise readiness.LaunchLineageError("fixture checkout differs from clock plan")
        return repository
    with (mock.patch.object(writer, "pack_roster", return_value=([], [], ["pre", "post"], [])),
          mock.patch.object(_qualification, "pack_roster", return_value=([], [], ["pre", "post"], [])),
          mock.patch.object(readiness, "_authenticate_launcher_identity", side_effect=checkout)):
        return _REAL_CLOCK_BUDGET(inputs, pack)


def install_clock_sizing_inputs(repository, pack, custody, *, maximum=320.):
    """Source-bound synthetic sizing; the small test pack has a specified roster."""
    from joulewise import qualification_readers as q; from joulewise import night_gate
    from tests import qualification_plan_factory as writer
    root = custody / pack.name / t0._INPUT_DIRECTORY
    window = custody / 'window-plan'
    source = root / 'clock-sizing-source.json'
    _write_json(source, {'seconds': maximum, 'pack_t0_s': 360, 't0_stage_cap_s': 3300,
        'basis': 'synthetic fixture only',
        'diagnostic_anchor_half_width_s': .001, 'stamp_resolution_s': 1e-9,
        'rho_per_s': 1e-6})
    allowance = {'seconds': maximum, 'source': q.reference(source), 'source_pointer': '/seconds'}
    observed = root / 'clock-observed-bound.json'
    _write_json(observed, {'seconds': .004, 'basis': 'synthetic fixture only'})
    sizing = root / 'clock-sizing.json'
    sizing_value = {'fixed': {name: allowance for name in writer.FIXED_COMPONENTS['s1']},
        'members': {}, 'auxiliary': {}, 'streams': {name: allowance for name in ('pre', 'post')},
        'clock': {'diagnostic_anchor_half_width_s': .001, 'stamp_resolution_s': 1e-9,
            'rho_per_s': 1e-6, 'source': q.reference(source),
            'observed_max_effective_bound': {'seconds': .004, 'source': q.reference(observed),
                                           'source_pointer': '/seconds'}}}
    for name in ('pack_t0', 't0_stage_cap'):
        sizing_value['fixed'][name] = {
            'seconds': 360 if name == 'pack_t0' else 3300,
            'source': q.reference(source), 'source_pointer': '/' + name + '_s'}
    window_max_s = writer.size_window('s1', sizing_value, brackets=('pre', 'post'))['window_max_s']
    _write_json(sizing, sizing_value)
    chain = window / 'window-chain.zsh'
    text = re.sub(r'^export NIGHT_(?:CLOCK_(?:SIZING_SHA256|STREAM_MAX_S)|ARM_CONTEXT_SHA256)=.*\n', '', chain.read_text(), flags=re.M)
    chain.write_text(f'export NIGHT_CLOCK_SIZING_SHA256="{q.sha(sizing)}"\n'
                    + f'export NIGHT_CLOCK_STREAM_MAX_S="{maximum}"\n'
                    + f'export NIGHT_ARM_CONTEXT_SHA256="{q.sha(root / "arm-context.json")}"\n' + text)
    sidecar = chain.with_name(chain.name + '.sha256')
    sidecar.write_bytes(readiness.gnu_sidecar(q.sha(chain), chain.name))
    tree, _ = readiness._plan_tree(pack)
    head = readiness.reviewed_main(pack)['head_commit']
    digest = readiness.committed_pack_tree_sha256(pack)
    auth = root / 'clock-sizing-authorization.json'
    _write_json(auth, {'purpose': 'G2B_SHAKEDOWN', 'attempt_id': tree['plan']['plan_id'] + '/1',
        'claim_eligible': False, 'pack_sha256': digest, 'permitted_chain_sha256': q.sha(chain),
        'permitted_blocks': 1, 'authority': 'D-171 §3'})
    table = root / 'clock-sizing-confirmation-table.json'
    _write_json(table, {'fixture': True})
    confirmation = root / 'clock-sizing-confirmation.json'
    _write_json(confirmation, {'table_path': str(table), 'table_sha256': q.sha(table),
        'transcript_sha256': '0'*64,
        'confirmed_at': {'epoch_s': 1., 'iso8601_utc': '1970-01-01T00:00:01.000000Z'}})
    plan = root / 'clock-sizing-plan.json'
    _write_json(plan, {'schema': night_gate.PACK_PLAN_SCHEMA, 'schema_version': 3,
        'plan_id': tree['plan']['plan_id'], 'receipt_class': 'TRANSACTION_PACK',
        't0_epoch_s': 1., 'authored_epoch_s': 0., 'window_max_s': window_max_s,
        'repo_head': head, 'measurement_root': str(repository), 'measurement_head': head,
        'chain_path': str(chain), 'chain_sha256_path': str(sidecar),
        'custody_root': str(custody), 'registration_path': None,
        'pack_night': {'pack_id': pack.name, 'pack_root': str(pack), 'pack_sha256': digest,
            'attempt_ordinal': 1, 'authorization_record': q.reference(auth),
            'confirmation_record': q.reference(confirmation)}})
    _write_json(root / 'kernel-frequency-binding.json', {
        'schema': 'joulewise.v5_qualification_clock_binding.v1', 'occurrence': 's1',
        'plan': q.reference(plan), 'sizing': q.reference(sizing),
        'plan_id': tree['plan']['plan_id'], 'pack_root': str(pack), 'pack_sha256': digest})
    _write_json(root / 'kernel-frequency-gate.json', kernel_clock.frequency_gate(frequency_probe(), maximum))


def make_t0_fixture(
    *,
    boot_session_id: str = TEST_BOOT_SESSION_ID,
    now_monotonic_ns: int = SYNTHETIC_MONOTONIC_NS,
    real_identity: bool = False,
    synthetic_boot_session: bool = True,
    synthetic_clock: bool = True,
    portable_launch_program: bool = False,
    sample_anchor=None,
):
    temporary, repository, pack, custody, _arm_path = make_go_fixture()
    repository = repository.resolve()
    pack = pack.resolve()
    custody = custody.resolve()
    clear_initial_arm(custody, pack.name)
    if real_identity:
        shutil.copytree(ROOT / "joulewise", repository / "joulewise", dirs_exist_ok=True)
        shutil.copytree(ROOT / "scripts", repository / "scripts", dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for relative in (
        "joulewise/network_time_off.py",
        "joulewise/dwell.py",
        "joulewise/prewindow.py",
        "joulewise/clock_reference.py",
        "joulewise/kernel_clock.py",
        "joulewise/arm_readiness_evidence_t0.py",
        "joulewise/identity_pins.py",
        "scripts/author_arm_evidence_t0.py",
        "scripts/capture_t0_step.py",
        "scripts/collect_clock_reference.py",
        "scripts/prewindow_check.sh",
        "scripts/quiet_mac_prep.sh",
        "scripts/recover_calibration_ledger.py",
        "scripts/reserve_calibration_window_bracket.py",
        "configs/calibration/calibration_ledger_head.json",
        "scripts/generate_arm_readiness.py",
        "scripts/mint_floor_artifact_generalized.py",
        "scripts/project_identity_pins.py",
    ):
        _copy(repository, relative)

    tree_path = pack / "plan_tree.json"
    tree = json.loads(tree_path.read_text())
    tree["external_inputs"] = {"artifacts": [], "manifests": []}
    tree["stage_graph"] = [
        {
            "stage_id": "synthetic-stage",
            "launch": {
                "commands": [
                    {
                        "argv_template": {
                            "arguments": [
                                {"kind": "literal", "value": "--power-policy"},
                                {"kind": "literal", "value": "ac_high_power"},
                            ]
                        }
                    }
                ]
            },
        }
    ]
    if real_identity:
        _install_synthetic_identity_inputs(
            repository,
            pack,
            tree,
            boot_session_override=(
                boot_session_id if synthetic_boot_session else None
            ),
            clock_override=(
                (now_monotonic_ns, SYNTHETIC_UTC_NOW)
                if synthetic_clock
                else None
            ),
        )
    tree_raw = readiness.render_json(tree)
    tree_path.write_bytes(tree_raw)
    (pack / "plan_tree.sha256").write_bytes(
        readiness.gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json")
    )
    (repository / ".gitignore").write_text("__pycache__/\n*.pyc\n")
    git(repository, "add", ".")
    git(repository, "commit", "-qm", "T-0 author inputs")
    if real_identity:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/project_identity_pins.py",
                "freeze",
                str(pack),
            ],
            cwd=repository,
            env=_fixture_child_environment(repository),
            text=True,
            capture_output=True,
        )
        if completed.returncode != 0:
            raise AssertionError(
                f"real synthetic identity freeze failed: {completed.stdout}{completed.stderr}"
            )
    if synthetic_boot_session:
        install_passing_freeze(repository, pack)
    else:
        # The real-boot-session variant must build a COHERENT world: the
        # freeze-side evidence carries the live session too, or the arm's
        # boot-session fence (X-3) correctly refuses the mix.
        import tests.test_arm_readiness_dry_run as _dry_mod

        with mock.patch.object(
            _dry_mod, "TEST_BOOT_SESSION_ID", boot_session_id
        ):
            install_passing_freeze(repository, pack)

    pack_sha = readiness.committed_pack_tree_sha256(pack)
    tree_oid = __import__("subprocess").run(
        ["git", "rev-parse", "HEAD^{tree}"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    message = "\n".join(
        (
            "terminal review",
            "",
            "JouleWise-Terminal-Review: PASS",
            f"JouleWise-Terminal-Review-Tree-Oid: {tree_oid}",
            f"JouleWise-Terminal-Review-Pack-Sha256: {pack_sha}",
        )
    )
    git(repository, "commit", "--allow-empty", "-qm", message)
    git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
    if synthetic_boot_session:
        install_passing_dry_run(pack, custody)
    else:
        import tests.test_arm_readiness_dry_run as _dry_mod2

        with mock.patch.object(
            _dry_mod2, "TEST_BOOT_SESSION_ID", boot_session_id
        ):
            install_passing_dry_run(pack, custody)

    context = arm_context(Path(temporary.name).resolve() / "context")
    input_root = custody / pack.name / t0._INPUT_DIRECTORY
    _write_json(input_root / "arm-context.json", context)

    plan_sha = readiness._pack_identity(pack, tree)["plan_sha256"]
    plan_path = pack / "calibration_plan.json"
    epoch_path = Path(temporary.name).resolve() / "identity-epoch.json"
    t1_path = Path(temporary.name).resolve() / "t1-bindings.json"
    ledger_path = Path(temporary.name).resolve() / "production-ledger.jsonl"
    session_receipt = _valid_session_receipt(context, plan_sha, tree)
    _write_json(epoch_path, session_receipt["slots"]["pre"]["identity_epoch"])
    _write_json(t1_path, session_receipt["slots"]["pre"]["t1_bindings"])
    ledger_path.write_text(
        json.dumps(session_receipt, sort_keys=True, separators=(",", ":")) + "\n"
    )

    window_root = custody / "window-plan"
    window_root.mkdir()
    env = {
        "MEASUREMENT_REPO": str(repository),
        "WINDOW_ID": tree["window_identity"]["window_id"],
        "FROZEN_PLAN": str(plan_path),
        "PACK_ROOT": str(pack),
        "PACK_ID": pack.name,
        "PLAN_ID": tree["plan"]["plan_id"],
        "EVIDENCE_ROOT_ID": tree["window_identity"]["evidence_root_id"],
        "IDENTITY_EPOCH_JSON": str(epoch_path),
        "T1_BINDINGS_JSON": str(t1_path),
        "RUNS_ROOT": context["claim_runs_root"],
        "BOUND_RUNS_ROOT": context["bound_runs_root"],
        "CALIBRATION_LEDGER": str(ledger_path),
        "LEDGER_HEAD_PIN": str(
            repository / "configs/calibration/calibration_ledger_head.json"
        ),
        "ARM_READINESS_CUSTODY_ROOT": str(custody),
        "CUSTODY_ROOT": context["custody_root"],
        "WINDOW_CUSTODY_ROOT": context["custody_root"],
        "QUARANTINE_ROOT": context["quarantine_root"],
        "CLAIM_BACKUP_DEST": context["claim_backup_destination"],
        "BOUND_BACKUP_DEST": context["bound_backup_destination"],
        "WAIVER_PATH": context["waiver_path"],
        "SETTLE_S": "180",
        "BRACKET_SESSION_ID": context["bracket_session_id"],
        "PRE_ATTEMPT_ID": context["pre_attempt_id"],
        "POST_ATTEMPT_ID": context["post_attempt_id"],
        "POWER_POLICY": "ac_high_power",
    }
    (window_root / "window.env").write_text(
        "".join(f"{name}={shlex.quote(value)}\n" for name, value in env.items())
    )
    chain_path = window_root / "window-chain.zsh"
    chain_path.write_text(f"#!/bin/zsh\nREPO={repository}\n")
    prewindow_argv = [
        str(repository / ".venv/bin/python"),
        str(repository / "joulewise/prewindow.py"),
        "--t0-wait",
        "--timeout-min",
        "45",
        "--window",
        "alpha",
    ]
    # The frozen argv's program is checked BY NAME only -- `_launch_argv_matches`
    # (joulewise/arm_readiness.py) and the T-0 launch-manifest validator both
    # test `Path(argv[0]).name == "caffeinate"` and nothing else.  A test that
    # actually reaches `os.execve` therefore needs a program that EXISTS on the
    # running machine, and `/usr/bin/caffeinate` is Darwin-only, so it raises
    # FileNotFoundError on a Linux CI runner.  `portable_launch_program` swaps in
    # an executable no-op of the same name inside the fixture tree; every caller
    # that stops short of the exec keeps the real Darwin path unchanged.
    launch_program = "/usr/bin/caffeinate"
    if portable_launch_program:
        shim = window_root / "caffeinate"
        shim.write_text("#!/bin/sh\nexit 0\n")
        shim.chmod(0o755)
        launch_program = str(shim)
    launch_argv = [
        launch_program,
        "-is",
        "/bin/zsh",
        str(chain_path),
        str(window_root),
    ]
    _write_json(
        input_root / "launch-manifest.json",
        {
            "schema_version": t0._LAUNCH_SCHEMA,
            "boot_session_id": boot_session_id,
            "window_plan_root": str(window_root),
            "prewindow_command": prewindow_argv,
            "launch_command": launch_argv,
        },
    )
    time_origin = now_monotonic_ns - t0._MIN_IDLE_NS - 1_000
    r0_anchor_monotonic_raw_ns = time_origin + 20
    if synthetic_clock and sample_anchor is None:
        r0_anchor_realtime_ns = None
        r0_anchor_read_skew_ns = 1_000
    else:
        real_anchor = (sample_anchor or t0._clock_reference.sample_anchor)()
        # R0 and the author anchor use RAW; capture ordering stays monotonic.
        # On Darwin these clock families can diverge across sleep and uptime.
        r0_anchor_monotonic_raw_ns = (
            real_anchor.monotonic_raw_ns - t0._MIN_IDLE_NS - 980
        )
        r0_anchor_realtime_ns = r0_anchor_monotonic_raw_ns + (
            real_anchor.realtime_ns - real_anchor.monotonic_raw_ns
        )
        r0_anchor_read_skew_ns = real_anchor.read_skew_ns
    reservation_argv = [
        str(repository / ".venv/bin/python"),
        str(repository / "scripts/reserve_calibration_window_bracket.py"),
        "--ledger",
        str(ledger_path),
        "--head-pin",
        str(repository / "configs/calibration/calibration_ledger_head.json"),
        "--session-id",
        context["bracket_session_id"],
        "--window-id",
        tree["window_identity"]["window_id"],
        "--plan-id",
        tree["plan"]["plan_id"],
        "--plan-sha256",
        plan_sha,
        "--plan",
        str(plan_path),
        "--evidence-root-id",
        tree["window_identity"]["evidence_root_id"],
        "--runs-root",
        context["claim_runs_root"],
        "--pre-attempt-id",
        context["pre_attempt_id"],
        "--post-attempt-id",
        context["post_attempt_id"],
        "--pre-custody-locator",
        str(Path(context["claim_runs_root"]) / "instrument_validation" / context["pre_attempt_id"]),
        "--post-custody-locator",
        str(Path(context["claim_runs_root"]) / "instrument_validation" / context["post_attempt_id"]),
        "--identity-epoch-json",
        str(epoch_path),
        "--t1-bindings-json",
        str(t1_path),
        "--execute",
    ]
    captures = {
        "clock-reference.json": _capture(
            "clock-reference",
            [
                str(repository / ".venv/bin/python"),
                str(repository / "scripts/collect_clock_reference.py"),
            ],
            repository,
            time_origin + 10,
            time_origin + 200,
            stdout=readiness.render_json(
                _clock_reference_value(
                    boot_session_id=boot_session_id,
                    anchor_monotonic_raw_ns=r0_anchor_monotonic_raw_ns,
                    anchor_realtime_ns=r0_anchor_realtime_ns,
                    anchor_read_skew_ns=r0_anchor_read_skew_ns,
                )
            ).decode("utf-8"),
            boot_session_id=boot_session_id,
        ),
        "clock-disable.json": _capture(
            "clock-disable",
            list(network_time_off.OFF_ARGV),
            repository,
            time_origin + 300,
            time_origin + 310,
            stdout=readiness.EXPECTED_NETWORK_TIME_OFF_STDOUT,
            boot_session_id=boot_session_id,
        ),
        "quiet-mac-prep.json": _capture(
            "quiet-mac-prep",
            ["/bin/bash", str(repository / "scripts/quiet_mac_prep.sh")],
            repository,
            time_origin + 320,
            time_origin + 330,
            stdout=(
                "OK: passwordless powermetrics works.\n"
                "OK: display verification reports all online displays asleep.\n"
                "OK: post-arm evidence reports screensaver disengaged.\nREADY.\n"
            ),
            boot_session_id=boot_session_id,
        ),
        "prewindow-check.json": _capture(
            "prewindow-check",
            prewindow_argv,
            repository,
            time_origin + 400,
            time_origin + 400 + t0._MIN_IDLE_NS,
            stdout="continuous clean dwell 0/600s (check 1)\ncontinuous clean dwell 600/600s (check 2)\nREADY after 10 min.\n",
            boot_session_id=boot_session_id,
        ),
        "ledger-readiness.json": _capture(
            "ledger-readiness",
            [
                str(repository / ".venv/bin/python"),
                str(repository / "scripts/recover_calibration_ledger.py"),
                "--ledger", str(ledger_path),
                "--head-pin", str(repository / "configs/calibration/calibration_ledger_head.json"),
                "readiness",
                "--phase",
                "pre-reserve",
                "--session-id",
                context["bracket_session_id"],
                "--plan",
                str(plan_path),
            ],
            repository,
            time_origin + 500 + t0._MIN_IDLE_NS,
            time_origin + 510 + t0._MIN_IDLE_NS,
            stdout=json.dumps(
                {
                    "status": "ready",
                    "early_warning_only": True,
                    "frozen_plan": {
                        "path": str(plan_path),
                        "plan_id": tree["plan"]["plan_id"],
                        "sha256": plan_sha,
                    },
                }
            ),
            boot_session_id=boot_session_id,
        ),
        "ledger-reservation.json": _capture(
            "ledger-reservation",
            reservation_argv,
            repository,
            time_origin + 520 + t0._MIN_IDLE_NS,
            time_origin + 530 + t0._MIN_IDLE_NS,
            stdout=json.dumps({"status": "reserved", "receipt": session_receipt}),
            stderr=json.dumps({"event": "calibration_pre_reserve_authorized"}) + "\n",
            boot_session_id=boot_session_id,
        ),
    }
    from datetime import datetime
    off_finished = captures["clock-disable.json"]["finished_monotonic_ns"]
    now_epoch = (datetime.fromisoformat(SYNTHETIC_UTC_NOW.replace("Z", "+00:00")).timestamp()
                 if synthetic_clock else time.time())
    _write_json(input_root / network_time_off.RECEIPT_BASENAME, {
        "schema": network_time_off.SCHEMA, "argv": list(network_time_off.OFF_ARGV),
        "exit_code": 0, "stdout": readiness.EXPECTED_NETWORK_TIME_OFF_STDOUT,
        "stderr": "", "error": None, "boot_id": boot_session_id,
        "plan_id": tree["plan"]["plan_id"], "window_id": tree["window_identity"]["window_id"],
        "epoch_s": now_epoch - (now_monotonic_ns - off_finished) / 1e9,
        "monotonic_s": off_finished / 1e9})
    captures["clock-reference.json"].update(kernel_frequency=frequency_probe(), t_stream_max_s=320.)
    _write_json(input_root / "kernel-frequency-gate.json", kernel_clock.frequency_gate(frequency_probe(), 320.))
    install_clock_sizing_inputs(repository, pack, custody)
    for name, value in captures.items():
        _write_json(input_root / name, value)

    if portable_launch_program:
        # The portable mode is consumed by the launch-window integration test,
        # which composes this T-0 stage fragment with make_author_fixture's
        # independently complete verdict/backup graph before re-authoring all
        # freeze evidence.  Keep the R1-complete closeout graph for ordinary
        # T-0 callers, but do not contribute a second pair of backups to that
        # composition: DOCTRINE_PIN requires exactly two in the final pack.
        composable_tree = json.loads(tree_path.read_text())
        composable_tree["stage_graph"] = [
            stage
            for stage in composable_tree["stage_graph"]
            if stage.get("stage_id") not in {"fixture-verdict", "fixture-backup"}
        ]
        composable_raw = readiness.render_json(composable_tree)
        tree_path.write_bytes(composable_raw)
        (pack / "plan_tree.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(composable_raw).hexdigest(), "plan_tree.json"
            )
        )
    return temporary, repository, pack, custody, context, input_root


def _probe_result(argv, cwd, exit_code=0, stdout="", stderr=""):
    # A bytes stdout is what `_execute_probe` captures (the battery probe's
    # grammar reads those exact bytes, obligation R2-11).
    if isinstance(stdout, bytes):
        return t0._ProbeResult(tuple(argv), str(Path(cwd).resolve()), exit_code,
                               stdout.decode("utf-8", errors="replace"), stderr, stdout)
    return t0._ProbeResult(tuple(argv), str(Path(cwd).resolve()), exit_code, stdout, stderr)


def _float_ioreg(name="float.ioreg", *, age_s=0) -> bytes:
    """A real capture (tests/fixtures/battery_float) whose `UpdateTime` is
    `age_s` before the authoring clock's now: fixed under the synthetic clock
    (so re-authoring stays byte-idempotent), fresh under the real one."""
    from datetime import datetime
    now = datetime.fromisoformat(t0._production_clock().utc_now().replace("Z", "+00:00"))
    raw = (Path(__file__).parent / "fixtures/battery_float" / name).read_bytes()
    return raw.replace(
        b'"UpdateTime" = 1790373525', f'"UpdateTime" = {int(now.timestamp()) - age_s}'.encode(), 1
    )


def passing_probe(argv, *, cwd):
    command = tuple(argv)
    joined = " ".join(command)
    if "kern.bootsessionuuid" in command:
        return _probe_result(command, cwd, stdout=TEST_BOOT_SESSION_ID + "\n")
    if command and command[0] == t0._clock_reference.SNTP_PATH:
        return _probe_result(command, cwd, stdout=_sntp_line(command[-1]) + "\n")
    if "systemsetup" in joined:
        return _probe_result(
            command, cwd, stdout=readiness.EXPECTED_NETWORK_TIME_OFF_STDOUT
        )
    if "/usr/bin/pgrep" in command:
        return _probe_result(command, cwd, exit_code=1)
    if command == t0._prewindow.PS_ARGV:
        return _probe_result(command, cwd, stdout="1 0.0 launchd\n")
    if command[-2:] == ("-g", "therm"):
        return _probe_result(
            command,
            cwd,
            stdout=(
                "Note: No thermal warning level has been recorded\n"
                "Note: No performance warning level has been recorded\n"
            ),
        )
    if command[-2:] == ("-g", "batt"):
        return _probe_result(command, cwd, stdout="Now drawing from 'AC Power'\n")
    if command[-2:] == ("-g", "custom"):
        return _probe_result(command, cwd, stdout=" lowpowermode 0\n")
    if command == t0._battery_float.IOREG_BATTERY_ARGV:
        return _probe_result(command, cwd, stdout=_float_ioreg())
    if "SPPowerDataType" in command:
        return _probe_result(
            command,
            cwd,
            stdout=json.dumps(
                {"adapter": {"sppower_charger_wattage": "140", "sppower_charger_connected": "Yes"}}
            ),
        )
    if any(Path(item).name == "powermetrics" for item in command):
        return _probe_result(command, cwd, stdout="Machine model: synthetic\n")
    raise AssertionError(f"unexpected probe: {command!r}")


@contextlib.contextmanager
def author_environment(
    repository: Path,
    *,
    probe=passing_probe,
    offline=None,
    real_offline: bool = False,
    boot_session_id: str = TEST_BOOT_SESSION_ID,
    free=100 * 1024**3,
    now_monotonic_ns: int = SYNTHETIC_MONOTONIC_NS,
    synthetic_clock: bool = True,
    sample_anchor=None,
    kernel_frequency=None,
    real_clock_budget: bool = False,
):
    if probe is passing_probe and boot_session_id != TEST_BOOT_SESSION_ID:
        def selected_probe(argv, *, cwd):
            if "kern.bootsessionuuid" in argv:
                return _probe_result(argv, cwd, stdout=boot_session_id + "\n")
            return passing_probe(argv, cwd=cwd)
    else:
        selected_probe = probe
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.object(kernel_clock, "read_kernel_frequency",
            return_value=frequency_probe() if kernel_frequency is None else kernel_frequency))
        if not real_clock_budget:
            stack.enter_context(mock.patch.object(_qualification, "authenticated_clock_budget",
                                                   side_effect=fixture_clock_budget))
        stack.enter_context(mock.patch.object(t0._time, "sleep"))
        stack.enter_context(mock.patch.object(t0, "_RUNNING_REPOSITORY", repository))
        if selected_probe is not None:
            stack.enter_context(mock.patch.object(t0, "_execute_probe", side_effect=selected_probe))
        if real_offline:
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            stack.enter_context(
                mock.patch.object(
                    t0._identity, "_mint_git_anchor", return_value=(repository, head)
                )
            )
            stack.enter_context(
                _patched_sys_module("mlx_lm", _load_synthetic_mlx(repository))
            )
        else:
            offline = offline or (
                lambda _context, *, kind: (
                    [],
                    {
                        "projection_input_sha256": "a" * 64,
                        "identity_check_count": 1,
                    },
                )
            )
            stack.enter_context(
                mock.patch.object(t0, "_reverify_offline_inputs", side_effect=offline)
            )
        stack.enter_context(
            mock.patch.object(t0._shutil, "disk_usage", return_value=mock.Mock(free=free))
        )
        if synthetic_clock:
            clock = t0._DerivationClock(
                monotonic_ns=lambda: now_monotonic_ns,
                utc_now=lambda: SYNTHETIC_UTC_NOW,
                sample_anchor=(
                    sample_anchor
                    if sample_anchor is not None
                    else lambda: coherent_clock_anchor(raw_ns=now_monotonic_ns)
                ),
            )
            stack.enter_context(
                mock.patch.object(t0, "_production_clock", return_value=clock)
            )
        yield


def _cli_stdout(buffer: io.BytesIO) -> mock.Mock:
    return mock.Mock(
        buffer=buffer,
        fileno=mock.Mock(side_effect=io.UnsupportedOperation("fileno")),
        isatty=mock.Mock(return_value=False),
    )


# Packet 34, Exhibit C: eight Apple executables across ten recorded lines,
# plus watchdogd. Preserve the captured truncation and strip only the PID.
_RECORDED_CENSUS_SERVICE_ARGV = (
    '/System/Cryptexes/App/usr/libexec/SafariBookmarksSyncAgent',
    '/System/Volumes/Preboot/Cryptexes/App/System/Applications/Safari.app/Contents/Extensions/SafariWidgetExtension.appex/Contents/MacOS/SafariWidgetExtension -',
    '/System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/XPCServices/com.apple.SafariPlatformSupport.Helper.xpc/Contents/MacOS/com.appl',
    '/System/Library/PrivateFrameworks/SafariFoundation.framework/Versions/A/XPCServices/CredentialProviderExtensionHelper.xpc/Contents/MacOS/CredentialProvider',
    '/System/Volumes/Preboot/Cryptexes/App/System/Applications/Safari.app/Contents/Extensions/SafariLinkExtension.appex/Contents/MacOS/SafariLinkExtension -Laun',
    '/System/Library/PrivateFrameworks/SafariSafeBrowsing.framework/com.apple.Safari.SafeBrowsing.Service',
    '/System/Cryptexes/App/usr/libexec/SafariLaunchAgent',
    '/System/Library/PrivateFrameworks/SafariFoundation.framework/Versions/A/XPCServices/SafariConfigurationSubscriber.xpc/Contents/MacOS/SafariConfigurationSu',
    '/System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/XPCServices/com.apple.SafariPlatformSupport.Helper.xpc/Contents/MacOS/com.app',
    '/System/Library/PrivateFrameworks/SafariPlatformSupport.framework/Versions/A/XPCServices/com.apple.SafariPlatformSupport.Helper.xpc/Contents/MacOS/com.app',
    "/usr/libexec/watchdogd",
)
_RECORDED_FIREFOX_LINE = "24781 /Applications/Firefox.app/Contents/MacOS/firefox"
_RECORDED_CENSUS_SERVICE_BASENAMES = (
    "SafariBookmarksSyncAgent", "SafariWidgetExtension",
    "com.apple.SafariPlatformSupport.Helper", "CredentialProviderExtensionHelper",
    "SafariLinkExtension", "com.apple.Safari.SafeBrowsing.Service",
    "SafariLaunchAgent", "SafariConfigurationSubscriber", "watchdogd",
)


class ArmReadinessEvidenceT0Tests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        publication_patcher = mock.patch.object(
            readiness,
            "verify_family_publication_marker",
            side_effect=synthetic_family_publication_verification,
        )
        clock_patcher = mock.patch.object(
            readiness,
            "_sample_live_clock_anchor",
            return_value={
                "boot_session_id": TEST_BOOT_SESSION_ID,
                "realtime_ns": SYNTHETIC_REALTIME_OFFSET_NS
                + SYNTHETIC_MONOTONIC_NS,
                "monotonic_raw_ns": SYNTHETIC_MONOTONIC_NS,
                "read_skew_ns": 1_000,
                "kernel_frequency": frequency_probe(),
            },
        )
        publication_patcher.start()
        clock_patcher.start()
        sizing_patcher = mock.patch.object(
            _qualification, "authenticated_clock_budget", side_effect=fixture_clock_budget
        )
        sizing_patcher.start()
        self.addCleanup(sizing_patcher.stop)
        self.addCleanup(clock_patcher.stop)
        self.addCleanup(publication_patcher.stop)




    def _author_with_r1_age(self, age_ns: int) -> dict[str, object]:
        temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        clock_state = {"now": SYNTHETIC_MONOTONIC_NS}
        original_batch = t0._fresh_clock_reference_batch

        def finish_r1_then_advance(context, *, kind):
            result = original_batch(context, kind=kind)
            clock_state["now"] += age_ns
            return result

        clock = t0._DerivationClock(
            monotonic_ns=lambda: clock_state["now"],
            utc_now=lambda: SYNTHETIC_UTC_NOW,
            sample_anchor=lambda: t0._clock_reference.ClockAnchor(
                realtime_ns=(
                    SYNTHETIC_REALTIME_OFFSET_NS + SYNTHETIC_MONOTONIC_NS
                ),
                monotonic_raw_ns=SYNTHETIC_MONOTONIC_NS,
                read_skew_ns=1_000,
            ),
        )
        with (
            author_environment(repository),
            mock.patch.object(t0, "_production_clock", return_value=clock),
            mock.patch.object(
                t0,
                "_fresh_clock_reference_batch",
                side_effect=finish_r1_then_advance,
            ),
        ):
            return author_arm_readiness_evidence_t0(pack, custody)







    def _assert_clock_refusal(
        self,
        *,
        detail: str,
        mutate=None,
        probe=passing_probe,
        now_monotonic_ns: int = SYNTHETIC_MONOTONIC_NS,
        sample_anchor=None,
        kind: str = "CLOCK_ATTESTATION",
        reason_code: str = "evidence_author_t0_clock_attestation_underivable",
    ) -> None:
        temporary, repository, pack, custody, _context, inputs = make_t0_fixture(
            now_monotonic_ns=now_monotonic_ns
        )
        self.addCleanup(temporary.cleanup)
        if mutate is not None:
            mutate(inputs)
        with (
            author_environment(
                repository,
                probe=probe,
                now_monotonic_ns=now_monotonic_ns,
                sample_anchor=sample_anchor,
            ),
            self.assertRaises(T0EvidenceAuthoringError) as caught,
        ):
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(caught.exception.kind, kind)
        self.assertEqual(caught.exception.reason_code, reason_code)
        self.assertEqual(str(caught.exception), detail)
        self.assertFalse((custody / pack.name / t0._SOURCE_DIRECTORY).exists())
        self.assertFalse((custody / pack.name / t0._EVIDENCE_DIRECTORY).exists())

    @staticmethod
    def _replace_r0(
        inputs: Path,
        *,
        legs: Mapping[str, tuple[int, str]] | None = None,
        anchor_raw: int | None = None,
        anchor_realtime: int | None = None,
        anchor_skew: int = 1_000,
    ) -> None:
        path = inputs / "clock-reference.json"
        capture = json.loads(path.read_text(encoding="utf-8"))
        current = json.loads(capture["stdout"])
        value = _clock_reference_value(
            boot_session_id=current["boot_session_id"],
            anchor_monotonic_raw_ns=(
                current["anchor_monotonic_raw_ns"]
                if anchor_raw is None
                else anchor_raw
            ),
            anchor_realtime_ns=anchor_realtime,
            anchor_read_skew_ns=anchor_skew,
            legs=legs,
        )
        capture["stdout"] = readiness.render_json(value).decode("utf-8")
        _write_json(path, capture)

    @staticmethod
    def _reference_probe(
        legs: Mapping[str, tuple[int, str]],
    ):
        def probe(argv, *, cwd):
            command = tuple(argv)
            if command and command[0] == t0._clock_reference.SNTP_PATH:
                exit_code, stdout = legs[command[-1]]
                return _probe_result(
                    command,
                    cwd,
                    exit_code=exit_code,
                    stdout=stdout,
                    stderr="" if exit_code == 0 else "failed",
                )
            return passing_probe(command, cwd=cwd)

        return probe

    @staticmethod
    def _terminal_review_message(tree_oid: str, packs: tuple[str, ...]) -> str:
        return "\n".join(
            (
                "terminal review",
                "",
                "JouleWise-Terminal-Review: PASS",
                f"JouleWise-Terminal-Review-Tree-Oid: {tree_oid}",
                *(
                    f"JouleWise-Terminal-Review-Pack-Sha256: {pack}"
                    for pack in packs
                ),
            )
        )

    def _derive_terminal_review_for(
        self, message: str, *, pack_sha256: str
    ) -> t0._DerivedRow:
        context = SimpleNamespace(
            repository=ROOT,
            head_tree_oid="1" * 40,
            pack_sha256=pack_sha256,
        )
        artifact = ({"path": "synthetic", "sha256": "f" * 64}, b"synthetic")
        with (
            mock.patch.object(t0, "_git_message", return_value=message),
            mock.patch.object(t0, "_committed_artifact", return_value=artifact),
        ):
            return t0._derive_terminal_review(context)

    def _assert_terminal_review_refuses(
        self, message: str, *, pack_sha256: str
    ) -> None:
        with self.assertRaises(T0EvidenceAuthoringError) as caught:
            self._derive_terminal_review_for(message, pack_sha256=pack_sha256)
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_t0_terminal_review_record_missing",
        )














































    def _assert_forbidden_process_evidence_expires_before_arm(
        self, *, start_real_process: bool
    ) -> None:
        authored_at = 1_000_000_000_000
        short_horizon_ns = 20 * 60 * 1_000_000_000
        temporary, repository, pack, custody, context, _inputs = make_t0_fixture(
            now_monotonic_ns=authored_at
        )
        self.addCleanup(temporary.cleanup)
        with author_environment(repository, now_monotonic_ns=authored_at):
            author_arm_readiness_evidence_t0(pack, custody)

        if start_real_process:
            process = subprocess.Popen(["/usr/bin/caffeinate", "-t", "60"])

            def stop_forbidden_process() -> None:
                if process.poll() is None:
                    process.terminate()
                process.wait(timeout=5)

            self.addCleanup(stop_forbidden_process)
            self.assertIsNone(
                process.poll(), "the post-authoring forbidden process must be live"
            )
        with (
            mock.patch.object(
                readiness,
                "_current_boot_session_id",
                return_value=TEST_BOOT_SESSION_ID,
            ),
            mock.patch.object(
                readiness,
                "verify_frozen_projection",
                side_effect=synthetic_identity_verifier,
            ),
            mock.patch.object(
                readiness.time,
                "monotonic_ns",
                return_value=(authored_at + short_horizon_ns + 1),
            ),
        ):
            arm = receipt_factory.generate_arm_receipt(pack, context, custody)
        self.assertEqual(arm["status"], "REFUSE", arm)
        self.assertEqual(arm["arm_disposition"], "NO_GO")
        self.assertIn("readiness_record_expired", arm["reason_codes"])
        arm_receipt = json.loads(Path(arm["receipt_path"]).read_text(encoding="utf-8"))
        self.assertTrue(
            any(
                refusal["code"] == "readiness_record_expired"
                and refusal["evidence_id"] == "arm-t0-t0-no-stray-keepawake-v1"
                for refusal in arm_receipt["refusals"]
            ),
            arm_receipt["refusals"],
        )




    def _real_probe_source(self, kind, commands):
        context = t0._Context(
            pack_root=ROOT,
            repository=ROOT,
            custody_root=ROOT,
            custody_pack_root=ROOT,
            tree={},
            pack_sha256="a" * 64,
            plan_sha256="b" * 64,
            head_commit="c" * 40,
            head_tree_oid="d" * 40,
            boot_session_id=TEST_BOOT_SESSION_ID,
            boot_probe=_probe_result(("/usr/sbin/sysctl",), ROOT),
        )
        real_popen = t0._subprocess.Popen
        with mock.patch.object(
            t0._subprocess,
            "Popen",
            side_effect=lambda *args, **kwargs: real_popen(*args, **kwargs),
        ) as popen:
            probes = tuple(t0._execute_probe(command, cwd=ROOT) for command in commands)
        for probe in probes:
            if (probe.argv[0] == "/usr/bin/pgrep" and probe.exit_code == 3
                    and "Cannot get process list" in probe.stderr):
                self.skipTest("/usr/bin/pgrep unavailable in sandbox: exit 3, Cannot get process list")
        self.assertEqual(popen.call_count, len(commands))
        row = t0._DerivedRow(
            f"test.{kind.lower()}",
            kind,
            {
                "live_exit_codes": [probe.exit_code for probe in probes],
                "live_stdout_sha256": [
                    hashlib.sha256(probe.stdout.encode("utf-8")).hexdigest()
                    for probe in probes
                ],
                "live_stderr_sha256": [
                    hashlib.sha256(probe.stderr.encode("utf-8")).hexdigest()
                    for probe in probes
                ],
            },
            "PROBE",
            probes=probes,
        )
        source = json.loads(t0._source_bytes(context, row))
        self.assertEqual(
            source["facts"][0]["value"]["live_exit_codes"],
            [probe.exit_code for probe in probes],
        )
        self.assertEqual(
            [probe["argv"] for probe in source["probes"]],
            [list(command) for command in commands],
        )
        self.assertEqual(
            [probe["stdout"] for probe in source["probes"]],
            [probe.stdout for probe in probes],
        )
        self.assertEqual(
            [probe["stderr"] for probe in source["probes"]],
            [probe.stderr for probe in probes],
        )
        return probes, source




















    def _assert_acid_authored_fifteen_then_arm_generator_reaches_go(
        self,
        *,
        boot_session_id: str,
        synthetic_boot_session: bool,
        synthetic_clock: bool,
    ) -> None:
        now_monotonic_ns = (
            SYNTHETIC_MONOTONIC_NS if synthetic_clock else time.monotonic_ns()
        )
        temporary, repository, pack, custody, context, _inputs = make_t0_fixture(
            boot_session_id=boot_session_id,
            now_monotonic_ns=now_monotonic_ns,
            real_identity=True,
            synthetic_boot_session=synthetic_boot_session,
            synthetic_clock=synthetic_clock,
        )
        self.addCleanup(temporary.cleanup)
        with author_environment(
            repository,
            real_offline=True,
            boot_session_id=boot_session_id,
            now_monotonic_ns=now_monotonic_ns,
            synthetic_clock=synthetic_clock,
        ):
            result = author_arm_readiness_evidence_t0(pack, custody)
            self.assertEqual(len(result["authored_rows"]), 15)
            if not synthetic_clock:
                clock_receipt = next(
                    json.loads(Path(path).read_text(encoding="utf-8"))
                    for path in result["receipt_paths"]
                    if json.loads(Path(path).read_text(encoding="utf-8"))["kind"]
                    == "CLOCK_ATTESTATION"
                )
                self.assertLess(
                    clock_receipt["facts"][0]["value"]["anchor_delta_ns"],
                    500_000,
                    "real R0-to-author RAW anchor delta must retain a 10x margin",
                )
        command = [
            sys.executable,
            "scripts/generate_arm_readiness.py",
            "arm",
            "--pack-root",
            str(pack),
            "--arm-context",
            json.dumps(context, sort_keys=True, separators=(",", ":")),
            "--window-custody-root",
            str(custody),
        ]
        with mock.patch.object(
            readiness,
            "generate_arm_receipt",
            side_effect=AssertionError("the ACID path must cross the CLI process boundary"),
        ):
            completed = subprocess.run(
                command,
                cwd=repository,
                env=_fixture_child_environment(repository),
                text=True,
                capture_output=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        arm = json.loads(completed.stdout)
        self.assertEqual(arm["reason_codes"], [])
        self.assertEqual(arm["status"], "PASS", arm)
        self.assertEqual(arm["arm_disposition"], "GO")
        identity_path = (
            custody
            / pack.name
            / "receipts"
            / context["bracket_session_id"]
            / "identity-pin-arm-verify.json"
        )
        identity_receipt = json.loads(identity_path.read_text(encoding="utf-8"))
        self.assertEqual(identity_receipt["receipt_kind"], "arm_reverification")
        self.assertEqual(identity_receipt["status"], "PASS")
        self.assertEqual(identity_receipt["reason_codes"], [])
        self.assertEqual(
            identity_receipt["identity_units"][0]["identity_unit_id"],
            "synthetic/decode",
        )
        self.assertTrue(identity_receipt["checks"])
        self.assertTrue(
            all(check["status"] == "PASS" for check in identity_receipt["checks"])
        )
        self.assertTrue(
            all(
                "shared_mint_projection" in check["check_id"]
                for check in identity_receipt["checks"]
            )
        )
        self.assertTrue(
            all(
                check["expected"] == check["observed"]
                for check in identity_receipt["checks"]
            )
        )
        self.assertIn(
            "joulewise.identity_pins._runtime_probe_metadata",
            identity_receipt["derivation"]["callables"],
        )
        self.assertNotEqual(
            identity_receipt["pack"]["projection_input_sha256"], "0" * 64
        )
        self.assertEqual(
            len(identity_receipt["identity_units"][0]["config_inventory"]), 2
        )


    def test_rf01_r0_fixed_roster_and_one_attempt_policy_refuses(self) -> None:
        def mutate(inputs: Path) -> None:
            path = inputs / "clock-reference.json"
            capture = json.loads(path.read_text(encoding="utf-8"))
            value = json.loads(capture["stdout"])
            value["samples"][1]["server"] = "substitute.invalid"
            capture["stdout"] = readiness.render_json(value).decode("utf-8")
            _write_json(path, capture)

        self._assert_clock_refusal(
            mutate=mutate,
            detail="R0 clock reference does not prove the fixed roster and one-attempt policy",
        )


    def test_rf01_r0_peer_address_must_equal_reparsed_stdout(self) -> None:
        def mutate(inputs: Path) -> None:
            path = inputs / "clock-reference.json"
            capture = json.loads(path.read_text(encoding="utf-8"))
            value = json.loads(capture["stdout"])
            value["samples"][0]["peer_address"] = "192.0.2.99"
            capture["stdout"] = readiness.render_json(value).decode("utf-8")
            _write_json(path, capture)

        self._assert_clock_refusal(
            mutate=mutate,
            detail="R0 clock reference parseable leg alters its peer address",
        )


    def test_rf01_r0_raw_line_must_equal_reparsed_stdout(self) -> None:
        def mutate(inputs: Path) -> None:
            path = inputs / "clock-reference.json"
            capture = json.loads(path.read_text(encoding="utf-8"))
            value = json.loads(capture["stdout"])
            value["samples"][0]["raw_line"] = "forged raw line"
            capture["stdout"] = readiness.render_json(value).decode("utf-8")
            _write_json(path, capture)

        self._assert_clock_refusal(
            mutate=mutate,
            detail="R0 clock reference parseable leg alters its raw line",
        )


    def test_rf02_r0_quorum_boundary_one_refuses_two_passes(self) -> None:
        one = {
            "time.apple.com": (0, _sntp_line("time.apple.com")),
            "pool.ntp.org": (69, ""),
            "time.nist.gov": (69, ""),
        }
        self._assert_clock_refusal(
            mutate=lambda inputs: self._replace_r0(inputs, legs=one),
            detail="R0 reference quorum has fewer than two parseable legs",
        )
        two = dict(one)
        two["pool.ntp.org"] = (0, _sntp_line("pool.ntp.org"))
        temporary, repository, pack, custody, _context, inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        self._replace_r0(inputs, legs=two)
        with author_environment(repository):
            self.assertEqual(
                author_arm_readiness_evidence_t0(pack, custody)["status"], "PASS"
            )


    def test_rf03_r0_disjoint_and_inconvenient_leg_cannot_be_discarded(self) -> None:
        two_disjoint = {
            "time.apple.com": (
                0,
                _sntp_line(
                    "time.apple.com", offset="+0.000000", uncertainty="0.010000"
                ),
            ),
            "pool.ntp.org": (
                0,
                _sntp_line(
                    "pool.ntp.org", offset="+0.100000", uncertainty="0.010000"
                ),
            ),
            "time.nist.gov": (69, ""),
        }
        self._assert_clock_refusal(
            mutate=lambda inputs: self._replace_r0(inputs, legs=two_disjoint),
            detail="R0 reference agreement intervals have empty intersection",
        )
        legs = {
            "time.apple.com": (
                0,
                _sntp_line(
                    "time.apple.com", offset="+0.000000", uncertainty="0.010000"
                ),
            ),
            "pool.ntp.org": (
                0,
                _sntp_line(
                    "pool.ntp.org", offset="+0.005000", uncertainty="0.010000"
                ),
            ),
            "time.nist.gov": (
                0,
                _sntp_line(
                    "time.nist.gov", offset="+0.100000", uncertainty="0.010000"
                ),
            ),
        }
        self._assert_clock_refusal(
            mutate=lambda inputs: self._replace_r0(inputs, legs=legs),
            detail="R0 reference agreement intervals have empty intersection",
        )


    def test_rf04_r0_reference_bound_boundary_gates(self) -> None:
        def legs(offset: str) -> dict[str, tuple[int, str]]:
            return {
                server: (
                    0,
                    _sntp_line(server, offset=offset, uncertainty="0.000000"),
                )
                for server in t0._clock_reference.SERVER_ROSTER
            }

        temporary, repository, pack, custody, _context, inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        self._replace_r0(inputs, legs=legs("+0.500000"))
        with author_environment(repository):
            self.assertEqual(
                author_arm_readiness_evidence_t0(pack, custody)["status"], "PASS"
            )
        self._assert_clock_refusal(
            mutate=lambda inputs: self._replace_r0(
                inputs, legs=legs("+0.500001")
            ),
            detail="R0 reference bound exceeds 0.5 seconds",
        )


    def test_rf05_r0_anchor_read_skew_boundary_gates(self) -> None:
        temporary, repository, pack, custody, _context, inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        self._replace_r0(inputs, anchor_skew=1_000_000)
        with author_environment(repository):
            self.assertEqual(
                author_arm_readiness_evidence_t0(pack, custody)["status"], "PASS"
            )
        self._assert_clock_refusal(
            mutate=lambda inputs: self._replace_r0(
                inputs, anchor_skew=1_000_001
            ),
            detail="R0 anchor read skew exceeds 1000000 ns",
        )


    def test_rf06_r1_quorum_boundary_one_refuses_two_passes(self) -> None:
        one = {
            "time.apple.com": (0, _sntp_line("time.apple.com") + "\n"),
            "pool.ntp.org": (69, ""),
            "time.nist.gov": (69, ""),
        }
        self._assert_clock_refusal(
            probe=self._reference_probe(one),
            detail="R1 reference quorum has fewer than two parseable legs",
        )
        two = dict(one)
        two["pool.ntp.org"] = (0, _sntp_line("pool.ntp.org") + "\n")
        temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        with author_environment(repository, probe=self._reference_probe(two)):
            self.assertEqual(
                author_arm_readiness_evidence_t0(pack, custody)["status"], "PASS"
            )


    def test_rf07_r1_disjoint_and_successful_inconvenient_leg_refuses(self) -> None:
        two_disjoint = {
            "time.apple.com": (
                0,
                _sntp_line(
                    "time.apple.com", offset="+0.000000", uncertainty="0.010000"
                ),
            ),
            "pool.ntp.org": (
                0,
                _sntp_line(
                    "pool.ntp.org", offset="+0.100000", uncertainty="0.010000"
                ),
            ),
            "time.nist.gov": (69, ""),
        }
        self._assert_clock_refusal(
            probe=self._reference_probe(two_disjoint),
            detail="R1 reference agreement intervals have empty intersection",
        )
        legs = {
            "time.apple.com": (
                0,
                _sntp_line(
                    "time.apple.com", offset="+0.000000", uncertainty="0.010000"
                ),
            ),
            "pool.ntp.org": (
                0,
                _sntp_line(
                    "pool.ntp.org", offset="+0.005000", uncertainty="0.010000"
                ),
            ),
            "time.nist.gov": (
                0,
                _sntp_line(
                    "time.nist.gov", offset="+0.100000", uncertainty="0.010000"
                ),
            ),
        }
        self._assert_clock_refusal(
            probe=self._reference_probe(legs),
            detail="R1 reference agreement intervals have empty intersection",
        )


    def test_rf08_r1_reference_bound_boundary_gates(self) -> None:
        def probes(offset: str):
            return self._reference_probe(
                {
                    server: (
                        0,
                        _sntp_line(
                            server, offset=offset, uncertainty="0.000000"
                        ),
                    )
                    for server in t0._clock_reference.SERVER_ROSTER
                }
            )

        temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        with author_environment(repository, probe=probes("+0.500000")):
            self.assertEqual(
                author_arm_readiness_evidence_t0(pack, custody)["status"], "PASS"
            )
        self._assert_clock_refusal(
            probe=probes("+0.500001"),
            detail="R1 reference bound exceeds 0.5 seconds",
        )


    def test_insufficient_positive_capture_history_refuses(self) -> None:
        self._assert_clock_refusal(
            now_monotonic_ns=500_000_000_000,
            detail="clock-reference command capture fields are invalid or stale",
        )


    def test_r0_raw_anchor_ahead_of_author_raw_refuses(self) -> None:
        now = SYNTHETIC_MONOTONIC_NS

        def mutate(inputs: Path) -> None:
            self._replace_r0(
                inputs,
                anchor_raw=now + 1,
                anchor_realtime=SYNTHETIC_REALTIME_OFFSET_NS + now + 1,
            )

        self._assert_clock_refusal(
            now_monotonic_ns=now,
            mutate=mutate,
            detail="T-0 RAW anchor span is below 600000000000 ns",
        )


    def test_capture_finish_ahead_of_ordinary_now_refuses(self) -> None:
        now = SYNTHETIC_MONOTONIC_NS

        def mutate(inputs: Path) -> None:
            path = inputs / "clock-reference.json"
            capture = json.loads(path.read_text(encoding="utf-8"))
            capture["finished_monotonic_ns"] = now + 1
            _write_json(path, capture)

        self._assert_clock_refusal(
            now_monotonic_ns=now,
            mutate=mutate,
            detail="clock-reference command capture is not a live T-0 artifact",
        )


    def test_rf09_rf10_author_span_boundaries_gate(self) -> None:
        now = 5_000_000_000_000
        for span, expected in (
            (599_999_999_999, False),
            (600_000_000_000, True),
            (600_000_000_001, True),
            (3_599_999_999_999, True),
            (3_600_000_000_000, True),
            (3_600_000_000_001, False),
        ):
            def mutate(inputs: Path, span: int = span) -> None:
                raw = now - span
                self._replace_r0(
                    inputs,
                    anchor_raw=raw,
                    anchor_realtime=SYNTHETIC_REALTIME_OFFSET_NS + raw,
                )

            if expected:
                temporary, repository, pack, custody, _context, inputs = make_t0_fixture(
                    now_monotonic_ns=now
                )
                self.addCleanup(temporary.cleanup)
                mutate(inputs)
                with author_environment(repository, now_monotonic_ns=now):
                    self.assertEqual(
                        author_arm_readiness_evidence_t0(pack, custody)["status"],
                        "PASS",
                    )
            else:
                detail = (
                    "T-0 RAW anchor span is below 600000000000 ns"
                    if span < 600_000_000_000
                    else "T-0 RAW anchor span exceeds 3600000000000 ns"
                )
                self._assert_clock_refusal(
                    mutate=mutate,
                    detail=detail,
                    now_monotonic_ns=now,
                )


    def test_rf11_author_anchor_falsifier_boundaries_gate(self) -> None:
        for delta, expected in ((4_999_999, True), (5_000_001, False)):
            def mutate(inputs: Path, delta: int = delta) -> None:
                capture = json.loads(
                    (inputs / "clock-reference.json").read_text(encoding="utf-8")
                )
                reference = json.loads(capture["stdout"])
                self._replace_r0(
                    inputs,
                    anchor_realtime=(
                        SYNTHETIC_REALTIME_OFFSET_NS
                        + reference["anchor_monotonic_raw_ns"]
                        + delta
                    ),
                )

            if expected:
                temporary, repository, pack, custody, _context, inputs = make_t0_fixture()
                self.addCleanup(temporary.cleanup)
                mutate(inputs)
                with author_environment(repository):
                    authored = author_arm_readiness_evidence_t0(pack, custody)
                self.assertEqual(authored["status"], "PASS")
            else:
                self._assert_clock_refusal(
                    mutate=mutate,
                    detail="R0-to-author RAW anchor delta exceeds 5000000 ns",
                )


    def test_rf12_author_anchor_read_skew_boundary_gates(self) -> None:
        for skew, expected in ((999_999, True), (1_000_000, True), (1_000_001, False)):
            anchor = lambda skew=skew: t0._clock_reference.ClockAnchor(
                realtime_ns=SYNTHETIC_REALTIME_OFFSET_NS + SYNTHETIC_MONOTONIC_NS,
                monotonic_raw_ns=SYNTHETIC_MONOTONIC_NS,
                read_skew_ns=skew,
            )
            if expected:
                temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
                self.addCleanup(temporary.cleanup)
                with author_environment(repository, sample_anchor=anchor):
                    self.assertEqual(
                        author_arm_readiness_evidence_t0(pack, custody)["status"],
                        "PASS",
                    )
            else:
                self._assert_clock_refusal(
                    sample_anchor=anchor,
                    detail="author anchor read skew exceeds 1000000 ns",
                )


    def test_rf13_r0_boot_mismatch_refuses(self) -> None:
        def mutate(inputs: Path) -> None:
            path = inputs / "clock-reference.json"
            capture = json.loads(path.read_text(encoding="utf-8"))
            reference = json.loads(capture["stdout"])
            reference["boot_session_id"] = OTHER_BOOT_SESSION_ID
            capture["stdout"] = readiness.render_json(reference).decode("utf-8")
            _write_json(path, capture)

        self._assert_clock_refusal(
            mutate=mutate,
            detail="R0 clock reference schema, sample policy, or boot binding is invalid",
        )


    def test_rf14_r0_must_complete_before_clock_disable_and_r1_before_censuses(self) -> None:
        def mutate(inputs: Path) -> None:
            reference_path = inputs / "clock-reference.json"
            disable = json.loads(
                (inputs / "clock-disable.json").read_text(encoding="utf-8")
            )
            reference = json.loads(reference_path.read_text(encoding="utf-8"))
            reference["finished_monotonic_ns"] = disable["started_monotonic_ns"] + 1
            _write_json(reference_path, reference)

        self._assert_clock_refusal(
            mutate=mutate,
            detail="R0 did not complete before the first clock-disable action",
        )
        calls: list[tuple[str, ...]] = []

        def ordered_probe(argv, *, cwd):
            calls.append(tuple(argv))
            return passing_probe(argv, cwd=cwd)

        temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        with author_environment(repository, probe=ordered_probe):
            author_arm_readiness_evidence_t0(pack, custody)
        last_sntp = max(
            index
            for index, argv in enumerate(calls)
            if argv and argv[0] == t0._clock_reference.SNTP_PATH
        )
        first_census = min(
            index
            for index, argv in enumerate(calls)
            if argv and argv[0] == "/usr/bin/pgrep"
        )
        self.assertLess(last_sntp, first_census)


    def test_rf14_clock_disable_must_finish_before_r1_starts(self) -> None:
        temporary, repository, pack, custody, _context, inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        disable = json.loads(
            (inputs / "clock-disable.json").read_text(encoding="utf-8")
        )

        def r1_started_before_disable_finished(context, *, kind):
            context.values["r1_batch_started_monotonic_ns"] = (
                disable["finished_monotonic_ns"] - 1
            )
            return (mock.sentinel.agreement, (), 0, mock.sentinel.anchor, 0)

        with (
            author_environment(repository),
            mock.patch.object(
                t0,
                "_fresh_clock_reference_batch",
                side_effect=r1_started_before_disable_finished,
            ),
            self.assertRaises(T0EvidenceAuthoringError) as caught,
        ):
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(caught.exception.kind, "CLOCK_ATTESTATION")
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_t0_clock_attestation_underivable",
        )
        self.assertEqual(
            str(caught.exception),
            "clock-disable did not finish before the R1 batch",
        )
        self.assertFalse((custody / pack.name / t0._SOURCE_DIRECTORY).exists())
        self.assertFalse((custody / pack.name / t0._EVIDENCE_DIRECTORY).exists())


    def test_rf14_census_refuses_missing_or_future_r1_completion_stamp(self) -> None:
        # Merely observing the happy deriver order cannot falsify this guard.
        # Inject each invalid state at the census boundary instead.
        for label, kind, values in (
            ("missing", "MAINTENANCE_CENSUS", {}),
            (
                "future",
                "PROCESS_CENSUS",
                {"r1_batch_finished_monotonic_ns": 101},
            ),
        ):
            context = SimpleNamespace(
                values=values,
                clock=SimpleNamespace(monotonic_ns=lambda: 100),
                repository=ROOT,
            )
            execute = mock.Mock(
                side_effect=AssertionError("invalid chronology must gate the census")
            )
            with (
                self.subTest(state=label),
                mock.patch.object(t0, "_execute_probe", execute),
                self.assertRaises(T0EvidenceAuthoringError) as caught,
            ):
                t0._fresh_probe(context, kind, "synthetic census", ("probe",))
            self.assertEqual(
                caught.exception.reason_code,
                f"evidence_author_t0_{kind.lower()}_underivable",
            )
            self.assertEqual(
                str(caught.exception),
                "fresh census cannot run before the R1 clock-reference batch completes",
            )
            execute.assert_not_called()


    def test_rf15_noncanonical_clock_reference_capture_refuses_missing_code(self) -> None:
        def mutate(inputs: Path) -> None:
            path = inputs / "clock-reference.json"
            path.write_bytes(path.read_bytes() + b" ")

        self._assert_clock_refusal(
            mutate=mutate,
            detail=(
                "clock-reference command capture is not canonical strict JSON: "
                "JSON bytes are not canonical D-134 bytes"
            ),
            reason_code="evidence_author_t0_clock_attestation_missing",
        )


    def test_rf16_r1_batch_duration_boundary_gates(self) -> None:
        now = SYNTHETIC_MONOTONIC_NS
        for duration, expected in (
            (-1, False),
            (0, True),
            (1, True),
            (29_999_999_999, True),
            (30_000_000_000, True),
            (30_000_000_001, False),
        ):
            anchors = iter(
                (
                    t0._clock_reference.ClockAnchor(
                        SYNTHETIC_REALTIME_OFFSET_NS + now - duration,
                        now - duration,
                        1_000,
                    ),
                    t0._clock_reference.ClockAnchor(
                        SYNTHETIC_REALTIME_OFFSET_NS + now,
                        now,
                        1_000,
                    ),
                )
            )
            sampler = lambda anchors=anchors: next(anchors)
            if expected:
                temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
                self.addCleanup(temporary.cleanup)
                with author_environment(repository, sample_anchor=sampler):
                    self.assertEqual(
                        author_arm_readiness_evidence_t0(pack, custody)["status"],
                        "PASS",
                    )
            else:
                self._assert_clock_refusal(
                    sample_anchor=sampler,
                    detail="R1 batch duration is outside 0 through 30000000000 ns",
                )


    def test_rf21_rf22_off_receipt_requires_exit_and_exact_stdout(self) -> None:
        for field, value in (("exit_code", 1), ("stdout", "Network Time: Off\n"), ("stdout", "setUsingNetworkTime: On\n")):
            def mutate(inputs, field=field, value=value):
                path = inputs / network_time_off.RECEIPT_BASENAME
                off = json.loads(path.read_bytes())
                off[field] = value
                _write_json(path, off)
            self._assert_clock_refusal(
                mutate=mutate, detail="network time OFF receipt not admitted",
                kind="CLOCK_PROBE", reason_code="evidence_author_t0_clock_probe_underivable")


    def test_rf36_r1_fixed_roster_one_attempt_and_raw_peer_records(self) -> None:
        def substituted_probe(argv, *, cwd):
            command = tuple(argv)
            if command and command[0] == t0._clock_reference.SNTP_PATH:
                return _probe_result(
                    (*command[:-1], "substitute.invalid"),
                    cwd,
                    stdout=_sntp_line(command[-1]),
                )
            return passing_probe(command, cwd=cwd)

        self._assert_clock_refusal(
            probe=substituted_probe,
            detail="R1 clock reference does not prove the fixed one-attempt roster",
        )
        temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        with author_environment(repository):
            author_arm_readiness_evidence_t0(pack, custody)
        source = json.loads(
            (
                custody
                / pack.name
                / t0._SOURCE_DIRECTORY
                / f"{t0._slug('clock.correct_and_prior_state')}.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(source["probes"]), 3)
        for server, probe in zip(t0._clock_reference.SERVER_ROSTER, source["probes"]):
            parsed = t0._clock_reference.parse_sntp_stdout(
                probe["stdout"], server=server
            )
            self.assertIsNotNone(parsed)
            self.assertIn(parsed.peer_address, parsed.raw_line)


    def test_rf37_r0_boolean_endpoint_refuses_integer_contract(self) -> None:
        def mutate(inputs: Path) -> None:
            path = inputs / "clock-reference.json"
            capture = json.loads(path.read_text(encoding="utf-8"))
            reference = json.loads(capture["stdout"])
            reference["anchor_monotonic_raw_ns"] = True
            capture["stdout"] = readiness.render_json(reference).decode("utf-8")
            _write_json(path, capture)

        self._assert_clock_refusal(
            mutate=mutate,
            detail="R0 clock reference numeric endpoint is not an integer",
        )


    @unittest.skipUnless(
        sys.platform == "darwin", "requires Darwin's real pgrep command semantics"
    )
    def test_real_maintenance_census_executes_pgrep_and_binds_output(self) -> None:
        self._real_probe_source(
            "MAINTENANCE_CENSUS",
            (
                (
                    "/usr/bin/pgrep",
                    "-lf",
                    "XProtect|mds_stores|mdworker|mdbulkimport|backupd|photoanalysisd|softwareupdated|Spotlight|mediaanalysisd",
                ),
            ),
        )


    @unittest.skipUnless(
        sys.platform == "darwin", "requires Darwin's real pgrep command semantics"
    )
    def test_real_process_census_executes_pgrep_and_binds_output(self) -> None:
        self._real_probe_source(
            "PROCESS_CENSUS",
            (
                ("/usr/bin/pgrep", "-x", "caffeinate"),
                ("/usr/bin/pgrep", "-a", "-lf", "[c]odex|[c]laude"),
                (
                    "/usr/bin/pgrep",
                    "-lf",
                    "/Contents/MacOS/(Safari|Google Chrome|Chromium|firefox)( |$)",
                ),
                (
                    "/usr/bin/pgrep",
                    "-lf",
                    "powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)",
                ),
            ),
        )


    def test_g1_ruled_census_patterns_ignore_recorded_macos_services(self) -> None:
        """G1 (packet 34 ruling 10 Q3): the recorded Apple services never match.

        Kills M1 (old browser alternation), M2 (no ``( |$)`` tail), M4 (bare
        ``watch``); M5 is killed by G2. M-numbers name the ruling's mutations.
        """
        for pattern in (t0._BROWSER_CENSUS_PATTERN, t0._MONITOR_CENSUS_PATTERN):
            for line in _RECORDED_CENSUS_SERVICE_ARGV:
                with self.subTest(pattern=pattern, line=line):
                    self.assertIsNone(re.search(pattern, line))


    def test_g2_ruled_census_patterns_refuse_real_browsers_and_monitors(self) -> None:
        """G2 (packet 34 ruling 10 Q3): real browsers and monitors match.

        Kills M3 (one browser name), M5 (no ``/Contents/MacOS/`` anchor), M6
        (a lost monitor token), M7 (``Firefox`` case-fold).
        """
        for line in (
            _RECORDED_FIREFOX_LINE.split(" ", 1)[1],
            "/Applications/Safari.app/Contents/MacOS/Safari",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --x",
            "/Applications/Chromium.app/Contents/MacOS/Chromium --headless=new",
            "/Applications/Firefox.app/Contents/MacOS/firefox https://example.com",
            "/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing --headless=new",
            "/Applications/Safari Technology Preview.app/Contents/MacOS/Safari Technology Preview",
        ):
            with self.subTest(browser=line):
                self.assertIsNotNone(re.search(t0._BROWSER_CENSUS_PATTERN, line))
        for line in (
            "/Applications/Firefox.app/Contents/MacOS/plugin-container -isForBrowser",
            "/usr/bin/env Safari",
        ):
            with self.subTest(nonbrowser=line):
                self.assertIsNone(re.search(t0._BROWSER_CENSUS_PATTERN, line))
        for line in (
            "/usr/bin/powermetrics -i 200 -n 1",
            "tail -f /var/log/system.log",
            "watch -n 5 pmset -g therm",
            "/opt/homebrew/bin/watch -n 1 date",
            "python3 scripts/window-chain.py",
            "python3 scripts/run_campaign.py",
        ):
            with self.subTest(monitor=line):
                self.assertIsNotNone(re.search(t0._MONITOR_CENSUS_PATTERN, line))


    def test_g3_browser_and_monitor_probes_gate_the_row(self) -> None:
        """G3 (packet 34 ruling 10 Q3): a browser or monitor hit refuses authoring.

        Kills M8 (an unchecked probe output) and M9 (a reordered or missing
        probe); the mocked probe stands in for pgrep on the authoring path.
        """
        commands = (
            ("/usr/bin/pgrep", "-x", "caffeinate"),
            ("/usr/bin/pgrep", "-a", "-lf", "[c]odex|[c]laude"),
            ("/usr/bin/pgrep", "-lf", t0._BROWSER_CENSUS_PATTERN),
            ("/usr/bin/pgrep", "-lf", t0._MONITOR_CENSUS_PATTERN),
        )
        for selected, output in (
            (commands[1], "123 codex\n"),
            (commands[2], _RECORDED_FIREFOX_LINE + "\n"),
            (commands[3], "574 /usr/bin/powermetrics -i 200\n"),
            (None, ""),
        ):
            with self.subTest(command=selected):
                temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
                with temporary:
                    seen = []

                    def probe(argv, *, cwd):
                        command = tuple(argv)
                        if command in commands:
                            seen.append(command)
                        if command == selected:
                            return _probe_result(argv, cwd, exit_code=0, stdout=output)
                        return passing_probe(argv, cwd=cwd)

                    with author_environment(repository, probe=probe):
                        if selected is None:
                            result = author_arm_readiness_evidence_t0(pack, custody)
                            self.assertEqual(result["status"], "PASS")
                        else:
                            with self.assertRaises(T0EvidenceAuthoringError) as caught:
                                author_arm_readiness_evidence_t0(pack, custody)
                            self.assertEqual(caught.exception.kind, "PROCESS_CENSUS")
                            self.assertFalse((custody / pack.name / t0._SOURCE_DIRECTORY).exists())
                            self.assertFalse((custody / pack.name / t0._EVIDENCE_DIRECTORY).exists())
                    self.assertEqual(seen, list(commands))


    @unittest.skipUnless(
        sys.platform == "darwin", "requires Darwin's POSIX extended regular expressions"
    )
    def test_g4_real_ruled_census_pgrep_dialect(self) -> None:
        r"""G4 kills M10: a construct pgrep rejects or silently never matches.

        Authority: packet 34 ruling 10 Q3 as amended by pairing refuter 12 (A2)
        and the synthesis-13 addendum (the decoy instrument). A *probe* is one
        recorded command execution; a *decoy* is a ``sleep`` child this test
        spawns whose argv0 carries a marker command line; the *dialect* is the
        regular-expression syntax pgrep's own engine interprets. Every
        alternative of each ruled pattern gets a positive decoy that MUST be
        reported by the real pgrep, and the recorded Apple services get
        negative decoys that MUST NOT be, so a Python-only construct (``\b``,
        ``\d``, ``(?:...)``) or a narrowed alternative fails closed with no
        browser or monitor running (bench-proven: ``\bwatch\b`` yields exit 1
        and zero lines against a live decoy). Bench-only: CI runs Linux.
        """
        cases = (
            (
                t0._BROWSER_CENSUS_PATTERN,
                (
                    "/Applications/Safari.app/Contents/MacOS/Safari",
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "/Applications/Chromium.app/Contents/MacOS/Chromium",
                    "/Applications/Firefox.app/Contents/MacOS/firefox",
                ),
                (
                    "/System/Volumes/Preboot/Cryptexes/App/System/Applications/Safari.app/Contents/Extensions/SafariWidgetExtension.appex/Contents/MacOS/SafariWidgetExtension",
                    "/System/Cryptexes/App/usr/libexec/SafariLaunchAgent",
                    "/Applications/Firefox.app/Contents/MacOS/plugin-container",
                ),
            ),
            (
                t0._MONITOR_CENSUS_PATTERN,
                (
                    "/usr/bin/powermetrics",
                    "/usr/bin/tail -f",
                    "scripts/window-chain",
                    "scripts/run_campaign",
                    "/opt/homebrew/bin/watch",
                ),
                ("/usr/libexec/watchdogd", "/usr/local/bin/stopwatch"),
            ),
        )
        # Every recorded service identity is a deterministic negative decoy,
        # checked in the same pgrep snapshot as the positives, so the check
        # does not depend on a live service surviving a later read. Full
        # executable paths are rebuilt where the recorded argv was truncated.
        service_paths = tuple(
            str(
                Path(
                    next(
                        argv.split(" ", 1)[0]
                        for argv in _RECORDED_CENSUS_SERVICE_ARGV
                        if basename in argv
                    )
                ).parent / basename
            )
            for basename in _RECORDED_CENSUS_SERVICE_BASENAMES
        )
        for pattern, positives, negatives in cases:
            with self.subTest(pattern=pattern):
                negative_markers = negatives + service_paths
                decoys = [
                    subprocess.Popen([marker, "30"], executable="/bin/sleep")
                    for marker in positives + negative_markers
                ]
                try:
                    time.sleep(0.5)
                    # PID-only output: with ``-lf`` a live process whose argv
                    # holds a newline prints continuation lines with no PID,
                    # which no line parser can tell from a new row. Matching
                    # is unchanged (``-f`` still matches the full argv); each
                    # hit's full argv is then read back per PID for a pattern
                    # check (lane TEST-CENSUS-MULTILINE-ARGV-01).
                    probes, _source = self._real_probe_source(
                        "PROCESS_CENSUS", (("/usr/bin/pgrep", "-f", pattern),)
                    )
                    probe = probes[0]
                    self.assertEqual(probe.exit_code, 0, probe.stderr)
                    reported = {int(line) for line in probe.stdout.splitlines()}
                    for decoy in decoys:
                        self.assertIsNone(decoy.poll())
                    for decoy, marker in zip(
                        decoys, positives + negative_markers, strict=True
                    ):
                        with self.subTest(marker=marker):
                            if marker in positives:
                                self.assertIn(decoy.pid, reported, probe.stdout)
                            else:
                                self.assertNotIn(decoy.pid, reported, probe.stdout)
                    for pid in sorted(reported):
                        shown = subprocess.run(
                            ["/bin/ps", "-ww", "-o", "command=", "-p", str(pid)],
                            capture_output=True, text=True, check=False,
                        )
                        if shown.returncode != 0 and pid not in {d.pid for d in decoys}:
                            continue  # an unrelated hit exited after pgrep ran
                        self.assertEqual(shown.returncode, 0, shown.stderr)
                        self.assertIsNotNone(re.search(pattern, shown.stdout), shown.stdout)
                finally:
                    for decoy in decoys:
                        decoy.terminate()
                    for decoy in decoys:
                        decoy.wait(timeout=5)


    @unittest.skipUnless(
        sys.platform == "darwin", "requires Darwin's real sysctl command"
    )
    def test_real_boot_census_executes_sysctl_and_binds_machine_result(self) -> None:
        probes, _source = self._real_probe_source(
            "MACHINE_PREFLIGHT",
            (("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"),),
        )
        probe = probes[0]
        if probe.exit_code == 0:
            self.assertRegex(
                probe.stdout.strip().lower(),
                r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
            )
        else:
            self.assertTrue(probe.stderr.strip())


    def test_power_row_battery_probe_passes_exact_bytes_and_refuses_cr_smuggle(self) -> None:
        # Obligation R2-11 (refuter M-4): `_execute_probe` keeps the child's
        # exact stdout bytes and the power row hands those bytes, not the
        # decoded text, to the grammar.  A real child writes the refuter's
        # CR-smuggled output.
        import dataclasses
        from datetime import datetime
        import sys
        from tests import battery_float_corpus
        execute = t0._execute_probe
        now = int(datetime.fromisoformat(t0._production_clock().utc_now().replace("Z", "+00:00")).timestamp())
        smuggle = battery_float_corpus.negatives(now)["cr_smuggled_required"]
        temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        children = []
        def probe(argv, *, cwd):
            if tuple(argv) == t0._battery_float.IOREG_BATTERY_ARGV:
                child = execute((sys.executable, "-c",
                                 "import sys; sys.stdout.buffer.write(bytes.fromhex(sys.argv[1]))",
                                 smuggle.hex()), cwd=cwd)
                children.append(child)
                return dataclasses.replace(child, argv=tuple(argv))
            return passing_probe(argv, cwd=cwd)
        with author_environment(repository, probe=probe), self.assertRaises(
            T0EvidenceAuthoringError
        ) as caught:
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(caught.exception.kind, "POWER_PREFLIGHT")
        self.assertRegex(str(caught.exception), "battery float probe error: .*framing: byte")
        [child] = children
        self.assertEqual(child.stdout_bytes, smuggle)
        self.assertIn("\r", child.stdout)


    def test_power_row_refuses_charging_and_stale_battery_and_records_float(self) -> None:
        # Final texts v1.1 §5.3 item 5: the t0 power row's own ioreg probe.
        cases = (
            ("charging", "charging-synthetic-from-real.ioreg", 0, "battery not at float"),
            ("stale", "float.ioreg", 181, "battery float probe error: .*UpdateTime stale"),
        )
        for label, name, age_s, detail in cases:
            with self.subTest(case=label):
                temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
                try:
                    def probe(argv, *, cwd, name=name, age_s=age_s):
                        if tuple(argv) == t0._battery_float.IOREG_BATTERY_ARGV:
                            return _probe_result(argv, cwd, stdout=_float_ioreg(name, age_s=age_s))
                        return passing_probe(argv, cwd=cwd)
                    with author_environment(repository, probe=probe), self.assertRaises(
                        T0EvidenceAuthoringError
                    ) as caught:
                        author_arm_readiness_evidence_t0(pack, custody)
                    self.assertEqual(caught.exception.kind, "POWER_PREFLIGHT")
                    self.assertRegex(str(caught.exception), detail)
                    self.assertFalse((custody / pack.name / t0._EVIDENCE_DIRECTORY).exists())
                finally:
                    temporary.cleanup()
        temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        seen = []
        def recording_probe(argv, *, cwd):
            seen.append(tuple(argv))
            return passing_probe(argv, cwd=cwd)
        with author_environment(repository, probe=recording_probe):
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertIn(t0._battery_float.IOREG_BATTERY_ARGV, seen)
        self.assertEqual(t0._PROBE_TIMEOUT_OVERRIDES, {
            t0._battery_float.IOREG_BATTERY_ARGV: 10, t0._prewindow.PS_ARGV: 5,
        })
        source = json.loads(
            (custody / pack.name / t0._SOURCE_DIRECTORY / "t0-power-path.json").read_text()
        )
        observation = source["derivation"]["battery_float"]
        self.assertEqual(observation["phase"], "t0_power_row")
        self.assertTrue(observation["passed"])
        self.assertIn(
            list(t0._battery_float.IOREG_BATTERY_ARGV),
            [probe["argv"] for probe in source["probes"]],
        )







if __name__ == "__main__":
    unittest.main()


def _historical_fixture_source(relative):
    """Copy code only, from this tree or the preserved pre-prune source tree."""
    path = ROOT / relative
    if path.is_file():
        return path.read_bytes()
    if not str(relative).endswith((".py", ".sh")):
        raise FileNotFoundError(path)
    return subprocess.check_output(["git", "-C", str(ROOT), "show", "92026c184:" + str(relative)])
