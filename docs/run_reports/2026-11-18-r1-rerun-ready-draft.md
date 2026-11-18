# 2026-11-18 · Item 433 R1 rerun READY draft

The [unsigned, one-use worksheet](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/r1-ready-1116/RERUN-READY-DRAFT.md) gives Opus the fields and the registered route for a future lead decision. It references the original checklist and item 398, uses item 437's D-7 one-key ruling copy, and retains the `b2e01464d` pin, the ten frozen sources and the unchanged-pin Part C carry. The earlier READY supplies neither the effective condition nor its timing to this attempt. Opus owns the new effective condition, if any, under RL-175 A.2.

## Synthetic disposition checks

| Invented input | Expected and observed disposition | Result |
|---|---|---|
| `TYPICAL-CASE` with clean Check | Proceed under the existing typical-case route. Leave the rerun worksheet unused. | PASS |
| `R1-RERUN` with complete clean Check and exact bytes | Send to Opus for a fresh, one-use lead issuance decision. Fresh ordinary notice and fresh directive/veto reads remain separate prerequisites to install. | PASS |
| `RESEARCH-LEAD` or exception | Refer with the permitted printed lines and withhold slots and dependent `R_op` fills. Independently exercised gated-D H, incomplete G1, bad thermometry and redo at close against an invented `R1-RERUN` word. | PASS |
| Missing Check with `R1-RERUN` | Await the owning Check. No lead issuance from the printed word alone. | PASS |
| Wrong pin with `R1-RERUN` | Refuse at the byte gate and report to the lead. If already issued, apply VOID. | PASS |
| Installation/t0 refusal | Installation refusal follows pre-t0 preservation, VOID and release of priority. A t0 refusal preserves the attempt and markers and is reported to the lead on the next activation. Neither queues a rerun. | PASS |

## Focused document checks

- **PASS** · Compared the worksheet's eight header keys and fixed values against the pinned schema. Built two disposable synthetic `DRAFT` headers, one with an invented expiry and one with schema-allowed null expiry, and passed both through the pinned `run_state_items.py` parser and validator. A blank item number and an extra `t0` property were rejected. All live fill cells remain blank. [Schema at `f1be75b21`](https://github.com/mpmdw/JouleWise/blob/f1be75b21/docs/process/run_state_item.schema.json#L1-L19)
- **PASS** · Checked the pinned and relative document references, the exact commit and tree, the first ten source hashes against the existing manifest, and both thermal blob identities against `a6a09e6d7`. Checked that the worksheet preserves fresh READY, notice and veto, separate refusal routes, no automatic retry and no global filler hold.
- **PASS** · Scope is two added Markdown files, the worksheet and this report. This is a Tier 0 document change. Local verification used focused checks only. The repository's docs CI runs on the draft PR in GitHub Actions. [Pipeline tiers at `f1be75b21`](https://github.com/mpmdw/JouleWise/blob/f1be75b21/docs/process/PIPELINE.md#L10-L18)

Intake used the pinned item 433/437/397 passages and item 398 at `f1be75b21`, the standing checklist, and RL-175 A.2/D.2, RL-179 F-4/F-10 and RL-183 §2.6 at audit `5a1151544`. The seat used public planning documents, source bytes, Git metadata and invented fixtures. Native state and all live gates remain for the authorized lead/magistrate.

## Handoff to Opus

When the owning post-close Check and printed `R1-RERUN` qualify, fill the trigger and provenance, new item and epochs, signature, effective condition if chosen, validity and deadlines, native readbacks, fresh plan and t0, notice and directive/veto evidence. Follow item 398 through `scripts/arm_align_r1.py` with item 437's D-7 correction. Use a new lead-issued READY for the single attempt.

**NEEDS_SPEC** · None.
