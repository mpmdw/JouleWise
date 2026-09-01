```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Delta audit complete: physical, lint, slot, and render checks pass except the added AUTH gloss is factually wrong.",
  "workspace": {
    "base_requested": "1f6182bd9a0b54158c4bce1ca81a849ebc3f481f",
    "base_mode": "exact",
    "head_start": "1f6182bd9a0b54158c4bce1ca81a849ebc3f481f",
    "head_end": "b854836aba1dcdfbf4015d83f325d4d57b9187b6",
    "upstream_end": "b854836aba1dcdfbf4015d83f325d4d57b9187b6",
    "branch": "feat/2026-09-01-dependence"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "docs/paper/round7/dependence-sensitivity.md.in:111 (rendered :112)",
        "title": "AUTH is misglossed",
        "detail": "The added text expands Sources code AUTH as “the authentication artifact.” The authoritative registry defines AUTH as docs/decision_log.md and decision entries D-119 and D-121 through D-124: an authority source, not an authentication artifact.",
        "evidence": "docs/paper/results-fill-registry.md:90-93",
        "recommendation": "Gloss AUTH as the decision-log authority source, or introduce a distinct code for an authentication artifact."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest discover -s tests -p 'test_dependence_sensitivity.py'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 22 tests in 9.424s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 22 tests in [0-9.]+s\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 scripts/dependence_sensitivity.py --check-sheet",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; sens=Path(\"joulewise/analysis_engine/sensitivity.py\").read_text(); mult=Path(\"joulewise/analysis_engine/multiplicity.py\").read_text(); script=Path(\"scripts/dependence_sensitivity.py\").read_text(); est=Path(\"joulewise/analysis_engine/estimators.py\").read_text(); reg=Path(\"docs/paper/results-fill-registry.md\").read_text(); h30=Path(\"docs/paper/round7/retensing-plan.md\").read_text(); draft=Path(\"docs/paper/draft-v1.md\").read_text(); rendered=Path(\"docs/paper/round7/dependence-sensitivity.md\").read_text(); assert \"p_value <= threshold\" in sens and \"adjusted[contrast_id] <= threshold\" in mult; assert \"if degrees < 1:\" in script and \"repeat_only_interval = _interval(mean_j, se_repeat, critical)\" in script and \"metrology_aware_interval = _interval(mean_j, se_total, critical)\" in script; assert \"se_total = math.hypot(se_repeat, se_metrology)\" in est; assert \"- `AUTH` — `docs/decision_log.md`\" in reg and \"- `gamma`: prospective pack\" in reg; assert \"The pulse portion of the calibration bound is the largest of 118 observed onset and offset excursions\" in h30 and \"largest allowed edge displacement among all pulses\" in draft and \"The pulse portion of the calibration bound is the largest of 118 observed onset and offset excursions\" in rendered; print(\"physical_source_checks=pass; AUTH_registry_definition=decision_log; gamma=prospective_pack; H30=118_excursions_plus_anchor\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "physical_source_checks=pass; AUTH_registry_definition=decision_log; gamma=prospective_pack; H30=118_excursions_plus_anchor"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "physical_source_checks=pass; AUTH_registry_definition=decision_log; gamma=prospective_pack; H30=118_excursions_plus_anchor"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical full unittest suite was not run, and the --render-sheet CLI was not invoked because it writes the tracked rendered file in this read-only sandbox. The focused suite covered in-memory byte equality; --check-sheet passed.",
      "needs": ""
    }
  ]
}
```

## Findings

- F1 — blocker — [dependence-sensitivity.md.in:111](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md.in:111) misdefines `AUTH`; the rendered copy is [line 112](/Users/edr/code/JouleWise-wt-dependence/docs/paper/round7/dependence-sensitivity.md:112).

All other named physical checks pass: inclusive comparisons, ν<1 refusal, shared three-decimal critical value, admission predicate, gamma’s prospective pack, H30 wording, and two decode/prefill contrasts.

First-use audit: “authentication artifact” is the genuine misbuilt term above. “Inference phase” and “retensing plan” are audience/document vocabulary; registered validity checks, total SE, rho, ν, and calibration-bound terms are explained or anchored to code. `gamma`, `DERIVE`, `DRAFT`, and binding-token vocabulary are already established.

## Residual risk

The canonical full suite and write-oriented `--render-sheet` CLI were not run; focused tests and `--check-sheet` passed.

VERDICT: BLOCKER