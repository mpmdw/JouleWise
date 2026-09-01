```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "D-165 close-out is refuted: forged sidecar inputs and unknown close-out cell identities can still produce Branch A licensing.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "baec098f67588ff40d3547f07f4018ee5e75565b",
    "head_end": "baec098f67588ff40d3547f07f4018ee5e75565b",
    "upstream_end": null,
    "branch": "HEAD (no branch)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "REFUTE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Self-consistent forged sidecar can license Branch A",
        "file": "joulewise/dominance_closeout.py:739-771; scripts/build_d165_dominance_closeout.py:36-48",
        "summary": "Source hashes are computed over caller-supplied objects; no mint custody, manifest block identity, or trusted attestation is verified."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "Unknown close-out cell identity is accepted",
        "file": "joulewise/dominance_closeout.py:1159-1228",
        "summary": "The validator compares ordinary and common-mode IDs only to each other, skips unknown expected records, and can accept forged-cell with Branch A licensing."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "CLI overwrites an existing output",
        "file": "scripts/build_d165_dominance_closeout.py:221-224",
        "summary": "An existing output path is accepted and written instead of refused."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "Mutation coverage leaves 94 core and 13 builder guards green",
        "file": "joulewise/dominance_closeout.py:183-1228; scripts/build_d165_dominance_closeout.py:15-228",
        "summary": "Independent force-false mutations remain green under every runnable focused test."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "Synthetic fixture makes lineage tests vacuous",
        "file": "tests/test_d165_dominance_closeout.py:56-181,394-402",
        "summary": "Minimal hand-built sources and production-derived synthetic independent records do not test authenticated finalized-manifest lineage."
      },
      {
        "id": "F6",
        "severity": "nit",
        "title": "Trailing blank line",
        "file": "docs/contracts/d165_dominance_closeout.md:251",
        "summary": "git diff --check reports a new blank line at EOF."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (errors=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_extraction_total_stays_bit_identical_after_split_exposure tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_generator_imports_shared_core_and_registration_bytes_are_unchanged",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "cmp <(PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_d165_dominance_closeout.py <(PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from tests.test_d165_dominance_closeout import finalized_manifest; print(json.dumps(finalized_manifest()))') <(PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from tests.test_d165_dominance_closeout import floor_artifact; print(json.dumps(floor_artifact()))') <(PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from tests.test_d165_dominance_closeout import floor_artifact,replay_sidecar; print(json.dumps(replay_sidecar(floor_artifact())))')) <(PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_d165_dominance_closeout.py <(PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from tests.test_d165_dominance_closeout import finalized_manifest; print(json.dumps(finalized_manifest()))') <(PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from tests.test_d165_dominance_closeout import floor_artifact; print(json.dumps(floor_artifact()))') <(PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from tests.test_d165_dominance_closeout import floor_artifact,replay_sidecar; print(json.dumps(replay_sidecar(floor_artifact())))')) && echo byte_identical",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "byte_identical"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^byte_identical$"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_d165_dominance_closeout.py <(PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from tests.test_d165_dominance_closeout import finalized_manifest; print(json.dumps(finalized_manifest()))') <(PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from tests.test_d165_dominance_closeout import floor_artifact; print(json.dumps(floor_artifact()))') <(PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json; from tests.test_d165_dominance_closeout import floor_artifact,replay_sidecar; print(json.dumps(replay_sidecar(floor_artifact())))') --output /dev/null",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "^d165_dominance_closeout_refused:"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_d165_dominance_closeout.py /missing/finalized.json /missing/floor.json /missing/sidecar.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "d165_dominance_closeout_refused: finalized manifest is unreadable"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "^d165_dominance_closeout_refused:"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check HEAD^ HEAD",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "docs/contracts/d165_dominance_closeout.md:251: new blank line at EOF."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The environment has no usable writable temporary directory; the CLI tempfile test, canonical suite, and literal /tmp mutation copies could not complete.",
      "needs": "Rerun in a writable isolated checkout."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No runs* retained corpus exists in this checkout; extraction parity was checked only against the available measured_pair fixture.",
      "needs": "Provide the retained corpus if full historical-total replay is required."
    }
  ]
}
```

## Findings

