# PR #795 isolated twin adoption

Mission M0 found a clean [AGENT] worktree at `f0946989493e2a50fa7087f2e1b19f071544040a`
and a matching branch and PR head. The follow-up retains the release boundary
from RL-180, implements the parent-owned handshake in RL-181 §5, and records
hard interruptions under RL-183 §2.4. Verification used generated data.

The byte-identical independent script is from PR #816 at
`ac5e4db87c4405d0e057e5d5ac70b7494a6a1985`. Its SHA-256 is
`aa041772d45bc955aba999721cfdea4b9776875ca635449fd0ff60593a5ba22a`.
The parent verifies that path and digest before reservation, invokes one
isolated child, authenticates the primary projection, recomputes the
registered comparisons and rechecks the coefficient commitment. The parent
uses the remaining stage-2 budget for the child. Both child streams and the
comparison stay in the reservation.

| Ruling or finding | Synthetic verification |
| --- | --- |
| RL-180 and the #816 pin | Missing pin, absent script and one-byte change refuse before reservation with zero response reads |
| RL-181 §5 | A real isolated child and primary pipeline agree on both raw readers and all three Step 3 cells in a generated, flat-locator case. An injected numeric change to a fold yields `no` even when the frame claims a zero maximum. |
| RL-180 completed primary on twin failure | A real child nonzero exit, incomplete fold, forged primary projection, malformed frame and injected timeout yield `not_evaluable` with public `stage2_error = no`. The descriptor checks witness private stdout and stderr. |
| Coefficient immutability | A subprocess witness compares the stored bytes before and after the child. A deliberate synthetic mutation after it returns blocks publication. The test compares public records across all completed fault cases with only the twin word masked. |
| RL-183 §2.4 | A public-only operation records `interrupted` / `none_recorded`; a fresh clone refuses the spent ID before opening responses. A delivered notice records `failed` with its actual type. |
| RL-180 host binding | A matching fixture identifier admits the reservation. A missing or different identifier and a non-synthetic request refuse. |

## Cold-pass dependencies

The lead must identify the campaign receipt field and matching local
derivation. Production admission is explicitly held for that confirmation.

The pinned twin's `span_identities` checks `Path(bundle).name == bundle`.
The cadence runtime creates member directories below `runs/`, and
`cadence_leg.py` records the relative bundle path. The ordinary generated
layout reproduced the child refusal on `runs/cadence-leg`. The positive
integration uses flat fixture locators bound in stage 1, plus complete
synthetic Step 3 telemetry. A reviewed reader supporting the runner's
nested locators and its updated pin are needed before campaign use. No input
receipt was rewritten by the integration or for production.

The PR body records exact-head CI and remains the review handoff.
