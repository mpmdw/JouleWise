"""P2-B1: the HAZARD_PACK NEG-8 mint's member verdicts and V1 timestamps.

NONCORE R1 ruling (orchestrator, 2026-10-06): the HAZARD mint drops a corpus
member only for a reason in DESIGN N2's closed member-validity set
(``NEG8_MINT_DROP_REASONS``); a member whose energy evidence cannot be
classified is kept (indeterminate) and the mint then cannot derive a bound; a
launch-lineage, condition, calibration-record or inventory reason refuses the
corpus (no majority vote on the condition).  The harvest accepts exactly the
mint's drop set.

V1 (PLAN2 row 2): the bound's ``derived_at_s`` is the end of the latest kept
corpus member's measured window, never the clock of whoever mints; the
row validator re-derives the end-reference evaluation time on a HAZARD root.
"""

from __future__ import annotations

import json
import tempfile
import time
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from joulewise import arm_readiness, whole_window
from joulewise.b5 import harvest
from tests.test_window_lineage import _SentinelMixin, build_window

SPAN_BASE_S = 1_800_000_000.0


def _member_number(path: Path) -> int:
    return int(path.name.rsplit("r", 1)[1])


class _CorpusFixture(_SentinelMixin):
    """Twelve corpus bundles in a hazard bound root, predicates patched per member."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.addCleanup(self._start_sentinels().close)
        self.w = build_window(Path(tmp.name))
        self.members = []
        for index in range(1, 13):
            self._write_member(index)
            name = f"neg8-refcorpus-r{index:02d}"
            self.members.append({"bundle_id": name, "bundle_path": name})
        self.manifest = self.w.bound / "neg8-corpus.collected.json"
        self.manifest.write_text(json.dumps({
            "schema_version": "joulewise.neg8_reference_corpus.v1", "corpus_id": "hazard-corpus",
            "freeze_status": "settled_reference", "condition_id": "df-rq-mid",
            "members": self.members}, indent=2, sort_keys=True) + "\n")
        self.reset()

    def _write_member(self, index: int) -> None:
        bundle = self.w.bound / f"neg8-refcorpus-r{index:02d}"
        bundle.mkdir(exist_ok=True)
        (bundle / "config.json").write_text(json.dumps({"run_id": bundle.name}) + "\n")
        (bundle / "metadata.json").write_text("{}\n")
        (bundle / "summary_metrics.json").write_text(
            json.dumps({"index": index, "status": "succeeded"}) + "\n")

    def reset(self) -> None:
        for index in range(1, 13):
            self._write_member(index)
        # Per-member overrides, keyed by member number.
        self.energy_cause: dict[int, str] = {}
        self.custody_invalid: set[int] = set()
        self.not_strict: set[int] = set()
        self.identity: dict[int, tuple[str | None, bool]] = {}
        self.lineage_error: set[int] = set()
        self.calibration_unrecorded: set[int] = set()
        self.inventory_error: set[int] = set()
        self.span_missing: set[int] = set()

    def bundle(self, number: int) -> Path:
        return self.w.bound / f"neg8-refcorpus-r{number:02d}"

    def patches(self) -> ExitStack:
        def energy(path: Path, **_kwargs):
            number = _member_number(path)
            cause = self.energy_cause.get(number)
            if cause is not None:
                return None, None, "provenance", cause
            value = 10.0 + number
            return {"point_j": value, "lower_j": value, "upper_j": value}, value - 1.0, None, None

        def lineage(path, **_kwargs):
            if _member_number(Path(path)) in self.lineage_error:
                raise arm_readiness.LaunchLineageError("launch_binding_mismatch", "fixture")
            return None

        def fields(metadata):
            number = metadata.get("_n") if isinstance(metadata, dict) else None
            return {"os_build": "25G83", "power_supply_identity_sha256": "e" * 64,
                    "calibration_identity_sha256": (
                        None if number in self.calibration_unrecorded else "f" * 64)}

        real_read = whole_window._read_json_object

        def read(path: Path):
            value = real_read(path)
            if path.name == "metadata.json" and isinstance(value, dict):
                value = {**value, "_n": _member_number(path.parent)}
            return value

        real_inventory = whole_window._bundle_evidence_sha256

        def inventory(path: Path):
            if _member_number(path) in self.inventory_error:
                raise ValueError("fixture inventory")
            return real_inventory(path)

        def span_end(path: Path):
            number = _member_number(path)
            return None if number in self.span_missing else SPAN_BASE_S + 100.0 * number

        stack = ExitStack()
        for target, kwargs in (
            ("authenticate_bundle_launch_lineage", {"side_effect": lineage}),
            ("_custody_strict_invalid", {"side_effect": lambda path, *_a, **_k:
                                         _member_number(path) in self.custody_invalid}),
            ("_current_strict_summary", {"side_effect": lambda summary, _path:
                                         summary.get("index") not in self.not_strict}),
            ("_scientific_config_identity", {"side_effect": lambda path:
                                             self.identity.get(_member_number(path), ("d" * 64, True))}),
            ("_reference_energy_evidence_detail", {"side_effect": energy}),
            # The three-value projection, so the same fixture runs against a
            # tree that predates the cause (the fail-before check).
            ("_reference_energy_evidence", {"side_effect": lambda path, **kw: energy(path)[:3]}),
            ("neg8_freshness_binding_fields", {"side_effect": fields}),
            ("_read_json_object", {"side_effect": read}),
            ("_bundle_evidence_sha256", {"side_effect": inventory}),
            ("_measured_window_end_s", {"side_effect": span_end}),
        ):
            stack.enter_context(patch.object(whole_window, target, create=True, **kwargs))
        return stack

    def mint(self) -> dict:
        with self.patches():
            return whole_window.mint_neg8_drift_bound_artifact(self.w.bound, self.manifest)

    def drops(self) -> list[dict]:
        with self.patches():
            return whole_window.neg8_corpus_mint_drops(self.w.bound, self.manifest)


class MintMemberVerdictTests(_CorpusFixture, unittest.TestCase):
    def test_the_drop_set_is_the_closed_member_validity_set_and_the_harvest_accepts_exactly_it(self) -> None:
        expected = {"status_not_succeeded", "not_current_strict_mint", "custody_triangle_disagrees",
                    "precheck_ineligible", "reduction_mismatch"}
        self.assertEqual(whole_window.NEG8_MINT_DROP_REASONS, expected)
        self.assertEqual(harvest.NEG8_ACCEPTED_DROP_REASONS, whole_window.NEG8_MINT_DROP_REASONS)

    def test_each_closed_reason_drops_one_member_and_the_bound_derives_from_the_rest(self) -> None:
        def absent():
            for path in self.bundle(2).iterdir():
                path.unlink()
            self.bundle(2).rmdir()

        def failed():
            (self.bundle(2) / "summary_metrics.json").write_text(
                json.dumps({"index": 2, "status": "failed"}) + "\n")

        cases = (
            ("status_not_succeeded", absent),
            ("status_not_succeeded", failed),
            ("custody_triangle_disagrees", lambda: self.custody_invalid.add(2)),
            ("not_current_strict_mint", lambda: self.not_strict.add(2)),
            ("precheck_ineligible", lambda: self.energy_cause.update({2: "precheck_ineligible"})),
            ("reduction_mismatch", lambda: self.energy_cause.update({2: "reduction_mismatch"})),
        )
        for reason, setup in cases:
            with self.subTest(reason=reason, setup=setup.__name__):
                self.reset()
                setup()
                self.assertEqual(self.drops(), [{"bundle_id": "neg8-refcorpus-r02", "reason": reason}])
                artifact = self.mint()
                self.assertEqual(len(artifact["reference_corpus"]["members"]), 11)
                self.assertNotIn("neg8-refcorpus-r02", artifact["reference_corpus"]["member_ids"])

    def test_an_unclassified_energy_evaluation_keeps_the_member_and_derives_no_bound(self) -> None:
        for cause in ("reduction_unavailable", "precheck_absent", "precheck_unknown",
                      "reduction_incomplete", None):
            with self.subTest(cause=cause):
                self.reset()
                self.energy_cause[4] = cause  # None: a problem with no cause recorded
                if cause is None:
                    self.energy_cause[4] = "energy_unclassified"
                self.assertEqual(self.drops(), [])  # kept, never dropped
                with self.assertRaisesRegex(ValueError, "could not be verified.*neg8-refcorpus-r04"):
                    self.mint()

    def test_non_member_validity_reasons_refuse_the_corpus(self) -> None:
        cases = (
            ("launch_lineage:launch_binding_mismatch", lambda: self.lineage_error.add(5)),
            ("not_canonical_condition", lambda: self.identity.update({5: ("d" * 64, False)})),
            ("calibration_identity_unrecorded", lambda: self.calibration_unrecorded.add(5)),
            ("bundle_inventory_invalid", lambda: self.inventory_error.add(5)),
        )
        for reason, setup in cases:
            with self.subTest(reason=reason):
                self.reset()
                setup()
                pattern = f"refused.*neg8-refcorpus-r05={reason}"
                with self.assertRaisesRegex(ValueError, pattern):
                    self.drops()
                with self.assertRaisesRegex(ValueError, pattern):
                    self.mint()

    def test_a_member_of_another_condition_refuses_instead_of_a_majority_drop(self) -> None:
        self.identity[9] = ("c" * 64, True)
        with self.assertRaisesRegex(ValueError, "<corpus>=condition_differs"):
            self.drops()
        with self.assertRaisesRegex(ValueError, "condition_differs"):
            self.mint()

    def test_a_dropped_member_of_another_condition_does_not_split_the_corpus(self) -> None:
        self.identity[9] = ("c" * 64, True)
        self.energy_cause[9] = "precheck_ineligible"
        self.assertEqual(self.drops(), [{"bundle_id": "neg8-refcorpus-r09", "reason": "precheck_ineligible"}])
        self.assertEqual(len(self.mint()["reference_corpus"]["members"]), 11)


class MintPhysicalTimestampTests(_CorpusFixture, unittest.TestCase):
    def test_derived_at_is_the_latest_kept_member_span_end_not_the_minting_clock(self) -> None:
        self.energy_cause[12] = "precheck_ineligible"  # the latest member is dropped
        with patch.object(whole_window.time, "time", return_value=SPAN_BASE_S + 10 * 86400.0):
            artifact = self.mint()
        self.assertEqual(artifact["freshness"]["derived_at_s"], SPAN_BASE_S + 1100.0)
        # A desk re-mint a day later binds the identical artifact.
        with patch.object(whole_window.time, "time", return_value=SPAN_BASE_S + 11 * 86400.0):
            self.assertEqual(self.mint(), artifact)

    def test_members_without_a_readable_window_do_not_set_the_time(self) -> None:
        self.span_missing.update({11, 12})
        self.assertEqual(self.mint()["freshness"]["derived_at_s"], SPAN_BASE_S + 1000.0)


class ValidatorEndReferenceTimeTests(unittest.TestCase):
    """The validator re-derives the end-reference evaluation time on a HAZARD root."""

    def _decide(self, *, hazard: bool, stored: float) -> float:
        root = Path("/nonexistent-hazard-root")
        manifest = {"members": [
            {"execution": "invoked", "role": "neg8_daily_reference_end",
             "sentinel_position": None, "bundle_ids": [f"end-{index}"]}
            for index in range(3)]}
        paths = {f"end-{index}": root / f"end-{index}" for index in range(3)}
        seen: list[float] = []

        def observation(metadata, *, evaluated_at_s=None):
            seen.append(evaluated_at_s)
            return {"evaluated_at_s": evaluated_at_s}

        energy = ({"point_j": 1.0, "lower_j": 1.0, "upper_j": 1.0}, 1.0, None)
        with patch.object(whole_window.Neg8BracketPolicy, "from_mapping", return_value=object()), \
                patch.object(whole_window, "_manifest_bundle_paths", return_value=paths), \
                patch.object(whole_window, "_read_json_object", return_value={}), \
                patch.object(whole_window, "_custody_strict_invalid", return_value=False), \
                patch.object(whole_window, "_current_strict_summary", return_value=False), \
                patch.object(whole_window, "_reference_energy_evidence", return_value=energy), \
                patch.object(whole_window, "_measured_window_end_s", create=True,
                             side_effect=lambda path: 5000.0 + int(path.name[-1])), \
                patch.object(whole_window, "_is_hazard_runs_root", return_value=hazard), \
                patch.object(whole_window, "build_neg8_freshness_observation", side_effect=observation), \
                patch.object(whole_window, "evaluate_neg8_point_drift", return_value={"decision": "passed"}):
            whole_window._derived_neg8_decision(
                [manifest], root, {}, current=True, point_drift=True,
                freshness_evaluated_at_s=stored)
        self.assertEqual(len(seen), 1)
        return seen[0]

    def test_hazard_root_uses_the_last_end_reference_span_end(self) -> None:
        self.assertEqual(self._decide(hazard=True, stored=time.time()), 5002.0)

    def test_other_roots_keep_the_stored_evaluation_time(self) -> None:
        self.assertEqual(self._decide(hazard=False, stored=1234.0), 1234.0)


class EnergyCauseTests(unittest.TestCase):
    """``_reference_energy_evidence_detail`` names why the evidence failed."""

    def _detail(self, reduced: dict | Exception, stored: dict):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "b"
            bundle.mkdir()
            (bundle / "summary_metrics.json").write_text(json.dumps(stored) + "\n")

            class Reduced:
                def to_dict(self_inner):
                    return reduced

            def reduce_bundle(_path, **_kwargs):
                if isinstance(reduced, Exception):
                    raise reduced
                return Reduced()

            with patch.object(whole_window, "_current_strict_summary", return_value=True), \
                    patch("joulewise.reduce.reduce_bundle", side_effect=reduce_bundle):
                detail = whole_window._reference_energy_evidence_detail(bundle)
                three = whole_window._reference_energy_evidence(bundle)
        self.assertEqual(three, detail[:3])
        return detail

    @staticmethod
    def _summary(gross: float = 10.0, idle: float = 9.0, *, gross_ok=True, idle_ok=True,
                 status="succeeded") -> dict:
        return {
            "status": status,
            "gross_energy_j": gross,
            "idle_subtracted_energy_j": idle,
            "energy_anchor_shift_envelopes": {
                "/gross_energy_j": {"point_j": gross, "lower_j": gross - 1, "upper_j": gross + 1}},
            "window_evidence_precheck": {
                "gross_request": {"eligible": gross_ok},
                "idle_subtracted_request": {"eligible": idle_ok}},
        }

    def test_causes(self) -> None:
        stored = self._summary()
        cases = (
            (self._summary(), None, None),
            (self._summary(gross_ok=False), "provenance", "precheck_ineligible"),
            (self._summary(idle_ok=False), "provenance", "precheck_ineligible"),
            (self._summary(idle_ok=None), "provenance", "precheck_unknown"),
            ({**self._summary(), "window_evidence_precheck": {}}, "provenance", "precheck_absent"),
            (self._summary(status="failed"), "provenance", "reduction_mismatch"),
            (self._summary(gross=11.0), "conflict", "reduction_mismatch"),
            (self._summary(idle=8.5), "conflict", "reduction_mismatch"),
            ({**self._summary(), "idle_subtracted_energy_j": None}, "provenance", "reduction_incomplete"),
            (RuntimeError("reducer"), "provenance", "reduction_unavailable"),
        )
        for reduced, problem, cause in cases:
            with self.subTest(cause=cause, problem=problem):
                detail = self._detail(reduced, stored)
                self.assertEqual(detail[2:], (problem, cause))

    def test_a_stored_summary_without_its_number_is_a_mismatch(self) -> None:
        stored = {**self._summary(), "idle_subtracted_energy_j": None}
        self.assertEqual(self._detail(self._summary(), stored)[2:], ("conflict", "reduction_mismatch"))


if __name__ == "__main__":
    unittest.main()
