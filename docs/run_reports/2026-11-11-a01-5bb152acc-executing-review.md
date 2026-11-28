# A-01 executing review: `5bb152acc`

2026-11-11. Reviewer: Opus 5.5, cold executing review. I did not write this commit.

- **Target:** `5bb152acc27b7c34aef7721a51dd959223ddd530`, "fix(night): surface
  failed chains and R1 refusals as faults (A-01)". Parent: `9abe6095f`.
- **Blobs at the target:** `joulewise/b5/driver.py` `d58ca9e4c7b6`,
  `scripts/run_night.py` `7c830753a129`, `tests/test_w1_reliability.py`
  `cd560a487157`.
- **Presign head:** I tested `origin/ops/2026-11-11-w1-presign` at `535bf9cee`. The
  branch later moved to `433bcd6a6`. Between the two it changed none of the three
  files, `tests/test_b5_driver_p2.py` or `configs/b6/executing_reviews.json`.

## Verdict

**ADMIT-WITH-FIXES.** The production change is correct for A-01, and the head carries
it unchanged.

- Every failed-chain and R1-refusal path I traced now reports `fault: true` with a
  named reason. The fault appears in `result.json`, in `hazard_result.json` and in the
  courier facts.
- The verdict and exit-code policy are unchanged, as Q3 requires.
- No healthy path is now reported as a fault.

The fixes are to tests and process, not to production code. None of them blocks W1.

1. **F-1 (MED, process). The commit was not green.** One existing test fails at
   `5bb152acc`:
   `tests.test_b5_driver_p2.SolReviewFixTests.test_an_instrument_not_sampling_refusal_carries_the_fault_facts`.
   - With the parent's production files, the same test passes (5.5 s).
   - The expectation is stale: the new `refusal:night_refused_instrument_not_sampling`
     reason is intended.
   - `e721e53c5` repaired it (ci-debt-4 row). `tests.test_b5_driver_p2` is green at
     head (46 tests).
   - Nothing remains to do. The record should show that the commit did not ship green.
2. **F-2 (LOW, test strength). Two fault branches have no witness.**
   - At the commit's tests, 16 of 35 mutants survive. At head's tests, 14 survive.
   - Production handles both of these branches correctly today, but no test pins them:
     - **M16, the ABORTED reason:** an ABORTED night whose exit code is `None` would
       report `fault: false`.
     - **M19/M20, the post-start REFUSED reason:** a night that refuses after its chain
       started (for example, termination not proven) and has no exit code would report
       `UNKNOWN` and `fault: false`.
   - The broader `tests.test_b5_driver_p2` at head does not kill them either.
   - Suggested witness: two `_chain_outcome` unit cases, `('ABORTED', None)` and
     `('REFUSED', None)` with `chain.started` present. Each must assert
     `fault is True` and the outcome label.

## What A-01 asked for

I took the finding from
`origin/audit/2026-11-10-fable:docs/research-audits/2026-11-10-fable/measurement-system.md`,
§3.1. Its cited rebind is Q3 in `implicit-state-machines.md` on the same branch.

- **A-01 (HIGH).** `night/result.json` says `GO` for any chain exit, with
  `fault: false`. An R1 refusal (exit 3), an abort (exit 4) or a wrapper exit 65 is
  therefore invisible. The audit's fix:
  - a nonzero chain exit is `CHAIN_FAILED`, with a `chain_exit:<rc>` reason;
  - for a single-chain plan, `r1_result.status` (or "absent") is copied into
    `result.json` and the report facts as `measurement_outcome`.
- **Q3.** Append `chain_exit_nonzero:<rc>` to the driver's fault list. In the audit's
  words: "The verdict stays GO, so block-5 readers are unaffected."

The commit follows Q3. `verdict` stays `GO`, and the audit's `CHAIN_FAILED` label
appears in a new `chain_outcome` field. The rest of the A-01 fix is implemented as
written.

## What I ran

How I ran everything:
- Command: `nice -n 10 python3.13 -B -m unittest <module>`, one module at a time.
- `TMPDIR=/Volumes/JW-EXT/scratch/a01-review`.
- A detached worktree under `jw-wt/`. The load average on the Air was 54–75
  throughout.
- I ran no host-changing command and read no Block 6, BYTES or v4 outcome data. Every
  fixture is synthetic.
