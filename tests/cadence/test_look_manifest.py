"""The look manifest validator (RL-150 R4, RL-166). Synthetic inputs only: no custody, energy, meter or journal
file exists in these tests, and one test proves the validator opens none even when such files sit beside it."""
from __future__ import annotations

import builtins
import copy
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
import unittest.mock

from joulewise.cadence_looks import manifest as lm
from scripts import cadence_look_manifest as cli

REPO = Path(__file__).resolve().parents[2]
LOOKS = REPO / "docs/process/cadence/looks"
MANIFEST = LOOKS / "lm-interim-01.json"
SCHEMA = LOOKS / "look_manifest.schema.json"
LOOK_LEDGER = REPO / lm.LOOK_LEDGER_PATH
FIT = "joulewise/cadence_looks/fit_interim.py"
RULE34 = "joulewise/cadence_looks/inclusion_34.py"
ADAPTER = "joulewise/cadence_looks/step3_roster.py"
RUNNER = "scripts/cadence_look_run.py"


def draft():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def finalize(doc, shas=None):
    """A synthetic committed manifest: every PENDING:CODE filled, no open question."""
    shas = shas or {}
    doc = copy.deepcopy(doc)
    doc["status"] = "committed"

    def fill(node):
        if isinstance(node, dict):
            if set(node) == {"path", "sha256"}:
                if node["path"] in shas:
                    node["sha256"] = shas[node["path"]]
                elif node["sha256"] == lm.PENDING_CODE:
                    node["sha256"] = hashlib.sha256(node["path"].encode()).hexdigest()
                return
            for v in node.values():
                fill(v)
        elif isinstance(node, list):
            for v in node:
                fill(v)
    fill(doc)
    doc["open_questions"] = []
    drift = next(d for d in doc["decisions"] if d["id"] == "drift_tripwire")
    if drift.pop("pending", None) is not None:          # Mythos N10: Q11 disposed before commit (synthetic)
        drift["disposed_by"] = "RL-999"
    return doc


def ledger(spans=None, reads=None, sha=None):
    days = {"dev-01": "2026-11-14", "dev-02": "2026-11-16", "dev-03": "2026-11-16", "dev-04": "2026-11-17",
            "dev-05": "2026-11-17", "hp-01": "2026-11-15"}
    default = [{"span_id": f"{b}-s01", "block_id": b, "phase": "extension" if b == "hp-01" else "development",
                "desk_final": True, "energy_seal": "sealed", "t0_local_date": d} for b, d in days.items()]
    default.append({"span_id": "dev-01-s04b", "block_id": "dev-01", "phase": "development", "desk_final": True,
                    "energy_seal": "sealed", "t0_local_date": "2026-11-15"})
    default.append({"span_id": "qual-01-s01", "block_id": "qual-01", "phase": "qualification", "desk_final": False,
                    "energy_seal": "sealed", "t0_local_date": "2026-11-19"})
    return {"schema": lm.LEDGER_SCHEMA,
            "look_manifest": {"look_id": "lm-interim-01", "sha256": sha or "a" * 64},
            "spans": spans if spans is not None else default,
            "energy_reads": reads or [{"read_id": "step3-1114", "spans": ["rehearsal-1112-step-d"], "cite": ["RL-150 §3.1"]}]}


def tmpdir(test, prefix):
    d = Path(tempfile.mkdtemp(prefix=prefix))
    test.addCleanup(lambda: shutil.rmtree(d, ignore_errors=True))
    return d


class Base(unittest.TestCase):
    def refused(self, fn, fragment):
        with self.assertRaises(lm.ManifestError) as ctx:
            fn()
        self.assertTrue(any(fragment in p for p in ctx.exception.problems),
                        f"{fragment!r} not in {ctx.exception.problems}")
        return ctx.exception.problems


class CommittedDraft(Base):
    def test_the_committed_draft_validates_with_only_code_hashes_open(self):
        pending = lm.validate_manifest(draft())
        self.assertLessEqual({q for _, q in pending}, {"CODE"})        # RL-166 §2 item 3
        self.assertTrue(all(p.endswith(".sha256") for p, _ in pending))
        self.assertEqual(draft()["open_questions"], [])

    def test_the_draft_is_refused_as_final(self):
        self.refused(lambda: lm.validate_manifest(draft(), final=True), "needs status 'committed'")
        doc = draft()
        doc["fit"]["code"][0]["sha256"] = lm.PENDING_CODE
        self.refused(lambda: lm.validate_manifest(doc, final=True), "placeholder")

    def test_a_filled_synthetic_manifest_validates_as_final(self):
        self.assertEqual(lm.validate_manifest(finalize(draft()), final=True), [])

    def test_the_schema_pins_match_the_files(self):
        doc = draft()
        for ref in (doc["outputs"]["schema"], doc["stages"]["stage1"]["schema"]):
            self.assertEqual(hashlib.sha256((REPO / ref["path"]).read_bytes()).hexdigest(), ref["sha256"])

    def test_the_committed_draft_passes_the_repo_check(self):
        kits = sorted(str(p) for p in (REPO / "docs/process/cadence/kits").glob("*.json"))
        self.assertTrue(kits)
        lm.check_repo(draft(), REPO, kits)

    def test_the_look_ledger_pins_the_manifest(self):
        led = lm.validate_look_ledger(lm.load_json(LOOK_LEDGER), REPO)
        row = next(r for r in led["looks"] if r["look_id"] == "lm-interim-01")
        self.assertEqual(row["sha256"], lm.sha256_file(MANIFEST))
        self.assertEqual(row["status"], "draft")

    def test_cli(self):
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(cli.main(["validate", str(MANIFEST), "--repo", str(REPO)]), 0)
            self.assertEqual(cli.main(["validate", str(MANIFEST), "--final"]), 1)


class MissingFields(Base):
    def test_every_top_level_field_is_required(self):
        for key in sorted(lm.TOP_KEYS):
            doc = draft()
            del doc[key]
            self.refused(lambda: lm.validate_manifest(doc), f"missing key {key!r}")

    def test_unknown_keys_are_refused(self):
        doc = draft()
        doc["extra"] = 1
        self.refused(lambda: lm.validate_manifest(doc), "unknown key 'extra'")
        doc = draft()
        doc["fit"]["heat_term"]["notes"] = "x"
        self.refused(lambda: lm.validate_manifest(doc), "unknown key 'notes'")

    def test_nested_required_fields(self):
        cases = [
            (("fit", "heat_term"), "predictors"), (("fit", "heat_term"), "base"), (("fit", "onset"), "censoring"),
            (("fit", "validation"), "min_calendar_days"), (("fit", "rates"), "r_d"), (("fit", "step3"), "leg_failure"),
            (("stages", "stage1"), "schema"), (("stages",), "tripwires"), (("freeze2",), "commit_before"),
            (("custody",), "no_import_by"), (("energy",), "per_leg_energy_in_output"), (("reads",), "leg_types_never"),
            (("inclusion",), "interval"),
        ]
        for path, key in cases:
            doc = draft()
            node = doc
            for p in path:
                node = node[p]
            del node[key]
            self.refused(lambda: lm.validate_manifest(doc), f"missing key {key!r}")

    def test_cites_are_required(self):
        doc = draft()
        doc["decisions"][0]["cite"] = []
        self.refused(lambda: lm.validate_manifest(doc), "decisions[0].cite")

    def test_placeholders(self):
        doc = draft()
        doc["fit"]["heat_term"]["response"] = "PENDING:Q99"
        self.refused(lambda: lm.validate_manifest(doc), "Q99, which is not an open question")
        doc = draft()
        doc["fit"]["heat_term"]["response"] = "PENDING later"
        self.refused(lambda: lm.validate_manifest(doc), "a placeholder is written")
        doc = draft()
        doc["fit"]["heat_term"]["form"] = lm.PENDING_CODE
        self.refused(lambda: lm.validate_manifest(doc), "PENDING:CODE stands only for the sha256")
        doc = draft()
        doc["fit"]["code"][0]["path"] = lm.PENDING_CODE
        self.refused(lambda: lm.validate_manifest(doc), "fit.code[0].path")
        doc = finalize(draft())
        doc["fit"]["code"][0]["sha256"] = lm.PENDING_CODE
        self.refused(lambda: lm.validate_manifest(doc, final=True), "fit.code[0].sha256: 64 lowercase hex")

    def test_one_path_one_hash(self):
        doc = finalize(draft())
        doc["fit"]["step3"]["adapter"]["sha256"] = "f" * 64
        self.refused(lambda: lm.validate_manifest(doc, final=True), "pinned with different sha256 values")


