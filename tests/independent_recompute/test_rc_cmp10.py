"""RC-CMP-10: the fix round inside the RC-CMP-9 design.

FS1-FS4 are the over-refusals of the lead's full-size synthetic window (RUN_STATE item 124): the resolution's
transport rule, the p42 refusal code, a sign or threshold word on numbers inside their bar, and the producer's
block-history leaves. OPUS F1-F2 and FABLE F1-F4 are the RC-CMP-9 delta reviews' findings
(review/2026-10-30-rc-cmp9-opus-rev, review/2026-10-30-rc-cmp9-fable-rev). The new rule: every word or code the
comparator expects L9 to print is pinned here to the producer source (or sealed config) that prints it.

Counterfactuals are in place: the check this round adds is switched off (mock) and the same case passes (or, for an
over-refusal, refuses as it did at f9f86869e). Fixture words come from the producers (producer_fixtures).
"""
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock

from . import producer_fixtures, test_comparator
from .test_comparator import ALPHA_CELLS, BLOCKS, DECODE, PREFILL, ROOT, cmp, item
from .test_input_gate import CODED, GateCase
from .test_rc_cmp7 import find, with_neg8, with_references
from .test_rc_cmp8 import FAMILY, PROJECTION, REPORTED, SENSITIVITY, contrast_rows, with_sensitivity
from .test_rc_cmp9 import fill_contrast, function, literal_sets, producer
from .test_review_fixes import DISCLOSURE, FILL, VERDICTS

EXTRACTION = f"mint/{test_comparator.SHA}-extraction-alpha.json"
FLOOR_KEY = "Qwen3-1.7B-4bit/decode/absolute"


def plain_exact(self, family, key, l9, ours, atoms=(), decide=None, raw=cmp.MISSING):
    """The comparator before FS3: every word compared exactly, whatever its numbers."""
    return self.exact(family, key, l9, ours, raw)


class Case(GateCase):
    def outcome(self):
        try:
            return self.exit_code(CODED)[0]
        except cmp.Refusal:
            return 2

    def row(self, out, key, family=None):
        return next(r for r in out["comparisons"] if r["key"] == key and family in (None, r["family"]))

    def base(self, widened=True):
        self.setUp()
        with_neg8(self)
        with_references(self)
        with_sensitivity(self, widened)


