"""Independent WI-13 arithmetic and dispatch checks; issuance uses authenticated per-window records."""

import copy
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from joulewise import calibration_bracketing as bracketing
from scripts import issue_calibration_acceptance_generation as issuer
from tests.test_acc_25g83_rev5 import sealed_registration
from tests.verify_w1w2_disposition_sources import candidate_members


DECLARATION_PATH = Path(__file__).parent / "fixtures/epoch_bootstrap/revision6_declaration.json"


def declaration():
    """Synthetic seal of the exact E1 block; these pins are never authority."""
    source = json.loads(DECLARATION_PATH.read_text())
    def seal(item):
        if isinstance(item, dict):
            return {key: seal(value) for key, value in item.items()}
        if isinstance(item, list):
            return [seal(value) for value in item]
        return "a" * 64 if item == "TO BE PINNED AT SEAL" else item
    source = seal(source)
    source["pins"]["cap_cells"] = 1_000_000
    source["pins"]["ledger_head_pin_at_first_window"] = {"sequence": 0, "digest": "0" * 64}
    return source


def registration(block):
    return sealed_registration() + "\n# Revision 6 (sealed synthetic fixture)\n\n```json\n" + json.dumps(block) + "\n```\n"


def session(index, *, sequence=None, state="aborted", finalized=None):
    return SimpleNamespace(
        session_id=f"d079-epoch-25g83-r6-20261001T{index:04d}Z",
        capability_sequence=index if sequence is None else sequence,
        state=state, session_kind="derivation", declared_slots=tuple(range(12)),
        finalized_slots={} if finalized is None else finalized,
    )


class RevisionSixDeclarationTests(unittest.TestCase):
    def test_unfilled_and_malformed_pins_refuse_then_sealed_counterfactual_passes(self):
        block = declaration()
        self.assertEqual(issuer.revision_six_declaration(registration(block)), block)
        for mutation in (
            lambda b: b["pins"].update(cap_cells="TO BE PINNED AT SEAL"),
            lambda b: b["pins"].update(cap_cells="1000000"),
            lambda b: b["pins"].update(chain_sha256="bad"),
            lambda b: b["sessions"].pop("session_id_pattern"),
        ):
            broken = copy.deepcopy(block)
            mutation(broken)
            with self.subTest(broken=broken["pins"]["cap_cells"]):
                with self.assertRaises(issuer.PrepareRefusal):
                    issuer.revision_six_declaration(registration(broken))
                self.assertEqual(issuer.revision_six_declaration(registration(block)), block)

    def test_exact_session_set_order_prefix_pin_and_null_session_are_ledger_bound(self):
        first, second = session(1), session(2, state="finalized", finalized={"s1": object()})
        snapshot = SimpleNamespace(bracket_sessions=(second, first), receipts=())
        ids = (first.session_id, second.session_id)
        block = declaration()
        result = issuer.revision_six_sessions(snapshot, ids, block)
        self.assertEqual(result, (first, second))
        self.assertFalse(result[0].finalized_slots)  # retained, never omitted by operator
        for names in ((second.session_id,), ids + ("W1",), ids + (ids[0],)):
            with self.subTest(names=names):
                with self.assertRaises(issuer.PrepareRefusal):
                    issuer.revision_six_sessions(snapshot, names, block)
                self.assertEqual(issuer.revision_six_sessions(snapshot, ids, block), result)
        first.session_id = "W1"
        with self.assertRaisesRegex(issuer.PrepareRefusal, "mixture"):
            issuer.revision_six_sessions(snapshot, ("W1", second.session_id), block)
        first.session_id = ids[0]
        block["pins"]["ledger_head_pin_at_first_window"] = {"sequence": 1, "digest": "b" * 64}
        snapshot.receipts = ({"receipt_digest": "c" * 64},)
        with self.assertRaisesRegex(issuer.PrepareRefusal, "pin disagrees"):
            issuer.revision_six_sessions(snapshot, (second.session_id,), block)
        snapshot.receipts = ({"receipt_digest": "b" * 64},)
        self.assertEqual(issuer.revision_six_sessions(snapshot, (second.session_id,), block), (second,))

    def test_prospective_lane_refuses_before_predecessor_or_member_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registration.md"
            path.write_text(registration(declaration()))
            first = session(1)
            snapshot = SimpleNamespace(
                bracket_sessions=(first,), bracket_session_by_id={first.session_id: first},
                receipts=(), valid=True, refusal_reasons=(),
            )
            args = issuer.build_parser().parse_args([
                "prepare-candidate", "--preregistration", str(path),
                "--preregistration-sha256", hashlib.sha256(path.read_bytes()).hexdigest(),
                "--registration-session-id", first.session_id,
                "--d125-ruling", "synthetic D-125 reference", "--out", str(Path(tmp) / "candidate.json"),
            ])
            with patch.object(issuer, "load_calibration_ledger_snapshot", return_value=snapshot), patch.object(
                issuer, "_authenticated_predecessor", side_effect=AssertionError("predecessor read")
            ), patch.object(issuer, "_read_member_evidence", side_effect=AssertionError("member read")):
                with self.assertRaisesRegex(issuer.PrepareRefusal, "harvest/R9 records"):
                    issuer._prepare_candidate(args)
                for field in ("ed_ruling", "nights_ruling", "slot_count_ruling"):
                    setattr(args, field, "operator override")
                    with self.assertRaisesRegex(issuer.PrepareRefusal, "no command-line ruling"):
                        issuer._prepare_candidate(args)
                    setattr(args, field, None)
                with self.assertRaisesRegex(issuer.PrepareRefusal, "harvest/R9 records"):
                    issuer._prepare_candidate(args)
            self.assertFalse(Path(args.out).exists())


