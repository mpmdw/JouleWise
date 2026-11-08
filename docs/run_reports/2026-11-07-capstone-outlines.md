# Capstone outlines — 7 November 2026

Task brief/branch: `capstone/2026-11-08-outlines`. Intake HEAD:
`fc1f2ae9cc35a774d1175c462f84dd3c920757b6`. The requested branch was already
checked out, tracking local `origin/main`, with a clean worktree. No fetch,
network request, push, merge or branch rewrite was performed.

## Intake and scope

Read the repository AGENTS/CLAUDE conventions, Mission M0, source-of-truth map,
targeted restart/queue safety material, and targeted D-139/D-174 entries.
`ACTIVE_STOP_CARD` reported NONE. The explicit capstone brief selects this
bounded documentation task over older queue pointers and supersedes the
coordination-state update requirement. No task was registered; `RUN_STATE.md`,
`TASK_QUEUE.md`, `docs/process/state_kernel.json`, `tests/test_gen_state.py` and
`PROJECT_STATUS.md` were left unchanged. No delegation or external consult.

This was an AGENT desk task. No processes belonging to the running analysis job
were inspected or touched. No measurement, live/hardware check, model loading,
weight download, MLX execution or full-suite command was run. No real restricted
directory or external home-directory data path was accessed. Git reads used
local repository objects, including the permitted shared alternates if Git
needed them. Archive/model paths embedded in documents remained text only.
Neither the Block-5 analysis pipeline nor any raw-data reader was executed.

## Deliverables and findings

- `docs/capstone/TALK-OUTLINE.md`: 16 slides totalling 23 minutes, a 20-minute
  cut, one message per slide, sourced visuals/numbers, and speaker guardrails.
- `docs/capstone/PAPER-OUTLINE.md`: manuscript sections, a pinned source
  register, nine numerical-evidence rows, related-work map, validity threats,
  tables and a December writing schedule. Includes a complete pilot-only
  variant and a conditional variant requiring an admitted v4 release by about
  10 December. The November talk remains free of v4 outcomes in either case.
- `docs/capstone/FIGURES.md`: F1–F11 with committed text/summary inputs,
  caption limits and no measurement-Mac dependency. A conditional released-v4
  panel has no current data source and remains blocked; no figures were rendered
  as part of this outline task.

The principal claim boundaries are explicit: the known-bytes outside-rails
share is about 76% of a specific rotate-minus-repeat contrast; the meter is
DC input after the adapter; historical residual scores use GPU energy; six
reported omission checks reuse two distinct sabotage trajectories; sample maxima
and heavy tails are not a deployment false-alarm guarantee. The adaptive squeeze
and interpretability layer are prospective. No Block-5 or v4/v5 outcomes were
read, inferred or supplied.

## Source handling and uncertainty

Read the strategy, agenda, tripwire HTML, known-bytes slot fill, council designs
and amendments, targeted older paper-draft sections, and the requested
literature audit. The literature audit was read from local Git at
`16e1db6230a80a605d084f0f9f61431d541b793f`; no cited web pages were reopened.
The adjudicated synthesis takes precedence over its unreconciled appendices.

Protocol v3, the residual document and BYTES pilot directory are absent from
this working checkout. Read their reported versions from local Git at
`e901eb2a480d51377a494be9d797733dfcd0220b`. Read BYTES's summary and accounting
code without executing its benchmark or summary scripts. Read frozen residual
and calibration source code only to check the formula, scored energy channel
and threshold construction.

No tracked file matched `docs/run_reports/*align*pilot*` in the available local
Git history (`git log --all -1 --format='%H %s' -- 'docs/run_reports/*align*pilot*'`
returned no entry). The committed pilot-7 through pilot-10 lead records under
`docs/process_traces/` supply the reported results instead. The paper's source
register discloses this substitution and pins each report to intake HEAD.
No private seat report or `PILOT.json` was sought.

Open authoring questions, none blocking these outlines:

- Ed must confirm the exact mid-December paper deadline.
- The lead should confirm the committed lead reports are the desired citation
  layer, or supply an authorized already-reported public summary later.
- LIT decision 4 leaves Khiani's relationship to the project unresolved;
  provenance/disclosure must be settled before final citation text.
- v4 outcome inclusion is a future lead-owned release decision. Gate refusal
  or no admitted release by the cut selects the pilot-only paper.

## Verification

All checks below passed. This is documentation-only work, so targeted
structural/source checks were proportionate. No unittest module, compileall,
quick suite or canonical suite was needed or run. There is no new MLX code and
no native test for the lead to run outside the sandbox for this change.

- `python3 -B docs/paper/build/check_markdown.py docs/capstone/TALK-OUTLINE.md`
  — exit 0, zero hard defects.
- `python3 -B docs/paper/build/check_markdown.py docs/capstone/PAPER-OUTLINE.md`
  — exit 0, zero hard defects.
- `python3 -B docs/paper/build/check_markdown.py docs/capstone/FIGURES.md`
  — exit 0, zero hard defects.
- The same checker on this report — exit 0, zero hard defects.
- An inline, dependency-free Python source/link check — passed: three outline
  files' local links resolve; no private archive locators are embedded; slides
  are numbered 1–16 and sum to 1,380 seconds; figure IDs are F1–F11; all 18
  checked pinned source objects exist via `git cat-file -e`. This checked
  provenance structure, not a fresh measurement re-derivation.
- Final staged whitespace/diff review: `git diff --cached --check` — passed;
  only the three capstone documents and this report were staged.

## Commit and next step

Commit locally on `capstone/2026-11-08-outlines` with message
`docs(capstone): outline tripwire talk, paper, and offline figures`; do not push.
The resulting commit hash is returned in the task handoff.

Next exact step: review the claim ledger with Ed/advisor, then produce F1–F4
and the discrete F6–F8 pilot summaries from the pinned report rows, preserving
channel, cohort and uncertainty labels. This requires desk work only. Neither
figure production nor the pilot-only manuscript depends on opening sealed data.