class LiteralPinTests(unittest.TestCase):
    """The new rule: each word or code the comparator expects L9 to print, pinned to the producer that prints it
    (origin/main read as text; the sealed configs through the registry)."""
    def source(self, path):
        text = producer(path)
        if text is None:
            self.skipTest("origin/main is not available in this clone")
        return text

    def test_transport_rule_is_the_group_rule(self):
        # FS1: the engine's exact resolution prints detection_floor.TRANSPORT_RULE_ID, the manifest's group_rule_id.
        floor = self.source("joulewise/detection_floor.py")
        rule = re.search(r'^TRANSPORT_RULE_ID = "([^"]+)"$', floor, re.M)[1]
        inputs = self.source("joulewise/analysis_engine/inputs.py")
        self.assertIn("transport_rule_id=TRANSPORT_RULE_ID,", inputs)
        self.assertIn('"transport_rule_id": value.transport_rule_id,', self.source("joulewise/analysis_engine/__init__.py"))
        registry = cmp.load_registry()
        for cid, entry in registry.tables["contrast"].items():
            self.assertEqual(entry["transport_rules"], (rule, rule), cid)
            # The selector's own rule id is a different word, printed in no L9 output (FS1).
            self.assertNotEqual(entry["floor_rules"]["transport_rule_id"], rule)
        artifact = literal_sets(ast.parse(self.source("joulewise/analysis_engine/artifact.py")))
        self.assertNotIn("transport_rule_id", artifact["_FLOOR_KEYS"] | artifact["_V3_FLOOR_KEYS"])

    def test_p42_and_refusal_codes(self):
        # FS2: the kernel's closed refusal codes; the sensitivity record's refused status; the below-minimum code.
        tree = ast.parse(self.source("joulewise/paper_reported_energy.py"))
        codes = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                     and ast.unparse(node.targets[0]) == "PAPER_REPORTED_ENERGY_REFUSAL_CODES")
        self.assertEqual(cmp.REPORTED_REFUSAL_CODES, tuple(e.value for e in codes.args[0].elts))
        estimate = ast.unparse(function(tree, "estimate_reported_cell"))
        self.assertIn(f"raise PaperReportedEnergyRefusal('{cmp.BELOW_MINIMUM_CODE}')", estimate)
        self.assertIn(cmp.BELOW_MINIMUM_CODE, cmp.REPORTED_REFUSAL_CODES)
        sensitivity = self.source("joulewise/b5_analysis/sensitivity.py")
        self.assertIn('"status": "refused",\n                                                  "code": _get(refused[cid], "code")}',
                      sensitivity)
        self.assertEqual(cmp.P42_REFUSED_STATUS, "refused")
        self.assertNotIn("p42_expected_unresolvable", Path(cmp.__file__).read_text())
        # The fixture's code is the issuer's own (tests/b5_analysis T12) and one of the set.
        self.assertIn(producer_fixtures.p42_refusal_code(), cmp.REPORTED_REFUSAL_CODES)
        # The recompute's words (the comparator's other side), from its own source.
        recompute = (ROOT / "scripts/independent_recompute_b5.py").read_text()
        self.assertIn(f'output["p42"][cid] = {{"status": "{cmp.P42_UNRESOLVABLE}"', recompute)
        self.assertIn(f'result["status"] = "{cmp.REPORTED_BELOW_MINIMUM}"', recompute)

    def test_outcome_direction_ceiling_words(self):
        claims = ast.parse(self.source("joulewise/analysis_engine/claims.py"))
        outcomes = next(node.value for node in claims.body if isinstance(node, ast.Assign)
                        and ast.unparse(node.targets[0]) == "CLAIM_OUTCOMES")
        outcomes = {e.value for e in outcomes.args[0].elts}
        decided = {cmp.decide_outcome(dict.fromkeys(names, value)) for value in (False, True)
                   for names in [("positive", "negative", "above_floor", "decision_lower", "decision_upper",
                                  "metrology_lower", "metrology_upper", "reject")]}
        decided |= {cmp.decide_outcome({"positive": True, "negative": False, "above_floor": True, "decision_lower": False,
                                        "decision_upper": True, "metrology_lower": False, "metrology_upper": True,
                                        "reject": True})}
        self.assertEqual(decided, {"not_resolvable", "unresolved", "direction_supported"})
        self.assertLessEqual(decided | {"not_estimable"}, outcomes)
        self.assertTrue(cmp.threshold_free("not_estimable"))
        text = self.source("joulewise/analysis_engine/claims.py")
        self.assertIn('direction = "positive" if numeric_estimate > 0.0 else "negative"', text)
        self.assertEqual({cmp.sign_word({"positive": True, "negative": False}),
                          cmp.sign_word({"positive": False, "negative": True})}, {"positive", "negative"})
        artifact = self.source("joulewise/analysis_engine/artifact.py")
        self.assertIn('ceiling not in {"L2", "L3", "L4"}', artifact)
        self.assertIn('ceiling not in {"L0", "L1"}', artifact)
        self.assertEqual(cmp.READY_CEILINGS, ("L2", "L3", "L4"))
        self.assertIn('"max_never_sum"', artifact)
        manifest = json.loads((cmp.CAMPAIGNS / cmp.MANIFEST).read_text())
        self.assertEqual(cmp.load_registry().alpha, manifest["families"][0]["multiplicity"]["alpha"])

    def test_leave_one_out_words(self):
        engine = self.source("joulewise/analysis_engine/__init__.py")
        self.assertIn('"not_run" if not loo_rows else "complete"', engine)
        self.assertEqual({cmp.loo_status(0, BLOCKS[DECODE]), cmp.loo_status(1, BLOCKS[DECODE])}, {"not_run", "complete"})
        self.assertRegex(engine, r'floor_status = \(\s+"above_floor"\s+if floor\["active_floor_j"\] is not None\s+'
                                 r'and abs\(estimate\.estimate\) > floor\["active_floor_j"\]\s+else "not_above_floor"')
        self.assertEqual(cmp.FLOOR_STATUS_WORDS, ("above_floor", "not_above_floor"))
        tree = ast.parse(self.source("joulewise/analysis_engine/sensitivity.py"))
        names = [call.args[0] for call in ast.walk(function(tree, "influence_triggers")) if isinstance(call, ast.Call)
                 and ast.unparse(call.func) == "triggers.append"]
        constant = next(node.value.value for node in tree.body if isinstance(node, ast.Assign)
                        and ast.unparse(node.targets[0]) == "MAGNITUDE_INFLUENCE_TRIGGER")
        self.assertEqual(cmp.INFLUENCE_TRIGGERS, tuple(n.value if isinstance(n, ast.Constant) else constant for n in names))
        self.assertIn(f"abs(loo_estimate - full_estimate) > {cmp.MAGNITUDE_SHARE} * threshold", ast.unparse(tree))
        # The recompute's own words the comparator reads (its other side): the exclusions re-derivation, the meter
        # window basis.
        recompute = (ROOT / "scripts/independent_recompute_b5.py").read_text()
        self.assertIn('"status": "disagrees" if differing else "agrees"', recompute)
        self.assertIn('"window_basis": "controller_stamps" if controller else', recompute)
        # The arm ids the engine prints, in arm order.
        self.assertIn('arm_by_condition = dict(zip(condition_ids, ("A", "B"), strict=True))', engine)

    def test_closeout_and_disclosure_words(self):
        closeout = self.source("joulewise/dominance_closeout.py")
        self.assertIn(f"DOMINANCE_THRESHOLD = {cmp.DOMINANCE_THRESHOLD!r}", closeout)
        self.assertIn('"passes": ratio >= DOMINANCE_THRESHOLD,', closeout)
        self.assertIn('branch = "A" if all_independent and all_common else "B"', closeout)
        self.assertEqual(cmp.DOMINANCE_BRANCHES, ("A", "B"))
        self.assertIn('"status": "complete",', closeout)
        disclosures = self.source("joulewise/b5_analysis/disclosures.py")
        self.assertIn('label="R" if group=="independent_ratios" else "R_cm"', disclosures)
        self.assertIn('f"{cid} {component}: {label} ', disclosures)
        self.assertEqual(re.match(cmp.RATIO_TEXT, "x absolute: R_cm 1.0")[1], "R_cm")
        ratio_table = (ROOT / "scripts/run_d165_closeout_from_custody.py").read_text()
        for field in cmp.NUMERATOR_FIELDS:
            self.assertIn(f'"{field}"', ratio_table)
        self.assertIn('return {"status": "computed", "mean_j": row["mean_j"],', disclosures)
        self.assertIn('{"status": "not_computable", "n": 0}', disclosures)
        self.assertIn('{"status": "one_quad", "n": 1,', disclosures)
        self.assertIn('return {"status": "computed", "n": estimate.n,', disclosures)
        self.assertIn("agree = abs(delta) <= math.hypot(h_G, primary[\"h_j\"])", disclosures)
        self.assertIn(f"SCREEN_BOUND_S = {cmp.SCREEN_BOUND_S!r}", disclosures)
        self.assertIn('"Qwen3-1.7B-4bit": "qwen3-1p7b", "Qwen3-8B-4bit": "qwen3-8b"', disclosures)
        self.assertEqual(cmp.SHORT_MODELS, {"Qwen3-1.7B-4bit": "qwen3-1p7b", "Qwen3-8B-4bit": "qwen3-8b"})
        self.assertIn('PACK_ORDER = ("alpha", "beta", "gamma")', disclosures)
        self.assertEqual(tuple(cmp.PACKS), ("alpha", "beta", "gamma"))
        sensitivity = self.source("joulewise/b5_analysis/sensitivity.py")
        self.assertIn('"label": "sensitivity"', sensitivity)
        bound = self.source("joulewise/paper_reported_energy.py")
        kinds = next(node.value for node in ast.parse(bound).body if isinstance(node, ast.Assign)
                     and ast.unparse(node.targets[0]) == "BOUND_KINDS")
        self.assertEqual(set(cmp.KIND_ORDER), {e.value for e in kinds.elts})

    def test_line_words(self):
        # Every line word the comparator reads is one disclosures.py prints (an _item word or a dict line).
        source = self.source("joulewise/b5_analysis/disclosures.py")
        printed = {call.args[0].value for call in ast.walk(ast.parse(source)) if isinstance(call, ast.Call)
                   and isinstance(call.func, ast.Name) and call.func.id == "_item" and isinstance(call.args[0], ast.Constant)}
        printed |= set(re.findall(r'"line":\s*"([a-z_0-9]+)"', source))
        # The sensitivity rows' block lines are printed through their loop's word (pinned in test_rc_cmp9).
        printed |= set(re.findall(r'"(sensitivity_(?:reported|floor|contrast))"', source))
        words = {word for section in cmp.LINE_KEYS.values() for word in section}
        self.assertEqual(words - printed - set(cmp.FIXED_SENTENCE_WORDS), set())
        for word in cmp.CELL_WORDS + cmp.CONTRAST_WORDS + cmp.BLOCK_WORDS + cmp.WINDOW_LINES + cmp.TRIPWIRES:
            self.assertIn(word, printed | set(cmp.TRIPWIRES))

    def test_history_words_and_keys(self):
        # FS4: the history lines' keys and words (disclosures._history_lines) and the index's (windows, archive).
        source = self.source("joulewise/b5_analysis/disclosures.py")
        history = function(ast.parse(source), "_history_lines")
        text = ast.unparse(history)
        self.assertIn("r.entry.seal != 'second'", text)
        self.assertEqual(cmp.DECIDING_SEAL, "second")
        self.assertIn("record.kind == 'no_archive'", text)
        self.assertIn('if entry.entry_kind == "no_archive":', self.source("joulewise/b5_analysis/archive.py"))
        self.assertEqual(cmp.NO_ARCHIVE, "no_archive")
        values = next(node.value for node in ast.walk(history) if isinstance(node, ast.Assign)
                      and ast.unparse(node.targets[0]) == "values")
        self.assertEqual(set(cmp.HISTORY_KEYS), {k.value for k in values.keys})
        update = next(node for node in ast.walk(history) if isinstance(node, ast.Call)
                      and ast.unparse(node.func) == "values.update")
        self.assertEqual(set(cmp.HARVESTED_HISTORY_KEYS), {k.arg for k in update.keywords})
        for word in ("attempt_count", "attempt_history", "g10", "superseded_history"):
            self.assertIn(f"_item('{word}'", text)
        windows = self.source("joulewise/b5_analysis/windows.py")
        self.assertIn(f'"{cmp.WINDOW_INDEX_SCHEMA}"', windows)
        self.assertEqual(cmp.WINDOW_INDEX, ROOT / "tests/independent_recompute/window_index/synthetic.json")
        self.assertTrue((ROOT / "configs/analysis/b5/analysed_windows.json").is_file())
        self.assertIn("_B5_WINDOW_INDEX_PATH = \"configs/analysis/b5/analysed_windows.json\"",
                      self.source("joulewise/paper_custody.py"))
        dry_run = self.source("joulewise/b5_analysis/dry_run.py")
        self.assertIn("'window_index_sha256': window_index_sha256", dry_run)

    def test_finalized_manifest_words(self):
        # FABLE F4: the fill names the claim artifact's analysis manifest (manifest_id, file_sha256), which step 8
        # writes as <manifest_id>.finalized.json with a lineage naming the sealed prospective manifest.
        artifact = literal_sets(ast.parse(self.source("joulewise/analysis_engine/artifact.py")))
        self.assertEqual(set(cmp.FINALIZED_MANIFEST_KEYS), artifact["_INPUT_ARTIFACT_KEYS"])
        manifest = self.source("joulewise/analysis_manifest_v3.py")
        self.assertIn('FINALIZED_BASENAME_SUFFIX = ".finalized.json"', manifest)
        self.assertIn('"prospective_manifest_sha256": prospective_sha256,', manifest)
        self.assertIn("hashlib.sha256(prospective_raw).hexdigest()", manifest)
        self.assertIn("FINALIZATION = 'finalized'", self.source("joulewise/b5_analysis/dry_run.py"))
        self.assertTrue(re.fullmatch(cmp.FINALIZED_MANIFEST, "finalized/am-x.finalized.json"))
        self.assertIn('output["gamma"]["finalized_manifest"] = deepcopy(artifact["inputs"]["analysis_manifest"])',
                      self.source("joulewise/results_fill_adapter.py"))

    def test_extended_fill_precondition(self):
        # FABLE F3: the fill prints the extended keys only when the adapter is given the finalized manifest or the
        # floor artifact (results_fill_adapter: extended = any(...)); block 5's build script passes both.
        adapter = self.source("joulewise/results_fill_adapter.py")
        self.assertIn("extended = any(value is not None for value in (finalized_manifest_raw, floor_artifact_raw,", adapter)
        build = self.source("scripts/build_results_fill_input.py")
        self.assertIn("finalized_manifest_raw=manifest_raw,", build)
        self.assertIn("floor_artifact_raw=floor_raw,", build)
        self.assertIn("manifest_raw=", build)

    def test_new_engine_key_sets(self):
        # OPUS F2, FABLE F2: the nested key sets the table now requires.
        sets = literal_sets(ast.parse(self.source("joulewise/analysis_engine/artifact.py")))
        for key, name in (("bundle_blocks", "_BUNDLE_BLOCK_KEYS"), ("block", "_BLOCK_KEYS"),
                          ("randomization", "_RANDOMIZATION_KEYS"), ("variance_contribution", "_VARIANCE_CONTRIBUTION_KEYS")):
            with self.subTest(name):
                self.assertEqual(set(cmp.ENGINE_KEYS[key]), sets[name])
                self.assertEqual(len(cmp.ENGINE_KEYS[key]), len(sets[name]))


