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
    - An interval is heavy when the host's busy CPU outside this process tree
      (`outside_aggregate_cpu_s_per_s`) is ≥ 0.5 cores.
    - Consecutive heavy intervals that touch or overlap form a run. A run
      whose union spans ≥ 60 s is a sustained episode.
    - Every heavy interval, and every interval over the 0.05 CPU-s/s
      per-process bar, is a flag with its top processes.
  - `rank` (#692's classifier) returns the capture's `contention` unchanged,
    and `contention_by_phase`: flagged intervals, heavy intervals, maximum
    outside cores and sustained episodes overlapping idle, load and recovery.
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

### Launcher (item 3)

`scripts/launch_align_r0.py` exists only on `main` (the magistrate runs it
from the canonical checkout against the measurement checkout's runner), so
that change is a separate PR into `main`. The runner on this lane already
accepts `--checks` and `--keep-going`.

## Implementation choices for the lead to confirm

- **Quantity.** "A contaminant sustained at ≥ 0.5 cores" is implemented as
  ruling 8's own quantity: all busy CPU outside the measured tree, as R1's
  `busy_cores` sums it (`joulewise/align/apple/r1_runtime_contract.py` on
  `lane/2026-11-06-v4-r1-integrated`). It is not limited to one named
  process. This is at least as strict as any single process. It includes
  `kernel_task` and `WindowServer`, which the GPU load step itself may raise.
  The worst case is one redo and a `contended` flag, never a refusal.
- **Boundary.** The ruling says ≥ 0.5; R1's code uses `> 0.5`
  (`_sustained_busy`). The code follows the ruling, ≥.
- **Resolution.** R1 judges one sample per second. R0's census gives
  windows of at least 30 s every 5 s, so "60 s" is the union of consecutive
  heavy windows. A 30 s burst at one full core averages 0.5 over that 60 s
  union and counts. The bias is toward a redo.
- **Abort timing.** The first episode abandons the capture as soon as it is
  detected, not at the end of the capture. The redo starts at once. Its
  adaptive idle (300 s minimum, up to the 1,200 s settle cap) is its release.
  R1 inserts a G0 release before a heavy redo; R0 has no G0.
- **Time budget.** Each attempt keeps the 3,300 s subprocess timeout. Two
  attempts fit inside the runner's 7,200 s per-check deadline. A desk deadline
  should leave room for one extra capture (at most about 55 min).

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