1. **BLOCKER — F1: forged sidecar can license Branch A.**

   `validate_d165_replay_sidecar` verifies internal arithmetic and the bracket’s self-reported digest (`joulewise/dominance_closeout.py:623-735`). `_validate_source_reference` only recomputes a digest over the caller-supplied object (`joulewise/dominance_closeout.py:739-771`), while `_source_precondition_errors` checks only schema, IDs, and local consistency (`joulewise/dominance_closeout.py:980-1016`). The builder likewise hashes whatever object it receives (`scripts/build_d165_dominance_closeout.py:36-48`).

   I supplied forged blocks `forged-a` and `forged-b`, a correctly hashed forged bracket, recomputed splits/results, and `sidecar_id: forged-no-mint-provenance`. The sidecar validator returned `[]`; the builder returned `branch: "A"` and `dominance_sentence_licensed: true`, with common-mode ratios about `9.000000000000083`.

   This violates the registration fence requiring `authenticated_custodied_block_inputs_only` (`configs/campaigns/d117_contrast_v5/generate_configs.py:553-559`), the ruling’s authenticated sidecar requirement (`docs/process_traces/2026-09-01-fresh-model-review/06b-RULING-d165-artifact-ownership.md:18-28`), and the contract’s mint-evidence requirements (`docs/contracts/d165_dominance_closeout.md:104-120,162-168`).

   Minimal fix: require a trusted mint attestation/custody receipt and independently verify finalized-manifest block identities and evidence digests. Do not authenticate an untrusted sidecar by hashing the object supplied by the same caller.

2. **BLOCKER — F2: unknown close-out cell identity can retain Branch A.**

   The validator only requires eight unique `(cell_id, component)` pairs and equality between ordinary and common-mode ID sets (`joulewise/dominance_closeout.py:1110-1163`). It never requires those IDs to equal the four floor IDs. Unknown ordinary IDs are skipped when expected floor records are built (`joulewise/dominance_closeout.py:1176-1208`), and unknown common IDs are skipped when matching sidecar cells (`joulewise/dominance_closeout.py:1210-1228`).

   Replacing the first real cell ID in both ordinary records and the common-mode record with `forged-cell` produced `validate_d165_closeout(...) == []`, while preserving `branch: "A"` and `dominance_sentence_licensed: true`.

   This violates the required four-cell identity census (`docs/contracts/d165_dominance_closeout.md:196-200,206`) and the ruling’s exact eight-plus-four, neither-branch-on-untruthful-input rule (`docs/process_traces/2026-09-01-fresh-model-review/06b-RULING-d165-artifact-ownership.md:29-34`).

   Minimal fix: require the independent and common-mode cell-ID sets to equal the floor artifact’s four IDs exactly; require one record per `(floor_cell_id, component)`; convert unknown IDs from `continue` into validation errors.

### Directed adversarial matrix

| Input | Refusing path and observed reason | Any `branch: A` or licensed sentence? |
|---|---|---|
| One block’s local width `+1e-9` | `validate_d165_replay_sidecar`, `derived_split: does not match split_common_mode_block_width` (`joulewise/dominance_closeout.py:684-713`) | No; builder stop |
| One shared sign flipped | Fresh replay result mismatch (`joulewise/dominance_closeout.py:719-735`) | No; builder stop |
| Ordinary denominator set to zero | Sidecar-only validator does not own floor operands; builder emits `dominance_ratio_zero_denominator` via (`joulewise/dominance_closeout.py:176-196`, `scripts/build_d165_dominance_closeout.py:89-98`) | No; `branch: null` |
| One comparative cell dropped | Standalone sidecar validator accepts nonempty subsets by design; close-out alignment refuses with `replay_sidecar.cells: cell census does not match floor artifact` (`joulewise/dominance_closeout.py:931-939`) | No |
| Fifth cell added | Same close-out alignment census error (`joulewise/dominance_closeout.py:931-939`) | No |
| Shared-edge bracket hash wrong | `calibration_bracket_sha256: source-hash mismatch` (`joulewise/dominance_closeout.py:638-649`) | No |
| Blocks reordered | No error; replay enumerates all block positions/signs (`joulewise/dominance_closeout.py:396-409`) | Yes, expected; order is semantically irrelevant |
| Per-cell ratio disagrees with raw inputs | `result: does not match replay_common_mode_dominance` (`joulewise/dominance_closeout.py:715-735`); builder also rejected the inconsistent close-out | No |
| Duplicate cell ID | `cell_id: duplicate 'qwen3-1p7b-prefill'` (`joulewise/dominance_closeout.py:570-581`) | No |
| NaN | Finite-value rejection (`joulewise/dominance_closeout.py:546`); builder’s canonical hash also rejects it | No |
| `inf` | Same finite-value/canonical-JSON rejection | No |
| Exact `R = 2.0` | `dominance_ratio` uses `>=` (`joulewise/dominance_closeout.py:189-196`) | Yes; Branch A |
| `R = 1.9999999999` | No refusal; normal branch calculation (`joulewise/dominance_closeout.py:1040-1049`) | No; Branch B |

3. **SHOULD-FIX — F3: existing output is overwritten.**

   The CLI unconditionally calls `write_text` for a supplied output path (`scripts/build_d165_dominance_closeout.py:221-224`). Running against the already-existing `/dev/null` returned exit `0`; a normal existing file would be truncated. This conflicts with the immutable-evidence rule (`docs/decision_log.md:1229-1231`) and the repository’s exclusive-write precedent (`scripts/extract_detection_floors.py:124-160`, `scripts/mint_floor_artifact.py:1939-1949`).

   Minimal fix: preflight refusal plus exclusive creation (`O_EXCL` or `Path.open("x")`), including the race between preflight and write.

