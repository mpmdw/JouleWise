# dev-03-s02 (dev-03 remainder, L004-L012) Check, magistrate 1292492b (headless, Opus 5.5), 2026-11-16 11:21 PST

Item 366 "Check" run from its two fenced blocks (maintenance line; the Check proper with receipt asserts, the RL-150 R1 / RL-158 Q1 print, restore and measurement_mode lines), as custody `cadence-dev03-s01-postcheck-d59960c1.sh` with OUT, LEGS and the worktree changed (diff: three lines), plus the stray-monitor, root-powermetrics, measurement_mode verify and `df` lines. PY is the align-pilot2 venv; `ARG=02:00-02:35` (recorded at the arm, RUN_STATE 369). cwd: the span's own worktree `/Users/edr/code/jw-wt/cadence-dev03-rest` at `2d347f721` (printed). Script: custody `cadence-dev03-s02-postcheck-1292492b.sh`; output: custody `cadence-dev03-s02-postcheck-out-1292492b.txt` (158 lines, excerpted below).

Before the Check: no `standdown.request`, no `desk_fence.json`, fence pid 95380 gone, no `com.joulewise.(night|align-r0)` label loaded and no such plist on disk (only `com.joulewise.magistrate`). Receipt `ended` epoch 1794856578.70 (11:16:18 PST). This activation spawned 11:19:56, after the close. No pending notices; no unread mail from Ed; the open directives (#587, #422, #421 and older) are standing; none names a stop and none changes this Check. Canonical root already at `origin/main` `35a02b4dc`. Slip: one `git fetch` in the canonical root at start, before reading the pointer (refs only; HEAD and tree unmoved; nothing new fetched).

measurement_mode NOTE 1: the one FAIL names 10483, 10479 (node codex-mcp-server) and 10480 (npm server-pdf), all children of this magistrate (pid 10464). WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates. Free disk 62 GiB (>= 60).

Intervals (local, from chain-stages and leg_summary): launch 07:52:04 (OUT stamp 15:52:04Z); dwell 07:52:20-07:57:20; soak 07:57:21-08:27:21; L004 08:27:22-08:46:15; L005 08:46:16-09:02:38; L006 09:02:39-09:23:34; L007 09:23:35-09:42:46; L008 09:42:47-09:59:10; L009 09:59:11-10:20:06; L010 10:20:07-10:36:21; L011 10:36:21-10:57:18; L012 10:57:19-11:16:17; close 11:16:18. No load redo (quota 2 unused). The span did not cross 00:00.

Maintenance overlap (print only; 73,382 lines): `dasd` 1,154-3,152 lines per 10 min through the span; `backupd` 6-27. Bursts by minute (over 20 lines): `mobileassetd` 208/157/170 at 08:08/08:11/08:24 (soak); `mobileassetd` 1,360 at 09:21 and 34 at 09:26, `mds` 32 at 09:20 (inside L006, 09:02:39-09:23:34); `mobileassetd` 69 at 10:38 (L011); **11:09: `softwareupdated` 2,573, `mobileassetd` 2,045, `XProtectPluginService` 562, `XProtect` 50; `softwareupdated` 23 at 11:11 (inside L012, 10:57:19-11:16:17).** L006 and L012 ran with no redo (`contaminated_redos` 0, admitted). Rule 5 judgment of L006 and L012 is left to the desk.

Admission (from each leg_summary): **run 9, admitted 9 of 9**, all `g0_outcome` released, `band_reached` true, start band q0, attempts 1, `contaminated_redos` 0, `os_level_max` 2, `pm_nominal` false (as dev-02 and the pilot).

| Leg | prefill | G0 shape / role | G0 s | span_reference | wall / budget |
|---|---|---|---|---|---|
| L004 | 10,000 | span / capture | 205.0 | null | 1,133.3 / 1,156 (0.980) |
| L005 | 2,000 | own / capture | 152.9 | null | 982.0 / 1,076 (0.913) |
| L006 | 19,458 | own / capture | 204.1 | null | 1,255.4 / 1,251 (1.004) |
| L007 | 10,000 | own / capture | 221.2 | null | 1,151.8 / 1,156 (0.996) |
| L008 | 2,000 | span / consume | 149.9 | L004 a1, not excluded, not redone | 983.2 / 1,467 (0.670) |
| L009 | 19,458 | span / consume | 211.1 | L004 a1, not excluded, not redone | 1,255.3 / 1,642 (0.764) |
| L010 | 2,000 | span / consume | 145.6 | L004 a1, not excluded, not redone | 973.8 / 1,467 (0.664) |
| L011 | 19,458 | own / capture | 211.1 | null | 1,256.9 / 1,251 (1.005) |
| L012 | 10,000 | span / consume | 213.2 | L004 a1, not excluded, not redone | 1,138.6 / 1,547 (0.736) |

**Consumers against L004's capture: 4 of 4 released** (L008, L009, L010, L012; `g0_reference_source` `cadence-cl-dev-03-l004`, reference record sha256 `3692d95c…fc44` for all four). Every leg decoded 4,096 tokens, `leg_status` complete.

RL-150 R1 / RL-158 Q1 print (gates nothing): soak reference TV0h/TV1h 34.177 °C, Tf08 mean over the soak's last 1,200 s 27.10. L004's capture (own `align_window_reference.json`): TV0h/TV1h 34.201 °C. Release readings (TV0h = TV1h; Tf08): L004 34.808, 33.86; L005 34.896, 34.78 (own ref 34.775); L006 35.046, 36.33 (own ref 34.717); L007 35.096, 36.62 (own ref 34.791); L008 34.906, 34.79; L009 35.041, 36.44; L010 34.918, 35.03; L011 35.050, 36.32 (own ref 34.760); L012 35.093, 36.71. Full lines in the custody output.

Named stops: LEG_OVERTIME none (largest wall/budget 1.005, L011; the stop needs two legs over 1.5 x). L004's reference present (no REFUSAL). CONTAMINATED_REDOS none. No named stop in the receipt (`fault` false, `error` null); the Air desk builds `stops.json`.

Receipt: rc 0, `cadence-legs-v1.1`, roster L004-L012, `batch_windows` ["02:00-02:35"], legs 9 of 9, load redos 0, span_result MEASURED_OK / COMPLETE / chain exit 0 / "9/9 legs run"; every step rc 0; kit sha, frozen commit and campaign id asserted; feed files hashed equal; desk bundle = nine leg summaries + span/meter.json + span/result.json. **RECEIPT OK.**

Restore lines: steps `restore`, `stop-volumes`, `stop-meter`, `stop-agents`, `close-volumes` all rc 0; after the close: AC powermode 0, no High Power marker, `night.lock` no holder, Network Time Off, kernel frequency word 0, no stray monitor, no root powermetrics, no align-r0 label. Meter: 61,197 polls over 12,239 s, 0 bad, 0 USB errors, proven stopped. Close epoch 1794856578.70.

Journal copy: no marker `/Users/Shared/JouleWise/desk-copy/cq-dev-03-s02-a1.ok` at 11:21; the MBP offload (items 347/348) runs at close + 30 min (11:46) if the lead's copy has not landed.

The magistrate reports; it does not decide. dev-03 is now 12 of 12 legs run (pilot 3 + remainder 9); the hand-read and desk are the lead's (item 366 "After").
