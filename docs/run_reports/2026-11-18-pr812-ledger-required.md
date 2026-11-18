# PR #812 requires ledger authority at qualification launch

Astra's pipeline round 1 reproduced a qualification launch reaching
bootstrap with both ledger arguments omitted. A bootstrap failure on
that path left the prior attempt at the head of the ledger.
`0d03cb7833bb8b15bc391127a7fe5519b7d98602` requires the ledger path,
previous close receipt, span ID and exact close bound for the
qualification seed law in the shared launch function. It checks the
loaded kit before creating a fence or invoking bootstrap.

`test_qualification_bootstrap_requires_ledger_and_retains_failed_attempt`
refuses when both proof arguments or either one is omitted. Its complete
authority case reaches a synthetic failed bootstrap, then proves that
the next launch refuses and names the pending attempt. The direct
function regression verifies the same guard outside CLI parsing.
The audit's other findings were refuted.

The cumulative draft patch is based on audit head
`61377dc45e9be3163466ef33e57dc0281423fdbc`. It includes the six
regenerated items, their kits and queues, and the round-3 close-proof
checks. The three kit hashes were recomputed and all 114 frozen blobs
verified. Relative to the round-3 pin, only the launcher source changed
among frozen paths. The GitHub test-merge tree matches the pin's tree
`421f5c2694234e6f906f34980b3df3920ed402a0`.

All 111 focused tests, 1,552 Bash/Zsh gate checks and 91 pinned draft
checks passed with synthetic fixtures. Hosted CI covers the full
suite, including tests that send process signals.
The local fixture census returned exit 2 because the environment
denied `ps`.
Qualification remains `HOLD_FOR_FIT_FREEZE`. The lead owns the audit
branch commit, the next audit and exact-pin admission.
[PR #812](https://github.com/mpmdw/JouleWise/pull/812) · [Final-head CI](https://github.com/mpmdw/JouleWise/actions/runs/44270871439)
