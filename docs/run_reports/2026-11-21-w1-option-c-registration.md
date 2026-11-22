# W1 option C registration text

Ed confirmed RL-198 in RUN_STATE 532 and 533. Mission M0 selected this
pre-signature desk task. The worktree was clean at the remote W1 base
`b2e01464d6d4fbf2901ff4d4154df9455104a12a`, with no existing remote topic branch
or PR. RL-198 §4 matched the supplied excerpt byte for byte at audit commit
`0a4d9d3cf`.

| Edit | Verification | Result |
| --- | --- | --- |
| P4:1086–1087, option C scope | Exact old bytes and exact replacement | PASS |
| P4:1157 and 1159, K HELD and K REFUTED disclosures | Two exact old matches and replacements. `test_option_c_disclosure_is_separate_from_k` | PASS |
| P4:1321–1322, physical check beside the curve | Exact old bytes and exact replacement | PASS |
| P4:1431–1433, B9 chair ruling 2 | Exact old bytes and exact replacement | PASS |
| P4:1434–1437, B9 interpretation | Exact old bytes and exact replacement | PASS |
| P4:576–579, move the P windows into v4 | Exact old bytes and exact replacement | PASS |
| Replace B8 | Exact old block and verbatim RL-198 replacement. `test_option_c_disclosure_is_separate_from_k` | PASS |
| Add B10 after B9 | Verbatim RL-198 block. `test_option_c_windows_follow_b9_and_stay_outside_the_series` | PASS |
| Record RS532 and RL-198 in DEVIATIONS | Single new row, `git diff --check` | PASS |
| W1 R1 protected sources | Compare all ten `R1_EXECUTED_SOURCES` blob IDs against W1 | PASS, 10/10 |
| §4.1 runtime disclosure | Exact identifier search across the W1 tree | NEEDS_SPEC |
| §4.2 RL-18 source | Look up the audit document at the W1 base | NEEDS_SPEC |

The byte check restored only the source line wraps identified by the ruling
and compared the entire edited protocol to the result of applying those
replacements to W1. The focused suites passed 50 tests with
`python3 -m unittest -v tests.align.test_protocol_v4_doc tests.test_check_gate_ledger`.
The local canonical suite was not run because the diff is registration prose
and its structural tests. The fixture census exited 2 because the environment
denied execution of `ps`. This leaves the census count unverified.

## NEEDS_SPEC

- **§4.1 disclosure emitter.** W1 has zero code or schema occurrences of the
  exact `positive_control_not_run` identifier. The draft registers B8's disclosure
  text. The lead needs to identify the emitter on the W1 line if the runtime
  rename and outcome values are expected in this PR.
- **§4.2 RL-18.** The audit decision file that owns RL-18 is absent from W1.
  The lead needs to name the target branch for the companion audit edit.
- **Council table row 2.** It still records the old option-B disclosure.
  RL-198 §4.3 names the B9 supersession and supplies no replacement for the
  table row. The lead needs to rule on a separate table-row edit.

Next step for the lead is to disposition the three scope findings and review
the draft against the W1 CI results before signature.
