# 01 — Harvest, uninstall and retirement record: `rehearsal-20260916c` (REHEARSAL_STUB), activation `0bd12d79`, 2026-09-16

Harvested per NIGHT_HANDBACK §Next lane at H `be221f6a` after the completion
boundary (03:45:00 PDT) with `courier.sent` present. Every time below is
clock-read from the files named; nothing in this record is estimated.

## Frozen triple (from the plan and the relaunch prompt)

| Field | Value |
|---|---|
| `plan_id` | `rehearsal-20260916c` |
| `root` | `/Users/edr/JouleWise-measurement-rehearsal-20260916c` (HEAD `be221f6a886498f62154faac0b5da14cb66616a1`, tree clean at the uninstall) |
| `head` (H) | `be221f6a886498f62154faac0b5da14cb66616a1` |
| custody root | `/Users/edr/night-custody/rehearsal-20260916c` (now retired, see below) |
| t0 / window / completion | 1789554300 (03:25:00 PDT) / 900 s / 1789555500 (03:45:00 PDT) |

## What the night did (read from `night.log`, `night/result.json`, `night/receipt.json`)

- `night driver started` 03:25:00.821 PDT. Gate verdict `REFUSED`, reason
  `night_refused_agent_present`; the raw `pgrep -lf "codex|claude|t3"` census
  returned Ed's interactive Claude session (pid 7066, `joulewise-95`), its two
  `codex mcp-server` processes (7086, 7094) and that session's zsh wait loop
  (9850, a `sleep 30` loop until 03:35). Two census rows in `censuses.jsonl`
  (the gate's and the driver's), `census_count` 1.
- The stub still ran, as the handback said it would for this class:
  `chain.started` pid/pgid 10755 at 1789554300.847, `chain.exited` exit 0 at
  1789554303.118, `chain.stdout.log` = `REHEARSAL`, `chain.stderr.log` empty.
  `result.json`: schema `joulewise.unattended_night_result.v1`, verdict
  `REHEARSAL_ONLY`, `chain_exit_code` 0, `aborted_reason` null,
  `receipt_class` REHEARSAL_STUB, seven artifacts with SHA-256.
- `receipt.json` (`joulewise.unattended_night_receipt.v2`): verdict `REFUSED`,
  `refusal.reason night_refused_agent_present` with the census output as
  evidence; C2 `NOT_APPLICABLE` (`no_pack_by_design`); C1, C3, C4, C5 `FAIL`.
  C5's `measured` block carries every pin and they all match (driver checkout,
  measurement checkout and plan head all `be221f6a…`, t0 1789554300, observed
  1789554300.82); the status is FAIL because the receipt marks every
  condition FAIL after a refusal by design (`joulewise/night_gate.py:543`,
  "not evaluated after refusal" on C1/C4). Observation, not a defect.
- Courier: `courier.attempts.jsonl` attempt 1 started 1789554310.24,
  heartbeat seen (pid 10900, ts 1789554318), sent true, no error.
  `courier.sent`: Gmail message `1a0a9c0fd1fc101e` at 1789554397 (03:26:37 PDT),
  pid 11000, to Ed's address. `launchd.night.out` holds the courier's report
  (harvest deferred to the relaunched magistrate, both plists left installed);
  `launchd.night.err` is EMPTY (0 bytes).
- Results branch `night-results/rehearsal-20260916c` on origin: `27e3855f`,
  `bb7c1d55`, `558d7b83` (fetched 03:5x PDT from the register worktree).
- `launchctl print` for `com.joulewise.night` before the uninstall: runs 1,
  last exit code 3 (`run_night.py`: 3 = refusal). Dead-man never fired
  (04:45 > completion).

**Acceptance (handback §Next lane):** `REHEARSAL_ONLY` with a recorded
`night_refused_agent_present` hit and the stub completing — MET;
`chain_exit_code` 0 — MET; EMPTY `launchd.night.err` — MET. No crash, no
`night_probe_error`, no installer or launchd irregularity. The night notice
thread `1a0a99fa2717d749` carried only the two magistrate-sent messages at
03:5x (no NO from Ed).

## Byte-exact preservation (03:53:09–03:53:12 PDT)

- `lstat` inventory (size, mtime, path; `results-clone/` excluded) taken
  BEFORE anything else:
  `/Users/edr/night-archive/rehearsal-20260916c-harvest-20260916.lstat-inventory.txt`
  (15 files; copy in `01-harvest-evidence/lstat-inventory.txt`).
- `cp -Rp` of the whole custody root to
  `/Users/edr/night-archive/rehearsal-20260916c-harvest-20260916`;
  `SHA256SUMS` (15 files, `results-clone/` excluded) written from the copy and
  checked against the live root with `shasum -c`: 15 OK, 0 non-OK (copies in
  `01-harvest-evidence/`). First write of `SHA256SUMS` listed itself
  (16 lines, one unreadable); rewritten without itself before the check that
  counts. `results-clone/` (248 MB) compared with `diff -qr`: identical.

## Uninstall (03:53:50 PDT)

FROM the clone at `be221f6a`: `scripts/install_night_agent.sh --plan
/Users/edr/night-custody/rehearsal-20260916c/night_plan.json --uninstall` →
rc 0 (03:53:51). `launchctl list | grep joulewise` → `com.joulewise.magistrate`
only; both `com.joulewise.night*.plist` gone from `~/Library/LaunchAgents`
(`01-harvest-evidence/launchctl-after-uninstall.txt`); clone tree clean.

