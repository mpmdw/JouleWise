# BFG-S S0: delta re-audit of fix round 4 (read-only)
WRITE_SCOPE: []

**Candidate.** The round-4 commit `c9081c6e` on `feat/2026-09-26-bfgs-s0-helper-fence`. Your working tree is that commit; `git log -1` names it. Review:
- `git diff 783a09be HEAD -- joulewise tests` (round 4);
- `git diff 5d5a0b75 HEAD -- joulewise scripts tests` (the whole of S0 against main).

**Authorities.** The round-4 brief and the ruled texts it quotes are the whole contract. All paths are under `/Users/edr/code/JouleWise-wt-bk-f8d6cab1/docs/process_traces/2026-09-26-activation-f8d6cab1/10-s0-delta/`:
- the brief: `40-seat-brief-round4.txt`;
- the addendum-3 ruling: `20-coldgate/10-coldgate-fable-ruling.md` (amendment 29, T16, and the §4 class table);
- the erratum: `20-coldgate/30-erratum/21-coldgate-fable-erratum-ruling.md` (amendments 30 and 31 as re-issued, T30-a…j, and probes P-A, P-B and P-D);
- the seat's report: `41-seat-report-round4.md`.

Earlier S0 authority, cited by the ruling: `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md` (Final texts v1.1, text 2).

**Stakes.** These wrappers are the only gate between a battery-confounded or evidence-lost window and a claim-bearing number. Two rounds have already failed with the same signature, and a third recurrence goes back to a cold gate. Two honest-failure shapes must never become custody: P-A (a `sampler.json` parse failure between the two appends) and P-B (a killed collector's provisional rows). Any loss after the collector finished must be custody.

**Required checks.**
1. **Closure.** For amendments 29, 30 (erratum) and 31 (S0 clauses), and for S-1 and S-2, state CLOSED, OPEN or REGRESSED, with executed evidence. Include each T16 and T30 row.
2. **Same-signature statement (mandatory).** Against the class table in ruling §4, extended by the erratum: does any input S0 reads still convert a read or decode failure into an empty value, or a custody failure into a status or `pass`? Try at least these:
   - deleting, emptying, truncating, symlinking or duplicating the key of each of `session.json`, `rounds.jsonl`, `metadata.json`, `events.jsonl` and `instrument_evidence.json`, in each envelope shape;
   - removing `end_stamp` or `error_class` to move a shape;
   - a bool, string or negative `journal_rows`;
   - a directory in place of a file.

   Write "same signature: yes/no" plainly.
3. **The honest-failure side.** P-A and P-B shaped envelopes must not raise. A shape-(iii) journal that is absent, empty or `{` must give `evidence_missing: quiet span unavailable`. The historical population (no `battery_float` key) must be unchanged. Report any honest shape that now raises.
4. **Freeze fence.** Every `FROZEN_ROOTS` closure definition is byte-identical to `git show 5d5a0b75:joulewise/battery_float.py`, and every pin equals the hash of the base segment under the test's own segment rule. Recompute this yourself.
5. **Guards.** The S-1 decorator and rebinding mutations turn the test RED, and the S-2 forms (`copy.replace`, `from copy import replace`, `x.__replace__(...)`) are flagged.

**Your lens** is one of:
- **EXECUTION** (Astra): run `tests.test_battery_float`, `tests.test_battery_float_consumers`, `tests.test_battery_float_sweep`, `tests.test_evidence_night` and `tests.test_night_kinds`, then attack by execution in `/tmp`. Report every counterexample that is accepted wrongly, and every honest shape that is refused wrongly, each with an exact reproduction.
- **CONTRACT** (Opus): go line by line against the ruled texts, and check that nothing outside WRITE_SCOPE moved.

Classify each finding BLOCKER, SHOULD-FIX or NIT, with executed evidence and the exact fix. Do not edit repository files. The sandbox cannot run the live `pgrep` or `sysctl` probes; a failure there alone is not a finding.
