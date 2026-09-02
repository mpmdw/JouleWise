# Refuter, CONTRACT lens — WO-2 night driver (Opus 5 seat)

Checkout `/Users/edr/code/JouleWise-wt-night-driver`. **Head note for the
magistrate:** the branch advanced under me mid-review. `git rev-parse HEAD` was
`89d58e80` (the briefed head) at the start and `8f3d4adf` at the end — commit
`8f3d4adf` ("merge gate fix round 1; driver owns RESULT_SCHEMA (gate S5); driver
fixture writes the GNU shasum sidecar") landed while I read. That commit touches
`scripts/run_night.py` by 4 lines only (moves `RESULT_SCHEMA` out of the gate into
the driver) and `tests/test_run_night.py` by the sidecar fixture. **Every finding
below was re-run and re-anchored at `8f3d4adf`; all line numbers are that head.**
Authority: `MAGISTRATE-RULING-UNATTENDED-STAGE1.md` §2 R-1..R-12, §8. All 58 tests
in the three named suites pass at `8f3d4adf`; tree left clean.

## VERDICT: FIX-ROUND

---

## Blockers

**B1 — R-7's whole reporting layer cannot run under launchd, and its failure is
invisible.** `run_night.py:50-59` launches the courier as `/usr/bin/env claude`.
`which claude` → `/Users/edr/.local/bin/claude`; `launchctl getenv PATH` is empty,
so a `gui/501` agent gets launchd's default `PATH=/usr/bin:/bin:/usr/sbin:/sbin`,
and the plist template (`com.joulewise.night.plist.template:1-30`) sets no
`EnvironmentVariables`. INPUT: the night fires from the installed LaunchAgent.
OBSERVED: `Popen` raises `FileNotFoundError` (an `OSError`), caught at
`run_night.py:437-439`; three attempts fail; `run_courier` returns `False`; **every
one of the seven call sites discards the return value** (`:584, :612, :632, :671,
:702, :745, :767`). `result.json` never mentions the courier
(`_write_result:461-492`), `_artifact_list:314-330` omits `courier.attempts.jsonl`
/ `.heartbeat` / `.sent`, and `_durable_record:366-374` neither copies them nor
could — it runs *before* `run_courier` on every path. EXPECTED (R-7): the night is
reported to Ed, or the record says it was not. A green night therefore exits 0,
pushes a branch that looks perfect, and Ed gets nothing — with no artifact anywhere
saying so. The dead-man at 07:00 fails identically (same PATH).

**B2 — the O_EXCL latch protects the chain but not the night's evidence; a second
invocation destroys the record.** `_claim_chain_start` is called at `:681`, but
`receipt.json` is written at `:587-589` and `result.json` / `refusal.json` by the
refusal writers at `:682-703` — all *before* the latch refuses. INPUT: run the same
plan twice (a launchd re-fire after a driver crash, a manual re-run, or the
operator's second `run`). OBSERVED (probed, `probe_clobber.py`, re-run at
`8f3d4adf`): run 1 → `result.json` `verdict=GO, chain_exit_code=17`, receipt
`authored_ns=99001`; run 2 → same file `verdict=REFUSED, chain_exit_code=null`,
receipt re-authored `authored_ns=99002`. The real night's result record is gone
locally. EXPECTED (§8 d.3 / D-078 once-only): a second invocation refuses without
touching the first night's records. Note the accidental partial mitigation — run 2's
`git push HEAD:branch` is non-fast-forward and fails silently into the `except` at
`:399`, so the *pushed* copy survives, but only if run 1 pushed at all.

**B3 — driver refusals are stamped with the v2 receipt schema and fail its own
validator.** `_write_driver_refusal:133-148` writes `{"schema": SCHEMA, ...}` where
`SCHEMA = "joulewise.unattended_night_receipt.v2"` (`night_gate.py:19`), the
identifier R-4 fixes for the five-condition receipt. INPUT: any driver-side refusal
(`night_plan_overruns_deadman`, `night_chain_already_started`,
`night_chain_digest_mismatch`, `night_receipt_class_invalid`, `night_chain_alive`).
OBSERVED at `8f3d4adf`: `night_gate.validate_receipt(doc)` → `['receipt: keys are
not exact (missing=["'authored_monotonic_ns'", "'conditions'"], extra=[])']`.
EXPECTED: one schema id per document shape. Two incompatible shapes now share one
identifier, and the shape that carries *most* refusing nights is the invalid one.
Cheap cure: a distinct `joulewise.night_refusal.v1`. (This survived the gate fix
round that just moved `RESULT_SCHEMA` to the driver for exactly this reason.)

**B4 — the zero-agent fence has a guard on the dead-man path and none on the run
path.** `_terminate_process_group:238-263` swallows `ProcessLookupError` /
`PermissionError` on both `killpg` calls (`:245-246`, `:254-255`) and, if both 30 s
waits expire, returns `process.poll()` — `None`, i.e. *still running* — and **skips
`_record_chain_exit` entirely** (`:262-263`). `run_night:711-721` then records
`verdict=ABORTED` and `:745` starts the courier regardless. INPUT: a chain child
that does not die (this chain runs `sudo powermetrics`, i.e. a root member of the
group an unprivileged driver cannot signal). OBSERVED: `claude -p` is spawned while
the measurement chain may still be sampling. EXPECTED: R-7 refuses exactly this on
the dead-man path (`:757-765`, `night_chain_alive`) on the stated ground that "a
courier is an agent process and starting one during capture breaches the zero-agent
fence" (§0, §8 d.3); the run path needs the same predicate. Second consequence: no
`chain.exited` is ever written on that branch, so the 07:00 dead-man refuses forever
and no email is ever sent.

## Should-fix

**S1 — `COURIER_DEADLINE_S = 600` contradicts R-7's ruled formula.** R-7 sets it to
`max(3 × measured, 300)` capped at 600. The measurement exists:
`docs/process_traces/2026-09-01-unattended/cold_start.json` → `median_ms = 5303`.
`max(3 × 5.303 s, 300) = 300`, capped → **300**. `run_night.py:38` hardcodes 600
with no reference to the artifact; `scripts/measure_claude_cold_start.sh` emits
durations but applies no rule. A ruled constant set by assertion, not derivation.

**S2 — the courier retry budget exceeds the driver's own overrun accounting, so two
couriers can run concurrently.** `:552-557` budgets `COURIER_DEADLINE_S +
sum(COURIER_BACKOFF_S)` = 600 + 840 = 1440 s. The actual loop (`:429-458`) is three
deadline waits plus two backoffs = 3×600 + 60 + 180 = **2040 s**. INPUT: a plan
sized to just pass the overrun predicate whose first two courier attempts stall.
OBSERVED: the run's courier loop is still retrying at 07:00; the dead-man (separate
label, so launchd starts it) sees no `courier.sent` and `chain.exited` present, and
calls `run_courier` again. The two loops then fight: each `heartbeat.unlink()` at
`:430` deletes the other's proof, and each `_terminate_process_group` at `:444`
kills the other's `claude` — possibly mid-send.

