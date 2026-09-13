# Cold-gate packet — CI-TRIM-01 T2 (PR #317): may a docs-only push skip the test matrix, and by what mechanism? (rule 11: second fix round on one defect; two rounds, same signature)

Assembled 2026-09-13 ~06:40 PDT by the resident magistrate (activation 24b9d3dd). Mechanically assembled: every exhibit is a verbatim copy of a seat or refuter report, a `git diff`, or a `git show`/`gh` extract; the magistrate wrote only this file and the two triage records (Exhibits C and H), which are its own dispositions and are marked as such.

## What happened

PR #317 (CI-TRIM-01, branch `chore/2026-09-10-ci-trim`, base `a4bb8838`, head after fix round 1 `8819cb5f`) proposes four things for `.github/workflows/ci.yml`: T1 hoist the once-per-run fences into their own job; T2 a pure-git `changes` detector that classifies a push as "docs-only" (Markdown under `docs/` and top-level `*.md`) and, when so, SKIPS the four-shard × two-Python test matrix and both exclusive jobs; T3 delete the `pr-fast` job; T4 guard the zsh install. The owner accepted the PR's two posed decisions (keep the 3.14 matrix half; delete `pr-fast`) "as proposed" (Exhibit K).

Round 0 review (Exhibits A, B): the Opus contract lens found a BLOCKER — 23 (later counted 48) test modules assert on Markdown content (the sharpest case: `tests/test_magistrate_watchdog.py` extracts a fenced Python block from `docs/process/MAGISTRATE_WATCHDOG.md` and `exec`s it), so a docs-only push that breaks a documented mechanism goes green. Fix round 1 (Exhibits D, E): a `docs-readers` job whose module set is derived at run time by a regex over test sources for quoted `docs/`/root-doc literals, run only when the matrix is skipped. Delta re-audits (Exhibits F, G): both lenses BLOCK again with the same signature — 15 further docs-asserting modules are missed because they reach documentation through `Path` joins or imported constants, one exclusive module (`tests/test_calibration_exits`, per Exhibit F; Exhibit G disagrees that any exclusive module reads docs — a split the judge should resolve from the file) is excluded by construction, and the root-doc names are a checked-in list. Exhibit G adds that the kernel fence TEST-SPEED-01 ("merges … keep the full suite") is made false on main by the merge itself, so a ruling on the narrowing must precede the merge.

The magistrate escalated (Exhibit H) instead of running round two, and convened two blind design seats (Exhibits I, J). Both recommend option A. Their executed counterexamples against a runtime-traced reader map (option B): reads through subprocesses (`tests/test_paper_build.py:95` runs `docs/paper/build/check_markdown.py`, which reads the draft), reads through `git show`/git objects, and files that do not yet exist at trace time are invisible to an `open()` audit hook; the fail-closed repair (treat every module with any untraceable read as a reader) pulls in 120 of 230 modules, about 66 % of suite seconds, so the saving collapses to roughly a third of the matrix cost against a build the seats estimate at several seat-days plus permanent maintenance of a map.

Arithmetic on the table (from the exhibits, not re-measured by the magistrate): full matrix ≈ 190 runner-minutes per push; a docs-only run under the PR ≈ 1.5 (fences) + ≈ 24.5 measured for the current `docs-readers` (Exhibit G Q4); under option A every push costs the full matrix, as today.

## Q1 — the mechanism (rule one option, or write a better one)

- (A) No path-based skipping. Delete the `changes` job, the `docs-readers` job and the `if:` guards on the matrix and exclusive jobs; keep T1 (fences job), T3 (`pr-fast` deletion), T4 (zsh guard) and FIX-1 (per-run concurrency group for pushes, ref group for PRs). The PR lands smaller than proposed; every push runs the full suite, as the kernel fence says today.
- (B) Skip with a runtime-traced reader map regenerated and checked on every code-touching run (Exhibit H states it; Exhibits I and J refute its completeness).
- (C) Skip with the docs class narrowed to paths a trace proves no test reads (converges with B).
- Other: the judge may rule a mechanism the seats did not consider, with the same burden — a stated proof that no docs-asserting test can be skipped, or an explicit, owner-visible acceptance that some can.

