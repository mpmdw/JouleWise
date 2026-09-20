```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Two execution defects.","workspace":{"base_requested":"798bced1","base_mode":"exact","head_start":"798bced1","head_end":"798bced1","upstream_end":"b8d18349","branch":"feat/2026-09-20-evidence-night-b2"},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"blocker"},{"id":"F2","severity":"should_fix"}]},"verification":[{"id":"V1","kind":"test","cmd":"cd /tmp/b2-execution.H7lheR/repo && /Users/edr/code/JouleWise/.venv/bin/python -B ../refute.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["REFUTATION COMPLETE"]},"expected":{"exit_code":0,"tail_regex":"REFUTATION COMPLETE"}}],"flags":[]}
```

## Findings

**F1 — blocker: publication accepts veto evidence after a new veto appears.**  
`joulewise/evidence_night.py:1097` validates the saved record but never reobserves directives, STOP, standdown, or `lifecycle/NO` before publication.

Executed evidence:

- Clear `veto` → open owner directive → `publish-install`: **`rehearsal_installed`**, one total `gh` observation, two installer calls.
- Clear `veto` → create STOP or `lifecycle/NO`: each also publishes and installs.
- Reproduced through the **real installer with FakeLaunchctl**, with both a newly opened owner directive and `lifecycle/NO` present: installation succeeds.
- Re-running `check` after `veto` also permits installation. Veto records contain no check digest or ordering requirement.
- Freshness is **0–3,600 seconds inclusive**, independently for finish time and file mtime. Executed 3,599-second evidence passes; 3,601-second evidence refuses.
- Preparation binding works: changing `prepare.json` then refreshing check refuses the old veto. Touching a sealed artifact then refreshing check also refuses the old veto.

**Bench comparison:** step 4 reads stop files at lines 8–10 and again at 39–42. It queries directives **once**, at line 11, then asserts that inventory empty at line 32. Thus the missing second stop-file observation is a concrete divergence; “directives twice” is not supported by that script.

The B2 contract explicitly documents snapshots and instructs boundary repetition, so this is not wholly undocumented. The handbook’s replacement sequence omits that qualification and the repeated check. Recommended next step: require fresh channel observations immediately before publication, preserve the second stop-file check, and have the lead settle the intended check/veto binding.

**F2 — should_fix: a valid non-owner directive blocks publication.**  
`joulewise/evidence_night.py:983–989` treats any author other than `mpmdw` as malformed inventory.

Injected a well-formed issue authored by `someone-else`: `veto` writes `clear:false` and refuses with **`cannot read directives: invalid directive issue inventory`**. The issue survives only in raw stdout, rather than a reported, non-vetoing inventory. This contradicts the requested owner-only behavior.

Filter structurally valid issues by owner, preserve non-owner observations, and add the missing negative test. The **non-owner-counts-as-veto mutant survives all three existing directive tests**.

Other executed results:

- **Fail-closed matrix:** nonzero exit, empty stdout, malformed JSON, missing executable, and timeout all replace prior clear evidence with `clear:false` and refuse “cannot read directives.” An owner issue with an empty body correctly refuses as an open owner directive. Injected STOP observation failure also refuses. The runner-error-clears mutant is killed by five assertion failures.
- **Baseline:** after actual fake-launchctl installation, changed file size/mtime, removed a file, and added a file. `verify` reports all three with `drift:true`, returns successfully, and preserves baseline bytes. This matches the report-only baseline semantics; bench step 5:39–48 records metadata without a drift-refusal gate. Injected baseline-scan failure triggers uninstall and restores the unpublished plan.
- **stdin:** intercepted 128 clone-side `P -B -c` calls during composition; no JSON payload remained in argv. Authoring, census, and retry records use stdin. A 1,049,174-byte census request round-tripped through the actual clone interpreter.
- **Notice:** refusal tests pass for missing, non-armable, stale, future-dated, mismatched, and invalidated checks. Refresh recomputes schedule and sealed registration/source bindings; it does **not** recompute attempt number or prior candidates. Repeated draft bytes match. Compared with `prepare.json.notice_draft`, the executed draft only reordered digest lines because saved JSON sorts mapping keys.
- **Handbook:** exactly one hunk, +9/−0. Command names, ordering, candidate arguments, and fallback sentence match the brief; boundary repetition has the F1 qualification. Protected regions are byte-identical: ARM-RETRY-POLICY MD5 `b9c2bda9817c14cf81a6412820385246`; Executed history through EOF MD5 `4c71305c61b0a8e3fea6b8fb9ec8b871`.
- **Tests:** 187 focused tests pass on Python 3.13; all 79 evidence-night tests pass on Python 3.11; three additional handbook-related tests pass.

**Same-signature statements:** “entry point diverges from bench procedure” **survives** through F1’s missing second stop-file check. “Evidence-affecting side effect without a refusal path” **survives at that authorization boundary**: publication and installation proceed despite a newly present NO. Baseline-scan failure itself has a functioning recovery path.

Replay artifacts: [refutation](/tmp/b2-execution.H7lheR/refute.py), [results](/tmp/b2-execution.H7lheR/refute-final.log), [mutants](/tmp/b2-execution.H7lheR/mutants.py), [mutation results](/tmp/b2-execution.H7lheR/mutants-final.log).

## Residual risk

All execution used temporary fixtures and injected seams; no live hardware, real `gh`, real `launchctl`, mail, or network validation occurred. The known blocked-journal watchdog case was not rerun. Final fixture-orphan census could not observe processes: exit 2, `PermissionError: Operation not permitted: 'ps'`; the lead must perform that census.

Repository remains clean at `798bced1`; no repository files changed. `origin/main` advanced concurrently to `b8d18349`; this review remains pinned to the requested commit.