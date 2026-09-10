"""Defect-shaped desk-watch and non-live chain skeleton regressions."""

from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from scripts import issue_calibration_acceptance_generation as issuer


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/d117_v2_production/issued"
CHAIN = ROOT / "scripts/night_chains/calibration_derivation_only.zsh"


class DeskEpochWatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "ledger.jsonl"
        self.pin = self.root / "head.json"
        self.acceptance = self.root / "acceptance.json"
        self.ledger.write_bytes((FIXTURE / "calibration_observation_ledger.jsonl").read_bytes())
        self.pin.write_bytes((FIXTURE / "calibration_ledger_head.json").read_bytes())
        self.acceptance.write_bytes(issuer.DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes())
        self.original = {p: p.read_bytes() for p in (self.ledger, self.pin, self.acceptance)}
        epoch = json.loads(self.acceptance.read_bytes())["identity_epoch"]
        t1 = json.loads(self.ledger.read_text().splitlines()[-1])["t1_bindings"]
        self.observed = {field: epoch[field] for field in ("os_build", "hardware_model")}
        self.observed.update({field: t1[field] for field in ("powermetrics_sha256", "mlx_version")})
        # The real parser, hash chain, receipt shapes, custody and acceptance
        # authentication run. Only Git's committed-pin byte source is a fixture.
        self.pin_source = mock.patch(
            "joulewise.calibration_ledger._committed_pin_bytes",
            return_value=self.pin.read_bytes(),
        )
        self.pin_source.start()
        self.addCleanup(self.pin_source.stop)

    def run_check(self, **changes: object) -> tuple[int, str]:
        output = io.StringIO()
        with mock.patch.object(issuer, "observe_machine", return_value=self.observed | changes):
            with redirect_stdout(output):
                rc = issuer.main([
                    "check", "--ledger", str(self.ledger), "--head-pin", str(self.pin),
                    "--acceptance", str(self.acceptance),
                ])
        return rc, output.getvalue()

    def test_equal_epoch_and_t1_admit_without_writes(self) -> None:
        rc, output = self.run_check()
        self.assertEqual(rc, 0, output)
        self.assertNotIn("MISMATCH", output)
        for path, raw in self.original.items():
            self.assertEqual(path.read_bytes(), raw)
        self.assertEqual(set(self.root.iterdir()), set(self.original))

    def test_changed_os_build_refuses_and_names_only_changed_field(self) -> None:
        rc, output = self.run_check(os_build="25G83")
        self.assertEqual(rc, 3, output)
        self.assertIn("mismatched fields: os_build\n", output)

    def test_binary_hash_alone_refuses_even_when_epoch_matches(self) -> None:
        self.assertNotIn("powermetrics_sha256", json.loads(self.acceptance.read_bytes())["identity_epoch"])
        rc, output = self.run_check(powermetrics_sha256="b" * 64)
        self.assertEqual(rc, 3, output)
        self.assertIn("mismatched fields: powermetrics_sha256\n", output)

    def test_hardware_and_mlx_changes_refuse(self) -> None:
        for field in ("hardware_model", "mlx_version"):
            with self.subTest(field=field):
                rc, output = self.run_check(**{field: "changed"})
                self.assertEqual(rc, 3, output)
                self.assertIn(f"mismatched fields: {field}\n", output)

    def test_unavailable_mlx_is_recorded_and_refuses(self) -> None:
        rc, output = self.run_check(mlx_version=None)
        self.assertEqual(rc, 3, output)
        self.assertIn("unavailable", output)
        self.assertIn("mismatched fields: mlx_version\n", output)
        self.assertEqual(issuer.mismatched_fields(
            self.observed | {"mlx_version": None}, self.observed | {"mlx_version": None},
        ), ("mlx_version",))

    def test_invalid_acceptance_bytes_refuse(self) -> None:
        self.acceptance.write_bytes(self.acceptance.read_bytes() + b" ")
        rc, output = self.run_check()
        self.assertEqual(rc, 3, output)
        self.assertIn("acceptance: invalid or not ACTIVE", output)

    def test_historical_issued_acceptance_is_not_active(self) -> None:
        from joulewise.calibration_bracketing import ISSUED_ACCEPTANCE_REGISTRY
        older = next(row for key, row in ISSUED_ACCEPTANCE_REGISTRY.items() if key != issuer.ACTIVE_ACCEPTANCE_ID)
        self.acceptance.write_bytes(Path(older["path"]).read_bytes())
        rc, output = self.run_check()
        self.assertEqual(rc, 3, output)
        self.assertIn("acceptance: invalid or not ACTIVE", output)

    def test_ledger_hash_mutation_refuses(self) -> None:
        self.ledger.write_text(self.ledger.read_text().replace('"mlx_version":"0.31.2"', '"mlx_version":"0.31.3"'))
        rc, output = self.run_check()
        self.assertEqual(rc, 3, output)
        self.assertIn("ledger:", output)

    def test_head_pin_mismatch_refuses(self) -> None:
        pin = json.loads(self.pin.read_bytes())
        pin["head_digest"] = "0" * 64
        self.pin.write_text(json.dumps(pin))
        rc, output = self.run_check()
        self.assertEqual(rc, 3, output)
        self.assertIn("calibration_ledger_head_mismatch", output)

    def test_last_row_without_t1_does_not_substitute_older_row(self) -> None:
        snapshot = SimpleNamespace(refusal_reasons=(), receipts=(
            {"t1_bindings": self.observed}, {"event": "session-aborted"},
        ))
        with mock.patch.object(issuer, "load_calibration_ledger_snapshot", return_value=snapshot):
            rc, output = self.run_check()
        self.assertEqual(rc, 3, output)
        self.assertIn("ledger: last row has no T1 bindings", output)

    def test_mutation_kills_check_comparator_bypass(self) -> None:
        # Production call site: issue_calibration_acceptance_generation.check
        # -> mismatched_fields. Without it, the changed-OS refusal must fail.
        with mock.patch.object(issuer, "mismatched_fields", return_value=()):
            with self.assertRaises(AssertionError):
                self.test_changed_os_build_refuses_and_names_only_changed_field()

    def test_mutation_kills_check_binary_field_omission(self) -> None:
        # Production call site: check -> mismatched_fields over WATCH_FIELDS.
        # Epoch-only implementations used to miss a same-build binary swap.
        with mock.patch.object(issuer, "WATCH_FIELDS", ("os_build", "hardware_model", "mlx_version")):
            with self.assertRaises(AssertionError):
                self.test_binary_hash_alone_refuses_even_when_epoch_matches()

    def test_production_defaults_and_stub(self) -> None:
        args = issuer.build_parser().parse_args(["check"])
        self.assertEqual(args.ledger, issuer.DEFAULT_LEDGER_PATH)
        self.assertEqual(args.head_pin, issuer.DEFAULT_HEAD_PIN_PATH)
        self.assertEqual(args.acceptance, issuer.DEFAULT_ACCEPTANCE_BOUND_PATH)
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts/issue_calibration_acceptance_generation.py"), "prepare-candidate"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 64, result.stderr)
        self.assertEqual(result.stdout.strip(), "not implemented: waits for seat S3's generation-row schema and the corpus")

    def test_machine_observation_reads_sysctl_hash_and_mlx(self) -> None:
        binary = self.root / "powermetrics"
        binary.write_bytes(b"fixture sampler bytes; never execute")
        with mock.patch.object(issuer, "POWERMETRICS_PATH", binary):
            with mock.patch.object(issuer.subprocess, "run", side_effect=[
                SimpleNamespace(stdout="25G83\n"), SimpleNamespace(stdout="Mac15,9\n"),
            ]) as run:
                with mock.patch.object(issuer.importlib, "import_module", return_value=SimpleNamespace(__version__="0.31.2")) as imp:
                    observed = issuer.observe_machine()
        self.assertEqual(observed, {
            "os_build": "25G83", "hardware_model": "Mac15,9", "mlx_version": "0.31.2",
            "powermetrics_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        })
        self.assertEqual([call.args[0] for call in run.call_args_list], [
            ["sysctl", "-n", "kern.osversion"], ["sysctl", "-n", "hw.model"],
        ])
        imp.assert_called_once_with("mlx.core")

    def test_unavailable_machine_inputs_do_not_crash(self) -> None:
        with mock.patch.object(issuer, "POWERMETRICS_PATH", self.root / "missing"):
            with mock.patch.object(issuer.subprocess, "run", side_effect=OSError("missing")):
                with mock.patch.object(issuer.importlib, "import_module", side_effect=ImportError("missing")):
                    self.assertEqual(issuer.observe_machine(), dict.fromkeys(issuer.WATCH_FIELDS))


@unittest.skipUnless(shutil.which("zsh"), "zsh not installed")
class DerivationChainSkeletonTests(unittest.TestCase):
    def run_chain(self, *, end: int = 10000, slots: str | None = None, fail: str = "") -> tuple[subprocess.CompletedProcess, list[dict]]:
        # All external commands are fixture executables, including the writer.
        # Neither the real sampler nor a real reservation/recovery tool runs.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "clock").write_text("0")
            fake = "#!" + sys.executable + "\n" + '''
import json, os, pathlib, sys
root = pathlib.Path(os.environ["FAKE_ROOT"])
clock = root / "clock"
now = int(clock.read_text())
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
with (root / "calls").open("a") as stream:
    stream.write(json.dumps({"name": name, "args": args, "time": now}) + "\\n")
if name == "date":
    print(now)
elif name == "sleep":
    clock.write_text(str(now + int(args[0])))
elif name == "python3":
    if "validate_powermetrics_fiducial.py" in args[0]:
        slot = args[args.index("--slot") + 1]
        if slot == os.environ.get("FAIL_SLOT"):
            sys.exit(7)
        clock.write_text(str(now + 480))
    elif not any(tool in args[0] for tool in ("reserve_calibration_window_bracket.py", "recover_calibration_ledger.py")):
        sys.exit(99)
else:
    sys.exit(98)
'''
            for name in ("date", "sleep", "python3"):
                path = root / name
                path.write_text(fake)
                path.chmod(0o755)
            env = os.environ.copy()
            env.pop("SLOT_COUNT", None)
            env.update({
                "PATH": str(root), "FAKE_ROOT": str(root), "FAIL_SLOT": fail,
                "SESSION_ID": "fixture-session", "WINDOW_ID": "fixture-window",
                "PLAN_ID": "fixture-plan", "PLAN_SHA256": "a" * 64, "PLAN": "/fixture/plan.json",
                "EVIDENCE_ROOT_ID": "fixture-root", "RUNS_ROOT": "/fixture/runs",
                "IDENTITY_EPOCH_JSON": "/fixture/epoch.json", "T1_BINDINGS_JSON": "/fixture/t1.json",
                "WINDOW_END_EPOCH_S": str(end),
            })
            if slots is not None:
                env["SLOT_COUNT"] = slots
            result = subprocess.run([shutil.which("zsh"), str(CHAIN)], env=env, capture_output=True, text=True, timeout=15)
            calls = [json.loads(line) for line in (root / "calls").read_text().splitlines()] if (root / "calls").exists() else []
            return result, calls

    def test_all_twelve_slots_admit_at_600_second_cadence(self) -> None:
        result, calls = self.run_chain()
        self.assertEqual(result.returncode, 0, result.stderr)
        python = [call for call in calls if call["name"] == "python3"]
        self.assertEqual(len(python), 13)
        self.assertIn("--session-kind", python[0]["args"])
        self.assertIn("derivation", python[0]["args"])
        self.assertEqual(python[0]["args"][python[0]["args"].index("--slot-count") + 1], "12")
        self.assertEqual([call["time"] for call in python[1:]], list(range(600, 7800, 600)))
        self.assertEqual(calls[0], {"name": "sleep", "args": ["600"], "time": 0})
        for index, call in enumerate(python[1:], 1):
            self.assertIn("--derivation-only", call["args"])
            self.assertIn(f"d{index:02d}", call["args"])
            self.assertIn("ac_high_power", call["args"])

    def test_window_exhausted_refuses_next_slot_and_aborts_once(self) -> None:
        result, calls = self.run_chain(end=1800)
        self.assertEqual(result.returncode, 0, result.stderr)
        python = [call for call in calls if call["name"] == "python3"]
        self.assertEqual(len(python), 4)  # open, d01, d02, abort
        self.assertEqual(python[-1]["args"][-2:], ["--reason", "window_exhausted"])
        self.assertIn("abort-session", python[-1]["args"])
        self.assertNotIn("d03", str(python))

    def test_slot_count_override_and_writer_error_stop(self) -> None:
        result, calls = self.run_chain(slots="2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len([c for c in calls if c["name"] == "python3"]), 3)
        result, calls = self.run_chain(fail="d02")
        self.assertEqual(result.returncode, 7)
        self.assertNotIn("d03", str(calls))

    def test_invalid_slot_count_refuses_before_settle_or_reservation(self) -> None:
        for slots in ("0", "-1", "text"):
            with self.subTest(slots=slots):
                result, calls = self.run_chain(slots=slots)
                self.assertEqual(result.returncode, 64, result.stderr)
                self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
