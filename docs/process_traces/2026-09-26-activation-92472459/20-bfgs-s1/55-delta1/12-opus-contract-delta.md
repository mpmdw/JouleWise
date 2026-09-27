# BFG-S S1 fix round, delta re-audit, CONTRACT lens (Opus 5.5)

Auditor: Claude Opus 5.5 (`claude-opus-5-5`), contract lens, one foreground session, no subagents, no background tasks. Session 2026-09-26.

- **Candidate:** `b859317c`.
- **Delta:** `git diff 24b79db3 b859317c`. It touches 7 files: set file, `bundle_read.py`, builder, and four test files. `controller.py` is not in the delta.
- **Authority:** the erratum ruling §4 (amendments 36, 37, 39–43).

**Where the probes ran.** Every probe ran in a scratch clone, `/tmp/s1d-opus/cand`, made with `git clone --shared` and checked out at `b859317c`. `/tmp/s1d-opus/JouleWise/runs` is a symlink to the real corpus, so the corpus-gated test runs. The mutation runner is `/tmp/s1d-opus/mut.sh`. It does three things:

1. applies one exact string replacement;
2. runs the named tests;
3. runs `git checkout -- .` to restore the file.

The read-only worktree was not touched, and no repository file was edited. This file is the only repository write.

Not read: RUN_STATE, TASK_QUEUE, CLAUDE*, AGENTS, the decision log, memory and skill files. (The harness preloaded the CLAUDE/MEMORY index text; none of it bears on these findings.)

## Tally

| Tier | Count |
|---|---|
| BLOCKER | 0 |
| SHOULD-FIX | 3 |
| NIT | 9 |

## Executed evidence (summary)

| # | Probe | Result |
|---|---|---|
| E1 | `git diff --stat 1417c0c4 b859317c -- joulewise/battery_float.py joulewise/reduce.py joulewise/bundle.py scripts/paper_*.py scripts/render_results_fills.py configs/campaigns configs/calibration` | empty; rc=0 (standing constraints hold) |
| E2 | `python3 -m unittest tests.test_bundle_read tests.test_bfgs_window_consumers tests.test_battery_float_consumers` | `Ran 130 tests in 45.476s` / `OK` |
| E3 | `python3 scripts/build_battery_float_historical_bundles.py --check` | `forward check: byte-identical entries=69`, rc=0 |
| E4 | `--witness /Users/edr/code/JouleWise/runs*` (61 s, one process) | `witness bundles=1402`; per-source counts identical to the seat's W1 (included complete floor 50; included tree input_manifest 6; listed tree artifact_manifest 6; listed prose complete 12/51/40; listed prose tree 3/3/6); rc=0 |
| E5 | Set composition: complete digests by source | floor file 50, `tests/fixtures/**` 13 |
| E5 | Set composition: tree digests by source | `analysis/rpt001-v2/input_manifest.json` 6 |
| E5 | Fixture rows versus the `24b79db3` set | the 13 fixture rows are byte-identical to the old set's 13 |
| E6 | Reader on the six RPT001 bundles (copied to /tmp) | all six: reader tree digest = `make_figures.bundle_tree_sha256` = set entry, and the bundle is admitted `unobserved_historical` |
| E6 | RPT001 copy, mutated: append a byte, add a file, add a hidden file, delete a file, rename a file | each refused `prospective bundle` |
| E6 | RPT001 copy with the MOCK marker added | refused `not_applicable not bound` |
| E6 | RPT001 copy with a symlinked member | `ValueError`, fails closed |
| E6 | RPT001 copy with one empty directory added | admitted. Both folds ignore directories, as the complete fold always has; no byte changes. |
| E7 | Floor bundle `p2015-df-ph-decode-abs-r03` | the `runs_window_a10_20260725` copy is admitted; its three same-named siblings in other corpora are refused `prospective` |
| E7 | All 57 directories under `runs_window_7bfloor_20260729` | all refused `prospective bundle` |
| E8 | `shasum` of `runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/power_trace.csv` | `6945160964bc…d3e06e9`. That bundle's complete digest is `c2851728…86bf` (amendment 41 confirmed). |
| E9 | `_digest_bound_mock_config` fed 10 hostile `config.json` shapes: list, string, null, int, `{}`, bad UTF-8, bad JSON, `hardware_target: null`, NaN, directory | every one gives a typed `BatteryStatusRefusal` `prospective bundle (<detail>)`; nothing is raised raw ("never raises" holds today) |
| E10 | `tests.test_rpt001_report_slice` with the controlled corpus present; the file is unedited (`git diff --quiet 24b79db3 b859317c`) | `test_full_route_census_emits_only_void_artifacts ... ok` |

