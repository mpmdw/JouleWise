RULING: RATIFY-AMENDED

# Cold gate REV5-REFUSAL-BRANCH-01: what follows if the issuance step refuses after W2

Judge: Fable 5.1, one non-interactive session, 2026-09-27, 12:10 to 12:20 PDT.
No subagents, no background tasks. Scratch files are only under `/tmp/cg-refusal-77b1bee2/`. That directory also holds `judge.out`, which no command of mine created; I take it to be the launcher's capture of this session and left it alone.

The three proposed points (a), (b) and (c) are each consistent with the sealed registration and are ratified in substance. They are amended because, as worded, they leave five gaps (§4). The text to record is in §5. It replaces the proposed statement.

## 0. Contamination disclosure

- **Injected before my first turn, not by my choice:** the session harness placed three texts in my context: the owner's global instruction file, this repository's `CLAUDE.md`, and the one-line index of the memory store. The index carries one-line summaries of past rulings and checkpoints, including lines on W1 and W2 being armed and on the council rule. I opened no memory file behind that index.
- **Not read:** `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md`, any `CLAUDE*.md` file on disk, any memory file, any skill file, the activation record `00-activation-record.md`.
- **How I limited the effect:** every fact this ruling relies on was read in this session from the registration, the issuing tool's code, the decision log, GitHub or Gmail, and is listed in §1.
- **Measured values of W1 and W2:** I opened no timing value, no ledger row and no capture evidence file. (The timing value is called B in this ruling: each capture's stored bound, in seconds, on how far its clock alignment can be off, held in the field `b_fiducial_s`.) My one run against a measurement root was the count-only dry run, which prints counts and states and no measured value.
- **Values I did see, and why they do not bear on the outcome:**
  - The eleven B values of the 2026-09-19 captures. They are printed in the registration itself (Revision 5, "Disclosed design inputs") and again in the decision log. They are not W1 or W2 values.
  - W2's frame-cadence figures (median 128.5 ms, worst 141.4 ms), which appear in the harvest email I read to verify the proposed statement. The registration allows this figure to be reported before any B value is read ("The dry run may report valid count and 'median native frame length'").
  - The battery capacity figures quoted in the final-pass ruling I was charged to read.
- **Read as charged material, not trusted:** the final-pass ruling (`20-harvest-gate/22-fable-finalpass-ruling.md`), the charge file, the operator's dry-run output `10-w2-harvest/check-w1w2.out`, and the four emails of Gmail thread `1a0e42883e977e7c`.

## 1. Executed evidence (this session)

| # | Check | How | Result |
|---|---|---|---|
| E1 | Working tree | `git rev-parse HEAD`, `git status --short` | `670756f3fbb366d9c40a7a128766c9afc5d331cf`, clean. |
| E2 | Registration digest | `shasum -a 256` on the registration file | `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`, as charged. 664 lines. The copy in the W2 measurement root has the same digest. |
| E3 | Registration text | read lines 1–664 in full | Revision 1 "Stopping." at :173–177; Revision 5 at :600–646; amendment A-R5b at :648–664. Quotations below are from this read. |
| E4 | Issuing tool, refusal paths | read `scripts/issue_calibration_acceptance_generation.py` :1025–1257, :1260–1351, :1650–2009, :2100–2154, :2299–2488; listed all refusal sites | The tool's order of work and its refusal texts are in §4.2. Floor constant 12 (:508). Its sha256 in my tree equals the copy in the W2 measurement root (`ceaf3807…7105`). |
| E5 | Code against text, the four thresholds | read :1851–1859, :2129–2141 | Refuses when a member's B is strictly above 0.25 s; marks `excursion_limited` when two or more members are strictly above 0.075 s; records `zero_headroom` when C equals S; refuses when retained n is below 12. Each matches the registration's wording. |
| E6 | Count-only dry run, W1 + W2 | from the W2 measurement root: `check --session-ids <W1> --session-ids <W2> --preregistration … --preregistration-sha256 81b65f08…` | rc = 0. Registration section identical to the operator's output: both windows `battery=pass recorded=pass`, `declared=12 filled=12 valid=6 excluded=none`; `prefix pending or unresolved rows: 0`; `registration admissible for prepare-candidate: yes`. One difference outside that section: see N1. |
| E7 | Nothing modified by E6 | sha256 of four files before and after; `git status` and `HEAD` of the measurement root before and after | identical; root clean at `722f7bd1`. Run with `PYTHONDONTWRITEBYTECODE=1`. |
| E8 | Value-free pre-check | `build_quantile_proof(11)` imported from my tree | builds without refusal (11 = n − 1 for n = 12). |
| E9 | Who may decide registration text | read `docs/decision_log.md` :12170–12225 | Decision D-184 and its addendum; the disposition entry for the 2026-09-19 captures; binding reading A-R5b-1. Quoted in §3 and §6. |
| E10 | The disposition registry | parsed `configs/calibration/observation_dispositions.json`, keys only | 11 rows, one decision id, one mechanism string, keys `content_id`, `disposing_decision_id`, `mechanism`. The file holds no B value. The issuer pins the registry's digest, the decision id and the mechanism string as constants (:509–515, :1260–1292). |
| E11 | Directive #416 | `gh issue view 416` | clause 3 as quoted in §4.5. |
| E12 | The statement as sent | Gmail thread `1a0e42883e977e7c`, message `1a0e446264f8b791`, read in full | sent 2026-09-27 19:09:57 UTC (12:09:57 PDT). Points a), b), c) match the charge in substance. No reply from the owner existed at 12:13 PDT. |
| E13 | What follows the issuance step | read `docs/phase_2/derivation_night_runbook.md` :3040–3160 | two further steps exist after a candidate is written: a cold science gate and the issuing transaction (§4.4 below). |

