# Paper-K — magistrate terminal review (apex read)

Read: the prose diff of docs/paper/draft-v2-skeleton.md from the paper-J head (4ea033ec) to 92f1ca19 in full
(non-table lines; table rows spot-checked), the seat report 01, deltas 02/04/08/09, fix reports 03/07, the Opus
counter-review 05 and the astra peer review 06.

Design-level questions. (1) Does every claim-bearing sentence now match the ratified ruling (43)? Yes: the
measurand is interval-overlap allocation with a conditional timing envelope; the enclosure is a labelled
synthetic diagnostic, never composed; R_cm is the shared-energy-sign/local-corner sensitivity diagnostic with no
common-time claim; F+B is planning only; TR-01 is the fixed untested-transfer sentence in all nine sites; the
contrast runs on prompt 0 with the generality disclaimer; the ABBA order suppresses a linear trend only under
midpoint symmetry; the inserted-gap check is future work not run. (2) Do the numbers match the code? The t
table (2.776 → 4.808173 J), p = 1.29e-6 after the t change, and the enclosure arithmetic [8,10] J were
recomputed by the seats and by two deltas. (3) Is anything now built after its first use? Rounds 1–3 cured the
late-built terms; delta 4 (luna) confirms the last antecedent. (4) Do the three outcome branches remain complete
alternatives with the Refusal branch conditioned on a verified failed production-window record? Yes (astra F1
adopted). (5) Overbuild: none; the two relocation nits were declined.

Residual, out of scope: registry rows 226–267 carry SUPPLIER_PENDING until the D-165 relabel lands (its
branch is in fix round 2); the D-166 registry row destination lands on its own branch.

Bench (this session): tests.test_paper_first_use_ledger, test_paper_terms_lint, test_select_outcome_branches
green after each bench edit. Fill markers 131; outcome markers parent-identical; ledger zero FAIL.

Verdict: LANDABLE, stacked on paper-J (#286). Full-suite replay on the merged head recorded before merge.

## Full-suite replay (row 9)

Unpiped `python3 -m unittest discover -s tests` on the merged head d053e969 (log: magistrate job dir,
paperk-replay.log), exact tail:

    Ran 5124 tests in 6820.392s
    FAILED (failures=1, skipped=110)

The single failure is tests.test_node_worker_subprocess…test_real_client_worker_artifact_contract_over_localhost:
ENVIRONMENTAL / PRE-EXISTING TEST SENSITIVITY (diagnosed in docs/process_traces/2026-09-04-fanout/30; same
disposition as PRs #285, #286 and #287): the test-only 15 s fake-vLLM prepare budget under concurrent load;
identical bytes on main; Linux CI green on this head. Paper-K touches docs/paper, its fill-rehearsal selector and
three test modules only.
