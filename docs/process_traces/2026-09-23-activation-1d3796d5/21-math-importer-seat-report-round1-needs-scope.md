```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "MATH source authentication, selection, scoring, tests, and hash-only custody are implemented; native suite manifest support needs a schema scope expansion.",
  "workspace": {
    "base_requested": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "base_mode": "exact",
    "head_start": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "head_end": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "upstream_end": null,
    "branch": "feat/2026-09-23-math-importer"
  },
  "pathspec": [
    "joulewise/benchmark_import_math.py",
    "scripts/gen_math_scored.py",
    "tests/test_benchmark_import_math.py",
    "tests/fixtures/math/hash_only_manifest.json",
    "tests/fixtures/math/synthetic_test.jsonl",
    "tests/fixtures/math/synthetic_train.jsonl"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 -B scripts/gen_math_scored.py --out-dir /private/tmp/math-scored-20260923 --hash-only-out tests/fixtures/math/hash_only_manifest.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "n128 1caaf115ac3e775d905be197bbdf63fb2f2b28b92cb7bac5cd46d044dc65aefa /private/tmp/math-scored-20260923/math_off_n128.json",
          "hash_only_sha256 47e96a3707a57357875ad48fd0c516d2b1f364aebce2ae0e5f44a139d639471f tests/fixtures/math/hash_only_manifest.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "hash_only_sha256 [0-9a-f]{64} tests/fixtures/math/hash_only_manifest.json"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_benchmark_import_math tests.test_benchmark_import tests.test_suite",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 59 tests in 0.468s",
          "OK (skipped=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 59 tests.*OK \\(skipped=2\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: SuiteManifest rejects the two-file source_files receipt field. The generated full manifests are custody manifests, not native runnable suite manifests.",
      "needs": "Magistrate grants prospective write scope for joulewise/suite.py and tests/test_suite.py, then resumes native suite manifest integration."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/suite.py",
      "tests/test_suite.py"
    ],
    "reason": "The native BenchmarkImport schema permits one source file and rejects source_files; MATH requires authenticated test.jsonl and train.jsonl receipts.",
    "blocked_work": "Emit and validate native runnable MATH suite manifests.",
    "minimal_change": "Add optional BenchmarkImport.source_files entries with path, sha256, bytes, line_count, git_blob_sha1, lfs_pointer_blob_sha1, and license_blob_sha1; validate them and omit the field from legacy serialization when absent; add a suite regression."
  }
}
```

## Change

**NEEDS_SCOPE.** The importer and producer are in [benchmark_import_math.py](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:20) and [gen_math_scored.py](/Users/edr/code/wt-1d3796d5-math/scripts/gen_math_scored.py:25). Full manifests containing problem text were generated under `/private/tmp/math-scored-20260923`; the repository [fixture](/Users/edr/code/wt-1d3796d5-math/tests/fixtures/math/hash_only_manifest.json) contains IDs, item hashes, set hashes, receipts, and population counts.

| Clause | Implementation and acceptance |
|---|---|
| C1 | Six pinned receipts and optional local pointer/license byte checks: [loader](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:50); mutation and receipt refusals: [tests](/Users/edr/code/wt-1d3796d5-math/tests/test_benchmark_import_math.py:51). |
| C2 | Duplicate exclusion, rational eligibility, answer/last-box cross-check, and level/subject counts: [eligibility](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:156). |
| C3 | Domain-separated 80-item pilot and subject-interleaved prefix selection: [selection](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:185); [tests](/Users/edr/code/wt-1d3796d5-math/tests/test_benchmark_import_math.py:79). |
| C4 | Fixed rational normalization and four-outcome scorer: [scorer](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:96); [golden tests](/Users/edr/code/wt-1d3796d5-math/tests/test_benchmark_import_math.py:139). |
| C5–C6 | Prompt hash, both thinking-arm rendering checks, and quarantine constants marked **AP-5M PENDING**: [constants](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:29), [rendering](/Users/edr/code/wt-1d3796d5-math/joulewise/benchmark_import_math.py:268). |
| C7 | Untracked full output and hash-only fixture: [producer](/Users/edr/code/wt-1d3796d5-math/scripts/gen_math_scored.py:25). |
| C8 | Synthetic fixtures and real-source checks that skip when the pinned files are absent: [tests](/Users/edr/code/wt-1d3796d5-math/tests/test_benchmark_import_math.py:1). |

