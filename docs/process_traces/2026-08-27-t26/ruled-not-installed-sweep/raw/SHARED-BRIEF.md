# S9 "ruled but never installed" sweep — shared enumeration brief

Repo: `/Users/edr/code/JouleWise` (branch `main`, READ-ONLY for you — do NOT edit
any tracked file, do NOT run git write commands, do NOT create files outside the
one output path your task names).

## Why this sweep exists (the shape you are hunting)

Three times in one session a ruled contract turned out to have **no route or no
check in code**. The canonical case is D-157 (read
`docs/process_traces/2026-08-27-t26/holm-m-consult/04-MAGISTRATE-RULING.md`):
D-139 clause A2 ruled on 2026-08-17 that a Holm family with multiplicity m=2
"enters the gamma prospective manifest's `families` block at the production
freeze". Ten days and eighteen decisions later, the gamma pack generator still
emitted `m=1` with a "contingent on unresolved ratification" note, no `families`
block at all, and the freeze/readiness path never ran the prospective validator —
so the mint would have produced bytes that the *consumption edge* refuses after a
168-hour campaign. The rule existed. The producer never learned it.

Your job: find every other instance of that shape in decisions D-117..D-157.

## Definitions (use these exactly)

**IMPLEMENTATION CLAUSE** — any sentence or clause in a decision that asserts a
value, rule, check, refusal, emission, schema key, threshold, or documentation
change is (or will be) realized in an *artifact*: Python code, a config/pack
file, generated pack bytes, a JSON schema, a runbook/checklist, a script, or a
test. Signal verbs: "enters", "is installed", "the code refuses", "refuses",
"lands as", "the generator emits", "the runbook says", "at the production
freeze", "must", "shall", "gains", "is added", "is stamped", "is recorded",
"regressions:", "the validator requires", "is deleted", "is pinned", "carries",
"is registered in the D-078 registry".

**NOT an implementation clause** (skip these): pure authority/process rulings
with no artifact ("delegated to the magistrate", "Ed signed off", "recorded as
D-1xx", "the magistrate may overrule"), narrative findings, and cost/date
estimates — UNLESS they also specify a mechanical check or a required document.

**Status codes** (assign exactly one per clause):

- **A — INSTALLED AND CHECKED AT THE PRODUCER.** The artifact that *writes* the
  bytes/state enforces or emits the ruled thing, and a check refuses the wrong
  value at write time. Evidence: `file:line` of the producer-side code plus, if
  it exists, `file:line` of the test that would fail if removed.
- **B — INSTALLED, NO PRODUCER-SIDE CHECK.** The value or rule exists somewhere
  (a consumer refuses it, a validator function exists, a doc says it) but
  nothing enforces it where the bytes are produced — the D-157 shape. Say
  explicitly WHERE the check is missing (which producer function/script).
  A validator function with **no callers outside its own module and tests** is
  a B, not an A. Check callers with grep before you decide.
- **C — NOT INSTALLED.** No code, config, pack byte, runbook, or test realizes
  the clause. You must show you looked: name the greps/files you checked.
- **D — SUPERSEDED.** A later decision (D-118..D-157 or a tail amendment)
  replaced or vacated this clause. Cite the superseding decision AND its
  `docs/decision_log.md:LINE`.

**transaction_relevant** — `yes` if the clause touches any of: the `_v4` pack
mint, arm/arm-readiness, the measurement window, the consumption edge, or the
claim edge (analysis manifest, finalization, claim-time validation). Otherwise
`no`. When in doubt, say `yes` and explain in one line.

## Method (mandatory — do not shortcut)

1. Read your assigned index rows and tail sections VERBATIM from
   `docs/decision_log.md` at the exact line ranges given (use
   `sed -n 'START,ENDp' docs/decision_log.md`). Do not summarize before
   extracting — extract clauses first, quoting them verbatim.
2. For EACH clause, go find the artifact. Search the real tree, not your memory:
   - code: `joulewise/` (notably `analysis_manifest_v3.py`, `arm_readiness*.py`,
     `analysis_engine/` {`artifact.py`, `multiplicity.py`, `claims.py`,
     `registry.py`}, `identity_pins.py`, `provenance.py`, `validation.py`,
     `schemas.py`, `campaign_provenance.py`, `detection_floor.py`,
     `floor_mint_estimator.py`, `quiet_guard*.py`, `window_duration_margins.py`)
   - scripts: `scripts/` (notably `launch_window.py`, `finalize_analysis_manifest.py`,
     `author_arm_readiness_evidence.py`, `capture_t0_step.py`,
     `generate_arm_readiness.py`, `build_v4_histsem_pinset.py`, `prewindow_check.sh`)
   - pack generators: `configs/campaigns/*/generate_configs.py`
   - runbooks/checklists: `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md`,
     `docs/process/phase2-transaction-runsheet.md`, `docs/phase_2/window_runbook.md`,
     `docs/process/ed-evening-checklist.md`, `docs/process/rehearsal-operator-card.md`,
     `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`
   - tests: `tests/`
3. **Every status needs `file:line` evidence you personally read.** Open the
   file at the line and confirm the line says what you claim. A grep hit alone
   is not evidence; a plausible-sounding filename is not evidence. If you cannot
   verify, write `UNVERIFIED` and say what blocked you — never guess.
4. For anything you mark A or B, check the PRODUCER side specifically: who
   writes these bytes, and does that writer refuse a wrong value? Use
   `grep -rn "function_name" joulewise scripts configs tests` to find callers.
5. If a clause is ambiguous about what artifact it demands, record it as
   `AMBIGUOUS` with your best reading and why — do not silently pick one.

## Output

Write your findings to the output file your task names, in this exact format,
one block per clause. Then reply with a SHORT summary only (counts by status +
the verbatim clause text of every transaction-relevant B and C). Do not paste
the whole file into your reply.

```
### <DECISION-ID> · clause <n>
- clause (verbatim): "..."
- source: docs/decision_log.md:<line or range>
- status: A | B | C | D | AMBIGUOUS | UNVERIFIED
- evidence: <file:line> — <one line of what that line actually says>
  (repeat for each piece; include the "no callers" grep result for B)
- producer: <the file/function that writes the bytes, or "none found">
- transaction_relevant: yes | no — <one line why>
- note: <only if D (cite superseder) or AMBIGUOUS/UNVERIFIED>
```

Be exhaustive on clause extraction and conservative on status. A false A is the
worst outcome of this sweep — it is exactly the error that let D-157 live for ten
days. When torn between A and B, choose B and explain.
