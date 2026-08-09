# Run report — 2026-08-08 T1 window session

> Evidence base (successor-assembled, dictated-fills): `RUN_STATE.md` lines 49–187; the T1 scratchpad `trace-notes.md`; `git log d81c78a..d071a3d`; recovery ruling commit `e265c9c`; trust checkpoint `1cae2bc`; and the named trust manifests/recovery report below.

**DELIVERABLE CHECK — SHIPPED:** the fixture-substrate ruling and addendum (`8788891`, `b7aad49`), Codex Fast Mode as the standing default on the tracked bridge (`de759c9`), the recovery escalation design (`bc01908`) and cold-gate ruling on the recovery branch (`e265c9c`), and the T1 consistency sweep (`2ba514a`). (Evidence: commit messages in `git log d81c78a..d071a3d`; `RUN_STATE.md` lines 92–101.)

**DELIVERABLE CHECK — NOT SHIPPED:** the T1 primary deliverable was not completed: recovery did not merge and therefore did not discharge ARMING; trust did not pass its decisive regression/final verification, publish the release, rewrite fixture history, reach PR/CI, or merge. (Evidence: `trace-notes.md` §0 and §§“TRUST 2b harvest + 2c launch”/“COLD GATE”; `RUN_STATE.md` lines 57–90; `trust2b-report-recovery.md` “Residual risk”; `trust2c-out.manifest.jsonl` line 2.)

Session shape: Phase-A continuation under D-128, with recovery, trust, and desk/bookkeeping lanes in disjoint worktrees, later expanded to a six-lens recovery delta fan-out and a two-instance cold gate. (Evidence: `trace-notes.md` §§0, “Shape”, “Launches”, and lines 105–113/167–194.) Exact session start/end wall time is **UNVERIFIED**; the primary trace labels the session “2026-08-08 afternoon,” while the final checkpoint records Ed's night stop order. (Evidence: `trace-notes.md` title; `RUN_STATE.md` line 49.)

## Product outcomes

### Mainline decisions and process changes

| Outcome | Status | Evidence |
|---|---|---|
| Release-asset hydration adopted for the 3.087-GiB/3.31-GB fixture problem; the ruling specifies a digest-pinned tar.zst release asset, required production-proof CI job, 38 content directories leaving Git, and a retained census manifest. | SHIPPED as ruling; implementation/PR not merged | `8788891`; `trace-notes.md` lines 42–45; `RUN_STATE.md` lines 92–97. The 3.087-GiB input and ~142-MiB archive estimate are from the trace; the built archive's measured values are in `trust2b-report-recovery.md` “Change.” |
| Classifier denial on two lead-side history-rewrite attempts was honored; rewrite was deferred, custody made first, and exact future commands recorded. | SHIPPED as addendum; rewrite pending | `b7aad49`; `trace-notes.md` lines 46–60; `RUN_STATE.md` lines 84–89. |
| Codex Fast Mode became the standing default on `scripts/codex-bridge`, with `CODEX_SERVICE_TIER=default` as opt-out; the machine-local v3 wrapper was also changed under Ed's authorization. | SHIPPED on tracked bridge | `de759c9`; `trace-notes.md` lines 87–96; `RUN_STATE.md` lines 123–130. Independent post-session verification of the machine-local wrapper is **UNVERIFIED**. |
| T1 consistency corrections reconciled the C-050 label, fast-mode wording, D-127 status, suite counts, live selection state, and ruling supersession text. | SHIPPED | `2ba514a` commit message in `git log d81c78a..d071a3d`. |

### Recovery / ARMING blocker

Recovery delta 1 failed the banked FIX-1..13 tree: unexecuted-proof remained alive at count 2; hard-link lease aliasing, late preservation sampling, lint blindness, and the orphan leak were recorded, while inspect-as-permission was ruled dead. (Evidence: `721593b`; `trace-notes.md` lines 61–70.) The ESC-2 design consult produced and the magistrate adopted FIX-14..18, including dual slot/object lease identity, the two-invocation preservation witness, double-keyed crash authorization, and receipt provenance analysis. (Evidence: `bc01908`; `trace-notes.md` lines 71–83.)

