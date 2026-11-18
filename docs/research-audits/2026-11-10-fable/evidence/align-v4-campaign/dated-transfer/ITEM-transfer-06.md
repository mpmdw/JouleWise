# DRAFT · cl-transfer-06-s01

**Unissued. Hold for effective freeze 2 and registered `lm-transfer-01`.** Date place 6 has no assigned date.

| Binding | Draft value |
| --- | --- |
| Kit | [cl-transfer-06](kits/cl-transfer-06.v1.1.json), SHA-256 `ce150a91217d795ec8d42d6553734c199ab1ef7c30e2fee129576a343cb4c344` |
| Queue | [cq-cl-transfer-06](queues/cl-transfer-06.queue.json), SHA-256 `564e2341f5bb9eb0c3b50f44a9073fbb9b161df86f49fc271c166c708ac4b7e9` |
| Span | `cl-transfer-06-s01`, sequence 1, attempt 1, roster `L001,L002,L003,L004,L005,L006` |
| Runner | `cadence-legs-v1.1` at `ab32a6c915a9a78f92554a89c5d0eb93333b7a39` |
| Cells | Four A at cap 4,096. L caps in run order 3,151, 4,096. q0, Automatic. |
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
next_observable: Operational Check for cq-cl-transfer-06-s01-a1 after proven close.
```
