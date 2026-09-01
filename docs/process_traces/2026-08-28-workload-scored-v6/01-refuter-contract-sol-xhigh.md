```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "DO-NOT-MERGE: source and set authentication fail open, while the stale branch deletes upstream artifacts including a _v5 surface.",
  "workspace": {
    "base_requested": "origin/main",
    "base_mode": "exact",
    "head_start": "0b7cb69952bc54215253affc8f4a2a39b67dbfc2",
    "head_end": "0b7cb69952bc54215253affc8f4a2a39b67dbfc2",
    "upstream_end": "0b7cb69952bc54215253affc8f4a2a39b67dbfc2",
    "branch": "feat/workload-scored-v6"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "DO-NOT-MERGE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The public manifest builder can stamp official provenance onto unauthenticated records",
        "question": "Q4",
        "location": "joulewise/benchmark_import.py:404"
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The aggregate scorer accepts arbitrary or empty sets while claiming pinned-set accuracy",
        "question": "Q3",
        "location": "joulewise/benchmark_import.py:782"
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "The endpoint diff deletes newer origin/main artifacts, including a _v5 projection surface",
        "question": "Q6",
        "location": "origin/main:scripts/paper_prefill_resolvability_projection.py:1"
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "Prompt and tokenizer generation pins are internally consistent but not independently bound to the reviewed panel pinset",
        "question": "Q4",
        "location": "joulewise/benchmark_import.py:55"
      }
    ],
    "questions": {
      "Q1": {
        "verdict": "HOLDS",
        "evidence": [
          "joulewise/floor_extraction.py:150",
          "joulewise/floor_extraction.py:716",
          "joulewise/floor_extraction.py:778",
          "joulewise/floor_extraction.py:1001",
          "tests/test_floor_extraction.py:4597"
        ],
        "refutation": "All committed v1 definitions and embedded bindings retained their stored digest; both/neither key sets, unknown versions, and extra keys were rejected; every v2 key participates in whole-object canonical hashing."
      },
      "Q2": {
        "verdict": "HOLDS-WITH-CAVEAT",
        "evidence": [
          "joulewise/analysis_engine/inputs.py:2552",
          "joulewise/analysis_engine/inputs.py:2584",
          "joulewise/bundle_read.py:1816",
          "tests/test_analysis_inputs.py:163"
        ],
        "refutation": "The scalar source is not literally byte-identical because its predicate was lifted into shape dispatch, but typed-JSON behavior is unchanged. The suite branch enforces hash equality and exact item_count-times-cap tokens; a missing workload_provenance.suite block fails closed."
      },
      "Q3": {
        "verdict": "FAILS",
        "evidence": [
          "joulewise/benchmark_import.py:49",
          "joulewise/benchmark_import.py:424",
          "joulewise/benchmark_import.py:736",
          "joulewise/benchmark_import.py:782",
          "joulewise/suite.py:856"
        ],
        "refutation": "k=8, cap 384, checker identity, four outcomes, and quarantine text are encoded, but the scoring consumer does not authenticate the eight-item set. One-item and empty inputs receive pinned-set accuracy output. Affine control is not yet wired to this workload, consistent with the prohibited analysis-arm boundary."
      },
      "Q4": {
        "verdict": "FAILS",
        "evidence": [
          "joulewise/benchmark_import.py:124",
          "joulewise/benchmark_import.py:279",
          "joulewise/benchmark_import.py:404",
          "joulewise/benchmark_import.py:518",
          "scripts/gen_gsm8k_scored.py:60"
        ],
        "refutation": "The canonical CLI authenticates the upstream bytes and the committed subset reconstructs to fcfc8ab8e8ce5ba2550d156d7a3242132b5216a89c7404053dae50105249231c. The public builder nevertheless accepts arbitrary records and prompt metadata, then stamps the fixed official source hash."
      },
      "Q5": {
        "verdict": "KEEP",
        "evidence": [
          "tests/test_gsm8k_import.py:139",
          "tests/test_gsm8k_import.py:163",
          "tests/test_gsm8k_import.py:223",
          "tests/test_gsm8k_import.py:233",
          "tests/test_gsm8k_import.py:270",
          "tests/test_gsm8k_import.py:367"
        ],
        "refutation": "Canonical tests do not yet subsume positive loader authentication, subset edge cases, capped-wrong scoring, scorer/annotation tamper refusal, deterministic build/order checks, or exhaustive committed-mirror prompt-token checks."
      },
      "Q6": {
        "verdict": "FAILS",
        "evidence": [
          "origin/main:docs/paper/round7/bibliography-verification.md:1",
          "origin/main:docs/paper/round7/prefill-resolvability-projection.json:1",
          "origin/main:docs/paper/round7/prefill-resolvability-projection.md:1",
          "origin/main:scripts/paper_prefill_resolvability_projection.py:1",
          "docs/phase_2/suite_implementation_research.md:126"
        ],
        "refutation": "No _v6 analysis-manifest arm or floor cell was added and D-041 itself remains untouched, but the stale endpoint deletes upstream PR #244/#245 artifacts, including a _v5 projection surface."
      }
    },
    "fix_list": [
      "Rebase onto current origin/main and preserve all four upstream artifacts, then repeat endpoint review.",
      "Require an authenticated loader receipt or authenticate the source inside the manifest builder; arbitrary records must not receive official GSM8K provenance.",
      "Bind aggregate scoring to the full manifest and sidecar, exact ordered k=8 set, and manifest SHA; reject empty, partial, reordered, or foreign sets.",
      "Enforce reviewed PR #241 panel revisions and literal chat, tokenizer, template, and empty-think pins at generation time.",
      "Transfer the uncovered deprecated-import assertions before deleting its script or test."
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_analysis_inputs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 0.005s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_suite.SuiteManifestTests.test_all_retained_v1_manifests_migrate_with_pinned_hashes tests.test_suite.SuiteManifestTests.test_v2_scoring_and_benchmark_import_are_exact_and_hash_validated tests.test_suite.SuiteManifestTests.test_v1_still_defers_v2_scoring_and_benchmark_import",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.012s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check origin/main..HEAD",
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
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests 2>&1 | tail -40",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: [Errno 2] No usable temporary directory found",
          "Ran 2731 tests in 95.845s",
          "FAILED (errors=1722, skipped=114)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "HEAD predates origin/main changes and deletes four upstream artifacts in the requested endpoint diff.",
      "needs": "Rebase onto origin/main, preserve the artifacts, and re-review the resulting head."
    },
    {
      "id": "R2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The canonical suite could not obtain a temporary directory under the read-only environment.",
      "needs": "Rerun the canonical suite in a writable lead-controlled workspace."
    },
    {
      "id": "R3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Transformers was unavailable, so exact local prompt re-tokenization tests were skipped; committed raw hashes and tokenizer identities were inspected instead.",
      "needs": "Run the mirror tests with the pinned Transformers dependency available."
    }
  ]
}
```

