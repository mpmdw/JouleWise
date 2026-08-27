```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Fidelity review complete: seven blockers, two should-fixes, and one citation nit; the rewrite does not yet have every equation and number correct against the current code and replay fence.",
  "workspace": {
    "base_requested": "/Users/edr/code/JouleWise-wt-r4",
    "base_mode": "exact",
    "head_start": "a1baf7ba8e4940f166c557c5410622def8525cfe",
    "head_end": "a1baf7ba8e4940f166c557c5410622def8525cfe",
    "upstream_end": "a4989f054ef4eae7991f71b354146ab10eec9870",
    "branch": "paper/t26-round4"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "every_equation_and_number_correct": false,
    "blockers": 7,
    "should_fix": 2,
    "nits": 1,
    "fence_run": {
      "compared": 43,
      "mismatches": 0,
      "appendix_restatements_byte_identical": false
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Issued-v2 pulse-0 values differ from the current-v3 replay",
        "location": "A3-fable-draft.md:170,197,222",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The record-0 combined-power literal is truncated and makes the displayed arithmetic inconsistent",
        "location": "A3-fable-draft.md:22",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "The exact subtraction of published bounds is incorrectly identified as the code's retained worst-edge value",
        "location": "A3-fable-draft.md:234",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F4",
        "severity": "blocker",
        "title": "The validity paragraph falsely says every invalid artifact omits the computed bound and omits required binding fields",
        "location": "A3-fable-draft.md:236",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F5",
        "severity": "blocker",
        "title": "The monotonic-resolution restatement is rounded and fails the Section 2 literal fence",
        "location": "A3-fable-draft.md:30",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F6",
        "severity": "blocker",
        "title": "The pulse-0 stamp half-width arithmetic uses rounded bracket inputs as exact",
        "location": "A3-fable-draft.md:222",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F9",
        "severity": "blocker",
        "title": "Two value-equivalent Section 2 restatements are not byte-identical",
        "location": "A3-fable-draft.md:30,240",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F7",
        "severity": "should_fix",
        "title": "The rounding rule incorrectly includes the point anchor among outward-rounded outputs",
        "location": "A3-fable-draft.md:55",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F8",
        "severity": "should_fix",
        "title": "The 120-second deadline is a pre-cell check, not a hard total-runtime cap",
        "location": "A3-fable-draft.md:240,244",
        "defect_class": "CONTRADICTED"
      },
      {
        "id": "F10",
        "severity": "nit",
        "title": "The evidence citation for hashing points to digest-format validation rather than hash computation",
        "location": "A3-fable-draft.md:274",
        "defect_class": "UNTRACEABLE"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 /Users/edr/code/JouleWise/scripts/check_paper_replay_fence.py --draft docs/paper/draft-v1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "MEMBER 20260722T145535-e941c821",
          "COMPARED 43",
          "MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MISMATCHES 0$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -c 'import json; from pathlib import Path; from joulewise.powermetrics_fiducial import rederive_detection_from_artifacts; from joulewise.uncertainty_evidence import CLOCK_METHOD_V3; d=Path(\"/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821\"); ev=json.loads((d/\"instrument_evidence.json\").read_text()); f=rederive_detection_from_artifacts((d/\"raw/powermetrics.plist\").read_bytes(),(d/\"events.jsonl\").read_bytes(),ev[\"clock_anchor\"],anchor_method=CLOCK_METHOD_V3); print(f.fits[0])'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PulseFit(pulse_index=0, detected=True, reasons=(), amplitude_w=40.6667, robust_snr=40666.7, delta_on_s=0.016, delta_off_s=-0.0115, onset_residual_lower_s=0.014464207030298189, onset_residual_upper_s=0.017213039063451813, offset_residual_lower_s=-0.012727246583042666, offset_residual_upper_s=-0.009977831541957334)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "delta_off_s=-0\\.0115.*offset_residual_upper_s=-0\\.009977831541957334"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c 'from decimal import Decimal,getcontext; getcontext().prec=60; s=Decimal(\"0.0006869160344978743\")+Decimal(\"0.00044608116149902344\")+Decimal(\"0.0000010000000000000002\")+Decimal(\"0.000001\"); print(\"ANCHOR_SUM\",s); print(\"B_MINUS_ANCHOR\",Decimal(\"0.030067931757111657\")-Decimal(\"0.0011349971959968978\")); print(\"COVERAGE\",Decimal(1)-Decimal(\"0.95\")**59); print(\"DEPTH_WIDTH\",Decimal(\"1.5\")/(Decimal(2)**14))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ANCHOR_SUM 0.0011349971959968977402",
          "B_MINUS_ANCHOR 0.0289329345611147592",
          "COVERAGE 0.951505474750576762317803871103212325211394200541445081464152",
          "DEPTH_WIDTH 0.000091552734375"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DEPTH_WIDTH 0\\.000091552734375$"
      }
    }
  ],
  "flags": [
    {
      "id": "FLAG1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The requested worktree's ruling ends at Addendum 3; Addendum 5/item 49 is present in /Users/edr/code/JouleWise at 6447497d. All relevant implementation and fence-script hashes are identical between the two checkouts, and both Section 2 fence runs pass.",
      "needs": "Assemble the rewrite against the intended final paper head after branch reconciliation."
    }
  ]
}
```

