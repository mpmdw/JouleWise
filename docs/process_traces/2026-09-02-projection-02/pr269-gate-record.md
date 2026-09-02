### Gate record — V5-PREFILL-REALIZED-PROJECTION-02 (D-118 full gate, 141a P-8)

Commits over `origin/main` @ `c5fa8a49`:
- `717b1ddb` Sol xhigh implementation (seat 145), rulings 141a P-1..P-10
- `01a94592` bench cure of Opus contract refuter 151 (F1 hash-binding test, F3/F4/F7 nits)
- `d7bf2ffa` Sol fix round 2 (seat 155) — terra 149 EXE-01 + EXE-03 regressions
- `ae7dd3d8` bench cure of luna delta re-audit 157 (F1 receipt digest, F2 arm mapper)

| Seat | Lens | Findings | Disposition |
|---|---|---|---|
| 149 terra (Sol) | execution / mutation | EXE-01, EXE-02, EXE-03 (all blocker) | all CURED — tests at `test_identity_pins.py:1422`, `:1569`, `:1507`; mutants executed dead (155 V2/V3, 157 V2–V4). Six ruled P-10 mutants killed (149 V1–V6). |
| 150 luna (Sol) | causality | F1 post-arm realization gap (blocker); `transformers_version` filter | F1 RULED OUT as blocker → ruling 150a R-150-1; filter RULED unchanged → R-150-4. |
| 151 Opus 5 | contract | F1 should-fix + F2–F7 nits | F1 CURED (`01a94592`); F3/F4/F7 CURED; F6 CURED (`d7bf2ffa`); F2/F5 accepted, no action. |
| 155 Sol | fix round 2 | none (report `clean`) | Both new tests independently re-verified by 157. |
| 157 luna (Sol) | delta re-audit | F1, F2 (should-fix) | Both CURED in `ae7dd3d8`. |
| 159 Opus 5 | contract + process record (near-final) | CR-01 should-fix; CR-02 should-fix; CR-03 note | CR-01 = P-5's `status: "PASS"` unpinned (mutant survives 87 tests) → 1-line bench cure; CR-02 = no contract prose for the new evidence row → magistrate-owned (P-9 barred the implementer from docs). |

**Written dissent (ruling 150a, R-150-1).** luna 150 labelled F1 — no realization
recheck between the arm receipt and collection — a BLOCKER. The magistrate
DOWNGRADED it to SHOULD-FIX because the gap is pre-existing and not specific to
prompt realization: `_replay_consumed_arm` replays the whole arm receipt, so every
identity unit has the identical post-arm window, and projection-02 neither opened
nor widened it. Follow-up row: **`V5-LAUNCH-REALIZATION-RECHECK-01`** (agent lane,
hard-start dependency: projection-02 merged), with luna's regression adopted
verbatim. Fence R-150-3: no `_v5` night may be armed for CLAIM use until that row
lands; rehearsal and DIAGNOSTIC_NO_PACK nights are unaffected.

**Tests at head** (`ae7dd3d8`, named modules only): `tests.test_identity_pins
tests.test_mlx_runtime tests.test_arm_readiness_integration` → 87 tests, OK
(skipped=5). Wider modules at the last source-changing commit: 183 tests OK
(157 V9), 219 tests OK (149 V7–V11).

**Open, post-merge, by ruling:** (1) 141a P-8 — magistrate freezes and arms a
THROWAWAY generated `_v5` pack against the real Qwen tokenizers before any night
uses it (no real model was loaded by any seat); (2) D-121 terminal review must be
re-run over `d7bf2ffa`+`ae7dd3d8`; (3) ruling 150a R-150-2 follow-up row.
