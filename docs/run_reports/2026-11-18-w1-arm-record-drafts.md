# W1 arm record drafts · 2026-11-18

Tier 0 documentation for register 32 and 35–36. The Part C handoff
records one smoke on the new W1-line pin. The W1 READY form records the
lead's independent signing and the magistrate's pre-install reads under
W1's registered route. Both files start **DRAFT / INELIGIBLE**.

- [Part C one-shot handoff](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/w1-prearm/ITEM-PART-C-DRAFT.md)
- [First W1 READY record](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/w1-prearm/W1-READY-DRAFT.md)

I used RUN_STATE 346 for the handoff and Check format, 397 and 400 for
the effective launch event, 398 for the separate installation record,
399 for the distinction between copying and retaining originals, and
422 for the typed header and current priority rules. R1's own route,
validity and timing stay with its issued items.
[RUN_STATE source](https://github.com/mpmdw/JouleWise/blob/211ff5033/RUN_STATE.md) ·
[R1 format reference](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/r1-ready-1116/ITEM-R1.md)

## Synthetic timeline exercise

The ticks below express event order only. I walked the draft's pointer,
priority and refusal instructions against each sequence. Each case
assumes the stated filler satisfies its own pinned checks and preserves
any pending dated window.

| Case | Invented event order | Expected classification | Observed classification | Result |
|---|---|---|---|---|
| A · READY between qualification spans | Tick 1, final block s01 closes. Tick 2, lead posts W1 READY with the already-issued s02 launch condition. Tick 3, s02's launch record lands. Tick 4, s02 completes and its clean close is proven. | Through tick 2, `SESSION_READY=no`. At tick 3, `SESSION_READY=yes`, W1 waits for the running span. At tick 4, W1 can take the close subject to its own pre-install checks. | The effective condition left s02 in the queue, then gave W1 priority while s02 ran. The proven close made the arm attempt eligible. No elapsed-time or qualification-result test was introduced. | PASS |
| B · Pre-notice | Tick 1, a pre-notice arrives with no issued READY. Tick 2, the latest predecessor's close is proven. The first stability leg of the local date is eligible and fits. | `SESSION_READY=no`. The short eligible leg can arm at tick 2. | The pre-notice guided filler choice. The first stability leg was selectable at the proven close. | PASS |
| C · Empty hour after R1 | Tick 1, R1 closes. Tick 2, its Check proves restore and retires F0. No counted or effective READY entry can arm. The date's first stability leg has run, the finite instrument legs are exhausted and the HP look already ran. A further stability leg is eligible. | Select the further stability leg. Standing F0 is off the ladder and there is no issued one-shot Part C for a new pin. | The Part C fallback order skipped the used or ineligible rungs and selected further `f2-stab`. It granted no F0 or repeat Part C. | PASS |
| D · Unsuccessful READY arm | Tick 1, effective READY takes the proven close. Tick 2, W1's arm-time recheck finds a foreign runtime SHA and the arm refuses. No host-wide stop applies. The date's first stability leg is done and an `f2-inst-02` leg is eligible. | W1 is ineligible. Return selection to the ladder at tick 2 and take the eligible instrument leg. | The SHA mismatch refused W1. The instrument leg was selectable at the refusal event, with the applicable stop scope checked and no extra close gap. | PASS |

The W1 refusal text was also exercised with a synthetic copy missing only
the ordinary PREQUAL, only W1-mode PREQUAL, only the first-pin read, or
only the actual veto read. Each classified **DRAFT / INELIGIBLE**. A
copy with a foreign SHA in an otherwise complete evidence set had the
same classification. A distinct synthetic receipt-bound commit with a
verified receipt-child link was treated as the bound commit, while the
native and PREQUAL runtime references still had to agree.

## Synthetic header schema examples

These invented headers exercise the JSON Schema only. The integers are
fixture values. These examples carry no evidence or authority.

**Part C example**

```json
{
  "schema": "joulewise.run_state_item.v1",
  "number": 9001,
  "owner": "magistrate",
  "status": "DRAFT",
  "issued_epoch_s": 1800000000,
  "expires_epoch_s": null,
  "supersedes": [],
  "sets": []
}
```

**W1 example**

```json
{
  "schema": "joulewise.run_state_item.v1",
  "number": 9002,
  "owner": "magistrate",
  "status": "DRAFT",
  "issued_epoch_s": 1800010000,
  "expires_epoch_s": 1800020000,
  "supersedes": [],
  "sets": []
}
```

Both schema examples passed Draft 2020-12 validation. Substituting the
literal draft placeholder for a required integer or deleting the
required issue epoch was rejected. The schema checks the header shape.
The evidence and authority checks are the lead's.
[Main schema at the checked revision](https://github.com/mpmdw/JouleWise/blob/2bb70e143/docs/process/run_state_item.schema.json)

## Clause map

| Authority | Draft location | Check and counterfactual |
|---|---|---|
| Register 32 · RLD:18701–18705, 18713–18716, 18838–18845, 18915–18918 | Part C · Lead fills before issue, Magistrate records launch and Check | The same SHA as the prior pin, stale smoke, absent exact-pin synthetic CI, or a missing automatic PASS, first-pin read or restore leaves the new-pin smoke unmet. |
| Register 32 · RLD:18734–18742, 18911–18918 | Part C · Refusal or non-pass | Case C selects a lawful product filler once R1 Check retires F0. Choosing F0 or granting an unchanged-SHA repeat fails this exercise. |
| Register 31–36 · RLD:1184–1199 and P4:779–817 | W1 · Lead fills before issue | Missing signing, probe, receipt, either PREQUAL, or native smoke evidence is ineligible. Substituting a foreign runtime SHA also fails even with a schema-valid header. The bound commit and receipt-carrying checkout each have their own field. |
| Register 35 · RLD:18674–18676, 18911, 19227 | W1 · Magistrate fills before install | The actual latest permitted predecessor must have a proven close and staged host facts must be read fresh. Substituting an earlier clean close or adding a timed close floor fails the check. |
| Register 36 · RLD:17285–17291, 17710–17716, 18827–18832, 18929–18931 | W1 · Effect and priority, Magistrate fills before install | Cases A, B and D distinguish pending READY, running s02, pre-notice and immediate ladder release. A split qualification block, pre-notice hold, or retained priority after refusal fails. |
| Register 36 · RLD:12656–12663, 18832, 18931 | W1 · Lead fills before issue, Magistrate fills before install | Part C evidence or campaign authority cannot substitute for the W1 route. Missing fresh prepare, notice or actual veto evidence leaves the arm ineligible. |

RLD line references use the register's pinned source.
[Research-lead decisions](https://github.com/mpmdw/JouleWise/blob/f9b03c33d/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md)

## Outstanding lead fills

- **Part C.** Verify and issue the one changed SHA and its prior pin,
  promoted tree, registered route, source checks, exact-pin synthetic CI,
  lawful predecessor/window, authority and timing. Assign the
  independent first-pin reader. The magistrate and reader supply the
  launch, terminal, restore, desk and hand-read records through the
  authorized native process. The lead verifies the evidence before
  carrying it to W1.
- **W1.** Supply the independent signing record, signer, allowed probe
  and receipt commitments, bound commit, receipt-carrying tree, exact
  kit, plan and seal. Verify both PREQUAL receipts and native acceptance
  at that checkout. Fill the issue header, allowed predecessor,
  qualification boundary, any effective span, t0/bounds, notice
  authority and veto interval. The magistrate records actual notice and
  veto, fresh prepare/packet, latest close and arm predicates, then the
  installation or refusal under the registered W1 route.

## Verification and handoff

- Documentation freshness passed all 31 checks in
  `python3 -m unittest -v tests.test_docs_freshness`.
- Both synthetic headers passed and both mutations per header were
  rejected. Both forms passed the blank-field and draft-label review.
- This three-file range is documentation only. The native procedures
  and full code suite are outside this draft exercise.

Lead verification and any issue of live items remain outstanding.

**NEEDS_SPEC:** None for the draft scope. The issue-time fills above
belong to the lead.
