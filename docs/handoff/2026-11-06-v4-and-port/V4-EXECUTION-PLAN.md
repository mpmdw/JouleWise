# ALIGN v4 execution plan

As of 2026-11-05, about 16:00 PST. I merged the CI, merge-plan and gap reports into one plan.

## Rulings I made where the three reports disagree

These are lead-level calls. They are not questions for Ed.

1. **Base branch.** The integration lane `lane/2026-11-05-align-v4-integration` is cut from `83e2dac59`, which is pilot10-benign. `c9a0a3943` is recorded as absorbed with `-s ours`. The pilot-10 pin is merged in after it lands, at about 00:40 on 11-06. Two things are dropped:
   - The CI report's plan to land fixes on pilot9-benign and cherry-pick them to pilot9-kit and pilot10-benign.
   - Any commit on pilot10-benign tonight.

   The six PRs get replaced by one integration PR.
2. **#657 default.** The field becomes `hybrid_checkpoint_limit: int | None = None` and is left out of the config when it is None. This follows the CI report's patch. The merge plan's fix (default 0, `None` in the kit's `member()`, regenerating the generator hash) is dropped. With default None:
   - committed v3 kit bytes and generator hashes stay the same as at `83e2dac59`;
   - trial fix-up items 1, 2 and 3 should no longer be needed;
   - the v4 kit sets `0` explicitly on Qwen3.8 cells, and the series runs with checkpoints off.
3. **Missing review rows.** No range-end hack in the test. For `1bf706fcf`, cite review `ee4ce93fc`, since the bytes are identical. For `dc2204dba`, `b29c25c59` and `0ba413d40`:
   - the lead checks `~/night-archive` for existing papers on the `mlx_runtime.py` hunks;
   - if there are none, run new Opus executing reviews now and record the rows labeled "retroactive".
4. **#657's edit to the pinned `mlx_runtime.py`.** Move the `prefill_prompt` hook into align-local code if that works without monkeypatching. Otherwise do a cited rebind ("frozen is not sacred") plus a boundary test showing the anchors' runtime path is unchanged when the limit is None or 0.
5. **Two reasoning-effort APIs.** Keep one: `chat_template_kwargs={"reasoning_effort": ...}`, which is covered by the hashed template policy. Drop #661's `reasoning_effort` endpoint argument and change `r0_mlx.py` to match.
6. **R0 disk bar.** For R0 the disk check only reports. The ≥80 GB bar and the offload hash checks become W1 arm gates. Offload labels come from config instead of being hard-coded to `{pilot8, pilot9}`.
7. **Headless launch.** Add a watchdog desk fence plus a one-shot LaunchAgent (gap option a). Do not exempt agents from the census.
8. **Fable cold passes.** These are required to merge the integration PR and to arm R1. They do not block R0. R0 is an engineering check, not registered data. If Fable later changes code R0 depends on, re-run only the affected R0 checks.
9. **#657 native test.** R0 repeats it on the measurement Mac. It is cheap and closes the "pinned stack" evidence gap.

---

## Work packages

Owner codes: **SOL** = Sol 6.1 xhigh in a sandbox (no Metal/MLX, may not have network). **OPUS** = Opus review agent. **LEAD** = native or Mac-side work by the lead. **ED** = Ed.

### Tonight (P0)

**WP0: merge PR #678 (RUN_STATE item 174) to main.** LEAD, CRITICAL for both paths.
- Goal: stop the magistrate from arming pilot 11 when the pilot-10 desk finishes.
- Dependencies: CI.
- Acceptance: merged before about 22:50 PST, and `origin/main` shows item 174.

### Track A: integration lane (critical for R0 and R1)

**WP1: create the lane from the trial merges.** LEAD, about 30 min, CRITICAL.
- Inputs:
  - trial branch `v4-trial` at `b49bace62` in `/Users/edr/code/CapstoneProject/jw-wt/v4-merge-survey`, or the bundle `/private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/359dce51-5c68-4ddf-a271-1a0232d75749/scratchpad/v4-trial.bundle`.
  - PR heads: #658 `58525031a`, #666 `989f649de`, #660 `78d7614a2`, #659 `e7960498f`, #661 `f14cba8fd`, #657 `8f8023277`.
