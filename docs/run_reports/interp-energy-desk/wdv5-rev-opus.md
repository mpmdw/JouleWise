# Cold review: `ops/2026-11-10-watchdog-v5-installed` (Opus 5.5)

Date: 2026-11-10 11:21 PST (from `date`). Reviewer: Opus 5.5, cold seat. I did not
read Sol's seat output before running my own probes.
Reviewed: `59dd6e2b8` (fix) and `7b2f2a571` (report) against `origin/main` `4bd293caa`.
(`85612ccc2`, Sol's desk report, is docs only.)
Clone: `jw-wt/opus-wdv5-rev` (`--shared` from `jw-wt/handoff`). TMPDIR `/private/tmp/opus-wdv5-rev`.
Every custody, HOME, LaunchAgents, ps and launchctl used here was synthetic. I read no real
custody, archive or restricted path, and I signalled no process.

## Verdict: ADMIT-WITH-FIXES

The parser fix is correct, minimal, and matches the lane's contract exactly. It
unstrands the watchdog without changing any release rule. Deploying it to the
watchdog's checkout should by itself clear the stranded MBP. A window that finished more
than two days ago, with `courier.sent`, is past completion and the deadman tail, so
`plan_span_active` is False and the installed plan no longer fences. The unstrand
script is safe in the fail-closed sense and keeps the records blinded. But in the
setting where it will most likely be used (run through a wrapping shell, such as an
agent Bash tool, `ssh host '...'`, `sudo` or `caffeinate`) it refuses itself (F1).
That should be fixed before anyone relies on it. F2 is a latent fail-open in main's
driver and needs a small guard. F3 to F5 are minor.

## What changed (independently established)

- `joulewise/night_gate.py`: `NightPlan.from_mapping` gains an optional `ac_powermode` key.
  It accepts integer 0 or 2 only (`type(mode) is int`), in any plan class. A new dataclass
  field `ac_powermode: int | None = None` stores it.
- `joulewise/night_plan_writer.py` omits the field when it is `None`, so legacy bytes are unchanged.
- `scripts/magistrate_watchdog.py` is **not** modified. `load_plans` (`:773`) and
  `_installed_agent_plans` (`:829`) already called the same `NightPlan.from_mapping`. The installed
  reader was never v2-only. It rejected the key because the shared dispatcher did not know it.
  The brief describes `_installed_agent_plans` as v2-only, and Sol's report corrects that. I agree with the correction.
- New `scripts/post_window_unstrand.sh` and its tests. Sibling CLI tests now isolate HOME.

## 1. Correctness

**Parser parity with the arming lane.** `git diff --no-index joulewise/night_gate.py
<(git show origin/lane/2026-11-08-r1-arm-fixes:joulewise/night_gate.py)` differs only in
comments, the `DEFAULT_AC_POWERMODE` constant and two driver reason codes. `from_mapping`,
`_plan_ac_powermode`, `_PLAN_KEYS` and the hazard_window validator are byte-identical.
The lane's `night_plan_writer.py` diff against main is the same one-line change. So any
plan that the lane's arm route (`joulewise/align/r1_arm.py:prepare`, which itself calls
`NightPlan.from_mapping`) or the lane's installer accepts now parses on main, in discovery
and in the installed reader alike.

**My probe (`probe_wdv5.py`, synthetic).** It builds the R1 plan exactly as the lane's
`r1_arm.prepare` does: v5, `ac_powermode: 0`, `member_count 0`, `g10 False`, `pack_sha256 None`,
`registration None`, `settle_s 0` and stage kind `r1_rehearsal`. This is not the W1-shaped
`fake_window` fixture that Sol's tests use. I installed it in both synthetic plists only.

| Probe | Branch | Base `origin/main` |
|---|---|---|
| R1 lane-shape parses (installed, no errors) | PASS | ERROR `plan keys are not exact (extra=["'ac_powermode'"])` |
| `ac_powermode` 2 and absent accepted | PASS | FAIL (installed_agent_fence error) |
| 20 mutations hold, with 2 installed errors and `HOLD_UNSAFE` | PASS | n/a |

