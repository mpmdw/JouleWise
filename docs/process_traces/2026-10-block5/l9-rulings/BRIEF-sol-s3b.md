SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/b5_analysis/context.py", "joulewise/b5_analysis/sources_replay.py", "tests/b5_analysis/test_tripwires.py", "tests/b5_analysis/test_sources_replay.py", "tests/b5_analysis/test_context.py", "tests/b5_analysis/fixtures_s3b.py", ".scratch-s3b/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written; do not end mid-flight. Start no background task and no other agent. Commit nothing; leave your changes uncommitted in the working tree. **You have 100 minutes of wall time. Write the report by minute 90 whatever is unfinished, and list exactly what is unfinished.** Building a synthetic window takes minutes: build each fixture once per test module (module-level cache), never per test.

# Build stage S3, part B, of lane L9 (the block-5 analysis code): the context builder, the survivor set, the tripwires, the sources replay

You work in `/Users/edr/code/JouleWise-wt-l9`, branch `lane/2026-10-07-l9-analysis` (clean tree; stages S0,
S1, S2 and S3 part A are committed). Part A put `ArchiveContext` and the context-aware row validator into
`joulewise/whole_window.py`; its tests use hand-built contexts. Part B builds the one function that makes a
real context from an analysed window's archive, and the structural checks that must pass before any number
is computed. **Two cold rulings are your specification and are frozen: build them item by item; you may not
change a rule.** If an item cannot be built exactly as written, do not approximate it: build everything else
and say which item, why, and the nearest exact behaviour.

## Read first, in this order

Rulings directory: `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/`.

1. `ERRATUM-RULING.md`: its terms paragraph (S(W), X(W), "deciding screen"), X1 whole (items 6 to 11 are
   the tripwire's exact definition; items 12 to 15 say how the validator uses the same set), X3 items 4
   and 6.
2. `RULING.md`: the terms paragraph; J2 (b) items 2 to 6; J3 (b); J4 (b) items 1 and 2; P9 (b) items 2
   and 3 (what a stop record may print).
3. `DECISIONS.md`, and the part A seat's report (the lead's launcher note below names its path) for the
   exact fields `ArchiveContext` ended up with.
4. The design, `/Users/edr/night-archive/gate-prune/wave-1007b/l9/L9_DESIGN.md`: section 0, 3.5, 4.5
   (Change 3 and "The two tripwires"), and "S3" in section 5 (the `BETA_SOURCES_RECOVERED` and tripwire
   refusal paths). The design is older than the rulings; where they differ the rulings win.
5. The admitted text the replay implements:
   `docs/process_traces/2026-10-block5/sources-erratum/ERRATUM.md` items 0 to 9.
