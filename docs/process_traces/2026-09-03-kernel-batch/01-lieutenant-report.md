# Post-merge kernel batch, 2026-09-03 — Opus lieutenant report

Branch `bookkeeping/2026-09-03-kernel-batch`, cut from `origin/main` =
`46eaf18c`. Worktree `/Users/edr/code/JouleWise-wt-kernel-batch`.

Every dictated fact was checked against primary evidence before it was
written. Two did not hold as dictated and are recorded below. Two of the four
dictated items are **blocked on a WRITE_SCOPE extension** and were not landed;
their prepared, tested edits are in this directory ready to apply.

---

## 1. Facts verified

### Item 1 — the D-171 addendum

| Dictated | Verified against | Held |
|---|---|---|
| D-171 item 6 says the first-use table is "PAIRED with executed probes" | `docs/decision_log.md` D-171 item 6, read in full | yes |
| The exact text was routed through the cold gate on packet 45 | same item 6, parenthetical | yes |
| Cold Fable found Ed's sentence covered only the first-use-table half | file 46 Q6(e), read verbatim | yes |
| Ed's checklist item and sentence, as quoted | file 46 Q6(e) quotes both: "pre-landing first-use table as a mandatory gate for defined-term contract edits, yes" and "5 and 6 sounds good i trust you" — matched word for word against D-171's own verbatim record of Ed's reply | yes |
| The Opus refuter reached the same conclusion | file 47 Q6-4, severity MATERIAL, names the three unseen clauses | yes |
| D-171 item 7 sets a 5-minute stand-down margin | `docs/decision_log.md` D-171 item 7 | yes |
| Watchdog gate row 4: request t0−25, SIGTERM t0−16, SIGKILL t0−15 | `docs/process_traces/2026-09-02-hands-free-week/15-watchdog-gate-synthesis.md` row 4 | yes, exactly |
| The runbook requires ≥10 min untouched idle before a window | `docs/phase_2/window_runbook.md:425-432`, read at the bench: "Leave the machine untouched and idle for at least 10 minutes **before** the §5C step-2 calibration-ledger pair … This is in addition to the chain-owned 180-second stage settle" | yes |

### Item 2 — the new rows

| Dictated | Verified against | Held |
|---|---|---|
| `LINEAGE-RELOCATABLE-01` from file 32 S3 ruling (d) | file 32 §S3 names the row explicitly: "(iii) a kernel row `LINEAGE-RELOCATABLE-01` in the post-merge kernel batch (bench, main)" | yes |
| `LINEAGE-RESOLVE-RACE-01` from file 46 NIT-1, sites ~:9020 and ~:10222, `inputs.py:_read_bundle` catches only `LaunchLineageError` | file 46 NIT-1 cites `arm_readiness.py:9020`, `:10222`, and `inputs.py:2778-2782` | yes |
| `ONE-USE-CONSUMPTION-TEST-01` from file 46 NIT-2, test skipped STRUCTURAL-BLOCKED at ~:751-755 | file 46 NIT-2 cites `tests/test_arm_readiness_lifecycle.py:751-755` | yes |
| Five rows from the code audit §5 items 1–5 | `13-audit-code-tests-opus.md` §5 table, items 1–5 in the dictated order, with the dictated one-line subjects | yes |
| §2.2 has "six SILENT refusals" | §2.2 table and §2.3 | **NO — see 2 below** |
| `WATCHDOG-INSTALL-01` evidence files 15/16 | both present in the hands-free-week directory | yes |
| `NIGHT-PLAN-PIN-01` branch `feat/2026-09-03-night-plan-pin` | branch exists **locally only** (worktree `/Users/edr/code/JouleWise-wt-planpin`, at `2f59e791`); `git ls-remote --heads origin` returns nothing for it | partly — see 2 |

### Item 3 — the audit's corrections

