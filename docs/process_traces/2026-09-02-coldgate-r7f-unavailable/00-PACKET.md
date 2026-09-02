# Cold-gate packet — R7F `CORPUS UNAVAILABLE` docstring grammar, 2026-09-02 (session 540125d5)

Mandatory trigger (charter §3 item 1: a second fix round on the same
defect). Branch `feat/2026-09-02-dx-registry` @ `74fb5206`, PR #272, the
round-7 paper-artifact fence `scripts/check_paper_round7_artifacts.py`.

The SAME docstring sentence — what follows `R7F CORPUS UNAVAILABLE: ` on the
fence's last stdout line when it exits 3 — has been found wrong by three
consecutive reviewers, each after a cure:

| Round | Reviewer (file) | Finding on the sentence | Cure applied |
| --- | --- | --- | --- |
| 1 | Opus counter-review, `../2026-09-02-dx-registry/19-opus-counter-review.md` (SF2(a), around `:146-167` and `:267`) | says `<path>` without saying the path is RESOLVED | luna 237 (commit `7fc87a7f`): `<resolved path>` + "printed after `Path.resolve()`" sentence |
| 2 | terra 239 delta re-audit, `../2026-09-02-dx-registry/20-terra-239-delta-3.md` | `<resolved path>` is false for the two producer-exit-3 branches, which print the producer's flattened output | magistrate bench (commit `9be7a229`): `<detail>` = preflight resolved path OR producer output flattened with ` \| ` |
| 3 | Sol 240 final-head fresh pass, `../2026-09-02-dx-registry/21-sol-240-fresh-pass.md` | the helper falls back to `str(corpus_root)` when the producer printed nothing, so "producer output" is not exhaustive either | NONE — this gate |

