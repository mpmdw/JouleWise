# W1 blockers merged review — Sol2

2026-11-08. **Verdict: ADMIT_WITH_FIXES.** Reviewed candidate `565cb1e47`
(`origin/align/2026-11-08-w1-blockers-merged`), Sol base `35dccf241`, including
v4-r11 delta2 `9891d679b`. Review branch:
`align/2026-11-08-w1bm-review-sol2`. Witness commit: `af6b626aa`.

The U3 arithmetic, optional R1-screen behavior, registration refusals and
standalone battery triage pass the synthetic checks. Full WP22 passes with its
one documented expected failure. Two bounded corrections remain: B-only
exclusions still block the full-desk helper, and export stdout contains detail
lists instead of counts only. Neither requires another scientific ruling.
No new reason to HOLD the statistical design was found.

## Findings and exact next work

### S2-01 — B-only exclusions still block automatic resume through the full desk

**Medium; operational next-arm defect.** In
`scripts/align_pilot_session.py:207`, a B-excluded member sets
`no_member_exclusions=False`. When the harvest records that exclusion,
line 364 also sets `chain_eligibility=False`. The new
`scripts/align_v4_session.py:147-153` helper exempts only `v4_B_bar`, so it still
returns false for these checks. After W1, or a code/config change, the mandatory
`full_desk_gate` therefore prevents the automatic resume that ruling 9 permits,
even if every surviving member and all required U checks pass.

The witness joins `v4_battery.attach`, the actual common
`instrument_checks`, and `full_desk_gate_pass`. It isolates the B-only cause:
all the checks except `no_member_exclusions` and `v4_B_bar` are true, and the
helper refuses. It does not rely on a live window or a hypothetical forged
packet. Independently, the triage test proves first-fail automatic resume,
second-fail refusal, exact-previous-window signed disposition, and continued
top-up/OBC gating.

**Repair:** derive an evidence-aware full-desk verdict that removes only the
B-caused aggregate failures, retaining raw checks, exclusions and every
non-B failure. Do not globally exempt `chain_eligibility` or
`no_member_exclusions`; that would hide unrelated failures. Verify the
harvest-to-common-desk-to-triage path with a B-only non-replay member and a
non-B failing control. Fix before relying on the first-B automatic-resume path;
this is not an additional gate on the initial R1-to-W1 arm.

Witness:
`tests.align.test_w1bm_sol2.BatteryWitnesses.test_B_only_exclusion_does_not_reblock_full_desk_automatic_resume`.

### S2-02 — export steps 4–5 print unavailable details, not counts only

**Low; explicit runbook-output requirement.**
`scripts/align_v4_u3_export.py:185-187` emits `unavailable` as a list of
session/ordinal/reason records for pilots, or reason strings for R1. The brief
requires counts only. Both command witnesses fail this requirement.

The separate positive witness passes: synthetic energy sentinels appear in the
explicit output file and never on stdout. No actual energy leak was observed.
The runbook currently says “counts and unavailable sessions only”; align it
with the stricter brief too.

**Repair:** print numeric available/unavailable counts only; retain the existing
detail records in the exclusively created output file. Count unavailable pilot
sessions and unavailable R1 screens, rather than treating each R1 reason as a
separate screen. Make this small change before the authorized export.

Witness:
`tests.align.test_w1bm_sol2.ExportWitnesses.test_steps_four_and_five_stdout_contains_counts_only`
(both `pilot` and `r1` subtests fail).

## Independent U3 derivation

Let independent null pilot relative differences have zero mean and scale σ.
Then `s0/σ = U`, with `U² ~ chi2_n/n`. Conditional on U, N future standardized
normal differences all pass with probability `erf(q*U/sqrt(2))**N`. Therefore q
solves the integral of `1-erf(q*u/sqrt(2))**N` against

`2*(n/2)**(n/2)/Gamma(n/2) * u**(n-1) * exp(-n*u*u/2)`.

The independent stdlib script used Simpson integration directly over the
**chi radius u**, on `[0,12]` with 16,384 cells and 45 bisections. Production
integrates over chi-square x with 2,000 cells. The committed witness retains
the independent method with 4,096 cells and 40 bisections.

