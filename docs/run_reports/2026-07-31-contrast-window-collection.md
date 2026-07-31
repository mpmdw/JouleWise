# 2026-07-31 — Contrast window `window_contrast_20260730`: collection, recovery, and PASSED verdict

Authored from the window's §12 close-out record
(`~/JouleWise-window-custody/window_contrast_20260730/close-out.md`), which is
the ONE home for these facts. Nothing here is sourced from anywhere else.

## What ran

`window_contrast_20260730` — the `splitwise_decode_v1` contrast collection,
under the frozen plan `splitwise-decode-v1-m3max-qwen25-1p5b-vs-7b`
(magistrate-ratified 2026-07-30 ~14:50). Under the metrology pivot this is
**demonstration study #1**.

- **Arms:** A = Qwen2.5-1.5B-Instruct-4bit (revision `8b403126`);
  B = Qwen2.5-7B-Instruct-4bit (revision `c26a38f6`). n = 10 ABBA blocks.
- **Repo state:** collection ran under commit `16c7af0` (the main checkout
  detached at the `impl/mint-tool` head per the pre-window checkpoint).
- **Campaign policy sha256:**
  `b0d7b228b88bea717aa9269c103aca760cc36cf05239e0f86c235b4b29665efd`.
- **Power:** AC, 140 W Apple charger, Ed-connected; §5A done 19:02 PT.

## Chain

- Original launch **2026-07-31T04:07Z**, chain sha `2a334f64…09d5f`, §5B screen
  passed.
