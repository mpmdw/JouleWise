ORIGIN: claude-code (Fable magistrate, JouleWise loop)
HOP: 1
WRITE_SCOPE: ["scripts/check_paper_round7_artifacts.py", "tests/test_paper_round7_artifacts.py", "docs/paper/round7/fill-checklist.md"]
GENRE: implementation
EFFORT: xhigh
TMPDIR: use the exported TMPDIR (a scratchpad subdir); never /tmp.

# FIX round 2b — round-7 artifact fence (branch feat/2026-09-02-dx-registry @ 781c8d78)

LINKED WORKTREE `/Users/edr/code/JouleWise-wt-dx`. Do NOT commit/rebase; never
canonical `unittest discover`; the magistrate commits. `runs*/` are immutable
corpora — read only. `docs/paper/draft-v1.md` is byte-frozen — never open it
for writing. `docs/paper/results-fill-registry.md` and
`docs/paper/draft-v2-skeleton.md` are OUT of scope (read them; never edit).
Run tests as `python3 -m unittest tests.test_paper_round7_artifacts`; the
literals-only fence as
`python3 scripts/check_paper_round7_artifacts.py --literals-only; echo EXIT=$?`
(expected tail today `R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`, plus
the new `R7F PLACED 0/16` line — see A2). Do NOT run the full replay (the
magistrate runs it at the bench; it needs the retained corpus).

AUTHORITY (read first, in this order; these live on main, NOT on this
branch — read them from the main checkout at the absolute paths given,
read-only):
1. `/Users/edr/code/JouleWise/docs/process_traces/2026-09-02-coldgate-dx-t26a/MAGISTRATE-RULING-coldgate-dx-t26a.md`
   §A1 and §A2 — DICTATED code shapes; apply verbatim. Also its dated
   addendum at the end of the file (site correction for `check_figure`).
2. `/Users/edr/code/JouleWise/docs/process_traces/2026-09-02-coldgate-dx-t26a/seat-cold-fable-220.md`
   §A1 — the reference `_typed` resolver and regression table.
3. `/Users/edr/code/JouleWise/docs/process_traces/2026-09-02-coldgate-dx-t26a/207-opus-counter-review.md`
   — for the P1/P2/P3 CLI regression inputs.
Current code: `scripts/check_paper_round7_artifacts.py` (880 lines; sites
below are at 781c8d78 — RE-AUDIT every line number before editing and record
the true ones in the clause map), tests (31 tests).

## Dictated closures

F-1 (ruling A1.1 — loader). `load_json_artifacts:340` and the AQ read in
`_required_corpus_paths:692`: `json.loads(text, parse_float=Decimal)`. No
`float` object from an artifact ever reaches a renderer or comparison.

F-2 (ruling A1.2 — comparison). `_comparison:168`:
`match = type(expected) is type(observed) and expected == observed`.
Audit every existing `_comparison(...)` call whose `expected`/`observed`
could legitimately differ in type but mean the same thing (e.g. a `Path` vs
`str`, an int count vs a Decimal) and normalise at the CALL SITE to one type —
never by weakening `_comparison`. List each such site in the clause map.
Regressions: `_comparison("x", True, 1)`, `("x", True, 1.0)`, `("x", 1, 1.0)`
all `match is False`; `("x", Decimal("1"), Decimal("1.0"))` is `True`
(Decimal equality is numeric — ruling P4: JSON `4` where a float is expected
is ACCEPTED by design; note `parse_float` only produces Decimal for tokens
with a fraction/exponent, so `4` stays `int` and a row rendered from an
`int` compares against an `int` — say in the clause map how P4 survives the
type-strict `_comparison`, with the test that pins it).

F-3 (ruling A1.3 — the ONE resolver). Add
`_typed(value: Any, kind: str, field: str)` with
`kind ∈ ("int", "number", "bool", "str")`:
- `int`: `isinstance(value, int) and not isinstance(value, bool)` → returns
  the int;
