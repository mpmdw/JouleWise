# Record 15 — Opus counter-review (gate-ledger row 6) of fix/2026-09-19-head-pin-test-drift @ ff788ef7

**Verdict: MERGE-WITH-FIXES** — 0 blocker, 1 should_fix, 5 nit. Base `2f79e633`, five test
files, +194/−18, production untouched (re-verified). The repair conforms the tests to
ruling 07a and the three fast modules pass here (194 tests, OK). The one should_fix is a
test-sensitivity regression that both Astra lenses missed because neither mutated a
generator in the working tree.

## F1 (should_fix) — `test_d117_floor_qwen3_v5_generate` now tests the COMMITTED generator bytes; uncommitted generator edits are invisible

`generation_repository()` (`tests/test_d117_floor_qwen3_v5_generate.py:275-289`) does
`git clone --shared ROOT`, and the three repaired tests then load the two v5 floor
generators from that clone (`:589`, `:798`, `:859`) and run the `--check` subprocess from
it (`:614-628`). A clone carries HEAD's committed bytes only. Before this change these
tests loaded `ROOT/configs/campaigns/<pack>/generate_configs.py` from the working tree, so
they were the executing oracle for any edit to those two generators; they asserted
`plan_id`, `fixed_n`, cell counts, the 2.0 dominance threshold, byte-identical double
generation, `expected_pack_paths()`, and the self-check exit. All of that now grades HEAD,
not the tree.

**Counterfactual executed** (A/B in a throwaway clone of this branch, `PLAN_ID` of
`d117_floor_qwen3-8b_v5` suffixed `-MUTATED`):

| Mutation state | `test_generators_are_deterministic_closed_and_checkable` |
|---|---|
| uncommitted (working tree only) | **OK** — blind |
| same mutation committed | **FAILED** (`plan-…-v5-MUTATED` != `plan-…-v5`) |

This silently defeats bench mutation probes on exactly the two generators whose byte pin
is the subject of the deferred lane GENERATOR-HEAD-FILE-BYTE-PIN-01. It is invisible in
hosted CI (everything is committed there), which is why it survived both lenses.

Scope note: `fixture_prefill_pin()` and `load_generator("d117_contrast_v5")` still load the
contrast generator from `ROOT`, so the module is now split — GAMMA tree-sensitive, ALPHA/BETA
not. `tests/test_campaign_generator_core.py` still reads `ROOT` sources and retains its
mutation-kill property for all three.

**Cure (≈5 lines, at the call site `generation_repository`, after the clone):** overlay the
working-tree copy of each generator under test into the clone —
`for _p, pack_id, *_ in FLOORS: rel = Path("configs/campaigns")/pack_id/"generate_configs.py"; shutil.copy2(ROOT/rel, repository/rel)`
(`import shutil`). The historical head-file fixture is unaffected; tree sensitivity returns.
A one-line comment should say why the clone exists (historical head bytes) and why the
generators are overlaid (tree sensitivity).

## Nits

- **N1 — the head fixture is never asserted to fire.**
  `tests/test_campaign_generator_core.py:118-141` patches `generator.sha256_file` and
  discards the mock. If a later edit stops routing the head-pin check through
  `sha256_file` for that path, the fixture becomes dead code with zero signal. Bind the
  patch (`with … as head_mock`) and assert `head_path` appears in `head_mock.call_args_list`.
  Q2 answer: a *bypass* that still byte-pins (e.g. `sha256_bytes(path.read_bytes())`) fails
  LOUDLY — the live head (`6b2d37c8…`, sequence 176) ≠ the pinned `6bbe2625…`. The genuinely
  silent case is a future edit that *reads the head file's content* (sequence/digest) to embed
  it: the hash boundary is intercepted, the bytes are not, so the pack would blend a
  historical `file_sha256` with live content and the test would stay green. Today no such read
  exists (`d117_floor_qwen3-8b_v5/generate_configs.py:2887-2889` embeds constants), so this is
  a hazard for lane GENERATOR-HEAD-FILE-BYTE-PIN-01, not a defect here.
- **N2 — interception keyed to labels, not to the declared pin.** `if label in ("ALPHA","BETA")`
  happens to equal the set of `GENERATOR_CASES` entries that declare `LEDGER_HEAD_FILE_SHA256`
  (verified: exactly five generators declare it, all with the same `6bbe2625…`; GAMMA/contrast
  does not). Keying on `getattr(generator, "LEDGER_HEAD_FILE_SHA256", None) == GENERATION_LEDGER_HEAD_SHA256`
  is self-maintaining and ties the fixture to what the generator actually asserts. Path keying
  itself is fine: `path == generator.REPO_ROOT / generator.LEDGER_HEAD_REL`, same expression the
  production drift loop uses (`:2507`); a mismatch degrades to the real hash, i.e. to a loud drift.
