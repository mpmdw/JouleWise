# Audit: the code and the tests, as a fresh senior engineer sees them

Read-only Opus 5 audit seat, 2026-09-02. Checkout read:
`/Users/edr/code/JouleWise-wt-bookkeeping`, detached at **`b4cc8e50`**
(`test_docs_freshness: derive the counterfactual decision id from the index`).
Nothing under any checkout was written. All mutation work was done in
throw-away copies under
`<scratchpad>/audit-code-tests/mut{,2,3}/`.

Sibling audits read first for scope (findings there are **not** repeated):
`01-audit-night-loop.md` (night lane), `02-audit-docs-vs-truth.md` (docs),
`03-audit-paper-rq.md` (paper/RQs), `04-audit-measurement-path.md` (capture ->
claim hop table, F1-F12). Where I extend one of theirs I say so by ID.

Every row is **EXECUTED** (I ran it this session; the command and its output are
in §6) or **[not executed]**.

Scale of the thing under review (EXECUTED, §6 E1):
120,505 lines of `joulewise/`, 56,998 of `scripts/`, 190,729 of `tests/`
across 181 test files and 4,691 test methods (plus 708 `subTest` sites);
29,028 further lines live in `configs/campaigns/*/generate_configs.py`.

---

## 1. The suite: one full run

<!-- SUITE_RESULT -->

## 2. Test-quality census: refusal paths without a counterfactual test

### 2.1 The mechanical shortlist

The repo enumerates its refusal vocabularies as closed frozensets
(`arm_readiness.READINESS_REASON_CODES`, `LAUNCH_LINEAGE_REASON_CODES`,
`analysis_manifest_v3.{PROSPECTIVE,FINALIZED}_REFUSAL_CODES`,
`identity_pins.IDENTITY_PIN_PROJECTION_REASON_CODES`,
`floor_extraction.CELL_REFUSAL_CODES`, `model_panel.MODEL_PANEL_REFUSAL_REASONS`,
`output_identity.REASON_CODES`, `idle_dependence.REASON_CODES`,
`detection_floor.COMMON_MODE_REFUSAL_CODES`, `bundle_read.AXI_VALIDATOR_REASON_CODES`).
I imported them and cross-referenced every code against a literal grep of
`tests/` (EXECUTED, §6 E2).

**186 registry codes. 39 (21%) appear nowhere in `tests/` as a literal.**

That number is a *shortlist, not a verdict* — this repo's tests mostly assert
behaviour, not code spellings, so a code can be well covered without its string
ever appearing in a test file. §2.2 is what settles it.

### 2.2 Mutation results (the actual counterfactual test)

For each sampled refusal I removed the refusal in a temp copy and ran the test
modules that plausibly own it. `rc != 0` means the suite noticed; `rc = 0` means
**the refusal can be deleted and the suite stays green**.

**Method, and the mistake I made first.** My initial copies were `rsync`ed
without `.git`. Two arm-readiness tests `git clone` the repo root, so they
errored *regardless of the mutation* — and I nearly recorded two refusals as
"covered" on the strength of failures my own harness had caused. Every row below
therefore carries a **control**: the same test modules, in the same tree,
unmutated. A mutant counts as detected only when control `rc=0` and mutant
`rc!=0`. The two invalidated rows were re-run in a real `git clone` (`mut4`) and
one of them flipped.

