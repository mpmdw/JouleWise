"""RC-CMP-9: the registry-driven expected-check table (the design rule that replaces per-family patches).

Before any comparison the comparator builds one expected-check table from the registered sources only
(compare_b5_recompute.REGISTERED_SOURCES) and requires every entry's item on L9's side and on the recompute's;
an output item outside the table can only DISAGREE. The regressions are Opus's RC-CMP-8 probes
(review/2026-10-29-rc-cmp8-opus-rev probe_cmp8.py confirm, joint2, loo; relabel_ids.out) and Fable's
(review/2026-10-29-rc-cmp8-fable-rev probes.py S1, sweep.py): at 0d317afd4 each drop and relabel named here
exits 0 (confirm.out, joint.out, loo.out, relabel_ids.out, probes.out, sweep.out there); where the check can be
switched off in place, the test also shows the case passing without it (no_table: the comparator before
RC-CMP-9). The producer pins read origin/main as text (git show) and skip only when that ref is absent.
"""
import ast
import copy
import re
import subprocess
import unittest
from unittest import mock

from . import test_comparator
from .test_comparator import DECODE, PREFILL, ROOT, SHA, cmp, no_table
from .test_input_gate import CODED, GateCase
from .test_rc_cmp7 import find, with_neg8, with_references
from .test_rc_cmp8 import FAMILY, FLOOR_CELLS, PROJECTION, REPORTED, SENSITIVITY, contrast_rows, with_sensitivity
from .test_review_fixes import DISCLOSURE, FILL, VERDICTS


def producer(path):
    """A producer source on origin/main, read as text (never imported)."""
    try:
        return subprocess.run(["git", "-C", str(ROOT), "show", "origin/main:" + path], capture_output=True,
                              check=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def literal_sets(tree):
    """Module-level NAME = {..} / (..) literals of strings, by name."""
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            value = node.value
            if isinstance(value, (ast.Set, ast.Tuple, ast.List)) and all(
                    isinstance(e, ast.Constant) and isinstance(e.value, str) for e in value.elts):
                found[node.targets[0].id] = {e.value for e in value.elts}
    return found


def function(tree, name):
    return next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name)


def dict_keys(node):
    return {k.value for k in node.keys if isinstance(k, ast.Constant)}


