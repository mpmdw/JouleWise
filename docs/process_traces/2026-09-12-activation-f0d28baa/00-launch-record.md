# Activation f0d28baa — launch record (2026-09-12 03:46 PDT)

- Activation `f0d28baa-84fd-4d38-a7bb-4374f9ec9482`, watchdog attempt 27, claude pid 22790, launched 03:46:04 PDT after `b02193d2` exited `usage_exhausted` about fifteen minutes into its run.
- Heartbeat written first (`/Users/edr/night-custody/magistrate/heartbeat`, ts 1789209977); launch email `1a0953b6f2c742bf` on thread `1a0800cdb282c3f1`; `notice.ack` written. `notice_pending` = `[]`; directives `[]`; no `standdown.request`, no `STOP`; remote stop CLEAR.
- Thread re-read (METADATA_ONLY): Ed's last inbound remains 2026-09-10 23:05Z → no NO.
- **Night untouched:** frozen triple `(d079-epoch-25g83-derivation-n1-20260913, /Users/edr/JouleWise-measurement-20260913-derivation, f90cb8c0…)` re-verified by `git rev-parse HEAD` (read-only); `launchctl list` shows `com.joulewise.night`, `com.joulewise.night.deadman`, `com.joulewise.magistrate`. t0 2026-09-13 02:56 PDT. No night work this activation; exit on the watchdog's 02:31 09-13 request.
- Canonical `/Users/edr/code/JouleWise` local `main` sits at 1d4045b4 (behind origin/main ace4cc3c); left alone by rule. One `git fetch origin main` was run there at launch before the fence was re-read; no ref of the canonical checkout moved. All later git work is in linked worktrees.
- Inherited state from b02193d2: both Astra seats' `.status` files read `RUNNING` but no codex process survived; seat-01 (A184) left a complete-looking but unverified draft dirty in `/Users/edr/code/JouleWise-wt-a184` (5 files, +53/−1); seat-02 (A177) left `/Users/edr/code/JouleWise-wt-a177` clean.
- This activation: bookkeeping worktree `/Users/edr/code/JouleWise-wt-bk-f0d28baa` (branch `bookkeeping/2026-09-12-activation-f0d28baa` from origin/main ace4cc3c); scratch `/tmp/magistrate-f0d28baa/`.
  - seat-01 = A184 resume+verify seat in wt-a184 (brief 01 → report 02), preserving the inherited dirty draft.
  - seat-02 = A177 fresh seat in wt-a177 (brief 03, verbatim from b02193d2 → report 04).
- Gate plan: A184 changes the exit table in `docs/contracts/calibration_ledger_append.md` (contract change) → paired refuters with distinct lenses before PR; A177 is tests/fixtures only → single refuter.
