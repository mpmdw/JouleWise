ADDENDUM: ISSUED

# Cold addendum SCI-25G83-CANDIDATE-01-A1 — ruling on the refuter's SF-1, SF-2, SF-3 and N-1 to N-4

Judge: cold Fable 5.1 seat, one foreground session, 2026-09-27 16:56–17:10 PDT (14 of the 20 budgeted minutes).
The verdict of the science-gate ruling, PROCEED TO ISSUANCE, is unchanged. This addendum adds one classification, one binding on the issuing transaction, one hold on later measurement windows, and four small corrections. It changes no member, no statistic and no operative number.

Inputs, by sha256 as I read them:

| Input | sha256 |
|---|---|
| Ruling `21-science-gate-ruling.md` | `f9de51b7bf78307ca9239e6750bb13f30f67004483070544fee57c395331f4a4` |
| Refuter `22-opus-refuter.md` | `8679be5c2a59760c71a6f1b2a93cad52360b2789b349450f50c6683b2ec740b4` |
| Statement `00-refusal-branch-final-statement.md` | `8717e33c27f069e3889d8f3d6095d76adbdd6ad9b012482e0cad3a936bb339a6` |
| Candidate `packet/02-candidate.json` | `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2` |
| Registration `preregistration_d079_epoch_25g83_rev1.md` | `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1` |
| Working tree | commit `e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1`, clean before and after |

## 0. Contamination disclosure

1. **Preloaded context I did not choose.** Before my first action the session harness injected the owner's global instruction file, the project instruction file of the judge worktree, and the one-line index of the memory store. I opened none of those files, and none of `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, memory files or skill files. The index carries owner directives and status lines. One of them is the directive this charge cites: anything bearing on whether a number is true is mandatory. I use that directive only as the charge states it. The index holds no B value.
2. **Same model family.** I am Fable 5.1, as was the judge whose ruling I am amending. I sat on no earlier step of this activation.
3. **Made after the values were known.** Every B value of W1 and W2 is printed in the ruling and the refuter's report, and I read both. Every reading of the statement that I give below is therefore a reading made after the outcome was known, and must be reported as such (statement item 10). To limit what that can do, I decide SF-1 by three questions that can each be answered without looking at any B value (§3).
4. **Values I created.** I re-ran the estimator on three captures (§2). That produced one B for an excluded capture, w2-d02, equal to the value both earlier seats had already computed. It is a diagnostic and never a member.
5. **Files.** I changed no existing file in any repository or custody directory. This ruling is one new file, at the path the charge names. Two facts outside the named inputs were read: one line of the earlier activation record `2026-09-27-activation-3ba66eeb/00-activation-record.md` (line 74, to check N-2), and the first judge's scratch outputs `w1.jsonl` and `w2.jsonl` (digests `a62f7d18…` and `336a820e…`, equal to those the ruling records). Scratch is `/tmp/cg-sci-a1-77b1bee2/` (`invariance.py` `55feae59…`, `invariance.out` `e01decf2…`).
6. **Not read.** The owner's directive #416 itself. I found no copy of its text in the decision log. I know its clause 3 only as statement items 7(b) and 9 quote it. §3.4 says what follows from that.

## 1. Words used

- **Capture**: one 197-second recording of the power sampler while the machine runs 59 commanded one-second GPU load pulses.
- **B**: the one number a capture contributes, in seconds: the largest timing uncertainty of any pulse edge plus the uncertainty of placing the capture on the wall clock.
- **Frame**: one power sample. **Cadence**: the length of the frames the sampler actually delivers. It is asked for 100 ms and delivered 127.6–130.2 ms in this epoch.
- **Estimator**: the code that turns a capture's raw bytes into B. It lives in four files (§4). **Digest**: the sha256 of a file's bytes; two files with the same digest are the same bytes.
- **Cell**: one rectangle of candidate pulse-edge timings that the estimator evaluates. **The cap**: the limit of 165,000 cells per capture, the constant `DETECTION_PROJECTION_CELL_BUDGET` at `joulewise/powermetrics_fiducial.py:88`. A capture that needs more is stopped, recorded invalid with reason `detection_nonconvergent`, and yields no B.
- **Member**: a capture recorded valid whose clock alignment resolved. The candidate has 12. **S**, **C**, **level screen**: the three operative numbers computed from the members' B values, as the ruling §1 defines them.
- **The issuing transaction**: the single reviewed change, governed by decision D-138, that turns the candidate into the calibration in force and updates every file that refers to it.
- **Bracket**: in a measurement window, one workload measurement with a calibration capture before it and one after it. If the capture before it is invalid, the bracket is abandoned and the measurement is not used.
- **Claim-bearing window**: a measurement window whose numbers will be reported as results.
- **F1**: the ruling's finding that the cap, sized in August for ≈120 ms frames, sits inside this epoch's workload and stopped 8 healthy captures.

