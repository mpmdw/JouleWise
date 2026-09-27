# Design consult ISSUANCE-CUSTODY-OUTSIDE-REPO-01: how issued calibration members name custody that lies outside the repository

ROLE: blind consult seat, read-only, with explicit license to disagree with the scout, the lead, and every option offered. Do not read other seats' answers.
WRITE_SCOPE: []
Write nothing in any repository; scratch only under /tmp/custody-consult-<your-seat>-77b1bee2/. No git fetch/pull/checkout. Do not call Claude or Codex by any route. No subagents.
OUTCOME-BLIND (binding): open no measured value (no B / `b_fiducial_s`, no ledger row value fields, no manifest.json / instrument_evidence.json value fields). You may read `custody_locator`, `attempt_id`, `session_id`, sequence/digest fields, and file paths, names and sizes.

**Working tree:** `/Users/edr/code/JouleWise-wt-custody-scout-77b1bee2` (origin/main `670756f3`). W2 measurement root, read-only (HEAD `722f7bd1`, its ledger holds W1 and W2): `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2`. The custody roots, read-only and never moved: `/Users/edr/night-custody/d079-epoch-25g83-derivation-w{1,2}-20260927/`.

**Forcing problem.** Epoch 25G83's calibration corpus is W1 + W2: 12 valid captures, exactly the floor, with no further window permitted.
- `scripts/issue_calibration_acceptance_generation.py prepare-candidate` will refuse, value-blind, before any statistic.
- The reason: every member's custody lies under `/Users/edr/night-custody/…`, outside every git checkout, and `_repo_relative_custody` (:896–912, called at :1244) requires repo-relative `source_directory` paths.
- The runbook deliberately put custody there and forbids moving it. Copying, symlinking, re-rooting or creating a git repository above it are ruled out as cures.

The scout's full evidence and two designs are in `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-77b1bee2/50-custody-outside-repo/11-sol-scout-report.md` (read it):
- **A:** an artifact-level logical `source_root` descriptor plus `--custody-root`, with the verifier and reissue taking a caller-supplied archive location.
- **B:** per-night logical roots.

**Answer:**
1. Which design? A, B, or your own C. Verify the scout's consumer map (issuer, `tests/verify_calibration_acceptance_corpus.py`, `scripts/reissue_calibration_acceptance.py`, the `joulewise/calibration_bracketing.py` validator and loader, the D-138 transaction) and correct it where it is wrong.
2. The minimum change set: exact sites; the artifact schema delta; how r6/r7 stay valid unchanged; what a future reader with only the repository plus the archived night roots can re-verify, and how.
3. Science and custody risks. Could any design let a choice depend on measured values? Does the corpus's evidential chain (the ledger row → `instrument_evidence.json` digest → raw bytes) stay intact? What about the iCloud-offload and archive plans for custody after issuance, and archive relocation?
4. Defect-shaped tests: RED before the change, GREEN after, and the refusal cases (undeclared root, `..`, absolute path, symlink escape, wrong basename, a one-byte mutation).
5. Anything that would make you prefer NOT to change code. For example: is there an already-sanctioned mechanism the scout missed?

Report: tier any findings BLOCKER / SHOULD-FIX / NIT, give file:line evidence and executed probes, and end with the line `RECOMMEND: A|B|C`.
