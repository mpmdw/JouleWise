# Watchdog v5 installed-plan review — Sol

2026-11-10. **Verdict: ADMIT.** No actionable regression found in the
reviewed change. This admits the software fix; it is not live watchdog,
process-group, or MBP recovery validation.

Reviewed `git diff origin/main...HEAD` at
`85612ccc272cba8f798a482bb083df18bfe251ef`, based on
`4bd293caa421d85f2d7b46c99276b7c80201c5c0`. The implementation is
`59dd6e2b826e9f9f1c58dcd8e4335f292a64e5ed`, its verification/audit report
is `7b2f2a571`, and `85612ccc2` adds only the earlier seat handoff.
Review branch: `review/2026-11-10-wdv5-sol` (the isolated branch supplied
with this checkout). No code under review was edited.

## Findings against the brief

**(a) Accepted-plan parity: PASS.** The bug description is slightly broader
than the actual defect: both discovery (`scripts/magistrate_watchdog.py:773`)
and the installed reader (`:829`) already used the v2/v3/v4/v5 dispatcher.
The missing allowance was `ac_powermode`. Adding it to that dispatcher fixes
both readers without an installed-only conversion or key stripping.

The review probes exercise six class/schema combinations: v2 diagnostic and
rehearsal, v3 transaction, v4 diagnostic and rehearsal, and v5 HAZARD_PACK.
Each accepts an absent power-mode field and integers 0 and 2: **18 positive
variants**, identical through the driver loader, discovery and both installed
plists. Discovery also deduplicates their shared identity. The arming-side
`NightPlan.from_mapping`, `_plan_ac_powermode`, and `validate_hazard_window`
have identical ASTs to this checkout, checked against Git object
`20e9edbc446a9f89a68badc1bd32bb0934cbb86d`
(`origin/lane/2026-11-08-r1-arm-fixes` at review time). The remaining diff of
that parser file changes comments, driver reason codes and the default-mode
constant, not accepted plan shapes.

**(b) Fail-closed parsing: PASS.** **194 negative variants** are refused by
the installed reader and discovery. These cover null, booleans, floats,
strings, lists, mappings, NaN, Low Power/other integer values for
`ac_powermode`; unknown top-level/nested hazard keys; malformed scalar
types; unknown schemas; cross-version headers; and v2/v3/v4 fields or receipt
classes mixed into v5. An exact retired-v1 shape is ignored only by
discovery's existing retirement rule; either installed plist naming it
remains an error. Future authorship remains covered by the installed-v5
regression. Installed parsing continues to validate each plist before
deduplication.

The pre-fix parser loaded from the base Git object, substituted **in memory**,
rejects the valid synthetic v5 plan with `extra=['ac_powermode']` for both
installed labels. No reviewed source bytes were replaced for this
counterfactual. Five legacy class/schema examples serialize byte-identically
against the base parser/writer. This review makes no throughput claim.

**(c) Terminal release: PASS.** Neither watchdog release code nor
`joulewise.arm_retry.terminal_window_release` changed. With both plists still
installed and the plan outside discovery's glob, **160 combinations** of
start/exit/delivery markers, terminal/unknown verdicts and end times match an
independent expectation of the existing rules. End time equal to now releases;
the next representable future float, null and boolean end times hold. GO,
ABORTED, CHAIN_STOPPED and REFUSED follow the existing collected/null rules.

The result file and courier alone do not latch a release. A fresh decision
also needs empty, proven agent and driver observations and a readable process
table with no custody process. Four additional probes independently hold for
an agent, a driver, a live custody process and an unreadable process table.
Once latched, the next magistrate's own census match does not re-fence the
window; removing `chain.exited` does re-fence an open chain.

The existing span boundaries also remain intact: lead entry is inclusive;
without early release, the nominal completion instant is still fenced;
delivery releases after that instant; absent delivery retains the inclusive
deadman-plus-courier tail; an open chain continues to hold. The installed-v5
and span tests exercise those boundaries. A release candidate is distinct
from a permission to launch: unrelated stop/census/clock/lock gates still apply.

**(d) Recovery helper: PASS within its documented completed-window handoff.**
`scripts/post_window_unstrand.sh` uses existence checks for `chain.exited`,
`result.json` and `courier.sent`; neither inline Python block nor the delegated
uninstall path opens those records. The uninstall path may read
`night_plan.json` to identify a probe label, which is plan metadata. The
watchdog event log is intentionally read, but output includes only transition
state words; reason/alert payloads and process argv are not printed.
`--events` is a trusted operator-selected watchdog event-log path.

