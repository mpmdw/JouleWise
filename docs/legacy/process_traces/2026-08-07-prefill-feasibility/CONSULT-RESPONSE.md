```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "MARGINAL: the exact-workload historical prefill ABBA diagnostic is only slightly above the approximate effective bar, so retain decode-only contrast unless a prospectively approved longer prompt is used.",
  "workspace": {
    "base_requested": "/Users/edr/code/JouleWise",
    "base_mode": "exact",
    "head_start": "03841c858c0b251f7f5bd44d31ec0e910978c8ef",
    "head_end": "03841c858c0b251f7f5bd44d31ec0e910978c8ef",
    "upstream_end": "03841c858c0b251f7f5bd44d31ec0e910978c8ef",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "label": "Every quantitative result and estimate in this report is NON-CLAIM / DIAGNOSTIC.",
    "classification": "MARGINAL",
    "rows": [
      {
        "row": "Existing 128-token prefill contrast",
        "action": "do_not_start",
        "reason": "The diagnostic point delta exceeds the approximate practical bar by too little margin, and the bar is not an exact hard literal."
      },
      {
        "row": "Prospectively frozen 256-token prefill contrast",
        "action": "needs_ruling",
        "reason": "The length sensitivity is promising, but no historical 7B corpus above 128 prompt tokens exists and workload resizing is a preregistration decision."
      },
      {
        "row": "Prefill floors with decode-only model contrast",
        "action": "wait_for",
        "reason": "Recommended default fork; collection must occur in a clean lead-controlled quiet-machine session."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "find runs_window_contrast_20260730 -mindepth 2 -maxdepth 2 -path '*/swdec-contrast-*/summary_metrics.json' -print0 | xargs -0 jq -e '.phase_energy_j.prefill | numbers' >/dev/null; printf 'metric_key_check_exit=%s\\n' \"$?\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "metric_key_check_exit=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "metric_key_check_exit=0"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "find runs_window_contrast_20260730 -mindepth 2 -maxdepth 2 -path '*/swdec-contrast-*/metadata.json' -print0 | xargs -0 jq -r '[.model.name,.workload_provenance.prompt.realized_token_count,.workload_provenance.prompt.token_ids_sha256,.workload_provenance.output_policy.requested_tokens,.workload_provenance.output_policy.emitted_tokens] | @tsv' | sort | uniq -c",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "20 Qwen2.5-1.5B-Instruct-4bit 128 75644f38b1d2e90edfd10b1bff572378198b7083173141667d1c98125feaf706 512 512",
          "20 Qwen2.5-7B-Instruct-4bit 128 75644f38b1d2e90edfd10b1bff572378198b7083173141667d1c98125feaf706 512 512"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "20 Qwen2.5-7B-Instruct-4bit"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --stat && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## main...origin/main"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## main\\.\\.\\.origin/main"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "D-083 says the approximately 5 J expression is a practical consequence of two separately enforced gates, not one summed acceptance threshold.",
      "needs": "Preserve that wording in any parent-facing plan or preregistration."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No repository historical 7B corpus uses more than 128 prompt tokens; longer-prompt sensitivity is an extrapolation.",
      "needs": "If lengthening is chosen, freeze the workload prospectively and treat the fresh arm as the first direct check."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "CLAIMS_STATUS reflects the earlier D-110 hard block, while later D-116 records the remint prerequisites satisfied and MINT-GENERALIZE-01 unblocked.",
      "needs": "Parent should verify current remint status before freezing a claim-window plan; this does not change the desk-feasibility verdict."
    }
  ]
}
```

Global label: every quantitative value below is **NON-CLAIM / DIAGNOSTIC**.

## Desk recommendation

**VERDICT: MARGINAL.**

At the historically measured workload—Qwen2.5 1.5B versus 7B, identical 128-token prompt and 512-token fixed output—the best ABBA estimate is a 7B−1.5B prefill delta of **5.809930 J**. The decision-log practical bar is only approximately **5 J**, leaving **0.809930 J**, or about **16%**, of point-estimate headroom.

That is not enough to recommend adding the contrast at its existing 128-token shape. The default fork should therefore be:

- claim prefill floors;
- retain the model contrast as decode-only;
- describe the 128-token prefill contrast as infeasible-to-clear-with-comfort in limitations.

A prospectively frozen 256-token prompt could change the answer: proportional sensitivity gives approximately **11.619860 J**, comfortably above the approximate bar. Because no historical 7B corpus above 128 prompt tokens exists, that is a sizing projection, not demonstrated evidence.