def set_loo(case, block, l9_estimate, own_estimate, triggers, full=None):
    """A kept block's leave-one-out row: L9's estimate and triggers (verdict and fill), the recompute's estimate."""
    position = BLOCKS[DECODE].index(block) + 1
    for contrast in contrast_rows(case):
        row = next(r for r in contrast["loo"]["rows"] if r["omitted_block_id"] == block)
        row.update(estimate=l9_estimate, influence_triggers=list(triggers))
        if full is not None:
            contrast.setdefault("estimate", None)
    own = next(r for r in case.ours["contrasts"][DECODE]["loo"] if r["block_number"] == position)
    own["dbar_j"] = own_estimate


class TransportRuleTests(Case):
    """FS1: each resolution's transport_rule_id is compared with its arm's registered group_rule_id."""
    def test_engine_word_agrees_and_the_selector_word_disagrees(self):
        out = self.shipped()
        row = self.row(out, f"contrast/{DECODE}/resolution/0/transport_rule_id")
        self.assertEqual((row["l9"], row["verdict"]), (test_comparator.TRANSPORT_RULE_ID, "AGREE"))
        self.assertEqual(self.outcome(), 0)
        # Counterfactual (f9f86869e): the selector's word as the reference refuses the engine's word, 4 rows.
        registry = cmp.load_registry()
        old ={cid: dict(entry, transport_rules=(entry["floor_rules"]["transport_rule_id"],) * 2)
               for cid, entry in registry.tables["contrast"].items()}
        with mock.patch.dict(registry.tables["contrast"], old):
            out = self.shipped()
            failing = [r["key"] for r in out["comparisons"] if r["verdict"] != "AGREE"]
            self.assertEqual(len([k for k in failing if k.endswith("/transport_rule_id")]), 4)
        # A resolution printing the selector's word disagrees.
        for contrast in contrast_rows(self):
            contrast["floor"]["resolutions"][1]["transport_rule_id"] = "exact_stack_only.v1"
        self.assertNotEqual(self.outcome(), 0)


