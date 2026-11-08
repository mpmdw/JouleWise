"""RUN_STATE 226 R15 bug fix: the shared measurement view must project ALIGN D
configs under their own model identity (``qwen3.8-27b-<run>``), not as
``neg8_reference-<run>``. The older BYTES roster has no D model, so the view
used to fall back to ``neg8_reference`` on the W1 path and every series window.

Repository files only: the W1 kit and one series window kit; no model opened.
"""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import align_v4_kit as w1, align_v4_series as series, bytes_h_session as h

ROOT = Path(__file__).resolve().parents[2]


def projected_units(kit, pack_id, *, root=ROOT):
    with tempfile.TemporaryDirectory() as tmp:
        session = Path(tmp) / 'session'
        session.mkdir()
        view, pack = h.measurement_view(Path(root), session, kit=kit, pack_id=pack_id)
        tree = json.loads((pack / 'plan_tree.json').read_bytes())
    return {u['identity_unit_id']: u for u in tree['arm_attachments']['identity_pin_projection']['identity_units']}


class MeasurementViewIdentityTests(unittest.TestCase):
    def test_w1_d_members_are_projected_as_d_not_neg8_reference(self):
        plan = json.loads((ROOT / w1.KIT / 'collection_plan.json').read_bytes())
        units = projected_units(w1.KIT, w1.PACK_ID)
        d_runs = [m['run_id'] for m in plan['members'] if m['model_id'] == w1.D_TAG]
        self.assertEqual(len(d_runs), 6)
        for run_id in d_runs:
            self.assertIn(h.align_unit_id(w1.D_TAG, run_id), units)
            self.assertNotIn(h.align_unit_id('neg8_reference', run_id), units)
            unit = units[h.align_unit_id(w1.D_TAG, run_id)]
            self.assertEqual(unit['declared_identity']['model_name'], 'Qwen3.8-27B-8bit')
        self.assertFalse([u for u in units if u.startswith('neg8_reference-')])
        # The projection names exactly the kit's own identity-pin units.
        pins = json.loads((ROOT / w1.KIT / 'registration/identity_pins.json').read_bytes())
        align_pins = {k for k in pins['units'] if k != 'neg8_reference'}
        self.assertTrue({h.align_unit_id(w1.D_TAG, r) for r in d_runs} <= align_pins)

    def test_series_window_d_members_are_projected_as_d(self):
        manifest = series.load(ROOT)
        files = series.build_files(ROOT, manifest, 'C1')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'm'
            root.mkdir()
            for p in ROOT.iterdir():
                if p.name != 'configs':
                    (root / p.name).symlink_to(p, target_is_directory=p.is_dir())
            for relative, omitted in (('configs', {'campaigns'}), ('configs/campaigns', set())):
                (root / relative).mkdir()
                for p in (ROOT / relative).iterdir():
                    if p.name not in omitted:
                        (root / relative / p.name).symlink_to(p, target_is_directory=p.is_dir())
            for path, raw in files.items():
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_bytes(raw)
            units = projected_units(series.kit_path('C1'), series.pack_id('C1'), root=root)
        d = [u for u in units if u.startswith(w1.D_TAG + '-')]
        self.assertEqual(len(d), 18)
        self.assertFalse([u for u in units if u.startswith('neg8_reference-')])

    def test_an_align_config_without_one_model_tag_is_refused(self):
        source = json.loads((ROOT / w1.KIT / 'collection_plan.json').read_bytes())['members'][4]['config_path']
        config = json.loads((ROOT / source).read_bytes())
        config['run_metadata']['tags'] = [t for t in config['run_metadata']['tags'] if not t.startswith('align-model=')]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'm'
            root.mkdir()
            for p in ROOT.iterdir():
                if p.name != 'configs':
                    (root / p.name).symlink_to(p, target_is_directory=p.is_dir())
            for relative, omitted in (('configs', {'campaigns'}), ('configs/campaigns', {'align_v4'})):
                (root / relative).mkdir()
                for p in (ROOT / relative).iterdir():
                    if p.name not in omitted:
                        (root / relative / p.name).symlink_to(p, target_is_directory=p.is_dir())
            kit = root / w1.KIT
            for p in (ROOT / w1.KIT).rglob('*'):
                if p.is_file():
                    (kit / p.relative_to(ROOT / w1.KIT)).parent.mkdir(parents=True, exist_ok=True)
                    (kit / p.relative_to(ROOT / w1.KIT)).write_bytes(p.read_bytes())
            (root / source).write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, 'one model identity tag'):
                projected_units(w1.KIT, w1.PACK_ID, root=root)


if __name__ == '__main__':
    unittest.main()
