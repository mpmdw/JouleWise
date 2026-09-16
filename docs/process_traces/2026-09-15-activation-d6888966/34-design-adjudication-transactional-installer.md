# 34 — Design adjudication: the transactional night-agent installer (INSTALL-WINDOWS-MULTI-01 redesign)

Magistrate `d6888966` (Fable 5.1), 11:56 PDT (clock-read). Inputs: three blind seats on brief 33 — Astra xhigh
(33a), Opus (33b), fresh Fable (33c). All three recommend (B). Where they differ I rule below and name the loser.
Nothing here amends a rule; the cold-gate rulings 25/28 and their syntheses stand and are cited where preserved.

## Adopted design (dictated; a seat implements without re-deciding)

D1. **Module and shell.** Engine in `joulewise/night_agent_install.py` (stdlib-only; no import of `scripts/run_night.py`
at module import time — the schedule/spans helpers are imported inside the install path only, so `--uninstall`
runs without the driver, its venv or valid pins: Astra Q4). `scripts/install_night_agent.sh` keeps ONLY argv
parsing, the MIN_PYTHON subprocess check (33c: must run before any project import — the 2026-09-11 defect), and
`exec "$python" -B -m joulewise.night_agent_install "$@"`; no trap, no mutation, no cleanup in shell. Same argv,
exit codes and strings as today wherever documented (D9). Rejected: keep zsh and fix the predicate (A) — all three
seats: zsh cannot carry a `finally`, a token type or state-dispatch (cold gate 25 measured errexit-in-function skips
EXIT); the class stays enumerable.

D2. **Liveness predicate (the only liveness API).** `LaunchctlAdapter.print(label) → Liveness`: `LOADED` iff rc 0;
`ABSENT` iff rc == 113 AND stderr contains the exact line `Could not find service "<label>" in domain for user
gui: <uid>` (executed by all three seats on this machine: rc 113, stdout empty, stderr `Bad request.` + that line);
everything else — any other rc, 113 with another message, timeout, OSError, decode failure — is `UNKNOWN`. Consumers:
verification requires `LOADED`; admission and every deletion require `ABSENT` (unknown ⇒ loaded). stderr is captured,
never discarded. The signature is pinned by one test and re-probed on OS change (33b: an empirical fact, same class
as the 25G83 epoch). Rejected: bare `rc != 0 ⇒ absent` (the lt-21 defect) and bare `113 ⇒ absent` (113 is
request-class; the label text proves the query addressed the right service).

D3. **Proof-carrying deletion (33b).** `require_absent(label) → Absent` raises on LOADED and UNKNOWN;
`remove_plist(label, proof: Absent)` and `restore_prior(label, proof: Absent)` take the token. No other function in
the module may unlink or overwrite a plist. I2 becomes a type fact.

D4. **Single mutation channel.** Exactly three mutators on the adapter — `write_plist`, `bootstrap`, `bootout` — and
nothing else touches `launch_dir` or launchctl (33b). Every adapter call returns `Outcome(kind, rc, stdout, stderr)`;
raw exit codes never reach a caller.

