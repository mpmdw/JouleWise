# STANDING-F0 launch (item 346), magistrate 428abccd, 2026-11-15 ~17:18 PST

Second F0 under item 346. Scripts: custody `f0-startcheck-428abccd.sh` and `f0-run-428abccd.sh`, derived from a187f945's by changing only the header (MAGISTRATE_PID, TRIGGER_SPAN, LAST_CLOSE_KIND, TMPDIR, the comment); the body lines were checked against item 346's fenced blocks on main (every script line outside the header is an item line). Start-and-check output: custody `f0-startcheck-out-428abccd.txt` (below). The Run's output and launcher JSON go to custody `r1-partc-f0-out-428abccd.txt`.

State set (rules 1-8):
- PY `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python`; MAGISTRATE_PID 35046 (`ps` shows `/Users/edr/.local/bin/claude`).
- OUTSTANDING_REFUSAL none. TRIGGER `no_staged`, TRIGGER_SPAN `after-f0-run1-close`: F0 run 1 closed 15:15:11 (item 352) and no staged item's gate can hold within 2 h 30 min: `dev-02-s03` (item 354) and the dev-03 pilot (item 355) are issued but cannot launch before 00:00:00 Mon 16 Nov.
- HOST_RESTORE_OK 1 (item 352's Check: every restore line clean). UNPROVEN_GROUP 0. HOLDING_STOP none.
- OTHER_CLOSE_EPOCH 0. LAST_CLOSE_KIND other; GAP 1200 s; host last close 1794784512 (census, 11 receipts, newest F0 run 1's receipt). Copy gate: non-campaign close, covered by its Check (item 352); the lead also copied F0 run 1's OUT to the Air (item 353).
- SESSION_READY no (no lead READY record; item 355 states the R1 slot session is not READY). RESTART_PENDING no (item 347 step 4). COUNTED_LATEST none: no staged counted span is due Sun 15 Nov; items 354 and 355 are due Mon 16 Nov from 00:00:00. Worst case launch + 12,180 s + 1,200 s is about 20:40, before 00:00.
- Ledger: last Part C t0 1794777374 (13:16:14); this launch is after 17:16:14 (rule 5); this is the second F0 t0 on Sun 15 Nov (cap 3).
- Six dry-check modules: `standing-f0/tests-ok-b2e01464d` exists (a187f945), so not re-run.
- 17 hashes equal the table; `verify_r1_executed_sources` returned the full sha; RL-89 MAC CHECK OK line exact; W1-line head `b2e01464d`.
- Batch print: next OS batch 2026-11-16 02:08:39 PST.
- measurement_mode: agent-family processes are only this magistrate's tree (35061 codex-mcp-server, 35064/35069 codex app-server, the tool shell); they end with this process. Free disk 63.7 GB (report only). Battery: AC, not charging, 0 mA.
- Expected end ~19:15 (about 2 h); worst case ~20:40; fence deadline launch + 14,400 s.
- No email at launch (as a187f945); the verdict mail follows the Check (rule 10).

## Start and check output

```
== F0 script start Sun Nov 15 17:16:35 PST 2026 epoch 1794791795
From https://github.com/mpmdw/JouleWise
 * branch                ops/2026-11-11-w1-presign -> FETCH_HEAD
35046 /Users/edr/.local/bin/claude
census: 11 receipts, newest mtime 1794784511.5079753 /Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261115T211611Z/runner_receipt.json
copy gate: newest close is non-campaign (/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261115T211611Z/runner_receipt.json); its Check covers the copy
F0 ELIGIBLE at 1794791796; trigger no_staged after-f0-run1-close; host last close 1794784512 (other, gap 1200 s)
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
Ran 1 test in 0.019s

OK
night.lock: no holder
sudo kill rc 0
no r12
no campaign span
35061 node scripts/codex-mcp-server.mjs
35064 node /opt/homebrew/bin/codex app-server
35069 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex app-server
no stray monitor
no root powermetrics
Network Time: Off
boot 2026-10-14 15:07:51 PDT; next OS batch 2026-11-16 02:08:39 PST (boot + 12 h + 48 s + whole days)
 powermode            0
no night/smoke agent
{"ac_power": true, "free_bytes": 63744024576, "disk_check": "report_only"}
agent-family processes (all must be in 35046's tree, NOTE 1):
35046 35042 /Users/edr/.local/bin/claude -p You are the top-level JouleWise magistrate, relaunched headless at 2026-11-15T15:48:46.732822-08
35061 35046 node scripts/codex-mcp-server.mjs
35064 35061 node /opt/homebrew/bin/codex app-server
35069 35064 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex app-s
36408 35046 /bin/zsh -c source /Users/edr/.claude/shell-snapshots/snapshot-zsh-1794786532408-c8jxoh.sh 2>/dev/null || true && setopt NO_EXTE
ntp_adjtime rc=0 offset=0 freq_scaled=0 freq_ppm=0.000 status=0x2081
span=1.150s wall-raw rate=+0.923 ppm -> over 5764 s: 5.32 ms
      "ExternalConnected" = Yes
      "InstantAmperage" = 0
      "IsCharging" = No
OUT=/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261116T011637Z
DEADLINE=1794806198.076538
START-AND-CHECK END Sun Nov 15 17:16:39 PST 2026 epoch 1794791799
```
