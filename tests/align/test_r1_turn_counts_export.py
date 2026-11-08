"""R1 -> W1 per-turn count export on synthetic lane-shaped bundles (no real data)."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import align_r1_rehearsal as r1
from scripts import align_r1_turn_counts_export as exporter
from scripts import align_v4_kit as kit
from scripts import align_w1_budget_procedure as procedure
from tests.align import test_r1_rehearsal as rehearsal


TURNS = 7


def write_bundles(run, *, finish='stop', last_finish='stop', mutate=None, compress=False):
    """Synthetic align_turns.jsonl per gated run, shaped like endpoint.turn_provenance."""
    result = json.loads((run / 'r1_result.json').read_text())
    for phase in result['phases']:
        if phase['name'] not in exporter.GATED_D_RUN_NAMES:
            continue
        total, turns = phase['result']['decode_tokens'], phase['result']['admitted_turns']
        counts = rehearsal.R1Tests.even_split(total, turns, 4096)
        rows = []
        for i, n in enumerate(counts):
            reason = last_finish if i == turns-1 else finish
            rows.append({'turn': i, 'flags': [] if reason != 'length' else [f'turn_token_budget_reached:{i}'],
                         'generation': {'output_token_ids': list(range(n)), 'prompt_token_ids': [1, 2, 3],
                                        'finish_reason': reason, 'sampler': {'per_turn_seed': i}}})
        if mutate:
            mutate(phase['name'], rows)
        path = run / phase['name'] / phase['result']['bundle'] / exporter.TURNS_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        body = ''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows).encode()
        if compress:
            plain = path.with_name('plain.jsonl')
            plain.write_bytes(body)
            subprocess.run(['zstd', '-q', str(plain), '-o', str(path) + '.zst'], check=True)
            plain.unlink()
        else:
            path.write_bytes(body)
    return counts


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        # 28,000 decode tokens over 7 admitted turns, as a lane-shaped gated record.
        with patch.object(r1, '_run', rehearsal.FakeWorld(step_d_rate=40.0, gated_decode_tokens=28000,
                                                gated_admitted_turns=TURNS)):
            self.assertEqual(r1.run(rehearsal.R1Tests.args(None, str(self.tmp), synthetic=True)), 0)
        self.run_dir = self.tmp / 'run'

    def test_export_matches_the_driver_and_binds_every_input_file(self):
        counts = write_bundles(self.run_dir)
        data = exporter.export(self.run_dir)
        self.assertEqual(set(data), set(exporter.GATED_D_RUN_NAMES))
        result_sha = hashlib.sha256((self.run_dir / 'r1_result.json').read_bytes()).hexdigest()
        for name, entry in data.items():
            self.assertEqual(entry['turn_decode_counts'], counts)
            self.assertEqual(entry['turn_completed'], [True] * TURNS)
            source = entry['source']
            path = self.run_dir / source['align_turns_path']
            self.assertEqual(source['align_turns_stored_sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(source['r1_result_sha256'], result_sha)

    def test_export_feeds_backfill_and_the_kit_binds_the_record(self):
        write_bundles(self.run_dir)
        out = self.tmp / 'export.json'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(exporter.main(['--run-dir', str(self.run_dir), '--out', str(out)]), 0)
        raw = out.read_bytes()
        slots = json.loads((self.tmp / 'registration/r1_slots.json').read_text())
        for key in ('admitted_turns', 'x7', 'phases_s'):      # a lane record carries no X-G evidence
            slots['x_g'].pop(key, None)
        for row in slots['deadman_budget']:
            for key in ('turn_decode_counts', 'turn_completed', 'turn_counts_source_sha256'):
                row.pop(key, None)
        result_raw = (self.run_dir / 'r1_result.json').read_bytes()
        slots = procedure.backfill_x_g(slots, json.loads(result_raw), hashlib.sha256(result_raw).hexdigest())
        slots = procedure.backfill_turn_counts(slots, json.loads(raw), hashlib.sha256(raw).hexdigest())
        kit.require_ready(rehearsal.R1Tests.bind_inputs(slots), slots, synthetic=True)
        # The CLI path consumes exactly the same file.
        cli_slots = self.tmp / 'in.json'
        stripped = json.loads((self.tmp / 'registration/r1_slots.json').read_text())
        for row in stripped['deadman_budget']:
            for key in ('turn_decode_counts', 'turn_completed', 'turn_counts_source_sha256'):
                row.pop(key, None)
        cli_slots.write_text(json.dumps(stripped))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(procedure.main(['backfill-turn-counts', '--r1-slots', str(cli_slots),
                                             '--counts-export', str(out), '--out', str(self.tmp / 'out.json')]), 0)
        done = json.loads((self.tmp / 'out.json').read_text())
        self.assertEqual({r['turn_counts_source_sha256'] for r in done['deadman_budget']},
                         {hashlib.sha256(raw).hexdigest()})

    def test_derive_contrast_prints_the_kits_own_rederivation(self):
        slots = json.loads((self.tmp / 'registration/r1_slots.json').read_text())
        inputs = self.tmp / 'inputs.json'
        inputs.write_text(json.dumps({'WP18': {'X': {'max_turns': 12}}}))
        path = self.tmp / 'slots.json'
        path.write_text(json.dumps(slots))
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(procedure.main(['derive-contrast', '--r1-slots', str(path), '--inputs', str(inputs)]), 0)
        printed = json.loads(buffer.getvalue())
        expected = kit.w1_contrast_g0_cap(slots, 12)
        self.assertEqual(printed, {'contrast_g0_cap_s': expected['value_s'], 'contrast_fit': expected})

    def test_compressed_turn_files_are_read_and_hashed_as_stored(self):
        if shutil.which('zstd') is None:
            self.skipTest('zstd not installed')
        counts = write_bundles(self.run_dir, compress=True)
        data = exporter.export(self.run_dir)
        entry = data['D_bank_benign_s1_gated_held']
        self.assertEqual(entry['turn_decode_counts'], counts)
        stored = (self.run_dir / (entry['source']['align_turns_path'] + '.zst')).read_bytes()
        self.assertEqual(entry['source']['align_turns_stored_sha256'], hashlib.sha256(stored).hexdigest())
        self.assertNotEqual(entry['source']['align_turns_stored_sha256'], entry['source']['align_turns_logical_sha256'])

    def test_completion_flags_follow_finish_reason_and_budget_cuts(self):
        write_bundles(self.run_dir, last_finish='length')
        entry = exporter.export(self.run_dir)['D_spam_benign_s1_gated_held_a']
        self.assertEqual(entry['turn_completed'], [True] * (TURNS-1) + [False])
        write_bundles(self.run_dir, finish='', last_finish='stop')       # unknown reason: fail closed
        self.assertEqual(exporter.export(self.run_dir)['D_spam_benign_s1_gated_held_a']['turn_completed'], [False] * (TURNS-1) + [True])

    def test_refuses_a_disagreement_with_the_driver_or_a_malformed_record(self):
        def drop(name, rows):
            if name == 'D_bank_benign_s1_gated_held':
                rows.pop()
        write_bundles(self.run_dir, mutate=drop)
        with self.assertRaisesRegex(ValueError, 'disagree'):
            exporter.export(self.run_dir)
        write_bundles(self.run_dir, mutate=lambda name, rows: rows[0].update(turn=5))
        with self.assertRaisesRegex(ValueError, 'out of order'):
            exporter.export(self.run_dir)
        write_bundles(self.run_dir, mutate=lambda name, rows: rows[0]['generation'].pop('output_token_ids'))
        with self.assertRaises(ValueError):
            exporter.export(self.run_dir)

    def test_missing_bundle_unsafe_path_and_existing_output_refuse(self):
        with self.assertRaises(FileNotFoundError):
            exporter.export(self.run_dir)                      # no bundles written
        write_bundles(self.run_dir)
        result = json.loads((self.run_dir / 'r1_result.json').read_text())
        for phase in result['phases']:
            if phase['name'] == 'D_bank_benign_s1_gated_held':
                phase['result']['bundle'] = '../../escape'
        (self.run_dir / 'r1_result.json').write_text(json.dumps(result))
        with self.assertRaisesRegex(ValueError, 'relative path'):
            exporter.export(self.run_dir)
        out = self.tmp / 'exists.json'
        out.write_text('x')
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(exporter.main(['--run-dir', str(self.run_dir), '--out', str(out)]), 1)
        self.assertEqual(out.read_text(), 'x')

    def test_only_the_turn_record_file_is_read(self):
        write_bundles(self.run_dir)
        opened = []
        real = Path.read_bytes
        def spy(path):
            opened.append(path.name)
            return real(path)
        with patch.object(Path, 'read_bytes', spy):
            exporter.export(self.run_dir)
        self.assertEqual(set(opened), {'r1_result.json', 'align_turns.jsonl'})


if __name__ == '__main__':
    unittest.main()