- **N3 — the bracketing test re-reads its own file under a hardcoded name.**
  `DEFAULT_ACCEPTANCE_BOUND_PATH` *is* `ANCHOR_V3_R6_ACCEPTANCE_BOUND_PATH`
  (`joulewise/calibration_bracketing.py:181`), so `r6_path` at
  `tests/test_calibration_bracketing.py:643-650` loads the same bytes as `artifact` by a second
  route, and `r6_cutoff == cutoff`. Harmless today; when the default advances to r7 the 76 /
  `08456d50…` literals quietly stop describing the live anchor the test is named for, and nothing
  fails. Add `self.assertEqual(DEFAULT_ACCEPTANCE_BOUND_PATH, r6_path)`, or drop `r6_path` and
  assert on `cutoff` with a comment that the default acceptance is r6.
- **N4 — the clone is created inside the generation output root** in
  `test_contrast_references_…` (`:794`) and `test_arm_registry_…` (`:843`): `repository =
  output/"repository"` while packs are emitted to `output/configs/campaigns/…`. No current
  assertion walks `output` recursively, so nothing breaks; but any future write-boundary or
  inventory check over the output root would find a whole repository under it. Clone to a
  sibling directory.
- **N5 — duplicated fixture self-check.** `assertEqual(sha256(GENERATION_LEDGER_HEAD_BYTES).hexdigest(),
  GENERATION_LEDGER_HEAD_SHA256)` appears three times (generator-core `:123`, packauth `:547`,
  d117 `:281`). It is a module-load invariant: assert it once at import in
  `tests/test_campaign_generator_core.py` and delete the other two.
- **N6 — `_commit_fixture_pin` hardcodes `"head.json"`** (`tests/test_calibration_ledger.py:650`)
  where `self.pin.name` is available (`:97`).

## Answers to the remaining brief questions

- **Q1 (does anything prove less than its name?):** only N3, and cosmetically. The bracketing
  rewrite's name and docstring now match what it checks; the equality it dropped was the
  unratified invariant ruling 07a removed. The three new `test_calibration_ledger` regressions
  go through the production loader with `require_committed_pin=True` and `verify_custody=True`
  and add coverage that did not exist (non-genesis cutoff under an advanced pin; wrong cutoff
  digest; pin-below-cutoff both with and without a physical-head mismatch). The packauth change
  strictly tightens: `assertIn(b"pinned input drifted")` could previously be satisfied by drift of
  *any* pinned input; it now requires the acceptance path by name — i.e. the change removes a
  wrong-reason pass rather than creating one.
- **Q3 (disposable-repository portability):** clean. `git clone -q --shared ROOT` is established
  precedent in this suite (`test_arm_readiness_evidence_packauth.py:129`,
  `test_receipt_histsem.py` ×6); all CI checkouts use `fetch-depth: 0`, so no shallow-clone
  hazard. Commit identity is supplied explicitly in both new paths (`committed_clone()` sets
  `user.name`/`user.email`; `_commit_fixture_pin` passes `-c user.name/-c user.email`), so a
  hosted runner without global git config is fine. Both repositories live under
  `tempfile.TemporaryDirectory`, so failure paths still clean up. No branch-name or HEAD-symbolic
  dependency: cloning this detached worktree worked here. No shell or macOS assumptions in the
  new code. No worktree leakage observed (`git status --short` clean after the runs).
- **Q4 (prune):** N4, N5, N6 above; nothing overbuilt, no test needs splitting, no comment lies —
  the `a816036f` provenance comment is exact (`git show a816036f:…` hashes to `6bbe2625…`).

## Commands run (worktree `/Users/edr/code/JouleWise-wt-refc-d0b83820`, read-only)

| # | Command | Outcome |
|---|---|---|
| 1 | `git diff --stat 2f79e633 ff788ef7`; `git status --short` | 5 files, +194/−18; tree clean |
| 2 | `for f in $(grep -rl '^LEDGER_HEAD_FILE_SHA256' configs/campaigns/*/generate_configs.py) …` | exactly 5 generators, all pinning `6bbe2625…` |
| 3 | `git show a816036f:configs/calibration/calibration_ledger_head.json \| shasum -a 256` | `6bbe2625…` = fixture constant |
| 4 | `shasum -a 256 configs/calibration/calibration_ledger_head.json` | `6b2d37c8…` (sequence 176) — live head differs, as expected |
| 5 | clone branch → `/tmp/magistrate-d0b83820/opus-counter-pin/probe`, mutate `PLAN_ID` **uncommitted**, run `…test_generators_are_deterministic_closed_and_checkable` | `Ran 1 test … OK` — **blind (F1)** |
| 6 | commit the same mutation in the probe, rerun | `FAILED (failures=1)` — proves only committed bytes are graded |
| 7 | `python -B -m unittest tests.test_campaign_generator_core tests.test_calibration_bracketing tests.test_calibration_ledger` | `Ran 194 tests in 8.534s … OK (skipped=2)` |

Not re-run here (Astra execution lens V4/V5 cover them): `tests.test_arm_readiness_evidence_packauth`
(59 s), `tests.test_d117_floor_qwen3_v5_generate` full module, quick tier. No sudo, no
powermetrics, no writes outside `/tmp/magistrate-d0b83820/opus-counter-pin/` and this file.
