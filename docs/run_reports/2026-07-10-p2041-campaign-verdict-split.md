# P2-041 Campaign Verdict Split (2026-07-10)

## Scope And Authority

Implemented queue row P2-041 on `impl/p2041` without committing. Authority was
`docs/specs/c027/analysis_engine_trio.md` Component C as amended by
`docs/specs/c027/ADJUDICATION.md`: H3 assigns the campaign-level D-014 recovery
gate and raw provenance to this row; B14 fixes the reason vocabulary; P2-006 L2
interpretation remains gated on both P2-041 and P2-037.

The worktree started clean at `2d6117a`. The pre-change canonical baseline was:

```text
Ran 910 tests in 33.321s

OK (skipped=12)
```

The loud six-frozen-corpus acceptance-gate skip was present as expected.

## Per-Unit Status

| Unit | Status | Evidence |
|---|---|---|
| Collection/claim split | implemented | `joulewise.campaign_verdict.v2` final log row; collection and readiness have independent objects and vocabularies |
| One-bundle legacy flip | implemented | clean arbitrary campaign is collection `usable`, readiness `not_assessed`; old verdict term absent from the runner and current tests |
| Member classification split | implemented | `collection_integrity_flags` and `claim_evidence_flags`; idle suspicion and reducer precheck failures no longer invalidate collection |
| Readiness consumer | implemented | fixed-n contrast slot checks, metric-specific reducer prechecks/reasons, collection usability, cap state, idle-only suspicion, and repetition/block completeness |
| Analysis-manifest preflight | implemented locally | pinned v1 identity, frozen state, order hash, config byte hashes, IDs, and contrast presence; invalid manifests refuse execution with named reasons |
| H3 campaign cooldown | implemented | same controller `cooldown_gate` rule (rolling 30 s, 10%, 300 s), run between independent physical config invocations and attached to the following member |
| First-run rule | implemented | exactly the first physical invocation in each campaign provenance session is declared `first_run_exempt` before execution |
| Raw cooldown provenance | implemented | immutable JSONL under `campaign_manifests/raw/`, relative path + SHA-256 + record count in the gate note; missing/hash-invalid raw evidence becomes unknown on resume |
| Persistent campaign provenance | implemented | atomic incremental `joulewise.campaign_provenance.v1` manifest plus repeated gate evidence in per-config and final campaign-log rows |
| Stable reason vocabulary | implemented/documented | P2-041 copies reducer reasons and uses the adjudicated campaign subset; the complete B14 v1 set was appended to D-057 |
| P2-006 interpretation gate | unchanged | P2-041 implementation alone does not open L2; P2-037 remains required |

Collection verdict vocabulary is `usable`, `partial`, `blocked`, `invalid`.
Claim-input readiness vocabulary is `ready_for_analysis`,
`not_ready_for_analysis`, `not_assessed`. Readiness never changes the campaign
process exit status and is explicitly not a claim outcome.

## Mutation-Style Tests

New tests:

- `test_missing_campaign_cooldown_evidence_fails_closed_with_named_reason`
- `test_cooldown_cap_hit_propagates_without_poisoning_collection`
- `test_explicit_campaign_cooldown_evidence_allows_ready_for_analysis`
- `test_recovered_cooldown_without_raw_provenance_fails_closed`
- `test_analysis_manifest_config_hash_mismatch_refuses_execution`
- `test_campaign_provenance_records_first_run_exemption_and_unknown_mock_gate`

Flipped/renamed legacy tests:

- `test_one_bundle_campaign_is_usable_and_claim_readiness_not_assessed`
- `test_idle_suspect_member_is_collection_usable_but_claim_evidence_flagged`

The clean gross-request fixture deliberately carries idle suspicion in the
positive readiness test, proving the STA-5 metric separation. Existing prompt
hash, waiver, missing-member, execution-order, resume, and process-failure tests
continue to cover collection integrity.

## Verification

Focused:

```text
python3 -m unittest tests.test_run_campaign tests.test_experiment tests.test_uncertainty_p2029
Ran 99 tests in 11.210s
OK
```

Canonical final suite:

```text
Ran 916 tests in 33.924s

OK (skipped=12)
```

Additional checks:

- `python3 scripts/claims_lint.py --mode ap --mode registry` -> `claims_lint: clean`
- `python3 -m py_compile scripts/run_campaign.py` -> exit 0
- `git diff --check` -> clean
- no old one-bundle verdict term remains in `scripts/run_campaign.py` or
  `tests/test_run_campaign.py`

## Deviations And Contradictions

1. P2-042 is not present at this branch head, despite the trio spec's preferred
   P2-042 -> P2-041 order. P2-041 therefore includes a bounded, fail-closed
   consumer seam for the pinned `joulewise.analysis_manifest.v1` fields. It
   does not build manifests. The spec's `analysis-registry` lint mode is also
   unavailable on this head; the installed linter advertises only
   `all/ap/registry/pack/forbidden`.
2. Component C5 assigns the reducer-field rename to P2-041, while the live
   queue's P2-037 acceptance cell assigns `_window_claim_eligibility` ->
   `window_evidence_precheck` to P2-037 and the user-scoped P2-041 units did not
   authorize a reducer-version/schema migration. This tranche does not perform
   that cross-schema rename. The readiness consumer prefers
   `window_evidence_precheck` when present and consumes the merged P2-040
   `claim_eligibility` stable-reason surface otherwise. The lead must adjudicate
   the ownership conflict before P2-037 lands.
3. No live/quiet-machine measurement was run. Mock campaign tests exercise the
   unknown/fail-closed route; the shared controller gate already owns live and
   fake-clock rule tests. Per repository safety, this agent session did not run
   a quiet-window campaign.
4. `origin/main` advanced by nine RPT-001/P2-039 commits during verification.
   This worktree was intentionally not merged/rebased; final state is
   `impl/p2041...origin/main [behind 9]` for lead pathspec handling.

## Double-Check List For Lead

- Confirm C5/P2-037 reducer-field rename ownership before accepting a positive
  current-era readiness path as final.
- Re-run the focused and canonical suites after applying the pathspecs on the
  integrated head (P2-039/RPT-001 landed concurrently).
- When P2-042 lands, run its analysis-manifest validator and
  `claims_lint --mode analysis-registry`; remove any redundant local validation
  only after equivalent fail-closed coverage is proven.
- Verify a fixture-injected non-mock campaign gate writes a raw JSONL whose
  recorded SHA-256 matches bytes, without starting a quiet-machine campaign.
- Keep P2-006 L2 interpretation closed until P2-037 independently repeats all
  structural, cooldown, reducer-reason, and floor checks.

## Changed Files

- `scripts/run_campaign.py`
- `tests/test_run_campaign.py`
- `docs/contracts/run_bundle_layout.md`
- `docs/decision_log.md`
- `RUN_STATE.md`
- `TASK_QUEUE.md`
- this report
