# Exhibit E — the retry policy in code and the handback prose it generates, at commit `a90ab4e8`

Blocks are verbatim `sed -n | nl -ba` output; the leading integer is the file's
line number. Bearing on proposition 9 (zero-capture bind-expiry refusal and the
successor-retry remedy).

## E1 — `joulewise/arm_retry.py`: the cold-gate code table (lines 28–40)

```
    28	# Explicit assignments are intentional: registry additions must force review.
    29	COLD_GATE_CODES = {
    30	    "night_refused_agent_present": "Production census refusal, including a receipt at t0; never an idle arm event.",
    31	    "night_refused_not_quiet": "Machine quietness failed; load, power and thermal thresholds stay fixed.",
    32	    "night_refused_hid_idle": "User-input inactivity guard failed.",
    33	    "night_refused_boot_clock": "Measurement boot/clock guard failed; not a watchdog uncertainty tick.",
    34	    "night_refused_registration": "Required registration did not validate.",
    35	    "night_window_expired": "Measurement window expired.",
    36	    "night_plan_stale": "Plan age or pinned head failed; not a stale notice.",
    37	    "night_plan_malformed": "Plan structure or fields failed their contract.",
    38	    "night_chain_digest_mismatch": "Executable chain bytes differ from their fixed fingerprint.",
    39	    "launch_go_receipt_missing": "Required measurement-pack launch authorization is absent.",
    40	    "launch_go_receipt_invalid": "Required measurement-pack launch authorization is invalid.",
```

Line 31 is the sentence a bind-window redesign would falsify: it asserts that
"load, power and thermal thresholds stay fixed."

## E2 — `classify_abort`, `retry_allowed`, `render_policy` (lines 82–110, 158–175, 195–205)

```
    82	@dataclass(frozen=True)
    83	class Decision:
    84	    allowed: bool
    85	    reason: str
    86	
    87	
    88	def classify_abort(cause):
    89	    """Classify exact arm-event IDs; unknown, mixed and malformed causes stop."""
    90	    return DISPOSITIONS.get(cause, "cold_gate") if isinstance(cause, str) else "cold_gate"
    91	
    92	
    93	def _number(value):
    94	    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
    95	        raise ValueError("expected a finite epoch/duration")
    96	    return value
    97	
    98	
    99	def retry_allowed(now_epoch_s, plan, attempts, notice) -> Decision:
   100	    """Check supplied evidence, without observing or mutating the machine.
   101	
   102	    plan: mapping with ``plan_bytes`` (reread candidate), ``saved_plan_bytes``
   103	    (pre-notice snapshot), ``reviewed_head``, ``install_close_epoch_s`` from
   104	    run_night.install_close_epoch, and ``plan_max_age_s`` from night_gate.
   105	
   106	    attempts: chronological prior abort mappings: attempt (1-based),
   107	    attempt_epoch_s, abort_epoch_s, cause, receipt_class, plan_sha256,
   108	    message_id (empty if no send), outcome (not_published/restored_unpublished).
   109	    The latter outcome certifies noncommit, uninstall 0, byte comparison and
   110	    unpublication. A lost install response cannot establish that outcome.
```

```
   158	            started = _number(prior["attempt_epoch_s"])
   159	            aborted = _number(prior["abort_epoch_s"])
   160	            if (type(prior["attempt"]) is not int or prior["attempt"] != ordinal
   161	                    or started > aborted or aborted > now
   162	                    or (previous_abort is not None and started < previous_abort)):
   163	                return Decision(False, "invalid_history")
   164	            if (classify_abort(prior["cause"]) != "retry"
   165	                    or prior["outcome"] not in ("not_published", "restored_unpublished")):
   166	                return Decision(False, "cold_gate_history")
   167	            if (prior["receipt_class"] != candidate["receipt_class"]
   168	                    or prior["plan_sha256"] != digest):
   169	                return Decision(False, "candidate_changed")
   170	            if prior["message_id"] == notice["message_id"]:
   171	                return Decision(False, "notice_reused")
   172	            previous_abort = aborted
   173	        if notice["latest_abort_epoch_s"] != previous_abort:
   174	            return Decision(False, "notice_abort_mismatch")
   175	        if attempts and now - attempts[-1]["attempt_epoch_s"] < RETRY_INTERVAL_S:
```