class RulingInvariants(Base):
    def test_stage_one_opens_no_energy_and_commits_first(self):
        doc = draft()
        doc["stages"]["stage1"]["opens"].append("energy")
        self.refused(lambda: lm.validate_manifest(doc), "stage 1 opens no energy")
        doc = draft()
        doc["stages"]["stage1"]["committed_before_stage2"] = False
        self.refused(lambda: lm.validate_manifest(doc), "committed_before_stage2")
        doc = draft()
        doc["stages"]["stage2"]["time_budget_s"] = 3600
        self.refused(lambda: lm.validate_manifest(doc), "time_budget_s")
        doc = draft()
        doc["stages"]["tripwires"][0]["threshold"] = 40
        self.refused(lambda: lm.validate_manifest(doc), "dev_included_below_45 with threshold 45")
        doc = draft()
        doc["reads"]["custody_files"][1]["carries"] = "energy"
        self.refused(lambda: lm.validate_manifest(doc), "stage 1 opens no energy file")

    def test_rules_3_and_4(self):
        doc = draft()
        del doc["inclusion"]["rules"][2]["code"]
        self.refused(lambda: lm.validate_manifest(doc), "the code that judges rule 3")
        doc = draft()
        doc["inclusion"]["rules"][3]["judged_at"] = "runner"
        self.refused(lambda: lm.validate_manifest(doc), "inclusion.rules[3].judged_at")
        doc = draft()
        del doc["inclusion"]["rules"][4]
        self.refused(lambda: lm.validate_manifest(doc), "rule 5 (not_a_contaminated_attempt) is missing")
        doc = draft()
        doc["inclusion"]["rules"][0]["reads_energy"] = True
        self.refused(lambda: lm.validate_manifest(doc), "inclusion reads no energy")
        doc = draft()
        doc["inclusion"]["rules"][2]["text"] = "powermetrics gaps within the U1 bound"
        self.refused(lambda: lm.validate_manifest(doc), "max(1 s, 5 periods)")
        doc = draft()
        doc["inclusion"]["rules"][3]["text"] += " And trailer counts zero."
        self.refused(lambda: lm.validate_manifest(doc), "'trailer counts zero' clause is refused")
        doc = draft()
        doc["inclusion"]["verdicts_frozen_before_energy"] = False
        self.refused(lambda: lm.validate_manifest(doc), "verdicts_frozen_before_energy")

    def test_heat_term(self):
        for bad in ("in_turn_clock", "start_tv0h_raw", "prompt_size_cell_effect"):
            doc = draft()
            doc["fit"]["heat_term"]["predictors"].append(bad)
            self.refused(lambda: lm.validate_manifest(doc), "not allowed")
        doc = draft()
        doc["fit"]["heat_term"]["forbidden_predictors"].remove("condition")
        self.refused(lambda: lm.validate_manifest(doc), "must list ['condition']")
        doc = draft()
        doc["fit"]["heat_term"]["sign_of_start_term_assumed"] = True
        self.refused(lambda: lm.validate_manifest(doc), "sign_of_start_term_assumed")
        doc = draft()
        doc["fit"]["heat_term"]["unit"] = "turn"
        self.refused(lambda: lm.validate_manifest(doc), "'segment'")
        doc = draft()
        doc["fit"]["reads_never"] = ["kit_start_band", "kit_g0_shape"]
        self.refused(lambda: lm.validate_manifest(doc), "fit.reads_never")
        doc = draft()
        doc["fit"]["code"] = [c for c in doc["fit"]["code"] if c["path"] != RUNNER]
        self.refused(lambda: lm.validate_manifest(doc), f"pins {RUNNER}")
        doc = draft()
        doc["fit"]["runtime"] = "Python with scipy"
        self.refused(lambda: lm.validate_manifest(doc), "fit.runtime")

    def test_onset_rates_validation(self):
        doc = draft()
        doc["fit"]["onset"]["response"] = "Seconds from the first decode token to the first off-state reading."
        self.refused(lambda: lm.validate_manifest(doc), "from the turn's start stamp")
        doc = draft()
        doc["fit"]["onset"]["predictors"] = ["start_tf08", "load_seconds_from_counts"]
        self.refused(lambda: lm.validate_manifest(doc), "fit.onset.predictors: exactly")
        doc = draft()
        doc["fit"]["onset"]["reads_energy"] = True
        self.refused(lambda: lm.validate_manifest(doc), "fitted in stage 1, reading no energy")
        doc = draft()
        doc["fit"]["rates"]["stage"] = "stage2"
        self.refused(lambda: lm.validate_manifest(doc), "fit.rates.stage")
        doc = draft()
        doc["fit"]["validation"]["folds_refit"].append("rates")
        self.refused(lambda: lm.validate_manifest(doc), "folds_refit")

    def test_step3_is_pinned_byte_identical(self):
        doc = draft()
        doc["fit"]["step3"]["code"]["sha256"] = "0" * 64
        self.refused(lambda: lm.validate_manifest(doc), "byte-identical")
        doc = draft()
        doc["fit"]["step3"]["adapter"]["path"] = "joulewise/cadence_looks/step3_adapter.py"
        self.refused(lambda: lm.validate_manifest(doc), "fit.step3.adapter.path")

    def test_decisions_carry_rl166_thresholds(self):
        for did, value, fragment in (("drift_tripwire", 0.05, "threshold 0.08"),
                                     ("qualified_interim_half", 0.03, "threshold 0.02"),
                                     ("step3_cell_not_run", 3, "threshold 2")):
            doc = draft()
            next(d for d in doc["decisions"] if d["id"] == did)["threshold"] = value
            self.refused(lambda: lm.validate_manifest(doc), fragment)
        doc = draft()
        next(d for d in doc["decisions"] if d["id"] == "drift_tripwire")["fallback_threshold"] = 0.05
        self.refused(lambda: lm.validate_manifest(doc), "fallback_threshold 0.04")
        doc = draft()
        doc["decisions"] = [d for d in doc["decisions"] if d["id"] != "stage1_tripwires"]
        self.refused(lambda: lm.validate_manifest(doc), "carries stage1_tripwires")
        doc = draft()
        doc["decisions"].append({"id": "rule_p", "statistic": "x", "rule": "x", "action": "x", "reads_energy": True,
                                 "cite": ["RL-149 §2.7"]})
        self.refused(lambda: lm.validate_manifest(doc), "retired")

    def test_prints_and_channels(self):
        doc = draft()
        doc["outputs"]["prints"] = [p for p in doc["outputs"]["prints"] if p["id"] != "without_heat_columns"]
        self.refused(lambda: lm.validate_manifest(doc), "prints without_heat_columns")
        doc = draft()
        bias = next(p for p in doc["outputs"]["prints"] if p["id"] == "prefix_length_bias")
        bias["ratios"] = [1.10, 1.374]
        self.refused(lambda: lm.validate_manifest(doc), "ratios")
        doc = draft()
        doc["energy"]["channels"] = [c for c in doc["energy"]["channels"] if c["id"] != "dc_in"]
        self.refused(lambda: lm.validate_manifest(doc), "reads exactly")
        doc = draft()
        doc["energy"]["channels"].append({"id": "cpu_rail", "source": "x", "unit": "J", "read_as": "x",
                                          "cite": ["RL-149 §2.6"]})
        self.refused(lambda: lm.validate_manifest(doc), "reads exactly")
        doc = draft()
        doc["energy"]["per_leg_energy_in_output"] = True
        self.refused(lambda: lm.validate_manifest(doc), "per_leg_energy_in_output")

    def test_leg_types_and_never_read(self):
        doc = draft()
        doc["reads"]["leg_types_never"].remove("T")
        self.refused(lambda: lm.validate_manifest(doc), "never reads type T (RL-166 Q14)")
        doc = draft()
        doc["reads"]["leg_types_read"].append("T")
        self.refused(lambda: lm.validate_manifest(doc), "both read and never read")
        doc = draft()
        doc["reads"]["never_read"] = [x for x in doc["reads"]["never_read"] if x["id"] != "type_T"]
        self.refused(lambda: lm.validate_manifest(doc), "carries type_T (RL-166 Q14: the type-T legs)")
        for nid in sorted(lm.REQUIRED_NEVER_READ_IDS["interim"]):          # Sol 7 / Mythos 11: the complete list
            doc = draft()
            doc["reads"]["never_read"] = [x for x in doc["reads"]["never_read"] if x["id"] != nid]
            self.refused(lambda: lm.validate_manifest(doc), f"reads.never_read: carries {nid}")
        doc = draft()
        doc["reads"]["never_read"] = [x for x in doc["reads"]["never_read"] if x["id"] == "type_T"]
        problems = self.refused(lambda: lm.validate_manifest(doc), "carries hp01_energy")
        self.assertGreaterEqual(len([p for p in problems if "reads.never_read: carries" in p]), 8)

    def test_freezes_custody_review(self):
        doc = draft()
        doc["freeze2"]["refit_on_qualification"] = True
        self.refused(lambda: lm.validate_manifest(doc), "refit_on_qualification")
        doc = draft()
        doc["freeze2"]["commit_before"].remove("qualification_leg_runs")
        self.refused(lambda: lm.validate_manifest(doc), "freeze2.commit_before")
        doc = draft()
        doc["freeze1"]["committed_before"] = "the interim look"
        self.refused(lambda: lm.validate_manifest(doc), "freeze1.committed_before")
        doc = draft()
        doc["freeze1"]["ledger_pointer"] = "BLOCK-QUEUE.json points at it"
        self.refused(lambda: lm.validate_manifest(doc), "LOOKS.json")
        doc = draft()
        doc["custody"]["seats"] = 2
        self.refused(lambda: lm.validate_manifest(doc), "seats 1")
        doc = draft()
        doc["review"]["paper_bound"] = False
        self.refused(lambda: lm.validate_manifest(doc), "paper_bound")

    def test_blocks_and_phases(self):
        doc = draft()
        doc["reads"]["blocks"].append({"block_id": "qual-01", "phase": "qualification", "role": "fit",
                                       "kit_sha256": None, "spans": "all_desk_final", "cite": ["RL-165 §8.1"]})
        problems = self.refused(lambda: lm.validate_manifest(doc), "out of phase")
        self.assertTrue(any("never reads qual-01" in p for p in problems))
        doc = draft()
        next(b for b in doc["reads"]["blocks"] if b["block_id"] == "hp-01")["role"] = "fit"
        self.refused(lambda: lm.validate_manifest(doc), "never in the fit")
        doc = draft()
        doc["reads"]["blocks"].append({"block_id": "ctl-01", "phase": "extension", "role": "describe",
                                       "kit_sha256": None, "spans": "desk_final_if_any", "cite": ["RL-149 §2.6"]})
        self.refused(lambda: lm.validate_manifest(doc), "never reads ctl-01")
        doc = draft()
        doc["reads"]["blocks"] = [b for b in doc["reads"]["blocks"] if b["block_id"] != "dev-05"]
        self.refused(lambda: lm.validate_manifest(doc), "dev-05 is waited for but not read")
        doc = draft()
        next(b for b in doc["reads"]["blocks"] if b["block_id"] == "reserve-01")["serves_phase"] = "qualification"
        self.refused(lambda: lm.validate_manifest(doc), "serves_phase 'development'")
        doc = draft()
        next(b for b in doc["reads"]["blocks"] if b["block_id"] == "hp-01")["spans"] = "all_desk_final"
        self.refused(lambda: lm.validate_manifest(doc), "does not wait for hp-01")
        doc = draft()
        next(b for b in doc["reads"]["blocks"] if b["block_id"] == "dev-03")["spans"] = "desk_final_if_any"
        self.refused(lambda: lm.validate_manifest(doc), "the look waits for dev-03")
        doc = draft()
        doc["when"]["after_desk_final"].append("hp-01")
        self.refused(lambda: lm.validate_manifest(doc), "does not wait for hp-01")
        doc = draft()
        doc["reads"]["attempts"] = "all"
        self.refused(lambda: lm.validate_manifest(doc), "accepted_only")

    def test_code_paths_stay_in_the_repository(self):
        for bad in ("/Users/x/night-align/fit.py", "../scratch/fit.py", "joulewise/cadence_looks/fit.csv"):
            doc = finalize(draft())
            doc["fit"]["code"][0]["path"] = bad
            self.refused(lambda: lm.validate_manifest(doc, final=True), "repository-relative")


