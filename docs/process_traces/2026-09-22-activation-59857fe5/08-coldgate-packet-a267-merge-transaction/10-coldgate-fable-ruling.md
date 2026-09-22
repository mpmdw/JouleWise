# Cold-gate ruling — A267 + A269 merge transaction (packet 08, activation 59857fe5)

Judge: Claude Fable 5.1, cold, foreground, 2026-09-22 11:18–11:23 PDT, worktree at `2858beec`; `489b0953`/`e52c7fbc` read via `git show`. Only this file written. No subagents, background tasks, `log`, `sudo`, `systemsetup`, `powermetrics`.

**Disclosure.** Auto-loaded: `~/.claude/CLAUDE.md`, project `CLAUDE.md`, memory index `MEMORY.md` (pointers only). Not read: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, record 01, council logs, run reports, any other trace; the two cited gate directories were touched only via `git show | shasum` to check exhibit B's pins.

## 0. Trust anchors

| Item | Expected | Observed | Method |
|---|---|---|---|
| charter (first run, deliberately altered) | `…a8700f8c…` | `099de884…c95d81` | `validate_gate_packet.py` → `REFUSE`, reason `charter_trusted_observed_mismatch`, rc 2 |
| charter (trusted) | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | identical | validator `PASS` rc 0; `shasum -a 256` identical |
| packet | `bb82962c7e531f8e60d4aa998aaa3153c7ff67fcf70c05ed29a3c67a7f2a4399` | identical | validator + `shasum -a 256` |
| exhibits A–D3 | manifest | 9/9 observed = expected | validator receipt |
| B1/B2/B3/B4/B5 source files at `c8812172` | `3c756cfa…`, `507c33cb…`, `37739f68…`, `aa3c4f45…` | identical | `git show c8812172:<path> \| shasum -a 256` |

The altered run refused; the trusted run passes.

## 1. Own probes (executed this session)

- **C3/C3b reproduced exactly.** Guard at `489b0953` (`:450-456`): fixture `True`, live syslog (191 lines) `False`, zero-match (51 B) `False`; markers 30/30/0. Proposed `first.rstrip() == "Timestamp                       (process)[PID]"`: True on both live captures, False on fixture, empty, HTML, bare newline, D2 line 2, compact header alone.
- **C1, C4, C5 reproduced.** Four governed files at `489b0953` hash to r7's pins (r7 json :39-44). Path sets 9/10, intersection 0; `447fd6bf` ancestor of both; scratch **4** commits, feature 21. r7 bytes `14c891eb…` = `ANCHOR_V3_R7_ACCEPTANCE_BOUND_SHA256` (`calibration_bracketing.py:141`@`e52c7fbc`). `62412ee6..489b0953`: one file, 7+/7−, docstring only.
- **r7 field diff reproduced independently:** 428 leaves each side, 0 added, 0 removed, exactly 3 changed: `acceptance_id`, `prospective_rederivation/estimator_code_sha256/joulewise/uncertainty_evidence.py`, `derivation_sha256`.
- **Code read at `489b0953`:** `attestation_timeout_s` (:579-601) and `cleanup_budget_s` (:986-989) both `gap − 5`; `CLEANUP_BUDGET_RESERVE_S` comment (:977-983) claims the reserve is what the attestation "fits in"; `attest_network_time` default `timeout=ATTESTATION_TIMEOUT_FLOOR_S` (:604); skeleton has `window_epoch_s: None` but no `window_argv_epoch_s` (:619, set only at :641-642); `record_attestation` first `except (OSError, ValueError): return False` leaves state untouched (:688-692); `os.replace` failure leaves the temporary (:700-713); `restore_network_time` `except Exception: pass` (:411-412); return code `and cleanup["cleanup_proven"]` (:1159); truth table asserts `cleanup_proven` True on all eight rows (test :1318-1345). Test pins :1259 `== 15`, :1262 `== 95`, :1267 `attest_burn=15`, :1269 `[15]*12`, :1274 `[15]*12` — the packet's enumeration (divergence iv) is correct; harness default `TIMED_LOG_HEADER` (test :20) is the **compact** header.
- **Single module run** (review2 @ `489b0953`): `Ran 98 tests in 9.219s OK` — green with the wrong constant because the fixture pre-satisfies the guard.
- **Q7 probe:** grep for dry/bench/replay/start_drift in `scripts/run_night.py` and `joulewise/night_gate.py` @`489b0953`: no dry-check or bench-replay path; no packet artifact records a ≤ 0.5 s replay.
- **Divergence (v):** 10.23 + q > 22 is False at q = 5, 9; True at 11.8, 15. The assembler is right; D1 §S1's 9 s example does not compute.

