# G5 enumeration — D-135, D-136, D-137, D-138, D-139, D-140, D-141

Method note: every `file:line` below was opened and read (sed/grep-with-context),
not inferred from a grep hit. Producer-side callers were checked with
`grep -rn <symbol> joulewise scripts configs tests`.

---

### D-135 · clause 1
- clause (verbatim): "The self-imposed conservative site budgets — the 1,000,000-byte measured capsule budget, per-page/per-shard byte budgets (e.g. the 30,000-byte record-page shard), and pagination-margin assertions — are ADVISORY: build tooling and tests may WARN on them but must not fail a build, a test suite, or a PR gate."
- source: docs/decision_log.md:8673-8678
- status: A
- evidence: scripts/pack_capsule.py:114-115 — `def warn_advisory_budget(message)` prints `ADVISORY BUDGET EXCEEDED (D-135): …` to stderr and returns; it never raises.
- evidence: scripts/pack_capsule.py:627-632 — pagination-margin overrun calls `warn_advisory_budget` under the comment `# D-135: pagination margins report pressure without gating the pack.`
- evidence: scripts/pack_capsule.py:633-639 — per-page/per-shard `MAX_SHARD_BASE64_BYTES = 30_000` overrun also warns (`# D-135: per-page and per-shard byte budgets are advisory only.`).
- evidence: scripts/pack_capsule.py:936-947 — measured artifact over `LAKEBED_MEASURED_ARTIFACT_BUDGET_BYTES` (1_000_000, line 49) warns and returns the measurement.
- evidence: scripts/build_site.py:204-205 — the site builder carries the same `warn_advisory_budget` helper, distinct from `fail()` at :200-201 which raises `SiteBuildError`.
- producer: scripts/pack_capsule.py (`pack_capsule`) and scripts/build_site.py — both write the site/capsule bytes and both warn rather than raise on advisory budgets.
- transaction_relevant: no — site publication is outside the `_v4` mint/arm/window/consumption path.

### D-135 · clause 2
- clause (verbatim): "The ONLY site-size condition that may fail anything is the physical Lakebed platform cap (1,048,576 bytes measured by the real validator), because exceeding it makes the deploy itself fail."
- source: docs/decision_log.md:8678-8681
- status: A
- evidence: scripts/pack_capsule.py:45 — `LAKEBED_ARTIFACT_CAP_BYTES = 1_048_576`.
- evidence: scripts/pack_capsule.py:929-935 — `if measured > LAKEBED_ARTIFACT_CAP_BYTES: raise CapsulePackError(… "is over the 1 MiB cap by …")` — the only size-driven raise in the postcondition.
- evidence: scripts/build_site.py:42 — `LAKEBED_PLATFORM_CAP_BYTES = 1_048_576`.
- producer: scripts/pack_capsule.py `enforce_lakebed_artifact_postcondition` (the measured branch at :920-947).
- transaction_relevant: no — site lane.

### D-135 · clause 3
- clause (verbatim): "Content decisions (what the decision log or council log records) are never to be trimmed, split, or archived to satisfy an advisory budget."
- source: docs/decision_log.md:8681-8683
- status: C
- evidence: greps run — `grep -rn "archive\|trim" scripts/build_site.py scripts/pack_capsule.py` finds no content-dropping path keyed to a budget; the only decision-log-shaped response to budget pressure is `warn_advisory_budget` (scripts/pack_capsule.py:627-632).
- evidence: TASK_QUEUE.md:536 — `SITE-ROADMAP-PAGINATE-01` still describes shard-budget-driven pagination work, but it is an open queue item (D-136 cl.4 keeps it frozen), not an installed trimmer.
- producer: none found — this is a content-policy prohibition with no artifact to enforce it; nothing currently violates it either.
- transaction_relevant: no.
- note: AMBIGUOUS in the weak sense that a prohibition on a behaviour nothing implements has no positive artifact to point at. Recorded C because no test or check would catch a future budget-driven content trim.

### D-135 · clause 4
- clause (verbatim): "SITE-CAPSULE-BUDGET-01 is SUPERSEDED by this ruling"
- source: docs/decision_log.md:8683-8685
- status: A
- evidence: TASK_QUEUE.md:268 — heading reads `## SITE-CAPSULE-BUDGET-01 (recorded 2026-08-11, T4-late) — SUPERSEDED BY D-135 (Ed: budgets are ADVISORY; only the physical 1,048,576-byte Lakebed cap may fail anything; implementation of warn-only behavior is OWED, see D-135)`.
- producer: TASK_QUEUE.md (the queue is the artifact that carries item status).
- transaction_relevant: no.

---

### D-136 · clause 1
- clause (verbatim): "No session spends tokens on Lakebed/capsule size, packing, deploy failures, or site-chain diagnosis. A red site-chain result is not a finding, not a follow-up, and never appears in a merge gate, run report priority list, or RUN_STATE watch item."
- source: docs/decision_log.md:8695-8699
- status: A
- evidence: .github/workflows/ci.yml:417-418 — `# The site observatory's publication chain and all site-lane tests / live in .github/workflows/site.yml — a separate failure domain that …`; `grep -in "site\|capsule\|lakebed" .github/workflows/ci.yml` returns only that comment plus one unrelated "site-packages" line at :386. The merge gate therefore carries zero site machinery.
- evidence: RUN_STATE.md:1723 — `re-audit ACCEPT; site-chain red is IRRELEVANT per **D-136**` — the watch-item half is honoured in the live run state.
- producer: .github/workflows/ci.yml (the merge gate) — it cannot go red on the site chain because it contains no site step.
- transaction_relevant: no.
- note: the "no session spends tokens" half is a process/attention rule with no mechanical enforcement; the enforceable half (merge gate / watch item) is installed.

### D-136 · clause 2
- clause (verbatim): "The `site` workflow triggers on `workflow_dispatch` only — never on push or pull_request. Site publication happens if and when a human chooses to run it."
- source: docs/decision_log.md:8700-8702
- status: A
- evidence: .github/workflows/site.yml:9-10 — the entire `on:` block is `on:` / `  workflow_dispatch:` with no `push:` or `pull_request:` key.
- evidence: .github/workflows/site.yml:1-6 — header comment names D-136 as the authority for exactly this shape.
- producer: .github/workflows/site.yml — the workflow file is the trigger definition; GitHub refuses to start it on push because no push trigger exists.
- transaction_relevant: no.

