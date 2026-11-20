ISSUE-READY

All 13 Round 6 fixture cases met the lead’s acceptance criteria for hp-02-s01. The four adverse first Runs returned 1 before dispatch. All eight precondition negatives returned 1 at Start with their archived refusal reasons. The clean s01 Start and Run returned 0 and recorded exactly one launcher call. [Execution log](probes-r6.jsonl)

| Round 5 finding on the revised spec | Evidence at the first Run | Launcher calls |
|---|---|---:|
| [HIGH] [REFUTED] A refreshed main pointer hides a queue revocation from stale inventory | The inventory review was two seconds older than item 485. The Run worksheet classified the fetched revocation as blocking. Run held on decision 485. | 0 |
| [HIGH] [REFUTED] An issue can dispatch despite a revocation published before Start | Item 484 revoked the queue before Start issued its review result. Run opened issue 485 and held because the Start inventory review predated decision 484. | 0 |
| [HIGH] [REFUTED] A magistrate success can clear a host halt | Sequence 50 recorded a failed restore. Sequence 51 recorded a later successful readback. Run held on the unresolved host fault and required typed lead clearance. | 0 |
| [HIGH] [REFUTED] A late filing can clear a failure with an older observation | The successful readback was observed 20 seconds before the failure and filed 10 seconds after it. Run identified newer evidence than the selected success and held. | 0 |

The eight Start negatives exercised an open look reservation, a conflicting hp-01 date, missing LINE2 evidence, a spent leg, occupancy beyond the fence, an unresolved host stop, an unproven s01 restore when considering s02, and an available higher-ranked instrument. [Precondition results](probes-r6.jsonl#L6)

The replay executed the literal Bash and Python from SPEC.md, SHA-256 `9ced6cb75223e606fc2d07d99afba3d06547e9c10c36386c7a7e407f27c6e890`. Historical issues were reconstructed from the Round 5 fixture inputs and a clean s01 Start result so each adverse case exercised Run directly. The host and clock were synthetic, and the launcher recorded its invocation. The replay used one worker and pinned Git objects for fixture construction because the source worktree’s Git metadata was unavailable. Live hardware validation remains provisional. Reproduce in this seat with `python3.13 -IB audit_r6.py`. [Replay driver](audit_r6.py)
