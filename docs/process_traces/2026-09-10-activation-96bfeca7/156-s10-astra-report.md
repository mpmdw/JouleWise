```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"partial","summary":"INCOMPLETE / NEEDS_SCOPE: continuation core implemented; writer routing, diagnostic registration and full-suite completion remain.","workspace":{"base_requested":"bc1d7ef9","base_mode":"exact","head_start":"bc1d7ef9f421d75b7ed0f92d1598dedef5179c66","head_end":"bc1d7ef9f421d75b7ed0f92d1598dedef5179c66","upstream_end":null,"branch":"feat/2026-09-10-epoch-continuation"},"pathspec":["joulewise/calibration_bracketing.py","joulewise/calibration_epoch_continuation.py","scripts/issue_epoch_continuation.py","tests/test_epoch_continuation.py","tests/fixtures/custody_read_replay_allowlist.json","tests/fixtures/epoch_continuation/README.md","tests/fixtures/epoch_continuation/mutation_cuts.py","tests/fixtures/epoch_continuation/s9-pass.json","tests/fixtures/epoch_continuation/s9-fail-level.json","tests/fixtures/epoch_continuation/s9-fail-bracket.json","docs/contracts/epoch_continuation.md"],"unowned_dirty":[],"verdict":{"implementation":"partial","acceptance":"needs_ruling"},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_epoch_continuation","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 39 tests in 77.859s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_bracketing","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 92 tests in 0.442s","OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},{"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_custody_mode_inventory","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 7 tests in 36.180s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},{"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_calibration_acceptance_generation","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 114 tests in 109.476s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},{"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 12 tests in 94.254s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},{"id":"V6","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 71 tests in 113.584s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},{"id":"V7","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 31 tests in 1.282s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},{"id":"V8","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_mint_policy_resolver_guard","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 0.022s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},{"id":"V9","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d078_reason_registry","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 13 tests in 0.109s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},{"id":"V10","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_reason_code_partition","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 7.086s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}},{"id":"V11","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_epoch_continuation.EpochContinuationTests.test_systematic_acknowledged_row_exempt_but_ordinary_row_stales","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 1.210s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},{"id":"V12","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/mutation_cuts.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["cuts=18 killed=18 survivors=0 source_sha256_restored=true"]},"expected":{"exit_code":0,"tail_regex":"cuts=18 killed=18 survivors=0 source_sha256_restored=true"}},{"id":"V13","kind":"build","cmd":"PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/s10-compile-cache python3 -m compileall -q joulewise scripts","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},{"id":"V14","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},{"id":"V15","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests > /tmp/s10-canonical.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":130,"tail":["KeyboardInterrupt"]},"expected":{"exit_code":0,"tail_regex":"OK(?: \\(skipped=[0-9]+\\))?$"}}],"flags":[{"id":"F1","kind":"scope_deviation","level":"blocking","text":"No out-of-scope edits made. The allowlisted joulewise/validate_powermetrics_fiducial.py does not exist; the real writer and governing reason amendment are outside WRITE_SCOPE.","needs":"Resume with the requested paths and authorize the helper import and derivation-basis pass-through beyond one-line comparisons."},{"id":"F2","kind":"environment","level":"nonblocking","text":"The acceptance issuer's live epoch-watch test fails because os_build is None in this sandbox; the identical failure was captured before edits.","needs":"Repeat the live identity probe in the lead's permitted environment."},{"id":"F3","kind":"verification_gap","level":"blocking","text":"Canonical discovery was interrupted near the seat-budget cutoff with exit 130. It reported failures, including campaign process-identity errors, but produced no complete failure summary. It began before final small guards; final focused checks cover those guards.","needs":"After scoped integration, rerun the canonical suite in a permitted environment and triage all remaining failures."}],"scope_expansion":{"requested_paths":["scripts/validate_powermetrics_fiducial.py","docs/contracts/d078_reason_registry_amendment.md"],"reason":"Complete both writer epoch guards and mandatory registration of calibration_epoch_continuation_invalid.","blocked_work":"Ordinary capture/G2 continuation routing, derivation-only exclusion for already-judged epochs, their integration tests, and governing diagnostic registration.","minimal_change":"Import acceptance_judged_epochs; route the ordinary comparison; pass judged epochs through the derivation basis and guard; append the diagnostic registration."}}
```

