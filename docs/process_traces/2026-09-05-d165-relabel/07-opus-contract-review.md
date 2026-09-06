# 07 — Opus counter-review, CONTRACT lens

Opus, contract lens. Branch `feat/2026-09-05-d165-relabel` at `cc64253c`
(round 3); diff `origin/main...HEAD` (21 files). No commits.

**Verdict: NOT LANDABLE** — one blocker (F1), cured by ~6 lines in one file.
Everything else on the checklist verifies clean.

## Executed evidence (this session, this tree)

| Command | Result |
|---|---|
| `unittest tests.test_d165_dominance_closeout` | 50 tests, **OK** |
| `unittest tests.test_d117_contrast_v5_pack` | 40 tests, **OK** |
| `unittest tests.test_d117_floor_qwen3_v5_generate` | 13 tests, **OK** |
| `unittest tests.test_night_gate` (incl. registration pin) | 47 tests, **OK** |
| P2 witness, run standalone (not via the test) | see below |
| `git merge-tree --write-tree HEAD 3d1ab23b` | **CONFLICT** in `results-fill-registry.md` |

All runs `PYTHONDONTWRITEBYTECODE=1`, one module at a time.

**(4) P2 witness — executed.** Ten blocks, `onset_sweep_j` widths alternating
±0.5 J, authenticated bracket 0.05, `shared_edge_bound_s = 0.05`:
`rule_id = …replay.v2`, point `1.0` J, corner `1.5000000000007119` J, **ratio
`1.500000`, `passes = False`** — the ruling's witness exactly; arithmetic
unchanged. v1 artifacts still validate:
`test_v1_sidecar_result_and_reason_remain_validator_compatible` passes with a
sidecar carrying `LEGACY_COMMON_MODE_REPLAY_RULE_ID` and
`LEGACY_ABSOLUTE_COMMON_MODE_REASON` (`validate_d165_replay_sidecar` → `[]`).

## (1) Frozen artifacts, pinned digests, custody

Digest `1c0a4a11…83a2b` → `dfe55f8d…ac265`. Complete set of live pins and
consumers of those bytes (grep; process traces are history):

1. `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`
   — canonical bytes, regenerated. Only `rule_id` and
   `absolute_common_mode.reason` change; thresholds, census, arithmetic,
   branch restrictions byte-identical.
2. `joulewise/night_gate.py:30` `D166_REGISTRATION_SHA256` — retargeted; `:923`
   (C1) is the **only** runtime consumer, and C1 runs *only* for
   `receipt_class ∈ {DIAGNOSTIC_NO_PACK, REHEARSAL_STUB}` (`:908`) —
   `TRANSACTION_PACK` never hashes it (pre-existing, out of lane scope, but it
   bounds the blast radius).
3. `tests/test_night_gate.py:194,199-215`,
   `test_d165_dominance_closeout.py:1823`,
   `test_d117_contrast_v5_pack.py:82+` — all updated.
4. The three `_v5` generators' `dominance_criterion_registration()` feeds the
   manifest's `frozen_semantics_sha256`; **no literal `frozen_semantics_sha256`
   digest is pinned anywhere in the tree** (grep), so nothing breaks silently.
5. `tests/fixtures/night_plan_v1_retired.json` — **not** affected: consumed for
   key shape only (`scripts/magistrate_watchdog.py:114-130`); no byte pin, and
   its `registration_path` is a path, not a digest.

No other tree file cites either digest outside process traces.

**Could the retarget make an issued night plan or rehearsal stub refuse? No.**
A plan carries `registration_path`, never a digest (`night_gate.py:120,278-300`).
C1 hashes the *file* via `read_text = lambda path: Path(path).read_text(...)`
(`scripts/run_night.py:288`), resolved against the launchd `WorkingDirectory`,
which `configs/launchd/com.joulewise.night.plist.template` pins to the same
`@@REPO@@` that supplies `run_night.py` and hence `night_gate.py`. Pin and bytes
come from one checkout and **land in one commit** (`c43b7086` touches both), so
a clean checkout at any commit cannot desync them. Staleness is safe too: the v2
gate compares `measurement_head` against the pinned measurement checkout
(`:653-665`), not `repo_head`, so dev-checkout motion does not invalidate the
armed `rehearsal-20260903` plan.

**Supersession to record BEFORE the next real night:** (a) the v1 → v2 digest
transition with the landing commit, naming `night_gate.py:30` and the
regenerated JSON as one atomic pair never split by a partial checkout, rebase,
stash or cherry-pick; (b) that receipts issued before that commit record
`C1.measured.registration_sha256 = 1c0a4a11…`, authenticate the **v1** bytes and
stay valid as history, unreissued (I did not and must not read
`~/night-custody`: a requirement, not a verified fact); (c) the driver checkout
at or past the landing commit before the next `DIAGNOSTIC_NO_PACK` /
`REHEARSAL_STUB` arming, `install_night_agent.sh` re-run there so `repo_head`
matches.

