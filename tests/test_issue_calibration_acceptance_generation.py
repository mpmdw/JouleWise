"""Defect-shaped desk-watch and non-live chain skeleton regressions."""

from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import re
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


def parse_watch_table(output: str) -> dict[str, tuple[str, str, str]]:
    """Return field -> (expected, observed, status) from the printed table."""

    rows: dict[str, tuple[str, str, str]] = {}
    for line in output.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0] in issuer.WATCH_FIELDS:
            rows[parts[0]] = (parts[1], parts[2], parts[3])
    return rows


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
        self.epoch = json.loads(self.acceptance.read_bytes())["identity_epoch"]
        self.t1 = json.loads(self.ledger.read_text().splitlines()[-1])["t1_bindings"]
        self.observed = {field: self.epoch[field] for field in ("os_build", "hardware_model")}
        self.observed.update(
            {field: self.t1[field] for field in ("powermetrics_sha256", "mlx_version")}
        )
        # The real parser, hash chain, receipt shapes, custody and acceptance
        # authentication run. Only Git's committed-pin byte source is a fixture.
        self.pin_source = mock.patch(
            "joulewise.calibration_ledger._committed_pin_bytes",
            return_value=self.pin.read_bytes(),
        )
        self.pin_source.start()
        self.addCleanup(self.pin_source.stop)

    def invoke_check(self) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            rc = issuer.main([
                "check", "--ledger", str(self.ledger), "--head-pin", str(self.pin),
                "--acceptance", str(self.acceptance),
            ])
        return rc, output.getvalue()

    def run_check(self, **changes: object) -> tuple[int, str]:
        with mock.patch.object(issuer, "observe_machine", return_value=self.observed | changes):
            return self.invoke_check()

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
        self.assertNotIn(
            "powermetrics_sha256",
            json.loads(self.acceptance.read_bytes())["identity_epoch"],
        )
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
        older = next(
            row for key, row in ISSUED_ACCEPTANCE_REGISTRY.items()
            if key != issuer.ACTIVE_ACCEPTANCE_ID
        )
        self.acceptance.write_bytes(Path(older["path"]).read_bytes())
        rc, output = self.run_check()
        self.assertEqual(rc, 3, output)
        self.assertIn("acceptance: invalid or not ACTIVE", output)

    def test_acceptance_without_identity_epoch_refuses_instead_of_raising(self) -> None:
        # The epoch is the whole comparison baseline; a shape the loader admits
        # but the watch cannot read must refuse, never raise at the desk.
        bound = json.loads(self.acceptance.read_bytes())
        bound.pop("identity_epoch")
        with mock.patch.object(issuer, "load_calibration_acceptance_bound", return_value=bound):
            rc, output = self.run_check()
        self.assertEqual(rc, 3, output)
        self.assertIn("acceptance: invalid or not ACTIVE", output)

    def test_ledger_hash_mutation_refuses(self) -> None:
        self.ledger.write_text(
            self.ledger.read_text().replace('"mlx_version":"0.31.2"', '"mlx_version":"0.31.3"')
        )
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
        with mock.patch.object(
            issuer, "WATCH_FIELDS", ("os_build", "hardware_model", "mlx_version")
        ):
            with self.assertRaises(AssertionError):
                self.test_binary_hash_alone_refuses_even_when_epoch_matches()

    def test_production_defaults_and_stub(self) -> None:
        args = issuer.build_parser().parse_args(["check"])
        self.assertEqual(args.ledger, issuer.DEFAULT_LEDGER_PATH)
        self.assertEqual(args.head_pin, issuer.DEFAULT_HEAD_PIN_PATH)
        self.assertEqual(args.acceptance, issuer.DEFAULT_ACCEPTANCE_BOUND_PATH)
        self.assertEqual(args.acceptance.name, "calibration_acceptance_d079_v2_n17_r6.json")
        result = subprocess.run(
            [
                sys.executable, "-B",
                str(ROOT / "scripts/issue_calibration_acceptance_generation.py"),
                "prepare-candidate",
            ],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 64, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "not implemented: waits for seat S3's generation-row schema and the corpus",
        )

    def test_machine_observation_reads_sysctl_hash_and_mlx(self) -> None:
        binary = self.root / "powermetrics"
        binary.write_bytes(b"fixture sampler bytes; never execute")
        with mock.patch.object(issuer, "POWERMETRICS_PATH", binary):
            with mock.patch.object(issuer.subprocess, "run", side_effect=[
                SimpleNamespace(stdout="25G83\n"), SimpleNamespace(stdout="Mac15,9\n"),
            ]) as run:
                with mock.patch.object(
                    issuer.importlib, "import_module",
                    return_value=SimpleNamespace(__version__="0.31.2"),
                ) as imp:
                    observed = issuer.observe_machine()
        self.assertEqual(observed, {
            "os_build": "25G83", "hardware_model": "Mac15,9", "mlx_version": "0.31.2",
            "powermetrics_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        })
        # Absolute probe path: a PATH-resolved sysctl could report an identity
        # this machine does not have.
        self.assertEqual([call.args[0] for call in run.call_args_list], [
            ["/usr/sbin/sysctl", "-n", "kern.osversion"],
            ["/usr/sbin/sysctl", "-n", "hw.model"],
        ])
        imp.assert_called_once_with("mlx.core")

    def test_unavailable_machine_inputs_do_not_crash(self) -> None:
        with mock.patch.object(issuer, "POWERMETRICS_PATH", self.root / "missing"):
            with mock.patch.object(issuer.subprocess, "run", side_effect=OSError("missing")):
                with mock.patch.object(
                    issuer.importlib, "import_module", side_effect=ImportError("missing")
                ):
                    self.assertEqual(issuer.observe_machine(), dict.fromkeys(issuer.WATCH_FIELDS))

    @unittest.skipUnless(
        sys.platform == "darwin" and issuer.SYSCTL_PATH.exists(),
        "live identity probes need macOS sysctl",
    )
    def test_live_probes_report_this_machine_against_the_active_epoch(self) -> None:
        # Real probes, fixture ledger and pin: the only non-deterministic input
        # is this machine's own identity, and every assertion is derived from
        # the live reading rather than pinned to one build.
        live = issuer.observe_machine()
        rc, output = self.invoke_check()
        rows = parse_watch_table(output)
        self.assertEqual(set(rows), set(issuer.WATCH_FIELDS), output)

        self.assertIsInstance(live["os_build"], str)
        self.assertTrue(live["os_build"])
        self.assertEqual(rows["os_build"][0], self.epoch["os_build"])
        self.assertEqual(rows["os_build"][1], live["os_build"])
        if live["os_build"] == self.epoch["os_build"]:
            self.assertEqual(rows["os_build"][2], "match")
        else:
            # The truth on this machine today: 25G83 observed against the r6
            # epoch's 25F84. The watch must name the field and refuse.
            self.assertEqual(rows["os_build"][2], "MISMATCH")
            self.assertEqual(rc, 3, output)
            self.assertIn("os_build", output.splitlines()[-1])

        if issuer.POWERMETRICS_PATH.exists():
            self.assertEqual(
                live["powermetrics_sha256"],
                hashlib.sha256(issuer.POWERMETRICS_PATH.read_bytes()).hexdigest(),
            )
            self.assertEqual(rows["powermetrics_sha256"][0], self.t1["powermetrics_sha256"])
            self.assertEqual(rows["powermetrics_sha256"][1], live["powermetrics_sha256"])


@unittest.skipUnless(shutil.which("zsh"), "zsh not installed")
class DerivationChainSkeletonTests(unittest.TestCase):
    """Drive the chain on a fake clock; no sampler and no ledger tool runs."""

    FAKE = "#!" + sys.executable + "\n" + '''
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
        clock.write_text(str(now + int(os.environ["FAKE_CAPTURE_S"])))
    elif not any(tool in args[0] for tool in ("reserve_calibration_window_bracket.py", "recover_calibration_ledger.py")):
        sys.exit(99)
else:
    sys.exit(98)
'''

    INPUT_FILES = ("plan.json", "epoch.json", "t1.json", "ledger.jsonl", "head.json")

    def run_chain(
        self, *, end: int = 10000, slots: str | None = None, fail: str = "",
        capture: int = 480, absent_input: str = "",
    ) -> tuple[subprocess.CompletedProcess, list[dict], list[str]]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "clock").write_text("0")
            for name in ("date", "sleep", "python3"):
                path = root / name
                path.write_text(self.FAKE)
                path.chmod(0o755)
            for name in self.INPUT_FILES:
                if name != absent_input:
                    (root / name).write_text("{}\n")
            custody = root / "custody"
            env = os.environ.copy()
            for knob in (
                "SLOT_COUNT", "SETTLE_S", "SLOT_CADENCE_S", "SLOT_CAPTURE_BUDGET_S",
            ):
                env.pop(knob, None)
            env.update({
                # Real PATH with injected absolute binaries: a bare sleep, date
                # or python3 left in the chain would reach the real one and hang
                # or escape the fake clock instead of being silently intercepted.
                "PATH": "/bin:/usr/bin",
                "FAKE_ROOT": str(root), "FAIL_SLOT": fail, "FAKE_CAPTURE_S": str(capture),
                "PY": str(root / "python3"), "SLEEP": str(root / "sleep"),
                "DATE": str(root / "date"),
                "SESSION_ID": "fixture-session", "WINDOW_ID": "fixture-window",
                "PLAN_ID": "fixture-plan", "PLAN_SHA256": "a" * 64,
                "PLAN": str(root / "plan.json"),
                "EVIDENCE_ROOT_ID": "fixture-root", "RUNS_ROOT": str(root / "runs"),
                "WINDOW_CUSTODY_ROOT": str(custody),
                "CALIBRATION_LEDGER": str(root / "ledger.jsonl"),
                "LEDGER_HEAD_PIN": str(root / "head.json"),
                "IDENTITY_EPOCH_JSON": str(root / "epoch.json"),
                "T1_BINDINGS_JSON": str(root / "t1.json"),
                "WINDOW_END_EPOCH_S": str(end),
            })
            if slots is not None:
                env["SLOT_COUNT"] = slots
            result = subprocess.run(
                [shutil.which("zsh"), str(CHAIN)], env=env,
                capture_output=True, text=True, timeout=60,
            )
            calls_path = root / "calls"
            calls = (
                [json.loads(line) for line in calls_path.read_text().splitlines()]
                if calls_path.exists() else []
            )
            log_path = custody / "operator_logs/derivation-chain.log"
            log = (
                [line.split(" ", 1)[1] for line in log_path.read_text().splitlines()]
                if log_path.exists() else []
            )
            return result, calls, log

    def test_all_twelve_slots_admit_at_600_second_cadence(self) -> None:
        result, calls, _log = self.run_chain()
        self.assertEqual(result.returncode, 0, result.stderr)
        python = [call for call in calls if call["name"] == "python3"]
        self.assertEqual(len(python), 13)
        self.assertIn("--session-kind", python[0]["args"])
        self.assertIn("derivation", python[0]["args"])
        self.assertEqual(python[0]["args"][python[0]["args"].index("--slot-count") + 1], "12")
        self.assertEqual([call["time"] for call in python[1:]], list(range(600, 7800, 600)))
        # The ONE settle: a single 600 s sleep, and the reservation is the last
        # machine action BEFORE it (pinned G2-a order). Every later sleep only
        # fills the start-to-start cadence.
        sleeps = [call for call in calls if call["name"] == "sleep"]
        self.assertEqual(sleeps[0], {"name": "sleep", "args": ["600"], "time": 0})
        self.assertIn("reserve_calibration_window_bracket.py", calls[0]["args"][0])
        self.assertLess(calls.index(python[0]), calls.index(sleeps[0]))
        self.assertEqual([call["args"][0] for call in sleeps[1:]], ["120"] * 11)
        for index, call in enumerate(python[1:], 1):
            self.assertIn("--derivation-only", call["args"])
            self.assertIn("--allow-live", call["args"])
            self.assertIn(f"d{index:02d}", call["args"])
            self.assertIn("ac_high_power", call["args"])

    def test_operator_log_records_each_lifecycle_transition(self) -> None:
        _result, _calls, log = self.run_chain(slots="2")
        # chain_start carries all three timing knobs, so a night's log states
        # the cadence it actually ran rather than the one someone assumed.
        self.assertEqual(log, [
            "session_open kind=derivation slots=2",
            "chain_start session=fixture-session window=fixture-window slots=2"
            " settle_s=600 slot_cadence_s=600 slot_capture_budget_s=480",
            "settle_complete settle_s=600",
            "slot_start slot=d01", "slot_end slot=d01",
            "slot_start slot=d02", "slot_end slot=d02",
            "derivation_night_complete slots=2",
        ])

    def test_missing_file_input_refuses_before_reservation_or_settle(self) -> None:
        for absent in self.INPUT_FILES:
            with self.subTest(absent=absent):
                result, calls, log = self.run_chain(absent_input=absent)
                self.assertEqual(result.returncode, 66, result.stderr)
                self.assertIn("derivation_chain_input_missing: ", result.stderr)
                self.assertIn(absent, result.stderr)
                # No reservation, no settle, no window time spent.
                self.assertEqual(calls, [])
                self.assertEqual(log, [])

    def test_window_exhausted_refuses_next_slot_and_aborts_once(self) -> None:
        result, calls, log = self.run_chain(end=1800)
        self.assertEqual(result.returncode, 0, result.stderr)
        python = [call for call in calls if call["name"] == "python3"]
        self.assertEqual(len(python), 4)  # open, d01, d02, abort
        self.assertEqual(python[-1]["args"][-2:], ["--reason", "window_exhausted"])
        self.assertIn("abort-session", python[-1]["args"])
        self.assertNotIn("d03", str(python))
        self.assertEqual(log[-3:], [
            "slot_end slot=d02",
            "slot_unused slot=d03 reason=window_exhausted",
            "session_abort reason=window_exhausted",
        ])

    def test_slot_that_cannot_finish_is_never_started(self) -> None:
        # d02 could START at 1200 inside a window ending at 1500, but its 480 s
        # capture would run 180 s past the agent-free end. Judging startability
        # alone (the defect) overruns the window; judge completability.
        result, calls, log = self.run_chain(end=1500)
        self.assertEqual(result.returncode, 0, result.stderr)
        python = [call for call in calls if call["name"] == "python3"]
        self.assertEqual(len(python), 3)  # open, d01, abort
        captures = [call for call in python if "validate_powermetrics_fiducial.py" in call["args"][0]]
        self.assertEqual([call["args"][call["args"].index("--slot") + 1] for call in captures], ["d01"])
        self.assertIn("slot_unused slot=d02 reason=window_exhausted", log)

    def test_overrunning_capture_stops_the_next_slot_after_the_cadence_wait(self) -> None:
        # A 700 s capture overruns the 600 s cadence, so d02's turn arrives with
        # the clock already at 1300: the PRE-wait check passes (next_start 1200
        # + 480 <= 1700) and only the POST-wait check sees 1300 + 480 > 1700.
        # Deleting that second check leaves every other test green.
        result, calls, log = self.run_chain(end=1700, capture=700)
        self.assertEqual(result.returncode, 0, result.stderr)
        python = [call for call in calls if call["name"] == "python3"]
        captures = [
            call for call in python
            if "validate_powermetrics_fiducial.py" in call["args"][0]
        ]
        self.assertEqual(
            [call["args"][call["args"].index("--slot") + 1] for call in captures], ["d01"]
        )
        self.assertEqual(len(python), 3)  # open, d01, abort
        self.assertIn("slot_unused slot=d02 reason=window_exhausted", log)

    def test_first_slot_that_cannot_finish_aborts_with_no_capture(self) -> None:
        result, calls, log = self.run_chain(end=1000)
        self.assertEqual(result.returncode, 0, result.stderr)
        python = [call for call in calls if call["name"] == "python3"]
        self.assertEqual(len(python), 2)  # open, abort
        self.assertNotIn("validate_powermetrics_fiducial.py", str(python))
        self.assertEqual(log[-2:], [
            "slot_unused slot=d01 reason=window_exhausted",
            "session_abort reason=window_exhausted",
        ])

    def test_slot_count_override_and_writer_error_stop(self) -> None:
        result, calls, _log = self.run_chain(slots="2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len([c for c in calls if c["name"] == "python3"]), 3)
        result, calls, log = self.run_chain(fail="d02")
        self.assertEqual(result.returncode, 7)
        self.assertNotIn("d03", str(calls))
        # A failed capture stops the chain; it never aborts or retries in-window.
        self.assertNotIn("abort-session", str(calls))
        self.assertEqual(log[-1], "slot_start slot=d02")

    def test_invalid_slot_count_refuses_before_settle_or_reservation(self) -> None:
        for slots in ("0", "-1", "text"):
            with self.subTest(slots=slots):
                result, calls, log = self.run_chain(slots=slots)
                self.assertEqual(result.returncode, 64, result.stderr)
                self.assertEqual(calls, [])
                self.assertEqual(log, [])

    def test_chain_source_carries_no_pack_probe_or_git_step(self) -> None:
        source = CHAIN.read_text(encoding="utf-8")
        self.assertIn(
            "# SKELETON: pending S1/S2 flag landing; not to be pinned in a plan"
            " until the integration replay\n",
            source,
        )
        self.assertIn("set -euo pipefail\n", source)
        code = "\n".join(
            line for line in source.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
        for forbidden in (r"\bgit\b", r"\bpack\b", r"generate_g2a_probe_inputs", r"launch_window"):
            with self.subTest(forbidden=forbidden):
                self.assertIsNone(re.search(forbidden, code), forbidden)
        self.assertEqual(code.count("\nsettle\n"), 1)
        self.assertTrue(os.access(CHAIN, os.X_OK))


if __name__ == "__main__":
    unittest.main()
