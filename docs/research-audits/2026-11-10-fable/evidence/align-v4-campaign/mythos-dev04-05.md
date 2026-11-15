# Seat: Mythos 5.2, dev-04/05

Sat Nov 14 18:25:48 PST 2026 (`date`). Delta check of `cl-dev-04.v1.1` and `cl-dev-05.v1.1` against `cl-dev-03.v1.1` for RL-149 §2.8 line 1 and RL-158 §3. I did not write the kits.

## Verdict

| Kit | sha256 (my `shasum` of the blob at `fecaf73f3`) | Verdict |
|---|---|---|
| `cl-dev-04.v1.1` | `1cc6673d…2228` | **ADMIT** |
| `cl-dev-05.v1.1` | `2747381b…ca1a` | **ADMIT** |

- **Neither kit needs a byte changed.** Both shas match the builder's, and dev-03's is still `0f535774…e14b`.
- **Both admits hold only on the ruled path:** dev-03 runs on `cl-dev-03.v1.1` and its class A smoke is met (F1).
- **Owed before READY:** the lead's two record lines in F1, the queue expiry in F2 and line 2 in F5. F3 is a question for the research lead.
- **I ran no Python.** `validate-kit`, `plan`, the mocks and the tests are the builder's. Everything below is from `git`, `shasum` and hand arithmetic.

## Findings

**F1. Both kits rest on dev-03's smoke, and no READY line says so.** Major; lead, and the research lead on the fallback.
- Each title says the smoke "was dev-03's first three legs" and the kit carries no pilot rule. dev-03 has not run yet.
- RL-158 §3 gates dev-04 on "dev-03's first span desk-final". That is not RL-161 §2's smoke line (L002 released against L001's capture and ran its turn), nor R9.
- **Fix:** the READY rows of dev-04 and dev-05 cite both dev-03 records, R9 passed and the class A smoke met. That is §2.8 line 8 for these kits (RL-150 R5).
- **On RL-158 §2's fallback (dev-03 on v1.1a) neither kit may arm as built.** dev-04 then needs its own smoke, and this draw cannot give a three-leg one: L001 to L003 are all own-shaped and the first consumer is L005. That case goes to the research lead.

**F2. The queues' expiry is legal only for a commit at or after Sun 15 Nov 23:59 PST.** Medium; lead.
- Both queues expire `2026-11-22T23:59:00-08:00`. Committed tonight or on Sunday, that is more than seven days (§2.8 line 3).
- Nothing in code checks it: `validate-queue` only requires that `expires_at` parses.
- **Fix:** commit on Monday as the builder assumes, or set `expires_at` to at most commit + 7 days. The dev-02 queue was corrected the same way.

**F3. dev-04's second span is five consumers on one reference.** Medium; research lead.
- L008 to L012 are all span-shaped, so span 2 has no own-shaped warm leg and span 1 has four own-shaped warm legs and one consumer. Within dev-04, shape cannot be separated from span.
- If L007's capture is missing the span stops with all five unrun. If consumers time out at G0, five legs each spend 1,200 s and are excluded, and no stop fires.
- dev-03's remainder is gated on its one pilot consumer (RL-158 §2). dev-04 has no such gate, although L005 is the same kind of signal.
- **Proposed:** span 2 arms back to back only if L005 released its G0; otherwise it comes to the research lead. I would keep the seed: a draw swapped for a nicer split is a choice for a ruling, not for the builder.

**F4. Two queue rules are not enforced by code at this pin.** Minor; lead and magistrate.
- **`not_before`:** only its format is validated; `next_action` never reads it.
- **The k+2 desk rule:** it looks only inside one queue's span list. Each queue here has two spans, so it never fires.
- **By hand:** dev-03's remainder desk-final before dev-04 s02 arms, dev-04 s01 before dev-05 s01, and dev-04 s02 before dev-05 s02.