- `number`: `int` (not bool) or `Decimal` → returned as `Decimal`;
- `bool`: exactly `bool`; `str`: exactly `str`;
- otherwise `raise ValueError(f"{field}: expected {kind}, found {type(value).__name__}: {value!r}")`.
`_decimal:386` and `_exact_int:402` become thin wrappers over `_typed`
(`_exact_int_field` collapses into `_typed(value, "int", field)`); every
renderer passes its `SRC#path` label as `field`; `check_gates:515` reads
through `_typed(value, "bool", f"{source}#{path}")` and turns `ValueError`
into an observed value `f"REFUSED: {exc}"` (existing MISSING branch kept);
`check_figure` per-pulse read at `:597` (`expected_value = float(pulse[value_key])`)
becomes `_typed(pulse[value_key], "number", f"XD#per_pulse[{index}].{value_key}")`
inside `try/except (KeyError, ValueError)` that appends a REFUSED comparison
and `continue`s; the `failures[0]` read goes through `_typed(..., "str", ...)`.
Regression table (dictated, one test method, subTests): int rejects
`Decimal("15.9")`, `Decimal("15.0")`, `True`, `"15"`, `None`; number rejects
`"4.05"`, `True`, `None`, `[]`; bool rejects `1`, `Decimal("1.0")`, `"true"`,
`None`; str rejects `1`, `True`, `None`; accepts int←`15`, number←`15` and
`Decimal("4.05")`, bool←`True`, str←`"x"`. Each rejection asserts the exact
message shape above.

