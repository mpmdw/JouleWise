"""Fixture-only qualification authoring; these checks discharge no live gate."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace
import subprocess
import tempfile
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, night_gate
from joulewise.night_plan_writer import night_plan_mapping, write_night_plan
from scripts import write_v5_qualification_plan as writer
from tests.test_arm_readiness_schemas import arm_context


class SizingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=tempfile.gettempdir())
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        source = self.root / "reviewed-estimate.json"
        source.write_text('{"basis":"prospective fixture only","diagnostic_anchor_half_width_s":0.001,"stamp_resolution_s":1e-9,"rho_per_s":1e-6}\n')
        self.source = writer.locator(source)
        self.roster = [{"run_id": name} for name in ("a1", "b1", "b2", "a2")]
        self.aux = ["neg8", "start", "midpoint", "end"]
        self.brackets = ["calibration-pre", "calibration-post"]
        self.sizing = {
            "fixed": {name: self.allow(100) for name in writer.FIXED_COMPONENTS["s1"]},
            "members": {r["run_id"]: {name: self.allow(10) for name in writer.MEMBER_COMPONENTS} for r in self.roster},
            "auxiliary": {name: self.allow(30) for name in self.aux},
            "streams": {name: self.allow(100) for name in [*(r["run_id"] for r in self.roster), *self.aux, *self.brackets]},
            "clock": {"diagnostic_anchor_half_width_s": 0.001, "stamp_resolution_s": 1e-9,
                      "rho_per_s": 1e-6, "source": self.source,
                      "observed_max_effective_bound": self.allow(0.004)},
        }

    def allow(self, seconds):
        path = self.root / f"allowance-{seconds}.json"
        path.write_bytes(readiness.render_json({"seconds": seconds, "basis": "prospective fixture only"}))
        return {"seconds": seconds, "source": writer.locator(path), "source_pointer": "/seconds"}

    def size(self, sizing=None):
        return writer.size_window("s1", sizing or self.sizing, roster=self.roster, auxiliary=self.aux, brackets=self.brackets)

    def test_components_count_once_and_window_has_single_dwell_cap(self):
        sized = self.size()
        self.assertEqual(5 * 100 + 4 * 6 * 10 + 4 * 30, sized["programmed_span_s"])
        self.assertEqual(3600, sized["window_max_s"])
        self.assertEqual(2700, sized["clean_dwell_cap_s"])

    def test_load_and_admission_sensitivity_kills_omission(self):
        before = self.size()["programmed_span_s"]
        for term in ("load", "idle_admission"):
            with self.subTest(term=term):
                changed = copy.deepcopy(self.sizing)
                changed["members"]["a1"][term] = self.allow(17)
                self.assertEqual(before + 7, self.size(changed)["programmed_span_s"])
                del changed["members"]["a1"][term]
                with self.assertRaisesRegex(ValueError, "member_components"):
                    self.size(changed)

    def test_missing_auxiliary_and_fixed_component_refused(self):
        for group, term in (("auxiliary", "neg8"), ("fixed", "stage_custody")):
            with self.subTest(term=term):
                changed = copy.deepcopy(self.sizing)
                del changed[group][term]
                with self.assertRaises(ValueError):
                    self.size(changed)
        before = self.size()["programmed_span_s"]
        changed = copy.deepcopy(self.sizing)
        changed["auxiliary"]["neg8"] = self.allow(41)
        self.assertEqual(before + 11, self.size(changed)["programmed_span_s"])

    def test_longest_auxiliary_stream_and_clock_violation(self):
        changed = copy.deepcopy(self.sizing)
        changed["streams"]["neg8"] = self.allow(5000)
        self.assertGreater(self.size(changed)["worst_case_effective_clock_bound_s"], 0.005)
        changed["clock"]["observed_max_effective_bound"] = self.allow(0.005000001)
        with self.assertRaisesRegex(ValueError, "clock_bound_exceeded"):
            self.size(changed)

    def test_bracket_streams_required_and_clock_checked_without_span_double_count(self):
        before = self.size()["programmed_span_s"]
        changed = copy.deepcopy(self.sizing)
        changed["streams"]["calibration-post"] = self.allow(200)
        self.assertEqual(before, self.size(changed)["programmed_span_s"])
        self.assertEqual(200, self.size(changed)["longest_sampler_stream_s"])
        changed["streams"]["calibration-post"] = self.allow(5000)
        self.assertGreater(self.size(changed)["worst_case_effective_clock_bound_s"], 0.005)
        del changed["streams"]["calibration-post"]
        with self.assertRaisesRegex(ValueError, "stream_inventory"):
            self.size(changed)

    def test_stream_must_cover_admission_guards_and_retry(self):
        changed = copy.deepcopy(self.sizing)
        changed["members"]["a1"]["idle_admission"] = self.allow(150)
        with self.assertRaisesRegex(ValueError, "stream_omits_guard_or_retry"):
            self.size(changed)

    def test_bound_derivation_counts_in_span_without_inventing_a_sampler(self):
        changed = copy.deepcopy(self.sizing)
        changed["auxiliary"]["bound-derivation"] = self.allow(7000)
        sized = writer.size_window("s1", changed, roster=self.roster,
            auxiliary=[*self.aux, "bound-derivation"], brackets=self.brackets, nonsampling=["bound-derivation"])
        self.assertEqual(self.size()["programmed_span_s"] + 7000, sized["programmed_span_s"])
        self.assertEqual(100, sized["longest_sampler_stream_s"])

    def test_effective_bound_prices_span_once_including_resolution(self):
        sized = self.size()
        from joulewise.uncertainty_evidence import NUMERIC_PADDING_S
        self.assertAlmostEqual(0.001 + 1e-9 + NUMERIC_PADDING_S + 1e-6 * 100,
                               sized["worst_case_effective_clock_bound_s"], places=15)
        self.assertEqual(self.sizing["clock"], sized["clock"])
        self.assertEqual(NUMERIC_PADDING_S, sized["numeric_padding_s"])

    def test_observed_clock_source_and_exact_five_ms_gate(self):
        for value, passes in ((0.005, True), (0.005000001, False)):
            changed = copy.deepcopy(self.sizing)
            changed["clock"]["observed_max_effective_bound"] = self.allow(value)
            if passes:
                self.assertEqual(value, self.size(changed)["observed_max_effective_clock_bound_s"])
            else:
                with self.assertRaisesRegex(ValueError, "clock_bound_exceeded"):
                    self.size(changed)
        changed["clock"]["observed_max_effective_bound"]["source"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            self.size(changed)

    def test_durable_adapter_keeps_all_allowances_without_tmp_sources(self):
        import hashlib
        adapter = json.loads((writer.REPO_ROOT / "configs/campaigns/v5_qualification_25g83/sizing_allowances.json").read_bytes())
        self.assertEqual(adapter["schema_version"], "joulewise.v5_qualification_sizing_allowances.v1")
        items = []
        def visit(value):
            if isinstance(value, dict):
                if "seconds" in value:
                    self.assertEqual(set(value), {"seconds", "source", "source_pointer"})
                    self.assertFalse(value["source"]["path"].startswith(("/tmp/", "/private/tmp/")))
                    items.append(value)
                else:
                    for child in value.values():
                        visit(child)
        visit(adapter)
        self.assertEqual(len(items), 60)  # 44 sizing terms, observed clock max, 8 totals, 7 controls.
        for item in items:
            path = Path(item["source"]["path"])
            if not path.is_absolute():
                raw = (writer.REPO_ROOT / path).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), item["source"]["sha256"])
                self.assertEqual(writer.allowance(item), item["seconds"])
        self.assertEqual(adapter["totals"]["post_quiet_backup_close_off_s"]["seconds"], 420)
        self.assertEqual(set(adapter["sizing"]["auxiliary"]), {
            "gamma-bound-collection", "gamma-bound-derivation", "gamma-reference-start",
            "gamma-reference-decode-midpoint", "gamma-reference-end"})

    def test_source_mutation_negative_nan_and_unresolved_fill(self):
        changed = copy.deepcopy(self.sizing)
        changed["fixed"]["pack_t0"]["source"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            self.size(changed)
        for bad in (-1, float("nan"), True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    writer.number(bad, "fixture")
        with self.assertRaisesRegex(ValueError, "unresolved_fill"):
            writer.no_fill({"nested": ["FILL[PACK]"]})

    def test_retired_r1_has_no_sizing_or_cli_route(self):
        with self.assertRaisesRegex(ValueError, "occurrence_retired"):
            writer.size_window("r1", self.sizing)
        for occurrence in ("a1", "a2"):
            self.assertEqual(self.size(), writer.size_window(occurrence, self.sizing,
                roster=self.roster, auxiliary=self.aux, brackets=self.brackets))

    def test_deadline_latest_chain_start_shutdown_courier_and_deadman(self):
        from scripts.run_night import deadman_epoch
        plan = night_gate.NightPlan("fixture", "TRANSACTION_PACK", 1000., 3600, 0., "a" * 40,
                                   str(self.root), "a" * 40, "/chain", "/chain.sha256", str(self.root), None)
        bounds = {"latest_chain_start_epoch_s": 3740., "shutdown_epoch_s": 4900.,
                  "courier_epoch_s": 5200., "deadman_epoch_s": deadman_epoch(plan)}
        self.assertEqual(bounds, writer.deadlines(plan, 860, bounds))
        for key in bounds:
            with self.subTest(key=key):
                changed = dict(bounds)
                changed[key] += 1
                with self.assertRaises(ValueError):
                    writer.deadlines(plan, 860, changed)


class PlanWriterTests(SizingTests):
    """Real record/plan serializer and gate; fixtures stub frozen ARM inputs only."""
    def setUp(self):
        super().setUp()
        self.repo = self.root / "JouleWise-fixture"
        self.repo.mkdir()
        self.pack = self.repo / "rehearsal-pack"
        self.pack.mkdir()
        (self.pack / "placeholder").write_text("fixture")
        for argv in (["init", "-q"], ["add", "."], ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.test", "commit", "-qm", "fixture"]):
            subprocess.run(["git", "-C", str(self.repo), *argv], check=True, capture_output=True)
        self.head = subprocess.check_output(["git", "-C", str(self.repo), "rev-parse", "HEAD"], text=True).strip()
        self.custody = self.root / "s1-fixture"
        self.custody.mkdir()
        self.chain = self.root / "chain.zsh"
        self.chain.write_text("#!/bin/zsh\nexport NIGHT_PROGRAMMED_SPAN_S=40\nexport NIGHT_LATEST_CHAIN_START_EPOCH_S=3720\nexport V5_QUALIFICATION_OCCURRENCE=s1\necho fixture\n")
        self.sidecar = self.root / "chain.sha256"
        self.sidecar.write_bytes(readiness.gnu_sidecar(writer.locator(self.chain)["sha256"], self.chain.name))
        self.table = self.root / "d117_step6_confirmation_table_v5.json"
        self.table.write_text("{}\n")
        self.hc = writer.locator(self.table)["sha256"]
        self.transcript = self.root / "085-ed-step6-confirmed-sha256.txt"
        self.transcript.write_text("YES " + self.hc + "\n")
        self.confirm = self.root / "confirmed.json"
        writer.create_record(self.confirm, {"table_path": str(self.table), "table_sha256": self.hc,
            "transcript_sha256": writer.locator(self.transcript)["sha256"],
            "confirmed_at": {"epoch_s": 0., "iso8601_utc": "1970-01-01T00:00:00.000000Z"}})
        digest = readiness.committed_pack_tree_sha256(self.pack)
        context = arm_context(self.root)
        context["custody_root"] = str(self.custody)
        for key in readiness.ARM_CONTEXT_KEYS - readiness.ARM_CONTEXT_NON_PATH_KEYS:
            path = Path(context[key])
            if key == "waiver_path":
                path.write_text("fixture")
            else:
                path.mkdir(exist_ok=True)
        self.input = {"schema_version": writer.INPUT_SCHEMA, "head": self.head,
            "plan": {"schema": night_gate.PACK_PLAN_SCHEMA, "schema_version": 3,
                "plan_id": self.custody.name, "receipt_class": "TRANSACTION_PACK", "t0_epoch_s": 1000.,
                "window_max_s": 2760, "authored_epoch_s": 0., "repo_head": self.head,
                "measurement_root": str(self.repo), "measurement_head": self.head,
                "chain_path": str(self.chain), "chain_sha256_path": str(self.sidecar),
                "custody_root": str(self.custody), "registration_path": None},
            "pack": {"root": str(self.pack), "sha256": digest, "attempt_ordinal": 2},
            "authorization": {"purpose": "G2B_SHAKEDOWN", "attempt_id": self.custody.name + "/2",
                "claim_eligible": False, "permitted_blocks": 1, "pack_sha256": digest,
                "permitted_chain_sha256": writer.locator(self.chain)["sha256"], "authority": "D-171 §3 / ruling 76"},
            "confirmation": {"record": writer.locator(self.confirm), "transcript": writer.locator(self.transcript),
                "expected_confirmation_digest": self.hc},
            "sizing": {"fixed": {name: self.allow(8) for name in writer.FIXED_COMPONENTS["s1"]},
                       "members": {}, "auxiliary": {}, "streams": {}, "clock": self.sizing["clock"]},
            "deadlines": {"latest_chain_start_epoch_s": 3720., "shutdown_epoch_s": 4060.,
                          "courier_epoch_s": 4360., "deadman_epoch_s": 7680.},
            "other_custody_roots": [], "arm_context": context, "prerequisites": {}}
        producers = {}
        for name, relative in (("driver", "scripts/run_night.py"), ("bundle", "scripts/produce_t0_rehearsal_bundle.py"), ("evaluator", "joulewise/t0_rehearsal.py")):
            path = self.repo / relative
            path.parent.mkdir(exist_ok=True)
            path.write_text("fixture source only\n")
            producers[name] = writer.locator(path)
        self.input["prerequisites"] = {"observation_producers": producers,
            "g10_control": writer.locator(self.confirm), "g10_artifacts": [writer.locator(self.transcript)]}
        self.output = self.custody / "night_plan.json"
        for target, name, replacement in (
            (writer, "g2b_body", mock.Mock(return_value="echo fixture\n")),
            (writer, "prerequisites", mock.Mock()),
            (writer, "pack_roster", mock.Mock(return_value=([], [], [], []))),
            (readiness, "_pack_record", mock.Mock(return_value={"plan_id": self.custody.name, "window_id": self.custody.name})),
            (writer, "authenticate_frozen_pack", mock.Mock(return_value={"path": "/fixture/freeze.json", "sha256": "0" * 64})),
            (readiness, "_authenticate_confirmation_table", mock.Mock()),
            (readiness, "_authenticate_launcher_identity", mock.Mock(return_value=self.repo)),
            (readiness, "_production_inventory", mock.Mock(return_value={})),
            (night_gate, "_pack_rehearsal_roots", mock.Mock()),
        ):
            patcher = mock.patch.object(target, name, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)

    def write(self):
        return writer.write_qualification("s1", self.input, self.output)

    def test_canonical_create_once_records_and_run_command(self):
        self.write()
        plan = night_gate.NightPlan.from_mapping(json.loads(self.output.read_bytes()))
        self.assertEqual(night_plan_mapping(plan), json.loads(self.output.read_bytes()))
        record = json.loads((self.custody / "qualification-plan-record.json").read_bytes())
        self.assertIn("run", record["driver_argv"])
        self.assertNotIn("rehearse", record["driver_argv"])
        self.assertEqual(2, plan.pack_night["attempt_ordinal"])
        for key in ("authorization_record", "confirmation_record"):
            ref = plan.pack_night[key]
            self.assertEqual(ref, writer.locator(ref["path"]))
            self.assertEqual(0o600, Path(ref["path"]).stat().st_mode & 0o777)
        before = self.output.read_bytes()
        with self.assertRaises(ValueError):
            self.write()
        self.assertEqual(before, self.output.read_bytes())
        with self.assertRaises(FileExistsError):
            write_night_plan(self.output, plan, create_once=True)

    def test_s1_plan_names_independent_backups_and_desk_recipe(self):
        self.write()
        record = writer.read_object(self.custody / "qualification-plan-record.json")
        self.assertEqual(record["backup_destinations"], writer.backup_destinations(self.input["arm_context"]))
        self.assertTrue(record["observation_recipe"]["desk_closeout_after_quiet_window"])
        self.assertIn("v5_s1_desk_closeout.py", " ".join(record["observation_recipe"]["desk_closeout_argv"]))

    def test_equal_or_nested_backup_destinations_refuse_before_write(self):
        context = self.input["arm_context"]
        for bound in (context["claim_backup_destination"], context["claim_backup_destination"] + "/nested"):
            context["bound_backup_destination"] = bound
            with self.assertRaisesRegex(ValueError, "backup_destinations_overlap"):
                self.write()
            self.assertFalse(self.output.exists())

    def test_wrong_head_purpose_claim_eligibility_and_partial_pack_refuse(self):
        for group, key, value in (("plan", "repo_head", "0" * 40),
                                  ("authorization", "purpose", "CAMPAIGN_TRANSACTION"),
                                  ("authorization", "claim_eligible", True),
                                  ("pack", "sha256", "0" * 64),
                                  ("authorization", "permitted_blocks", 2)):
            with self.subTest(key=key):
                original = self.input[group][key]
                self.input[group][key] = value
                with self.assertRaises(ValueError):
                    self.write()
                self.input[group][key] = original
                self.assertFalse(self.output.exists())

    def test_custody_overlap_symlink_fill_and_environment_digest_refuse(self):
        self.input["other_custody_roots"] = [str(self.custody / "nested")]
        with self.assertRaisesRegex(ValueError, "custody_overlap"):
            self.write()
        self.input["other_custody_roots"] = []
        self.chain.write_text(self.chain.read_text() + "export EXPECTED_CONFIRMATION_DIGEST=abc\n")
        with self.assertRaisesRegex(ValueError, "confirmation_environment_route"):
            self.write()

    def test_confirmation_uses_prior_digest_and_transcript_not_current_self_hash(self):
        self.input["confirmation"]["expected_confirmation_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "independent_confirmation_digest"):
            self.write()

    def test_confirmation_digest_cannot_be_embedded_in_chain(self):
        digest = self.input["confirmation"]["expected_confirmation_digest"]
        self.chain.write_text(self.chain.read_text() + "# " + digest + "\n")
        with self.assertRaisesRegex(ValueError, "confirmation_chain_literal"):
            self.write()

    def test_runtime_gate_checks_latest_start_before_arm_verification(self):
        self.write()
        plan = night_gate.NightPlan.from_mapping(writer.read_object(self.output))
        prepared = night_gate._authenticate_pack_records(plan)
        probes = mock.Mock(now_epoch_s=lambda: 3721.)
        with mock.patch.object(night_gate, "_authenticate_pack_records", return_value=prepared), \
             mock.patch.object(readiness, "_verify_arm_receipt") as verify:
            with self.assertRaises(night_gate.PlanError) as error:
                night_gate._evaluate_pack_conditions(plan, probes, {}, None)
            self.assertEqual("night_window_expired", error.exception.reason)
            verify.assert_not_called()

    def test_qualification_marker_cannot_authorize_a_claim_purpose(self):
        self.write()
        plan = night_gate.NightPlan.from_mapping(writer.read_object(self.output))
        text = self.chain.read_text().replace("V5_QUALIFICATION_OCCURRENCE=s1", "V5_QUALIFICATION_OCCURRENCE=s1")
        with self.assertRaisesRegex(ValueError, "non-claim purpose"):
            night_gate.qualification_start_deadline(plan, text, "CAMPAIGN_TRANSACTION")

    def test_render_chain_emits_span_and_deadline_without_modifying_template(self):
        template = self.root / "template.zsh"
        template.write_text("#!/bin/zsh\necho fixture\n")
        output = self.root / "rendered-chain.zsh"
        result = writer.render_qualification_chain("s1", template, self.input["sizing"], self.pack, 1000., output)
        self.assertEqual(40, result["programmed_span_s"])
        self.assertEqual("40", night_gate.chain_literal(output.read_text(), "NIGHT_PROGRAMMED_SPAN_S"))
        self.assertEqual("3720", night_gate.chain_literal(output.read_text(), "NIGHT_LATEST_CHAIN_START_EPOCH_S"))
        self.assertEqual("#!/bin/zsh\necho fixture\n", template.read_text())
        self.assertEqual(writer.locator(output)["sha256"], Path(str(output) + ".sha256").read_text().split()[0])

    def test_a1_is_context_only_and_s1_is_a_canonical_run_plan(self):
        for occurrence in ("a1", "a2", "s1"):
            with self.subTest(occurrence=occurrence):
                inputs = copy.deepcopy(self.input)
                custody = self.root / (occurrence + "-context-fixture")
                custody.mkdir()
                inputs["plan"].update(plan_id=custody.name, custody_root=str(custody))
                inputs["arm_context"]["custody_root"] = str(custody)
                inputs["sizing"]["fixed"] = {key: self.allow(8) for key in writer.FIXED_COMPONENTS["s1"]}
                inputs["authorization"].update(purpose="G2B_SHAKEDOWN", authority="D-171 §3", attempt_id=custody.name + "/2")
                chain = self.root / (occurrence + "-chain.zsh")
                chain.write_text(self.chain.read_text().replace("V5_QUALIFICATION_OCCURRENCE=s1", "V5_QUALIFICATION_OCCURRENCE=s1"))
                sidecar = self.root / (occurrence + "-chain.sha256")
                sidecar.write_bytes(readiness.gnu_sidecar(writer.locator(chain)["sha256"], chain.name))
                inputs["plan"].update(chain_path=str(chain), chain_sha256_path=str(sidecar))
                inputs["authorization"]["permitted_chain_sha256"] = writer.locator(chain)["sha256"]
                output = custody / ("arm-only-context.json" if occurrence in {"a1", "a2"} else "night_plan.json")
                with mock.patch.object(writer, "g2b_body", return_value="echo fixture\n"), \
                     mock.patch.object(readiness, "_pack_record", return_value={"plan_id": custody.name, "window_id": custody.name}), \
                     mock.patch.object(writer, "prerequisites"):
                    writer.write_qualification(occurrence, inputs, output)
                value = writer.read_object(output)
                if occurrence in {"a1", "a2"}:
                    self.assertEqual(writer.ARM_ONLY_SCHEMA, value["schema_version"])
                    self.assertNotIn("driver_argv", value)
                    self.assertFalse((custody / "night_plan.json").exists())
                    with self.assertRaises(night_gate.PlanError):
                        night_gate.NightPlan.from_mapping(value)
                else:
                    self.assertEqual("TRANSACTION_PACK", night_gate.NightPlan.from_mapping(value).receipt_class)


class PrerequisiteTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.custody = self.root / "s1"; self.custody.mkdir()
        self.head = "a" * 40
        self.refs = {}
        self.controls = {}
        from joulewise import t0_rehearsal as t0
        from scripts.check_v5_arm_abort import ABSENCE_KEYS, CONTROL_SCHEMA
        for label, at in (("a1", 1000), ("a2", 2000)):
            root = self.root / label; root.mkdir()
            context = root / "context.json"
            source = root / "source.json"
            context.write_bytes(readiness.render_json({"head": self.head}))
            source.write_bytes(readiness.render_json({"first_t0_boundary_monotonic_ns": at - 100}))
            control = {"schema_version": CONTROL_SCHEMA, "occurrence": label, "verdict": "PASS",
                "refusal_reason_code": "readiness_record_expired", "checked_epoch_s": at,
                "checked_monotonic_ns": at, "boot_session_id": "same-boot",
                "absence": {key: True for key in ABSENCE_KEYS}, "context": writer.locator(context),
                "ordering": {"expired_before_s1_t0": True}, "arm_receipt": writer.locator(source),
                "observation": writer.locator(source), "sources": []}
            path = root / "arm-abort-control.json"
            path.write_bytes(readiness.render_json(control))
            self.refs[label + "_control"] = writer.locator(path)
            self.controls[label] = (path, control)
        producers = {}
        for name, suffix in (("driver", "scripts/run_night.py"), ("bundle", "scripts/produce_t0_rehearsal_bundle.py"), ("evaluator", "joulewise/t0_rehearsal.py")):
            path = self.root / suffix; path.parent.mkdir(exist_ok=True)
            path.write_text("fixture-only source")
            producers[name] = writer.locator(path)
        positive = self.root / "g10.json"
        positive.write_bytes(readiness.render_json({"schema_version": t0.POSITIVE_CONTROL_SCHEMA,
            "performed_by": "Ed", "outside_t0_sequence": True, "network_time_reenabled": True,
            "forced_resync": True, "anchor_before_ns": 0, "anchor_after_ns": 5_000_001,
            "author_refusal_reason_code": "evidence_author_t0_clock_attestation_underivable"}))
        self.refs.update(observation_producers=producers, g10_control=writer.locator(positive),
                         g10_artifacts=[writer.locator(positive)])

    def test_fold_has_no_r1_and_requires_a1_a2_g10_and_source_pins(self):
        writer.prerequisites("a1", {}, self.head, 500, self.custody)
        writer.prerequisites("a2", {"a1_control": self.refs["a1_control"]}, self.head, 1500, self.custody)
        writer.prerequisites("s1", self.refs, self.head, 3000, self.custody)
        for key in self.refs:
            changed = dict(self.refs); changed.pop(key)
            with self.subTest(key=key), self.assertRaises(ValueError):
                writer.prerequisites("s1", changed, self.head, 3000, self.custody)
        with self.assertRaises(ValueError):
            writer.prerequisites("s1", dict(self.refs, r1_bundle=self.refs["g10_control"]), self.head, 3000, self.custody)

    def test_each_control_must_expire_without_launch_before_s1_t0(self):
        for label in ("a1", "a2"):
            path, control = self.controls[label]
            for defect in ("late", "wrong_refusal", "launch"):
                candidate = copy.deepcopy(control)
                if defect == "late": candidate["checked_epoch_s"] = 3000
                elif defect == "wrong_refusal": candidate["refusal_reason_code"] = "different"
                else: candidate["absence"]["chain_started_absent"] = False
                path.write_bytes(readiness.render_json(candidate))
                refs = dict(self.refs, **{label + "_control": writer.locator(path)})
                with self.subTest(label=label, defect=defect), self.assertRaises(ValueError):
                    writer.prerequisites("s1", refs, self.head, 3000, self.custody)
                path.write_bytes(readiness.render_json(control))

    def test_a2_t0_must_follow_a1_expiry(self):
        path, control = self.controls["a1"]
        control["checked_monotonic_ns"] = 1900
        path.write_bytes(readiness.render_json(control))
        refs = dict(self.refs, a1_control=writer.locator(path))
        with self.assertRaisesRegex(ValueError, "a1_before_a2"):
            writer.prerequisites("s1", refs, self.head, 3000, self.custody)


class PackRosterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=tempfile.gettempdir())
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve() / writer.GAMMA
        self.root.mkdir()
        self.science = []
        self.inventory = []
        for index in range(80):
            stage = self.root / f"stage-{index // 20}"
            stage.mkdir(exist_ok=True)
            path = stage / f"member-{index:02}.json"
            path.write_text(json.dumps({"run_id": f"member-{index:02}"}))
            self.inventory.append({"path": path.relative_to(self.root).as_posix(), "sha256": writer.locator(path)["sha256"]})
            pos = ("A1", "B1", "B2", "A2")[index % 4]
            self.science.append({"stage_id": f"science-{index // 20}", "run_id": f"member-{index:02}",
                "config_path": path.relative_to(self.root).as_posix(), "config_sha256": writer.locator(path)["sha256"],
                "block_id": f"block-{index // 4}", "position": pos, "arm": "A" if pos.startswith("A") else "B"})
        for index in range(4):
            rows = self.science[index * 20: (index + 1) * 20]
            path = self.root / f"stage-{index}" / "order_manifest.json"
            path.write_bytes(readiness.render_json({"executed_order": [
                {"index": i + 1, "config": Path(row["config_path"]).name, "run_id": row["run_id"]}
                for i, row in enumerate(rows)]}))
        self.tree = {"science": self.science,
            "stage_graph": [{"stage_id": f"science-{i}", "kind": "campaign_collection"} for i in range(4)]
                + [{"stage_id": name, "kind": "campaign_collection"} for name in ("neg8", "start", "midpoint", "end")]
                + [{"stage_id": "bound-derivation", "kind": "bound_derivation"}]
                + [{"stage_id": name, "kind": "calibration_capture"} for name in ("calibration-pre", "calibration-post")],
            "arm_attachments": {"identity_pin_projection": {"identity_units": [{"config_inventory": self.inventory}]}}}
        def collection(name, path):
            return {"stage_id": name, "kind": "campaign_collection", "launch": {"commands": [
                {"argv_template": {"arguments": [{"kind": "repo_path", "value": path}]}}]}}
        self.tree["stage_graph"] = [
            {"stage_id": "calibration-pre", "kind": "calibration_capture", "input_ref": {"slot": "pre_attempt_id"}},
            collection("neg8", "configs/campaigns/neg8_reference_corpus"),
            {"stage_id": "bound-derivation", "kind": "bound_derivation"},
            collection("start", "configs/campaigns/window_references/start_triplet"),
            {"stage_id": "science-0", "kind": "campaign_collection"},
            collection("midpoint", "configs/campaigns/window_references/midpoint"),
            collection("end", "configs/campaigns/window_references/end_triplet"),
            {"stage_id": "calibration-post", "kind": "calibration_capture", "input_ref": {"slot": "post_attempt_id"}}]
        patch = mock.patch.object(readiness, "_repo_for_pack", return_value=writer.REPO_ROOT)
        patch.start(); self.addCleanup(patch.stop)
        self.save()

    def save(self):
        path = self.root / "plan_tree.json"
        path.write_bytes(readiness.render_json(self.tree))
        path.with_name("plan_tree.sha256").write_bytes(readiness.gnu_sidecar(writer.locator(path)["sha256"], path.name))

    def test_authentic_first_stage_and_full_auxiliary_roster(self):
        rows, aux, brackets, nonsampling = writer.pack_roster(self.root, "s1")
        self.assertEqual(["A1", "B1", "B2", "A2"], [r["position"] for r in rows])
        self.assertEqual(["neg8", "bound-derivation", "start", "midpoint", "end"], aux)
        self.assertEqual(["calibration-pre", "calibration-post"], brackets)
        self.assertEqual(["bound-derivation"], nonsampling)
        self.assertEqual(80, len(self.tree["science"]))

    def test_undispatched_stages_change_nothing_dispatched_omission_refuses(self):
        before = writer.pack_roster(self.root, "s1")
        dormant = copy.deepcopy(self.tree["stage_graph"][5])
        dormant["stage_id"] = "gamma-reference-arm-boundary"
        self.tree["stage_graph"].insert(6, dormant)
        dormant = copy.deepcopy(dormant)
        dormant["stage_id"] = "gamma-reference-prefill-midpoint"
        self.tree["stage_graph"].insert(7, dormant)
        self.tree["stage_graph"].append({"stage_id": "extra-unused", "kind": "campaign_collection"})
        self.save()
        self.assertEqual(before, writer.pack_roster(self.root, "s1"))
        graph = copy.deepcopy(self.tree["stage_graph"])
        for missing in ("start", "midpoint"):
            self.tree["stage_graph"] = [row for row in graph if row["stage_id"] != missing]
            self.save()
            with self.subTest(missing=missing), self.assertRaisesRegex(ValueError, "dispatched_stage_missing"):
                writer.pack_roster(self.root, "s1")

    def test_partial_pack_swapped_order_and_missing_config_refuse(self):
        self.tree["science"].pop()
        self.save()
        with self.assertRaisesRegex(ValueError, "partial_gamma_pack"):
            writer.pack_roster(self.root, "s1")

    def test_swapped_first_stage_manifest_refuses(self):
        path = self.root / "stage-0/order_manifest.json"
        value = writer.read_object(path)
        value["executed_order"][0]["config"], value["executed_order"][1]["config"] = (
            value["executed_order"][1]["config"], value["executed_order"][0]["config"])
        path.write_bytes(readiness.render_json(value))
        with self.assertRaisesRegex(ValueError, "first_stage_order"):
            writer.pack_roster(self.root, "s1")

    def test_missing_bracket_stream_roster_refuses(self):
        self.tree["stage_graph"].pop()
        self.save()
        with self.assertRaisesRegex(ValueError, "dispatched_stage_missing"):
            writer.pack_roster(self.root, "s1")

    def test_missing_or_mutated_config_and_unresolved_fill_refuse(self):
        path = self.root / self.science[6]["config_path"]
        path.write_text("{}\n")
        with self.assertRaises(ValueError):
            writer.pack_roster(self.root, "s1")

    def test_generated_body_retains_one_block_and_post_path_without_hc_env(self):
        body = writer.g2b_body(writer.REPO_ROOT)
        self.assertIn("--max-blocks 1", body)
        self.assertIn("post-bracket-terminal-boundary.json", body)
        self.assertNotIn("$EXPECTED_CONFIRMATION_DIGEST", body)
        self.assertNotIn("$STEP6_CONFIRMATION_TABLE", body)
        self.assertNotIn("```", body)
        subprocess.run(["/bin/zsh", "-n"], input=body, text=True, check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
