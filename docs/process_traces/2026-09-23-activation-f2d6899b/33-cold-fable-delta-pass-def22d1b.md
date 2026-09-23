# Cold final pass (Fable 5.1), gate-ledger row 10 — head def22d1b (post-review commits on 665d3bd7, branch feat/2026-09-23-a271-corecaptured)

Judge: Fable 5.1, cold, one non-interactive session, no subagents, no background tasks, every probe in the foreground. Worktree `/Users/edr/code/wt-f2d6899b-finalpass2`, checked out detached at def22d1b, tree clean before and after; returned to detached 665d3bd7 at the end. Nothing committed. Wall budget 25 min; used ≈ 14 min.

## 0. Contamination disclosure

Context on arrival: the two CLAUDE.md files (global and repo) and the auto-memory `MEMORY.md` index (one-line pointers only; no memory file bodies read). No loop context, no seat transcripts, no Opus counter-review, no PR body. Inputs read this session: §4 and §6 of `/tmp/f2d6899b/finalpass-verdict-665d3bd7.md`, `git diff 665d3bd7..def22d1b` (6 files, +43/−14), `joulewise/evidence_night.py` 840–930 and 1047–1130 and 1604–1625, `joulewise/night_gate.py` 1500–1535, `joulewise/corecaptured_loop.py` head, the two doc paragraphs and their surrounding first-use context, `tests/test_evidence_night.py` setUp and the new test.

## 1. Change-by-change correctness (question 1)

### S-1 rehearsal licensing (`evidence_night.py` check(), lines 1096–1108)

Code as landed:

```python
actuator = corecaptured_actuator or production_corecaptured_actuator()
rehearsal_on_real_machine = (record["fake_launchctl"] and corecaptured_actuator is None)
if (nothing_loaded and not rehearsal_on_real_machine
        and all(row["verdict"] == "pass" for row in checks.values())):
    inspect("corecaptured", lambda: corecaptured_arm_check(actuator))
else:
    inspect("corecaptured", lambda: corecaptured_arm_check(actuator, read_only=True))
```

`record["fake_launchctl"]` is `str(launchctl_bin) != "launchctl"` (line 1054), the same predicate that already decides `armable` vs `rehearsal_ready` (lines 1123–1124). So the guard reuses the lifecycle's existing definition of "rehearsal" rather than inventing a second one. Correct.

**Can the guard be bypassed?** Only by passing a non-None `corecaptured_actuator` together with a fixture launchctl. That parameter is Python-only: `main()` builds kwargs from argparse (`operation(**args)`, line 1609) and the `check` subparser adds only `--candidate` and `--launchctl-bin` (lines 1599–1601); there is no CLI or environment route to inject an actuator. A Python caller that injects `production_corecaptured_actuator()` explicitly is choosing to actuate; that is not a bypass of a guard, it is the documented fake-actuator seam. No bypass from the CLI or from the magistrate/watchdog entry points. **Verified in code, not by grep alone.**

**Can it wrongly block a real arm?** With `launchctl_bin == "launchctl"` (the CLI default) `fake_launchctl` is False, so `rehearsal_on_real_machine` is False regardless of the actuator argument, and licensing is exactly the 665d3bd7 rule (nothing loaded, every earlier row passed). No. The one edge: a caller passing an absolute path to the real binary (e.g. `/bin/launchctl`) is treated as a rehearsal — but that was already true at 665d3bd7 for `armable` (such a check can never arm), so the guard is consistent with the existing convention, not a new block.

**Behavioural change, stated plainly:** a rehearsal on a machine with a live corecaptured loop (>2 spawns in 10 min) now refuses `night_refused_not_quiet … not licensed` and is not `rehearsal_ready`, instead of toggling the real radio. A rehearsal with ≤2 spawns passes with `remediation: not_licensed`. The read-only path still runs the real `/usr/bin/log show` (a read, no actuation). That is the intended cure.

**Test:** `test_corecaptured_rehearsal_never_actuates_production_machine` patches `production_corecaptured_actuator` to a fake, passes no `corecaptured_actuator` kwarg (verified: `self.kw` at lines 257–259 contains neither `launchctl_bin` nor `corecaptured_actuator`; the fixture launchctl arrives via the harness default, and the test asserts `self.kw["launchctl_bin"] != "launchctl"`), and asserts no `networksetup`/`sudo` argv. **Mutant executed:** removing `and not rehearsal_on_real_machine` makes exactly that test fail (1 failed, 15 passed). The regression test is live.