## Findings

Draft path: `/private/tmp/claude-501/-Users-edr-code-JouleWise/5ce660ee-d53f-472d-98bc-e236206db99d/scratchpad/t26/r5/A3-fable-draft.md`

| ID | Location | Verbatim quote | Defect class | Severity | Governing file:line | Proposed correction |
|---|---:|---|---|---|---|---|
| F1 | 170, 197, 222 | “Example (pulse 0, issued artifact): *d_on* = 0.016 s, *d_off* = −0.011 s.” | CONTRADICTED | blocker | `joulewise/powermetrics_fiducial.py:1095-1271`; v3 replay through `rederive_detection_from_artifacts` | Replace or remove the issued-v2 fit example. Current-v3 replay gives `d_off = −0.0115` and changes three of the four region endpoints; the “issued artifact” label does not make v2 values examples of the v3 pipeline being specified. |
| F2 | 22 | “*p_0* = 0.925904 W” | CONTRADICTED | blocker | `joulewise/adapters/powermetrics.py:1791-1806` | Preserve the full channel sum, `0.9259043699999999 W` as executed (`0.92590437 W` as the exact decimal input sum), or explicitly label the displayed value rounded and do not use it as the operand for the following precision claim. |
| F3 | 234 | “the worst edge excursion is the difference, 0.0289329345611147592 s” | CONTRADICTED | blocker | `joulewise/powermetrics_fiducial.py:1022-1043`; `docs/paper/draft-v1.md:79` | Distinguish the exact decimal subtraction of the two published outputs from the detector’s retained maximum edge value. The code/fence value is `0.02893293456111476`; the longer literal is only the exact subtraction of the printed bound literals. |
| F4 | 236 | “*B_fiducial* is emitted, and the evidence file is marked `valid`, only if all of the following hold” / “Otherwise the bound is absent” | CONTRADICTED | blocker | `joulewise/powermetrics_fiducial.py:1412-1445,1464-1473` | Separate bound computation/emission from artifact validity. A successful fit can remain serialized in an invalid artifact; validity additionally requires all binding fields. Do not state that every invalid artifact has an absent bound. |
| F5 | 30 | “a monotonic resolution of 4.17·10⁻⁸ s” | CONTRADICTED | blocker | Retained clock stamps; `docs/paper/draft-v1.md:75`; fence V1 | Use the fenced literal `4.166666666666666e-8` in the paper’s chosen mathematical notation. |
| F6 | 222 | “*ma* − *mb* = 0.25 µs and *r* = 1 µs, so *u_on* = 1.125·10⁻⁶ s” | CONTRADICTED | blocker | `joulewise/powermetrics_fiducial.py:1067-1081`; retained pulse-0 on-stamp | The executed bracket difference is `2.500019036233425e-7 s`, and the code computes `u_on = 1.1250009518116714e-6 s`. Either use the executed value or mark every displayed operand and result as approximate. |
| F9 | 30, 240 | “the example capture used 122 859” | CONTRADICTED | blocker | `scripts/check_paper_replay_fence.py:123-126,138-145`; `docs/paper/draft-v1.md:75,79` | Copy fenced source literals byte-for-byte. The count is printed as `122{,}859` in Section 2, and the wall-resolution notation also differs at the byte level despite being value-equivalent. |
| F7 | 55 | “only the final outputs are rounded, and each is rounded outward” | CONTRADICTED | should-fix | `joulewise/uncertainty_evidence.py:1189-1196` | State that limits and bounds are rounded outward; the midpoint point-anchor uses ordinary binary64 conversion, not outward rounding. |
| F8 | 240, 244 | “at most 120 s of wall time” | CONTRADICTED | should-fix | `joulewise/powermetrics_fiducial.py:533-550,666-680` | Describe a monotonic pre-cell deadline: elapsed time is checked before each cell’s lower-bound evaluation. It is not a continuously enforced hard cap and can be crossed during the final cell evaluation. |
| F10 | Evidence 274 | “Primary bytes hashed and re-derived; stored values not inputs: pf:1104–1110, 1419–1424.” | UNTRACEABLE | nit | `scripts/validate_powermetrics_fiducial.py:2155-2163`; `joulewise/powermetrics_fiducial.py:1419-1424` | Cite the validator’s hash computation. The cited `pf:1419-1424` only validates that supplied digest strings have lowercase 64-hex syntax. |

