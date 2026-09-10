# 118 — Magistrate terminal review (ledger row 12) of the exact merge candidate: integration **1e15a3a509197d7f7382bb2c12f496ac7193ee54** — 2026-09-10 16:20 PDT (opened; closed when rows 9 and 10 return)

Not delegable. Read by the magistrate with full session context.

## What was read
- The whole production diff `origin/main...d9612e68` (record 110: nine files, +3996/−136) earlier this afternoon, and now the whole post-review production diff `d9612e68..1e15a3a5` (`calibration_bracketing.py` +29, `gen_derivation_night.py` +136, `issue_calibration_acceptance_generation.py` +208, `calibration_derivation_only.zsh` +75; 399/−49) in full.

## Judgments on the post-review diff
1. Chain dispatch (S7 r3): the writer runs as an `if` condition; `$?` in the `else` arm is the writer's status (zsh semantics; pinned by the two chain tests and the bench cuts); rc 0/1 continue with the row finalized; rc ≥ 2 stops with the session open — correct for independent derivation slots; the readiness/reservation failures still stop under `set -e`, as the closing comment now states truthfully.
2. Issuer fences (S4 r6): the pre-registration's `os_build` and powermetrics digest are PARSED from the file the caller names by strict single-match patterns (`/usr/bin/powermetrics sha256 in force is <64 hex>`; `os_build: <token>`) — the text is the authority, no third home; absent/ambiguous refuse; B-2's two escapes fence separately; B-3 pins the file's digest; the r6 level screen now comes from the authenticated predecessor and the A-4 literal is cross-checked in Decimal at run time. Brittleness accepted knowingly: the regexes bind the pre-registration's wording; the row-10 reviewer runs `check --preregistration` on the real file to prove the phrase matches at this head.
3. Third-epoch refusal (S4 r5): fail-closed before labelling; isolating by construction (neither A-7 nor the pending scan can see the injected row).
4. Validator floor (S3 r6): `ENVELOPE_MINIMUM_CORPUS_N = 17` on envelope rows only; the six issued rows unaffected; the comment gives the physical reason (the df tail under the Q99).
5. Generator (S7 r4): the ledger's slot ceiling imported, not restated; the identity epoch parsed with the ledger's own scalar rule (the brief's "strings" was wrong — `sampling_interval_ms` is an int; sensible-gates direction applied by the seat); `power_policy` cross-checked against the chain's literal; the example plan block is validated by the driver's own parser.
6. Nothing in the post-review diff amends ruled text or a process rule; every change is a fail-closed fence, a truthful comment, or a test.

## Open for Ed / the cold science gate (not blocking the merge)
- Veto windows: cold gate 69 (predecessor ceiling relation + isolation rule), record 80 (pre-registration screen rule as CG46's adopted default), record 82 (the rule name describes the rule, not the branch), record 88 (operand-collapse cuts).
- The S6 addendum's cold-gate-adopted V4 text still says "128 of a 210 min window" (the armed window is 150 min; 210 min is the install span) — ruled text, needs a dated correction by the gate or Ed.
- The successor screen rule conflict (pre-registration `max(range, 0.010818)` vs consult §2 `max(S_{g-1}, Q95_g)`) remains Ed's open V7 item; the issuer encodes only the pre-registration's rule and the candidate licenses nothing.
- Limitation for the record: every seat and every refuter in this lane after 08:41 ran on Opus (Codex limit, record 57); cross-model diversity is Fable (magistrate, cold gates 46/69) + Opus only.

## Closure (to append): replay 5 tail and rc (row 9); row-10 fresh-eyes verdict (117); the exact head sha re-verified at PR creation.

## Row 10 (record 117, Opus fresh eyes over d9612e68..1e15a3a5): should_fix, no blocker — and the magistrate's disposition (16:27)
- Reviewed properties intact (executed): the six issued rows still validate; blindness still first; `prepare-candidate` without `--preregistration-sha256` → rc 2, no file; `check --preregistration` on the REAL pre-registration and machine prints `pre-registered powermetrics sha256 b762e5bf…30c5: match` with exactly one appended line (byte identity proven by diff); all six contract-named flags match the merged parser; pin rot net-negative.
- S-1 (rule 11): S6 round 6 edited cold gate 46 clause V7 IN PLACE ("inherited" → "predecessor ceiling"). Magistrate fix (6c91dd2c): the ruled wording restored verbatim, followed by a dated addendum that TRANSCRIBES ruling 69 A1 (the rename is 69's, not the seat's); S-2: a dated open-item NOTE under V4 (210 min = the install span; the clause awaits the gate or Ed); S-3: the contract's epoch-match sentence now says the sampler digest is checked on every row's T1 bindings (stronger than "the identity epoch", which does not carry it).
- Nits: the three-nights fence counted flag repetitions → S4 round 7 (distinct ids; a repeated id refuses); a writer CRASH also exits 1 (no top-level guard) and would be logged `non-valid` — blast radius one slot (the next slot's `slot != expected_slot` refuses, rc 2, chain stops) — recorded, not changed; `_identity_epoch_value_ok` admits floats — acceptable (sensible gates).
- Consequence: the PR head moves past 1e15a3a5 by a docs commit and a one-line issuer fence; replay 6 at the new head is the row-9 run (replay 5 at 1e15a3a5 remains an early signal); a second short fresh-eyes pass covers the delta.