### S-3 shared constants (`corecaptured_loop.py`, `night_gate.py:1526`, `evidence_night.py` 882/889/899/916/923)

Each replacement is value-identical: `600`→`WINDOW_S=600`, `> 2` / `<= 2`→`SPAWNS_MAX=2` (three sites, two files), `sleep(8)`→`WIFI_OFF_S=8`, `sleep(180)`→`POST_TOGGLE_WAIT_S=180`, `>= 1`→`POST_TOGGLE_SPAWNS_MIN=1`. Both modules already imported `corecaptured_loop` (night_gate.py:28, evidence_night.py:22). No control-flow change. See §2 for the mutants.

Residual (recorded, non-blocking): `LOG_ARGV` still carries the literal `"--last", "10m"` and the refusal strings say "10 minutes"; `WINDOW_S` and the `log show` argument can still drift apart. The "one home" claim is true for the five numbers the commit names, not for the log-read window argument. Same state as 665d3bd7.

### Docs (S-2, N-1, §6.2)

See §3.

## 2. Constants refactor: behaviour-identical, mutants (question 2)

Regression set at def22d1b (exact command from the brief):

| Command | Result |
|---|---|
| `pytest tests/test_corecaptured_loop.py tests/test_night_gate.py tests/test_arm_retry.py tests/test_docs_freshness.py` | 154 passed, 546 subtests passed |
| `pytest tests/test_evidence_night.py -k corecaptured` | 16 passed, 111 deselected |

Tests pin literals, not symbols: no test file references `SPAWNS_MAX`, `WINDOW_S`, `WIFI_OFF_S`, `POST_TOGGLE_WAIT_S` or `POST_TOGGLE_SPAWNS_MIN` (grep over `tests/*.py`); the boundary tests assert `fake.sleeps == [8, 180]`, `off` sent iff `i == 3`, `refusal iff i == 3`. So the exactly-two boundary tests still pin the values, not the names.

Mutants, one sed per constant, tests re-run, file restored by `git checkout` after each (tree verified clean):

| Mutant | loop+gate files | evidence_night `-k corecaptured` | Killed? |
|---|---|---|---|
| `SPAWNS_MAX` 2→3 | 2 failed | 3 failed | yes |
| `SPAWNS_MAX` 2→1 | 1 failed | 1 failed | yes |
| `WIFI_OFF_S` 8→9 | pass | 1 failed | yes |
| `POST_TOGGLE_WAIT_S` 180→179 | pass | 1 failed | yes |
| `POST_TOGGLE_SPAWNS_MIN` 1→2 | pass | 1 failed | yes |
| `POST_TOGGLE_SPAWNS_MIN` 1→0 | pass | 3 failed | yes |
| `WINDOW_S` 600→601 | pass | pass | **survives** |
| `WINDOW_S` 600→599 | pass | pass | **survives** |
| `WINDOW_S` 600→300 | 6 failed | 6 failed | yes |

Reading: the four thresholds/waits that the ruling-16 boundary tests were written for are pinned to the exact value. The 10-minute window is pinned coarsely (300 dies, ±1 s survives): no test places a spawn at exactly `now−600` vs `now−601`. This gap is pre-existing (the literal `600` at 665d3bd7 had the same tests) and the refactor neither widened nor narrowed it. Non-blocking; a one-line boundary test in `test_corecaptured_loop.py` would close it and is a candidate for the v4 follow-up lane.

## 3. Docs against the code and the first-use test (question 3)

**Zero-capture refusal definition (NIGHT_HANDBACK.md:57, runbook:1856), S-2.** Adds "or a `corecaptured` respawn loop" to the not-quiet cause list. True: `night_gate._check_machine` returns `Refusal("night_refused_not_quiet", "corecaptured: N launchd spawns …")` (1526–1530), which is one of the five listed codes, so the "five refusal codes" count is unchanged and correct. Both copies are byte-identical to each other (diff shows the same hunk in both files).

