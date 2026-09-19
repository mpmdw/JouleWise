# Exhibit B — the contract and process clauses (verbatim at main `0c529f99`)

## docs/process/NIGHT_HANDBACK.md lines 125,140 at main `0c529f99`

```
| `--render-only directory must differ from launch_dir` | Use a separate directory for rendered job files. |

**Other explicit refusals — cold-gate path.**

| Exact cause | Why A172 grants no retry exception |
|---|---|
| `HOLD_CENSUS` | A supervisor census hold alone does not establish the narrowly evidenced idle arm cause. |
| `slot_refused` | A measurement slot refused; cure the finding before any further night. |

Unknown or mixed causes and every capture, clock, custody, ledger or pre-registration guard stay on the cold-gate path; receipt refusals remain ineligible for same-plan retries. Known concurrent refusal evidence overrides an eligible arm cause. These dispositions preserve existing harvest, delivery and human-resolution remedies; they do not call a review into a live chain.

R1's operative time bounds are `now < install_close_epoch(plan)` and plan age within `PLAN_MAX_AGE_S` (including the existing authored-to-t0 check), with at least 60 seconds between arm attempts. D-180's same-or-next-listed-span ceiling is subsumed by `install_close_epoch(plan)` and `PLAN_MAX_AGE_S`, because with whole-day install spans it could otherwise bind 15 minutes before install close. There is no attempt-count cap, separate notice-age limit, new window cadence or delay after a successful harvest.

D-182: binding observations inside the window are not retries; a terminal zero-capture machine-state refusal permits ONE new-plan successor only after positive evidence of no chain.started claim, no reservation or ledger session, no capture writer run and an empty runs/instrument_validation inventory, plus completed courier.sent delivery. zero_capture_successor_allowed checks that evidence separately. successor_arm_allowed requires a new id and digest, fresh notice, at least 60 s after the predecessor's terminal write, and now before the successor's own install_close_epoch. Every observed NO on any notice thread still stops. Never re-arm the predecessor or put a new plan in same-candidate retry history.

Every actual attempt sends a newly accepted notice and repeats the existing notice-to-publication lead: accepted email before publication, with no additional minimum interval. A notice is stale if its SHA-256 fingerprint (digest of the exact plan bytes) or reviewed head differs, a newer abort or NO exists, or it belongs to an earlier attempt. A new thread never clears an earlier NO. Waiting observations send no repeated email. Preserve each attempt in `$STAGE/arm-attempts/NNNNNN/` (a positive ordinal padded to at least six digits, without a count limit), created exclusively; never overwrite prior notice, candidate or failure evidence.
```

## docs/process/NIGHT_HANDBACK.md lines 88,110 at main `0c529f99`

```
| `night_refused_registration` | Required registration did not validate. |
| `night_window_expired` | Measurement window expired. |
| `night_plan_stale` | Plan age or pinned head failed; not a stale notice. |
| `night_plan_malformed` | Plan structure or fields failed their contract. |
| `night_chain_digest_mismatch` | Executable chain bytes differ from their fixed fingerprint. |
| `launch_go_receipt_missing` | Required measurement-pack launch authorization is absent. |
| `launch_go_receipt_invalid` | Required measurement-pack launch authorization is invalid. |
| `night_refused_class_unbuilt` | This gate cannot execute the requested plan class. |
| `night_receipt_class_invalid` | Receipt class/condition contract is invalid. |
| `night_probe_error` | An observation failed; missing evidence grants no permission. |
| `night_aborted_agent_present` | An agent appeared while the chain ran. |
| `night_chain_already_started` | The once-only chain-start record exists. |
| `night_chain_alive` | The existing chain has not been proved ended. |
| `night_chain_launch_failed` | Launch failed after the once-only start claim; not pre-arm transport. |
| `night_courier_running` | The result-delivery process is still running. |
| `night_courier_unavailable` | The driver's delivery executable is unavailable; not a failed notice send. |
| `night_plan_overruns_deadman` | Completion/dead-man schedule was refused; retained even if normally unreachable. |
| `night_record_exists` | A write-once night record proves invocation already occurred. |
| `night_calibration_refused` | The chain's calibration ledger refused (custody timeout, strict pre-reserve, or invalid custody); the document names the exact code; never an auto-retry cause. |
| `night_window_exceeded` | The chain ran past the exclusive window end and was terminated by the driver; reservation or capture intent may have been written and the session may need desk recovery; never an auto-retry cause. |

**Installer §1.3 refusals — cold-gate path.**

```