F-4 (ruling addendum — geometry). The SVG attribute reads at `:565-571`
parse SVG STRINGS (`shape.attrib[...]`), not artifact scalars; they stay
`float(...)`. The tolerance comparison needs one float from the typed
Decimal: do it in ONE named helper `_geometry(value: Decimal) -> float` with
a one-line comment ("tolerance arithmetic only; the rendered literal is the
Decimal"). The `expected=` string of that comparison renders the Decimal
(`f"index={index}, value={expected_value:.6f}"` works on Decimal).
Acceptance grep (addendum-amended):
`grep -n 'Decimal(str(' scripts/check_paper_round7_artifacts.py` → empty;
`grep -n 'float(' scripts/check_paper_round7_artifacts.py` → ONLY the
`shape.attrib` lines, `float("nan")`, and the body of `_geometry`. Paste
both outputs in the report.

F-5 (ruling A1 — CLI regressions P1/P2/P3). Three end-to-end tests through
the production path (`main` with `--literals-only` against a scratch copy of
the registry + artifacts in TMPDIR, the same fixture pattern the existing
end-to-end tests use):
- P1: AQ `max_absolute_pct: "4.046812"` (string) → rc 2, stdout names
  `row DX-026` (or whichever row renders that field — say which) and
  `expected number, found str`;
- P2: XD `calibration_gate.b_fiducial_s_matches_exactly: 1` → rc 2, the
  gate label and `expected bool, found int`;
- P3: XD `per_pulse[0].onset_best_fit_lag_ms: "16.0"` → the figure
  comparison `figure onset mark 0` and `expected number, found str`
  (this one needs the F4 figure check; if `--literals-only` skips the
  figure, run the test through the non-replay path that includes
  `check_figure` — say which entry point and why).
- P4 control: XD scalar written as `4` where the retained artifact has a
  float → PASSES (assert rc 0 on a fixture where the rendered literal is
  unchanged) — or, if no such field exists in the fixture, a unit test on
  `_typed(4, "number", ...)` returning `Decimal(4)` plus a rendered-literal
  equality assertion. Say which.

F-6 (ruling A2 — placement census, in THIS PR). Module constant
`DX_STANDING_SENTENCE_HEAD` = the first clause of the registry's mandatory
standing sentence, byte-exact from `docs/paper/results-fill-registry.md`
(the sentence beginning “The following are diagnostic-era instrument
statistics” — copy it from the file, curly quotes and all; pin its
provenance line in a comment). `check_placement(skeleton_text) ->
list[Comparison]`:
- `n_standing` = count of `DX_STANDING_SENTENCE_HEAD` in the skeleton;
- `n_standing == 0` → one comparison `placement standing sentence` expecting
  `0 [FILL:DX- markers`; any `[FILL:DX-` marker present → MISMATCH naming
  the count;
- `n_standing ≥ 1` → for each of the 16 non-identity rows DX-010..017,
  DX-020..027 (take the ids from the parsed registry, NOT a hard-coded
  list; assert the parsed set has exactly those 16 in a test) a comparison
  `placement DX-nnn` expected `≥1`, observed the marker count; missing →
  `MISMATCH placement DX-nnn: expected ≥1, observed 0`.
- `main` prints `R7F PLACED n/16` (n = rows with ≥1 marker) on its own line
  IMMEDIATELY BEFORE the `R7F … COMPARED` tail, in both modes.
Regressions: (a) skeleton copy with the standing sentence + 15 markers → rc 2
naming the 16th; (b) `[FILL:DX-010] +13.0 ms` with no standing sentence →
rc 2; (c) the current skeleton → `R7F PLACED 0/16`, rc 0; (d) the tail
order (`PLACED` line precedes `COMPARED`).
`docs/paper/round7/fill-checklist.md`: one sentence under the R7F section
stating the census and its `PLACED` line; and ONE sentence stating that
prose placement (rendered literal without its marker inside the DX region)
is NOT covered by R7F until kernel row `R7F-DX-PROSE-SCAN-01` closes (ruling
A2 last sentence — no acceptance row may claim otherwise).

F-7 (M5 re-dictation). `test_bad_repository_root_flag_in_pinned_command_fails_replay`
tests an injected unknown flag, not the dictated mutation. Add
`test_renamed_out_flag_in_pinned_command_is_refused`: patch
`FENCE.F4_REPLAY_COMMAND` with `--out` → `--outt`; `_f4_replay_argv` raises
`ValueError("pinned F4 command must contain exactly one --out")`; through
`replay_half` (with `_required_corpus_paths` patched to `[]`) the single
comparison is `replay F4 command` / mismatch carrying that message. Keep the
existing test.

F-8 (line-number audit). Sol 216's clause map cited call sites at
b36d1e85 (F-A `:840,860,869,874`; F-B `:625-648`; F-H `:725-778`). The
registry repin at 781c8d78 touched only `docs/paper/results-fill-registry.md`;
confirm the checker line numbers are unchanged from b36d1e85 and say so, or
correct them.

## Mutation check (report each: KILLED by <test> / SURVIVED)

M1 `_comparison` back to `expected == observed` → KILLED by the
`(True, 1)` regression AND by P2 end-to-end.
M2 `parse_float=Decimal` removed from the loader → KILLED (name the test —
P1 alone does not kill it; a fixture with a float-token field rendered to a
fixed-places literal that differs under repr-roundtrip does; build it).
M3 `_typed` `number` accepting `str` → KILLED by the table AND P1.
M4 `check_figure` per-pulse read back to `float(...)` → KILLED by P3.
M5 `F4_REPLAY_COMMAND` `--out` → `--outt` → KILLED by F-7.
M6 `check_placement` standing-sentence gate removed (always take the
`n_standing ≥ 1` branch) → KILLED by (c) (current skeleton would report
16 MISMATCHES).
M7 `DX_STANDING_SENTENCE_HEAD` altered by one character → KILLED by a test
that reads the registry and asserts the constant is a substring of it.

## ACCEPTANCE

- `python3 -m unittest tests.test_paper_round7_artifacts` tail (expect ≥ 40 tests OK).
- `python3 scripts/check_paper_round7_artifacts.py --literals-only; echo EXIT=$?`
  → `R7F PLACED 0/16`, `R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`, EXIT=0.
- the two grep outputs from F-4.
- `git status --porcelain` shows only in-scope files; `git diff --stat`.
- Same-signature statement: the ruling classifies this round as the rule-11
  SECOND round on the family "scalar reads coerce instead of refuse"; state
  which closures make a THIRD round on that family structurally impossible
  (every artifact-scalar read goes through `_typed`; prove it: `grep -n
  'artifacts\[\|pulse\[\|resolve_field(' ` and show each hit is either
  inside `_typed`-guarded code or is a dict/list navigation, not a scalar
  read).
- `## Clause map`: one row per closure F-1…F-8 — production `file:line`,
  biting test `file:line`, counterfactual (the input that fails without it).
