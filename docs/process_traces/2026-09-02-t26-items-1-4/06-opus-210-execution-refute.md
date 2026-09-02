# REFUTE (execution lens) — T26 items 1 + 4 + Q1/Q2 install, `2d24ef70`

Seat: Opus 5, execution lens. Worktree `/Users/edr/code/JouleWise-wt-t26-a2`
(detached at `2d24ef70`, five commits over `6075389a`). All mutations reverted
in-run; tree byte-clean at exit (proof at the bottom). No commits, no
`unittest discover`, no codex/claude launched, `JouleWise-wt-t26-a` untouched.

**Same-signature statement:** first round on this branch. No prior round shares
a signature with this one.

**Headline:** `test_dated_magistrate_rulings_carry_executed_evidence` (item 4)
asserts on **zero files** in the repository as it stands, including on the very
ruling that installs it. Two of the brief's named counterfactuals (M7, M8) —
the ones the ruling most wanted killed — SURVIVED. The assertion itself is
sound (positive control M7b kills); the *trigger* is the defect, and the
trigger is verbatim from the ruled text, so the seat installed a mechanism the
ruling shipped DOA and then recorded it in `T26-RULING-INSTALL-01` acceptance
as "present and mutation-killed."

---

## Mutations

Suite for every row: `python3 -m unittest tests.test_docs_freshness tests.test_gen_state`
(52 tests). `TMPDIR` set to the scratchpad probe dir. `M-` rows are the brief's
named counterfactuals; `M13`–`M15` and the lettered sub-probes are mine.