**Handback paragraph (NIGHT_HANDBACK.md:267–280), N-1 and §6.2.**
- "Both the pre-arm check … and the night gate at `t0` read `/usr/bin/log show --last 10m …`": true; both call `corecaptured_loop.LOG_ARGV` (night_gate:1510, evidence_night:867) and the argv in the doc matches `LOG_ARGV` verbatim.
- "toggles Wi-Fi once if it counts at least three spawns": `before.count > SPAWNS_MAX(2)`. True.
- "(on a real arm, never a rehearsal with a fixture `launchctl`)": exactly the S-1 guard. True.
- "waits at least three minutes after Wi-Fi is back on, and counts only new spawns": `completed = now()` is taken after the `on` command in the `finally`, then `sleep(POST_TOGGLE_WAIT_S=180)`, then `observe(after=completed)`. True.
- "One or more new spawns triggers `sudo -n …restart-fseventsd` once and refuses … `night_refused_not_quiet`": `after.count >= POST_TOGGLE_SPAWNS_MIN(1)`. True.
- There is no second copy of this paragraph in the runbook (grep for "toggles Wi-Fi once" hits only NIGHT_HANDBACK.md), so no cross-doc drift was introduced. `test_docs_freshness.py` passes, so the generated ARM-RETRY-POLICY block (lines 70–147) still matches `arm_retry.render_policy()`.

**First-use test.** The two glosses the prior pass asked for are present at first use *within the paragraph*: "the **arm check**: the checks that run before a night is installed" (line 270) and "`night_refused_not_quiet` (the refusal code for a machine that is not quiet)" (line 278). The §6.2 ask is met as written.

Document-level residuals (recorded, not blocking, not part of the §6.2 ask):
1. "arm check" first appears in the document at line 86, inside the generated refusal-code table, unglossed; the gloss arrives at line 270. Fixing that means editing the policy text in `arm_retry.py` and regenerating both blocks, which is a policy-text change, not a docs-only one; leave for the v4 lane. `night_refused_not_quiet` at line 86 is in a definitions table, so it is glossed at its own first use.
2. The new phrase "a rehearsal with a fixture `launchctl`" introduces "rehearsal" and "fixture" without a gloss; "rehearsal" is used at line 66 ("a rehearsal chain") but never defined. A reader with no project grounding can infer "dry run" and "stand-in for the launchctl command"; it is inferable, not built. Suggested wording for the next touch: "(on a real arm, never a rehearsal, meaning a dry run whose `launchctl` is a test stand-in)".

## 4. Regressions (question 4)

None found. The specified test set passes in full (§2 table). The S-1 test is the only new test and is proven live (§1). The eight killed mutants show the refactor did not loosen any pinned value. The tree was clean after every mutant restore (`git status --short` empty, checked after each loop).

## 5. NOT EXECUTED

Live `/usr/bin/log`, `networksetup`, `sudo`, `launchctl`; the full `tests/test_evidence_night.py` (only `-k corecaptured`, per the brief); `tests/test_magistrate_watchdog*.py`, `tests/test_install_magistrate_watchdog.py`; the Opus counter-review text itself (not provided; I judged the cures against the code, not against its wording); the `pilot_protocol_v3.json` bytes.

## VERDICT

**MERGE.**

Grounds: S-1 is correct, has no CLI-reachable bypass, cannot block a real arm (`launchctl_bin == "launchctl"` leaves licensing exactly as at 665d3bd7), and its regression test fails without the guard. S-3 is value-identical at every site, both modules import the shared home, and mutants on `SPAWNS_MAX` (both directions), `WIFI_OFF_S`, `POST_TOGGLE_WAIT_S` and `POST_TOGGLE_SPAWNS_MIN` (both directions) all die under the existing literal-pinned boundary tests. The docs state what the code does at every checked clause and carry the two glosses the prior pass asked for. The specified regression set is green.

Non-blocking residuals for the v4 follow-up lane, in priority order: (a) a `WINDOW_S` exact-edge test (±1 s mutants survive); (b) `LOG_ARGV`'s `"10m"` is a second copy of the window; (c) document-level first use of "arm check" is in the generated table at line 86; (d) gloss "rehearsal"/"fixture launchctl" in the handback paragraph.
