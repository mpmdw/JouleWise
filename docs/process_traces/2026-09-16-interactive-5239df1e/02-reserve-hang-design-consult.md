I recommend **B plus a hard, process-enforced custody deadline** for this repair, preserving full artifact authentication. Defer A to a separately specified local-store change; reject its “recorded hashes only” variant. The existing readiness gate authenticates every finalized observation, and the local store authenticates actual bytes against an exact ledger-head projection—these are materially stronger than trusting recorded digests alone. B is the smaller change to current issuing semantics, provided it exercises the actual launchd process chain and invalidates its result when the effective interpreter changes. The deadline, rather than the remembered consent, guarantees unattended refusal. ([Readiness](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:5176), [store verification](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:2036))

## 1. Cure shape and soundness

The historical scan protects **continued availability and byte integrity of receipt-bound evidence**. It does not rederive the calibration physics: `_observation_custody_reasons` reads artifacts and compares SHA-256 values. Ledger parsing, committed-head comparison, and observation-state reduction separately protect lineage, rollback, and conflicting classifications. ([Artifact checks](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:4924), [snapshot authentication](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:2100))

Historical imports are excluded from prospective bracket-candidate discovery, so their presence does not make them eligible endpoints. Nevertheless, skipping their bytes changes the meaning of a successful enforcing readiness check. It would not automatically falsify a downstream scientific claim, but it removes a current assurance and requires an explicit decision about where that assurance moves. Comparing recorded hashes with other recorded hashes cannot establish that evidence remains intact or accessible. ([Candidate exclusion](/Users/edr/code/JouleWise/joulewise/calibration_bracketing.py:1791), [enforcing verification](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:5182))

**A with authenticated local bytes is sound in principle.** The existing store checks its manifest against the physical ledger head and hashes every governed artifact. However, that exact-head manifest changes as the session advances, and readiness currently has no store parameter. A needs a defined policy for the historical prefix, new observations, and store updates. It also changes the current runbook’s explicit “copy no custody directories” route. It is more than skipping imports in `issuing` mode. ([Store/head binding](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:2044), [runbook](/Users/edr/code/JouleWise/docs/phase_2/derivation_night_runbook.md:360))

A finite deadline can refuse a healthy slow disk. That is an availability tradeoff, not evidence of corruption. Use a generous **whole-pass budget**, report elapsed time and progress, and retain full hash comparison on success. Do not apply the existing two-second metadata budget to multi-gigabyte reads.

For B, interpreter identity must be part of the arm evidence. The driver explicitly sets the chain’s `PY` to the measurement venv, whereas installation also accepts `--python`; checking only the installer’s interpreter is insufficient. ([Driver](/Users/edr/code/JouleWise/scripts/run_night.py:451), [installer](/Users/edr/code/JouleWise/scripts/install_night_agent.sh:40))

## 2. Smallest sound implementation and budget

**Bound the custody operation, while leaving the append transaction synchronous.** Do not put the entire reservation—including writes—in a timeout worker.

My proposed operating values are:

| Scope | Proposed bound |
|---|---|
| Complete custody verification | 120 seconds, including worker startup, metadata, opens, reads, and hashing |
| Worker termination/reaping | At most 5 additional seconds |
| Window boundary | Stop verification at least 10 seconds before the exclusive window end |
| Individual artifacts/observations | Share the same deadline; never restart it |

These are proposed operational limits, **not measured throughput claims**. The current runbook allocates 300 seconds to all pre-settle work, so 120 seconds leaves room for other preparation. The launchd dry run must establish whether the actual corpus fits comfortably. ([Pre-settle allocation](/Users/edr/code/JouleWise/docs/phase_2/derivation_night_runbook.md:1200))

Use an absolute monotonic deadline, clipped by the remaining plan window. Recheck expiry before accepting success and immediately before entering the append path. An already-expired window gets the existing window-exhaustion refusal; a running custody operation exhausting its allowance gets the new custody-timeout refusal.

The implementation shape:

1. The parent acquires `CalibrationWriterLease`, authenticates the ledger/pin, and freezes the observation list.
2. A fresh **read-only subprocess** verifies that exact list using original issuing locators and expected artifact hashes. It receives no writer descriptors or append capability.
3. The parent bounds every wait, including IPC. Success requires a complete response for the exact request and normal worker exit.
4. On timeout, discard late results, terminate/reap the worker, and raise the typed refusal directly. Do not continue into session-status fallback or append recovery.

