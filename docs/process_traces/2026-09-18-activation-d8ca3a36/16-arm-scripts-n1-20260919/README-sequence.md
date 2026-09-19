# 09-19 v2 equivalence night: bench sequence (not executed)

Candidate triple:
`(d079-epoch-25g83-derivation-n1-20260919, /Users/edr/JouleWise-measurement-20260919-derivation, __H__)`.
These are preparation artifacts. Acceptance remains blocked by the test-scope
and lease findings in [verification.md](verification.md). The magistrate reviews and executes each
step separately, retaining stdout, stderr and exit status. No script sends
mail. No script here has been run by the implementing seat.

## Run order and manual acts

1. Review, commit and push the handback rewrite and inventory entry to main
   through the lead's normal gate. Set `H` in `arm-env.zsh` to that reviewed
   full main SHA, replacing the literal `__H__`. The handback's placeholder
   means its containing commit; retain the resolved triple in the notice and
   arm record. Run copies of these scripts outside the fresh measurement
   clone so filling H does not dirty that clone. Keep the entire directory
   together: each zsh step sources its sibling `arm-env.zsh`.
   In the bench shell, enter that scripts directory with a guarded `cd`,
   then `source ./arm-env.zsh` so the manual acts below also have `$STAGE`
   and `$ATTEMPT_DIR`; child-script exports do not persist in the parent.
2. `zsh step0-retire.zsh`. Before any move, this checks launchd labels, both
   existing harvest archives, every inventory entry, complete archive/live
   bytes (including `results-clone/`), and SHA256SUMS from each live root.
   It resolves the existing `*-harvest-2026091x` archive, requiring exactly
   one directory per plan. Any precheck mismatch exits 3 with neither root
   moved. The pre/post inventory excludes no live paths; the historical
   inventory itself excludes `results-clone/`, as record 48 did. Save the
   output and `retirement-evidence/`. A failure after a move requires lead
   inspection; never blindly rerun or reverse a completed move.
   Manually export `RETIRED_0917_ROOT` to the exact `RETIRED:` path printed
   for 09-17. Both old clones stay in place. Discovery must be empty.
3. `zsh step1-clone.zsh`. Confirm origin/main equals H, fresh clone and
   detached HEAD, Python 3.13 lock match, read-only canonical ledger source,
   byte-equal ledger copy, authenticated head-equals-pin, clean tree.
4. `zsh step2-desk.zsh`. Review BOTH rc-3 epoch reports: only the explained
   OS/sampler mismatch is acceptable; any ledger error stops. Review
   pre-registration revision 3, D-166, v2/2 `DIAGNOSTIC_NO_PACK`, 9000 s,
   staged plan, input/wrapper hashes, `--check`, `--verify`, syntax,
   preflight, rendered agents and schedule. No v4 flags apply.
5. Close the delegated seats and foreign sessions using their real controls.
   `zsh step3-notice.zsh` creates attempt `000001` exclusively, saves exact
   staged bytes and `attempts.json` = `[]`, observes census twice 30 seconds
   apart and raw `/usr/bin/pgrep -lf 'codex|claude|t3'`, then writes
   `notice-body.txt` and an unaccepted `notice.json` TEMPLATE. The real-class
   census rc 0 is diagnostic; review foreign PIDs, descendants and workloads.
6. Manually send the generated recipient, subject and body through the
   authorized Gmail tool. Record actual acceptance epoch, message id,
   thread id, accepted body/digest/H, fresh census and veto/directive/STOP
   observations in `$ATTEMPT_DIR/notice-evidence.txt`. In `notice.json`,
   replace `__MESSAGE_ID__`, `__THREAD_ID__`, `__ACCEPTED_EPOCH__` (the last
   becomes a JSON number), and set `accepted`, `prerequisites_clear` and
   `veto_clear` to true only from actual observations. Preserve every
   observed NO, including on old threads, and all blockers. Record any
   unreadable thread limitation. Accepted send precedes publication, with
   no extra notice waiting interval. Do not clear a NO by making a new thread.
