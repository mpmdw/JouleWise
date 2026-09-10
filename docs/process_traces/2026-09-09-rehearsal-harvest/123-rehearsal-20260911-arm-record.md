# Arm record — rehearsal-20260911 (REHEARSAL_STUB), armed 2026-09-10 04:10:57–04:10:58 PDT

Shape follows 21h; runbook [67](67-arm-runbook-rehearsal-20260911.md) executed by headless
activation `7ce7af2a-8eb6-470e-bf56-70f714977293` (magistrate.lock pid 18817, supervisor 18814, watchdog attempt 10,
launched 2026-09-09 20:52:18 PDT). Record written 2026-09-10 04:11:44 PDT (epoch 1789038704). Evidence directory:
[123-arm-evidence/](123-arm-evidence/). Facts below carry artifact pointers; nothing here is an expected value presented
as an observation.

## Pins and authority

| Pin | Value | Evidence |
|---|---|---|
| Plan / class | `rehearsal-20260911` / `REHEARSAL_STUB` | `123-arm-evidence/arm-night_plan.json` (byte copy, sha256 `a7447608c7c7dc0a3d2a3f6ab56489bd509c9206e8574746c1cf01d113c887bc`, identical to `/Users/edr/night-custody/rehearsal-20260911/night_plan.json` by `cmp`) |
| H = repo_head = measurement_head | `57ddad20226c6921d81a87b9d78e61950c14a74f` | Block A `validated pins:` line; `git rev-parse HEAD` in the checkout = H |
| Frozen triple | (`rehearsal-20260911`, `/private/tmp/joulewise-rehearsal-20260911-checkout`, `57ddad20226c6921d81a87b9d78e61950c14a74f`) | `arm-blockB-output.txt` line `validated pins:` |
| Custody root | `/Users/edr/night-custody/rehearsal-20260911` | `moved .../night_plan.json` line |
| Consolidated notice | Gmail `1a086f4174733bfb`, thread `1a0800cdb282c3f1`, sent 2026-09-09 09:15 PDT, after H and before any move | runbook 67 addendum 1; durable pointer NOTICE SENT line |
| NO channel | No NO relayed to this activation. Limitation (synthesis 65): a headless activation cannot read the thread; Ed's two replies on the thread of 2026-09-09 13:10 and 13:59 PDT (read at launch, 20:55 PDT, before the window) contain no NO. No later reply could be read. | launch email `1a08975838bc2df0`; 03:00 blocker email `1a08ac33d58248e0` |
| Install window | 2026-09-10 03:00–06:30 PDT | install-start epoch `1789038657` (04:10:57 PDT), install-end `1789038658` (04:10:58 PDT); `install verified epoch= 1789038658.277` |
| Expected first firings | dead-man 2026-09-10 07:00 PDT epoch `1789048800`; night t0 2026-09-11 02:56 PDT epoch `1789120560`; courier deadline `1789121760` (03:16 PDT) | plists below; `expected dead-man=...` line is the runbook's expectation, not an observation |
| Exit boundary / belt | 2026-09-11 02:31 PDT (`1789119060`) / 02:45–03:30 PDT | runbook 67 step 0 |

## Timeline (all PDT, 2026-09-10)

- 03:00:10 — window opened; own watch reported two FOREIGN interactive `claude` sessions (pid 16371 ttys001, pid 17047 ttys000,
  each with a codex mcp-server child; both in `/Users/edr/code/JouleWise`). Not signalled (runbook step 0). Ed emailed
  (`1a08ac33d58248e0`) with the 06:05 last-start cutoff.
