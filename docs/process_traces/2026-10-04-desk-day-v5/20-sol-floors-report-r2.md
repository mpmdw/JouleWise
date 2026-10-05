```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_SCOPE: ladder registrations, end-state authority and component planning implemented; both 2048 packs check; custody repin and importer verification remain blocked.",
  "workspace": {"base_requested":"03235037","base_mode":"exact","head_start":"03235037d2cccafd83debbf53ff733b79f1825a1","head_end":"03235037d2cccafd83debbf53ff733b79f1825a1","upstream_end":"03235037d2cccafd83debbf53ff733b79f1825a1","branch":"feat/2026-10-04-v5-floor-prefill-from-pin"},
  "pathspec": ["configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py","configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py","joulewise/paper_reported_energy.py","docs/contracts/paper_reported_energy.md","tests/test_d117_floor_qwen3_v5_generate.py","tests/test_paper_reported_energy.py","tests/test_d117_floor_qwen25_1p5b_plan.py","tests/test_campaign_generator_core.py","tests/fixtures/paper_reported_energy/p512_replay.json"],
  "unowned_dirty": [],
  "verdict": {"implementation":"partial","acceptance":"needs_ruling"},
  "verification": [
    {"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp/dd5-floors2 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-floors2 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_d117_floor_qwen3_v5_generate.py tests/test_paper_reported_energy.py tests/test_d117_floor_qwen25_1p5b_plan.py tests/test_campaign_generator_core.py > /tmp/dd5-floors2/targeted-final.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED tests/test_paper_reported_energy.py::ReportedEnergyTests::test_d173_is_only_evidence_entry_and_fixture_cannot_render"]},"expected":{"exit_code":0,"tail_regex":"(?m)^\\d+ passed"}},
    {"id":"V2","kind":"suite","cmd":"TMPDIR=/tmp/dd5-floors2 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-floors2 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_generator_head_pin_relation.py tests/test_paper_rendering.py tests/test_paper_comparison_placements.py tests/test_arm_readiness_lifecycle.py tests/test_arm_readiness_integration.py tests/test_arm_readiness_dry_run.py tests/test_arm_readiness_registry.py tests/test_arm_readiness_evidence_author.py tests/test_family_marker.py tests/test_launch_window.py tests/test_receipt_histsem.py > /tmp/dd5-floors2/importers-final.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":2,"tail":["!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!","3 failed, 126 passed, 1 skipped, 2 warnings, 1550 subtests passed in 1488.98s (0:24:48)"]},"expected":{"exit_code":0,"tail_regex":"(?m)^\\d+ passed"}},
    {"id":"V3","kind":"test","cmd":"TMPDIR=/tmp/dd5-floors2 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-floors2 /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_d117_floor_qwen3_v5_generate.py::D117FloorQwen3V5PackTests::test_generators_are_deterministic_closed_and_checkable > /tmp/dd5-floors2/clone-env-final.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["1 passed, 2 subtests passed in 30.49s"]},"expected":{"exit_code":0,"tail_regex":"1 passed, 2 subtests passed"}},
    {"id":"V4","kind":"smoke","cmd":"TMPDIR=/tmp/dd5-floors2 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-floors2 /Users/edr/code/JouleWise/.venv/bin/python -B configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py --check --output-root /tmp/dd5-floors2/generated","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["verified d117_floor_qwen3-1p7b_v5 unfrozen draft: 100 science configs; calibration_plan_sha256=f4992afbfa3e948c70714c6a463dceef73a638a98178379f8f992cb1e6505c54; plan_tree_sha256=9ee34f13bab96361db6680121b60897c19808033e1c82d094c19732f8ae1764d"]},"expected":{"exit_code":0,"tail_regex":"verified.*100 science configs;"}},
    {"id":"V5","kind":"smoke","cmd":"TMPDIR=/tmp/dd5-floors2 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-floors2 /Users/edr/code/JouleWise/.venv/bin/python -B configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py --check --output-root /tmp/dd5-floors2/generated","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["verified d117_floor_qwen3-8b_v5 unfrozen draft: 100 science configs; calibration_plan_sha256=fed2a431162d8f0938d573a33d048862dac36947a7d2828280f4174c8724d949; plan_tree_sha256=c96869c64610d08d2cafc6fa6780bc85d17d0b09cfd8146638748df97169318a"]},"expected":{"exit_code":0,"tail_regex":"verified.*100 science configs;"}},
    {"id":"V6","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V7","kind":"inspection","cmd":"TMPDIR=/tmp/dd5-floors2 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans","cwd":".","observed":{"result":"fail","exit_code":2,"tail":["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]},"expected":{"exit_code":0,"tail_regex":"^\\[\\]$"}}
  ],
  "flags": [
    {"id":"F1","kind":"scope_deviation","level":"blocking","text":"NEEDS_SCOPE: validator changes stale the synthetic reported_energy_parents receipt and inventory digests in configs/paper_supply/supply_map.json. That unlisted file is unchanged. A two-field proposal is at /tmp/dd5-floors2/supply-map-fixture-repin.patch.","needs":"Grant this exact path or apply the patch lead-side, then rerun custody tests."},
    {"id":"F2","kind":"environment","level":"nonblocking","text":"Sandbox denied git staging at the parent index.lock (exit 128). Uncommitted; no push.","needs":"Lead reviews and commits."},
    {"id":"F3","kind":"verification_gap","level":"blocking","text":"Expanded importer run was interrupted after stalling; managed pytest exited 2. Three observed failures are the stale custody fixture. Remaining module completion and descendant cleanup are unverified; sandbox denies ps and orphan census exited 2.","needs":"Lead checks descendants and completes importer verification in an environment permitting process observation/control."},
    {"id":"F4","kind":"scope_deviation","level":"nonblocking","text":"Legacy clone checks briefly used /tmp when TMPDIR was cleared; contexts cleaned up. Fixed fixture inherits scratch env; focused check passes.","needs":""}
  ],
  "scope_expansion": {"requested_paths":["configs/paper_supply/supply_map.json"],"reason":"The changed reported-energy validator changes the synthetic custody source census, invalidating its receipt and inventory envelope digests.","blocked_work":"Green reported-energy custody and rendering tests.","minimal_change":"Update only expected_sha256 for fixture.reported_energy_parents.receipt and .inventory; proposed two-field patch is in scratch."}
}
```

