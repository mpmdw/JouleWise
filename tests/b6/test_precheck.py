import dataclasses
import io
from contextlib import redirect_stdout
from fractions import Fraction
import json
import os
from pathlib import Path
import signal
from types import SimpleNamespace
from unittest import mock

from joulewise.b5 import plan
from joulewise.b6 import precheck as p, fingerprint
from joulewise.b6.acceptance_interface import AcceptanceResult, StubAcceptance
from joulewise.hazards import battery, clock, instrument
from joulewise.hazards.base import Context, PASS
from scripts import fixture_orphan_census as census
from tests.hazards.fakes import FakeClocks, Runner, completed, FAKE_POWERMETRICS
from tests.b6.support import DeskCase, ROOT, PACKS, fp, synthetic_checkout, fake_environment
from tests.b6 import support


class FakeAcceptance(StubAcceptance):
    def __init__(self, nominal=False, margin=False, structural=False, flags=()):
        self.nominal, self.margin, self.structural, self.flags = nominal, margin, structural, flags
        self.preparations = []
        self.evaluations = []

    def prepare(self, **kwargs):
        self.preparations.append(kwargs)
        return 'prepared'

    def evaluate(self, prepared, evidence):
        self.evaluations.append(evidence)
        failed = any(member.status == 'failed' for stage in evidence.stages for member in stage.members)
        exclude = self.margin if failed else self.nominal
        return AcceptanceResult('EXCLUDE' if exclude else 'ACCEPT', ('test exclusion',) if exclude else (),
                                self.flags, self.structural)


