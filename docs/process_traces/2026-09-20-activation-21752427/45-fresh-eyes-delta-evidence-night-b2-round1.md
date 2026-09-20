# Record 45 — fresh-eyes delta re-audit of B2 fix round 1 (`798bced1..67a147c4`), 2026-09-20 ≈14:40 PDT

Auditor: Opus 5 subagent (read-only; /tmp/dr41-b2). Verbatim report:

**VERDICT: PASS** (D1–D8 all land as dictated; four should-fix/nit findings, no blocker, nothing wider or narrower than the brief)

**1. Closure table** (all in `joulewise/evidence_night.py`; HEAD 67a147c4): D1 `:1198-1201` fresh `observe_veto(state, attempt/"veto-at-publication.json")` before `os.replace` `:1203`; earlier `veto.json` still required `:1132`. D2 `:1011-1013` owner-only veto, `non_owner_directives` top-level; malformed still `cannot read directives` `:1004-1010`. D3 `:1021-1026`. D4 `:992` provenance, gates `:1134`+`:1200`. D5 `:257-300`, `:968-976`. D6 `:1136-1142`. D7 `:1074-1080`, `:1217`. D8 `:930`, `:965`; handbook clause added. Mutants: (a) re-observation replaced by the stale record → `test_d1_publication_observes_new_directive_and_each_stop` + `..._unreadable_publication_channels_refuse`: `FAILED (failures=5)` — the mutant **published the plan** with a NO standing; (b) missing magistrate dir = clear → `test_d3_...`: `FAILED (failures=2)`; (c) both production gates deleted → `test_d4_...`: `FAILED (failures=1)`.

**2. D1 semantics** — one code path (`observe_veto`, shared with `veto`:984), per-attempt record written before raising, refuses on any non-clear/unreadable channel; `veto.json` is bound and left byte-identical. Window: two statements between the observation and `os.replace` — same irreducible TOCTOU as the bench; inside `observe_veto`, directives are read before the stop files.

**3. D5/D6** — body = provenance line + `lines[4:]`; banner/To/Subject dropped only. Content complete vs NIGHT_HANDBACK (per-boundary local+UTC+epoch, both install spans, all digests, registration + chain_source shas, the NO clause, `Arm attempt N; prior candidates…`). D6 strictly-newer than prepare.json, check.json and every sealed digest. `Ran 6 tests … OK`.

**4. D7** — `baseline_drift` takes the max decimal attempt; attempt 2 reads `baseline: null`; malformed attempt-1 and legacy `lifecycle/baseline.json` both ignored and preserved. Test passes.

**5. Docs/protected regions** — both byte-identical to `origin/main` (`4c71305c…`, `fc6e3a97…`). All five new refusal strings documented. **No undocumented refusal.**

**6. Suites** — 3.13 `Ran 87 tests in 183.142s / OK`; 3.11.15 `Ran 87 tests in 228.833s / OK`; `test_evidence_arm_sequence + test_arm_retry + test_night_gate` `Ran 108 tests in 5.846s / OK`.

**Findings (delta, all new this round)**
1. *should-fix* — `:1200-1201` is a **surviving mutant**: deleting the boundary production gate passes all 87 tests (exit 0). Defence-in-depth only (CLI can't reach it), but untested.
2. *should-fix* — `:1196` records phase `publishing` **before** an unbounded `gh` network call (`probe_command`:583 has no `timeout`). Contract:283 defines that phase as "the rename may have occurred"; a hang/kill now leaves it set with nothing published, and the hang burns the install window under the candidate lock. Move the observation above `record["phase"]="publishing"` or give it its own phase + a timeout.
3. *should-fix* — doc contradiction: `NIGHT_HANDBACK.md:295` "check and veto are repeated by `publish-install`" vs `evidence_night_entry.md:265` "the lead repeats `check` at the publication boundary". Code repeats only check-record *freshness* + the job-state probe (contract:415 is the accurate wording). The D8 dictation is the defect; risk is the arm-night operator skipping the manual re-`check`.
4. *nit/coverage* — `LifecycleTests.kw` moved to `launchctl_bin="/fixture/launchctl"` (forced by D4), so no test now exercises a successful `fake=False` publication end-to-end; only the D4 refusal touches real-launchctl.
5. *nit* — sent body has no blank line between the provenance line and `Ed,`. Also `tests/test_evidence_night.py:1696` prints a full notice body to real stdout during runs.

Same-signature statements: "the entry point silently diverges from the bench procedure" — true only in the doc direction (finding 3); "an evidence-affecting side effect without a refusal path" — none found.

## Magistrate disposition (14:42 PDT) → round 2 (seat 46, third worktree while replay 44 runs)
1 ACCEPT (a test for the boundary production gate: fixture veto at publication with a real launchctl → refuse). 2 ACCEPT (observe BEFORE `phase = publishing`, own phase `observing-veto`; `probe_command` gets a timeout — 60 s for `gh`, refusal "cannot read directives: timeout"). 3 ACCEPT — the D8 wording was the lead's error: the handbook clause becomes "publish-install repeats the veto observation and the loaded-jobs probe at the publication boundary and requires a fresh check record; the lead re-runs `check` after any change"; contract aligned. 4 nit: a `fake=False` end-to-end path is untestable without launchctl — document as the bench's first-live-use item. 5 nits applied (blank line; silence the test's stdout).
