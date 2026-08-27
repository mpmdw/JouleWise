# G7 — D-150, D-150a, D-150b, D-151, D-152, D-153, D-154, D-155, D-156, D-157

Sweep basis: index rows `docs/decision_log.md:175-184`, tail bodies
`:10177-10263` (all tail bodies for this group are POINTERS — D-150a/D-150b
have no body at all, and D-151/D-152/D-153/D-154/D-155/D-156/D-157 bodies say
"index row carries the operative detail; this section is the tail-body anchor").
Implementation clauses were therefore extracted from the index rows and from the
pointed-to trace rulings, cited as `trace-file:line`.

Repo head at sweep time: `0dd3b6dc` (main, clean).

---

## D-151 — O-1 cold-gate pinset ruling (index row `docs/decision_log.md:175`)

Pointer target: `docs/process_traces/2026-08-22-t20/o1-coldgate/MAGISTRATE-RULING-O1.md`
(nine-condition set at `:37-110`). Conditions enumerated from that ONE home.

### D-151 · clause 1 (condition 1)
- clause (verbatim): "Pre-derivation reviewed candidate carries the contract amendment (governed pinset → closed, ordered, code-enumerated chain), the chain-read code delta (constant → tuple, gate loops, `verify_all` union, existing refusal codes; CLI and activation model unchanged), and the allowlist at **112 with the successor pinset's exact path as the 112th entry**. No ruled number is amended."
- source: docs/decision_log.md:175; MAGISTRATE-RULING-O1.md:41-46
- status: A
- evidence: joulewise/arm_readiness.py:2853-2856 — `RECEIPT_HISTSEM_PINSET_RELATIVE_PATH` is a 2-tuple of `legacy_receipt_histsem_pinset_v1.json` and `legacy_receipt_histsem_pinset_v4_v1.json` (constant → tuple, closed enumeration).
- evidence: configs/arm_readiness/d117_row_registry_v2.json — `freeze_evidence_lifecycle.irrelevant_path_allowlist` has exactly 112 entries, and `configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json` is a member (verified by loading the JSON and counting).
- evidence: tests/test_receipt_histsem.py:89-103 — `test_pinset_chain_is_closed_ordered_and_absent_successor_is_unchanged` asserts the exact 2-tuple; removing the successor path reddens it.
- evidence: tests/test_arm_readiness_schemas.py:457-459 — asserts the successor is in the allowlist AND in `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS`.
- producer: the tracked registry `configs/arm_readiness/d117_row_registry_v2.json` (reviewed candidate, PR #? / S1-CANDIDATE-01) + `joulewise/arm_readiness.py` chain reader.
- transaction_relevant: yes — the changed-set contract at the `_v4` mint.

### D-151 · clause 2 (condition 2)
- clause (verbatim): "The successor class is DIGEST-CONDITIONAL against Ed's step-6 confirmation-table digest — V-1(vi) exercised, not waived; this is what makes O-1-D lawful where Option 1 is not. No probe may record \"the test run itself\" as an authenticator."
- source: docs/decision_log.md:175; MAGISTRATE-RULING-O1.md:47-50
- status: A
- evidence: joulewise/arm_readiness.py:2858-2871 — `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS = frozenset({RECEIPT_HISTSEM_PINSET_RELATIVE_PATH[1].as_posix()})` with the docstring "the bytes committed at the reviewed HEAD must additionally hash to the digest Ed recorded in the step-6 confirmation table's matching section (the C -> S edge). Without that confirmation the path stays in the relevant set and the gate refuses `DEPENDENCY_CHANGED_SET`."
- evidence: joulewise/arm_readiness.py:2909-2922 — only paths in `R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS` may take the conditional branch; anything else raises.
- evidence: joulewise/arm_readiness.py:4426-4427 — the gate intersects the registry allowlist with the digest-conditional set at evaluation.
- evidence: tests/test_receipt_histsem.py:168-186 — the successor shape check is explicitly documented "THIS IS NOT AN AUTHENTICATOR … The successor's ONLY byte authenticator is the hS literal" (the "no probe records the test run as authenticator" sub-clause, in prose and in the test's own design).
- producer: `joulewise/arm_readiness.py` R1 changed-set gate; the confirmation digest is supplied out of band per `docs/contracts/d117_step6_confirmation_table.md:75-85`.
- transaction_relevant: yes — arm-time changed-set subtraction.

### D-151 · clause 3 (condition 3)
- clause (verbatim): "Fixation = the first commit after window close (r4-3 commit-freeze): successor SHA literal + counts land as NEW assertions touching no v1 assertion; independent reviewer recomputes the SHA against Ed's step-6 table; the same commit renames the then-false `test_differential_self_test_all_nine_packs`."
- source: docs/decision_log.md:175; MAGISTRATE-RULING-O1.md:51-56
- status: split — the rename sub-clause is **A**; the fixation commit itself is **C (future-dated by the ruling; runbook slot exists)**
- evidence (rename, A): tests/test_receipt_histsem.py:240 — the method is now `test_differential_self_test_all_governed_packs`, and its comment at :241-244 says "The old name asserted a count that the mint falsifies (D-153 A2)". `grep -rn "differential_self_test_all" tests` returns only this one hit; the nine-packs name is gone.
- evidence (fixation, C): docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:697-701 — "**Fixation does NOT happen here.** … fixation is post-campaign — see §6."; :1200-1205 — "**THE FIXATION COMMIT — first, before anything else.** It carries exactly …"; :1402-1404 — "**No fixation commit.** Fixation is the first commit after the commit freeze".
- evidence (fixation, C): no successor pinset SHA literal or loud-fail guard exists in the tree — `grep -rn "hS\b|SUCCESSOR_PINSET_SHA" tests/test_receipt_histsem.py` returns only prose references at :45 and :174, no literal.
- producer: the future fixation commit (magistrate-executed, runbook Phase H5 / §6 item 6). Nothing in code enforces that the commit carries the literal.
- transaction_relevant: yes — the post-window claim edge.
- note: not a defect at this moment — the ruling itself dates this after window close. Recorded C so the parent can see nothing is installed yet, with the runbook slot cited.

### D-151 · clause 4 (condition 4)
- clause (verbatim): "TWO-PART GREEN (material): local suite green is forged-`origin/main`-conditional (`s0-runsheet.md:325`; `tests/test_receipt_histsem.py:92-103` runs `require_published=True`) and must be recorded with the forged OID; acceptance closure requires PUBLISHED green. No transcript may report local green as \"the suite is green.\""
- source: docs/decision_log.md:175; MAGISTRATE-RULING-O1.md:57-62
- status: B
- evidence: tests/test_receipt_histsem.py:253-255 — `result = verify_all_receipt_histsem(ROOT, require_published=True)` — the published-head dependence the condition names is real and live.
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:26 and :997 — "The rehearsal ran inside a throwaway clone with a forged remote"; "classified the result 'forged-`origin/main`-conditional'. **There is no forged …**"; :1363 — "published green. The response is never 'adjust a test expectation'."
- producer: the human/agent transcript author. No code or CI check refuses a transcript that reports local green as "the suite is green"; the discipline exists only as runbook prose.
- transaction_relevant: yes — acceptance closure of the mint.
- note: B, not A: the rule is a reporting discipline with no mechanical enforcement point. Nothing stamps the forged OID into a machine-checked record.

### D-151 · clause 5 (condition 5, as re-scoped by D-155/NR-7)
- clause (verbatim, re-scoped text): "5. The residual runs **mint → post-window fixation** (≤ ~8 days worst case, D-153 A4), with the per-phase controls named. Within it: the sub-interval **mint → the first consuming arm** carries no arm of any kind (r4-3 / B-4: dry-run ceremony only); the sub-interval **first consuming arm → post-window fixation** carries the campaign's claim-bearing arms under the published marker and confirmed table, which is the controlled state the residual prices."
- source: docs/decision_log.md:175 (pointer only, self-declared "This row is a paraphrase"); MAGISTRATE-RULING-O1.md:79-88 (the ONE home)
- status: A
- evidence: MAGISTRATE-RULING-O1.md:63-88 — the amendment marker "**AMENDED 2026-08-26 under D-155 (NR-7). Re-scoped, not struck; the original clause is preserved immediately above.**" and the re-scoped condition text, present verbatim.
- evidence: docs/decision_log.md:175 — the index row carries the "CLARIFIED 2026-08-26 by D-155/NR-7 … This row is a paraphrase; the ONE home for the re-scoped condition 5 is `MAGISTRATE-RULING-O1.md`" pointer, i.e. the ruled one-home discipline is realized.
- producer: the ruling document itself (this clause demands a document amendment, and it landed).
- transaction_relevant: yes — prices the residual across the whole campaign.

### D-151 · clause 6 (condition 6)
- clause (verbatim): "Chain integrity: closed enumeration (un-enumerated pinset files govern nothing); cross-member duplicate `(pack_id, pack_path)` refuses `histsem_pinset_invalid`; absent enumerated member keeps the rule-11-settled `:36` absence semantics UNCHANGED."
- source: docs/decision_log.md:175; MAGISTRATE-RULING-O1.md:89-92
- status: A
- evidence: joulewise/arm_readiness.py:3508 — `raise HistoricalSemanticsError("histsem_pinset_invalid", f"pinset has duplicate rows for {pack_relative}")` on the cross-member duplicate path.
- evidence: joulewise/arm_readiness.py:3223 — `"pinset pack identities must be unique and path-bound"` under the same code.
- evidence: joulewise/arm_readiness.py:3286-3296 — the loader iterates only `RECEIPT_HISTSEM_PINSET_RELATIVE_PATH` (closed enumeration).
- evidence: tests/test_receipt_histsem.py:97-103 — the absent-successor case loads and returns exactly the 9 v1 rows; tests/test_receipt_histsem.py:189-196 asserts absence contributes no rows and is not a refusal.
- producer: `joulewise/arm_readiness.py::_load_histsem_pinset`.
- transaction_relevant: yes — the pinset chain the `_v4` mint extends.

### D-151 · clause 7 (condition 7, standing fixed-point rule)
- clause (verbatim): "FIXED-POINT PRINCIPLE (standing rule, all future transactions): **no authenticator path ever enters any allowlist, in any transaction.** A proposal to add one is a V-1(vi) tripwire event routing to the V-1(vii) derived manifest, not an amendment. `_v5` repeats this shape with its own successor artifact."
- source: docs/decision_log.md:175; MAGISTRATE-RULING-O1.md:93-98
- status: B
- evidence: tests/test_arm_readiness_schemas.py:459-460 — `self.assertFalse(any("d117_step6_confirmation" in path for path in allowlist))` and `self.assertFalse(any("family_publication" in path for path in allowlist))` — two NAMED authenticator classes are mechanically barred.
- evidence: no general predicate exists. `grep -rn "authenticator" joulewise/arm_readiness.py` yields prose only; there is no `is_authenticator_path()` check the registry loader runs over the whole allowlist.
- producer: `configs/arm_readiness/d117_row_registry_v2.json` (hand-edited allowlist). A reviewer, not code, decides whether a proposed 113th entry is an authenticator.
- transaction_relevant: yes — governs every future changed-set contract including `_v5`.
- note: B rather than A because the check enumerates two known authenticator substrings; a NEW authenticator class (say a future confirmation artifact under a different name) would pass both assertions and land in the allowlist unnoticed. That is exactly the D-157 shape one generation out.

### D-151 · clause 8 (condition 8)
- clause (verbatim): "Endorsed out-of-scope defects (to the S-0 runsheet r2 revision): the `freeze_evidence_lifecycle.irrelevant_path_allowlist` key is absent at HEAD (candidate must author it; `s0-runsheet.md:628` would `KeyError`); and the record that the changed-set contract is a WINDOW PROPERTY, not a standing repo invariant — the unstated fact whose absence generated O-1."
- source: docs/decision_log.md:175; MAGISTRATE-RULING-O1.md:99-104
- status: A
- evidence: joulewise/arm_readiness.py:587 and :615 — `"irrelevant_path_allowlist"` is a required registry key with a default `[]`; :1668 `allowlist = registry["irrelevant_path_allowlist"]` no longer KeyErrors because the key is authored.
- evidence: configs/arm_readiness/d117_row_registry_v2.json — the key exists and holds 112 paths.
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:299-301 — "**changed-set window, not the freeze span.** The guard's own files … the changed-set window opens at …" — the window-property record.
- producer: the registry file + the runbook.
- transaction_relevant: yes.

### D-151 · clause 9 (condition 9 — the struck tightening)
- clause (verbatim): "Cold Fable's round-2 history-dependent absence tightening is **STRUCK** … The contingent condition set (merged §4 item 9) governs if a tightening is ever proposed — Ed/magistrate sign-off required."
- source: docs/decision_log.md:175; MAGISTRATE-RULING-O1.md:105-110
- status: A
- evidence: tests/test_receipt_histsem.py:368 — the normative `test_committed_pinset_deletion_gate_returns_normally` still exists unchanged (the ruling's own verification target: striking the tightening means this test stays as it is).
- evidence: joulewise/arm_readiness.py:3286-3296 — no history-dependent absence logic was added.
- producer: n/a — the clause demands that nothing change, and nothing did.
- transaction_relevant: yes — pinset deletion semantics inside the changed-set window.

---

## D-150b — step-6 exact-byte confirmation + terminal review DELEGATED (index row `docs/decision_log.md:176`; NO body section)

### D-150b · clause 1
- clause (verbatim): "the STEP-6 EXACT-BYTE CONFIRMATION and the TERMINAL REVIEW are DELEGATED to the magistrate, executed as mechanical comparisons with INDEPENDENCE preserved (every digest independently recomputed from the artifacts — never accepted from the producing session's report — before the a==b evaluation; refusal on any mismatch, with Ed pinged on mismatch)"
- source: docs/decision_log.md:176
- status: B
- evidence: docs/contracts/d117_step6_confirmation_table.md:8-13 — "Authority is the 2026-08-22 family-marker magistrate ruling, D-151 conditions 2 and 7, and D-150b (delegated execution of the exact-byte confirmation). *(The D-150b clause was appended 2026-08-26 under D-155 …)*" — the contract prose records the delegation.
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1454-1458 (the NR table) and Phase E4 — the delegated confirmation/`hC` step exists as an operator step.
- producer: the magistrate at the desk. There is **no code** that recomputes `hM`/`hS` independently and refuses a mismatch — the recomputation is a hand-executed procedure. `grep -rn "recompute" scripts joulewise` finds no confirmation-table recomputation tool.
- transaction_relevant: yes — gates the changed-set subtraction and publication.
- note: B — the independence property (recompute, never accept the producer's report) is unenforceable by construction here; the check lives in the operator's hands with the runbook as the only instruction.

### D-150b · clause 2
- clause (verbatim): "the confirmation table keeps authority ED with the statement field recording this standing delegation and the recomputation evidence; Ed is NOTIFIED after each execution rather than blocked on."
- source: docs/decision_log.md:176
- status: A
- evidence: docs/contracts/d117_step6_confirmation_table.md:8-13 + the amendment record at the file's end — the prose amendment landed (D-155 operator fix), and D-155's index row states "`authority: ED` / `decision: YES` unchanged".
- evidence: joulewise/arm_readiness.py:10389-10390 — the marker verifier binds the table's contract identifier and required decision, never the table path/digest (consistent with authority staying ED).
- producer: `docs/contracts/d117_step6_confirmation_table.md` (the ONE normative home) — the demanded artifact is the contract prose, and it carries the text.
- transaction_relevant: yes.

### D-150b · clause 3
- clause (verbatim): "Remaining Ed-hands items: the pre-campaign reboot, window-night non-interference, and S-0 permission prompts (or the optional settings rule)."
- source: docs/decision_log.md:176
- status: A
- evidence: docs/process_traces/2026-08-22-t20/CHECKPOINT-2026-08-26.md — "Ed's open items (the only gates left before the window)" enumerates the venv relock, permission hygiene, cadence, and the night; docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:340-341 carries the no-reboot span.
- producer: the checkpoint + runbook (the demanded artifact is a recorded item list).
- transaction_relevant: yes.

---

## D-150a — Ed rulings 2026-08-23, packet items 5+7 (index row `docs/decision_log.md:177`; NO body section)

### D-150a · clause 1
- clause (verbatim): "NO-REBOOT COMMITMENT GRANTED, open-ended span, WITH a ruled PRE-CAMPAIGN REBOOT — … the laptop restarts AFTER S-0 passes and IMMEDIATELY BEFORE the real transaction's evidence stamping … the no-reboot span runs from that boot through campaign close."
- source: docs/decision_log.md:177
- status: A
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:340-341 — "**No reboot from Phase B onward.** D-150a grants an open-ended no-reboot span beginning at the pre-campaign reboot and running through campaign close."
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:88-91 — "**A reboot after this step voids all 33 receipts** … This is why the reboot in §2 Phase B happens where it [does]" — the reboot is placed at Phase B, before evidence stamping.
- producer: the runbook (operator instruction). No code refuses evidence authored across a boot boundary at this seam — but the boot-UUID binding is the pre-existing fuse; the clause itself demands only the ordering, which the runbook carries.
- transaction_relevant: yes — evidence stamping / arm freshness.

### D-150a · clause 2
- clause (verbatim): "ORIGIN-MAIN PUSH FREEZE ACCEPTED conditional on VISIBILITY, committed as: push notifications at every state change (transaction open/push-freeze ON; per-window \"T-0 at ~HH:MM, machine untouchable until morning\"; window closed; campaign done/freeze OFF), standing duration estimates … and the current state always carried in RUN_STATE's header line."
- source: docs/decision_log.md:177
- status: B
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1288-1292 — the notification table with the exact four state-change rows including "Campaign end | Campaign done; freeze **OFF** — sent at step 3 of the H5 record order".
- evidence: scripts/window_status.sh:34,95-98 — the freeze-span sentinel: `if [ -e "$COMMIT_FREEZE_SENTINEL" ]; then echo "freeze span open: status written locally, not published."; exit 0; fi` — the local-write channel survives the freeze.
- evidence (the RUN_STATE header sub-clause is DEVIATED, not installed as ruled): docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1132-1143 — "**H2 is struck, and the reason is mechanical, not stylistic.** D-150a asks that the current state be carried in `RUN_STATE.md`'s header line. Writing that line on transaction night would require a commit to `main` … So the header update moves to **H5's post-fixation tail**."
- producer: the magistrate sending notifications by hand; `scripts/window_status.sh` for the local status file. Nothing checks that a notification was actually sent at each state change.
- transaction_relevant: yes — the visibility condition Ed attached to the freeze.
- note: B. The push-notification half has no producer-side check at all (no send-receipt, no gate that refuses to advance a phase with an unsent notification). The RUN_STATE-header half is knowingly deviated from the ruled text and re-sited to H5 — recorded here because a reader of D-150a alone would expect a header line on the night and will not find one.

---

## D-150 — Ed rulings 2026-08-22, r5 V-7 packet items 1-4 (index row `docs/decision_log.md:178`, body `:10193-10207`)

### D-150 · clause 1 (item 1, mint license)
- clause (verbatim): "MINT LICENSE GRANTED — operationalized as LIVE PROMPTS AT ED'S HANDS, not a standing settings rule: each `_v4` freeze/projection command surfaces a permission prompt Ed approves at execution time (the most literal D-148.1 reading; no settings.local.json rule exists and none is required under this form)."
- source: docs/decision_log.md:178; :10196-10199
- status: B
- evidence: .claude/settings.local.json — 24 allow rules, including six blanket `-20260818` measurement-checkout allows and `Bash(gh pr merge:*)`, all still present today (read directly; file mtime 2026-08-19).
- evidence: docs/process_traces/2026-08-22-t20/w6-prompt-inventory.md (PR #200) — the W-6 inventory that verifies the six licensed ASK prompts are unmatched by any allow rule.
- evidence: docs/process_traces/2026-08-22-t20/CHECKPOINT-2026-08-26.md — "**Permission hygiene (W-6 NEEDS-ED)** … delete the six -20260818 blanket allows; suspend `Bash(gh pr merge:*)` from C11.1 until fixation is pushed" — still an OPEN Ed gate.
- producer: the Claude Code permission classifier, configured by `.claude/settings.local.json` (untracked, per-machine). No repository artifact enforces that the prompt actually fires.
- transaction_relevant: yes — the mint itself.
- note: B — the inventory (a document) verifies non-collision today, but nothing refuses a mint executed under a settings file that has since drifted, and the ruled cleanup has not been applied. The two seats' own catch (D-155 index row) was precisely that these allow rules "could suppress or bypass the D-150(1) live prompts."

### D-150 · clause 2 (item 2, horizon)
- clause (verbatim): "HORIZON = 168h (`604_800_000_000_000` ns, policy id `r1.execution_bound.freeze_generic_168h.v1`) for the ten generic freeze-time kinds … The four B-2 no-lane kinds stay 24h; the two T-0 kinds stay 6h (code-stamped)."
- source: docs/decision_log.md:178; :10199-10203
- status: A
- evidence: configs/arm_readiness/d117_row_registry_v2.json:11-12 (and 17 further occurrences) — `"freshness_policy_id": "r1.execution_bound.freeze_generic_168h.v1"`, `"horizon_ns": 604800000000000`.
- evidence: tests/test_arm_readiness_schemas.py:461-474 — enumerates the ten generic kinds (`ACCEPTANCE_OWNER, ACCEPTANCE_SUCCESSOR, ESTIMATOR_IDENTITY, MINT_TRUST, MULTICELL_MINT, PACK_AUTHENTICATION, REASON_CODE_COVERAGE, RECEIPT_ORACLE, RECOVERY_LEDGER_TEST, THREE_WINDOW_REGRESSION`) and asserts `horizon_ns == 604800000000000` + the policy id; then the four no-lane kinds at `86400000000000` and the two T-0 kinds at `21600000000000`. Removing any value reddens the suite.
- evidence: joulewise/arm_readiness.py:1717-1746 — the registry loader validates `horizon_ns` shape and the RE_DERIVABLE null rule at load.
- producer: `configs/arm_readiness/d117_row_registry_v2.json`, consumed by `joulewise/arm_readiness.py:1717`.
- transaction_relevant: yes — arm/consume freshness across the 168-hour campaign.

### D-150 · clause 3 (item 3, V6 marker)
- clause (verbatim): "V6 MARKER = OPTION (a) BUILD-AT-BOUNDARY, CUSTODY-EXTERNAL … r4-1's conditional two tracked paths do NOT engage; the changed-set contract stays at the cold-ratified 112 pending only the O-1 ruling."
- source: docs/decision_log.md:178; :10203-10206
- status: A
- evidence: scripts/build_family_marker.py:29 and scripts/verify_family_marker.py:23-31 — a `--phase` argument exists and "Nothing on disk can switch lanes -- only `--phase` can", i.e. the marker is built at a named boundary rather than read off tracked files.
- evidence: configs/arm_readiness/d117_row_registry_v2.json — allowlist length is exactly 112 (counted); `tests/test_arm_readiness_schemas.py:460` additionally asserts no `family_publication` path is in the allowlist, so the marker is custody-external by mechanical check.
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:776-779 — "The marker is built at `--head ATTESTATION_HEAD`".
- producer: `scripts/build_family_marker.py`; the 112-count and the marker's absence from the allowlist are both test-checked.
- transaction_relevant: yes — the publication boundary.

### D-150 · clause 4 (item 4, B-δ)
- clause (verbatim): "B-δ = UNATTENDED WORK ORDER AUTHORIZED — the D-127 privileged-scope + code change removing operator attestation from T-0 proceeds as its own gauntleted work order (registered as `T0-UNATTENDED-01`); `_v4` windows gate on its landing rather than on Ed's presence at each T-0."
- source: docs/decision_log.md:178; :10206-10207
- status: B (registration installed; the gate is NOT installed, and its scope was quietly narrowed)
- evidence: docs/process/state_kernel.json:3616,3654 — the row `T0-UNATTENDED-01` exists with `"status": "queued"` (read via json; the row's only status field is `queued`).
- evidence: docs/process/state_kernel.json:3853-3863 — the companion row records "Separate row by ruling: T0-UNATTENDED-01 owns evidence semantics only … Production windows depend on BOTH."
- evidence (narrowing): RUN_STATE.md:53-54 — "W-8 (§1.5 preflight) runs the evening before; **W-9 items gate the SHAKEDOWN, not the transaction.**" and `nr-synthesis-ruling.md:112-116` places `T0-UNATTENDED-01` in W-9, i.e. pre-shakedown. D-150(4) said `_v4` *windows* gate on its landing.
- producer: `docs/process/state_kernel.json` (registration: done). Nothing in `scripts/launch_window.py` or the arm path refuses a `_v4` window while `T0-UNATTENDED-01` is queued.
- transaction_relevant: yes — window launch / T-0.
- note: B. The registration clause is satisfied; the gating clause is a promise with no enforcement point, and the D-155 worklist reassigned it from "gates `_v4` windows" to "gates the shakedown". That reassignment is defensible (the transaction night has no T-0) but it is a narrowing of D-150(4)'s literal text and is not marked as an amendment anywhere in the decision log.

---

## D-152 — P06 characterization Ed-input rulings (index row `docs/decision_log.md:179`, body `:10219-10223`)

### D-152 · clause 1
- clause (verbatim): "C3 sizing_tolerance_ratio = 0.25 … a realized/predicted miss beyond ±25% returns indeterminate (characterization_effect_sizing_missed), never contradicted."
- source: docs/decision_log.md:179
- status: B
- evidence: configs/campaigns/metrology_v1/characterization_result_schema_v1.json:734 — `"decision_rule": "sizing_miss <= sizing_tolerance_ratio for every slot"`; :758-760 — `"limit_basis": "ruled"`, `"limit_source": "D-152 (Ed, 2026-08-24): sizing_tolerance_ratio=0.25"`.
- evidence: docs/contracts/analysis_plans.md:361 — the same value and reason code in the contract table.
- evidence (no producer): `grep -rn "characterization_result" joulewise scripts tests` returns **zero hits** — no code reads this schema, no reducer computes `sizing_miss`, and no test would fail if 0.25 became 0.9.
- producer: none found. The spec file is hand-authored; the criterion has no evaluator.
- transaction_relevant: no — the P06 characterization family (metrology_v1), not the `_v4` transaction.

### D-152 · clause 2
- clause (verbatim): "C4 tau_float = 1e-6 J … so 1e-6 J neither weakens the claim materially nor risks float false-positives."
- source: docs/decision_log.md:179
- status: B
- evidence: configs/campaigns/metrology_v1/characterization_result_schema_v1.json:842 — `"decision_rule": "max_i D_i <= tau_float"`; :870-872 — `"limit_source": "D-152 (Ed, 2026-08-24): tau_float=1e-6 J …"`.
- evidence: docs/contracts/analysis_plans.md:383 — the same value in the contract.
- evidence (no producer): as clause 1 — no code consumes the schema.
- producer: none found.
- transaction_relevant: no — characterization family.

### D-152 · clause 3
- clause (verbatim): "C5 held_out_reference_count = 6, two per window third … buys per-third containment comparison."
- source: docs/decision_log.md:179
- status: B
- evidence: configs/campaigns/metrology_v1/characterization_result_schema_v1.json:1206-1208 — `"limit_basis": "ruled"`, `"limit_source": "D-152 (Ed, 2026-08-24): held_out_reference_count=6, two per window third (~30-45 min total across the paper's windows)"`.
- evidence (no producer): the literal key `"held_out_reference_count"` appears **0 times** as a schema key in the file (only inside the ruling string); no window-plan generator reserves six reference members. `grep -rn "held_out_reference" configs joulewise scripts tests` → only the two ruling strings.
- producer: none found — no calibration plan or window planner allocates the six held-out members.
- transaction_relevant: no — characterization windows.
- note: this is the weakest of the four: the count is recorded as a ruling annotation but is not a schema field, so a window built tomorrow would not reserve the members.

### D-152 · clause 4
- clause (verbatim): "R1/R2 anchored limbs carry NO absolute fallback — the ratified dual-limb design governs: an unissued operative floor renders the anchored limb indeterminate with characterization_operative_floor_unavailable, decidable once floors issue; no invented constants. Spec updated in place (limit_basis: ruled, limit_source: D-152)."
- source: docs/decision_log.md:179
- status: A (for the "spec updated in place" sub-clause) / B (for the runtime behaviour)
- evidence: configs/campaigns/metrology_v1/characterization_result_schema_v1.json:382,459,574 — `"reason_code_on_limit_unavailable": "characterization_operative_floor_unavailable"` on all three anchored limbs.
- evidence: docs/contracts/characterization_result_schema_v1.md:320 — the reason code is registered in the contract's vocabulary table.
- evidence: docs/contracts/analysis_plans.md:316 — "D-152 ruled that this claim-anchored limb has NO absolute fallback".
- evidence (no producer): no code consumes the schema (as above), so nothing actually returns `indeterminate` at runtime.
- producer: the spec file (updated as ruled). Runtime evaluator: none found.
- transaction_relevant: no.

---

## D-153 — packet-5 amendment package (index row `docs/decision_log.md:180`, body `:10224-10228`)

Pointer target: `docs/process_traces/2026-08-24-packet5/04-MAGISTRATE-SYNTHESIS-PACKET5.md`.

### D-153 · clause A1
- clause (verbatim): "D-151 condition 3: \"window close\" = the r4-3 COMMIT-FREEZE CLOSE (after the LAST consuming window); the mint-side event is ALLOWLIST-CONTRACT CLOSURE at `PINSET_MINT_HEAD`; the fixation commit is the first commit after window close and carries EXACTLY the successor pinset SHA literal + its loud-fail guard — no mint-falsifiable assertion."
- source: docs/decision_log.md:180
- status: B
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:159-163 — "called `PINSET_MINT_HEAD`. **Two heads, and they are different commits.**"; :773-775 — "**`PINSET_MINT_HEAD`** is the **allowlist-contract closure head** (D-153 A6)".
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1200-1212 — the fixation commit's ruled slot and the trap of letting a `RUN_STATE` edit take it.
- evidence: no SHA literal or loud-fail guard exists in the tree yet (see D-151 clause 3).
- producer: the future fixation commit; the runbook is the only instruction. No code refuses a first-post-freeze commit that is not the fixation commit.
- transaction_relevant: yes.

### D-153 · clause A2
- clause (verbatim): "condition 1 widened: the pre-derivation candidate carries every digest-independent test consequence of the chain read (rename to `_all_governed_packs`; chain-derived corpus totals; presence-conditional NON-AUTHENTICATING successor shape assertion) — forcing rationale: without them the published-head suite is RED for the entire window, the defect O-1-E was killed for."
- source: docs/decision_log.md:180
- status: A
- evidence: tests/test_receipt_histsem.py:240-244 — `test_differential_self_test_all_governed_packs`, iterating `readiness._load_histsem_pinset(ROOT)` with the comment "nine rows before the successor is minted, twelve after, with no edit at the mint. The old name asserted a count that the mint falsifies (D-153 A2)."
- evidence: tests/test_receipt_histsem.py:253-260 — "Corpus totals are DERIVED FROM THE LOADED CHAIN, never literal 9/99 … no mint-falsifiable assertion may sit in a pre-derivation test."
- evidence: tests/test_receipt_histsem.py:168-217 — `test_successor_member_shape_when_present`, explicitly documented as presence-conditional and NON-AUTHENTICATING, skipping while the successor is absent.
- producer: the test module itself (the demanded artifact IS the test change); it is in the pre-derivation candidate on main today.
- transaction_relevant: yes — keeps the published-head suite green across the whole window.

### D-153 · clause A3
- clause (verbatim): "(A3, clarification) condition 4: published-head green required and achievable without the byte pin."
- source: docs/decision_log.md:180
- status: A
- evidence: tests/test_receipt_histsem.py:253 — `verify_all_receipt_histsem(ROOT, require_published=True)` passes today with only the v1 byte pin present, and the successor shape check skips when absent (:196) — i.e. published-head green is achievable without the successor's byte pin, exactly as clarified.
- producer: the test module; CI run 32970864856 (declared reviewed head 3c96b18f) is the recorded green.
- transaction_relevant: yes.

### D-153 · clause A4
- clause (verbatim): "condition 5 residual re-priced mint->post-window fixation (<=~8 days worst case) with per-phase controls named; ordinary-commit tail charged to the truth boundary / D-139 A1."
- source: docs/decision_log.md:180
- status: A
- evidence: MAGISTRATE-RULING-O1.md:63-88 — the amendment block cites D-153 A4 by name and carries the ≤ ~8 days figure and the per-phase controls, in the ONE home.
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1402-1404 — "D-153 A1 and A4 price the mint-to-fixation interval at up to about [eight] days".
- producer: the ruling documents (the clause demands a re-priced written residual, which landed).
- transaction_relevant: yes.

### D-153 · clause A5
- clause (verbatim): "`d117_step6_confirmation_table.md` prose repaired: `hC`'s standing source is transaction custody out of band for the life of the evidence, never any repository path; the fixation commit pins `hS` (archival byte pin), not `hC` — two-seat independent concurrence on the same prose defect."
- source: docs/decision_log.md:180
- status: A
- evidence: docs/contracts/d117_step6_confirmation_table.md:~79-85 — "The standing source of `hC` is transaction custody, out of band, for the life of the evidence; no repository path ever holds `hC`. The D-151 fixation commit pins `hS` — the successor pinset's own digest — which is a durable archival byte pin, not a source of `hC`".
- producer: the contract document (the demanded artifact).
- transaction_relevant: yes — the authenticator of the changed-set subtraction.

### D-153 · clause A6
- clause (verbatim): "condition 8: the changed-set window opens at the evidence-derivation head and CLOSES AT THE LAST CONSUMING ARM; vocabulary reserved accordingly."
- source: docs/decision_log.md:180
- status: B
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:299-301 — "**changed-set window, not the freeze span.** … the changed-set window opens at [the evidence-derivation head]".
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1178-1180 — "the **arm receipt id of the last consuming arm** — this closes the **changed-set window** (D-153 A6, whose normative text governs the unit)".
- producer: the magistrate's H5 declaration, recorded in `campaign-close.json`. No code computes or asserts the window's endpoints — the changed-set gate in `arm_readiness.py` evaluates per-arm against the registry allowlist and never learns that the window has closed.
- transaction_relevant: yes — defines the interval the whole allowlist contract governs.

### D-153 · clause A7 (registered limitation)
- clause (verbatim): "REGISTERED LIMITATION: a mid-campaign non-config cure forces a new family generation (luna)."
- source: docs/decision_log.md:180; 04-MAGISTRATE-SYNTHESIS-PACKET5.md:105
- status: B
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1116 — "| H4 | Record the registered limitation (D-153 W5): a mid-campaign non-configuration cure forces a new family generation. There is no patching a published `_v4`."
- evidence: TASK_QUEUE.md A92 (referenced from docs/process_traces/2026-08-27-t26/holm-m-consult/03-fable-seat.md:11 as "TASK_QUEUE `:648`, A92").
- evidence (gap): there is no `docs/limitations*.md` in the tree (`ls docs | grep -i limit` → nothing), and the paper draft carries no D-153 limitation line found by `grep -rn "mid-campaign non-config" docs/paper/`.
- producer: the runbook's H4 step (a future recording action). The limitation is not registered in any standing limitations register.
- transaction_relevant: yes — bounds what a mid-campaign cure can do to a live `_v4` campaign.

---

## D-154 — `pack_root` locality ruling (index row `docs/decision_log.md:181`, body `:10229-10236`)

Pointer target: `docs/process_traces/2026-08-25-packroot-consult/03-MAGISTRATE-RULING.md`.

### D-154 · clause R-1
- clause (verbatim): "For registry-governed generations at or above `family_publication_first_generation` (= 4), the `_load_freeze_reference` identity comparison treats `pack_root` as repository-relative structural identity (both sides projected; lexical validation of the recorded path — it need not exist; no normcase; non-repo packs keep refusing). `_v3` and earlier keep absolute semantics"
- source: docs/decision_log.md:181; 03-MAGISTRATE-RULING.md:23-35
- status: A
- evidence: joulewise/arm_readiness.py:6427-6435 — `generation = _pack_generation(pack_root.name)`; `successor_relative = registry.get("schema_version") == R1_ROW_REGISTRY_SCHEMA and generation >= _family_first_generation(registry)`; if not, the absolute comparison is kept.
- evidence: joulewise/arm_readiness.py:6442-6461 — `repository_relative_projection()` does lexical validation only (`is_absolute`, no `//`, no `.`/`..` parts, suffix match), never touching the filesystem.
- evidence: joulewise/arm_readiness.py:10035-10046 + :1836-1847 — the threshold is read from `freeze_evidence_lifecycle.successor_policy.family_publication_first_generation`, which the registry sets to 4 (verified in the JSON).
- producer: `joulewise/arm_readiness.py::_load_freeze_reference` (the replay/arm path). Landed as PR #192 (`bf88212e`).
- transaction_relevant: yes — freeze replay at arm time for the `_v4` family.

### D-154 · clause R-2
- clause (verbatim): "Refusal details become true, per branch. The content-mismatch branch keeps \"freeze receipt pack identity differs from committed pack bytes\" (now true — it fires only on content). The v4+ projection-mismatch branch gets its own detail naming the repository-relative location difference. The v3 absolute-mismatch branch gets a detail naming the location binding and the ruling that imposes it. No new reason codes (D-151 condition 1e)."
- source: docs/decision_log.md:181; 03-MAGISTRATE-RULING.md:37-44
- status: A
- evidence: joulewise/arm_readiness.py:6425 — content branch: `"freeze receipt pack identity differs from committed pack bytes"`, reached only after `pack_root` is excluded from the compared keys (:6420-6424).
- evidence: joulewise/arm_readiness.py:6433 — v3 branch: `"freeze receipt archival location differs; replay below the registry's family-publication generation threshold is location-bound (see the 2026-08-20 ruling)"`.
- evidence: joulewise/arm_readiness.py:6471 — v4+ branch: `"freeze receipt repository-relative pack location differs"`.
- evidence: all three are detail strings on the pre-existing error type; no new reason code was introduced (the three branches return details, not codes).
- producer: same function.
- transaction_relevant: yes.

### D-154 · clause R-3
- clause (verbatim): "The locality lens is re-sited, not retired (rule 11). The one real event the absolute comparison ever caught (T10 wtTXN mint) is better caught ONCE, AT MINT, against a declared target: a kernel row registers the mint-time measurement-checkout declaration check (new reason code + registry entry, fenced outside the S-0 window). Until it lands, the recorded absolute path remains in every receipt as provenance"
- source: docs/decision_log.md:181; 03-MAGISTRATE-RULING.md:46-53
- status: C
- evidence: docs/process/state_kernel.json — `MINT-CHECKOUT-DECLARATION-01` appears 4 times (row registered), but no code implements it: `grep -rn "MINT-CHECKOUT-DECLARATION" joulewise scripts tests` → no hits.
- evidence: no new reason code exists — `grep -rn "mint_checkout_declaration\|measurement_checkout_declared" joulewise scripts configs` → no hits.
- producer: none. The mint path (`joulewise/arm_readiness.py` freeze/mint) performs no declared-target comparison.
- transaction_relevant: yes — the mint. The ruling's own fallback ("the recorded absolute path remains in every receipt as provenance, and the T10 class remains detectable by inspection") is the current state; detection is now by human inspection only.
- note: registered-but-unimplemented is the ruling's own intended interim state, but the lens the ruling promised "is re-sited, not retired" is at this moment retired in practice — nothing catches the T10 class mechanically anywhere.

### D-154 · clause R-4
- clause (verbatim): "Estate 7 disposition: instrument failure; STRUCK. … Estate 7's custody is preserved read-only, and its positive results STAND AS EVIDENCE OF EXECUTABILITY … Estate 8 runs at the cured head after re-ratification."
- source: docs/decision_log.md:181; 03-MAGISTRATE-RULING.md:55-62
- status: A
- evidence: docs/process_traces/2026-08-22-t20/S0-COMPLETION-RECORD.md + CHECKPOINT-2026-08-26.md — "S-0 clone-proof: COMPLETE (estate 10, full green through §5) … Ten estates; every earlier halt was a real instrument defect, cured on main." Estates 8-10 ran after the cure, as ruled.
- producer: the S-0 runsheet execution record.
- transaction_relevant: yes — S-0 is the transaction's clone proof.

### D-154 · clause R-5
- clause (verbatim): "Implementation gauntlet (C-028): Sol implements (WRITE_SCOPE: joulewise/arm_readiness.py + the two test modules the seats name), with the seats' combined regression list: cross-clone idempotent replay green; wrong repo-relative location refuses; every non-pack_root content mutation still refuses with the byte-mismatch detail; v3 stays location-bound; histsem foreign-root PASS retained; the mutant restoring the absolute term in the v4+ branch goes red."
- source: docs/decision_log.md:181; 03-MAGISTRATE-RULING.md:64-76
- status: A
- evidence: git log — `bf88212e D-154: successor-scoped repository-relative pack_root identity (freeze replay) (#192)` merged, with the fresh cross-model refuter the ruling required (recorded at `6601b69c`).
- evidence: joulewise/arm_readiness.py:6420-6472 — the three branches the regression list targets all exist and are distinguishable, so the mutant test (restoring the absolute term in the v4+ branch) has a real target.
- producer: PR #192.
- transaction_relevant: yes.
- note: I did not execute the suite; the regression battery's existence is inferred from the merged PR and the branch structure. Marked A on the code evidence; the individual regression assertions in `tests/test_arm_readiness_lifecycle.py` were not read line by line.

### D-154 · clause R-6
- clause: scorekeeping (rule 2) — NOT an implementation clause (pure process record). Skipped per the brief.

### D-154 · clause R-7 (index-row tail)
- clause (verbatim): "BACKFILLED 2026-08-27 (T26): the ruling was custodied and cited as D-154 from 2026-08-25 but never indexed here — a consistency-sweep miss, not a new decision."
- source: docs/decision_log.md:181
- status: A
- evidence: docs/decision_log.md:181 — the index row now exists; git log `d9170fff Decision log: D-156 supersession write-time refusal ruling; backfill the missing D-154 index row` and `3109c0dc … D-154 body ordered before D-155`.
- producer: the decision log itself.
- transaction_relevant: no — bookkeeping.

---

## D-155 — NR adjudication package, the thirteen pre-window rulings (index row `docs/decision_log.md:182`, body `:10237-10246`)

Pointer target: `docs/process_traces/2026-08-22-t20/nr-synthesis-ruling.md`.
Thirteen items = NR-1..NR-13. **Eleven ruled; NR-5 and the cadence half of
NR-9 remain OPEN by the ruling's own text.** Cross-checked against the landed
worklist: W-0..W-7 done (`CHECKPOINT-2026-08-26.md`), W-8 is the night-before
preflight, W-9 is pre-shakedown, W-10 was added by D-157.

### D-155 · clause NR-1
- clause (verbatim): "branch A: `/Users/edr/JouleWise-measurement-20260813` fast-forwarded (ancestry verified); `-20260818` rejected on three grounds including its blanket allow rule; a fresh checkout is the NAMED FALLBACK if the venv relock cannot reach the lock."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:44-51
- status: B
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:199 — "`/Users/edr/JouleWise-measurement-20260813`**, fast-forwarded to the reviewed [head]"; :261, :408, :557 use the same path.
- evidence: CHECKPOINT-2026-08-26.md — "W-5: measurement checkout /Users/edr/JouleWise-measurement-20260813 fast-forwarded to 3c96b18f, clean tree, reviewed_main exact_match true (run via the real predicate), zero _v4 output present." — executed.
- evidence (the gap): .claude/settings.local.json still carries all six `-20260818` blanket allow rules, including `Bash(cd /Users/edr/JouleWise-measurement-20260818 && *)` and `Read(//Users/edr/JouleWise-measurement-20260818/**)`. The ruling rejected `-20260818` partly *because of* those rules and they have not been deleted.
- producer: the operator, per the runbook. Nothing refuses a session launched against `-20260818`.
- transaction_relevant: yes — the checkout the mint runs from.

### D-155 · clause NR-2
- clause (verbatim): "branch A: pull-into-dev -> push origin -> fetch-back, four-way equality asserted by RUNNING `reviewed_main`, never by eye; a fetch is licensed inside the freeze span, a commit/push/branch-move is not; the invented `file://` form dropped."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:36-43
- status: A
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:821 — "**RULED (D-155, NR-2): pull-into-dev → push → fetch-back.**"; :833 — "**Assert the four-way equality by running `reviewed_main`, not by comparing [by eye]**"; :1489 — "The earlier draft's `file://` command form is dropped — it appears in no source."
- evidence: `grep -n "file://" docs/process_traces/2026-08-22-t20/real-transaction-runbook.md` → no command form remains (only the :1489 record of its removal).
- evidence: joulewise/arm_readiness.py `reviewed_main` is a real predicate consumed by `scripts/capture_t0_step.py:292` (`reviewed = readiness.reviewed_main(pack_root)`), so "running it" is mechanically possible and is what the T-0 capture already does.
- producer: the runbook (operator procedure) + `readiness.reviewed_main` as the executed predicate.
- transaction_relevant: yes — publication topology.

### D-155 · clause NR-3
- clause (verbatim): "branch A, push-then-build, with Phase E reordered E1 build -> E3 render -> E4 delegated confirmation/`hC` -> E2 verify -> E5 promote (a publication-phase verify REQUIRES the confirmation pair); r4-3 amended with a dated marker, never silently."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:31-35
- status: A
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md Phase E preamble (around :900-1000) — the reordered phase with `--phase publication` at :908-911 and the confirmation pair required for the verify.
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1523 — "**RULED (D-155): branch A — `--phase publication` for both the build and the verify**".
- evidence: the dated amendment convention is realized elsewhere in the same style (MAGISTRATE-RULING-O1.md:63 "**AMENDED 2026-08-26 under D-155 (NR-7)**").
- producer: the runbook + `docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING-r3.md` (the r4-3 home).
- transaction_relevant: yes — the publication phase.
- note: I verified the Phase E ordering statements in the runbook and the `--phase publication` line, not each of E1..E5's step rows individually.

### D-155 · clause NR-4
- clause (verbatim): "branch A: marker build AND verify `--phase publication`; the §1.3 candidate manifest is STILL PRODUCED because C9 consumes it for custody-tool digests."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:52-56
- status: A
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1523 — "with no `--candidate-manifest` on either. The §1.3 candidate manifest is **still produced**, because C9 consumes it to authenticate the executing custody tools; only the marker stops consuming it."
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:373 — the checklist row "The mechanical candidate manifest generated from committed bytes at the [reviewed head]".
- evidence: joulewise/arm_readiness.py:10429 — `{"custody_tools": {"<repo-relative tool path>": "<64 hex sha256>"}}` — the C9 consumer the guard protects.
- evidence: scripts/build_family_marker.py:29, scripts/verify_family_marker.py:23 — both carry `--phase`.
- producer: the runbook step + the two marker scripts.
- transaction_relevant: yes — publication + custody-tool authentication.

### D-155 · clause NR-6
- clause (verbatim): "branch B: dry-run ceremony x3, NO real arm; `file-09-probe P1/P2/P3` STRUCK AS SPECIFIED (P3 requires the arm B-4 forbids) and replaced by named assertions over the dry-run receipts, with P3 discharged at the shakedown GO receipt and arm-side U11 at the shakedown arm; the Sol seat's read-only reformulation of P3 recorded as DISSENT and declined"
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:66-79
- status: A
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1054-1058 — "## Phase G — The dry-run ceremony (MAGISTRATE) … **RULED (D-155, NR-6): the dry-run ceremony, and no real arm.**"
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1071 — "**`file-09-probe P1/P2/P3` is struck as specified** (D-155, NR-6)."; :1093 — "**P3 is recorded as discharged at the shakedown GO receipt**"; :1100 — arm-side U11 at the "**shakedown arm**".
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1090 — the named receipt assertion "the same-head pack-binding check PASS, `head_binding == ATTESTATION_HEAD`".
- producer: the runbook (the demanded artifact is the ceremony's specification, and it landed with the replacement assertions named).
- transaction_relevant: yes — the transaction night's only arm-adjacent exercise.

### D-155 · clause NR-7
- clause (verbatim): "D-153 A4 governs; condition 5 RE-SCOPED, not struck, into two sub-intervals … ONE home `MAGISTRATE-RULING-O1.md` condition 5, with the D-151 index row clarified as a pointer."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:80-86
- status: A
- evidence: MAGISTRATE-RULING-O1.md:63-88 — the dated amendment block and the restated condition 5 (see D-151 clause 5).
- evidence: docs/decision_log.md:175 — "CLARIFIED 2026-08-26 by D-155/NR-7 … This row is a paraphrase; the ONE home for the re-scoped condition 5 is `MAGISTRATE-RULING-O1.md`".
- producer: the two documents.
- transaction_relevant: yes.

### D-155 · clause NR-8
- clause (verbatim): "mechanical campaign-close declaration by the magistrate with an ED ESCAPE for early termination/waivers/abandonment; canonical `campaign-close.json` in transaction custody; STRICT record order — declaration -> freeze-off -> notification -> THE FIXATION COMMIT FIRST -> only then any bookkeeping."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:87-96
- status: C (the artifact) / A (the procedure)
- evidence (procedure, A): docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1191-1212 — the numbered record order with "4. **THE FIXATION COMMIT — first, before anything else.**" and the explanation of the trap at :1211-1212.
- evidence (procedure, A): docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1178-1180 — the two closing coordinates (last consuming arm id; window-consume completion).
- evidence (artifact, C): docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1122 — "because one ruled artifact does not exist yet: `campaign-close.json`, written at campaign close (H5), days later." There is no schema, no writer, and no validator: `grep -rn "campaign-close" joulewise scripts tests` → no hits.
- producer: the magistrate at H5, by hand. No script mints or validates `campaign-close.json`, and nothing refuses a close declaration whose executed arm set differs from the published plan.
- transaction_relevant: yes — campaign close and the fixation slot.
- note: the ruling names it "canonical", which for every other canonical artifact in this repo means a D-134 schema + validator. Here it is prose only.

### D-155 · clause NR-10
- clause (verbatim): "six ruled prompts stand PLUS a mandatory pre-window prompt inventory (ALLOW/ASK/DENY table with exact strings, cwd and the `python3` vs `python` spelling trap); if the broad allows would swallow a licensed command, ED narrows them — no agent self-modification of settings."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:106-112
- status: B
- evidence: docs/process_traces/2026-08-22-t20/w6-prompt-inventory.md (52 KB, merged as PR #200 `b96d0676`) — the inventory exists.
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:388 — checklist row "**The prompt inventory delivered to Ed** (RULED, D-155, NR-10; work [order W-6])"; :557 — the `python3` vs `python` interpreter trap recorded; :408 — the `cd /Users/edr/JouleWise-measurement-20260813 && …` cwd-form note.
- evidence (the gap): the narrowing half is UNEXECUTED — .claude/settings.local.json still carries the six `-20260818` blanket allows and `Bash(gh pr merge:*)`; CHECKPOINT-2026-08-26.md lists this as open Ed gate #2, including "note Phase A (evening before, Ed absent) contains ~12 unlicensed ASK rows".
- producer: Ed, editing `.claude/settings.local.json` by hand. Nothing re-checks the inventory against the live settings file at transaction time.
- transaction_relevant: yes — whether the D-150(1) mint prompts actually fire.

### D-155 · clause NR-11
- clause (verbatim): "branch D at BOTH parsers: `PASS`/`Tree-Oid` stay exactly-once, `Pack-Sha256` becomes non-empty, duplicate-free, membership of the arming pack's digest; zero refusal-registry cost; five-case regressions at each site; three-trailer producer in `window_runbook.md` §5C; no zero-code path exists (branch E verified mechanically empty three times)."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:18-30
- status: A
- evidence: joulewise/arm_readiness_evidence_t0.py:931-951 — `_derive_terminal_review` parses the three trailer names, requires `PASS` and `Tree-Oid` exactly-once (`trailers.get(name) != [value]`), and refuses on `len(set(packs)) != len(packs) or context.pack_sha256 not in packs`; comment at :939 "An empty Pack-Sha256 list refuses via the membership clause below."
- evidence: scripts/capture_t0_step.py:288-325 — the TWIN parser, byte-for-byte the same predicate, refusing `evidence_author_t0_capture_terminal_review_missing`. This is the seat-discovered second call site, and it is cured.
- evidence: docs/phase_2/window_runbook.md:842,852-853,866,888-890 — the §5C producer emits `JouleWise-Terminal-Review: PASS`, `-Tree-Oid: $TREE_OID`, and one `-Pack-Sha256: $PACK_SHA256` per pack.
- evidence: tests/test_arm_readiness_evidence_t0.py and tests/test_capture_t0_step.py both contain `Pack-Sha256` cases (`grep -rln "Pack-Sha256" tests/` → exactly these two files).
- evidence: no new reason code — both sites reuse the existing `..._terminal_review_missing` / `..._terminal_review_record_missing` codes ("zero refusal-registry cost").
- producer: the operator's commit trailers (produced per `window_runbook.md` §5C) — and BOTH consumers refuse at write time of the evidence, which is the producer seam for T-0 evidence.
- transaction_relevant: yes — T-0 evidence authoring and capture.
- note: this is the strongest A in the group; the twin-parser cure is exactly the D-157 "another missed call site" shape caught before the window. Landed PR #199 (`3c96b18f`).

### D-155 · clause NR-12
- clause (verbatim): "branch B: ONE magistrate-executed (D-150b), tree-preserving attestation commit AFTER the mint; `ATTESTATION_HEAD` = published head, `PINSET_MINT_HEAD` = allowlist-closure/`hS` head; every step naming 'the head' says which."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:24-30
- status: A
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:159-163 — "**Two heads, and they are different commits.**"
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:767-769 — "| C11.2 | MAGISTRATE | Assert the preconditions: `HEAD == PINSET_MINT_HEAD`, working tree clean …"; "| C11.4 | MAGISTRATE | Record the resulting head as **`ATTESTATION_HEAD`**. Re-run the closure diff … must still be exactly the 112 allowlisted paths. An empty commit adds no paths, so the number is unchanged — but the assertion is re-run rather than reasoned about."
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:773-779, :854-855, :911, :994, :1018-1019, :1084, :1090 — every "the head" mention is disambiguated.
- producer: the runbook (the demanded artifact is the disambiguated procedure, and C11.4 re-runs the closure assertion mechanically rather than reasoning).
- transaction_relevant: yes.

### D-155 · clause NR-13
- clause (verbatim): "code guard landing BEFORE Phase C1 — the binding gate is the changed-set window, not the freeze span: custody-external sentinel, refuse-before-write, byte-identical out-of-span behaviour, two-branch regression; D-150a visibility unaffected (the channel is the push notification, not the git push)."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:57-65
- status: A
- evidence: scripts/window_status.sh:34 — `COMMIT_FREEZE_SENTINEL="${JOULEWISE_COMMIT_FREEZE_SENTINEL:-/Users/edr/JouleWise-window-custody/COMMIT_FREEZE_OPEN}"` — custody-external default with env override, exactly as ruled.
- evidence: scripts/window_status.sh:95-98 — refuse-before-write of the git side: `if [ -e "$COMMIT_FREEZE_SENTINEL" ]; then echo "freeze span open: status written locally, not published."; exit 0; fi` — placed BEFORE `cd "$REPO"; git add …` at :100-101.
- evidence: tests/test_window_status_guard.py:49-64 — `test_present_sentinel_writes_status_without_git_publication` asserts HEAD unchanged, index empty, file untracked, and the exact message; :65-80 `test_absent_sentinel_commits_status_as_before` asserts the commit count increments and the subject is unchanged (the two-branch regression, byte-identical out-of-span behaviour).
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1143 — "the window status publisher still writes `WINDOW_STATUS.md` **locally** under the C11.1 sentinel guard. What is withheld until fixation is only the *published* copy."
- producer: `scripts/window_status.sh` — the writer itself refuses the publication branch.
- transaction_relevant: yes — the commit freeze that protects every armed pack.

### D-155 · clause NR-5 (OPEN)
- clause (verbatim): "STILL OPEN: NR-5 (does the real lane re-run the §4 probe battery)"
- source: docs/decision_log.md:182; real-transaction-runbook.md:1441
- status: C
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1453 — "| NR-5 | Does the real transaction re-run the §4 probe battery? | **OPEN** | — |"; :1538 the §7 section header "### NR-5 — Does the real transaction re-run the §4 probe battery?"
- producer: none — no ruling exists, so no artifact is owed yet.
- transaction_relevant: yes — determines the night's runtime budget and what evidence the transaction produces.
- note: recorded as C because it is an enumerated pre-window item with no disposition, not because a ruled thing was missed. It is a KNOWN open, surfaced in the runbook's own gap table.

### D-155 · clause NR-9 cadence (OPEN)
- clause (verbatim): "and NR-9's notification cadence, which is Ed's one-word question (recommendation: immediate)."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:113-118
- status: C
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1457 — "| NR-9 | … | **PART-RULED** — the contract prose is amended and the delegation is live; **the cadence is Ed's, still open** |"
- evidence: CHECKPOINT-2026-08-26.md — "**One word on notification cadence** (NR-9)" listed as open Ed gate #3.
- producer: none pending Ed's word.
- transaction_relevant: yes — the D-150a visibility condition's timing.

### D-155 · clause OP-1 (operator fix: venv relock)
- clause (verbatim): "fresh-venv relock (preserve `.venv` as `.venv.pre-v4`, rebuild from the lock's canonical constraints form) accepted on an EMPTY 37-line diff, not a version print, with wheel-unavailability falling back to the fresh checkout"
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:120-127
- status: B
- evidence: docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:263 — "1. `mv .venv .venv.pre-v4` — the old environment is preserved, so rollback [is possible]" in the §1.1 checklist.
- evidence: CHECKPOINT-2026-08-26.md — "**Venv relock** at -20260813 (~10 min): fresh-venv method in the runbook §1.1 checklist (mv .venv .venv.pre-v4 → rebuild from env/mac-measurement-lock.txt constraints → empty diff vs the 37-line lock). Wheel unavailability ⇒ fall back to a fresh checkout (NR-1 C)." — still open Ed gate #1.
- producer: Ed at the machine, per the checklist. No script performs or verifies the relock, and nothing refuses a transaction run against a `.venv` that does not diff empty against the lock.
- transaction_relevant: yes — the environment the mint executes in.

### D-155 · clause OP-2 (operator fix: step-6 contract prose)
- clause (verbatim): "the step-6 contract prose amended to record the D-150b standing delegation with independent recomputation of `hM`/`hS` (`authority: ED` / `decision: YES` unchanged)."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:128-133
- status: A
- evidence: docs/contracts/d117_step6_confirmation_table.md:8-13 — the amended authority sentence with the dated amendment marker "*(The D-150b clause was appended 2026-08-26 under D-155; the sentence previously ended at \"D-151 conditions 2 and 7.\" See the amendment record at the end of this contract.)*"
- evidence: docs/contracts/d117_step6_confirmation_table.md:~14-16 — a second dated marker for the superseded "Ed confirms the digest `hC` over those exact final bytes." sentence.
- producer: the contract document.
- transaction_relevant: yes.

### D-155 · clause W (pre-window worklist)
- clause (verbatim): "PRE-WINDOW WORKLIST W-0..W-9 in the synthesis; earliest credible transaction night 2026-08-28, gated on W-2 clearing its gauntlet first-pass."
- source: docs/decision_log.md:182; nr-synthesis-ruling.md:135-152
- status: A (with a D-157 supersession on the date)
- evidence: W-0 `nr-synthesis-ruling.md` + both seats custodied (`d15c7506`); W-2 PR #199 `3c96b18f`; W-3 PR #198 `a44f4129`; W-4 reviewed head declared 3c96b18f, CI run 32970864856; W-5 measurement checkout fast-forwarded; W-6 PR #200 `b96d0676` → `w6-prompt-inventory.md`; W-7 full suite rc=0 in 2084 s. All recorded in CHECKPOINT-2026-08-26.md and corroborated by `git log --oneline`.
- evidence: W-8 not run by design (evening before); W-9 items are pre-shakedown (RUN_STATE.md:53-54).
- evidence (date superseded): RUN_STATE.md:44-50 — "**T26 (2026-08-27) AMENDMENT — W-10 ADDED, the night is gated on it (D-157)** … earliest credible night ~2026-08-29/30."
- producer: the merged PRs.
- transaction_relevant: yes.
- note: the 2026-08-28 date in D-155's index row is now false; D-157 moved it. The decision-log row carries no amendment marker for it (the amendment lives only in RUN_STATE.md and D-157's own row).

---

## D-156 — supersession write-time refusal (index row `docs/decision_log.md:183`, body `:10247-10256`)

### D-156 · clause 1 (the core refusal)
- clause (verbatim): "the supersession recorder REFUSES, before row construction, any write whose `bundle_id` already has a recognizable row in the target campaign log — unconditionally, keyed on `bundle_id` within one log, with NO requirement that the existing row validate (an invalid competing disposition never licenses a second write)"
- source: docs/decision_log.md:183
- status: **C — NOT INSTALLED**
- evidence: scripts/run_campaign.py:5449-5466 — the supersession writer builds the row (`row: dict[str, Any] = {"schema_version": OCCURRENCE_SUPERSESSION_SCHEMA, "record_type": "campaign_occurrence_supersession", "timestamp": utc_timestamp(), …}`), computes `entry_sha256`, validates the constructed entry, then `append_log(log_path, row, lock_token=lock_token)`. There is **no** read of the existing log for a prior `bundle_id` row anywhere before that append.
- evidence: the only pre-append checks are at :5423-5437 — "supersession requires exactly one duplicated ordinary-run membership group" and "exactly one canonical present bundle and no moved copy inside --runs-dir" — neither looks at the campaign log for an already-recorded supersession.
- evidence: `grep -rn "campaign_occurrence_supersession_already_recorded" joulewise scripts tests configs docs` → the ONLY hit is `docs/decision_log.md:183`. The reason code exists in the ruling and nowhere else.
- evidence: the recognizability predicate the ruling keys on already exists as a reader — `joulewise/whole_window.py:2742-2795 supersession_entry_validation_results` — but it has no caller on the write path (`grep -rn "supersession_entry_validation_results" scripts joulewise` → definition + `whole_window.py` internals only).
- producer: `scripts/run_campaign.py` supersession subcommand (the `append_log` at :5466). The check is missing exactly there.
- transaction_relevant: yes — the campaign log is consumed by the whole-window verdict and the cooldown join at the claim edge; a second row produces the cross-consumer divergence the ruling describes.

### D-156 · clause 2 (reason code registration)
- clause (verbatim): "registered reason code `campaign_occurrence_supersession_already_recorded` on the existing `LaunchLineageError` pattern; no consumer change; no byte repair owed."
- source: docs/decision_log.md:183
- status: C
- evidence: as clause 1 — the code string exists only in the decision log. `grep -rn "LaunchLineageError" scripts/run_campaign.py joulewise` finds the pattern but no new member.
- producer: none.
- transaction_relevant: yes.

### D-156 · clause 3 (Q1 residual — chained-supersession schema as a QUEUED row)
- clause (verbatim): "Q1 later failure of an already-selected occurrence → A (fresh root / non-claim disposition) now, chained-supersession schema minted as a QUEUED row"
- source: docs/decision_log.md:183
- status: C
- evidence: docs/process/state_kernel.json — `SUPERSESSION-DUP-REFUSAL-01` appears 4 times; no chained-supersession row exists (`grep -c "chained.supersession"` over the kernel → 0).
- evidence: docs/decision_log.md:10251-10254 (tail body) — "Two queued rows owed by the residuals: a chained-supersession schema (Q1-B) and the cross-consumer divergence cure (Q4-B); **the lieutenant drafts their kernel rows in the PR for the magistrate to register.**" The PR has not landed, so neither row exists.
- producer: none.
- transaction_relevant: yes — claim-edge disposition of a failed selected occurrence.

### D-156 · clause 4 (Q3 — off-machine scan MANDATORY before consumption)
- clause (verbatim): "Q3 off-machine Window B/C per-`bundle_id` scan → A MANDATORY before any consumption of those corpora, documented in runbook §11"
- source: docs/decision_log.md:183
- status: C
- evidence: `grep -n "per-bundle_id|bundle_id.*scan|Window B/C" docs/phase_2/window_runbook.md` → no hits. There is no §11 scan step; the runbook was never edited for this.
- evidence: no scanning script exists — `grep -rn "bundle_id" scripts/*.py | grep -i scan` → no hits.
- producer: none. Nothing refuses consumption of the Window B/C corpora without the scan.
- transaction_relevant: yes — the consumption edge for those corpora.

### D-156 · clause 5 (Q4 — cross-consumer divergence cure as its own queued row)
- clause (verbatim): "Q4 the cross-consumer divergence → B its own queued row (a fail-closed consumer change does not ride a write-time-guard PR)"
- source: docs/decision_log.md:183
- status: C
- evidence: as clause 3 — the queued row does not exist in `docs/process/state_kernel.json`.
- producer: none.
- transaction_relevant: yes — the divergence is between the whole-window membership selector and the cooldown join, both claim-edge consumers.

### D-156 · clause 6 (Q5)
- clause (verbatim): "Q5 this entry is the ruling the row's acceptance requires."
- source: docs/decision_log.md:183
- status: A
- evidence: docs/decision_log.md:183 exists (committed `d9170fff`); docs/decision_log.md:10247-10256 is the tail anchor.
- producer: the decision log.
- transaction_relevant: no — bookkeeping precondition.

**D-156 summary: the entire ruling is UNIMPLEMENTED.** It was ruled 2026-08-27
and its PR ("lands with the SUPERSESSION-DUP-REFUSAL-01 PR", tail body
`:10250`) has not merged — `git log --oneline -45` shows no such commit. This is
the freshest instance of the D-157 shape in the group, and the one with the
shortest half-life: the packet is written, the code is not.

---

## D-157 — gamma analysis manifest inadmissible as generated, W-10 (index row `docs/decision_log.md:184`, body `:10257-10263`)

**Reference instance, not a new finding.** All six rulings are C by
construction — they are the CURE for the already-diagnosed defect, scheduled as
W-10 on stream S8 (branch `fix/d139-a2-gamma-families`). I verified the defect
first-hand rather than taking the ruling's word.

Defect verified at the bench:
- configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:948-953 — the decode cell still emits `"multiplicity": "Holm"`, `"family_m": 1`, with `"multiplicity_note": "family_m=1 is contingent on unresolved decode/prefill family-cardinality ratification; see the prefill_p256 cell's multiplicity TODO."`
- configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:961-975 — the `prefill_p256` cell's `"test"` is `empty_slot("TODO(lead authority): D-122 requires the arm but does not pin …")`.
- no `families` block: `grep -n "\"families\"" configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py` → no hits.
- the prospective validator has NO callers on the freeze path: `grep -rn "validate_prospective_analysis_manifest_v3" --include=*.py .` returns only `tests/test_analysis_manifest_v3.py` (12 hits) and `joulewise/analysis_manifest_v3.py` itself (:1885, :2777, :2816, :2838, :3759, :3876, :4178). **Zero callers in `scripts/` and zero in any other `joulewise/` module.** This is the canonical B-not-A shape the brief names.
- the consumption edge that would refuse: joulewise/analysis_engine/artifact.py:1573-1576 — `if isinstance(family["m"], bool) or not isinstance(family["m"], int): errors.append(…)` / `elif ids is not None and family["m"] != len(ids): errors.append(f"{where}.m: must equal frozen contrast count")`.

### D-157 · clause R-1
- clause (verbatim): "R-1 W-10 — production resolver installs D-139 A2 verbatim + full prospective top-key set, plan-tree digest recomputed, regenerate"
- source: docs/decision_log.md:184
- status: C — cured-in-plan as W-10
- evidence: the generator evidence above; branch `fix/d139-a2-gamma-families` is not merged (`git log --oneline -45` has no such commit).
- producer: `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py`.
- transaction_relevant: yes — gates the transaction night.

### D-157 · clause R-2
- clause (verbatim): "R-2 close the CLASS — the freeze/readiness path runs the prospective validator and null-p multiplicity admission and REFUSES the mint on any finding (third instance this session of the contract-required-input-with-no-check shape)"
- source: docs/decision_log.md:184
- status: C — cured-in-plan as W-10
- evidence: the zero-caller grep above — the freeze path does not call the validator today.
- producer: the mint/freeze path in `joulewise/arm_readiness.py` (the missing call site).
- transaction_relevant: yes — the mint refusal.
- note: this is the class-closing clause. Until it lands, D-151 clause 7's fixed-point rule and this sweep's whole premise share the same unguarded seam.

### D-157 · clause R-3
- clause (verbatim): "R-3 mint-path change ⇒ S-0 re-runs as ESTATE 11 before the transaction"
- source: docs/decision_log.md:184
- status: C — cured-in-plan as W-10
- evidence: docs/process_traces/2026-08-22-t20/S0-COMPLETION-RECORD.md records estate 10 as the completion; RUN_STATE.md:47-49 — "S8 installs the resolver + a mint-time admission refusal; S-0 re-runs as estate 11".
- producer: the S-0 runsheet execution.
- transaction_relevant: yes.

### D-157 · clause R-4
- clause (verbatim): "R-4 post-window analysis-side m=2 REJECTED (post-hoc family selection; bytes refused regardless)"
- source: docs/decision_log.md:184
- status: A
- evidence: joulewise/analysis_engine/artifact.py:1573-1576 — the consumption edge already refuses `m != len(contrast_ids)`, so an analysis-side m=2 over a manifest minted with m=1 is refused by existing code. The clause rules OUT a path, and the code already forecloses it.
- producer: `joulewise/analysis_engine/artifact.py` claim-time validation.
- transaction_relevant: yes — the claim edge.

### D-157 · clause R-5
- clause (verbatim): "R-5 changed-set consequence reported by S8, pinset/D-151 collision returns as NEEDS-RULING"
- source: docs/decision_log.md:184
- status: C — cured-in-plan as W-10
- evidence: no S8 report exists in `docs/process_traces/2026-08-27-t26/` (`ls` shows `holm-m-consult/` and `supersession-dup-ruling-packet.md` only).
- producer: stream S8.
- transaction_relevant: yes — regenerating the gamma pack changes bytes inside the 112-path allowlist contract.

### D-157 · clause R-6
- clause (verbatim): "R-6 earliest credible night moves to the first free night after W-10 merges and estate 11 is green (~2026-08-29/30)."
- source: docs/decision_log.md:184
- status: A
- evidence: RUN_STATE.md:44-50 — "**T26 (2026-08-27) AMENDMENT — W-10 ADDED, the night is gated on it (D-157)** … earliest credible night ~2026-08-29/30."
- producer: RUN_STATE.md (the demanded artifact is the recorded date move).
- transaction_relevant: yes.
- note: D-155's own index row still says "earliest credible transaction night 2026-08-28" with no amendment marker (see D-155 clause W).
