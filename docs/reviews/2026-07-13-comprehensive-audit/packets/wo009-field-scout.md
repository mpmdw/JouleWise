```json
[
  {
    "field": "execution_policy.order_policy",
    "declared_in": [
      "joulewise/suite.py:281",
      "joulewise/suite.py:304",
      "joulewise/gensuite/__init__.py:1415",
      "joulewise/gensuite/__init__.py:1446",
      "joulewise/workloads.py:265",
      "joulewise/workloads.py:347",
      "scripts/gen_jw_mixed.py:76",
      "scripts/gen_affine_smoke.py:37",
      "configs/suite_manifests/affine_smoke_v1.json:14",
      "configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:15",
      "configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:15",
      "configs/suite_manifests/mock_suite_manifest.json:18"
    ],
    "consumed_by": [
      "joulewise/suite.py:810",
      "joulewise/suite.py:839",
      "joulewise/adapters/mock_runtime.py:211",
      "joulewise/adapters/mock_runtime.py:236",
      "joulewise/adapters/mock_runtime.py:364",
      "joulewise/adapters/mlx_runtime.py:276",
      "joulewise/adapters/mlx_runtime.py:305",
      "joulewise/adapters/mlx_runtime.py:439",
      "joulewise/controller.py:860",
      "joulewise/controller.py:1042",
      "joulewise/bundle_read.py:835",
      "joulewise/bundle_read.py:888",
      "joulewise/bundle_read.py:890",
      "joulewise/bundle_read.py:985",
      "joulewise/bundle_read.py:1094",
      "joulewise/bundle_read.py:1199",
      "joulewise/bundle_read.py:1228",
      "scripts/run_campaign.py:1239",
      "scripts/run_campaign.py:1241"
    ],
    "enforced": "full",
    "doc_promise": "D-056, docs/decision_log.md:2858-2869: selects a closed manifest/round-robin/Latin-square block-order policy; strict validation recomputes order and order_seed.",
    "recommendation": "enforce",
    "rationale": "Closed vocabulary drives realized block order and strict recomputation in both adapters and bundle validation."
  },
  {
    "field": "execution_policy.within_bundle_repeats",
    "declared_in": [
      "joulewise/suite.py:282",
      "joulewise/suite.py:309",
      "joulewise/gensuite/__init__.py:1447",
      "joulewise/workloads.py:348",
      "configs/suite_manifests/affine_smoke_v1.json:16",
      "configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:17",
      "configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:17",
      "configs/suite_manifests/mock_suite_manifest.json:19"
    ],
    "consumed_by": [
      "joulewise/suite.py:771 (validation-only constant check; bounded runtime search found no execution consumer)"
    ],
    "enforced": "partial",
    "doc_promise": "C-015, docs/research_question_bank.md:120-129: each distinct item executes once (r_within=1); within-bundle repeats are reserved for sentinels and never inflate n.",
    "recommendation": "reserved-compat",
    "rationale": "Validation pins 1, while runtime ignores the field; sentinel repeats are materialized as duplicate tagged items."
  },
  {
    "field": "execution_policy.cooldown_policy",
    "declared_in": [
      "joulewise/suite.py:283",
      "joulewise/suite.py:313",
      "joulewise/gensuite/__init__.py:1448",
      "joulewise/workloads.py:349",
      "configs/suite_manifests/affine_smoke_v1.json:12",
      "configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:13",
      "configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:13",
      "configs/suite_manifests/mock_suite_manifest.json:20"
    ],
    "consumed_by": [
      "NONE FOUND (bounded search: rg for cooldown_policy and execution_policy.cooldown_policy over the repository; hits only schema/parser, generators, manifests, fixtures/tests, and docs)"
    ],
    "enforced": "none",
    "doc_promise": "C-015, docs/research_question_bank.md:129-130 promises no per-item micro-cooldowns and back-to-back items; D-005/D-014 place actual cooldown between bundle repetitions.",
    "recommendation": "descriptive-provenance",
    "rationale": "D-014 cooldown exists independently at experiment level; this manifest string neither selects nor verifies that behavior."
  },
  {
    "field": "execution_policy.cache_policy",
    "declared_in": [
      "joulewise/suite.py:284",
      "joulewise/suite.py:316",
      "joulewise/gensuite/__init__.py:1449",
      "joulewise/workloads.py:350",
      "configs/suite_manifests/affine_smoke_v1.json:11",
      "configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:12",
      "configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:12",
      "configs/suite_manifests/mock_suite_manifest.json:21"
    ],
    "consumed_by": [
      "NONE FOUND (bounded search: rg for cache_policy and execution_policy.cache_policy over the repository; hits only schema/parser, generators, manifests, fixtures/tests, and docs)"
    ],
    "enforced": "none",
    "doc_promise": "C-015, docs/research_question_bank.md:127-133 and :151-154 requires cache metadata so sentinels can characterize cache effects; no authority defines warm_cache/cold_between_bundles enforcement.",
    "recommendation": "descriptive-provenance",
    "rationale": "Warm/cold values diverge across hashed manifests but no runtime or validator establishes the declared cache condition."
  },
  {
    "field": "execution_policy.warmup_policy",
    "declared_in": [
      "joulewise/suite.py:285",
      "joulewise/suite.py:319",
      "joulewise/gensuite/__init__.py:1450",
      "joulewise/workloads.py:351",
      "configs/suite_manifests/affine_smoke_v1.json:15",
      "configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:16",
      "configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:16",
      "configs/suite_manifests/mock_suite_manifest.json:22"
    ],
    "consumed_by": [
      "NONE FOUND (bounded search: rg for warmup_policy and execution_policy.warmup_policy over the repository; hits only schema/parser, generators, manifests, fixtures/tests, and docs)"
    ],
    "enforced": "none",
    "doc_promise": "docs/phase_2/suite_implementation_research.md:130 explicitly defers honoring this field; docs/specs/c027/p2-040_reducer_gate_correctness.md:742 says not to implement it.",
    "recommendation": "reserved-compat",
    "rationale": "Authority explicitly defers and later forbids implementation; retaining it only as reserved legacy shape avoids false runtime authority."
  },
  {
    "field": "execution_policy.default_output_policy",
    "declared_in": [
      "joulewise/suite.py:286",
      "joulewise/suite.py:322",
      "joulewise/gensuite/__init__.py:1451",
      "joulewise/workloads.py:352",
      "configs/suite_manifests/affine_smoke_v1.json:13",
      "configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:14",
      "configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:14",
      "configs/suite_manifests/mock_suite_manifest.json:23"
    ],
    "consumed_by": [
      "joulewise/adapters/mock_runtime.py:385",
      "joulewise/adapters/mlx_runtime.py:455"
    ],
    "enforced": "partial",
    "doc_promise": "docs/contracts/run_bundle_layout.md:229-232 promises it is recorded as bundle-level output-policy provenance with summed planned/emitted tokens; no fallback or item-consistency promise exists.",
    "recommendation": "descriptive-provenance",
    "rationale": "Adapters use it only to label bundle rollup provenance; every item still requires an explicit behavioral output policy."
  },
  {
    "field": "items[].output_policy",
    "declared_in": [
      "joulewise/suite.py:552",
      "joulewise/suite.py:596",
      "joulewise/gensuite/__init__.py:1400",
      "joulewise/workloads.py:246",
      "configs/suite_manifests/affine_smoke_v1.json:42 (first of 26 item declarations)",
      "configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:43 (first of 48 item declarations)",
      "configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:43 (first of 5 item declarations)",
      "configs/suite_manifests/mock_suite_manifest.json:66 (first of 5 item declarations)"
    ],
    "consumed_by": [
      "joulewise/adapters/mock_runtime.py:426",
      "joulewise/adapters/mock_runtime.py:528",
      "joulewise/adapters/mlx_runtime.py:512",
      "joulewise/adapters/mlx_runtime.py:555",
      "joulewise/adapters/mlx_runtime.py:571",
      "joulewise/bundle_read.py:1111"
    ],
    "enforced": "full",
    "doc_promise": "D-045, docs/decision_log.md:2392-2400 and implementation research :136-138 define fixed-budget success/underrun and natural-EOS capped behavior; SUB-3 closes the vocabulary.",
    "recommendation": "enforce",
    "rationale": "Both runtime adapters apply EOS/status behavior from each item, and strict validation checks fixed-budget completion."
  },
  {
    "field": "items[].status_policy",
    "declared_in": [
      "joulewise/suite.py:553",
      "joulewise/suite.py:601",
      "joulewise/gensuite/__init__.py:1401",
      "joulewise/workloads.py:247",
      "configs/suite_manifests/affine_smoke_v1.json:58 (first of 26 item declarations)",
      "configs/suite_manifests/jw_mixed_v1_qwen25_15b.json:58 (first of 48 item declarations)",
      "configs/suite_manifests/jw_sentinel_v1_qwen25_15b.json:571 (first of 5 item declarations)",
      "configs/suite_manifests/mock_suite_manifest.json:67 (first of 5 item declarations)"
    ],
    "consumed_by": [
      "NONE FOUND (bounded search: rg for status_policy and .status_policy over the repository; hits only schema/parser, generators, 84 manifest declarations, fixtures/tests, and docs)"
    ],
    "enforced": "none",
    "doc_promise": "docs/phase_2/suite_implementation_research.md:137 says malformed may result from violating the declared structural check; SUB-3 permits only none and says growth requires a decision.",
    "recommendation": "reserved-compat",
    "rationale": "Only none validates and no adapter reads it; current malformed handling is independent of this field."
  }
]
```
BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Enumerated all eight suite-manifest policy fields, traced operational consumers and bounded absences, and checked all four effective examples under configs/suite_manifests; configs/suites does not exist.","pathspec":[],"verification":["Read WO-009 and C1-010 in docs/reviews/2026-07-13-comprehensive-audit/register.jsonl","Repository-wide rg inventory found six execution-policy fields and two per-item policy fields, with no additional suite policy keys","Repository-wide bounded consumer searches completed for all eight fields","jq inspection confirmed four effective manifests and 84 declarations each of items[].output_policy and items[].status_policy","Read-only audit; no files changed"],"flags":["no_edits"]}