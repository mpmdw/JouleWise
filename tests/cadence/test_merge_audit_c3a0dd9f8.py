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
        and nothing protected was opened. Stage 1 still refuses after the first open: a known limitation (lead
        ruling N1(a); POST_OPEN_REASONS ``no_fit_candidate``; AuditCommittedStageOne.test_audit_r7_1_...)."""
        excluded = {k: dict(v, sidecar_coverage=False) for k, v in self.verdicts.items()}
        root = self.custody()
        with _Opens() as opened:
            plan = R.stage1_preflight(self.roster, LF.span_dirs(root, []), excluded)
        self.assertEqual((plan["fit_candidates"], opened), ([], []))
        self.assertTrue(R.stage1_preflight(self.roster, LF.span_dirs(self.custody(), []), self.verdicts)["fit_candidates"])


    def test_audit_r8_no_cell_able_to_supply_both_rates_refuses_before_any_open(self):
        """Closing decision F4 (final confirm audit on 2a3752363, C1 HIGH): with every 2,000-token turn starting at its
        first token (no prefill seconds) and every other turn ending at it (no decode seconds), no cell holding a fit
        candidate can supply both rates and the fit is impossible whatever the protected reads give. The preflight
        refuses with zero protected opens. With only the 2,000-token turns changed, the other cells supply both rates
        and the preflight passes."""
        original = R.turn_operational

        def zero_prefill(turn):
            turn["turn_start_s"] = turn["segments"][0]["wall_start_s"] = turn["first_token_s"]
            turn["journal"] = [r for r in turn["journal"] if r["t_s"] >= turn["turn_start_s"] - 60.0]

        def zero_decode(turn):
            first = turn["first_token_s"]
            for part in turn["segments"][1:] + turn["prefix_tails"]:
                part["wall_start_s"] = part["wall_end_s"] = part["first_token_s"] = first
            turn["last_token_s"] = first
            turn["journal"] = [r for r in turn["journal"] if r["t_s"] <= first + 5.0]

        def shaped(others):
            def turn(bundle, result, fan_keys):
                got = original(bundle, result, fan_keys)
                parts = Path(bundle).parts
                leg_dir = Path(*parts[:parts.index("legs") + 2])
                cell = _rj(leg_dir / "leg_record.json")["spec"]["prefill_tokens"]
                self.assertIn(cell, F.CELLS)
                if cell == 2000:
                    zero_prefill(got)
                elif others:
                    zero_decode(got)
                return got
            return turn
        ok = ("ok", None, None, None, None)          # every changed leg keeps its start reading: still a candidate
        for others, refuses in ((True, True), (False, False)):
            root = self.custody()
            with self.subTest(other_cells_without_decode=others), _Opens() as opened, \
                    mock.patch.object(R, "turn_operational", side_effect=shaped(others)), \
                    mock.patch.object(R.F, "start_reading", return_value=ok):
                if refuses:
                    with self.assertRaisesRegex(F.LookInputError, "zero prefill or decode seconds in every cell that "
                                                                  "holds a fit candidate"):
                        R.stage1_preflight(self.roster, LF.span_dirs(root, []), self.verdicts)
                else:
                    self.assertTrue(R.stage1_preflight(self.roster, LF.span_dirs(root, []), self.verdicts)
                                    ["fit_candidates"])
                self.assertEqual(opened, [])


@unittest.skipIf(F is None, "numpy is not installed; runs in the look-fit CI job")
class PostOpenAllowlist(unittest.TestCase):
    """Lead C2's mechanical guard on C1, extended by the closing decision's F3. The protected phase of stage 1 is
    ``stage1_protected``, the rest of the stage-1 entry point (``finish_stage1``), the ``sdir_of`` callback they are
    handed, the methods of the objects they use (the look's layout, the pin guard), and every function, class method
    and imported project helper they reach, across modules. Each raise
    reached there is classified:

    * in cadence_look_run.py's own functions: a ContentRefusal with a POST_OPEN_REASONS code, a PreflightBreach, or
      ``owned_refusal`` (a breach after the first open);
    * under ``fit_interim.stage1`` (wrapped by ``fit_stage1``): an allowlisted code when its text is one of
      FIT_CONTENT_REASONS, else a breach;
    * anywhere else (an imported helper or a callback): a breach, which ``main`` reports as FAILED, never a refusal.
    """

    ENTRIES = ("stage1_protected", "finish_stage1")
    OWN = ("ContentRefusal", "PreflightBreach", "owned_refusal")

    @staticmethod
    def module_tree(module):
        import ast
        return ast.parse(Path(module.__file__).read_text(encoding="utf-8"))

    def walk(self, roots, *, boundary=()):
        """{(file, qualified name): AST} for every definition reached from ``roots`` ([(module, name)]), following
        calls by name, through imported project modules (module aliases, ``from`` imports, imports inside a
        function), into class methods; ``boundary`` ([(module, name)]) is not entered."""
        import ast
        import importlib
        import types
        trees, reached, pending = {}, {}, list(roots)

        def project(value):
            name = getattr(value, "__name__", "") if isinstance(value, types.ModuleType) else ""
            return name.startswith(("joulewise.", "scripts.", "_step3"))

        def definitions(module):
            if module.__name__ not in trees:
                tree = self.module_tree(module)
                defs = {}
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        defs[node.name] = node
                trees[module.__name__] = defs
            return trees[module.__name__]

        def local_modules(module, function):
            aliases = {k: v for k, v in vars(module).items() if project(v)}
            for node in ast.walk(function):
                if isinstance(node, ast.ImportFrom) and node.module:
                    for alias in node.names:
                        try:
                            value = importlib.import_module(f"{node.module}.{alias.name}")
                        except ImportError:
                            continue
                        aliases[alias.asname or alias.name] = value
            return aliases

        while pending:
            module, name = pending.pop()
            if (module, name) in boundary:
                continue
            node = definitions(module).get(name)
            if node is None:
                value = getattr(module, name, None)        # a helper imported by name from another project module
                home = importlib.import_module(getattr(value, "__module__", "") or "builtins")
                if callable(value) and project(home) and home is not module:
                    pending.append((home, name))
                continue
            key = (Path(module.__file__).name, name)
            if key in reached:
                continue
            reached[key] = node
            bodies = [node] if isinstance(node, ast.FunctionDef) else [n for n in node.body if isinstance(n, ast.FunctionDef)]
            for body in bodies:
                aliases = local_modules(module, body)
                for call in ast.walk(body):
                    if not isinstance(call, ast.Call):
                        continue
                    func = call.func
                    if isinstance(func, ast.Name):
                        pending.append((module, func.id))
                    elif (isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name)
                          and func.value.id in aliases):
                        pending.append((aliases[func.value.id], func.attr))
                    elif (isinstance(func, ast.Attribute) and isinstance(func.value, ast.Attribute)
                          and isinstance(func.value.value, ast.Name) and func.value.value.id in aliases):
                        inner = getattr(aliases[func.value.value.id], func.value.attr, None)    # e.g. R.F.stage1
                        if project(inner):
                            pending.append((inner, func.attr))
        return reached

    @staticmethod
    def raises(reached):
        import ast
        return [(file, name, node) for (file, name), definition in reached.items()
                for node in ast.walk(definition) if isinstance(node, ast.Raise)]

    def sdir_of_callback(self):
        """The ``sdir_of`` closure ``_stage1`` hands the protected phase: its raises are reached after the open."""
        import ast
        stage1 = next(n for n in self.module_tree(R).body if isinstance(n, ast.FunctionDef) and n.name == "_stage1")
        return next(n for n in ast.walk(stage1) if isinstance(n, ast.FunctionDef) and n.name == "sdir_of")

    def test_every_refusal_after_the_first_open_is_allowlisted_or_a_breach(self):
        import ast
        own = Path(R.__file__).name
        fit_root = [(R.F, "stage1")]
        # the objects made before the open whose methods the protected phase calls: the look's layout (create, file)
        # and the pin guard every open of a roster path passes through
        objects = [(R.M, "LookLayout"), (R.PINS, "PinnedCustody")]
        phase = self.walk([(R, name) for name in self.ENTRIES] + objects, boundary=fit_root)
        fit = self.walk(fit_root)
        names = {name for file, name in phase if file == own}
        for name in ("read_protected", "protected_span", "span_meter", "trace_holes", "native_states", "fit_stage1",
                     "stage2_preflight", "_stamp_protected", "finish_stage1", "owned_refusal"):
            self.assertIn(name, names)
        for name in ("stage1_preflight", "plan_span", "plan_leg", "turn_operational", "validate_runtime_bundles",
                     "check_roster", "_guard_loaded", "_stamp"):
            self.assertNotIn(name, names, f"{name} is a preflight function and must not run after the first open")
        imported = {file for file, _ in phase} - {own}
        self.assertTrue({"inclusion_34.py", "time_fields.py", "manifest.py"} <= imported, imported)
        self.assertIn(("manifest.py", "LookLayout"), phase)          # layout.create's class, by its methods
        codes, breaches, other = set(), [], []
        for file, name, node in self.raises(phase) + [(own, "sdir_of", n) for n in ast.walk(self.sdir_of_callback())
                                                       if isinstance(n, ast.Raise)]:
            where = f"{file}:{name}:{node.lineno}"
            if file != own or name in ("sdir_of", "ContentRefusal", "PreflightBreach"):
                # an imported helper, a callback, or the refusal classes' own guard (an unregistered code, which this
                # test proves is never passed): main reports each as a breach
                other.append(where)
                continue
            call = node.exc
            self.assertIsInstance(call, ast.Call, f"{where}: a bare or non-constructing raise")
            self.assertIsInstance(call.func, ast.Name, where)
            self.assertIn(call.func.id, self.OWN, f"{where}: raises {call.func.id}")
            if call.func.id != "ContentRefusal":
                breaches.append(where)
                continue
            code = call.args[0]
            if isinstance(code, ast.Constant):
                codes.add(code.value)
            else:                                   # fit_interim's refusals, through the registry of their texts
                self.assertEqual((name, getattr(code, "id", None)), ("fit_stage1", "code"), where)
        self.assertIn(f"{own}:finish_stage1:" + str(next(node.lineno for f, n, node in self.raises(phase)
                                                         if (f, n) == (own, "finish_stage1"))), breaches)
        fit_codes = {}
        for file, name, node in self.raises(fit):
            text = node.exc.args[0].value if (isinstance(node.exc, ast.Call) and node.exc.args
                                              and isinstance(node.exc.args[0], ast.Constant)) else None
            code = next((c for c, pattern in R.FIT_CONTENT_REASONS if text and pattern.fullmatch(text)), None)
            fit_codes[f"{file}:{name}:{node.lineno}"] = code or "breach"
            self.assertNotIn("ContentRefusal", ast.unparse(node), "only cadence_look_run.py makes a content refusal")
        rate = [w for w, c in fit_codes.items() if c == "zero_rate_seconds"]
        self.assertTrue(rate and all(w.startswith("fit_interim.py:") for w in rate), fit_codes)   # fit_interim.py:800
        self.assertTrue(any(c == "no_leg_enters_fit" for c in fit_codes.values()), fit_codes)
        codes |= {c for c in fit_codes.values() if c != "breach"} | {c for c, _ in R.FIT_CONTENT_REASONS}
        self.assertEqual(codes, set(R.POST_OPEN_REASONS), "an allowlisted code that no protected path raises")
        self.assertTrue(other and breaches)
        self.assertEqual(R.KNOWN_LIMITATION_REASONS, {"no_fit_candidate"})
        self.assertTrue(all(R.POST_OPEN_REASONS[c].startswith("Known limitation (lead ruling N1(a)")
                            for c in R.KNOWN_LIMITATION_REASONS))

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
                 (R.PINS.PinRefusal("x: a file that is not pinned"), "FAILED preflight breach"),
                 (PermissionError(13, "generated"), "FAILED preflight breach: PermissionError at "),
                 (KeyError("generated"), "FAILED preflight breach: KeyError at "))
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
                      "\n\n+ **Observed offload manifest** `{sha}`",
                      # closing decision F1 (final confirm audit on 2a3752363, C3 HIGH): the bold adjective and noun
                      "\n\n- Observed **offload** manifest `{sha}`", "\n\n- Observed offload **manifest** `{sha}`",
                      # micro-fix G1 (narrow check on ac5a44818): a sentence ended by "!" before the observation
                      "\n\n- Verified! Observed **offload** manifest `{sha}` (6 files)."):
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

    def test_audit_r8_a_read_only_private_directory_refuses_before_any_open(self):
        """Closing decision F2 (final confirm audit on 2a3752363, C1/C2 MED): a private directory stage 1 cannot write
        into gave ``FAILED PermissionError`` after four protected opens. The preflight now refuses first."""
        import stat
        arena = self.arena
        directory = arena.out.parent
        for name in ("stage1.json", "level_r.json"):
            (directory / name).unlink(missing_ok=True)
        mode = stat.S_IMODE(directory.stat().st_mode)
        try:
            directory.chmod(mode & ~0o222)
            if os.access(directory, os.W_OK):
                self.skipTest("this account can write a read-only directory")
            self.assert_refused_before_any_open(self.run_stage1(), "the look's private directory cannot be written")
        finally:
            directory.chmod(mode)

    def test_audit_r7_1_no_fit_candidate_is_a_known_limitation_and_refuses_after_the_first_open(self):
        """Known limitation (lead ruling N1(a), 2026-11-24). Audit on 5a7a3eae0, finding 1: every verdict's
        sidecar_coverage false leaves
        no fit candidate (the preflight knows it: ValidateBeforeOpen.test_the_preflight_knows_when_no_leg_can_enter_
        the_fit), yet stage 1 opens the protected sources and refuses "no leg enters the fit" (POST_OPEN_REASONS
        ``no_fit_candidate``). The refusal is not moved before the first open because the frozen admission matrix's
        negative-arena control (the roster of 101,605 of its 101,889 cases) has every verdict false and must reach a
        protected open, and the production entry point is the same CLI (ruling N1(c) is not applicable). This test
        pins the ruled behaviour: no output, no reservation, no public file, no value printed, and the refusal after
        the opens."""
        try:
            self.register({k: dict(v, sidecar_coverage=False) for k, v in self.verdicts.items()})
            row = self.run_stage1()
            self.assertEqual(row["rc"], 2, row)
            self.assertEqual(row["err"], "REFUSED stage 1: no leg enters the fit\n")      # no value printed
            self.assertFalse(row["output"] or row["public"] or row["spent"] or row["responses"], row)
            self.assertTrue(row["opens"], "the known-limitation refusal moved before the first open without a ruling")
        finally:
            self.restore()


@unittest.skipIf(F is None, "numpy is not installed; runs in the look-fit CI job")
class AuditR8ImpossibleFit(unittest.TestCase):
    """Closing decision F4, the final confirm audit's own case on 2a3752363 through committed stage 1: two supporting
    spans whose two fit candidates sit in different cells, the 2,000-token turn with no prefill seconds and the
    19,458-token turn with no decode seconds. It opened the four protected source types, then refused on zero rate
    seconds; the preflight now refuses with no protected open, no output and no reservation."""

    @classmethod
    def setUpClass(cls):
        from tests.cadence import test_interim_admission_closure as suite
        cls.suite = suite
        owner = unittest.TestCase()
        cls.addClassCleanup(owner.doCleanups)
        cls.arena = arena = suite.Arena(owner)
        cls.case = suite.Case("admit", suite.PINS[0], "normal")
        arena.install(cls.case)
        support, second = arena.support, arena.source / "dev-02-s01"
        shutil.copytree(support, second)
        for name, doc in arena.corpus[suite.PINS[1]]["support"].items():
            (second / name).write_bytes(suite.wire(doc))
        row = next(r for r in json.loads(arena.inputs[0].read_bytes()) if r["span_id"] == support.name)
        cls.roster = [row, dict(row, span_id=second.name, block_id="dev-02")]
        arena.inputs[0].write_bytes(suite.wire(cls.roster))

    register = AuditCommittedStageOne.register
    assert_refused_before_any_open = AuditCommittedStageOne.assert_refused_before_any_open

    def test_audit_r8_impossible_fit_refuses_before_any_open(self):
        arena, sdir_of = self.arena, (lambda sid: self.arena.source / sid)
        verdicts = {f"{r['span_id']}/L001": dict(sidecar_coverage=True, km003c_clean=True) for r in self.roster}
        plan = R.stage1_preflight(self.roster, sdir_of, verdicts)
        cells = {}
        for span in plan["spans"]:
            for leg in span["legs"]:
                if leg["key"] in plan["fit_candidates"]:
                    cells.setdefault(leg["cell"], leg)
        self.assertGreaterEqual(len(cells), 2, cells)
        (low, low_leg), (high, high_leg) = sorted(cells.items())[0], sorted(cells.items())[-1]
        keep = {low_leg["key"], high_leg["key"]}
        verdicts = {k: dict(v) if k in keep else dict(v, sidecar_coverage=False) for k, v in verdicts.items()}
        self.register(verdicts)
        control = arena.run(self.case)
        self.assertEqual((control["rc"], control["output"]), (0, True), control)
        turns = low_leg["bundle"] / "outputs/align_turns.jsonl"           # no prefill seconds in the low cell
        item = json.loads(turns.read_bytes())
        item["start_stamp"]["epoch_s"] = low_leg["turn"]["first_token_s"]
        turns.write_bytes(self.suite.wire(item))
        events = high_leg["bundle"] / "events.jsonl"                       # no decode seconds in the high cell
        rows = [json.loads(line) for line in events.read_bytes().splitlines()]
        for event in rows:
            if event["timestamp_s"] >= high_leg["turn"]["first_token_s"]:
                event["timestamp_s"] = high_leg["turn"]["first_token_s"]
        events.write_bytes(b"".join(self.suite.wire(event) for event in rows))
        self.register(verdicts)
        with _Opens() as opened, self.assertRaisesRegex(F.LookInputError, "in every cell that holds a fit candidate"):
            R.stage1_preflight(self.roster, sdir_of, verdicts)      # the audit's plan: two candidates, no full cell
        self.assertEqual(opened, [])
        arena.out.unlink(missing_ok=True)
        self.assert_refused_before_any_open(arena.run(self.case), "zero prefill or decode seconds in every cell")


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

    def test_inline_markdown_anywhere_in_the_statement_changes_no_binding(self):
        """Closing decision F1 (final confirm audit on 2a3752363, C3 HIGH): inline Markdown is normalized across the
        whole statement, so a bold, italic or code-quoted part of the label binds as the plain label does."""
        d = self.digest
        for body in ("- Observed **offload** manifest `{d}`", "- Observed offload **manifest** `{d}`",
                     "- `Observed` offload manifest `{d}`", "- __Observed__ offload _manifest_ `{d}`",
                     "- *Observed* **offload** *manifest* `{d}` (5 files)", "- **Observed offload manifest** `{d}`"):
            with self.subTest(body):
                self.assertEqual(self.form("Copy checked.\n\n" + body.format(d=d)), "full")

    def test_a_qualifier_anywhere_in_the_statement_holds_the_span(self):
        """Closing decision F1 (C3 MED): qualification is judged on the complete normalized statement, never on the
        clause a comma, semicolon or colon cuts out of it. The audit's text-only case was "- Expected, offload
        manifest <the pin>", whose clause "offload manifest" bound."""
        d = self.digest
        for word in ("Expected", "Planned", "Target", "Intended", "Projected", "Not"):
            for body in ("- {w}, offload manifest `{d}`", "- {w}; offload manifest `{d}`", "- {w}: offload manifest `{d}`",
                         "- **{w}**, offload **manifest** `{d}`", "- Offload manifest `{d}`, {w}"):
                text = "Copy checked.\n\n" + body.format(w=word, d=d)
                with self.subTest(text=text):
                    self.assertEqual(self.form(text), "absent")
                    states = P.check_states({"schema": P.SCHEMA, "spans": [self.span]},
                                            f"1. **Check of dev-03-s01 (generated).** {text}\n")
                    self.assertEqual(states["dev-03-s01"]["state"], P.HELD)
        # the statement is the digest's whole line (micro-fix G1): a qualifier in an earlier sentence of the same
        # line holds the span; a qualifier on another line leaves it alone
        self.assertEqual(self.form(f"Expected copy done. Offload manifest `{d}`."), "absent")
        self.assertEqual(self.form(f"Planned at 02:00.\n- Observed offload manifest `{d}`"), "full")

    def test_g1_every_sentence_terminator_ends_the_observation_sentence(self):
        """Lead micro-fix G1 (narrow check on ac5a44818, tmp/check-sentences.py): "- Verified! Observed **offload**
        manifest <the pin>" held a span that "- Verified. ..." bound. A sentence before the observation ends at any of
        ".", "!", "?", ";", ":" followed by whitespace, or a line break, after the Markdown normalization. A qualified
        line still binds nothing, whatever ends its sentences."""
        pin = "91f18fc93b5a5a8789b0b15d9cb1d3dbe6b846afe51cc1e914ea90dad87df71a"
        span = dict(check_item=3, span_id="dev-03-s01", offload_manifest_sha256=pin)
        heading = "3. **Check of dev-03-s01 (generated).**\n\n"
        for mark in (".", "!", "?", ";", ":"):
            binds = (f"- Verified{mark} Observed **offload** manifest `{pin}` (6 files).",       # the reproduction
                     f"- **Verified{mark}** Observed offload manifest `{pin}`",
                     f"- Copy checked{mark} Offload manifest `{pin}` (6 files){mark} Read back OK",
                     f"Verified{mark}\n- Observed offload **manifest** `{pin}`")
            held = (f"- Expected{mark} Observed **offload** manifest `{pin}` (6 files).",
                    f"- Verified{mark} Expected **offload** manifest `{pin}`",
                    f"- Verified{mark} Observed offload manifest `{pin}`{mark} Planned",
                    f"- Target{mark} offload manifest `{pin}`",
                    f"- Verified{mark} Planned offload manifest{mark} `{pin}`")
            for line, form in [(x, "full") for x in binds] + [(x, "absent") for x in held]:
                with self.subTest(line=line):
                    self.assertEqual(P.check_binding(span, heading + line)["form"], form)
            # whatever ends the sentence before it, a contradicting readback "offload manifest readback: <digest>"
            # keeps its label (the words from "manifest" to the digest are never cut) and holds the span
            other = pin[:-1] + "0"
            line = f"- Verified{mark} Observed offload manifest `{pin}`{mark} Offload manifest readback: `{other}`"
            with self.subTest(line=line):
                self.assertEqual(P.check_binding(span, heading + line)["form"], "mismatch")

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