The FIX-14..18 implementation reported all in-run mutations killed, a 71-row registry, census 22/3/46, and `2785 OK`; it was explicitly ungated pending delta 2. (Evidence: `4495609`; `trace-notes.md` lines 100–104.) Delta 2 then returned all six lenses NOT-CLOSED: G1 reproduced unexecuted-proof at count 3; G2 repeated the lease family at genesis publication; G3 repeated preservation at gate timing; G4 found an inherited-pipe hang; G5 found analyzer laundering; and G6 found destructive crash-authorization cleanup. (Evidence: `0c30993`; `trace-notes.md` §§“DELTA-2 TRIAGE” and “DISPOSITION FORMING”; recovery branch log `468e0a6..e265c9c`.)

The mandatory cold gate confirmed the freeze and prohibited FIX-19 AST hardening because the claimed in-process anti-fabrication property is unattainable in Python. (Evidence: `e265c9c:docs/process_traces/2026-08-08-recovery-exits-escalation/COLD-GATE-SYNTHESIS.md`, “Both instances agree.”) It ruled ARMING dischargeable only after one ordinary executed-probe fix round for G2/G6/G4, a D-117 manual arming procedure, and non-delegable lead live verification; witness integrity moved to a separate out-of-process mutation-kill harness, with an L1-style limitation surfaced to Ed. (Evidence: the same synthesis, “MAGISTRATE RULING” items 2–5; `RUN_STATE.md` lines 58–72.)

The licensed G2/G4/G6 fix round did not start before Ed's stop order; the recovery worktree was recorded clean. No scoped delta, lead replay, integration tree, PR, CI, D-121 review, merge, or ARMING discharge occurred. (Evidence: `RUN_STATE.md` lines 58–69; `d071a3d` commit message.)

### Trust / mint bar

Round 2b started from `1cae2bc` with a 24-path WRITE_SCOPE, Sol xhigh, and an eight-hour cap. (Evidence: `trust2b-out.manifest.jsonl` line 1; `trace-notes.md` lines 52–56.) It ran for 28,803,970 ms (8:00:03.970) and ended `ACCEPTANCE_FAILED` at `report_capture` because the required report was missing; all 12 actual changed paths were within declared scope and `scope_violation_count` was zero. (Evidence: `trust2b-out.manifest.jsonl` line 2.)

The recovered 2b report establishes partial implementation and proof: the transport/archive and trust changes occupied exactly the 12 paths in its envelope; no commit or `git rm` occurred; `reduce.py` matched SHA-256 `5118849d…`; ABA registration, absent-mode custody parity, authentication/custody/transport focused suites, the V2 pinset subset, and the 190/190 fixture census passed. (Evidence: `trust2b-report-recovery.md` envelope V1–V6 and “Verification notes”; changed-path cross-check: `trust2b-out.manifest.jsonl` line 2.)

One authentic unpatched production-CLI mint passed as an internal stage of the 4,056.083-second decisive-regression run, but the overall test failed later in the test-only open auditor before production bidirectional equality and the attack/mutation legs. (Evidence: `trust2b-report-recovery.md` V7 and “Verification notes.”) After auditor repair, a focused diagnostic reported `counts 193 193 equal True`, but the wholesale regression did not complete; the report explicitly says the diagnostic is not a substitute for final proof. (Evidence: `trust2b-report-recovery.md` “Bidirectional production open/registry equality” and flag F1.) V1 byte parity, the complete focused generalized-mint suite, `git diff --check`, full unpiped suite, two requested commit-split diff files, and the 16-item future-delta checklist were not reached. (Evidence: `trust2b-report-recovery.md` V8–V9, flags F2–F3, and “Also not reached.”)

The external archive was built with SHA-256 `f1286bc814c9b392667a82443a2aa73df087ca126056d5046da597a310db9553`, 3,333,877,627 logical bytes, and 191 logical files; the recovered report records reproducible-byte, fresh-hydrate, loader, 190/190 census, and 193-record checks as passing. (Evidence: `trust2b-report-recovery.md` “Change” and “Built archive self-verification.”) The trace records a draft release asset upload and fresh-download SHA match, but publication remained gated on a post-harvest hydrator census. (Evidence: `trace-notes.md` lines 114–116; `RUN_STATE.md` lines 81–86.) Independent lead re-verification of archive/release is **UNVERIFIED**. (Evidence: `trust2b-report-recovery.md` flag F4 and “Residual risk.”)

