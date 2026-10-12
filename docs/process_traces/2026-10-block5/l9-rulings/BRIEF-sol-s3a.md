SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/whole_window.py", "joulewise/neg8_survivors.py", "tests/b5_analysis/test_validator_context.py", "tests/b5_analysis/test_neg8_parity.py", "tests/b5_analysis/test_neg8_predicate.py", "tests/b5_analysis/test_launch_lineage.py", "tests/b5_analysis/fixtures_s3.py", ".scratch-s3/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written; do not end mid-flight. Start no background task and no other agent. Commit nothing; leave your changes uncommitted in the working tree. **You have 100 minutes of wall time. Write the report by minute 90 whatever is unfinished, and list exactly what is unfinished.** Building a synthetic window takes minutes: build each fixture once per test module (module-level cache), never per test.

# Build stage S3, part A, of lane L9 (the block-5 analysis code): the row validator with an archive context

You work in `/Users/edr/code/JouleWise-wt-l9-s3`, branch `lane/2026-10-12-l9-s3`, cut from the lane (clean
tree; stages S0 and S1 are committed; stage S2, the window bracket, is on another branch and is not needed:
your tests give the context a hand-built `window_bracket` mapping). Synthetic windows are opened through
`tests/b5_analysis/fixtures.py` (`PACK_TABLE`, `selected_window`); read how `tests/b5_analysis/fixtures_s1.py`
does it. This is the stage on which every number of the block rests: the function that
decides whether a claim may rest on a window's stored verdict row. Every block-5 stored row reads failed, and
today the validator refuses every one. Two cold rulings say exactly which stored conditions may be set aside,
on what evidence, and what replaces the comparisons that cannot be made. **The rulings are frozen: build them
item by item. You may not change a rule.** If an item cannot be built exactly as written, do not approximate
it: build everything else, and say in your report which item, why, and the nearest exact behaviour.

## Read first, in this order

Rulings directory: `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/`.

1. `RULING.md`: the terms paragraph, section J1 whole (items 1 to 12 are the rule), J2 item 6, J4 items 1
   and 2, and Z item 3.
2. `ERRATUM-RULING.md`, whole. It **replaces** J1 item 5 (its X1 item 12), **amends** J1 item 9 (X1 item 15),
   **replaces** J1 item 6 (X2), and **replaces** the stored-bracket replay of J1 items 2 and 10 (X3 items 1
   to 7). Where the two files differ, the erratum wins.
3. `DECISIONS.md` (the lead's decisions; section 2's row on sessions and contexts, and item B1).
4. The design, `/Users/edr/night-archive/gate-prune/wave-1007b/l9/L9_DESIGN.md`: section 0 (terms), 3.5,
   4.5 (Changes 1, 2, 4), and "S3" in section 5. The design is older than the rulings: where it says "the
   replay of the stored NEG-8 bracket, unchanged", "CPU admission of the stored members, unchanged", or "or is
   a NEG-8 reference or spare", the rulings have replaced it.
5. The code: `joulewise/whole_window.py` (in this tree it is the pinned harvest program's file,
   `b039c0257`; the rulings cite line numbers of main's older copy as "WW" and of this file as "WW@pin4":
   bind to the functions, not the lines), `joulewise/b5/harvest.py` (frozen; read
   `_neg8_reproduces`, `_NEG8_BOUND_DEPENDENT_FIELDS`, `neg8_screen`, `_neg8_reference_losses`),
   `scripts/run_campaign.py` (frozen; the verdict writer).

## What part A delivers

In `joulewise/whole_window.py`:

- `ArchiveContext` (design 3.5), extended with what the rulings need: the survivor set S(W) of the window's
  deciding screen as a frozen set of bundle ids (computed by part B's context builder per `ERRATUM-RULING.md`
  X1 item 7; part A takes it as a field and tests with hand-built contexts), the roster's references and
  spares, `removed_bundle_ids`, `window_bracket`, `governed_e3`, `sources_replay`, and for the catalog path
  the authenticated catalog manifests (X3 item 6). The context is immutable, nested data included.
- The answered set and the two tests against `conditions − A` (`RULING.md` J1 items 2 to 8 with item 5 as
  replaced), the member-level attribution of the consumer's own re-derivation (J1 item 9 as amended), the two
  adapter-continuity sites (X2), the stored-bracket authentication (X3 items 1 to 7), `admitted` (J1 item
  11). Every refusal name the rulings give is used exactly as spelled.
- One consumption session carries one context for its whole life; the validator's cache must not return an
  admit computed under another context. Make the session refuse a second, different context
  (`archive_context_changed`) and test it.
- **Without a context every function behaves byte for byte as today, on every root** (J1 item 12). The
  frozen harvest calls these functions without a context. Do not change the signature or the return shape of
  anything the harvest or `scripts/run_campaign.py` calls (`harvest_neg8_allowance_bracket` keeps its
  two-value return; design 4.5 Change 2 says why).