| id | mutation | verdict | killed_by (test : assertion line) |
|---|---|---|---|
| M1 | `docs/decision_log.md:212` D-170 status → `decided` | **KILLED** | `test_decision_index_status_vocabulary_is_closed` : `tests/test_docs_freshness.py:257` — *"'decided' not found in {…}"* |
| M2 | same row → `Accepted` (capitalised) | **KILLED** (+ spurious ERROR) | `…vocabulary_is_closed` : `:252` *"status has no leading token"*; ALSO `test_open_decisions_name_an_installing_kernel_task` raises `AttributeError` at `:263` (`re.match(...).group(0)` on `None`) — an ERROR, not a diagnosis |
| M3 | same row → `open (installs via NO-SUCH-TASK-01)` | **KILLED** | `…installing_kernel_task` : `:280` *"installing kernel task does not exist"* |
| M4 | same row → `open (installs via ARM-PACKET-01)` (task exists, carries no `kind:decision` dep on D-170) | **SURVIVED** | — (see F2) |
| M4b | M4 **plus** strip the D-170 dep off `V5-TRANSACTION-01` | **KILLED** | `…installing_kernel_task` : `:293` *"no kernel task has a kind: decision dependency on this row"* |
| M5 | add index row `\| D-150c \| probe row \| frobnicated \|` | **KILLED** | `…vocabulary_is_closed` (subTest `decision_id='D-150c'`) : `:257` — the widened `D-\d{3}[a-z]?` regex **does** iterate suffixed ids; `test_decision_index_matches_decision_bodies` also fails |
| M6 | `state_kernel.json` D-170 dep `state → satisfied`, `evidence: null` | **KILLED** | `scripts/gen_state.py --check` exit 2: `gen_state: tasks[V5-TRANSACTION-01].dependencies[0]: satisfied dependency requires evidence`; suite errors in `tests.test_gen_state` |
| M6b | same dep → `satisfied` with a *valid but vacuous* pointer (`{"path":"README.md","label":"placeholder…"}`), D-170 left `open` | **SURVIVED** (suite `OK`) | `gen_state --check` exits 1 only on incidental `DRIFT: TASK_QUEUE.md generated region differs` — regenerating clears it (see F3) |
| M6c | D-170 index status → `adopted (magistrate; PR #999)` while the install task is `partial` and the dep `pending` | **SURVIVED** | suite `OK`, `gen_state --check` exit 0 (see F4) |
| M7 | delete the `## Executed evidence` heading from `…/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md` | **SURVIVED** | — **F1** |
| M8 | keep heading; drop the `exit 0` line from the fence **and** the only `file:line` citation (`_has_executed_evidence` → `False`, verified directly) | **SURVIVED** | — **F1** |
| M8b | drop only the `exit 0` line (citation kept) | SURVIVED | — F1 (and F5 once triggered) |
| M8c | drop only the citation (`exit 0` kept) | SURVIVED | — F1 (and F5 once triggered) |
| M7b | *positive control*: rename `## Disposition` → `## Rulings`, then delete the evidence heading | **KILLED** | `test_dated_magistrate_rulings_carry_executed_evidence` : `tests/test_docs_freshness.py:310` — the assertion works; only the trigger is dead |
| M7c | rename `## Disposition` → `## Rulings`, evidence intact | SURVIVED (correct) | — |
| M9 | pre-cutoff ruling (`2026-08-25-packroot-consult/03-MAGISTRATE-RULING.md`, has `## Rulings`) copied to `docs/process_traces/2026-09-09-probe/` with the evidence section stripped | **KILLED** | `…carry_executed_evidence` : `:310` — prospective gate is on the **directory** date, as ruled |
| M9b | same file under `2026-08-30-probe/` | **KILLED** | `:310` — ≥ 2026-08-29 boundary holds |
| M9c | same file under `2026-08-28-probe/` | SURVIVED (correct) | — pre-cutoff exemption is exact |
| M10 | `docs/process_traces/2026-09-09-probe/foo-impl.md` with no `## Clause map` | **KILLED** | `test_custodied_impl_reports_carry_clause_map` : `:327` *"missing ## Clause map heading"* |
| M10b | same file under `2026-09-01-probe/` | SURVIVED (correct) | — prospective ≥ 2026-09-03 holds |
| M10c | same file under `2026-09-03-probe/` (boundary) | **KILLED** | `:327` — boundary is inclusive, as ruled |
| M10d | clause map present, header `\| clause \| where \|` | **KILLED** | `:340` *"Clause map table header must name production site, biting assertion, and counterfactual"* |
| M10e | clause map with the three ruled cells + divider | SURVIVED (correct) | — |
| M10f | clause map body is only `\| NOT PINNED: everything \|` | SURVIVED (**as ruled** — S1 grants the escape hatch) | — see F7 |
| M11 | delete the S2 sentence from `docs/contracts/bridge_protocol.md:71` | **KILLED** | `test_bridge_protocol_clause_map_pins_s1_and_s2` : `:347` |
| M11b | **re-wrap** the S2 sentence at 80 cols, semantics identical | **KILLED — false positive** | `:347` (see F6) |
| M11c | `**Clause map (ruling installs)**` → `**Clause map**` | **KILLED** | `:345` |
| M12 | remove `ED-D118-NA-TIER-E2-01` from `EXPECTED_IDS` | **KILLED** | `tests.test_gen_state.TestRefreshedStateFidelity.test_exact_live_id_set` — census binds |
| M13 | D-170 row's status cell written `\| decided\|` (one space lost before the closing pipe) | **SURVIVED** | — **F5b**: `_decision_index_rows()` drops from 172 → 171 rows; D-170 vanishes from *both* item-1 tests with no signal |
| M14 | dead-evidence ruling in `docs/process_traces/**archive**/2026-09-09-probe/` (non-dated top-level parent) | **SURVIVED** | — F8; the identical file at `2026-09-09-probe/` **KILLED** at `:310` |
| M15 | with the trigger forced live, citation-only and exit-only variants | both SURVIVED | — the `or` at `:134` is as ruled (item 4 allows execution record **or** code-path proof); see F5 for the citation branch's shape |

---

## Findings

### F1 — BLOCKER: the item-4 test asserts on zero files; its acceptance claim is false
- **Site:** `tests/test_docs_freshness.py:296-311` (trigger at `:299-301`), scanning `:110-111`.
- **Counterfactual input:** M7 (delete `## Executed evidence` from the 2026-09-02 magistrate ruling) and M8 (gut the section until `_has_executed_evidence` returns `False`, verified by direct call).
- **Observed:** suite `OK` both times. Instrumented directly:

