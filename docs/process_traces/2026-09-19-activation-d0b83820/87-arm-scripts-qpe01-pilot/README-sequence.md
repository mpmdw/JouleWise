# QPE-01 pilot night one: bench sequence, prepared 2026-09-19

**BLOCKED AT THE PINNED H. Do not run this sequence at the bench yet.** All
requested scripts are present and syntax/fixture checked. Two contract conflicts
below require the lead's ruling. The publication guard deliberately exits 3;
nothing has been armed. The generated notice is a draft, not a sendable claim.

Authority: record 85 (`85-pilot-night-one-arm-recipe.md` in the magistrate's
activation worktree), `docs/process/NIGHT_HANDBACK.md` (evidence amendment and
ARM-RETRY-POLICY), and `docs/phase_2/derivation_night_runbook.md` §0–§1.5.
Template: `2026-09-18-activation-d8ca3a36/16-arm-scripts-n1-20260919/`.
The task's evidence deltas replace calibration-specific instructions only.

This is one idle-variance evidence night: 600 s settle, twelve 600 s envelopes,
each with a 480 s interior beginning 60 s after its scheduled start. The
programmed span is 7,800 s inside 9,000 s. The protocol fixes 100 ms power
sampling and a 30 s busy-core journal. There is no load generator, model,
calibration-ledger session or pack. Busy cores remain a covariate; no new
quiet-admission threshold is activated. Results remain PROVISIONAL.

## Fill-in values and boundaries

Fill only `NIGHT_DATE` (YYYYMMDD, the local date of t0) and `T0_EPOCH_S` in
`arm-env.zsh`. Pick a whole, unambiguous local minute at least 40 minutes after
the intended initial arm, within 36 hours of authoring. The env refuses unset
placeholders, a date mismatch or a non-minute epoch. H is already fixed to
`a9e48ae900a608b3254a732fb8e7463d66bdef1e`; changing it requires a new lead brief.
Every runtime Git operation below is in the fresh clone, never the canonical
checkout. The lead rechecks H is an ancestor of fetched `origin/main`.

The derived triple is `(qpe01-pilot-n1-<date>,
/Users/edr/JouleWise-measurement-<date>-qpe01-pilot-n1, H)`.
Custody is `/Users/edr/night-custody/<PLAN_ID>`; staging is
`/Users/edr/night-plan-staging/<PLAN_ID>/night_plan.json`.
Neither `SESSION_ID` nor `EVIDENCE_ROOT_ID` has a reader in this evidence chain.

| Boundary | Derived epoch |
|---|---|
| Install close, excluded | t0 − 600 |
| REQUEST; all owned agents exit strictly before | t0 − 480 |
| TERM | t0 − 360 |
| KILL | t0 − 300 |
| Acquisition end | t0 + 9000 |
| Completion / courier deadline | t0 + 9300 |
| Daily dead-man | ceil((t0 + 9300 + 3600) / 60) × 60 |

The notice prints local time, UTC and epoch for every boundary and prints the
actual install-day spans from `schedule(plan)`. The helper checks install close
and dead-man against that same driver. The 40-minute initial-arm choice does
not redefine the existing exclusive install close or retry policy.

## Run order and exit conditions

After resolving the blockers, the lead reviews each step separately and keeps
stdout, stderr and exit status. Keep the directory together, outside the fresh
measurement clone. Step 0 must be run from this authoring worktree so it can
find the read-only census implementation. It executes the supplied project
interpreter but writes nothing in the canonical checkout. Use a guarded `cd`
to this scripts directory and `source ./arm-env.zsh` in the bench shell;
exports in a child script do not persist in its parent.

1. `zsh step0-precheck.zsh`: requires exactly `com.joulewise.magistrate` among
   loaded JouleWise labels, no night plists or retained night-plist sidecars,
   and exactly the three discoverable retained roots listed below. It runs
   `ls /Users/edr/night-custody`, prints the diagnostic real-class arm census
   and raw `pgrep`, and never retires anything. Exit 0 means observations
   completed, **not** that the census cleared. The lead must inspect ancestry,
   foreign PIDs, workloads and unknowns: no seat/Workflow or foreign session
   may remain; identify the lead's own MCP helper by ancestry. A real-class
   census return 0 grants no stub exemption. Resolve uncertainty before step 1.
