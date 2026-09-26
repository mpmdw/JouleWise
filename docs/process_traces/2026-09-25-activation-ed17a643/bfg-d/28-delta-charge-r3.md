# BFG-D final delta re-audit charge: rounds 7 and 7b plus the main merge, `3e984ecc` → `a44f0685`

**Sources.**
- `23-consumer-drift-final-texts-v1.1-source.md` §3: the consumer-drift cure, from cold gate CONSUMER-DRIFT-ESC-01 and its addendum.
- `24-fix-contract-r7.md` and `26-fix-contract-r7b.md`: the contracts.
- `25-seat-report-r7.md` and `27-seat-report-r7b.md`: the seat reports. Verify these; do not trust them.
- `a9c40d4c`: merges main (#418, #419, #423) and resolves the decision-log conflict. A-R5b comes first, then A-R5b-1.
- `a44f0685`: the lead's kernel-label update for the renamed liveness test.

**Check each of the following with executed evidence:**
1. §3.1–§3.13 are implemented exactly. In particular:
   - the seam is the only consumer path;
   - the shared collector and policy are called by both `check` and `prepare-candidate` with the same arguments, including `target_epoch`;
   - `check --battery-confounded-session-id` works;
   - A-7 and the ledger refusal are mirrored;
   - the AST guard covers `load_committed_verdict`, `validate_window`, `compare_verdict`, `verdict_record` and `parse`, with the six-row allowlist.

   Mutate in /tmp copies to prove the guard fails for each of these: a new direct call, a caught-and-continued refusal, and a divergent session set.
2. Parity. For every mirrored refusal the charge enumerates, `check` and `prepare-candidate` give the same answer. Build fixtures for P3, P4, P5 and the F1 reproduction.
3. Round 7b:
   - H-2 determinism holds;
   - the new `--battery-probe-fixture-for-test` path (or its equivalent) cannot be used in production. Show what refuses it outside the logical-clock mode;
   - H-4 leaves the paper tool byte-identical to `c6814dd8`.
4. Regressions. Run every test module that imports a file changed in `3e984ecc..a44f0685` (use `git diff --name-only` plus grep) and paste the tails.
5. Same signature. Look for any remaining consumer that decides on battery verdicts outside the seam. Re-grep.
6. The pin proof must be empty: `git diff --stat c6814dd8 a44f0685 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs scripts/paper_anchor_correction_quantified.py`.

**Constraints.**
- Read-only in the repo; /tmp is fine.
- No full discovery.
- No launchctl, powermetrics, sudo, installer or model inference.
- One foreground session.

**Verdict:** MERGE or FIX-FIRST, with every finding tiered BLOCKER / MATERIAL / NIT.
