# Interim look rules 3 and 4 rehearsal and stage-2 timing

Mission M0 selected the lead's P1 [AGENT] assignment for the interim look
manifest-pass packet. The working branch starts at PR #970's merge
`0ec997277`. The active stop card is clear. RL-217 A.4 and E.1/E.6 govern the
work. [RL-217](https://github.com/mpmdw/JouleWise/blob/0a1433996176d204ebcf4d4c7359803388821721/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L25776)

## Rules 3 and 4

The producer's `--rehearsal` uses the registered draft's roster, campaign
host and code pins. It binds every roster span to its offload Check and
shares the hash-only verifier and guarded reads with stage 1. It uses the
stock evaluator and serialization, creates the destination exclusively and
prints the verdict basename and sha256. Both commands use the same
destination fence against the repository and the registered roots on the
shared branch and freshly fetched main. Stage 1 reads the verdict only
from that private directory. It checks its hash against the draft ledger
before opening the four rehearsal blocks. The hp-01 tripwire word from
this rehearsal describes the absence of hp-01.

Re-pinned the producer, runner and manifest library, plus the draft
ledger's manifest digest, for the E.1 changes. The two host-command
inventory rows explain the documented isolated invocations. The shared
Git, execution-host probe and hash-only verifier use existing call sites.
[RL-217 E.1](https://github.com/mpmdw/JouleWise/blob/0a1433996176d204ebcf4d4c7359803388821721/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L25934)

The synthetic tests cover draft-to-committed producer byte and hash
equality, stage 1 without a custody verdict, and destination refusals.
The canonical local discovery suite includes archived measurement fixtures
outside this seat's read scope. The draft leaves the whole-suite rollup,
independent executing review and cold final-head review to their gates.

## Stage-2 timing

The opt-in timing helper generates 14 spans and 72 legs from the public
roster counts. It uses the 50 Hz format and public poll counts where
available, with estimates for the other spans. The public draft's pin
table is empty. Main item 581 requests the per-file sizes. The helper can
check an available public size table and refuses a size-matched label if
a stream is missing or outside 10 percent of its target.
[Public RUN_STATE](https://github.com/mpmdw/JouleWise/blob/f8250a29ae39a3c93c6e10c1b4ff246e331caec3/RUN_STATE.md#L1159)

The seat refused the literal stage-2 reservation basename in a generated
temporary directory. The helper's opt-in synthetic reservation name uses
the existing fixture seam. The Air (`Mac16,13`, Python 3.14.6, NumPy 2.2.6)
ran three sequential committed-path stage-2 invocations at utility priority
using one numerical library thread. The generated fixture had 436 streams
totalling 406,093,168 bytes. Wall time includes fetch, pin verification,
preflight, fit, Step 3, the independent twin and publication. Fixture
generation, stage 1 and the synthetic commits ran before the clock started.

```sh
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  taskpolicy -c utility python3 -B -m tests.cadence.look_campaign_timing --fixture-reservation
```

| Trial | Stage 2 wall time | Twin agreement |
| --- | ---: | --- |
| 1 | 39.787 s | yes |
| 2 | 40.316 s | yes |
| 3 | 41.034 s | yes |

The longest invocation took 3.4% of the twin's 1,200 s deadline and was
below the 600 s escalation threshold. These timings are provisional for
E.6. The literal timing needs the public byte-size inventory, a fixture
within 10% for every stream and an Air execution context that can create
the registered reservation basename.
[RL-217 E.6](https://github.com/mpmdw/JouleWise/blob/0a1433996176d204ebcf4d4c7359803388821721/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L25939)

The lead's next step for E.1 is to bind the manifest, whole roster, input
pins and Air host in the shared draft, then follow the
[operator sequence](../process/cadence_look_manifest.md#7-stage-1-rehearsal-for-the-manifest-pass).
