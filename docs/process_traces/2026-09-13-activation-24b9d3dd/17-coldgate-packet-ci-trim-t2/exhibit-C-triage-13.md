# 13 — Lead triage, review round 1 on PRs #317 (CI-TRIM-01) and #329 (DOCS-THIN-01)

Activation `c5048879`, 06:02 PDT 2026-09-13. Inputs: Astra execution lens 04
(#317) and 06 (#329); Opus contract lens 07 (#317) and 09 (#329); the lead's
own diff-gate read of `.github/workflows/ci.yml` (05:57). Authority for the
content: Ed's 2026-09-12 reply "both pr's accepted as proposed" (Gmail
`1a0969ba0b31c2b2`) on the two draft decisions each PR body posed.

**Baseline correction (both lenses, both PRs).** The briefs said origin/main
`27957b60` had been merged into the PR heads; the merges (05:47) took
`a4bb8838`, two minutes before H landed. Every lens noticed and re-based on
`a4bb8838`; the "blocker" F1 in record 06 and flag F1 in record 04 are this
misstatement, not defects. The final heads merge main again before the gate
closes; the integration replay already runs on `27957b60` + both heads.

## PR #317 — dispositions

| Finding | Source | Severity | Disposition |
|---|---|---|---|
| Queued run eviction: a docs push replaces a QUEUED code push in the same concurrency group even with cancel-in-progress off; the docs push then classifies `B..C` docs-only and skips the matrix | 04 R1 (blocker), 07 §4 (should-fix at ≥3 pushes) | blocker | FIX-1: per-run group for `push`, ref group for PRs |
| Docs-only runs skip the 48 test modules that assert on Markdown under `docs/` and the root docs (paper term lint, first-use ledger, claims lint, identity pins, the watchdog reaper block that `test_magistrate_watchdog` `exec`s out of `MAGISTRATE_WATCHDOG.md`) | lead diff gate D1; 07 §3 (blocker) | blocker | FIX-2: runtime-derived `docs-readers` job, two shards, runs only when the matrix does not |
| Whole-job failure of `changes` silently skips dependents | 04 residual risk | should-fix | FIX-3: `!cancelled() && code != 'false'` on the gated jobs |
| `pr_fast_tier` in `scripts/test_timings.json` is dead config; decision-log addendum retiring TEST-SPEED-01 lever 2 and narrowing "merges keep the full suite" to code-touching merges is owed | 07 §1 | should-fix | NOT this PR: the addendum records an owner ruling and goes to Ed/the cold gate (rule 11); the dead config is a follow-up nit — both listed in the PR body |
| Kernel fence cites D-061 for "zero deletions" but that phrase lives in D-101 addendum II | 07 §1 | nit (pre-existing) | noted; not this PR |
| Comment says ~1.6 min, body says 1.4 | 07 §2 | nit | FIX-5 |
| Trailing whitespace `ci-trim-01-seat-astra.md:194` | 04 R2 | nit | lead bench edit after the seat exits |

Design note on FIX-2 (the lead's call, both lenses consulted): Opus proposed an
extension/directory allowlist; the lead chose the runtime-derived module set
because the hazard is "a test reads this file", which only the test sources
know, and a derived list cannot go stale (the same principle the deleted
`pr-fast` job used). Cost at the bench: 48 modules ≈ 23 hosted minutes on one
runner, ≈ 12 on two shards — against ≈ 190 runner-minutes for the full matrix.

## PR #329 — dispositions

| Finding | Source | Severity | Disposition |
|---|---|---|---|
| Runtime readers, contracts, kernel, magistrate/courier docs: zero moved paths referenced | 06 §"no archive-caused runtime blocker", 09 §1–2 | — | clean |
| `RUN_STATE.md:6-9` cites `RESUME-2026-07-27/28` at their old paths; `RESUME-2026-07-26` stayed live while its siblings moved | 09 §3 (should-fix + nit) | should-fix | FIX-1: archive the sibling, add its README row, repair the sentence |
| Live pointers still old: `docs/paper/results-fill-registry.md:132`, `docs/project_critique_review.html:880`, `docs/specs/axi/sb_static_batch_verdict.md:200` | 06 F2, 09 §5 | should-fix | FIX-2 (registry line only if no test pins its bytes) |
| Six added lines with trailing whitespace | 06 F4 | nit | FIX-3 |
| Historical records keep old links by policy (`docs/legacy/README.md:16`) | 06 F3 | nit | accepted as designed |
| `tests/test_docs_freshness.py` exclusion: no ratified guarantee narrows (docstring already scopes out dated history) | 09 §5 | — | no addendum |
| PR body names base `29dbc537` | 09 nit | nit | lead updates the body |

## Round 1 launches

- 08 → seat 11: #317 fix round 1, Astra high, `WRITE_SCOPE
  [".github/workflows/ci.yml"]`, in `JouleWise-wt-ci-trim`.
- 10 → seat 12: #329 fix round 1, Astra high, enforced eight-path scope, in
  `JouleWise-wt-docs-thin`.
- Replay 1 on the integration tree `JouleWise-wt-integ-c5048879` (27957b60 +
  f5f2403e + ae5b09e7) is running; a second replay at the final heads follows
  the fix rounds. Delta re-audits of both rounds follow (adversarial-review
  §C-028).
