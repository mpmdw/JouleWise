ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: ["tests/test_docs_freshness.py", "scripts/gen_state.py", "tests/test_gen_state.py", "docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md"]
GENRE: implementation
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FIX round 1 — T26 items 1 + 4 install (branch feat/2026-09-02-t26-install @ 2d24ef70)

LINKED WORKTREE `/Users/edr/code/JouleWise-wt-t26-a`. Do NOT commit/rebase;
never canonical `unittest discover`; the magistrate commits.
`docs/process/state_kernel.json`, `docs/decision_log.md`, `TASK_QUEUE.md`,
`RUN_STATE.md` are OUT of scope — read them; every kernel/decision-log edit
this round needs is written as exact proposed text/JSON to
`$TMPDIR/bench-<name>.{md,json}` and named in the report; the magistrate
applies at the bench (`gen_state.py` → `--check` → `tests.test_gen_state`).
Tests: `python3 -m unittest tests.test_docs_freshness tests.test_gen_state`.
Python: `python3` on PATH in this worktree.

AUTHORITY (read first, in this order; 1–2 live on main, NOT on this branch —
read them read-only at the absolute paths given):
1. `/Users/edr/code/JouleWise/docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md`
   §B1, §B2, §B3, §B4 — DICTATED shapes (B1's enforcement text is quoted
   verbatim below; apply it byte-exact where it says "operative text").
2. `/Users/edr/code/JouleWise/docs/process_traces/2026-09-02-coldgate-dx-t26a/210-opus-t26a-exec.md`
   (execution-lens refuter; F3/F5/F5b/F6/F7/F8 dictated below) and
   `.../209-luna-t26a-contract.md` (F2/F3 dictated below).
3. On this branch: `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
   (the T26 ruling; its `Enforcement (mechanical, shape not truth)` paragraph
   at `:281-290` is what B1 replaces — BY DATED ADDENDUM at the end of the
   file, never in place), `tests/test_docs_freshness.py` (item-1/4 tests at
   `:90-134`, `:237-311`, `:313-341`), `scripts/gen_state.py`
   (`_check_pointer:131-165`, `_check_dependency:167-191`, `DEP_SCOPES:63`).

## Dictated closures

F-1 (ruling B1 — item-4 enforcement fired on zero files). Replace the
heading trigger: the FILENAME is the trigger. Two selectors, both scanning
for a dated `YYYY-MM-DD(-…)?` directory component at ANY depth under
`docs/process_traces/` (Opus F8 — today only `parts[0]` is date-tested;
`docs/process_traces/archive/2026-09-09-probe/...` must be selected):
(a) `**/*MAGISTRATE-RULING*.md` with dated component ≥ `2026-08-29`, except
the closed exemption list
`{"2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md"}` (relative
to the trace root; a module constant with the reason in a comment);
(b) `**/*RULING*.md` with dated component ≥ `2026-09-03`, excluding basenames
starting `NEEDS-RULING-`. The union must be NON-EMPTY (assert; today it is
exactly `2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md` — say
so in the test's comment, replacing the stale "Install-time scan" comment).
Every selected file must contain a `## Executed evidence` heading whose
section (to the next `^## `) satisfies ONE of:
  (1) a fenced block containing a line matching `^\$ .+` AND a DIFFERENT
      line matching `^\s*(?:exit|EXIT|rc|exit code|exit status)[\s=:]+\d+\s*$`;
  (2) a citation `[A-Za-z0-9_./-]+\.(?:py|sh|json|toml|ya?ml):\d+` whose
      path (the part before `:`) exists at HEAD (`ROOT / path` is a file).