### Detailed equation and number trace

| Draft region | Status | Independent result and governing source |
|---|---|---|
| 9–34: samplers, 100 ms interval, record fields, channel formulas, health inequality, cumulative elapsed, stamp half-width, trace intervals, pulse indices | TRACED except F2/F5 | `joulewise/adapters/powermetrics.py:57-58,1766-1833,1837-1858`; `joulewise/uncertainty_evidence.py:62-73,972-975`; `joulewise/powermetrics_fiducial.py:1067-1081,1249-1260`. The formulas for \(p_i\), \(E_i\), \(q_i\), \(u(S)\), and \(I_i\) match code. |
| 40–51: v3 capture sequence, 3 warm-ups, 5 s rests, 59 pulses, 1 s duration, irregular gaps, loop origin, 4096-square float16 work | TRACED | `joulewise/powermetrics_fiducial.py:45,61-68,355-398,1554-1585`; `scripts/validate_powermetrics_fiducial.py:1883-2057`. The first five stated gaps recompute to 2.0, 1.75, 2.25, 1.625, and 2.125 s. |
| 55–64: method identity, affine model, two unknowns, 250 µs full allowance, network-time condition | TRACED except F7 | `joulewise/uncertainty_evidence.py:20,814-868,1027-1044,1197-1223,1298-1299`. |
| 66: ordered admission/refusal rules | TRACED | `joulewise/uncertainty_evidence.py:871-1006`. The stamp, exact-input, delta, health, monotonicity, rollover, 60 s baseline, and controller-coverage conditions match. |
| 68–74: span equation, 5 ms limit, four-ulp check, 1 µs numeric pad | TRACED | `joulewise/uncertainty_evidence.py:35,42-60,310-329,997-1025`. The worked span recomputes exactly under binary64 execution. |
| 76–98: stamp, native-label, and causal equations; \(m_0\), \(k_{\mathrm{pre}}\), \(k_{\mathrm{parse}}\) | TRACED | `joulewise/uncertainty_evidence.py:721-737,1027-1075`. Crucially, \(k_{\mathrm{pre}}=e_0-r_{\mathrm{pre}}\): it differs from \(e_0\) by exactly one clock-resolution unit by design, as required. The reported \(k_{\mathrm{parse}}\) is the exact-Fraction result from the stored binary64 inputs. |
| 100–116: Fourier–Motzkin rows, boxes, exact LP, refusal order, 50 ppm, 0.25 s lag, 24 bisections | TRACED | `joulewise/uncertainty_evidence.py:61,622-679,740-811,1077-1177`. The 25/5/5 row counts and 3,330 native rows for 1,665 records are correct. |
| 106: “any exact LP solver returns the same optimal values” | UNTRACEABLE-to-code but mathematically correct | The code implements one fixed-seed exact solver at `uncertainty_evidence.py:622-679`. For a fixed feasible set and scalar objective, the optimum objective value is unique even when optimizer points are not. The caveat states this correctly. |
| 118–141: four-term anchor bound and worked anchor values | TRACED | `joulewise/uncertainty_evidence.py:1179-1234`; `r4-derivation.json:4-27`. The required sum is exactly `0.0011349971959968977402`, outward-rounding to `0.0011349971959968978`. Endpoints, point, rate interval, lag, residual diagnostic, rollovers, records, and term values trace. |
| 145–151: rate-1 trace placement, event pairing, warm-up trimming, schedule authentication | TRACED | `joulewise/adapters/powermetrics.py:1770-1785`; `joulewise/powermetrics_fiducial.py:401-441,1084-1092,1189-1263`. |
| 157–164: baseline set, overlap rule, minimum 3 intervals, median/MAD scale, spurious plateau | TRACED | `joulewise/powermetrics_fiducial.py:712-734,891-907`. Warm-up intervals do not participate. |
| 166–180: local/interior sets, amplitude/SNR thresholds, fixed amplitude, overlap model, Huber objective | TRACED except the mixed-generation example | `joulewise/powermetrics_fiducial.py:553-587,737-807`. Constants 0.75, 0.25, 10 W, SNR 10, 1.345, and 0.6725 match. |
| 182–200: explicit candidate grids and coordinate search | TRACED except F1 | `joulewise/powermetrics_fiducial.py:707-709,808-852`. Recomputed counts are 301, 298, and 2,971; there are eight one-dimensional searches, first-minimum tie resolution, strict significance, and strict 0.5 s acceptance. |
| 202–224: tolerance, branch-and-bound, projection, widening | TRACED except F1/F6 | `joulewise/powermetrics_fiducial.py:590-704,854-888`. Fourteen halvings per dimension give `0.000091552734375 s`, hence 28 path bisections at full depth. |
| 228–236: 118 excursions, maximum-plus-anchor bound, median/p95 rank, 95/95 arithmetic | TRACED except F3/F4 | `joulewise/powermetrics_fiducial.py:1022-1048,1366-1473`. The p95 is the 113th ordered value. \(1-0.95^{59}=0.9515054747\ldots\), so the 95/95 statement is correct. |
| 240–244: shared cell budget and clock origin | TRACED origin; CONTRADICTED hard-cap wording | `joulewise/powermetrics_fiducial.py:524-550,975-1010`. The budget object is created after baseline statistics and before the first fit, is shared across pulses, and excludes anchoring/trimming/authentication. |