class ProducerPinTests(unittest.TestCase):
    """F1: every key set the table copies as a literal, pinned to its producer source on origin/main."""
    def source(self, path):
        text = producer(path)
        if text is None:
            self.skipTest("origin/main is not available in this clone")
        return text

    def test_engine_key_sets(self):
        sets = literal_sets(ast.parse(self.source("joulewise/analysis_engine/artifact.py")))
        names = {"contrast": "_CONTRAST_KEYS", "metric": "_METRIC_KEYS", "conditions": "_CONDITION_KEYS",
                 "sampling": "_CONTRAST_SAMPLING_KEYS", "estimator": "_ESTIMATOR_KEYS", "deterministic": "_DETERMINISTIC_KEYS",
                 "floor": "_FLOOR_KEYS", "v3_floor": "_V3_FLOOR_KEYS", "arm_gate": "_ARM_GATE_KEYS",
                 "resolution": "_FLOOR_RESOLUTION_KEYS", "multiplicity": "_MULTIPLICITY_EVIDENCE_KEYS", "loo": "_LOO_KEYS",
                 "loo_row": "_LOO_ROW_KEYS", "evaluation": "_EVALUATION_KEYS", "deterministic_term": "_DETERMINISTIC_TERM_KEYS"}
        for key, name in names.items():
            with self.subTest(name):
                self.assertEqual(set(cmp.ENGINE_KEYS[key]), sets[name])
                self.assertEqual(len(cmp.ENGINE_KEYS[key]), len(sets[name]))
        source = self.source("joulewise/analysis_engine/artifact.py")
        self.assertIn('({"kept_n", "removed_block_ids"} if kept_sampling else set())', source)
        self.assertEqual(cmp.ENGINE_KEYS["kept_sampling"], ("kept_n", "removed_block_ids"))
        # A v3 contrast requires the whole armwise floor, exactly two gates (the table's arm positions).
        self.assertIn("v3 contrast requires the complete cross-stack armwise floor contract", source)
        self.assertIn("requires exactly two arm gates", source)
        self.assertEqual(len(cmp.ARMS), 2)

    def test_fill_shape(self):
        tree = ast.parse(self.source("joulewise/results_fill_adapter.py"))
        adapt = function(tree, "adapt_claim_verdicts")
        base = next(dict_keys(call.args[0]) for call in ast.walk(adapt) if isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute) and call.func.attr == "append" and call.args
                    and isinstance(call.args[0], ast.Dict))
        extended = set()
        for node in ast.walk(adapt):
            if isinstance(node, ast.Call) and ast.unparse(node.func) == "target.update" and isinstance(node.args[0], ast.DictComp):
                for generator in node.args[0].generators:
                    extended |= {e.value for e in generator.iter.elts}
            if (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Subscript)
                    and ast.unparse(node.targets[0].value) == "target"):
                extended.add(node.targets[0].slice.value)
        self.assertEqual(len(base), 14)
        self.assertEqual(set(cmp.FILL_SHAPE["contrast"]), base | extended)
        self.assertEqual(len(cmp.FILL_SHAPE["contrast"]), 24)
        output = next(node.args[0] for node in ast.walk(adapt) if isinstance(node, ast.Call)
                      and isinstance(node.func, ast.Name) and node.func.id == "deepcopy" and node.args
                      and isinstance(node.args[0], ast.Dict) and "gamma" in dict_keys(node.args[0]))
        self.assertEqual(set(cmp.FILL_SHAPE["top"]), dict_keys(output))
        gamma = next(v for k, v in zip(output.keys, output.values) if isinstance(k, ast.Constant) and k.value == "gamma")
        added = {node.targets[0].slice.value for node in ast.walk(adapt) if isinstance(node, ast.Assign)
                 and isinstance(node.targets[0], ast.Subscript) and ast.unparse(node.targets[0].value) == "output['gamma']"}
        self.assertEqual(set(cmp.FILL_SHAPE["gamma"]), dict_keys(gamma) | added)
        source = self.source("joulewise/results_fill_adapter.py")
        self.assertIn('set(characterization) != {"funded", "run", "verdict"}', source)
        self.assertIn('for key in ("artifact_id", "file_sha256")', source)
        build = ast.parse(self.source("scripts/build_results_fill_input.py"))
        campaign = next(node.value for node in ast.walk(build) if isinstance(node, ast.Assign)
                        and ast.unparse(node.targets[0]) == "campaigns[pack]")
        self.assertEqual(set(cmp.FILL_SHAPE["campaign"]), dict_keys(campaign))

    def test_disclosure_shape(self):
        source = self.source("joulewise/b5_analysis/disclosures.py")
        tree = ast.parse(source)
        produce = function(tree, "produce_disclosures")
        result = next(node.value for node in ast.walk(produce) if isinstance(node, ast.Assign)
                      and ast.unparse(node.targets[0]) == "result")
        self.assertEqual(set(cmp.DISCLOSURE_SHAPE["top"]), dict_keys(result))
        windows = next(v for k, v in zip(result.keys, result.values) if k.value == "windows")
        self.assertEqual(set(cmp.DISCLOSURE_SHAPE["window"]), dict_keys(windows.value))
        cell = next(node.value for node in ast.walk(function(tree, "_cell_values")) if isinstance(node, ast.Return))
        self.assertEqual(set(cmp.DISCLOSURE_SHAPE["cell_values"]), dict_keys(cell))
        fixed = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                     and ast.unparse(node.targets[0]) == "FIXED_SENTENCES")
        self.assertEqual(set(cmp.FIXED_SENTENCE_WORDS), dict_keys(fixed) | {"conditionality", "config_binding"})
        tripwires = next(node.iter for node in ast.walk(function(tree, "_ruling_lines")) if isinstance(node, ast.For)
                         and isinstance(node.iter, ast.Tuple) and all(isinstance(e, ast.Constant) for e in node.iter.elts))
        self.assertEqual(cmp.TRIPWIRES, tuple(e.value for e in tripwires.elts))
        self.assertIn(f"SCREEN_BOUND_S = {cmp.SCREEN_BOUND_S!r}", source)
        codes = next(node.value for node in ast.walk(function(tree, "_monitor_lines")) if isinstance(node, ast.Assign)
                     and ast.unparse(node.targets[0]) == "battery_codes")
        self.assertEqual(cmp.BATTERY_CODES, tuple(e.value for e in codes.elts))
        triggers = next(node.value for node in ast.walk(function(tree, "_trigger_values")) if isinstance(node, ast.Assign)
                        and ast.unparse(node.targets[0]) == "result")
        self.assertEqual(set(cmp.TRIGGER_KEYS), dict_keys(triggers))
        self.assertIn('dropped_counts["status"]=', source)
        self.assertIn('dropped_counts["desk_cap"]=', source)
        self.assertEqual(cmp.CORPUS_DROPS, ("status", "desk_cap"))

    def test_sensitivity_shape(self):
        tree = ast.parse(self.source("joulewise/b5_analysis/sensitivity.py"))
        record = next(node.value for node in ast.walk(function(tree, "sensitivity_pass")) if isinstance(node, ast.Assign)
                      and ast.unparse(node.targets[0]) == "record")
        self.assertEqual(set(cmp.SENSITIVITY_SHAPE["top"]), dict_keys(record))
        for name, key in (("_reported_values", "reported_values"), ("_compose_floor", "floor_values"),
                          ("_contrast_values", "contrast_values")):
            returned = [node.value for node in ast.walk(function(tree, name)) if isinstance(node, ast.Return)
                        and isinstance(node.value, ast.Dict)][-1]
            self.assertEqual(list(cmp.SENSITIVITY_SHAPE[key]), [k.value for k in returned.keys], name)
        bracket = ast.parse(self.source("joulewise/b5_analysis/bracket.py"))
        bmax = next(node for node in ast.walk(bracket) if isinstance(node, ast.ClassDef) and node.name == "BMax")
        self.assertEqual(cmp.SENSITIVITY_SHAPE["b_max"], tuple(n.target.id for n in bmax.body if isinstance(n, ast.AnnAssign)))

    def test_closeout_census(self):
        source = self.source("joulewise/dominance_closeout.py")
        self.assertIn("closeout.independent_ratios: must contain exactly eight records", source)
        self.assertIn("census must be 4 absolute + ", source)
        self.assertIn("closeout.comparative_common_mode_ratios: must contain exactly ", source)
        self.assertIn('"four records"', source)
        floors = len(cmp.load_registry().tables["floor"])
        self.assertEqual((floors * len(cmp.CLOSEOUT_RATIOS["independent"]), floors), (8, 4))
        # The closeout's exact top keys include branch: the dominance_branch line always prints.
        self.assertIn('"branch"', source[source.index("_CLOSEOUT_TOP_KEYS"):source.index("_SOURCE_KEYS")])


def section(target):
    """The disclosure section an append writes to: result["cells"], result["window_lines"][pack], result[section]."""
    keys = []
    while isinstance(target, ast.Subscript):
        keys.append(target.slice)
        target = target.value
    return (keys[-1].value if isinstance(keys[-1], ast.Constant) else "*") if keys else None


