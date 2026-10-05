"""D6/D7 delta regressions using native refusal and admission records."""
from pathlib import Path
import shutil
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import night_gate, v5_qualification as q
from scripts import harvest_v5_g2b_window as harvest, run_night as driver
from tests import test_v5_block4_x7 as x7, test_v5_block4_x12a as x12a


class AdmissionRootsTests(unittest.TestCase):
    def check_member(self, *, bound, incomplete):
        fixture = x12a.AdmissionAssessmentTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        root = fixture.bound if bound else fixture.fixture.runs
        member = root / "earlier-failed-member"
        shutil.copytree(fixture.success, member)
        metadata = q.read(member / "metadata.json")
        metadata["run_id"] = member.name
        x7.put(member / "metadata.json", metadata)
        if incomplete:
            (member / "summary_metrics.json").unlink()
            cause = "attempt_bundle_incomplete"
        else:
            x7.put(member / "summary_metrics.json", {
                "status": "failed", "failure_message": "runtime failed outside admission"})
            (member / "events.jsonl").write_text(
                '{"event_type":"failure","phase":"inference","message":"runtime failed outside admission"}\n')
            cause = "member_failed_outside_idle_admission"
        record = fixture.harvest()
        self.assertEqual(record["verdict"], "RECOVER", record)
        self.assertEqual(record["cause_codes"], sorted([q.ADMISSION_ABORT_CODE, cause]))
        self.assertEqual(record["recovery_classification"], "admission_abort_with_other_recover_cause")
        self.assertTrue(record["end_state"])
        self.assertFalse(q.is_admission_abort(record))
        prior = q.reference(fixture.args.archive_root / "harvest.json")
        with self.assertRaisesRegex(q.HarvestRefusal, "fresh_s1_predecessor_not_rearmable"):
            q.attempt_history(x7.attempt("fresh", prior), fixture.plan.block_archive_root)

    def test_failed_bound_member_prevents_admission_rearm(self):
        self.check_member(bound=True, incomplete=False)

    def test_incomplete_bound_member_prevents_admission_rearm(self):
        self.check_member(bound=True, incomplete=True)

    def test_failed_runs_member_prevents_admission_rearm(self):
        self.check_member(bound=False, incomplete=False)

    def test_incomplete_runs_member_prevents_admission_rearm(self):
        self.check_member(bound=False, incomplete=True)


