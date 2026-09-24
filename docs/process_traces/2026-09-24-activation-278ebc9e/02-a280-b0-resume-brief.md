ROLE: IMPLEMENTATION SEAT (RESUMED) for JouleWise lane A280, PR B0. Do not call Claude or any other agent (bridge depth is one hop).

WRITE_SCOPE: ["joulewise/night_kinds.py", "joulewise/evidence_night.py", "scripts/gen_evidence_night.py", "joulewise/night_gate.py", "joulewise/night_agent_install.py", "scripts/run_night.py", "joulewise/zero_capture_facts.py", "tests/test_night_kinds.py", "tests/test_evidence_night.py", "tests/test_gen_evidence_night.py", "tests/test_night_gate.py", "tests/test_night_agent_install.py", "tests/test_run_night.py", "tests/test_zero_capture_facts.py", "tests/test_kind_dispatch_literals.py"]

RESUME PREFACE (activation 278ebc9e). A previous seat on this exact brief was stopped about 25 minutes in by a scheduled stand-down, without a report and without running V1–V3. Its partial work is commit `74b4dc65` ("WIP ... UNVERIFIED") at the tip of branch `feat/2026-09-24-a280-b0-kind-dispatch` in YOUR worktree /Users/edr/code/wt-7370d0fb-a280b0 (base main `2ea6a7ec`). Treat that commit as an untrusted draft, not as done work:
 R1. First read `git diff 2ea6a7ec 74b4dc65` in full and list, per brief item 1(a)–1(f), what the draft did, what is missing, and anything in it that violates §2 MUST NOT CHANGE or introduces a second, unauthenticated kind authority. Fix or revert what violates; complete what is missing.
 R2. Commit on top of `74b4dc65` in logical commits (do not rewrite or squash `74b4dc65`; do not push).
 R3. Your report must include the R1 inventory, and V1–V3 executed at your final head against base `2ea6a7ec` (the diff check is `git diff --check 2ea6a7ec HEAD`).
The original brief follows verbatim except its WRITE_SCOPE line (identical, stated once above); where it says "from main 2ea6a7ec", the branch now also carries `74b4dc65`.

----- ORIGINAL BRIEF 10 (verbatim) -----
ROLE: IMPLEMENTATION SEAT for JouleWise lane A280, PR B0: make every remaining idle-only site dispatch on the night-kind table, with the existing idle night BYTE-IDENTICAL. Do not call Claude or any other agent (bridge depth is one hop).

(WRITE_SCOPE: identical to the line at the top of this prompt; not repeated so the prompt carries exactly one.)