The default is an immutable dry run with no launchctl calls. `--go` invokes
the existing verified-uninstall route, checks both plists are gone, and never
kickstarts the watchdog. Directory-valued synthetic markers succeed, proving
they are not opened as records. Existing tests cover live direct driver,
chain, monitor and custody commands, missing markers, wrong-plan/malformed
plists, failed unload and event filtering. Four extra probes show refusal
before uninstall for stderr despite status zero, a partly malformed table,
a nonnumeric PID and an unavailable `ps`. Nonzero/empty output and raised
probe exceptions also fail closed in the code and existing tests.

This is one process snapshot before uninstall, not an interlock against
concurrent rearming. The implementation report explicitly requires the
completed-window handoff with no concurrent rearm; retain that precondition.
A successful uninstall is not proof that a subsequent watchdog launch occurred.

**(e) Reader audit: no missed installed-reader fix.** Searches of repository
source, excluding restricted paths, found the installed/discovery/driver/
installer/census/readiness/evidence readers using the shared dispatcher.
The explicit v2 check at
`scripts/issue_g2a_prefill_prompt_pin.py:262` is an additional reader absent
from the author's audit table. It deliberately requires a
DIAGNOSTIC_NO_PACK G2-a harvest with its registered inventory; it is not a
generic installed-plan reader and should not be broadened to v5 for this fix.
The v2 literals in `gen_derivation_night` and `evidence_night` author legacy
plans; `night_plan_writer` intentionally produces v2/v3/v4. Its existing lack
of a v5 writer path does not affect installed parsing.

## Executed evidence

All tests ran one module at a time, with
`PYTHONNOUSERSITE=1 python3.13 -B -m unittest MODULE`:

| Module | Result | Test time |
|---|---:|---:|
| `tests.test_magistrate_watchdog_v5` | 4 passed | 0.027 s |
| `tests.test_post_window_unstrand` | 9 passed | 5.271 s |
| `tests.test_night_plan_writer` | 11 passed | 0.022 s |
| `tests.test_night_gate` | 113 passed | 1.468 s |
| `tests.test_magistrate_watchdog_cli` | 8 passed | 11.778 s |
| `tests.test_magistrate_watchdog` | 155 passed | 1.591 s |
| `tests.test_magistrate_watchdog_span` | 24 passed | 0.076 s |
| `tests.test_arm_retry` | 36 passed | 0.291 s |

**360 tests passed**, about 21 seconds of reported test time. This includes
the real CLI subprocess test of installed v5 fencing followed by a terminal
dry-run launch. No full-suite or quick-suite launcher was used.

Reproducible review probes are committed alongside this report:

```sh
PYTHONNOUSERSITE=1 python3.13 -B docs/run_reports/interp-energy-desk/wdv5-rev-sol-probes.py
```

Final result: exit 0; 18 accepted / 194 refused parser variants; arming AST
parity; five legacy byte matches; old-parser rejection; 160 installed-only
terminal combinations; four release-process holds; four additional recovery
process-observation holds; marker non-reading and dry-run immutability.
The final complete run passed in 0.913 s wall time.

`bash -n scripts/post_window_unstrand.sh` and `git diff --check` passed.
Only review artifacts are changed, so targeted execution is appropriate;
the brief expressly prohibits the canonical full suite in this running-job
environment.

## Limits, files and handoff

This seat did not rerun `tests.test_magistrate_watchdog_yield`: the author
reports three failures also present on the untouched base when native process
visibility is denied. That baseline comparison is the author's evidence,
not an independently reproduced result of this review. Lead's next exact
native check, outside the sandbox:

```sh
python3.13 -B -m unittest tests.test_magistrate_watchdog_yield
```

Then install the admitted parser in the actual watchdog checkout. At a
lead-controlled completed-window handoff, with no concurrent rearm and proven
native process visibility, run the helper's dry run before the explicitly
authorized `--go`. This seat performed no live uninstall, launchd change,
hardware check or measurement. No MLX code changed; no MLX test applies.

Files added by this seat: this report and
`docs/run_reports/interp-energy-desk/wdv5-rev-sol-probes.py`. All reviewed
production code and existing tests remain unchanged. No code-fix request or
open policy question remains; native integration and actual recovery remain
unverified.

M0 intake found no active stop card and a clean isolated review tree. The
explicit review brief overrides ordinary queue selection. Coordination files
and `tests/test_gen_state.py` were left untouched; no kernel task was
registered. No subagents, network, weights, real custody, real restricted
directories, measurement records or B5 analysis pipeline were accessed.
The long blinded analysis job was not touched. The review is local-only;
no push or merge is authorized or performed. The local review commit is the
commit introducing this report and its companion probes, discoverable with
`git log -1 --oneline -- docs/run_reports/interp-energy-desk/wdv5-rev-sol.md`.
