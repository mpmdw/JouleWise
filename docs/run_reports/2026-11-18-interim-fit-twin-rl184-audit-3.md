# Interim fit twin audit after RL-184, round 3

Round 3 blocked `4300ea8e3`. The test cases use synthetic fixtures and the recorded primary outcomes. The twin uses the two registered KM003C pins through its independent child.

Tested `scripts/cadence_interim_twin.py` SHA-256 `a79ccaa4b15e8601500c1653aa1d5c161f4c830678500f42be7b5737dc7ef59c`.

| Finding | Regression and disposition | Result |
| --- | --- | --- |
| T05 | Step 3 JSONL allows an exponent outside the finite float range to reach the hold timestamp conversion. The isolated child agrees on the literal `1e309` case and keeps the earlier quoted-NaN and missing-timestamp results. | PASS |
| T07 | Journal map fields are checked before field access. One out-of-turn record with an array in `sensors` drops the corrupted leg and preserves an estimable cell. | PASS |
| T10 | A null member of the GPU state list fails the affected leg. The remaining legs still produce a verdict. | PASS |
| T11 | Malformed native plist dates are classified at the native frame reader. Numeric elapsed counts use the registered integer pair comparison. Tests cover a malformed date in one leg, fractional elapsed, and the prior truncated frame and quoted rich elapsed controls. | PASS |
| T12 | The histogram checks registered output keys as well as pressure names. The `slope` witness passes and an unknown key still fails the cell. The remaining registered key list needs a code-blind handoff. | Witness PASS |
| T13 | Active time is multiplied by overlap before interval division. Both integer-clock witnesses now fire on the first eligible window at 18 seconds. | PASS |
| T14 | The GPU counter diagnostic and the clock use the same padded rich-sample window. A far-future row with a bad counter cannot affect the turn even if its interval overlaps decode. | PASS |
| F04 | Every recorded attempt refusal must match the runner's `SoakRefusal` step code and error text. Controls distinguish a valid refusal from a terminal `SystemExit(130)`. The bound child refuses the forged terminal summary and the earlier forged retry. | PASS |
| Earlier audits | Required T01, T03, T05 absent turn index and F02 controls and the existing twin regressions. | PASS |
| Private capture | Child stdout is privately captured under RL-181. The outer digit scan and empty outer stderr check cover agreement and refusal. | PASS |

All 44 focused tests passed with the registered decoder and initializer. `git diff --check` passed. Retry and terminal refusal validation follow the same pinned writer handler. [Step error recording](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L477-L495), [soak refusal handler](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L575-L606)

P01 and P02 remain open on the audited parent. P03 and the Stage 1 malformed-input refusals remain open on the audited primary. The paired census rerun remains pending.
