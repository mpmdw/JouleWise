# D-166 prompt-0 Phase-2 implementation seat report

Status: **COMPLETE**

Base: `f4810d9b4b4d8ad31bfc77f734e72c838bf1257e` on
`feat/2026-09-05-d166-prompt0`. No commit was made.

## Change

- Replaced the modulo-eight decode assignment with
  `d166_fixed_prompt_zero.v1`. All ten decode blocks share prompt index 0 in
  both model arms. The thinking-off rendering policy, greedy forced-512 output
  policy, tokenizer/chat-template and token-ID pins, and
  `decode_prompt_shape_mismatch` refusal are unchanged.
- Added the prospective supersession record. It names
  `d166_block_prompt_cycle.v1`, the active fixed-zero rule, ratified Q-17-4
  authority, the Phase-1 dependency census, and the pre-collection ordering.
- The generator loads the record fail closed during configuration and again
  immediately before generation writes. A missing record, wrong active rule,
  malformed record, or non-zero active assignment refuses.
- Retargeted the former rotation and emitted-census regressions. The declared
  identity census contains the one used prompt-0 manifest with 20 members per
  model arm; all eight authenticated prompt manifests remain in the closed
  generated-pack inventory. Repointing an emitted config to prompt 1 remains
  covered and refuses as an undeclared suite manifest.
- Added regressions for the superseded and active IDs, missing record, wrong
  active rule, and a code mutation restoring the old cycle.

The production pack
`configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/` was not generated
and remains absent. Tests generated packs only under temporary directories.

## Verification

Focused methods were run first.

`python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_decode_assignment_is_fixed_zero_for_all_blocks_and_arms`

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.032s

OK
```

`python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_decode_assignment_supersession_names_cycle_rule`

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.028s

OK
```

`python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_decode_assignment_supersession_refuses_absent_record`

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

`python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_decode_assignment_supersession_refuses_wrong_active_rule`

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.005s

OK
```

`python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_decode_assignment_refuses_cycle_rule_mutation`

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.035s

OK
```

`python3 -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_decode_declaration_is_rule_derived_not_folded_from_emission`

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.949s

OK
```

Then the permitted module:

`python3 -m unittest tests.test_d117_contrast_v5_pack`

```text
............................................
----------------------------------------------------------------------
Ran 44 tests in 14.500s

OK
```

`git diff --check` exited 0 with no output.

## Verification notes

The first census retarget attempted to declare seven zero-count suite rows;
the existing identity validator correctly rejected non-positive declared
counts. The implementation was narrowed to the single used prompt-0 suite,
the drift probe was retargeted to an undeclared prompt-1 suite, and both the
focused method and full module then passed as shown above.

The discovery suite was not run, per the seat preflight rule. No measurement
checkout, agent launcher, or quiet-machine task was touched.

## Blockers

None. Production pack generation, identity-pin projection, custody receipts,
and clone proof remain intentionally deferred to the post-G2-a desk day.
