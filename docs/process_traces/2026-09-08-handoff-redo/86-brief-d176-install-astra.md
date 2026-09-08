WRITE_SCOPE: ["docs/decision_log.md","docs/process/state_kernel.json","TASK_QUEUE.md","RUN_STATE.md","tests/test_gen_state.py","docs/contracts/pack_night_go_receipt.md","docs/process_traces/2026-09-08-handoff-redo/85-d176-install-astra-report.md"]

# Seat brief — install D-176 (D-169 stage 3 ruling): decision log, kernel graph, and the seat-1 contract draft (gpt-6-astra, high)

HEAD of this worktree carries the packet at docs/process_traces/2026-09-08-handoff-redo/78-coldgate-packet-d169-stage3/
(00-PACKET, exhibits A-E, 10-coldgate-fable-ruling.md, 11-coldgate-opus-refutation.md, 13-magistrate-synthesis.md).
13-magistrate-synthesis.md is the RULING OF RECORD; where it says "the judge's text governs" copy from 10-; where it
adopts an Opus amendment copy from 11-. Do not re-decide anything; install.

Deliverables:
A. docs/decision_log.md: a `## D-176: …` entry in the file's established shape (see D-172..D-175: Trigger, Decision,
   Why, Evidence) with the six decisions of the synthesis stated in full (not by pointer), the failure-mode tests, and
   "adopted by cold gate + Opus refuter + magistrate synthesis 2026-09-08 (Ed may veto)"; add the index row near the
   top table (D-175's row is the model) — tests.test_docs_freshness checks index ↔ bodies.
B. docs/process/state_kernel.json: install synthesis §5 EXACTLY, each clause naming its JSON pointer: re-root
   UNATTENDED-LAUNCH-01's hard start on the D-176 decision (kind "decision", authority = the synthesis path) and
   make T0-UNATTENDED-01 a close dependency; S9-06-WINDOW-T0-GO-RECEIPT-GATE-01 closes by UNATTENDED-LAUNCH-01's PR
   (dependency text); D169-STAGE3-01 start satisfied by D-176, close = decisions 1-4 merged + NIGHT-PACK-REHEARSAL-01
   harvested; NEW row NIGHT-PACK-REHEARSAL-01 (goal, lane agent, priority p1_phase_gate, fences copied from
   NIGHT-REHEARSAL-01, hard-start on UNATTENDED-LAUNCH-01 merged AND NIGHT-REHEARSAL-01 harvested); V5-G2B-SHAKEDOWN-01
   hard-starts on it; T0-UNATTENDED-01's hard start on NIGHT-REHEARSAL-01 replaced by D-176; T0-REHEARSAL-PRODUCERS-01's
   stale `REHEARSAL_PRODUCER_WORK_ORDER` pointer replaced by a pointer to the G1–G10 table in exhibit A (copy that
   table into the packet dir as 14-g1-g10-table.md — allowed as part of the trace scope? NO: that path is not in
   scope; instead point at exhibit A's section heading and line); T0-LIVENESS-BOUND-EMPIRICAL-01 status_note: registered
   limitation through G2-b, must close or be reruled before ALPHA; V5-TRANSACTION-GO-01 goal text amended per §5.
   Then `python3 scripts/gen_state.py` and `--check` rc 0; update tests/test_gen_state.py EXPECTED_IDS (+NIGHT-PACK-
   REHEARSAL-01) and the count pin (+1) with a dated comment; `python3 -m unittest tests.test_gen_state` rc 0.
C. docs/contracts/pack_night_go_receipt.md (NEW): the seat-1 contract — schema `joulewise.pack_night_go_receipt.v1`
   with the judge's exact key list (10- §1) as a table (key, type, bound-to, checked-where), producer (night driver
   after ARM verify), consumer contract (`_consume_launch_capability` required keywords, callee re-read/re-digest,
   every binding equality, the two ruled refusal codes and their R-8 registration), consumption record v3 additions
   and the v2 legacy rule, `verify_consumed_launch` replay rule, the transaction authorization record (§2: keys,
   purposes, claim_eligible), the step-6 confirmation record and the argv/consumption-record route with the
   environment route forbidden (§3), the rehearsal purpose and G7 rule (§4), the retirement of
   `joulewise.t0_unattended_d149_go_receipt.v1`, and a D-170 clause map (which existing ruling clause each contract
   line installs). Plain language, first-use terms defined (Ed's writing standard); it must be replicable from the
   text alone.
D. docs/process_traces/2026-09-08-handoff-redo/85-d176-install-astra-report.md: what you installed where (file:pointer
   per clause), verification commands + rc, anything you could not install and why.
Acceptance: gen_state --check rc 0; tests.test_gen_state rc 0; tests.test_docs_freshness rc 0 (each to a log, rc
from the process). Never the repository-wide suite; no `git commit`; header < 8192 bytes; genre implementation
verdict keys.
