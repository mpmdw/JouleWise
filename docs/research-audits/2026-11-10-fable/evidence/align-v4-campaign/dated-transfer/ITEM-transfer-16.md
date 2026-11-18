# DRAFT · cl-transfer-16-s01

**Unissued. Hold for effective freeze 2 and registered `lm-transfer-01`.** Date place 16 has no assigned date.

| Binding | Draft value |
| --- | --- |
| Kit | [cl-transfer-16](kits/cl-transfer-16.v1.1.json), SHA-256 `5626da9346676158484d557ac2c86474ac66cfc04485c3485690982f704924ee` |
| Queue | [cq-cl-transfer-16](queues/cl-transfer-16.queue.json), SHA-256 `a2df0df7f0e0d98efb812e133de2fbf3b7d2391ca77726e3523bd2f5b110d57d` |
| Span | `cl-transfer-16-s01`, sequence 1, attempt 1, roster `L001,L002,L003,L004,L005,L006` |
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
next_observable: Operational Check for cq-cl-transfer-16-s01-a1 after proven close.
```