**NOT EXECUTED**
- `prepare-candidate`: not run. A reviewer must not run it.
- Any read of W1's or W2's ledger rows, evidence files or custody files.
- The full test suite.
- The decision-log entries for D-125, D-126, D-138 and D-182 in full. I read D-184, the 2026-09-25 addenda and A-R5b-1 only.
- The council ruling that authorised Revision 5 (`…05-coldgate-packet-acc2/30-addendum/21-…ruling.md`). I saw single lines of it and of two exhibits through a search, and relied on none except the one marked in §2.
- The meaning of "estimator lane" and "phase-split claim" (see N2): not traced to a definition.
- A paired refuter for this ruling: none was convened by me. My protocol forbids subagents.
- A second check of the owner's inbox after 12:13 PDT.

## 2. Terms used in this ruling

Each term is given here before it is used.

- **Epoch.** The six-field identity the calibration is bound to. Here: macOS build 25G83 on this machine, under the registered sampler and protocol.
- **Capture.** One 59-pulse calibration measurement. **Window.** One scheduled run of 12 declared captures. W1 and W2 are the two windows of this epoch, 24 captures in all.
- **Valid.** A capture's disposition in the ledger when every protocol check passed. The alternative here is "ordinary-invalid". W1 and W2 each have 6 valid and 6 ordinary-invalid.
- **Retained** (also "a member"). A valid capture whose stored clock alignment also resolves when the issuing tool reads it back. The 12 valid captures are expected to be the 12 retained ones, because the dry run reports `excluded=none`.
- **B.** Defined in §0.
- **The registration.** The file at digest `81b65f08…ddf1`. Revision 5 and amendment A-R5b are the parts in force for this epoch.
- **The issuance step.** The command `prepare-candidate`. It reads the members' B values, and then either writes one candidate calibration file, marked not issued, or prints `REFUSED: <reason>`, writes nothing and exits with code 3 (:1650–1661, and the class note at :1026).
- **Refusal.** The second of those two results.
- **The floor.** The registration's minimum: "Retained n ≥ 12 is the issuance floor".
- **Plateau inset.** A fixed 0.25 s margin belonging to the pulse protocol, named `PLATEAU_INSET_S` in code. The registration says only: "0.25 s is that protocol's plateau inset". The physical reason a larger B refuses, as one council exhibit puts it, is that a timing shift that large "crosses the whole inset". I did not verify that reason against the protocol code.
- **Top-up.** Adding captures to a sample after its size or its values are known.
- **Successor registration.** A new registration text for the same epoch, written after this one has ended.
- **The council.** The four-model review body defined by decision D-184 (quoted in §3.3).
- **The owner.** Ed.

## 3. Ruling 1: are (a), (b) and (c) consistent with the sealed text?

### 3.1 Point (a): on refusal, derivation under Revision 5 ends and there is no further capture under it

