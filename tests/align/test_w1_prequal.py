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
        from scripts import align_v4_session
        # Harness probes must supply their own explicit synthetic seam. Fail
        # before any real LaunchAgents read if that adapter is missing.
        watchdog = mock.patch.object(align_v4_session, 'watchdog_acceptance',
                                     side_effect=AssertionError('PREQUAL omitted synthetic watchdog'))
        watchdog.start()
        self.addCleanup(watchdog.stop)
        for name in ('frequency_word_preflight', 'frequency_word_pre_t0'):
            frequency = mock.patch.object(align_v4_session, name,
                side_effect=AssertionError('PREQUAL omitted synthetic frequency'))
            frequency.start()
            self.addCleanup(frequency.stop)
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
    def test_named_watchdog_hold_check_is_registered_and_proves_rollback(self):
        self.assertIn('watchdog-hold-rollback', wp.CHECKS)
        row = self.probe('watchdog-hold-rollback')
        self.assertEqual(row['status'], wp.PASS, row)
        cases = {case['phase']: case for case in row['evidence']['cases']}
        self.assertTrue(cases['pre_install']['refused'])
        self.assertFalse(cases['pre_install']['installer_called'])
        for key in ('refused', 'uninstalled_this_plan', 'both_labels_verified_absent', 'automatic_restored'):
            self.assertTrue(cases['post_install'][key], key)
        report = wp.run_all(self.ctx, spawn=lambda name: dict(row) if name == row['check'] else
            {'check': name, 'status': wp.PASS, 'detail': '', 'evidence': {}})
        self.assertIn('| watchdog-hold-rollback | PASS | w1 | yes |', wp.table(report))

    def test_synthetic_watchdog_holding_refuses_with_w1_reason(self):
        import time
        now = time.time()
        base, session, disk = wp.arm_fixture(self.ctx, 'watchdog-hold', now=now)
        packet = wp.valid_packet(self.ctx, base, now)
        control = wp.run_install(self.ctx, session, disk, packet, host=wp.FakeHost(now=now), now=now)
        self.assertEqual(control['rc'], 0, control['stderr'])
        self.assertTrue(control['arm']['admitted'])
        self.assertEqual(len(control['installer_calls']), 1)
        host = wp.FakeHost(now=now, watchdog_state='HOLD_PLAN_MALFORMED')
        row = wp.run_install(self.ctx, session, disk, packet, host=host, now=now)
        self.assertNotEqual(row['rc'], 0)
        self.assertFalse(row['arm']['admitted'])
        self.assertIn('watchdog_acceptance: pre_install: HOLD_PLAN_MALFORMED:',
                      '\n'.join(row['arm']['reasons']))
        self.assertEqual(row['installer_calls'], [])
        with mock.patch.object(wp, 'FakeHost', return_value=host):
            arm = wp._arm_on_records(self.ctx, base / 'measurement', packet, now=now)
        self.assertFalse(arm['admitted'])
        self.assertIn('watchdog_acceptance: pre_install: HOLD_PLAN_MALFORMED:', '\n'.join(arm['reasons']))

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

    def test_packet_rebuild_and_tamper_pass_on_the_production_arm(self):
        rebuild, tamper = self.probe('packet-rebuild'), self.probe('packet-tamper')
        self.assertEqual(rebuild['status'], wp.PASS, rebuild['detail'])
        self.assertEqual(tamper['status'], wp.PASS, tamper['detail'])
        self.assertEqual(tamper['evidence']['zero_capture_attempt'], 'C3')
        self.assertGreater(tamper['evidence']['mutations_tried'], 20)

    def test_an_arm_that_keeps_no_rebuild_or_trusts_the_supplied_packet_fails(self):
        from scripts import align_v4_next_arm_packet as builder, align_v4_session as session
        real = session.arm_checks

        def forgetful(*a, **kw):          # the pre-fix arm: no rebuilt packet in the record
            record = real(*a, **kw)
            record['next_arm_triage'].pop('rebuilt_packet', None)
            return record
        with mock.patch.object(session, 'arm_checks', forgetful):
            self.assertIn('no rebuilt packet', self.probe('packet-rebuild')['detail'])
        rebuild = builder.rebuild_and_compare
        with mock.patch.object(builder, 'rebuild_and_compare',
                               lambda *a, **kw: (rebuild(*a, **kw)[0], True)):     # trusts any supplied packet
            row = self.probe('packet-tamper')
        self.assertEqual(row['status'], wp.FAIL)
        self.assertTrue(row['evidence']['admitted_mutations'])

    def test_packet_checks_judge_a_stand_in_rebuilding_arm(self):
        from scripts import align_v4_session as session
        with mock.patch.object(session, 'arm_checks', RebuildingArm()):
            rebuild, tamper = self.probe('packet-rebuild'), self.probe('packet-tamper')
        self.assertEqual(rebuild['status'], wp.PASS, rebuild['detail'])
        self.assertEqual(tamper['status'], wp.PASS, tamper['detail'])
        with mock.patch.object(session, 'arm_checks', RebuildingArm(ignore={'record_commit'})):
            row = self.probe('packet-tamper')
        self.assertEqual(row['status'], wp.FAIL)
        self.assertTrue(any('record_commit' in m for m in row['evidence']['admitted_mutations']))
        with mock.patch.object(session, 'arm_checks', RebuildingArm(chain_strict=False)):
            row = self.probe('packet-tamper')
        self.assertEqual(row['status'], wp.FAIL)
        self.assertIn('chain omits attempt C3', row['evidence']['admitted_mutations'])
        with mock.patch.object(session, 'arm_checks', RebuildingArm(expiry=False)):
            self.assertIn('not refused for expiry', self.probe('packet-rebuild')['detail'])


