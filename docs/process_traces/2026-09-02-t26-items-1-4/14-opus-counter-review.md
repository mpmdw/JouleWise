# Opus counter-review — PR #273 @ 10845c14

Worktree `/Users/edr/code/JouleWise-wt-t26-a` @ `10845c14`, scope
`git diff main...HEAD` against `/Users/edr/code/JouleWise` @ `403998e1`.
Read-only; no writes outside the scratchpad. All file:line below are on the
branch head unless a `main...<branch>` diff is named.

---

## 1. Does the installed D-170 entry say what the ruling ruled — no creep, no silent drop?

Index row: `docs/decision_log.md:212` —
`| D-170 | T26 COLD-GATE VERDICTS — … | open (installs via T26-RULING-INSTALL-01) |`.
This is item 1's own form applied to the entry that carries item 1. Correct.

Clause-by-clause against `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`:

| Ruled clause | Ruling line | Installed at | Verdict |
|---|---|---|---|
| Item 1 status form `open (installs via <TASK-ID>)` + `kind: decision` hard/start/pending dep + satisfaction only on a producer regression | `:67-81` | `decision_log.md:10483-10491`; How-To at `:22-30` | FAITHFUL |
| Item 1 "not all 460 clauses" scoping | `:84-86` | `decision_log.md:10489-10490` | FAITHFUL |
| Item 1 "the S9 SHORTLIST items marked 'gates the mint' or 'gates windows' are registered under it in the ruling's implementation commit" | `:82-84` | **nowhere** | **SILENT DROP — see SHOULD-FIX 1** |
| Item 2 tracked gate ledger (a)(b)(c), verbatim | `:130-143` | `decision_log.md:10493-10506` (verbatim quote) | FAITHFUL |
| Item 2 E1/E2 routed to Ed | `:145-153` | `decision_log.md:10544-10550`; kernel rows `state_kernel.json` `ED-BRANCH-PROTECTION-E1-01`, `ED-D118-NA-TIER-E2-01` (both `lane: ed_external`) | FAITHFUL |
| Item 3 strike + 600 s liveness relation + ordinary monotonic + provenance | `:196-215` | `decision_log.md:10508-10517` | FAITHFUL (relation transcribed character-for-character against `:201`) |
| Item 4 executed-evidence duty, verbatim | `:269-279` | `decision_log.md:10519-10529` | FAITHFUL text; **citation is `:270-282`, which starts one line inside the quote and runs 3 lines past it into the SUPERSEDED enforcement paragraph at `:281` — see SHOULD-FIX 5** |
| Item 4 charter-v3 deferral + consult-brief `Executed:` having no tracked home | `:296-300` | `decision_log.md:10540-10544`; also `2026-08-27-t26/process-proposals/README.md:13-16` | FAITHFUL (deferral recorded, not hidden) |
| Q1/Q2 paragraph in the D-170 body | process-rules ruling "Installation" | `decision_log.md:10567` | FAITHFUL |

Creep check — I found no clause in D-170 that binds more than the ruling. Two
near-misses, both benign and both NITs below: (a) the How-To at `:14-23`
supplies plain-language glosses for all nine ruled status tokens, which the
ruling did not dictate but enforcement (ii) at `:92-94` presupposes; in doing
so it silently rewrites the pre-existing gloss of `accepted` from "binding
until revisited" (main) to "binding design choice" (NIT 9). (b) Item 2's ruled
text is quoted inside D-170 and D-118 gets only a pointer
(`decision_log.md:7830`), whereas the ruling named D-118's "Mechanical
enforcement" paragraph as "the ONE home" (`:155-156`). Text-once with a
pointer is the better shape and D-170 says so explicitly at `:10536-10537`;
I flag it only so the inversion is on the record (NIT 10).

