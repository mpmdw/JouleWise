# Host side effects, shadow reader — 2026-11-11

Branch: `feat/2026-11-11-sm-host-effects`. Base: `origin/main` at
`711467824395b689216ab24481d8f6e0a1d36ab4`. The supplied branch already had that
name and base, with a clean tree. No checkout, network, push, host probe or
measurement run was needed.

Authority: the audit's sections 0, 4.5, 7 items 6–7, 8.2 item 3 and 8.3, and
the state-machine lane PLAN. RL-53 W-4 keeps the writers unchanged. The current
pointer and inactive stop card were checked. This is the assigned AGENT lane,
not permission to follow the pointer into another lane. Coordination files
remain lead-owned and untouched under the seat's explicit instructions.

## Built

- `joulewise/host_effects.py`: frozen facts and observations, seven effects,
  a pure `owed_effects`, three named invariant checks, one filesystem reader,
  and a CLI. Nothing in the existing writers imports it.
- `tests/test_host_effects.py`: 30 synthetic-only unittest tests. No fixture
  data files were added.
- `CANONICAL.md`: one tool-map row.
- `scripts/test_timings.json`: exactly one alphabetically inserted line.
  Its 0.694 seconds is a local scheduling hint, not a hosted median.
- This report.

`owed` is True for debt, False for a clear or explained observation, and None
for an unknown. Reasons are stable codes. Each night label is a separate
obligation. Thus the November 10 section-0 reconstruction yields three debts:
network time and two uninstalls. It uses the audit's description, not a results
branch. The November 8 reconstruction retains both non-W1 marker obligations
and the nonzero power-mode obligation after the process group dies.

Spans are half-open `[start, end)`. None means the host plan census is unknown;
an empty tuple explicitly means no active span. Explicit plan directories can
provide recorded ownership, but do not establish an exhaustive plan census.
A held lock explains a deferred power cleanup. A matching owner span can also
explain a marker. An unrelated span cannot excuse an owned orphan marker.
Any nonzero AC mode violates the audit's Automatic-mode invariant without a
held lock; this includes mode 1, even though the effect name says HIGH_POWER.

Keep-awake has a standing authorization in audit 4.5. Its loaded state is
explained while that authorization stands. A caller can supply False for
`keep_awake_expected` to expose an uninstall obligation, or None for unknown
policy. A fence explains stopped Spotlight only before its deadline with
caller-observed PID liveness. The reader never sends even a PID-zero signal.

Receipts provide recorded provenance only. They never prove the current network
setting. A lock file never proves a held lock. A Spotlight receipt never proves
a currently stopped process. Missing, corrupt and unrecognized observations
remain unknown. Unknown outcome words remain visible even on an otherwise clean
host. `StateReport` and `WindowOutcome` inputs are optional; the sibling import
is guarded, and a missing dependency inside that module is not swallowed.

## Effect table and writer evidence

Here M means `origin/main` at `711467824`; W means
`origin/align/2026-11-08-v4-r11` at `b4a6c217f0285a20aff33a8407160dd77af2a8a6`.
All anchors below were read as code or text with `git show`, without checkout.
M has no `joulewise/align/apple/powermode.py`. An absent writer is stated as
absent, rather than assigning W's line numbers to M.

