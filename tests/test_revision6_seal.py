"""Bind the prospective registration to shipped bytes and its empty dry run."""

from contextlib import redirect_stdout
import copy
import hashlib
import io
import json
from pathlib import Path
import re
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise import powermetrics_fiducial
from scripts import issue_calibration_acceptance_generation as issuer
from tests.test_acc_25g83_rev6 import declaration, registration, session


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "configs/calibration/preregistration_d079_epoch_25g83_rev1.md"


class RevisionSixSealTests(unittest.TestCase):
    def test_historical_bytes_and_shipped_pins_are_preserved(self):
        raw = PREREG.read_bytes()
        prefix, section = raw.split(b"\n# Revision 6 (", 1)
        self.assertEqual(hashlib.sha256(prefix).hexdigest(),
                         "81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1")
        self.assertNotIn(b"TO BE PINNED AT SEAL", section)
        block = issuer.revision_six_declaration(raw.decode())
        pins = block["pins"]
        for key, relative in (
            ("chain_sha256", "scripts/night_chains/calibration_derivation_only.zsh"),
            ("validator_sha256", "scripts/validate_powermetrics_fiducial.py"),
            ("prewindow_check_sha256", "scripts/prewindow_check.sh"),
            ("harness_sha256", "scripts/cap_replay_harness.py"),
            ("roster_sha256", "docs/process_traces/2026-09-29-interactive-ff50b201/130-cap-roster.md"),
        ):
            with self.subTest(pin=key):
                self.assertEqual(pins[key], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())
        predecessor = block["predecessor"]
        p8_raw = (ROOT / predecessor["path"]).read_bytes()
        p8 = json.loads(p8_raw)
        self.assertEqual(predecessor["file_sha256"], hashlib.sha256(p8_raw).hexdigest())
        self.assertEqual(predecessor["derivation_sha256"], issuer.derivation_sha256(p8))
        self.assertEqual(predecessor["derivation_sha256"], p8["derivation_sha256"])
        self.assertEqual(pins["estimator_code_sha256"], p8["prospective_rederivation"]["estimator_code_sha256"])
        for relative, digest in pins["estimator_code_sha256"].items():
            with self.subTest(estimator=relative):
                self.assertEqual(digest, hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())
        self.assertEqual(pins["cap_cells"], 1710000)
        self.assertEqual(pins["cap_cells"], powermetrics_fiducial.DETECTION_PROJECTION_CELL_BUDGET)
        # The registration pins the ledger head as it stood before the first window.
        # Each harvest then advances the live pin (recipe section 6), so the live pin
        # equals the registered one until C1 is harvested and only moves forward after.
        head = json.loads((ROOT / "configs/calibration/calibration_ledger_head.json").read_bytes())
        first = pins["ledger_head_pin_at_first_window"]
        self.assertEqual(set(first), {"sequence", "digest"})
        if head["sequence"] == first["sequence"]:
            self.assertEqual(head["head_digest"], first["digest"])
        else:
            self.assertGreater(head["sequence"], first["sequence"])
        for pattern in (issuer._PREREGISTRATION_OS_BUILD, issuer._PREREGISTRATION_POWERMETRICS,
                        r"\bchain digest\s+([0-9a-f]{64})\b"):
            self.assertEqual(len(re.findall(pattern, raw.decode())), 1)
        self.assertEqual(issuer.preregistration_epoch_pins(raw.decode())[0], "25G83")

    def test_empty_check_authenticates_registration_and_cannot_issue(self):
        snapshot = SimpleNamespace(
            receipts=(), bracket_sessions=(), bracket_session_by_id={}, observations=(),
            valid=True, refusal_reasons=(),
        )
        block = declaration()
        with self.assertRaises(issuer.PrepareRefusal):
            issuer.revision_six_sessions(snapshot, (), block)
        # Use the real check dispatcher, declaration parser and count replay;
        # only the ledger/machine sources are injected for this portable fixture.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registration.md"
            for unfilled, expected in ((False, 0), (True, issuer.DRY_RUN_INADMISSIBLE_EXIT)):
                candidate = copy.deepcopy(block)
                if unfilled:
                    candidate["pins"]["chain_sha256"] = "TO BE PINNED AT SEAL"
                path.write_text(registration(candidate))
                args = issuer.build_parser().parse_args([
                    "check", "--preregistration", str(path), "--preregistration-sha256",
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                ])
                output = io.StringIO()
                with patch.object(issuer, "load_calibration_ledger_snapshot", return_value=snapshot), \
                     patch.object(issuer, "observe_machine", return_value={
                         "powermetrics_sha256": issuer.preregistration_epoch_pins(path.read_text())[1]}), \
                     redirect_stdout(output):
                    self.assertEqual(issuer.check(args), expected)
                if not unfilled:
                    self.assertIn("counted_total=0 members_total=0 decision=NEXT_WINDOW", output.getvalue())
            # An opened but unnamed session must still refuse in the empty dry run.
            snapshot.bracket_sessions = (session(1),)
            code, _ = issuer.revision_six_dry_run(snapshot, (), block, (), repo_root=ROOT,
                                                 preregistration_sha256="a" * 64)
            self.assertEqual(code, issuer.DRY_RUN_INADMISSIBLE_EXIT)
