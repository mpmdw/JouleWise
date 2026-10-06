"""The block-5 HAZARD_PACK window plan writer (desk only; never arms)."""

from __future__ import annotations

import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from joulewise import arm_readiness_evidence_t0 as t0_author
from joulewise import night_gate
from joulewise.b5 import chain as b5_chain
from joulewise.b5 import plan as b5_plan
from tests.fixtures.b5_plan import fake_window

REPO_ROOT = Path(__file__).resolve().parents[1]


class WindowPlanFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="b5-plan-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.measurement = fake_window.build_checkout(self.root)
        self.t0 = (int(time.time()) // 60 + 60) * 60

    def inputs(self, pack="alpha", **changes):
        value = fake_window.inputs(self.root, self.measurement, pack, plan_id=f"b5-{pack}-1", t0_epoch_s=self.t0)
        value.update(changes)
        return value

    def write(self, inputs=None, **keywords):
        keywords.setdefault("pack_digest", lambda _root: "e" * 64)
        keywords.setdefault("threshold_defaults", fake_window.threshold_defaults)
        return b5_plan.write_window_plan(inputs if inputs is not None else self.inputs(), **keywords)

    def assert_nothing_written(self):
        self.assertFalse((self.root / "custody").exists())
        self.assertEqual([], list((self.root / "runs").iterdir()))


class WindowPlanTests(WindowPlanFixture):
    def test_each_pack_yields_a_parseable_hazard_plan_with_all_fourteen_bindings(self):
        for pack, members in (("alpha", 119), ("beta", 119), ("gamma", 101)):
            with self.subTest(pack=pack):
                root = self.root / pack
                root.mkdir()
                inputs = fake_window.inputs(root, self.measurement, pack, plan_id=f"b5-{pack}-1", t0_epoch_s=self.t0)
                record = self.write(inputs)
                self.assertEqual([], record["thresholds_audit"]["differences_from_defaults"])
                self.assertEqual([], record["thresholds_audit"]["sized_keys_replaced"])
                plan = night_gate.NightPlan.from_mapping(json.loads(Path(record["plan"]["path"]).read_text()))
                self.assertIsInstance(plan, night_gate.HazardNightPlan)
                self.assertEqual(night_gate.HAZARD_PACK, plan.receipt_class)
                window = plan.hazard_window
                self.assertEqual(set(night_gate.HAZARD_LAUNCH_BINDINGS), set(window["bindings"]))
                self.assertEqual(members, window["member_count"])
                self.assertEqual(members * inputs["bytes_per_member"], window["planned_bytes"])
                self.assertEqual(inputs["bracket_session_id"], window["bracket_session_id"])
                self.assertEqual(str(self.measurement / b5_plan.DEFAULT_LEDGER_RELATIVE), window["bindings"]["ledger_path"])
                # The copied thresholds, plus the two keys the window sizes itself.
                expected = json.loads(json.dumps(fake_window.THRESHOLDS))
                expected["disk"]["planned_bytes"] = window["planned_bytes"]
                expected["clock"]["t_stream_max_s"] = 335
                self.assertEqual(expected, window["thresholds"])
                self.assertEqual((335, 3600), (window["T_stream_max_s"], window["programmed_span_s"]))
                self.assertEqual(list(b5_chain.DEVIATIONS), window["chain_deviations"])
                self.assertEqual(Path(window["bindings"]["claim_runs_root"]) / "instrument_validation" /
                                 inputs["pre_attempt_id"], Path(window["bindings"]["pre_calibration_dir"]))
                # The window maximum carries the 3300 s T-0 stage cap (dwell cap 2700 s inside it).
                span = inputs["programmed_span_s"]["seconds"]
                self.assertEqual(60 * math.ceil((span + 3300) / 60), plan.window_max_s)
                self.assertGreaterEqual(plan.window_max_s - span, b5_plan.DWELL_CAP_S)
                # Fresh runs roots exist and are empty; the chain and its sidecar agree.
                for name in ("claim", "bound"):
                    self.assertEqual([], list(Path(window["runs_roots"][name]).iterdir()))
                chain = Path(plan.chain_path).read_bytes()
                self.assertEqual(b5_chain.sidecar_bytes(chain, "chain.zsh"), Path(plan.chain_sha256_path).read_bytes())
                self.assertIn(b"export SETTLE_S=60\n", chain)
                self.assertEqual(60, window["settle_s"])

    def test_window_env_is_the_exact_25_key_allowlist(self):
        record = self.write()
        values = t0_author.parse_window_environment(Path(record["window_env"]["path"]).read_bytes())
        self.assertEqual(set(b5_plan.WINDOW_ENV_KEYS), set(values))
        self.assertEqual(set(t0_author.WINDOW_ENV_KEYS), set(b5_plan.WINDOW_ENV_KEYS))
        self.assertEqual(values["CALIBRATION_LEDGER"], str(self.measurement / b5_plan.DEFAULT_LEDGER_RELATIVE))
        self.assertEqual("b5-alpha-1-calibration", values["BRACKET_SESSION_ID"])

    def test_the_command_line_renders_the_registered_60_s_settle(self):
        # Review finding (L2 settle) set the runbook's SETTLE_S=180, not 600 s. The
        # block-5 timing ruling (2026-10-06) cut every block-5 settle to 60 s
        # (registration draft sections 0.6 and 5.1); the runbook keeps 180 s for
        # the legacy windows, and the chain lists the difference as a deviation.
        runbook = (REPO_ROOT / b5_chain.RUNBOOK_RELATIVE).read_text()
        registered = re.findall(r"(?m)^SETTLE_S=([0-9]+)$", runbook)
        self.assertEqual(["180"], registered)
        self.assertEqual(60, b5_chain.SETTLE_S)
        self.assertEqual(1, sum("SETTLE_S = 60 s, not the runbook's SETTLE_S=180" in item
                                for item in b5_chain.DEVIATIONS))
        path = self.root / "inputs.json"
        path.write_text(json.dumps(self.inputs()))
        output = io.StringIO()
        with redirect_stdout(output), mock.patch.object(b5_plan, "hazard_threshold_defaults",
                                                        fake_window.threshold_defaults):
            self.assertEqual(0, __import__("scripts.write_b5_window_plan", fromlist=["main"]).main(["--inputs", str(path)]))
        record = json.loads(output.getvalue())
        chain = Path(record["chain"]["path"]).read_bytes()
        self.assertIn(b"export SETTLE_S=60\n", chain)
        self.assertNotIn(b"SETTLE_S=600", chain)
        self.assertNotIn(b"export SETTLE_S=180", chain)
        plan = json.loads(Path(record["plan"]["path"]).read_text())
        self.assertEqual(60, plan["hazard_window"]["settle_s"])
        env = t0_author.parse_window_environment(Path(record["window_env"]["path"]).read_bytes())
        self.assertEqual("60", env["SETTLE_S"])

    def test_a_ledger_other_than_the_checkout_default_is_refused_at_the_desk(self):
        other = self.root / "other-ledger.jsonl"
        other.write_text("")
        with self.assertRaisesRegex(b5_plan.WindowPlanError, "default ledger"):
            self.write(self.inputs(ledger_path=str(other)))
        self.assertFalse((self.root / "custody").exists())
        self.assertEqual([], list((self.root / "runs").iterdir()))
        # The default itself is accepted when named explicitly.
        self.write(self.inputs(ledger_path=str(self.measurement / b5_plan.DEFAULT_LEDGER_RELATIVE)))

    def test_an_existing_runs_root_is_never_reused(self):
        leaf = json.loads((REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json").read_text())["roots"]
        (self.root / "runs").mkdir(exist_ok=True)
        (self.root / "runs" / leaf["bound_root_leaf"]).mkdir()
        with self.assertRaisesRegex(b5_plan.WindowPlanError, "already exists"):
            self.write()
        self.assertFalse((self.root / "custody").exists())
        self.assertFalse((self.root / "runs" / leaf["claim_root_leaf"]).exists())

    def test_input_refusals_write_nothing(self):
        cases = {
            "custody not empty": None,
            "thresholds missing a module": {"thresholds": {k: v for k, v in fake_window.THRESHOLDS.items() if k != "disk"}},
            "t0 not a whole minute": {"t0_epoch_s": self.t0 + 1},
            "identity digest wrong": {"identity_epoch_json": {"path": str(self.root / "identity-epoch.json"), "sha256": "0" * 64}},
            "pack outside the checkout": {"pack_root": str(REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5")},
            "backup inside custody": {"claim_backup_destination": str(self.root / "custody/backup")},
            "unknown key": {"extra": 1},
            "same pre and post attempt": {"post_attempt_id": "b5-alpha-1-cal-pre"},
        }
        for label, change in cases.items():
            with self.subTest(case=label):
                custody = self.root / "custody"
                if label == "custody not empty":
                    custody.mkdir()
                    (custody / "stale").write_text("x")
                with self.assertRaises(b5_plan.WindowPlanError):
                    self.write(self.inputs(**(change or {})))
                self.assertEqual([], list((self.root / "runs").iterdir()))
                if label == "custody not empty":
                    (custody / "stale").unlink()
                    custody.rmdir()
                self.assertFalse(custody.exists())

    def test_pack_digest_failure_is_recorded_not_refused(self):
        def broken(_root):
            raise RuntimeError("pack is not committed")
        record = self.write(pack_digest=broken)
        self.assertIsNone(record["pack_sha256"])
        self.assertIn("pack is not committed", record["pack_digest_error"])
        plan = json.loads(Path(record["plan"]["path"]).read_text())
        self.assertIsNone(plan["hazard_window"]["pack"]["pack_sha256"])

    def test_both_launch_binding_shapes_are_read(self):
        floor = json.loads((REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json").read_text())
        contrast = json.loads((REPO_ROOT / "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/"
                                           "plan_tree.json").read_text())
        self.assertIn("bindings", floor["arm_attachments"]["launch"])
        self.assertIn("closed_bindings", contrast["arm_attachments"]["launch"])
        for tree in (floor, contrast):
            self.assertEqual(set(night_gate.HAZARD_LAUNCH_BINDINGS), set(b5_plan.declared_bindings(tree)))
        broken = json.loads(json.dumps(floor))
        broken["arm_attachments"]["launch"]["bindings"].pop()
        with self.assertRaises(b5_plan.WindowPlanError):
            b5_plan.declared_bindings(broken)

    def test_writer_stays_off_the_retired_arm_path_at_import(self):
        code = ("import sys; import joulewise.b5.plan, joulewise.b5.chain, joulewise.b5.driver; "
                "bad = sorted(m for m in sys.modules if m.split('.')[-1] in {'arm_readiness', "
                "'arm_readiness_evidence', 'arm_readiness_evidence_t0', 'capture_t0_step', 'launch_window', "
                "'t0_rehearsal', 'v5_qualification'}); print(bad); sys.exit(1 if bad else 0)")
        completed = subprocess.run([sys.executable, "-B", "-c", code], cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


class ThresholdAndSizingTests(WindowPlanFixture):
    """Review finding (L2 thresholds): a threshold set the arm's judges would raise on is
    refused at the desk; the window's own sizing wins over a copied value; the two sizing
    inputs come from a committed sizing output, never a free number."""

    def test_every_key_a_module_reads_is_required_at_the_desk(self):
        for module, keys in fake_window.THRESHOLDS.items():
            for key in keys:
                if fake_window.L1_DEFAULT_THRESHOLDS[module].get(key, 0) is None:
                    continue  # an optional limit: test_an_optional_limit_is_null_or_positive_and_may_be_left_out
                with self.subTest(key=f"{module}.{key}"):
                    thresholds = json.loads(json.dumps(fake_window.THRESHOLDS))
                    del thresholds[module][key]
                    with self.assertRaisesRegex(b5_plan.WindowPlanError, re.escape(f"{module}.{key}")):
                        self.write(self.inputs(thresholds=thresholds))
                    self.assert_nothing_written()

    def test_a_misnamed_or_non_numeric_key_is_refused_not_defaulted(self):
        misnamed = json.loads(json.dumps(fake_window.THRESHOLDS))
        misnamed["contention"]["limit_cpu_s_per_s"] = misnamed["contention"].pop("cpu_limit_s_per_s")
        with self.assertRaisesRegex(b5_plan.WindowPlanError, re.escape("contention.cpu_limit_s_per_s")):
            self.write(self.inputs(thresholds=misnamed))
        textual = json.loads(json.dumps(fake_window.THRESHOLDS))
        textual["thermal"]["max_level"] = "0"
        with self.assertRaisesRegex(b5_plan.WindowPlanError, re.escape("thermal.max_level")):
            self.write(self.inputs(thresholds=textual))
        boolean = json.loads(json.dumps(fake_window.THRESHOLDS))
        boolean["battery"]["limit_ma"] = True
        with self.assertRaisesRegex(b5_plan.WindowPlanError, re.escape("battery.limit_ma")):
            self.write(self.inputs(thresholds=boolean))
        self.assert_nothing_written()

    def test_an_optional_limit_is_null_or_positive_and_may_be_left_out(self):
        # L1's contention.aggregate_cpu_limit_s_per_s defaults to null and is judged
        # only when registered; contention.aggregate_limit raises on anything but
        # null or a positive number, which the real arm would read as a NULL window.
        for value in ("0.5", 0, -1, True, float("inf")):
            with self.subTest(value=value):
                bad = json.loads(json.dumps(fake_window.THRESHOLDS))
                bad["contention"]["aggregate_cpu_limit_s_per_s"] = value
                with self.assertRaisesRegex(b5_plan.WindowPlanError,
                                            re.escape("contention.aggregate_cpu_limit_s_per_s")):
                    self.write(self.inputs(thresholds=bad))
                self.assert_nothing_written()
        absent = json.loads(json.dumps(fake_window.THRESHOLDS))
        del absent["contention"]["aggregate_cpu_limit_s_per_s"]
        record = self.write(self.inputs(thresholds=absent))
        self.assertEqual(["contention.aggregate_cpu_limit_s_per_s"],
                         record["thresholds_audit"]["optional_keys_absent"])

    def test_a_registered_optional_limit_is_kept_and_recorded(self):
        registered = json.loads(json.dumps(fake_window.THRESHOLDS))
        registered["contention"]["aggregate_cpu_limit_s_per_s"] = 0.5
        record = self.write(self.inputs(thresholds=registered))
        window = json.loads(Path(record["plan"]["path"]).read_text())["hazard_window"]
        self.assertEqual(0.5, window["thresholds"]["contention"]["aggregate_cpu_limit_s_per_s"])
        self.assertEqual([{"key": "contention.aggregate_cpu_limit_s_per_s", "value": 0.5, "default": None}],
                         record["thresholds_audit"]["differences_from_defaults"])
        try:
            from joulewise.hazards import contention
        except ImportError:
            return
        self.assertEqual(0.5, contention.aggregate_limit(window["thresholds"]["contention"]))

    def test_an_unavailable_contract_is_refused_at_the_desk(self):
        def missing():
            raise ModuleNotFoundError("No module named 'joulewise.hazards'")
        with self.assertRaisesRegex(b5_plan.WindowPlanError, "threshold contract"):
            self.write(threshold_defaults=missing)
        self.assert_nothing_written()

    def test_differences_and_replaced_sized_copies_are_recorded_and_the_window_wins(self):
        thresholds = json.loads(json.dumps(fake_window.THRESHOLDS))
        thresholds["battery"]["limit_ma"] = 150
        thresholds["thermal"]["note"] = 1
        thresholds["disk"]["planned_bytes"] = 1         # a stale copy
        thresholds["clock"]["t_stream_max_s"] = 100     # an understated copy would loosen the clock gate
        record = self.write(self.inputs(thresholds=thresholds))
        window = json.loads(Path(record["plan"]["path"]).read_text())["hazard_window"]
        self.assertEqual(window["planned_bytes"], window["thresholds"]["disk"]["planned_bytes"])
        self.assertEqual(335, window["thresholds"]["clock"]["t_stream_max_s"])
        self.assertEqual(150, window["thresholds"]["battery"]["limit_ma"])
        audit = record["thresholds_audit"]
        self.assertEqual([{"key": "battery.limit_ma", "value": 150, "default": 200}],
                         audit["differences_from_defaults"])
        self.assertEqual(["thermal.note"], audit["keys_not_in_contract"])
        self.assertEqual({"disk.planned_bytes": (1, window["planned_bytes"]), "clock.t_stream_max_s": (100, 335)},
                         {item["key"]: (item["copied"], item["window"]) for item in audit["sized_keys_replaced"]})

    def test_sizing_inputs_must_come_from_a_committed_sizing_output(self):
        good = fake_window.stream_max_allowance()
        self.assertEqual(335, good["seconds"])
        source = dict(good["source"])
        cases = {
            "a free number": {"T_stream_max_s": 335},
            "an understated value the source does not carry": {"T_stream_max_s": dict(good, seconds=300)},
            "a source digest that does not match": {"T_stream_max_s": dict(good, source=dict(source, sha256="0" * 64))},
            "a source outside the checkout": {"T_stream_max_s": dict(
                good, source=dict(source, path=str(REPO_ROOT / source["path"])))},
            "a pointer that does not resolve": {"T_stream_max_s": dict(good, source_pointer="/totals/nope")},
            "a free span": {"programmed_span_s": 3600},
        }
        for label, change in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(b5_plan.WindowPlanError):
                    self.write(self.inputs(**change))
                self.assert_nothing_written()
        record = self.write()
        self.assertEqual(good, record["sizing"]["T_stream_max_s"])
        self.assertEqual("/totals/programmed_span_s", record["sizing"]["programmed_span_s"]["source_pointer"])

    def test_the_fixture_contract_is_lane_l1s_when_its_package_is_present(self):
        try:
            real = b5_plan.hazard_threshold_defaults()
        except ImportError:
            self.skipTest("lane L1's joulewise.hazards lands at integration")
        self.assertEqual({module: set(keys) for module, keys in fake_window.L1_DEFAULT_THRESHOLDS.items()},
                         {module: set(keys) for module, keys in real.items()})


class LedgerHeadTests(WindowPlanFixture):
    """Rehearsal round 1, B5: after a window's post slot the ledger is ahead of the committed pin.

    The next window's reservation then refuses (calibration_reservation_head_mismatch)
    and its chain stops at exit 10 after the whole arm. The plan writer refuses
    that at the desk, and the desk pin advance (advance-head-pin plus a
    pin-only commit) cures it.
    """

    def setUp(self):
        super().setUp()
        for key, value in (("user.name", "fixture"), ("user.email", "fixture@example.invalid"),
                           ("commit.gpgsign", "false")):
            subprocess.run(["git", "-C", str(self.measurement), "config", "--local", key, value], check=True)
        self.ledger = self.measurement / b5_plan.DEFAULT_LEDGER_RELATIVE
        self.pin = self.measurement / b5_plan.HEAD_PIN_RELATIVE

    def reserve(self, session_id: str):
        from joulewise.calibration_ledger import IDENTITY_EPOCH_FIELDS, append_bracket_session_receipt
        from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
        epoch = dict(zip(IDENTITY_EPOCH_FIELDS, ("25F84", "Mac15,9", "ac_high_power", 100, "estimator-v1",
                                                 "pulse-v3"), strict=True))
        t1 = {field: f"value-{field}" for field in V2_BINDING_FIELDS}
        t1.update(epoch)
        runs_root = self.root / "runs-of" / session_id
        captures = runs_root / "instrument_validation"
        slots = {slot: {"attempt_id": f"{session_id}-{slot}", "custody_locator": str(captures / f"{session_id}-{slot}"),
                        "identity_epoch": epoch, "t1_bindings": t1} for slot in ("pre", "post")}
        append_bracket_session_receipt(
            self.ledger, session_id=session_id, window_id=session_id, plan_id=session_id, plan_sha256="1" * 64,
            evidence_root_id=f"evidence-{session_id}", runs_root=runs_root, slots=slots,
            head_pin_path=self.pin, require_committed_pin=True, repo_root=self.measurement)
        return slots, epoch, t1

    def finalize(self, session_id: str, slots, epoch, t1) -> None:
        from joulewise.calibration_ledger import artifact_hashes, finalize_bracket_session_slot
        for slot in ("pre", "post"):
            capture = Path(slots[slot]["custody_locator"])
            (capture / "raw").mkdir(parents=True)
            (capture / "raw" / "powermetrics.plist").write_bytes(f"raw-{slot}".encode())
            (capture / "events.jsonl").write_text('{"timestamp_s":99.0}\n')
            (capture / "instrument_evidence.json").write_text(json.dumps({"slot": slot}))
            (capture / "manifest.json").write_text(json.dumps({"slot": slot}))
            finalize_bracket_session_slot(
                self.ledger, session_id=session_id, slot=slot, disposition="valid", custody_locator=str(capture),
                artifact_sha256=artifact_hashes(capture), identity_epoch=epoch, t1_bindings=t1,
                capture_wall_time_s="99.0" if slot == "pre" else "111.0", exact_bound_lexeme_s="0.025")

    def test_a_ledger_ahead_of_its_committed_pin_is_refused_at_the_desk_and_cured_by_the_pin_advance(self):
        from joulewise.calibration_exits import RefusalCode
        from joulewise.calibration_ledger import CalibrationLedgerError, terminal_head_pin_for_session
        # ALPHA: its bracket session reserves at the committed pin and finalizes both slots.
        self.finalize("alpha-1-calibration", *self.reserve("alpha-1-calibration"))
        status = b5_plan.ledger_head_status(self.measurement)
        self.assertEqual(["calibration_ledger_head_mismatch"], status["blocking"])
        self.assertEqual(0, status["pinned"]["sequence"])
        self.assertGreater(status["physical"]["sequence"], 0)
        # BETA's reservation against it refuses, as in the rehearsal.
        with self.assertRaises(CalibrationLedgerError) as refused:
            self.reserve("beta-1-calibration")
        self.assertEqual(RefusalCode.RESERVATION_HEAD_MISMATCH, refused.exception.code)
        # The plan writer refuses at the desk, names the cure, and writes nothing.
        with self.assertRaisesRegex(b5_plan.WindowPlanError, "calibration_ledger_head_mismatch.*advance_b5_ledger_pin"):
            self.write()
        self.assert_nothing_written()
        # The desk pin advance, against the harvest's terminal pin.
        terminal = terminal_head_pin_for_session(self.ledger, session_id="alpha-1-calibration")
        wrong = dict(terminal, sequence=terminal["sequence"] - 1)
        with self.assertRaisesRegex(b5_plan.PinAdvanceError, "not the harvested terminal pin"):
            b5_plan.advance_ledger_pin(self.measurement, session_id="alpha-1-calibration", operator_identity="test",
                                       attestation_reason="test", expected_pin=wrong)
        record = b5_plan.advance_ledger_pin(self.measurement, session_id="alpha-1-calibration",
                                            operator_identity="test", attestation_reason="test", expected_pin=terminal)
        self.assertEqual("ADVANCED", record["status"])
        self.assertEqual([b5_plan.HEAD_PIN_RELATIVE], record["commit"]["changed_paths"])
        self.assertEqual([], record["after"]["blocking"])
        changed = subprocess.run(["git", "-C", str(self.measurement), "show", "--name-only", "--format=", "HEAD"],
                                 capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual([b5_plan.HEAD_PIN_RELATIVE], changed)
        self.assertEqual(terminal["sequence"], json.loads(self.pin.read_text())["sequence"])
        # Now the next window plans, and its reservation opens.
        record = self.write()
        self.assertEqual([], record["ledger_head"]["blocking"])
        beta = self.reserve("beta-1-calibration")
        # The next harvest's advance, then one with nothing to do, which changes nothing.
        self.finalize("beta-1-calibration", *beta)
        again = b5_plan.advance_ledger_pin(self.measurement, session_id="beta-1-calibration",
                                           operator_identity="test", attestation_reason="test")
        self.assertEqual("ADVANCED", again["status"])
        self.assertEqual("NOT_NEEDED", b5_plan.advance_ledger_pin(
            self.measurement, session_id="beta-1-calibration", operator_identity="test",
            attestation_reason="test")["status"])

    def test_an_uncommitted_pin_and_an_open_session_are_refused_at_the_desk(self):
        slots = self.reserve("alpha-1-calibration")
        with self.assertRaisesRegex(b5_plan.WindowPlanError, "calibration_ledger_bracket_session_open.*abort-session"):
            self.write()
        self.assert_nothing_written()
        with self.assertRaisesRegex(b5_plan.PinAdvanceError, "not in a pin-advance state"):
            b5_plan.advance_ledger_pin(self.measurement, session_id="alpha-1-calibration", operator_identity="test",
                                       attestation_reason="test")
        self.finalize("alpha-1-calibration", *slots)
        record = b5_plan.advance_ledger_pin(self.measurement, session_id="alpha-1-calibration",
                                            operator_identity="test", attestation_reason="test", commit=False)
        self.assertEqual("ADVANCED_UNCOMMITTED", record["status"])
        self.assertEqual(["calibration_ledger_head_uncommitted"], record["after"]["blocking"])
        with self.assertRaisesRegex(b5_plan.WindowPlanError, "calibration_ledger_head_uncommitted"):
            self.write()
        self.assert_nothing_written()
        # The CLI commits it.
        plan = self.root / "previous-plan.json"
        plan.write_text(json.dumps({"measurement_root": str(self.measurement),
                                    "hazard_window": {"bracket_session_id": "alpha-1-calibration"}}))
        output = io.StringIO()
        with redirect_stdout(output):
            code = __import__("scripts.advance_b5_ledger_pin", fromlist=["main"]).main(
                ["--plan", str(plan), "--operator-identity", "test"])
        self.assertEqual(0, code, output.getvalue())
        self.assertEqual("ADVANCED", json.loads(output.getvalue())["status"])
        self.write()


class HazardWindowValidationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path("/fixture/b5")

    def window(self):
        return fake_window.hazard_window_mapping(self.root, pack_root=REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5")

    def test_valid_window_round_trips(self):
        self.assertEqual(self.window(), night_gate.validate_hazard_window(self.window()))

    def test_structural_defects_are_refused(self):
        cases = {
            "extra key": lambda w: w.update(extra=1),
            "missing thresholds module": lambda w: w["thresholds"].pop("clock"),
            "bindings not fourteen": lambda w: w["bindings"].pop("ledger_path"),
            "bracket session drift": lambda w: w.update(bracket_session_id="other"),
            "runs root drift": lambda w: w["runs_roots"].update(claim="/fixture/elsewhere"),
            "relative volume": lambda w: w.update(disk_volumes=["relative/path"]),
            "g10 not boolean": lambda w: w.update(g10="yes"),
            "pack basename": lambda w: w["pack"].update(pack_id="other"),
            "stage shape": lambda w: w["stages"][0].pop("in_chain"),
            "negative span": lambda w: w.update(programmed_span_s=0),
        }
        for label, mutate in cases.items():
            with self.subTest(case=label):
                window = self.window()
                mutate(window)
                with self.assertRaises(ValueError):
                    night_gate.validate_hazard_window(window)


if __name__ == "__main__":
    unittest.main()