| Dictated | Verified against | Held |
|---|---|---|
| D-170 installed via #273/#274/#275 | `gh pr view` each: #273 MERGED 2026-09-02T20:16:17Z (items 1+4), #275 MERGED 2026-09-02T20:17:10Z (item 2), #274 MERGED 2026-09-03T03:01:29Z (item 3). Each carries real producer regressions, not documentation alone: #273 `scripts/gen_state.py` + `tests/test_gen_state.py` + `tests/test_docs_freshness.py`; #275 `scripts/check_gate_ledger.py` + `tests/test_check_gate_ledger.py` + the workflow and template; #274 `joulewise/arm_readiness.py` + five arm-readiness test modules | yes |
| D-170's own closing condition is that all three land | D-170 body: "moves this entry to `adopted` only after all three installing pull requests land and names those pull requests here" | yes |
| Rows blocked only on D-170 | kernel dump of all nine D-170 dependants: six have D-170 as their sole pending dependency (`GAMMA-UNIT-ROSTER-GUARD-01`, `S9-01B`, `S9-02`, `S9-03`, `S9-05`, `S9-06`); `T26-RULING-INSTALL-01`'s is scope `close`, not `start`; `L10-SACRIFICIAL-REHEARSAL-SCHEDULE-01` and `V5-TRANSACTION-01` keep other pending dependencies and stay blocked | yes |
| V4-TRANSACTION-01 → retired; D-164 says `_v4` is never collected | D-164 index row, verbatim: "`_v4` is never collected"; D-167 installs `V5-TRANSACTION-01` as successor; `V5-TRANSACTION-01` is live in the kernel | yes |
| PIPELINE-SMOKE-LIVE-01 blocks on a ghost event | kernel dump: pending hard-start dependency, `kind: event`, `target: V5-QWEN3-PACK-GENERATED-S15`; that id is absent from `tasks` | yes |
| The audit names the retarget row | audit A5: "Retarget the dep to `V5-DECODE-IDENTITY-SET-01`" | yes |
| Four "ruled-not-installed" rows | audit A7 lists exactly four and calls them "the 3rd–6th 'ruled ≠ installed' instances": `LINEAGE-RELOCATABLE-01`, `R7F-EXIT3-SEMANTICS-01`, a `_v5` prewindow-pin row, a charter-v3 owner row. Each independently re-verified: the r7f ruling `:73` does promise `R7F-EXIT3-SEMANTICS-01`; `MAGISTRATE-RULING-UNATTENDED-STAGE1.md:208` is R-12 on `prewindow_check.sh`; `scripts/prewindow_check.sh:51` still reads "the governed family is the _v2 campaign packs"; D-170's body does defer item 4 to charter v3 | yes |

### Item 4 — NIGHT

| Dictated | Verified against | Held |
|---|---|---|
| Night LaunchAgents uninstalled 2026-09-03 at `33290b8b` | `docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md:12`: "Night launchd agents UNINSTALLED at the pinned HEAD 33290b8b (`launchctl list` shows none)"; independently re-run this session: `launchctl list` → no matching jobs, `ls ~/Library/LaunchAgents/` → no matching plists. `33290b8b` is an ancestor of `origin/main` | yes |
| #277 merged the NIGHT-REHEARSAL-01 harvest | `gh pr view 277` → MERGED 2026-09-04T02:27:04Z, "NIGHT-REHEARSAL-01 harvest: rehearsal-20260903 delivered (R-7 stand-down proven)" | yes |

---

## 2. Facts that did NOT hold as dictated

**(a) "the six SILENT refusals in its §2.2" — the count is not supported by
§2.2.** The audit's §5 item 2 does say "six silent refusals … per code in the
§2.2 SILENT rows", but its own §2.2 table carries **one** row verdicted
`SILENT — no counterfactual test` (M6, `readiness_pack_not_committed`); three
rows marked "narrow set silent" (M4, M9, M13) that each flipped to **COVERED**
once a wider module set was run (M4b, M9c, M13b); and one row, M8
(`launch_binding_mismatch`), whose mutant and verdict cells were never filled —
the raw `<!--M8-->` and `<!--M8V-->` placeholders are still in the file. §2.3
states the count in words: "Nine of the ten sampled refusals have a real
counterfactual test" and "**One sampled refusal is unguarded (M6).**" §2.3
separately names four refusals that are silent *against the module a developer
would reach for first* — a coverage-cost finding, not an absence of coverage.
Six is reachable only by adding categories the audit itself distinguishes.

*Disposition:* `SILENT-REFUSAL-TESTS-01` is written to what §2.2 and §2.3
support — M6 as the one confirmed unguarded refusal, M8 as an unresolved row
to re-run to a verdict, and the four expensive-module refusals as a named
separate question — and the "six" is carried in its status note as an open
reconciliation rather than as a work-item count. The discrepancy is recorded in
this directory's `02-evidence-index.md` §D so the source is not silently
re-quoted.

