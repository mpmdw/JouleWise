"""W1 PREQUAL extension: every check and the orchestrator, synthetic only (no hardware, no MBP).

Fast checks run for real against this checkout; host commands go to w1_prequal.FakeHost.
The clone-based checks run for real on a shared scratch clone (about 10-20 s each).
"""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from joulewise.align import w1_prequal as wp

ROOT = Path(__file__).resolve().parents[2]


def completed(argv, rc=0, out='', err=''):
    return subprocess.CompletedProcess(argv, rc, out, err)


class _Ctx(unittest.TestCase):
    NEXT = 'w1'

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='w1pq-test-'))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        env = mock.patch.dict(os.environ, {'JOULEWISE_HOST_STATE_DIR': str(self.tmp / 'host-state')})
        env.start()
        self.addCleanup(env.stop)
        (self.tmp / 'host-state').mkdir()
        self.ctx = wp.Context(ROOT, self.tmp / 'work', self.NEXT)
        self.ctx.work.mkdir()

    def probe(self, name, **ctx):
        for key, value in ctx.items():
            setattr(self.ctx, key, value)
        return wp.probe(name, self.ctx)


class ArmCliTests(_Ctx):
    def test_production_cli_admits_the_control_and_refuses_every_fault_before_the_installer(self):
        row = self.probe('arm-cli')
        self.assertEqual(row['status'], wp.PASS, row['detail'])
        cases = {c['case']: c for c in row['evidence']['cases']}
        self.assertTrue(cases['control']['admitted'] and cases['control']['installer_called'])
        for name, case in cases.items():
            if name != 'control':
                self.assertFalse(case['installer_called'], name)
                self.assertFalse(case['admitted'], name)

    def test_a_dropped_required_flag_fails_the_check(self):
        real = wp.run_install

        def without_triage(ctx, session, disk, packet, **kw):
            if kw.get('args_override', {}).get('--obc-off-attested-by') == ' ':
                kw['args_override'] = {}      # the fault never reaches the arm: refusal missing
            return real(ctx, session, disk, packet, **kw)
        with mock.patch.object(wp, 'run_install', without_triage):
            row = self.probe('arm-cli')
        self.assertEqual(row['status'], wp.FAIL)
        self.assertIn('obc-unattested', row['detail'])

    def test_fake_host_refuses_unknown_commands(self):
        with self.assertRaises(AssertionError):
            wp.FakeHost()(['/usr/bin/true'])


class CadenceTests(_Ctx):
    def test_calibration_stop_passes_on_the_planned_manifest(self):
        row = self.probe('calibration-stop')
        self.assertEqual(row['status'], wp.PASS, row['detail'])

    def test_calibration_stop_fails_when_the_predicate_drifts(self):
        from joulewise.align.apple import v4_cadence as cad
        with mock.patch.object(cad, 'CAL_WINDOWS', 7):
            row = self.probe('calibration-stop')
        self.assertEqual(row['status'], wp.FAIL)

    def test_escalation_exit_resumes_on_a_signed_lead_ruling(self):
        row = self.probe('cal-escalation-exit')
        self.assertEqual(row['status'], wp.PASS, row['detail'])
        from joulewise.align.apple import v4_cadence as cad
        real = cad.calibration_stop
        with mock.patch.object(cad, 'calibration_stop', lambda rows, rulings=(): real(rows)):   # rulings ignored
            row = self.probe('cal-escalation-exit')
        self.assertEqual(row['status'], wp.FAIL)
        self.assertIn('MED-2', row['detail'])

    def test_staleness_gap_is_reported_and_goes_green_when_the_arm_binds_the_latest_record(self):
        row = self.probe('triage-staleness')
        self.assertEqual(row['status'], wp.FAIL)
        self.assertTrue(row['evidence']['verdicts']['fresh']['admitted'])
        self.assertTrue(row['evidence']['verdicts']['stale']['admitted'])
        from joulewise.align.apple import v4_cadence as cad
        real = cad.next_arm_triage

        def latest_only(packet, internal, identity=None):      # a stand-in for the G1 fix
            verdict = real(packet, internal, identity)
            if packet.get('previous_window') == 'C2':
                verdict = {**verdict, 'admitted': False, 'reasons': verdict['reasons'] + ['stale record']}
            return verdict
        with mock.patch.object(cad, 'next_arm_triage', latest_only):
            self.assertEqual(self.probe('triage-staleness')['status'], wp.PASS)

    def test_edited_packet_bytes_gap_and_green_on_a_digest_binding(self):
        row = self.probe('triage-edited-bytes')
        self.assertEqual(row['status'], wp.FAIL)
        self.assertTrue(row['evidence']['verdicts']['committed']['admitted'])
        from joulewise.align.apple import v4_cadence as cad
        real = cad.next_arm_triage

        def digest_bound(packet, internal, identity=None):     # a stand-in for the G1b fix
            verdict = real(packet, internal, identity)
            if 'edited after commit' in json.dumps(packet):
                verdict = {**verdict, 'admitted': False, 'reasons': ['packet bytes differ from the committed packet']}
            return verdict
        with mock.patch.object(cad, 'next_arm_triage', digest_bound):
            self.assertEqual(self.probe('triage-edited-bytes')['status'], wp.PASS)