Keep the worker in the chain’s process group, close inherited descriptors, and prohibit worker descendants. Do not use a forked copy of the parent’s lease or authentication context.

I would add a bounded night-specific wrapper around `_custody_reasons`, with a shared synchronous verification core inside its worker. All metadata probes in that route must consume the same deadline and produce the named timeout. Preserve generic `probe_custody`’s caller-context behavior for other consumers: authentication uses a `ContextVar` and an `RLock`, and tests explicitly require caller-thread registration. Moving its callback wholesale into a daemon thread would violate that contract. ([Authentication context](/Users/edr/code/JouleWise/joulewise/authentication_io.py:322), [existing regression](/Users/edr/code/JouleWise/tests/test_calibration_ledger_custody.py:443))

**No new open session:** the timeout must precede `append_bracket_session_receipt`, including the current failed-readiness/existing-session branch. `_locked_append` performs recovery before building a new receipt; an irrevocable intent is already enough to cause later session creation. Assert unchanged ledger bytes, not merely absence of a completed open row. ([Reservation branch](/Users/edr/code/JouleWise/scripts/reserve_calibration_window_bracket.py:256), [append/recovery](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:4148), [irrevocable intent](/Users/edr/code/JouleWise/docs/contracts/calibration_ledger_append.md:181))

**No stale lease:** normal exception unwinding releases both kernel locks and descriptors. The permanent `.lock` file should remain; its existence is not liveness. Verify reacquisition from another process. ([Release](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:3434), [lease semantics](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:3167))

Finally, reservation-only bounding is insufficient for the lane’s broad wording. Each capture writer performs historical custody verification before acquisition and again under its lease. Thread the same bounded facility through these night callers and `_custody_state`, sharing a deadline across each preparation operation. A later timeout preserves an **already-open** session for recovery. ([Writer preflight](/Users/edr/code/JouleWise/scripts/validate_powermetrics_fiducial.py:1949), [under-lease checks](/Users/edr/code/JouleWise/scripts/validate_powermetrics_fiducial.py:1537))

## 3. Exact refusal and courier propagation

Use:

```python
RefusalCode.LEDGER_CUSTODY_TIMEOUT = "calibration_ledger_custody_timeout"
```

“Timeout” states what was observed. “Unreachable” conflates expiry with absence, permission denial, and invalid bytes.

Register it as an **operational, arm-blocking, stop-preserved refusal**, with process exit `2` and terminal result `night_stopped_preserved`. Include phase, session, ledger-head identity, budget, elapsed time, and last reported artifact/observation in diagnostic context. Do not prescribe automatic retries or repair of an otherwise unchanged ledger. The registry already distinguishes operational witnesses from corruption backstops and supplies structured refusal payloads. ([Registry](/Users/edr/code/JouleWise/joulewise/calibration_exits.py:116), [payload](/Users/edr/code/JouleWise/joulewise/calibration_exits.py:566))

The driver needs an explicit bridge:

- Reservation/writer publishes the structured payload to a fixed night-owned `calibration-refusal.json`, as well as stderr.
- After chain exit, the driver validates that record and its plan/session binding.
- Register `night_calibration_refused` in `NIGHT_DRIVER_REASON_CODES`; preserve the exact calibration code and payload as its evidence.
- Write a `REFUSED` result retaining `chain_exit_code=2`, then take the ordinary reporting path.
- The courier reports **`calibration_ledger_custody_timeout`**, its budget/context, and whether a session already existed.

Exit code `2` alone is insufficient to infer this cause. Currently a nonzero chain exit without a driver abort yields `verdict="GO"` and generic chain failure, while the courier is instructed to read result/receipt/refusal documents rather than discover structured stderr records. Merely calling `emit_refusal` will not reliably surface the cause. ([Driver completion](/Users/edr/code/JouleWise/scripts/run_night.py:1761), [courier instructions](/Users/edr/code/JouleWise/docs/process/NIGHT_COURIER_PROMPT.md:7))

## 4. Defect-shaped regression and launchd probe

