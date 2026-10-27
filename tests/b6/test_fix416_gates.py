"""FIX-416 desk regressions: counting, blinding custody and sizing provenance."""
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from joulewise.b5 import harvest
from joulewise.b6 import acceptance, blinding, export_runs
from joulewise.b6.acceptance_interface import MemberEvidence, StageEvidence
from tests.b6.support import ROOT, prepared, session, IDENTITY, write_json
from tests.b6.test_export_runs import archive_fixture
from tests import test_harvest_b5_window as windows


class Fix416Tests(unittest.TestCase):
    def test_preparation_reads_the_bytes_pack_effect_and_catalog_pin(self):
        digest = hashlib.sha256((ROOT / 'configs/b6/flag_catalog_b6.json').read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            for path in sorted((ROOT / 'configs/b6/packs').glob('bytes-s*-p*/registration.json')):
                reg = json.loads(path.read_bytes())
                if 'bytes_extension' in reg:
                    continue  # extension packs get their tree at the desk (test_bytes_extension)
                tree = json.loads((ROOT / reg['plan_tree_ref']).read_bytes())
                prep = prepared(Path(tmp), tree=tree)
                self.assertEqual(prep.registration['pack_registration'], reg)
                self.assertEqual(reg['flag_effects']['cell.below_minimum'], 'DISCLOSE')
                self.assertEqual(reg['flag_effects']['clock.step_unmeasured'], 'DISCLOSE')
                self.assertEqual(reg['flag_catalog_sha256'], digest)

    def test_below_minimum_is_disclosed_only_for_registered_bytes_packs(self):
        with tempfile.TemporaryDirectory() as tmp:
            prep = prepared(Path(tmp))
            base = session()
            for pack_path in sorted((ROOT / 'configs/b6/packs').glob('bytes-s*-p*/registration.json')):
                reg = json.loads(pack_path.read_bytes())
                members = []
                for model in ('A', 'B'):
                    for stratum, positions in (('repeat', 1), ('quad', 4)):
                        for unit in range(10):
                            for pos in range(positions):
                                flags = ('thermal.os_level_nonzero',) if model == 'A' and stratum == 'repeat' and unit < 6 else ()
                                members.append(MemberEvidence('science', f'{model}-{stratum}-{unit}-{pos}',
                                    'succeeded', flags, ((model, stratum, str(unit)),), runtime=IDENTITY))
                evidence = dataclasses.replace(base, pack_id=reg['pack_id'], stages=(
                    StageEvidence('science', 'campaign_collection', 100, tuple(members)), base.stages[1]))
                scoped = dataclasses.replace(prep, registration={**prep.registration, 'pack_registration': reg})
                result = acceptance.ACCEPTANCE.evaluate(scoped, evidence)
                self.assertTrue(result.counting, result.reasons)
                self.assertIn('cell.below_minimum', result.flags)
                self.assertEqual(result.record['cells'], {'A': {'repeat': 4, 'quad': 10}, 'B': {'repeat': 10, 'quad': 10}})
                legacy = acceptance.ACCEPTANCE.evaluate(prep, evidence)
                self.assertFalse(legacy.counting)
                self.assertIn('cell.below_minimum', legacy.reasons)
                self.assertEqual(result.record['cells'], legacy.record['cells'])
                print(reg['pack_id'], 'BYTES counting=True; legacy counting=False; A=4/10 B=10/10')

    def test_catalog_digest_mismatch_discloses_registered_and_running_digests(self):
        with tempfile.TemporaryDirectory() as tmp:
            prep = prepared(Path(tmp))
            reg = {'flag_catalog_sha256': '0' * 64}
            scoped = dataclasses.replace(prep, registration={**prep.registration, 'pack_registration': reg})
            result = acceptance.ACCEPTANCE.evaluate(scoped, session())
            flag = next(f for f in result.record['emitted_flags'] if f['code'] == 'catalog.digest_mismatch')
            self.assertEqual(flag['observed'], {'registered': '0' * 64, 'running': prep.catalog.sha256})
            self.assertTrue(result.counting)

    def test_export_missing_registration_stops_before_publishing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive, reg, plan, record = archive_fixture(root)
            (archive / 'sources/pack/registration.json').unlink()
            with self.assertRaisesRegex(ValueError, 'pack registration unresolved for desk-pack'):
                export_runs.export(archive, plan, reg, root / 'packs', root / 'out', non_claim=True)
            self.assertFalse((root / 'out').exists())
            write_json(archive / 'sources/pack/registration.json', {'pack_id': 'another-pack'})
            with self.assertRaisesRegex(ValueError, 'pack registration unresolved for desk-pack'):
                export_runs.export(archive, plan, reg, root / 'packs', root / 'out', non_claim=True)
            with self.assertRaisesRegex(ValueError, 'explicit pack registration empty or malformed'):
                export_runs.export(archive, plan, reg, root / 'packs', root / 'out', pack_registration={})

    def test_export_resolves_closed_replication_campaign_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive, reg, plan, record = archive_fixture(root)
            record['pack_id'] = 'd117_floor_qwen3-1p7b_v5'
            result = export_runs.export(archive, plan, reg, root / 'packs', root / 'out',
                                        acceptance_record=record)
            sidecar = json.loads(result.sidecar_path.read_bytes())
            self.assertNotIn('group', sidecar['blinding'])
            self.assertEqual(sidecar['pack_id'], record['pack_id'])

    def test_export_binds_key_bytes_and_lost_or_changed_group_key_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive, reg, plan, record = archive_fixture(root)
            write_json(archive / 'sources/pack/registration.json', {'pack_id': 'desk-pack', 'blinding_group': 'bytes', 'bytes_pass': 1})
            result = export_runs.export(archive, plan, reg, root / 'packs', root / 'out')
            sidecar = json.loads(result.sidecar_path.read_bytes())
            directory = root / 'packs/bytes/blinding'
            for name, digest in sidecar['blinding']['key_sha256'].items():
                self.assertEqual(digest, hashlib.sha256((directory / name).read_bytes()).hexdigest())
            key = directory / 'pack.json'
            original = key.read_bytes()
            key.unlink()
            with patch.object(blinding, '_draw', side_effect=AssertionError('redrawn')):
                with self.assertRaisesRegex(ValueError, 'key missing after session export'):
                    blinding.pack_factor(directory, session_id='next')
            self.assertFalse(key.exists())
            key.write_bytes(original + b' ')
            with self.assertRaisesRegex(ValueError, 'key differs from session binding'):
                blinding.pack_factor(directory, session_id='next')

    def test_key_creation_is_exclusive_private_and_watts_are_offset(self):
        self.assertEqual(blinding.PACK_RANGE, (0.8, 1.25))
        self.assertEqual(blinding.CONFIG_RANGE, (0.97, 1.03))
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(blinding.os, 'link', wraps=os.link) as linked:
                blinding.factor(tmp, 'science')
            self.assertEqual(linked.call_count, 2)
            for call in linked.call_args_list:
                self.assertTrue(Path(call.args[0]).name.startswith('.' + Path(call.args[1]).name + '.'))
                self.assertEqual(stat.S_IMODE(Path(call.args[1]).stat().st_mode), 0o600)
                self.assertFalse(Path(call.args[0]).exists())
            self.assertEqual(blinding.apply({'idle_power_w': 3, 'idle_variance_w2': 4}, 2),
                             {'idle_power_w': 6, 'idle_variance_w2': 16})

    def test_harvest_source_mutation_reaches_acceptance_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'summary_metrics.json'
            source.write_text('{"phase_energy_j":{"decode":1}}')
            emit = Mock()
            stub = SimpleNamespace(sources={'run': source}, original={'run': harvest.tree_inventory(source)}, emit=emit)
            harvest._Harvest.sources_unchanged(stub)
            emit.assert_not_called()
            source.write_text('{"phase_energy_j":{"decode":2}}')
            harvest._Harvest.sources_unchanged(stub)
            emit.assert_called_once()
            self.assertEqual(emit.call_args.args, ('records.source_changed_during_harvest',))
            result = acceptance.ACCEPTANCE.evaluate(prepared(root), dataclasses.replace(session(),
                window_flags=('records.source_changed_during_harvest',)))
            self.assertEqual(result.verdict, 'HARVEST_RERUN')
            self.assertFalse(result.counting)

    def test_sizing_rows_match_their_own_derivation(self):
        sizing = json.loads((ROOT / 'configs/b6/registration/sizing_b5.json').read_bytes())['packs']
        rows = json.loads((ROOT / 'docs/process_traces/2026-10-23-magistrate-786c0858/derivation.json').read_bytes())['table']
        self.assertEqual({r['pack_id'] for r in rows}, {f'bytes-s{n}-p1' for n in range(1, 7)})
        for row in rows:
            actual = sizing[row['pack_id']]
            self.assertEqual(actual['T_stream_max_s'], row['T_stream_max_s'], row['pack_id'])
            self.assertEqual(actual['programmed_span_s'], row['S'], row['pack_id'])
            terms = actual['disk_derivation']
            for key, source in (('B_bytes', 'B'), ('required_free_bytes', 'P'),
                                ('extra_wait_raw_bytes', 'WAIT'), ('fixed_retained_bytes', 'fixed')):
                self.assertEqual(terms[key], row[source], row['pack_id'])


class SourceChangedPipelineTests(windows.WindowTestCase):
    def test_late_source_change_is_seen_by_the_harvest_pipeline(self):
        window = self.window()

        def change_after_assessment(run):
            # The reductions have finished. A changed raw source still demands
            # a fresh harvest, even if the cached member assessments agree.
            (window.claim / 'b5t-abs-r01' / 'summary_metrics.json').write_text('{}\n')

        with patch.object(harvest._Harvest, 'diagnostics', change_after_assessment):
            window.harvest(run_g3=False)
        self.assertIn('records.source_changed_during_harvest', window.codes())
