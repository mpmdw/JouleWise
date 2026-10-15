# Block 6, stage 1: the machine test and the round-1 arm

Branch `integration/2026-10-14-b6-stage1`, not merged to main (orchestrator decision of 2026-10-14, RUN_STATE
item 39: block 6 is collected from a measurement checkout at a pinned commit of this branch and merges to main
after the block-5 release). This page gives the two commands the design's stage 1 ends with
(`docs/design/block6_collection_draft.md` section 17): the one machine test of about 40 minutes, then the arm of
round 1. Neither has been run. Run nothing here while a block-5 analysis job or any agent is using the Mac.

## What is on this branch

The four stage-1 lanes of design section 17, merged one at a time in its order, then the loop:

| Order | Lane | Head merged | What it adds |
|---|---|---|---|
| 1 | `lane/2026-10-14-b6-harvest` | `83163e6a4` | flags as records, one acceptance function, carried calibration bound, own-capture staleness, spare removed, model-hash refusal, the block-6 catalog |
| 2 | `lane/2026-10-14-b6-driver` | `a1b2b59c3` | pause on an agent sighting, the driver's own keep-awake hold, a sleep reading at every run, waiting idle admission |
| 3 | `lane/2026-10-14-b6-precheck` | `82dfb8bdc` | the pre-session check (`precheck.json`), smoke by fingerprint, a copied ledger |
| 4 | `lane/2026-10-14-b6-desk` | `8c69dff71` | compression, the session structure check, pack stopping |
| 5 | `lane/2026-10-14-b6-loop` | `7bd443286` | the unattended loop under launchd (precheck, smoke, session, desk, rotate), program mail |
| 6 | `lane/2026-10-14-b6-adapters` | `165b1972f` (merge `b2837ba38`) | the loop's lane adapters (P1/P2, D1/D2, S1/K1, H3, A1), block-6 plan inputs, one harvest path for smoke and session, the registration loaders and copies of block 5's pins and sizing, `plan.resolve_stage_dispatch`, the program courier, the wake job |
| 7 | `lane/2026-10-15-b6-cold-chain`, `lane/2026-10-15-b6-cold-acceptance`, `lane/2026-10-15-b6-cold-packroot` | `2b2bea4cc`, `f67854d41`, `76aa47884` (merges `90d9222de`, `dd9a9be35`, `3827f63de`) | the cold passes' fixes: every block-6 chain renders the block-6 opening screen (flag above the alignment reference, stop only on b_pre + s_bracket above the registered line, null values while `acceptance.json` is absent) and no spare retries; a driver's physical stop is a physical stop (rotate), an opening capture with no bound is N1; the loop counts from the acceptance verdict; compression waits for a judged harvest and a re-harvest uses a fresh archive root; GAMMA's interior references have their own role; the pack registrations close at 2026-11-02T00:00:00-08:00; the pre-check and smoke desk judge each pack with its own roster (one `acceptance.json` serves all three packs) |
| 8 | `fix/2026-10-15-b6-s3-review`, `lane/2026-10-15-b6-s3-cold` | `9409c83b2`, `d9ce14fcb` (merges `e81e60530`, `91e37e7c6`) | stage 3: the review of the integration's own commits and the second pair of cold passes. A block-6 night job's courier is a program (default `scripts/b6_courier.sh`; an agent courier is refused and a missing one is never replaced by `claude`) and the job's PATH is `/usr/bin:/bin:/usr/sbin:/sbin`; the machine-test injector reaps its children on SIGTERM; the machine-test report needs a start and an end sleep reading for every run of the reduced plan; after any chain stop the desk finalizes or aborts the open calibration bracket and advances the pin, so a stop no longer holds the loop; a physical stop keeps the structural defects it cannot explain; the operative-bound stop exits 13 (12 stays the opening-screen failure); a session dropped at the pack close closes its arm notice and is recorded `never_armed`; `configs/b6/executing_reviews.json` lists the executing reviews of every number-bearing commit |