## Change

**INCOMPLETE — NEEDS_SCOPE.** The authorized continuation core is implemented. The brief, synthesis, three consult records, and directive issue 316 were read.

- [Continuation authentication and loading](/Users/edr/code/JouleWise-wt-s10-continuation/joulewise/calibration_epoch_continuation.py:140) enforce byte pins, all three acceptance references, marker absence, canonical derivation hash, reproduced arithmetic, and terminal-session acknowledgment checks. Missing snapshots are explicitly labeled.
- Bracket evaluation now uses judged epochs at all four required sites: [freshness](/Users/edr/code/JouleWise-wt-s10-continuation/joulewise/calibration_bracketing.py:2053), [per-epoch doubling](/Users/edr/code/JouleWise-wt-s10-continuation/joulewise/calibration_bracketing.py:2350), [range expansion](/Users/edr/code/JouleWise-wt-s10-continuation/joulewise/calibration_bracketing.py:2369), and [systematic failure](/Users/edr/code/JouleWise-wt-s10-continuation/joulewise/calibration_bracketing.py:2382).
- The [candidate tool](/Users/edr/code/JouleWise-wt-s10-continuation/scripts/issue_epoch_continuation.py:64) re-reads primary evidence, derives the Decimal verdict, cross-checks S9 witnesses, and implements issuance-marker and output-path guards.
- The [contract](/Users/edr/code/JouleWise-wt-s10-continuation/docs/contracts/epoch_continuation.md:1) documents authentication, terminology, trigger semantics, the worked example, and outstanding integration requirements.

All six issued acceptance files remain byte-identical to HEAD. Existing acceptance pins and operatives are unchanged; the continuation registry is empty. No continuation was issued.

Final `git status --short` footprint: **2 tracked modifications, 9 untracked additions**, exactly the 11 paths in the envelope; no other dirty paths. No commits or Git state changes.

The identity-comparison census is:

| Site | Disposition |
|---|---|
| Bracket evaluator | Implemented at the four sites linked above. |
| [Writer ordinary preflight](/Users/edr/code/JouleWise-wt-s10-continuation/scripts/validate_powermetrics_fiducial.py:396) | Required routing is blocked: actual script is outside scope. |
| [Writer derivation-only guard](/Users/edr/code/JouleWise-wt-s10-continuation/scripts/validate_powermetrics_fiducial.py:1931) | Must refuse derivation-only once the planned epoch is judged. Blocked by the same scope issue. |
| [Arm readiness `_issued_d079`](/Users/edr/code/JouleWise-wt-s10-continuation/joulewise/arm_readiness.py:6142) | Checks acceptance ID, not machine epoch; already recognizes r6. Unchanged. |
| [G2 `_derive_live_vectors`](/Users/edr/code/JouleWise-wt-s10-continuation/scripts/generate_g2a_probe_inputs.py:638) | Delegates preflight to the writer. Inherits its eventual fix; no independent comparison to change. |
| [Acceptance issuer `check`](/Users/edr/code/JouleWise-wt-s10-continuation/scripts/issue_calibration_acceptance_generation.py:260) | Desk-only epoch watch; unchanged. |
| Ledger reservations, historical corpus/member bindings, G2 inventory bindings | Compare evidence or planned inputs with their own identities. Unchanged. |

The minimal **unapplied** integration proposal is:

```diff
--- a/scripts/validate_powermetrics_fiducial.py
+++ b/scripts/validate_powermetrics_fiducial.py
@@ imports
+from joulewise.calibration_epoch_continuation import acceptance_judged_epochs
@@ _derive_preflight_systematic_screen_s
-        if stale_fields:
+        if stale_fields and identity_epoch not in acceptance_judged_epochs(artifact):
@@ _derivation_only_screen_basis
         "epoch": dict(epoch),
+        "judged_epochs": [dict(item) for item in acceptance_judged_epochs(artifact)],
@@ main derivation-only branch
-        if not stale_fields:
+        if not stale_fields or planned_epoch in basis["judged_epochs"]:
--- a/docs/contracts/d078_reason_registry_amendment.md
+++ b/docs/contracts/d078_reason_registry_amendment.md
@@ append
+## D-102 continuation diagnostic
+
+`calibration_epoch_continuation_invalid` identifies a rejected continuation
+in the evaluation record. When no judged epoch matches, the outer refusal
+remains `calibration_acceptance_bound_stale`.
```