# The producer loops whose multiplicity the registry fixes (each registered window, floor window, projection cell,
# extraction cell, contrast, fixed sentence, ratio group, sensitivity row, tripwire key, kept-units group); a line
# printed in any other loop or under any condition is conditional.
REGISTERED_LOOPS = {"PACK_ORDER", "PACK_ORDER[:2]", "primary_observations.items()", "FIXED_SENTENCES.items()",
                    "sorted(PACK_ORDER, key=lambda p: windows[p].record.entry.t0_epoch_s)",
                    "('independent_ratios', 'comparative_common_mode_ratios')",
                    "(('reported_cells', 'sensitivity_reported'), ('floor_cells', 'sensitivity_floor'), "
                    "('contrasts', 'sensitivity_contrast'))", "projections[pack]['cells']",
                    "extraction_reports[pack]['cells']", "closeout.get(group, [])", "sensitivity[name]",
                    "('excluded_reference_in_screen', 'kept_member_outside_verdict_membership')", "groups"}


def unconditional_lines(source):
    """(section, line word) of every line produce_disclosures prints on every path, per registered multiplicity."""
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}

    def stops(body):
        return any(isinstance(node, (ast.Continue, ast.Return, ast.Break)) for node in body)

    def emitted(statement):
        out = set()
        for call in ast.walk(statement):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "append" and call.args:
                arg, where = call.args[0], section(call.func.value)
                if (isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id == "_item"
                        and isinstance(arg.args[0], ast.Constant)):
                    out.add((where, arg.args[0].value))
        return out

    def must(body, seen):
        out = set()
        for statement in body:
            if isinstance(statement, ast.If):
                out |= must(statement.body, seen) & must(statement.orelse, seen)
                if stops(statement.body) != stops(statement.orelse):
                    break
            elif isinstance(statement, ast.For):
                if ast.unparse(statement.iter) in REGISTERED_LOOPS:
                    out |= must(statement.body, seen)
            elif isinstance(statement, (ast.With, ast.Try)):
                out |= must(statement.body, seen)
            elif isinstance(statement, (ast.Expr, ast.Assign)) and isinstance(statement.value, ast.Call):
                call = statement.value
                if isinstance(call.func, ast.Name) and call.func.id in functions and call.func.id not in seen:
                    out |= must(functions[call.func.id].body, seen | {call.func.id})
                else:
                    out |= emitted(statement)
            elif isinstance(statement, (ast.Return, ast.Continue, ast.Break)):
                break
        return out
    return must(functions["produce_disclosures"].body, frozenset())


def table_words(table):
    """(section, line word) of every disclosure line the table expects (any condition)."""
    words = set()
    for entry in table:
        for locator in entry["l9"]:
            for label, path, _ in (locator[1] if locator[0] == "any" else (locator,)):
                if label != "disclosure" or not path:
                    continue
                selector = next((step for step in path if isinstance(step, dict)), None)
                if selector and "line" in selector:
                    words.add((path[0], selector["line"]))
    return words


class TableTests(GateCase):
    """A1: one table, a function of registered inputs, printed (structure only), containing every unconditional
    producer line kind and its nested keys."""
    def test_unconditional_producer_line_kinds_are_in_the_table(self):
        source = producer("joulewise/b5_analysis/disclosures.py")
        if source is None:
            self.skipTest("origin/main is not available in this clone")
        printed = unconditional_lines(source)
        # Printed through a variable word (the sensitivity rows' and the fixed sentences' loops), pinned above.
        printed |= {("block_lines", "sensitivity_reported"), ("block_lines", "sensitivity_floor"),
                    ("block_lines", "sensitivity_contrast")}
        printed |= {("fixed_sentences", word) for word in cmp.FIXED_SENTENCE_WORDS}
        printed = {(where, word) for star, word in printed for where in
                   (("cells", "floors", "contrasts") if star == "*" else (star,))}
        words = table_words(cmp.expected_checks(cmp.load_registry()))
        self.assertEqual(printed - words, set())
        self.assertGreaterEqual(len(printed), 45)
        # The table's further lines, each printed under a registered condition (reported cell computed, floor
        # computed, kept n), the D-165 closeout's branch (an exact closeout key), the window index's attempts.
        self.assertEqual(words - printed, {("cells", "cross_window"), ("floors", "floor_composition"),
                                           ("fixed_sentences", "floor_drift_ownership"), ("fixed_sentences", "gross_energy"),
                                           ("block_lines", "dominance_branch"), ("block_lines", "attempt_count")})

    def test_unconditional_keys_of_each_line_are_required(self):
        source = producer("joulewise/b5_analysis/disclosures.py")
        if source is None:
            self.skipTest("origin/main is not available in this clone")
        required, selectors = {}, {}
        for entry in cmp.expected_checks(cmp.load_registry()):
            for locator in entry["l9"]:
                if locator[0] == "disclosure" and locator[1] and isinstance(locator[1][-1], dict) \
                        and "line" in locator[1][-1]:
                    word = locator[1][-1]["line"]
                    required.setdefault(word, set()).update(key[0] for key in locator[2])
                    selectors.setdefault(word, set()).update(k for k in locator[1][-1] if isinstance(k, str))
        literal = {}
        for call in ast.walk(ast.parse(source)):
            if (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "_item"
                    and isinstance(call.args[0], ast.Constant)):
                literal.setdefault(call.args[0].value, []).append({k.arg for k in call.keywords if k.arg})
        for word, keys in required.items():
            with self.subTest(word):
                # Every literal keyword each _item call of the word writes is required, or names the line (its
                # selector's identity fields). Keys written through ** are the comparator's LINE_KEYS (RC-CMP-8).
                written = set.intersection(*literal[word]) if word in literal else set()
                self.assertEqual(written - keys - selectors[word], set(), word)
        self.assertGreaterEqual(len(required), 45)

    def test_table_is_a_function_of_registered_inputs(self):
        registry = cmp.load_registry()
        first, second = cmp.expected_checks(registry), cmp.expected_checks(cmp.Registry())
        self.assertEqual(first, second)
        self.assertEqual(len({entry["check"] for entry in first}), len(first))
        # Its only parameter is the registry; the walk takes no output universe (no L9 or recompute key).
        self.assertEqual(cmp.expected_checks.__code__.co_varnames[:cmp.expected_checks.__code__.co_argcount], ("registry",))
        self.assertEqual(len(cmp.REGISTERED_SOURCES), 10)

    def test_table_lists_each_registered_item_at_its_multiplicity(self):
        table = cmp.expected_checks(cmp.load_registry())
        counts = {}
        for entry in table:
            counts[entry["kind"]] = counts.get(entry["kind"], 0) + 1
        self.assertEqual(counts, {
            "fill_document": 1, "fill_campaign": 2, "verdicts_document": 1, "kept_units_record": 3,
            "disclosure_document": 1, "disclosure_window": 3, "window_line": 3 * (21 + 2), "block_line": 3 + 2,
            "fixed_sentence": 13, "sensitivity_record": 1, "sensitivity_bmax": 1, "sensitivity_window": 3,
            "sensitivity_reported": 2 + 4 * 2, "projection_cell": 6, "cell_line": 4 * 5, "sensitivity_floor": 4,
            "aggregate_cell": 4, "ratio": 12, "dominance_branch": 1, "extraction_cell": 12, "floor_line": 12 + 8,
            "extraction_floor": 8, "bracket": 4, "contrast": 2, "contrast_floor_arm_gate": 4,
            "contrast_floor_resolution": 4, "loo_row": 20, "contrast_line": 2 * 10, "sensitivity_contrast": 2})
        checks = {entry["check"]: entry for entry in table}
        fill = next(loc for loc in checks[f"contrast/{DECODE}"]["l9"] if loc[0] == "fill")
        for key in (("estimate",), ("decision_interval", "lower"), ("floor", "claim_floor_rule"),
                    ("conditions", "difference_orientation"), ("claim_evaluation", "outcome"), ("floor", "arm_gates")):
            self.assertIn(key, fill[2])
        self.assertIn(("p42", "df-ph-prefill-p42-qwen3-1p7b"),
                      [loc[0] for loc in checks["extraction/alpha/d117-df-ph-prefill-p42-qwen3-1p7b-absolute"]["recompute"]])

    def test_structure_is_printed_without_values(self):
        out = self.exit_code(CODED)[2]
        structure = out["expected_checks"]
        self.assertEqual(structure["registered_sources"], list(cmp.REGISTERED_SOURCES))
        self.assertEqual(sum(structure["families"].values()), len(structure["checks"]))
        # Structure only: every leaf of the checks is a word (names, documents, condition kinds), never a value.
        leaves = [value for check in structure["checks"] for value in check.values()]
        self.assertTrue(all(value is None or isinstance(value, str) or isinstance(value, list)
                            and all(isinstance(v, str) for v in value) for value in leaves))
        rows = [r for r in out["comparisons"] if r["key"].startswith("expected/")]
        self.assertTrue(rows and all(r["verdict"] == "AGREE" for r in rows))

    def test_every_compared_leaf_lies_inside_an_expected_check(self):
        out = self.shipped()
        self.assertEqual(out["coverage"]["unbound"], [])
        # Counterfactual: no claim at all, so every compared leaf is outside the table and refuses (not_in_table).
        with mock.patch.object(cmp, "compare_expected", lambda c, custody, ours: []):
            reasons = {u["reason"] for u in self.shipped()["coverage"]["unbound"]}
        self.assertEqual(reasons, {"not_in_table"})