| Effect | Files or facts read | Setter on M; setter on W | Clearer on M; clearer on W |
|---|---|---|---|
| NETWORK_TIME_OFF | Caller `network_time_on`; direct or `night/` `network_time_off.json` and `network_time_off.action.json`; explicit `night_plan.json` for provenance | M: `joulewise/network_time_off.py:87–111`, `joulewise/b5/driver.py:1901–1915`. W: `joulewise/network_time_off.py:87–111`, `joulewise/b5/driver.py:2058–2072` | M: no automatic ON restore in the night driver; audit 4.5 names the manual runbook step (`implicit-state-machines.md:261`). W: `scripts/run_night.py:4500–4522` and `:4588–4594` restore and read back ON, subject to ownership and lock deferral. |
| AC_HIGH_POWER | Caller `ac_powermode` and `night_lock_held`; unique recorded marker owner if available | M: power-mode writer absent. W: `joulewise/align/apple/powermode.py:479–510`; R1 `scripts/align_r1_rehearsal.py:470–482` | M: power-mode clearer absent. W: `joulewise/align/apple/powermode.py:519–534`; R1 `scripts/align_r1_rehearsal.py:392–454`; shell `scripts/night_chains/align_r1_rehearsal.zsh:6–18` has an unconditional trap restore. |
| HIGH_POWER_MARKERS | `high-power.marker`, `.align-r1-high-power`; first-line tag and second-line JSON owner; explicit plan id, or textual match to an explicitly supplied plan root/path | M: writer absent. W: names at `joulewise/align/apple/powermode.py:51,89`; owner writer `:148–164`; W1 creation `:503`; R1 `scripts/align_r1_rehearsal.py:472–478` | M: clearer absent. W: `joulewise/align/apple/powermode.py:519–534`, `:291–340`; R1 `scripts/align_r1_rehearsal.py:439–453`. W's `owned_by`/W1 filter is at `powermode.py:60–66,178–186`; this reader reports non-W1 debt too. |
| NIGHT_PLISTS | Caller loaded census; only the two exact `<label>.plist` filenames in supplied roots; explicit plan id; `night/result.json` presence only; optional structural outcome | Both: `joulewise/night_agent_install.py:496–505` publishes and bootstraps | Both: `joulewise/night_agent_install.py:537–555`, bootout proof before deletion. A loaded terminal label without an active span is owed an uninstall. |
| NIGHT_LOCK | Caller held state and optional owner; `night.lock` existence only | M: host-power lock implementation absent. W: `joulewise/align/apple/powermode.py:189–233` | M: absent. W: `joulewise/align/apple/powermode.py:236–243`; the kernel releases the lock when the final inherited descriptor closes. A reported debt means investigate the holder, not force-unlock it. |
| SPOTLIGHT_STOPPED | Caller stopped state; `desk_fence.json` purpose, PID and deadline; caller PID liveness; `spotlight-stopped` existence only in explicitly supplied roots | Both: `scripts/run_align_r0_launchagent.sh:73–81`; fence set by `scripts/launch_align_r0.py:269` | Both: `scripts/run_align_r0_launchagent.sh:25–40` resumes PIDs and removes the receipt only on success; `scripts/launch_align_r0.py:122–127` clears the owned fence. Both R0 files have identical blobs across M and W. |
| KEEP_AWAKE_AGENT | Caller loaded state and standing authorization; no home-directory plist is opened | Neither ref has a repository setter for the original manual install. M: `RUN_STATE.md:38`, W: `RUN_STATE.md:36`, item 19 records `local.jwbench.keepawake` loaded for good | Neither ref has an automatic clearer; the same item and audit 4.5 record the permanent assumption. No new writer or restorer was added. |

The filesystem allowlist also includes `night_plan.json` to match recorded
owners. The only nested names are the fixed `night/` receipt names and
`night/result.json`. Result content is never read. No glob finds plans,
restoration journals, LaunchAgents, R0 jobs, payloads or measurement artifacts.
A caller must explicitly name any additional roots. The W1 courier delivery
and chain-fault records do not prove any host setting, so this module does not
open them.

Ancestors are resolved to permit macOS `/var` and `/tmp` aliases. The supplied
root and every accessed descendant use descriptor-relative `O_NOFOLLOW` opens.
No directory is enumerated. Symlinks outside the allowlist are never inspected.
Nonregular files, oversized files and decode errors cannot count as absence.
Recorded absolute owner paths are compared as strings, never resolved or opened.
The reader does not acquire `night.lock`, run commands or consult host defaults.

## CLI

Required interface: `python3 -m joulewise.host_effects --state-dir D` with
optional `--network-time`, `--ac-powermode`, repeated `--loaded-label` and
`--json`. Exit codes are declared in `EXIT_CODES`: 0 clean, 1 any debt,
3 unknowns only, 2 invalid invocation or refused input path. Debt takes
precedence over unknowns, which still appear in the report.

Extra flags expose the remaining caller observations: `--plan-dir`,
`--night-lock`, `--active-plan PLAN START END`, `--no-active-spans`,
`--no-loaded-labels`, `--spotlight`, `--keep-awake`,
`--keep-awake-expected`, and `--outcome`. Loaded-label arguments declare a
complete census of the three known labels, including keep-awake; omission is
unknown. Contradictory explicit keep-awake facts are refused. No span census is
inferred from marker absence. The minimal invocation normally exits 3.

## Verification

Modules ran sequentially. Total test time was far below 20 minutes.

