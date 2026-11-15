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
        doc["reads"]["never_read"] = [x for x in doc["reads"]["never_read"] if "type-T" not in x["what"]]
        self.refused(lambda: lm.validate_manifest(doc), "names the type-T legs")

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
            in_repo_code = path.startswith(str(REPO)) and path.endswith((".py", ".json"))
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
    def test_assemble_cross_checks_the_stage1_hash(self):
        d = tmpdir(self, "lm-asm-")
        s1 = d / "stage1.json"
        s1.write_text('{"schema": "joulewise.cadence_look_stage1.v1"}\n')
        h = hashlib.sha256(s1.read_bytes()).hexdigest()
        fit = {"schema": "joulewise.cadence_look_fit.v1", "stage1_sha256": h, "code_sha256": {"a.py": "1" * 64},
               "numpy_version": "2.5.4", "qualified_interim_half": {"verdict": "passes"}}
        step3 = {"schema": "joulewise.cadence_look_step3.v1", "stage1_sha256": h, "cells": [],
                 "tripwire": {"decision": "within"}}
        (d / "fit.json").write_text(json.dumps(fit))
        (d / "step3.json").write_text(json.dumps(step3))
        args = ["assemble", "--manifest", str(MANIFEST), "--stage1", str(s1), "--fit", str(d / "fit.json"),
                "--step3", str(d / "step3.json"), "--analyst-seat", "test", "--out", str(d / "out.json")]
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(cli.main(args), 0)
        out = json.loads((d / "out.json").read_text())
        schema = json.loads((LOOKS / "lm-interim-01.output.schema.json").read_text())
        self.assertEqual(set(out), set(schema["required"]))
        self.assertEqual(out["decisions"]["drift_tripwire"], "within")
        self.assertEqual(out["decisions"]["qualified_interim_half"], "passes")
        self.assertEqual(out["manifest_sha256"], lm.sha256_file(MANIFEST))
        self.assertIn("joulewise/cadence_looks/step3_roster.py", out["disclosure"]["code_sha256"])
        step3["stage1_sha256"] = "0" * 64
        (d / "step3.json").write_text(json.dumps(step3))
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(cli.main(args), 1)


class RL166b(Base):
    def test_stated_limits_and_deferred_rules_are_required(self):
        for sid in sorted(lm.REQUIRED_STATED_LIMITS["interim"]):
            doc = draft()
            doc["fit"]["stated_limits"] = [x for x in doc["fit"]["stated_limits"] if x["id"] != sid]
            self.refused(lambda: lm.validate_manifest(doc), f"fit.stated_limits: carries {sid}")
        for rid in sorted(lm.REQUIRED_DEFERRED["interim"]):
            doc = draft()
            doc["freeze2"]["deferred_rules"] = [x for x in doc["freeze2"]["deferred_rules"] if x["id"] != rid]
            self.refused(lambda: lm.validate_manifest(doc), f"freeze2.deferred_rules: carries {rid}")

    def test_the_dictated_sentences_are_in_the_manifest(self):
        lim = {x["id"]: x["text"] for x in draft()["fit"]["stated_limits"]}
        self.assertIn("about 4 times in 10", lim["qualified_pass_rate"])
        self.assertIn("about 1 time in 12", lim["qualified_pass_rate"])
        self.assertIn("It is not evidence that the term is wrong", lim["qualified_pass_rate"])
        self.assertIn("3 % of its 439 s value on a 75 s turn", lim["half_t2_limit"])
        self.assertIn("under about 150 s, H is the onset step alone", lim["half_t2_limit"])
        sd = next(x for x in draft()["freeze2"]["deferred_rules"] if x["id"] == "sd_j_covariance")["rule"]
        self.assertIn("larger of the leg-clustered standard error and the day-jackknife", sd)

    def test_withdrawn_sentence_days_tripwire_and_116_rule(self):
        doc = draft()
        doc["fit"]["heat_term"]["form"] += " H is zero for a turn that ends before its predicted onset."
        self.refused(lambda: lm.validate_manifest(doc), "withdrawn")
        doc = draft()
        next(t for t in doc["stages"]["tripwires"] if t["id"] == "days_below_4")["threshold"] = 3
        self.refused(lambda: lm.validate_manifest(doc), "days_below_4 with threshold 4")
        doc = draft()
        doc["decisions"] = [x for x in doc["decisions"] if x["id"] != "onsets_before_116_s"]
        self.refused(lambda: lm.validate_manifest(doc), "carries onsets_before_116_s")
        doc = draft()
        doc["outputs"]["prints"] = [x for x in doc["outputs"]["prints"] if x["id"] != "onset_offset_residuals"]
        self.refused(lambda: lm.validate_manifest(doc), "prints onset_offset_residuals")
        doc = draft()
        doc["rulings"].remove("RL-166b §3")
        self.refused(lambda: lm.validate_manifest(doc), "must cite 'RL-166b §3'")

    def test_the_schemas_carry_rl166b_fields(self):
        s1 = json.loads((LOOKS / "lm-interim-01.stage1.schema.json").read_text())
        for k in ("active_readings", "onsets_before_116_s", "meter_clock"):
            self.assertIn(k, s1["required"])
        self.assertIn("days_below_4", s1["properties"]["tripwires"]["required"])
        self.assertIn("n_uncensored_by_cell", s1["properties"]["onset"]["required"])
        out = json.loads((LOOKS / "lm-interim-01.output.schema.json").read_text())
        for k in ("fold_coefficients", "day_detail", "onset_offset_residuals"):
            self.assertIn(k, out["$defs"]["channel_fit"]["required"])


if __name__ == "__main__":
    unittest.main()
