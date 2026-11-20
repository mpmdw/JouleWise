# File prune g4 and stacked handoff

Branch: `ops/2026-11-10-file-prune-g4-spikes`, based on g3 `30098da9d`.
Offline/local only. No push, model download, analysis pipeline, measurement
collection, or edits to lead-owned coordination/deferred source.

## Candidate verdicts

`docs/ops/FILE-PRUNE-G4.tsv` records all eight candidates:

- DELETE `scripts/spike_mlx_prompt_cache.py`: 623 lines / 21,777 bytes, an
  isolated feasibility experiment. Its exact blob matches
  `archive/process-traces-before-release-prune-2026-11-08:<path>`. The recorded
  Stage 3.0.1 verdict is `replay_supported`, from the historical feasibility
  document; that verdict was not rerun here. Current size prediction remains
  `python -m joulewise kv-size`.
- Retire only its dedicated
  `tests.test_mlx_runtime.MlxRuntimeTests.test_spike_report_rejects_equal_truncated_decodes`
  and import. All current runtime tests, including fixed-budget truncation
  behavior, remain. The isolated remaining module takes 0.219 seconds including
  import; its timing hint was updated to that observation.
- KEEP `gen_gsm8k_scored.py`: canonical authenticated scored-v6 producer,
  imported by live benchmark-import tests. The scored lane is expressly deferred.
- KEEP `gen_jw_mixed.py`: current mixed/sentinel producer; public tokenizer
  metadata helpers are imported by live gensuite tests. No production generator
  helper was moved or duplicated.
- ALREADY ABSENT: `axi_sb_static_batch_spike.py`, `axi_sc_spec_decode_spike.py`,
  `codex_usage_probe.py`, `measure_claude_cold_start.sh`, `gen_affine_smoke.py`.
  These five are absent from the November 8 archive as well as current main;
  their exact paths remain at `archive/pre-prune-2026-11-06`. CANONICAL cites
  that actual retaining tag, not a newer tag that lacks them.

