# A93/A94 implementation notes

## Severable units

Unit 1 owns `joulewise/arm_readiness_evidence.py` and
`tests/test_arm_readiness_evidence_packauth.py`. Its functions are
`_generator_preserve_capability`, `_generator_frozen_receipt_constant`,
`_generator_invocation`,
`_recorded_generator_check`, `_require_regenerated_generator_result`,
`_generator_command`, `_recorded_projected_pack_authentication`,
`_frozen_receipt_constant_relation`, and `_derive_pack_authentication`.

Unit 2 owns `joulewise/arm_readiness.py`,
`tests/test_receipt_histsem.py`, and
`docs/contracts/receipt_histsem_verifier.md`. Its functions are
`_histsem_authenticate_legacy_item`,
`_histsem_rederive_pack_authentication`, and
`verify_receipt_histsem_pack`. Unit 2 composes Unit 1's syntax-only generator
classification and projected anchor/replay boundary; Unit 1 does not depend on
Unit 2, so Unit 2 can be dropped without changing Unit 1.

## Derivation-mode classification

1. The authenticated, plan-pinned generator bytes are parsed with `ast.parse`.
   They are never imported, executed speculatively, or queried through
   `--help` for capability discovery.
2. An AST call that declares `--preserve-current-frozen-bytes` with
   `BooleanOptionalAction` exposes an explicit selection. Authentication
   always supplies `--no-preserve-current-frozen-bytes` and records
   `derivation_mode: regenerated`. An explicitly selected preserve call is
   recorded as `derivation_mode: echo`.
3. Preserve-capability classification and constant extraction are independent.
   A flagless historical generator is admitted when its AST contains no
   preserve identifier/attribute, regardless of the presence, syntax, or value
   of `CURRENT_FROZEN_RECEIPT_SHA256`. Its bare `--check` is classified as
   `regenerated`. A generator with a preserve mechanism but no explicit
   `BooleanOptionalAction` flag refuses, as does a flagless preserve request.
4. A projected pack runs the anchored generator under the same explicit
   no-preserve rule (or the AST-admitted historical bare rule), then composes
   that regeneration with the existing byte-exact U11 projection replay.
5. `_require_regenerated_generator_result` rejects every `echo` result, so an
   echo cannot produce the authored six-key fact's
   `pack_generator_check_status: PASS`.
6. `CURRENT_FROZEN_RECEIPT_SHA256` is extracted by a total diagnostic function
   that never raises. The extraction status is `absent`, `readable`,
   `duplicated`, `non_literal`, `malformed`, or `source_unreadable`. Its relation
   to the authenticated current D-134 receipt is recorded as a named source
   check with `authentication_dependency: false`; authentication never reads
   the value, status, or relation.

## Frozen-receipt constant relation vocabulary

`absent` means there is no top-level constant assignment. `no_current_receipt`
means a readable constant exists but the plan names no current D-134 receipt.
`matches_current` means exact equality with the current receipt digest, and
`names_predecessor` means exact equality with the predecessor receipt digest.
`unrelated` means a readable digest equals neither. `unreadable` covers a
duplicated, computed/non-literal, malformed, or source-unreadable constant; the
more precise cause remains in `constant_extraction_status`. Every relation is
diagnostic-only.

## Regression falsification

The original A93/A94 tests were copied into a clean local clone checked out at
the unmodified session-start `HEAD`, then executed with
`/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest`; both original
pre-change commands exited 1. The FIX-seat regressions were run against the
accepted pre-fix working tree before their cures, and the accepted audit's
flagless-generator control supplied the constant-presence message. The table
records the exact decisive messages observed in those runs (long tracebacks
and Python 3.14 tar deprecation warnings omitted).