def l9_name(case, label):
    pattern, how = cmp.check_doc(label)
    names = [name for name in case.files if re.fullmatch(pattern, name)]
    if how == "sensitivity":
        names = [name for name in names if case.files[name].get("label") == "sensitivity"]
    return names[0] if names else None


def delete(root, path):
    """Delete the item at a table path (a selector path); True when it was there."""
    item, at = cmp.resolve(root, path)
    if item is cmp.MISSING or item is cmp.DUPLICATE or not at:
        return False
    parent = root
    for step in at[:-1]:
        parent = parent[step]
    del parent[at[-1]]
    return True


def delete_l9(case, locator):
    choices = locator[1] if locator[0] == "any" else (locator,)
    for label, path, _ in choices:
        name = l9_name(case, label)
        if name is None:
            continue
        if not path:
            case.files.pop(name)
            return True
        if delete(case.files[name], path):
            return True
    return False


def delete_recompute(case, path):
    return delete(case.ours, path)


class GenericDeletionTests(GateCase):
    """A5: every entry of the table, its item deleted from L9's side alone (every copy, and each copy alone), from
    the recompute's side alone and from both: never exit 0. Base: the producer-shaped window with NEG-8 lines,
    references and a widened sensitivity record."""
    def base(self):
        self.setUp()
        with_neg8(self)
        with_references(self)
        with_sensitivity(self, True)

    def outcome(self):
        try:
            return self.exit_code(CODED)[0]
        except cmp.Refusal:
            return 2

    def active(self):
        self.base()
        out = self.exit_code(CODED)[2]
        agreeing = {r["key"][len("expected/"):] for r in out["comparisons"]
                    if r["key"].startswith("expected/") and r["verdict"] == "AGREE"}
        return [entry for entry in cmp.expected_checks(cmp.load_registry()) if entry["check"] in agreeing]

    def assert_never_zero(self, kinds):
        entries = [entry for entry in self.active() if entry["kind"] in kinds]
        self.assertTrue(entries)
        for entry in entries:
            cases = {"l9": [entry["l9"]], "recompute": [()], "both": [entry["l9"]]}
            if len(entry["l9"]) > 1:
                cases.update({f"l9[{i}]": [(locator,)] for i, locator in enumerate(entry["l9"])})
            for side, (locators,) in cases.items():
                with self.subTest(check=entry["check"], side=side):
                    self.base()
                    if side != "recompute":
                        self.assertTrue(all([delete_l9(self, locator) for locator in locators]), side)
                    if side in ("recompute", "both"):
                        self.assertTrue(all([delete_recompute(self, path) for path, _ in entry["recompute"]]), side)
                    self.assertNotEqual(self.outcome(), 0)

    def test_documents_windows_and_records(self):
        self.assert_never_zero(("fill_document", "fill_campaign", "verdicts_document", "kept_units_record",
                                "disclosure_document", "disclosure_window", "sensitivity_record", "bracket"))

    def test_window_block_and_fixed_lines(self):
        self.assert_never_zero(("window_line", "block_line", "fixed_sentence", "dominance_branch"))

    def test_sensitivity_rows(self):
        self.assert_never_zero(("sensitivity_bmax", "sensitivity_window", "sensitivity_reported", "sensitivity_floor",
                                "sensitivity_contrast"))

    def test_cells_floors_and_ratios(self):
        self.assert_never_zero(("projection_cell", "cell_line", "aggregate_cell", "ratio", "extraction_cell",
                                "floor_line", "extraction_floor"))

    def test_contrasts_floors_and_leave_one_out(self):
        self.assert_never_zero(("contrast", "contrast_floor_arm_gate", "contrast_floor_resolution", "loo_row",
                                "contrast_line"))

    def test_every_kind_is_exercised(self):
        kinds = {entry["kind"] for entry in self.active()}
        self.assertEqual(kinds, {entry["kind"] for entry in cmp.expected_checks(cmp.load_registry())})


