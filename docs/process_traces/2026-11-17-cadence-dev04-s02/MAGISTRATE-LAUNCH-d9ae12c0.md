# dev-04-s02 (dev-04 second span, L007-L012) pre-launch record, magistrate d9ae12c0 (headless, Opus 5.5), 2026-11-17 ~03:25 PST

Item 372, launched under its own gates after item 367's Check (RUN_STATE 380).

Scripts (custody `/Users/edr/night-custody/magistrate/`): `cadence-dev04-s02-{inputs,check,launch}-d9ae12c0.sh`, built from item 372's two fenced blocks on main `4f25062e3`; the three canonical-root `git fetch` lines are replaced by object-presence checks of the commits they fetch (`2d347f721`, `fecaf73f3`, `b7a0d9882`, all local), as ee21df57 did for item 367 (no fetch in the canonical root). Diff against ee21df57's item-367 scripts: only the lines where item 372's text differs from item 367's (worktree, PRIOR_CLOSE text, SPAN/LEGS/EXPECT, ISSUED_EPOCH, PRED_SPAN/CAMP/ROSTER, WATCH_UNTIL_EPOCH, budget comment) and the activation id.

Dry tests in the fresh worktree `/Users/edr/code/jw-wt/cadence-dev-04-s02` at `2d347f721` (own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONPATH=.:tests`, homebrew python3.13, one module at a time), all OK (custody `cadence-dev04-s02-tests-d9ae12c0.txt`): test_kit_v11 30, test_span_reference 19, test_legs_runner 42, test_kit 18, test_stops_desk 14, test_runner_guards 8, test_launch_cadence_span 12, test_r1_smoke_launcher 58 (201 tests). Tree clean after.

Journal copy (items 347/348 fallback): marker `cq-dev-04-s01-a1.ok` absent at close + 30 min (03:20:44), so this activation ran the MBP cloud offload: encrypted tarball and manifest copied to iCloud Drive `JouleWise-offload/cq-dev-04-s01-a1`, cloud-copy hashes OK, decrypt-and-list round trip 341 entries, manifest 255 files; enc sha256 `ddd1274a…36bb`, manifest sha256 `f8508272…5cfc`; `brctl` 03:22:10: no needs-upload, client idle, caught-up, last-sync 03:21:45 after the copy at 03:21:04. Marker written 03:22:10 by this activation (path: MBP offload, not the lead's Air copy). Output custody `offload-dev04-s01-{out,poll,brctl}-d9ae12c0.txt`.

Inputs: PY align-pilot2 venv; MAGISTRATE_PID 70429; PRIOR_CLOSE_EPOCH 1794912793 (later of the receipt close 1794912643.42 and the fence seen gone 02:53:13); LAST_CLOSE_KIND campaign (GAP 300 s); OTHER_CLOSE_EPOCH 0; HOST_RESTORE_OK 1 (RUN_STATE 380); SESSION_READY no.

Start and check, 03:22:23-03:22:25 PST, rc 0, every line passed:
- ARG `02:00-02:35` (band 02:35:00-10:50:00); SPAN dev-04-s02, LEGS L007-L012; HEAD `2d347f721`, clean.
- census 20 receipts, newest = dev-04-s01's receipt (campaign close); journal-copy line: the marker above.
- day_gate: t0-date 2026-11-17, 6 development legs already launched (dev-04-s01, mixed-size 6) + this span 6 = 12, mixed.
- pred_gate: `dev-04-s01` CLEAN (rc 0, 6 of 6, MEASURED_OK COMPLETE, close steps rc 0, overtime 0, contaminated redos 1 within quota, close_epoch 1794912644).
- expiry: valid until 11:40:40 PST Tue (RL-173 D.5).
- validate-kit ok (cl-dev-04, frozen_paths_verified, 12 legs, kit sha `1cc6673d…2228`); queue sha asserted at `b7a0d9882`.
- measurement_mode verify: one FAIL = this magistrate's own MCP children 70444/70445/70448 (NOTE 1); WARN battery-limit syntax and softwareupdate schedule (not gates); Network Time Off; frequency word 0; AC, not charging; free 301,681,106,944 bytes.
- night.lock no holder; sudo kill rc 0; no r12; no stray monitor; no root powermetrics; no night/smoke agent; powermode 0.
- batch print: next OS batch Wed 18 Nov 02:08:39 PST.
- Plan: batch_windows ["02:00-02:35"], cadence-legs-v1.1, expected 12,071 s, worst case 24,750 s, blackout_clear true; L007 captures the span reference, L008-L012 consume it. Fence end ≈ launch + 26,210 s.

The launch script re-runs Start and check on fresh state, then the Run block; its output (t0 = LAUNCH_EPOCH, OUT, DEADLINE, LAUNCH_RC, launcher JSON) goes to custody `cadence-dev04-s02-out-d9ae12c0.txt` and `cadence-dev04-s02-launch-d9ae12c0.json`. A STOP, WAIT, CEDE or VOID line, or LAUNCH_RC other than 0, means nothing ran.
