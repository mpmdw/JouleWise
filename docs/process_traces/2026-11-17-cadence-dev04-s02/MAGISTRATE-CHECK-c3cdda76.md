# dev-04-s02 (dev-04 second span, L007-L012) Check, magistrate c3cdda76 (headless, Opus 5.5), 2026-11-17 05:53 PST

Item 372 "Check" run as custody `cadence-dev04-s02-postcheck-c3cdda76.sh`: item 380's custody script `cadence-dev04-s01-postcheck-d9ae12c0.sh` with OUT, LEGS, ARG and the worktree changed (diff: four lines; kit sha256 and campaign id unchanged, same kit). PY is the align-pilot2 venv; `ARG=02:00-02:35` (recorded at the arm, RUN_STATE 381). cwd: the span's own worktree `/Users/edr/code/jw-wt/cadence-dev-04-s02` at `2d347f721` (printed). Output: custody `cadence-dev04-s02-postcheck-out-c3cdda76.txt` (130 lines, excerpted below).

Before the Check: no `standdown.request`, no `desk_fence.json`, fence pid 72892 gone, no `com.joulewise.(night|align-r0)` label loaded and no such plist on disk (only `com.joulewise.magistrate`). Receipt `ended` epoch 1794923463.33 (05:51:03 PST). This activation spawned 05:52:57, after the close. No pending notices; no unread mail from Ed; the open directives are standing; none names a stop and none changes this Check. Canonical root fast-forwarded `365cb0395` -> `90a169847` (`origin/main`, read by `ls-remote`; no fetch in the canonical root; nothing armed, no night plist on disk).

measurement_mode NOTE 1: the one FAIL names 83226, 83222 (node codex-mcp-server) and 83223 (npm server-pdf), all children of this magistrate (pid 83202). WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates. Free disk 278 GiB (>= 60).

Intervals (local, from the receipt's attempts): launch 03:23:32 (OUT stamp 11:23:32Z); soak 03:28:46-03:58:46; L007 03:58:47-04:14:46; L008 04:14:47-04:35:38; L009 04:35:39-04:54:39; L010 04:54:39-05:10:56; L011 05:10:57-05:31:56; L012 05:31:57-05:51:02; close 05:51:03. Load redos used 0 of quota 2. No 00:00 crossing.

Maintenance overlap (print only; 55,517 lines): `dasd` 1,334-2,116 lines per 10 min; `backupd` 3-42. **05:00 bucket: `softwareupdated` 2,597, `mobileassetd` 2,045, `XProtectPluginService` 843, `XProtect` 56, concentrated at 05:08-05:09 (a software-update / MobileAsset scan; log lines name macOS 26.7.3 and 27.2.1 and the MacRecoveryOSUpdate asset), inside L010 (04:54:39-05:10:56).** L010 ran with no redo (max busy cores 2.361, the runner's load rule did not fire). Otherwise `mobileassetd` 69 at 03:30, 122 at 03:50, 129 at 05:40. Rule 5 judgment of L010 is left to the desk.

Admission (from each leg_summary): **run 6, admitted 6 of 6**, all `g0_outcome` released, `band_reached` true, start band q0, `os_level_max` 1 (L007) or 2, `pm_nominal` false (as dev-03 and dev-04-s01). Every leg decoded 4,096 tokens, `leg_status` complete.

| Leg | prefill | G0 shape / role | G0 s | span_reference | attempts / contaminated redos | wall / budget |
|---|---|---|---|---|---|---|
| L007 | 2,000 | own / capture | 132.5 | null | 1 / 0 | 959.2 / 1,076 (0.891) |
| L008 | 19,458 | span / consume | 205.0 | L007 a1, not excluded, not redone | 1 / 0 | 1,251.2 / 1,642 (0.762) |
| L009 | 10,000 | span / consume | 213.2 | L007 a1, not excluded, not redone | 1 / 0 | 1,139.9 / 1,547 (0.737) |
| L010 | 2,000 | span / consume | 147.9 | L007 a1, not excluded, not redone | 1 / 0 | 977.0 / 1,467 (0.666) |
| L011 | 19,458 | span / consume | 215.3 | L007 a1, not excluded, not redone | 1 / 0 | 1,259.3 / 1,642 (0.767) |
| L012 | 10,000 | span / consume | 217.2 | L007 a1, not excluded, not redone | 1 / 0 | 1,145.1 / 1,547 (0.740) |

**Consumers against L007's capture: 5 of 5 released** (L008-L012; `g0_reference_source` `cadence-cl-dev-04-l007`, reference record sha256 `0311a7c45acb8b9267a088155543b1b2c1f33c8bd097ed746619a6be4b597f0b`).

RL-150 R1 / RL-158 Q1 print (gates nothing): soak reference TV0h/TV1h 34.234 °C, Tf08 mean over the soak's last 1,200 s 27.69. L007's capture (own `align_window_reference.json`, status captured): TV0h/TV1h 34.235 °C, Tf08 median 27.82. Release readings (TV0h = TV1h; Tf08): L007 34.564, 31.30; L008 35.058, 36.54; L009 35.103, 36.89; L010 34.905, 34.86; L011 35.051, 36.37; L012 35.099, 36.71 (L008-L012 against L007's 34.235). Full lines in the custody output.

Named stops: LEG_OVERTIME none (largest wall/budget 0.891, L007). L007's reference present (no REFUSAL). CONTAMINATED_REDOS: 0 of quota 2. No named stop in the receipt (`fault` false, `error` null); the Air desk builds `stops.json`.

Receipt: rc 0, `cadence-legs-v1.1`, roster L007-L012, `batch_windows` ["02:00-02:35"], legs 6 of 6, load redos 0, span_result MEASURED_OK / COMPLETE / chain exit 0 / "6/6 legs run"; every step rc 0; kit sha `1cc6673d…2228`, frozen commit `2d347f721` and campaign id `cl-dev-04` asserted; feed files hashed equal (meter stream not opened, RL-150 R8); desk bundle = six leg summaries + span/meter.json + span/result.json. **RECEIPT OK.**

Restore lines: steps `restore`, `stop-volumes`, `stop-meter`, `stop-agents`, `close-volumes` all rc 0; after the close: AC powermode 0, no High Power marker, `night.lock` no holder, Network Time Off, kernel frequency word 0, no stray monitor, no root powermetrics, no align-r0 label. Meter: 44,194 polls over 8,839 s, 0 bad, 0 USB errors, proven stopped. Close epoch 1794923463.33.

Journal copy: no marker `/Users/Shared/JouleWise/desk-copy/cq-dev-04-s02-a1.ok` at 05:53; under items 347/348 the MBP offload runs at close + 30 min (06:21:04) if the lead's copy has not landed (custody `offload-dev04-s02-{,run-}c3cdda76.sh`, output `offload-dev04-s02-out-c3cdda76.txt`).

The magistrate reports; it does not decide. dev-04 is now 12 of 12 legs run (dev-04-s01 6, dev-04-s02 6); the hand-read and desk are the lead's (item 372 "After"). No further campaign item is staged, so the standing F0 item (346) applies under its own rules, trigger (c) NO_STAGED after this close.
