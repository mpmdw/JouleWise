"""The look manifest validator (RL-150 R4). Synthetic inputs only: no custody, energy, meter or journal file
exists in these tests, and one test proves the validator opens none even when such files sit beside it."""
from __future__ import annotations

import builtins
import copy
import hashlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
import unittest.mock

from joulewise.cadence_looks import manifest as lm
from scripts import cadence_look_manifest as cli

REPO = Path(__file__).resolve().parents[2]
LOOKS = REPO / "docs/process/cadence/looks"
MANIFEST = LOOKS / "lm-interim-01.json"
SCHEMA = LOOKS / "look_manifest.schema.json"
FIT = "joulewise/cadence_looks/fit_interim.py"
RULE34 = "joulewise/cadence_looks/inclusion_rules_3_4.py"
STEP3 = "joulewise/cadence_looks/step3_energy_ratios.py"
ADAPTER = "joulewise/cadence_looks/step3_adapter.py"


def draft():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def finalize(doc, shas=None):
    """A synthetic committed manifest: every placeholder filled, no open question."""
    shas = shas or {}
    doc = copy.deepcopy(doc)
    doc["status"] = "committed"
    doc["fit"]["code"] = [{"path": FIT, "sha256": shas.get(FIT, "1" * 64)}]
    doc["fit"]["step3"]["code"] = {"path": STEP3, "sha256": shas.get(STEP3, "2" * 64)}
    doc["fit"]["step3"]["adapter"] = {"path": ADAPTER, "sha256": shas.get(ADAPTER, "3" * 64)}
    for rule in doc["inclusion"]["rules"]:
        if rule["rule"] in (3, 4):
            rule["code"] = {"path": RULE34, "sha256": shas.get(RULE34, "4" * 64)}
    if "outputs.schema" in shas:
        doc["outputs"]["schema"]["sha256"] = shas["outputs.schema"]
    for d in doc["decisions"]:
        if isinstance(d.get("threshold"), str):
            d["threshold"] = 8.0
    doc["open_questions"] = []

    def scrub(node):
        if isinstance(node, dict):
            return {k: scrub(v) for k, v in node.items()}
        if isinstance(node, list):
            return [scrub(v) for v in node]
        if isinstance(node, str):
            return re.sub(r"PENDING:Q\d+", "ruled", node)
        return node
    return scrub(doc)


def ledger(spans=None, reads=None):
    days = {"dev-01": "2026-11-14", "dev-02": "2026-11-16", "dev-03": "2026-11-16", "dev-04": "2026-11-17",
            "dev-05": "2026-11-17", "hp-01": "2026-11-15"}
    default = [{"span_id": f"{b}-s01", "block_id": b, "phase": "extension" if b == "hp-01" else "development",
                "desk_final": True, "energy_seal": "sealed", "t0_local_date": d} for b, d in days.items()]
    default.append({"span_id": "dev-01-s04b", "block_id": "dev-01", "phase": "development", "desk_final": True,
                    "energy_seal": "sealed", "t0_local_date": "2026-11-15"})
    default.append({"span_id": "qual-01-s01", "block_id": "qual-01", "phase": "qualification", "desk_final": False,
                    "energy_seal": "sealed", "t0_local_date": "2026-11-19"})
    return {"schema": lm.LEDGER_SCHEMA, "spans": spans if spans is not None else default,
            "energy_reads": reads or [{"read_id": "step3-1114", "spans": ["rehearsal-1112-step-d"], "cite": ["RL-150 §3.1"]}]}


class Base(unittest.TestCase):
    def refused(self, fn, fragment):
        with self.assertRaises(lm.ManifestError) as ctx:
            fn()
        self.assertTrue(any(fragment in p for p in ctx.exception.problems),
                        f"{fragment!r} not in {ctx.exception.problems}")
        return ctx.exception.problems


