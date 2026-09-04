# OPUS COUNTER-REVIEW — paper-e (gate ledger item 6)

Object: `/Users/edr/code/JouleWise-wt-paper-e`, `feat/2026-09-02-paper-e`. Head MOVED mid-review:
read at `6e874903`, re-verified at **`b5fd4ba2`** ("magistrate apex read cures"; only
`draft-v2-skeleton.md`, 6 insertions). Worktree clean; no writes. 02/03/03a/04/05 read.

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
......
Ran 6 tests in 1.542s

OK
```

## Findings

| # | Sev | Site | Evidence |
|---|---|---|---|
| B-1 | **BLOCKER** | `results-fill-registry.md:947-954` | The registry's own "Measured marker-row command" paragraph prints its grep and then states `Result: **34 [PENDING...] rows**. Including DS-01, DS-08a, and DS-34 gives the complete-family total of 37.` Running that exact command at `b5fd4ba2` returns **32** → complete-family total **35**. This diff's DG-071/DG-075 `[PENDING]`→`ISSUED` flip removed the two rows; the fill-checklist census was updated (37→35, re-derived live = 35) but the registry's own in-file census was not. The custody spine now contradicts the checklist by exactly the two rows this branch flipped, and the registry's documented command no longer reproduces its documented result. Two-number edit. **Missed by all priors:** 02's E7 re-derived only the *checklist* census ("37 − 2 = 35"); 04/05 inherited that scope. |
| S-1 | SHOULD-FIX | draft `:967-976` + fig5 upper row | The explanation contradicts the branch's own issued numbers. DG-070 phase = 0.121034145 s = **121.034145 ms**; DG-071 median record width = **120.9186 ms** — the median sampling record is *narrower* than the phase (issued quartiles q1 116.9720, q3 122.9227; the phase sits just above the median). Yet the prose offers the width IQR as evidence that a shorter record is merely "possible", and both `:974` and the figure's upper row explain two overlaps by records "wider than the phase" — an antecedent the cited run's own statistic falsifies for the typical record. A metrology reader who subtracts gets a *stronger* fact than the paper gives, and is then owed the real binding constraint: with the phase only ~0.1 % longer than the median record, full containment of a middle record is rare, so **alignment**, not width, denies the third overlap. Cure stays qualitative (no new number). **Inherited from ruling R2**, which nominated the IQR as the evidence — correcting it is a magistrate call, not a seat defect. |
| S-2 | SHOULD-FIX (residual — **closure does not hold**) | `round7/survival-map.md:275-277` | Still directs "render `DG-071` and `DG-075` with their exact registered omission sentences until their path- and SHA-pinned statistic artifacts issue." Those artifacts issued (PR #276); the draft now renders values. This is 02's N-1, ruled out of scope in 03a — but survival-map is a **live instruction doc** for future writer seats, so a seat following it reverts §6 to omission sentences. Close it or register it as carried debt. (`fill-rehearsal-2026-08-27.md:244,288` is stale the same way but is a dated record; leave.) |
| S-3 | SHOULD-FIX | draft `:963-966` | "...begins where the previous one ends **within its stated tolerance**" — the tolerance is never stated. The issuing artifact states it (`dg071-dg075-statistics.md` §Tiling: within **0.000001 s**; 100 of 405 boundaries nonzero, largest 0.0000004 s). Unreplicable as written, and the clause is not load-bearing: the inference rests entirely on the exact literal `interval_end_s == timestamp_s` refusal. Name the tolerance or delete the clause. |
| N-1 | NIT | draft `:961` | "the 405 differences between consecutive recorded timestamps" drops "**unique**" from the issued recipe (DG-075: "consecutive unique `timestamp_s` differences"). Numerically identical here (406→405); the printed replication recipe differs from the issued one. |
| N-2 | NIT | draft `:972` | "The 0.121-s phase duration is **close to** the issued … medians" — "close to" is an unbuilt criterion word doing technical work. Same root as S-1. |
| N-3 | NIT (out of §6 scope; queue paper-wide) | draft `:146,:217,:293`; ledger `:1632,:1669,:1680,:1747` | R4's one-name rule holds *inside* §6, but the paper still carries "**sampler record**" in §1/§3 and in four ledger glosses — including the `three-record minimum` gloss, whose first use is §1. Two names for one object survive across sections. |
| N-4 | NIT | draft `:983-984` | "37 of 50 … and the **remaining** 13 of 50" asserts exhaustiveness (no phase at 0, 1, or ≥4). Sound — DG-068=50, DG-076=37, DG-077=13 sum exactly and DG-069 `identifiable`=13 corroborates — but it is a desk inference across three rows. Worth a checklist note so a reissue of any one re-checks the sum. |

## Closures that HOLD (spot-re-verified)

- Every §6 numeric token still traces to DG-067..077 or the PR #276 artifact; both SHA-256 pins present in both rows and the checklist.
- **(d) vocabulary:** one verdict word — "not resolvable" at §3 `:307`, §4 `:764`, §6 `:935`; §6 glosses the record-support reason and `not_resolvable_sample_count` at first use and names §4's different reason in the same sentence (R1 met). "sampling record" consistent in §6; record support / overlap count / three-record minimum equated once at `:931-934` (R4 met in scope).
- **(c) diagram:** SVG labels extracted — both rows label R1/R2/R3, phase start/end edges, overlap segments, count box, decision, axis; lower row carries "prompt-processing interval (same width)", "narrower than phase", "record widths vary". Caption matches the drawing; R2's story is drawn as ruled. The residual objection is S-1, against the ruling, not the rendering.
- **(e)** checklist census `== 35` re-derived live = 35; figures-plan and figures/README three→four counts consistent. Only downstream trips are B-1 and S-2.
- Code claim verified independently: `joulewise/bundle_read.py:2828` raises `"power_trace.csv row {index} interval_end_s must equal timestamp_s"`, and `dg071-dg075-statistics.md:26` confirms the *producer* enforces it — §6's attribution to "the program that issued these statistics" is accurate.

## Verdict

**FIX FIRST** — B-1 is a two-number edit inside a file this diff already touched; S-1 needs a magistrate ruling on R2 before a seat is briefed.
