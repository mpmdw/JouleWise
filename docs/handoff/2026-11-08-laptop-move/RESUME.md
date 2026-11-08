# Laptop-lead checkpoint: 2026-11-08, about 11:50 PST (Ed is moving the Air for a couple of days)

All work is on GitHub, and nothing that matters exists only on the Air. Authority lives in `RUN_STATE.md` on main, items 213-232. This file is the map for picking the work back up.

## 1. MBP (magistrate). Do not touch while a plan is armed
- **R1 has been ARMED since 01:17 PST 11-08** (item 227). Plan `align-r1-20261108T0917Z`, route `lane/2026-11-08-r1-arm-fixes` @ `20e9edbc4`, `window_max_s` 105,427 s, latest end Mon 11-09 06:39 PST. The expected finish is Sun evening.
- **After R1 closes, the magistrate follows item 222 (3) and runbook §4:**
  - restore network time;
  - read `r1_result.json`;
  - check the Automatic restore, KM003C capture and stray processes;
  - uninstall;
  - record, then mail Ed.
- **Then the R1→W1 chain:** `scripts/align_r1_to_w1_chain.py` on the v4 line (export → backfill-x-g → backfill-turn-counts → kit regen → derive-contrast → `--check`). The MBP does the close, finalize and push; the Air does the rest.

## 2. W1 integration onto `align/2026-11-08-v4-r11`
Current head: `03253edca` plus fixes in flight. The plan is in item 228, updated in 229.

| Item | Status |
|---|---|
| 1. R0 fill | merged |
| 2. R0-L3 (#699) | merged |
| 3. W1 blockers (U3 + battery, `w1-blockers-merged` @ 6d20e787a) | merged |
| 4. D/C/T series (`dct-series-merged` @ 25860dcaf, seed check MATCH) + R20 sentinels | merged |
| 5. Condition waits | OUT for W1. W1 uses today's cool-down; fixes are on `condition-waits-impl` @ 477f6f9e4 and need an Opus delta review |
| 6. Timing receipts (`perf/2026-11-08-timing-receipts` @ bcd4fd3c2) | cleared (Sol re-review ADMIT_WITH_FIXES: one test fixture). The Sonnet fixer merges it after the delta5 fixes |
| 7. Harvest off the MBP (R17) | merged build in progress (`align/2026-11-08-harvest-off-merged`, WIP backup `backup/wip-harvest-off-merged`). Then a Sol review |
| 8. Smoke kit (`align/2026-11-08-w1-smoke-merged` @ ed65d9094, WIP `backup/wip-w1-smoke-merged`) | the two Sol delta reviews HOLD (isolation, TOCTOU, deadline forgery, teardown). Fix in progress, then a delta review |
| 9. R14-R17 agreement docs | still to bring into the tree |

- **Delta5 review of 03253edca:** ADMIT_WITH_FIXES from both seats. Supplemental sentinels must count toward nothing; retry ids must match slots; a 23-member window must refuse. The Sonnet fixer has these.
- **Before W1 can register:**
  - integration done;
  - the full suite plus `JW_WP22_FULL=1`;
  - PREQUAL `--w1-next w1` green on the exact commit, pinned for BOTH the native smoke and W1;
  - the U3 bar exported and signed (runbook `docs/align/v4/W1-BLOCKERS-merged.md` §4; inputs drafted on `align/2026-11-08-u3-inputs-draft` @ 2688ba38c; the magistrate must first confirm that the 14 pilot bundle paths exist);
  - the battery policy signed;
  - the receipt regenerated;
  - the blind registration gate with Fable as final eyes;
  - the native smoke (≤45 min, isolated clone).

## 3. Block 5: RELEASED and UNSEALED (items 229, 231, 232)
- **Release check:** agree, exit 0 (main `02ef89f5c`, analysis `ab1e0098d`).
- **Results:** `docs/analysis/b5/RESULTS.md` on `analysis/2026-11-08-b5-results` @ `0b0658a20`.
  - Decode +146.63 J (decision interval 141.36-151.90).
  - Prefill +101.81 J (95.81-107.81).
  - Both direction_supported, claim ceiling L2.
- **Ed's ruling:** Block 5 goes in the paper as the instrument-validation section. It must still pass the Results cold gate before any rendered number is used.
- **Lessons forensics running:** `analysis/2026-11-08-b5-lessons` covers contention culprits, v4 calibration risk at Block 5's 45 % loss, between-window τ, the timing bound and comparator rules. Anything required before W1 registration gets integrated.
- **Prune** (Ed approved): an Opus delta check plus `docs/ops/PRUNE-EXECUTION.md` on `ops/2026-11-08-prune-execution`. Backups and tags come first. The magistrate runs the MBP steps only after R1 closes.

## 4. v4 analysis (B5-grade rigor; item 230 / R21 + A37)
- Sol primary engine: `align/2026-11-08-v4-analysis-engine-sol` @ c8da9ee40, with the R21 fixes. A37 (1 µs contiguity, overlaps snapped) still has to be applied to the engine.
- Opus independent recompute: `align/2026-11-08-v4-recompute-opus` @ c0d1efcae, digest `28db6c12…`. It runs about 2 min per full series.
- Next: the blinded comparator plus `release_v4.py` (2 > 1 > 0), then a synthetic full-series rehearsal. Rule: an empty family HOLDS.

## 5. v5
The design draft is at revision 7 on `align/2026-11-08-v5design-ruling` @ 4078c0850 (corrected power, prospective sizing rule). The round-7 Sol checks are pending or done on `-delta7-*`. Sign once both say SIGN.

## 6. Speed and anti-idle program (items 213-228)
- **R12 cadence:** in the registration.
- **R1 at the earliest t0:** done.
- **CI split (#685):** merged.
- **Nightly opt-in (#705):** passed review with a fix; merge once CI is green.
- **Readiness gate and guard replay:** reviewed. Each needs its listed fixes before it binds (R18/R19).
- **Air offload (compressed):** built (`ops/2026-11-08-air-offload-opus` @ 7e0c264e0, plus the Sol variant). Waiting on Ed's SSD choice.
- **Desk-parallel, kit batching and wake:** admitted, each pending a small rebase or split.
- **Toolbox:** `docs/perf/SPEED-TOOLBOX.md`.

## 7. Decisions pending with Ed
- **SSD:** on the Air with compressed offload (recommended), or permanently on the MBP (SSD-P1).
- **U3 bar:** sign it once it is exported after R1.
- **v5:** monitor spend cap and the other §7 decision items.

## 8. Resuming on the Air
1. `git -C ~/code/CapstoneProject/jw-wt/handoff fetch origin`.
2. Read RUN_STATE 213-232 and this file.
3. Agents are spawned per lane. Their briefs live in the review and branch docs above.
4. Sol wrapper: `/private/tmp/jwsol/squeeze/sol-fast.zsh`. It is wiped on reboot; rebuild it from `RUN_STATE` and the memory notes if needed.
5. Watchers must re-arm before going idle, and Ed must be pinged on any pending decision (memory: ping-on-decisions).

**Blinding is unchanged:** BYTES held-out, ALIGN v4, Block 6, and every night or restricted path stay sealed.
