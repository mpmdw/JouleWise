"""Plain/.zst parity through actual compression, parsing and harvest joins.

All inputs are synthetic or committed fixtures. Comparisons are exact because
the same code consumes identical decompressed bytes; no numeric slack applies.
"""
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest

from joulewise import desk_compress as desk
from joulewise import authentication_io as auth, campaign_provenance as provenance
from joulewise import whole_window
from joulewise.b6 import survivor_screen
from joulewise.b5 import harvest as h
from joulewise.bundle_read import BundleReader
from joulewise.cli import validate_bundle
from joulewise.external import km003c_parse as kp
from joulewise.hazards import monitor
from joulewise.reduce import reduce_bundle
from tests.external.test_km003c_parse import Synthetic, NS

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/b5_harvest/l1_monitor"


@unittest.skipUnless(Path(desk.zstd_path()).is_file(), "zstd CLI required")
class CompressedReaderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.archive, self.custody = self.root / "archive", self.root / "custody"
        (self.archive / "sources").mkdir(parents=True)
        (self.custody / "night").mkdir(parents=True)
        (self.archive / "harvest.json").write_text('{"verdict":"COLLECTED"}\n')
        (self.custody / "night/chain.exited").write_text('{}\n')
        self.hazards = self.custody / "hazards"

    def compress_historical_hazards(self):
        # New compression protects hazards/. Simulate an older archive by
        # compressing these bytes at an eligible path using the real code,
        # then putting the .zst siblings back at the original logical paths.
        staging = self.custody / "legacy-inputs"
        self.hazards.rename(staging)
        rc, summary = desk.compress(archive=self.archive, custody=self.custody, min_bytes=0)
        staging.rename(self.hazards)
        self.assertEqual(rc, 0)
        self.assertGreater(summary["files"], 0)
        self.assertFalse(list(self.hazards.rglob("*.jsonl")))

    def harvest(self, name):
        output = self.root / name
        (output / "withheld").mkdir(parents=True)
        thresholds = h.parse_registration_thresholds(
            (ROOT / "configs/campaigns/v5_claim_25g83/registration_block5.md").read_bytes())
        inputs = SimpleNamespace(custody_root=self.custody, monitor_dir=self.hazards / "monitor",
                                 thresholds=thresholds, plan_id="synthetic", attempt=1, h_claim="a" * 40,
                                 catalog_path=ROOT / "tests/fixtures/b5_harvest/flag_catalog.json")
        # Fixed clock seams stabilize flag timestamps; parsing and joins are real.
        return h._Harvest(inputs, output, h.Seams(now=lambda: 0, monotonic_ns=lambda: 0,
                          boot_session_uuid=lambda: "synthetic"), prepare_desk=False, run_g3=False)

    def compress_archive(self):
        rc, summary = desk.compress(archive=self.archive, custody=self.custody, min_bytes=0)
        self.assertEqual(rc, 0)
        self.assertGreater(summary["files"], 0)

    def test_campaign_manifest_catalog_and_log_authentication_are_identical(self):
        runs = self.archive / "sources/claim-runs"
        path = runs / "campaign_manifests/fixture.json"
        path.parent.mkdir(parents=True)
        manifest = {"schema_version": provenance.CAMPAIGN_PROVENANCE_SCHEMA_V2,
                    "session_id": "synthetic-session", "members": [
                        {"run_id": "fixture", "execution": "invoked", "bundle_ids": ["fixture"]}]}
        raw = (json.dumps(manifest, sort_keys=True) + "\n").encode()
        path.write_bytes(raw)
        row = provenance.campaign_provenance_attestation(
            manifest_path=path, raw_manifest_bytes=raw, manifest=manifest, timestamp="synthetic")
        log = runs / "campaign_log.jsonl"
        log.write_text(json.dumps(row, sort_keys=True) + "\n")

        def read():
            with auth.V2AuthenticationReadSession() as session:
                single = provenance.load_authenticated_campaign_manifest(runs, path)
                catalog = provenance.load_authenticated_campaign_catalog(runs)
                self.assertIsNotNone(single)
                self.assertEqual(catalog, [single])
                return single, catalog, dict(session.records)

        plain = read()
        # The real compressor now exempts campaign_log.jsonl. Compress the
        # historical log at an eligible name, then restore its logical name.
        staging = log.with_name("legacy-log.jsonl")
        log.rename(staging)
        self.compress_archive()
        Path(str(staging) + ".zst").rename(Path(str(log) + ".zst"))
        self.assertEqual(read(), plain)
        self.assertFalse(path.exists())
        self.assertFalse(log.exists())
        # Stale compressed siblings must not override an existing plain file.
        path.write_bytes(raw)
        Path(str(path) + ".zst").write_bytes(b"invalid stale sibling")
        self.assertEqual(read(), plain)

    def test_authentication_io_streams_hashes_and_logical_registry_paths_match(self):
        root = self.archive / "sources/authentication"
        root.mkdir()
        path = root / "input.json"
        raw_path = root / "input.csv"
        path.write_bytes(b'{"fixture":true}\r\n')
        raw_path.write_bytes(b'column,value\r\nfixture,1\r\n')

        def read():
            outside = [auth.read_authentication_input(path, grammar="json", label="fixture"),
                       auth.read_authentication_text(path, grammar="json", label="fixture"),
                       auth.sha256_authentication_input(raw_path, label="fixture raw")]
            with auth.open_authentication_input(raw_path, grammar="raw", label="fixture raw",
                                                newline="") as stream:
                outside.append(stream.read())
            with auth.V2AuthenticationReadSession() as session:
                capability = auth.v2_authentication_path(path)
                inside = [capability.read_bytes(), capability.read_text(),
                          auth.sha256_authentication_input(path, label="fixture JSON"),
                          auth.sha256_authentication_input(raw_path, label="fixture raw")]
                with capability.open("rb") as stream:
                    inside.append(stream.read())
                self.assertEqual(set(session.records), {str(path.resolve()), str(raw_path.resolve())})
                self.assertTrue(session.records[str(path.resolve())].strict_parse_succeeded)
                return outside, inside, dict(session.records)

        plain = read()
        self.compress_archive()
        self.assertEqual(read(), plain)
        # The same session sees decompressed bytes under the original identity.
        with auth.V2AuthenticationReadSession() as session:
            auth.read_authentication_input(path, grammar="raw", label="fixture")
            path.write_bytes(b'{"fixture":false}\n')
            with self.assertRaisesRegex(auth.V2AuthenticationInputError, "input_changed"):
                auth.read_authentication_input(path, grammar="json", label="fixture")
            self.assertEqual(set(session.records), {str(path.resolve())})

    def test_compressed_authentication_preserves_strict_parsing_before_registration(self):
        root = self.archive / "sources/authentication"
        root.mkdir()
        invalid = {"duplicate.json": (b'{"a":1,"a":2}', "duplicate_json_key"),
                   "nonfinite.json": (b'{"a":NaN}', "nonfinite_json_number"),
                   "malformed.json": (b'{"a":', "invalid_json")}
        for name, (raw, _reason) in invalid.items():
            (root / name).write_bytes(raw)
        self.compress_archive()
        for name, (_raw, reason) in invalid.items():
            with self.subTest(name=name), auth.V2AuthenticationReadSession() as session:
                with self.assertRaisesRegex(auth.V2AuthenticationInputError, reason):
                    # A logical .json suffix still forces JSON even when the
                    # caller requests raw; storage compression cannot downgrade it.
                    auth.read_authentication_input(root / name, grammar="raw", label="fixture")
                self.assertEqual(dict(session.records), {})

    def test_bundle_read_reduce_strict_validation_and_survivor_screen_are_identical(self):
        from tests.test_p2038_production_path import P2038ProductionPathTests

        # The production controller/reducer writes synthetic raw, calibration
        # custody, events, metadata and summaries. Only its runtime and telemetry
        # source are fixtures; no reader or reduction function is mocked.
        source, _summary = P2038ProductionPathTests().run_mode(self.root / "primary", "normal")
        members = [{"run_id": f"corpus{i}", "stage_id": "neg8_bound", "status": "succeeded"}
                   for i in range(6)]
        members += [{"run_id": f"{slot}{i}", "stage_id": f"{slot}_reference", "status": "succeeded"}
                    for slot in ("start", "end") for i in range(2)]
        # Six corpus members and two per endpoint are the screen's registered
        # minimums; identical primary-byte copies make the expected drift zero.
        runs = self.archive / "sources/bound-runs"
        for member in members:
            shutil.copytree(source, runs / member["run_id"])
        bundle = runs / members[0]["run_id"]

        def read():
            reader = BundleReader(bundle)
            reduced = reduce_bundle(bundle, reducer_version="0.5.2").to_dict()
            problems = validate_bundle(bundle, strict=True)
            self.assertEqual(problems, [])
            self.assertTrue(reduced["window_evidence_precheck"]["gross_request"]["eligible"])
            self.assertTrue(reduced["window_evidence_precheck"]["idle_subtracted_request"]["eligible"])
            self.assertTrue(whole_window._current_strict_summary(reduced, bundle))
            energy = whole_window._reference_energy_evidence_detail(bundle)
            self.assertEqual(energy[2:], (None, None))
            result = survivor_screen.screen({"members": members}, {},
                survivor_screen.archive_energy_of(self.archive),
                {"neg8": {"corpus_minimum": 6, "corpus_cap": 6}})
            self.assertEqual(result.verdict, "passed")
            return {"config": reader.config().to_dict(), "metadata": reader.metadata(),
                    "events": reader.events(), "trace": reader.trace_rows(),
                    "raw": reader.raw_artifact_bytes("powermetrics.plist"),
                    "validation": reader.problems(), "strict": problems,
                    "reduced": reduced, "energy": energy, "screen": result}

        plain = read()
        self.assertTrue((bundle / "instrument_calibration/manifest.json").is_file())
        self.compress_archive()
        self.assertFalse((bundle / "raw/powermetrics.plist").exists())
        self.assertFalse((bundle / "instrument_calibration/manifest.json").exists())
        self.assertTrue((bundle / "instrument_calibration/manifest.json.zst").is_file())
        self.assertEqual(read(), plain)

    def test_plain_path_has_precedence_over_compressed_sibling_in_presence_checks(self):
        path = self.archive / "sources/fixture"
        path.write_bytes(b"plain")
        Path(str(path) + ".zst").write_bytes(b"invalid stale sibling")
        self.assertTrue(desk.is_file(path))
        self.assertEqual(desk.read_bytes(path), b"plain")
        path.unlink()
        path.mkdir()
        self.assertTrue(desk.exists(path))
        self.assertFalse(desk.is_file(path))
        with self.assertRaises(IsADirectoryError):
            desk.read_bytes(path)

    def test_harvest_all_hazard_journals_and_findings_are_identical(self):
        directory = self.hazards / "monitor"
        directory.mkdir(parents=True)
        for module in h.MONITOR_MODULES:
            shutil.copyfile(FIXTURES / f"{module}.jsonl", directory / f"{module}.jsonl")
        cases = json.loads((FIXTURES / "expected.json").read_bytes())["cases"]

        def joined(name):
            run = self.harvest(name)
            run.roster = {"members": [{"run_id": key} for key in cases]}
            run.spans = {key: {"member": case["span"]["monotonic_ns"],
                               "request": (case["request"] or case["span"])["monotonic_ns"]}
                         for key, case in cases.items()}
            run.monitor_joins()
            self.assertEqual(run.faults, [])
            codes = {flag["code"] for flag in run.flags.records}
            self.assertFalse(codes & {"battery.unmeasured", "contention.unmeasured",
                                      "records.monitor_journal_absent"})
            raw = monitor.load_journals(self.custody)
            findings = {key: monitor.member_findings(raw, span=case["span"], request=case["request"])
                        for key, case in cases.items()}
            return {"flags": run.flags.records, "hazards": run.hazards, "journals": run._journals,
                    "raw": raw, "findings": findings, "assist": run.battery_assist}

        plain = joined("plain")
        self.compress_historical_hazards()
        self.assertEqual(joined("compressed"), plain)

    def test_meter_entry_point_and_harvest_stream_lookup_are_identical(self):
        directory = self.hazards / "meter"
        directory.mkdir(parents=True)
        synthetic = Synthetic()
        synthetic.lines[0].update(start_raw_ns=synthetic.start_ns, start_mono_ns=synthetic.start_ns)
        # 20 fit points in separate 10 s bins are required by the parser;
        # 240 s of 50 SPS data spans 24 bins, including complete fit endpoints.
        for _ in range(1200):
            synthetic.poll(10)
        end = synthetic.host(synthetic.dev_ms)
        synthetic.raw_line({"k": "t", "end_raw_ns": end, "end_mono_ns": end})
        path = synthetic.write(directory, "stream-001.jsonl")

        def joined(name):
            run = self.harvest(name)
            start = synthetic.start_ns
            run.roster = {"members": [{"run_id": "fixture"}]}
            run.spans = {"fixture": {"request": [start + 5 * NS, start + 7 * NS]}}
            run.members = {"fixture": {"idle_baseline_span": [start + NS, start + 3 * NS]}}
            run.meter_joins()
            self.assertNotIn("meter.absent", {flag["code"] for flag in run.flags.records})
            output = json.loads((run.withheld / h.METER_RECORD_NAME).read_bytes())
            self.assertEqual(output["members"]["fixture"]["stream"], path.name)
            self.assertIsNotNone(output["members"]["fixture"]["machine"])
            return kp.parse(path), run.flags.records, output

        plain = joined("plain")
        self.compress_historical_hazards()
        self.assertEqual(joined("compressed"), plain)
        # Prefer the plain sibling and enumerate the logical stream only once.
        path.write_bytes(desk.read_bytes(path))
        self.assertEqual(joined("both"), plain)

    def test_monitor_truncated_tail_and_missing_journal_keep_their_semantics(self):
        directory = self.hazards / "monitor"
        directory.mkdir(parents=True)
        path = directory / "battery.jsonl"
        path.write_bytes(b'{"kind":"fixture"}\n{"truncated"')
        plain = monitor.read_journal(path)
        self.compress_historical_hazards()
        self.assertEqual(monitor.read_journal(path), plain)
        self.assertEqual(monitor.read_journal(directory / "missing.jsonl"), ([], None))


if __name__ == "__main__":
    unittest.main()
