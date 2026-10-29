# RC-CMP-FABLE-CONSULT: design consult on the comparator's third false-agreement recurrence

**RECOMMENDATION: approve a producer-derived input gate, but build it from L9's writer and L9's registered ids, not from a hand-written schema of L9's source: (1) refuse any step-11 output whose bytes are not the canonical serialisation of their own strict parse (duplicate keys, NaN, any other writer); (2) refuse an identity field anywhere but on the object it names; (3) route every binding by a literal, registered id (sealed `extraction_spec.json` and `analysis_manifest_v3.json`), never by substring parsing; then one delta round, both reviewers, with the round-1..3 probes plus the gate's own refusal list as the acceptance tests. Defer per-field type schemas for the disclosure record (70 line kinds) to after the block-5 release.**

Seat: Fable 5.1, high effort, cloud, synthetic only. Branch `review/2026-10-29-rc-cmp-fable-consult` from
`lane/2026-10-27-recompute-comparator` at `7fede8c7`. No real block-5, block-6 or BYTES data was opened or searched.
L9's full-size `test_dry_run` was not run. Interpreter `/usr/bin/python3.13`, `TMPDIR=/tmp/jwfc-tmp`. L9's producer
code was read from `origin/main` (the comparator lane carries no `joulewise/b5_analysis`, by design).

Executed evidence in this directory (`.codex-report/rc-cmp-fable-consult/`):

- `suite.out`: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
  at `7fede8c7`: `Ran 235 tests in 138.282s OK (skipped=18)`.
- `prototype_gate.py` and `probes.out`: the three gates as an in-memory wrapper around
  `scripts/compare_b5_recompute.py` (no production edit), run on the lane's own fixtures through the comparator CLI.
  19 cases, every one as predicted: 8 controls accepted, 7 round-3 witnesses refused, 4 non-producer shapes refused.
  Where the gate refuses, the line `comparator alone` shows what `7fede8c7` does today on the same bytes.

## 1. Which path closes the class, and the invariant behind exit 0

**The class.** All three rounds are one defect: the comparator decided *where a printed number belongs* from
something L9's own document asserts. Round 1: by the value itself (value-only coverage). Round 2: by an attribute
the leaf's line asserts (`condition_family_id`). Round 3: by the nearest enclosing object's identity field
(`leaves()` merges every object's scalar fields over its parents', `scripts/compare_b5_recompute.py:1308-1323`;
`binding()` reads identities from that merged context, `:1335-1368`), by a reader that silently picks one of two
duplicate members (`loads()`, `:248-257`, plain `json.loads`), and by substring parsing of ids (`cell_phase`,
`cell_model`, `floor_kind`, `:397-407`: `"decode" in cell_id`, `endswith("-absolute")`). RC-CMP-5's S2 narrowed
*which* document values may route, but the routing still reads values out of the document under test.

**The invariant that makes exit 0 trustworthy.** Exit 0 means every printed number agrees if and only if:

- (I1) the parse is the unique reading of the bytes (no reader-dependent interpretation);
- (I2) every leaf of the document is consumed exactly once, either by a compared row or by a registered,
  enumerated exemption listed by name;
- (I3) the row a leaf is compared against is chosen by the leaf's *position* and by *registered* ids compared
  literally, never by any value the document asserts about itself.

(I1) is what F2 (duplicate keys) and the NaN-erasure break. (I3) is what F1, Sol 1, Sol 2 (round 2) and Sol 3 break.
(I2) already exists as `step11_unmapped_fill` (`:1515-1518`) but is weakened by catch-all patterns: the identity
rule `(fill|disclosure):(.*/)?(cell_id|contrast_id|...)` (`:1297-1300`) accepts an identity field at *any* depth,
which is exactly the hole F1 and Sol 1 walked through, and `IDENTITY_NUMBER` `(.*/)?(positions/\*|attempt)` (`:1296`)
and the `(conditions|metric|equivalence)(/.*)?` subtree rule (`:1165`) accept any number below a broad name (Opus F5).

