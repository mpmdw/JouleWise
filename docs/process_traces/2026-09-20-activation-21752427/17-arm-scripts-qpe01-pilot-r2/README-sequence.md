# QPE-01 pilot night one, attempt 2: bench sequence, prepared 2026-09-20

Prepared at **H4 `980f8d6452fb6923644bdac1e243ce0a344c881f`**, the merge of
PR #371 (census self-match cure). The mock-free installer/driver dry-check
passes at this same H; nothing has been armed. Fill the two environment
placeholders and satisfy the bench gates before execution. The aborted
`qpe01-pilot-n1-20260920` retained zero envelopes, so this remains pilot night
ONE with a new date-based plan identity. “Attempt 2” identifies the second
pilot-night effort; the fresh plan still uses arm attempt `000001` and `[]`
retry history, not a same-plan retry.

Authority: record 85 (`85-pilot-night-one-arm-recipe.md` in the magistrate's
activation worktree), `docs/process/NIGHT_HANDBACK.md` (evidence amendment and
ARM-RETRY-POLICY), and `docs/phase_2/derivation_night_runbook.md` §0–§1.5.
Template: `2026-09-19-activation-a743be05/02-arm-scripts-qpe01-pilot-n1-20260919/`,
including seat 11's mock-free dry-check. Historical step outputs and the
abandoned candidate are excluded. This successor applies the lead's H4,
census, retained-root and watchdog-precondition deltas.

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
`980f8d6452fb6923644bdac1e243ce0a344c881f` (H4); changing it requires a new lead brief.
Step 0 makes one read-only ancestry check in the canonical checkout because
watchdog ticks import code there. Other runtime Git operations below are in
the fresh clone. The lead rechecks H is an ancestor of fetched `origin/main`.
The committed placeholders are exactly `__YYYYMMDD__` and `__T0_EPOCH_S__`;
using the unfilled environment exits 3.

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

The lead reviews each step separately and keeps
stdout, stderr and exit status. Keep the directory together, outside the fresh
measurement clone. Step 0 must be run from this authoring worktree so it can
find the read-only census implementation. It executes the supplied project
interpreter but writes nothing in the canonical checkout. Use a guarded `cd`
to this scripts directory and `source ./arm-env.zsh` in the bench shell;
exports in a child script do not persist in its parent.

1. `zsh step0-precheck.zsh`: requires exactly `com.joulewise.magistrate` among
   loaded JouleWise labels, no night plists or retained night-plist sidecars,
   and exactly the four discoverable retained roots listed below. It runs
   `ls /Users/edr/night-custody`, prints the diagnostic real-class arm census
   and raw `/usr/bin/pgrep -lf '[c]odex|[c]laude|[t]3'`, and never retires anything.
   Before either census it enforces NIGHT_HANDBACK §Census (a)/(b): canonical
   checkout HEAD must contain H, and no resident supervisor may remain alive.
   It reads `resident_session.supervisor_pid` (not the child `pid`) from
   `/Users/edr/night-custody/magistrate/state.json`. A null resident, a PID that `ps` cannot find,
   or a reused PID whose command does not name `magistrate_watchdog.py`
   passes; a live supervisor prints its start time and refuses with exit 3.
   Unreadable/malformed state or process-inspection errors also refuse.
   These checks are read-only hard refusals. Exit 0 means observations
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
   The final publication-safe path check must pass at H4. **Stop on refusal;
   do not skip this guard.** The sealed wrapper must name the published plan.
4. Close delegated seats and foreign sessions using their real controls.
   `zsh step3-notice.zsh` first repeats the publication-safe check, then
   creates attempt `000001` exclusively, copies exact plan bytes, and writes
   `attempts.json = []`. It saves two arm censuses 30 s apart and raw `pgrep`.
   It derives `notice-body.txt` from the saved/staged bytes and writes an
   unaccepted `notice.json` template. Exit 0 means PREPARED ONLY. Re-running
   over an existing attempt stops; do not delete or overwrite attempt evidence.
5. **Lead's manual Gmail call only:** use the printed subject, recipient
   `claude2.glaring610@passmail.net`, and
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
   manifest, all evidence plan fields and publication-safe path. Any failure
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

The retained discoverable plan roots confirmed by read-only `ls` on 2026-09-20 were:

- `d079-epoch-25g83-derivation-n1-20260916`
- `d079-epoch-25g83-derivation-n1-20260919`
- `d079-epoch-25g83-derivation-n2-20260919`
- `qpe01-pilot-n1-20260920` (aborted pilot; retained per [harvest record](../01-qpe01-pilot-n1-20260920-harvest-record.md))

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
| Fresh QPE-01 id/root; two timing values; H fixed to PR #371 merge (H4) | New evidence candidate, no reused night or calibration identity |
| Precheck instead of retirement; four retained discoverable roots | Preserve the aborted pilot alongside the three derivation roots |
| Single-quoted bracketed census in steps 0 and 3 | Match H4 `night_gate.AGENT_CENSUS_ARGV`; prevent census self-match and zsh globbing |
| Canonical-checkout ancestry and resident-supervisor preconditions | Watchdog ticks must import the cure; a resident supervisor must end before arm |
| Same lock-based clone; no ledger copy/authentication | Evidence chain opens no calibration session |
| No SESSION_ID, EVIDENCE_ROOT_ID, calibration plan, epoch/T1 desk inputs | No evidence-chain readers for those calibration inputs |
| Pilot protocol replaces D-166 registration; v2 class/window retained | Frozen QPE-01 protocol is the ruled chain-bound registration |
| Evidence render-only generator and manifest checks replace derivation generator | Wrapper's payload literal selects the evidence route; no evidence `--verify` exists |
| Evidence notice and exact-byte notice snapshots | Describe twelve idle envelopes and no-objection boundaries |
| Initial `retry_allowed(..., [], notice)` replaces step4a predecessor inspection | Pilot night one is a fresh arm; no D-182 successor is claimed |
| Evidence receipt validator replaces custody-budget inequality | Verify-only files/imports; no calibration-ledger fields |
| Schedule and exit deadline computed, no historical date literal | Supports the lead's next quiet slot |
| Explicit `diff` failure exit before “lock matches” | Template's `diff ... && echo` alone would not stop under `set -e` |
| Publication-safe guard retained | Assert repaired staged-to-published binding before notice/publication |

Harvest after courier completion and clear ownership: `night/evidence_outcome.json`,
`night/evidence_envelopes.jsonl`, `night/evidence_cleanup.json`, any refusal,
`night.log`, `night/evidence_busy_cores.jsonl` and courier evidence. Use the campaign's
pilot summary for block-two sizing or “no cutoff qualifies”; retain the root
if any envelope was captured. The lead owns the subsequent plan and ruling.

## Resolved template blockers and bench checks