## Change

Implemented ladder-specific registrations and census checks, preserving historical p512 manifest and projection digests. Mixed lengths and p512 aliases refuse. Both floors accept the closed 4096 end-state record; only the issuer schema ID and key set were copied. Decode continues to force 512 output tokens.

Planning uses 50 long-prompt members, each with warmup and measured prefill: `P = 100 × L × rate`. Fixed allowance is `F = 18840 − 100 × 512 × rate`; span is `1.2 × (F + P)`.

Both generators carry `PLANNING_BASELINE_SECONDS = 18840.0`. Their `PLANNING_PREFILL_SECONDS_PER_TOKEN` values are 0.0005217025056481362 for 1.7B and 0.0015653804875910282 for 8B, using the larger per-rung mean rate from the p512/p2048 diagnostics.

| Floor | Tokens | Prefill s | Fixed s | Headroom s | Span min |
|---|---:|---:|---:|---:|---:|
| 1.7B | 512 | 26.71 | 18,813.29 | 3,768.00 | 376.80 |
| 8B | 512 | 80.15 | 18,759.85 | 3,768.00 | 376.80 |
| 1.7B | 1024 | 53.42 | 18,813.29 | 3,773.34 | 377.33 |
| 8B | 1024 | 160.29 | 18,759.85 | 3,784.03 | 378.40 |
| 1.7B | 2048 | 106.84 | 18,813.29 | 3,784.03 | 378.40 |
| 8B | 2048 | 320.59 | 18,759.85 | 3,816.09 | 381.61 |
| 1.7B | 4096 | 213.69 | 18,813.29 | 3,805.40 | 380.54 |
| 8B | 4096 | 641.18 | 18,759.85 | 3,880.21 | 388.02 |

Fixed allowance includes decode, cooldowns, calibration, references, bounds and other overhead.

## Verification notes

The four observed custody/rendering failures require the unlisted supply-map repin. Your exhaustive `WRITE_SCOPE` excludes that file. Grant its exact path or apply the [two-field patch](/tmp/dd5-floors2/supply-map-fixture-repin.patch), then rerun the failed tests.

The importer run was interrupted after stalling, so verification remains incomplete. The initial baseline overlapped edits and was discarded. Changes remain uncommitted because Git staging was denied.

## Residual risk

Descendant cleanup is unverified because `ps` is denied; the lead must check before quiet-machine work.

Timing values are planning estimates. The fixed allowance is inherited, and diagnostic rates use five small-model members and one large-model member per rung; they are not validated window limits.