"""Real capture finalization and rendered-chain reachability, synthetic only."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from joulewise import calibration_ledger as ledger, window_lineage
from joulewise.b5 import chain, plan
from joulewise.b6.driver_lane import metadata_path, read, write
from joulewise.b6.lanes import Prepared
from joulewise.b6.capture_screen import operative_bound_stop_s
from tests import test_validate_powermetrics_fiducial_derivation_only as capture_fixtures
from tests.b6 import round_support
from tests.b6.support import DeskCase, document

REFERENCE = '0.036462861644980'


def window_binding(runs, custody, *, block6):
    runs.mkdir(parents=True, exist_ok=True)
    custody.mkdir(parents=True, exist_ok=True)
    write(runs / window_lineage.LOCATOR_BASENAME, {
        'schema_version': window_lineage.HAZARD_LOCATOR_SCHEMA,
        'launch_lineage': {'window_context': {'custody_root': str(custody)}}})
    write(custody / 'night_plan.json', {'plan_id': 'synthetic-window', 'hazard_window': {
        'attempt': 1, 'bindings': {'capture_screen': {
            'alignment_reference_s': REFERENCE, 'bracket_screen_s': '0.014531',
            'operative_bound_stop_s': '0.092'}} if block6 else {}}})


class PolicyReadTests(unittest.TestCase):
    def test_root_without_hazard_locator_keeps_block5_without_records_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            flags = []
            self.assertFalse(ledger.uses_block6_capture_screen(Path(tmp), records_flags=flags))
            self.assertEqual(flags, [])

    def test_hazard_root_with_unreadable_plan_keeps_block6_with_records_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs, custody = Path(tmp) / 'runs', Path(tmp) / 'custody'
            window_binding(runs, custody, block6=True)
            policy = custody / 'night_plan.json'
            for payload in (None, '{broken', '{}', '{"hazard_window":{"bindings":null}}'):
                with self.subTest(payload=payload):
                    if payload is None:
                        policy.unlink()
                    else:
                        policy.write_text(payload)
                    flags = []
                    self.assertTrue(ledger.uses_block6_capture_screen(runs, records_flags=flags))
                    self.assertEqual(flags, ['records.window_plan_unreadable'])

    def test_hazard_locator_with_unresolved_custody_keeps_block6_with_records_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp)
            write(runs / window_lineage.LOCATOR_BASENAME, {
                'schema_version': window_lineage.HAZARD_LOCATOR_SCHEMA})
            flags = []
            self.assertTrue(ledger.uses_block6_capture_screen(runs, records_flags=flags))
            self.assertEqual(flags, ['records.window_plan_unreadable'])

    def test_window_policy_joins_the_existing_authentication_read_session(self):
        from joulewise.authentication_io import V2AuthenticationReadSession

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs, custody = root / 'runs', root / 'custody'
            window_binding(runs, custody, block6=True)
            policy = custody / 'night_plan.json'
            expected = hashlib.sha256(policy.read_bytes()).hexdigest()
            with V2AuthenticationReadSession() as session:
                self.assertTrue(ledger.uses_block6_capture_screen(runs))
                self.assertTrue(ledger.uses_block6_capture_screen(runs, window_plan_path=policy))
                record = session.records[str(policy.resolve())]
                self.assertEqual((record.grammar, record.sha256, record.read_count), ('json', expected, 2))


class CaptureDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        capture_fixtures.DerivationOnlyLiveCaptureTests.setUpClass()
        cls.fixture = capture_fixtures.DerivationOnlyLiveCaptureTests()

    @classmethod
    def tearDownClass(cls):
        capture_fixtures.DerivationOnlyLiveCaptureTests.tearDownClass()

    def capture(self, token, bound, block6, *, status='valid', unreadable_plan=False):
        f = self.fixture
        acceptance = f._rekey_acceptance()
        epoch, t1 = f._epoch(acceptance['identity_epoch']['os_build'])
        path, pin, session, custody = f._session(token, slots=('pre', 'post'),
            session_kind=None, epoch=epoch, t1=t1)
        window_binding(custody['pre'].parent.parent, path.parent / 'custody', block6=block6)
        if unreadable_plan:
            (path.parent / 'custody/night_plan.json').write_text('{broken')
        # Only the estimator's returned value is fixed. The public main, its
        # acceptance preflight, classification, hashed artifacts, ledger and
        # exit all run. MLX and sampler are the existing synthetic fixtures.
        wrapper = f.repo / ('bound-' + token + '.py')
        wrapper.write_text('from scripts import validate_powermetrics_fiducial as w\n'
            'import sys\noriginal = w.instrument_evidence\n'
            'def evidence(*args, **kwargs):\n'
            '    result = original(*args, **kwargs)\n'
            f'    result.update(status={status!r}, b_fiducial_s={float(bound)!r})\n'
            '    return result\n'
            'w.instrument_evidence = evidence\nraise SystemExit(w.main(sys.argv[1:]))\n')
        real_runner = f.runner
        def run(argv, **kwargs):
            return real_runner.run([argv[0], str(wrapper), *argv[2:]], **kwargs)
        with mock.patch.object(f, 'runner', mock.Mock(run=run)):
            result = f._writer(ledger=path, pin=pin, session_id=session, slot='pre',
                custody=custody['pre'], epoch=epoch, derivation_only=False)
        self.assertIn(result.returncode, (0, 1), result.stdout + result.stderr)
        evidence = read(custody['pre'] / 'instrument_evidence.json')
        manifest = read(custody['pre'] / 'manifest.json')
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        final = next(row for row in rows if row.get('event') == ledger.BRACKET_SESSION_FINALIZATION_EVENT)
        self.assertEqual(manifest['artifacts']['instrument_evidence.json'],
            hashlib.sha256((custody['pre'] / 'instrument_evidence.json').read_bytes()).hexdigest())
        return result, evidence, manifest, final

    def test_40ms_unreadable_block6_plan_finalizes_valid_with_records_flag(self):
        result, evidence, manifest, final = self.capture('unreadable-b6', '0.040', True, unreadable_plan=True)
        self.assertEqual((final['disposition'], result.returncode), ('valid', 0))
        for record in (evidence, manifest):
            self.assertTrue(record['exceeds_prior_level_screen'])
            self.assertIn('records.window_plan_unreadable', record['records_flags'])

    def test_block6_and_block5_capture_disposition_and_exit_matrix(self):
        for block6 in (False, True):
            for bound in ('0.030', '0.040', '0.077', '0.100'):
                with self.subTest(block6=block6, bound=bound):
                    result, evidence, manifest, final = self.capture(
                        f'b{6 if block6 else 5}-{bound[2:]}', bound, block6)
                    above = float(bound) > float(REFERENCE)
                    valid = block6 or not above
                    self.assertEqual((final['disposition'], result.returncode),
                        ('valid', 0) if valid else ('systematic-invalid', 1))
                    self.assertNotIn('derivation_only', evidence)
                    if block6:
                        for record in (evidence, manifest):
                            self.assertEqual(record['exceeds_prior_level_screen'], above)
                            self.assertEqual(record['screen_basis']['preflight_level_screen_s'], REFERENCE)
                    else:
                        self.assertNotIn('screen_basis', evidence)
                        self.assertNotIn('exceeds_prior_level_screen', manifest)

    def test_block6_does_not_promote_invalid_evidence(self):
        result, evidence, _, final = self.capture('invalid-b6', '0.100', True, status='invalid')
        self.assertEqual((final['disposition'], result.returncode), ('ordinary-invalid', 1))
        self.assertTrue(evidence['exceeds_prior_level_screen'])


class RenderedRound(round_support.Round):
    """Run the actual rendered zsh chain, stubbing only non-screen stages.

    Round's launcher supplies synthetic bundles/ledger custody and the real
    loop, desk and harvest. The public capture main runs with the existing
    fake sampler; its return code reaches the production chain's pre-capture
    stop check and its value reaches the real screen before the driver polls.
    """
    def registered_screen(self):
        # Round normally exercises pending registration (null screen values).
        # Use the registered synthetic calibration before plan rendering.
        prepared = Prepared(**self.state()['session']['prepared'])
        md = read(metadata_path(prepared))
        md['inputs']['capture_screen'] = {key: document()['calibration'][key] for key in
            ('alignment_reference_s', 'bracket_screen_s', 'operative_bound_stop_s')}
        md['inputs']['capture_screen']['operative_bound_stop_s'] = str(operative_bound_stop_s({}, md['packs'][0]))
        write(metadata_path(prepared), md)

    def opening_chain(self, bound):
        prepared = Prepared(**self.state()['session']['prepared'])
        metadata = read(metadata_path(prepared))
        p = read(prepared.plan_path)
        b = p['hazard_window']['bindings']
        night = Path(metadata['paths']['custody']) / 'night'
        capture = Path(b['pre_calibration_dir'])
        # The fake launcher bypasses run_night's publication of this locator.
        write(Path(b['claim_runs_root']) / window_lineage.LOCATOR_BASENAME, {
            'schema_version': window_lineage.HAZARD_LOCATOR_SCHEMA,
            'launch_lineage': {'window_context': {'custody_root': p['custody_root']}}})
        captured, tool_evidence, _, final = self.capture_tool.capture(
            'reach-' + bound[2:], bound, True)
        self.screen_disposition = final['disposition']
        evidence = read(capture / 'instrument_evidence.json')
        for key in ('b_fiducial_s', 'screen_basis', 'exceeds_prior_level_screen'):
            evidence[key] = tool_evidence[key]
        write(capture / 'instrument_evidence.json', evidence)
        # Use the real synthetic capture main's receipt for the pre stage;
        # other program stages are supplied by Round's synthetic collection.
        # The real chain's stop checks and block-6 screen remain intact.
        source = Path(p['chain_path']).read_text()
        before = source.index('cd "$REPO"')
        source = source[:before] + f'CAPTURE_RC={captured.returncode}\n' + '''
run_stage() {
  local stage="$1" kind="$2"
  shift 4
  if [[ "$kind" == calibration_capture && "$stage" == *-pre-calibration ]]; then
    journal "$stage" "$kind" "$CAPTURE_RC" "$(/bin/date +%s)"
    return $CAPTURE_RC
  fi
  if [[ "$kind" == pre_calibration_screen ]]; then
    "$@"
    local rc=$?
    journal "$stage" "$kind" "$rc" "$(/bin/date +%s)"
    return $rc
  fi
  journal "$stage" "$kind" 0 "$(/bin/date +%s)"
  return 0
}
settle() { return 0; }
''' + source[before:]
        (night / chain.STAGE_JOURNAL).write_text('')
        script = self.root / 'actual-chain.zsh'
        script.write_text(source)
        result = subprocess.run(['/bin/zsh', '-f', str(script)], env={**self.env, 'NIGHT_DIR': str(night)},
                                capture_output=True, text=True, timeout=60)
        self.chain_output = result.stdout + result.stderr
        write(night / 'chain.exited', {'epoch_s': 1786216000, 'exit_code': result.returncode})
        write(night / 'result.json', {'verdict': 'CHAIN_STOPPED' if result.returncode else 'GO',
                                     'chain_exit_code': result.returncode})
        return result


class ChainReachabilityTests(DeskCase):
    @classmethod
    def setUpClass(cls):
        CaptureDispositionTests.setUpClass()
        RenderedRound.capture_tool = CaptureDispositionTests()

    @classmethod
    def tearDownClass(cls):
        CaptureDispositionTests.tearDownClass()

    def test_opening_40ms_reaches_real_screen_and_desk(self):
        r = RenderedRound(self.root)
        r.until('SESSION_RUN')
        r.registered_screen()
        r.loop.tick()
        result = r.opening_chain('0.040')
        self.assertEqual((r.screen_disposition, result.returncode), ('valid', 0), r.chain_output)
        flags = Path(read(Prepared(**r.state()['session']['prepared']).plan_path)['custody_root']) / 'flags'
        self.assertIn('calibration.alignment_above_reference', '\n'.join(
            path.read_text() for path in flags.glob('*.jsonl')))
        r.until('SESSION_DESK')
        r.loop.tick()
        self.assertEqual(r.state()['state'], 'ROTATE')

    def test_opening_150ms_stops_at_13_and_full_pack_outcome_is_physics(self):
        r = RenderedRound(self.root, full_pack='alpha')
        r.until('SESSION_RUN')
        r.register_acceptance()
        r.registered_screen()
        write(r.control, {**read(r.control), 'stop': 'operative_bound_above_stop'})
        r.loop.tick()
        result = r.opening_chain('0.150')
        self.assertEqual((r.screen_disposition, result.returncode), ('valid', 13), r.chain_output)
        r.until('SESSION_DESK')
        r.loop.tick()
        state = r.state()
        self.assertEqual(state['attempts'][0]['outcomes']['alpha'], {
            'status': 'physics_stopped', 'cause': 'calibration.operative_bound_above_stop'})