D5. **States** (33c's list, 33a's atomic publication): `PARSED → VALIDATED → ADMITTED → STAGED → PUBLISHED →
NIGHT_LOADED → DEADMAN_LOADED → VERIFIED → COMMITTED`; terminal `SUCCESS`, `REFUSED`, `ROLLED_BACK`, `RETAINED`.
- VALIDATED: every read-only refusal at today's `:85-154,:283-307` with today's reason strings and exit codes; no
  `mkdir`, no file write (today's `:309` ordering).
- ADMITTED: `require_absent` on BOTH labels (rule 28 Q2; refusal `night_agent_already_loaded` naming the label, exit 3;
  an UNKNOWN refuses with `state=unknown` and the raw diagnostics — 33a); the selected span frozen from a fresh
  admission-time date. Consequence (33a + 33c, adopted): **no bootout on the success path** — the pre-bootout of the
  dead-man (today's `:370`) is deleted; a prior LOADED job is a refusal, never something to unload and "restore".
- STAGED: signal handlers installed FIRST (INT/TERM/HUP raise `Signalled(130/143/129)`; 33b: this closes F4 by
  construction); then prior bytes + mode + mtime of each existing plist snapshotted to `<label>.plist.prior` beside it
  (the fence reads only `<label>.plist`, `magistrate_watchdog.py:727-728`); no TMPDIR directory exists anywhere in the
  design (33c: the F4 / 28-Q1b class disappears). Rejected: 33b's TMPDIR journal — same information, one more
  directory whose absence is ambiguous; the `.prior` sidecar is resumable (33b's SIGKILL-mid-restore concern) without
  it.
- PUBLISHED: both plists rendered to a temp name in `launch_dir` and atomically replaced in place (same directory,
  `os.replace`); bootstrap is impossible before both files exist (33a). Unsupported destination types (symlinks,
  directories) refuse before any write.
- NIGHT_LOADED, DEADMAN_LOADED: the only two launchd mutations, each recorded BEFORE invocation.
- VERIFIED: both `print` reads == LOADED (UNKNOWN fails verification, D2).
- COMMITTED: the single commit predicate, evaluated exactly once, on a clock read taken after the last launchd
  mutation: `now < min(selected_span_close, install_close_epoch)` (`>=` refuses `install_span_closed`, today's
  `:190-193` semantics, cold gate 25 Q1(c)). Passing sets `state = COMMITTED` BEFORE any stdout write; then
  `validated pins: …`. I1: exit 0 is reachable only through this predicate and nothing after it mutates launchd.
  Rejected (33a): a gate at every mutator — the earlier checks may stay as early refusals but they never authorise
  success; one evaluation is the ruling (25 Q1c) and one is what a reader can verify.

D6. **Single teardown** = one `finally`, dispatching on `state`, never on an exception or exit code (synthesis 28/13's
positive rule made structural; a `BrokenPipeError` from the success print lands in the success branch). Signals
masked (`pthread_sigmask` SIG_BLOCK) for the whole unwind (rule 28 Q4-F3). Branches:
- COMMITTED: no launchctl call, no plist change; `.prior` sidecars removed inside `except BaseException: warn`; exit 0.
- ≤ VALIDATED / ADMITTED: nothing to undo; the refusal's exit code.
- STAGED / PUBLISHED (no bootstrap attempted): `restore_prior`/`remove_plist` under `require_absent` (which holds
  by admission); the original exit code.
- NIGHT_LOADED … VERIFIED (a bootstrap was attempted): `bootout` both labels (outcomes recorded, never trusted); then
  `require_absent` both; if BOTH ABSENT → restore priors byte-identical with mtime or unlink new files, remove
  sidecars, exit with the original code (today's matrix 143/130/129/1/2/3); if EITHER LOADED or UNKNOWN → restore
  nothing, remove nothing (sidecars retained), print today's `teardown: <night> loaded=…; <deadman> loaded=…; retained
  plists: …` line plus one `liveness_unknown: <label> rc=<n> stderr=<first line>` line per UNKNOWN, **exit 4**.
  Teardown never bootstraps; runs once; a repeated signal does not restart it. What each failure leaves: never
  files-gone-jobs-loaded — a file is removed only after an ABSENT proof for its label (I2, I3).

D7. **`--uninstall`**: same adapter and the same `verified_bootout(labels)` routine; exit 0 only when both labels read
ABSENT after bootout, then `remove_plist` with the proofs; exit 4 with today's `uninstall: still loaded after bootout:
…; retained plists: …` line otherwise; idempotent and re-runnable; must run under the system interpreter with no
project imports beyond the module (33a). **`--render-only`**: constructs the machine with a `NullAdapter` that raises
on any call (I4 is a type); no occupancy check (rule 28 Q6.3); render and uninstall are mutually exclusive, refused
before any launchctl call (33a). Rejected (33a): a lock file for the label pair — the handback runs install/uninstall
sequentially by one operator; a lock adds a file whose staleness is ambiguous. Recorded as a rejected alternative.

D8. **Constants and scope (I5).** `INSTALL_SPANS = (("00:00","24:00"),)`, `INSTALL_CLOSE_MARGIN_S`, `PLAN_LEAD_S`
unchanged and read from `scripts/run_night.py`, never restated. No duration ceiling. The module is parameterised by
label set from the first commit (33b) so A204 (the watchdog installer's uninstall) is a one-label caller landed as a
SEPARATE PR after this one, with its own fake-launchctl matrix (33b/33c; 33a's "now" is adopted as "designed now,
landed next").

D9. **Migration in the same lane.** Runbook §1.3 `:1405-1415` (the "rolled back …" prose no longer exists in code —
33b grep; replace with the D6 outcome table: committed / restored / retained, and the unknown-query behaviour);
runbook §1.4 recovery commands conditional on a successful uninstall (33a: today's sequence can unpublish after a
failed uninstall); NIGHT_HANDBACK: exit 4 retains plists, re-running uninstall is safe, exit 4 stops retirement and
successor arming; courier prompt `:20`: retained/unknown state stops uninstall-dependent cleanup. Refusal strings
preserved verbatim: `install_span_closed`, `install_outside_span`, `plan_t0_in_the_past`,
`night_agent_already_loaded`, `plan_outside_custody_root`, `night_plan_malformed`, `plan_schedule_unrepresentable`,
`install_spans_unresolvable_on_day`, `plan_t0_not_minute_aligned`, `plan_t0_ambiguous_local_time`, `failed to
bootstrap <label>`, `launch agent verification failed`, both retained-state lines, `validated pins: …`; exit codes
2/3/4 and the signal codes; the schedule JSON keys. New, documented: `liveness_unknown: …` and
`night_agent_already_loaded … state=unknown`. Callers unchanged (runbook, handback, courier, `tests/test_run_night.py`,
relaunch prompt).

D10. **Tests.** Fake launchctl rewritten three-valued and stateful: marker → rc 0 + a `gui/<uid>/<label> = {` block +
empty stderr; no marker → rc 113 + the two verbatim stderr lines with label/uid substituted; fault directives per
label → `{9, 64, 112, 113-with-wrong-label, 0-with-junk-stderr, hang past the adapter timeout}` WITHOUT changing loaded
state; mutators model return code and effect independently (a failed bootstrap may load; a "successful" bootout may
leave loaded). The regression matrix is a PRODUCT (33b): {every state} × {op FAILED, op UNKNOWN, INT, TERM, HUP,
clock at exactly close, clock past selected close, clock past install_close, render PermissionError, restore I/O
error}, each cell asserting the 4-tuple (rc; per-label liveness from the stub state; per-plist bytes+mtime vs prior;
`installed_agent_fence()` over the resulting directory); structurally unreachable cells declared unreachable; ONE
shared assertion in every cell: the fence never returns `None` while the stub state says a label is loaded. FIX-1..10
and FIX-A assertions ported with a mapping table (old test → cell); the clock-advance-during-cleanup case renamed
`control_…`. Mutation must-die set (union of 33a/33b/33c): UNKNOWN→ABSENT anywhere; ABSENT widened to `rc != 0`;
113 accepted without the stderr match; drop the label check; remove the signal mask; remove `require_absent` at any
deletion; move or delete the commit predicate; `<`→`<=` / `>=`→`>` at the gate; set COMMITTED after the print;
success branch calling bootout; unlink before the ABSENT proof; occupancy on one label; NullAdapter replaced under
render-only; `copy2`→`copy` (mtime); the RETAINED exit 4; the COMMITTED branch's `except BaseException`; collapse
either `min` operand; verify accepting UNKNOWN. Replay = the full sharded suite at the landing head PLUS lt-21's
`reproduce.py` re-run expecting `class_1: NO` and `class_2: NO`, with the class-1 predicate read as ruling 28 Q1
defines it (clock read after the last LAUNCHD mutation; a sidecar removal is not launchd state) — a recording of
that ruling, not a new rule.

## Why B (for the record)

Four rounds did not fail on four bugs; they failed on one topology: invariants enforced by inspecting call sites, and
the class reappearing one site further each time. B replaces enumeration with three constructions — a single
mutation channel, a commit predicate that is the only road to exit 0, and deletion that requires an absence proof —
so the unsafe states become unrepresentable rather than reviewed away.

## Still enumerable, honestly (33b)

The managed label set (two constants); the ABSENT signature (an OS fact, pinned by a test); a SIGKILL between
`bootstrap` and its record (ordering makes the half-state files-present, fence-visible); whether `bootout` is
synchronous (a dying job reads LOADED or UNKNOWN, both of which refuse — resolved conservatively, not eliminated).

## Implementation plan

Branch `feat/2026-09-15-install-windows-transactional` from the integration head `073a9763` (keeps rounds 1–3's tests,
docs and the faithful `test_run_night` stub); worktree `/Users/edr/code/JouleWise-wt-iw-txn`. Seat T1 (Astra xhigh,
workspace-write): `joulewise/night_agent_install.py`, `scripts/install_night_agent.sh`, `tests/test_night_agent_install.py`
(new, the matrix), `tests/test_install_night_agent.py` (ported assertions + mapping table + new fake launchctl). Seat
T2 (Astra high, parallel): D9 docs. Then the gauntlet under the lieutenant: contract + execution refuters, fix rounds
with delta re-audits (the stop condition of synthesis 28/13 §Q3 applies unchanged, with the class-1 predicate as
D10 reads it), Opus counter-review, replay, ledger; magistrate rows 7/12; PR; merge; then A204 as its own PR.

## Addendum 2026-09-15 20:45 PDT (magistrate b0ae8462, from lt-31 F2)

D5's rationale above says the `.prior` sidecar "is resumable (33b's SIGKILL-mid-restore concern)". As implemented and
as ruled in D7, it is not: `restore_prior` reads only the in-process `priors` map, `validate()` refuses while a sidecar
exists, and `--uninstall` discards sidecars. After a SIGKILL the sidecar is operator-readable evidence (copy it by hand),
never automatically restored. The shipped behaviour is right; only the word "resumable" in the D5 rationale overclaimed.
The runbook §1.3/§1.4 and NIGHT_HANDBACK wording was corrected in fix round 5 (F2). D5's rejection of the TMPDIR journal
stands on its other ground (one more directory whose absence is ambiguous).