**Consistent. The text supports no other answer.**

Text relied on (Revision 5, "Sample, stops and blindness"):
- "W3 is permitted only if the count-only dry run after W2 shows fewer than 12 valid, and is another 12-slot window."
- "No B-based exclusion or outcome-driven top-up is permitted."
- "Rules are fixed here before capture."

The dry run after W2 shows 6 + 6 = 12 valid (E6). Twelve is not fewer than twelve, so the third window is closed. The issuing tool enforces the same reading (:1831–1838).

The only other route to an extra window is the battery replacement of amendment A-R5b. It opens only for a window whose battery verdict is not `pass`: "A window with either verdict is replaced by one fresh window". Both recorded verdicts are `pass` (E6). The amendment ends: "No other top-up is permitted."

Revision 1's "Stopping." carries the same rule for its own design: "No top-ups, retries, early stops, or outcome-driven extra nights."

**Where (a) needs amending.** The word "refusal" is not scoped. Read literally, a mistyped argument would end the epoch, because the tool prints `REFUSED` for that too. Read loosely, anyone could call a refusal "curable" after seeing it. §4.2 closes both.

### 3.2 Point (b): the 24 captures become disclosed diagnostics and are never members of a later registration

**Consistent. The text is silent on this exact case, and the proposed fill is outcome-independent and the most conservative one available.**

The text does not say what becomes of W1 and W2 after a refusal. Three passages show how the registration treats captures that are not members, and all point the same way:

- Revision 1, "Membership.": "Every member carries the target epoch and belongs to a session of this registration; a valid same-epoch observation outside this registration refuses issuance rather than being absorbed." A later registration has its own sessions. W1 and W2 would be outside them.
- Revision 5, "Disclosed design inputs", on the eleven 2026-09-19 captures: "They are never members of the new registration."
- Amendment A-R5b, "Consequences.", on a window set aside for battery reasons: "A window with either verdict is retained and disclosed. None of its slots is a member".

**Why it is outcome-independent.** It applies to all 24 captures, whatever their values, and it is triggered by the fact of refusal, not by which capture caused it.

**Why it is the most conservative fill.** The alternatives are:

| Alternative | What it would allow | Why it is worse |
|---|---|---|
| Keep the 12 and add new captures | a larger sample built after a refusal | this is a top-up, which the text forbids by name |
| Keep the 12 under a changed rule (a higher limit, or one capture dropped) | the same data passing a rule written after the data was seen | the rule becomes a function of the outcome |
| Set all 24 aside (the proposal) | nothing | costs about one day of capture and no science |

**The tool already enforces (b).** A successor's issuance would find the 12 valid W1/W2 rows in the ledger, carrying the same epoch and belonging to none of its sessions, and would refuse with "valid same-epoch observations outside this registration" (:1839–1850) until those rows are formally set aside in the disposition registry. They cannot be absorbed by accident.

**Two corrections to (b)'s wording.**
1. "This is the same treatment the eleven 2026-09-19 captures received" is true of the result and not of the reason. The eleven were set aside for a named instrument condition: "captured under the default-ProcessType launch context (utility QoS, timer coalescing, median ≈ 248 ms)". W1 and W2 would be set aside for a different reason: they belong to a registration that ended in refusal. The record must name that reason and not borrow the other.
2. The existing registry accepts only the one decision id and the one reason string of the eleven, both pinned as constants in the issuer (E10). Setting W1 and W2 aside therefore needs a new decision-log entry and a reviewed code change. (b) should say so, so that nobody later treats the missing registry rows as optional.

### 3.3 Point (c): a successor is authorized by the owner or the council, and sealed before its first capture

**Consistent.**

- Revision 1, "Stopping.": "any further capture is Ed's written ruling, not this registration's."
- Revision 5 amends that paragraph without restating the sentence. For its own two stops it says: "stop: no W2, return to council." Amendment A-R5b says the same for its stop: "stops the epoch and returns it to council."
- Decision D-184, addendum (owner, 2026-09-24): "The four-model council decides experiment-design changes (block-two redesign, shakedown design, registration text, analysis-plan adoption) and Ed receives an after-the-fact summary by email, not a question. Only hardware, sudo, a notice NO, and publishing claims remain Ed's."
- Revision 5 itself was authorized this way. Its authority line reads: "council ACCEPTANCE-25G83-02 under D-184 **Addendum**".
- Sealing before capture is the registration's founding rule: "every rule that could otherwise be chosen after seeing values is fixed here first."

