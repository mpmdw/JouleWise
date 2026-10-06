"""Record-only collectors: counterfactual fixtures for each replaced arm-path NUMBER check.

Each fixture is a disposable Git repository holding a small pack. A
counterfactual changes one thing the retired arm path used to refuse on and
asserts that the collector now records the matching flag instead.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path
from unittest import mock

from joulewise.flags.collect import (
    COLLECTORS,
    collect_checkout_identity,
    collect_executed_code,
    collect_ledger_readiness,
    collect_model_identity,
    collect_pack_identity,
    committed_pack_tree_sha256,
    run_collector,
    run_collectors,
)
from joulewise.flags.schema import validate_flag
from joulewise.flags.sink import FlagSink, read_flags
from joulewise.provenance import model_artifact_identity
from tests.git_fixture import init_git_fixture

REPO = Path(__file__).resolve().parents[2]
REAL_PACKS = (
    "configs/campaigns/d117_floor_qwen3-1p7b_v5",
    "configs/campaigns/d117_floor_qwen3-8b_v5",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5",
)
PACK_REL = "configs/campaigns/fake_v5"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args),
        check=True, capture_output=True, text=True,
    )
    return completed.stdout.strip()


class PackFixture:
    """A committed repository with joulewise/, scripts/ and one small pack."""

    def __init__(self, root: Path, *, duplicate_run_id: bool = False, model_pin: str | None = None) -> None:
        self.repo = root / "repo"
        self.repo.mkdir()
        init_git_fixture(self.repo, "-q")
        self.model = root / "model"
        self.model.mkdir()
        (self.model / "model.safetensors").write_bytes(b"weights-v1" * 100)
        (self.model / "tokenizer.json").write_bytes(b'{"tokenizer": 1}')
        (self.repo / "joulewise").mkdir()
        (self.repo / "joulewise" / "core.py").write_text("VALUE = 1\n")
        (self.repo / "scripts").mkdir()
        (self.repo / "scripts" / "tool.py").write_text("print('tool')\n")
        (self.repo / "configs" / "calibration").mkdir(parents=True)
        (self.repo / "configs" / "calibration" / "calibration_ledger_head.json").write_text('{"sequence": 1}\n')
        self.pack = self.repo / PACK_REL
        (self.pack / "01_stage").mkdir(parents=True)
        tokenizer_sha = sha((self.model / "tokenizer.json").read_bytes())
        science = []
        inventory = []
        for index in (1, 2, 3):
            run_id = "fake-r01" if duplicate_run_id and index == 2 else f"fake-r0{index}"
            config = {"schema_version": "x", "run_id": run_id,
                      "model": {"source": str(self.model), "tokenizer_json_sha256": tokenizer_sha}}
            raw = json.dumps(config, sort_keys=True).encode() + b"\n"
            relative = f"01_stage/{run_id}-{index}.json"
            (self.pack / relative).write_bytes(raw)
            science.append({"ordinal": index, "stage_id": "01_stage", "config_path": f"{PACK_REL}/{relative}",
                            "config_sha256": sha(raw), "run_id": run_id})
            inventory.append({"path": relative, "sha256": sha(raw)})
        spec = b'{"schema_version": "spec"}\n'
        (self.pack / "extraction_spec.json").write_bytes(spec)
        plan = b'{"plan_id": "plan-fake"}\n'
        (self.pack / "calibration_plan.json").write_bytes(plan)
        tree = {
            "schema_version": "joulewise.d117_plan_tree.v1",
            "plan": {"path": "calibration_plan.json", "plan_id": "plan-fake", "actual_sha256": sha(plan)},
            "science": science,
            "external_inputs": {"manifests": [{"external_input_id": "neg8", "members": [
                {"run_id": "neg8-r01", "path": f"{PACK_REL}/01_stage/{science[0]['config_path'].split('/')[-1]}",
                 "sha256": science[0]["config_sha256"]}]}]},
            "downstream_contract": {"extraction_spec": {"path": f"{PACK_REL}/extraction_spec.json",
                                                        "sha256": sha(spec)}},
            "arm_attachments": {"identity_pin_projection": {
                "state": "unprojected",
                "identity_units": [{
                    "identity_unit_id": "u1",
                    "declared_identity": {"model_source": str(self.model)},
                    "config_inventory": inventory,
                    "model_runtime_config": {"model_artifact_sha256": model_pin,
                                             "runtime_identity_sha256": None, "config_set_sha256": None},
                }],
            }},
        }
        (self.pack / "plan_tree.json").write_text(json.dumps(tree, indent=1, sort_keys=True) + "\n")
        self.chain = self.repo / "night" / "chain.zsh"
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "fixture")
        self.head = git(self.repo, "rev-parse", "HEAD")

    def params(self, **extra):
        return {"pack_root": str(self.pack), "repo_root": str(self.repo), "stage": "desk",
                "plan_id": "plan-fake", "attempt": 1, **extra}

    def commit(self, message: str = "change") -> str:
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", message)
        return git(self.repo, "rev-parse", "HEAD")


def checks(result, code: str) -> list[str]:
    for flag in result["flags"]:
        assert validate_flag(flag) == [], validate_flag(flag)
    return sorted(flag["observed"]["check"] for flag in result["flags"] if flag["code"] == code)


class FixtureCase(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)

    def tearDown(self) -> None:
        self.directory.cleanup()


class PackIdentityCounterfactualTests(FixtureCase):
    def test_committed_fixture_pack_has_no_flags(self) -> None:
        fixture = PackFixture(self.root)
        result = collect_pack_identity(fixture.params())
        self.assertEqual(result["flags"], [])
        # calibration plan, three science configs, one external member, the
        # extraction spec and three identity-unit inventory rows.
        self.assertEqual(result["observed"]["pins_checked"], 9)

    def test_flipped_config_byte_flags_pack_identity(self) -> None:
        fixture = PackFixture(self.root)
        config = fixture.pack / "01_stage" / "fake-r02-2.json"
        raw = bytearray(config.read_bytes())
        raw[5] ^= 0x01
        config.write_bytes(bytes(raw))
        result = collect_pack_identity(fixture.params())
        self.assertEqual(checks(result, "pack.identity_mismatch"), ["pack_committed", "pinned_file_digest"])
        fixture.commit("flip committed")
        result = collect_pack_identity(fixture.params())
        self.assertEqual(checks(result, "pack.identity_mismatch"), ["pinned_file_digest"])
        differing = next(f for f in result["flags"] if f["observed"]["check"] == "pinned_file_digest")
        self.assertEqual({d["path"] for d in differing["observed"]["differing"]},
                         {f"{PACK_REL}/01_stage/fake-r02-2.json", "01_stage/fake-r02-2.json"})

    def test_uncommitted_pack_flags_pack_identity(self) -> None:
        fixture = PackFixture(self.root)
        (fixture.pack / "01_stage" / "stray.json").write_text("{}\n")
        result = collect_pack_identity(fixture.params())
        self.assertEqual(checks(result, "pack.identity_mismatch"), ["pack_committed"])
        flag = result["flags"][0]
        self.assertEqual(flag["observed"]["reason"], "not_committed")
        self.assertEqual(flag["source"]["legacy_site"], "joulewise/arm_readiness.py:committed_pack_tree_sha256")

    def test_missing_extraction_spec_flags_pack_identity(self) -> None:
        fixture = PackFixture(self.root)
        git(fixture.repo, "rm", "-q", f"{PACK_REL}/extraction_spec.json")
        fixture.commit("drop spec")
        result = collect_pack_identity(fixture.params())
        self.assertEqual(checks(result, "pack.identity_mismatch"), ["pinned_file_missing"])
        self.assertEqual(result["flags"][0]["observed"]["missing"][0]["path"], f"{PACK_REL}/extraction_spec.json")

    def test_duplicate_run_id_flags_pack_identity(self) -> None:
        fixture = PackFixture(self.root, duplicate_run_id=True)
        result = collect_pack_identity(fixture.params())
        self.assertEqual(checks(result, "pack.identity_mismatch"), ["run_id_unique"])
        self.assertEqual(result["flags"][0]["observed"]["duplicate_run_ids"], ["fake-r01"])

    def test_registered_pack_tree_digest_is_compared(self) -> None:
        fixture = PackFixture(self.root)
        digest = committed_pack_tree_sha256(fixture.pack)
        self.assertEqual(collect_pack_identity(fixture.params(expected_pack_tree_sha256=digest))["flags"], [])
        result = collect_pack_identity(fixture.params(expected_pack_tree_sha256="0" * 64))
        self.assertEqual(checks(result, "pack.identity_mismatch"), ["pack_tree_digest"])

    def test_ported_digest_equals_arm_readiness_digest(self) -> None:
        from joulewise import arm_readiness

        fixture = PackFixture(self.root)
        self.assertEqual(committed_pack_tree_sha256(fixture.pack), arm_readiness.committed_pack_tree_sha256(fixture.pack))


class RealPackTests(unittest.TestCase):
    def test_committed_block5_packs_raise_no_pack_flags_and_match_the_d134_digest(self) -> None:
        from joulewise import arm_readiness

        status = subprocess.run(("git", "-C", str(REPO), "status", "--porcelain", "--", *REAL_PACKS),
                                capture_output=True, text=True, check=True).stdout
        if status.strip():
            self.skipTest("block-5 packs have working-tree edits in this checkout")
        for relative in REAL_PACKS:
            pack = REPO / relative
            with self.subTest(pack=relative):
                result = collect_pack_identity({"pack_root": str(pack), "repo_root": str(REPO), "stage": "desk"})
                self.assertEqual(result["flags"], [])
                self.assertGreater(result["observed"]["pins_checked"], 150)
                self.assertEqual(result["observed"]["committed_pack_tree_sha256"],
                                 arm_readiness.committed_pack_tree_sha256(pack))


class ModelIdentityTests(FixtureCase):
    def pinned_fixture(self) -> PackFixture:
        probe = self.root / "probe"
        probe.mkdir()
        (probe / "model.safetensors").write_bytes(b"weights-v1" * 100)
        identity = model_artifact_identity(str(probe))
        return PackFixture(self.root, model_pin=identity["folded_sha256"])

    def test_pinned_model_passes(self) -> None:
        fixture = self.pinned_fixture()
        result = collect_model_identity(fixture.params())
        self.assertEqual(result["flags"], [])

    def test_model_file_digest_change_flags_model_identity(self) -> None:
        fixture = self.pinned_fixture()
        weights = fixture.model / "model.safetensors"
        raw = bytearray(weights.read_bytes())
        raw[0] ^= 0x01
        weights.write_bytes(bytes(raw))
        result = collect_model_identity(fixture.params())
        self.assertEqual(checks(result, "model.identity_mismatch"), ["model_artifact"])

    def test_unpinned_model_is_disclosed_with_its_digest(self) -> None:
        fixture = PackFixture(self.root)
        result = collect_model_identity(fixture.params())
        self.assertEqual(checks(result, "model.identity_unpinned"), ["model_artifact"])
        observed = result["flags"][0]["observed"]["model_artifact_sha256"]
        self.assertEqual(observed, model_artifact_identity(str(fixture.model))["folded_sha256"])
        pinned = collect_model_identity(fixture.params(expected_model_artifact_sha256={"u1": observed}))
        self.assertEqual(pinned["flags"], [])

    def test_tokenizer_change_flags_model_identity(self) -> None:
        fixture = self.pinned_fixture()
        (fixture.model / "tokenizer.json").write_bytes(b'{"tokenizer": 2}')
        result = collect_model_identity(fixture.params())
        self.assertEqual(checks(result, "model.identity_mismatch"), ["tokenizer_json"])

    def test_missing_model_flags_model_identity(self) -> None:
        fixture = self.pinned_fixture()
        (fixture.model / "model.safetensors").unlink()
        result = collect_model_identity(fixture.params())
        self.assertIn("model_artifact", checks(result, "model.identity_mismatch"))

    def test_frozen_projection_refusal_flags_model_identity(self) -> None:
        fixture = self.pinned_fixture()
        tree_path = fixture.pack / "plan_tree.json"
        tree = json.loads(tree_path.read_text())
        tree["arm_attachments"]["identity_pin_projection"]["state"] = "frozen"
        tree_path.write_text(json.dumps(tree))
        calls = []

        def verify(pack_root, custody_root, session_id):
            calls.append((Path(pack_root), custody_root, session_id))
            return {"status": "REFUSE", "reason_codes": ["readiness_identity_environment_dirty"],
                    "identity_units": [], "receipt_sha256": "f" * 64}

        result = collect_model_identity(
            fixture.params(verify_frozen_projection=True, custody_root=str(self.root / "custody"),
                           bracket_session_id="session-1"),
            verify_frozen=verify,
        )
        self.assertEqual(calls, [(fixture.pack, str(self.root / "custody"), "session-1")])
        self.assertEqual(checks(result, "model.identity_mismatch"), ["frozen_projection"])
        self.assertEqual(result["flags"][0]["source"]["legacy_code"], "readiness_identity_environment_dirty")


class CheckoutIdentityTests(FixtureCase):
    def test_clean_checkout_at_h_claim_passes(self) -> None:
        fixture = PackFixture(self.root)
        result = collect_checkout_identity(fixture.params(h_claim=fixture.head))
        self.assertEqual(result["flags"], [])

    def test_head_not_h_claim_flags_code_identity(self) -> None:
        fixture = PackFixture(self.root)
        (fixture.repo / "joulewise" / "core.py").write_text("VALUE = 2\n")
        fixture.commit("code change after the seal")
        result = collect_checkout_identity(fixture.params(h_claim=fixture.head))
        self.assertEqual(checks(result, "code.executed_differs_from_sealed"), ["head_is_h_claim"])
        self.assertEqual(result["flags"][0]["observed"]["non_pin_changes"], ["joulewise/core.py"])

    def test_pin_only_commit_keeps_the_code_identity(self) -> None:
        fixture = PackFixture(self.root)
        (fixture.repo / "configs" / "calibration" / "calibration_ledger_head.json").write_text('{"sequence": 2}\n')
        fixture.commit("pin advance")
        result = collect_checkout_identity(fixture.params(h_claim=fixture.head))
        self.assertEqual(result["flags"], [])
        self.assertEqual(result["observed"]["changed_paths"], ["configs/calibration/calibration_ledger_head.json"])

    def test_dirty_checkout_flags_code_identity(self) -> None:
        fixture = PackFixture(self.root)
        (fixture.repo / "scripts" / "tool.py").write_text("print('edited')\n")
        result = collect_checkout_identity(fixture.params(h_claim=fixture.head))
        self.assertEqual(checks(result, "code.executed_differs_from_sealed"), ["checkout_clean"])


class ExecutedCodeTests(FixtureCase):
    def sealed(self, fixture: PackFixture, *, roots=None) -> Path:
        result = collect_executed_code(fixture.params())
        self.assertEqual(result["flags"], [])
        files = {}
        for relative in ("joulewise/core.py", "scripts/tool.py"):
            files[relative] = sha((fixture.repo / relative).read_bytes())
        document = {"files": files}
        if roots is not None:
            document["roots"] = roots
        path = self.root / "sealed_inventory.json"
        path.write_text(json.dumps(document))
        return path

    def test_inventory_is_preserved_create_once_as_evidence(self) -> None:
        fixture = PackFixture(self.root)
        custody = self.root / "custody"
        first = collect_executed_code(fixture.params(custody_root=str(custody)))
        second = collect_executed_code(fixture.params(custody_root=str(custody)))
        written = sorted((custody / "flags").glob("executed_inventory.desk.*.json"))
        self.assertEqual(len(written), 1)
        self.assertEqual(first["observed"]["inventory_sha256"], sha(written[0].read_bytes()))
        self.assertEqual(first["observed"], second["observed"])
        inventory = json.loads(written[0].read_text())
        self.assertIn(f"{PACK_REL}/plan_tree.json", inventory["files"])

    def test_changed_sealed_file_flags_code_identity(self) -> None:
        fixture = PackFixture(self.root)
        sealed = self.sealed(fixture)
        self.assertEqual(collect_executed_code(fixture.params(sealed_inventory=str(sealed)))["flags"], [])
        (fixture.repo / "joulewise" / "core.py").write_text("VALUE = 3\n")
        result = collect_executed_code(fixture.params(sealed_inventory=str(sealed),
                                                      custody_root=str(self.root / "custody")))
        self.assertEqual(checks(result, "code.executed_differs_from_sealed"), ["executed_inventory"])
        flag = result["flags"][0]
        self.assertEqual(flag["observed"]["changed"], ["joulewise/core.py"])
        self.assertEqual(len(flag["evidence"]), 1)

    def test_added_file_under_a_sealed_root_flags_code_identity(self) -> None:
        fixture = PackFixture(self.root)
        sealed = self.sealed(fixture, roots=["joulewise"])
        (fixture.repo / "joulewise" / "new.py").write_text("X = 1\n")
        fixture.commit("new module")
        result = collect_executed_code(fixture.params(sealed_inventory=str(sealed)))
        self.assertEqual(result["flags"][0]["observed"]["added"], ["joulewise/new.py"])

    def test_chain_sidecar_mismatch_flags_code_identity(self) -> None:
        fixture = PackFixture(self.root)
        chain = self.root / "chain.zsh"
        chain.write_text("#!/bin/zsh\nrun_stage one\n")
        sidecar = self.root / "chain.zsh.sha256"
        sidecar.write_text(f"{sha(chain.read_bytes())}  chain.zsh\n")
        params = fixture.params(chain_path=str(chain), chain_sidecar=str(sidecar))
        self.assertEqual(collect_executed_code(params)["flags"], [])
        chain.write_text("#!/bin/zsh\nrun_stage two\n")
        result = collect_executed_code(params)
        self.assertEqual(checks(result, "code.executed_differs_from_sealed"), ["chain_sidecar"])
        self.assertEqual(result["flags"][0]["source"]["legacy_code"], "night_chain_digest_mismatch")


class LedgerReadinessTests(FixtureCase):
    def stub(self, payload: dict, code: int) -> list[str]:
        script = self.root / "readiness_stub.py"
        script.write_text(f"import json, sys\nprint(json.dumps({payload!r}))\nsys.exit({code})\n")
        return [sys.executable, str(script)]

    def test_refusal_is_disclosed_not_refused(self) -> None:
        argv = self.stub({"refusal_code": "calibration_ledger_bracket_session_open"}, 3)
        result = collect_ledger_readiness({"repo_root": str(self.root), "argv": argv, "stage": "arm"})
        self.assertEqual(checks(result, "calibration.ledger_not_ready"), ["ledger_readiness"])
        self.assertEqual(result["flags"][0]["source"]["legacy_code"], "calibration_ledger_bracket_session_open")
        self.assertEqual(result["flags"][0]["source"]["stage"], "arm")

    def test_ready_gives_no_flag(self) -> None:
        argv = self.stub({"status": "ready"}, 0)
        result = collect_ledger_readiness({"repo_root": str(self.root), "argv": argv})
        self.assertEqual(result["flags"], [])
        self.assertEqual(result["observed"]["status"], "ready")


FAKE_COLLECTOR_MODULE = textwrap.dedent(
    """
    import json, sys, time
    if sys.argv[1:] == ["--run-collector"]:
        request = json.loads(sys.stdin.read())
        mode = request["params"]["mode"]
        if mode == "sleep":
            time.sleep(60)
        elif mode == "garbage":
            print("not json")
        elif mode == "badflag":
            print(json.dumps({"ok": True, "flags": [{"code": "x"}], "observed": None}))
        elif mode == "crash":
            raise SystemExit(9)
    """
)


class RunnerTests(FixtureCase):
    def fake_module(self) -> None:
        (self.root / "fake_collector_l4.py").write_text(FAKE_COLLECTOR_MODULE)
        patcher = mock.patch.dict(os.environ, {"PYTHONPATH": str(self.root)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_subprocess_runner_returns_validated_flags(self) -> None:
        fixture = PackFixture(self.root)
        (fixture.pack / "01_stage" / "stray.json").write_text("{}\n")
        outcome = run_collector("pack_identity", fixture.params(), timeout_s=60)
        self.assertEqual(outcome.status, "ok", outcome.error)
        self.assertEqual([f["code"] for f in outcome.flags], ["pack.identity_mismatch"])

    def test_collector_exception_is_an_error_entry_not_a_raise(self) -> None:
        outcome = run_collector("pack_identity", {"repo_root": str(self.root)}, timeout_s=60)
        self.assertEqual(outcome.status, "error")
        self.assertIn("KeyError", outcome.error)

    def test_timeout_kills_the_collector(self) -> None:
        self.fake_module()
        started = time.monotonic()
        outcome = run_collector("fake", {"mode": "sleep"}, timeout_s=1.0, module="fake_collector_l4")
        self.assertEqual(outcome.status, "timeout")
        self.assertLess(time.monotonic() - started, 30)

    def test_garbage_crash_and_malformed_flags_are_errors(self) -> None:
        self.fake_module()
        for mode in ("garbage", "crash", "badflag"):
            with self.subTest(mode=mode):
                outcome = run_collector("fake", {"mode": mode}, timeout_s=30, module="fake_collector_l4")
                self.assertEqual(outcome.status, "error")
                self.assertEqual(outcome.flags, [])

    def test_run_collectors_writes_flags_and_run_log_and_never_raises(self) -> None:
        fixture = PackFixture(self.root)
        (fixture.pack / "01_stage" / "stray.json").write_text("{}\n")
        custody = self.root / "custody"
        sink = FlagSink(custody / "flags" / "arm.jsonl")
        outcomes = run_collectors(
            [("pack_identity", fixture.params()),
             ("checkout_identity", {"repo_root": str(self.root / "not-a-repo")})],
            stage="arm", sink=sink, runs_log=custody / "flags" / "collector_runs.jsonl",
        )
        self.assertEqual([o.status for o in outcomes], ["ok", "error"])
        flags, problems = read_flags(custody / "flags" / "arm.jsonl")
        self.assertEqual(problems, [])
        self.assertEqual({f["source"]["stage"] for f in flags}, {"arm"})
        self.assertEqual({f["code"] for f in flags}, {"pack.identity_mismatch"})
        record = json.loads((custody / "flags" / "collector_runs.jsonl").read_text().splitlines()[-1])
        self.assertEqual(record["stage"], "arm")
        self.assertEqual([e["collector"] for e in record["collector_errors"]], ["checkout_identity"])

    def test_every_collector_is_registered(self) -> None:
        self.assertEqual(sorted(COLLECTORS),
                         ["checkout_identity", "executed_code", "ledger_readiness", "model_identity", "pack_identity"])


class CollectWindowFlagsCliTests(FixtureCase):
    def test_cli_records_and_exits_zero_even_when_collectors_fail(self) -> None:
        fixture = PackFixture(self.root)
        (fixture.pack / "01_stage" / "stray.json").write_text("{}\n")
        custody = self.root / "custody"
        completed = subprocess.run(
            [sys.executable, "-B", str(REPO / "scripts" / "collect_window_flags.py"), "--stage", "desk",
             "--custody", str(custody), "--repo", str(fixture.repo), "--pack", str(fixture.pack),
             "--plan-id", "plan-fake", "--attempt", "1", "--h-claim", fixture.head,
             "--sealed-inventory", str(self.root / "absent.json")],
            capture_output=True, text=True, timeout=300,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["collectors"]["executed_code"]["status"], "error")
        self.assertEqual(summary["collectors"]["pack_identity"]["status"], "ok")
        flags, problems = read_flags(custody / "flags" / "desk.jsonl")
        self.assertEqual(problems, [])
        self.assertIn("pack.identity_mismatch", {f["code"] for f in flags})
        self.assertTrue((custody / "flags" / "collector_runs.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
