# Exhibit D — driver, generator and chain timing at commit `a90ab4e8`, and the arithmetic of a 9600 s window

Blocks 1–6 are verbatim `sed -n | nl -ba` output from this checkout at
`a90ab4e8`; the leading integer on each line is the file's line number.
Section 7 is NOT an excerpt: it is arithmetic this session computed from the
constants in blocks 1–6 using the consult's formulas, and every number in it
names its source.

## D1 — `scripts/run_night.py` timing constants (lines 58–92)

```
    58	
    59	
    60	RESULT_SCHEMA = "joulewise.unattended_night_result.v1"
    61	REFUSAL_SCHEMA = "joulewise.night_refusal.v1"
    62	PROBE_TIMEOUT_S = 30
    63	CENSUS_INTERVAL_S = 30
    64	# R-7: min(600, max(3 * (5303 ms / 1000), 300)) from cold_start.json.
    65	COURIER_DEADLINE_S = 300
    66	# Separate shutdown allowance for the chain's bounded end-of-window abort (one
    67	# 120 s custody budget for the abort's single custody read plus lease overhead);
    68	# not derived from the courier deadline.
    69	WINDOW_SHUTDOWN_GRACE_S = 300
    70	# One process-group SIGTERM or SIGKILL reaches the members that exist when it
    71	# is sent, and wait() only ever proves the DIRECT child ended. Proving the
    72	# GROUP gone therefore needs a census, and a census needs a bound: each phase
    73	# re-signals the group and re-censuses it every GROUP_CENSUS_INTERVAL_S for at
    74	# most GROUP_CENSUS_WINDOW_S. Worst case for the whole sequence:
    75	# 30 s wait + 5 s census + 30 s wait + 5 s census.
    76	GROUP_CENSUS_WINDOW_S = 5
    77	GROUP_CENSUS_INTERVAL_S = 0.2
    78	GROUP_WAIT_S = 30
    79	TERMINATION_BOUND_S = 2 * (GROUP_WAIT_S + GROUP_CENSUS_WINDOW_S)
    80	COURIER_BACKOFF_S = (60, 180, 600)
    81	COURIER_LOCK_FRESH_S = COURIER_DEADLINE_S + max(COURIER_BACKOFF_S)
    82	DEADMAN_GRACE_S = 3600
    83	# LEAD-MARGIN-01: 391a194b introduced a flat hour before the resident fence.
    84	# D-180/D-181 permit any quiet window; that pad is not a measurement gate.
    85	# Two minutes separate the exclusive installation cutoff from REQUEST (twelve
    86	# nominal 10 s resident polls to discover the published plan and hand back).
    87	# With the eight-minute plan lead, the exclusive arm-to-t0 floor is ten minutes.
    88	# This is an installation/handback allowance, not load-average settling time:
    89	# that belongs after agent teardown. The installer still rechecks its cutoff.
    90	INSTALL_CLOSE_MARGIN_S = 2 * 60
    91	INSTALL_SPANS: tuple[tuple[str, str], ...] = (("00:00", "24:00"),)
```

Note line 62: `PROBE_TIMEOUT_S = 30` — the existing subprocess bound. Bearing
on proposition 5 and on the consult's warning that a 30–60 s sampler cannot be
wrapped by it.

## D2 — the forced-shutdown deadline (lines 835–850)

```
   835	        census_hits: list[dict[str, Any]] = []
   836	        # Read the driver's wall clock ONCE, here, and convert the deadline to
   837	        # a monotonic instant: a clock step during the window must not move
   838	        # the moment the chain is stopped. Neither `deadman_epoch` nor the plan
   839	        # schema learns about this instant -- a plan field would be a contract
   840	        # change, and the v2 schema is exact (see the _chain_environment note).
   841	        deadline_epoch_s = plan.t0_epoch_s + plan.window_max_s + WINDOW_SHUTDOWN_GRACE_S
   842	        deadline = _WindowDeadline(
   843	            process,
   844	            pgid=pgid,
   845	            night_dir=night_dir,
   846	            plan=plan,
   847	            deadline_epoch_s=deadline_epoch_s,
   848	            deadline_monotonic=(
   849	                time.monotonic() + (deadline_epoch_s - float(probes.now_epoch_s()))
   850	            ),
```