**Primary regression:** construct a valid committed fixture ledger with finalized historical observations and valid hashes. Make the custody root’s existence/directory probes succeed, then block an actual governed-artifact read inside `_observation_custody_reasons`. Invoke the production reservation CLI with `--execute`.

A local FIFO whose writer supplies a prefix but withholds EOF can reproduce the blocking read without iCloud or TCC. Alternatively, use a controlled read barrier at the filesystem seam. Do not mock `calibration_readiness` into returning a refusal.

Assert:

- The read was entered after successful metadata probing.
- The named refusal arrives within the budget plus bounded cleanup tolerance.
- Ledger and head-pin bytes are unchanged; no intent or session was added.
- Another process acquires the lease.
- Releasing the blocked input later cannot append anything; no verifier survives.
- A positive control using the same ledger and correct regular-file bytes reserves successfully.

The existing timeout tests block only `exists`/`is_dir`; they cannot catch this defect. ([Existing tests](/Users/edr/code/JouleWise/tests/test_calibration_ledger_custody.py:221))

**B probe:** add an explicit verify-only mode sharing the enforcing reservation preflight, stopping immediately before append. Existing omission of `--execute` only validates inputs and never runs readiness. ([Current dry run](/Users/edr/code/JouleWise/scripts/reserve_calibration_window_bracket.py:237))

Run that mode through a temporary LaunchAgent in the **same GUI user domain and process topology** as production: driver interpreter → shell/chain environment → actual reservation interpreter → custody worker. Use the exact clone, ledger/pin, reservation arguments, environment, and full observation set. No capture, settle, production chain-start record, or session append.

Persist a non-authorizing probe receipt binding the plan, ledger head, relevant input/code digests, effective interpreter identity, budget, and outcome. Require a matching successful receipt before installation; interpreter or input changes invalidate it before night-path custody reads. After any consent interaction, rerun successfully without further interaction. Boot out the probe and prove its processes are gone.

The current installer preflight is an ordinary subprocess, not launchd evidence, and the recorded post-event probe hashed only one manifest. Neither substitutes for this check. ([Installer preflight](/Users/edr/code/JouleWise/joulewise/night_agent_install.py:663), [recorded probe](/Users/edr/code/JouleWise/docs/process_traces/2026-09-16-interactive-5239df1e/01-night-reserve-hang-root-cause.md:75))

## 5. Co-design with the sibling lanes

**Neither deadline is redundant.** The custody deadline supplies an early, specific refusal before reservation writes. The driver deadline bounds other stalls and failures of that mechanism. Killing the chain at the window end cannot establish that no reservation intent was written.

For `NIGHT-STALL-WALLCLOCK-ABORT-01`, I recommend initiating termination at the exclusive window end, with separately bounded shutdown grace. A pre-termination grace permits acquisition beyond the declared window. Check the deadline independently of census cadence, including around potentially blocking census probes. Existing termination waits can consume up to 60 seconds. ([Driver loop](/Users/edr/code/JouleWise/scripts/run_night.py:483), [termination](/Users/edr/code/JouleWise/scripts/run_night.py:358))

Termination proof must cover the custody worker too. The current helper waits for the direct child; that alone does not demonstrate that every process-group member has disappeared. Courier launch must retain its existing “termination proven” condition.

For `DRIVER-REFUSAL-COLLISION-01`, use immutable distinct refusal documents with collision-resistant names or exclusive-create sequence allocation. **Do not append another JSON object to `refusal.json`**, and do not assume second-resolution epoch names are unique. Preserve both causes, reference their actual paths in the result/artifact inventory, and have the courier read them. The current artifact list hardcodes only `refusal.json`. ([Artifact inventory](/Users/edr/code/JouleWise/scripts/run_night.py:531))

Also update the sibling’s “daily firing” wording: current dead-man timing is already derived from plan completion plus grace, rounded to a minute. ([Current calculation](/Users/edr/code/JouleWise/scripts/run_night.py:961))

## 6. Disagreements with the lane text

I would amend these points before implementation:

