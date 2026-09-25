# OSCTX-MVP-01 v2.4: stage 0 moves into the unattended session; live-integration defects

Written 2026-09-24 ≈21:40 PDT. No verdict data exist: stage 0 feeds sizing only.

## What the attended stage-0 attempts showed

Two attempts ran with agents active: the magistrate's A291 bench verification and Codex seats. The first crashed after block 1 on the SH cleanup. The second crashed after its first cell on the survivor check. In total 6 production runs completed:

| Run | E (J/token) | R (tok/s) | Idle baseline W (mean ± sd) | Drift bound J | Anchor |
|---|---|---|---|---|---|
| attempt 1 I r1 | 0.4041 | 84.85 | 5.90 ± 0.53 | 37.1 | 2.2 ms |
| attempt 1 I r2 | 0.4635 | 85.51 | 0.29 ± 0.76 | 58.0 | 1.2 ms |
| attempt 1 SH r1 | 0.3739 | 83.67 | 1.94 ± 2.67 | 87.0 | 4.0 ms |
| attempt 1 SH r2 | 0.3884 | 83.73 | 0.47 ± 1.27 | 82.5 | 1.9 ms |
| attempt 2 I r1 | 0.3923 | 84.69 | 5.33 ± 3.02 | 55.9 | 2.0 ms |
| attempt 2 I r2 | 0.3645 | 84.54 | 5.42 ± 1.24 | 55.0 | **unresolved** |

- **R is stable to about 1 %.** **E swings about 25 %**, and the swing tracks the idle baseline, which ranges from 0.3 to 5.9 W with within-baseline sd up to 3 W. Drift bounds are 18–45 % of net energy.
- **In the attended state, E's spread is dominated by agent CPU landing in the 30 s idle baseline.** This is the "lagging processes" mechanism, measured.
- **The attended spread therefore cannot size the unattended stage.** Astra's caution, that attended spread is not presumed conservative, was right, in the other direction: it is far too pessimistic to be informative.

## Amendments

- **D1. Stage 0 runs in state U**, as the first step of the unattended session, with all agents drained. The design is unchanged: 3 blocks of (I, SH), 2 runs per cell, excluded from every verdict. After it, the lead runs `analyze power`, freezes the U1 block count (a multiple of 6) and runs_per_cell, records the freeze in this folder and commits it, then starts U1. If the frozen size would take > 3 h, the lead stops and reports instead.
- **D2. Network time is paused per stage, as production does it.** The runner calls `sudo -n /usr/sbin/systemsetup -setusingnetworktime off` at stage start and `… on` on every exit path (trap), through the installed sudoers rule `scripts/joulewise-network-time.sudoers`. Both calls are logged.
  - Evidence: attempt 2 I r2 was unanchored with detail `wall_minus_monotonic_span_exceeded`, 23.8 ms, which is a wall-clock step during the capture. Production's anchor method refuses such captures, and the v2.3 validity rule correctly invalidated the cell.
- **D3. The survivor proof checks owned processes, not path strings.** After bootout, the runner proves that the job's recorded pid and its process group have no members (`pgrep -g`), and that `launchctl print` fails. The old `pgrep -f <cell_dir>` matched any process whose argv mentioned the path. It false-positived on a read-only seat inspecting the live folder.
- **D4. SH cleanup.** It reaps first and proves survivors with `pgrep -g`, because macOS returns EPERM from killpg on a group holding only exited members (bench fix bb… on the build branch).
- **D5. A live rehearsal before real data.** Before stage 0, one full stage-0 block runs with `runs_per_cell = 1` into a rehearsal directory, and its data are discarded. This exercises every live path: launchd I, SH, NTP pause and restore, cleanup, analysis. Three live-only defects in one evening show that offline tests cannot stand in for this.
