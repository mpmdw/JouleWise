"""Defect-shaped desk-watch, chain skeleton, and prepare-candidate regressions.

Seat S5 owns the ``check`` desk-watch and chain-skeleton classes below; seat S4
appends ``PrepareCandidateTest``, which builds synthetic mixed-epoch ledgers
under ``tests/fixtures/epoch_bootstrap`` and touches no production config, no
real ledger, and no capture.
"""

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

from decimal import Decimal
import math

from joulewise.calibration_bracketing import (
    _registered_generation_row_is_complete,
    load_calibration_acceptance_bound,
)
from joulewise.calibration_ledger import SESSION_KIND_BRACKET
from tests.fixtures.epoch_bootstrap.build import Slot, build_derivation_ledger


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/d117_v2_production/issued"
CHAIN = ROOT / "scripts/night_chains/calibration_derivation_only.zsh"

D125_REFERENCE = "D-125 cl.2 as ruled at cold gate 46 R-b V7"
PREREGISTRATION = (
    ROOT / "configs" / "calibration" / "preregistration_d079_epoch_25g83_rev1.md"
)
R6 = (
    ROOT / "configs" / "calibration"
    / "calibration_acceptance_d079_v2_n17_r6.json"
)
SESSION = "derivation-night-1"


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

    def test_production_defaults_and_required_destination(self) -> None:
        """`check` keeps its production defaults; `prepare-candidate` has none.

        Seat S4 replaced the stub.  The destination and the pre-registration are
        REQUIRED arguments precisely so the tool can never default to writing
        into `configs/calibration`: issuing is the D-138 transaction's act.
        """

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
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("--out", result.stderr)
        self.assertIn("--preregistration", result.stderr)

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
    elif "recover_calibration_ledger.py" in args[0]:
        if "readiness" in args and os.environ.get("FAIL_READINESS"):
            sys.exit(3)
    elif "reserve_calibration_window_bracket.py" not in args[0]:
        sys.exit(99)
else:
    sys.exit(98)
