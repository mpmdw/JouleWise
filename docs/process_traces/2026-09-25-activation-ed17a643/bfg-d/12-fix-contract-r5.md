# BFG-D fix round 1 (seat round 5): lead-written FIX contract with dictated closure shapes

Magistrate ed17a643, triage of the three lenses on `df33888f`:
- Sol 6.0 xhigh execution lens (`11-review/01`): FIX-FIRST, 2 BLOCKER and 2 MATERIAL.
- Astra 6 high science/bypass lens (`11-review/02`): FIX-FIRST, 2 BLOCKER and 5 MATERIAL.
- Opus 5.5 contract lens (`11-review/03`): MERGE, 1 MATERIAL.

The findings are merged below. Each FX item states the defect, the required closure shape, and the defect-shaped test that must fail on `df33888f` and pass after the fix. Before you change code, reproduce each test's failure at `df33888f` in a /tmp copy, and paste the RED output and then the GREEN output.

**FX-1 (Astra B1, BLOCKER): the parser accepts a malformed or structurally wrong object.**
- Closure: `battery_float` parsing accepts only a stdout that holds exactly one object header line of the form `+-o AppleSmartBattery  <...>`, with the class name exactly `AppleSmartBattery`, and that object's property block must open with `{` and close with `}`.
- Required properties are read only from that block's top-level property lines, meaning the indentation of the block's first property line.
- Any other structure is a probe error, reached through the existing `night_probe_error` path. That includes a missing closing brace, another class, required keys present only at a deeper indentation or only inside a nested dictionary, and any content after the closing brace other than whitespace.
- Tests: Astra's three counterexamples (missing final brace; another class substituted; required properties only inside a nested dictionary), each driven through `night_gate.evaluate_night`, `evaluate_dynamic_hard` and `validate_window`. Each must be RED at `df33888f`.

**FX-2 (Astra B2, BLOCKER): the ruled harvest order cannot complete.** `battery-verdict` requires a committed pin, but §4.9 step (iv) commits the pin together with the verdict.
- Closure (a lead deviation from the literal §4.2 text; the cold Fable final pass will rule on it):
  - `battery-verdict` loads the ledger in `read_replay` mode with `require_committed_pin=False`.
  - It then refuses unless the working-tree head pin file `configs/calibration/calibration_ledger_head.json` authenticates against the ledger's computed head (same sequence and digest), and it records that pin in `ledger_head`.
  - `load_committed_verdict` adds check 5: the single adding commit of the verdict file also changes `configs/calibration/calibration_ledger_head.json`, and the pin blob at that commit carries the record's `ledger_head` sequence and digest. Otherwise it raises NoRecord `verdict not committed with its ledger head pin`.
- Test: the COMPLETE §4.9 sequence, end to end through the real CLIs on a fixture:
  1. terminal session, pin updated but uncommitted;
  2. `battery-verdict` exit 0;
  3. one commit of pin plus verdict;
  4. `check` and cadence and `prepare-candidate` succeed.
  Also: a verdict committed in a separate commit from the pin must be refused by every consumer.

**FX-3 (Astra M1 = Opus M-1, MATERIAL): the history check misses modifications that arrive through a merge.**
- Closure: `load_committed_verdict` uses `git log --full-history --format=%H -- <path>` and `git log --full-history --diff-filter=A --format=%H -- <path>`. It requires exactly one commit in the full history to touch the path, and that commit must add it. Any other result is NoRecord.
- Test: commit a verdict; on a branch, modify it and restore it; merge; the consumer refuses. RED at `df33888f`.

**FX-4 (Sol F1 BLOCKER = Astra M2 MATERIAL): the cadence report reads capture paths the caller chose.**
- Closure: `report_window` derives the capture inventory itself from the authenticated session's finalized ledger rows (their custody directories and `powermetrics.plist`). It authenticates each plist's bytes against the digest the ledger row or its hashed evidence records, and computes cadence only over those files.
- The `--window LABEL=PATH` argument may remain for labelling, but the report refuses (exit 2) unless the set of plist paths under PATH equals the derived set exactly.
- Update the runbook §2.2a invocation to match.
- Tests: Sol's swap (`--session W1=W2` with W1's plist) refuses. The runbook's directory argument containing another session's captures refuses. A tampered plist refuses.

**FX-5 (Sol F2, BLOCKER): the dry run opens B-bearing member evidence before the verdict gate.**
- Closure: in `registration_dry_run`, for a Revision-5 session whose committed record is absent, fails to authenticate, disagrees with the recomputation, or meets a custody failure, emit the blocker line and do not read that session's member evidence or any other B-bearing file (`continue` before `_read_member_evidence`).
- Test: patch or trace `_read_member_evidence`, or open-record the file reads; with no record, it is never called for that session. RED at `df33888f`.

**FX-6 (Sol F3, MATERIAL): `check` answers "admissible" when a computed non-pass session is omitted.**
- Closure: the dry run computes the same set S as the issuer (§4.4, including exemptions (i) and (ii)) and emits `blocker: computed non-pass session omitted: <id>` for any S member with a recorded non-pass verdict that is not named, so the dry run agrees with `prepare-candidate`.
- Test: Sol's fixture (W1 charging, W1′ and W2 clean, `check --session-ids W1-prime --session-ids W2`) gives a non-zero exit and "not admissible". RED at `df33888f`.

**FX-7 (Sol F4 = Astra M4, MATERIAL): three consumers skip the registration-digest identity check.**
- Closure (conformance with §4.3):
  - `check` requires `--preregistration` and `--preregistration-sha256` whenever any named or computed session is Revision-5; without them it emits a blocker and exits non-zero.
  - The cadence report gains a required `--preregistration-sha256`.
  - `issue_epoch_continuation` gains a required `--preregistration-sha256` for Revision-5 rows.
  - All three pass the digest to `load_committed_verdict`.
- Tests: for each consumer, a wrong digest refuses and a missing digest refuses.

**FX-8 (Astra M3, MATERIAL): the documented cadence CLI fails with ModuleNotFoundError.**
- Closure: add the same repository-root `sys.path` bootstrap the issuer uses.
- Test: a subprocess runs `python3 scripts/calibration_cadence_report.py --help` from a clean environment (no PYTHONPATH, cwd = /tmp) and exits 0.

**FX-9 (Astra M5, MATERIAL): the production t0 probe gives ioreg a 30 s timeout.**
- Closure: the production probe executor used by the night gate (`scripts/run_night.py` `_probe_runner`, or wherever `Probes.run` is bound in production) applies `battery_float.PROBE_TIMEOUT_S` (10 s) to `IOREG_BATTERY_ARGV`. One home for the override.
- Test: the production wiring with a mocked subprocess records `timeout=10` for the ioreg argv and the unchanged timeout for every other argv. RED at `df33888f`.

**FX-10 (Sol F5, MATERIAL): test 8 cannot reach its ruled assertion.** No code change. HARVEST-VERDICT-FINAL-01 §5.1 AFFIRMED F-1: the no-row outcome is the reachable one, and the post-observation is guarded by the writer bracket test (Sol confirmed it kills the mutation). Add one sentence to test 8's docstring naming the bracket test as the post-observation guard.

**FX-11 (NITs).**
- The liveness-test docstring 600 → 610 s arithmetic. Keep 610 s: all three lenses affirm it as correct for the implemented per-site timeouts.
- Fixture trailing whitespace: do NOT alter the real ioreg capture bytes. If the synthetic fixtures carry whitespace only because they are derived from the real bytes, leave them. Add a `tests/fixtures/battery_float/.gitattributes` with `* -whitespace` so `git diff --check` does not flag capture fidelity.
