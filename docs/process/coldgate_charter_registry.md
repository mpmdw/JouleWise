# Cold-gate charter registry (trust anchor)

This file is the external home for the charter's ratification status,
provenance, and operative SHA-256 — kept OUTSIDE the hashed charter
bytes so status changes never mint a new unreviewed charter digest
(Sol consult Q6.1, thread 019fcb1a). The expected digest handed to a
cold judge at launch comes from THIS file at an immutable revision,
independently of the packet.

## Operative charter

| Field | Value |
|---|---|
| File | `docs/process/coldgate_charter.md` |
| Version | v2 (post-consult rewrite, 2026-08-03) |
| sha256 | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` |
| Status | **BOOTSTRAP-AUTHORIZED** (Ed, 2026-08-03 ~22:44 PT, verbatim declaration recorded in the packet §7) — not ratified; awaiting the t3-doctrine gate's ruling on the charter text at this digest. |
| Frozen packet | `docs/process_traces/2026-08-03-t3-doctrine-gate/PACKET.md`, sha256 `1f027d0714f0669a63405c9e245ad2e98f78034bd6608b4130084593e173b616` |
| Consult record | `docs/process_traces/2026-08-03-t3-doctrine-gate/inputs/charter-consult-record.md` |

## History

| Version | sha256 | Disposition |
|---|---|---|
| v1 (2026-08-03) | `2a738630e5bd780b4664ad47d058e93e7241595064b9d0d2dbd223b4bbc8acaa` | Superseded pre-ratification — Sol consult found five seams (bias leakage, missing doctrine, §4 laundering channel, §5 composition holes, hash-pin trust anchor); never used in a live gate. |

## Minimal validator (queued; spec from the consult)

`scripts/validate_gate_packet.py` (to be built): accepts `--packet`,
`--charter`, and an independently supplied `--expected-charter-sha256`;
strictly parses exactly one charter pin in the packet; hashes the
charter and every manifest-listed exhibit; requires trusted pin ==
packet pin == observed hash; emits a receipt (packet digest, charter
digest, exhibit-manifest digest, result); the judge is invoked only
with the exact sealed bytes validated. Until built, the launch-time
expected digest is read from this registry at an immutable revision
and the judge performs the recorded recompute per charter §9
(defense in depth).