class Roster(Base):
    def setUp(self):
        self.doc = finalize(draft())

    def test_resolves_desk_final_sealed_in_phase_spans(self):
        roster = lm.resolve_roster(self.doc, ledger(), "a" * 64)
        ids = [r["span_id"] for r in roster]
        self.assertIn("dev-01-s04b", ids)
        self.assertNotIn("qual-01-s01", ids)
        self.assertEqual({r["role"] for r in roster if r["block_id"] == "hp-01"}, {"describe"})

    def test_the_ledger_carries_this_manifest(self):
        self.refused(lambda: lm.resolve_roster(self.doc, ledger(), "b" * 64), "another manifest hash")
        led = ledger()
        led["look_manifest"]["look_id"] = "lm-qual-01"
        self.refused(lambda: lm.resolve_roster(self.doc, led, "a" * 64), "is for 'lm-qual-01'")
        led = ledger()
        del led["look_manifest"]
        self.refused(lambda: lm.resolve_roster(self.doc, led), "missing key 'look_manifest'")

    def test_unsealed_spans_are_refused(self):
        led = ledger()
        led["spans"][1]["energy_seal"] = "opened"
        self.refused(lambda: lm.resolve_roster(self.doc, led), "dev-02-s01: unsealed: its energy seal is broken")
        led = ledger(reads=[{"read_id": "early", "spans": ["dev-03-s01"], "cite": ["RL-149 §2.6"]}])
        self.refused(lambda: lm.resolve_roster(self.doc, led), "dev-03-s01: unsealed: energy read early")

    def test_out_of_phase_spans_are_refused(self):
        led = ledger()
        led["spans"][0]["phase"] = "qualification"
        self.refused(lambda: lm.resolve_roster(self.doc, led), "dev-01-s01: out of phase")
        doc = copy.deepcopy(self.doc)
        doc["reads"]["blocks"][0]["spans"] = ["dev-01-s01", "qual-01-s01"]
        self.refused(lambda: lm.resolve_roster(doc, ledger()), "qual-01-s01: belongs to qual-01, not dev-01")
        led = ledger()
        led["spans"][5]["phase"] = "development"   # hp-01 recorded as development
        self.refused(lambda: lm.resolve_roster(self.doc, led), "hp-01-s01: out of phase")

    def test_waited_blocks_must_be_desk_final_and_present(self):
        led = ledger()
        led["spans"][4]["desk_final"] = False
        self.refused(lambda: lm.resolve_roster(self.doc, led), "dev-05-s01: not desk-final")
        doc = copy.deepcopy(self.doc)
        doc["reads"]["blocks"][1]["spans"] = ["dev-02-s09"]
        self.refused(lambda: lm.resolve_roster(doc, ledger()), "dev-02-s09: not in the span ledger")
        led = ledger(spans=[s for s in ledger()["spans"] if s["block_id"] != "dev-04"])
        self.refused(lambda: lm.resolve_roster(self.doc, led), "dev-04: no span of this block")

    def test_hp01_and_reserve_are_not_waited_for(self):
        led = ledger()
        led["spans"][5]["desk_final"] = False                       # hp-01 still running: skipped
        led["spans"].append({"span_id": "reserve-01-s01", "block_id": "reserve-01", "phase": "reserve",
                             "serves_phase": "development", "desk_final": True, "energy_seal": "sealed",
                             "t0_local_date": "2026-11-18"})
        led["spans"].append({"span_id": "reserve-01-s02", "block_id": "reserve-01", "phase": "reserve",
                             "serves_phase": "qualification", "desk_final": True, "energy_seal": "sealed",
                             "t0_local_date": "2026-11-20"})
        led["spans"].append({"span_id": "reserve-01-s03", "block_id": "reserve-01", "phase": "reserve",
                             "serves_phase": "development", "desk_final": False, "energy_seal": "sealed",
                             "t0_local_date": "2026-11-18"})
        ids = {r["span_id"]: r for r in lm.resolve_roster(self.doc, led)}
        self.assertNotIn("hp-01-s01", ids)
        self.assertIn("reserve-01-s01", ids)
        self.assertEqual(ids["reserve-01-s01"]["t0_local_date"], "2026-11-18")   # its own day (RL-166 Q13)
        self.assertNotIn("reserve-01-s02", ids)
        self.assertNotIn("reserve-01-s03", ids)
        led["spans"][0]["energy_seal"] = "opened"
        led["spans"][-3]["energy_seal"] = "opened"
        self.refused(lambda: lm.resolve_roster(self.doc, led), "reserve-01-s01: unsealed")

    def test_fewer_than_three_fit_days_is_refused(self):
        led = ledger()
        for s in led["spans"]:
            s["t0_local_date"] = "2026-11-16"
        self.refused(lambda: lm.resolve_roster(self.doc, led), "covers 1 calendar day")

    def test_a_malformed_ledger_is_refused(self):
        led = ledger()
        del led["spans"][0]["energy_seal"]
        self.refused(lambda: lm.resolve_roster(self.doc, led), "missing key 'energy_seal'")