- Steps:
  - Create the worktree at `/Users/edr/code/CapstoneProject/jw-wt/align-v4-integ`.
  - Take the trial merge chain up to `b49bace62^`. That is the `-s ours` merge of `c9a0a3943`, then 658, 666 with the `test_thermal_legacy` re-pin to `7bd1609e…`, then 660, 659, 661 and 657. Leave out the fix-up commit; WP2 replaces it.
  - Push the lane.
- Acceptance: a `git diff b49bace62^` against the pushed head is empty, and the lane is pushed. Sol worktrees branch from this head.

**WP2: #657 default fix and the rest of the fix-up.** SOL, then OPUS. CRITICAL.
- Inputs: the WP1 head, `/private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/359dce51-5c68-4ddf-a271-1a0232d75749/scratchpad/pr657-kit-default.patch`, and the trial fix-up `b49bace62`.
- Changes:
  - Default None, left out when None.
  - `tests/align/test_cache_checkpoint.py:365` sets `0` explicitly.
  - Keep trial fix-up item 4 (122B `unverified_xml_template:qwen3_5_moe`).
  - Keep trial fix-up item 5 (`unsplit(*, add_generation_prompt=True)`).
  - Drop items 1-3 unless tests still need them.
  - Check the endpoint treats None the same as 0, i.e. off.
- Acceptance:
  - `scripts/align_pilot_kit.py --check` is clean.
  - `plan_tree.json`, `identity_pins.json` and `local_file_verification.json` are byte-identical to `83e2dac59`.
  - Grep finds no `hybrid_checkpoint_limit` in any committed `align_pilot_v3` config.
  - `KitTests`, `test_cache_checkpoint*`, `test_pilot3_cache`, `test_pilot4`, `test_decode_budget`, `test_history_rendering` and `test_xml_tool_calls` all pass.

**WP3: #657 pinned-runtime ruling.** SOL builds, OPUS gives the executing review. CRITICAL.
- Inputs: `0ba413d40`, `joulewise/adapters/mlx_runtime.py`, registry pin `file@c27485347`, and #666's boundary test (`test_measurement_core_boundary`).
- Goal: carry out ruling 4.
- Acceptance:
  - A boundary test asserts the pinned core is unchanged, or that the rebind is cited and the anchor path behaves the same.
  - The Opus executing-review paper exists and is cited in the WP5 row for `0ba413d40`.

**WP4: R0 code fixes.** SOL, then OPUS. CRITICAL for R0.
- Inputs:
  - the WP1 head;
  - `/private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/359dce51-5c68-4ddf-a271-1a0232d75749/scratchpad/pr661-lock-path.patch`;
  - `joulewise/align/r0_mlx.py`, `r0_runner.py`, `r0_host.py` and `endpoint.py`.
- Changes:
  - (a) Lock path: a `MACHINE_LOCK` constant and a `main(..., lock_path=None)` parameter.
  - (b) `smc_source_commit` changes from `274fec2cb` to `58525031a`, or is derived at runtime. R0's own `rank_response` choices are labeled provisional.
  - (c) Ruling 5: remove the endpoint `reasoning_effort` argument. `r0_mlx` passes `chat_template_kwargs`.
  - (d) C2: `inventory()` accepts HF snapshot→blob symlinks only when the link resolves inside the hub root, and hashes the resolved target. No 17 GB copy.
  - (e) Ruling 6: the disk check splits into an R0 report-only check and a W1 arm gate, and offload labels come from config.
- Acceptance:
  - `test_r0_{checks,host,mlx,integration,progress,documentation,step}` pass on Linux CI and macOS. On macOS use a resolved TMPDIR, because `test_r0_host` fails 3/16 under `/var`.
  - A new test shows R0 completes with 66 GB free and no offloads.
  - A test confirms a symlink escaping the hub root is refused.
  - A test confirms reasoning effort shows up in the template-policy hash.

