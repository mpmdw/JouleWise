## Fix round 1 delta re-audit, PR-R (3c52518d..62db28b7)

**Verdict: no BLOCKER and no SHOULD-FIX.** All six SHOULD-FIX items (S1–S6), the ten NITs (N1–N10) and both Astra findings (F1–F2) are closed. I found three new NITs, listed at the end. All my work ran in read-only `git archive` extracts under `/tmp/152c9255/prr-delta/`. I did not touch the worktree, the canonical checkout or night-custody.

### Checks I ran

**1. The explicit disposition id is bound end to end, and the bare `D-126` is refused.**
- **Registry:** all 11 rows now carry `D-126-disposition-25G83-v3-2026-09-25` (`configs/calibration/observation_dispositions.json`).
- **Issuer constant:** set to the same id at `scripts/issue_calibration_acceptance_generation.py:383`. The registry reader checks every row against it by exact equality (`:1134`).
- **Prior set:** the successor's `disposing_decision_ids` is now asserted to equal `[DECISION_ID]` (`tests/test_acc_25g83_rev5.py:191`).
- **Decision-log heading:** `## D-126-disposition-25G83-v3-2026-09-25 — …` at `docs/decision_log.md:12176`. It appears exactly once, and the entry's sentence "its decision id is" now names the full id.
- **New test:** `test_decision_log_binds_exact_registry_ids` checks that the entry's table holds 11 content ids and that they equal the registry's rows.
- **Refusal probe (my own run):** I set one row to each of the following. All three were refused with "invalid or duplicate row":
  - the bare `D-126`;
  - the old heading text;
  - the new id with a leading space.
- **Parser safety:** the site's entry regex, `^## (D-\d{3}):`, matches neither the new heading nor the two addendum headings. So `#D-126` still resolves to the original policy entry at line 8481.

**2. The seal-robust fixtures still work after a real seal.**
- In a /tmp copy, I replaced the four placeholders in the actual prereg file with well-formed hex, leaving a placeholder count of 0.
- I then ran `tests.test_acc_25g83_rev5` and `tests.test_preregistration_chain_digest` on that sealed copy: **Ran 17 tests, OK.**
- In that run, the unsealed fixture (rebuilt by regex) still raised "unsealed placeholders", and the `not-a-commit` fixture still raised "pins are malformed".
- The new test `test_sealed_copy_clears_placeholder_refusal_but_malformed_seal_refuses` passes too.
- The seal-step sentence added to the prereg contains no placeholder token of its own.

**3. The pinned-file test pins the right four files.** The four hard-coded digests in `tests/test_acc_25g83_rev5.py:221-225` equal `git show c034a56f:<path> | shasum -a 256` for each file, and equal the files at 62db28b7:
- `powermetrics_fiducial.py`: `386e8254…`
- `uncertainty_evidence.py`: `b583f35a…`
- `adapters/powermetrics.py`: `70f47086…`
- `reduce.py`: `7b9c0d28…`

`git diff c034a56f 62db28b7` over those four files plus the derivation chain `.zsh` is empty. So the N6 import of `PLATEAU_INSET_S` and the N7 import of `REVISION_FIVE_EPOCH` did not modify any pinned file.

**4. r7 validation is still byte-identical.** I re-ran the prior lens's `diff_probe.py` on both c034a56f and 62db28b7:
- **266 of 266 keys are identical.**
- The output also equals the prior lens's 3c52518d output.
- r7's loaded-artifact hash is still `211ed076…`.

**5. S3 and the rest of the scope.**
- `tests/test_preregistration_chain_digest.py` is byte-identical to c034a56f, so S3's guard is restored verbatim. Revision 5 now writes `` `os_build` = `25G83` ``, which that guard's regex does not match.
- Every hunk in the delta maps to a dispositioned item, with one exception (NIT-1 below).

**6. Tests on the fix head.** I ran the brief's eight modules plus `test_docs_freshness` and `test_build_site_parsers`: **Ran 387 tests in 1031.465s, OK (skipped=31)**. `python3 scripts/gen_state.py --check` exited with rc=0. I did not run the full discovery suite.

### Closure by item

| Item | Status | How I confirmed it |
|---|---|---|
| S1 / F1 | Closed | Point 1 above |
| S2 | Closed | Point 2 above (a real seal of a /tmp copy) |
| S3 | Closed | Test file restored verbatim; the pin regex matches only the original line |
| S4 | Closed in effect, with residue | See NIT-1 |
| S5 | Closed | The hashes match c034a56f |
| S6 | Closed in scope | The seal-step sentence is present; the ruling file landing on main remains the magistrate's action |
| N1 | Closed | D-184 addendum cited by text, plus Revision 1/Revision 2 section names |
| N2 | Closed | Text now says "I/SH/D", which matches the table's row order |
| N3 | Closed | Cadence stop now comes before futility |
| N4 | Closed | Delimiter row now has 10 cells |
| N5 | Closed | Docstring now carries the Revision 5 exception |
| N6 | Closed | `Decimal(str(0.25))` equals `Decimal("0.25")`; the refusal message is unchanged |
| N7 | Closed | The bracketing module's dict is identical to the removed copy; the test patch targets the issuer's own binding, so it still takes effect |
| N8 | Closed | The registry is read, and `disposing_decision_ids` emitted, only under Revision 5; historical candidates have the same shape as at c034a56f |
| N9 | Closed | The two addenda have their own dated headings; record 37 is cited |
| N10 | Closed | Revision 5 tests use r7 as predecessor; a non-r7 predecessor is refused, and a test covers it |
| F2 | Closed | Stale simulation docstring fixed |

### New findings

**BLOCKER:** none.

**SHOULD-FIX:** none.

**NIT-1: the S4 revert left a dead statement.** At `tests/test_issue_calibration_acceptance_generation.py:344-347`, `probe = subprocess.run([str(issuer.SYSCTL_PATH), "-n", "kern.osversion"], …)` is still there. Nothing uses it, it runs one extra real `sysctl` call, and it does not exist at c034a56f. The seat removed only the `if … skipTest` lines.
- **Fix:** delete lines 344-347 so the `DeskEpochWatchTests` hunk matches c034a56f exactly.

**NIT-2: no test covers the bare `D-126` refusal.** My probe shows the code refuses it (equality at `scripts/issue_calibration_acceptance_generation.py:1134`), but no test pins that behaviour.
- **Fix:** in `tests/test_acc_25g83_rev5.py:test_registry_rejects_unruled_or_duplicate_dispositions` (around line 86), add a case that sets `row["disposing_decision_id"] = "D-126"` and asserts "invalid or duplicate".

**NIT-3: the prereg still names the bare id.** `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:618` says the eleven values were "disposed as diagnostics under D-126". That is the only place in Revision 5 that still names the bare id; the registry, issuer and decision log all use the explicit one.
- **Fix:** change it to "under `D-126-disposition-25G83-v3-2026-09-25`", and do it before sealing, because the arm digest pins the prereg text.

### Residual risk
- The new sealed-copy test builds its sealed text from the live file by regex, so on its own it never exercises a seal of the live file. My manual seal run in point 2 covers that.
- The production validator never reads `disposing_decision_ids`. The issuer is the only enforcer of the disposition id. This was already true before the fix round and was ruled acceptable under R4(d); the delta does not change it.

One environment note: the claude.ai Anthropic Economic Index connector needs authorization before its tools can be used. You can do that in your claude.ai connector settings. Nothing in this audit needed it.