So "the owner or the council" is the correct pair. Revision 1's sentence is not lost: the owner delegated registration text to the council on 2026-09-24, and kept the right to overrule.

**Where (c) needs amending.**
1. It should say that the operator who runs the issuance step (the magistrate) cannot authorize a successor alone.
2. A successor written after a refusal is written by people who know something about the outcome: at the least, which capture exceeded 0.25 s. The registration's own practice for that situation is disclosure. Revision 5 lists the eleven values it had seen, and the decision-log entry that set them aside says it "is authored after the values were seen and discloses that timing". The successor must do the same for W1 and W2.

## 4. Ruling 2: what is missing

### 4.1 The map of outcomes

The issuance step, and the two steps after it, can end in six ways. The proposed statement covers one of them.

```
issuance step runs on W1 + W2 (12 valid captures)
 │
 ├─ prints REFUSED
 │    ├─ cause on the closed "curable" list ........ CURE, then run again      [statement item 5]
 │    ├─ cause on the "terminal" list .............. EPOCH ENDS under Rev. 5   [item 4]  ← the only case (a)–(c) covered
 │    └─ any other cause, or a crash ............... HELD for a ruling         [item 6]
 │
 └─ writes a candidate file (not yet issued)
      ├─ with or without the marks
      │  excursion_limited / zero_headroom ......... ISSUANCE PROCEEDS         [item 3]
      └─ then the cold science gate and the
         issuing transaction
           ├─ accept ............................... ISSUED
           ├─ reject, numbers unchanged by the fix . CURE, resubmit            [item 7]
           └─ reject, numbers would change ......... EPOCH ENDS under Rev. 5   [item 7]
```

Named elements: "issuance step", "candidate file", "curable", "terminal" and "held" are defined in §2 and §4.2; "marks" in §4.3; "cold science gate" and "issuing transaction" in §4.4.

### 4.2 Refusal is not one thing: three classes, fixed by cause

**The forcing problem.** The tool prints the same word, `REFUSED`, for a mistyped argument and for a capture above 0.25 s. If the class of a refusal is judged after it appears, the judgment can lean on the outcome. So the classes are fixed now, by cause, as closed lists.

**What makes this safe.** The tool does its work in a fixed order (E4). Everything up to line 1826 is decided from arguments, file digests, ledger structure and battery records. Members' evidence is first opened at line 1827. On any refusal the tool prints the reason and writes nothing. So the only thing a refusal reveals is its reason text.

| Class | Causes | What may be done |
|---|---|---|
| **Curable** | Wrong or missing argument; sessions named out of order; wrong checkout, interpreter or file path; a custody file missing or not matching the digest its ledger row recorded at capture | Correct the command, or restore the bytes exactly from the harvest archive. Then run again. |
| **Terminal** | A member's B above 0.25 s; fewer than 12 retained; a clock alignment unresolved for an unregistered reason; stored B text differing from the ledger row; the registration void; an undisposed same-epoch capture outside the registration; a battery record that still disagrees after an exact restore | The consequences of (a), (b) and (c). |
| **Held** | Anything not on the two lists; any crash; any refusal removable only by changing code | Stop. No re-run, no capture. The owner or a fresh cold gate rules on the refusal text. |

Worked examples with the tool's real texts:
- `REFUSED: Revision 5 sessions must be named in W1/W2/W3 ledger order` is curable. Re-run with W1 named first. No value was read.
- `REFUSED: member <id>: instrument_evidence.json does not match the ledger row` is curable by exact restore only. The ledger row's digest was fixed at capture, so a file that hashes to it cannot have been altered. This is the cure the binding reading A-R5b-1 already names: "Restoring the custody bytes byte-exact from the harvest archive, so that the recomputation agrees, is the only cure."
- `REFUSED: member B exceeds PLATEAU_INSET_S = 0.25 s: <id>` is terminal. With 12 retained and a floor of 12, removing even one capture would leave 11, below the floor; and the text says "No B value is excluded."
- `REFUSED: member <id>: primary b_fiducial_s does not match the ledger row's exact bound lexeme` is terminal. The final pass listed it as "owner ruling". It is an integrity failure inside one member. The member cannot be dropped, and 11 is below the floor.