# Opus probe_cmp8.py confirm: each single-output drop that exited 0 at 0d317afd4 (confirm.out there).
def line_drop(section, word, pack=None, index=0):
    def edit(case):
        record = case.files[DISCLOSURE]
        rows = record[section] if pack is None else record[section][pack]
        del rows[[i for i, row in enumerate(rows) if row["line"] == word][index]]
    return edit


def fill_contrast(case, cid=DECODE):
    return next(row for row in case.files[FILL]["gamma"]["contrasts"] if row["contrast_id"] == cid)


OPUS_DROPS = {
    "fill decode contrast row": lambda c: c.files[FILL]["gamma"]["contrasts"].remove(fill_contrast(c)),
    "fill contrasts emptied": lambda c: c.files[FILL]["gamma"]["contrasts"].clear(),
    "fill gamma": lambda c: c.files[FILL].pop("gamma"),
    "fill estimate": lambda c: fill_contrast(c).pop("estimate"),
    "fill decision_interval": lambda c: fill_contrast(c).pop("decision_interval"),
    "fill difference_orientation": lambda c: fill_contrast(c)["conditions"].pop("difference_orientation"),
    "fill claim_floor_rule": lambda c: fill_contrast(c)["floor"].pop("claim_floor_rule"),
    "fill floor": lambda c: fill_contrast(c).pop("floor"),
    "primary_contrast line": line_drop("contrasts", "primary_contrast"),
    "primary_contrast estimator/estimate": lambda c: c.files[DISCLOSURE]["contrasts"][
        find(c, "primary_contrast")[1]]["estimator"].pop("estimate"),
    "decision_floor line": line_drop("contrasts", "decision_floor"),
    "contrast_interval line": line_drop("contrasts", "contrast_interval"),
    "attribution_floor line": line_drop("cells", "attribution_floor"),
    "dominance_branch line": line_drop("block_lines", "dominance_branch"),
    "dominance_ratio line": line_drop("block_lines", "dominance_ratio"),
    "sensitivity_bmax line": line_drop("block_lines", "sensitivity_bmax"),
    "sensitivity_window line": line_drop("block_lines", "sensitivity_window"),
    "sensitivity_contrast line": line_drop("block_lines", "sensitivity_contrast"),
    "sensitivity_reported computed line": line_drop("block_lines", "sensitivity_reported"),
    "sensitivity copy contrasts emptied": lambda c: c.files[DISCLOSURE]["sensitivity"]["contrasts"].clear(),
    "sensitivity copy": lambda c: c.files[DISCLOSURE].pop("sensitivity"),
    "block_lines": lambda c: c.files[DISCLOSURE].pop("block_lines")}


def drop_contrast_everywhere(case, cid=DECODE):
    """Opus joint2: a registered contrast removed from every L9 output that prints it and from the recompute."""
    for rows in (case.files[VERDICTS]["contrasts"], case.files[FILL]["gamma"]["contrasts"]):
        rows[:] = [r for r in rows if r["contrast_id"] != cid]
    record = case.files[DISCLOSURE]
    record["contrasts"][:] = [r for r in record["contrasts"] if r.get("contrast_id") != cid and r.get("cell_id") != cid]
    for doc in (case.files[SENSITIVITY], record["sensitivity"]):
        doc["contrasts"][:] = [r for r in doc["contrasts"] if r["contrast_id"] != cid]
    record["block_lines"][:] = [r for r in record["block_lines"] if (r.get("record") or {}).get("contrast_id") != cid]
    for section in (case.ours["contrasts"], case.ours["descriptive"], case.ours["disclosures"]["battery_assist"],
                    case.ours["disclosures"]["sensitivity_bound"]["contrasts"]):
        section.pop(cid, None)


def drop_reported_everywhere(case):
    """Opus joint2: ALPHA's decode reported cell removed from every L9 output and from the recompute."""
    projection = case.files[PROJECTION]
    projection["cells"][:] = [r for r in projection["cells"] if r["cell_id"] != REPORTED]
    record = case.files[DISCLOSURE]
    record["cells"][:] = [r for r in record["cells"] if r.get("cell_id") != REPORTED]
    for doc in (case.files[SENSITIVITY], record["sensitivity"]):
        doc["reported_cells"][:] = [r for r in doc["reported_cells"] if r["cell_id"] != REPORTED]
    record["block_lines"][:] = [r for r in record["block_lines"] if (r.get("record") or {}).get("cell_id") != REPORTED]
    for section in (case.ours["reported_cells"], case.ours["disclosures"]["battery_assist"],
                    case.ours["disclosures"]["sensitivity_bound"]["reported_cells"]):
        section.pop(FAMILY, None)
    case.ours["disclosures"]["cross_window"].pop("Qwen3-1.7B-4bit/decode", None)


