# R0-L3: R0 contention is recorded, not fatal

Lead ruling R0-L3, laptop lead (interactive session 1544c617), 2026-11-07.
Source audit: `docs/research-audits/2026-11-07/proportionality.md` on
`research/2026-11-07-proportionality`, decisions 1 and 2, findings F1-F3 and
section 4 (the R0 case study). Background: `RUN_STATE.md` items 194, 195, 201
and 205.

## Ruling (verbatim)

1. In R0, background-process CPU contention is recorded, not fatal. The SMC capture follows ruling 8's rule. A contaminant sustained at ≥ 0.5 cores for 60 s triggers ONE redo of the capture. A second sustained episode records the capture as `contended` (a flag, with the receipts) instead of aborting R0. Shorter or lower contention (e.g. frauddefensed at 0.09 CPU-s/s for 30-60 s) is recorded in the receipts and flagged in report.md but never refuses. The other check classes (armed-window, LaunchAgent, chain, custody refusals) are unchanged and still refuse.
2. Non-SMC checks record contention as a flag too.
3. scripts/launch_align_r0.py passes --checks and --keep-going through to the runner, with keep-going as the default for desk runs, so a subset run (R0-L1, RUN_STATE 196) is launchable headless.
4. The R0 thermometry classifier (#692) gets the contention flags so its picks can be read with them. No classifier rule changes.

Why: R0's capture is selection data, not a reported number (R0 picks are PROVISIONAL; R1 makes the final selection). Its strict 0.05 CPU-s/s abort has caused most of R0's refusals, from routine macOS jobs that the blocks tolerated under their dwell/redo rules. Chasing daemons does not converge.

## Follow-up rulings on the implementation choices (verbatim)

The lead ruled on the eight questions raised in PR #699 (2026-11-07):

(1) A contaminant is the LARGEST SINGLE PROCESS outside the capture's process tree, at ≥ 0.5 cores (CPU-s/s) sustained over consecutive census windows spanning ≥ 60 s. Exclude kernel_task from the judgement, because our own GPU load step drives it, but record it in the receipts. The aggregate outside-tree figure stays recorded, never judged. Add a failing-first test (an aggregate-only heavy load with no single process ≥ 0.5 must not redo; a single process ≥ 0.5 for 60 s must redo; kernel_task ≥ 0.5 must not).
(2) Keep ≥ 0.5 as ruled.
(3) Accepted.
(4) Accepted.
(5) Accepted: unmeasurable CPU stays an indeterminate refusal (a tooling fault).
(6) Accepted; say in R0_HEADLESS_LAUNCH.md that the deadline must leave room for one redo capture (about 55 min).
(7) After merge, the clean-gap scheduling rule for R0 is dropped; the lead delivers that in RUN_STATE. Mention it in the doc.
(8) #700 is tooling under gate policy rule 2: CI plus its regression test satisfy it. Fill #700's ledger accordingly once CI is green.

## Display ruling (verbatim)

From the magistrate's investigation in `RUN_STATE.md` item 206 (commit
`20413903b` on `main`): the MBP display had been on since 11-05 with
`displaysleep 0`. With the display on, ControlCenter's menu-bar redraws
every 3-4 min wake WindowServer and trip the census; after
`pmset displaysleepnow` those bursts stopped. macOS also starts about 650
background dasd activities per hour on an idle AC Mac. The lead ruled:

(a) before any census-checked segment, the R0 launcher runs `pmset displaysleepnow` (no sudo) and dwells 300 s (one constant), then records the display state in the report (`pmset -g` displaysleep value, `pmset -g log` display transitions during the run, i.e. any display wake). A display wake during the SMC capture is recorded as a flag, never a refusal. (b) The R0-L3 redo rule stays as ruled (one capture redo on a sustained single-process ≥ 0.5-core episode; flag otherwise).

## What the code does

### SMC capture (items 1 and 4)

- `joulewise/align/r0_host.py` `smc_enumeration` runs `scripts/align_smc_enumerate.py`
  with `--contention-policy redo`.
  - If the capture exits 4, it had a sustained episode. The host moves its
    directory to `<output>.rejected1` and records the attempt in the receipt's
    `contention_redo` (argv, exit code, stderr and the episode from
    `contention.json`).
  - It then runs the capture once more with `--contention-policy flag`.
  - Any other exit is not redone. A census refusal (exit 3) stays a `fail`.
- `--contention-policy flag` never aborts on contention. The capture completes
  and `r0.json` carries `contention` with `contended: true` when it had an
  episode.
- The receipt carries `contended`, `contention` and `contention_by_phase`.
  `contended` is a flag: the selection status is the classifier's, unchanged,
  and a contended `pass` still counts toward `complete_r0`.
