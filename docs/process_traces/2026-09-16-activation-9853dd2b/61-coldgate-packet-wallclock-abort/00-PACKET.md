# Cold-gate packet 61 — NIGHT-STALL-WALLCLOCK-ABORT-01 (kernel rank 221, P1): where the night driver's wall-clock deadline sits, how large its shutdown allowance is, and how termination is proved (assembled mechanically by activation 9853dd2b, 2026-09-17 10:55 PDT)

Convened under rule 11 because the lane's acceptance text (exhibit A) sends "the grace value" to the cold gate or a consult before merge, and because the sibling lanes that landed this week (NIGHT-RESERVE-HANG-01, CUSTODY-PASS-MEMO-01) changed the arithmetic the value depends on: the chain's own end-of-window abort now runs under an inherited custody budget and can lawfully take up to about 26 minutes (exhibit C). Nothing is armed; no night can be re-planned before this lane lands.

## What was found (from the exhibits; the judge verifies)

- On 2026-09-16 a chain stalled inside its reservation for 11 h 07 m; the chain's own window guard sits AFTER the reservation step (exhibit E lines 214–236 at this head; exhibit F), the dead-man correctly refuses while the chain is alive, and the driver has no wall-clock abort: the night ended only when a person's session entered the agent census (exhibit F). The custody-side cure (a bounded read with a typed refusal) has landed; this lane is the driver-side backstop the design consult called "not redundant" (exhibit B).
- The driver's only termination path today is the census-abort branch of `_run_chain_once` (exhibit D): `_terminate_process_group` sends SIGTERM to the chain's process group, waits up to 30 s on the DIRECT child, then SIGKILL and another 30 s, and returns True only when `wait()` proves the direct child exited; an unproven termination writes `chain.unkilled`, refuses `night_chain_alive` and suppresses the courier. The loop sleeps at most 1 s between census probes and checks nothing else against the clock.
- Existing time constants (exhibit D): `CENSUS_INTERVAL_S = 30`, `COURIER_DEADLINE_S = 300`, `DEADMAN_GRACE_S = 3600`; the dead-man fires at `t0 + window_max_s + COURIER_DEADLINE_S + DEADMAN_GRACE_S` (3900 s after the exclusive window end), rounded to a minute.
- The chain's `abort_window_exhausted` (exhibit E) starts when the NEXT slot cannot fit before `WINDOW_END_EPOCH_S`, so it normally begins BEFORE the window end; under the inherited custody budget its worst case is `SLOT_COUNT × CUSTODY_BUDGET_S = 12 × 120 s = 24 min` (26 min with its own call), which record 44 §4 (exhibit C) places inside the 3900 s dead-man allowance with ~39 min spare. A driver that kills the chain AT the window end can therefore interrupt a lawful abort, leaving the ledger session open with a live lease for desk recovery.
- The design consult's recommendation (exhibit B §5): initiate termination at the exclusive window end with a separately bounded shutdown grace; no pre-termination grace that permits acquisition beyond the declared window; check the deadline independently of the census cadence, including around potentially blocking census probes; termination proof must cover the custody worker (the helper waits for the direct child only).

## Q1 — where the driver's deadline sits and how large the shutdown allowance is (rule one option, or write a better one, with numbers)

(a) Terminate at the exclusive window end `t0 + window_max_s`; shutdown allowance = the existing helper's 30 s SIGTERM wait + 30 s SIGKILL wait; accept that a lawful `abort_window_exhausted` still running at the window end is killed and the session is left open for desk recovery (the courier then reports `night_window_exceeded`). (b) Terminate at `t0 + window_max_s + COURIER_DEADLINE_S` (300 s): the allowance the dead-man arithmetic already reserves between the window end and delivery, so no new constant is invented; a lawful abort longer than 300 s is still cut. (c) Terminate at the window end plus an explicit shutdown allowance sized to the abort path's worst case (SLOT_COUNT × CUSTODY_BUDGET_S, 1440 s today), keeping the total inside the dead-man's 3900 s; state what carries the number (the plan, the chain environment, or a driver constant) and whether that is a "pre-termination grace that permits acquisition beyond the declared window" — the thing exhibit B forbids — or not, given that no NEW slot can be acquired once `abort_window_exhausted` has begun. (d) Bound the chain's abort itself smaller (a per-slot custody budget for the abort path, or one bounded pass instead of one per slot) so that (a) or (b) suffices; say which and what it costs. Whichever option: is the value a mechanism choice or a contract change?

