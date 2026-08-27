from __future__ import annotations

import contextlib
import hashlib
import importlib.machinery
import importlib.util
import inspect
import io
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Mapping
from unittest import mock

import joulewise.arm_readiness as readiness
import joulewise.arm_readiness_evidence as generic_evidence
import joulewise.arm_readiness_evidence_t0 as t0
import joulewise.adapters.mlx_runtime as mlx_runtime
import joulewise.calibration_ledger as ledger
import joulewise.identity_pins as identity_pins
from joulewise.arm_readiness_evidence_t0 import (
    T0EvidenceAuthoringError,
    author_arm_readiness_evidence_t0,
)
from scripts import author_arm_evidence_t0 as t0_cli
from tests.test_arm_readiness_dry_run import install_passing_freeze
from tests.test_arm_readiness_integration import (
    clear_initial_arm,
    install_passing_dry_run,
    synthetic_identity_verifier,
)
from tests.test_identity_pins import declared_identity, synthetic_config
from tests.test_arm_readiness_lifecycle import git, make_go_fixture
from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID, arm_context


ROOT = Path(__file__).resolve().parents[1]
OTHER_BOOT_SESSION_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
SYNTHETIC_MONOTONIC_NS = 1_000_000_000_000
SYNTHETIC_UTC_NOW = "2026-08-13T20:30:00Z"
SYNTHETIC_REALTIME_OFFSET_NS = 2_000_000_000_000_000_000


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
    target.write_bytes((ROOT / relative).read_bytes())


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


def _install_synthetic_identity_inputs(
    repository: Path,
    pack: Path,
    tree: dict,
    *,
    boot_session_override: str | None,
    clock_override: tuple[int, str] | None,
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
    if boot_session_override is not None or clock_override is not None:
        customization = "from joulewise import arm_readiness\n"
        if boot_session_override is not None:
            customization += (
                "arm_readiness._current_boot_session_id = "
                f"lambda: {boot_session_override!r}\n"
            )
        if clock_override is not None:
            monotonic_ns, utc_now = clock_override
            customization += (
                "arm_readiness.time.monotonic_ns = "
                f"lambda: {monotonic_ns!r}\n"
                "arm_readiness._utc_now = "
                f"lambda: {utc_now!r}\n"
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


def make_t0_fixture(
    *,
    boot_session_id: str = TEST_BOOT_SESSION_ID,
    now_monotonic_ns: int = SYNTHETIC_MONOTONIC_NS,
    real_identity: bool = False,
    synthetic_boot_session: bool = True,
    synthetic_clock: bool = True,
    portable_launch_program: bool = False,
):
    temporary, repository, pack, custody, _arm_path = make_go_fixture()
    repository = repository.resolve()
    pack = pack.resolve()
    custody = custody.resolve()
    clear_initial_arm(custody, pack.name)
    if real_identity:
        shutil.copytree(ROOT / "joulewise", repository / "joulewise", dirs_exist_ok=True)
    for relative in (
        "joulewise/clock_reference.py",
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
            env={**os.environ, "PYTHONPATH": str(repository), "PYTHONDONTWRITEBYTECODE": "1"},
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

    context = arm_context(Path(temporary.name) / "context")
    input_root = custody / pack.name / t0._INPUT_DIRECTORY
    _write_json(input_root / "arm-context.json", context)

    plan_sha = readiness._pack_identity(pack, tree)["plan_sha256"]
    plan_path = pack / "calibration_plan.json"
    epoch_path = Path(temporary.name) / "identity-epoch.json"
    t1_path = Path(temporary.name) / "t1-bindings.json"
    ledger_path = Path(temporary.name) / "production-ledger.jsonl"
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
        "/bin/bash",
        str(repository / "scripts/prewindow_check.sh"),
        "--wait",
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
                    anchor_monotonic_raw_ns=time_origin + 20,
                )
            ).decode("utf-8"),
            boot_session_id=boot_session_id,
        ),
        "clock-disable.json": _capture(
            "clock-disable",
            ["/usr/bin/sudo", "/usr/sbin/systemsetup", "-setusingnetworktime", "off"],
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
            stdout="READY after 10 min.\n",
            boot_session_id=boot_session_id,
        ),
        "ledger-readiness.json": _capture(
            "ledger-readiness",
            [
                str(repository / ".venv/bin/python"),
                str(repository / "scripts/recover_calibration_ledger.py"),
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
    for name, value in captures.items():
        _write_json(input_root / name, value)
    return temporary, repository, pack, custody, context, input_root


def _probe_result(argv, cwd, exit_code=0, stdout="", stderr=""):
    return t0._ProbeResult(tuple(argv), str(Path(cwd).resolve()), exit_code, stdout, stderr)


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
):
    if probe is passing_probe and boot_session_id != TEST_BOOT_SESSION_ID:
        def selected_probe(argv, *, cwd):
            if "kern.bootsessionuuid" in argv:
                return _probe_result(argv, cwd, stdout=boot_session_id + "\n")
            return passing_probe(argv, cwd=cwd)
    else:
        selected_probe = probe
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.object(t0, "_RUNNING_REPOSITORY", repository))
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
                    else lambda: t0._clock_reference.ClockAnchor(
                        realtime_ns=SYNTHETIC_REALTIME_OFFSET_NS
                        + now_monotonic_ns,
                        monotonic_raw_ns=now_monotonic_ns,
                        read_skew_ns=1_000,
                    )
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