**Does the lead's schema gate establish it?** Yes for (I1) through its step (1), and for the F1/Sol-1 half of (I3)
through "identity fields only at their owning container". Its step (3), "compare routing ids literally", is the
other half of (I3), but only if *literal* means against a registered id set, not against the comparator's own
parse of the id (Sol 3 is precisely a `routing_id` label earned by partial parsing, `:1439-1441`). "Exact field set
per object, types per path" is (I2) made exact. So the gate as described is the right shape. The question is where
each part comes from, because a hand-written schema is a second copy of the producer and will drift.

**Where each part comes from concretely, and what keeps it from drifting.**

| Part | Producer source (origin/main) | Gate form | Drift control |
|---|---|---|---|
| (1) strict + canonical load | Fill writer `joulewise/results_fill_adapter.py:207-209` (`render_results_fill_input`: `sort_keys=True, separators=(",",":"), ensure_ascii=False, allow_nan=False` + `"\n"`); disclosure writer `joulewise/calibration_ledger.py:223-230` (`canonical_json_bytes`, same flags, no newline) called at `b5_analysis/disclosures.py:1310`; L9's own readers already refuse duplicate members (`b5_analysis/kept_units.py:24-31` `_strict_json`; `results_fill_adapter.py:30-37` `_object`, `:39-40` `_nonfinite`) | `json.loads(raw, object_pairs_hook=refuse_dup, parse_constant=refuse_nonfinite)`, then `canonical(parsed) == raw` else `l9_output_not_canonical` | None needed: both writers are one `json.dumps` call with fixed flags; a producer change to the flags fails the comparator's own control (`A1`) and L9's `test_A1_A3_A4_canonical_and_pure_renderer` (`tests/b5_analysis/test_disclosures.py:170-180`) |
| (2) owner-only identity | Fill rows: the dict literal in `adapt_claim_verdicts` (`results_fill_adapter.py:163-179`), identity `contrast_id` on the row; `loo/rows/*` carry `omitted_block_id`. Disclosure lines: `_item(line, restricted, text, **values)` (`disclosures.py:111-113`) appended to `cells`, `floors`, `contrasts`, `window_lines/<pack>`, `block_lines` (`:1282-1312`); `loo_magnitude/rows/*` carry `block_number`; the sensitivity record's `reported_cells/*`, `floor_cells/*`, `contrasts/*` | A table of owning-container paths (6 patterns in the prototype) and attribute exceptions (1: `central_band/pack`); an identity-named key elsewhere refuses `identity_field_misplaced:<path>` before any binding | The nested copies in the fill (`floor`, `multiplicity`, `claim_evaluation`, `loo`, `sampling`, ...) are verbatim verdict objects whose exact key sets L9 already enforces in `analysis_engine/artifact.py` (`_CONTRAST_KEYS:170-189`, `_FLOOR_KEYS:233-241`, `_ARM_GATE_KEYS:243-248`, `_FLOOR_RESOLUTION_KEYS:249-258`, `_exact_keys:418-428`); none contains `contrast_id`, so the owner rule is already the producer's rule for the fill. For the disclosure record, add one L9-side test: the record `produce_disclosures` builds in `tests/b5_analysis/test_disclosures.py:162` passes the same owner table (shared data file) |
| (3) literal routing ids | Sealed `configs/campaigns/d117_floor_qwen3-{1p7b,8b}_v5/extraction_spec.json` (`cells[*].cell_id`, `cells[*].kind`, `reported_energy_cells[*].cell_id`; grammar `paper_reported_energy.py:39` `CELL_RE`) and `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/analysis_manifest_v3.json` (`contrasts[*].contrast_id`, `floor_selector.condition_family_ids` in [A, B] order, `analysis_engine/__init__.py:506-519`). L9's fill builder already reads the registered contrast ids from git HEAD (`scripts/build_results_fill_input.py:35-40`) | A table `registered id -> (model, phase, form)` built from the spec's own `kind` field; an L9 id not in the table refuses `routing_id_unregistered:<path>:<id>`; `binding()` derives `floor_cell`, `minted_field`, `rcid`, `aggregate_cell` from the table, never from the string | The spec is sealed and hashed into the custody record; the comparator reads it by digest like every other input. A spec change is a registration change (gate policy rule 5), which is where it should surface |