**(b) `NIGHT-PLAN-PIN-01`'s branch is local, not pushed.**
`feat/2026-09-03-night-plan-pin` exists as a local branch and worktree
(`/Users/edr/code/JouleWise-wt-planpin`, at `2f59e791`, which is a commit
already on main — no work committed on it yet). `git ls-remote --heads origin`
returns nothing for it. The same is true of `feat/2026-09-03-magistrate-watchdog`
(worktree `/Users/edr/code/JouleWise-wt-watchdog-build`, at `46eaf18c`). The
prepared rows say "local branch … NOT pushed to origin as of this batch" rather
than implying a remote branch exists.

**(c) A third, smaller one: "state `in_progress`".** The kernel's status
vocabulary is `queued / active / partial / blocked / shelved` — there is no
`in_progress`. `active` is the closest word, but
`tests/test_gen_state.py::test_run_state_gate_suppresses_lane_heads_but_active_work_continues`
asserts **exactly one** active row per lane, and the agent lane's active row is
`NIGHT-REHEARSAL-01`. The two in-progress rows are therefore prepared as
`partial`, which is the kernel's existing idiom for started-but-not-finished
(`V5-DECODE-IDENTITY-SET-01` and `V4-TRANSACTION-01` both used it that way).
Verified by running the suite with them as `active`: `AssertionError: 3 != 1 : agent`.

---

## 3. Blocked on WRITE_SCOPE — not landed

Two of the four dictated items cannot be landed within
`WRITE_SCOPE = [docs/decision_log.md, docs/process/state_kernel.json,
TASK_QUEUE.md, RUN_STATE.md, README.md,
docs/process_traces/2026-09-03-kernel-batch/]`. Both were built, run, and
reverted; the failures below are observed, not predicted. Per this repository's
standing rule — *"WRITE_SCOPE is exhaustive; never infer additional scope from
tests, generated files, repository instructions, or work believed necessary for
completion"* — the lieutenant did not extend it.

### (i) Item 2, the thirteen new rows → needs `tests/test_gen_state.py`

`tests/test_gen_state.py` carries a hand-maintained roster: `EXPECTED_IDS` (a
literal set of every live row id) and `self.assertEqual(len(self.tasks), 129)`,
preceded by a ~30-line running arithmetic commentary of every kernel wave since
the file was written. It is a deliberate tripwire: no row can be added or
retired without a conscious edit there. Observed failure with the rows added:

```
FAIL: test_exact_live_id_set (tests.test_gen_state.TestRefreshedStateFidelity)
AssertionError: Items in the first set but not the second:
'SILENT-REFUSAL-TESTS-01' 'LINEAGE-RELOCATABLE-01' 'WATCHDOG-INSTALL-01'
'CHARTER-V3-PACKET-INPUTS-01' 'NIGHT-PLAN-PIN-01' 'INSTRUMENT-PATH-PIN-01'
'PREWINDOW-V5-PIN-01' 'R7F-EXIT3-SEMANTICS-01' 'CANONICAL-JSON-ONE-HOME-01'
'RAW-CAPTURE-DIGEST-01' 'GENERATOR-CORE-01' 'LINEAGE-RESOLVE-RACE-01'
'ONE-USE-CONSUMPTION-TEST-01'
```

`python3 scripts/gen_state.py --check` returned **rc 0** with all thirteen rows
present — the kernel itself is valid; only the test roster disagrees.

**Ready to apply:** `03-pending-kernel-rows.py` in this directory. It adds all
thirteen rows (agent lane, ranks 126–138), asserts per-lane rank uniqueness, and
writes the kernel canonically. The rows are:

