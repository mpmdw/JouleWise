# W1 registration: Stage A gate

Verdict: ADMIT

- **Gate.** Stage A of the W1 registration receipt (RL-183 §2.7; `docs/align/pilot_protocol_v4.md`, "Registration receipt"). It is also the research lead's diff-only cold pass on the signing head (RL-193 §3 item 9; RL-226 §3 step 5).
- **Reviewer.** Research lead, Fable 5.2 (`claude-fable-5-2`), seat `fable-w1-stagea-cold-1128`, 2026-11-28.
- **Ruling.** RL-227, in `docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md` on the branch `audit/2026-11-10-fable`. The ruling is the record; this report is its summary for the receipt.
- **Reviewed head.** `e0242030576e41d19e37dcd7e319611ed5ce7050`, tree `c903a041737d915391888c7324da8aa96b5b6be0`, branch `ops/2026-11-26-w1-signing`.
- **Signing commit.** The commit on that head that adds the records of section 5 and no change to a reviewed path. This report is one of that commit's files, so it cannot name the commit's id. The receipt names it.

## 1. What the verdict covers

Every component of the W1 registration either has a cold verdict on the bytes the signing commit holds, or had its diff from the verdict's bytes read here. Stage B, the new registration bytes, is a separate gate by another model family and is not judged here.

The verdict holds for a signing commit whose diff from the reviewed head is confined to section 5's records and whatever the step-1 tool regenerates from them. Any other changed path returns to the research lead before the receipt is signed.

## 2. The packet

Prepared by GPT-6.2 Astra, seat `astra-w1-stageab-1128`, at the reviewed head.

| File | sha256 |
|---|---|
| `STAGE-A-PACKET.md` | `cc203428ef9f936b3b537b67606bb74ef3c21a28d98d0c7b27797b1a4d9acf03` |
| `STAGE-B-RECOMPUTATION.md` | `559ce16febf642ef5557a376d0441fc92cbf75b1dc620be9ab5dcec68c56fb6d` |
| `stage-b-gate.json` | `40e9b71885d99099fd16844155e865b596b03ace37679e3711cebc689e0e4aec` |

The packet compares the blob each historical verdict was given on with the blob at the reviewed head: 171 comparisons, **94 equal and 77 unequal**. A further 16 freeze and integration controls are all equal, the ten executed R1 sources among them.

| Verdict | Equal | Unequal | | Verdict | Equal | Unequal |
|---|---:|---:|---|---|---:|---:|
| R11 | 3 | 9 | | #813 | 9 | 9 |
| R11 delta | 0 | 2 | | #826 | 9 | 7 |
| W1-blockers merged | 7 | 8 | | #831 | 4 | 0 |
| R1-to-W1 arm | 0 | 2 | | #839 | 1 | 1 |
| RL-28 | 4 | 0 | | #886 | 2 | 6 |
| RL-35 | 3 | 4 | | #896 | 9 | 16 |
| R11 plan record | 0 | 2 | | #904 | 2 | 0 |
| #774 | 0 | 1 | | #959 | 11 | 2 |
| #787 | 1 | 3 | | #977 | 12 | 0 |
| #790 | 0 | 2 | | #979 | 7 | 0 |
| #798 | 0 | 2 | | #981 | 3 | 0 |
| #806 | 1 | 0 | | RL-206 text union | 0 | 1 |
| LR-U3-1 code | 1 | 0 | | U3 gate | 5 | 0 |

The registration module's bound set, evaluated from its code, is 333 paths at the R1 pin `b2e01464d` and 337 at the reviewed head: four added, none removed. 48 bound paths differ between the two commits. The packet lists the same 48 and each has a comparison row.

## 3. Result of the reading

- **All 77 unequal ranges carry.** Each diff was read from the verdict's commit to the reviewed head, by the research lead or by forks of the same seat. No hunk alters what its verdict was given on except under a later verdict or a named ruling. RL-227 §1 gives the table.
- **PR #896 had no content verdict.** The review the packet cites for it checks that a merge was a pure union. RL-193 §3 had sent #896 to C1's re-signed receipt, and it was merged into the W1 line on 24 November. Its diff from the R1 pin was read here on every bound code file it touches, for what it does on a W1 window. It is **carried**: W1 signs with its bytes, and its own gate stays open for C1. Two effects on W1's own path are looser than at the pin and are disclosed in the deviation log; the rest fail closed, add record fields, or return their input unchanged (RL-227 §2).
- **LR-WP19-1 is ratified.** R1's X-G member did not run the registered seed stream, WP19 records a failed identity, and the X-G contrast is INCONCLUSIVE in W1, a non-veto. The registered seed law is unchanged and W1's own members follow it (RL-227 §3).
- **LR-U3-1 is ratified.** With R1's D screen missing on a record-side reason, the signed U3 policy carries two null configuration digests. D's U3 is INCONCLUSIVE in W1 and in every C and T window (RL-227 §4).
- **The 94 equal rows** were not reread, except six paths that had only #896's merge review behind them.

