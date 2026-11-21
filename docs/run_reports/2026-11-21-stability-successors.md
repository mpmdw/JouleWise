# Stability successor mint, 2026-11-21

The Tier 1 mint adds **32 kits on pin A** (`f2-stab-17..48`, 384 positions)
and **5 kits on pin B** (`f2-stab-49..53`, 60 positions). Each kit follows
the last admitted kit on its pin, including all twelve ordered cells and
the frozen paths. The existing generator selects the first layout match
whose master seed and derived leg seeds are distinct from one another and
available in the pre-mint public campaign kit inventory. Earlier successor
seeds enter that inventory before the next draw. Every mint row enters the
wider roster under RL-190 §1.3. The base population remains kits 01–14.
[Kit index](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/KITS.json)

## Capacity replay

The replay starts from the same RS483 anchor, uses the same pinned planners,
admission rules and preemption schedule as PR #916, and appends successors
in kit and leg order on each pin. The original 192-position ledger
reproduced byte for byte before the extension. In fast-close, an ample
roster uses 365 new A positions and 41 new B positions before
**Dec 15 12:35:29 PST**. That requires 31 A kits and 4 B kits. With one
fewer than the minimum and the other pin at its minimum, the first
uncovered A dispatch is Dec 15 06:24:58 and the first uncovered B dispatch
is Dec 14 10:57:23. The mint adds one whole kit per pin above the minimum.
[Original replay and assumptions](https://github.com/mpmdw/JouleWise/blob/9d1117724f42958c959fc58c5a0a841490da8938/docs/run_reports/2026-11-20-stability-runway.md#reproduce-and-verify)

All dates below are local PST. The first uncovered dispatch is the first
modeled clean dispatch in a pin's band with no eligible position. The
inventory column assumes successor queues are renewed beyond Dec 15.

| Scenario | Pin | First successor start | First uncovered with current expiry | Unspent at expiry | Inventory depletion with renewal |
| --- | --- | --- | --- | ---: | --- |
| Uninterrupted fallback | A | Nov 30 01:09:30 | Dec 15 13:15:00 | 121 | Dec 22 17:42:53 |
| Uninterrupted fallback | B | Dec 1 12:49:11 | Dec 15 12:44:07 | 34 | Jan 1 12:05:12 |
| Fast-close sensitivity | A | Nov 28 04:24:58 | Dec 15 13:30:18 | 19 | Dec 16 08:57:53 |
| Fast-close sensitivity | B | Nov 29 11:05:18 | Dec 16 10:50:01 | 19 | Dec 22 11:50:12 |
| W1 and qualification preemption | A | Dec 2 08:25:39 | Dec 15 13:15:25 | 161 | Dec 25 01:02:14 |
| W1 and qualification preemption | B | Dec 4 12:36:56 | Dec 16 10:50:01 | 39 | Jan 4 12:05:12 |

Successor A occupies time that exposed earlier B dispatches in the
unextended fast case. The joint replay therefore moves B's first successor
start to Nov 29 while the Nov 27 admission deadline covers either pin.
Every predecessor position starts before its existing expiry in all three
scenarios. The ledger marks each projected start for which the queue is
still valid. Its post-expiry rows show the inventory-only forecast.
[Capacity ledger](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/filler-capacity-20261121.tsv)

## NEEDS_SPEC

Both admitted pins rejected the requested literal
`not_before: 2026-11-26T00:00:00-08:00`. Their queue schema accepts an
earliest local t0 date in `YYYY-MM-DD` form. The proposed encoding is
`2026-11-26`, with the midnight PST bound in the README and admission item.
Pinned validators accepted all 444 scratch candidates using that encoding.
Release of `fillers-w3` and use of the draft item below await the lead's
encoding ruling.

## Verification

The eight audit tooling tests passed. The audit `validate_kit.py` passed
69 invocations across 37 kits, with both item 463 windows on all 32 A
kits and no window on all 5 B kits. Each invocation verified the kit
bytes, the frozen paths and the ordered cells against its pinned runner.
The ledger recount passed for all 636 rows, per-pin order, clock bands,
ranks, expiry and nonoverlapping dispatches. Local checks use synthetic
planning and the audit tooling. The draft PR carries hosted repository CI.

## DRAFT RUN_STATE item

**Stability successors admitted on the existing pins (RL-190 §1.3)**

- From the landed audit mint commit `<AUDIT_MINT_COMMIT>`, use the next
  unspent successor position in kit and leg order on the eligible pin.
  Verify the selected `fillers-w3/README.md` queue digest and the
  `f2-stab/KITS.json` kit digest and pin before issuing. Each file names
  one leg. Earliest start is 2026-11-26 00:00:00 PST. Queue expiry is
  2026-12-15 12:35:29 PST. Obtain a lead renewal before starting on an
  expired queue.
- On pin A `2d347f721`, use kits 17–48 once kit 14's last position is
  spent. The first eligible A start of the local date is rank 1 and
  further A starts are rank 4. Select the actual-t0 window under item 463.
  On pin B `6e9d42f1d`, use kits 49–53 once kit 16's last position is
  spent, at rank 4 only from 10:50:01 through 13:14:59 local, without a
  batch window. Items 422, 447, 463, 464 and 473 govern selection, proof of
  close, and refusal. For a refusal or missing proof, record it and apply
  item 422 before taking the next eligible rung.
- Successors enter the wider `lm-stab-02` population only. Base remains
  kits 01–14 for `lm-stab-01` and the base tables in `lm-stab-02`.
- Next activation checks whether the predecessor roster is spent on the
  eligible pin. The first successor issue names that predecessor close
  and the selected queue, kit digest and pin. Admission is due Fri Nov 27.
  If the mint is missing at that deadline, report it to the lead and
  continue the admitted ladder.