- I left `scripts/test_timings.json` untouched.

### Fail before, pass after

For this table I put the parent's two production files under the commit's test file.

| Production files | `tests.test_w1_reliability` (commit's version, 4 tests) |
|---|---|
| parent `9abe6095f` | **FAILED**, 10 errors: `KeyError: 'chain_outcome'` in tests 1, 2 and 4; `AttributeError: … no attribute '_chain_outcome'` in all 7 subtests of test 3 |
| `5bb152acc` | **OK**, 4 tests, 6.7 s |

At the parent, the tests fail on the missing field before they reach the fault
assertions, so this table alone is a weak witness. The mutants below supply the
semantic kill power.

### Affected modules at `5bb152acc`

| Module | Result |
|---|---|
| `tests.test_w1_reliability` | OK, 4 tests |
| `tests.test_b5_driver` | OK, 48 tests, 146 s |
| `tests.test_b5_driver_p2` | **FAILED (1)**, 46 tests, 140 s. This is F-1. The same test passes with the parent's production files |
| `tests.test_b5_driver_p3` | OK, 30 tests, 99 s |
| `tests.test_run_night` | 318 tests, 464 s; FAILED (8) in `BindSupervisionProcessTests` and `NightProbeTests` |

The `tests.test_run_night` failures are timing flakes under load, not this commit.
They are 8-second external watchdogs, probe deadlines and "never reached its own
startup inside the probe deadline". Evidence:

- Re-run alone at `5bb152acc`, the subset (25 tests) failed 7, a different set.
- With the parent's production files, the same subset failed 9.
- None of them touches `_write_result`'s outcome fields.
- The other 310 `test_run_night` tests, which include the `_write_result` callers,
  pass.

### Presign head (`535bf9cee`, A-01 files identical at `433bcd6a6`)

| Module | Result |
|---|---|
| `tests.test_w1_reliability` | OK, 11 tests, 32.8 s |
| `tests.test_b5_driver_p2` | OK, 46 tests, 177 s |
| `tests.test_b5_driver_p3` | OK, 30 tests, 126 s |
| `tests.test_b5_driver` | OK, 48 tests, 273 s |
| `tests.b6.test_audit_record_fixes` (review-rows test) | FAILED before this paper: `['5bb152acc…'] != []`. 5bb152acc is the only unreviewed commit. With the ledger row for this paper applied locally (not committed), the test result is in the hand-off report |

## Path analysis

### What `_chain_outcome` reads

`_chain_outcome` (in run_night) has three callers:
- `_write_result`, which every `result.json` writer uses;
- the driver's `refuse()`;
- the driver's terminal block.

It reads `chain.started`. For an R1 plan that started, it also reads one key, `status`,
from `night/align-r1/r1_result.json`.

- **The path matches the armed route.** `20e9edbc4:joulewise/align/r1_arm.py:113`
  names the plan `align-r1-…`, and runbook line 183 reads
  `$S/night/align-r1/r1_result.json`.
- **Status handling:** any value outside `complete/refused/aborted/running` becomes
  `invalid`. Only `complete` is fault-free.
- **Blinding:** this is a structural read. No measurement or slot value is read.

### Failure paths (HAZARD_PACK, the R1/W1 route)

| Path | verdict | chain_outcome | fault reason(s) |
|---|---|---|---|
| R1 refuses, exit 3 | GO | CHAIN_FAILED | `r1_status:refused`, `chain_exit_nonzero:3` |
| R1 aborts, exit 4 | GO | CHAIN_FAILED | `r1_status:aborted`, `chain_exit_nonzero:4` |
| wrapper exit 65, no payload | GO | CHAIN_FAILED | `r1_status:absent`, `chain_exit_nonzero:65` |
| R1 refused/absent/unreadable/running/invalid at exit 0 | GO | CHAIN_FAILED | `r1_status:<s>` |
| any plan, nonzero exit | GO | CHAIN_FAILED | `chain_exit_nonzero:<rc>` |
| chain stop 10/11/12 | CHAIN_STOPPED | CHAIN_FAILED | existing `chain_stopped:<kind>` + `chain_exit_nonzero:<rc>` |
| driver abort | ABORTED | ABORTED | `abort:<reason>` (+ exit reason) |
| post-start refusal / termination unproven | REFUSED | CHAIN_FAILED | exit reason, else `chain_verdict:REFUSED` |
| pre-chain refusal (`refuse()`, night-gate refusal) | REFUSED | REFUSED_PRE_CHAIN | `refusal:<reason>` |

Where each fault lands:
- **`result.json`:** every path above reaches it through `_write_result`, which also
  merges in the hazard record's existing reasons.
- **Hazard record:** the driver adds the reasons to `hazard_result.json`
  `faults.reasons`.
- **Courier facts:** the driver writes `fault`, `fault_reasons`, `chain_outcome` and
  `measurement_outcome`.

### Healthy paths

- A started chain that exits 0 gives `COMPLETE` with no new reason. For R1, the payload
  must also say `status: complete`. Witnesses: test 4 and the `complete` subtest.
- A non-R1 plan needs no payload.
- `REHEARSAL_ONLY` with exit 0 gives `COMPLETE`, with no fault.

### Every refusal is now a fault

Every refusal now carries `fault: true`. This is a deliberate change of meaning: a
refusal collects nothing, and the audit asks that such an outcome be impossible to
miss.

No consumer's behaviour changes:
- No production code at the commit reads `fault`, `fault_reasons`, `chain_outcome` or
  `measurement_outcome` from these records. I grepped `scripts/` and `joulewise/`.
- No validator constrains the keys of `result.json`. `align_v4_next_arm_packet.py`
  checks only the schema string.

### Residual notes

None of these blocks admission.

- **N-1.** A refusal after the chain started, with exit code `None`, gets the reason
  `chain_verdict:REFUSED`. The specific cause is in `aborted_reason`, not in
  `fault_reasons`. Cosmetic.
- **N-2.** If `hazard_result.json` is unreadable, `_write_result` silently skips merging
  its reasons. The hazard record itself still holds them.
- **N-3.** On the legacy non-HAZARD_PACK path, `result.json` gains the new fields, but
  the courier facts and the "minimal result persistence" fallback do not. R1 and W1 do
  not use that path.
- **N-4.** The inner-status check covers R1 plans only. W1 (`align-v4-*`) plans fault on
  a nonzero exit, but no inner record is read. This is within A-01's stated scope
  ("single-chain plan").
- **N-5.** The `status` normalisation is untested (mutant M06). If it were removed, a
  `null` status would raise `TypeError` in the driver's terminal block, which has no
  `try`. The code has the normalisation, so this is a test gap only.

## Mutants

Each mutant is an exact single-occurrence string swap on one production line. I ran
them one at a time and restored the file after each run.

- **"Commit"** means the commit's own `tests.test_w1_reliability` (4 tests).
- **"Head"** means the same production lines at head, run against head's version of
  that module (11 tests).

| # | Mutant | Commit | Head |
|---|---|---|---|
| M01 | R1 detection: drop plan-id prefix clause | killed | killed |
| M02 | R1 detection: drop `chain_path` clause | survived | survived |
| M03 | R1 detection: drop payload-presence clause | survived | killed |
| M04 | read R1 status even before chain start | survived | survived |
| M05 | never read R1 status | killed | killed |
| M06 | drop status normalisation to `invalid` | survived | survived |
| M07 | swallow absent payload (treat as complete) | killed | killed |
| M08 | swallow unreadable payload (treat as complete) | killed | killed |
| M09 | swallow R1 refusal: drop `r1_status:` reason | killed | killed |
| M10 | invert `status != "complete"` | killed | killed |
| M11 | drop `chain_exit_nonzero` reason | killed | killed |
| M12 | invert nonzero-exit condition | killed | killed |
| M13 | drop pre-chain `refusal:` reason | killed | killed |
| M14 | pre-chain branch ignores `started` | survived | survived |
| M15 | pre-chain branch inverts `started` | killed | killed |
| M16 | drop `abort:` reason | survived | survived |
| M17 | remove ABORTED branch | survived | survived |
| M18 | CHAIN_FAILED ignores reasons | killed | killed |
| M19 | CHAIN_FAILED ignores REFUSED/CHAIN_STOPPED verdict | survived | survived |
| M20 | drop `chain_verdict:` reason | survived | survived |
| M21 | never COMPLETE | killed | killed |
| M22 | COMPLETE ignores `started` | survived | survived |
| M23 | `fault` always False | killed | killed |
| M24 | `fault_reasons` always empty | killed | killed |
| M25 | `_write_result` without outcome | killed | killed |
| M26 | `_write_result` drops hazard-reason merge | survived | survived |
| M27 | `_write_result` drops `fault` recompute | survived | survived |
| M28 | `refuse()` drops outcome reasons | killed | killed |
| M29 | `refuse()` drops hazard `chain_outcome` | survived | survived |
| M30 | `refuse()` report drops `chain_outcome` | survived | survived |
| M31 | `refuse()` report drops `measurement_outcome` | survived | survived |
| M32 | terminal drops outcome reasons | killed | killed |
| M33 | terminal drops hazard `chain_outcome` | killed | killed |
| M34 | terminal report drops `chain_outcome` | killed | killed |
| M35 | terminal report drops `measurement_outcome` | survived | killed |

**Totals.** The commit's tests kill 19 of 35. Head's tests kill 21 of 35. Head's added
test, the R1 refused payload at exit 0 checked through all three records, kills M03
and M35.

**The three classes the brief named:**
- Each new fault-surfacing branch removed: M09, M11, M13, M16, M20, M24, M28, M32.
- Conditions inverted: M10, M12, M15.
- The refusal swallowed: M07, M08, M09.

All of these are killed except M16 and M20 (F-2).

### The broader driver module

I also ran six of head's survivors against `tests.test_b5_driver_p2` at head, which is
green on baseline (46 tests):

| Mutant | Result |
|---|---|
| M16, M17, M19, M20, M26 | all survived |
| M29 | "killed" by `test_a_crash_loop_in_the_window_is_a_fault_in_the_report` |

I do not credit the M29 kill. That test runs a real 6-second chain to GO and never
reaches `refuse()`, and the load average was about 100 when it failed. I count M29 as a
survivor.

I stopped the planned p3 and `test_b5_driver` mutant passes to spare the loaded Air.
Their head baselines are in the table above. The M16, M17, M19 and M20 branches
appear in no assertion I could find in these modules.

### Survivors

- **Fault branches with no witness (F-2):** M16, M17, M19, M20.
- **Record plumbing, no witness:**
  - M26 and M27: the hazard-reason merge into `result.json`;
  - M29, M30 and M31: `refuse()` writing `chain_outcome` to the hazard record and the
    report.

  Without these lines the fault still surfaces: `refuse()` merges the same reasons into
  its report, and `result.json` computes its own. What is lost is a label, or an
  earlier hazard reason in `result.json`.
- **Detection alternatives:** M02, the `chain_path` clause. The plan-id clause is the
  one that identifies the armed R1.
- **Near-equivalent:**
  - M04 adds `r1_status:absent` to an R1 pre-chain refusal, which is still a fault.
  - M14 labels a post-start refusal `REFUSED_PRE_CHAIN`, which is still a fault.
  - M22: an exit of 0 implies a started chain in practice.
  - M06: see N-5.

## At the presign head

Between `5bb152acc` and `535bf9cee`, 11 commits touch these files. The A-01 lines
compare as follows:

- **Driver `refuse()` and terminal block:** byte-identical.
- **`_chain_outcome`:** identical, with one addition. For a `refused` or `aborted`
  status it adds an enrichment step, `_r1_refusal_summary`, behind
  `except Exception`, which reports `chain_refused_phase` and `chain_refusal_codes`.
- **`_write_result`:** gains `host_restoration` and a `host_restoration_incomplete`
  fault.

None of these removes or weakens an A-01 branch. All 35 mutants apply at head, with the
results shown in the table above. The verdict holds at head.

## Ledger note

`tests/b6/test_audit_record_fixes.py` sets two conditions on each new row:
- its `paper` must be in `docs/align/reviews/`;
- its `covered` text must contain `paper sha256 <digest>`.

A paper in `docs/run_reports/` cannot satisfy that test. This branch therefore also adds
a citation record,
`docs/align/reviews/2026-11-11-a01-5bb152acc-executing-review-citation.md`. It names
this report and pins it by SHA-256, the same convention as
`2026-11-11-w1-executing-review-citations.md`. The ledger row cites the citation record.
