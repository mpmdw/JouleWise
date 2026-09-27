# BFG-S S0 (helper and arm fence): review lens charge (read-only)
WRITE_SCOPE: []

**Candidate.** Commit `26ab7234` on `feat/2026-09-26-bfgs-s0-helper-fence`. Your working tree is that commit. Review `git diff 64e39bb9 26ab7234` (8 files).

**Authority.** The ONE authority is cold gate BFGS-DESIGN-01 addendum Final texts v1.1 §4: texts 1–4, 15, 17 and test obligations T1–T4. It is at `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md`. Also read:
- the magistrate gap-fill on the bundle span: `.../60-bfgs-s0/20-ruling-bundle-span.md`;
- the seat briefs `00-seat-brief.txt` and `21-seat-brief-round2.txt`, and the reports `10-seat-report.md` and `22-seat-report-round2.md`, all in the same directory.

**Known and not a finding.** The `FROZEN_FUNCTION_SOURCE_SHA256` pin table will be regenerated after a rebase onto the A309 merge (PR #426 changes `load_committed_verdict`). Findings about pin *values* are out of scope; findings about the pin *mechanism* are in scope.

**Context.** `authenticate_pair` and its wrappers will be the only gate between a battery-confounded measurement window and a claim-bearing number, for every non-derivation window kind. The arm fence must stop a quiet-predicate-evidence night from arming before its brackets exist. A pair that passes when it should not is a false number. A fence that can be bypassed arms an unbracketed window.

**Your lens** is one of:
- **EXECUTION** (Sol or Astra): run the tests yourself, then attack by execution in /tmp.
  - Build record and raw fixtures that pass when they should not: wrong phase, identity swaps, a pre/post swap, a raw-path traversal (`../`), symlinked raw files, a digest-case mismatch, a non-int or bool monotonic, NaN or inf wall times, duplicate JSON keys, and a span that is equal, reversed or of the wrong type.
  - Test custody-versus-status precedence.
  - Test the fence through `evidence_night.check` with every payload kind, including an unknown kind, a None payload and an attribute-missing NightKind.
  - Report every accepting counterexample.
- **CONTRACT** (Opus): line by line against texts 1–4, 15, 17, T1–T4 and the gap-fill. Check that nothing outside S0 moved: no frozen function edited, no frozen-source pin, no controller or bundle_read change. Check the guard allowlist and self-test, and the sweep coverage.

Classify each finding BLOCKER, SHOULD-FIX or NIT, with executed evidence and the exact fix. Do not edit repository files.
