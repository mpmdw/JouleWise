# Fresh-eyes review 2 — gate row 10, final head c28684a9

Range reviewed: `0f8a395d..c28684a9` (5 commits, 7 files, +78/-32, tests only).
Read-only; no test run. All hashes below re-derived this session in
/Users/edr/code/JouleWise-wt-transaction.

## 1. Hunk classification — no assertion weakened or deleted

All 7 files are TESTS-only. Every hunk is one of: a generation-id/filename pin
move (r6 -> r7), a harness argument, an added assertion, or a comment. Net
assertion count rises: one new test (4 asserts), one added `assertNotIn`, zero
removed. No tolerance widened, no `assertEqual` -> `assertIn`, no science value
(operatives, screens, fiducials, floors) touched; the only numeric constants that
move are digests/ids.

`tests/test_arm_readiness_evidence_author.py:130-131` ADDS r7 to the allowlist and
KEEPS r6 — a strict widening of the fixture's retained-generation set, not a swap.

## 2. Floor-mint pins — re-derived independently, all four agree

`tests/test_mint_floor_artifact_generalized.py`. The file's oracle is
`_fixture_canonical_sha256` (:849, json sort_keys/compact/utf-8), independent of
the mint code. I imported the module (PYTHONDONTWRITEBYTECODE=1), ran
`synthetic_v2_fixture()`, applied the component-sha overrides exactly as
`freeze_synthetic_v2_pinset` (:1336) does, and hashed:

- SYNTHETIC_PRODUCER_PIN_SHA256S (:1304) `0873dfba… / a92cf81e…` — MATCH
- SYNTHETIC_PRODUCER_SET_SHA256 (:1308) `bdee6762…` — MATCH
- `old_producers` (:6297) `8151052a… / e9760631…` — MATCH (re-derived under the
  old_components substitution)
- `_fixture_canonical_sha256(before)` (:6308) `5d22aa11…` — MATCH

Fixture acceptance ids are `d079_calibration_acceptance_v2_n17_r7` throughout.
The `acceptance_bytes` literal (:6287-6291) matches the real file:
`shasum -a 256 configs/calibration/calibration_acceptance_d079_v2_n17_r7.json`
= `9c3a29f6…`, and its `derivation_sha256` = `2c7dab72…`. Both agree byte-for-byte.

NOT verified (would require a test run): the phase-0 floor.json pin
`5a244411…` (:7053) — derived by executing the pinned scenario. Its commit
message and comment claim execution-derivation; the full-suite run in the
worktree is the check.

## 3. Step 8 — the s9 override is confined and the new pin is identity-only

- `S9_WITNESS_ACCEPTANCE` (tests/test_epoch_continuation.py:76) is used at exactly
  6 call sites (:972, :986, :991, :1005, :1010, :1030) = the four s9 tests named
  in the brief. Every other path still goes through `args()` (:63), which passes
  `bracket.DEFAULT_ACCEPTANCE_BOUND_PATH` — the ACTIVE r7 default. The one other
  literal `--acceptance` in the module (:929) also uses the ACTIVE default.
  Override is a trailing plain-store argparse option, so last-wins.
- New pin `test_s9_witness_against_the_active_generation_refuses_by_name`
  (:1035-1047) calls `self.args(...)` (ACTIVE default), asserts `rc == 3`,
  `assertIn("equivalence_record.reference_envelope.acceptance_id", error)` and
  `assertNotIn("b_fiducial_s", error)`. Identity + ordering only; no science value.
- `git diff 0f8a395d..c28684a9 -- tests/fixtures/` is EMPTY. s9 witnesses byte-identical.

The r6 anchor pin is not orphaned by the :1072 move: `ANCHOR_V3_R6_ACCEPTANCE_BOUND_SHA256`
is still asserted at tests/test_calibration_bracketing.py:620-624, alongside the r7
assertion at :615-617.

## 4. Frozen witnesses — clean

`git diff --stat 56ea8ae0..c28684a9 -- configs/campaigns/ configs/floor_mint/ tests/fixtures/ configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`
returns EMPTY. D-138 cl.(3) holds.

## 5. Remaining `n17_r6` hits in tests/ — no live-staging left

11 non-fixture hits, all classified benign:
- Retention/precedent assertions: test_calibration_bracketing.py:655 (r6 ledger_cutoff
  history), test_capture_pipeline_era.py:281 (r6 "stays recognised"),
  test_issue_calibration_acceptance_generation.py:1166,1170 (r7's PREDECESSOR is r6 —
  correct by construction), verify_calibration_acceptance_corpus.py:61 (corpus retention),
  test_arm_readiness_evidence_author.py:130 (r6 retained in allowlist).
- Issuance inputs: test_issue_calibration_acceptance_generation.py:61 `R6` constant,
  used as `--predecessor-acceptance` / `--acceptance` input to the r7-issuance runs
  (:870, :1612, :1787, :2011, :2084) and as the source of the predecessor's own
  statistics. Correct: this module issues r7 FROM r6.
- Private synthetic fixtures naming a retained generation:
  test_d117_v3_family.py:22-23, test_summarize_g2a_prefill_probe.py:449,
  test_generate_g2a_probe_inputs.py:71. These are cl.(3)-permitted private synthetic
  fixtures; none reads the live default. SHOULD-FIX candidate only if the r7 issuance
  was meant to make them exercise the active generation — but they assert nothing
  about the live default, so leaving them is consistent with "retained generations
  are never un-issued."

## Findings

- BLOCKER: none.
- SHOULD-FIX: none.
- NIT tests/test_epoch_continuation.py:1047-1048 — no blank line between the new
  test's last assert and `def test_malformed_self_pinned_json_refuses`. Cosmetic;
  no linter is configured in pyproject.toml or CI, so this cannot fail a gate.
- NIT tests/test_mint_floor_artifact_generalized.py:1293 — the reflowed comment line
  ("…remain unchanged at both issuances. Pins also move with a reviewed") runs past
  the file's ~72-col comment width.
- OBSERVATION: the floor.json scenario pin (:7053) is the single constant in this
  range I could not re-derive without executing a test. The in-flight full suite is
  the only evidence for it; if that suite does not include
  `V2PinsetAndMintTests`'s phase-0 floor scenario, this pin is unverified.

VERDICT: APPROVE — all five re-derivable constants match the independent oracle,
frozen witnesses are byte-identical, the s9 override is confined to the four s9
tests while every other path exercises the active r7 default, and no hunk weakens
or removes an assertion; only two cosmetic nits remain.
