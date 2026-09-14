# 10 — Cold Fable gate ruling: CI-TRIM-01 T2 (PR #317), packet 17

Judge: Claude Fable 5.1, fresh non-interactive session, 2026-09-13. Single session, no subagents, every probe in the foreground.

## Contamination disclosure

Auto-loaded by the harness before any tool call (not opened by me, not reread): `~/.claude/CLAUDE.md` (global writing/orchestration rules), the worktree's `CLAUDE.md` (Codex bridge notes), and the memory index `MEMORY.md` (one-line checkpoint pointers; two lines mention that #317 was "escalated, same signature" to a cold gate and that packet 17 exists). The git-status banner listed five recent commit subjects, one saying "design consult 15 (Opus: option A)". Effect: these repeat the magistrate's framing already inside the packet (Exhibit H). No conclusion below rests on them; every load-bearing fact was checked against files named by the packet or git objects at pinned revisions. I did not read `CLAUDE.local.md`, `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/decision_log.md`, or any trace outside the packet directory.

Digest check (before the merits): validator run first with the convening prompt's charter sha ending `…870ff8c7285c749c1b440c95d81` typed as `…880…` → `REFUSE`, reason `charter_trusted_observed_mismatch`, rc=2. Re-run with `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` and packet sha `325d0ddc4a0ca821271d68c6ee277d268974fc4261b26bbd3fe46600aabc0792` → `PASS`, rc=0, all eleven exhibit digests observed = expected. Method: `scripts/validate_gate_packet.py` as instructed.

Packet hygiene: complete and neutrally assembled. Exhibit K's kernel excerpt is verbatim at `27957b60:docs/process/state_kernel.json:6516` (verified). Ed's acceptance is a quoted Gmail line I cannot open; Q2 takes it as the premise the question itself states. The packet's own Q1 note fairly flags the F/G disagreement, which I resolved from the file (below).

## Q1 — the mechanism: AFFIRM option A (no path-based skipping)

**Ruled option:** A. Delete the detector, the docs-readers job, and the path guards. Keep T1 (fences job), T3 (`pr-fast` stays deleted), T4 (zsh guard), FIX-1 (per-run concurrency group for pushes, ref group for PRs), FIX-3's intent is moot once nothing is gated.

**Exact edits to the post-image `8819cb5f:.github/workflows/ci.yml`** (line numbers verified by `git show`):

- Delete lines 15–91: the four-line comment starting "Docs-only paths are selected by classify_path" plus the whole `changes:` job (19–90) and its trailing blank line.
- Delete lines 125–194: the three-line "FENCE for documentation-asserting tests" comment plus the whole `docs-readers:` job (128–193) and its trailing blank line.
- Delete lines 196–197 (`needs: changes` / `if: ${{ !cancelled() && needs.changes.outputs.code != 'false' }}`) under `test:`; lines 286–287 under `calibration-exits-exclusive:`; lines 322–323 under `calibration-writer-crash-matrix-exclusive:`.
- Replace comment lines 8–9 (line 9 names the deleted docs-readers fence) with one sentence: "Pushes get a per-run group so nothing can evict a queued run; PRs share a ref group and cancel superseded runs."
- Keep unchanged: lines 10–12 (`concurrency` block, FIX-1); the `fences` job and its comment (92–123); the bodies of `test`, both exclusive jobs, `build` (424–), `installed-wheel` (442–); the zsh guard steps; `pr-fast` remains absent. `scripts/shard_tests.py` untouched.
- No test parses `ci.yml` (`git grep -E 'ci\.yml|workflows/' 8819cb5f -- tests` → no hits), so the deletions break no test. Exhibit B §5 reports no branch protection on main; I did not re-query GitHub, so the lead confirms there are no required checks named `changes` or `docs-readers`.

**Reason, grounded in the exhibits and my probes.** The proponent of skipping bears the burden of showing that no documentation-asserting test can be skipped. Two mechanisms were tried and both fail on primary evidence:

