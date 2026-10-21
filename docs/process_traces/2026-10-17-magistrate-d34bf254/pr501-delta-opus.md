# Delta review (Opus 5.5, executing): b6 MT r2 fix round 2

- Delta: `git diff 0276a3327 021f935c8` (round 2). Context: round 1 = `git diff f3ef7804b 0276a3327`.
- Worktree: `/Users/edr/code/JouleWise-wt-cold-mt2-opus`, detached at 021f935c8. I did not edit it.
- Scratch: `TMPDIR=/Users/edr/night-archive/b6-mt2-fix/tmp/delta.B1eh`. It holds `base/` (`git archive 0276a3327`), `orig/` (`git archive f3ef7804b`) and `probes/`.
- Real archive `/Users/edr/night-b6/machine-test/MT-20261017T1735Z/` was only read. Every probe that touches it calls pure read functions (`evidence_from_archive`, `validate_whole_window_verdict_row`, `environment_admission_refusals`, `stages_succeeded`, `classify`) and writes nothing.
- Interpreter: `/opt/homebrew/bin/python3.13 -B`, `JW_B5_SYNTHETIC_ONLY=1`, and `PYTHONPATH=<tree under test>`. Each probe asserts that its module was loaded from that tree.

## Verdict: MERGE

Each finding this round addresses is fixed. I showed every one by building the failing input and running it on 0276a3327 and on 021f935c8:

- Fable F1: the verdict writer vetoed busy-only members.
- Fable/Opus F2: round 1 had narrowed the "absent stage" test.
- Opus F1: a wait-budget skip was called structural.
- The CI failure in `tests/test_b6_busy_fraction_desk.py`.

The writer's new pass condition is never weaker than the old one except for a marked busy-only member. Of the 17 constructed cores, 16 give identical `status`, writer exit and claim-barrier output on both commits. Only the marked busy-only member moves (failed/exit 1 → passed/exit 0).

Block-5-shaped cores are byte-identical before and after. No test failed. The delta adds no tolerance or threshold.

I found no input that produces a wrong number or a lost run. The three NITs below need no change before merge.

## Findings

No BLOCKER, MAJOR or MINOR.

### N1 NIT: the claim barrier reads the copy of the final attempt carried in the core, not the member's metadata

`scripts/run_campaign.py:9046-9048`. `_idle_admission_claim_barrier_reasons` gets `final` from `member["final_admission_attempt"]`. The writer copied that value from the same bundle's `metadata.json` a few lines earlier (`:7243-7267`), so inside the writer the two can never differ.

The independent check is the whole-window validator, `joulewise/whole_window.py:6950-6962`. It re-reads `final` from the bundle bytes and does not trust the carried copy. I confirmed this: injecting the key into the real archived row changes none of its reasons (probe 3b).

A forged core would therefore have to get past the validator, which needs an operator-level edit. D-161 rules that threat model out. No change needed.

### N2 NIT: `files_missing` is now written but never read

Round 1 added `runtime["files_missing"]` (`joulewise/b6/acceptance.py:457`) to support the narrowed predicate. Round 2 restored the original predicate, so no code in `joulewise/b6` reads that field any more; only tests set it. It does no harm and could be removed later.

### N3 NIT (observation): a recorded skip that also lost `summary_metrics.json` stays exempt

The case "cap skip + lost summary json too" is not structural on head (and was not on 0276a3327). That is right physically: a cap or budget skip happens before measurement, so no capture was lost. The member is still excluded through `member.bytes_missing` (EXCLUDE_MEMBER). No change needed.

## Check 1: each addressed finding is fixed (base 0276a3327 vs head 021f935c8)

### Fable F1: writer veto of a busy-only member

Probe `probes/writer_probe.py` runs the real `run_whole_window_verdict` on the passing fixture of `tests/test_run_campaign.py`. It wraps the real `_idle_admission_core_evaluation` and rewrites the core it returns. Case "I marked busy-only member":

