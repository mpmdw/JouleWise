"""The protected-core flag helper on the HAZARD_PACK path (core-prune N1).

``joulewise.flags.core`` is glue over ``make_flag`` and ``FlagSink``: it decides
whether a runs root is a HAZARD window (the hazard lineage locator), where that
window's flags go (``<custody>/flags/<writer>.jsonl``), which plan id and
attempt they carry (the window plan's, never the lineage's), and what happens
when a flag cannot be written (printed whole behind ``UNWRITTEN_MARKER``).
These tests pin that contract, carry it end to end through the harvest, and
keep the code vocabulary equal across the helper, the draft catalog, the
harvest's fixture catalog and the harvest's own code table.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from joulewise import window_lineage
from joulewise.arm_readiness import LAUNCH_LINEAGE_LOCATOR_SCHEMA
from joulewise.flags import core as flags_core
from joulewise.flags.catalog import (
    DISCLOSE,
    DRAFT_CODES,
    EXCLUDE_MEMBER,
    EXCLUDE_WINDOW,
    SEALED_CATALOG_RELATIVE_PATH,
    UNCLASSIFIED,
    load_catalog,
)
from joulewise.flags.schema import validate_flag

REPO = Path(__file__).resolve().parents[2]
FIXTURE_CATALOG = REPO / "tests/fixtures/b5_harvest/flag_catalog.json"
PLAN_ID = "plan-core-flags"

# DESIGN.md section 5: code -> (family, klass, effect).
SECTION_5 = {
    "calibration.capture_battery_pair_unverified": ("CALIBRATION", "PHYSICS", DISCLOSE),
    "records.pin_ledger": ("RECORDS", "REPRESENTATION", DISCLOSE),
    "calibration.power_policy_unverified": ("CALIBRATION", "REPRESENTATION", DISCLOSE),
    "instrument.binary_identity_unmeasured": ("INSTRUMENT", "NUMBER", EXCLUDE_MEMBER),
    "env.member_quiet_state_violated": ("MEMBER_VALIDITY", "PHYSICS", EXCLUDE_MEMBER),
    "env.member_guard_flagged": ("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "member.idle_admission_telemetry_missing": ("MEMBER_VALIDITY", "PHYSICS", EXCLUDE_MEMBER),
    "teardown.survivors": ("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "cooldown.result_unknown": ("DIAGNOSTIC", "PHYSICS", DISCLOSE),
    "env.stage_preflight_not_admitted": ("DIAGNOSTIC", "REPRESENTATION", DISCLOSE),
    "campaign.runner_record_flagged": ("RECORDS", "REPRESENTATION", DISCLOSE),
    "calibration.writer_record_flagged": ("CALIBRATION", "REPRESENTATION", DISCLOSE),
    "code.executed_differs_from_sealed": ("CODE_IDENTITY", "NUMBER", EXCLUDE_WINDOW),
    "calibration.capture_invalid": ("CALIBRATION", "NUMBER", EXCLUDE_WINDOW),
    "neg8.corpus_member_dropped": ("NEG8", "REPRESENTATION", DISCLOSE),
    "calibration.capture_battery_span": ("CALIBRATION", "PHYSICS", EXCLUDE_WINDOW),
    "calibration.capture_battery_unmeasured": ("CALIBRATION", "PHYSICS", EXCLUDE_WINDOW),
    # Gate-prune round 2, lane P2-CHAIN (the block-5 chain, writer b5-chain).
    "roster.horizon_truncated": ("ROSTER", "REPRESENTATION", DISCLOSE),
    "member.retried": ("ROSTER", "REPRESENTATION", DISCLOSE),
    # Gate-prune round 2, lane P2-RC.
    "member.timeout": ("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    "member.stderr_uncopied": ("MEMBER_VALIDITY", "NUMBER", EXCLUDE_MEMBER),
    # Gate-prune round 2, lane P2-CTL (controller).
    "calibration.refit_cache_miss": ("CALIBRATION", "REPRESENTATION", DISCLOSE),
    "records.auxiliary_match_raised": ("RECORDS", "REPRESENTATION", DISCLOSE),
}
# Core codes whose consumer tables (DRAFT_CODES, the harvest's CODES and
# CORE_WRITER_CODES, the fixture catalog) were still to be filled by lane
# P2-HARV.  Empty since integration int3: every core code is cross-checked in full.
PRUNE2_CONSUMER_PENDING = frozenset()
HARVEST_NONCORE_CODES = ("neg8.corpus_member_dropped", "calibration.capture_battery_span",
                         "calibration.capture_battery_unmeasured", "calibration.capture_invalid")
# The protected-core files whose literal codes must be in CORE_FLAG_CODES.
CORE_WRITER_FILES = ("joulewise/controller.py", "scripts/run_campaign.py",
                     "scripts/validate_powermetrics_fiducial.py", "scripts/reserve_calibration_window_bracket.py")


def hazard_root(base: Path, custody: Path | None, *, plan: dict | None = None, name: str = "runs") -> Path:
    """A runs root carrying the hazard locator, and (optionally) the custody's window plan."""

    root = base / name
    root.mkdir(parents=True)
    context = {"custody_root": str(custody) if custody is not None else None}
    (root / window_lineage.LOCATOR_BASENAME).write_text(json.dumps({
        "schema_version": window_lineage.HAZARD_LOCATOR_SCHEMA, "root_role": "claim_runs_root",
        "root_path": str(root), "launch_lineage": {"window_context": context}}))
    if custody is not None and plan is not None:
        custody.mkdir(parents=True, exist_ok=True)
        (custody / flags_core.WINDOW_PLAN_BASENAME).write_text(json.dumps(plan))
    return root