**F5. Line 2 at the pin is open, and four shards are red.** Lead; carried from my delta report's D2.
- At 18:24 on #788's head `9cbb365a6`: test shards 2, 3, 5 and 6 failed, 4 and 7 to 12 were pending, and shard 1 passed.
- I could not read which tests failed. The lead records the red set against the base (RL-155a §4's reading). One result covers dev-03, dev-04 and dev-05, since they share the pin.
- The lead also re-runs `validate-kit` on both new kits.

**F6. The memo's numbers run 07 to 21, not 08 to 20.** Minor; lead, in the ledger.
- The block-design memo also assigns 07 (dev-06), 11 (pilot-02), 12 to 17 (qual-01 to qual-04, dose-01, dose-02) and 21 (reserve-02).
- It gave 05 to dev-04 and 06 to dev-05, the same names, so these two seeds sit where the memo put them. Its dev-05 was a different design that was never built.
- The memo is not a live ledger: it had 03 for dev-02, 04 for dev-03 and 09 for hp-01.

**F7. Each title states a date.** Minor; no re-hash for this alone.
- "Runs on Tue 17 Nov after dev-03" and "Wed 18 Nov from 02:40" turn false if dev-04's second span slips to Wednesday, which RL-158 §3 allows.
- Drop the sentence if a re-hash happens for another reason; otherwise the ledger notes that the date is the plan.

**F8. Smaller items.** Notes.
- **The branch has no PR.** Keep `align/2026-11-14-dev04-05-kits` or tag `fecaf73f3` until both blocks are desk-final; the kit files are not on the pin.
- **dev-05 is twelve type A.** That is RL-155 §5.3's "if not" branch. A dev-05 with two type-T legs would be a new pin and a new kit.
- **D1 carries over:** the Air desk must run this line's `desk.py` for both blocks.
- **The two "back to back" plan rows** start at span 1's expected end with no time for the close and restore check. The real t0 is later; the bound is still 18:33:10.

## Answers to the brief

**1. The diff: every difference is allowed, and dropping `pilot_counted` is right.**
- **Changed, by `git diff` of the blobs:** `campaign_id`, `title`, `seed_law.master_seed`, each leg's `seed`, `prefill_tokens` and `g0_shape` where the draw differs, and the `pilot_counted` rule removed. Nothing else.
- **Unchanged:** the frozen block (commit and all 38 path hashes), runner, model, the other eleven inclusion rules, `stop_rules` with RL-161's stop text, `span_template`, checklist, looks and desk.
- **No code change:** the pin and the branch head differ only in the kit files and three test lines.
- **`pilot_counted`:** it registers dev-03's first three legs as a smoke and gates "the remaining nine". Kept in dev-04 it would describe another block's legs. `cl-dev-02` dropped dev-01's rule the same way, and RL-155 §3.3 accepted that. The condition is F1.

**2. Seeds: the legs reproduce, and nothing collides.**
- **By hand from `shasum` draws:** all 24 seeds, 24 sizes and 24 shapes match the kits. I checked the method on dev-03 first (L001 and L012 seeds, block 0 sizes).
- **Master seeds in any ref's history:** 01 (dev-01), 02 (dev-02), 03 (dev-03), 04 (hp-01), 99 and 20261113 (test fixtures). 05 and 06 appear only in `fecaf73f3`.
- **Leg seeds:** the only repeats across the kit files are the twelve that dev-03's two drafts share. hp-01's twelve match none.
- **Reserved numbers:** F6.

**3. The half rule on 6 + 6 holds for both.**

| Block | Span 1 consumers | Span 2 consumers | Total | Cut at L007 |
|---|---|---|---|---|
| dev-04 | L005 | L008, L009, L010, L011, L012 | 6 of 10 | own (2,000) |
| dev-05 | L002, L003, L005, L006 | L008, L012 | 6 of 10 | own (19,458) |

- **By size:** two consumers per size in both blocks.
- **Other layouts:** the builder's 16 and 22 are right. Every cut on an own leg keeps all six consumers, so every such layout holds half.
- **Chosen cuts:** dev-04's span 2 cannot be split by choice, since every leg after L007 is span-shaped, so filler P skips it. dev-05's span 2 can be cut at L010 only.
- **If dev-04's span 2 is lost:**
  - The block ends with one consumer (L005, 2,000 tokens) of five warm legs. That is under RL-158 Q6's four, so it goes to the research lead. Nothing stops and the six legs count.
  - If span 2 stops part-way, its re-run starts on a span-shaped leg, which then captures. Wherever it stops, the block ends with 5 consumers of 9 warm legs, which still holds half.
  - The exposure itself is F3.

**4. The queues are finite, pinned and in order; the plans respect both bounds.**
- **Finite:** two spans each, L001-L006 and L007-L012, every leg once, in kit order.
- **Pinned:** both spans carry the kit path and the sha I computed.
- **Expiry:** F2.
- **Plans:** I re-did all seven rows by hand.
  - Expected seconds follow from the kit's leg budgets: 10,507 and 12,071 for dev-04, 11,680 and 10,898 for dev-05.
  - The worst case is 24,750 s, the fence adds 1,460 s, and the latest t0 is 18:33:10.
  - Every t0 is legal, including 10:50:00, 13:15:00 and the fence end at exactly 01:50:00.
- **The expected Tuesday:** dev-03 closes about 09:28, so span 1 arms about 09:48 and ends about 12:43. Span 2 then waits for 13:15; its fence ends 20:31:50.

**5. What would make the data non-countable.**
- Arming either block before dev-03's smoke is recorded as met, or on the v1.1a fallback (F1).
- A queue committed with an expiry over seven days (F2).
- Line 2 left unrecorded at the pin (F5).
- A change to a frozen path or to host state between dev-03 and dev-05; the campaign-scope stop covers it.
- Nothing in the kit bytes themselves.

## Not done

- No test, mock, validator or `plan` was run.
- I did not read the failing CI tests, and I did not re-hash the frozen paths: the frozen block is byte-identical to dev-03's, which I checked at this pin.
- Blinding held: no measurement, slot, transcript, energy, power, meter or powermetrics file was opened, nothing under `~/night-*` or `campaign-out`, none of the builder's mock directories, and not the block-design seat's `stream.jsonl`. No SSH. Nothing was written or edited.