Line 164: any cause classified `cold_gate` in a prior attempt's history makes
the whole retry `cold_gate_history`. Lines 167–169: the history check requires
the SAME `plan_sha256`, so a new-plan successor cannot present itself as
another attempt on the same candidate.

```
   195	def render_policy() -> str:
   196	    """Return the entire marked Markdown block, including its final newline."""
   197	    lines = ["<!-- BEGIN ARM-RETRY-POLICY v1 -->", "",
   198	             "D-180 clause 2; A172 rulings R1–R3 and fix-round-1 R1–R4 (2026-09-15). "
   199	             "Exact arm-event IDs are labels for recorded observations, not receipt codes.", "",
   200	             "| Retry cause | Meaning and required clearance |", "|---|---|"]
   201	    lines.extend("| `{}` | {} |".format(k, v) for k, v in RETRY_CAUSES.items())
   202	    for title, rows in (("Gate and driver refusals", COLD_GATE_CODES),
   203	                        ("Installer §1.3 refusals", INSTALLER_REFUSALS),
   204	                        ("Other explicit refusals", OTHER_REFUSALS)):
   205	        lines.extend(["", "**{} — cold-gate path.**".format(title), "",
```

`render_policy` GENERATES the handback's policy block from `COLD_GATE_CODES`:
the prose in E3 is code output, not independently authored text.

## E3 — `docs/process/NIGHT_HANDBACK.md`: the install-close sentence and R1

Lines 57–62 (the definitions paragraph, quoted whole):

```
    57	A **listed install span** is a local-time interval from `run_night.INSTALL_SPANS`,
    58	resolved for its local date; an **epoch second** counts from 1970-01-01 00:00 UTC.
    59	`install_close_epoch(plan)` is the exclusive install cutoff, `t0 − 85 minutes`;
    60	`PLAN_MAX_AGE_S` is the night gate's 36-hour plan-age limit. A **dead-man** is
    61	the scheduled recovery job after planned completion. A **plist** is a launchd
    62	job file; **UNKNOWN** means a query cannot establish whether a job is loaded.
```

Line 59 says `t0 - 85 minutes`. Exhibit D §D3 shows the code deriving
`t0 - 600 s = t0 - 10 minutes`. The two disagree by 75 minutes; the code is at
`a90ab4e8` and the prose is at `a90ab4e8` as well.