### Fence-verified Section 2 restatements

| Restated quantity | Appendix literal | Fenced Section 2 literal | Result |
|---|---|---|---|
| Pulse count | `59` | `59` | MATCH |
| Evaluated-cell count | `122 859` | `122{,}859` / extracted `122859` | BYTE MISMATCH |
| Wall-clock resolution, scientific form | `1.0000000000000002·10⁻⁶` | `1.0000000000000002\times10^{-6}` | VALUE MATCH; BYTE MISMATCH |
| \(r_{\max}\), decimal form | `0.0000010000000000000002` | `0.0000010000000000000002` | MATCH |
| Monotonic resolution | `4.17·10⁻⁸` | `4.166666666666666\times10^{-8}` | MISMATCH |
| `pre_spawn` monotonic-before | `458736.4081875` | `458736.4081875` | MATCH |
| `first_parse` monotonic-after | `458737.509840291` | `458737.509840291` | MATCH |
| Anchor bound | `0.0011349971959968978` | `0.0011349971959968978` | MATCH |
| Final capture bound | `0.030067931757111657` | `0.030067931757111657` | MATCH |
| Exact printed subtraction | `0.0289329345611147592` | `0.0289329345611147592` | MATCH as subtraction |
| Code’s retained worst-edge value | Appendix calls the longer subtraction literal this quantity | `0.02893293456111476` | MISMATCH |

### Self-declared caveats

1. The v2/v3 caveat is a real fidelity risk and the prose must change. A current-v3 replay confirms that pulse 0’s offset optimum and three region endpoints differ from the issued-v2 rows. Labeling them “issued artifact” is transparent provenance, but they remain wrong worked values for the current-v3 algorithm specified by the appendix.

2. The exact-LP-solver caveat is correctly stated. It is not a code assertion, so it is UNTRACEABLE-to-code, but it is a valid mathematical property of the fixed LP objective values. It does not imply a unique optimizer point.

### Five named replication gaps

| Named gap | Closed? | True? |
|---|---|---|
| Baseline set and warm-up participation | Yes | Yes. Lines 149 and 157 explicitly exclude warm-ups; this matches trimming at `powermetrics_fiducial.py:1084-1092`. |
| Explicit onset-candidate grid with integer extent | Yes | Yes. Lines 182–188 give the set, \(N=\lceil R/s\rceil\), index range, clipping, and correct counts. |
| Channel sums for \(p_i\) and \(E_i\) | Yes | The equations are true; the record-0 \(p_0\) worked literal is not, per F2. |
| Origin of the 120 s work clock | Yes | Yes. Line 242 locates construction after baseline statistics and before fitting. The separate hard-cap wording still needs F8. |
| `pre`, `parse`, `post`, \(k_{\mathrm{pre}}\), \(k_{\mathrm{parse}}\), and \(e_0\) defined before displayed use | Yes | Yes. The stamp names appear at lines 42–49, \(e_0\) at line 22, and the two \(k\) values are introduced and defined at lines 89–92. |

### VERDICT

No. Not every equation and number in the rewrite is correct against the code and fence-verified values. The four-term anchor sum and the designed one-resolution-unit \(k_{\mathrm{pre}}\) offset are both stated correctly, but seven blocker defects remain.

## Residual risk

The requested worktree predates Addendum 5, while the parent checkout contains item 49. This did not limit the fidelity audit: the relevant implementation and fence-script files are byte-identical between checkouts, the primary capture bytes were available, and both Section 2 fence runs compared all 43 values with zero mismatches.