The loop is in stage 1 because stage 1 cannot run without it: the pre-session check waits while any `claude` or
`codex` process is alive or the keyboard was used in the last 600 s (`joulewise/b6/precheck.py`), so no agent can
run it to a start, and the smoke module leaves launching to the loop (`joulewise/b6/smoke.py`). Since lane 6, the
loop's connections to the other lanes (`joulewise/b6/lanes.py` `resolve(repo_root, loop_root, ...)`) are real
adapters; with registered packs the loop no longer holds on `lane_missing`. Lane 6's build, review and fixes are in
`/Users/edr/night-archive/b6-build/stage2/DISPOSITIONS-adapters.md`.

## The measurement checkout (both commands need it)

Built once, by the block-5 post-seal runbook's steps 3 to 5
(`docs/process_traces/2026-10-07-block5-seal/30-post-seal-runbook.md`), with these values:

- **Commit:** a pinned commit of this branch, `P` below (the head after the open issues that matter for the test
  are closed). Candidate `P` (stage 3, 2026-10-15): the commit that adds this sentence; its hash is in
  `/Users/edr/night-archive/b6-build/stage3/DISPOSITIONS-cold.md`. The checkout is never pulled, fetched or edited afterwards; its only later commits are the ledger
  pin advances the chain's desk step makes.
- **Path:** `/Users/edr/night-custody/measurement/JouleWise-measurement-<UTC stamp>-b6`. No path may contain
  `claude` or `codex`: the agent census matches those strings anywhere in a process's arguments.
- **Interpreter:** step 4's relock (`/opt/homebrew/bin/python3.13 -m venv .venv`, then the two `pip install -c
  env/mac-measurement-lock.txt` commands), and `brew pin python@3.13`.
- **Ledger:** step 5's seed, unchanged: block 3's terminal ledger
  (`/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/derived/terminal-ledger.jsonl`,
  SHA-256 `6ee89e5a…7530e`) copied to `runs/calibration_observation_ledger.jsonl`. Its head, row 402, is the pin
  this branch already commits (`configs/calibration/calibration_ledger_head.json`), so no pin commit is needed
  and no block-5 runs root is read. Block 5's own captures (rows after 402) are then not in block 6's ledger:
  block 6's acceptance judges each session by its own captures and only discloses other sessions' captures, so
  this changes flags, not which sessions count (open issue 4).
- **Registration directory:** `configs/b6/registration/` holds, since lane 6, the loaders' README, copies of block
  5's `identity_pins.json` and `sizing_b5.json`, and their schemas. `acceptance.json` (registration draft S-4 to
  S-9) is absent until the registration seat writes it from quiet-machine numbers (open issue 2). The machine test
  does not need it: it writes its own non-claim one.

## The machine test

**What it checks, on the real machine, with no agent alive.** Design section 13: "agent pause, an idle
disturbance up to the 1,500 s cap, meter unplugged". It is a non-claim smoke of pack ALPHA (4 runs: start
reference, one decode repeat, one prefill repeat, end reference, between an opening and a closing capture),
launched exactly as a session is (the night job through `scripts/install_night_agent.sh`, ProcessType
Interactive), with two faults injected by a second launchd job and the meter's data link unplugged. Its numbers
are never claim data; its ledger is a copy.

**Before it, Ed does one thing:** disconnect the KM003C meter's data link to the Mac (the USB cable the Mac reads
it over). The Mac must stay on its charger: if the meter sits in the charger's path and cannot be disconnected
without cutting power, take it out of the path and plug the charger straight into the Mac. On battery the arm
refuses. This is the "meter unplugged" item: the session must go on, with the meter recorded as absent.

**The command** (from a terminal or an activation that then exits at once; it bootstraps two launchd jobs):

```zsh
M=/Users/edr/night-custody/measurement/JouleWise-measurement-<UTC stamp>-b6
/opt/homebrew/bin/python3.13 -B "$M/scripts/b6_machine_test.py" prepare --install \
  --measurement-root "$M" \
  --out "/Users/edr/night-b6/machine-test/MT-$(date -u +%Y%m%dT%H%MZ)" \
  --pack d117_floor_qwen3-1p7b_v5 --lead-s 900 --agent-s 45 --busy-cores 1 --busy-s 1620
