# Adversarial review: qwen4_exp real-weight gold-parity harness

**Review date:** 2026-11-06  
**Reviewed head:** `12bf3f72559485dfe2f5ce252e186557d6d32514`  
**Requested lane:** `lane/2026-11-05-qwen4exp-gold-adapter` (PR #680, stacked on PR #667)  
**Reviewer posture:** false PASS is the worst outcome. This was a read-only code review of the harness; only this review record was added.

## Executive verdict

**Do not accept a real-weight PASS from this head.** I found two high-severity false-PASS paths and two material provenance/validation gaps. The most important defect is resume: a case report is trusted as the verdict-bearing object but is not itself authenticated. The second is the A1 normalization amendment: it turns one input outlier into a trace-wide tolerance allowance, so unrelated output elements can pass with an allowance derived from a different element.

The ordinary missing-trace, reference-chain, candidate-self-comparison, sparse-row extraction, and QSA tie-scope paths otherwise appear fail-closed in the reviewed code. In particular, required reference traces set `reference_valid = false`; required candidate traces prevent `passed`; real chaining returns the reference `output.npy`; sparse rows are copied from LFS-hash-verified source shard offsets; and the `Tensor.topk` patch is entered only by the wrapped QSA indexer's `forward` call. Those positive observations do not cure the findings below.

## Findings

### GH-01 — HIGH — Resume trusts mutable `report.json`, allowing a prior mismatch to become PASS

**Location:** `joulewise/align/qwen4_gold/runner.py:200-211, 278-286, 355-368`; `joulewise/align/qwen4_gold/stream.py:402-410`

**Evidence.** `reusable()` parses the existing case `report.json`, checks its embedded fingerprint, `reference_valid`, and a map of `.npy` artifact hashes, but does not authenticate the report bytes or independently recompute the verdict. It explicitly accepts every status except `MLX_ERROR` and `REFERENCE_ERROR`. On reuse, `Harness.case()` appends that parsed report directly to `self.rows`; `publish()` later treats the report's stored `status == "PASS"` as authoritative. The stream then records the aggregate unit result and calls it PASS.

This creates a direct false-PASS path: after a genuine numerical FAIL, changing only the case report's `status` to `PASS` (or changing stored metrics and status together) leaves all `.npy` hashes valid and the fingerprint unchanged. `--resume` accepts it without comparing a single tensor. This also means filesystem corruption or an interrupted/manual recovery that changes verdict JSON is not detected, despite the documentation's stronger claim that resume integrity-checks results. The completed-unit hash in `stream.py` is too late: it authenticates the newly generated aggregate, which was built from the already-trusted mutable case report.

**Concrete fix.** Never reuse a verdict. Reuse only authenticated worker artifacts, then rerun the coordinator comparison and regenerate `report.json`. At minimum, put a digest of a canonical verdict payload in a separately committed resume manifest and verify the report hash, but recomputation is preferable and cheap relative to worker execution. Bind the complete artifact inventory (including both workers' `result.json`, request, trace-name mapping, shapes/dtypes, and report) rather than merely every discovered `.npy`. Add a mutation test: run a failing case, edit only `report.json` to PASS, resume, and require refusal or a recomputed FAIL.

### GH-02 — HIGH — A1 uses a trace-global maximum input error as every element's allowance

**Location:** `joulewise/align/qwen4_gold/core.py:517-560`

**Evidence.** `compare_norm()` computes `e_x = inputs["input"]["max_abs"]` (and the analogous global `e_z`) once for the entire trace. It then inserts those scalar maxima into `allowance` for every output element. A single input element near the ordinary tolerance limit therefore grants every element—across all rows/tokens/channels—an extra propagated allowance, even where the two norm inputs are bit-identical. The chained check can consequently accept a mismatch at element B using input error observed only at unrelated element A. For small-RMS rows or large norm weights the amplification can be large. The op self-checks do not close this hole: a candidate can faithfully compute the official norm of its locally wrong input while the layer-by-layer output difference is waived using another location's error budget.

This is not the documented per-element relationship implied by `P_c`; it is a worst-element-to-all-elements widening. It is especially risky because A1 was introduced specifically to change a previously failing verdict to PASS.

**Concrete fix.** Stream aligned input chunks and compute an elementwise (or rigorously group-local) `e_x = abs(x_ref - x_mlx)` and `e_z`, propagating only the errors that can influence the corresponding normalized group/output element. If a conservative bound needs a reduction, restrict it to the exact RMS group and row, never the whole trace. Add an adversarial two-row test: place the sole input error in row 0, an otherwise-unallowable output difference in row 1, and require FAIL; then confirm the causally corresponding row-0 difference can pass.

### GH-03 — MEDIUM — Resume provenance does not bind all executed reference/runtime code

**Location:** `joulewise/align/qwen4_gold/runner.py:41-54, 249-262`; `joulewise/align/qwen4_gold/reference.py:14-23, 147-158`; `joulewise/align/qwen4_gold/stream_ple.py:82-95`

**Evidence.** `runtime_identity()` hashes only `transformers/models/qwen4_exp/modeling_qwen4_exp.py`. The workers also execute `configuration_qwen4_exp.py`, Torch operators/binaries, NumPy, safetensors, and their transitive code. For those, the fingerprint records version strings only. Reinstalling or locally patching `configuration_qwen4_exp.py` (or replacing a wheel/build while retaining its version string) can change the official computation while leaving the invocation fingerprint unchanged, causing old results to be reused after executable code changed. Worker metadata repeats the modeling-file hash but does not validate it against the request or cover configuration source.

The candidate side has the same general problem for installed MLX/mlx-lm implementation code: versions are recorded, while the external canonical source files are hashed. Version equality is useful provenance but is not a code identity.

**Concrete fix.** Hash the complete installed distributions used by each worker (prefer RECORD-file identities plus hashes of all imported Python/native artifacts), or run from immutable wheel files/locked environments whose wheel SHA256s are in the fingerprint. At minimum bind `configuration_qwen4_exp.py`, package RECORD, Python executable, Torch/MLX build identifiers, and validate worker-reported source identities against the request before accepting traces. Add a resume test that changes configuration source without changing package version and requires a fresh work directory.

### GH-04 — MEDIUM — Sparse-PLE store validates file hashes but not its semantic row contract

**Location:** `joulewise/align/qwen4_gold/stream_ple.py:127-160, 163-215`; `joulewise/align/qwen4_gold/stream.py:352-368`

**Evidence.** Extraction correctly derives byte offsets from an authenticated full shard and records IDs. On consumption, however, `valid_entry()` checks only basename, existence, symlink status, and SHA256. `SparseCheckpoint.__init__()` does not verify that an entry's tensor name, IDs, shape, storage dtype, row-file shape/dtype, source shard SHA, and official plan are mutually consistent. `ngram_rows()` trusts `entry["ids"]` to select positions in the loaded array without first asserting the array has exactly the promised rows and storage representation.

In the normal uninterrupted producer path the fields are generated together, so this is not presently a demonstrated automatic substitution. It is nevertheless a provenance boundary: the shim's claim that rows came from the official table is established by mutable manifest assertions rather than revalidated semantics. A repaired/resumed store with a self-consistent new file hash but reordered `ids`, stale plan, wrong tensor association, or wrong source SHA can return a different official row under the requested ID. Both reference and candidate share the shim, so they can agree perfectly on the same wrong row and report PASS.

**Concrete fix.** Validate every entry against the current checkpoint weight map and pinned source metadata: exact tensor key, source shard and LFS SHA, partition shape/storage, sorted unique IDs equal to the official plan intersection, and `.npy` dtype/shape exactly matching `(len(ids), width)`. Commit a store root digest from canonical `(official-plan digest, source identities, entry metadata, row hashes)` and include it in the stream fingerprint/state transition. Add tests that swap two entry files/ID lists and that mutate source SHA/tensor association; both workers must refuse before lookup.

### GH-05 — MEDIUM — The advertised CPU test gate was mostly vacuous in this environment

**Location:** `tests/test_qwen4_gold_parity.py:18-34` (dependency gates); `tests/test_qwen4_gold_stream.py:17-22, 415-416`; `tests/test_qwen4_gold_canonical_adapter.py:25-39`

**Evidence.** The requested command reported 64 tests, but skipped 53. In this environment even NumPy/safetensors/Torch-dependent CPU comparator, resume, restage, sparse-PLE, official-reference, and tie-scope tests skipped. Only 11 policy/provenance tests executed. The command still exits success, so a green result here does not exercise the number-bearing comparator or most lifecycle claims. In particular, the strongest end-to-end CPU test uses a candidate double that copies the reference trace files verbatim (`tests/test_qwen4_gold_stream.py:584-612`), which can validate coordinator plumbing but cannot catch comparing the candidate against reference bytes by mistake; the test's own docstring acknowledges that limitation.

**Concrete fix.** Split test entry points into mandatory CPU and optional native groups. The mandatory gold-harness CI job should fail (not skip) when NumPy, safetensors, Torch, Transformers 5.22.1, and the official CPU stack are absent, and should report an asserted executed-test inventory. Keep Metal tests optional only on non-Mac hosts. Add an independent candidate fixture that computes known outputs without copying reference artifacts, plus negative mutations for every required trace and comparator branch.

## Targeted hazard disposition

| Requested hazard | Result |
|---|---|
| Missing traces treated as pass | No direct path found in a fresh run; reference omissions invalidate the chain and candidate omissions make `passed` false. GH-01 can bypass those fresh checks on resume by trusting edited status. |
| Tolerance misuse | **Found: GH-02.** |
| Comparing a tensor with itself | No production path found. The end-to-end CPU plumbing test deliberately copies reference traces, so it cannot disprove this class in production (GH-05). |
| Chain inputs taken from candidate | No path found: `Harness.case()` returns the reference `output.npy`, and stream chain records that returned path. |
| Sparse-PLE rows not official | Extraction path is byte-exact from authenticated shards, but consumer semantic binding is incomplete (**GH-04**). |
| QSA tie override leaks | No leak found in the single-threaded reference worker: the `torch.Tensor.topk` patch is scoped by a context manager around only the indexer instance's wrapped `forward`. |
| Resume stale after code changes | In-package `.py` files and declared adapter dependencies are hashed; installed/transitive runtime code is incompletely bound (**GH-03**), and verdict JSON itself is unauthenticated (**GH-01**). |
| SHA/provenance gaps | **Found: GH-01, GH-03, GH-04.** |
| Disk guard/restage corruption | No definite corruption path found. Full source shards are size/SHA checked before subset copying; subset bytes are hashed; guard runs before writes; committed subsets are rehashed on resume. |
| Tests that cannot fail | **Found: GH-05** for environment-skipped gates and the trace-copy end-to-end double's limited oracle power. |

## Verification performed

```text
PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  python3 -B -m unittest -v \
  tests.test_qwen4_gold_parity \
  tests.test_qwen4_gold_stream \
  tests.test_qwen4_gold_canonical_adapter

Result: OK; 64 discovered, 11 executed, 53 skipped.
```

No MLX/Metal result was attempted or inferred. No real weights were downloaded or executed.