def drop_loo_everywhere(case):
    """Opus loo: both L9 copies of the decode contrast's rows and the recompute's dropped, status not_run, count 0."""
    for row in contrast_rows(case):
        row["loo"].update(rows=[], status="not_run")
    case.ours["contrasts"][DECODE]["loo"] = []
    lines, index = find(case, "loo_counts")
    lines[index]["count"] = 0


def old_loo_status(rows, blocks):
    """0d317afd4's loo_status: complete when the recompute printed rows, else not_run."""
    if not isinstance(rows, list) or blocks is None or len(blocks) > cmp.LOO_REQUIRED_MAX:
        return None
    return "complete" if rows else "not_run"


class OpusDropTests(GateCase):
    """A2: Opus's 22 single-output drops and the joint drops (decode contrast, ALPHA reported cell, loo rows)."""
    def outcome(self):
        try:
            return self.exit_code(CODED)[0]
        except cmp.Refusal:
            return 2

    def fresh(self, widened):
        self.setUp()
        with_neg8(self)
        with_references(self)
        with_sensitivity(self, widened)

    def test_each_single_output_drop_exits_non_zero(self):
        self.assertEqual(len(OPUS_DROPS), 22)
        for widened in (True, False):
            for label, edit in OPUS_DROPS.items():
                with self.subTest(label, widened=widened):
                    self.fresh(widened)
                    self.assertEqual(self.outcome(), 0)
                    edit(self)
                    self.assertNotEqual(self.outcome(), 0)

    def test_without_the_table_the_drops_pass(self):
        # Counterfactual in place: the walk switched off (no_table), each drop of a whole fill row or object and
        # each dropped line exits 0 as at 0d317afd4; a key dropped inside a present fill row still meets the
        # RC-CMP-8 gate (that is not one of Opus's drops).
        passing = []
        for label, edit in OPUS_DROPS.items():
            self.fresh(True)
            edit(self)
            with mock.patch.object(cmp, "compare_expected", no_table):
                if self.outcome() == 0:
                    passing.append(label)
        self.assertGreaterEqual(len(passing), 14, passing)

    def test_joint_drops_exit_non_zero(self):
        for label, edit in (("decode contrast", drop_contrast_everywhere), ("alpha decode reported cell",
                                                                           drop_reported_everywhere),
                            ("decode loo rows", drop_loo_everywhere)):
            for widened in (True, False):
                with self.subTest(label, widened=widened):
                    self.fresh(widened)
                    edit(self)
                    self.assertNotEqual(self.outcome(), 0)

    def test_joint_drops_passed_before_the_table(self):
        # Counterfactual: no table, and no RC-CMP-9 leave-one-out binding (the status row from the kept n and the
        # two row counts); each joint drop exits 0 again, as at 0d317afd4 (joint.out, loo.out there).
        for label, edit in (("decode contrast", drop_contrast_everywhere),
                            ("alpha decode reported cell", drop_reported_everywhere),
                            ("decode loo rows", drop_loo_everywhere)):
            with self.subTest(label):
                self.fresh(True)
                edit(self)
                # 0d317afd4's word, from the rows the recompute printed (compare_contrasts asks in contrast order).
                old = [old_loo_status(self.ours["contrasts"][cid]["loo"], cmp.load_registry().blocks[cid])
                       for cid in sorted(self.ours["contrasts"])]
                with mock.patch.object(cmp, "compare_expected", no_table), \
                        mock.patch.object(cmp, "loo_status", side_effect=old), \
                        mock.patch.object(cmp.Comparison, "numeric", numeric_off(cmp.Comparison.numeric,
                                                                                 "/loo/l9_rows", "/loo/recompute_rows")):
                    self.assertEqual(self.outcome(), 0)

    def test_loo_status_follows_the_kept_n(self):
        self.fresh(True)
        drop_loo_everywhere(self)
        code, _, out = self.exit_code(CODED)
        self.assertNotEqual(code, 0)
        row = next(r for r in out["comparisons"] if r["key"] == f"{DECODE}/loo_status")
        self.assertEqual((row["l9"], row["recompute"]), ("not_run", "complete"))


def rows_off(exact, *suffixes):
    def patched(self, family, key, l9, ours, raw=cmp.MISSING):
        return None if key.endswith(suffixes) else exact(self, family, key, l9, ours, raw)
    return patched


def numeric_off(numeric, *suffixes):
    def patched(self, family, key, l9, ours):
        return None if key.endswith(suffixes) else numeric(self, family, key, l9, ours)
    return patched