class LookLedger(Base):
    def setUp(self):
        self.repo = tmpdir(self, "lm-looks-")
        (self.repo / "docs/process/cadence/looks").mkdir(parents=True)
        self.man = self.repo / "docs/process/cadence/looks/lm-interim-01.json"
        doc = draft()
        for rule in doc["inclusion"]["rules"]:
            if "code" in rule:
                rule["code"]["sha256"] = lm.PENDING_CODE                      # as if inclusion_34.py were unwritten
        doc["fit"]["code"][1]["sha256"] = lm.PENDING_CODE
        doc["fit"]["code"][0]["sha256"] = lm.PENDING_CODE                      # as if fit_interim.py were unwritten
        self.man.write_text(json.dumps(doc), encoding="utf-8")
        self.row = {"look_id": "lm-interim-01", "manifest_path": "docs/process/cadence/looks/lm-interim-01.json",
                    "sha256": lm.sha256_file(self.man), "status": "draft"}

    def doc(self, **row):
        return {"schema": lm.LOOK_LEDGER_SCHEMA, "looks": [{**self.row, **row}]}

    def test_valid(self):
        lm.validate_look_ledger(self.doc(), self.repo)

    def test_refusals(self):
        self.refused(lambda: lm.validate_look_ledger(self.doc(sha256="0" * 64), self.repo), "sha256 differs")
        self.refused(lambda: lm.validate_look_ledger(self.doc(status="committed"), self.repo), "not committed")
        self.refused(lambda: lm.validate_look_ledger(self.doc(status="open"), self.repo), "status: one of")
        self.refused(lambda: lm.validate_look_ledger(self.doc(look_id="lm-other"), self.repo), "look_id is")
        self.refused(lambda: lm.validate_look_ledger(self.doc(manifest_path="/abs/x.json"), self.repo),
                     "repository-relative")
        bad = self.doc()
        bad["looks"].append(dict(bad["looks"][0]))
        self.refused(lambda: lm.validate_look_ledger(bad, self.repo), "unique")

    def test_pin_fills_existing_files_and_the_ledger(self):
        (self.repo / RULE34).parent.mkdir(parents=True, exist_ok=True)
        (self.repo / RULE34).write_text("X = 1\n", encoding="utf-8")
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(cli.main(["pin", str(self.man), "--repo", str(self.repo)]), 0)
            self.assertEqual(json.loads(self.man.read_text())["inclusion"]["rules"][2]["code"]["sha256"],
                             lm.PENDING_CODE)                                  # nothing written without --write
            self.assertEqual(cli.main(["pin", str(self.man), "--repo", str(self.repo), "--write"]), 0)
        doc = json.loads(self.man.read_text())
        self.assertEqual(doc["inclusion"]["rules"][2]["code"]["sha256"], lm.sha256_file(self.repo / RULE34))
        self.assertEqual(doc["fit"]["code"][0]["sha256"], lm.PENDING_CODE)     # fit_interim.py absent here
        looks = lm.validate_look_ledger(lm.load_json(self.repo / lm.LOOK_LEDGER_PATH), self.repo)
        self.assertEqual(looks["looks"][0]["sha256"], lm.sha256_file(self.man))
        doc["status"] = "committed"
        self.man.write_text(json.dumps(doc), encoding="utf-8")
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(cli.main(["pin", str(self.man), "--repo", str(self.repo), "--write"]), 1)


