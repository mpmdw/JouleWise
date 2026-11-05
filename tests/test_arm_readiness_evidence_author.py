from __future__ import annotations
import subprocess
from tests import receipt_factory

import copy
import hashlib
import io
import inspect
import json
import os
import shlex
import shutil
import signal
import time
import unittest
from pathlib import Path
from unittest import mock

import joulewise.receipt_readers as readiness
import joulewise.evidence_replay as evidence
from tests.evidence_factory import author_arm_readiness_evidence
from joulewise.evidence_replay import (
    EvidenceAuthoringError,
)
from joulewise.receipt_oracle import derive_bracket_session_receipt_oracle
pass
pass
from tests.test_arm_readiness_lifecycle import (
    commit_u11_projection,
    git,
    make_go_fixture,
    predecessor_pack_root,
)
from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID


ROOT = Path(__file__).resolve().parents[1]
OTHER_BOOT_SESSION_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"


def _cli_stdout(buffer: io.BytesIO) -> mock.Mock:
    """Stand-in for sys.stdout that survives argparse's 3.14 colorize probe."""
    return mock.Mock(
        buffer=buffer,
        fileno=mock.Mock(side_effect=io.UnsupportedOperation("fileno")),
        isatty=mock.Mock(return_value=False),
    )


def passing_suites(
    repository: Path, test_ids: list[str] | tuple[str, ...]
) -> evidence._SuiteResult:
    executed = []
    loaded_ids = []
    for test_id in test_ids:
        module = ".".join(test_id.split(".")[:2])
        relative = f"{module.replace('.', '/')}.py"
        raw = (repository / relative).read_bytes()
        executed.append(
            evidence._ExecutedFile(module, relative, hashlib.sha256(raw).hexdigest())
        )
        loaded_ids.append(test_id)
    return evidence._SuiteResult(
        tuple(loaded_ids),
        len(test_ids),
        0,
        0,
        0,
        0,
        0,
        tuple(executed),
    )


def _copy_primary(repository: Path, relative: str) -> None:
    target = repository / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    body = _historical_fixture_source(relative)
    target.write_bytes(body)


def _identity_unit(arm: str, model: str) -> dict:
    return {
        "declared_identity": {
            "hardware_target": "synthetic-mac",
            "model_name": model,
            "model_revision": f"{model}-revision",
            "model_source": f"/synthetic/{model}",
            "quantization": {"bits": 4, "group_size": None, "name": "int4"},
            "runtime_backend": "mlx",
            "telemetry_backend": "powermetrics",
            "workload_profile": {
                "dataset_ref": None,
                "name": "df_ph_decode",
                "output_tokens": 8,
                "prompt_text": None,
                "prompt_tokens": 8,
                "repetitions": 1,
                "warmup_runs": 1,
            },
        },
        "consumer_bindings": [
            {"arm": arm, "family": f"synthetic-{arm}", "measurement_arm": "decode"}
        ],
    }