Round 2c started from the same `1cae2bc` head with a narrower 18-path scope, Sol high, and the verification-tail instruction. (Evidence: `trust2c-out.manifest.jsonl` line 1; `trace-notes.md` lines 159–163.) It ran for 3,782,506 ms (1:03:02.506), reported no attempt-changed paths, and ended `ACCEPTANCE_FAILED` at `report_capture` with a missing report and unknown semantic completion. (Evidence: `trust2c-out.manifest.jsonl` line 2.) The final checkpoint says the tail “ran” and directs harvest from disk, but no supplied primary report establishes a 2c proof outcome; all claimed 2c test results are **UNVERIFIED**. (Evidence: `RUN_STATE.md` lines 73–80; `trust2c-out.manifest.jsonl` line 2.)

### What shipped against the primary deliverable

The session removed the fixture-substrate design blocker and converted the recovery freeze into a bounded ruling, but neither product branch crossed its terminal merge gate. (Evidence: `8788891`; `e265c9c`; `RUN_STATE.md` lines 57–90.) The primary outcome was therefore partial: trust was unblocked at the substrate-design layer, while recovery ARMING and the trust mint bar remained unmerged. (Evidence: `trace-notes.md` §0; `RUN_STATE.md` lines 58–89.)

## Verification evidence — claim ledger

| Claim | Result | Primary evidence |
|---|---|---|
| Recovery FIX-14..18 in-run suite | PASS reported: 2785 OK; later delta invalidated closure, not the suite tail | `4495609`; `trace-notes.md` lines 100–104 |
| Recovery delta 2 | NOT-CLOSED, all six lenses | `0c30993`; `trace-notes.md` lines 121–145 |
| Recovery cold gate | RULING ADOPTED; no fix/merge | `e265c9c` synthesis; `RUN_STATE.md` lines 58–72 |
| Trust 2b reduce.py SHA | PASS (`5118849d…`) | `trust2b-report-recovery.md` V1 |
| Trust 2b ABA regression | PASS, 1 test | `trust2b-report-recovery.md` V2 |
| Trust 2b authentication/custody/transport suites | PASS, 14/7/7 | `trust2b-report-recovery.md` V3–V5 |
| Trust 2b V2 pinset subset | PASS, 4 tests | `trust2b-report-recovery.md` V6 |
| Trust 2b fixture census | PASS, 190/190 | `trust2b-report-recovery.md` “Verification notes” |
| Trust 2b authentic production mint | PASS as internal stage only; containing regression FAILED | `trust2b-report-recovery.md` V7 |
| Trust 2b bidirectional equality | NOT COMPLETED; 193/193 focused diagnostic only | `trust2b-report-recovery.md` flag F1 |
| Trust 2b wholesale regression/matrix | FAIL/incomplete: 1 test, 4056.083 s, failures=1 | `trust2b-report-recovery.md` V7 |
| Trust 2b v1 parity / full suite | NOT RUN | `trust2b-report-recovery.md` V8–V9 |
| Trust 2c tail | UNVERIFIED; report missing, semantic status unknown | `trust2c-out.manifest.jsonl` line 2 |
| This bookkeeping turn | Inspection only; project tests NOT RUN because the request was evidence drafting with no repository writes | Delivery envelope; starting/final `git status --short --branch` |

## Restart instructions

1. **Recovery first:** relaunch the clean G2/G4/G6 arm-fix round from `impl/d117-ledger-recovery@e265c9c` using `recovery-armfix-prompt.md`; require the three executed site probes, focused suites, and a site-scoped delta. Do not harden FIX-14 AST gates. Another lease facet escalates to an IDENTITY-MODEL consult. (Evidence: `RUN_STATE.md` lines 58–72; `e265c9c` synthesis items 1, 2a, 5.)
2. **Then recovery gate chain:** lead replay → integration tree against current main → PR → CI → D-121 → merge; ARMING is not discharged before this plus the D-117 manual procedure and lead live verification. (Evidence: `RUN_STATE.md` lines 67–72; `e265c9c` item 2b.)
3. **Trust harvest before belief:** inspect the worktree diff on top of `1cae2bc`, recover/resume 2c only if useful, and independently rerun the decisive regression, equality, v1 parity, focused suite, `git diff --check`, and full unpiped suite. (Evidence: `RUN_STATE.md` lines 73–80; `trust2b-report-recovery.md` flags F1–F3; `trust2c-out.manifest.jsonl` line 2.)
4. **Trust integration:** split auth-core/substrate commits; verify archive/hydrator census before publishing `fixture-d117-v2-production-v1`; then permissioned history rewrite, 16-question delta, PR/CI, terminal review. Remove temporary permissions after merge. (Evidence: `RUN_STATE.md` lines 81–89/103–109; `trace-notes.md` lines 57–60/114–119.)
5. **Keep U2 frozen:** branch `5b00200` remains count 3 and post-window. (Evidence: `RUN_STATE.md` lines 90/111–114.)

