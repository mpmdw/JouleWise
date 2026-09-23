# Bench replay — chain-level `start_drift_s` (full)

Schema `joulewise.bench_replay_start_drift.v1`. Merged sha `4dea946b5a2eb150e58eadc91709d3b0ddd09f70` (clean tree: True).
Protocol: envelope 600 s, pitch 620 s, settle 600 s, 12 slots; gap 20 s; cleanup budget 15 s; attestation timeout 5 s.
Registration sha256 `2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1`; bench script sha256 `b11dd00e9116d078d9773355fe1e83beb33fae773289334dbf2a416bbfe911c6`.

Transaction merge `7eb53effc78b8c90995ca8206df67c0e10ff18e5` is an ancestor: True.

## Verdict

**FAIL** — max <= 0.5 s NOT shown: over=[] missing=[] recorded=2/12; slot 1 anchor_status='unknown' (required 'bounded'); slot 1 interior_complete_support=False (required True); slot 2 anchor_status='unknown' (required 'bounded'); slot 2 interior_complete_support=False (required True); the session-level bar is exceeded too (max 0.608 s > 0.5 s on slots [1]).
max(session `start_drift_s`) = 0.6076677920063958 s (bar 0.5 s; over: [1]).
Session bar exceeded (true whatever the status): True.
Chain-pass/session-fail split requiring escalation (this is `status == ESCALATE`; a FAIL over the session bar reads False here and True on the line above): False.
Inadmissible slots (the finalisation tail did not run): [{'index': 1, 'field': 'anchor_status', 'value': 'unknown', 'required': 'bounded'}, {'index': 1, 'field': 'interior_complete_support', 'value': False, 'required': True}, {'index': 2, 'field': 'anchor_status', 'value': 'unknown', 'required': 'bounded'}, {'index': 2, 'field': 'interior_complete_support', 'value': False, 'required': True}].

## Per slot

| slot | scheduled_mono_s | actual_mono_s | chain drift s | session drift s | collector exit | cleanup proven | cleanup wall s | attestation | attest wall s | anchor | tail s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 342350.927 | 342351.281 | 0.354 | 0.608 | 0 | True | 0.030 | authenticated | 1.089 | unknown | 5.570 |
| 2 | 342970.927 | 342971.077 | 0.150 | 0.402 | 0 | True | 0.057 | slew_attested | 0.857 | unknown | 5.507 |

## Replay provenance (never evidence)

| slot | recorder_kind | label shift | K s | frames | source plist sha256 | written stream sha256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | replay | auto | 51568 | 2546 | `ef4429b4a78546318d957ebedc5248d166f3bac4a4d75e8173aabdd891cf2dde` | `31eb4c734de5f6aced967edd26c6573d5839326cfcb84c482f926e403356917f` |
| 2 | replay | auto | 51580 | 2534 | `d88f88215e53d570b36d9ced75bbfed2f8dc2d128ff48184bbc77b54f1c9cb77` | `ce9975198634f3048ca1b73ea56515aeacc5327fdd3ad7a6a1bb16ed2e9d6dac` |

The bench NEVER turns network time off: the `systemsetup` stub toggles nothing, it only prints the exact stdout the chain's comparator demands. `timed` therefore goes on applying clock corrections for the whole run, and a slot whose capture window contains one comes back `slew_attested`. On a night that is an exclusion; here it is the EXPECTED state of a machine whose clock is still being disciplined, and it is not a bench failure — the verdict treats `slew_attested` and `authenticated` alike. Only `asserted` (the query failed, was blocked, or timed out) is a named slot defect, because then the `log show` whose wall cost this bench exists to measure did not run. The attestation walls in the table above are the cost of a LIVE `log show` over a log that is still receiving `timed` entries.

Under `--label-shift auto` the plist the feeder writes carries LIVE-LOOKING dates: every `<date>` label is the archived one moved forward by one constant whole number of seconds K, so the file cannot be told from a fresh capture by reading it. Nothing in the plist marks it. The provenance is entirely OUT-OF-BAND, in three places that all survive the run: the feeder's sidecar (`source_sha256`, `written_stream_sha256`, `label_shift_s` = K), the envelope's `session.json` (`power.recorder_kind: "replay"`, `power.replay.*`, including K read back from the sidecar), and the custody root itself (`~/night-bench/`, plan id `bench-replay-…`). Under `--label-shift none` the labels are the archived ones and K is 0.

Archive (read-only, never copied): `/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922`.
Outcome: `refused` (rc 2); summary status `REPLAY_NEVER_EVIDENCE`; `evidence_outcome.json` recorder_kind `replay`; plan id `bench-replay-20260922T233629Z`; custody root `/Users/edr/night-bench/bench-replay-20260922T233629Z`.

A refused outcome with `REPLAY_NEVER_EVIDENCE` is the CORRECT result: the harvest-side interlock is what proves these frames can never be labelled evidence. Every slot's row survives the refusal in `evidence_envelopes.jsonl`, which is where the drift figures above come from.

## Machine state

- at start: uptime `16:36  up 3 days, 22:56, 2 users, load averages: 1.17 1.80 2.98`, `pgrep claude` = 0
- at end: uptime `17:10  up 3 days, 23:29, 2 users, load averages: 2.07 1.86 1.78`, `pgrep claude` = 0

Extra daytime load LENGTHENS the inter-slot tail, so a pass taken under load is a fortiori evidence for a quiet night; a FAIL under load is inconclusive and is retried on a census-clean machine.