The mutations, all fail-closed on the branch: `True`, `False`, `1`, `3`, `-1`, `2.0`, `"0"`, `null`,
`2**64`, an unknown sibling `ac_powermodes`, `AC_POWERMODE`, `"ac_powermode "` (trailing space),
a dropped `hazard_window`, schema `v4` with a HAZARD class, `schema_version 4`, an unknown hazard_window key,
hazard_window schema `v2`, a future `authored_epoch_s`, a relative `custody_root` and a NaN `t0`. I found no
malformed plan that now passes. The only newly accepted inputs are the key with value exactly
int 0 or 2, which is the lane contract.

Note on the contract: it accepts the key on every class, v2, v3 and v4 included, as the lane does.
This is not a divergence, but see F2.

## 2. Release semantics

The watchdog's code is untouched, so the only question is whether an installed-only plan
now reaches the same predicates that a discovered plan reaches. I ran one timeline under
three placements of the same R1 plan: discovered only (no plists), installed only (both
plists, custody outside discovery's glob) and both. Each tick recorded
`(decide.state, decide.launch, plan_span_active, #terminal latches)`. The monotonic clock
advanced with wall time.

```
pre0 (t0-lead-1)        LAUNCHING  launch  span=F  latch=0
pre1 (t0-lead)          FENCED     -       span=T  0
pre2 (t0+10)            FENCED     -       span=T  0
pre3 (ended-1)          FENCED     -       span=T  0
ended_no_courier        FENCED     -       span=T  0
courier, busy census    HOLD_CENSUS -      span=T  0
courier, clean census   LAUNCHING  launch  span=F  1
pre_completion          LAUNCHING  launch  span=F  1
post_completion         LAUNCHING  launch  span=F  1
post_deadman            LAUNCHING  launch  span=F  1
```

All three placements produced **identical** sequences (`assertEqual` passes). Release happens
at the first tick with `chain.exited`, `courier.sent`, a terminal `result.json` and a clean census,
and no earlier: the busy-census tick holds. The latch is one-way. With an **open chain**
(`chain.started` without `chain.exited`) the installed-only plan stays FENCED with span True and
latch 0 through post-deadman, so the in-span fence is intact. Sol's
`test_terminal_release_keeps_all_existing_evidence_and_process_gates` also covers the removal of each marker
and each census or process seam. On base, the same probe errors at parse, so the installed
placement could only ever produce `HOLD_UNSAFE`, which matches the production strand.

## 3. Blinding

- The script checks `night/{chain.exited,result.json,courier.sent}` with `[[ -e ]]` only. Neither the
  embedded Python nor the installer's `--uninstall` path opens a night record. The installer reads only
  `night_plan.json` for `plan_id`, and a plan is not a blinded record. The process probe never prints argv.
  The event follower prints only `FROM -> TO` strings that match `[A-Z][A-Z0-9_]{0,63}` from
  `kind == "transition"` rows.
- In every one of my script probes the stdout and stderr contained no marker payload (`leak=False`).
- The tests write and read only synthetic temp custody. `result.json` content appears only in the
  watchdog tests' synthetic fixtures, and the watchdog's own existing release code reads that by design.
  Nothing touches a real HOME. The branch also *improves* isolation:
  `HandoffCliDefectTests`/`MagistrateWatchdogCliTests` previously reached the real `~/Library/LaunchAgents`.

Blinding: PASS.

## 4. Operator safety of `post_window_unstrand.sh`

Probe file: `probe_unstrand.py`. It uses a synthetic custody and HOME, and real `/bin/ps` only in a1 and a2,
where the output is consumed only by the script, which prints no argv.

| # | Case | Result |
|---|---|---|
| a1 | direct argv, real ps, clean synthetic custody | rc 0 (dry run) |
| **a2** | same command inside `zsh -c 'cd /; <script> … <custody>; exit $?'`, real ps | **rc 1 "a chain, driver or window process is still present."** |
| b1 | custody passed via symlink; live R1 child `align_r1_rehearsal.py --output <link>/night/align-r1` | **rc 0 (missed)** |
| b2 | same child naming the resolved path | rc 1 (caught) |
| b3 | only the inner `/bin/zsh -f …/night_chains/align_r1_rehearsal.zsh` alive | rc 0 (missed) |
| c1 | ps row with a pid and an empty command | rc 1 (unproven; fail-closed) |
| d1 | operator names an old finished custody while a live plan's plists are installed | rc 1 "belongs to a different plan" |
| d2 | correct custody | rc 0 |
| e1 | relative custody with `CDPATH` set | rc 1 (`cd` echoes to stdout and the path is garbled, so it fails closed) |
| — | ps rc≠0 / stderr / empty / garbage; missing marker; wrong-plan plist; unreadable plist; still loaded after bootout | all refuse (Sol's tests, re-run green) |

So a live chain or driver refuses. An unreadable ps refuses. A wrong custody refuses whenever plists
naming another plan are installed, and when no plists are installed `--uninstall` is a no-op. The
installer's `uninstall()` is plan-independent: it boots out both labels whatever `--plan` it is given.
That makes the script's plan-identity check the only guard against tearing down another window, and the
check is correct (`installed.resolve() == root/night_plan.json`, with both sides resolved).

## Findings

### F1 (MEDIUM, operability; fix before relying on the script). The script refuses itself under any wrapping shell
The process scan excludes only `$$` and the embedded Python's pid. Any **ancestor** whose argv
contains the custody path counts as "a process naming custody". That includes a non-exec `zsh -c`
compound command (the shape an agent Bash tool or a `ssh mbp '…'` remote command produces), `sudo`,
`caffeinate -i` and `time`.
Repro: a2 above. With real `/bin/ps`,
`/bin/zsh -c "cd /; /bin/bash scripts/post_window_unstrand.sh --events X --wait-seconds 0 $S; exit \$?"`
exits 1 with "process is still present", while the direct argv form exits 0.
The failure is fail-closed (safe), but it defeats the recovery in exactly the setting where a
magistrate or lead would run it. Fix: read `pid=,ppid=,command=`, walk from `$$` up to pid 1 and
exclude those ancestors. None of them can be the chain or the driver. Add a test that runs the script
inside a `zsh -c` compound command.

### F2 (LOW–MEDIUM, latent fail-open in main's driver). `ac_powermode: 2` is accepted but not enforced on main
On base, a plan that declares `ac_powermode` was refused at parse. On the branch, main's
`scripts/run_night.py` loads it, and main has **no** AC-powermode admission
(`grep -c powermode scripts/run_night.py joulewise/night_agent_install.py joulewise/arm_readiness.py
joulewise/arm_census.py` gives 0 0 0 0). The admission (`_admit_ac_powermode`, HIGH-3) exists only on
`origin/lane/2026-11-08-r1-arm-fixes`.
Repro:
```
python3.13 -B - <<'EOF'   # in the branch checkout
import json,tempfile,pathlib
from tests.test_night_gate import HazardPackPlanTests
from scripts import run_night
t=HazardPackPlanTests("setUp"); t.setUp(); m=t.mapping(); m["ac_powermode"]=2
p=pathlib.Path(tempfile.mkdtemp())/"night_plan.json"; p.write_text(json.dumps(m))
print(run_night._load_plan(p).ac_powermode)   # branch: 2 ; base: PlanError extra=['ac_powermode']
EOF
```
This is not reachable today. No main producer emits the key, and `validate_install` pins
`repo_head` to the installing checkout, so a lane plan cannot be installed from main. It becomes
reachable as soon as anything on main writes the key before the lane's admission merges. Fix: keep
the parser change, because the watchdog and other readers need it. In main's `run_night` preflight/run
(and `validate_install`), refuse `plan.ac_powermode == 2` with a named reason
until the HIGH-3 admission lands. Value 0 is equivalent to absent on main and can stay admitted.
Do **not** narrow the parser to 0. That would re-strand the watchdog on any W1 plan that declares 2.

### F3 (LOW). The process match uses only the resolved custody path
`str(root) in command` uses `pwd -P`. A live child whose argv names the custody through a
symlinked alias is missed (b1). An orphaned inner R1 chain is missed too (b3), because it names only
`scripts/night_chains/align_r1_rehearsal.zsh`. Both are defence-in-depth gaps: for HAZARD_PACK,
`chain.exited` is written only after the driver's group census proves the group gone (otherwise it
writes `chain.unkilled`). Fix: also match the literal argument, the plan's declared `custody_root`
(reading the plan is not blinded) and the chain basename `night_chains/`.

### F4 (LOW, hardening nits)
- `ps` is resolved from `PATH`, which the tests need. Prefer `${UNSTRAND_PS:-/bin/ps}` with the test
  setting the override, so that an operator PATH cannot substitute another `ps`.
- `custody="$(cd "$custody" && pwd -P)"` should be `CDPATH= cd -- "$custody" >/dev/null && pwd -P`
  (e1 fails closed today, but by accident). An argument that begins with `-` (and not `--`) is taken as the path.
- If the event follower dies after a successful `--go` (for example a pathological events line raising
  `RecursionError`), the script exits nonzero although the uninstall succeeded. Print the success line before
  following (it already does) and make the follower's own failure non-fatal, or label it.

### F5 (INFO). Scope of the helper
- It requires `chain.exited`, so it cannot be used for the `null_window` terminal shape (a refusal before
  the chain claim) that `terminal_window_release` allows. That is conservative. State it in the usage text.
- With the parser fix deployed, the watchdog releases on its own (§2). The helper is then a fallback, not
  the primary remedy. Sol's report says so in its limits. The installed watchdog service must run a checkout
  that contains `59dd6e2b8`.

## Tests I ran (native, this Air, `python3.13` 3.13.18, cwd = branch checkout)

`python3.13 -B -m unittest tests.<module>`, one module per command:

| Module | Result |
|---|---|
| test_magistrate_watchdog | 155 OK (1.685 s) |
| test_magistrate_watchdog_cli | 8 OK (11.442 s) |
| test_magistrate_watchdog_b6 | 9 OK |
| test_magistrate_watchdog_span | 24 OK |
| **test_magistrate_watchdog_yield** | **20 OK (5.909 s)**. Sol's three failures pass natively. |
| test_magistrate_watchdog_v5 | 4 OK |
| test_install_magistrate_watchdog | 10 OK |
| test_magistrate_desk_fence | 42 OK (29.4 s) |
| test_night_gate | 113 OK |
| test_night_plan_writer | 11 OK |
| test_arm_retry | 36 OK |
| test_post_window_unstrand | 9 OK (5.0 s) |

Total: 441 OK, 0 failed. I also ran the three tests by name:
`tests.test_magistrate_watchdog_yield.DriverRecordsToWatchdogTests.{test_a_chain_stop_is_released_on_the_driver_records,
test_a_live_process_naming_the_custody_holds_the_release,
test_an_empty_window_alerts_ed_in_window_and_is_released_after_delivery}` gave 3 OK (5.96 s). This confirms that Sol's
failures were its sandbox's `/bin/ps` denial and not a product defect.

Other checks: `bash -n scripts/post_window_unstrand.sh` OK. `git diff --check origin/main...HEAD` OK.
shellcheck is not installed. My probes were `probe_wdv5.py`, 5 tests, all OK on the branch. On base
the same 5 give 3 errors and 1 failure, which reproduces the strand. `probe_unstrand.py` produced the
table in §4. Both lived in the session scratchpad and are not committed.

## Required before merge (ADMIT-WITH-FIXES)
1. F1: exclude the script's ancestors from the process scan, and add a wrapped-shell test.
2. F2: a refusal in main's driver for a declared `ac_powermode: 2` (no parser narrowing).

F3 and F4 are recommended and can ride along. F5 is a note for the usage text.