| Pilot n | N | β | Independent q | Implementation q |
|---:|---:|---:|---:|---:|
| 5 | 16 | .05 | 4.657449755003 | 4.657468892217 |
| 5 | 16 | .025 | 5.516032038059 | 5.516074532804 |
| 7 | 16 | .05 | 4.089789793720 | 4.089789546325 |
| 7 | 16 | .025 | 4.692761777304 | 4.692761254735 |

The largest probability error in these cases is about `8.14e-7` (conservative
at n=5). At n=7, β=.05 the independent probability at the implementation's q is
`.050000014597`. This is a numerical quadrature approximation to the correct
exact-model quantile, not a material validity finding. “Exact” describes the
shared-scale distribution, not exact floating-point integration. Additional
n=10 and n=16 checks agreed to about `4.4e-11` or better in q.

The review also verifies:

- The template fixes β=.05, N=16 and f=1.5: W1 has four 30B comparisons and
  one D comparison, C1–C8 and T1–T3 one D comparison each.
- RMS is centred at zero with df=n. Identical nonzero pilot drift retains
  positive RMS even when sample SD is zero. Margins scale linearly with energy;
  there is no additive floor.
- The heavy-tail trigger uses the **other n−1 sessions' RMS**, is strictly
  greater than three, and halves β. A binary-exact equality case does not
  trigger; a five-session outlier that an in-sample RMS would miss does trigger.
  The brief's lead-confirmed leave-one-out rule governs; the merged build note's
  “needs lead confirmation” sentence is stale, not an open ruling.
- Fewer than five sessions, repeated pilot sessions and W1/C1 inputs refuse.
  The exporter chooses by design positions before measuring the selected pair;
  an ineligible selection is unavailable, never substituted.
- Pending, unsigned, arithmetically edited and detached synthetic fixture bars
  refuse through `require_registration`, even with a valid receipt bound to
  the bad bar's committed bytes. Existing custody tests additionally bind and
  mutate the export, justification and independent gate at one commit.
  This checks ordinary custody/adoption, not adversarial forgery detection.
- Missing/refuted R1 D screens retain a valid 30B bar but make D U3
  inconclusive. The D window's U3 check consequently fails the full desk;
  optional does not mean D passes. Source population, D fingerprint and frozen
  window/comparison scope remain enforced.
- One prospective bar serves the series. The derivation rejects judged-window
  inputs, adoption refuses an existing output file, and the receipt binds the
  bar as strict evidence. Nothing here re-derives a bar from W1/C/T outcomes.
- Charging/AC-loss flags and accumulator excursions fail B with zero tolerance;
  missing evidence is non-passing; assist is disclosed and retained. Missing or
  malformed triage rows never pass. Two consecutive non-passes require the
  signed disposition. S2-01 is the integration gap beyond that working triage.

## Verification

Every module ran in its own process, sequentially. No full-suite discovery or
sharding was run. Common command: `python3.13 -B -m unittest tests.align.<module>`.

| Module at reviewed candidate | Tests | Result |
|---|---:|---|
| `test_v4_w1_blockers` | 14 | OK |
| `test_v4_cadence` | 28 | OK |
| `test_v4_registration` | 21 | OK |
| `test_v4_receipt_tiers` | 7 | OK |
| `test_v4_executed_closure` | 4 | OK |
| `test_v4_dynamic_closure` | 9 | OK |
| `test_v4_record_binding` | 5 | OK |
| `test_v4_topup` | 11 | OK |
| `test_km003c` | 19 | OK |
| `test_v4_dc_sealing` | 2 | OK |
| `test_v4_estimands` | 15 | OK |
| `test_v4_kit` | 116 | OK |
| `test_r1_to_w1_chain` | 6 | OK |
| `test_r11_delta_sol1` | 8 | OK |
| `test_r11_delta_sol2` | 6 | OK |
| `test_r11_delta2_sol1` | 11 | OK |
| `test_r11_delta2_sol2` | 10 | OK |
| `test_thermal_desk` | 25 | OK |
| `test_v4_w1_plan` | 12 | OK |
| `test_v4_powermode_record` | 9 | 1 pre-existing failure |
| `test_v4_prequal` | 33 | 1 pre-existing failure, 3 native-tokenizer skips |
| `test_w1bm_sol2` | 12 | 10 pass; 2 failing test methods, 3 failure records (S2-01 and both S2-02 subtests) |