Lines 78–84 (the generated cold-gate table's first rows):

```
    78	**Gate and driver refusals — cold-gate path.**
    79	
    80	| Exact cause | Why A172 grants no retry exception |
    81	|---|---|
    82	| `night_refused_agent_present` | Production census refusal, including a receipt at t0; never an idle arm event. |
    83	| `night_refused_not_quiet` | Machine quietness failed; load, power and thermal thresholds stay fixed. |
    84	| `night_refused_hid_idle` | User-input inactivity guard failed. |
```

Lines 132–138 (R1's operative bounds and the clearance definitions, quoted
contiguously so the judge can check for selective quotation):

```
   132	Unknown or mixed causes, any receipt refusal, and every capture, clock, custody, ledger or pre-registration guard stay on the cold-gate path. Known concurrent refusal evidence overrides an eligible arm cause. These dispositions preserve existing harvest, delivery and human-resolution remedies; they do not call a review into a live chain.
   133	
   134	R1's operative time bounds are `now < install_close_epoch(plan)` and plan age within `PLAN_MAX_AGE_S` (including the existing authored-to-t0 check), with at least 60 seconds between arm attempts. D-180's same-or-next-listed-span ceiling is subsumed by `install_close_epoch(plan)` and `PLAN_MAX_AGE_S`, because with whole-day install spans it could otherwise bind 15 minutes before install close. There is no attempt-count cap, separate notice-age limit, new window cadence or delay after a successful harvest.
   135	
   136	Every actual attempt sends a newly accepted notice and repeats the existing notice-to-publication lead: accepted email before publication, with no additional minimum interval. A notice is stale if its SHA-256 fingerprint (digest of the exact plan bytes) or reviewed head differs, a newer abort or NO exists, or it belongs to an earlier attempt. A new thread never clears an earlier NO. Waiting observations send no repeated email. Preserve each attempt in `$STAGE/arm-attempts/NNNNNN/` (a positive ordinal padded to at least six digits, without a count limit), created exclusively; never overwrite prior notice, candidate or failure evidence.
   137	
   138	`prerequisites_clear` covers census, watchdog, science, custody, no invocation and authorized observable stop/directive checks; `veto_clear` covers directive issues (`gh issue list --label directive`), `standdown.request`/STOP and any NO relayed into a readable channel. Record an unreadable notice thread as a limitation in the attempt directory; it is not a stop and neither clearance boolean requires reading it. Preserve every observed NO; each stops publication.
```

Line 142 (what a retry-class abort authorises today):

```
   142	A retry-class abort recorded by a prior activation authorises a successor's ordinary fresh-plan arm of the same class without a new cold gate; the predecessor's published plan directory, if any, stays untouched under the existing human-resolution path.
```

## E4 — the A212 lane as registered (primary trace, not a decision-log entry)

There is no decision-log entry for the fast-retry ruling. The nearest primary
record is the lane registration written by the activation that received the
remark, which quotes the owner verbatim and states explicitly what was and was
NOT ratified. `docs/process_traces/2026-09-15-activation-08ca8197/06-refusal-fast-retry-lane-registration.md`,
lines 1–12 and 28–40, quoted contiguously:

```
     1	# 06 — Registration of REFUSAL-FAST-RETRY-01 (2026-09-16 ~00:08 PDT, activation `08ca8197`)
     2	
     3	## Source
     4	
     5	At ~00:05 PDT the interactive session `b0ae8462` (Ed at the machine) relayed
     6	Ed's remark on the cost of a t0 refusal (about three hours per refusal),
     7	quoted by that session as verbatim:
     8	
     9	> "how have we not made this a lower cost to pay"
    10	
    11	Not a directive issue (`gh issue list --label directive` empty before this
    12	slice). Registered as relayed.
```

```
    28	## What was registered
    29	
    30	Kernel row `REFUSAL-FAST-RETRY-01`, rank 212, `p1_phase_gate`, lane `agent`,
    31	status `blocked` with hard start dependencies on `ARM-RETRY-CLASS-01` and
    32	`INSTALL-WINDOWS-MULTI-01`. Kernel 185 → 186 rows; `TASK_QUEUE.md`
    33	regenerated; `tests/test_gen_state.py` updated. Registration only; no code
    34	changed.
    35	
    36	Part (b) of the lane (treating a zero-capture machine-state refusal as a
    37	pre-authorized retry) is a process rule. Under rule 11 it is not this
    38	activation's or the lieutenant's to ratify: the row records it as waiting for
    39	Ed's ruling (or the cold gate's with Ed's sight), to be installed as a dated
    40	decision-log addendum plus NIGHT_HANDBACK / runbook §1.4a prose. Parts (a)
```

Why this trace rather than a contract or code file: the cure described at
lines 36–40 is explicitly NOT INSTALLED, so no code or contract states it. Its
exact words are the object of proposition 9, which asks whether a bind-expiry
refusal falls inside "the authorized successor-retry remedy" — and lines 36–40
say the remedy is not yet authorized. The judge should treat this as evidence
about the remedy's STATUS, not as authority for granting it.