## 4. The anti-hindsight list

Analysis rules changed since R1's record existed (first session 18 November), each with its ruling id. No change is without one.

| # | Change | Ruling |
|---|---|---|
| 1 | The X-G contrast is INCONCLUSIVE in every W1 print, with its reduced cap | RL-189 §2.3, §2.5 item 3 |
| 2 | Installed decision leaves equal the slot decision; the planning release is generated, compared and bound | RL-189 §2.5 items 1-2; RL-193 §3; RL-207; RL-211 |
| 3 | A rank-deficient S design is a fourth cause of an undefined score | RL-193 §7; RL-212 |
| 4 | Option C: four positive-control windows, B10, and K's disclosure code | RL-198 |
| 5 | Council row 2 names B10 | RL-198a |
| 6 | The dose run may move to calibration completion | RL-200 |
| 7 | The ctl-01 disclosure | RL-190 §3.7; RL-198 |
| 8 | The W1-to-C1 packet checks the supplemental sentinels and the desk proof | RL-162 §5; RL-163 §4 |
| 9 | Member reservations per role | LR-MS1; RL-218 §7 |
| 10 | The S-row builder is carried with its own gate open | RL-160 §4; RL-218 §8 |
| 11 | S is a print; no S outcome word is issued | RL-221; RL-223 |
| 12 | A missing D screen is recorded as two null digests | RL-218 §11.1; LR-U3-1; RL-227 §4 |
| 13 | A seed mismatch on a complete X-G comparison is a recorded failed identity | LR-WP19-1; RL-227 §3 |
| 14 | PR #896 on the W1 line: C1's handoff gate at arm and install, the arm's clock taken at entry, one plan-tree pin where there were four | RL-227 §2 |

Line 14 is not an analysis rule. It is listed because it changed W1's bound arm and staging code after the record existed. Twelve further groups were ruled before 18 November and built after it (RL-148 to RL-185, in #813, #826 and #831). The Part C evaluator's fixes are ordered by RL-219, RL-220, RL-222 and RL-224 and judge a smoke; they are not analysis rules.

## 5. Conditions

All are records. None changes reviewed code.

1. **Five rows in `docs/align/v4/DEVIATIONS.md`,** verbatim from RL-227 §7.1, in the signing commit: `RL218-831-CARRIED`, `R1-D-SCREEN-MISSING`, `R1-XG-SEED`, `C1-896-CARRIED`, `P4-ALLOWLIST-EMPTY`.
2. **Two paragraphs in `docs/align/v4/W1-SIGNING-RECORD.md`** (RL-227 §7.3).
3. **The receipt or its file list marks** the S-row builder's files as carried with their own gate open (RL-218 §8), and #896's eighteen bound files as bound and executed by W1 with #896's cold final pass owed at C1's re-signed receipt.
4. **The step-1 tool is run again at the signing commit** to a fixed point, then the three-blob check, the census, CI green, the receipt, and `--check` exit 0 (RL-218 §10).
5. **Shown by the lead at the signing commit:** the reader-census module and its evidence, the accepted-diff proof with no unaccepted residual, and the published file list (RL-193 §3 items 5, 7 and 8; RL-211).
6. **At W1's arm,** the arm notice records that the staged view's campaign policy file has the sha256 the staged plan tree pins for it.
7. **Before C1 arms:** reports A and B for the S-row builder (RL-160), one cold final pass over PR #896 whole, and a re-signed receipt.

## 6. Not covered

- Stage B's bytes and numbers.
- PR #896 as C1's handoff.
- Any test, suite, trace or probe: none was run in this pass. CI on the reviewed head and the step-1 results are the lead's records.
- The receipt, which did not exist when this was written.
- Native evidence: no W1 window has run.

No custody, energy, power, meter, transcript, slot, hazard, sealed or restricted data was opened, and no value of a file under `configs/campaigns/align_v4/registration/` was read or printed.