`.md:N` satisfies nothing (Opus F5). Keep `_has_executed_evidence` as the
one predicate (signature may gain `root`).
Mutations, each as a test over a scratch copy or a literal string, not by
editing the tracked ruling: M7 the 09-02 ruling text with its
`## Executed evidence` heading deleted → fails; M8 its `exit 0` line AND its
`.md` citation dropped → fails; a fence whose only content is `$ echo exit`
→ fails; a section citing only `docs/contracts/bridge_protocol.md:48` →
fails; a section citing `scripts/gen_state.py:63` → passes; a section citing
`scripts/does_not_exist.py:1` → fails; positive control: a scratch tree
`docs/process_traces/2026-09-09-probe/X-RULING-probe.md` with no evidence
section → selected by (b) and fails; the same file under
`docs/process_traces/archive/2026-09-09-probe/` → also selected (F8);
`docs/process_traces/2026-09-09-probe/NEEDS-RULING-x.md` → not selected.
Operative addendum text for `COLD-GATE-RULING.md` — APPEND a section
`## Addendum 2026-09-02 — item 4 enforcement (dx cold gate B1)` whose body
is exactly the block quote from ruling §B1 ("Selected files: (a) every …
satisfies nothing.") plus one sentence: "Replaces the Enforcement paragraph
above (`:281-290` at 2d24ef70), which fired on zero files at install; the
rule body is unchanged." Nothing above the addendum is edited.

F-2 (ruling B2 — item-1 test has four limbs; luna F2 / Opus F2 / Opus F5b).
Module constant `DECISION_RULE_FLOOR = 170`. Rewrite
`test_open_decisions_name_an_installing_kernel_task`: for each
`open (installs via X)` row with D-number ≥ `DECISION_RULE_FLOOR`:
(1) `X in tasks`; (2) task X carries ≥ 1 `kind: decision` dep targeting the
D-id (ANY scope/strength — the installer's dep is `close`); (3) SOME task
carries a `kind: decision` dep on the D-id with `strength: hard`,
`scope: start`, `state: pending`; (4) the number of rows parsed by
`_decision_index_rows` equals the number of `^\| D-\d{3}[a-z]? \|` lines in
the index — a malformed status cell FAILS naming the row, never skips (Opus
F5b: `| decided|` dropped D-170 silently). Drop the `decision_number < 170
and installing is None: continue` legacy skip in favour of the floor
applied once. Counterfactuals as tests over a scratch kernel/index string:
M4 `installs via ARM-PACKET-01` → fails at limb 1 (and say what limb 2 does
if ARM-PACKET-01 exists but carries no dep); a kernel where only
V5-TRANSACTION-01 carries the dep → fails at limb 2; a kernel where the
installer carries `close` but no task carries `start` → fails at limb 3;
M13 `| decided|` → fails at limb 4.
NOTE: at 2d24ef70 the kernel has `T26-RULING-INSTALL-01.dependencies: []`,
so limb 2 FAILS on the live kernel until the bench applies B2. Write the
exact dependency object (ruling §B2) to `$TMPDIR/bench-b2-dep.json` and
report the limb-2 failure as EXPECTED-UNTIL-BENCH with the test name; do
not weaken the test to pass today.

F-3 (ruling B3 — terminal rows with a pending decision dep). New test
`test_terminal_decisions_carry_no_pending_dependency`: for every index row
with D-number ≥ `DECISION_RULE_FLOOR`, the leading status token must be in
`{"open", "proposed"} ∪ TERMINAL`, `TERMINAL = {"adopted", "accepted",
"ratified", "recorded", "executed", "adjudicated", "superseded"}` (module
constants; `DECISION_STATUS_TOKENS` at `:29` becomes exactly that union —
assert equality in a test so the two cannot drift); any other token FAILS
naming the row. For a TERMINAL row no task may carry a `kind: decision` dep
targeting it with `state: pending`; the message names the status and the
task. Controls (scratch strings): unmodified kernel + index passes; M6c
(D-170 → `adopted`, dep pending) fails; `D-171 adopted` with no dep passes;
`D-171 proposed` with a pending dep passes; D-110 (`accepted`, pending dep
on MINT-GENERALIZE-01) is BELOW the floor and must not fire — assert that
explicitly with a comment citing kernel row `D110-MINT-DEP-RECONCILE-01`
(bench registers it).

F-4 (Opus 207b B1 carry-over — dangling `D-\d{3}` references). New test
`test_decision_references_resolve`: every `D-\d{3}[a-z]?` token in
`docs/**/*.md` (excluding `docs/process_traces/**` and `docs/decision_log.md`
itself), `.github/**`, `README.md`, `TASK_QUEUE.md`, `RUN_STATE.md`,
`docs/process/state_kernel.json` must be a body id in `docs/decision_log.md`
(`^## (D-\d{3}[a-z]?):`). Run it; if it fails today on real dangling
references, LIST them in the report with file:line and do NOT add an
allowlist — the magistrate decides; keep the test in place failing (say so
under acceptance as EXPECTED-UNTIL-BENCH) unless the failures are
prose-only mentions of future ids in the T26 ruling addendum you wrote
(then cite the decision log entry instead).

F-5 (Opus 210 F3 — "satisfied" accepts any pointer). In
`scripts/gen_state.py::_check_dependency`, for `kind == "decision"` and
`state == "satisfied"`: `evidence.path` must match `^tests/[A-Za-z0-9_/]+\.py$`
and `evidence.label` must contain a `test_[a-z0-9_]+` token that occurs in
that file as `def test_…` (open the file; this is the "regression that
fails when the ruled value is absent" being named, not merely a pointer
that resolves). Refusal messages name the dep and the reason. Tests in
`tests/test_gen_state.py`: M6b (`README.md` / "placeholder pointer") →
refused; `tests/test_docs_freshness.py` + label naming
`test_open_decisions_name_an_installing_kernel_task` → accepted; a label
naming a test that does not exist in the file → refused. Do not touch any
other dep kind.

F-6 (Opus F6). `test_bridge_protocol_clause_map_pins_s1_and_s2:343-348`:
normalise whitespace (`re.sub(r"\s+", " ", …)` on both sides) before
`assertIn`, so an 80-column re-wrap of `bridge_protocol.md:71` cannot fire
it; keep the deletion-bite (test: text with the sentence removed → fails).

F-7 (Opus F7). `test_custodied_impl_reports_carry_clause_map`: wrap the
per-file assertions in `with self.subTest(path=…)` so one bad file does not
hide the rest; the `NOT PINNED:` escape is applied PER ROW (a row whose
first cell starts `NOT PINNED:` is skipped; every other body row must have
the three cells non-empty), not per file. Tests over literal strings: a
table with one `NOT PINNED: reason` row and one complete row → passes; a
body row `| a | b | |` (empty counterfactual) → fails; header-only → fails.

F-8 (luna 209 F3 — citation extensions). Covered by F-1's regex
(`ya?ml` added, `md` removed). State it in the clause map.

## Mutation check (report each: KILLED by <test> / SURVIVED)

M7, M8, `$ echo exit`, `.md:48`-only, positive control (both depths),
`NEEDS-RULING-` exclusion → per F-1.
M4, only-V5 dep, no-`start` dep, M13 → per F-2.
M6c, unknown token `decided` on a ≥170 row → per F-3.
Dangling `D-999` in a scratch `.github/x.md` → per F-4.
M6b → per F-5.
Re-wrap of the S2 sentence → per F-6 (must PASS after; FAIL before — show both).

## ACCEPTANCE

- `python3 -m unittest tests.test_docs_freshness tests.test_gen_state` tail,
  with the EXPECTED-UNTIL-BENCH failures (F-2 limb 2; possibly F-4)
  enumerated by test name — nothing else may fail.
- `python3 scripts/gen_state.py --check; echo EXIT=$?` (expect 0 — you did
  not edit the kernel).
- `git status --porcelain` shows only in-scope files; `git diff --stat`.
- `$TMPDIR/bench-b2-dep.json` (the B2 dependency object, exact) and
  `$TMPDIR/bench-kernel-rows.md`: proposed rows `D110-MINT-DEP-RECONCILE-01`
  and a correction to `T26-RULING-INSTALL-01.acceptance.evidence[1]`
  (ruling B1 last paragraph: "mutation-killed" was FALSE at 2d24ef70 — the
  corrected sentence names the mutations that now kill).
- Same-signature statement: first fix round on this landing; classify each
  closure (selector defect / test-limb gap / doc-shape) and state that no
  ruled text was changed except by the F-1 addendum.
- `## Clause map`: one row per closure F-1…F-8 — production `file:line`,
  biting test `file:line`, counterfactual.
