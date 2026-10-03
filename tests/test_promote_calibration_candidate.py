"""Promotion input, seals, disclosure, and temporary-output counterfactuals."""

import copy
import hashlib
import gzip
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joulewise.calibration_bracketing as bracket
from scripts import promote_calibration_candidate as promote
from scripts.issue_calibration_acceptance_generation import derivation_input_sha256


class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name).resolve()
        self.candidate_raw = promote.CANDIDATE.read_bytes()
        self.candidate = json.loads(self.candidate_raw)
        (root / "candidate.json").write_bytes(self.candidate_raw)
        ruling_raw = b"synthetic ruling citation for promotion tests\n"
        (root / "ruling.txt").write_bytes(ruling_raw)
        log_raw = b"synthetic preserved network-time log\n"
        (root / "log.gz").write_bytes(gzip.compress(log_raw))
        citation = {"relative_path": "ruling.txt",
                    "file_sha256": hashlib.sha256(ruling_raw).hexdigest()}
        # Main has the candidate, but no issuance text for the withdrawn file.
        # Supply synthetic text and cited evidence entirely in a temporary tree.
        issuance = {
            "reason": "synthetic promotion test",
            "required_verification": "complete: synthetic promotion test",
            "network_time_provenance": {
                "disclosure_id": "D8", "text": "synthetic disclosure 8",
                "source_rulings": [dict(citation)],
                "preserved_log": {"relative_path": "log.gz",
                                  "plain_text_sha256": hashlib.sha256(log_raw).hexdigest()},
            },
            "issuance_record": {
                "source_candidate": {
                    "relative_path": "candidate.json", "file_sha256": promote.CANDIDATE_SHA256,
                    "derivation_sha256": self.candidate["derivation_sha256"],
                },
                "disclosures": [{"id": f"D{n}", "text": f"synthetic disclosure {n}"}
                                for n in range(1, 9)],
                "holds": [{"id": key, "text": f"synthetic condition {key}"}
                          for key in ("H1", "H5", "H6", "H7")],
                "rulings": [{"id": key, **citation} for key in promote.RULING_IDS],
                "claim_eligible_meaning": promote.CLAIM_ELIGIBLE_MEANING,
                "hold_enforcement": "synthetic issuance metadata; no runtime authority",
            },
        }
        self.issuance_raw = json.dumps(issuance).encode()
        (root / "issuance.json").write_bytes(self.issuance_raw)
        root_patch = patch.object(promote, "ROOT", root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        self.issued_raw = promote.promote(self.candidate_raw, self.issuance_raw)
        self.issued = json.loads(self.issued_raw)

    def test_p1_write_and_check_temporary_output(self):
        runner = ("import sys; from pathlib import Path; "
                  "from scripts import promote_calibration_candidate as p; "
                  "p.ROOT = Path(sys.argv.pop(1)); p.main()")
        path = promote.ROOT / "issued.json"
        common = ["python3", "-B", "-c", runner, str(promote.ROOT),
                  "--candidate", str(promote.ROOT / "candidate.json"),
                  "--issuance-text", str(promote.ROOT / "issuance.json")]
        for action in ("--out", "--check"):
            result = subprocess.run(common + [action, str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(),
                             f"issued sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
        self.assertEqual(path.read_bytes(), self.issued_raw)
        self.assertIsNone(bracket.load_calibration_acceptance_bound(path))
        self.assertNotIn(self.issued["acceptance_id"], bracket.ISSUED_ACCEPTANCE_REGISTRY)
        self.assertEqual(bracket.ACTIVE_ACCEPTANCE_ID, bracket.EPOCH_25G83_R2_ACCEPTANCE_ID)

    def test_cli_requires_explicit_issuance_text(self):
        script = Path(__file__).resolve().parents[1] / "scripts/promote_calibration_candidate.py"
        path = promote.ROOT / "must-not-be-created.json"
        result = subprocess.run(["python3", "-B", str(script), "--out", str(path)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("--issuance-text", result.stderr)
        self.assertFalse(path.exists())

    def test_p2_protected_paths_unchanged(self):
        protected = (
            "schema_version", "acceptance_id", "decision_ids", "ledger_cutoff",
            "identity_epoch", "prospective_rederivation", "derivation_corpus",
            "prior_observation_set", "decimal_derivation", "registered_generation_row",
            "derivation_input_sha256",
        )
        for key in protected:
            self.assertEqual(self.issued[key], self.candidate[key], key)
            self.assertEqual(json.dumps(self.issued[key], ensure_ascii=True), json.dumps(self.candidate[key], ensure_ascii=True), key)
        for key in self.candidate["derivation_notes"]:
            self.assertEqual(self.issued["derivation_notes"][key], self.candidate["derivation_notes"][key])
            self.assertEqual(json.dumps(self.issued["derivation_notes"][key], ensure_ascii=True),
                             json.dumps(self.candidate["derivation_notes"][key], ensure_ascii=True))
        self.assertEqual(self.issued["backfill_candidate"]["candidate_inventory"], self.candidate["backfill_candidate"]["candidate_inventory"])
        self.assertEqual(json.dumps(self.issued["backfill_candidate"]["candidate_inventory"], ensure_ascii=True),
                         json.dumps(self.candidate["backfill_candidate"]["candidate_inventory"], ensure_ascii=True))

    def test_p3_changed_member_refuses_both_seals(self):
        candidate = copy.deepcopy(self.candidate)
        candidate["derivation_corpus"]["members"][0]["b_fiducial_s"] = "0.9"
        raw = (json.dumps(candidate, indent=2) + "\n").encode()
        with self.assertRaisesRegex(ValueError, "candidate digest mismatch"):
            promote.promote(raw, self.issuance_raw)
        with patch.object(promote, "CANDIDATE_SHA256", hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(ValueError, "candidate seal"):
                promote.promote(raw, self.issuance_raw)

    def test_p4_required_disclosures_h1_and_ruling_digests(self):
        issuance = json.loads(self.issuance_raw)
        for missing in (f"D{number}" for number in range(1, 9)):
            text = copy.deepcopy(issuance)
            text["issuance_record"]["disclosures"] = [row for row in text["issuance_record"]["disclosures"] if row["id"] != missing]
            with self.assertRaises(ValueError):
                promote.promote(self.candidate_raw, json.dumps(text).encode())
        text = copy.deepcopy(issuance)
        text["issuance_record"]["holds"] = [row for row in text["issuance_record"]["holds"] if row["id"] != "H1"]
        with self.assertRaisesRegex(ValueError, "H1"):
            promote.promote(self.candidate_raw, json.dumps(text).encode())
        for index in range(4):
            text = copy.deepcopy(issuance)
            del text["issuance_record"]["rulings"][index]["file_sha256"]
            with self.assertRaisesRegex(ValueError, "ruling digests"):
                promote.promote(self.candidate_raw, json.dumps(text).encode())

    def test_p8_citations_and_all_four_holds_are_complete(self):
        issuance = json.loads(self.issuance_raw)
        edits = (
            lambda t: t["issuance_record"]["source_candidate"].pop("relative_path"),
            lambda t: t["issuance_record"]["rulings"][0].pop("relative_path"),
            lambda t: t["network_time_provenance"]["source_rulings"][0].pop("file_sha256"),
            lambda t: t["network_time_provenance"]["preserved_log"].pop("relative_path"),
            lambda t: t["issuance_record"]["holds"][1].__setitem__("text", ""),
        )
        for edit in edits:
            text = copy.deepcopy(issuance)
            edit(text)
            with self.subTest(edit=edit), self.assertRaises(ValueError):
                promote.promote(self.candidate_raw, json.dumps(text).encode())

    def test_p6_cited_evidence_and_disclosure_mutations_refuse(self):
        issuance = json.loads(self.issuance_raw)
        mutations = []

        def changed(edit):
            text = copy.deepcopy(issuance)
            edit(text)
            mutations.append(text)

        changed(lambda t: t["issuance_record"]["rulings"][0].__setitem__("file_sha256", "f" * 64))
        changed(lambda t: t["issuance_record"]["rulings"][0].__setitem__("relative_path", "nonexistent.md"))
        changed(lambda t: t["issuance_record"]["disclosures"][7].__setitem__("text", "x"))
        changed(lambda t: t["network_time_provenance"].__setitem__("text", "contradicts D8"))
        changed(lambda t: (t["issuance_record"].pop("claim_eligible_meaning"),
                           t["issuance_record"].pop("hold_enforcement")))
        changed(lambda t: t["issuance_record"]["source_candidate"].__setitem__("relative_path", "elsewhere"))
        for index, text in enumerate(mutations, start=1):
            with self.subTest(altered_text=f"P4{chr(ord('a') + index - 1)}"):
                with self.assertRaises(ValueError):
                    promote.promote(self.candidate_raw, json.dumps(text).encode())

    def test_p7_issued_input_seal_drift_stops(self):
        def drift_on_issued(value):
            if value.get("artifact_role") == "issued":
                return "f" * 64
            return derivation_input_sha256(value)

        with patch.object(promote, "derivation_input_sha256", side_effect=drift_on_issued):
            with self.assertRaisesRegex(ValueError, "STOP: derivation input seal"):
                promote.promote(self.candidate_raw, self.issuance_raw)


class RevisionSixPromotionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.candidate_raw = promote.REV6_CANDIDATE.read_bytes()
        self.candidate = json.loads(self.candidate_raw)
        (self.root / 'candidate.json').write_bytes(self.candidate_raw)
        citation_raw = b'synthetic rev6 citation\n'
        (self.root / 'citation.txt').write_bytes(citation_raw)
        citation = {'relative_path': 'citation.txt',
                    'file_sha256': hashlib.sha256(citation_raw).hexdigest()}
        self.text = {
            'reason': 'synthetic Revision 6 issuance',
            'required_verification': 'complete: synthetic Revision 6 verification',
            'issuance_record': {
                'source_candidate': {'relative_path': 'candidate.json',
                    'file_sha256': promote.REV6_CANDIDATE_SHA256,
                    'derivation_sha256': self.candidate['derivation_sha256']},
                'rulings': [{'id': key, **citation} for key in promote.REV6_RULING_IDS],
                'disclosures': [{'id': 'D1', 'text': 'synthetic OFF receipts'}] + [
                    {'id': f'D{n}', 'text': f'synthetic disclosure {n}'} for n in range(2, 11)],
                'claim_eligible_meaning': promote.REV6_CLAIM_ELIGIBLE_MEANING,
            },
            'network_time_provenance': {
                'disclosure_id': 'D1', 'text': 'synthetic OFF receipts',
                'erratum': dict(citation),
                'receipts': [{'session_id': session, **citation} for session in
                             self.candidate['registered_generation_row']['registration_session_ids']],
            },
        }
        root_patch = patch.object(promote, 'ROOT', self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)

    def promote_text(self, text):
        return promote.promote(self.candidate_raw, json.dumps(text).encode())

    def test_rev6_write_check_reload_and_protected_fields(self):
        path = self.root / 'issued.json'
        issuance = self.root / 'issuance.json'
        issuance.write_text(json.dumps(self.text))
        runner = ('import sys; from pathlib import Path; '
                  'from scripts import promote_calibration_candidate as p; '
                  'p.ROOT = Path(sys.argv.pop(1)); p.main()')
        import sys
        common = [sys.executable, '-B', '-c', runner, str(self.root),
                  '--candidate', str(self.root / 'candidate.json'),
                  '--issuance-text', str(issuance)]
        for action in ('--out', '--check'):
            result = subprocess.run(common + [action, str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(),
                f'issued sha256={hashlib.sha256(path.read_bytes()).hexdigest()}')
        issued = json.loads(path.read_bytes())
        self.assertEqual(issued['artifact_role'], 'issued')
        self.assertTrue(issued['issuance']['claim_eligible'])
        self.assertEqual(issued['derivation_input_sha256'], promote.REV6_INPUT_SHA256)
        for key in promote.PROTECTED:
            self.assertEqual(issued[key], self.candidate[key], key)
            self.assertEqual(json.dumps(issued[key]), json.dumps(self.candidate[key]), key)
        for key, value in self.candidate['derivation_notes'].items():
            self.assertEqual(issued['derivation_notes'][key], value, key)
        self.assertEqual(issued['backfill_candidate']['candidate_inventory'],
                         self.candidate['backfill_candidate']['candidate_inventory'])
        # Synthetic text is not the lead's issued pin. Authenticate this temporary
        # file under a temporary registry pin, then restore the production pin.
        with patch.dict(bracket.ISSUED_ACCEPTANCE_REGISTRY, {
            issued['acceptance_id']: {'path': path, 'relative_path': 'issued.json',
                                     'file_sha256': hashlib.sha256(path.read_bytes()).hexdigest()},
        }):
            loaded = bracket.load_calibration_acceptance_bound(path)
            self.assertEqual(loaded, issued)
            self.assertTrue(bracket._valid_acceptance_bound(loaded))

    def test_rev6_schema_counterfactuals_red_then_restored(self):
        mutations = []
        for key in self.text:
            mutations.append((f'top_missing_{key}', lambda t, key=key: t.pop(key)))
        mutations += [
            ('top_extra', lambda t: t.update(extra=True)),
            ('reason_empty', lambda t: t.update(reason='')),
            ('verification_prefix', lambda t: t.update(required_verification='pending')),
        ]
        for key in self.text['issuance_record']:
            mutations.append((f'record_missing_{key}',
                lambda t, key=key: t['issuance_record'].pop(key)))
        mutations += [
            ('source_path_missing', lambda t: t['issuance_record']['source_candidate'].pop('relative_path')),
            ('source_file_digest', lambda t: t['issuance_record']['source_candidate'].update(file_sha256='f'*64)),
            ('source_derivation_digest', lambda t: t['issuance_record']['source_candidate'].update(derivation_sha256='f'*64)),
            ('ruling_order', lambda t: t['issuance_record']['rulings'].reverse()),
            ('ruling_id', lambda t: t['issuance_record']['rulings'][0].update(id='unknown')),
            ('ruling_count', lambda t: t['issuance_record']['rulings'].pop()),
            ('holds_present', lambda t: t['issuance_record'].update(holds=[])),
            ('hold_enforcement_present', lambda t: t['issuance_record'].update(hold_enforcement='none')),
            ('disclosures_empty', lambda t: t['issuance_record'].update(disclosures=[])),
            ('disclosure_order', lambda t: t['issuance_record']['disclosures'][0].update(id='D2')),
            ('disclosure_text_empty', lambda t: t['issuance_record']['disclosures'][0].update(text='')),
            ('disclosure_last_missing', lambda t: t['issuance_record']['disclosures'].pop()),
            ('disclosure_extra', lambda t: t['issuance_record']['disclosures'].append({'id': 'D11', 'text': 'extra'})),
            ('claim_meaning', lambda t: t['issuance_record'].update(claim_eligible_meaning=promote.CLAIM_ELIGIBLE_MEANING)),
            ('provenance_disclosure_id', lambda t: t['network_time_provenance'].update(disclosure_id='D2')),
            ('provenance_text', lambda t: t['network_time_provenance'].update(text='different')),
            ('provenance_extra', lambda t: t['network_time_provenance'].update(extra=True)),
            ('receipt_count', lambda t: t['network_time_provenance']['receipts'].pop()),
            ('receipt_session_missing', lambda t: t['network_time_provenance']['receipts'][0].pop('session_id')),
            ('receipt_session_unknown', lambda t: t['network_time_provenance']['receipts'][0].update(session_id='other')),
            ('receipt_session_duplicate', lambda t: t['network_time_provenance']['receipts'][1].update(
                session_id=t['network_time_provenance']['receipts'][0]['session_id'])),
            ('receipt_digest_wrong', lambda t: t['network_time_provenance']['receipts'][0].update(file_sha256='f'*64)),
            ('erratum_digest_wrong', lambda t: t['network_time_provenance']['erratum'].update(file_sha256='f'*64)),
        ]
        for key in self.text['network_time_provenance']:
            mutations.append((f'provenance_missing_{key}', lambda t, key=key: t['network_time_provenance'].pop(key)))
        for index in range(4):
            for field in ('relative_path', 'file_sha256'):
                mutations.append((f'ruling_{index}_missing_{field}', lambda t, index=index, field=field:
                    t['issuance_record']['rulings'][index].pop(field)))
            mutations.append((f'ruling_{index}_digest_malformed', lambda t, index=index:
                t['issuance_record']['rulings'][index].update(file_sha256='bad')))
            mutations.append((f'ruling_{index}_digest_wrong', lambda t, index=index:
                t['issuance_record']['rulings'][index].update(file_sha256='f'*64)))
        for surface in ('erratum', 'receipts'):
            for field in ('relative_path', 'file_sha256'):
                def remove(t, surface=surface, field=field):
                    item = t['network_time_provenance'][surface]
                    (item[0] if isinstance(item, list) else item).pop(field)
                mutations.append((f'{surface}_missing_{field}', remove))
        baseline = self.promote_text(self.text)
        for name, mutate in mutations:
            with self.subTest(clause=name):
                text = copy.deepcopy(self.text)
                mutate(text)
                with self.assertRaises(ValueError) as refused:
                    self.promote_text(text)
                self.assertEqual(self.promote_text(self.text), baseline)
                print(f'W1 RED {name}: {refused.exception}; RESTORED=PASS')

    def test_rev6_unknown_candidate_digest_red_then_restored(self):
        baseline = self.promote_text(self.text)
        with self.assertRaisesRegex(ValueError, 'candidate digest mismatch'):
            promote.promote(self.candidate_raw + b' ', json.dumps(self.text).encode())
        self.assertEqual(self.promote_text(self.text), baseline)
        print('W1 RED unknown_candidate_sha: candidate digest mismatch; RESTORED=PASS')

    def test_rev6_input_seal_stop_red_then_restored(self):
        baseline = self.promote_text(self.text)
        def drift(value):
            return 'f'*64 if value.get('artifact_role') == 'issued' else derivation_input_sha256(value)
        with patch.object(promote, 'derivation_input_sha256', side_effect=drift):
            with self.assertRaisesRegex(ValueError, 'STOP: derivation input seal differs from ruled digest'):
                self.promote_text(self.text)
        self.assertEqual(self.promote_text(self.text), baseline)
        print('W1 RED rev6_input_seal: STOP: derivation input seal differs from ruled digest; RESTORED=PASS')


if __name__ == "__main__":
    unittest.main()