class P42CodeTests(Case):
    """FS2: the p42 code is a member of the producer's closed refusal codes and the same in every L9 copy."""
    def copies(self, code, which=None):
        for name in (PROJECTION, f"outputs/{test_comparator.SHA}-projection-beta.json"):
            for row in self.files[name]["refused_cells"]:
                if which in (None, "projection"):
                    row["code"] = code
        for record in (self.files[SENSITIVITY], self.files[DISCLOSURE]["sensitivity"]):
            for row in record["reported_cells"]:
                if row["status"] == "refused" and which in (None, "record"):
                    row["code"] = code
        for line in self.files[DISCLOSURE]["block_lines"]:
            if line["line"] == "sensitivity_reported" and line["record"]["status"] == "refused" and which in (None, "line"):
                line["record"]["code"] = code

    def test_producer_code_passes_and_the_invented_word_refuses(self):
        self.base()
        code, err, out = self.exit_code(CODED)
        self.assertEqual((code, err), (0, ""))
        row = self.row(out, "sensitivity/alpha/df-ph-prefill-p42-qwen3-1p7b/code")
        self.assertEqual((row["l9"], row["recompute"]), (producer_fixtures.p42_refusal_code(),) * 2)
        self.assertEqual(out["coverage"]["leaves"]["disclosure:sensitivity/reported_cells/*/code"], "outcome_word")
        # The invented word (f9f86869e's P42_EXIT) in every copy: not a producer code, DISAGREE.
        self.base()
        self.copies("p42_expected_unresolvable")
        self.assertNotEqual(self.outcome(), 0)
        # Counterfactual: f9f86869e's reference (the invented word) passes the invented fixture.
        with mock.patch.object(cmp, "refused_code", lambda *args, **kwargs: "p42_expected_unresolvable"):
            self.assertEqual(self.outcome(), 0)
            # ... and refuses the producer's word (the full-size window's FS2 rows).
            self.base()
            self.assertNotEqual(self.outcome(), 0)

    def test_every_copy_must_print_the_same_member_code(self):
        other = "paper_reported_energy_schema_invalid"
        for which in ("projection", "record", "line"):
            with self.subTest(which):
                self.base()
                self.copies(other, which)
                self.assertNotEqual(self.outcome(), 0)
        # RC-CMP-11 F2: a member code printed identically in every copy is not the producer's p42 code: non-zero.
        self.base()
        self.copies(other)
        self.assertNotEqual(self.outcome(), 0)
        # Counterfactual (1affc4208, NEEDS_RULING 1): any member code passed.
        original = cmp.refused_code
        with mock.patch.object(cmp, "refused_code", lambda custody, record, pack, cell_id, expected=None:
                               original(custody, record, pack, cell_id,
                                        None if expected == cmp.P42_REFUSAL_CODE else expected)):
            self.assertEqual(self.outcome(), 0)