2. `zsh step1-clone.zsh`: requires all three new paths absent, makes the fresh
   GitHub clone detached at H, creates Python 3.13's venv from
   `env/mac-measurement-lock.txt`, requires an exact lock match, checks H's
   ancestry and an empty `git status --porcelain=v1 --untracked-files=all`.
   Prints interpreter path, version and binary SHA-256. No ledger seeding or
   desk-input preparation. Exit 0 is `STEP1 OK`; any failure stops.
3. `zsh step2-author.zsh`: author the v2 plan once at STAGED_PLAN with
   `write_night_plan`, no v4 or pack fields, the repo-relative pilot protocol,
   and 9000 s. FROM the clone, call
   `"$PY" -B scripts/gen_evidence_night.py --plan "$STAGED_PLAN" --render-only`.
   Print wrapper digest, both sidecars and manifest; check the evidence
   literal, manifest equality, tracked source at H and ruled registration;
   syntax-check the wrapper; run import/parse preflight and render-only agent
   validation; print the schedule. No chain or measurement is executed.
   The final publication-safe path check currently exits 3 at H. **Stop here;
   do not skip this guard.** A future approved repair must satisfy it.
4. Close delegated seats and foreign sessions using their real controls.
   `zsh step3-notice.zsh` first repeats the publication-safe check, then
   creates attempt `000001` exclusively, copies exact plan bytes, and writes
   `attempts.json = []`. It saves two arm censuses 30 s apart and raw `pgrep`.
   It derives `notice-body.txt` from the saved/staged bytes and writes an
   unaccepted `notice.json` template. Exit 0 means PREPARED ONLY. Re-running
   over an existing attempt stops; do not delete or overwrite attempt evidence.
5. **Lead's manual Gmail call only:** after resolving the no-Git wording,
   use the printed subject, recipient `claude.ai.copper531@passmail.net`, and
   exact body file. None of these scripts sends mail. Preserve actual accepted
   body, plan digest/H, message id, thread id and acceptance epoch in
   `$ATTEMPT_DIR/notice-evidence.txt`. Fill `notice.json` from those observations:
   replace the three placeholders (epoch must become a JSON number), and set
   `accepted`, `prerequisites_clear`, `veto_clear` only on actual evidence.
   Preserve all observed NOs, including older threads. An unreadable thread is
   recorded as a limitation, never fabricated as read. Acceptance precedes
   publication; ARM-RETRY-POLICY adds no minimum notice waiting interval.
6. Refresh watchdog, no invocation/ownership, power/load/thermal, census and
   observable STOP/directive/NO observations; record them in notice evidence.
   `zsh step4-publish-install.zsh` checks standdown/STOP including dangling
   symlinks, obtains owner-authored open directives, checks HEAD H, a clean
   clone, fetched ancestry, exact staged/attempt bytes, wrapper sidecar and
   manifest, all evidence plan fields and publication-safe path. It currently
   refuses before publication. The directive list must be empty; any open
   directive returns to the lead. Render-only checks precede a final census.
   The lead reviews that diagnostic census and preserves its evidence before
   allowing the publication portion to proceed; if needed, execute the
   foreground block in reviewed sections, without skipping its guards.
   Immediately before `os.replace`, re-read saved/staged bytes and the actual
   notice and require `retry_allowed(now, context, [], notice)` to allow this
   initial arm. Require target absent (including symlink), at least 40 min to
   t0, and no standdown/STOP. Atomic publication is into NIGHT_ROOT only.
7. The remainder of step 4 compares published bytes to the attempt, re-hashes
   the wrapper, repeats the evidence checks and runs the owner-present
   `--launchd-probe`. It requires the evidence receipt schema,
   `verify_only=true`, `collect_started=false`, `load_started=false`, correct
   `probe_label`, proven cleanup, full recomputed bindings and freshness under
   six hours via `validate_evidence_probe_receipt`. No calibration custody-time
   arithmetic applies. After a consent dialog, follow the handback's successful
   no-further-interaction probe-repeat procedure before installation. Only
   then does the normal install run. Installer failure stops; keep its exact
   exit code and evidence. No success is inferred from a lost response.
8. `zsh step5-verify-and-exit.zsh`: prints both loaded agents and both plists;
   checks their labels and schedule against `schedule(plan)`, full argv against
   rendered argv, clone-venv Python as argv[0], clone WorkingDirectory,
   `RunAtLoad=false`, exact published/attempt bytes and wrapper sidecar. Saves
   the post-install `night/` baseline in stdout and prints the exit deadline.
   Exit 0 proves these installation checks only. The lead records the frozen
   triple, notice, digests, schedule and harvest pointer in lead-owned records,
   then actually terminates itself and every owned seat, MCP child and helper
   strictly before REQUEST. Never signal foreign sessions. Keep agent apps
   closed through completion, longer if ownership is still active.