- `joulewise/align/apple/smc_enumeration.py`:
  - `require_quiet(record_contention=True)` returns measured contention
    instead of raising `NotQuiet`. The default (`False`) is unchanged.
  - `Ruling8Quiet` wraps that census and applies ruling 8.
    - It reads each `CpuQuietProbe` interval: at least 30 s, at the capture's
      5 s census cadence.
    - An interval is heavy when the largest single process outside this
      process tree, excluding `kernel_task`, is at ≥ 0.5 CPU-s/s (follow-up
      ruling 1).
    - Consecutive heavy intervals that touch or overlap form a run. A run
      whose union spans ≥ 60 s is a sustained episode. The episode lists the
      processes that made each window heavy.
    - A flag is recorded for every heavy interval, every interval over the
      0.05 CPU-s/s per-process bar, and every interval whose outside-tree
      aggregate or `kernel_task` is ≥ 0.5. Each flag carries the largest
      process, the aggregate and `kernel_task`. The aggregate and
      `kernel_task` are recorded, never judged.
  - `rank` (#692's classifier) returns the capture's `contention` unchanged,
    and `contention_by_phase`: flagged intervals, heavy intervals, the
    maximum largest-process cores, the maximum outside aggregate and the
    sustained episodes overlapping idle, load and recovery.
    No rule reads them, and the picks are unchanged (regression test).
- The agent, custody, measurement-process and LaunchAgent censuses still
  raise `NotQuiet`. So does an unmeasured CPU interval (host CPU unread or a
  failed snapshot): it is a missing measurement, not contention.

### Non-SMC checks (items 1 and 2)

- `QuietGuard.check` no longer raises `Refused("contaminating CPU contention")`.
  It writes `contention_flag` into that census receipt and appends to
  `QuietGuard.contention_flags`. Nothing latches.
- The armed-window, loaded-LaunchAgent, indeterminate LaunchAgent census,
  agent, chain and custody refusals are unchanged and still latch.
- `r0_runner.execute` attaches each check's new flags to its row as
  `contention_flags`. The report gets a `contention` summary: guard flags,
  flagged checks, SMC `contended`, SMC redos and SMC flagged intervals.
- `report.md` gets a "Contention (R0-L3: recorded, not fatal)" section.

### Display (display ruling, RUN_STATE 206)

- The launcher (`scripts/launch_align_r0.py` `run`, on `main`, PR #700)
  runs `pmset displaysleepnow` after Spotlight is paused, then dwells
  `DISPLAY_SLEEP_DWELL_S` = 300 s before it starts the runner, whose first
  act is a census. A failed `displaysleepnow` is recorded, not refused. It
  hands its record to the runner in `JOULEWISE_R0_DISPLAY_PREP`.
- The runner (`r0_runner.display_summary`, `r0_host.display_census`)
  writes `display` into the report when the run ends: the launcher's record,
  `pmset -g`'s `displaysleep`, the display state at the run's start, every
  `pmset -g log` display transition during the run and
  `display_woke_during_run`.
- A display wake whose time falls inside the SMC check's wall window
  (`wall_window_epoch_s` on the SMC row) sets `smc_display_wake_flag` and
  lists the wake in `smc_display_wakes`. It is a flag, never a refusal.
- `report.md` gets a "Display (R0-L3, RUN_STATE 206)" section.
- An unavailable or failing `pmset` is recorded in `display` and never
  changes a check's outcome.

### Launcher (item 3)

`scripts/launch_align_r0.py` exists only on `main` (the magistrate runs it
from the canonical checkout against the measurement checkout's runner), so
that change is a separate PR into `main`. The runner on this lane already
accepts `--checks` and `--keep-going`.

## Implementation choices, as ruled

- **Quantity (ruling 1).** The largest single process outside the capture's
  tree, `kernel_task` excluded. On this Mac `ps` may not list `kernel_task`
  at all (`joulewise/hazards/contention.py`); when it is listed, its rate is
  recorded. This differs from R1's ruling 8 quantity, which sums all
  background CPU (`busy_cores`).
- **Boundary (ruling 2).** ≥ 0.5, as ruled. R1's `_sustained_busy` uses
  `> 0.5`.
- **Resolution (ruling 3, accepted).** R1 judges one sample per second. R0's
  census gives windows of at least 30 s every 5 s, so "60 s" is the union of
  consecutive heavy windows. A 30 s burst at one full core counts. The bias
  is toward a redo.
- **Abort timing (ruling 4, accepted).** The first episode abandons the
  capture as soon as it is detected. The redo starts at once, and its
  adaptive idle (300 s minimum, up to the 1,200 s settle cap) is its release.
  R1 inserts a G0 release before a heavy redo; R0 has no G0.
- **Unmeasured CPU (ruling 5, accepted).** An unmeasurable CPU interval
  (host CPU unread, a failed snapshot) stays an indeterminate refusal, a
  tooling fault.
- **Time budget (ruling 6, accepted).** Each attempt keeps the 3,300 s
  subprocess timeout. Two attempts fit inside the runner's 7,200 s per-check
  deadline. The desk deadline must leave room for one redo capture, about
  55 min (`docs/process/R0_HEADLESS_LAUNCH.md` on `main`, PR #700).
- **Clean-gap rule (ruling 7).** After this merges, the clean-gap scheduling
  rule for R0 is dropped. The lead delivers that change in `RUN_STATE.md`.
- **Launcher tier (ruling 8).** #700 is tooling under gate policy rule 2: CI
  plus its regression test satisfy its gates.

## Not changed

- The 0.05 CPU-s/s per-process bar, the 30 s interval and the contaminant list
  (`joulewise/prewindow.py`) are unchanged. In R0 they now mark flags only.
- The default `scripts/align_smc_enumerate.py` policy (`refuse`) and the
  default `require_quiet` are unchanged for any other caller.
- R1 and W1 do not call `require_quiet`, `CpuQuietProbe` or `QuietGuard`
  (audit section 1, item 4).

## Interaction with draft PR #694

#694 (the `QuietGuard` background sampler) is unmerged. This change is based
on `lane/2026-11-05-align-pilot10-benign` without it. Expect conflicts in
`QuietGuard.check`, `r0_runner.execute`, `r0.markdown` and
`tests/align/test_r0_host.py`. When rebasing either PR onto the other:

- keep #694's sampler and windows;
- replace its `raise Refused(f"contaminating CPU contention: ...")` with this
  PR's flag;
- drop the `break` on `interval_busy` in its `_cpu_interval`, so every later
  window is still judged and recorded;
- keep its stall, long-window and background-census refusals. They are
  census indeterminacy, not contention.
