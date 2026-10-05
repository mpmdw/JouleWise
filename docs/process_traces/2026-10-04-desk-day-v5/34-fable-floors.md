FINAL PASS: PASS

Cold final pass on `a1133594` (PR #472, parent `8fa002f7`). No BLOCKER, no MAJOR.
Three MINOR and four NIT findings below; none needs to hold the merge.

## What I ran

- Tests: `tests/test_paper_reported_energy.py`, `tests/test_d117_floor_qwen3_v5_generate.py`,
  `tests/test_campaign_generator_core.py` -> 59 passed, 133 subtests passed (242 s).
  NOT run: `tests/test_d117_floor_qwen25_1p5b_plan.py` (6 changed lines, fixture-pin plumbing
  only) and the whole suite.
- Scratch probes under `/tmp/dd5-fable-fl/` (fixture pins, never the issued pin):
  both floor generators at two non-512 rungs; both floors plus the contrast at one
  non-512 rung; a successor-family (`_v6`) generation at a non-512 rung; the parent
  commit's registry module replayed against the new p512 fixture; alias probes on a
  really generated extraction spec.
- No mutation testing was executed (checkout is read-only). Statements about which
  test kills which regression are from reading the assertions, and are marked so.

## Answers to the five questions

**1. Pin fidelity, contrast agreement, path back to 512 — holds.**
- `PREFILL_LENGTH` starts `None` (`generate_configs.py:78`) and is published only at
  `:1332`, after every pin check. Every use is at call time; `p512_family_definition`
  (`:833`), `projected_runtime_budget` (`:684`) and `generate` (`:2595`) refuse while it
  is unset. The only surviving `512` literals are the decode output budget, the ladder,
  the planning baseline and the name templates that `:1333-1339` rewrite.
- Generated at two non-512 rungs, both models: zero `p512` identifiers in any output
  path or JSON body; all 50 long-prefill configs per pack carry the pin's exact
  `prompt_text`, `token_count` equal to the pin length, and the pin's
  `token_ids_sha256`; the custodied pin is byte-identical to the input; `check_current`
  round-trips.
- Floors + contrast at one non-512 rung: all four contrast identity units resolve to a
  floor `calibration_plan.json` whose `plan_id` matches; the floors'
  `allowed_consumer_families` and long-prefill artifact ids appear in the contrast;
  exactly one long-prefill prompt identity (text hash, token-id hash, count) exists
  across the three packs; the contrast refuses the same pin with a different
  `--prefill-length` (`prefill_prompt_pin_length_mismatch`).
- The floor generator does not itself compare against the contrast. Agreement is
  enforced by the length being inside every cross-pack name (plan id, family id,
  artifact/transport ids, consumer family, identity unit id). Two different pins of the
  same length would share names; I did not trace the arm-time identity-pin projection
  that is meant to catch that (`identity_pins.py:1795-1806` compares the token-id hash).

**2. Acceptance binding and ledger literal — exact.**
- `SUCCESSOR_ACCEPTANCE_ID/_REL/_SHA256` (`:213-222`) equal
  `calibration_bracketing.ACTIVE_ACCEPTANCE_ID` and its registry row
  (`calibration_bracketing.py:157-162, 219-232`); file digest recomputed with `shasum`:
  `f949f511…3660`. Derivation digest equals the artifact's own `derivation_sha256`.
- `LEDGER_HEAD_SHA256` (`:223-225`) equals the artifact's `ledger_cutoff.head_digest`
  (sequence 376). The live head pin is at sequence 402 with a different digest, so the
  literal is the cutoff, not the head.
- If wrong, generation itself refuses: `pinned input drifted` (`:2681`) for the artifact
  digest, `acceptance ledger cutoff drifted` (`:2629`) for the ledger literal, and
  `ledger head pin behind the acceptance cutoff` (`:2637`) on rollback. Binding the old
  id instead would embed the previous epoch's allowance rule
  (`max(observed_drift_s,0.009724)` instead of `…0.014531`, both computed from the
  registry). `arm_readiness._issued_d079` (`arm_readiness.py:6198-6226`) lists the new
  id. I did not trace freeze-receipt or whole-window consumers beyond that.

**3. Historical p512 — byte-identical; mixing and declared aliasing refuse.**
- Loaded the parent commit's `paper_reported_energy.py` and the parent test helper in
  scratch: for both models the registration manifest bytes, the synthetic spec bytes and
  the full projection digest are identical old-vs-new, and equal to
  `tests/fixtures/paper_reported_energy/p512_replay.json`. The fixture is therefore not
  self-referential. Default-argument digests equal the contract table; all six ladder
  digests in the contract table recompute.
- A really generated long-rung spec relabelled to `p512` everywhere, with family hashes
  recomputed so it is structurally valid, refuses `cell_census_invalid`. A
  registration-level length that disagrees with the family declarations refuses.
  Non-int, bool, float, string and off-ladder lengths refuse.
- `supply_map.json`: only the `reported_energy_parents` fixture receipt and inventory
  digests moved; that receipt embeds `validator_source_sha256`
  (`tests/fixtures/paper_custody/repin.py`), and the validator source changed. Mode is
  `test_fixture_non_issuing`. Legitimate.
- No v5 `extraction_spec.json` has ever been committed on any local ref.

**4. Planning constants — planning only.**
Repo-wide search for `runtime_budget` and `planning_estimate_`: generators, tests and
process traces only; nothing in `joulewise/` or `scripts/` reads them, and no plan-tree
validator closes that object's key set. Tooling outside the repository was not inspected.
At 512 the model reproduces the inherited 376.8 minutes.

**5. Tests — adequate, with the gap in MINOR-2.**
By reading: hardcoding 512 at publish, at `token_count`, in the workload name, in stage
ids or in `registration_sha256` each trips an assertion in
`test_d117_floor_qwen3_v5_generate.py:296-367`; the acceptance and ledger literals are
compared to the registry and the artifact, not to copied constants (`:488-504`); the
ordering test (`test_paper_reported_energy.py:360-399`) fails if the original p512 owner
commit is allowed to authorize a ladder registration.

## Findings

**MINOR-1 — an undeclared spec still defaults to 512, so the contract sentence "a longer
prompt labelled `p512` refuses" holds only when the pack declares a length.**
`joulewise/paper_reported_energy.py:178-196` (default at `:196`);
`docs/contracts/paper_reported_energy.md` prospective-extension paragraph.
Evidence: the generated long-rung spec, relabelled `p512`, with
`condition_family_id`/`condition_family_definitions` removed from cells 4-5 (which
`floor_extraction.py:904-907` allows) passes `validate_extraction_spec` with zero errors
and `_validate_registered_spec` ACCEPTS it. Not a regression (the parent had no length
census at all), the generator cannot emit this shape, and `--check` would flag the edited
spec as drift. Since no v5 spec predates this change, a follow-up could require the
declaration on the production path and keep the default for synthetic fixtures only.

**MINOR-2 — the cross-pack join is tested only at 512.**
`tests/test_d117_floor_qwen3_v5_generate.py:1013-1059` and `:1103-1118` pass
`prefill_length=512`; `:930`, `:958`, `:973`, `:1041` assert 512 literals. The case the
campaign will actually run (a non-512 rung) has no regression test for floor-to-contrast
resolution. My scratch probe shows it works today; nothing keeps it working.

**MINOR-3 — the end-state 4096 branch is ahead of its neighbours in this tree.**
`generate_configs.py:85-90, 1187-1217` (both packs). The schema id, key set and trigger
vocabulary are copied from the issuer, which is not on this branch; the test
(`:393-454`) repeats the same literals. I compared against the issuer branch commit
`ff4f11f33`, `scripts/issue_g2a_prefill_prompt_pin.py:295-325`: key set, both trigger
strings and the 1-harvest/2-harvest mapping agree. Separately,
`configs/campaigns/d117_contrast_v5/generate_configs.py` has no end-state handling at
this commit, so on that branch the floors would generate and the contrast would refuse
until its own change lands. Both fail closed. The floor checks only the record's shape;
`registration_sha256` and the harvest paths are not opened (stated as issuer-owned at
`:85-86`).

**NIT-1 — raw `AttributeError` can escape the ordering fence.**
`paper_reported_energy.py:211-212` calls `_spec_prefill_length` inside a `try` whose
handler (`:243`) lists `OSError, ValueError, KeyError, TypeError`. A committed spec that
is a JSON list, or whose cells 4-5 are not objects, raises `AttributeError` (reproduced
for three shapes). It still fails; `_verify_gate_ordering` (`:251`) converts it to
`request_invalid` rather than the documented `ordering_history_invalid`.

**NIT-2 — the gate accepts any rung's digest and does not require the two models to
share a length.** `paper_reported_energy.py:260-261`. The proof is computed from the
spec's declared length a few lines earlier, so this is not exploitable by itself; campaign
-level agreement between the two floors rests on the contrast join, not on the registry.

**NIT-3 — planning model details.** `generate_configs.py:681-727`. The "fixed" allowance
includes the forced 512-token decode of the 50 long-prefill members, whose per-token cost
rises with context length; only prefill is scaled. The 8B rate rests on one member per
rung (8B file `:82`). `baseline_minutes_with_margin: 376.8` (`:703`) is a literal that
duplicates `18840 * 1.2 / 60`. All inside the 20 % headroom and planning-only.

**NIT-4 — one test's expected code coincides with a mutant's.**
`test_mixed_declared_prefill_family_refuses` (`:369-391`) expects `cell_census_invalid`,
which is also what a registry that ignored family declarations would return for that
input. That mutant is instead caught by `_validate_registered_spec(spec)` at `:359`.
Reasoned from the code, not executed.

## Not verified

- The issued pin itself, and the selected length, were not read.
- Arm-time identity-pin projection, freeze receipt and whole-window verdict paths were
  not executed.
- Successor-family generation at a non-512 rung produced a correctly threaded `_v6`
  plan id and no stale `p512`; two pre-existing `v5` strings in the decode suite id and
  renderer name remain, untouched by this change.