- 04:09:04 — watch reported `FOREIGN_CLEAR` (both sessions gone). Per the concurrent interactive magistrate's records 121/122 and checkpoint T38g (pushed to main at `cc171556` ~04:10 PDT), Ed — remote and unable to close them — said KILL, and that magistrate terminated pids 16371 and 17047 (itself included) after landing PR #313 (directive channel) and D-180. Numbering note: this record was first written as 115 and renumbered to 123 because the interactive session had concurrently used 115–122 in this directory.
- 04:09:42 — Block A attempt 1 FAILED at `preconditions.py` before any checkout, plan or custody write: the pgrep census
  output included this activation's own multi-line keepalive Monitor shell (its command text contains the word `claude`),
  and the parser's `int(line.split()[0])` raised `ValueError: invalid literal ... 'while'` — the census failed closed on an
  OWN process, exactly as the runbook requires for an unclassifiable line. Output preserved as
  `arm-blockA-attempt1-failed-output.txt`. Only the empty staging/scratch directories created by that attempt were removed.
  Cure applied: the Monitor was stopped (TaskStop `b86zo5h87`, the step-3b own-background stop) before the rerun. FINDING for
  the runbook owner (no process change here): multi-line own background commands break the census line parser; run step 3b
  before the Block A census, not only before Block B.
- 04:10:10 — Block A attempt 2 rc=0 (`arm-blockA-output.txt`, final line `block A rc=0`): preconditions clean (only
  `com.joulewise.magistrate` loaded; census hits 18831/18848 = own codex mcp-server transport, ancestry `[.., 18817, 18814]`;
  `foreign agent matches: []`); H exists, descends from `a52810c9`, is an ancestor of `origin/main`; handback shown;
  worktree added detached at H; real plan authored to staging and twin to scratch by `write_night_plan`; twin
  `--render-only` OK; both rendered plists lint OK; differing fields exactly `chain_path, chain_sha256_path, custody_root`;
  custody root absent.
- 04:10:53 — step 3b: `ps ... grep -E 'claude (daemon run|bg-spare|bg-pty-host)|--resume'` → no matches; no Codex
  children or seats were started by this activation; own background work = none after the Monitor stop.
- 04:10:57 — Block B rc=0 (`arm-blockB-output.txt`, final line `block B rc=0`): checkout clean at H; H still on
  `origin/main`; power `Now drawing from 'AC Power'`, `InternalBattery-0 80%; AC attached; not charging` (observation; it was
  99 % finishing charge at 20:53 the previous evening — recorded, not gated); `powermode 0` on both the Battery Power and
  AC Power profiles (output lines 6 and 21); timer probe `0.1653 s` per `sleep(0.05)` (≈3.3× slack, same class as the
  3.25–3.45× readings of 09-09; recorded, not gated); staging and custody on the same device; final census identical to
  Block A (`foreign agent matches: []`); plan moved by `os.replace`; installer `validated pins: repo_head=H
  measurement_root=/private/tmp/joulewise-rehearsal-20260911-checkout measurement_head=H`; `launchctl list` shows
  `com.joulewise.night`, `com.joulewise.magistrate`, `com.joulewise.night.deadman`; plist checks passed
  (`com.joulewise.night` calendar `{Hour: 2, Minute: 56}`, `com.joulewise.night.deadman` `{Hour: 7, Minute: 0}`, both
  WorkingDirectory = the checkout, ProgramArguments `run`/`dead-man --plan <custody plan>`, RunAtLoad false);
  `post-install night/ baseline: []` (empty directory, inventory taken 04:10:58).
- 04:11:44 — this record; installed plists copied to `123-arm-evidence/com.joulewise.night*.plist`, rendered twins under
  `123-arm-evidence/render/`.

**A green stub says nothing about the capture-timeout seam.** This night is REHEARSAL_STUB with no pack and no
measurement; acceptance items 5/6 and the dead-man/`night/` literal-absence check are judged at harvest per runbook 67
§Expected observations, not here.

## Harvest pointer (next activation)

After t0 + window + courier deadline (2026-09-11 03:16 PDT) and outside the 02:45–03:30 belt: harvest
`night/{result.json,receipt.json,refusal.json,courier.sent,courier.json}` and `night.log`; verify the 07:00 09-10 dead-man
stand-down line precedes the `night gate verdict=` line and that `night/` holds nothing from that firing (compare with the
empty baseline above); verify `night-results/20260911` on origin; then uninstall FROM the stub checkout, remove the checkout
(`git worktree remove`) and the plan root, and record under NIGHT-REHEARSAL-01 (items 4/5/6). Never reuse this stub root
for a real plan. This activation ends with no own background work; the watchdog owns the 09-11 stand-down.