The magistrate has NOT edited the sentence since round 3 and has NOT amended
anything. Read-only. Repo worktree: `/Users/edr/code/JouleWise-wt-dx` @
`74fb5206` (no seat is running there; if `git status --short` is non-empty,
read committed bytes with `git show 74fb5206:<path>`). Write NOTHING under
it; TMPDIR = a subdirectory you create under
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/`.
Python: `/Users/edr/code/JouleWise/.venv/bin/python` (or `python3`). Do NOT
launch any codex/claude process. Do NOT run canonical `unittest discover`;
the module `tests.test_paper_round7_artifacts` costs ~8 min because of a
retained-corpus replay class — run only the classes `TypedArtifactCliTests`
and `InvocationTests` if you need to execute anything.

Charter: `docs/process/coldgate_charter.md` — expected sha256
`099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` (verify
with `shasum -a 256`; if it differs, say so in your disclosure and stop).
Read §3–§5 and §8 before anything else. Charter §4 read set: ONLY this
packet, the excerpt files in this directory, the three reviewer files named
above, and the primary code/test files at `74fb5206` — no narrative
process/state docs (README.md, RUN_STATE.md, TASK_QUEUE.md,
docs/orchestration.md, docs/agent_playbook.md, MAGISTRATE-NOTES.md,
`*-disposition-*.md`), no CLAUDE*.md doctrine, no memory files. Disclose any
contamination (anything you read outside the set, or prior context).

## Packet (read all, in this order)

1. This file, §Question and §Facts.
2. Excerpts in this directory, all cut mechanically with `sed -n` from the
   named revision (re-cut them yourself if you doubt any):
   `docstring-73f7fcc2.txt` (`:12-20`, before round 1),
   `docstring-7fc87a7f.txt` (`:12-27`, after round 1),
   `docstring-74fb5206.txt` (`:12-31`, current),
   `helper-74fb5206.txt` (`_producer_unavailable_message`, `:841-846`),
   `preflight-74fb5206.txt` (`replay_half` preflight, `:878-884`),
   `xs-site-74fb5206.txt` (`:900-907`), `as-site-74fb5206.txt` (`:929-936`),
   `main-handler-74fb5206.txt` (`:1008-1015`),
   `test-multiline-74fb5206.txt` (`tests/test_paper_round7_artifacts.py:600-623`),
   `test-absent-corpus-74fb5206.txt` (`:850-865`).
3. The three reviewer files (table above), the SF2/UNAVAILABLE parts only.
4. Primary code, read-only: `scripts/check_paper_round7_artifacts.py` and
   `tests/test_paper_round7_artifacts.py` at `74fb5206`; the two producers'
   exit-3 sites `scripts/paper_excursion_decomposition.py:798-802` and
   `scripts/paper_anchor_correction_quantified.py:718-723` (both print one
   line to STDERR — `artifacts unavailable: …` / `population unavailable: …`
   — before `return 3`).

## Question

**Q1 (rule the cure shape, once).** Three consecutive patches to one
docstring sentence have each been true for one branch and false for
another. Rule ONE of:

(a) DOCUMENT the code as it is: the detail after the prefix is exactly one
    of three things — (i) the resolved path of the first required corpus
    file the preflight finds absent (`:881-883`), (ii) the producer's
    stdout+stderr stripped and flattened with ` | ` when a producer exits 3
    with output (`:841-846`, `:904-905`, `:933-934`), (iii) the resolved
    corpus root when a producer exits 3 with NO output (`:846`). State the
    operative sentence(s).

(b) SIMPLIFY the code so that a shorter grammar is true: e.g. the helper
    always returns `f"{corpus_root}: {flattened output or 'no output'}"`
    (two branches: preflight path, or corpus root + producer text), or the
    detail is ALWAYS the resolved corpus root and the producer text goes on
    its own preceding stdout line. State the operative code shape, the
    operative docstring, which existing assertions change
    (`test-multiline-74fb5206.txt:619-621`, `test-absent-corpus-74fb5206.txt`)
    and the biting counterfactual.

(c) Something better, or UNRULED with the reason.

Also rule, separately labelled: **Q1-consumer** — is there any consumer of
the last line other than the two tests and a human reading the log (grep
the repository for `CORPUS UNAVAILABLE`), and does your Q1 answer preserve
what each consumer asserts? And **Q1-scope** — does the cure belong in this
PR (docstring-only or code+test), or is the docstring left as (a) in this
PR and a code simplification registered for later? Note the threat model in
force (D-161, `docs/decision_log.md`, `grep -n '^### D-161'`): the adversary
is not the operator; the fence exists against re-issued artifacts and
honest producer drift, not forgery — an exit-3 line is a diagnostic for a
human, not a claim-bearing number.

Deliverable: a sealed ruling for Q1 (with Q1-consumer and Q1-scope), each
with verdict (ADOPT (a)/(b)/(c) / UNRULED with reason), the operative text
or code shape, the biting counterfactual, and what it does NOT decide. Under
charter §8, disclose contamination and the charter digest first.

## Facts (bench-verified by the magistrate 2026-09-02; re-verify any you rely on)

F1. `_producer_unavailable_message(completed, fallback)` at `:841-846`
    returns `" | ".join(lines)` when `(stdout+stderr).strip().splitlines()` is
    non-empty, else `str(fallback)`; both call sites pass `corpus_root`
    (resolved by `main` at `:998`, `(args.corpus_root or repository_root).resolve()`)
    as `fallback`.
F2. The preflight at `:881-883` raises `ArtifactsUnavailable(str(path))`
    for the first absent required corpus path; `path` derives from the
    resolved `corpus_root`.
F3. `main` at `:1011-1014` prints `R7F CORPUS UNAVAILABLE: {exc}` and returns
    3; nothing else prints that prefix. Repository census of the string
    outside process traces (`grep -rn "CORPUS UNAVAILABLE" scripts tests docs
    .github`): `scripts/check_paper_round7_artifacts.py:24`, `:1013`;
    `tests/test_paper_round7_artifacts.py:424`, `:619`, `:859` — five
    sites, nothing under `docs/` or `.github/`.
F4. Both real producers print exactly one stderr line before `return 3`
    (packet item 4), so branch (iii) of (a) is reachable only through a
    producer that exits 3 silently — none in the repository today.
F5. `test-multiline-74fb5206.txt`: the regression stubs `_run_producer` with
    a two-line stdout and exit 3, asserts exit 3, last line starts with the
    prefix and contains `producer line one | producer line two`, no
    `COMPARED` line. `test-absent-corpus-74fb5206.txt`: a missing corpus root
    yields the exact resolved path of `…/instrument_evidence.json` as the
    last line.
F6. Sol 240 executed the full module at `9be7a229`: `Ran 45 tests`, `OK`;
    `--literals-only` tail `R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`.
F7. Charter digest at the worktree: `099de884…` (recompute yourself).
