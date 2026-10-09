# Block 5, second seal: the second measurement clone

Magistrate activation 1aed44f9 (Opus 5.5, headless), 2026-10-09, about 11:15 to 11:20 PDT. Structure only.
Ruling section D, gate 6. The commands are those of the clone consult
(`/Users/edr/night-archive/b5-consults/corpus18-build/sol-clone-consult.md`, sections 2.2 to 2.5 and 3), a
Sol 6.1 seat that proved the pin carry on a scratch clone before the lead ran it, and of step 4 of
`docs/process_traces/2026-10-07-block5-seal/30-post-seal-runbook.md` for the environment.

| Item | Value |
|---|---|
| The clone | `/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18` |
| How made | `git clone --no-hardlinks` of the canonical root, detached at the seal commit; not shallow |
| Seal commit | `be6525e5a6511adf882282e404e163e14dbb738b`; its parent is the claim head `c27485347c9629b857df81665b5b1b8d10dcd36a`; its diff against the claim head is the three seal documents |
| Environment | a new `.venv` from `/opt/homebrew/bin/python3.13` (3.13.1) and the two `pip install -c env/mac-measurement-lock.txt` commands of the runbook; no Homebrew command |
| Lock check | the installed list equals the lock line for line; `pip check`: no broken requirements |
| Interpreter digest | `9033a69906aab1f0ff5724b5a6c2f3efd623512ee49a7048713e2410e701c794`, equal to the sealed `runtime_versions_sha256` |
| Ledger | `runs/calibration_observation_ledger.jsonl`, a byte copy of the first clone's (422 rows, file sha256 `0af3448c8d6370dada9b4ab5a74e772f831b183a0fef37efd6357991328eaa69`) |
| Pin | a byte copy of the first clone's committed pin (sequence 422, head digest `1ae51d38cec5ac271231011a56cfd6604749a9d748a2a99ad734ed751f33f717`), committed alone as the seal commit's first child |
| Clone head (the carry commit) | `39665b8cb8ce841b1345c9b39b10022e0f92dfa4`; its diff against the seal commit is `configs/calibration/calibration_ledger_head.json` only |
| `ledger_head_status` | physical equals pinned at 422; `blocking` empty; no open session |
| Ledger replay with custody verified | no refusal, head 422 (every older capture the ledger names still resolves) |
| `tests.test_b5_seal_landing` in the clone | 9 tests, OK |
| Sealed inventory | all 682 working-tree digests equal the inventory; an inventory regenerated in the clone has the same files map; the inventory's `head` is the claim head |
| Identity pins | regenerated with the clone's interpreter and the model files on disk: nine units equal to the sealed pins |
| Clone state | clean; no stray `.DS_Store` or `__pycache__` in the pack directories |

Why the pin is a carried copy and not a pin advance: the seal commit's tree still holds the pin main has
(sequence 402), and the ledger the block continues from stands at 422 after the first seal's two chains.
A ledger ahead of the committed pin blocks every plan. The pin-advance program takes a window's plan and
there is no window of this clone yet, so the first clone's authenticated, committed pin is copied byte for
byte. The harvest classifies a commit that changes only the pin file as pin-only, so the code identity of
a window run from this clone is unaffected (the consult ran the plan writer and the identity tests on a
scratch clone of this shape: an ALPHA plan of 125 members was written with both plan heads equal to the
carry commit).

The fixed-values file `/Users/edr/night-plan-staging/b5-bench/b5-fixed-env.zsh` now names this clone, its
interpreter, the new claim head, the new seal commit and the new registration digest
(`c7b3fdf78dde0a403bbc0b63262d1f8b1a697695bdeb2fb737a90cedde1ddb3f`); the old file is kept beside it as
`b5-fixed-env.zsh.before-corpus18-20261009T181526Z`. The first clone is untouched (head
`96e6d7a9a6b276f2e64135fb16b3eec2fb29f7c4`, clean). A re-harvest of one of its three attempts passes
`--measurement-root` with the first clone's path.

Not done yet, and required before any arm: the harvest pin for this seal (gate 5), the desk seal check
with the new claim head and a scratch plan for each pack, the rehearsal (gate 7). The RUN_STATE hold is
unchanged: `B5-ARM-RELEASED: none`.

## The rehearsal (gate 7), started 11:17 PDT

The rehearsal rig `scripts/rehearse_b5_real.py` runs the real path (plan writer, driver, arm, chain, the
real model and power sampler, the corpus prune and the bound derivation) on a shortened roster, in a
private clone with a private copy of an older ledger, and its numbers are discarded. It is built to run
at the desk while agent sessions are alive: it runs the real agent census and idle-admission checks,
records what they measured in `overrides.jsonl`, and forces their decisions (its documented overrides R1
to R6). It is therefore not a quiet-machine measurement and not a claim window, and no rule about agent
sessions is broken by running it from this session.