Forced shutdown fires at `t0 + window_max_s + WINDOW_SHUTDOWN_GRACE_S`
(line 841), i.e. `E + 300`, NOT at `E`. The deadline is converted to a
monotonic instant once (lines 848–850).

## D3 — dead-man and install close (lines 1399–1415)

```
  1399	def deadman_epoch(plan: NightPlan) -> float:
  1400	    """The plan's completion plus recovery grace, rounded up to a minute."""
  1401	    try:
  1402	        return float(math.ceil(
  1403	            (plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S + DEADMAN_GRACE_S)
  1404	            / 60
  1405	        ) * 60)
  1406	    except (OverflowError, ValueError) as exc:
  1407	        raise ValueError(f"t0_epoch_s/window_max_s cannot derive deadman_epoch_s: {exc}") from exc
  1408	
  1409	
  1410	def install_close_epoch(plan: NightPlan) -> float:
  1411	    # The watchdog owns this existing stand-down lead and imports this driver.
  1412	    # Resolve it only when needed, after module initialization on either path.
  1413	    from scripts.magistrate_watchdog import PLAN_LEAD_S
  1414	
  1415	    return plan.t0_epoch_s - PLAN_LEAD_S - INSTALL_CLOSE_MARGIN_S
```

`scripts/magistrate_watchdog.py:86` reads `PLAN_LEAD_S = 8 * 60`, so
`install_close_epoch(plan) = t0 - 480 - 120 = t0 - 600 s = t0 - 10 minutes`.
Compare exhibit E §E3: `docs/process/NIGHT_HANDBACK.md:59` still says
`t0 - 85 minutes`.

## D4 — nominal completion and the artifact list (lines 1506–1507, 945–951)

```
  1506	def _completion_epoch_s(plan: NightPlan) -> float:
  1507	    return plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S
```

```
   945	def _artifact_list(custody_root: Path, night_dir: Path) -> list[dict[str, str]]:
   946	    paths = [
   947	        custody_root / "night.log",
   948	        night_dir / "receipt.json",
   949	        night_dir / "go_receipt.json",
   950	        night_dir / "go-census.json",
   951	        *_refusal_paths(night_dir),
```

`_artifact_list` is the enumerated set the courier ships; a new
`quiet_samples.jsonl` is not shipped unless it is added here.

## D5 — where `evaluate_night` is called (lines 2052–2072)

```
  2052	            receipt = evaluate_night(plan, probes, pack_arm_receipt=arm_state["path"])
  2053	        except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
  2054	            receipt = _pack_refused_receipt(plan, error, probes)
  2055	    else:
  2056	        # Reuse the first census for the legacy evaluator's census slot; no
  2057	        # filesystem or command probe preceded the driver's initial census.
  2058	        original_run = probes.run
  2059	        cached = [initial_probe]
  2060	        def first_census(argv):
  2061	            if tuple(argv) == night_gate.AGENT_CENSUS_ARGV and cached:
  2062	                return cached.pop()
  2063	            return original_run(argv)
  2064	        receipt = evaluate_night(plan, replace(probes, run=first_census))
  2065	    if not is_pack or receipt.verdict != "GO":
  2066	        _write_bytes_exclusive(night_dir / "receipt.json", receipt.to_json_bytes())
  2067	    gate_message = f"night gate verdict={receipt.verdict}"
  2068	    if receipt.verdict == "REFUSED":
  2069	        refusal = _refusal_from_object(receipt.refusal) or {}
  2070	        detail = " ".join(str(refusal.get("detail", "")).splitlines())[:200]
  2071	        gate_message += f" reason={refusal.get('reason')} detail={detail}"
  2072	    _append_log(custody_root, gate_message)
```

Two call sites (2052 pack, 2064 legacy). Note lines 2058–2063: the driver's
FIRST census result is cached and replayed into the evaluator, so today's gate
does not take a fresh census of its own. Bearing on proposition 6 (a bind
window must re-census, not replay).

## D6 — the generator's schedule constants and the chain's order

