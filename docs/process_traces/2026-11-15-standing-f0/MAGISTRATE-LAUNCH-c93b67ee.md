# STANDING-F0 launch (item 346), magistrate c93b67ee, 2026-11-15 ~21:19 PST

Third and last F0 t0 on Sun 15 Nov under item 346. Scripts: custody `f0-startcheck-c93b67ee.sh` and `f0-run-c93b67ee.sh`, derived from 428abccd's by changing only the header (MAGISTRATE_PID, TRIGGER_SPAN, TMPDIR, the comment); `diff` shows nothing else. Start-and-check output: custody `f0-startcheck-out-c93b67ee.txt` (below). The Run's output and launcher JSON go to custody `r1-partc-f0-out-c93b67ee.txt`.

State set (rules 1-8):
- PY `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python`; MAGISTRATE_PID 45208 (`ps` shows `/Users/edr/.local/bin/claude`).
- OUTSTANDING_REFUSAL none. TRIGGER `no_staged`, TRIGGER_SPAN `after-f0-run2-close`: F0 run 2 closed 19:16:33 (item 357) and no staged item's gate can hold within 2 h 30 min: `dev-02-s03` (item 354) and the dev-03 pilot (item 355) cannot launch before 00:00:00 Mon 16 Nov.
- HOST_RESTORE_OK 1 (item 357's Check: every restore line clean). UNPROVEN_GROUP 0. HOLDING_STOP none.
- OTHER_CLOSE_EPOCH 0. LAST_CLOSE_KIND other; GAP 1200 s; host last close 1794798994 (census, 12 receipts, newest F0 run 2's receipt). Copy gate: non-campaign close, covered by its Check (item 357).
- SESSION_READY no. RESTART_PENDING no. COUNTED_LATEST none: no staged counted span is due Sun 15 Nov. Rule 7 binds nothing today; item 356's "not where it would delay them" is weighed in item 357 (expected end ~23:16, close interval to ~23:36, before 00:00; worst case ~01:00 costs `dev-02-s03` no day).
- Ledger: last Part C t0 1794791845 (17:17:25); this launch is after 21:17:25 (rule 5) and before 22:40 (rule 6); the third F0 t0 on Sun 15 Nov (cap 3).
- Six dry-check modules: `standing-f0/tests-ok-b2e01464d` exists, so not re-run.
- 17 hashes equal the table; `verify_r1_executed_sources` full sha; RL-89 MAC CHECK OK line exact; W1-line head `b2e01464d`.
- Batch print: next OS batch 2026-11-16 02:08:39 PST.
- measurement_mode: agent-family processes are only this magistrate's tree (45223 codex-mcp-server, 45226/45227 codex app-server, the tool shell); they end with this process. Free disk 61.7 GB (report only). Battery: AC, not charging, 0 mA.
- Canonical root fast-forwarded to `06841229c` at 21:17 (no night label loaded, no night plist, clean tracked tree).
- Expected end ~23:17 (about 2 h); worst case ~00:42 Mon (launch + 12,180 s); fence deadline launch + 14,400 s.
- No email at launch; the verdict mail follows the Check (rule 10).

## Start and check output

```
== F0 script start Sun Nov 15 21:17:59 PST 2026 epoch 1794806279
From https://github.com/mpmdw/JouleWise
 * branch                ops/2026-11-11-w1-presign -> FETCH_HEAD
45208 /Users/edr/.local/bin/claude
census: 12 receipts, newest mtime 1794798993.1206815 /Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261116T011723Z/runner_receipt.json
copy gate: newest close is non-campaign (/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261116T011723Z/runner_receipt.json); its Check covers the copy
F0 ELIGIBLE at 1794806280; trigger no_staged after-f0-run2-close; host last close 1794798994 (other, gap 1200 s)
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
Ran 1 test in 0.003s

OK
night.lock: no holder
sudo kill rc 0
no r12
no campaign span
45223 node scripts/codex-mcp-server.mjs
45226 node /opt/homebrew/bin/codex app-server
45227 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex app-server
no stray monitor
no root powermetrics
Network Time: Off
boot 2026-10-14 15:07:51 PDT; next OS batch 2026-11-16 02:08:39 PST (boot + 12 h + 48 s + whole days)
 powermode            0
no night/smoke agent
{"ac_power": true, "free_bytes": 61666979840, "disk_check": "report_only"}
agent-family processes (all must be in 45208's tree, NOTE 1):
45208 45204 /Users/edr/.local/bin/claude -p You are the top-level JouleWise magistrate, relaunched headless at 2026-11-15T19:18:58.068645-08
45223 45208 node scripts/codex-mcp-server.mjs
45226 45223 node /opt/homebrew/bin/codex app-server
45227 45226 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex app-s
47265 45208 /bin/zsh -c source /Users/edr/.claude/shell-snapshots/snapshot-zsh-1794799144605-bzt38w.sh 2>/dev/null || true && setopt NO_EXTE
ntp_adjtime rc=0 offset=0 freq_scaled=0 freq_ppm=0.000 status=0x2081
span=1.150s wall-raw rate=+0.761 ppm -> over 5764 s: 4.39 ms
      "ExternalConnected" = Yes
      "InstantAmperage" = 0
      "IsCharging" = No
OUT=/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261116T051800Z
DEADLINE=1794820681.817167
START-AND-CHECK END Sun Nov 15 21:18:03 PST 2026 epoch 1794806283
```