## 2. What I executed

**The four estimator files in my working tree** have exactly the digests the candidate pins under `prospective_rederivation.estimator_code_sha256`:

| File | sha256 |
|---|---|
| `joulewise/powermetrics_fiducial.py` | `386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92` |
| `joulewise/uncertainty_evidence.py` | `b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8` |
| `joulewise/adapters/powermetrics.py` | `70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4` |
| `joulewise/reduce.py` | `7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc` |

**What the cap does in the code.** `_ProjectionWorkBudget.consume_cell` (lines 528–547) counts one cell per call and raises a stop signal when the count reaches the cap. It returns nothing and changes no fitted quantity. The cap can therefore only decide whether a capture finishes. It cannot move the B of a capture that does finish.

**The same thing, measured.** I re-ran the estimator from raw custody bytes (digests checked against each capture's own record) at three cap values:

| Capture | Status on record | Cap | Result | Cells used | B (s) |
|---|---|---:|---|---:|---|
| w1-d06 | member | 165,000 | fitted 59 of 59 | 163,849 | 0.02626709931386116 |
| w1-d06 | member | 206,000 | fitted 59 of 59 | 163,849 | 0.02626709931386116 |
| w1-d06 | member | 5,000,000 | fitted 59 of 59 | 163,849 | 0.02626709931386116 |
| w2-d10 | member | 165,000 | fitted 59 of 59 | 163,405 | 0.03807857930294817 |
| w2-d10 | member | 206,000 | fitted 59 of 59 | 163,405 | 0.03807857930294817 |
| w2-d10 | member | 5,000,000 | fitted 59 of 59 | 163,405 | 0.03807857930294817 |
| w2-d02 | invalid | 165,000 | stopped, `detection_nonconvergent` | 165,000 | none |
| w2-d02 | invalid | 206,000 | fitted 59 of 59 | 165,311 | 0.029163507175724863 (diagnostic) |
| w2-d02 | invalid | 5,000,000 | fitted 59 of 59 | 165,311 | 0.029163507175724863 (diagnostic) |

w1-d06 is the member nearest the cap. w2-d10 is the member that sets the level screen. Both give the stored B to the last digit at every cap value. w2-d02 is the excluded capture nearest the cap: it needed 311 cells more than allowed, which is 0.19 %. I ran 2 of the 12 members. The ruling and the refuter each report the same result for all 12.

**Branches that would change an estimator file.** Four branches on the remote are not merged into main and differ from it in one of the four files:

| Branch | Commit | Dated | File touched |
|---|---|---|---|
| `feat/2026-09-04-instrument-path-pin` | `bda7ffe0` | 2026-09-04 | `powermetrics_fiducial.py` |
| `feat/2026-09-04-raw-capture-digest` | `aeea07b6` | 2026-09-04 | `reduce.py` |
| `feat/2026-09-24-acc-25g83-v4-rev4` | `ea10e3c8` | 2026-09-24 | `powermetrics_fiducial.py`, `reduce.py` |
| `impl/p2041` | `5135c1d2` | 2026-07-11 | `reduce.py` |

The refuter named the first three. The fourth is mine.

**How work grows with frame length.** A straight-line fit of cells needed against median frame length, over the 20 captures whose clock alignment resolved, gives about 7,500 more cells per extra millisecond of frame (correlation r = +0.82, which I recomputed from the first judge's outputs). At 127.8 ms the fitted need is about 152,800 cells; at 129.7 ms about 166,900. Individual captures sit up to 11,700 cells above the line.

**Can W1 and W2 say whether power depends on cadence?** No. The GPU's resting power reads 0.0 W in all 20 captures, so there is nothing to correlate. The question needs a real workload.

## 3. SF-1 — is the cap a "defect found in the code that derives them"? No.

### 3.1 What item 7(b) says and when it applies

Item 7 of the statement applies only "if the cold science gate or the issuing transaction rejects" the candidate. Item 7(b) then makes the rejection final in two cases: the fix would change the member list, the statistics or S, C and the level screen; or the rejection is "for a defect found in the code that derives them". Final means the consequences of item 4(a) to (d): derivation under Revision 5 ends, nothing issues, and all 24 captures become diagnostics that can never be members.

The science gate did not reject. So 7(b) has not been triggered. The question left open is whether the issuing transaction's own gate should reject on F1. The refuter is right that the ruling never answers this, and that its words "mis-sized" and "sign of an artifact" invite the wrong answer.

### 3.2 The test

I take "a defect in the code that derives them" to mean one of two things: the code does something other than what was registered for it, or the code produces a wrong value. Three questions decide it. None needs a B value.

1. **Was the behaviour fixed before the data?** Yes. The stop rule was registered on 2026-08-15: exhausting the cap "always makes the evidence `invalid`, clears the fitted bound, discards every partial fit", and the capture is "a completed `ordinary-invalid` observation" (decision log, D-078 registry amendment, bounded pulse-detection projection). The value 165,000 was frozen on 2026-08-18 (D-143). The registration, written 2026-09-10, pins the estimator by digest and says "an estimator-code rotation mid-campaign" voids it (lines 136–137). Revision 5 was sealed 2026-09-25. The captures ran 2026-09-27. The file that holds the cap has the pinned digest today (§2).
2. **Did the code do what was registered?** Yes. w2-d02 at cap 165,000 stops at cell 165,000 with `detection_nonconvergent` and no B (§2). That is the registered behaviour, word for word.
3. **Does the cap enter any derived number?** No. It enters no B (§2: code and measurement). S, C and the level screen are arithmetic on the 12 member B values, and the ruling §3 reproduced that arithmetic independently.

The member list is therefore the registered member list. The registration defines a member by the record's disposition ("every observation … whose ledger disposition is valid and whose stored anchor-v3 outcome … resolves", lines 156–157), and the cap was part of what "valid" meant on the day that sentence was sealed.

### 3.3 What F1 is

F1 is a sizing assumption that no longer holds. The August sizing saw captures needing 112,205–137,189 cells and left 20.3 % of room. This epoch's frames are about 7 % longer and healthy captures need 144,037–170,965. The cap's purpose is to stop a fit that will never finish. Stopping a fit that would have finished 311 cells later serves no purpose. The cost is yield (12 of 24 where 20 of 24 were usable) and a corpus that is 25 % longer-cadence against 45 % in the usable set. Those are limits of the registered instrument at this epoch. They are disclosed (D1, D2) and repaired later (§4, §5). They are not errors in a number.

**The counter-argument, and why it fails.** One can say: 8 healthy captures were left out, so the member list is wrong. But the protection a registration gives is that the rule was fixed before the data, not that the rule was the best one. Two seats now know all 20 B values. Any change to the member list made today is a choice made with the values in view, which is the one thing the registration exists to prevent ("no parameter is tuned between observations", line 145; item 7(b): "a repair can no longer be ruled blind"). The ruling also measured what the rule did in effect: it did not select on B (r = −0.05 between cells and B; permutation p = 0.44).

**There is no route by which the 8 captures enter this corpus.** If F1 is not a defect, the candidate issues with its 12 members. If a gate holds that F1 is a defect, item 7(b) sends everything to item 4 and all 24 captures become diagnostics. Item 7 also says that where (a) and (b) both seem to apply, (b) governs. No reading allows a re-prepared candidate with a different cap.

### 3.4 Directive #416, clause 3

Item 7(b) says the owner's directive "already answers a defect in the derivation path with recapture". I have not read the directive (§0 item 6). Item 9 of the statement shows how it was applied to the custody fault: that fault was not a clause-3 finding because it "was found before issuance, it blocks issuance and cannot pass silently, and its repair changes no capture and no number". F1 measured against the same three points:

- Found before issuance: yes.
- Changes no capture and no number: yes. No repair is made in this transaction (§4).
- Cannot pass silently: **no**. F1 did pass silently through the packet and the cross-family re-derivation. It was found only because the gate re-ran the estimator from raw bytes.

The third point does not make F1 a defect in a number, by §3.2. It is the reason the disclosures are mandatory and the reason §5 imposes a hold. Whether clause 3 reaches a registered parameter that has outgrown its sizing is the owner's to say. My ruling is that it does not. The owner may overrule in writing under item 10, and such a ruling, like this one, is recorded as made after the outcome was known.

### 3.5 The sentence the issuing transaction's gate must read

> **F1 is not a defect in the code that derives the member list, the statistics, or S, C and the level screen, within the meaning of statement item 7(b), and it is not a ground to reject this candidate.** The 165,000-cell cap is a stop rule that was registered on 2026-08-15, frozen at its value on 2026-08-18 and pinned by file digest in the registration sealed on 2026-09-25; on 2026-09-27 it behaved exactly as registered; and it enters no number, because a capture that finishes gives the same B to the last digit whether the cap is 165,000, 206,000 or 5,000,000 cells. A gate that nevertheless rejects the candidate on F1 is invoking item 7(b), and item 4's consequences (a) to (d) follow. F1 is never a ground to re-prepare the candidate with a different cap or a different member list.

## 4. SF-2 — must the issuing transaction keep the four digests, and exclude any estimator change? Yes to both.

**Why.** The pin in a calibration file means one thing: this code produced these values. The 12 member B values were produced on 2026-09-27 by the four files at the digests in §2. If the transaction issued with any other digest, the pin would name code that never ran on the members, and a reader could no longer reproduce a member's B from the pinned code. The registration voids itself on an estimator-code change mid-campaign (lines 136–137), and the campaign is not over until the calibration is issued. The statement requires the four files byte-identical in every cure and repair (items 5, 6(c), 6(d) R2).

**The apparent conflict with D-138.** D-138 says any change to the four files "lands only inside the ONE atomic successor-family re-freeze", and its inheritance corollary says later work on the same files "RIDES THE SAME BRANCH". Read quickly, that invites folding the waiting branches, or a cap re-size, into this transaction. It does not require it. D-138 says where an estimator change may land. It does not say every issuing transaction must carry one. The four waiting branches stay staged for a later transaction.

**Binding text.**

> B1. The tree from which the calibration is issued holds the four estimator files at exactly these sha256 digests: `joulewise/powermetrics_fiducial.py` `386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92`; `joulewise/uncertainty_evidence.py` `b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8`; `joulewise/adapters/powermetrics.py` `70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4`; `joulewise/reduce.py` `7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc`. The four digests are computed and recorded immediately before the issue and again on the merged result. The issued file's `estimator_code_sha256` block equals the candidate's character for character.
>
> B2. The transaction contains no change to any of the four files. It does not change `DETECTION_PROJECTION_CELL_BUDGET`. It merges none of `feat/2026-09-04-instrument-path-pin` (`bda7ffe0`), `feat/2026-09-04-raw-capture-digest` (`aeea07b6`), `feat/2026-09-24-acc-25g83-v4-rev4` (`ea10e3c8`), `impl/p2041` (`5135c1d2`), and no other branch whose difference from main touches one of the four files.
>
> B3. If B1 or B2 cannot be met, the transaction does not issue and the matter is held for a ruling. It is not cured by re-preparing the candidate under different code.
>
> B4. A change to the cap, or any other change to the four files, is a separate and later transaction under D-138. It makes the calibration issued here stale and forces a re-issue. Before such a change is staged, the council rules in writing on two things: which captures the re-issue may contain, and the rule by which the new cap value is chosen. That rule uses cell counts and frame lengths only, and no B value. D-138's inheritance corollary applies to that later transaction, not to this one.

## 5. SF-3 — is the cap a risk to the truth of later measurements? Yes. It is mandatory to resolve or measure it before claim-bearing windows.

### 5.1 The mechanism, step by step

1. The sampler delivers frames of 127.6–130.2 ms. The length varies from capture to capture with the state of the machine; the registration says "launch context sets the sampler cadence".
2. Longer frames cost the estimator more cells: about 7,500 per millisecond, r = +0.82 (§2).
3. The cap sits inside the range of need. Of the 9 captures in the longer-cadence group (near 129.7 ms) 6 were stopped. Of the 11 others, 2 were. One capture, at 128.94 ms, lies between the groups; counted with the longer group the split is 7 of 10 against 1 of 10. A one-sided exact test gives p = 0.040 for the first split and 0.010 for the second.
4. In a measurement window, a stopped calibration capture abandons its bracket (decision log, D-078 amendment of 2026-08-15: "for an invalid pre slot the terminal bracket-abort receipt carries the exact registered reason `detection_nonconvergent`").
5. So the measurements that survive are mostly those taken while the machine was delivering shorter frames.
6. If whatever lengthens the frames (scheduler load, heat, display activity) also changes the energy the workload draws, the surviving measurements are a filtered sample of machine states. The reported energy would then be the energy in the short-frame state, presented as the energy of the machine.

Step 6 is an "if". Nobody has measured it, and W1 and W2 cannot (§2). An unmeasured selection on machine state bears directly on whether a reported energy is true. Under the owner's directive that makes it mandatory, not advisory. The ruling's §8 treats the cap as a throughput cost only. The refuter is right that this understates it.

### 5.2 What it does not touch

It does not touch this issuance. The calibration's numbers are correct for the registered corpus, and the ruling measured that the filter did not act on B. There is also a consistency worth stating: while the cap stays at 165,000, the captures that pass it in a measurement window are filtered exactly as the 12 members were, so the calibration describes the population it will be applied to. That stops being true the day the cap changes, which is one reason B4 sends the re-issue question to the council first.

### 5.3 What must be true before a claim-bearing window is armed at 25G83

> H1. **Hold.** No claim-bearing window is armed at 25G83 until a written ruling closes the cap-and-cadence question by route R or route M below. The hold is written into the issuing transaction's record and into the arm material of every 25G83 window. Windows that carry no claim may run, and are the way to gather the evidence.
>
> H2. **Route R: remove the filter.** The cap is re-sized in a later transaction under B4 so that healthy captures at this epoch's cadence do not reach it. The sizing rule is written before the new value is computed, states the range of frame lengths it covers, and uses cell counts and frame lengths only. It is then shown to work: in at least 24 captures taken under the new cap in windows that carry no claim, none stops on the cap.
>
> H3. **Route M: keep the cap and measure the filter.** Before the window, a registered plan fixes all of the following. (i) Every bracket attempted is recorded, abandoned ones included, with the reason, the median frame length of its calibration captures, and the cells used. (ii) The workload's energy is computed for abandoned brackets too, as a diagnostic. (iii) The report states how many brackets were attempted, completed and abandoned on the cap, and the difference in energy and in frame length between completed and abandoned brackets, with its uncertainty. (iv) If that difference is larger than the uncertainty the claim carries, the claim is reported as holding for the short-frame state only.
>
> H4. **Clock steps.** The three captures lost to a wall-clock step (52.0, 5.8 and 35.9 ms) are the same kind of filter: a machine event decides which measurements survive. Under either route, abandoned brackets are recorded by cause, and the cause of the steps is sought before claim-bearing windows run.

I recommend route R. Route M leaves about a third of calibration captures stopped, so few brackets complete, and it leaves the claim resting on a comparison with diagnostics.

A worked example of why the sizing rule in H2 must state its frame-length range, offered as illustration and not as a ruling. The August rule was "largest need seen, plus 20.3 %". Applied to this epoch's largest need, 170,965 cells, it gives about 205,600. But the registration's own table records launch-context sessions with a median frame of 131.6 ms and a 95th percentile of 134.8 ms. The straight line of §2, carried beyond the data it was fitted to, puts the need near 181,000 cells at 131.6 ms and 205,000 at 134.8 ms, before allowing the 11,700 cells by which single captures exceed the line. A cap of 205,600 could be inside the workload again. The extrapolation is unverified; it shows only that a cap sized from one day's counts repeats the August mistake.

## 6. N-1 to N-4

| Item | Ruling | Reason |
|---|---|---|
| **N-1** | **Adopted in part.** | *Route (c) is rejected.* The registration's route (c) covers "a recorded operator or system event [that] interrupted the window". No window was interrupted: both ran all 12 slots. Resting the three clock-step exclusions on (c) would stretch its words, and the ruling's five reasons do not need it. *The Revision 5 citation is adopted as consistent, not as independent proof.* Revision 5 lists "anchor feasibility" among the physical barriers. The 5 ms check on wall-clock movement runs inside the same clock-alignment routine as the fit (`joulewise/uncertainty_evidence.py:1110–1125`, ahead of the fit's own refusal at line 1232), so a capture that fails it has failed at that barrier. But the phrase most naturally names the fit itself, which is clause (a)'s own class, so it cannot carry the reading alone. |
| **N-2** | **Adopted.** | Confirmed at `2026-09-27-activation-3ba66eeb/00-activation-record.md` line 74: "d11's +9 mAh gauge re-estimate (0 mA)" was already in the notices. The ruling's §5 is corrected: of the two gauge observations it calls new, only the reading 12 mAh lower at W2's start than at W1's end is new. |
| **N-3** | **Adopted.** | "One bracket in four" is 0.5 × 0.5 and assumes the two captures of a bracket fail independently at the overall 50 % rate. It is an illustration. For scale: among the 22 pairs of neighbouring slots in W1 and W2, 6 have both captures valid (27 %). Neighbouring slots are 600 s apart and are not brackets, so this too is only indicative. With the cap as the only cause (8 of 24 stopped) the same arithmetic gives 0.67 × 0.67 = 44 %. |
| **N-4** | **Adopted, against D4 and not D6.** | The diagnostic values are disclosed in D4; D6 is known conditions. The eight values were computed twice, independently, by the judge and by the refuter, and agree to every printed digit. I computed one of them a third time (w2-d02). A successor registration's list of disclosed design inputs names all three seats. |

## 7. Addendum A1 — the text to append to the ruling

> ## Addendum A1 (2026-09-27, cold addendum SCI-25G83-CANDIDATE-01-A1)
>
> This addendum was written after every B value of W1 and W2 was known. The verdict, the member list, the statistics and the three operative numbers are unchanged. Full reasons and executed evidence: `31-addendum-ruling.md`.
>
> **A1.1 Classification of F1 (adds to §2.2, §5 and D2).** F1 is not a defect in the code that derives the member list, the statistics, or S, C and the level screen, within the meaning of statement item 7(b), and it is not a ground to reject this candidate. The 165,000-cell cap is a stop rule that was registered on 2026-08-15, frozen at its value on 2026-08-18 and pinned by file digest in the registration sealed on 2026-09-25; on 2026-09-27 it behaved exactly as registered; and it enters no number, because a capture that finishes gives the same B to the last digit whether the cap is 165,000, 206,000 or 5,000,000 cells. A gate that nevertheless rejects the candidate on F1 is invoking item 7(b), and item 4's consequences (a) to (d) follow. F1 is never a ground to re-prepare the candidate with a different cap or a different member list. In §5, "sign of an artifact" is read as: a registered parameter whose sizing assumption, frames of about 120 ms, no longer holds. The owner may overrule this classification in writing under statement item 10.
>
> **A1.2 Binding on the issuing transaction (replaces the first recommendation of §8 so far as it concerns this transaction).**
> B1. The tree from which the calibration is issued holds the four estimator files at exactly these sha256 digests: `joulewise/powermetrics_fiducial.py` `386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92`; `joulewise/uncertainty_evidence.py` `b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8`; `joulewise/adapters/powermetrics.py` `70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4`; `joulewise/reduce.py` `7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc`. The four digests are computed and recorded immediately before the issue and again on the merged result. The issued file's `estimator_code_sha256` block equals the candidate's character for character.
> B2. The transaction contains no change to any of the four files. It does not change `DETECTION_PROJECTION_CELL_BUDGET`. It merges none of `feat/2026-09-04-instrument-path-pin` (`bda7ffe0`), `feat/2026-09-04-raw-capture-digest` (`aeea07b6`), `feat/2026-09-24-acc-25g83-v4-rev4` (`ea10e3c8`), `impl/p2041` (`5135c1d2`), and no other branch whose difference from main touches one of the four files.
> B3. If B1 or B2 cannot be met, the transaction does not issue and the matter is held for a ruling. It is not cured by re-preparing the candidate under different code.
> B4. A change to the cap, or any other change to the four files, is a separate and later transaction under D-138. It makes the calibration issued here stale and forces a re-issue. Before such a change is staged, the council rules in writing on which captures the re-issue may contain and on the rule by which the new cap value is chosen. That rule uses cell counts and frame lengths only, and no B value. D-138's inheritance corollary applies to that later transaction, not to this one.
>
> **A1.3 Hold on claim-bearing windows (adds disclosure D7; replaces "The cap will refuse about a third…" in §8).** D7: the cap stops a capture according to how much work the estimator needs, and that work rises with the length of the sampler's frames (r = +0.82, about 7,500 cells per millisecond). In a measurement window a stopped calibration capture abandons its bracket, so the measurements that survive are mostly those taken while the machine delivered shorter frames. Whether the workload's energy differs between those machine states has not been measured, and W1 and W2 cannot measure it. This bears on whether a reported energy is true.
> H1. No claim-bearing window is armed at 25G83 until a written ruling closes this question by route R or route M. The hold is written into the issuing transaction's record and into the arm material of every 25G83 window. Windows that carry no claim may run.
> H2. Route R: the cap is re-sized in a later transaction under B4, by a rule written before the new value is computed, which states the range of frame lengths it covers and uses cell counts and frame lengths only; and in at least 24 captures taken under the new cap in windows that carry no claim, none stops on the cap.
> H3. Route M: the cap stays, and a plan registered before the window fixes that (i) every bracket attempted is recorded, abandoned ones included, with the reason, the median frame length of its calibration captures and the cells used; (ii) the workload's energy is computed for abandoned brackets too, as a diagnostic; (iii) the report states how many brackets were attempted, completed and abandoned on the cap, and the difference in energy and in frame length between completed and abandoned brackets, with its uncertainty; (iv) if that difference is larger than the uncertainty the claim carries, the claim is reported as holding for the short-frame state only.
> H4. The three captures lost to a wall-clock step are the same kind of filter. Under either route abandoned brackets are recorded by cause, and the cause of the steps is sought before claim-bearing windows run.
> This hold is not a condition on the issuance.
>
> **A1.4 Corrections.**
> (a) §2.4: Revision 5's list of physical barriers includes "anchor feasibility", and the 5 ms check on wall-clock movement runs inside the same clock-alignment routine as the fit. This is consistent with the structural reading and is not relied on as independent proof. Route (c) of the registration is not relied on: no window was interrupted.
> (b) §5, battery gauge: the +9 mAh step inside W1 slot d11 had already been disclosed (activation 3ba66eeb, item S4). Of the two observations §5 calls new, only the reading 12 mAh lower at W2's start than at W1's end is new.
> (c) §8: "roughly one bracket in four" assumes the two captures of a bracket fail independently at the overall 50 % rate. It is an illustration, not an estimate.
> (d) D4: the eight diagnostic B values were computed independently by the judge and by the paired refuter and agree to every printed digit; the addendum judge recomputed one (w2-d02). A successor registration's list of disclosed design inputs names all three seats.
> (e) §5, "Left unchecked": the second seat's replication of §2.3 is now EXECUTED, by the paired refuter (its §A1.3).

## 8. Left unchecked, stated plainly

- NOT EXECUTED: reading directive #416. §3.4 rests on the statement's quotation of it.
- NOT EXECUTED: the estimator at three cap values on the other 10 members. I ran 2; the ruling and the refuter each report all 12 with the cap lifted.
- NOT EXECUTED: a review of what the four waiting branches change. I established only that each touches a pinned file.
- NOT ESTABLISHABLE from W1 and W2: whether workload energy depends on cadence.
- UNVERIFIED: the cell needs at 131.6 ms and 134.8 ms in §5.3. They extend a straight line beyond its data.
- NOT EXECUTED: whether the conditions of the custody-repair and predecessor-path rulings were discharged. That remains with the issuing transaction's gate, as the ruling said.

## Summary for the owner

1. The verdict stands and nothing in the calibration changes: the 165,000-cell cap is a rule that was registered and frozen before the captures and changes no number, so it is not a code defect under item 7(b), and the 8 captures it stopped can never be added to this corpus; you may overrule this reading in writing.
2. The issuing transaction must issue with the four estimator files byte-for-byte as they ran on 2026-09-27 and must merge none of the four waiting branches and no cap change; re-sizing the cap is a separate later step, after the council rules on what a re-issue may contain.
3. No claim-bearing measurement window may be armed at 25G83 until the cap is either re-sized and shown to stop no healthy capture, or kept under a registered plan that measures whether it filters measurements by machine state; this is a hold on later windows, not on this issuance.