```
docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md | trigger= False | has_evidence= False
docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md  | trigger= False | has_evidence= True
files actually asserted on: 0
```

  The trigger is `^## (?:Rulings|RULED|Addendum)(?:\s.*)?$`, case-sensitive. The
  2026-09-02 ruling's headings are `## Disposition`, `## Ruled text (…)`,
  `## Installation (…)`, `## Executed evidence` — `Ruled` ≠ `RULED`, so it does
  not match. Across all 22 `*MAGISTRATE-RULING*.md` files in the repo the
  trigger fires on 11; the split is generational — `## Rulings` appears 9×
  (older convention), while the current template uses `## Disposition` +
  `## Ruled text`. The prospective date cutoff (≥ 2026-08-29) selects exactly
  the two files written under the *new* convention, i.e. the cutoff and the
  trigger are disjoint by construction. Absence will never be "loud at CI time"
  for any ruling written from here on.
- **Why this is a blocker, not a nit:** `T26-RULING-INSTALL-01`
  `acceptance.evidence[1]` (`docs/process/state_kernel.json`) reads *"tests.test_docs_freshness green with … the Executed-evidence shape test present and **mutation-killed**."* M7 and M8 are precisely that mutation, and neither kills. The acceptance criterion is asserted-but-unmet.
- **Aggravating:** the in-test comment at `:297-298` says *"MAGISTRATE-RULING-UNATTENDED-STAGE1.md is the **only** eligible file; it has no Rulings/RULED/Addendum heading, so is exempt."* The 2026-09-02 ruling in the same commit is equally eligible and equally exempt; the comment enumerates the exemption one file short, which is exactly the enumeration that would have exposed the vacuity.
- **Cause split (for adjudication):** the trigger vocabulary is *verbatim ruled text* (`COLD-GATE-RULING.md:288-293`: "containing a `## Rulings`, `## RULED`, or `## Addendum` heading"). So the seat installed as ruled; the defect originates in the ruling. But the ruled clause "installed as ruled" and the acceptance clause "mutation-killed" are jointly unsatisfiable here, and per the `T26-RULING-INSTALL-01` fence that collision is a magistrate dissent to record, not a green acceptance row. Positive control M7b proves the fix is one word wide (add the current heading vocabulary, or trigger on any `## Ruled*`/`## Disposition`).

### F2 — SHOULD-FIX: the item-1 dependency check does not check the named task
- **Site:** `tests/test_docs_freshness.py:282-294`.
- **Counterfactual input:** M4 — D-170 status → `open (installs via ARM-PACKET-01)`.
- **Observed:** SURVIVED. `dependent_tasks` is a scan of **all 119 kernel tasks**
  for *any* `kind:decision` dep targeting the row's D-id; the task named inside
  the status cell is only existence-checked at `:280`. Today the named task
  `T26-RULING-INSTALL-01` has `"dependencies": []`; the D-170 dep is carried by
  `V5-TRANSACTION-01`. So the two assertions are satisfied by two unrelated
  tasks, and the status cell's `<TASK-ID>` is load-bearing for nothing beyond
  spelling. M4b confirms the only thing that kills is total absence of the dep
  anywhere in the kernel.
- **Against authority:** `COLD-GATE-RULING.md:88-101` (item 1 enforcement) ruled
  the test assert *"`open \(installs via ([A-Z0-9-]+)\)` with that id present in
  `state_kernel.json` `tasks` **AND that task carrying a `kind: decision`
  dependency targeting the row's D-id**"*. The ruled *rule* body at `:67-86`
  places the dep on "every task the clause gates," which for item 3 is
  `V5-TRANSACTION-01` — so the ruling is internally in tension, and the seat
  resolved it to the **weakest of the three available readings** (any task)
  rather than either ruled reading.
- **Fence violated:** `T26-RULING-INSTALL-01.fences[1]` — *"any deviation from
  the ruled text is a magistrate dissent recorded separately and shown to Ed,
  never a silent reinterpretation by the installing seat."* The kernel
  `status_note` and `decision_log.md:10559-10562` do describe the gated-task
  placement, but `decision_log.md:10557-10558` affirmatively states this entry
  *"records them by pointer and does not reinterpret them"* — which is not
  accurate about the enforcement clause. No dissent record exists.
- **Available stronger form:** assert the named task carries the dep, *or* the
  named task's `status_note`/`acceptance` names the gated task that does.

