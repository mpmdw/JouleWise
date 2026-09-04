# REPORT-F — paper seat F: 24 first-use cures, §1 scope paragraph + naming bridge, ledger test hardening

Worktree: `/Users/edr/code/JouleWise-wt-paper-f`, branch `feat/2026-09-02-paper-f` (the brief's `-firstuse` suffix does not exist; the launch message's branch name is the real one), base `33290b8b`. NOT pushed.

Commits (both on the branch):
- `44e22d99` — Sol's landing (gpt-5.6-sol, effort high, `CODEX_SERVICE_TIER=default`, audited `codex-run-v3`, genre implementation, invocation `paper-f-firstuse-20260902T204943`, lease `lease-aaca83ff60d248c9ac57c35ca182e488`). Committed by the lead: the workspace-write sandbox cannot write `/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-paper-f/index.lock`, so Sol returned `BLOCKED` (valid, final envelope) with a complete `REPORT_FALLBACK` body instead of a commit. Sandbox also refused the external report path; this file was written by the lead.
- `b10abe47` — lead bench edits after inspecting the diff (listed under "Lead adjudication").

Files: `docs/paper/draft-v2-skeleton.md`, `docs/paper/round7/built-terms-lexicon.md`, `tests/test_paper_first_use_ledger.py`, `tests/fixtures/paper_first_use_pre_cure.md` (new).

## Sol's envelope (verbatim)

`{"status":"BLOCKED","summary":"All authorized draft, lexicon, ledger-test, and 24-row regression-fixture work is implemented; focused and full paper suites pass, scope is clean, excluded regions are unchanged, and U_edge is absent. The sandbox denied writes to the linked worktree's external Git index and rejected the external report file, so the required commit and clean status could not be produced; the complete report is supplied above as REPORT_FALLBACK.","pathspec":["docs/paper/draft-v2-skeleton.md","docs/paper/round7/built-terms-lexicon.md","tests/fixtures/paper_first_use_pre_cure.md","tests/test_paper_first_use_ledger.py"],"verification":["first-use suite: 5 tests, OK","negative fixture: expected failures=24","paper suite: 70 tests in 616.397s, OK (skipped=3)","bridge scope-check: SCOPE_OK","excluded regions: unchanged","retired U_edge grep: absent","git diff --check: clean","git add: blocked by index.lock Operation not permitted"],"flags":["BLOCKING environment: /Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-paper-f is outside writable roots, preventing commit","BLOCKING environment: external REPORT-F.md write rejected; complete REPORT_FALLBACK supplied","NONBLOCKING residual: excluded Section 6 remains for its owning seat"]}`

Full Sol output (claude-codex-report/v1 body + REPORT_FALLBACK): `<scratchpad>/paper/F-codex-out.md`. Prompt: `F-prompt.md` beside it.

## 24-row disposition (Sol's table, each row re-checked by the lead against the diff)

Line numbers: audit line → current line (after `b10abe47`).

