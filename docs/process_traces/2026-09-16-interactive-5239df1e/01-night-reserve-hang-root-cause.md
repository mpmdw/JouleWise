# NIGHT-RESERVE-HANG-01: why the 2026-09-16 equivalence night stalled for eleven hours

Interactive session `5239df1e` (Fable 5.1), 2026-09-16 22:46–23:1x PDT, at the machine
after the move, with Ed present. This record establishes the root cause of the stall that
the headless activation e0c58148 left open in
`docs/run_reports/2026-09-16-activation-e0c58148-equivalence-night-stall.md`.
Every fact below was executed in this session unless marked otherwise.

## The stall in one paragraph

The night chain of `d079-epoch-25g83-derivation-n1-20260916` started at 09:45:02 PDT and
entered the reservation step (`scripts/reserve_calibration_window_bracket.py --execute`).
Inside the ledger writer lease (lock file born 09:45:02), the readiness pass verifies the
custody of every historical calibration observation by reading and hashing its governed
artifacts. Thirty-eight of the fifty custody locators in the clone's ledger live under
iCloud Drive (`~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/...`), 190
files, 3,333,856,927 bytes. The reads are not time-bounded: `probe_custody` bounds only the
`exists`/`is_dir` probe to two seconds and then runs the inspect callback synchronously and
unbounded on the caller (its own docstring records this as an accepted race). The Python
that performed the reads was spawned by launchd, not by a terminal. macOS gates file access
under iCloud Drive with a Files-and-Folders consent; a process without a stored decision
blocks inside the open call until a person answers the dialog. Nobody was at the machine.
The user consent database changed at 20:52:04; the readiness pass completed and the ledger
rows 77/78 were written at 20:52:06; Ed's interactive `claude` entered the census at
20:52:13 and the driver terminated the chain at 20:52:19.

## Executed evidence

Machine state at session start (22:46 PDT): on AC power, no `com.joulewise.*` launchd jobs,
no claude processes other than this session's own Codex MCP children, watchdog plist parked.

1. The stall is inside the reservation, not before it or after it.
   `night.log` has three lines, all at 09:45:02 (driver started, gate GO, chain digest
   verified). `night/chain.started` pgid 20946 at epoch 1789577102.83. `night/chain.exited`
   exit_code −15 at epoch 1789617139.04. `operator_logs/derivation-chain.log` (birth
   20:52) holds `session_open` and `chain_start` at 2026-09-17T03:52:06Z only.
   `chain.stdout.log` birth 09:45:02, mtime 20:52:06, 339 lines: line 1 is the pre-reserve
   readiness with `status: ready`, lines 18–335 the `bracket-session-open` receipt with
   `status: reserved`. `chain.stderr.log` (105 bytes) holds only
   `calibration_pre_reserve_authorized`; no `custody_locator_unreachable` line, so no
   two-second probe timed out: the probes passed and the reads blocked.
   Clone ledger: `runs/calibration_observation_ledger.jsonl` mtime 20:52:06; its `.lock`
   sidecar born 09:45.
2. The machine did not sleep. `night/censuses.jsonl`: 1,332 rows, median gap 30.12 s, max
   gap 30.24 s, no gap over 60 s; monotonic span 40,036.38 s against a wall span of
   40,036.21 s between `chain.started` and `chain.exited`. `pmset -g log` for 09:40–21:00
   shows only maintenance-wake and darkwake assertions, no sleep entry.
3. The lease cannot block. `CalibrationWriterLease.acquire` uses
   `fcntl.LOCK_EX | fcntl.LOCK_NB` and raises `LIVE_WRITER_CONTENTION` on
   `BlockingIOError` (`joulewise/calibration_ledger.py`, class at line 3167).
