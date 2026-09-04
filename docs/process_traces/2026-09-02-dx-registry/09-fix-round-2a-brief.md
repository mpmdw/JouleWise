ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: ["scripts/check_paper_round7_artifacts.py", "tests/test_paper_round7_artifacts.py", "docs/paper/round7/fill-checklist.md", "scripts/paper_anchor_correction_quantified.py"]
GENRE: implementation
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FIX round 2a — round-7 artifact fence (branch feat/2026-09-02-dx-registry @ 3f1677b7)

LINKED WORKTREE `/Users/edr/code/JouleWise-wt-dx`. Do NOT commit/rebase; never
canonical `unittest discover`; the magistrate commits. `runs*/` are immutable
corpora — read only. `docs/paper/draft-v1.md` is byte-frozen — never open it
for writing. `docs/paper/results-fill-registry.md` is NOT in scope: if a
closure needs a registry row change, return NEEDS_SCOPE naming the row.

AUTHORITY: Opus 5 counter-review (report 207) of the fence after fix round 1
(Sol 191, terra 198 delta). This round takes the findings that are FIRST-ROUND
at their sites. Two items are deliberately EXCLUDED and must not be touched:
S1 (type-laxness at `_decimal`/`_comparison` — under cold gate as a second
round on round-1's int-truncation class) and S2 (placement census — under
cold gate as a scope question). Apply the dictated closures exactly;
anything that does not fit → NEEDS_RULING.

## Dictated closures

F-A (B1, blocker). `scripts/check_paper_round7_artifacts.py:799-804`: on
`ArtifactsUnavailable` the script prints `R7F CORPUS UNAVAILABLE: <path>`
FIRST, then 181 `ok` lines, then the final line `R7F COMPARED 181 /
MISMATCHES 0`, exit 3 — byte-identical final line to `--literals-only`
success. Closure, mirroring `scripts/check_paper_replay_fence.py:568-576`
(RF's shape): the unavailable branch prints its `R7F CORPUS UNAVAILABLE:`
line LAST and prints NO `COMPARED` line; `--literals-only` prints
`R7F LITERALS-ONLY COMPARED n / MISMATCHES m` (distinct token); the full
replay alone prints `R7F COMPARED n / MISMATCHES m`. Also `:774`: the
`--corpus-root` default is a hardcoded absolute path — default to the
repository root argument (or `Path(__file__).resolve().parents[1]`) so CI
and other machines do not silently take the exit-3 path by default. Update
`docs/paper/round7/fill-checklist.md:24-25` to require the exact successful
tail `R7F COMPARED 184 / MISMATCHES 0` (pin n = 184 and say the 181-count
literals-only tail is NOT sufficient before a fill batch). Tests: rewrite
`test_absent_corpus_exits_three_and_names_path` (`tests/…:329-341`) to assert
the final line is the UNAVAILABLE line and that no `COMPARED` line is
printed; add a literals-only test asserting the distinct token.

F-B (B2, blocker). `:600-603` `observed = suffix[: len(expected)]` is a prefix
match — `[FILL:DX-020] 150 captures` passes as `15`. Closure: after the
marker, the literal is either the backticked form (exact, unchanged) or a
bare form that must be followed by end-of-line or a non-alphanumeric,
non-`.`, non-`%` delimiter; any other continuation is a MISMATCH naming the
observed continuation. Drop the speculative `("=", ":", "→", "—")` stripping
at `:595-596` (no checklist placement form uses them). Tests: the three
counterfactuals `[FILL:DX-020] 150 captures`, `[FILL:DX-012] 59 of 599 pulses`,
`[FILL:DX-026] 4.05 %%%` each → MISMATCH; exact forms still pass.

F-C (S3, should_fix). `:711-714`, `:739-742` classify producer failures as
corpus absence by lowercase substring sniffing of the output. Closure: XS —
rely on `returncode == 3` only (XS returns 3 on unavailable population at
`scripts/paper_excursion_decomposition.py:800-802`); AS — in
`scripts/paper_anchor_correction_quantified.py` `main` (`:714-734`) catch
`PopulationUnavailable`, print `population unavailable: <path>` to stderr,
and `return 3`; the fence then tests `returncode == 3` for AS too. Any other
non-zero return is `_producer_failure` (exit 2, traceback text in the
message). Remove the substring sniff entirely. Test: AS raising
`FileNotFoundError` on its `--out` parent → fence exit 2 with a producer
failure line, NOT exit 3.

F-D (N1). `check_figure:534-537,573`: guard `pulses[index]` being a dict
with the value key; refuse via the same path `check_rendered_rows:484` uses
(a REFUSED comparison, exit 2) instead of a `TypeError` traceback (exit 1).
Test: a per_pulse entry that is a string → exit 2, no traceback.

F-E (N3 + Q5 deletion). The `source_sha256_*` renderer (`:404-408`) is
tautological given `parse_registry_text:276-280`; delete it and let the
identity rows be checked solely by `check_file_pins:307`; adjust the census
accordingly and pin the new counts (full replay and literals-only) in the
tests and the checklist line from F-A.

F-F (N4). Hardcoded English `(all anchor_unresolved)`, `(both refused_by_v3)`
at `:445,:456` and the `len(failures) != 1` assumption at `:463-464`: render
"all"/"both"/count-aware wording FROM the observed counts (e.g. `both` only
when the count is 2, `all` only when bucket == refused) and keep the
comparison exact against the marker; the singularity assumption becomes a
REFUSED comparison naming the count, not a silent shape.

F-G (N2). `check_gates:493-506` hardcodes three gate paths. Closure: keep
the check but derive the gate list from a module-level table that names,
per gate, the DX row (or `ungoverned`) it belongs to, and add a test that
every entry with a DX row exists in the parsed registry; the two
`XD#calibration_gate.*` entries are marked `ungoverned` with a comment. (No
registry edit this round.)

F-H (N5). `F4_REPLAY_COMMAND` is asserted as text but the replay runs a
different argv. Closure: build the replay argv FROM the pinned command
string (split, substitute the temp `--out`/`--svg` and the repo root) so a
drift between the pinned command and what XS accepts fails the replay.

## Mutation check (report each: KILLED by <test> / SURVIVED)

M1 restore the COMPARED line on the unavailable branch → must be KILLED.
M2 restore `suffix[: len(expected)]` → KILLED by the F-B tests.
M3 restore the substring sniff and make AS raise FileNotFoundError → KILLED.
M4 remove the per_pulse dict guard → KILLED.
M5 in F-H, change the pinned command's `--repository-root` flag name → the
replay must fail (KILLED by the existing replay test or a new one).

## ACCEPTANCE

- `python3 -m unittest tests.test_paper_round7_artifacts tests.test_paper_replay_fence tests.test_docs_freshness` — paste tails (the round7 module takes ~8 min; run it once at the end).
- `python3 scripts/check_paper_round7_artifacts.py --literals-only; echo EXIT=$?` and the full `python3 scripts/check_paper_round7_artifacts.py; echo EXIT=$?` — paste the last 3 lines of each; and `--corpus-root /nonexistent; echo EXIT=$?` → last line is the UNAVAILABLE line, EXIT=3.
- `git status --porcelain` shows only in-scope files; `git diff --stat -- runs* docs/paper/draft-v1.md` empty.
- Same-signature statement over Opus 207's B1, B2, S3, N1–N5 (S1/S2 excluded by ruling): KILLED / what remains.
- `## Clause map`: one row per closure F-A…F-H — production site `file:line`, biting test `file:line`, counterfactual.

## VERIFICATION
`git diff --stat` in the report; nothing outside WRITE_SCOPE touched.
