# BFG-S S0: delta re-audit of fix rounds 3, 3b and the lead bench commit (read-only)
WRITE_SCOPE: []

**Candidate.** Commit `783a09be` on `feat/2026-09-26-bfgs-s0-helper-fence`. Your working tree is that commit. It is S0 round 3 (`aa90f349`), round 3b (`980138c7`), a clean merge of main `5d5a0b75` (which contains A309, PR #426), and the lead bench commit `783a09be`.

**What to review.**
- The whole S0 change against current main: `git diff 5d5a0b75 783a09be -- joulewise scripts tests`.
- Concentrate on what changed since the last lens round (the lenses ran at `26ab7234`): `git diff 26ab7234 980138c7 -- joulewise scripts tests` (rounds 3 and 3b) and `git show 783a09be` (bench).

**Authorities**, in precedence order. All paths are under `/Users/edr/code/JouleWise-wt-bk-8e43cfa7/docs/process_traces/2026-09-26-activation-6bec2aa6/`:
1. Cold addendum 2, amendments 20–28: `60-bfgs-s0/40-addendum2/21-coldgate-fable-addendum2-ruling.md`. Amendments 26 and 28 are owned by S1/S2 and are out of S0 scope unless S0 touches them.
2. Final texts v1.1 §4, texts 1–4, 15, 17 and T1–T4: `40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md`.
3. The round-3 fix contract C1–C13: `60-bfgs-s0/41-fix-contract-round3.md`.
4. The lead rulings on the round-3 early return: `60-bfgs-s0/44-lead-rulings-round3.md`.
5. The magistrate gap-fill on the bundle span: `60-bfgs-s0/20-ruling-bundle-span.md`.

The prior lens reports (`60-bfgs-s0/31-*.md`, `32-*.md`, `33-*.md`) list the findings rounds 3 and 3b were meant to close.

**Stakes.** `authenticate_pair` and its wrappers will be the only gate between a battery-confounded measurement window and a claim-bearing number, for every non-derivation window kind. A pair that passes when it should not produces a false number.

**Required checks.**
1. **Closure.** For each C1–C13 and each addendum-2 amendment in S0 scope, state CLOSED, OPEN or REGRESSED, with executed evidence.
2. **Same-signature statement (mandatory).** Round 3 closed a BLOCKER class: *malformed or unreadable input masks a custody failure* (a mismatching digest raised `CustodyFailure`, but appending a malformed line to the same journal returned `pass`). Search every input path that S0 reads — `session.json`, `metadata.json`, `events.jsonl`, `rounds.jsonl`, `instrument_evidence.json`, the raw ioreg files, spans and monotonic fields — for any input that downgrades what should be a custody failure to a status, or any status to `pass`. State plainly whether the class recurs: "same signature: yes/no".
3. **Freeze fence (new finding at the bench).** Round 3 had widened the frozen `CustodyFailure.__init__` to accept a string, because C1/C3/C4 dictated `CustodyFailure("<str>")`, and had pinned its own modified bytes. The bench commit restores `CustodyFailure` byte-identical to main and adds `CustodyUnreadable(CustodyFailure)` for the five string-detail raises. Verify:
   - every definition in the `FROZEN_ROOTS` transitive closure is byte-identical between `git show 5d5a0b75:joulewise/battery_float.py` and the candidate, and every pin equals the base hash (recompute it yourself from the base file);
   - no consumer depends on `CustodyFailure.failures` being non-empty, or on the message prefix `custody failure:`, in a way that the subclass breaks;
   - no other frozen definition was edited in rounds 3 or 3b.
4. **Guards (C8, C10, ruling 44).** Check that the `REPLACE_CALL_ALLOWLIST` is content-keyed and shrink-only, and that each C10 guard has a mutation proof that actually turns it RED.

**Your lens** is one of:
- **EXECUTION** (Sol): run the focused suites (`tests.test_battery_float`, `tests.test_battery_float_consumers`, `tests.test_battery_float_sweep`, `tests.test_evidence_night`, `tests.test_night_kinds`), then attack by execution in `/tmp`. Report every accepting counterexample, with its exact reproduction.
- **CONTRACT** (Opus): go line by line against the authorities above. Check that nothing outside S0's scope moved.

Classify each finding BLOCKER, SHOULD-FIX or NIT, with executed evidence and the exact fix. Do not edit repository files. The sandbox cannot run the live `pgrep` census probe; a failure there alone is not a finding.
