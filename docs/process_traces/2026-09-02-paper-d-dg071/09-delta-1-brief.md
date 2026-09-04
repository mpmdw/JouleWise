ORIGIN: claude-code lead (magistrate)
HOP: 1 (never run `claude -p` or any Claude launcher)
GENRE: review
WRITE_SCOPE: []

# Delta re-audit — DG-071/075 producer fix round (commits 681f30ce + a3dadadd on feat/2026-09-02-paper-d)

Read-only (write nothing under the checkout; TMPDIR = a subdirectory you
create under <scratchpad>/). Do NOT run canonical `unittest discover`.
Python: /Users/edr/code/JouleWise/.venv/bin/python.

Prior contract review (luna): <scratchpad>/out/178-luna-paper-d-contract.md — read it
first. The fix seat's report: <scratchpad>/out/180-sol-paper-d-fix1.md.
The delta: `git diff 1baf8c4c..a3dadadd` (two commits: producer+tests, then
the magistrate's re-issued artifact).

Questions, in order:
1. Is every luna-178 finding cured at the production call site (not only in
   tests)? For each: cured / not cured / partially, with file:line.
2. Did the fix round introduce any new defect? Look especially at: the
   absolute path still used as the refusal pin vs the repo-relative locator
   in the artifact (can the artifact now be issued from a checkout where the
   bundle sits elsewhere? should it?); the cross-checkout determinism test
   (does it actually bite — mutate mentally); the exit-2 `record_field_missing`
   test (does it exercise the CLI path or only the function?).
3. Re-run the producer yourself to a TMPDIR path and confirm byte identity
   with the committed docs/paper/round7/dg071-dg075-statistics.json
   (sha256 0ba0efafbdd8d2ec48ea55d08ef3c8121bb139e4fdadc35d0bb1b914c7e148f9)
   and .md. Report the exact cmp/shasum output.
4. Run `python -m unittest tests.test_issue_dg071_dg075_statistics` and
   paste the result line.
5. Update the two draft registry rows in luna-178's report to the new
   artifact sha and the new producer commit/script sha (read them from the
   artifact JSON), and return them verbatim so the magistrate can paste them.

Verdict: DELTA CLEAN / DELTA NOT CLEAN with severity-tiered findings.
Envelope first (claude-codex-report/v1, genre review), then under 60 lines,
file:line for every claim.
