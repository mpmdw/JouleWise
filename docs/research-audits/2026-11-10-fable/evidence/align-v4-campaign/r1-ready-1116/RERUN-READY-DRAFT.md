# DRAFT · One-use R1 rerun READY record

Unsigned worksheet for Opus. Only a complete, clean post-close Check and `R1-RERUN` from the kit's printed `decide` step can send this worksheet to the lead for a fresh READY decision under item 433 and RL-183 §2.6. A fresh lead-issued READY record, a fresh ordinary notice to Ed and the lead, and a fresh directive and veto read are separate requirements for this attempt. The draft carries no authority to arm. [Item 433] · [RL-183 §2.6]

## Read the prior close before filling

Use item 398's **Check after the fence is gone**, with the sequence in item 437. The Check starts with the registered R1 terminal status and chain exit (exit 0 required), followed by fence clearance, exact restore and process/group absence, the three A–B–A G0 releases, uninstall, and the network-time return and OFF/zero readback with minutes ON recorded. Record the close as `OTHER_CLOSE_EPOCH` with `LAST_CLOSE_KIND=other`. Include any required copy/offload verification and the RL-175 D.2 hand count by admitted turn before applying A12/A20. Use only the owning Check and the kit's printed disposition for this worksheet. The shared launcher GO is insufficient. [Item 398 Check] · [Item 437] · [RL-175 D.2]

| Prior close or refusal | Disposition |
|---|---|
| `TYPICAL-CASE`, complete clean Check | Proceed under the existing typical-case route. This worksheet stays unused. |
| `R1-RERUN`, complete clean Check, exact pin and frozen sources | Refer to the lead for one new READY record. The lead decides whether to issue it. |
| `RESEARCH-LEAD`, any gated-D H, incomplete G1 count, thermometry other than `ok`, or redo set at close | Report to the research lead with the permitted printed lines (member and turn index for G1, verdict words for thermometry). Withhold slots and dependent `R_op` fills. An exception controls even if the printed word is `R1-RERUN`. |
| Check missing or incomplete | Obtain the owning Check before considering issuance. For nonzero chain exit or an unproven close or restore, apply RL-179 rows 17 and 21 first, withhold slots, and refer to the research lead once the host is clean. |
| Wrong pin, tree or frozen source | Stop this rerun at the byte gate and report to the lead. If already issued, VOID under the refused-arm rule. The unchanged-pin Part C carry applies only at the admitted bytes. |
| Pre-install gate or arm refusal | While an ordinary gate is open, nothing installs. If the arm refuses, including an install failure, apply the registered preservation, notice and uninstall provisions as applicable, VOID the READY, and release its priority at once. Apply item 437's pre-t0 cancellation path to Ed's NO or a directive stop at that stage. Return any request for fresh authority to the lead. |
| Night job refuses at t0 | Preserve the attempt and every recovery marker and report the refusal to the lead on the next activation. Neither refusal branch supplies a post-close `R1-RERUN` trigger. |

There is no automatic retry. Before READY is effective and after a refused arm releases its priority, the ladder follows its own gates. Standing F0 retires at R1's post-close Check under RL-179 F-4. While a valid READY is effective it takes the next admissible clean close under R-A and RL-172(f). Let running work finish. A pre-notice may inform filler choice under F-10 and imposes no global filler hold. [R-A] · [RL-172(f)] · [F-4] · [F-10] · [Item 437]

## Opus fills at issue

Fill these rows only from the fresh lead decision and its cited evidence. Use the [typed header schema] for the header on main at issuance. The empty cells are intentional.

| Header field | Value |
|---|---|
| `schema` | `joulewise.run_state_item.v1` |
| `number` | |
| `owner` | `lead` |
| `status` | `DRAFT` |
| `issued_epoch_s` | |
| `expires_epoch_s` | |
| `supersedes` | `[]` |
| `sets` | `[]` |

`DRAFT` marks this worksheet. Change the header to `ISSUED` only when the lead signs and posts the new record. The empty arrays give this worksheet no transition or supersession effect on prior items. Keep the following evidence and decisions in the body or the linked fresh arm record, outside the typed header.

| Lead fill | Value |
|---|---|
| Prior R1 attempt and Check provenance (main commit and item, printed `decide` word, terminal status and exit, close and fence times, restore/copy evidence, hand count, gated-D, thermometry and redo verdicts) | |
| Checklist adoption and pin/carry evidence references (including item 328 and its counted Part C G1 re-read) | |
| Effective condition, if chosen, and the issued span/item and launch-record provenance | |
| Fresh validity window, one-use limit and pointer deadline (with time zone) | |
| Lead signature, issue timestamp and new READY item/main reference | |
| Fresh typed arm item/main reference binding this READY to one session on the registered route | |

The lead may issue an unconditional READY or choose any admissible condition under RL-175 A.2. The sole conditional form is “effective from the launch record of span X” for an already-issued span. Until the qualifying launch record is on main, record `SESSION_READY=no` and cite the new READY and A.2. Observe A.2's block boundary and F-10's qualification rule without splitting a protected block. The effective predicate, validity window and timestamps of item 397 belonged to the first run and confer no effect on this one. Enter the fresh issue and expiry values under RL-175 A.1 Q5. [RL-175 A.1–A.2] · [F-10] · [Item 397]

