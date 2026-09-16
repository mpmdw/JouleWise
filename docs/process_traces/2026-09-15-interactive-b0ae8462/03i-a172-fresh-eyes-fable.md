# A172 ARM-RETRY-CLASS-01 — fresh final-head review (Fable, row-10 shape)

Head reviewed: `feat/2026-09-15-arm-retry-class` @ `2daf2b0b` (three commits over `0ba6ce54`; diff touches exactly the four WRITE_SCOPE files). Copy at `scratchpad/seats/a172-fresh-copy`; nothing outside it touched.

## 1. Rulings compliance — every ruling met; one stale residue

- Single home = module: enumeration `joulewise/arm_retry.py:21-77`, `classify_abort` :86, `retry_allowed` :97, `render_policy` :193. No `arm_retry_policy.json`, no `MAGISTRATE_RELAUNCH_PROMPT.md` edit (diff stat), no exec-from-Markdown at arm time — the foreground block imports the module (`derivation_night_runbook.md:1779`).
- Both doc blocks byte-identical to `render_policy()` (test :113-121, green).
- 03e R1: clearance defined over directive issues / `standdown.request` / relayed NO; unreadable thread = recorded limitation (module :116-121, block :210, runbook step 4 :1636-1638). R2: no `install_spans` input, no `outside_same_or_next_span` denial; informational "subsumed" sentence :208. R3: runbook step 5 :1652-1654. R4: notice well-formedness :149-153 precedes `notice_reused` :168.
- 03b R2 sentence verbatim in NIGHT_HANDBACK :139 (test :123-127). 22 gate/driver codes pinned against the live registry (test :97-98), installer table pinned against the live §1.3 table (test :107-111), `HOLD_CENSUS`/`slot_refused` present.
- Ed's directive: every denial traces — `install_closed` :180, `plan_age` :178 (PLAN_MAX_AGE_S, dominated `now-authored` accepted per 03e), `retry_spacing` :173 (60 s), notice binding/timing/reuse/abort-mismatch :149-187 (per-attempt notice), `cold_gate_evidence`/`cold_gate_history` :141-164, `owner_no` :144. No count cap, no notice-age cap, no span ceiling.
- **Residue (should-fix S1):** runbook :1910 "original and next resolved spans" in "What the arm record must carry" is the dropped ceiling's leftover; replace with "actual install-close and plan-age checks".

## 2. Test oracles — 12/15 targeted mutants killed; one branch has no oracle

Killed: ordinal check, prior sha/class, spacing 59/60 and interval value, install-close boundary, `sent < previous_abort`, t0-authored bound, `veto_clear` truthy, unknown→retry, bytes-vs-parsed. Survived:

- **S2 (should-fix):** `invalid_history` (:158-161) has zero test references. Mutants dropping `started > aborted or aborted > now` and the attempt-ordering guard pass all 27 tests. Add one cell: abort before start, abort in the future, attempt N+1 starting before abort N → `invalid_history`.
- `candidate_head_mismatch` (:137) unobserved at module level; production is defended by foreground step 3 `assert plan.repo_head == plan.measurement_head == os.environ['H']` (:1794). Add to the same cell (nit).
- Pins bite: F1 pin is on `render_policy()` plus byte-identity, so a docs-only edit of either block fails `test_both_document_blocks_are_exact`; F2 needle (:268-272) is exact including the line break — brittle to reflow, but bites. The step-4 duplicate of the R1 sentence (:1636-1638) outside the block is unpinned (nit; the block in the same document governs).
- **S3 (should-fix):** `test_whole_day_install_spans_are_informational` (:165-168) pins `run_night.INSTALL_SPANS == (("00:00","24:00"),)` — a foreign constant that Ed's "windows whenever quiet" knob legitimately changes; its failure would not indicate an A172 defect. Delete it (keep `test_midnight_retry_two_days_later…`, which is the R2 regression).
- `test_foreground_publication…` strips imports, so a misspelled import in the block escapes it; I verified `NightPlan.from_mapping` (night_gate.py:211) and `install_close_epoch` (run_night.py:965) resolve. Nit.

## 3. 3 a.m. walk of §1.4a — executable headless; two joins ambiguous

Steps 1-7 need no human; per-attempt latency is one email round-trip plus the 60 s spacing. Ambiguities:

- **S4 (should-fix):** initial-arm linkage. §1.4 (:1504-1508) says write to `$ATTEMPT_DIR/notice-evidence.txt` "with the parsed `notice.json` below", and the foreground block dies at `: "${ATTEMPT_DIR:?}"` (:1728), but nothing in §1.4 says the FIRST arm runs §1.4a steps 4-6 with `ARM_ATTEMPT=1` and `attempts.json` = `[]`; the subsection title says "Recover an eligible arm abort". Add one sentence to §1.4: "Every arm attempt, including the first, runs §1.4a steps 4-6 (`ARM_ATTEMPT=1`, `attempts.json` = `[]`)."
- **S5 (should-fix):** step 7 `outcome.json` has no named fields, while step 5 requires the aborting attempt to have recorded `attempt_epoch_s`, `abort_epoch_s`, `cause`, `receipt_class`, `plan_sha256`, `message_id`, `outcome` under those names. Amend step 7: "`outcome.json` carries exactly the step-5 record fields for this attempt; attempt N+1's `attempts.json` is the unmodified concatenation of attempts 1..N `outcome.json`." Without it the byte-for-byte copy in step 5 has no defined source.
- Nit: step 2 "restore … exclusively if absent" — give the command (`cp -n "$ATTEMPT_DIR/plan.json" "$STAGED_PLAN"` then `cmp`). Nit: step 3 "Repeat §0's input/science checks" vs :353 "without rerunning §0.2" — name the §0.x repeated to bound turnaround.

## 4. Overbuilt / dead

`UNCERTAIN_STATES` (:20) is used by nothing but a test assert — delete or reference from the `arm_watchdog_uncertain` row (nit). S1 span residue and S3 span test above. `NOTICE_LEAD_S = 0` is a documented zero, fine. Imports all used.

## 5. Python 3.9 / module tests

`/usr/bin/python3` 3.9.6 imports `joulewise.arm_retry` (22/13/2 rows). `tests.test_arm_retry`: 27 OK; `tests.test_night_gate` (pins the arm block): 59 OK. The test module itself needs ≥3.11 because it imports `scripts.run_night` — expected and documented (:3-5).

## 6. Verdict

**LANDABLE with amendments** — no blocker. Exact list: S1 (runbook :1910 span residue), S2 (`invalid_history` + `candidate_head_mismatch` test cell), S3 (delete the INSTALL_SPANS pin), S4 (§1.4 initial-arm sentence), S5 (step-7 `outcome.json` schema = step-5 record). Nits at lead discretion. All five are bench-sized; S2 is the only code-behaviour gap and touches tests only.