class WithinBarTests(Case):
    """FS3: a word derived from the sign of, or a threshold on, a compared number is compared only when the number
    lies outside its family bar from the threshold on both sides."""
    BLOCK = BLOCKS[DECODE][9]

    def sign_flip(self, l9_estimate, own_estimate, triggers):
        self.base()
        set_loo(self, self.BLOCK, l9_estimate, own_estimate, triggers)

    def test_full_size_loo_b10_sign_flip_inside_the_bar_passes(self):
        # The full-size window: decode loo b10 dbar L9 +3.55e-15, recompute -1.78e-15 (bar 1e-6), L9's triggers
        # ["estimate_sign"] against the recompute's [].
        self.sign_flip(3.55e-15, -1.78e-15, ["estimate_sign"])
        code, err, out = self.exit_code(CODED)
        self.assertEqual((code, err), (0, ""))
        row = self.row(out, f"{DECODE}/loo/b10/influence_triggers/0", "outcome_word")
        self.assertEqual((row["reason"], row["verdict"]), ("within_bar_undetermined", "AGREE"))
        self.assertIn(f"{DECODE}/loo/b10/dbar_j", row["within_bar"])
        # L9 printing no trigger there passes too (the word is undetermined either way).
        self.sign_flip(3.55e-15, -1.78e-15, [])
        self.assertEqual(self.outcome(), 0)
        # Counterfactual (f9f86869e): every word compared exactly, no trigger undetermined: the trigger rows DISAGREE.
        self.sign_flip(3.55e-15, -1.78e-15, ["estimate_sign"])
        with mock.patch.object(cmp.Comparison, "word", plain_exact), \
                mock.patch.object(cmp, "undetermined_triggers", lambda c, tests: []):
            self.assertNotEqual(self.outcome(), 0)

    def test_sign_flip_outside_the_bar_disagrees(self):
        # Both estimates agree (+1.0) but outside the bar from 0: the sign is decided, so a missing or invented
        # trigger disagrees.
        self.sign_flip(1.0, 1.0, [])
        code, _, out = self.exit_code(CODED)
        self.assertNotEqual(code, 0)
        row = self.row(out, f"{DECODE}/loo/b10/influence_triggers", "outcome_word")
        self.assertEqual((row["l9"], row["recompute"], row["verdict"]), ([], ["estimate_sign"], "DISAGREE"))
        self.sign_flip(1.0, 1.0, ["estimate_sign"])
        self.assertEqual(self.outcome(), 0)
        # A sign flip inside the bar whose numbers disagree: the row is DISAGREE (the numbers decide).
        self.sign_flip(3.55e-15, -5e-6, ["estimate_sign"])
        self.assertNotEqual(self.outcome(), 0)

    def test_below_screen_bound_inside_and_outside_the_bar(self):
        for b_op, l9_word, own_word, expected in ((cmp.SCREEN_BOUND_S, False, None, 0),
                                                  # RC-CMP-11 F1: b_op identical on both sides decides the
                                                  # test (b_op < bound), so a printed False now disagrees.
                                                  (cmp.SCREEN_BOUND_S * (1 - 2e-7), False, None, 1),
                                                  (0.0375, True, None, 1)):
            with self.subTest(b_op=b_op, word=l9_word):
                self.base()
                for pack in ("alpha",):
                    lines, index = find(self, "below_screen_bound")
                    lines[index].update(b_op_s=b_op, below=l9_word)
                    self.ours["windows"]["ALPHA"]["b_op_s"] = b_op
                    for name in (f"brackets/{test_comparator.SHA}-alpha.json",):
                        self.files[name]["evaluation"]["acceptance"]["allowance"]["operative_b_fiducial_binary64_s"] = b_op
                    for record in (self.files[SENSITIVITY], self.files[DISCLOSURE]["sensitivity"]):
                        record["windows"]["alpha"]["b_op_s"] = b_op
                    for line in self.files[DISCLOSURE]["block_lines"]:
                        if line["line"] == "sensitivity_window" and line["pack"] == "alpha":
                            line["b_op_s"] = b_op
                self.assertEqual(self.outcome() != 0, bool(expected))

    def test_holm_rejection_at_alpha(self):
        # An adjusted p within its bar of the registered alpha leaves the rejection word undetermined.
        self.base()
        alpha = cmp.load_registry().alpha
        for contrast in contrast_rows(self):
            contrast["multiplicity"].update(adjusted_p=alpha, rejected=True)
        self.ours["contrasts"][DECODE]["holm_p"] = alpha + 5e-7
        out = self.exit_code(CODED)[2]
        row = self.row(out, f"{DECODE}/holm_reject")
        self.assertEqual((row["l9"], row["recompute"], row["verdict"]), (True, False, "AGREE"))
        # Outside the bar the word is compared.
        self.ours["contrasts"][DECODE]["holm_p"] = alpha + 0.5
        for contrast in contrast_rows(self):
            contrast["multiplicity"]["adjusted_p"] = alpha + 0.5
        self.assertNotEqual(self.outcome(), 0)

    def test_relation_words_inside_the_bar(self):
        # Unwidened, every sensitivity value equals its primary value bit for bit on both sides: RC-CMP-11 F1 decides
        # each test (no within_bar_undetermined row), and the producer's words agree.
        self.base(widened=False)
        code, err, out = self.exit_code(CODED)
        self.assertEqual((code, err), (0, ""))
        rows = [r for r in out["comparisons"] if r["key"].endswith("/equals_primary")]
        self.assertTrue(rows and all(r["verdict"] == "AGREE" for r in rows))
        self.assertFalse(any(r.get("reason") == "within_bar_undetermined" for r in rows))
        # A decided difference (widened) still compares the word: L9 printing True there disagrees.
        self.base(widened=True)
        for record in (self.files[SENSITIVITY], self.files[DISCLOSURE]["sensitivity"]):
            next(r for r in record["floor_cells"] if r["cell_id"] == "d117-qwen3-1p7b-decode-floor-v5")["equals_primary"] = True
        for line in self.files[DISCLOSURE]["block_lines"]:
            if line["line"] == "sensitivity_floor" and line["record"]["cell_id"] == "d117-qwen3-1p7b-decode-floor-v5":
                line["record"]["equals_primary"] = True
        self.assertNotEqual(self.outcome(), 0)


def history_case(case, attempts, records=None, edit=None):
    """A window index with these attempts; the disclosure's history lines printed by the producer from it."""
    directory = Path(tempfile.mkdtemp(dir=case.root))
    path = directory / "index.json"
    path.write_text(json.dumps({"schema": cmp.WINDOW_INDEX_SCHEMA, "attempts": attempts}))
    lines = case.files[DISCLOSURE]["block_lines"]
    lines[:] = [line for line in lines if line["line"] not in ("attempt_count", "attempt_history", "g10",
                                                                 "superseded_history")]
    lines += producer_fixtures.history_lines(attempts, **(records or {}))
    if edit:
        edit(lines)
    return mock.patch.object(cmp, "WINDOW_INDEX", path)


def attempt(pack, number, plan, seal="second", kind="harvested", verdict="COLLECTED", cause=None, **extra):
    return {"pack": pack, "pack_id": "synthetic-" + pack, "attempt": number, "plan_id": plan, "seal": seal,
            "entry_kind": kind, "verdict": verdict, "claim_usable": seal == "second", "cause_key": cause, **extra}


HISTORY = ([attempt("alpha", 1, "plan-alpha-a1", seal="first", verdict="COLLECTED", cause="NEG8+cell.below_minimum",
                    g10_requested=True),
            attempt("alpha", 2, "plan-alpha-a2", seal="first", kind="no_archive", verdict="NO_COLLECTION"),
            attempt("alpha", 3, "plan-alpha"), attempt("beta", 1, "plan-beta-a1", cause="harvest.fault",
                                                       verdict="HARVEST_FAULT"),
            attempt("beta", 2, "plan-beta", g10_requested=True, g10_redraw_cycles=2), attempt("gamma", 1, "plan-gamma")])