def window_plan(attempt=2) -> dict:
    return {"plan_id": PLAN_ID, "hazard_window": {"attempt": attempt}}


def lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def marker_lines(text: str) -> list[str]:
    return [line[len(flags_core.UNWRITTEN_MARKER):] for line in text.splitlines()
            if line.startswith(flags_core.UNWRITTEN_MARKER)]


class HazardContextTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name).resolve()

    def test_legacy_roots_have_no_context(self):
        plain = self.base / "plain"
        plain.mkdir()
        arm = self.base / "arm"
        arm.mkdir()
        (arm / window_lineage.LOCATOR_BASENAME).write_text(json.dumps(
            {"schema_version": LAUNCH_LINEAGE_LOCATOR_SCHEMA, "launch_lineage": {}}))
        garbage = self.base / "garbage"
        garbage.mkdir()
        (garbage / window_lineage.LOCATOR_BASENAME).write_bytes(b"\xff not json")
        for root in (None, plain, arm, garbage, self.base / "absent", "\0bad"):
            with self.subTest(root=root):
                self.assertIsNone(flags_core.hazard_flag_context(root, writer="core-controller"))

    def test_hazard_locator_and_window_plan_resolve_custody_plan_and_attempt(self):
        custody = self.base / "custody"
        root = hazard_root(self.base, custody, plan=window_plan(attempt=3))
        context = flags_core.hazard_flag_context(root, writer="core-run_campaign", stage="harvest")
        self.assertEqual((context.custody_root, context.plan_id, context.attempt, context.scope_resolved,
                          context.stage, context.writer),
                         (custody, PLAN_ID, 3, True, "harvest", "core-run_campaign"))
        self.assertEqual(context.path, custody / "flags" / "core-run_campaign.jsonl")

    def test_missing_or_partial_plan_leaves_null_bindings_unresolved(self):
        cases = {"missing": None, "no_attempt": {"plan_id": PLAN_ID, "hazard_window": {}},
                 "bool_attempt": {"plan_id": PLAN_ID, "hazard_window": {"attempt": True}},
                 "no_plan_id": {"hazard_window": {"attempt": 1}}}
        for name, plan in cases.items():
            with self.subTest(name):
                custody = self.base / name / "custody"
                root = hazard_root(self.base / name, custody, plan=plan)
                context = flags_core.hazard_flag_context(root, writer="core-fiducial")
                self.assertEqual((context.custody_root, context.plan_id, context.attempt, context.scope_resolved),
                                 (custody, None, None, False))

    def test_relative_or_absent_custody_has_no_path(self):
        root = hazard_root(self.base, None)
        context = flags_core.hazard_flag_context(root, writer="core-controller")
        self.assertIsNotNone(context)  # still HAZARD: the dispatch is the locator schema
        self.assertIsNone(context.custody_root)
        self.assertIsNone(context.path)
        relative = self.base / "relative"
        relative.mkdir()
        (relative / window_lineage.LOCATOR_BASENAME).write_text(json.dumps({
            "schema_version": window_lineage.HAZARD_LOCATOR_SCHEMA,
            "launch_lineage": {"window_context": {"custody_root": "custody"}}}))
        self.assertIsNone(flags_core.hazard_flag_context(relative, writer="core-controller").custody_root)

    def test_a_published_lineage_gives_its_custody_root(self):
        from tests.test_window_lineage import build_window

        w = build_window(self.base / "published")
        for root in (w.claim, w.bound):
            context = flags_core.hazard_flag_context(root, writer="core-controller")
            self.assertIsNotNone(context)
            self.assertEqual(context.custody_root, w.custody)


class EmitTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name).resolve()
        self.custody = self.base / "custody"
        root = hazard_root(self.base, self.custody, plan=window_plan())
        self.context = flags_core.hazard_flag_context(root, writer="core-controller")

    def emit(self, context, code, **kwargs):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            written = flags_core.emit(context, code, **kwargs)
        return written, stderr.getvalue()

    def test_one_valid_record_and_a_repeat_is_deduplicated(self):
        for _ in range(2):
            written, stderr = self.emit(self.context, "records.pin_ledger", level="window",
                                        observed={"refusal_reasons": ["head_mismatch"]},
                                        legacy_site="joulewise/controller.py:631@e6b6a0ce")
            self.assertEqual((written, stderr), (True, ""))
        records = lines(self.context.path)
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(validate_flag(record), [])
        self.assertEqual((record["code"], record["family"], record["klass"], record["blinding"]),
                         ("records.pin_ledger", "RECORDS", "REPRESENTATION", "STRUCTURE"))
        self.assertEqual({key: record["scope"][key] for key in ("level", "plan_id", "attempt")},
                         {"level": "window", "plan_id": PLAN_ID, "attempt": 2})
        self.assertEqual(record["source"], {"stage": "window", "collector": "core.core-controller",
                                            "legacy_site": "joulewise/controller.py:631@e6b6a0ce",
                                            "legacy_code": None})

    def test_member_scope_names_the_run_and_without_one_widens_to_the_window(self):
        self.emit(self.context, "teardown.survivors", level="member", run_id="r07", observed={"kind": "sampler"})
        self.emit(self.context, "teardown.survivors", level="member", observed={"kind": "runtime"})
        first, second = lines(self.context.path)
        self.assertEqual((first["scope"]["level"], first["scope"]["run_id"], first["scope"]["bundle_id"]),
                         ("member", "r07", "r07"))
        self.assertEqual((second["scope"]["level"], second["scope"]["run_id"]), ("window", None))
        self.assertEqual(second["observed"], {"value": {"kind": "runtime"}, "run_id_missing": True})

    def test_unknown_code_is_written_and_the_fixture_catalog_leaves_it_unclassified(self):
        written, _ = self.emit(self.context, "core.not_in_the_table", level="window", observed=1)
        self.assertTrue(written)
        (record,) = lines(self.context.path)
        self.assertEqual((record["family"], record["klass"]), flags_core.UNKNOWN_CODE_CLASS)
        self.assertEqual(load_catalog(FIXTURE_CATALOG).effect("core.not_in_the_table"), UNCLASSIFIED)

    def test_unserializable_observed_is_replaced_not_dropped(self):
        written, _ = self.emit(self.context, "teardown.survivors", level="member", run_id="r1",
                               observed={"path": Path("/x")}, expected=float("nan"))
        self.assertTrue(written)
        (record,) = lines(self.context.path)
        self.assertEqual(set(record["observed"]), {"unserializable"})
        self.assertIn("PosixPath", record["observed"]["unserializable"])
        self.assertEqual(set(record["expected"]), {"unserializable"})

    def test_unresolved_scope_is_recorded_in_observed(self):
        root = hazard_root(self.base / "no-plan", self.base / "no-plan" / "custody")
        context = flags_core.hazard_flag_context(root, writer="core-fiducial")
        self.assertTrue(self.emit(context, "calibration.writer_record_flagged", level="window",
                                  observed={"kind": "display_sleep_action_failed"})[0])
        (record,) = lines(context.path)
        self.assertEqual((record["scope"]["plan_id"], record["scope"]["attempt"]), (None, None))
        self.assertEqual(record["observed"], {"value": {"kind": "display_sleep_action_failed"},
                                              "scope_unresolved": True})

    def test_unwritable_flags_print_the_whole_flag_behind_the_marker(self):
        unresolved = flags_core.HazardFlagContext(writer="core-controller", custody_root=None, plan_id=PLAN_ID,
                                                  attempt=2, scope_resolved=True)
        blocked_custody = self.base / "blocked"
        blocked_custody.mkdir()
        (blocked_custody / flags_core.FLAGS_DIRNAME).write_text("a file where the flags directory goes")
        blocked = flags_core.HazardFlagContext(writer="core-controller", custody_root=blocked_custody,
                                               plan_id=PLAN_ID, attempt=2, scope_resolved=True)
        for name, context in (("custody_unresolved", unresolved), ("directory_unwritable", blocked)):
            with self.subTest(name):
                written, stderr = self.emit(context, "instrument.binary_identity_unmeasured", level="member",
                                            run_id="r03", observed={"device_metadata": "no executable_sha256"})
                self.assertFalse(written)
                (line,) = marker_lines(stderr)
                record = json.loads(line)
                self.assertEqual(validate_flag(record), [])
                self.assertEqual((record["code"], record["scope"]["run_id"], record["scope"]["plan_id"]),
                                 ("instrument.binary_identity_unmeasured", "r03", PLAN_ID))

    def test_a_flag_that_cannot_be_built_still_prints_its_code(self):
        written, stderr = self.emit(self.context, "Not A Code", level="window")
        self.assertFalse(written)
        (line,) = marker_lines(stderr)
        value = json.loads(line)
        self.assertEqual(value["code"], "Not A Code")
        self.assertIn("FlagSchemaError", value["unbuilt"])
        self.assertTrue(validate_flag(value))  # not a flag: the harvest makes it records.malformed_flag
        self.assertFalse(self.context.path.exists())

    def test_the_legacy_path_writes_and_prints_nothing(self):
        written, stderr = self.emit(None, "records.pin_ledger", level="window")
        self.assertEqual((written, stderr), (False, ""))
        self.assertFalse((self.custody / "flags").exists())