class CommittedDraft(Base):
    def test_the_committed_draft_validates_as_a_draft(self):
        pending = lm.validate_manifest(draft())
        qids = {q["id"] for q in draft()["open_questions"]}
        self.assertTrue(pending)
        self.assertTrue({q for _, q in pending} <= qids)

    def test_the_draft_is_refused_as_final(self):
        problems = self.refused(lambda: lm.validate_manifest(draft(), final=True), "placeholder")
        self.assertTrue(any("open questions" in p for p in problems))
        self.assertTrue(any("needs status 'committed'" in p for p in problems))

    def test_a_filled_synthetic_manifest_validates_as_final(self):
        self.assertEqual(lm.validate_manifest(finalize(draft()), final=True), [])

    def test_the_output_schema_pin_matches_the_file(self):
        pin = draft()["outputs"]["schema"]
        raw = (REPO / pin["path"]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), pin["sha256"])

    def test_the_committed_draft_passes_the_repo_check(self):
        kits = sorted(str(p) for p in (REPO / "docs/process/cadence/kits").glob("*.json"))
        self.assertTrue(kits)
        lm.check_repo(draft(), REPO, kits)

    def test_cli(self):
        with unittest.mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(cli.main(["validate", str(MANIFEST)]), 0)
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
            (("fit", "heat_term"), "predictors", "missing key 'predictors'"),
            (("fit", "validation"), "min_calendar_days", "missing key 'min_calendar_days'"),
            (("freeze2",), "commit_before", "missing key 'commit_before'"),
            (("custody",), "no_import_by", "missing key 'no_import_by'"),
            (("energy",), "per_leg_energy_in_output", "missing key 'per_leg_energy_in_output'"),
        ]
        for path, key, fragment in cases:
            doc = draft()
            node = doc
            for p in path:
                node = node[p]
            del node[key]
            self.refused(lambda: lm.validate_manifest(doc), fragment)

    def test_cites_are_required(self):
        doc = draft()
        doc["decisions"][0]["cite"] = []
        self.refused(lambda: lm.validate_manifest(doc), "decisions[0].cite")

    def test_placeholders_must_name_an_open_question(self):
        doc = draft()
        doc["fit"]["heat_term"]["response"] = "PENDING:Q99"
        self.refused(lambda: lm.validate_manifest(doc), "Q99, which is not an open question")
        doc = draft()
        doc["fit"]["heat_term"]["response"] = "PENDING later"
        self.refused(lambda: lm.validate_manifest(doc), "written PENDING:Qn")


