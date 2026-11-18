# First W1 READY record

**DRAFT / INELIGIBLE.** Only the lead may issue W1 READY. The effective
record gives W1 priority at the next eligible clean close. Installation
requires W1's own registered prepare and install route, Ed's notice and
actual veto check, and a fresh arm-time readback.

```pointer
owner: magistrate
wait: UNFILLED (effective launch record if applicable, qualification boundary and latest permitted predecessor's proven clean close)
deadline: UNFILLED (authority validity and W1 schedule references)
on_early_or_refused: keep the ordinary queue before effectiveness; on a refused arm record the cause and immediately release the ladder under the applicable stop scope
next_observable: lead-issued W1 READY and any effective launch record, then the W1 prepare/packet record, actual notice and veto read, and the installation or refusal record
```

## Lead fills before issue

| Field | Fill |
|---|---|
| Typed header | `schema` `joulewise.run_state_item.v1`, `owner` `magistrate`, `status` `DRAFT`. `number`, `issued_epoch_s`, `expires_epoch_s`, `supersedes` and `sets` all UNFILLED. |
| READY issuing lead, issue time and authority item | UNFILLED |
| Authority validity and deadline | UNFILLED |
| W1 registration signer's identity and independent lead signing record | UNFILLED |
| STRICT registration receipt commitment and verification pointer | UNFILLED |
| Probe commitments and verification pointers referenced by the signing record | UNFILLED |
| Immutable commit bound by the receipt (full SHA) | UNFILLED |
| Runtime checkout (receipt-carrying full SHA, tree and clean-state proof) | UNFILLED |
| Verification linking receipt-bound bytes to the clean runtime tree, including the receipt child if distinct | UNFILLED |
| Exact W1 kit, plan and seal commitments | UNFILLED |
| Authorized W1 `HAZARD_PACK` route (registered W1 prepare and install, receipt and restore) | UNFILLED |
| One-shot Part C close, automatic PASS and independent first-pin read on the runtime SHA | UNFILLED |
| Ordinary off-Mac PREQUAL receipt (`prequal.json` pass, runtime SHA and clean checkout) | UNFILLED |
| W1-mode off-Mac PREQUAL receipt (`--w1-next w1` PASS, runtime SHA and clean checkout) | UNFILLED |
| PREQUAL digest verification for installed plan, triage, projection and implementation | UNFILLED |
| Registered native W1 smoke (source checkout SHA, parser PASS, teardown and native acceptance pointers) | UNFILLED |
| Effective condition, if used (already-issued span and its launch-record pointer) | UNFILLED |
| Qualification boundary and permitted predecessor under the issued W1 route | UNFILLED |
| Plan ID and schedule (`t0` local/UTC, runtime/bounds, latest end and deadman) | UNFILLED |
| Authorized Ed notice route and veto interval | UNFILLED |

Use approved evidence pointers or commitments in public records. Keep
protected contents and private locators with their authorized owners.
The runtime SHA is the exact clean checkout cited by both PREQUAL
receipts, the native smoke source and the one-shot Part C. The receipt
can bind a distinct immutable commit only with verified binding to the
runtime tree. A filled header or a pointer alone proves no live predicate.

## Effect and priority

Before an issued READY is effective, record `SESSION_READY=no` and keep
the ordinary queue. The single permitted effective condition is
“effective from the launch record of span X,” where X is already issued
and the launch record is on main. Through the qual-03 close, a READY
posted between qualification s01 and s02 takes effect at s02's launch
record. Then record `SESSION_READY=yes` and let s02 reach its proven
clean close. Qualification results supply no additional arm threshold.

A pre-notice may guide the choice of a short eligible filler and never
holds the host. Once READY is effective, no lower-priority entry arms
ahead of W1's attempt at the next eligible clean close. Running work
finishes. If W1's arm fails, release the ladder immediately. Each
successor still has to satisfy its own predicates and any applicable
host-wide stop. After R1's post-close Check use the current product filler
ladder, with standing F0 retired.

## Magistrate fills before install

| Field | Fresh evidence or disposition |
|---|---|
| Effective W1 READY and registered prepare, rebuilt packet plus digest, rendered plan/seal and schedule readback | UNFILLED |
| Actual Ed notice record, delivery time and authorized veto window | UNFILLED |
| Actual veto read after the authorized interval (time, checker, source and disposition) | UNFILLED |
| Proven qual-03 close for the qualification boundary (register 9) | UNFILLED |
| Latest attempted predecessor and proven clean close (terminal receipt, restore readback, feeds stopped, fence and process group gone) | UNFILLED |
| Fresh runtime SHA/tree, registration and evidence matches | UNFILLED |
| Fresh census (no foreign process, agent, orphan or unowned High Power marker), allowed labels, R1 uninstalled and no R1 chain process | UNFILLED |
| Applicable stops, maintenance marker and conflicting transfer status | UNFILLED |
| Physical setup, AC, series power mode, thermal state and maintenance/hygiene readback | UNFILLED |
| Battery floating at ≥99%, not charging, absolute current ≤200 mA, top-up proof within 1,800 s and OBC-off attestation | UNFILLED |
| Disk floor and reservation, collector and live meter probe proof, network time OFF and word 0 | UNFILLED |
| Host-link deviation and power configuration readback, with link monitor unloaded or `armed_until` evidenced in the notice | UNFILLED |
| Installing magistrate, recheck time and decision | UNFILLED |

The actual latest attempt controls the close check. Apply the
proved-close rule and the registered host predicates. Leave an incomplete
or mismatched copy **DRAFT / INELIGIBLE**. Any missing required evidence,
foreign SHA or unauthorized route is ineligible. A pre-notice or implied
silence cannot fill the actual veto read. Proceed only with a recorded
no-veto outcome from the authorized route.

## Magistrate records the outcome

| Field | Fill |
|---|---|
| Installed jobs and final arm record, or refusal with reason and stop scope | UNFILLED |
| On refusal, next eligible entry and authority, or applicable stop | UNFILLED |
| After execution, registered terminal, restore and release record | UNFILLED |

[W1 native checks and host-link record](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L1184-L1199) ·
[Typed priority and effective launch event](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L17710-L17716) ·
[Pre-notice, refusal and registered route (RL-179 F-10)](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18827-L18832)
