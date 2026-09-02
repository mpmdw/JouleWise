# Ruling 153a — D-165 stage 2 (PR #267) refuter findings, Opus 153 (contract lens)

Magistrate: Fable, 2026-09-02. Terra 152 (execution lens) is folded in by
addendum below when it lands. Findings F1-F5 and N1-N6 are in
`out/153-opus-s2-contract.md`.

R-5 (F1, BLOCKER — ACCEPTED). The refused `common_mode_replay.result` shape
(`dominance_closeout.py:124-132, 791-803, 858-880, 1105-1111`) is deleted.
Stage 1 fixed `result` at exactly seven keys and nothing in clauses 7-14 or
R-1..R-4c licensed a second shape. Zero denominator (`corner-widened
unguarded floor == 0 J`) is a malformed close-out input, and the mint
refuses to emit rather than recording a refusal inside a pre-registered
evidence artifact — the stage-1 fail-closed behaviour, restored verbatim.
The contract paragraph added at `d165_dominance_closeout.md:190-195` is
removed and the deleted sentence justifying `…replay.v1` ("because no
production sidecar was emitted before this exact shape was fixed") is
restored at `:144-145`. Regression: a mint whose replay hits the zero
denominator refuses (name the refusal the existing path raises) and writes
NO sidecar and NO floor.json (rollback holds).

R-6 (F2, SHOULD-FIX — RULED PATH STANDS, docstring corrected). The fixed
`/tmp/joulewise-test-d165-phase0-floor-pin` path is ruling R-4c after
consult 146/147; it is load-bearing for the digest and is not reopened.
Reopening a ruled mechanism is a cold-gate trigger and the finding gives no
new fact (the parallel-hostility was known and accepted: the test runs once
per CI job, on isolated runners). Docstring change only: "binds nine
path-sensitive scalars … the digest is over the whole file". Contention
handling is deliberately left as `mkdir(exist_ok=False)` failing loudly.

R-7 (F3, SHOULD-FIX — ACCEPTED, in the form Opus recommends). The clause-10
census walks `joulewise/**/*.py` and `scripts/**/*.py` (excluding the
owner) and, per Opus's form-independent recommendation, checks each
non-owner module's compiled `co_consts` recursively for the literal instead
of enumerating string syntaxes; the four-file map stays only for the
reference-site assertion. Runtime-split forms (`join`/`%`/`format`) are
left open by this ruling (D-161: drift, not adversary). `_folded_string_constant`
may be deleted if the `co_consts` walk subsumes it (it does for every
compiler-folded form).

R-8 (F4a, SHOULD-FIX — ACCEPTED). The `d165_replay_output_required_for_common_mode`
refusal moves to the estimator-selection gate
(`scripts/mint_floor_artifact_generalized.py:2614-2636`, right after the
sink write) per R-3 "at the first common-mode cell selection"; the contract
prose at `d165_dominance_closeout.md:222-223` reverts to "selection".
Regression: the existing missing-flag test additionally asserts that no
bind-stage work ran (e.g. the recomputation census is empty / the bind
function was not entered).

R-9 (F5, process — RECORDED, no code). R-1a was executed backwards:
`ec761c04` is red on `tests.test_d117_contrast_v5_pack` because the 7e
generator edit sits in `2b2bb166`. The head is green; bisectability on one
commit is lost. Recorded in the PR body; the branch is not rewritten
(seat commits are never rebased).

R-10 (nits). N3: use `DOMINANCE_REPLAY_SIDECAR_ROLE` in the pack pin test.
N4: drop the tautological `== []` assertion or turn it into the
raise-on-invalid assertion. N5: restore the defence-in-depth sentence
("A finalized manifest without the role is nevertheless fail-closed at its
consumer … `manifest_lacks_replay_sidecar`") since the refusal still exists
and is still listed. N1, N2, N6: recorded, no change.

## Addendum — terra 152 (execution lens)

All six ruled mutants killed by named tests; R-4 digest reproduced from the
pristine base tree (`9127a51d…`); generated `_v5` pack: five rows, no
refusals; four-row mutation refuses the named code; 387 passed / 2 skipped.

R-11 (terra F1, SHOULD-FIX — RECORDED, no code). The committed frozen v3 pack
(`as_generated_pre_d134_freeze`, nine keys, no `finalization_contract`)
refuses prospective validation with `schema_invalid`/`unknown_key`/
`unresolved_slot`/`not_frozen`. That is the pre-D-134 form refusing the
D-134 validator — it refused identically on the base tree and stage 2 did
not change it. Clause 7's "legacy four-row packs still validate" is about
D-134-form packs without `dominance_criterion` (pinned by
`tests/test_analysis_finalizer.py:857-872`), not pre-D-134 packs; D-167
retires the v3 transaction. The contract sentence is tightened to say
"legacy D-134-form four-row packs" so the promise reads as what is tested.