| # | Audit line | Term | Disposition | Cure as landed |
|---:|---|---|---|---|
| 1 | 120 → 129 | member's edges | cured | "moves the edges of each run (member) of a block independently" |
| 2 | 121 → 130-134 | A/B/B/A block; shared / local timing-error sign | cured | "An A/B/B/A block is four runs in the order A, B, B, A. A timing-error sign says which direction the allowed error moves energy: a shared sign is one choice applied across all blocks, while a local sign is chosen separately for each block." |
| 3 | 137 → 146 | reasoning disabled | cured | "(Qwen3's optional chain-of-thought output is switched off)" |
| 4 | 163 → 173 | declared machine state; the fixed record | cured | "meaning the hardware and operating conditions recorded before collection"; "must match the frozen plan's calibration entry; **frozen** means fixed and fingerprinted before collection" |
| 5 | 165 → 175 | signal/fit/range… checks; shared search-work limits | cured | "…checks defined in Appendix A.3.5"; "…limits defined in Appendix A.3.7" |
| 6 | 167 → 177 | first-record endpoint; stamp brackets; native labels; launch-to-first-parse ordering; four allowances | cured | endpoint defined; the four constraint families stated in words (stamp bracket, native label, after-launch, parsed-after-written) with "Appendix A.3.3 gives the inequalities"; four allowances named (half the endpoint range, wall-vs-monotonic span, largest clock resolution, numeric-rounding pad). Lead verified each against A.3.3 (`:1374-1394`, "Composing the bound" `:1414-1418`): faithful. |
| 7 | 169 → 179 | calibration policy | cured | "The frozen **calibration-acceptance rule** is the pre-collection rule that decides whether those two captures may bracket one window" |
| 8 | 173 → 183 | entry check | cured | "the **entry check** (the admission gate of Section 5)" |
| 9 | 173 → 184-186 | reference runs | cured | "fixed reference workloads repeated at the window's opening, midpoint, and close to track drift… Those repeated workloads are the **reference runs**." |
| 10 | 173 → 193-195 | gross energy; idle-subtracted energy | cured | "**Gross energy** is the processor energy recorded during a run. **Idle-subtracted energy** removes the mean idle power multiplied by run duration from that gross amount." Lead verified against `joulewise/reduce.py:2960` (`gross_energy_j - idle_baseline.power_w_mean * window.duration_s`). |
| 11 | 214 → 173 | frozen | cured | glossed at its (now earlier) first use in §2 — see row 4 |
| 12 | 236, 307 → 266 | null-test blocks; `null_test`; `floor_train` | cured | "identical-condition null-test blocks—blocks in which both conditions are the same"; the code names left with the deleted rows (row 15) |
| 13 | 285 → 316 | package power | cured | "the summed CPU, GPU, and neural-engine power" (matches the artifact boundary string "Apple SoC CPU + GPU + ANE package power") |
| 14 | 292 → 324 | cadence below its fixed ratio | cured by deletion | no ratio exists in the registry or round7 artifacts; sampling flags now "mark too few in-window sampler records"; ledger row updated |
| 15 | 306-307 → (deleted) | per-token conversion; workload level; registered workload magnitude / three magnitudes | cured by deletion — FLAGGED, see Adjudication F1 | the "Workload response" and "Identical-condition response" rows of the §3 table deleted (audit-sanctioned option "delete the rows (see W2)") |
| 16 | 370, 382 → 399-404, 416-419 | retired calculation; thirty recorded timing members | cured | "pilot evidence from the July 25, 2026 diagnostic window under a **retired calculation**… That calculation used an equal-rate clock anchor and a yes/no rule that called a cell attribution-limited when its exact edge-moved corner maximum exceeded its point-only value after a fixed widening factor. The current calculation instead uses the corner-to-point ratios in Section 4."; "Across the 30 phase-energy runs collected in that July 25 diagnostic window". No decision IDs in reader text. Lead verified: date from registry supplier `A10 = runs_window_a10_20260725`; predicate from `detection_floor.py:806-843` (corner-widened maximum > guard-factor-widened point floor) and D-165. |
| 17 | 516 → 550-552 | close-out records | cured | "post-campaign **close-out artifact**, which checks every required ratio" |
| 18 | 705 → 740-743 | energy term | cured | "The recorded **energy terms** are gross request energy, idle-subtracted request energy, gross prompt-processing energy, and gross token-generation energy." Lead verified against `joulewise/analysis_manifest.py:526-529` (gross_request, idle_request, gross_prefill, gross_decode). |
| 19 | 770 → 805-809 | named kind of deterministic bound | cured | "The named **deterministic-bound kinds** are joint movement of interpolation edges, idle-power drift for idle-subtracted request energy, clock-anchor movement, and the whole-window drift allowance." Lead corroborated by the production key names `E_interpolation_joint_edge_bound_j`, `E_drift_bound_j`, `E_clock_anchor_shift_bound_j`, `E_whole_window_drift_allowance_j`. |
| 20 | 796 → 102-105 | named M3 Max hardware | cured | §1 scope paragraph: "It measures one Apple M3 Max with 128 GB of unified memory and one `powermetrics` configuration. MLX is Apple's on-device inference framework used to run the models. The resulting bounds do not transfer to another machine, software stack, workload, or power counter." A.1 `:1286` now points to Section 1. |
| 21 | 115 vs 486 | U_edge vs U_corner | cured | `U_{\rm corner}` everywhere (4 occurrences: 3 `\rm`, 1 `\mathrm`); `U_edge` absent (grep 0) |
| 22 | absent → 118-121 | detection floor | cured (lead-reworded) | "Its resolution bound—also called the **detection floor**; its final value, after the safeguards of Section 4, is what the artifacts call the **cell floor**—is the largest false phase-energy difference…" (see Adjudication L1) |
| 23 | 810 → 845 | "Figure 3 is required here" | cured | "Figure 3 shows three separate paths…"; `figures/fig3_decision_gates.svg` exists |
| 24 | 917-940 | IQR; record support; overlap count (§6) | out-of-seat-region | §6 byte-identical to base; owned by seat E |

