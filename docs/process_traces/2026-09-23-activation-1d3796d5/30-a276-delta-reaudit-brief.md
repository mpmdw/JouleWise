ROLE: delta re-audit seat for JouleWise lane A276 fix round 1. Fix rounds introduce defects; find them. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: []

0. CONTEXT. Detached worktree at candidate head 912345cd (branch feat/2026-09-23-a276-notice-v3). The delta under audit is `git diff c9e2bd14..912345cd`; the base of the lane is main 313efcca. Scratch only under $TMPDIR or /tmp. Never run launchctl, sudo, networksetup; never touch /Users/edr/night-custody or /Users/edr/JouleWise-measurement-*.

1. The fix contract is /Users/edr/code/wt-1d3796d5-bk/docs/process_traces/2026-09-23-activation-1d3796d5/25-a276-fix1-seat-brief.md (X1-X7); the findings it closes are in 22-a276-opus-contract-lens.md and 15-a276-sol-refuter.md in the same directory; the seat's report is 26-a276-fix1-seat-report.md.

2. QUESTIONS (executed evidence for each): (a) Is each X1-X7 closed as specified, at the production call site? (b) X1 in particular: does the armability decision now really run in candidate H's interpreter (trace the call from `prepare`/`check`/`notice` through sealed_candidate or equivalent), and can the caller-checkout path still veto or, worse, still APPROVE a registration H would refuse? (c) Did the fix round introduce a new defect: any sentence in the rendered notice or summary now false against the code (quote the enforcing line), any refusal that fires on the next legitimate v3 arm, any test that passes only because of fixture shape? (d) SAME-SIGNATURE STATEMENT (mandatory): is any finding the same defect class as a round-1 finding (false generated text; unpinned sentence; caller-checkout import)? Say yes/no per class. (e) Re-run 5 mutants of your own choosing on the delta in a /tmp copy. Named modules ONLY: `python3 -B -m unittest tests.test_evidence_night tests.test_quiet_predicate_campaign`; NEVER `unittest discover` or scripts/shard_tests.py.

3. OUTPUT: review-genre envelope, verdict = {counts, findings} only, JSON header under 8 KB; body with each answer, the same-signature statement, and findings with severity blocker/should_fix/nit and executed counterexamples. Timebox 40 minutes.