- `measurement_complete` **2026-07-31T08:25:40Z**, reached via the **round-3
  continuation** (continuation sha `93a6720bdb902b82…`, §10 shape — it pins the
  window's pre-calibration and re-runs the §5B screen).

## Calibrations and the bracket

- **Pre:** `20260730T210703-f76b5771`, `b_fiducial`
  **0.026131301462788137** s, §5B screen PASSED, single attempt.
- **Post:** `20260731T012210-374020b6`, `b_fiducial`
  **0.024850427856341006** s, single attempt, no retries.
- **Bracket drift 0.0012808736064471304 s** against the derived screen value
  **0.010818 s** — PASS clean. This is the **third consecutive passing window
  bracket**, after window C (1.279 ms) and window D (0.484 ms).

## Members

- **NEG-8 bound corpus:** 12/12 usable (`neg8-refcorpus-r01..r12`), collected
  and the dual-family bound minted **in-window, before the failures** (first
  chain segment); consumed by the verdict.
- **References:** start triplet r1–r3, midpoint, end triplet r1–r3 — **7/7
  usable** at final state (r1 via the round-3 replacement; see deviations).
- **Science members:** 40 ABBA (`swdec-contrast-b01..b10` × `a1`/`b1`/`b2`/`a2`,
  fixed A/B/B/A per Q5) — **40/40 usable, zero science-member failures**.

## Verdict

**Whole-window verdict: PASSED** — row **58** of the claim log.

- `evaluation_basis` sha256
  `1e08e8eff4ede001a6d68525a7748bbf66f81278a3b963b9b24e7405d105d147`
- 47 bundle ids; **1 occurrence supersession consumed**; no exclusions, no
  waivers.
- `neg8_bracket` passed; CPU admission admitted throughout; adapter wattage
  continuity stable (140 W PD charger, AC, **188 observations, 0 unknown**).

## Deviations and recovery (§10-sanctioned, evidence preserved)

1. **Start-triplet r1 CPU admission failure, ×2 attempts, ~04:52Z**
   (`cpu_busy_ratio_p95` **0.726** against the 0.5 gate). The cause was
   initially **misattributed to a Time Machine backup**. The slot was
   quarantined (`…045749Z`) and continuation #1 launched after TM-only
   verification.
2. **Same-signature failure ~05:13Z.** An **XProtect Remediator sweep was
   DIRECTLY OBSERVED active** — `XProtectRemediatorPirrit` at **941 CPU ms/s**
   in a `powermetrics` tasks sample, with modules running sequentially until
   **05:31Z / 22:31 PT**. That was the true cause of *both* rounds: the round-2
   relaunch was an **operator error** — Time Machine had been checked, overall
   CPU quiet had not. Slot quarantined (`…051547Z`).

   The **standing escalation trigger fired** (two consecutive same-signature
   failures). A bounded **Sol xhigh consult** was convened (thread
   `019fb69a-7692`), which ruled round 3 conditionally sound, banked the
   **one-invocation supersession contract**, and verified the continuation
   chain shape.

   A **second observed intruder** — `corespotlightd` at **624 CPU ms/s**,
   Spotlight indexing the fresh bundles — was waited out. Round 3 launched
   **06:05Z (23:05 PT)** only after: the full remediator sweep completed, **8
   consecutive daemon-quiet minutes past the Time Machine hour boundary**, and
   a clean final tasks sample.

   **Round 3 ran the entire window without a single further admission event.**

The **supersession was recorded ONCE, post-window** (entry sha `92a8d378…`),
with the round-3 occurrence selected and both failed occurrences superseded,
their manifests hash-named — per the consult-verified recorder contract.

The window used **2 of its 3 permitted failures**, both on one reference slot;
the **third-failure salvage rule was never invoked**.

## Custody

**Backup ran §11 order, BEFORE any consumption:** claim root 49 bundles + bound
root 13 bundles to iCloud `JouleWise-backup/window_contrast_20260730` (and
`_bound`). Both exit 0; sources unchanged.

## No floor extraction — by design

This is a **science window, not a calibration window**, so there is no floor
extraction. The paper's demonstration numbers come from bundle summaries plus
the **two existing floor artifacts**: the 1.5B operative decode floor
**7.377086 J** (mint #1, mainline) and the 7B floors, absolute **6.294380** /
comparative **13.998037** J (prose-only, pending `MINT-GENERALIZE-01`).

## Diagnostics vs gated claims — the distinction that governs this window

The numbers below are **bundle-summary DIAGNOSTICS: prose, not gated claims.**

- **A-arm (1.5B)** idle-subtracted decode energy mean **51.961375 J**
  (n = 20, σ = 0.266).
- **B-arm (7B)** mean **198.691724 J** (n = 20, σ = 0.266).
- **Per-block ABBA contrast (7B − 1.5B)** mean **146.730349 J**, σ = 0.241,
  range **[146.385, 147.093]**, n = 10 blocks.

The effect is **~600× the block-to-block scatter** and **~10–20× the operative
floors** — the resolvable-contrast demonstration the metrology paper's claims
table anticipates.

**The GATED contrast claim remains BLOCKED** on the `MANIFEST-CONTRAST` desk
work, per pre-registration §5: this window is **evidence-bearing now,
claim-bearing later**, and there is **never** post-hoc promotion. Quoting the
diagnostics above as a claim would be exactly the promotion the pre-registration
forbids.

## Status and the one open operator action

- **Collection COMPLETE, verdict PASSED.** The window is evidence-bearing now
  and becomes claim-bearing for the contrast once `MANIFEST-CONTRAST` lands.
- **Network time:** Ed disabled it 2026-07-30 19:02:38 PT (§5A) and it is
  **NOT YET RESTORED**. Ed restores with
  `sudo systemsetup -setusingnetworktime on`.

## Process Trace

- Active stop card at start: none
- Skills/playbooks used: window runbook §5A/§5B/§10/§11/§12; standing
  escalation trigger (rule 11)
- Subagents / delegated sessions:
  - role/lens: bounded escalation consult — round-3 disposition, supersession
    recorder contract, continuation chain shape
  - model: Sol, xhigh
  - thread: `019fb69a-7692`
  - output: consumed live by the solo window operator at a stage boundary
- Councils: recorded as C-039 addendum II (ii) in `docs/council_log.md`
- Worktrees: none (main checkout detached at `16c7af0` for the collection)
