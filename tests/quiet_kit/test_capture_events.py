"""Event stamps are flushed before GPU work and synced once on capture exit."""
import dataclasses
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from joulewise.clock import ClockStamp
from joulewise.quiet_kit import capture
from .fixtures import EPOCH, RAW, plist_stream

REPO = Path(__file__).resolve().parents[2]


class CaptureEventTests(unittest.TestCase):
    def test_on_stamp_has_no_fsync_before_gpu_and_capture_syncs_once(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-event-sync-') as tmp:
            out = Path(tmp)
            stamp = ClockStamp(EPOCH, RAW, RAW, 0., 0.)
            hw = SimpleNamespace(cleanup=Mock())
            def sampler(*args):
                (out/'raw').mkdir()
                (out/'raw/powermetrics.plist').write_bytes(plist_stream([
                    {'start_s': EPOCH, 'end_s': EPOCH+.1, 'gpu_power': 2.}]))
                return SimpleNamespace(clock=SimpleNamespace(stamp=lambda: stamp),
                    stamps={'sampling_started': stamp},
                    close=lambda: {'clock_anchor': {'method': 'desk'}, 'span_s': .1, 'cadence_median_ms': 100.})
            read = capture.read_bytes
            def read_bytes(path):
                if str(path) == '/usr/bin/powermetrics': return b'desk binary binding'
                return read(path)
            work = []
            def gpu(seconds, buffers):
                # The row is visible to a separate open before any GPU work.
                event = json.loads((out/'events.jsonl').read_text().splitlines()[-1])
                self.assertTrue(event['event_type'].endswith('_command_on'))
                sync.assert_not_called()
                work.append(event['event_type'])
            with (patch.object(capture, 'Hardware', return_value=hw),
                  patch.object(capture, 'Sampler', side_effect=sampler),
                  patch.object(capture, 'read_bytes', side_effect=read_bytes),
                  patch.object(capture, 'atomic_json'),
                  patch('joulewise.quiet_kit.capture.os.fsync') as sync,
                  patch('joulewise.quiet_kit.capture.time.sleep'),
                  patch('joulewise.quiet_kit.capture.importlib.metadata.version', return_value='desk'),
                  patch('joulewise.powermetrics_fiducial.allocate_matmul_buffers', return_value=()),
                  patch('joulewise.powermetrics_fiducial.run_matmul_pulse', side_effect=gpu),
                  patch('joulewise.powermetrics_fiducial.WARMUP_PULSE_COUNT', 1),
                  patch('joulewise.powermetrics_fiducial.pulse_schedule', return_value=[(0., 1.)]),
                  patch('joulewise.powermetrics_fiducial.instrument_evidence', return_value={'reasons': []}),
                  patch('joulewise.quiet_kit.fiducial.derive', return_value={}),
                  patch('joulewise.quiet_kit.fiducial.report', return_value={})):
                self.assertEqual(capture.main(['--out', str(out)]), 0)
                sync.assert_called_once()
            self.assertEqual(work, ['warmup_command_on', 'pulse_command_on'])
            self.assertEqual(json.loads((out/'events.jsonl').read_text().splitlines()[-1])['event_type'], 'sampling_stopped')

