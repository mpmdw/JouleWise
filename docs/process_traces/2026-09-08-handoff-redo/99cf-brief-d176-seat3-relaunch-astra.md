WRITE_SCOPE: ["joulewise/arm_readiness.py","scripts/launch_window.py","docs/contracts/d078_reason_registry_amendment.md","tests/test_arm_readiness_schemas.py","tests/test_arm_readiness_lifecycle.py","tests/test_launch_window.py","docs/contracts/pack_night_go_receipt.md"]

# D-176 seat 3 — RELAUNCH with the three rulings (gpt-6-astra, HIGH, genre implementation)
Your intake run (report filed as trace 99ce) returned NEEDS_RULING F1–F3. RULINGS (magistrate, 2026-09-08):
R1 (F1, keywords): the CONTRACT §3 governs over the launch brief's wording. The callee takes SIX sentinel-required
   inputs for a TRANSACTION_PACK launch: the four §3 GO/plan keywords (`night_plan`, `go_receipt`,
   `authenticated_go_receipt`, `go_receipt_sha256`) PLUS the existing confirmation pair (`--step6-confirmation-table`
   and `--expected-confirmation-digest`, made REQUIRED per §10.1 F6/Opus F6). Every one defaults to the missing
   sentinel; omission of any refuses with its registered code. Non-pack classes keep their existing behaviour.
R2 (F2, replay plan locator): PERSIST the locator. `launch_consumption.v3` gains a `night_plan` object
   {`path`: absolute path inside the night custody root as pinned by the installer, `sha256`} (so the record grows by
   one key; state the new exact key count in the contract), written from the consumer's authenticated inputs at the
   O_EXCL write; `verify_consumed_launch` and the child read the plan bytes from that persisted path and refuse on
   digest mismatch against BOTH the record's `night_plan.sha256` and the GO's `plan_sha256`; live replay refuses if
   the path is outside the custody root. Install this as a dated "§10.2 seat-3 rulings (2026-09-08)" block in the
   contract, propagated to §3, the key tables and your §9 rows (edit only your own rows; seat 2 runs in parallel).
R3 (F3, baseline anchors): SUPERSEDED for runner-owned lanes. codex-run-v3 snapshots its own launch baseline and
   records head_start/head_end in the report envelope; BASELINE_MANIFEST/BASELINE_DIGEST are a bridge-protocol v1.1
   requirement the wrapper does not yet emit (follow-up BRIDGE-BASELINE-ANCHORS-01 is registered elsewhere). Do not
   block on them; proceed to writes.
Everything else in the original brief stands (repeated here for completeness): implement the §7.1 row "3 — consumer,
v3 consumption, replay and child" seams: R-8 registration of `launch_go_receipt_missing` / `launch_go_receipt_invalid`
BEFORE emission (registry amendment doc + code); `_consume_launch_capability` re-reads bytes, recomputes digests,
refuses on binding mismatch / wrong class / non-GO / any non-PASS condition / monotonic outside [issued, valid_until);
`launch_consumption.v3` with go_receipt{…}, step6_confirmation{…} and night_plan{…}; v2 to the legacy branch replaying
only with require_current_boot=False; the extended reader FORWARDS require_current_boot with the four call sites'
per-site values per §3/§10.1-F3; `verify_consumed_launch` re-reads GO bytes and refuses a live replay of a record
without go_receipt; the O_EXCL consumption write is the single linearization point; scripts/launch_window.py gains
REQUIRED `--night-plan` and `--go-receipt` (+ required confirmation flags for TRANSACTION_PACK) with omission-refusal
regressions; child v3 reader; shared JSON refusal handler. Every clause → regression with the §9 counterfactual
(forged receipt, replayed receipt, CLI-then-callee mutation, class relabeling, pre-registration drift,
caller-substituted plan, lineage reader hardcoding False on the live path, persisted plan path outside custody root).
Touch joulewise/arm_readiness.py everywhere the row names EXCEPT the constants area at ~:223 (seat 2's).
Acceptance (rc-gated to a log): tests.test_arm_readiness_schemas tests.test_arm_readiness_lifecycle
tests.test_launch_window tests.test_d078_reason_registry tests.test_docs_freshness; git diff --check; no commit;
header < 8192 bytes; report = per-clause map (clause → file:line → test → counterfactual).
