# DRAFT · cl-transfer-20-s01

**Unissued. Hold for effective freeze 2 and registered `lm-transfer-01`.** Date place 20 has no assigned date.

| Binding | Draft value |
| --- | --- |
| Kit | [cl-transfer-20](kits/cl-transfer-20.v1.1.json), SHA-256 `7700a96872ef766c6f4926eedc28acea674134683c338991b9e5d2fa7f51f80c` |
| Queue | [cq-cl-transfer-20](queues/cl-transfer-20.queue.json), SHA-256 `e374b389386473debaf53402d4105b7bf6594ed1de224399438059f259ae6c09` |
| Span | `cl-transfer-20-s01`, sequence 1, attempt 1, roster `L001,L002,L003,L004,L005,L006` |
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
next_observable: Operational Check for cq-cl-transfer-20-s01-a1 after proven close.
```