| Regression | Mutation / control | Observed failure against unmodified code |
|---|---|---|
| `test_preserve_authentication_refuses_canonical_committed_freeze_receipt_tamper_with_regenerated_sidecar` | Canonically alter `freeze-0001.json.pack_identity.pack_root`, regenerate its GNU sidecar, and commit; request an explicit preserve classification. | `TypeError: _recorded_generator_check() got an unexpected keyword argument 'preserve_current_frozen_bytes'` |
| `test_stale_current_frozen_receipt_constant_is_detected_but_not_an_authentication_dependency` | Authenticate the current projected/frozen v2 coordinate whose constant names its predecessor. | `AttributeError: module 'joulewise.arm_readiness_evidence' has no attribute '_frozen_receipt_constant_relation'` |
| `test_preserve_echo_accepts_science_row_tamper_but_cannot_set_generator_pass` | Append a newline to one committed science row; raw preserve returns 0, then request classification and the regenerated-only guard. | `TypeError: _recorded_generator_check() got an unexpected keyword argument 'preserve_current_frozen_bytes'` |
| `test_external_pinned_input_drift_is_checked_in_derivation_mode` | Emit an unfrozen successor, append a newline to its pinned acceptance JSON, observe preserve rc=0 and no-preserve refusal, then require echo classification. | `TypeError: _recorded_generator_check() got an unexpected keyword argument 'preserve_current_frozen_bytes'` |
| `test_projected_pack_authentication_uses_no_preserve_anchor_when_constant_is_stale` | Build a projected pre-freeze fixture whose modern generator names a predecessor digest. | `AssertionError: '--check' != '--no-preserve-current-frozen-bytes'` |
| `test_recorded_anchor_replay_refuses_historical_science_mutation` | Check out the recorded historical coordinate, append a newline to a generated science row, commit it, and request recorded regeneration. | `AttributeError: module 'joulewise.arm_readiness' has no attribute '_histsem_rederive_pack_authentication'` |
| `test_recorded_anchor_replay_refuses_unresolvable_or_off_lineage_commit` | Coherently rewrite source, receipt, receipt sidecar, freeze, freeze sidecar, plan, plan sidecar, and the in-memory pin row to an absent 40-hex anchor. | `AssertionError: 'histsem_commit_off_lineage' != 'histsem_commit_unresolvable'` |
| `test_projected_pack_pack_auth_receipt_survives_histsem_regeneration_gate` | Author and freeze a projected PACK_AUTH receipt, construct its v4-shaped histsem row, require a passing gate and one regeneration call. | `AttributeError: module 'joulewise.arm_readiness' has no attribute '_histsem_rederive_pack_authentication'` |
| `test_v4_prefreeze_authors_then_postfreeze_bare_refuses_without_invalidating_recorded_authentication` | Author at a projected pre-freeze coordinate, freeze it, observe current bare rc=1, then require the recorded projected coordinate to pass through one regeneration call. | `AttributeError: module 'joulewise.arm_readiness' has no attribute '_histsem_rederive_pack_authentication'` |
| `test_frozen_receipt_constant_variants_do_not_change_the_authentication_verdict` | Hold one flagless, no-preserve derivation behavior and context fixed while varying the constant through absent, current, predecessor, unrelated, computed, duplicated, and malformed forms. | `EvidenceAuthoringError: flagless generator has a preserve branch or frozen-receipt constant` (valid present variants); `EvidenceAuthoringError: pack generator frozen-receipt constant is not a literal` (computed variant). |
| `test_unrelated_frozen_receipt_constant_has_its_own_relation` | Supply one readable digest equal to neither the current nor predecessor freeze receipt. | `AssertionError: 'names_predecessor' != 'unrelated'` |
| `test_temporary_workspace_allocation_failure_is_governed_at_arm_and_freeze_boundaries` | Force `TemporaryDirectory` allocation to raise while entering both public histsem gates. | `OSError: simulated histsem temporary-workspace exhaustion` |

## Durable A93 record

The explicit **Adopted A93 ruling** section in
`docs/contracts/receipt_histsem_verifier.md` is the durable normative record for
this implementation. It records constant non-authority, the impossible
refresh alternative, the diagnostic vocabulary, the mechanism, the exact
regression pointer, and the honest limit. It remains pending the magistrate's
separate merge-gate entry in `docs/decision_log.md`; this FIX seat did not edit
that lead-owned file.

## Honest limit of `pack_generator_check_status: PASS`

The precise claim is:

> `pack_generator_check_status: PASS` proves that the plan-pinned generator
> regenerated the authenticated historical pack coordinate (composed with the
> receipted projection replay when that coordinate is U11-projected); it does
> not prove that current HEAD pack bytes were regenerated, and a preserve-mode
> echo cannot establish or renew this claim.

The same sentence is recorded in code in
`joulewise.arm_readiness._histsem_rederive_pack_authentication` and normatively
in `docs/contracts/receipt_histsem_verifier.md` under **Coordinates and
checks**.

## Transaction effect and residual limit

No pack bytes, receipt bytes, pinset bytes, schema, six-key predicate fact,
custody script, or campaign configuration is changed. The `_v4` §3.4 authoring
fixture takes the composed projected path, runs its anchor under explicit
no-preserve, and passes. After freeze its bare current-tree check refuses, while
the historical projected receipt continues to pass the histsem gate. The
constant relation remains diagnostic and cannot make either result pass or
refuse.
