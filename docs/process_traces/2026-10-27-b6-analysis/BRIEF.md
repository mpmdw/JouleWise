BRIDGE_TASK_V1
{"TASK_SHAPE": "autonomous",
 "GENRE": "implementation",
 "ROLE": "B6-AN-1: build the block-6 analysis driver (registration §9-§13) on synthetic data",
 "OBJECTIVE": "Replace the stub joulewise/b6/analysis_lane.py with a block-6 analysis driver that runs block 5's registered analysis per counting session, pairs GAMMA by round, and produces the between-session summary, side-by-side table, replication word and flagged-inclusive line, tested end to end on synthetic fixtures, ready for executing review.",
 "AUTHORITY": [
   "docs/registrations/block6_replication_DRAFT.md (REGISTERED 2026-10-17; sections 4, 6.2, 8, 9, 10, 11, 12, 13, 14 and 17; never edited by this seat)",
   "configs/campaigns/v5_claim_25g83/analysis_plan_block5.md (sealed; the arithmetic block 6 reuses unchanged)",
   "report/2026-10-22-blind-dry-run-scout:.codex-report/BLIND-DRY-RUN-SCOUT.md section 4 (the prerequisite table) and section 5",
   "RUN_STATE.md items 53, 59 and 77; directive issue #587",
   "this brief"],
 "WRITE_SCOPE": [
   "joulewise/b6/analysis_lane.py",
   "joulewise/b6/analysis/**",
   "scripts/b6_analyze.py",
   "tests/b6/analysis/**",
   "configs/b6/analysis/**",
   ".codex-report/B6-AN-1.md"],
 "BASE_HEAD": "991358f73f6d509c8a1ace3e812ff4e81a3983b2 (work/2026-10-23-by-slots-draft) merged with 0576a734df9ecf8cc155af4c4a8c8dfff30e4a37 (lane/2026-10-20-l9-ruling-build)",
 "BASELINE_MANIFEST": "FILL_AT_LAUNCH",
 "BASELINE_DIGEST": "FILL_AT_LAUNCH",
 "ACCEPTANCE": [
   "A1: counting comes from the loop's acceptance (attempts.jsonl / the loop record), not from a block-5-style exclusions.json claim_usable; a synthetic r2-gamma-shaped session with claim_usable:false from neg8.midpoint_lost_primary counts (RUN_STATE item 53)",
   "A2: GAMMA pairing by registered round, never by value: G r1 -> A r1/B r1; G r2 -> A r3/B r2; G r3 -> A r3/B r3 (registration §6.2; scout §4)",
   "A3: block 5's plan steps run per counting session with no pooling across sessions; §10 prints, per quantity, each session's value, their mean and sample SD (block 5 plus the three block-6 counting sessions), with no ratio and no pooled interval",
   "A4: §11.2's word 'replicated' only when every counting GAMMA session's outcome word and sign of dbar match block 5's; block-5 not_estimable permits no such word",
   "A5: §11.4's flagged-inclusive line indexes every collected session, counting or not (alpha r2 included), under §11.4's admission rules",
   "A6: every public byte is structure only (§12.1): no energy, power, phase duration, floor, ratio, mean, dbar, sign or outcome word in stdout, stderr, logs or unrestricted files; restricted outputs content-addressed",
   "A7: an end-to-end run on reduced-size synthetic block-6 sessions (all nine counting plus alpha r2) through the real L9 programs passes; full-size synthetic runs are §13's requirement and are listed as owed, not skipped silently",
   "A8: no file outside WRITE_SCOPE changed"],
 "VERIFICATION": [
   "JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b6/analysis -t .",
   "git diff --stat <start>..HEAD shows only WRITE_SCOPE paths plus the base merge"],
 "EARLY_RETURN": ["NEEDS_SCOPE", "NEEDS_RULING"],
 "OUTPUT_PROTOCOL": "bridge-report/v1"}
END_BRIDGE_TASK_V1

# B6-AN-1 brief: the block-6 analysis driver

Written 2026-10-27 by a Claude Code session for Ed, under directive #587 item 3 ("build the block-6 analysis driver
now, in the cloud, on synthetic data"). Effort: xhigh (multi-component, registration-bound).

## Why

Block 6 closed on 2026-10-21 with 9 of 9 sessions counting (RUN_STATE item 59). Its analysis driver is a 16-line
stub (`AnalysisLane.precision_reached` returns `None`), identical on every block-6 lane. Ed wants block 5 and
block 6 results front to back as soon as possible. Block 6's numbers can only be released after block 5's release
(registration §12.3 item 2), and they use L9 at its release tag (§13). Building the driver now, while L9 is
finished (seat L9-2, `lane/2026-10-27-l9-2`), lets block 6's blind dry run follow block 5's release without a gap.

## Start

1. Seat setup: clone `mpmdw/JouleWise-data`, `bash tools/cloud/seat_setup.sh <checkout>`, `source /tmp/jw-seat.env`.
2. Your checkout starts at `work/2026-10-23-by-slots-draft` (991358f73: the latest block-6 code line, including
   #573's block-6 fixes). Merge `lane/2026-10-20-l9-ruling-build` at 0576a734d into it (L9's `joulewise/b5_analysis/`).
   If that merge conflicts outside WRITE_SCOPE in anything but trivial bookkeeping, stop and return NEEDS_SCOPE with
   the conflict list. Push only to `lane/2026-10-27-b6-analysis`.
3. Read the AUTHORITY list in order. The scout report's §4 table is the work list. Of its rows:
   - **Build:** the item-53 counting consumer (A1), the pairing (A2), the per-session run of block 5's steps (A3),
     the between-session summary, side-by-side table, replication word and flagged-inclusive line (A3 to A5), and
     the restricted-output discipline (A6).
   - **Code only, values later:** S-9 (`P* = F_min / (4 × T_phase)` with the registered F_min = 1.9 J and S-11),
     S-11 (longest non-claim smoke target-phase duration per pack and phase, read from smoke records),
     S-15 (whole-machine phase energy, the block-5 definition carried over) and S-16 (replay counts of new or
     changed §8 rules on block 5's usable sessions). Write the code that computes each one from its registered
     source. Values are filled by automation on the Mac, never by you.
   - **Not yours:** the independent recompute's block-6 adaptation. It must share no code with L9 or this driver,
     so a different seat builds it. Say what interface it needs in your report.

## Rules

- Synthetic data only. Never open a real block-5 or block-6 archive, export, `derived/` file or key directory.
- No change to registered arithmetic, exclusion levels, blinding factors or any sealed file. The driver calls L9's
  programs. It does not re-implement them.
- L9 is being changed in parallel by seat L9-2. Depend on L9's public entry points (`joulewise/b5_analysis/steps.py`,
  `dry_run.py`); record in your report which ones and at which L9 commit.
- Never write fix/fixes/close/resolve immediately before "#<number>" in a commit message or report. No model
  identifiers in commits or reports. No force push, no PR, no merge to main.
- Long runs start detached with durable logs; push `.codex-report/B6-AN-1.md` after each milestone.

## Report

`.codex-report/B6-AN-1.md` on `lane/2026-10-27-b6-analysis`: SUMMARY, the acceptance rows A1 to A8 with evidence,
FILES CHANGED, DECISIONS I MADE, OPEN ISSUES (including §13's owed full-size run and the two cold passes),
NEEDS_RULING.