1. Static selection over test sources (rounds 0 and 1) cannot enumerate reads. I ran both regexes over the test sources at `8819cb5f`: the shipped regex selects 48 of 230; Exhibit G's widened regex selects 63, but the fifteen it adds are not Exhibit F's fifteen. It still misses `tests.test_claims_index_lint` (reaches `docs/contracts/analysis_plans.md` via the imported constant `claims_lint.DEFAULT_AP_PATH`, `test_claims_index_lint.py:382`) and `tests.test_gen_derivation_night` (via `GEN.RUNSHEET_PATH`), while adding two JSON-only readers (`test_env_locks`, `test_run_night`). And `tests.test_calibration_exits` matches the widened regex yet stays subtracted as an exclusive module: it reads `docs/contracts/calibration_ledger_append.md` and `docs/phase_2/window_runbook.md` through `REPO_ROOT / "docs" / …` joins and asserts on their content (`8819cb5f:tests/test_calibration_exits.py:1501–1533`, verified). Exhibit F is right on R2; Exhibit G's "no exclusive module reads docs" is false.
2. A runtime-traced reader map (options B/C) was refuted by executed counterexamples from two blind seats: a subprocess read of `docs/paper/draft-v1.md` records zero docs reads in the parent hook (Exhibit J, `tests/test_paper_build.py:95` → `check_markdown.py:499`; Exhibit I V2 agrees), `git show` reads open no tracked path (Exhibit I V4, Exhibit J counterexample 2), and a file added by a docs-only push cannot be in any trace taken before it existed (Exhibit J counterexample 3, `claims_lint.py:861` rglob). The fail-closed repair pulls 120 of 230 modules and 66 % of suite seconds (Exhibit J, from committed weights), so a sound docs-only run costs ≈121 runner-min against 190. That is a 36 % saving bought with 12–24 seat-hours, a permanent map, and a new silent-hole class for every future subprocess in a test.

No option "Other" clears the burden: Exhibit J's burst-coalescing lever reverses FIX-1 and trades per-commit content coverage, a different question the packet did not pose; it may be brought as its own packet. Runner minutes are not shown anywhere in the packet to be a binding constraint (both seats ask the lead to confirm billing); fence soundness and magistrate attention are. Under A the kernel fence stays literally true and the PR still lands T1, T3, T4 and FIX-1.

Severity notes for the lead (MATERIAL, amend before merge): the PR title and body (Exhibit K) describe T2, a "1.4 runner-min" docs-only row, and "60 test modules"; under A the body must drop T2 and the docs-only row and restate "Fences that survive" #1 as true again. NIT: under FIX-1, N rapid pushes run N concurrent full matrices instead of queueing (Exhibit G Q2); accepted, cost only.

## Q2 — the kernel fence and the addendum

**(a) AFFIRM: under option A no narrowing of the fence is needed.** The fence (`27957b60:docs/process/state_kernel.json:6516`) says merges, whole-window verdicts and audited heads keep the full suite. With no path gate, every push to main and every PR runs the full matrix plus both exclusive jobs, exactly as today. Exhibit G's Q3 point (the merge itself would falsify the fence) applied only to the path-gated shape and is dissolved by A.

**(b) The addendum may follow the merge as bookkeeping; it is not required before.** Reasoning: the fence forbids the fast tier *substituting* for a full-suite gate; deleting the fast tier cannot violate that. What the deletion changes is the task's goal and acceptance-evidence row 2 ("PR-fast/full tier split implemented"), which are ratified prose, not a fence. The authorizing act already exists and predates the merge: the PR body's decision 2 proposed "accept (and retire `pr_fast_tier` …, amend the TEST-SPEED-01 kernel text)" and Ed accepted "as proposed" (Exhibit K). The addendum records that ruling; it does not make it. Condition: it lands in the same activation's bookkeeping commit as the merge, together with the kernel-row prose amendment, so no head is left with a goal that names a tier the workflow no longer has. Exact text:

