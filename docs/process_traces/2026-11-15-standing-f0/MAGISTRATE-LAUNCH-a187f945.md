# STANDING-F0 launch (item 346), magistrate a187f945, 2026-11-15 ~13:20 PST

First F0 under item 346. Script: custody `f0-startcheck-a187f945.sh` (Start and check) and `f0-run-a187f945.sh` (the same text plus item 346's Run block; the Run re-runs the complete eligibility check on fresh state and launches). Both are item 346's fenced blocks extracted mechanically from RUN_STATE on main, preceded by a header that sets the state `f0_eligible` reads, and followed by three print lines (agent-process tree, kernel frequency word as item 308 read it, battery). Output of Start and check: custody `f0-startcheck-out-a187f945.txt` (below). The Run's output and the launcher JSON go to custody `r1-partc-f0-out-a187f945.txt`.

State set (rules 1-8):
- PY `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python`; MAGISTRATE_PID 22868 (`ps` shows `/Users/edr/.local/bin/claude`).
- OUTSTANDING_REFUSAL none. TRIGGER `no_staged`, TRIGGER_SPAN `after-dev-02-s02-close`: the dev-02-s02 close (12:42:45) leaves no staged item whose gate can hold within 2 h 30 min. `dev-02-s03` is not issued (items 346-348), and dev-02-s01 was withdrawn unarmed (item 345).
- HOST_RESTORE_OK 1 (item 344's Check, RUN_STATE 349: every restore line OK). UNPROVEN_GROUP 0. HOLDING_STOP none.
- OTHER_CLOSE_EPOCH 0 (no session or W1 close outside the census roots). LAST_CLOSE_KIND campaign; QUIET_CAMPAIGN_S 300; host last close 1794775366 (census, 10 receipts, newest the dev-02-s02 receipt).
- SESSION_READY no (no lead READY record for a v4 session in RUN_STATE). RESTART_PENDING no (item 347 step 4: the lead has not scheduled the RL-172 (h) restart). COUNTED_LATEST none (no staged counted span due today).
- Journal-copy line: `cq-dev-02-s02-a1 cloud-offload Sun Nov 15 13:14:28 PST 2026 | ... enc sha256 bf34a938… | manifest sha256 0af51efe… files=226 | upload evidence brctl ...` (RUN_STATE 350).
- Ledger `standing-f0/ledger.tsv` seeded on first use: item 319 t0 1794703426 and item 325 t0 1794720205 (from `r1-partc2-c3f4-out-b418e121.txt`). Last Part C t0 21:23:25 Sat, so spacing (4 h) holds; zero F0 t0s on Sun 15 Nov before this one.
- Six dry-check modules at `b2e01464d`, run once on this host by this activation (scratch worktree, own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, python3.13): 1, 31, 15, 58, 24, 24 tests, all OK (no skip printed here; the Air's log had one). `standing-f0/tests-ok-b2e01464d` written; log `standing-f0/tests-b2e01464d-a187f945.log`.
- 17 hashes: the printed lines equal the item's table (sorted `diff`, empty). `verify_r1_executed_sources` returned the full sha. RL-89 MAC CHECK OK line exact. W1-line head `b2e01464d` (fetched). Staged worktree `/Users/edr/code/jw-wt/partc-b2e01464d` created by the script at the pin, tree `c904864e4`.
- Batch print: boot 2026-10-14 15:07:51 PDT; next OS batch 2026-11-16 02:08:39 PST.
- Rule 6: launch inside 02:35:00-22:40:00. Rule 7: nothing staged today. Expected end ~15:20 (item 322's 7,134 s); worst case launch + 12,180 s (~16:43); fence deadline launch + 14,400 s.
- measurement_mode: the agent-process line shows only this magistrate's tree (22888 codex-mcp-server, 22891/22892 codex app-server under it), NOTE 1; they end with this process. Free disk 66.4 GB (preflight `free_bytes` 66,441,154,560, report only).

## Start and check output

```
== F0 script start Sun Nov 15 13:14:36 PST 2026 epoch 1794777276
From https://github.com/mpmdw/JouleWise
 * branch                ops/2026-11-11-w1-presign -> FETCH_HEAD
22868 /Users/edr/.local/bin/claude
Preparing worktree (detached HEAD b2e01464d)
HEAD is now at b2e01464d Merge PR #790: W1 kit retires the R10-2(a) receipt path (RL-148 §2; RL-170, RL-172c row 4)
census: 10 receipts, newest mtime 1794775365.1627553 /Users/edr/campaign-out/cl-dev-02/cq-dev-02-s02-a1-20261115T180023Z/runner_receipt.json
journal copy of cq-dev-02-s02-a1: cq-dev-02-s02-a1 cloud-offload Sun Nov 15 13:14:28 PST 2026 | provider /Users/edr/Library/Mobile Documents/com~apple~CloudDocs (iCloud Drive) JouleWise-offload/cq-dev-02-s02-a1 | enc sha256 bf34a938107856122de6d1e047152c4f0e3d969df489fcc917f5b28f20f01ae3 | manifest sha256 0af51efee1b638bc6c569aa886c957acf6fdf4b2a4f19533fd494ec73ab31057 files=226 | upload evidence 
F0 ELIGIBLE at 1794777280; trigger no_staged after-dev-02-s02-close; host last close 1794775366 (campaign, gap 300 s)
2806f9eae61210d457ae19a5484cfe7dc7ac70a31c20b1ca0a2856f32178a825 scripts/align_r1_rehearsal.py
7403e69d9aedb54887bfc4218a45db84faa653329ca977bcf97edf20af88f923 scripts/align_r1_runtime.py
a5ba3cd4dce1b41c8448e2e26653789a9f607ffc2836a7b4a9339b991f9b6dac joulewise/align/apple/r1_runtime.py
4b9d1c69b0459a0382dfdd5e3aee56366e99f770ed2320cfff90539647ab6591 joulewise/align/apple/r1_runtime_contract.py
0132579cc33f8a997cdfd5f3dd84466352cdeeeebf9ca7de8dc1ec7990cea0a9 joulewise/align/apple/smc_enumeration.py
c72937bd8bf7b5553c1ffd70e76018ffbf25f32578533c8749aa88419837918d joulewise/align/apple/thermal_gates.py
ffd6c025f4691771ea348f5d0f670c8f4bbfcb61afe67b83831afdd6c3d6f1ea joulewise/align/apple/r1_phase_table.py
837b74be97616c48c26b0c1277fe2a605b575d5cfc4396dc05e1139079daf1ba joulewise/align/apple/workload.py
b9b46f9ede50b265c245dcc05d3503139632ae129e313675622fa1dce25d39d7 joulewise/align/apple/thermal.py
272aecb8bc0d9e33defd7f686b129ea236b925fdfbf68137697120dd63232f46 configs/align/v4/r1_runtime.json
242cd7aa0bf5788786ca8630e6931abcaaa3e01dc3bf014255a6191b50c6e799 scripts/launch_align_r0.py
ac1dc2a223754cfc3295dd1352a838a3077671da140ffeeba484400e1bd249c6 scripts/run_align_r0_launchagent.sh
6f1fb9f4ac3109650b36b07012e24728c17e7112e7b59953e6557f2b5fdd35aa scripts/run_align_r1_smoke.py
39dd7946e899058987038130b9c133298283a80ae3db4dceee79daad3c8e08b8 scripts/align_r1_followup_kit.py
b2c91c77ef9f1c227c5c172690fadf5f36cff22b4874d0eeaa66798ca9ef12b8 scripts/align_r1_part_c.py
b605195f9a23226a702376d9fbdb2e451546d6c3187297c39bd5b88e2e78f167 joulewise/align/apple/rl145_prints.py
28caceeba15c30ca679e25c49a7c85b828096bb3b1ab3e2c676d8d1c8d10db80 joulewise/align/apple/v4_registration.py
b2e01464d6d4fbf2901ff4d4154df9455104a12a
RL-89 MAC CHECK OK e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b 60 16 44 272aecb8bc0d9e33defd7f686b129ea236b925fdfbf68137697120dd63232f46
.
----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
night.lock: no holder
sudo kill rc 0
no r12
no campaign span
22888 node scripts/codex-mcp-server.mjs
22891 node /opt/homebrew/bin/codex app-server
22892 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex app-server
no stray monitor
no root powermetrics
Network Time: Off
boot 2026-10-14 15:07:51 PDT; next OS batch 2026-11-16 02:08:39 PST (boot + 12 h + 48 s + whole days)
 powermode            0
no night/smoke agent
{"ac_power": true, "free_bytes": 66441154560, "disk_check": "report_only"}
agent-family processes (all must be in 22868's tree, NOTE 1):
22868 22864 /Users/edr/.local/bin/claude -p You are the top-level JouleWise magistrate, relaunched headless at 2026-11-15T12:43:27.980472-08
22888 22868 node scripts/codex-mcp-server.mjs
22891 22888 node /opt/homebrew/bin/codex app-server
22892 22891 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex app-s
24907 22868 /bin/zsh -c source /Users/edr/.claude/shell-snapshots/snapshot-zsh-1794775414263-2v5le4.sh 2>/dev/null || true && setopt NO_EXTE
ntp_adjtime rc=0 offset=0 freq_scaled=0 freq_ppm=0.000 status=0x2081
span=1.150s wall-raw rate=+0.416 ppm -> over 5764 s: 2.40 ms
      "ExternalConnected" = Yes
      "InstantAmperage" = 0
      "IsCharging" = No
OUT=/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261115T211440Z
DEADLINE=1794791681.753814
START-AND-CHECK END Sun Nov 15 13:14:42 PST 2026 epoch 1794777283
```
