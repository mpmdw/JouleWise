# Cold-gate refutation — contract lens (Opus 5), D-169 stage 3

Read-only, at the working tree of 2026-09-08. Every cite below was opened this session with the
command shown. Paired with the cold Fable judge on packet
`78-coldgate-packet-d169-stage3/00-PACKET.md`.

## Findings

**F1 — The D-149 receipt schema of record binds nothing at all.**
`python3 -c "import sys;sys.path.insert(0,'.');from joulewise import t0_rehearsal as t;print(t.D149_SCHEMA, sorted(t._D149_KEYS), sorted(t._D149_CONDITION_KEYS))"`
→ `joulewise.t0_unattended_d149_go_receipt.v1 ['conditions','schema_version','verdict'] ['condition_id','evidence','status']`
(`joulewise/t0_rehearsal.py:48,86,87`), enforced exact at `:719`. There is no pack digest, ARM identity,
plan id, measurement head, boot session, window id, or validity field anywhere in the schema. A receipt
in the schema of record is **replayable against any pack, plan, or window by construction**. The consult
never rules this; it demotes it to an open question ("Which versioned schema is authoritative?",
exhibit A, cold-gate skeleton Q2). Packet decision 1 therefore cannot be UPHELD as written — the ruling
must itself specify the bound schema, or stage 3 begins with the forgery hole open.

**F2 — Installing those bindings mechanically breaks G5, and the consult's schema clause does not cover it.**
Because `:719` tests `set(value) != _D149_KEYS`, a receipt carrying the bindings F1 demands **FAILS**
`evaluate_g5`. So the rehearsal that qualifies the design cannot pass with the receipt the design
requires. The consult's only schema instruction is "Preserve current diagnostic/stub schemas; their
exact-key contracts should not change silently" (exhibit A, Desk phase) — this is not a silent change,
it is a *mandatory* one, and leaving v1 grandfathered keeps the unbound receipt admissible at G5.

**F3 — No D-149 producer exists anywhere in code.**
`grep -rln "t0_unattended_d149_go_receipt" .` → `joulewise/t0_rehearsal.py` and six trace documents; no
producer, no validator, no test. The consult's sentence "The T-0 clock producer itself is substantially
implemented. Do not rebuild it" is true only of `author_arm_readiness_evidence_t0()`
(`joulewise/arm_readiness_evidence_t0.py:2245`, fifteen ARM_ONLY evidence receipts) — but it sits inside
the R1 table row headed *"Evidence-backed D-149 GO production"*, where a reader takes it as saying the GO
producer is substantially built. Answering the packet's decision-4 sub-question exactly: the ARM T-0
**evidence** author is substantially implemented; the **D-149 GO producer** is zero lines; the
rehearsal-bundle producers (execution/fd-0, HID witness, lifecycle, falsifier, positive control) are zero
lines.

**F4 — Binding the GO into the consumption record is a v3 schema change the consult never names.**
`validate_consumption_receipt` is exact-key (`joulewise/arm_readiness.py:2598`); the probe prints twenty
keys with no authorization field, schema `joulewise.arm_readiness_launch_consumption.v2`. R2 item 3
("Record its identity/digest in the atomic consumption record") is therefore: a v3 schema, a legacy
branch mirroring `:2593-2597`, **and** an extension of `verify_consumed_launch`'s `expected_identity`
dict (`:9483-9491`) — otherwise replay re-authenticates pack, ARM, head, manifest, env, chain and argv
while never re-authenticating the authorization, which is the one thing stage 3 adds.

**F5 — The reuse of the ARM consumption pattern is faithful; UPHOLD it.**
`_consume_launch_capability` re-reads the receipt from disk (`arm_readiness.py:9663`) and refuses if the
CLI-assembled context differs ("authenticated arm receipt context changed before consumption",
`:9673-9677`); the sole linearization point is the no-clobber `_exclusive_write` mapping collision →
`readiness_record_consumed` (`:9771-9780`). The consult's "authenticate inside the callee, not at the
CLI" and "do not add a second GO-consumed lock" are exactly this pattern; a second lock would create a
two-phase crash window with no one-shot gain.

