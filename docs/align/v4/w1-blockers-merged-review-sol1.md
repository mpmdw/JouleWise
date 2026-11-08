# W1 blockers merged build — Sol 1 executing review

2026-11-08. Task: `w1-blockers-merged-review`.
Branch: `align/2026-11-08-w1bm-review-sol1` (already provisioned, clean at intake).
Reviewed candidate: `565cb1e47`, including Sol base `35dccf241`, Opus U3 arithmetic
and v4-r11 delta2 `9891d679b`.
Fix and witnesses: `abe2d4164`.

**Verdict: ADMIT_WITH_FIXES. The one required change is included in
`abe2d4164`: export steps 4–5 now print numeric counts only. No remaining
merged-build validity, blinding or custody blocker was found in this review.**
This admits the reviewed implementation; it does not issue a registration or
authorize a real arm. Production U3, battery-policy and registration adoption
remain the lead's existing prerequisites. The two reported baseline failures
are confirmed below and are not newly introduced by this merge.

## Authority and boundaries

Read root AGENTS/CLAUDE, Mission M0, orchestration, the generated intake and
queue fences, relevant protocol/registration/runbook sources and targeted
decision-log entries. No active stop card. The explicit brief selects this
offline review over the historical queue and forbids coordination-state edits
and the full suite. Those files were preserved.

`git show origin/main:RUN_STATE.md` item 226 was read at local
`origin/main = 6b6d5a1348e1dc62d8e3dcacd3100916bdf9518e`.
The brief's lead-confirmed leave-one-out clarification governs heavy tails;
the runbook's old “needs lead confirmation” sentence is stale, not an open
ruling. The speed toolbox was also read; no throughput change was attempted.

No network, downloads, real model weights, real measurement records, sealed Block 5
outcomes, prohibited personal paths or real restricted directories were opened.
No analysis pipeline, hardware collection or machine-state mutation was run.
Git used local objects, including its allowed shared alternate. All execution
used synthetic fixtures and temporary repositories. No additional agent or
cross-model consult was launched; the lead owns the other seat and adjudication.

## Findings and witnesses

### 1. Exact series quantile and heavy tails: admitted

The independent stdlib oracle is committed as
`tests/align/test_w1bm_sol1.py:independent_quantile`. It integrates in
`U = sqrt(chi2(n)/n)`, rather than production's chi-square variable X, using

`f_U(u) = 2 (n/2)^(n/2) / Gamma(n/2) * u^(n-1) * exp(-n*u*u/2)`

and bisects `integral f_U(u) * [1-(1-erfc(q*u/sqrt(2)))^16] du = beta`.
Doubling the oracle grid from 4096 to 8192 panels agrees to eight decimal
places for all four cases below. No production quadrature is used in the oracle.

| Pilot n | Beta | Independent q | Production q |
|---|---|---|---|
| 5 | .05 | 4.6574497550 | 4.6574688922 |
| 5 | .025 | 5.5160320381 | 5.5160745328 |
| 7 | .05 | 4.0897897937 | 4.0897895463 |
| 7 | .025 | 4.6927617773 | 4.6927612547 |

This is the exact-model series equation with numerical quadrature, not symbolic
exact arithmetic. The largest tested q discrepancy is `4.25e-5` at n=5,
beta=.025; the independent series probability at that production q is
`.02499918658`. At n=7 the probability discrepancies are about `1.46e-8`.
These numerical errors do not warrant holding W1. Separate spot checks at
n=10 and n=20 also agreed closely.

The code retains a common drift in the zero-centred RMS, uses df=n and N=16,
and makes margins proportional to mean energy with D factor 1.5. The heavy-tail
witness straddles three times the RMS of the OTHER four sessions at n=5:
beta changes from .05 to .025 even though a ratio to the full RMS cannot exceed
sqrt(5). Zero other-session scale also triggers correctly. There is no recentering,
fixed energy floor or historical k substitution.

