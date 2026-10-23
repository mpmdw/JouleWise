"""Executable comparison with both pinned programs, on synthetic bytes only."""
import hashlib
import json
import os
import selectors
import subprocess
import sys
import tarfile
import tempfile
from decimal import Decimal
from pathlib import Path
import unittest
from unittest import mock

from joulewise import whole_window
from joulewise.b5_analysis.archive import open_archive, open_attempt_record
from joulewise.b5_analysis.windows import SealPins
from tests.b5_analysis import fixtures as fx


def read(root, relative):
    return json.loads((root / relative).read_bytes())


class FixtureShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins = SealPins.load()
        cls.gamma = fx.build_window("gamma")
        try:
            cls.beta = fx.build_window("beta")
        except BaseException:
            cls.gamma.close()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.beta.close()
        cls.gamma.close()

    def pin2(self, name="STD"):
        entry = fx.archived_entry("pin2", name)
        return entry.archive_root, entry

    def test_d1_d2_d3_d8_top_level_outputs_program_files(self):
        aroot, aentry = self.pin2()
        alpha, beta = read(aroot, "harvest.json"), read(self.beta.archive, "harvest.json")
        self.assertNotIn("calibration_bracket", alpha)  # D1
        self.assertIn("calibration_bracket", beta)
        path = "withheld/bracket-evaluation.json"
        self.assertTrue((aroot / path).is_file())  # D2: file exists even without an output digest
        self.assertNotIn(path, alpha["outputs"])
        self.assertEqual(beta["outputs"][path], fx.sha(self.beta.archive / path))
        self.assertEqual(len(alpha["harvest_checkout"]["files"]), 3)  # D3
        self.assertEqual(len(beta["harvest_checkout"]["files"]), 4)
        self.assertNotIn("joulewise/calibration_bracketing.py", alpha["harvest_checkout"]["files"])
        for record, shape in ((alpha, "pin2"), (beta, "pin4")):  # D8
            self.assertEqual(record["harvest_checkout"]["files"]["joulewise/whole_window.py"],
                             self.pins.pins[shape]["files"]["joulewise/whole_window.py"])
        self.assertNotEqual(alpha["harvest_checkout"]["files"]["joulewise/whole_window.py"],
                            beta["harvest_checkout"]["files"]["joulewise/whole_window.py"])
        for entry in (aentry, self.beta.entry):
            record = open_attempt_record(entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)
            handle = open_archive(fx.selected_window(record, seal_pins=self.pins),
                                  seal_pins=self.pins, pack_table=fx.PACK_TABLE)
            handle.withheld_bytes(path)
            check = next(row.check for row in handle.census() if row.path == path)
            self.assertEqual(check, "input_census" if entry == aentry else "harvest_outputs")

    def test_d4_bracket_projection_and_gamma_other_session(self):
        aroot, _ = self.pin2()
        new = {"trigger_scope", "recorded_only_triggers", "corpus_doubling", "other_session_systematic_sequences"}
        key = "withheld/bracket-evaluation.json"
        alpha = read(aroot, key)["assessment"]["acceptance"]["prospective_rederivation"]
        gamma = read(self.gamma.archive, key)["assessment"]["acceptance"]["prospective_rederivation"]
        self.assertFalse(new & alpha.keys())
        self.assertTrue(new <= gamma.keys())
        self.assertEqual(gamma["trigger_scope"], "window_evidence")
        self.assertTrue(gamma["other_session_systematic_sequences"])
        self.assertIn("new_systematic_failure_challenges_preflight_screen", gamma["recorded_only_triggers"])
        ledger = self.gamma.archive / "sources/ledger/calibration_observation_ledger.jsonl"
        rows = [json.loads(line) for line in ledger.read_bytes().splitlines()]
        self.assertTrue(any(row.get("attempt_id") == "s0-other-systematic" and
                            row.get("disposition") == "systematic-invalid" and row.get("session_id") == "s0-other-session" for row in rows))

    def test_m1_m2_m3_m4_m5_and_unhashed_inputs(self):
        aroot, _ = self.pin2()
        for root in (aroot, self.beta.archive):
            record = read(root, "harvest.json")
            exclusions = read(root, "derived/exclusions.json")
            self.assertEqual(record["harvest_checkout"], exclusions["harvest_checkout"])  # M1
            physics = read(root, "derived/neg8-corpus-physics.json")
            self.assertIn("members_collected", physics)  # M2
            self.assertIn("beyond_cap", physics)
            self.assertEqual(physics["members_kept"], 12)
            self.assertEqual(len(physics["beyond_cap"]), 5)
            screen = read(root, "derived/neg8-screen.json")  # M3
            self.assertEqual((screen["bound_used"], screen["rescreen"]["decision"]), ("corpus_physics_clean", "passed"))
            allowance = read(root, "derived/neg8-allowance.json")
            self.assertEqual(allowance["source"], "survivor_rescreen")
            self.assertNotIn("derived/neg8-clean-corpus.json", record["outputs"])
            self.assertEqual(allowance["clean_bound"]["corpus_manifest"]["sha256"], fx.sha(root / "derived/neg8-clean-corpus.json"))
            self.assertFalse(any(path.startswith("sources/") for path in record["outputs"]))
            self.assertEqual({path for path in record["outputs"] if path.startswith("withheld/")},
                             {"withheld/bracket-evaluation.json"} if "calibration_bracket" in record else set())
            identity = read(root, "derived/code-identity.json")  # M5
            self.assertIn("own_pack", identity)
            self.assertIn("changed_paths_in_other_claim_packs", identity)
            self.assertEqual(len(identity["driver_checkout"]), 9)
        from joulewise.b5 import harvest
        self.assertEqual(len(harvest.NEG8_REFERENCE_LOSS_CODES), 21)  # M4
        required = {"member.strict_validation_failed", "member.bytes_missing", "contention.unmeasured",
                    "env.member_quiet_state_violated"}
        self.assertTrue(required <= set(harvest.NEG8_REFERENCE_LOSS_CODES))
        pinned = read(fx.FIXTURES / "pin2", "PROGRAM_STRUCTURE.json")
        self.assertEqual(pinned["harvest_pin"], self.pins.pins["pin2"]["head"])
        self.assertEqual(set(pinned["neg8_reference_loss_codes"]), set(harvest.NEG8_REFERENCE_LOSS_CODES))
        # The pin2 source itself is kept with its export and can be checked
        # through the archive's recorded program hashes. The shape test also
        # exercises a real validity-code loss below.

    def test_d7_catalog_path_records_realised_midpoint_loss_on_insufficient_screen(self):
        root, _ = self.pin2("REFERENCES_INSUFFICIENT")
        for archive in (root,):
            screen = read(archive, "derived/neg8-screen.json")["rescreen"]
            self.assertEqual(screen["survivors"]["survivor_screen"], "references_insufficient")
            self.assertFalse(screen["survivors"]["midpoint_lost"])
            self.assertIn("midpoint", {row["position"] for row in screen["survivors"]["reference_losses"]})
        with fx.build_window("beta", variants=("SOURCES_RECOVERED", "REFERENCES_INSUFFICIENT")) as built:
            self.assert_capture_bounds(built)
            screen = read(built.archive, "derived/neg8-screen.json")["rescreen"]
            self.assertEqual(screen["survivors"]["survivor_screen"], "references_insufficient")
            self.assertTrue(screen["survivors"]["midpoint_lost"])

    def test_build_named_alpha_restores_original_synthetic_bytes(self):
        with fx.build_named("ALPHA_STD") as built:
            self.assertTrue(built.claim.is_dir())
            self.assertTrue(built.entry.claim_usable)
            record = open_attempt_record(built.entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)
            handle = open_archive(fx.selected_window(record, seal_pins=self.pins),
                                  seal_pins=self.pins, pack_table=fx.PACK_TABLE)
            self.assertEqual(handle.compare_runs_root(), ())

    def test_all_exported_pin2_capture_pairs_use_marker(self):
        for directory in sorted((fx.FIXTURES / "pin2").iterdir()):
            if not directory.is_dir():
                continue
            data = read(directory, "INDEX_ENTRY.json")
            variants = () if directory.name == "STD" else (directory.name,)
            with self.subTest(case=directory.name), fx.build_window(data["pack"], shape="pin2", variants=variants) as built:
                self.assert_capture_bounds(built)

    def test_each_committed_pin4_archive_has_exact_producer_identity(self):
        pin = self.pins.pins["pin4"]
        directory = fx.FIXTURES / "pin4"
        self.assertEqual({path.name for path in directory.iterdir() if path.is_dir()}, set(fx.PIN4_CASES))
        for name, (pack, variants) in fx.PIN4_CASES.items():
            with self.subTest(case=name):
                case = directory / name
                with tarfile.open(case / "archive.tar.xz") as blob:
                    raw = blob.extractfile("archive/harvest.json").read()
                record = json.loads(raw)
                self.assertEqual(record["harvest_checkout"]["head"], pin["head"])
                self.assertEqual(record["harvest_checkout"]["files"], pin["files"])
                data = read(case, "INDEX_ENTRY.json")
                self.assertEqual(data["pack"], pack)
                self.assertEqual(data["harvest_pin"], pin["head"])
                self.assertEqual(data["harvest_record_sha256"], hashlib.sha256(raw).hexdigest())
                self.assertEqual(fx.exported_case(pack, "pin4", variants), name)
        structure = read(directory, "PROGRAM_STRUCTURE.json")
        self.assertEqual(structure["harvest_pin"], pin["head"])
        self.assertEqual(structure["neg8_reference_loss_codes"],
                         read(fx.FIXTURES / "pin2", "PROGRAM_STRUCTURE.json")["neg8_reference_loss_codes"])

    def test_s3b_archives_preserve_prepared_retry_inputs(self):
        for name in ("BETA_STD_S3B_ROSTER", "BETA_SOURCES_RECOVERED_S3B_ROSTER"):
            case = fx.FIXTURES / "pin4" / name
            data = read(case, "INDEX_ENTRY.json")
            with self.subTest(case=name), tarfile.open(case / "archive.tar.xz") as blob:
                def document(relative):
                    return json.loads(blob.extractfile("archive/" + relative).read())
                pack = "configs/campaigns/" + data["pack_id"]
                tree = document("sources/repo/" + pack + "/plan_tree.json")
                retries = {stage["spare_retry"]["slot"]: stage for stage in tree["stage_graph"]
                           if stage.get("spare_retry")}
                self.assertEqual(set(retries), {"start", "midpoint", "end"})
                prefix = "s0-" if "SOURCES_RECOVERED" in name else "s3b-"
                self.assertEqual({stage["stage_id"] for stage in retries.values()},
                                 {prefix + slot for slot in retries})
                spare = "s3b-end-spare-uninvoked"
                member = next(item for item in retries["end"]["spare_retry"]["members"]
                              if item["run_id"] == spare)
                raw = blob.extractfile("archive/sources/repo/" + member["path"]).read()
                digest = hashlib.sha256(raw).hexdigest()
                self.assertEqual(member["sha256"], digest)
                self.assertEqual(json.loads(raw)["run_id"], spare)
                inventory = document("sources/inputs/sealed_inventory.json")
                executed = document("sources/night-custody/night/executed_inventory.json")
                self.assertEqual(inventory["files"][member["path"]], digest)
                self.assertEqual(executed["measurement_checkout"]["files"][member["path"]], digest)
                roster = document("derived/roster.json")
                self.assertNotIn(spare, {item["run_id"] for item in roster["members"]})

    def test_export_build_still_refuses_wrong_program_hashes(self):
        with mock.patch.dict(os.environ, {"B5_S0_EXPORT_PIN": self.pins.pins["pin4"]["head"]}), \
                mock.patch.object(fx, "sha", return_value="0" * 64):
            with self.assertRaisesRegex(ValueError, "exported program hash differs"):
                fx.build_window("beta")

    def test_existing_unowned_directory_is_preserved(self):
        with tempfile.TemporaryDirectory(prefix="s0-unowned-") as directory:
            sentinel = Path(directory) / "unowned"
            sentinel.write_bytes(b"preserve these bytes")
            with mock.patch.object(fx, "_RESTORE_BASE", directory), fx.build_named("BETA_STD") as built:
                self.assertNotEqual(built.root, Path(directory))
                self.assertEqual(sentinel.read_bytes(), b"preserve these bytes")
        self.assertTrue(self.beta.archive.is_dir())

    def test_loaded_handles_have_independent_lifetimes(self):
        first = fx.build_window("gamma", variants="MIDPOINT_LOST")
        second = fx.build_window("gamma", variants="MIDPOINT_LOST")
        try:
            self.assertNotEqual(first.root, second.root)
            first.close()
            self.assertFalse(first.root.exists())
            self.assertTrue(second.archive.is_dir())
            self.assertTrue(self.beta.archive.is_dir())
        finally:
            first.close()
            second.close()
        self.assertFalse(first.root.exists())
        self.assertFalse(second.root.exists())

    def test_two_processes_load_both_standard_windows_together(self):
        script = """
import contextlib, json, sys
from tests.b5_analysis import fixtures as fx
print('ready', flush=True)
assert sys.stdin.readline() == 'go\\n'
with contextlib.ExitStack() as stack:
    windows = [stack.enter_context(fx.build_named(name)) for name in ('BETA_STD', 'GAMMA_STD')]
    for window in windows:
        record = json.loads((window.archive / 'harvest.json').read_bytes())
        assert record['pack_id'] == window.entry.pack_id
        assert record['claim_usable'] is True
    print(json.dumps([str(window.root) for window in windows]), flush=True)
    assert sys.stdin.readline() == 'close\\n'
"""
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        env.pop("B5_S0_EXPORT_PIN", None)
        processes = []
        def line(process):
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                self.assertTrue(selector.select(timeout=120), "fixture child did not respond")
                return process.stdout.readline()
        try:
            for _ in range(2):
                processes.append(subprocess.Popen([sys.executable, "-c", script], cwd=fx.ROOT,
                    env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
            for process in processes:
                self.assertEqual(line(process).strip(), "ready")
            for process in processes:
                process.stdin.write("go\n")
                process.stdin.flush()
            roots = [json.loads(line(process)) for process in processes]
            self.assertEqual(len({root for pair in roots for root in pair}), 4)
            self.assertTrue(all(Path(root).is_dir() for pair in roots for root in pair))
            for process in processes:
                process.stdin.write("close\n")
                process.stdin.flush()
            for process in processes:
                _stdout, stderr = process.communicate(timeout=120)
                self.assertEqual(process.returncode, 0, stderr)
            self.assertTrue(all(not Path(root).exists() for pair in roots for root in pair))
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.communicate()

    def test_loading_uses_portable_temporary_base(self):
        with tempfile.TemporaryDirectory(prefix="s0-portable-base-") as directory, \
                mock.patch.object(fx, "_RESTORE_BASE", directory):
            for name in ("ALPHA_STD", "BETA_STD", "GAMMA_STD"):
                with self.subTest(name=name), fx.build_named(name) as built:
                    self.assertEqual(built.root.parent, Path(directory).resolve())
                    self.assertTrue(built.claim.is_dir())
                    self.assert_capture_bounds(built)
                    record = open_attempt_record(built.entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE)
                    handle = open_archive(fx.selected_window(record, seal_pins=self.pins),
                                          seal_pins=self.pins, pack_table=fx.PACK_TABLE)
                    self.assertEqual(handle.compare_runs_root(), ())

    def test_relocation_preserves_pinned_science_and_authenticates_original_outputs(self):
        for name, built in (("BETA_STD", self.beta), ("GAMMA_STD", self.gamma)):
            case = fx.FIXTURES / "pin4" / name
            with self.subTest(name=name), tarfile.open(case / "archive.tar.xz") as blob:
                def raw(relative):
                    return blob.extractfile("archive/" + relative).read()
                original = json.loads(raw("harvest.json"))
                for relative, digest in original["outputs"].items():
                    self.assertEqual(hashlib.sha256(raw(relative)).hexdigest(), digest)
                writer = json.loads(raw("sources/claim-runs/whole-window-verdict.json"))
                self.assertEqual(built.writer_row["evaluation_basis"], writer["evaluation_basis"])
                self.assertEqual(built.writer_row["idle_admission_core"], writer["idle_admission_core"])
                self.assertEqual(built.writer_row["member_failures"], writer["member_failures"])
                prefix = b"".join(raw("sources/ledger/calibration_observation_ledger.jsonl").splitlines(keepends=True)[:376])
                self.assertTrue((built.archive / "sources/ledger/calibration_observation_ledger.jsonl").read_bytes().startswith(prefix))
                # These outputs are the pinned program's scientific projection.
                # Location-only relocation must never regenerate them.
                for relative in ("derived/roster.json", "derived/exclusions.json", "derived/neg8-corpus-physics.json",
                                 "withheld/neg8-rescreen-bracket.json", "withheld/neg8-clean-bound.json"):
                    self.assertEqual((built.archive / relative).read_bytes(), raw(relative))

    def test_pin4_provenance_names_producer_commit(self):
        provenance = (fx.FIXTURES / "pin4/PROVENANCE.md").read_text()
        self.assertIn(self.pins.pins["pin4"]["head"], provenance)
        self.assertIn("git archive " + self.pins.pins["pin4"]["head"], provenance)

    def test_pin4_loading_ignores_tree_program_hashes_and_git(self):
        import subprocess
        real_run = subprocess.run
        def no_git(argv, *args, **kwargs):
            self.assertNotEqual(Path(argv[0]).name, "git")
            return real_run(argv, *args, **kwargs)
        # A separate base avoids the standard windows held by setUpClass.
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch.object(fx, "sha", side_effect=AssertionError("tree hash read")), \
                mock.patch.object(subprocess, "run", side_effect=no_git), \
                mock.patch.object(subprocess, "check_output", side_effect=AssertionError("git subprocess")):
            for name in ("BETA_QUAD_MEMBER_REMOVED", "BETA_STD_S3B_ROSTER",
                         "BETA_SOURCES_RECOVERED_S3B_ROSTER"):
                with self.subTest(case=name), fx.build_named(name) as built:
                    self.assertEqual(read(built.archive, "harvest.json")["harvest_checkout"]["head"],
                                     self.pins.pins["pin4"]["head"])

    def test_standard_real_writer_claim_licensing_and_failed_row(self):
        for built in (self.beta, self.gamma):
            self.assertEqual(built.writer_row["status"], "failed")
            self.assertTrue(built.writer_row["claim_licensing"])
            self.assertTrue(built.entry.claim_usable)
            self.assertEqual(built.writer_row["member_failures"], [])
        _, entry = self.pin2()
        self.assertTrue(open_attempt_record(entry, seal_pins=self.pins, pack_table=fx.PACK_TABLE).claim_usable)

    def assert_capture_bounds(self, built):
        from joulewise.calibration_ledger import load_calibration_ledger_snapshot
        from tests.test_harvest_b5_window import SESSION_ID
        snapshot = load_calibration_ledger_snapshot(
            built.archive / "sources/ledger/calibration_observation_ledger.jsonl",
            built.archive / "derived/terminal-pin.json", require_committed_pin=False,
            verify_custody=False, repo_root=built.measurement)
        self.assertEqual(snapshot.refusal_reasons, ())
        slots = {row.bracket_slot: Decimal(row.exact_bound_lexeme_s) for row in snapshot.observations
                 if row.bracket_session_id == SESSION_ID and row.bracket_slot in ("pre", "post")}
        self.assertEqual(set(slots), {"pre", "post"})
        self.assertEqual(slots["post"] - slots["pre"], fx.POST_CAPTURE_BOUND_MARKER_S)
        assessment = read(built.archive, "withheld/bracket-evaluation.json")["assessment"]
        self.assertEqual(Decimal(assessment["pre"]["b_fiducial_decimal_s"]), slots["pre"])
        self.assertEqual(Decimal(assessment["post"]["b_fiducial_decimal_s"]), slots["post"])
        allowance = assessment["acceptance"]["allowance"]
        operative = Decimal(allowance["operative_b_fiducial_decimal_s"])
        self.assertEqual(operative, max(slots.values()) + Decimal(allowance["value_s"]))
        self.assertEqual(float(operative), assessment["b_fiducial_s"])
        return operative

    def test_distinct_capture_and_window_operative_bounds(self):
        with fx.build_named("ALPHA_STD") as alpha:
            bounds = [self.assert_capture_bounds(built) for built in (alpha, self.beta, self.gamma)]
        self.assertEqual(len(set(bounds)), 3)

    def test_named_removals_and_minimum_boundary(self):
        for variant, repeat_n, quad_n, usable in (("REPEAT6_REMOVED", 9, 10, True), ("QUAD_MEMBER_REMOVED", 10, 9, True),
                                                ("SIX_QUADS_REMOVED", 10, 4, False), ("FIVE_QUADS_REMOVED", 10, 5, True)):
            with self.subTest(variant=variant), fx.build_window("beta", variants=(variant,)) as built:
                exclusions = read(built.archive, "derived/exclusions.json")
                cell = exclusions["cells"][0]
                self.assertEqual(cell["n_kept"], {"repeat": repeat_n, "quad": quad_n})
                self.assertEqual(built.entry.claim_usable, usable)
                self.assert_capture_bounds(built)

    def test_writer_dropped_members_have_the_real_condition_mapping(self):
        for variant in ("WRITER_DROPPED_SCIENCE_MEMBER", "WRITER_DROPPED_REFERENCE"):
            with self.subTest(variant=variant), fx.build_window("beta", variants=(variant,)) as built:
                row = built.writer_row
                self.assert_capture_bounds(built)
                self.assertIn("whole_window_bundle_invalid", row["idle_admission_core"]["conditions"])
                excluded = {item["bundle_id"] for item in row["excluded_bundles"]}
                failures = {item["member_id"] for item in row["member_failures"] if item["reason_code"] == "whole_window_bundle_invalid"}
                self.assertEqual(excluded, failures)
                self.assertEqual(len(excluded), 1)
                if variant == "WRITER_DROPPED_REFERENCE":
                    screen = read(built.archive, "derived/neg8-screen.json")
                    # The pinned harvest projects recorded manifests onto the
                    # writer's included-member basis. The writer-dropped id is
                    # absent from that projection, so it is not a new harvest
                    # loss (design 6.3 item 1 already identifies this omission).
                    dropped = next(iter(excluded))
                    self.assertNotIn(dropped, row["bundle_ids"])
                    self.assertNotIn(dropped, screen["harvest_reference_losses"])
                    self.assertEqual(screen["rescreen"]["survivors"]["reference_counts"],
                                     {"start": 3, "midpoint": 1, "end": 2})

    def test_d5_d6_d7_sources_recovered_and_bundle_absent(self):
        aroot, _ = self.pin2()
        self.assertNotIn("reference_source", read(aroot, "derived/neg8-allowance.json"))
        self.assertNotIn("reference_source", read(aroot, "derived/neg8-screen.json")["rescreen"])
        with fx.build_window("beta", variants=("SOURCES_RECOVERED",)) as built:
            self.assert_capture_bounds(built)
            self.assertEqual(built.writer_row["source_campaign_manifests"], [])
            screen = read(built.archive, "derived/neg8-screen.json")["rescreen"]
            self.assertEqual(screen["reference_source"]["source"], "claim_campaign_manifests_authenticated")  # D5
            allowance = read(built.archive, "derived/neg8-allowance.json")
            self.assertIn("reference_source", allowance)  # D6
            losses = screen["survivors"]["reference_losses"]
            self.assertIn("bundle_absent", {loss["reason"] for loss in losses})  # D7
        with fx.build_window("gamma", variants=("MIDPOINT_LOST",)) as built:
            self.assert_capture_bounds(built)
            screen = read(built.archive, "derived/neg8-screen.json")["rescreen"]
            self.assertTrue(screen["survivors"]["midpoint_lost"])
            self.assertEqual(screen["decision"], "passed")

    def test_stored_neg8_passed_variant(self):
        with fx.build_window("beta", variants=("STORED_NEG8_PASSED",)) as built:
            self.assert_capture_bounds(built)
            self.assertEqual(built.writer_row["idle_admission_core"]["neg8_bracket"]["decision"], "passed")
            self.assertEqual(read(built.archive, "derived/neg8-allowance.json")["source"], "survivor_rescreen")

    def test_validator_over_synthetic_archive_copy(self):
        row = read(self.beta.archive, "sources/claim-runs/whole-window-verdict.json")
        result = whole_window.validate_whole_window_verdict_row(row, self.beta.archive / "sources/claim-runs", set(row["bundle_ids"]))
        # This is the O9 experiment, not a weakening of the validator. Its
        # original-path/basis and synthetic-observation checks still refuse.
        self.assertFalse(result.authentic)
