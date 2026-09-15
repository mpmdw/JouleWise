# Refuter brief — GAMMA root-key fix, EXECUTION lens (`fix/2026-09-15-gamma-root-keys` @ `678d9bcc`)

SESSION_MODE: delegated
WRITE_SCOPE: []

Worktree `/Users/edr/code/JouleWise-wt-ref-gamma` (detached at `678d9bcc`); you may NOT edit it. You MAY write under `/tmp`: first `cp -R /Users/edr/code/JouleWise-wt-ref-gamma /tmp/magistrate-d6888966/gamma-exec-copy` and do every mutation in that copy. Never touch `/Users/edr/code/JouleWise`, other worktrees, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`. No network. Run single modules (`TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest ...`).

## Under review
`git diff 664b3f6c..678d9bcc` (three files). Defect and context: `docs/process_traces/2026-09-15-activation-d6888966/08-gamma-seat-report.md` is NOT in this checkout; the facts: `configs/campaigns/d117_contrast_v5/generate_configs.py:2697` emitted `roots: {claim_leaf, bound_leaf}`; `joulewise/arm_readiness_evidence_t0.py:1014–1020` reads `claim_root_leaf`/`bound_root_leaf`. The contract-lens refuter (a separate seat) already confirmed by source review: canonical key pair, `root_namespace` is a distinct mapping, historical v1–v3 trees are frozen bytes not semantically read, both floor v5 generators are canonical. Do NOT repeat the contract review; execute.

## Execute, in the /tmp copy
1. Baseline: `python3 -B -m unittest tests.test_d117_contrast_v5_pack tests.test_arm_readiness_evidence_t0` — paste the tail. (If the G4 census test errors on `pgrep`/`sysmond` in your sandbox, name it and exclude it by `-k` inversion or by listing the other tests; say exactly what you excluded.)
2. Mutation M1: revert line 2697 to `{"claim_leaf": CLAIM_ROOT_LEAF, "bound_leaf": BOUND_ROOT_LEAF}`; run the two new regressions (`-k canonical_root_leaf_keys -k legacy_keys_are_refused`); both must fail; paste the failure lines. Restore.
3. Mutation M2: in `tests/test_arm_readiness_evidence_t0.py`, feed the positive call `t0._root_observation(context(tree["roots"]), kind="ROOTS")` the `legacy_roots` mapping instead; the test must fail with "arm roots do not derive from frozen leaves"; paste. Restore.
4. Mutation M3: in `joulewise/arm_readiness_evidence_t0.py`, make the reader accept EITHER key pair (e.g. `roots.get("claim_root_leaf") or roots.get("claim_leaf")`); which of the two regressions catches that loosening? If neither does, that is a should-fix finding (the negative assertion must pin the refusal). Restore.
5. Isolation: count `python`/`vllm`/`pgrep` processes and `/tmp` entries before and after step 1; report leaks. Confirm both regressions use `TemporaryDirectory` cleanup on failure paths (force a failure inside and check the directory is gone).
6. `git -C /Users/edr/code/JouleWise-wt-ref-gamma status --short` must be empty at the end (you never edited it).

## Report
claude-codex-report/v1 envelope (genre `review`, under 8192 bytes): verdict LANDABLE / FIX-FIRST; findings with severity (blocker / should-fix / nit), file:line, counterfactual; the M1/M2/M3 tails verbatim; leak counts; anything not verifiable.