```
base: I marked busy-only member   status=failed  exit=1 core_conditions=[] barrier(core_blocks_claim)=['cpu_admission_core_failed']
head: I marked busy-only member   status=passed  exit=0 core_conditions=[] barrier(core_blocks_claim)=[]
```

Probe `probes/writer_real.py` takes the real path, with no core rewrite. The member's `metadata.json` carries `busy_fraction_admitted=True`, and `rich_telemetry_idle.jsonl` holds busy records; this is the input from the cold report. The probe then runs the real validator on the row that was written:

```
base marker=True  status=failed exit=1 conditions=[] validator=(False, ('whole_window_neg8_verdict_failed', 'whole_window_verdict_provenance_invalid'))
base marker=False status=failed exit=1 conditions=['cpu_busy_ratio_p95_exceeded'] validator=(False, ('cpu_admission_core_failed', 'whole_window_neg8_verdict_failed', 'whole_window_verdict_provenance_invalid'))
head marker=True  status=passed exit=0 conditions=[] member_keys=[[..., 'final_admission_attempt'], [...]] validator=(False, ('whole_window_verdict_provenance_invalid',))
head marker=False status=failed exit=1 conditions=['cpu_busy_ratio_p95_exceeded'] validator=(False, ('cpu_admission_core_failed', 'whole_window_neg8_verdict_failed', 'whole_window_verdict_provenance_invalid'))
```

The remaining `whole_window_verdict_provenance_invalid` comes from the fixture: the clean control window, with no busy member, gets the same result on both commits (`probes/writer_clean.py`). So a head-written busy-only row validates exactly as a clean window does:

```
base marker=None status=passed exit=0 conditions=[] validator=(False, ('whole_window_verdict_provenance_invalid',))
head marker=None status=passed exit=0 conditions=[] validator=(False, ('whole_window_verdict_provenance_invalid',))
```

### Fable F2 / Opus F2: "absent" predicate

On head, the predicate is the f3ef7804b original (`git diff f3ef7804b 021f935c8 -- joulewise/b6/acceptance.py` shows only a line reflow):

```
absent = not stage.members or all(m.runtime.get("bundle_present", True) is False
                                  or "member.bytes_missing" in m.flags for m in stage.members)
```

The real-archive case comes from Fable: the decode member's cap record is removed, `files_missing=summary_metrics.json` is set, and the decode stage rc is forced to 0. Results from `probes/smoke_cases2.py`:

```
base X5 Fable F2: crash after capture (summary missing), decode rc 0  structural=False sf=[] stages_ok=True classify=physics
head X5 Fable F2: crash after capture (summary missing), decode rc 0  structural=True sf=['structure.missing_stage_bundles'] stages_ok=True classify=fail
base X6 same, smoke=False                                             structural=False ... classify=physics
head X6 same, smoke=False                                             structural=True sf=['structure.missing_stage_bundles'] ... classify=fail
base C decode: crash after capture (summary missing, plist present)   structural=False sf=[] stages_ok=False classify=fail
head C decode: crash after capture (summary missing, plist present)   structural=True sf=['structure.missing_stage_bundles'] stages_ok=False classify=fail
```

### Opus F1: wait-budget skip

Opus's case D on the real archive: the decode member's `idle.wait_cap_skip` becomes `idle.wait_budget_skip`, and `skip_reason` becomes `wait_budget_exhausted`.

```
base D decode: wait BUDGET skip (physical, cataloged PHYSICS)  structural=True sf=['structure.missing_stage_bundles'] stages_ok=False classify=fail
head D decode: wait BUDGET skip (physical, cataloged PHYSICS)  structural=False sf=[] stages_ok=True classify=physics
```

### CI failure: `tests/test_b6_busy_fraction_desk.py`

```
base: FAIL: test_attempt_validators_accept_extra_signal_without_changing_evidence_result
      - ()  + ('environment_admission_failed',)      (Ran 6 tests, FAILED (failures=1))
head: module passes inside the 193-test run below
```

The fix changes only what the test expects. On 0276a3327 the code already returned `()` for a marked busy-only attempt, as round 1 intended under council Q3; the test was stale. The renamed test still asserts that the attempt is never `environment_admission_missing`, and now also asserts `before == ('environment_admission_failed',)` and `after == ()`.

