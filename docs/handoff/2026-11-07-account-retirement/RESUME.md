# Resume: lead state at account retirement (2026-11-07, about 17:00 PST)

Written by the laptop lead (Opus 5.5, session 1544c617) before Ed retired this Claude account. A new lead session should read this, then `RUN_STATE.md` items 191-201 on main, then the memory index (`~/.claude/projects/-Users-edr-code-CapstoneProject-JouleWise/memory/MEMORY.md`, which stays on this Mac).

## Standing rules (from Ed; details are in the memory files)
- **Blinding:** never read `/Users/edr/jw-b5-*`, `/Users/edr/night-*`, night-custody, night-archive or any `restricted/`. Allowed:
  - dry-run `steps.log`, `start`, `end` and `exit`;
  - existence tests;
  - the release `verdict.json`, read through a float-masking printer;
  - structure-only probes you have read before running. These print counts, enum words and key names and refuse decimals.
- **Who decides what:** the lead owns preregistration rulings: blind, logged in `docs/analysis/b5/DEVIATION-LOG.md`, Ed told after. The magistrate on the MBP owns measurement runs; the lead delivers kits through RUN_STATE items. The lead merges once CI is green and the chosen reviews pass. PRs from untrusted audits stay open.
- **Working conventions:**
  - Worktrees only under `/Users/edr/code/CapstoneProject/jw-wt/`; the canonical clone is `jw-wt/handoff`.
  - Use `/usr/bin/grep`; plain `grep` is a broken shell wrapper.
  - TMPDIR goes under `/private/tmp/...`.
  - Git identity: `-c user.name=mpmdw -c user.email=edr@Edrs-MacBook-Air.local`.
- **Priority** (Ed, 11-07): ALIGN (SHADE-Arena) research first. The Flash-Next port's live work waits for the SSD enclosure (delayed to Sunday 11-08, possibly Tuesday).

