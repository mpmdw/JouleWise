# CG-4(e) desk simulation — 2026-09-24

Source: cold gate CLAIMGATE-01 and addendum, `docs/process_traces/2026-09-24-activation-278ebc9e/66-coldgate-packet-claimgate/`; exact R1–R4 replacement text in `92b-claimgate-v2-refuter-astra.md` in the same activation. This rerun uses the four trace-19 generator forms, six blocks per envelope, independent envelope shocks, same-epoch calibration, Holm m=5 (one target plus four missing), production `estimate_scale_floor`, `estimate_paired_blocks`, `tost_p_value`, `holm_adjust`, and `evaluate_claim`. It is CPU-only model evidence, not live hardware validation. `run.py`/`models.py` adapt `19-desk-simulations/sim.py` and the addendum’s `ex-88-probe-probe.py`; `perm.c` implements the same 2,000-repetition one-sided pooled permutation statistic for Monte Carlo throughput.

## CG-1 / CG-2

Each cell has 5,000 trials. `B/σ` is 0.5, 1, or 2. Direction false admission is tested at δ=0; 2σ and 5σ power are measured. Equivalence registers Δ=F_est+B+2σ after simulated calibration and before simulated analysis observations; false admission is measured at the true boundary δ=Δ and power at δ=0. Separate hypothetical claim shapes are measured, not jointly admitted on one data set.

| Generator | k | Max direction false admission | 2σ power at B/σ=.5 / 1 / 2 | 5σ power range | Max equivalence boundary false admission | Equivalence null power range |
|---|---:|---:|---|---:|---:|---:|
| gaussian | 5 | 0.04% | 75.72% / 63.78% / 2.26% | 100.00%–100.00% | 0.00% | 99.66%–99.98% |
| gaussian | 8 | 0.00% | 99.96% / 95.98% / 2.28% | 100.00%–100.00% | 0.00% | 100.00%–100.00% |
| heavy_t3 | 5 | 0.00% | 78.34% / 65.18% / 2.24% | 99.84%–99.90% | 0.00% | 99.02%–99.64% |
| heavy_t3 | 8 | 0.00% | 99.36% / 95.30% / 2.46% | 99.98%–99.98% | 0.00% | 99.88%–99.92% |
| linear_drift | 5 | 0.00% | 76.72% / 63.70% / 2.20% | 100.00%–100.00% | 0.00% | 99.60%–100.00% |
| linear_drift | 8 | 0.00% | 99.98% / 96.18% / 2.06% | 100.00%–100.00% | 0.00% | 100.00%–100.00% |
| shared_local | 5 | 0.04% | 52.30% / 36.42% / 1.76% | 99.72%–100.00% | 0.00% | 96.56%–98.72% |
| shared_local | 8 | 0.00% | 99.14% / 82.82% / 2.44% | 100.00%–100.00% | 0.00% | 99.92%–100.00% |

Maximum direction false admission: 0.04% (ceiling 5%). Maximum equivalence boundary false admission: 0.00% (ceiling 5%).

## CG-3 fixed r7 corpus

The checked-in r7 artifact supplies 17 member values across ten windows. Computed with Decimal from the authenticated lexemes and displayed to 18–20 significant digits: w̄=27.05126130322395995 ms, s_w=2.70955485752457996 ms, s_old=2.46085620769463617 ms, prediction half-width=5.20934969771577647 ms, Δ_loc=8.61299672693122658 ms, strict location radius=3.40364702921545011 ms. The ruling's earlier illustration printed 27.052, 2.711, 2.461, 5.212, 8.613, and 3.401 ms respectively; the R5 corrected six-decimal values are 27.051261, 2.709555, 2.460856, 5.209350, 8.612997, and 3.403647 ms. Null and boundary cells have 10,000 trials; detection cells have 2,000 trials, each with 2,000 permutations. Level is the operative r7 `preflight_level_screen_s`.

| Generator | m | No-change false FAIL | Boundary false PASS | +3σ detection | +5σ detection | ×4 variance detection | ×16 variance detection |
|---|---:|---:|---:|---:|---:|---:|
| gaussian | 8 | 4.18% | 0.14% | 98.45% | 100.00% | 51.70% | 97.00% |
| gaussian | 12 | 3.79% | 0.08% | 99.20% | 100.00% | 57.80% | 99.30% |
| heavy_t3 | 8 | 4.36% | 0.12% | 98.45% | 100.00% | 37.70% | 88.85% |
| heavy_t3 | 12 | 3.69% | 0.08% | 98.80% | 100.00% | 37.65% | 92.60% |
| linear_drift | 8 | 4.59% | 0.16% | 98.75% | 100.00% | 64.50% | 98.85% |
| linear_drift | 12 | 3.94% | 0.05% | 99.00% | 100.00% | 70.95% | 99.85% |
| shared_local | 8 | 3.53% | 0.07% | 99.30% | 100.00% | 31.15% | 90.15% |
| shared_local | 12 | 3.09% | 0.06% | 98.90% | 100.00% | 28.80% | 94.00% |

No-change false FAIL range: 3.09–4.59% (every generator/m <=5%). Boundary false PASS range: 0.05–0.16% (every generator/m <=5%).

## Simulated-old-corpus sensitivity

This changes the old corpus in each trial and recomputes the reference and margin. It is sensitivity only; the ruled acceptance condition uses fixed r7. Each cell has 2,000 trials.

| Generator | m=8 / 12 no-change false FAIL | m=8 / 12 boundary false PASS |
|---|---:|---:|
| gaussian | 4.85% / 4.65% | 2.10% / 1.75% |
| heavy_t3 | 7.00% / 5.40% | 1.85% / 1.60% |
| linear_drift | 1.80% / 2.25% | 1.40% / 1.50% |
| shared_local | 7.20% / 6.05% | 2.55% / 3.00% |

## Replay

```sh
clang -O3 -shared -fPIC -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX15.4.sdk docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/perm.c -o /tmp/claimgate_v2_perm.dylib
CLAIMGATE_PERM_LIB=/tmp/claimgate_v2_perm.dylib python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/run.py claims 5000 > docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/claims.jsonl
CLAIMGATE_PERM_LIB=/tmp/claimgate_v2_perm.dylib python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/run.py nights 10000 > docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/nights.jsonl
python3 -B docs/process_traces/2026-09-24-activation-278ebc9e/94-claimgate-v2-simulation/summarize.py
```

The C permutation implementation is a simulation accelerator. The production epoch checker uses the same one-sided variance-ratio ordering with deterministic Decimal replay. Both calculate `(hits+1)/(reps+1)`.
