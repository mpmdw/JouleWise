# DRAFT · cl-transfer-12-s01

**Unissued. Hold for effective freeze 2 and registered `lm-transfer-01`.** Date place 12 has no assigned date.

| Binding | Draft value |
| --- | --- |
| Kit | [cl-transfer-12](kits/cl-transfer-12.v1.1.json), SHA-256 `b9b7e552a343b1acc8a44cc5eaae4dc586d32e6e8d385df54c10ad5d009259cb` |
| Queue | [cq-cl-transfer-12](queues/cl-transfer-12.queue.json), SHA-256 `e9ef2d490836e75377507c1ad6cebb38b7a801ced948b1f460b0ec8ff456015e` |
| Span | `cl-transfer-12-s01`, sequence 1, attempt 1, roster `L001,L002,L003,L004,L005,L006` |
| Runner | `cadence-legs-v1.1` at `ab32a6c915a9a78f92554a89c5d0eb93333b7a39` |
| Cells | Four A at cap 4,096. L caps in run order 4,096, 3,151. q0, Automatic. |
| Pinned plan | Expected 12,262 s, worst case 24,750 s, launch minimum 27,260 s. |

Use the [shared draft issue and Check](ISSUE.md). The lead fills the issue timestamp,
authenticated qualifying-window identity and record, actual America/Los_Angeles date
and both t0 bounds, committed issue-queue hash, exact predecessor and proven close.
A refusal or expired date gets a recorded disposition. There is no replacement.

```pointer
owner: magistrate
wait: none
deadline: <LEAD FILLS CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: WAIT on a higher-priority entry or a named gate within the authorized date. Record any refusal and expire an unserved date at its boundary.
next_observable: Operational Check for cq-cl-transfer-12-s01-a1 after proven close.
```