### 2. Registration, D screen and frozen bar: admitted

Pending, unsigned, numerically edited and policy-edited bars refuse through
the real `require_registration` entry point. Each witness first establishes a
complete passing receipt in an isolated Git repository, so a pending receipt
cannot mask a missing U3 check. The detached signed synthetic fixture also
refuses there because its source/gate bytes lack registration custody; it is
accepted only by the detached synthetic-desk control. This is a custody check,
not an automatic classifier of whether arbitrary committed numbers are real.

The existing blocker module additionally executes export/report/gate drift,
same-commit binding, gate-content disagreement, configuration/window scope,
duplicate-session and W1-training refusals. Sources, arithmetic, OC and the
derivation digest are recomputed. The CLI uses exclusive output creation; U3
artifacts are strict receipt inputs. Series policy forbids deriving a new bar
from judged windows; no such derivation is introduced here.

A missing or refuted R1 D screen leaves the 30B bar valid and D U3 inconclusive.
The desk converts that D result to a non-passing U3 check, requiring the existing
lead disposition. “Optional screen” never means D automatically passes.

### 3. Battery rule and resume: admitted

Both desks reuse the raw journal/controller-span join. The existing raw fixture
tests cover clean flow, idle charging, AC loss, assist and missing/malformed
journals. Window tests cover `battery.member_span` and accumulator excursions:
one such member fails B; assist is disclosed and retained. Missing evidence is
inconclusive, never a passing or empty-vacuous B result.

`battery_window` is present in the gating triage list. A first non-pass resumes
automatically only with the arm-computed fresh top-up/OBC check. A second
consecutive non-pass refuses without a signed ruling for the current previous
window. Unsigned and stale-window rulings refuse. Only `v4_B_bar` is exempt from
`full_desk_gate_pass`; failed or missing U3/cohort checks still fail that gate.

Operational detail for the packet producer: map a desk B `inconclusive` to
packet `status: fail` and include it in `consecutive_non_pass`. The packet
asserts that streak; the evaluator checks its shape and required ruling rather
than independently rebuilding the battery history. No new automation claim is made.

### 4. Export stdout: required fix supplied

At `565cb1e47`, stdout was `{pairs: <count>, unavailable: <details list>}`.
Although ordinary diagnostics contained no numeric energies, this did not meet
the brief's literal counts-only requirement and could forward arbitrary diagnostic
text. New witnesses failed first on both an empty list and a diagnostic payload.

`abe2d4164` changes only that stdout field to the list's length. Both commands now
print `{pairs: <integer>, unavailable: <integer>}`. Detailed unavailability and
the selected energies remain in the exclusively created export JSON. The file
write, estimator and selection procedure are unchanged. The witnesses execute
both CLI commands, verify synthetic energies remain in the files, and verify
diagnostic text stays out of stdout.

Selection is by the fixed design-order manifest before the selected pair's
energy read. Adjacent candidates are skipped by ordinal distance alone; a failed
selected pair never causes a substitute or an energy-based search. The lead must
freeze the manifest before running the export, as the existing runbook requires.

## Confirmed baseline failures

Both full modules were replayed one process at a time against a temporary archive
of `35dccf241`, with the same local origin/main launcher objects available. No
checkout switch or original-tree mutation was needed.

| Module | Merged 565cb1e47 | Sol base 35dccf241 | Diagnosis |
|---|---|---|---|
| `test_v4_powermode_record` | 9 tests, 1 failure | 9 tests, same failure | `DeskPowermodeTests.test_desk_check_passes_only_when_every_bundle_matches` expects the whole extra-check map to contain only `ac_powermode_members`. Its fixture supplies no U3/WP19 registration evidence; the extended desk correctly adds `v4_registration_evidence: False`. |
| `test_v4_prequal` | 33 tests, 1 failure, 3 skips | 33 tests, same failure, 3 skips | `LauncherDryRun.test_real_launcher_keeps_the_venv` uses origin/main's newer launcher: default `--keep-going` is absent from PREQUAL's exact argv expectation. Its separate 120 s help-run deadline also cannot accommodate the launcher's 300 s display dwell. |

