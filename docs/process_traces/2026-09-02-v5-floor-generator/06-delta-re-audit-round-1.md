# Delta re-audit of fix round 1 at 7ad3f3e0 (terra xhigh, direct run), verbatim

```json
{"schema":"claude-codex-report/v1","genre":"review","status":"clean","completion":"complete","summary":"Round-one cures pass all requested re-audits at exact HEAD 7ad3f3e0; verdict LANDABLE.","workspace":{"base_requested":"4e742b5b","base_mode":"exact","head_start":"7ad3f3e0a4cfc68f97daf9e458ccd6ab07deb590","head_end":"7ad3f3e0a4cfc68f97daf9e458ccd6ab07deb590","upstream_end":null,"branch":"feat/2026-09-02-v5-floor-generator"},"pathspec":[],"unowned_dirty":[],"verdict":{"decision":"LANDABLE","findings":[]},"verification":[{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_floor_qwen3_v5_generate tests.test_d117_contrast_v5_pack","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 38 tests in 10.760s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 38 tests.*OK"}},{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_floor_qwen3_v5_generate.D117FloorQwen3V5PackTests.test_generators_are_deterministic_closed_and_checkable tests.test_d117_floor_qwen3_v5_generate.D117FloorQwen3V5PackTests.test_contrast_references_resolve_to_matching_floor_plan_digests","cwd":"$TMPDIR/floorgen-generation.J9OrcV","observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 5.559s","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 2 tests.*OK"}},{"id":"V3","kind":"inspection","cmd":"git diff --check 4e742b5b -- configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py tests/test_d117_floor_qwen3_v5_generate.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[]}
```

## Findings

| Severity | ID | Result |
|---|---|---|
| — | — | No blocker, should-fix, or nit findings. **LANDABLE**. |

| Replay | ALPHA observed | BETA observed |
|---|---|---|
| SHA-rebound ladder missing `schema_version` | `prefill_prompt_pin_invalid: prompt_ladder` | same |
| SHA-rebound ladder missing `prompt_sentence` | `prefill_prompt_pin_invalid: prompt_ladder` | same |
| Self-consistent `repeat_count: true` | `prefill_prompt_pin_invalid: prompt realization` | same |
| Selection wrong schema | `selection_record_schema_version_invalid` | same |
| Selection wrong status | `selection_record_status_invalid` | same |
| Selection `collection_prefill_tokens: 1024` | `selection_record_collection_prefill_tokens_mismatch` | same |
| Temporary `threshold: 1.99` | committed `test_alpha_dominance_registration_matches_contrast` failed, exit 1 | committed `test_beta_dominance_registration_matches_contrast` failed, exit 1 |

- The base→HEAD changed patch bodies for both generators are byte-for-byte identical after diff metadata removal: `changed_logic_patch_equal=True`.
- In a clean `$TMPDIR` archive, the fixture-pin deterministic-generation and contrast-reference tests passed: two identical floor generations, `--check` clean, and both contrast producer-plan references resolved with matching digests.
- Same-signature disposition versus 02/03: PFP-001, F1, and F4 no longer reproduce; F3’s requested p42 provenance addendum is present in `01-sol-landing-report.md:228-230`. F2 remains explicitly out of this object.

Focused-suite tail:

```text
......................................
----------------------------------------------------------------------
Ran 38 tests in 10.760s

OK
```

## Residual risk

Only synthetic fixture pins were exercised; issued G2-a bundle/live-hardware validation remains a separate gate. Checkout stayed clean; no repository files were written.