6. The code: `joulewise/b5/harvest.py` (frozen: `claim_neg8_sources`, `_neg8_reference_losses`,
   `neg8_screen`, what it writes into `derived/neg8-screen.json`), `joulewise/whole_window.py`
   (`_derived_neg8_decision`, `harvest_neg8_allowance_bracket`, part A's additions),
   `joulewise/b5_analysis/{archive,windows,kept_units,bracket}.py` (stages S0 to S2: every byte you read from
   an archive goes through the S0 handle).

## What part B delivers

`joulewise/b5_analysis/context.py`:

- `survivor_set(archive, row, roster) -> SurvivorSet`: S(W) computed exactly as `ERRATUM-RULING.md` X1 item
  7 says (basis references and spares, less both loss lists), with the count cross-check and the refusal
  `survivor_set_count_mismatch`.
- `excluded_references(archive, roster) -> frozenset[str]`: X(W) as X1 item 6 says.
- The tripwire `excluded_reference_in_screen` (X1 items 8 to 11), the named special case
  `reference_config_mismatch_in_screen` folded into it or kept beside it with the same stop semantics (say
  which; `RULING.md` J2 item 2), and the call of stage S1's `require_kept_members_in_verdict` (J3). A stop
  produces two records: an unrestricted one carrying only what X1 item 11 and P9 item 2 allow, and a
  restricted one carrying the full sets.
- `build_context(window, archive, kept_units, window_bracket, row, ...) -> whole_window.ArchiveContext`: the
  one constructor of a context for a real window. It runs the tripwires first and puts the same `SurvivorSet`
  into the context that the tripwire used (X1 item 14: the validator's clause and the tripwire must be the
  same set, computed once).
- A context is built once per window and per bound: the sensitivity pass (stage S9) will ask for a second
  context with another bracket; make that an explicit second call that returns a new object, never a
  mutation.

`joulewise/b5_analysis/sources_replay.py`: `replay_claim_sources` (design 4.5 Change 3; Erratum 2 items 0 to
7), with the loss list recomputed and compared (`sources_replay_losses_differ`), the item-6 call's arguments
word for word, and on the catalog path the outputs X3 item 6 needs: the authenticated catalog manifests
projected onto the row's basis for the validator's core re-derivation, and the equality of the re-derived
survivor bracket with the withheld re-screen bracket on the bound-independent fields.

## Tests

The design's S3 refusal paths for `BETA_SOURCES_RECOVERED`, the replay and the tripwires, **as changed by the
rulings**, each with its counterfactual and a mutation run. Beyond them:

1. S(W) on the standard window equals the references the real pinned re-screen aggregated: show it against
   the frozen harvest's own evaluation on the same synthetic window (not against a typed list).
2. A reference the exclusion function removed under a code outside the harvest's loss list, still a
   survivor: the three codes the erratum names (`member.whole_window_member_failure`,
   `records.malformed_flag_member_exclusion_possible`, `roster.before_chain_started`) and one other
   member-removing code, each on a real synthetic window built by the real writer and the real pinned
   harvest → `excluded_reference_in_screen`; the unrestricted record carries the counts and the member id
   with its code only when the catalog marks the code STRUCTURE.
3. The same reference lost by the harvest for another reason → the tripwire is silent.
4. `survivor_set_count_mismatch`: the recorded survivor counts edited (with the digests rebound).
5. The end-to-end pair that the Fable consult seat constructed (`seat-fable.md`, Q1): an included reference
   with a failed stored admission, in S(W) → the tripwire fires at `build_context`; and with the tripwire
   bypassed in the test, part A's validator refuses with `reference_in_screen_named_by_verdict`. Both stops
   name the same member.
6. One structural test that no test of this stage reads a typed survivor list where a computed one exists.

## Constraints

- **Frozen files.** Edit nothing outside WRITE_SCOPE; in particular not `joulewise/whole_window.py` (part A
  owns it; if part B needs a seam it lacks, report the exact change), not `joulewise/b5/harvest.py`, no
  existing test module.
- **Do not run** the six harvest-lane modules, `test_fixture_shapes`, or the whole suite; the lead runs them.
- **Interpreter.** `/opt/homebrew/bin/python3.13` (not a virtual environment), `PYTHONDONTWRITEBYTECODE=1`, a
  `TMPDIR` whose path contains neither "claude" nor "codex".
- **Blinding (binding).** The measurement block is blinded until a recorded release event that has not
  happened. Do NOT open anything under `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`,
  `/Users/edr/night-g2a/`, `/Users/edr/night-archive/harvest-v5-b5-*`, or any runs root of the measurement
  clone under `/Users/edr/night-custody/measurement/`, and run no program over them. Synthetic fixtures only.
  Your report carries no energy, power or duration of a real window.
- **A question of what the rule is** is not yours to settle: finish the independent work and return the
  question (question, options, recommendation, blocked work).

## Report

Changed files; one row per ruling item (X1 items 6 to 11 and 14; J2 items 2 to 6; J3 items 1 to 3; X3 item
6; Erratum 2 items 0 to 7): the function and line, the test, "exact" or the deviation; each mutation with its
output; design divergences; what is unfinished.
