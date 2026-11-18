# DRAFT · cl-transfer-01-s01

**Unissued. Hold for effective freeze 2 and registered `lm-transfer-01`.** Date place 1 has no assigned date.

| Binding | Draft value |
| --- | --- |
| Kit | [cl-transfer-01](kits/cl-transfer-01.v1.1.json), SHA-256 `a018bf05c67e0417cb2a3e5cf0f8a3073a7fac9502670f823b10d868539cefd3` |
| Queue | [cq-cl-transfer-01](queues/cl-transfer-01.queue.json), SHA-256 `1b2d179a40a71d9c8ac189996ce6a276bde8fa410fd9abb00a9e1804f33d0c2e` |
| Span | `cl-transfer-01-s01`, sequence 1, attempt 1, roster `L001,L002,L003,L004,L005,L006` |
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
next_observable: Operational Check for cq-cl-transfer-01-s01-a1 after proven close.
```