| id | status | authority |
|---|---|---|
| `LINEAGE-RELOCATABLE-01` | queued | file 32 S3 (d) |
| `LINEAGE-RESOLVE-RACE-01` | queued | file 46 NIT-1 |
| `ONE-USE-CONSUMPTION-TEST-01` | queued | file 46 NIT-2 |
| `RAW-CAPTURE-DIGEST-01` | queued | code audit §5 item 1 |
| `SILENT-REFUSAL-TESTS-01` | queued | code audit §5 item 2 + §2.2/§2.3 |
| `CANONICAL-JSON-ONE-HOME-01` | queued | code audit §5 item 3 |
| `INSTRUMENT-PATH-PIN-01` | queued | code audit §5 item 4 |
| `GENERATOR-CORE-01` | queued | code audit §5 item 5 |
| `WATCHDOG-INSTALL-01` | partial | watchdog gate synthesis |
| `NIGHT-PLAN-PIN-01` | partial | watchdog gate synthesis row 7 |
| `R7F-EXIT3-SEMANTICS-01` | queued | r7f-unavailable ruling `:73` |
| `PREWINDOW-V5-PIN-01` | queued | unattended stage-1 R-12 |
| `CHARTER-V3-PACKET-INPUTS-01` | queued | D-170 item 4 deferral |

The last three, with `LINEAGE-RELOCATABLE-01`, are the audit's four
ruled-not-installed rows.

### (ii) Item 3's D-170 close → needs `tests/test_docs_freshness.py`

D-170 is the **live fixture** for that file's open-decision mutation guards.
Closing it makes four counterfactual assertions stop raising. Observed:

```
FAIL: test_malformed_decision_index_status_is_not_skipped
FAIL: test_open_decision_counterfactuals_bind_all_installation_limbs
        (mutation='only V5 carries D-170 dependency')
FAIL: test_open_decision_counterfactuals_bind_all_installation_limbs
        (mutation='installer close dependency but no start dependency')
FAIL: test_terminal_decision_counterfactuals (mutation='M6c')
```

`M6c` is explicit about it: it flips D-170 to `adopted` against the live kernel
and requires an `AssertionError` naming a "pending decision dependency on task".
Once the nine dependencies are satisfied there is none, so the guard no longer
fires. Again `gen_state.py --check` returned **rc 0** — the kernel is valid;
these are test fixtures that must move with D-170.

**Ready to apply:** `04-pending-d170-close.py`. It satisfies all nine
dependencies with the pointers D-170's own item-1 rule demands (a `tests/*.py`
path whose label names a test defined in that file):
`tests/test_gen_state.py::test_satisfied_decision_dependency_requires_named_test_regression`
for the item-1 rows, and
`tests/test_arm_readiness.py::test_t0_liveness_bound_refuses_at_600s_plus_1ns`
for `V5-TRANSACTION-01` (item 3). It then unblocks the six rows whose only
pending dependency was D-170, retires `T26-RULING-INSTALL-01`, and unblocks
`ED-BRANCH-PROTECTION-E1-01`. The decision-log index flip to
`adopted (magistrate, 2026-09-03; installed by PRs #273, #274, #275)` is a
one-line edit applied alongside it.

---

## 4. Landed

| Commit | What |
|---|---|
| `01232da1` | D-171 dated addendum: item 6's ratification corrected, item 7's timing superseded, with an Executed-evidence block per D-170 item 4. Original D-171 text untouched. |
| `471c2f01` | Kernel row-state corrections A4 (`V4-TRANSACTION-01` retired by supersession, with a dated D-167 addendum), A5 (`PIPELINE-SMOKE-LIVE-01` ghost dependency retargeted to `V5-DECODE-IDENTITY-SET-01`; goal `_v4`→`_v5`), A9 (`T0-UNATTENDED-01` re-stated as blocked on `NIGHT-REHEARSAL-01`), A7-adjacent (`NIGHT-REHEARSAL-01` fifth acceptance row + uninstall-now-done note). |
| `bac9ae31` | README activity blurb rewritten; RUN_STATE T31 NEXT MACHINE STEP set to watchdog install → plan pin → G2-a night; audit A2, C1, B1, B2, B3 applied. |
| `c365825b` | README B4 reverted — see below. |

Two notes on what landed:

- **"Retired" is recorded as `shelved`.** The kernel's status enum has no
  `retired`, so `V4-TRANSACTION-01` and (in the pending script)
  `T26-RULING-INSTALL-01` are `shelved` with the reason in the status note.
  `gen_state.py` exempts `shelved` from the blocked-iff-pending-hard-start
  invariant, so this is the mechanically correct choice, but it is a vocabulary
  substitution and is flagged as such.
