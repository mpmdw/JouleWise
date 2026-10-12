# Stage S1 (kept units): independent review and dispositions

Reviewer: a Sonnet 5.5 agent that did not write the code, executing lens, commit `3653be6dc`. Its run of the
module: 34 tests pass. Its probes and mutants: `/Users/edr/night-archive/b5-consults/l9-rulings/s1/review-scratch/`.
No blocker. None of the four findings is reachable from an honest output of the sealed exclusion function;
each is a document that authenticates and is inconsistent with itself or with the roster.

| # | Finding (executed by the reviewer) | Disposition |
|---|---|---|
| 1 | A member removed in one cell can stay kept in another cell that shares it (decode and p42 share member ids): the checks look at each cell alone | Fix: all of a member's units are dropped or none, within and across cells (`kept_units_member_split_across_cells`) |
| 2 | `members_excluded` is never read: a member listed as excluded whose unit stays kept loads | Fix: every excluded member that has units lies in a dropped unit (`excluded_member_in_kept_unit`) |
| 3 | The below-minimum exemption applies to any cell the roster marks not a target, not to the p42 cell only; two mutants on the p42 clauses survive the tests | Fix: the exemption needs both "not a target" and the p42 cell; tests that kill both mutants |
| 4 | A release-blocked document with an unclassified code is refused as `exclusions_schema_invalid`, never `attempt_release_blocked` | Fix: test `release_blocked` first |
| note | The roster's `pack_id` is not compared with the window's pack | Fix with the above (`exclusions_roster_mismatch`) |
| note | The tripwire raises `TypeError` on `None`, treats a bare string as characters | Fix: refuse non-collection input with a refusal code |
| note | A sensitivity view's structure record carries no label | Fix: the label is carried |
| note | The p42 gate exception accepts any code on a kept p42 unit | Kept: decision O4 (the registered p42 precheck exception); the caller identifies the precheck |

Fix round (Sol 6.1) and the lead: every row marked Fix is built and tested at `lane/2026-10-12-l9-s1`; the tripwire's malformed input refuses `verdict_membership_invalid` (the seat asked for the name; the lead ruled it). The lead's run of the module: 47 tests pass. Merged into the lane.
