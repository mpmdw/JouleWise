# Cold gate REV5-REFUSAL-BRANCH-01: paired contract-lens refuter (Opus 5.5)

Seat: Opus 5.5, contract lens, one foreground session, 2026-09-27 ≈12:05–12:35 PDT. It used no subagents, no Codex and no `claude -p`. It modified no file in any repository, measurement root, ledger or custody root. Scratch is `/tmp/opus-refusal-77b1bee2/`, which holds the Section A draft written before the ruling existed. This file is the only thing written outside scratch.

Section A was written independently. It was drafted and saved to scratch at 12:15 PDT. The judge's ruling file first appeared at 12:19 PDT and was read only after that. Section B refutes the ruling.

## Section A: independent answers, written before the judge's ruling was read

### A.0 Contamination disclosure and verification

- **What I read:**
  - the charge;
  - the registration, all 664 lines;
  - the issuer `scripts/issue_calibration_acceptance_generation.py`: the prepare-candidate path :1650–2244, the dry run :183–380, member selection, custody, dispositions, the battery-epoch collector and the CLI;
  - `joulewise/calibration_bracketing.py` :393–530 (the validator's Revision 5 branch);
  - runbook `docs/phase_2/derivation_night_runbook.md` §4.1–§4.2;
  - `docs/decision_log.md`: the D-125 addendum of 2026-09-25, the D-126 addendum, the D-126-disposition-25G83-v3 entry and A-R5b-1;
  - the harvest dry-run output `10-w2-harvest/check-w1w2.out` (counts only);
  - §4 of the final-pass ruling `20-harvest-gate/22-fable-finalpass-ruling.md`.
- **What I did not read:** RUN_STATE, CLAUDE*, AGENTS, memory files or skills. The harness preloaded the owner's global instruction file and the memory index into my context. Neither states any W1 or W2 value.
- **Values:** I opened no W1 or W2 B value, no ledger value field and no capture evidence value. From the W2 ledger I extracted only the `custody_locator` path strings, using `grep -o` with the attempt ids masked.
- **Checkout:** `HEAD` in `/Users/edr/code/JouleWise-wt-refusal-cg-77b1bee2` is `670756f3fbb366d9c40a7a128766c9afc5d331cf`.
- **Registration digest:** `shasum -a 256` on the registration gives `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`, which matches.
- **NOT EXECUTED:** `prepare-candidate` itself. It would evaluate the value-dependent plateau predicate and could print member ids or statistics.

### A.1 Q1: are (a), (b) and (c) consistent with the sealed text?

**(a) "On refusal, derivation under Revision 5 ends; no further capture under it."**

This is consistent. For a value-dependent refusal it is not a fill at all; the text entails it. Revision 5, "Sample, stops and blindness", says:
- "W3 is permitted only if the count-only dry run after W2 shows fewer than 12 valid …"
- "No B-based exclusion or outcome-driven top-up is permitted …"
- "Rules are fixed here before capture."

A-R5b, "Replacement", says: "At most one replacement window is permitted per epoch … No other top-up is permitted."

The dry run shows 6 + 6 = 12 valid, and both battery verdicts are `pass`. So neither the W3 route nor the replacement route is open, and any capture after a refusal would be an outcome-driven top-up. Revision 5 has its own words for a stop: "stop: … return to council" (twice) and, in A-R5b, "stops the epoch and returns it to council". (a) should borrow them.

**Defect in (a): "on refusal" is not scoped.** It covers every `REFUSED:` line the tool can print, including mechanical ones. Read literally, it turns a deterministic, value-blind mechanical refusal into the end of the epoch. That is not hypothetical: A.5 shows that `prepare-candidate`, as the runbook would run it, refuses on the first W1 member with `custody … lies outside the repository`.

**(b) "The 24 captures become disclosed diagnostics, never members of a later registration."**

This is consistent, and it is the most conservative fill. The text fixes the precedent in Revision 5, "Disclosed design inputs": the eleven 2026-09-19 values were "seen before this revision and disposed as diagnostics … They are never members of the new registration." The alternative would let a later registration choose its rules knowing these values and then absorb them. That is the selection Revision 1's preamble forbids: "every rule that could otherwise be chosen after seeing values is fixed here first".

Is (b) itself outcome-dependent? Its trigger is value-dependent for the plateau cause, and every branch rule has that property. Its content is fixed now and does not vary with any value. Two gaps remain:
1. **"Never members" is not "removed from the record."** Revision 1, "Prospective use": a successor's "prior set is the complete history through it, including finalized observations of abort-closed sessions".
2. **(b) is not self-executing.**
   - `_registered_dispositions` (:1260–1292) accepts only decision id `D-126-disposition-25G83-v3-2026-09-25` and the 09-19 mechanism string.
   - The registry digest is pinned at :514.
   - So setting W1 and W2 aside needs a new decision id and a reviewed code change.

**(c) "Successor authorized by the owner or the council, sealed before its first capture."**

"Sealed before first capture" is consistent. My independent reading of "owner or council" was that it is not the most conservative fill. Revision 1's "Stopping." reserves further capture to the owner ("any further capture is Ed's written ruling"). Revision 5 amends that paragraph but does not restate or replace the sentence.

*(Conceded in Section B, B.1: the D-184 addendum, which I had not read at this point, delegates registration text to the council in the owner's own words.)*

### A.2 Q2: what is missing

1. **A closed list of curable, value-blind refusals, with the cure for each.** The cure may not change the inputs: sessions W1 then W2, no ruling flags, floor 12, predecessor r7, digest `81b65f08…`. A cure that needs code goes through the ordinary PR gate as the smallest change. It alters no rule, and it is reviewed without any member value. The precedent is Revision 2, "On PASS", consequence 4: "A refusal in code is not worked around … the smallest change … through the ordinary pull-request gate with its diff reported."
2. **Incurable but value-blind refusals end the epoch like (a).** These are:
   - a lexeme mismatch;
   - "registration is void";
   - an unregistered exclusion mechanism.

   Revision 1 says: "Nothing in this registration … weakens a physics or evidence refusal."
3. **Non-issue after `prepare-candidate` succeeds.** The cold science gate or the D-138 transaction can still refuse, and both see the values. The branch must read "no acceptance issues under Revision 5", with the same carve-out for mechanical cures.
4. **The two labels are issuance, not refusal.** Revision 5 already writes both consequences:
   - "Two or more mark the candidate `excursion_limited`, requiring the estimator lane before a phase-split claim";
   - "If C = S, record `zero_headroom` and proceed with issuance".

   The validator accepts `screen <= drift` on the Revision 5 branch (`calibration_bracketing.py:490`). One sentence should say that neither label triggers a capture, a re-derivation or a refusal.
5. **The owner's override window closes when `prepare-candidate` first runs.** After that, a change is a successor-registration matter.
6. **Disclosure on a final non-issue.** The W1 and W2 values are reported as diagnostics, with the refusal line verbatim. This follows A-R5b's convention: "not read before issuance is decided and are diagnostics afterwards".

### A.3 Q3: my independent draft (superseded by the judge's §5; kept for the record)

1. **Scope and fixing.** The statement is fixed before the first `prepare-candidate` run, and no amendment is accepted after it.
2. **Labels.** Issued with either or both labels means issued, with the consequences Revision 5 states.
3. **Mechanical refusals.** A refusal on the closed list is cured and re-run with the same inputs. A code cure goes through the PR gate, is reviewed blind and alters no rule.
4. **Everything else is final.** This covers a member above 0.25 s, any refusal not on the list, and a cold-science-gate "no". Nothing issues, derivation under Revision 5 ends, and the epoch returns to council.
5. **The captures.** All 24 rows become disclosed diagnostics, reported in full. No W1 or W2 row is ever a member again, and all stay in every later prior set. They are disposed under a new decision id, written now.
6. **Successor.** A successor needs Ed's written ruling (see the concession above). Its text is sealed before its first capture. If its authors have seen the W1 and W2 values, it discloses them as design inputs.

### A.4 Q4: owner or cold gate

A cold gate can ratify, because the statement restricts and licenses nothing. Any grant of capture authority beyond what the sealed text gives needs the owner.

### A.5 The `prepare-candidate` flag set under Revision 5 with W1 + W2, and a certain refusal

**Why the runbook command is wrong here.** Runbook §4.2 is the three-night FAIL route: three session ids, floor 19 and the screen challenge. The code's Revision 5 branch (`revision_five = target_epoch == REVISION_FIVE_EPOCH`) differs in four ways:
- it permits two or three sessions (:1780);
- its floor is 12 (:1766);
- it has no screen-challenge veto (:1863);
- it computes `C = max(C, S)` (:1897).

It also requires the r7 predecessor (:1734).

**Derived command:**

```zsh
cd /Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2
"$PY" scripts/issue_calibration_acceptance_generation.py prepare-candidate \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md \
  --preregistration-sha256 81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1 \
  --registration-session-id d079-epoch-25g83-derivation-w1-20260927 \
  --registration-session-id d079-epoch-25g83-derivation-w2-20260927 \
  --d125-ruling "docs/decision_log.md, D-125 addendum (2026-09-25): Revision 5 screen and ceiling for epoch 25G83/v3 (ACCEPTANCE-25G83-02 §5 R5(i), R9)" \
  --out <new path outside configs/ and outside both custody runs/ trees>
```

**What the command depends on:**
- **Checkout.** It runs from the W2 measurement root, where `HEAD` is `722f7bd1`. Its ledger holds both sessions, and `c5088b87` (the W1 verdict commit) is an ancestor. `--ledger`, `--head-pin`, `--repo-root` and the estimator-code hashes all default to the checkout the script is run from.
- **Session order.** W1 must be named first (:1786–1791).
- **`--d125-ruling`.** The code checks only that it is non-empty (:1667; validator :519). The substantively correct reference is the 2026-09-25 D-125 addendum, which states exactly Revision 5's S and C. The historical D-125 envelope requires strict S < C, which is not the rule being applied.

**Flags to omit:**
- `--minimum-corpus-size`: it defaults to 12, and any other value refuses.
- `--ed-ruling`, `--nights-ruling`, `--slot-count-ruling`.
- `--battery-confounded-session-id`: both verdicts are `pass`, so naming a session fails the exact-set check.
- `--predecessor-acceptance`: the default is r7.
- `--epoch-catalog-id`, `--acceptance-id`.

**Predicted refusal: value-blind and deterministic.**
1. Every W1 and W2 `custody_locator` in the W2 ledger has the form `/Users/edr/night-custody/d079-epoch-25g83-derivation-{w1,w2}-20260927/runs/instrument_validation/<attempt>`.
2. That directory is outside every measurement root, and `/Users/edr/night-custody` is not a git checkout.
3. `_select_members` builds each member's `source_directory` with `_repo_relative_custody(custody_locator, attempt_id, repo_root)` (:896–912, called at :1244).
4. That call raises `member <id>: custody … lies outside the repository, so no repo-relative source_directory exists`.
5. It raises on the first valid W1 member. That is before the plateau check (:1852–1855) and before any statistic, and the message carries a path, not a value.

**Executed check.** I called the issuer's own `_repo_relative_custody` on both custody prefixes against the W2 root. Both calls returned exactly that refusal.

**Why no earlier check catches it.** The count-only dry run does not exercise this path. Its docstring lists "member custody" under "List B, not mirrored".

**Why it cannot be cured by arguments.** `--repo-root` must be a git checkout, because the verdict and pin checks run `git -C`. The final pass (§4.5) and runbook §2.2a(ii) forbid moving the custody root. The cure is therefore a code change. That change needs a design decision on how the issued artifact's members stay verifiable, because `tests/verify_calibration_acceptance_corpus.py` joins `repo_root / source_directory`.

## Section B: refutation of the judge's ruling (`21-coldgate-fable-ruling.md`, RULING: RATIFY-AMENDED)

### B.0 What I checked in the ruling

**Checked and agreed:**
- (a) is entailed by the text (§3.1).
- (b) is outcome-independent and the most conservative fill (§3.2), including both wording corrections.
- There are six terminal outcomes (§4.1).
- Refusals fall into three classes fixed by cause, with a "held" class (§4.2).
- The two labels are issuance, with the converse rule that nobody may decline to issue because of the numbers (§4.3).
- A candidate can be written and then rejected (§4.4).
- The three escape flags are banned (§4.6).
- The override becomes outcome-aware after the first run (item 10).
- A cold gate suffices to ratify (§6).

**Spot-verified against code:**
- floor 12 (:508);
- W3 refusal (:1831–1838);
- A-7 (:1839–1850);
- plateau (:1852–1855);
- registry constants (:509–515);
- the D-184 addendum quote (`docs/decision_log.md:12176`).

### B.1 Concession: (c) "owner or council"

The ruling quotes the D-184 addendum (decision_log :12176): "The four-model council decides experiment-design changes (… registration text …) … Only hardware, sudo, a notice NO, and publishing claims remain Ed's." I verified the quote. My Section A preference for "owner only" rested on Revision 1's sentence alone, and the owner's own later delegation overrides it. Item 8 also requires a cold-gate ruling on a council-authored successor's final text, and §6 point 1 keeps every permissive post-outcome departure with the owner. I withdraw the point.

### B.2 Findings

#### BLOCKER

None against the statement's substance. The statement is safe as written: nothing in it can license a capture, a member or a threshold after the outcome is known.

#### SHOULD-FIX

**SF-1. A refusal the ruling treats as possible is certain, and the ruling does not know it.**

This is operationally the next event.

*What happens:* as A.5 shows, the first `prepare-candidate` run from any existing checkout refuses on W1's first valid member. The message is `member <id>: custody /Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/runs/instrument_validation/<id> lies outside the repository, so no repo-relative source_directory exists`. It comes from `_repo_relative_custody`, :896–912, called at :1244. I executed the issuer's own function on both custody prefixes, and both refuse.

*How the statement classifies it:* the refusal is removable only by changing code, so it is **held** (item 6). But item 5(a) lists "a wrong checkout … or file path" as curable by "correct the command". An operator could plausibly misfile this path-worded refusal there. That invites workarounds that are cures in form only:
- a `git init` above `/Users/edr/night-custody`;
- a copy of the custody into a checkout, which does not even help, because the locator is absolute;
- a symlink.

*Why the default matters:* item 6 ends with "If the ruling is no, **or if no ruling is given**, the refusal is terminal". There is no time bound. A certain, value-blind tool fault could therefore end the epoch through inaction. That is the outcome the ruling's own §4.2 ("Why 'held' exists") says must not follow from a software fault.

*Amend the statement by adding to item 6:*

> "Known before the first run: every W1 and W2 custody path lies outside every git checkout, so the issuing tool refuses `… lies outside the repository, so no repo-relative source_directory exists` before any B value is compared. This refusal is held, not curable under item 5. Its repair is ruled on and landed through the ordinary pull-request gate BEFORE the issuance step first runs. The ruling is made by the owner or a fresh cold gate, shown no B value. The repair must also say how the issued calibration's members stay verifiable (`repo_root / source_directory`). Moving, copying or re-rooting the custody tree, or creating a git repository above it, is never a cure."

*And change* "or if no ruling is given" *to:*

> "A held refusal stays held (no re-run, no capture, no issuance) until it is ruled; it becomes terminal only by a ruling."

**SF-2. Item 2 does not fix the run's inputs completely.**

The charge asked for the flag set, and the ruling gives only prohibitions. Add:
- `--d125-ruling` is fixed now to the 2026-09-25 D-125 addendum ("Revision 5 screen and ceiling for epoch 25G83/v3", ACCEPTANCE-25G83-02 §5 R5(i), R9). The code accepts any non-empty string (:1667), so fixing the text removes a post-outcome choice, and the reference names the rule actually applied.
- `--predecessor-acceptance` is left at its r7 default.
- The run is made from a checkout whose ledger, head pin and battery verdicts are those at `722f7bd1` (the W2 measurement root), with the project's own interpreter. This folds in the ruling's N1.

The full command is in A.5.

**SF-3. "The tool already enforces (b)" (§3.2) is true only against unnamed rows.**

The A-7 check (`_foreign_rows`, :1364–1377) skips every session the caller names as a registration session. `_select_members` (:1203–1257) never consults the disposition registry. So a same-epoch successor that *names* W1 or W2 as one of its sessions is stopped by nothing in code. Registering the dispositions (item 4(d)) does not change that; it only exempts the rows from A-7.

The claim should be corrected. Item 4(d)'s reviewed change should also make the issuer refuse any registration that names a session owning a disposed row. Then (b) is enforced by code, not only by the written rule.

#### NIT

- **N-a. Item 4(vi) makes an undisposed same-epoch row outside W1 and W2 (A-7) terminal.** Revision 1 says only that such a row "refuses issuance rather than being absorbed". The issuer's comment at :1839 says "Either way it is Ed's call". By the ruling's own logic this is held, not terminal: the fault is not W1's or W2's. It is moot today, because the dry run mirrors A-7 and reports none.
- **N-b. Item 3's "no value is a ground … to write a new registration" is broader than the registration.** Revision 5's own `excursion_limited` consequence ("requiring the estimator lane") can lead to a new estimator revision and so to a new registration. The issued artifact also carries re-derivation triggers. Add: "except as the registration's stated consequence for a mark, or the issued calibration's re-derivation triggers, provide."
- **N-c. Item 7(b) ends the epoch for a derivation-path defect found after the candidate exists.** Item 6 lets a tool defect be repaired. The asymmetry is defensible, because the owner's directive #416 clause 3 ("W1/W2 are re-run") already prescribes recapture for a derivation-path defect. The record should cite #416 as the reason, so that 7(b) does not read as inconsistent with item 6.
- **N-d. §4.2 says "Members' evidence is first opened at line 1827."** Battery authentication, which runs before that, already reads each slot's `instrument_evidence.json` bytes (`joulewise/battery_float.py:419`, :514). It prints nothing from them, so the conclusion that only the reason text is revealed still holds.

### B.3 Net

The ratified statement is sound, and it is stricter than both the proposal and my own draft. Items 5 to 7 are good additions, and the concession in B.1 stands. My dissent is limited to adding SF-1 to SF-3 before the statement is recorded. SF-1 matters most: the first run of the issuance step will certainly produce a held refusal, and the owner summary ("Nothing needs you today") should say that a code repair, ruled blind, comes before any candidate.

REFUTER: CONCUR