## Verified doctrine and conflict check

[D-078 clause 11](</Users/edr/code/JouleWise/docs/decision_log.md:4599>) says:

- attribution error is roughly **0.7–1.0 J** per phase member;
- the instrument is attribution-limited rather than noise-limited;
- the practical effective clearable effect is **floor + claim-side bound, approximately 5 J for phase contrasts**;
- workload length is the free lever because the attribution error is approximately duration-independent while the effect scales with workload.

There is no exact **5.000000 J** threshold in the decision log. It is explicitly approximate.

[D-083](</Users/edr/code/JouleWise/docs/decision_log.md:5130>) adds an important wording correction: the expression is not a single summed acceptance gate. The floor gate and claim decision interval are enforced separately; approximately **5 J** remains the correct practical description of what an effect must jointly clear. Thus, if “effective claim bar” in the prompt meant one literal acceptance threshold, the decision log narrows that wording.

D-110 does not void the PASSED windows themselves, but it makes the old minted floors non-claim-bearing because their never-zero allowance was understated. Consequently, old point energies remain usable here as diagnostics; old floor or interval values cannot be promoted.

## Best evidence: direct matched ABBA

Metric key confirmed in all members: `phase_energy_j.prefill`.

Root: `runs_window_contrast_20260730`, whole-window verdict **PASSED**. This was registered as a decode contrast, so its prefill field is incidental and off-manifest—useful for this desk triage only.

Workload comparability is unusually strong:

- both models realized exactly **128 prompt tokens**;
- both used prompt-token hash `75644f38b1d2e90edfd10b1bff572378198b7083173141667d1c98125feaf706`;
- both requested and emitted exactly **512 output tokens**;
- both used `df_ph_decode`, fixed-budget exact generation, and one repetition.

Files:

- 1.5B: `runs_window_contrast_20260730/swdec-contrast-b{01..10}-{a1,a2}/summary_metrics.json`
- 7B: `runs_window_contrast_20260730/swdec-contrast-b{01..10}-{b1,b2}/summary_metrics.json`

| Model | Per-member prefill energies by block | Mean | Sample SD | Min–max; range | n | Status |
|---|---|---:|---:|---:|---:|---|
| 1.5B | b01 1.885440/1.539441; b02 1.586462/1.861176; b03 1.889846/1.727033; b04 1.789189/1.838999; b05 1.419751/1.890385; b06 1.746431/1.870292; b07 1.467694/1.763132; b08 1.623674/1.788001; b09 1.845281/1.714564; b10 1.558800/1.452191 J | 1.712889 J | 0.158925 J | 1.419751–1.890385 J; 0.470634 J | 20 | Clean/PASSED window; prefill value off-manifest |
| 7B | b01 7.457512/7.684994; b02 7.479750/7.621606; b03 7.535448/7.549410; b04 7.776995/7.481640; b05 7.199367/7.481595; b06 7.539043/7.829077; b07 7.593805/7.557487; b08 7.410829/7.380489; b09 7.408870/7.441063; b10 7.610961/7.416439 J | 7.522819 J | 0.142814 J | 7.199367–7.829077 J; 0.629711 J | 20 | Clean/PASSED window; prefill value off-manifest |

The ten block deltas are **5.858813, 5.826859, 5.733989, 5.815223, 5.685413, 5.875698, 5.960233, 5.689822, 5.645045, and 6.008204 J**.

Their mean is **5.809930 J**, sample SD **0.121023 J**, and range **5.645045–6.008204 J**. A repeatability-only 95% interval around the block mean is approximately **5.723–5.896 J**, but that interval does not replace the attribution-bound decision interval.

## Independent corroboration and corpus disposition