**Mutants** (each one is a counterfactual; the exact replacement strings are in this session's commands):

| Mutant | Clause it breaks | Tests run | Result |
|---|---|---|---|
| M1 | reader drops the `tree_identity` check | `test_historical_set_rejects_wrong_tree_identity_and_duplicate` | **SURVIVES** (`OK`) → SF-1 |
| M2 | reader drops the duplicate-digest check | same | killed |
| M3 | reader drops tree step 2 | `test_rpt001_tree_entry_and_mutation` | killed, but only when the corpus is present → N-1 |
| M16 | verdict carries the tree digest when admitted by tree | rpt001 row + window suite | **SURVIVES** → N-4 |
| M4 | `metadata()` raises plain `BundleReadError` for a non-pass verdict from `authenticate_bundle` | bundle_read + window + controller brackets | killed |
| M5 | no `add_note` | window suite | killed |
| M6 | status refusal falls through to custody | window suite | killed (errors=2) |
| M13 | gate stops at the first status refusal | window suite | killed |
| M18 | gate re-raises a new `CustodyFailure` object | window suite | killed |
| M19 | gate-built `CustodyUnreadable` lacks `window_member` | window suite | killed |
| M7 | unreadable config gives an empty detail | bundle_read | killed |
| M8 | non-mock bound config gives a non-empty detail | bundle_read | killed |
| M20 | `_digest_bound_mock_config` lets a re-validation `BundleReadError` escape | bundle_read + window | **SURVIVES** (`Ran 110 ... OK`) → SF-2 |
| M21 | digest mismatch raises instead of returning | bundle_read | killed |
| M9 | path-level exemption for `controller.py` | amendment 36 (i) | killed |
| M9b | text-level exemption of the `run_experiment` row in any function | amendment 36 (i) | killed |
| (iii) | a new controller `replace` call plus its row, absent at `1417c0c4` | `test_replace_rows_precede_s1` | killed |
| M24 | no marker emitted for a non-mock, non-provider backend | amendment 43 | killed |
| M25 | marker emitted for mock too | amendment 43 | killed |
| M26 | extra key in the marker metadata | amendment 43 | killed |

## SHOULD-FIX

### SF-1: amendment 39's wrong-`tree_identity` row does not die under its own counterfactual

**Ruled text.** Amendment 39 test list: "a set file with a tree entry naming another `tree_identity` is rejected".

**Defect.** `tests/test_bundle_read.py::test_historical_set_rejects_wrong_tree_identity_and_duplicate` builds the bad row as `dict(rows[-1], tree_identity="other")`. That row keeps `rows[-1]`'s digest, so it is also a duplicate. The duplicate check rejects it whether or not the identity check exists.

**Evidence.**
- Mutant M1 (the condition `and row["tree_identity"] == "joulewise.bundle-tree.nul-v1"` deleted from `joulewise/bundle_read.py::_historical_bundles`) → `Ran 1 test in 0.014s  OK`.
- Under M1, a set file with a *fresh* digest (`"b"*64`) and `tree_identity="other"` is accepted: `M1 fresh-digest foreign identity ACCEPTED; tree size 7`.

**Production call site.** `bundle_read._historical_bundles()`, read by `BundleReader._battery_verdict` step 2. Today's code is correct; the pin is missing.

**Closure.**
- Give the wrong-identity subcase a digest not already in the set.
- Add a positive twin: the same fresh row with the correct identity is accepted.
- Show M1 RED.

### SF-2: amendment 37's "never raises" is unpinned on the re-validation branch, and its regression is round 1's SF-3 class

**Ruled text.** "`_digest_bound_mock_config` never raises … reports not-bound … when it does not re-validate (the validator's message)". Amendment 42(a) adds that every such refusal is a `BatteryStatusRefusal`.

**Defect.** No test exercises a `config.json` that binds by digest but fails to re-validate. Mutant M20 turns `except BundleReadError` in `_digest_bound_mock_config` into a clause that never matches. Under M20 that plain `BundleReadError` escapes, and in `authenticate_window_members` it becomes `CustodyUnreadable`. That is a battery status reported as custody: the exact SF-3 shape. M20 passes `tests.test_bundle_read` and `tests.test_bfgs_window_consumers` (`Ran 110 tests … OK`).

The code is correct today (E9: all ten hostile shapes give a typed `prospective bundle (config.json does not re-validate: …)`).

**Production call site.** `BundleReader._battery_verdict` → `_digest_bound_mock_config` → `self.config()`, reached through `authenticate_window_members`.

**Closure.** Add two rows:
1. In `tests/test_bundle_read.py`: a key-absent bundle whose `config.json` is `[]`, with `metadata.config_sha256` re-bound to it, raises `BatteryStatusRefusal` matching `^battery_float_evidence_missing: prospective bundle \(config\.json does not re-validate`.
2. In `tests/test_bfgs_window_consumers.py`: the same bundle as a window member gives `WindowBatteryRefusal`, not `CustodyUnreadable`.

Show M20 RED.

### SF-3: the builder mislabels the six `rpt001-v2/artifact_manifest.json` duplicates as awaiting a cold gate

**Ruled text.** Amendment 40: "`analysis/rpt001-v2/artifact_manifest.json` carries the same six tree digests; the entry's `source` is `input_manifest.json` and the second citation is listed as a duplicate." A candidate from an unnamed source is listed "with the reason `source not named by amendment 40`… it enters the set only by a cold gate."

**Defect.** In `build()`, the listing reason is chosen while candidates are still streaming in, by testing `digest in rows`. The file `analysis/rpt001-v2/artifact_manifest.json` sorts before `input_manifest.json`, so its six digests are not yet in `rows` when they are listed. They get the cold-gate reason.

**Evidence.** Forward-check stderr (E3):

```
listed analysis/rpt001-v2/artifact_manifest.json bundle_tree_sha256 tree_nul_v1 2888c9d2…e213: source not named by amendment 40
```

The same line appears in the seat's verbatim transcript at lines 52–54. The seat's report (`11-seat-report.md`) says "the duplicate six v2 artifact-manifest citations are listed", so the report states the opposite of its own pasted stderr.

The floor file's 50 `bundle_sha256s` values are labelled correctly, `duplicate of included citation`, only because of walk order.

**Effect.** The set bytes are unaffected. But the listed output, which is the ruled record of omissions, nominates six already-included digests for a cold gate.

**Production call site.** `scripts/build_battery_float_historical_bundles.py::build`, the `else:` reason expression.

**Closure.**
- Assign reasons after all inclusions (a second pass over `listed`, or check against the final row set).
- Add a builder test asserting those six carry `duplicate of included citation`.
- Re-run the forward check twice; the set and pin must stay unchanged.

## NIT

1. **Amendment 39 rows are gated on the local corpus.** Tree admission, byte mutation and fold equivalence all sit inside `test_rpt001_tree_entry_and_mutation`, which skips unless `REPO_ROOT.parent/JouleWise/runs/example-mac-mlx-local__r1` exists. Hosted CI therefore never runs step 2, and M3 survives there.
   - The fold-equivalence row needs no corpus and could run on `tests/fixtures/d078_r01`.
   - A hermetic admission row would need to patch the set bytes and the pin. F-3 restricts that to named tests, so whether to add one is the magistrate's call.
2. **The forward scan's prose pattern is narrower than the ruled key pattern.** `TEXT_CANDIDATE` matches only the literals `bundle_sha256` and `complete_bundle_sha256`; the ruling asks for "the same key pattern". A probe applying the key pattern to every line of non-JSON text found 4 extra 64-hex strings that go unlisted. None is a bundle digest:
   - an `output_identity` patch value quoted in `prop-param-scaling-energy.md`;
   - the ordered-corpus digest in `COMMONMODE-REPLAY.md`;
   - one in `35-enclosure-refuter-execution.md`;
   - one in `docs/site/run_state.html`.

   Other skips:
   - Non-UTF-8 files are skipped without a stderr line.
   - The 22 unparseable JSON files are reported but not line-scanned. A probe found no bundle-key hex in any of them.

   The set is unaffected, and the reverse witness confirms that no on-disk bundle is cited by a non-prose file outside the sources.
3. **Several classification citations point at a fold definition, not the line that writes the key.**
   - `joulewise/detection_floor.py:558` is `def complete_bundle_sha256`; the floor artifact's `bundle_sha256` writer is elsewhere.
   - `scripts/make_figures.py:138` is `def legacy_v1_bundle_tree_sha256`.
   - `scripts/run_campaign.py:7044` is `def _axi_bundle_digest`.
   - `joulewise/output_identity.py:102` is `def _hash_file`.
   - The two `prose` rows cite a producer, though prose has none.
   - `validated_bundle_sha256` is a digest of a bundle under another fold (an AXI inventory), but it is classed `not_a_bundle`.

   No row can change the set, since only `complete` and `tree_nul_v1` rows from named sources are written.
4. **Amendment 39's rule that the verdict carries the complete digest "in both cases" is unpinned.** M16 survives. The code is correct.
5. **Amendment 37's rows use a simulated bundle.** They are labelled "non-simulated", but they are built from `mock_local.json`. The code path to the refusal is identical before the backend is read, so the counterfactual power is the same.
6. **Amendment 36 (iii) appends the `battery_float` import instead of prepending it.** Prepending also parses (checked). The two are equivalent because the scanner resolves imports before recording sites. The row still dies under a new-call mutant.
7. **Flagged, not a fix-round defect.** A window member containing a symlink or special file makes the complete fold raise `ValueError`. That escapes `authenticate_window_members` with no member label: probe output `ValueError calibration bundle member is not a regular file: x.csv`, `window_member` None, no notes. This existed at `24b79db3` and is within ruled text ("does not suppress an exception from the digest function"). The gate fails closed, but text 12's "name the member" is not met for this failure class. Magistrate's call.
8. **A test patches the pin outside the pin test.** `test_historical_set_rejects_wrong_tree_identity_and_duplicate` patches `HISTORICAL_BUNDLE_SET_SHA256`, which amendment 39's rejection rows require. Round F's refuter should not read F-3 ("patched only by the reader's own pin test") as forbidding it.
9. **The amendment 41 listed reason does not name the file.** It reads `file digest, not a bundle` and does not name `power_trace.csv` of `p2015-df-ph-decode-abs-r03`. E8 verified the fact independently.

## Per-amendment verdict (contract)

- **36: exact.** The four rows match the ruling byte for byte (checked mechanically), and the comment is extended with the four replaced types in order. The count goes from 9 to 13, and nothing existing is loosened (the diff is additions plus the count).
  - (i), (ii) and (iii) are present.
  - Matching is an exact tuple lookup (`site not in REPLACE_CALL_ALLOWLIST`), so the rows cover exactly those four calls.
  - M9, M9b and the (iii) mutant are all killed.
- **37: exact in behaviour.**
  - The detail strings, the empty-detail case, `invalid record`, and the typed class match the ruling.
  - The rewritten SF-6 row is anchored with `$`, and the tightened row is present.
  - One clause is unpinned (SF-2).
- **39: exact in behaviour.**
  - Key sets, identity, duplicate rejection, and the `NamedTuple` are as ruled.
  - Steps run in the ruled order: complete digest, then tree digest, then (iii), then prospective.
  - The tree fold is computed from the bundle's own bytes (`sha256_authentication_input` plus `lstat` size, folded by `publication_privacy.tree_sha256`, imported inside the function).
  - A modified RPT001 bundle is refused (E6).
  - One row is weak (SF-1); coverage is local-only (N-1).
- **40: set contents exact.**
  - 69 = 50 + 6 + 13, and the sources are exactly the three named ones.
  - The forward and reverse checks reproduce.
  - The ruled listed populations are present: `6945…`, the twelve rpt001-v1 values, and the 100 results.json runs, including all fifty `sw7bfloor-*` 7B runs.
  - Listing defects: SF-3 and N-2.
- **41: exact** (see N-9).
- **42: exact.**
  - The reader raises the typed class for all five refusal kinds.
  - The gate's four branches follow the ruled order.
  - Custody is re-raised as the same object with a note and `window_member`.
  - Every refused member is appended, and nothing is dropped.
  - M4, M5, M6, M13, M18 and M19 are all killed.
- **43: not in the delta.** `controller.py` is unchanged since `24b79db3`, and the stage matches the text. The new rows kill M24, M25 and M26.

## Answers to the charge's question 2

- **Can the 69-entry set admit a bundle no committed artifact names as historical?**
  - No. Every entry is a citation from one of the three ruled sources at `1417c0c4`, read from `git archive`, not the working tree.
  - The 13 fixture rows are unchanged from `24b79db3`.
  - All fifty 7B runs stay `prospective` (E7).
- **Can a live run collide with an entry's digest?**
  - Not without being byte-identical to a listed bundle.
  - Every run the S1 controller writes carries a `battery_float` key, so it never reaches steps 1 or 2.
  - The complete and tree sets are checked separately, so a digest cannot match across kinds.
- **Is amendment 39's tree fold computed from the bundle's own bytes?** Yes (E6).
- **Can a modified RPT001 bundle still pass?** Only by adding an empty directory, which changes no byte and matches the complete fold's long-standing rule.
- **Does amendment 42 ever turn a `CustodyFailure` into a status, or drop a member?** No. `CustodyFailure` is not a `BundleReadError` subclass (checked), it is re-raised as the same object, and there is no status branch for it.
- **Does amendment 43 change any energy, stamp difference or `b_fiducial_s`?** No. `controller.py` is untouched by this delta, and `FakeClock.stamp` does not advance the clock.
- **Did amendment 36 widen the guard?** No.

## Same-signature statement (question 3), per round-1 defect class

| Round-1 class | Same signature in this delta? |
|---|---|
| Custody turned into a status, or a status reported as custody (round-1 SF-3/SF-4) | **No live defect.** One latent exposure: SF-2 is an unpinned clause whose regression would reproduce SF-3's direction (status → custody). |
| The reader overreaching a ruled binding | **No.** The reader admits nothing beyond the ruled order. Its one extra check (rejecting non-64-hex digests in the set file) fails closed. |
| A set enumeration miss | **No for the set's contents.** Exactly 69, as ruled, reproduced by the forward and reverse checks. SF-3 and N-2 are defects in the *listed-output* half of the same builder: a wrong reason, and a narrower prose pattern. They are adjacent, but not a miss of an entry. |
