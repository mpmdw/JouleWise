## D-176 seat 4 — contract-lens refutation (`git diff e73e5439 9bc8861d`, HEAD `3032dd93`)

### Confirmations (the four things I was asked to verify)

**Pre-ARM admission is installed in the consumer as ruled.** `joulewise/arm_readiness.py:9925 _admit_pack_launch_go` runs plan bytes → GO bytes → digest (`:9938`) → exact 26-key shape (`:9943`) → `validate_pack_night_go_receipt` → `NightPlan.from_mapping` → plan class → **digest-verified** authorization purpose (via `_go_record:9794`, which checks the plan's pinned sha256) → `rehearsal_purpose_on_production_id`. It is called at `:10357` in `_consume_launch_capability`, **before** `_verify_arm_receipt` (`:10395`) and before every path/type check that touches an ARM path; and at `scripts/launch_window.py:109–120`, before `args.pack_root.resolve()`. I found **no path where an ARM read precedes admission**. `test_pre_arm_admission_rejects_rehearsal_go_and_authenticates_digest_first` deletes the ARM file, mocks `_verify_arm_receipt` and asserts `not_called` — the counterfactual bites. `launch_window.py` still parses eight flags (`argv[2:]` length 16 asserted at `tests/test_launch_window.py:2347`).

**Census-cure bytes are byte-preserved.** `git diff c16a2ac4 9bc8861d -- joulewise/arm_readiness.py` = 46 insertions, **0 deletions, 0 modifications**.

**§10 S4 2×2.** `_produce_pack_go` retains `_pack_rehearsal_roots(plan, arm, authorization["purpose"])` unchanged; the new producer test covers all four purpose×prefix cells at issuance using the ARM window id (S1), the consumer test covers the four-case table including the root collision. Matches §6/§10 S4.

**G5 / G7.** G5 validates `joulewise.pack_night_go_receipt.v1` and refuses D-149 outright (never grandfathered); C1/C3/C4/C5 counterfactuals genuinely bite with hashes rebound. G7's v1 artifact keys equal the ruling's list exactly; both presentations, first-refusal, locator, re-validation, and preservation of the completed rehearsal (writes confined to `<control>/night` after a freshness scan) are all installed. `_consume_launch_capability` is reached only from `launch_window.py:264` (pack-only), so **DIAGNOSTIC_NO_PACK / REHEARSAL_STUB / CAMPAIGN_TRANSACTION paths are not broken**; real rehearsal launches short-circuit because their plan authorization purpose is `T0_REHEARSAL`.

### Findings

1. **BLOCKER — the loader now makes every rehearsal bundle unloadable until a manual post-night command runs.** `scripts/rehearse_t0_unattended.py:29` adds `g7_control` to the closed `RECORD_NAMES`, enforced by the exact-census check at `:147`. Nothing automated emits it: `produce_g7_control` is a separate `run_night.py g7-control` invocation that additionally requires a fresh sibling control custody holding a *production* plan, a real production pack on disk, and a `CAMPAIGN_TRANSACTION` authorization. §6 names the command but installs **no ordering obligation** saying the bundle cannot load before it. With rehearsal-20260909 armed, this is an operational stop. Fix: an explicit §6/§10.5 sequencing clause plus the runbook step.

2. **BLOCKER — no test composes an overall PASS.** Every `overall_verdict` assertion in `tests/test_t0_rehearsal.py` (`:649,:662,:679,:837`) is now FAIL. `FixtureBuilder` keeps a legacy `d149_go`, so G5 hard-fails *every* loader-built bundle; `PackGoReplayTests` constructs `EvidenceBundle` by hand and bypasses `load_evidence_bundle`. `_assert_single_failure:651` was relaxed to expect `{gate_id, "G5"}`. Net: **the G5 PASS path through the real loader, and the ten-gate PASS composition, are unexercised** — first evidence would be the live night.

3. **SHOULD-FIX — detail aliasing defeats bytes-only G7 acceptance.** `_go_invalid("receipt_class")` is raised at `arm_readiness.py:9944` (presented GO's key shape) *and* `:9951` (control plan is not `TRANSACTION_PACK`). `validate_g7_control` accepts detail `receipt_class` for the `rehearsal_receipt` presentation, so a control built on a non-pack plan produces a byte-identical, PASSing artifact. The producer's own guard cannot help — ruling item 8 requires acceptance from the artifact bytes only. Fix: distinct details (`go_receipt.receipt_class` / `night_plan.receipt_class`), pinned in §6, §10.5 and `validate_g7_control`.

4. **SHOULD-FIX — §9 rows violate the contract's own pin rule.** Line 617: "Each seat must pin final production/test lines in §9 on return." The four rewritten rows (S1 `:839`, S4 `:842`, B4 `:843`, N1) and §7.1 row 4 (`:626`) carry `file::symbol` with **no line numbers**, unlike every other row and unlike the 166 pins re-verified in `93870527`.

5. **SHOULD-FIX — rewritten rows dropped citations their falsifier columns still claim.** S4 still asserts "wrong-name custody… stale manifest census passes" but no longer cites `tests/test_run_night.py:2197`, `tests/test_rehearse_t0_unattended.py:21`, or `:127` (all still present). N1 dropped `test_gate_checks_authorization_fields_and_confirmation_bytes`, its only pin for "accepts a string confirmation epoch".

6. **SHOULD-FIX — the C2 counterfactual does not bite.** `_authenticate_go_t0_evidence` is mocked on the G5 PASS path; `test_g5_requires_arm_semantic_replay_and_real_t0_inventory` only restores the real authenticator and shows the synthetic fixture fails. No test mutates, omits or substitutes a T-0 evidence file. §9 N1/B4's "C2 ARM/T0" claim holds for the ARM half only.

7. **NIT.** Debug `print("G7_ARTIFACT_JSON=…")` left in `tests/test_launch_window.py`; the comment explaining that non-pack classes never enter the pack launcher was deleted with the moved block in `launch_window.py`.

All five seat test modules pass (exit 0).

**Verdict: LAND-WITH-FIXES** — findings 1–3 must close before rehearsal-20260909 is armed; 4–6 before the contract is treated as pinned.
