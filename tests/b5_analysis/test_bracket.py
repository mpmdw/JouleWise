"""L9 S2 rule probes, entirely synthetic; fixture builds are module-cached."""
import inspect
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise import calibration_bracketing as calibration
from joulewise.b5_analysis import bracket as br
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis import fixtures_s2 as fx

_WINDOWS = {}


def windows():
    for name in ("GAMMA_STD", "ALPHA_STD", "BETA_STD"):
        if name not in _WINDOWS:
            _WINDOWS[name] = fx.build_named(name)
    return _WINDOWS


class BracketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.windows = windows()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s2-test-")
        self.addCleanup(self.tmp.cleanup)
        self.adapter = fx.capture_adapter()
        self.adapter.__enter__()
        self.addCleanup(self.adapter.__exit__, None, None, None)

    def cloned(self, name="GAMMA_STD"):
        return fx.fork(self.windows[name], Path(self.tmp.name) / "clone")

    def evaluate(self, built):
        return br.evaluate_window_bracket(fx.handle(built), repo_root=fx.s0.ROOT)

    def test_gamma_equals_harvest_and_records_only_trigger(self):
        built = self.windows["GAMMA_STD"]
        handle = fx.handle(built)
        result = br.evaluate_window_bracket(handle, repo_root=fx.s0.ROOT)
        self.assertEqual((result.trigger_scope, result.compared_with_harvest), ("window_evidence", "equal"))
        self.assertEqual(result.evaluation["status"], "passed")
        prospective = result.evaluation["acceptance"]["prospective_rederivation"]
        self.assertIn("new_systematic_failure_challenges_preflight_screen", prospective["recorded_only_triggers"])
        self.assertEqual(result.sources_sha256sums_sha256, fx.s0.sha(built.archive / "sources/SHA256SUMS"))
        self.assertEqual(result.ledger_copy_sha256, fx.s0.sha(built.archive / br.LEDGER_COPY))
        census = {row.path: row for row in handle.census()}
        self.assertEqual(census["sources/SHA256SUMS"].sha256, result.sources_sha256sums_sha256)
        self.assertEqual(census["sources/SHA256SUMS"].check, "input_census")

    def test_alpha_sealed_is_fresh_without_harvest_digest(self):
        built = self.windows["ALPHA_STD"]
        self.assertNotIn("withheld/bracket-evaluation.json", fx.handle(built).record["outputs"])
        result = self.evaluate(built)
        self.assertEqual((result.trigger_scope, result.compared_with_harvest), ("sealed", "no_harvest_digest"))
        self.assertEqual(result.evaluation["acceptance"]["freshness"]["status"], "fresh")

    def test_source_inventory_read_once(self):
        built = self.windows["GAMMA_STD"]
        manifest = built.archive / "sources/SHA256SUMS"
        original = Path.read_bytes
        reads = []
        def read(path):
            if path == manifest:
                reads.append(path)
            return original(path)
        with mock.patch.object(Path, "read_bytes", read):
            self.evaluate(built)
        self.assertEqual(len(reads), 1)

    def test_each_listed_assessment_field_must_match(self):
        built = self.cloned()
        target = built.archive / "withheld/bracket-evaluation.json"
        original = json.loads(target.read_bytes())
        for key in br.COMPARED_FIELDS:
            with self.subTest(key=key):
                row = json.loads(json.dumps(original))
                row["assessment"][key] = "counterfactual"
                fx.s0.put(target, row)
                fx.refresh(built)
                with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_differs_from_harvest$"):
                    self.evaluate(built)
        for key in br.COMPARED_ACCEPTANCE_FIELDS:
            with self.subTest(key="acceptance." + key):
                row = json.loads(json.dumps(original))
                row["assessment"]["acceptance"][key] = "counterfactual"
                fx.s0.put(target, row)
                fx.refresh(built)
                with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_differs_from_harvest$"):
                    self.evaluate(built)
        row = json.loads(json.dumps(original))
        row["reasons"] = ["counterfactual"]
        fx.s0.put(target, row)
        fx.refresh(built)
        with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_differs_from_harvest$"):
            self.evaluate(built)

    def test_members_and_window_times_are_not_comparison_fields(self):
        built = self.cloned()
        target = built.archive / "withheld/bracket-evaluation.json"
        row = json.loads(target.read_bytes())
        row["members"] = 999
        row["assessment"].update(members=999, window_start_s=-999, window_end_s=999)
        fx.s0.put(target, row)
        fx.refresh(built)
        self.assertEqual(self.evaluate(built).compared_with_harvest, "equal")

    def test_edited_harvest_without_updated_output_digest_refuses(self):
        built = self.cloned()
        target = built.archive / "withheld/bracket-evaluation.json"
        with target.open("ab") as output:
            output.write(b" ")
        with self.assertRaisesRegex(AnalysisRefusal, "^archive_output_unauthenticated$"):
            self.evaluate(built)

    def test_governed_sealed_scope_is_not_passed(self):
        actual = calibration.evaluate_calibration_bracket
        def sealed(*args, **kwargs):
            kwargs["trigger_scope"] = "sealed"
            return actual(*args, **kwargs)
        with mock.patch.object(calibration, "evaluate_calibration_bracket", side_effect=sealed):
            with self.assertRaisesRegex(AnalysisRefusal, "^window_bracket_not_passed$"):
                self.evaluate(self.windows["GAMMA_STD"])

    def test_appended_three_entries_cut_at_terminal_without_changing_evaluation(self):
        built = self.cloned()
        original = self.evaluate(built)
        path = built.archive / br.LEDGER_COPY
        raw = path.read_bytes()
        last = json.loads(raw.splitlines()[-1])
        # The tail is deliberately not part of this window's decision chain.
        appended = b"".join(json.dumps({"sequence": last["sequence"] + n, "receipt_digest": "a" * 64}).encode() + b"\n"
                            for n in (1, 2, 3))
        path.write_bytes(raw + appended)
        fx.refresh(built)
        pin = json.loads((built.archive / br.TERMINAL_PIN).read_bytes())
        self.assertEqual(br.ledger_prefix(path.read_bytes(), pin), raw)
        changed = self.evaluate(built)
        self.assertEqual(changed.evaluation, original.evaluation)
        self.assertNotEqual(changed.ledger_copy_sha256, original.ledger_copy_sha256)

    def test_absent_terminal_sequence_refuses(self):
        built = self.windows["GAMMA_STD"]
        raw = (built.archive / br.LEDGER_COPY).read_bytes()
        pin = json.loads((built.archive / br.TERMINAL_PIN).read_bytes())
        pin["sequence"] += 100
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_prefix_not_at_terminal_pin$"):
            br.ledger_prefix(raw, pin)

    def test_terminal_head_mismatch_refuses(self):
        built = self.windows["GAMMA_STD"]
        raw = (built.archive / br.LEDGER_COPY).read_bytes()
        pin = json.loads((built.archive / br.TERMINAL_PIN).read_bytes())
        pin["head_digest"] = "a" * 64
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_prefix_not_at_terminal_pin$"):
            br.ledger_prefix(raw, pin)

    def test_chain_change_below_terminal_refuses(self):
        built = self.windows["GAMMA_STD"]
        raw = (built.archive / br.LEDGER_COPY).read_bytes()
        pin = json.loads((built.archive / br.TERMINAL_PIN).read_bytes())
        raw = raw.replace(b'"predecessor_digest":"', b'"predecessor_digest":"a', 1)
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_prefix_not_at_terminal_pin$"):
            br.ledger_prefix(raw, pin)

    def test_ledger_copy_digest_mismatch(self):
        built = self.cloned()
        with (built.archive / br.LEDGER_COPY).open("ab") as output:
            output.write(b" ")
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copy_digest_mismatch$"):
            self.evaluate(built)

    def test_missing_ledger_manifest_line_refuses(self):
        built = self.cloned()
        path = built.archive / "sources/SHA256SUMS"
        path.write_text("".join(line for line in path.read_text().splitlines(keepends=True)
                                if not line.endswith("  ledger/calibration_observation_ledger.jsonl\n")))
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copy_digest_mismatch$"):
            self.evaluate(built)

    def test_live_ledger_one_byte_changed_mid_file_refuses(self):
        built = self.windows["GAMMA_STD"]
        raw = (built.archive / br.LEDGER_COPY).read_bytes()
        path = Path(self.tmp.name) / "live.jsonl"
        path.write_bytes(raw + b"synthetic extension\n")
        br.require_ledger_copies_are_prefixes([fx.handle(built)], path)
        raw = bytearray(path.read_bytes())
        raw[len(raw) // 2] ^= 1
        path.write_bytes(raw)
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copy_not_prefix_of_live$"):
            br.require_ledger_copies_are_prefixes([fx.handle(built)], path)

    def test_archived_copy_changed_mid_file_with_digest_rebound_refuses(self):
        built = self.cloned()
        path = built.archive / br.LEDGER_COPY
        raw = path.read_bytes()
        live = Path(self.tmp.name) / "live.jsonl"
        live.write_bytes(raw)
        changed = bytearray(raw)
        changed[len(changed) // 2] ^= 1
        path.write_bytes(changed)
        fx.refresh(built)
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copy_not_prefix_of_live$"):
            br.require_ledger_copies_are_prefixes([fx.handle(built)], live)

    def test_release_checks_whole_archived_copy_not_only_terminal_cut(self):
        built = self.cloned()
        path = built.archive / br.LEDGER_COPY
        raw = path.read_bytes()
        path.write_bytes(raw + b"later archived bytes\n")
        fx.refresh(built)
        live = Path(self.tmp.name) / "live.jsonl"
        live.write_bytes(raw)
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copy_not_prefix_of_live$"):
            br.require_ledger_copies_are_prefixes([fx.handle(built)], live)

    def test_one_snapshot_cannot_be_supplied_for_two_windows(self):
        self.assertEqual(tuple(inspect.signature(br.evaluate_window_bracket).parameters), ("archive", "repo_root"))
        first = self.evaluate(self.windows["ALPHA_STD"])
        second = self.evaluate(self.windows["GAMMA_STD"])
        self.assertNotEqual(first.terminal_sequence, second.terminal_sequence)
        self.assertNotEqual(first.ledger_copy_sha256, second.ledger_copy_sha256)

    def test_distinct_post_capture_bounds_and_three_operative_bounds(self):
        results = [self.evaluate(self.windows[name]) for name in ("ALPHA_STD", "BETA_STD", "GAMMA_STD")]
        self.assertEqual(len({row.b_fiducial_s for row in results}), 3)
        for result in results:
            pre, post = result.evaluation["pre"], result.evaluation["post"]
            self.assertNotEqual(pre["b_fiducial_s"], post["b_fiducial_s"])
            self.assertEqual(result.evaluation["endpoint_max_b_fiducial_s"], post["b_fiducial_s"])
            self.assertEqual(result.b_fiducial_s, result.evaluation["b_fiducial_s"])

    def test_member_missing_operative_bound_refuses(self):
        window = self.evaluate(self.windows["GAMMA_STD"])
        with self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
            br.require_member_bound_is_window_bracket({}, window)

    def test_member_pre_capture_bound_substituted_refuses(self):
        window = self.evaluate(self.windows["GAMMA_STD"])
        provenance = {"operative_fiducial_bound_s": window.evaluation["pre"]["b_fiducial_s"]}
        with self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
            br.require_member_bound_is_window_bracket(provenance, window)

    def test_member_another_window_bound_substituted_refuses(self):
        gamma, beta = (self.evaluate(self.windows[name]) for name in ("GAMMA_STD", "BETA_STD"))
        with self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
            br.require_member_bound_is_window_bracket({"operative_fiducial_bound_s": beta.b_fiducial_s}, gamma)

    def test_member_bound_matches_exactly_and_rejects_nonfinite_and_bool(self):
        window = self.evaluate(self.windows["GAMMA_STD"])
        br.require_member_bound_is_window_bracket({"operative_fiducial_bound_s": window.b_fiducial_s}, window)
        br.require_member_bound_is_window_bracket({"operative_fiducial_bound_s": window.b_fiducial_s}, window.evaluation)
        for value in (True, "0.045031", float("nan"), float("inf"), window.b_fiducial_s + 1e-15):
            with self.subTest(value=value), self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
                br.require_member_bound_is_window_bracket({"operative_fiducial_bound_s": value}, window)


class BlockBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = fx.toy_ledger()
        cls.acceptance = {"identity_epoch": calibration.load_calibration_acceptance_bound()["identity_epoch"],
                          "derivation_corpus": {"members": [{"b_fiducial_s": "0.036"}]}}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s2-block-")
        self.addCleanup(self.tmp.cleanup)

    def test_made_up_b_max_and_b_sens(self):
        prefix = br.ledger_prefix(self.raw, fx.pin_at(self.raw, 500))
        maximum = br.block_b_max(self.acceptance, prefix)
        self.assertEqual((maximum.value_s, maximum.attained_by_sequence, maximum.T), (.040, 456, 500))
        self.assertEqual(br.b_sens(.038, maximum), .040)
        self.assertEqual(br.b_sens(.045, maximum), .045)

    def test_acceptance_maximum_can_dominate_without_a_ledger_sequence(self):
        acceptance = dict(self.acceptance, derivation_corpus={"members": [{"b_fiducial_s": ".050"}]})
        maximum = br.block_b_max(acceptance, br.ledger_prefix(self.raw, fx.pin_at(self.raw, 500)))
        self.assertEqual((maximum.value_s, maximum.attained_by_sequence), (.050, None))

    def test_acceptance_member_attainer_is_identified_from_ledger_row(self):
        acceptance = dict(self.acceptance, derivation_corpus={"members": [
            {"member_id": "toy-188", "b_fiducial_s": ".900"}]})
        maximum = br.block_b_max(acceptance, br.ledger_prefix(self.raw, fx.pin_at(self.raw, 500)))
        self.assertEqual((maximum.value_s, maximum.attained_by_sequence), (.900, 376))

    def test_T_window_is_second_and_its_copy_is_cut_at_500(self):
        archives = [fx.toy_archive(Path(self.tmp.name) / str(n), self.raw, n) for n in (480, 500, 490)]
        maximum = br.block_b_max_for_archives([fx.handle(item) for item in archives])
        self.assertEqual((maximum.value_s, maximum.attained_by_sequence, maximum.T), (.040, 456, 500))

    def test_copy_disagrees_below_T_refuses(self):
        archives = [fx.toy_archive(Path(self.tmp.name) / str(n), self.raw, n) for n in (480, 500, 490)]
        (archives[0].archive / br.LEDGER_COPY).write_bytes(fx.toy_ledger(changed_at=456))
        # Both chains are internally valid, independently bound, and at their
        # respective pins. Only the cross-window byte-prefix rule rejects them.
        fx.s0.put(archives[0].archive / br.TERMINAL_PIN, fx.pin_at(fx.toy_ledger(changed_at=456), 480))
        fx.refresh(archives[0])
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_copies_disagree_below_T$"):
            br.block_b_max_for_archives([fx.handle(item) for item in archives])

    def test_b_max_unchanged_when_all_historical_capture_files_unreadable(self):
        prefix = br.ledger_prefix(self.raw, fx.pin_at(self.raw, 500))
        original = br.block_b_max(self.acceptance, prefix)
        self.assertEqual((original.value_s, original.attained_by_sequence, original.T), (.040, 456, 500))
        # Refuse every file read, including absent/unreachable historical
        # locators. B_max must do zero file I/O and keep every ledger row.
        with mock.patch.object(Path, "read_bytes", side_effect=PermissionError("historical file unreadable")), \
                mock.patch.object(Path, "read_text", side_effect=PermissionError("historical file unreadable")):
            self.assertEqual(br.block_b_max(self.acceptance, prefix), original)

    def test_b_max_refuses_malformed_chain(self):
        with self.assertRaisesRegex(AnalysisRefusal, "^ledger_prefix_not_at_terminal_pin$"):
            br.block_b_max(self.acceptance, self.raw + b"broken\n")

    def test_b_max_refuses_bad_numeric_bound(self):
        for value in (True, "NaN", "-0.1", "Infinity", "1e1000", "bad"):
            acceptance = dict(self.acceptance, derivation_corpus={"members": [{"b_fiducial_s": value}]})
            with self.subTest(value=value), self.assertRaisesRegex(AnalysisRefusal, "^block_b_max_invalid$"):
                br.block_b_max(acceptance, self.raw)
