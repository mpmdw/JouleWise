BLOCK

**[HIGH] [VERIFIED] RL-182a(b), check 1.** On PR #813 at `07ebee6c8`, a mutation confined to the adapter’s stamp block hashed the synthetic prompt between prefill end and token 0. **Both checks passed on the registered first turn.** The AST check recognized ordinary assignments but skipped annotated assignments on the executed branch. The clock still measured exactly one tick. A second mutation on a turn reusing five cached tokens also passed both PR boundary tests. [First-turn diff](/private/tmp/jw813-r5.J87QGW3A/first-turn.diff) · [Cache-hit diff](/private/tmp/jw813-r5.J87QGW3A/check1.diff) · [Replay output](/private/tmp/jw813-r5.J87QGW3A/check1.log)

```sh
python3.13 -B /private/tmp/jw813-r5.J87QGW3A/check1.py
```

| Status | Edits |
|---|---|
| PRESENT-VERBATIM · RL-182 §1.3 | E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E17 |
| PRESENT-VERBATIM · RL-185 | E18 in B2a, E19 in B7 item 9 |

**RL-182a(a,c,d) passed.** Both `Turn.first_token_ns` reads are byte-identical, now at lines 215 and 482. The flagged turn produced zero decode rows. Flat-energy and below-threshold unequal-energy folds produced no S score. E2, E10 and AM:47 match the addendum. [Text and field checks](/private/tmp/jw813-r5.J87QGW3A/registered.log) · [E18/E19 comparison](/private/tmp/jw813-r5.J87QGW3A/rl185.log) · [Focused tests](/private/tmp/jw813-r5.J87QGW3A/focused.log)

**S and Q matched byte for byte** against `a36b28b73` on 22 accepted synthetic strata. `cmp` matched 27,626 bytes with Q words disabled and 27,677 enabled. `RUN_STATE.md` and `TASK_QUEUE.md` are byte-identical to the PR base and absent from its final diff. [Scorer comparison](/private/tmp/jw813-r5.J87QGW3A/byte-check.txt)

**§1.4:** (a) #787 and the named release caller remain pre-C1 gates. (b) Benign-only DC refusal passed. (c) Numeric side transfer passed and booleans yielded null. (d) Ties matched enumeration. (e) Mixed grids stayed separate. (f) W1’s missing-stamp count and maximum gap remain pre-C1 checks. (g) Prompts and the three-term fit are unchanged. [Gate text](/private/tmp/jw813-r5.J87QGW3A/gates.txt)

Prior replays refuted the signing-placeholder and lost-subject findings. Closure passed 6/6 with the same 16 inherited binding exceptions. The superseded timing replay stayed red as ruled. The remaining merge gate is for check 1 to reject the in-block mutation above.