**S3 — the courier cannot resolve the handback it is ordered to read.**
`NIGHT_COURIER_PROMPT.md:7` says "Read `docs/process/NIGHT_HANDBACK.md`" — a
relative path — but the courier `Popen` at `:433-436` passes no `cwd`, and the plist
sets no `WorkingDirectory`, so the courier's directory is launchd's, not the repo.
Separately, `docs/process/NIGHT_HANDBACK.md` does not exist in this tree (it is
WO-4's, at the bench) — a cross-WO dependency worth naming in the handoff.

**S4 — the courier's grant exceeds R-7's fixed-text fence.** `COURIER_ALLOWED_TOOLS`
(`:42-44`) grants `Bash,Edit,Write` alongside the Gmail send. The contract line is
"a Gmail send … nothing else — no tool that writes to the repo, no second agent, no
interpretation of the night's data." `Bash` is an unrestricted shell: it can `git
commit`, and it can start a second agent. `NIGHT_COURIER_PROMPT.md:18` then says
"Continue with the handback's next lane under the standing loop rules" — R-7 does
authorize "resume the loop", so this is a ruling-internal tension the magistrate
should settle explicitly rather than a pure code defect; but as written the night
ends with an unbounded write-capable agent in the *development checkout* that R-7
forbids the driver itself from touching, and (via B4) possibly during capture.

**S5 — a rehearsal cannot succeed while agents are present, which is the one
property R-4 says the rehearsal class exists to provide.** R-4: "A `REHEARSAL_STUB`
receipt can never carry `verdict: GO`; that is what lets the driver be rehearsed
while agents are present without ever minting a launch." The driver does bypass the
gate verdict for rehearsal (`:615`), but `_run_chain_once`'s first census fires
immediately (`next_census = time.monotonic()`, `:290-294`) and applies the same
abort rule. INPUT/OBSERVED (probed, `probe_rehearsal.py`, re-run at `8f3d4adf`):
REHEARSAL_STUB plan, `rehearse`, census returns `12345 claude` → `rc=4`,
`verdict=ABORTED`, `aborted_reason=night_aborted_agent_present`, stub killed
(`killpg(4242, SIGTERM)`). EXPECTED: `REHEARSAL_ONLY`. Nothing in the driver can
ever produce the `REHEARSAL_ONLY` verdict on a machine with an agent open — which
also bears on stage 2's acceptance shape (§3).

**S6 — R-2 item 3's "the human view and the executed bytes cannot diverge" is not
proven.** `tests/test_gen_g2_phase_d.py:59-68` asserts each reviewed block is `in`
the chain — a subset test with no upper bound. An emitter that appended arbitrary
lines after the summarizer block passes every assertion in the file. The property
ruled is byte identity of the reviewed region; assert the full reconstruction.

**S7 — test coverage gaps on ruled behaviour.** No test exercises the
`REHEARSAL_ONLY` path at all (only `test_rehearsal_refuses_a_non_rehearsal_plan`
:322, which asserts a refusal) — the gap that hid S5. `census_count` is never
asserted `> 0` and `CENSUS_INTERVAL_S` is never asserted, so R-2's "census every
30 s" has no test. `test_clone_failure_does_not_change_a_go_exit_code:327` patches
`subprocess.run` wholesale, so R-7's "fresh shallow clone, never the working
checkout" has no argv-shape assertion.

**S8 — the digest/HEAD custody covers the wrapper, not the code it runs.** R-6 binds
`repo_head` to "the checkout's HEAD", implemented as `REPO_ROOT` (`:32`, `:196-200`)
— the development tree. The emitted chain executes `$REPO = $MEASUREMENT_CHECKOUT =
/Users/edr/JouleWise-measurement-20260813` (emitted chain lines 5-6), whose HEAD is
never pinned or checked. The sidecar pins the 274-line wrapper; the eight scripts it
invokes are unpinned.

**S9 — installer re-install is non-atomic and can strand a live night.**
`install_night_agent.sh:2` (`set -e`) + `:91-96`: a `launchctl bootstrap` failure on
the first plist exits before the dead-man plist is bootstrapped, leaving a night
armed with no dead-man. And `bootout` (`:93`) on a live night SIGTERMs the driver
while the chain, in its own session, survives — `chain.started` with no
`chain.exited`, so the dead-man refuses forever (`night_chain_alive`) and no email
is ever sent. The driver installs no SIGTERM handler.

## Nits

- `_night_date:333-334` uses UTC; `_next_deadman_epoch:499-509` uses naive local
  (correct for launchd). A 22:30 PDT night is branch `night-results/20260902`. Two
  time bases in one file; pick one and say which.
- A `REHEARSAL_STUB` plan run under `run` writes a receipt with `verdict:
  REHEARSAL_ONLY, refusal: null` into a file named `refusal.json` (`:615-616`).
- `test_census_refusal_terminates_group_and_records_abort:246` asserts
  `killpg.assert_called_once()` without args; the behaviour is right (my probe saw
  `(4242, SIGTERM)`) but the assertion would survive killing the wrong pid.
- `test_courier_tries_three_times_with_the_declared_backoffs:272` asserts the
  constant tuple equals itself; `COURIER_BACKOFF_S[2] = 600` is never used. Either
  the tuple has a dead element or R-7's "up to 3 times" means four spawns.
- `_CODES` (`:46-49`) keys by `code[6:]`; any future registry member without the
  `night_` prefix silently mis-keys instead of failing.
- `dead_man` never calls `_durable_record`, so its `night_chain_alive` refusal is
  never pushed — and it overwrites the local `refusal.json` first.
- The driver raises gate-registry codes for driver-side conditions
  (`night_receipt_class_invalid` at `:596`, `night_chain_digest_mismatch` at `:653`);
  permitted by the union the brief names, but it blurs R-8's split.
- `chain.started` / `chain.exited` are written without `fsync`.
- R-3 "the census is the driver's first act": `checkout_head` (`:196-200`) spawns
  `git rev-parse` before the census runs (`night_gate.py:602`). WO-1 territory.
- Both plists share `@@CUSTODY_ROOT@@/night/launchd.out` and `.err`.

## What holds

- **R-10 / E-10 (checked hardest).** The emitted G2-a chain contains no
  `launch_window.py`, no `generate_arm_readiness.py`, no `--pack-root` /
  `--arm-receipt` consumer. `PACK_ROOT`, `FLOOR_*_PACK_ROOT` and
  `ARM_READINESS_CUSTODY_ROOT` appear only as `export`s (emitted chain lines 21-27)
  and are never read; `run_campaign.py` is called with `$config_dir` derived from
  `$G2A_CONFIG_ROOT` (lines 241-243). The launcher block at
  `gen_g2_phase_d.py:323-325` belongs to `render_generated_region` (the G2-b runbook
  path), not to `render_g2a_night_chain`. §8's fence test — pack/launcher
  *consumption*, not the word "diagnostic" — is met.
- **§8 d.3 once-only, chain half.** `_claim_chain_start:512-539` is a genuine
  `O_EXCL|O_CREAT|O_WRONLY` 0600 claim, made before `Popen`, refusing
  `night_chain_already_started`; probed — the second run spawns nothing.
- **R-2 lifecycle order** run → overrun → gate → digest → claim → `Popen(...,
  start_new_session=True)` → census loop → `chain.exited` on `wait()` → result →
  push → courier, with `_durable_record` before `run_courier` on every one of the
  seven terminal paths (so the branch is the floor, as R-7 intends).
- **Production census argv.** `_run_chain_once:294` calls `night_gate.agent_census`,
  which uses `AGENT_CENSUS_ARGV` verbatim (`night_gate.py:381`) with exit-1 +
  empty-stdout as the only clean outcome; no second spelling anywhere in the driver.
  Cadence is 30 s (`:307`).
- **R-2 item 2 / §8 item 3, plist and installer.** No `KeepAlive` (and the installer
  refuses a template containing it, `:31-34`); `RunAtLoad false`; both labels
  rendered from the one template (`:89-90`); the dead-man hour imported from
  `DEADMAN_HOUR`/`DEADMAN_MINUTE` and never literal (`:43-46`); zero occurrences of
  `sudo`; user domain `gui/$(id -u)` only; `bootout || true` then `bootstrap`.
  Uninstall boots out both labels and removes both plists.
- **REHEARSAL_STUB never runs the real chain.** `rehearse` on a non-REHEARSAL_STUB
  plan refuses before the chain path (`:592-613`); the rehearsal branch substitutes
  `/bin/zsh -c "sleep 2; echo REHEARSAL"` unconditionally (`:676-678`) and
  `chain_path` is `/dev/null`. A REHEARSAL_STUB plan under `run` gets
  `REHEARSAL_ONLY` from the gate (`night_gate.py:474`), never GO, so it refuses.
- **Reason-code hygiene (R-8).** Every driver refusal names a registry member via
  `_CODES`, which `KeyError`s on an unregistered name, and
  `test_driver_reason_codes_are_registered_and_are_not_literal_call_sites` forbids
  literal `"night_` strings in the source. No edits to the frozen D-078 registry.
- **Sidecar seam.** `_sidecar_digest:69-84` accepts the GNU shasum form the emitter
  writes (`gen_g2_phase_d.py:156`) and bare hex, refusing uppercase, a wrong
  basename, extra tokens, and empty — matching the gate's parser at
  `night_gate.py:622-652`. As briefed, the fixture's form is not reported.
- **Courier tool name.** `mcp__claude_ai_Gmail__send_message` is confirmed present in
  `cold_start.json`'s recorded tool listing.

## Commands run

```
git -C /Users/edr/code/JouleWise-wt-night-driver rev-parse HEAD        # 89d58e80 → later 8f3d4adf
git -C … status --porcelain                                           # clean, before and after
git -C … log --oneline cd9b2216..HEAD -- scripts/run_night.py
git -C … diff 89d58e80 8f3d4adf [-- scripts/run_night.py tests/test_run_night.py]
wc -l <the seven files under review> joulewise/night_gate.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/gen_g2_phase_d.py --emit-chain $S/chain.zsh --night-date 20260902
grep -n -i "pack|launch_window|generate_arm_readiness|config_dir|sudo" $S/chain.zsh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate   # 58 OK (both heads)
PYTHONDONTWRITEBYTECODE=1 python3 -c "from joulewise.night_gate import validate_receipt, SCHEMA; …"   # B3
PYTHONDONTWRITEBYTECODE=1 python3 $S/probe_clobber.py     # B2
PYTHONDONTWRITEBYTECODE=1 python3 $S/probe_rehearsal.py   # S5
which claude ; launchctl getenv PATH                      # B1
```
No chain, no `claude`, no `launchctl` mutation, no push, nothing written in the
tree. All probe files under `…/scratchpad/opusprobe/`.

## Confidence

High on B2, B3, S1, S5, S6, S7 — each directly probed at `8f3d4adf`, or arithmetic
against a ruled formula and a recorded measurement. High on B1's mechanism,
medium-high on its consequence: the PATH claim rests on `launchctl getenv PATH`
being empty plus launchd's documented default, and installing the agent once would
settle it — the cheapest possible confirmation, and worth doing before stage 2.
Medium on B4 and S2: both are reachable-path arguments rather than observed
failures, and neither is refuted by any existing test. S8 and S9 are
contract-completeness findings the magistrate may reasonably scope out of WO-2.
