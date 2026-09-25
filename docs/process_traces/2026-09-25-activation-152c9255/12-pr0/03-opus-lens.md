# PR-0 (WR-7) review: claim-gate v1 replay golden, `ab48c5d3`

**Verdict: not ready to merge (2 BLOCKERs).** The golden regenerates identically every time and is canonical. But it barely touches the v1 decision code that CG-4 will edit. In the mutation run, 7 of 9 real changes to v1 code passed the golden test. One of them deleted the floor check outright.

**What I ran.** I cloned the branch to `/tmp/152c9255/pr0-lens/repo` and read the ruling from `origin/docs/2026-09-25-152c9255`. I didn't write anything to the worktree, and `git status` stayed clean in both places. No sudo, no launchctl, no full test discovery.

## (1) Does the golden capture everything WR-7 lists?

I listed every tracked JSON file by `schema_version` and compared that with the golden.

| WR-7 item | In the repo | In the golden | Result |
|---|---|---|---|
| Fixture families via `_replay_family` | 5 `fixture.*` roles | 5 | Complete, but every result is the same (SF-3) |
| Claim-verdict artifacts, fill-rehearsal | 2 (`claim_verdicts.v1`) | 2 | OK |
| Claim-verdict artifacts, test fixtures | No such JSON files. There are code-built ones in `tests/test_analysis_claims.py:297` `minimal_artifact()` and `tests/test_analysis_integration.py:629` (`analyze_claims` end-to-end) | 0 | **Missing** (B-1) |
| Manifests | v2 ×3, v3 ×1, v3.prospective ×3; no v1, no finalized | 7 | Complete |
| Registries | v1 ×1, v2 ×2 (the three WR-6 files) | 3 | Complete |
| 09-19 epoch replays | n1 INCONCLUSIVE m=4, n2 FAIL m=7 | both; replay matches the record | OK |

The three d117 prospective manifests return `analysis_prospective_not_frozen` and related codes. That is genuine: they are drafts (`draft_status`), not a wrong call.

## (2) Deterministic and canonical: PASS

- Regenerating in `/tmp` gave blob `72148bfe…`, the same as the pin. It held under Python 3.14.7 and 3.13.1, `PYTHONHASHSEED` 1, 2 and 999, `TZ=Asia/Tokyo` and `LC_ALL=C`.
- Output is canonical: sorted keys, compact separators, `allow_nan=False`, trailing newline. The test also checks that the file re-canonicalizes to itself.

## (3) Does `test_claimgate_v1_replay_golden_unchanged` catch real v1 changes?

Each mutation was applied in the clone, the single test was run, and the file was restored. Bytecode writing was off (`PYTHONDONTWRITEBYTECODE=1`, `__pycache__` removed; see the note at the end).

| # | Mutation (file) | Result |
|---|---|---|
| M1 | `claims.py:343` floor comparison `<=` → `<` | **SURVIVED** |
| M2 | `claims.py:343` floor check deleted (`if False:`) | **SURVIVED** |
| M3 | `claims.py:343` compare against `2 * floor` | killed |
| M4 | `claims.py:351` equivalence `margin <= floor` → `<` | **SURVIVED** |
| M5 | `claims.py` multiplicity check dropped (`elif not adjusted_rejected` → `elif False`) | **SURVIVED** |
| M6 | `claims.py` legacy demotion (`and not legacy`) dropped | **SURVIVED** |
| M7 | `epoch_equivalence_check.py:127` `MINIMUM_RETAINED_M` 6 → 4 | killed (n1 becomes FAIL) |
| M8 | `analysis_engine/__init__.py:408` floor selector ignores metric | **SURVIVED** |
| M9 | `paper_custody.py` `_claim_issuance_gate` skips `validate_claim_verdicts` | **SURVIVED** |

Comment-only edits to `claims.py` and `paper_custody.py` don't change the capture, so there are no false alarms.

## (4) `test_golden_detects_one_number_mutation`: it only tests itself

`tests/test_claim_replay_golden.py:32-43` edits a copy of the parsed golden and checks that the edited bytes differ from the golden. That is always true. It never calls `capture()` and never goes through the comparison the real test uses. A broken comparison, such as a tolerance or keys-only check, would still pass it. See SF-2.

## (5) Can the golden be silently refreshed in the same PR as a source change?

Yes. Running `python3 scripts/capture_claim_replay_golden.py` and changing `GOLDEN_BLOB_SHA` (`tests/test_claim_replay_golden.py:16`) turns everything green. Nothing enforces WR-7's "at a commit with no `joulewise/` change", because `main()` (`scripts/capture_claim_replay_golden.py:226-229`) writes at any commit. The golden is also a single 21.6 KB line, so a refresh diff can't be reviewed line by line. See SF-1.

---

## Findings

### BLOCKER