class HarvestFoldTests(unittest.TestCase):
    """A core flag file in a window's custody reaches the harvest's exclusions with its catalog effect."""

    def test_core_flags_are_folded_and_the_fixture_catalog_effect_applies(self):
        import shutil
        from unittest import mock

        from joulewise.b5 import harvest as h
        from tests import test_harvest_b5_window as harvest_tests
        from tests.test_harvest_b5_window import MEMBERS, PLAN_ID as WINDOW_PLAN_ID, Window, cached_assess

        # A template of its own: that module's tearDownModule removes its shared template when its
        # own tests end, without forgetting it, and this test may run after them in one process.
        def drop_template():
            if harvest_tests._TEMPLATE is not None:
                shutil.rmtree(harvest_tests._TEMPLATE, ignore_errors=True)

        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(mock.patch.object(harvest_tests, "_TEMPLATE", None))
        stack.callback(drop_template)
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(h, "assess_member", cached_assess):
            base = Path(directory).resolve()
            window = Window(base / "w", catalog_overrides={"member.cooldown_evidence_unverified": "DISCLOSE"})
            # The context a core writer in this window computes: the window plan's id and attempt.
            root = hazard_root(base, window.custody, name="core-runs")
            context = flags_core.hazard_flag_context(root, writer="core-controller")
            self.assertEqual((context.plan_id, context.attempt, context.scope_resolved), (WINDOW_PLAN_ID, 1, True))
            run_id = MEMBERS[0][0]
            for code, level, member in (("instrument.binary_identity_unmeasured", "member", run_id),
                                        ("records.pin_ledger", "window", None),
                                        ("calibration.capture_battery_pair_unverified", "window", None)):
                self.assertTrue(flags_core.emit(context, code, level=level, run_id=member, observed={"t": 1}))
            window.harvest()
            codes = {flag["code"]: flag for flag in window.flags()}
            for code in ("instrument.binary_identity_unmeasured", "records.pin_ledger",
                         "calibration.capture_battery_pair_unverified"):
                self.assertIn(code, codes)
            self.assertNotIn("records.malformed_flag", codes)
            exclusions = window.exclusions()
            excluded = {row["run_id"]: row["codes"] for row in exclusions["members_excluded"]}
            self.assertIn("instrument.binary_identity_unmeasured", excluded[run_id])
            self.assertFalse({"records.pin_ledger", "calibration.capture_battery_pair_unverified"}
                             & set(exclusions["reasons"]))
            self.assertEqual(window.window_flags()["flags"]["unclassified"], [])


