# 59f — Magistrate ruling on cold gate #3, packets B and C

Packet A (dependence sheet) was ruled in `59a`/report 60: RESHAPE "the script renders the sheet" — landed at `feat/2026-09-01-dependence` @ `1f6182bd`; Opus delta (mutation table) and a fresh-Fable pedagogy pass over the template are the acceptance seats. This file records B and C.

## Packet B — fiducial receipt inventory (`59b` cold Fable: BENCH-EDIT; `59c` Opus: AMEND-CURE)

**Ruling: BENCH-EDIT, executed.** Commits `71215cae` (code) and `a2f99b09` (contract) on `feat/transfer-fiducial-01`. The cold seat's "closed by execution" definition was adopted verbatim into `docs/contracts/transfer_fiducial.md`: with every `joulewise/` module except `__main__` pre-imported, a module is a member when a function, method, lambda, or comprehension whose code object names its file receives a call while the test runs `fit_run` on `synthetic-transfer-r01` and `build_capture`. Inventory 24 → 9; `RECEIPT_TRACE_BLIND_MODULES = ("joulewise/clock.py",)` because dataclass-generated methods carry `co_filename "<string>"`; the test assertion is two-way (`executed ∪ blind == inventory`, `blind ⊆ inventory`, `executed ∩ blind = ∅`). Bench mutation probes M1–M4 all killed (recorded in the transcript; delta seat terra, report 62, re-checks them).

Opus items **not adopted**, with reasons:
- (a) subprocess isolation — the pre-import makes the trace order-independent by construction (verdict B measured the same count in two orders); isolating further buys nothing the assertion does not already prove.
- (b) an explicit pre-import name list — replaced by `pkgutil.walk_packages` + the `__main__` skip + an asserted lower bound on the imported count; a hand list would be a second self-graded inventory.
- (c) per-verdict fixture coverage + refusal-vocabulary closure — a real limitation, **registered, not cured** (the receipt inventory freezes the code that *ran*, not the code that *could* run on a refusing bundle).
- (d) per-function digests — struck under D-161: the adversary here is the operator; whole-file freeze plus the stated re-issue rule (any edit to `bundle_read.py` or `adapters/powermetrics.py` before first receipt → re-issue; after data → no cure) is the fail-closed shape the evidence rule needs.

## Packet C — skeleton first-use class, third occurrence (`59d` cold Fable: (iv); `59e` Opus: (ii))

**Ruling: (iv) as the cold seat specified, taking Opus's extra terms where one clause is cheap.** The two seats agree on the shape — the ledger becomes a criterion-closed inventory with a mechanical home-section test, run once, then the class STOPS on the skeleton until the `_v5` fill — and disagree only on how many of luna's thirteen terms are real. That boundary is the magistrate's (verdict 59d: "the FAILS/audience-vocabulary boundary is the magistrate's call, recorded in the ledger, never the delta's"). Ruled per term:

| Term | Line | Ruling | Cure |
|---|---:|---|---|
| base-two varied-gap schedule | :122 | FAILS (both seats) | "gaps stepping through powers of two" |
| clock-anchor bound | :124 | FAILS (both) | appositive: "the uncertainty in placing the trace on wall-clock time, built next" |
| 99% quantile / \(t_{0.995,16}\) | :128 | FAILS (both) | tie them: two-sided 99% = the 0.995 one-sided point |
| directional comparison | :501 | FAILS (both) | "whose direction was fixed before collection" |
| warm-up pulses | :122 | FAILS (Opus) — one clause is cheap | "which are discarded" |
| quiet trace | :122 | FAILS (Opus) — "quiet" is a criteria word checked at :124 | "no commanded pulse" |
| sample standard deviation | :128 | audience-vocabulary, but ledger row :1216 mis-homed | pointer clause "(the n−1 formula of Section 4)" + fix the row |
| measurement variance | :507 | FAILS (Opus) — load-bearing vs repeat scatter | one appositive |
| sampler cadence, corpus range | :122, :128 | audience-vocabulary (both seats) | ledger rows, no prose change |
| Holm step-down, direction gate | :502, :559 | glossed-at-first-use / forward-pointer-next-paragraph (both seats) | ledger rows; "sign test" → "sign check" (59d nit) |

Interface (from 59d, binding): ledger gains a `Status` column ∈ {built-before, glossed-at-first-use, audience-vocabulary, forward-pointer-next-paragraph, FAILS} and a preamble defining *audience-vocabulary* (textbook statistics / plain English the metrology-CS professor uses without definition — listed, so a delta must argue the class, not re-raise the word); new test `tests/test_paper_first_use_ledger.py` asserts each ledger term's first body occurrence (outside `<!-- -->` and build notes) lies inside its named home section; Opus's closure clause (bolded/italic-introduced tokens ⊆ ledger terms) is adopted where it can be made deterministic, otherwise recorded as the inventory writer's charge. Seats: magistrate applies the prose clauses at the bench (below the rule-9 delegation threshold); inventory writer Sol xhigh over the whole skeleton; delta auditor luna, whose output is ONLY a list of ledger omissions. Acceptance: zero FAILS rows, zero delta-found omissions, test green, "could not build: none" replaced by the true count. Queued item: rerun the inventory once on the filled draft.

## Cold gate #1's waiver (`48c` §Packet 2), both seats concur

Recorded as **mis-scoped reshape / mis-ruled — not a missed trigger.** The trigger fired and the designated organ ruled, but its RESHAPE targeted replay targets (numbers), which it closed (all thirteen round-3 replay targets PASS), while the first-use class got no fixture; its "23 → 3 → 0" convergence prediction was extrapolated from the wrong class. Doctrine note for future gates: **count convergence is never a defense against a signature** — falling counts are motion, which is the disposition the trigger exists to catch.

VERDICT-B: BENCH-EDIT executed; delta pending (terra 62)
VERDICT-C: (iv) — bench clauses + criterion-closed ledger + home-section test, once, then STOP the class until fill
