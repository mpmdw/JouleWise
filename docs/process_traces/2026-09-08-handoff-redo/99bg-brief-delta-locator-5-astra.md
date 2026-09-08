# Delta re-audit — ICLOUD-CUSTODY-LOCATOR-01 part 5 (gpt-6-astra, HIGH, genre review, READ-ONLY)
Branch fix/2026-09-08-icloud-custody-locator, head 96bfb448; the round is `git diff ae09cad7 96bfb448`. It implements the cold-gate
synthesis at the absolute path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ak-coldgate-packet-locator-boundary/13-magistrate-synthesis.md
(read it and the ruling 10 / refutation 11 beside it). Audit, with file:line and an executed or in-memory counterfactual per claim:
1. INVARIANT BY CONSTRUCTION: with the defaults now issuing at `load_calibration_ledger_snapshot` and `_custody_reasons`,
   enumerate EVERY call site (AST, not grep) of load_calibration_ledger_snapshot / probe_custody / _custody_state /
   _custody_reasons and of the parameterised shared validators (AuthenticatedConsumptionSession, bind_floor_artifact_evidence,
   load_analysis_inputs, extract_cells, the mint module's two loads) in joulewise/ and scripts/. For each site that passes or
   forwards read_replay, trace its caller chain to a process entry and state whether ANY chain reaches minting, binding
   publication, ledger append, or analysis-manifest finalization. Name any that does. Confirm the allowlist fixture equals
   exactly that set.
2. Does tests/test_custody_mode_inventory.py's AST census actually bind: what happens on (a) a new read_replay literal at an
   unlisted site, (b) a forwarded variable named `mode` whose caller passes read_replay from an issuing entry, (c) a call through
   an alias or **kwargs? Name escapes.
3. Entry guards: is `_refuse_custody_override_mint()` truly the first executable statement of the four public entries, and can
   any of those entries be reached through another public function that skips it?
4. Planted-replacement fixture: does it assert ZERO opens under the replacement root (how is the counter attached), and does the
   read_replay branch of the same fixture prove the override still works for replay?
5. Replay regressions: did any genuinely-replay path LOSE the override (paper producers, replay fence, recover/audit,
   provenance checks, campaign re-evaluation)? Name the test that proves each still maps.
6. The 11 authentication-surface pins: confirm each moved pin has an unchanged function body/operation (the seat claims AST
   comparison) and that NO new direct read outside the wrapper census was introduced by this round.
7. Any NEW defect. Verdict keys per genre review; severity per finding; ≤ 900 words; no edits; header < 8192 bytes.
