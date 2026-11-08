# v5 ruling revision 3 — Sol2 review record

Task: `v5-ruling-delta3`, independent **Sol2** seat, docs only.
Branch: `align/2026-11-08-v5design-ruling-delta3-sol2` (already created at
intake). Candidate: `b606d9788cd0cb25e0c85903ba7c75116edad894`;
reviewed delta: `7d2e43464..b606d9788`.

Delivered [the review](../align/squeeze/v5-design/ruling-delta3-review-sol2.md).
**SIGN_WITH_CHANGES:** two HIGH findings (nominal-size certification;
conditional-mean fallback versus the stated null), two MED findings
(H4 date composition/weights; CAP units/yield accounting). The S/E evidence
boundary, adverse point bound, nominal calibration caveat, main ledger and
local access/quarantine obligations are repaired at ruling level. Future
implementation, size/power and native gates remain unverified.

## Authority, intake and scope

- Read root AGENTS/CLAUDE instructions, Mission M0, targeted run-state/queue
  sections, AP/D-062, orchestration and relevant authority objects. No active
  stop card was present. This is explicitly requested documentation/review
  work in the agent lane; it does not select a measurement task from the queue.
- Read both complete round-2 delta reviews from local Git objects:
  DS1 `8c2c6c1cec136c724c83c9526cac1e3ae26a3e18`,
  DS2 `94acc5b815d79dbfb8d6a4c31aab50114c69faee`.
- Verified the newly pinned R12 in `319f6a51d:RUN_STATE.md`, item 214.
  Absolute data paths appearing in repository text were treated as text only.
- Initial worktree was clean on the requested branch. No other writer's work
  was present. This seat invoked no child agent, bridge or peer consult and
  supplies no verdict for the companion seat. Delegation count: zero.
- The user's standing rules override ordinary coordination updates: no
  RUN_STATE, TASK_QUEUE, state kernel, state test, task registration, ruling
  draft or PROJECT_STATUS edit was made.

## Files and verification

Only these repository files are added:

1. `docs/align/squeeze/v5-design/ruling-delta3-review-sol2.md`
2. `docs/run_reports/2026-11-08-v5-ruling-delta3-sol2.md`

Temporary script:
`/private/tmp/jw-v5-ruling-delta3-sol2-arithmetic.py`.
SHA-256: `fca889a8063891f0263fa606201f334d13966424f0c2b6d320f6490ad62d364f`.
Temporary stdout:
`/private/tmp/jw-v5-ruling-delta3-sol2-arithmetic-output.txt`.
SHA-256: `b7000fb7cd21ff0bfd0b7a955de539c7be9ffcfb15aa92e669c88d8b13e400e8`.
The script is not a permanent test or a runtime dependency. Its formulae,
selected verbatim output and counterexample explanations are preserved in
the review; scratch files need not survive handoff.

Checks:

| Command/check | Result and what it established |
|---|---|
| `python3.13 -I -B /private/tmp/jw-v5-ruling-delta3-sol2-arithmetic.py` | PASS, exit 0, under one second. Literal roster, ledger, cuts, storage and calendar arithmetic; exhaustive 27-pattern binary completion check; synthetic H4 and conditional-null counterexamples. No experiment simulation or hardware validation. |
| Verbatim-output and finding-coverage assertions, stdlib Python | PASS. Every line in the review's quoted output occurs in actual script stdout; all DS1 D1–D5 and DS2 D1–D8 are explicitly covered. |
| `git diff --no-index --check /dev/null docs/align/squeeze/v5-design/ruling-delta3-review-sol2.md` and final `git diff --cached --check` | PASS. Documentation whitespace only; lead seat reviewed the complete added diff. |
| Unit tests, full/sharded suite, compileall | Not run. No implementation changes; documentary checks and subsecond stdlib arithmetic are task-proportionate. The user's no-full-suite rule controls. |

The principal reported numbers reproduce using unrounded L1 scoring:
711.3/889.1 h base/reserved and 732.1/915.1 h GO at 900 s;
1,190.3 h reserved GO at 1,200 s. The 224-attempt H4 total is feasible,
but the literal rotation permits empty H4 dates. The completion minimum is
pointwise adverse. A bounded-mean betting theorem requires a conditional
null; 20 arm dates do not establish it. CAP's ratio needs conversion to
hours/day and a single consistent treatment of yield.

No network, model weights, MLX execution, process/job inspection, hardware
probe, real measurement read or block-5 analysis pipeline was used. No paths
under forbidden external data roots or real restricted directories were
opened. Git-object reads were repository objects only. No quiet-Mac work was
started, and the ongoing blinded analysis job was untouched.

## Handoff and remaining uncertainty

Next: the lead dispositions R1–R4, revises the inference/null, H4 date-weight
and CAP clauses, and obtains both independent seats' responses on that exact
candidate. Recompute the dated GO schedule with measured inputs only after
the appropriate lead-controlled gates. This review grants no collection,
purchase, scoring, network access or calendar extension authority.

The finding about duplicated yield is conditional: window loss and member
loss could be distinct; the draft must state whether they are. Actual host
receipt coverage, custodian enforcement, capacity, physical resolution,
capability, G12 error/power and the companion seat's verdict are unknown here.
Novelty/venue verification is explicitly deferred to separately authorized
network work. No positive or negative experimental outcome is inferred.

No new native code or test module was added. Outside this sandbox the lead
must identify and run the eventual import-gated tiny-synthetic MLX unittest
modules for actual/public replay, forced twins, history/cache/RNG, receipt
partitioning, helper concurrency/teardown and tails, one module at a time.
Quiet-machine measurements require agents to stop first; no weight download
is needed for the synthetic tests.

The local commit containing this record and review is identified in the
session's final response and Git history. No push is authorized or performed.
