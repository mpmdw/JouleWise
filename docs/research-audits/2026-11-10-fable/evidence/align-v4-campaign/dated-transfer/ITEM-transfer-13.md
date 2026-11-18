# DRAFT · cl-transfer-13-s01

**Unissued. Hold for effective freeze 2 and registered `lm-transfer-01`.** Date place 13 has no assigned date.

| Binding | Draft value |
| --- | --- |
| Kit | [cl-transfer-13](kits/cl-transfer-13.v1.1.json), SHA-256 `fff6daf0bb33f00c74045a092a6f874822c819e37b39f9ad41eb505e253898c2` |
| Queue | [cq-cl-transfer-13](queues/cl-transfer-13.queue.json), SHA-256 `882acb14e13251547647d2632345a9422867ec7541807f28136904160a7196d1` |
| Span | `cl-transfer-13-s01`, sequence 1, attempt 1, roster `L001,L002,L003,L004,L005,L006` |
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
next_observable: Operational Check for cq-cl-transfer-13-s01-a1 after proven close.
```