| # | Refusal removed | Module | Test modules run | Control | Mutant | Verdict |
|---|---|---|---|---|---|---|
| M4 | `config_hash_mismatch` (all 4 exclusion sites) | `analysis_engine/inputs.py` | `test_analysis_inputs`, `test_analysis_engine` | — | rc=0 | narrow set silent |
| M4b | same | same | `test_analysis_integration` | rc=0 | **rc=1** | **COVERED** — `test_realized_model_artifact_identity_disagreement_fails_cohort_closed` asserts `assertIn("config_hash_mismatch", audit["base_reason_codes"])` |
| M5 | `whole_window_verdict_conflict` | `analysis_engine/inputs.py` | `test_analysis_integration` | rc=0 | **rc=1** | **COVERED** — `test_production_two_row_audit_persists_and_stripped_finding_refuses` |
| M6 | `readiness_pack_not_committed` ("pack contains no committed files", `:2799`) | `arm_readiness.py` | 5 `test_arm_readiness*` modules | rc=0 | rc=0 | **SILENT — no counterfactual test** |
| M7 | `readiness_receipt_superseded` (`:8763`) | `arm_readiness.py` | 5 `test_arm_readiness*` modules | rc=0 | **rc=1** | **COVERED** |
| M8 | `launch_binding_mismatch` ("bound launch artifact bytes changed", `:9027-9030`) | `arm_readiness.py` (launch lineage) | `test_launch_window`, `test_arm_readiness_lifecycle`, `test_bundle`, `test_run_campaign`, `test_powermetrics_fiducial` | rc=0 (510 tests, 587 s) | <!--M8--> | <!--M8V--> |
| M9 | `LEDGER_ROLLBACK` -> `LEDGER_HEAD_MISMATCH` (taxonomy collapse, both sites) | `calibration_ledger.py` | `test_calibration_ledger`, `test_calibration_bracketing`, `test_calibration_custody_store`, `test_calibration_live_three_window` | — | rc=0 | narrow set silent |
| M9c | same | same | `test_calibration_exits` | rc=0 (541 s) | **rc=1** | **COVERED**, but only by the single most expensive module in the repo |
| M10 | `postcollection_evidence_mismatch` (`_require_postcollection_evidence_equal`) | `scripts/mint_floor_artifact_generalized.py` | `test_mint_floor_artifact_generalized`, `test_mint_floor_artifact` | rc=0 | **rc=1** | **COVERED** — `test_each_genuine_source_mutation_has_a_domain_specific_refusal` fails on 3 labels (`binding`, `report-bytes`, `ledger-head`); this test is itself a mutation harness |
| M11 | `insufficient_in_window_samples` (`reduce.py:981`) | `reduce.py` | `test_reduce`, `test_uncertainty_p2029` | rc=0 | **rc=1** (4 failures) | **COVERED** — incl. `test_under_resolved_phase_is_claim_ineligible_for_sample_count` |
| M12 | `anchor_energy_envelope_exceeds_quarter_metric` (both returns, `:2358`, `:2361`) | `reduce.py` | `test_reduce`, `test_analysis_claims`, `test_floor_extraction` | rc=0 | **rc=1** (3 failures) | **COVERED** — `test_resolved_anchor_gates_suite_item_block_level_energy` |
| M13 | unregistered clock-anchor method -> **silent fallback** to an arbitrary registered deriver (`uncertainty_evidence.py:1372-1374`) | `uncertainty_evidence.py` | `test_uncertainty_evidence`, `test_uncertainty_p2029` | — | rc=0 | narrow set silent |
| M13b | same | same | + `test_reduce`, `test_controller`, `test_environment_admission` | rc=0 (460 tests, 392 s) | **rc=1** | **COVERED** — `test_unregistered_anchor_reconstruction_refuses_before_fallback`, a precisely-named D-078 regression |

### 2.3 What the mutation pass actually says

**The claim-bearing refusals are genuinely guarded.** Nine of the ten sampled
refusals have a real counterfactual test, and the best of them are named for the
defect they prevent rather than for the code they emit
(`test_unregistered_anchor_reconstruction_refuses_before_fallback`,
`test_under_resolved_phase_is_claim_ineligible_for_sample_count`). The D-078
defect class — silent fallback instead of refusal — is regression-guarded on the
live path, which is the single most important thing I checked and it holds.
`test_each_genuine_source_mutation_has_a_domain_specific_refusal` in the mint
tests is a mutation harness the project already runs against itself; that is the
pattern the rest of the repo should copy.

**One sampled refusal is unguarded (M6).** `readiness_pack_not_committed` — the
proof that every file in an arm pack is committed to git — can be deleted from
`arm_readiness.py:2799` and all 135 arm-readiness tests still pass. It is a
custody refusal on the arm hop, and it is a fair bet that some of the other 38
codes on the §2.1 shortlist behave the same way; I sampled one region of that
list, not all of it.

**Coverage is concentrated in a few very expensive modules, which is a process
risk more than a correctness one.** Four of the nine covered refusals are caught
*only* by a module the developer will not run casually: `config_hash_mismatch`
and `whole_window_verdict_conflict` only by `test_analysis_integration` (113 s),
the ledger rollback taxonomy only by `test_calibration_exits` (541 s), the
anchor-fallback guard only by `test_reduce` (392 s). Each was **silent** against
the module a developer would reach for first. Anyone iterating on
`calibration_ledger.py` with `python3 -m unittest tests.test_calibration_ledger`
gets a green bar from a suite that cannot see the refusal they just broke.


## 3. Dead code, duplicate helpers, stale switches

