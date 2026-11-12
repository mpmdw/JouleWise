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
