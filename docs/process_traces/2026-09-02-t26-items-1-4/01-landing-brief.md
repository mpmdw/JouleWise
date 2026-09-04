WRITE_SCOPE: ["docs/decision_log.md","docs/agent_playbook.md","tests/test_docs_freshness.py","docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md","docs/process_traces/2026-08-27-t26/process-proposals/README.md"]
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: implementation

# INSTALL T26 cold-gate verdicts — items 1 and 4 (docs + tests), plus the D-170 entry

Linked worktree `/Users/edr/code/JouleWise-wt-t26-a`, branch
`feat/2026-09-02-t26-install` @ 300ca7f2 (kernel rows already committed by the
magistrate: `T26-RULING-INSTALL-01`, `ED-BRANCH-PROTECTION-E1-01`,
`ED-D118-NA-TIER-E2-01`, and a `kind: decision` dependency on D-170 in
`V5-TRANSACTION-01`). You cannot commit; the magistrate commits. Never run
`python -m unittest discover`; run named modules only. `TMPDIR` is preset under
the scratchpad. NEVER edit `docs/process/state_kernel.json`, `RUN_STATE.md`,
`TASK_QUEUE.md`, `README.md`, or anything outside WRITE_SCOPE.

## Situation (verified at the bench 2026-09-02)

The cold gate of 2026-08-27 ruled four AMENDED process verdicts:
`docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
(read it in full first; items at :45-111, :113-160, :162-253, :255-300;
summary table :302-317). It merged as PR #231 and its refuter's sealed output
was custodied in PR #238. NONE of the four mechanisms reached the repo:
- item 1: `docs/decision_log.md` "How To Use This Log" (:10-20) has no
  `open (installs via <TASK-ID>)` form; no status-vocabulary test exists in
  `tests/test_docs_freshness.py`; `docs/agent_playbook.md` Mission M0 (:50 ff.)
  has no pending-decision-dependency line; no D-number carries the verdicts.
- item 4: no `## Executed evidence` shape test exists; D-160 R-5 was never
  amended.
(Items 2 and 3 are being installed by two sibling seats on other branches —
do NOT touch `.github/`, `joulewise/arm_readiness*.py`, or their tests.)

You are implementing a RULING, verbatim where it speaks. If a ruled clause
cannot be implemented as written, STOP that clause and return a
`NEEDS_RULING` flag naming the clause, the obstacle, and two concrete options;
do not improvise. Everything else still lands.

## Deliverables

### A. Decision-log entry D-170 (index row + body)

Index row `| D-170 | ... | open (installs via T26-RULING-INSTALL-01) |` after
D-169 (:~193), body `## D-170: ...` after the D-169 body (:~10437 ff.; follow
the shape of D-165..D-169 — Options Considered and Considerations are
mandatory per the How-To). The entry carries the four T26 verdicts BY POINTER
to the ruling file (one paragraph per item quoting the ruled text's operative
sentence and citing `COLD-GATE-RULING.md:<lines>`), names the installing row
and the three branches, and records:
- item 2's amendment to D-118 "Mechanical enforcement" (`:7806`) — write the
  ruled text (`COLD-GATE-RULING.md:128-143`) into D-170's body as "amends
  D-118 additively"; ALSO append to the D-118 body, immediately after the
  `:7806` paragraph, ONE dated line: `**AMENDED by D-170 (T26 cold gate item
  2, 2026-09-02):** the gate ledger has a tracked form — see D-170.` Never
  rewrite the existing paragraph.