**F6 — The confirmation pair is NOT currently required by the launcher; R3 misstates the baseline, and the
consult's fix leaves a fail-open.**
`sed -n '46,57p' scripts/launch_window.py` → `--step6-confirmation-table` and
`--expected-confirmation-digest` are **optional** (no `required=True`). They are forwarded as `None` to
`_verify_arm_receipt` (`:126-131`), `_consume_launch_capability` (`:247`), `verify_consumed_launch`
(`:255`) and lifecycle start (`:278`). The digest is demanded only when a digest-conditional allowlist
path is in the R1 changed set (`_require_confirmed_conditional_path`, `arm_readiness.py:4643-4698`,
reached from `validate_r1_evidence_lifecycle` `:4779-4790` for members of
`R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS`, `:2883`). So R3's "the current launcher requires the
confirmation pair during ARM verification (`:126`)" is false; it *forwards* it and enforcement is
contingent. Consequence the consult misses: giving hC a mode-0600 custody home does not make it
mandatory. An unattended pack night whose changed set contains no conditional path launches with **no
confirmation at all** — a fail-open reached by doing nothing.

**F7 — The G2-b bootstrap conflict is real and the consult's split is the right shape.**
`/tasks/V5-TRANSACTION-GO-01/acceptance` in `docs/process/state_kernel.json` requires "Ed reviews the
preserved G2-b verdict, bracket binding, desk-check result, and exact finalizer-refusal result" — the
C1 authority the stage-1 R-4 table assigns to every `TRANSACTION_PACK` night (exhibit C §R-4) is
evidence-dependent on G2-b having already run. D-171 item 3 (`docs/decision_log.md:10621`ff) moves the
*authority* to the magistrate's cold-gate-adjudicated gate; it does not dissolve the evidence
dependency. The consult's answer keeps G2-b in `TRANSACTION_PACK` with full C2–C5 and varies only the
C1 *artifact* — so no class GOes without a complete C1–C5 census, `REHEARSAL_STUB` still can never carry
GO (exhibit C §R-4), and no `no_pack_by_design` basis reaches a pack. Class honesty survives.

**F8 — R6 as written is itself a ruled-not-installed candidate.**
`grep -n "REHEARSAL_PRODUCER_WORK_ORDER" joulewise/t0_rehearsal.py` → no match, while
`/tasks/T0-REHEARSAL-PRODUCERS-01/acceptance` still requires "every entry of
REHEARSAL_PRODUCER_WORK_ORDER in joulewise/t0_rehearsal.py is either discharged … or struck". The
consult flags the stale pointer but prescribes only "install an enumerated checklist in a ruled home or
replace the stale pointer explicitly" — an unbound disjunction with no named file, symbol, or row edit.
`D169-STAGE3-01` already exists (status `blocked`), so the packet's "rows to create" framing is stale by
one row.

