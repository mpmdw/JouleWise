ORIGIN: claude-code lead (magistrate)
HOP: 1 (do not call Claude by any route — never run `claude -p` yourself)
GENRE: review
WRITE_SCOPE: []

# Design consult — V5-PREFILL-REALIZED-PROJECTION-02 (identity-pin projection catcher for registered prefill prompt realization)

Checkout: `/Users/edr/code/JouleWise-wt-proj02` (branch
`feat/v5-prefill-realized-projection-02`, head `4a41d791` = main). Linked
worktree: READ-ONLY for you — edit nothing under the repo; do not commit,
rebase, push, or run `git checkout`. `TMPDIR` = a subdirectory you create
under `/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Run only named test modules (never `unittest discover`). Never load a real
model from `~/jw_models`; never spawn `claude`.

## The row (docs/process/state_kernel.json → tasks/V5-PREFILL-REALIZED-PROJECTION-02)

Goal: "Add the identity-pin projection catcher for registered prefill prompt
realization at freeze and arm." Acceptance evidence: (1) the freeze
projection derives the prompt realization from the registered prompt text on
the collection stack; (2) arm-time projection re-verification refuses a
count, ids-hash, or domain mismatch before collection; (3) the arm-critical
`identity_pins.py` change passes the required council and delta-review gates.
Authority: `docs/process_traces/2026-09-01-fresh-model-review/44c-RULING-realized-prefill-check.md`
(read in full; the "Earliest catcher" row explains why this was deferred to a
second row and why it is defense-in-depth, not the fence). The fence that
already exists (row 01, landed as PR #258): `joulewise/bundle_read.py:931-1077`
`_prompt_realization_problems` refuses a succeeded prefill bundle whose
realized provenance count / ids-hash / domain / text digest differs from
`workload_profile.prompt_token_expectation`. Row 02 buys "before the first
joule" over "first prefill bundle" — a lost quiet night costs Ed a week.

## What you must read before designing

- `joulewise/identity_pins.py` — the freeze/arm projection path:
  `_derive_projection_units` (~`:1364`), the runtime probe hook
  (`:1159`, `:1276` `identity_projection_metadata`), the refusal class
  `IdentityPinProjectionError` and the existing refusal-name vocabulary
  (`readiness_identity_*`). Find where freeze vs arm re-verification split
  and what each one already compares.
- `joulewise/adapters/mlx_runtime.py:315` `identity_projection_metadata` —
  what the projection probe loads today (model? tokenizer?) and what it
  returns; `:396-401` the single-prompt realization path and `:936`
  `_encode(..., add_special_tokens=True)`; `joulewise/provenance.py:12,:321`.
- `configs/campaigns/d117_contrast_v5/generate_configs.py:624`
  `_load_prefill_prompt_pin`, `:1003-1053` how the pin fills
  `PREFILL_TOKEN_IDS[_SHA256]`, `:1324-1352` `workload_for` emitting
  `prompt_token_expectation`. The registration bytes
  `dominance_criterion_registration()` are frozen (digest `1c0a4a11…`,
  `tests/test_d117_contrast_v5_pack.py`); the generator file is in NO seat's
  scope, ever.
- D-131 in `docs/decision_log.md` (the council trigger for identity_pins.py)
  and D-166 (pre-registration), D-167 (immutability).
- `tests/test_identity_pins.py` — the fixture style for projection tests
  (how the runtime probe is faked).

## Questions to answer (each with file:line evidence)

Q1. Does the projection probe at freeze already have the tokenizer in hand
(model loaded for artifact identity)? If yes, the cheapest catcher is:
tokenize the config's registered `prompt_text` with the same `_encode`
helper and flags the runtime uses, and compare `(len, sha256, domain)` to
`workload_profile.prompt_token_expectation`. If no, say what it would cost
to load the tokenizer alone and whether that changes the projection's
identity semantics (it must not alter any existing projection receipt byte
for configs WITHOUT an expectation — legacy packs must project identically;
prove this from the receipt construction).

Q2. Where exactly does the check live: inside `_derive_projection_units`
(per identity unit, representative config) or per config? An identity unit
may contain both arms' prefill configs with DIFFERENT expectations (A and B
share the pin today — "identical today under the shared pin" per 44c — but
the schema is per config, per arm). Design for per-config comparison or
justify representative-only.

Q3. Refusal naming and semantics: propose names in the existing
`readiness_identity_*` style (or reuse), one for mismatch (text names which
of count/hash/domain differed) and one for "expectation present but the
projection cannot realize it" (tokenizer absent / adapter without the hook).
Absence of the expectation on a config is NOT a refusal here (row 01 owns
absence semantics at the bundle) — confirm or argue otherwise.

Q4. Freeze vs arm: the acceptance says both. Is arm-time re-verification a
re-run of the same function on the frozen pack (so the check comes for free)
or does arm compare against the freeze receipt? If the freeze receipt would
now carry the realized projection (count/sha/domain), is that a receipt
schema change (closed schema? golden?) — list every golden/pinned artifact
that would move and say whether that is acceptable under D-167.

Q5. Council/gauntlet shape: D-131 says what exactly for identity_pins.py
changes? Enumerate the gates the implementation PR must pass.

Q6. Tests: list the tests (names + the one assertion each), the counterfactual
input for each (memory rule: a cure whose test can't name the production
call site and the counterfactual input kills nothing), and 4-6 mutants.

Q7. Anything in this design that would touch the `_v5` generator file,
`generate_configs.py`, or the frozen registration? If so, STOP and say so —
that is a NEEDS_RULING, not a design choice.

## Report

Envelope first (`claude-codex-report/v1`, genre `review`, verdict.decision
one of DESIGN-READY / NEEDS_RULING). Then: a proposed WRITE_SCOPE (exhaustive
file list), the design as a numbered spec an implementer can build from
without reading this brief, answers Q1–Q7 with file:line, and a
disagreement section: where you would push back on the row's own framing.
Under 120 lines after the envelope.
