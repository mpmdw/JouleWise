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

## Round 4: one stage-1 exit authority and a parity check on the parent

Astra's second narrow recheck reproduced a HIGH at `434f32151`. During
rehearsal preflight, a fetch registered the rehearsal destination as the
campaign look directory. Rehearsal then wrote `level_r.json` and a marked
`stage1.json` there against the old ledger commit, which spent the
write-once slot. At `75ce4bf5c` the same replay exited 2 and wrote
nothing. Fix 2 had made the preflight-exit ledger check conditional on
`rehearsal is None`. Each earlier fix had likewise closed its finding and
dropped a guard that `75ce4bf5c` had. The retained audit is
`astra-971-narrow2-1125`, with `tmp/rehearsal_fetch.py` and its parent and
head logs.

Commit `0e20148e0` restores `RUN_STATE.md` and `TASK_QUEUE.md` to the PR
base bytes, as the lead's standing rule requires.

Test-only commit `db5d7b183` adds the convergence check (lead spec S2).
`tests/cadence/look_parity_cases.py` replays every reproducer from rounds
1 to 3 on generated custody against one source tree. It adds two
before-write variants and a branch rehearsal whose fetch registers the
destination on main only. `Pr971Convergence` runs each replay against this
checkout and against `75ce4bf5c` extracted from git. Every replay here
must refuse for its stated reason and write nothing. Every parent refusal
without a write must hold here too. The parent's outcomes must match the
audits' observations. A second test lists every raise site and refusing
call in the parent's `_stage1`, `finish_stage1` and `finish_rehearsal`,
with the guards that reach each one. Each must survive at the same guards
or name its replacement and the replacement's own guards. At `db5d7b183`
three replays wrote outputs. The enumeration found the parent's
preflight-exit ledger gate with no unconditional replacement.

The fix (lead spec S1) replaces the separate checks with one function.
`stage1_authority` derives everything a non-draft stage 1 runs under from
the ledger as fetched now. That covers the committed row for this
manifest, roster, verdict and ruled exclusions, the ledger gate and the
manifest's current bytes. A campaign run adds the stock receipt and its
input pins. A rehearsal adds the registered host and the destination
fence under every fenced ref. Stage 1 calls it at admission.
`stage1_exit_authority` calls it again at the end of preflight, before the
first protected read, and immediately before the writes. It does this in
campaign and rehearsal modes alike and refuses any change. The fence moved
from `rehearsal_output` into `rehearsal_fence`, and the fence and host
refusals now use `owned_refusal`. Before the first protected read these
are the same refusals as before. After it they are preflight breaches.
The stage-1 file records the preflight-exit gate again, as at `75ce4bf5c`,
so `stage1_problems` checks the bytes that are written. An unrelated
commit on the ledger ref leaves the ledger and row unchanged, so it still
passes. The runner was re-pinned, along with the draft row's manifest
digest. The manifest's `pin_check` and the operator sequence now describe
the shared exit check.

| Replay (audit round) | `75ce4bf5c` | `434f32151` | This fix |
| --- | --- | --- | --- |
| provenance (1) | wrote both | refused, no write | refused, no write |
| span_override `--span-dir` (2) | wrote all three | refused, no write | refused, no write |
| span_override stale copy (2) | wrote all three | refused, no write | refused, no write |
| preflight_fetch (2) | refused, no write | refused, no write | refused, no write |
| preflight fetch before writes (2) | wrote both | refused, no write | refused, no write |
| rehearsal_fetch (3) | refused, no write | wrote both | refused, no write |
| rehearsal fetch before writes (3) | wrote both | wrote both | refused, no write |
| branch rehearsal, main fence (3) | wrote both | wrote both | refused, no write |

Every control run succeeded on both trees. `rehearsal_fetch` now refuses
with the parent's message. The branch case refuses because the fresh
main ledger registers the destination's parent. Its ledger gate reads the
shared branch and passes, as it did at the parent.

On 14 generated spans and 72 legs, stock and rehearsal verdicts were
byte-identical at
`21a928663d60134d5d6169c11caa5fbc67b695fab02a89133d93bb25bf25e16e`. Stock
and campaign stage 1 both exited 0. Astra's round-3 provenance replay gave
the same results as at `434f32151`. Every receipt negative refused, the
current stock receipt admitted stage 1, and stage 2 refused both a wrong
stage-1 hash and the exact committed hash of the marked rehearsal
artifact without taking a reservation. Locally, at utility priority with
at most two workers, `test_look_run` (including the new class),
`test_merge_audit_c3a0dd9f8`, `test_inclusion_34`, `test_round7_admission`
and the host-command inventory passed: 183 tests. A run of the manifest,
layout, custody-pin and input-review modules had passed 30 tests with no
failure when the 20-minute local budget stopped it. Draft validation and
the pin check are clean after the re-pin. No command-site key changed.
The frozen admission matrix and the full suite run in hosted CI.

E.6 remains provisional for the reasons above. The independent final-head
recheck remains open.

## Round 5 (lead fix, after Astra's final narrow check)

Astra's final narrow check at `3c45f2e0d` (reproducer `final_receipt_fetch.py`) stopped the run while it opened the stock receipt in the before-write check and fetched a ledger whose verdict commitment had changed. `434f32151` exited 2. `3c45f2e0d` exited 0 and wrote `level_r.json` and `stage1.json` against the superseded commitment, because `stage1_authority` read the ledger before the receipt.

The fix is in `stage1_authority`. It reads the receipt before the ledger, and its last read is the committed row again (`require_inputs_committed`), which refuses if the row changed while the receipt or the fence was being validated. The only window left is between that final read and the write, a single comparison; the parent has the same window.

The regression is `test_campaign_refuses_a_verdict_hash_fetched_while_the_last_receipt_is_validated`. The fetch fires just before the third `require_rules34_receipt` call. It fails at `3c45f2e0d` (exit 0, `stage1.json` written) and passes here. The harness's `advance_main` now takes `before:`/`after:` with a call number, and `M.` targets. The enumeration test names the receipt read under its new condition. The runner and manifest digests are re-pinned.