Merged `origin/lane/2026-11-05-prune-s1` (`4fea8484f`, #654) into this group.
Its five source deletions were already present from the first prune, so they
were not restored/re-deleted. The two old stage-1 report/harness files were
not reintroduced into today's tree; the merge parent preserves them at
`4fea8484f:docs/run_reports/2026-11-05-prune-s1.md` and
`4fea8484f:docs/run_reports/2026-11-05-prune-checks.txt`.

## Files and references

Edited `CANONICAL.md` (one verdict per candidate and current producer map),
`tests/test_mlx_runtime.py`, `scripts/test_timings.json`,
`configs/pins/registry.json`, `docs/phase_3/kv_feasibility.md`,
`docs/phase_2/suite_implementation_research.md`, and the retired-script citation
in historical `docs/process/TRIM_REPORT.md` (with an explicit annotation).
Added the per-candidate inventory and this report. No refusal site or current
number-coverage row was deleted; `hazard_refusals.json` and coverage tables
therefore stay unchanged. The retained runtime truncation assertions still
protect the production decode-count behavior.

Per-deletion source grep includes imports, paths, tests, manifests, scanners
and `.github/`: zero live/unqualified narrative hits. Residuals before this
report was staged: seven qualified archive references, eight historical
inventory/audit hits, and three frozen-record references. The latter are
original sealed-inventory metadata and commit-scoped registry bindings, not
current filesystem readers. Immutable audit JSONL and original sealed digest
values were preserved. No inspected live v4 artifact inventory binds any of
the three present G4 candidates.

## Verification

One unittest module at a time, Python 3.13, supplementary path/network guard
and synthetic TMPDIR as documented in g1:

- `python3.13 -B -m unittest tests.test_mlx_runtime`: 42 OK, synthetic stand-ins;
  no native MLX execution, Metal device, model load or weights download.
- `python3.13 -B -m unittest tests.b5_analysis.test_frozen_files`: 4 OK.
- `python3.13 -B -m unittest tests.test_b5_seal_landing`: 9 OK.
- `python3.13 -B -m unittest tests.test_docs_freshness`: 31 OK.
- `python3 -m compileall -q joulewise scripts tests`: PASS.
- `python3 -B scripts/repin.py --write registry`: completed; `--check`: PASS, all 16 families current. No protected number was repinned from changed bytes.
- Final source-reference audits for g1/g2/g4: zero live or unqualified
  narrative hits. Exact final deletion set equals the three inventories
  (409 paths after the F5 synthesis restoration); all blob-preservation checks passed.
- Prune diff after F5: 409 deletions, 43 additions, 16 edited original paths; protected
  coordination/deferred source and both retained generators have no diff.
  Frozen `run_campaign.py`, `whole_window.py` and B5 analysis source also
  compare byte-identically. Zero surviving resolved protected registry
  bindings were lost (compared by holder/family/target, ignoring moved line
  coordinates). `dcaf2ca2c` is an ancestor.
- `git diff --check`: PASS. The tracked-file count after F5 is 4,762, before
  adding the cold-review and fixes reports.

Independent source/metadata review by `prune_readers_review` confirmed the
sole spike/test deletion, both generator KEEP decisions, absence of v4
bindings, and the older retaining tag for #654. Final review found all retained MLX runtime test ASTs unchanged and both
retained generators byte-identical to main. Final diff review remains this
seat's. Final independent review also confirmed all retained MLX test ASTs unchanged
and both retained generators byte-identical to main. All required
reviewable-tree checks pass as recorded; exploratory
prototype failures/fixes are separated in g3's report. Full suite is CI's job. Guarded unittest runs across the session, including
exploratory failures, totaled about 163 seconds; all guarded commands including
registry regeneration/checks totaled under ten minutes.

## Stack outcome and remaining ruling

| Group | Commit / status | Deleted files |
|---|---|---:|
| g1 traces/reports | `98bc99fd4` plus its ops-plan merge parent; F5 synthesis restoration | 111 |
| g2 campaigns | `a7bacd7b1` | 297 |
| g3 CA-42 | `30098da9d`, KEEP / owning ALIGN migration required | 0 |
| g4 spikes | this merge commit | 1 |

The prepared four-branch stack, with F5 applied, removes **409** original files. It adds 33
plan/tool/evidence files via the explicitly requested ops-branch merge and ten
inventory/report/helper/pointer files. Expected tracked main count if this
safe stack lands: **4,762**, from **5,128** (net −366), before adding the
cold-review and fixes reports. This count includes g3's
KEEP disposition; it is not a claim that the CA-42 retirement is complete.
A future approved g3 migration needs its own revised count and verification.

The only blocking ruling is in the g3 report: keep CA-42 held until the ALIGN
owner migrates the registered executed closure, or commission an explicitly
scoped joint migration after the active R1 gate. Recommendation: KEEP now.
#668 remains held; #654 is folded in. No coordination task was registered.

DEFER unchanged: `joulewise/b5_analysis/**`, `whole_window.py` mirror, remote
node/SSH/vLLM/NVIDIA stack, site/report pipeline, scored modules, every ALIGN
v4 path/lane, BYTES, B6, x86 and port work. Protected source and original digest
values have no diff. No new native test is required for the code-free groups
or isolated spike retirement. If g3 is commissioned later, its lead must run
the owning ALIGN closure/registration gates and dynamic
`tests.hazards.test_import_graph.ImportGraphTests.test_a_complete_arm_and_monitor_run_load_no_retired_module`
outside this sandbox, plus the required native/hardware gates for that lane.
None of those gates may disturb the pinned running measurement checkout.

Next exact step: review g1/g2/g4 and obtain the g3 ruling; CI runs the full
suite. Nothing was pushed. The unlandable g3 prototype remains scratch evidence,
not a landing candidate, at the path/digest recorded in its report.