## Block 5 analysis: one defect from release
- **r3:** `b5/analysis-r3` = `68e47e1f2` (PR #693). Its real dry run (dry-l) took 1 h 40 min; dry-k took about 37 h. The release check (`scripts/release_b5.py`) held on exactly one cause, D5, which covers the two GAMMA d117 contrasts (108 rows). Every other family agrees.
- **D5 root cause (found blind 11-07):** `joulewise/analysis_engine/inputs.py` `_order_member_ids(..., campaign_log=True)` counts the GAMMA campaign log's campaign-level evaluation row, whose `bundle_ids` lists every bundle, as executed members. Every calibration bundle therefore appears twice, so `component_evidence_root_disagreement` ("does not bind every calibration bundle exactly once") leaves all four GAMMA floor cells unbound. The evidence is intact: hashes, order manifest and A/B/B/A order all pass. Probes are in `tools/` here.
- **In flight:** an r4 PR into main titled "b5 analysis r4: L9 campaign-log member parse (D5 cause), DLE-4".
- **Next steps:**
  1. Run the executing review and the cold Fable pass.
  2. Merge, then tag `b5/analysis-r4`.
  3. Run `tools/launch_b5_dry_run.zsh <sha>` with `RUN=m TAG=r4`.
  4. Run the release check: `scripts/release_b5.py --custody /Users/edr/jw-b5-custody/dry-m --window-index configs/analysis/b5/analysed_windows.json --pinned-commit <sha> --restricted-out /Users/edr/jw-b5-custody/release-check-drym-<ts> --workers 6`. Read only the exit code: 0 agree, 1 hold, 2 refusal.
  5. If it exits 0, ask Ed for the unseal OK. Nothing is unsealed without it.
- **Later:**
  - DLE-2 items before Block 6 (seven uncovered families).
  - Speed backlog: `sol/burn-s8` next. See `docs/run_reports/2026-11-07-b5-robust-fullchain.md`.

## ALIGN v4 (measurement Mac)
- **R0:** re-run 8 launches at or after 17:15 PST 11-07 (RUN_STATE 201), using the new SMC classifier (#692, merged into `lane/2026-11-05-align-pilot10-benign` as `5f817856b`). The OS quieting is done: Spotlight and the Photos agents are off. The softwareupdated scan is still on (it does not persist on macOS 26.6.2); runs are timed after the scans at about 05:09, 11:09, 17:09 and 23:09.
- **PR #694**, the R0 guard background sampler, is required before W1. It is a draft, CI-green, with every gate row filled. **Merge it into pilot10-benign after R0 re-run 8 exits**, then merge pilot10-benign into the R1 lane.
- **R1 lane:** `lane/2026-11-06-v4-r1-integrated` @ `e901eb2a4`. Rounds 6-9 are integrated and reviewed, and it carries the WP18 fixtures (`aaee4b2d2`) and #692.
  - The kit (`scripts/align_v4_kit.py --check`) blocks only on `R0.reasoning_effort` and on R1 outputs (`B_D`, `I_D`, `T_dead`, `thermal_policy`).
  - Before R1 arms, the slow-pick rule (#692 D5) must be chosen from re-run 8's settled capture (LEAD-RULINGS-2 Round 9).
  - The R1 night's worst case is 56,207 s with no redo, or 61,607 s with one batch-window wait. Use these for the R1 plan's `window_max_s`.
  - Next: an R1 kit delivery as a RUN_STATE item after R0. Before any W1 arm, the protocol's blind Fable + Opus gate is owed; the 11-07 research-audit workflow ran a version of it (see below).
- **Open lead call after the R1 night:** the ruling 1(e) fallback. Ruling 1(f) will likely refuse W1 at about 20 tok/s with a G0 cap of 600-1,200 s. The research-audit track `w1-budget-fallback` prepares the decision procedure.

## Flash-Next port (qwen4_exp)
- The bf16 quality reference (L3) exists: `records/2026-11-07-qwen4-l3-reference-top64` (`ade3bf7f5`), RUN_STATE 197. It closes operator card B12.
- The live MBP tests need Ed and the SSD (Sunday to Tuesday).

## Research audits (11-07 burn)
- Workflow `research-audit-burn` ran seven tracks: W1 pre-arm gate, 1(e)/1(f) fallback, Block 6 design, B5 release-to-paper, literature, research program, proportionality.
- Each track had a Fable 5.1 high seat and an Opus 5.5 xhigh seat, then an Opus synthesis.
- Outputs are under `docs/research-audits/2026-11-07/` on branches `research/2026-11-07-*`, collected in a draft PR "Research audits 2026-11-07 ...". They are model-written; triage them, do not adopt them wholesale.

## Ops
- `scripts/ops/mbp_quiet_os.zsh` is on branch `ops/2026-11-07-mbp-quiet-os`; Ed ran it 11-07 15:42.
- `tools/` here also holds the dry-run launcher and the blinded D-188 comparator wrapper example.

## Update, about 18:00 PST 11-07 (later the same session)
- **Research outputs** (draft PRs, docs only, model-written; triage them, do not adopt them wholesale):
  - **#695**, seven audits: W1 pre-arm gate, W1 budget fallback, Block 6 design, B5 release-to-paper, literature, research program, proportionality.
  - **#696**, the open-source contribution plan: 22 items, 11 decisions for Ed.
  - **#698**, methodology vs literature, giving ten new experiments with novelty checks; plus the Qwen-Next port and upstream plan.
  - All of it lives under `docs/research-audits/2026-11-07/`.
- **RUN_STATE 202:** R1 kit delivered, plus ruling R0-L2 (slow pick = the default band-hold rule, decided before the capture). The magistrate may fill the R0 rung and regenerate the kit on `lane/2026-11-07-r1-kit-r0fill`, then arm R1. The lead reviews that branch afterwards.
- **RUN_STATE 203:** ruling R10, the W1 budget fallback, declared blind before R1. 8-bit D runs at about 11.9 tok/s, so it fails 1(f) at every B_D. The order of fallbacks: (a) a budget-sized D G0 cap G0*; (b) 4-bit with its own R1 night; (c) the window council. The kit work for it (R10-4) is on `lane/2026-11-07-w1-kit-r10`, which needs a review before any W1 arm.
- **Pre-W1 blockers** (`w1-prearm-gate.md`):
  - protocol v4 is missing nine chair rulings (4, 5, 6, 9, 11, 15, 17, 18, 20) and WP19;
  - the battery 4(a) arm rule;
  - the 30B contrast deadman fit;
  - the duty-bar fallback;
  - the Ruling 76 test, red at the R1 lane head since D8-1.
- **BYTES stage 1 is due 12 Nov** and now has an owner (an agent PR plus magistrate instructions in `docs/run_reports/2026-11-07-bytes-stage1-plan.md`). It is Paper 1's strongest material.
- **Block 6** was collected on 10-21 and is sealed. Its REG §17 amendments (R0-R12 in `block6-design.md`) should land before the Block 5 unseal.
- **B5 release-to-paper** (`b5-release-to-paper.md`):
  - The release comparator cannot pass a registered null outcome (compare_b5_recompute.py:211-222). This needs a blind rule before any null-carrying release.
  - Nothing fills Paper 1's 219 FILL ids yet.
  - The "Release event" section of SEAL_RECORD is empty.
- **Gold L3 run backup:** copied to `/Users/edr/Dropbox/JouleWise-offload/2026-11-07-air/jwgold-run-l3` with a `.sha256` manifest; all 605 files verified.
- **Ed decisions outstanding:**
  - the ALIGN paper claim, and whether to allow 30B inject nights;
  - FINAL-DESIGN Q4 and Q6;
  - whether the Khiani paper is connected to us;
  - the OSS questions: the license, the "John Davis" alias, and running upstream code in sandboxes;
  - a Paper 1 retitle.
