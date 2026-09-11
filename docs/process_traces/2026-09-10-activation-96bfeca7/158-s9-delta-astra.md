```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F1 closed; F2 remains open through a Unicode case alias on this Mac. Two new tests detect the fixes; two add boundary coverage.",
  "workspace": {
    "base_requested": "d1c3d0c5",
    "base_mode": "informational",
    "head_start": "c409228470fc7383675743b23197336f26d3b204",
    "head_end": "c409228470fc7383675743b23197336f26d3b204",
    "upstream_end": "c409228470fc7383675743b23197336f26d3b204",
    "branch": "feat/2026-09-10-epoch-equivalence-check"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "scripts/epoch_equivalence_check.py",
        "line": 163,
        "title": "Unicode case alias still bypasses the acceptance-directory guard",
        "input": "--out configſ/calibration/calibration_acceptance_d079_v2_n17_r6.json --force",
        "actual": "The destination is the existing r6 acceptance file on this Mac, but _refuse_out_path accepts it.",
        "recommendation": "Handle Unicode filesystem case equivalence; casefold() catches this long-s alias. Add a regression verifying both samefile equivalence and refusal."
      }
    ],
    "audit": {
      "F1": "Closed under the production loader and registry contract. Every returned envelope must have ANCHOR_V3_R6_ACCEPTANCE_ID. All other registered generations refused. Redirected reads of unchanged r6 bytes at another path authenticated. Renamed IDs refused, including with the loader stubbed to return a renamed artifact. Existing operative and corpus registry-disagreement tests passed.",
      "F2": "ASCII uppercase bypass closed; Unicode long-s bypass remains. lower() is not full case folding.",
      "over_refusal": "An unrelated temporary output with configs/calibration anywhere above it is rejected at both revisions. The fix extends that blanket rule to case variants. Distinct uppercase directories on case-sensitive volumes are consequently rejected too. Prefix lookalikes such as myconfigs/calibration and configs/calibration-copy remain allowed.",
      "new_defects": "No additional import, arithmetic, print-envelope-only or exit-code regression found. The help's never-writes-under-calibration promise remains false because F2 survives. Default print-only succeeds without ledger reads or writes; predecessor print-only now refuses with exit 3.",
      "four_new_tests": [
        {
          "test": "test_another_authenticated_generation_is_refused_as_the_reference",
          "against_base": "Would fail: the predecessor is accepted and the supplied 0.033 values produce PASS."
        },
        {
          "test": "test_an_out_path_under_configs_calibration_refuses_case_folded",
          "against_base": "Would fail: uppercase path passes the guard, so the required acceptance-directory refusal is absent."
        },
        {
          "test": "test_exactly_six_retained_values_are_judged_not_inconclusive",
          "against_base": "Would pass: inclusive m=6 behavior already exists. Boundary coverage, not a fix regression."
        },
        {
          "test": "test_a_range_exactly_equal_to_the_bracket_screen_passes",
          "against_base": "Would pass: inclusive spread comparison already exists. Boundary coverage, not a fix regression."
        }
      ]
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_artifact_and_registry_disagreement_refuses tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_an_operative_the_loader_does_not_police_still_refuses tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_a_disagreeing_corpus_size_refuses tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_help_says_what_the_tool_never_does_and_glosses_its_terms tests.test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_print_envelope_only_needs_no_session_and_writes_nothing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 5 tests in 0.004s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -B -c 'from pathlib import Path; from scripts.epoch_equivalence_check import _refuse_out_path; p=Path(\"config\\u017f/calibration/calibration_acceptance_d079_v2_n17_r6.json\"); print(\"same_file:\",p.samefile(Path(\"configs/calibration/calibration_acceptance_d079_v2_n17_r6.json\"))); print(\"resolved:\",p.resolve()); _refuse_out_path(p,True); print(\"GUARD_ACCEPTED_EXISTING_ACCEPTANCE_WITH_FORCE\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "same_file: True",
          "resolved: /Users/edr/code/JouleWise-wt-s9-eq-check/configſ/calibration/calibration_acceptance_d079_v2_n17_r6.json",
          "GUARD_ACCEPTED_EXISTING_ACCEPTANCE_WITH_FORCE"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "GUARD_ACCEPTED_EXISTING_ACCEPTANCE_WITH_FORCE"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -B -c 'import subprocess,types\nfrom pathlib import Path\nfrom unittest.mock import patch\nfrom decimal import Decimal\nfrom scripts import epoch_equivalence_check as c\nfrom joulewise import calibration_bracketing as b\nold=types.ModuleType(\"old\"); old.__file__=c.__file__\nexec(compile(subprocess.check_output([\"git\",\"show\",\"d1c3d0c5:scripts/epoch_equivalence_check.py\"]),c.__file__,\"exec\"),old.__dict__)\nfor ident,row in b.ISSUED_ACCEPTANCE_REGISTRY.items():\n try: result=c.reference_envelope(row[\"path\"])[\"acceptance_id\"]\n except c.EquivalenceRefusal: result=\"REFUSED\"\n assert result==(ident if ident==b.ANCHOR_V3_R6_ACCEPTANCE_ID else \"REFUSED\")\nwith patch.object(b,\"read_authentication_input\",return_value=c.DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes()):\n assert c.reference_envelope(Path(\"/tmp/copy.json\"))[\"acceptance_id\"]==b.ANCHOR_V3_R6_ACCEPTANCE_ID\nrenamed=dict(c.load_calibration_acceptance_bound(c.DEFAULT_ACCEPTANCE_BOUND_PATH),acceptance_id=\"renamed\")\nwith patch.object(c,\"load_calibration_acceptance_bound\",return_value=renamed):\n try: c.reference_envelope(Path(\"/tmp/renamed.json\"))\n except c.EquivalenceRefusal: pass\n else: raise AssertionError(\"renamed ID accepted\")\nprint(\"F1: registered alternatives refused; copied bytes accepted; renamed loader result refused\")\nenv=c.reference_envelope(c.DEFAULT_ACCEPTANCE_BOUND_PATH)\nlevel=Decimal(env[\"level_screen_s\"]); bracket=Decimal(env[\"bracket_screen_s\"])\nsession=types.SimpleNamespace(session_kind=\"derivation\",state=\"aborted\",abort_reason=\"window_exhausted\",declared_slots=tuple(range(12)))\ntop=level-Decimal(\"0.00005\")\ncases={\"m6\":[level-Decimal(\"0.0005\")-Decimal(\"0.00001\")*(5-i) for i in range(6)],\"range_equal\":[top-bracket]+[top-Decimal(\"0.000001\")*(10-i) for i in range(11)]}\nfor name,vals in cases.items():\n retained=[dict(slot=str(i),attempt_id=str(i),b_fiducial_s=str(v)) for i,v in enumerate(vals)]\n for module in (old,c):\n  with patch.object(module,\"_slot_outcomes\",return_value=([],retained)): result=module.evaluate_session(session,\"night\",env)\n  assert result[\"verdict\"]==\"PASS\" and result[\"m\"]==len(vals)\n  if name==\"range_equal\": assert Decimal(result[\"range_s\"])==bracket\n print(name+\": PASS at base and head\")\nprint(\"DELTA_ASSERTIONS_OK\")\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "F1: registered alternatives refused; copied bytes accepted; renamed loader result refused",
          "m6: PASS at base and head",
          "range_equal: PASS at base and head",
          "DELTA_ASSERTIONS_OK"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "DELTA_ASSERTIONS_OK"}
    }
  ],
  "flags": []
}
```

## Findings

**F2 — should_fix, still open:** [epoch_equivalence_check.py:163](/Users/edr/code/JouleWise-wt-s9-eq-check/scripts/epoch_equivalence_check.py:163) uses `.lower()`, which leaves `ſ` (U+017F LONG S) unchanged.

On this Mac, `configſ/calibration/calibration_acceptance_d079_v2_n17_r6.json` is **the existing acceptance file**, confirmed with `samefile()`. Nevertheless, `_refuse_out_path(path, True)` accepts it. A successful comparison followed by writing would therefore overwrite the acceptance through this alias.

Use Unicode-aware case handling and add this filesystem-equivalence regression. `.casefold()` catches this particular bypass. The uppercase-only test does not establish full macOS protection.

## Residual risk

The four new fixture-backed tests were assessed by inspection and isolated execution of their relevant behavior; their complete fixture workflows were not run because they create files. The exact-six and bracket-equality calculations passed against both revisions. They are useful boundary tests, but **only two of the four would fail against the baseline**.

Alternate-path authentication was tested with redirected byte reads, without creating a physical copy. Five existing read-only tests passed. No files were modified; HEAD and the clean workspace remained unchanged.