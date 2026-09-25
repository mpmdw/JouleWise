# Open facts and inspection tails

This packet reports repository state at branch head `4a78cc021386aaaee405ec258360c0aae9f628c7` (`git rev-parse HEAD`, output that SHA). No measurement, network lookup or model load was performed.

## Unsettled facts and what would settle them

1. **Alternative attention for A3.** Local MLX model-tree and Hugging Face cache names do not establish that any installed artifact is a compatible 4-bit sliding-window/linear/hybrid contrast. A read-only scan of each candidate's config, complete weight inventory and MLX architecture support would identify a candidate; a governed load/32k smoke under an authorized agent or quiet gate would establish execution and memory fit. The existing strategy explicitly requires verified named artifacts and executed attention paths for the rider (docs/strategy/2026-08-09-extension-axes-roadmap.md:986).
2. **32k trace duration and one-night fit.** The panel declares 40,960 context for the two Qwen3 models (configs/model_panels/qwen3_4bit.json:16,49), and the current quiet protocol is 9,000 s, twelve 600 s envelopes (configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:17-18,98). A bench throughput/memory smoke with the exact prompt, cap, EOS policy and model would settle duration; a reviewed A3 night registration would settle whether a continuous trace gets a longer envelope.
3. **KM003C accuracy and synchrony.** Archived reads establish communication and watts but not a calibration certificate, latency, clock alignment, stable sampling period or IOReport comparison (/Users/edr/night-archive/km003c-tools-20260923/meter_paired.txt:1-6). Calibration documentation, a paired timed bench and a registered alignment method would settle these. The tool prints time.time() on receipt, not a device timestamp (/Users/edr/night-archive/km003c-tools-20260923/km003c_probe.py:120-133).
4. **Bit-width coverage.** The admitted Qwen3 pair is 4-bit only (configs/model_panels/qwen3_4bit.json:5-16,38-49). An artifact inventory and admission/pinning decision would settle which 3/6/8-bit or bf16 cells can be registered for B1.
5. **D-165 simulation.** The review's 0.47 pass probability at w/σ=1 was not independently replayed by this scout (record 02:68; bench status same file:26). A deterministic simulation using the current `comparative_false_effect_floor` / `dominance_ratio` implementation, with declared data-generating assumptions and seeds, would settle that numerical assertion (joulewise/detection_floor.py:1132-1140; joulewise/dominance_closeout.py:517-537).
6. **Claim-gate scale.** The floor uses a one-new-observation prediction component, while claims.py gates a supplied estimate against that floor (joulewise/detection_floor.py:871-881; joulewise/analysis_engine/claims.py:343-352). A simulation across n under the registered estimand and the separate interval/floor discipline would settle whether the resulting claim is mis-scaled and by how much.
7. **Exact A1/A2 run budget.** AP-5M estimates 12 or 23 nights for its present two-model, two-arm design, not for six budgets and votes (docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:1297-1298). A factorized pilot and amended registration would determine envelope and night counts.
8. **A1 batching at k=8/16.** The review reports static B=2/4 feasibility, not k=8/16 energy or memory fit (record 02:117-121). A bench-only MLX batch smoke on pinned weights would settle fit; governed power capture would settle the energy curve.
9. **Network-time switch removal.** The bench reports that A267 plus network-time attestation already retained 11/12 captures (record 02:10-11,22). An audited monotonic-to-epoch mapping and clean pilot under the new stamp path would settle whether toggling can be removed without widening timing error.

## Reproducible read-only inventory tails

- `find /Users/edr/jw_models/mlx-community -maxdepth 1 -type d -print | sort` ended with `Qwen3-1.7B-4bit`, `Qwen3-4B-4bit`, `Qwen3-8B-4bit`, `Qwen3.5-122B-A10B-4bit`; `du -sh /Users/edr/jw_models/mlx-community/* | sort -h | tail -7` gave `939M ...Qwen3-1.7B-4bit`, `2.1G ...Qwen3-4B-4bit`, `4.3G ...Qwen3-8B-4bit`, `65G ...Qwen3.5-122B-A10B-4bit`. The complete tree list also had Qwen2.5 0.5B/1.5B/7B.
- `find /Users/edr/.cache/huggingface/hub -maxdepth 1 -type d -name 'models--*' -print | sort` returned DSpark Qwen3-4B block7, Qwen2.5 0.5B/7B, Qwen3-4B and DFlash Qwen3-4B; `du -sh` on DSpark/DFlash returned `2.6G` and `1.0G`.
- `ls -la /Users/edr/night-archive/km003c-tools-20260923` listed `km003c_probe.py`, `meter_paired.txt`, `venv-km003c-requirements.txt` and `km003c-protocol-research/`.
- `rg -n 'km003c|KM003C' joulewise scripts configs tests` returned no lines (exit 1): no repository-local KM003C reader was located by that search.

## Ten line checks

Each row is the exact output tail of `sed -n '<line>p' <file>` at the source head, with leading indentation omitted here:

| Source | Pasted output |
|---|---|
| docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md:129 | `- Force generation out to about 32k tokens and measure J/token in 1k-token bins. At 8B each bin is tens of joules, so it is easy to resolve.` |
| docs/decision_log.md:10737 | `and amends item 28: the dominance RATIO **R ≥ 2** (per component, per` |
| configs/model_panels/qwen3_4bit.json:16 | `"context_window": 40960,` |
| joulewise/adapters/mlx_runtime.py:727 | `original_eos_ids = self._suppress_eos() if suppress_eos else None` |
| configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:98 | `"window_max_s": 9000` |
| docs/process_traces/2026-09-24-activation-a65fb4fa/07d-a282-ap5m-draft-v4.md:529 | `> **Fixed n and pilot.** A 16-problem sizing pilot, disjoint from test problems, never reported as a result, may set only` |
| docs/process_traces/2026-09-24-activation-a65fb4fa/02d-a291-contract-v4-self-contained.md:272 | `never the mapping's insertion order.» [FT-6]` |
| configs/campaigns/d117_contrast_v5/generate_configs.py:208 | `ABBA_POSITIONS = (("A", "A1"), ("B", "B1"), ("B", "B2"), ("A", "A2"))` |
| joulewise/analysis_engine/claims.py:349 | `if margin is None or margin <= 0.0 or method != "tost_v1":` |
| docs/process_traces/2026-09-24-interactive-02a24110/01-ed-rulings-harvest-and-reply-miss.md:44 | `AP-5M registers the estimate-level floor check.` |