**Why "held" exists.** A tool defect is possible. Treating every defect as terminal would discard a day of captures for a software fault. Letting the operator repair the tool and re-run would let a repair be shaped by what the refusal revealed. The held class puts a second party between the refusal and the repair.

### 4.3 The two marks do not need a new consequence, but they need one sentence

The registration already fixes both:
- "Count retained B > 0.075 s. Two or more mark the candidate `excursion_limited`, requiring the estimator lane before a phase-split claim."
- "If C = S, record `zero_headroom` and proceed with issuance; drift above S is refused by the operative bracket."

(S is the screen on how far two calibration readings around a measurement may differ. C is the ceiling on the drift a measurement may budget for. Both are computed from the corpus by the registered formulas.)

What is missing is the converse. Once the candidate exists, its values are known. A person who dislikes them could decline to issue and start over, which is selection in the other direction. The statement must say that no mark, no diagnostic and no value is a ground to withhold issuance, exclude a capture or capture again.

### 4.4 A candidate can be written and still not be issued

Two steps follow a written candidate (E13):
- the **cold science gate**: "a fresh adjudicating seat with no campaign context, ruling on a mechanically assembled packet";
- the **issuing transaction**: "the single reviewed commit that swaps the live acceptance and every pin that names it."

Both see the values. Either can say no. The proposed statement is silent on that. The fill in §5 item 7 uses one mechanical test: would the fix change the member list, the statistics or the three operative numbers? If not, cure and resubmit. If so, the epoch ends under Revision 5, exactly as for a terminal refusal.

### 4.5 Directive #416, clause 3

Clause 3 of the owner's directive reads: "If the audit finds a defect in the calibration derivation path, W1/W2 are re-run before any headline run." Revision 5 has no window left. The two are reconciled by reading "re-run" as "captured again under a successor registration". The statement says so (item 9). The operator has already told the owner of this conflict (E12, point 2). What becomes of an already issued calibration in that case is the audit's question and is not ruled here.

### 4.6 The tool has three escape flags the Revision 5 text does not grant

`--nights-ruling` and `--slot-count-ruling` let a run depart from the registered window count and slot count by naming a written ruling. `--ed-ruling` belongs to the older floor of 19. Revision 5 grants none of them. The runbook already says of the first two: "never to make a shortfall issue." The statement forbids all three for this epoch (item 2).

## 5. Ruling 3: the statement to record

Paste the block below verbatim into the prepare record. It replaces points (a), (b) and (c).

