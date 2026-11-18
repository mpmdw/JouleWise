# DRAFT · cl-transfer-05-s01

**Unissued. Hold for effective freeze 2 and registered `lm-transfer-01`.** Date place 5 has no assigned date.

| Binding | Draft value |
| --- | --- |
| Kit | [cl-transfer-05](kits/cl-transfer-05.v1.1.json), SHA-256 `9ace0db032b332a3a350739609e9ba421b2ca5bd84e214ff0af502de1055c20b` |
| Queue | [cq-cl-transfer-05](queues/cl-transfer-05.queue.json), SHA-256 `290cb879a6628690be488fbb41553826b92cdf84269f52339fc6b542dfece5e5` |
| Span | `cl-transfer-05-s01`, sequence 1, attempt 1, roster `L001,L002,L003,L004,L005,L006` |
| Runner | `cadence-legs-v1.1` at `ab32a6c915a9a78f92554a89c5d0eb93333b7a39` |
| Cells | Four A at cap 4,096. L caps in run order 4,096, 3,724. q0, Automatic. |
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
next_observable: Operational Check for cq-cl-transfer-05-s01-a1 after proven close.
```
