# Stage S3 part B (context builder, survivor set, tripwires, sources replay): independent review and dispositions

Reviewer: an Opus 5.5 agent that did not write the code, executing lens, on the part B branch head
(production files identical to the S3 branch's). Synthetic archives only. No blocker: on every input the
frozen harvest can write it found no wrong pass through `build_context` and no wrong roster. It ran the
sealed-digest branch on the three sealed packs of the checkout (design files only): the three sealed digests
equal the checkout's plan trees, and the pinned `build_roster` gives 6, 2 and 6 references and spares by slot.

| # | Finding (executed unless marked) | Disposition |
|---|---|---|
| S1 | The two guards that tie the window, the archive and the kept units together (`context_window_mismatch`, `context_kept_units_mismatch`) have no test; with the first removed, a context for window A is built from window B's tripwires and the validator admits A | Fix: tests for both; `build_context` takes the window from the archive handle, with no separate window argument |
| S2 | The rule "no excluded reference among the survivors" is enforced only in `build_context`; a context built by the public constructor with an excluded survivor is admitted by the validator | Fix, in the validator: refuse `excluded_reference_in_screen` when the context's survivor set and removed ids intersect (erratum X1 item 14: the two checks never disagree). Stage S3 part A's file; this round may edit that one site |
| S3 | Five guards of `sources_replay.py` and three of `context.py` are noticed by no test (among them the only comparison of the evaluator's loss list, Erratum 2 item 4) | Fix: a test for each, from the reviewer's probe inputs; the reviewer's mutants must die |
| S4 | The test seam that supplies a plan-tree digest is a keyword of production code and leaves no trace: with it, a plan tree with swapped slots is accepted for a pack | Fix: the seam is refused for a pack id that is in the sealed table; the binding kind (sealed or synthetic) is recorded in the archive census, and `build_context` refuses a synthetic binding unless the caller states it is a test |
| N1 | The survivor set takes counts and loss rows from the copy in `derived/neg8-screen.json`, not from the withheld bracket; a hand-edited archive can make the tripwire silent (the validator still refuses) | Fix: cross-check the loss rows and counts against the authenticated withheld bracket (`survivor_set_record_differs_from_bracket`) |
| N2 | A screen record with no re-screen is reported as a roster problem, and a malformed `survivors` raises an uncaught exception | Fix: `neg8_screen_record_invalid`, a refusal |
| N5 | The public stop record prints one row per code, so the number of restricted codes on a member is visible | Fix: one row per member; a member with any restricted code prints "restricted code" once |
| N3, N4 | A precondition is checked by both callers and not inside the replay; on the recorded-sources path nothing checks that every invoked reference is in the rebuilt set (reasoned, not executed) | Kept: each can only add a refusal elsewhere (the count check fires) |
| N6, N8 | Equality of `build_roster` at the two pins is held by a test, not at run time; `seal_pins.json` is the trust root and is covered by the frozen-file test | Kept, as the roster ruling's item 6(c) is written |
| N7 | An absent spare with a harvest-only loss code other than `bundle_absent` and no evaluator row is accepted | Kept: it is what the roster ruling's three checks say; listed for the cold pass with the lead's decision of section 4a |
