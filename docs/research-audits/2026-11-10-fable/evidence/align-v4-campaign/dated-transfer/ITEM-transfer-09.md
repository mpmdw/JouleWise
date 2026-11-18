# DRAFT · cl-transfer-09-s01

**Unissued. Hold for effective freeze 2 and registered `lm-transfer-01`.** Date place 9 has no assigned date.

| Binding | Draft value |
| --- | --- |
| Kit | [cl-transfer-09](kits/cl-transfer-09.v1.1.json), SHA-256 `03aa6cde0c57e1fd0a1697922bb960df42866db822f1907fb14b63caac46e750` |
| Queue | [cq-cl-transfer-09](queues/cl-transfer-09.queue.json), SHA-256 `f4724a112921718558c40849fdbfa36aac36c08009e0aaa3b37605ecfba8c7c5` |
| Span | `cl-transfer-09-s01`, sequence 1, attempt 1, roster `L001,L002,L003,L004,L005,L006` |
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
next_observable: Operational Check for cq-cl-transfer-09-s01-a1 after proven close.
```