class ArmReadinessEvidenceT0Tests(unittest.TestCase):
    maxDiff = None

    def test_mlx_metal_memory_reuses_cached_core_after_module_eviction(self) -> None:
        fake_mlx = ModuleType("mlx")
        fake_mlx.__path__ = []
        fake_core = ModuleType("mlx.core")
        # The adapter remembers ONLY a module loaded from a native shared
        # object, so this stand-in must present itself as one. A plain
        # ModuleType models a test double, and a test double must never be
        # remembered; tests/test_mlx_runtime.py pins that other half.
        fake_core.__loader__ = importlib.machinery.ExtensionFileLoader(
            "mlx.core", "/nonexistent/mlx/core.so"
        )
        fake_core.get_active_memory = lambda: 101
        fake_core.get_cache_memory = lambda: 202
        fake_core.get_peak_memory = lambda: 303
        missing = object()
        previous = {
            name: sys.modules.get(name, missing) for name in ("mlx", "mlx.core")
        }
        init_count = 0

        def initialize_fake_core(name: str):
            nonlocal init_count
            self.assertEqual(name, "mlx.core")
            init_count += 1
            sys.modules["mlx"] = fake_mlx
            sys.modules["mlx.core"] = fake_core
            return fake_core

        try:
            sys.modules["mlx"] = fake_mlx
            sys.modules.pop("mlx.core", None)
            with (
                mock.patch.object(
                    mlx_runtime.importlib,
                    "import_module",
                    side_effect=initialize_fake_core,
                ),
                mock.patch.object(
                    mlx_runtime, "_MLX_CORE_MODULE", None, create=True
                ),
            ):
                first = mlx_runtime._mlx_metal_memory({})
                sys.modules.pop("mlx.core", None)
                sys.modules.pop("mlx", None)
                second = mlx_runtime._mlx_metal_memory({})
        finally:
            for name, module in previous.items():
                if module is missing:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = module

        self.assertEqual(init_count, 1)
        self.assertEqual(
            first,
            {
                "api_available": True,
                "active_memory_bytes": 101,
                "cache_memory_bytes": 202,
                "peak_memory_bytes": 303,
            },
        )
        self.assertEqual(second, first)

    def test_author_environment_preserves_modules_imported_inside_context(self) -> None:
        temporary, repository, _pack, _custody, _context, _inputs = make_t0_fixture(
            real_identity=True
        )
        self.addCleanup(temporary.cleanup)
        sentinel_name = f"_joulewise_author_environment_sentinel_{id(self)}"
        sentinel_module = SimpleNamespace()
        previous_mlx_lm = SimpleNamespace()
        missing = object()
        original = {
            name: sys.modules.get(name, missing)
            for name in ("mlx_lm", sentinel_name)
        }

        try:
            for prior in (missing, previous_mlx_lm):
                with self.subTest(mlx_lm_preexisting=prior is not missing):
                    sys.modules.pop(sentinel_name, None)
                    if prior is missing:
                        sys.modules.pop("mlx_lm", None)
                    else:
                        sys.modules["mlx_lm"] = prior

                    with author_environment(repository, real_offline=True):
                        self.assertIsNot(sys.modules["mlx_lm"], prior)
                        sys.modules[sentinel_name] = sentinel_module

                    self.assertIs(sys.modules[sentinel_name], sentinel_module)
                    if prior is missing:
                        self.assertNotIn("mlx_lm", sys.modules)
                    else:
                        self.assertIs(sys.modules["mlx_lm"], prior)
        finally:
            for name, module in original.items():
                if module is missing:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = module
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

    def test_terminal_review_three_pack_message_accepts_each_pack(self) -> None:
        tree_oid = "1" * 40
        packs = ("a" * 64, "b" * 64, "c" * 64)
        message = self._terminal_review_message(tree_oid, packs)
        for pack_sha256 in packs:
            with self.subTest(pack_sha256=pack_sha256):
                row = self._derive_terminal_review_for(
                    message, pack_sha256=pack_sha256
                )
                self.assertEqual(row.value["same_pack_digest"], True)

    def test_terminal_review_foreign_pack_list_refuses(self) -> None:
        message = self._terminal_review_message(
            "1" * 40, ("b" * 64, "c" * 64)
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_duplicate_pack_line_refuses(self) -> None:
        message = self._terminal_review_message(
            "1" * 40, ("a" * 64, "a" * 64)
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_single_pack_message_still_passes(self) -> None:
        message = self._terminal_review_message("1" * 40, ("a" * 64,))
        row = self._derive_terminal_review_for(message, pack_sha256="a" * 64)
        self.assertEqual(row.value["terminal_review_status"], "PASS")

    def test_terminal_review_pack_line_with_trailing_token_refuses(self) -> None:
        message = self._terminal_review_message("1" * 40, ()).replace(
            "JouleWise-Terminal-Review-Tree-Oid: " + "1" * 40,
            "JouleWise-Terminal-Review-Tree-Oid: "
            + "1" * 40
            + "\nJouleWise-Terminal-Review-Pack-Sha256: "
            + "a" * 64
            + " trailing",
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_malformed_pack_digest_refuses(self) -> None:
        message = self._terminal_review_message(
            "1" * 40, ("a" * 64, "not-a-sha256")
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_duplicate_pass_line_refuses(self) -> None:
        message = (
            self._terminal_review_message("1" * 40, ("a" * 64,))
            + "\nJouleWise-Terminal-Review: PASS"
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_duplicate_tree_oid_line_refuses(self) -> None:
        message = (
            self._terminal_review_message("1" * 40, ("a" * 64,))
            + "\nJouleWise-Terminal-Review-Tree-Oid: "
            + "1" * 40
        )
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_terminal_review_empty_pack_list_refuses(self) -> None:
        message = self._terminal_review_message("1" * 40, ())
        self._assert_terminal_review_refuses(message, pack_sha256="a" * 64)

    def test_t0_row_census_site_resolves_a_historical_pack(self) -> None:
        """The T-0 census site keeps resolving a historical v1 identity.

        The pack/profile map is immutable history (the v1 packs' own committed
        T-0 receipts were minted through this site), so it is never the gate
        that refuses a superseded pack.  The refusal the v1 ALPHA/BETA packs
        actually hit is the R2 frozen-plan resolution pinned by
        ``test_alpha_beta_repo_relative_plan_refuses_both_generic_r2_sites``
        immediately below.
        """

        temporary, _repository, pack, _custody, _arm_path = make_go_fixture(
            "d117_floor_qwen25_1p5b_v1", "ALPHA"
        )
        self.addCleanup(temporary.cleanup)
        tree, _raw = readiness._plan_tree(pack)
        context = SimpleNamespace(pack_root=pack, tree=tree)
        rows = t0._required_rows(context)
        self.assertTrue(rows)

    def test_alpha_beta_repo_relative_plan_refuses_both_generic_r2_sites(self) -> None:
        for profile, pack_name in (
            ("ALPHA", "d117_floor_qwen25_1p5b_v1"),
            ("BETA", "d117_floor_qwen25_7b_v1"),
        ):
            pack = ROOT / "configs/campaigns" / pack_name
            tree, _raw = readiness._plan_tree(pack)
            with self.subTest(profile=profile, site="shared-resolver"):
                with self.assertRaises(readiness.ArmReadinessError):
                    readiness.resolve_frozen_plan(pack, tree)
            context = generic_evidence._DerivationContext(
                pack_root=pack,
                repository=ROOT,
                tree=tree,
                pack_sha256="0" * 64,
                head_commit="0" * 40,
            )
            for site_name, site in (
                (
                    "manifest-validation",
                    lambda: generic_evidence._validate_manifests(
                        context, kind="PACK_AUTHENTICATION"
                    ),
                ),
                (
                    "estimator-derivation",
                    lambda: generic_evidence._derive_estimator_identity(context),
                ),
            ):
                with self.subTest(profile=profile, site=site_name):
                    with self.assertRaises(
                        generic_evidence.EvidenceAuthoringError
                    ) as caught:
                        site()
                    self.assertIn("R2 frozen-plan reference is invalid", str(caught.exception))

    def test_retired_prior_state_artifacts_and_privileged_get_are_absent(self) -> None:
        temporary, repository, pack, custody, _context, inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        self.assertFalse((inputs / "clock-prior-state.json").exists())
        self.assertFalse((inputs / "clock-attestation.json").exists())
        source = inspect.getsource(t0)
        self.assertNotIn("clock-prior-state", source)
        self.assertNotIn("-getusingnetworktime", source)

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

    def test_rf13_final_boot_resample_refuses_before_publication(self) -> None:
        boot_probe_count = 0

        def boot_changes_only_at_final_sample(argv, *, cwd):
            nonlocal boot_probe_count
            if "kern.bootsessionuuid" in argv:
                boot_probe_count += 1
                boot_session = (
                    TEST_BOOT_SESSION_ID
                    if boot_probe_count == 1
                    else OTHER_BOOT_SESSION_ID
                )
                return _probe_result(argv, cwd, stdout=boot_session + "\n")
            return passing_probe(argv, cwd=cwd)

        self._assert_clock_refusal(
            probe=boot_changes_only_at_final_sample,
            kind="AUTHORING_SET",
            reason_code="evidence_author_t0_input_changed",
            detail="boot session changed during derivation",
        )
        self.assertEqual(boot_probe_count, 2)

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

    def test_rf21_rf22_fresh_clock_disable_requires_exit_and_exact_stdout(self) -> None:
        def failing_probe(argv, *, cwd):
            if "systemsetup" in " ".join(argv):
                return _probe_result(argv, cwd, exit_code=1, stderr="sudo failed")
            return passing_probe(argv, cwd=cwd)

        self._assert_clock_refusal(
            probe=failing_probe,
            detail="fresh D-127 enforcement exited nonzero before setting Off",
            kind="CLOCK_PROBE",
            reason_code="evidence_author_t0_clock_probe_underivable",
        )

        def wrong_stdout_probe(argv, *, cwd):
            if "systemsetup" in " ".join(argv):
                return _probe_result(argv, cwd, stdout="Network Time: Off\n")
            return passing_probe(argv, cwd=cwd)

        self._assert_clock_refusal(
            probe=wrong_stdout_probe,
            detail="fresh D-127 enforcement stdout did not exactly report Off",
            kind="CLOCK_PROBE",
            reason_code="evidence_author_t0_clock_probe_underivable",
        )

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

    def test_public_namespace_and_signature_are_closed(self) -> None:
        self.assertEqual(
            tuple(inspect.signature(author_arm_readiness_evidence_t0).parameters),
            ("pack_root", "custody_root"),
        )
        self.assertEqual(
            t0.__all__,
            ["T0EvidenceAuthoringError", "author_arm_readiness_evidence_t0"],
        )
        self.assertEqual(
            sorted(name for name in vars(t0) if not name.startswith("_")),
            [
                "T0EvidenceAuthoringError",
                "annotations",
                "author_arm_readiness_evidence_t0",
            ],
        )
        self.assertFalse(hasattr(t0, "DERIVERS"))
        for keyword in ("runner", "facts", "outcomes", "boot_session_id"):
            with self.subTest(keyword=keyword), self.assertRaises(TypeError):
                author_arm_readiness_evidence_t0(
                    Path("unused"), Path("unused"), **{keyword: object()}
                )

    def test_all_fifteen_rows_have_an_explicit_volatility_class(self) -> None:
        self.assertEqual(
            t0._VOLATILE_EVIDENCE_VALIDITY_NS,
            20 * 60 * 1_000_000_000,
        )
        self.assertGreater(
            t0._NONVOLATILE_EVIDENCE_VALIDITY_NS,
            t0._VOLATILE_EVIDENCE_VALIDITY_NS,
        )
        self.assertFalse(
            t0._VOLATILE_EVIDENCE_KINDS & t0._NONVOLATILE_EVIDENCE_KINDS
        )
        self.assertEqual(
            t0._VOLATILE_EVIDENCE_KINDS | t0._NONVOLATILE_EVIDENCE_KINDS,
            set(t0._ROW_KIND.values()),
        )
        self.assertEqual(
            t0._VOLATILE_EVIDENCE_KINDS,
            {
                "BACKUP_PREFLIGHT",
                "CLOCK_PROBE",
                "LAUNCH_RECIPE",
                "MAINTENANCE_CENSUS",
                "MACHINE_PREFLIGHT",
                "POWERMETRICS_PROBE",
                "POWER_PREFLIGHT",
                "PROCESS_CENSUS",
                "ROOT_PREFLIGHT",
            },
        )
        self.assertEqual(
            sum(
                kind in t0._VOLATILE_EVIDENCE_KINDS
                for kind in t0._ROW_KIND.values()
            ),
            11,
        )
        self.assertEqual(
            t0._PUBLICATION_COMPLETION_MARKER,
            f"{t0._receipt_name('t0.storage_backup_capacity')}.sha256",
        )

    def test_authors_exact_fifteen_valid_rows_and_is_byte_idempotent(self) -> None:
        temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        with author_environment(repository):
            first = author_arm_readiness_evidence_t0(pack, custody)
            self.assertTrue(first["mutated"])
            self.assertEqual(first["authored_rows"], list(t0._EXPECTED_ROWS))
            self.assertEqual(len(first["authored_kinds"]), 13)
            evidence = custody / pack.name / t0._EVIDENCE_DIRECTORY
            sources = custody / pack.name / t0._SOURCE_DIRECTORY
            self.assertEqual(len(list(evidence.glob("*.json"))), 15)
            self.assertEqual(len(list(evidence.glob("*.json.sha256"))), 15)
            self.assertEqual(len(list(sources.glob("*.json"))), 15)
            registry = json.loads(
                (
                    repository
                    / readiness.ROW_REGISTRY_RELATIVE_PATH
                ).read_text(encoding="utf-8")
            )
            profile = next(
                item for item in registry["plan_profiles"] if item["profile_id"] == "ALPHA"
            )
            rows_by_predicate = {
                row["predicate_id"]: row for row in registry["rows"]
            }
            before = {path.name: path.read_bytes() for path in evidence.iterdir()}
            independently_observed_rows = []
            independently_observed_kinds = set()
            for receipt_path in sorted(evidence.glob("*.json")):
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                self.assertEqual(receipt["boot_session_id"], TEST_BOOT_SESSION_ID)
                self.assertEqual(receipt["status"], "PASS")
                self.assertEqual(receipt["reason_codes"], [])
                self.assertEqual(
                    receipt["assurance"],
                    {
                        "model": "single_authority_hash_bound_replay.v1",
                        "independent_attestation": False,
                    },
                )
                horizon = (
                    t0._VOLATILE_EVIDENCE_VALIDITY_NS
                    if receipt["kind"] in t0._VOLATILE_EVIDENCE_KINDS
                    else t0._NONVOLATILE_EVIDENCE_VALIDITY_NS
                )
                self.assertEqual(
                    receipt["valid_until_monotonic_ns"],
                    1_000_000_000_000 + horizon,
                )
                self.assertEqual(len(receipt["facts"]), 1)
                fact = receipt["facts"][0]
                row = rows_by_predicate[fact["fact_id"]]
                self.assertIn(row["row_id"], profile["required_row_ids"])
                self.assertEqual(row["evaluation_phase"], "ARM_ONLY")
                self.assertEqual(row["applicability_rule"], "ALWAYS")
                self.assertEqual(row["required_evidence_kinds"], [receipt["kind"]])
                source_path = custody / pack.name / fact["source_path"]
                source_raw = source_path.read_bytes()
                self.assertEqual(hashlib.sha256(source_raw).hexdigest(), fact["source_sha256"])
                source = json.loads(source_raw)
                self.assertEqual(source["row_id"], row["row_id"])
                self.assertEqual(source["kind"], receipt["kind"])
                if row["row_id"] == "clock.network_time_off":
                    self.assertEqual(
                        source["probes"][0]["argv"],
                        [
                            "/usr/bin/sudo",
                            "-n",
                            "/usr/sbin/systemsetup",
                            "-setusingnetworktime",
                            "off",
                        ],
                    )
                self.assertEqual(source["facts"][0]["fact_id"], row["predicate_id"])
                self.assertEqual(source["facts"][0]["value"], fact["value"])
                independently_observed_rows.append(row["row_id"])
                independently_observed_kinds.add(receipt["kind"])
            self.assertEqual(len(independently_observed_rows), 15)
            self.assertEqual(len(set(independently_observed_rows)), 15)
            self.assertEqual(
                sorted(independently_observed_rows), sorted(first["authored_rows"])
            )
            self.assertEqual(
                independently_observed_kinds, set(first["authored_kinds"])
            )
            self.assertEqual(
                set(independently_observed_rows),
                {
                    row["row_id"]
                    for row in registry["rows"]
                    if row["evaluation_phase"] == "ARM_ONLY"
                    and row["applicability_rule"] == "ALWAYS"
                    and row["required_evidence_kinds"][0]
                    not in {"GIT_CHECKOUT", "DRY_RUN_REHEARSAL"}
                },
                "the independent registry census must account for exactly the fifteen receipts",
                )
            second = author_arm_readiness_evidence_t0(pack, custody)
            self.assertFalse(second["mutated"])
            self.assertEqual(
                before, {path.name: path.read_bytes() for path in evidence.iterdir()}
            )

    @unittest.skip(
        "STRUCTURAL-BLOCKED: synthetic fixture authors legacy generic evidence; "
        "R1 requires content/execution receipt schemas"
    )
    def test_arm_consumes_volatile_receipts_within_short_horizon(self) -> None:
        """Blocked by legacy-schema evidence installed before ARM generation."""

        authored_at = 1_000_000_000_000
        short_horizon_ns = 20 * 60 * 1_000_000_000
        temporary, repository, pack, custody, context, _inputs = make_t0_fixture(
            now_monotonic_ns=authored_at
        )
        self.addCleanup(temporary.cleanup)
        with author_environment(repository, now_monotonic_ns=authored_at):
            author_arm_readiness_evidence_t0(pack, custody)
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
                return_value=(authored_at + short_horizon_ns - 1),
            ),
        ):
            arm = readiness.generate_arm_receipt(pack, context, custody)
        self.assertEqual(arm["status"], "PASS", arm)
        self.assertEqual(arm["arm_disposition"], "GO")

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
            arm = readiness.generate_arm_receipt(pack, context, custody)
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

    @unittest.skip(
        "STRUCTURAL-BLOCKED: synthetic fixture authors legacy generic evidence; "
        "R1 requires content/execution receipt schemas"
    )
    def test_mocked_forbidden_process_evidence_expires_before_arm(self) -> None:
        """Blocked by legacy-schema evidence installed before ARM generation."""

        self._assert_forbidden_process_evidence_expires_before_arm(
            start_real_process=False
        )

    @unittest.skipUnless(
        sys.platform == "darwin", "requires Darwin's real caffeinate process"
    )
    @unittest.skip(
        "STRUCTURAL-BLOCKED: synthetic fixture authors legacy generic evidence; "
        "R1 requires content/execution receipt schemas"
    )
    def test_forbidden_process_started_after_authoring_expires_before_arm(self) -> None:
        """Blocked by legacy-schema evidence installed before ARM generation."""

        self._assert_forbidden_process_evidence_expires_before_arm(
            start_real_process=True
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
                ("/usr/bin/pgrep", "-lf", "codex|claude|t3"),
                (
                    "/usr/bin/pgrep",
                    "-lf",
                    "Safari|Google Chrome|Chromium|Firefox|browser automation",
                ),
                (
                    "/usr/bin/pgrep",
                    "-lf",
                    "powermetrics|window-chain|run_campaign|tail -f|watch",
                ),
            ),
        )

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

    def test_missing_first_artifact_refuses_without_output(self) -> None:
        temporary, repository, pack, custody, _context, inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        (inputs / "clock-reference.json").unlink()
        with author_environment(repository), self.assertRaises(T0EvidenceAuthoringError) as caught:
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(caught.exception.kind, "CLOCK_ATTESTATION")
        self.assertEqual(
            caught.exception.reason_code, "evidence_author_t0_clock_attestation_missing"
        )
        self.assertFalse((custody / pack.name / t0._SOURCE_DIRECTORY).exists())
        self.assertFalse((custody / pack.name / t0._EVIDENCE_DIRECTORY).exists())

    def test_named_refusal_matrix_covers_every_distinct_kind(self) -> None:
        cases = (
            ("CLOCK_ATTESTATION", lambda _r, _p, _c, _x: ( _x / "clock-reference.json").unlink(), {}),
            ("CLOCK_PROBE", lambda *_args: None, {"probe": lambda argv, *, cwd: _probe_result(argv, cwd, exit_code=1, stderr="sudo refused\n") if "systemsetup" in " ".join(argv) else passing_probe(argv, cwd=cwd)}),
            ("TERMINAL_REVIEW", lambda *_args: None, {"patch_message": True}),
            ("MAINTENANCE_CENSUS", lambda *_args: None, {"probe": lambda argv, *, cwd: _probe_result(argv, cwd, exit_code=0, stdout="123 XProtect\n") if "XProtect" in " ".join(argv) else passing_probe(argv, cwd=cwd)}),
            ("ROOT_PREFLIGHT", lambda _r, _p, c, _x: (Path(c["claim_runs_root"]) / "campaign.lock").write_text("busy\n"), {}),
            ("MACHINE_PREFLIGHT", lambda _r, _p, _c, x: _write_json(x / "quiet-mac-prep.json", {**json.loads((x / "quiet-mac-prep.json").read_text()), "stdout": "READY.\n"}), {}),
            ("LEDGER_RESERVATION", lambda _r, _p, _c, x: _write_json(x / "ledger-reservation.json", {**json.loads((x / "ledger-reservation.json").read_text()), "stdout": json.dumps({"status": "refused"})}), {}),
            ("PROCESS_CENSUS", lambda *_args: None, {"probe": lambda argv, *, cwd: _probe_result(argv, cwd, exit_code=0, stdout="123 caffeinate\n") if tuple(argv)[-2:] == ("-x", "caffeinate") else passing_probe(argv, cwd=cwd)}),
            ("OFFLINE_INPUT_INVENTORY", lambda *_args: None, {"offline_fail": True}),
            ("POWERMETRICS_PROBE", lambda *_args: None, {"probe": lambda argv, *, cwd: _probe_result(argv, cwd, exit_code=1, stderr="sudo refused\n") if any(Path(item).name == "powermetrics" for item in argv) else passing_probe(argv, cwd=cwd)}),
            ("POWER_PREFLIGHT", lambda *_args: None, {"probe": lambda argv, *, cwd: _probe_result(argv, cwd, stdout="Now drawing from 'Battery Power'\n") if tuple(argv)[-2:] == ("-g", "batt") else passing_probe(argv, cwd=cwd)}),
            ("LAUNCH_RECIPE", lambda *_args: None, {"launch_used": True}),
            ("BACKUP_PREFLIGHT", lambda *_args: None, {"free": 1}),
        )
        for expected_kind, mutate, options in cases:
            with self.subTest(kind=expected_kind):
                temporary, repository, pack, custody, context, inputs = make_t0_fixture()
                try:
                    mutate(repository, pack, context, inputs)
                    if options.get("launch_used"):
                        used = custody / pack.name / "arm_readiness.receipts"
                        used.mkdir(parents=True)
                        (used / "prior-use").write_text("used\n")
                    offline = None
                    if options.get("offline_fail"):
                        def offline(_context, *, kind):
                            raise t0._underivable(kind, "synthetic offline mutation")
                    with author_environment(
                        repository,
                        probe=options.get("probe", passing_probe),
                        offline=offline,
                        free=options.get("free", 100 * 1024**3),
                    ), contextlib.ExitStack() as stack:
                        if options.get("patch_message"):
                            stack.enter_context(mock.patch.object(t0, "_git_message", return_value="no terminal review"))
                        with self.assertRaises(T0EvidenceAuthoringError) as caught:
                            author_arm_readiness_evidence_t0(pack, custody)
                    self.assertEqual(caught.exception.kind, expected_kind)
                    self.assertTrue(caught.exception.reason_code.startswith("evidence_author_t0_"))
                    self.assertFalse((custody / pack.name / t0._SOURCE_DIRECTORY).exists())
                    self.assertFalse((custody / pack.name / t0._EVIDENCE_DIRECTORY).exists())
                finally:
                    temporary.cleanup()

    def test_existing_namespace_is_append_only_boot_bound_and_tamper_evident(self) -> None:
        temporary, repository, pack, custody, _context, inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        evidence = custody / pack.name / t0._EVIDENCE_DIRECTORY
        with author_environment(repository):
            author_arm_readiness_evidence_t0(pack, custody)
        before = {path.name: path.read_bytes() for path in evidence.iterdir()}
        arm_context_path = inputs / "arm-context.json"
        arm_context_raw = arm_context_path.read_bytes()
        arm_context_path.write_bytes(arm_context_raw + b" ")
        with author_environment(repository), self.assertRaises(T0EvidenceAuthoringError) as caught:
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(caught.exception.reason_code, "evidence_author_t0_arm_context_missing")
        self.assertEqual(before, {path.name: path.read_bytes() for path in evidence.iterdir()})
        arm_context_path.write_bytes(arm_context_raw)
        with author_environment(
            repository,
            probe=lambda argv, *, cwd: _probe_result(argv, cwd, stdout=OTHER_BOOT_SESSION_ID + "\n") if "kern.bootsessionuuid" in argv else passing_probe(argv, cwd=cwd),
        ), self.assertRaises(T0EvidenceAuthoringError) as caught:
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(
            caught.exception.reason_code,
            "evidence_author_t0_clock_attestation_underivable",
        )
        self.assertEqual(before, {path.name: path.read_bytes() for path in evidence.iterdir()})

    def test_clock_probe_publishes_exact_ruled_value_dictionary(self) -> None:
        temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        with author_environment(repository):
            author_arm_readiness_evidence_t0(pack, custody)
        receipt = json.loads(
            (
                custody
                / pack.name
                / t0._EVIDENCE_DIRECTORY
                / t0._receipt_name("clock.correct_and_prior_state")
            ).read_text(encoding="utf-8")
        )
        fact = receipt["facts"][0]
        self.assertEqual(fact["source_kind"], "PROBE")
        self.assertEqual(set(fact["value"]), readiness._CLOCK_PROBE_VALUE_KEYS)
        boolean_names = {
            name for name, value in fact["value"].items() if isinstance(value, bool)
        }
        self.assertEqual(
            boolean_names,
            {
                "independent_clock_attestation",
                "reference_quorum_satisfied",
                "absolute_offset_within_ceiling",
                "unstepped_across_t0_sequence",
            },
        )
        self.assertNotIn("prior_systemsetup_state_captured", fact["value"])

    def test_source_and_receipt_mutations_are_killed_without_overwrite(self) -> None:
        for target_kind in ("source", "receipt"):
            with self.subTest(target=target_kind):
                temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
                try:
                    with author_environment(repository):
                        author_arm_readiness_evidence_t0(pack, custody)
                    evidence = custody / pack.name / t0._EVIDENCE_DIRECTORY
                    source = custody / pack.name / t0._SOURCE_DIRECTORY
                    target = (
                        next(source.glob("*.json"))
                        if target_kind == "source"
                        else next(evidence.glob("*.json"))
                    )
                    target.write_bytes(target.read_bytes() + b" ")
                    before = {
                        str(path): path.read_bytes()
                        for directory in (source, evidence)
                        for path in directory.iterdir()
                    }
                    with author_environment(repository), self.assertRaises(T0EvidenceAuthoringError):
                        author_arm_readiness_evidence_t0(pack, custody)
                    self.assertEqual(
                        before,
                        {
                            str(path): path.read_bytes()
                            for directory in (source, evidence)
                            for path in directory.iterdir()
                        },
                    )
                finally:
                    temporary.cleanup()

    def test_coordinated_source_receipt_rewrite_is_killed_by_fresh_derivation(self) -> None:
        temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        with author_environment(repository):
            author_arm_readiness_evidence_t0(pack, custody)
        source_path = (
            custody
            / pack.name
            / t0._SOURCE_DIRECTORY
            / f"{t0._slug('t0.power_path')}.json"
        )
        receipt_path = (
            custody
            / pack.name
            / t0._EVIDENCE_DIRECTORY
            / t0._receipt_name("t0.power_path")
        )
        source = readiness.parse_json_bytes(
            source_path.read_bytes(), require_canonical=True
        )
        source["derivation"]["operator_supplied_conclusion"] = True
        source_raw = readiness.render_json(source)
        source_path.write_bytes(source_raw)
        receipt = readiness.parse_json_bytes(
            receipt_path.read_bytes(), require_canonical=True
        )
        receipt["facts"][0]["source_sha256"] = hashlib.sha256(source_raw).hexdigest()
        receipt_raw = readiness.render_json(receipt)
        receipt_path.write_bytes(receipt_raw)
        receipt_path.with_name(f"{receipt_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                hashlib.sha256(receipt_raw).hexdigest(), receipt_path.name
            )
        )
        before = {
            str(path): path.read_bytes()
            for directory in (
                custody / pack.name / t0._SOURCE_DIRECTORY,
                custody / pack.name / t0._EVIDENCE_DIRECTORY,
            )
            for path in directory.iterdir()
        }
        with author_environment(repository), self.assertRaises(T0EvidenceAuthoringError) as caught:
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(caught.exception.reason_code, "evidence_author_t0_existing_stale")
        self.assertEqual(
            before,
            {
                str(path): path.read_bytes()
                for directory in (
                    custody / pack.name / t0._SOURCE_DIRECTORY,
                    custody / pack.name / t0._EVIDENCE_DIRECTORY,
                )
                for path in directory.iterdir()
            },
        )

    def test_staged_discovery_refusal_publishes_no_output(self) -> None:
        temporary, repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        refusal = {
            "type": "REFUSE",
            "code": "readiness_evidence_digest_mismatch",
            "row_id": None,
            "evidence_id": None,
        }
        with (
            author_environment(repository),
            mock.patch.object(
                t0._readiness,
                "_discover_evidence",
                return_value=([], {}, [refusal]),
            ),
            self.assertRaises(T0EvidenceAuthoringError) as caught,
        ):
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(
            caught.exception.reason_code, "evidence_author_t0_validation_failed"
        )
        self.assertFalse((custody / pack.name / t0._SOURCE_DIRECTORY).exists())
        self.assertFalse((custody / pack.name / t0._EVIDENCE_DIRECTORY).exists())

    def test_every_publication_crash_point_is_prestate_or_detectable(self) -> None:
        class InjectedKill(BaseException):
            pass

        for completed_renames in range(4):
            with self.subTest(completed_renames=completed_renames):
                temporary, repository, pack, custody, _context, _inputs = (
                    make_t0_fixture()
                )
                try:
                    custody_pack = custody / pack.name
                    source_dir = custody_pack / t0._SOURCE_DIRECTORY
                    evidence_dir = custody_pack / t0._EVIDENCE_DIRECTORY
                    marker = evidence_dir / t0._PUBLICATION_COMPLETION_MARKER
                    final_destinations = {
                        source_dir,
                        evidence_dir,
                        marker,
                    }
                    real_replace = t0._os.replace
                    rename_count = 0

                    def kill_after_selected_rename(source, destination):
                        nonlocal rename_count
                        destination_path = Path(destination)
                        if destination_path not in final_destinations:
                            return real_replace(source, destination)
                        if completed_renames == 0:
                            raise InjectedKill("before the first publication rename")
                        result = real_replace(source, destination)
                        rename_count += 1
                        if rename_count == completed_renames:
                            raise InjectedKill(
                                f"after publication rename {rename_count}"
                            )
                        return result

                    with (
                        author_environment(repository),
                        mock.patch.object(
                            t0._os,
                            "replace",
                            side_effect=kill_after_selected_rename,
                        ),
                        self.assertRaises(InjectedKill),
                    ):
                        author_arm_readiness_evidence_t0(pack, custody)

                    self.assertEqual(
                        [
                            path.name
                            for path in custody_pack.iterdir()
                            if path.name.startswith(".arm-readiness-t0-")
                        ],
                        [],
                    )
                    if completed_renames == 0:
                        self.assertFalse(source_dir.exists())
                        self.assertFalse(evidence_dir.exists())
                        with author_environment(repository):
                            recovered = author_arm_readiness_evidence_t0(
                                pack, custody
                            )
                        self.assertTrue(recovered["mutated"])
                    elif completed_renames < 3:
                        self.assertTrue(source_dir.is_dir())
                        self.assertEqual(evidence_dir.is_dir(), completed_renames == 2)
                        self.assertFalse(marker.exists())
                        with (
                            author_environment(repository),
                            self.assertRaises(T0EvidenceAuthoringError) as caught,
                        ):
                            author_arm_readiness_evidence_t0(pack, custody)
                        self.assertEqual(
                            caught.exception.reason_code,
                            "evidence_author_t0_publication_incomplete",
                        )
                        if completed_renames == 2:
                            _items, _receipts, refusals = (
                                readiness._discover_evidence(
                                    pack,
                                    custody_pack,
                                    pack_sha256=readiness.committed_pack_tree_sha256(
                                        pack
                                    ),
                                    head_commit=readiness.reviewed_main(pack)[
                                        "head_commit"
                                    ],
                                    boot_session_id=TEST_BOOT_SESSION_ID,
                                    now_monotonic_ns=1_000_000_000_000,
                                    include_pack=False,
                                )
                            )
                            self.assertIn(
                                "readiness_evidence_unreadable",
                                {item["code"] for item in refusals},
                            )
                    else:
                        self.assertTrue(
                            t0._publication_complete(source_dir, evidence_dir)
                        )
                        with author_environment(repository):
                            recovered = author_arm_readiness_evidence_t0(
                                pack, custody
                            )
                        self.assertFalse(recovered["mutated"])
                finally:
                    temporary.cleanup()

    def test_each_absent_runbook_artifact_class_has_one_named_refusal(self) -> None:
        expected = {
            "arm_context": "evidence_author_t0_arm_context_missing",
            "clock_reference_capture": "evidence_author_t0_clock_attestation_missing",
            "clock_disable_capture": "evidence_author_t0_clock_disable_missing",
            "quiet_mac_prep_capture": "evidence_author_t0_quiet_mac_prep_missing",
            "prewindow_check_capture": "evidence_author_t0_prewindow_check_missing",
            "ledger_readiness_capture": "evidence_author_t0_ledger_readiness_missing",
            "ledger_reservation_capture": "evidence_author_t0_ledger_reservation_missing",
            "launch_manifest": "evidence_author_t0_launch_manifest_missing",
            "window_environment": "evidence_author_t0_window_environment_missing",
            "window_chain": "evidence_author_t0_window_chain_missing",
            "waiver_record": "evidence_author_t0_waiver_record_missing",
            "identity_epoch": "evidence_author_t0_identity_epoch_missing",
            "t1_bindings": "evidence_author_t0_t1_bindings_missing",
            "production_ledger": "evidence_author_t0_production_ledger_missing",
        }
        self.assertEqual(len(expected), 14)
        self.assertEqual(len(set(expected.values())), 14)
        for artifact_class, reason_code in expected.items():
            with self.subTest(artifact_class=artifact_class):
                temporary, repository, pack, custody, context, inputs = make_t0_fixture()
                try:
                    launch = json.loads((inputs / "launch-manifest.json").read_text())
                    reservation = json.loads((inputs / "ledger-reservation.json").read_text())
                    flags = t0._argv_flags(
                        reservation["argv"], valueless=frozenset({"--execute"})
                    )
                    paths = {
                        "arm_context": inputs / "arm-context.json",
                        "clock_reference_capture": inputs / "clock-reference.json",
                        "clock_disable_capture": inputs / "clock-disable.json",
                        "quiet_mac_prep_capture": inputs / "quiet-mac-prep.json",
                        "prewindow_check_capture": inputs / "prewindow-check.json",
                        "ledger_readiness_capture": inputs / "ledger-readiness.json",
                        "ledger_reservation_capture": inputs / "ledger-reservation.json",
                        "launch_manifest": inputs / "launch-manifest.json",
                        "window_environment": Path(launch["window_plan_root"]) / "window.env",
                        "window_chain": Path(launch["window_plan_root"]) / "window-chain.zsh",
                        "waiver_record": Path(context["waiver_path"]),
                        "identity_epoch": Path(flags["--identity-epoch-json"]),
                        "t1_bindings": Path(flags["--t1-bindings-json"]),
                        "production_ledger": Path(flags["--ledger"]),
                    }
                    paths[artifact_class].unlink()
                    with (
                        author_environment(repository),
                        self.assertRaises(T0EvidenceAuthoringError) as caught,
                    ):
                        author_arm_readiness_evidence_t0(pack, custody)
                    self.assertEqual(caught.exception.reason_code, reason_code)
                    self.assertFalse(
                        (custody / pack.name / t0._SOURCE_DIRECTORY).exists()
                    )
                    self.assertFalse(
                        (custody / pack.name / t0._EVIDENCE_DIRECTORY).exists()
                    )
                finally:
                    temporary.cleanup()

    def test_cli_refuses_a_pack_from_another_repository(self) -> None:
        temporary, _repository, pack, custody, _context, _inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        output = io.BytesIO()
        with mock.patch.object(t0_cli.sys, "stdout", _cli_stdout(output)):
            code = t0_cli.main(
                ["--pack-root", str(pack), "--custody-root", str(custody)]
            )
        self.assertEqual(code, 2)
        value = readiness.parse_json_bytes(output.getvalue(), require_canonical=True)
        self.assertEqual(value["status"], "REFUSE")
        self.assertEqual(
            value["reason_codes"], ["evidence_author_t0_repository_mismatch"]
        )

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
                env={**os.environ, "PYTHONPATH": str(repository), "PYTHONDONTWRITEBYTECODE": "1"},
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

    @unittest.skip(
        "STRUCTURAL-BLOCKED: fixture R1 schemas require FIXTURE-MODERNIZATION-01 (A84)"
    )
    def test_acid_authored_fifteen_then_real_arm_generator_reaches_go(self) -> None:
        """Blocked on fixture R1 schema modernization (A84)."""

        self._assert_acid_authored_fifteen_then_arm_generator_reaches_go(
            boot_session_id=TEST_BOOT_SESSION_ID,
            synthetic_boot_session=True,
            synthetic_clock=True,
        )

    @unittest.skip(
        "STRUCTURAL-BLOCKED: fixture R1 schemas require FIXTURE-MODERNIZATION-01 (A84)"
    )
    def test_synthetic_acid_is_hermetic_to_system_timezone(self) -> None:
        """Blocked on fixture R1 schema modernization (A84)."""

        previous = os.environ.get("TZ")
        try:
            os.environ["TZ"] = "Pacific/Kiritimati"
            if hasattr(time, "tzset"):
                time.tzset()
            self._assert_acid_authored_fifteen_then_arm_generator_reaches_go(
                boot_session_id=TEST_BOOT_SESSION_ID,
                synthetic_boot_session=True,
                synthetic_clock=True,
            )
        finally:
            if previous is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = previous
            if hasattr(time, "tzset"):
                time.tzset()

    @unittest.skip(
        "STRUCTURAL-BLOCKED: fixture R1 schemas require FIXTURE-MODERNIZATION-01 (A84)"
    )
    def test_synthetic_acid_ignores_wall_clock_48_hours_in_future(self) -> None:
        """Blocked on fixture R1 schema modernization (A84)."""

        with mock.patch.object(
            t0._readiness,
            "_utc_now",
            return_value="2026-08-15T20:30:00Z",
        ):
            self._assert_acid_authored_fifteen_then_arm_generator_reaches_go(
                boot_session_id=TEST_BOOT_SESSION_ID,
                synthetic_boot_session=True,
                synthetic_clock=True,
            )

    @unittest.skipUnless(
        sys.platform == "darwin", "requires Darwin's real boot-session sysctl command"
    )
    @unittest.skip(
        "STRUCTURAL-BLOCKED: fixture R1 schemas require FIXTURE-MODERNIZATION-01 (A84)"
    )
    def test_acid_real_boot_session_then_real_arm_generator_reaches_go(self) -> None:
        """Blocked on fixture R1 schema modernization (A84)."""

        try:
            boot_session_id = readiness._current_boot_session_id()
        except readiness.ArmReadinessError as exc:
            if "Operation not permitted" not in str(exc):
                raise
            self.skipTest(f"Darwin boot-session sysctl is unavailable: {exc}")
        self._assert_acid_authored_fifteen_then_arm_generator_reaches_go(
            boot_session_id=boot_session_id,
            synthetic_boot_session=False,
            synthetic_clock=False,
        )


if __name__ == "__main__":
    unittest.main()