7. Supply the preserved successor-count evidence. Copy
   `successor-count.template.json` to `$ATTEMPT_DIR/successor-count.json`.
   The magistrate reviews the predecessor's arm history and subsequent
   arm records, writes that review to a separate text file naming its
   sources and the predecessor, and records the observed integer count
   plus that file's absolute path in the JSON. Export
   `SUCCESSOR_COUNT_EVIDENCE="$ATTEMPT_DIR/successor-count.json"`.
   No checked-in harvest file contains this count; absence is NOT zero.
   A missing, unsubstantiated or nonzero count stops step 4. This manual
   evidence is required by D-182, not a new retry authorization.
8. Refresh manual veto/directive, census, power/load and watchdog gates, then
   `zsh step4-publish-install.zsh`. It invokes `step4a-successor-evidence.py`
   using `RETIRED_0917_ROOT`, the retired refusal/result/courier files,
   tracked harvest hashes and ledger dry run, unchanged ledger bytes in the
   new clone, and the explicit count evidence. Every assertion names its
   source. It writes `successor-evidence.json` once. Any missing raw
   `C5.measured.zero_capture_evidence` is supplemented only in this separate
   copy with measured file observations; the raw receipt stays unchanged.
   `successor_arm_allowed(now, context, notice, predecessor_result,
   harvested_receipt, delivery)` must allow before `os.replace`. Refusal
   exits 3 without moving the staged plan. Then verify the published
   wrapper, execute the owner-present launchd access probe, inspect its
   receipt, and install FROM the pinned clone. After a consent dialog,
   follow the standing probe-repeat procedure before installing.
9. `zsh step5-verify-and-exit.zsh`. Verify loaded labels, both calendar
   mappings against `schedule(plan)`, all plist arguments against the
   rendered agents (including courier arguments), absolute interpreter,
   working directory, saved plan bytes, wrapper sidecar and hashes. Retain
   the actual post-install `night/` baseline and probe receipt. No future
   result is inferred from successful installation.
10. Lead only: record/push the exact frozen triple, plan digest, notice,
    evidence, installed schedule, harvest pointer and consumption of the one
    D-182 successor for predecessor 09-17; update the RUN_STATE
    pointer through its owning workflow. These bookkeeping paths are outside
    this delegated seat's scope. Terminate the magistrate, every owned seat,
    MCP child and helper **strictly before 2026-09-18 23:52:00 PDT**.
    Announcing exit does not terminate a process. Do not signal foreign
    sessions. No agent performs a quiet measurement during this sequence.

## Boundaries

| Boundary | PDT | UTC | Epoch |
|---|---|---|---|
| Install close (excluded) | Sep 18 23:50 | Sep 19 06:50 | 1789800600 |
| REQUEST / exit strictly before | Sep 18 23:52 | Sep 19 06:52 | 1789800720 |
| TERM | Sep 18 23:54 | Sep 19 06:54 | 1789800840 |
| KILL | Sep 18 23:55 | Sep 19 06:55 | 1789800900 |
| t0 | Sep 19 00:00 | Sep 19 07:00 | 1789801200 |
| Acquisition end | Sep 19 02:30 | Sep 19 09:30 | 1789810200 |
| Completion / courier | Sep 19 02:35 | Sep 19 09:35 | 1789810500 |
| Daily dead-man | Sep 19 03:35 | Sep 19 10:35 | 1789814100 |

600 s settle + 11 × 600 s cadence + 480 s last capture = 7680 s;
generator minimum 7980 s; allocated window 9000 s. The notice body derives
all timestamps, install spans, hashes and pins from actual staged bytes.

## Preconditions (scout record 12, for the magistrate to check)