In `joulewise/neg8_survivors.py`: `neg8_reference_strict_invalid`, `neg8_reference_energy_unreadable`,
`neg8_stored_conditions` (design 4.5 Change 1; no config leg, `RULING.md` J2 item 6).

Not part A (a second seat builds them next; leave the seams): `joulewise/b5_analysis/context.py` (the context
builder, S(W) and X(W), the tripwires) and `joulewise/b5_analysis/sources_replay.py` (the Erratum 2 item 9
replay). Part A's validator calls `context.sources_replay` as a callable and tests it with a stub.

## Tests

The design's S3 list of tests and refusal paths, **as changed by the rulings**. In particular, beyond the
design's list:

1. The Fable consult seat's row (`seat-fable.md` in the rulings directory, Q1): an included start reference
   whose run succeeded and whose stored admission failed, present in the survivor set. It must be refused with
   `reference_in_screen_named_by_verdict:<c>:<bundle id>` and `admitted` false. The same reference absent from
   the survivor set (lost by the harvest): answered, admitted.
2. An included science member whose stored admission failed and which the exclusion function removed:
   admitted, with `removed_member_rederivation:<reason>:<id>` in the detail (J1 item 9). The same member kept:
   `member_code_on_kept_unit:<id>`. This pair must go through the real re-derivation
   (`_current_core_rederivation_reasons`), not a stub: Z item 3 says the design missed that this path refuses.
3. The stored bracket of the standard window is underived (null allowance in each family record). With a
   context: no `whole_window_verdict_conflict` from the allowance guard; the bound-dependent facts come from
   the allowance record (X3 items 3 and 4). Mutation that must fail it: the old family comparison restored.
4. One stored endpoint field changed (a reference's bundle replaced after the writer ran): X3 item 3 refuses
   `whole_window_verdict_conflict`.
5. The catalog path with an empty manifest list in the context: `core_rederivation_sources_empty`, never a
   pass (X3 item 6 (i)). Mutation that must fail it: today's silent return.
6. Adapter continuity: stored decision not `stable`, record reproduced → not a refusal, decision word in the
   disclosure detail; stored record differing from the re-derived one → `adapter_continuity_record_mismatch`;
   stored record absent → `adapter_continuity_evidence_missing`. Without a context all three as today.
7. `status` values: `passed` and `failed` proceed; `flagged`, `invalid` and an unknown word refuse.
8. Neutrality: a root of blocks 1 to 3 (stored pass, no context) gives reasons and allowances byte-identical
   to the base commit. Show it by running the same probe at the base commit (`git stash` is forbidden; export
   the base file with `git show HEAD:joulewise/whole_window.py` into `.scratch-s3/` and import it under
   another module name).
9. T-A1 parity as the design states it and as `RULING.md` J4 item 2 defines the three drop sets; T-A4 the
   import fence.

For each refusal path, the counterfactual input and the call site are named in your report, and for each
mutation you show the failing output.

## Constraints

- **Frozen files.** Edit nothing outside WRITE_SCOPE: not `joulewise/b5/harvest.py`,
  `joulewise/calibration_bracketing.py`, `scripts/run_campaign.py`, `scripts/harvest_b5_window.py`, no existing
  test module, no file of stages S0 to S2. `joulewise/whole_window.py` is the one pinned harvest file this lane edits (design 6.2, 6.3); if
  `tests/b5_analysis/test_frozen_files.py` fails once you edit it, report that and do not edit the test.
- **Do not run** the six harvest-lane modules or the whole suite; the lead runs them. You may run single
  tests of `tests/test_neg8_survivors.py` while you work.
- **Interpreter.** `/opt/homebrew/bin/python3.13` (not a virtual environment), `PYTHONDONTWRITEBYTECODE=1`, a
  `TMPDIR` whose path contains neither "claude" nor "codex".
- **Blinding (binding).** The measurement block is blinded until a recorded release event that has not
  happened. Do NOT open anything under `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`,
  `/Users/edr/night-g2a/`, `/Users/edr/night-archive/harvest-v5-b5-*`, or any runs root of the measurement
  clone under `/Users/edr/night-custody/measurement/`, and run no program over them. Everything is exercised
  on synthetic fixtures only. Your report carries no energy, power or duration of a real window.
- **A question of what the rule is** (not what the code does) is not yours to settle: finish the independent
  work and return the question (question, options, recommendation, blocked work).

## Report

Changed files; a table with one row per ruling item (J1 items 1 to 12 as amended; X2; X3 items 1 to 7): the
function and line that implements it, the test that covers it, and "exact" or the deviation; each mutation
with its output; the parity table; design divergences; what is unfinished.