| Command | Result |
|---|---|
| `python3.13 -B -m py_compile joulewise/host_effects.py` | PASS before tests were added. |
| `python3.13 -B -m unittest tests.test_host_effects` | PASS at each iteration: 29 tests in 0.585 s; 29 in 0.309 s; 30 in 0.424 s; 30 in 0.529 s; 30 in 0.643 s; final 30 in 0.694 s. |
| `python3.13 -B -m unittest tests.test_fixture_orphan_census` | PASS, 14 tests in 0.577 s, 2 skipped. |
| `python3.13 -B -m unittest tests.test_gen_state` | PASS, 44 tests in 13.043 s. Ran separately to respect the one-module-at-a-time rule. |
| `python3.13 -m compileall -q joulewise/host_effects.py tests/test_host_effects.py` | PASS. Applied only to the Python files touched; no existing Python source changed. |
| `python3.13 -B -` local in-memory mutation harness over `ClassifierTests` | All 10 selected mutants failed assertions, with zero test errors. No mutant source was written to disk. |
| `git diff --check` | PASS. |

The local mutants changed inclusive span start, exclusive span end, network
and AC invariant disjunctions, marker ownership matching, terminal label result
logic, Spotlight deadline, keep-awake authorization, unknown outcome reporting,
and observation-error reporting. This is local verification, not a cold review
or a claim of exhaustive mutation coverage. Tests also cover frozen snapshots,
classification without filesystem/clock/process/network access, all three
states for every effect, unknown dependencies, owner conflicts, malformed and
oversized records, path refusals, ancestor aliases, default TMPDIR creation,
CLI exit precedence, and the actual module entry point.

## Limits, uncertainty, and next step

No live hardware validation was performed. No measurement, custody, sealed
results or prohibited personal path was opened. No model weights or MLX were
used. The full suite was intentionally not run under the machine-load rule.
Python 3.13 was executed; Python 3.11 compatibility was maintained by using
standard-library APIs and syntax available there, but not executed here.

The audit's network-time invariant is applied literally. It may flag a host
that current operational instructions deliberately leave OFF between windows.
This is an advisory shadow finding, not authority to restore or change that
policy. Marker and receipt ownership is recorded provenance, not a verified
proof of which process last changed a live setting. Files and caller snapshots
are not an atomic observation. Missing ownership is retained as missing.

The next step is the lead's cold review and integration decision. Any future
live check must be lead-controlled and respect the quiet-machine gate. Writers,
ledger adoption, restoration actions and a complete native host census remain
outside this seat. No new coordination task was registered.


## Round 2

Applied the Fable review's HE-1, HE-2 and HE-3 fixes. The review file is
unchanged. Work stays on `feat/2026-11-11-sm-host-effects`, as the round-2
brief requests. Intake, the inactive stop card, audit section 8, lane PLAN,
and both generations of the arm-stack source were read locally. No network,
host probe, real data, model weights or measurement job was used.

### Changes and decisions

- HE-1: a known owner uses its full half-open span. Before start, a label
  with an observed absent result is explained by `AWAITING_PLAN_SPAN`.
  During the span it is explained by `ACTIVE_PLAN_SPAN`. At or after end,
  a present result retains `NIGHT_LABEL_TERMINAL_WITHOUT_ACTIVE_SPAN` debt.
  An observed absent result now creates
  `NIGHT_LABEL_AFTER_SPAN_WITHOUT_RESULT` debt. A result before start is
  unknown with `RESULT_BEFORE_PLAN_SPAN`.
- Network time off and a held night lock use the same waiting/active/ended
  timing when their owner has a known span. An unrelated active plan cannot
  excuse an ended owner's effect. The two audit host invariants retain their
  literal definitions. In particular, the network-time invariant can flag
  OFF before a span even when the owed-effects row explains the waiting state.
- Unknown result presence, missing clock or census, ambiguous inactive spans
  for one owner, unobserved live settings and unknown outcomes retain unknown
  rows. The label invariant shares the timing classifier. An observed absent
  result alone no longer makes a loaded label pass when its timing is unknown.
- HE-2: mode 1 is explicitly tested as set and owed without a lock. The
  nonzero-mode implementation was already correct. The test rejects the
  review's mode-2-only mutant.
- HE-3: `HostFacts.plan_spans` now names the complete known-plan census.
  Its docstring explicitly includes past, current and future start/end times.
  The CLI accepts `--plan-span` and `--no-plan-spans`; `--active-plan` and
  `--no-active-spans` remain aliases. Their fixed-clock JSON output is byte
  identical. The Python field uses the new name.
- The ignored-file test now uses `sealed-like/measurement-secret`.