class VocabularyTests(unittest.TestCase):
    """Interface I5: CORE_FLAG_CODES = fixture catalog = DRAFT_CODES = harvest CODES (= sealed draft)."""

    def test_every_core_code_has_its_section_5_classification_everywhere(self):
        from joulewise.b5 import harvest as h

        fixture = json.loads(FIXTURE_CATALOG.read_bytes())["codes"]
        for code, (family, klass) in flags_core.CORE_FLAG_CODES.items():
            with self.subTest(code):
                expected = SECTION_5[code]
                self.assertEqual((family, klass), expected[:2])
                if code in PRUNE2_CONSUMER_PENDING and code not in DRAFT_CODES:
                    continue
                self.assertEqual((DRAFT_CODES[code]["family"], DRAFT_CODES[code]["klass"],
                                  DRAFT_CODES[code]["effect"]), expected)
                self.assertEqual((fixture[code]["family"], fixture[code]["klass"], fixture[code]["effect"]),
                                 expected)
                self.assertEqual((h.CODES[code].family, h.CODES[code].klass), expected[:2])
        pending = {code for code in PRUNE2_CONSUMER_PENDING if code not in h.CORE_WRITER_CODES}
        self.assertEqual(set(flags_core.CORE_FLAG_CODES) - {"code.executed_differs_from_sealed"} - pending,
                         set(h.CORE_WRITER_CODES))
        self.assertEqual(set(flags_core.WRITERS),
                         {"core-controller", "core-run_campaign", "core-fiducial", "core-reservation"})

    def test_the_harvest_codes_of_this_lane_are_classified(self):
        from joulewise.b5 import harvest as h

        fixture = json.loads(FIXTURE_CATALOG.read_bytes())["codes"]
        for code in HARVEST_NONCORE_CODES:
            with self.subTest(code):
                expected = SECTION_5[code]
                self.assertEqual((DRAFT_CODES[code]["family"], DRAFT_CODES[code]["klass"],
                                  DRAFT_CODES[code]["effect"]), expected)
                self.assertEqual((fixture[code]["family"], fixture[code]["klass"], fixture[code]["effect"]),
                                 expected)
                self.assertEqual((h.CODES[code].family, h.CODES[code].klass), expected[:2])

    def test_the_harvest_reads_the_helpers_marker(self):
        from joulewise.b5 import harvest as h

        self.assertEqual(h.UNWRITTEN_MARKER, flags_core.UNWRITTEN_MARKER)

    def test_the_sealed_catalog_classifies_them_when_present(self):
        sealed = REPO / SEALED_CATALOG_RELATIVE_PATH
        if not sealed.exists():
            self.skipTest("the sealed catalog is not in this tree (the orchestrator adds these codes to the draft)")
        catalog = load_catalog(sealed)
        for code, expected in SECTION_5.items():
            entry = catalog.codes.get(code)
            self.assertIsNotNone(entry, code)
            self.assertEqual((entry["family"], entry["klass"], entry["effect"]), expected, code)

    def test_every_literal_code_a_core_writer_emits_is_in_the_table(self):
        found: dict[str, list[str]] = {}
        for relative in CORE_WRITER_FILES:
            tree = ast.parse((REPO / relative).read_text(encoding="utf-8"), filename=relative)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                function = node.func
                if not (isinstance(function, ast.Attribute) and function.attr == "emit"
                        and isinstance(function.value, ast.Name) and function.value.id == "flags_core"):
                    continue
                arguments = list(node.args[1:2]) + [keyword.value for keyword in node.keywords
                                                    if keyword.arg == "code"]
                for argument in arguments:
                    if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                        found.setdefault(argument.value, []).append(f"{relative}:{node.lineno}")
        unknown = {code: sites for code, sites in found.items() if code not in flags_core.CORE_FLAG_CODES}
        self.assertEqual(unknown, {})

    def test_the_scan_sees_a_literal_code(self):
        # The scan above is vacuous on a tree where no core writer emits yet; prove it would catch one.
        source = "def f(ctx):\n    flags_core.emit(ctx, 'core.unlisted', level='window')\n"
        node = next(item for item in ast.walk(ast.parse(source)) if isinstance(item, ast.Call))
        self.assertEqual((node.func.value.id, node.func.attr, node.args[1].value),
                         ("flags_core", "emit", "core.unlisted"))


if __name__ == "__main__":
    unittest.main()
