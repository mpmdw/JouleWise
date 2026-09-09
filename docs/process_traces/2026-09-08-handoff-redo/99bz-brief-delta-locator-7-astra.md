# Delta re-audit — ICLOUD-CUSTODY-LOCATOR-01 part 7 (gpt-6-astra, medium, genre review, READ-ONLY, execution lens)
Branch fix/2026-09-08-icloud-custody-locator, head 07e6e4c1; the round is `git diff b598113e 07e6e4c1` (five files). It implements
the ruling at /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99bw-magistrate-ruling-census-scope.md
items 2–3. Audit ONLY this diff: (1) does `_idle_admission_core_evaluation` default to issuing and forward it; do all
three callers pass what the ruling says (only the completed-window replay caller passes read_replay); execute the
regression and one in-memory counterfactual (live AXI path with replay literal → the absent-vs-replacement assertion
must fail); (2) is the census now keyed by ordinal-within-function with `line` informational; execute the
inserted-line and second-call counterfactuals; (3) does the contract paragraph name all four census limits and the
runtime invariant, without contradicting the earlier addenda; (4) any NEW defect (an existing test that "assumed
implicit replay" was changed to opt in — is that test a genuine replay path or did the change hide an issuing-path
regression? cite it). ≤ 500 words; verdict keys per genre review; no edits; header < 8192 bytes.
