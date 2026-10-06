"""HAZARD_PACK whole-window verdict: lineage (B1) and membership (B9).

A block-5 window collects tagged science members (stamped with the hazard
lineage) next to untagged NEG-8 references, untagged calibration captures and
an untagged NEG-8 reference corpus in the bound runs root.  The ARM-path rules
refused every such window: ``run_campaign --whole-window-verdict`` exited 2
(``launch_lineage_conflict`` / ``launch_consumption_missing``), and the
membership grouping by analysis-manifest identity left the window unresolved.

What is real here: the measurement code (bundle writer and controller through
mock adapters, the calibration ledger, the hazard lineage publication), the
verdict writer ``run_campaign --whole-window-verdict`` (membership, member
strict validation, evaluation basis, log append, verdict publication) and the
row validator's lineage replay.  What is faked: the idle-admission core (its
numbers need real telemetry), so it is replaced by a core that carries a
formed calibration bracket; and the calibration snapshot/binding loaders it
would have consumed.  The ARM replay chain is a sentinel throughout.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from joulewise import arm_readiness, controller, whole_window, window_lineage
from joulewise.clock import FakeClock
from joulewise.schemas import BenchmarkConfig, CampaignPolicy
from scripts import run_campaign
from tests.test_window_lineage import (
    _MockWorkloadRegistry,
    POST_ATTEMPT,
    PRE_ATTEMPT,
    ROOT,
    SESSION_ID,
    _member_config,
    _SentinelMixin,
    build_window,
    remove_night_records,
    run_member,
    write_night_records,
)

POLICY = ROOT / "configs/campaign_policies/quiet_mac_exploratory.json"
POLICY_SHA = hashlib.sha256(POLICY.read_bytes()).hexdigest()
GAMMA_ANALYSIS_ID = "am-568cd8f3daee4a73017874bc24b5af1658caa8f5d7aa46a468a40277fb852b37"


def run_untagged(w, run_id: str) -> Path:
    """An untagged member (a daily reference) in the claim root, no stamp.

    Collected without the Revision-5 pre-slot attachment, which only plan-
    pinned auxiliary configs may carry; the lineage path does not read it.
    """

    config = _member_config(run_id, tagged=False)
    policy = CampaignPolicy.from_mapping(json.loads(
        (ROOT / "configs/campaign_policies/quiet_mac_exploratory.json").read_bytes()))
    policy = replace(policy, idle_admission=replace(policy.idle_admission, enabled=False))
    with patch.object(sys, "argv", ["joulewise", "run", str(w.plain_path)]), \
            patch.dict(os.environ, {}, clear=True):
        bundle, _summary = controller.run_benchmark(
            config, w.claim, FakeClock(start=1700000000), registry=_MockWorkloadRegistry(),
            environment_snapshot=None, campaign_policy=policy,
            campaign_environment_preflight={"snapshot": {
                "power_source": "AC Power", "power": {"external_connected": True},
                "low_power_mode": False}})
    return bundle


def _manifest_member(bundle: Path, *, role: str | None, position: str | None) -> dict:
    return {
        "config": f"{bundle.name}.json",
        "run_id": bundle.name,
        "execution": "invoked",
        "bundle_ids": [bundle.name],
        "role": role,
        "sentinel_position": position,
        "canonical_neg8_workload": position is not None,
    }


class HazardWholeWindowVerdictTests(_SentinelMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        cls.addClassCleanup(cls._start_sentinels().close)
        w = cls.w = build_window(Path(tmp.name))
        cls.lineage = w.lineage
        # One tagged science member and two untagged daily references, all in
        # the claim runs root, collected by the real controller.
        cls.science, _ = run_member(w, w.member_path)
        cls.ref_start = run_untagged(w, "hazard-ref-start")
        cls.ref_end = run_untagged(w, "hazard-ref-end")
        cls.members = (cls.science, cls.ref_start, cls.ref_end)
        assert len({path.name for path in cls.members}) == 3, cls.members
        # The post capture: the same real Revision-5 evidence under the
        # post attempt (a stand-in for the second capture of the session).
        cls.post_capture = w.claim / "instrument_validation" / POST_ATTEMPT
        shutil.copytree(w.capture, cls.post_capture)
        # The untagged 12-member NEG-8 reference corpus in the bound root.
        cls.corpus = []
        for index in range(1, 13):
            bundle = w.bound / f"neg8-refcorpus-r{index:02d}"
            bundle.mkdir()
            (bundle / "config.json").write_text(json.dumps({"run_id": bundle.name}) + "\n")
            (bundle / "summary_metrics.json").write_text(
                json.dumps({"status": "succeeded", "index": index}) + "\n")
            (bundle / "telemetry").mkdir()
            (bundle / "telemetry/samples.jsonl").write_text(f'{{"w": {index}}}\n')
            cls.corpus.append(bundle)

    def setUp(self) -> None:
        self.w = type(self).w
        self.addCleanup(remove_night_records, self.w)
        self.addCleanup(self._reset_claim_records)
        write_night_records(self.w)

    def tearDown(self) -> None:
        self.assertEqual(type(self).sentinel_calls, [], "a hazard path reached the ARM replay")

    def _reset_claim_records(self) -> None:
        claim = self.w.claim
        shutil.rmtree(claim / "campaign_manifests", ignore_errors=True)
        for name in ("campaign_log.jsonl", "whole-window-verdict.json", ".campaign.lock"):
            (claim / name).unlink(missing_ok=True)

    # -- fixtures ------------------------------------------------------------

    def _bracket(self, *, session: str = SESSION_ID, pre: str = PRE_ATTEMPT,
                 post: str = POST_ATTEMPT) -> dict:
        """A formed bracket as the evaluator records it (descriptor fields)."""

        bracket: dict = {}
        for role, attempt, path in (("pre", pre, self.w.capture), ("post", post, self.post_capture)):
            raw = (path / "instrument_evidence.json").read_bytes()
            bracket[role] = {
                "relative_path": str(path),
                "evidence_sha256": hashlib.sha256(raw).hexdigest(),
                "attempt_id": attempt,
                "bracket_session_id": session,
                "bracket_slot": role,
                "bracket_window_id": self.lineage["window_id"],
                "bracket_plan_id": self.lineage["plan_id"],
                "bracket_runs_root": str(self.w.claim),
            }
        return bracket

    def _bound(self, count: int, *, lineage: dict | None = None) -> dict:
        members = [
            {
                "bundle_id": bundle.name,
                "point_gross_j": 38.0 + index,
                "point_idle_subtracted_j": 36.0 + index,
                "bundle_evidence_sha256": whole_window._bundle_evidence_sha256(bundle),
            }
            for index, bundle in enumerate(self.corpus[:count])
        ]
        artifact = {
            "schema_version": "joulewise.neg8_drift_bound.v1",
            "reference_corpus": {"corpus_id": "fixture-corpus", "members": members,
                                 "member_ids": [row["bundle_id"] for row in members]},
        }
        if lineage is not None:
            artifact["launch_lineage"] = lineage
        return artifact

    def _write_manifests(self, layout: str) -> None:
        """ALPHA/BETA: every stage records a null analysis-manifest identity.
        GAMMA: the science stage records the contrast's identity; references null."""

        directory = self.w.claim / "campaign_manifests"
        directory.mkdir(exist_ok=True)
        science_identity = GAMMA_ANALYSIS_ID if layout == "gamma" else None
        stages = (
            ("00-start.json", None, [_manifest_member(
                self.ref_start, role=run_campaign.NEG8_REFERENCE_START_ROLE, position="start")]),
            ("01-science.json", science_identity, [_manifest_member(
                self.science, role="comparative_contrast_member", position=None)]),
            ("02-end.json", None, [_manifest_member(
                self.ref_end, role=run_campaign.NEG8_REFERENCE_END_ROLE, position="end")]),
        )
        for name, identity, members in stages:
            (directory / name).write_text(json.dumps({
                "schema_version": "joulewise.campaign_provenance.v1",
                "analysis_manifest_id": identity,
                "campaign_policy": {"sha256": POLICY_SHA},
                "members": members,
            }) + "\n")

    def _core(self, bound: dict | None = None) -> run_campaign._IdleAdmissionCoreEvaluation:
        return run_campaign._IdleAdmissionCoreEvaluation(
            core={
                "schema_version": run_campaign.IDLE_ADMISSION_CORE_SCHEMA,
                "policy_sha256": POLICY_SHA,
                "conditions": [],
                "members": [],
                "adapter_wattage_continuity": {"decision": "stable"},
                "neg8_bracket": {"decision": "passed", "drift_bound_artifact": bound},
                "instrument_calibration_bracket": self._bracket(),
            },
            member_failures=(),
        )

    def _write_verdict(self, layout: str) -> tuple[int, str, dict | None]:
        self._write_manifests(layout)
        claim = self.w.claim
        output = claim / "whole-window-verdict.json"
        argv = ["--whole-window-verdict", "--runs-dir", str(claim),
                "--log", str(claim / "campaign_log.jsonl"), "--campaign-policy", str(POLICY),
                "--whole-window-verdict-output", str(output)]
        out, err = io.StringIO(), io.StringIO()
        with patch.object(run_campaign, "_idle_admission_core_evaluation",
                          return_value=self._core()), \
                patch.object(run_campaign, "_load_calibration_snapshot_for_evaluation",
                             return_value=None), \
                patch.object(run_campaign, "_validated_bracket_binding_input",
                             return_value=(None, None)), \
                redirect_stdout(out), redirect_stderr(err):
            code = run_campaign.main(argv)
        row = json.loads(output.read_bytes()) if output.is_file() else None
        return code, out.getvalue() + err.getvalue(), row

    # -- B1: members ---------------------------------------------------------

    def test_mixed_tagged_and_untagged_members_share_the_window_lineage(self) -> None:
        self.assertEqual(whole_window._authenticated_bundle_launch_lineage_set(
            list(self.members), require_completion=True), self.lineage)
        self.assertEqual(whole_window.launch_lineage_refusal_reasons(
            self.w.claim, {path.name for path in self.members}, require_completion=True), ())

    def test_untagged_member_outside_the_stamped_root_is_refused(self) -> None:
        stray = self.w.base / "elsewhere" / self.ref_end.name
        shutil.copytree(self.ref_end, stray)
        self.addCleanup(shutil.rmtree, stray.parent, True)
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            whole_window._authenticated_bundle_launch_lineage_set(
                [self.science, self.ref_start, stray], require_completion=True)
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    def test_completion_is_still_required(self) -> None:
        remove_night_records(self.w)
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            whole_window._authenticated_bundle_launch_lineage_set(
                list(self.members), require_completion=True)
        self.assertEqual(caught.exception.reason_code, "launch_lifecycle_incomplete")

    # -- B1: calibration captures --------------------------------------------

    def test_science_only_window_binds_captures_through_the_ledger_session(self) -> None:
        self.assertEqual(whole_window._authenticated_bundle_launch_lineage_set(
            [self.science], require_completion=True), self.lineage)
        self.assertEqual(whole_window._authenticate_whole_window_launch_sources(
            copy.deepcopy(self.lineage), calibration_bracket=self._bracket(),
            drift_bound_artifact=None, require_completion=True, require_bound=True), self.lineage)

    def test_foreign_capture_or_tampered_evidence_is_refused(self) -> None:
        cases = (
            (self._bracket(session="foreign-session"), "launch_binding_mismatch"),
            (self._bracket(pre=POST_ATTEMPT), "launch_binding_mismatch"),
            (self._bracket(post=PRE_ATTEMPT), "launch_binding_mismatch"),
        )
        tampered = self._bracket()
        tampered["post"]["evidence_sha256"] = "0" * 64
        for bracket, reason in (*cases, (tampered, "launch_consumption_invalid")):
            with self.subTest(bracket=bracket), \
                    self.assertRaises(arm_readiness.LaunchLineageError) as caught:
                whole_window._authenticate_whole_window_launch_sources(
                    copy.deepcopy(self.lineage), calibration_bracket=bracket,
                    drift_bound_artifact=None, require_completion=True, require_bound=True)
            self.assertEqual(caught.exception.reason_code, reason)

    # -- B1: the NEG-8 bound -------------------------------------------------

    def test_untagged_corpus_bound_of_ten_to_twelve_members_binds_to_the_bound_root(self) -> None:
        for count in (10, 11, 12):
            with self.subTest(members=count):
                self.assertEqual(whole_window._authenticate_whole_window_launch_sources(
                    copy.deepcopy(self.lineage), calibration_bracket=self._bracket(),
                    drift_bound_artifact=self._bound(count),
                    require_completion=True, require_bound=True), self.lineage)

    def test_corpus_member_bytes_or_presence_mismatch_is_refused(self) -> None:
        bound = self._bound(11)
        target = self.corpus[4] / "telemetry/samples.jsonl"
        original = target.read_bytes()
        self.addCleanup(target.write_bytes, original)
        target.write_bytes(original + b'{"w": 0}\n')
        missing = copy.deepcopy(self._bound(10))
        missing["reference_corpus"]["members"][0]["bundle_id"] = "neg8-refcorpus-r99"
        for artifact in (bound, missing):
            with self.subTest(), self.assertRaises(arm_readiness.LaunchLineageError) as caught:
                whole_window._authenticate_whole_window_launch_sources(
                    copy.deepcopy(self.lineage), calibration_bracket=self._bracket(),
                    drift_bound_artifact=artifact, require_completion=True, require_bound=True)
            self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    def test_stamped_bound_must_carry_the_window_lineage(self) -> None:
        self.assertEqual(whole_window._authenticate_whole_window_launch_sources(
            copy.deepcopy(self.lineage), calibration_bracket=self._bracket(),
            drift_bound_artifact=self._bound(12, lineage=copy.deepcopy(self.lineage)),
            require_completion=True, require_bound=True), self.lineage)
        foreign = copy.deepcopy(self.lineage)
        foreign["window_id"] = "another-window"
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            whole_window._authenticate_whole_window_launch_sources(
                copy.deepcopy(self.lineage), calibration_bracket=self._bracket(),
                drift_bound_artifact=self._bound(12, lineage=foreign),
                require_completion=True, require_bound=True)
        self.assertEqual(caught.exception.reason_code, "launch_lineage_conflict")

    # -- B9: membership --------------------------------------------------------

    def test_membership_resolves_alpha_beta_and_gamma_hazard_roots(self) -> None:
        expected = sorted(path.name for path in self.members)
        for layout in ("alpha", "gamma"):
            with self.subTest(layout=layout):
                self._reset_claim_records()
                self._write_manifests(layout)
                resolution = run_campaign._whole_window_campaign_membership(
                    self.w.claim, POLICY_SHA)
                self.assertEqual(resolution.conditions, ())
                self.assertEqual(sorted(source.path.name for source in resolution.sources), expected)
                catalog = run_campaign.load_authenticated_campaign_catalog(self.w.claim)
                self.assertEqual(resolution.membership_id, run_campaign.whole_window_membership_id([
                    run_campaign._membership_manifest_descriptor(self.w.claim, record)
                    for record in catalog]))
                self.assertIsNone(resolution.membership_binding)

    def test_a_root_without_a_hazard_locator_keeps_the_old_grouping(self) -> None:
        # The same manifests in a root with no hazard locator: the null group
        # still needs its binding artifact, exactly as before.
        plain = self.w.base / "plain-root"
        self.addCleanup(shutil.rmtree, plain, True)
        self._write_manifests("alpha")
        shutil.copytree(self.w.claim, plain, ignore=shutil.ignore_patterns(
            window_lineage.LOCATOR_BASENAME, "instrument_validation"))
        resolution = run_campaign._whole_window_campaign_membership(plain, POLICY_SHA)
        self.assertEqual(resolution.conditions[0], "whole_window_campaign_membership_unresolved")

    # -- B1 + B9 through the verdict writer and the row validator --------------

    def test_verdict_writer_and_validator_on_a_formed_bracket(self) -> None:
        for layout in ("alpha", "gamma"):
            with self.subTest(layout=layout):
                self._reset_claim_records()
                code, transcript, row = self._write_verdict(layout)
                self.assertIn(code, (0, 1), transcript)
                self.assertIsNotNone(row, transcript)
                self.assertEqual(sorted(row["bundle_ids"]), sorted(path.name for path in self.members))
                self.assertNotIn("whole_window_campaign_membership_unresolved",
                                 row["idle_admission_core"]["conditions"])
                self.assertEqual(row["evaluation_basis"]["launch_lineage"], self.lineage)
                self.assertIsNone(row["window_membership"]["binding"])
                self.assertEqual(
                    whole_window._whole_window_row_launch_refusal_reasons(row, self.w.claim), ())
                self.assertEqual(whole_window.authenticate_window_launch_lineage(
                    self.w.claim, set(row["bundle_ids"])), self.lineage)

    def test_validator_replays_an_eleven_member_untagged_bound(self) -> None:
        _code, transcript, row = self._write_verdict("alpha")
        self.assertIsNotNone(row, transcript)
        row = copy.deepcopy(row)
        row["idle_admission_core"]["neg8_bracket"]["drift_bound_artifact"] = self._bound(11)
        self.assertEqual(whole_window._whole_window_row_launch_refusal_reasons(row, self.w.claim), ())
        row["idle_admission_core"]["neg8_bracket"]["drift_bound_artifact"]["reference_corpus"][
            "members"][3]["bundle_evidence_sha256"] = "0" * 64
        self.assertEqual(whole_window._whole_window_row_launch_refusal_reasons(row, self.w.claim),
                         ("launch_binding_mismatch",))

    # -- Sol consult F3, F5, F6 ------------------------------------------------

    def test_validator_requires_the_complete_hazard_catalog(self) -> None:
        _code, transcript, row = self._write_verdict("gamma")
        self.assertIsNotNone(row, transcript)
        self.assertEqual(whole_window._hazard_membership_replay_reasons(
            row, self.w.claim, POLICY_SHA), set())
        late = self.w.claim / "campaign_manifests" / "03-late.json"
        late.write_text(json.dumps({
            "schema_version": "joulewise.campaign_provenance.v1", "analysis_manifest_id": None,
            "campaign_policy": {"sha256": POLICY_SHA},
            "members": [_manifest_member(self.science, role=None, position=None)]}) + "\n")
        self.assertEqual(whole_window._hazard_membership_replay_reasons(
            row, self.w.claim, POLICY_SHA), {"whole_window_verdict_provenance_invalid"})

    def test_unstamped_member_must_have_a_readable_untagged_config(self) -> None:
        copy_path = self.w.claim / "science-unreadable-config"
        shutil.copytree(self.science, copy_path)
        self.addCleanup(shutil.rmtree, copy_path, True)
        (copy_path / "config.json").write_text("{not json\n")
        with self.assertRaises(arm_readiness.LaunchLineageError) as caught:
            whole_window._authenticated_bundle_launch_lineage_set(
                [self.science, copy_path], require_completion=True)
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    def test_relocated_bound_root_is_read_through_relocated_custody(self) -> None:
        bound = self._bound(11)
        moved = self.w.base / "archive" / self.w.bound.name
        shutil.copytree(self.w.bound, moved)
        away = self.w.bound.with_name(self.w.bound.name + ".away")
        self.w.bound.rename(away)
        self.addCleanup(shutil.rmtree, moved.parent, True)
        self.addCleanup(away.rename, self.w.bound)

        def check():
            return whole_window._authenticate_whole_window_launch_sources(
                copy.deepcopy(self.lineage), calibration_bracket=self._bracket(),
                drift_bound_artifact=bound, require_completion=True, require_bound=True)

        with self.assertRaises(arm_readiness.LaunchLineageError):
            check()
        with window_lineage.relocated_custody({self.w.bound: moved}):
            self.assertEqual(check(), self.lineage)