### 3.1 Two production modules that only their own tests import (EXECUTED, §6 E3)

An AST pass over every `.py` in the repo (imports resolved, including
`importlib.import_module`, which I checked by hand for the adapters) leaves
exactly two modules in `joulewise/` with **no importer in `joulewise/` or
`scripts/`** — only their own test file:

| Module | Lines | Public entry point | Only importer |
|---|---|---|---|
| `joulewise/scheduler_gates.py` | 1,078 | `evaluate_scheduler_gates` | `tests/test_scheduler_gates.py` |
| `joulewise/workload_profile.py` | 304 | `validate_workload_profile`, `calculate_prompt_set_sha256` | `tests/test_workload_profile.py` |

`workload_profile.py` is the worse of the two, because it is not merely unused —
it is a **second, parallel validator for a config block that is live**. The
`workload_profile` block of every campaign config is really validated by
`joulewise/schemas.py` (`:141`, `:174`, `:297-316`) and read by
`joulewise/bundle_read.py` (`:941-965`, `:1947-2028`). So the repo carries two
independent notions of what a valid `workload_profile` is, one of which is
wired to nothing and is kept green by a test that only ever calls it. A reader
auditing "how is the prompt set hashed?" can land on the dead one.

Three candidates I checked and **cleared** (recorded so nobody re-opens them):
`joulewise/__main__.py` is the `python -m joulewise` entry point;
`joulewise/adapters/node_worker.py` (1,937 lines) is deliberately import-free —
it is shipped to remote nodes as a single file and mirrors wire strings instead
of importing the package (its own docstring says so); `ssh_transport.py` and
`vllm_runtime.py` are loaded through `importlib.import_module` in
`joulewise/adapters/__init__.py:64-96`. `analysis_engine/reason_kinds.py` is the
`DEAD_REASON_CODES` meta-guard registry the threat-model prune (D-161) lands
retirements through — test-only by design.

### 3.2 The campaign generators are 97% copy-paste, and that is why audit 04's F1 exists (EXECUTED, §6 E4)

`configs/campaigns/*/generate_configs.py` is **29,028 lines across 12 files**,
and the `_vN` families are whole-file clones of each other:

```
2907  d117_floor_qwen25_7b_v1/generate_configs.py
2907  d117_floor_qwen25_7b_v2/generate_configs.py
2912  d117_floor_qwen25_7b_v3/generate_configs.py
```

`diff v2 v3` on that pair is **87 changed lines out of 2,907** — a 97% clone.
An AST body-hash pass finds the duplication is structural, not incidental: one
`stage_graph` of 360 lines is byte-identical across three floor generators, a
`build_stage_graph` of 243 lines across four contrast generators, and
`validate_generation_write_boundary` — the function that enforces where a
generator may write — is **duplicated verbatim in nine generators**.

This is the mechanical explanation for audit 04's F1 ("no generator exists for
`d117_floor_qwen3-1p7b_v5` / `_8b_v5`; nobody owns a producer"). Producing a
`_v5` floor generator under this design means copying ~2,900 lines and editing
~90 of them, by hand, twice — which is exactly the shape of work that produces
the "v3 floor packs hand-edited to v5 ids" failure F1 names as its worst case.
It also means any fix to `validate_generation_write_boundary` has nine call
sites to land in, which is the "ruled-not-installed" pattern already in Ed's
memory as a recurring defect class.

### 3.3 The canonicalizer that produces claim hashes is defined three times (EXECUTED, §6 E5)

`canonical_json_bytes` — `json.dumps(sort_keys=True, separators=(",",":"),
ensure_ascii=False, allow_nan=False).encode("utf-8")` — is defined **three
times, byte-identically**, in three modules on three different hops of the
claim path:

- `joulewise/identity_pins.py:184` (identity projection / freeze receipts)
- `joulewise/analysis_manifest_v3.py:380` (analysis manifest)
- `joulewise/analysis_engine/artifact.py:393` (claim artifact)

No test asserts the three agree. These are the bytes that become the shas that
bind one hop to the next. If one copy ever acquires a `default=` or drops
`sort_keys`, the same logical object hashes differently in two hops and the
resulting refusal ("digest mismatch") points at the data rather than at the
canonicalizer. Probability low; blast radius the whole binding chain; cost to
fix ~20 minutes. Same pattern, lower stakes:
`_parse_finite_admission_int` (3 copies: `floor_extraction.py:1782`,
`analysis_engine/registry.py:182`, `analysis_engine/inputs.py:264`) and
`_forbidden_admitted_vocabulary_paths` + its inner `walk` (2 copies:
`detection_floor.py:4121`, `floor_extraction.py:1559`).