**WP5: b6 baseline repair.** SOL, plus a LEAD archive check. CRITICAL, because CI has to be green.
- Inputs:
  - `/private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/359dce51-5c68-4ddf-a271-1a0232d75749/scratchpad/b6-end-date-fixture.patch`, which only touches `tests/b6/round_support.py` and sets `FIXTURE_END_T0_BEFORE` to now + 365 days;
  - `configs/b6/executing_reviews.json`;
  - review `ee4ce93fc` from `origin/codex/2026-10-28-by-therm-lines*`.
- Changes: apply the date patch, then add review rows for `1bf706fcf`, `dc2204dba`, `b29c25c59` and `0ba413d40` per ruling 3. Any retroactive Opus reviews are their own OPUS sub-task and run in parallel.
- Acceptance:
  - `test_loop_round_desk` 6/6, `test_desk_resume_finalize` 6/6, `test_capture_screen_reachability` 9/9, `test_cold_pass_fixes` 14/14 and `test_audit_record_fixes` all pass.
  - Every new row cites a paper that actually exists.
- To reproduce locally: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/Users/edr/code/CapstoneProject/jw-wt/ci-rootcause-b6-tmp`.

**WP6: assemble, run the full suite and native tests, open the PR.** LEAD. CRITICAL.
- Inputs: the WP2, WP3, WP4 and WP5 commits, applied in that order onto the WP1 head.
- Tests:
  - all 98 ALIGN modules plus `tests/b6`, using the pinned mlx 0.31.2 / mlx-lm 0.31.3 venv with Jinja2;
  - native tests on the M4 Air: `test_cache_checkpoint_native`, `test_r0_mlx_native`, `test_thermal_mlx` (`JW_ALIGN_MLX_NATIVE_TESTS=1`), `test_smc_native` (`JW_LIVE_HW=1`) and the MLX deadman test;
  - `compileall`, `git diff --check` and `align_pilot_kit.py --check`.
- Then open one integration PR into pilot10-benign and link the six PRs as superseded.
- Acceptance: everything passes locally and every CI shard is green. If #659's reharvest failure (`desk_compress` reserve of 20 GiB) comes back, re-run it once.

**WP7: Opus executing review of the integration diff.** OPUS. CRITICAL.
- Inputs: `83e2dac59..<WP6 head>`.
- Focus:
  - the `diagnostics.end_state` stop order (deadman → thermal timeouts → `thermal.incomplete` → `runner.error` → `decode_budget`); rule on whether a thermal stop should outrank a fault;
  - the six omit-if-None `EpisodeSpec` fields;
  - `add_generation_prompt` passing through the XML, `reasoning_content` and JSON render paths;
  - #666's rebuild `5e257e63e..989f649de`, which was never reviewed;
  - the WP2, WP3 and WP4 commits.
- Acceptance: a written verdict, every HIGH or BLOCKER fixed and re-verified, and executing-review rows recorded.

**WP8: Fable cold passes.** Fable, LEAD writes dispositions. In parallel with WP7. CRITICAL for R1 only.
- Inputs: the WP6 head, covering B1/B2 (#659), B5/B6/B7 (#666, #657) and the `attribution.py` changes.
- Acceptance: a recorded pass and every finding dispositioned.

**WP9: merge the pilot-10 pin.** LEAD. CRITICAL.
- When: after the magistrate pushes the pin and `DESK_DONE`, about 00:40 PST on 11-06.
- Command: `git merge --no-ff origin/lane/2026-11-05-align-pilot10-benign`.
- Acceptance: the merge is clean (only `calibration_ledger_head.json` changes), `test_align_pilot_session` and `test_thermal_legacy` pass, and CI is green.
- Then: merge the integration PR once WP7 (and WP8, if done) pass, per the merge authorization. The measurement checkout can then fast-forward to this head.

### Track C: making R0 headless (critical for R0, parallel with Track A)

**WP10: watchdog desk fence and R0 launcher.** SOL, then OPUS. Full tier, on main. CRITICAL for R0.
- Inputs: the magistrate watchdog on main, and `QuietGuard`/`agent_census` from #661.
- Changes:
  - The magistrate writes a fence file `{purpose, pid, deadline}`.
  - The watchdog treats an active fence like a plan span and does not relaunch.
  - A stale fence (dead pid or deadline passed) is cleared.
  - R0 is launched through a one-shot LaunchAgent (`launchctl`, not `nohup`), and the magistrate exits.
  - The launcher checks AC power (`pmset -g batt`) and free space.
  - The launcher SIGSTOPs corespotlightd and spotlightknowledged and resumes them on every exit path (trap on normal exit, error and SIGTERM).
- Acceptance: tests with a fake launchctl show:
  - no relaunch during the fence;
  - a relaunch after the process exits or the deadline passes;
  - a stale fence is cleared;
  - Spotlight is resumed in all three exit cases.

  CI is green and Opus has approved.

**WP11: committed R0 config for the measurement Mac.** LEAD (Mac facts), SOL (headless runbook).
- Inputs:
  - from the measurement Mac: `hw.model` (Mac15,9 is expected), D's path `/Users/edr/jw_models/mlx-community/Qwen3.8-27B-8bit` (check `symlink:false`), the 30B HF hub snapshot path, the SHADE cache and custody parents;
  - from the laptop: HF LFS sha256 values at `815b83c0` via `?blobs=true`, which closes #661's deferred LOW.
- The config uses no offloads and drops the High Power repeat. The R0 record (`report.json`, `report.md`, SMC journal hash) is committed to `docs/align/r0/2026-11-06/` on the integration lane.
- Acceptance:
  - the committed `r0_desk.json` validates in a dry run on the laptop;
  - D's local hashes match HF LFS;
  - the runbook has a headless section.

**WP12: council housekeeping on main.** LEAD, light tier. Needed for R0 (the directive cites it).
- Merge #656.
- Add an amendment that records:
  - the R0 step profile 300/900/600 s;
  - the frozen desk commit: name `cda28a5ef` (what actually runs) and show its diff against `4d54cb47b`;
  - that Mac15,9 sensor keys are provisional until R0.
- Acceptance: merged, and the magistrate can read it.

**WP13: RUN_STATE item 175 (R0 directive).** LEAD. CRITICAL.
- Dependencies: WP9 merged head, WP10 merged, WP11, WP12.
- Contents:
  - the commit to run and the measurement checkout head;
  - R0 runs headless, by day, with no window armed and only after `DESK_DONE`;
  - the exact fence plus LaunchAgent command;
  - preconditions: Spotlight pause, AC power and free space;
  - after a census refusal, retry in a new record directory, at most 2 retries;
  - where the record is committed, and an email to Ed with the summary.
- Pre-declared dispositions:

| R0 outcome | Disposition |
|---|---|
| Effort rung | Use the first passing of xhigh/medium/low. If none pass, D is screen-only. |
| B7 checkpoint | Off for the series. Record what R0 measures. |
| #1632 mitigation fails | Stop and mail the lead. |
| D-4bit | Only if the predicted B_D < 6,144 and the disk check passes; otherwise stop and mail. |
| SMC roles inconclusive | Stop and mail. |

- Item 175 also lists the R1 arm conditions (below) and keeps the standing items: no v3 windows, pilots 8-10 stay on disk.
- Acceptance: merged to main before R0 is meant to start on 11-06.

**R0 run.** Magistrate, about 6.5 h on 11-06 by day.
- Acceptance: `complete_r0: true`, and the record is committed.

### Track B: R1 builds (start now, in parallel with A and C)

**WP14: protocol v4 rulings.** OPUS chair. CRITICAL for R1.
- (a) The sensor-selection rule. Council §2.6 says t63 ≤ 5 s and ΔT ≥ 3 °C with τ ≤ 300 s. The R0 ruling and #658 say τ < 30 s, and τ in (120, 900) s.
- (b) The window-reference R custody mechanism. Recommended: member 5 writes a custody file; later members' specs carry its path plus a digest; the file is verified when read at runtime.
- (c) How `ThermalRegistry` reaches `run_benchmark` past the pinned `run_campaign.py`: align-local entry point, or cited rebind.
- Acceptance: written rulings committed next to the council amendment.

**WP15: thermal runtime wiring (B3).** SOL, then OPUS. CRITICAL for R1.
- Dependencies: WP14 (b, c) and the WP6 head.
- Acceptance:
  - A test shows a gated D cell selects `ThermalRegistry`.
  - A later member reads R from member 5's custody file and refuses on a digest mismatch.
  - Anchors run unchanged.

**WP16: kit v4, R1 shape first (B1).** SOL, then OPUS. CRITICAL for R1.
- Inputs:
  - the 18-member roster (Amendment A1);
  - seed tag `qwen3.8-27b` (indices 1 and 91-93; held-out from 2);
  - anchors a-e01..e04 hash-identical to `83e2dac59`;
  - X = b-e25 (index 16) and Y = b-e18 (index 14) from `45b47f7b6`, with `max_turns` taken from WP18;
  - D base configs: sampler 1.0/0.95/20/0, `assistant_history: reasoning_content`, XML tools, thermal, B_D, deadman, explicit `hybrid_checkpoint_limit=0`, `warmup_condition='benign'`, no `max_episode_seconds`;
  - D 8-bit identity pins from WP11;
  - a parameterised `align_pilot_session.py` (KIT, PACK_ID and desk schema).
- Acceptance: `test_v4_kit.py` checks:
  - seeds recomputed independently;
  - ABBA position sums 22/22;
  - anchor hashes;
  - contrast seeds against V11;
  - the fit-rule drop order (drop ordinal 17, then lower B_D in 1,024 steps down to 6,144).

**WP17: R1 window kit (B4).** SOL, then OPUS. CRITICAL for R1.
- Shape: an armed night-plan window run through `run_night`.
- Contents:
  - the 30-min idle soak;
  - step tests for the 30B and for D (10k fed prefill + 4,096 seeded decode, 10-min cooldowns);
  - one X-G contrast run;
  - two gated and held D spam/benign s1 runs;
  - an optional D-4bit run;
  - no High Power A-B-A unless Ed says otherwise.
- It writes `registration/r1_slots.json` covering S1-S9, B_D, I_D, T_dead, N_chunk, t_decline and the heavy/light class.
- Dependencies: WP15 and WP16.
- Acceptance: a synthetic rehearsal on the laptop fills every slot field, and the calibration brackets and harvest are wired in.

**WP18: pilot-7 reference fixture (B6).** LEAD and magistrate (Mac-side), then SOL.
- Inputs: the b-e25 and b-e18 `align_turns.jsonl` files from the pilot 6-7 offload copy, and `p7-PILOT.json`.
- Acceptance: a committed token-id fixture plus the X and Y turn counts, and `cross_pilot_identity` passes against the fixture.

**WP19: contrast token-identity check (D5).** OPUS. CRITICAL for R1.
- Check: the neutral warmup and sidecar startup leave the 30B cache and sampler RNG exactly as in pilot 7.
- Dependencies: WP16 and WP18.
- Acceptance: a written verdict, with a laptop replay showing X matches b-e25 token for token.

**WP20: protocol v4 document (B2).** SOL drafts, then a blind cold gate by Fable and Opus.
- Dependencies: WP14.
- Output: `docs/align/pilot_protocol_v4.md`, including the reserved "Addendum FN" section.
- This is not needed to arm R1 itself, only for W1 registration. Start it now.

**WP21: full v4 desk (B5).** LEAD copies `k_sessions.py`, `summ_alt.py` and `seeds.py` from `~/night-archive` into the repo, then SOL builds:
- U4-U6;
- the K-session anchor read;
- `--compare-session`;
- the imports of `cda28a5ef` / `7fbd95e31`.

Needed to read R1's results, not to arm it.

**WP22: synthetic W1 dry run (B7).** OPUS. W1 gate only.
- Dependencies: WP16 and WP21.

**WP23: W1 plan template (G).** SOL. The lead freezes it after R1.

---

## Critical paths

**(a) R0 headless allowed.** Target: R0 starts on the morning of 11-06.

```
WP0 (tonight)
WP1 → {WP2, WP3, WP4, WP5 in parallel} → WP6 → WP7 → WP9 (after the ~00:40 pin) → merge
                                                                                    ↘
