"""Verify PR #813 against the verbatim RL-182 §1.3 and RL-176 §D excerpts."""

import ast
from decimal import Decimal
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).with_name("fixtures") / "rl182"
EVIDENCE = ROOT / "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign"
POWER_SCRIPT = EVIDENCE / "rl178-cells/power_table.py"


class RegistrationEditsTests(unittest.TestCase):
    def test_each_of_the_seventeen_edits_appears_once_at_each_ruled_location(self):
        # Edits copied from audit 7ec51b1d9, matched-control clauses from 61377dc45.
        chunks = re.split(r"(?m)^\*\*E(\d+)\. ", (FIXTURES / "edits.md").read_text())
        edits = dict(zip(map(int, chunks[1::2]), chunks[2::2]))
        self.assertEqual(list(edits), list(range(1, 18)))

        def quoted(number):
            return re.findall(r'"([^"\n]+)"', edits[number])

        def block(number):
            return "\n".join(line.removeprefix("> ").removeprefix(">") for line in
                             edits[number].splitlines() if line.startswith(">"))

        p4 = (ROOT / "docs/align/pilot_protocol_v4.md").read_text()
        am = (EVIDENCE / "r1-ready-1116/AMENDMENT-R1-DRAFT.md").read_text()
        dv = (ROOT / "docs/align/v4/DEVIATIONS.md").read_text()
        scorer = (ROOT / "joulewise/align/apple/rl176.py").read_text()

        b2, remainder = p4.split("**B2. S,", 1)[1].split("**B2a.", 1)
        b2 = "**B2. S," + b2
        b2a = remainder.split("\n\n", 1)[0]
        am_score = am.split("### S score\n", 1)[1].split("\n### RL-178", 1)[0]
        row = next(line for line in dv.splitlines() if line.startswith("| RL176-B-S-admit |"))
        transfer = next(line for line in am.splitlines() if line.startswith("| 14 |"))
        control_lines = (FIXTURES / "matched-control.md").read_text().strip().splitlines()
        trigger = control_lines[0].split("** Under a null", 1)[0] + "**"
        heading = re.search(r"headed (\*Matched control .*?\*)", edits[13])[1]
        control = f"{heading}\n\n{trigger}\n\n" + "\n".join(control_lines[3:7])
        digest = hashlib.sha256(POWER_SCRIPT.read_bytes()).hexdigest()

        checks = {
            1: [(b2, passage) for passage in quoted(1)],
            2: [(b2, block(2)), (am_score, block(2))],
            3: [(b2, "in rational arithmetic. " + block(3))],
            4: [(b2, quoted(4)[0].rstrip("…")), (b2, "to about 11 %" + quoted(4)[2])],
            5: [(b2, "`docs/align/v4/claim-b-power.json`. "
                 + quoted(5)[0].replace("‹the builder prints it›", digest))],
            6: [(b2a, block(6))],
            7: [(b2, block(7))],
            8: [(b2, quoted(8)[0])],
            9: [(b2, block(9)), (am, block(9)), (am, quoted(9)[0])],
            10: [(b2a, quoted(10)[0].lstrip("…") + quoted(10)[1].rstrip("…")),
                 (b2a, quoted(10)[2].lstrip("…") + "."),
                 (b2a, quoted(10)[3].lstrip("…") + quoted(10)[4])],
            11: [(p4.split("**B9.", 1)[1], quoted(11)[0].strip("…"))],
            12: [(p4, passage) for passage in quoted(12)],
            13: [(b2, control), (am, control)],
            14: [(am, quoted(14)[0] + "\n\n## G."),
                 (am, quoted(14)[1].lstrip("…")),
                 (am, f"({quoted(14)[4]})."),
                 (am, f"Amendment {quoted(14)[4]}."),
                 (am_score, block(2))],
            15: [(row, " | " + block(15) + " |")],
            16: [(scorer, 'raise ValueError("sabotage-instructed member carries a DC-in trace")')],
            17: [(transfer, quoted(17)[0])],
        }
        self.assertEqual(checks.keys(), edits.keys())
        for number, checks_for_edit in checks.items():
            for location, passage in checks_for_edit:
                with self.subTest(edit=f"E{number}", passage=passage):
                    self.assertEqual(location.count(passage), 1)
        self.assertNotIn("W1_PYDANTIC_VERSION", p4 + am)
        self.assertNotIn("B2a's Q planning reference uses the original", p4)
        self.assertNotIn("subject to cold review", am)
        self.assertNotIn("awaits the research lead's cold review", am.replace("\n", " "))
        self.assertEqual(row.strip("| ").split(" | ")[2], block(15))

    def test_rl182a_first_token_stamp_text_matches_in_protocol_and_amendment(self):
        source = (FIXTURES / "addendum.md").read_text()
        self.assertEqual(re.findall(r"(?m)^- \*\*([^*]+)\*\*", source), [
            "E2, first bullet (P4:1188).", "E10 (P4:1283).", "AM:47.",
        ])
        score, outcome, old_am, wording = re.findall(r'"([^"]+)"', source)
        p4 = (ROOT / "docs/align/pilot_protocol_v4.md").read_text()
        am = (EVIDENCE / "r1-ready-1116/AMENDMENT-R1-DRAFT.md").read_text()
        for doc in (p4, am):
            self.assertEqual(doc.count("- " + score), 1)
            self.assertEqual(doc.count(outcome.lstrip("…")), 1)
            self.assertNotIn("first stamped token", doc)
        self.assertEqual(am.count(wording), 1)
        self.assertNotIn(old_am, am)

    def test_named_power_script_reproduces_both_columns(self):
        output = subprocess.check_output([sys.executable, "-B", POWER_SCRIPT], text=True)
        rows = {}
        for line in output.splitlines():
            count, levels = line.split(" ", 1)
            estimates = ast.literal_eval(levels)
            self.assertEqual([row[0] for row in estimates], [.025, .0125])
            rows[int(count)] = [
                " / ".join(f"{Decimal(str(power)):.2f}".lstrip("0") for power in row[3])
                for row in estimates
            ]
        self.assertEqual(list(rows), [22, 20, 16, 11, 6])
        amendment = (EVIDENCE / "r1-ready-1116/AMENDMENT-R1-DRAFT.md").read_text()
        for count, powers in rows.items():
            with self.subTest(strata=count):
                self.assertEqual(amendment.count(f"| {count} | {' | '.join(powers)} |"), 1)