## 2. Rulings

### Q1 — REJECT-IN-PART the lead's (a). Ruled: option (a) as to shape; r7 NOT YET admissible as issued; proof set amended.

**Shape:** (a). D-138 (B1 :10372-10374) binds the *merge* to the re-freeze transaction; one merge commit of a branch that carries both the feature and the rebased r7 delta gives atomicity and keeps the per-item trail. (b) rejected: no atomicity gain, trail lost. (c) rejected on D-138's face (staleness window on main).

**Admissibility of r7:** the artifact as prepared is *mechanically* sound (3/428 leaves, C1/C2/C5 all reproduced), but it is not admissible as the issued acceptance until three things exist that the packet does not hold: (1) r7 rebased onto the FINAL head *after* fix round 2 with C1 re-executed there — Q2 and Q3 cures do not touch a governed file (both are in `quiet_predicate_campaign.py` and tests), so the pins should not move, but the transaction must prove it, not assume it; (2) the neutrality evidence re-executed at that head: C6 quotes the 349-test run at the scratch head and the quick tier at `e52c7fbc`, i.e. *before* the feature delta is applied on top; a rebased branch is a new tree; (3) D-138 clause (3): the packet does not show whether any of the scratch delta's four test modules (C4 list, `tests/test_calibration_*.py`, `test_capture_pipeline_era.py`, `test_powermetrics_fiducial.py`, `verify_calibration_acceptance_corpus.py`) re-keyed anything other than the r6→r7 pin/id. I did not read those diffs (time budget). **MATERIAL**: the PR ledger must print `git diff --stat 447fd6bf..<scratch-tip>` for those five test paths with a one-line statement per file that only acceptance-id/digest pins moved. Divergence (ii) (the tenth path unnamed by the lead) is exactly why this must be printed rather than dictated.

**Contrary evidence weighed:** the 616/1-failure run (C6 step 22). The re-run-alone green and untouched-files argument is plausible but is argument; I do not accept "contention flake" as a verified fact. Cure: proof (vi) below must be a single green run, or two runs with the same one failure re-run alone green AND the flaking test named in the ledger. Not a blocker.

