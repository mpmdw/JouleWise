# Fable cold pass — PR #687 (ALIGN R0 echo prompt states its call total)

Reviewer: Claude Fable 5.1, cold (no prior context), detached worktree
`/Users/edr/code/wt-cold-78981c26-687`, head `e05f53f56`, base `84848dc68`
(lane/2026-11-05-align-pilot10-benign). Read: the diff, the PR body, the Sol
executing review, the rerun2 record (`NOTE.md`, `echo_probe.py`,
`echo_probe_results.json` on `origin/records/2026-11-06-align-r0-v4-rerun2`),
and `joulewise/align/r0.py` (`rewrite`, `turn_row`, `append_result`,
`load_coherence`, `template_rewrites`, `generated_rewrites`, `checkpoint_verdict`).

## Verdict: ADMIT_WITH_FIXES

The code change is sound and the live model confirms it at the production seed.
One fix is owed under the no-silly-numbers rule (M1, a comment, not a number).
Two LOW record-hygiene items may follow in the same or a later lane.

## Answers

1. **What B7 measures is unchanged.** `rewrite()` (`joulewise/align/r0.py:69-79`)
   compares `prompt_token_ids + output_token_ids` of turn k with the render after
   the assistant message and the tool reply are appended. The user prompt is the
   same leading prefix of both sides, so it cancels: rewritten tokens can arise only
   from how the template re-renders the stored assistant turn (reasoning, visible
   text, tool call) and the tool reply. The prompt changes only which turns D
   samples. The one bias channel is turn shape: a prompt that makes D emit less
   visible text or shorter reasoning changes the population of turns the template
   is tested on. That channel exists for any prompt, including the old one, and
   the live data show no direction: 0 rewritten tokens and closed reasoning on
   every transition under both prompts (old: 6+12+12 turns; new: 12+12+12 in the
   record, plus my 12 below). Closed-reasoning eligibility (`r0.py:95`) comes from
   the endpoint's parse flags per turn, not from the prompt text.
2. **Floor and threshold unchanged in value and use.** Floor `12` is now
   `ECHO_TRANSITIONS` at `r0.py:31`, consumed at `r0.py:510`, `:533`, `:565`;
   D's threshold is still `fraction > 0` at `r0.py:569`. Base and head
   `checkpoint_verdict` agree on 11 rows (inconclusive), 12 clean (not_required),
   12 with one rewind (required). `generated` still passes at `>= transitions`
   (`r0.py:556`) and the loop still stops at 12, so the model never reaches its
   announced 16.
3. **No other pass/fail consumer.** `load_coherence` (`r0.py:472-491`) uses
   `ECHO_PROMPT` at seed 94 for `tool_round_trip`, but `status` is built from the
   NLL verdict and `generation_check` only; the round trip is flagged diagnostic
   (`r0.py:502`). Executed: with the echo round trip removed entirely, `load`
   still passes with empty `reasons` (tail below). The prompt string is not
   registered or hashed anywhere else (`grep` over joulewise/tests/scripts/docs/configs).
4. **The `+ 4` reason is incomplete.** The comment at `r0.py:27-30` and the PR
   body justify a spare so "the required transitions are never the model's
   announced last call". That argument supports any spare of at least one; it
   does not say why four. The live evidence (record seeds 95-97, my seed 95) was
   collected only at 16, so it shows 16 works, not that 4 is derived. Sol's review
   accepted the motivation; I do not, on magnitude. See M1. I substitute no number.

## Findings

- **M1 (MEDIUM) `joulewise/align/r0.py:27-32`.** State what the size of the spare
  covers, or say plainly that it is an unmeasured margin verified live only at 16.
  A candidate true reason the author may hold: keep the 12 measured turns away from
  the model's wind-down turns (near an announced last call D tends to add visible
  text or a summary, which changes turn shape and thus the sampled population in
  answer 1). Whatever the reason, write it; "spare" alone is a bare number.
- **L1 (LOW) `joulewise/align/r0.py:567`.** The inconclusive reason string still
  hardcodes "12" while the floor is `ECHO_TRANSITIONS`; make it an f-string so the
  two cannot drift.
- **L2 (LOW) `joulewise/align/r0.py:556-558`.** `generated_rewrites` records no
  prompt text or hash. The 2235Z record (6 transitions, old prompt) and the coming
  re-run (new prompt) will look identical in `report.json` apart from the checkout
  sha. `load` records `short_prompt` and `generation` records `user_prompt`; add
  `"prompt": ECHO_PROMPT` here for the same lineage.

Not findings: the new test kills the stated mutants (no number, number below the
floor, two numbers, default drift) and `test_r0_checks.py:285` still holds
("exactly once" absent). Budget admission (`r0.py:539`) moves by ~20 prompt tokens.

## Commands run (worktree cwd, venv python -B, TMPDIR scratch, JW_B5_SYNTHETIC_ONLY=1)

```
python -B -m unittest tests.align.test_r0_checks
  Ran 30 tests in 0.696s
  OK
  pass: /Users/edr/night-custody/scratch-78981c26/tmp-fable/tmpuczriec2/output/report.json; complete_r0=False
```

Live probe, ONE model process, seed 95 only, head prompt (script copied to
`/Users/edr/night-custody/scratch-78981c26/fable/echo_probe.py`, restricted to
`PROMPTS={"head_e05f53f": r0.ECHO_PROMPT}` and `seeds=(95,)`; argv[1] = worktree;
output `.../fable/echo_probe_seed95_head.json`, log `.../echo_probe_seed95_head.log`):

```
PROMPT: Call r0_echo with value desk-check 16 times in total, one call per turn. After each
tool reply, make the next call. Do not stop, summarize or ask the user before all 16 calls
are made. ECHO_CALLS: 16 ECHO_TRANSITIONS: 12
{"prompt": "head_e05f53f", "seed": 95, "status": "pass", "transitions": 12, "closed": 12,
 "rewritten": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "off_spec": 0,
 "verdict": {"status": "not_required", "eligible_transitions": 12, "rewind_fraction": 0.0},
 "last_visible": "\n\n<tool_call>\n<function=r0_echo>\n<parameter=value>\ndesk-check\n</parameter>\n</function>\n</tool_call>",
 "seconds": 45.5}
EXIT=0
```
Afterwards `ps` showed no python/MLX model process (only this reviewer's claude -p).
This reproduces the record's count16/seed 95 row (12/12/0, not_required).

Fake-backend probe (stdin script; base module loaded from `git show 84848dc68:joulewise/align/r0.py`):

```
base: generated=pass/12 rewritten=[0 x12] template=diagnostic/12 D=not_required
head: generated=pass/12 rewritten=[0 x12] template=diagnostic/12 D=not_required
load_coherence with NO echo round trip: pass reasons= [] round_trip.succeeded= False diagnostic flag= True
checkpoint_verdict floor expr : ['if len(rows) < ECHO_TRANSITIONS:']
checkpoint_verdict threshold  : ['... "required" if fraction > (0 if tag == "D" else 0.10) else "not_required",']
D rows=11 rewritten=0: base==head -> inconclusive
D rows=12 rewritten=0: base==head -> not_required
D rows=12 rewritten=1: base==head -> required
ECHO_TRANSITIONS 12 ECHO_CALLS 16
```

`git -C <wt> diff 84848dc68 HEAD --stat`: r0.py +12/-4, test_r0_checks.py +20, review doc +418.
Nothing committed or pushed; this file is the only edit.
