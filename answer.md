# WP16 handoff — ALIGN v4 kit skeleton

Branch: `lane/2026-11-05-align-v4-wp16-kit`, from `c8ef6b2f6`.
Implementation commit: `edac8cc7a50494f414fae4625713d246718500d1`
(`Build fail-closed ALIGN v4 W1 kit skeleton and acceptance tests`). This
handoff and the dated run report are committed separately. Nothing pushed.

Implemented the 18-member A1 roster, independent seed/turn-seed witnesses,
ABBA/BAAB position and predecessor balance, midpoint after ordinal 9, pinned
pilot-7 contrast sources, and prospective fit-rule helper. All four original
anchor configs are byte-identical to `83e2dac59`, including their run IDs.
D configs carry the required sampler/history/family/XML selection, explicit
checkpoint zero, neutral warmup, heavy/G1/hold policy shape and pending limits.
Added kit/pack/schema parameters to the shared session runner and a guarded
v4 wrapper. V3 generator and committed kit bytes remain unchanged.

Files: `scripts/align_v4_kit.py`, `scripts/align_v4_session.py`,
`scripts/align_pilot_session.py`, `tests/align/test_v4_kit.py`, and the committed
kit under `configs/campaigns/align_v4/`. Detailed evidence and limitations:
`docs/run_reports/2026-11-05-align-v4-wp16-kit.md`.

## Verification

Each unittest command ran alone, with `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=/private/tmp`.

| Exact command | Final result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_v4_kit` | **31 tests, 31 passed**, 5.047 s |
| `python3.13 -B -m unittest tests.test_align_pilot_session` | **15 tests: 14 passed, 1 failed**, 134.689 s |
| `JW_ALIGN_NATIVE_TESTS=0 python3.13 -B -m unittest tests.align.test_history_rendering` | **9 tests: 5 passed, 1 failed, 3 skipped**, 0.064 s |
| `python3.13 -B -m unittest tests.align.test_xml_tool_calls.XmlToolCallTests` | **14 tests, 14 passed**, 0.027 s |
| `python3.13 -B -m compileall -q joulewise tests scripts/align_v4_kit.py scripts/align_v4_session.py scripts/align_pilot_session.py` | Exit 0 |
| `python3.13 -B scripts/align_v4_kit.py` | Exit 0, generated skeleton |
| `python3.13 -B scripts/align_v4_kit.py --check` | **Expected exit 1**, names pending WP11/WP18/R0/R1/WP15 inputs |
| `git diff --check` / `git diff --cached --check` | Exit 0 |

Both legacy failures are in unchanged code: the supplied integration base
serializes `hybrid_checkpoint_limit: 0` on legacy paths. They are the WP2
default-None repair, not fixed here. History skips: one optional-Jinja2 test
and two native tokenizer/MLX tests. Two development runs of the new tests
found timing-fixture errors; both were corrected before the final 31/31 run.
All unittest attempts together took about 161.5 s. No full suite was run.

## Blockers, uncertainty and next step

This is an intentionally unarmable skeleton. WP11 D identity pins/inventory/
verification and WP18 historical X/Y max_turns/fixture digests are null.
R0 effort and R1 budget/intercept/deadman/thermal slots are also null. The
placeholder test proves `--check`, prepare and install refuse them; no model
or measurement path was followed. There is no arm-compatible `sizing_b5.json`.

The window-plan draft at `40c569cfd` chooses D index **101**. Synthesized WP16
and A1 instead require **1**, with development **91–93** and held-out from **2**;
implemented the latter. A1's conditional checkpoint enablement is superseded
by the synthesized ruling: D stays explicitly **0** throughout the series.
No new Ed ruling is requested for this skeleton.

Lead next: review/cherry-pick the implementation onto the repaired integration
lane, obtain the non-author Opus review, and rerun the legacy modules after
WP2. WP15 must implement the launcher and member-5 reference custody; its
input field is only a placeholder, not runtime wiring. WP17 must consume R1
evidence, apply/requalify any fit-rule changes and generate real sizing. The
builder currently emits the full 18-member skeleton; the fit helper returns
prospective ordinals/budget, not a silently changed committed roster. WP21
still owns the complete v4 desk. Merely replacing nulls is not arm admission.

MLX/Metal, real tokenizer IDs, historical token replay, holds, sensor selection,
and local D identity authentication were **not validated** here. Lead must run
the pinned-stack native history, checkpoint, thermal/lookahead and R0 memory
modules outside the sandbox, one at a time; SMC and R0/R1 hardware gates need
the clean measurement Mac. Exact command pointers are in the dated report.