### D-136 · clause 3
- clause (verbatim): "The 2026-08-12 physical-cap overrun on PR #136's branch is explicitly NOT to be diagnosed or fixed (the in-flight diagnosis was killed on this ruling)."
- source: docs/decision_log.md:8705-8707
- status: C
- evidence: greps run — `grep -rn "D-136" --exclude-dir=.git .` over the tree finds only decision_log.md, RUN_STATE.md:1633/1670/1723, docs/council_log.md, docs/run_reports/2026-08-12-t5-window-session.md, and the site.yml header. No queue item, checklist row, or test encodes this one-time prohibition.
- producer: none found — a one-time historical instruction, discharged at ruling time.
- transaction_relevant: no.
- note: not an implementation clause in the brief's sense (a one-off stop order, not a standing artifact requirement). Recorded C for completeness.

### D-136 · clause 4
- clause (verbatim): "Open SITE-* queue items and the D-135 advisory-budget machinery stay as they are (merged or in-flight work is not reverted), but no new site work is minted."
- source: docs/decision_log.md:8707-8709
- status: A
- evidence: TASK_QUEUE.md:155 (SITE-02, closed), :158 (SITE-01, closed), :268 (SITE-CAPSULE-BUDGET-01 superseded), :536 (SITE-ROADMAP-PAGINATE-01, still open, untouched) — the SITE-* rows are all present and unrevised.
- evidence: scripts/pack_capsule.py:114-115 and :627-639 — the D-135 advisory machinery is still in place, matching "stay as they are".
- producer: TASK_QUEUE.md.
- transaction_relevant: no.

---

### D-137 · clause 1
- clause (verbatim): "Every v1 arm-readiness arm receipt and generic evidence receipt that carries `valid_until_monotonic_ns` also carries the required, derived `boot_session_id`."
- source: docs/decision_log.md:8787-8790
- status: A
- evidence: joulewise/arm_readiness.py:434-435, :469-470, :495-496 — three receipt key tuples each list `"boot_session_id"` immediately followed by `"valid_until_monotonic_ns"` (exact-key sets, so absence is a schema refusal).
- evidence: joulewise/arm_readiness.py:2427-2430 — `_require_boot_session_id(receipt["boot_session_id"], "arm receipt.boot_session_id")` then the monotonic check, in the arm-receipt validator.
- evidence: joulewise/arm_readiness.py:2131-2141 — same pair enforced for the generic evidence receipt.
- evidence: joulewise/arm_readiness.py:7745-7746 — the arm-receipt MINT writes `"boot_session_id": boot_session_id, "valid_until_monotonic_ns": valid_until` into the receipt dict.
- evidence (test): tests/test_arm_readiness_lifecycle.py:872-874 — asserts `readiness_record_expired` with `"prior boot session"` in the message.
- producer: joulewise/arm_readiness.py `issue_arm_receipt` path (:7589 derives, :7745 writes).
- transaction_relevant: yes — arm/arm-readiness receipts gate the measurement window.

### D-137 · clause 2
- clause (verbatim): "The value is machine-derived and is never supplied by an operator, API argument, or command-line option."
- source: docs/decision_log.md:8789-8791
- status: A
- evidence: joulewise/arm_readiness.py:1195-1225 — `_current_boot_session_id()` shells `/usr/sbin/sysctl -n kern.bootsessionuuid` and fails closed with `readiness_io_error` on any failure; there is no parameter.
- evidence: joulewise/arm_readiness.py:7589 — the mint calls `boot_session_id = _current_boot_session_id()` with no argument; the same pattern at :6540, :6706, :6942.
- evidence: `grep -rn "boot.session" scripts/*.py` — the only script touch points are scripts/capture_t0_step.py:269-271 (`return readiness._current_boot_session_id()`) and :486; no argparse option anywhere sets it.
- producer: joulewise/arm_readiness.py, scripts/capture_t0_step.py — both derive, neither accepts.
- transaction_relevant: yes.

### D-137 · clause 3
- clause (verbatim): "Verification and atomic consumption compare the receipt's boot session with the current boot session; a mismatch refuses closed as `readiness_record_expired`. The monotonic expiry is therefore never interpreted across a reboot."
- source: docs/decision_log.md:8791-8794
- status: A
- evidence (verify): joulewise/arm_readiness.py:8032-8034 — `if receipt["boot_session_id"] != _current_boot_session_id(): raise ArmReadinessError("readiness_record_expired", "arm receipt belongs to a prior boot session")`.
- evidence (consumption): joulewise/arm_readiness.py:8668-8675 — the consumption path recomputes `current_boot` and refuses on mismatch before checking `valid_until_monotonic_ns`.
- evidence (launch lifecycle): joulewise/arm_readiness.py:9229-9234 — `if current_boot != consumption["boot_session_id"]: raise LaunchLineageError("launch_binding_mismatch", "launch lifecycle crossed a boot boundary")`.
- evidence (evidence items): joulewise/arm_readiness.py:5514-5520 and :5738-5744 — `readiness_record_expired`, "evidence item/receipt belongs to a prior boot session".
- evidence (test): tests/test_arm_readiness.py:1584 and tests/test_arm_readiness_lifecycle.py:2452, :2502 — assert `readiness_record_expired`.
- producer: joulewise/arm_readiness.py — the same module both mints and refuses.
- transaction_relevant: yes.

---

### D-138 · clause 1
- clause (verbatim): "Any change to a file in the issued D-079 acceptance artifact's `estimator_code_sha256` pin set (`joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`, `joulewise/reduce.py`) deliberately stales the issued artifact"
- source: docs/decision_log.md:9964-9969
- status: A
- evidence: joulewise/calibration_bracketing.py:180-185 — `ESTIMATOR_CODE_PATHS` is exactly those four paths.
- evidence: joulewise/calibration_bracketing.py:387-400 — `_current_estimator_code_sha256()` hashes those four files from the live checkout.
- evidence: joulewise/calibration_bracketing.py:1734-1740 — `if protocol_sha256(PROTOCOL_ID) != prospective.get("protocol_sha256") or _current_estimator_code_sha256() != dict(prospective["estimator_code_sha256"]): observed_triggers.append("protocol_or_estimator_byte_change")` — a live byte change stales the artifact at evaluation.
- evidence: scripts/validate_powermetrics_fiducial.py:389-390 — the same comparison on the production validation path.
- producer: joulewise/calibration_bracketing.py (evaluation writes the observed-trigger list into the acceptance evaluation).
- transaction_relevant: yes — the D-079 acceptance artifact is a claim-edge input to the transaction.

