# Cold-gate packet — QUIET-PREDICATE-EVIDENCE-01 harness, finding D5-T1: what may a real-scheduler regression assert about delivered CPU share? (rule 11 mandatory trigger: second fix round on the same defect)

Assembled 2026-09-18 ~23:10 PDT by the resident magistrate (activation e82f29ac). Mechanically assembled: every exhibit is a verbatim `git show`/`git diff`/`sed`/`cat` extract of branch `feat/2026-09-18-quiet-predicate-evidence-harness` at `498ad1d0` or of the four prior audit records on main `b05563bc`; the magistrate wrote only this file.

## What was found

The harness `scripts/sample_quiet_predicate_evidence.py` (Exhibit A) runs a load worker that burns a requested share of one CPU core (here 0.1 cores) in fixed periods. `duty_periods` (Exhibit A, line 770) gives each period a thread-CPU budget with an absolute wall deadline and never catches up: CPU that the scheduler did not let the worker burn in one period is discarded, not carried forward (the "no-catch-up rule", lines 775–778 of the docstring; `debt` and `work_budget` at 794–796). The only starvation the row records is `wake_late_s` (line 820): how late the worker woke from the sleep that ends a period. The initial sleep before the first period (`clock.sleep_until(start)` at line 869, in `load_worker`) is outside `duty_periods` and is never recorded. Preemption during a burn shortens the delivered CPU but leaves `wake_late_s` near zero.

The regression `test_real_load_tracks_point_one_core_and_guards_worker_budget` (Exhibit B) launches the real worker for 3 s at 0.1 cores and asserts on the delivered fraction. Round 1 (Exhibit D, record 04) found that a correct worker whose every sleep wakes 1.05 s late delivers 0.033 cores and fails the old two-sided ±0.04 check. The lead's bench fix `498ad1d0` (Exhibit C) keyed a relaxation to the summed `wake_late_s`: over 0.14 cores always fails; with summed lateness ≤ 0.12 s the tight check stands; otherwise the deficit must be ≤ 0.1 × late_s / duration. Round 2 (Exhibit E, record 05) found the same signature survives with two further correct-code inputs:

| Scheduling input (correct code) | Delivered cores | Summed `wake_late_s` | Result under `498ad1d0` |
|---|---:|---:|---|
| worker first scheduled 2 s after `start` (initial sleep, never recorded) | 0.0333 | 0 | FAIL |
| during burning, wall time advances 100× thread CPU time (preempted burn) | 0.0100 | 0.025 | FAIL |

Corroborating datum (record 05, E5): on this idle machine both instrumented runs recorded summed lateness ≈ 0.82–0.90 s, so the "tight" branch never fired; the starvation branch is the one that runs in practice. All three mutations (`cores`, `alignment`, `observer`) are still killed at `498ad1d0` (record 05, E3); the `cores` mutation dies at the pre-launch share guard (Exhibit B, the `process` wrapper) and at the fake-clock budget test `test_cpu_budget_overshoot_and_frozen_duty` (Exhibit B), not at the delivery check.

The lead's adjudication (Exhibit E, record 05a): D5-T1 stays a should_fix OPEN; the question is design-bearing (what a real-scheduler regression may legitimately assert), so no round 2 until this gate rules.

## Q1 — the ruled shape of the real-load regression (rule one option or write a better one)

- (a) Drop the delivery minimum from the real-load test entirely. Keep: the over-burn ceiling (≤ 0.14 cores), the pre-launch share guard, the cleanup/reaping assertions, and the fake-clock tests as the budgeting oracle. The real-load test then proves "never over-burns, launches with the requested share, cleans up", and nothing about delivery.
- (b) Make the harness emit starvation evidence that covers both surviving counterexamples: record the initial-scheduling lateness (actual first wake minus `start`) and, per period, the wall time spent inside the burn loop versus the thread CPU it produced (preemption ratio); then assert the deficit against that evidence (deficit ≤ share × (initial lateness + summed wake lateness + preempted burn wall time) / duration). This changes the harness (row fields or a worker-level field), not only the test.
- (c) Other, with the same burden: the ruled assertion must ACCEPT all three known correct-code inputs (1.05 s late wakes; first scheduling 2 s late; burn preempted 100×) and must REJECT an under-burning defect that is on time (a controller that burns half its budget every period, `late_s` 0, fraction 0.05) unless another named test already rejects it.

Deliver: the ruled option; the exact assertion text (code-level, at the level a seat can implement from it); if (b), the exact field names and the producing line for each, and whether the JSON row shape under `joulewise.quiet_predicate_evidence.v1` changes (that is a contract change and pairs refuters); the reason, with the deciding exhibit or executed probe.

## Q2 — the residual and its limitation statement

Under the ruled option, state in one paragraph what the real-load test can and cannot prove about delivered share on a real scheduler, in words fit for the lane 232 evidence memo (a reader with no project grounding). If the ruled option leaves an under-burning defect that could hide behind observed starvation, name the test that independently catches it or say the residual is accepted and why.

## Q3 — the regression specification for fix round 2

Specify the defect-shaped regression(s) a seat must add or change beside Exhibit B, for BOTH surviving counterexamples: (i) a fake-clock or scheduling fixture where the worker is first scheduled 2 s after `start`; (ii) a burn where wall time advances 100× thread CPU time. For each: what correct code must produce, what the assertion accepts, and the counterfactual mutation each kills (name it: e.g. reverting the no-catch-up rule so budgets carry forward; a controller that under-burns on time; dropping the starvation term). State whether the existing real-load test remains a macOS-only real-subprocess test or becomes deterministic, and what the bench must run to accept the round (single module under `unittest`, the three mutation files in record 02a of activation 507514d5).

## Constraints on the judge

Read-only. A measurement night is armed for 00:00 PDT on this machine: every process you start must end inside 60 s; load experiments at most `--cores 0.1` for 3 s; wall budget for the whole session 15 minutes, hard. Probes allowed: `git show 498ad1d0:<path>`, `rg`/`grep`, `sed -n`, single Python snippets with a fake clock under `/tmp` copies, the single module `python3 -B -m unittest tests.test_sample_quiet_predicate_evidence` at most once (≈6 s). Never run the discovery suite. Do not edit any tracked file. Never touch `/Users/edr/code/JouleWise` (canonical root), any `/Users/edr/JouleWise-measurement-*` directory, `/Users/edr/night-custody`, or `~/Library/LaunchAgents`. Ruling file: `10-coldgate-fable-ruling.md` in this packet directory — sections: Contamination disclosure; Q1 (ruled option, exact assertion text in a fenced block, contract-change statement, reason); Q2; Q3 (regression spec in a fenced block, acceptance commands); Executed probes (commands and outputs). Plain words; define each term at first use. Under 12 KB.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
a92270edf162bd69db4a1528aa6235cfc954f053ec189522988c984613eee527  exhibit-A-harness-duty-periods-and-worker.md
89fb4d3a3b961151def5f5c3b65cd5869d5710c3f5c0329df9c1be8b6e8653d3  exhibit-B-real-load-test.md
c3932e86c2ee26304c55ce07a753ee6fab45db6b3f0a70addb8b76875f62afc7  exhibit-C-bench-fix-diff.md
ffd7d26ba127e98d4dcf289541e3a171affbd44cad3d5b4ad3cafdbd6bb21342  exhibit-D-round-1-records-04-04a.md
daff1d534fb0cd747644662b3eb6980928f1579b6725dabd561f69e1b5021bb3  exhibit-E-round-2-records-05-05a.md
```
