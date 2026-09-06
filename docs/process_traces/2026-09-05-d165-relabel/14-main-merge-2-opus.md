# 14 — second origin/main merge into feat/2026-09-05-d165-relabel (Opus lieutenant)

Worktree `/Users/edr/code/JouleWise-wt-d165-relabel`. Branch head before the
merge: `40590c6c`. Merge base: `434568f0`. `origin/main` moved twice while this
ran (the magistrate is pushing to the shared ref): `b1644210` → `031c79cc`
(README blurb + DURABLE-STATE) → `df657492` (RUN_STATE T35). The merge parent
recorded is **`df657492`** — the tip at commit time. The `b1644210..df657492`
delta is doc-only (`README.md`, `00-DURABLE-STATE.md`, `RUN_STATE.md`).

## Conflicts and how they were resolved

Three files conflicted. The resolution rule was the one from report 13: keep
this branch's D-165 relabel semantics, keep everything main added for other
reasons, never drop or reactivate a registry row.

**`configs/paper_supply/supply_map.json`** — both sides moved the two
`d165_closeout` fixture digests (`inventory.json`, `inputs/validator_receipt.json`)
because the validator source changed on each side. Taken to main's side, then
re-anchored with the contract's fixture-only lane
(`R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 tests/fixtures/paper_custody/repin.py`
— "Repinned five synthetic, non-issuing fixture envelopes; production role
pending"). Only the `d165_closeout` family moved; the other four re-pinned to
identical bytes. Final values:

```
inventory.json          57f28f301112acdb29b8cfe0ea6deb1af187456764ff263eab6231deab10047d
validator_receipt.json  b9949937d5751ce310b1182dcb7f1767c5651f12137ed50460ffef5f72200c0a
```

**`docs/paper/results-fill-registry.md`** — the whole 32-row fill table
conflicted. Main (D-174) rewrote every row's Fill rule to `RETIRED_FALLBACK`
and its Freeze status to `RETIRED_FALLBACK 2026-09-05 (D-174): no submission
placement; former rule …`. This branch had made two D-165 edits to the same
rows. Resolution: main's 32 rows kept verbatim as the base, then the branch's
two edits re-applied on top —

1. the four comparative-R_cm rows lose `; SUPPLIER_PENDING: producer emits .v1
   until the D-165 relabel lands` (the relabel has landed on this branch);
2. the four absolute-R_cm rows keep the branch's producing-artifact wording
   ("Literal `not_applicable` plus the registered comparative-only rationale"
   on the two prefill rows; the full registered rationale sentence on the two
   decode rows) instead of main's base text.

All 32 rows survive; none was dropped, added, or reactivated. The prose
paragraph above the table auto-merged (main did not touch it), so the branch's
cured v2/v1 sentence stands.

**`docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md`** —
append-log; both sides appended. Kept all six of main's new sections in main's
order, then appended this branch's `~12:30 PDT` section after them.

## draft-v2-skeleton.md

The branch never touched `docs/paper/draft-v2-skeleton.md` (empty
`git log $(git merge-base HEAD origin/main)..HEAD -- docs/paper/draft-v2-skeleton.md`,
and no entry in the branch-vs-base diffstat), so there was no D-165 wording
cure to preserve and no conflict. Main's paper-M draft wins wholesale;
`git diff origin/main -- docs/paper/draft-v2-skeleton.md` is empty after the
merge. **Nothing kept from this branch on that file.**

## Allowlist re-anchoring (no widening)

Four existing entries in `tests/fixtures/d165_rationale_allowlist.json` went
stale on line number only — same path, same phrase, same reason — because main
inserted lines above them. Re-anchored, not widened; no entry added, none
removed, no phrase or reason changed except one factual figure label:

| path | old line | new line |
|---|---|---|
| `docs/paper/results-fill-registry.md` | 231 | 262 |
| `docs/paper/results-fill-registry.md` | 246 | 277 |
| `docs/paper/results-fill-registry.md` | 262 | 293 |
| `docs/paper/draft-v2-skeleton.md` | 253 | 1459 |

The draft entry is the unrelated ABBA drift-schematic caption; paper-M renumbered
that figure from 2 to A2, so its reason text now reads "Figure-A2 ABBA drift
schematic caption".

## Test tails (single targets, `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise`)

- `tests.test_d165_rationale_census` — **Ran 8 tests … FAILED (failures=1)**,
  one test red on 11 active occurrences (list below); the other 7 pass.
- `tests.test_d165_dominance_closeout` — Ran 59 tests in 9.701s — **OK**
- `tests.test_dominance_closeout` — Ran 3 tests in 1.710s — **OK**
- `tests.test_paper_custody` — Ran 29 tests in 38.235s — **OK** (after the
  repin; before it, 10 failures on `stale supply-map receipt digest: d165_closeout`)
- `tests.test_paper_terms_lint` — Ran 16 tests in 1.378s — **OK**
- `tests.test_paper_first_use_ledger` — Ran 11 tests in 2.105s — **OK**

Extra prudence check (main reconciled the round-7 checker while this branch
edited three `docs/paper/round7/` documents), and the one auto-merged test
file both sides had touched:

- `tests.test_paper_round7_artifacts` — Ran 67 tests in 599.174s — **OK**
- `tests.test_d117_contrast_v5_pack` — Ran 44 tests in 14.268s — **OK**

## Census RED lines (11 occurrences, 8 lines, 4 files)

Every one is a *denial* sentence — text that says the diagnostic is **not** a
common-time replay — sitting on a line with no `SUPERSEDED` / `LEGACY v1`
marker. The allowlist was deliberately not widened.

**(a) draft / protocol prose the relabel lane must now cure itself** (paper
lanes are closed):

1. `docs/paper/draft-v2-skeleton.md:156` — `common-time` and `physical common-time`
   — "It does not globally replay one physical common-time"
2. `docs/paper/draft-v2-skeleton.md:157` — `common-time` — "shift and has no
   proven conservatism for common-time motion."
3. `docs/paper/draft-v2-skeleton.md:396` — `common-time` — "This within-block
   construction is not a global common-time replay across blocks."
4. `docs/paper/draft-v2-skeleton.md:811` — `common-time` and `physical common-time`
   — "no proven conservatism for physical common-time motion."
5. `docs/paper/protocol/first-use-audit-ledger.md:137` — `common-time` and
   `physical common-time` — "…it is not a physical common-time replay."
6. `docs/paper/protocol/first-use-audit-ledger.md:138` — `common-time` —
   "…without claiming common-time conservatism."

**(b) something else — figure artwork source plus its committed output** (a
cure must edit the generator and regenerate the SVG so the pair stays in sync):

7. `docs/paper/figures/build_mechanism_figures.py:80` — `common-time` — inside
   the `t(s,30,392, …)` call: "A shared energy sign does not replay one physical
   time shift across blocks; no common-time conservatism is proven."
8. `docs/paper/figures/figA4_shared_signs.svg:18` — `common-time` — the same
   sentence as the rendered `<text x="30" y="392" …>` element.

All eight lines arrived with paper-L/paper-M; none is on a line this branch
wrote. The next seat cures them (marker banner or reworded denial) and re-runs
the census.