`scripts/gen_derivation_night.py` lines 80–95:

```
    80	DERIVATION_RECEIPT_CLASS = "DIAGNOSTIC_NO_PACK"
    81	
    82	# Chain defaults, quoted from the chain itself (see CHAIN_ANCHORS) and pinned
    83	# explicitly by the wrapper: the driver hands the chain `os.environ.copy()`, so
    84	# an inherited SETTLE_S, SLEEP or DATE from the arming operator's shell would
    85	# silently retime the night.
    86	DEFAULT_SETTLE_S = 600
    87	DEFAULT_SLOT_CADENCE_S = 600
    88	DEFAULT_SLOT_CAPTURE_BUDGET_S = 480
    89	
    90	# The chain does its input checks and bounded reservation preflight (including
    91	# enforcing readiness) BEFORE reservation and settle. The driver does gate work
    92	# before it starts the chain at all.  This is the allowance the window must hold
    93	# on top of the programmed span; it is deliberately far smaller than runbook
    94	# 99 §1.2's total 1320 s margin, which also covers per-capture overrun.
    95	PRE_SETTLE_ALLOWANCE_S = 300
```

lines 124–132 (the span function's contract):

```
   124	def programmed_span_s(
   125	    slot_count: int,
   126	    settle_s: int = DEFAULT_SETTLE_S,
   127	    slot_cadence_s: int = DEFAULT_SLOT_CADENCE_S,
   128	    slot_capture_budget_s: int = DEFAULT_SLOT_CAPTURE_BUDGET_S,
   129	) -> int:
   130	    """Seconds from chain start to the end of the last slot's capture budget.
   131	
   132	    The cadence is START-to-START, so N slots cost (N-1) gaps plus one budget:
```

lines 462–463 and 509–520 (`build_spec`'s window check):

```
   462	def build_spec(args: argparse.Namespace) -> tuple[WrapperSpec, Path, bytes]:
   463	    """Validate every input and resolve every literal, or refuse."""
```

```
   509	    # The window must hold the schedule the chain will actually run, or the
   510	    # night opens its session and aborts part-way with window_exhausted.
   511	    required_span = programmed_span_s(slot_count)
   512	    required_window = required_span + PRE_SETTLE_ALLOWANCE_S
   513	    if plan.window_max_s < required_window:
   514	        raise GenerationRefusal(
   515	            f"window_max_s {plan.window_max_s} < required {required_span} + "
   516	            f"{PRE_SETTLE_ALLOWANCE_S} = {required_window} s: the programmed "
   517	            f"span of {slot_count} slots is settle {DEFAULT_SETTLE_S} + "
   518	            f"{slot_count - 1} x cadence {DEFAULT_SLOT_CADENCE_S} + budget "
   519	            f"{DEFAULT_SLOT_CAPTURE_BUDGET_S}, plus the pre-settle allowance; "
   520	            "lengthen the window rather than shortening the schedule"
```

`scripts/night_chains/calibration_derivation_only.zsh` lines 187–222 — the
order of operations AFTER the gate says GO:

```
   187	reservation_call \
   188	    --pre-reserve-strict \
   189	    --ledger "$CALIBRATION_LEDGER" \
   190	    --head-pin "$LEDGER_HEAD_PIN" \
   191	    --custody-budget-s "${CUSTODY_BUDGET_S:-120}" \
   192	    --custody-deadline-epoch-s "$(( WINDOW_END_EPOCH_S - 10 ))" \
   193	    --session-kind derivation \
   194	    --slot-count "$SLOT_COUNT" \
   195	    --session-id "$SESSION_ID" \
   196	    --window-id "$WINDOW_ID" \
   197	    --plan-id "$PLAN_ID" \
   198	    --plan-sha256 "$PLAN_SHA256" \
   199	    --plan "$PLAN" \
   200	    --evidence-root-id "$EVIDENCE_ROOT_ID" \
   201	    --runs-root "$RUNS_ROOT" \
   202	    --identity-epoch-json "$IDENTITY_EPOCH_JSON" \
   203	    --t1-bindings-json "$T1_BINDINGS_JSON" \
   204	    "$@" \
   205	    "${reservation_mode[@]}"
```

```
   215	# The ONE settle of the night, and the last machine action before it is the
   216	# reservation above. The cadence below is start-to-start and never inserts a
   217	# second settle.
   218	settle
   219	log_event "settle_complete settle_s=$SETTLE_S"
   220	
   221	next_start=$("$DATE" +%s)
   222	for (( index = 1; index <= SLOT_COUNT; index++ )); do
```

Reservation (line 187) runs FIRST, then the one 600 s settle (line 218), then
the slots. Admission at GO is therefore separated from the first capture by
the reservation plus 600 s.

## D7 — computed table (NOT an excerpt; this session's arithmetic)

A v4 derivation plan with `bind_max_s B = 600`, `post_bind_budget_s R = 9000`
and `window_max_s = B + R = 9600`, as proposed at exhibit A §2 and exhibit G
§D4. `t0` is the plan's scheduled start; all offsets are seconds from `t0`.

| Quantity | Formula | Source of the formula | Value |
|---|---|---|---|
| `B` bind allocation | plan field `bind_max_s` | exhibit A §2 table; exhibit G §D1 | 600 |
| `R` post-bind budget | plan field `post_bind_budget_s` | exhibit A §2 table; exhibit G §D1 | 9000 |
| `window_max_s` | `B + R` | exhibit A §2 ("Validate `window_max_s >= B+R`") | 9600 |
| `E` acquisition end | `t0 + window_max_s` | D2 line 841 (`plan.t0_epoch_s + plan.window_max_s`) | `t0 + 9600` |
| bind deadline | `min(t0 + B, E - R)` | exhibit A §2 ("Binding ends at `min(t0+B,E-R)`") | `t0 + 600` (both branches equal) |
| forced shutdown | `E + WINDOW_SHUTDOWN_GRACE_S` | D1 line 69 + D2 line 841 | `t0 + 9900` |
| nominal completion | `E + COURIER_DEADLINE_S` | D4 line 1507 + D1 line 65 | `t0 + 9900` |
| dead-man | `60 x ceil((E + 300 + 3600)/60)` | D3 lines 1402–1405 + D1 lines 65, 82 | `t0 + 13500` (t0 minute-aligned) |
| install close | `t0 - PLAN_LEAD_S - INSTALL_CLOSE_MARGIN_S` | D3 line 1415; `magistrate_watchdog.py:86` `PLAN_LEAD_S = 8*60`; D1 line 90 | `t0 - 600` |

Runway remaining after GO, where "remaining" means `E - GO_instant`:

| GO instant | Remaining to `E` | Programmed span needed | Slack |
|---|---|---|---|
| `t0 + 0` | 9600 s | 7980 s | 1620 s |
| `t0 + 187` | 9413 s | 7980 s | 1433 s |
| `t0 + 600` (bind deadline) | 9000 s | 7980 s | 1020 s |

"Programmed span needed" = `programmed_span_s(12) + PRE_SETTLE_ALLOWANCE_S`,
computed from D6: `settle 600 + (12-1) x cadence 600 + budget 480 = 7680`,
plus `PRE_SETTLE_ALLOWANCE_S = 300`, total `7980`. Twelve slots is the count
the consult and the brief assume for a derivation night; the judge should
verify the slot count against the plan it is actually ruling on, because
`build_spec` (D6 line 511) takes `slot_count` as an input, not a constant.

Three facts this table makes checkable, each stated without argument:

1. `E`, the forced shutdown, the nominal completion and the dead-man are all
   derived from `t0` and `window_max_s` only (D2, D3, D4). None of them reads
   the GO instant, so a GO at `t0 + 600` shortens the runway and moves nothing
   else.
2. At the latest admissible GO the slack over the programmed span is 1020 s,
   which is 3.4x `PRE_SETTLE_ALLOWANCE_S`. At `t0 + 0` it is 1620 s.
3. Adding 600 s of bind allocation to today's 9000 s window (9600 total)
   leaves the post-bind runway exactly equal to today's whole window. This is
   what the consult means by "the acquisition end is fixed": the comparison
   that matters is `R` versus 7980 s, not `window_max_s` versus 9000 s.