class HistoryTests(Case):
    """FS4: the history lines are table entries keyed on the window index; every producer leaf is bound or named."""
    def test_producer_history_passes_with_every_leaf_bound(self):
        self.base()
        with history_case(self, HISTORY, {"plan-beta": {"g10_codes": {"g10.redraw": 1}},
                                          "plan-alpha": {"bracket": {"observed_triggers": ["t1"],
                                                                     "other_session_systematic_sequences": [3]}}}):
            code, err, out = self.exit_code(CODED)
        self.assertEqual((code, err), (0, ""))
        leaves = out["coverage"]["leaves"]
        for path, family in (("block_lines/attempt_count/causes/*", "outcome_word"),
                             ("block_lines/attempt_history/cause_key", "outcome_word"),
                             ("block_lines/attempt_history/verdict", "outcome_word"),
                             ("block_lines/attempt_count/count", "count"),
                             ("block_lines/g10/redraw_cycles", "outcome_word")):
            self.assertEqual(leaves["disclosure:" + path], family, path)
        self.assertTrue(leaves["disclosure:block_lines/attempt_history/triggers"].startswith(cmp.NULL_NAMED))
        checks = {c["check"] for c in out["expected_checks"]["checks"]}
        self.assertIn("disclosure/block_lines/superseded_history", checks)
        self.assertIn("disclosure/block_lines/attempt_count/alpha/superseded", checks)
        # Counterfactual (f9f86869e): without the history rules the producer's null leaves are unmapped (FS4).
        self.base()
        old = tuple(rule for rule in cmp.COVERAGE if "history/" not in str(rule[-1])
                    and "no calibration bracket recorded for the attempt" not in str(rule[-1]))
        with history_case(self, HISTORY), mock.patch.object(cmp, "COVERAGE", old):
            self.assertEqual(self.exit_code(CODED)[:2], (2, "refused=step11_unmapped_fill\n"))

    def test_history_drops_and_changes_refuse(self):
        def drop(word, nth=0):
            def edit(lines):
                del lines[[i for i, line in enumerate(lines) if line["line"] == word][nth]]
            return edit

        def change(word, key, value, nth=0):
            def edit(lines):
                [line for line in lines if line["line"] == word][nth][key] = value
            return edit
        cases = {"attempt_history dropped": drop("attempt_history", 2),
                 "attempt_count dropped": drop("attempt_count", 1),
                 "superseded_history dropped": drop("superseded_history"),
                 "g10 dropped (requested)": drop("g10", 0),
                 "cause key changed": change("attempt_history", "cause_key", "NEG8"),
                 "null cause key named": change("attempt_history", "cause_key", "none", 2),
                 "cause list changed": change("attempt_count", "causes", [None], 3),
                 "count changed": change("attempt_count", "count", 3),
                 "verdict changed": change("attempt_history", "verdict", "COLLECTED", 1),
                 "superseded flipped": change("attempt_history", "superseded", False, 4),
                 "redraw cycles changed": change("g10", "redraw_cycles", 3, 1),
                 "an attempt the index lacks": lambda lines: lines.append(dict(
                     [line for line in lines if line["line"] == "attempt_history"][-1], plan_id="plan-other"))}
        for label, edit in cases.items():
            with self.subTest(label):
                self.base()
                with history_case(self, HISTORY, edit=edit):
                    self.assertNotEqual(self.outcome(), 0)

    def test_the_index_is_bound_to_the_record(self):
        self.base()
        with history_case(self, HISTORY):
            root = self.custody()
        # The custody's record names another index: the run refuses before any comparison.
        with self.assertRaisesRegex(cmp.Refusal, "window_index_digest_differs"):
            cmp.Custody(root, [], cmp.load_registry())
        with self.assertRaisesRegex(cmp.Refusal, "window_index_unreadable"):
            cmp.Custody(root, [], cmp.load_registry(), root / "absent.json")

    def test_reharvest_accounts_follow_harvest_once(self):
        self.base()
        lines = self.files[DISCLOSURE]["block_lines"]
        lines.append(item("reharvest_account", False, "alpha: re-harvest", pack="alpha", original_pin="a", deciding_pin="b",
                          original_harvest_sha256="ab" * 32, deciding_harvest_sha256="cd" * 32, reason="r",
                          survivors_before=3, survivors_after=2))
        self.assertNotEqual(self.outcome(), 0)
        next(line for line in lines if line["line"] == "harvest_once")["no_analysed_window_harvested_twice"] = False
        self.assertEqual(self.outcome(), 0)
        lines[:] = [line for line in lines if line["line"] != "reharvest_account"]
        self.assertNotEqual(self.outcome(), 0)


def n2_case(case, widened=True, kept=2):
    """Opus's probe_cmp9 n2: the decode contrast keeps blocks b02.. (kept n of 1 or 2): every copy of n, the kept set,
    the engine's rows (one per kept block) and the recompute's none (n < LOO_MIN)."""
    saved = dict(test_comparator.KEPT)
    test_comparator.KEPT[DECODE] = BLOCKS[DECODE][1:1 + kept]
    try:
        case.base(widened)
    finally:
        test_comparator.KEPT.clear()
        test_comparator.KEPT.update(saved)
    verdict, fill = contrast_rows(case)
    blocks, keep = list(BLOCKS[DECODE]), list(BLOCKS[DECODE][1:1 + kept])
    removed = [b for b in blocks if b not in keep]
    for row in (verdict, fill):
        row["sampling"].update(kept_n=kept, observed_complete_n=kept, removed_block_ids=removed)
    verdict["estimator"].update(n=kept, df=kept - 1)
    fill.update(n=kept, df=kept - 1, kept_block_ids=keep, removed_block_ids=removed)
    for row in verdict["loo"]["rows"] + fill["loo"]["rows"]:
        row.update(n_blocks=kept - 1, df=kept - 2)
    for line in case.files[DISCLOSURE]["contrasts"]:
        if DECODE in (line.get("contrast_id"), line.get("cell_id")):
            if line["line"] == "primary_contrast":
                line["estimator"].update(n=kept, df=kept - 1)
            if line["line"] == "contrast_interval":
                line["n"] = kept
            if line["line"] == "loo_counts":
                line["count"] = kept
            if line["line"] == "kept_units":
                line["n_b"] = kept
    case.ours["contrasts"][DECODE].update(n=kept, kept_quads=keep, loo=[])
    return verdict, fill


