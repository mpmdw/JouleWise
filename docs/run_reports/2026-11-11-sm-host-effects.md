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