class PrecheckTests(DeskCase):
    def setUp(self):
        super().setUp()
        self.measurement, self.state, self.model = synthetic_checkout(self.root)

    def check(self, *, acceptance=None, smoke=False, out=None, **kwargs):
        ctx, seams, table = fake_environment(self.measurement, **kwargs)
        if not smoke:
            index = self.state / 'smoke-passes.jsonl'
            if not index.exists():
                fingerprint.record_pass(fp(), self.root, index)
        return p.run_precheck(PACKS['alpha'], self.measurement, self.state, ctx=ctx, seams=seams,
                              acceptance=acceptance, out=out), ctx

    def test_01_clock_fit_exact_boundary_steps_boot_and_span(self):
        limits = p.PRECHECK_DEFAULTS['clock']

        def series(rate, count=61, spacing=10, step=0):
            rows = []
            for i in range(count):
                t = i * spacing * 10**9
                rows.append({'anchor': {'monotonic_raw_ns': t, 'anchor_ns': 10**18 + Fraction(str(rate)) * t / 10**6
                                        + (step if i >= count // 2 else 0), 'read_skew_ns': 100},
                             'frequency': {'raw_word': 0}, 'error': None})
            return rows
        for rate, expected in ((2, []), (4, ['clock.rate_above_budget']), (3.63059, []),
                               (3.6306, ['clock.rate_above_budget']), (3.6307, ['clock.rate_above_budget']),
                               (Fraction(5000, 335) - Fraction(1, 4), ['clock.rate_above_budget']),
                               (15, ['clock.rate'])):
            reading, codes = p.clock_rate(series(rate), 'boot', 'boot', limits)
            self.assertEqual(codes, expected)
            # 0.001 ppm resolves 0.335 us over 335 s, below the 125 us anchor reads.
            self.assertAlmostEqual(reading['rate_ppm'], float(rate), delta=1e-3)
        self.assertIn('clock.step', p.clock_rate(series(2, step=2_000_000), 'boot', 'boot', limits)[1])
        self.assertIn('clock.boot_changed', p.clock_rate(series(2), 'boot', 'other', limits)[1])
        self.assertIn('clock.unmeasured', p.clock_rate(series(2, count=41, spacing=1), 'boot', 'boot', limits)[1])
        samples = series(2)
        samples[2]['anchor'] = None
        samples[2]['error'] = 'read skew'
        self.assertEqual(p.clock_rate(samples, 'boot', 'boot', limits)[1], [])

    def test_02_battery_and_thermal(self):
        for kwargs, code in (({'battery_name': 'on-battery-synthetic-from-real.ioreg'}, 'battery.float'),
                             ({'current_ma': 250}, 'battery.float'), ({'thermal_level': 1}, 'thermal.pressure')):
            result, _ = self.check(**kwargs)
            self.assertIn(code, [item['code'] for item in result['would_refuse']])
        result, _ = self.check(current_ma=150)
        self.assertEqual(result['would_refuse'], [])
        self.assertEqual(result['readings']['battery']['verdict']['status'], PASS)

    def test_03_assertion_wait_custom_sleep_record_only(self):
        result, _ = self.check(assertion=False)
        self.assertIn('power.no_sleep_assertion_absent', [item['code'] for item in result['would_refuse']])
        clean, _ = self.check()
        self.assertIn('sleep 1', clean['readings']['power']['custom']['stdout'])
        self.assertEqual(clean['decision'], 'START')

    def test_04_initial_final_agents_and_hid(self):
        # At the census seam, retain an actual agent identity without consulting
        # the live kernel for our deliberately synthetic pid.
        with mock.patch('joulewise.hazards.arm.agent_identity.filter_census',
                        side_effect=lambda text, **kwargs: SimpleNamespace(ignored=[], kept_text=text)):
            for kwargs in ({'initial_agent': True}, {'final_agent': True}):
                result, _ = self.check(**kwargs)
                self.assertEqual(result['decision'], 'WAIT')
                self.assertTrue(any(item['hazard'] == 'agents' for item in result['would_refuse']))
        self.assertEqual(self.check(idle_s=900)[0]['decision'], 'START')
        recent, _ = self.check(idle_s=120)
        self.assertEqual(recent['decision'], 'START')
        self.assertIn('agents.hid_recent', [row['code'] for row in recent['predicted_flags']])

    def test_05_contention_dwell_no_wall_sleep(self):
        result, ctx = self.check(busy=True)
        self.assertIn('contention.dwell', [item['code'] for item in result['would_refuse']])
        self.assertGreaterEqual(result['readings']['contention']['measurement']['values']['elapsed_s'], 600)
        clean, _ = self.check()
        self.assertGreaterEqual(clean['readings']['contention']['measurement']['values']['clean_run_s'], 180)
        self.assertLess(clean['readings']['contention']['measurement']['values']['elapsed_s'], 181)
        self.assertTrue(ctx.clocks.sleeps)

    def test_06_orphan_signatures_and_uid_kill_seam(self):
        signatures = census.load_signatures()
        rows = []
        for pid, path in ((100, 'tests/fixtures/fake_powermetrics_process.py'),
                          (101, 'tests/fixtures/hazards/instrument/fake_powermetrics.py')):
            command = f'/opt/homebrew/bin/python3.13 /tmp/synthetic/{path} -n 300'
            line = f'{pid} 1 Thu Sep 3 10:20:30 2026 100 {command}\n'
            matched = census.census(line, signatures)
            self.assertEqual(len(matched), 1)
            rows.extend(matched)
            self.assertEqual(census.census(line.replace(f'{pid} 1 ', f'{pid} 2 '), signatures), [])
        self.assertEqual(census.census('120 1 Thu Sep 3 10:20:30 2026 100 /usr/bin/sleep 30\n', signatures), [])
        calls = []
        ctx = Context(clocks=FakeClocks())
        result = p.reap_orphans(ctx, collect=lambda: rows, process_uid=lambda pid: 123,
                               uid=123, kill=lambda pid, sig: calls.append((pid, sig)))
        self.assertEqual(calls, [(100, signal.SIGTERM), (100, signal.SIGKILL),
                                 (101, signal.SIGTERM), (101, signal.SIGKILL)])
        self.assertEqual(len(result['rows']), 2)
        self.assertEqual(p.reap_orphans(ctx, collect=lambda: rows, process_uid=lambda pid: 999,
                                       uid=123, kill=lambda *args: self.fail('foreign uid'))['rows'], [])

    def test_07_disk_smoke_budget_and_remedy(self):
        result, _ = self.check(smoke=True, free_gib=60)
        low = next(item for item in result['would_refuse'] if item['code'] == 'disk.low')
        self.assertEqual(low['remedy'], 'wake_orchestrator')
        self.assertEqual(low['limit']['planned_bytes'], 43 * 1024**3 + 6 * 190_840_832 * 2)
        self.assertEqual(self.check(free_gib=70)[0]['decision'], 'START')

    def test_08_real_cadence_parser_fake_binary(self):
        # Every child is owned by instrument.measure and reaped before return;
        # no real sampler or signal to an unrelated process is used.
        base = json.loads((ROOT / 'tests/fixtures/hazards/instrument/cadence-20261004-block3-idle.json').read_text())
        for cadence in (255, 100):
            fixture = self.root / f'cadence-{cadence}.json'
            fixture.write_text(json.dumps({**base, 'elapsed_ns': [cadence * 10**6] * 300}))
            def capture(argv, timeout):
                output = io.StringIO()
                original_popen = instrument.subprocess.Popen

                def spawn(*args, **kwargs):
                    process = original_popen(*args, **kwargs)
                    self.processes.append(process)
                    return process
                # The process-table census is injected; the adapter's child is
                # the fake fixture we own and wait for in _child_main.
                with mock.patch.object(instrument, 'group_absent', return_value=(True, [])), \
                        mock.patch.object(instrument.subprocess, 'Popen', side_effect=spawn), redirect_stdout(output):
                    rc = instrument._child_main(argv[argv.index('--output'):])
                return completed(argv, output.getvalue().encode(), returncode=rc)
            with mock.patch.dict(os.environ, {'FAKE_PM_FIXTURE': str(fixture), 'FAKE_PM_SLEEP_S': '0',
                                             'FAKE_PM_FRAMES': '300', 'FAKE_PM_EXIT': '0'}):
                os.environ.pop('FAKE_PM_SPAWN_ORPHAN', None)
                measurement = instrument.measure(Context(clocks=FakeClocks(), run=capture),
                                                 executable=str(FAKE_POWERMETRICS), privilege_prefix=())
            self.assertEqual(instrument.judge(measurement, instrument.DEFAULT_THRESHOLDS).status == PASS, cadence == 100)
            self.assertTrue(measurement.values['group_gone'])
        result, _ = self.check(cadence_ms=255)
        self.assertEqual(next(item for item in result['would_refuse'] if item['code'] == 'instrument.cadence')['remedy'],
                         'relaunch_in_production_context')

    def test_09_evicted_file_download_only_and_simulated_poll(self):
        ledger = self.root / 'synthetic-ledger.jsonl'
        rows = [{'custody_locator': 'capture', 'artifact_sha256': {'evidence.json': 'a'*64}}]
        ledger.write_text(json.dumps(rows))
        for clears in (True, False):
            clocks = FakeClocks()
            calls = []
            runner = Runner({'/usr/bin/brctl': lambda argv: (calls.append(argv) or completed(argv))}, real_python=False)
            def lstat(path):
                self.assertEqual(Path(path), self.root / 'capture/evidence.json')
                return SimpleNamespace(st_flags=0 if clears and clocks.sleeps else 0x40000000)
            with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('hydrating file read')):
                reading, flags = p.restore_evicted(json.loads(ledger.read_text()), self.root,
                                                   ctx=Context(run=runner, clocks=clocks), lstat=lstat)
            self.assertEqual(calls, [('/usr/bin/brctl', 'download', str(self.root / 'capture/evidence.json'))])
            self.assertEqual(bool(flags), not clears)
            if not clears:
                self.assertEqual(flags[0]['observed']['count'], 1)
                self.assertEqual(sum(clocks.sleeps), 600)
        directory = SimpleNamespace(st_flags=0x40000000, st_mode=0o040755)
        runner = Runner({}, real_python=False)
        p.restore_evicted(rows, self.root, ctx=Context(run=runner, clocks=FakeClocks()),
                          lstat=lambda path: directory)
        self.assertEqual(runner.calls, [])

    def test_10_model_hash_mismatch(self):
        self.assertIsNone(self.check()[0]['certain_exclusion'])
        self.model.write_bytes(b'synthetic weightX')
        result, _ = self.check()
        self.assertEqual(result['decision'], 'DO_NOT_START')
        self.assertEqual(result['certain_exclusion']['source'], 'model_hash')
        self.assertIn('model.hash_mismatch', result['certain_exclusion']['reasons'][0])

    def test_11_acceptance_nominal_margin_and_stub(self):
        a = FakeAcceptance(nominal=True)
        result, _ = self.check(acceptance=a)
        self.assertEqual(result['decision'], 'DO_NOT_START')
        self.assertEqual(len(a.preparations), 1)
        a = FakeAcceptance(margin=True)
        result, _ = self.check(acceptance=a)
        self.assertEqual(result['decision'], 'START')
        self.assertEqual(result['margin']['status'], 'thin')
        self.assertEqual(result['margin']['excluding_placements'], [s.stage_id for s in a.evaluations[0].stages
                                                                  if s.kind == 'campaign_collection'])
        # First 3-member reference placement spills five losses into science.
        ref = next(e for e in a.evaluations[1:] if e.stages[4].members and e.stages[4].members[0].status == 'failed')
        self.assertEqual(sum(m.status == 'failed' for s in ref.stages for m in s.members), 8)
        result, _ = self.check(acceptance=StubAcceptance())
        self.assertEqual(result['decision'], 'START')
        self.assertEqual(result['acceptance']['status'], 'unavailable')
        self.assertIn('precheck.acceptance_unavailable', [f['code'] for f in result['predicted_flags']])

    def test_12_full_session_counts_valid_median_and_ledger_adapter(self):
        rows = [{'sequence': i, 'disposition': 'invalid' if i % 5 == 0 else 'valid',
                 'exact_bound_lexeme_s': str(Fraction(i, 1000))} for i in range(1, 31)]
        # Use decimal lexemes, just as the ledger does.
        for row in rows:
            row['exact_bound_lexeme_s'] = str(row['sequence'] / 1000)
        for pack, count in (('alpha', 125), ('beta', 125), ('gamma', 107)):
            evidence = p.synthetic_session(ROOT / 'configs/campaigns' / PACKS[pack], ROOT, rows, {})
            self.assertEqual(sum(len(s.members) for s in evidence.stages), count)
            self.assertEqual(evidence.captures[0].bound_ms, 15)
            self.assertTrue(all(c.synthetic for c in evidence.captures))
        empty = p.synthetic_session(ROOT / 'configs/campaigns' / PACKS['alpha'], ROOT, [], {})
        self.assertIsNone(empty.captures[0].bound_ms)
        result, _ = self.check()
        self.assertIn('precheck.no_valid_capture', [f['code'] for f in result['predicted_flags']])
        # Adapter reuses existing parse/observation calls, never historical byte replay.
        from joulewise import calibration_ledger as ledger
        with mock.patch.object(ledger, '_parse_ledger', return_value=(['receipt'], set())) as parsed, \
                mock.patch.object(ledger, '_attempts_and_observations', return_value=(['observation'], [], set())) as observed, \
                mock.patch.object(ledger, '_custody_observations', return_value=[SimpleNamespace(sequence=1)]):
            self.assertEqual(len(p.ledger_rows(self.measurement / plan.DEFAULT_LEDGER_RELATIVE)), 1)
            parsed.assert_called_once()
            observed.assert_called_once_with(['receipt'])
        self.assertEqual(p.ledger_rows(self.root / 'missing'), [])

    def test_acceptance_uses_session_pack_roster_with_alpha_registration(self):
        from joulewise.b5.harvest import build_roster, l4_exclusion_inputs
        from joulewise.b6.acceptance import ACCEPTANCE

        registration = support.registration_dir(self.root / 'cross-pack')
        document = support.document()
        document.update(pack_id=PACKS['alpha'], registered_commit=fp()['code_commit'])
        support.write_json(registration / 'acceptance.json', document)
        ledger = self.root / 'capture-list.jsonl'
        ledger.write_text('')
        rows = [{'sequence': i, 'disposition': 'valid', 'exact_bound_lexeme_s': '0.028'}
                for i in range(1, 25)]
        for pack in ('beta', 'gamma'):
            with self.subTest(pack=pack):
                ctx, seams, _ = fake_environment(ROOT)
                acceptance = mock.Mock(wraps=ACCEPTANCE)
                with mock.patch.object(p, 'model_files', return_value=({'measured': {}}, [])), \
                        mock.patch.object(p, 'runtime_versions', return_value={}), \
                        mock.patch.object(p, 'ledger_rows', return_value=rows):
                    result = p.run_precheck(PACKS[pack], ROOT, self.state, ctx=ctx, seams=seams,
                                            registration_dir=registration, ledger=ledger, acceptance=acceptance)
                self.assertEqual(result['acceptance']['nominal']['verdict'], 'ACCEPT')
                self.assertIsNone(result['certain_exclusion'])
                self.assertEqual(result['decision'], 'START')
                pack_root = ROOT / 'configs/campaigns' / PACKS[pack]
                acceptance.prepare.assert_called_once()
                self.assertEqual(acceptance.prepare.call_args.kwargs['pack_root'], pack_root)
                prepared = acceptance.evaluate.call_args_list[0].args[0]
                expected, _ = l4_exclusion_inputs(build_roster(pack_root, ROOT), {}, plan_id=None, attempt=None)
                self.assertEqual(prepared.roster, expected)
                self.assertTrue(prepared.roster['cells'])

    def test_13_precedence_exit_codes_and_create_once(self):
        out = self.root / 'precheck.json'
        for kwargs, expected in (({'acceptance': FakeAcceptance(nominal=True), 'current_ma': 250}, 20),
                                 ({'current_ma': 250}, 10), ({}, 0)):
            result, _ = self.check(**kwargs)
            self.assertEqual(p.exit_code(result), expected)
            if expected == 20:
                self.assertTrue(result['would_refuse'])
                self.assertIn('instrument', result['readings'])
        result, _ = self.check(out=out)
        self.assertEqual(json.loads(out.read_text()), json.loads(json.dumps(result)))
        with self.assertRaises(FileExistsError):
            self.check(out=out)
        self.assertEqual(p.PENDING, tuple(result['pending']))
        # The CLI's raw directory retains exact stdout and stderr for every
        # executed probe, including the two agent census calls.
        ctx, seams, _ = fake_environment(self.measurement)
        ctx.raw_dir = self.root / 'raw'
        raw_result = p.run_precheck(PACKS['alpha'], self.measurement, self.state, ctx=ctx, seams=seams)
        self.assertEqual(raw_result['decision'], 'START')
        self.assertEqual(len(list(ctx.raw_dir.glob('probe-*.stdout'))), len(ctx.run.calls))
        self.assertEqual(len(list(ctx.raw_dir.glob('probe-*.stderr'))), len(ctx.run.calls))

    def test_f1_directory_model_folded_hash_and_changed_byte(self):
        from joulewise.provenance import model_artifact_identity
        model = self.measurement / 'directory-model'
        model.mkdir()
        (model / 'weights.bin').write_bytes(b'weights')
        (model / 'config.json').write_bytes(b'{}')
        digest = model_artifact_identity(str(model))['folded_sha256']
        registration = self.measurement / p.REGISTRATION_RELATIVE / 'identity_pins.json'
        pins = json.loads(registration.read_text())
        pins['units']['test'].update(model_source=str(model), model_artifact_sha256=digest)
        registration.write_text(json.dumps(pins))
        tree = json.loads((self.measurement / 'configs/campaigns' / PACKS['alpha'] / 'plan_tree.json').read_text())
        for dispatch in plan.resolve_stage_dispatches(tree, self.measurement):
            directory = self.measurement / dispatch.config_dir
            manifest = json.loads((directory / 'order_manifest.json').read_text())
            for entry in manifest['executed_order']:
                (directory / entry['config']).write_text(json.dumps({'model': {'source': str(model)}}))
        result, _ = self.check()
        self.assertEqual(result['decision'], 'START')
        self.assertIsNone(result['certain_exclusion'])
        self.assertEqual(result['readings']['model_files']['measured'][str(model)], digest)
        (model / 'weights.bin').write_bytes(b'weightX')
        result, _ = self.check()
        self.assertEqual(result['decision'], 'DO_NOT_START')
        self.assertEqual(result['certain_exclusion']['reasons'], [f'model.hash_mismatch: {model}'])

    def test_f4_missing_capture_is_reported_without_polling(self):
        rows = [{'custody_locator': 'capture', 'artifact_sha256': {'missing.json': 'a'*64}}]
        path = self.root / 'capture/missing.json'
        runner = Runner({}, real_python=False)
        clocks = FakeClocks()
        with mock.patch('os.lstat', side_effect=FileNotFoundError(str(path))) as lstat:
            reading, flags = p.restore_evicted(rows, self.root, ctx=Context(run=runner, clocks=clocks),
                                               lstat=lstat)
        self.assertEqual(clocks.sleeps, [])
        self.assertEqual(runner.calls, [])
        lstat.assert_called_once_with(path)
        self.assertEqual(reading['missing'], [str(path)])
        self.assertEqual(reading['unavailable'], [str(path)])
        self.assertEqual(flags[0]['code'], 'calibration.historical_custody_unmeasured')

    def test_f5_unreadable_or_absent_ledger_is_a_flag(self):
        ledger = self.measurement / plan.DEFAULT_LEDGER_RELATIVE
        for content in ('{not json', None):
            with self.subTest(content=content):
                if content is None:
                    ledger.unlink()
                else:
                    ledger.write_text(content)
                result, _ = self.check()
                self.assertEqual(result['decision'], 'START')
                flag = next((f for f in result['predicted_flags'] if f['code'] == 'precheck.ledger_unreadable'), None)
                self.assertIsNotNone(flag)
                self.assertTrue(flag['observed'])
                self.assertEqual(result['would_refuse'], [])

    def test_f6_sigkill_requires_same_pid_signature_and_parent(self):
        row = {'pid': 100, 'ppid': 1, 'signature': 'fixture'}
        for refreshed, kill_expected in (([], False), ([{**row, 'signature': 'other'}], False),
                                         ([{**row, 'ppid': 2}], False), ([row], True)):
            with self.subTest(refreshed=refreshed):
                collect = mock.Mock(side_effect=[[row], refreshed])
                calls = []
                ctx = Context(clocks=FakeClocks())
                p.reap_orphans(ctx, collect=collect, kill=lambda pid, sig: calls.append((pid, sig)),
                               process_uid=lambda pid: 123, uid=123)
                expected = [(100, signal.SIGTERM)] + ([(100, signal.SIGKILL)] if kill_expected else [])
                self.assertEqual(calls, expected)
                self.assertEqual(collect.call_count, 2)
        collect = mock.Mock(side_effect=[[row], OSError('ps failed')])
        calls = []
        reaped = p.reap_orphans(Context(clocks=FakeClocks()), collect=collect,
                                kill=lambda pid, sig: calls.append((pid, sig)), process_uid=lambda pid: 123, uid=123)
        self.assertEqual(calls, [(100, signal.SIGTERM)])
        self.assertIn('recensus failed', reaped['rows'][0]['outcome'])

    def test_f9a_clock_linearity_has_own_wait_code(self):
        samples = []
        for i in range(61):
            t = i * 10**9
            residual = 2_000_000 if i % 2 else -2_000_000
            samples.append({'anchor': {'monotonic_raw_ns': t, 'anchor_ns': 10**18 + residual,
                                       'read_skew_ns': 100}, 'error': None})
        limits = {**p.PRECHECK_DEFAULTS['clock'], 'step_ns': 10_000_000}
        reading, codes = p.clock_rate(samples, 'boot', 'boot', limits)
        self.assertEqual(codes, ['clock.linearity'])
        ctx, seams, _ = fake_environment(self.measurement)
        with mock.patch.object(p, 'clock_rate', return_value=(reading, codes)):
            result = p.run_precheck(PACKS['alpha'], self.measurement, self.state, ctx=ctx, seams=seams)
        wait = next(item for item in result['would_refuse'] if item['code'] == 'clock.linearity')
        self.assertEqual(wait['retry_after_s'], 600)

    def test_f9b_dispatch_error_excludes_and_skips_acceptance(self):
        tree = json.loads((self.measurement / 'configs/campaigns' / PACKS['alpha'] / 'plan_tree.json').read_text())
        dispatch = next(iter(plan.resolve_stage_dispatches(tree, self.measurement)))
        (self.measurement / dispatch.config_dir / 'order_manifest.json').unlink()
        out = self.root / 'dispatch-precheck.json'
        acceptance = FakeAcceptance()
        result, _ = self.check(out=out, acceptance=acceptance)
        self.assertEqual(result['decision'], 'DO_NOT_START')
        self.assertEqual(p.exit_code(result), 20)
        self.assertTrue(any(reason.startswith('plan.dispatch_unresolved:')
                            for reason in result['certain_exclusion']['reasons']))
        self.assertEqual(result['acceptance']['status'], 'skipped')
        self.assertEqual(acceptance.preparations, [])
        self.assertEqual(acceptance.evaluations, [])
        self.assertIsNone(result['margin'])
        self.assertIn('instrument', result['readings'])
        self.assertEqual(json.loads(out.read_text())['decision'], 'DO_NOT_START')

    def test_missing_identity_record_and_unmeasured_model_only_flag(self):
        (self.measurement / p.REGISTRATION_RELATIVE / 'identity_pins.json').unlink()
        result, _ = self.check()
        self.assertIsNone(result['certain_exclusion'])
        self.assertEqual(result['decision'], 'START')
        self.assertIn('model.identity_unpinned', [row['code'] for row in result['predicted_flags']])
        self.assertIn('model.source_unpinned', [row['code'] for row in result['predicted_flags']])
        _, errors = p.model_files(json.loads((self.measurement / 'configs/campaigns' /
            PACKS['alpha'] / 'plan_tree.json').read_text()), self.measurement, {}, identity=lambda source: {})
        self.assertTrue(errors)
        self.assertTrue(all(row.startswith('model.identity_unmeasured:') for row in errors))
