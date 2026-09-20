# Record 13 — fresh-eyes delta re-audit of fix round 1 (`7472a7c7..80e715ba`), CENSUS-SELF-MATCH-01, 2026-09-20 ≈04:33 PDT

Auditor: Opus 5 subagent (read-only; mutations only in a /tmp copy). Verbatim report:

**VERDICT: FIX-NEEDED — one should-fix, docs-only (no code blocker; mutant is killed, no assertion weakened).**

1. **S1 should-fix — `docs/process/NIGHT_HANDBACK.md:254-255`: the prescribed pre-arm verification cannot be performed.** "Verify in `events.jsonl` that the watchdog's census rows carry the bracketed argv" — `append_census_event` (`scripts/magistrate_watchdog.py:1291-1307`) writes only `schema/kind/sequence/epoch_s/exit_code/empty/stdout/stderr`; there is no `argv` field, and no watchdog event anywhere records the pattern (`grep AGENT_CENSUS|\[c\]odex scripts/magistrate_watchdog.py` → no hits). The operator will look and find nothing. Replace with a checkable test (e.g. `pgrep -lf magistrate_watchdog` → confirm the process's checkout is at/after the fix, or `ps -o lstart` vs the relaunch time), or add `argv` to the census event.
2. **Nit — `NIGHT_HANDBACK.md:250`:** "binds `AGENT_CENSUS_ARGV` at import" is mechanically imprecise. `scripts/magistrate_watchdog.py:39-45` imports `agent_census` (the function); the constant is read per call from module globals at `:398`. Conclusion is unchanged and correct — the running process holds the pre-fix *module*, so relaunch is required either way.
3. **Nit — `NIGHT_HANDBACK.md:257`:** "prewindow_check.sh is a bench tool … never inside acquisition" is accurate (it is a `capture_t0_step.py:414-421` bench ceremony step, frozen/validated at `arm_readiness_evidence_t0.py:913-929`), but the paragraph omits *why* it is load-bearing: the script detects via `ps aux | grep -E "codex|claude|t3|…"` (`scripts/prewindow_check.sh:149`), and the **new** bracketed pattern matches that grep child's argv (verified: `re.search("[c]odex|…", "grep -E codex|claude|t3|…")` → True). One clause would replicate the constraint.
4. **Nit, same-signature — `tests/test_agent_census_concurrency.py:159`:** skip message still says "2 x 1,000 old-pattern probes" after 1000→300. Same stale-number class as nit 3 that this round fixed.
5. **Nit — `tests/test_night_gate.py:296`:** the new name names one constant, but the body asserts seven production argv constants (`:296-315`); the rename trades one inaccuracy for a narrower one.
6. **Verified correct:** "the reverse is not true" — old `codex|claude|t3` vs new-pattern pgrep line → False; new vs old-pattern line → True. Handbook change is ONE hunk (`@@ -244,10 +244,20`); all ten `## Executed —` blocks (first heading→EOF, 33 276 B) and the `ARM-RETRY-POLICY v1` region (lines 68-144, 9 311 B) are byte-identical `cmp` between `e1e7d6a7` and `80e715ba`; lines 1-67 and 145-239 identical too.
7. **No weakening (item 4):** the driver line is strictly stronger; plain-foreign coverage is retained by `test_run_night.py:983` (`"20 claude"`, asserts bracketed argv). Full modules green: `tests.test_night_gate tests.test_run_night tests.test_arm_census tests.test_quiet_admission` → **Ran 335 tests … OK**.

**Item 1 tails (/tmp/census-delta-audit; mutant = drop `/usr/bin/pgrep` stdout lines, emptied success → exit 1):**
Unmutated: `Ran 2 tests in 0.221s / OK`.
Mutated — BOTH die:
```
ERROR: test_census_does_not_match_peer_argv (command='/usr/bin/claude -p inspect /usr/bin/pgrep')
  test_night_gate.py:378 self.assertEqual("night_refused_agent_present", refusal.reason)
  AttributeError: 'NoneType' object has no attribute 'reason'
FAIL: test_foreign_agent_alongside_peer_still_aborts_chain
  test_run_night.py:977 AssertionError: 4 != 0 : {'aborted_reason': None, … 'verdict': 'GO'}
Ran 2 tests in 0.241s / FAILED (failures=1, errors=1)
```
Mutant reverted; `cmp` confirms `/tmp` copy's `night_gate.py` == `80e715ba`.

**Item 3 tail (real pgrep available; instrumented counters added to the /tmp copy only):**
```
test_synchronized_peer_censuses_do_not_match ...
NEW-PATTERN SELF-MATCHES: 0 of 300 rounds
OLD-PATTERN CONTROL HITS: 300 of 300 rounds
ok — Ran 1 test in 21.731s
```
Uninstrumented module run: `Ran 3 tests in 22.605s / OK`. 300 rounds is decisive with full margin; the docstring's "bench 2026-09-20: 300/300 hits" reproduces exactly. No file in `/Users/edr/code/` was modified.

## Magistrate disposition (04:36 PDT) → fix round 2 `70637c31` (docs + two test strings)
S1 accepted: the paragraph now verifies the watchdog PROCESS (checkout contains the fix via `merge-base --is-ancestor`; process start time postdates the checkout reaching the fix), since the census events carry no argv. Nits 2–5 accepted as written. Round 2 signature: the same paragraph, second correction (round 1 = incomplete, round 2 = unverifiable instruction) — the defect set shrank to prose under executed evidence; a third correction of the same paragraph would go to a consult, not a round 3. Round-2 modules at the bench: `tests.test_night_gate` + `tests.test_agent_census_concurrency` → OK. Final fresh-eyes pass on `80e715ba..70637c31` = record 14.
