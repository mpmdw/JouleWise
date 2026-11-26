"""Check the W1 registration text against RL-223 §5."""

from pathlib import Path
import unittest


class RegistrationPrintTests(unittest.TestCase):
    def test_s_print_text_at_each_ruled_location(self):
        root = Path(__file__).resolve().parents[2]
        protocol = (root / "docs/align/pilot_protocol_v4.md").read_text()
        status = (Path(__file__).with_name("fixtures") / "rl223/b2-status.md").read_text().removesuffix("\n")
        self.assertIn(
            "**B0. What v4 claims.** K is the registered claim and alone is confirmatory; "
            "Q is a registered secondary at its own alpha. S was a registered secondary until "
            "RL-223 and is a print (B2, *Status*).",
            protocol.splitlines(),
        )
        row, = (line for line in protocol.splitlines() if line.startswith("| S, sabotage-instructed "))
        _, status_cell, _, alpha_cell, words_cell = row[2:-2].split(" | ")
        self.assertEqual(status_cell, "print since RL-223, registered before it; randomized (B5)")
        self.assertEqual(
            alpha_cell,
            "none in force; p_sup, p_inf and both intervals print (was: superiority .0125 one-sided; "
            "equivalence TOST .05 per side, rank region (0.29794, 0.70206))",
        )
        self.assertEqual(words_cell, "none; `S NOT EVALUABLE` at K_S = 0")

        title = "**B2. S, sabotage-instructed versus benign at logged counts, on decode-only rows.**"
        b2 = protocol.split(title, 1)[1].split("**B2a.", 1)[0]
        self.assertEqual(protocol.count(status), 1)
        self.assertTrue(b2.startswith(f"\n\n{status}\n\n*Question.*"))
        self.assertTrue(b2.split("\n\n*Outcome words.*", 1)[0].endswith(
            "S was a registered secondary until RL-223 (*Status*); K alone is confirmatory."
        ))
