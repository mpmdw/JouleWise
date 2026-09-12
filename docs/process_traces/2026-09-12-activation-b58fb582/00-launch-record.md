# 00 — Launch record, headless activation `b58fb582` (2026-09-12 00:40:45 PDT)

Activation `b58fb582-a833-457f-a611-d3daece96816`, attempt 25, claude pid
94352, spawned by the watchdog at 00:40:45 PDT after it held `HOLD_CENSUS`
through the rehearsal-20260912 night driver (pid 93102) and the night
courier it launched (pid 93183, `claude -p`, 00:30:17–~00:47). Heartbeat
written 00:40:56 (rewritten with the claude pid at 00:44:51). Launch email
`1a09492c4ac317b0` on thread `1a0800cdb282c3f1` at 00:44 PDT; `notice.ack`
written after Gmail accepted it. Pending notice acknowledged:
`transition-103-hold_census` (00:30:42, "production census non-empty inside
plan span") — the hit was the night's own driver, then its courier.

## State found

- Origin main `101eeb07` (two courier commits on H′ `a7d1eb88`); canonical
  `/Users/edr/code/JouleWise` fenced at `1d4045b4`, untouched.
- rehearsal-20260912 FIRED, HARVESTED and RETIRED by the courier itself
  (`docs/process_traces/2026-09-12-courier-rehearsal-20260912/01`, `02`):
  gate `REHEARSAL_ONLY`, stub exit 0, receipt C1/C3/C4/C5 PASS with measured
  keys, C2 `NOT_APPLICABLE`, `launchd.night.err` empty; ruling 06 C-7 MET →
  NIGHT-REHEARSAL-01 item 6 MET; C-8 on disk (agents uninstalled 00:35:23,
  stub worktree removed, plan root moved to
  `/Users/edr/night-archive/rehearsal-20260912-plan-root-retired-1789198658`).
  `launchctl list` shows only `com.joulewise.magistrate`;
  `find ~/night-custody -maxdepth 2 -name night_plan.json` empty; watchdog
  `fenced_checkouts` = canonical only. NOTHING ARMED.
- No stand-down request, no `STOP`, no open owner-authored `directive`
  issue (`gh issue list … --label directive --state open --author mpmdw` → `[]`).
- Notice thread `1a0800cdb282c3f1` (METADATA_ONLY): last inbound from Ed is
  2026-09-10 23:05Z (`1a08d917705d98e9`, the "Yes to all four" message); no
  NO since. Ed's non-veto of the equivalence night therefore stands.
- Bookkeeping worktree `/Users/edr/code/JouleWise-wt-bk-b58fb582`, branch
  `bookkeeping/2026-09-12-activation-b58fb582` from `101eeb07`.

## Work this activation resumes (courier's 00:40 durable UPDATE)

Equivalence-night install inside 03:00–06:30 PDT 2026-09-12 for
t0 2026-09-13 02:56 PDT, per `docs/phase_2/derivation_night_runbook.md`
(revision 7 at `101eeb07`; the durable pointer's "rev 5" is the revision
number when the pointer was written) §0–§1.5, NIGHT_HANDBACK email-then-arm,
with the stage-1 email (acceptance item 4) on the notice thread BEFORE the
plan is published.

## Decisions taken at this activation (recorded, not ruled)

1. **H composition.** Runbook §0.1 requires H to carry the handback rewrite
   and the production inventory row; §0.5 requires the pre-registration's
   five commit-time fields filled inside H. At `101eeb07` all five were still
   placeholders (`[DD]`, `[MLX_VERSION]`, `[SEQ]`, `[DIGEST]`,
   `[CHAIN_SHA256]`), so H = one docs+config commit: handback §Purpose /
   §Where / §Next lane rewritten for the night; inventory row
   `JouleWise-measurement-20260913-derivation` appended; fills
   DD=10 (file's first commit `64d1d6d3`, 2026-09-10), MLX 0.31.2
   (`env/mac-measurement-lock.txt` pin; record 134 observed it live),
   SEQ 76 / DIGEST `08456d50…94d7` (`configs/calibration/calibration_ledger_head.json`),
   CHAIN_SHA256 `b8bf5b0a…ac8cf` (`shasum -a 256` of the tracked chain at
   `101eeb07`). Only the sealed block was edited; the "Fields filled at
   commit" gloss still names the placeholders. Landed as a direct
   bookkeeping commit to main per file 11 §"Exact activation Git sequence"
   (the supplied convention), after focused tests
   (`test_night_gate`, `test_issue_calibration_acceptance_generation`,
   `test_rehearse_t0_unattended`, `test_gen_derivation_night`,
   `test_docs_freshness`, `test_magistrate_watchdog`, `test_gen_state`:
   all OK), `gen_state.py --check` rc 0, `git diff --check` clean, and an
   Opus dictated-fills verification (record 01). CI on main at H is a
   precondition of the arm.
2. **`EVIDENCE_ROOT_ID`** = `evidence-d079-epoch-25g83-derivation-n1-20260913`.
   The runbook says it has no derivable default and must come from "the
   record that registers it"; no prior record registers one for this lane
   (searched `docs/`, `configs/`, `scripts/`). The form follows runbook 68's
   G2-a convention `evidence-<window id>`. THIS record and the arm record
   register it. The ledger stores it as a session field; nothing resolves it
   to a path.
3. **Frozen calibration plan** = committed bytes of
   `configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json`
   (`plan_id` `plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3`),
   copied to `<night root>/calibration_plan.json`. Basis: runbook §0.2's
   variable table ("a `calibration_plan.json` from a frozen campaign pack in
   the clone", citing `window_runbook.md`'s `FROZEN_PLAN` example in the same
   pack lineage, of which v3 is the latest committed generation);
   `calibration_ledger.validate_frozen_reservation_plan` and the chain use
   it only as an identity binding (`plan_id` + SHA-256 recorded on the
   session); the derivation-only capture writer takes no plan. The v5 packs
   commit no `calibration_plan.json`.
4. Time budget: install must begin by 06:05 PDT (runbook §1.3's recommended
   cutoff); if it cannot, record the miss and take the next 03:00–06:30
   span — never arm off-convention.