class RepoCheck(Base):
    def make_repo(self, fit_src="def fit(rows):\n    return rows['start_tf08']\n", runner_src="import json\n"):
        tmp = tmpdir(self, "lm-repo-")
        files = {FIT: fit_src, RULE34: "def judge(stamps):\n    return True\n",
                 lm.STEP3_PATH: (REPO / lm.STEP3_PATH).read_text(encoding="utf-8"),
                 ADAPTER: "from joulewise.cadence_looks import step3_energy_ratios\n", RUNNER: "X = 1\n",
                 "scripts/cadence_legs_runner.py": runner_src,
                 "docs/process/cadence/looks/lm-interim-01.output.schema.json": "{}\n",
                 "docs/process/cadence/looks/lm-interim-01.stage1.schema.json": "{}\n"}
        doc0 = draft()
        for ref in doc0["fit"]["dependencies"] + doc0["fit"]["code"] + \
                [{"path": p} for p in lm.EVIDENCE]:
            files.setdefault(ref["path"], (REPO / ref["path"]).read_text(encoding="utf-8"))
        for rel, src in files.items():
            (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp / rel).write_text(src, encoding="utf-8")
        shas = {rel: lm.sha256_file(tmp / rel) for rel in files}
        kit = {"frozen": {"commit": "a" * 40, "paths": {"scripts/cadence_legs_runner.py": "0" * 64}}, "looks": []}
        kp = tmp / "kit.json"
        kp.write_text(json.dumps(kit), encoding="utf-8")
        return tmp, finalize(draft(), shas), kp

    def test_clean_repo_passes(self):
        tmp, doc, kp = self.make_repo()
        lm.validate_manifest(doc, final=True)
        lm.check_repo(doc, tmp, [kp])

    def test_hash_mismatch_and_missing_file(self):
        tmp, doc, kp = self.make_repo()
        (tmp / FIT).write_text("def fit(rows):\n    return 0\n", encoding="utf-8")
        self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "sha256 differs")
        (tmp / FIT).unlink()
        self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "is not in the repository")

    def test_a_draft_may_pin_a_file_from_another_branch(self):
        tmp, doc, kp = self.make_repo()
        (tmp / FIT).unlink()
        doc["status"] = "draft"
        warnings = lm.check_repo(doc, tmp, [kp])
        self.assertTrue(any(FIT in w and "draft pin" in w for w in warnings), warnings)
        self.refused(lambda: lm.check_repo(doc, tmp, [kp], final=True), "is not in the repository")

    def test_a_frozen_path_that_imports_look_code_is_refused(self):
        for src in ("from joulewise.cadence_looks import fit_interim\n", "import joulewise.cadence_looks.manifest\n",
                    "from joulewise.cadence_looks.inclusion_34 import judge\n"):
            tmp, doc, kp = self.make_repo(runner_src=src)
            self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "never import look code")

    def test_look_code_as_a_kit_frozen_path_is_refused(self):
        tmp, doc, kp = self.make_repo()
        kit = json.loads(kp.read_text())
        kit["frozen"]["paths"][RULE34] = "0" * 64
        kp.write_text(json.dumps(kit))
        self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "must stay outside every leg kit")
        kit["looks"] = [{"look_id": "x", "after_legs": 1, "fit": {"path": FIT}}]
        kp.write_text(json.dumps(kit))
        self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "looks must stay []")

    def test_look_code_that_reads_condition_is_refused(self):
        for src in ("def fit(cfg):\n    return cfg['condition']\n", "def fit(b):\n    return b.condition\n",
                    "FORBIDDEN = 1\ndef fit(cfg):\n    return cfg.get('condition')\n"):
            tmp, doc, kp = self.make_repo(fit_src=src)
            self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "reads a 'condition' field")

    def test_a_deny_list_that_refuses_condition_is_not_a_read(self):
        tmp, doc, kp = self.make_repo(fit_src='FORBIDDEN_FIELDS = ("condition", "slot")\nDENY_KEYS = {"condition"}\n')
        lm.check_repo(doc, tmp, [kp])


class OpensNoEnergy(Base):
    def test_the_validator_opens_only_manifest_ledgers_kits_and_code(self):
        tmp = tmpdir(self, "lm-custody-")
        custody = tmp / "custody" / "dev-01-s01" / "legs" / "L001" / "runtime"
        custody.mkdir(parents=True)
        for name in ("power_trace.csv", "rich_telemetry.jsonl", "align_thermal.jsonl"):
            (custody / name).write_text("SENTINEL\n", encoding="utf-8")
        (tmp / "custody" / "dev-01-s01" / "hazards").mkdir()
        (tmp / "custody" / "dev-01-s01" / "hazards" / "stream-0001.jsonl").write_text("SENTINEL\n")
        led_path = tmp / "ledger.json"
        led_path.write_text(json.dumps(ledger()), encoding="utf-8")
        opened = []
        real_open = builtins.open

        def spy(file, *a, **k):
            opened.append(str(file))
            return real_open(file, *a, **k)
        kits = sorted(str(p) for p in (REPO / "docs/process/cadence/kits").glob("*.json"))
        with unittest.mock.patch.object(builtins, "open", spy), unittest.mock.patch.object(io, "open", spy):
            doc = lm.load_json(MANIFEST)
            lm.validate_manifest(doc)
            lm.check_repo(doc, REPO, kits)
            lm.validate_look_ledger(lm.load_json(LOOK_LEDGER), REPO)
            lm.resolve_roster(finalize(doc), lm.load_json(led_path))
        self.assertTrue(opened)
        for path in opened:
            self.assertNotIn(str(tmp / "custody"), path)
            in_repo_code = path.startswith(str(REPO)) and (path.endswith((".py", ".json")) or
                                                           path in {str(REPO / e) for e in lm.EVIDENCE})
            self.assertTrue(in_repo_code or path == str(led_path), path)
            self.assertFalse(re.search(r"(power_trace\.csv|rich_telemetry\.jsonl|stream-\d+\.jsonl|\.plist$)", path),
                             path)