```
**TEST-SPEED-01 addendum (2026-09-13): lever 2, the PR-fast tier, is retired.** Ed ratified three levers on 2026-08-03 (suite-speed priority, a PR-fast/full tier split, a Blacksmith runner evaluation). Lever 2 was implemented on 2026-08-23 as the additive `pr-fast` job in `.github/workflows/ci.yml` and the `pr_fast_tier` selection block in `scripts/test_timings.json`; it was never a gate and never a required check. On 2026-09-12 Ed accepted PR #317 "as proposed" (Gmail 1a0969ba0b31c2b2), whose decision 2 proposed deleting `pr-fast`, retiring `pr_fast_tier`, and amending this task's kernel text. Lever 2 is therefore RETIRED with zero test deletions: PR #317 deletes the job and the block, and the TEST-SPEED-01 goal and acceptance-evidence row 2 in `docs/process/state_kernel.json` are amended to read "implemented 2026-08-23, retired 2026-09-13 by owner acceptance". The fence is unchanged and remains literally true: no test deletions; merges, whole-window verdicts, and audited heads keep the full suite. Cold gate 17 (2026-09-13) ruled option A on PR #317 T2, so no path-based skipping narrows this fence. Levers 1 and 3 are unaffected.
```

**(c) `pr_fast_tier` in `scripts/test_timings.json:6–13`: delete it in this PR.** Nothing reads it: `git grep pr_fast_tier 8819cb5f` hits only the JSON itself and three trace records; `scripts/shard_tests.py` and `tests/` never name it (the `pr-fast` mention in `tests/test_check_gate_ledger.py:36` is a comment). Ed's acceptance explicitly covered retiring it. Leaving dead config that describes a tier "derived at run time" invites the next reader to believe the tier exists. Removing a top-level JSON key the loader never touches is a two-line diff the full matrix (which runs under A) will exercise.

## Q3 — for the record: AFFIRM the escalation

The magistrate's escalation after deltas 07/08 was the correct application of the standing trigger, and the charter's own §9 rule ("two consecutive rounds failing with the same signature: the next spend is a consult or redesign, not round three"). Exhibit G's one-line widening is not a bench fix; it is round three of the same class, and I proved it on the file: widening moves the count from 48 to 63 but reaches only 13 of Exhibit F's 15 missed modules, leaves the two imported-constant readers (`test_claims_index_lint`, `test_gen_derivation_night`) unselected, and leaves `test_calibration_exits` subtracted by the exclusive-module rule on a false premise. A third static widening would have produced a third delta with the identical sentence "a documentation-asserting test does not run on a docs-only push". Exhibit G itself wrote "same signature: YES". The consult then found the structural reason (reads escape any static or open-hook observer), which is exactly what a consult is for.

## Executed probes (all read-only, this session)

1. `validate_gate_packet.py` with the typo sha → REFUSE rc=2; with the correct sha → PASS rc=0, 11/11 exhibit digests match.
2. `git show 8819cb5f:tests/test_calibration_exits.py | sed -n 1495,1540p` → docs reads and assertions at 1501–1533 (resolves F vs G).
3. `git show 8819cb5f:.github/workflows/ci.yml | grep -n` for job ids / `needs` / `if` / blank lines → the line numbers cited in Q1.
4. Shipped and widened selection regexes run with the canonical venv interpreter over a `git archive 8819cb5f tests scripts/test_timings.json` extract in a temp dir (removed after): `shipped 48, widened 63`; F15 still missed by widened: `test_claims_index_lint`, `test_gen_derivation_night`; exclusive modules matching widened: `tests.test_calibration_exits`.
5. `git grep -n pr_fast_tier 8819cb5f` and `git grep -E 'ci\.yml|workflows/' 8819cb5f -- tests` → no code or test reader of either.
6. `git show 27957b60:docs/process/state_kernel.json` parsed with the venv interpreter → TEST-SPEED-01 fence, status `queued`, evidence row 2 match Exhibit K verbatim; fence at line 6516.
7. `docs/process/coldgate_charter.md` read in full (7155 bytes).

Not executed: any test, the discovery suite, hosted CI, GitHub API reads. No file outside this ruling was written.