class HazardNeg8MintTests(_SentinelMixin, unittest.TestCase):
    """A3 (core) and B1's reach into the NEG-8 mint, on a hazard bound root."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.addCleanup(self._start_sentinels().close)
        self.w = build_window(Path(tmp.name))
        self.lineage = self.w.lineage
        self.members = []
        for index in range(1, 13):
            bundle = self.w.bound / f"neg8-refcorpus-r{index:02d}"
            bundle.mkdir()
            (bundle / "config.json").write_text(json.dumps({"run_id": bundle.name}) + "\n")
            (bundle / "metadata.json").write_text("{}\n")
            (bundle / "summary_metrics.json").write_text(
                json.dumps({"index": index, "status": "succeeded"}) + "\n")
            self.members.append({"bundle_id": bundle.name, "bundle_path": bundle.name})
        self.manifest = self.w.bound / "neg8-corpus.collected.json"
        self.manifest.write_text(json.dumps({
            "schema_version": "joulewise.neg8_reference_corpus.v1", "corpus_id": "hazard-corpus",
            "freeze_status": "settled_reference", "condition_id": "df-rq-mid",
            "members": self.members}, indent=2, sort_keys=True) + "\n")
        self.not_strict: set[str] = set()
        self.calibration: dict[str, str] = {}
        self.os_build: dict[str, str | None] = {}

    def _patches(self) -> ExitStack:
        def strict(summary, _path):
            return summary.get("index") is not None and f"r{summary['index']:02d}" not in self.not_strict

        def energy(path: Path, **_kwargs):
            value = 10.0 + float(path.name.rsplit("r", 1)[1])
            return {"point_j": value, "lower_j": value, "upper_j": value}, value - 1.0, None, None

        def span_end(path: Path):
            return 1_800_000_000.0 + float(path.name.rsplit("r", 1)[1])

        def fields(metadata):
            name = metadata.get("_name") if isinstance(metadata, dict) else None
            return {"os_build": self.os_build.get(name, "25G83"),
                    "power_supply_identity_sha256": "e" * 64,
                    "calibration_identity_sha256": self.calibration.get(name, "f" * 64)}

        real_read = whole_window._read_json_object

        def read(path: Path):
            value = real_read(path)
            if path.name == "metadata.json" and isinstance(value, dict):
                value = {**value, "_name": f"r{path.parent.name.rsplit('r', 1)[1]}"}
            return value

        stack = ExitStack()
        for target, kwargs in (
            ("_custody_strict_invalid", {"return_value": False}),
            ("_current_strict_summary", {"side_effect": strict}),
            ("_scientific_config_identity", {"return_value": ("d" * 64, True)}),
            ("_reference_energy_evidence", {"side_effect": lambda path, **kw: energy(path)[:3]}),
            ("_reference_energy_evidence_detail", {"side_effect": energy}),
            ("_measured_window_end_s", {"side_effect": span_end}),
            ("neg8_freshness_binding_fields", {"side_effect": fields}),
            ("_read_json_object", {"side_effect": read}),
        ):
            stack.enter_context(patch.object(whole_window, target, **kwargs))
        return stack

    def test_failing_member_is_dropped_and_the_bound_binds_the_pruned_manifest(self) -> None:
        self.not_strict = {"r03"}
        self.os_build = {"r05": "25G99", "r06": None}
        with self._patches():
            artifact = whole_window.mint_neg8_drift_bound_artifact(self.w.bound, self.manifest)
            drops = whole_window.neg8_corpus_mint_drops(self.w.bound, self.manifest)
        self.assertEqual(drops, [{"bundle_id": "neg8-refcorpus-r03", "reason": "not_current_strict_mint"}])
        corpus = artifact["reference_corpus"]
        self.assertEqual(len(corpus["members"]), 11)
        self.assertNotIn("neg8-refcorpus-r03", corpus["member_ids"])
        pruned = json.loads(self.manifest.read_bytes())
        pruned["members"] = [m for m in pruned["members"] if m["bundle_id"] != "neg8-refcorpus-r03"]
        pruned_raw = (json.dumps(pruned, indent=2, sort_keys=True) + "\n").encode()
        self.assertEqual(corpus["manifest_sha256"], hashlib.sha256(pruned_raw).hexdigest())
        self.assertEqual(artifact["freshness"]["bindings"]["os_build"], "25G83")
        self.assertNotIn("launch_lineage", artifact)
        self.assertTrue(whole_window.validate_neg8_drift_bound_artifact(
            artifact, reference_corpus_bytes=pruned_raw, require_corpus_identity=True))

    def test_mixed_stamped_and_unstamped_corpus_carries_the_window_lineage(self) -> None:
        first = self.w.bound / "neg8-refcorpus-r01"
        (first / "config.json").write_text(json.dumps(
            {"run_id": first.name, "run_metadata": {"tags": ["launch_lineage_required"]}}) + "\n")
        (first / "metadata.json").write_text(json.dumps({"extra": {"launch_lineage": self.lineage}}) + "\n")
        with self._patches():
            artifact = whole_window.mint_neg8_drift_bound_artifact(self.w.bound, self.manifest)
        self.assertEqual(artifact["launch_lineage"], self.lineage)
        self.assertEqual(len(artifact["reference_corpus"]["members"]), 12)
        self.assertTrue(whole_window.validate_neg8_drift_bound_artifact(artifact))

    def test_calibration_conflict_or_too_few_members_still_raise(self) -> None:
        for name, setup, pattern in (
            ("calibration", lambda: self.calibration.update({"r07": "a" * 64}), "calibration identity"),
            ("minimum", lambda: self.not_strict.update({"r01", "r02", "r03"}), "keeps 9 members"),
        ):
            with self.subTest(name), self._patches():
                self.not_strict, self.calibration = set(), {}
                setup()
                with self.assertRaisesRegex(ValueError, pattern):
                    whole_window.mint_neg8_drift_bound_artifact(self.w.bound, self.manifest)

    def test_a_root_without_a_hazard_locator_keeps_the_all_or_nothing_mint(self) -> None:
        (self.w.bound / window_lineage.LOCATOR_BASENAME).rename(self.w.base / "bound-locator.away")
        self.not_strict = {"r03"}
        with self._patches(), \
                patch.object(whole_window, "neg8_freshness_bindings_from_metadata",
                             return_value={"os_build": "25G83", "power_supply_identity_sha256": "e" * 64,
                                           "calibration_identity_sha256": "f" * 64}), \
                self.assertRaisesRegex(ValueError, "not a current strict mint"):
            whole_window.mint_neg8_drift_bound_artifact(self.w.bound, self.manifest)


if __name__ == "__main__":
    unittest.main()