The retained discoverable plan roots observed by `ls` on 2026-09-19 were:

- `d079-epoch-25g83-derivation-n1-20260916`
- `d079-epoch-25g83-derivation-n1-20260919`
- `d079-epoch-25g83-derivation-n2-20260919`

The listing also contained `active-campaigns`, `magistrate`, `magistrate-bench`
and `retired-v1`. These are not asserted to be disposable or inactive. The lead
must check retained roots' completed harvest and ownership before arming; a
listing alone establishes neither. An unexpected discovery set exits 3.

`set -euo pipefail`, guarded directory changes and exclusive creation remain.
No failed command is permission to continue. Custom refusals use exit 3;
Python assertions use exit 1; parser/generator/receipt/installer refusals retain
their own codes (usually 2; uninstall's retained/unknown job outcome is 4).
After **any** post-publication failure, use the handback's existing
uninstall-first recovery, preserve/compare/unpublish only after uninstall 0.
These scripts contain no automatic recovery or retry loop. Initial attempt 1
is not a D-182 successor, and retained nights never enter its retry history.

There is **no `--verify` on `gen_evidence_night.py`**. Re-rendering an existing
wrapper refuses `chain already exists; author a fresh plan`. Verification here
reads hashes, sidecar, manifest and tracked bytes without re-rendering. Do not
patch the sealed wrapper, preserve a staging alias, or regenerate after notice
as an improvised repair.

## Deltas from the n1 derivation set

| Change | Reason |
|---|---|
| Fresh QPE-01 id/root; two timing values; H fixed to PR #364 merge | New evidence candidate, no reused night or calibration identity |
| Precheck instead of retirement; retained discovery list | Brief explicitly preserves retained roots |
| Same lock-based clone; no ledger copy/authentication | Evidence chain opens no calibration session |
| No SESSION_ID, EVIDENCE_ROOT_ID, calibration plan, epoch/T1 desk inputs | No evidence-chain readers for those calibration inputs |
| Pilot protocol replaces D-166 registration; v2 class/window retained | Frozen QPE-01 protocol is the ruled chain-bound registration |
| Evidence render-only generator and manifest checks replace derivation generator | Wrapper's payload literal selects the evidence route; no evidence `--verify` exists |
| Evidence notice and exact-byte notice snapshots | Describe twelve idle envelopes and no-objection boundaries |
| Initial `retry_allowed(..., [], notice)` replaces step4a predecessor inspection | Pilot night one is a fresh arm; no D-182 successor is claimed |
| Evidence receipt validator replaces custody-budget inequality | Verify-only files/imports; no calibration-ledger fields |
| Schedule and exit deadline computed, no historical date literal | Supports the lead's next quiet slot |
| Explicit `diff` failure exit before “lock matches” | Template's `diff ... && echo` alone would not stop under `set -e` |
| Publication-safe guard and unsendable draft warning | Expose the two pinned-code/recipe conflicts instead of arming a known failure |

Harvest after courier completion and clear ownership: `night/evidence_outcome.json`,
`night/evidence_envelopes.jsonl`, `night/evidence_cleanup.json`, any refusal,
`night.log`, `night/evidence_busy_cores.jsonl` and courier evidence. Use the campaign's
pilot summary for block-two sizing or “no cutoff qualifies”; retain the root
if any envelope was captured. The lead owns the subsequent plan and ruling.

## NEEDS_RULING — blocking conflicts

1. **Question:** How should staged authoring bind the future published plan?
   **Evidence:** `gen_evidence_night.generate` writes the supplied STAGED_PLAN
   into `EVIDENCE_PLAN_PATH`. `evidence_probe_bindings` requires that literal
   equal the published input path; `verify_environment` opens that literal.
   Required `os.replace` removes the staged file. The fixture reproduces both
   the absent path and `evidence plan path mismatch` before any probe starts.
   **Options considered:** repair generation plus staged validation in their
   owning code and re-pin H; or authorize a changed publication procedure.
   Rewriting a sealed wrapper after notice or leaving an unreviewed staging
   alias cannot satisfy the specified byte and binding checks.
   **Recommendation:** a separate scoped generator/installer integration fix
   with staged-render → publish → evidence-binding coverage, then a new H
   ruling and rerun of this set. **Blocked work:** a usable step-2 success,
   sendable notice, publication and installation at the specified H.
2. **Question:** Does “no Git runs” prohibit read-only pinned-file verification?
   **Evidence:** both `run` and `record` enter `verify_environment` →
   `verify_manifest` → `manifest_for` → `tracked_bytes`, which invokes
   `/usr/bin/git ... show H:path`. Record 85 and the brief promise no Git.
   **Options considered:** allow and describe these read-only verification
   commands; or repair runtime verification in the owning code to honor an
   absolute no-Git rule. **Recommendation:** lead rules explicitly; until then
   keep the notice marked DRAFT and unsendable. **Blocked work:** truthful
   final no-Git notice wording and confirmation that the payload meets recipe.

No out-of-scope repair was attempted. No scope expansion is presumed: the lead
can assign the repair separately or resume this seat with an explicit allowlist.

## NEEDS_RULING — non-blocking assumptions for lead review

- **Question:** Is the observed three-root discovery set the intended retained
  set at execution? **Options:** accept this snapshot or supply an updated
  exact set after harvest review. **Recommendation:** confirm it from the
  retained harvest/ownership records immediately before step 0; never delete
  a root to make the check pass. **Blocked work:** none in script preparation;
  an execution mismatch stops for the lead.
- **Question:** Keep the template's notice recipient for QPE-01?
  **Options:** use `claude.ai.copper531@passmail.net` or provide a different
  authorized destination. **Recommendation:** retain the bench-tested recipient
  unless the lead directs otherwise. **Blocked work:** none in preparation;
  the lead owns the actual Gmail call.
- **Question:** Is the lead's own MCP helper the only extra census hit allowed
  during bench work, as this brief states? **Options:** lead identifies its
  exact ancestry or closes it. **Recommendation:** keep the real-class census
  diagnostic, require manual ancestry review, and close every owned helper
  before REQUEST; apply no stub-only exemption. **Blocked work:** none in
  preparation; unresolved ancestry blocks the bench sequence.

No other scientific/timing assumptions were added; frozen protocol values and
notice timing come from the supplied authorities.

## Dry-check

Replay from this detached worktree:

```zsh
TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B docs/process_traces/2026-09-19-activation-d0b83820/87-arm-scripts-qpe01-pilot/dry-check.py
```

This runs `zsh -n` on every shell script, parses all Python heredocs and helpers,
then exercises the actual authoring, notice and publication heredocs and the
assertion-only helper against a fresh `/tmp/qpe01-arm-fixture-*` tree. Tracked
source/manifest reads use this worktree at H; no clone is made. The fixture
publication intentionally bypasses the shell's refusal guard only to reproduce
the integration defect in /tmp. Synthetic receipt bindings and installed-plist
reads are explicitly mocked. Step 5's actual assertions are exercised with
matching and corrupted fixture plists. No live custody/staging write, launchctl,
probe, chain, collector, load, power, email or network operation is exercised.
The template contains no `--dry` mode. Broad/full repository suites and live
checks were not run: this is scoped operator-tooling preparation with explicit
no-clone/no-probe/no-install constraints; the focused fixture checks cover the
changed assertions. Full-suite and live verification remain lead-owned.

Observed output (exit 0 means fixture assertions passed, **not arm-ready**):

```text
PASS zsh -n arm-env.zsh
PASS zsh -n step0-precheck.zsh
PASS zsh -n step1-clone.zsh
PASS zsh -n step2-author.zsh
PASS zsh -n step3-notice.zsh
PASS zsh -n step4-publish-install.zsh
PASS zsh -n step5-verify-and-exit.zsh
PASS Python syntax: 8 shell heredocs and 2 helper scripts
PASS filled environment: local date, minute alignment, all seven boundaries
PASS unfilled environment refuses with exit 3
PASS actual authoring heredoc, generator, manifest, source-at-H and registration checks
PASS generated wrapper zsh -n (wrapper never executed)
PASS second render refuses existing chain
CONFIRMED BLOCKER: staged wrapper fails publication-safe guard, exit 3
PASS wrapper byte drift refuses
PASS actual notice heredocs: evidence body, byte binding, unaccepted template
PASS publication heredoc refuses unaccepted notice, owner NO and changed saved bytes
CONFIRMED BLOCKER: fixture publication preserves bytes but probe binding refuses evidence plan path mismatch
PASS synthetic receipt validator: schema, verify-only, no collect/load, cleanup, <6 h freshness
PASS actual step5 assertions on synthetic plists; wrong schedule/argv/root/RunAtLoad refuse
DRY CHECK COMPLETE: fixture checks passed; staging/publication incompatibility remains BLOCKING
```
