# Phase 3 Exit Checklist

Phase 3 is complete only when every required item has evidence or a
documented fallback execution. Companion plan: `docs/phase_3/phase_3_plan.md`.

## Evidence Matrix

| Item | Kind | Status | Required Evidence | Where Recorded |
|---|---|---|---|---|
| 3.0.0 kv-size helper | required | pending | tool + tests matching hand calculations; actual-vs-predicted deltas recorded after spikes | test suite + `kv_feasibility.md` |
| 3.0.1 mlx-lm replay verdict | required | pending | commands, file size vs predicted, greedy-diff result, verdict code | `docs/phase_3/kv_feasibility.md` |
| 3.0.2 llama.cpp replay verdict (same-machine) | required | pending | as 3.0.1 | `kv_feasibility.md` |
| 3.0.2 llama.cpp cross-machine portability | required | pending | CUDA-save -> Metal-restore result with pinned versions and GGUF hash; explicit yes/no/partial | `kv_feasibility.md` |
| 3.0.3 vLLM verdict | required (time-boxed) | pending | version, APIs surveyed, attempt log, verdict | `kv_feasibility.md` |
| 3.0.4 pairing matrix | required | pending | every planned pairing marked feasible-with-runtime or infeasible-with-reason | `kv_feasibility.md` |
| Schema v0.2 | required | pending | tests incl. v0.1 backward compat; new example configs validate | test suite |
| Transfer microbenchmark | required | pending | loopback CI test + at least one real link's energy/GiB with uncertainty (or documented hardware blocker) | run report + bundles |
| Offline split decomposition | required | pending | >=1 pairing with prefill/transfer/deserialize/decode energy + uncertainty; equivalence checks pass; composite bundles validate | run reports + bundles |
| Live split | stretch | pending | one live split decomposed, or explicit drop note (no evidence burden) | run report |
| Interconnect sweep dataset | required | pending | >=2 links × >=2 prompt lengths × >=1 pairing, n>=3; executed-vs-planned matrix with reasons for gaps | manifests + session reports |
| Clock-offset discipline | required | pending | every multi-node bundle records offset bound; reducer flags sub-bound intervals | bundle metadata + reducer tests |
| Borrow-window runbook | required before window | pending | step-by-step session script rehearsed on available hardware | `docs/phase_3/borrow_runbook.md` |
| Risk register updated | required | pending | R-004/R-005/R-006/R-011 statuses reflect outcomes | `docs/risk_register.md` |

## Phase 4 Readiness Gate

Phase 4 may start when:

- The crossover dataset meets the acceptance bar (or its documented
  fallback shape is final - no more split data is expected).
- All bundles intended for analysis pass `validate-bundle`.
- Monolithic references exist for every pairing in the dataset (same model,
  same config-hash discipline).
- Stage accounting definitions (serialize/transfer/deserialize/decode)
  were applied consistently - spot-check three bundles across pairings.

Phase 4 should not start while hardware sessions that could still change
the dataset are scheduled; analysis of a moving dataset wastes the
figure-pipeline work.