class NativeNullRefusalTests(unittest.TestCase):
    def setUp(self):
        self.fixture = x7.WriterHistoryTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        prior = self.fixture.prior("NULL")
        old = q.read(Path(prior["path"]))
        self.first_path = Path(old["plan"]["path"])
        mapping = q.read(self.first_path)
        gamma = self.root / "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"
        shutil.copytree(Path(mapping["pack_night"]["pack_root"]), gamma)
        mapping["pack_night"].update(pack_id=gamma.name, pack_root=str(gamma))
        x7.put(self.first_path, mapping)
        self.first_plan = night_gate.NightPlan.from_mapping(mapping)
        shutil.rmtree(Path(prior["path"]).parent)
        self.policies = {name: x7.put(self.root / (name + "-null.json"), {})
                         for name in ("policy", "acceptance")}
        self.arm = self.root / "null-arm"
        (self.arm / "runs").mkdir(parents=True)
        self.bound = self.root / "null-bound"
        self.bound.mkdir()

    def harvest_null(self, plan, path, code, *, refusal_plan=None):
        refusal_path = Path(plan.custody_root) / "night/refusal.json"
        refusal_path.parent.mkdir(parents=True, exist_ok=True)
        driver._write_driver_refusal(refusal_path, refusal_plan or plan, code,
                                     "independent native fixture refusal")
        inputs = self.root / (plan.plan_id + "-inputs.json")
        x7.put(inputs, {"schema": harvest.INPUT_SCHEMA, "occurrence": "s1",
            "plan": q.reference(path), "custody_root": str(self.arm),
            "bound_runs_root": str(self.bound), **self.policies})
        args = SimpleNamespace(inputs=inputs, inputs_sha256=q.sha(inputs),
            archive_root=Path(plan.block_archive_root) / "attempts" / plan.plan_id,
            scratch_root=self.root, prepare_desk=False, previous_harvest=None)
        with mock.patch.object(q, "load_plan", return_value=plan):
            result = harvest.harvest(args, clear=lambda *a, **kw: True)
        return result, q.reference(args.archive_root / "harvest.json")

    def two_nulls(self, codes):
        previous = {"none": True}
        for index, code in enumerate(codes):
            if index == 0:
                plan, path = self.first_plan, self.first_path
            else:
                path = self.root / "prior-2/night_plan.json"
                chain = self.root / "prior-2-chain.zsh"
                chain.write_text("export V5_QUALIFICATION_OCCURRENCE=s1\nexit 0\n")
                plan = x7.bind_history_fixture(path, SimpleNamespace(plan_id="prior-2",
                    custody_root=str(path.parent), chain_path=str(chain),
                    chain_sha256_path=str(chain) + ".sha256", pack_night=self.first_plan.pack_night),
                    Path(self.first_plan.block_archive_root), previous=previous)
            result, previous = self.harvest_null(plan, path, code)
            self.assertEqual(result["verdict"], "NULL", result)
            self.assertIn(code, result["cause_codes"])
            self.assertEqual(result["native_refusal_codes"], [code])
            self.assertEqual(result["native_refusals"], [q.reference(Path(plan.custody_root) / "night/refusal.json")])
            archived = Path(previous["path"]).parent / "withheld/sources/night-custody/night/refusal.json"
            self.assertEqual(q.sha(archived), result["native_refusals"][0]["sha256"])
        self.fixture.fixture.input["previous_attempt"] = previous
        return self.fixture.fixture, result

    def test_distinct_native_refusals_allow_third_writer(self):
        fixture, record = self.two_nulls(["night_probe_error", "night_chain_digest_mismatch"])
        self.assertFalse(record["attempt_history"]["same_refusal_twice"])
        fixture.write()
        self.assertTrue((fixture.custody / "authorization_record.json").is_file())
        self.assertEqual(q.read(fixture.output)["previous_attempt"], fixture.input["previous_attempt"])

    def test_identical_native_refusals_block_third_writer(self):
        fixture, record = self.two_nulls(["night_probe_error", "night_probe_error"])
        self.assertTrue(record["attempt_history"]["same_refusal_twice"])
        with self.assertRaisesRegex(q.HarvestRefusal, "same_refusal_twice") as refusal:
            fixture.write()
        self.assertEqual(refusal.exception.refusal_codes, ["night_probe_error"])
        self.assertFalse((fixture.custody / "authorization_record.json").exists())
        self.assertFalse(fixture.output.exists())

    def test_foreign_plan_refusal_is_not_a_native_null_cause(self):
        from dataclasses import replace
        result, _ = self.harvest_null(self.first_plan, self.first_path, "night_probe_error",
            refusal_plan=replace(self.first_plan, plan_id="foreign-plan"))
        self.assertEqual(result["verdict"], "REFUSED")
        self.assertEqual(result["cause_codes"], ["native_refusal_identity_mismatch"])


class NullComparisonTests(unittest.TestCase):
    def test_native_codes_take_precedence_over_generic_harvest_causes(self):
        fixture = x7.AttemptHistoryTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        first = fixture.save(x7.attempt("first", {"none": True},
            native_refusal_codes=["night_probe_error"]))
        second = fixture.save(x7.attempt("second", first,
            native_refusal_codes=["night_chain_digest_mismatch"]))
        proof = fixture.history(x7.attempt("third", second, verdict="REFUSED"))
        self.assertFalse(proof["same_refusal_twice"])


if __name__ == "__main__":
    unittest.main()
