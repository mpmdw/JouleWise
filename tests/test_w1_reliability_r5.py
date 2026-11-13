"""Round-5 delta witnesses; synthetic hosts, streams and R1 records only."""
import dataclasses
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.b5 import driver as hazard
from tests import test_w1_reliability_r2 as r2, test_w1_reliability_r3 as r3
from scripts import align_v4_session as session


class HostTests(r2.DriverCase):
    def test_unverified_left_off_is_recorded_as_incomplete_without_setter(self):
        h, host = self.make()
        def run(argv):
            result = host(argv)
            return dataclasses.replace(result, exit_code=1) if tuple(argv) == h.driver.NETWORK_TIME_QUERY_ARGV else result
        record = h.driver.restore_owed(h.plan, dataclasses.replace(h.census.probes(), run=run), {})
        self.assertFalse(record['ok'])
        self.assertFalse(record['network_time']['verified'])
        self.assertIsNone(record['network_time']['observed'])
        self.assertNotIn(h.driver.NETWORK_TIME_ON_ARGV, host.calls)

    def test_abandoned_launch_with_pending_launcher_defers_without_night_writes(self):
        h, host = self.make()
        h.night.mkdir(exist_ok=True)
        (h.night / h.driver.LAUNCH_ABANDONED_MARKER).write_text('{}')
        (h.night / 'launch.pending').write_text('{"pgid":123}')
        before = {p.name: p.read_bytes() for p in h.night.iterdir()}
        self.assertEqual(h.driver.dead_man(h.plan_path), 0)
        self.assertEqual({p.name: p.read_bytes() for p in h.night.iterdir()}, before)
        self.assertEqual(host.calls, [])

    def test_r1_refusal_vocabulary_reaches_terminal_result_without_values(self):
        h, _ = self.make()
        exited = h.driver._run_chain_once
        def with_payload(*args, **kwargs):
            result = exited(*args, **kwargs)
            path = h.night / 'align-r1/r1_result.json'
            path.parent.mkdir()
            path.write_text(json.dumps({'status': 'refused', 'error':
                'Refusal: runtime.step-30b: exit 1: incomplete thermal.start_gate_timeout '
                'episode.deadman:12345 thermal.unknown temperature=98765 /synthetic/private'}))
            return result
        h.driver._run_chain_once = with_payload
        self.assertEqual(h.run(), 0)
        record = h.result()
        self.assertEqual(record['chain_refused_phase'], 'step_30b')
        self.assertEqual(record['chain_refusal_codes'], ['episode.deadman', 'thermal.start_gate_timeout'])
        self.assertNotIn('98765', json.dumps(record))
        self.assertNotIn('/synthetic/private', json.dumps(record))

    def test_structured_summary_drops_unknown_or_malformed_fields(self):
        h, _ = self.make()
        for phase in ('/synthetic/private', 123, ['step_30b']):
            summary = h.driver._r1_refusal_summary({'refused_phase': phase,
                'refusal_codes': ['thermal.start_gate_timeout', 'private.value', 123, {}]})
            self.assertIsNone(summary['chain_refused_phase'])
            self.assertEqual(summary['chain_refusal_codes'], ['thermal.start_gate_timeout'])


class FrequencyTests(unittest.TestCase):
    def test_loaded_or_unknown_job_has_own_cause_without_setting_host_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'plan.json'
            path.write_text(json.dumps({'t0_epoch_s': session.time.time() + 3600,
                'hazard_window': {'thresholds': {'clock': r3.LIMITS}, 'T_stream_max_s': 5764}}))
            state = {'plan_path': str(path), 'plan_sha256': session.pilot.h.locator(path)['sha256']}
            for loaded in (True, False):
                host = r3.Host(0, job_absent=False)
                def run(argv):
                    result = host(argv)
                    if not loaded:
                        result.returncode = 1
                    return result
                record = session.frequency_word_preflight(state, reader=host.read, runner=run)
                self.assertFalse(record['ok'])
                self.assertEqual(record['cause'], 'prepare.night_job_loaded' if loaded else 'prepare.night_job_state_unavailable')
                self.assertEqual(len(host.calls), 1)


class MeterTests(unittest.TestCase):
    def test_empty_final_polls_preserve_nonempty_batch_age_and_validate_only_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'stream-001.jsonl'
            now, raw = [1000.], [1_000_000_000_000]
            header = {'k': 'h', 'status': 'streaming', 'start_raw_ns': raw[0], 'start_mono_ns': raw[0]}
            batch = {'k': 'b', 'n': 1, 'p': '00' * 20, 'rx': raw[0] - 5_000_000_000}
            empty = {'k': 'b', 'n': 0, 'p': '', 'rx': raw[0]}
            path.write_text('\n'.join(map(json.dumps, [header, batch, empty, empty])) + '\n')
            live = hazard.MeterLiveness(Path(tmp), clock=lambda: now[0], raw_clock=lambda: raw[0])
            with mock.patch.object(hazard.json, 'loads', wraps=json.loads) as loads:
                self.assertIsNone(live.check())
                self.assertEqual(loads.call_count, 2)
            self.assertEqual(live.last_sample, 995.)
            # Empty polls alone must not refresh liveness or turn old samples fresh.
            now[0] += 601
            raw[0] += 601_000_000_000
            with path.open('a') as out:
                out.write(json.dumps(empty) + '\n')
            self.assertIsNotNone(live.check())
            self.assertEqual(live.last_sample, 995.)

    def test_malformed_nonempty_final_batch_is_not_replaced_by_an_earlier_batch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'stream-001.jsonl'
            rows = [{'k': 'h', 'status': 'streaming', 'start_raw_ns': 0, 'start_mono_ns': 0},
                    {'k': 'b', 'n': 1, 'p': '00' * 20, 'rx': 1},
                    {'k': 'b', 'n': 1, 'p': 'bad', 'rx': 2}, {'k': 'b', 'n': 0, 'p': '', 'rx': 3}]
            path.write_text('\n'.join(map(json.dumps, rows)) + '\n')
            live = hazard.MeterLiveness(Path(tmp), clock=lambda: 10., raw_clock=lambda: 10_000_000_000)
            live.check()
            self.assertIsNone(live.last_sample)


if __name__ == '__main__':
    unittest.main()
