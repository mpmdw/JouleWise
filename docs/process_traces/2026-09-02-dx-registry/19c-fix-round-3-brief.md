ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: ["scripts/check_paper_round7_artifacts.py","tests/test_paper_round7_artifacts.py"]
GENRE: implementation
EFFORT: high
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FIX ROUND (Opus counter-review SF2 + NIT3 + NIT4) — dx lane, worktree `/Users/edr/code/JouleWise-wt-dx` @ 73f7fcc2

Branch `feat/2026-09-02-dx-registry`. Linked worktree: do NOT commit (the
magistrate commits); never `git checkout/stash/rebase`; never canonical
`unittest discover`. Tests: `python3 -m unittest tests.test_paper_round7_artifacts`
— NOTE the corpus-gated replay class fires on this machine and costs ~8 min;
run the non-replay classes first
(`RegistryAndDigestTests RefusalTests TypedArtifactCliTests InvocationTests`,
prefixed `tests.test_paper_round7_artifacts.`), then the full module once at
the end. Do NOT edit `docs/paper/results-fill-registry.md` (bench-only) or
any file outside WRITE_SCOPE. The Opus report is at
`/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/out/opus-6-dx.md`
(read-only, outside the repo).

## SF2(a) — the fence contract does not say the printed path is RESOLVED
`scripts/check_paper_round7_artifacts.py:13-15,20` says "names the missing
path" / `<path>`. The implementation resolves `args.corpus_root` (`:978`)
before constructing the path, so the printed path is the resolved one
(symlinks followed — `/var/…` prints as `/private/var/…` on macOS). CLOSURE:
at `:20` change `<path>` to `<resolved path>` and add one sentence: "The
path is printed after `Path.resolve()`, so a consumer must compare against
the resolved form of what it passed, never the as-given argument."

## SF2(b) — producer-exit-3 branches put a multi-line MESSAGE after the prefix
`:888` and `:915` raise `ArtifactsUnavailable((stdout+stderr).strip() or
str(corpus_root))`. If a producer prints more than one line before exiting
3, `R7F CORPUS UNAVAILABLE:` is no longer the last line and the last-line
contract (`tests/test_paper_round7_artifacts.py:831-837`) stops describing
reality. CLOSURE: flatten the producer text with the `_producer_failure`
idiom (`:824-827`: strip, splitlines, join with " | ") before raising — one
helper used at both sites; then the R7F line is single-line by construction.
REGRESSION: a test in `TypedArtifactCliTests` (or a new small class) that
runs the fence with a stub producer that prints TWO lines and exits 3 — the
existing tests already show how the producers are substituted (find the
mock/stub pattern in the module; if the producers are only substitutable
via the retained-corpus path, stub the module function that runs them with
`mock.patch`) — and asserts (1) exit 3, (2) the LAST stdout line starts
with `R7F CORPUS UNAVAILABLE: ` and contains both producer lines joined by
` | `, (3) no `COMPARED` line. Counterfactual you must EXECUTE: with the
flattening removed the assertion (2) fails; restore; paste both runs.

## NIT3 — corpus root has no env override
`tests/test_paper_round7_artifacts.py:39` `CORPUS_ROOT = Path("/Users/edr/code/JouleWise")`
while `REGISTRY_PATH` two lines above honours `R7F_REGISTRY`. CLOSURE:
`CORPUS_ROOT = Path(os.environ.get("R7F_CORPUS_ROOT", "/Users/edr/code/JouleWise"))`
and a module-docstring sentence: "`R7F_CORPUS_ROOT` overrides the corpus
root; point it at a directory without the corpus to skip the ~8-minute
replay locally." Executed check: `R7F_CORPUS_ROOT=$TMPDIR/nocorpus python3
-m unittest tests.test_paper_round7_artifacts` must SKIP the replay class
(paste the `skipped=` tail). Do NOT touch `scripts/test_timings.json`.

## NIT4 — docstring overclaims the registry as the single field-path source
`:3-5`. DX-021's render rule discards the row's third declared ref (`:456`)
and reads `AQ#summary.population_size` (`:466`), which the row does not
declare. CLOSURE (docstring only — no behaviour change): after "single
source of digest, field-path, rendering, and row-value truth" add "(render
rules may read additional artifact fields they name explicitly, as
`derived_refused_counts` reads `AQ#summary.population_size`)".

## Out of scope — do not touch
Opus SF1 (placement-dependent tail pins in `fill-checklist.md` and the
181/184 assertions) is DEFERRED by the magistrate to the DX fill-batch
brief; NIT1 (identity supplier fields untyped) and NIT2 (list elements
untyped) are recorded as D-161 prune. Leave those assertions as they are.

## Report
claude-codex-report/v1 envelope; `## Clause map` (header
`| Ruling quote | Production site | Biting assertion | Counterfactual |`,
one row for SF2(b) with the executed counterfactual; doc-only rows `NOT
PINNED: doc-only`); `## Executed evidence` with: the non-replay classes'
tail, the full-module tail with the corpus present, the `R7F_CORPUS_ROOT`
skip tail, the SF2(b) mutant run + restore, `python3
scripts/check_paper_round7_artifacts.py --literals-only` tail (must still
read `R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`), `git diff --stat`.
Do not end the turn before every item is done or returned NEEDS_RULING.
