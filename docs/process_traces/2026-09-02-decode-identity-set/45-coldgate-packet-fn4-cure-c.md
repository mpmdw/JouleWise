# Cold-gate packet: the decode-identity lineage paragraph — Cure C, F-N5/F-N6, and the first-use gate rule (2026-09-02)

Assembled by the magistrate at branch `fix/2026-09-02-decode-identity-set`, commit `fc52bda6` (worktree `/Users/edr/code/JouleWise-wt-decode-id`). The seats read this packet, the exhibits in the manifest, and the code read-only at that commit. This packet asks atomic questions; it offers no diagnosis and no recommendation.

## 1. Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

## 2. Convening triggers (charter §3)

- §3 item 1: round 4 on `docs/contracts/identity_pin_projection.md` §Analysis consumption would be a second fix round on a defect already fixed once (exhibit 41 §2 Grounds 1-2; exhibit 42 Q1). Whether it IS one is question Q1 below.
- §3 item 4: a process rule is proposed (exhibits 40 Q4, 41 §5, 42 Q4) and a ratifying sentence from Ed exists (exhibit 45c).

## 3. The object

The paragraph at `docs/contracts/identity_pin_projection.md:609-621` (exhibit 45a, the file at `fc52bda6`) and the defined-terms block at `:580-594`. Findings on the paragraph, each with its evidence file: F-N4 (exhibit 37: terms used before definition), F-N5 (exhibits 41 §1 and 42 §0 X1: two of the named refusal labels are not what the code emits), F-N6 (exhibits 41 §1 and 42 §0 X2: the pack root is recorded at arm time, not at consumption). Two proposed rewrites called Cure C exist: exhibit 41 §3 "Cure C" (family-level reason-code sentence) and exhibit 42 §2.3 "Cure C (i)+(ii)" (per-hop reason codes in execution order). The consult synthesis (exhibit 44) records what the magistrate adopts; it is custody, not authority.

Code to verify against, read-only at `fc52bda6`: `joulewise/arm_readiness.py` (`_pack_record`, `CONSUMPTION_RECEIPT_KEYS`, `_read_v2_consumption`, `_read_exact_launch_reference`, `_read_lifecycle_receipt`, `authenticate_launch_lineage`, `authenticate_bundle_launch_lineage`, `_replay_consumed_arm`, `LAUNCH_LINEAGE_REASON_CODES`), `joulewise/analysis_engine/inputs.py` (`_read_bundle`).

## 4. Questions (answer each atomically; REFUSE any you cannot answer from the exhibits and the code)

**Q1.** Under charter §3 item 1, is landing a round-4 rewrite of `:609-621` "a second fix round on the same defect"? Answer YES or NO and name the defect you individuate on. (Exhibit 40 says no; exhibits 41 and 42 say the gate is reached either way.)

**Q2.** Execute the five missing-file hops yourself (consumption receipt, pack root, launch manifest, window plan root, start/settle lifecycle receipts) against the code at `fc52bda6` and state the reason code each emits. Does the landed paragraph name the wrong code for any of them? (F-N5.)

**Q3.** Is the pack root recorded in the arm receipt at arm issuance (`_pack_record`) rather than "when the arm was consumed"? Does the consumption receipt carry a pack root of its own? (F-N6.)

**Q4.** Of the two Cure C texts (exhibit 41 §3; exhibit 42 §2.3), which, if either, may land — and with what corrections? Grade every sentence of the chosen text against (i) the first-use rule (each term built before use, glossed at first use, or deleted) and (ii) execution: for each clause that names a reason code, an order, a provenance, or uses before/after/only/never/every/strictly, state the probe you executed and its output. A `file:line` citation is not proof for (ii).

**Q5.** Should the paragraph name each hop's reason code (exhibit 42 form) or the family "the launch-lineage reason code belonging to the artifact that failed" (exhibit 41 form)? Decide on the replication standard (a reader must be able to rebuild the mechanism from the text) and on drift risk; say which consideration you weighted and why.

**Q6.** The proposed process rule, as ratified by Ed's sentence in exhibit 45c: "a pre-landing first-use table is mandatory for contract-prose edits that add, move or rename defined terms or code literals, PAIRED with an executed probe for every behavioural clause (a clause naming a reason code, an order, a provenance, or containing before/after/first/then/only/never/always/every/all/each/strictly/exactly), both pasted by the writer under Executed evidence before a verifier sees the text, the verifier re-running both." Is this text installable as written? If not, give the exact amended text. Attach the drop test you would record (exhibit 41 §5 proposes a noise-rate condition; exhibit 40 Q4 proposes a two-session applicability floor with no auto-delete).

**Q7.** Formulation for round 4: exhibit 41 §4 and exhibit 42 Q3 propose that the magistrate write a claim list and a seat write the prose, with a different-model verifier re-executing every probe. Is anything in that formulation contrary to the charter or to the contract's own conventions? If so, what.

**Q8.** Packet-hygiene duty (charter §6): is this packet complete and neutrally assembled? Name any missing exhibit or leading phrasing.

## 5. What the seats must not do

Do not read `RUN_STATE.md`, `docs/council_log.md`, run reports, `CLAUDE.local.md`, session memory, or any scratchpad. Do not write under the checkout. Do not re-litigate ruling (d) of exhibit 32 (the lineage stays machine-absolute in this lane); only the paragraph's text is in question. Do not lower F-N4's severity. Do not end mid-flight.

## 6. Exhibit manifest

```
4db7e3da039b591b3b66307733a94d09116662fb0628fb5059cd9853504c0152  37-terra-267-delta-re-audit-3-report.md
b20cba048f9e75ec26bf7be7eda75f3e96538414e384d9d460df87276eae963f  38-consult-packet-fn4-fourth-prose-signature.md
d7c5484cbec7c8c2cdf72e99977bd73800c8502ac32633355e299f6dda126e3a  40-luna-268-consult-fn4-report.md
808bd3b0534698ce5aba75b21d7d2636b5a86ea79996ccfb44118efdb922452a  41-opus-seat-consult-fn4-report.md
4ece4e126851489e237d334aec657daf5e78e7f2eb18354c3b49faafbda6ce07  42-blind-fable-seat-consult-fn4-report.md
0739baebb1635891e29a98f1674e3790f52fda5c4358318dac9687c7d2937a1e  44-magistrate-synthesis-fn4-consult.md
fcc9051523fbced6e66da1deaf2b97e5d72ec6c0aaeda8aa4f145717543497ea  45a-exhibit-identity_pin_projection-at-fc52bda6.md
b7dc210c77909965c6abad3a820146ad0b5afd07e86d78690306543a9da5c3e9  45c-exhibit-ed-ruling-2026-09-02-verbatim.md
93e90920ffeaaaa32306fd191d861255633beaec4354c725c9c08ad0c371d553  32-magistrate-synthesis-s1-s3.md
```
