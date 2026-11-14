"""scripts/b6_r3_table.py: the §17-R3 table regenerates from code with no UNSTATED row. Synthetic and code only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "b6_r3_table.py"
KEYS = REPO / "configs" / "b6" / "recompute" / "production_comparison_keys.json"
sys.path.insert(0, str(REPO / "scripts"))
import b6_r3_table  # noqa: E402


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, cwd=REPO, timeout=120)


class R3TableTests(unittest.TestCase):
    def test_current_tree_has_no_unstated_row_and_covers_every_key(self):
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        text = result.stdout.decode()
        self.assertNotIn("UNSTATED |", text)
        self.assertIn("UNSTATED groups: 0.", text)
        keys = json.loads(KEYS.read_text(encoding="utf-8"))
        total = len(keys["block_quantity_keys"]) + sum(len(v) for v in keys["session_quantity_keys"].values())
        self.assertIn("Keys covered: {} of {};".format(total, total), text)
        _, groups = b6_r3_table.build({k: REPO / v for k, v in b6_r3_table.DEFAULTS.items()})
        names = {name for _, name in groups}
        for pack, rows in keys["session_quantity_keys"].items():
            for key in rows:
                self.assertIn(b6_r3_table.generalize(key), names, key)
        for key in keys["block_quantity_keys"]:
            self.assertIn(b6_r3_table.generalize(b6_r3_table.split_block(key)[0]), names, key)
        for name in b6_r3_table.DEFAULTS.values():
            self.assertRegex(text, r"`" + name + r"` `[0-9a-f]{64}`")

    def test_formerly_unstated_groups_resolve_from_code(self):
        text = run().stdout.decode()
        rows = {line.split("|")[3].strip(): line for line in text.splitlines() if line.startswith("| ")}
        self.assertIn('"single implementation; not independently recomputed" (§17-R8)',
                      rows["`lines/whole_machine/<model>/<phase>/mean_j`"])
        self.assertIn("`single-source` (RL-99 item 1)", rows["`dominance/<model>/<phase>/<mode>/R`"])
        for name in ("`dominance/branch`", "`lines/waited_runs/<phase>/dbar_j`", "`contrast/<phase>/t`",
                     "`cross_session/<model>/<phase>/F_j`"):
            self.assertEqual(rows[name].split("|")[9].strip(), b6_r3_table.LABEL_ONE, name)
        # RL-103: gate rows carry the gate's bar and the check family in Source.
        cells = rows["`contrast/<phase>/s_d_j`"].split("|")
        self.assertEqual(cells[9].strip(), b6_r3_table.LABEL_GATE)
        self.assertIn("5e-06 absolute", cells[8])
        self.assertIn("check family `engine`", cells[10])
        cells = rows["`contrast/<phase>/outcome`"].split("|")
        self.assertEqual(cells[9].strip(), b6_r3_table.LABEL_GATE_WORD)
        self.assertIn("exact", cells[8])
        # RL-102 item 4: block-scope rows.
        self.assertEqual(rows["`summary/ALPHA/reported/<model>/<phase>/mean_j`"].split("|")[9].strip(),
                         b6_r3_table.LABEL_BLOCK)

    # RL-101 item 3, RL-102 item 4, RL-103, RL-104: exact ruled strings, written as literals (not the generator's constants).
    RULED_ONE = "not independently recomputed"
    RULED_SINGLE = "`single-source` (RL-99 item 1)"
    RULED_BLOCK = "§10-§11 arithmetic computed and compared; session inputs as labelled at session scope"
    # RL-114 (amends RL-103 and RL-110), character for character.
    RULED_GATE = ("computed and compared in the option (c) gate when the session's NEG-8 verdict is not `undefined` and "
                  "the twin returns an estimate, otherwise not independently recomputed; not an S-13 table row")
    # RL-133 §1a (amends RL-114 for the word, `p` and `holm_p`), character for character.
    RULED_GATE_WORD = ("computed and compared in the option (c) gate when the session's NEG-8 verdict is not "
                       "`undefined` and either the twin refuses or the contrast has five or more quads; with two to "
                       "four quads the gate requires only that the word is `not_estimable`; with an undefined verdict "
                       "the gate requires only that the word is `not_resolvable` or `not_estimable`; otherwise not "
                       "independently recomputed; not an S-13 table row")
    RULED_P = ("computed and compared (decision 6 (a)) when the session's NEG-8 verdict is not `undefined`, the twin "
               "returns an estimate and the contrast has five or more quads; with two to four quads the gate requires "
               "only that the value is 1.0; otherwise not independently recomputed")
    RULED_HOLM = ("computed and compared (decision 6 (a)) when the session's NEG-8 verdict is not `undefined`, the twin "
                  "returns an estimate and the contrast has five or more quads, with a family member below five quads "
                  "counted at p = 1.0 on both sides; with two to four quads the gate requires only that the value is "
                  "1.0; otherwise not independently recomputed")
    RULED_CONTRAST = ("computed and compared (decision 6 (a)) when the session's NEG-8 verdict is not `undefined` and "
                      "the twin returns an estimate, otherwise not independently recomputed")
    # RL-110, character for character (unchanged by RL-114).
    RULED_NEG8 = ("computed and compared (decision 6 (a)) when the session's NEG-8 verdict is not `undefined`, "
                  "otherwise not independently recomputed")
    RULED_COPIED = '"copied from the harvest or acceptance record, bound by digest, not recomputed" (decision 6 (b))'

    def labels(self):
        text = run().stdout.decode()
        rows = {line.split("|")[3].strip(): line.split("|")[9].strip()
                for line in text.splitlines() if line.startswith("| ") and len(line.split("|")) > 10}
        return text, rows

    def test_rulings_pinned_as_literals(self):
        text, rows = self.labels()
        # RL-101 item 3: one ALPHA/BETA row per section 9.5 family, scaled allowance and single step: one producer, no
        # second side, so NOT single-source.
        for name in ("`lines/load_sensitivity/<model>/<phase>/mean_j`", "`lines/battery_assist/<model>/<phase>/mean_j`",
                     "`lines/waited_runs/<model>/<phase>/mean_j`",
                     "`lines/outside_processor_alternative/<model>/<phase>/mean_j`",
                     "`lines/scaled_allowance/<model>/<phase>/gate_j`",
                     "`lines/single_step_reconstruction/<model>/<phase>/mean_j`"):
            self.assertEqual(rows[name], self.RULED_ONE, name)
        # RL-101 items 1 and 2: a copy or an estimator output of the Block 5 estimators prints single-source.
        for name in ("`reported/<model>/<phase>/mean_j`", "`floor/<model>/<phase>/<mode>/floor_j`",
                     "`dominance/<model>/<phase>/<mode>/R`", "`dominance/<model>/<phase>/<mode>/R_cm`"):
            self.assertEqual(rows[name], self.RULED_SINGLE, name)
        # RL-102 item 4, RL-103.
        self.assertEqual(rows["`summary/ALPHA/reported/<model>/<phase>/mean_j`"], self.RULED_BLOCK)
        # RL-114: the three gate numbers, the gate word, and (below) the five S-13 contrast fields.
        for field in ("s_d_j", "decision_lower_j", "decision_upper_j"):
            self.assertEqual(rows["`contrast/<phase>/" + field + "`"], self.RULED_GATE, field)
        self.assertEqual(rows["`contrast/<phase>/outcome`"], self.RULED_GATE_WORD)
        self.assertEqual(sorted(k for k, v in rows.items() if v == self.RULED_GATE),
                         ["`contrast/<phase>/decision_lower_j`", "`contrast/<phase>/decision_upper_j`",
                          "`contrast/<phase>/s_d_j`"])
        self.assertEqual([k for k, v in rows.items() if v == self.RULED_GATE_WORD], ["`contrast/<phase>/outcome`"])
        self.assertEqual(sorted(k for k, v in rows.items() if v == self.RULED_CONTRAST),
                         sorted("`contrast/<phase>/" + f + "`" for f in ("n", "dbar_j", "D_j")))
        # RL-133 §1a: `p` and `holm_p` carry the registered minimum.
        self.assertEqual([k for k, v in rows.items() if v == self.RULED_P], ["`contrast/<phase>/p`"])
        self.assertEqual([k for k, v in rows.items() if v == self.RULED_HOLM], ["`contrast/<phase>/holm_p`"])
        # RL-110: every neg8/* key; RL-114: the five S-13 contrast fields.
        for name in ("`neg8/verdict`", "`neg8/bound_j`", "`neg8/allowance_j`"):
            self.assertEqual(rows[name], self.RULED_NEG8, name)
        for field in ("n", "dbar_j", "D_j"):
            self.assertEqual(rows["`contrast/<phase>/" + field + "`"], self.RULED_CONTRAST, field)
        self.assertEqual(sum(1 for k, v in rows.items() if k.startswith("`neg8/")), 3)
        for family in ("monitor_cost", "arm_host", "battery_phase", "subject_temperature", "reference_history",
                       "attempt_history", "g10_history", "block5_codes_carried"):
            self.assertEqual(rows["`" + family + "`"], self.RULED_COPIED, family)
        # The whole count block.
        expected = "\n".join([
            "Keys by label:", "",
            '- "single implementation; not independently recomputed" (§17-R8): 24',
            "- `single-source` (RL-99 item 1): 100",
            "- computed and compared (decision 6 (a)): 3",
            "- " + self.RULED_CONTRAST + ": 6",
            "- " + self.RULED_NEG8 + ": 9",
            "- " + self.RULED_HOLM + ": 2",
            "- " + self.RULED_P + ": 2",
            "- " + self.RULED_GATE_WORD + ": 2",
            "- " + self.RULED_GATE + ": 6",
            "- not independently recomputed: 183",
            "- " + self.RULED_BLOCK + ": 338", ""])
        self.assertTrue(text.endswith(expected), text[-900:])

    def _mutated(self, old, new):
        source = (REPO / b6_r3_table.DEFAULTS["check"]).read_text(encoding="utf-8")
        self.assertEqual(source.count(old), 1, old)
        with tempfile.TemporaryDirectory(prefix="b6-r3-table-") as tmp:
            path = Path(tmp) / "check.py"
            path.write_text(source.replace(old, new), encoding="utf-8")
            return b6_r3_table.read_check(path)

    def _classify(self, check, key):
        paths = {k: REPO / v for k, v in b6_r3_table.DEFAULTS.items()}
        return b6_r3_table.classify_session(key, "GAMMA", check, b6_r3_table.read_recompute(paths["recompute"]))

    def test_outcome_is_unstated_unless_refusal_and_word_checks_are_both_present(self):
        key = "contrast/decode/outcome"
        whole = self._classify(b6_r3_table.read_check(REPO / b6_r3_table.DEFAULTS["check"]), key)
        self.assertEqual(whole[1], self.RULED_GATE_WORD)
        word = 'check("engine_word", cid, original["outcome"], engine.outcome(v, floors[cid], ruled[cid]), 0)'
        refusal = 'check("engine_refusal", cid, original["outcome"], "not_estimable", 0)'
        for old in (word, refusal):
            result = self._classify(self._mutated(old, "pass"), key)
            self.assertEqual(result[:2], (b6_r3_table.UNSTATED, b6_r3_table.UNSTATED), old)

    def test_rl133_minimum_labels_need_the_below_minimum_guard_in_check_block(self):
        """RL-133 §1a: `p`, `holm_p` and the word carry the two-to-four-quads clause only while check_block guards a
        short contrast (`engine_below_minimum`). Without the guard those rows are UNSTATED; the other fields are not."""
        check = b6_r3_table.read_check(REPO / b6_r3_table.DEFAULTS["check"])
        self.assertTrue(check["below_minimum"])
        mutated = self._mutated('check("engine_below_minimum", cid, guarded, True, 0)', "pass")
        self.assertFalse(mutated["below_minimum"])
        for key in ("contrast/decode/p", "contrast/decode/holm_p", "contrast/decode/outcome"):
            result = self._classify(mutated, key)
            self.assertEqual(result[:2], (b6_r3_table.UNSTATED, b6_r3_table.UNSTATED), key)
            self.assertIn("engine_below_minimum", result[2])
        self.assertEqual(self._classify(mutated, "contrast/decode/n")[1], self.RULED_CONTRAST)
        self.assertEqual(self._classify(check, "contrast/decode/p")[1], self.RULED_P)
        self.assertEqual(self._classify(check, "contrast/decode/holm_p")[1], self.RULED_HOLM)

    def test_rl114_clause_needs_the_undefined_screen_branch_in_check_block(self):
        """RL-114: the 'verdict is not `undefined`' clause is printed only while check_block skips the twin and guards
        the word for such a session. Without that branch the clause-bearing rows are UNSTATED; one-producer rows are not."""
        check = b6_r3_table.read_check(REPO / b6_r3_table.DEFAULTS["check"])
        self.assertIsNotNone(check["screen"])
        guard = 'check("engine_screen_undefined", cid, guarded, True, 0)'
        branch = 'if s.neg8["verdict"] == "undefined":\n                # RL-114'
        for old, new in ((guard, "pass"), (branch, 'if False:\n                # RL-114'),
                         ('"not_resolvable", "not_estimable"', '"not_estimable",')):
            mutated = self._mutated(old, new)
            self.assertIsNone(mutated["screen"], old)
            for key in ("contrast/decode/n", "contrast/decode/D_j", "contrast/decode/s_d_j",
                        "contrast/decode/decision_lower_j", "contrast/decode/outcome"):
                result = self._classify(mutated, key)
                self.assertEqual(result[:2], (b6_r3_table.UNSTATED, b6_r3_table.UNSTATED), (old, key))
                self.assertIn("engine_screen_undefined", result[2])
            self.assertEqual(self._classify(mutated, "contrast/decode/t")[1], self.RULED_ONE, old)
        # The guard's line is named in the outcome row's Source column.
        result = self._classify(check, "contrast/decode/outcome")
        self.assertIn("`engine_screen_undefined` CHK:{}".format(check["screen"]["guard"]), result[2])

    def test_bar_passed_by_keyword_is_honoured_or_refused(self):
        old = 'check("engine", cid + "/" + key, original[key], expected)'
        result = self._classify(self._mutated(old, 'check("engine", cid + "/" + key, original[key], expected, bar=0.5)'),
                                "contrast/decode/s_d_j")
        self.assertEqual(result[3], "gate: 0.5 absolute, unrounded (CHK `check` bar)")
        with self.assertRaises(SystemExit):
            self._mutated(old, 'check("engine", cid + "/" + key, original[key], expected, bar=BAR)')

    def test_copied_families_are_the_eight_and_not_comparison_keys(self):
        """RL-104 check 1: exactly the eight decision 6 (b) families, none a key or key prefix."""
        self.assertEqual(b6_r3_table.COPIED_FAMILIES, (
            "monitor_cost", "arm_host", "battery_phase", "subject_temperature", "reference_history",
            "attempt_history", "g10_history", "block5_codes_carried"))
        keys = json.loads(KEYS.read_text(encoding="utf-8"))
        self.assertEqual(b6_r3_table.copied_overlap(keys), [])
        every = list(keys["block_quantity_keys"]) + [k for v in keys["session_quantity_keys"].values() for k in v]
        for family in b6_r3_table.COPIED_FAMILIES:
            for key in every:
                self.assertFalse(key == family or key.startswith(family + "/") or family in key.split("/"),
                                 (family, key))
        keys["session_quantity_keys"]["ALPHA"].append("monitor_cost/cpu_s")
        self.assertEqual(b6_r3_table.copied_overlap(keys), ["monitor_cost"])
        records, _ = b6_r3_table.copied_records(REPO / b6_r3_table.VERIFY)
        self.assertEqual(set(records), set(b6_r3_table.COPIED_FAMILIES))
        text = run().stdout.decode()
        for family in b6_r3_table.COPIED_FAMILIES:
            row = next(line for line in text.splitlines() if "| `" + family + "` |" in line)
            self.assertIn(b6_r3_table.LABEL_COPIED, row)
            for path in records[family]:
                self.assertIn("`" + path + "`", row)

    def test_missing_producer_exits_nonzero_and_names_the_group(self):
        keys = json.loads(KEYS.read_text(encoding="utf-8"))
        keys["session_quantity_keys"]["ALPHA"].append("synthetic_unproduced/qwen3-1p7b/decode/mean_j")
        with tempfile.TemporaryDirectory(prefix="b6-r3-table-") as tmp:
            path = Path(tmp) / "keys.json"
            path.write_text(json.dumps(keys), encoding="utf-8")
            result = run("--keys", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("synthetic_unproduced/<model>/<phase>/mean_j", result.stderr.decode())
        self.assertIn("1 UNSTATED group", result.stderr.decode())

    def test_missing_producer_function_is_unstated(self):
        source = (REPO / b6_r3_table.DEFAULTS["recompute"]).read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="b6-r3-table-") as tmp:
            # Only the AST is read from --recompute's text for producers; drop one producer function.
            broken = Path(tmp) / "recompute.py"
            broken.write_text(source.replace("def dominance_rows(", "def renamed_rows("), encoding="utf-8")
            tree = b6_r3_table.read_recompute(broken)
        self.assertNotIn("dominance_rows", tree["fns"])
        paths = {k: REPO / v for k, v in b6_r3_table.DEFAULTS.items()}
        check = b6_r3_table.read_check(paths["check"])
        prod, label, why = b6_r3_table.classify_session("dominance/qwen3-8b/decode/absolute/R", "BETA", check, tree)
        self.assertEqual((prod, label), (b6_r3_table.UNSTATED, b6_r3_table.UNSTATED))

    def test_output_is_deterministic(self):
        first, second = run(), run()
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)


if __name__ == "__main__":
    unittest.main()
