# Claims Status

**The single standing home for "what can we actually claim right now."**
Every scientific number the project can publish, is holding, or must not
repeat — with its exact validity state and blocker. Refresh this file
whenever claim-bearing state changes (a verdict, a mint, a merge in the
D-095 chain, an adjudication); quote verdicts as issued, never
reinterpreted. Companion docs: `RUN_STATE.md` (session pointer),
`WINDOW_STATUS.md` (machine state), `docs/decision_log.md` (policy).

Last updated: **2026-08-01** (post metrology window B; report:
`docs/run_reports/2026-08-01-metrology-window-b.md`).

---

## 1. VALID — minted, mainline, citable

| Claim | Value | Basis | Notes |
|---|---|---|---|
| **Operative decode detection floor (Qwen2.5-1.5B MLX)** | **7.377086 J** | Mint #1 `df-ph-decode-floor-mint1.json`, mainline (PR #88, D-088 conditioned license) | Cell composes a10's absolute component with window C's comparative; gate is the **max, never the sum** (W3 rule 8, D-084). Validator clean. |
| Absolute floor components (a10, LABELLED) | 3.823787 J prefill / 3.592138 J decode | Window a10, verdict PASSED | Components **in isolation**, incl. 0.652272 J drift allowance. 3.592138 is NOT the operative decode floor (D-084). |
| Comparative floor component (window C) | 7.377086 J decode | Window C, verdict PASSED (first passing comparative window) | Published LABELLED per D-078 cl.11. |

**Standing measurement fact (D-078 cl.11, Ed-ratified):** the instrument
is attribution-limited (~1 J), not noise-limited (~0.3 J). Floors
publish LABELLED with the widened number; the effective clearable
effect for phase contrasts is floor + claim-side bound ≈ 5 J. No
instrument-tightening program.

## 2. EVIDENCE-BEARING — collected and verdict-PASSED, awaiting a specific gate

| Candidate claim | Value (prose-only until gated) | Window / verdict | Blocker |
|---|---|---|---|
| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | `MINT-GENERALIZE-01`: D-088 no-mint-from-duplicate-bearing-corpus condition until the cooldown-join gauntlet fully closes (commit 3 outstanding). |
| **1.5B-vs-7B decode contrast** (demonstration study #1) | 7B−1.5B per-block 146.730349 J, σ 0.241 J, n=10 ABBA blocks (~600× block scatter, ~10–20× the floors) | `window_contrast_20260730`, **PASSED** | The D-095 chain, in order: gauntlet commit 3 (D-097) → MANIFEST-CONTRAST v3 → multi-cell mint → gated claim. Diagnostic is quotable as prose, never as a gated claim. |

## 3. COLLECTED — verdict FAILED as-issued; consumption blocked on the machinery adjudication

Both metrology windows closed as salvage under the third-failure rule
and their whole-window verdicts **FAILED with distinct condition sets**.
The verdicts stand; the open question is whether the verdict machinery
mis-rules salvage-shaped windows (dangling quarantined-without-
replacement occurrences; deviation post-cal selection; multi-chain
manifest/membership resolution). Adjudication = independent audit →
cold gate for any proposed override. **No number below may be consumed
for any claim until that adjudication rules — and the bundles
themselves are banked, intact, and not invalidated.**

| Paper claim | Campaign | Collected | Verdict state |
|---|---|---|---|
| **C1 — linearity** | `linearity_ramp` | **40/40** (window A) | Window A verdict FAILED (machinery) |
| **C2 — null ladder** | `null_ladder` | o0128 + o0512 **complete** (window B); o2048 → window C | Window B verdict FAILED (machinery) |
| **C3 — micro-delta** | `micro_delta` | not collected | Plan is draft-pending-slope by design |
| **C4 — additivity** | `additivity_shapes` | **23/24 single-root** (window B; p2048o0128-r08 outstanding) + 21/24 corroborating (window A) | Window B verdict FAILED (machinery) |
| **C5 — long holds** | `long_holds` | not collected → window C | — |

## 4. Standing gates on EVERY claim consumption

1. **D-088 cl.3(c)** three-check bench scan (no unlicensed declared
   duplicates, no zero-candidate declarations, no failed/incomplete-
   existing encounters) — binds until the cooldown-join gauntlet closes.
2. **D-093** raw-vs-validated supersession-record scan — any divergence
   refuses consumption.
3. Verdicts consumed as issued; overrides only via the cold-gate path
   with written dissent Ed sees.

## 5. DO NOT QUOTE — retired, void, or wrong-as-stated

- **3.17 / 2.94 J** floors — pre-allowance attribution-width
  diagnostics only (D-079 cl.5).
- **3.592138 J as "the decode floor"** — it is the isolated absolute
  component; the operative floor is 7.377086 J (D-084).
- **4.923 J item / 24.62 J suite** comparative floors — Ventura
  screensaver contamination artifacts (2026-07-17 campaign).
- Old window B (`04_phase_prefill_abba`) figures — verdict FAILED
  (`instrument_calibration_mismatch`, GPU DVFM ramp aliasing), corpus
  preserved but not claim-bearing.
- All pre-repair (pre-D-078) powermetrics corpora for claim use —
  time-anchor defect (D-078 soundness gate).
- Window A/B metrology numbers as claims — see §3 (verdicts FAILED,
  adjudication pending).

## 6. Instrument findings queued for the paper (not claims yet)

- **Clock-anchor knife-edge** (2026-08-01 Sol consult, accepted): at
  197 s capture length the native-second intersection margin is ~±1 ms
  and the unmodeled wall/monotonic rate (~−12 ppm ≈ 2.3 ms/capture)
  exceeds it; pass/fail is quantization-phase luck. Desk item:
  rate-aware anchor design; directly publishable as a metrology
  limitation/finding.
- **Quiet-state definition**: validated windows now include suspended
  cloud sync (bird-SIGSTOP protocol) — claims describe that controlled
  state, not an arbitrary unattended Mac.
- **Operator-session streaming hazard**: the operating session's own
  output streaming can fail a member's idle admission (window B
  failure #3) — a reproducible environmental-validity observation.