WP10 (fence, on main, parallel with Track A) ───────────────────────────────────────→ WP13 → R0
WP11, WP12 (parallel) ─────────────────────────────────────────────────────────────↗
```

Not on this path: WP8 (Fable) and all of Track B.

**(b) R1 armable.** Target: 11-07/08 at the earliest.

```
R0 complete with dispositions applied
+ WP8 Fable dispositions
+ WP14 → WP15 → WP16 (R1 shape) → WP17
+ WP18 → WP19
+ Ed's physical checklist confirmed by mail
+ disk ≥ R1 root size plus the floor (R1 is about 15-20 GB, +16.1 GB if D-4bit; about 66 GB free)
+ the ledger-pin lane named as the integration lane
+ arm notice mailed to Ed
→ RUN_STATE item 176 (R1 arm)
```

Off this path: WP20, WP21, WP22, WP23, and the offload of pilots 8-10 (needed for W1, not R1, unless the D-4bit run plus the floor goes over the free space).

## How to run it in parallel

- **Now, on Sol:** WP2, WP3, WP4, WP5, WP10, WP16 (skeleton), WP20 (skeleton).
- **Now, on Opus:** WP14 rulings, and the retroactive reviews for WP5.
- **Lead:** WP0, WP1, WP11 Mac facts and HF hashes, WP12, the archive copies for WP21, the WP18 request to the magistrate.
- **After WP6:** WP7 and WP8 together.
- Sol never runs native tests. Every native check goes to the lead on the M4 Air. Measurement-Mac checks go to the magistrate or R0.

## Leftover housekeeping

LEAD, small, not on either critical path.
- Close #657-#661 and #666 as superseded by the integration PR.
- Log the deferred LOWs:
  - #657: R1 overhead measurement and the council SHA;
  - #658: the census tick missed under `taskpolicy -b`;
  - #661: exact weight authentication, which WP11 closes.
- Write down that #659/#660's "reconcile against Amendment 1" step is now covered by WP16 and WP20.

---

## Questions for Ed

1. **Disk (E1).** Go or no-go on the #665 verified offload of pilots 8-10 (iCloud plus a second copy on the SSD arriving about 11-07). And which goes first on the measurement Mac: W1 or the Flash-Next gold-parity run (needs about 120 GB free at peak)? R0 and probably R1 do not depend on this. W1 does: it needs about 117 GB free at arm.
2. **High Power A-B-A in R1 (Q5).** Will you toggle it in person, add a `pmset` entry to sudoers, or skip it? The headless default is to skip it.
3. **Q4 and Q6.** Default yes for 59,520 s D windows (Q4) and default no for registration grade (Q6). Confirm or override.
4. **Physical checklist (§3.1), before R1.**
   - stand with at least 5 cm clearance;
   - thermostat setpoint recorded;
   - ambient thermometer or logger;
   - battery at least 95 % with Optimized Battery Charging OFF;
   - 140 W MagSafe connected directly;
   - cooler in place but off, if you own one;
   - no Claude or Codex desktop apps open on the measurement Mac, because the census matches them.

   This one is a task for you, not a decision. Mail a confirmation.
5. **Optional:** launch `/code-review ultra` on the integration PR once WP6 opens it. I cannot launch it myself.

Two lead-level process calls you should know about, but that I'm not asking you to decide: the watchdog desk-fence change (ruling 7, full tier) and letting R0 run before the Fable pass (ruling 8). I'll tell you once they're done.
## Ed ruling (2026-11-05, after the plan): High Power A-B-A is IN R1
Ed: "im fine with providing a narrow sudo rule just like i did for network time." R1 (WP17) includes the High Power A-B-A segment, using a narrow sudoers rule limited to exactly `pmset -c powermode {0,2}`, installed by Ed in /etc/sudoers.d/joulewise-powermode. The R1 driver must:
- verify the rule with `sudo -n -l`;
- record powermode before and after each segment;
- restore Automatic (0) on every exit path (trap on normal exit, error and signals);
- refuse to start if it cannot restore.

## Ed (2026-11-05): R0 wall time — "does this really need 6.5 hours?"
Lead ruling, a WP4 follow-up (WP4b), with no change to the checks' content:
1. Fail-fast order: run host, disk, template, generated tool-call turns, memory and the SMC profile before the long generations.
2. Ladder: start at xhigh and stop at the first passing rung (ruling: first passing rung is adopted).
3. Long decode: one attempt; the second runs only on failure.
Target: about 3-4 h when everything passes. The report records each phase's actual duration.
