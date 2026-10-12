"""E3 launch provenance comes from the consumer bracket, using real receipts."""
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise import whole_window as ww
from joulewise import arm_readiness
from tests import test_whole_window as support
from tests.test_arm_readiness_schemas import TEST_BOOT_SESSION_ID
from tests.b5_analysis import fixtures_s3 as fx


class LaunchLineageContextTests(unittest.TestCase):
    def test_gamma_standard_and_another_launch_member(self):
        case = fx.Case("GAMMA_STD")
        self.addCleanup(case.close)
        self.assertNotIn("launch_lineage", case.row["evaluation_basis"])
        with fx.adapter_projection(case):
            result = ww.validate_whole_window_verdict_row(case.row, case.window.claim,
                set(case.row["bundle_ids"]), consumption_session=case.session())
        self.assertTrue(result.admitted, result.reasons)
        helper = support.LaunchLineageWholeWindowTests()
        self.addCleanup(helper.doCleanups)
        launch, lineage = helper._completed_launch()
        root, _ = helper._write_authenticated_marker_bundle(launch, lineage, "other-member")
        other_metadata = json.loads((root / "other-member/metadata.json").read_text())
        bundle = "s0-mock-r01"
        case.mutate_metadata(bundle, lambda metadata: metadata.update(extra=other_metadata["extra"]))
        case.mutate_config(bundle, lambda config: config.setdefault("run_metadata", {}).setdefault("tags", []).append("launch_lineage_required"))
        case.bind_row()
        with fx.adapter_projection(case), mock.patch.object(arm_readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID):
            result = ww.validate_whole_window_verdict_row(case.row, case.window.claim,
                set(case.row["bundle_ids"]), consumption_session=case.session())
        self.assertFalse(result.admitted)
        self.assertTrue(any(reason.startswith(("launch_", "readiness_")) for reason in result.reasons), result.reasons)
        (fx.SCRATCH / "gamma-launch-refusal.json").write_text(json.dumps({"admitted": result.admitted,
            "reasons": list(result.reasons), "counterfactual": "one tagged member carries another completed launch"}, indent=2) + "\n")

    def test_governed_launch_recomputed_without_stored_lineage(self):
        helper = support.LaunchLineageWholeWindowTests()
        self.addCleanup(helper.doCleanups)
        launch, lineage = helper._completed_launch()
        root, occurrence = helper._write_authenticated_marker_bundle(launch, lineage, "member-a")
        _, second = helper._write_authenticated_marker_bundle(launch, lineage, "member-b")
        with tempfile.TemporaryDirectory(prefix="s3-lineage-") as temporary:
            bracket = helper._write_calibration_bracket(Path(temporary), lineage)
            context = ww.ArchiveContext(Path(temporary), window_bracket=bracket, governed_e3=True)
            row = {"evaluation_basis": {"member_occurrences": [occurrence, second]},
                "idle_admission_core": {"instrument_calibration_bracket": {"status": "failed"}}}
            neg8 = ww.Neg8ScreenOutcome(True, "survivor_rescreen", None, {"drift_bound_artifact": {"launch_lineage": lineage}})
            with mock.patch.object(arm_readiness, "_current_boot_session_id", return_value=TEST_BOOT_SESSION_ID):
                self.assertEqual(ww._archive_launch_refusal_reasons(row, root, context, neg8), ())
                # Swap one member's full lineage to a second completed launch.
                other, other_lineage = helper._completed_launch()
                metadata = json.loads((root / "member-b/metadata.json").read_text())
                metadata["extra"]["launch_lineage"] = other_lineage
                (root / "member-b/metadata.json").write_text(json.dumps(metadata))
                reasons = ww._archive_launch_refusal_reasons(row, root, context, neg8)
                self.assertTrue(reasons)
                self.assertTrue(any(reason.startswith(("launch_", "readiness_")) for reason in reasons), reasons)

    def test_governed_launch_uses_consumer_bracket_and_allowance_bound(self):
        context = ww.ArchiveContext(Path("/private/tmp"), window_bracket={"pre": {"capture": "consumer"}}, governed_e3=True)
        row = {"evaluation_basis": {"member_occurrences": [{"bundle_path": "member"}]},
            "idle_admission_core": {"instrument_calibration_bracket": {"pre": "stored"}}}
        neg8 = ww.Neg8ScreenOutcome(True, "survivor_rescreen", None, {"drift_bound_artifact": {"bound": "harvest"}})
        with mock.patch.object(ww, "_authenticated_bundle_launch_lineage_set", return_value={"launch": "same"}), \
                mock.patch.object(ww, "_authenticate_whole_window_launch_sources", return_value={"launch": "same"}) as authenticate:
            self.assertEqual(ww._archive_launch_refusal_reasons(row, Path("/private/tmp"), context, neg8), ())
        self.assertEqual(authenticate.call_args.kwargs["calibration_bracket"], {"pre": {"capture": "consumer"}})
        self.assertEqual(authenticate.call_args.kwargs["drift_bound_artifact"], {"bound": "harvest"})

    def test_ungoverned_launch_preserves_original_call(self):
        context = ww.ArchiveContext(Path("/private/tmp"))
        row = {"row": "same"}
        with mock.patch.object(ww, "_whole_window_row_launch_refusal_reasons", return_value=("launch_lifecycle_incomplete",)) as check:
            self.assertEqual(ww._archive_launch_refusal_reasons(row, Path("/private/tmp"), context,
                ww.Neg8ScreenOutcome(False, None, "screen_not_passed", None)), ("launch_lifecycle_incomplete",))
        check.assert_called_once_with(row, Path("/private/tmp"))


if __name__ == "__main__":
    unittest.main()