### D-138 · clause 2
- clause (verbatim): "the canonical suite's authenticated-staleness fan-out is a LIVE INVARIANT (the suite proves the issued artifact matches real bytes), and re-keying those tests to fixtures to make such a branch mergeable is FORBIDDEN — it would delete the invariant that catches accidental estimator drift."
- source: docs/decision_log.md:9969-9973
- status: A (with a fragility note — read it)
- evidence: tests/test_powermetrics_fiducial.py:1571-1576 — `# The artifact's own estimator pins are the live ones: no isolation patch, so this also proves the staleness guard is genuinely cured.` followed by `self.assertEqual(validation_script._current_estimator_code_sha256(), dict(artifact["prospective_rederivation"]["estimator_code_sha256"]))` against the ISSUED artifact `d079_calibration_acceptance_v2_n17_r6` (:1563).
- evidence (the permitted, fixture-only insulation): tests/test_calibration_bracketing.py:215-246 — an explicit comment block stating the genesis FIXTURE's pins are re-keyed in memory only, with `_checkout_estimator_code_sha256()` (:257-264) digesting the real files "unpatchably" and `_SYNTHETIC_ESTIMATOR_CODE_SHA256` (:247-255) reserved for tests whose SUBJECT is a staleness trigger.
- producer: none — this is a suite-side invariant; the "producer" of drift is any edit to the four files, and the live assertion is what refuses it.
- transaction_relevant: yes — it is the guard on the acceptance artifact the transaction re-issues.
- note: FRAGILITY. The whole live invariant now rests on ONE unpatched assertion (tests/test_powermetrics_fiducial.py:1573-1576). Everything else in the estimator-pin test surface has been insulated from the tree by design (tests/test_calibration_bracketing.py:227-255). Deleting or patching that single assertion would silently delete the invariant D-138 declared undeletable, and no other test would go red. Worth a named regression/comment lock; not a defect today.

### D-138 · clause 3
- clause (verbatim): "such branches complete their C-028 gauntlet normally but are MERGE-STAGED: they merge ONLY inside the atomic Phase-2 successor re-freeze transaction that re-issues the acceptance artifact and every dependent pin"
- source: docs/decision_log.md:9975-9979
- status: B
- evidence (where it IS recorded): docs/process/phase2-transaction-runsheet.md:57-63 — step 1 names "the D-138 moment: the canonical suite's acceptance-staleness fan-out APPEARS here and is cured at step 3 — the two steps land in one push window, never separately CI-gated".
- evidence (where it IS recorded): TASK_QUEUE.md:590 and docs/process/state_kernel.json:4077 — WO-DETECT-PULSES-BUDGET carries `MERGE-STAGED for the atomic re-freeze (D-138)`.
- evidence (missing producer-side check): `grep -rn "D-138" docs/process docs/process_traces/2026-08-22-t20/real-transaction-runbook.md docs/phase_2 RUN_STATE.md TASK_QUEUE.md` returns ZERO hits in `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md` — the live `_v4` runbook, which superseded the `_v2`-era runsheet, never mentions D-138 or merge-staging.
- evidence (what the only mechanical guard actually enforces): tests/test_powermetrics_fiducial.py:1573-1576 goes red for a branch that edits a pinned file without re-issuing — that enforces "cannot land WITHOUT the reissue", NOT "must land INSIDE the atomic re-freeze". A branch that carried both the edit and a reissue would pass CI and could merge outside the transaction.
- producer: git merge / the merge gate — no gate, hook, or CI job consults the D-138 staging rule. `.github/workflows/ci.yml` has no such step.
- transaction_relevant: yes — it governs what may enter the transaction branch and when.
- note: the rule's only live doc home is `docs/process/phase2-transaction-runsheet.md`, which is itself stale (it is written against `_v2` pack IDs and `freeze-0002`; the live family is `_v4`/`freeze-0004`). An operator following the current `_v4` runbook would never encounter D-138.