## Check 2: the writer's new condition against the old one

Old (0276a3327): `bracket.decision == "passed"`, plus `continuity.decision == "stable"`, plus every member's raw `cpu_admission.decision == "admitted"`, plus empty `conditions`.

New: no barrier reasons, plus empty `conditions`.

Reading the code, the barrier holds the same three checks:

- it maps a non-Mapping bracket or `not_evaluated` to `..._missing`, and any other decision except `"passed"` to `..._failed`;
- it maps a non-Mapping continuity or any decision except `"stable"` to a reason;
- it maps an empty or non-list `members`, a non-Mapping member, a non-Mapping cpu, or a decision other than `"admitted"` to a reason. The one exception is `busy_fraction_admission_admitted(final, cpu)`.

The barrier's extra condition checks are a subset of `conditions`, which must be empty anyway. So the new condition is the old one minus one exception.

`probes/writer_probe.py` runs this on the real writer. Every case empties `core["conditions"]`, so the barrier alone decides:

```
                                                 base (0276a3327)        head (021f935c8)
A clean control                                  passed  exit=0          passed  exit=0
B bracket failed                                 failed  exit=1          failed  exit=1   ['whole_window_neg8_verdict_failed']
C bracket not_evaluated                          failed  exit=1          failed  exit=1   ['whole_window_neg8_verdict_missing']
D bracket missing                                failed  exit=1          failed  exit=1   ['whole_window_neg8_verdict_missing']
D2 bracket not a dict                            failed  exit=1          failed  exit=1   ['whole_window_neg8_verdict_missing']
E continuity unstable                            failed  exit=1          failed  exit=1   ['adapter_continuity_failed']
F continuity missing                             failed  exit=1          failed  exit=1   ['adapter_continuity_evidence_missing']
G busy+power, marker, final busy+power           failed  exit=1          failed  exit=1   ['cpu_admission_core_failed']
G2 busy+power stored, marker, final busy-only    failed  exit=1          failed  exit=1   ['cpu_admission_core_failed']
G3 busy-only stored, marker, final busy+power    failed  exit=1          failed  exit=1   ['cpu_admission_core_failed']
H unmarked busy member (no final key)            failed  exit=1          failed  exit=1   ['cpu_admission_core_failed']
H2 busy, final present, marker absent            failed  exit=1          failed  exit=1   ['cpu_admission_core_failed']
H3 busy, marker, final admitted False            failed  exit=1          failed  exit=1   ['cpu_admission_core_failed']
H4 busy, marker string 'true'                    failed  exit=1          failed  exit=1   ['cpu_admission_core_failed']
K members empty                                  failed  exit=1          failed  exit=1   ['cpu_admission_core_missing']
K2 member not a dict                             failed  exit=1          failed  exit=1   ['cpu_admission_core_failed']
I marked busy-only member                        failed  exit=1          passed  exit=0   []
```