**Ruled pre-merge proof set at the final rebased head (all seven of the lead's, amended):** (i) 38-member replay `EQUAL 38 / DIFF 0 / NOT_EXECUTED 0` with ids in the ledger; (ii) corpus verify r6 vs r7 identical statistics + `PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK`; (iii) derivation-digest MATCH for r7; (iv) four governed digests vs head bytes (C1 re-run); (v) quick tier green **at the rebased head**; (vi) six D-138 modules + seven exit-contract modules green at the rebased head, with the flake rule above; (vii) twelve-row ledger; **(viii, added)** the Q2/Q3/Q5 regressions listed below present and green, each with its counterfactual kill recorded (the C-028 shape); **(ix, added)** the D-138 clause-(3) test-diff statement. Divergence (i) (4 not 5 commits) bears on nothing.

### Q2 — AFFIRM the lead's (a). BLOCKER confirmed at the bench (C3, reproduced).

Ruled guard text, replacing `:443-456`:

```python
# `log show --style syslog` (the argv ruled by A267 ruling 14 R4) prints this
# exact column header before any entry, and prints it when nothing matched
# (live zero-match capture 07c-exhibit-D3, one line).  The `--style compact`
# header is `Timestamp               Ty Process[PID:TID]` and is REJECTED:
# the guard pins the ruled argv's output, not any header.
TIMED_LOG_SYSLOG_HEADER = "Timestamp                       (process)[PID]"

def timed_log_has_header(text):
    """Did this body come from the ruled ``log show --style syslog`` query?"""
    first = text.splitlines()[0] if text else ""
    return first.rstrip() == TIMED_LOG_SYSLOG_HEADER
```

(b) rejected: it cannot distinguish the styles, so the defect being cured could recur undetected. (c) rejected: amends a ruled argv for a fixture.

**Fixture set (tracked, sha-pinned in the tests):** `tests/fixtures/qpe01_pilot_n1_20260922/exhibit-D-timed-log.txt` (compact, retained as the marker/envelope corpus), **new** `tests/fixtures/qpe01_pilot_n1_20260922/exhibit-D2-timed-log-0210-0435-syslog.txt` (sha `dba7fb7c…`) and **new** `…/exhibit-D3-timed-log-zero-match-syslog.txt` (sha `da1b28ef…`), byte-copies of the two tracked captures. Test constant `TIMED_LOG_HEADER` (test :20) must become the syslog header + `"\n"`; the harness default (`D6` in D3) follows.

**Regressions:** R2.1–R2.5 as written, adopted, with these additions: **R2.3 must assert both** `timed_log_has_header(compact_fixture) is False` *and* that an end-to-end night fed the compact fixture yields 12 × `asserted` with reason `timed log query returned no header` (counterfactual at `489b0953`: 12 × `authenticated`). **R2.6 (added):** trailing-whitespace tolerance — the header line with and without its four trailing spaces both accept (counterfactual: replace `.rstrip() ==` with `==` and the live capture fails). **NIT:** R2.5's "identical outcomes" must include `log_sha256` differing (different bytes) while `matched_lines`, `matched_marker_lines`, and state are equal.

### Q3 — AFFIRM the lead's (b).

Ruled bound: `return max(ATTESTATION_TIMEOUT_FLOOR_S, gap - cleanup_budget_s(protocol))` at `:601`, with the invariant `attestation_timeout_s(p) + cleanup_budget_s(p) <= gap` for every protocol where the floor does not bind, and a comment noting that when the floor binds (gap ≤ 10 s) the pair may overrun and the drift abort is the detector. Under v2: 5 s. At 700 s pitch: 5 s. (a) rejected: two functions each spending the same 5 s reserve is a defect in fact, not only in comment, and D1 §S1's *direction* stands even though its band does not (divergence v). (c) not needed.

**Pins to move (five, one test, :1257-1278):** :1259 → `5`; :1262 → `5`; :1267 `attest_burn=5`; :1269 `[5] * 12`; :1274 `[5] * 12`. :1260 unchanged. Also `:589` ("15 s under v2") and `:592-597` (the "deliberate residual" paragraph) must be rewritten — the residual no longer exists — and `:977-983` stays true under (b) and needs no rewrite beyond naming `attestation_timeout_s` as the function that spends the reserve. Regressions R3.1–R3.4 adopted as written. **R3.4 amendment (MATERIAL):** the counterfactual must be executed as a kill, not "the same test with 15 s pins": re-introduce `gap − CLEANUP_BUDGET_RESERVE_S` and show R3.3 fails.

### Q4 — AFFIRM as implemented; AFFIRM the null-initialisation.

B4 :39 rules `window_epoch_s` = the float union window with `window_method`; brief 06 item 14 (B6 :29) inverted the meaning. A seat may not silently rename a ruled field, but here the seat *preserved* the ruled field and added a new one; the brief, not the ruling, was wrong; D2 §N4's "rename" characterisation is inaccurate (nothing ruled was renamed). Amendment text: at `:619` insert `"window_argv_epoch_s": None,` immediately after `"window_epoch_s": None,`. Regression: blocked and window-unavailable records carry the key with value `null` (counterfactual at `489b0953`: `KeyError`). Record `window_argv_epoch_s` as ruled vocabulary beside `window_method` in the ruling index.

### Q5 — Rule per item.

1. **AFFIRM** (MATERIAL). `:688-692` returns `False` with `authenticated` intact; verified. Exact cure: in that `except`, `attestation["state"] = "asserted"; attestation["reason"] = f"session record unreadable: {type(exc).__name__}: {exc}"`. R5.1 adopted.
2. **AFFIRM** (MATERIAL). `temporary.unlink(missing_ok=True)` inside the `except OSError` before setting `asserted`. R5.2 adopted; the `.tmp` assertion must sit on the `os.replace`-raises variant.
3. **AFFIRM** (NIT→MATERIAL for the table's honesty). Verified: all eight rows assert `cleanup_proven` True; the two "refused" rows return 2 via `outcome == "refused"` regardless. R5.3 adopted: a row with `outcome == "complete"` and final `cleanup_proven False` → rc 2.
4. **AFFIRM** (NIT). `print(f"restore receipt write failed: {type(exc).__name__}: {exc}", flush=True)` in `:411-412`; R5.4 adopted.
5. **AFFIRM** docstring-only (NIT). Add one sentence to `timed_log_window_epoch_s`; no regression required.
6. **AFFIRM** (NIT). `def attest_network_time(out, blocked=None, *, timeout):`; R5.5 adopted. Note the harness at test :1267 passes `timeout` through kwargs already.
7. **AFFIRM** no change.
No further regressions required.

### Q6 — AFFIRM with one correction (MATERIAL).

The parity on which the corpus stands is executed (C3, reproduced: 191/191 lines, 30/30 markers). No sealed A267 finding depends on the header line, so nothing sealed re-opens. Correction: ruling 14 R3 regression 12 ("scanner over exhibit D returns 10 matches") and R4's argv are both satisfied only if the syslog twin is made a fixture; Q2 orders that. The A267 gate record must carry a dated addendum stating that exhibit D was captured in `--style compact`, that the two live syslog captures are its production-format twins, and that the compact fixture's header line is henceforth a *negative* fixture.

### Q7 — REJECT the lead's disposition. Extra precondition named.

B4 :35 is exact: before the re-run night is *prepared*, a daytime bench replay ("real `execute` and real collector with an injected recorder replaying an archived plist, no sudo, no measurement, never labeled R6 evidence") must show chain-level `start_drift_s` ≤ 0.5 s on **every** slot. No code path at `489b0953` implements such a replay under a "dry check" name, and no artifact in this packet records one. "The tracked entry point's dry check" is not shown to be that replay. Ruled precondition: **(P7.1)** the bench replay is executed after merge, at the merged head, and recorded as a tracked artifact `docs/process_traces/2026-09-22-activation-59857fe5/<nn>-bench-replay-start-drift.md` carrying the merged sha, the archived plist's sha256, the twelve `start_drift_s` values from `evidence_envelopes.jsonl` (chain-level), the maximum, and the statement `max ≤ 0.5 s`; **(P7.2)** it is linked from the arm notice; **(P7.3)** B3b's ordering (both A267 Part 3 and A269 merged; v2 exclusion list complete on main) is evidenced by the merge sha. Only then NIGHT_HANDBACK. If the replay exceeds 0.5 s on any slot, no arm; the night refuses on the 2 s rule only *after* the 0.5 s bench bar is met — the two bars are sequential, not alternatives.

## 3. Nine divergences

(i) 4 commits, not 5 — NIT, bears on nothing. (ii) tenth path unnamed — MATERIAL, drives Q1 proof (ix). (iii) 51 vs 50 bytes — NIT. (iv) five pins not two — MATERIAL, Q3 pin list adopted from the packet. (v) D1 §S1 arithmetic — MATERIAL to D1's *band* only; Q3 direction unaffected; the packet's correction is adopted. The packet names four more implicitly: the seat's D6 harness default is compact (Q2 fixture set); D2 §N4's "rename" (Q4, rejected characterisation); D3 "NEEDS_RULING: None" while D3 itself flags the bound (Q3, resolved by ruling); C6 neutrality runs executed pre-rebase (Q1 (v)/(vi) re-execution).

## 4. Packet hygiene

PASS with two NITs. Complete, neutrally assembled, contrary evidence (the 616/1 run) included, argument labelled, D1–D3 verbatim. NIT 1: "nine divergences" are enumerated only as five plus prose; the remaining four are inferable but not numbered. NIT 2: Q1 bundles three deliverables (shape, admissibility, proof set); I ruled them separately above. No cherry-picking found: my own probes matched every executed C figure.

## 5. Findings tier summary

- **BLOCKER:** Q2 header constant is the compact header under a syslog argv (C3, reproduced).
- **MATERIAL:** Q3 double-spent reserve; Q1 r7 not yet issued (rebase + re-executed neutrality + clause-(3) statement); Q5 items 1–3; Q6 addendum; Q7 missing ≤ 0.5 s replay artifact; divergences (ii), (iv), (v).
- **NIT:** Q5 items 4–6; R2.5 `log_sha256` note; hygiene NITs; divergences (i), (iii).

Two consecutive rounds have not failed with the same signature: round 1 cured the dictated items and surfaced a constant built from the only artifact available; round 2 is a different defect class (fixture provenance), so a same-shape round is licensed.

Charter §9: no prior verdict is reinterpreted; A269 ruling 10 Q3 stands as issued and is applied, not amended.