**B-1: The golden doesn't exercise the v1 code CG-4 edits.** `scripts/capture_claim_replay_golden.py:100-140`
- The only `evaluate_claim` inputs are two near-identical synthetic contrasts, both `direction_supported` and far from the floor (estimate 999109.5 J vs floor 999104.5 J).
- None of these are reached: `analyze_claims` (window engine), `_resolve_contrast_floor`, `_claim_issuance_gate`, and the equivalence, unresolved, not-resolvable and demotion branches. Those include the exact sites WR-6 changes.
- The test-fixture filter at `:104-106` (`tests/fixtures/` plus "claim" and "verdict" in the name) matches **zero** files. The test fixtures WR-7 names are built in code.
- **Fix:**
  - (a) Add a `claim_matrix` section: a pinned table of `evaluate_claim` inputs that covers `|estimate| == floor`, `< floor` and `> floor`; margin `== floor` and `> floor`, inside and outside; `adjusted_rejected=False`; `legacy_l1`; non-confirmatory; sensitivity-blocking; direction mismatch; floor `None` and negative; valid and invalid `floor_metadata`. Store inputs and outputs.
  - (b) Add `window_engine`: import the builders at `tests/test_analysis_integration.py:600-633` and `tests/test_analysis_claims.py:297`, run `analyze_claims` / `validate_claim_verdicts` on every v1 scenario, and store `manifest_id` plus each contrast's `claim_evaluation`.
  - Acceptance: re-run `/tmp/152c9255/pr0-lens/mut.py`. M1, M2, M4, M5, M6 and M8 must all be killed.

**B-2 (from B-1): The golden can't do WR-6's job.** WR-6 admits v1 contrasts "iff finalized `manifest_id` is in the PR-0 golden set". The golden contains no finalized manifest. Its only claim-artifact id is `SYNTHETIC-REHEARSAL-manifest_id`, which the validator itself rejects as invalid. The other ids come from v2 fixtures and the splitwise v3 manifest, so which ids count as "the set" is ambiguous.
- **Fix:** add an explicit top-level `v1_golden_manifest_ids` list with a documented selection rule, so WR-6 imports a precise set. If the intended set is empty, record that and say so in the PR body.

### SHOULD-FIX

**SF-1: Nothing mechanically stops a same-PR refresh.** Locations: `tests/test_claim_replay_golden.py:16` and `scripts/capture_claim_replay_golden.py:226`.
- **Fix, part 1:** add `test_golden_refresh_isolated`. It computes `base = git merge-base HEAD origin/main`. If `git diff --quiet base HEAD -- tests/golden/claimgate_v1_replay.json` fails, it asserts that `git diff --name-only base HEAD -- joulewise/ scripts/epoch_equivalence_check.py` is empty. It skips with a clear message only when `origin/main` is missing.
- **Fix, part 2:** have `main()` refuse to write when `joulewise/` differs from `origin/main`.
- **Fix, part 3:** write the golden as sorted, indented JSON (`indent=1`) so a refresh diff shows exactly which decision moved.

**SF-2: The mutation test is a tautology.** `tests/test_claim_replay_golden.py:32-43`
- **Fix:** move the comparison into one helper, `_assert_matches_golden(actual: bytes)`, used by the real test. The mutation test then patches real code, for example `mock.patch.object(epoch, "MINIMUM_RETAINED_M", 4)` or a patched `evaluate_claim`, calls `canonical_bytes(capture())`, and asserts `_assert_matches_golden` raises.

**SF-3: Auto-discovered files will force refreshes during CG-4.** `scripts/capture_claim_replay_golden.py:44-46, 218`
- The capture scans every tracked JSON file at run time, so any new manifest, registry or verdict fixture added later fails the golden. So does any edit to the pinned drafts or rehearsal files. Each failure pushes a refresh, which makes the same-PR refresh routine.
- **Fix:** store the path list inside the golden and have `capture()` read exactly those paths. Add a separate informational test that lists newly tracked matching files without failing on them.

**SF-4: The fixture-family results are the same by construction.** `scripts/capture_claim_replay_golden.py:72-97`
- In fixture mode `_replay_family` (`paper_custody.py:1340-1342`) always returns `admitted=False` with no grants. All five families read `(True, False, [], [])`, and M9 survives.
- The raws are also written by the script instead of read from the checked-in `tests/fixtures/paper_custody/*.json`.
- **Fix:** read the real fixture bytes. Record in the golden that this section covers fixture authentication only; B-1(b) covers the issuance-gate logic.

### NIT

- **N-1** `:137`: `validate_claim_verdicts` stops at `_synthetic_scalars`. Also capture the errors with that key removed; there are at least six deeper errors (ID, sha, base64, supersession) that the golden currently misses.
- **N-2** `:198-214`: the epoch section has no PASS case. Add `tests/fixtures/epoch_continuation/s9-{pass,fail-bracket,fail-level}.json`. CG-3 edits `epoch_equivalence_check.py`, and the PASS comparison is currently unguarded.
- **N-3** `:130-133, :212`: make `capture()` raise when `evaluated != recorded` or `replayed != recorded`, so a golden can't be captured over a disagreement. Both agree today.
- **N-4** `:65-69`: `str(exc)` can include absolute paths. Record only `type(exc).__name__` plus `exc.code`. Nothing in today's output depends on the path.
- **N-5** `:45`: the capture needs a git checkout. That's fine; say so in the docstring.

**Note on method:** the first mutation run was contaminated. Changing M7's `6` to `4` kept the file size the same, and restoring it in the same second left a stale `.pyc` behind, so M8 and M9 looked killed. All results above are from the clean re-run. This only affects local mutation harnesses, not CI.
