# F2 item repair and issued-pattern assessment — 2026-11-16

User-directed AGENT tooling/draft repair on `audit/2026-11-10-fable`, starting
detached at `ebff15ad2`. `git pull --rebase origin audit/2026-11-10-fable`
completed before edits (already up to date). Intake: M0, no active stop card,
current queue/do-not-do list, orchestration and source-of-truth map; the user's
explicit repair/push direction selects this work ahead of normal queue heads.
The independent review's FINAL-MESSAGE and
`2026-11-16-independent-f2-item-review.md` were read. Authority: RL-169/169a,
RL-171/172/173 and RL-174 B/C. No phase exit or live measurement gate closes.

The user explicitly forbids RUN_STATE edits. That overrides the normal session
handoff requirement; no kernel regeneration is run because it would write that
file. TASK_QUEUE gets a manual repair handoff outside its generated region.
PROJECT_STATUS is unchanged: no advisor-visible scientific state changed.

## Findings disposition and changes

**F1 HIGH fixed.** The census projects only each `runner_receipt.json`'s recorded
`ended.epoch_s`, selects the maximum raw epoch and its exact receipt identity,
then rounds up for shell interval arithmetic. Filesystem mtime never selects the
marker. Missing roots, empty census, unreadable/missing/non-numeric/non-finite/
non-positive/bool stamps and equal maximum recorded epochs stop. Distinct
fractional closes that ceil to the same second still select the correct identity.
The campaign marker remains derived from that selected receipt's span id.
OTHER_CLOSE_EPOCH remains the explicit outside-root close observation.

Applied to **30 unissued draft forms**: four F2, seven 1115 (including both
unissued dev-05 spans), six qualification, the 1118 standing-F0 renewal, and the
12 older RL-172 item/F0 templates. The older forms remain superseded for issuance;
their historical plans/test captures are unchanged. The RL-172/173 generators and
1118 renewal generator carry the repair, and F2/qualification shared gates equal
their embedded copies. The shared rendering source is
`item-drafts-1115/tools/close_census.py`.

**F2 MED fixed.** After a campaign close, require that span's `.ok` or `.air.ok`.
After F0/F2/Part C/session/W1, follow the issued non-campaign Check rule. F2 now
requires explicit verified Check/copy evidence bound to the selected receipt
path and rounded close epoch (`NONCAMPAIGN_COPY_OK`, `_CLOSE_EPOCH`, `_RECEIPT`,
`_RECORD`); an outside-root session binds to literal `OTHER`. Missing, stale,
wrong-path or placeholder proof holds. No F0 marker or new marker producer is
invented. Restore, process-group absence, fence disappearance and the 1200 s
interval remain mandatory. Existing qualification proof inputs are preserved.

**Dates fixed under RL-174 B.** p01 Tue17, p02/p03 Wed18, p04 Fri20; all are whole
PST t0-date windows, shortened by each item's own 24 h expiry and kit expiry.
Monday is withdrawn. Friday explicitly illustrates an F2 piece on a qualification
date after qual-02 and the higher-priority F0 starts. Forecasts are synthetic
examples, never reservations; fresh READY v4/counted work (including qualification)
cedes every F2 arm. The 13010 s protected horizon and pin's admitted launch bands
are unchanged. The actual pinned planner rechecked all four new dates.

**Test portability/evidence.** The 1115 runner/lint now target their own directory,
generate disposable pinned mocks and propagate failure, rather than reading
another scratch tree. The qualification regeneration test runs in an isolated
copy and restores its default outputs there; it cannot overwrite source drafts
or retained evidence. New execution logs/kit reports/comparison diff live under
`evidence/fix-2026-11-16/`. No pre-existing evidence or run bundle was modified.

## Verification

All three current `tests/run_all_gates.sh` runners completed with exit 0 when
invoked with **bash and zsh**, and each exercises the embedded functions in both
shells. Source pin for F2/1115: detached
`/Volumes/JW-EXT/jw-wt/desk-final-pin-2d347f721` at
`2d347f721552fe03bdd19f113e7bad7a7c24908e`. Qualification extracts its own allowlisted
source at `e1b85a59c53bfbeaa3477df46bcbe9dd8fdfc427`. No hardware runner executes.

Per outer invocation (do not confuse doubled runs with distinct cases):

| Runner | Results |
|---|---|
| F2 | 872 gate +144 close/copy regressions; 22 local staging checks; pinned kit/leg-law/queues, eight mock spans, operational Checks and one q600 fake runtime; all pass |
| 1115 final | 238 predecessor/expiry/watcher checks +210 close/copy regressions +360 older RL-172 regressions; syntax lint BAD 0; seven pinned mock spans; all pass |
| 1118 | 1092 gate +246 close/copy regressions; 91 pinned checks; 21 standing-F0 checks; seven isolated generator checks; 74 shell syntax checks and 60 Python compilations; all pass |

The lead additionally ran the universal close/copy regression on all 30 forms:
**960 checks, zero failures** in bash/zsh. This keeps old receipt bytes unchanged
while giving that file a newer mtime, refuses the old marker for the newer uncopied
span, accepts the actual latest marker, rejects invalid/tied closes, and exercises
a live-style F0 path with Check/copy proof but no F0 marker.
[Lead output](2026-11-16-f2-item-fixes-evidence/all-draft-close-regressions.txt).

Independent executing delta review: read-only agent `/root/review_f2_fix`, same
inherited model, tasked under orchestration with the exact F1/F2/date scope. It
reported no blockers, independently ran the 960 cases, checked 60 shell blocks
and 149 Python heredocs, and confirmed all 30 censuses equal the shared program.
Its negative control used the pre-fix dev05-s01 Git blob: the new regression
actually failed because that form accepted the stale marker. Its judgment:
p01–p04 READY as draft tooling, live issue prerequisites pending. No reviewer
writes; final verification, diff, issued-item assessment and push remain lead-owned.