## Lead adjudication

Replayed by the lead this session (all in the seat worktree at `b10abe47` unless stated):

- `scripts/bridge scope-check` (baseline-anchored, expect-digest): `SCOPE_OK`, four in-scope paths, no unowned dirty paths.
- Excluded regions byte-compared against `33290b8b` by heading: Abstract UNCHANGED; "Printed negative result…" UNCHANGED; "What the finding changes" UNCHANGED; "10. Conclusion" UNCHANGED. Seat G's edit regions are exactly these, so no F/G collision. Seat E's scope overlaps F on `tests/` and `docs/paper/round7/` and both edit the draft's ledger table — integration-tree merge, not a defect.
- Internal-shorthand grep over reader text (`D-\d{3}|T26|null_test|floor_train|se_metrology`): only pre-existing `[FILL:…]` registry markers and the fill-notation build note hit; nothing from this seat.
- `git diff --check`: clean. Canonical checkout `/Users/edr/code/JouleWise` untouched (status clean).

**L1 — bench edit (`b10abe47`), §1 naming bridge.** Sol wrote "the quantity the advisor calls the detection floor and the artifacts call the cell floor". "The advisor" is internal shorthand to an ICPE reviewer (common seat rule), and it dropped the relation §4 `:680-681` states ("The final resolution bound is called the cell floor in the artifacts"). Reworded to: resolution bound = also called detection floor; its FINAL value after the Section 4 safeguards = cell floor. Ledger + lexicon rows reworded to match. Bold terms kept on one physical line so the per-line ledger matcher sees them.

**L2 — bench edit (`b10abe47`), outcome sentence A.** Sol changed "on the named M3 Max hardware, MLX, Apple's on-device inference framework, and *powermetrics* power-recording configuration" to a pointer-only "on the machine, inference runtime, and *powermetrics* configuration named in Section 1". The section header says "Do not soften, combine, or mechanically retensor these sentences" and seat G's fill procedure reads `:788-808` verbatim, so I restored the concrete names with the Section 1 pointer: "on the Apple M3 Max hardware, MLX, and *powermetrics* power-recording configuration named in Section 1". Minimal divergence from base; the MLX gloss now lives in §1.

