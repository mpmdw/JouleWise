# Interim fit twin under RL-184

The eight temporary switches are removed. The required T01, T03, T05 and F02 regressions pass. The isolated synthetic child fixture includes a one-second unsupported GPU piece, token events without a turn index and a span that closed before recording a soak attempt. The fixture uses the registered KM003C decoder and initializer. [RL-184 §3](https://github.com/mpmdw/JouleWise/blob/61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21085)

Tested `scripts/cadence_interim_twin.py` SHA-256 `d2801f1bd7584eda3168489c2b5f94ecc4883653aa7413b1488dbf61975db1d4`.

## Closed path and soak shapes

| Clause | Admitted writer shape and disposition | Writer evidence |
| --- | --- | --- |
| F01 | A literal nonempty relative POSIX path with no empty, dot or parent component. The key is preserved when a span is staged. A null or absent bundle is unbound. | Each leg runtime derives the path relative to its runtime directory, and each span writer copies the result field. [b4b6aeb19 runtime](https://github.com/mpmdw/JouleWise/blob/b4b6aeb192da60d895a7529311b06599efff5be4/joulewise/align/apple/cadence_leg.py#L126), [2d347f721 runtime](https://github.com/mpmdw/JouleWise/blob/2d347f721552fe03bdd19f113e7bad7a7c24908e/joulewise/align/apple/cadence_leg.py#L199), [6e9d42f1d runtime](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/joulewise/align/apple/cadence_leg.py#L199). |
| F02 | The two older writers omit the attempt array, which projects one accepted historical attempt. The newest writer initializes the array empty. If it closes before the first attempt, an empty array with no soak execution step projects zero attempts and zero stopped. A blackout wait is a wait step. | [b4b6aeb19 initialization](https://github.com/mpmdw/JouleWise/blob/b4b6aeb192da60d895a7529311b06599efff5be4/scripts/cadence_legs_runner.py#L316-L321), [2d347f721 initialization](https://github.com/mpmdw/JouleWise/blob/2d347f721552fe03bdd19f113e7bad7a7c24908e/scripts/cadence_legs_runner.py#L318-L323), [6e9d42f1d initialization](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L448-L453). |
| F03 | An attempt has exactly `attempt`, `started_epoch_s`, `refused`, and `output_dir`. A recorded final soak with missing or null `rc` projects `accepted=false`. An interruption during a soak can also leave a nonzero return code and a null refusal. The writer appends the step with a null return code before calling the soak. | [Attempt and step writers](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L575-L603), [step and interruption handling](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L477-L498), [receipt close](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L647-L657). |
| F04 | The newest writer records at most two attempts in order with execution steps `soak` and `soak.a2`. A retry follows a refused first attempt with a failed step. The first refused attempt can point to `soak.rejected1`, including when the span closes during the retry wait. Contradictory histories raise. | [Retry limit](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L84), [retry and rename](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L575-L606). |
| F05 | The three rostered pins omit kind fields, so retries print `kind not recorded` with null provenance. Under the pinned-writer rule, any present structured array or extra attempt field raises for these pins. RL-173 E reserves the structured array for a future runner pin. | [b4b6aeb19 soak](https://github.com/mpmdw/JouleWise/blob/b4b6aeb192da60d895a7529311b06599efff5be4/scripts/cadence_legs_runner.py#L455-L461), [2d347f721 soak](https://github.com/mpmdw/JouleWise/blob/2d347f721552fe03bdd19f113e7bad7a7c24908e/scripts/cadence_legs_runner.py#L480-L486), [6e9d42f1d soak](https://github.com/mpmdw/JouleWise/blob/6e9d42f1dd3d308bc9239143d0d634ab965e50e1/scripts/cadence_legs_runner.py#L575-L606), [RL-173 E](https://github.com/mpmdw/JouleWise/blob/61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L17489). |

F06 and F07 still produce `no` under the registered relative comparisons. The inclusive 2% cutoff and exact agreement on the verdict word preserve `no` for F08. Under the separate post-`no` ruling, F06 and F07 require agreement within 1e-8 relative on every fitted energy value and 1e-6 on predicted onsets. F08 requires agreement within 1e-8 relative and both values within 1e-12 of the threshold. All other verdict and diagnostic equalities still apply. [RL-184 §3.4](https://github.com/mpmdw/JouleWise/blob/61e8c9c2ccfd023c82e0da048dd89f4ed854a5bc/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21137-L21148)

## Verification

| Clause | Regression | Result |
| --- | --- | --- |
| T01 | Inherited column mask for both reduced channels and their folds | PASS |
| T03 | One-second unsupported prefix and connected gap controls | PASS |
| T05 | Absent and null turn indices and token selection matrix | PASS |
| F02 | Empty attempt array in focused and fully bound child modes; null array or empty with a soak step raises | PASS |
| T02, T04, T06–T16 | [Recorded census regressions](2026-11-18-interim-fit-twin-census.md) | PASS |
| F01, F03, F04, F05 | Literal bundle keys, invalid spelling refusal, incomplete final step, writer shape, ordering, retry limit and refusal-kind rejection | PASS |
| F06–F08 | Planted near-zero cases and exact boundary verdict comparison | PASS |
| RL-181 and RL-183a | Actual isolated child, registered pins, response words, refused imports and reads, and no digits in outer streams | PASS |

The 36 focused tests and `git diff --check` pass. Astra's paired census rerun and the primary's stage-1 refusal tests are the separate look acceptance checks. No twin census class is left open in the focused regressions.
