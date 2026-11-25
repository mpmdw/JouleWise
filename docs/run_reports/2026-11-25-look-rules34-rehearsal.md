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

## Fix 1 after Astra's audit

Astra reproduced a HIGH at `75ce4bf5c`. The official row command accepted
the rehearsal verdict hash. Moving that same file into the registered
campaign location then let stage 1 and the stage-1 row command succeed
with zero stock producer invocations. The retained audit is under
`astra-971-audit-1125`, with `FINAL-MESSAGE.md`, `tmp/provenance.py` and
`tmp/provenance.log`.

The stock producer now verifies the manifest, roster and rehearsal hash
commitments on main, computes the same verdict bytes and publishes the
verdict followed by a private, closed `rules_3_4.receipt.json`. The receipt
binds the committed producer code, the first-parent main commit that put
the current look row in effect, the manifest, roster and verdict hashes,
and the producer's wall and monotonic clock readings. The wall reading
must follow the Git committer timestamp. The monotonic reading is sampled
in the producer after the verified row and completed judgment. A later
commit that leaves the look row intact preserves its receipt. A changed
row needs a fresh stock run. Campaign stage 1 verifies the receipt before
admitting spans. The draft rehearsal continues to publish only verdict
bytes. [RL-217 E.1](https://github.com/mpmdw/JouleWise/blob/0a1433996176d204ebcf4d4c7359803388821721/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L25934)

The regression uses the official row command and moves the same rehearsal
inode to the campaign destination. Stage 1 refuses without the receipt.
Wrong verdict, clock, shape and stale ledger bindings also refuse. The
post-commit stock run reproduces the rehearsal bytes and admits stage 1.
The admission suite's driver plants receipts for its generated inputs.
Its case-source digest, test data and expected decisions are unchanged.
The runner, producer and manifest library were re-pinned. The host-command
inventory tracks the revised runner docstring; production commands reuse
the existing Git seam.

All seven rehearsal checks and both host-command inventory checks passed
locally at utility priority. Draft validation, pin and generated-state
checks passed. The canonical local discovery suite remains outside this
seat's archived-data read boundary.

The HIGH is addressed in the fix and awaits Astra's final-head recheck.
The E.6 timings above remain provisional until the input pins provide
per-stream byte sizes and the literal Air invocation is available.

## Fix 2 after Astra's narrow recheck

Both replays reproduced the block at `a5c6c2487`. Stock accepted an old
synthetic span through `--span-dir` and accepted its stale bytes at the
registered path. A fetch during stage-1 preflight changed the committed
verdict hash, yet stage 1 wrote both outputs. The same fetch at parent
`75ce4bf5c` exited 2 and wrote neither artifact. The isolated before-run
logs are `fix2-span-before.log`, `fix2-fetch-head.log` and
`fix2-fetch-parent.log` in the builder seat's `tmp` directory.

Test-only commit `8a21e1324` records the failing regressions before the
fix. It covers both stale-span routes, a fetch during preflight and a
fetch just before publication. It also checks the receipt's exact
committed pin inventory and corrupts that inventory to prove refusal.

Campaign stock now accepts only the registered span paths. The existing
isolated verifier checks the full committed pin inventory before judgment.
The pinned reader supplies verified operational bytes and rehashes each
consumed stream before returning its bytes for parsing. The version-2
receipt records the verified relative names and SHA-256 digests. Campaign
stage 1 checks that inventory against the committed manifest, and it
revalidates the ledger and receipt at the end of preflight and immediately
before publication. The rehearsal route retains its draft behavior.
[RL-217 E.1](https://github.com/mpmdw/JouleWise/blob/0a1433996176d204ebcf4d4c7359803388821721/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L25934)

The synthetic CLI replays refused both stale-span routes without a
verdict or receipt and restored the parent fetch refusal without either
stage-1 output. On 14 generated spans and 72 legs, stock and rehearsal
verdicts were byte-identical at
`21a928663d60134d5d6169c11caa5fbc67b695fab02a89133d93bb25bf25e16e`.
The stock run and campaign stage 1 both exited 0 on those inputs. The
manifest pins cover the three changed code files. This fix reuses the
existing isolated verifier command site.

Stage 2 still refused both a wrong stage-1 hash and an exact committed
hash of the marked rehearsal artifact before taking a reservation. All 15
rehearsal, protected-phase and command-inventory checks passed locally
at utility priority with at most two concurrent workers. Draft validation,
pin and generated-state checks passed. Suite rollup evidence is recorded
against the fix head in the draft PR gate ledger.

E.6 remains provisional until the committed pins supply per-stream sizes
and the literal Air invocation can run. The independent final-head
recheck and cold pass remain open.
