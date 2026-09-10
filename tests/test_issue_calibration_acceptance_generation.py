"""Defect-shaped desk-watch, chain skeleton, and prepare-candidate regressions.

Seat S5 owns the ``check`` desk-watch and chain-skeleton classes below; seat S4
appends ``PrepareCandidateTest``, which builds synthetic mixed-epoch ledgers
under ``tests/fixtures/epoch_bootstrap`` and touches no production config, no
real ledger, and no capture.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
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

from decimal import Decimal, localcontext
import math

from joulewise.calibration_bracketing import (
    _D102_GENERATION_DERIVATIONS,
    ISSUED_ACCEPTANCE_REGISTRY,
    _registered_generation_row_is_complete,
    _valid_acceptance_bound,
    load_calibration_acceptance_bound,
)
from joulewise.calibration_bracketing import _canonical_sha256
from joulewise.calibration_ledger import (
    SESSION_KIND_BRACKET,
    load_calibration_ledger_snapshot,
)
import tests.fixtures.epoch_bootstrap.build as build_module
from tests.fixtures.epoch_bootstrap.build import (
    TARGET_EPOCH,
    Slot,
    build_derivation_ledger,
    tamper_member_bundle,
)


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
PREREGISTRATION_SHA256 = hashlib.sha256(PREREGISTRATION.read_bytes()).hexdigest()


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
            "--preregistration-sha256", PREREGISTRATION_SHA256,
            "--out", str(self.out),
        ]
        # Every fixture but the shape tests is ONE session of N slots, so the
        # two shape rulings are supplied here; the shape refusals get their own
        # tests, which omit them.
        if "--nights-ruling" not in extra:
            argv += ["--nights-ruling", "fixture: single-session shape"]
        if "--slot-count-ruling" not in extra:
            argv += ["--slot-count-ruling", "fixture: N-slot shape"]
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
        self.assertEqual(
            set(payload["prospective_rederivation"]["triggers"]),
            issuer.rederivation_triggers(
                payload["registered_generation_row"]["corpus_doubling_trigger"]
            ),
        )
        self.assertEqual(len(payload["derivation_sha256"]), 64)

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

    def test_emitted_row_refuses_when_its_predecessor_ceiling_is_rebased(self) -> None:
        """The row's lineage fence is live, not decorative."""

        self.run_issuer(self.wide)
        row = self.registry_row()
        row["predecessor_ceiling_s"] = "0.0095"
        self.assertFalse(_registered_generation_row_is_complete(row))

    # ---- the screen rule, now registered by S3 --------------------------

    def registry_row(self) -> dict:
        """The emitted row in the exact shape the registration will take.

        `generation_row_for_registry` is the ONE home for the list-to-tuple
        conversion, and it lives on the EMITTING side: S3's fences are
        `isinstance(..., tuple)`, JSON has no tuple, and a row handed over
        unconverted is refused silently.  The transaction seat that writes
        `_D102_GENERATION_DERIVATIONS` calls this function; it does not
        re-derive the conversion.
        """

        return issuer.generation_row_for_registry(
            self.payload()["registered_generation_row"]
        )

    def assert_row_admitted(self, fixture: dict[str, Path]) -> dict:
        self.assertEqual(self.run_issuer(fixture), 0)
        row = self.registry_row()
        self.assertEqual(row["screen_rule"], issuer.SCREEN_RULE_FLOORED_RANGE_ENVELOPE)
        self.assertEqual(row["d125_ruling"], D125_REFERENCE)
        self.assertEqual(
            row["predecessor_acceptance_id"], "d079_calibration_acceptance_v2_n17_r6"
        )
        self.assertEqual(
            row["predecessor_ceiling_s"],
            _D102_GENERATION_DERIVATIONS["d079_calibration_acceptance_v2_n17_r6"][
                "operatives"
            ]["maximum_budgetable_drift_s"],
        )
        self.assertIsInstance(row["epoch_catalog_ids"], tuple)
        self.assertIsInstance(row["registration_session_ids"], tuple)
        self.assertTrue(_registered_generation_row_is_complete(row))
        return row

    def test_range_bound_corpus_row_is_admitted_alongside_r6(self) -> None:
        """The envelope row S3 now registers, range arm."""

        row = self.assert_row_admitted(self.wide)
        outcomes = self.payload()["derivation_notes"]["rule_outcomes"]
        self.assertIs(outcomes["screen_floor_bound"], False)
        self.assertEqual(row["operatives"]["bracket_screen_s"], outcomes["quantized_range_s"])

    def test_floor_bound_corpus_row_is_admitted_alongside_r6(self) -> None:
        """The same rule name, floor arm — the n = 19 norm, not the exotic case."""

        row = self.assert_row_admitted(self.floored)
        outcomes = self.payload()["derivation_notes"]["rule_outcomes"]
        self.assertIs(outcomes["screen_floor_bound"], True)
        self.assertEqual(row["operatives"]["bracket_screen_s"], "0.010818")

    def test_no_stale_seam_flag_or_warning_is_emitted(self) -> None:
        """The screen rule is registered now; the old warning must be gone."""

        self.run_issuer(self.wide)
        self.assertNotIn("SEAM", self.printed)
        self.assertNotIn(
            "screen_rule_registered_in_validator",
            json.dumps(self.payload()),
        )

    # ---- B1: the triggers are derived, never copied ---------------------

    def test_emitted_triggers_are_derived_from_the_emitted_row(self) -> None:
        """`prospective_rederivation.triggers` matches what the validator demands."""

        self.run_issuer(self.wide)
        payload = self.payload()
        row = payload["registered_generation_row"]
        self.assertEqual(row["corpus_doubling_trigger"], "corpus_doubles_from_20_to_40")
        self.assertEqual(
            set(payload["prospective_rederivation"]["triggers"]),
            issuer.rederivation_triggers(row["corpus_doubling_trigger"]),
        )
        # The predecessor's own trigger names the predecessor's corpus and must
        # NOT survive the copy that used to make this artifact unauthenticatable.
        self.assertNotIn(
            "corpus_doubles_from_17_to_34",
            payload["prospective_rederivation"]["triggers"],
        )

    def test_only_the_candidate_label_stops_the_candidate_authenticating(self) -> None:
        """The refusal REASON is `candidate_not_issued`, and nothing else.

        Flipping the three label fields (and registering the row and the id, as
        the D-138 transaction will) makes the production validator ADMIT the
        artifact.  Any other shape defect — a copied trigger, a wrong digest
        recipe, a missing block — shows up here as a still-refusing artifact.
        """

        self.run_issuer(self.wide)
        payload = self.payload()
        self.assertIsNone(load_calibration_acceptance_bound(self.out))
        issued = json.loads(json.dumps(payload))
        del issued["candidate_not_issued"]
        issued["artifact_role"] = "issued"
        # The whole `issuance` block is a candidate LABEL, `licence` included:
        # the transaction rewrites it rather than editing fields, so the
        # candidate's "these bytes license nothing" sentence cannot survive into
        # an issued artifact and contradict it.
        self.assertIn("licence", payload["issuance"])
        issued["issuance"] = {
            "status": "issued",
            "claim_eligible": True,
            "reason": payload["issuance"]["reason"],
        }
        self.assertNotIn("licence", issued["issuance"])
        issued["backfill_candidate"]["status"] = "issued"
        issued["backfill_candidate"]["production_issuance_blocked"] = False
        issued["derivation_sha256"] = issuer.derivation_sha256(issued)
        acceptance_id = issued["acceptance_id"]
        row = issuer.generation_row_for_registry(issued["registered_generation_row"])
        with mock.patch.dict(_D102_GENERATION_DERIVATIONS, {acceptance_id: row}), \
                mock.patch.dict(
                    ISSUED_ACCEPTANCE_REGISTRY,
                    {acceptance_id: {"path": self.out, "relative_path": str(self.out),
                                     "file_sha256": "0" * 64}},
                ):
            self.assertTrue(_valid_acceptance_bound(issued))

    # ---- B3: the realized df is proven before issuance ------------------

    def test_realized_df_carries_a_two_route_quantile_proof(self) -> None:
        """A df nobody pinned in a test still issues only with its own proof."""

        rows = [Slot(v) for v in _grid(22, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "df21", rows)
            self.assertEqual(self.run_issuer(fixture), 0)
        proof = self.payload()["decimal_derivation"]["quantile_proof"]
        self.assertEqual(proof["degrees_of_freedom"], 21)
        self.assertEqual(proof["probabilities"], ["0.975", "0.995"])
        self.assertEqual(proof["precision"], issuer.DECIMAL_WORK_PRECISION)
        for probability in ("0.975", "0.995"):
            self.assertGreaterEqual(
                proof["closed_form_agreement_digits"][probability],
                issuer.QUANTILE_PROOF_MINIMUM_AGREEMENT_DIGITS,
            )
            self.assertLess(
                Decimal(proof["forward_residuals"][probability]),
                issuer.QUANTILE_PROOF_MAXIMUM_FORWARD_RESIDUAL,
            )
        # df 21 is not in the set any test pins, which is the point.
        self.assertEqual(proof["quantiles"]["0.995"], "2.83135955802305001688")

    def test_a_disagreeing_independent_route_refuses(self) -> None:
        """`quantile_proof_failed`: no corpus issues on an unproven df."""

        def wrong(probability: str, degrees_of_freedom: int) -> Decimal:
            return issuer.student_t_quantile(probability, degrees_of_freedom) + 1
        with mock.patch.object(issuer, "student_t_quantile_closed_form", wrong):
            code = self.run_issuer(self.wide)
        self.assert_refused(code, "quantile_proof_failed")

    def test_a_failing_forward_check_refuses(self) -> None:
        """The other half of the proof is a fence too, not a printed number."""

        with mock.patch.object(
            issuer, "QUANTILE_PROOF_MAXIMUM_FORWARD_RESIDUAL", Decimal(0)
        ):
            code = self.run_issuer(self.wide)
        self.assert_refused(code, "quantile_proof_failed")

    def test_the_closed_form_route_reproduces_r6_and_both_parities(self) -> None:
        """The independent route is independently right, not merely agreeing."""

        cases = {
            (16, "0.995"): "2.92078162242509999197",
            (18, "0.995"): "2.87844047273860811781",
            (19, "0.975"): "2.09302405440830976918",
        }
        for (df, probability), expected in cases.items():
            with self.subTest(df=df, p=probability):
                value = issuer.student_t_quantile_closed_form(probability, df)
                self.assertEqual(
                    str(+value.quantize(Decimal(1).scaleb(-20))), expected
                )

    # ---- SF1: the custody-hash clause -----------------------------------

    def test_a_manifest_edited_after_finalization_refuses(self) -> None:
        """`_read_member_evidence` authenticates bundle bytes against the row."""

        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "tampered", rows)
            tamper_member_bundle(fixture, "derivation-night-1-d06", "manifest.json")
            code = self.run_issuer(fixture)
        self.assert_refused(
            code, "manifest.json does not match the ledger row"
        )

    # ---- SF2: addendum A-7 ----------------------------------------------

    def test_a_valid_same_epoch_row_outside_the_registration_refuses(self) -> None:
        """A-7: it is neither absorbed nor ignored; issuance stops."""

        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(
                Path(tmp) / "foreign", rows,
                second_session=("derivation-night-foreign", [Slot("0.0260")]),
            )
            code = self.run_issuer(fixture)
        self.assert_refused(code, "valid same-epoch observations outside this registration")

    # ---- SF3: what the input seal covers --------------------------------

    def test_the_input_seal_covers_every_derivation_input(self) -> None:
        """Rewriting any input moves `derivation_input_sha256`."""

        self.run_issuer(self.wide)
        payload = self.payload()
        baseline = payload["derivation_input_sha256"]
        self.assertEqual(issuer.derivation_input_sha256(payload), baseline)
        rewrites = {
            "identity epoch": lambda p: p["identity_epoch"].__setitem__("os_build", "26A1"),
            "ledger cutoff": lambda p: p["ledger_cutoff"].__setitem__("head_digest", "9" * 64),
            "predecessor id": lambda p: p["registered_generation_row"].__setitem__(
                "predecessor_acceptance_id", "d079_calibration_acceptance_v2_n19"
            ),
            "quantile proof": lambda p: p["decimal_derivation"]["quantile_proof"].__setitem__(
                "degrees_of_freedom", 99
            ),
            "member lexeme": lambda p: p["derivation_corpus"]["members"][0].__setitem__(
                "b_fiducial_s", "0.0201"
            ),
            "operative screen": lambda p: p["decimal_derivation"]["ratified_operatives"]
            .__setitem__("bracket_screen_s", "0.011401"),
        }
        for label, rewrite in rewrites.items():
            with self.subTest(input=label):
                mutated = json.loads(json.dumps(payload))
                rewrite(mutated)
                self.assertNotEqual(issuer.derivation_input_sha256(mutated), baseline)
        # Prose and the candidate label stay OUT, deliberately.
        unchanged = json.loads(json.dumps(payload))
        unchanged["derivation_notes"]["generation"] = "different prose"
        self.assertEqual(issuer.derivation_input_sha256(unchanged), baseline)

    def test_the_artifact_digest_uses_the_production_recipe(self) -> None:
        """`derivation_sha256` is what `_valid_acceptance_bound` recomputes."""

        self.run_issuer(self.wide)
        payload = self.payload()
        core = {k: v for k, v in payload.items() if k != "derivation_sha256"}
        self.assertEqual(payload["derivation_sha256"], _canonical_sha256(core))

    # ---- nits -----------------------------------------------------------

    def test_the_default_acceptance_id_names_the_realized_epoch(self) -> None:
        self.run_issuer(self.wide)
        self.assertEqual(
            self.payload()["acceptance_id"],
            "d079_calibration_acceptance_v2_n20_25g83_r1",
        )
        self.assertEqual(
            issuer.default_acceptance_id(19, {"os_build": "26A2"}),
            "d079_calibration_acceptance_v2_n19_26a2_r1",
        )

    def test_the_quantile_pins_its_own_precision(self) -> None:
        """Accuracy must not follow the caller's ambient Decimal context."""

        with localcontext() as context:
            context.prec = 15
            value = issuer.student_t_quantile("0.995", 19)
        self.assertEqual(
            str(+value.quantize(Decimal(1).scaleb(-20))), "2.86093460646497919208"
        )

    def test_the_two_draw_rule_string_matches_r6(self) -> None:
        """The rule string is sealed, so a paraphrase would move the digest."""

        self.assertEqual(
            issuer.TWO_DRAW_PREDICTION_RULE,
            json.loads(R6.read_text())["decimal_derivation"][
                "two_draw_prediction_derivation"
            ]["rule"],
        )


    # ---- fix round 2 ----------------------------------------------------

    VALUE_LEXEME_FRAGMENTS = ("0.02", "0.03", "0.011", "0.010818", "corpus n")

    def assert_no_measured_value_leaked(self, text: str) -> None:
        """No member value, screen, ceiling or corpus count anywhere in output."""

        for fragment in self.VALUE_LEXEME_FRAGMENTS:
            self.assertNotIn(fragment, text)

    # 93 SF-1 blindness

    def test_an_open_registration_session_refuses_before_anything_is_computed(self) -> None:
        """`refuse_open_registration` gates every read of the corpus."""

        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "open", rows, fill_slots=6)
            code = self.run_issuer(fixture)
        self.assert_refused(code, "is 'open', not terminal")
        self.assertIn("Blindness", self.printed)
        self.assert_no_measured_value_leaked(self.printed)

    def test_the_blindness_gate_is_isolated_from_the_ledger_refusal(self) -> None:
        """The gate is a clause of its own, not a by-product of the snapshot.

        The CLI path also carries `calibration_ledger_bracket_session_open`, so
        this exercises the clause directly against a snapshot that has NO
        refusal reason at all — the state the desk is in once the pin has been
        advanced between nights.
        """

        session = SimpleNamespace(
            session_id="s1", session_kind="derivation", state="open",
            declared_slots=("d01",),
        )
        snapshot = SimpleNamespace(
            bracket_session_by_id={"s1": session}, refusal_reasons=(),
        )
        with self.assertRaises(issuer.PrepareRefusal) as caught:
            issuer.refuse_open_registration(snapshot, ("s1",))
        self.assertIn("not terminal", caught.exception.reason)
        for state in issuer.TERMINAL_SESSION_STATES:
            with self.subTest(state=state):
                session.state = state
                issuer.refuse_open_registration(snapshot, ("s1",))

    # 93 SF-2 the only ruled departure is 17

    def test_only_seventeen_is_a_ruled_alternative_floor(self) -> None:
        """A ruling reference licenses n = 17, not any number the caller likes."""

        self.assert_refused(
            self.run_issuer(self.wide, "--minimum-corpus-size", "3", "--ed-ruling", "Ed"),
            "is not a ruled floor",
        )
        self.assert_refused(
            self.run_issuer(self.wide, "--minimum-corpus-size", "18", "--ed-ruling", "Ed"),
            "is not a ruled floor",
        )
        self.assert_refused(
            self.run_issuer(self.wide, "--minimum-corpus-size", "20", "--ed-ruling", "Ed"),
            "is not a ruled floor",
        )

    # 93 SF-4 pending or unresolved prefix rows

    def test_an_unresolved_prefix_row_refuses(self) -> None:
        """The pre-registration says refuse, not drop."""

        values = _grid(20, "0.0200", "0.0006")
        rows = [Slot(v) for v in values]
        rows[4] = Slot(values[4], disposition="abandoned")
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "unresolved", rows)
            code = self.run_issuer(fixture)
        self.assert_refused(code, "pending or unresolved attempts")

    # 91 + 93 SF-3 repo-relative member paths

    def test_member_source_directory_is_repo_relative_and_re_resolves(self) -> None:
        """Both consumers do `repo_root / member["source_directory"]`."""

        self.assertEqual(self.run_issuer(self.wide), 0)
        payload = self.payload()
        root = Path(self.wide["root"]).resolve()
        for member in payload["derivation_corpus"]["members"]:
            directory = member["source_directory"]
            self.assertFalse(Path(directory).is_absolute(), directory)
            resolved = (root / directory).resolve()
            self.assertTrue(resolved.is_dir(), resolved)
            self.assertEqual(resolved.name, member["member_id"])
        # r6's own members are stored the same way.
        self.assertFalse(
            Path(
                json.loads(R6.read_text())["derivation_corpus"]["members"][0][
                    "source_directory"
                ]
            ).is_absolute()
        )

    def test_custody_outside_the_repository_refuses(self) -> None:
        with self.assertRaises(issuer.PrepareRefusal):
            issuer._repo_relative_custody("/tmp/elsewhere/x", "a01", Path("/var/empty"))

    # 91 DF-1 the ceiling arithmetic, both operands, no CLI

    def test_the_ceiling_takes_whichever_operand_is_larger(self) -> None:
        """`max(predecessor, Q99)` — a collapse to EITHER operand must fail.

        The real predecessor (r6) has a ceiling below the screen floor, so the
        predecessor arm can never win through the CLI; these synthetic pairs
        exercise it directly.
        """

        cases = (
            ("predecessor wins", Decimal("0.02"), Decimal("0.014"), Decimal("0.02")),
            ("own Q99 wins", Decimal("0.0101"), Decimal("0.014"), Decimal("0.014")),
            ("equal", Decimal("0.014"), Decimal("0.014"), Decimal("0.014")),
        )
        for label, predecessor, own, expected in cases:
            with self.subTest(case=label):
                self.assertEqual(issuer.envelope_ceiling(predecessor, own), expected)
        self.assertEqual(
            issuer.envelope_screen(Decimal("0.0114"), Decimal("0.010818")),
            Decimal("0.0114"),
        )
        self.assertEqual(
            issuer.envelope_screen(Decimal("0.0100"), Decimal("0.010818")),
            Decimal("0.010818"),
        )

    # 93 SF-6 the registration dry run inside `check`

    def dry_run_output(self, fixture: dict[str, Path], *session_ids: str) -> tuple[int, str]:
        snapshot = load_calibration_ledger_snapshot(
            fixture["ledger"], fixture["pin"], require_committed_pin=True,
            verify_custody=False, mode="read_replay", repo_root=fixture["root"],
        )
        code, lines = issuer.registration_dry_run(snapshot, list(session_ids))
        return code, "\n".join(lines)

    def test_the_dry_run_reports_a_terminal_registration_as_admissible(self) -> None:
        code, text = self.dry_run_output(self.wide, SESSION)
        self.assertEqual(code, 0)
        self.assertIn("kind=derivation", text)
        self.assertIn("terminal=yes", text)
        self.assertIn("declared=20", text)
        self.assertIn("filled=20", text)
        self.assertIn("admissible for prepare-candidate: yes", text)

    def test_the_dry_run_reports_no_measured_value(self) -> None:
        """Blindness binds the dry run too — it is run BETWEEN nights."""

        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "dryopen", rows, fill_slots=6)
            code, text = self.dry_run_output(fixture, SESSION)
        self.assertEqual(code, issuer.DRY_RUN_INADMISSIBLE_EXIT)
        self.assertIn("terminal=no", text)
        self.assertIn("admissible for prepare-candidate: no", text)
        self.assert_no_measured_value_leaked(text)

    def test_the_dry_run_names_exclusion_mechanisms_and_unresolved_rows(self) -> None:
        values = _grid(19, "0.0200", "0.0006")
        rows = [Slot(v) for v in values]
        rows.append(Slot("0.0260", unresolved_detail="affine_clock_fit_empty"))
        rows[2] = Slot(values[2], disposition="abandoned")
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "dryexcl", rows)
            code, text = self.dry_run_output(fixture, SESSION)
        self.assertEqual(code, issuer.DRY_RUN_INADMISSIBLE_EXIT)
        self.assertIn("affine_clock_fit_empty:1", text)
        # A COUNT, never the attempt ids.
        self.assertIn("prefix pending or unresolved rows: 1", text)
        self.assertNotIn("derivation-night-1-d03", text)
        self.assertIn("admissible for prepare-candidate: no", text)

    def test_check_output_is_unchanged_when_no_registration_is_named(self) -> None:
        """`--session-ids` only ever APPENDS to the epoch watch."""

        def run(*extra: str) -> str:
            stream = io.StringIO()
            args = issuer.build_parser().parse_args(
                ["check", "--ledger", str(self.wide["ledger"]),
                 "--head-pin", str(self.wide["pin"]),
                 "--acceptance", str(R6), *extra]
            )
            with redirect_stdout(stream):
                issuer.check(args)
            return stream.getvalue()

        baseline = run()
        self.assertEqual(baseline, run("--session-ids", ""))
        self.assertNotIn(issuer.DRY_RUN_HEADER, baseline)
        with_registration = run("--session-ids", SESSION)
        self.assertTrue(with_registration.startswith(baseline))
        self.assertIn(issuer.DRY_RUN_HEADER, with_registration)

    # 93 SF-7 the tool describes itself truthfully

    def test_the_module_docstring_describes_both_subcommands_truthfully(self) -> None:
        """First-use test: every claim in the help text is checkable here."""

        text = issuer.__doc__ or ""
        self.assertNotIn("reserved for S4", text)
        self.assertIn("`check` is READ-ONLY", text)
        self.assertIn("WRITES EXACTLY ONE FILE", text)
        self.assertIn("no default destination", text)
        self.assertIn("candidate_not_issued", text)
        self.assertIn("D-138 transaction", text)
        for reason in ("terminal", "--d125-ruling", "--ed-ruling", "pending or unresolved",
                       "outside the registration", "quantile proof", "budget ceiling"):
            with self.subTest(reason=reason):
                self.assertIn(reason, text)
        # argparse rewraps the docstring, so normalise before matching.
        parser = issuer.build_parser()
        self.assertIn(
            "WRITES EXACTLY ONE FILE", " ".join(parser.format_help().split())
        )

    # 93 wording: the selection string says what the code does

    def test_the_selection_string_describes_a_read_not_a_re_derivation(self) -> None:
        self.run_issuer(self.wide)
        selection = self.payload()["derivation_corpus"]["selection"]
        self.assertIn("stored anchor-v3 record", selection)
        self.assertIn("authenticated against its ledger row", selection)
        self.assertIn("no value is re-derived here", selection)

    # 91 nits

    def test_the_predecessor_note_identifies_it_by_bytes(self) -> None:
        self.run_issuer(self.wide)
        note = self.payload()["derivation_notes"]["predecessor"]
        self.assertEqual(
            note["file_sha256"], hashlib.sha256(R6.read_bytes()).hexdigest()
        )
        self.assertEqual(
            note["derivation_sha256"], json.loads(R6.read_text())["derivation_sha256"]
        )

    # 93 SF-5 the proof bounds say whose they are

    def test_the_quantile_proof_records_where_its_bounds_came_from(self) -> None:
        self.run_issuer(self.wide)
        proof = self.payload()["decimal_derivation"]["quantile_proof"]
        self.assertIn("issuer-declared bounds", proof["bounds_origin"])
        self.assertIn(
            "stated in the pre-registration's quantile-proof clause",
            proof["bounds_origin"],
        )
        self.assertIn("1e-30", proof["bounds_origin"])
        self.assertIn("30 significant digits", proof["bounds_origin"])
        # It is inside the seal, so the bounds cannot be edited quietly.
        mutated = json.loads(json.dumps(self.payload()))
        mutated["decimal_derivation"]["quantile_proof"]["bounds_origin"] = "whatever"
        self.assertNotEqual(
            issuer.derivation_input_sha256(mutated),
            self.payload()["derivation_input_sha256"],
        )


    # ---- fix round 3 ----------------------------------------------------

    def test_the_candidate_states_its_licence_in_words(self) -> None:
        """SF-8: a reader can act on the label without decoding a boolean.

        The sentence sits inside the sealed artifact, so `derivation_sha256`
        covers it and it cannot be edited away silently.  It is a
        candidate-LABEL field: the D-138 transaction rewrites the whole
        `issuance` block when it issues (see
        `test_only_the_candidate_label_stops_the_candidate_authenticating`),
        and that test still ADMITS the artifact with this key present.
        """

        self.assertEqual(self.run_issuer(self.wide), 0)
        payload = self.payload()
        self.assertEqual(
            payload["issuance"]["licence"],
            "These bytes license nothing: no measurement window, no claim, no "
            "threshold. No tool may load them as authority; the production "
            "loader refuses them by artifact_role.",
        )
        # Sealed: inside `derivation_sha256`, outside `derivation_input_sha256`
        # (prose is deliberately outside the input seal).
        mutated = json.loads(json.dumps(payload))
        mutated["issuance"]["licence"] = "these bytes license everything"
        core = {k: v for k, v in mutated.items() if k != "derivation_sha256"}
        self.assertNotEqual(payload["derivation_sha256"], _canonical_sha256(core))
        self.assertEqual(
            issuer.derivation_input_sha256(mutated),
            payload["derivation_input_sha256"],
        )
        # It says what the loader does, and the loader does it.
        self.assertIsNone(load_calibration_acceptance_bound(self.out))


    # ---- fix round 4 ----------------------------------------------------

    DRY_RUN_SESSION_PATTERN = re.compile(
        r"^(?P<id>[\w-]+): kind=(?P<kind>\w+) state=(?P<state>\w+) "
        r"terminal=(?P<terminal>yes|no) declared=(?P<declared>\d+) "
        r"filled=(?P<filled>\d+) excluded=(?P<excluded>none|[\w:,]+)$"
    )

    # E-1: filled comes from the session record, not from published rows

    def test_the_dry_run_counts_filled_slots_on_an_open_session(self) -> None:
        """An open session publishes no observation; its progress still shows.

        `len(session.finalized_slots)` is a COUNT of the session record's own
        slots, so it reports 6 of 20 without anything reading a captured value.
        """

        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "open6", rows, fill_slots=6)
            code, text = self.dry_run_output(fixture, SESSION)
        self.assertEqual(code, issuer.DRY_RUN_INADMISSIBLE_EXIT)
        match = self.DRY_RUN_SESSION_PATTERN.match(
            next(line for line in text.splitlines() if line.startswith(SESSION))
        )
        self.assertIsNotNone(match)
        self.assertEqual(match.group("declared"), "20")
        self.assertEqual(match.group("filled"), "6")
        self.assertEqual(match.group("terminal"), "no")
        self.assert_no_measured_value_leaked(text)

    # E-2: the "aborted" arm of the terminal set, witnessed literally

    def test_an_aborted_session_is_terminal(self) -> None:
        """`window_exhausted` is the pre-registration's planned early close.

        Deliberately written against the literal state name rather than by
        iterating `TERMINAL_SESSION_STATES`, so removing `"aborted"` from that
        set fails here instead of quietly agreeing with itself.
        """

        rows = [Slot(v) for v in _grid(24, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(
                Path(tmp) / "aborted", rows, fill_slots=20,
                abort_reason="window_exhausted",
            )
            code, text = self.dry_run_output(fixture, SESSION)
            self.assertEqual(self.run_issuer(fixture), 0)
        self.assertEqual(code, 0)
        self.assertIn("state=aborted", text)
        self.assertIn("terminal=yes", text)
        self.assertIn("declared=24", text)
        self.assertIn("filled=20", text)
        # prepare-candidate proceeds past the blindness gate on it.
        self.assertEqual(self.payload()["derivation_corpus"]["n"], 20)

    # E-4: check's exit code when a registration is named

    def check_exit(self, fixture: dict[str, Path], *extra: str) -> tuple[int, str]:
        stream = io.StringIO()
        args = issuer.build_parser().parse_args(
            ["check", "--ledger", str(fixture["ledger"]),
             "--head-pin", str(fixture["pin"]), "--acceptance", str(R6), *extra]
        )
        with redirect_stdout(stream):
            code = issuer.check(args)
        return code, stream.getvalue()

    def test_check_returns_the_registration_verdict_when_one_is_named(self) -> None:
        """The epoch has drifted — that is WHY a new corpus is being captured.

        So with `--session-ids` the exit code answers the question asked, and
        the epoch-watch table still prints in full above it.
        """

        code, text = self.check_exit(self.wide, "--session-ids", SESSION)
        self.assertEqual(code, 0)
        self.assertIn("MISMATCH", text)
        self.assertIn("Desk epoch watch", text)
        self.assertIn("admissible for prepare-candidate: yes", text)

    def test_check_returns_a_distinct_code_for_an_inadmissible_registration(self) -> None:
        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "opencli", rows, fill_slots=6)
            code, text = self.check_exit(fixture, "--session-ids", SESSION)
        self.assertEqual(code, 5)
        self.assertEqual(code, issuer.DRY_RUN_INADMISSIBLE_EXIT)
        self.assertNotEqual(code, 3)
        self.assertIn("blocker:", text)
        self.assert_no_measured_value_leaked(text)

    # E-5: the terminal gate around the bundle reads

    def test_no_bundle_is_opened_for_an_open_session(self) -> None:
        """The `if terminal:` gate is structural, not reviewed.

        The reader is replaced with one that raises, so ANY path reaching a
        member's primary bytes for an open session fails this test.
        """

        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]

        def forbidden(observation):
            raise AssertionError(
                f"bundle read for {observation.attempt_id} before the session is terminal"
            )

        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "nogate", rows, fill_slots=6)
            with mock.patch.object(issuer, "_read_member_evidence", forbidden):
                code, text = self.dry_run_output(fixture, SESSION)
        self.assertEqual(code, issuer.DRY_RUN_INADMISSIBLE_EXIT)
        self.assertIn("filled=6", text)

    # E-6: every flag documents itself, and the prose passes the first-use test

    def test_every_flag_carries_a_help_string(self) -> None:
        parser = issuer.build_parser()
        subparsers = next(
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        )
        for name, sub in subparsers.choices.items():
            for action in sub._actions:
                if action.dest == "help":
                    continue
                with self.subTest(command=name, flag=action.dest):
                    self.assertTrue(action.help, action.dest)

    def test_the_docstring_glosses_every_term_of_art_at_first_use(self) -> None:
        """Each term is built before it does any work, or it is not used."""

        # Line wrapping is not meaning: collapse it before matching, so a term
        # broken across two lines still counts as used.
        text = " ".join((issuer.__doc__ or "").split())
        glossed = {
            "OPERATIVES": "the three numbers the acceptance actually governs",
            "BRACKET SCREEN": "the drift below which a measurement window passes",
            "BUDGET CEILING": "the largest drift the generation will ever budget",
            "LEVEL SCREEN": "above which a single capture is refused",
            "PRIOR-SET PREFIX": "the run of ledger rows at or below the cutoff",
            "QUANTILE PROOF": "checked two independent ways",
            "TRIGGER OBSERVATION": "would oblige the generation to be re-derived",
            "COLD SCIENCE GATE": "the fresh-eyes review",
            "D-138 transaction": "the single reviewed commit",
        }
        for term, gloss in glossed.items():
            with self.subTest(term=term):
                self.assertIn(term, text)
                self.assertIn(gloss, text)
                # The gloss must arrive at or before the term's first use.
                self.assertLess(text.index(term), text.index(gloss) + len(gloss))
        for decision in ("D-102", "D-109", "D-125", "D-126"):
            with self.subTest(decision=decision):
                self.assertIn(decision + " ", text)

    # E-7: the dry run's lines match a fixed template

    def test_every_dry_run_line_matches_the_fixed_template(self) -> None:
        """Only integers and enum words vary — nothing free-form can appear."""

        values = _grid(19, "0.0200", "0.0006")
        rows = [Slot(v) for v in values]
        rows.append(Slot("0.0260", unresolved_detail="affine_clock_fit_empty"))
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "template", rows)
            _, text = self.dry_run_output(fixture, SESSION, "absent-session")
        lines = text.splitlines()
        self.assertEqual(lines[0], "")
        self.assertEqual(lines[1], issuer.DRY_RUN_HEADER)
        self.assertIsNotNone(self.DRY_RUN_SESSION_PATTERN.match(lines[2]))
        self.assertEqual(lines[3], "absent-session: absent")
        self.assertRegex(lines[4], r"^prefix pending or unresolved rows: \d+$")
        self.assertRegex(
            lines[5], r"^registration admissible for prepare-candidate: (yes|no)$"
        )
        for line in lines[6:]:
            self.assertRegex(line, r"^  blocker: .+$")
        self.assert_no_measured_value_leaked(text)


    # ---- fix round 5 ----------------------------------------------------

    def test_a_third_identity_epoch_in_the_prefix_refuses(self) -> None:
        """A row that is neither the target's epoch nor the predecessor's.

        The catalog has exactly two entries, so labelling is a two-way choice;
        made with `else`, it would stamp a THIRD epoch's row with the
        predecessor's catalog id and every downstream check would agree with the
        lie.  The row here is `valid` and has a content id, so neither the
        addendum A-7 scan (which only sees TARGET-epoch rows) nor the
        pending/unresolved scan can refuse it — only the epoch guard can.
        """

        third_epoch = dict(TARGET_EPOCH)
        third_epoch["os_build"] = "25H01"
        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(
                Path(tmp) / "thirdepoch", rows,
                second_session=("derivation-night-other", [Slot("0.0260")]),
                second_session_epoch=third_epoch,
            )
            code = self.run_issuer(fixture)
        self.assert_refused(
            code,
            "prior set: attempt derivation-night-other-d01 carries an identity "
            "epoch that is neither the target's nor the predecessor's; not issued",
        )

    def test_the_epoch_catalog_stays_exactly_two_entries(self) -> None:
        """The guard exists so the catalog need not grow to stay honest."""

        self.assertEqual(self.run_issuer(self.wide), 0)
        catalog = self.payload()["prior_observation_set"]["epoch_catalog"]
        self.assertEqual(len(catalog), 2)
        epochs = list(catalog.values())
        self.assertIn(self.payload()["identity_epoch"], epochs)
        self.assertIn(json.loads(R6.read_text())["identity_epoch"], epochs)
        # Every prior-set row is labelled with one of the two, never by default.
        labels = {row["epoch_id"] for row in
                  self.payload()["prior_observation_set"]["observations"]}
        self.assertTrue(labels.issubset(set(catalog)))


    # ---- fix round 6 ----------------------------------------------------

    # B-1: the machine facts a change to which VOIDS the registration

    def test_the_preregistration_epoch_pins_are_parsed_from_the_text(self) -> None:
        os_build, powermetrics = issuer.preregistration_epoch_pins(
            PREREGISTRATION.read_text(encoding="utf-8")
        )
        self.assertEqual(os_build, "25G83")
        self.assertEqual(
            powermetrics,
            "b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5",
        )

    def test_an_absent_or_ambiguous_epoch_pin_refuses(self) -> None:
        """Absent and ambiguous are both failures; neither may be guessed past."""

        with self.assertRaises(issuer.PrepareRefusal) as absent:
            issuer.preregistration_epoch_pins("no pins here")
        self.assertIn("absent", absent.exception.reason)
        doubled = (
            "os_build: 25G83\nos_build: 25H01\n"
            "/usr/bin/powermetrics sha256 in force is " + "a" * 64
        )
        with self.assertRaises(issuer.PrepareRefusal) as ambiguous:
            issuer.preregistration_epoch_pins(doubled)
        self.assertIn("ambiguous", ambiguous.exception.reason)

    def test_a_registration_under_another_os_build_is_void(self) -> None:
        other = dict(TARGET_EPOCH)
        other["os_build"] = "25H01"
        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            # The registered session itself was captured under a later build:
            # the machine moved on mid-campaign, which voids the registration.
            fixture = build_derivation_ledger(
                Path(tmp) / "osbuild", rows, session_epoch=other,
            )
            code = self.run_issuer(fixture)
        self.assert_refused(code, "is not the pre-registered '25G83'")

    def test_a_registration_under_another_powermetrics_binary_is_void(self) -> None:
        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        rotated = dict(build_module.T1_BINDINGS)
        rotated["powermetrics_sha256"] = "c" * 64
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(
                Path(tmp) / "rotated", rows, t1_bindings=rotated,
            )
            code = self.run_issuer(fixture)
        self.assert_refused(code, "is not the pre-registered b762e5bf")

    def test_check_compares_the_preregistered_binary_only_when_asked(self) -> None:
        """Byte-identical without `--preregistration`; one line with it."""

        def run(*extra: str) -> str:
            stream = io.StringIO()
            args = issuer.build_parser().parse_args(
                ["check", "--ledger", str(self.wide["ledger"]),
                 "--head-pin", str(self.wide["pin"]),
                 "--acceptance", str(R6), *extra]
            )
            with redirect_stdout(stream):
                issuer.check(args)
            return stream.getvalue()

        baseline = run()
        self.assertNotIn("pre-registered powermetrics", baseline)
        with_pin = run("--preregistration", str(PREREGISTRATION))
        self.assertTrue(with_pin.startswith(baseline))
        self.assertIn(
            "pre-registered powermetrics sha256 "
            "b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5",
            with_pin,
        )

    # B-2: the corpus is bound to the pre-registered shape

    def test_a_registration_of_other_than_three_nights_refuses(self) -> None:
        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "onenight", rows)
            code = self.run_issuer(fixture, "--nights-ruling", "")
        self.assert_refused(code, "registration names 1 sessions, not the pre-registered 3")

    def test_a_night_declaring_other_than_twelve_slots_refuses(self) -> None:
        rows = [Slot(v) for v in _grid(20, "0.0200", "0.0006")]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(Path(tmp) / "slots", rows)
            code = self.run_issuer(fixture, "--slot-count-ruling", "")
        self.assert_refused(
            code, "declared 20 slots, not the pre-registered 12"
        )

    def test_the_pre_registered_shape_needs_no_ruling(self) -> None:
        """Three nights of twelve slots emit with neither departure flag."""

        nights = [
            ("derivation-night-1", [Slot(v) for v in _grid(12, "0.0200", "0.0009")]),
            ("derivation-night-2", [Slot(v) for v in _grid(12, "0.0212", "0.0009")]),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            fixture = build_derivation_ledger(
                Path(tmp) / "shape", nights[0][1], second_session=nights[1],
            )
            argv = [
                "prepare-candidate",
                "--ledger", str(fixture["ledger"]), "--head-pin", str(fixture["pin"]),
                "--repo-root", str(fixture["root"]),
                "--preregistration", str(PREREGISTRATION),
                "--preregistration-sha256", PREREGISTRATION_SHA256,
                "--predecessor-acceptance", str(R6),
                "--registration-session-id", "derivation-night-1",
                "--registration-session-id", "derivation-night-2",
                "--d125-ruling", D125_REFERENCE,
                "--out", str(self.out),
            ]
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = issuer.main(argv)
            self.printed = stream.getvalue()
        # Two nights, so the night-count fence fires and the SLOT fence does not:
        # both sessions declare exactly 12, with no --slot-count-ruling given.
        self.assert_refused(code, "registration names 2 sessions")
        self.assertNotIn("declared", self.printed)

    # B-3: the pre-registration text is pinned

    def test_a_changed_preregistration_refuses(self) -> None:
        self.assert_refused(
            self.run_issuer(self.wide, "--preregistration-sha256", "d" * 64),
            "does not match the pinned",
        )

    def test_the_preregistration_pin_is_required(self) -> None:
        argv = ["prepare-candidate", "--preregistration", str(PREREGISTRATION),
                "--out", str(self.out)]
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                issuer.build_parser().parse_args(argv)

    # the level screen is read, not restated

    def test_the_level_screen_threshold_comes_from_the_predecessor(self) -> None:
        self.assertEqual(self.run_issuer(self.wide), 0)
        outcomes = self.payload()["derivation_notes"]["rule_outcomes"]
        self.assertEqual(
            outcomes["screen_challenge_threshold_s"],
            json.loads(R6.read_text())["decimal_derivation"]["ratified_operatives"][
                "preflight_level_screen_s"
            ],
        )
        self.assertFalse(
            hasattr(issuer, "R6_PREFLIGHT_LEVEL_SCREEN_S"),
            "the level screen must have one home: the predecessor artifact",
        )

    def test_the_a4_diagnostic_is_checked_against_the_predecessor(self) -> None:
        """The ruled literal must still describe the predecessor's own corpus."""

        statistics = json.loads(R6.read_text())["decimal_derivation"][
            "source_statistics"
        ]
        with localcontext() as context:
            context.prec = issuer.DECIMAL_WORK_PRECISION
            recomputed = Decimal(statistics["maximum_s"]) + Decimal(
                statistics["range_s"]
            )
        self.assertEqual(recomputed, issuer.R6_MAXIMUM_PLUS_RANGE_S)
        with mock.patch.object(
            issuer, "R6_MAXIMUM_PLUS_RANGE_S", Decimal("0.0426220830041564")
        ):
            code = self.run_issuer(self.wide)
        self.assert_refused(code, "does not equal the ruled diagnostic")

    def test_the_docstring_states_the_binary64_prediction_step(self) -> None:
        text = " ".join((issuer.__doc__ or "").split())
        self.assertIn("evaluated in BINARY64", text)
        self.assertIn("shortest decimal that reads back as the same double", text)

    def test_the_derivation_digest_docstring_names_symbols_not_line_numbers(self) -> None:
        doc = issuer.derivation_sha256.__doc__ or ""
        self.assertIn("_canonical_sha256", doc)
        self.assertNotRegex(doc, r"`:\d+`")


    # ---- fix round 7 ----------------------------------------------------

    def test_a_repeated_registration_session_refuses(self) -> None:
        """Three flags naming one night are not three nights.

        The three-nights fence counted flag REPETITIONS, so repeating one id
        satisfied it while the ledger held a single session.  The repetition is
        refused on its own terms — a registration naming the same night twice is
        malformed whatever the count fence would have said.
        """

        code = self.run_issuer(
            self.wide,
            "--registration-session-id", SESSION,
            "--registration-session-id", SESSION,
            "--nights-ruling", "",
        )
        self.assert_refused(
            code, f"registration names a session more than once: {SESSION}"
        )

    def test_the_night_count_fence_counts_distinct_sessions(self) -> None:
        """With the repetition refusal disabled, the count still sees ONE night.

        The two checks must not depend on each other having run, or deleting
        either would silently restore the other's defect.  Disabling the
        repetition refusal is the only way to reach the count fence with
        duplicates, so it is disabled here — and the fence catches them.
        """

        with mock.patch.object(
            issuer, "refuse_repeated_sessions", lambda session_ids: None
        ):
            code = self.run_issuer(
                self.wide,
                "--registration-session-id", SESSION,
                "--registration-session-id", SESSION,
                "--nights-ruling", "",
            )
        self.assert_refused(code, "registration names 1 sessions, not the pre-registered 3")


if __name__ == "__main__":
    unittest.main()