## Retirement (record-48 procedure)

- Plan root: inventory re-taken and `cmp` identical to the harvest inventory;
  `mv` to `/Users/edr/night-archive/rehearsal-20260916c-plan-root-retired-1789556074`
  (03:54:34 PDT); inventory re-taken after the move, `cmp` identical; the 15
  checksums re-verified in the new location (15 OK). Discoverable plans
  (`~/night-custody/*/night_plan.json`) after: 0. Watchdog `ACTIVE`
  (transition_seq 163) throughout. Nothing inside the root was altered.
- Lapsed candidate `rehearsal-20260916` (H `cf249594`, never published):
  staging dir (10 files) checksummed and moved to
  `/Users/edr/night-archive/rehearsal-20260916-staging-lapsed-1789556131`
  (10 OK); its empty custody root `~/night-custody/rehearsal-20260916` (empty
  `night/`) removed with `rmdir`.
- This plan's staging dir `~/night-plan-staging/rehearsal-20260916c` (attempt
  1 evidence + rendered agents, 13 files, all duplicated in activation
  83d93f5a's record 01) checksummed and moved to
  `/Users/edr/night-archive/rehearsal-20260916c-staging-1789556658` (13 OK).
- Stub clones: `rm -rf` of the three clean stub clones
  (`JouleWise-measurement-rehearsal-20260916` at `1f721fbf`, `…20260916b` at
  `cf249594`, `…20260916c` at `be221f6a`; each head on `origin/main`, each
  tree clean) was REFUSED by the Claude Code permission classifier, the same
  refusal the 2026-09-12 courier met. All three are RETAINED unchanged; they
  hold nothing that is not on origin and Ed may delete them (~750 MB each).
- The unused derivation clone `/Users/edr/JouleWise-measurement-20260916-derivation`
  (HEAD `3c8bd220`, clean, never a measurement root of a published plan) was
  moved to `/Users/edr/night-archive/JouleWise-measurement-20260916-derivation-unused-3c8bd220-1789556506`
  so that the inventoried path is free for the fresh clone at the equivalence
  night's H (record 02).

## Findings and registrations

- **F1 (design, no action).** A refused receipt marks C1/C3/C4/C5 FAIL even
  where the measured pins match; the result record, not the receipt, carries
  the stub's completion. Noted for NIGHT-HANDBACK-GLOSS-01's wording pass.
- **F2 (registered on WATCHDOG-STALE-EXIT-CLASS-01).** Live again: the
  predecessor `100ac5da` exited clean (events.jsonl sequence 160, 03:16:23
  PDT) and `state.json` at this launch (03:49) still read `last_exit_class`
  `usage_exhausted`. The peer confirmed in code that the clean-exit branch
  (`scripts/magistrate_watchdog.py:1714-1723` at `92e3a4e7`) never writes the
  field; only `apply_backoff` (`:1372`) does.
- **F3 (registered on NIGHT-HANDBACK-GLOSS-01).** The shared first-use block
  still says "25 minutes before t0" and "t0 − 85 minutes"
  (`docs/process/NIGHT_HANDBACK.md:55-59`,
  `docs/phase_2/derivation_night_runbook.md:1622-1626`) while the merged
  constants are 8 and 10 minutes (`magistrate_watchdog.py:86`,
  `run_night.py:75`).
- **Lane PHASE-PARTITION-INVARIANT-01 registered (kernel rank 218).** From the
  interactive session's relay (04:0x PDT) of Ed's 03:48 question about
  Vishakha Ramani, "The System Had the Final Word" (ACM SIGARCH blog,
  2026-09-09, https://www.sigarch.org/the-system-had-the-final-word/): an
  executed partition invariant (disjoint, covering, sequenced) over per-phase
  energy intervals before Paper C's phase numbers. The peer's other two
  candidates are recorded here as doc edits for their owners, not lanes:
  (a) cite the article in the prospectus methodology and the fixed-difficulty
  research question (their fixed-load matched replays are the analogue of our
  fixed-difficulty repeats; their leaks were caught only where a result could
  be checked against a concrete record, a precedent for refusal-as-record);
  (b) horizon leg: disaggregated prefill/decode placement is measured by
  goodput only in that work, nobody measures energy per request across the
  placement choice, and a BLIS-style simulator calibrated with measured
  per-phase energy is the plausible bridge from the one-Mac instrument to
  fleet-level placement questions (heterogeneous-placement leg; not Paper A/B).
  The prospectus is under an Astra register seat in `JouleWise-wt-register`
  at this write; the citation waits for that seat to land.

## Machine state observed (for the successor plan)

03:55 PDT: load 3.86 / 4.45 / 3.28 with the peer's Astra seat and two Claude
sessions alive; `fseventsd` (pid 101) at 0.0 % CPU, 84 CPU-minutes over the
8 h since the 2026-09-15 19:55 restart — the 09-15 load precondition is
cleared. AC power, 80 %, `powermode 0`, `sleep 0`, `displaysleep 0`;
`sudo -n -l powermetrics` rc 0; `python3.13` = 3.13.1; canonical ledger
`aa806848…` 76 records, head pin sequence 76 / `08456d50…94d7` unchanged.

## Next exact action

Record 02: the equivalence night `d079-epoch-25g83-derivation-n1-20260916`
(handback commit H, fresh clone, desk block, notice after the interactive
session exits, arm) — see this activation's `00-launch-record.md` §Work and
NIGHT_HANDBACK §Purpose / §Next lane at H.
