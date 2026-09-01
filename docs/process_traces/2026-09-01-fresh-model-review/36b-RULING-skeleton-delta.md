# Ruling 36b — draft-v2 skeleton delta re-audit (luna max, report 36: SHOULD-FIX)

Magistrate ruling, 2026-09-01, on `feat/2026-09-01-skeleton` @ `cc52daab`. Delta seat: luna
(report `36-luna-delta-27-skeleton.md`); fixer was terra (report 27). Registration, survival
map (45 ranges cover frozen lines 1–672 exactly once), STOP_FILL census (50 placements / 33
rows, all with local omission text) and no-campaign-value check all PASS. Residuals are
pedagogy/replication only. This is the second fix round on the first-use/replication classes
→ cold-gate trigger; the cold seat's verdict is appended below.

## Dispositions

| Finding | Ruling |
|---|---|
| PED-FU-01 Student-t used at :128 before built at :257 | ACCEPTED. One-sentence gloss at :128 (a small-sample bell curve whose quantile widens the bracket when few captures exist), the full build stays at :257. |
| PED-FU-02 "reference-run trajectory excursion" / "issued repeatability bound" used at :132 before §4 | ACCEPTED. Define both inline in one sentence each at :132 (physical: how far the reference run's power trace strays from its own median; the bound the calibration issued for that stray). |
| PED-FU-03 "total standard error", "metrology scatter" at :498 | ACCEPTED. State the two component estimators and the exact combination (sum of variances → square root) before the direction test. |
| PED-R1-01 17-capture corpus constants not derivable | ACCEPTED WITH A BOUND. The 17 retained capture differences are diagnostic data from the retained (immutable, non-claim) corpus; print them as a table with the 99 % quantile rule and the rounding rule so 10.164834757777545 ms and 9.724 ms replay. They are NOT campaign result values; label the table "retained calibration corpus, diagnostic". The fixer must read the values from the corpus at the bench (state the file path in the report), never from memory. |
| PED-R2-01 t_{.975,1} = 12.706 and block-2 operands not printed | ACCEPTED. Print the critical value with its source (Student-t, 1 degree of freedom); mark q_2, ℓ_2 as authenticated fixture inputs with their fixture path. |
| PED-R6-01 direction test has no ten-block fixture | ACCEPTED as an ILLUSTRATIVE fixture, not data. Use the ten one-decimal deltas already ruled for the dependence sheet (R1–R8, `feat/2026-09-01-dependence`: `[5.0, 7.6, 5.5, 4.2, 4.7, 6.8, 5.5, 3.6, 3.9, 3.2]`, s = 1.4) so the two documents share one worked example; label "illustrative, not campaign data"; show the statistic and the Holm comparison to completion. |
| REG-COUNT-01 fixer said 36 exact placements; census says 38 | ACCEPTED as a record correction (38). |
| REG-HUNK-01 30 W clipping example unnamed in fixer table | ACCEPTED; no change to the draft, noted here. |

## Round-2 shape

Fixer: Sol high (distinct from terra/luna), WRITE_SCOPE `docs/paper/draft-v2-skeleton.md`,
`docs/paper/round7/survival-map.md`. Verify: `python3 -m unittest tests.test_paper_terms_lint`,
lexicon lint, the survival-map coverage one-liner from report 36 V3, the STOP_FILL census
one-liner from V4. Delta: Opus 5 pedagogy lens (a fourth family on this doc).

## Cold-gate verdict

(appended when the cold seat returns)