### D-138 · clause 4
- clause (verbatim): "Follow-on work that must touch the same pinned files RIDES THE SAME BRANCH rather than opening a second staleness event on main (the inheritance corollary; the flake fix is the precedent)."
- source: docs/decision_log.md:9979-9982
- status: C
- evidence: greps run — `grep -rn "inheritance corollary" --exclude-dir=.git .` finds it only in docs/decision_log.md (index row :163 and body :8817, :9979). No script, hook, CI job, or checklist row implements branch-riding.
- producer: none found.
- transaction_relevant: yes — same class as clause 3 (governs the transaction branch's contents).

### D-138 · clause 5
- clause (verbatim): "The re-issue and pin update remain lead-owned inside the re-freeze; tests may re-key only private synthetic fixtures."
- source: docs/decision_log.md:9982-9983
- status: A
- evidence: tests/test_calibration_bracketing.py:247-255 — `_SYNTHETIC_ESTIMATOR_CODE_SHA256` is built from `hashlib.sha256(f"hermetic-estimator-pin::{relative}".encode())`, i.e. a private synthetic value bound to nothing in the tree.
- evidence: tests/test_calibration_bracketing.py:245-246 — "The fixture bytes, the fixture sha256 pin, and the checked-in artifacts are untouched by any of this; the re-key is in-memory only."
- producer: the test module itself; the issued artifact bytes under `configs/calibration/` are not modified by any test.
- transaction_relevant: yes.

### D-138 impl note (2026-08-17) · clause 6
- clause (verbatim): "Every output is conspicuously marked `\"candidate_not_issued\": true`. The production exact-byte acceptance loader refuses those marked bytes"
- source: docs/decision_log.md:9997-9999
- status: A
- evidence: scripts/reissue_calibration_acceptance.py:44 — `CANDIDATE_MARKER = "candidate_not_issued"`; :5 — module docstring "every output carries ``candidate_not_issued: true`` and remains inadmissible".
- evidence: scripts/reissue_calibration_acceptance.py:578-581 — `predecessor = load_calibration_acceptance_bound(args.predecessor); if predecessor is None or predecessor.get(CANDIDATE_MARKER) is True: print("VERDICT=STOP reason=predecessor_not_authenticated_issued_artifact"); return CORPUS_AUTHENTICATION_FAILURE_EXIT`.
- evidence: joulewise/calibration_bracketing.py:689-700 + :703-707 — `load_calibration_acceptance_bound` routes through `read_authentication_input(..., grammar="json")` and `_acceptance_bound_from_authenticated_bytes`, which "Parse[s] acceptance bytes only when their role-indexed pin authenticates" — a marker byte changes the digest, so the pin refuses.
- evidence (test): tests/test_reissue_calibration_acceptance.py:270, :281 — asserts the candidate carries the marker.
- producer: scripts/reissue_calibration_acceptance.py `write_candidate_artifact`.
- transaction_relevant: yes — the acceptance re-issue rides the transaction.

### D-138 impl note (2026-08-17) · clause 7
- clause (verbatim): "The F3 stop rule is executable: a member-set, threshold, or any other non-pin/science-facing delta prints `VERDICT=STOP` and returns a nonzero status; only a pure protocol/estimator-pin delta prints `VERDICT=PROCEED`."
- source: docs/decision_log.md:10002-10005
- status: A
- evidence: scripts/reissue_calibration_acceptance.py:546-549 — `if report["verdict"] == "STOP": print("VERDICT=STOP reasons=" + …) else: print("VERDICT=PROCEED reason=only_code_or_protocol_pins_differ")`.
- evidence: scripts/reissue_calibration_acceptance.py:602 — `return 0 if report["verdict"] == "PROCEED" else SCIENCE_DELTA_STOP_EXIT`; :605 `raise SystemExit(main())`. `CORPUS_AUTHENTICATION_FAILURE_EXIT = 2` at :45.
- producer: scripts/reissue_calibration_acceptance.py `main`.
- transaction_relevant: yes.

---

### D-139 A1 · clause 1
- clause (verbatim): "A1 — In-process adversary RULED OUT OF MODEL (registered limitation, family-wide). … The paper states the assumption once, plainly."
- source: docs/decision_log.md:10068-10079
- status: B
- evidence (the paper half IS installed): docs/paper/draft-v1.md:445 — "**Where the captures came from rests on trusting the operator.** … Two gaps in this trust are worth naming explicitly, because the design places them outside what it defends against rather than defeating them. The first is a program running on this same machine under the same user account as the measurement…".
- evidence: docs/paper/draft-v1.md:447 — "Because a locally running hostile program lies outside the assumption stated just above, this is carried as a disclosed limitation with a procedural rule attached…".
- evidence (the registration half is MISSING): docs/risk_register.md — the risk table ends at R-020 (line 40); `grep -n "^| R-"` shows R-001..R-020 and no row for the in-process-adversary exclusion. The same cold gate that ruled D-141 wrote the registration standard explicitly at docs/risk_register.md:376-377: "Code comments are not registration; this row is." By that standard A1's "registered limitation, family-wide" has no register row.
- producer: docs/paper/draft-v1.md (the disclosure) — installed; docs/risk_register.md (the registration home) — not installed.
- transaction_relevant: no — a paper disclosure, not mint/arm/window/consumption/claim-time validation.
- note: B rather than A because the artifact D-141 named as the registration home carries no A1 row; the rule lives only in decision-log prose and paper prose.

### D-139 A1 · clause 2
- clause (verbatim): "(1) WO-RECORDER-GRANT-IDENTITY is RETIRED to the registered check-to-grant limitation — no implementation, no cold gate"
- source: docs/decision_log.md:10072-10074
- status: A
- evidence: TASK_QUEUE.md:121 — the row reads `RETIRED WITHOUT IMPLEMENTATION by D-139 A1 (Ed: in-process adversary out of model) — the registered check-to-grant limitation stands as the permanent disposition; design consult custodied docs/process_traces/2026-08-16-grant-identity-consult/ should appetite change.`
- evidence: docs/decision_log.md:9538 — the check-to-grant TOCTOU is described in the decision log as a registered limitation of `window_duration_margins.py`.
- producer: TASK_QUEUE.md.
- transaction_relevant: no.

### D-139 A1 · clause 3
- clause (verbatim): "(2) the T-0 trusted-operator limitation v1 is FINAL for the MVP claim (option-(a) attested capture stays closed); (3) the launch-binding forged-complete-context residual is FINAL as registered."
- source: docs/decision_log.md:10074-10077
- status: C
- evidence: `grep -rn "forged.complete.context" docs/risk_register.md docs/decision_log.md` returns exactly one hit — docs/decision_log.md:10076, the ruling itself. No register row, no code constant, no test.
- evidence: `grep -rn "T-0 trusted-operator\|trusted-operator limitation" docs/risk_register.md docs/decision_log.md` returns exactly one hit — docs/decision_log.md:10074, the ruling itself. docs/risk_register.md:395 mentions "trusted-operator" only inside R-020, a different residual (D-141(ii)).
- producer: none found — neither residual is registered anywhere outside the decision-log sentence that declares them "FINAL as registered".
- transaction_relevant: yes — both concern T-0 capture and launch binding, which are arm/window-path properties whose limitation text the claim's disclosure depends on.
- note: this is a self-referential registration: the ruling says "FINAL as registered" but no register row exists to be final. Same shape as A1 clause 1, one level worse.

### D-139 A2 · clause 4 — **KNOWN DEFECT, already ruled by D-157**
- clause (verbatim): "ONE primary Holm family, alpha=0.05, m=2, containing the decode and prefill_p256 contrasts, two-sided tests with pre-registered positive scientific directions; a missing/non-estimable member stays in the frozen m=2 … These values enter the gamma prospective manifest's families block at the production freeze."
- source: docs/decision_log.md:10081-10089
- status: B
- evidence (producer emits m=1): configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:948-954 — `"multiplicity": "Holm", "family_m": 1,` with `"multiplicity_note": ("family_m=1 is contingent on unresolved decode/prefill family-cardinality ratification; see the prefill_p256 cell's multiplicity TODO.")`.
- evidence (producer leaves prefill EMPTY): same file :974-986 — `"test": empty_slot("TODO(lead authority): D-122 requires the arm but does not pin the prefill inferential test")`, `"family_alpha": empty_slot(…)`, `"multiplicity": empty_slot("TODO(lead authority): ratify whether decode and prefill share a family")`, `"family_m": empty_slot("TODO(lead authority): ratify multiplicity cardinality")`.
- evidence (second producer, same defect): same file :1522-1531 — the plan-side contrast emits `"multiplicity": {"method": "Holm", "alpha": 0.05, "m": 1, "note": "family_m=1 is contingent …"}`; :1549-1556 leaves the prefill `test` and `multiplicity` EMPTY.
- evidence (THIRD producer, not named in D-157's row): joulewise/analysis_manifest_v3.py:470-478 — `_family_and_contrast()` hardcodes ONE family with `"multiplicity": {"method": "holm", "alpha": 0.05, "q": None, "m": 1}` and `"contrast_ids": [contrast_id]` (decode only); `build_analysis_manifest_v3` writes it at :579, :619.
- evidence (the VALIDATOR is pinned to the wrong value too): joulewise/analysis_manifest_v3.py:968-971 — `expected_families, expected_contrasts = _family_and_contrast(); families = value.get("families"); if families != expected_families: errors.append("manifest.families: must be the frozen Holm alpha=0.05 m=1 family")`. Installing m=2 therefore requires changing the validator as well as the generator.
- evidence (validator never reached from the freeze path): `grep -rn "validate_prospective_analysis_manifest_v3" joulewise scripts configs tests` → callers are joulewise/analysis_manifest_v3.py:2838, :3759, :3876 (all inside the same module), the `__all__` entry at :4178, and tests/test_analysis_manifest_v3.py. ZERO callers in `scripts/` and ZERO in `configs/campaigns/*/generate_configs.py`.
- evidence (the gamma generator does not import it): `grep -n "from joulewise" configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py` → detection_floor, floor_extraction, identity_pins, arm_readiness, receipt_oracle. Not analysis_manifest_v3.
- evidence (the frozen-m mechanism itself IS generic and correct): joulewise/analysis_engine/multiplicity.py:49-54 — `holm_adjust(..., m=m)` "Return Holm-adjusted p-values while retaining the frozen ``m``"; `adjust_p_values` at :119-139 takes `m` as a parameter. Nothing in the engine hardcodes 1; the wrong value is entirely at the producers.
- producer: configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py `build_analysis_manifest` (:1478, written at :2122) and joulewise/analysis_manifest_v3.py `build_analysis_manifest_v3` (:579-627).
- transaction_relevant: yes — the gamma prospective manifest is minted into the `_v4` pack and consumed at the claim edge.
- note: ALREADY RULED. D-157 (docs/decision_log.md:184; ruling `docs/process_traces/2026-08-27-t26/holm-m-consult/04-MAGISTRATE-RULING.md`) found exactly this and gates the `_v4` transaction night on worklist item **W-10** (R-1 install A2 verbatim + regenerate; R-2 close the class by running the prospective validator on the freeze/readiness path). Not re-litigated here. One addition for W-10's scope: the m=1 literal also lives in the *validator's expected value* at joulewise/analysis_manifest_v3.py:476 and its error string at :971, and in the *builder* at :470-478 — three sites, not just the campaign generator.

### D-139 A2 · clause 5
- clause (verbatim): "the frozen cross-arm block-strata mapping (block numbers 1-10 across both arms) carries the family (mechanism merged in #155)"
- source: docs/decision_log.md:10086-10088
- status: B
- evidence (consumer mechanism installed): joulewise/analysis_manifest_v3.py:1187-1250 — `frozen_family_block_strata(...)`, docstring "…sensitivity evidence when that cross-arm mapping is absent or ambiguous", raising `AnalysisManifestV3Error("frozen family block strata are absent")` at :1203.
- evidence (it has a real consumer): joulewise/analysis_engine/__init__.py:23 imports it; :1378-1398 — `if …: frozen_strata = frozen_family_block_strata(…)` guarded by `except: … "multi-contrast family lacks complete frozen block strata"` at :1392.
- evidence (producer emits nothing cross-arm): joulewise/analysis_manifest_v3.py:566-578 — the `blocks` list is built solely from `f"sw-decode-contrast-b{block_number:02d}"`; there is no prefill_p256 arm block. The mapping the ruling says "carries the family" is not produced.
- evidence: joulewise/analysis_manifest_v3.py:1199-1212 — `matching_families` requires exactly one family; with `_family_and_contrast()` returning a single decode contrast, the multi-contrast branch at analysis_engine/__init__.py:1381 is unreachable in production.
- producer: joulewise/analysis_manifest_v3.py `build_analysis_manifest_v3` (blocks at :566-578).
- transaction_relevant: yes — same manifest bytes as clause 4.
- note: same root cause as the D-157 defect (m=1, one contrast). Listing it separately because W-10 must emit the cross-arm strata, not only bump `m` — the analysis engine hard-refuses a multi-contrast family whose strata are absent.

### D-139 A2 · clause 6 — **SECOND INSTANCE OF THE D-157 SHAPE, different artifact**
- clause (verbatim): "(3) p256 floor: DEDICATED ARTIFACT (no p128→p256 transport rule) — Ed's preference, at zero extra collection cost: the funded fixed-256-token prefill floor cells are already in the frozen packs (#138)."
- source: docs/decision_log.md:10089-10092
- status: C (for the binding; the cells themselves are A — see evidence)
- evidence (the cells DO exist, as the ruling says): configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:314 — `"d117-qwen25-1p5b-prefill-p256-floor-v3"`; configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py:397 and :1297 — `"d117-qwen25-7b-prefill-p256-floor-v3"`. Pack stages `04_phase_prefill_p256_absolute`, `05_/06_phase_prefill_p256_abba_blocks_*` are present on disk in both floor packs.
- evidence (the DEDICATED-FLOOR RULING NEVER ENTERED THE GAMMA GENERATOR): configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:797-808 — `consumer_declaration()` still emits `"prefill_p256_floor_dependency": {"cell_ids": empty_slot("TODO(lead authority): D-122 does not identify ruled 256-token prefill floor cells", value=[]), "transport_rule": empty_slot("TODO(lead authority): D-122 does not ratify transport from the alpha/beta 128-token prefill floor cells to this 256-token estimand")}`.
- evidence (and it is already BAKED INTO COMMITTED PACK BYTES): configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/consumer_family_declaration.json — read back with python json: `prefill_p256_floor_dependency.cell_ids = {"status": "EMPTY", "value": [], "todo": "TODO(lead authority): D-122 does not identify ruled 256-token prefill floor cells"}` and `transport_rule = {"status": "EMPTY", "value": "", "todo": "TODO(lead authority): D-122 does not ratify transport from the alpha/beta 128-token prefill floor cells to this 256-token estimand"}`.
- evidence (the contrast cell's floor binding is EMPTY too): same generator :1557-1560 — `"floor_dependency": empty_slot("TODO(lead authority): ratify a 256-token prefill floor or transport rule")` for the prefill_p256 arm, while the decode arm at :1533-1537 binds a real `consumer_family_declaration_sha256`.
- producer: configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py `consumer_declaration()` (:780-813) and `build_analysis_manifest`/plan cells (:1478, :1549-1560); the declaration is SHA-bound into the pack (`declaration_sha` consumed at :1535).
- transaction_relevant: yes — `consumer_family_declaration.json` is inside the gamma pack whose bytes the `_v4` mint freezes.
- note: D-157's ruling text names "dedicated p256 floor" inside the D-139-A2 clause it found uninstalled, so this IS inside W-10's authority. But D-157's *evidence* is stated against the analysis manifest's `families` block; this clause fails in a DIFFERENT file — `consumer_family_declaration.json` — whose bytes are separately hashed into the pack. If W-10 is scoped to the manifest alone it will regenerate an m=2 family whose prefill member still has no floor dependency. Flagging for W-10 scope, not as a new ruling.

### D-139 A2 · clause 7
- clause (verbatim): "The consumption edge's analysis_manifest_transport_ruling_pending branch remains permanently refusing (dormant), as designed."
- source: docs/decision_log.md:10090-10092
- status: A
- evidence: joulewise/analysis_manifest_v3.py:39-41 — `TRANSPORT_RULING_PENDING_REFUSAL = ("analysis_manifest_transport_ruling_pending")`.
- evidence (it has a real refusal site, not just a constant): joulewise/analysis_engine/__init__.py:22 imports it; :1676 — `f"{TRANSPORT_RULING_PENDING_REFUSAL}: valid transported v3 …"` inside the refusal message.
- evidence (test): tests/test_analysis_integration.py:33 imports it, :837 asserts it.
- producer: joulewise/analysis_engine — the consumption edge; the branch is present and refusing.
- transaction_relevant: yes — consumption edge.

### D-139 A3 · clause 8
- clause (verbatim): "uniform `_v2` successor pack IDs"
- source: docs/decision_log.md:10094-10095
- status: D
- evidence (superseded): docs/decision_log.md:170 (D-147, 2026-08-19) — "immutable `_v3` pack family bound at birth to the LIVE generation"; docs/decision_log.md:178 (D-150) and :175 (D-151) then govern the `_v4` family.
- evidence (shape installed at the ruled values' successor): configs/arm_readiness/d117_row_registry_v2.json:527-531 — `"successor_pack_ids": {"ALPHA": "d117_floor_qwen25_1p5b_v4", "BETA": "d117_floor_qwen25_7b_v4", "GAMMA": "d117_contrast_qwen25_1p5b_vs_7b_v4"}`.
- evidence (enforced at the producer): joulewise/arm_readiness.py:3841-3858 — the profile resolver reads `lifecycle["successor_policy"]["successor_pack_ids"]` and raises `readiness_row_registry_mismatch` for an ID the registry does not install, and again for an installed ID "of an unapproved shape".
- evidence: joulewise/arm_readiness.py:10674-10676 — the family-publication marker builder raises `FamilyPublicationError("roster_mismatch", …)` if the pack roots differ from the registry roster.
- producer: joulewise/arm_readiness.py (marker/freeze path), registry file `configs/arm_readiness/d117_row_registry_v2.json`.
- transaction_relevant: yes — successor pack identity is the `_v4` mint's identity.
- note: SUPERSEDED literal, installed shape. The stale `_v2` literal survives in an operator-facing document: docs/process/phase2-transaction-runsheet.md:71-79 still instructs "Generate the `_v2` successor family" and "Install the D-139-approved reserved values … (uniform `_v2` IDs; freeze-0002 …)". That runsheet is not the live `_v4` runbook but is not marked superseded either.

### D-139 A3 · clause 9
- clause (verbatim): "chain-monotonic `freeze-0002` with explicit predecessor bindings"
- source: docs/decision_log.md:10094-10095
- status: D (the `freeze-0002` literal) / A (the chain-monotonic-with-predecessor-bindings mechanism)
- evidence (literal superseded): joulewise/arm_readiness.py:10219-10227 — the live constants are `freeze-0004` (`freeze["receipt_id"] != "freeze-0004"` → `FamilyPublicationError("freeze_binding_mismatch", "freeze-0004 constants differ")`); :10567-10568 — `freeze_not_pass`, "family freeze must be PASS freeze-0004"; scripts/build_v4_histsem_pinset.py:154-156 — "the v4 pinset requires freeze-0004 exactly". Superseding authority: D-150/D-151 (docs/decision_log.md:178, :175).
- evidence (mechanism installed): joulewise/arm_readiness.py:1418-1424 — `_validate_freeze_predecessor(...)` "Exact-key structural validation of D-139's predecessor binding."
- evidence (monotonic enforced): joulewise/arm_readiness.py:2367-2374 — `predecessor_ordinal = _validate_freeze_predecessor(receipt["predecessor"])` then a refusal "freeze receipt ordinal is not the predecessor ordinal plus one"; the same check on the successor side at :4759-4768.
- evidence (bindings pinned by name): configs/arm_readiness/d117_row_registry_v2.json:516-524 — `"freeze_receipt_v2_predecessor_bindings": ["evidence_set_sha256","freeze_receipt","identity_receipt","pack_digest_algorithm","pack_id","pack_path","pack_sha256","plan_id","plan_sha256"]`; validated at joulewise/arm_readiness.py:1869-1884 (`"R1 freeze-v2 predecessor bindings are invalid"`).
- evidence (bindings authenticated against real bytes): joulewise/arm_readiness.py:3685-3706 — reopens the predecessor pack and raises `histsem_binding_mismatch`, "freeze predecessor binding differs from current bytes".
- producer: joulewise/arm_readiness.py freeze-mint path.
- transaction_relevant: yes.
- note: `scripts/ed_session/build_rehearsal_env.sh:71-88` still requires `freeze-0002` — correct for the rehearsal environment, but a live-vs-rehearsal literal split an operator could trip over.

### D-139 A3 · clause 10
- clause (verbatim): "the existing operational horizons — 20-minute volatile / six-hour procedural — carry forward as the approved freshness defaults"
- source: docs/decision_log.md:10096-10098
- status: A
- evidence: configs/arm_readiness/d117_row_registry_v2.json:26, :40, :82, :96, :103, :145, :152, :166, :194 — `"horizon_ns": 1200000000000` (20 min); :33, :89, :124, :201 — `"horizon_ns": 21600000000000` (6 h). No `ED_RESERVED` sentinel remains anywhere in the file (verified: `'ED_RESERVED' in json.dumps(registry)` → False).
- evidence (producer-side validation): joulewise/arm_readiness.py:1717-1762 — `validate_r1_lifecycle_registry` refuses a non-positive / wrongly-classed horizon (`"R1 evidence_policies[i].horizon_ns is invalid"`, `"… must have a positive horizon and …"`), and refuses an `ED_RESERVED:` sentinel unless the reserved-prefix branch applies.
- evidence (test): tests/test_arm_readiness_schemas.py:475 — `self.assertEqual(policies[kind]["horizon_ns"], 21600000000000)`.
- producer: the registry file plus joulewise/arm_readiness.py `validate_r1_lifecycle_registry` (:1828-1890), which every freeze/arm path loads.
- transaction_relevant: yes — evidence freshness gates the arm.

### D-139 A3 · clause 11
- clause (verbatim): "The environment-fingerprint comparison semantics remain an open Ed ruling (the R1 fail-closed seam stands)."
- source: docs/decision_log.md:10098-10100
- status: A
- evidence: joulewise/arm_readiness_evidence.py:126 — the policy vocabulary contains `"EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE"`.
- evidence (the seam refuses): joulewise/arm_readiness_evidence.py:2922-2926 — `… == "EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE" and receipt["environment_fingerprint"] != _execution_environment_fingerprint(context, kind)` — an exact-match refusal at reuse.
- evidence (registry populates it): the R1 registry's 29 evidence policies split `NOT_APPLICABLE` 13 / `EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE` 12 / `NO_R1_AUTHORING_LANE` 4 (read from configs/arm_readiness/d117_row_registry_v2.json via json).
- evidence (validated at load): joulewise/arm_readiness.py:1730-1762 — `environment_comparison` is required, string-checked, and cross-checked against `freshness_class`/horizon.
- producer: joulewise/arm_readiness_evidence.py (evidence issuance and reuse).
- transaction_relevant: yes.

### D-139 A3 · clause 12
- clause (verbatim): "RESERVED STILL: the final exact-byte publication confirmation at the transaction's irreversible point — Ed confirms when the bytes exist."
- source: docs/decision_log.md:10100-10103
- status: D
- evidence: docs/decision_log.md:176 (D-150b, 2026-08-23) — "packet item 10 + the exact-byte class, discharged by DELEGATION: 'Approve them for me if they match … def want the campaign moving fast'".
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:447 — "the step-6 exact-byte confirmation and the terminal review are **delegated to**…"; :1605 — "**D-150b delegates** the step-6 exact-byte confirmation and the terminal…".
- producer: the runbook's Phase E/step-6 sequence.
- transaction_relevant: yes — it is the transaction's irreversible point.
- note: superseded by D-150b (docs/decision_log.md:176). The stale `_v2` runsheet still describes it as Ed-reserved at docs/process/phase2-transaction-runsheet.md:96-99.

### D-139 · clause 13 (shakedown-first sequencing directive)
- clause (verbatim): "The first quiet-machine consumption after a READY-candidate verdict is MINIMAL INSTRUMENT VERIFICATION — the ED-Q-L9-3 quiet-state baseline and calibration-only shakedown runs proving signal purity — BEFORE any claim window. … The claim windows (alpha/beta/gamma) follow only after the shakedown evidence is clean."
- source: docs/decision_log.md:10105-10111
- status: A
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1065-1066 — "**The first real arm of the `_v4` family is the shakedown window's own**, under its D-149 GO receipt. B-3 makes the shakedown a **non-claim** window…".
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1417 — "with no real arm. The family's first real arm is the shakedown window's,".
- evidence: docs/process/window-run-cards/shakedown-v3-first-light.md:3 — "Purpose (D-139 SHAKEDOWN-FIRST directive): the first quiet block after…".
- evidence: docs/process/ed-evening-checklist.md:29 — "shakedown runs per D-139."
- producer: the `_v4` real-transaction runbook (the document the operator executes) plus the window run card.
- transaction_relevant: yes — it orders the transaction night's windows.

---

### D-140 · clause 1
- clause (verbatim): "the receipts-govern-over-descriptive-bytes core is EXTENDED to ALL successor packs by this entry's own authority"
- source: docs/decision_log.md:173 (index), 8893-8896
- status: A
- evidence: configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:61 — `SUCCESSOR_EMITTED_STATUS = "as_generated_pre_d134_freeze"`, with the rationale at :54-60 ("it states when the bytes were generated, never that the pack is unfrozen or unarmable. The dynamic authority remains GenerationIdentity.target_status, read from the authenticated attachment.").
- evidence (all successor generators carry it): `grep -c as_generated_pre_d134_freeze` per generator — the three contrast generators (`_v1`,`_v2`,`_v3`) have 2 each, the six floor generators 1 each; the three pre-D-117 generators (p2_015_floors, qwen25_7b_decode_floor_v1, splitwise_decode_v1) have 0 and are not successor packs.
- producer: the pack generators — they write the descriptive bytes.
- transaction_relevant: yes — pack bytes minted in the `_v4` transaction.

### D-140 · clause 2
- clause (verbatim): "The draft→frozen transition IS the minting+committing of the D-134 freeze receipt and plan-tree attachment"
- source: docs/decision_log.md:8896-8898
- status: A
- evidence: configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:233-237 — `def target_status(self): if not self.target_is_current: return DRAFT_STATUS; return freeze_aware_status(ARM_READINESS_ATTACHMENT["freeze_receipt"])` — status is a function of the attachment, not of a stored byte.
- evidence: same file :148-158 — `ARM_READINESS_ATTACHMENT = plan_arm_readiness_attachment(REPO_ROOT / PACK_REL, "GAMMA", REPO_ROOT)`; `PRESERVE_CURRENT_FROZEN_BYTES` and `PACK_STATUS` derive from it. The attachment is read from the real pack root through `joulewise.arm_readiness`, not from a literal.
- evidence: same file :98-105 — `freeze_aware_status()` returns `DRAFT_STATUS` while the attached receipt is the 2026-08-13 one and `FROZEN_STATUS` once a different receipt is attached.
- evidence (test): tests/test_d117_decode_contrast_plan.py:646-648 — "``target_status``, the DYNAMIC state read from the authenticated freeze"; :958 asserts `successor.target_status == "unfrozen_draft"`; :965 asserts `current.target_status == "frozen_by_d134_receipt"`.
- producer: the gamma generator's `GenerationIdentity`.
- transaction_relevant: yes.

### D-140 · clause 3
- clause (verbatim): "bytes inside the receipt's `pack_identity` transitive closure (`calibration_plan.json` and everything hashed into it) never change post-mint, and remaining pack descriptive bytes are never repaired"
- source: docs/decision_log.md:8898-8900
- status: A
- evidence (downgrade guard, refuses before any write): configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:195-201 — `if self.target_ordinal < self.current_ordinal: raise ValueError(… "an earlier family's committed bytes are never rewritten by a later generator, in any mode")`.
- evidence (preserve-mode guard, both directions): same file :202-211 — `if self.preserve_current_frozen_bytes and not self.target_is_current: raise ValueError("preserve mode requires the current target identity")` and `if not self.preserve_current_frozen_bytes and self.target_is_current and (…): raise ValueError("the current frozen identity requires preserve mode")`.
- evidence (freeze-neutral literal so a byte never needs repairing): same file :62-77 — `LEGACY_FREEZE_RATIFICATION` vs `SUCCESSOR_FREEZE_RATIFICATION`, with the comment "Successor packs therefore serialize the ratification AUTHORITY, which is true on both sides of the receipt, instead of a ratification STATE that flips at it."
- evidence (test): tests/test_d117_decode_contrast_plan.py:948 `test_target_status_inventory_and_invalid_modes_are_fail_closed`; :1551-1571 asserts the pre-freeze state emits `as_generated_pre_d134_freeze` at every site; :1745-1757 asserts the same after freeze.
- producer: the gamma generator (and the five sibling generators, same construction).
- transaction_relevant: yes.

### D-140 · clause 4
- clause (verbatim): "\"Freeze-aware\" status = dynamic `target_status` from the authenticated attachment + the fail-closed non-preserve guard + option-(d) freeze-neutral emitted wording (round 6/7: `as_generated_pre_d134_freeze` + authority-naming fields)."
- source: docs/decision_log.md:8900-8903
- status: A
- evidence: all three components read at configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py — dynamic `target_status` :233-237; the fail-closed guards :195-211; the freeze-neutral wording :61 and :72-77; the emitted-status function `emitted_draft_status()` :108-128 with "``FROZEN_STATUS`` is unreachable from every serialization site by design".
- evidence (test): tests/test_d117_decode_contrast_plan.py:1566 — `set(sites.values()) - {"as_generated_pre_d134_freeze"}` asserted empty across serialization sites; :801 execs `GenerationIdentity(preserve_current_frozen_bytes=True).target_status` in a subprocess.
- producer: the pack generators.
- transaction_relevant: yes.

### D-140 · clause 5
- clause (verbatim): "The first structural consult's SS-B3 transition sentences, D-6, and R-7 are superseded per the composed verdict's amendment language."
- source: docs/decision_log.md:8903-8905
- status: C
- evidence: greps run — `grep -rn "D-6\b\|R-7\b" docs/process_traces/2026-08-18-freeze-semantics-coldgate/` is a trace-internal reference; nothing in `joulewise/`, `scripts/`, `configs/`, or `tests/` cites §B3, D-6, or R-7, and the superseded consult is preserved-not-edited by design.
- producer: none — a documentary supersession whose target is a preserved historical trace that is deliberately not edited.
- transaction_relevant: no.
- note: not an implementation clause; recorded for completeness.

---

### D-141 · clause 1
- clause (verbatim): "(i) Post-validation symlink substitution at the generators' check-then-write boundary: registered residual on desk-time single-operator grounds (D-139 A1 cited by analogy), 16-case refuse-before-any-write coverage closes the accidental class"
- source: docs/decision_log.md:8909-8913
- status: A
- evidence (registered, per the gate's own standard): docs/risk_register.md:39 — the R-019 table row; :366-389 — the full section, including :376-377 "Code comments are not registration; this row is."
- evidence (the write boundary exists): configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:560-590 — the residual comment then `root = output_root.absolute()`, `def refuse(path, reason)` raising `ValueError(f"refusing generation: {reason}: …")`, `if root.is_symlink(): refuse(root, "output root is a symlink")`, `if root.exists() and not root.is_dir(): refuse(root, "output root is not a real directory")`, then a per-component ancestor walk.
- evidence (present in every successor generator): the same comment block at configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py:567, `_v2`:567, `_v3`:567, d117_floor_qwen25_1p5b_v1/:631, `_v2`:631, `_v3`:634, d117_floor_qwen25_7b_v1/:2735, `_v2`:2735, `_v3`:2740.
- evidence (tests): tests/test_d117_decode_contrast_plan.py:996 `test_generation_refuses_symlinked_write_inventory_before_any_write` (cases at :1001-1010: pack_directory / pack_file / sidecar); tests/test_d117_floor_qwen25_1p5b_plan.py:629 and tests/test_d117_floor_qwen25_7b_plan.py:631, same test name.
- producer: the pack generators' write-inventory validation, which runs before any `write_bytes`.
- transaction_relevant: yes — pack generation is the `_v4` mint.
- note: the "16-case" figure is an aggregate across the three plan-test families (3 case kinds x directory/file/sidecar variants per generator family); I verified the coverage exists at all three, not the exact arithmetic of 16.

### D-141 · clause 2
- clause (verbatim): "reopening trigger = threat-model revision admitting concurrent adversarial local processes or multi-operator generation"
- source: docs/decision_log.md:8913-8915
- status: A
- evidence: docs/risk_register.md:379-381 — "Trigger (reopening, cold ruling C-B1a): any threat-model revision admitting concurrent adversarial local processes, or multi-operator / shared-machine pack generation."
- evidence (mirrored at the code site): configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:568-572 — "The residual reopens if the threat model is revised to admit concurrent adversarial local processes, or if generation moves to multi-operator/shared-machine use (cold-gate conditions C-B1a and C-B1b, 2026-08-18…)".
- producer: docs/risk_register.md (the registration home, per its own :376-377 rule).
- transaction_relevant: no — a conditional reopening rule, not a mint-time value.

### D-141 · clause 3
- clause (verbatim): "Delta-4's dirfd/`O_NOFOLLOW` remedy demand is formally SUPERSEDED."
- source: docs/decision_log.md:8915 / index row 174
- status: A
- evidence: docs/risk_register.md:385-387 — "Fallback: implement the dirfd / `O_NOFOLLOW` write boundary (delta-4's F2 remedy demand, formally SUPERSEDED at this gate per C-B1b) and regenerate; no published evidence depends on the current boundary."
- evidence: configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:571-573 — "C-B1b formally supersedes delta-4's F2 dirfd remedy demand. No dirfd/O_NOFOLLOW hardening is attempted here; the residual is registered, not closed."
- producer: docs/risk_register.md + the generator comment (both, consistently).
- transaction_relevant: no.

### D-141 · clause 4
- clause (verbatim): "(ii) `_load_freeze_reference` accepting a hand-authored v1-schema receipt in a `_v2` pack: registered residual under trusted-operator (no crash or tooling path produces the state)."
- source: docs/decision_log.md:8916-8918
- status: A
- evidence (the function exists and is on the live path): joulewise/arm_readiness.py:6475 `def _load_freeze_reference(`; callers at :6874, :7235, :7564, :7809 — i.e. the dry-run, arm, and verify paths.
- evidence (registered): docs/risk_register.md:40 — the R-020 table row; :390-409 — the full section, naming the mitigation ("mint is v2-selecting pre-write; plan-tree attachment updates are atomic") and the fallback ("key the chain check on the pack generation (pack ID suffix) rather than the receipt schema").
- evidence (the schema-keyed chain is real): joulewise/arm_readiness.py:2332-2340 — `successor = declared == FREEZE_RECEIPT_V2_SCHEMA` then the exact-key set for v2 vs v1; :425 — `FREEZE_RECEIPT_V2_KEYS = (FREEZE_RECEIPT_KEYS - {"supersedes"}) | {"predecessor"}`.
- producer: joulewise/arm_readiness.py freeze mint (v2-selecting pre-write).
- transaction_relevant: yes — the freeze loader runs at dry-run/arm/verify in the transaction.

### D-141 · clause 5
- clause (verbatim): "Both registered in `docs/risk_register.md` (R-019, R-020)"
- source: docs/decision_log.md:174 (index) / 8918-8920
- status: A
- evidence: docs/risk_register.md:39 — `| R-019 | Pack-generator check-then-write boundary admits post-validation symlink substitution | 2+ | low | high | registered residual (D-141(i), cold gate 2026-08-18) |`.
- evidence: docs/risk_register.md:40 — `| R-020 | Freeze loader accepts a hand-authored v1-schema receipt inside a `_v2` pack | 2+ | low | medium | registered residual (D-141(ii), delta-8 ratified 2026-08-18) |`.
- producer: docs/risk_register.md.
- transaction_relevant: no.