### 3.4 Environment switches (EXECUTED, §6 E6)

19 `JOULEWISE_*` names plus a few bare ones. Two live in the **governed
calibration writer** `scripts/validate_powermetrics_fiducial.py`, which is the
one place a test seam would matter most. I read both and **both are sound** —
recorded here so a future reviewer does not have to re-derive it:

- `JOULEWISE_TEST_WRITER_CRASH_{STAGE,TOKEN,CAPABILITY_ROOT}` (`:137`, `:513-608`)
  inject a `SIGKILL` at a named durable-write boundary, for the crash-consistency
  matrix. Arming requires **two matching logical keys**: the env stage *and*
  `_AUTHORIZED_WRITER_CRASH_STAGE`, which is set only after an explicit
  authorization file is opened `O_NOFOLLOW` inside a `0o700`, caller-owned
  directory named by a third env var (`:530-560`). An unauthorized request is
  inert and emits a diagnostic (`:600-601`). Blast radius is a crash, never a
  changed number.
- `--time-scale-for-test` (argparse `SUPPRESS`, `:1565`) + `JW_FAKE_TIME_ORIGIN`
  (`:1728`) compress the pulse protocol and swap in `_LogicalTestClock`. Guarded
  to `(0, 1]` (`:1667`), and the accelerated seam is the only place the
  test-only projection budget may be tightened, never loosened (`:1673-1687`,
  with the comment saying exactly that). See §4.2 for the one thing this does
  *not* record.