### F3 — SHOULD-FIX: "satisfied" needs only a pointer that resolves, not a regression
- **Site:** `scripts/gen_state.py:185-188` + `_check_pointer` `:131-165`.
- **Counterfactual input:** M6b — D-170 dep `satisfied` with
  `{"path": "README.md", "label": "placeholder pointer that proves nothing"}`.
- **Observed:** dependency validation passes; the 52-test suite is `OK`.
  `gen_state --check` exits 1 only with `DRIFT: … TASK_QUEUE.md generated
  region differs`, which is the *incidental* consequence of the task becoming
  selectable — regenerate and the mutation is invisible.
- **Against authority:** item 1 ruled the dep moves to satisfied *"only with an
  `evidence` pointer at the repo-relative path (+ anchor) of the **regression
  that FAILS when the ruled value is absent** at the producer"*, and
  `T26-RULING-INSTALL-01.acceptance.evidence[4]` repeats it. Nothing mechanical
  distinguishes that pointer from `README.md`. (M6, the null-evidence case, is
  correctly refused — that half is real.)

### F4 — SHOULD-FIX: nothing closes the loop when a row moves off `open`
- **Site:** `tests/test_docs_freshness.py:260-294` (the `!= "open": continue` guard at `:263`).
- **Counterfactual input:** M6c — D-170 → `adopted (magistrate; PR #999)` while
  `T26-RULING-INSTALL-01.status == "partial"` and the D-170 dep is `pending`.
- **Observed:** suite `OK`, `gen_state --check` exit 0. The entire item-1
  mechanism is opt-in by a string the row-writer controls: editing one cell
  from `open (…)` to `adopted` silently removes the row from every check while
  the ruling stays uninstalled. That is the exact `decided ≠ done` failure the
  item was minted to prevent (and option (2) in D-170's own Options Considered,
  rejected on the merits but not mechanically foreclosed). A check in the other
  direction — a non-`open` row whose D-id still has a `pending` `kind:decision`
  dep in the kernel is a contradiction — costs three lines.

### F5 — SHOULD-FIX: `_has_executed_evidence`'s citation branch is satisfied by a doc pointer
- **Site:** `tests/test_docs_freshness.py:120-134`, citation regex at `:130-132`, `or` at `:134`.
- **Counterfactual input:** M15 / M8b, run with the trigger forced live.
- **Observed:** SURVIVED with no execution record at all. The regex is
  `[A-Za-z0-9_./-]+\.(?:py|md|json|sh|toml|yml):\d+`, matched anywhere in the
  section. In the 2026-09-02 ruling the satisfying token is
  `docs/contracts/bridge_protocol.md:48-49` — a *home-anchor* pointer for where
  Q1's text was filed, not a code path at which anything refuses. Item 4 ruled
  branch (b) as *"a code-path proof citing the `file:line` at which the path
  refuses"*; any prose citation to any `.md` line clears it.
- **Answering the brief's sub-question:** a bare `:162-260` is **not** treated
  as a citation — the regex requires a `name.ext` prefix, so the ruling's own
  `` `:787` `` does not count. That is the correct behaviour and should stay;
  the over-permissive half is `.md:\d+`, which arguably should be narrowed to
  source extensions (`.py`, `.json`, `.sh`, `.toml`, `.yml`) for the code-path
  branch.
- **F5b (same site class, `nit`→`should_fix`): silent row-skip.** M13 —
  `| decided|` with one space lost before the closing pipe — drops D-170 from
  `_decision_index_rows()` (172 → 171 rows) and disables *both* item-1 tests for
  that row with zero signal; `test_decision_index_matches_decision_bodies` still
  passes because it uses a looser regex (`^\| (D-\d{3}[a-z]?) \|`) on the same
  table. One assertion closes it: the two extractions must return the same
  count.

### F6 — NIT (real false positive): the S2 pin is a raw substring over wrapped Markdown
- **Site:** `tests/test_docs_freshness.py:346-348`.
- **Counterfactual input:** M11b — re-wrap the S2 sentence at 80 columns,
  semantics byte-identical modulo `\n> `.
