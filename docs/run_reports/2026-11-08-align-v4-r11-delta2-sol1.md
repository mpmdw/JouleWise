# R11 delta2 Sol1 review handoff — 2026-11-08

**HOLD** on candidate `f993b784f`, range `353446ad6..f993b784f`.
Full findings, prior-finding dispositions, uncertainty and exact next steps:
[`r11-delta2-review-sol1.md`](../align/squeeze/fanout/r11-delta2-review-sol1.md).
Branch: `align/2026-11-08-v4-r11-delta2-sol1` (already provisioned and clean
at intake). No product changes, state-file edits, kernel registration,
network, push, native MLX, weights, real measurement access or job control.

Changed files are that review, this handoff, and
`tests/align/test_r11_delta2_sol1.py`. The local review commit contains
all three; its exact id is supplied in the final handoff message.

Findings requiring disposition:

- **F01 HIGH:** configured R1 runtime script and config are unbound; the
  current W1 bracket/fiducial launch programs are mistakenly amendable.
  A synthetic clean later commit and a signed amendment demonstrate the
  two admission holes. Already-classified strict paths cannot be amended.
- **F02 MED:** sampling only between windows cannot maintain the required
  continuous float chain through a long measured window. If the battery
  stays full, waiting longer or starting a new log does not repair it.
- **F03 MED:** filtering off-AC/error rows before detecting a completed
  charge bridges an invalid transition. Reconnection can be substituted
  for an earlier completion and thereby satisfy the 1800 s bar incorrectly.

All requested touched modules ran **serially, one module per process**.
Common command prefix:

```sh
JOULEWISE_HOST_STATE_DIR=/private/tmp/r11-delta2-sol1-host \
  python3.13 -B -m unittest tests.align.<module>
```

| Module | Tests | Result | Seconds |
|---|---:|---|---:|
| test_r11_delta_sol1 | 8 | OK | 2.509 |
| test_r11_delta_sol2 | 6 | OK | 4.877 |
| test_r1_rehearsal | 74 | OK | 11.900 |
| test_r1_turn_counts_export | 11 | OK | 2.413 |
| test_v4_cadence | 26 | OK | 0.999 |
| test_v4_dc_sealing | 2 | OK | 0.038 |
| test_v4_estimands | 15 | OK | 0.075 |
| test_v4_executed_closure | 4 | OK | 7.883 |
| test_v4_kit | 116 | OK | 29.920 |
| test_v4_opus_cold_witnesses | 1 | OK | 13.717 |
| test_v4_receipt_tiers | 7 | OK | 8.660 |
| test_v4_registration | 21 | OK | 50.082 |
| test_v4_topup | 6 | OK | 0.027 |
| test_v4_w1_synthetic | 20 | OK, 14 skipped | 44.577 |
| test_r11_review_sol1_witnesses | 5 | OK | 0.003 |
| test_r11_review_sol2 | 4 | OK | 1.113 |
| test_thermal_desk | 25 | OK | 2.027 |
| test_v4_r11 | 27 | OK | 0.787 |
| test_protocol_v4_doc | 6 | OK | 0.716 |

The full command also ran separately and serially:

```sh
JW_WP22_FULL=1 JOULEWISE_HOST_STATE_DIR=/private/tmp/r11-delta2-sol1-host \
  nice -n 19 python3.13 -B -m unittest tests.align.test_v4_w1_synthetic
```

**20 tests in 165.459 s, OK (expected failures=1).** The sole xfail is the
documented WP8 F2 fail-fast behavior after collector death. Companion tests
require X4 exclusion/U1 fault accounting. It is acceptable for this delta.
U3 remains inconclusive and arming remains refused; that test change is
correct while no U3 bar is installed.

New witnesses command:

```sh
JOULEWISE_HOST_STATE_DIR=/private/tmp/r11-delta2-sol1-host \
  python3.13 -B -m unittest tests.align.test_r11_delta2_sol1
```

Initial run: 11 tests in 4.600 s, 7 failure records across 6 methods and
5 passing controls. The module intentionally stays red as review evidence.
The off-AC witness was then sharpened to show an actual 1800 s boundary
violation. **Final rerun: 11 tests in 4.132 s, FAILED (failures=7)**,
with the same six failing methods/five passing controls.
No failing test is called a passing registration gate.

The independent stage-sensitive control matches the registered coefficient
and CI tightly and is invariant to a 70 J nuisance-stage shift. The loose
0.1 J WP22 comparison is to a legacy four-column oracle, while the v4
desk uses five columns/df=3. No solver defect has been demonstrated; the
legacy oracle should be brought to the same model rather than relying on
this tolerance as estimator verification.

Additional clean synthetic W1 audit: `dry.main([OUTPUT, '--inject', 'none'])`
under `nice -n 19`, followed by the independent `dry.ols` solver applied to
the eight contrast rows with four and five columns, first using the world's
own integral and then the desk's integrated energies. It succeeded and
matched the production coefficient (<1e-7 J) and CI (<1e-5 J):

- Legacy oracle: 4.162669121218187 J.
- Same world integrals, stage-adjusted oracle: 4.219431311450080 J.
- Independent fit to desk energies and production desk:
  4.219431311451899 J, df=3, T REJECTED.
- Stage accounts for 0.056762190231893 J; integration accounts for
  1.82e-12 J. This confirms the stated 0.057 J discrepancy is a legitimate
  model change, not a masked integration/solver defect.

Temporary evidence logs are under `/private/tmp/r11-delta2-sol1-tests/`;
the audit summary is `stage_audit.json` there. All inputs/output bundles of
that audit were created synthetically in this session under the permitted
temporary root, never read from study custody.

Completed static checks: `python3.13 -B -m compileall -q joulewise tests`
and `git diff --check`, both exit 0. The 19 baseline/affected modules and
the separate full run account for 404 test instances, 14 default skips
and one accepted xfail. All unittest executions, including the two new
witness runs, total **356.514 s** (426 instances); the additional clean
audit also leaves the work comfortably below the 20-minute test budget.

Native and scientific limits: the Metal cache/thermal/R0 gates,
termination/census and installed deadline checks remain lead-owned and
unrun here. Final U3/U6/B-window, R13/R14, F/C/T and custody/access-history
qualification remain open. Neither portable tests nor the full synthetic
window prove a live hardware gate. No full suite was run, as the explicit
brief prohibits it and only targeted review artifacts are changed.

Next exact step: lead dispositions F01–F03 against sol2, repairs the
boundary, chooses and qualifies the battery procedure, and reruns both
delta2 witness modules and affected modules on one integrated candidate.
No W1 registration or arm is authorized by this review.
