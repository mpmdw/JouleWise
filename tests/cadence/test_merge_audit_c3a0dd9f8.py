"""The merge audit of PR #795 at c3a0dd9f8 (2026-11-23): its three verified findings as named regressions, each fixed
as a class with one rule. Every custody byte, ledger and repository here is generated; no recording is read.

1. Validate before open. Every refusal stage 1 can decide from its inputs (the roster, the rules-3/4 verdict file,
   the ruled exclusions, the run mode) and from the operational custody files is decided for the whole roster
   before the first protected source (a trace, telemetry, powermetrics or meter stream) opens.
2. Observed, not expected. A public Check binds only a full observed offload manifest digest; a pending, malformed,
   conflicting or expected-only observation holds the span.
3. Fail closed on fetch. An authority is resolved only from a ref fetched now: freeze 2 fetches main before it
   resolves main and, on the naming path, the audit branch before the ancestry test; ``row`` records an outcome
   against main as fetched now. A failed required fetch refuses.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from joulewise.cadence_looks import custody_pins as P
from joulewise.cadence_looks import inclusion_34 as I34
from joulewise.cadence_looks import interim_release as C
from joulewise.cadence_looks import manifest as M
from tests.cadence import custody_pin_fixture as PF
from tests.cadence import look_layout_fixture as LF
from tests.cadence import look_minirepo as MR

try:
    from scripts import cadence_look_run as R
    from scripts import cadence_look_synth as SY
    from joulewise.cadence_looks import fit_interim as F
except ModuleNotFoundError as exc:
    if exc.name != "numpy":
        raise
    R = SY = F = None

LOOK = "lm-interim-01"
PROTECTED_NAMES = ("power_trace.csv", "rich_telemetry.jsonl", "powermetrics.plist")
_RECORDING = []          # the open being recorded: a list of protected paths, or nothing


def _protected(path):
    return os.path.basename(path) in PROTECTED_NAMES or "/hazards/meter/" in path.replace(os.sep, "/")


def _audit(event, args):
    if _RECORDING and event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        path = os.fsdecode(args[0])
        if _protected(path):
            _RECORDING[-1].append(path)


sys.addaudithook(_audit)          # passive: it records only while a test holds a list in _RECORDING


class _Opens:
    """Every protected source this process opens while the block runs (the ``open`` audit event: builtins.open,
    io.open, os.open and io.FileIO alike)."""

    def __enter__(self):
        self.paths = []
        _RECORDING.append(self.paths)
        return self.paths

    def __exit__(self, *exc):
        _RECORDING.remove(self.paths)
        return False


def _rj(path):
    return json.loads(Path(path).read_text())


def _wj(path, doc):
    Path(path).write_text(json.dumps(doc))


# ============================================================================================ finding 1, its class
@unittest.skipIf(F is None, "numpy is not installed; runs in the look-fit CI job")
class ValidateBeforeOpen(unittest.TestCase):
    """Finding 1 (cadence_look_run.py:601 at c3a0dd9f8): the verdict for a roster leg of the second span was looked
    up after the first span's meter stream and telemetry had been opened. The class: each refusing precondition of
    ``admit_look_input``, planted in the roster's second span (or its inputs), refuses with no protected source
    opened. The unchanged custody opens them (the instrument sees opens), and at c3a0dd9f8 nine of these cases
    opened 5 to 60 protected files before refusing, and five were admitted."""

    S1, S2 = "dev-01-s01", "dev-01-s02"

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="validate-before-open-")
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.source = Path(cls.tmp.name) / "custody"
        tokens = {}
        li, en, _ = SY.build("exact", tokens=tokens)
        wanted = {f"{sid}/L00{leg}" for sid in (cls.S1, cls.S2) for leg in (1, 2, 3)}
        li["legs"] = [leg for leg in li["legs"] if leg["leg_key"] in wanted]
        li["spans"] = [span for span in li["spans"] if span["span_id"] in (cls.S1, cls.S2)]
        SY.write_custody(str(cls.source), li, en, tokens)
        cls.roster = _rj(cls.source / "roster.json")
        selected = I34.keys(_rj(MR.REPO / I34.RUNTIME_CONFIG)["sensors"])
        cls.verdicts = I34.judge_custody(cls.roster, LF.span_dirs(cls.source, []), selected)[0]
        assert [entry["span_id"] for entry in cls.roster] == [cls.S1, cls.S2]
        assert all(all(v.values()) for v in cls.verdicts.values())

    def custody(self):
        td = tempfile.TemporaryDirectory(prefix="validate-before-open-case-")
        self.addCleanup(td.cleanup)
        root = Path(td.name) / "custody"
        shutil.copytree(self.source, root)
        return root

    def bundle(self, root, sid, leg="L001"):
        rec = _rj(root / sid / "legs" / leg / "leg_record.json")
        return root / sid / "legs" / leg / "runtime" / rec["result"]["bundle"]

    def read(self, root, roster=None, verdicts=None, **kwargs):
        return R.read_look_input(self.roster if roster is None else roster, LF.span_dirs(root, []),
                                 self.verdicts if verdicts is None else verdicts, **kwargs)

    def cases(self):
        """{name: (change(root) -> read keywords, the refusal's text)}. Each plants one refusing precondition."""
        S1, S2 = self.S1, self.S2
        r0, r1 = self.roster

        def verdicts(change):
            return lambda root: {"verdicts": change(json.loads(json.dumps(self.verdicts)))}

        def roster(second):
            return lambda root: {"roster": [r0, *second]}

        def leg_record(change):
            def plant(root):
                path = root / S2 / "legs/L001/leg_record.json"
                doc = _rj(path)
                change(doc)
                _wj(path, doc)
                return {}
            return plant

        def compressed_meter(root):
            stream = next((root / S2 / "hazards/meter").glob("stream-*.jsonl"))
            Path(str(stream) + ".zst").write_bytes(b"generated")
            return {}

        def compressed_trace(root):
            Path(str(self.bundle(root, S2) / "power_trace.csv") + ".zst").write_bytes(b"generated")
            return {}

        def no_such_leg(root):
            return {"ruled": {f"{S2}/L099": ("km003c_clean", "RL-999")}}

        def zero_prefill(root):
            return {"_zero_prefill": True}

        def unreadable_turn(root):
            # the second span's first leg, which its record and verdicts include, gives no turn from its journals
            return {"_turn_fault": True}

        return {
            # the audit's two cases: a missing verdict for a leg of the first and of the second span
            "audit 1: no verdict for the first span's leg": (
                verdicts(lambda v: {k: x for k, x in v.items() if k != f"{S1}/L001"}),
                "no verdict for a roster leg"),
            "audit 1: no verdict for the second span's leg": (
                verdicts(lambda v: {k: x for k, x in v.items() if k != f"{S2}/L002"}),
                "no verdict for a roster leg"),
            "a verdict that is not two booleans": (
                verdicts(lambda v: {**v, f"{S2}/L002": {"sidecar_coverage": "yes", "km003c_clean": True}}),
                "verdict is not sidecar_coverage and km003c_clean as booleans"),
            "a verdict with another member": (
                verdicts(lambda v: {**v, f"{S2}/L002": {**v[f"{S2}/L002"], "note": True}}),
                "verdict is not sidecar_coverage and km003c_clean as booleans"),
            "a verdict file that is not an object": (verdicts(lambda v: sorted(v)), "not an object of leg verdicts"),
            "a roster role that is neither fit nor describe": (roster([dict(r1, role="support")]),
                                                                "roster: a role is neither fit nor describe"),
            "audit r7 2: a block id the registry refuses": (roster([dict(r1, block_id="Dev-01")]),
                                                           "roster: a block_id is not a registered block id"),
            "every development leg with zero prefill seconds": (zero_prefill, "zero prefill or decode seconds on every"),
            "a roster entry with no day": (
                roster([{k: x for k, x in r1.items() if k != "t0_local_date"}]), "roster: a span entry"),
            "a roster day that is not the receipt's": (roster([dict(r1, t0_local_date="2026-01-01")]),
                                                       "t0_local_date: must match"),
            "a span twice on the roster": (roster([r1, r1]), "roster: a span appears twice"),
            "a ruled exclusion of a leg with no record": (no_such_leg, "a ruled exclusion names a leg with no record"),
            "a desk-compressed meter stream": (compressed_meter, "desk-compressed"),
            "a desk-compressed GPU trace": (compressed_trace, "GPU rail: dev-01-s02/L001: power_trace.csv.zst"),
            "a cell that is not registered": (leg_record(lambda d: d["spec"].update(prefill_tokens=1234)),
                                              "cell_prompt_tokens is not a registered cell"),
            "an included leg whose journals give no turn": (unreadable_turn, "included leg's bundle has no readable turn"),
        }

    def test_the_unchanged_custody_opens_protected_sources(self):
        with _Opens() as opened:
            li = self.read(self.custody())
        self.assertTrue(any(path.endswith("power_trace.csv") for path in opened), opened)
        self.assertTrue(any("/hazards/meter/" in path for path in opened), opened)
        self.assertEqual({leg["span_id"] for leg in li["legs"]}, {self.S1, self.S2})

    def test_every_refusing_precondition_opens_no_protected_source(self):
        original = getattr(R, "turn_operational", None)
        for name, (plant, text) in self.cases().items():
            with self.subTest(name):
                root = self.custody()
                kwargs = plant(root)
                fault = kwargs.pop("_turn_fault", False)
                zero = kwargs.pop("_zero_prefill", False)

                def turn(bundle, result, fan_keys):
                    if fault and f"/{self.S2}/legs/L001/" in str(bundle):
                        raise KeyError("generated")
                    got = original(bundle, result, fan_keys)
                    if zero:         # the turn starts at its first token: a valid turn with no prefill seconds
                        got["turn_start_s"] = got["segments"][0]["wall_start_s"] = got["first_token_s"]
                        got["journal"] = [r for r in got["journal"] if r["t_s"] >= got["turn_start_s"] - 60.0]
                    return got
                with mock.patch.object(R, "turn_operational", side_effect=turn, create=True), _Opens() as opened:
                    with self.assertRaisesRegex(F.LookInputError, text):
                        self.read(root, **kwargs)
                self.assertEqual(opened, [], f"{name}: protected sources opened before the refusal")

    def test_allow_draft_on_custody_that_is_not_synthetic_refuses_before_any_open(self):
        root = self.custody()
        with mock.patch.object(R, "_json", side_effect=lambda path: (
                dict(R.M.strict_json(Path(path).read_text()), synthetic=False)
                if Path(path).name == "runner_receipt.json" and self.S2 in str(path)
                else R.M.strict_json(Path(path).read_text()))), _Opens() as opened:
            with self.assertRaisesRegex(F.LookInputError, "synthetic input only"):
                self.read(root, synthetic_only=True)
        self.assertEqual(opened, [])


    def test_every_roster_field_with_an_invalid_value_refuses_before_any_open(self):
        """Lead C2: for each roster field, an invalid value refuses with zero protected opens (the second span's
        entry, so a late check would have opened the first span's sources)."""
        r0, r1 = self.roster
        invalid = {"span_id": ("Dev-01-s02", "dev-01-s02/L001", "d", ""),
                   "block_id": ("Dev-01", "dev-01\n", "d", "", "DEV-01"),
                   "role": ("support", "Fit", ""),
                   "t0_local_date": ("2026-1-01", "2026-11-14T00:00", "01/02/2026", "")}
        variants = [(f"{field} missing", {k: v for k, v in r1.items() if k != field}) for field in R.ROSTER_ENTRY_KEYS]
        variants += [(f"{field} {bad!r}", dict(r1, **{field: bad})) for field in R.ROSTER_ENTRY_KEYS
                     for bad in (None, 5, True, ["x"], *invalid[field])]
        variants += [("another member", dict(r1, note="x")), ("a list", [r1]), ("text", "dev-01-s02")]
        root = self.custody()
        for name, entry in variants:
            with self.subTest(name), _Opens() as opened:
                with self.assertRaisesRegex(F.LookInputError, "^roster: "):
                    self.read(root, roster=[r0, entry])
                self.assertEqual(opened, [], name)
        with self.assertRaisesRegex(F.LookInputError, "^roster: not a list"), _Opens() as opened:
            self.read(root, roster={"spans": [r0, r1]})
        self.assertEqual(opened, [])

    def test_the_preflight_knows_when_no_leg_can_enter_the_fit(self):
        """Audit r7 finding 1: with every verdict's sidecar_coverage false, the preflight's plan has no fit candidate
        and nothing protected was opened. Whether stage 1 refuses here is NEEDS_SPEC (POST_OPEN_REASONS
        ``no_fit_candidate``; AuditCommittedStageOne.test_audit_r7_1_no_fit_candidate_is_needs_spec_...)."""
        excluded = {k: dict(v, sidecar_coverage=False) for k, v in self.verdicts.items()}
        root = self.custody()
        with _Opens() as opened:
            plan = R.stage1_preflight(self.roster, LF.span_dirs(root, []), excluded)
        self.assertEqual((plan["fit_candidates"], opened), ([], []))
        self.assertTrue(R.stage1_preflight(self.roster, LF.span_dirs(self.custody(), []), self.verdicts)["fit_candidates"])


@unittest.skipIf(F is None, "numpy is not installed; runs in the look-fit CI job")
class PostOpenAllowlist(unittest.TestCase):
    """Lead C2's mechanical guard on C1. The protected phase of stage 1 is ``stage1_protected`` and every function of
    cadence_look_run.py it reaches; each raise there must be a ContentRefusal whose code is in POST_OPEN_REASONS (a
    literal, or fit_interim's refusals through FIT_CONTENT_REASONS) or a PreflightBreach. ``main`` reports anything
    else that stops the protected phase as a breach, never a refusal."""

    SOURCE = Path(R.__file__) if R is not None else None
    ENTRY = "stage1_protected"
    REFUSAL = "ContentRefusal"
    BREACH = "PreflightBreach"

    def tree(self):
        import ast
        return ast.parse(self.SOURCE.read_text(encoding="utf-8"))

    def protected_phase(self):
        """{function name: its AST} for the entry and every module function it reaches by name."""
        import ast
        functions = {node.name: node for node in self.tree().body if isinstance(node, ast.FunctionDef)}
        reached, pending = {}, [self.ENTRY]
        while pending:
            name = pending.pop()
            if name in reached or name not in functions:
                continue
            reached[name] = functions[name]
            pending += [node.func.id for node in ast.walk(functions[name])
                        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
        return reached

    def test_every_refusal_after_the_first_open_has_an_allowlisted_reason_code(self):
        import ast
        phase = self.protected_phase()
        for name in ("read_protected", "protected_span", "span_meter", "trace_holes", "native_states",
                     "fit_stage1", "stage2_preflight", "_stamp_protected"):
            self.assertIn(name, phase)
        for name in ("stage1_preflight", "plan_span", "plan_leg", "turn_operational", "validate_runtime_bundles",
                     "check_roster", "_guard_loaded", "_stamp"):
            self.assertNotIn(name, phase, f"{name} is a preflight function and must not run after the first open")
        codes, breaches = set(), 0
        for name, function in phase.items():
            for node in ast.walk(function):
                if not isinstance(node, ast.Raise):
                    continue
                where = f"{name}:{node.lineno}"
                call = node.exc
                self.assertIsInstance(call, ast.Call, f"{where}: a bare or non-constructing raise")
                self.assertIsInstance(call.func, ast.Name, where)
                self.assertIn(call.func.id, (self.REFUSAL, self.BREACH), f"{where}: raises {call.func.id}")
                if call.func.id == self.BREACH:
                    breaches += 1
                    continue
                code = call.args[0]
                if isinstance(code, ast.Constant):
                    codes.add(code.value)
                else:                      # fit_interim's refusals, through the registry of their texts
                    self.assertEqual((name, getattr(code, "id", None)), ("fit_stage1", "code"), where)
                    codes |= {code for code, _ in R.FIT_CONTENT_REASONS}
        self.assertLessEqual(codes, set(R.POST_OPEN_REASONS))
        self.assertEqual(codes, set(R.POST_OPEN_REASONS), "an allowlisted code that no protected path raises")
        self.assertGreater(breaches, 0)
        self.assertEqual(R.NEEDS_SPEC_REASONS, {"no_fit_candidate"})
        self.assertTrue(all(R.POST_OPEN_REASONS[c].startswith("NEEDS_SPEC") for c in R.NEEDS_SPEC_REASONS))

    def test_a_content_refusal_takes_only_an_allowlisted_code(self):
        with self.assertRaises(ValueError):
            R.ContentRefusal("roster_block_id", "a preflight reason")
        self.assertEqual(R.ContentRefusal("native_states", "x").code, "native_states")

    def test_any_other_stop_in_the_protected_phase_is_a_breach_never_a_refusal(self):
        import contextlib
        import io

        def protected(error):
            def stage1(a):
                R._PHASE["protected"] = True
                raise error
            return stage1
        cases = ((R.ContentRefusal("native_states", "plist/rich frame count mismatch"), "REFUSED plist/rich"),
                 (F.LookInputError("roster: a block_id is not a registered block id"), "FAILED preflight breach"),
                 (R.PreflightBreach("stage-2 preflight: x"), "FAILED preflight breach"),
                 (R.M.ManifestError(["a ledger problem"]), "FAILED preflight breach"),
                 (R.PINS.PinRefusal("x: a file that is not pinned"), "FAILED preflight breach"))
        for error, text in cases:
            with self.subTest(type(error).__name__), mock.patch.object(R.M, "verify_pins",
                                                                        return_value={"look_id": F.LOOK_ID}), \
                    mock.patch.object(R, "cmd_stage1", side_effect=protected(error)), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(R.main(["stage1", "--allow-draft"]), 2)
                self.assertTrue(err.getvalue().startswith(text), err.getvalue())
                self.assertNotIn("REFUSED", err.getvalue()) if text.startswith("FAILED") else None
        # before the protected phase the same refusal is an ordinary refusal
        with mock.patch.object(R.M, "verify_pins", return_value={"look_id": F.LOOK_ID}), \
                mock.patch.object(R, "cmd_stage1", side_effect=F.LookInputError("roster: a span appears twice")), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(R.main(["stage1", "--allow-draft"]), 2)
        self.assertEqual(err.getvalue(), "REFUSED roster: a span appears twice\n")


@unittest.skipIf(F is None, "numpy is not installed; runs in the look-fit CI job")
class AuditCommittedStageOne(unittest.TestCase):
    """The audit's reproductions through committed stage 1 in an isolated process (the frozen admission matrix's
    own positive arena and observer, unchanged): findings 1 and 2. Refusals open no protected source, take no
    reservation and write nothing; the complete control opens the timestamp sources and writes stage 1's file."""

    @classmethod
    def setUpClass(cls):
        from tests.cadence import test_interim_admission_closure as suite
        cls.suite = suite
        owner = unittest.TestCase()
        cls.addClassCleanup(owner.doCleanups)
        cls.arena = suite.Arena(owner)
        cls.case = suite.Case("admit", suite.PINS[0], "normal")
        cls.arena.install(cls.case)
        # the registered inputs as the arena made them: a test that re-registers restores these
        cls.roster_bytes = cls.arena.inputs[0].read_bytes()
        cls.verdicts = json.loads(cls.arena.inputs[1].read_bytes())

    def restore(self):
        self.arena.inputs[0].write_bytes(self.roster_bytes)
        self.register(self.verdicts)

    def run_stage1(self, label=None):
        """Committed stage 1 on the arena's pinned custody; with ``label``, the focus span's Check item prints its
        offload manifest as ``label`` (``{sha}``: the pinned digest) in place of "Offload manifest `<sha>`"."""
        arena, original = self.arena, PF.run_state
        if label is None:
            return arena.run(self.case)

        def run_state(table):
            sha = next(span["offload_manifest_sha256"] for span in table["spans"]
                       if span["span_id"] == arena.span.name)
            text, printed = original(table), f"Offload manifest `{sha}`"
            self.assertEqual(text.count(printed), 1)
            return text.replace(printed, label.format(sha=sha))
        with mock.patch.object(PF, "run_state", side_effect=run_state):
            return arena.run(self.case)

    def register(self, verdicts):
        arena = self.arena
        arena.inputs[1].write_bytes(self.suite.wire(verdicts))
        arena.pin()
        command = [sys.executable, "-I", "-B", str(arena.mini / "scripts/cadence_look_manifest.py"), "row",
                   "--manifest", str(arena.manifest), "--repo", str(arena.mini), "--roster", str(arena.inputs[0]),
                   "--verdicts", str(arena.inputs[1]), "--write"]
        done = subprocess.run(command, cwd=arena.mini, capture_output=True, text=True, timeout=600)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def assert_refused_before_any_open(self, row, text):
        self.assertEqual(row["rc"], 2, row)
        self.assertIn(text, row["err"])
        self.assertEqual(row["opens"], [], row)
        self.assertEqual(row["timestamp_readers"], [], row)
        self.assertFalse(row["output"] or row["public"] or row["spent"], row)

    def test_audit_findings_1_and_2_through_committed_stage_one(self):
        arena = self.arena
        complete = self.run_stage1()
        self.assertEqual(complete["rc"], 0, complete)
        self.assertTrue(complete["output"])
        self.assertIn("stream-0001.jsonl", complete["opens"])

        # finding 2: the expected digest beside a pending observation bound the Check at c3a0dd9f8 (rc 0, four opens)
        for label in ("Observed offload manifest pending",
                      "Observed offload manifest pending. Expected offload manifest `{sha}`",
                      "Expected offload manifest `{sha}`"):
            with self.subTest(label):
                self.assert_refused_before_any_open(self.run_stage1(label), "the span is held")

        # finding 1: a registered verdict file with no verdict for a rostered leg of either span (the second, the
        # supporting span, opened rich_telemetry.jsonl and stream-0001.jsonl at c3a0dd9f8 before refusing)
        verdicts = self.verdicts
        receipt = arena.docs[self.suite.RECEIPT]
        first = f"{arena.span.name}/{receipt['roster'][0]}"
        support = next(key for key in verdicts if key.startswith(arena.support.name + "/"))
        try:
            for key in (first, support):
                with self.subTest(missing=key):
                    self.register({k: v for k, v in verdicts.items() if k != key})
                    self.assert_refused_before_any_open(self.run_stage1(), "no verdict for a roster leg")
        finally:
            self.restore()


    def test_audit_r7_2_and_3_through_committed_stage_one(self):
        """Audit on 5a7a3eae0, findings 2 and 3, as reproduced there: the supporting block's id ``Dev-01`` refused
        after four protected opens; the Check line ``- Observed offload manifest <sha>`` held a correct span."""
        arena = self.arena
        for label in ("\n\n   - Observed offload manifest `{sha}`", "\n\n   * Observed offload manifest `{sha}`",
                      "\n\n+ **Observed offload manifest** `{sha}`"):
            with self.subTest(label):
                row = self.run_stage1(label)
                self.assertEqual((row["rc"], row["output"]), (0, True), row)
        for label in ("\n\n   - Expected offload manifest `{sha}`", "\n\n   * Planned offload manifest `{sha}`"):
            with self.subTest(label):
                self.assert_refused_before_any_open(self.run_stage1(label), "the span is held")
        roster = json.loads(self.roster_bytes)
        try:
            roster[-1]["block_id"] = roster[-1]["block_id"].capitalize()
            arena.inputs[0].write_bytes(self.suite.wire(roster))
            self.register(self.verdicts)
            self.assert_refused_before_any_open(self.run_stage1(), "roster: a block_id is not a registered block id")
        finally:
            self.restore()

    def test_audit_r7_1_no_fit_candidate_is_needs_spec_and_refuses_after_the_first_open(self):
        """NEEDS_SPEC (PR #795 round 8). Audit on 5a7a3eae0, finding 1: every verdict's sidecar_coverage false leaves
        no fit candidate (the preflight knows it: ValidateBeforeOpen.test_the_preflight_knows_when_no_leg_can_enter_
        the_fit), yet stage 1 opens the protected sources and refuses "no leg enters the fit" (POST_OPEN_REASONS
        ``no_fit_candidate``). The refusal is not moved before the first open because the frozen admission matrix's
        negative-arena control (the roster of 101,605 of its 101,889 cases) has every verdict false and must reach a
        protected open. This test pins today's behaviour until the lead rules: no output, no reservation, no public
        file, and the refusal after the opens. If the ruling moves the refusal, this test changes with it."""
        try:
            self.register({k: dict(v, sidecar_coverage=False) for k, v in self.verdicts.items()})
            row = self.run_stage1()
            self.assertEqual(row["rc"], 2, row)
            self.assertIn("stage 1: no leg enters the fit", row["err"])
            self.assertFalse(row["output"] or row["public"] or row["spent"] or row["responses"], row)
            self.assertTrue(row["opens"], "the NEEDS_SPEC refusal moved before the first open without a ruling")
        finally:
            self.restore()


# ============================================================================================ finding 2, its class
class ObservedNotExpected(unittest.TestCase):
    """Finding 2 (custody_pins.py:313 at c3a0dd9f8): "Expected offload manifest <the pin>" beside a pending
    observation bound the Check. The class: only an observation in full hex binds; a pending, malformed,
    conflicting or expected-only one holds the span, whatever else the item prints."""

    def setUp(self):
        self.digest = "0123456789abcdef" * 4
        self.span = {"span_id": "dev-03-s01", "runner_commit": "0" * 40, "close_item": 2, "check_item": 1,
                     "check_corrected_from": None, "offload_manifest_sha256": self.digest,
                     "files": [{"path": "runner_receipt.json", "sha256": "1" * 64, "size": 1}]}

    def form(self, body):
        return P.check_binding(self.span, f"1. **Check of dev-03-s01 (generated).** {body}\n")["form"]

    def test_an_observation_in_full_hex_binds(self):
        d = self.digest
        for body in (f"Offload manifest `{d}` (5 files).", f"Observed offload manifest `{d}`.",
                     f"Verified offload manifest sha256 `{d}`.", f"dev-03-s01 read back: offload manifest `{d}`.",
                     f"`cq-dev-03-s01-a1/` offload manifest (226 files) sha256 `{d}`; cloud copy hash check OK",
                     f"Offload manifest `{d}`. Read back: dev-03-s01 offload manifest `{d[:8]}…{d[-4:]}`."):
            with self.subTest(body):
                self.assertEqual(self.form(body), "full")

    def test_a_markdown_list_marker_or_emphasis_changes_no_binding(self):
        """Lead C3 (audit on 5a7a3eae0, finding 3): the observation line is classified after its Markdown list marker,
        emphasis and surrounding whitespace are stripped. The writer's form and every marker variant bind; an
        expected, planned or target digest binds nothing in every variant."""
        d = self.digest
        leads = (("", ""), ("* ", ""), ("- ", ""), ("+ ", ""), ("   - ", ""), ("\t* ", ""), ("7. ", ""), ("7) ", ""),
                 ("- **", "**"), ("* _", "_"), ("+ __", "__"), ("**", "**"), ("- *", "*"))
        for lead, closing in leads:
            for word, form in (("Observed ", "full"), ("", "full"), ("Expected ", "absent"), ("Planned ", "absent"),
                               ("Target ", "absent")):
                body = f"Copy checked.\n\n{lead}{word}offload manifest{closing} `{d}` (5 files)"
                with self.subTest(lead=lead, word=word):
                    self.assertEqual(self.form(body), form)
        # the generated public Check, as the fixture writes it, and the audit's two replayed lines
        doc = {"schema": P.SCHEMA, "spans": [self.span]}
        self.assertEqual(P.chain_link(doc, PF.run_state(doc)), {"dev-03-s01": "full"})
        for line in ("\n\n   - Observed offload manifest `{d}`", "\n\n   * Observed offload manifest `{d}`"):
            text = PF.run_state(doc).replace(f"Offload manifest `{d}`", line.format(d=d))
            self.assertEqual(P.chain_link(doc, text), {"dev-03-s01": "full"}, line)

    def test_a_pending_malformed_conflicting_or_expected_only_observation_holds_the_span(self):
        d = self.digest
        other = d[:-1] + "0"
        held = {
            "audit 2: pending, with the expected digest": (
                f"Observed offload manifest pending. Expected offload manifest `{d}`.", "absent"),
            "expected only": (f"Expected offload manifest `{d}`.", "absent"),
            "planned": (f"Planned offload manifest `{d}`.", "absent"),
            "a target": (f"Target offload manifest sha256 `{d}`.", "absent"),
            "not the offload manifest": (f"Not the offload manifest `{d}`.", "absent"),
            "the expected value after the label": (f"Offload manifest: expected `{d}`.", "absent"),
            "a pending readback beside the observation": (
                f"Offload manifest `{d}`. Offload manifest readback pending.", "absent"),
            "awaiting the observation": (f"Offload manifest `{d}`; offload manifest re-read awaiting.", "absent"),
            "a malformed digest beside the observation (upper case)": (
                f"Offload manifest `{d}`. Readback `{d.upper()}`.", "absent"),
            "a malformed digest beside the observation (65 hex)": (
                f"Offload manifest `{d}`. Offload manifest readback `{d}a`.", "absent"),
            "a malformed digest beside the observation (63 hex)": (
                f"Offload manifest `{d[:-1]}`. Offload manifest `{d}`.", "absent"),
            "a malformed digest beside the observation (a letter that is not hex)": (
                f"Offload manifest `{d[:30]}g{d[31:]}`. Offload manifest `{d}`.", "absent"),
            "a conflicting observation": (f"Offload manifest `{d}`. Offload manifest `{other}`.", "mismatch"),
            "a conflicting expected value": (f"Offload manifest `{d}`. Expected offload manifest `{other}`.",
                                             "mismatch"),
        }
        doc = {"schema": P.SCHEMA, "spans": [self.span]}
        for label, (body, form) in held.items():
            with self.subTest(label):
                text = f"1. **Check of dev-03-s01 (generated).** {body}\n"
                self.assertEqual(P.check_binding(self.span, text)["form"], form)
                self.assertEqual(P.held_spans(doc, text), ["dev-03-s01"])
                self.assertTrue(P.check_chain_problems(doc, text))
                with self.assertRaisesRegex(P.PinRefusal, "stays HELD"):      # nor is it a correction's target
                    P.correct_check(doc, "dev-03-s01", 2, text.replace("1. **", "2. **", 1))


# ============================================================================================ finding 3, its class
class FailClosedOnFetch(unittest.TestCase):
    """Finding 3 (manifest.py:1761 at c3a0dd9f8): with both fixture fetches failing, authorize-freeze2 still exited 0
    with RL-999 from the cached refs. RL-184 section 2.3: a failed fetch of either ref holds. The class: every
    authority resolution fetches the ref it resolves, now, and refuses when the fetch fails."""

    AUDIT_BRANCH = M._FREEZE2_AUDIT_REF.split("/", 1)[1]

    def named_freeze(self):
        """A generated look published with twin_agrees "no" and named freeze 2 by a generated ruling RL-999, its
        stanza on the audit branch of the copy's origin."""
        from tests.cadence.test_interim_release import HOST_TOKEN, digest, report
        mini = MR.mini_repo(self)
        MR.commit(mini, stage1_sha256="c" * 64)
        ledger = mini / M.LOOK_LEDGER_PATH
        data = M.load_json(ledger)
        row = M._look_row(data, LOOK)
        row.update(public_root="public", custody_root=str(mini.parent / "synthetic-only"), execution_host=HOST_TOKEN)
        ledger.write_bytes(C.dump(data))
        MR.git_commit(mini, "commit generated stage one")
        record = dict(report(twin="no"), commit=MR.git(mini, "rev-parse", "HEAD").stdout.strip(),
                      manifest_sha256=row["sha256"])
        public = mini / "public" / LOOK / "PUBLIC.json"
        public.parent.mkdir(parents=True)
        public.write_bytes(C.dump(record))
        row.update(status="run", output_sha256=digest(public.read_bytes()), coefficients_sha256=record["coefficients_sha256"])
        ledger.write_bytes(C.dump(data))
        MR.git_commit(mini, "publish generated no")
        rule = "RL-999"
        stanza = (f'FREEZE-2-NAMING ruling={rule} look={LOOK} coefficients_sha256={row["coefficients_sha256"]} '
                  f'public_sha256={row["output_sha256"]} designation=freeze-2')
        MR.git(mini, "checkout", "-qb", "fixture-audit")
        decisions = mini / M._FREEZE2_DECISIONS_PATH
        decisions.parent.mkdir(parents=True, exist_ok=True)
        decisions.write_text(f"# {rule}. Generated ruling\n\n{stanza}\n")
        MR.git_commit(mini, "name the generated digest", publish=False)
        audit = MR.git(mini, "rev-parse", "HEAD").stdout.strip()
        MR.run(["git", "-C", str(mini), "push", "-q", "origin", f"{audit}:refs/heads/{self.AUDIT_BRANCH}"], mini,
               check=True)
        MR.git(mini, "checkout", "-q", "main")
        naming = {"schema": "joulewise.cadence_looks.freeze2_naming.v1", "look_id": LOOK, "ruling": rule,
                  "coefficients_sha256": row["coefficients_sha256"], "public_sha256": row["output_sha256"],
                  "designation": "freeze-2", "decisions_path": M._FREEZE2_DECISIONS_PATH,
                  "decisions_commit": audit, "stanza": stanza}
        (mini / MR.MANIFEST.replace(".json", ".freeze2.json")).write_bytes(C.dump(naming))
        row.update(status="frozen", ruling=rule)
        ledger.write_bytes(C.dump(data))
        MR.git_commit(mini, "register the exact generated naming record")
        return mini, row

    def authorize(self, mini, row):
        return MR.py(mini, "scripts/cadence_look_manifest.py", "authorize-freeze2", "--repo", mini, "--look-id", LOOK,
                     "--expected-coefficients-sha256", row["coefficients_sha256"])

    def test_audit_3_freeze_2_refuses_when_a_required_fetch_fails(self):
        mini, row = self.named_freeze()
        accepted, evidence = M.freeze2_authority(mini, expected_coefficients_sha256=row["coefficients_sha256"])
        self.assertEqual((accepted, evidence["decision_source"]), (row, "RL-999"))
        result = self.authorize(mini, row)
        self.assertEqual((result.returncode, json.loads(result.stdout)), (0, evidence), result.stderr)
        audit_ref = "refs/remotes/" + M._FREEZE2_AUDIT_REF
        self.assertTrue(MR.git(mini, "rev-parse", "--verify", audit_ref).stdout.strip())   # a cached copy is here

        # the audit's first fixture: main fetches, the audit branch does not (it is gone from origin)
        MR.run(["git", "-C", str(mini), "push", "-q", "origin", f":refs/heads/{self.AUDIT_BRANCH}"], mini, check=True)
        with self.assertRaisesRegex(M.ManifestError, "origin/audit/2026-11-10-fable cannot be fetched"):
            M.freeze2_authority(mini, expected_coefficients_sha256=row["coefficients_sha256"])
        result = self.authorize(mini, row)
        self.assertEqual((result.returncode, result.stdout), (1, ""), result.stderr)
        self.assertIn("REFUSE freeze 2 public authority", result.stderr)

        # the audit's second fixture: origin is unreachable, so neither ref fetches
        origin = MR.git(mini, "remote", "get-url", "origin").stdout.strip()
        MR.git(mini, "remote", "set-url", "origin", str(mini.parent / "no-such-synthetic-origin.git"))
        try:
            with self.assertRaisesRegex(M.ManifestError, "origin/main cannot be fetched"):
                M.freeze2_authority(mini, expected_coefficients_sha256=row["coefficients_sha256"])
            with self.assertRaisesRegex(M.ManifestError, "origin/main cannot be fetched"):
                M.freeze2_commitment(mini)                   # the scorer's path (predict_frozen) too
            result = self.authorize(mini, row)
            self.assertEqual((result.returncode, result.stdout), (1, ""), result.stderr)
        finally:
            MR.git(mini, "remote", "set-url", "origin", origin)

    def test_a_twin_yes_freeze_refuses_when_main_does_not_fetch(self):
        mini, row = self.named_freeze()
        MR.git(mini, "remote", "set-url", "origin", str(mini.parent / "no-such-synthetic-origin.git"))
        with mock.patch.object(M, "_freeze2_naming", side_effect=AssertionError("naming path")):
            with self.assertRaisesRegex(M.ManifestError, "origin/main cannot be fetched"):
                M.freeze2_authority(mini)

    def test_recording_an_outcome_refuses_when_main_does_not_fetch(self):
        mini = MR.mini_repo(self)
        MR.commit(mini, stage1_sha256="c" * 64)
        args = ("row", "--manifest", mini / MR.MANIFEST, "--repo", mini, "--error-type", "RuntimeError")
        result = MR.py(mini, "scripts/cadence_look_manifest.py", *args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        MR.git(mini, "remote", "set-url", "origin", str(mini.parent / "no-such-synthetic-origin.git"))
        result = MR.py(mini, "scripts/cadence_look_manifest.py", *args)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("REFUSE origin/main cannot be fetched", result.stdout)


if __name__ == "__main__":
    unittest.main()
