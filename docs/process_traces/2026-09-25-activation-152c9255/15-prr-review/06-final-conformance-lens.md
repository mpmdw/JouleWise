**Verdict: CONFORMS.** The delta 8cd9e831..2bbcc779 applies the PRR-FINALPASS-01 F2 and F3 texts and the ratified A-R5a-1 texts (PRR-R3-01 §2 Q2) exactly. The only departure is the declared erratum from record 00 item 76, and it does not change the meaning.

## What changed
Five files; the delta touches nothing else:
- the registration file (preregistration_d079_epoch_25g83_rev1.md)
- `docs/decision_log.md`
- the issuer script (issue_calibration_acceptance_generation.py)
- `tests/test_acc_25g83_rev5.py`
- `tests/test_issue_calibration_acceptance_generation.py`

In the registration file only lines 608 and 618 changed; the line count stays at 646.

## Word-for-word checks
I compared each item by script against the quoted ruling text, taking both rulings via `git show origin/docs/2026-09-25-152c9255:…`.

| Item | Result |
|---|---|
| Registration line 608 | The new line equals the old prefix, then the ratified Q2 paragraph, then the unchanged sentence "Launch context sets the sampler cadence; …". It matches **only after** the erratum substitution. Exactly one substitution is involved: the grep example `'<PR-L-MERGE-SHA>\|<TEMPLATE-SHA256:'` becomes `'<PR-L-MERGE[-]SHA>\|<TEMPLATE[-]SHA256:'`. |
| Header parenthetical | Unchanged: `# Revision 5 (2026-09-25; sealing pending PR-L pins)`. This is the exact string the seal instruction says to replace, and the new test replaces it. |
| Line 618 (F2) | Matches exactly: ``disposed as diagnostics under `D-126-disposition-25G83-v3-2026-09-25`,`` |
| Issuer, lines 1283–1289 | Placeholder regex is `<PR-L-MERGE-SHA>\|<TEMPLATE-SHA256:[^>]+>`. The malformed-pin checks are `template at commit [0-9a-f]{40}\b` and `template digests [0-9a-f]{64} and [0-9a-f]{64}\b`. Both refusal messages are unchanged. Everything stays inside the Revision 5 branch. |
| Test fixtures | All match the ruling: `LAUNCH_CONDITION`, `registration_with_launch_pins(commit, night, probe)`, `sealed_registration()` = a×40/b×64/c×64, the unsealed fixture with three placeholders, and the malformed `not-a-commit` fixture. |
| New "rendered-plist digests" case | Present in `test_issuer_refuses_unsealed_launch_context_and_disposes_exact_ids`. The fixture reads `template at commit <40 hex>, rendered-plist digests <64>, <64>, and <64>.` and the issuer refuses it with `pins are malformed`. |
| Decision-log entry | Heading matches exactly and appears once. It sits immediately after the `## D-126 addendum (2026-09-25): Revision 5 corpus…` entry, at the end of the file. The body is the ratified paragraph plus the `Ratification: …§2 Q2.` line, byte-exact. Everything before it in the file is byte-identical. |
| F3 | The dead `probe = subprocess.run(...kern.osversion...)` statement is gone. Compared with `c034a56f`, no diff hunk remains in that region; the other hunks come from earlier commits (historical fixture). The `subprocess` import is still used elsewhere in the file. |

## The erratum (the only deviation)
- **Declared:** record 00 item 76 declares the erratum and says a test will prove that a fully sealed copy passes and greps 0. The test changes do that:
  - `test_sealed_copy_…` is renamed to `test_full_seal_accepts_and_grep_count_zero_while_malformed_refuses`;
  - that test now replaces the header on the sealed copy and asserts `grep -c -E` returns `(1, "0\n")`.
  
  They fall under the declared erratum, so I don't count them as a separate deviation.
- **Seal probe in `/tmp/prr-delta-audit`:** I sealed the live file with:
  - commit `e×40`;
  - the real template digests at PR-L head 99495ba9: night `e62a461b…e5c8` and probe `1570b745…1fd` (these match cold gate P6);
  - the header rewritten to `sealed 2026-09-25 at PR-L merge eeeeeeee`.
- **Results:**
  - Sealed copy: `grep -c -E '<PR-L-MERGE[-]SHA>|<TEMPLATE[-]SHA256:'` gives 0 (rc 1). The issuer's regexes accept it: no placeholder match, and both well-formed patterns match.
  - `test_acc_25g83_rev5` and `test_preregistration_chain_digest` on the sealed tree: **Ran 17, OK.**
  - Unsealed copy: grep gives 1 and the issuer refuses it with "unsealed placeholders".
- **Counterfactual (why the erratum is needed):** with the ratified grep example exactly as written, a fully sealed file still greps 1, and the issuer's placeholder refusal still fires. The ratified text could never be sealed, which confirms the need that item 76 identified.
- **Meaning:** the regex still matches the real tokens, so the erratum preserves the meaning.

## Invariants
- The four D-138 pinned files plus the chain `.zsh` (`powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, `reduce.py`, `calibration_derivation_only.zsh`) are byte-identical to both 8cd9e831 and origin/main 95521871 (`git diff --quiet` rc 0).
- Consumers of the pin sentence across the tree (excluding process traces): only the registration file, the issuer and the rev5 test. No stale `RENDERED-PLIST-SHA256` or `rendered-plist digests` parser remains; the only "rendered-plist digests" strings left are the prose on line 608, the decision-log entry, and the negative fixture.
- No behaviour change beyond the ruled regexes.

## Tests (clean /tmp clone at 2bbcc779, foreground)
`python3 -m unittest tests.test_acc_25g83_rev5 tests.test_preregistration_chain_digest tests.test_issue_calibration_acceptance_generation` → **Ran 131 tests in 57.4 s, OK.**

## Exact fixes required
None.

## Notes, not blocking
- The erratum is flagged in item 76 for the next cold gate to ratify. Until then it is a magistrate reading, not a ruled text.
- Per the FIX-FIRST order, PR #412 must merge before PR-R. R3/R16-a is recorded outside Revision 5 and does not affect this delta.

## Scope
I was read-only on the worktree. My only writes were the `/tmp/prr-delta-audit` clone (seal probe reverted, clean tree) and `/tmp/prr-unsealed.md` and `/tmp/prr-raw-sealed.md`. I used no sudo, launchctl or powermetrics, no background tasks, and did not touch `/Users/edr/code/JouleWise` or `/Users/edr/night-custody`.

The claude.ai Anthropic Economic Index connector needs authorization in claude.ai connector settings; this audit didn't use it.
