"""Revision 6 member custody is named by the night plan id, not the session id.

The first Revision 6 derivation (2026-10-02) refused every member: the issuer's
corpus-root check (ISSUANCE-CUSTODY-OUTSIDE-REPO-01, written for Revision 5)
required ``<corpus root>/<session id>/runs/instrument_validation/<capture>``,
but run_night.py names a Revision 6 custody directory by the NIGHT PLAN id
(``d079-epoch-25g83-r6-derivation-c1-20261001T0617Z``), which the window's
harvest record carries as ``plan_id``; the session id is
``d079-epoch-25g83-r6-20261001T0617Z``. Fixtures that used one name for both
hid it. These tests use identity keys and paths only; no measured value is
read from real data.
"""
from __future__ import annotations

from contextlib import redirect_stdout
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import issue_calibration_acceptance_generation as issuer

REPO_ROOT = Path(__file__).resolve().parents[1]
WINDOWS = REPO_ROOT / "docs/process_traces/rev6-windows"
C1_SID = "d079-epoch-25g83-r6-20261001T0617Z"
C2_SID = "d079-epoch-25g83-r6-20261001T2252Z"
LEDGER_PLAN_ID = "plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3"
REAL_CORPUS_ROOT = "/Users/edr/night-custody"
REAL_LEDGER = Path(REAL_CORPUS_ROOT) / (
    "measurement/JouleWise-measurement-20261001T2252Z-r6-c2/runs/calibration_observation_ledger.jsonl")
REAL_ARCHIVE = Path("/Users/edr/night-archive")

# (session id, capture id, custody_locator) of every Revision 6 valid
# finalization row in the calibration ledger at sequence 376 (head pin
# a5b825b7...7014), copied verbatim; identity keys only.
REAL_ROWS = (
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d01', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d01'),
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d02', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d02'),
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d03', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d03'),
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d04', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d04'),
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d05', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d05'),
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d06', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d06'),
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d07', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d07'),
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d08', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d08'),
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d09', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d09'),
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d10', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d10'),
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d11', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d11'),
    ('d079-epoch-25g83-r6-20261001T0617Z', 'd079-epoch-25g83-r6-20261001T0617Z-d12', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c1-20261001T0617Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T0617Z-d12'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d01', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d01'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d02', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d02'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d03', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d03'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d04', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d04'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d05', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d05'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d06', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d06'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d07', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d07'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d08', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d08'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d09', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d09'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d10', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d10'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d11', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d11'),
    ('d079-epoch-25g83-r6-20261001T2252Z', 'd079-epoch-25g83-r6-20261001T2252Z-d12', '/Users/edr/night-custody/d079-epoch-25g83-r6-derivation-c2-20261001T2252Z/runs/instrument_validation/d079-epoch-25g83-r6-20261001T2252Z-d12'),
)


def _rows(sid):
    return [row for row in REAL_ROWS if row[0] == sid]