The earlier template recorded a staging-path binding conflict and an absolute
“no Git runs” conflict. Its later scripts already require the publication-safe
binding repair (PR #365) and carry ruling 87a F2's read-only Git wording in
the notice. H4 includes those repairs; the dry-check below verifies the
publication-safe guard and real installer/driver composition. The notice
still requires the lead's actual mail acceptance and recorded prerequisites.

The retained roots require harvest/ownership review immediately before step 0;
never delete a root to satisfy the check. The notice recipient remains
`claude2.glaring610@passmail.net`. The lead identifies its own MCP helper by
ancestry and closes every owned helper before REQUEST; no stub exemption is
introduced. Results remain PROVISIONAL until the live gates pass.

The courier/driver path issue (`WATCHDOG-COURIER-PATH-HOLD-01`) may produce a HOLD_CENSUS watchdog notice during the span; it is not fatal.

## Dry-check

Ed's rule (issue #368): "Every arm dry-check executes the real installer
render-only path and the real night driver on a fixture, and consumes the
plists they actually produce. A dry-check that passes while the arm fails is
worse than none."

Replay from this worktree:

```zsh
TZ=America/Los_Angeles PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B docs/process_traces/2026-09-20-activation-21752427/17-arm-scripts-qpe01-pilot-r2/dry-check.py
```

All fixture writes stay under this scripts directory in `qpe01-arm-fixture-*`
and are removed on exit, keeping this delegated run within its write scope.
The check makes a local, shallow Git clone of this worktree's committed
HEAD (no network), with a fixture `.venv/bin/python` symlink to the supplied
interpreter. H, this worktree's HEAD and the fixture's HEAD must all equal
H4 `980f8d6452fb6923644bdac1e243ce0a344c881f`; the plan's repo/measurement
heads match that checkout. The literal H in `arm-env.zsh` must also be an
ancestor of this worktree's existing `origin/main`; the check asserts that
without fetching or changing the live arm pin. Date/epoch substitutions happen
only in a temporary environment copy,
whether the source environment is filled or still contains placeholders.

The dry-check executes:

- `zsh -n` for all bench scripts and Python syntax checks for their heredocs
  and helpers; the actual authoring, notice and atomic-publication heredocs;
  manifest, tracked-source, registration and publication-safe assertions;
  existing refusal cases for altered wrappers, repeat generation and notices.
- The fixture's real `scripts/install_night_agent.sh --plan STAGED --python PY
  --render-only RENDER_DIR` before publication, then the same command with
  the published plan after `os.replace`, using a fresh directory for each render.
  Both must exit 0 and print evidence
  `payload_kind` JSON. Each must produce the night, dead-man and probe plists;
  night/dead-man bytes must match between renders. The plan, wrapper, manifest
  and both hash sidecars must retain their sealed bytes.
- Real `run_night.py preflight --plan` and `schedule --plan`, then
  `run_night.probe_night` through a real supervisor process and the actual
  verify-only chain. It checks supervisor/chain process identities,
  verify-only/no-collect/no-load flags and `validate_probe_receipt`, then
  mutates the real receipt to retain schema, flag, cleanup and freshness
  refusal coverage.
- Step 5's unchanged Python assertions against the actual rendered plists
  copied to a fake LaunchAgents directory. Wrong schedule, argv, working root
  and RunAtLoad cases mutate these real plists; none is manufactured.

The supervisor uses the same sole census stub as
`tests/test_evidence_arm_sequence.py`: `_probe_group_absent` returns true.
The real supervisor still performs process-group termination/reaping and
computes `cleanup_proven`; this is not live host-census proof. A fixture
`claude` executable that exits 99 satisfies installer discovery, matching
`EvidenceFixture`; render-only must not execute the courier. Step 5 substitutes
only `Path.home()` and the response to `launchctl list`; all other subprocess
calls remain real. No actual launchctl, installation in the user's LaunchAgents,
powermetrics, collection, load, email, network or live custody operation occurs.
The bench shell scripts themselves are not run wholesale.

Observed on 2026-09-20 at H4: exit 0; all seven scripts passed `zsh -n`,
nine shell Python heredocs and both helpers parsed, the unfilled environment
refused with exit 3, and no `CONFIRMED BLOCKER` line appeared. Output tail:

```text
PASS real installer render-only on PUBLISHED plan: three plists; night/dead-man byte-identical
PASS fixture publication preserves bytes; real probe bindings accept the published plan and refuse the staged path
PASS real run_night.py preflight and schedule on published fixture
PASS real probe_night supervisor, verify-only chain, process identity and validate_probe_receipt
PASS real receipt validator: schema, verify-only, no collect/load, cleanup, <6 h freshness
PASS actual step5 assertions on installer-produced plists; wrong schedule/argv/root/RunAtLoad refuse
DRY CHECK COMPLETE
```

This validates fixture composition at the exact arm H. It does not establish
live census clearance, canonical-checkout ancestry, resident-supervisor absence,
or machine readiness. Step 0 and the subsequent bench gates remain mandatory.
Separate step-0 checks exercised the extracted guard against fixture state
and this worktree's ancestry: null resident passed; an unavailable H refused.
The sandbox blocked real `ps` with “operation not permitted”, which refused
with exit 3. Supplied process-output fixtures verified missing/reused PID
acceptance, live-supervisor refusal (including start time), inspection-error
refusal, and invalid/missing supervisor-field refusal. These checks do not
prove the live resident state; no state shape was guessed: the handback and
`scripts/magistrate_watchdog.py` name `supervisor_pid` separately from `pid`.
The predecessor's negative control at `0959e613` is historical evidence in the
source template; it was not rerun for this successor.

Verification is scoped to this operator tooling: the full dry-check exercises the
real dispatch and composed arm sequence. Separate repository regression tests
were not rerun in this delegated tooling-only task. No production
code changes; the full repository suite and live/hardware gates remain with
the lead.
