# WP19 failed-identity receipt for LR-WP19-1

The W1 signing worktree started clean at `10ef5a3af`. Mission M0 found no
active stop card. The lead's LR-WP19-1 directive selects this synthetic-only
builder task. The protocol §9 WP19 and R11/R07 disposition govern the receipt.

WP19 checks the registered X seed across the ordered live rows. When the
coverage is complete, both renders match, and at least one seed differs, the
writer records a failed receipt with `seed_binding.reason_code`,
`seed_binding.turns_checked`, and `seed_binding.turns_mismatched`. Exit 0
indicates that the receipt was written. The verdict and predeclaration convey
the identity outcome. The kit accepts a valid failed receipt through the
existing registration path, and the desk reports the contrast INCONCLUSIVE.
The receipt remains a strict Git-bound registration artifact.

## Gate evidence and handoff

| Check | Evidence |
| --- | --- |
| Independent review | Ready for reviewer execution of the synthetic tests below. Independent review is pending. |
| Local tests | Taskpolicy utility, one worker. Eight focused tests passed. The synthetic kit witness also refused a byte change to the signed WP19 receipt. |
| Final-head CI | The PR head is pinned in its ledger. CI status is tracked on the PR. |
| Cold final pass | Pending with the lead. The synthetic run grants no native validation or signing approval. |
| Findings | The build addresses the R1 seed-binding receipt gap by retaining the registered comparator and using the existing non-veto disposition. Review findings are pending. |

The focused command exited 0:

```sh
taskpolicy -b python3.13 -B -m unittest tests.align.test_v4_wp19 \
  tests.align.test_v4_registration.RegistrationTests.test_wp19_requires_all_turns_and_live_x_with_static_proof \
  tests.align.test_v4_registration.RegistrationTests.test_wp19_zero_native_turns_is_a_retained_nonveto_failure_never_a_pass \
  tests.align.test_v4_registration.RegistrationTests.test_wp19_renders_fresh_history_from_recorded_outputs
```

State generation check: `taskpolicy -b python3.13 -B scripts/gen_state.py --check`
exited 0. The unrestricted canonical suite is outside the synthetic-only
instruction because existing discovery tests read repository fixture data.

Review the draft against `ops/2026-11-26-w1-signing`. After review and
integration, the authorized lead can run WP19 against the accepted R1 source
and use the validated receipt in W1 signing.
