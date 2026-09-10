# 30 — Pre-night dead-man firing observed, 2026-09-10 07:00 PDT (rehearsal-20260911, acceptance item 5 evidence)

Observed by headless activation `96bfeca7` (read-only inspection of custody at 07:02–07:05 PDT; nothing in custody was
written, moved or deleted). Baseline at install (arm record 123, 04:10:58): `post-install night/ baseline: []`.

## Facts

```text
/Users/edr/night-custody/rehearsal-20260911/night.log  size=110  mtime_ns=1789048802.092639143  birth=1789048802
2026-09-10T07:00:02.092553-07:00 dead-man fired before the night's completion epoch 1789121760; standing down

/Users/edr/night-custody/rehearsal-20260911/night/launchd.deadman.out  size=0  mtime_ns=1789048801.948138143  birth=1789048801
/Users/edr/night-custody/rehearsal-20260911/night/launchd.deadman.err  size=0  mtime_ns=1789048801.948226143  birth=1789048801
(both files empty; `cat` prints nothing)

launchctl list: com.joulewise.night (0), com.joulewise.magistrate (0), com.joulewise.night.deadman (0) — all still loaded.
```

- The `night.log` line is byte-for-byte the message runbook 67 §Expected observations requires, with its ISO local
  timestamp prefix; the quoted epoch 1789121760 is the completion epoch (t0 + 900 + 300), as the runbook explains.
- `night/` holds exactly two zero-byte files, `launchd.deadman.out` and `launchd.deadman.err`. Their birth time
  (07:00:01.948) precedes the driver's log line (07:00:02.092) by 144 ms: they are the stdout/stderr handles launchd
  opens when it spawns the job, at the `StandardOutPath`/`StandardErrorPath` the installer rendered into the plist
  (`123-arm-evidence/com.joulewise.night.deadman.plist`). The driver's `dead_man` (scripts/run_night.py:1727–) wrote no
  record: `night_dir.mkdir(exist_ok=True)` on the existing directory, no `courier.sent`, no refusal, no result.
- The first rehearsal's harvest record (21i, line 21) already treated the night agent's stream file
  (`night-launchd.night.out`) as the courier transcript, i.e. as launchd's file in `night/` by design.

## Why this needs a ruling before the 09-11 harvest

Synthesis 65 / runbook 67 phrase item 5 as: the dead-man stand-down line precedes the night's verdict line "and
`night/` holds nothing from that dead-man firing. Record any deviation; do not silently exempt a file from this
wording." Checklist 13 repeats: "Dead-man wrote anything into `night/`, including launchd stream files … Item 5 is not
met under its literal criterion; escalate … Do not redefine 'only a log line' or exempt stream files locally."
Literally read, the criterion is unmeetable by construction: launchd creates these two handles on every firing at the
paths the installer chose. The question of whether zero-byte launchd handles are "something from that firing" is an
application of an acceptance criterion, not a process rule; under rule 11 the resident magistrate does not
reinterpret a verdict criterion alone — it goes to a cold gate (packet 31) paired with an Opus refuter, so that the
09-11 activation can accept or refuse item 5 mechanically.

## Not done here

No harvest (the night has not fired); no uninstall; no change to any plan, plist, or custody file.