class RulingInvariants(Base):
    def test_rules_3_and_4_are_judged_at_the_look_with_pinned_code(self):
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

    def test_predictors(self):
        doc = draft()
        doc["fit"]["heat_term"]["predictors"].append("in_turn_clock")
        self.refused(lambda: lm.validate_manifest(doc), "not allowed by RL-149 §2.7")
        doc = draft()
        doc["fit"]["heat_term"]["predictors"].append("start_tv0h_raw")
        self.refused(lambda: lm.validate_manifest(doc), "not allowed")
        doc = draft()
        doc["fit"]["heat_term"]["forbidden_predictors"].remove("condition")
        self.refused(lambda: lm.validate_manifest(doc), "must list ['condition']")
        doc = draft()
        doc["fit"]["heat_term"]["sign_of_start_term_assumed"] = True
        self.refused(lambda: lm.validate_manifest(doc), "sign_of_start_term_assumed")
        doc = draft()
        doc["fit"]["reads_never"] = ["kit_start_band", "kit_g0_shape"]
        self.refused(lambda: lm.validate_manifest(doc), "fit.reads_never")

    def test_rule_p_and_the_one_decision_are_retired(self):
        doc = draft()
        doc["decisions"].append({"id": "rule_p", "statistic": "x", "rule": "x", "action": "x", "reads_energy": True,
                                 "cite": ["RL-149 §2.7"]})
        self.refused(lambda: lm.validate_manifest(doc), "retired")

    def test_required_prints_decisions_and_channels(self):
        doc = draft()
        doc["outputs"]["prints"] = [p for p in doc["outputs"]["prints"] if p["id"] != "step3_statistic_iii"]
        self.refused(lambda: lm.validate_manifest(doc), "prints step3_statistic_iii")
        doc = draft()
        bias = next(p for p in doc["outputs"]["prints"] if p["id"] == "prefix_length_bias")
        bias["ratios"] = [1.10, 1.374]
        self.refused(lambda: lm.validate_manifest(doc), "ratios")
        doc = draft()
        doc["decisions"] = [d for d in doc["decisions"] if d["id"] != "drift_tripwire"]
        self.refused(lambda: lm.validate_manifest(doc), "carries drift_tripwire")
        doc = draft()
        doc["energy"]["channels"] = [c for c in doc["energy"]["channels"] if c["id"] != "dc_in"]
        self.refused(lambda: lm.validate_manifest(doc), "reads dc_in")
        doc = draft()
        doc["energy"]["per_leg_energy_in_output"] = True
        self.refused(lambda: lm.validate_manifest(doc), "per_leg_energy_in_output")

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
        doc["custody"]["seats"] = 2
        self.refused(lambda: lm.validate_manifest(doc), "seats 1")
        doc = draft()
        doc["review"]["paper_bound"] = False
        self.refused(lambda: lm.validate_manifest(doc), "paper_bound")

    def test_out_of_phase_blocks_are_refused_in_the_manifest(self):
        doc = draft()
        doc["reads"]["blocks"].append({"block_id": "qual-01", "phase": "qualification", "role": "fit",
                                       "kit_sha256": None, "spans": "all_desk_final", "cite": ["RL-165 §8.1"]})
        problems = self.refused(lambda: lm.validate_manifest(doc), "out of phase")
        self.assertTrue(any("never reads qual-01" in p for p in problems))
        doc = draft()
        hp = next(b for b in doc["reads"]["blocks"] if b["block_id"] == "hp-01")
        hp["role"] = "fit"
        self.refused(lambda: lm.validate_manifest(doc), "never in the fit")
        doc = draft()
        doc["reads"]["blocks"].append({"block_id": "ctl-01", "phase": "extension", "role": "describe",
                                       "kit_sha256": None, "spans": "all_desk_final", "cite": ["RL-149 §2.6"]})
        self.refused(lambda: lm.validate_manifest(doc), "never reads ctl-01")
        doc = draft()
        doc["reads"]["blocks"] = [b for b in doc["reads"]["blocks"] if b["block_id"] != "dev-05"]
        self.refused(lambda: lm.validate_manifest(doc), "dev-05 is waited for but not read")
        doc = draft()
        doc["reads"]["blocks"].append({"block_id": "reserve-01", "phase": "reserve", "role": "fit",
                                       "kit_sha256": None, "spans": "all_desk_final", "cite": ["RL-149 §2.4"]})
        self.refused(lambda: lm.validate_manifest(doc), "serves_phase 'development'")
        doc["reads"]["blocks"][-1]["serves_phase"] = "development"
        lm.validate_manifest(doc)

    def test_rejected_attempts_are_never_read(self):
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
        roster = lm.resolve_roster(self.doc, ledger())
        ids = [r["span_id"] for r in roster]
        self.assertIn("dev-01-s04b", ids)
        self.assertNotIn("qual-01-s01", ids)
        self.assertEqual({r["role"] for r in roster if r["block_id"] == "hp-01"}, {"describe"})

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

    def test_spans_not_desk_final_or_unknown_are_refused(self):
        led = ledger()
        led["spans"][4]["desk_final"] = False
        self.refused(lambda: lm.resolve_roster(self.doc, led), "dev-05-s01: not desk-final")
        doc = copy.deepcopy(self.doc)
        doc["reads"]["blocks"][1]["spans"] = ["dev-02-s09"]
        self.refused(lambda: lm.resolve_roster(doc, ledger()), "dev-02-s09: not in the span ledger")
        led = ledger(spans=[s for s in ledger()["spans"] if s["block_id"] != "dev-04"])
        self.refused(lambda: lm.resolve_roster(self.doc, led), "dev-04: no span of this block")

    def test_fewer_than_three_fit_days_is_refused(self):
        led = ledger()
        for s in led["spans"]:
            s["t0_local_date"] = "2026-11-16"
        self.refused(lambda: lm.resolve_roster(self.doc, led), "covers 1 calendar day")

    def test_a_malformed_ledger_is_refused(self):
        led = ledger()
        del led["spans"][0]["energy_seal"]
        self.refused(lambda: lm.resolve_roster(self.doc, led), "missing key 'energy_seal'")