class PortedSolTests(_Ctx):
    def write(self, name, value):
        proj = self.tmp / 'proj'
        (proj / 'plans').mkdir(parents=True, exist_ok=True)
        (proj / 'plans' / f'{name}.json').write_text(json.dumps(value))
        return f'plans/{name}.json'

    def probe(self, name, **ctx):
        ctx.setdefault('repo', self.tmp / 'proj')
        return super().probe(name, **ctx)

    def series(self, **change):
        source = self.write('source', {'frozen': True})
        windows = ([{'window': 'W1', 'role': 'w1'}]
                   + [{'window': f'C{i}', 'role': 'calibration', 'benign_per_pair': {'spam': 7, 'bank': 7}}
                      for i in range(1, 9)] + [{'window': 'T1', 'role': 'test'}])
        import hashlib
        value = {'schema': wp.SERIES_SCHEMA, 'windows': windows,
                 'source': {'path': source, 'sha256': hashlib.sha256((self.tmp / 'proj' / source).read_bytes()).hexdigest()}}
        value.update(change)
        return self.write('series', value)

    def test_series_projection_binding_and_fixed_eight(self):
        self.write('placeholder', {})
        self.assertEqual(self.probe('series-manifest', next='r1')['status'], wp.PENDING)
        self.assertEqual(self.probe('series-manifest', series_projection=self.series())['status'], wp.PASS)
        bad = self.series(source={'path': self.write('other', {'x': 1}), 'sha256': '0' * 64})
        self.assertEqual(self.probe('series-manifest', series_projection=bad)['status'], wp.FAIL)
        reordered = self.series(windows=[{'window': 'C1', 'role': 'calibration'}])
        self.assertEqual(self.probe('series-manifest', series_projection=reordered)['status'], wp.FAIL)

    def test_deadline_projection_r1_floors_and_encounters(self):
        self.assertEqual(self.probe('deadline', next='r1')['status'], wp.FAIL)
        plan = {'window_max_s': 100000, 'smoke_deadline_projection': {
            'kind': 'r1', 'bracket_s': 600, 'close_s': 600, 'harvest_s': 600,
            'segments': [{'bound_s': 30000, 'attempts': 2, 'batch_encounters': 1}]}}
        row = self.probe('deadline', next='r1', deadline_projection=self.write('ok', plan))
        self.assertEqual(row['status'], wp.PASS, row['detail'])
        self.assertEqual(row['evidence']['required_s'], max(30000 * 2 + 11164, 96427) + 1800)   # R1 redo floor
        short = {**plan, 'window_max_s': 90000}       # below the 96,427 s redo floor + overhead
        self.assertEqual(self.probe('deadline', next='r1', deadline_projection=self.write('short', short))['status'],
                         wp.FAIL)
        self.assertEqual(self.probe('deadline', next='w1', deadline_projection=self.write('ok2', plan))['status'],
                         wp.FAIL)    # an R1 projection cannot size W1

    def test_executed_closure_reaches_the_arm_and_driver_modules(self):  # noqa: D102
        closure = wp.executed_closure(ROOT)
        for path in ('scripts/align_v4_session.py', 'joulewise/align/apple/v4_cadence.py', 'joulewise/b5/driver.py'):
            self.assertIn(path, closure)

    def test_runbook_kit_steps(self):
        doc = self.tmp / 'doc.md'
        doc.write_text('```sh\npython3 scripts/align_v4_kit.py --check   # step\n```\n')
        self.assertEqual(wp.runbook_kit_steps(doc), ['check'])
        doc.write_text('```sh\npython3 scripts/align_v4_kit.py\npython3 scripts/align_v4_kit.py --check\n```\n'
                       '# python3 scripts/align_v4_kit.py outside the block\n')
        self.assertEqual(wp.runbook_kit_steps(doc), ['regenerate', 'check'])
        doc.write_text('no block\n')
        with self.assertRaises(ValueError):
            wp.runbook_kit_steps(doc)

    def test_optin_ledger_is_a_warn_row_that_never_blocks(self):
        row = self.probe('optin-required', repo=ROOT)
        self.assertEqual(row['status'], wp.WARN)
        self.assertIn('tests.align.test_v4_w1_synthetic -> wp22-dry-run (JW_WP22_FULL=1)', row['evidence']['covered'])
        self.write('placeholder', {})
        self.assertEqual(self.probe('optin-required')['status'], wp.WARN)


