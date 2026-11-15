# Powermetrics orphan reap (RL-91, RL-96): executing cold review

2026-11-12, Fable 5.2 (cold reviewer, Air). I did not write this; Opus built it.
Blind: code only. No v4 outcome and no energy value was read. No real `sudo` was run; no MBP access.

## Verdict: ADMIT-WITH-FIXES

The reap is correct where it is exercised: on a capture that succeeds the wrapper changes nothing, the matcher
signals only this capture's own `-o` path, and a failed capture's sampler is reaped, proven gone and recorded.
It may ride tonight once three things are true. None of them changes a line of `powermetrics_reap.py`.

1. **A test pins the exact `-o` match.** Three wrong-match mutants survive the test file (prefix, no `-o`
   anchor, basename). The code is right; nothing holds it there. Test-only. (Finding 1)
2. **`sudo -n -l /bin/kill` exits 0 on the MBP before the arm**, checked by listing over SSH. The R1 night does
   not run the W-2 preflight, and on the R1 path a missing rule turns one timed-out capture into a refusal of
   every remaining member. (Finding 2)
3. **A PR exists and CI is green.** There is no PR for the branch yet, so RL-91's "green" is not met.

Four further findings are owed before W1 signing, not tonight. Two of them are for the research lead: the
refusal does not reach the next member in W1, and one failed `ps` poisons the process for good.

- **Reviewed:** `fix/2026-11-12-powermetrics-orphan-reap` @ `b4521cb8e546b2aed03338b8e6c6346b0c3a9a6f`, one
  commit on presign `22f438fd3`. Ten files, +616 / -7.
- **Rulings read:** RL-91 and RL-96 in `origin/audit/2026-11-10-fable` @ `cc8825611`.
- **Byte checks:** `joulewise/adapters/powermetrics.py` is sha256 `70f47086…e5e4` (the RL-58 pin) and
  byte-identical to base. `configs/align/v4/r1_runtime.json` and `joulewise/align/apple/r1_runtime.py` are
  byte-identical to base. No changed file is in `R1_EXECUTED_SOURCES` (condition 13).
- **Not done:** the sudo rule on the MBP, CI, and Part A itself.

## RL-96 terms

| # | Term | Result | Evidence |
|---|---|---|---|
| 1 | Calls the parent; adds only post-exception handling; success is identical | PASS, with two notes | See "Term 1" below. |
| 2 | Signals only this capture's own `-o` path, never by name | PASS in code; **test gap** | See "Term 2" below and Finding 1. |
| 3 | Absence proven by census and recorded; the original exception propagates | PASS for a member's own capture; gap on the cooldown path | See "Term 3" below and Finding 5. |
| 4 | Unprovable absence refuses as NUMBER_INTEGRITY; registry row; hazard scan; executed closure | PASS, row wording to correct | See "Term 4" below and Findings 3 and 6. |
| 5 | `sudo -n /bin/kill` in the W-2 preflight listing, listed and not run | PASS | `host_privilege_rules()` adds `('powermetrics_reap_kill', KILL_PREFIX)`; the preflight runs `/usr/bin/sudo -n -l /bin/kill`. `tests.align.test_v4_arm_watchdog_check` (80 tests) passes: 7 rules, each refusing by name when missing. |
| 6 | One deviation row drafted | **NOT FOUND** | No row text is in the commit, the commit message or the builder's scratch. A draft is offered below. Owed before signing, not tonight. |
| 7 | Cold review; the `adapters/__init__.py` test pin follows | PASS | This document. Pin list below. |

### Term 1

`_run_bounded_capture` calls `super()` inside a `try` and returns its value untouched. The handler runs only
in `except BaseException`.

- **The identity test compares bytes.** `test_successful_capture_is_identical_with_and_without_the_wrapper`
  compares the `bytes` returned by `_run_bounded_capture` for the base class and the production class, and
  both against `FIXTURE.read_bytes()`. It also compares the `IdleBaseline`, the device metadata and the
  pending-capture names. A mutant that strips trailing whitespace from the returned bytes is killed, so the
  comparison is byte-sensitive.
