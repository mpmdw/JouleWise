"""The landed known-bytes reading rule keeps the as-run text byte-identical, and
registration section 1 cites it with the slot fill (RL-7 (b), RL-24 #11)."""
import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / 'docs/registrations/bytes_known_bytes_reading_rule.md'
REGISTRATION = ROOT / 'docs/registrations/bytes_pack_v1.md'
SLOT_FILL = ROOT / 'docs/process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md'
BLINDCHECK = ROOT / 'docs/process_traces/2026-11-11-bytes-blindcheck/BLINDCHECK.md'

# sha256 of 53bcceeac:docs/registrations/bytes_known_bytes_reading_rule_DRAFT.md (the code the test ran on).
AS_RUN_SHA256 = '569601b3cce8b88dda20d8cbe7e4804c37d04fedfe5945f60c6492328ea79132'
# sha256 of the slot record as committed on main (blob 4159c0ac).
SLOT_FILL_SHA256 = '5729d8c7dad4400b533d9939f885037e100fa6fd27e75d812bbe31035c970312'
BEGIN = ('<!-- PART A BEGIN: byte-identical to '
         '53bcceeac:docs/registrations/bytes_known_bytes_reading_rule_DRAFT.md -->\n')
END = '<!-- PART A END -->\n'


class KnownBytesRuleLanding(unittest.TestCase):
    def test_part_a_is_the_as_run_text(self):
        data = RULE.read_bytes()
        self.assertEqual(data.count(BEGIN.encode()), 1)
        self.assertEqual(data.count(END.encode()), 1)
        part_a = data.split(BEGIN.encode(), 1)[1].split(END.encode(), 1)[0]
        self.assertEqual(hashlib.sha256(part_a).hexdigest(), AS_RUN_SHA256)
        self.assertIn(AS_RUN_SHA256, data.split(BEGIN.encode(), 1)[0].decode('utf-8'))

    def test_slot_record_is_byte_identical(self):
        self.assertEqual(hashlib.sha256(SLOT_FILL.read_bytes()).hexdigest(), SLOT_FILL_SHA256)

    def test_registration_slot_is_filled_and_cites_the_landed_rule(self):
        text = REGISTRATION.read_text(encoding='utf-8')
        section1 = text.split('\n## 1. ', 1)[1].split('\n## 2. ', 1)[0]
        self.assertRegex(section1, r'`⟦MAC: known-bytes stream test outcome⟧` — \*\*FILLED\*\* \(2026-10-31')
        self.assertIn('(bytes_known_bytes_reading_rule.md)', section1)
        self.assertIn('(../process_traces/2026-10-31-magistrate-5cbfbcfc/KB-SLOT-FILL.md)', section1)
        self.assertNotIn('bytes_known_bytes_reading_rule_DRAFT.md', text)
        for boundary, value in (('rails', '0.0092 ± 0.0021'), ('GPU rail', '0.00879 ± 0.00010'),
                                ('DC input', '0.0389 ± 0.0072'), ('rest', '0.0296 ± 0.0084')):
            self.assertRegex(section1, rf'\| {re.escape(boundary)} \| {re.escape(value)} \|')
        row = next(line for line in text.splitlines()
                   if line.startswith('| `⟦MAC: known-bytes stream test outcome⟧` | §1 |'))
        self.assertIn('**FILLED** 2026-10-31', row)

    def test_blinding_check_record_exists_for_the_commitment_to_cite(self):
        text = BLINDCHECK.read_text(encoding='utf-8')
        self.assertIn('P1-AUTO-BLINDCHECK', text)
        self.assertIn('RL-7 (g)', text)


if __name__ == '__main__':
    unittest.main()