Authenticated population, in subject order **Algebra / Counting & Probability / Geometry / Intermediate Algebra / Number Theory / Prealgebra / Precalculus**:

| Level | Eligible by subject | Eligible / nonduplicate | Retention |
|---|---|---:|---:|
| 1 | 128 / 38 / 35 / 32 / 30 / 83 / 35 | 381 / 437 | 0.872 |
| 2 | 178 / 100 / 65 / 81 / 83 / 171 / 55 | 733 / 894 | 0.820 |
| 3 | 229 / 99 / 75 / 137 / 109 / 211 / 64 | 924 / 1,130 | 0.818 |
| 4 | 250 / 109 / 82 / 174 / 130 / 172 / 50 | 967 / 1,214 | 0.797 |
| 5 | 248 / 121 / 88 / 199 / 149 / 162 / 68 | 1,035 / 1,324 | 0.782 |

There are **5,001 rows, 5,000 distinct IDs before exclusion, and 4,999 singleton IDs**. Exclusions are two duplicate-ID rows, 954 nonrational references, and five plain-comma references. Eligible total: **4,040**. The reference self-check passed **4,040/4,040**. Packet A’s table also sums to 4,040; the integration synthesis’s description of that figure as an arithmetic slip is inconsistent with the authenticated data.

| Set | Canonical ID-list SHA-256 | Reproduces packet A? |
|---|---|---|
| Pilot, 16 per level | `d6a1671839efd2b99a3146f6f67be50d9b2cb57bff89704b630d17f7bd91d17c` | No |
| Test, 64 per level | `face9ab2eae3d9b0abf2d87ae83f4d1264d6951a8d9706ebc6ff7f147de81430` | No |
| Test, 128 per level | `1caaf115ac3e775d905be197bbdf63fb2f2b28b92cb7bac5cd46d044dc65aefa` | No |

All three differ because the amended pilot reserves 80 items before test selection, versus packet A’s 16.

| Golden responses against reference | Pinned outcome |
|---|---|
| `\dfrac{3}{4}`, `0.75`, `3/4`, `\frac{6}{8}`, nested boxed `\frac{3}{4}` against `\frac34`; `-\frac12`, `x=5`, `10,080`, `90^\circ`, `5\text{ cm}`, `\$4`, `.5` against their packet A references | Correct |
| `\sqrt{2}`, `\frac{1}{0}`, `1,2`, `2\frac12`, `0.333`, and two boxes whose last value is wrong | Incorrect |
| Box only before an unclosed `</think>`; no box | Malformed |
| Capped with a parseable box or without one | Truncated; parsed value retained when present |

## Verification notes

The named acceptance command passed: **59 tests, two skips**. The real-source MATH test ran and checked both receipts, all population counts, hashes, and the 4,040-reference self-check. No full suite, model, network, or quiet-machine task was run.

For the requested native schema change, the exact field-level diff is: add optional `source_files` to `BenchmarkImport` in `joulewise/suite.py`; allow it in `from_mapping`; validate each entry’s seven fields (`path`, `sha256`, `bytes`, `line_count`, `git_blob_sha1`, `lfs_pointer_blob_sha1`, `license_blob_sha1`); serialize it only when present so GSM8K hashes stay stable; and add a two-file acceptance case in `tests/test_suite.py`. Those paths were preserved under the exhaustive write scope.

## Residual risk

The magistrate should double-check the schema addition and native suite validation before campaign use, and review the factual discrepancy between the synthesis’s “arithmetic slip” claim and the matching computed total of 4,040.