> **Statement REV5-REFUSAL-BRANCH-01.** Fixed before the issuance step first runs on W1 and W2. Ratified by cold gate ruling `40-refusal-branch/21-coldgate-fable-ruling.md`, 2026-09-27.
>
> Words used: **the registration** is `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` at sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`; Revision 5 and amendment A-R5b are the parts in force. **W1** is session `d079-epoch-25g83-derivation-w1-20260927` and **W2** is session `d079-epoch-25g83-derivation-w2-20260927`; together they hold 24 captures, 12 valid and 12 ordinary-invalid. **The issuance step** is the command `prepare-candidate` of `scripts/issue_calibration_acceptance_generation.py`. It either writes one candidate calibration file, marked not issued, or prints `REFUSED: <reason>` and writes nothing. **B** is a capture's stored timing bound in seconds (`b_fiducial_s`). **Retained** means valid in the ledger and resolved on read-back.
>
> 1. **Scope.** This statement grants nothing the registration does not grant. It fixes what follows each possible result of the issuance step, before any B value of W1 or W2 has been read. Its sha256 is committed and sent to the owner by email before the issuance step first runs.
>
> 2. **How the step is run.** The step names W1 and then W2, and no other session. It is given the registration digest above. It is not given `--nights-ruling`, `--slot-count-ruling`, `--ed-ruling` or `--battery-confounded-session-id`. `--minimum-corpus-size` is omitted or is 12. Every run is recorded verbatim in the prepare record, refused runs included: the command, the commit it ran at, the exit code, the full output and the time. No run is left out.
>
> 3. **If a candidate is written.** Issuance proceeds to the cold science gate and the issuing transaction. This holds whether or not the candidate carries either mark the registration defines: `excursion_limited` (two or more retained B above 0.075 s) or `zero_headroom` (the ceiling C equals the screen S). Each mark is recorded and travels with the calibration, with the consequence the registration states for it. No mark, no diagnostic and no value is a ground to withhold issuance, to exclude a capture, to capture again, or to write a new registration.
>
> 4. **Terminal refusal.** A refusal is terminal when its cause is any of these:
>    (i) a member's B is above 0.25 s (`PLATEAU_INSET_S`);
>    (ii) fewer than 12 captures are retained;
>    (iii) a valid capture's stored clock alignment did not resolve for a reason other than `affine_clock_fit_empty`, or was recorded under a method other than anchor-v3;
>    (iv) a member's stored B text differs from its ledger row's;
>    (v) the registration is void (the rows' OS build or sampler digest differs from the registered one), or the rows disagree on the epoch;
>    (vi) a valid capture of this epoch lies outside W1 and W2 and has not been set aside in the disposition registry;
>    (vii) a battery record and its recomputation still disagree after the exact restore of item 5(b).
>    On a terminal refusal, all of the following hold:
>    (a) Derivation under Revision 5 ends for this epoch. There is no further capture under it: no third window, no battery replacement window, no retry and no top-up.
>    (b) Nothing issues from W1 and W2. No capture is dropped, no threshold is moved and no flag is used to make them issue.
>    (c) All 24 captures of W1 and W2 become disclosed diagnostics. None is ever a member of a later registration's corpus, alone or alongside new captures. Their ledger rows and custody bytes are kept unmodified. Their B values may be read after the refusal, to find the cause, and each such read is recorded.
>    (d) The setting-aside is recorded in a new decision-log entry. The entry names its own reason: "member of registration Revision 5, which ended in a terminal refusal; disposed as diagnostic, never a member". It says whether it was written before or after any W1 or W2 value was read. The 12 valid captures' content ids are added to the disposition registry through the ordinary pull-request gate before any successor's issuance step runs.
>
> 5. **Curable refusal.** A refusal is curable only when its cause is on this list, and only by the cure named:
>    (a) a wrong or missing argument, sessions named out of order, or a wrong checkout, interpreter or file path. Cure: correct the command and run again;
>    (b) a custody file that is missing, unreadable or does not match the digest its ledger row recorded at capture. Cure: restore the bytes exactly from the harvest archive, so that they hash to the recorded digest, and run again;
>    (c) a committed input that is not the registered one: the ledger head pin, the predecessor calibration file, a battery verdict record or the disposition registry. Cure: run from a checkout that holds the committed file. No file is edited.
>    A cure never changes the ledger, the registration, a capture's evidence, the issuing tool, or the four estimator-code files. A cure never includes a capture.
>
> 6. **Held refusal.** Any other refusal is held. So is any crash, and any refusal that could be removed only by changing code. Work stops: no re-run and no capture. The output is kept verbatim. The owner, or a fresh cold gate shown the refusal text and the proposed change and no B value, rules whether the change is a tool repair. A tool repair changes none of the registered rules (membership, the floor of 12, the 0.075 s and 0.25 s limits, the formulas for S and C, the quantile bounds), leaves the four estimator-code files byte-identical, and lands through the ordinary pull-request gate. If the ruling is no, or if no ruling is given, the refusal is terminal and item 4 applies. If the held output showed any B value or statistic, the ruling is recorded as made after values were seen.
>
> 7. **Candidate written, then rejected.** When the candidate is written, its sha256 is recorded at once. If the cold science gate or the issuing transaction rejects it:
>    (a) for a reason whose fix leaves the member list, the statistics and the three operative numbers (S, C and the level screen) unchanged, such as an incomplete packet or a wrong identifier, the fix is made and the candidate is resubmitted. A re-prepared candidate must match the first in those fields character for character;
>    (b) for any reason whose fix would change one of those fields, or for a defect found in the derivation path, item 4's consequences (a) to (d) apply.
>
> 8. **Successor registration.** Any further calibration capture for this epoch happens only under a successor registration. A successor is authorized by the owner's written ruling, or by the four-model council under decision D-184's addendum with a cold-gate ruling on its final text, as Revision 5 was. The operator that runs the issuance step cannot authorize one alone. The successor's text is sealed, and its digest is pinned in the arm material, before its first capture. The text states that it was written after Revision 5 ended, names the refusal reason, and lists as disclosed design inputs every W1 and W2 value its authors had seen. The owner receives a summary by email before its first arm notice.
>
> 9. **Directive #416, clause 3.** "W1/W2 are re-run" is read as: captured again under a successor registration, per item 8. No window is added to Revision 5 for an audit finding.
>
> 10. **Override.** The owner may overrule any item in writing. A ruling given before the issuance step first runs is outcome-blind and simply replaces the item. A ruling given after that is recorded as made after the outcome was known, and any text that reports the resulting calibration says so.

## 6. Ruling 4: owner or cold gate

**A cold gate may ratify this statement. The owner's approval is not required for it to take effect.**

Reasons:
- The statement restricts and never permits. Every item either restates the registration or fills a silence with the narrower choice. No one can gain a capture, a member or a threshold through it.
- The owner delegated registration text to the council and kept four matters for himself: "Only hardware, sudo, a notice NO, and publishing claims remain Ed's." (D-184 addendum). This statement is none of the four.
- The owner has the statement and can overrule it (E12).

**What does need the owner:**
1. **Any departure in the permissive direction.** Re-using a W1 or W2 capture as a member, any capture under Revision 5, or a floor below 12. After the issuance step has run, such a ruling is made with the outcome known. It should be the owner's own, in writing, and disclosed (item 10). I would not accept the council for this.
2. **Confirmation of item 9.** It reads the owner's own directive. The reading is the only one the registration allows, so it does not block. A one-word yes from the owner closes it.
3. **Timing of the owner's veto.** The owner's right to overrule is outcome-blind only until the issuance step first runs. If the owner is expected to reply today, waiting costs nothing in science. That is the operator's call. It is not a condition of this ruling.

## 7. Findings

### BLOCKER
None.

### SHOULD-FIX (conditions of this ratification)

- **S1.** Record the §5 block verbatim, commit it, and send its sha256 to the owner by email, all before the issuance step first runs. The email is the copy held outside the machine that fixes the order of events.
- **S2.** Check the owner's replies immediately before the issuance step runs. A reply that overrules any item governs.
- **S3.** Send the owner the amended statement, saying in plain words what changed from the a), b), c) he received: three classes of refusal; the rule for a candidate that is written and then rejected; the ban on the three escape flags; the disclosure duty of a successor.
- **S4.** Correct "the same treatment the eleven 2026-09-19 captures received" wherever it is repeated (§3.2).

### NIT

- **N1.** My dry run (E6) printed `mlx_version … unavailable … MISMATCH` in the desk-watch section, where the operator's output reads `0.31.2 … match`. The cause is my shell's `python3`, which has no MLX installed. The registration section was identical. It is a live example of item 5(a): run the issuance step with the project's own interpreter, and record which one.
- **N2.** The registration uses "estimator lane" and "phase-split claim" in the `excursion_limited` sentence and defines neither. I did not trace them (NOT EXECUTED). The prepare record should state both in plain words before the mark is first reported to the owner.
- **N3.** Times in the charge and the final-pass ruling are approximate. The statement email was sent at 12:09:57 PDT, not "≈12:15". The final-pass file existed by 12:08 PDT though its header says "about 12:00–12:25". Neither affects any ruling here.
- **N4.** The final pass's table lists "Quantile proof for 11 degrees of freedom fails" as a possible cause. I re-ran the pre-check and it builds (E8). Under the statement such a failure would be held (item 6): it is a fault in code and carries no information about the values.
- **N5.** This ruling had no paired refuter. If the operator's practice pairs one with every cold gate, the refuter's target should be §5 items 5, 6 and 7, which are this ruling's additions and not the registration's words.

## 8. Plain summary for the owner

1. Your three points are right and are approved: if issuance refuses because of the measured values, this registration is finished for the epoch, all 24 captures become disclosed diagnostics that can never be reused as sample members, and any new registration needs you or the council and must be sealed before its first capture.
2. Four things were added so that nothing is decided after the values are seen: a fixed list of which refusals can simply be fixed and re-run (typing errors, files restored exactly from the archive) and which end the epoch; a rule for a calibration file that is written and then rejected by review; a rule that no one may decline to issue because they dislike the numbers; and a ban on the tool's three override flags.
3. Nothing needs you today. You can overrule any item, and a reply before the issuance step runs is the clean time to do it; after that, any change would have to be reported as made with the outcome known.
