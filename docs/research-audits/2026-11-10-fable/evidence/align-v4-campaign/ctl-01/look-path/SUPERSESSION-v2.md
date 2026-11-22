# ctl-01 look-path suite: superseded v2 expectations (lead record)

Date: 2026-11-22. Owner: release lead (named owner in the frozen suite v3 README and OPEN.md).

Four frozen suite-v2 cases expected `meter_absent`. Under RL-202a §2.4 (candidate-stream definition: sampled streams exist in the span but none is a candidate), the correct code on all seven affected legs is `not_bracketed`. The non-builder suite seat recorded this in freeze 3 (suite-v3 README, `vectors.json`, SPEC §7, OPEN.md) before the build finished. The governing v3 regressions are listed beside each case.

| Frozen v2 case | Affected legs | Superseded expectation | Governing expectation | Governing v3 regression |
|---|---|---|---|---|
| `meter_absent_fresh` | L002 | `meter_absent` | `not_bracketed` | `other_streams_exist_outside_leg`, `no_streaming_samples_fresh` |
| `meter_absent_disposed` | L002 | `meter_absent` | `not_bracketed` | `other_streams_exist_outside_leg`, `no_streaming_samples_disposed` |
| `dc_only_three_hidden` | L002, L005, L008 | `meter_absent` | `not_bracketed` | `correct_code_too_few_hidden_legs` |
| `dc_four_hidden_two_levels` | L005, L012 | `meter_absent` | `not_bracketed` | `correct_code_too_few_hidden_levels` |

Frozen bytes are unchanged: suites v1, v2 and v3 and their manifests are byte-identical to the suite seat's files (SUITE.sha256, SUITE-v2.sha256 05b80b078839db31ae481390824ae8d79c42494fd47516e5b0cab59b4fed5dc6, SUITE-v3.sha256). The acceptance count for PR #951 is therefore 75 of 79 raw outcomes passing, plus these 4 cases passing under their governing expectation; every raw outcome is retained in CI.

Independent confirmation: Mythos 5.2 executing audit of PR #951 head 4df6c5244 recomputed RL-202a §2.4 on the frozen v2 fixtures and got `not_bracketed` on all seven legs; it found the supersession was recorded by the non-builder seat, not by the builder (finding 1, REFUTED as a HIGH).