## Process trace appendix

### Shape

The session began with three disjoint lanes: recovery delta, trust substrate consultation/implementation, and T0 bookkeeping, using separate worktrees and quiescent main. (Evidence: `trace-notes.md` “Shape”/“Launches.”) It evolved into ESC-2, one recovery implementation, a six-lens parallel delta, and a two-instance cold gate; trust evolved into an eight-hour 2b monolith plus narrower 2c tail. (Evidence: `trace-notes.md` lines 71–119/147–194; trust manifests.)

### Catches

- **Substrate Sol consult:** out-designed the listed options with release-asset hydration; adopted in full. (Evidence: `8788891`; `trace-notes.md` lines 42–45.)
- **Recovery delta 1:** kept unexecuted-proof alive at count 2, found lease alias/preservation timing, confirmed orphan leak, killed inspect-as-permission. (Evidence: `721593b`; `trace-notes.md` lines 61–70.)
- **ESC-2 consult:** rejected single-key lease identity and supplied dual identity, two-invocation binding witness, double-key crash capability, and sequencing. (Evidence: `bc01908`; `trace-notes.md` lines 76–83.)
- **Recovery implementation:** caught the `git diff` omission of untracked files; four support files were included in the pathspec commit. (Evidence: `trace-notes.md` lines 100–104.)
- **Delta 2:** G1 count 3; G2 genesis dirfd; G3 fingerprint timing; G4 pipe hang; G5 analyzer laundering; G6 invalid-stage unlink. (Evidence: `0c30993`; `trace-notes.md` lines 121–145; `e265c9c` item 2a.)
- **Cold Opus refuter:** reproduced freeze, caught the G2 label contradiction, refined G6 severity, and forced the core-seam/F1 disagreement into synthesis. (Evidence: `trace-notes.md` lines 167–194; `e265c9c` synthesis.)
- **Cold Fable adjudicator:** identified the unattainable in-process property and supplied the fix/manual-gate plus mutation-kill replacement. (Evidence: `e265c9c` synthesis.)
- **Trust 2b:** exposed the 68-minute verification atom and macOS `/dev/fd` auditor defect; authentic mint passed before overall failure. (Evidence: `trace-notes.md` lines 147–158; `trust2b-report-recovery.md` V7.)
- **Ed/lead:** honored classifier denial; granted rewrite permissions, fast default, and harder parallelism; preserved custody before rewrite. (Evidence: `trace-notes.md` lines 46–60/87–99; `RUN_STATE.md` lines 103–109.)

### Deliberations

The substrate consult compared checkout cost, raw-byte LFS metering, and compression behavior before release hydration was adopted. (Evidence: `trace-notes.md` lines 42–45; `8788891`.) Recovery stopped ordinary fixing when two consecutive rounds—including a “terminating” consult—repeated lease/preservation families and count 3 reproduced unexecuted-proof. (Evidence: `trace-notes.md` lines 137–145/167–174; `0c30993`.) The cold disagreement was preserved: the refuter rejected a bare clean-core landing; the adjudicator also rejected a bare merge but supplied a bounded fix/manual-gate path and moved future-test-author integrity off path. (Evidence: `e265c9c` “The split.”) Trust scheduling established that fast inference cannot shorten a 68-minute real-fixture test; substrate/auth should have been parceled while verification remains slow. (Evidence: `trace-notes.md` lines 97–99/147–163.)

### Interventions

