"""D-176 census-loader regressions. Synthetic custody is never live evidence."""
import dataclasses
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import arm_readiness as readiness, t0_rehearsal as rehearsal
from scripts import rehearse_t0_unattended as cli
from tests.test_t0_rehearsal import FixtureBuilder, fixture_bundle, fixture_inventory, _write_json


class ProductionCensusLoaderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = FixtureBuilder(Path(temporary.name)).build()

    def test_stale_census_cannot_false_pass_g6(self):
        self.assertEqual(rehearsal.GateStatus.PASS, rehearsal.evaluate_g6(fixture_bundle(self.root)).status)
        path = self.root / cli.MANIFEST_NAME
        original = readiness.parse_json_bytes(path.read_bytes())
        for record in (original["production_roots"][:-1], [], original["production_roots"] + [original["production_roots"][0]]):
            with self.subTest(record=record):
                _write_json(path, {**original, "production_roots": record})
                with self.assertRaisesRegex(cli.BundleLoadError, "production-root census incomplete"):
                    fixture_bundle(self.root)
        changed = [dict(item) for item in original["production_roots"]]
        changed[0]["path"] += "-substituted"
        _write_json(path, {**original, "production_roots": changed})
        with self.assertRaisesRegex(cli.BundleLoadError, "production-root census incomplete"):
            fixture_bundle(self.root)

    def test_inventory_must_equal_head_bytes(self):
        raw = readiness.render_json(fixture_inventory(self.root))
        with mock.patch.object(cli, "_regular_bytes", return_value=raw), mock.patch.object(readiness, "_git_blob_at_head", return_value=raw):
            self.assertEqual(fixture_inventory(self.root), cli._production_inventory())
        for pinned in (None, raw + b" "):
            with mock.patch.object(cli, "_regular_bytes", return_value=raw), mock.patch.object(readiness, "_git_blob_at_head", return_value=pinned):
                with self.assertRaisesRegex(cli.BundleLoadError, "production-root census incomplete"):
                    cli._production_inventory()

    def test_symlinked_rehearsal_root_refuses_before_resolution_hides_it(self):
        link = self.root.with_name("alias")
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(cli.BundleLoadError, "non-symlink"):
            cli.load_evidence_bundle(link)
        bundle = dataclasses.replace(fixture_bundle(self.root), custody_root=link)
        self.assertEqual(rehearsal.GateStatus.FAIL, rehearsal.evaluate_g6(bundle).status)

    def test_sibling_child_rejects_parent_nested_and_wrong_basename(self):
        bundle = fixture_bundle(self.root)
        parent = self.root.parent
        for path in (parent, self.root / self.root.name, parent / "other-rehearsal"):
            path.mkdir(parents=True, exist_ok=True)
            value = dict(bundle.record("rehearsal_receipt").value)
            value["custody_root"] = str(path)
            artifact = dataclasses.replace(bundle.record("rehearsal_receipt"), value=value)
            changed = dataclasses.replace(bundle, custody_root=path,
                artifacts=tuple(artifact if item.relative_path == artifact.relative_path else item for item in bundle.artifacts))
            with self.subTest(path=path):
                result = rehearsal.evaluate_g6(changed)
                self.assertEqual(rehearsal.GateStatus.FAIL, result.status)

    def test_missing_production_root_counts_and_resolution_error_fails(self):
        bundle = fixture_bundle(self.root)
        candidate = self.root / "missing-production"
        changed = dataclasses.replace(bundle, production_roots=bundle.production_roots + (rehearsal.ProductionRoot("deployment_measurement_root:future", candidate),))
        self.assertEqual(rehearsal.GateStatus.FAIL, rehearsal.evaluate_g6(changed).status)
        changed = dataclasses.replace(bundle, production_roots=bundle.production_roots + (rehearsal.ProductionRoot("broken", candidate, "resolution_error"),))
        self.assertEqual(rehearsal.GateStatus.FAIL, rehearsal.evaluate_g6(changed).status)
