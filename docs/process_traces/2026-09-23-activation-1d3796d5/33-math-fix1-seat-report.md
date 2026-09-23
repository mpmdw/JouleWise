```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Closed Y1–Y10, regenerated the hash-only fixture, and passed the named acceptance modules.",
  "workspace": {
    "base_requested": "313efcca",
    "base_mode": "exact",
    "head_start": "47ea644d8cce0a95d39cd7a702e67f58edc2ce18",
    "head_end": "47ea644d8cce0a95d39cd7a702e67f58edc2ce18",
    "upstream_end": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "branch": "feat/2026-09-23-math-importer"
  },
  "pathspec": [
    "joulewise/benchmark_import_math.py",
    "joulewise/suite.py",
    "tests/fixtures/math/hash_only_manifest.json",
    "tests/test_benchmark_import_math.py",
    "tests/test_suite.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_benchmark_import_math tests.test_benchmark_import tests.test_suite",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 62 tests in 1.046s", "OK (skipped=2)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 62 tests.*OK \\(skipped=2\\)"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "python3 -B scripts/gen_math_scored.py --out-dir /tmp/jw-math-fix-full --hash-only-out tests/fixtures/math/hash_only_manifest.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["hash_only_sha256 534e8c7f3782fba1be0a94a79216e1bcdf8bf88af971b9933b1ad1edfdc09acc tests/fixtures/math/hash_only_manifest.json"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "hash_only_sha256 [0-9a-f]{64}"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Real-tokenizer rendering and MLX decode handling of </think> remain the separate N5 lane.",
      "needs": "Magistrate to verify in the model-runtime lane."
    }
  ]
}
```

## Change

| Disposition | Closure |
|---|---|
| Y1 | [Importer:55](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:55) reads both pointer files and the licence, derives receipt hashes from their bytes, and refuses missing or mismatched files with the receipt name. [Tests:68](/Users/edr/code/wt-1d3796d5-math/tests/test_benchmark_import_math.py:68) cover omissions and corruption, including the train pointer. |
| Y2 | [Importer:111](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:111) freezes a separate reference parser used by eligibility. A scorer-only mixed-number extension leaves all 4,040 eligible rows and all three set hashes unchanged in [the real-file test](/Users/edr/code/wt-1d3796d5-math/tests/test_benchmark_import_math.py:271). |
| Y3 | [Importer:393](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:393) defines the complete prompt for each arm; the builder and [annotation validator:526](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:526) require exact equality. [Tests:225](/Users/edr/code/wt-1d3796d5-math/tests/test_benchmark_import_math.py:225) refuse an appended user turn and extra tail content. |
| Y4 | [Scorer:292](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:292) retains exact rational comparison. [Golden pairs:178](/Users/edr/code/wt-1d3796d5-math/tests/test_benchmark_import_math.py:178) pin the large-integer mismatch, fraction reduction, `\fbox{7}` **as a box**, normalization steps, and last-box choice. [Eligibility:215](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:215) refuses a rational answer field that disagrees with the solution’s last box. |
| Y5 | [Scorer:301](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:301) denies correctness for the specified magnitude words, imaginary-unit forms, and one-sided percent signs. [Golden pairs:178](/Users/edr/code/wt-1d3796d5-math/tests/test_benchmark_import_math.py:178) pin each and document `5,120` versus `5120` as correct thousands grouping. |
| Y6 | [Quarantine:39](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:39) now attributes malformed and capped outcomes separately and retains AP-5M PENDING and “no capability claim.” |
| Y7 | [Selection:256](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:256) interleaves pilot subjects per level. [Tests:119](/Users/edr/code/wt-1d3796d5-math/tests/test_benchmark_import_math.py:119) retain pilot/test disjointness and the n=64 prefix of n=128. |
| Y8 | [Extractor:187](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:187) recognizes brace-less `\boxed 5` and selects the last box. |
| Y9 | [Schema:630](/Users/edr/code/wt-1d3796d5-math/joulewise/suite.py:630) refuses an omitted pointer-hash key while preserving a present `null` value byte-identically. [Suite test:250](/Users/edr/code/wt-1d3796d5-math/tests/test_suite.py:250) also pins GSM8K serialization. |
| Y10 | [Eligibility note:40](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:40) states all exclusion counts and per-level retention. |

The [regenerated fixture](/Users/edr/code/wt-1d3796d5-math/tests/fixtures/math/hash_only_manifest.json) contains no problem text. Its population block is unchanged from HEAD: **5,001 rows, 4,040 eligible**; exclusions are 2 duplicate rows, 954 non-rational references, and 5 plain-comma references.

| Level | Retained |
|---|---:|
| 1 | 381/437 |
| 2 | 733/894 |
| 3 | 924/1,130 |
| 4 | 967/1,214 |
| 5 | 1,035/1,324 |

| Set | New SHA-256 |
|---|---|
| Pilot | `04c04ffec881aed3d970da059945587f1d2abecaf05b7361e05c1babf1b12d53` |
| n=64 | `bf94123715a95328fc89bdf6fdbe5388ea803214283d764fd8113aede618b0d2` |
| n=128 | `7ebb2d9defaf4d973bd975e7d7e0dcd6862c0fcdf47fec5bb3ac42127ccede92` |

## Verification notes

The final named acceptance command passed: `Ran 62 tests in 1.046s`; `OK (skipped=2)`. Fixture generation wrote full manifests only under `/tmp/jw-math-fix-full`. There were no scope or execution-fence deviations.

I reran the formerly surviving targeted mutations in a `/tmp` repository copy. Float equality, `\fbox` removal, slash-reduction removal, `\:`, `\ `, `~`, `%`, and `\degree` normalization removals were killed by `test_golden_pairs`. Dropping the reference-box comparison’s left operand was killed by `test_synthetic_fixture_loader_and_eligibility`; choosing the first box was killed by `test_real_population_receipts_hashes_and_reference_self_check`. Dropping the comparison’s right-side `box is None` guard **survived**: for an eligible rational gold value, `canonical_reference_v1(None) != gold` already refuses, so that mutant is equivalent on this path.

## Residual risk

N5 remains in its separate runtime lane. The magistrate should double-check the exact prompt shape with the real tokenizer, `</think>` survival through MLX decoding, and the deliberate `\fbox{7}` and `5,120` scoring choices.