The lead honored two classifier denials, created custody, pre-staged but did not publish the release, and waited for both cold opinions. (Evidence: `trace-notes.md` lines 46–60/114–116/167–194.) Ed changed policy to Codex-fast/Claude-lean and harder parallelism, authorized bridge/wrapper changes and temporary permissions, then issued the stop order leaving nothing in flight. (Evidence: `trace-notes.md` lines 57–60/87–99; `RUN_STATE.md` lines 49–51/103–109.)

## Delegation calibration

| Stream / run | Mechanism / tier | Outcome | Evidence |
|---|---|---|---|
| Substrate ruling | read-only Sol xhigh | Design win; adopted | `trace-notes.md` lines 24–26/42–45; `8788891` |
| Recovery delta 1 | review Sol xhigh | Failed closure; count-2 escalation | `trace-notes.md` lines 20–23/61–70; `721593b` |
| ESC-2 | read-only Sol xhigh | First launch failed for missing literal scope line; relaunch yielded five designs | `trace-notes.md` lines 71–83; `bc01908` |
| FIX-14..18 | implementation Sol xhigh | In-run green; all six external lenses not closed | `trace-notes.md` lines 84–104/121–145; `4495609`; `0c30993` |
| Delta 2 | six graders, high/xhigh, fast | High yield; scoped-runner lock forced workaround | `trace-notes.md` lines 105–113/121–145 |
| Cold gate | cold Fable + Opus | Independent reproduction plus productive disagreement | `e265c9c` synthesis |
| Trust 2b | Sol xhigh, standard tier, 8 h | Partial; report wall; 68-minute test dominated | `trust2b-out.manifest.jsonl`; `trust2b-report-recovery.md` V7 |
| Trust 2c | Sol high | Ran 63:02; no report; outcome unknown | `trust2c-out.manifest.jsonl`; `RUN_STATE.md` lines 73–80 |
| T0 bookkeeping | Fable dictated-fills | Shipped `d81c78a`; caught blob sizing and duplicate label | `trace-notes.md` lines 15–18/27–28/40–41 |

## Yield and spend estimate

The trace names at least 15 model-bearing lanes/roles: substrate consult, recovery delta 1, bookkeeping subagent, ESC-2, recovery implementation, six delta-2 graders, trust 2b, trust 2c, and two cold judges; it also records one instant failed ESC-2 wrapper launch. This is a lower bound, not a runner census. (Evidence: `trace-notes.md` “Launches,” lines 71–113/147–194; `e265c9c`.) Unique yield concentrated in independent design/review: substrate consult changed storage; delta 1 forced escalation; delta 2 produced six non-closures; the cold pair created the bounded ruling. (Evidence: `8788891`; `721593b`; `0c30993`; `e265c9c`.)

Exact session spend is **UNVERIFIED** because both manifests record `token_usage:null`, no whole-session spend snapshot is supplied, and the trace is not billing evidence. (Evidence: both trust manifest line 2 records.) The only explicit token figure supplied is `1,909,882` at the end of `trust2b-report-recovery.md`; whether directly billable, resumed-context-inclusive, or summable is **UNVERIFIED**, so it is not total T1 spend. Exact measured runner wall time is available only for 2b (8:00:03.970) and 2c (1:03:02.506). (Evidence: manifest line 2 in each file.)

## UNVERIFIED / open at close

- Every claimed trust 2c result; report missing and semantic completion unknown. (`trust2c-out.manifest.jsonl` line 2.)
- Final passing trust regression, equality within it, attack/masking/mutation legs, v1 parity, focused suite, `git diff --check`, full suite. (`trust2b-report-recovery.md` F1–F3.)
- Independent lead archive/release verification and publication. (`trust2b-report-recovery.md` F4; `RUN_STATE.md` lines 81–86.)
- Trust commit split, rewrite, delta, PR/CI/D-121, merge. (`RUN_STATE.md` lines 80–89.)
- Recovery fix, probes, delta, replay, PR/CI/D-121, merge, ARMING discharge. (`RUN_STATE.md` lines 58–72.)
- Exact session duration, total spend, exhaustive launch count. (Evidence gap: trace plus null manifest token usage.)
- Current machine-local wrapper bytes and skill-fold bytes. (`RUN_STATE.md` lines 97–100/123–130 are reports only.)