## docs/phase_2/derivation_night_runbook.md lines 3040,3055 at main `0c529f99`

```
Chain exits (`scripts/night_chains/calibration_derivation_only.zsh`):

| Signal | Meaning | Operator action |
|---|---|---|
| exit 64 | A knob (`SLOT_COUNT`, `SETTLE_S`, `SLOT_CADENCE_S`, `SLOT_CAPTURE_BUDGET_S`, `WINDOW_END_EPOCH_S`) was not a non-negative integer string, or failed the positivity check — which covers `SLOT_CAPTURE_BUDGET_S` as well as `SLOT_COUNT`, `SLOT_CADENCE_S` and `SETTLE_S`. Refused before the settle, the reservation and any operator-log write. | The environment or plan is malformed. No window time was spent and no partial night exists. Fix at the desk; author a fresh plan for a later night. **Why the budget is in the positivity guard:** at `SLOT_CAPTURE_BUDGET_S=0` the window test `slot_start + budget > WINDOW_END_EPOCH_S` becomes vacuous, so a slot could start one second before the agent-free window ends and capture straight past it. |
| exit 66 `derivation_chain_input_missing: <path>` | One of `PLAN`, `IDENTITY_EPOCH_JSON`, `T1_BINDINGS_JSON`, `CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN` was absent. | The clone is incomplete or a path in the plan is wrong. Re-verify §0.2 and §0.4 before authoring the next night. |
| exit 1 | **Ambiguous — read `chain.stderr.log` to disambiguate.** With a `FAIL <reason>` line it is a wrapper refusal (table above). Without one it is the tracked chain's own `:?required` guard, meaning the chain ran without the wrapper's environment. | Both are pre-window failures costing no window time. Resolve per the matching row above before re-arming. |
| Reservation enforcing preflight exits 2 | **Enforcing** means the decision is made while the reservation holds the writer lease (exclusive permission to change ledger state). `--pre-reserve-strict` refuses before retry, recovery or append, including interrupted claims. The check consumes up to the custody budget of window time. Only enforcing under-lease predicates can produce `ready_to_arm`; success also emits a `pre_reserve_readiness` diagnostic line. | `calibration_ledger_custody_timeout` stops with `night_stopped_preserved`, leaving ledger/session state unchanged; report the budget and elapsed time. `calibration_ledger_recovery_required` requires desk recovery. Other readiness refusals preserve their named cause. Do not retry or repair inside the window. |
| Verify-only probe receipt | **Verify-only** performs access checks and stops before append, settle or capture. Its `outcome: ok` is non-authorizing arm-admission evidence; it is never a `ready_to_arm` result. | Install requires matching input and interpreter fingerprints and fresh receipt timestamps. A refused probe does not authorize capture, recovery or retry. |
| `slot_end slot=dNN disposition=non-valid`, night continues | **Not a failure.** The writer exited 1: the row is finalized with a disposition other than `valid`, and the next declared slot runs on the unchanged cadence (§2.4). | Record the count of such slots. Do nothing else, and read no value. Exclusion is decided at issuance, by named mechanism. |
| `slot_refused slot=dNN rc=2` + chain exits 2, session left OPEN | The writer REFUSED this capture (`emit_refusal` exits 2). The row is **not** finalized, so the chain stops rather than continuing over an unrecorded slot — and deliberately does not abort the session. | Read the refusal in `chain.stderr.log`, then **desk recovery**: `recover_calibration_ledger.py … abort-session --session-id <id> --plan <plan> --reason <the named reason>` (§2.4). Never a retry inside the window. Until the session is closed the next night cannot open at head-equals-pin. |
| `slot_refused slot=dNN rc=<n≥3>` + chain exits with that status, session left OPEN | The writer crashed rather than refusing. Same dispatch branch, same unfinalized row. | Same desk recovery, and account for the crash before any further night is armed: a crash is a defect, not an outcome. |
| `slot_unused … reason=window_exhausted` + `session_abort` + exit 0 | The window could not finish a slot's 480 s budget. Slots are recorded unused, never compressed or retried. Δ larger than 1320 s is the usual cause (§1.2). | Record the count. The session is terminal and §2.5 judges its finalized rows (an equivalence night with fewer than six retained values is INCONCLUSIVE). No top-up, no fourth night (§2.4). |
| Any other non-zero exit, with a `session_open` line already in the chain log | A ledger call failed under `set -e` after the session was opened. | Treat exactly as `slot_refused`: read the log, then desk recovery with a named reason. A `session_open` line with no `session_abort` and no terminal slot means the session is still open, whatever the exit code was. |

Capture-writer refusals (`scripts/validate_powermetrics_fiducial.py`, codes in
```

