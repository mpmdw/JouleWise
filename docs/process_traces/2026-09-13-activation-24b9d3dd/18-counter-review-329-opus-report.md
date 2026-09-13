# 18 — Counter-review, PR #329 DOCS-THIN-01 (gate row 6, Opus 5 contract lens)

Head reviewed `f636f70b`; PR base `a4bb8838`; round-0 merge head `ae5b09e7`.
Read-only in `/Users/edr/code/JouleWise-wt-ref-329`. No tracked file touched.

**VERDICT: AMEND** — two one-line link repairs (§4 SF-1, SF-2) and a PR-body
refresh (§7). No blocker: the archive itself is mechanically exact, the code
change masks nothing, and no runtime reader is broken.

> Deciding line for the amendment: `docs/specs/axi/sb_static_batch_verdict.md:6`
> still reads `evidence: \`docs/process_traces/2026-07-16-axi-sb-live-probes/\``
> while line 200 of the *same file* was repaired by fix round 1.

---

## 1. Rule fidelity — CLEAN

`git diff -M --name-status a4bb8838..HEAD` → **310 R100, 16 M, 7 A; zero R0xx,
zero D**. Every R100 checked in-process against the rule (`docs/X →
docs/legacy/X`; root `Y.md → docs/legacy/root/Y.md`): **310 checked, 0
violations**. Three root moves only: `FREEZE-FCM01.md`, `STATUS.md`,
`STOPPED-FCM01.md` → `docs/legacy/root/`.
`git diff -M --numstat` shows **no `=>` row with a non-zero add/delete count** —
no content changed during archival. `git diff --check a4bb8838..HEAD` rc 0;
`scripts/gen_state.py --check` rc 0.

## 2. The one code change — CLEAN (narrowing named, nothing masked)

`tests/test_docs_freshness.py`, +2 lines in `_decision_reference_documents`,
the corpus for `test_decision_references_resolve` (no dangling `D-###`):

```
        and not path.relative_to(root).as_posix().startswith("docs/process_traces/")
+        # DOCS-THIN-01: archived history stays outside the live reference scan.
+        and not path.relative_to(root).as_posix().startswith("docs/legacy/")
```

The file has no module docstring; the guarantee is the assertion at line 1059
(`self.assertEqual([], dangling, ...)`). Forcing problem: archived traces move
from `docs/process_traces/` (already excluded on main) to
`docs/legacy/process_traces/`, which the old prefix test no longer catches —
without the +2 the scan would *grow* from 402 to 685 documents.

Narrowing is real but bounded and empty: re-running the helper with the new
clause removed gives 685 vs 402 documents, i.e. **283 newly excluded**, and
`_dangling_decision_references` over exactly those 283 returns **0**. The test
passes with or without the exclusion today. Main 459 / branch 402 (57 dropped)
in the PR body reproduces exactly. `python3 -m unittest tests.test_docs_freshness
tests.test_gen_state` → `Ran 75 tests ... OK`.

## 3. Runtime readers — CLEAN

Scanned 2,768 files under `joulewise/`, `scripts/`, `tests/`, `.github/`,
`configs/`, `docs/process/state_kernel.json`, `docs/contracts/` for all 310 old
paths plus every archived directory prefix. **10 apparent hit files, all the
substring `STATUS.md` inside `WINDOW_STATUS.md`** (`scripts/window_status.sh:33`,
`:102`, `docs/contracts/window_liveness.md:670`,
`tests/test_window_status_guard.py:50`, `:75`, and `CLAIMS_STATUS.md` matches).
Boundary-anchored recount: **0 real references**. The five magistrate/courier/
handback process docs (`docs/process/{MAGISTRATE_RELAUNCH_PROMPT,
MAGISTRATE_WATCHDOG,NIGHT_COURIER_PROMPT,NIGHT_HANDBACK}.md`, watchdog set) are
inside that scan and clean, including `NIGHT_HANDBACK.md` as it stands on
`origin/main` today.

## 4. Living surfaces — 2 should-fix, 3 nits

**SF-1 (should-fix).** `docs/specs/axi/sb_static_batch_verdict.md:6` — the PR
repaired line 200 of this file and left the header verdict citation of the same
archived directory stale. Replacement (one path, nothing else on the line):

```
  evidence: `docs/legacy/process_traces/2026-07-16-axi-sb-live-probes/`)
```

**SF-2 (should-fix).** `docs/specs/axi/sc_spec_decode_verdict.md` — the sibling
pinned-verdict spec, not touched by this PR at all, cites the archived
`2026-07-17-axi-sc-live-probes/` twice. Same signature as FIX-1 (an archived set
split from its sibling). Replacements:

- line 7: ``  evidence + SHA-256: `docs/legacy/process_traces/2026-07-17-axi-sc-live-probes/`).``
- line 280: ``` `docs/legacy/process_traces/2026-07-17-axi-sc-live-probes/`. ```

If the two `docs/specs/axi/*_verdict.md` files are instead ruled dated records,
then SF-1's counterpart at line 200 should not have been repaired either; the
defect is the asymmetry, and either direction closes it.

**N-1 (nit).** `docs/project_critique_review.html:880` — the `href` is repaired
to `legacy/test_audit_2026-07-07.md`; the anchor *text* still reads
`docs/test_audit_2026-07-07.md`. Defensible as "what it used to be"; flagged so
the choice is on the record.

