# 170 — S10 round 1 refuter (Opus, contract + execution lens), read-only

Target: `c75da300` on `feat/2026-09-10-epoch-continuation` (diff base `bc1d7ef9`).
Read via `git show`/`git diff`; tests run from a read-only export at
`/tmp/s10-r1-export` (`git archive c75da300 | tar -x`). Nothing written in any
repo; no git write commands; the S10 worktree, canonical, and night-custody
were not touched.

**Verdict: NOT CLEAN — 1 blocker, 3 should-fix, 3 nits.** Everything the brief
asked me to try to break held EXCEPT the completeness of the ledger
cross-check: a night the tool itself scores FAIL can be re-spun into an
authenticated PASS. Demonstrated with a running counterexample below.

---

## Test evidence (question 8)

`cd /tmp/s10-r1-export && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
tests.test_epoch_continuation tests.test_calibration_bracketing
tests.test_arm_readiness`
→ **`Ran 202 tests in 64.344s` / `OK (skipped=1)`**, rc 0. Not stopped; well
under the 15-minute cap.

Caution for whoever repeats this: **`timeout` does not exist on this machine**
(zsh: "command not found"). My first two attempts wrapped the suite in
`timeout 900` and exited 0 having run NOTHING. Any seat or refuter report whose
evidence line contains `timeout` on this host has run no tests.

Independent mutation replay:
`PYTHONDONTWRITEBYTECODE=1 python3 tests/fixtures/epoch_continuation/mutation_cuts.py`
→ `cuts=18 killed=18 survivors=0 source_sha256_restored=true`, rc 0. The seat's
claim reproduces.

---

## BLOCKER

### B1 — the ledger cross-check never requires the continuation to DISCLOSE every finalized row of the cited session, so a FAIL night authenticates as PASS

`joulewise/calibration_epoch_continuation.py:234-244`

`finalized` is derived *from the continuation file* (`:195`, the slots whose
`content_id` is not null). The cross-check then iterates `for slot in
finalized` and confirms each disclosed slot against
`session.finalized_slots`. It never asserts the converse — that
`session.finalized_slots` contains **no rows the file omitted**. A slot the
file re-labels `content_id: null, disposition: "window_exhausted"` satisfies
`:204-209` (state `aborted`, all fields null) and is then skipped by the
cross-check entirely. `m`, the extrema, the range and therefore the verdict are
recomputed over the surviving subset and agree with themselves at `:219-222`.

The suppressed rows are exactly the ones an issuer would want to suppress: the
captures that exceed the level screen.

**Concrete failing input, executed** (`/tmp/s10_gap_demo.py`, synthetic fixture
ledger via `tests/fixtures/epoch_bootstrap/build.py`, 12 declared slots, 9
filled, session aborted `window_exhausted`; six retained at `0.025` and three at
`level + 0.001`):

```
honest prepare rc = 4 (4 == FAIL)  m = 9  max = 0.033898493715362  level = 0.032898493715362
forged: hidden rows = ['derivation-night-1-d07', 'derivation-night-1-d08', 'derivation-night-1-d09']
forged loaded = 1  refusals = []
RESULT: ACCEPTED  m = 6  verdict = pass  cross_check = verified_terminal_derivation_session
ledger really has 9 finalized rows; the continuation discloses 6
```

The tool correctly scored this night **FAIL, rc 4**. Re-labelling three rows,
recomputing `m`/extrema/`derivation_sha256` by the documented recipe, and
pinning the bytes yields a continuation that `load_epoch_continuations` accepts
with **zero refusals** and — this is the part that makes it a blocker rather
than an operator-adversary nit — reports
`ledger_cross_check: "verified_terminal_derivation_session"`. The field that
exists to say "I independently checked this night against the ledger" asserts
full verification over a night one third of whose finalized rows it never
looked at.

Why this is not disposed of by D-161 (operator-only adversaries are
over-engineering): the defect is not only a forgery path. It is a *mislabelled
degradation*. Any issuer bug, partial re-run, or hand-edit that drops rows
produces a file the reader blesses and stamps as verified, and the record shows
no trace. The module docstring's own division of labour — "The candidate issuer
owns primary-evidence replay. This reader authenticates issued bytes and, when
given a snapshot, checks the acknowledged session rows" — is what fails: the
reader checks the rows the file chose to acknowledge, not the rows the night
actually produced.

