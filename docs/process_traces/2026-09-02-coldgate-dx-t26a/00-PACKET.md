# Cold-gate packet — two subjects, 2026-09-02 (session 540125d5)

Mandatory triggers (CLAUDE.local.md rule 11 / charter §3), both from refuter
findings on in-flight branches:

- Subject A (branch `feat/2026-09-02-dx-registry` @ `3f1677b7`, the round-7
  paper-artifact fence): a SECOND fix round on the same defect class
  (type-laxness in scalar comparison — round 1 cured `int` truncation;
  the `Decimal` and boolean paths are uncured), plus a scope question.
- Subject B (branch `feat/2026-09-02-t26-install` @ `2d24ef70`, the install of
  T26 cold-gate items 1 + 4): the ruled enforcement text of item 4 cannot
  fire on any post-cutoff file, so curing it REINTERPRETS a cold-gate verdict;
  the item-1 enforcement clause admits three readings and the seat took the
  weakest; one refuter proposes a NEW rule (a non-`open` row with a pending
  decision dependency is a contradiction).

The magistrate has NOT amended anything. Read-only. Repo worktrees:
`/Users/edr/code/JouleWise-wt-dx` (subject A) and
`/Users/edr/code/JouleWise-wt-t26-a2` (subject B, detached @ 2d24ef70). Write
NOTHING under either; TMPDIR = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Python: `/Users/edr/code/JouleWise/.venv/bin/python`. Do NOT launch any
codex/claude process. Do NOT run canonical `unittest discover`. NOTE: another
seat (Sol 216) is editing `/Users/edr/code/JouleWise-wt-dx` concurrently on
files OTHER than the ones you are asked about — if `git status --short` there
is non-empty, read the committed bytes with `git show 3f1677b7:<path>`.

Charter: `docs/process/coldgate_charter.md` — expected sha256
`099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` (verify with
`shasum -a 256`; if it differs, say so in your disclosure and stop). Read
§3–§5 and §8 before anything else. Charter §4 read set: ONLY this packet and
the primary evidence cited below — no narrative process/state docs
(README.md, RUN_STATE.md, TASK_QUEUE.md, docs/orchestration.md,
docs/agent_playbook.md), no CLAUDE*.md doctrine, no memory files. Disclose any
contamination (anything you read outside the set, or prior context).

## Packet (read all, in this order)

1. This file, §Questions and §Facts.
2. Subject A evidence, in this directory (`coldgate-dx/`):
   `189-luna-refute.md` (round-1 refute), `191-fix-brief.md` (the magistrate's
   round-1 fix contract), `191-sol-fix-report.md`, `198-terra-delta.md`
   (delta re-audit of round 1), `207-opus-counter-review.md` (the
   counter-review that raised S1/S2), `diff-fence-main-to-3f1677b7.patch`.
   Primary code: `scripts/check_paper_round7_artifacts.py` at `3f1677b7`
   (`_comparison` :155-160, `_decimal` :369-370, `_exact_int` :385-388,
   `check_gates` :493-506, `check_skeleton_literals` :581-604);
   `tests/test_paper_round7_artifacts.py`; `docs/paper/round7/fill-checklist.md`
   :20-26 and :250-266; `docs/paper/draft-v2-skeleton.md` (0 `[FILL:DX-` markers).
3. Subject B evidence: `../out/209-luna-t26a-contract.md` (contract lens),
   `../out/210-opus-t26a-exec.md` (execution lens, M1–M15). Primary text:
   `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
   item 1 (`:45-110`) and item 4 (`:255-298`); `tests/test_docs_freshness.py`
   :99-134 (helpers), :260-311 (the two item-1/item-4 tests); the installing
   commits `git log --oneline 6075389a..2d24ef70` in `-a2`;
   `docs/process/state_kernel.json` tasks `T26-RULING-INSTALL-01`,
   `V5-TRANSACTION-01`, `MINT-GENERALIZE-01`; `scripts/gen_state.py:131-191,
   357-366`; `docs/decision_log.md` D-170 entry (`grep -n '^### D-170'`).

## Questions

**A1 (rule-11 second round, same defect).** Is Opus 207 S1 (`_decimal` accepts
`str`; `_comparison` `==` lets `True` match `1`/`1.0` in `check_gates`) the SAME
defect class as luna 189's `int()` truncation that round 1 cured at
`_exact_int`? Whatever the classification, RULE the cure shape: (a) structural
— one typed field resolver (`int` / `Decimal` / `bool` / `str`, refusing every
cross-type coercion including `str→Decimal`, `bool→int`, `int→bool`,
`float→Decimal`) through which EVERY renderer and `check_gates` reads
artifact values, with one table-driven test over the four kinds × the
rejected coercions; or (b) site-by-site patches at `:370` and `:155`; or (c)
something better. State the biting counterfactual per kind. Note the threat
model in force (D-161): the adversary is not the operator; the fence exists
against RE-ISSUED artifacts and honest producer drift, not forgery.

**A2 (scope).** Opus 207 S2: the skeleton literal check emits ZERO comparisons
today (no markers placed) and nothing detects a DX value typed as bare prose.
Rule whether (i) a placement census ("each of the 16 non-identity DX rows is
placed as `[FILL:DX-nnn]` at least once, gated on a flag") and (ii) a scan for
each row's rendered literal appearing outside a marker belong in THIS PR, or in
a kernel row at the fill stage (the successor draft is not yet being filled);
and the acceptance shape for whichever you rule.

**B1 (reinterpretation of a verdict).** Item 4's ruled enforcement (`:281-290`)
triggers on `## Rulings` / `## RULED` / `## Addendum`. Bench census (Facts F3):
those headings appear in 11 of 20 PRE-cutoff files and in 0 of 2 POST-cutoff
files, whose headings are `## Rulings on the …` (no — see F3 exactly) /
`## Ruled text (operative…)` / `## Disposition`. So the test as ruled asserts
on zero files and can never fire for a new ruling; the seat installed it
verbatim and the kernel acceptance row claims "mutation-killed" (false: Opus
M7/M8 survive). Rule the amendment: (i) drop the heading trigger — every
`*MAGISTRATE-RULING*.md` (and `*-RULING-*.md`, e.g. `171a-RULING-decode-identity.md`,
which the ruled glob also misses) under a dated directory ≥ 2026-08-29 must
carry `## Executed evidence`; (ii) widen the vocabulary (case-insensitive
`## Ruled…`, `## Rulings`, `## Disposition`, `## Addendum…`); or (iii) keep as
ruled and record the magistrate's dissent. Also rule luna F3 / Opus F5: the
`file:line` branch accepts any `name.ext:\d+` anywhere (a home-anchor pointer
satisfies it) and the fenced branch accepts `$ echo exit` on one line —
tighten (how?) or accept as the shape-not-truth residual the ruling already
named (`:288-290`).

