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

The loop is in stage 1 because stage 1 cannot run without it: the pre-session check waits while any `claude` or
`codex` process is alive or the keyboard was used in the last 600 s (`joulewise/b6/precheck.py`), so no agent can
run it to a start, and the smoke module leaves launching to the loop (`joulewise/b6/smoke.py`). The loop's
connections to the other lanes (`joulewise/b6/lanes.py` `resolve`) are still stubs; until they are built (open
issue 1 below) the loop starts nothing.

## The measurement checkout (both commands need it)

Built once, by the block-5 post-seal runbook's steps 3 to 5
(`docs/process_traces/2026-10-07-block5-seal/30-post-seal-runbook.md`), with these values:

- **Commit:** a pinned commit of this branch, `P` below (the head after the open issues that matter for the test
  are closed). The checkout is never pulled, fetched or edited afterwards; its only later commits are the ledger
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
- **Registration directory:** `configs/b6/registration/` must be committed at `P` before round 1 (open issue 2).
  The machine test does not need it: it writes its own non-claim one.

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
  `configs/campaigns/v5_claim_25g83/`), the two desk identity files from the live machine, the plan inputs (the
  sealed block-5 threshold block, ALPHA's sizing), the fingerprint, then `joulewise.b6.smoke.prepare`: a fresh
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

It runs the smoke desk (the block-5 harvester, then block 6's acceptance in smoke mode), uninstalls the night
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

**What must be true first, or the loop holds and starts nothing** (it says why in `state.json` and by one mail):

1. The loop's lane adapters exist on the pinned commit (open issue 1). Until then a tick with registered packs
   holds with `lane_missing:driver`; with draft packs it idles (`pack_not_open`).
2. `configs/b6/packs/{alpha,beta,gamma}/registration.json` are `registered`, committed and valid (after a tick,
   `/opt/homebrew/bin/python3.13 -B "$M/scripts/b6_loop.py" status` shows `pack_not_open` with each refused
   pack's reasons; today all three say `draft`), and `configs/b6/registration/` is committed (open issue 2).
3. The machine test passed on the same commit.
4. `gh` is logged in for `mpmdw/JouleWise` (the mail transport); `loop.json` `wake_argv` names the orchestrator's
   wake command if the loop should start one (empty today: a wake is a record and a mail).
5. Nothing else is installed: `launchctl list | grep com.joulewise` prints nothing, and no agent is alive when
   the first session's pre-check runs (it waits otherwise; it does not fail).

To stop: `/opt/homebrew/bin/python3.13 -B "$M/scripts/b6_loop.py" hold` (the loop holds after its current step; a running
collection is never killed), then `launchctl bootout gui/$(id -u)/com.joulewise.b6loop` once `collection.active`
is gone.

## Decisions made at the integration (the texts determine them)

- **The loop joins stage 1**, inert until its adapters exist (above).
- **Driver M2 needs no change for the replications.** The driver lane asked that `window_max_s` add the pause
  limit and the session wait budget (7,200 + 7,200 s). `joulewise/b5/plan.py` sets `window_max_s` to the pack's
  programmed span plus the 3,300 s arm cap, rounded up to a minute: 110,220 s (30.6 h) for ALPHA, 112,620 s for
  BETA, 99,060 s for GAMMA (`configs/campaigns/v5_claim_25g83/sizing_b5.json`, whose member allowance is about
  595 s against a measured 135 to 150 s per run). A 125-run session takes about 6 h; with both budgets spent it
  takes about 10 h, 20 h inside the deadline and inside the chain's 24 h calibration horizon. A pack whose
  sizing lacks that slack must add the budgets in its own sizing.
- **One block-6 registration directory**, `configs/b6/registration/`, for the pre-check, the smoke desk and the
  session harvest (open issue 2); a registration the pre-check cannot read is the flag
  `precheck.acceptance_unavailable`, not a stop.
- **Block-6 codes live in the block-6 catalog** (`configs/b6/flag_catalog_b6.json`, built by
  `scripts/build_b6_flag_catalog.py`), never in block 5's sealed catalog: the driver's seventeen codes and the
  loop's three were added there, and the loop reads it.

## Open issues

1. **The loop's lane adapters are not built.** `joulewise/b6/lanes.py` `resolve()` returns stubs for the
   pre-check (P1, P2), the driver (D1 prepare, D2 launch and status), the smoke and session desk (S1, K1), the
   harvest (H3) and the analysis (A1). The loop spec (`/Users/edr/night-archive/b6-build/loop/SPEC.md` section 4)
   assigned D1 and D2 to the driver lane, which did not build them. They are a lane of their own: plan inputs
   from the block-6 registration (the block-5 bench helpers `b5_plan_inputs.py` and `b5_desk_identity.py` ported
   into the repository), t0 chosen at launch rather than at `prepare_session` (the plan writer binds t0, and the
   loop prepares before the pre-check and the 30-minute NO window), install and uninstall through
   `install_night_agent.sh`, the ledger pin advance after each chain, the `Refused` result for an arm or t0
   refusal, K1 as `scripts/harvest_b6_session.py` plus `joulewise/session_structure.py` plus
   `joulewise/desk_compress.py`, the production `wake_argv`, and `--courier-bin` on every install (the installer
   accepts it since this integration; without it the night job runs block 5's `claude -p` courier after the
   chain, while design 6.4 says block 6's mail is sent by a program, the loop's mailer).
2. **The block-6 registration directory** `configs/b6/registration/` (acceptance.json in
   `joulewise.b6_acceptance_registration.v1`, identity_pins.json, sizing_b5.json, optional
   precheck_thresholds.json) is where the pre-check, the smoke desk and the session harvest all read the
   registration (`joulewise.b6.registration.DEFAULT_DIR_RELATIVE`). The registration seat writes it, and the
   three pack registrations should name `configs/b6/flag_catalog_b6.json` (they name block 5's sealed catalog,
   which the block-6 catalog contains, so they validate either way).
3. **Effects of the driver's codes** are set in the block-6 catalog from the design texts (agent overlap and a
   sleep inside a run exclude the run; a run skipped at the wait cap or budget is excluded; the rest disclose;
   `idle.waited` discloses until test M2). The registration may set others through `flag_effects`.
4. **Ledger seed.** This page seeds block 6 from block 3's terminal ledger (row 402, the pin committed here).
   Carrying block 5's later captures would mean reading the block-5 clone's `runs/` directory, which the block-5
   blinding rule of the integration brief names; the orchestrator decides whether that read is allowed.
5. **The smoke desk harvests with block 5's harvester** (`scripts/harvest_b5_window.py --prepare-desk`, the plan's
   catalog), then judges with block 6's acceptance in smoke mode, while a session's desk is to use
   `scripts/harvest_b6_session.py` (block-6 catalog and registration pins). The block-5 harvester records codes
   its catalog lacks as unclassified and goes on, so the smoke still runs; the adapter lane should make the two
   desks harvest the same way. The machine test is the first run of either on a block-6 archive (harvest lane L4).
