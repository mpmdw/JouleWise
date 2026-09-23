ROLE: refuter seat (execution lens) for JouleWise lane A276 (NOTICE-SUMMARY-V3-TEXT-01). Your job is to break the change, not to confirm it. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: []

0. CONTEXT. Detached worktree at the candidate head c9e2bd14 (branch feat/2026-09-23-a276-notice-v3; base main 313efcca). Scratch only under $TMPDIR or /tmp; never write in the repo. Never run launchctl, sudo, networksetup, or touch /Users/edr/night-custody or /Users/edr/JouleWise-measurement-*.

1. SPEC: TASK_QUEUE.md row A276 and docs/process/state_kernel.json NOTICE-SUMMARY-V3-TEXT-01 acceptance; brief /Users/edr/code/wt-1d3796d5-bk/docs/process_traces/2026-09-23-activation-1d3796d5/03-a276-seat-brief.md. Diff: `git diff 313efcca..HEAD`.

2. LENS: EXECUTION. (a) Mutation: for each changed production line in joulewise/evidence_night.py render_notice and joulewise/quiet_predicate_campaign.py pilot_summary, make a copy of the worktree under /tmp, apply a mutant (drop a sentence, swap an operand in the span formula, collapse each max/min or comparison to each operand, change the registration check to accept any sha, flip the `if rule` branch, restore the old SD label), run the named tests, and report which mutants SURVIVE. (b) Execute render_notice on a realistic v3-bound state (build it the way tests/test_evidence_night.py does) and paste the full rendered notice; check each sentence against configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json and the enforcing code. (c) Find every production caller of render_notice (evidence_night's notice command and any other) and show the new Refused path cannot fire for the plan the next arm will pin. (d) Run `python3 -B -m unittest tests.test_evidence_night tests.test_quiet_predicate_campaign` once at HEAD. Named modules ONLY; NEVER run `unittest discover` or scripts/shard_tests.py.

3. OUTPUT: review-genre envelope, verdict = {counts, findings} only, JSON header under 8 KB; the body carries the rendered notice, the mutant table (mutant, test that killed it or SURVIVED), and each finding with severity blocker/should_fix/nit and an executed counterexample. Timebox 45 minutes.
