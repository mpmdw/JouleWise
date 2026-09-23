# Bench replay — chain-level `start_drift_s` (full)

Schema `joulewise.bench_replay_start_drift.v1`. Merged sha `4f8bc36d39b71a06d0502016df0ff26f452b7a63` (clean tree: True).
Protocol: envelope 600 s, pitch 620 s, settle 600 s, 12 slots; gap 20 s; cleanup budget 15 s; attestation timeout 5 s.
Registration sha256 `2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1`; bench script sha256 `b11dd00e9116d078d9773355fe1e83beb33fae773289334dbf2a416bbfe911c6`.

Transaction merge `7eb53effc78b8c90995ca8206df67c0e10ff18e5` is an ancestor: True.

## Verdict

**FAIL** — 7/12 slots NOT admissible, so their drift figures are not a measurement of the finalisation tail: slot 1 anchor_status='unknown' (required 'bounded'); slot 1 interior_complete_support=False (required True); slot 3 anchor_status='unknown' (required 'bounded'); … and 11 more; the chain figures themselves are under the bar (max 0.352 s <= 0.5 s); the session-level bar is exceeded too (max 0.608 s > 0.5 s on slots [1]).
max(session `start_drift_s`) = 0.6078682499937713 s (bar 0.5 s; over: [1]).
Session bar exceeded (true whatever the status): True.
Chain-pass/session-fail split requiring escalation (this is `status == ESCALATE`; a FAIL over the session bar reads False here and True on the line above): False.
Inadmissible slots (the finalisation tail did not run): [{'index': 1, 'field': 'anchor_status', 'value': 'unknown', 'required': 'bounded'}, {'index': 1, 'field': 'interior_complete_support', 'value': False, 'required': True}, {'index': 3, 'field': 'anchor_status', 'value': 'unknown', 'required': 'bounded'}, {'index': 3, 'field': 'interior_complete_support', 'value': False, 'required': True}, {'index': 4, 'field': 'anchor_status', 'value': 'unknown', 'required': 'bounded'}, {'index': 4, 'field': 'interior_complete_support', 'value': False, 'required': True}, {'index': 7, 'field': 'anchor_status', 'value': 'unknown', 'required': 'bounded'}, {'index': 7, 'field': 'interior_complete_support', 'value': False, 'required': True}, {'index': 8, 'field': 'anchor_status', 'value': 'unknown', 'required': 'bounded'}, {'index': 8, 'field': 'interior_complete_support', 'value': False, 'required': True}, {'index': 9, 'field': 'anchor_status', 'value': 'unknown', 'required': 'bounded'}, {'index': 9, 'field': 'interior_complete_support', 'value': False, 'required': True}, {'index': 10, 'field': 'anchor_status', 'value': 'unknown', 'required': 'bounded'}, {'index': 10, 'field': 'interior_complete_support', 'value': False, 'required': True}].

## Per slot

| slot | scheduled_mono_s | actual_mono_s | chain drift s | session drift s | collector exit | cleanup proven | cleanup wall s | attestation | attest wall s | anchor | tail s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 345949.298 | 345949.650 | 0.352 | 0.608 | 0 | True | 0.052 | slew_attested | 0.876 | unknown | 5.448 |
| 2 | 346569.298 | 346569.448 | 0.150 | 0.404 | 0 | True | 0.055 | authenticated | 0.855 | bounded | 7.995 |
| 3 | 347189.298 | 347189.448 | 0.150 | 0.404 | 0 | True | 0.063 | authenticated | 0.862 | unknown | 5.497 |
| 4 | 347809.298 | 347809.448 | 0.150 | 0.408 | 0 | True | 0.032 | slew_attested | 0.849 | unknown | 5.427 |
| 5 | 348429.298 | 348429.448 | 0.150 | 0.408 | 0 | True | 0.032 | slew_attested | 0.822 | bounded | 7.356 |
| 6 | 349049.298 | 349049.447 | 0.149 | 0.411 | 0 | True | 0.060 | authenticated | 0.858 | bounded | 7.690 |
| 7 | 349669.298 | 349669.448 | 0.150 | 0.403 | 0 | True | 0.056 | slew_attested | 0.864 | unknown | 5.410 |
| 8 | 350289.298 | 350289.448 | 0.150 | 0.404 | 0 | True | 0.043 | authenticated | 0.729 | unknown | 5.612 |
| 9 | 350909.298 | 350909.448 | 0.150 | 0.406 | 0 | True | 0.057 | authenticated | 0.856 | unknown | 5.537 |
| 10 | 351529.298 | 351529.448 | 0.150 | 0.408 | 0 | True | 0.046 | slew_attested | 0.862 | unknown | 5.565 |
| 11 | 352149.298 | 352149.448 | 0.150 | 0.399 | 0 | True | 0.049 | slew_attested | 0.789 | bounded | 8.410 |
| 12 | 352769.298 | 352769.448 | 0.150 | 0.403 | 0 | True | 0.075 | slew_attested | 0.839 | bounded | 6.923 |

## Replay provenance (never evidence)