class RegisteredIdentityTests(GateCase):
    """A3 and A4: the floor source cells, the projection's p42 row and the identity relabels Opus found exiting 0
    (relabel_ids.out at 0d317afd4) bind to registered values."""
    def outcome(self):
        try:
            return self.exit_code(CODED)[0]
        except cmp.Refusal:
            return 2

    def test_floor_cell_ids_bind_to_the_registered_source_cells(self):
        prefill = ["d117-qwen3-1p7b-prefill-p2048-floor-v5", "d117-qwen3-8b-prefill-p2048-floor-v5"]
        cases = {
            "fill floor_source_cell_ids": lambda c: fill_contrast(c)["floor_source_cell_ids"].__setitem__(0, prefill[0]),
            "fill floor_row_ids": lambda c: fill_contrast(c)["floor"]["floor_row_ids"].reverse(),
            "verdict floor_row_ids": lambda c: contrast_rows(c)[0]["floor"].__setitem__("floor_row_ids", list(prefill)),
            "sensitivity record floor_cell_ids": lambda c: c.files[SENSITIVITY]["contrasts"][0]["floor_cell_ids"].reverse(),
            "sensitivity copy floor_cell_ids": lambda c: c.files[DISCLOSURE]["sensitivity"]["contrasts"][0][
                "floor_cell_ids"].reverse(),
            "sensitivity_contrast line floor_cell_ids": lambda c: c.files[DISCLOSURE]["block_lines"][
                find(c, "sensitivity_contrast")[1]]["record"]["floor_cell_ids"].reverse()}
        for label, edit in cases.items():
            with self.subTest(label):
                self.setUp()
                edit(self)
                self.assertNotEqual(self.outcome(), 0)
        self.setUp()
        out = self.shipped()
        self.assertEqual(out["coverage"]["leaves"]["fill:gamma/contrasts/*/floor_source_cell_ids/*"], "routing_id")
        self.assertEqual(out["coverage"]["leaves"]["disclosure:sensitivity/contrasts/*/floor_cell_ids/*"], "routing_id")

    def test_opus_identity_relabels_refuse_or_disagree(self):
        alpha = f"kept-units/{SHA}-alpha.json"
        cases = {
            "floors kept_units cell_id": lambda c: next(
                line for line in c.files[DISCLOSURE]["floors"] if line["line"] == "kept_units"
                and line["cell_id"] == test_comparator.ALPHA_CELLS["absolute"]).update(
                cell_id="d117-df-cmp-abba-ph-decode-qwen3-1p7b"),
            "kept-units pack": lambda c: c.files[alpha].update(pack="beta"),
            "kept unit cell_id": lambda c: next(iter(c.files[alpha]["cells"].values()))["kept"]["repeat"][0].update(
                cell_id="d117-df-cmp-abba-ph-decode-qwen3-1p7b"),
            "excluded block id": lambda c: contrast_rows(c)[0]["bundle_blocks"]["blocks"][0].update(
                block_id="d117-decode-contrast-b02"),
            "planned block ids": lambda c: contrast_rows(c)[0]["bundle_blocks"]["planned_block_ids"].reverse(),
            "transport group": lambda c: [row["floor"]["resolutions"][0].update(transport_group_id="tg-other")
                                          for row in contrast_rows(c)]}
        for label, edit in cases.items():
            with self.subTest(label):
                self.setUp()
                edit(self)
                self.assertNotEqual(self.outcome(), 0)
                # Counterfactual: 0d317afd4's composition (no table, none of these binding rows, the identity rule
                # for the fill's transport groups and block ids).
                with mock.patch.object(cmp, "compare_expected", no_table), \
                        mock.patch.object(cmp.Comparison, "exact", rows_off(
                            cmp.Comparison.exact, "/kept_units/pack", "/planned_block_ids", "/bundle_block_ids",
                            "/transport_group_id")), \
                        mock.patch.object(cmp, "verdict_block_ids", lambda row: ([], [])), \
                        mock.patch.object(cmp, "registered_block_ids", lambda registry, cid, mine: ([], [])), \
                        mock.patch.object(cmp, "COVERAGE", ((r"fill:gamma/contrasts/\*/(floor/resolutions/\*/"
                                                             r"transport_group_id|kept_block_ids/\*|"
                                                             r"(sampling/)?removed_block_ids/\*)", cmp.IDENTITY),)
                                          + cmp.COVERAGE):
                    if label == "kept unit cell_id":
                        continue
                    self.assertEqual(self.outcome(), 0)

    def test_fill_block_ids_bind_by_position(self):
        for label, edit in (("kept relabelled", lambda c: fill_contrast(c)["kept_block_ids"].__setitem__(
                                 0, "d117-decode-contrast-b01")),
                            ("removed relabelled", lambda c: fill_contrast(c)["removed_block_ids"].__setitem__(
                                 0, "d117-decode-contrast-b02")),
                            ("sampling removed relabelled", lambda c: fill_contrast(c)["sampling"]["removed_block_ids"]
                             .__setitem__(0, "d117-decode-contrast-b02")),
                            ("kept order", lambda c: fill_contrast(c)["kept_block_ids"].reverse()),
                            ("kept shortened", lambda c: fill_contrast(c)["kept_block_ids"].pop())):
            with self.subTest(label):
                self.setUp()
                edit(self)
                self.assertNotEqual(self.outcome(), 0)
        self.setUp()
        leaves = self.shipped()["coverage"]["leaves"]
        for path in ("kept_block_ids/*", "removed_block_ids/*", "sampling/removed_block_ids/*"):
            self.assertEqual(leaves["fill:gamma/contrasts/*/" + path], "routing_id")

    def test_list_positions_and_terms_are_required(self):
        cases = {
            "fill floor_source_cell_ids shortened": lambda c: fill_contrast(c)["floor_source_cell_ids"].pop(),
            "fill floor_row_ids shortened": lambda c: fill_contrast(c)["floor"]["floor_row_ids"].pop(),
            "fill resolution source emptied": lambda c: fill_contrast(c)["floor"]["resolutions"][1]["source_cell_ids"].pop(),
            "sensitivity copy floor_cell_ids shortened": lambda c: c.files[DISCLOSURE]["sensitivity"]["contrasts"][0][
                "floor_cell_ids"].pop(),
            "deterministic term dropped": lambda c: contrast_rows(c)[0]["deterministic_bounds"]["terms"].clear(),
            "deterministic term name dropped": lambda c: contrast_rows(c)[0]["deterministic_bounds"]["terms"][0].pop("name"),
            "battery count code dropped": lambda c: c.files[DISCLOSURE]["window_lines"]["alpha"][
                find(c, "battery_counts")[1]]["counts"].pop("battery.assist"),
            "corpus status drops dropped": lambda c: c.files[DISCLOSURE]["window_lines"]["alpha"][
                find(c, "corpus_counts")[1]]["drop_counts"].pop("status"),
            "trigger key dropped": lambda c: c.files[DISCLOSURE]["window_lines"]["alpha"][
                find(c, "erratum3_triggers")[1]]["values"].pop("doubling_count")}
        for label, edit in cases.items():
            with self.subTest(label):
                self.setUp()
                edit(self)
                self.assertNotEqual(self.outcome(), 0)
        # A window whose record has no bracket prints no trigger object (values null): no key is required.
        self.setUp()
        self.files[DISCLOSURE]["window_lines"]["alpha"][find(self, "erratum3_triggers")[1]]["values"] = None
        self.assertEqual(self.outcome(), 0)

    def test_projection_p42_row_is_unconditional(self):
        for label, edit in (("refused_cells dropped", lambda c: c.files[PROJECTION].pop("refused_cells")),
                            ("refused p42 relabelled", lambda c: c.files[PROJECTION]["refused_cells"][0].update(
                                cell_id="d117-reported-mean-ph-decode-qwen3-1p7b")),
                            ("refused_cells an object", lambda c: c.files[PROJECTION].update(
                                refused_cells={"cell_id": "d117-reported-mean-ph-prefill-p42-qwen3-1p7b"}))):
            with self.subTest(label):
                self.setUp()
                edit(self)
                self.assertNotEqual(self.outcome(), 0)
        self.setUp()
        self.files[PROJECTION].pop("refused_cells")
        out = self.shipped()
        row = next(r for r in out["comparisons"] if r["key"] == "alpha/projection/p42")
        self.assertEqual((row["l9"], row["verdict"]), (None, "DISAGREE"))


