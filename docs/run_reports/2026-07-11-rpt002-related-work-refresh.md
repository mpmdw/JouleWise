# RPT-002 related-work refresh and verification fold-in

Date: 2026-07-11  
Branch/worktree: `impl/rpt002`  
Lane: `[AGENT]`, report-source only  
Authority: hardening C8 plus the lead's completed primary-source verification

## Outcome

RPT-002 is complete in this worktree. The original eleven-source survey is
preserved, and all seven RPT-002 records are now
`VERIFIED_AGAINST_PRIMARY` with retrieval date `2026-07-11`. The canonical
bibliography, source map, related-work draft, and assembled chapter contain the
lead-corrected metadata and boundary-honest claim language.

The two root handoff files, `LEAD-VERIFICATION-1-4.md` and
`LEAD-VERIFICATION-5-7.md`, were read in full and absorbed into the canonical
artifacts below. They were then deleted because they were transient handoff
artifacts, not repository documentation.

## Per-source applied changes

| Stable id | Metadata applied | Claim, boundary, and artifact wording applied |
|---|---|---|
| `revisiting-disaggregation-energy-2026` | EuroMLSys '26 `paper-conference`; five authors; 2026-04-27; pp. 397-406; DOI `10.1145/3805621.3807662` | Load/baseline/transfer sensitivity attaches to performance; higher disaggregation energy is essentially unconditional; bounded to one two-A100 PCIe Gen3 node and pynvml+RAPL+IPMI J/token. |
| `dualscale-2026` | Four authors; arXiv v3 dated 2026-04-03; arXiv-only preprint | Phase placement/per-phase DVFS confirmed; homogeneous 16xH100/two-node InfiniBand scope; energy is GPU-only 10 ms NVML, never node/cluster level. |
| `prima-cpp-2025` | Exact title; eleven authors; v3 dated 2026-07-04; ICLR 2026 `paper-conference` | v3 energy evaluation stated as fact; whole-run Wh/1K output tokens, device-side communication accounting, no wall power or per-stage split; niche stated as “per-stage both-end split, boundary-labeled discipline, re-reducible bundles.” |
| `splitzip-2026` | Two authors; arXiv v3 dated 2026-06-23; arXiv-only preprint | Bitwise losslessness and 5.7%/92.9%/1.4% online performance shares confirmed; no energy implication; code release recorded as CC BY 4.0. |
| `systematic-quantization-2025` | Two authors; v1 dated 2025-08-22; arXiv-only preprint | Task/workload/method/GPU and bit-width-tuple claims confirmed; A100/H100 GPU-only J/token boundary; no edge/consumer generalization; no artifact released. |
| `sustainable-edge-ai-2025` | Full title; eight authors; v1 dated 2025-04-04; arXiv-only preprint | Single Raspberry Pi 4 4 GB, CPU-only; 28 Ollama models, weight-only PTQ, five accuracy benchmarks; whole-device DC-input Joulescope boundary; mean±SD only, no rigorous-UQ claim; artifacts stated available but release unverified. |
| `silicon-showdown-2026` | Two authors; v2 record with issued date 2026-05-01; arXiv-only preprint | Ecosystem-as-deployed comparison with unmatched runtime/artifact/precision stacks; PyNVML GPU-board versus powermetrics whole-SoC boundary; every repeated 23x headline flags those unmatched boundaries; no accuracy evaluation and no artifact release. |

## Files

Created in the RPT-002 stream:

- `docs/report_src/references.csl.json`
- `docs/report_src/source_map.json`
- `tests/test_rpt002_related_work.py`
- `docs/run_reports/2026-07-11-rpt002-related-work-refresh.md`

Modified in the combined RPT-001/RPT-002 worktree:

- `docs/phase_4/related_work_draft.md`
- `docs/phase_4/phase_4_exit_checklist.md`
- `docs/report_src/README.md`
- `docs/report_src/chapters/03_background_and_related_work.md`
- `docs/report_src/report.json`
- `scripts/build_capstone.py`
- `tests/test_rpt001_report_slice.py`
- `RUN_STATE.md`
- `TASK_QUEUE.md`

Deleted after absorption:

- `LEAD-VERIFICATION-1-4.md`
- `LEAD-VERIFICATION-5-7.md`

No claims-engine file, `scripts/claims_lint.py`, `PROJECT_STATUS.md`, generated
site file, or retained evidence bundle was changed. No commit was created.

## Verification

JSON parsing:

```text
python3 -m json.tool docs/report_src/references.csl.json
python3 -m json.tool docs/report_src/source_map.json
python3 -m json.tool docs/report_src/report.json
all exited 0
```

Focused RPT-001/RPT-002 tests (`/tmp/rpt002-focused-tests.txt`):

```text
.......make_figures: ERROR: bundle tree hash mismatch for example-mac-mlx-local__r1
.............
----------------------------------------------------------------------
Ran 20 tests in 0.020s

OK
```

The `make_figures` line is expected stderr from the tampered-bundle negative
test; the test command exited 0.

Report build/check:

```text
build_capstone: assembled build/capstone/rpt001/report.md sha256=161285db7bb2bf75b5daa3de2f2c007ad6048617c624b574bad4a413e8783bf5
build_capstone: check OK (no drift)
```

Claims lint:

```text
python3 scripts/claims_lint.py --mode all       # exit 0; existing warning-only review list, no errors
python3 scripts/claims_lint.py --mode phase4    # claims_lint: clean
```

Canonical suite was run unpiped with stdout/stderr redirected directly to
`/tmp/rpt002-canonical-suite.txt`:

```text
----------------------------------------------------------------------
Ran 1050 tests in 68.285s

OK (skipped=13)
```

`git diff --check` also exited 0.

## Unapplied lead instructions

None. Every metadata correction, claim confirmation/contradiction, boundary
caveat, novelty rewording, and artifact-status instruction in both lead
handoffs was applied.

## Next exact step

Lead reviews the RPT-002 diff by pathspec and decides whether to commit it. No
additional primary-source gate remains for these seven records.
