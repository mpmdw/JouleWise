# v5-design-groundup — independent seat handoff

2026-11-08. Branch `align/2026-11-08-v5design-groundup-sol1`.
Starting HEAD `32ba4928573ce1981f8a953ab700f00dda9e94d1`; initial worktree clean.

Built the [ground-up v5 proposal](../v5-design/groundup-sol1.md) and
[synthetic arithmetic checks](../v5-design/groundup-sol1_checks.py). Those two
files and this report are the complete change. No production code changed.

The proposal uses a capability-gated Next-Thinking 4-bit candidate, longer
episodes and two procedurally varied task families; frontier API monitoring;
whole-member DC-in residuals; matched nominal FPR arms; a strong software/time/
replay comparator; runtime-external positive controls; and bounded adaptive
attack development. It assigns 136/240 attacks to the strongest discovered
policies, uses 79 calibration members per pair, and separates 240 benign FPR
tests from 240 attacks and 48 positive controls. It reserves 46 capture nights,
six software-replay nights and 13 contingency nights, with a calendar through
mid-May 2027. Subjective main-track-strength probability: about 25%, highly
dependent on the cheap capability and nonredundancy gates.

Verification:

- Failing-first acceptance run: `python3.13 -B docs/align/squeeze/v5-design/groundup-sol1_checks.py`
  initially ran six tests: five passed and the report-input test failed because
  the report did not yet exist. This is document/arithmetic acceptance evidence,
  not a claim of TDD for an implemented detector.
- Final same command: **6 tests passed**. Checks cover allocations, matched
  rank/FPR arithmetic, member/window envelopes, replay charge, disk estimate,
  exact iid binomial examples, paired sample-size arithmetic and clustering costs.
- `git diff --check`: passed. New Markdown links and Python syntax checked locally.
- No full suite, pipeline, model execution, API request, weight download, live
  measurement, network access or machine-state modification. Tests were one
  process at a time and completed in well under one second of test time.

Standing rulings assumed: all six in the brief (KM003C DC-in authority; scoped
on-host adversary; frontier API primary/no premature v4 scoring; m≥39 with
held-out tests/max ranks; runtime-external controls; escape per attempt primary).
No v4 calibration is transferred. Coordination state and R1's lane are untouched.
No other design-seat branches or real restricted data were read.

Open decisions: canonical A0–A13 definitions were unavailable in the common
read set; the report supplies a clearly provisional mechanism inventory and
NEEDS_RULING crosswalk request. The lead must also confirm full local-model/API
pins, long-night allocation and replay cost, and freeze/test the cluster inference
and drift checks before registration. The nominal FPR guarantee requires
exchangeability; the final cluster power is not certified by these arithmetic
checks. Same-pass and work-substitution attacks may defeat the squeeze.

Native work for the lead outside this sandbox: qualify actual decode/member
timing and capability; 12-turn template/cache/RNG replay exactness; helper
isolation and full teardown capture; DC-in/battery/timestamp audit; thermal
G0/G1/hold behavior; and the unforced helper-sabotage nonredundancy screen.
No new MLX implementation or native tests were written in this design-only run.
Next step: resolve the taxonomy crosswalk and authorize only the bounded
development gates before reserving claim-calibration nights.
