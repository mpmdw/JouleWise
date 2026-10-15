"""Production hazard adapters driven by raw fixture replies, never live probes."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.hazards import base, contention
from joulewise.agent_identity import ProcessInfo
from joulewise.quiet_kit.hardware import Hardware
from joulewise.quiet_kit.paths import read_json
from joulewise.quiet_kit.readers import flag_segments
from joulewise.quiet_kit.runner import Runner
from joulewise.quiet_kit.schedule import BY_ID
from tests.hazards.fakes import FakeClocks, FakeSmc, battery_bytes, update_time
from .fakes import FakeHardware
from .fixtures import ps_bytes

REPO = Path(__file__).resolve().parents[2]


class ProductionHazardPlumbingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='quiet-kit-hazard-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.battery = battery_bytes('float-20261005-desk.ioreg')
        self.clocks = FakeClocks(wall_s=update_time(self.battery)+10, read_cost_ns=0, drift_word=0)
        self.started_ns = self.clocks.raw_ns
        self.current, self.thermal, self.cpu_rate = 0, 0, 0.
        self.agent = False
        self.calls = []
        self.hw = Hardware(REPO, sys.executable)
        self.hw.now = lambda: (self.clocks.raw_ns-self.started_ns)/1e9
        self.ctx_index = 0
        def context(directory=None, **kw):
            self.ctx_index += 1
            return base.Context(run=self.run_reply, clocks=self.clocks, raw_dir=directory,
                                label=f'probe-{self.ctx_index}')
        self.hw.ctx = context
        smc = patch('joulewise.hazards.smc.read_once', side_effect=FakeSmc(self.clocks, current=lambda t: self.current))
        smc.start()
        self.addCleanup(smc.stop)
        # Host ticks are a hardware seam; keep the actual raw ps parser and
        # contention accounting, while forbidding any host kernel read.
        take = contention.take_snapshot
        def snapshot(ctx, **kw):
            kw['host_reader'] = None
            return take(ctx, **kw)
        patcher = patch('joulewise.hazards.contention.take_snapshot', side_effect=snapshot)
        patcher.start()
        self.addCleanup(patcher.stop)
        for target in ('subprocess.Popen', 'joulewise.hazards.contention._host_functions'):
            guard = patch(target, side_effect=AssertionError('live hardware seam: '+target))
            guard.start()
            self.addCleanup(guard.stop)
        # Keep the real agent matcher, with a fixture kernel identity for
        # the production-shaped pgrep row (on either supported desk OS).
        info = ProcessInfo(424242, 1, 424242, '/fixture/claude', ('/fixture/claude',))
        for target in ('joulewise.agent_identity._darwin_inspect', 'joulewise.agent_identity._linux_inspect'):
            inspector = patch(target, side_effect=lambda pid: info if pid == 424242 else None)
            inspector.start()
            self.addCleanup(inspector.stop)

    def run_reply(self, argv, timeout):
        argv = tuple(argv)
        self.calls.append(argv)
        if argv[0].endswith('notifyutil'):
            raw = f'com.apple.system.thermalpressurelevel {self.thermal}\n'.encode()
        elif argv[0].endswith('pgrep'):
            return base.Completed(argv, 0 if self.agent else 1, b'424242 /fixture/claude\n' if self.agent else b'', b'')
        elif argv[0].endswith('ps'):
            raw = ps_bytes(100+self.cpu_rate*self.hw.now())
        elif 'AppleSmartBattery' in argv:
            raw = self.battery
        elif 'IOHIDSystem' in argv:
            raw = b'    "HIDIdleTime" = 1234567890\n'
        elif 'IOUSB' in argv:
            raw = b'POWER-Z KM003C\n'
        elif argv[0].endswith('sysctl'):
            raw = b'25G83\n'
        else:
            raw = b''
        return base.Completed(argv, 0, raw, b'')

    def parameters(self, **extra):
        return {'cancel': lambda: False, 'record_only': False, 'duration_s': 0,
                'archive': str(self.root), 'planned_bytes': 8*1024**3,
                'tree_roots': [os.getpid()], 'deadline': 200., **extra}

    def probe(self, name, **extra):
        return self.hw.probe(name, self.root/name, self.parameters(**extra))

    def test_battery_500ma_and_thermal_two_production_verdicts(self):
        self.current = 500
        battery = self.probe('battery')
        self.assertEqual(battery['verdict']['status'], 'REFUSE')
        self.assertIn('500', str(battery['verdict']['reasons']))
        self.thermal = 2
        thermal = self.probe('thermal')
        self.assertEqual(thermal['verdict']['status'], 'REFUSE')
        watched = self.hw.watch(self.root)
        self.assertEqual(watched['thermal_level'], 2)
        self.assertEqual(watched['battery_current_ma'], 500)
        data = flag_segments({'segments': [{'start': {'raw_s': 0}, 'end': {'raw_s': 2}}]},
                             [{'stamp': {'monotonic_raw_ns': 0}, 'physics': watched}])
        self.assertEqual(data['segments'][0]['hazard_flags'], ['battery current over 200 mA', 'thermal pressure'])
        # Test-level disclosure is independently present (P15).
        runner = Runner(REPO, self.root, sys.executable, FakeHardware().seams())
        flags = runner._flags({}, [{'stamp': {}, 'physics': watched}], {}, {})
        self.assertIn('thermal pressure during test', [f['reason'] for f in flags])

    def test_disk_reserves_planned_bytes_plus_twenty_gib(self):
        statvfs = SimpleNamespace(f_bavail=27*1024**3//4096, f_frsize=4096, f_blocks=100*1024**3//4096)
        with patch('os.statvfs', return_value=statvfs):
            out = self.probe('disk')
        self.assertEqual(out['verdict']['status'], 'REFUSE')
        self.assertIn('28', str(out['verdict']['reasons']))

    def test_battery_watcher_excludes_overlapping_clock_reading(self):
        self.current = 500
        watched = self.hw.watch(self.root)
        self.assertEqual(watched['thermal_level'], 0)
        data = flag_segments({'clock': [{'anchor': {'monotonic_raw_ns': 1_000_000_000}}]},
                             [{'stamp': {'monotonic_raw_ns': 0}, 'physics': watched}])
        self.assertEqual(data['clock_clean'], [])

    def test_three_unmeasured_readings_are_required_before_flagging(self):
        fake = FakeHardware()
        fake.bad_probes = {'battery': ['UNMEASURED']*3}
        runner = Runner(REPO, self.root/'unmeasured', sys.executable, fake.seams(), scale=.001, emit=lambda _: None)
        result = runner.preflight(BY_ID['m9-time-server'], runner.new_attempt('m9-time-server'))
        self.assertEqual(sum(r['module'] == 'battery' for r in result['reads']), 3)
        self.assertEqual(sum(r['hazard'] == 'battery' for r in result['waits']), 2)
        self.assertTrue(any('3 consecutive' in f['reason'] for f in result['flags']))

    def test_contention_clean_dwell_requires_180s_and_point_three_refuses(self):
        clean = self.probe('contention', duration_s=180)
        self.assertEqual(clean['verdict']['status'], 'PASS')
        self.assertGreaterEqual(clean['measurement']['values']['clean_run_s'], 180)
        self.cpu_rate = .3
        dirty = self.probe('contention', record_only=True, duration_s=20)
        self.assertNotEqual(dirty['verdict']['status'], 'PASS')
        intervals = dirty['measurement']['values']['intervals']
        self.assertTrue(any(not r['clean'] for r in intervals))
        self.assertAlmostEqual(intervals[-1]['max_outside']['cpu_s_per_s'], .3, places=6)

    def test_production_census_and_analysis_agents_and_targeted_hid(self):
        self.agent = True
        self.assertFalse(self.hw.census(self.root)['clean'])
        self.agent = False
        self.assertTrue(self.hw.census(self.root)['clean'])
        old = self.run_reply
        def reply(argv, timeout):
            if argv[0].endswith('ps'):
                return base.Completed(tuple(argv), 0, ps_bytes(100, name='mediaanalysisd'), b'')
            return old(argv, timeout)
        self.hw.ctx = lambda directory=None, **kw: base.Context(run=reply, clocks=self.clocks)
        with patch('joulewise.quiet_kit.hardware.coregraphics_display_state', return_value=({'asleep': True}, None)):
            out = self.hw.observe(self.root)
        self.assertTrue(out['analysis_agents']['mediaanalysisd']['present'])
        self.assertEqual(out['analysis_agents']['mediaanalysisd']['cpu_seconds'], 100.)
        self.assertEqual(out['hid_idle_ns'], 1234567890)
        self.assertIn(('/usr/sbin/ioreg', '-r', '-c', 'IOHIDSystem', '-k', 'HIDIdleTime', '-d', '1'), self.calls)
        self.assertTrue(out['meter_present'])

    def test_every_measured_hazard_reaches_runner_wait_and_final_census(self):
        # Use actual production verdicts as the runner's first reading,
        # then a PASS so each wait is finite and independently observable.
        for name in ('battery', 'thermal', 'disk', 'contention'):
            with self.subTest(name=name):
                self.current, self.thermal = 500, 2
                if name == 'disk':
                    with patch('os.statvfs', return_value=SimpleNamespace(f_bavail=27*1024**3//4096,
                               f_frsize=4096, f_blocks=100*1024**3//4096)):
                        bad = self.probe(name)
                elif name == 'contention':
                    self.cpu_rate = .3
                    bad = self.probe(name, record_only=True, duration_s=20)
                else:
                    bad = self.probe(name)
                self.assertNotEqual(bad['verdict']['status'], 'PASS')
                fake = FakeHardware()
                production = fake.probe
                seen = []
                def probe(module, directory, parameters):
                    self.assertEqual(parameters['duration_s'],
                                     {'contention': 180, 'instrument': 60, 'clock': 60}.get(module, 0))
                    seen.append(module)
                    if module == name and seen.count(name) == 1: return bad
                    return production(module, directory, parameters)
                fake.probe = probe
                runner = Runner(REPO, self.root/name/'runner', sys.executable, fake.seams(), scale=.001, emit=lambda _: None)
                attempt = runner.new_attempt('m9-time-server')
                result = runner.preflight(BY_ID['m9-time-server'], attempt)
                self.assertIn(name, [r['hazard'] for r in result['waits']])
                self.assertEqual(set(seen), {'battery', 'thermal', 'disk', 'contention', 'instrument', 'clock'})
                self.assertGreaterEqual(fake.census_calls, 3)  # retry, next cycle, final census

