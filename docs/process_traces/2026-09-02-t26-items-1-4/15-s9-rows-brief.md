ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: ["docs/process_traces/2026-09-02-t26-items-1-4/15-s9-kernel-rows-draft.json"]
GENRE: implementation
EFFORT: high
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# DRAFT the seven S9 kernel rows (JSON only; the kernel itself is bench-only)

DETACHED WORKTREE `/Users/edr/code/JouleWise-wt-t26-a2` @ 10845c14. Write
exactly ONE file: `docs/process_traces/2026-09-02-t26-items-1-4/15-s9-kernel-rows-draft.json`.
Do NOT edit `docs/process/state_kernel.json`, do NOT run `gen_state.py`
without `--check`, do NOT commit, no `git checkout/stash`. You MAY run
`python3 scripts/gen_state.py --check` (read-only) and a scratch validation
described below.

## Why
Ruling §B4 (`docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md:245-247`):
"The S9 rows S9-01b/02/03/04/05/06/12 register at the bench with the
hard/start/pending dep". The sweep that produced them is
`docs/process_traces/2026-08-27-t26/ruled-not-installed-sweep/` (SHORTLIST.md
rows 19–30 hold the seven, FINDINGS-TABLE.md and raw/ hold the evidence
with file:line). The magistrate applies your draft to the kernel; your job
is the reading and the drafting.

## Shape
The file is a JSON object `{"tasks": {<id>: <row>, ...}}` with seven rows
whose shape is EXACTLY that of an existing row — copy the key set and value
types from `docs/process/state_kernel.json` task `T26-RULING-INSTALL-01`
(keys: acceptance{evidence[],pointer{json_pointer,label,path},summary},
authority{label,path}, dependencies[], fallback, fences[], flags[], goal,
id, lane, priority, rank, status, status_note, stop_card). Read
`scripts/gen_state.py` for every validation the kernel enforces (rank
uniqueness per lane, pointer path existence, priority vocabulary, status
vocabulary, dependency object shape) and satisfy each.

Dictated values:
- IDs and lanes/ranks (ranks are the next free ones; agent lane max today is
  119 and rank 120 is reserved for a row the magistrate is adding —
  VERIFY the max with a one-liner and state it):
  - `S9-01B-REFUSAL-PRODUCER-CHECK-01` agent rank 121
  - `S9-02-W10-SCOPE-P256-M1-01` agent rank 122
  - `S9-03-GAMMA-PREFILL-PROMPT-OWNER-01` agent rank 123
  - `S9-04-GAMMA-ROSTER-CHECK-01` agent rank 124
  - `S9-06-WINDOW-T0-GO-RECEIPT-GATE-01` agent rank 125
  - `S9-12-L10-REHEARSAL-SCHEDULE-01` agent rank 126
  - `S9-05-CAL-SCREEN-FLOOR-RULING-01` ed_external rank 71 (Ed rules; the
    live calibration screen 0.009724 vs the D-125 floor 0.010818 is a
    metrology value — magistrate does not rule metrology floors)
- `status`: `"pending"` for all (check the vocabulary in gen_state; if the
  kernel uses a different word for not-started, use that and say so).
- `priority`: choose from the kernel's vocabulary by the SHORTLIST severity:
  BLOCKER rows (01b, 02) and the two window-gating rows (06, 12) take the
  same tier as `T26-RULING-INSTALL-01`; 03/04/05 one tier lower. Quote the
  vocabulary you found.
- `authority`: `{"label": "Cold-gate ruling on the dx and t26-a packets (2026-09-02) §B4 + ruled-not-installed sweep S9", "path": "docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md"}`.
- `dependencies`: exactly one object on every row:
  `{"evidence": null, "kind": "decision", "required": "<one sentence: which T26 mechanism the row waits on>", "scope": "start", "state": "pending", "strength": "hard", "target": "D-170"}`.
- `goal`: 2–4 sentences from the sweep's own words: what was ruled, where
  it is not installed (file:line from FINDINGS-TABLE/raw — quote them, do
  not invent), and what closes it (CODE / RUNBOOK / ED as the SHORTLIST
  says). For 01b say "D-157 R-2 already rules the cure; this row is the
  producer-side check inside W-10, not a descoping".
- `acceptance.evidence`: 1–3 concrete, checkable strings (a test name that
  must exist and fail when the ruled value is absent; a runbook line; for
  05 "Ed's ruling recorded as a dated addendum on D-125 or a new D entry").
- `acceptance.summary`: one sentence. `acceptance.pointer`: json_pointer
  `/tasks/<ID>/acceptance`, label `<ID> acceptance`, path
  `docs/process/state_kernel.json`.
- `status_note`: "Registered 2026-09-02 by the magistrate per the cold-gate
  ruling §B4 (S9 row <n> of the ruled-not-installed sweep)." + one
  sentence of context.
- `fences`: [] unless the sweep names a fence the row must respect (06 and
  12 gate windows: add a fence "No spent quiet window launches while this
  row is pending" with the same authority object). `flags`: [],
  `fallback`: null, `stop_card`: null.

## Validation (scratch only)
Write a scratch script under `$TMPDIR` that loads the kernel, merges your
seven rows into a COPY, and runs whatever validation function gen_state
exposes (or invokes `gen_state.py --check` against a scratch copy if it
takes a path argument — read the CLI; if it cannot run on a copy, say so
and instead run the checks you can replicate by hand: rank uniqueness,
pointer existence, vocabularies). Paste the result. Leave the worktree
with ONLY the one new untracked file: `git status --porcelain` must show
exactly `?? docs/process_traces/2026-09-02-t26-items-1-4/15-s9-kernel-rows-draft.json`.

## Report
claude-codex-report/v1 envelope; then `## Rows` — a 7-row table (id, lane,
rank, priority, evidence sources by file:line); `## Executed evidence`
(the validation run, `gen_state --check` on the untouched kernel, `git
status --porcelain`). Any SHORTLIST row whose evidence you could not locate
in the sweep files is reported as `NOT PINNED` in the table, not invented.
