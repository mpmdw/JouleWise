# Courier record — rehearsal-20260916c (night courier, 2026-09-16 03:25–03:31 PDT)

Written by the night courier session (pid 10808 / heartbeat pid 10900, Fable 5.1)
that the night driver (pid 10751) launched after the stub completed. The courier
prompt (`docs/process/NIGHT_HANDBACK.md` at H `be221f6a`) named this night's
purpose, result paths and next lane; the handback was PRESENT.

## 1. What fired (from the records, not from the handback)

| Fact | Value |
|---|---|
| Plan | `rehearsal-20260916c`, class `REHEARSAL_STUB`, t0 epoch 1789554300 (03:25:00 PDT 2026-09-16), window 900 s |
| Frozen triple | (`rehearsal-20260916c`, `/Users/edr/JouleWise-measurement-rehearsal-20260916c`, `be221f6a886498f62154faac0b5da14cb66616a1`) |
| Driver start (launchd) | 03:25:00.821 PDT (`night.log`: `night driver started`) |
| Gate verdict | `night gate verdict=REFUSED reason=night_refused_agent_present` at 03:25:00.844 |
| Census hit | `pgrep -lf codex\|claude\|t3` exit 0: pid 7066 `claude` (Ed's interactive session 3427f330), 7086/7094 its `codex mcp-server` seat, 9850 its `/bin/zsh -c` wait loop |
| Stub chain | pid 10755, started 03:25:00.847, exited 03:25:03.118, exit code 0, stdout `REHEARSAL`, stderr empty |
| Result | `result.json` verdict `REHEARSAL_ONLY`, `chain_exit_code` 0, `aborted_reason` null, `chain_sha256` null, `census_count` 1, `census_hits` 1 |
| Receipt | `receipt.json` verdict `REFUSED`, refusal `night_refused_agent_present`; C2 `NOT_APPLICABLE`, C3 FAIL (census), C4 FAIL (`not evaluated after refusal`), C5 FAIL with driver/measurement/plan heads all `be221f6a` |
| `refusal.json` | absent (result directs to `night/receipt.json`) |
| Results branch | `night-results/rehearsal-20260916c` on origin: `27e3855f` (03:25:10, night records) then `bb7c1d55` (03:26:39, courier records); every branch file except the still-growing `night.log` is `cmp`-identical to the custody record (9/9 SAME) |
| Courier | attempt 1, heartbeat seen (epoch 1789554318), sent; Gmail message id `1a0a9c0fd1fc101e` (thread `1a0a9c0fd1fc101e`); `courier.sent` written epoch 1789554397 |
| `launchd.night.err` | EMPTY (0 bytes); `launchd.night.out` EMPTY |
| Launchd after the driver exited | `com.joulewise.night` last exit 3 (the stub's unconditional status), `com.joulewise.night.deadman` 0, `com.joulewise.magistrate` 0; both night plists still in `~/Library/LaunchAgents` (not uninstalled) |
| Watchdog at courier launch (prompt fields) | `/Users/edr/night-custody/magistrate/state.json` age 45.500 s, decision `HOLD_CENSUS` — alive; reason `production census non-empty inside plan span` (transition 161, 03:19:23) |

## 2. Acceptance for this stub (handback §Next lane), on the records

| Clause | Evidence | Verdict |
|---|---|---|
| `result.json` verdict `REHEARSAL_ONLY`, or a recorded `night_refused_agent_present` hit with the stub still completing | both: `REHEARSAL_ONLY` and the hit recorded in `result.json.census_hits`, `receipt.json.refusal`, `censuses.jsonl` | MET |
| `chain_exit_code` 0 | `result.json` and `chain.exited` both 0 | MET |
| EMPTY `launchd.night.err` | 0 bytes | MET |
| No crash, no `night_probe_error`, no installer/launchd irregularity visible in the records | `night.log` has the four expected lines plus the courier line; stderr streams empty | none observed |

The handback's §Purpose predicted exactly this outcome ("Ed's interactive
session ... may still be alive at t0 ... the stub still runs and the hit is
recorded"). This record and the result record agree.

## 3. What the courier did NOT do, and why

The harvest (lstat inventory, byte-exact archive, `--uninstall` FROM the
clone, plan-root retirement) is assigned by this handback's §Next lane to the
**relaunched magistrate**, and only after the completion boundary 03:45:00 PDT
(epoch 1789555500) with `courier.sent` present. `magistrate_watchdog.plan_span_active`
keeps the span active until that boundary and releases it once `courier.sent`
exists, so the watchdog is free to relaunch the magistrate at its first tick
after 03:45 (300-second cadence). Running the harvest or `--uninstall` from
this courier would (a) act before the boundary the handback sets and (b) risk
two agents retiring the same root. The courier therefore stops after this
record. The pre-03:45 records are complete; nothing in them needs human
resolution; no `--uninstall` was attempted, so no retained/UNKNOWN outcome
exists.

## 4. Next exact action (successor magistrate, after 03:45 + `courier.sent`)

1. Harvest per §Next lane: read the records above; `lstat` inventory; byte-exact archive outside watchdog discovery.
2. `cd /Users/edr/JouleWise-measurement-rehearsal-20260916c && scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260916c/night_plan.json --uninstall`; record the exit code. Only 0 permits step 3.
3. Retire the plan root to `~/night-archive/rehearsal-20260916c-plan-root-retired-<epoch>` with `SHA256SUMS`; remove the stub clone; also the lapsed `rehearsal-20260916` staging/custody dirs per the arming activation's note.
4. The equivalence science night (issue #316) as a `DIAGNOSTIC_NO_PACK` plan with a clean all-agents-closed census.