- Run from a detached checkout at the seal commit, `/Users/edr/code/JouleWise-wt-seal2-rig` (so the claim
  clone's working tree is never touched), with `/opt/homebrew/bin/python3.13 -B`.
- Base: `/Users/edr/night-archive/gate-prune/rehearsal-real/corpus18-20261009T1816Z`. Pack ALPHA. Kept
  members: all 18 of the corpus, the start triplet, the midpoint, the end triplet, the whole stage
  `06_phase_prefill_p2048_abba_blocks_06_10` (20), and the rig's defaults for the other stages.
- `prepare` exited 0: the plan has 125 members and `window_max_s` 110,220.
- `run` was started detached (pid in `<base>/run.pid`; its exit code is written to `<base>/run.rc`; the
  rig's own log is `<base>/rig.log`). Arm dwell shortened to 60 s clean within 120 s, as the rig allows.

Next action when `<base>/run.rc` exists: if it reads `rehearsal run rc=0`, advance the private clone's pin
and harvest the rehearsal with the pinned harvest program of the second seal (the consult's section 5 has
both commands; the harvest waits for gate 5). Read from the harvest's record, by a program that prints
structure only: that the re-screen was evaluated, that the clean bound was built by the cap rule
(`members_kept` 12 with the rest under `beyond_cap` when at least 12 are clean), and the wall times of the
corpus prune and the bound derivation (above 1,200 s goes to a consult). Read the runner's log line for
the stage `alpha-science-prefill-p2048-abba-06-10` (ruling A.10: why it returns rc 1 with 20 of 20
succeeded). If the run failed, the rig's log names the stage; that is a defect to fix before any arm.

## Desk proofs in the new clone (11:25 PDT)

A scratch plan for each pack, written from the new clone into a scratch directory (no custody root under
`/Users/edr/night-custody`, no launchd job): desk identity `WRITTEN`, plan inputs rc 0, plan writer
`STAGED` with no difference from the default thresholds and no pack digest error, chain check rc 0, chain
sidecar equal, and both plan heads equal to the clone's head `39665b8cb`. Members and `window_max_s`:
ALPHA 125 and 110,220 s; BETA 125 and 112,620 s; GAMMA 107 and 99,060 s. The clone stayed clean.

The desk seal check (`b5_desk_seal_check.sh`) was not run in this session: the session's safety check
refused the command because the helper contains a removal it could not inspect. It was not worked around.
It runs as an ordinary step of the next arm (brief 5.3), where it must print `no flag`; its content, the
comparison of the clone with the claim head, is also covered above by the inventory digests (all 682
equal) and the regenerated identity pins (nine units equal).

## The rehearsal's first run was refused by the arm, correctly (11:17 PDT)

`<base>/run.rc`: `rehearsal run rc=0`; the driver exited 3 after 60 s. From the rehearsal's arm record:
battery, clock, thermal and disk `PASS`; **instrument `REFUSE`**: the power sampler's cadence probe got
228 of the 300 frames it needs within its 55 s bound, with a median interval of 255 ms against a limit
of 150 ms. Contention was not evaluated because the arm stops at the first refusal. The rig overrides
the agent census, contention, thermal and idle admission; it does not override the instrument check, and
it should not: a sampler that cannot keep its cadence is a real fault of the measurement.

Cause: the machine was busy. A builder seat was running the harvest's test modules (several processes
at full load) when the probe ran; the rehearsal's own override log names that seat's process. This is
the machine's state, not a defect of the 18-member path, which the run never reached.

So the rehearsal is run again when no test suite is running: after the desk seat reports and the whole
suite on the harvest lane has finished, and while CI (which runs remotely) checks the lane's pull
request. A new base directory is used (`prepare` refuses an existing one); the refused base
`corpus18-20261009T1816Z` is kept as it is.

## The rehearsal's second refusal, its real cause, and the third run (12:44 to 12:53 PDT)

The second run (base `corpus18-20261009T1944Z`), started on a quiet machine, was refused in the same way:
221 of 300 sampler frames, median interval 253.9 ms. The first run had measured 255.0 ms. Two values that
close, with and without load, mean the cause is not load. The 11:17 explanation above is withdrawn.

What was measured next, with the arm's own sampler command (`sudo -n /usr/bin/powermetrics -n … -b 0 -i
100 …`) started from this session: the marginal time per frame is 213 ms with the thermal sampler alone
and 236 ms with the CPU sampler alone, and 618 ms when the interval is set to 500 ms. So every frame
carries a fixed delay of about 115 ms whatever is sampled. The same command measured 131 ms per frame in
ALPHA attempt 3's arm last night and 113 ms in the rehearsal of 2026-10-06.

The cause: this session is a child of the magistrate's launchd job, which has no `ProcessType` key, and
macOS delays the timers of such background jobs (timer coalescing); `taskpolicy` could not lift it (215
ms with latency and throughput tier 0). The night job that runs a real window is installed with
`ProcessType` `Interactive`, and the installer refuses any other value
(`joulewise/night_agent_install.py` lines 585 to 593 and 675), which is why a real window is not
affected. The rehearsal of 2026-10-06 was started from an interactive session. **The sampler-cadence
check therefore cannot pass in anything started from a headless magistrate session, and that says
nothing about the machine.**

The third run (base `/Users/edr/night-archive/gate-prune/rehearsal-real/corpus18-20261009T1949Z`) is
started the way a window is: by a one-off launchd job with `ProcessType` `Interactive` (label
`com.joulewise.rehearsal.corpus18`, plist in the base directory, bootstrapped into `gui/501` with
`launchctl bootstrap`; the label does not begin with `com.joulewise.night`, so the watchdog and the
brief's checks for night jobs do not see it). Its arm: instrument 300 frames, median 130.8 ms, maximum
137.0 ms; decision `GO`; the chain started at about 12:51 PDT.

When it ends (`<base>/run.rc`): remove the job with `launchctl bootout
gui/501/com.joulewise.rehearsal.corpus18` before anything else (it has `RunAtLoad` and would run again
at the next login). The two refused bases are kept as they are.

For later: any desk run of the rig, and any probe of the sampler, from a headless session has to go
through a job of that process type. A consult that sees a slow sampler from a headless session should
check this first.

## The rehearsal's result (gate 7): passed (12:50 to 15:38 PDT)

Base `/Users/edr/night-archive/gate-prune/rehearsal-real/corpus18-20261009T1949Z`. Structure only; the
rehearsal is not a claim window and its numbers are discarded.

**The run.** Driver exit 0 after 8,636 s; verdict `GO`; chain to its end, closing calibration done. Kept
members 53, all 53 succeeded: corpus 18 of 18, start references 3 of 3, midpoint 1, end references 3 of
3, the whole stage `alpha-science-prefill-p2048-abba-06-10` 20 of 20, and the rig's defaults elsewhere
(the driver's yield status is `LOW` only because the rig keeps one to four members of the other science
stages). The corpus stage needed no retry (`retry-decision` rc 0, no retry stage). Wall times: corpus
collection 2,464 s; **corpus prune 373 s; bound derivation 372 s** (both rc 0; the chain's budget for each
is 1,800 s and the ruling's consult line is 1,200 s; the sizer charges 320 s each, so a window runs about
105 s longer than its sizing says, far inside the deadline's margin).

**The harvest, by the pinned program** (`harvest_checkout.head`
`224a264c5faaae90cdf56118df37e773a932700b`, `status_clean` true; archive `<base>/archive-pinned`; exit 0,
about 21 minutes): verdict `COLLECTED`. The private clone's pin was advanced first (392 to 402 in its own
ledger copy). The claim clone and the rig checkout stayed clean and the claim ledger is unchanged at 422
rows.

- In-window bound: derived from the collected subset (route 2), 18 members.
- **Clean bound, by the cap rule:** 2 members dropped for physics (`contention.request_overlap`, the
  first and the third in committed order; agent sessions were alive, which is what that flag measures);
  of the 16 that remained, **the first 12 in committed order were kept** (`members_kept` 12) and **4 are
  under `beyond_cap`** (the fifteenth to the eighteenth); `clean_bound_validated` true; no problem listed.
- **Re-screen: evaluated, decision `passed`, no condition, no problem, freshness `fresh`;** the bound used
  is `corpus_physics_clean`. (The stored in-window verdict reads `failed`, as the registration says it
  does for every window of this seal; the re-screen decides.)
- `claim_usable` false, for two reasons that belong to the rehearsal and not to the path: the shortened
  roster (`cell.below_minimum`) and the rig's own inventory (`code.identity_unmeasured`).

This is the first time the prune, the mint, route 2, the cap and the re-screen have run on ten or more
real bundles. The expected count of the gate ("12 used, 6 beyond the cap") became 12 and 4 because two
members were dropped for physics first; that is the rule working, by the lead's decision 4 in
`corpus18-erratum/CORRECTIONS-APPLIED.md`.

**The stage that returns rc 1 with every member succeeded (ruling A.10): explained.** In the rehearsal
it was `alpha-science-abba-01-05` (4 kept, 4 succeeded, rc 1); the stage it happened in during both real
chains returned rc 0 here. The runner's log for the stage shows the cause, in status words: one member
exited 0 with summary status `succeeded` and passed strict validation, and carries a collection
integrity flag for its clock anchor (the anchor fell back to its second method). The runner counts such
a member as `failed` in its own tally and writes the stage's provisional verdict as `invalid`, which is
the rc 1; the driver counts summary statuses, which is the "20 of 20". Nothing is lost or altered: the
bundle is complete, and whether the member enters a claim is decided by the harvest's own member checks.
So this is a difference of bookkeeping between two programs about a member with a clock-anchor flag, not
a runner defect, and by the ruling it changes no file: it is recorded here, and the runner is left
alone.

Gates 4 to 7 of the ruling's section D are done. What remains is gate 8 (the checks before the arm) and
the arm.