class RevisionSixArithmeticTests(unittest.TestCase):
    def test_disclosed_w1w2_worked_example(self):
        members = list(candidate_members().values())
        bindings = {m["member_id"]: m["source_directory"].split("/")[0] for m in members}
        record = issuer.within_window_prediction(members, bindings)
        stats = issuer._corpus_statistics(members)
        q99 = issuer.two_draw_prediction_lexeme(
            issuer.student_t_quantile("0.995", 11), stats["sample_sd_presentation_s"]["value"],
        )
        self.assertEqual((record["n"], record["K"], record["degrees_of_freedom"]), (12, 2, 10))
        self.assertEqual(round(float(q99), 5), .01902)
        self.assertEqual(round(float(record["prediction_99_within_window_two_draw_s"]), 5), .01854)
        self.assertEqual(record["quantile_proof"]["degrees_of_freedom"], 10)
        self.assertEqual(record["rule"],
                         "prediction_p_within_window_two_draw_s = t(p, n-K) * s_within_presentation_s * sqrt(2), "
                         "evaluated in binary64 and recorded as its shortest round-tripping decimal")
        self.assertNotEqual(record["rule"], issuer.TWO_DRAW_PREDICTION_RULE)

    def test_invented_worked_examples_and_decimal_pooling(self):
        with localcontext() as context:
            context.prec = issuer.DECIMAL_WORK_PRECISION
            for sd, expected in (("0.0030", .011596), ("0.0041", .015848)):
                # Twelve equally spaced members have mean zero and sum of
                # squares 572. Scale each of three windows to the stated SD.
                scale = Decimal(sd) * (Decimal(11) / Decimal(572)).sqrt()
                members = [{"member_id": f"w{w}s{i}", "b_fiducial_s": str(Decimal(".04") + scale * (2*i-11))}
                           for w in range(3) for i in range(12)]
                bindings = {m["member_id"]: m["member_id"].split("s")[0] for m in members}
                record = issuer.within_window_prediction(members, bindings)
                self.assertEqual((record["K"], record["degrees_of_freedom"]), (3, 33))
                self.assertEqual(Decimal(record["s_within_presentation_s"]["value"]), Decimal(sd))
                self.assertEqual(round(float(record["prediction_99_within_window_two_draw_s"]), 6), expected)
        q99 = issuer.two_draw_prediction_lexeme(issuer.student_t_quantile("0.995", 35), "0.0040")
        self.assertEqual(round(float(q99), 6), .015408)

    def test_one_window_matches_plain_q99_and_missing_binding_refuses(self):
        members = [{"member_id": str(i), "b_fiducial_s": str(Decimal(".02") + Decimal(i)/1000)}
                   for i in range(12)]
        bindings = {m["member_id"]: "one-window" for m in members}
        record = issuer.within_window_prediction(members, bindings)
        sd = issuer._corpus_statistics(members)["sample_sd_presentation_s"]["value"]
        self.assertEqual(record["s_within_presentation_s"]["value"], sd)
        self.assertEqual(record["prediction_99_within_window_two_draw_s"],
                         issuer.two_draw_prediction_lexeme(issuer.student_t_quantile("0.995", 11), sd))
        missing = dict(bindings)
        missing.pop("0")
        with self.assertRaisesRegex(issuer.PrepareRefusal, "one session binding"):
            issuer.within_window_prediction(members, missing)
        self.assertEqual(issuer.within_window_prediction(members, bindings), record)

    def test_fourth_term_exact_equation_and_all_registered_generations(self):
        for row in bracketing._D102_GENERATION_DERIVATIONS.values():
            self.assertTrue(bracketing._registered_generation_row_is_complete(row))
        self.assertEqual(len(bracketing._D102_GENERATION_DERIVATIONS), 8)
        row = copy.deepcopy(bracketing._D102_N17_DERIVATION)
        row.update(corpus_n=12, prior_prefix_mode="import_plus_live",
                   screen_rule=bracketing.SCREEN_RULE_FLOORED_RANGE_ENVELOPE,
                   registration_session_ids=(session(1).session_id, session(2).session_id),
                   d125_ruling="synthetic", registration_revision=6,
                   predecessor_acceptance_id=bracketing.ANCHOR_V3_R7_ACCEPTANCE_ID,
                   predecessor_ceiling_s="0.010164834757777545",
                   prediction_99_two_draw_s="0.015408",
                   prediction_99_within_window_two_draw_s="0.015848")
        row["operatives"].update(bracket_screen_s="0.010818", maximum_budgetable_drift_s="0.015848",
                                max_budgetable_excess_s="0.005030")
        validate = lambda r: bracketing._registered_generation_row_is_complete(r, revision_six=True)
        self.assertTrue(validate(row))
        for bad in (None, "bad", "NaN", "-1"):
            broken = copy.deepcopy(row)
            broken["prediction_99_within_window_two_draw_s"] = bad
            self.assertFalse(validate(broken))
            self.assertTrue(validate(row))
        for ceiling in ("0.015408", "0.020000"):
            broken = copy.deepcopy(row)
            broken["operatives"]["maximum_budgetable_drift_s"] = ceiling
            self.assertFalse(validate(broken))
            self.assertTrue(validate(row))
        # The same row under Revision 5 obeys the old three-term equation.
        old = copy.deepcopy(row)
        old["registration_revision"] = 5
        old.pop("prediction_99_within_window_two_draw_s")
        old["operatives"]["maximum_budgetable_drift_s"] = "0.015408"
        self.assertTrue(bracketing._registered_generation_row_is_complete(old, revision_five=True))