4. **SHOULD-FIX — F4: mutation survivors.**

   The focused tests cover the contract’s basic fail-closed cases but do not kill 94 of 110 core conditional mutations or any of the 13 builder mutations. No surviving mutation emitted a licensed sentence within the ten runnable tests, so this remains SHOULD-FIX rather than an additional blocker. The contract nevertheless requires fail-closed validation (`docs/contracts/d165_dominance_closeout.md:246-250`).

5. **SHOULD-FIX — F5: synthetic fixture makes lineage checks vacuous.**

   `floor_artifact()` and `finalized_manifest()` are minimal hand-built objects (`tests/test_d165_dominance_closeout.py:56-84`). `replay_sidecar()` copies the same fixture blocks into every cell and derives independent records through the production functions (`tests/test_d165_dominance_closeout.py:87-181`). The measured-pair test explicitly adds synthetic independent records (`tests/test_d165_dominance_closeout.py:394-402`).

   Affected tests are T1, T2, T3, T4, T5, T6, T7, T10, and the skipped T11 CLI test. They do not exercise a mint-issued sidecar, finalized manifest topology, or independently calculated expected ratios. This leaves the authenticated-evidence requirement untested (`docs/process_traces/2026-09-01-fresh-model-review/06b-RULING-d165-artifact-ownership.md:18-28`; `docs/contracts/d165_dominance_closeout.md:104-120`).

6. **NIT — F6: trailing blank line.**

   `git diff --check HEAD^ HEAD` reports `docs/contracts/d165_dominance_closeout.md:251: new blank line at EOF`.

## Mutation table

Each listed line was independently forced false in a fresh in-memory AST clone. No worktree or `/tmp` files were modified. Core: 110 mutations, 94 green and 16 red. Builder: 13 mutations, all 13 green.

Tests T1–T10 were green for every listed mutation:

- T1 `test_census_is_eight_ordinary_plus_four_comparative_common_mode`
- T2 `test_ratio_equal_to_two_passes`
- T3 `test_zero_denominator_refuses_with_named_reason`
- T4 `test_missing_sidecar_cell_stops_with_neither_branch`
- T5 `test_source_hash_mutation_refuses_validation`
- T6 `test_validators_reject_missing_extra_and_nonfinite_fields`
- T7 `test_branch_a_and_branch_b_fixtures`
- T8 `test_generator_imports_shared_core_and_registration_bytes_are_unchanged`
- T9 `test_extraction_total_stays_bit_identical_after_split_exposure`
- T10 `test_measured_pair_reshaped_as_one_cell_sidecar_round_trips`

T11, `test_cli_writes_the_same_valid_closeout_as_the_python_builder`, was blocked by `tempfile.TemporaryDirectory()`.

| File/function | Guard lines deleted/disabled | Green tests |
|---|---:|---|
| `joulewise/dominance_closeout.py` — ratio/split helpers | 183, 185, 190, 207, 210, 216, 239 | T1–T10 |
| Core replay input guards | 302, 304, 339, 342, 383, 385 | T1–T10 |
| Key and independent-record validation | 428, 494, 515, 518, 527 | T1–T10 |
| Common-mode result validation | 537, 548, 550 | T1–T10 |
| Sidecar schema/cell guards | 560, 564, 567, 573, 576, 578, 591, 606, 616, 625 | T1–T10 |
| Bracket, bound, block, split, replay guards | 629, 631, 638, 646, 650, 659, 671, 676, 680, 685, 708 | T1–T10 |
| Source-reference checks | 748, 751, 753, 756, 758, 761, 763 | T1–T10 |
| Close-out record checks | 779, 782, 784, 832, 835, 837, 846, 848, 850, 852, 866, 869, 879, 885, 887, 889 | T1–T10 |
| Floor/sidecar maps and alignment | 897, 900, 904, 908, 910, 920, 962, 972 | T1–T10 |
| Source preconditions | 986, 989, 994, 996, 1000, 1005, 1010, 1014 | T1–T10 |
| Close-out census/branch checks | 1064, 1066, 1119, 1131, 1136, 1155, 1162, 1168, 1173, 1205, 1210, 1217, 1228 | T1–T10 |
| `scripts/build_d165_dominance_closeout.py` — builder/setup/CLI guards | 15, 40, 42, 58, 65, 75, 84, 104, 120, 175, 185, 221, 228 | T1–T10 |

## Residual risk

The available `fcm_r4_real_blocks/measured_pair.json` fixture reproduced the prior extraction totals bit-for-bit: `0.31034858733220494` and `0.7509875593848513`. Registration bytes also remained unchanged (`tests/test_d165_dominance_closeout.py:333-346`).

No `runs*` retained corpus is present in this checkout, and the canonical suite could not reach a normal completion because the environment lacks a usable writable temporary directory.

VERDICT: REFUTE