| Root and files | Workload | Mean; spread | n | Disposition |
|---|---|---:|---:|---|
| `runs_window_a10_20260725/p2015-df-ph-short-prefill-abs-r{01..10}/summary_metrics.json` | 1.5B; 128 prompt, 64 output | 1.649076 J; SD 0.131227 J; range 1.387866–1.818284 J | 10 | Clean/PASSED |
| `runs_window_7bfloor_20260729/sw7bfloor-df-ph-decode-abs-r{01..10}/summary_metrics.json` | 7B; 128 prompt, 512 output | 7.552262 J; SD 0.194722 J; range 7.373120–7.916055 J | 10 | Clean/PASSED |
| Cross-window subtraction of the two preceding rows | Matched prompt length; output budget differs but metric isolates prefill | 5.903186 J | — | Corroborating diagnostic only |
| `runs_window_a10_20260725/p2015-df-ph-prefill-abs-r{01..10}/summary_metrics.json` | 1.5B; 4096 prompt, 64 output | 51.072749 J; SD 0.121716 J; range 50.846637–51.254767 J | 10 | Clean/PASSED |
| `runs_window_b_20260726/p2015-df-cmp-abba-ph-prefill-b{01..10}-{a1,a2,b1,b2}/summary_metrics.json` | 1.5B; 4096 prompt, 64 output | 51.242708 J; SD 0.241066 J; range 50.874749–51.930955 J | 40 | FAILED; D-113 claim-retired |
| `runs/p2_015_floors_window_a/p2015-df-ph-prefill-abs-r{01..10}/summary_metrics.json` | 1.5B; 4096 prompt, 64 output | 40.452004 J; SD 0.622442 J; range 39.476172–41.321647 J | 10 | Pre-D-078 time-anchor-defective; void for claims |
| `runs/p2_015_floors_window_a/p2015-df-ph-short-prefill-abs-r{01..10}/summary_metrics.json` | 1.5B; 128 prompt, 64 output | 0.080930 J; SD 0.011251 J; range 0.064470–0.099860 J | 10 | Pre-D-078 time-anchor-defective; void for claims |

The old short-prefill value’s disagreement with current-era values is itself a useful warning against using pre-D-078 point magnitudes uncritically.

As actually present locally, `runs_window_a9_20260724` contains seven reference summaries and no named prefill-floor member summaries; the usable clean 1.5B floor members are in a10.

A repository-wide scan found historical 7B summaries only at **128 prompt / 512 output tokens**. No long-prompt 7B diagnostic exists.

## Contrast uncertainty composition

For a 7B−1.5B contrast, energy points subtract but uncertainty magnitudes add. D-078’s contrast rule is `Σ|cᵢ|wᵢ`, not root-sum-square.

In the direct ABBA corpus:

- mean 1.5B prefill anchor half-width: **0.768096 J**;
- mean 7B prefill anchor half-width: **1.039955 J**;
- ABBA block-composed contrast half-width: mean **1.808052 J**, range **1.713501–1.908734 J**.

Applying that historical composed half-width to the point delta gives a diagnostic interval of approximately **4.001878–7.617982 J**. Its lower side falls below the practical approximately **5 J** bar. Moreover, D-110 shows that the old minted uncertainty was understated, so these historical widths must not be used to argue for a lower bar.

D-082’s “max, never sum” rule concerns absolute versus comparative components inside one floor cell. It does not authorize RSS or non-composition of the two model measurements in a model contrast.

## Length sensitivity

A purely proportional diagnostic inversion gives nominal break-even at approximately **110 prompt tokens**, which explains why the observed 128-token point estimate is only barely over the practical bar.

Projected from the matched 128-token ABBA delta:

| Prompt length | Projected delta | Point ratio to approximate bar | Interpretation |
|---:|---:|---:|---|
| 128 tokens | 5.809930 J observed | 1.16× | Marginal |
| 192 tokens | 8.714895 J projected | 1.74× | Likely clear, but still extrapolated |
| 256 tokens | 11.619860 J projected | 2.32× | Recommended sizing if the contrast is retained |

The 1.5B clean corpus supports approximate scaling: multiplying its 128-token mean by **32** predicts **52.770445 J**, versus **51.072749 J** observed at 4096 tokens, an approximately **3.3%** difference. That is encouraging, but it is not a substitute for missing long-prompt 7B evidence.

## Rough ABBA arm and runtime

For a retained, lengthened contrast:

- fixed A/B/B/A order;
- ten blocks;
- forty cross-model members total;
- same prompt-token hash across models;
- prospective prompt length of at least 256 tokens;
- `phase_energy_j.prefill` explicitly registered before collection.

The proven 128-token contrast’s forty members took approximately **106.7 minutes** from the first member completion to the last. Window B’s forty-member prefill ABBA took approximately **109.4 minutes**. Thus budget roughly **110 minutes** core, or about **130 minutes** with a 20% member-failure margin.

The proven ten-absolute companion took roughly **25–28 minutes**. A ten-absolute plus forty-null floor design is therefore about **135 minutes** of science-member time before calibrations and references.

