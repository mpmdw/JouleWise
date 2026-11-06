import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import qwen4exp_align_feasibility as feasibility

ROOT = Path(__file__).resolve().parents[1]
KIT_REF = "origin/lane/2026-11-05-align-v4-assembled"
# Roles in align_v4_kit.ROSTER order (ordinals 1..18).
ROLES = ("anchor",) * 4 + ("D", "X-G", "Y-S", "D", "X-S", "Y-G", "D", "Y-G", "X-S", "D",
                           "Y-S", "X-G", "D", "D")
SLOPE = 1.13544


def _ref_available():
    return subprocess.run(["git", "cat-file", "-e", f"{KIT_REF}:scripts/align_v4_kit.py"],
                          cwd=ROOT, capture_output=True).returncode == 0


class AlignFeasibilityTests(unittest.TestCase):
    """Fixtures use the kit's own JSON shapes (align_v4_kit.build_files at fc83cfe1d)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.kit = self.root / "align_v4"
        (self.kit / "registration").mkdir(parents=True)
        self.inputs = {"schema_version": "joulewise.align_v4_inputs.v1",
                       "status": "PROVISIONAL_PLACEHOLDERS_NOT_EXECUTABLE",
                       "WP11": {"identity_unit": None, "artifact_inventory": None,
                                "local_file_verification": None},
                       "WP18": {"X": {"max_turns": None, "token_fixture_sha256": None},
                                "Y": {"max_turns": None, "token_fixture_sha256": None}},
                       "R0": {"reasoning_effort": None},
                       "R1": {"B_D": None, "I_D": None, "T_dead": None, "thermal_policy": None},
                       "WP15": {"runtime_entrypoint": None}}
        members = []
        for ordinal, role in enumerate(ROLES, 1):
            spec = {"max_tokens": 4096, "max_context_tokens": 40960,
                    "max_turns": 12 if role in ("anchor", "D") else None}
            if role == "D":
                spec.update(max_episode_decode_tokens=None, deadman_s=None,
                            chat_template_kwargs={"reasoning_effort": None})
            members.append({"ordinal": ordinal, "role": role, "spec": spec})
        self.plan = {"schema_version": "joulewise.align_v4.v1", "plan_id": "align-v4", "members": members}
        self.sizing = {"align_members": 18, "fit_rule": ["drop ordinal 17", "lower B_D by 1024 to 6144",
                                                         "return to lead"],
                       "member_seconds": {"D": 1800, "G": 1150, "S": 850, "anchor": 782.8175},
                       "non_claim": True, "planning_align_s": 21931.27, "planning_span_s": 26927,
                       "planning_two_copy_GB": 37.4, "planning_window_max_s": 44640, "scaffold_s": 4995,
                       "span_limit_s": 26940, "status": "PROVISIONAL_NOT_ARM_SIZING"}
        self.tree = {"generator": {"path": "scripts/align_v4_kit.py", "sha256": feasibility.KIT_SHA256}}
        self.slots = {"schema": "joulewise.align.r1_slots.v1", "source": "PENDING_R1_REHEARSAL",
                      "slot_names": ["B_D", "I_D", "T_dead"], "slots": None}
        self.write_kit()

    def write_kit(self):
        for rel, value in (("registration/inputs.json", self.inputs), ("collection_plan.json", self.plan),
                           ("registration/sizing_preview.json", self.sizing), ("plan_tree.json", self.tree),
                           ("registration/r1_slots.json", self.slots)):
            (self.kit / rel).write_text(json.dumps(value))

    def load(self):
        self.write_kit()
        return feasibility.load_kit(*feasibility.kit_reader(kit_dir=self.kit))

    def performance(self, name, prefill=1000, decode=25, profile="maxfit", synthetic=None, contexts=None):
        rows = [{"reasoning_effort": e, "context": c, "prefill_tps": prefill, "decode_tps": decode}
                for e in ("low", "medium", "xhigh") for c in (contexts or feasibility.CONTEXT_RUNGS)]
        report = {"schema": "qwen4exp-mbp-live/v1", "command": "performance", "validation_only": True,
                  "profile": profile, "verdict": "completed",
                  "results": {"verdict": "completed", "medians": rows}}
        if synthetic == "top":
            report["synthetic"] = True
        elif synthetic == "results":
            report["results"]["synthetic"] = True
        path = self.root / name
        path.write_text(json.dumps(report))
        return path

    def set_r1(self, b_d, i_d, tail=None, t_dead=None):
        self.inputs["R1"].update(B_D=b_d, I_D=i_d,
                                 T_dead=t_dead if t_dead is not None else feasibility.t_dead_rule(i_d, tail))
        if tail is not None:
            self.slots["max_r1_tail_s"] = tail

    # ------------------------------------------------------------------ kit format

    @unittest.skipUnless(_ref_available(), f"{KIT_REF} not fetched")
    def test_reads_the_real_assembled_kit_from_git(self):
        kit = feasibility.load_kit(*feasibility.kit_reader(ref=KIT_REF, repo=ROOT))
        self.assertTrue(kit["rules_verified"])
        self.assertEqual((kit["turn_cap"], kit["context_cap"], kit["max_turns"]), (4096, 40960, 12))
        self.assertEqual([o for o, r in kit["roles"] if r == "D"], [5, 8, 11, 14, 17, 18])
        self.assertEqual(kit["window"], {"scaffold_s": 4995, "span_limit_s": 26940, "planning_window_max_s": 44640})
        self.assertIsNone(kit["r1"])  # R1 slots are still null on the assembled lane

    def test_caps_come_from_the_kit_not_the_module(self):
        for spec in (m["spec"] for m in self.plan["members"] if m["role"] == "D"):
            spec["max_tokens"] = 2048
        kit = self.load()
        self.assertEqual(kit["turn_cap"], 2048)
        cost = feasibility.episode_seconds(kit, {"prefill_tps": 1000, "decode_tps": 25}, 8192)
        self.assertEqual(cost["decode_tokens"], 8192 - 1 + 2048)

    def test_refuses_other_formats(self):
        self.inputs["schema_version"] = "align-v4-feasibility/v1"
        with self.assertRaisesRegex(ValueError, "joulewise.align_v4_inputs.v1"):
            self.load()

    def test_rules_digest_mismatch_is_printed(self):
        self.tree["generator"]["sha256"] = "0" * 64
        kit = self.load()
        self.assertFalse(kit["rules_verified"])
        text = feasibility.render(feasibility.calculate(
            kit, feasibility.load_performance([self.performance("p.json")])))
        self.assertIn("RULES_UNVERIFIED", text)

    # ------------------------------------------------------------------ R1 pending

    def test_pending_r1_reports_largest_kit_legal_budget(self):
        rows = feasibility.calculate(self.load(), feasibility.load_performance([self.performance("p.json")]))["rows"]
        self.assertEqual([r["effort"] for r in rows], ["xhigh", "medium", "low"])
        best = rows[0]["best"]
        # Deadman at I_D = 0 is 1750 / 1.13544 = 1541.2 s.  No reuse: 12 x 36,864
        # prefill = 442.4 s, so decode <= 1098.8 s; B_D 22528 decodes 26,623 tokens.
        self.assertEqual(best["uncached_s"]["B_D"], 22528)
        # Prefix cache: B_D 33792 decodes 37,887 tokens (1515.5 s) + 3,073 prefill.
        self.assertEqual(best["cached_s"]["B_D"], 33792)
        self.assertAlmostEqual(best["cached_s"]["I_D_max"], 1750 - SLOPE * (37887 / 25 + 3073 / 1000))
        self.assertEqual(rows[0]["verdict"], "FITS_AT_B_D_FLOOR")
        self.assertEqual(rows[0]["window"]["programmed_span_s"], 26927)  # sizing_preview at the D cap

    def test_selected_r0_effort_is_the_only_row(self):
        self.inputs["R0"]["reasoning_effort"] = "medium"
        rows = feasibility.calculate(self.load(), feasibility.load_performance([self.performance("p.json")]))["rows"]
        self.assertEqual([r["effort"] for r in rows], ["medium"])

    # ------------------------------------------------------------------ R1 filled

    def test_r1_budget_verdict_member_and_window(self):
        self.set_r1(16384, 400)
        row = feasibility.calculate(self.load(), feasibility.load_performance([self.performance("p.json")]))["rows"][0]
        t_dead = (1750 - 400) / SLOPE
        self.assertEqual(row["decode_tokens"], 20479)
        self.assertGreater(row["uncached_s"], t_dead)
        self.assertLess(row["cached_s"], t_dead)
        self.assertEqual(row["verdict"], "FITS_ONLY_IF_PREFIX_CACHE_HOLDS")
        self.assertAlmostEqual(row["member_s_worst"], 1750)
        self.assertTrue(row["window"]["fits"])
        self.assertEqual(row["window"]["programmed_span_s"], 26627)

    def test_window_applies_the_kit_fit_rule(self):
        self.set_r1(16384, 400)
        self.sizing["span_limit_s"] = 26000
        row = feasibility.calculate(self.load(), feasibility.load_performance([self.performance("p.json")]))["rows"][0]
        self.assertEqual(row["window"]["actions"], [{"drop_ordinal": 17}])
        self.assertNotIn(17, row["window"]["ordinals"])

    def test_t_dead_follows_lead_ruling_l1(self):
        self.set_r1(16384, 400, t_dead=(1750 - 400) / SLOPE)
        self.load()  # tail unknown: the kit's own rule
        self.slots["max_r1_tail_s"] = 60  # second term governs: (1800 - 400 - 60 - 10) / 1.13544
        with self.assertRaisesRegex(ValueError, "T_dead must equal"):
            self.load()
        self.set_r1(16384, 400, tail=60)
        self.assertAlmostEqual(self.load()["r1"]["T_dead"], 1330 / SLOPE)

    def test_r1_slots_are_validated(self):
        self.inputs["R1"].update(B_D=16384, I_D=None, T_dead=None)
        with self.assertRaisesRegex(ValueError, "filled together"):
            self.load()
        self.set_r1(16000, 400)
        with self.assertRaisesRegex(ValueError, "multiple of 1024"):
            self.load()
        self.set_r1(16384, 1750, t_dead=0.0)
        with self.assertRaisesRegex(ValueError, "I_D"):
            self.load()

    # ------------------------------------------------------------------ performance

    def test_refuses_synthetic_performance_reports(self):
        for where in ("top", "results"):
            with self.assertRaisesRegex(ValueError, "synthetic"):
                feasibility.load_performance([self.performance(f"{where}.json", synthetic=where)])

    def test_cli_refuses_synthetic(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
            feasibility.main(["--performance", str(self.performance("s.json", synthetic="top")),
                              "--align-kit", str(self.kit)])
        self.assertIn("synthetic", err.getvalue())

    def test_charges_the_slowest_measured_rung(self):
        path = self.performance("p.json")
        report = json.loads(path.read_text())
        for row in report["results"]["medians"]:
            if row["context"] == 16384:
                row["decode_tps"] = 5
        path.write_text(json.dumps(report))
        rate = feasibility.slowest(feasibility.load_performance([path]), "low", 40960)
        self.assertEqual(rate, {"prefill_tps": 1000, "decode_tps": 5})

    def test_refuses_unmeasured_context_cap(self):
        rates = feasibility.load_performance([self.performance("p.json", contexts=(4096, 16384))])
        with self.assertRaisesRegex(ValueError, "missing measured median"):
            feasibility.calculate(self.load(), rates)

    def test_second_performance_file_supplies_preferred_medians(self):
        rates = feasibility.load_performance([self.performance("512.json"),
                                              self.performance("2048.json", prefill=2000)])
        self.assertEqual(rates[("low", 4096)]["prefill_tps"], 2000)

    def test_reads_medians_where_the_supervisor_writes_them(self):
        path = self.performance("p.json")
        report = json.loads(path.read_text())
        report["medians"] = report.pop("results")["medians"]
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "not completed|no median"):
            feasibility.load_performance([path])

    def test_refuses_mixed_profiles_and_incomplete_reports(self):
        with self.assertRaisesRegex(ValueError, "mix artifact profiles"):
            feasibility.load_performance([self.performance("a.json"), self.performance("b.json", profile="maxfit5")])
        path = self.performance("incomplete.json")
        report = json.loads(path.read_text())
        report["verdict"] = "incomplete"
        path.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, "not completed"):
            feasibility.load_performance([path])

    def test_cli_labels_estimate(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(feasibility.main(["--performance", str(self.performance("p.json")),
                                               "--align-kit", str(self.kit)]), 0)
        self.assertIn("PLANNING ESTIMATE — NOT ENERGY EVIDENCE", out.getvalue())
        self.assertIn("4096 tokens/turn, 12 turns, context 40960", out.getvalue())
        self.assertNotIn("RULES_UNVERIFIED", out.getvalue())


if __name__ == "__main__":
    unittest.main()