**F9 — G1's stdin gap confirmed.** `scripts/run_night.py:424-430`: `subprocess.Popen(command…,
stdout=stdout, stderr=stderr, env=environment, start_new_session=True)` — no `stdin=`; the chain
inherits the driver's stdin. The consult's G1 note is accurate.

## Per-decision verdicts

**1. Receipt binding — AMEND.** The consult's placement (inside `_consume_launch_capability`, replayed
through `verify_consumed_launch`, single ARM lock) is faithful (F5): UPHOLD that half. The binding half
is unruled (F1) and mechanically incomplete (F2, F4). Add verbatim:

> The authoritative GO receipt schema is `joulewise.t0_unattended_d149_go_receipt.v2`, whose exact key
> set adds `pack_id`, `pack_sha256`, `arm_receipt` (`receipt_id`/`path`/`sha256`), `plan_id`,
> `window_id`, `boot_session_id`, `head_commit`, `measurement_root`, `measurement_head`,
> `t0_evidence_set_sha256`, `issued_at_monotonic_ns` and `valid_until_monotonic_ns`. In the same change,
> `D149_SCHEMA`, `_D149_KEYS`, `_D149_CONDITION_KEYS` and `evaluate_g5`
> (`joulewise/t0_rehearsal.py:48,86,87,710-739`) are retargeted to v2 and v1 is REFUSED, not
> grandfathered. The consumption record becomes
> `joulewise.arm_readiness_launch_consumption.v3` carrying `go_receipt` (`receipt_id`/`path`/`sha256`),
> with `CONSUMPTION_RECEIPT_KEYS`, the legacy branch at `arm_readiness.py:2593-2597`, and
> `verify_consumed_launch`'s `expected_identity` (`:9483-9491`) extended together; a v2 consumption
> replays as before and can never satisfy a v3 launch.

**2. G2-b authorization — UPHOLD** (F7), with one added sentence: *"The G2-b C1 artifact is a magistrate
authorization under D-171 item 3 naming the exact pack, attempt, permitted chain and
`claim_eligible: false`; it is not `V5-TRANSACTION-GO-01` and does not discharge it."*

**3. Confirmation custody — AMEND.** Adopt the mode-0600 create-once record and the prohibition on
deriving hC from the table present at T-0, but add: *"`--step6-confirmation-table` and
`--expected-confirmation-digest` become REQUIRED whenever `--arm-receipt`'s pack is a
`TRANSACTION_PACK` night (`scripts/launch_window.py:46-57`), with a regression proving refusal on
omission; the driver reads the record and passes both, and the child's supply line is the named
`window.env` allowlist entry, not an implicit inheritance."* Without this the custody route is decided
and the fence still open (F6). Inheritance across a magistrate relaunch is satisfied because the record
lives in transaction custody, not in session state — no unattended session ever holds the digest as
authority.

**4. Rehearsal obligations — AMEND.** The consult's closure list (G1–G10 all PASS, no UNRULED counted as
success, dedicated identity/custody/ledger/runs/backups, Ed-owned physical positive control, separate
production-entry rejection of a valid rehearsal receipt) is correct and matches `evaluate_g6`/`g7`
(`t0_rehearsal.py:749-793`) and coldgate-d1's morning-before case (`coldgate-d1-RULING.md:115-121`).
G2-a discharges **none** of it — UPHELD. Amend the R1 sentence to read: *"the ARM T-0 evidence author
(`arm_readiness_evidence_t0.py:2245`) is substantially implemented; the D-149 GO producer and every
rehearsal-bundle producer are unwritten (F3)."*

**5. Kernel installation — AMEND.** As written it permits ruled-not-installed (F8). Require: *"the ruling
enumerates, per clause, the file, symbol and kernel JSON pointer it installs at; `T0-REHEARSAL-
PRODUCERS-01` acceptance is edited to strike `REHEARSAL_PRODUCER_WORK_ORDER` and name the ten-gate table
instead; `S9-06-WINDOW-T0-GO-RECEIPT-GATE-01` is retargeted to close against the same implementation as
`UNATTENDED-LAUNCH-01`; `D169-STAGE3-01` (already present, `blocked`) is retargeted, not created; and
`T0-LIVENESS-BOUND-EMPIRICAL-01` is explicitly recorded as a retained limitation, not a launch gate."*

**6. Smaller than sound? — Not overall; sound with amendments 1 and 3.**
*Strongest reason to REJECT:* the design's central artifact is unspecified and, in the only schema that
exists, binds nothing — `_D149_KEYS = {"schema_version","verdict","conditions"}`
(`joulewise/t0_rehearsal.py:86`), enforced at `:719`. A design whose GO receipt cannot name its pack is
not a launch authorization; it is a boolean.
*Strongest reason to UPHOLD:* the enforcement point it chooses is already the correct one — the callee
re-reads and re-verifies the receipt bytes and refuses on drift (`arm_readiness.py:9663-9677`) and the
atomic no-clobber write is the single-use linearization point (`:9771-9780`). Building on that, rather
than a new lock, is the smallest addition that is genuinely sound.