**B2 (three readings).** Item 1 rule body (`:72-75`): "that kernel task gains a
dependency `{kind: decision, target: D-NNN, strength: hard, scope: start,
state: pending…}` on every task the clause gates"; enforcement (ii) (`:94-97`):
"that id present in `state_kernel.json` `tasks` AND that task carrying a
`kind: decision` dependency targeting the row's D-id". Facts F4–F5: the seat put
the D-170 dependency on the GATED task `V5-TRANSACTION-01`; the installing task
`T26-RULING-INSTALL-01` has `dependencies: []`; the test checks the named task
EXISTS and that ANY task carries a decision dep on the D-id. The literal
reading — the installing task itself carries a `pending` hard `start`
dependency — makes the installing task unselectable under invariant 3
(`gen_state.py:357-366`), i.e. nothing could ever install the ruling. Rule the
placement (installing task / gated tasks / both with `scope: finish` on the
installer?) and the exact test assertion set, so that two unrelated tasks can
no longer satisfy the two assertions (Opus M4 survived).

**B3 (proposed new rule — Opus F4).** A non-`open` index row (e.g. `adopted`)
whose D-id still has a `pending` `kind: decision` dependency anywhere in the
kernel passes today (Opus M6c). Adopt, amend, or reject a test refusing it.

**B4 (install, not ruling — answer only if it changes B2).** Luna F1: the S9
SHORTLIST rows marked "gates the mint" (S9-01b, 02, 03, 04, 05) / "gates
windows" (S9-06, 12) were ruled registered "in the ruling's implementation
commit" and are absent. The magistrate will register them at the bench (the
kernel file is in no seat's scope). Say only whether any of them changes your
B2 placement answer.

Deliverable: a sealed ruling per question (A1, A2, B1, B2, B3; B4 optional),
each with verdict (ADOPT / AMEND / REJECT / UNRULED with reason), the operative
text or code shape, the biting counterfactual, and what it does NOT decide.
Under charter §8, disclose contamination and the charter digest first.

## Facts (bench-verified by the magistrate 2026-09-02; re-verify any you rely on)

F1. `scripts/check_paper_round7_artifacts.py@3f1677b7`: `_decimal` at :369-370
    `return value if isinstance(value, Decimal) else Decimal(str(value))` —
    accepts `str`; `_comparison` at :155 builds `match = expected == observed`.
    `_exact_int` :385-388 rejects `bool` and non-`int`.
F2. Round 1 (`191-fix-brief.md` F-B) dictated the `_exact_int` cure for counts
    only; terra 198's delta re-audit passed it with NIT-1.
F3. Heading census over `docs/process_traces/*/**/*MAGISTRATE-RULING*.md`
    (22 files; regex `^## (?:Rulings|RULED|Addendum)(?:\s.*)?$`): fires on 11
    pre-cutoff files, 0 of the 2 post-cutoff files
    (`2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`: `## 0. The
    forcing problem`, `## 2. Rulings on the p…`, …;
    `2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md`:
    `## Disposition`, `## Ruled text (operative…)`, `## Installation…`,
    `## Executed evidence`). NB `## 2. Rulings on…` does not match because of
    the numeric prefix. `171a-RULING-decode-identity.md` matches neither glob.
F4. `state_kernel.json`: the only `kind: decision` dependencies are D-110 on
    `MINT-GENERALIZE-01` and D-170 on `V5-TRANSACTION-01`;
    `T26-RULING-INSTALL-01` has `dependencies: []`, status `partial`.
F5. `tests/test_docs_freshness.py:277-294` (at 2d24ef70): asserts the named
    task id is in the kernel (`:277-280`), then collects `dependent_tasks`
    across ALL tasks (`:282-289`) and asserts non-empty (`:291-294`).
F6. Charter digest at both worktrees: `099de884…` (recompute yourself).
F7. `docs/paper/draft-v2-skeleton.md` contains 0 occurrences of `[FILL:DX-`.
