# OSCTX-MVP-01 v2.2: the cell runs production's own measurement

Written 2026-09-24 ≈19:40 PDT, before any MVP data. v2.1 (08) stands except where amended here. The forcing question came from Ed: are some of the reviewers' problems byproducts of the artificial minimal workload?

## Finding

**Yes, partly.** A bespoke 3.2 s, 256-token request made three problems larger than production has them:
- **Boundary misattribution.** A 3 s window at 118–248 ms cadence holds 13–27 samples.
- **Bespoke integration and anchoring.** The reviewers could only ask that it "match production".
- **An arbitrary request length inside the margin argument.**

Production already has a fixed workload and a vetted measurement path. The d117 v3 decode contrast config for Qwen2.5-7B-Instruct-4bit (`configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/01_decode_contrast_blocks_01_05/d117c15v7-decode-contrast-b01-b2.json`) uses:
- a 128-token prompt and **exactly 512 output tokens**, with EOS suppressed under the `fixed_budget_exact` output policy (`joulewise/adapters/mlx_runtime.py:600`). The fixed length is production practice, not an artefact of this diagnostic;
- 1 warm-up, a 30 s idle baseline and powermetrics at 10 Hz;
- its own eligibility prechecks and uncertainty terms.

One shell run of that config, executed at the bench at ≈19:35 with agents active:

| Quantity | Value |
|---|---|
| Wall time | 66.5 s |
| Request window | 6.40 s, 57 in-window samples; production's cadence precheck (≥ 4 samples) passes at 55.8 |
| Gross energy | 257.7 J |
| Idle-subtracted energy | 193.4 J |
| Net energy per output token | **0.3778 J** |
| Inter-token throughput | **83.62 tok/s** |
| Idle baseline | 10.04 ± 0.41 W over 34 s |
| Median sample interval | 113 ms |
| Production drift bound | 32.6 J |

## Amendments

- **B1. The cell workload is production.** Each cell runs `python -m joulewise run <cfg> --runs-dir <cell>/runs` **twice** back to back, on a copy of the config above. The only edits are `run_id` and `run_metadata.tags`: the campaign tags and `launch_lineage_required` are removed. Those are custody gates for real campaigns and play no part in measurement. The workload, the sampler argv, the anchoring, the integration and the idle subtraction are production's, byte for byte.
- **B2. The endpoints are production's own summary fields**, averaged over the cell's 2 runs:
  - E = `energy_output_token_j` (idle-subtracted J per output token);
  - R = `inter_token_throughput_tokens_s`.
  The v2.1 margins and statistics are unchanged (δ = 3 %, 99.375 % paired-t on the log-ratio, Williams stages).
- **B3. Secondary, reported and not decision inputs:**
  - `gross_energy_j`;
  - `idle_baseline.power_w_mean`, the idle floor per arm. This speaks directly to Ed's "lagging OS processes";
  - `idle_mean_uncertainty.median_sample_interval_s` (the cadence);
  - production's `window_evidence_precheck` pass/fail;
  - `energy_bound_terms_j`;
  - the bundle status.
  A bundle whose status is not `succeeded`, or whose prechecks fail, invalidates the cell. The cell is reported, and the block re-runs as in A5.
- **B4. The bespoke energy code is dropped.** v2.1's boundary-bound and two-integral checks are dropped with it; production's prechecks and bounds replace them. The bespoke 256-token request and the CPU probe leave the decision path. The CPU probe stays as a mechanism probe in the wrapper, run **after** the production runs, so it cannot disturb them.
- **B5. The wrapper.** The launchd job (or SH) runs `zsh -c 'exec <python> wrapper.py …'`. The wrapper records ancestry and QoS, starts the census thread (A5, unchanged), pre-reads the model files, runs the two production runs as child processes (so they inherit the context), then runs the CPU probe. It samples the child's `ps -o pri,nice` and ancestry.
- **B6. Budget.** A cell is ≈2.4 min. Stage 1 in U (1 warm-up, 18 cells, B ×2) is ≈50 min. Stage 0 (6 cells) is ≈15 min. The U–S–U sandwich is ≈22 min.

## Why fixed tokens remain right for this diagnostic (Ed asked)

The paper's headline estimand is energy per correct answer on a fixed-difficulty problem set (COUNCIL-407-01; AP-5M v5). This diagnostic asks something narrower: does the launch context change the joules measured for **identical** work? That needs byte-identical work in every arm, which a fixed-length greedy request provides. Energy per correct answer is a sum of per-request energies divided by the count of correct answers, so a per-token bias from the launch context passes into it multiplicatively. This check is a precondition for the headline metric, not a substitute for it.