Adding a separate forty-member cross-model contrast produces about **245 minutes** of core science-member time before references, calibration, adjudication, and failure margin. That likely exceeds the project’s two-to-four-hour preferred window envelope. If the parent retains the contrast, splitting floor and contrast collection into separate quiet windows is safer than compressing both.

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Existing 128-token contrast | do_not_start | None | Too little margin over the approximate bar |
| Prospectively sized 256-token contrast | needs_ruling | Workload-size/preregistration ruling and current claim-window readiness gates | Adds about 110 core minutes; likely collides with the floor window’s runtime envelope |
| Prefill floors; contrast decode-only | wait_for | Clean, zero-agent quiet-machine window | Default recommendation; lowest additional runtime and policy risk |

## Critical path

A lengthened contrast requires the workload-sizing ruling before plan freeze. Plan freeze then precedes the clean quiet-machine window. If the parent does not approve that sizing change, the fork terminates at prefill floors plus decode-only contrast.

## Caveats and parent double-checks

- Confirm that `phase_energy_j.prefill` is added to the prospective analysis manifest; its presence in decode summaries does not register it as a claim metric.
- Verify current D-110/D-116 remint state and use newly governed floors, not historical floor literals.
- Decide whether a 256-token prompt is acceptable scientifically; changing input length changes the estimand.
- Confirm the new prompt realizes identical token IDs under both pinned tokenizers.
- Recompute the full window budget with pre/post calibration, seven reference members, cooldown, and at least 20% failure margin.
- Confirm whether existing clean 1.5B absolute evidence may pair with a fresh comparative component or whether the owning plan requires fresh absolute members too.
- Do not use Window B for any claim cell. Its only permitted role here is labelled diagnostic magnitude.

## Exact replay commands

Decision text:

```bash
sed -n '4057,4695p' docs/decision_log.md
sed -n '4835,4910p' docs/decision_log.md
sed -n '5070,5198p' docs/decision_log.md
sed -n '6279,6375p' docs/decision_log.md
sed -n '7082,7175p' docs/decision_log.md
sed -n '7241,7338p' docs/decision_log.md
rg -n 'D-078|D-102|D-110|D-113|04_phase_prefill_abba' CLAIMS_STATUS.md docs/decision_log.md
```

Direct ABBA extraction:

```bash
find runs_window_contrast_20260730 -mindepth 2 -maxdepth 2 -path '*/swdec-contrast-*/summary_metrics.json' -print0 |
  xargs -0 jq -r '[(input_filename|split("/")[-2]), .phase_energy_j.prefill, .phase_energy_j.decode] | @tsv' |
  sort -V
```

Metric and workload checks:

```bash
find runs_window_contrast_20260730 -mindepth 2 -maxdepth 2 -path '*/swdec-contrast-*/summary_metrics.json' -print0 |
  xargs -0 jq -e '.phase_energy_j.prefill | numbers' >/dev/null

find runs_window_contrast_20260730 -mindepth 2 -maxdepth 2 -path '*/swdec-contrast-*/metadata.json' -print0 |
  xargs -0 jq -r '[.model.name,.workload_provenance.prompt.realized_token_count,.workload_provenance.prompt.token_ids_sha256,.workload_provenance.output_policy.requested_tokens,.workload_provenance.output_policy.emitted_tokens] | @tsv' |
  sort | uniq -c
```

Corpus verdicts:

```bash
for root in runs_window_a10_20260725 runs_window_7bfloor_20260729 runs_window_contrast_20260730 runs_window_b_20260726; do
  echo "$root"
  jq -c 'select((.record_type // "") | test("verdict")) | {record_type,status,decision,passed,conditions,reason,failure_reason,timestamp,runs_dir}' "$root/campaign_log.jsonl" | tail -5
done
```

Runtime evidence:

```bash
jq -r 'select((.run_id // "")|startswith("swdec-contrast")) | [.timestamp,.status,.run_id] | @tsv' runs_window_contrast_20260730/campaign_log.jsonl
jq -r 'select((.run_id // "")|startswith("p2015-df-cmp-abba-ph-prefill")) | [.timestamp,.status,.run_id] | @tsv' runs_window_b_20260726/campaign_log.jsonl
jq -r 'select((.run_id // "")|startswith("sw7bfloor-df-ph-decode-abs")) | [.timestamp,.status,.run_id] | @tsv' runs_window_7bfloor_20260729/campaign_log.jsonl
```

Workspace verification:

```bash
git rev-parse HEAD
git rev-parse --abbrev-ref HEAD
git rev-parse '@{upstream}'
git diff --stat
git status --short --branch
```