class LeaveOneOutTests(Case):
    """OPUS F1: at a kept n of 1 or 2, L9's rows and loo_counts are bound to the kept n."""
    def test_rows_dropped_refuse(self):
        for kept in (1, 2):
            for widened in (True, False):
                with self.subTest(kept=kept, widened=widened):
                    n2_case(self, widened, kept)
                    # Sound (engine rows printed, recompute none): refuses, the declared safe side (NEEDS_RULING 2).
                    self.assertNotEqual(self.outcome(), 0)
                    verdict, fill = n2_case(self, widened, kept)
                    verdict["loo"]["rows"], fill["loo"]["rows"] = [], []
                    lines, index = find(self, "loo_counts")
                    lines[index]["count"] = 0
                    code, _, out = self.exit_code(CODED)
                    self.assertNotEqual(code, 0)
                    rows = {r["key"]: r for r in out["comparisons"]}
                    self.assertEqual((rows[f"{DECODE}/loo/l9_rows"]["l9"], rows[f"{DECODE}/loo/l9_rows"]["recompute"]),
                                     (0, kept))
                    self.assertEqual(rows[f"disclosure/{DECODE}/loo_counts/count"]["recompute"], kept)
                    verdict, fill = n2_case(self, widened, kept)
                    verdict["loo"]["rows"], fill["loo"]["rows"] = [], []
                    self.assertNotEqual(self.outcome(), 0)

    def test_rows_dropped_passed_before(self):
        # Counterfactual (f9f86869e): rows bound from LOO_MIN, loo_counts to the recompute's printed rows, the
        # table's loo condition from LOO_MIN: the joint drop exits 0 (Opus cmp9_n2.out).
        verdict, fill = n2_case(self, True, 2)
        verdict["loo"]["rows"], fill["loo"]["rows"] = [], []
        lines, index = find(self, "loo_counts")
        lines[index]["count"] = 0
        with mock.patch.object(cmp, "loo_rows_expected", lambda n, blocks: cmp.finite(n) and n >= cmp.LOO_MIN), \
                mock.patch.object(cmp, "loo_status", side_effect=lambda n, blocks: "complete" if n and n >= 1 else
                                  "not_run") as status, \
                mock.patch.object(cmp.Comparison, "numeric", numeric_count_off(cmp.Comparison.numeric)):
            self.assertEqual(self.outcome(), 0)
            self.assertTrue(status.called)


def numeric_count_off(numeric):
    """f9f86869e's loo_counts reference: the rows the recompute printed (none for the decode contrast here)."""
    def patched(self, family, key, l9, ours):
        if key == f"disclosure/{DECODE}/loo_counts/count":
            ours = 0
        return numeric(self, family, key, l9, ours)
    return patched


class NestedKeyTests(Case):
    """OPUS F2, FABLE F2: the producer-unconditional nested keys are required, in the verdict and in the
    disclosure's primary_contrast estimator copy; the verdict's kept-sampling words are bound."""
    def test_each_nested_key_dropped_refuses(self):
        def verdict(case):
            return contrast_rows(case)[0]

        def estimator_copy(case):
            lines, index = find(case, "primary_contrast")
            return lines[index]["estimator"]
        cases = {
            "included_bundle_ids": lambda c: verdict(c)["bundle_blocks"].pop("included_bundle_ids"),
            "block bundle_a_id": lambda c: verdict(c)["bundle_blocks"]["blocks"][3].pop("bundle_a_id"),
            "block bundle_b_id": lambda c: verdict(c)["bundle_blocks"]["blocks"][3].pop("bundle_b_id"),
            "block reason_codes": lambda c: verdict(c)["bundle_blocks"]["blocks"][3].pop("reason_codes"),
            "removed block included": lambda c: verdict(c)["bundle_blocks"]["blocks"][0].pop("included"),
            "repeat_point_CI95 lower": lambda c: verdict(c)["estimator"]["repeat_point_CI95"].pop("lower"),
            "variance contribution key": lambda c: verdict(c)["estimator"]["variance_contributions"][0].pop(
                "squared_standard_error"),
            "copy repeat_point_CI95 upper": lambda c: estimator_copy(c)["repeat_point_CI95"].pop("upper"),
            "copy variance contribution key": lambda c: estimator_copy(c)["variance_contributions"][0].pop("name")}
        for key in cmp.ENGINE_KEYS["randomization"]:
            cases["randomization_check/" + key] = (lambda k: lambda c: verdict(c)["randomization_check"].pop(k))(key)
        for label, edit in cases.items():
            with self.subTest(label):
                self.base()
                edit(self)
                self.assertNotEqual(self.outcome(), 0)
                # Counterfactual (f9f86869e): the table without these keys passes the drop.
                with mock.patch.object(cmp, "ESTIMATOR_NESTED", ()), \
                        mock.patch.dict(cmp.ENGINE_KEYS, bundle_blocks=("planned_block_ids", "blocks"), randomization=(),
                                        block=("block_id",)), \
                        mock.patch.object(cmp.Comparison, "exact", rows_off(cmp.Comparison.exact, "/included")):
                    self.assertEqual(self.outcome(), 0, label)

    def test_fable_p6_p7_verdict_sampling_words(self):
        cases = {"P6.a removed_block_ids emptied": lambda row: row["sampling"].update(removed_block_ids=[]),
                 "P6.b kept_n 5 against n 9": lambda row: row["sampling"].update(kept_n=5),
                 "P7.a the not-kept block's included null": lambda row: row["bundle_blocks"]["blocks"][0].update(
                     included=None)}
        for label, edit in cases.items():
            with self.subTest(label):
                self.base()
                edit(contrast_rows(self)[0])
                self.assertNotEqual(self.outcome(), 0)
                # Counterfactual (f9f86869e): none of the three rows.
                with mock.patch.object(cmp.Comparison, "exact", rows_off(
                        cmp.Comparison.exact, "/included", *[f"/sampling_removed_block_ids{s}/{i}" for i in range(10)
                                                             for s in ("", "_position")])), \
                        mock.patch.object(cmp.Comparison, "numeric", numeric_rows_off(cmp.Comparison.numeric, "/kept_n")), \
                        mock.patch.object(cmp, "COVERAGE", F9_SAMPLING_RULES + cmp.COVERAGE), \
                        mock.patch.object(cmp, "COPIED_LISTS", ()):
                    self.assertEqual(self.outcome(), 0, label)


# f9f86869e's rules for the fill's sampling copies: kept_n bound to the estimator's n, the removed ids to the bundle's.
F9_SAMPLING_RULES = ((r"fill:gamma/contrasts/\*/sampling/kept_n", "count", "{cid}/n"),
                     (r"fill:gamma/contrasts/\*/sampling/removed_block_ids/\*", "routing_id",
                      "contrast/{cid}/removed_block_ids/{removed_block}"))


def rows_off(exact, *suffixes):
    def patched(self, family, key, l9, ours, raw=cmp.MISSING):
        return None if key.endswith(suffixes) else exact(self, family, key, l9, ours, raw)
    return patched


def numeric_rows_off(numeric, *suffixes):
    def patched(self, family, key, l9, ours):
        return None if key.endswith(suffixes) else numeric(self, family, key, l9, ours)
    return patched


