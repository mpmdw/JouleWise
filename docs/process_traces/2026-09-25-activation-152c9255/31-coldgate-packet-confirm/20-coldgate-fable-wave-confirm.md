# Cold Fable confirm WAVE-CONFIRM-01 — ruling

Judge: Claude Fable 5.1 (claude-fable-5-1), cold session, foreground only, no subagents, no background tasks. Session start 2026-09-25 19:25 UTC; ruling written 19:38 UTC. Judge worktree HEAD `09c4875d` (unmodified; only this file written). All test runs in a `/tmp` clone built from a `git bundle` of the two PR branches and `origin/main`; the canonical root, night-custody, and LaunchAgents were not touched; no sudo, launchctl, powermetrics, systemsetup or pmset.

## 0. Disclosures and trust anchors

**Auto-loaded context (not requested):** the harness injected `/Users/edr/.claude/CLAUDE.md`, the worktree's tracked `CLAUDE.md`, and the `MEMORY.md` index. None was used for any finding. I did not open RUN_STATE.md, TASK_QUEUE.md, council logs, run reports, memory files, CLAUDE.local.md, or any trace file outside the packet directory except the two files the charge lists: `24-finalpass-packet-prl/20-fable-final-pass-prl.md` (read in full at `58d9ddc3`, as the prior verdict C1 asks me to protect) and `15-prr-review/06-final-conformance-lens.md` (grep of verdict lines only). "Record 00 item 84/86" were NOT read (narrative record); the 613-test/UTC-LA-Tokyo bench claim is therefore replaced by my own runs below.

**Validator receipts** (method: `python3 scripts/validate_gate_packet.py --packet …/00-charge.md --charter docs/process/coldgate_charter.md …`, then independent `shasum -a 256`):

| Run | Expected charter sha | Observed | Result |
|---|---|---|---|
| 1 (deliberate typo) | `…c95d82` | `099de884…c95d81` | `REFUSE`, reason `charter_trusted_observed_mismatch`, rc 2 |
| 2 (correct) | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | same | `PASS`, rc 0 |

Packet sha expected = observed = `c4bdec1ddfe43dabcae7cc27e11953ab9bcd9e04fa42694fc1f916c6d95b8424`; exhibit manifest `6f3cf641…fc617`; all four exhibit digests observed = expected. Independent `shasum` agreed on both anchors. Judging proceeded.