```

Every argument:

- `"$M/scripts/b6_machine_test.py"`: the harness as committed at `P` in the measurement checkout, so the test
  runs the code the sessions will run. `/opt/homebrew/bin/python3.13 -B`: the Homebrew interpreter, no bytecode
  files written into the checkout.
- `prepare`: build everything under `--out` and never write into `$M`: a non-claim block-6 registration
  directory (acceptance times of the non-claim replay, pins and sizing copied from
  `configs/campaigns/v5_claim_25g83/`), the two desk identity files from the live machine
  (`joulewise/b6/desk_identity.py`), the plan inputs (`joulewise/b6/plan_inputs.py`, the same code the loop's D1
  uses: the sealed block-5 threshold block, ALPHA's sizing), the fingerprint, then `joulewise.b6.smoke.prepare`: a fresh
  clone of `$M` at its head inside `--out`, a copy of the ledger and pin, the plan tree reduced to the smoke's
  4 runs by `configs/b6/smoke_keep.json`, the plan. Then the night-job plists (the installer in render-only
  mode) and the injector plist, and `install.zsh`.
- `--install`: run `install.zsh` at the end: the real installer on the smoke plan (two labels,
  `com.joulewise.night` and `com.joulewise.night.deadman`, with `--courier-bin` naming the smoke's file-writing
  courier stub, so no `claude` session runs after the chain) and `launchctl bootstrap gui/<uid>` of the injector
  `com.joulewise.b6mt.inject` (ProcessType Standard, so its busy core is a real core, not an efficiency core at
  background priority). Without `--install`, `prepare` stops after writing, for a dry look.
- `--measurement-root "$M"`: the checkout above.
- `--out`: a new directory per attempt (refused if it exists); `/Users/edr/night-b6/` is block 6's working root
  (the loop's root is `/Users/edr/night-b6/loop`).
- `--pack d117_floor_qwen3-1p7b_v5`: ALPHA, the 1.7B pack: the shortest runs, and the pack round 1 starts with.
- `--lead-s 900`: t0 is 15 minutes after the command (rounded up to a minute). The installer refuses an install
  later than t0 minus 300 s, and the activation must have exited before t0: the night job's own census refuses
  the session while an agent is alive.
- `--agent-s 45`: the injected "agent" (a process that does nothing, whose command line contains `claude`) lives
  45 s. The in-chain census runs every 30 s, so 45 s is seen at least once; design 3.4 names 30 s, which can fall
  between two censuses.
- `--busy-cores 1 --busy-s 1620`: the idle disturbance: one core kept busy for 1,620 s (the 1,500 s cap plus
  margin), started when the agent pause has ended, so the next run's waiting idle admission reaches its cap and
  that run is skipped with `idle.wait_cap_skip`. One core is design 3.4's disturbance.

**What happens, and how long.** The injector waits for the start reference to end (so the arm, census and dwell
are over), starts the agent, waits for the pause to end (resume 10 minutes after the last sighting, with a fresh
idle admission), starts the disturbance, and exits when the chain's terminal record exists. Roughly: 15 min to
t0, about 5 min of arm, 4 min opening capture, 2.5 min start reference, about 11 min of agent pause (the run in
flight excluded), 25 min of waiting to the cap (that run skipped), 2.5 min for the last run, 4 min closing
capture: about 55 minutes of chain after t0, plus the desk report. Design 13's "about 40 minutes" did not count
the cap wait in full.

**After the chain** (any session that may run agents, once `night/result.json` exists):

```zsh
/opt/homebrew/bin/python3.13 -B "$M/scripts/b6_machine_test.py" report --uninstall --state "<out>/machine-test.json"
```

It runs the smoke desk (since lane 6 the session's own harvest, `scripts/harvest_b6_session.py --smoke` with the
block-6 catalog and the test's registration directory, then reads its `derived/b6-acceptance.json`), uninstalls the night
job and the injector, writes `<out>/report.json`, and prints, structure only, for each item whether the records
show it: the agent pause (an episode, resume no sooner than 600 s after the last sighting, the overlapping run
excluded, the chain not stopped); the idle cap (exactly one `idle.wait_cap_skip`, later runs measured); the meter
(stream header `absent`, harvest flag `meter.absent`); the keep-awake hold verified at start and end, a sleep
reading at every run; chain exit 0, harvest exit 0, the smoke desk's status `physics` (the injected faults are
physical, so a real smoke would wait and run again) and no desk errors. Reconnect the meter afterwards.

**Pass.** Every item observed and no desk error. A missing item is a defect in the code it names: fix it on this
branch, re-pin, run the test again. A physical refusal at the arm (clock, battery, thermal, contention, disk,
instrument) is not a failure of the test: run it again later.

## Arming round 1

Round 1 is the loop's first session: pack ALPHA (`configs/b6/loop.json` `base_order`: alpha, beta, gamma; design
section 13, rotation A B G in round 1). The one command installs the loop's launchd agent from the measurement
checkout:

```zsh
M=/Users/edr/night-custody/measurement/JouleWise-measurement-<UTC stamp>-b6
/usr/bin/sed -e "s#__REPO_ROOT__#$M#g" -e "s#__LOOP_ROOT__#/Users/edr/night-b6/loop#g" \
  "$M/configs/launchd/com.joulewise.b6loop.plist.template" > "$HOME/Library/LaunchAgents/com.joulewise.b6loop.plist" \
  && /bin/launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.joulewise.b6loop.plist"