**Executed:** `probes.out` B1-B7. With the gate, all seven round-3 witnesses refuse at the shape (`identity_field_misplaced`
for F1/Sol 1, `l9_output_duplicate_key` and `l9_output_nonfinite` for F2/Sol 2 including the NaN-erasure,
`routing_id_unregistered` for Sol 3). The comparator alone exits 0 on B1, B2, B3, B5 and B7 at `7fede8c7`.

**Side finding (over-refusal, fail-closed, not a false agreement).** The registered v5 spec spells comparative
extraction cells `d117-df-cmp-abba-ph-decode-qwen3-1p7b` (kind `comparative`); the lane's fixtures spell them
`d117-df-ph-decode-qwen3-1p7b-comparative` (`tests/independent_recompute/test_comparator.py:35-36`). L9's
`floor_composition` line prints the spec's id (`disclosures.py:445-470`, `cid = row["cell_id"]`). The comparator's
`floor_kind()` needs the `-comparative` suffix, so on the registered spelling the leaf is `key_unresolved` and the
run refuses (`probes.out` A8: `('disclosure:floors/floor_composition/guarded_j', 'key_unresolved')`, exit 2). The
step-10 floor comparison is unaffected (it keys by the report's `kind` field, `:425-426`). Whether RC-CMP-4's
synthetic spec uses the registered spelling is for the lead to read from its restricted output
(`coverage.unbound` reasons on `floors/floor_composition/*`); on the real block-5 spec this refuses every window.
A literal id table from the spec (part 3) removes the parser and this refusal together.

## 2. Risks of the schema gate

1. **Over-refusal on legitimate real outputs.** This is the real cost, and it scales with how much of the schema
   is written by hand. Three kinds, with evidence:
   - *Shapes the fixtures never had.* The lane's fill fixture has 3 keys per contrast row; the producer writes 24
     (`probes.out` D: "missing 21 keys"). Any exact-field schema refuses today's fixtures, so every comparator
     test needs a producer-shaped fixture first, or the gate ships untested against real shape. The
     `d117-df-cmp-abba` spelling above is the same debt already biting.
   - *Registered nulls, list order, spelling* (Sol answer 3). Parts (1)-(3) accept all three where the producer
     does: a registered `j_per_token` null (A2), keyed lists in any order (A3: canonical bytes sort keys, never
     lists), arm gates and resolutions as attributes (A4), a refused gate printed null (A5: the gate accepts; the
     comparator's `row_disagrees` there is the ruling Opus named, not the gate's). Model spelling (`qwen3-1p7b` on
     machine lines, `disclosures.py:579-588`; lowercase packs, `PACK_ORDER`) belongs in part (3)'s table, taken from
     the producer, not retyped.
   - *A per-field type schema of the disclosure record.* 70 distinct line kinds built with `**values`
     (`disclosures.py`, `_item` calls), many conditional on flags, battery assist, lost references, p42 status. A
     hand-derived schema will miss branches the synthetic fixtures do not exercise and refuse a sound real window at
     the release gate. That is why I recommend deferring it, and taking the exact leaf census from a full-size
     run instead (section 3).
2. **The schema as a new home for a false agreement.** A schema written by hand from the producer is a second
   copy; if it names a field the producer does not emit, nothing breaks (the field is simply never seen), and if
   it omits one, the gate refuses, so the schema itself cannot *admit* a wrong number. The residual risk sits in
   the exemption list: a broad `uncovered-by-name` pattern is where a renamed or added numeric field still passes
   with exit 0 and only a count in the public line (Opus F5, Sol answer 2). Parts (1)-(3) do not touch that; the
   fix is to make the exemptions exact paths from a census (section 3) rather than regex subtrees.
3. **Schedule.** Block-5 release gates on this (8 Nov checkpoint; Paper 1 draft 22 Nov). Parts (1) and (2) are
   each under 40 lines and were prototyped here in one sitting; part (3) replaces `cell_phase`/`cell_model`/
   `floor_kind`/`reported_key` (`:397-407`, `:771-776`) with a table lookup and removes the `(.*/)?` identity
   catch-alls (`:1296-1300`), which is a bounded edit inside `binding()` and `COVERAGE`. The disclosure type schema
   is the only open-ended item and is the one I defer. The real schedule risk is a refusal on the first real
   window; the only protection is the full-size synthetic comparison at the fixed head (RC-CMP-4 rerun), which
   both round-3 reviewers also named as the thing that settles readiness.

## 3. A cheaper structural alternative the reviewers did not name

**Canonical round-trip instead of a strict loader plus schema for (I1).** Both step-11 writers are canonical
`json.dumps` with fixed flags. Requiring `canonical(parse(raw)) == raw` is one comparison and establishes more
than "no duplicate keys": no NaN, no key-order or whitespace variant, no number spelling the writer cannot
produce (`probes.out` C2-C4: pretty-printed, unsorted and `1E0` all refuse), and therefore no second reader that
could read the same bytes differently. It needs no schema and cannot drift unless the writer's flags change.

**Recompute-driven bindings (reverse the walk) for (I2)+(I3).** Today the comparator walks L9's leaves and derives
each row key from the document's context. Walk the other way: for each registered id and each comparison row the
recompute produced, *construct* the L9 path literally (`gamma/contrasts/[contrast_id=<registered>]/estimate`), fetch
that leaf by exact path with list items selected by literal id equality at the owning container only, compare,
and mark the leaf consumed. At the end, every unconsumed leaf must be on an exact-path exemption list, else refuse.
No identity is ever read from a nested object, no id is ever parsed, and one-sided keys are missing rows by
construction. The existing `COVERAGE` table already holds the path knowledge; its templates invert mechanically
(L9 path pattern with `{cid}` to be filled from the registered set, instead of a regex matched against L9). This is
the "declared path table" variant of the question and it is smaller than a producer-derived schema because it
adds no artifact: the table is the one the comparator already carries, made exact.

**An exact exemption census instead of a hand-written schema for the disclosure record.** Run the comparator at
the fixed head on the full-size synthetic custody (RC-CMP-4's, rerun at the new head as both reviewers asked),
take `coverage.leaves` from its restricted output, and commit the exemption keys as an exact path list reviewed
once (gate policy rule 3, since it selects what is compared). Add one L9-side test that the record built in
`tests/b5_analysis/test_disclosures.py:162` and the fill built in `tests/b5_analysis/test_fill_adapter.py:97`
produce no path outside that list. Producer drift then fails L9's CI, not the release comparison. This gives the
"exact field set" property of the schema gate for the disclosure record without anyone writing 70 line schemas,
and it is the only route that is also validated against real shape.

**What the comparison of canonical full documents would not do.** Comparing a projected expected document
byte-for-byte fails on numeric bars (values agree within a bar, not exactly), so the structural diff above with
per-leaf bars is the usable form of that idea. It is what the reverse walk is.

## 4. Recommendation Ed can approve in one line, acceptance tests, reviewers

**One line for Ed:** "Approve RC-CMP-6: canonical-bytes load, owner-only identity, registered-id routing, exact
exemption census from the full-size run; one delta round, Sol xhigh fast and Opus together; disclosure type
schemas deferred to after the block-5 release."

**Minimal acceptance tests** (each a regression test with a counterfactual at `7fede8c7`, per gate policy rule 3):

1. Round-1 probes (RC-CMP-3 tests `test_review_fixes.py`, `test_meter_fit.py`, `test_auditfix.py`) and round-2
   probes (`test_structural_rules.py`) still fail closed: suite green at the new head (today 235 OK).
2. Round-3 witnesses, each refusing with the named code and each exiting 0 at `7fede8c7`:
   Opus Q3c / Sol nested `contrast_id` (`identity_field_misplaced`), Opus Q4 / Sol duplicate member wrong-first and
   NaN-then-value (`l9_output_duplicate_key`, `l9_output_nonfinite`), Sol typo'd `cell_id` prefix
   (`routing_id_unregistered`). The prototype's B1-B7 are the cases.
3. Canonical-bytes controls: pretty-printed, unsorted keys, `1E0` spelling refuse (`l9_output_not_canonical`); the
   fixture written with L9's writer flags is accepted (A1); keyed lists in any order accepted (A3).
4. Owner-table controls: registered null accepted (A2), v3 arm gates and resolutions accepted (A4), band `pack`
   attribute accepted (A6), an identity key repeating its owner's own id inside a nested object refused (C1).
5. Registered-id controls: both registered spellings of a floor cell accepted and bound
   (`d117-df-ph-...-absolute`, `d117-df-cmp-abba-ph-...`; A7 and A8, where A8 must become exit 0); any other id
   refused; the table is read from the sealed spec by digest, and a test shows a spec edit changes the table.
6. Exemption census: `coverage.leaves` exemptions are exact paths; the AST test asserts no `(.*/)?` identity or
   number catch-all remains in `COVERAGE`; L9's `tests/b5_analysis` has the two census tests above.
7. Fixture debt: at least one comparator fixture carries a producer-shaped fill row (all 24 adapter keys) and a
   producer-shaped `floor_composition`, `machine_summary` and `primary_contrast` line, so the gate is tested on real
   shape before the full-size run.
8. Readiness, not a unit test: the full-size synthetic comparison at the new head with `coverage.unbound`,
   `coverage.unmapped`, `nonfinite`, `absent_sources` empty and zero family failures, read from the restricted
   output; hashes retained (both round-3 reviewers' condition; Sol answer 3).

**Reviewers under rule 4.** This is a fix round on code that selects which numbers are compared, so both seats,
launched together and told to probe and mutate: Sol 6.1 xhigh fast and Opus 5.5, as before, each checking the fix
diff plus the gate's refusal list. Give each the prototype and `probes.out` as the attack list to extend, and ask
each for one new shape the gate accepts that the producer cannot emit (the residual class). If a round again finds
a wrong printed number passing with exit 0 through a *value-derived* route, that is a fourth recurrence and the
comparator's walk direction should be reversed (section 3) rather than patched.

## What the prototype does not show

- It wraps the comparator; it does not change `binding()`, so A8 still refuses and the comparator's own
  `routing_id` labelling is unchanged. The production change is parts (1)-(3) inside the script.
- It uses the lane's fixtures, which are not producer-shaped (D). Its owner and attribute tables (6 + 1 patterns)
  were written from reading `disclosures.py` and `results_fill_adapter.py`, not generated; the census step in
  section 3 is how they should be produced for real.
- No meter stream, so machine-line spelling (Sol answer 3's 16 `rho` failures) was not re-executed here; the fix
  belongs in part (3)'s table from `disclosures.py:579-588`.

## Pruning tally (gate policy rule 9)

| gate | ran | caught_number | caught_session_refusal | evidence |
|---|---|---|---|---|
| comparator suite at `7fede8c7` | yes | no | no | `suite.out`, 235 OK |
| prototype gate on round-3 witnesses | yes | yes (B1, B2, B3, B5, B7 exit 0 today) | no | `probes.out` |
| prototype gate on registered id spelling | yes | no (fail-closed over-refusal) | no | `probes.out` A8 |