0. CONTEXT AND FENCES.
Worktree (yours): /Users/edr/code/wt-7370d0fb-a280b0, branch `feat/2026-09-24-a280-b0-kind-dispatch` from main `2ea6a7ec`. Commit your work on that branch, in logical commits; do not push.
Fences: never launchctl, sudo, networksetup, powermetrics; never touch /Users/edr/night-custody, /Users/edr/JouleWise-measurement-* or ~/Library/LaunchAgents; never import or execute from /Users/edr/code/JouleWise. Scratch only under /tmp.
Background: PR A (PR #401, merge `1246b299`) added the immutable `NightKind` table (`joulewise/night_kinds.py`), with an idle row (`quiet_predicate_evidence`) and a calibration row, without changing idle behaviour. PR B adds a new "scored" night kind; it has been split, and this PR (B0) is the first, parity-only step. B0 adds NO scored row, NO scored code and NO armable kind.
Inputs (read first, read-only):
- the scout inventory at /Users/edr/code/wt-7370d0fb-bk/docs/process_traces/2026-09-24-activation-7370d0fb/05-a280-prb-scout-report.md, sections T1, T2 and T5 (file:line at `2ea6a7ec`);
- the decomposition consult at /Users/edr/code/wt-7370d0fb-bk/docs/process_traces/2026-09-24-activation-7370d0fb/09-a280-prb-decomposition-consult.md, row B0, Q2 steps 1–4 and Q5.

1. WHAT TO BUILD.
 (a) In `joulewise/evidence_night.py`, replace the module-fixed `KIND` selection at every site in scout T1 with the candidate's kind. The sites are `locations`, `prior_records`, `sealed_candidate`, `notice_subject`, `render_notice`, the H-side census snippet, `notice_unused`, `prepare`, `candidate_state` and `sealed_state`. The kind must come from the same authenticated source that already establishes the candidate's identity (the sealed plan and chain source). A new unauthenticated field such as a bare `state["kind"]` is not acceptable, because it would create a second authority. Where no such source exists yet (for example in `prepare`'s CLI), the idle kind stays the default, and a non-idle kind that has no handler refuses exactly as today.
 (b) Row-selected notice text: the subject label and the idle-only notice clauses (scout T1 rows 7–8) come from the row or from a row-selected renderer. The corecaptured t0 sentence is printed only when the row's `corecaptured_at_arm_and_t0` flag is set. For the idle row every byte of the notice is unchanged.
 (c) `scripts/gen_evidence_night.py`: select the manifest, executor and literal names from the row. The idle `EVIDENCE_*` wrapper bytes are unchanged. `quiet_predicate_campaign` stays idle-only; do not touch it.
 (d) Installer receipt validation and render inspection (`night_agent_install.py` ~793, ~1164), the driver probe dispatch (`run_night.py` ~3690), the artifact inventory and courier/cleanup (`run_night.py` ~1029–1344), and `zero_capture_facts` (~99–120) dispatch by the recognised row. A row with no approved handler FAILS CLOSED with a typed refusal. It must never fall into the calibration path, acquire a ruled registration digest, or gain successor release.
 (e) `night_gate.py`: routing only. Do not add the registration payload-kind comparison; that belongs to B2. Do not weaken any existing refusal (ambiguity, co-export, superseded registration, no-overwrite, chain authentication).
 (f) Tests:
   - `tests/test_night_kinds.py`: a TEST-ONLY third row, injected by patching the table inside the test and never added to the module, driven through production `prepare`/`candidate_state`, notice render, wrapper generation, gate C5/C3, installer render and probe, driver inventory and cleanup dispatch, and `zero_capture_facts`. Each path must either route to the row's declared handler or refuse typed. Unknown-kind admission stays refused.
   - `tests/test_kind_dispatch_literals.py`: a source-level test that scans the shared dispatch files (`evidence_night.py`, `gen_evidence_night.py`, `night_gate.py`, `night_agent_install.py`, `run_night.py`, `zero_capture_facts.py`) for idle literals (`quiet_predicate_evidence`, `QPE01`, `qpe01`, `evidence_manifest.json`, `EVIDENCE_`). Every hit must be inside an explicit allowlist, each entry with a one-line reason. The idle row in `night_kinds.py`, the idle executor and historical records are exempt.
   - Mutation check: temporarily re-hard-code one site back to the idle row and show that a test fails (report the command and the failing test; revert).

2. MUST NOT CHANGE. The eight-artifact byte goldens (`tests/test_night_kinds.py` `test_base_archive_byte_goldens`) and `test_refusal_parity` stay green WITHOUT editing their expected bytes. No change to any idle output, notice byte, wrapper byte, refusal code or refusal text. No scored row, no scored manifest, no new registration digest.

3. VERIFY (execute, paste tails):
 V1. `python3 -B -m unittest tests.test_night_kinds tests.test_evidence_night tests.test_gen_evidence_night tests.test_night_gate tests.test_night_agent_install tests.test_run_night tests.test_zero_capture_facts tests.test_kind_dispatch_literals`
 V2. `git diff --check 2ea6a7ec HEAD`
 V3. the mutation check from 1(f).

4. EARLY RETURN. If a site cannot be generalised without a behaviour change, or its kind cannot be taken from an authenticated source, STOP and return NEEDS_RULING naming the site and the options. Never pick a behaviour change silently. For any file outside WRITE_SCOPE, return NEEDS_SCOPE.

5. ACCEPTANCE. Implementation genre. A report with a per-site table covering every T1 site and every NEW site, each with its before/after file:line and the test that drives it, and the V1–V3 tails. JSON header under 8 KB. Wall budget 3 hours. End your turn only when the work is committed, or on an early return.