'''

    INPUT_FILES = ("plan.json", "epoch.json", "t1.json", "ledger.jsonl", "head.json")

    def run_chain(
        self, *, end: int = 10000, slots: str | None = None, fail: str = "",
        capture: int = 480, absent_input: str = "", fail_readiness: bool = False,
        knobs: dict[str, str] | None = None,
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
                "FAIL_READINESS": "1" if fail_readiness else "",
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
            env.update(knobs or {})
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
        self.assertEqual(len(python), 14)
        # G2-a order: pre-reserve readiness, then the reservation, then the ONE
        # settle, then the captures.
        self.assertIn("recover_calibration_ledger.py", calls[0]["args"][0])
        self.assertEqual(calls[0]["args"][calls[0]["args"].index("--phase") + 1], "pre-reserve")
        self.assertIn("readiness", calls[0]["args"])
        self.assertIn("reserve_calibration_window_bracket.py", calls[1]["args"][0])
        self.assertIn("--session-kind", python[1]["args"])
        self.assertIn("derivation", python[1]["args"])
        self.assertEqual(python[1]["args"][python[1]["args"].index("--slot-count") + 1], "12")
        self.assertEqual([call["time"] for call in python[2:]], list(range(600, 7800, 600)))
        # The ONE settle: a single 600 s sleep, and the reservation is the last
        # machine action BEFORE it. Every later sleep only fills the cadence.
        sleeps = [call for call in calls if call["name"] == "sleep"]
        self.assertEqual(sleeps[0], {"name": "sleep", "args": ["600"], "time": 0})
        self.assertLess(calls.index(python[1]), calls.index(sleeps[0]))
        self.assertEqual([call["args"][0] for call in sleeps[1:]], ["120"] * 11)
        for index, call in enumerate(python[2:], 1):
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
                # No readiness, no reservation, no settle, no window time spent.
                self.assertEqual(calls, [])
                self.assertEqual(log, [])

    def test_unready_ledger_refuses_before_any_reservation(self) -> None:
        result, calls, log = self.run_chain(fail_readiness=True)
        self.assertEqual(result.returncode, 3, result.stderr)
        # Exactly the readiness call: nothing was reserved, nothing settled.
        self.assertEqual(len(calls), 1)
        self.assertIn("recover_calibration_ledger.py", calls[0]["args"][0])
        self.assertIn("readiness", calls[0]["args"])
        self.assertEqual(log, [])

    def test_zero_settle_or_cadence_refuses_before_readiness_or_settle(self) -> None:
        # A zero settle would collect with the operator's activity still in the
        # thermal state; a zero cadence would collapse the start-to-start
        # spacing the pre-registration declares. Both refuse as declarations.
        for knob in ("SETTLE_S", "SLOT_CADENCE_S"):
            with self.subTest(knob=knob):
                result, calls, log = self.run_chain(knobs={knob: "0"})
                self.assertEqual(result.returncode, 64, result.stderr)
                self.assertIn("must be positive", result.stderr)
                self.assertEqual(calls, [])
                self.assertEqual(log, [])

    def test_window_exhausted_refuses_next_slot_and_aborts_once(self) -> None:
        result, calls, log = self.run_chain(end=1800)
        self.assertEqual(result.returncode, 0, result.stderr)
        python = [call for call in calls if call["name"] == "python3"]
        self.assertEqual(len(python), 5)  # readiness, open, d01, d02, abort
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
        self.assertEqual(len(python), 4)  # readiness, open, d01, abort
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
        self.assertEqual(len(python), 4)  # readiness, open, d01, abort
        self.assertIn("slot_unused slot=d02 reason=window_exhausted", log)

    def test_first_slot_that_cannot_finish_aborts_with_no_capture(self) -> None:
        result, calls, log = self.run_chain(end=1000)
        self.assertEqual(result.returncode, 0, result.stderr)
        python = [call for call in calls if call["name"] == "python3"]
        self.assertEqual(len(python), 3)  # readiness, open, abort
        self.assertNotIn("validate_powermetrics_fiducial.py", str(python))
        self.assertEqual(log[-2:], [
            "slot_unused slot=d01 reason=window_exhausted",
            "session_abort reason=window_exhausted",
        ])

    def test_slot_count_override_and_writer_error_stop(self) -> None:
        result, calls, _log = self.run_chain(slots="2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len([c for c in calls if c["name"] == "python3"]), 4)
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

    def test_chain_header_pins_its_hand_written_and_unlanded_flag_warnings(self) -> None:
        source = CHAIN.read_text(encoding="utf-8")
        # Deleting either line loses a warning a future reader needs: that this
        # file is not regenerated from a runbook section, and that the writer
        # rejects every dNN slot name until seat S2 lands the declared list.
        self.assertIn(
            "# This file is HAND-WRITTEN and is NOT a generated region of\n"
            "# scripts/gen_g2_phase_d.py;",
            source,
        )
        self.assertIn(
            '#   validate_powermetrics_fiducial.py      --slot dNN — today the writer\'s --slot\n'
            '#   is choices=("pre","post") and REJECTS every d01..dNN name;',
            source,
        )

    def test_chain_readiness_call_puts_globals_before_the_subcommand_and_binds_the_night_ledger(self) -> None:
        """recover_calibration_ledger.py declares --ledger/--head-pin on its top-level parser; placed
        after `readiness` the real CLI exits 2 (delta re-audit 68 D-9). Dropping them silently retargets
        the check at DEFAULT_LEDGER_PATH instead of the night's ledger (D-10). The stubbed harness cannot
        see argparse, so the invocation shape is pinned in the source."""
        source = CHAIN.read_text(encoding="utf-8")
        self.assertIn(
            '"$PY" "$REPO/scripts/recover_calibration_ledger.py" \\\n'
            '    --ledger "$CALIBRATION_LEDGER" \\\n'
            '    --head-pin "$LEDGER_HEAD_PIN" \\\n'
            '    readiness \\\n'
            '    --phase pre-reserve',
            source,
        )


def _grid(count: int, start: str, step: str) -> list[str]:
    """A corpus whose spread is set BEFORE any statistic is computed."""

    return [str(Decimal(start) + Decimal(step) * index) for index in range(count)]


class PrepareCandidateTest(unittest.TestCase):
    """One temporary Git repository per corpus shape, built once."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        root = Path(cls._tmp.name)
        # n = 20 retained, range 0.0114 > the 0.010818 floor, maximum 0.0314
        # below r6's level screen: the ordinary admit case, df 19 (ODD).
        cls.wide = build_derivation_ledger(root / "wide", [Slot(v) for v in _grid(20, "0.0200", "0.0006")])
        # 17 retained: 17 valid-and-resolved, two ordinary-invalid, one valid
        # row the replay refuses.  df 16 (EVEN).
        seventeen = [Slot(v) for v in _grid(17, "0.0200", "0.0007")]
        seventeen.append(Slot("0.0250", disposition="ordinary-invalid"))
        seventeen.append(Slot("0.0251", disposition="ordinary-invalid"))
        seventeen.append(Slot("0.0252", unresolved_detail="affine_clock_fit_empty"))
        cls.seventeen = build_derivation_ledger(root / "seventeen", seventeen)
        # A corpus so tight that its own Q99 falls below the 0.010818 screen
        # floor: S = 0.010818 and the predecessor ceiling 0.0101648... cannot
        # rescue S < C.
        cls.tight = build_derivation_ledger(root / "tight", [Slot(v) for v in _grid(20, "0.0250", "0.0000005")])
        # Two retained members above r6's level screen 0.032898493715362.
        challenged = [Slot(v) for v in _grid(18, "0.0200", "0.0006")]
        challenged.extend([Slot("0.0330"), Slot("0.0340")])
        cls.challenged = build_derivation_ledger(root / "challenged", challenged)
        # A bimodal corpus: range 0.0100 is BELOW the 0.010818 floor (so the
        # floor wins the screen) while the spread keeps Q99 well above it (so
        # the ceiling still clears the screen and the candidate emits).
        cls.floored = build_derivation_ledger(
            root / "floored",
            [Slot("0.0200") for _ in range(10)] + [Slot("0.0300") for _ in range(10)],
        )
        # A bracket-kind session may never serve as a derivation registration.
        cls.bracket = build_derivation_ledger(
            root / "bracket",
            [Slot("0.0200"), Slot("0.0300")],
            session_kind=SESSION_KIND_BRACKET,
        )
        # A valid row whose replay refused for a mechanism nobody registered.
        unregistered = [Slot(v) for v in _grid(19, "0.0200", "0.0006")]
        unregistered.append(Slot("0.0300", unresolved_detail="numeric_padding_insufficient"))
        cls.unregistered = build_derivation_ledger(root / "unregistered", unregistered)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def setUp(self) -> None:
        self.out_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.out_dir.cleanup)
        self.out = Path(self.out_dir.name) / "candidate.json"

    def run_issuer(self, fixture: dict[str, Path], *extra: str, omit_d125: bool = False) -> int:
        """Run the command and keep its printed reason for assertion."""

        argv = [
            "prepare-candidate",
            "--ledger", str(fixture["ledger"]),
            "--head-pin", str(fixture["pin"]),
            "--repo-root", str(fixture["root"]),
            "--preregistration", str(PREREGISTRATION),
            "--predecessor-acceptance", str(R6),
            "--registration-session-id", SESSION,
            "--out", str(self.out),
        ]
        if not omit_d125:
            argv += ["--d125-ruling", D125_REFERENCE]
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = issuer.main(argv + list(extra))
        self.printed = stream.getvalue()
        return code

    def assert_refused(self, code: int, reason: str) -> None:
        """A refusal is its REASON, not merely a non-zero code.

        Asserting the code alone lets an upstream fence stand in for the clause
        under test, which is exactly the masking the isolation rule forbids.
        """

        self.assertEqual(code, 3)
        self.assertIn(reason, self.printed)
        self.assertFalse(self.out.exists())

    def payload(self) -> dict:
        return json.loads(self.out.read_text(encoding="utf-8"))

    # ---- admit ---------------------------------------------------------

    def test_retained_corpus_at_the_floor_emits_a_not_issued_candidate(self) -> None:
        """ADMIT: n = 20 >= 19 passes the floor clause in `_prepare_candidate`."""

        self.assertEqual(self.run_issuer(self.wide), 0)
        payload = self.payload()
        self.assertEqual(payload["derivation_corpus"]["n"], 20)
        self.assertIs(payload["candidate_not_issued"], True)
        self.assertEqual(payload["issuance"]["status"], "candidate_not_issued")
        self.assertIs(payload["issuance"]["claim_eligible"], False)
        self.assertEqual(payload["ledger_cutoff"]["sequence"], 82)
        self.assertEqual(len(payload["prior_observation_set"]["epoch_catalog"]), 2)
        self.assertEqual(len(payload["prior_observation_set"]["observations"]), 20)
        self.assertEqual(payload["prospective_rederivation"]["triggers"],
                         json.loads(R6.read_text())["prospective_rederivation"]["triggers"])
        self.assertEqual(len(payload["derivation_sha256"]), 64)

    def test_derivation_digest_moves_with_an_operative_lexeme(self) -> None:
        """`derivation_sha256` seals the decimal lexemes and rounding rules."""

        self.assertEqual(self.run_issuer(self.wide), 0)
        payload = self.payload()
        baseline = payload["derivation_sha256"]
        self.assertEqual(issuer.derivation_sha256(payload), baseline)
        payload["decimal_derivation"]["ratified_operatives"]["bracket_screen_s"] = "0.011401"
        self.assertNotEqual(issuer.derivation_sha256(payload), baseline)

    # ---- the corpus-size floor (addendum A-2) ---------------------------

    def test_seventeen_member_corpus_refuses_without_the_ed_ruling(self) -> None:
        """`_prepare_candidate` floor clause: n = 17 < 19 and no --ed-ruling."""

        self.assert_refused(self.run_issuer(self.seventeen), "below the required floor 19")

    def test_seventeen_member_corpus_emits_with_the_ed_ruling(self) -> None:
        """The SAME corpus emits once Ed's written ruling lowers the floor."""

        self.assertEqual(
            self.run_issuer(
                self.seventeen,
                "--minimum-corpus-size", "17",
                "--ed-ruling", "Ed email 2026-09-10: n = 17 acceptable",
            ),
            0,
        )
        payload = self.payload()
        self.assertEqual(payload["derivation_corpus"]["n"], 17)
        self.assertEqual(
            payload["decimal_derivation"]["two_draw_prediction_derivation"][
                "degrees_of_freedom"
            ],
            16,
        )

    def test_lowering_the_floor_without_a_ruling_refuses_before_reading_the_ledger(self) -> None:
        """The --ed-ruling clause fires on a corpus that WOULD otherwise pass."""

        self.assert_refused(
            self.run_issuer(self.wide, "--minimum-corpus-size", "17"),
            "requires --ed-ruling",
        )

    def test_excluded_member_is_named_not_silently_dropped(self) -> None:
        """`_select_members` records the replay refusal with its mechanism."""

        self.run_issuer(self.seventeen, "--minimum-corpus-size", "17",
                        "--ed-ruling", "Ed email 2026-09-10")
        excluded = self.payload()["derivation_notes"]["excluded_members"]
        self.assertEqual(len(excluded), 1)
        self.assertEqual(excluded[0]["reason"], "affine_clock_fit_empty")
        self.assertEqual(
            set(excluded[0]),
            {"member_id", "manifest_sha256", "instrument_evidence_sha256", "reason"},
        )

    def test_unregistered_exclusion_mechanism_refuses(self) -> None:
        """`_select_members` never invents an exclusion class."""

        self.assert_refused(
            self.run_issuer(self.unregistered),
            "unregistered exclusion mechanism 'numeric_padding_insufficient'",
        )

    def test_primary_value_disagreeing_with_the_ledger_row_refuses(self) -> None:
        """`_select_members` cross-checks the bundle lexeme against the row."""

        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        # A perturbation in the last place: everything downstream still
        # passes, so only the cross-check itself can refuse this input.
        rows[3] = Slot(rows[3].b_fiducial_s, evidence_lexeme="0.02180000001")
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "skew", rows)
            code = self.run_issuer(fixture)
        self.assert_refused(code, "does not match the ledger row's exact bound lexeme")

    def test_a_non_v3_anchor_is_not_an_anchor_v3_replay(self) -> None:
        """`anchor_v3_replay_outcome` refuses a resolved anchor of another method.

        The row is `valid` and its anchor says RESOLVED; only the method test
        can see that the resolution came from the superseded v2 estimator.
        """

        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        rows[5] = Slot(
            rows[5].b_fiducial_s,
            anchor_method="powermetrics_native_second_censored_intersection_v1",
        )
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "v2anchor", rows)
            code = self.run_issuer(fixture)
        self.assert_refused(code, "unregistered exclusion mechanism 'anchor_method_not_v3'")

    # ---- the D-125 reference (ruling 46 V7) -----------------------------

    def test_missing_d125_ruling_refuses(self) -> None:
        """`_prepare_candidate` refuses to settle D-125 implicitly."""

        self.assert_refused(
            self.run_issuer(self.wide, omit_d125=True), "d125_ruling reference absent"
        )

    def test_the_d125_reference_is_recorded_on_the_row(self) -> None:
        self.run_issuer(self.wide)
        self.assertEqual(
            self.payload()["registered_generation_row"]["d125_ruling"], D125_REFERENCE
        )

    # ---- the ceiling relation (D-126 cl.3, addendum A-3) ----------------

    def test_screen_at_or_above_the_ceiling_refuses(self) -> None:
        """`successor_screen_exceeds_budget_ceiling`: Q99 below the floor."""

        self.assert_refused(
            self.run_issuer(self.tight), "successor_screen_exceeds_budget_ceiling"
        )

    def test_the_ceiling_is_the_max_of_predecessor_and_own_q99(self) -> None:
        """The emitted ceiling transcribes D-125 cl.2 exactly."""

        self.run_issuer(self.wide)
        row = self.payload()["registered_generation_row"]
        predecessor = Decimal(row["predecessor_ceiling_s"])
        own = Decimal(row["prediction_99_two_draw_s"])
        self.assertEqual(
            Decimal(row["operatives"]["maximum_budgetable_drift_s"]),
            max(predecessor, own),
        )
        self.assertEqual(
            predecessor,
            Decimal(
                json.loads(R6.read_text())["decimal_derivation"]["ratified_operatives"][
                    "maximum_budgetable_drift_s"
                ]
            ),
        )
        self.assertLess(
            Decimal(row["operatives"]["bracket_screen_s"]),
            Decimal(row["operatives"]["maximum_budgetable_drift_s"]),
        )

    # ---- the screen challenge (ruling 46 R-b) ---------------------------

    def test_two_members_over_the_prior_level_screen_refuse(self) -> None:
        """The screen-challenge clause halts issuance for Ed."""

        self.assert_refused(self.run_issuer(self.challenged), "screen challenge: 2 retained members")

    def test_one_member_over_the_prior_level_screen_is_recorded_and_admits(self) -> None:
        """One challenged member is a DIAGNOSTIC, never a membership edit."""

        one = [Slot(v) for v in _grid(19, "0.0200", "0.0006")]
        one.append(Slot("0.0330"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "one", one)
            self.assertEqual(self.run_issuer(fixture), 0)
        outcomes = self.payload()["derivation_notes"]["rule_outcomes"]
        self.assertEqual(outcomes["screen_challenge_member_count"], 1)
        self.assertEqual(len(self.payload()["derivation_corpus"]["members"]), 20)

    # ---- the registration (ruling 46 R-a A7) ----------------------------

    def test_bracket_kind_session_is_not_a_derivation_registration(self) -> None:
        """`_registration_observations` refuses a bracket-kind session."""

        self.assert_refused(
            self.run_issuer(self.bracket, "--minimum-corpus-size", "17", "--ed-ruling", "Ed"),
            "is kind 'bracket', not a derivation session",
        )

    # ---- the quantile implementation (both parities) --------------------

    def test_quantiles_reproduce_known_values_for_even_and_odd_df(self) -> None:
        """`student_t_quantile` on df 16 (r6's pins), 18 and 19."""

        cases = {
            (16, "0.975"): "2.11990529922125467446",
            (16, "0.995"): "2.92078162242509999197",
            (18, "0.975"): "2.10092204024103848806",
            (18, "0.995"): "2.87844047273860811781",
            (19, "0.975"): "2.09302405440830976918",
            (19, "0.995"): "2.86093460646497919208",
        }
        for (df, probability), expected in cases.items():
            with self.subTest(df=df, p=probability):
                value = issuer.student_t_quantile(probability, df)
                self.assertEqual(
                    str(+value.quantize(Decimal(1).scaleb(-20))), expected
                )

    def test_r6_predictions_are_reproduced_from_its_own_sd(self) -> None:
        """The two-draw rule is r6's, verbatim, including the binary64 step."""

        artifact = json.loads(R6.read_text())
        statistics = artifact["decimal_derivation"]["source_statistics"]
        sd = statistics["sample_sd_presentation_s"]["value"]
        self.assertEqual(
            issuer.two_draw_prediction_lexeme(issuer.student_t_quantile("0.975", 16), sd),
            statistics["prediction_95_two_draw_s"],
        )
        self.assertEqual(
            issuer.two_draw_prediction_lexeme(issuer.student_t_quantile("0.995", 16), sd),
            statistics["prediction_99_two_draw_s"],
        )

    def test_pi_constant_agrees_with_the_platform_double(self) -> None:
        """A gross typo in the odd-df Beta normalizer cannot travel.

        The real fence on the tail digits is the odd-df quantile test above: a
        wrong pi moves t(p, 19) in the fifteenth place and that test fails.
        """

        self.assertEqual(float(issuer._PI), math.pi)
        self.assertEqual(len(str(issuer._PI).split(".")[1]), 100)

    # ---- the candidate is not authority ---------------------------------

    def test_emitted_candidate_is_refused_by_the_production_loader(self) -> None:
        """`load_calibration_acceptance_bound` never authenticates a candidate."""

        self.run_issuer(self.wide)
        self.assertIsNone(load_calibration_acceptance_bound(self.out))

    def test_emitted_row_satisfies_the_registered_row_validator(self) -> None:
        """The row S3's table would carry passes `_registered_generation_row_is_complete`."""

        self.run_issuer(self.wide)
        row = dict(self.payload()["registered_generation_row"])
        # JSON carries lists; S3's registry carries tuples.  Transport only.
        row["epoch_catalog_ids"] = tuple(row["epoch_catalog_ids"])
        row["registration_session_ids"] = tuple(row["registration_session_ids"])
        self.assertTrue(_registered_generation_row_is_complete(row))

    def test_emitted_row_refuses_when_its_predecessor_ceiling_is_rebased(self) -> None:
        """The row's lineage fence is live, not decorative."""

        self.run_issuer(self.wide)
        row = dict(self.payload()["registered_generation_row"])
        row["epoch_catalog_ids"] = tuple(row["epoch_catalog_ids"])
        row["registration_session_ids"] = tuple(row["registration_session_ids"])
        row["predecessor_ceiling_s"] = "0.0095"
        self.assertFalse(_registered_generation_row_is_complete(row))

    # ---- the screen-rule seam (reported to S3) --------------------------

    def test_floor_bound_screen_names_an_unregistered_rule(self) -> None:
        """SEAM: the floor branch is honest and S3 has registered no name."""

        self.assertEqual(self.run_issuer(self.floored), 0)
        payload = self.payload()
        outcomes = payload["derivation_notes"]["rule_outcomes"]
        self.assertIs(outcomes["screen_floor_bound"], True)
        self.assertEqual(
            payload["registered_generation_row"]["screen_rule"],
            issuer.SCREEN_RULE_FLOORED_RANGE_ENVELOPE,
        )
        self.assertIs(outcomes["screen_rule_registered_in_validator"], False)
        row = dict(payload["registered_generation_row"])
        row["epoch_catalog_ids"] = tuple(row["epoch_catalog_ids"])
        row["registration_session_ids"] = tuple(row["registration_session_ids"])
        self.assertFalse(_registered_generation_row_is_complete(row))


if __name__ == "__main__":
    unittest.main()