- **It does not compare the artifact on disk**, because it passes `context=None`. I ran that myself: a full
  `run_benchmark` with the base class and with the wrapper, same fake sampler. Every file under `raw/` has the
  same sha256 (`powermetrics_idle.plist`, `powermetrics_idle_post.plist`, `powermetrics.plist`), and
  `metadata.json`'s `device` block is equal with no `capture_reaps` key.
- **Note A: the subclass overrides more than RL-96 names.** RL-96 says "overrides `_run_bounded_capture`
  only". The class also overrides `_command` and `_probe_command` (each records the output path and returns
  the parent's list unchanged), `_probe_capability` (reaps after a probe timeout) and `_ensure_capability`
  (the poison check). The first two are how the wrapper learns the path without touching the parent. The
  probe reap is a scope extension to the same defect in the same file. I accept all four; the deviation row
  must name the probe.
- **Note B: two branches run before the parent**, the `if UNPROVEN_REAPS` checks. They read an empty list in
  any process that has had no unprovable reap. See "The process-wide refusal".

### Term 2

The census reads `/bin/ps -axww -o pid=,command=` and matches a row when the command holds the adapter's
executable and either ends with ` -o <path>` or contains ` -o <path> `. The path is the adapter's own
`tempfile` name, `joulewise-powermetrics-<random>.plist`.

I fed `_census` a table of fifteen crafted rows. It matched four: the sampler, the `sudo` wrapper of the same
capture, the sampler with trailing blanks, and a shell wrapping the same command line. It matched none of
these:

| Row | Why it could be confused |
|---|---|
| `-o <path>2`, `-o <path>.bak` | same prefix |
| `-o /private<path>` | this path is a suffix of another |
| `-o <path minus six characters>` | another path is a prefix of this one |
| the night's sidecar, `-o /tmp/r1-sidecar/powermetrics.plist` | same executable, streaming |
| another member's capture, `-o …/joulewise-powermetrics-zzz999.plist` | same executable, same directory |
| `/usr/bin/tail -f -o <path>` | the path, not the executable |
| `--note <path>` after another `-o` | the path, not as the `-o` value |
| `x-o <path>`, `-o<path>` | `-o` glued to a token |
| `/opt/other/powermetrics … -o <path>` | another executable |

- **The sidecar on the R1 night** is a base-class adapter built directly in `r1_runtime.py:1467`. It streams
  to its own path and is never matched.
- **Root arguments are visible to the census.** `/bin/ps` is setuid root on macOS, so a non-root caller reads
  a root process's arguments. Checked on the Air; a census that could not would read "absent" falsely.
- **Pid reuse** between a census and its kill is the residual. Each signal round re-reads the table, so the
  gap is one `ps` and one `sudo` spawn.

### Term 3

I ran `run_benchmark` end to end with a fake `subprocess.run` that times out one bounded capture.

| Capture that times out | Census | Base class | Wrapper | `device.capture_reaps` in `metadata.json` |
|---|---|---|---|---|
| pre-run idle | proves absent | failed / `unknown_error` | failed / `unknown_error` | one record, `absent: true` |
| pre-run idle | cannot answer | failed / `unknown_error` | **unsupported / `telemetry_unavailable`** | one record, `absent: false` |
| post-run idle | proves absent | succeeded | succeeded | one record, `absent: true` |
| post-run idle | cannot answer | succeeded | **succeeded** | one record, `absent: false` |

- **Where it is recorded.** `_reap_capture` appends to the adapter's `_device_metadata["capture_reaps"]`. The
  controller holds that same dict and writes it as `device` in `metadata.json`, so the record reaches the
  member's bundle whether the member fails or succeeds.
- **The original exception propagates when absence is proven.** Row 1 is identical to base.
- **The campaign cooldown gate is the gap.** `run_campaign` resolves its own adapter there and discards it,
  so a proven reap on that path is written nowhere. (Finding 5)

