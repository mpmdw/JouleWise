# Cold-gate ruling (Fable seat) — skill-distill doctrine landing, 2026-09-04

Session 15:22–15:33 PDT, single non-interactive instance, all probes foreground.

## 0. Contamination disclosure

Auto-loaded without my action: `~/.claude/CLAUDE.md` (global rules), the
worktree `CLAUDE.md` (Codex bridge notes), and the auto-memory index
`MEMORY.md` (one-line pointers). Used as authority: none. Not read:
`CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, any narrative state doc
except the bounded exhibit lines the packet cites.

## 1. Digests and validator receipt

| Item | Expected | Observed (`shasum -a 256`) |
|---|---|---|
| charter | `099de884…95d81` | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` MATCH |
| registry `cc56a9a7` line 16 | same | MATCH |
| packet | `11ec7b87…40573` | `11ec7b877ec34ac981185968da1e590155450724b6b38637291456c707640573` MATCH |

Validator: `scripts/validate_gate_packet.py … --expected-charter-sha256 … --expected-packet-sha256 …` → `"result":"PASS"`, rc=0, 25/25 exhibit digests observed = expected, `judge_handoff_bound:false` (treated as byte observation only).

Exhibit provenance (all `cmp` against `git show`): 05 = `git diff --full-index b0ed6991..ef06b4c7`; 06 = `git diff 849915bc..5a5fc606`; 07 = `git diff ef06b4c7^..ef06b4c7` (doctrine files); 08/10 = merge-base files; 09/11 = files at ef06b4c7; 12, 13, 14–25 = byte-identical to their tracked sources at ef06b4c7; 01–04 = the four trace files at ef06b4c7. Merge base recomputed = `b0ed6991`. `ef06b4c7..755bb090` touches only the packet directory (0 doctrine-file lines).

## 2. Executed table (scratch worktree `/private/tmp/cold-skill-40423` @ ef06b4c7, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPYCACHEPREFIX=/private/tmp/cold-skill-pyc`)

| # | Probe | Result |
|---|---|---|
| E1 | Test modules named by the packet | NONE NAMED (doctrine-only landing). Census: only `tests/test_docs_freshness.py` binds a changed file (`DOC_PATHS` includes `docs/orchestration.md`); no test reads `docs/agent_playbook.md`. |
| E2 | `python3 -m unittest tests.test_docs_freshness` @ ef06b4c7 | **FAILED (failures=1)**: `test_current_sections_do_not_copy_volatile_literals` → `('orchestration reconstruction', 'orchestration model name', 'Opus')`. Same failure at branch head 755bb090. |
| E3 | Same test with `docs/orchestration.md` from merge base b0ed6991 | OK (23 tests). The landing turns a green tracked test red. |
| E4 | `tests.test_build_site_parsers` | OK (skipped=26). |
| M1 | Delete heading `## Reconstructing the loop on a clean machine` | 3 failures (`missing freshness boundary`) — positive control: the test binds the file. |
| M2 | `D-129`→`D-128` inside the addendum | No new failure. No executable check on decision-ID citations. |
| M3 | Cited trace path → nonexistent (`17k-…-NOPE.md`) | No new failure. No executable check on trace-path citations. |
| M4 | Insert model literal `claude` into the addendum | Same single failure (checker reports first hit per region). |
| M5 | Strip “It does not supersede D-129 …” sentence | No new failure. |
| M6 | Gut Q1 text (“Record the”→“IGNORE the”) in `agent_playbook.md` | No test binds the file (0 references in `tests/`). |
| M7 | **Counterfactual cure**: `Opus-directed`→`lieutenant-directed` at the two addendum sites only | `test_docs_freshness` → **OK**. Restored file sha `3122791681e9…` verified after every mutation. |
| R1 | Q5 refusal leg, tracked analogue `scripts/bridge scope-check` (baseline + `codex-cli` lease, scope `docs/orchestration.md`) with a lead-created untracked `LEAD-NOTE-untracked.md`, seat changed nothing | `verdict=SCOPE_VIOLATION` rc=3; path row `out_of_scope: persistent delta does not match declared scope`. |
| R2 | Same, clean tree | `SCOPE_OK` rc=0. |
| R3 | Same, in-scope edit only | `SCOPE_OK` rc=0, row `in_scope`. |
| R4 | Q5 envelope byte-cap leg (8459 B > 8192 → rc=65) | NOT EXECUTED: no 8192/byte-cap implementation in tracked `scripts/` or `bridge_protocol.md`; it lives in untracked personal tooling. Evidence accepted from exhibit 17 (row “Final-head fresh pass 2”) and exhibit 18 (the 243 report itself). |
| R5 | Q1 leg (broad discovery interrupted) | NOT RE-EXECUTED (load-sensitive multi-hour suite, 40-min budget); exhibit 14 V1/V2/G2 read verbatim: V1 focused pass rc=0, V2 discover rc=130 `KeyboardInterrupt` at `test_calibration_writer_crash_matrix.py:1558`. |
| P1 | Post-test dirt in scratch tree | none (`git status --short --ignored` shows only `.codex-bridge`). |

## 3. Verdicts (packet vocabulary; AMEND = charter REJECT-as-written with cure)

**Q1 — AMEND (MATERIAL).** Evidence supports the precedence rule (exhibit 14:35–42, 65–67; 15:24–27). But “leave *any required* merge-wide replay to the lead” makes the lead replay optional, and this very landing shows the gap: seat (01:108), refuter (03:146) and fix seat (04:92) each skipped discovery and E2 went unnoticed. Replace the sentence “Record the broader suite … cannot use.” with: “Record the broader suite as deliberately not run. A landing whose seat skipped discovery is not merge-ready until the lead has run the full suite green at the candidate head; do not spend the seat on a default discovery run that the task cannot use.” Also conflicts in placement with M0 step 5 (exhibit 08:70–72), see Q-SCOPE.