class SizingTests(_Ctx):
    def test_window_max_paths_agree_and_the_committed_plan_is_pending_before_w1(self):
        row = self.probe('w1-window-max', next='r1')
        self.assertEqual(row['status'], wp.PASS, row['detail'])
        self.assertEqual(row['evidence']['validator_window_max_s'], row['evidence']['writer_window_max_s'])
        self.assertEqual(row['evidence']['unplanned_wait_sources'], [])
        at_gate = self.probe('w1-window-max', next='w1')
        self.assertEqual(at_gate['status'], wp.FAIL)        # PENDING at its own gate fails
        self.assertIn('not committed yet', at_gate['detail'])

    def test_an_unplanned_wait_in_the_w1_closure_fails(self):
        fake = self.tmp / 'repo'
        shutil.copytree(ROOT / 'configs/campaigns/align_v4', fake / 'configs/campaigns/align_v4')
        (fake / 'scripts').mkdir()
        (fake / 'scripts/waits.py').write_text('wait_outside_os_batch(1)\n')
        with mock.patch.object(wp, 'executed_closure', lambda root: {'scripts/waits.py'}):
            row = self.probe('w1-window-max', repo=fake)
        self.assertEqual(row['status'], wp.FAIL)
        self.assertIn('waits outside the programmed span', row['detail'])


class RouteTests(_Ctx):
    def test_w1_route_is_declared_and_answers(self):
        row = self.probe('arm-route')
        self.assertEqual(row['status'], wp.PASS, row['detail'])

    def test_no_r1_route_fails_naming_item_218(self):
        row = self.probe('arm-route', next='r1')
        self.assertEqual(row['status'], wp.FAIL)
        self.assertIn('218', row['detail'])

    def test_missing_manifest_or_broken_step_fails(self):
        fake = self.tmp / 'repo'
        (fake / 'configs/align/v4').mkdir(parents=True)
        self.assertEqual(self.probe('arm-route', repo=fake)['status'], wp.FAIL)
        routes = {'routes': {'w1': {'status': 'declared', 'steps': [
            {'id': 'x', 'requires': ['scripts/absent.py']},
            {'id': 'y', 'probe': {'argv': ['/bin/sh', '-c', 'echo nope'], 'expect_text': ['--plan']}}]}}}
        (fake / wp.ARM_ROUTES).write_text(json.dumps(routes))
        row = self.probe('arm-route', repo=fake)
        self.assertEqual(row['status'], wp.FAIL)
        self.assertIn('missing scripts/absent.py', row['detail'])
        self.assertIn("missing=['--plan']", row['detail'])


class KitReadyTests(_Ctx):
    def fake_run(self, rc, err):
        def run(argv, **kw):
            if argv[0] == 'git':
                return completed(argv, 0, 'f' * 40 + '\n')
            return completed(argv, rc, '', err)
        return run

    def test_classification(self):
        cases = [((0, ''), 'w1', wp.PASS),
                 ((1, 'align_v4_kit: v4 kit BLOCKED by placeholders: R1.B_D'), 'r1', wp.PENDING),
                 ((1, 'align_v4_kit: v4 kit BLOCKED by placeholders: R1.B_D'), 'w1', wp.FAIL),
                 ((1, 'align_v4_kit: generated v4 kit drifted: x'), 'r1', wp.FAIL),
                 ((1, 'Traceback (most recent call last)'), 'r1', wp.FAIL),
                 ((1, 'something else entirely'), 'r1', wp.FAIL)]
        for (rc, err), nxt, expected in cases:
            with self.subTest(err=err, next=nxt):
                self.assertEqual(self.probe('kit-ready', run=self.fake_run(rc, err), next=nxt)['status'], expected)