- item 4's amendment to D-160 R-5 — the ruled text (`COLD-GATE-RULING.md:
  270-282`) goes in D-170's body; append to the D-160 body (`:10326` ff.) ONE
  dated pointer line of the same shape. Never edit R-5 in place.
- item 3 — pointer only (the code lands on the sibling branch); D-170 states
  the ruled relation verbatim (`COLD-GATE-RULING.md:196-215`) and that the T-0
  ruling file gains the dated Horizon line (deliverable D below).
- the "Where recorded" obligations of each item and which are discharged
  by this PR vs the sibling PRs vs routed to Ed (E1, E2 rows exist).
Status semantics: the row is `open (installs via T26-RULING-INSTALL-01)`
now; the magistrate flips it to `adopted` when all three PRs land.

### B. "How To Use This Log" (item 1)

At `docs/decision_log.md:14-16`, extend the Statuses line so the closed set is
exactly `{accepted, adopted, ratified, open, proposed, superseded, recorded,
executed, adjudicated}` with one-phrase glosses, and add the ruled form:
`open (installs via <TASK-ID>)` — an entry carrying an implementation clause
(a value that enters a manifest, a check code refuses on, a runbook line, a
generator output) names the state-kernel task that carries the uninstalled
clauses; the task the clause GATES holds a `kind: decision` hard-start
dependency on the D-id; it moves to `satisfied` only with an evidence pointer
at the regression that FAILS when the ruled value is absent at the producer.
Write it so a row-writer can apply it from this text alone (writing
standard: define every term at first use; no word does unpaid work).

### C. Tests in `tests/test_docs_freshness.py` (items 1 and 4)

Beside `test_decision_index_matches_decision_bodies` (:177):
1. `test_decision_index_status_vocabulary_is_closed`: every index Status
   cell's leading token is in the closed set above (a `superseded by D-NNN`
   cell's leading token is `superseded`; check what tokens the live index
   actually uses FIRST — `grep -o '^| D-[0-9a-z]* |.*| [a-z]*' ` — and if a
   live cell uses a token outside the ruled set, do NOT widen the set:
   report it as a finding with the row id and STOP that assertion behind a
   `NEEDS_RULING` flag, keeping the rest of the test).
2. `test_open_decisions_name_an_installing_kernel_task`: every `open` cell
   matches `open \(installs via ([A-Z0-9-]+)\)` (a bare `open` with no
   pointer is ALSO accepted only for rows whose D-number is below D-170 —
   the ruling binds prospectively from its merge; assert the prospective
   rule for ≥ D-170), the named id exists in `state_kernel.json` `tasks`,
   AND some task in the kernel carries a `kind: decision` dependency whose
   `target` is that row's D-id (for D-170 that task is `V5-TRANSACTION-01`
   — already committed; the test must find it by scanning, not by name).
3. Fix the `D-\d{3}` regex in the existing test to `D-\d{3}[a-z]?` so
   D-150a/D-150b are no longer silently skipped (verify the existing test
   still passes after the widening; if it fails on a real inconsistency,
   report it — do not paper over it).
4. `test_dated_magistrate_rulings_carry_executed_evidence` (item 4): over
   `docs/process_traces/<YYYY-MM-DD-*>/**/*MAGISTRATE-RULING*.md` whose
   directory date is ≥ 2026-08-29, any file containing a `## Rulings`,
   `## RULED`, or `## Addendum` heading must also contain a
   `## Executed evidence` section holding at least one fenced block with a
   `$ ` argv line plus an `exit` line, OR a `file:line` citation
   (`[A-Za-z0-9_./-]+\.(py|md|json|sh|toml|yml):\d+`). Existing files are not
   retro-failed; state in a comment which files the test currently scans and
   the result for each.
Each new test gets a MUTATION CHECK you run and report: temporarily break the
input in a scratch copy (or monkeypatch the path the test reads) and show the
assertion fails naming the row/file. Do not leave the mutation in the tree.

### D. T-0 ruling file (item 3's "Where recorded")

`docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md`
Horizon paragraph (:73 ff.): append — never edit in place — one dated line
`**Horizon — AMENDED by cold gate 2026-08-28 (T26 item 3):** the 5 s
issuance bound and the 35 s corollary are STRUCK; the retained relation is
`0 ≤ (valid_until_monotonic_ns − 21_600_000_000_000) −
r1_batch_finished_monotonic_ns ≤ 600_000_000_000` on the ordinary monotonic
clock, a liveness bound, not a metrology bound — see
`docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
item 3 and D-170.`

### E. Mission M0 line (item 1) and a trace README

`docs/agent_playbook.md` Mission M0 gains one line: "a pending `kind:
decision` dependency in `state_kernel.json` is an uninstalled ruling — the
task is not selectable until the dependency is satisfied with an evidence
pointer (D-170)". Create
`docs/process_traces/2026-08-27-t26/process-proposals/README.md` (≤25 lines):
what the directory holds, the install date and branches, and that the
consult-brief "Executed:" block requirement (item 4, "Where recorded") has
NO tracked template home in this repo — say so plainly; the magistrate carries
it in the scratchpad brief template.

## Verify and report (verbatim tails)

- `python3 -m unittest tests.test_docs_freshness tests.test_gen_state`
- `python3 scripts/gen_state.py --check`
- the four mutation checks (C.1, C.2, C.3-widening, C.4), each with the
  failing assertion text
- `git status --porcelain` — only WRITE_SCOPE files dirty.

FINAL message = `claude-codex-report/v1` envelope (implementation) with a
`verification` entry per command, `flags` for any NEEDS_RULING, and a "Change"
section mapping A–E → file:line, plus the ruled clause each discharges
(`COLD-GATE-RULING.md:<lines>`).
