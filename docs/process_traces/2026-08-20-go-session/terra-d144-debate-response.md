```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "GO unchanged: SF-1 is a non-blocking S5 reporting gap, but neither proposed one-line change is safe for the merge wave.",
  "workspace": {
    "base_requested": "7d4454e",
    "base_mode": "exact",
    "head_start": "afb7d5705add3475cd016177a8f8fa1dd02a814e",
    "head_end": "afb7d5705add3475cd016177a8f8fa1dd02a814e",
    "upstream_end": null,
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "GO",
    "sf1_merge_wave": "CONTEST: do not ride either proposed one-line form; require a non-gating persisted diagnostic plus an end-to-end regression.",
    "findings": [
      {"id":"SF-1","severity":"should_fix","disposition":"CONCUR","reason":"Executed mixed v2+v3 fixture without diagnostics returns status=passed and reasons=(); S5 observability is absent, but direct stored-v2 claim barriers remain fail-closed."},
      {"id":"SF-2","severity":"nit","disposition":"CONTEST (down-grade)","reason":"The constants coincide today and missing bindings cannot enter a valid ledger observation; this is future-policy drift, not present should-fix behavior."},
      {"id":"SF-3","severity":"should_fix","disposition":"CONCUR","reason":"Current static schema sets equal both registries, but no test enforces future synchronization; the Python gate remains the primary defense."},
      {"id":"SF-4","severity":"nit","disposition":"CONTEST (down-grade)","reason":"The capture already occurred after runtime cleanup; only the buffered cleanup-completed event moves ahead of it. No claim-evidence timing change was shown."},
      {"id":"SF-5","severity":"should_fix","disposition":"CONCUR","reason":"R2 S1 is broader than the three-file literal guard; current code is clean but the guard is fragile."},
      {"id":"N-1","severity":"nit","disposition":"CONCUR","reason":"CLOCK_METHOD_V2 is an unused import."},
      {"id":"N-2","severity":"nit","disposition":"CONCUR","reason":"The canonical schema map is mutable while related policy sets are immutable."},
      {"id":"N-3","severity":"nit","disposition":"CONCUR","reason":"The live-record arithmetic comment is false although the asserted count is correct."},
      {"id":"N-4","severity":"nit","disposition":"CONCUR","reason":"The synthetic oracle normalizes the active D147 row and narrows that test's observation scope."},
      {"id":"N-5","severity":"nit","disposition":"CONTEST (not an actionable defect)","reason":"The alleged order-dependent failure remains unisolated and unreproduced; retain only as a verification gap."},
      {"id":"N-6","severity":"nit","disposition":"CONCUR","reason":"The emitted bare --check command fails after freeze; preserve mode is required. This is inherited documentation/replay drift."}
    ]
  },
  "verification": [
    {
      "id":"V1",
      "kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_calibration_bracketing.CalibrationBracketingTests.test_v2_ledger_candidate_reports_era_rejection_not_custody_failure tests.test_calibration_bracketing.CalibrationBracketingTests.test_v1_ledger_candidate_reports_era_rejection_not_custody_failure",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 0.004s","OK"]},
      "expected":{"exit_code":0,"tail_regex":"Ran 2 tests.*OK"}
    },
    {
      "id":"V2",
      "kind":"inspection",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -c 'from types import SimpleNamespace; from joulewise.calibration_bracketing import _capture_pipeline_refusal_for_observation; from joulewise.uncertainty_evidence import capture_pipeline_refusal; print(\"ledger_missing=\"+str(_capture_pipeline_refusal_for_observation(SimpleNamespace(t1_bindings={})))) ; print(\"claim_missing=\"+str(capture_pipeline_refusal({\"uncertainty_evidence\":{\"clock_anchor\":{}}})))'",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["ledger_missing=capture_pipeline_superseded","claim_missing=capture_pipeline_absent"]},
      "expected":{"exit_code":0,"tail_regex":"ledger_missing=capture_pipeline_superseded.*claim_missing=capture_pipeline_absent"}
    },
    {
      "id":"V3",
      "kind":"test",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_mint_policy_resolver_guard.MintPolicyResolverGuardTests.test_mint_lane_has_no_copied_bracket_screen_literals tests.test_gen_state.TestRefreshedStateFidelity.test_exact_live_id_set",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 0.001s","OK"]},
      "expected":{"exit_code":0,"tail_regex":"Ran 2 tests.*OK"}
    },
    {
      "id":"V4",
      "kind":"smoke",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py --check; printf 'exit=%s\\n' $?",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["generation failed: the current frozen identity requires preserve mode","exit=1"]},
      "expected":{"exit_code":0,"tail_regex":"requires preserve mode.*exit=1"}
    },
    {
      "id":"V5",
      "kind":"lint",
      "cmd":"git diff --check 7d4454e..afb7d57 -- joulewise/ scripts/ configs/ tests/",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":[]},
      "expected":{"exit_code":0,"tail_regex":"^$"}
    }
  ],
  "flags": [
    {
      "id":"F1",
      "kind":"environment",
      "level":"nonblocking",
      "text":"This read-only seat has no usable writable temporary directory. Replaying N-5's multi-module run and preserve-mode checks for two packs is blocked by tempfile, not an artifact failure.",
      "needs":"Use the merge runner's writable scratch for those optional reproductions."
    },
    {
      "id":"F2",
      "kind":"residual_risk",
      "level":"nonblocking",
      "text":"The checkout contains only the current ledger head pin, not the authoritative live ledger body; live mixed-era occupancy cannot be established here.",
      "needs":"None for GO; verify only if deciding to implement SF-1 now."
    }
  ]
}
```

