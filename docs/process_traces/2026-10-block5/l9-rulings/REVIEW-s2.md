# Stage S2 (window bracket): independent review and dispositions

Reviewer: a Sonnet 5.5 agent that did not write the code, executing lens, commit `dbecf331d`. Its run of the
module: 30 tests pass. Probes and mutants: `/Users/edr/night-archive/b5-consults/l9-rulings/s2/review-scratch/`.
No blocker: it found no path that gives a governed window (BETA, GAMMA) a wrong operative bound without a
refusal. The block-wide largest bound (B_max) and ALPHA's evaluation are authenticated more weakly than a
governed window's.

| # | Finding (executed unless marked) | Disposition |
|---|---|---|
| S1 | B_max reads the acceptance file with only the archive's own digest line: rewritten member bounds, a cut member list and an unissued role are all accepted, and B_max follows the file | Fix: the same authentication the window evaluation uses (the frozen registry digest), role `issued`, exactly 24 members, and identical acceptance bytes in all three archives; refusal `block_b_max_invalid` |
| S2 | A missing `ledger_cutoff`, `plan.path` or `window_identity` raises a bare `KeyError` | Fix: refusals (`block_b_max_invalid`, `window_bracket_not_passed`) |
| S3 | The field-comparison test reads the compared fields back from the module, so dropping `b_fiducial_s` from the comparison survives all tests; the ALPHA "reads fresh" branch and the inclusion of row T are untested (three surviving mutants) | Fix: the test's field list is typed from Erratum 3 item 10(ii); a stale ALPHA fixture; a largest bound placed at row T. All three mutants must die |
| S4 | For ALPHA nothing cross-checks the evaluation, and `withheld/member-assessments.json` (which selects the members that set the window span) has no digest under `outputs` at either pin | Fix: authenticate that file by a digest the archive does record if one exists (the reviewer names the `assessments_evidence` digest in `derived/window_flags.json`; check it at both pins); if none exists at pin `224a264c5`, recompute the selection from authenticated bundle files, or say exactly why neither can be done. Never silently unauthenticated |
| N1 | The module calls the bracket evaluation directly and skips the wrapper's check that the registered valid captures all load (the harvest's anti-withholding check) | Fix: call the frozen wrapper the harvest calls (`calibration_bracket_for_bundles`) if its inputs can be built from the archive; otherwise replay that one check and say so |
| N2 | `require_member_bound_is_window_bracket` accepts any mapping with a `b_fiducial_s` key | Fix: accept only the module's `WindowBracket` |
| N3 | B_max accepts one archive, or one archive three times | Fix: exactly the three analysed windows, packs alpha, beta, gamma, distinct; the empty list to the prefix check refuses too |
| N5 | An `except ValueError` relabels custody refusals as `window_bracket_not_passed` (read, not executed) | Fix: a refusal passes through with its own code |
| N6 | The authenticated `calibration_bracket` block of `harvest.json` is not compared with the module's scope and result | Fix: compare scope, status, reasons and the governed word (`window_bracket_differs_from_harvest`) |
| N7 | The epoch filter of B_max ignores continued epochs; the continuation registry is empty in this tree | Fix, small: refuse `block_b_max_invalid` if the registry is not empty, so a later change cannot pass silently |
| N4, N8 | A row with no bound refuses B_max; capture bytes are read from ledger locators outside the archive handle (hash-verified against the ledger) | Kept as they are: both fail closed |
