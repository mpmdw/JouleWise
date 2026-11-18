# Interim fit twin audit after RL-184, round 2

Round 2 blocked `30dadd7b4`. The regressions use synthetic cases and the recorded primary outcomes. The focused suite also replays the round-one and earlier audit witnesses. The twin still uses only the manifest-pinned KM003C decoder above the standard library and NumPy.

Tested `scripts/cadence_interim_twin.py` SHA-256 `a1b8fb75dce06be86c7a891d37a7d277e5c3a585e50e5f46932a86144d1a711b`.

| Finding | Regression and disposition | Result |
| --- | --- | --- |
| T05 | Thermal-hold timestamps use the pinned numeric conversion. The string `"NaN"` leaves the cell within and a missing stamp still fails the leg. The bound child matches both recorded outcomes. | PASS |
| T07 | A known PM observation requires a numeric producer clock on every journal row. Malformed readings before and after the scoring interval fail their leg. Missing freshness evidence still permits an unestimable cell. | PASS |
| T08 | The native pressure guard treats `not_read` as unavailable. Its in-turn appearance leaves the cutoff unchanged. | PASS |
| T10 | Zero-total GPU state lists carry no clock. A positive-total row requires frequencies for all its states and numeric active times. Mixed empty states and quoted activity values fail their leg. | PASS |
| T11 | An in-window XML parse failure drops only its leg. Two usable legs still form an estimable cell. Native elapsed string conversion and rich numeric elapsed are tested separately. | PASS |
| T12 | The pressure histogram covers `(turn_start, last_token]`. An unregistered value exactly at start falls outside that histogram. | PASS |
| T13 | The clock uses the member-wide frequency reference and the turn's padded rich-sample range. The ordered weighted mean fires at 18 seconds for the integer-clock boundary reproduction. A sample before the lower bound cannot enter a window. | PASS |
| T14 | Only positive decode overlaps use the measured GPU counter. Quoted counters inside decode and malformed temperatures in post-cut full blocks still fail the leg. | PASS |
| F04 | Retry progression requires the recorded `SoakRefusal` and its runner step code. The test preserves a genuine retry and rejects process exits, other exceptions, inconsistent reasons and the soak child's exit code. The bound child refuses the forged retry even when the reference carries the same forged summary. | PASS |
| Earlier audits and required controls | Nested paths and overrides, overlap and gaps, main and marked delta masks, absent turn index, partial decode, optional pressure, and zero or interrupted soak attempts. | PASS |
| Private capture | The bound isolated child uses the registered private frame. Outer streams contain no numeric values and outer stderr is empty. | PASS |

The 42 focused tests passed with the registered KM003C decoder and initializer. `git diff --check` passed. The retry distinction follows the pinned writer's exception wrapping and the one retry handler. [Soak child result mapping](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L319-L330), [step error recording](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L477-L495), [retry handler](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L575-L606)

P01 and P02 remain open in the audited primary parent. P03 and the malformed-path and soak refusal checks remain open in the audited primary Stage 1. The twin's coverage and cell map transport regressions passed, as did its refusal of fabricated soak provenance and noncanonical bundle paths. Astra's paired rerun remains the look acceptance check.