**F1 — FLAGGED for the magistrate (not reversed): deletion of the two §3 table rows (audit row 15).** Sol took the audit's "delete the rows" option because no registry or round7 source lists the workload levels or the three magnitudes. Consequences the lead found: (a) registry row `DS-02` ("Section 3 characterization specification row… `**Workload response:**` content anchor", `results-fill-registry.md:822`) now anchors on deleted text — the registry is outside F's scope; (b) the §3 prose that served those rows survives ("For workload response, an independent unit is one separately admitted bundle…" `:246-251`, and the null-test interval formula `:253-270`), so the table no longer describes the calculations the prose sets up. Options: (i) keep the deletion and delete or re-home the orphaned prose (seat with §3 authority) and retire DS-02; (ii) restore the two rows from base with only the code-name cure and de-numbered "every registered level / magnitude" wording (no new numbers) and accept the unlisted-levels first-use debt; (iii) list the levels/magnitudes from the frozen plan if a registry row can be issued for them. Recommendation: (i) if W2 stands (ladder not collected for this paper), else (iii).

**F2 — corrected claim: "would have caught these 24".** Sol's "negative fixture: expected failures=24" is against the synthetic fixture `tests/fixtures/paper_first_use_pre_cure.md`, not the real pre-cure draft. Lead replay of the NEW test against the real `33290b8b` draft (`PAPER_FIRST_USE_DRAFT=<git show 33290b8b:…>`): `FAILED (failures=4)` — terms `members`, `false-difference components / false-difference`, `independent units`, `Commanded pulses` (each first occurs, in an inflected/compound form, in an earlier section than its ledger home). The old exact-string test on the same draft: `OK`. The other 20 audit rows were terms with NO ledger row at all, which no matcher can see; Sol added ledger rows for every one of them (224 → 243 terms), so they are now under test going forward. The fixture test is a matcher-coverage regression (24 constructed forms), and the lead's mutation probe (revert the locator to exact-only) makes `PaperFirstUseFormRegressionTests` FAIL — it bites.

**F3 — Figure 3.** The build instruction is gone and `fig3_decision_gates.svg` exists, but the build note at `:880` still says "Build Figure 3 from three distinct paths" — a build note, not reader text; left alone.

## Executed evidence

### First-use table for sentences added or changed (lead re-run on `b10abe47`; line = current draft line)