```

Every argument:

- `__REPO_ROOT__` → `$M`: the job runs `/bin/zsh $M/scripts/b6_loop_guard.zsh`, so the loop, its configuration
  (`$M/configs/b6/loop.json`), the pack registrations (`$M/configs/b6/packs/*/registration.json`) and every
  collection are the pinned commit's.
- `__LOOP_ROOT__` → `/Users/edr/night-b6/loop`: the loop's state (`state.json`, `attempts.jsonl`, the outbox, wake
  records, `collection.active`); the same value `loop.json` names.
- The rendered file goes to `~/Library/LaunchAgents/com.joulewise.b6loop.plist`; `launchctl bootstrap gui/<uid>`
  loads it in Ed's login session, where the night jobs also run.
- What it then does on its own: a tick every 300 s (`StartInterval`) and once at load (`RunAtLoad`), as a
  Background process. The guard exits in milliseconds while a collection is live, so the loop costs nothing
  inside measured runs. Each tick takes one locked step: pick the session (ALPHA), pre-check (wait on physics,
  hold on a certain exclusion), arm notice to GitHub issue mail with Ed's 30-minute NO, smoke if the fingerprint
  changed, install the session by the night-job route, desk it (harvest, structure check, compression), rotate.

**What each step now starts (lane 6 adapters, `joulewise/b6/*_lane.py`).**

- *Pre-check (P1/P2, `precheck_lane.py`):* writes `precheck.json` from the registration directory; a missing
  `acceptance.json` is the flag `precheck.acceptance_unavailable`, not a stop. It kills registered orphaned
  fixtures (parent pid 1) after a fresh census (lead fix L-4).
- *Prepare (D1, `driver_lane.py` `prepare_session`):* plan inputs from `joulewise/b6/plan_inputs.py` (the block-6
  registration's pins and sizing, the sealed threshold block) and the two desk identity files
  (`desk_identity.py`). Session ids are `r<round>-<pack>`, then `-n<k>` when reused, `-a<k>` after a refusal,
  `-smoke-<k>` for smokes; each id is used once. Paths: `/Users/edr/night-b6/sessions/<id>/{custody,runs-parent,
  backup-claim,backup-bound,archive,export}`, staging `/Users/edr/night-b6/loop/staging/<id>`.
- *Launch (D2):* t0 is bound at launch, `launch_lead_s` (420 s, `configs/b6/loop.json`) after the tick, rounded
  up to a minute; the plan is written then, and the night job is installed by `scripts/install_night_agent.sh
  --courier-bin $M/scripts/b6_courier.sh` (labels `com.joulewise.night` and `.deadman`; without `--courier-bin` a
  block-6 plan gets that file too, an agent courier is refused, and both jobs run with PATH
  `/usr/bin:/bin:/usr/sbin:/sbin`). The courier is a program that writes the driver's mail request to `<session>/courier-program/` and marks it sent; block-6 mail goes by
  the loop's mailer. Status reads `launchctl print` (`runs`, `state`, `pid`) and the chain's process group; an
  arm or t0 refusal on physics (agent census, unmeasured instrument, clock, battery, ...) returns `Refused` and
  the loop waits without using a slot. The night job is uninstalled once the terminal record exists.
- *Smoke (S1):* the same route on a 4-run clone; its desk is the session harvest with `--smoke`.
- *Desk (K1, `desk_lane.py`):* first the ledger: a chain that stopped before its closing capture leaves its bracket
  session open, so the desk finalizes a slot whose capture custody is complete (`recover_calibration_ledger.py
  resume-finalize` with the reservation's frozen plan), aborts what is still open with the stop as the reason, and
  advances the pin; then `scripts/harvest_b6_session.py` (4 h timeout), `joulewise/session_structure.check` and,
  after a judged harvest, `joulewise/desk_compress.compress`. Harvest exit 6 (acceptance unavailable) keeps
  every number and flag and records the session `pending_registration`; `b6_loop.py reharvested <id>` judges it
  once `acceptance.json` exists. Any exit other than 0 and 6 is a harvest fault, `pending_harvest`, never a
  judged session. A lost chain (job gone or ended with no terminal record, process group gone) has its ledger
  bracket aborted and is flagged `records.terminal_record_absent`.
- *Wake:* on a hold the loop bootstraps `com.joulewise.b6wake.<n>`, which runs `$M/scripts/b6_wake.zsh` → `claude
  -p` with `docs/process/b6_wake_brief.md` from `/Users/edr/code/JouleWise` (deferred while a collection is live);
  output in `/Users/edr/night-b6/loop/wake/com.joulewise.b6wake.<n>.out/.err`. A woken agent makes the next
  pre-check wait until it has exited.

**What must be true first, or the loop holds and starts nothing** (it says why in `state.json` and by one mail):

1. Done at `b2837ba38`: the lane adapters are on the branch.
2. `configs/b6/packs/{alpha,beta,gamma}/registration.json` are `registered`, committed and valid (after a tick,
   `/opt/homebrew/bin/python3.13 -B "$M/scripts/b6_loop.py" status` shows `pack_not_open` with each refused
   pack's reasons; today all three say `draft`; they name `configs/b6/flag_catalog_b6.json`). With registered
   packs and no `acceptance.json`, sessions run and wait as `pending_registration`, and pending sessions count
   toward `attempts_before_pause` (5 per pack, then `pack_paused` and a wake): commit `acceptance.json` first.
3. The machine test passed on the same commit.
4. `gh` is logged in for `mpmdw/JouleWise` (the mail transport); `claude` is at `/Users/edr/.local/bin/claude`
   for the wake job.
5. Nothing else is installed: `launchctl list | grep com.joulewise` prints nothing (wake jobs stay loaded after
   their run; boot out any `com.joulewise.b6wake.*` left from a test), and no agent is alive when the first
   session's pre-check runs (it waits otherwise; it does not fail).

To stop: `/opt/homebrew/bin/python3.13 -B "$M/scripts/b6_loop.py" hold` (the loop holds after its current step; a running
collection is never killed), then `launchctl bootout gui/$(id -u)/com.joulewise.b6loop` once `collection.active`
is gone.

## Decisions made at the integration (the texts determine them)

- **The loop joins stage 1**; its adapters arrived with lane 6.
- **Driver M2: the session's kill deadline covers both budgets.** The driver lane asked that `window_max_s` add
  the pause limit and the session wait budget (7,200 + 7,200 s), and the registration draft (section 7 item 2)
  registers it. `joulewise/b5/plan.py` now writes `window_max_s` = the pack's programmed span + the 3,300 s arm
  cap + 7,200 + 7,200, rounded up to a minute: 124,620 s (34.6 h) for ALPHA, 127,020 s for BETA, 113,460 s for
  GAMMA (spans from `configs/campaigns/v5_claim_25g83/sizing_b5.json`). The replications had the room already
  (a 125-run session takes about 6 h, about 10 h with both budgets spent, against 30.6 h before), so this changes
  no replication outcome; it makes the code say what the registration says, and it holds for a pack whose sizing
  has less slack. The dead-man time moves with it (the installer derives it from `window_max_s`).
- **One block-6 registration directory**, `configs/b6/registration/`, for the pre-check, the smoke desk and the
  session harvest (open issue 2); a registration the pre-check cannot read is the flag
  `precheck.acceptance_unavailable`, not a stop.
- **Block-6 codes live in the block-6 catalog** (`configs/b6/flag_catalog_b6.json`, built by
  `scripts/build_b6_flag_catalog.py`), never in block 5's sealed catalog: the driver's seventeen codes and the
  loop's three were added there, and the loop reads it.

## Open issues

1. **Closed at `b2837ba38`: the loop's lane adapters** (lane 6; see "What each step now starts"). Untested on
   hardware, for the machine test or the first round to show: the `launchctl print` fields D2 parses; a live
   install and uninstall through the program courier; live arm and t0 refusal records; a lost session after a
   restart; the wake job (`claude -p` from launchd); `gh` mail; the 4 h harvest timeout under the live runner.
2. **The block-6 registration directory** `configs/b6/registration/` (acceptance.json in
   `joulewise.b6_acceptance_registration.v1`, identity_pins.json, sizing_b5.json, optional
   precheck_thresholds.json) is where the pre-check, the smoke desk and the session harvest all read the
   registration (`joulewise.b6.registration.DEFAULT_DIR_RELATIVE`). Since lane 6 the pins and sizing are
   committed copies of block 5's and the pack registrations name `configs/b6/flag_catalog_b6.json`;
   `acceptance.json` (S-4 to S-9) is still absent and the packs are still `draft`. The registration seat writes
   the one and flips the other.
3. **Effects of the driver's codes** are set in the block-6 catalog from the design texts (agent overlap and a
   sleep inside a run exclude the run; a run skipped at the wait cap or budget is excluded; the rest disclose;
   `idle.waited` discloses until test M2). Since `dd9a9be35` the pack registrations' `flag_effects` no longer
   decide counting; the loop counts from the acceptance verdict, which reads the catalog.
4. **Ledger seed.** This page seeds block 6 from block 3's terminal ledger (row 402, the pin committed here).
   Carrying block 5's later captures would mean reading the block-5 clone's `runs/` directory, which the block-5
   blinding rule of the integration brief names; the orchestrator decides whether that read is allowed.
5. **Closed at `b2837ba38`: one harvest path.** Smoke and session both run `scripts/harvest_b6_session.py` with the
   block-6 catalog. The machine test is still the first run of it on a real block-6 archive (harvest lane L4).
6. **Closed at `e81e60530`: review of the integration's own commits.** A Sol 6.1 finder and the stage-3 director
   reviewed the seven commits on `696164b31`; four findings, all fixed (`fix/2026-10-15-b6-s3-review`). Dispositions:
   `/Users/edr/night-archive/b6-build/stage3/DISPOSITIONS-integration-review.md`.
7. **Closed at `dd9a9be35`: cold passes.** Fable 5.1 and Opus 5.5 ran blind executing passes on `850265137`; their
   three refusal-class findings survived re-execution and are fixed (row 7), with an executing re-check by Opus 5.5.
   Dispositions: `/Users/edr/night-archive/b6-build/stage2/DISPOSITIONS-cold.md`.
8. **Closed at stage 3: the pin's review list.** `configs/b6/executing_reviews.json` lists every commit since
   main's `3bb305d7a` that changed a number-bearing file (`joulewise.b6.registration.NUMBER_BEARING_PATHS`), with its
   executing reviews and their papers; `code_check` on the candidate pin with `registered_commit` = `3bb305d7a` reports
   no unreviewed path (stage-3 dispositions). Any later commit to a number-bearing file needs its own row.
9. **Second cold passes (stage 3).** Fable 5.1 and Opus 5.5 ran blind executing passes on `850265137..696164b31`;
   Opus's one refusal-class finding (a chain stop left the calibration bracket open and the next session's plan
   write held the loop) survived re-execution and is fixed (row 8). Dispositions:
   `/Users/edr/night-archive/b6-build/stage3/DISPOSITIONS-cold.md`.
10. **For the machine test (hardware only):** besides open issue 1's list, a real `launchctl bootout` of the injector
   (the SIGTERM path), the rendered courier and PATH of the night and dead-man jobs on the real block-6 plan, and,
   if the faults allow, one chain stop followed by the desk's bracket close on the real ledger.
11. **Still before round 1:** `acceptance.json` from the quiet-machine measurements (registration S-4 to S-9); the
   three pack registrations flipped from `draft`; the registration through its cold gate; the pin (S-1, with the
   catalog digest S-3 and pins S-18) and the 40-minute machine test on it. CI does not run on this branch (pushes to
   main and pull requests only); the local whole suite stands in for it.