class Wp22Tests(_Ctx):
    def fake(self, witness_ok, full_rc):
        def run(argv, **kw):
            argv = [str(a) for a in argv]
            if 'scripts/align_v4_w1_synthetic.py' in argv:
                out = Path(argv[argv.index('scripts/align_v4_w1_synthetic.py') + 1])
                if witness_ok:
                    out.mkdir(parents=True)
                    (out / 'dry_run_record.json').write_text(json.dumps({'desk_status': 'ok'}))
                    return completed(argv, 0)
                return completed(argv, 1, '', 'ValueError: R11 contrast_fit')
            return completed(argv, full_rc, '', 'Ran 18 tests in 1.0s\n' + ('OK' if full_rc == 0 else 'FAILED (errors=2)'))
        return run

    def test_green_witness_and_full_module_pass(self):
        self.assertEqual(self.probe('wp22-dry-run', run=self.fake(True, 0))['status'], wp.PASS)

    def test_any_red_part_fails(self):
        self.assertEqual(self.probe('wp22-dry-run', run=self.fake(False, 0))['status'], wp.FAIL)
        self.assertEqual(self.probe('wp22-dry-run', run=self.fake(True, 1))['status'], wp.FAIL)


class ReceiptTests(_Ctx):
    def test_self_test_admits_exact_and_refuses_drift_then_reports_the_pending_receipt(self):
        from joulewise.align.apple import v4_registration as reg
        bound = ('docs/align/v4/PREQUAL.md', 'scripts/align_v4_kit.py')
        with mock.patch.object(reg, 'ARTIFACTS', bound), mock.patch.object(wp, 'executed_closure', lambda root: set()):
            row = self.probe('receipt', next='r1')
        self.assertEqual(row['status'], wp.PENDING, row['detail'])
        self.assertEqual(row['evidence']['self_test']['exact'], 'admitted')
        self.assertIn('digest drift', row['evidence']['self_test']['digest_mismatch'])
        self.assertIn('digest drift', row['evidence']['self_test']['working_bytes_drift'])

    def test_an_executed_module_outside_the_receipt_fails(self):
        from joulewise.align.apple import v4_registration as reg
        trimmed = tuple(p for p in reg.ARTIFACTS if p != 'joulewise/align/apple/v4_cadence.py')
        with mock.patch.object(reg, 'ARTIFACTS', trimmed):
            row = self.probe('receipt', next='r1')
        self.assertEqual(row['status'], wp.FAIL)
        self.assertIn('joulewise/align/apple/v4_cadence.py', row['evidence']['uncovered'])

    def test_absent_bound_artifacts_are_pending_before_w1_and_fail_at_w1(self):
        self.assertIn(self.probe('receipt', next='r1')['status'], (wp.PENDING,))
        self.assertEqual(self.probe('receipt', next='w1')['status'], wp.FAIL)


class ChainTests(_Ctx):
    def test_chain_runs_every_cli_step_on_a_lane_shaped_record(self):
        row = self.probe('r1-w1-chain')
        steps = {s['step']: s for s in row['evidence'].get('steps', [])}
        for name in ('export', 'backfill-x-g', 'backfill-turn-counts', 'derive-contrast', 'decide'):
            self.assertEqual(steps[name]['rc'], 0, (name, row['detail']))
        self.assertIn('kit.require_ready(backfilled record)', steps)
        self.assertIn(row['status'], (wp.PASS, wp.FAIL))
        if row['status'] == wp.FAIL:      # only the runbook-drift finding or a pending refusal may remain
            self.assertIn('R1-TO-W1-CHAIN.md as written', row['detail'])


class MeterTests(_Ctx):
    def test_meter_through_the_hazard_pack_driver_flags_the_member_it_lost(self):
        row = self.probe('km003c-launch')
        self.assertEqual(row['status'], wp.PASS, row['detail'])
        killed = row['evidence']['killed']
        self.assertGreaterEqual(killed['restarts'], 1)
        self.assertEqual(killed['members']['member-straddles-kill']['status'], 'missing')
        self.assertEqual(row['evidence']['clean']['members']['member-clean']['status'], 'available')


class MeterCrashRadiusTests(_Ctx):
    def test_a_member_before_a_reader_crash_is_judged(self):
        row = self.probe('km003c-crash-radius')
        self.assertIn(row['status'], (wp.PASS, wp.FAIL), row['detail'])
        self.assertIn('member_before_kill', row['evidence'])
        self.assertFalse(row['evidence']['stream_001_trailer'])
        if row['status'] == wp.FAIL:      # today: the whole killed stream loses its clock offset
            self.assertIn('meter.clock_unresolved', row['evidence']['member_before_kill']['flags'])