4. What the readiness pass reads. `_custody_reasons` (line 1898) calls `probe_custody` for
   every observation with `_observation_custody_reasons` as the inspect callback, which
   hashes the governed artifacts (`raw/powermetrics.plist`, `events.jsonl`,
   `power_trace.csv`, `instrument_evidence.json`, `manifest.json`). `probe_custody`
   (line 4945, `CUSTODY_PROBE_TIMEOUT_S = 2.0`) bounds only the existence probe; its
   docstring: "a mount can stall between a successful probe and the unchanged, unbounded
   authenticated read ... it does not bound reads."
   Locator census from the clone's ledger: 50 unique custody locators, 38 under
   `~/Library/Mobile Documents/com~apple~CloudDocs/`; walking those 38 trees: 190 files,
   3,333,856,927 bytes; every file exists now; zero `*.icloud` eviction placeholders under
   `JouleWise-backup`; file birth times are all July/August 2026 (iCloud preserves birth
   times across eviction, so this neither confirms nor excludes a download).
5. The release coincides with a consent decision, before Ed's terminal session existed.
   `~/Library/Application Support/com.apple.TCC/TCC.db` mtime 2026-09-16 20:52:04 (the
   database itself is not readable from this shell: "authorization denied"). Ledger write
   20:52:06. Ed's interactive `claude` pid 26787 first appears in the census at 20:52:13
   (last census row of `censuses.jsonl`). The unified log has zero `tccd` lines in
   20:50:00–20:53:00 and zero `bird`/`cloudd`/`Python` lines in 09:45:00–09:46:30 and
   20:51:30–20:52:10 (these subsystems log privately by default; absence is not evidence).
6. This was the first launchd-spawned reservation ever. Every earlier equivalence-night
   candidate was refused at t0 or lapsed unarmed, and the rehearsal nights ran the stub
   chain, which does not reserve. The iCloud locators entered the ledger through the
   historical-import rows after the 2026-09-15 iCloud offload. Terminal-spawned
   reservations (desk dry runs) inherit the terminal's consent and never showed this.
7. Reproduction now, after the decision was stored. A throwaway launchd job
   (`com.joulewise.tccprobe-1789624362`, RunAtLoad, python3.14 from Homebrew) that stats,
   lists, reads and hashes `manifest.json` under one of the 38 iCloud locators completed in
   0.019 s from launchd and 0.001 s from the terminal; booted out afterwards, `launchctl
   list` shows no `tccprobe` job. A stored consent (or an already-materialised file) makes
   the read instant; the hypothesis predicts exactly that after 20:52:04.

## Verdict

Root cause: an unbounded governed-artifact read over iCloud Drive custody, executed inside
the writer lease by a launchd-spawned interpreter without a stored file-access consent,
blocked on a macOS consent dialog until a person answered it. The night path depended on a
human. One item is Ed's to confirm in words: whether he answered a macOS permission dialog
about Python and iCloud Drive (or Files and Folders) at 20:52 on 09-16. If he did not, the
same evidence supports the alternative of an iCloud materialisation wait that ended when he
reached the machine; the cure below covers both, because both are "a night-path read that
can wait on the outside world without a bound".

Two cures, both mechanism, neither physics/evidence/pre-registration:

- The night path never blocks on a human or on the network: custody verification on the
  night path gets a wall-clock budget and a stall becomes a named refusal before the window
  ends; historical custody outside the measurement root is either not read on the night
  path or exercised from a launchd job at arm time, with the owner present, so any consent
  surfaces then. Lane `NIGHT-RESERVE-HANG-01` (named `NIGHT-RESERVATION-STALL-01` in the
  e0c58148 record; same defect).
- Operational precondition, recorded for the runbook: the plan interpreter
  (`measurement_root/.venv/bin/python` by default, per `install_night_agent.sh`) must hold
  the file-access grant; a Homebrew Python upgrade changes the binary's code identity and
  resets it. This precondition is a guard, not the cure.

Sibling lanes from the same night: `DRIVER-REFUSAL-COLLISION-01` (second `refusal.json`
writer crashes the driver) and `NIGHT-STALL-WALLCLOCK-ABORT-01` (nothing terminates a
stalled chain before an agent census hit; the chain's own window guard sits after the
reservation).

## Not done here

No code changed. No design chosen: the cure shape (bounded reads versus keeping historical
custody off the night path) is design-bearing and goes to a pre-decision consult before
implementation. Ed's verbal confirmation of the dialog is requested in the session's closing
message.