Reproduction from repository root (D is the campaign draft parent):

```sh
D=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign
PIN=/path/to/detached/2d347f721
python3 -B "$D/item-drafts-f2/build_items.py" "$PIN"
bash "$D/item-drafts-f2/tests/run_all_gates.sh" "$PIN" "$PWD"
zsh "$D/item-drafts-f2/tests/run_all_gates.sh" "$PIN" "$PWD"
bash "$D/item-drafts-1115/tests/run_all_gates.sh" "$PIN"
zsh "$D/item-drafts-1115/tests/run_all_gates.sh" "$PIN"
bash "$D/item-drafts-1118/tests/run_all_gates.sh"
zsh "$D/item-drafts-1118/tests/run_all_gates.sh"
python3 -B "$D/item-drafts-1115/tests/test_close_selection.py"
```

Actual logs are per outer shell under each changed folder's
`evidence/fix-2026-11-16/{bash,zsh}/`; final 1115 reruns, including the added older
RL-172 sweep, use `{bash-final,zsh-final}/`. A `JW_DRAFT_EVIDENCE_DIR` override
keeps each invocation separate. Four new-date planner reports are in F2's fix
evidence root. Earlier evidence remains historical.

Source/docs `git diff --cached --check` passes when newly captured evidence is excluded; raw log/diff output whitespace is retained unchanged. Production runner/measurement code, frozen paths,
kit/queue-a bytes and estimator contracts are unchanged; this docs/tooling-only
repair uses the targeted checks above instead of the multi-hour canonical suite.
The existing pinned `return`-in-`finally` SyntaxWarning remains. The ancillary
local fixture orphan census was attempted and returned observation error (exit 2,
`PermissionError: [Errno 1] Operation not permitted: 'ps'`), not an empty census;
no permission bypass was attempted. All supplied runner processes finished and
their disposable directories were removed by their normal cleanup.

## Issued items on origin/main

Read-only Git source: `origin/main` at
`0656dfe3a4263629e1d752933d386b99145fe8ac`. **All five named issued items contain
the same mtime-based selection defect:**

| RUN_STATE item | Issued action | Assessment |
|---|---|---|
| 354 | dev-02-s03, rest of dev-02 | Defect present; same counterexample in bash/zsh |
| 355 | dev-03-s01, counted pilot | Defect present; same counterexample in bash/zsh |
| 366 | dev-03-s02, remainder | Defect present; same counterexample in bash/zsh |
| 367 | dev-04-s01, first span | Defect present; same counterexample in bash/zsh |
| 372 | dev-04-s02, second span | Defect present; same counterexample in bash/zsh |

[Reproducer](2026-11-16-f2-item-fixes-evidence/check_issued_items.py) and
[30 observations](2026-11-16-f2-item-fixes-evidence/issued-items.txt) use only issued
source text and disposable synthetic files. Exit 0 confirms the expected
vulnerability/control observations; it is not a gate-correctness pass. With
normal mtime order, each issued copy gate holds for an uncopied latest receipt
and accepts its actual marker. Giving the old receipt a newer mtime, with its
bytes unchanged, makes each gate accept the old span's valid marker while the
real latest span remains uncopied. PRIOR_CLOSE_EPOCH is correct throughout.

**Normal-operation assessment:** ordinary fresh receipt creation writes each
receipt once at close, so its mtime tracks close order. Read-only Checks, hashing
and normal outbound offload/copy do not themselves reorder the originals. The
counterexample therefore is not expected in the ordinary append-only close
sequence. It can occur after a restore, copy-back, touch or rewrite of an older
receipt (or equivalent mtime reordering), without forgery or a wrong PRIOR input.
PRIOR protects elapsed time but does not bind marker identity. This is a latent
fail-open copy gate, not evidence that a particular live arm violated copy policy.
No live receipt, offload archive, hardware state or custody data was inspected,
so this task cannot establish whether it happened in production. Future/reissued
items should use the corrected forms. No issued item or RUN_STATE was edited.

## Per-item status and handoff

| F2 item | Draft quality | Issuance |
|---|---|---|
| p01 Tue17 | READY | NOT READY until lead records admission/re-check adoption, same-pin smoke/hand release, staging, actual issue/watcher stamps and current operational proofs |
| p02 Wed18 | READY | NOT READY until p01's live hand-read PASS, committed queue-b path/hash, applicable L005/class A releases, staging and fresh stamps/proofs |
| p03 Wed18 | READY | Same live holds as p02; p02's clean close mandatory at arm |
| p04 Fri20 | READY | Same live holds as p02; p03's clean close mandatory; READY qualification/v4 takes priority |

No synthetic receipt is a live prerequisite. The lead's next exact step is to
adopt the corrected forms, fill p01's actual current prerequisites and issue only
inside its new date/24 h bounds. It must not reuse a missed date or cross the
piece-1 hand gate. Handle issued-form supersession separately on main if a new
item is needed; this audit-branch repair grants no new arm authority.

Workspace was initially clean and is quiescent for lead bookkeeping. Changed
files are the draft/template/generator/test/STATUS groups described above, new
synthetic proof directories, this report/support and a TASK_QUEUE handoff.
RUN_STATE remains byte-for-byte equal to the starting blob, SHA-256
`acb7f4f0e5b3997c958bd4850cbb86278643e6273203d401f50f5c140c911c51`.
No MBP/SSH contact, real measurement, custody read, integration installation,
external message, merge or deployment occurred. Git commit/push is explicitly
user-authorized; commit trailers name Sol as requested.