Deliver: the ruled option; for A the exact list of YAML deletions (job ids and `if:` lines by line number in Exhibit E's post-image) and what must stay; the reason grounded in the exhibits.

## Q2 — the kernel fence and the addendum (process rule; the magistrate may not decide this)

TEST-SPEED-01's fence (Exhibit K) says merges, whole-window verdicts and audited heads keep the full suite, and its goal names an Ed-ratified "PR-fast/full tier split". Rule the following: (a) under option A, is any narrowing of the fence needed at all? (b) `pr-fast` is deleted by this PR under the owner's explicit acceptance — is a decision-log addendum retiring TEST-SPEED-01 lever 2 (the fast tier) REQUIRED BEFORE the merge, or may it follow as bookkeeping, and what is its exact text (one paragraph, dated, citing Exhibit K's acceptance)? (c) the dead `pr_fast_tier` block in `scripts/test_timings.json:6-13` — in this PR, a follow-up, or leave it?

## Q3 — for the record

Was the magistrate's escalation after delta 07/08 (Exhibit H) the correct application of the standing trigger (two consecutive rounds, same signature), given that Exhibit G proposes a one-line regex widening (48 → 63 modules) as a "bench-sized" cure? One paragraph: is a third static widening a round three of the same class, or a bench fix?

## Constraints on the judge

Read-only. Probes allowed: `git show 8819cb5f:<path>`, `git show a4bb8838:<path>`, `git diff`, `grep`/`rg`, `sed -n`, running the `docs-readers` selection Python locally (never the test suite), `gh pr view 317` reads if available. Do not edit any tracked file. Never touch `/Users/edr/code/JouleWise` (its `.venv/bin/python3` may be used read-only for PyYAML), any `/Users/edr/JouleWise-measurement-*` directory, or `/Users/edr/night-custody`. The PR branch is checked out read-only at `/Users/edr/code/JouleWise-wt-ref-317` (HEAD `8819cb5f`). Ruling file: `10-coldgate-fable-ruling.md` in this packet directory — sections: Contamination disclosure; Q1 (ruled option; exact YAML deletions/keeps; reason); Q2 (a)(b)(c) with the addendum text verbatim in a fenced block; Q3; Executed probes. Plain words; define each term at first use.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
72965483abac004f3bfd1038e91e104a9f3ea4f0ba7cd2c9526fd1d4c6d06852  exhibit-A-round0-execution-astra-04.md
a6f12c55fde82f00f6810d5e3e7ddb97316f039595da702a045ee32ab96d37c6  exhibit-B-round0-contract-opus-07.md
0da0cbd4db1ca5627a98e2b35d85be45ec754c7b6f7b699977240c3b5c357687  exhibit-C-triage-13.md
05f9bfa2598b2c64aef525aa9982b1aa8a54a0cfd7f47373024289a0286fdfb5  exhibit-D-fix-contract-08.md
2f5c25496abb27a60366e0d0e6ff790f4f162fa5b25c540b60d44c9615608226  exhibit-E-fix-round-1-diff.md
4afd998433b7129c475e9e41bc9f159c59ef388e76407dded8d9fe48976ef431  exhibit-F-delta-execution-astra-07.md
9d90c4275e1eb484bb97550e89a4cf8e56bd72d0f73fef60f3a133042a2b68c1  exhibit-G-delta-contract-opus-08.md
d1df15b46b2b5d113379bfbcb12e2a868789a765f2ebd0a42c92fbab3cd0a54c  exhibit-H-triage-12.md
23ae70e19385204a3393758c4207966c08344bec9730c6ff629a59e4423d5e5d  exhibit-I-design-astra-xhigh-14.md
29f9274586b136f77cde2af41e0d89cee0a77c9d59213620791477babfd1307a  exhibit-J-design-opus-15.md
29338d702e7df7f29583f141918a57cddf86a5f4445e9b0ef48289433cab35c2  exhibit-K-governing-text.md
```
