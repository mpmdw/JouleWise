from __future__ import annotations

import contextlib
import hashlib
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
from types import SimpleNamespace
from unittest import mock

import joulewise.arm_readiness as readiness
import joulewise.arm_readiness_evidence as generic_evidence
import joulewise.arm_readiness_evidence_t0 as t0
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


def make_t0_fixture(
    *,
    boot_session_id: str = TEST_BOOT_SESSION_ID,
    now_monotonic_ns: int = SYNTHETIC_MONOTONIC_NS,
    real_identity: bool = False,
    synthetic_boot_session: bool = True,
    synthetic_clock: bool = True,
):
    temporary, repository, pack, custody, _arm_path = make_go_fixture()
    repository = repository.resolve()
    pack = pack.resolve()
    custody = custody.resolve()
    clear_initial_arm(custody, pack.name)
    if real_identity:
        shutil.copytree(ROOT / "joulewise", repository / "joulewise", dirs_exist_ok=True)
    for relative in (
        "joulewise/arm_readiness_evidence_t0.py",
        "joulewise/identity_pins.py",
        "scripts/author_arm_evidence_t0.py",
        "scripts/capture_t0_step.py",
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
    launch_argv = [
        "/usr/bin/caffeinate",
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
    _write_json(
        input_root / "clock-attestation.json",
        {
            "schema_version": t0._ATTESTATION_SCHEMA,
            "attestation_id": "synthetic-clock-1",
            "observer": "synthetic-independent-observer",
            "reference_source": "synthetic-reference-clock",
            "system_time_utc": "2026-08-13T20:00:00Z",
            "reference_time_utc": "2026-08-13T20:00:01Z",
            "observed_monotonic_ns": time_origin + 10,
            "boot_session_id": boot_session_id,
        },
    )

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
        "clock-prior-state.json": _capture(
            "clock-prior-state",
            ["operator-interactive", "network-time-prior-state"],
            repository,
            time_origin + 20,
            time_origin + 30,
            stdout="Network Time: On\n",
            boot_session_id=boot_session_id,
        ),
        "clock-disable.json": _capture(
            "clock-disable",
            ["/usr/bin/sudo", "/usr/sbin/systemsetup", "-setusingnetworktime", "off"],
            repository,
            time_origin + 40,
            time_origin + 50,
            boot_session_id=boot_session_id,
        ),
        "quiet-mac-prep.json": _capture(
            "quiet-mac-prep",
            ["/bin/bash", str(repository / "scripts/quiet_mac_prep.sh")],
            repository,
            time_origin + 60,
            time_origin + 70,
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
            time_origin + 100,
            time_origin + 100 + t0._MIN_IDLE_NS,
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
            time_origin + 200 + t0._MIN_IDLE_NS,
            time_origin + 210 + t0._MIN_IDLE_NS,
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
            time_origin + 220 + t0._MIN_IDLE_NS,
            time_origin + 230 + t0._MIN_IDLE_NS,
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
    if "systemsetup" in joined:
        return _probe_result(command, cwd, stdout="Network Time: Off\n")
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
                mock.patch.dict(
                    sys.modules, {"mlx_lm": _load_synthetic_mlx(repository)}
                )
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

    def test_superseded_pack_refuses_the_t0_row_census_site(self) -> None:
        """D-138: the T-0 author's registry site refuses a v1 campaign pack."""

        temporary, _repository, pack, _custody, _arm_path = make_go_fixture(
            "d117_floor_qwen25_1p5b_v1", "ALPHA"
        )
        self.addCleanup(temporary.cleanup)
        tree, _raw = readiness._plan_tree(pack)
        context = SimpleNamespace(pack_root=pack, tree=tree)
        with self.assertRaises(readiness.ArmReadinessError) as caught:
            t0._required_rows(context)
        self.assertEqual(
            caught.exception.reason_code, "readiness_row_registry_mismatch"
        )

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

    def test_legacy_privileged_prior_state_capture_is_refused(self) -> None:
        temporary, repository, pack, custody, _context, inputs = make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        prior_path = inputs / "clock-prior-state.json"
        prior = json.loads(prior_path.read_text(encoding="utf-8"))
        prior["argv"] = [
            "/usr/bin/sudo",
            "/usr/sbin/systemsetup",
            "-getusingnetworktime",
        ]
        _write_json(prior_path, prior)
        with (
            author_environment(repository),
            self.assertRaises(T0EvidenceAuthoringError) as caught,
        ):
            author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(caught.exception.kind, "CLOCK_ATTESTATION")
        self.assertIn("not Ed's interactive action", str(caught.exception))

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
                    / "configs/arm_readiness/d117_row_registry_v1.json"
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

    def test_arm_consumes_volatile_receipts_within_short_horizon(self) -> None:
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

    def test_mocked_forbidden_process_evidence_expires_before_arm(self) -> None:
        self._assert_forbidden_process_evidence_expires_before_arm(
            start_real_process=False
        )

    @unittest.skipUnless(
        sys.platform == "darwin", "requires Darwin's real caffeinate process"
    )
    def test_forbidden_process_started_after_authoring_expires_before_arm(self) -> None:
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
        (inputs / "clock-attestation.json").unlink()
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
            ("CLOCK_ATTESTATION", lambda _r, _p, _c, _x: ( _x / "clock-attestation.json").unlink(), {}),
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
            "clock_attestation": "evidence_author_t0_clock_attestation_missing",
            "clock_prior_state_capture": "evidence_author_t0_clock_prior_state_missing",
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
        self.assertEqual(len(expected), 15)
        self.assertEqual(len(set(expected.values())), 15)
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
                        "clock_attestation": inputs / "clock-attestation.json",
                        "clock_prior_state_capture": inputs / "clock-prior-state.json",
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

    def test_acid_authored_fifteen_then_real_arm_generator_reaches_go(self) -> None:
        self._assert_acid_authored_fifteen_then_arm_generator_reaches_go(
            boot_session_id=TEST_BOOT_SESSION_ID,
            synthetic_boot_session=True,
            synthetic_clock=True,
        )

    def test_synthetic_acid_is_hermetic_to_system_timezone(self) -> None:
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

    def test_synthetic_acid_ignores_wall_clock_48_hours_in_future(self) -> None:
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
    def test_acid_real_boot_session_then_real_arm_generator_reaches_go(self) -> None:
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