**N-2 (nit, by policy `docs/legacy/README.md:16`).** Full-repo boundary-anchored
scan outside `docs/legacy/` found stale old-path refs in 108 files. All are
dated records: `RUN_STATE.md` 36 hits, every one at line ≥1831, i.e. below
`RUN_STATE.md:1807` `## ▶▶ T7 CHECKPOINT (2026-08-15, Ed pause order) —
superseded by T8 above; kept as record`; `TASK_QUEUE.md` 6 hits (lines 182–203,
under `## Completed Queue Items` at line 98); `docs/council_log.md` 22 and
`docs/decision_log.md` 32 in append-only dated entries; `docs/run_reports/`,
`docs/stream_logs/`, `docs/reviews/`, `docs/advisor_briefs/`,
`docs/process_traces/`. No live non-dated document other than SF-1/SF-2 is
affected.

**N-3 (nit, D-136).** `docs/site/*.html` (9 files, ~55 hits) are generated pages
of the retired site lane; left as they are, per the resume note.

## 5. README arithmetic — CLEAN, exact

Recomputed with `git cat-file -s a4bb8838:<old path>` over the 310 old paths:
**310 files, 83,134,998 bytes, 79.2837… → 79.28 MiB.** All three README figures
match to the byte. Every one of the 17 table rows reproduces exactly, e.g.
`docs/process_traces/<dated dir>/` 240 / 55,109,940; paper-portfolio 52 /
27,777,245; `docs/evidence/` 4 / 5,582; `RESUME-2026-07-26.md` 1 / 13,223. The
listed archived trace directory names are **41**, and `diff` against the 41
distinct dated directories in the move set is empty.

## 6. Merge-ability — CLEAN

`origin/main` = `27957b60`. `git merge-tree --write-tree origin/main f636f70b`
→ rc 0, tree `77e13c4a`, **0 conflicts**. Note for the record: the pushed PR
head is **`59e06abb`**, whose parents are exactly `f636f70b` and `27957b60` —
i.e. the GitHub head is the reviewed head plus that clean merge, and
`git diff f636f70b 59e06abb` is only the three main-side files
(`configs/production_custody_inventory.json`, `docs/process/NIGHT_HANDBACK.md`,
`tests/test_arm_readiness_schemas.py`), none of which references a moved path.
`gh pr view 329` reports `mergeable: MERGEABLE`. Reviewing `f636f70b` is
therefore equivalent to reviewing the PR head for all DOCS-THIN content.

## 7. PR body — stale sentences and replacement text (should-fix)

1. "**309 git renames**" → "**310 git renames**".
2. "5 loose retired process-trace records" → "**6** loose retired process-trace
   records" (the three `RESUME-2026-07-2{6,7,8}.md` plus the three 2026-07/08
   loose files).
3. "Active documentation surface `docs/` excluding `docs/legacy/`: 3809 files /
   145.8 MB → 3504 files / 62.7 MB" — neither count reproduces at this head, and
   the two sizes mix MB and MiB. Replace with: "Active documentation surface
   `docs/` excluding `docs/legacy/`: 4,207 files / 148.7 MB (141.8 MiB) →
   3,906 files / 65.7 MB (62.7 MiB)."
4. "Live links to moved files repaired: six on the original branch, ten more
   after the Fable review (record 67)." → append "…, and **eight more** in fix
   round 1 (`RUN_STATE.md:7`, `docs/paper/results-fill-registry.md:132`,
   `docs/project_critique_review.html:880`,
   `docs/specs/axi/sb_static_batch_verdict.md:200`,
   `docs/process/model_allocation_ledger.md` ×3, plus the
   `docs/legacy/README.md` row)."
5. "## Verification (2026-09-12, main merged in at 29dbc537, zero conflicts)" →
   "## Verification (2026-09-13; base `a4bb8838`, head `f636f70b`, pushed head
   `59e06abb` = that head merged with `origin/main` `27957b60`, zero
   conflicts)". **The stated diff base must be named as `a4bb8838`**; the body
   currently names no base, and the fix-round delta is
   `git diff -M ae5b09e7..HEAD`.
6. "Full-suite replay on this tree (29dbc537 …) … `REPLAY_RC=0`" — true of the
   pre-fix-round tree only. Append: "Fix round 1 (`8727a84c`, `60e40e5d`,
   `f636f70b`) is docs-only plus the one `git mv`; re-verified at `f636f70b`:
   `tests.test_docs_freshness` + `tests.test_gen_state` → `Ran 75 tests … OK`,
   `gen_state.py --check` rc 0, `git diff --check a4bb8838..HEAD` rc 0."
7. Decision 3: "`docs/paper/**` still carries eight dangling old-path lines
   (`results-fill-registry.md`, `draft-v1-review-round2-lensA.md`)" →
   "`docs/paper/**` still carries five dangling old-path lines, all in
   `draft-v1-review-round2-lensA.md` (lines 30, 41, 52, 62, 125), which is a
   dated `claude-codex-report/v1` review record; `results-fill-registry.md:132`
   was repaired in fix round 1."
8. Decision 2 remains accurate as written.

## What the magistrate should double-check

The SF-1/SF-2 pair is a bench-sized edit (three lines in two files), below the
delegation threshold. If it is applied, `docs/legacy/README.md` needs no change
(no file moves), and the counts in §5 stay exact.
