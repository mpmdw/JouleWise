# OSCTX harness: structural consult (fresh Fable 5.1 seat, read-only)

Triggered by the same-signature rule: two consecutive audits found the analyzer admitting cells that should not be combined (audits 14 and 16). The lead adopts this consult as the spec for fix round 5. The seat's full report is kept verbatim at /tmp/4b-osaudit/17-consult (the hand-back). The substance follows.

## Diagnosis

The analyzer never learns which cells the runner *accepted*. It **re-infers** acceptance from side-effects: directory names, `discarded.json` presence, a predecessor check, the schedule, and a pairing key `(stage, block)` that drops `attempt`. Each audit found one more missing inference, and there will always be one more. The runner already knows the exact accepted set (`runner.py:439`, `if not bad:`); it never writes it down.

## Cure: the runner asserts, the analyzer verifies

**The ledger.** Each stage directory holds `ledger.jsonl`: append-only, fsync after each write, one line per event.
- `block_accepted` carries {stage, block, attempt, discard flag, reference_hash, cells:[{slot, arm, dir, label, runs:[{run_id, bundle, materialized_sha256}]}], wall_ns, seal}. It is written at acceptance, and the warm-up block gets one too.
- `block_discarded` carries {stage, block, attempt, reason, trigger, cells, wall_ns, seal}. It is written at every discard and council stop.
- `seal` is the sha256 of the record's canonical JSON. It detects truncation and corruption; it is not a security control (D-161).

**The invariants.** Any violation refuses the stage with an error, never INCONCLUSIVE.
- **I1.** Exactly one `block_accepted` per scheduled block, attempt ≤ 3, with the cells' slots and arms equal to the schedule.
- **I2.** Each block's attempt history is contiguous: discarded a1..a(k−1), accepted ak, no gaps, no duplicates, nothing after acceptance.
- **I3.** Every `cell.json` on disk appears in exactly one ledger record, and every listed dir exists with the right marker. Violations are reported as `unledgered_cell` or `missing_ledgered_cell`.
- **I4.** Rows come only from accepted records. The pairing keys are (stage, block, attempt) everywhere.
- **I5.** The ledger's run_id, bundle and sha equal cell.json and the files on disk.
- **I6.** Every line parses, the seals verify, and the file ends with a newline.

**The tests.**
- The ledger sequence under scripted failures.
- Rows come only from the ledger: an unledgered cell and a missing ledgered cell are both refused.
- The exact round-2 mixed-attempt witness is refused.
- **A property test.** 200 seeded random attempt histories run through the fake runner, and rows must equal accepted cells. Then one random mutation is applied from {drop a discard record, copy an a1 dir to a2, stray a2 beside an accepted a1, duplicate an accepted record, edit a sha, truncate the last line, swap reference hashes}. Every mutation must be refused.

## F7–F9: durable ownership, deferred signals, escalated termination

- **(a) `Critical` sections defer signals.** During a critical section a signal handler only records the signal, and the signal is re-raised on exit. They wrap the network-time `on`, each cleanup, and the final cleanup loop. `timeout=60` goes on those commands.
- **(b) Ownership is durable and released only after proof.** `owned.jsonl` gets its entry before any start, and the release after proof. `runner.py --recover DIR` replays unreleased entries and restores network time. Start is refused while unreleased entries exist. This covers SIGKILL and power loss.
- **(c) SH stop escalates.** SIGTERM, then SIGKILL, sent per pid to every `pgrep -g` member, with a bounded wait and a verify.
- **No separate supervisor.** It is not warranted.

## Acceptance

- The focused suite is green, and the property test passes 200/200.
- Astra's probes are re-run unchanged in the delta audit.
