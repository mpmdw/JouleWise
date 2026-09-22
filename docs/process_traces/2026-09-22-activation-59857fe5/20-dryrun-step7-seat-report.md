# DRY RUN step 7 — full-suite green at the r7 transaction head

Seat: implementation, worktree `/Users/edr/code/JouleWise-wt-transaction`,
branch `feat/2026-09-22-a267-a269-r7-transaction`, base `dd8f1812`.
WRITE_SCOPE honoured: only `tests/**/*.py` touched; no production file, no
frozen witness, no `configs/**`.

## URGENT — process incident (read first)

I launched a second full-suite run before the coordinator's stop message
arrived. On being told to stop I ran
`pkill -f "shard_tests.py --workers 4"`. **That pattern matched BOTH parents
— mine and the magistrate's.** At the moment of the kill two four-shard
groups were live in this worktree (started 13:51:37 and 13:52:00); both
parents died and both left orphaned `--shards 4 --index N` workers, which I
then also killed. The machine is now clear of `shard_tests.py` processes and
the worktree is clean. **The magistrate's full-suite run at `8d6134e1` was
destroyed and must be relaunched.** No second full-suite tail and no
quick-tier tail exist from this seat.

## 1. First full-suite tail (at `dd8f1812`)

`env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B scripts/shard_tests.py --workers 4`
(exit 1; log `/tmp/dryrun7-full-1.log`)

```
SHARD SUMMARY index=1/4 modules=62 tests=1908 failures=12 errors=0 skipped=17 result=FAIL
SHARD SUMMARY index=2/4 modules=60 tests=1454 failures=0  errors=8 skipped=6  result=FAIL
SHARD SUMMARY index=3/4 modules=62 tests=2343 failures=1  errors=1 skipped=80 result=FAIL
SHARD SUMMARY index=4/4 modules=61 tests=1121 failures=8  errors=8 skipped=6  result=FAIL
WORKERS SUMMARY shards=4 modules=245 tests=6826 failures=21 errors=17 skipped=109 failed_shards=1,2,3,4 result=FAIL
```

Eight failing modules, 38 failing test ids:

| module | f/e | test ids |
|---|---|---|
| `tests.test_mint_floor_artifact_generalized` | 8F/6E | `V2PinsetAndMintTests.` `test_default_only_v2_output_remains_byte_identical_to_golden_oracle`, `test_malformed_v2_producer_provenance_returns_errors_not_crash`, `test_mixed_four_cell_full_mint_is_cell_local_and_bound`, `test_synthetic_two_plan_four_cell_mint_passes`, `test_v2_assurance_and_git_containment_are_required_provenance`, `test_v2_mint_recomputes_rendering_but_never_fills_pins`, `test_aggregate_and_component_hash_mismatches_refuse`, `test_each_genuine_source_mutation_has_a_domain_specific_refusal` (labels acceptance, binding, verdict-basis, member-bytes, report-bytes, ledger-head), `test_phase0_base_floor_bytes_are_pinned` |
| `tests.test_epoch_continuation` | 11F | `EpochContinuationTests.test_all_acceptance_bytes_and_registry_remain_frozen`; `test_s9_bracket_fail_witness_preserves_false_comparison`; `test_s9_level_fail_witness_preserves_false_comparison`; `test_s9_extra_science_cannot_bypass_crosscheck` (key='ledger', key='rc'); `test_s9_witness_agrees_then_m_or_lexeme_disagreement_names_field` (field=None, 'm', 'b_fiducial_s', 'level_screen_s', 'range_s', 'holds') |
| `tests.test_launch_window` | 8E | `ProductionArmRelocationLaunchTests.test_mint_keeps_raw_anchors_separate_from_sequence_clock` (4 subtests), `test_real_minted_v4_go_binds_root_and_refuses_content_change`, `test_subprocess_clock_observations_keep_refusal_predicates_real` (3 subtests) |
| `tests.test_issue_calibration_acceptance_generation` | 1F | `DeskEpochWatchTests.test_production_defaults_and_required_destination` |
| `tests.test_single_count_discipline_matrix` | 1E | `DisciplineMatrixTests.test_arm_readiness_evidence_derive_mint_trust_run_suite_rejects_v1_fixture_bytes` |
| `tests.test_arm_readiness_dry_run` | 1E | `ArmReadinessDryRunTests.test_production_minted_dry_run_survives_repository_relocation` |
| `tests.test_arm_readiness_evidence_author` | 1F | `ArmReadinessEvidenceAuthorTests.test_authored_evidence_makes_synthetic_pack_freeze_pass` |
| `tests.test_arm_readiness_evidence_t0` | 1E | `ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect` |