## (2) Contract consistency — PASS

`docs/contracts/d165_dominance_closeout.md` matches the code and the addendum:
v2 active with v1 accepted as history at the `rule_id` row (`:190`); withdrawn
cancellation paragraph replaced by the diagnostic framing (`:39-46`); absolute
rationale quoted verbatim as `ABSOLUTE_COMMON_MODE_REASON` returns it, with
`LEGACY_ABSOLUTE_COMMON_MODE_REASON` marked "not the active physical
interpretation" (`:139-143`); worked-sidecar digest updated to `f0f8e86e…`
(`:61`), reproduced by the test. No threshold, census, arithmetic or branch text
moved.

## (3) Registry text — PASS; paper-K merge — CONFLICT

`docs/paper/results-fill-registry.md:228` and the eight R_cm rows
(`:236,243,251,259` plus the beta mirrors) carry the ratified sentence verbatim,
including the exact registered absolute rationale. Correct.

Paper-K (`3d1ab23b`) **also** rewrites that paragraph and those eight rows;
`git merge-tree` confirms a content conflict (its other hunks at ~112, ~143,
~878-921 merge clean). Two things make it un-side-pickable: paper-K's four
comparative rows and its paragraph append `SUPPLIER_PENDING: the producer emits
.v1 until the D-165 relabel lands`, which **becomes false the moment this branch
lands**; and paper-K's absolute rows paraphrase ("the registered replay is
comparative-only, not a claim that absolute timing uncertainty vanishes") where
this branch quotes `ABSOLUTE_COMMON_MODE_REASON` verbatim — the row must
reproduce the registered string, so this branch's text survives.

Resolution (author it; not `-X ours/theirs`): this branch's paragraph and all
eight rows, every `SUPPLIER_PENDING` clause deleted, paper-K's three
non-overlapping hunks kept; then re-run `tests.test_paper_terms_lint` and
`tests.test_paper_first_use_ledger` (both new on paper-K).

## Findings

**F1 — BLOCKER. The withdrawn rationale survives in the operative desk
instruction.** `docs/paper/round7/fill-checklist.md:61` still says absolute R_cm
is `not_applicable` "with the registered deviations-from-mean cancellation
reason", and rows `:203`, `:211`, `:219`, `:227` tell the desk to print
"`not_applicable`; deviations-from-mean cancels uniform shift" for the four
`R_cm_*_abs` tokens. Round 3 touched only this file's `rule_id` lines
(`:135-141`). Two operative fill instructions now contradict each other for the
same four claim-bearing tokens, and the checklist's is exactly the rationale the
addendum withdraws; `structural-edits.md` and `retensing-plan.md` got SUPERSEDED
banners, this file did not. Proposed `:61`: "…`not_applicable` with the
registered comparative-only rationale (`ABSOLUTE_COMMON_MODE_REASON`; see
`results-fill-registry.md`)"; each of the four rows: "`not_applicable`;
registered replay is comparative-only, not a claim that absolute timing
uncertainty vanishes".

**F2 — SHOULD-FIX. Campaign pack states the withdrawn derivation.**
`docs/campaign_packs/d117_contrast_v5.md:137-141`: "the absolute estimator
operates on deviations from the mean, so a uniform shared fiducial shift cancels
exactly…" — the pack's pre-registration description of the very JSON regenerated
in this diff, so it now disagrees with the artifact it documents. Replace it, or
add a dated SUPERSEDED banner like `retensing-plan.md`'s.

**F3 — SHOULD-FIX (record only). The validator no longer binds the label to the
producing semantics.** `joulewise/dominance_closeout.py:842-862`
accepts either rule id and then *adopts the supplied* `rule_id` into the expected
record before comparing; `:904-916` accepts either absolute reason. A sidecar
produced by today's v2 code can therefore be labelled `.v1` and still validate.
The addendum requires v1 be *readable* as history, not new output *labelable* as
v1; the branch tests only the historical direction. Rebuild is stopped and no
post-relabel sidecar is issued, so record it as a limitation. Minimum cure: a
regression that the builder cannot emit `.v1` or the legacy reason.

**F4 — NIT (overbuild).** `joulewise/dominance_closeout.py:602` replaced the
descriptive docstring with a bare label, and
`tests/test_d165_dominance_closeout.py:441-446` pins that docstring by exact
string equality — prose coupled to a test, buying nothing the registration bytes
do not, while the function stops saying what it does. Propose an operational
first line, the label second, `assertIn("shared-energy-sign", ...)`.

**(5) Overbuild, otherwise none.** The v1/v2 constant pair,
`COMMON_MODE_REPLAY_RULE_IDS`, the generators mirroring
`ABSOLUTE_COMMON_MODE_REASON` from the shared constant (closing R1) and the
SUPERSEDED banners are minimum-shape for the ruling; no threshold, census,
arithmetic or branch logic was touched (every code hunk read).

Cure F1 (preferably F2), re-run the four modules, land; F3/F4 are follow-ups.
