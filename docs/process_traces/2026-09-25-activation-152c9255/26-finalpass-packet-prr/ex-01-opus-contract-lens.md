# PR-R contract lens (Opus 5.5): `feat/2026-09-25-acc-registration-rev5` @ 3c52518d vs c034a56f

**Verdict: no BLOCKER. Six SHOULD-FIX items and several NITs.** Every clause the ruling dictates is present in the diff with the wording it dictates. Nothing changes behaviour for historical epochs, and I proved r7's validation is unchanged byte for byte (§3). The main problems are traceability and test robustness:

- the disposing-decision id `D-126` does not point at the new entry;
- sealing Revision 5 will break a new test;
- one existing test guard was weakened;
- a test that is not part of the ruling now skips itself.

## 1. The magistrate's question: is the `D-126` id unambiguous?

**No. It binds the decision number, not the new entry.**

- Every row of `configs/calibration/observation_dispositions.json` carries `"disposing_decision_id": "D-126"`.
- The issuer hardcodes the same value: `DISPOSITION_DECISION_ID = "D-126"` (`scripts/issue_calibration_acceptance_generation.py:381`).
- The successor's prior set records only `"disposing_decision_ids": ["D-126"]`, a single top-level list (`:1741`).
- In the decision log, `D-126` resolves to the 2026-08-07 U2 synthesis entry at `docs/decision_log.md:8481`. That is the only heading matching the site's `## D-NNN:` entry pattern, and it owns the `#D-126` anchor.
- The new entry is headed `## D-126 disposition, epoch 25G83 v3, 2026-09-25` (`:12176`) and asserts "its decision id is `D-126`". That is self-consistent but not unique: any later D-126 disposition for another epoch or mechanism would carry the same id.
- No test ties the entry's 11-row table to the registry.

The content ids themselves are exact. I recomputed all 24 n1/n2 evidence directories under `/Users/edr/night-archive/…20260919…` with `content_id_from_artifact_hashes`: exactly 11 are `valid`, their set equals the registry, and each maps to the B value in the decision-log table. The binding problem is only which decision entry the id resolves to.

The ruling leaves the id's value open: R4(b) names only the field `disposing_decision_id`. R4(a) names the entry.

- **SHOULD-FIX S1.** Set `disposing_decision_id` (all 11 rows) and `DISPOSITION_DECISION_ID` to the exact heading text, `D-126 disposition, epoch 25G83 v3, 2026-09-25`. Change the entry's sentence "its decision id is `D-126`" to match. Update `tests/test_acc_25g83_rev5.py:44`. Add a test that `docs/decision_log.md` has exactly one line equal to `## ` plus that id, and that the backticked 64-hex ids in that entry's table equal the registry rows carrying that id (11).
- Also checked: no qpe01 rows need disposing. The qpe01 archives for 09-20, 09-22 (×2) and 09-23 contain no `instrument_evidence.json`. The earlier n1 archives (09-13/15/16/17) contain no evidence files at all.
- One residual I could not check: the canonical ledger is off-limits to this lens. If any other valid 25G83/v3 row exists there, A-7 refuses at issuance, which fails closed.

## 2. Ruling conformance, clause by clause

**R5 Revision 5** (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:600-647`)

| Element | Status | Notes |
|---|---|---|
| Header | ✓ | `# Revision 5 (2026-09-25; …` |
| STATUS | ✓ | Revision 4 held at `acc-v4-fallback` = `ea10e3c8` |
| Authority line | ✓ | What it amends (Revision 2 equivalence/PASS/FAIL, Revision 1 Stopping, dry-run outputs, screen challenge), the r6→r7 reading, and Revision 3's chain digest are all stated. See N1 on the missing locations. |
| (a) | ✓ | Six fields, v3, operating condition, reason |
| (b) | ✓ | |
| (c) | ✓ | |
| (d) | ✓ | Futility <6/12 |
| (e) | ✓ | |
| (f) | ✓ | All 11 values match P1 and the archive. See N2 on the table order. |
| (g) | ✓ | 16.3 % |
| (h) | ✓ | |
| (i) | ✓ | |
| (j) | ✓ | See N9 |
| (k) | ✓ | |
| (l) | ✓ | The ruling writes "strict S ≥ C"; the PR writes "strict S < C". The PR's reading is the intended one (the ruling's is a typo). Leave the text; note it. |
| (m) | ✓ | Verbatim |
| (n) | ✓ | |
| (o) | ✓ | |

