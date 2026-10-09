# Dry render of the three chains with the 18-member corpus

Magistrate activation 1aed44f9, 2026-10-09 09:15 PDT. Ruling section D, gate 2. Nothing was executed but
the renderer and a shell parse.

A **chain** is the shell program a window runs between its two calibration captures; the plan writer
renders it from the pack's plan tree. A **dry render** renders it with scratch directory names in place of
a real window's, parses it with `zsh -n` (which checks syntax and runs nothing), and reads the rendered
commands. The question it answers: does the corpus stage of each pack now ask the runner for 18 members?

Tree: branch `lane/2026-10-09-corpus18` at `a5ae00c4623a2770ab1156b4b1bf3cba0aad761f`. Program: the
production functions `joulewise.b5.chain.stage_plan`, `stage_argv` and `render_chain`, called through
`tests/fixtures/b5_plan/corpus18_render.py` with `/opt/homebrew/bin/python3.13 -B`; output written under a
scratch directory in `/private/tmp`.

| Pack | Corpus stage | `expected_count` | `--max-failures` in the stage's runner command | Rendered lines carrying `--max-failures 18` | `zsh -n` | Rendered chain SHA-256 (scratch bindings) |
|---|---|---|---|---|---|---|
| ALPHA | `alpha-bound-collection` | 18 | 18 | 2 (the stage and its retry) | 0 | `6944e1a1c822c290e9492d1183ea68322f7a89fa087552b3b5464626b3430418` |
| BETA | `beta-bound-collection` | 18 | 18 | 2 | 0 | `1731e07f034eb3a1c73f2d4a4f22de76dac5a30b7629c5badc9821c9105cd647` |
| GAMMA | `gamma-bound-collection` | 18 | 18 | 2 | 0 | `f14f9e3f3c3440622bd80f9144f7d406c30fd2f2668bff68e4579c30515a45bd` |

Each rendered script still has 2 comment lines that say 12 (the registered deviation 9: comment strings
the chain program writes, which no logic reads). A real window's chain differs from these bytes only in
its directory names and ids, so the digests above identify these scratch renders and nothing else.

The independent reviewer rendered the three chains separately, by calling the same three production
functions without the helper, and found the same counts
(`/Users/edr/night-archive/b5-consults/corpus18-build/sol-window-review.full-report.md`).