| Done | Gate | Evidence | Actor |
|---|---|---|---|
| [ ] | Retirement | Both archives/inventories match live bytes; labels absent; both roots moved and reverified; discovery empty; clones untouched. A230 conflict remains recorded. | Magistrate under this brief's move direction |
| [ ] | Clone / ledger | H is merged/pushed; detached clean clone, lock diff clean, copied ledger matches source and committed pin with custody authentication. | Magistrate |
| [ ] | Registration | Both explained rc-3 reports reviewed; revision-3 preregistration hash/source digest; separate D-166 path/hash. | Magistrate |
| [ ] | Readiness / dry-run binding | Pack-only binding N/A: C2=no_pack_by_design; render, preflight, owner-present access probe and cleanup passed. | Magistrate / Ed consent |
| [ ] | Census | Two observations 30 s apart plus final census; no foreign processes at publication; raw census empty by t0. | Magistrate / Ed close own processes |
| [ ] | Load / power | Record `/usr/sbin/sysctl -n vm.loadavg`, `/usr/bin/pmset -g batt`, `/usr/bin/pmset -g`, `/usr/bin/pmset -g therm`; resolve the harvest's churn finding. v2 load >2.0 refuses. | Magistrate observes; Ed cures |
| [ ] | Notice / veto | Accepted exact-byte notice; all observed NOs preserved; STOP/standdown absent; no unresolved owner directive; watchdog state reviewed. | Magistrate; Ed NO |
| [ ] | D-182 predecessor | Retired 09-17 hashes, absent start/session/reservation/capture, courier delivery, explicit zero successor-count review; fresh id/digest/notice; ≥60 s after terminal write. | Magistrate |
| [ ] | Deadline / handoff | Probe and install finish before 23:50; durable triple and RUN_STATE pointer; all owned agents gone before 23:52. | Magistrate |

## Source compatibility and unchanged-rule findings

- 09-17 `arm-step4.zsh:43–60` used `retry_allowed`; this block now calls
  `successor_arm_allowed` with `plan_bytes`, `saved_plan_bytes`,
  `reviewed_head`, `install_close_epoch_s`, `plan_max_age_s`, plus notice,
  result, supplemented harvested receipt and delivery. `attempts.json`
  remains empty; the predecessor never enters same-candidate history.
- PR #355 was already in the last arm's H. Its `rev1.md` filename remains
  unchanged, with revision-3 contents. PR #357 / #358 require the successor
  call above; no other predecessor CLI argument needed replacement.
  The generator's `--check` is included per the scout; no v4 flags are used.
- Steps 1/2 preserve the old command arguments with sibling env sourcing,
  guarded `cd`, printed assertions and the requested ledger-source check.
  Post-install inspection is moved from step 4 to step 5; complete launchctl
  dumps replace `head -30` / `head -20` pipelines so pipefail cannot trip on truncation.
- At BASE_HEAD, the inventory has entries through 09-16, not a 09-17 entry.
  The new entry uses exactly the existing five fields; `Status: pending-arm`
  lives in `notes`, since the inventory has no status field.
- Handback recovery, ARM-RETRY-POLICY (including R1 and D-182), census,
  scientific decision rule and standing-rule prose are preserved. Its
  §Next lane still says `REFUSAL-FAST-RETRY-01 is queued, not landed`,
  conflicting with the implemented D-182 route; the retention sentence
  still conflicts with runbook discovery (A230). Its Purpose census block
  retains the dated 09-16 candidate history. These require lead/owning-rule
  adjudication, not an unauthorized process-rule rewrite by this seat.
  The old instruction to re-pin the pre-registration is also kept verbatim
  with the factual note that PR #355 already supplied that re-pin.
- Runbook §1.4 also still defines the plan span as 25 minutes before t0,
  while §0.6 and the driver use eight. No rule text is changed here.

The implementing seat runs syntax/static checks and isolated fixture tests
only. Full-suite, exact-head diff review, live archives, notices, census,
consent, probe, install and measurement verification remain lead-owned.