**Q2 — AFFIRM.** Executed pattern verified (15:24–52, 16:28–52, 19:1–7); reproduced here (P1).

**Q3 — AMEND (BLOCKER for merge).** Content is correct against D-129 (12:8318–8332) and 13:42–45. But the literal “Opus” in the reconstruction region breaks `tests/test_docs_freshness.py` (E2/E3) and violates the file's own rule that model assignments “live in D-129 and the memory index, not here” (exhibit 10:38–41). Replace “Opus-directed Sol lanes remain the standing default” with “lieutenant-directed executor lanes remain the standing default (model assignments live in D-129, not here)”. M7 shows this cure alone turns the test green.

**Q4 — AMEND (same defect).** Replace “bounded Sol seats” with “bounded executor seats” and “standing Opus-directed default” with “standing lieutenant-directed default”. The dated-exception framing is supported verbatim by 13:42–45 and cures refuter F2 (03:109–117, 04:80).

**Q5 — AFFIRM.** Untracked-dirt scope failure reproduced with the tracked bridge (R1–R3); envelope cap evidenced, not executed (R4). Text is generic enough (“declared byte limit”) to survive tooling changes.

**Q6 — AFFIRM.** 13:77–86 verbatim; rule is a prohibition on blind relaunch, not mechanics.

**Q7 — AFFIRM.** 20:91–100 (restore SHA per mutation), 21:1–30 (merge parents, unpiped log, rc), 16:50–52; I applied the same custody here (sha check after every mutation).

**Q8 — AFFIRM.** 22:704–720 (H-1 `claude --bg --help` starts a session), 22:770–789, 23:149–162 verbatim. It does not amend the charter; it binds the packet assembler. NIT: partly restates charter §4; add a pointer to §4/§6.

**Q9 — AFFIRM.** 24:19 verbatim; independently corroborated by the packet-45 ruling's sealing note (`46-coldgate-fable-ruling-packet-45.md:9`, seven foreign files in the shared scratch).

**Q10 — AFFIRM.** D-171 addendum 12:10683–10685: table half RATIFIED. NIT: cite “D-171 item 6, first-use-table half” inline.

**Q11 — AFFIRM.** Each element of 12:10683–10690 is preserved (pending Ed; magistrate-commissioned briefs only; must be labelled; not citable as ratified). The original overbroad text (06: “every behavioral clause also needs an executed probe”) is gone at ef06b4c7. NIT: cite the decision-log addendum itself, not only the lieutenant report.

## 4. Q-SCOPE

| Q | Ruling | Home / replacement |
|---|---|---|
| Q1 | ONE-HOME MOVE (within file) | The rule sentence belongs in M0 step 5 (`agent_playbook.md` §Mission M0, after “A red suite is itself the mission.”); the addendum keeps the incident pointer only. A reader of step 5 must see the exception where the default lives. |
| Q2 | KEEP HERE | Seat-facing verification hygiene; no other repo home. |
| Q3, Q4 | KEEP HERE (as amended) | The D-129 pointer already exists at 10:37–41; the addendum's value is the dated-exception record. Model names stay in D-129. |
| Q5 | SPLIT | Sentence 1 (launch record checklist) is the delegated-agent invocation contract → ONE-HOME MOVE to the `codex-delegation` skill (10:327–341 declares it skill-only), replaced by “Launch records: see the codex-delegation skill.” Sentences 2–4 KEEP HERE (repo-side `scripts/bridge` behaviour, R1). |
| Q6, Q7 | KEEP HERE | Doctrine prohibitions/custody, repo-derivable. |
| Q8, Q9 | KEEP HERE | Charter is judge-facing and gated; lead-side packet duties need this process-layer home. |
| Q10, Q11 | KEEP HERE as pointer paragraphs | ONE home is D-171 (`docs/decision_log.md`); keep only if the D-171 citation is inline (NITs above). |

## 5. Packet hygiene (charter §6)

1. **MATERIAL, omission.** No exhibit or sentence discloses the tracked-test status of the delta; all three seat reports record “discovery not run” and the packet frames grading as “the candidate delta” only. Effect: Q3/Q4 would have been AFFIRMed on content alone. Cure for future packets: an executed `test_docs_freshness` (or the binding-test census) line per changed doc.
2. **NIT.** Exhibit 13 is a whole narrative state file rather than a charter §4 bounded excerpt; the cited lines are byte-identical to git at ef06b4c7, so no selective-quotation risk; no effect.
3. **NIT.** Packet §7 forbids running tests while the convening instruction requires executed probes; I followed the convening instruction in a scratch tree and wrote only this file.
4. Otherwise neutral: before/after quotes exact, contrary refuter findings (03) and the superseded wording (06) present in full, questions atomic.

## 6. Overall verdict

**MERGE: REFUSE as-is (BLOCKER).** `tests/test_docs_freshness.py` is red at ef06b4c7 and 755bb090 and green at the merge base (E2/E3); M0 step 5 makes a red suite the mission. **Counterfactual input that clears the blocker:** apply the Q3/Q4 amendments (M7 verified green), apply Q1's replacement text, then a lead replay of the full suite at the new head with Q7 custody. With those cures the landing is mergeable; no second same-shape seat round is needed (one-site doc edit, verified here).

Scratch worktree removed and lease/temp state deleted immediately after this file was written (receipt in the final reply).
