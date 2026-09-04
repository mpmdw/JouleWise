# Bench ruling on Sol 266's NEEDS_RULING (R3-A) and the round-3 landing `47f083a2`, 2026-09-02

## Ruling (R3-A cross-profile assertion)

Sol 266 (file 34) returned NEEDS_RULING: each decode unit's
`declared_identity.workload_profile` is the TYPED profile, so after removing
`suite_manifest_set` it still carries `prompt_tokens: None`,
`prompt_text: None`, `dataset_ref: None`, and cannot equal the four-key plan
workload directly. Ruled: option 1 — drop the None-valued keys from the
declared profile, then require exact equality with the plan workload for
BOTH decode units (the null keys are typed-only placeholders, so what
remains is exactly the declared common profile; option 2's subset check
would admit undeclared extras). Bench edit under the bench-vs-session
threshold (one assertion block), `tests/test_d117_contrast_v5_pack.py`
inside `test_unstubbed_temp_pack_is_complete_and_validator_clean`.

## Executed evidence (bench, `wt-decode-id`, pasted)

```
$ TMPDIR=$S/tmpbench3 python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_unstubbed_temp_pack_is_complete_and_validator_clean 2>&1 | tail -3
Ran 1 test in 0.489s

OK
--- counterfactual: restore the literal
----------------------------------------------------------------------
Ran 1 test in 0.454s

FAILED (failures=1)
AssertionError: {'nam[52 chars]1, 'warmup_runs': 1, 'output_tokens': 512, 'prompt_tokens': 42} != {'nam[52 chars]1, 'warmup_runs': 1, 'output_tokens': 512}
  {'name': 'real_prompts_v1_chat_rendered',
   'output_tokens': 512,
-  'prompt_tokens': 42,
```

(The counterfactual wraps `generator.workload_for` in memory to re-add
`prompt_tokens = DECODE_PROMPT_TOKENS["A"]` on the decode branch during
`generate_pack`, then restores it.)

```
$ grep -n "def test_generated_v5_pack_refuses_tampered_declared_manifest_bytes\|def test_generated_v5_verify_refuses_tampered_declared_manifest_bytes" tests/test_d117_contrast_v5_pack.py
1111:    def test_generated_v5_pack_refuses_tampered_declared_manifest_bytes(self) -> None:
1142:    def test_generated_v5_verify_refuses_tampered_declared_manifest_bytes(self) -> None:
$ TMPDIR=$S/tmpbench3 python3 -m unittest tests.test_detection_floor tests.test_analysis_inputs tests.test_analysis_claims tests.test_identity_pins tests.test_analysis_integration tests.test_d165_dominance_closeout tests.test_d117_contrast_v5_pack tests.test_docs_freshness 2>&1 | tail -3
Ran 487 tests in 110.544s

OK (skipped=1)
$ shasum -a 256 configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json | cut -c1-16
1c0a4a119fa06984
$ git diff --check && echo CHECK-OK
CHECK-OK
```

## Magistrate read of the landing

- Contract diff read in full at the bench: the three dictated texts landed
  verbatim (79-col rewrap only); step 3's join reads as prose; the
  executable-evidence table gained the two manifest-tamper tests (exist at
  :1111/:1142) and the missing-root test. No factual correction was claimed
  by the seat and none was needed against the lines bench-read for file 32.
- `generate_configs.py`: exactly one line removed (:1321); D-166 digest
  unchanged.
- `tests/test_analysis_inputs.py:706–727` missing-root test; RED on the
  `OSError` counterfactual pasted by the seat (file 34).
- `docs/decision_log.md:8464–8467` addendum as dictated; original line
  untouched.

Next: delta re-audit by terra xhigh (file 36 brief; different model), then
the §5 fresh pass, integration replay, PR.