- **Observed:** **FAILS**. `docs/contracts/bridge_protocol.md:71` is 140 chars
  in a file whose surrounding block quote wraps at ~75; the line was left
  unwrapped to satisfy this assertion. A prose test that constrains prose
  layout will fire on the next formatting pass. `re.sub(r"\s+", " ", ...)` on
  both sides before `assertIn` removes the coupling. (M11 and M11c confirm the
  pin does bite real deletions, so the mechanism is worth keeping — just
  normalize.)

### F7 — NIT: clause-map shape check grades the header row only
- **Site:** `tests/test_docs_freshness.py:318-341`.
- **Observed:** M10e passes with body row `| a | b | c |`; M10f passes on
  `| NOT PINNED: everything |` alone. Both are *as ruled* — S1 explicitly
  provides the `NOT PINNED: <reason>` escape and the ruled duty on `NOT PINNED`
  rows is handed to the refuters, not to CI — so this is recorded for the
  magistrate's awareness rather than as a defect. Worth noting only that the
  escape hatch is granted per-*file* here (one `NOT PINNED:` line anywhere in
  the section skips the whole table check), not per-row as the ruled text reads.
  Also: `assertIsNotNone(section, …)` at `:326` sits outside a `subTest`, so the
  first offending report aborts the scan and hides the rest.

### F8 — NIT: any non-dated parent directory removes a trace from both scans
- **Site:** `tests/test_docs_freshness.py:99-106` — `path.relative_to(trace_root).parts[0]`.
- **Counterfactual input:** M14 — the M9 dead-evidence file placed at
  `docs/process_traces/archive/2026-09-09-probe/MAGISTRATE-RULING-probe.md`.
- **Observed:** SURVIVED; the identical file at `docs/process_traces/2026-09-09-probe/` KILLED.
  Only the *top-level* component is date-tested, so any future
  `process_traces/archive/…` reorganisation (the repo already archives traces —
  see `6075389a`'s message) silently empties both prospective scans. Scanning
  for a dated component at any depth would close it. Currently harmless: the
  three non-dated top-level entries are `RESUME-2026-07-2{6,7,8}.md` files, not
  directories.

---

## Tests

Clean tree, `TMPDIR=…/scratchpad/tmp-opus-a2`:

```
$ python3 -m unittest tests.test_docs_freshness tests.test_gen_state
----------------------------------------------------------------------
Ran 52 tests in 1.453s

OK
```

```
$ python3 scripts/gen_state.py --check
(no output)
gen_state exit=0
```

```
$ shasum -a 256 docs/process/coldgate_charter.md
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81  docs/process/coldgate_charter.md
```

Charter digest matches the value pinned in the brief and in the 2026-09-02
ruling's `## Executed evidence` section.

Representative kill tails (full transcripts not retained; each was produced
under the mutation named in the table and reverted immediately):

```
FAIL: test_decision_index_status_vocabulary_is_closed (… ) (decision_id='D-170')
AssertionError: 'decided' not found in {…} : D-170: status token is outside the closed vocabulary: 'decided'
```

```
FAIL: test_open_decisions_name_an_installing_kernel_task (…) (decision_id='D-170')
AssertionError: [] is not true : D-170: no kernel task has a kind: decision dependency on this row
```

```
$ python3 scripts/gen_state.py --check
gen_state: tasks[V5-TRANSACTION-01].dependencies[0]: satisfied dependency requires evidence
EXIT=2
```

```
FAIL: test_dated_magistrate_rulings_carry_executed_evidence (…) (path='docs/process_traces/2026-09-09-probe/MAGISTRATE-RULING-probe.md')
AssertionError: False is not true : …: dispositive ruling lacks a valid ## Executed evidence section
```

---

## Tree clean at exit

```
$ cd /Users/edr/code/JouleWise-wt-t26-a2 && git status --short
$ git stash list
$ git log --oneline -1
2d24ef70 Process-rules cold gate 2026-09-02 (terra 201): Q1 clause map installed in bridge_protocol §1 …
```

`git status --short` produced **no output** — the tree is byte-clean, still
detached at `2d24ef70`, no stashes, no commits made. All probe directories
(`2026-09-09-probe`, `2026-08-30-probe`, `2026-08-28-probe`,
`2026-09-01-probe`, `2026-09-03-probe`, `archive/`) were `rm -rf`'d in the same
command block that created them. Scratch files live only under
`…/scratchpad/tmp-opus-a2/`.

No fixes applied.