- **“Local custody store or recorded hashes” is not an equivalence.** Require authenticated local bytes, or explicitly adopt a weaker, deferred custody assurance.
- **“Night path” is broader than reservation.** Include writer preflight and under-lease custody reads, or narrow the acceptance honestly.
- **“Leaves no open session” needs an initial-state condition.** Require no new intent/session for a fresh reservation. Preserve pre-existing sessions and recovery evidence.
- **“Bind-window” names an inadequate boundary.** The repository’s `bind_window` constructs G2-a inputs and authenticates their ledger binding; the needed check belongs in shared reservation preflight and the actual derivation-night arm flow. ([Implementation](/Users/edr/code/JouleWise/scripts/generate_g2a_probe_inputs.py:855))
- **B cannot promise that permissions never change.** Promise bounded autonomous completion/refusal, plus arm evidence invalidation after interpreter changes.
- **The TCC attribution remains an inference.** The root-cause record explicitly leaves Ed’s confirmation outstanding and retains materialization as an alternative. The unbounded-read defect is established regardless. ([Evidence qualification](/Users/edr/code/JouleWise/docs/process_traces/2026-09-16-interactive-5239df1e/01-night-reserve-hang-root-cause.md:84))

For the runbook, say: **“Treat every Homebrew Python replacement as invalidating the successful launchd access probe; verify again.”** Avoid claiming every upgrade universally resets a grant. Apple ties remembered consent to stable signing identity and process responsibility; unsigned/ad-hoc replacements can trigger new prompts. That supports conservative invalidation without overstating the specific TCC event. ([Apple DTS explanation](https://developer.apple.com/forums/thread/678819))

## Files and functions to change

- [calibration_ledger.py](/Users/edr/code/JouleWise/joulewise/calibration_ledger.py:1898): bounded custody wrapper/core; deadline plumbing through snapshot/readiness and custody-state checks.
- **New read-only custody worker module:** isolated verification, bounded protocol, no writer authority.
- [reserve_calibration_window_bracket.py](/Users/edr/code/JouleWise/scripts/reserve_calibration_window_bracket.py:189): shared enforcing preflight, verify-only mode, immediate timeout exit, structured refusal artifact.
- [validate_powermetrics_fiducial.py](/Users/edr/code/JouleWise/scripts/validate_powermetrics_fiducial.py:1330): bound all night custody verification paths and transport typed refusals.
- [calibration_exits.py](/Users/edr/code/JouleWise/joulewise/calibration_exits.py:18): enum, description, route, operational witness.
- [night_agent_install.py](/Users/edr/code/JouleWise/joulewise/night_agent_install.py:628), [run_night.py](/Users/edr/code/JouleWise/scripts/run_night.py:435), [night_gate.py](/Users/edr/code/JouleWise/joulewise/night_gate.py:83): launchd probe/admission binding, deadline supervision, refusal transport and collision handling.
- [calibration_derivation_only.zsh](/Users/edr/code/JouleWise/scripts/night_chains/calibration_derivation_only.zsh:160): pass deadline/refusal destinations.
- [derivation_night_runbook.md](/Users/edr/code/JouleWise/docs/phase_2/derivation_night_runbook.md:360), [NIGHT_COURIER_PROMPT.md](/Users/edr/code/JouleWise/docs/process/NIGHT_COURIER_PROMPT.md:7), and the generated refusal-contract projection: revised preconditions and reporting.

## Regressions

- Successful metadata probe followed by stalled governed read, through the real reservation CLI.
- Multiple individually slow observations exhaust **one shared budget**.
- Slow-but-within-budget success; hash mismatch remains `calibration_ledger_custody_invalid`.
- Timeout leaves ledger/pin unchanged, lease reacquirable, and no late worker activity.
- Existing-session timeout bypasses neither refusal nor recovery safeguards.
- Writer preflight and under-lease stalls refuse without starting the slot.
- Launchd full-path probe succeeds; missing/stale probe or changed interpreter blocks arm.
- Typed calibration refusal reaches result, artifact inventory, and stub-courier reporting.
- Dead-man refusal followed by custody/window/census refusal preserves both records.
- Window abort kills the chain and verifier; unproven termination suppresses courier.
- Preserve existing authentication-context tests and add the registry’s public-CLI witness. ([Witness requirement](/Users/edr/code/JouleWise/docs/contracts/calibration_ledger_append.md:23))

Read-only consult completed; no files changed, tests run, or launchd jobs started.