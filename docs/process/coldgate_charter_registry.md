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
| Status | **RATIFIED** (Ed ack, 2026-08-05, recorded in `RUN_STATE.md`) — the t3-doctrine cold gate ruled 2026-08-03 affirming the charter text at this digest (`docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md`); Ed's ratification confirmation closes the loop. Prior status: BOOTSTRAP-AUTHORIZED (Ed, 2026-08-03 ~22:44 PT, verbatim declaration recorded in the packet §7). |
| Frozen packet | `docs/process_traces/2026-08-03-t3-doctrine-gate/PACKET.md`, sha256 `1f027d0714f0669a63405c9e245ad2e98f78034bd6608b4130084593e173b616` |
| Consult record | `docs/process_traces/2026-08-03-t3-doctrine-gate/inputs/charter-consult-record.md` |

## Candidate charter v3 (not operative)

| Field | Value |
|---|---|
| File | `docs/process/coldgate_charter_v3_candidate.md` |
| Version | v3 candidate (packet-input amendment) |
| sha256 | `9275316e46c6c7bf084e35caa927dae9727dd544dae72656bed22ba82d22b977` |
| Status | **CANDIDATE — NOT OPERATIVE; AWAITING ED RE-RATIFICATION.** Cold gates continue to use the v2 file and digest in the Operative charter table above. |
| Change authority | D-170 item 4 and its charter-v3 deferral in `docs/decision_log.md` |
| Tracked consult brief | `docs/process/coldgate_consult_brief_template.md` |

Promotion requires Ed to re-ratify these exact candidate bytes. After that
external decision is recorded, the lead replaces the operative charter bytes
with the candidate bytes, verifies that the digest is unchanged, changes the
operative table to v3 with the same digest, and moves v2 into History. Until
all promotion steps occur together, the candidate must not be supplied to a
cold judge as the operative charter.

## History

| Version | sha256 | Disposition |
|---|---|---|
| v1 (2026-08-03) | `2a738630e5bd780b4664ad47d058e93e7241595064b9d0d2dbd223b4bbc8acaa` | Superseded pre-ratification — Sol consult found five seams (bias leakage, missing doctrine, §4 laundering channel, §5 composition holes, hash-pin trust anchor); never used in a live gate. |

## Convening procedure (ADOPTED 2026-08-03 late night — cure for the
## doctrine-gate judges' BLOCKER B1: suppression failed via harness
## auto-injection on the mechanism's first live use)

1. **Clean launch environment:** cold instances are convened from a
   git WORKTREE (where `CLAUDE.local.md` is provably absent — E1
   probe, 2026-08-03) or an equivalently verified doctrine-free
   context. The convener verifies before launch that the instance's
   environment will not auto-load: `CLAUDE.local.md`, session memory
   (path-keyed to the main checkout), or any narrative process/state
   document.
2. **Contamination disclosure duty:** every cold ruling opens with a
   disclosure of any doctrine/memory material present at launch. A
   contaminated ruling is not void per se — it stands or falls on
   whether its conclusions cite verified evidence — but an undisclosed
   contamination discovered later voids the ruling.
3. **Trust anchors at launch:** the expected charter digest (and
   frozen-packet digest) are supplied to the judge from this registry
   at an immutable revision, independently of the packet, by the
   operator or the convening session.
4. Fold items 1-2 into charter v3 at the next byte-change opportunity
   (new candidate, new gate per the bootstrap rule).

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