Wording drift worth one line: the ruling says the dependency sits "on **every**
task the clause gates (at minimum the transaction task …)" (`:75-76`); the
How-To at `decision_log.md:25-27` says "A task that the clause GATES … holds a
hard-start dependency". Singular-indefinite reads as "one is enough". Today only
item 3 gates a task (`V5-TRANSACTION-01`, `state_kernel.json:5387-5395`) so
nothing is lost operationally; the drift matters only if a future clause gates
two tasks.

## 2. Q1 and Q2 — replicable from the text alone?

**Q2 (`decision_log.md:10351`): YES, replicable.** Every term that does work is
built at first use — "the artifact pair the clause quantifies over
(repo-relative paths at a named revision)", "the field as a full JSON pointer",
"both observed values", and the failure branch ("Where no committed pair exists
the clause is recorded `UNVERIFIED against artifacts`"). The line ends with the
ruling path, so the `(S3)` label and the worked exhibit (the
`/identity_units/<i>/model_runtime_config/config_set_sha256` vs the packet's
`…/config_set_sha256` → `None` probe) are one hop away. A reader can rebuild
the rule.

**Q1 (`docs/contracts/bridge_protocol.md:54-73`): NO — three terms do unpaid
work.**

- **`(S2)` at `:71` and `(S1, shape test)` at `:72`.** These labels are defined
  only in `docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md`,
  and **no installed home cites that path**: not §1 (the block carries no
  citation at all), not the §10 inventory row at `:823` ("the T26 process-rules
  ruling is the record" — no path), not the M0 line at
  `docs/agent_playbook.md:60` ("(process-rules ruling 2026-09-02)" — no path).
  A brief-writer reading the contract hits two bare tokens with no referent
  anywhere in the repository's search path. This is the exact first-use failure
  Ed's standard names.
- **"biting assertion" (`:64`).** The parenthetical `(test method file:line)`
  gives the cell's FORMAT, never the meaning of *biting*. The whole rule lives
  in that adjective — the assertion must actually fail when the clause is
  violated — and it is recoverable only by inferring backwards from the third
  cell. One clause ("biting assertion — a test method that FAILS under the
  counterfactual in the next cell, `file:line`") would close it.
- **"dated ≥ 2026-09-03" (`:72`).** Dated *how*? The installed test resolves it
  as the dated **directory component** (`_dated_process_trace_files`,
  `tests/test_docs_freshness.py:105-119`), but the contract text does not say
  so. Contrast the item-4 addendum at `COLD-GATE-RULING.md:318-320`, which
  spells out "whose dated directory component (`YYYY-MM-DD` prefix, any
  depth)". Two rules installed in the same PR, one replicable and one not.
- Fourth, lower-grade: the `NOT PINNED: <reason>` escape at `:66` is attached to
  a list of three cells with no statement of its scope. The test resolves it as
  "first cell of the row begins `NOT PINNED:` → the whole row is skipped"
  (`tests/test_docs_freshness.py:472-474`). Not derivable from the text.

Also: `bridge_protocol.md:71` is a ~150-column line in a file wrapped at ~78.
The rewrap test (`test_bridge_protocol_clause_map_s2_rewrap_passes`) exists
precisely so this sentence can be wrapped; it was not.

## 3. `## Executed evidence` — does the test model B1's citation, and is the accepted limitation bounded?

**Citation model: matches B1, with one deliberate narrowing and one small
over-acceptance.**

- Regex `([A-Za-z0-9_./-]+\.(?:py|sh|json|toml|ya?ml)):\d+`
  (`tests/test_docs_freshness.py:150-151`) is B1's, character for character;
  `.md:N` cannot match, as ruled.
- Narrowing (Sol 230 F1, correct): `:152-157` additionally rejects a leading `/`
  and any `..` component. B1's own character class admits `/Users/…/x.py:1`;
  refusing it is faithful to "exists at HEAD" and is mutation-tested at
  `:824-846`.
- Fenced branch: `:158-176` requires, inside one fence, ≥1 line matching
  `^\$ .+` and ≥1 line matching the exit/rc pattern at a different offset. Since
  a `$ `-prefixed line can never match `^\s*(?:exit|…)`, the offset test reduces
  to "both present", which is exactly B1's "a different line". `$ echo exit` is
  refused (asserted at `:809-814`).
- Over-acceptance (NIT 7): the `^## Executed evidence$` heading match at
  `:139-143` is not fence-aware, so a file that quotes the heading inside a code
  fence opens a "section". Harmless today — the section still has to satisfy one
  of the two branches — but it is a divergence from a reader's model of B1.
- Selector: verified by census — the union today is exactly
  `2026-09-02-coldgate-dx-t26a/…` and `2026-09-02-process-rules/…`; the
  exemption target `2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
  exists and is the only file it removes. Faithful.

**Is the accepted limitation (file 13: worktree-based, not HEAD-based) correctly
bounded? YES.** I looked for a non-operator path to CI green on a citation that
exists in the worktree but not at HEAD, and found none:

1. Every job in `.github/workflows/ci.yml` is `runs-on: ubuntu-latest`
   (`:18`, `:124`, `:187`, `:292`, `:363`, `:382`) with `actions/checkout@v5`
   and no `clean: false`. GitHub-hosted runners get a fresh workspace per job,
   so no untracked file survives from a previous run. There is no self-hosted
   runner anywhere in `.github/workflows/`.
2. The steps that run before the unit-test step in the `test` job are
   `gen_state.py --check` (documented read-only, `scripts/gen_state.py:10`; the
   only write site, `:785`, is on the non-`--check` path),
   `verify_receipt_histsem.py` (no `write_text` / `open(...,"w")` / `extractall`
   / `mkdir` anywhere in the file), and `compileall -q joulewise tests`, which
   writes only `__pycache__/*.pyc` — an extension outside the citation
   allowlist. `apt-get install zsh` writes outside the repo.
3. No test in `tests/` writes into the repository tree (grep for
   `write_text|open(...,"w")|mkdir` against `ROOT /` / `REPO_ROOT /` returns
   nothing); every fixture uses `tempfile.TemporaryDirectory`, which lands under
   `TMPDIR`, outside `ROOT`.
4. On `pull_request`, checkout takes the merge ref, so a file deleted on base
   but cited in the ruling is *absent*, i.e. fail-closed — not a false green.

So the residual really is a local-run-only weakening, exactly as file 13 states.
The disposition is sound and I would not reopen it.

## 4. Kernel and TASK_QUEUE

**B2 dependency object — exact match to the ruling.** `state_kernel.json:4492-4499`
on `T26-RULING-INSTALL-01`: `kind: decision`, `target: D-170`, `strength: hard`,
`scope: "close"`, `state: pending`, `evidence: null`, `required: "the four T26
verdict mechanisms are installed and each is proven by a regression that fails
when the ruled value is absent"` — the ruling's dictated object, including the
`finish` → `close` correction (`DEP_SCOPES`, `gen_state.py:63`). The gated-task
half is at `state_kernel.json:5387-5395` on `V5-TRANSACTION-01`
(`hard`/`start`/`pending`), so B2's limbs 2 and 3 are satisfied by different
tasks, as ruled. `gen_state.py --check` exits 0.

**D-110 reconcile row — present with the ruled id and scope**
(`state_kernel.json:1151-1188`), fenced to the B3 ruling, and the floor guard is
asserted in the test (`test_terminal_decisions_carry_no_pending_dependency`,
`assertLess(110, DECISION_RULE_FLOOR)`). One deviation: the ruling says the
disposition is "Ed's call, batched" (`MAGISTRATE-RULING-coldgate-dx-t26a.md`
§B3); the row is `"lane": "agent"` (`:1182`) with acceptance "an explicit
magistrate **or Ed** disposition". See NIT 8 — arguable both ways.

**TASK_QUEUE.md — nothing beyond the kernel.** The whole-branch diff moves
exactly 6 lines in each of the two generated renderings (12 total): `+E8`,
`+E10`, `-/+Q4`, `+A17`, `+A20`, mirrored at `:585-618` and `:707-750`. Each
maps 1:1 to a kernel edit (two Ed rows, the V5 dependency line, the installer
row, the D-110 row); there is no unexplained rendering churn, and
`gen_state.py --check` exit 0 proves the file is the faithful regeneration. The
file-13 claim ("`TASK_QUEUE.md` moved only the two generated A17 renderings")
is about the delta commit `f84be217` alone, and I verified that commit's
TASK_QUEUE diff is exactly the two A17 lines and nothing else.

**Unruled addition worth naming:** `scripts/gen_state.py:189-218` now requires a
*satisfied* `kind: decision` dependency's `evidence.path` to match
`tests/[A-Za-z0-9_/]+\.py` and its `evidence.label` to name a `def test_…`
defined in that file. This is not in any cold-gate text; it is the magistrate's
bench cure of Opus 210 F3, dictated at `07-fix-round-1-brief.md:128-139`.
Defensible and well-tested — but it is now a hard constraint on how *every*
future ruling closes, and it is documented nowhere a row-writer reads (NIT 5).

## 5. Merge-ability — conflict surfaces visible from this diff

This branch merges first. `feat/2026-09-02-dx-registry`,
`feat/2026-09-02-t26-gateledger` and `feat/2026-09-02-t26-liveness` touch
**none** of `state_kernel.json`, `TASK_QUEUE.md`, `docs/decision_log.md`,
`tests/test_docs_freshness.py`, `scripts/gen_state.py` or `RUN_STATE.md`
(verified by `git diff --name-only main...<branch>`), so the kernel/queue
collision I was asked to look for does not exist today. Three real surfaces
remain:

1. **Semantic, not textual — the pinned ruling census.**
   `tests/test_docs_freshness.py:628-637` asserts the selected set *equals* a
   hard-coded two-path list. `feat/2026-09-02-t26-gateledger` adds
   `docs/process_traces/2026-09-02-t26-item2/16-MAGISTRATE-RULING-gateledger-splitter.md`,
   whose dated directory `2026-09-02-t26-item2` fullmatches `DATED_DIRECTORY`
   and is ≥ `2026-08-29`. Probe (below) confirms the selector returns three
   paths and the `assertEqual` fails. That lane's CI goes red the moment this
   PR lands, for a file that *does* carry valid executed evidence
   (`$ gh api …` + `exit 0`). SHOULD-FIX 2.
2. **Same file, two lanes:**
   `docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md`
   is the one path both this branch and `feat/2026-09-02-t26-liveness` modify.
   Git will merge them cleanly (this branch inserts after old line 84; liveness
   rewrites old lines 79-80 and appends at EOF — four unchanged lines apart),
   but the *content* collides: after the wave the file carries this branch's
   `**Horizon — AMENDED by cold gate 2026-08-28 (T26 item 3):**` paragraph AND
   liveness's inline `[STRUCK 2026-09-02 …]` marker AND liveness's end-of-file
   dated addendum — three notices of one strike, in two different algebraic
   formulations (`valid_until − 21_600_000_000_000 − r1_batch_finished` here vs
   `validity_origin − r1_batch_finished` there). Equivalent, but a reader must
   derive that. NIT 4.
3. **The D-170 close is a four-part transaction nothing documents.** When the
   last sibling lands, moving `D-170` to `adopted` requires, in one commit:
   both pending `kind: decision` deps on D-170 flipped to `satisfied`
   (`T26-RULING-INSTALL-01` `scope: close` and `V5-TRANSACTION-01`
   `scope: start`) — otherwise
   `test_terminal_decisions_carry_no_pending_dependency` fails — AND each of
   those two evidence pointers must be a `tests/*.py` path whose label names a
   real `def test_…` (`gen_state.py:189-218`). That sequence is written in no
   single place; `T26-RULING-INSTALL-01.acceptance.evidence[4]` names only "the
   single D-170 dependency on this row". NIT 6.

## 6. What I would not merge as-is

Nothing here is a blocker: the branch is green, the B2 object is exact, the
ruled text is quoted faithfully, and the one accepted limitation is correctly
bounded. Five items I would fix before the merge wave, cheapest first:
SHOULD-FIX 4 (a wrong count in a comment), 2 (the census pin that reds the
sibling lane), 5 (a citation that points at superseded text), 3 (a shape check
that refuses a compliant map), 1 (the dropped S9 clause).

---

## Findings

### SHOULD-FIX 1 — item 1's S9 registration clause is dropped with no record

`COLD-GATE-RULING.md:82-84` rules that "the S9 SHORTLIST items marked 'gates the
mint' or 'gates windows' are registered under it **in the ruling's implementation
commit**". This branch *is* that commit for item 1. The seven rows
(S9-01b/02/03/04/05/06/12, enumerated in `2026-09-02-coldgate-dx-t26a/00-PACKET.md:120-125`)
are absent from `state_kernel.json`; luna 209 raised it as a BLOCKER
(`04-luna-209-contract-refute.md:24-26,116`); the packet answered "the
magistrate will register them at the bench"; §B4 of the ruling confirmed they
"register at the bench with the hard/start/pending dep". They did not. Worse,
D-170's item-1 paragraph (`decision_log.md:10489-10491`) keeps only the negative
half of the ruled sentence — "not a retrospective registration of all 460
clauses" — and omits the affirmative carve-in, so a reader of D-170 concludes no
retrospective registration is owed at all. Contrast the *other* deferrals in the
same entry, which are recorded explicitly (`:10540-10544`).

**Counterfactual:** merge as-is and there is no kernel row, no test, no queue
item and no decision-log sentence anywhere that names the seven S9
registrations; all seven target decisions are below `DECISION_RULE_FLOOR = 170`
(`tests/test_docs_freshness.py:32`), so no installed test will ever ask for
them. The clause becomes decided-and-not-done — the precise failure
`T26-RULING-INSTALL-01` was minted to end. Fix: either register them at the
bench in this commit, or add one sentence to D-170 recording the deferral and a
kernel row carrying it, the way item 4's charter-v3 deferral is carried.

### SHOULD-FIX 2 — the pinned two-path census will red-CI the gateledger lane

`tests/test_docs_freshness.py:628-637` asserts the selected set *equals* a
literal two-element list. B1 ruled only that "the selected set must be
non-empty" (`COLD-GATE-RULING.md:325`); pinning the exact census is more than
was ruled, and it couples this test to every future ruling-custody PR.

**Counterfactual (executed, below):** with
`docs/process_traces/2026-09-02-t26-item2/16-MAGISTRATE-RULING-gateledger-splitter.md`
present — it is on `feat/2026-09-02-t26-gateledger` today — the selector returns
three paths and `assertEqual` fails, even though that ruling carries a valid
`## Executed evidence` section (`$ gh api …` / `exit 0`). Replace the equality
with `assertIn` on the two known paths plus `assertTrue(selected)` (the ruled
non-emptiness), or make the pin a `>=`-shaped census.

### SHOULD-FIX 3 — the clause-map row check refuses a compliant four-column map

`_assert_clause_map` accepts any header that *contains* the three required names
(`required_cells.issubset(...)`, `tests/test_docs_freshness.py:459-462`) and a
divider of any arity, then demands each body row have **exactly** three cells
(`:475-477`). The two halves disagree. And the ruled text itself asks each row to
carry a fourth thing — "each row quoting the phrase with ruling `file:line`"
(`bridge_protocol.md:61-62`) — before saying the returned map has "three cells
per row" (`:63`).

**Counterfactual (executed, below):** a map whose columns are
`clause (ruling file:line) | production site | biting assertion | counterfactual`
passes the header and divider assertions and fails every body row with
`4 != 3`. The first custodied `*-impl.md` after 2026-09-03 written by an author
who takes `:61-62` literally is refused. Fix: assert `>= 3` cells with the three
required ones located by header index, or state in the contract that the quote
column is the brief's, not the report's.

### SHOULD-FIX 4 — wrong arithmetic in the kernel-census comment

`tests/test_gen_state.py:607` now reads
`# 116 - 1 = 115; 2026-09-02 T26 install wave: 116 + 3 = 119.` while the
assertion two lines down is `self.assertEqual(len(self.tasks), 120)` (`:609`).
Four rows were added, not three (`T26-RULING-INSTALL-01`,
`D110-MINT-DEP-RECONCILE-01`, `ED-BRANCH-PROTECTION-E1-01`,
`ED-D118-NA-TIER-E2-01`, `:88-96`); the `+3` matches the prose comment at
`:88-92`, which names only the installer and the two Ed rows and forgets the
D-110 row added later at the fix bench.

**Counterfactual:** the next agent to change the task count trusts the running
arithmetic, computes `119 ± n`, and lands a red assertion — this comment chain
is the only census trail in the file, and it now disagrees with the number it
exists to explain. One-line fix: `115 + 1 (installer) + 2 (Ed rows) + 1 (D-110
reconcile) = … = 120` (and, while there, reconcile the pre-existing `115` vs
`116` drift inherited from main).

### SHOULD-FIX 5 — D-170's item-4 citation points into superseded text

`decision_log.md:10529` cites `COLD-GATE-RULING.md:270-282` for item 4. The
quoted rule body is `:269-279`; `:281` begins **Enforcement (mechanical, shape
not truth)** — the heading-triggered paragraph the dx cold gate B1 *replaced*
(the replacement is the dated addendum at `COLD-GATE-RULING.md:317-331`). The
superseded paragraph carries no forward marker of its own (custody forbids
editing in place), and D-170 never mentions the addendum at all.

**Counterfactual:** a future brief-writer opens D-170 item 4, follows
`:270-282`, lands on `:281-291`, and implements the `## Rulings` / `## RULED` /
`## Addendum` heading trigger that fires on zero files — the exact defect B1 was
convened to cure. Fix: cite `:269-279`, and add half a sentence to D-170: "the
enforcement machinery is replaced by the dated addendum at `:317-331` (dx cold
gate B1)".

### NIT 1 — `(S1)` / `(S2)` are unresolvable from any installed home

`bridge_protocol.md:71-73` uses the labels; §1 carries no citation, the §10 row
at `:823` says "the T26 process-rules ruling is the record" with no path, and
`agent_playbook.md:60` says "(process-rules ruling 2026-09-02)" with no path.
Q2's install does this right (`decision_log.md:10351` ends with the ruling path).
Counterfactual: a brief-writer cannot find what S1 or S2 constrain without
guessing a directory name.

### NIT 2 — "biting assertion" and "dated ≥ 2026-09-03" are unglossed

`bridge_protocol.md:64` and `:72`; the mechanisms live only in
`tests/test_docs_freshness.py:475-483` and `:105-119`. Counterfactual: two
implementers produce two different date semantics (file date vs directory date)
and only one passes CI.

### NIT 3 — the `NOT PINNED:` escape's scope is defined only in the test

`bridge_protocol.md:66` vs `tests/test_docs_freshness.py:472-474` (first cell of
the row, whole row skipped). Counterfactual: an author writes
`| site | NOT PINNED: no test yet | |` and is refused for an empty cell.

### NIT 4 — mid-file insertion into a custodied ruling, and a duplicate strike notice

This branch inserts a new paragraph at line 85 of
`docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md`
rather than appending a dated addendum — the convention the same lane used for
`COLD-GATE-RULING.md:317` and that `feat/2026-09-02-t26-liveness` used for this
very file, and which B1's own text asserts ("custodied files are not edited in
place", `COLD-GATE-RULING.md:321`). Counterfactual: after the liveness lane
merges the file carries three notices of one strike in two formulations (see §5
item 2). Cheap fix: drop this branch's paragraph and let the liveness addendum
be the single record, or move it to an addendum block at EOF.

### NIT 5 — `gen_state.py`'s `tests/*.py` constraint is undocumented

`scripts/gen_state.py:189-218` (from `07-fix-round-1-brief.md:128-139`, not from
any ruling) makes it impossible to satisfy a decision dependency with a
regression that is not a Python method under `tests/`. Neither D-170 nor the
How-To at `decision_log.md:22-30` says so. Counterfactual: an author points at
`scripts/check_gate_ledger.py` self-checks and `gen_state.py --check` refuses
with a rule they could not have read.

### NIT 6 — the D-170 close sequence is written nowhere

See §5 item 3. Counterfactual: the closing commit flips only the installer's
dependency, `test_terminal_decisions_carry_no_pending_dependency` fails on the
`V5-TRANSACTION-01` dep, and the lane discovers the transaction shape in CI.

### NIT 7 — `_has_executed_evidence` heading match is not fence-aware

`tests/test_docs_freshness.py:139-143`. A `## Executed evidence` line quoted
inside a code fence opens a section. Harmless today (the section must still
satisfy a branch); noted as a model divergence from B1.

### NIT 8 — D-110 reconcile row sits in the agent lane against "Ed's call"

`state_kernel.json:1182` `"lane": "agent"`; ruling §B3 says "Ed's call, batched".
Against that, Ed's standing instruction is that the magistrate rules all
non-hardware/non-sudo items, which this is. Flagged so the choice is deliberate
rather than incidental; I would not block on it.

### NIT 9 — an unruled edit to an existing status gloss

`decision_log.md:14` redefines `accepted` from main's "binding until revisited"
to "binding design choice", losing the revisitability semantics, inside a change
whose mandate was to *add* the closed vocabulary (`COLD-GATE-RULING.md:92-94`).

### NIT 10 — item 2's ruled text lives at D-170, not at its named ONE home

`decision_log.md:7830` gives D-118 a pointer; the ruling named D-118's
"Mechanical enforcement" paragraph as the ONE home (`COLD-GATE-RULING.md:155-156`).
Text-once-plus-pointer is the better shape and D-170 declares it at
`:10536-10537`; recorded only so the inversion is not silent.

### Observation (not a finding) — B1's `NEEDS-RULING-` exclusion is asymmetric

The install is faithful: `tests/test_docs_freshness.py:127-131` applies the
exclusion to branch (b) only, exactly as `COLD-GATE-RULING.md:322-324` writes it.
But a live counterexample exists one day outside the cutoff —
`docs/process_traces/2026-08-28-workload-scored-v6/NEEDS-RULING-01-MAGISTRATE-RULING.md`
— so a future dated directory holding a file of that shape would be selected by
branch (a) and required to prove executed evidence of a *question*. That is a
ruling-level gap, not an install defect; it belongs in the next cold gate, not
in this PR.

---

## Executed evidence

All commands run with
`TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmp-opus-a`,
cwd `/Users/edr/code/JouleWise-wt-t26-a` unless stated.

```text
$ git -C /Users/edr/code/JouleWise-wt-t26-a log --oneline -1
10845c14 t26-items-1-4 trace: gauntlet files 01-13 … + MAGISTRATE-NOTES
$ git -C /Users/edr/code/JouleWise log --oneline -1
403998e1 Cold-gate dx ruling: dated addendum — A1 check_figure site is :597 …
exit 0
```

```text
$ git diff main...HEAD --stat | tail -1
 30 files changed, 3546 insertions(+), 11 deletions(-)
exit 0
```

```text
$ python3 -m unittest tests.test_docs_freshness tests.test_gen_state
Ran 65 tests in 1.986s
OK
exit 0
$ python3 scripts/gen_state.py --check
exit 0
```

```text
$ git diff main...HEAD -U0 -- TASK_QUEUE.md | grep -c '^[+-][^+-]'
12          # +E8 +E10 -Q4 +Q4 +A17 +A20, mirrored in both generated renderings
$ git show f84be217 -- TASK_QUEUE.md | grep '^[+-][^+-]'
-| A17 | T26-RULING-INSTALL-01 | … [AGENT] | …
+| A17 | T26-RULING-INSTALL-01 | … [AGENT] | …
-| A17 | T26-RULING-INSTALL-01 | … | …
+| A17 | T26-RULING-INSTALL-01 | … | …
exit 0
```

```text
$ for b in dx-registry t26-gateledger t26-liveness; do git diff --name-only main...feat/2026-09-02-$b | grep -E 'state_kernel|TASK_QUEUE|decision_log|test_docs_freshness|gen_state|RUN_STATE' || echo "(none)"; done
(none)
(none)
(none)
$ comm -12 <(git diff --name-only main...HEAD | sort) <(git diff --name-only main...feat/2026-09-02-t26-liveness | sort)
docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md
exit 0
```

Probe A — SHOULD-FIX 2 (selector with the gateledger ruling present):

```text
$ python3 -  # mock ROOT onto a scratch tree holding the two current rulings + 16-MAGISTRATE-RULING-gateledger-splitter.md
SELECTED:
  docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md
  docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md
  docs/process_traces/2026-09-02-t26-item2/16-MAGISTRATE-RULING-gateledger-splitter.md
would the pinned 2-element assertEqual hold? False
exit 0
```

Probe B — SHOULD-FIX 3 (four-column clause map):

```text
$ python3 -  # DocsFreshnessTests._assert_clause_map on a 4-column map
4-column map: FAILS -> 4 != 3 : four-column-map: Clause map body row must have three cells: '| "600 s" COLD-GATE-RULING.md:201 | joulewise/arm_readiness.py:51 | tests/test_x.py:10 | s
exit 0
```

CI-environment checks for §3:

```text
$ grep -n 'runs-on\|actions/checkout\|clean:' .github/workflows/*.yml
… all six jobs: runs-on: ubuntu-latest ; uses: actions/checkout@v5 ; no `clean:` key …
$ grep -n 'extractall\|open(.*"w\|write_text\|mkdir' scripts/verify_receipt_histsem.py
(no output)
$ grep -rn 'REPO_ROOT\s*/\|ROOT /' tests/*.py | grep -E 'write_text|open\(.*"w"|mkdir'
(no output)
$ grep -n 'def main\|--check\|write_text\|\.write(' scripts/gen_state.py
10:  python3 scripts/gen_state.py --check         read-only drift/validity check
785:            fh.write(data)
807:def main(argv=None) -> int:
809:    parser.add_argument("--check", action="store_true")
822:            sys.stdout.write(fragment)
exit 0
```

Census and citation checks:

```text
$ find docs/process_traces -name '*MAGISTRATE-RULING*.md' | sort | tail -3
docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md
docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md
docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md
$ grep -n 'Addendum 2026-09-02 — item 4' docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md
317:## Addendum 2026-09-02 — item 4 enforcement (dx cold gate B1)
$ wc -l < docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md
332
$ grep -n '"S9-' docs/process/state_kernel.json | wc -l
0            # no S9 SHORTLIST rows registered
$ grep -n '116 + 3\|assertEqual(len(self.tasks)' tests/test_gen_state.py
607:        # 116 - 1 = 115; 2026-09-02 T26 install wave: 116 + 3 = 119.
609:        self.assertEqual(len(self.tasks), 120)
exit 0
```

VERDICT: SHOULD-FIX 5
