# 27 — Magistrate terminal review, PR #334 NIGHT-CENSUS-CHATGPT-APP-01 install, merge candidate `92408a18` (gate rows 7, 8, 10, 12)

Activation `24b9d3dd`, 07:00 PDT 2026-09-13. Read in full session context by the magistrate. Base `27957b60` (= main); diff `git diff 27957b60..92408a18`: `docs/phase_2/derivation_night_runbook.md` (+15 lines, one new §0.6 paragraph pair), `docs/process/NIGHT_HANDBACK.md` (the successor notice's precondition sentence, 3 lines), `tests/test_night_gate.py` (+17, one test).

## Row 7 (code-reading diff gate)
- The test: `FakeProbeSource` + `result` helpers (module lines 23/61) as every neighbour uses; stdout is the recorded live argv of pid 25658; asserts the refusal reason, that the detail preserves the line, and that `AGENT_CENSUS_ARGV` is the literal. Refuter 20 and pairing refuter 12 both ran it: passes at HEAD; FAILS under a narrowed literal (`codex mcp-server|codex exec|claude|t3`) and under an `/Applications/ChatGPT.app/` exclusion inside `agent_census`. Defect-shaped against both narrowing routes.
- The runbook paragraph: A2 + A3 text from pairing refuter 12, with three inline glosses added at the bench after refuter 20's first-use lens ("helper processes", "argv", what "refuses the night" means); every factual claim in it was probed live by the magistrate at 06:50 (nine ChatGPT helper lines in the census; the app's top-level `…/Contents/MacOS/ChatGPT` absent from it).
- The handback sentence: A1 text plus "so no chain starts". It is the 09-15 successor notice's precondition; the frozen clone at H `27957b60` does not carry it, which is correct — the arm-time email is composed from main, and the clone's handback is what the courier reads after the night.
- Design question answered: does anything change what the night gate DOES? No production code changes; the pattern is pinned twice more (the new test and the existing literal test at line 296).

## Row 8 (overbuild / merge-ability): nothing to prune; merges clean (base is main's tip).

## Row 10 (fresh eyes after every post-review commit)
Post-review commit after refuter 20 (`cda6b727`): `92408a18` — the three glosses only (`git diff cda6b727..92408a18`: +6/−5 lines across the two docs; test untouched). Read by me line by line; `tests.test_night_gate` and `tests.test_docs_freshness` OK after it.

## Row 12 (terminal review)
Merge candidate `92408a18`. Authority chain: kernel lane (ruling-first) → cold gate packet 05 ruling 10 → Opus pairing refuter 12 (AMEND) → synthesis 13 (amendments adopted; gloss addendum recorded) → refuter 20 → this review. Nothing in the diff amends a process rule: the ruled behaviour is the existing behaviour, now stated and pinned. Verdict: LANDABLE once row 9 (replay at `92408a18`) and row 11 (CI) are green.

**Addendum (07:35 PDT):** main moved to `64fc4e27` (PR #329); merge `f8bcccb2` = `92408a18` + main, zero conflicts, `git diff 92408a18..f8bcccb2 --stat` = main's own 334 archive files, none touched by this PR. Merge candidate is now `f8bcccb2`; row 9 is the replay on the integration tree `ee82373b` (= #317's `c59bdc57` + this head).