class FableFindingTests(GateCase):
    """A4b: Fable's F2 (arm gates and resolutions), F3 (13 line words), F4 (projection p42) and F5 (conditional keys
    under their status word) probes (probes.out S1 at 0d317afd4: each exit 0)."""
    def outcome(self):
        try:
            return self.exit_code(CODED)[0]
        except cmp.Refusal:
            return 2

    def test_f2_arm_gates_and_resolutions_dropped(self):
        for key in ("arm_gates", "resolutions"):
            for copies in ((0, 1), (1,)):
                with self.subTest(key, copies=copies):
                    self.setUp()
                    with_sensitivity(self, True)
                    for cid in (DECODE, PREFILL):
                        rows = contrast_rows(self, cid)
                        for index in copies:
                            rows[index]["floor"].pop(key)
                    self.assertNotEqual(self.outcome(), 0)
                    if copies == (0, 1):
                        out = self.exit_code(CODED)[2]
                        rows_built = [r for r in out.get("comparisons", ())
                                      if r["key"].startswith(f"contrast/{DECODE}/{'arm' if key == 'arm_gates' else 'resolution'}/")]
                        self.assertTrue(rows_built)

    def test_f3_each_line_word_dropped(self):
        words = {"contrasts": ("primary_contrast", "contrast_interval", "decision_floor"),
                 "cells": ("attribution_floor",), "floors": ("kept_units",),
                 "block_lines": ("dominance_branch", "dominance_ratio", "sensitivity_bmax", "sensitivity_window",
                                 "sensitivity_reported", "sensitivity_floor", "sensitivity_contrast",
                                 "sensitivity_boundary")}
        self.assertEqual(sum(len(w) for w in words.values()), 13)
        for section, names in words.items():
            for word in names:
                with self.subTest(word):
                    self.setUp()
                    with_sensitivity(self, True)
                    record = self.files[DISCLOSURE]
                    record[section] = [row for row in record[section] if row["line"] != word]
                    self.assertNotEqual(self.outcome(), 0)

    def test_f5_conditional_keys_follow_the_status_word(self):
        self.setUp()
        lines, index = find(self, "dominance_ratio")
        for key in ("ratio", "numerator_j", "denominator_j"):
            with self.subTest(key):
                self.setUp()
                lines, index = find(self, "dominance_ratio")
                lines[index].pop(key)
                self.refused(f"required_key_absent:disclosure:block_lines/dominance_ratio/complete/{key}")
        self.setUp()
        lines, index = find(self, "battery_assist_contrast")
        lines[index].pop("t_star")
        self.refused("required_key_absent:disclosure:contrasts/battery_assist_contrast/computed/t_star")
        # Control: a refused ratio and a not-computable assist contrast carry none of them and pass the gate.
        cmp.gate_lines({"block_lines": [test_comparator.item("dominance_ratio", True, "x absolute: R refused",
                                                             cell_id=FLOOR_CELLS["alpha"], component="absolute", n=9,
                                                             status="refused")],
                        "contrasts": [test_comparator.item("battery_assist_contrast", True, "x", contrast_id=DECODE,
                                                           status="not_computable", n=0, assist_quads=9,
                                                           assist_members={})]})


class OverRefusalTests(GateCase):
    """A6: the producer-shaped windows exit 0 (with every NEG-8 line, the reference members and the computed
    sensitivity, widened and unwidened), and a conditional item is expected only under its condition."""
    def test_producer_shaped_windows_pass(self):
        for widened in (True, False):
            with self.subTest(widened=widened):
                self.setUp()
                with_neg8(self)
                with_references(self)
                with_sensitivity(self, widened)
                code, err, out = self.exit_code(CODED)
                self.assertEqual((code, err), (0, ""))
                self.assertFalse([r for r in out["comparisons"] if r["verdict"] != "AGREE"])

    def test_conditional_items_follow_their_condition(self):
        registry = cmp.load_registry()
        table = cmp.expected_checks(registry)
        custody = cmp.Custody(self.custody(), [], registry)
        expected, l9, own, missing = cmp.expected_items(custody, self.ours, table, {})
        conditional = [entry["check"] for entry in table if entry["condition"] is not None]
        # The base: every reported and floor cell computed, nine blocks kept per contrast (b01 left out), ratios.
        self.assertEqual(sorted(check for check in conditional if check not in expected),
                         sorted([f"contrast/{cid}/loo/{blocks[0]}" for cid, blocks in test_comparator.BLOCKS.items()]
                                + [f"sensitivity/reported_cells/{pack}/{cid}/refused" for pack in ("alpha", "beta")
                                   for phase, (cid, _) in test_comparator.reported_cells(pack).items()
                                   if phase != "prefill-p42"]))
        self.assertEqual(set(expected), set(l9) - {k for k in l9 if k.startswith("unexpected/")})
        self.assertEqual(set(expected), set(own))