class SmokeKitTests(_Ctx):
    def test_smoke_reduction_and_fault_expectations_match_production(self):
        row = self.probe('smoke-kit')
        self.assertEqual(row['status'], wp.PASS, row['detail'])
        self.assertEqual(set(row['evidence']['reduction']['kept_runs']),
                         {'align-v4-reference-start', 'align-v4-episodes-a'})


class OrchestratorTests(unittest.TestCase):
    def ctx(self, nxt):
        run = lambda argv, **kw: completed(argv, 0, '' if 'status' in argv else 'f' * 40)
        return wp.Context(ROOT, tempfile.mkdtemp(prefix='w1pq-orch-'), nxt, commit='f' * 40, run=run)

    def rows(self, statuses):
        return lambda name: {'check': name, 'status': statuses.get(name, wp.PASS), 'detail': 'synthetic',
                             'covers': '', 'evidence': {}}

    def test_blocking_and_pending_rules(self):
        ctx = self.ctx('r1')
        report = wp.run_all(ctx, spawn=self.rows({'receipt': wp.PENDING, 'wp22-dry-run': wp.FAIL}))
        self.assertEqual(report['status'], 'PASS')      # neither gates R1
        rows = {r['check']: r for r in report['checks']}
        self.assertFalse(rows['wp22-dry-run']['blocks'])
        report = wp.run_all(ctx, spawn=self.rows({'arm-route': wp.FAIL}))
        self.assertEqual(report['status'], 'FAIL')
        report = wp.run_all(self.ctx('w1'), spawn=self.rows({'receipt': wp.PENDING}))
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual({r['check']: r for r in report['checks']}['receipt']['status'], wp.FAIL)

    def test_warn_never_blocks(self):
        report = wp.run_all(self.ctx('w1'), spawn=self.rows({'optin-required': wp.WARN}))
        self.assertEqual(report['status'], 'PASS')
        self.assertIn('| optin-required | WARN |', wp.table(report))

    def test_waivers_and_subsets(self):
        report = wp.run_all(self.ctx('w1'), spawn=self.rows({'triage-staleness': wp.FAIL}),
                            waivers={'triage-staleness': 'lead ruling X'})
        self.assertEqual(report['status'], 'PASS')
        report = wp.run_all(self.ctx('w1'), only={'arm-route'}, spawn=self.rows({}))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('| arm-route | PASS | r1 | yes |', wp.table(report))

    def test_spawn_parses_the_probe_line_and_fails_closed(self):
        ctx = self.ctx('w1')
        good = json.dumps({'check': 'arm-route', 'status': 'PASS', 'detail': 'ok'})
        for out, expected in ((f'noise\n{good}\n', 'PASS'), ('garbage\n', 'FAIL'), ('', 'FAIL')):
            ctx.run = lambda argv, out=out, **kw: completed(argv, 0, out)
            self.assertEqual(wp.spawn_probe('arm-route', ctx, ROOT / 'scripts/align_v4_prequal.py')['status'],
                             expected)

        def timeout(argv, **kw):
            raise subprocess.TimeoutExpired(argv, 1)
        ctx.run = timeout
        self.assertIn('timed out', wp.spawn_probe('arm-route', ctx, 'x')['detail'])

    def test_probe_turns_exceptions_into_fail(self):
        with mock.patch.dict(wp.CHECKS, {'boom': {'fn': lambda ctx: 1 / 0, 'covers': '', 'gates': 'w1'}}):
            row = wp.probe('boom', self.ctx('w1'))
        self.assertEqual(row['status'], wp.FAIL)
        self.assertIn('ZeroDivisionError', row['detail'])


class CliTests(unittest.TestCase):
    def test_probe_mode_and_usage_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/align_v4_prequal.py'), '--w1-probe',
                                  'calibration-stop', '--work', tmp, '--w1-next', 'w1'],
                                 capture_output=True, text=True, cwd=ROOT, timeout=120)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(json.loads(out.stdout.splitlines()[-1])['status'], 'PASS')
            from scripts import align_v4_prequal as cli
            for argv in (['--w1-next', 'w1', '--output', str(Path(tmp) / 'r'), '--only', 'nope'],
                         ['--w1-next', 'w1', '--output', str(Path(tmp) / 'r'), '--waive', 'arm-route'],
                         ['--w1-probe', 'arm-route']):
                with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    cli.main(argv)


if __name__ == '__main__':
    unittest.main()