def l9_reported_refused(case):
    """Fable's probes.py: L9 refuses ALPHA's decode reported cell (below the registered minimum) in every copy."""
    projection = case.files[PROJECTION]
    projection["cells"] = [x for x in projection["cells"] if x["cell_id"] != REPORTED]
    projection["refused_cells"].append({"cell_id": REPORTED, "code": cmp.BELOW_MINIMUM_CODE})
    refused = {"pack": "alpha", "cell_id": REPORTED, "status": "refused", "code": cmp.BELOW_MINIMUM_CODE}
    for record in (case.files[SENSITIVITY], case.files[DISCLOSURE]["sensitivity"]):
        record["reported_cells"] = [refused if r["cell_id"] == REPORTED else r for r in record["reported_cells"]]
    for line in case.files[DISCLOSURE]["block_lines"]:
        if line["line"] == "sensitivity_reported" and line["record"].get("cell_id") == REPORTED:
            line["record"] = dict(refused)
    case.files[DISCLOSURE]["cells"] = [x for x in case.files[DISCLOSURE]["cells"]
                                       if not (x.get("cell_id") == REPORTED and x["line"] in cmp.CELL_WORDS)]


def ours_reported_refused(case, counts=True):
    case.ours["reported_cells"][FAMILY] = {"status": "below_minimum", "n_r": 2, "n_b": 2} if counts else \
        {"status": "below_minimum"}
    case.ours["disclosures"]["sensitivity_bound"]["reported_cells"][FAMILY] = {"status": "below_minimum"}
    case.ours["disclosures"]["battery_assist"].pop(FAMILY, None)
    case.ours["disclosures"]["cross_window"].pop("Qwen3-1.7B-4bit/decode", None)


def l9_floor_refused(case):
    for cell in case.files[EXTRACTION]["cells"]:
        if cell["cell_id"] == ALPHA_CELLS["absolute"]:
            cell.pop("operative_floor_j", None)
            cell.pop("n_admitted", None)
            cell["floor"] = None
    case.files[DISCLOSURE]["floors"] = [x for x in case.files[DISCLOSURE]["floors"]
                                        if not (x["line"] == "floor_composition" and x["cell_id"] == ALPHA_CELLS["absolute"])]


def ours_floor_refused(case):
    case.ours["floors"][FLOOR_KEY] = {"status": "below_minimum", "n": 2}


def l9_ratio_bare(case):
    lines, index = find(case, "magnitude_ratio", lambda row: row["contrast_id"] == DECODE)
    for key in ("log_mean", "log_sd", "ratio", "lower", "upper"):
        lines[index].pop(key)
    lines[index]["text"] = DECODE + ": registered descriptive estimates: ratio not computable"


def ours_ratio_none(case):
    case.ours["descriptive"][DECODE].update(ratio=None, ratio_interval=None)


class ConditionalFamilyTests(Case):
    """FABLE F1: a conditional family's value rows are built under the table's own condition; when both sides
    refuse, the status words are compared and no value row is built (Fable's P1-P4, X1-X5)."""
    def test_both_sides_refuse_passes_and_one_side_refuses(self):
        both = {"P1 reported": (l9_reported_refused, ours_reported_refused),
                "P3 floor": (l9_floor_refused, ours_floor_refused),
                "P4 ratio": (l9_ratio_bare, ours_ratio_none),
                "X5 reported, status only": (l9_reported_refused, lambda c: ours_reported_refused(c, counts=False))}
        for widened in (True, False):
            for label, (l9, own) in both.items():
                with self.subTest(label, widened=widened):
                    self.base(widened)
                    l9(self)
                    own(self)
                    code, err, out = self.exit_code(CODED)
                    self.assertEqual((code, err), (0, ""), [(r["key"], r["l9"], r["recompute"]) for r in
                                                            out["comparisons"] if r["verdict"] != "AGREE"][:6])
                    for side in (l9, own):
                        self.base(widened)
                        side(self)
                        self.assertNotEqual(self.outcome(), 0)
        # The status words are compared: L9's below-minimum code replaced by another member code disagrees.
        self.base()
        l9_reported_refused(self)
        ours_reported_refused(self)
        self.files[PROJECTION]["refused_cells"][-1]["code"] = "paper_reported_energy_schema_invalid"
        self.assertNotEqual(self.outcome(), 0)

    def test_value_rows_were_built_before(self):
        # Counterfactual (f9f86869e): the value rows built whatever the condition: both-refused windows refuse.
        for label, (l9, own) in {"P3 floor": (l9_floor_refused, ours_floor_refused),
                                 "P4 ratio": (l9_ratio_bare, ours_ratio_none)}.items():
            with self.subTest(label):
                self.base()
                l9(self)
                own(self)
                with mock.patch.object(cmp, "holds", lambda custody, ours, condition: True):
                    self.assertNotEqual(self.outcome(), 0)


class FinalizedManifestTests(Case):
    """FABLE F4: the fill's finalized manifest digest is bound (Fable's P8); Custody.step_ok is gone."""
    def test_p8_digest_differs(self):
        self.base()
        self.assertEqual(self.outcome(), 0)
        self.files[FILL]["gamma"]["finalized_manifest"]["file_sha256"] = "9" * 64
        self.assertNotEqual(self.outcome(), 0)
        # Counterfactual (f9f86869e): the identity rule, no row.
        with mock.patch.object(cmp, "compare_fill_identity", lambda c, custody, ours: None), \
                mock.patch.object(cmp, "COVERAGE", ((r"fill:gamma/finalized_manifest/(manifest_id|file_sha256)",
                                                     cmp.IDENTITY),) + cmp.COVERAGE):
            self.assertEqual(self.outcome(), 0)

    def test_the_lineage_must_name_the_sealed_manifest(self):
        self.base()
        self.files[test_comparator.FINALIZED]["lineage"]["prospective_manifest_sha256"] = "8" * 64
        self.files[FILL]["gamma"]["finalized_manifest"]["file_sha256"] = hashlib.sha256(test_comparator.written(
            test_comparator.FINALIZED, self.files[test_comparator.FINALIZED])).hexdigest()
        self.assertNotEqual(self.outcome(), 0)

    def test_step_ok_is_gone(self):
        self.assertFalse(hasattr(cmp.Custody, "step_ok"))


if __name__ == "__main__":
    unittest.main()