| slot | recorder_kind | label shift | K s | frames | source plist sha256 | written stream sha256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | replay | auto | 55167 | 2546 | `ef4429b4a78546318d957ebedc5248d166f3bac4a4d75e8173aabdd891cf2dde` | `d1522a870d0cb01379ff2491f80a41f9497f9149c4dd653b6d52ca83a70fd6a6` |
| 2 | replay | auto | 55179 | 2534 | `d88f88215e53d570b36d9ced75bbfed2f8dc2d128ff48184bbc77b54f1c9cb77` | `03a211bfc5dce1972590b60f729e1627b2b4ff0c3ea62b2f6841a36ed2a33ae1` |
| 3 | replay | auto | 55198 | 2503 | `a7cbfc49461b780e713a71b224d513aaf4059c18a61c8251f67c21c0088d2c18` | `364f1343b29c38a8506bf8a221ae7a233cb8a4c6f8dcdfef0b56cc9d0f105076` |
| 4 | replay | auto | 55220 | 2481 | `116eb2ebed788a94d1afb260b710025c47e0ddaa6de2472f2d00b14ba21d0c6a` | `260af7f91e99c8618614d743bb4046c79f08d1ec8d9380ffd435c42346cc92c9` |
| 5 | replay | auto | 55239 | 2510 | `ecf01ab1711b0374a5007d9f34c80e029293f848d0756deb03d5222a80f1e772` | `a55e6fe68b716a71072e887d997e6fed2bc6a69fead46c17b0b47dee8f33165b` |
| 6 | replay | auto | 55257 | 2487 | `93d9d11474499b187f567fb428a0dccbea03d7ddee1c20b145fc107b31e24e6a` | `8383f714014fb8b40a71329ce730c7a51a76bc23c9b5801c8d451a89dd9388f3` |
| 7 | replay | auto | 55278 | 2487 | `06561794454e444e37fd91e1be6e05bdebde4e12b8d2676e6d4ef684a50071ef` | `39af8c6d44ec238261dba3dce48d6e83b1d2327ab90476551c102bf11443bb54` |
| 8 | replay | auto | 55300 | 2531 | `117e2d51962dd9046523d925037316109175a88d994cc674f621a374cd6f8a18` | `dfe349f694157bed7f905442b9ca993847c4d24eb0838228234a1362ca6a733b` |
| 9 | replay | auto | 55318 | 2528 | `a3e38147bb0ba01a76dc5ec8dc01e175b1739cce670399cbeb051f01d8adcc42` | `ab208dc64014b63779265b54830e453f5cb74ec15c9e27d1f3db3458924f374d` |
| 10 | replay | auto | 55339 | 2501 | `713c2b1f2b1eb76ad311525eba9cd948ff7a23b7e77803013c11b6f0c316caee` | `f06e2945639019853d56f2df789039b2febcc35e3e1c2cfcff615bb0a2f65c0b` |
| 11 | replay | auto | 55359 | 2512 | `a797c292ca71f128553af2e696f22a253c87de9e4903f4acee0e574cf6c48772` | `f7ab9133bea33f11fd4c42a9bbfed42619e63fc98b2f1bb85b144726ef500c2b` |
| 12 | replay | auto | 55377 | 2531 | `f77b72df88abdd3539736791634418580cc587019226275ac3d498378bdf7696` | `d03238bf3308549949253be77c65d57d2a0eaf8e6de2785ee5bb53b92873b55b` |

The bench NEVER turns network time off: the `systemsetup` stub toggles nothing, it only prints the exact stdout the chain's comparator demands. `timed` therefore goes on applying clock corrections for the whole run, and a slot whose capture window contains one comes back `slew_attested`. On a night that is an exclusion; here it is the EXPECTED state of a machine whose clock is still being disciplined, and it is not a bench failure — the verdict treats `slew_attested` and `authenticated` alike. Only `asserted` (the query failed, was blocked, or timed out) is a named slot defect, because then the `log show` whose wall cost this bench exists to measure did not run. The attestation walls in the table above are the cost of a LIVE `log show` over a log that is still receiving `timed` entries.

Under `--label-shift auto` the plist the feeder writes carries LIVE-LOOKING dates: every `<date>` label is the archived one moved forward by one constant whole number of seconds K, so the file cannot be told from a fresh capture by reading it. Nothing in the plist marks it. The provenance is entirely OUT-OF-BAND, in three places that all survive the run: the feeder's sidecar (`source_sha256`, `written_stream_sha256`, `label_shift_s` = K), the envelope's `session.json` (`power.recorder_kind: "replay"`, `power.replay.*`, including K read back from the sidecar), and the custody root itself (`~/night-bench/`, plan id `bench-replay-…`). Under `--label-shift none` the labels are the archived ones and K is 0.

Archive (read-only, never copied): `/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922`.
Outcome: `refused` (rc 2); summary status `REPLAY_NEVER_EVIDENCE`; `evidence_outcome.json` recorder_kind `replay`; plan id `bench-replay-20260923T003627Z`; custody root `/Users/edr/night-bench/bench-replay-20260923T003627Z`.

A refused outcome with `REPLAY_NEVER_EVIDENCE` is the CORRECT result: the harvest-side interlock is what proves these frames can never be labelled evidence. Every slot's row survives the refusal in `evidence_envelopes.jsonl`, which is where the drift figures above come from.

## Machine state

- at start: uptime `17:36  up 3 days, 23:56, 2 users, load averages: 1.34 1.64 1.75`, `pgrep claude` = 0
- at end: uptime `19:50  up 4 days,  2:09, 2 users, load averages: 1.93 1.90 1.80`, `pgrep claude` = 0

Extra daytime load LENGTHENS the inter-slot tail, so a pass taken under load is a fortiori evidence for a quiet night; a FAIL under load is inconclusive and is retried on a census-clean machine.