- **A consequence the magistrate should rule on.** `ARM-PACKET-01` carries a
  pending hard-start dependency on the now-shelved `V4-TRANSACTION-01`. It is
  visibly blocked rather than silently broken, but it wants a disposition
  (retarget to `V5-TRANSACTION-01`, or retire alongside). Recorded in the D-167
  addendum; not decided here — retargeting a claim-path packet row is not a
  lieutenant call.

---

## 5. Corrections SKIPPED, with reasons

| Audit item | Reason skipped |
|---|---|
| **B4** — README status-site paragraph (D-136 retired the lane; the README still instructs sessions to do site work) | Applied, then **reverted**. `tests/test_docs_freshness.py::test_site_closeout_is_drift_report_then_ed_deploy` requires every site-publish section to carry the DRIFT-report-then-Ed-deploy sentence, and `_site_publish_instructions` rejected the replacement prose. Landing B4 needs that test edited — out of WRITE_SCOPE. **The audit did not notice this test.** Observed failures: `test_site_closeout_is_drift_report_then_ed_deploy` and `test_checker_mutation_probes_are_rejected_and_history_is_ignored`. |
| **A1** — copy pause-state file 39 to main | Target `docs/process_traces/2026-09-02-decode-identity-set/` is outside WRITE_SCOPE. Mitigated: the T31 addendum now says the pointer resolves only on the decode-identity branch. |
| **A3** — D-170 close | Blocked on `tests/test_docs_freshness.py`; see §3(ii). |
| **A6 (second half)** — `PROJECT_STATUS.md` paragraph on the unattended driver | `PROJECT_STATUS.md` outside WRITE_SCOPE. |
| **A7** — register the four ruled-not-installed rows | Blocked on `tests/test_gen_state.py`; see §3(i). Prepared. |
| **A8** — open the `paper-c` PR | Not a file edit; opening a PR is outside this task and is an irreversible action a lieutenant does not take alone. `origin/feat/2026-09-02-paper-c` still carries two commits with no PR. |
| **A10** — `latest_report` repoint / catch-up run report | Both branches need `docs/run_reports/`, outside WRITE_SCOPE. The kernel's `latest_report` still points at 2026-08-25. |
| **B5** — publication checklist D-078 fence | `docs/publication_release_checklist.md` outside WRITE_SCOPE. This one adds a soundness fence and should be prioritised. |
| **B6** — `docs/milestones.md` rewrite | Outside WRITE_SCOPE. |
| **B7** — `docs/agent_playbook.md` mission menu | Outside WRITE_SCOPE. |
| **B8** — `docs/orchestration.md` roles section | Outside WRITE_SCOPE. |
| **B9** — `docs/risk_register.md` | Outside WRITE_SCOPE. Note it proposes two new rows (unattended nights with Ed absent; the paper deadline) that are live risks right now. |
| **B10** — orphan "A" in `PROJECT_STATUS.md:136` | Outside WRITE_SCOPE. |
| **C2** — D-131 cl.2/cl.3 amendment | Genuinely owed and in flight on the decode-identity branch; not this batch's to land. |
| **C3** — trace retenses | All targets are trace files outside WRITE_SCOPE. |
| **C4** — dated addendum on the dx-t26a ruling's grep predicate | Trace file outside WRITE_SCOPE. |
| **C5** — label the unresolvable sha | Trace file outside WRITE_SCOPE. |
| **C6** — `TASK_QUEUE.md` intake rule + T30 council-log block | The intake rule sits outside the generated marker fence, and WRITE_SCOPE permits `TASK_QUEUE.md` changes only via `gen_state.py`; `docs/council_log.md` is outside WRITE_SCOPE. |
| **A5 (partial)** — `_v4` wording inside `PIPELINE-SMOKE-LIVE-01`'s acceptance evidence | In WRITE_SCOPE but deliberately not applied: editing a claim-path gate's acceptance text is a magistrate call. The dependency and goal are fixed; the acceptance wording is flagged in the row's status note. |

Nothing in the audit's "soundness fences — KEEP" list was touched. In
particular the D-078 voiding language in `README.md` and the
`V5-TRANSACTION-01` fences are exactly as they were.

---

## 6. Suite state

Before any edit, at `46eaf18c`:

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_state tests.test_docs_freshness
Ran 65 tests in 2.537s
OK
```

At the branch head:

```
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_gen_state tests.test_docs_freshness
Ran 65 tests in 2.572s
OK

$ python3 scripts/gen_state.py --check ; echo rc=$?
rc=0
```
