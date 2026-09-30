You are an implementation seat in the JouleWise repo (worktree: /Users/edr/code/JouleWise-wt-d138a-ff50b201, branch feat/2026-09-29-d138-loader-promotion, based on main 9eab16f8). Single non-interactive session: no background tasks, no subagents; every command in the foreground.

## 1. Goal (owner ruling — do not reinterpret)
The owner (Ed) chose D-138 option (a) on 2026-09-29: "withdraw the file registration and hold code; land the loader repair, the promotion tool and their tests." The source branch is `origin/feat/2026-09-27-d138-25g83-issuance` (head b953f4b0). Port ONLY these onto main:
- the **loader repair**: the new module `joulewise/calibration_dispositions.py` (pinned observation-disposition registry loader) and whatever minimal call-site change in `joulewise/calibration_bracketing.py` and `scripts/issue_calibration_acceptance_generation.py` is the loader repair itself (reading the disposition registry through the new loader);
- the **promotion tool**: `scripts/promote_calibration_candidate.py`;
- their tests: `tests/test_calibration_dispositions.py`, `tests/test_promote_calibration_candidate.py`, and ONLY the loader-repair portions of `tests/test_calibration_bracketing.py`.

## 2. Must NOT be ported (dropped by the owner's ruling)
- the claim hold: `joulewise/claim_hold.py`, anything named hold / held build / G1 / G2 / S1 bracket hold / S2 go-receipt hold / S3 manual-campaign hold / identity seam / `REGISTERED_GENERATION_OS_BUILD` / non-claim-purpose opt-in for a held file; `tests/test_claim_hold_census.py`, `tests/test_claim_hold_routes.py`;
- the file registration and pin swap: the issued `d079_calibration_acceptance_v2_n12_25g83_r1` acceptance file must NOT be registered, pinned, or made loadable as default or opt-in; R7 (25F84) stays the only registered default; no registry/pin/pinset changes (`scripts/floor_mint_pinsets/schema_v2.json`, `tests/verify_calibration_acceptance_corpus.py`, arm_readiness, run_campaign, calibration_epoch_continuation, epoch_equivalence_check, sim_acc_25g83_rev5, validate_powermetrics_fiducial changes are all out);
- anything under `docs/`.
If the promotion tool or a loader test depends on a dropped piece, make it NOT depend on it (e.g. a test that promotes into a temp directory rather than the registry). If that cannot be done without touching a file outside WRITE_SCOPE, STOP and return NEEDS_SCOPE with the exact file and reason.

## 3. Scope (exhaustive; never infer more)
WRITE_SCOPE: ["joulewise/calibration_dispositions.py","joulewise/calibration_bracketing.py","scripts/issue_calibration_acceptance_generation.py","scripts/promote_calibration_candidate.py","tests/test_calibration_dispositions.py","tests/test_promote_calibration_candidate.py","tests/test_calibration_bracketing.py"]

## 4. Method
Use `git show origin/feat/2026-09-27-d138-25g83-issuance:<path>` and `git diff 9eab16f8 origin/feat/2026-09-27-d138-25g83-issuance -- <path>` to read the source. For each hunk you port, decide loader-repair / promotion vs hold / registration and record the decision. Do not add new behaviour.

## 5. Verification (you run it; report exact commands and outputs)
- `python3 -B -m unittest tests.test_calibration_dispositions tests.test_promote_calibration_candidate tests.test_calibration_bracketing tests.test_acc_25g83_rev5` (use `python3`, never a venv interpreter) — all OK.
- `git grep -n -i 'claim_hold\|held_build\|n12_25g83_r1' -- joulewise scripts tests` shows no registration or hold reference except string constants inside `scripts/promote_calibration_candidate.py` naming the candidate it promotes (list every hit and justify it).
- One counterfactual per ported behaviour: revert the loader call-site change in a scratch copy and show a named test goes RED; restore.
- NOTE: sandboxed runs cannot use pgrep/sysctl; if an unrelated test fails only for that reason, say so, do not "fix" it.

## 6. Output
Commit on the branch (one or two commits, message prefix "D-138 option (a):"), do not push. Final report: per-file hunk ledger (ported / dropped + one-line reason), test commands + results, counterfactual results, any NEEDS_SCOPE / NEEDS_RULING items. Do not claim anything you did not execute.