### Term 4

- **Registry.** `configs/gates/hazard_refusals.json` gains the module in its scan list and two rows:
  `<reraise>` as INTERNAL, and `PowermetricsOrphanRefusal|TELEMETRY_UNAVAILABLE` (count 2) as
  NUMBER_INTEGRITY. `tests.hazards.test_refusal_allowlist` passes (24 tests, 1 skipped), on the branch and on
  the merge with `bb6394f2b`.
- **Closure.** `EXECUTED_CLOSURE` and `registration_receipt.json` (a null row) list the module.
  `tests.align.test_v4_registration`, `test_v4_executed_closure` and `test_v4_dynamic_closure` pass.
- **Host command sites.** Four rows; `tests.test_host_command_sites` passes.
- **The refusal is raised.** A mutant that drops it is killed by three tests.
- **The row's `protects` text overstates.** (Finding 6)
- **Two refusals have no row.** `_ensure_capability` and `_probe_capability` refuse by returning
  `AdapterResult(ok=False, …)`, which the scan does not count. (Finding 6)

### Term 6: a draft row

None was found, so this is offered for the lead to edit. It states what the code does today.

> The capture adapter is wrapped. `resolve_telemetry` builds `ReapingPowermetricsTelemetryAdapter`
> (`joulewise/adapters/powermetrics_reap.py`), a subclass of the calibrated adapter. The estimator file
> `joulewise/adapters/powermetrics.py` and its acceptance pin (`70f47086…e5e4`) are unchanged, and a capture
> that succeeds returns the same bytes and writes the same artifact. After a bounded capture raises, or the
> capability probe times out, the wrapper finds the process whose arguments carry that capture's own `-o`
> path, sends INT, TERM and KILL through `sudo -n /bin/kill`, and proves it gone by a process census that
> must list the caller. The reap is recorded in the member's `device.capture_reaps`. If absence is proven the
> capture's own exception stands. If it cannot be proven the capture refuses (`PowermetricsOrphanRefusal`,
> NUMBER_INTEGRITY) and every later capture, probe and sampling start in the same process refuses. The
> refusal does not carry to a later process.

The last sentence is true of the code as built. Finding 3 asks whether it should stay true for W1.

### Term 7: every pin, receipt or test naming `adapters/__init__.py`

Base sha256 `32917f9f…d54a`, branch `ccea8352…f05c`. A search of the tree for the base digest and the base
blob id finds nothing after the change.

| Where | What it holds | Issued acceptance or condition 13? |
|---|---|---|
| `tests/align/test_measurement_core_boundary.py` `test_wp14_c_untouched_execution_path_files` | the live digest, moved `32917f9f` to `ccea8352` | No. A test pin. It passes. |
| `joulewise/align/apple/v4_registration.py` `EXECUTED_CLOSURE` | the path | No digest. |
| `configs/campaigns/align_v4/registration/registration_receipt.json` | the path, `null` | Template row, unsigned. |
| `configs/gates/hazard_refusals.json` | the path, in the scan list | No digest. |
| `configs/pins/registry.json` | `file:` and `file@c2748534…:` pin names | The second is a historical commit pin. `tests.test_digest_pin_census` and `tests.test_repin` pass. |
| `docs/align/v4/dynamic_closure_trace.json` | the path, in a saved trace | No digest. The trace predates the new module. (Finding 8) |
| `configs/campaigns/d117_*/…`, `configs/campaigns/v5_claim_25g83/sealed_inventory.json` | `ccc3710f…9db5` | Historical receipts of an older file; already not the base bytes. |
| `docs/reviews/2026-07-13-…`, `docs/process_traces/…`, `docs/legacy/…` | prose and old manifests | No. |

The calibration acceptance pins four files (`ESTIMATOR_CODE_PATHS`): `powermetrics_fiducial.py`,
`uncertainty_evidence.py`, `adapters/powermetrics.py`, `reduce.py`. `adapters/__init__.py` is not one, and it
is not in `R1_EXECUTED_SOURCES`. `docs/align/pilot_protocol_v4.md` line 339 asks that it stay unchanged "by
this wiring" (WP14); RL-96 rules the one-line change, and the deviation row is where that is disclosed.

