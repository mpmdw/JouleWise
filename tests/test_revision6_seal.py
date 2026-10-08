"""Bind the prospective registration to shipped bytes and its empty dry run."""

from contextlib import redirect_stdout
import copy
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise import powermetrics_fiducial
from scripts import issue_calibration_acceptance_generation as issuer
from tests.test_acc_25g83_rev6 import declaration, registration, session


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
VALIDATOR = "scripts/validate_powermetrics_fiducial.py"
# Revision 6's heading records the commit it was sealed at.
SEAL_HEADING = re.compile(r"^# Revision 6 \(sealed [0-9]{4}-[0-9]{2}-[0-9]{2} at ([0-9a-f]{7,40})\)$", re.M)
# Era records (orchestrator ruling 2026-10-06): pins.validator_sha256 records the
# validator that produced block 1's derivation captures, so it is checked against
# the validator's bytes at the sealing commit, not today's tree. Acceptance
# re-derives only the estimator files and the protocol; those stay live below.
ERA_PINS = (("validator_sha256", VALIDATOR),)
LIVE_PINS = (
    ("chain_sha256", "scripts/night_chains/calibration_derivation_only.zsh"),
    ("prewindow_check_sha256", "scripts/prewindow_check.sh"),
    ("harness_sha256", "scripts/cap_replay_harness.py"),
    ("roster_sha256", "docs/process_traces/2026-09-29-interactive-ff50b201/130-cap-roster.md"),
)


def _git(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *argv], cwd=ROOT, capture_output=True)


def sealing_commit(text: str) -> str:
    """The full commit Revision 6's heading names; it must be in HEAD's history."""

    found = SEAL_HEADING.findall(text)
    if len(found) != 1:
        raise AssertionError(f"{len(found)} Revision 6 seal headings, expected 1")
    resolved = _git("rev-parse", "--verify", "--quiet", f"{found[0]}^{{commit}}")
    if resolved.returncode != 0:
        raise AssertionError(f"sealing commit {found[0]} is not in this repository")
    commit = resolved.stdout.decode().strip()
    if _git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
        raise AssertionError(f"sealing commit {commit} is not an ancestor of HEAD")
    return commit


def era_pin_mismatches(text: str) -> list[str]:
    """Era pins whose digest differs from the pinned file's bytes at the sealing commit."""

    pins = issuer.revision_six_declaration(text)["pins"]
    commit = sealing_commit(text)
    mismatches = []
    for key, relative in ERA_PINS:
        shown = _git("show", f"{commit}:{relative}")
        if shown.returncode != 0 or pins[key] != hashlib.sha256(shown.stdout).hexdigest():
            mismatches.append(f"{key} != sha256({commit}:{relative})")
    return mismatches


class RevisionSixSealTests(unittest.TestCase):
    def test_historical_bytes_and_shipped_pins_are_preserved(self):
        raw = PREREG.read_bytes()
        prefix, section = raw.split(b"\n# Revision 6 (", 1)
        self.assertEqual(hashlib.sha256(prefix).hexdigest(),
                         "81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1")
        self.assertNotIn(b"TO BE PINNED AT SEAL", section)
        block = issuer.revision_six_declaration(raw.decode())
        pins = block["pins"]
        self.assertEqual(era_pin_mismatches(raw.decode()), [])
        for key, relative in LIVE_PINS:
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

    def test_tampered_era_pin_still_fails(self):
        text = PREREG.read_text(encoding="utf-8")
        pins = issuer.revision_six_declaration(text)["pins"]
        sealed = pins["validator_sha256"]
        flipped = sealed[:-1] + ("0" if sealed[-1] != "0" else "1")
        tampered = text.replace(f'"validator_sha256": "{sealed}"', f'"validator_sha256": "{flipped}"')
        self.assertNotEqual(tampered, text)
        self.assertEqual(era_pin_mismatches(tampered), [f"validator_sha256 != sha256({sealing_commit(text)}:{VALIDATOR})"])
        # Moving the recorded seal to a commit whose validator differs also fails:
        # the parent of the last validator change at or before the seal.
        commit = sealing_commit(text)
        changed = _git("log", "-n1", "--format=%H", commit, "--", VALIDATOR).stdout.decode().strip()
        earlier = _git("rev-parse", f"{changed}^").stdout.decode().strip()
        moved = SEAL_HEADING.sub(lambda m: m.group(0).replace(m.group(1), earlier), text)
        self.assertEqual(sealing_commit(moved), earlier)
        self.assertEqual(len(era_pin_mismatches(moved)), 1)
        # A seal heading naming no commit in history cannot vouch for anything.
        with self.assertRaises(AssertionError):
            era_pin_mismatches(SEAL_HEADING.sub(lambda m: m.group(0).replace(m.group(1), "0" * 40), text))

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