## Findings

FINAL: **GO unchanged.** SF-1 should not ride the wave in either proposed one-line form.

### Should-fix

- **SF-1 — SHOULD-FIX — CONCUR on defect/severity; CONTEST on fix shape.** I executed the mixed v2-plus-v3 fixture with `diagnostics` omitted: it returned `status=passed`, `reasons=()`, despite one superseded observation. The direct claim lanes are not silent: stored v2 bundles are refused by the shared S3 helper. This is a mixed-era calibration-ledger reporting gap, not a claim-soundness blocker. Removing `if not candidates:` would add the reason to whole-window’s global refusal set and reject valid v3 claims merely because retained history exists. Passing an otherwise-unused diagnostics list at the three callers also does nothing. S5 calls for a non-gating, persisted report channel.

- **SF-3 — SHOULD-FIX — CONCUR.** The current n19/n17 schema sets exactly match both Python registries, and the Python mint gate still rejects unregistered IDs. There is no registry-sync regression, though, so a future generation can weaken the schema’s defense-in-depth conditional.

- **SF-5 — SHOULD-FIX — CONCUR.** The guard checks only three fixed files, while R2 S1’s policy is mint-lane-wide. No forbidden literal exists now; this is correctly “correct but fragile.”

### Nits

- **SF-2 — NIT — CONTEST (down-grade).** The two constants match today, and a missing method cannot reach a valid ledger observation. Keep a future-policy test if desired, but this is not present should-fix behavior.

- **SF-4 — NIT — CONTEST (down-grade).** Before and after the change, post-run observation occurs after `runtime.cleanup()`. `_complete_stage()` only buffers an event, so the demonstrated change is event ordering, not post-teardown evidence timing.

- **N-1, N-2, N-3, N-4, N-6 — NIT — CONCUR.** These are respectively a dead import, mutable canonical map, incorrect count arithmetic comment, narrowed synthetic-oracle coverage, and stale bare `--check` replay instruction.

- **N-5 — CONTEST: not an actionable defect.** The cache is now keyed by anchor method, but the cited failure is still unisolated and unreproduced. Retain it as a nonblocking verification gap, not a defect finding.

## Residual risk

My earlier clean pass concentrated on frozen-surface recomputation and the stored-v2 claim-barrier walk. It did not perform Opus’s caller-census/diagnostic reachability check, static schema-to-registry synchronization check, lifecycle event-order inspection, guard-boundary review, state-kernel test-seam review, cross-module cache-order experiment, or post-freeze emitted-command replay. Those per-layer checks explain the different finding counts; they do not contradict the prior claim-soundness result.