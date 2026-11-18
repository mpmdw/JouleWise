BLOCK

**[HIGH] [VERIFIED] RL-182a(b).** At PR #813 head `6093a7454`, a one-line chained assignment in the adapter’s stamp block computed the synthetic prompt’s SHA-256 **after the prefill clock read and before the token clock read**. The AST check passed, and the cold, cache-hit, uncached and suite-item paths each measured exactly one tick. The merge gate is for check 1 to reject this assignment. [One-line diff](/private/tmp/jw-813-MB7hAtI8/check1.diff) · [Execution trace](/private/tmp/jw-813-MB7hAtI8/check1.log)

```sh
python3.13 -B /private/tmp/jw-813-MB7hAtI8/check1.py
```

| Ruling | Status | Edits |
|---|---|---|
| RL-182 §1.3 | PRESENT-VERBATIM | E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E17 |
| RL-185 | PRESENT-VERBATIM | E18 in B2a, E19 in B7 item 9 |

**RL-182a(a,c,d) passed.** The original S and Q reads of `Turn.first_token_ns` are byte-identical at lines 215 and 482. The flagged turn produced zero decode rows. Flat and below-threshold unequal-energy folds yielded `s_score_undefined`. E2, E10 and AM:47 match the addendum. [Text and field comparison](/private/tmp/jw-813-MB7hAtI8/registered.log) · [Focused tests](/private/tmp/jw-813-MB7hAtI8/focused.log)

**S and Q matched byte for byte** against `a36b28b73` on 22 accepted synthetic strata. `cmp` matched 27,626 bytes with Q words disabled and 27,677 enabled. `RUN_STATE.md` and `TASK_QUEUE.md` are byte-identical to the PR base and absent from its final diff. [Scorer outputs and hashes](/private/tmp/jw-813-MB7hAtI8/byte-check.txt)

**§1.4 accounted for all seven items.** (a) #787 and the release caller remain pre-C1 gates. (b) Benign-only DC refusal passed. (c) Numeric side-transfer values passed and booleans yielded null. (d) Tied ranks matched enumeration. (e) Mixed grids stayed separate. (f) W1’s missing-stamp count and maximum gap remain pre-C1 checks. (g) Prompts and the three-term fit are unchanged. [Gate text](/private/tmp/jw-813-MB7hAtI8/pre-c1.txt) · [Test results](/private/tmp/jw-813-MB7hAtI8/focused.log)

Prior replays rejected all earlier stamp mutations and refuted the signing-placeholder and lost-subject findings. Closure passed 6/6 with the same 16 inherited binding exceptions. The superseded timing replay stayed red as ruled. [Mutation replays](/private/tmp/jw-813-MB7hAtI8/prior.log) · [Binding comparison](/private/tmp/jw-813-MB7hAtI8/bindings.log)