**Minimal fix (one line, after `finalized` is bound at `:195` and inside the
`ledger_snapshot is not None` branch):**

```python
_require(set(session.finalized_slots) == {slot["slot"] for slot in finalized},
         "session_finalized_rows_undisclosed")
```

Defect-shaped regression: exactly the demo above — an aborted 12-slot session
with 9 finalized rows, a file disclosing 6, must refuse with that named detail
and must not appear in `load_epoch_continuations`.

---

## SHOULD-FIX

### S1 — the retained set is entirely issuer-asserted: `anchor_v3_resolved` is unverifiable and `anchor_v3_detail` may be null

`joulewise/calibration_epoch_continuation.py:201-203, 216-218`

The ledger row carries disposition and `exact_bound_lexeme_s` (both
cross-checked at `:240-241`) but not anchor-v3 resolution, so the reader cannot
re-derive it. `:203` requires `detail is None` when resolved, but nothing
requires a detail when **not** resolved. A `valid` row whose bound exceeds the
level screen can therefore be dropped from `m` by asserting
`anchor_v3_resolved: false, anchor_v3_detail: null` — and unlike B1 the row is
still disclosed and still cross-checks, so the omission is invisible.

This one cannot be fully closed (the ledger simply does not store the replay
outcome), but it can be made *auditable*: require every excluded valid capture
to name its exclusion class.

```python
_require(slot["anchor_v3_resolved"] or slot["disposition"] != "valid"
         or (isinstance(slot["anchor_v3_detail"], str) and slot["anchor_v3_detail"]),
         "slots.anchor_v3_detail_required_for_excluded_valid_capture")
```

The contract already asserts at `docs/contracts/epoch_continuation.md:52-53`
that exclusion "is never based on the magnitude of a bound". Nothing in the
reader enforces or even records enough to check that claim. With B1 fixed and
S1 fixed, a human reading the continuation can see every dropped capture and
why.

### S2 — the contract says `continuation_refusals` is recorded "always"; the code records it only when non-empty

`docs/contracts/epoch_continuation.md:134-136` vs
`joulewise/calibration_bracketing.py:2128-2129`.

The **code is right** — gating on non-empty is what keeps the no-continuation
evaluation record byte-identical for the arm-readiness receipts that hash it
(verified: `tests.test_arm_readiness` 71 tests OK, and with an empty registry
`acceptance_judged_epochs` returns a single-element tuple, `matched_epoch`
resolves to the original `identity_epoch`, `stale_fields` is computed exactly as
before, `basis` stays `"exact_identity_epoch"`, and neither
`continuation_refusals` nor the `evaluation_record()` keys appear). It is the
**doc sentence** that is wrong, and it is wrong in the direction that would
invite a future seat to "fix the code to match the contract" and break every
receipt hash. Change the doc to: "recorded as `acceptance.continuation_refusals`
when at least one registered continuation refused; absent otherwise, so an
evaluation with no registered continuation is byte-identical to the pre-D-102
record."

### S3 — a `systematic-invalid` row inside the equivalence night is acknowledged, and therefore permanently exempt from the trigger it exists to fire — although the equivalence rule never examined it

`scripts/issue_epoch_continuation.py:114` (every finalized attempt is
acknowledged, unconditionally) → `joulewise/calibration_bracketing.py:2381-2383`.

The equivalence arithmetic ranges only over `valid` + anchor-resolved rows
(`calibration_epoch_continuation.py:216`). A `systematic-invalid` row in the
same night entered no comparison, yet it is acknowledged and thus never fires
`new_systematic_failure_challenges_preflight_screen`. So a night can carry an
un-adjudicated systematic instrument failure, grant epoch continuation on its
six good captures, and take that failure permanently off the trigger surface.
Nothing in the issuer refuses to prepare a PASS candidate from a night
containing a systematic-invalid slot (`:104` admits it).