**R4** ✓:
- (a) The entry heading matches exactly. The mechanism string is verbatim, both in the registry and in the issuer's equality check.
- (b) The registry exists.
- (c) A-7 excludes registered content ids (`:1378`), and A-7 is the only consumer.
- (d) The successor's prior set records the disposing id, and the issuer refuses if any disposed id is missing from the prior set (`:1524-1532`).
- (e) Covered by `test_issuer_refuses_unsealed_launch_context_and_disposes_exact_ids`: empty registry → refuses; registry present → issues; prior set contains all 11; bracketing returns `fresh`.

**R9** ✓:
- The predicate is `target_epoch == REVISION_FIVE_EPOCH`, a dict equality over exactly the six fields with `PROTOCOL_ID` (v3 on main). Every issued artifact's `identity_epoch` has exactly those six keys.
- The text test is `"# Revision 5 ("` (`:1283`).
- Futility is **6** (`:1332`).
- `PROTOCOL_V3_ID`, `R8_ACCEPTANCE_ID`, `_registered_protocol_pin_matches` and `protocol_v4` are absent from both the diff and the tree.
- `git diff --quiet c034a56f 3c52518d` over the four pinned files is clean.
- Salvage is confined to the allowed set: stale-number audit, dry-run `valid=`, `_derivation_frame_cadence`, zero-headroom arithmetic.
- The W3 check now counts `classification_disposition == "valid"` rather than v4's retained members. That matches R5(d)'s "dry run shows < 12 valid" better than v4 did.
- Both addenda carry "epoch 25G83/v3 under registration Revision 5" and cite the ruling.

**R10** ✓: all four models, the finite-sample bounds, and no equivalence branch. See N4 for a formatting defect in the report.

**R17** ✓: `scripts/calibration_cadence_report.py` imports nothing from `joulewise`, and the chain is unchanged. The seat's smoke run (n1: 247.9 ms median of capture medians, 353.3 ms maximum, STOP) matches the prereg's D row.

**Placeholder refusal.** It blocks issuance: `<PR-L-MERGE-SHA>` and `<RENDERED-PLIST-SHA256:…>` are refused, and after sealing the values must be a 40-hex commit and three 64-hex digests. It can block nothing else:
- It lives only inside `_prepare_candidate` behind `revision_five`.
- No arm, night-gate or validator path reads the prereg (grep of `night_gate.py`, `night_agent_install.py`, `arm_readiness_evidence.py` and `run_night.py` found nothing).
- r7 is unaffected (§3).

**Decision log.** The entry is appended after the D-184 addendum and no earlier line changed. Its heading has no colon, so the site's entry regex treats it as an addendum, the same precedent as `## D-100 addendum (…)`. `test_docs_freshness` and `test_build_site_parsers` pass on a clone at the PR head.

## 3. Proof that historical epochs are unchanged

`/tmp/152c9255/prr-lens-opus/diff_probe.py` runs against both `git archive c034a56f` and `git archive 3c52518d`. It covers:
- `load_calibration_acceptance_bound` (canonical dump hash) and `_valid_acceptance_bound` for r2–r7 and the genesis artifact;
- the same artifacts with `os_build` swapped to 25G83;
- `_registered_generation_row_is_complete` on all 7 registered rows, plus 240+ fuzzed rows: every drift/screen pair drawn from the row's own values × `corpus_n` ∈ {12, 16, 17, 19} × `registration_revision` absent or 5, and a screen-rule swap.

**Result: 266 of 266 keys are identical.** r7's loaded-artifact hash is `211ed076…` in both trees.

`_prior_set_matches_import_cutoff_prefix` reaches the same helper with `revision_five=False` whenever the identity is not 25G83/v3 or the row lacks `registration_revision: 5`, so the same proof covers it.

Issuer differences on non-Revision-5 epochs (none touches r7):
- the dry-run line gains `valid=N` (ruled);
- candidates gain `"disposing_decision_ids": []`;
- the registry is read for every epoch, failing closed;
- the `--minimum-corpus-size` refusal now fires after the ledger loads, with reworded messages. The accept/refuse sets are unchanged.

## 4. SHOULD-FIX

- **S1**: the disposing-decision id, as in §1.
- **S2: sealing breaks a new test.** In a clone I replaced the four placeholders with well-formed values and ran `test_issuer_refuses_unsealed_launch_context_and_disposes_exact_ids`. It fails: `args(PREREG)` no longer raises "unsealed placeholders" (it fails on the registry path instead). The `malformed` fixture also stops being malformed, because `.replace("a"*40, …)` becomes a no-op. As written, the R15 "seal Revision 5" step cannot be a text-only commit.
  - Fix: build the unsealed and malformed fixtures from a canonical template. Regex-substitute the operating-condition sentence (`template at commit \S+, rendered-plist digests …`) with the placeholder form or a malformed form, whatever the live file's state.
