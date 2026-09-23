# Cold final pass (Fable 5.1), gate-ledger row 7 — candidate 665d3bd7 (A271 merged with main ea4995d5)

Judge worktree `/Users/edr/code/wt-f2d6899b-finalpass2`, detached at 665d3bd7, clean. One non-interactive session, all probes in the foreground, no subagents, no watchers, nothing committed, no tracked file edited. Scratch worktree `/tmp/f2d6899b-final2-judge` at 665d3bd7 for tests, mutants and probes; removed at the end. Session 2026-09-23, about 35 minutes of the 40-minute budget.

## 0. Contamination disclosure

Loaded by the harness before I acted, not by me: the user-level `/Users/edr/.claude/CLAUDE.md` (playbook names, writing standard), the project `CLAUDE.md` at 665d3bd7 (bridge policy), and the auto-memory index `MEMORY.md` (one-line pointers; it names lane A234, PR #392/#393, an "fseventsd cure passwordless" memory, and the 09-23 checkpoints). I opened no memory file, no RUN_STATE.md, no TASK_QUEUE.md, no council log, no skill. Beyond the charge I read: the lane diff `git diff ea4995d5...665d3bd7`; records 05, 11, 13, 16, 28, 30, 31 on `origin/docs/2026-09-23-f2d6899b`; the code and tests on the candidate; `docs/process/NIGHT_HANDBACK.md` lines 240–290 for the paragraph's context. I did not read `pilot_protocol_v3.json`, `night_gate.py:55-75` (I take record 31's description of the digest-keyed table as its claim, and rule on the convention as stated), the decision log, or any custody root. No live `/usr/bin/log`, `networksetup`, `sudo` or `launchctl` was run.

## 1. Ruling 16 Q2 required tests/actions 1–4, Q3 conditions 1–4, record-30 cures

Baseline (scratch worktree at 665d3bd7):

```
$ PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_corecaptured_loop.py tests/test_night_gate.py tests/test_arm_retry.py
123 passed, 163 subtests passed in 1.56s
$ … tests/test_evidence_night.py
126 passed, 127 subtests passed in 418.41s (0:06:58)
```

Total 249 passed (record 30 reported 246 at 1b8c6410; the three new tests are the record-30 cures).

| Item | Where in code | Test | Verdict |
|---|---|---|---|
| Q2-1 clock read before the log read anchors the 10-min window; lines after the anchor kept | `night_gate.py` `_check_machine`: `log_started_epoch_s = _clock_value(...)` before `_run(probes, LOG_ARGV)`, `log_finished_epoch_s` after, both passed to `count_spawns(…, until_epoch_s=…)`; `evidence_night.py` `observe()` same shape; `corecaptured_loop.count_spawns` window `now-600 <= epoch <= until` | `test_corecaptured_t0_window_anchors_before_slow_log_read`, `test_corecaptured_arm_window_anchors_before_slow_log_read` (three spawns at −590, −300, +10 with a 30 s read → count 3, refuse/toggle). My probe: "three, 30s read, one during read" → `night_refused_not_quiet`, count 3 | MET |
| Q2-2 every actuator command bounded: log 30 s, networksetup 30 s, restart 60 s; timed-out `off` still reaches `on` | `command(..., timeout=30/30/30/60)`; `try/finally` around off → on | `test_corecaptured_arm_commands_have_bounded_timeouts` (timeouts `[30,30,30,30,60]`), `test_corecaptured_arm_off_timeout_restores_wifi_and_refuses`. My probe D: off hangs → `['off','on']` issued, refusal names the toggle failure | MET |
| Q2-3 post-toggle persistence threshold ≥ 1 new spawn | `if after.count >= 1:` | `test_corecaptured_one_new_spawn_after_toggle_refuses`; my mutant `>= 2` → that test FAILS (killed) | MET |
| Q2-4 exactly-two boundary tests; blank-line tolerant parser | `if line.strip()` filter; `> 2` at both sites | `test_corecaptured_t0_threshold_is_three_spawns`, `test_corecaptured_arm_threshold_is_three_spawns` (i=2 no refusal/toggle, i=3 refusal/toggle); `test_post_toggle_cutoff_and_malformed_output`. My t0 probe: 2 spawns → no refusal, 3 → refusal | MET |
| Q2-5 Opus N3 latent (arm-to-t0 < ~13 min) | no code change, as ruled | — | as ruled |
| Q3-1 actuation only when item 0 AND every earlier row passed; otherwise read-only, `remediation: "not_licensed"`, fail on count > 2 | `check()`: `if nothing_loaded and all(row["verdict"] == "pass" for row in checks.values()): … else: corecaptured_arm_check(actuator, read_only=True)`; read-only branch sets `not_licensed`, raises on `> 2`, returns pass on ≤ 2 | `test_loaded_night_agent_makes_corecaptured_read_only`, `test_failed_census_makes_corecaptured_read_only`, `test_failed_census_read_only_count_of_two_passes_without_actuation`. Mutant dropping the `all(...)` clause → 2 tests FAIL (killed; record 30's surviving `license_right` mutant is now dead) | MET |
| Q3-2 contract line 175 replaced by the three-move enumeration; corecaptured row in the inventory | `docs/contracts/evidence_night_entry.md:175` carries the enumeration (with the record-30 F2 addition about exceptions); item 7 added | read | MET |
| Q3-3 (a) loaded label + 5 spawns → `REFUSED: night agents already loaded…`, zero actuator commands; (b) census failed + 5 → refusal names the census, zero commands; (c) all pass + 5 → exactly one off, one on, restart only on persistence | — | (a) `test_loaded_night_agent_makes_corecaptured_read_only` and my probe A; (b) `test_failed_census_makes_corecaptured_read_only` and my probe B/B2/B3; (c) `test_corecaptured_arm_toggles_once_and_counts_only_post_toggle_spawns` (no sudo, one off, one on), `test_corecaptured_arm_persistence_restarts_once_and_refuses` (one sudo); my probes C/C2 | MET |
| Q3-4 this cold pass reads the amended line against the code path and the tests in 3 | this file | — | done |
| Record 30 F1 (backward clock → false zero) | `count_spawns` raises `ValueError("clock moved backward…")` when `until < now`; t0 catches `ValueError` → `not_measured`; arm → `Refused`, no actuation | `test_corecaptured_t0_backward_clock_is_not_measured`, `test_corecaptured_arm_backward_clock_refuses_without_actuation`; my probes "three, clock back 30s" (t0: `not_measured`, no refusal) and E4 (arm: refused, `actuators=[]`); mutant `if False:` → both tests FAIL (killed) | CURED |
| Record 30 F2 (moves that raised leave no record) | `command_errors` dict populated on every raise, carried in `Refused.evidence` so `inspect` merges it into the row; contract text says "or, when it produced none (a timeout, for example), with the exception it raised" | `test_corecaptured_timed_out_move_is_recorded_without_exit_code`; my probes D/D2/D3/D4 show `command_errors` for off/on/restart timeouts and an OSError | CURED |
| Record 30 F3 (slow-read tests only pre-read stamps) | both slow-read tests now place the third spawn at +10 s, inside the 30 s read | see Q2-1 | CURED |

## 2. Can the arm check or t0 gate ever actuate wrongly? Wi-Fi left off? False measured zero?

Probe scripts `/tmp/f2d6899b/probe_t0.py` (through `night_gate.evaluate_night` → `_check_machine`, the same entry the pilot plan takes) and `/tmp/f2d6899b/probe_check.py`, `/tmp/f2d6899b/probe_e4.py` (a `LifecycleTests` subclass calling production `entry.check()`), all run from the scratch worktree. Output tails:

```
t0:
two spawns                         refusal=None                    measured 2   actuators=[]
three spawns                       refusal=night_refused_not_quiet measured 3   actuators=[]
three, 30s read, one during read   refusal=night_refused_not_quiet measured 3   actuators=[]
three, clock back 30s              refusal=None   not_measured 'clock moved backward during the corecaptured log read'
exit 0, empty stdout               refusal=None   not_measured 'corecaptured log has no syslog header'
exit 0, header only                refusal=None   measured 0
exit 124 (timeout)                 refusal=None   not_measured 'log exited 124: ProbeError: timeout after 30 s'
spawn at exactly -600              refusal=night_refused_not_quiet measured 3
spawn at -601 (outside)            refusal=None                    measured 2

check():
[A loaded label + 5 spawns]            refused='night agents already loaded…'  remediation=not_licensed actuators=[] 
[A2 plist present, fake launchctl says absent + 5 spawns] refused='…plists present: …com.joulewise.night.plist' not_licensed actuators=[]
[B retained_roots failed + 5]          refused='night_refused_not_quiet: corecaptured: 5 … remediation not licensed' actuators=[]
[B2 canonical failed + 5]              same, actuators=[]
[B3 census failed + exactly 2]         refused='census failed'; corecaptured row verdict=pass, not_licensed, actuators=[]
[C all pass + 5, loop persists]        refused (…2 new spawns after toggle; fseventsd restart exit 0) actuators=['off','on','/usr/bin/sudo'] sleeps=[8,180]
[C2 all pass + 5, cured]               no refusal; wifi_toggled_once; actuators=['off','on']; rehearsal_ready=True
[D off hangs]                          refused; command_errors={'Wi-Fi off': TimeoutExpired…}; actuators=['off','on']; sleeps=[]
[D2 on hangs]                          refused 'Wi-Fi on failed'; command_errors={'Wi-Fi on': TimeoutExpired…}; actuators=['off','on']
[D3 restart hangs]                     refused; command_errors={'fseventsd restart': TimeoutExpired…}; one sudo
[D4 off raises OSError]                refused; command_errors={'Wi-Fi off': 'OSError: boom'}; actuators=['off','on']
[E log exit 0 empty stdout]            refused 'corecaptured log not measured: … no syslog header'; actuators=[]
[E2 log header only]                   pass, count 0, remediation none
[E3 post-toggle read empty stdout]     refused 'post-toggle observation failed'; no restart
[E4 clock back 30 s, 3 recent spawns]  refused 'clock moved backward…'; actuators=[]
```

Answers:

- **Actuation with a night loaded, an earlier row failed, or at t0:** no path found. At t0 `_check_machine` issues only `LOG_ARGV`; the t0 probe recorded no `networksetup`/`sudo` argv in any scenario. In `check()` the licence is `nothing_loaded and all rows pass`; every failed or skipped earlier row (item 0, canonical, retained_roots, census) forced the read-only branch. A fake `launchctl` (rehearsal mode) cannot hide a real loaded night because `night_agents` also lists real plist files under `~/Library/LaunchAgents` (probe A2 refuses on the plist alone). Residual, not a defect: a rehearsal check with a fake launchctl on a machine with no plist and no loaded label but > 2 spawns does run the real toggle; that is exactly the licensed state (nothing loaded, all rows pass), and the production actuator is the intended one.
- **Hung or failed command leaving Wi-Fi off:** a hung or failing `off` still issues `on` (finally block; D, D4). If `on` itself hangs or exits non-zero there is no second attempt; the check refuses naming "Wi-Fi on failed" / the exit codes and records the exception (D2). Wi-Fi can therefore be left off only when the restore command itself fails, which is loud in the refusal text and `check.json`. Acceptable: a stuck radio is not something a retry of the same command cures, and the refusal blocks the arm. Recorded as residual, no cure required.
- **False measured zero:** the only way to get a measured 0 is a syslog header with no spawn lines. Empty stdout, non-zero exit, a timeout (exit 124 from the 30 s t0 probe runner), an unparseable line, and a backward clock step are all `not_measured` (t0) or a refusal (arm). Not tested live: whether `/usr/bin/log show` can exit 0 with a header and no lines while the log store is unavailable; if it can, the zero is a genuine instrument limit, and at t0 the existing 0.5-busy-core predicate still guards the machine. NOT EXECUTED: any live log read.

## 3. Integration with A234 (merge with main ea4995d5)

```
merge parents: 6b62d6bc (lane) ea4995d5 (main); merge-base 971e60d8
conflict markers: none in joulewise/, docs/contracts, NIGHT_HANDBACK.md, runbook
files touched by BOTH sides: docs/phase_2/derivation_night_runbook.md, docs/process/NIGHT_HANDBACK.md, joulewise/arm_retry.py
main-side hunks (MB..ea4995d5) vs merge-side hunks (6b62d6bc..665d3bd7), sorted +/- lines, md5:
  joulewise/arm_retry.py                     c16fc874… == c16fc874…
  docs/process/NIGHT_HANDBACK.md             98d89d86… == 98d89d86…
  docs/phase_2/derivation_night_runbook.md   8df76835… == 8df76835…
```

The merge carries every A234 hunk on the three shared files byte-for-byte, and the lane's own hunks on them are the `night_refused_not_quiet` row rewrite (both generated policy blocks and `COLD_GATE_CODES` say the same text; record 30 V6 verified byte-equality with `render_policy()`, I did not re-run it). `tests/test_arm_retry.py` passes at the merge (part of the 123). `scripts/magistrate_watchdog.py` and `tests/test_magistrate_watchdog.py` are main-side only; NOT EXECUTED here (long modules, outside the charge's test list). No lost or garbled hunk.

## 4. REINTERPRETATION RULING — ruling 16 Q2(a) first condition vs. the registration-immutability convention

**ACCEPT the proposal in record 31, with one wording condition.** Exact ruling text:

> Ruling 16 Q2(a), first condition, is reinterpreted as follows. "Record it where the precedent recorded the 0.5-busy-core rule" is satisfied for A271 by (i) the threshold as a named code constant in the t0 and arm-check paths, and (ii) the `night_refused_not_quiet` policy text in `joulewise/arm_retry.py` (rendered into `NIGHT_HANDBACK.md` and the runbook) and the campaign README citing cold ruling 16 Q2 (2026-09-23). The `pilot_protocol_v3.json` bytes are not edited: the registration table is digest-keyed and prior versions are kept byte-identical as ruled history, so an in-place edit would orphan the v3 entry used by the 2026-09-23 07:00 pilot records or force a re-pin the convention forbids. The v4 recording (`t0_corecaptured_spawns_max: 2` and ruling 16's id appended to the `ruling` string) is a follow-up lane, landed with the next registration change (block two or the next pilot re-run, whichever comes first). Until v4 lands, the next arm notice names the new refusal in plain words ("the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes"), so the owner's standing veto covers it.

Wording condition (not a code change): the code constant must actually be a named constant. At 665d3bd7 the threshold is the literal `2` in three places (`night_gate.py` `spawns.count > 2`, `evidence_night.py` `before.count > 2` twice) and `>= 1` for persistence. See §6.

Reason for ACCEPT over REQUIRE v4 in this PR: v4 is registration machinery that the sealed-candidate check and every future plan consume, hence claim-bearing and deserving its own review; bundling it here would widen a machine-state lane into a registration change under a 40-minute cold pass. The science fence in Q2 holds without it (a t0 refusal captures nothing; no estimator, exclusion or sizing changes). Reason against a different recording: the policy text plus README already tell a later reader where the rule came from, and the notice gives the owner the veto point Q2 wanted.

## 5. Doc paragraphs against the code and the first-use test

**Contract item 7 (`evidence_night_entry.md:283-294`) and line 175.** True against the code: the row reads `LOG_ARGV` (`--last 10m`), counts the pinned spawn line, fails on an unmeasured read (`Refused` from `observe`), records `not_licensed` and fails above two without any move when item 0 or an earlier row failed, otherwise makes moves (2) and (3) at most once each with the 180 s wait and the ≥ 1 persistence rule, and records counts, remediation, exit codes and `command_errors`. One imprecision on line 175: "(2) … when more than two `corecaptured` spawns were counted" and "(3) … when new spawns persist 180 s after that cycle" is correct, and item 7 says "at least one new spawn", which matches `>= 1`. First-use test: "corecaptured" is glossed at first use in item 7 ("the Wi-Fi log-capture helper; a respawn loop makes the file-system event daemon fseventsd burn a core"); "item 0" and "row" are defined earlier in the contract (item list and check-row inventory). Passes.

**NIGHT_HANDBACK.md corecaptured paragraph (lines 267-288).** True against the code, with two small drifts: (a) "toggles Wi-Fi once if it counts at least three spawns" is `> 2`, correct; (b) "waits at least three minutes after Wi-Fi is back on" is `sleep(180)` after `toggle_completed`, correct; (c) "One or more new spawns triggers … once and refuses" matches `>= 1`; (d) "If any earlier arm check fails … not_licensed … fails if the count exceeds two" matches the read-only branch; (e) "A failed log read refuses at the arm check" and "A failed t0 log read is recorded as not measured; the processor check still guards the machine" both match. First-use test for a technical reader with no project grounding: `launchd` ("macOS's service manager"), `corecaptured` ("the Wi-Fi log-capture helper"), `fseventsd` ("the file-system event daemon"), the exact counted line, the restart command and what it does (`pkill -x fseventsd`; launchd respawns), the `machine_quiet` row (30 s, 0.5 busy cores), "t0" (used earlier in the same section as the night's start) are all built before or at first use. Two terms arrive unglossed: "the arm check" (the pre-arm check that runs before a night is installed) and "`night_refused_not_quiet`" (a refusal code). Both appear earlier in the file (the refusal-code table at line 84 and the attempt narratives), so a reader of the whole document has them; a reader landing on the paragraph alone does not. Minor; listed as optional in §6, not a blocker.

## 6. Should-fix before merge

None that blocks. Named items, all optional at the lead's discretion:

1. **Name the threshold constant** (ties to §4's wording condition). Replace the three literal `2` comparisons with one module constant, e.g. `T0_CORECAPTURED_SPAWNS_MAX = 2` in `joulewise/night_gate.py` next to `T0_NON_OBSERVER_SHARE_MAX`, and `POST_TOGGLE_SPAWNS_PERSIST_MIN = 1` in `joulewise/evidence_night.py`; reference them from both call sites and from the docs. Pure refactor; the exactly-two boundary tests already pin the values. This can land in the v4 follow-up lane instead if the lead prefers not to reopen the PR.
2. **NIGHT_HANDBACK paragraph, two glosses**: at first use in the paragraph, write "the arm check (the pre-arm check that runs before a night is installed)" and "`night_refused_not_quiet` (the refusal code for a machine that is not quiet)". Docs only.
3. **Residual, recorded, no change**: a failing or hung `networksetup … on` leaves Wi-Fi off with a loud refusal (§2). Opus N3 (arm-to-t0 under ~13 min) stays latent as ruled.

## VERDICT

**MERGE.**

Grounds: every ruling 16 Q2 test/action and Q3 condition is met in code and in call-site tests (§1); the three record-30 cures are in and their mutants die; no counterexample through `check()` or `_check_machine` actuates with a night loaded, after an earlier failed row, or at t0; a hung `off` still restores the radio; every non-measurable read is `not_measured` or a refusal rather than a zero; the A234 merge carries both sides' hunks intact; the reinterpretation in §4 is ACCEPTED so the registration file is correctly untouched. The items in §6 are non-blocking.

NOT EXECUTED: live `/usr/bin/log`, `networksetup`, `sudo`, `launchctl`; `tests/test_magistrate_watchdog*.py`, `tests/test_install_magistrate_watchdog.py`, `tests/test_docs_freshness.py`; the `render_policy()` byte-equality check (record 30 V6); a read of `pilot_protocol_v3.json` and `night_gate.py:55-75`.

Judge: Fable 5.1, cold, session ended after this file was written and the scratch worktree removed.
