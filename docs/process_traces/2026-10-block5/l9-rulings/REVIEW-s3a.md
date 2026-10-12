# Stage S3 part A (the row validator with an archive context): independent review and dispositions

Reviewer: an Opus 5.5 agent that did not write the code, executing lens, commit `e7ad34fde`. Probes, logs and
mutated copies: `/Users/edr/night-archive/b5-consults/l9-rulings/s3/review-scratch/`. Synthetic fixtures only.

What held: without a context the new file equals the base on every differential the reviewer ran (40
comparisons on two governed fixtures, 18 legacy rows of blocks 1 to 3, the admit and cache paths), and
importing the harvest or the verdict writer loads neither new module. The ordinary good case admits through
the real re-derivation (a science member with failed admission that the exclusion function removed), and the
same member kept refuses. The lead's run on the branch: the five harvest-lane modules pass unmodified (205,
55, 28, 89, 19 tests).

Two wrong admits were reproduced. Neither is reachable from a row the frozen writer is expected to write;
both are fixed, because the validator is the last check before a number.

| # | Finding (executed unless marked) | Disposition |
|---|---|---|
| B1 | A removed member whose measured window cannot be read is noted and skipped, and the skip switches off the whole block that follows only when every member was re-derived: the stored-against-re-derived adapter-continuity comparison (erratum X2 site (i)), session preparation, the ungoverned calibration comparison. A stored continuity record the bundles do not reproduce is then admitted | Fix. Under a context, if any member of `bundle_ids` was not re-derived, refuse `member_rederivation_incomplete:<bundle id>` (a tooling refusal; on a real window it goes to a cold gate, since a member whose bytes cannot be read may or may not be one the exclusion function removed for that reason). This is the lead's rule, not the judge's: it can only stop more than ruling J1 item 9 does, and it keeps erratum X2 enforceable |
| B2 | Any stored condition is answered when the stored NEG-8 bracket's own `conditions` list also names it; nothing authenticates that list. `whole_window_campaign_membership_ambiguous`, `calibration_ledger_baseline_missing` and an unknown word were each admitted that way | Fix. A condition is in the NEG-8 family only if its name is one the verdict writer can write for the NEG-8 screen: take the closed vocabulary from the writer's code (`scripts/run_campaign.py`), not a bare `neg8_` prefix and not the stored bracket's list. Ruling J1 item 2 says "every condition of the stored bracket" and items 3, 4 and 7 say "never"; where they meet, "never" wins. Narrower than the ruling's letter; it can only stop more |
| S1 | An allowance record whose source is `stored_verdict` hands back the row's own stored allowance with no recomputation; the base compared every family field | Fix. For that source the base's full comparison of family records, decision and freshness against the consumer's re-derivation runs (erratum X3 removed those comparisons because the stored allowance is null, which is not the case for a stored bracket that passed). The erratum's terms say this source cannot occur on block 5 |
| S2 | The two neutrality tests take their "base" from `git show HEAD:`, which is the new file once it is committed, so they compare it with itself; the fixtures export `git archive HEAD`, which the S0 program-hash fence refuses once `whole_window.py` is edited; tests write into the worktree | Fix, in two places: the base is pinned to `b039c0257` (this fix round); the fixtures move to committed pin4 archives (`BRIEF-sol-fixtures.md`); scratch output goes under `TMPDIR` |
| S3 | Four guards have no test that fails when they are removed: a member reason naming one removed and one kept member; the identity (not only the count) of the survivor set; the `energy_unreadable` argument of the endpoint authentication; the ungoverned stored calibration comparison | Fix: a test for each, killing the reviewer's mutants m1, m4, m5 and m7 |
| S4 | A malformed entry of `excluded_bundles` is dropped silently, so a member the row names can be missed | Fix: refuse `whole_window_verdict_provenance_invalid` |
| N4 | A `member_failures` entry naming a kept member under a reason absent from `conditions` raises nothing | Fix: refuse `member_code_on_kept_unit:<id>` whatever the conditions list says |
| N1 | On an ungoverned window (ALPHA) the allowance record's bound artifact is not launch-checked; erratum X3 item 6 (iii) says the launch check is unchanged | Carried to the cold Fable pass at the lane's merge as a named question |
| N2, N3 | The validator alone admits a reference that is both a survivor and excluded when the row does not name it; the context's fields are trusted | By design: part B's tripwire and context builder own both (erratum X1 items 8 and 14) |
| N6 | `ArchiveContext` is unhashable | Kept; the session compares contexts by equality |
| N7 | The reviewer's control run of the prescribed test overwrote two scratch files in the worktree | No tracked file changed; the scratch moves under `TMPDIR` with S2 |