I flag this **as a design question for the magistrate, not a seat defect**: the
seat implemented the authority literally. Brief 155 §17 says "EXCLUDING exactly
`acknowledged_attempt_ids` ... those rows were judged under r6 by the
equivalence rule" and synthesis 153 §20 defines the set as "the adjudicated
session's finalized attempt ids". The brief's *justification* ("judged by the
equivalence rule") is true only of the retained rows; the brief's *definition*
covers all finalized rows. The two disagree, and the seat followed the
definition. Two clean resolutions: acknowledge only retained rows, or have
`prepare-candidate` refuse a night containing any `systematic-invalid` slot.
Note this is not a regression against today's behaviour — pre-change the
evaluation returns stale before reaching the trigger block on a 25G83 machine —
but it is a weakening relative to the state the continuation is meant to create.

---

## NITS

### N1 — `check` picks which acceptance to trust from the untrusted candidate

`scripts/issue_epoch_continuation.py:273`. `ISSUED_ACCEPTANCE_REGISTRY.get(value.get("acceptance_id"))`
reads the acceptance id out of the file being checked, so `check` will happily
authenticate and print rc 0 for a continuation of a **retired** acceptance
(r5) if one is registry-pinned. The production loader is unaffected — it passes
the artifact it already loaded, and the r5 case is correctly refused there
(`tests/test_epoch_continuation.py:225`). Suggest comparing against
`acceptance_module.ACTIVE_ACCEPTANCE_ID` and naming the mismatch.

### N2 — the issuer can emit a candidate the reader will refuse

`scripts/issue_epoch_continuation.py:87` emits disposition `no_row` for a
declared slot with no observation, but `calibration_epoch_continuation.py:205`
only tolerates a null slot when `session_state == "aborted"`. A `finalized`
session with a missing declared-slot row therefore yields an unloadable
candidate. Fail-closed, so harmless, but `prepare-candidate` should refuse at
preparation time rather than write a file that can never be issued.

### N3 — hand-typed operatives in the contract prose, outside the guard's reach

`docs/contracts/epoch_continuation.md:180-182` types `0.032898493715362`,
`0.009724`, `0.03289849371536248`, `0.00972358928879385`. All four are
**correct** (checked against `calibration_bracketing.py:332-334` and Ed's issue
316). But `tests/test_mint_policy_resolver_guard.py` only scans
`joulewise/**/*.py` and `scripts/**/*.py`, so nothing pins these. No code
literal violates the mint policy — the new module and tool read every
comparator through `continuation_rule` → `acceptance_generation_operatives`.
Consider extending the guard to `docs/contracts/*.md`, or phrasing the worked
example without repeating the digits.

---

## Answers to the eight questions

**(1) Authentication — holds, with the B1 hole.** Unregistered id → `:154-155`
`continuation_unregistered`. Byte-pin mismatch → `:156-157` (C18 kills the
removal of this check; the whitespace-rotation test isolates it cleanly since
the canonical digest still agrees). `candidate_not_issued` → `:151`, checked
before anything else and keyed on **presence**, so `false` also refuses.
`verdict != "pass"` → `:168`, before the arithmetic, so `inconclusive` cannot
slip through. `derivation_sha256` → `:169-170` over every other top-level key.
r5's id/sha → `:162-167` requires **all three** of `acceptance_id`,
`acceptance_file_sha256`, `acceptance_derivation_sha256` to equal the loaded
artifact's, each in its own iteration with its own named detail, so file-sha
matching while derivation-sha does not (or the reverse) refuses naming the
field that failed — `tests/test_epoch_continuation.py:225-235` covers all three
against real r5 values. The acceptance itself must re-authenticate as
`artifact_role == "issued"` (`:158-159`). **The gap is not in the pins; it is
that the pins authenticate a file whose retained set the reader cannot
reconstruct (B1, S1).**

**(2) Session cross-check.** With a snapshot: snapshot has no refusal reasons;
session present; state terminal AND equal to the file's; `session_kind ==
derivation`; `declared_slots` equal as an ordered list; `ledger_schema` equal
and `head_sequence >= ` the file's; then per **disclosed** finalized slot —
row present with matching `attempt_id`, present in `observation_by_attempt` and
belonging to this session, matching `content_id`, matching
`classification_disposition`, matching `exact_bound_lexeme_s`, and for retained
rows a matching `identity_epoch`. Missing: the reverse-direction completeness
check (B1). `ledger_snapshot=None` → `cross_check =
"skipped_no_ledger_snapshot"` (`:224`), surfaced in
`Continuation.evaluation_record()` and into the freshness record. **Nothing
production-facing calls it that way:** `evaluate_calibration_bracket` returns
`("calibration_ledger_snapshot_required",)` at `calibration_bracketing.py:2017`
long before the continuation call at `:2058`, so the degraded path is reachable
only from `check --candidate` without `--ledger`, where it is printed verbatim.
Contract `:143-148` states this correctly.

**(3) Loader semantics — all as specified.** `matched_epoch`
(`calibration_bracketing.py:2060-2063`) is the first judged epoch equal to
`observed_identity`, defaulting to the artifact's; `stale_fields` is computed
against `matched_epoch` (`:2069-2073`) so it is empty on a match;
`expected_identity_epoch` names the matched vector; `basis` flips to
`"epoch_continuation"`; and `freshness.update(matched_continuation.evaluation_record())`
adds `continuation_id`, `continuation_file_sha256`, `session_id`, `m`,
`verdict`, `ledger_cross_check`. `ACCEPTANCE_IDENTITY_FIELDS` **is**
`IDENTITY_EPOCH_FIELDS` (`calibration_bracketing.py:194`) — verified at runtime,
so there is no silent field-set mismatch making the match unreachable.

*Doubling counterexample, confirmed by reading `:2350-2358`:* r6 has
`corpus_n = 17`, threshold 34. 30 distinct valid 25F84 contents plus 12 valid
25G83 contents pools to 42 ≥ 34 and would fire; per-epoch the counts are 30 and
12 and `any(count >= 34 ...)` is False, so it does not. The code builds one
count per judged epoch and never sums — the comprehension iterates
`for epoch in judged_epochs` with the sum *inside*. Matches contract `:194-198`.

*Range expansion / systematic failure:* both filters are
`attempt_id not in acknowledged_attempt_ids and dict(identity_epoch) in
judged_epochs` (`:2369-2372`, `:2381-2383`). `acknowledged_attempt_ids` is the
union over *matched continuations only*, so a future derivation session's rows
and ordinary 25G83 rows both participate — nothing keys on session kind.
Confirmed.

*25F84 no-continuation path byte-identical:* yes. With the registry empty
`judged_epochs` is the one-element tuple of the artifact's own epoch,
`matched_continuation` is `None`, `continuation_refusals` is empty, and both new
record keys are gated (`:2126-2129`), so the record shape is unchanged — see
S2 for the doc that contradicts this. `tests.test_calibration_bracketing` (92,
OK skipped=1) and `tests.test_arm_readiness` (71, OK) pass unmodified.

**(4) Container type — works.** `acceptance_judged_epochs` returns
`tuple[MappingProxyType, ...]`. `dict in tuple-of-mappingproxy` resolves via
`mappingproxy.__eq__` against the underlying dict; verified at runtime:
`{'a':1} in (MappingProxyType({'a':1}),)` → `True`. `dict(matched_epoch)` also
yields a plain JSON-serializable dict for the record.

**(5) The tool — re-derives the science.** Snapshot loaded with
`require_committed_pin=True, verify_custody=False, mode="read_replay"` (`:50-54`);
session must exist, be derivation-kind, terminal, and declare exactly 12 slots
(`:71-75`); each finalized slot re-read through the acceptance issuer's own
`_read_member_evidence` (imported, not reimplemented — and that helper
re-hashes `manifest.json` and `instrument_evidence.json` against the ledger
row's `artifact_sha256`, refusing on drift); `content_id_from_artifact_hashes`
recomputed and compared (`:95-96`); `anchor_v3_replay_outcome` reused (`:97`);
the stored lexeme must equal `exact_bound_lexeme_s` exactly (`:99`); retained
epochs unanimous (`:120`) and different from the acceptance's (`:121`); m, min,
max, range in Decimal from lexemes at full precision
(`equivalence_statistics`, whose working precision is sized to the represented
places of every operand, `:81-86`). Comparators come from
`acceptance_generation_operatives` (the `_D102_GENERATION_DERIVATIONS` registry)
and are cross-checked against the artifact's `decimal_derivation.ratified_operatives`
for **both** screens, refusing with the named field
(`calibration_epoch_continuation.py:53-68`). *One gap:* `_s9_projection` reports
`maximum_budgetable_drift_s` straight from the artifact (`:177`) without the
same registry cross-check the two screens get — cosmetic here, since it is not
a comparator, but Ed's issue names the budget ceiling as part of the reference
envelope.

S9 record is a **cross-check only**: `expected` is built entirely from the
independently derived `record` (`:240`), the witness is only ever the right-hand
side of `_crosscheck`, and lines `:244-251` copy `record[key]`, never
`witness[key]`. Disagreement raises `ContinuationRefusal(field)` →
`REFUSED: equivalence_record.<field>` → rc 3 (`:320-323`). Unknown witness keys
refuse (`:214-215`) rather than being ignored.

INCONCLUSIVE/FAIL write nothing: `rc = VERDICT_EXITS[...]`; `if rc: print;
return rc` at `:253-256`, before `args.out.open` at `:264`. `--out` under any
resolved `configs/calibration` pair is refused (`:57-61`), as is an existing
output without `--force` (both there and again structurally by `"xb"` at
`:264`), plus out-overwrites-input (`:230-231`) and
out-overwrites-primary-evidence (`:235-237`). Checked before derivation runs.

**(6) Three cut→test claims, assessed by reading, then confirmed by running.**
*C11* `len(values) >= MINIMUM_RETAINED → True`: the test builds 5 valid at
`0.025` + 7 ordinary-invalid, so m=5; mutated, spread 0 and every value under
the level screen make the verdict `pass` → rc 0 and a file written, failing
both `assertEqual((rc, error), (5, ""))` and `assertFalse(self.out.exists())`
(`tests/test_epoch_continuation.py:399-404`). Kills.
*C12* `disposition == "valid" and resolved → resolved`: 6 valid at `0.025`, 3
ordinary-invalid at `0.9`, 3 valid-but-unresolved at `0.9`; mutated, the three
resolved ordinary-invalid rows at `0.9` enter the retained set, m becomes 9 and
`0.9` blows the level screen → FAIL rc 4, so `self.candidate()`'s
`assertEqual((rc, error), (0, ""))` fails (`:406-411`). Kills.
*C18* `file_sha == registered.get("file_sha256") → True`: the test rotates one
`\n` to a space, which changes the bytes but not the JSON semantics or the
canonical digest, so with the pin check removed everything downstream still
authenticates and `assertEqual(loaded, ())` fails (`:210-219`). Kills — and the
isolation is deliberate and correct.
All three confirmed empirically; full replay 18/18 killed, source SHA-256s
restored. The runner's `killed` predicate requires a *failure* and not an
*error*, which is the conservative direction.

**(7) Hand-typed operative digits.** None in code. `grep -nE
"[0-9]\.[0-9]{6,}"` over the two new modules and the bracketing diff returns
nothing new; every digit in `calibration_bracketing.py:243-335` predates this
commit. `tests.test_mint_policy_resolver_guard` passes. Four operative digits
do appear in the new contract prose — see N3.

**(8)** Reported at the top. 202 tests, OK (skipped=1), rc 0, ~64 s; not
stopped.

---

## Scope honesty of the seat's own report

The seat's envelope self-declares `status: blocked`, `implementation:
partial`, with F1/F3 naming the two unbuilt writer integration sites
(`scripts/validate_powermetrics_fiducial._derive_preflight_systematic_screen_s`
and its derivation-only branch), the unregistered
`calibration_epoch_continuation_invalid` diagnostic, and the interrupted
canonical suite. Brief 155 cut (m) — "each routed site accepts 25G83 with a
valid continuation and refuses without one" — is correspondingly unmet. I
confirm those are **declared, not concealed**: the contract's own consumer
census (`docs/contracts/epoch_continuation.md:230-243`) marks both writer rows
as required integration sites and closes with "The ordinary and derivation-only
writer integrations, governing reason registration, and subsequent issued
registry entry are promotion requirements." The one claim I would not accept as
written is in the seat's own prose — "Missing snapshots are explicitly labeled"
is true, but "checks the acknowledged session rows" is only true of the rows the
file elects to acknowledge (B1).

Registry is empty; no continuation issued; r6 bytes and
`ISSUED_ACCEPTANCE_REGISTRY` unchanged (guarded by the seat's own
`all_acceptance_bytes_and_registry_remain_frozen` test, which passes).