def make_author_fixture(pack_name: str = "d117_floor_qwen25_1p5b_v1"):
    """Build an ALPHA authoring pack plus its two family siblings.

    PACK_FAMILY derivation reads the family named by
    ``evidence._PACKS_BY_PROFILE``, which is the IMMUTABLE HISTORICAL family, so
    the default fixture is that family's generation-1 ALPHA member and the
    siblings match its generation.  A caller may ask for a later generation to
    exercise successor-chain behaviour; it must then supply the family route for
    that generation (today: by patching ``_PACKS_BY_PROFILE``, which stands in
    for the registry-driven successor family route that does not exist yet).
    """

    generation_suffix = pack_name[pack_name.rindex("_v") :]
    temporary, repository, pack, custody, arm_path = make_go_fixture(
        pack_name, "ALPHA", project=False
    )

    for relative in (
        # Every registered issued generation is available to the fixture:
        # historical `_v1`/`_v2` packs pin n19/n19_r2, and successor packs may
        # name any retained n17 r3-r7/P8 issuance.
        "configs/calibration/calibration_acceptance_d079_v2.json",
        "configs/calibration/calibration_acceptance_d079_v2_r2.json",
        "configs/calibration/calibration_acceptance_d079_v2_n17_r3.json",
        "configs/calibration/calibration_acceptance_d079_v2_n17_r4.json",
        "configs/calibration/calibration_acceptance_d079_v2_n17_r5.json",
        "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json",
        "configs/calibration/calibration_acceptance_d079_v2_n17_r7.json",
        "configs/calibration/calibration_acceptance_d079_v2_n17_r8.json",
        "configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json",
        "configs/calibration/observation_dispositions.json",
        "docs/decision_log.md",
        "docs/phase_2/window_runbook.md",
        "joulewise/analysis_manifest_v3.py",
        "joulewise/arm_readiness.py",
        "joulewise/calibration_bracketing.py",
        "joulewise/calibration_ledger.py",
        "joulewise/detection_floor.py",
        "joulewise/floor_extraction.py",
        "joulewise/floor_mint_estimator.py",
        "joulewise/identity_pins.py",
        "joulewise/receipt_oracle.py",
        "scripts/floor_mint_pinsets/schema_v2.json",
        "scripts/mint_floor_artifact_generalized.py",
        # Revision 6 acceptance validation imports the within-window derivation.
        "scripts/issue_calibration_acceptance_generation.py",
        "scripts/recover_calibration_ledger.py",
        "tests/test_calibration_ledger.py",
        # RECOVERY_LEDGER_TEST runs `tests.test_calibration_ledger` as a focused
        # suite INSIDE this minimal repository, so every file that suite reads
        # must exist here too.  `DerivationSessionSlotTests.PRODUCTION_LEDGER`
        # reads the committed 76-row production ledger prefix by a path relative
        # to the test module, which resolves into this fixture repository.
        "tests/fixtures/d117_v2_production/issued/calibration_observation_ledger.jsonl",
        "tests/test_calibration_bracketing.py",
        "tests/test_calibration_live_three_window.py",
        "tests/receipt_corpus.py",
        "tests/test_arm_readiness_dry_run.py",
        "tests/test_arm_readiness_lifecycle.py",
        "tests/test_arm_readiness_schemas.py",
        "tests/test_arm_readiness_integration.py",
        "tests/git_fixture.py",
        "tests/test_mint_floor_artifact.py",
        "tests/test_mint_floor_artifact_generalized.py",
    ):
        _copy_primary(repository, relative)
    for relative in evidence._AUTHORING_ARTIFACTS:
        _copy_primary(repository, relative)
    for source in (ROOT / "joulewise").rglob("*.py"):
        _copy_primary(repository, source.relative_to(ROOT).as_posix())
    for source in (ROOT / "scripts").rglob("*.py"):
        _copy_primary(repository, source.relative_to(ROOT).as_posix())
    fixture = ROOT / "tests/fixtures/calibration_live_three_window/scenario.json"
    fixture_target = repository / fixture.relative_to(ROOT)
    fixture_target.parent.mkdir(parents=True, exist_ok=True)
    fixture_target.write_bytes(fixture.read_bytes())
    seven_b = ROOT / "configs/campaigns/qwen25_7b_decode_floor_v1"
    shutil.copytree(
        seven_b,
        repository / seven_b.relative_to(ROOT),
        dirs_exist_ok=True,
    )

    plan_path = pack / "calibration_plan.json"
    plan_raw = readiness.render_json(
        {"plan_id": "plan-test", "analysis": {"estimator": "d054_false_effect_guard.v1"}}
    )
    plan_path.write_bytes(plan_raw)
    config_raw = readiness.render_json({"run_id": "synthetic-member-1"})
    (pack / "config.json").write_bytes(config_raw)
    manifest = {
        "schema_version": "joulewise.order_manifest.v1",
        "manifest_id": "synthetic-order-v1",
        "plan_id": "plan-test",
        "calibration_plan_sha256": hashlib.sha256(plan_raw).hexdigest(),
        "planned_n_bundles": 1,
        "executed_order": [
            {
                "index": 1,
                "config": "config.json",
                "config_sha256": hashlib.sha256(config_raw).hexdigest(),
                "run_id": "synthetic-member-1",
            }
        ],
    }
    (pack / "order_manifest.json").write_bytes(readiness.render_json(manifest))

    generator_relative = f"configs/campaigns/{pack.name}/generate_configs.py"
    # The synthetic generator declares the SAME explicit two-way preserve flag
    # the real pack generators do.  Authentication admits a FLAGLESS generator
    # only by exact digest membership in the reviewed historical allowlist, and
    # this fixture is not a reviewed historical anchor -- so it must carry the
    # flag rather than be allowlisted, which would widen a list that is
    # deliberately closed and minimal.
    generator_raw = (
        "import argparse\n"
        "parser = argparse.ArgumentParser()\n"
        "parser.add_argument('--check', action='store_true')\n"
        "parser.add_argument(\n"
        "    '--preserve-current-frozen-bytes',\n"
        "    action=argparse.BooleanOptionalAction,\n"
        "    default=False,\n"
        ")\n"
        "args = parser.parse_args()\n"
        "if not args.check:\n"
        "    raise SystemExit(2)\n"
        "print('synthetic pack check passed')\n"
    ).encode("utf-8")
    (pack / "generate_configs.py").write_bytes(generator_raw)
    # The producer contract is written LAST, once the plan tree's projection
    # block is final: `identity_pins._load_pack_projection` requires the two
    # blocks to be equal and the tree to authenticate the producer's bytes.
    producer_raw = b""

    extraction_relative = "configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json"
    _copy_primary(repository, extraction_relative)
    extraction_raw = (repository / extraction_relative).read_bytes()
    acceptance_relative = "configs/calibration/calibration_acceptance_d079_v2.json"
    acceptance_raw = (repository / acceptance_relative).read_bytes()

    tree_path = pack / "plan_tree.json"
    tree = json.loads(tree_path.read_text())
    tree["plan"] = {"path": "calibration_plan.json", "plan_id": "plan-test"}
    tree["generator"] = {
        "path": generator_relative,
        "sha256": hashlib.sha256(generator_raw).hexdigest(),
    }
    tree["downstream_contract"] = {
        "extraction_spec": {
            "path": extraction_relative,
            "sha256": hashlib.sha256(extraction_raw).hexdigest(),
        },
        "producer_contract": {
            "path": f"configs/campaigns/{pack.name}/producer_contract.json",
            "sha256": hashlib.sha256(producer_raw).hexdigest(),
        },
    }
    tree["attempt_policy"] = {
        "policy": "abort_window_on_any_required_member_failure",
        "predeclared_before_data": True,
        "calibration_retries": 0,
        "science_member_replacements": 0,
        "outcome_dependent_top_up": "forbidden",
    }
    tree["acceptance_policy"] = {
        "selection": "issued_d116_artifact_only",
        "issued_acceptance": {
            "acceptance_id": "d079_calibration_acceptance_v2_n19",
            "path": acceptance_relative,
            "artifact_sha256": hashlib.sha256(acceptance_raw).hexdigest(),
        },
    }
    tree["stage_graph"] = [
        {
            "stage_id": "synthetic-verdict",
            "kind": "whole_window_verdict",
            "launch": {"commands": []},
        },
        {
            "stage_id": "synthetic-backup",
            "kind": "backup",
            "launch": {
                "commands": [
                    {"command_kind": "backup", "command_id": "backup.claim"},
                    {"command_kind": "backup", "command_id": "backup.bound"},
                ]
            },
        },
    ]
    tree["closeout_attachments"] = {
        "backup_requirements": {"required_successful_backups": 2}
    }
    tree["arm_attachments"]["launch"] = {
        "schema_version": "joulewise.stage_launch_bindings.v1",
        "bindings": [],
        "derived_path_rules": [],
    }
    tree["arm_attachments"]["receipt_oracle"] = (
        derive_bracket_session_receipt_oracle()
    )

    alpha_identity = _identity_unit("A", "alpha-model")
    tree["arm_attachments"]["identity_pin_projection"]["identity_units"][0][
        "declared_identity"
    ] = copy.deepcopy(alpha_identity["declared_identity"])
    tree["arm_attachments"]["identity_pin_projection"]["identity_units"][0][
        "consumer_bindings"
    ] = copy.deepcopy(alpha_identity["consumer_bindings"])
    producer_raw = readiness.render_json(
        {
            "schema_version": "synthetic-producer.v1",
            "identity_pin_projection": copy.deepcopy(
                tree["arm_attachments"]["identity_pin_projection"]
            ),
        }
    )
    (pack / "producer_contract.json").write_bytes(producer_raw)
    tree["downstream_contract"]["producer_contract"]["sha256"] = hashlib.sha256(
        producer_raw
    ).hexdigest()
    tree_raw = readiness.render_json(tree)
    tree_path.write_bytes(tree_raw)
    (pack / "plan_tree.sha256").write_bytes(
        readiness.gnu_sidecar(hashlib.sha256(tree_raw).hexdigest(), "plan_tree.json")
    )

    beta_identity = _identity_unit("B", "beta-model")
    sibling_trees = (
        {
            "d117_floor_qwen3-8b_v5": [beta_identity],
            "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5": [
                alpha_identity,
                beta_identity,
            ],
        }
        if pack_name == "d117_floor_qwen3-1p7b_v5"
        else {
            f"d117_floor_qwen25_7b{generation_suffix}": [beta_identity],
            f"d117_contrast_qwen25_1p5b_vs_7b{generation_suffix}": [
                alpha_identity,
                beta_identity,
            ],
        }
    )
    for pack_name, units in sibling_trees.items():
        sibling = repository / "configs/campaigns" / pack_name
        sibling.mkdir(parents=True, exist_ok=True)
        (sibling / "plan_tree.json").write_bytes(
            readiness.render_json(
                {
                    "arm_attachments": {
                        "identity_pin_projection": {"identity_units": units}
                    }
                }
            )
        )

    git(repository, "add", ".")
    git(repository, "commit", "-qm", "author evidence inputs")
    # PACKAUTH: that commit carries the finished PRE-projection pack, so it is
    # the commit the projection receipt anchors.
    commit_u11_projection(repository, pack, ("alpha",))
    git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
    return temporary, repository, pack, custody, arm_path


class ArmReadinessEvidenceAuthorTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        boot = mock.patch.object(
            readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID
        )
        utc = mock.patch.object(readiness, "_utc_now", return_value="2026-08-12T12:00:00Z")
        monotonic = mock.patch.object(evidence.time, "monotonic_ns", return_value=100)
        boot.start()
        utc.start()
        monotonic.start()
        self.addCleanup(boot.stop)
        self.addCleanup(utc.stop)
        self.addCleanup(monotonic.stop)












    def _install_target_sentinel_suite(
        self,
        repository: Path,
        *,
        marker: Path,
        marker_text: str,
        failing: bool,
    ) -> bytes:
        relative = "tests/test_calibration_ledger.py"
        failure = "self.fail('target sentinel failure')" if failing else "self.assertTrue(True)"
        raw = (
            "from pathlib import Path\n"
            "import unittest\n"
            "\n"
            "class TargetBytesTests(unittest.TestCase):\n"
            "    def test_executes(self):\n"
            f"        Path({str(marker)!r}).write_text({marker_text!r}, encoding='utf-8')\n"
            f"        {failure}\n"
        ).encode("utf-8")
        (repository / relative).write_bytes(raw)
        git(repository, "add", relative)
        git(repository, "commit", "-qm", "install target-only sentinel suite")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")
        return raw

    def _install_environment_sentinel_suite(
        self, repository: Path, *, marker: Path, poison_name: str
    ) -> None:
        relative = "tests/test_calibration_ledger.py"
        raw = (
            "import json\n"
            "import os\n"
            "from pathlib import Path\n"
            "import unittest\n"
            "\n"
            "class TargetBytesTests(unittest.TestCase):\n"
            "    def test_executes(self):\n"
            f"        observed = {{'poison': os.environ.get({poison_name!r}), "
            "'LC_ALL': os.environ.get('LC_ALL'), 'LANG': os.environ.get('LANG')}\n"
            f"        Path({str(marker)!r}).write_text(json.dumps(observed, sort_keys=True), encoding='utf-8')\n"
            f"        self.assertNotIn({poison_name!r}, os.environ)\n"
            "        self.assertEqual(os.environ.get('LC_ALL'), 'C')\n"
            "        self.assertEqual(os.environ.get('LANG'), 'C')\n"
        ).encode("utf-8")
        (repository / relative).write_bytes(raw)
        git(repository, "add", relative)
        git(repository, "commit", "-qm", "install hermetic environment sentinel")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")

    def _install_grandchild_sentinel_suite(
        self, repository: Path, *, marker: Path, block_seconds: float
    ) -> None:
        relative = "tests/test_calibration_ledger.py"
        ready = marker.with_suffix(".ready")
        release = marker.with_suffix(".release")
        lifecycle = marker.with_suffix(".fifo")
        grandchild = (
            "import time\n"
            "from pathlib import Path\n"
            f"lifecycle = open({str(lifecycle)!r}, 'wb', buffering=0)\n"
            "lifecycle.write(b'READY\\n')\n"
            f"Path({str(ready)!r}).write_text('READY', encoding='utf-8')\n"
            f"while not Path({str(release)!r}).exists():\n"
            "    time.sleep(0.01)\n"
            f"Path({str(marker)!r}).write_text('LEAKED', encoding='utf-8')\n"
        )
        raw = (
            "from pathlib import Path\n"
            "import subprocess\n"
            "import sys\n"
            "import time\n"
            "import unittest\n"
            "\n"
            "class TargetBytesTests(unittest.TestCase):\n"
            "    def test_executes(self):\n"
            f"        subprocess.Popen([sys.executable, '-I', '-B', '-c', {grandchild!r}])\n"
            "        deadline = time.monotonic() + 30.0\n"
            f"        while not Path({str(ready)!r}).exists():\n"
            "            self.assertLess(time.monotonic(), deadline, 'grandchild never ready')\n"
            "            time.sleep(0.01)\n"
            f"        time.sleep({block_seconds!r})\n"
        ).encode("utf-8")
        (repository / relative).write_bytes(raw)
        git(repository, "add", relative)
        git(repository, "commit", "-qm", "install process-group sentinel")
        git(repository, "update-ref", "refs/remotes/origin/main", "HEAD")

    def _execute_ready_grandchild_suite(self, repository, marker, *, timeout=False):
        """Begin the timeout only after the grandchild's readiness handshake."""
        ready = marker.with_suffix(".ready")
        lifecycle = marker.with_suffix(".fifo")
        os.mkfifo(lifecycle)
        reader = os.open(lifecycle, os.O_RDONLY | os.O_NONBLOCK)
        self.addCleanup(os.close, reader)
        processes = []
        real_popen = evidence.subprocess.Popen

        def start(*args, **kwargs):
            self.assertIs(kwargs.get("start_new_session"), True)
            process = real_popen(*args, **kwargs)
            processes.append(process)
            real_wait = process.wait

            def cleanup():
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                real_wait(timeout=5.0)

            self.addCleanup(cleanup)

            def wait(timeout=None):
                deadline = time.monotonic() + 30.0
                while not ready.exists():
                    self.assertIsNone(process.poll(), "suite exited before grandchild ready")
                    self.assertLess(time.monotonic(), deadline, "grandchild never ready")
                    time.sleep(0.01)
                return real_wait(timeout=timeout)

            process.wait = wait
            return process

        test_ids = ("tests.test_calibration_ledger.TargetBytesTests.test_executes",)
        with mock.patch.object(evidence.subprocess, "Popen", side_effect=start):
            if timeout:
                with (
                    mock.patch.object(evidence, "_SUITE_TIMEOUT_SECONDS", 0.1),
                    self.assertRaisesRegex(ValueError, "timed out after 0.1 seconds"),
                ):
                    evidence._execute_unittest_suite_subprocess(repository, test_ids)
            else:
                result = evidence._execute_unittest_suite_subprocess(repository, test_ids)
                self.assertTrue(result.passed)

        self.assertTrue(ready.exists(), "grandchild never ran")
        self.assertEqual(len(processes), 1)
        marker.with_suffix(".release").write_text("RELEASE", encoding="utf-8")
        deadline = time.monotonic() + 30.0
        observed = bytearray()
        while True:
            self.assertFalse(marker.exists(), "grandchild survived suite cleanup")
            try:
                chunk = os.read(reader, 4096)
            except BlockingIOError:
                chunk = None
            if chunk == b"":
                break  # EOF proves the ready grandchild closed its held writer.
            if chunk:
                observed.extend(chunk)
            self.assertLess(time.monotonic(), deadline, "grandchild lifecycle never closed")
            time.sleep(0.01)
        self.assertEqual(bytes(observed), b"READY\n")
        self.assertFalse(marker.exists())




    def _target_sentinel_deriver(self, context) -> evidence._DerivedKind:
        kind = "RECOVERY_LEDGER_TEST"
        result = evidence._run_suite(
            context,
            kind,
            ("tests.test_calibration_ledger.TargetBytesTests.test_executes",),
        )
        artifact, _raw = evidence._committed_artifact(
            context.repository, "tests/test_calibration_ledger.py", kind=kind
        )
        return evidence._DerivedKind(
            kind,
            {"desk.recovery_ledger_path.v1": {"target_sentinel_status": "PASS"}},
            (artifact,),
            (evidence._check("target_sentinel_suite", result.evidence()),),
            {"bound_head": context.head_commit},
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
