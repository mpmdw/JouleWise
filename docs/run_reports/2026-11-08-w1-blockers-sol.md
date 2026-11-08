# W1 blockers — SOL implementation handoff, 2026-11-08

Branch: `align/2026-11-08-w1-blockers-sol`.
Base: `05b6d04cba4868531cc03da187689a3dc187e0eb`.
Implementation commit: `40db1c675` — `align v4: derive signed predictive U3 bars and battery window consequences`.
This report is committed separately. No push or merge was performed.

The independent SOL candidate is implemented and synthetically exercised.
**It does not issue a live registration or install a statistics ruling.**
The production receipt and new battery-policy template remain PENDING.
The lead must compare the independent Opus build, rule the choices, obtain
authorized source summaries and complete independent/native admission.

## Findings and resulting behavior

Both requested local-object critical-path audits were read, together with
AGENTS/CLAUDE, Mission M0, stop-card/current-state/queue fences and targeted
protocol/decision authority. The active stop card was NONE. The explicit brief
selects this desk work and prohibits the normal coordination-state updates and
full-suite instruction. No other agent or model was consulted; SOL's build
remains independent.

U3 now has a relative Student-t predictive procedure with one prespecified
separated-ordinal 30B pair per independent session, an explicit series comparison
budget, uncertainty in estimated location/scale, reproducible synthetic OC and
dependence/heavy-tail/transfer/drift sensitivity. The validator recomputes the
derivation, checks a lead signature and exact independent ADMIT, and binds export,
transfer justification and gate bytes to the registration commit. Old constant
bars, self-calibration on W1, missing evidence and configuration drift refuse.
Draft/adoption CLI operations never overwrite an existing artifact.

Important constraint discovered: R1's D_spam a/b pair is adjacent with matched
predecessors. It is explicitly a transfer screen, not a separated-ordinal D
variance estimate. No factor can be justified statistically from that one pair.
The code requires an explicit source→target justification and factor; the test
factor 2 is not a production default. W1 5/17 tests the already frozen bar.

Battery processing reuses the existing raw-journal/controller-span join, without
changing shared Block-5 code or the arm predicate. The proposed signed zero-B
policy admits clean observed windows, retains/discloses discharge assistance on
AC for the GPU endpoint, fails charging/AC-loss windows and keeps missing evidence
inconclusive. Both desks include per-model/window consequences, member observations,
source digests and a print-only no-assist member sensitivity. Empty reports cannot
pass vacuously. B/missing-battery pairs cannot supply passing U3 evidence.

WP22 now builds separate synthetic registration and battery evidence under its
temporary root. Its synthetic R1 X-G completion/contrast fit follows the actually
generated reference turn count. Its independent contrast oracle uses R11's stage
term and positive direction. Fake MLX versions are explicitly synthetic, allowing
the clean window to check D cohort identity instead of accepting a hash of missing
runtime evidence. The final full run passes clean-window U3, battery, cohort,
energy/oracle and contrast checks, plus the injected-fault cases.

Design, equations, inputs, exact prospective workflow and the NEEDS_RULING table:
[W1-BLOCKERS-sol.md](../align/v4/W1-BLOCKERS-sol.md).
Synthetic simulation outputs:
[W1-BLOCKERS-sol-OC.json](../align/v4/W1-BLOCKERS-sol-OC.json).

## Verification

All commands ran locally, one unittest module/process at a time, using synthetic
inputs only. Aggregate unittest time including intermediate failures was about
10 minutes, below the brief's approximate 20-minute limit. No full suite, pytest,
network, model download, measurement command or Block-5 analysis pipeline ran.

