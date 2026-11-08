"""Bounded path rehearsals used by the offline W1 prequalification command.

All host commands are injected. Only the meter stand-in is a real subprocess;
it writes synthetic samples through the production HAZARD_PACK supervisor.
No MLX, USB, powermetrics, real model paths or study records are opened.
"""
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from joulewise.align.apple import powermode, v4_cadence as cadence
from scripts import align_v4_session as session, align_v4_kit as kit
from tests.align.test_v4_cadence import passing_packet
from tests.align.test_v4_kit import FakeArmHost

ROOT = Path(__file__).resolve().parents[2]


class ArmPathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='w1-smoke-arm-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        p = patch.dict(os.environ, {powermode.HOST_STATE_ENV: str(self.root / 'host')})
        p.start()
        self.addCleanup(p.stop)

    def options(self):
        return dict(runner=FakeArmHost(0), volume_runner=FakeArmHost(0),
                    obc_off_attested_by='synthetic', topup_completed_at=time.time() - 60,
                    topup_source='synthetic', next_arm_triage=passing_packet())

    def test_production_cli_forwards_every_required_arg_and_refuses_each_omission(self):
        argv = ['install', '--session-root', str(self.root), '--w1-disk-config', 'disk.json',
                '--obc-off-attested-by', 'synthetic', '--topup-completed-at', '1234',
                '--topup-source', 'synthetic', '--next-arm-triage', 'triage.json']
        with patch.object(session, 'install', return_value={'exit_code': 0}) as install:
            self.assertEqual(session.main(argv), 0)
            got = install.call_args.kwargs
            self.assertEqual(got, {'w1_disk_config': Path('disk.json'),
                'obc_off_attested_by': 'synthetic', 'topup_completed_at': '1234',
                'topup_source': 'synthetic', 'next_arm_triage': Path('triage.json')})
            for flag in argv[1::2]:
                index = argv.index(flag)
                with self.subTest(flag=flag), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exit:
                    session.main(argv[:index] + argv[index+2:])
                self.assertEqual(exit.exception.code, 2)
            self.assertEqual(install.call_count, 1)

    def test_real_arm_records_checks_and_only_hands_off_a_pass(self):
        plan = {'runtime_requirements': {'ac_powermode': 0}}
        for name in ('ok', 'missing_topup', 'missing_obc', 'edited_triage', 'volume'):
            with self.subTest(case=name):
                root = self.root / name
                state = {}
                options = self.options()
                if name == 'missing_topup':
                    options['topup_completed_at'] = None
                    options['topup_source'] = None
                if name == 'missing_obc':
                    options['obc_off_attested_by'] = ''
                if name == 'edited_triage':
                    options['next_arm_triage']['checks']['meter_samples_clock']['status'] = 'fail'
                if name == 'volume':
                    options['volume_runner'] = FakeArmHost(0, ssd=True)
                with patch.object(session, 'w1_disk_check', return_value={'status': 'pass'}), \
                        patch.object(session.pilot, 'install', return_value={'exit_code': 0}) as install:
                    call = lambda: session._arm_and_install(root, state, self.root, plan, None,
                        now=time.time, w1_disk_config='synthetic', disk_gate=None, **options)
                    if name == 'ok':
                        self.assertEqual(call(), {'exit_code': 0})
                        install.assert_called_once()
                    else:
                        with self.assertRaisesRegex(ValueError, 'v4 arm refused'):
                            call()
                        install.assert_not_called()
                record = json.loads((root / 'staging/v4-arm-001.json').read_text())
                self.assertEqual(record['admitted'], name == 'ok')
                self.assertEqual(set(record['next_arm_triage']['checks']), set(cadence.TRIAGE_IDS))

    def test_stale_valid_triage_is_an_exposed_production_gap(self):
        # A truthful regression witness, NOT evidence that stale packets refuse.
        # The schema does not consume this timestamp or bind previous record bytes.
        options = self.options()
        options['next_arm_triage']['created_at_epoch_s'] = 1
        record = session.arm_checks(self.root, {'runtime_requirements': {'ac_powermode': 0}}, **options)
        self.assertTrue(record['admitted'])