class SchemaCopy(Base):
    def test_the_json_schema_matches_the_validator(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), lm.TOP_KEYS)
        self.assertEqual(set(schema["properties"]), lm.TOP_KEYS)
        self.assertEqual(set(schema["$defs"]["predictor"]["enum"]), lm.ALLOWED_PREDICTORS)
        self.assertEqual(set(schema["$defs"]["channel"]["enum"]), lm.ENERGY_CHANNELS)
        self.assertEqual(set(schema["$defs"]["leg_type"]["enum"]), lm.LEG_TYPES)
        self.assertEqual(schema["properties"]["schema"]["const"], lm.SCHEMA)

    def test_every_schema_file_is_json(self):
        for p in LOOKS.glob("*.json"):
            json.loads(p.read_text(encoding="utf-8"))

    def test_the_manifest_validates_against_the_json_schema_when_available(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed; the Python validator is authoritative")
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        jsonschema.validate(draft(), schema)
        jsonschema.validate(finalize(draft()), schema)


class Assemble(Base):
    """assemble on a pinned copy of the look's files (tests/cadence/look_minirepo.py), run as a file under -I. The
    three inputs are the smallest documents their pinned schemas admit (tests/cadence/look_fixtures.py), carrying
    the provenance a real run records: this manifest's sha256 and the pinned hashes of the code each stage runs."""

    ROSTER = "0" * 64

    def setUp(self):
        from tests.cadence import look_minirepo as mr
        from tests.cadence.look_fixtures import minimal
        from joulewise.cadence_looks import schema_check as sc
        self.mr, self.minimal, self.sc = mr, minimal, sc
        self.mini = mr.mini_repo(self)
        self.d = tmpdir(self, "lm-asm-")
        self.s1 = self.d / "stage1.json"
        self.s1_schema = json.loads((self.mini / LOOKS.relative_to(REPO) / "lm-interim-01.stage1.schema.json").read_text())
        self.out_schema = json.loads((self.mini / LOOKS.relative_to(REPO) / "lm-interim-01.output.schema.json").read_text())
        leg = minimal(self.s1_schema["properties"]["legs"]["items"], self.s1_schema)
        self.legs = [dict(leg, leg_key="dev-03-s01/L001", cell_prompt_tokens=2000, prefill_tokens=2200),
                     dict(leg, leg_key="dev-03-s01/L002", cell_prompt_tokens=10000, prefill_tokens=10100)]
        self.write_stage1()

    def pins(self):
        man = json.loads((self.mini / self.mr.MANIFEST).read_text())
        return lm.sha256_file(self.mini / self.mr.MANIFEST), {p: sha for _, p, sha in lm.code_refs(man)}, man

    def write_stage1(self, **changes):
        msha, pins, man = self.pins()
        stage1 = self.minimal(self.s1_schema)
        stage1.update(manifest_sha256=msha, synthetic=True, allow_draft=True, legs=self.legs,
                      code_sha256={FIT: pins[FIT], RUNNER: pins[RUNNER], "input:roster_sha256": self.ROSTER})
        stage1.update(changes)
        self.stage1 = stage1
        self.s1.write_text(json.dumps(stage1) + "\n")
        h = hashlib.sha256(self.s1.read_bytes()).hexdigest()
        stage2 = (set(cli.STAGE2_CODE) | {d["path"] for d in man["fit"]["dependencies"]}) - \
            {"configs/align/v4/r1_runtime.json"}
        self.fit = self.minimal(self.sc.sub_schema(self.out_schema, "fit_output"))
        self.fit.update(stage1_sha256=h, manifest_sha256=msha, allow_draft=True, numpy_version="2.5.4",
                        code_sha256={k: pins[k] for k in sorted(stage2)})
        self.step3 = self.minimal(self.sc.sub_schema(self.out_schema, "step3_output"))
        self.step3.update(stage1_sha256=h, manifest_sha256=msha, allow_draft=True, synthetic=True,
                          code_sha256={ADAPTER: pins[ADAPTER], lm.STEP3_PATH: pins[lm.STEP3_PATH]})
        self.dump()
        return h

    def undraft(self):
        """The inputs as a run without --allow-draft writes them, on the copy's current (committed) manifest."""
        self.write_stage1(allow_draft=False)
        self.fit["allow_draft"] = self.step3["allow_draft"] = False
        self.dump()
        return hashlib.sha256(self.s1.read_bytes()).hexdigest()

    def dump(self):
        (self.d / "fit.json").write_text(json.dumps(self.fit))
        (self.d / "step3.json").write_text(json.dumps(self.step3))

    def run_(self, *extra):
        return self.mr.py(self.mini, "scripts/cadence_look_manifest.py", "assemble",
                          "--manifest", self.mini / self.mr.MANIFEST, "--stage1", self.s1, "--fit", self.d / "fit.json",
                          "--step3", self.d / "step3.json", "--analyst-seat", "test", "--out", self.d / "out.json", *extra)

    def refused_run(self, fragment, *extra):
        r = self.run_(*extra)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(fragment, r.stdout)
        self.assertFalse((self.d / "out.json").exists())
        return r

    def test_assemble_writes_the_schema_shape(self):
        r = self.run_("--allow-draft")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = json.loads((self.d / "out.json").read_text())
        self.assertEqual(self.sc.errors(out, self.out_schema), [])
        self.assertEqual(set(out), set(self.out_schema["required"]))
        self.assertNotIn("high_power_table", out)                                     # RL-167 §3
        self.assertNotIn("hp01_table", out["decisions"])
        self.assertEqual(out["decisions"]["drift_tripwire"], "within")
        self.assertEqual(out["realized_prompt_tokens"],                                 # RL-158 Q5, > 5 %
                         [{"leg_key": "dev-03-s01/L001", "nominal": 2000, "realized": 2200}])
        self.assertEqual(out["disclosure"]["holds_cleared"], [])
        self.assertEqual((out["allow_draft"], out["synthetic"]), (True, True))         # Mythos N2
        self.assertEqual(out["soak_retries"], self.stage1["soak_retries"])              # RL-172a
        r = self.run_("--allow-draft", "--hp-table", self.d / "fit.json")               # the option is gone
        self.assertEqual(r.returncode, 2)
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as so:          # validate --output
            rc = cli.main(["validate", str(self.mini / self.mr.MANIFEST), "--output", str(self.d / "out.json")])
        self.assertEqual(rc, 0, so.getvalue())
        out["synthetic"] = False
        (self.d / "out2.json").write_text(json.dumps(out))
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as so:
            rc = cli.main(["validate", str(self.mini / self.mr.MANIFEST), "--output", str(self.d / "out2.json")])
        self.assertEqual(rc, 1)
        self.assertIn("made under --allow-draft on input that is not synthetic", so.getvalue())

    def test_assemble_refuses_code_that_is_not_the_pin(self):
        """Mythos 3: the hashes the fit recorded are compared with the manifest's pins."""
        self.fit["code_sha256"][FIT] = "f" * 64
        self.dump()
        self.refused_run("which is not the manifest's pin", "--allow-draft")
        f = self.mini / "joulewise/cadence_looks/step3_roster.py"
        f.write_text(f.read_text() + "\n# edited\n")
        self.write_stage1()
        self.refused_run("step3_roster.py sha256 differs from the pin", "--allow-draft")

    def test_the_fit_records_exactly_the_pinned_stage(self):
        """Sol N2: a fit that recorded fewer files, extra files, or ran under another manifest is refused."""
        dep = "joulewise/external/km003c_parse.py"
        del self.fit["code_sha256"][dep]
        self.dump()
        self.refused_run(f"the fit does not record {dep}'s hash", "--allow-draft")
        self.write_stage1()
        self.fit["code_sha256"][ADAPTER] = self.pins()[1][ADAPTER]
        self.dump()
        self.refused_run(f"records {ADAPTER}, which the pinned stage does not run", "--allow-draft")
        self.write_stage1()
        self.fit["manifest_sha256"] = "e" * 64            # the two-manifest case: same code, another manifest
        self.dump()
        self.refused_run("the fit was made under manifest eeeeeeeeeeee, not this one", "--allow-draft")

    def test_inputs_must_pass_their_schemas(self):
        """Sol N3: an unknown field (here, a per-leg energy payload) is refused before anything is written."""
        self.fit["per_leg_joules"] = {"dev-03-s01/L001": 1.0}
        self.dump()
        self.refused_run("the fit does not pass its schema: $.per_leg_joules: not allowed", "--allow-draft")
        self.write_stage1()
        self.step3["cells"] = [{"cell": 2000, "joules": [1.0]}]
        self.dump()
        self.refused_run("step 3 does not pass its schema", "--allow-draft")
        self.write_stage1(legs=[dict(self.legs[0], energy_j=1.0)])
        self.refused_run("stage 1 does not pass its schema: $.legs[0].energy_j: not allowed", "--allow-draft")

    def test_allow_draft_is_synthetic_only_and_recorded(self):
        """Mythos N2: --allow-draft on input that is not synthetic, or a draft input without it, is refused."""
        self.write_stage1(synthetic=False)
        self.refused_run("--allow-draft on a stage-1 file that is not synthetic", "--allow-draft")
        self.mr.commit(self.mini)
        h = self.write_stage1()                     # made under --allow-draft, on the committed manifest
        self.mr.commit(self.mini, stage1_sha256=h, roster_sha256=self.ROSTER)
        self.refused_run("made under --allow-draft; a real output cannot use it")

    def test_assemble_needs_stage1_committed_unless_draft(self):
        """Mythos 8 / Sol N1: the stage-1 row is read from the committed, published LOOKS.json."""
        self.mr.commit(self.mini)
        h = self.undraft()
        self.refused_run("stage 1 is not committed")
        self.mr.commit(self.mini, stage1_sha256=h, roster_sha256=self.ROSTER, git_commit_it=False)
        self.refused_run("differs from the one committed at HEAD")      # a loose ledger (Sol N1)
        self.mr.git_commit(self.mini, "stage 1", publish=False)
        self.refused_run("is not on")                                   # committed, not on the shared ref
        self.mr.git(self.mini, "update-ref", "refs/remotes/origin/main", "HEAD")
        r = self.run_()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = json.loads((self.d / "out.json").read_text())
        self.assertEqual((out["allow_draft"], out["synthetic"]), (False, True))
        self.mr.commit(self.mini, stage1_sha256=h, roster_sha256="9" * 64)   # another roster
        (self.d / "out.json").unlink()
        self.refused_run("is not the roster the stage-1 file records")

    def test_held_flags_need_their_clearing_ruling(self):
        """RL-166c §2 row 7 and RL-166 Q8 (Mythos 8): P-4, R-20 and the five tripwires."""
        self.assertEqual(self.run_("--allow-draft", "--hold-cleared", "meter_clock.to_research_lead=RL-170").returncode, 1)
        trip = copy.deepcopy(self.minimal(self.s1_schema)["tripwires"])
        trip["any"] = True
        onsets = dict(self.minimal(self.s1_schema)["onsets_before_116_s"], to_research_lead=True, total=2)
        self.write_stage1(tripwires=trip, onsets_before_116_s=onsets, legs=[])
        r = self.run_("--allow-draft")
        self.assertEqual(r.returncode, 1)
        self.assertIn("onsets_before_116_s.to_research_lead true: stage 2 was held", r.stdout)
        self.assertIn("tripwires.any true: stage 2 was held", r.stdout)
        r = self.run_("--allow-draft", "--hold-cleared", "onsets_before_116_s.to_research_lead=RL-170",
                      "--hold-cleared", "tripwires.any=not-a-ruling")
        self.assertEqual(r.returncode, 1)
        r = self.run_("--allow-draft", "--hold-cleared", "onsets_before_116_s.to_research_lead=RL-170",
                      "--hold-cleared", "tripwires.any=RL-171")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = json.loads((self.d / "out.json").read_text())
        self.assertEqual(out["disclosure"]["holds_cleared"],
                         [{"flag": "onsets_before_116_s.to_research_lead", "cleared_by": "RL-170"},
                          {"flag": "tripwires.any", "cleared_by": "RL-171"}])
        self.step3["stage1_sha256"] = "0" * 64
        self.dump()
        self.assertEqual(self.run_("--allow-draft", "--hold-cleared", "onsets_before_116_s.to_research_lead=RL-170",
                                   "--hold-cleared", "tripwires.any=RL-171").returncode, 1)


class ColdSeatFixes(Base):
    def test_dictated_texts_are_pinned_verbatim(self):
        """Sol 7 / Mythos 11: one character changed in any pinned text is refused."""
        texts = lm.verbatim_texts(draft())
        self.assertEqual(set(texts), set(lm.VERBATIM_SHA256))
        for name in sorted(lm.VERBATIM_SHA256):
            doc = draft()
            section, key = name.rsplit(".", 1) if name.count(".") >= 2 else (None, None)
            node = None
            if name.startswith("fit.stated_limits."):
                node = next(x for x in doc["fit"]["stated_limits"] if x["id"] == name.split(".")[2]); field = "text"
            elif name.startswith("freeze2.deferred_rules."):
                node = next(x for x in doc["freeze2"]["deferred_rules"] if x["id"] == name.split(".")[2]); field = "rule"
            elif name.startswith("reads.never_read."):
                node = next(x for x in doc["reads"]["never_read"] if x["id"] == name.split(".")[2]); field = "what"
            elif name.startswith("stages.stage2.holds."):
                node = next(x for x in doc["stages"]["stage2"]["holds"] if x["flag"] == name.split("holds.", 1)[1])
                field = "rule"
            else:
                parts = name.split(".")
                node = doc
                for p_ in parts[:-1]:
                    node = node[p_]
                field = parts[-1]
            node[field] = node[field].replace("0", "1", 1) if "0" in node[field] else node[field] + "."
            self.refused(lambda: lm.validate_manifest(doc), f"{name}: differs from the ruled text")

    def test_old_figures_and_withdrawn_form_are_refused(self):
        doc = draft()
        pc = next(x for x in doc["fit"]["stated_limits"] if x["id"] == "partial_correction")
        pc["text"] = pc["text"].replace("0.84 to 0.96", "0.85 to 0.95")
        self.refused(lambda: lm.validate_manifest(doc), "partial_correction: differs from the ruled text")
        doc = draft()
        doc["fit"]["onset"]["estimable_when"] = "always"
        self.refused(lambda: lm.validate_manifest(doc), "fit.onset.estimable_when: differs")
        doc = draft()
        doc["fit"]["heat_term"]["form"] = "d * m * (k . z) + delta * w, w the overlap with [tau_hat, inf)."
        self.refused(lambda: lm.validate_manifest(doc), "fit.heat_term.form: differs")

    def test_evidence_is_cited_and_hashed(self):
        doc = draft()
        pr = next(x for x in doc["fit"]["stated_limits"] if x["id"] == "qualified_pass_rate")
        pr["note"] = pr["note"].replace(list(lm.EVIDENCE.values())[0], "0" * 64)
        self.refused(lambda: lm.validate_manifest(doc), "qualified_pass_rate.note: cites")
        tmp, doc2, kp = RepoCheck.make_repo(self)
        ev = tmp / list(lm.EVIDENCE)[0]
        ev.write_text(ev.read_text() + "x")
        self.refused(lambda: lm.check_repo(doc2, tmp, [kp]), "the evidence the dictated sentences cite")

    def test_q11_fallback_and_ruled_threshold(self):
        doc = draft()
        drift = next(d for d in doc["decisions"] if d["id"] == "drift_tripwire")
        self.assertEqual((drift["threshold"], drift["ruled_threshold"]), (0.04, 0.08))       # Sol 6
        self.assertIn("pending the research lead's disposition", drift["pending"])
        drift["threshold"] = 0.08
        del drift["pending"], drift["ruled_threshold"]
        lm.validate_manifest(doc)                                                         # the ruled value
        drift["threshold"] = 0.05
        self.refused(lambda: lm.validate_manifest(doc), "threshold 0.08, or the fallback 0.04")
        drift["threshold"] = 0.04
        self.refused(lambda: lm.validate_manifest(doc), "carries ruled_threshold 0.08 and either the pending")
        # Mythos N10: a committed manifest carries the disposing ruling, never the pending note
        doc = finalize(draft())
        drift = next(d for d in doc["decisions"] if d["id"] == "drift_tripwire")
        self.assertEqual(lm.validate_manifest(doc, final=True), [])
        drift["pending"] = "pending the research lead's disposition"
        self.refused(lambda: lm.validate_manifest(doc, final=True), "a committed manifest carries no pending")
        del drift["disposed_by"]
        self.refused(lambda: lm.validate_manifest(doc, final=True), "a committed manifest carries no pending")
        del drift["pending"]
        self.refused(lambda: lm.validate_manifest(doc, final=True), "either the pending disposition or the disposing")
        drift["disposed_by"] = "the lead said so"
        self.refused(lambda: lm.validate_manifest(doc, final=True), "drift_tripwire.disposed_by: the disposing ruling")

    def test_soak_retries_print_is_required(self):
        """RL-172a: the look prints the retried soaks by refusal kind; the receipt read is operational."""
        doc = draft()
        doc["outputs"]["prints"] = [p for p in doc["outputs"]["prints"] if p["id"] != "soak_retries"]
        self.refused(lambda: lm.validate_manifest(doc), "the interim look prints soak_retries")
        doc = draft()
        doc["rulings"].remove("RL-172a")
        self.refused(lambda: lm.validate_manifest(doc), "rulings: must cite 'RL-172a'")
        doc = draft()
        row = next(x for x in doc["reads"]["custody_files"] if "soak_attempts" in x["basename"])
        self.assertEqual((row["stage"], row["carries"].split(":")[0]), ("inclusion", "operational"))
        for name in ("stage1", "output"):
            schema = json.loads((LOOKS / f"lm-interim-01.{name}.schema.json").read_text())
            self.assertIn("soak_retries", schema["required"])

    def test_hp01_table_is_out(self):
        """Sol 5 / Mythos 5: RL-167 §3."""
        doc = draft()
        self.assertNotIn("high_power_table", {p["id"] for p in doc["outputs"]["prints"]})
        doc["outputs"]["prints"].append({"id": "high_power_table", "what": "x", "cite": ["RL-157 §1"]})
        self.refused(lambda: lm.validate_manifest(doc), "high_power_table is not printed by this look")
        out = json.loads((LOOKS / "lm-interim-01.output.schema.json").read_text())
        self.assertNotIn("high_power_table", out["properties"])
        self.assertNotIn("hp01_table", out["properties"]["decisions"]["properties"])
        self.assertIn("RL-167 §3", doc["rulings"])
        self.assertIn("RL-166a", doc["rulings"])

    def test_dependencies_are_pinned(self):
        """Mythos 3 / Sol 9: the DC-in decoder and its imports."""
        for dep in sorted(lm.REQUIRED_DEPENDENCIES["interim"]):
            doc = draft()
            doc["fit"]["dependencies"] = [x for x in doc["fit"]["dependencies"] if x["path"] != dep]
            self.refused(lambda: lm.validate_manifest(doc), f"fit.dependencies: pins {dep}")

    def test_holds_include_the_tripwires(self):
        doc = draft()
        doc["stages"]["stage2"]["holds"] = [h for h in doc["stages"]["stage2"]["holds"] if h["flag"] != "tripwires.any"]
        self.refused(lambda: lm.validate_manifest(doc), "holds stage 2 on tripwires.any")

    def test_looks_rows_record_the_hashes(self):
        """Mythos 8: a status needs its hashes; require_stage1_committed reads them from the committed ledger."""
        led = lm.load_json(LOOK_LEDGER)
        row = led["looks"][0]
        row["status"] = "stage1_committed"
        with self.assertRaises(lm.ManifestError) as ctx:
            lm.validate_look_ledger(led)
        self.assertTrue(any("needs stage1_sha256" in p for p in ctx.exception.problems))
        row.update(stage1_sha256="2" * 64, roster_sha256="3" * 64)
        lm.validate_look_ledger(led)
        row["output_sha256"] = "nothex"
        self.refused(lambda: lm.validate_look_ledger(led), "output_sha256: 64 hex or null")

    def test_require_stage1_committed_reads_git(self):
        """Sol N1: the row is read from LOOKS.json as committed at HEAD and published on the shared ref; a loose
        or unpublished ledger, a wrong hash, a wrong roster or a plain 'committed' row is refused."""
        from tests.cadence import look_minirepo as mr
        mini = mr.mini_repo(self)
        s1doc = {"code_sha256": {"input:roster_sha256": "3" * 64}}
        req = lambda sha="2" * 64, doc=s1doc: lm.require_stage1_committed(mini, "lm-interim-01", sha, stage1_doc=doc)
        mr.commit(mini)
        self.refused(req, "stage 1 is not committed")
        mr.commit(mini, stage1_sha256="2" * 64, roster_sha256="3" * 64, git_commit_it=False)
        self.refused(req, "differs from the one committed at HEAD")
        mr.git_commit(mini, "stage 1", publish=False)
        self.refused(req, "is not on")
        mr.git(mini, "update-ref", "refs/remotes/origin/main", "HEAD")
        req()
        self.refused(lambda: req("4" * 64), "names stage-1 sha256")
        self.refused(lambda: req(doc={"code_sha256": {"input:roster_sha256": "5" * 64}}), "is not the roster")
        led = json.loads((mini / lm.LOOK_LEDGER_PATH).read_text())
        led["looks"].append(dict(led["looks"][0]))                       # a duplicate row contradicts
        (mini / lm.LOOK_LEDGER_PATH).write_text(json.dumps(led, indent=2) + "\n")
        mr.git_commit(mini, "duplicate")
        with self.assertRaises(lm.ManifestError):
            req()

    def test_verify_pins(self):
        from tests.cadence import look_minirepo as mr
        mini = mr.mini_repo(self)
        m = mini / mr.MANIFEST
        lm.verify_pins(m, mini, allow_draft=True, running=[mini / "scripts/cadence_look_manifest.py"])
        self.refused(lambda: lm.verify_pins(m, mini), "LOOKS.json lists this look as 'draft', not committed")
        self.refused(lambda: lm.verify_pins(m, mini, allow_draft=True, running=[mini / "joulewise/schemas_x.py"]),
                     "runs but is not pinned")
        dep = mini / "joulewise/external/km003c_parse.py"
        dep.write_text(dep.read_text() + "\n# changed\n")
        self.refused(lambda: lm.verify_pins(m, mini, allow_draft=True), "km003c_parse.py sha256 differs from the pin")
        mini2 = mr.mini_repo(self)
        mr.commit(mini2)
        lm.verify_pins(mini2 / mr.MANIFEST, mini2)
        led = json.loads((mini2 / lm.LOOK_LEDGER_PATH).read_text())
        led["looks"][0]["sha256"] = "6" * 64
        (mini2 / lm.LOOK_LEDGER_PATH).write_text(json.dumps(led, indent=2) + "\n")
        mr.git_commit(mini2, "another manifest's row")
        self.refused(lambda: lm.verify_pins(mini2 / mr.MANIFEST, mini2), "does not name this manifest's sha256")

    def test_a_ledger_status_short_of_committed_is_refused(self):
        """Mythos N5: superseded (or any status but committed, stage1_committed, run, frozen) does not run."""
        from tests.cadence import look_minirepo as mr
        mini = mr.mini_repo(self)
        mr.commit(mini)
        led = json.loads((mini / lm.LOOK_LEDGER_PATH).read_text())
        for status, fragment in (("superseded", "lists this look as 'superseded', not committed"),
                                 ("approved", ".status: one of")):
            led["looks"][0]["status"] = status
            (mini / lm.LOOK_LEDGER_PATH).write_text(json.dumps(led, indent=2) + "\n")
            mr.git_commit(mini, status)
            self.refused(lambda: lm.verify_pins(mini / mr.MANIFEST, mini), fragment)

    def test_a_loaded_module_the_manifest_does_not_pin_is_named(self):
        """Mythos N6: each entry point refuses before writing when a repository module it loaded is unpinned."""
        import importlib.util
        import sys
        from tests.cadence import look_minirepo as mr
        mini = mr.mini_repo(self)
        doc = json.loads((mini / mr.MANIFEST).read_text())
        self.assertEqual(lm.unpinned_loaded_modules(doc, mini), [])
        extra = mini / "joulewise/extra_helper.py"
        extra.write_text("X = 1\n")
        spec = importlib.util.spec_from_file_location("lm_test_extra_helper", extra)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules["lm_test_extra_helper"] = mod
        self.addCleanup(sys.modules.pop, "lm_test_extra_helper", None)
        self.assertEqual(lm.unpinned_loaded_modules(doc, mini), ["joulewise/extra_helper.py (not pinned)"])
        doc["fit"]["dependencies"].append({"path": "joulewise/extra_helper.py", "sha256": "0" * 64})
        self.assertEqual(lm.unpinned_loaded_modules(doc, mini), ["joulewise/extra_helper.py (differs from the pin)"])

    def test_roster_out_writes_one_list(self):
        led = self_ledger = ledger(sha=lm.sha256_file(MANIFEST))
        d = tmpdir(self, "lm-roster-")
        lp, ro = d / "ledger.json", d / "roster.json"
        lp.write_text(json.dumps(led))
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO) as so:
            rc = cli.main(["validate", str(MANIFEST), "--span-ledger", str(lp), "--roster-out", str(ro)])
        self.assertEqual(rc, 0, so.getvalue())
        roster = json.loads(ro.read_text())
        self.assertIsInstance(roster, list)
        self.assertEqual({r["block_id"] for r in roster}, {"dev-01", "dev-02", "dev-03", "dev-04", "dev-05", "hp-01"})
        self.assertIn(f"sha256={lm.sha256_file(ro)}", so.getvalue())
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(cli.main(["validate", str(MANIFEST), "--roster-out", str(ro)]), 1)


if __name__ == "__main__":
    unittest.main()