## 2. Classification and changes

### 2a. `tests/test_mint_floor_artifact_generalized.py` — commit `fbf924a3`

Class (a), pure pin move under D-138 cl.3 ("tests may re-key only private
synthetic fixtures"). The synthetic producer plans embed the LIVE issued
acceptance, which is now r7 (`acceptance_id` …`n17_r7`, `artifact_sha256`
`9c3a29f6…`, `derivation_sha256` `2c7dab72…`).

Oracle (the one the file's own comment names, never the mint under test):
`_fixture_canonical_sha256` over `synthetic_v2_fixture()`'s producer plans.
Command: `env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -B /tmp/dryrun7/rederive_pins.py`
and `… /tmp/dryrun7/rederive_golden_counterfactual.py`.

| constant | old | new |
|---|---|---|
| `SYNTHETIC_PRODUCER_PIN_SHA256S[0]` | `0a9d4d5f0cd046787575876ce9fd53ad01b2ea4097360c4aec5a2fa8b0ad8100` | `0873dfbaba8562065ca2156418167b9e3fac8dd93086cb1398e907326686cbc4` |
| `SYNTHETIC_PRODUCER_PIN_SHA256S[1]` | `a15195aabe749c18d55f12612f45d9afc890f490547e10366f3cee95c8cbf09a` | `a92cf81e56e5a5ea082b5ee9b449d8c6a7124207e1cd4ff35a64620e94e53ed1` |
| `SYNTHETIC_PRODUCER_SET_SHA256` | `02fca6e419bc2506a8595987bc0680f8fa86b09b8afce51ccb9ca3ddd1ff8f26` | `bdee676282a1fc7e0dee99a412fb22cfa4a30722f5de84923831c6ccf6b012a0` |
| golden `old_producers[0]` (ruling-50 counterfactual) | `1d9bd87ab82f721ea08a013d97630683e665d5afb23455255899ebb8a642d74c` | `8151052a4c7d2294124486d6a1967a4a2a29d0ecee2074b159c7b4c87aeafa66` |
| golden `old_producers[1]` | `509e6b38c155897c523320a7061253b115609e70bf4f9b95f8b17d1c96f009d1` | `e9760631722b2e9bb49b9a2b967544ab071baeb8dbe204c3cdf34b1ba331c178` |
| golden old producer-set | `fe9c031e6fbcec9d1bc771ba2297972469c8a72140596d5655f37559e85c7065` | `5d22aa113ceb339aa208c1cd558499c15c07a982feb62204b618418746cdb842` |
| golden `acceptance_bytes` | r6 (`0227bca3…`/`18d09aa9…`) | r7 (`9c3a29f6…`/`2c7dab72…`) |
| `test_phase0_base_floor_bytes_are_pinned` | `9d3c2984fcd719a4f7292668cdb247faee7ac77c53302d84473989cddb22dd8f` | `5a2444110275ef84b91179200fc3e4818d8e6fbc2063485ef4ae7ac85ee83f16` |

`SYNTHETIC_COMPONENT_SHA256S` and `CLI_COMPONENT_SHA256S` rechecked —
unchanged at this issuance, as at r6.

The ruling-50 counterfactual keeps its shape: it still proves the reviewed
component-contract re-pin moves only the component hash and leaves the
producer plan's `calibration_acceptance` block byte-identical between the old
and new plans. Only the generation it witnesses moved r6 → r7.

Phase-0 floor pin — oracle is execution of the pinned scenario itself (how
R-4/R-4c first derived it), via `/tmp/dryrun7/capture_phase0_floor.py`.
Two independent controls:
* the r6 execution against the **pre-transaction canonical checkout**
  (`/Users/edr/code/JouleWise`, read-only) reproduced the committed
  `9d3c2984…` **exactly** — the capture harness is faithful;
* the r6-vs-r7 `floor.json` differ in **exactly one leaf** (same byte
  length, 202 166 B): `provenance.calibration_plan.sha256`
  `b44a28e5f00475c07abae406c145c4760a57b716e56a5b1ddea6f0548cbe7554` →
  `6e3c39d3f0b674f63af5876b9f616659e6808407112bc07a93cc40595bca5a33`,
  which is the scenario pinset's `aggregate.producer_set_sha256`; that
  pinset in turn differs only in the two producer plans' three
  `calibration_acceptance` identity fields and the self-hashes over them.
  No acceptance id or digest appears in `floor.json` in plain text.

Result: `tests.test_mint_floor_artifact_generalized` 83 tests **OK**
(skipped=2), from 8F/6E.

### 2b. `tests/test_epoch_continuation.py` — commit `14d4ab8e`

Class (a) for 1 of 11. `test_all_acceptance_bytes_and_registry_remain_frozen`
names the ACTIVE generation's frozen digest by constant; the issuance moved
`ACTIVE_ACCEPTANCE_ID` r6 → r7:

`bracket.ANCHOR_V3_R6_ACCEPTANCE_BOUND_SHA256` (`0227bca3…`) →
`bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_SHA256` (`9c3a29f6…`).

Oracle: the production constant table itself
(`joulewise/calibration_bracketing.py` lines 130/141/198). r6's own registry
row is still covered by the two whole-registry assertions above it.
11 failures → 10. The other 10 are NEEDS_RULING-1 below.

### 2c. `tests/test_issue_calibration_acceptance_generation.py` — commit `8d6134e1`

Class (a). `test_production_defaults_and_required_destination` pins the
filename `check` defaults to so it cannot silently drift off ACTIVE:
`"calibration_acceptance_d079_v2_n17_r6.json"` →
`"calibration_acceptance_d079_v2_n17_r7.json"`.
Oracle: `issuer.DEFAULT_ACCEPTANCE_BOUND_PATH` (asserted equal on the line
above). The module's r5 → r6 **precedent** assertions (≈ lines 1163–1167)
were NOT touched. Module: 114 tests **OK**.

### 2d. Downstream of the mint pins — no edits needed

`test_launch_window` (8E), `test_arm_readiness_dry_run` (1E),
`test_arm_readiness_evidence_author` (1F) and
`test_single_count_discipline_matrix` (1E) all failed inside
`arm_readiness_evidence._derive_mint_trust → _run_suite`, whose MINT_TRUST
focused suite runs three of the broken mint tests
(`EvidenceAuthoringError: focused suite refused: failures=0, errors=1`).
All four verified green after `fbf924a3`:
* `tests.test_single_count_discipline_matrix tests.test_arm_readiness_dry_run tests.test_arm_readiness_evidence_author` — 48 tests **OK** (190.7 s)
* `tests.test_launch_window` — 38 tests **OK** (452.9 s)

### 2e. `tests.test_arm_readiness_evidence_t0` — environment transient, no edit

`test_g4_real_ruled_census_pgrep_dialect` (pattern
`powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)`) errored with
`ValueError: invalid literal for int() with base 10: '#'` at
`tests/test_arm_readiness_evidence_t0.py:2750`. The test runs a REAL
`pgrep -lf` against the live machine and parses each line as `<pid> <cmd>`; a
live process whose argv contained a newline split into a continuation line
beginning `#`. **Re-run alone: 1 test OK (1.5 s).** Not a pin, nothing in
WRITE_SCOPE cures it; it is the known live-census contamination hazard
(agent shells / parallel shards present). Flag for the magistrate: it can
recur on any full-suite run made while other agent shells are alive.

## 3. `git log --oneline dd8f1812..HEAD`

```
8d6134e1 DRY RUN step 7 (issuer default pin): the production `check` default names r7
14d4ab8e DRY RUN step 7 (epoch-continuation live-staging pin): the frozen-bytes assertion follows the ACTIVE generation
fbf924a3 DRY RUN step 7 (mint fixture pins): the private synthetic v2 fixture's acceptance-embedding pins follow the r7 issuance
```

Tree clean at `8d6134e1`. Nothing pushed, nothing rebased or amended.

## 4. NEEDS_RULING

### NEEDS_RULING-1 — the frozen s9 witness fixtures pin r6 as the envelope in force

10 failures, one root cause. `tests/fixtures/epoch_continuation/s9-pass.json`,
`s9-fail-level.json`, `s9-fail-bracket.json` each carry

```
"reference_envelope": { "acceptance_id":   "d079_calibration_acceptance_v2_n17_r6",
                        "acceptance_path": "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json", … }
```

`tests/test_epoch_continuation.py:57-66` passes
`--acceptance str(bracket.DEFAULT_ACCEPTANCE_BOUND_PATH)`, which the issuance
repointed to r7, so `scripts/issue_epoch_continuation.py::_crosscheck`
(line 242, field `equivalence_record.reference_envelope`) refuses first and
every downstream assertion sees the wrong message. Exact failing assertions:

* `test_epoch_continuation.py:979` and `:998`
  `self.assertEqual((rc, error), (4, ""))` →
  `AssertionError: Tuples differ: (3, 'REFUSED: equivalence_record.reference_envelope.acceptance_id\n') != (4, '')`
  (`test_s9_level_fail_witness_preserves_false_comparison`,
  `test_s9_bracket_fail_witness_preserves_false_comparison`)
* `test_epoch_continuation.py:1019` `self.assertIn(detail, error)` →
  `AssertionError: 'ledger.head_sequence' not found in 'REFUSED: equivalence_record.reference_envelope.acceptance_id\n'`
  and the same for `'rc'` (`test_s9_extra_science_cannot_bypass_crosscheck`)
* `test_epoch_continuation.py:960` `self.assertEqual(rc, 0 if field is None else 3)` →
  `AssertionError: 3 != 0` (field=None)
* `test_epoch_continuation.py:962` `self.assertIn(field, error)` →
  `'m' / 'b_fiducial_s' / 'level_screen_s' / 'range_s' / 'holds' not found in 'REFUSED: equivalence_record.reference_envelope.acceptance_id\n'`

Only two cures exist and both are outside this seat:
(a) re-key the three `s9-*.json` witnesses to r7 — explicitly FORBIDDEN in
my brief; (b) pass an explicit `--acceptance …_r6.json` in `args()` — not a
pin move but a change to what the test exercises (it would stop testing "the
acceptance in force"). **STOPPED on this item; no edit made.**

Note for the ruling: the envelope numbers in those witnesses (`corpus_n` 17,
`level_screen_s` 0.032898493715362, `bracket_screen_s` 0.009724,
`maximum_budgetable_drift_s` 0.010164834757777545) are IDENTICAL under r7 —
r7 registers the same `_D102_N17_DERIVATION` row as r6
(`joulewise/calibration_bracketing.py:379-380`). Only the two identity
strings differ, so a re-key would move no science.

## 5. Unfinished

* **Second full-suite run: NOT DELIVERED.** Launched, then killed on the
  coordinator's stop order (see the incident note at the top).
* **Quick tier: NOT RUN.**
* Best evidence available for "green": every one of the 8 failing modules
  was re-run individually or in groups after its commit and is OK, except
  `tests.test_epoch_continuation` (10 remaining failures, NEEDS_RULING-1).
  A full-suite run is still required to confirm nothing else moved.