class RebuildingArm:
    """A stand-in for the ruled design: rebuild from the repository, canonical equality, expiry."""

    def __init__(self, ignore=(), chain_strict=True, expiry=True):
        self.ignore, self.chain_strict, self.expiry = set(ignore), chain_strict, expiry

    def rebuild(self, root):
        log = subprocess.run(['git', '-C', str(root), 'log', '--reverse', '--format=%H', '--name-only'],
                             capture_output=True, text=True, check=True).stdout.split()
        rows, head = [], None
        for token in log:
            if len(token) == 40 and all(c in '0123456789abcdef' for c in token):
                head = token
            elif token.endswith('/record.json'):
                record = json.loads(subprocess.run(['git', '-C', str(root), 'show', f'{head}:{token}'],
                                                   capture_output=True, text=True, check=True).stdout)
                captured = sum(v is not None for v in (record.get('captures') or {}).values())
                rows.append({'window': record['window'], 'captured_members': captured})
        stamp = int(subprocess.run(['git', '-C', str(root), 'log', '-1', '--format=%ct'], capture_output=True,
                                   text=True, check=True).stdout)
        return {'schema': 'stand-in.next_arm_triage', 'record_commit': head, 'calibration_windows': rows,
                'valid_until_epoch_s': stamp + 600,          # deterministic: from committed history
                'checks': {'capture_faults': {'status': 'pass', 'basis': 'b'}}}

    def __call__(self, measurement_root, plan, *, next_arm_triage=None, now=None, **kw):
        rebuilt = self.rebuild(measurement_root)
        try:
            packet = json.loads(Path(next_arm_triage).read_text())
        except (OSError, ValueError, TypeError):
            packet = {}
        strip = lambda p: {k: v for k, v in p.items() if k not in ('pushed_tip', 'packet_preflight')
                           and k not in self.ignore}
        same = strip(packet) == strip(rebuilt)
        if not self.chain_strict and isinstance(packet.get('calibration_windows'), list):
            same = same or (strip({**packet, 'calibration_windows': rebuilt['calibration_windows']}) == strip(rebuilt))
        fresh = (not self.expiry or 'valid_until_epoch_s' not in rebuilt
                 or (now or __import__('time').time)() <= rebuilt['valid_until_epoch_s'])
        reasons = ([] if same else ['next_arm_triage: packet does not match its committed sources'])
        reasons += [] if fresh else ['next_arm_triage: packet expired before this arm']
        return {'admitted': not reasons, 'reasons': reasons, 'next_arm_triage': {'rebuilt_packet': rebuilt}}


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
        windows = ([{'window': 'W1', 'role': 'w1'}]
                   + [{'window': f'C{i}', 'role': 'calibration', 'benign_per_pair': {'spam': 7, 'bank': 7}}
                      for i in range(1, 9)] + [{'window': 'T1', 'role': 'test'}])
        import hashlib

        def projection(name, source_windows, projected=windows, sha=None):
            source = self.write(f'source-{name}', {'windows': source_windows})
            digest = sha or hashlib.sha256((self.tmp / 'proj' / source).read_bytes()).hexdigest()
            return self.write(f'series-{name}', {
                'schema': wp.SERIES_SCHEMA, 'windows': projected, 'source': {'path': source, 'sha256': digest}})
        self.write('placeholder', {})
        self.assertEqual(self.probe('series-manifest', next='r1')['status'], wp.PENDING)
        self.assertEqual(self.probe('series-manifest', series_projection=projection('ok', windows))['status'], wp.PASS)
        short = [dict(w) for w in windows]
        short[1]['benign_per_pair'] = {'spam': 1, 'bank': 1}
        self.assertEqual(self.probe('series-manifest', series_projection=projection('short', short))['status'],
                         wp.FAIL)
        self.assertEqual(self.probe('series-manifest', series_projection=projection('sha', windows, sha='0' * 64))[
            'status'], wp.FAIL)
        self.assertEqual(self.probe('series-manifest', series_projection=projection(
            'two', windows[:2], projected=windows[:2]))['status'], wp.FAIL)     # roster agrees, not fixed-8
        # R24: reserve windows C9.. flagged `replacement` may follow C8 (at most six, in order); fixed-8 still holds
        reserve = lambda n: {'window': f'C{n}', 'role': 'calibration', 'replacement': True,
                             'benign_per_pair': {'spam': 7, 'bank': 7}}
        with_reserves = windows[:9] + [reserve(n) for n in range(9, 15)] + windows[9:]
        passed = self.probe('series-manifest', series_projection=projection('reserves', with_reserves, with_reserves))
        self.assertEqual(passed['status'], wp.PASS)
        self.assertEqual(passed['evidence']['reserve_order'], [f'C{n}' for n in range(9, 15)])
        for label, bad in (('seven', windows[:9] + [reserve(n) for n in range(9, 16)] + windows[9:]),
                           ('gap', windows[:9] + [reserve(10)] + windows[9:]),
                           ('unflagged', windows[:9] + [dict(reserve(9), replacement=False)] + windows[9:]),
                           ('thin', windows[:9] + [dict(reserve(9), benign_per_pair={'spam': 1, 'bank': 7})] + windows[9:]),
                           ('after tests', windows + [reserve(9)])):
            with self.subTest(reserves=label):
                self.assertEqual(self.probe('series-manifest', series_projection=projection(
                    'bad-' + label, bad, bad))['status'], wp.FAIL)

    def bundle(self, name, *, plan_id='align-v4-20261109T000000Z', plist_plan=None, sha=None, exit_code=0):
        """An installed-plan evidence bundle around a REAL plan from the production plan writer."""
        import hashlib
        import plistlib
        import time as _time
        from joulewise.b5 import plan as b5_plan
        from tests.fixtures.b5_plan import fake_window
        root = self.tmp / f'plan-{name}'
        root.mkdir()
        measurement = fake_window.build_checkout(root)
        record = b5_plan.write_window_plan(
            fake_window.inputs(root, measurement, 'alpha', plan_id=plan_id, t0_epoch_s=(int(_time.time()) // 60) * 60,
                               g10=False),
            settle_s=0, pack_digest=lambda _root: 'e' * 64, threshold_defaults=fake_window.threshold_defaults)
        plan_path = record['plan']['path']
        raw = Path(plan_path).read_bytes()
        directory = self.tmp / 'proj' / 'bundles' / name
        directory.mkdir(parents=True)
        (directory / 'night_plan.json').write_bytes(raw)
        (directory / 'session.json').write_text(json.dumps({
            'plan_path': plan_path, 'plan_sha256': sha or hashlib.sha256(raw).hexdigest(),
            'install': {'exit_code': exit_code, 'argv': ['install_night_agent.sh', '--plan', plan_path]}}))
        (directory / 'com.joulewise.night.plist').write_bytes(plistlib.dumps({'ProgramArguments': [
            '/v/bin/python', 'scripts/run_night.py', 'run', '--plan', plist_plan or plan_path]}))
        return f'bundles/{name}', json.loads(raw)

    def test_deadline_is_bound_to_the_installed_plan_plist_and_session(self):
        self.write('placeholder', {})
        self.assertEqual(self.probe('deadline', next='w1')['status'], wp.FAIL)
        name, plan = self.bundle('ok')
        row = self.probe('deadline', next='w1', deadline_projection=name)
        self.assertEqual(row['status'], wp.PASS, row['detail'])
        self.assertEqual(row['evidence']['window_max_s'], plan['window_max_s'])
        self.assertEqual(row['evidence']['programmed_span_s'], plan['hazard_window']['programmed_span_s'])
        self.assertEqual(self.probe('deadline', next='r1', deadline_projection=name)['status'], wp.FAIL)  # kind
        for label, kwargs in (('other-plist', {'plist_plan': '/elsewhere/night_plan.json'}),
                              ('bad-sha', {'sha': '0' * 64}), ('failed-install', {'exit_code': 1}),
                              ('smoke', {'plan_id': 'align-v4-smoke-20261109T0000Z'})):
            with self.subTest(label=label):
                bundle, _ = self.bundle(label, **kwargs)
                self.assertEqual(self.probe('deadline', next='w1', deadline_projection=bundle)['status'], wp.FAIL)
        r1, _ = self.bundle('r1', plan_id='align-r1-20261108T0917Z')
        self.assertIn('required', self.probe('deadline', next='r1', deadline_projection=r1)['detail'])  # R1 floor
        lone = self.write('lone-plan', plan)
        self.assertEqual(self.probe('deadline', next='w1', deadline_projection=lone)['status'], wp.FAIL)

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

    def test_r1_route_is_pinned_at_its_armed_commit(self):
        row = self.probe('arm-route', next='r1')
        self.assertEqual(row['status'], wp.PASS, row['detail'])
        self.assertIn('align-r1-20261108T0917Z', row['detail'])
        fake = self.tmp / 'repo'
        (fake / 'configs/align/v4').mkdir(parents=True)
        (fake / wp.ARM_ROUTES).write_text(json.dumps({'routes': {'r1': {'status': 'declared', 'commit': 'f' * 40,
                                                                        'steps': []}}}))
        missing = self.probe('arm-route', next='r1', repo=fake)
        self.assertEqual(missing['status'], wp.FAIL)
        self.assertIn('git fetch origin', missing['detail'])
        (fake / wp.ARM_ROUTES).write_text(json.dumps({'routes': {'r1': {'status': 'none', 'note': 'x'}}}))
        self.assertIn('218', self.probe('arm-route', next='r1', repo=fake)['detail'])

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
        report = wp.run_all(self.ctx('w1'), spawn=self.rows({'packet-rebuild': wp.FAIL}),
                            waivers={'packet-rebuild': 'lead ruling X'})
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
