WRITE_SCOPE: ["joulewise/detection_floor.py","tests/test_detection_floor.py","joulewise/analysis_engine/inputs.py","joulewise/analysis_engine/__init__.py","tests/test_analysis_inputs.py","tests/test_analysis_claims.py","docs/contracts/identity_pin_projection.md","docs/specs/c027/p2-039_floor_artifact.md"]
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: implementation

# FIX round 1b — decode-identity lane, finding F-M only (ruling 171a; Opus F6)

Checkout: `/Users/edr/code/JouleWise-wt-decode-id`, branch `fix/2026-09-02-decode-identity-set` at `3ac6cffb` (fix round 1 landed there; its report deferred F-M as NEEDS_SCOPE because the governed reason-code census was outside scope — it is inside scope now). Do NOT `git rebase`, `git checkout`, `git stash`, or commit; leave your edits in the working tree — the magistrate commits. Do NOT run `python3 -m unittest discover` (canonical suite); run named modules only, with `TMPDIR` set to a subdirectory of your scratch dir.

## Hard invariant (unchanged from round 1)

`configs/campaigns/d117_contrast_v5/generate_configs.py` is NOT in scope and must not change; the dominance-criterion registration digest `1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b` is pinned by `tests.test_d165_dominance_closeout`. `docs/paper/draft-v1.md`, `runs*/`, `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/` are frozen.

## The defect (F-M, Opus 204 F6)

`floor_request_for_evidence` (`joulewise/analysis_engine/inputs.py`, ~4051–4096) returns `None` on every failure, and the production caller (`joulewise/analysis_engine/__init__.py`, ~395–424) turns `None` into `unavailable_floor_resolution(...)` whose only reason code is `consumer_term_unknown`. So when successor lineage is present but the U8-bound frozen identity set CANNOT BE AUTHENTICATED (`_frozen_consumer_identity_set` returns the empty frozenset — pack tree hash mismatch, freeze receipt sidecar mismatch, projection not frozen, config bytes not matching the inventory hash, etc.), or when the evidence's identity is NOT A MEMBER of an authenticated frozen set, the resolution is indistinguishable from an ordinary "no consumer term" refusal. A reader of the analysis output cannot tell "the frozen declaration was tampered with / unreadable" from "no matching floor cell". This is fail-closed already (the refusal happens); the defect is the LABEL.

## Ruled closure

R-M1. Add exactly TWO reason codes to the governed census `TRANSPORT_REASON_CODES` (`joulewise/detection_floor.py:293`):
  - `consumer_identity_set_unauthenticated` — successor launch lineage was present on the evidence but the U8-bound frozen identity declaration could not be authenticated (every `return frozenset()` path in `_frozen_consumer_identity_set`, including the caught-exception path).
  - `consumer_identity_undeclared` — the frozen set authenticated but at least one evidence row's scientific identity is not a member of it; ALSO the legacy case where more than one identity is present and NO declaration exists (`len(consumer_identities) > 1 and declared is None`).
  Every other `None` return in `floor_request_for_evidence` keeps collapsing to `consumer_term_unknown` — do not invent further codes.
R-M2. Extend the exact census test `tests/test_detection_floor.py::test_reason_code_set_is_closed_v1_set` with both codes (it must stay an EXACT set equality), and add both to the spec list `docs/specs/c027/p2-039_floor_artifact.md` §6.3 (the spec says adding a reason is additive and schema-compatible; keep that sentence). Keep `TRANSPORT_RULE_ID` unchanged — no check is weakened, no meaning changes.
R-M3. Carry the reason out of `floor_request_for_evidence` WITHOUT changing the test-only `request_factory` seam in `__init__.py` (it still returns `FloorRequest | None`, and production CLI calls never supply it). Choose the smallest shape: e.g. an internal `_floor_request_or_refusal(...)` returning `FloorRequest | tuple[str, ...]` that the public `floor_request_for_evidence` wraps (returning `None` on any refusal as today), with the production caller in `__init__.py` calling the internal form and building the refused `FloorResolution` with `reason_codes=(<code>,)` instead of `unavailable_floor_resolution`. Say in the report which shape you chose and why. `_floor_engine_reasons` (`__init__.py:~205`) maps unknown codes to `floor_transport_inapplicable` — decide whether the two new codes should map there (default: yes, they are transport-inapplicable) and state it; do not add a new engine reason.
R-M4. Tests (tests-first, defect-shaped, through the PRODUCTION path — no `request_factory`): in `tests/test_analysis_inputs.py` (class `FrozenConsumerIdentitySetTests` already builds a real committed v3-shaped pack with a U8 freeze receipt), add
  (a) a case where the frozen identity receipt's bytes are perturbed by one byte after the sidecar was written (authentication fails) → the resolution is `refused` with `reason_codes == ("consumer_identity_set_unauthenticated",)` and NOT containing `consumer_term_unknown`;
  (b) a case where the set authenticates but one evidence row's config differs in a scientific field (identity not a member) → `("consumer_identity_undeclared",)`;
  (c) the legacy two-identity-no-declaration case → `("consumer_identity_undeclared",)`;
  (d) a counterfactual: the SAME fixture as (a) with the perturbation NOT applied resolves as today (exact or transported), proving the code is emitted only on the failure. Each test must fail against `3ac6cffb`'s production code (run them once against the unmodified tree before your edits and paste the failing tails in the report — that is the counterfactual evidence the mutation-cure rule requires).
  In `tests/test_analysis_claims.py`, update any assertion that today expects `consumer_term_unknown` for what is actually an identity-set failure (line ~2188 `idle_resolution` — check what that fixture actually exercises before touching it; if it is a genuine no-consumer-term case, leave it).
R-M5. Contract: `docs/contracts/identity_pin_projection.md` analysis-gate prose (~563–600; the first-use definitions block landed in round 1 — do not reorder it) gets ONE plain-language paragraph saying what the two refusal labels mean and when each is emitted, built from the mechanism (Ed's writing standard: a reader must be able to replicate it; no term used before it is glossed), plus one row in the executable-evidence table (~954) naming the new tests.

## Verification you must run and paste

`python3 -m unittest tests.test_detection_floor tests.test_analysis_inputs tests.test_analysis_claims tests.test_identity_pins tests.test_d165_dominance_closeout tests.test_docs_freshness` (tails), `git diff --stat`, and a grep proving every `return frozenset()` in `_frozen_consumer_identity_set` maps to the unauthenticated code (or explain the one you routed elsewhere).

## Report

`claude-codex-report/v1` envelope, genre implementation; `verdict` block under 8 KB. Markdown body: shape chosen for R-M3 and why; per-clause R-M1..R-M5 status with file:line; the pre-edit failing tails for R-M4(a)–(c); executed evidence; anything you could not do as ruled → `NEEDS_RULING` naming the clause, the obstacle, and two options (do not improvise a semantics).
