# dev-04-s01 (dev-04 first span, L001-L006) Check, magistrate d9ae12c0 (headless, Opus 5.5), 2026-11-17 02:54 PST

Item 367 "Check" run from its two fenced blocks (maintenance line; the Check proper with receipt asserts, the RL-150 R1 / RL-158 Q1 print, restore and measurement_mode lines), as custody `cadence-dev04-s01-postcheck-d9ae12c0.sh`: item 366's custody script `cadence-dev03-s02-postcheck-1292492b.sh` with OUT, LEGS, ARG, the worktree, the kit sha256 and the campaign id changed (diff: six lines; the two assert lines now equal item 367's text). PY is the align-pilot2 venv; `ARG=13:14-13:15` (recorded at the arm, RUN_STATE 379). cwd: the span's own worktree `/Users/edr/code/jw-wt/cadence-dev-04-s01` at `2d347f721` (printed). Output: custody `cadence-dev04-s01-postcheck-out-d9ae12c0.txt` (139 lines, excerpted below).

Before the Check: no `standdown.request`, no `desk_fence.json`, fence pid 58523 gone, no `com.joulewise.(night|align-r0)` label loaded and no such plist on disk (only `com.joulewise.magistrate`). Receipt `ended` epoch 1794912643.42 (02:50:43 PST). This activation spawned 02:52:46, after the close. No pending notices; no unread mail from Ed; the open directives (#587, #422, #421 and older) are standing; none names a stop and none changes this Check. Canonical root at `origin/main` `365cb0395` (read by `ls-remote`; no fetch in the canonical root).

measurement_mode NOTE 1: the one FAIL names 70448, 70444 (node codex-mcp-server) and 70445 (npm server-pdf), all children of this magistrate (pid 70429). WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates. Free disk 238 GiB (>= 60).

Intervals (local, from the receipt's attempts): launch 00:01:53 (OUT stamp 08:01:53Z); soak 00:07:15-00:37:15; L001 00:37:16-00:55:58; L002 00:55:58-01:16:44; L003 01:16:44-01:33:02; L004 01:33:02-01:52:17; L005 01:52:18-02:08:39; L006 a1 02:08:39-02:29:35 (contaminated, redone, `cpu_load`, max busy cores 3.638); L006 a2 02:29:36-02:50:42; close 02:50:43. Load redos used 1 of quota 2. The span did not cross 00:00 (launched 00:01:53).

Maintenance overlap (print only; 63,974 lines): `dasd` 1,288-2,018 lines per 10 min through the span, 5,175 in 02:00 and 3,267 in 02:10 (minute peaks 1,350 / 2,459 at 02:08 / 02:09); `backupd` 6-33. Bursts by minute (over 20 lines, not dasd): `backupd` 33 at 00:56 (L002 start); **`mobileassetd` 3,651 at 01:21 (inside L003, 01:16:44-01:33:02; L003 ran with no redo)**; **02:08-02:24: `mobileassetd` 171 / 1,152 / 1,191 / 233 / 218 / 217 / 170, `XProtectPluginService` 290 / 39 / 295 / 24 / 24, `XProtect` 48 at 02:15 and 35 at 02:22, `mds` 33 at 02:15 (the OS batch at 02:08:39 predicted at the arm, inside L006 a1, which the runner redid under rule 5)**; `mobileassetd` 379 at 02:46 (inside L006 a2, no redo). Rule 5 judgment of L003 and L006 a2 is left to the desk.

Admission (from each leg_summary): **run 6, admitted 6 of 6**, all `g0_outcome` released, `band_reached` true, start band q0, `os_level_max` 2, `pm_nominal` false (as dev-03).

| Leg | prefill | G0 shape / role | G0 s | span_reference | attempts / contaminated redos | wall / budget |
|---|---|---|---|---|---|---|
| L001 | 10,000 | own / capture | 201.0 | null | 1 / 0 | 1,121.7 / 1,156 (0.970) |
| L002 | 19,458 | own / capture | 202.0 | null | 1 / 0 | 1,245.3 / 1,251 (0.995) |
| L003 | 2,000 | own / capture | 145.7 | null | 1 / 0 | 977.2 / 1,076 (0.908) |
| L004 | 10,000 | own / capture | 221.3 | null | 1 / 0 | 1,155.0 / 1,156 (0.999) |
| L005 | 2,000 | span / consume | 151.9 | L001 a1, not excluded, not redone | 1 / 0 | 980.8 / 1,467 (0.669) |
| L006 | 19,458 | own / capture | 215.3 | null | 2 / 1 (`cpu_load`) | 1,266.1 / 1,251 (1.012) |

Note: the leg_summary `g0_role` reads `capture` and `g0_shape` `own` for L001-L004 and L006; item 367 names L001 as the span's reference capture. **Consumer against L001's capture: 1 of 1 released** (L005; `g0_reference_source` `cadence-cl-dev-04-l001`, reference record sha256 `78383ca7…f15b`). L005's outcome is the gate of `dev-04-s02` (item 372): released. Every leg decoded 4,096 tokens, `leg_status` complete.

RL-150 R1 / RL-158 Q1 print (gates nothing): soak reference TV0h/TV1h 34.152 °C, Tf08 mean over the soak's last 1,200 s 26.81. L001's capture (own `align_window_reference.json`, status captured): TV0h/TV1h 34.188 °C, Tf08 median 27.30. Release readings (TV0h = TV1h; Tf08): L001 34.841, 34.44; L002 35.075, 36.58 (own ref 34.713); L003 34.892, 34.65 (own ref 34.749); L004 35.075, 36.50 (own ref 34.792); L005 34.933, 35.20 (against L001's 34.188); L006 35.094, 36.63 (own ref 34.846). Full lines in the custody output.

Named stops: LEG_OVERTIME none (largest wall/budget 1.012, L006 a2; the stop needs two legs over 1.5 x). L001's reference present (no REFUSAL). CONTAMINATED_REDOS: 1 used of quota 2 (L006). No named stop in the receipt (`fault` false, `error` null); the Air desk builds `stops.json`.

Receipt: rc 0, `cadence-legs-v1.1`, roster L001-L006, `batch_windows` ["13:14-13:15"], legs 6 of 6, load redos 1, span_result MEASURED_OK / COMPLETE / chain exit 0 / "6/6 legs run"; every step rc 0 (including `L006.a1` and `L006.a2`); kit sha `1cc6673d…2228`, frozen commit `2d347f721` and campaign id `cl-dev-04` asserted; feed files hashed equal (meter stream not opened, RL-150 R8); desk bundle = six leg summaries + span/meter.json + span/result.json. **RECEIPT OK.**

Restore lines: steps `restore`, `stop-volumes`, `stop-meter`, `stop-agents`, `close-volumes` all rc 0; after the close: AC powermode 0, no High Power marker, `night.lock` no holder, Network Time Off, kernel frequency word 0, no stray monitor, no root powermetrics, no align-r0 label. Meter: 50,549 polls over 10,110 s, 0 bad, 0 USB errors, proven stopped. Close epoch 1794912643.42.

Journal copy: no marker `/Users/Shared/JouleWise/desk-copy/cq-dev-04-s01-a1.ok` at 02:55; under items 347/348 the MBP offload runs at close + 30 min (03:20:43) if the lead's copy has not landed.

The magistrate reports; it does not decide. dev-04 is now 6 of 12 legs run; the hand-read and desk are the lead's (item 367 "After").