class R1ChainTests(unittest.TestCase):
    def test_lane_shaped_export_backfills_contrast_and_real_kit_check(self):
        from scripts import align_r1_rehearsal as r1, align_r1_turn_counts_export as exporter
        from scripts import align_w1_budget_procedure as proc
        from tests.align import test_r1_rehearsal as rehearsal
        from tests.align.test_r1_turn_counts_export import write_bundles
        with tempfile.TemporaryDirectory(prefix='w1-smoke-r1-') as tmp, redirect_stdout(io.StringIO()):
            root = Path(tmp)
            with patch.object(r1, '_run', rehearsal.FakeWorld(step_d_rate=40.,
                    gated_decode_tokens=28000, gated_admitted_turns=7)):
                self.assertEqual(r1.run(rehearsal.R1Tests.args(None, tmp, synthetic=True)), 0)
            run = root / 'run'
            write_bundles(run, drop_bundle_key=True)
            slots = json.loads((root / 'registration/r1_slots.json').read_text())
            for key in ('admitted_turns', 'x7', 'phases_s'):
                slots['x_g'].pop(key, None)
            for row in slots['deadman_budget']:
                for key in ('turn_decode_counts', 'turn_completed', 'turn_counts_source_sha256'):
                    row.pop(key, None)
            (root / 'slots0.json').write_text(json.dumps(slots))
            counts, xg, final = (root / x for x in ('counts.json', 'slots1.json', 'slots2.json'))
            self.assertEqual(exporter.main(['--run-dir', str(run), '--out', str(counts)]), 0)
            self.assertEqual(proc.main(['backfill-x-g', '--r1-slots', str(root / 'slots0.json'),
                '--r1-result', str(run / 'r1_result.json'), '--out', str(xg)]), 0)
            self.assertEqual(proc.main(['backfill-turn-counts', '--r1-slots', str(xg),
                '--counts-export', str(counts), '--out', str(final)]), 0)
            slots = json.loads(final.read_text())
            inputs = rehearsal.R1Tests.bind_inputs(slots)
            (root / 'inputs.json').write_text(json.dumps(inputs))
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(proc.main(['derive-contrast', '--r1-slots', str(final),
                    '--inputs', str(root / 'inputs.json')]), 0)
            derived = json.loads(stdout.getvalue())
            self.assertEqual(derived['contrast_fit'], inputs['R1']['thermal_policy']['contrast_fit'])
            kit.require_ready(inputs, slots, synthetic=True)
            # The actual kit --check compares regenerated bytes. Only prospective
            # identity/registration readiness is replaced with explicit synthetic
            # readiness, and is tested separately against the actual candidate.
            with patch.object(kit, 'read_inputs', return_value=inputs), \
                    patch.object(kit, 'read_r1_slots', return_value=slots), \
                    patch.object(kit, 'read_w1_plan_bytes', return_value=None), \
                    patch.object(kit, 'require_w1_ready', side_effect=lambda *a:
                                 kit.require_ready(inputs, slots, synthetic=True)):
                kit.generate(root)
                self.assertEqual(kit.main(['--output-root', str(root), '--check']), 0)
                member = root / kit.KIT / 'stages/episodes-a/align-v4-episodes-a-e05.json'
                member.write_bytes(member.read_bytes() + b' ')
                with redirect_stderr(io.StringIO()):
                    self.assertNotEqual(kit.main(['--output-root', str(root), '--check']), 0)
            # A bad count export fails at the real CLI, not only at a helper.
            data = json.loads(counts.read_text())
            data[next(iter(data))]['turn_decode_counts'][0] = -1
            counts.write_text(json.dumps(data))
            with redirect_stderr(io.StringIO()):
                self.assertNotEqual(proc.main(['backfill-turn-counts', '--r1-slots', str(xg),
                    '--counts-export', str(counts), '--out', str(root / 'bad.json')]), 0)


class MeterPathTests(unittest.TestCase):
    def test_shared_launcher_and_supervisor_use_a_fake_stream(self):
        from joulewise.b5 import driver
        from tests.test_b5_driver import Harness
        from tests.test_b5_driver_p3 import FAKE_METER
        harness = Harness(self, g10=False)
        # Process-table observation is injected too: the sandbox's process
        # census is not a native MBP liveness qualification.
        harness.driver._group_census = lambda *a, **k: (True, [])
        harness.replace_chain('#!/bin/zsh -f\n/bin/sleep 1\nexit 0\n')
        calls = []
        def launch(request):
            argv = driver.production_seams(ROOT).meter_argv(request)
            calls.append(argv)
            self.assertEqual(argv[2], str(ROOT / 'scripts/km003c_monitor.py'))
            return [sys.executable, '-c', FAKE_METER, 'streaming', *argv[-2:]]
        import sys
        harness.meter_argv = launch
        self.assertEqual(harness.run(), harness.driver.EXIT_GO, harness.result())
        self.assertTrue(calls)
        saved = harness.hazard()['meter']
        self.assertTrue(saved['stop']['proven_stopped'])
        self.assertEqual(saved['streams'][0]['sha256'], hashlib.sha256(
            (harness.custody / saved['streams'][0]['path']).read_bytes()).hexdigest())

    def test_reader_gap_flags_only_affected_member_and_preserves_gpu_channel(self):
        from tests.align.test_km003c import fake_stream, episode, NS
        from joulewise.align.apple import km003c
        with tempfile.TemporaryDirectory(prefix='w1-smoke-meter-') as tmp:
            path = Path(tmp) / 'stream.jsonl'
            full = fake_stream(path)
            short = fake_stream(path, end=3000)  # reader died during member
            capture = lambda stream, end: km003c.capture_member([(path.name, stream)],
                member_span=(NS, end * NS), baseline_span=(NS, 2*NS), episode=episode())
            self.assertEqual(capture(full, 4)['status'], 'available')
            missing = capture(short, 4)
            self.assertEqual(missing['status'], 'missing')
            self.assertTrue(missing['flags'])
            self.assertTrue(missing['powermetrics_admissibility_unchanged'])


if __name__ == '__main__':
    unittest.main()
