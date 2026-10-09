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
