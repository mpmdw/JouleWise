# 2026-09-23 interactive session 7ec32e8b — owner at the machine: rulings, machine cures, cleanup

Interactive Fable 5.1 session with Ed at the machine, 01:10–01:55 PDT 2026-09-23, concurrent with headless
activation a022aecc (which was holding for its v3 seat and had not yet read Ed's 01:06 email reply).
This record is the durable copy of what Ed decided and what changed on the instrument, for the magistrate
and its successors. Nothing here touches code; lanes named below are for the magistrate to register
through the kernel tooling.

## 1. Ed's rulings (verbatim where quoted)

| # | Subject | Ed's words / decision | Effect |
|---|---------|----------------------|--------|
| 1 | D-182 addendum (abort on `non_observer_process_busy` licenses one successor night) | email 01:06 PDT, thread `1a0ccfe8cb5c59ee`, message `1a0cd4d699a90f29`: "Yes, whatever you recommend that gets me towards paper safe data asap" | RATIFIED; decision-log entry via the normal gate |
| 2 | Block-two level vs apparatus | same email: "c , the recommended - , whatever you guys decide" | option (c) adopted (corrected statistic, registered comparison kept); block-two design pass follows |
| 3 | Major decisions | same email: "im about to update chatgpt and claude with the new models so wait on major decisions til i get the reads of the new models" | HOLD any major design decision (block-two redesign is one) until Ed says go; pilot re-runs under v3 are already ruled and proceed |
| 4 | A268 NIGHT-RESULTS-LARGE-FILES-01 destination | in session 01:37: "agree to your rec on both answers pending" | raw powermetrics plists EXCLUDED from the results branch; reduced per-envelope records stay; raw plists offloaded to iCloud after each harvest (iCloud offload directive); driver checks sizes before push. A268 UNBLOCKED |
| 5 | Worktree prune | same message | approved; executed (§4) |
| 6 | Photos analysis daemons | "yeah fuck photos this is a science insturment" | disabled (§3) |
| 7 | Model mix | "start using opus 5.5 more and see if its more useful than you, fable 5.1"; "you can use a little astra and sol 6.0 high, sol got updated so consult it on some thigns as your decisions dictate" | Opus 5.5 first for lenses/refuters/briefs with a same-packet scorecard vs Fable; Codex seats allowed again at lead discretion (Sol 6.0 high, a little Astra); no xhigh/ultra before the 09-24 03:00 reset |
| 8 | North star | "all i care about is good science and a good paper at the end of this that would impress the joulewise author" | tiebreaker unchanged (decisions serve the better paper; the reader is the JouleSort author) |

## 2. fseventsd runaway — root cause and cures (bench-verified)

- `fseventsd` pid 341 had run at a full core since 04:49:03 09-22 (unified log `scan_old: bailing out because
  device mounted … has dls 0x0`, ~40/h). `sudo launchctl kickstart -k system/com.apple.fseventsd` is REFUSED
  under System Integrity Protection. `sudo kill 341` (01:17) worked; launchd respawned pid 36420, which spent
  ~30 CPU-s on its initial rescan and then sat at 0.0–0.1 % with periodic bursts.
- Root cause (Opus 5.5 read-only diagnosis, verified at the bench): not a bad mount. launchd respawned
  `corecaptured` (Wi-Fi log capture) every ~95 s for a stuck CoreCapture session
  `/Library/Logs/CrashReporter/CoreCapture/WiFi/[2026-09-22_04,49,02.409064]=inducer@DNSFailureRecovery…`;
  each spawn registers CacheDelete FSEvents streams requesting event history on ~3 volumes, and fseventsd
  replays (gzread) and bails on the volume without a log. Bench: 13 corecaptured spawns vs 14 `scan_old` lines
  in the 30 min before the cure.
- Cure without sudo, VERIFIED: `networksetup -setairportpower en0 off; sleep 8; networksetup -setairportpower en0 on`
  at 01:41 → 0 spawns and 0 `scan_old` lines in the following 4 min; fseventsd flat at 0.1 %.
- Ed installed a passwordless cure for the kill route as well: `/usr/local/sbin/joulewise-restart-fseventsd`
  (root-owned, `exec /usr/bin/pkill -x fseventsd`) with `/etc/sudoers.d/joulewise-fseventsd` (NOPASSWD;
  `visudo -c` OK; `sudo -n -l` resolves it). Under D-183 a pegged fseventsd is no longer an owner action.
- Lane to register (magistrate): FSEVENTSD-CORECAPTURED-PREDICATE-01 — the arm `check` and the t0 predicate
  count `launchd … spawned corecaptured` lines over the last 10 min; > 2 ⇒ toggle Wi-Fi once, wait ≥ 3 min,
  re-sample fseventsd and the spawn count, and only then refuse (`night_refused_not_quiet`, naming the process).
  Regression: a fixture log with 5 spawn lines triggers the toggle path; one with 0 does not.

## 3. Photos analysis daemons disabled

`launchctl disable gui/501/com.apple.mediaanalysisd` and `…/com.apple.photoanalysisd` (rc 0, persists across
reboots; `print-disabled` shows both). `bootout` refused by SIP; the running instances (pids 763, 853, 2818)
were killed as the user and did not return. `mediaanalysisd` had run at 1.4–1.8 cores for ~5 min inside
envelope 1 of the 21:00 pilot. Photos.app must not be opened on this machine. Reverse with `launchctl enable`.

## 4. Worktree prune

56 worktrees classified against `origin/main`: 37 merged and clean were removed with `git worktree remove` and
their merged local branches deleted with `git branch -d` (one kept: `feat/2026-09-22-a267-clock-anchor-v3_1`,
not an ancestor of main). Excluded on purpose: `JouleWise-wt-bench` (two live processes), every `*-a022aecc`
worktree (the live activation's), and every dirty or unmerged tree. 20 worktrees remain.

## 5. Open items handed to the magistrate

1. Read Ed's reply (§1 rows 1–3) — the activation was holding when this record was written.
2. Land v3 (lane QPE01-NONOBSERVER-PREDICATE-01) under the twelve-row gate; then NIGHT_HANDBACK for the
   v3 pilot at the next quiet slot (the machine is census-clean and fseventsd is quiet as of 01:50).
3. Register FSEVENTSD-CORECAPTURED-PREDICATE-01 (§2) and unblock A268 with Ed's choice (§1 row 4).
4. Block-two design pass under option (c) is a MAJOR decision: prepare the packet, do not decide it, until Ed's go.
5. Codex model id for "Sol 6.0": `gpt-6-sol` and `gpt-6.0-sol` are rejected for this ChatGPT account
   (probe 01:52); `.mcp.json` still pins `gpt-5.6-sol`. Ask Ed for the id from the Codex app's model picker.
