# 59d — Cold gate #3, Packet C verdict (cold Fable seat): skeleton first-use class, third occurrence

Cold Fable seat (fresh session, read-only) on the Packet C sheet (appended below the verdict). Paired refuter: `59e-opus-refuter-C-skeleton.md`. Raw verdict follows.

---

### Ruling: (iv) — bench-sized round 4 (five dictated clauses, no Sol round) + reshape the EXISTING ledger into a criterion-closed inventory with a mechanical home-section test, run ONCE, then STOP the class on the skeleton until fill.

**Interface**

- Files: `docs/paper/draft-v2-skeleton.md` only (ledger stays at `## First-use audit ledger`; add a fourth column `Status ∈ {built-before, glossed-at-first-use, audience-vocabulary, forward-pointer-next-paragraph, FAILS}` and a preamble defining *audience-vocabulary*: textbook statistics/plain-English words the intended reader — a metrology/CS professor — uses without definition; listed explicitly, so a delta must argue the class, not re-raise the word); new test `tests/test_paper_first_use_ledger.py`.
- Test: for every ledger row, the term's first occurrence outside `<!-- -->` and build notes lies inside the heading range named in "First reader-facing home". This would have caught the "sample standard deviation → Section 4" row today.
- Seats: magistrate applies the five clauses at the bench (below the rule-9 delegation threshold; luna's wording for four is usable). Inventory writer: Sol xhigh, reading the whole skeleton once, adding every §2/§4 term luna named plus any it finds, each with a status. Delta auditor: luna (the strictest reader — make its strictness produce *inventory omissions*, not prose asks); its output is a list of candidate terms absent from the ledger, nothing else. Magistrate rules each status; the FAILS/audience-vocabulary boundary is the magistrate's call, recorded in the ledger, never the delta's.
- Acceptance: zero FAILS rows, zero delta-found omissions, test green, and the sentence "Terms the final first-use audit could not build: none" replaced by the true count. Register one queued item: rerun the inventory pass once on the filled draft (the test carries over as drift guard).

**Reason.** The evidence table below shows the residue is not a fixer failure repeating: five of luna's thirteen terms are genuine but each one clause, and eight are reviewer over-reach (glossed purpose at first use, ordinary statistical vocabulary, or a dictated forward pointer to the very next paragraph). Three rounds failed the same way because each delta re-lints prose against its own threshold and the ledger is self-graded with no criterion — so an enumerated round 4 (i) predicts a fifth list, and (iii) leaves a ledger that says "none" while omitting every §2 term and mis-homing one. Ed's standard stays binding (I have not relaxed it — every genuine item is cured), but the standard is a criterion, and the fixture must carry that criterion so disagreement collapses to a status column the magistrate rules on. That is the Packet A move for prose: no renderer exists, but home-section membership is mechanically checkable and the vocabulary class is explicitly closed.

**Per-term evidence (skeleton @ 9a563caf)**

| Term | First use | Finding |
|---|---:|---|
| warm-up pulses | :122 | (b) plain English; "After three warm-up pulses, it commands 59…" already implies exclusion from the measured train. |
| base-two varied-gap schedule | :122 | (c) purpose glossed (anti-aliasing), mechanism not; "base-two" only built at :945. One clause: "gaps stepping through powers of two". |
| sampler cadence | :122 | (b) "requested 100-ms sampler cadence" + :112 built records over intervals. |
| quiet trace | :122 | (b) "on both sides of the train"; "power trace" introduced at :118. |
| clock-anchor bound | :124 | (c) named one paragraph before its build at :126; six-word appositive ("the uncertainty in placing the trace on wall-clock time, built next"). |
| 99% quantile / \(t_{0.995,16}\) | :128 | (c) "99% quantile" and subscript 0.995 are never tied together; a replicator must guess two-sided 99% = one-sided 0.995. One clause. |
| sample standard deviation | :128 | (b) for the reader (textbook term; 17 bounds printed in A.3.8 so it replicates), but the LEDGER row is wrong (home "Section 4", formula :254). Cheapest: pointer clause "(the n−1 formula of Section 4)" + fix the row. |
| corpus range | :128 | (b) largest minus smallest is ordinary. |
| directional comparison | :501 | (c) that the direction was fixed before collection arrives only at :573. One clause. |
| Holm step-down correction | :502 | (a) purpose glossed at first use; mechanics at :552 after the p-values exist — correct order. Over-reach. |
| measurement variance | :507 | (b) textbook term; the formula at :515-519 immediately shows it. |
| decision-interval sign test / direction gate | :559 | (a) the dictated forward pointer to the next paragraph (:563-574), phrased as a cross-reference. Over-reach. (Nit: "sign test" risks confusion with the nonparametric sign test — consider "sign check".) |

Five clauses total; the four (b)-and-glossed items go into the ledger as audience-vocabulary rows so they cannot be re-raised without argument.

**Cold-gate #1 waiver.** Not a missed trigger: the trigger fired and the consult was cold gate #1 itself; its RESHAPE (checkable replay targets) demonstrably closed the replication class — all thirteen round-3 replay targets PASS in report 57. What the trace should record is a *mis-scoped reshape*: replay targets cover numbers, not glossing, so the first-use class got no fixture and its convergence prediction (23→3→0) was extrapolated from the wrong class. Record as "reshape mis-scoped, first-use class unfixtured", not "trigger eaten".

VERDICT: (iv) bench round 4 (five clauses) + criterion-closed ledger inventory with home-section test, once, then stop the class until fill

---

## Packet C sheet (as handed to both seats)

# Cold gate #3 — Packet C (mechanically assembled, 2026-09-01 16:20)

## Packet C — draft-v2 skeleton: THIRD consecutive delta finding strict first-use residue

Trigger: STANDING ESCALATION — "two consecutive rounds failing with the SAME SIGNATURE — same
defect class, another missed call site" → the next spend is a CONSULT, not another round. This
class has now failed three deltas running:

| Round | Fixer (report) | Delta (report) | First-use finding |
|---|---|---|---|
| 1 | terra `27-terra-fix-08-skeleton.md` (after refuter 22 + Opus pedagogy 25) | luna `36-luna-delta-27-skeleton.md` | PED-FU-01/02/03: Student-t, excursion/bound, total SE / metrology scatter named before built |
| 2 | Sol `51-sol-fix-skeleton-2.md` (ruling `36b`, amended by cold gate #1 `48c` §Packet 2 — which WAIVED the consult: "the bar is moving toward Ed's standard, so no consult") | Opus (pedagogy lens; findings folded into the round-3 brief, scratchpad `run-fix-skeleton-3.md`, §Should-fix glosses 1–13) | covariance, recorded stochastic term, √2 reason, s_b, rounding rule, effective sample size, dangling 0.041, 12.706 provenance |
| 3 | terra `56-terra-fix-skeleton-3.md` (every cure DICTATED by the lead) | luna `57-luna-delta-skeleton-3.md` | F2 §2 (:122-128): warm-up pulses, base-two schedule, cadence, quiet trace, clock-anchor bound, quantile notation, sample standard deviation, corpus range. F3 §4 (:501-560): Holm mechanics, measurement variance, directional comparison, direction gate named before gloss |

Every round's NUMBERS have passed (registration, survival map 45 ranges/672 lines exact, STOP_FILL
census 50/33/38, t/p values). The residue is purely the first-use class, and every round has been an
ENUMERATED list of glosses; each fresh reader then finds the next un-enumerated term. This is the
same structural signature Packet A had (enumeration of surfaces vs a rule) — Packet A was reshaped
to "the script renders the sheet". Prose has no renderer.

Bench facts (magistrate-measured at `feat/2026-09-01-skeleton` @ `9a563caf`, worktree
`~/code/JouleWise-wt-skeleton`):
- F1 of report 57 (DG-128 cited 1150–1166; body is 1151–1167) is a fixer miss on a dictated item;
  bench-fixed and committed at `9a563caf`. Not part of this packet.
- `docs/paper/draft-v2-skeleton.md` is 1,2xx lines; it is a SKELETON: 50 `[FILL:…]` placements
  (33 STOP_FILL registry rows) will be filled when the `_v5` campaign lands, and §2/§4 prose is
  expected to be revised at fill time. `docs/paper/draft-v1.md` is frozen (the paper reviewers'
  copy); the skeleton is the round-7 successor.
- Ed's binding writing standard (global CLAUDE.md, "Writing standard"): first-use test run
  MECHANICALLY before delivering; a term whose meaning arrives only in later text fails the draft;
  pedagogy reviewed as its own dimension; "Diff ritual".
- **The skeleton ALREADY carries a self-graded inventory**: `## First-use audit ledger` at
  :1189-1248 (49 term rows, "Terms the final first-use audit could not build: none"), written by
  the fixer seats. NONE of luna's F2 terms (warm-up pulses, base-two schedule, cadence, quiet
  trace, clock-anchor bound, corpus range) appears in it; "sample standard deviation" is listed
  with home "Section 4" although luna finds it used at §2 :128 first. So the ledger is
  enumerated-and-self-graded — the very pattern every delta has beaten. Option (ii) below is
  therefore "make the EXISTING ledger the fixture" (delta audits the ledger for omissions; a test
  asserts each ledger term's first occurrence lies in its named home section), not a new file.
- Cost so far on this class: 3 fixer rounds + 3 deltas + 1 Opus pedagogy pass + cold gate #1.

Read, in order (all on main unless stated):
1. `36b-RULING-skeleton-delta.md` (incl. its cold-gate section) and `48c-COLD-GATE-1-verdict-42b-36b.md` §Packet 2.
2. Scratchpad `run-fix-skeleton-3.md` (the round-3 dictated brief) — copied below as §C.1.
3. `57-luna-delta-skeleton-3.md` (on the skeleton branch, trace dir) — F2/F3 verbatim.
4. Branch `feat/2026-09-01-skeleton` @ `9a563caf`: `docs/paper/draft-v2-skeleton.md` §2 (:100-160) and §4 (:490-570) — READ THEM; judge whether luna's F2/F3 residues are real first-use failures under the standard (a term whose meaning arrives only in later text) or reviewer over-reach (e.g. "cadence", "quiet trace" may be ordinary English; "quantile notation" may be built at :128).

Question for the seat: what is the right next spend? Options the magistrate sees (strike or add):
- **(i) Round 4, enumerated**: dictate the F2/F3 glosses, Sol high, luna/Opus delta. Cheap; the
  same signature predicts a fourth residue list.
- **(ii) RESHAPE to an inventory**: one seat (xhigh) reads the WHOLE skeleton once and produces a
  closed TERM INVENTORY — every term of art / criteria word / technical verb, its first-use line,
  and status {built-before, glossed-at-first-use, FAILS} — kept IN the existing ledger at :1189 (or split out — seat decides); the fixer cures every FAILS row; the delta seat
  audits the INVENTORY for completeness (missed terms) rather than re-linting the prose from
  scratch. Acceptance = zero FAILS rows and zero delta-found omissions. A test can at least assert
  every inventory term's first occurrence line matches the inventory (mechanical drift guard).
- **(iii) STOP the class on the skeleton**: merge now (numbers pass; F1 fixed); register the
  first-use inventory (ii) as a queued item that runs ONCE on the filled draft, because §2/§4 will
  be rewritten at fill time and glosses added now may be rewritten away. Risk: the skeleton is
  what the next writer reads; unglossed prose propagates.
- **(iv) something else.**

Also rule: is the cold-gate #1 waiver ("bar moving toward Ed's standard, no consult") still
defensible after a third occurrence, or should the trace record it as a missed trigger?

Deliver: `### Ruling: <(i)|(ii)|(iii)|(iv)>`, the interface if (ii)/(iv) (file names, acceptance,
who audits what), a one-paragraph reason, then `VERDICT: <ruling>` on its own line last.

### C.1 round-3 brief (skeleton), verbatim

ORIGIN: claude-code lead (Fable magistrate), JouleWise repo, worktree `feat/2026-09-01-skeleton` @ `b1d23e41`.
HOP: 1 (you must not call Claude by MCP, `claude -p`, or any launcher).
GENRE: implementation (prose) — draft-v2 skeleton fix round 3. Every cure below is DICTATED (bench-verified by the lead against the sources named); apply them, do not redesign. Round 2 (report 51) was correct on every number; the delta seat found one wrong physical attribution (from the LEAD's brief, not the fixer) plus pedagogy residue.

WRITE_SCOPE: ["docs/paper/draft-v2-skeleton.md", "docs/paper/results-fill-registry.md"]
`docs/paper/draft-v1.md` is FROZEN. No `git rebase`. Leave the tree dirty.

## Blocker — :536-538 cross-reference misattributes the mechanism
The sheet (`docs/paper/round7/dependence-sensitivity.md`, other branch) has TWO scenarios: an ESTIMATED AR(1) fit (n_eff = 5.764703, ν = 4, t = 8.111070, p = 0.001256) and a STIPULATED effective-n HALVING (n_eff = 5, ν = 4, t = 7.607258, p = 0.001602, "a named pessimistic scenario, not a bound"). The draft currently attributes 7.607258/0.0016 to AR(1). Replace the clause with exactly this substance:
"…works the same ten differences on its separate branch under a stipulated halving of the effective sample size to five blocks — a named pessimistic scenario, not an estimate — obtaining ν = 5 − 1 = 4, t = 7.607258, p = 0.0016; its separately estimated AR(1) model, which treats adjacent block errors as serially correlated, leaves n_eff = 5.76 and gives t = 8.111070, p = 0.0013. The documents differ in that dependence assumption, not in their data."

## Should-fix glosses (apply each; line numbers at b1d23e41)
1. :504 "recorded stochastic energy term" → "for every recorded energy term that carries its own measurement variance — the gross repetition term is left out because its scatter is already counted in se_repeat —" (source: `joulewise/analysis_engine/estimators.py:386-388` excludes `GROSS_REPETITION_TERM`, `:44`).
2. :506 "covariance" first use → "covariance, the part of the two conditions' measurement error that moves together and therefore cancels when B is differenced against A".
3. :128 restore the √2 reason: "the two-draw rule — two fresh capture bounds are drawn, and the spread of their difference is √2 times one capture's spread — so t_{0.995,16} × s_b × √2".
4. :128 bind s_b: "…the sample standard deviation is s_b = 2.460856 ms".
5. :128 rounding rule in words: "rounded to the nearest microsecond, with an exact tie going to the even digit (`ROUND_HALF_EVEN`)".
6. :128 and :1131 "source S17" → "the retained calibration acceptance file `configs/calibration/calibration_acceptance_d079_v2_n17_r3.json` (registry source S17)".
7. :537-538 "effective sample size" → "the effective sample size — the number of independent blocks that would give the same repeat scatter — to five, so its degrees of freedom ν fall to 5 − 1 = 4" (folds into the blocker sentence).
8. :543 dangling "the existing illustrative 0.041" → "Pairing the fixture's 2.8 × 10⁻⁶ with a second illustrative raw probability of 0.041 for the other comparison…".
9. :424-426 provenance of 12.706: the value comes from the fixed table `_T_CRITICAL_95[1] = 12.706` in `joulewise/aggregate.py:41-42` (`student_t_critical_95`), used by `joulewise/detection_floor.py:696`; the artifact records `t_critical_source: joulewise.aggregate.student_t_critical_95.v1` (`detection_floor.py:1283`). Replace the `_ci_t_critical` citation with this. (`_ci_t_critical`, `estimators.py:224-228`, serves the direction-test intervals only.)
10. :1127 appendix heading date → "2026-07-22 to 2026-07-25 instrument-validation captures" (member ids span `20260722T145535` → `20260725T060617`).
11. DG-128 in the registry: cite the table body lines (post-edit `:1134-1151` equivalents), not the heading.
12. :438-440 precision claim: say the replay from the printed 10-decimal operands agrees to nine significant figures (it cannot support ten).
13. Holm paragraph (:541-547): one forward-pointer clause that Holm is one step and the decision-interval sign test (the direction gate, :549+) is the other — the sheet's ν = 9 row fails the direction gate on these same deltas while both comparisons pass Holm.

## Verify (paste tails)
- `python3 -m unittest tests.test_paper_terms_lint`
- survival-map coverage one-liner and STOP_FILL census one-liner from report 36 (V3/V4): must still give 45 ranges / 672 exact, 50 placements / 33 rows / checklist_exact=38.
- `grep -n '8.111070\|7.607258' docs/paper/draft-v2-skeleton.md`
- `git diff --check`; `git status --short` (only WRITE_SCOPE dirty).

## Report
`claude-codex-report/v1` envelope. Findings: item → line → applied text (short). Any number you cannot source → NEEDS_RULING; never invent one.