The second diagnosis follows the launcher's explicit refusal before display
operations: `remaining <= dwell` returns exit 2. The interpreter remains the
unresolved venv executable; this is not the original venv-resolution bug.
The three skips are the tokenizer tier without `JW_PREQUAL_HF`; that variable
was explicitly removed for these runs.

Suggested lead cleanup: isolate the powermode assertion while retaining a
separate missing-registration refusal test; update PREQUAL's argv expectation
and use the existing synthetic dwell/pmset seams for its help probe. Do not weaken
the production registration or dwell checks. These failures predate the merged
candidate, but a failed PREQUAL report must not be represented as green readiness.

## Verification

Every unittest invocation ran separately and sequentially with Python 3.13.
The full repository suite and pytest were not run, per the binding brief.
Aggregate unittest execution, including baseline replay, failing-first witnesses
and both full WP22 runs, remained below ten minutes and below the 20-minute cap.

For each row below the command is `python3.13 -B -m unittest tests.align.<module>`.

| Module | Result |
|---|---|
| `test_w1bm_sol1` | Final 12 tests OK, 3.848 s |
| `test_v4_w1_blockers` | Final 14 tests OK, 2.777 s |
| `test_v4_cadence` | 28 tests OK |
| `test_v4_registration` | 21 tests OK |
| `test_v4_kit` | 116 tests OK |
| `test_thermal_desk` | 25 tests OK |
| `test_protocol_v4_doc` | 6 tests OK |
| `test_v4_receipt_tiers` | 7 tests OK |
| `test_v4_executed_closure` | 4 tests OK |
| `test_v4_dynamic_closure` | 9 tests OK, including a fresh synthetic process trace |
| `test_v4_record_binding` | 5 tests OK |
| `test_v4_topup` | 11 tests OK |
| `test_r11_delta2_sol1` | 11 tests OK |
| `test_r11_delta2_sol2` | 10 tests OK |
| `test_r1_to_w1_chain` | 6 tests OK |
| `test_v4_powermode_record` | Known baseline failure above |
| `test_v4_prequal` | Known baseline failure and 3 skips above |

`JW_WP22_FULL=1 python3.13 -B -m unittest tests.align.test_v4_w1_synthetic`:
22 tests OK at the merged candidate, 139.097 s, one existing expected failure.
The rerun at committed fix `abe2d4164` also passed: 22 tests in 132.547 s,
one existing expected failure and no skips.
The expected failure is the accepted collector-death divergence: WP8 fails the
member fast while the older design assertion expects continuation. Clean-window
U3, battery/cohort, independent energy integral, contrast and injected-fault checks pass.

`python3.13 -m compileall -q joulewise tests` and `git diff --check` passed.
No native MLX execution was attempted: WP22 injects a labelled fake MLX stream.

## Handoff

Changed files: `scripts/align_v4_u3_export.py`, `tests/align/test_w1bm_sol1.py`,
and this report. No coordination state, decision authority, measured evidence,
production bar, registration signature or battery policy was changed. Local
commit only; no push, merge or external write.

Next exact step: the lead adjudicates both review seats and takes the small stdout
fix, then follows the existing post-R1 export/signing/receipt runbook at the final
code head. Keep missing/refuted D screening inconclusive and obtain the existing
disposition if it occurs. Preserve the frozen selection and one series bar.

Outside this sandbox, the lead still owes the existing native W1 smoke through
the real arm, MLX runtime, meter, finalization and wake, plus registration-grade
U3 source/gate review and physical top-up/OBC evidence. This review supplies no
native performance, thermal, battery or D-transfer validation. No new statistics
ruling is requested. The small quadrature error, trusted packet streak assertion
and baseline PREQUAL failure are the explicit limitations above.
