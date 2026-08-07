codex
# U4 implementation plan — synthetic three-window live-ledger regression

## Baseline and constraints

Implement against U1 commit `f665dd4` (`impl/d117-u1-ledger-session` and the local `origin/…` ref both point there). A fresh remote lookup was impossible because network DNS is unavailable; no fetch was performed because this was explicitly read-only.

U4 remains logically downstream of U1 and U2. The non-successor portion can be prepared against U1; U4 must not merge with successor tests still skipped.

## Exact `WRITE_SCOPE`

Only:

- `tests/fixtures/calibration_live_three_window/fixture_spec.json`
- `tests/test_calibration_live_three_window.py`

No production modules, configuration, registry, bookkeeping, generated state, or existing tests are in scope.

## Fixture specification

`fixture_spec.json` will contain:

- Schema/version identifier for the U4 fixture.
- The expected production issued-anchor facts:
  - acceptance artifact SHA-256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`;
  - cutoff sequence `76`;
  - cutoff head `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`;
  - inventory `{valid: 30, systematic-invalid: 2, ordinary-invalid: 6}`.
- Exact six-field epoch copied from the issued artifact.
- One complete ten-field T1 vector:
  - `hardware_model`
  - `os_build`
  - `powermetrics_sha256`
  - `sampling_interval_ms`
  - `anchor_method_version`
  - `mlx_version`
  - `pulse_protocol_id`
  - `power_policy`
  - `estimator_revision`
  - `protocol_sha256`
- Three explicit window records: `alpha`, `beta`, `gamma`, each with unique session, window, plan, evidence-root, and runs-root suffixes.
- Window timing far enough apart to make causal/stale mutations unambiguous:
  - alpha science `[1_000_000, 1_000_100]`, endpoints `999_990/1_000_110`;
  - beta `[2_000_000, 2_000_100]`, endpoints `1_999_990/2_000_110`;
  - gamma `[3_000_000, 3_000_100]`, endpoints `2_999_990/3_000_110`.
- Endpoint decimal bounds below the issued range ceiling and with drift below the `0.010818` screen:
  - alpha `0.025/0.026`;
  - beta `0.027/0.028`;
  - gamma `0.029/0.030`.
- Expected capability/finalization sequences:
  - alpha `77/78/79`;
  - beta `80/81/82`;
  - gamma `83/84/85`.
- Expected candidate count `6`, imported candidate count `0`, final sequence `85`, and allowance literal `0.010818`.

Identifiers must be explicitly synthetic; they must not pre-empt U5–U7’s final campaign identifiers.

## Construction algorithm

`tests/test_calibration_live_three_window.py` will define a reusable `FixtureHarness`.

1. Load and byte-authenticate the checked-in issued acceptance artifact. Assert its exact SHA, sequence-76 cutoff, 38-member prior set, and 30/2/6 inventory.

2. Materialize 38 synthetic custody directories in a temporary checkout. Preserve the issued artifact’s attempt IDs and dispositions. Each directory gets deterministic:
   - `raw/powermetrics.plist`
   - `events.jsonl`
   - `power_trace.csv`
   - `instrument_evidence.json`
   - `manifest.json`

3. Build the historical disposition table and custody manifest, then call the public `prepare_historical_import`/`bootstrap_historical_import` path. Assert:
   - 76 receipts;
   - alternating historical reservation/finalization semantics;
   - 38 content-distinct observations;
   - 30 valid, two systematic-invalid, six ordinary-invalid;
   - every observation is import-marked;
   - the chain and generated sequence-76 head pin authenticate.

4. Construct a structurally valid synthetic issued acceptance artifact:
   - clone the production artifact’s policy/numeric fields;
   - bind its cutoff to the synthetic sequence-76 head;
   - replace the prior set with the 38 generated observations;
   - replace the 19 derivation-corpus identities/hashes with the first 19 generated valid members while retaining the original bound lexemes and arithmetic;
   - recompute `derivation_sha256`;
   - assert `_valid_acceptance_bound` before use.
   
   Patch only the acceptance-loader boundary to supply this artifact. Do not patch ledger loading, candidate discovery, binding validation, or bracket evaluation.

5. For each window, starting from the current pinned head:
   - call `append_bracket_session_receipt` with exactly two immutable slots;
   - call `finalize_bracket_session_slot` directly for `pre`, then `post`;
   - do not emit optional writer-claim receipts, preserving the memo’s three-receipt/session sequence model;
   - obtain the terminal pin through `terminal_head_pin_for_session`;
   - load a pinned snapshot with the sequence-76 baseline;
   - build the window binding with `build_calibration_bracket_binding`;
   - advance the synthetic committed pin before opening the next session.

6. After gamma, load exactly one immutable sequence-85 snapshot. Call `discover_calibration_candidates` once and reuse that exact six-candidate tuple and snapshot for all three evaluations.

7. Candidate custody remains fully hash-authenticated. Only the raw-physics refit is replaced with a deterministic test double returning each evidence file’s exact decimal bound; this keeps receipt, manifest, evidence, content-ID, epoch, T1, protocol, and path authentication live.

8. Structural mutation tests use a common `_rechain()` helper that recomputes sequence, predecessor, and receipt digests. This distinguishes semantic refusal from trivial broken-hash refusal.

## Named proof-obligation tests

| Test | Required proof |
|---|---|
| `test_issued_prefix_has_exact_76_receipt_38_observation_30_2_6_semantics` | Both the production anchor and generated prefix carry the ruled issuance shape. |
| `test_final_snapshot_discovers_exactly_six_live_and_zero_imported_candidates` | Six live candidates; no import-marked observation reaches candidate loading. |
| `test_alpha_beta_gamma_bind_only_their_own_pre_post_pairs` | Each binding resolves to its own two attempt/content/receipt digests. |
| `test_all_six_live_endpoints_are_same_epoch_causal_fresh_protocol_and_t1_valid` | Exact epoch/T1/protocol equality and causal/fresh timing for every endpoint. |
| `test_neighboring_endpoint_cannot_substitute_for_any_bound_endpoint` | Replacing either endpoint with any of the other five candidates refuses. |
| `test_all_three_verdicts_consume_same_complete_final_candidate_universe` | All verdicts pass only with the same final snapshot and complete six-candidate tuple; discovery occurs once. |
| `test_three_receipt_sessions_terminate_at_sequence_85` | Receipt events and sequences are exactly `76 + 3 × 3 = 85`. |
| `test_d110_never_zero_allowance_is_embedded_once_in_all_three_verdicts` | All three results record `max(drift, 0.010818)`, value `0.010818`, `embedding_count == 1`, and the correct operative decimal. |

## Named refusal-vector tests

### Import boundary

| Test | Setup and oracle |
|---|---|
| `test_import_marker_removal_refuses_authenticated_issuance_prefix` | Convert one fully re-chained import reservation/finalization pair to ordinary live events. Evaluation must refuse with `calibration_ledger_baseline_missing`. |
| `test_import_candidate_leakage_refuses_complete_universe_check` | Add a candidate derived from an import observation to the supplied tuple. Expect `calibration_ledger_off_ledger_artifact`. |
| `test_candidate_discovery_never_invokes_loader_for_import_marked_observations` | Spy on the observation-to-candidate loader; it must be called exactly six times, all after sequence 76. |

### Session/finalization integrity

| Test | Setup and oracle |
|---|---|
| `test_missing_session_or_finalization_receipt_refuses` | Subtests remove a capability, pre finalization, or post finalization and fully re-chain. Require session conflict/open refusal and no passing evaluation. |
| `test_duplicate_session_or_finalization_receipt_refuses` | Duplicate an open receipt and, separately, a finalization. Expect `calibration_ledger_bracket_session_conflict`. |
| `test_reordered_finalization_receipts_refuse` | Put post before pre and re-chain. Expect session conflict. |
| `test_conflicting_session_or_finalization_identity_refuses` | Change session identity, reserved attempt, custody, or plan hash on a later event and re-chain. Expect session conflict. |
| `test_open_session_refuses_claim_evaluation_and_terminal_pin` | Stop after a valid pre finalization. Snapshot contains `calibration_ledger_bracket_session_open`; terminal-pin creation and evaluation both refuse. |
| `test_abandoned_slot_without_governed_abort_refuses` | Finalize pre as abandoned but omit `abort_bracket_session`. The session remains open and cannot yield a terminal pin or candidate. |

### Head and chain authority

| Test | Setup and oracle |
|---|---|
| `test_physical_head_pin_mismatch_refuses` | Keep the pin at 76 while the physical chain reaches 85. Expect `calibration_ledger_head_mismatch`. |
| `test_rollback_from_pinned_terminal_head_refuses` | Pin sequence 85, truncate the physical chain to 84. Expect `calibration_ledger_rollback`. |
| `test_sibling_fork_refuses_even_when_pin_names_fork_tip` | Append a correctly hashed sibling transition and pin that tip. Expect `calibration_ledger_chain_conflict`. |
| `test_uncommitted_terminal_head_pin_refuses` | In a temporary Git repo, commit the sequence-76 pin, advance it to 85 without committing, and load with committed-pin enforcement. Expect `calibration_ledger_head_uncommitted`. |

### Complete observation universe

| Test | Setup and oracle |
|---|---|
| `test_omitted_registered_observation_refuses` | Remove one of six candidates from the supplied tuple. Expect `calibration_ledger_off_ledger_artifact`. |
| `test_added_registered_observation_invalidates_frozen_six_candidate_universe` | Append and pin a seventh authentic valid live observation, then supply the old six. Expect off-ledger refusal. |
| `test_duplicate_supplied_observation_refuses` | Duplicate one candidate while retaining tuple length. Expect off-ledger refusal from the duplicate/cardinality guard. |
| `test_off_ledger_observation_refuses` | Add a well-formed candidate with no receipt. Expect off-ledger refusal. |
| `test_content_substituted_observation_refuses` | Keep attempt/receipt identity but replace content or artifact hashes. Expect off-ledger refusal. |

### Binding integrity

| Test | Setup and oracle |
|---|---|
| `test_missing_bracket_binding_refuses` | Evaluate a session-backed window with no binding. Expect `calibration_bracket_binding_missing`. |
| `test_tampered_bracket_binding_refuses` | Alter an endpoint or identity without updating the binding digest. Expect `calibration_bracket_binding_invalid`. |
| `test_swapped_bracket_binding_endpoints_refuse` | Swap pre/post and recompute the outer digest. Exact role comparison must still reject it. |
| `test_cross_window_bracket_binding_refuses` | Supply alpha’s authentic binding to beta, and vice versa. Expect binding-invalid refusal. |

### Endpoint eligibility

| Test | Setup and oracle |
|---|---|
| `test_noncausal_bound_endpoint_refuses` | Move a bound pre after science start or post before science end; rebuild evidence and receipts. Expect bracket-missing/binding refusal, never neighbor substitution. |
| `test_stale_bound_endpoint_refuses` | Place a causal endpoint beyond `MAX_AGE_S`. Expect `instrument_calibration_stale`. |
| `test_t1_mismatched_bound_endpoint_refuses` | Make reservation, evidence, and receipt internally consistent under a different T1 value while science keeps the original T1. Expect `instrument_calibration_bracket_missing`. |
| `test_non_v3_protocol_endpoint_refuses` | Make one authentic endpoint v2 rather than the claim-bearing v3 protocol. Expect bracket-missing refusal. |
| `test_identity_epoch_mismatch_refuses` | Change one acceptance identity field in the evaluated science binding. Expect `calibration_acceptance_bound_stale` with that field listed. |
| `test_systematic_live_observation_refuses_under_prior_artifact` | Classify one live observation systematic-invalid. Expect stale/refusal and the systematic trigger; no successor is consulted. |

### D-102 triggers available under U1

| Test | Setup and oracle |
|---|---|
| `test_range_expanding_live_observation_refuses_prior_artifact_and_requires_successor` | Set one valid endpoint above `0.03355875667989999`. The prior artifact must become stale with `new_valid_same_identity_capture_expands_observed_range`. |
| `test_observation_count_at_38_refuses_prior_artifact_and_requires_successor` | Extend the base 30+6 valid inventory with two further authenticated valid same-epoch observations. At 38, require `corpus_doubles_from_19_to_38` and stale refusal. |

## Tests staged behind U2

Keep these methods in the same module to preserve the exact U4 write scope. While U2’s public API/design brief is unavailable, mark them with an explicit `unittest.skip` reason. Imports of U2 APIs must occur inside the skipped methods so the module remains importable.

Before U4 merges, U2 must land, the skips must be removed, and all five tests must pass:

- `test_range_expanding_live_observation_passes_only_with_authenticated_successor`
  - Judge the range expander under the prior artifact, stop before science, build/register a successor over the complete governed prefix, finalize the session, and prove the final bracket passes only under that successor.

- `test_count_boundary_passes_only_with_authenticated_successor`
  - Reach exactly 38 valid same-epoch observations, refuse the prior artifact, then prove a deterministic registered successor restores eligibility.

- `test_successor_cannot_absorb_systematic_observation_as_valid`
  - Attempt to include or relabel a systematic observation in the successor corpus. U2 must refuse; a successor cannot launder it.

- `test_successor_refuses_omitted_authenticated_prefix_observation`
  - Omit any import or finalized live observation at or before the successor cutoff, recompute otherwise self-consistent bytes, and require registry/validator refusal.

- `test_successor_refuses_changed_authenticated_prefix_observation`
  - Change content ID, disposition, epoch, attempt identity, or receipt/cutoff identity in the authenticated prefix and require refusal.

Use skip-marking rather than a separate module: a second module is outside the frozen U4 scope and makes it easier for the canonical suite to overlook the staged vectors. Skips are temporary branch state, not an acceptable merged U4 outcome.

## Verification

During pre-U2 staging:

```sh
python3 -m unittest tests.test_calibration_live_three_window
```

Expected: 38 active tests pass and exactly five U2-dependent tests skip.

After U2 lands:

```sh
python3 -m unittest tests.test_calibration_live_three_window
python3 -m unittest tests.test_calibration_live_three_window
python3 -m unittest discover -s tests
```

Acceptance:

- 43 U4 tests pass;
- zero U4 skips remain;
- two consecutive focused runs produce identical semantic receipts, bindings, successor bytes, and trigger outcomes for the same fixture root;
- canonical suite passes;
- no production or bookkeeping files changed.

## Estimated size

- `fixture_spec.json`: approximately 180–300 lines.
- Test harness and 43 tests: approximately 1,100–1,450 lines.
- Total: approximately 1,300–1,750 lines.
- Focused runtime target: under 20 seconds by constructing one pristine base tree per class and copying it for mutation tests.

## Risks and mitigations

- **Sequence-85 versus U1 claim receipts:** U1 added optional persistent slot-claim events. Exercising those through the production writer would yield five receipts per window and terminate at 91. This plan follows the memo’s explicit 85 oracle by calling the public open/finalize APIs directly. Existing U1 tests retain claim/concurrency coverage.
- **Synthetic acceptance authentication:** synthetic historical evidence cannot reproduce the off-repo production content hashes. U4 therefore validates the real issued artifact separately, then uses a structurally validated synthetic issued artifact at the loader boundary. All downstream ledger, custody, candidate, binding, and evaluation checks remain live.
- **Mutation tests becoming trivial:** every semantic mutation is re-chained and re-pinned unless the vector specifically targets hashes or heads.
- **Reason stacking:** tests assert the exact refusal when only one contract should fire; deliberately compound malformed cases assert the required primary taxonomy plus a failed verdict.
- **U2 API uncertainty:** successor semantics and oracles are frozen above, but the mechanical adapter cannot be completed until the U2 brief/public API lands.
- **Runtime from 44 custody trees:** build the pristine fixture once and copy it per test; do not regenerate all physics artifacts for every vector.

## Lead questions

1. Confirm that sequence 85 is the normative U4 oracle and that optional U1 slot-claim receipts are intentionally excluded from this semantic regression. Recommended: keep 85 here and add any claim-enabled production-path integration check under U1’s writer tests, not U4.
2. Ratify the successor corpus rule: all content-distinct, valid, same-epoch observations through the authenticated cutoff; systematic, ordinary-invalid, abandoned, unresolved, and duplicates remain recorded but excluded.
3. Confirm that U4 may use the structurally valid synthetic issued artifact described above rather than requiring the unavailable off-repo production ledger/custody bytes.
4. Decide whether the five temporary successor skips may exist on an intermediate U4 branch. Recommended: yes during staging, but never in the merged U4 commit.
5. Confirm `f665dd4` remains the intended U1 integration base, since a fresh origin lookup was unavailable in this read-only environment.
tokens used