class RealRevisionSixIdentityReplay(unittest.TestCase):
    """C1 and C2 as recorded: committed harvest records plus ledger locators."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.corpus = self.base / "night-custody"
        # The issuer's own harvest-record reader supplies each session's plan
        # id; empty finalized_slots stops it at record identity, before any
        # evidence file this replay does not carry.
        harvests, sessions = [], []
        for sid in (C1_SID, C2_SID):
            custody = self.base / sid / "custody-root"
            for relative in ("night/start_conditions.json", "harvest/r9_window.json"):
                (custody / relative).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(WINDOWS / sid / relative, custody / relative)
            harvest = json.loads((WINDOWS / sid / "harvest.json").read_bytes())
            harvest["custody_root"] = str(custody)
            path = self.base / sid / "harvest.json"
            path.write_text(json.dumps(harvest, sort_keys=True))
            harvests.append(path)
            sessions.append(type("Session", (), {"session_id": sid, "plan_id": LEDGER_PLAN_ID,
                                                 "finalized_slots": {}})())
        records = issuer.revision_six_records(harvests, sessions, {}, repo_root=REPO_ROOT,
                                              require_committed=False)
        self.plan_ids = {sid: record["plan_id"] for sid, record in records.items()}
        # Rebuild the real locator tree under a temporary corpus root with
        # stub primary files (no real capture bytes are copied or read).
        self.stub = {"manifest.json": b"{}\n", "instrument_evidence.json": b'{"b_fiducial_s": "stub"}\n'}
        self.locators = []
        for sid, attempt, locator in REAL_ROWS:
            relative = Path(locator).relative_to(REAL_CORPUS_ROOT)
            directory = self.corpus / relative
            directory.mkdir(parents=True)
            for name, raw in self.stub.items():
                (directory / name).write_bytes(raw)
            self.locators.append((sid, attempt, str(directory), relative.as_posix()))

    def test_harvest_plan_ids_name_the_custody_directories_not_the_sessions(self):
        self.assertEqual(self.plan_ids, {
            C1_SID: "d079-epoch-25g83-r6-derivation-c1-20261001T0617Z",
            C2_SID: "d079-epoch-25g83-r6-derivation-c2-20261001T2252Z"})
        self.assertEqual(len(_rows(C1_SID)), 12)
        self.assertEqual(len(_rows(C2_SID)), 12)
        for sid, _attempt, locator in REAL_ROWS:
            first = Path(locator).relative_to(REAL_CORPUS_ROOT).parts[0]
            self.assertEqual(first, self.plan_ids[sid])
            self.assertNotEqual(first, sid)

    def test_every_real_member_path_is_admitted_under_its_night_plan(self):
        for sid, attempt, locator, relative in self.locators:
            self.assertEqual(issuer._corpus_relative_custody(
                locator, attempt, sid, self.corpus, night_plan_id=self.plan_ids[sid]), relative)

    def test_revision_five_rule_still_refuses_the_real_rows(self):
        sid, attempt, locator, _ = self.locators[0]
        with self.assertRaisesRegex(issuer.PrepareRefusal,
                                    "first path part does not equal the session id$"):
            issuer._corpus_relative_custody(locator, attempt, sid, self.corpus)

    def test_the_other_windows_plan_id_refuses(self):
        for sid, attempt, locator, _ in self.locators:
            other = self.plan_ids[C2_SID if sid == C1_SID else C1_SID]
            with self.assertRaisesRegex(issuer.PrepareRefusal, "night plan id"):
                issuer._corpus_relative_custody(locator, attempt, sid, self.corpus, night_plan_id=other)
            with self.assertRaisesRegex(issuer.PrepareRefusal, "night plan id"):
                issuer._corpus_relative_custody(locator, attempt, sid, self.corpus, night_plan_id="")

    def test_verify_member_binds_the_real_rows_to_their_night_plan(self):
        digests = {name: hashlib.sha256(raw).hexdigest() for name, raw in self.stub.items()}
        content_id = issuer.content_id_from_artifact_hashes(digests)
        prior = [{"session_id": sid, "attempt_id": attempt, "content_id": content_id,
                  "disposition": "valid"} for sid, attempt, _, _ in self.locators]
        for index, (sid, attempt, _locator, relative) in enumerate(self.locators):
            member = {"member_id": attempt, "source_directory": relative, "b_fiducial_s": "stub",
                      "manifest_sha256": digests["manifest.json"],
                      "instrument_evidence_sha256": digests["instrument_evidence.json"]}
            rows = [prior[index]]
            self.assertTrue(issuer._verify_corpus_member(member, rows, self.corpus, self.plan_ids))
            self.assertFalse(issuer._verify_corpus_member(member, rows, self.corpus))
            swapped = {C1_SID: self.plan_ids[C2_SID], C2_SID: self.plan_ids[C1_SID]}
            self.assertFalse(issuer._verify_corpus_member(member, rows, self.corpus, swapped))
            self.assertFalse(issuer._verify_corpus_member(member, rows, self.corpus, {}))

    @unittest.skipUnless(REAL_LEDGER.is_file(), "measurement ledger not on this machine")
    def test_literal_rows_equal_the_ledger_and_archive_equals_committed(self):
        rows = []
        with REAL_LEDGER.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                if (row.get("event") == "bracket-session-slot-finalization"
                        and row.get("session_id") in (C1_SID, C2_SID)
                        and row.get("disposition") == "valid"):
                    rows.append((row["session_id"], row["attempt_id"], row["custody_locator"]))
        self.assertEqual(tuple(rows), REAL_ROWS)
        for sid, plan in ((C1_SID, "c1-20261001T0617Z"), (C2_SID, "c2-20261001T2252Z")):
            archived = REAL_ARCHIVE / f"harvest-d079-epoch-25g83-r6-derivation-{plan}/harvest.json"
            self.assertEqual(archived.read_bytes(), (WINDOWS / sid / "harvest.json").read_bytes())
        for sid, attempt, locator in REAL_ROWS:
            self.assertEqual(issuer._corpus_relative_custody(
                locator, attempt, sid, Path(REAL_CORPUS_ROOT), night_plan_id=self.plan_ids[sid]),
                Path(locator).relative_to(REAL_CORPUS_ROOT).as_posix())


class ProductionShapedCandidate(unittest.TestCase):
    """Full synthetic Revision 6 candidate with custody outside the repository."""

    def build(self, root, **kwargs):
        from tests.fixtures.epoch_bootstrap.build import Slot
        from tests.fixtures.epoch_bootstrap.revision6 import build
        return build(root, corpus_root=True,
                     slots=[Slot(str(Decimal(".02") + Decimal(i) / 10000)) for i in range(12)],
                     second_slots=[Slot(str(Decimal(".0201") + Decimal(i) / 10000)) for i in range(12)],
                     **kwargs)

    def prepare(self, f):
        from tests.fixtures.epoch_bootstrap.revision6 import commit
        with patch.object(issuer, "load_calibration_ledger_snapshot", return_value=f["snapshot"]), \
                patch.object(issuer, "_authenticated_predecessor", return_value=f["predecessor"]):
            try:
                return issuer._prepare_candidate(f["args"])
            except issuer.PrepareRefusal as error:
                if "campaign R9 bytes are not committed" not in str(error):
                    raise
                record = Path(f["args"].out).with_name("r9_campaign.json")
                (f["fixture"]["root"] / "r9_campaign.json").write_bytes(record.read_bytes())
                commit(f["fixture"]["root"])
                return issuer._prepare_candidate(f["args"])

    def verify(self, artifact, corpus_root):
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = issuer.main(["verify-members", "--artifact", str(artifact),
                                "--corpus-root", str(corpus_root)])
        return code, stream.getvalue()

    def test_custody_named_by_night_plan_issues_and_verifies(self):
        from tests.fixtures.epoch_bootstrap.revision6 import night_plan_of, sid
        with tempfile.TemporaryDirectory() as tmp:
            f = self.build(Path(tmp) / "case")
            corpus = Path(f["args"].corpus_root)
            for index in (1, 2):
                self.assertTrue((corpus / night_plan_of(sid(index))).is_dir())
                self.assertFalse((corpus / sid(index)).exists())
                self.assertNotEqual(night_plan_of(sid(index)), sid(index))
            candidate = self.prepare(f)
            members = candidate["derivation_corpus"]["members"]
            self.assertEqual(len(members), 24)
            self.assertEqual({m["source_directory"].split("/")[0] for m in members},
                             {night_plan_of(sid(1)), night_plan_of(sid(2))})
            records = candidate["derivation_notes"]["revision6_records"]
            self.assertEqual({k: v["plan_id"] for k, v in records.items()},
                             {sid(1): night_plan_of(sid(1)), sid(2): night_plan_of(sid(2))})
            self.assertIn("night plan", candidate["derivation_notes"]["member_custody"])
            artifact = Path(tmp) / "artifact.json"
            artifact.write_text(json.dumps(candidate))
            code, text = self.verify(artifact, corpus)
            self.assertEqual(code, 0, text)
            self.assertEqual(text.count(": PASS"), 24)
            # A Revision 6 artifact naming another plan id for a session fails
            # that session's members, and only those.
            tampered = json.loads(artifact.read_text())
            tampered["derivation_notes"]["revision6_records"][sid(1)]["plan_id"] = night_plan_of(sid(2))
            artifact.write_text(json.dumps(tampered))
            code, text = self.verify(artifact, corpus)
            self.assertEqual(code, 3)
            self.assertEqual((text.count(": PASS"), text.count(": FAIL")), (12, 12))
            # Dropping the plan id fails closed; it never falls back to the
            # session-id rule.
            tampered["derivation_notes"]["revision6_records"][sid(1)].pop("plan_id")
            artifact.write_text(json.dumps(tampered))
            self.assertEqual(self.verify(artifact, corpus)[1].count(": FAIL"), 12)

    def test_custody_named_by_another_plan_id_refuses(self):
        from tests.fixtures.epoch_bootstrap.revision6 import night_plan_of, sid
        with tempfile.TemporaryDirectory() as tmp:
            f = self.build(Path(tmp) / "case", custody_names={sid(1): night_plan_of(sid(2)) + "-other"})
            with self.assertRaisesRegex(issuer.PrepareRefusal,
                                        f"member {sid(1)}-d01: .*night plan id"):
                self.prepare(f)

    def test_custody_named_by_session_id_refuses_under_revision_six(self):
        from tests.fixtures.epoch_bootstrap.revision6 import sid
        with tempfile.TemporaryDirectory() as tmp:
            f = self.build(Path(tmp) / "case", custody_names={sid(1): sid(1)})
            with self.assertRaisesRegex(issuer.PrepareRefusal,
                                        f"member {sid(1)}-d01: .*night plan id"):
                self.prepare(f)


if __name__ == "__main__":
    unittest.main()
