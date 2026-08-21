```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NO-GO: the rewritten clock-anchor refusal predicate contradicts the implementation; the new ABBA time-imbalance mechanism is also not implemented or operationally specified.",
  "workspace": {
    "base_requested": "3d0b48a1cec94a324e694e13c073b4b6785a553d",
    "base_mode": "exact",
    "head_start": "32b5424b59655aaf1b8683ee2d1773934c40817b",
    "head_end": "32b5424b59655aaf1b8683ee2d1773934c40817b",
    "upstream_end": "32b5424b59655aaf1b8683ee2d1773934c40817b",
    "branch": "impl/paper-pedagogy-r4"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "NO-GO",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "docs/paper/draft-v1.md:79, 94, 101",
        "discrepancy": "The prose says a fitted clock-rate interval that reaches/touches ±50 ppm refuses. The implementation refuses only when the interval extends strictly beyond either limit; equality at a boundary satisfies neither refusal comparison.",
        "replay_evidence": "joulewise/uncertainty_evidence.py uses beta_lower < 1-delta OR beta_upper > 1+delta."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "location": "docs/paper/draft-v1.md:294",
        "discrepancy": "The new prose says the protocol records q and reports it as an adjustment variable, but the current ABBA extraction computes only abba_delta from four energies and has no midpoint-time/q reporting field. The text also never specifies how q changes a reported estimate or gate.",
        "replay_evidence": "joulewise/floor_extraction.py:2674-2676 supplies only A1/B1/B2/A2 energy values to abba_delta; repository search found no time-imbalance field in the floor extractor, whole-window logic, or results registry."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest -q tests.test_uncertainty_evidence tests.test_powermetrics_fiducial",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"arm_blocked\": true, \"code\": \"calibration_frozen_protocol_invalid\", \"exit_id\": \"correct-preflight\", \"next_command\": \"recover_calibration_ledger.py readiness --phase pre-reserve --session-id SESSION --plan PLAN\", \"status\": \"refused\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest -q tests.test_detection_floor tests.test_reduce",
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
      "cmd": "python3 -c \"import json; from decimal import Decimal as D; from pathlib import Path as P; r=json.loads(P('docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json').read_text())[0]; a=r['anchor_v3']; s=sum((D(str(a[k])) for k in ('anchor_only_bound_s','wall_minus_monotonic_span_s','stamp_resolution_s','numeric_padding_s')),D()); assert s==D('0.0011349971959968977402') and D(str(a['effective_clock_anchor_bound_s']))==D('0.0011349971959968978') and D(str(r['b_fiducial_v3_s']))-D(str(a['effective_clock_anchor_bound_s']))==D('0.0289329345611147592'); c=json.loads(P('configs/calibration/calibration_acceptance_d079_v2_n17_r6.json').read_text())['decimal_derivation']['ratified_operatives']; assert c['bracket_screen_s']=='0.009724' and c['maximum_budgetable_drift_s']=='0.010164834757777545'; w=P('joulewise/whole_window.py').read_text(); assert 'statistics.fmean(ordered[-NEG8_REPLICATED_ENDPOINT_N:])' in w and 'math.sqrt(2.0 / NEG8_REPLICATED_ENDPOINT_N)' in w; print('fidelity_arithmetic_and_settled_reference_formula=pass')\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "fidelity_arithmetic_and_settled_reference_formula=pass"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "fidelity_arithmetic_and_settled_reference_formula=pass"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c \"from pathlib import Path as P; src=P('joulewise/uncertainty_evidence.py').read_text(); assert 'beta_lower < Fraction(1) - physical_rate_delta' in src and 'beta_upper > Fraction(1) + physical_rate_delta' in src; print('clock-rate predicate is strict')\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "clock-rate predicate is strict"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "clock-rate predicate is strict"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 -c \"from pathlib import Path as P; import re,subprocess; c=P('docs/paper/draft-v1.md').read_text(); p=subprocess.check_output(['git','show','32b5424^:docs/paper/draft-v1.md'],text=True); m='<!-- CONDITIONAL-INSERT-TIGHTER-FLOOR'; assert c[c.index(m):]==p[p.index(m):]; tok=lambda x:re.findall(r'\\\\[(?:F|C)_[^]]+\\\\]',x); assert tok(c)==tok(p); render=re.sub(r'<!--[\\\\s\\\\S]*?-->','',c[:c.index(m)]); assert not any(x in c for x in ('8.611855','1.869502')); assert not any(x in render for x in ('11.6','a9','a10','anchor-v2','n=19')); print('conditional=identical tokens=unchanged banned=absent superseded_markers=absent')\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "conditional=identical tokens=unchanged banned=absent superseded_markers=absent"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "conditional=identical tokens=unchanged banned=absent superseded_markers=absent"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -c \"import json; from pathlib import Path as P; d=json.loads(P('docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json').read_text())[0]; assert 'clock_stamps' not in d['anchor_v3'] and not any(k in d for k in ('commanded_onset','commanded_offset','fitted_onset_interval','fitted_offset_interval')); s=json.loads(P('configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json').read_text()); assert s['freeze_status']=='settled_reference' and len(s['members'])>=10; r=P('docs/paper/results-fill-registry.md').read_text(); assert 'VALUE_UNISSUED' in r and 'SUPPLIER_UNKNOWN' in r; print('fences=P01/P02 raw substitutions absent; P03/P04/P06/P07/P13/P14/P19 issuance states unissued')\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "fences=P01/P02 raw substitutions absent; P03/P04/P06/P07/P13/P14/P19 issuance states unissued"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "fences=.*issuance states unissued"
      }
    }
  ],
  "flags": []
}
```

## Findings

- **F1 — blocker.** The rate-limit prose must say “extends beyond” rather than “reaches,” “touches,” or “crosses,” unless the code is deliberately changed to make equality refuse. This affects the estimator explanation and its flow diagram.

- **F2 — should_fix.** Either implement and evidence the recording/reporting of \(q\), including its analytical role, or describe it as a future reporting requirement. As written, it implies a present mechanism that the code and result schema do not provide.

All nine evidence fences are honest: the raw pulse/stamp substitutions are absent, and the current floor, drift, characterization, ABBA, claim, sizing, and Holm values are marked unissued/unknown. Replayed added arithmetic, settled-reference formula, sample-overlap rule, bracket substitution, integrity controls, and prior-round regression sentinels otherwise passed.

## Residual risk

Raw current-capture pulse edges and clock stamps are not retained in the repository, so their literal substitutions remain intentionally unreplayable; the revised fences disclose that limitation accurately.