Changed files are `joulewise/host_effects.py`, `tests/test_host_effects.py`
and this report. No writer, coordination state, review, fixture data, tool-map
row or timing-map line changed. No new module or tool was added.

### Failing-first evidence and checks

All test modules ran sequentially, with the default TMPDIR. Total test time
was well below 20 minutes. No full suite was run, per the load restriction.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_host_effects` | Baseline: PASS, 30 tests, 0.424 s. After the timing change: 33 tests, six stale label-invariant expectations failed; those expectations now retain unknown timing. Subsequent PASS runs: 33 tests in 0.324 s; 37 in 0.238 s; 39 in 0.509 s. |
| `python3.13 -B -m unittest tests.test_host_effects.ClassifierTests.test_owned_label_timeline_and_boundaries tests.test_host_effects.ClassifierTests.test_owned_network_and_lock_timeline_and_boundaries tests.test_host_effects.ClassifierTests.test_mode_one_is_set_and_owed_without_lock` | Before the fix: 3 tests, 14 expected HE-1 subtest failures, 0.004 s. Mode 1 already passed against correct code. |
| `python3.13 -B -` in-memory HE-2 probe | The new mode-1 assertion fails against `mode == 2`. An initial whole-module reload broke enum identity and was discarded as a harness error. Compiling only the target function corrected the harness; the mutant then failed the assertion without a test error. |
| `python3.13 -B -m unittest tests.test_host_effects.ClassifierTests.test_purity_frozen_snapshots_and_no_io` | Before the field rename: expected TypeError for `plan_spans`, 1 test, 0.001 s. An earlier invocation before the test rename passed, 1 test, 0.001 s. |
| `python3.13 -B /private/tmp/jw-host-effects-round2-mutations.py` | Initial pass: 278 mutants, 260 killed, 36.205 s. Surviving ownership and reason-code changes prompted stronger assertions. Second pass: 278 mutants, 277 killed, 34.605 s; one equivalent boundary survivor. Final pass: 279 mutants, 278 killed, 35.637 s; the same equivalent survivor. The exact HE-2 value mutant was killed. |
| `python3.13 -m compileall -q joulewise/host_effects.py tests/test_host_effects.py` | PASS. Limited to the touched Python files; no script was changed. |
| `python3.13 -B -m unittest tests.test_fixture_orphan_census` | PASS, 14 tests, 2 skipped, 0.346 s. |
| `python3.13 -B -m unittest tests.test_gen_state` | PASS, 44 tests, 10.885 s. |
| `git diff --check` | PASS before the report; repeated at the final diff gate. |

### Mutation coverage and survivor

The local harness compiles only classifier functions in memory. It never
writes mutant source into the repository. It mutates every `if` and conditional
expression to true, false and its inverse, inverts comparisons and boolean
operators, changes span boundaries, and removes loop/comprehension iterations.
The two host invariants, the label invariant, all of `owed_effects` including
its nested row classifier, and all span/label explanation helpers are included.
All 56 conditional sites took both outcomes in the instrumented baseline.

The final pass killed every mutant in `owed_effects` (150), the network-time
invariant (12), the AC invariant (12), the label invariant (12), `_active` (20),
`_span_explanation` (12) and `_label_explanation` (40). It killed 20 of 21 in
`_plan_phase`. Of 278 kills, 275 had assertion failures; three failed only
with test errors when guards were removed. This is a bounded local mutation
pass, not independent cold verification or all possible value mutations.
The final pass includes the exact HE-2 mode-2-only value mutant.

| Survivor | Why equivalent |
|---|---|
| Mutant 180: `_plan_phase`, `facts.now < spans[0][0]` becomes `<=` | This fallback runs only after the matching span was found inactive. Equality at start has already returned `active`, so equality is unreachable here. Both choices return the same before/after phase for every valid fact reaching this line. The start and end boundary tests still reject changes to `_active` itself. |

The temporary harness and JSON manifest are at
`/private/tmp/jw-host-effects-round2-mutations.py` and the matching `.json`.
They contain code and synthetic-test mutation metadata only. They are not
committed fixture data.

### Limits and handoff

Python 3.13 was executed. Python 3.11 was not executed. The code remains
standard library only with compatible syntax and APIs.
No native hardware or MLX validation is claimed or needed for these pure
synthetic fixes. A live host census remains a lead-controlled future check.
No open contract question was found. The lead's next step is cold review of
this round-2 commit, then its integration decision. The local commit message is
`Fix host-effect span timing and close Fable review gaps`. Nothing was pushed.