Decisions where the brief was silent: continuation IDs are deterministic content-derived identifiers; `declared_slots` stores ordered names; invalid-continuation details remain nested while preserving the existing outer stale refusal. Mutation checks replace compiled function copies and verify source SHA-256 restoration after each cut. No disagreement with the scientific design.

The cut table below uses test-name suffixes under `EpochContinuationTests.test_` in [the new tests](/Users/edr/code/JouleWise-wt-s10-continuation/tests/test_epoch_continuation.py:157). C-identifiers refer to the executable mutation runner.

| Cut | Killing test suffix |
|---|---|
| Freshness and unchanged screens | `continued_freshness_and_screens_equal_original_path` |
| Byte rotation / C18 pin-check removal | `rotated_byte_surfaces_invalid_and_stale` |
| Wrong acceptance ID or either pin | `other_acceptance_id_or_pin_refuses_even_with_valid_continuation_pin` |
| Machine field mismatch | `machine_must_match_every_continued_identity_field` |
| FAIL, marker, bad derivation hash | `fail_marker_and_derivation_hash_refuse` |
| Phantom/open/wrong-kind session or missing attempt | `phantom_open_wrong_kind_and_missing_attempt_sessions_refuse` |
| Wrong acknowledged content | `acknowledged_content_id_must_match_snapshot` |
| Per-epoch doubling versus pooling | `doubling_is_per_epoch_and_acknowledged_values_count` |
| Acknowledged versus ordinary low value | `low_acknowledged_value_exempt_but_ordinary_row_stales` |
| Future derivation session | `future_derivation_session_remains_in_range_trigger` |
| Acknowledged versus ordinary systematic failure | `systematic_acknowledged_row_exempt_but_ordinary_row_stales` |
| C01–02 extrema swaps; C09–10 subtraction collapse | `full_precision_decimal_extrema_and_range_survive` |
| C03–04 level operand collapse | `one_quantum_above_level_fails_without_writing` |
| C05–06 bracket operand collapse | `range_above_screen_fails_even_when_every_value_meets_level` |
| C07 strict level boundary | `level_equality_passes` |
| C08 strict bracket boundary | `range_equality_passes_with_distinct_min_and_max` |
| C11 minimum-count bypass | `five_retained_is_inconclusive_and_writes_nothing` |
| C12–13 retention-gate removal | `only_valid_resolved_values_are_retained_but_all_finalized_acknowledged` |
| C14–15 S9 level comparison collapse | `s9_level_fail_witness_preserves_false_comparison` |
| C16–17 S9 bracket comparison collapse | `s9_bracket_fail_witness_preserves_false_comparison` |
| Candidate recipe, marker and pin | `candidate_recipe_marker_pin_and_check` |
| S9 count/lexeme disagreement | `s9_witness_agrees_then_m_or_lexeme_disagreement_names_field` |
| Frozen acceptances and registry | `all_acceptance_bytes_and_registry_remain_frozen` |
| Routed writer integration | **Blocked by scope; not claimed complete.** |

## Verification notes

V4 reproduces the pre-edit failure in `DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch`: `os_build` is `None`, failing its string assertion. The [baseline log](/tmp/s10-baseline.log) records the same failure before implementation.

V15 is incomplete. The [canonical log](/tmp/s10-canonical.log) contains failures, including unavailable campaign process identity, but interruption prevented a complete failure summary. The run began before the final small guards; focused checks cover those changes. The final fixture-only adjustment was checked separately by V11.

Passing D-078 tests do **not** establish registration of the new diagnostic; that required amendment remains outside scope. The ordinary writer proposal was smoke-checked in memory only, and is not installed integration evidence.

Compilation redirected bytecode into `/tmp` to preserve the write scope. All continuation evidence is synthetic; no live capture or hardware validation was performed.

## Residual risk

Ordinary continued-epoch capture/G2 routing and derivation-only exclusion remain unfinished. The diagnostic also needs governing registration.

**Exact resume point:** expand scope to the two requested paths, authorize the import and basis-field changes, apply and verify the writer integration, register the diagnostic, add caller integration tests, then rerun the canonical suite and triage its failures. Issuance, live verification, final review, and merge remain lead-owned.