WRITE_SCOPE: ["docs/contracts/pack_night_go_receipt.md","docs/decision_log.md","docs/process_traces/2026-09-08-handoff-redo/85-d176-install-astra-report.md"]

# Seat brief — D-176 install part 3: §10 wire addendum ruling B1-B5, S1-S6, N1-N2 of the Opus refutation (gpt-6-astra, high)

HEAD = bfedd6fa (parts 1-2). Opus refutation at docs/process_traces/2026-09-08-handoff-redo/78-coldgate-packet-d169-stage3/15-opus-contract-refutation-go-receipt.md
(present in this worktree? if not, read it at the absolute path /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/78-coldgate-packet-d169-stage3/15-opus-contract-refutation-go-receipt.md).
MAGISTRATE RULING (interactive, 2026-09-08 ~11:00 PDT; within the cold gate's envelope; install verbatim as a
new §10 "Wire addendum (ruled 2026-09-08, second pass)" and propagate into the key tables, clause map and seat
scopes; keep the exact-key discipline):

B1 — the plan is the root of trust for C1/C5 and must carry the bindings. Define `joulewise.night_plan.v3` = the v2
exact-key set plus ONE exact-key sub-object `pack_night {pack_id, pack_sha256, attempt_ordinal (int ≥ 1),
authorization_record {path, sha256}, confirmation_record {path, sha256}}`, REQUIRED iff `receipt_class ==
TRANSACTION_PACK` and FORBIDDEN otherwise; v2 plans stay valid for the other classes. The plan is authored by
`write_night_plan` (extend it), validated by `NightPlan.from_mapping` (`joulewise/night_gate.py:106-121, :203` —
seat 2's scope), installed by `install_night_agent.sh` which already pins the plan path. The GO receipt gains
`plan_sha256` (sha256 of the plan file bytes the driver read) and the v3 consumption record's `go_receipt` block
gains `plan_sha256`; the consumer recomputes it from the plan path in the launch context and refuses on mismatch.
The authorization-swap attack is thereby refused: the plan names the record digest, the plan digest is in the GO
and in the consumption record, and rewriting the plan after arm is the D-127/D-175 arming procedure (magistrate,
email-then-arm), not an operator footgun (D-161).
B2 — consumption record versions: add a third key constant `CONSUMPTION_RECEIPT_KEYS_V2` (the current 20-key set,
`joulewise/arm_readiness.py:681-702`) and `CONSUMPTION_RECEIPT_KEYS` becomes the v3 set (22 keys: + `go_receipt`,
`step6_confirmation`). `_read_v2_consumption` (`:8975-8992`) is renamed/extended to accept v3 always, v2 ONLY when
`require_current_boot=False` (historical replay), refusing a v2 record on live replay with
`launch_go_receipt_missing`; the 8-key legacy branch is untouched. Seat 3's scope.
B3 — exception type: GO failures in `_consume_launch_capability` raise `LaunchLineageError` with the two registered
codes (`LAUNCH_LINEAGE_REASON_CODES`); `scripts/launch_window.py` catches `ArmReadinessError` and
`LaunchLineageError` at the same site and renders the same refusal JSON shape. Seat 3's scope names both files.
B4 — check ORDER in the consumer: (1) read bytes, recompute sha256; (2) parse JSON; (3) read `schema_version`; if it
equals the rehearsal receipt schema `joulewise.t0_unattended_rehearsal_receipt.v1` (`joulewise/t0_rehearsal.py:38`)
refuse `launch_go_receipt_invalid` with `detail = "class=<value of its class field>"` BEFORE exact-key validation;
(4) exact-key validation of `pack_night_go_receipt.v1`; (5) bindings. G7 artifact: the driver writes
`night/g7_refusal.json` = exact keys `{schema: "joulewise.g7_refusal_record.v1", presented_schema, presented_class,
refusal_code, detail, consumed_json_absent (bool), capture_absent (bool), epoch_s}` where "capture absent" means no
`chain.started` marker exists under the custody root. Seat 4's scope.
B5 — locators: the GO's `confirmation_record_sha256` becomes the object `confirmation_record {path, sha256}` and
`authorization` becomes `{path, sha256, purpose, attempt_id, claim_eligible}`; paths absolute inside the transaction
custody root (= the plan's `custody_root`); the consumer re-reads BOTH by path, recomputes sha256, and re-verifies
the copied fields against the parsed bytes.
S1 — the authenticated window id is `receipt["pack"]["window_id"]` of the ARM receipt (`arm_readiness.py:9748,
:9486`); name it wherever the rehearsal prefix rule reads a window id.
S2 — seat 2's scope includes `joulewise/night_gate.py:738-746`: the unconditional `night_refused_class_unbuilt` is
lifted ONLY for plans carrying a valid `pack_night` object, and C1-C5 are then evaluated (no `no_pack_by_design`).
S3 — GO conditions REUSE night_gate's condition shape `{condition_id, status, basis, evidence, measured}` with
`_CONDITION_IDS` ordering, `_STATUSES` vocabulary, no duplicates; for a pack night the GO receipt IS the night-gate
receipt (the driver writes one file); state this in §2 and §3.
S4 — "disjoint roots": a NEW frozen constant `PRODUCTION_CUSTODY_ROOTS` in `joulewise/arm_readiness.py` (the list
G6 consumes today via `bundle.production_roots`, `t0_rehearsal.py:779-787`, is derived from it — seat 2 makes G6
read the constant); the consumer refuses a `T0_REHEARSAL` purpose whose plan `measurement_root` or `custody_root`
lies under any production root (`launch_go_receipt_invalid`, detail `rehearsal_roots_not_disjoint`). Complete the
2×2 table: unprefixed id + T0_REHEARSAL → refuse (`rehearsal_purpose_on_production_id`); prefixed id + other
purpose → refuse; prefixed + T0_REHEARSAL + disjoint → accept; prefixed + T0_REHEARSAL + not disjoint → refuse.
S5 — `_lifecycle_receipt_path` (`arm_readiness.py:9796-9802`) reads v3 (seat 3's scope); a v2 record on live replay
→ `launch_go_receipt_missing`.
S6 — `t0_evidence` = exactly the file set returned by `author_arm_readiness_evidence_t0` (`receipt_paths`: the
fifteen ARM_ONLY receipts) plus the capture-step record files it inventories; the GO carries the array of
`{path, sha256}` (paths relative to the transaction custody root) AND `t0_evidence_set_sha256` = sha256 over the
canonical JSON of the sorted array; the consumer recomputes both and refuses on any mismatch or missing file.
N1 — `epoch_s` is `number` (float) everywhere; `status` ∈ `_STATUSES`; conditions ordered by `_CONDITION_IDS`, no
duplicates. N2 — the six/seven-key `go_receipt` block's constant is `GO_RECEIPT_REFERENCE_KEYS`.
Also define at first use: "the plan" (path, schema, authentication route per B1), `attempt_ordinal` persistence
(the driver persists it in the plan; replay reads the plan, never recomputes), "transaction custody root" (= plan
`custody_root`; relative evidence paths resolve against it), "capture" (= `chain.started`), "namespace" (define
before §7 uses it). Replace the three gesture clauses (§2:146-147 "authenticate … membership/evidence/condition
semantics", §3:171 "independently held launch context") with the concrete checks above.
Then update the seat scopes section so each seat's WRITE_SCOPE names every file:line this addendum touches, append a
dated line to the D-176 decision-log entry, update report 85. Acceptance: `python3 -m unittest
tests.test_docs_freshness` rc 0. No `git commit`; never the repository-wide suite; header < 8192 bytes; genre
implementation verdict keys.