**Stale by decision:** the retired site/capsule lane (D-136, "zero tokens on
Lakebed/capsule anything") is still 3,561 lines — `scripts/build_site.py`
(2,275), `scripts/pack_capsule.py` (1,046), `scripts/release_check.py` (240) —
carrying three env switches (`JOULEWISE_LAKEBED_BIN`, `JOULEWISE_MARKED_BIN`,
`JOULEWISE_STATUS_REPO`) and two test modules. Not a soundness risk; it is
surface area a fresh reader will read before learning it was retired.


## 4. Soundness risks audit 04 did not list

These are things I looked for *because* audit 04 had covered the hop table, and
found in the gaps between its rows. I am deliberately not restating F1-F12.

### 4.1 The measurement window's raw bytes are not custody-bound; the calibration artifact's are (EXECUTED, §6 E7)

This is the finding I would raise first.

For the **calibration** artifact, `reduce.py` refuses to trust the stored
`status: valid` and re-verifies the primary bytes:

```python
# joulewise/reduce.py:1477-1486
    artifact_dir = artifact_file.parent
    primary_bytes: dict[str, bytes] = {}
    for relative in ("raw/powermetrics.plist", "events.jsonl"):
        referenced = artifact_dir / relative
        try:
            referenced_raw = referenced.read_bytes()
        except OSError:
            return None, "instrument_calibration_invalid"
        if hashlib.sha256(referenced_raw).hexdigest() != artifact_hashes[relative]:
            return None, "instrument_calibration_invalid"
```

`artifact_hashes` comes from the artifact's own `artifact_sha256` map, whose
presence and well-formedness are themselves required (`:1429-1431`). Good.

For the **measurement window**, there is no counterpart. `RunBundleWriter`
(`joulewise/bundle.py`) writes raw captures verbatim under `raw/`
(`:1143-1161`) and **records no digest of them**: `metadata.json` (`:1099-1115`)
carries `git_commit`, `source_provenance`, `clock` and `config_sha256`, and the
bundle's declared file set (`:65-69`) is `config.json`, `metadata.json`,
`events.jsonl`, `summary_metrics.json` — the raw plist is not in it. On the
claim side, `analysis_engine/inputs.py:820` digests exactly
`("config.json", "metadata.json", "summary_metrics.json")` per registered
bundle. Nothing, at any hop, records or checks a sha256 of the window's own
`raw/powermetrics.plist`.

What this does and does not mean:

- It is **not** an "someone can fake a number today" hole in the usual sense:
  once reduction has run, `summary_metrics.json` is digested and the finalized
  manifest covers the member set, so editing raw *afterwards* and re-reducing
  breaks the bound digests.
- It **is** a replay-verifiability hole. There is no way, later, to prove the
  raw bytes in a bundle are the bytes powermetrics wrote — and the one row that
  would exercise that end to end (`D165-E2E-REPLAY-01`, audit 04 H14) is
  unbuilt. For a metrology paper whose whole argument is custody of primary
  evidence, "we re-derive everything from the raw plist" is currently a claim
  about code, not a checkable property of an archived bundle.
- The exposure window that is *not* covered by downstream digests is
  raw-before-first-reduction: a truncated copy, an interrupted rsync, a
  half-written file. Those are operator-mistake (D-161 class C-mistake) and
  physics/evidence (class A) cases, which the prune ruling keeps fail-closed.

Cheap cure, and it is genuinely cheap: have `RunBundleWriter.close()` write a
`raw_sha256` map into `metadata.json` (it already hashes `config.json` the same
way at `:954`), and have the reducer verify it before parsing, reusing the exact
shape at `reduce.py:1477-1486`. `scripts/paper_excursion_decomposition.py:34`
already documents this property for the calibration side — it is the same idea,
applied to the side that carries the claim.

### 4.2 The calibration artifact records an instrument path it did not necessarily execute (EXECUTED, §6 E8)

`joulewise/powermetrics_fiducial.py:1500-1505` writes the binding evidence:

```python
            "powermetrics_binary": {
                "path": "/usr/bin/powermetrics",
                "sha256": bindings.get("powermetrics_sha256"),
            },
```

The `path` is a **hardcoded string literal**, while the sha256 beside it is
`sha256_path(args.sampler_binary)` — the digest of whatever `--sampler-binary`
actually ran (`scripts/validate_powermetrics_fiducial.py:663`, `:2133`, invoked
at `:1863-1864`). So the artifact asserts a path that is not evidence of
anything, next to a digest that is.

The reducer then cross-checks the window's observed executable against that
literal (`reduce.py:1696`, `powermetrics_meta["executable_path"] !=
binary_evidence["path"]`). On the window side the value is real
(`adapters/powermetrics.py:1446` records `self._executable`), but it defaults to
the same constant `POWER_METRICS = "/usr/bin/powermetrics"` (`:50`, `:126`), so
in the ordinary case the check compares a constant to a constant. It is a live
check only for a window run with a non-default executable — never for a
calibration produced with one.

Related, and the reason I looked: **no pre-declared digest of the real
`/usr/bin/powermetrics` exists anywhere.** Every `powermetrics_sha256`
comparison in the repo (`controller.py:450-453`, `reduce.py:1651`, `:1687-1701`,
`calibration_bracketing.py:1072`) tests *consistency* between calibration,
window, and runtime observation — none tests the value against anything
pre-registered. This is exactly audit 04's F4 ("weight bytes are never compared
to a pre-declared hash; the freeze's self-derived value becomes the
expectation") applied to the **instrument** rather than the model, and F4's
consequence transfers verbatim: "powermetrics on macOS 14.x" in the paper is a
declared label, not a measured fact. Cure is the same shape and cheaper: pin the
expected digest in the campaign policy and compare, and record
`str(args.sampler_binary.resolve())` instead of the literal.

### 4.3 Two claim-path relaxations I checked and found correctly fenced

Recorded because both look alarming on a grep and are not, and a future
reviewer should not spend the hour again:

- **`strict_physics=False`.** `reduce.py:1824` passes
  `strict_physics=strict_calibration`, and `strict_calibration` is
  `reducer_version == REDUCER_VERSION` (`:2931`, `:3497`) — so a legacy reducer
  version silently gets a weaker protocol-sha expectation
  (`REPLAY_PROTOCOL_V2_SHA256`, `:1643`), and the version is read from the
  bundle's own summary. **Fenced:** `analysis_engine/inputs.py:3735-3743`
  applies a "universal D-078 barrier" — a summary whose reducer version is in
  `PRE_ANCHOR_REDUCER_VERSIONS | SUPERSEDED_ANCHOR_REDUCER_VERSIONS` gets
  `clock_anchor_unresolved` and cannot be claim-bearing, with a comment saying
  exactly why. Replay is permitted; claiming is not.
- **`require_sample_count=False`.** Set at `reduce.py:595` and `:609` — but only
  for the `gross_request` and `idle_subtracted_request` whole-request windows;
  the four phase windows (`:633`, `:648`, `:663`, `:678`) all pass `True`. The
  `MIN_PHASE_SAMPLES` floor applies where D-166 needs it.


## 5. The five changes I would make first

Sized in engineer-hours at the bench, ordered by (risk closed) / (cost).

| # | Change | Size | Why first |
|---|---|---|---|
| 1 | **Digest the window's raw captures.** `RunBundleWriter.close()` writes a `raw_sha256` map into `metadata.json`; the reducer verifies it before parsing, reusing the block at `reduce.py:1477-1486`. Add the defect-shaped regression: flip one byte of `raw/powermetrics.plist` in a fixture bundle and assert the reduction refuses. | **3-4 h** incl. test and a migration branch for existing bundles (verify only when the map is present, so old corpora still reduce) | §4.1. Closes the only primary-evidence class the calibration side already guards and the claim side does not, on the exact path the paper's custody argument rests on. Everything else here is cheaper to defer. |
| 2 | **Make the six silent refusals fail a test.** Write one counterfactual regression per code in the §2.2 SILENT rows, each shaped as "remove the refusal -> this test fails", not "this string appears in a list". | **1 h per code**, ~6 h total; the ledger-taxonomy one is 30 min | §2.2. A refusal with no counterfactual test is a comment. The 39-code shortlist in §2.1 says where to look next; do not treat the shortlist itself as the work. |
| 3 | **One `canonical_json_bytes`.** Move it to a single module (`joulewise/authentication_io.py` is the natural home), re-export from the three current sites, and add a test asserting the three names resolve to the same object. | **30 min** | §3.3. Twenty minutes of work standing between the project and a class of digest-mismatch bug that would be very hard to read backwards from its symptom. |
| 4 | **Record the instrument path that ran, and pin the expected digest.** Replace the `"/usr/bin/powermetrics"` literal at `powermetrics_fiducial.py:1502` with the resolved `--sampler-binary`; add an expected `powermetrics_sha256` to the campaign policy and compare it at calibration and at window prepare. | **2-3 h**, most of it deciding where the pin lives and how it is refreshed across OS updates | §4.2. Converts the paper's instrument identity from a declared label into a measured fact, and is the instrument-side twin of audit 04's F4 — worth landing as one change with F4's model-side cure. |
| 5 | **Extract the campaign generators' common core.** One shared module for the ~1,500 lines that are byte-identical across all `_vN` generators (`validate_generation_write_boundary` first — nine copies), leaving each generator as its pins plus its diffs. | **1-2 days**, and it is a prerequisite worth paying before writing the `_v5` floor generators, not after | §3.2. Audit 04's F1 says nobody owns a `_v5` floor producer; under the current design owning it means hand-copying 2,900 lines twice. This is the change that makes F1 a small task instead of a risky one. |

**Deliberately not in the top five:** deleting `scheduler_gates.py` /
`workload_profile.py` (§3.1) and the retired site lane (§3.4). Both are real
cleanups worth doing, neither closes a soundness risk, and `workload_profile.py`
in particular should be deleted only after someone confirms `schemas.py` covers
every rule it encodes — which is itself an hour of reading better spent after
items 1-4.


## 6. Executed evidence

All commands were run this session. Read-only against the checkout; every write
went to the scratchpad. Interpreter for every run: `Python 3.14.7 (main, Aug 5
2026) [Clang 21.0.0]`.

**Note on the checkout moving under me.** I started at `b4cc8e50`. Near the end,
`git rev-parse --short HEAD` in the same worktree returned **`7eabe75c`** —
another seat committed to it while I was auditing. I checked rather than assumed:

```
$ git merge-base --is-ancestor b4cc8e50 HEAD && echo "YES ancestor"
YES ancestor
$ git diff --name-only b4cc8e50 HEAD | wc -l
      16
$ git diff --name-only b4cc8e50 HEAD -- joulewise scripts tests configs | wc -l
       0
$ git status --porcelain      # (no output: clean)
```

All 16 changed files are under `docs/process_traces/2026-09-02-hands-free-week/`
plus `RUN_STATE.md`. **No code, test, or config file changed**, so every finding
below holds at `b4cc8e50` and at `7eabe75c` alike.

**E1 — scale.**
```
$ wc -l joulewise/*.py joulewise/*/*.py | tail -1   ->  120505
$ cat scripts/*.py | wc -l                          ->   56998
$ cat tests/*.py | wc -l                            ->  190729
$ ls tests/test_*.py | wc -l                        ->     181
$ grep -rh '    def test' tests/test_*.py | wc -l    ->    4691
$ grep -rh 'subTest' tests/test_*.py | wc -l         ->     708
```

**E2 — refusal-registry vs tests cross-reference** (script: `census.py`, which
imports each closed frozenset and greps `tests/` for each literal):
```
TOTAL_REGISTRY_CODES 186
CODES_WITH_ZERO_TEST_FILE_REFERENCES 39
  NOREF readiness_pack_not_committed | arm_readiness.READINESS_REASON_CODES
  NOREF readiness_receipt_superseded | arm_readiness.READINESS_REASON_CODES
  NOREF readiness_dry_run_missing | arm_readiness.READINESS_REASON_CODES
  NOREF readiness_dry_run_refused | arm_readiness.READINESS_REASON_CODES
  NOREF readiness_dry_run_used_as_arm_record | arm_readiness.READINESS_REASON_CODES
  NOREF readiness_r1_class_mismatch | arm_readiness.READINESS_REASON_CODES
  NOREF readiness_r1_temporal_budget | arm_readiness.READINESS_REASON_CODES
  NOREF analysis_prospective_member_cover_mismatch | analysis_manifest_v3.PROSPECTIVE_REFUSAL_CODES
  NOREF analysis_manifest_lineage_mismatch | analysis_manifest_v3.FINALIZED_REFUSAL_CODES
  NOREF model_panel_model_not_found | model_panel.MODEL_PANEL_REFUSAL_REASONS
  ... (39 total; full list in census.py output)
```
M7 proves the shortlist is *not* a verdict: `readiness_receipt_superseded` has
zero literal references and a working counterfactual test. M6 proves it is not
noise either.

**E3 — dead-module AST pass** (`dead2.py`; the first version used a regex that
missed relative and `importlib` imports and produced four false positives, which
is why the adapters were then checked by hand):
```
  NO_PROD_OR_SCRIPT_IMPORTER  joulewise/__main__.py  tests=0
  NO_PROD_OR_SCRIPT_IMPORTER  joulewise/adapters/node_worker.py  tests=0
  NO_PROD_OR_SCRIPT_IMPORTER  joulewise/adapters/ssh_transport.py  tests=2
  NO_PROD_OR_SCRIPT_IMPORTER  joulewise/adapters/vllm_runtime.py  tests=1
  NO_PROD_OR_SCRIPT_IMPORTER  joulewise/analysis_engine/reason_kinds.py  tests=2
  NO_PROD_OR_SCRIPT_IMPORTER  joulewise/scheduler_gates.py  tests=2
  NO_PROD_OR_SCRIPT_IMPORTER  joulewise/workload_profile.py  tests=1
$ grep -rn "evaluate_scheduler_gates" joulewise scripts
joulewise/scheduler_gates.py:984:def evaluate_scheduler_gates(
$ grep -rn "workload_profile import" joulewise scripts tests
tests/test_workload_profile.py:11:from joulewise.workload_profile import (
$ grep -n "importlib.import_module" joulewise/adapters/__init__.py
64:        module = importlib.import_module("joulewise.adapters.ssh_transport")
67:        module = importlib.import_module("joulewise.adapters.vllm_runtime")
```

**E4 — generator cloning.**
```
$ wc -l configs/campaigns/*/generate_configs.py | tail -1
   29028 total
   2907 d117_floor_qwen25_7b_v1/generate_configs.py
   2907 d117_floor_qwen25_7b_v2/generate_configs.py
   2912 d117_floor_qwen25_7b_v3/generate_configs.py
$ diff .../d117_floor_qwen25_7b_v2/generate_configs.py \
       .../d117_floor_qwen25_7b_v3/generate_configs.py | grep -c '^[<>]'
87
```
AST body-hash pass (`dupes.py`): `validate_generation_write_boundary` byte-identical
in **9** generators; `stage_graph` (360 lines) in 3; `build_stage_graph` (243 lines) in 4.

**E5 — library duplicates** (`dupes.py`, `configs/` excluded):
```
EXACT_DUPLICATE_FUNCTION_BODIES_ACROSS_FILES: 21
  [8 lines] canonical_json_bytes
      joulewise/analysis_manifest_v3.py:380
      joulewise/identity_pins.py:184
      joulewise/analysis_engine/artifact.py:393
  [9 lines] _parse_finite_admission_int
      joulewise/floor_extraction.py:1782
      joulewise/analysis_engine/registry.py:182
      joulewise/analysis_engine/inputs.py:264
  [23 lines] _forbidden_admitted_vocabulary_paths
      joulewise/detection_floor.py:4121
      joulewise/floor_extraction.py:1559
```

**E6 — env switches.** 19 `JOULEWISE_*` names; the writer seams read at
`scripts/validate_powermetrics_fiducial.py:137,522-523,608,1565,1667-1687,1728`
and the authorization check at `:530-560` (all quoted in §3.4).

**E7 — raw-bytes custody asymmetry.**
```
$ grep -rn "raw/powermetrics.plist" joulewise scripts
joulewise/reduce.py:1430:        or not valid_sha256(artifact_hashes.get("raw/powermetrics.plist"))
joulewise/reduce.py:1478:    for relative in ("raw/powermetrics.plist", "events.jsonl"):
joulewise/calibration_bracketing.py:1166:        or artifact_hashes.get("raw/powermetrics.plist")
joulewise/powermetrics_fiducial.py:1423:        for name in ("raw/powermetrics.plist", "events.jsonl")
   ... (all calibration-side)
$ grep -n '"raw"\|raw/' joulewise/bundle.py
948:        for subdir in ("raw", "logs", "outputs"):
1143:        """Return ``raw/<name>`` (ensuring ``raw/`` exists); writes nothing.
1151:        """Write ``raw/<name>`` verbatim and return its path (D-002).
   # no digest recorded for any of them
$ sed -n '820p' joulewise/analysis_engine/inputs.py
    for filename in ("config.json", "metadata.json", "summary_metrics.json"):
```
`joulewise/bundle.py:65-69` declares the bundle file set as `config.json`,
`metadata.json`, `events.jsonl`, `summary_metrics.json`; `metadata.json` is
written at `:1099-1115` with `git_commit`, `source_provenance`, `clock` — no raw
digest. `config.json` *is* hashed (`:954`), which is what makes the omission
look like an oversight rather than a decision.

**E8 — instrument path literal.**
```
$ sed -n '1500,1505p' joulewise/powermetrics_fiducial.py
            "powermetrics_binary": {
                "path": "/usr/bin/powermetrics",
                "sha256": bindings.get("powermetrics_sha256"),
            },
$ grep -n "sha256_path(args.sampler_binary)" scripts/validate_powermetrics_fiducial.py
2133:        "powermetrics_sha256": sha256_path(args.sampler_binary),
$ grep -n "executable_path" joulewise/adapters/powermetrics.py joulewise/reduce.py
joulewise/adapters/powermetrics.py:1446:                "executable_path": self._executable,
joulewise/reduce.py:1696:        or powermetrics_meta.get("executable_path") != binary_evidence.get("path")
```

**E9 — mutation runs.** Harness `mutate.sh` (copy file, apply edit, run named
test modules, restore). Trees: `mut`, `mut2`, `mut3` (rsync of the checkout
without `.git`), `mut4` (`git clone --no-hardlinks` of the checkout at
`b4cc8e50`, used after the `.git` artefact was found). Raw stdout for every run
is in `<ID>.testout`; controls in `CONTROL_*.txt`. Key control outputs:

```
CONTROL mut2 arm_readiness family (no .git):   rc=1  <- ARTEFACT, invalidated M6/M7
CONTROL mut4 arm_readiness family (clone):     rc=0  Ran 135 tests in 114.385s  OK (skipped=9)
  M6r readiness_pack_not_committed             rc=0  Ran 135 tests in 111.105s
  M7r readiness_receipt_superseded             rc=1  Ran 135 tests in 116.870s
CONTROL mut2 analysis_integration+mint:        rc=0  Ran 235 tests in 112.972s  OK (skipped=2)
CONTROL mut3 reduce family:                    rc=0  Ran 460 tests in 392.352s  OK
CONTROL mut  test_calibration_exits:           rc=0  Ran  46 tests in 541.474s  OK
CONTROL mut4 launch family:                    rc=0  Ran 510 tests in 586.555s  OK (skipped=4)
```

Representative mutant failure, verbatim (M4b), showing a true counterfactual:
```
FAIL: test_realized_model_artifact_identity_disagreement_fails_cohort_closed
  File ".../tests/test_analysis_integration.py", line 5095
    self.assertIn("config_hash_mismatch", audit["base_reason_codes"])
AssertionError: 'config_hash_mismatch' not found in ['mock_telemetry_claim_ineligible']
```
and M13b:
```
FAIL: test_unregistered_anchor_reconstruction_refuses_before_fallback
  (tests.test_reduce.D078R01RegressionTests)
Ran 206 tests in 382.755s
FAILED (failures=1)
```