## Findings

### Blockers

- **F1 — Upstream authentication can be bypassed.** The loader at [benchmark_import.py:124](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:124) authenticates SHA-256, byte count, git-blob SHA-1, and line count. But [build_gsm8k_scored_manifest at line 404](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:404) accepts caller-provided records and rendered metadata, then stamps the fixed official hashes at [line 518](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:518). An adversarial eight-record synthetic dataset was accepted and labeled with official GSM8K provenance. The safe CLI call sequence does not make this public construction path fail-closed.

- **F2 — Accuracy quarantine is documented, not enforced.** The committed manifest correctly encodes eight items, cap 384, the pinned checker, and quarantine metadata. The four-way table is implemented at [benchmark_import.py:782](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:782). However, that function authenticates neither the manifest nor the exact set: it accepts a one-item sidecar and even an empty sidecar, returning aggregate accuracy labeled as belonging to the pinned set. [suite.py:856](/Users/edr/code/JouleWise-wt-scored/joulewise/suite.py:856) merely requires nonempty quarantine prose. This violates D-166’s set-property boundary.

- **F3 — The requested endpoint violates boundary honesty.** `origin/main..HEAD` deletes four files introduced upstream, including `scripts/paper_prefill_resolvability_projection.py`, a `_v5` projection surface. This is merge-blocking regardless of whether the deletions were intentional; the branch must be rebased and reviewed again. Apart from those deletions, no `_v6` floor cell or analysis-manifest arm was introduced, and the D-041-fenced decisions remain untouched.

### Should fix

- **F4 — The prompt pin chain is self-consistent but insufficiently externalized.** The committed subset reconstructs offline to the required `fcfc8ab8…` digest, and the current chat/template/tokenizer values match the inspected PR #241 panel world. Nevertheless, [PROMPT_TEMPLATE_SHA256 at line 55](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:55) is computed from the current mutable template, [render_prompts at line 279](/Users/edr/code/JouleWise-wt-scored/joulewise/benchmark_import.py:279) only establishes agreement between two local mirrors, and the builder accepts caller-supplied rendered hashes. Generation should compare against independently reviewed literal panel pins and revisions.

Q5 is **KEEP**. The assertions not yet transferred from [test_gsm8k_import.py:139](/Users/edr/code/JouleWise-wt-scored/tests/test_gsm8k_import.py:139) include positive four-part source authentication, subset duplicate/order/invalid-k behavior, capped-wrong scoring, checker and annotation tamper refusal, deterministic build and order rejection, and exhaustive committed-mirror prompt token IDs. Deleting that script and test now would reduce coverage.

## Residual risk

The full suite result is not product evidence: 1,722 errors arose because the read-only environment exposed no usable temporary directory. Focused pure tests passed. Exact prompt re-tokenization also remains unverified because the pinned Transformers dependency was unavailable; raw artifact hashes and tokenizer identities did match.