## Q2 — independence from the census cadence

The acceptance requires the deadline check to run "independently of the census cadence", and exhibit B adds "including around potentially blocking census probes" (a census probe is a `pgrep` subprocess with its own timeout). Rule the mechanism: (i) a monotonic deadline check in the existing loop before AND after each probe plus a sleep bound that never exceeds the time to the deadline; (ii) a separate watchdog thread or `signal.alarm` that terminates the group when the deadline passes regardless of where the loop is; (iii) both. State the failure the chosen mechanism still cannot cover.

## Q3 — proof of termination of the whole process group

The helper proves only the direct child's exit. The acceptance requires proof that the whole process group, including any custody worker, is gone before the courier runs. Rule: (i) after SIGKILL, a bounded census of the group (`pgrep -g <pgid>`, retried to a short deadline) must return empty; on failure keep today's behaviour (`chain.unkilled`, `night_chain_alive`, courier suppressed); (ii) additionally require the custody worker's own pid file or progress record to show exit; (iii) a better proof. Also rule: does an unproven termination at the wall-clock deadline keep `night_chain_alive` as its reason, or does it need a distinct reason so the courier can say "window exceeded AND not proven dead"?

## Q4 — the reason code `night_window_exceeded`

It must be registered in `NIGHT_DRIVER_REASON_CODES` (exhibit D's registry; the arm-retry registry parity test forces an explicit cold-gate/retry assignment for every code). Rule its class: COLD (a wall-clock overrun means a stall the machine did not diagnose; a human reads the record before another arm) or RETRY (a zero-capture overrun is operationally like a zero-capture t0 refusal, which Ed ruled auto-retries). State the deciding consideration.

## Q5 — landing

(i) Implement now (the only available seats are Opus 5; the Codex quota is exhausted until 2026-09-19 03:35 PDT) with regressions proving: a chain that sleeps past the deadline is terminated with its custody worker and the refusal named; unproven termination suppresses the courier; a lawful abort that finishes inside the allowance is NOT interrupted; then the night is re-planned. (ii) Re-plan the night first with the custody-side cures alone (the driver-side backstop deferred to the next lane), given that the failure mode this backstop covers is now a typed refusal within budget. Rule one, with the risk of the other.

## Constraints on the judge

Rule only the questions above; do not amend any rule, decision-log entry or skill doctrine (name text changes as text for the magistrate to record). Cite exhibits by name; code by file:line only if you read it in this checkout (main `5472ff53`). For Q1 and Q3, execute at least one probe in the foreground (e.g. a short zsh script whose child sleeps in a new session, terminated through `os.killpg` from Python, proving what `wait()` on the direct child does and does not establish about a grandchild). State for each ruling whether it is a mechanism choice or a contract change. Under 14 KB. Write the ruling to `docs/process_traces/2026-09-16-activation-9853dd2b/61-coldgate-packet-wallclock-abort/10-coldgate-fable-ruling.md`.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
c35bffa070ddab61e7ff2bc8c3b02bb771477ac3791c550c6bf3f757f1ccbdc8  exhibit-A-lane-A221-kernel.md
273ccbd70442d2b611cbcc3a62ace4a34be125b58dc799255b4031f3979269b3  exhibit-B-consult-02-section-5.md
5fbe3ee560c782c8f29606db7cc9694dc5344ec4f584b0658f38e3ad5773f0c0  exhibit-C-consult-44-abort-path.md
ddee6008f29b6cba9543a4bbd8b2a187732403261e2a710d3824226e325d0f52  exhibit-D-run_night-termination-and-timing.md
7e11a4bb623dae8cfd3551417136d72caf3a6229653fb8a0eaf45e6a0fbe1a56  exhibit-E-chain-window-guard.md
795ebd7a1df6c4c29eb18641b51de2a8698ed0420f7846c205ef480cbc63c15a  exhibit-F-e0c58148-defects.md
```