| Term | First used | Built/glossed | Verdict |
|---|---:|---:|---|
| Apple M3 Max, 128 GB, powermetrics configuration (scope) | 102-103 | 102-105 | PASS |
| MLX | 103 | 103-104 | PASS |
| resolution bound / detection floor / cell floor | 118-121 | 118-121 (cell floor's final-value sense restated at 680) | PASS |
| U_point / U_corner | 123-125 | 123-125 | PASS |
| member; A/B/B/A block | 129-130 | 129-130 | PASS |
| timing-error sign; shared sign; local sign | 131-134 | 131-134 | PASS |
| reasoning disabled | 146 | 146 | PASS |
| declared machine state; frozen | 173 | 173 | PASS |
| signal/fit/range/trace-coverage/completeness checks; shared search-work limits | 175 | 175 (pointer to A.3.5 / A.3.7) | PASS (forward pointer, explicit) |
| first-record endpoint; four evidence constraints; four allowances | 177 | 177 | PASS |
| calibration-acceptance rule | 179 | 179 | PASS |
| entry check | 183 | 183-184 | PASS |
| reference runs | 184-186 | 184-186 | PASS |
| gross energy; idle-subtracted energy | 193-195 | 193-195 | PASS |
| identical-condition null-test blocks | 266 | 266-267 | PASS |
| package power | 316 | 316-317 | PASS |
| retired calculation | 399-400 | 400-404 | PASS |
| July 25, 2026 diagnostic window | 399 | 399 (date is the definition) | PASS |
| close-out artifact | 550-551 | 550-552 | PASS |
| energy terms | 740 | 740-743 | PASS |
| deterministic-bound kinds | 806 | 805-809 | PASS |
| Figure 3 | 845 | 845-855 | PASS |
| outcome A hardware clause | 834 | 102-105 (Section 1 pointer) | PASS |

### Tests (lead replay)

Fast set on the final tree (`b10abe47`):

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_build
Ran 10 tests in 1.423s
OK (skipped=2)
```

New test vs real pre-cure draft (`git show 33290b8b:docs/paper/draft-v2-skeleton.md`): `FAILED (failures=4)` (terms listed under F2). Old test vs same draft: `OK`.
New test vs synthetic fixture (`PAPER_FIRST_USE_DRAFT=tests/fixtures/paper_first_use_pre_cure.md … test_first_occurrence_is_in_exact_home_section`): `FAILED (failures=24)`.
Mutation probe (locator forced to `_occurs_exact`): `PaperFirstUseFormRegressionTests` → `FAILED (failures=1)`; probe file removed, tree clean.

Baseline reference, canonical checkout at `33290b8b` before any change: full paper suite `OK (skipped=2)`.

Sol's own full-suite run on its delivered tree: `Ran 70 tests in 616.397s — OK (skipped=3)`.

Full paper suite, lead replay on `b10abe47`:

```
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paper*'   (cwd = seat worktree, HEAD b10abe47)
----------------------------------------------------------------------
Ran 70 tests in 613.934s

OK (skipped=3)
```

Skips: two `tests.test_paper_build` tests skip everywhere ("markdown-it-py not installed; the build cannot run here"); the third is environmental to the worktree (see the skip line recorded below), identical on Sol's run.

Third skip: `tests.test_paper_replay_fence.ReplayAgainstPrimaryArtifactsTests.test_every_fenced_value_replays` — "retained capture 20260722T145535-e941c821 is not on this machine" (the untracked corpus is under the canonical checkout, not the worktree; canonical baseline ran it and passed).

### Bridge ceremony

- `session-open` invocation `paper-f-firstuse-20260902T204943`, lease `lease-aaca83ff60d248c9ac57c35ca182e488`, baseline `sha256:31b5c2aa…`; `lease-expand` added `tests:subtree` (the first spec `tests/**` was recorded as an exact entry — harmless).
- `session-close --status DONE` → `SCOPE_VIOLATION` ("HEAD moved but commits were not authorized"; the close has no commit-authorization flag) → thread `waiting_lead`, lease retained.
- Lead adjudication: `scope-check --allow-commits` on `b10abe47` → `SCOPE_OK`, `head_disposition: authorized` ("authorized descendant HEAD movement is owned by the governing write lease"), four paths `in_scope`. The commits are the lead's own. Recorded a terminal `complete` thread event (thread-record rc=0) and released the lease (`release` event 2026-09-03T04:49:33Z).
- Process note for the coordinator: a Sol seat in a LINKED worktree under `workspace-write` cannot `git add`/`commit` (the worktree's index lives under the main repo's `.git/worktrees/`), so "commit on the branch" in seat briefs will always fall to the lead; the close ceremony then needs the lead to adjudicate HEAD movement as above.

## Summary

1. All 23 in-seat audit rows cured (22 in place, row 15 by audit-sanctioned deletion — flagged F1 for a ruling on the orphaned §3 prose and the dangling `DS-02` registry anchor); row 24 (§6) left to seat E; excluded regions byte-identical.
2. §1 scope paragraph names Apple M3 Max / 128 GB / MLX / powermetrics once, early; one appositive bridges resolution bound = detection floor, final value = cell floor; `U_corner` is the single corner symbol.
3. Ledger matcher now counts singular/plural, possessive, and spaced/hyphenated compound forms; it catches 4 real defects on the pre-cure draft (the other 20 were unlisted terms, now all in the ledger, 243 rows); synthetic 24-form fixture + mutation-verified regression test.
4. Lead bench edits (`b10abe47`): removed "the advisor" from reader text and restored the §4 relation; kept concrete names in outcome sentence A.
5. Full paper suite OK (70 tests, skipped=3, environmental); scope `SCOPE_OK`; two commits on `feat/2026-09-02-paper-f`, not pushed; canonical checkout untouched.