class RepoCheck(Base):
    def make_repo(self, fit_src="def fit(rows):\n    return rows['start_tf08']\n", runner_src="import json\n"):
        tmp = Path(tempfile.mkdtemp(prefix="lm-repo-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        files = {FIT: fit_src, RULE34: "def judge(stamps):\n    return True\n", STEP3: "X = 1\n",
                 ADAPTER: "from joulewise.cadence_looks import step3_energy_ratios\n",
                 "scripts/cadence_legs_runner.py": runner_src,
                 "docs/process/cadence/looks/lm-interim-01.output.schema.json": "{}\n"}
        for rel, src in files.items():
            (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp / rel).write_text(src, encoding="utf-8")
        shas = {rel: hashlib.sha256((tmp / rel).read_bytes()).hexdigest() for rel in files}
        shas["outputs.schema"] = shas["docs/process/cadence/looks/lm-interim-01.output.schema.json"]
        kit = {"frozen": {"commit": "a" * 40, "paths": {"scripts/cadence_legs_runner.py": "0" * 64}}, "looks": []}
        kp = tmp / "kit.json"
        kp.write_text(json.dumps(kit), encoding="utf-8")
        return tmp, finalize(draft(), shas), kp

    def test_clean_repo_passes(self):
        tmp, doc, kp = self.make_repo()
        lm.check_repo(doc, tmp, [kp])

    def test_hash_mismatch_and_missing_file(self):
        tmp, doc, kp = self.make_repo()
        (tmp / FIT).write_text("def fit(rows):\n    return 0\n", encoding="utf-8")
        self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "sha256 differs")
        (tmp / FIT).unlink()
        self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "is not in the repository")

    def test_a_frozen_path_that_imports_look_code_is_refused(self):
        for src in ("from joulewise.cadence_looks import fit_interim\n", "import joulewise.cadence_looks.manifest\n"):
            tmp, doc, kp = self.make_repo(runner_src=src)
            self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "never import look code")

    def test_fit_code_as_a_kit_frozen_path_is_refused(self):
        tmp, doc, kp = self.make_repo()
        kit = json.loads(kp.read_text())
        kit["frozen"]["paths"][FIT] = "0" * 64
        kp.write_text(json.dumps(kit))
        self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "must stay outside every leg kit")
        kit["looks"] = [{"look_id": "x", "after_legs": 1, "fit": {"path": FIT}}]
        kp.write_text(json.dumps(kit))
        self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "looks must stay []")

    def test_fit_code_that_reads_condition_is_refused(self):
        for src in ("def fit(cfg):\n    return cfg['condition']\n", "def fit(b):\n    return b.condition\n"):
            tmp, doc, kp = self.make_repo(fit_src=src)
            self.refused(lambda: lm.check_repo(doc, tmp, [kp]), "reads a 'condition' field")


class OpensNoEnergy(Base):
    def test_the_validator_opens_only_manifest_ledger_kit_and_code(self):
        tmp = Path(tempfile.mkdtemp(prefix="lm-custody-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        custody = tmp / "custody" / "dev-01-s01" / "legs" / "L001" / "runtime"
        custody.mkdir(parents=True)
        for name in ("power_trace.csv", "rich_telemetry.jsonl", "outputs_align_thermal.jsonl"):
            (custody / name).write_text("SENTINEL\n", encoding="utf-8")
        (tmp / "custody" / "dev-01-s01" / "hazards").mkdir()
        (tmp / "custody" / "dev-01-s01" / "hazards" / "stream-0001.jsonl").write_text("SENTINEL\n")
        led_path = tmp / "ledger.json"
        led_path.write_text(json.dumps(ledger()), encoding="utf-8")
        opened = []
        real_open, real_io_open = builtins.open, io.open

        def spy(file, *a, **k):
            opened.append(str(file))
            return real_open(file, *a, **k)
        kits = sorted(str(p) for p in (REPO / "docs/process/cadence/kits").glob("*.json"))
        with unittest.mock.patch.object(builtins, "open", spy), unittest.mock.patch.object(io, "open", spy):
            doc = lm.load_json(MANIFEST)
            lm.validate_manifest(doc)
            lm.check_repo(doc, REPO, kits)
            lm.resolve_roster(finalize(doc), lm.load_json(led_path))
        self.assertTrue(opened)
        for path in opened:
            self.assertNotIn(str(tmp / "custody"), path)
            # repository source (the frozen paths' import scan) and JSON (manifest, kits, ledger) only
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
        self.assertEqual(schema["properties"]["schema"]["const"], lm.SCHEMA)

    def test_the_manifest_validates_against_the_json_schema_when_available(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed; the Python validator is authoritative")
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        jsonschema.validate(draft(), schema)
        jsonschema.validate(finalize(draft()), schema)


if __name__ == "__main__":
    unittest.main()