| Final command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_v4_w1_blockers` | 9 tests, OK, 5.792 s |
| `python3.13 -B -m unittest tests.align.test_v4_registration` | 20 tests, OK, 33.604 s |
| `python3.13 -B -m unittest tests.align.test_v4_r11` | 27 tests, OK, 0.973 s |
| `python3.13 -B -m unittest tests.align.test_v4_executed_closure` | 2 tests, OK, 3.074 s |
| `python3.13 -B -m unittest tests.align.test_thermal_desk` | 25 tests, OK, 2.831 s |
| `python3.13 -B -m unittest tests.align.test_protocol_v4_doc` | 6 tests, OK, 0.570 s |
| `JW_WP22_FULL=1 python3.13 -B -m unittest tests.align.test_v4_w1_synthetic` | 19 tests, OK, one pre-existing expected failure, 88.523 s |
| `python3.13 -m compileall -q joulewise tests` | exit 0 |
| `git diff --check` / staged diff check | exit 0 after removing an extra fixture EOF blank line |

The expected failure is the existing WP22 collector-death case: WP8 deliberately
fails the member fast, whereas the older design assertion expects it to continue.
It remains explicitly labelled; this lane neither hides nor reclassifies it.

Failing-first evidence: the new blocker module initially produced five errors
against the old APIs (U3 policy unsupported, battery consequence unsupported,
missing non-vacuous session helper). Full WP22 initially failed before W1 because
its reference turn count changed without rederiving R11 contrast evidence; the
next attempt exposed the stale contrast oracle. Both fixture defects were fixed.
The added raw battery test exposed a missing pre-span bracketing sample at fake
time zero; the synthetic clock/journal now brackets the first member. No physics
threshold was loosened. Subsequent final focused and full runs are green above.

The new tests additionally check closed-form t quantiles, small-sample/series-size
widening, source/commit/report drift, raw gate-content disagreement even with a
matching digest, unsigned/pending/forged bars, failed D screening, W1 contamination,
D identity/scope restrictions, idle charging, AC loss, assist and malformed/missing
journals. Fixture assertions are never represented as native evidence.

## Open questions and limitations

The design document's NEEDS_RULING table gives question, options, recommendation
and blocked work. The decisive choices are the relative versus additive energy
law, session selection/minimum sample/normal-law assumptions, the joint U1–U5
error allocation and final comparison horizon, D transfer and R1→final-policy
comparability, and the proposed zero-B window consequence. All need prospective
lead/statistics disposition before live use.

Synthetic OC is a warning against overclaiming: with the example inputs, nominal
series rejection is 0.4%, t3/skew scenarios are 5.1%/6.4%, and twice the assumed D
scale gives 22.8%. The two-SD D drift has little power; even the eight-SD alternative
has only 42.3% series rejection in this simulation. These are model diagnostics
with Monte Carlo uncertainty, not measurements or assurances about the MBP.
The wide predictive interval may be inadequate for the lead's intended control
sensitivity. A finite factor or a signed receipt cannot repair an unsupported
transfer assumption. A distribution-free sample maximum at the example per-pair
alpha would require at least 319 independent differences, not seven.

Real authorized pilot/R1 exports, actual selection/access history, final roster
counts, transfer evidence, real signatures and independent Stage A/B admissions
were unavailable and were not invented. The export's token/clock/eligibility and
source-summary assertions require the independent review described in the design.
Only Python 3.13 was executed here; Python 3.11 CI compatibility was not exercised.

No native MLX code path or Metal device was run. No MLX algorithm changed. Outside
this sandbox and all active measurement/agent load, the lead must run the final
head's existing W1 native smoke and verify actual battery/SMC/journal clocks and
coverage, top-up/OBC/charge-hold evidence, exact-head PREQUAL and registration.
The existing opt-in tiny native stream qualification remains:

```sh
JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx
```

That test is not real D model qualification or authority to disturb the running
blinded job. All live/hardware gates remain lead-owned.

## Files touched

- `joulewise/align/apple/v4_u3.py`
- `joulewise/align/apple/v4_battery.py`
- `joulewise/align/apple/v4_registration.py`
- `joulewise/align/apple/thermal_desk.py`
- `scripts/align_v4_u3_bar.py`
- `scripts/align_v4_session.py`
- `scripts/align_v4_thermal_desk.py`
- `scripts/align_v4_w1_synthetic.py`
- `configs/campaigns/align_v4/registration/battery_window_policy.json`
- `configs/campaigns/align_v4/registration/registration_receipt.json`
- `tests/align/test_v4_w1_blockers.py`
- `tests/align/v4_registration_fixtures.py`
- `tests/align/test_v4_registration.py`
- `tests/align/test_v4_r11.py`
- `tests/align/test_v4_w1_synthetic.py`
- `tests/align/w1_synthetic.py`
- `docs/align/pilot_protocol_v4.md`
- `docs/align/v4/W1-BLOCKERS-sol.md`
- `docs/align/v4/W1-BLOCKERS-sol-OC.json`
- This report.

`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` are untouched. No task was registered, and no real
restricted path, external user directory or sealed outcome was accessed.

Next exact step: lead compares this candidate with the independent Opus build,
rules the five design rows, supplies the authorized export/transfer justification,
then executes derive → independent gate → lead adoption at the final integrated
head. Finish native admission and the signed pending artifacts before W1; if D
transfer cannot be defended, return unresolved and rule the qualification remedy
prospectively rather than selecting a convenient factor.