## docs/contracts/night_quiet_admission.md lines 20,60 at main `0c529f99`

```
- **Terminal versus WAIT** distinguishes a refusal that ends this invocation immediately from an excessive-CPU observation that continues binding without writing a refusal artifact. An **ERROR** sample records an incomplete or invalid observation; it never counts as quiet.
- **Attribution** means identifying which observed processes contributed CPU work, alongside any work only visible in the host total.
- **Cutoff authority**, `cutoff_authority`, is the required record path naming the gate ruling that affirmed the sealed CPU limit; naming a path alone does not authenticate the ruling.

All admission policy numbers are **PROVISIONAL**. No cutoff is proposed or
validated here. Cold-gate ruling 70 proposition 4 refused activation pending
`QUIET-PREDICATE-EVIDENCE-01`: measured effects through the actual floor
pipeline and the clean-machine distribution, including observer cost. A cold
gate is an independent adjudication of a named proposition. It rules the
scientific cutoff; the magistrate (lead coordinator) owns implementation and
sequencing. The sealed policy must name the affirming ruling in
`cutoff_authority`; merely naming a path does not authenticate or supply that
ruling. No environment variable changes a parameter. The prospective packless
v4 receipt exception is recorded in the [pack receipt contract](pack_night_go_receipt.md).

## Why interval activity matters

On 2026-09-17 the one-minute load average was **3.66** at the 15:30 refusal,
above the legacy **2.0** maximum, although the agent census was empty. That
refused a census-clean machine during a Spotlight/mediaanalysisd burst; it
was not proof that CPU activity was scientifically clean. At 18:10–18:19 the
load was **1.3–1.5**, which would pass, while `fseventsd` continuously consumed
**85–100% of one core**. Load measures runnable/waiting work over time, not
the energy contamination of the upcoming observation interval.

A capture slot has a **480 s budget**. Using the illustrative assumption of
**5 W per busy core** over that entire budget gives 2400 J for one core.
The rejected arithmetic examples **0.05 core → 120 J per slot** and
**0.01 core → 24 J per slot** are not candidate cutoffs. D-078 clause 11's
instrument bars are approximately **1 J attribution limit** and **5 J
claim-side bar** per floor. A 1 J ceiling at 5 W/core over 480 s would imply
**0.0004 core**, below even the sampler's measured cost before including the
census. The earlier observer measurement omitted the census and cannot set
the full sampler floor; the native smoke below measures it again with census.
These calculations assume full-budget duration and a linear power model;
core mix and cancellation in the experiment's contrast must be measured.
**This is why the cutoff must be measured, not computed.** The numerical
examples authorize nothing. Evidence: [the executed harvest record](../process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md),
findings 1–2, and [D-078 clause 11](../decision_log.md).

## Sealed policy and version dispatch
```

## docs/contracts/night_quiet_admission.md lines 78,90 at main `0c529f99`

```

Every key is required and extra keys refuse. Only `cpu_interval_v1` is
recognized. All numbers must be finite. Durations and the consecutive count must be
positive; the sample interval is a whole number of seconds and the consecutive
count is an integer of at least one. The cutoff is nonnegative: zero explicitly
admits nothing, even a zero-CPU observation. `cutoff_authority` is a required
nonempty string naming the record path of the gate ruling that affirmed the
cutoff. No v4 plan can be authored without naming who affirmed its cutoff;
test fixtures use the literal above, which is not activation authority. The bind allocation must hold the sample
interval times the required count, and window_max_s must hold bind_max_s plus
post_bind_budget_s. There is no implicit policy for an old or malformed plan.


```

## docs/contracts/night_quiet_admission.md lines 118,130 at main `0c529f99`

```
without one, the identity is listed as `unaccounted`, never treated as a known
zero. An observer cannot recover a process born and exited between snapshots;
host busy time includes such work, kernel time and other unattributed activity.

```
process_busy_cores = sum(measurable CPU-second deltas) / elapsed_seconds
host_busy_cores    = logical_cpu_count × (1 − idle_fraction)
busy_cores         = max(process_busy_cores, host_busy_cores)
quiet             = busy_core_max > 0 and busy_cores ≤ busy_core_max
```

All processes count. There are no daemon exemptions or name-based bans. The
observer (driver interpreter and its descendants) counts too and is labelled
```