## Registered route and fresh arm fills

Reference the existing [CHECKLIST.md](CHECKLIST.md), [item 398] and the [pinned R1 runbook] for the single-session HAZARD_PACK LaunchAgent route through `scripts/arm_align_r1.py`. Use the full registered R1 program there. The measurement pin is `b2e01464d6d4fbf2901ff4d4154df9455104a12a`, tree `c904864e46879a4adfbdf0b467d4da1ee5928285`. Preserve the ten condition-13 source blobs at that pin and use the existing 25-source manifest checks. The adopted item 328 Part C and its [carry record](CARRY-RECORD-DRAFT.md) carry at the unchanged pin under RL-172b/172c and RL-183 §2.6. Retain its RL-175 D.2 G1 re-read gate. A failed counted-Part-C G1 re-read goes to the research lead. No new Part C is needed at this pin. [SOURCES.sha256](SOURCES.sha256) · [Item 433] · [RL-175 D.2]

Apply item 437's D-7 correction to item 398: use a fresh session-local copy of the committed RL-145 sensor ruling. The sole changed key on the copy is `authorizes_night`, set to `true` under the checklist authority, after confirming `thermal_gates.py` and `thermal.py` still match the `a6a09e6d7` blobs. Keep the committed ruling intact. Record the source and copy digests and the one-key delta. Require a fresh `FOR_LEAD_ARM` packet with the registered weight and stack checks and matching `PKT_SHA` in the arm record. A prior packet supplies no authority. [Item 437 D-7] · [CHECKLIST.md](CHECKLIST.md)

| Fresh arm fill for the authorized lead/magistrate | Value |
|---|---|
| Native checks record on main and current A14, A15, B01–B15 evidence (staging, both interpreters, 60-key check, G1 re-read, host and transfer readbacks) | |
| Actual newest clean close, kind, Check, fence, restore/process and copy/offload evidence, and applicable close floor | |
| D-7 ruling-copy decision, byte comparison and digests, packet verdict and `PKT_SHA` | |
| Fresh session reference, plan ID/digest, arm-record reference and rendered job review | |
| Whole-minute t0 (Pacific, UTC and epoch), install cutoff, driver end, latest end with grace and rendered dead-man deadline | |
| Fresh notice reference, authorized route, actual send time and interval | |
| Last pre-install directive/stop and Ed NO/veto reads, time and disposition | |

Use the latest clean predecessor and item 398's close floors (300 s after campaign, 1,200 s after F0, F2 or other, including R1). Expected runtime is `UNKNOWN` (driver bound 102,168 s, outer bound 119,880 s plus 300 s grace). Follow item 398's timing, install and stand-down provisions. For the new attempt, choose t0 at least 900 s ahead and send the ordinary notice to Ed and the lead as soon as the fresh arm record is read. Use item 306's `directive-notice` route when mail is unavailable. Record the fresh pre-install read, including Ed's NO by reply or `directive` issue. A missing, unsettled or stale arm gate blocks install. [Item 398] · [Item 398 notice]

[Item 433]: https://github.com/mpmdw/JouleWise/blob/f1be75b21/RUN_STATE.md#L1154-L1167
[Item 437]: https://github.com/mpmdw/JouleWise/blob/f1be75b21/RUN_STATE.md#L1055-L1066
[Item 437 D-7]: https://github.com/mpmdw/JouleWise/blob/f1be75b21/RUN_STATE.md#L1075-L1085
[Item 398]: https://github.com/mpmdw/JouleWise/blob/f1be75b21/RUN_STATE.md#L2042-L2158
[Item 398 notice]: https://github.com/mpmdw/JouleWise/blob/f1be75b21/RUN_STATE.md#L2062-L2065
[Item 398 Check]: https://github.com/mpmdw/JouleWise/blob/f1be75b21/RUN_STATE.md#L2155-L2158
[Item 397]: https://github.com/mpmdw/JouleWise/blob/f1be75b21/RUN_STATE.md#L2159-L2175
[RL-183 §2.6]: https://github.com/mpmdw/JouleWise/blob/5a1151544/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20246-L20261
[RL-175 A.1–A.2]: https://github.com/mpmdw/JouleWise/blob/5a1151544/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L17699-L17716
[RL-175 D.2]: https://github.com/mpmdw/JouleWise/blob/5a1151544/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L17846-L17853
[R-A]: https://github.com/mpmdw/JouleWise/blob/5a1151544/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L14164-L14165
[RL-172(f)]: https://github.com/mpmdw/JouleWise/blob/5a1151544/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L17285-L17290
[F-4]: https://github.com/mpmdw/JouleWise/blob/5a1151544/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18713-L18716
[F-10]: https://github.com/mpmdw/JouleWise/blob/5a1151544/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18827-L18834
[typed header schema]: https://github.com/mpmdw/JouleWise/blob/f1be75b21/docs/process/run_state_item.schema.json#L1-L19
[pinned R1 runbook]: https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/r1_arm_runbook.md
