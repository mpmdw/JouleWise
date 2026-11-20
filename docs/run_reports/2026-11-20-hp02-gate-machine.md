# hp-02 gate machine adoption · 2026-11-20

The gate loads the frozen transition and outcome table from the reviewed checkout. The transition function selects the phase and hold outcome from that table. The sequenced ledger records independent blocking facts, failed-read digests and verified dispositions. A failed issue identity or inaccessible issue ledger holds the admitted queue SHA and position in separate custody. A confirmed lm-hp-01 execution remains a shared terminal fact until a lead attestation correction cites the original digest and evidence of error. Ordinary holds still require their own clearance and a fresh assessment.

The date guard works backwards through every outstanding counted span and split window. For each feasible latest start it subtracts the full HP fence, external transfer and startup bound. R1 expiry margins and R2 Start publication checks remain in force. Run finishes its writes before the successful final read and launcher invocation.

## Tier 2 spec freeze

The lead resolved the Q2 replacement-issue binding mismatch by keeping exact issue binding and correcting the frozen observation producer. The successor spec commit is `eafae0cb9eca1c5355091492e3d1423bf3328441`. `Desk.row` now assigns the authenticated issue's record to `observation["issue_record"]` immediately after copying the seed. The corrected file's SHA-256 is `200a4f9a46365bc33a97d63b17f6f9179c0e37b05eba7a77f2f771f1cb5c5ea5`. The other five acceptance files match the original freeze byte for byte. The [successor manifest](../../tests/hp02_gate_machine/SUITE.sha256) changes one entry and has SHA-256 `b48a8b567f20d652abf93fe8261d707a0ec2dfc742986215b58d30a8e48941f4`. The original freeze is preserved in the delivery and at implementation commit `07305edefb94eee7fdb13d240e8aa09fd05eae6b`. Its manifest SHA-256 is `c52623b0fd612c8d33df69e84e365028dca383a99cdcb0b1adda4e2e5dcc92d2`.

The original suite expected 100 replacement-identity recoveries to succeed while supplying the prior issue's record in the observation. The successor freeze corrects those inputs. The production gate and pinned runner are identical across the freeze commit.

## Verification

All 374,900 assertions passed across the eight frozen partitions. This includes all 300 Q2 end-to-end recoveries, 7,749 full-command dated-start probes and 156,825 clock assertions. Each JSON summary reconciled to its complete compressed trace, including its native-command and network isolation assertion. The three new CI-discovered modules carry provisional weights from these synthetic replay wall times in `scripts/test_timings.json`.

A focused Q2 replay first created a custody hold at the queue SHA and position. A correctly bound replacement observation still returned `HOLD_UNKNOWN` before disposition, with zero launcher calls. After a verified disposition named the exact hold, failed-read digest and queue position, stale Start and Run observations naming the prior issue each returned `WAIT_EVIDENCE` with zero launcher calls. Fresh Start and Run observations naming the replacement issue produced exactly one simulated launcher call. The replay recorded zero native-command or network attempts.

All six original hp-02 fixtures match their deliveries byte for byte. The three original CI-discovered hp-02 tests passed locally, covering 60 contract vectors, 54 occupancy decisions, 1,764 occupancy clock cases, 43 runner traces, 11 runner pairs and 360 legacy replay cases. The checks used synthetic inputs and recorded zero native-command attempts and zero measured energy data.

The full repository suite runs on draft PR #890. Local unittest discovery for the shard-invariant test hit filesystem permissions on optional historical archives. The shard discoverer and its timing coverage check run without opening those archives.

The audit base advanced to `eaaa1fd560cd457f4e4ccef316be62af920d08e1` before CI could start. The merge preserves both qualification and hp-02 handoffs in `RUN_STATE.md` and both branches' module weights. The hp-02 item, generator, test and fixture paths are byte-identical to the locally verified tree.