(The barrier column is the same on both commits. It is also `core_blocks_claim`, which feeds the campaign producer's exit at `run_campaign.py:11605-11612`.)

The AXI producer (`:10209`) already used the barrier on base, so it changes only through the barrier's exception. The new test `test_busy_only_member_passes_writer_status_and_producer_exit` covers it, and that test passes (78/78 below). Every caller of the barrier is in `run_campaign.py` (`:8610, 9070, 10209, 10271, 11542, 11607`), and each gets its core from `_idle_admission_core_evaluation`.

## Check 3: who reads `final_admission_attempt`, and the block-5 wire shape

The key is added only when `final.get("busy_fraction_admitted") is True`. `probes/core_shape_probe.py` runs the real `_idle_admission_core_evaluation` and prints a SHA-256 of the canonical JSON of the whole core. I ran it twice per tree, and the hashes were stable:

```
                                   base sha          head sha          head member keys
b5 clean idle (no marker)          cecfd0ffdf5f3a53  cecfd0ffdf5f3a53  adapter_observation_count, bundle_id, cpu_admission
b5 busy-only, no marker            fbce42b0c7d5ba03  fbce42b0c7d5ba03  (same 3)
b5 busy-only, no marker, abort     24c619abfcf0566c  24c619abfcf0566c  (same 3)
b5 busy+power, no marker           67e7925570ee63c3  67e7925570ee63c3  (same 3)
b6 marker, final admitted False    fe8af86cef3b29e7  fe8af86cef3b29e7  (same 3; attempt ledger invalid, so final = {})
b6 busy-only, marker               3751df0df4ea6771  8354f54e9c2d874a  + final_admission_attempt   barrier: cpu_admission_core_failed removed
b6 busy+power, marker              a0ad8e801b19db68  8bd52621d1b2f554  + final_admission_attempt   barrier keeps cpu_admission_core_failed
```

Block-5-shaped cores are byte-identical.

The places that read core members:

- **Validator** (`joulewise/whole_window.py`). At `:5388-5401` it compares only `stored["cpu_admission"]` against the derived value. At `:6928-6962` it hashes each whole member and checks only that the hashes are distinct, then re-reads `final` from the bundle bytes. Neither step rejects an extra key. I confirmed this by running the probes: the real archived row as written, and the same row with the key injected for both marked members, get identical reasons on both commits.
  ```
  as-written authentic= False reasons= ('calibration_ledger_snapshot_required', 'whole_window_neg8_verdict_failed', 'whole_window_verdict_conflict', 'whole_window_verdict_provenance_invalid')
  injected   authentic= False reasons= (same)
  ```
  (These reasons come from the archived row: the f3ef7804b writer wrote it with `status: failed`, and no ledger snapshot is passed. Cold Opus reported the same.)
- **Harvest** (`joulewise/b5/harvest.py:4583, 4677-…`). It reads only `idle_admission_core.conditions` and `neg8_bracket`, never member keys.
- **Schemas.** No schema or fixture pins the member key set: `adapter_observation_count` appears only in `run_campaign.py`, one test and legacy docs.

## Check 4: acceptance

`probes/acc_probe.py` puts a constructed "lost" stage ahead of the clean `tests.b6.support.session()`, so the "a later stage ran" condition holds. It shows whether that stage is flagged `structure.missing_stage_bundles`:

```
case                                       f3ef7804b  0276a3327  021f935c8
all cap (flag+reason)                      True       False      False
all budget (flag+reason)                   True       True       False
mixed cap+budget                           True       True       False
crossed: cap flag/budget reason            True       True       True
crossed: budget flag/cap reason            True       True       True
cap flag, no reason                        True       True       True
cap reason, no flag                        True       True       True
partial: 1 of 2 expected present           True       True       True
partial: skip + unexplained loss           True       True       True
skip + bundle_present False                True       True       True
clean capture lost summary (succeeded)     True       False      True
lost summary (failed), no skip             True       False      True
cap skip + lost summary json too           True       False      False   (N3)
all bundle_present False                   True       True       True
```

Head matches the original predicate everywhere except a complete stage of recorded cap or budget skips, where both the flag and the matching `skip_reason` are present. Crossed pairs, partial stages and a stage that lost its summaries after a clean capture all stay structural.

For the smoke desk on the real archive (`stages_succeeded` and `classify`), head gives:

| Case | Result |
|---|---|
| A (real) | physics |
| D (budget) | physics |
| B, B2, D2, X1–X4 (unexplained, or crossed/half records) | fail |
| C, X5, X6 (lost summary) | fail |
| E, E2, F, F2, G (wrong rc or unexplained rc) | fail |

## Check 5: tests

```
TMPDIR=/Users/edr/night-archive/b6-mt2-fix/tmp/delta.B1eh JW_B5_SYNTHETIC_ONLY=1 PYTHONPATH=$PWD /opt/homebrew/bin/python3.13 -B -m unittest \
  tests.test_b6_busy_fraction_desk tests.test_environment_admission tests.test_whole_window tests.test_hazard_whole_window_verdict \
  tests.test_harvest_b5_p3harv tests.hazards.test_refusal_allowlist tests.b6.test_acceptance tests.b6.test_smoke
Ran 193 tests in 99.877s
OK

... -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests     (the only run_campaign class the diff touches)
Ran 78 tests in 114.709s
OK

... -m unittest tests.test_b6_idle_wait tests.test_idle_admission tests.test_harvest_b5_window
    (the other modules in tests/ that assert on busy_fraction_admitted / cpu_busy_ratio_p95_exceeded)
Ran 227 tests in 472.837s
OK

base 0276a3327: cd $T/base && PYTHONPATH=$T/base python3.13 -B -m unittest tests.test_b6_busy_fraction_desk
Ran 6 tests ... FAILED (failures=1)   (the CI failure; see check 1)
```

193 + 78 = 271, which matches the author's V1 count.

## Check 6: deciding functions on the real archive

- **`environment_admission_refusals`** (`probes/replay_admission.py`, copied from the cold Opus pass). Round 2 does not touch `environment_admission.py`, so both commits agree:
  ```
  d117fq31p7-df-ph-prefill-p2048-abs-r01 decision=admitted final_admitted=True marker=True conds=['cpu_busy_ratio_p95_exceeded'] p95W=0.406085 busy_p95=0.87254 refusals=()
  neg8-window-end-r1                     decision=admitted final_admitted=True marker=True conds=['cpu_busy_ratio_p95_exceeded'] p95W=0.417253 busy_p95=0.8717  refusals=()
  ```
- **Acceptance and smoke stage classification on the real archive** (`probes/smoke_cases2.py`, case A). Both commits give `structural=False sf=[] stages_ok=True classify=physics`. The real night still reads physics, and the decode member is still recognized as a recorded cap skip.

## No new numbers

Every added non-test line that contains a digit is listed below. None of them is a tolerance or threshold:

- `(0, 6)` is the existing harvest-exit set, moved within the line;
- the digits in `b6` and `block-5` are inside a module path and a comment.

The admission criteria and the 576-record / `cpu_busy_ratio_p95_max` values were not touched.

## What I ran

1. `git diff --stat` and the full code diff for 0276a3327..021f935c8; `git diff f3ef7804b 021f935c8 -- joulewise/b6/{acceptance,smoke}.py`.
2. Read: BRIEF-r2.md; COLD-fable.md F1–F3; COLD-opus.md in full through "adversarial"; the author report header; `run_campaign.py:7180-7290, 8570-8700, 9023-9075, 10190-10235, 11595-11620`; `environment_admission.py:464-505`; `whole_window.py:5370-5410, 6900-6965`; `harvest.py:4570-4700`.
3. Built `base/` and `orig/` with `git archive`.
4. My probes, under `$T/probes/`: `writer_probe.py`, `writer_real.py`, `writer_clean.py`, `core_shape_probe.py`, `replay_ww2.py`, `acc_probe.py`. Probes adapted from the cold Opus pass: `replay_admission.py` (copied), `smoke_cases2.py` (copied and extended with X1–X6). Each ran on base and head; `acc_probe.py` also ran on f3ef7804b.
5. The test commands in check 5.

## NOT EXECUTED

- The author's V2 suite: `tests.test_controller`, `test_controller_retry_backoff`, `test_controller_hazard_flags`, `test_run_campaign_max_blocks`, `test_floor_extraction`, `test_reduce` (433 tests). The diff does not touch those code paths, apart from `floor_extraction` listing `cpu_admission_core_failed` as a reason code, which did not change.
- The full `tests.test_run_campaign` module (only `IdleAdmissionCoreVerdictTests` was run).
- An end-to-end production `smoke.desk` run on an APFS clone of the real smoke dir, as in cold Opus's `desk_e2e.py`. The desk gate's widened flag intersection is covered by `test_desk_idle_loss_requires_exact_dispatch_records_and_campaign_exit` (cases cap, budget and mixed → physics; 11 others → fail), which passed, and by the direct `stages_succeeded`/`classify` replay on the real archive.
- The CI matrix.