**Commit identity (all verified present):** `99495ba9`, `58d9ddc3` (= local and `origin/feat/2026-09-25-acc-launch-context`, = GitHub PR #412 `headRefOid`), `2bbcc779`, `e77ec15d` (= local and origin branch head, = PR #413 `headRefOid`), `d48bd18f`, `d9ed116f`, `f6e6d162`, `95521871` (= `origin/main`). Merge-base of both PR heads with main: `c034a56f`.

## 1. C1 — PR-L head 58d9ddc3

**Diff equality: AFFIRMED.** `git diff 99495ba9 58d9ddc3 -- . ':(exclude)docs/process_traces/2026-09-25-activation-152c9255'` written to a file has sha256 `02537836140d694ecc484388059042f57dd75451293a149e364d54d36e694030` = ex-01's digest; `diff` reports identical bytes. The only non-records file in `99495ba9..58d9ddc3` is `tests/test_install_night_agent.py` (+19/−1), introduced by `2e522d1a`; `58d9ddc3` is records-only on top (`git diff --quiet 2e522d1a 58d9ddc3` outside the trace directory: empty; 230 files, all under `docs/process_traces/2026-09-25-activation-152c9255/`).

**Fix correctness: AFFIRMED.** Mechanism verified in the code at `58d9ddc3`: `_prepare_receipt` (`tests/test_install_night_agent.py:159-185`) calls the fixture oracle `write_matching_probe_receipt` (`tests/test_run_night.py:189`), which renders `run_night.schedule(parsed_plan)` and `night_agent_install.Prepared(...).launch_context()` in the test process; the installer subprocess receives `self.environment`, and `_install_local_t0` (`:577`) sets `self.environment["TZ"] = "America/Los_Angeles"`. `StartCalendarInterval` is a local-time rendering, so when the test process TZ differs from the subprocess TZ the receipt's `launch_context` digests differ from the install's and the installer refuses. The fix sets `os.environ["TZ"]` to the subprocess value only when `self.environment` carries one, calls `time.tzset()`, and restores the prior value (or pops it) in `finally`. When `self.environment` has no `TZ`, both processes inherit the same environment and the fix is a no-op. This is the correct equivalence.

Executed evidence (clone, foreground):

| Tree | Command | Result |
|---|---|---|
| `99495ba9` (pre-fix) | `TZ=UTC python3 -m unittest tests.test_install_night_agent` | Ran 65 in 47.4 s — FAILED (failures=2): `test_installer_accepts_ordinary_20260916_0256_whole_minute`, `test_installer_accepts_spring_20260308_0430_after_gap`, both `AssertionError: 0 != 2 : probe receipt launch_context differs from install: com.joulewise.night` |
| `58d9ddc3` | `TZ=UTC python3 -m unittest tests.test_install_night_agent` (the charge's mandated run) | Ran 65 in 48.3 s — OK, rc 0 |
| `58d9ddc3` | `TZ=Asia/Tokyo …` same module | Ran 65 in 48.7 s — OK |

The pre-fix reproduction matches the charge's description exactly (two installer tests, UTC only) and is itself evidence that the installer's `launch_context` comparison is a live check, not weakened: the fix changes only what the fixture renders, never what the installer compares.

**Weakens nothing the final pass relied on: AFFIRMED.** PRL-FINALPASS-01 §3 executed 463 tests in `test_night_gate`, `test_run_night_probe_cadence`, `test_run_night_probe_worker_cadence`, `test_launch_context_no_qos_override`, `test_arm_retry`, `test_evidence_arm_sequence`, `test_run_night`, `test_night_agent_install` and the merged-tree `gen_state`/`test_gen_state`/`test_arm_retry`; `tests.test_install_night_agent` was not among them, and no production file changes. §1 R2's recording chain (installer `launch_context` refusals) is what the pre-fix failure exercised; it still fires on a real mismatch.

**CONFIRM MERGE of 58d9ddc3: NOT CONFIRMED — the head cannot be merged.** This is a defect the packet omitted. Deciding probes:

- `git merge-tree --write-tree 95521871 58d9ddc3` rc 1: `CONFLICT (add/add)` in `docs/process_traces/2026-09-25-activation-152c9255/00-activation-record.md` (main blob `e0dfcc1c`, 139 lines, added by PR #411; PR-L blob `e60fc46e`, 260 lines). No other path conflicts. A real merge in the clone reproduced it; `merge-tree` of main with the pre-records head `2e522d1a` is clean (rc 0), so the records-only commit `58d9ddc3` created the conflict.
- `gh pr view 412`: `mergeable: CONFLICTING`, `mergeStateStatus: DIRTY`. `gh pr checks 412`: "no checks reported" on `58d9ddc3` — GitHub does not run `pull_request` workflows on a PR whose merge commit cannot be computed, so neither `ci` nor `gate-ledger` has run on this head. Last runs on the branch: `2e522d1a` `ci` success, `gate-ledger` FAILURE at step "Validate the twelve-row gate ledger in the PR body"; `99495ba9` both failed.
- Main's 139-line record is a byte-exact prefix of PR-L's 260-line record (`diff` of main's file against `head -139` of PR-L's: empty), and PR-L's and PR-R's record blobs are identical (`cmp` clean). The resolution is therefore mechanical.

**Ruled text (execute without choosing):**

> C1-a. With `feat/2026-09-25-acc-launch-context` checked out at `58d9ddc3`, run `git merge 95521871`; it stops on the single conflict. Resolve by keeping PR-L's version verbatim: `git checkout --ours -- docs/process_traces/2026-09-25-activation-152c9255/00-activation-record.md && git add <that path> && git commit --no-edit`. The result is H. Confirm `git show H:<that path> | shasum -a 256` equals `git show 58d9ddc3:<that path> | shasum -a 256` (blob `e60fc46e`). No other file may change.
> C1-b. Before merging, all four hold: (1) `git merge-base --is-ancestor 58d9ddc3 H` rc 0; (2) `git diff --quiet 58d9ddc3 H -- . ':(exclude)docs/process_traces/2026-09-25-activation-152c9255/'` rc 0; (3) `gh pr view 412 --json mergeable -q .mergeable` prints `MERGEABLE`; (4) `gh pr checks 412` shows `gate-ledger` pass on H and no failed check. The `ci` check on H may still be pending at merge time: the non-records code of H equals `2e522d1a`, where `ci` passed, and equals `58d9ddc3`, where I ran the module under UTC and Tokyo.
> C1-c. If (1)–(4) hold, H is CONFIRMED for merge as PR-L under this ruling; no further cold gate is required for H. If any fails, H is not confirmed and a new packet is required.

Charter §9: two consecutive `gate-ledger` failures on this PR (`99495ba9`, `2e522d1a`) have the same signature (PR-body ledger). `58d9ddc3`'s message claims to supply the ledger evidence, but nothing has been able to run on it. C1-b(4) is the executed proof this ruling requires instead of a third blind attempt.

## 2. C2 — PR-R head e77ec15d

**Records-only: AFFIRMED.** `git diff --name-only 2bbcc779 e77ec15d` lists 81 files, +6744/−0, every path under `docs/process_traces/2026-09-25-activation-152c9255/`; filtered for anything else: none. ex-02's "(empty above = records-only)" is accurate. The conformance lens at `e77ec15d` line 1 reads "**Verdict: CONFORMS.** The delta 8cd9e831..2bbcc779 …" as the charge states; I did not re-audit F1–F3, which PRR-FINALPASS-01 and the lens own.

Merge state verified: `git merge-tree --write-tree 95521871 e77ec15d` rc 0 (PR-R already contains main via `8cd9e831`); `git merge-tree --write-tree 58d9ddc3 e77ec15d` rc 0; `gh pr view 413`: `mergeable: MERGEABLE`, `mergeStateStatus: BLOCKED` (checks running); `gh pr checks 413` at 19:26Z: `gate-ledger` pass, `build`/`changes`/`fences` pass, nine `test`/`calibration-*` jobs pending. Because PR-L's record blob equals PR-R's, merging H (C1-a) first leaves PR-R conflict-free.

Additional executed evidence: the only production change in PR-R's fix round `2bbcc779` outside tests is two regexes in `scripts/issue_calibration_acceptance_generation.py:1283,1288` (`<RENDERED-PLIST-SHA256:…>` → `<TEMPLATE-SHA256:…>`, "rendered-plist digests …" → "template digests …"). That script is imported by `scripts/epoch_equivalence_check.py:108`, `scripts/issue_epoch_continuation.py:46` and `scripts/sim_acc_25g83_rev5.py`, whose test modules `tests.test_epoch_continuation` and `tests.test_epoch_equivalence_check` are NOT in ex-04's list and were last run in ex-03 on a tree without `2bbcc779`. I ran both at `e77ec15d`: Ran 90 in 49.9 s — OK.

**Ruled text:**

> C2-a. `e77ec15d` is CONFIRMED for merge as PR-R, to be merged only after H (C1-c) is on main, and only when `gh pr checks 413` shows no failed check (pending `ci` jobs must have completed; if any fails, stop and open a new packet). No new cold gate is required for the PR-R merge itself.
> C2-b. The A-R5a-1 seal step in `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` names "the commit GitHub reports as PR #412's merge commit (`gh pr view 412 --json mergeCommit`)". With H merged by GitHub, that commit exists; use it, not H and not `58d9ddc3`.

## 3. C3 — Row 9 evidence (ex-03 + ex-04)

**Finding on ex-03.** The full suite ran at `d48bd18f` = main `95521871` + PR-L at `1bdbca1d` + PR-R at `8cd9e831`. By ancestry (`git merge-base --is-ancestor`, each rc 1) that tree contains NONE of: `99495ba9` (the PR-L final-pass candidate), `2e522d1a` (the fixture fix), `2bbcc779` (the PR-R fix round), `f6e6d162` (A292). The charge's phrase "the first integration tree" is true but does not disclose this. Delta `d48bd18f..d9ed116f` outside records: `joulewise/scored_reduce.py` (A, A292), `scripts/issue_calibration_acceptance_generation.py` (M), `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (M), `docs/decision_log.md` (M), plus six test files. The two full-suite failures: I ran `test_g4_real_ruled_census_pgrep_dialect` and `test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child` alone at `58d9ddc3`: Ran 2 in 3.2 s — OK. The census error's pattern (`powermetrics|window-chain|run_campaign|tail -f|…`) is a live-process census and depends on what else the machine was running; the exhibit does not record the offending process line, so "known defect" is the charge's characterisation, not shown in ex-03.

**Finding on ex-04.** `d9ed116f` contains `2e522d1a`, `2bbcc779`, `f6e6d162`, `95521871` (each rc 0) but NOT the records-only heads `58d9ddc3`/`e77ec15d` — immaterial, since those add no code (§1, §2). Every test module that references the changed production files (`git grep` at `d9ed116f`: `test_acc_25g83_rev5`, `test_issue_calibration_acceptance_generation`, `test_night_gate`, `test_preregistration_chain_digest`, `test_scored_reduce`) is in ex-04's list, and the PR-L test files are covered by `test_install_night_agent`, `test_run_night_probe_worker_cadence`, `test_night_agent_install`, `test_arm_retry`, `test_gen_state`. Two transitive importers' modules were missed (`test_epoch_continuation`, `test_epoch_equivalence_check`, §2) — cured by my 90-test run. `joulewise/scored_reduce.py` has no importer under `joulewise/` or `scripts/` at `d9ed116f`, so the wave tree without A292 (main + PR-L + PR-R) loses nothing ex-04 exercised for PR-L/PR-R; `python3 scripts/gen_state.py --check` on the main+PR-L work tree: rc 0.

**Ruled text:**

> C3. Row 9 is adequately evidenced for this wave by ex-03 + ex-04 + the runs recorded in this ruling (UTC/Tokyo module at `58d9ddc3`; the two known failures alone, 2 OK; `test_epoch_continuation` + `test_epoch_equivalence_check` at `e77ec15d`, 90 OK), PROVIDED C1-b(2) holds for H. No additional run is required. If C1-b(2) fails (H changes any non-records file), rerun ex-04's fifteen modules plus the two named here on H before merging.

## 4. Findings (severity independent of verdict)

- **BLOCKER-1.** `58d9ddc3` is unmergeable (add/add on `00-activation-record.md`; GitHub `CONFLICTING`/`DIRTY`) and has no hosted check run. The packet, assembled 12:27 PDT for "the exact merge heads", omits the mergeability state. Cure: C1-a/C1-b. Packet-hygiene defect (charter §6: omitted contrary evidence).
- **MATERIAL-1.** ex-04's "every delta module" omitted `tests.test_epoch_continuation` and `tests.test_epoch_equivalence_check`, both importers of the one production script PR-R's fix round changed. Cured by execution here (90 OK). Future packets: derive the module list by `git grep` of every changed production module and its importers, and paste that derivation.
- **MATERIAL-2.** `gate-ledger` failed at `99495ba9` and `2e522d1a` with the same signature; the cure commit has never been checked. C1-b(4) converts this from a claim into an executed result before merge.
- **NIT-1.** ex-03 carries no statement of tree composition; the reader cannot see that the full suite predates the PR-L final-pass candidate. State the merge parents in the exhibit.
- **NIT-2.** The charge's bench claims (613 tests, three timezones, record 00 item 84) point at a narrative record and are unverifiable from the packet; superseded by my runs, not relied upon.
- **NIT-3.** ex-03 does not include the census test's matched process line, so its classification as a "known defect" rather than a real contaminant is unverified here. Record the `pgrep` output in future full-suite exhibits.

## 5. Two-line summary

PR-L's fixture fix is correct and cures the UTC failure (reproduced at `99495ba9`, passes at `58d9ddc3` under UTC and Tokyo; diff byte-identical to ex-01), but `58d9ddc3` itself cannot merge: it conflicts with main on the activation record and has no hosted check; merge the successor H under C1-a/C1-b, no further cold gate needed.
PR-R `e77ec15d` is records-only, merges cleanly after H, and is CONFIRMED (C2-a); row 9 is adequately evidenced once this ruling's runs are counted (C3), with two missed importer modules now executed.

Charter §5: I disagree with the lead's implied disposition that `58d9ddc3` is a mergeable candidate; I concur with the lead on the fix's correctness, on PR-R, and on ex-04's sufficiency for the modules it lists.