## Signal escalation and wall time

INT, then TERM, then KILL, each as `sudo -n /bin/kill -<NAME> <pid>`, in that order (two mutants that reorder
or drop KILL are killed).

| Step | Bound |
|---|---|
| each census | 5 s (`CENSUS_TIMEOUT_S`) |
| each kill | 5 s per pid (`SIGNAL_TIMEOUT_S`) |
| wait after each signal | 2 s (`REAP_GRACE_S`), polled every 0.1 s by census |

Worst case with one pid is about 41 s: one census, then three rounds of a kill, a 2 s wait and a census that
starts just inside it. Every loop ends on a monotonic deadline. `sudo -n` with no rule exits at once. A reap
cannot hang the member.

## The two judgement calls

### 1. The refusal type on an unproven reap: accepted

On an unproven reap the member sees `PowermetricsOrphanRefusal`, chained to the original with `raise … from`.
Term 3's "the original exception still propagates" is the proven case and is unchanged. Term 4 accepts a
refusal in the unproven case, so the two terms do not conflict.

One side effect to disclose. The refusal carries `FailureReason.TELEMETRY_UNAVAILABLE`, which the controller
maps to status `unsupported`; the bare timeout maps to `failed`. The CLI exits 3 for both and every campaign
check I found tests "not succeeded", so nothing downstream reads the difference. The member's label changes
all the same.

### 2. The process-wide refusal: it stays for tonight; two questions go to the research lead

It is needed. Three callers swallow the refusal: the parent's `measure_post_run_idle` (`except Exception`),
the controller's sentinel stage, and the campaign cooldown gate. Without the module-level list the unproven
case would be recorded and then ignored.

What it does depends on how members are launched.

- **R1, tonight.** `r1_runtime.run_member` calls `run_benchmark` in the night's own process. One unprovable
  reap refuses every remaining member of the night. That is what term 4's reason asks for.
- **W1.** `run_campaign` launches each member as a fresh `python -m joulewise` process. The list dies with
  the member. The next member is not refused. (Finding 3)

Can it poison a healthy night? Not from outside the process. `UNPROVEN_REAPS` is appended in one place,
`_reap_capture`, after a real capture or probe has failed in that process. Nothing reads a file or the
environment, so a test or a probe in another process cannot reach it. The false-positive path is inside the
process: one census that fails once. (Finding 4)

## Mutants

Each mutant was applied to a scratch worktree and `tests.test_powermetrics_reap` was run. 21 of 27 are killed.

