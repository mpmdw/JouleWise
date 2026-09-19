# Record 38a — lead triage of Opus counter-review 38 (GENERATOR-HEAD-FILE-BYTE-PIN-01 at `842e5b39`) and the post-review bench commit (2026-09-19 11:3x PDT)

| # | Severity | Disposition |
|---|---|---|
| F1 | should_fix | ACCEPTED, fixed at the bench (bench-vs-session threshold: a three-line wrap in two identical hunks): the pin's `json.loads` is wrapped so a corrupt file refuses `ledger head pin is not valid JSON: configs/calibration/calibration_ledger_head.json` on the ordinary `main` ValueError path; regression `test_corrupt_pin_json_refuses_naming_the_file` added (both generators). The counterfactual the seat and both refuters missed: neither ran a corrupt pin through the real CLI. |
| N1 | nit | ACCEPTED, fixed with F1: the shape refusal now names the path (`ledger head pin shape invalid: <pin rel>`), a deliberate one-token deviation from ruling 10's verbatim message that adds diagnosability and changes no semantics; the regressions' expected strings updated. Recorded so the ruling-vs-code diff is explained. |
| N2 | nit | Docstring under-describes the check — queue data; the comment block above the function carries the full statement (37c C2). |
| N3 | nit | Preserve mode never reaches the head check — parity with the deleted byte pin (the drift loop is also skipped in preserve mode), not a regression; no change. |
| N4 | nit | Misleading `pin` local name in the manifest regression — queue data for the next touch of that module. |

Clean on the hard questions (38): no exception type bypasses the `main` refusal path (rc 1, no traceback across four counterfactuals); `--check` runs the head check via `check_current → generate`; ordering drift loop → head check → first write with nothing between; emitted bytes independent of the pin's bytes and sequence (176 / 76 / 999 → identical digests); no committed pack stranded; six of ten regressions detect whole-call deletion and the four survivors are legitimately independent.

Post-review commit: one. Fresh eyes (row 10): seat 40 (read-only, detached worktree at the new head, real-CLI corrupt-pin execution).