class RevisionSixConsumerTests(unittest.TestCase):
    def fixture(self, root, **kwargs):
        from tests.fixtures.epoch_bootstrap.revision6 import build
        return build(root, **kwargs)

    def prepare(self, f):
        with patch.object(issuer, 'load_calibration_ledger_snapshot', return_value=f['snapshot']), patch.object(
                issuer, '_authenticated_predecessor', return_value=f['predecessor']):
            try:
                return issuer._prepare_candidate(f['args'])
            except issuer.PrepareRefusal as error:
                if 'campaign R9 bytes are not committed' not in str(error):
                    raise
                from tests.fixtures.epoch_bootstrap.revision6 import commit
                record = Path(f['args'].out).with_name('r9_campaign.json')
                target = f['fixture']['root'] / 'r9_campaign.json'
                target.write_bytes(record.read_bytes())
                commit(f['fixture']['root'])
                return issuer._prepare_candidate(f['args'])

    def records(self, f):
        return issuer.revision_six_records(f['paths'], f['snapshot'].bracket_sessions, f['block'],
                                          repo_root=f['fixture']['root'])

    def replay(self, f, records=None, adverse=None):
        return issuer.revision_six_count_replay(f['snapshot'].bracket_sessions,
            self.records(f) if records is None else records, f['block'], set() if adverse is None else adverse)

    def test_full_candidate_four_term_ceiling_both_decisions_and_serial_pairs(self):
        from tests.fixtures.epoch_bootstrap.build import Slot
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case', slots=[Slot(str(Decimal('.02')+Decimal(i)/10000)) for i in range(12)],
                second_slots=[Slot(str(Decimal('.0201')+Decimal(i)/10000)) for i in range(12)])
            candidate = self.prepare(f)
            self.assertEqual(candidate['acceptance_id'], 'd079_calibration_acceptance_v2_n24_25g83_r2')
            row = candidate['registered_generation_row']
            self.assertEqual(row['registration_revision'], 6)
            self.assertEqual(candidate['derivation_notes']['revision6_count_replay']['decision'], 'CLOSE_AND_DERIVE')
            source = candidate['decimal_derivation']['source_statistics']
            within = candidate['decimal_derivation']['within_window_prediction_derivation']
            self.assertEqual((within['n'], within['K'], within['degrees_of_freedom']), (24, 2, 22))
            self.assertEqual(Decimal(row['operatives']['maximum_budgetable_drift_s']), max(
                Decimal(row['predecessor_ceiling_s']), Decimal(source['prediction_99_two_draw_s']),
                Decimal(source['prediction_99_within_window_two_draw_s']), Decimal(row['operatives']['bracket_screen_s'])))
            self.assertEqual(candidate['prior_observation_set']['disposing_decision_ids'],
                             sorted(f['block']['disposing_decision_ids_required']))
            diagnostics = candidate['derivation_notes']['sampling_dependence']
            self.assertEqual(diagnostics['rho1_pairs'], 22)
            self.assertEqual(Decimal(diagnostics['rho1']), Decimal(1))
            self.assertEqual(candidate['derivation_sha256'], issuer.derivation_sha256(candidate))
            self.assertEqual(candidate['derivation_input_sha256'], issuer.derivation_input_sha256(candidate))
            f['args'].acceptance_id = 'd079_calibration_acceptance_v2_n12_25g83_r1'
            with self.assertRaisesRegex(issuer.PrepareRefusal, 'identifier'):
                self.prepare(f)

    def test_campaign_record_is_blind_committed_before_B_and_pins_are_bytes(self):
        from tests.fixtures.epoch_bootstrap.revision6 import commit
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            with patch.object(issuer, 'load_calibration_ledger_snapshot', return_value=f['snapshot']), patch.object(
                    issuer, '_read_member_evidence', side_effect=AssertionError('B read')):
                with self.assertRaisesRegex(issuer.PrepareRefusal, 'campaign R9 bytes are not committed'):
                    issuer._prepare_candidate(f['args'])
            path = Path(f['args'].out).with_name('r9_campaign.json')
            record = json.loads(path.read_bytes())
            self.assertEqual(len(record['clauses']), 5)
            self.assertTrue(all(record['clauses'].values()))
            self.assertEqual([len(w['slots']) for w in record['sessions']], [12, 12])
            self.assertEqual(record['cap_rule_text_sha256'], f['block']['pins']['cap_rule_text_sha256'])
            self.assertNotIn('b_fiducial', path.read_text())
            self.assertFalse(Path(f['args'].out).exists())
            for name, pin_path in record['pinned_files'].items():
                file = Path(pin_path['path'])
                original = file.read_bytes()
                file.write_bytes(original + b'changed')
                with self.subTest(pin=name), patch.object(issuer, 'load_calibration_ledger_snapshot', return_value=f['snapshot']), patch.object(
                        issuer, '_read_member_evidence', side_effect=AssertionError('B read')):
                    with self.assertRaisesRegex(issuer.PrepareRefusal, 'file digest disagrees'):
                        issuer._prepare_candidate(f['args'])
                file.write_bytes(original)
            self.assertEqual(self.prepare(f)['derivation_corpus']['n'], 24)

    def test_no_recording_is_listed_and_not_counted_or_a_stop(self):
        from dataclasses import replace
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            sessions = f['snapshot'].bracket_sessions
            records = self.records(f)
            first = sessions[0]
            slot, row = next(iter(first.finalized_slots.items()))
            hashes = dict(row.artifact_sha256)
            hashes.pop('raw/powermetrics.plist')
            slots = dict(first.finalized_slots)
            slots[slot] = replace(row, artifact_sha256=hashes, disposition='ordinary-invalid')
            first = replace(first, finalized_slots=slots)
            r9 = records[first.session_id]['r9']
            r9['captures'][0].update(has_recording=False, cells=None, ratio=None, median_frame_ms=None,
                median_frame_reported=False, cap_trigger=None, counted=False, disposition='ordinary-invalid',
                ledger_reason='ordinary-invalid')
            r9.update(counted=11, valid=11)
            result = issuer.revision_six_count_replay([first], records, f['block'], set())
            self.assertEqual((result['decision'], result['counted']), ('NEXT_WINDOW', 11))
            self.assertEqual(result['sessions'][0]['stops'], [])
            r9['captures'][0]['cells'] = 1
            with self.assertRaises(issuer.PrepareRefusal):
                issuer.revision_six_count_replay([first], records, f['block'], set())

    def test_revision6_misnamed_session_cannot_dispatch_as_revision5(self):
        from dataclasses import replace
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            first, second = f['snapshot'].bracket_sessions
            misnamed = replace(first, session_id='misnamed-revision6-window')
            f['snapshot'] = replace(f['snapshot'], bracket_sessions=(misnamed, second))
            f['args'].registration_session_id = [misnamed.session_id, second.session_id]
            with patch.object(issuer, 'revision_six_records', side_effect=AssertionError('records read')):
                with self.assertRaisesRegex(issuer.PrepareRefusal, 'pattern mismatch'):
                    self.prepare(f)

    def test_digest_authentication_precedes_parsing_and_commit_is_required(self):
        from tests.fixtures.epoch_bootstrap.revision6 import rewrite_record, commit
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            self.assertEqual(self.replay(f)['decision'], 'CLOSE_AND_DERIVE')
            rewrite_record(f['paths'][0], 'r9_window', lambda r: r.update(counted=11), refresh_digest=False)
            with self.assertRaisesRegex(issuer.PrepareRefusal, 'sha256 disagreement'):
                self.records(f)
            rewrite_record(f['paths'][0], 'r9_window', lambda r: r.update(counted=12))
            # Identical bytes restore the original committed state.
            self.assertEqual(self.replay(f)['decision'], 'CLOSE_AND_DERIVE')
            rewrite_record(f['paths'][0], 'r9_window', lambda r: r.update(extra='uncommitted'))
            with self.assertRaisesRegex(issuer.PrepareRefusal, 'not committed'):
                self.records(f)
            commit(f['fixture']['root'])
            self.assertEqual(self.replay(f)['decision'], 'CLOSE_AND_DERIVE')

    def test_each_start_entry_pin_exit_dwell_and_off_receipt_is_authenticated(self):
        from tests.fixtures.epoch_bootstrap.revision6 import rewrite_record, canonical
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            h = json.loads(f['paths'][0].read_bytes())
            path = Path(h['custody_root'])/h['start_conditions']['path']
            original = path.read_bytes()
            original_harvest = f['paths'][0].read_bytes()
            mutations = [lambda r, key=key: r['evidence'].pop(key) for key in json.loads(original)['evidence']]
            mutations += [lambda r: r['evidence']['g_clean_dwell'].update(script_sha256='f'*64),
                          lambda r: r['evidence']['g_clean_dwell'].update(exit=1),
                          lambda r: r['evidence']['g_clean_dwell'].update(passed_epoch_s=3e9),
                          lambda r: r.update(boot_id='different-boot'),
                          lambda r: r.update(result='refused', refusal_reason='driver refused')]
            for mutate in mutations:
                with self.subTest(mutate=mutate):
                    rewrite_record(f['paths'][0], 'start_conditions', mutate)
                    with self.assertRaises(issuer.PrepareRefusal):
                        self.records(f)
                    path.write_bytes(original)
                    f['paths'][0].write_bytes(original_harvest)
                    self.assertEqual(self.replay(f)['decision'], 'CLOSE_AND_DERIVE')
            dwell_path = Path(h['custody_root'])/'night/prewindow_check.out'
            dwell_path.write_bytes(b'continuous clean dwell 599/600s (check 20)\n')
            rewrite_record(f['paths'][0], 'start_conditions', lambda r: r['evidence']['g_clean_dwell'].update(
                sha256=hashlib.sha256(dwell_path.read_bytes()).hexdigest()))
            with self.assertRaisesRegex(issuer.PrepareRefusal, 'below 600'):
                self.records(f)

    def test_all_eight_stops_and_adverse_r9_campaign_void_distinction(self):
        from tests.fixtures.epoch_bootstrap.build import Slot
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            records = self.records(f)
            sessions = f['snapshot'].bracket_sessions
            first = sessions[0].session_id
            mutations = {
                'STOP-R9-CELL': lambda r: r['captures'][0].update(cap_trigger='evaluated_cell_budget'),
                'STOP-R9-DEADLINE': lambda r: r['captures'][0].update(cap_trigger='wall_deadline'),
                'STOP-R9-RATIO': lambda r: r['captures'][0].update(cells=500001, ratio=.500001),
                'STOP-R9-FRAME': lambda r: (r['captures'][0].update(median_frame_reported=False,
                    median_frame_ms=None, counted=False), r.update(counted=11)),
                'STOP-CADENCE': lambda r: ([c.update(median_frame_ms=151, counted=False) for c in r['captures']], r.update(counted=0)),
            }
            for stop, mutate in mutations.items():
                broken = copy.deepcopy(records)
                mutate(broken[first]['r9'])
                with self.subTest(stop=stop):
                    # First-window stop must refuse a second session and never
                    # reach the B-reading member selection seam.
                    with patch.object(issuer, '_read_member_evidence', side_effect=AssertionError('B read')):
                        result = issuer.revision_six_count_replay(sessions[:1], broken, f['block'], set())
                    self.assertIn(stop, result['sessions'][0]['stops'])
                    self.assertEqual(result['decision'], 'STOP_TO_REVIEW')
                    self.assertEqual(result['sessions'][0]['campaign_void'], stop in {
                        'STOP-R9-CELL', 'STOP-R9-DEADLINE', 'STOP-R9-RATIO'})
            # Futility from ledger dispositions, never the record's declaration.
            weak = self.fixture(Path(tmp)/'weak', slots=[Slot('0.025', disposition='ordinary-invalid') for _ in range(7)] +
                                [Slot('0.025') for _ in range(5)])
            result = issuer.revision_six_count_replay(weak['snapshot'].bracket_sessions[:1], self.records(weak), weak['block'], set())
            self.assertIn('STOP-FUTILITY', result['sessions'][0]['stops'])
            adverse_records = copy.deepcopy(records)
            for rec in adverse_records.values():
                rec['r9'].update(counted=0, valid=0)
                for capture in rec['r9']['captures']:
                    capture['counted'] = False
            result = self.replay(f, adverse_records, {s.session_id for s in sessions})
            self.assertIn('STOP-BATTERY-SECOND', result['sessions'][1]['stops'])
            adverse_records[first]['r9']['captures'][0].update(cells=500001, ratio=.500001, median_frame_ms=200)
            result = issuer.revision_six_count_replay(sessions[:1], adverse_records, f['block'], {first})
            self.assertIn('STOP-R9-RATIO', result['sessions'][0]['stops'])
            self.assertTrue(result['sessions'][0]['campaign_void'])
            null = self.fixture(Path(tmp)/'null', null_first=True)
            null_records = self.records(null)
            from dataclasses import replace
            first_null = null['snapshot'].bracket_sessions[0]
            next_null = replace(first_null, session_id=null['snapshot'].bracket_sessions[1].session_id)
            null_records[next_null.session_id] = copy.deepcopy(null_records[first_null.session_id])
            null_records[next_null.session_id]['r9']['session_id'] = next_null.session_id
            result = issuer.revision_six_count_replay((first_null, next_null), null_records, null['block'], set())
            self.assertIn('STOP-NULL-REPEAT', result['sessions'][1]['stops'])
            self.assertTrue(all(row['window_label'] is None for row in result['sessions']))

    def test_count_triggers_exhaustion_and_session_after_close(self):
        from tests.fixtures.epoch_bootstrap.build import Slot
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'third', slots=[Slot('0.025') for _ in range(12)],
                second_slots=[Slot('0.026') for _ in range(12)], third_slots=[Slot('0.027') for _ in range(12)])
            records = self.records(f)
            with self.assertRaisesRegex(issuer.PrepareRefusal, 'session exists after CLOSE_AND_DERIVE'):
                self.replay(f, records)
            first = f['snapshot'].bracket_sessions[0].session_id
            records[first]['r9']['captures'][0].update(cells=0, ratio=0, counted=False)
            records[first]['r9']['counted'] = 11
            result = self.replay(f, records)
            self.assertEqual([r['decision'] for r in result['sessions']], ['NEXT_WINDOW','NEXT_WINDOW','CLOSE_AND_DERIVE'])
            for rec in records.values():
                for c in rec['r9']['captures']:
                    c.update(cells=0, ratio=0, counted=False)
                rec['r9']['counted'] = 0
            result = self.replay(f, records)
            self.assertEqual(result['decision'], 'R9_COUNT_NOT_REACHED_TO_REVIEW')
            # 6 valid in C1 avoids futility, but only 11 resolved members in all.
            unresolved = [Slot('0.025', unresolved_detail='affine_clock_fit_empty') for _ in range(12)]
            short = self.fixture(Path(tmp)/'short', slots=[Slot('0.025') for _ in range(6)] + unresolved[:6],
                second_slots=[Slot('0.026') for _ in range(5)] + unresolved[:7], third_slots=unresolved)
            result = self.replay(short)
            self.assertEqual(result['decision'], 'MEMBERS_SHORT_TO_REVIEW')
            self.assertEqual(result['members'], 11)
            with patch.object(issuer, '_select_members', side_effect=AssertionError('B read')):
                with self.assertRaisesRegex(issuer.PrepareRefusal, 'MEMBERS_SHORT_TO_REVIEW'):
                    self.prepare(short)

    def test_null_does_not_count_and_terminal_gate_precedes_record_or_B_reads(self):
        from tests.fixtures.epoch_bootstrap.build import Slot
        from dataclasses import replace
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case', null_first=True, third_slots=[Slot('0.027') for _ in range(12)])
            result = self.replay(f)
            self.assertEqual([row['window_label'] for row in result['sessions']], [None, 'C1', 'C2'])
            self.assertEqual(result['counted'], 24)
            first = replace(f['snapshot'].bracket_sessions[0], state='finalized')
            terminal_null = issuer.revision_six_count_replay([first], self.records(f), f['block'], set())
            self.assertEqual(terminal_null['decision'], 'NEXT_WINDOW')
            self.assertEqual(self.prepare(f)['derivation_corpus']['n'], 24)
            last = f['snapshot'].bracket_sessions[-1]
            opened = replace(last, state='open')
            f['snapshot'] = replace(f['snapshot'], bracket_sessions=(*f['snapshot'].bracket_sessions[:-1], opened))
            with patch.object(issuer, 'revision_six_records', side_effect=AssertionError('record read')), patch.object(
                    issuer, '_select_members', side_effect=AssertionError('B read')):
                with self.assertRaisesRegex(issuer.PrepareRefusal, 'not terminal'):
                    self.prepare(f)

    def test_r9_count_valid_identity_coverage_and_raw_flag_disagreement_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            records = self.records(f)
            first = f['snapshot'].bracket_sessions[0].session_id
            mutations = [lambda r: r.update(counted=11), lambda r: r.update(valid=11),
                lambda r: r['captures'].pop(), lambda r: r['captures'].append(dict(r['captures'][0])),
                lambda r: r['captures'][0].update(content_id='f'*64),
                lambda r: r['captures'][0].update(has_recording=False),
                lambda r: r['captures'][0].update(ratio=.2),
                lambda r: r['captures'][0].update(counted=False)]
            for mutate in mutations:
                broken = copy.deepcopy(records)
                mutate(broken[first]['r9'])
                with self.subTest(mutation=mutate), self.assertRaises(issuer.PrepareRefusal):
                    self.replay(f, broken)
                self.assertEqual(self.replay(f, records)['decision'], 'CLOSE_AND_DERIVE')

    def test_validator_recomputes_within_record_and_refuses_value_df_rule_and_bindings(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            candidate = self.prepare(f)
            issued = copy.deepcopy(candidate)
            issued.pop('candidate_not_issued')
            issued['artifact_role'] = 'issued'
            issued['issuance'] = {'status':'issued','claim_eligible':True}
            issued['backfill_candidate'].update(status='issued', production_issuance_blocked=False)
            issued['derivation_sha256'] = issuer.derivation_sha256(issued)
            row = issuer.generation_row_for_registry(issued['registered_generation_row'])
            with patch.dict(bracketing._D102_GENERATION_DERIVATIONS, {
                issued['acceptance_id']: row, 'd079_calibration_acceptance_v2_n17_r8': bracketing._D102_N17_DERIVATION}), patch.dict(
                    bracketing.ISSUED_ACCEPTANCE_REGISTRY, {issued['acceptance_id']: {'file_sha256':'0'*64}}):
                self.assertTrue(bracketing._valid_acceptance_bound(issued))
                import builtins
                original_import = builtins.__import__
                def unavailable(name, *args, **kwargs):
                    if name == 'scripts.issue_calibration_acceptance_generation':
                        raise ImportError('issuer unavailable')
                    return original_import(name, *args, **kwargs)
                with patch.object(builtins, '__import__', side_effect=unavailable):
                    self.assertFalse(bracketing._valid_acceptance_bound(issued))
                mutations = [lambda p: p['decimal_derivation']['within_window_prediction_derivation'].update(degrees_of_freedom=23),
                    lambda p: p['decimal_derivation']['within_window_prediction_derivation'].update(rule=issuer.TWO_DRAW_PREDICTION_RULE),
                    lambda p: p['decimal_derivation']['within_window_prediction_derivation'].update(prediction_99_within_window_two_draw_s='0.01'),
                    lambda p: p['decimal_derivation']['within_window_prediction_derivation']['quantile_proof'].update(degrees_of_freedom=23),
                    lambda p: [row.update(session_id=f"separate-{i}") for i, row in enumerate(p['prior_observation_set']['observations'])
                               if row['session_id'].startswith('d079-epoch-25g83-r6-')]]
                for mutate in mutations:
                    broken = copy.deepcopy(issued)
                    mutate(broken)
                    broken['derivation_sha256'] = issuer.derivation_sha256(broken)
                    with self.subTest(mutate=mutate):
                        self.assertFalse(bracketing._valid_acceptance_bound(broken))
                    self.assertTrue(bracketing._valid_acceptance_bound(issued))

    def test_blind_dry_run_uses_count_rule_and_never_member_value_seam(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            with patch.object(issuer, '_read_member_evidence', side_effect=AssertionError('B read')):
                code, lines = issuer.revision_six_dry_run(f['snapshot'], f['args'].registration_session_id,
                    f['block'], f['paths'], repo_root=f['fixture']['root'],
                    preregistration_sha256=f['args'].preregistration_sha256)
            self.assertEqual(code, 0)
            self.assertIn('counted_total=24 members_total=24 decision=CLOSE_AND_DERIVE', lines)
            self.assertFalse(any('b_fiducial' in line or 'screen' in line for line in lines))

    def test_adverse_window_and_frame_outside_range_are_disclosed_exclusions(self):
        from tests.fixtures.epoch_bootstrap.build import Slot
        from tests.fixtures.epoch_bootstrap.revision6 import rewrite_record, commit
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'adverse', slots=[Slot('0.025', battery_mode='charging') for _ in range(12)],
                third_slots=[Slot('0.027') for _ in range(12)])
            first = f['args'].registration_session_id.pop(0)
            f['args'].battery_confounded_session_id = [first]
            candidate = self.prepare(f)
            self.assertEqual(candidate['derivation_corpus']['n'], 24)
            excluded = candidate['derivation_notes']['excluded_members']
            self.assertEqual(len(excluded), 12)
            self.assertEqual({row['reason'] for row in excluded}, {'adverse_window'})
            self.assertEqual(candidate['registered_generation_row']['registration_session_ids'],
                             [s.session_id for s in f['snapshot'].bracket_sessions])
            windows = candidate['derivation_notes']['sampling_dependence']['windows']
            self.assertEqual([w['member_count'] for w in windows], [0, 12, 12])
            self.assertIsNotNone(windows[0]['window_end'])
            harvest = json.loads(f['paths'][0].read_bytes())
            harvest['window_end'] = None
            from tests.fixtures.epoch_bootstrap.revision6 import canonical
            f['paths'][0].write_bytes(canonical(harvest))
            with self.assertRaisesRegex(issuer.PrepareRefusal, 'window end'):
                self.prepare(f)
            g = self.fixture(Path(tmp)/'frames', third_slots=[Slot('0.027') for _ in range(12)])
            rewrite_record(g['paths'][0], 'r9_window', lambda r: (r['captures'][0].update(
                median_frame_ms=99, counted=False), r.update(counted=11)))
            commit(g['fixture']['root'])
            candidate = self.prepare(g)
            self.assertEqual(candidate['derivation_corpus']['n'], 35)
            self.assertEqual([row['reason'] for row in candidate['derivation_notes']['excluded_members']],
                             ['frame_out_of_covered_range'])

    def test_identity_p8_registry_and_inset_refusals(self):
        from tests.fixtures.epoch_bootstrap.build import Slot
        from dataclasses import replace
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            original = f['predecessor']['acceptance_id']
            f['predecessor']['acceptance_id'] = bracketing.ANCHOR_V3_R7_ACCEPTANCE_ID
            with self.assertRaisesRegex(issuer.PrepareRefusal, 'P8 predecessor identity'):
                self.prepare(f)
            f['predecessor']['acceptance_id'] = original
            original_snapshot = f['snapshot']
            foreign = replace(original_snapshot.observations[0], attempt_id='foreign', bracket_session_id='unregistered', content_id='f'*64)
            f['snapshot'] = replace(original_snapshot, observations=(*original_snapshot.observations, foreign))
            # Authentication requires a terminal owner or refuses this foreign
            # row before any candidate can be produced.
            with self.assertRaises(issuer.PrepareRefusal):
                self.prepare(f)
            f['snapshot'] = original_snapshot
            self.assertEqual(self.prepare(f)['derivation_corpus']['n'], 24)
            wide = self.fixture(Path(tmp)/'wide', slots=[Slot('0.251') for _ in range(12)])
            with self.assertRaisesRegex(issuer.PrepareRefusal, 'PLATEAU_INSET'):
                self.prepare(wide)

    def test_sealed_letter_mapping_overrides_sketch_evidence_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            harvest = json.loads(f['paths'][0].read_bytes())
            root = Path(harvest['custody_root'])
            start = json.loads((root/harvest['start_conditions']['path']).read_bytes())
            start['evidence']['b_any_blind_name'] = start['evidence'].pop('b_blind_checks')
            start['evidence']['f_any_off_name'] = start['evidence'].pop('f_network_time_off_receipt')
            issuer.revision_six_start_conditions(start, root, f['block'])
            start['evidence']['f_any_off_name']['sha256'] = 'f'*64
            with self.assertRaisesRegex(issuer.PrepareRefusal, 'sha256 disagreement'):
                issuer.revision_six_start_conditions(start, root, f['block'])

    def test_window_timing_uses_admission_and_exit_in_ledger_order(self):
        from tests.fixtures.epoch_bootstrap.revision6 import rewrite_record, commit
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            # Write times deliberately differ from admission, and harvest
            # arguments arrive out of order. Neither determines window timing.
            rewrite_record(f['paths'][0], 'start_conditions', lambda r: r.update(
                written_epoch_s=r['written_epoch_s'] + 123, written_monotonic_s=1.0))
            commit(f['fixture']['root'])
            f['args'].harvest_record.reverse()
            candidate = self.prepare(f)
            windows = candidate['derivation_notes']['sampling_dependence']['windows']
            first, second = windows
            self.assertEqual([w['session_id'] for w in windows],
                             [s.session_id for s in f['snapshot'].bracket_sessions])
            harvest = json.loads(f['paths'][0].read_bytes())
            root = Path(harvest['custody_root'])
            start = json.loads((root/'night/start_conditions.json').read_bytes())
            self.assertEqual(first['window_start']['epoch_s'], start['chain_start_admitted']['epoch_s'])
            self.assertEqual(first['window_end']['epoch_s'], harvest['window_end']['epoch_s'])
            self.assertIsNone(first['start_to_start_interval'])
            self.assertIsNone(first['inter_window_gap'])
            for key, earlier in [('start_to_start_interval', first['window_start']),
                                 ('inter_window_gap', first['window_end'])]:
                delta = second[key]
                self.assertEqual(delta['wall_s'], second['window_start']['epoch_s'] - earlier['epoch_s'])
                self.assertEqual(delta['monotonic_s'], second['window_start']['monotonic_s'] - earlier['monotonic_s'])
                self.assertEqual(delta['clock_basis'], 'wall_and_monotonic')
                self.assertEqual(delta['wall_minus_monotonic_s'], 0)
            self.assertNotIn('start_condition_write_interval_s', first)

    def test_missing_null_and_malformed_window_timing_refuses_before_B(self):
        from tests.fixtures.epoch_bootstrap.revision6 import canonical, rewrite_record
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            path = f['paths'][0]
            h = json.loads(path.read_bytes())
            start_path = Path(h['custody_root'])/'night/start_conditions.json'
            original_start, original_harvest = start_path.read_bytes(), path.read_bytes()
            mutations = [('start', lambda r: r.pop('chain_start_admitted')),
                ('start', lambda r: r.update(chain_start_admitted=None)),
                ('harvest', lambda r: r.pop('window_end')),
                ('harvest', lambda r: r.update(window_end=None)),
                ('harvest', lambda r: r.pop('boot_id')),
                ('harvest', lambda r: r['window_end'].pop('source')),
                ('harvest', lambda r: r['window_end']['source'].update(path='night/other.json')),
                ('harvest', lambda r: r['window_end']['source'].update(sha256='f'*64)),
                ('harvest', lambda r: r['window_end'].update(epoch_s=r['window_end']['epoch_s']+1)),
                ('harvest', lambda r: r['window_end'].update(monotonic_s=r['window_end']['monotonic_s']+1))]
            for location in ('start', 'harvest'):
                key = 'chain_start_admitted' if location == 'start' else 'window_end'
                for clock in ('epoch_s', 'monotonic_s'):
                    mutations += [(location, lambda r, k=key, c=clock: r[k].pop(c))]
                    for invalid in (None, True, '1000', float('inf'), float('nan'), 10**400):
                        # JSON deliberately permits nonfinite fixture values:
                        # the consumer must fail closed even on those bytes.
                        mutations += [(location, lambda r, k=key, c=clock, v=invalid: r[k].update({c: v}))]
            for location, mutate in mutations:
                with self.subTest(location=location, mutate=mutate):
                    if location == 'start':
                        record = json.loads(original_start)
                        mutate(record)
                        raw = (json.dumps(record, sort_keys=True) + '\n').encode()
                        start_path.write_bytes(raw)
                        changed = copy.deepcopy(h)
                        changed['start_conditions']['sha256'] = hashlib.sha256(raw).hexdigest()
                    else:
                        changed = copy.deepcopy(h)
                        mutate(changed)
                    path.write_text(json.dumps(changed, sort_keys=True) + '\n')
                    with patch.object(issuer, '_revision_six_committed', return_value='a'*40), patch.object(
                            issuer, '_read_member_evidence', side_effect=AssertionError('B read')):
                        with self.assertRaises(issuer.PrepareRefusal):
                            self.prepare(f)
                    start_path.write_bytes(original_start)
                    path.write_bytes(original_harvest)
            # Missing/null timing is permitted on a true null session.
            null = self.fixture(Path(tmp)/'null', null_first=True)
            rewrite_record(null['paths'][0], 'start_conditions', lambda r: r.pop('chain_start_admitted'))
            changed = json.loads(null['paths'][0].read_bytes())
            changed.pop('window_end')
            null['paths'][0].write_bytes(canonical(changed))
            records = issuer.revision_six_records(null['paths'], null['snapshot'].bracket_sessions,
                null['block'], repo_root=null['fixture']['root'], require_committed=False)
            self.assertIsNone(records[null['snapshot'].bracket_sessions[0].session_id]['timing'])
            self.assertIsNone(records[null['snapshot'].bracket_sessions[1].session_id]['timing']['inter_window_gap'])

    def test_cross_reboot_uses_wall_clock_and_explicit_note(self):
        from tests.fixtures.epoch_bootstrap.revision6 import canonical, rewrite_record, commit
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            path = f['paths'][1]
            h = json.loads(path.read_bytes())
            root = Path(h['custody_root'])
            off_path = root/'night/network_time_off.json'
            off = json.loads(off_path.read_bytes())
            off.update(boot_id='rebooted', monotonic_s=1000.0)
            off_path.write_bytes(canonical(off))
            def reboot_start(r):
                r.update(boot_id='rebooted', written_monotonic_s=2020.0)
                r['chain_start_admitted']['monotonic_s'] = 2000.0
                r['evidence']['f_network_time_off_receipt']['sha256'] = hashlib.sha256(off_path.read_bytes()).hexdigest()
            rewrite_record(path, 'start_conditions', reboot_start)
            h = json.loads(path.read_bytes())
            h['boot_id'] = 'rebooted'
            h['window_end']['monotonic_s'] = 9200.0
            exited_path = root/'night/chain.exited'
            exited = json.loads(exited_path.read_bytes())
            exited['monotonic_ns'] = 9_200_000_000_000
            exited_path.write_bytes(canonical(exited))
            h['window_end']['source']['sha256'] = hashlib.sha256(exited_path.read_bytes()).hexdigest()
            path.write_bytes(canonical(h))
            commit(f['fixture']['root'])
            windows = self.prepare(f)['derivation_notes']['sampling_dependence']['windows']
            for key, earlier in [('start_to_start_interval', windows[0]['window_start']),
                                 ('inter_window_gap', windows[0]['window_end'])]:
                delta = windows[1][key]
                self.assertEqual(delta['wall_s'], windows[1]['window_start']['epoch_s']-earlier['epoch_s'])
                self.assertIsNone(delta['monotonic_s'])
                self.assertIsNone(delta['wall_minus_monotonic_s'])
                self.assertEqual(delta['clock_basis'], 'wall_only_across_reboot')
                self.assertIn('Across a reboot: wall clock used', delta['note'])

    def test_both_clocks_report_drift_and_refuse_reversed_order(self):
        earlier = {'epoch_s': 1000.0, 'monotonic_s': 20.0, 'boot_id': 'same'}
        later = {'epoch_s': 1101.0, 'monotonic_s': 120.0, 'boot_id': 'same'}
        result = issuer._revision_six_elapsed(earlier, later, 'gap')
        self.assertEqual((result['wall_s'], result['monotonic_s'], result['wall_minus_monotonic_s']), (101, 100, 1))
        for clock in ('epoch_s', 'monotonic_s'):
            broken = dict(later)
            broken[clock] = earlier[clock]-1
            with self.assertRaisesRegex(issuer.PrepareRefusal, 'reversed'):
                issuer._revision_six_elapsed(earlier, broken, 'gap')

    def test_settle_and_dwell_are_measured_at_admission(self):
        from tests.fixtures.epoch_bootstrap.revision6 import rewrite_record
        with tempfile.TemporaryDirectory() as tmp:
            f = self.fixture(Path(tmp)/'case')
            for clock in ('epoch_s', 'monotonic_s'):
                def early(r):
                    r['chain_start_admitted'][clock] -= 401
                rewrite_record(f['paths'][0], 'start_conditions', early)
                with self.assertRaises(issuer.PrepareRefusal):
                    self.records(f)
                rewrite_record(f['paths'][0], 'start_conditions', lambda r: r['chain_start_admitted'].update(
                    {clock: r['chain_start_admitted'][clock]+401}))


if __name__ == "__main__":
    unittest.main()