- **S3: a pin-uniqueness guard was weakened.** In `tests/test_preregistration_chain_digest.py:95-102`, "exactly one `os_build:` pin" became "two matches, equal". That guard existed to reject repeated pin text.
  - Fix: restore the original test. In Revision 5 (`:608`), write the field so `_PREREGISTRATION_OS_BUILD` (`os_build:\s*`) does not match, e.g. `` `os_build` = `25G83` `` or "os_build 25G83".
- **S4: a test outside the ruling now skips itself.** `DeskEpochWatchTests` gained a `skipTest` when `sysctl` is unavailable (`tests/test_issue_calibration_acceptance_generation.py:344-349`). It is not in R4/R5/R9/R10/R17, and it hides a real-probe test (likely one of the seat's `skipped=2`). Revert it.
- **S5: `test_pinned_estimator_files_match_main` is fragile.** It runs `git diff --quiet origin/main`, so it fails in any clone without an `origin/main` ref (reproduced), becomes tautological after merge, and would permanently fail a future council-approved v4 reopen.
  - Fix: assert the four files' sha256 against the c034a56f blob hashes, or drop the test and keep R9's `git diff` as the gate-ledger command it was ruled to be.
- **S6: the cited ruling file is missing from this branch and from main.** The ruling path cited in the prereg Authority line and the decision-log entry is `docs/process_traces/2026-09-25-activation-152c9255/…/21-coldgate-fable-acc2-addendum-ruling.md`.
  - Fix: land `docs/2026-09-25-152c9255` before or with PR-R, so the sealed registration never cites a file that does not exist.
  - Related: no arm-time code refuses a prereg that still holds placeholders, so an arm made from unsealed text makes the campaign permanently unissuable, because of the sha pin. Add to the R15 seal step: the placeholder count (`grep -c '<PR-L-MERGE-SHA>\|<RENDERED-PLIST-SHA256:'`) must be 0 before the arm-notice digest is taken. Seal only the literal tokens, with no backticks: the issuer's "malformed" regex expects bare hex.

## 5. NIT

- **N1**: The Authority line omits the ruling's locations. The D-184 addendum is at `docs/decision_log.md:12174`; the ruling's "≈12176-12178" now lands on this new entry. Cite it by text, "D-184 **Addendum (Ed, 2026-09-24 ≈04:40 PDT)**", plus Revision 1 "Stopping."/"Blindness."/"Screen challenge." and Revision 2 `## What replaces it` / `## On PASS` / `## On FAIL`.
- **N2**: `:620` says "in the ruling's I/D/SH order", but the table runs I, I, SH, D, D. Say "I/SH/D", or reorder the rows. I did not re-derive the table's cadence numbers apart from the n1 D row.
- **N3**: R15 orders the stops as cadence first, then futility. Revision 5 states futility first. Both stop, so the outcome is the same; align the text with R15.
- **N4**: In `docs/calibration/acc_25g83_rev5_simulation.md`, the table header has 10 cells but the delimiter row has 9, so GFM will not render it as a table. Add one `---:`.
- **N5**: The docstring of `joulewise/calibration_bracketing.py:418-422` still says the screen must sit strictly below the ceiling "in every case". Add the Revision 5 exception.
- **N6**: The issuer hardcodes `Decimal("0.25")` (`:1389`). Import `PLATEAU_INSET_S` from `joulewise.powermetrics_fiducial` (importing leaves the pinned file unchanged).
- **N7**: `REVISION_FIVE_EPOCH` is duplicated in the issuer and the bracketing module. Import the bracketing one.
- **N8**: Emit `disposing_decision_ids` only when `revision_five` is true. Consider reading the registry only on that path, so historical candidates stay byte-stable.
- **N9**: The D-125 and D-126 addenda sit under the disposition heading. Give each its own `## D-125 addendum (2026-09-25): …` / `## D-126 addendum (2026-09-25): …` heading, following the D-100/D-101 precedent. The stale-number audit (`:636`) should cite "record 37" as its source.
- **N10**: The Revision 5 issuer tests use `--predecessor-acceptance` R6. Revision 5 reads r7, so use R7. Optionally, refuse a predecessor other than r7 when `revision_five` is true.
- **N11**: Revision 5 adds "W3 … is another 12-slot window". The ruling does not say this, but it matches the issuer's per-session slot fence. Acceptable; noting it only.

Verification I ran in `/tmp/152c9255/prr-lens-opus/`:
- `tests.test_acc_25g83_rev5` and `tests.test_preregistration_chain_digest`: 15 tests, OK.
- `tests.test_docs_freshness` and `tests.test_build_site_parsers`: 61 tests, OK (30 skipped).
- The §3 differential probe.
- The S2 seal simulation and the S5 missing-ref run.

The worktree was never written to.