| Mutant | Result |
|---|---|
| reap by name (`"powermetrics" in command`) | killed |
| reap by executable only, no `-o` | killed |
| skip the census after signalling | killed |
| census without the own-pid proof | killed |
| census exception read as "absent" | killed |
| **census ignores `ps` exit status** | **survived** |
| swallow the original exception | killed |
| drop the `from exc` chain | killed |
| wrap the success path: record a reap on success | killed |
| wrap the success path: alter the returned bytes | killed |
| refusal not raised | killed |
| no poison; poison unchecked in capture; unchecked in capability | killed (3) |
| kill without sudo: constant, argv, direct `os.kill` | killed (3) |
| **wrong `-o` match: prefix (`marker in command`)** | **survived** |
| **wrong `-o` match: no ` -o ` anchor** | **survived** |
| **wrong `-o` match: basename only** | **survived** |
| KILL first; no KILL | killed (2) |
| reap not recorded | killed |
| **`except Exception` in place of `BaseException`** | **survived** |
| probe timeout not reaped | killed |
| reap only on `TimeoutExpired` | killed |
| own pid not skipped in the census | survived; equivalent (the caller's command never matches) |

At base `22f438fd3` the test file fails 8 of its 9 tests, as the builder says.

## Tests

One module at a time, `nice -n 10 python3.13 -B`, 31 GB free throughout, host load about 35.

| Module | Branch `b4521cb8e` | Merge with `bb6394f2b` |
|---|---|---|
| `tests.test_powermetrics_reap` | 9 OK | 9 OK |
| `tests.test_powermetrics` | 61 OK | |
| `tests.test_adapters_powermetrics` | 3 OK | |
| `tests.align.test_measurement_core_boundary` (WP14(c) pin) | 6 OK | 6 OK |
| `tests.align.test_v4_registration` | 24 OK | 24 OK |
| `tests.align.test_v4_executed_closure` | 6 OK | 6 OK |
| `tests.align.test_v4_dynamic_closure` | 10 OK | 10 OK |
| `tests.hazards.test_refusal_allowlist` | 24 OK, 1 skipped | 24 OK, 1 skipped |
| `tests.test_host_command_sites` | 2 OK | 2 OK |
| `tests.align.test_v4_arm_watchdog_check` | 80 OK | |
| `tests.test_shard_split` | 33 OK | 33 OK |
| `tests.hazards.test_import_graph`, `test_physics_coverage` | 6 OK; 7 OK, 1 skipped | |
| `tests.test_idle_admission`, `test_controller`, `test_custody_durability` | 32, 74, 5 OK | |
| `tests.test_identity_pins`, `test_calibration_bracketing` | 42 OK; 95 OK, 1 skipped | |
| `tests.test_digest_pin_census`, `tests.test_repin` | 22 OK; 37 OK | |
| `tests.align.test_r1_smoke_launcher` | | 53 OK |
| `tests.align.test_r1_runtime` | 7 failures, 2 errors | |

- **`test_r1_runtime`:** the same nine tests fail at base `22f438fd3`, by name. Unchanged.
- **`tests.hazards.test_host_command_sites` does not exist;** the module is `tests.test_host_command_sites`.
- **Not run:** `tests.test_harvest_b5_window` (it blocks on an evicted iCloud file).
  `tests.test_validate_powermetrics_fiducial_derivation_only` was started and stopped after eight minutes
  under load; `powermetrics.py` is byte-identical, which is what it pins.
- **Other test modules and the reaper.** Many existing tests patch `subprocess.run` globally and now resolve
  the wrapper, so a patched census could leave the poison set for later tests in the same process. I ran
  `test_powermetrics`, `test_adapters_powermetrics`, `test_idle_admission`, `test_custody_durability`,
  `test_b6_idle_wait` and `test_controller` with a spy on `_reap_capture`: no test triggers a reap, and
  `UNPROVEN_REAPS` is empty after each. A future test that fails a bounded capture through the production
  class must clear the list, as the new test file does.

## Merge-ability

`git merge-tree --write-tree bb6394f2b b4521cb8e` exits 0, tree `162bea015`. No conflicts.
`configs/gates/hazard_refusals.json` auto-merges (both sides add rows); the closure lists and
`registration_receipt.json` are untouched on the presign side. `scripts/test_timings.json` is untouched by
both, and `tests.test_shard_split` passes with the new module absent from it. The merged tree passes the
modules in the right-hand column above.

## Findings

### Required before it rides tonight

**1. Nothing pins the exact `-o` match.** Three mutants survive: `marker in command` (prefix), a marker with
no ` -o ` anchor, and a basename match. The one targeting test uses a sidecar at `/tmp/sidecar.plist`, which
shares nothing with the capture path. Add rows to `test_kill_targets_only_this_captures_output_path` and
assert none is signalled:

- `-o <path>2` kills the prefix mutant;
- `-o /private<path>` kills the no-anchor and basename mutants;
- `--note <path> -o /tmp/other.plist` holds the "as the `-o` value" rule.

**2. The R1 night has no check that `/bin/kill` is permitted.** The W-2 listing lives in
`align_v4_session.host_privilege_preflight`, which the R1 path does not call. If the rule is missing on the
MBP, the first timed-out capture whose sampler is still alive cannot be reaped, the refusal is raised, and
every remaining member of the night is refused. Without the wrapper that night would have continued. The
magistrate lists it over SSH before the arm: `sudo -n -l /bin/kill` must exit 0. Listing only.

### Owed before W1 signing

**3. In W1 the refusal does not reach the next member. For the research lead.** Each W1 member is a fresh
process, so `UNPROVEN_REAPS` is empty again. Two cases follow.

- A pre-run idle capture is refused. That member fails. The next member starts beside the unproven sampler
  and is not refused.
- A post-run idle capture is refused. The refusal is swallowed, the member **succeeds** with
  `idle_drift: unknown`, and the next member is not refused. I reproduced this (Term 3, row 4).

Both leave `absent: false` in the earlier member's `device.capture_reaps`, so it is recorded. It is not
refused, which is what term 4 asks for. Closing it needs state that outlives the process, or a census at the
start of each member. That is a design choice, not a wording fix.

**4. One failed census poisons the process for good. For the research lead.** `_census` is tried once per
look with a 5 s limit. If a look fails after a signal, escalation stops (TERM and KILL are not sent), the
reap is unproven, and the list is never cleared, even if the sampler exits a second later. On the R1 path
that ends the night's remaining members. It errs the safe way, and it needs a capture to have failed first.
Two cheap changes would narrow it: keep escalating on the last known pids when a look fails, and let a later
census that proves absence clear the entry and record that it did.

**5. A reap on the cooldown path is recorded nowhere.** `run_campaign`'s cooldown gate builds its own
adapter, catches the exception into a note and drops the adapter. A proven reap leaves no `capture_reaps`
anywhere; an unproven one survives only as the note's reason string. Term 3 says "recorded".

**6. Registry wording and coverage.**

- The NUMBER_INTEGRITY row's `protects` begins "Every later member's power and energy numbers". That holds
  only for members in the same process. Say so.
- The refusals returned by `_ensure_capability` and `_probe_capability` are not `raise` sites and have no
  row. If the scan cannot count a returned refusal, the row for `_run_bounded_capture` should name them.
- The `<reraise>` row is INTERNAL. It re-raises what the parent's BASELINE row already raises and adds no
  stop, so I agree; under RL-86 it is the lead's to confirm.

**7. Three test gaps besides Finding 1.**

- `ps` exiting non-zero with a table that lists the caller must still refuse. The present subtest passes an
  empty table, so the own-pid check answers for it.
- A `KeyboardInterrupt` during the capture must reap and re-raise.
- The identity test should pass a `RunContext` and compare the persisted artifact. I checked it by hand.

**8. Smaller points.**

- `docs/align/v4/dynamic_closure_trace.json` was recorded before the module existed. Its test passes; a
  fresh trace would list `powermetrics_reap.py`.
- `sudo -n -l /bin/kill` lists the command without arguments. A sudoers rule restricted to particular
  arguments would be reported missing. That is the safe direction.
- Reported by the builder and confirmed: `r1_runtime.py:1467` builds the base class for its status sidecar,
  and `run_night._powermetrics_cadence_probe` relays TERM with no proof of absence. Neither is reaped by this
  change. The first is a condition-13 file.

## An error of mine during the review

My "reap by name" mutant matched `"powermetrics" in command`, and two of the builder's tests drive a real
`os.kill` through the fake `sudo`. From about 05:21:57 to 05:22:12 PST those tests sent INT, TERM and KILL to
every process on the Air owned by `edr` with `powermetrics` anywhere in its command line. Root processes were
out of reach. My own background shell died with a signal in that window, which is how I noticed. I cannot list what
else it hit. Any
watcher or test run whose command line named the branch (`…powermetrics-orphan-reap`) or a powermetrics test
module in that window should be checked and restarted. The other mutants matched only the test's own
temporary paths.

The mutant shows the hazard the term exists for: it was killed by the tests, and it also did the damage the
tests are there to prevent.