`JW_WP22_FULL=1 python3.13 -B -m unittest tests.align.test_v4_w1_synthetic`:
**22 tests, OK (expected failures=1), 106.232 s.** The expected failure is the
documented WP22 F3 collector-death divergence (fail-fast rather than continuing).
It is not a newly waived failure.

`PYTHONPYCACHEPREFIX=/private/tmp/w1bm-sol2-pycache python3.13 -m compileall -q joulewise tests`:
exit 0. `git diff --check`: clean. Across the 25 module invocations, including
the two base reproductions, unittest reports 447 test invocations and 255.559 s;
the process startup overhead also stays well within the 20-minute limit.
Network-dependent tokenizer work was disabled (`JW_PREQUAL_HF` unset;
`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`).

## Confirmed pre-existing failures

Both complete modules were rerun, separately, in a detached synthetic review
worktree at **`35dccf241`**, with the same local `origin/main` object:
`6b6d5a1348e1dc62d8e3dcacd3100916bdf9518e`. They fail at the same assertions.
Neither test file nor `joulewise/align/prequal.py` changed from base to candidate.

1. `test_v4_powermode_record.DeskPowermodeTests.test_desk_check_passes_only_when_every_bundle_matches`:
   the old fixture creates only collection-plan and powermode bundle bytes.
   The expanded v4 desk also needs U3/WP19 registration evidence and correctly
   returns `v4_registration_evidence=False`. The test asserts exact equality
   with the older one-key result. Repair the fixture or isolate its powermode
   assertion; do not remove the fail-closed registration check. Base: 9 tests,
   1 failure, 0.331 s; candidate: 9 tests, 1 failure, 0.369 s.
2. `test_v4_prequal.LauncherDryRun.test_real_launcher_keeps_the_venv`:
   `check_launcher` expects the old runner argv without `--keep-going`, whereas
   the `origin/main` launcher's R0-L3 default now includes it. Its real `run
   --help` subprocess also has a 120 s deadline, which the launcher's mandatory
   300 s display dwell refuses before running the child (`remaining <= dwell`).
   The unresolved venv interpreter is still preserved; this does not establish
   a regression to the original symlink-resolution bug. Update the prequal's
   argv expectation and synthetic launcher rehearsal, keeping the live 300 s
   dwell intact. Base: 33 tests, 1 failure, 3 skips, 7.678 s; candidate: 33 tests,
   1 failure, 3 skips, 10.956 s. Launcher blob: `776d593ee75a8bf13ab853724ba1e60d2b11d7c3`.

## Handoff and limits

Only `tests/align/test_w1bm_sol2.py` and this report are changed. No production
code, coordination state, registration artifact or measurement bundle was
edited. The new review witnesses intentionally remain red for the lead's
repairs, as prior executing-review witness modules did. No network, model
download, real restricted directory, blinded outcome, live measurement or
running analysis job was accessed. No subagent or external consult was used.

No new MLX code/tests were added. Native MLX/WP19 identity, R1 qualification,
meter liveness and battery/top-up/OBC arm evidence remain the lead's existing
live gates; synthetic WP22 does not discharge them. The unsigned/pending bar
and B policy must still be adopted through the existing registration procedure.

Next exact step: apply S2-01 and S2-02, rerun their witnesses plus the focused
affected modules, then carry out the authorized post-R1 export/signing runbook
and fresh exact-candidate receipt. No open scientific ruling is requested.
The B repair's full integration still needs verification; this review does not
claim it is fixed. Stdlib quantile tolerances and the two inherited stale-test
diagnoses are stated above rather than calling the entire tree green.

Local-only scratch evidence: `/private/tmp/w1bm-sol2-review-logs/` contains all
module logs and `targeted-results.json`; `/private/tmp/w1bm-sol2-base-review/`
is the retained detached base worktree. Nothing was pushed.
