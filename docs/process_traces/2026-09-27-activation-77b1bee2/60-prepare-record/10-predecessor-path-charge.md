# Cold gate PREDECESSOR-PATH-01: may the prepare step pass `--predecessor-acceptance` by its repository-relative path?

You are a COLD judge: a fresh session with no loop context. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files. **Write a contamination disclosure first.** Stay outcome-blind: open no epoch 25G83 W1/W2 measured value.

**Working tree:** `/Users/edr/code/JouleWise-wt-corpus-fp-77b1bee2` (detached at `f783a3fd`, the custody repair; its PR #436 is pending merge). The issuer is `scripts/issue_calibration_acceptance_generation.py`.

**The texts**, all under `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/`:
- The statement REV5-REFUSAL-BRANCH-01: `60-prepare-record/00-refusal-branch-final-statement.md`, sha256 `8717e33c…39a6`. Read item 2, the fixed arguments and the ban on escape flags; items 6(d) R4 and 10 (the override).
- The finding: `50-custody-outside-repo/71-coldgate-final-diff-ruling.md`, S1 and options (a)–(c). The statement's fixed command omits `--predecessor-acceptance`. The issuer's default is an absolute path to `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`, and it is stored in `derivation_notes.predecessor.relative_path`. R4 says the issued file stores no absolute path.

**The owner was asked** at ≈14:05 PDT (Gmail `1a0e4ac6d73738a2`), recommending option (b). No reply has come yet. The owner's reply, if one arrives before the prepare step runs, overrides this ruling.

**Rule on:**
1. Verify the finding by reading the issuer. Where is the default set, and how is it stored? Does passing `--predecessor-acceptance configs/calibration/calibration_acceptance_d079_v2_n17_r7.json` from the run checkout name byte-identical content? Is it authenticated the same way, against the registry pin? Is `relative_path` then relative? Run a synthetic probe if useful.
2. Is option (b) an escape flag under item 2, or does it only choose how an unchanged input is named? Can a cold gate permit it, or only the owner?
3. Choose (a), (b) or (c), and give the exact argument text for the prepare record.

**Protocol.**
- One non-interactive session: no background tasks, no subagents, every command in the foreground.
- Modify NO file in any repository. Scratch goes under `/tmp/cg-pred-77b1bee2/`.
- Write the ruling with the Write tool to `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/11-predecessor-path-ruling.md`. Ending before that file exists is a protocol failure.
- Budget: 20 minutes. The first line is `RULING: (a)`, `RULING: (b)` or `RULING: (c)`. End with a 3-line plain summary.
