# DRAFT · cl-transfer-19-s01

**Unissued. Hold for effective freeze 2 and registered `lm-transfer-01`.** Date place 19 has no assigned date.

| Binding | Draft value |
| --- | --- |
| Kit | [cl-transfer-19](kits/cl-transfer-19.v1.1.json), SHA-256 `6ebd03e473f20ad4003e9facf51f603507046886e6e90090a370cbd4ee7de828` |
| Queue | [cq-cl-transfer-19](queues/cl-transfer-19.queue.json), SHA-256 `1a8186d844e0caa3b6fd60d50da0c3e8126d78d1a1f82be5aaf5ef8883ddd9af` |
| Span | `cl-transfer-19-s01`, sequence 1, attempt 1, roster `L001,L002,L003,L004,L005,L006` |
| Runner | `cadence-legs-v1.1` at `ab32a6c915a9a78f92554a89c5d0eb93333b7a39` |
| Cells | Four A at cap 4,096. L caps in run order 3,724, 4,096. q0, Automatic. |
| Pinned plan | Expected 12,310 s, worst case 24,750 s, launch minimum 27,260 s. |

Use the [shared draft issue and Check](ISSUE.md). The lead fills the issue timestamp,
authenticated qualifying-window identity and record, actual America/Los_Angeles date
and both t0 bounds, committed issue-queue hash, exact predecessor and proven close.
A refusal or expired date gets a recorded disposition. There is no replacement.

```pointer
owner: magistrate
wait: none
deadline: <LEAD FILLS CHECK TARGET, ISO 8601 WITH OFFSET>
on_early_or_refused: WAIT on a higher-priority entry or a named gate within the authorized date. Record any refusal and expire an unserved date at its boundary.
next_observable: Operational Check for cq-cl-transfer-19-s01-a1 after proven close.
```
