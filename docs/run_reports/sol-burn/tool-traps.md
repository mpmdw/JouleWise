# Tool-trap audit: overlapping producers on the block-5 path

Date: 2026-11-06

Scope: tracked repository code and synthetic timing records only. No experiment-data
root was opened. This is a static call-path audit, not a claim about untracked
operator commands.

## Executive ranking

| Rank | Overlap | Live-path finding | Impact | Disposition |
|---:|---|---|---|---|
| 1 | `scripts/independent_recompute_b5.py` versus `scripts/run_b5_analysis.py` / `joulewise.b5_analysis` | The independent, standard-library recompute predates the optimized L9 runner, but no tracked non-test program invokes it. The live runner instead executes the complete sealed pipeline twice. | **Critical:** the synthetic production-shaped runner still took 5,872 s with default workers after a 5.7x optimization; the pre-optimization total was 21,215 s. | Wire orchestration to launch the recompute beside the blind run and make `compare_b5_recompute.py` the explicit convergence gate. Do not replace registered L9 computation without the governing amendment. |
| 2 | `joulewise.b5.harvest.assess_member(s)` versus L9 steps 1–2 | Harvest already performs strict validation and re-reduction in a process pool with a per-worker physics cache and records whether the result is byte-identical to the stored summary. L9 nevertheless validates and re-reduces the same bundles again; later L9 steps do not consume step 2's products. | **High:** 82 identical calibration refits consumed 594 of the first 941 s in the recorded joined run. The later speedup reduced, rather than removed, this repeated work. | Authenticate and consume harvest's withheld assessment/re-reduction digests at L9 step 2; retain one independently implemented recomputation where independence matters. |
| 3 | L9 blind mode versus L9 release mode | One CLI dispatches the same steps over the same inputs twice; release mode's distinguishing job is digest equality, but it recomputes every output before comparing. | **Medium/high:** at the measured optimized synthetic duration, a second full pass is another 5,872 s (1 h 37 m 52 s) of runner time. | Keep the dry-run bytes immutable and run a narrow authenticated input/output-digest verifier after release, unless the sealed plan continues to require full replay. This is a policy-gated trap, not a safe unilateral code deletion. |

The ranks use avoidable wall time first, then risk of maintaining two arithmetic
implementations. Rank 1 is the exact “better tool already exists” case. Rank 2
is an existing-result-not-consumed case. Rank 3 is a narrower duplicate-mode
case whose removal needs authority.

## 1. Independent recompute exists, but the optimized pipeline owns the live command

### Evidence

* The independent tool declares that it uses only the Python standard library
  and computes energy and reported statistics itself
  (`scripts/independent_recompute_b5.py:2-6`). Its initial commit is
  `ab14e02d80d27c61d9ecfdff92e5adc641848c47`, authored
  `2026-10-14T02:48:37-07:00`, with subject “Independent block-5 recompute:
  headline numbers from raw power records, no L9 code.”
* The operator-facing L9 command is explicitly `scripts/run_b5_analysis.py`; its
  help runs steps 0–11 in blind mode and the same steps again in release mode
  (`scripts/run_b5_analysis.py:2-23`). Its `--workers` option parallelizes steps
  1, 2, and 4 (`scripts/run_b5_analysis.py:29-32`).
* A repository census
  `rg -n "independent_recompute_b5|compare_b5_recompute" --glob '!docs/**' --glob '!tests/**' --glob '!.codex-report/**' .`
  found **six** matches: one schema declaration in the recompute and five
  explanatory comments in the comparator. It found **zero invocation or import
  sites**. Thus “unused” here precisely means *not connected by tracked runtime
  code*; it does not assert that an operator has never typed its command.
* The optimization report says the frozen outputs were byte-identical and the
  default-worker runner became 5.7x faster (`.codex-report/L9-SPEEDUP-R1.md:1-9`).
  Its measured synthetic totals are 21,215 s before and 5,872 s after
  (`.codex-report/L9-SPEEDUP-R1.md:220-235`). That is a 15,343 s optimization,
  but it does not connect the already-independent producer.

### Why this is a trap

The repository invested in accelerating the monolithic path while the independent
producer remained a disconnected sibling. The tools are not byte-for-byte
substitutes: independence is the recompute's value, and L9 carries custody and
sealed-plan semantics. The actionable correction is therefore orchestration,
not deletion: run them concurrently, then use the already-present comparator.
This converts duplicate elapsed time into independent checking rather than
serial ceremony.

## 2. Harvest computes and authenticates work that L9 computes again

### Evidence

* Harvest's `assess_member` performs strict validation and calls `reduce_bundle`
  (`joulewise/b5/harvest.py:2437-2443`, `:2473-2489`). It writes the re-reduced
  bytes once and records `identical_to_stored` (`joulewise/b5/harvest.py:2487-2494`).
* Harvest owns a calibration cache keyed by authenticated calibration bytes;
  the comments say cache hits skip only a refit after hash checks
  (`joulewise/b5/harvest.py:2412-2418`). `assess_members` already has a
  `ProcessPoolExecutor` path (`joulewise/b5/harvest.py:2549-2553`), and the
  collector persists all assessments under
  `withheld/member-assessments.json` (`joulewise/b5/harvest.py:4270-4275`).
* The joined-run record measured 146 uncached refits in step 1, while the cached
  run needed three in step 1 and zero in step 2
  (`.codex-report/L9-2.md:146-159`). The audit's earlier measured slice was 82
  identical refits taking 594 of 941 s; that measurement is preserved in
  `docs/process_traces/2026-10-27-pipeline-audit/segments.json:1126` and
  independently restated at `:1949`.
* The dry-run validator itself admits outputs under a `rereduced/` namespace
  (`joulewise/b5_analysis/dry_run.py:478-484`), while harvest has already stored
  the byte comparison. This is overlapping production work, not merely similar
  naming.

### Why this is a trap

The optimized L9 cache is worthwhile if L9 must independently repeat the work,
but step 2's re-reductions are commitments rather than inputs to later arithmetic.
That makes the harvest evidence the better existing primitive for this slot:
authenticate its digest and stored byte-equality result rather than regenerate
the same artifact hundreds of times. Independence should be spent once—in the
rank-1 recompute—not by repeatedly driving the same repository reducer.

## 3. Release mode repeats the whole producer to perform an equality check

### Evidence

* The CLI contract says blind mode runs steps 0–11, while release mode “runs the
  same steps again from the same bytes” and compares every input and output
  digest (`scripts/run_b5_analysis.py:11-23`). Both modes dispatch the same
  `joulewise.b5_analysis.dry_run.run` entry point
  (`scripts/run_b5_analysis.py:114-117`).
* The optimized synthetic total is 5,872 s (`.codex-report/L9-SPEEDUP-R1.md:220-235`),
  so a same-duration second pass costs another 5,872 s. This is an estimate from
  the recorded synthetic total, not a claim about live hardware.

### Why this is a trap—and the boundary

The narrow job unique to release is proving that the authenticated inputs and
outputs match the blind record. A small verifier can do that without reproducing
all number generation. However, the current help text makes the second execution
part of the sealed protocol, so this is **not** a recommendation to silently
change the runnable path. Amend the plan first, then prove the verifier accepts
the unchanged synthetic record and rejects one-bit mutations of every bound
input and output.

## Candidates checked and cleared

These name pairs looked suspicious but are not current live-path traps:

* **Legacy versus generalized floor mint.** L9 step 5 imports
  `mint_floor_artifact_generalized`, not the hard-pinned legacy sibling
  (`joulewise/b5_analysis/dry_run.py:1195-1212`). The better/generalized tool is
  already on the live path.
* **Analysis-manifest v1/v2/v3.** The live block-5 custody path imports the v3
  validator (`joulewise/paper_custody.py:733-746`), while the input layer retains
  explicit schema dispatch for old versions
  (`joulewise/analysis_engine/inputs.py:800-819`). That is compatibility, not an
  accidentally selected older implementation.
* **Arm-readiness generator versus evidence authors.** The evidence author emits
  a command that deliberately calls `generate_arm_readiness.py freeze`
  (`scripts/author_arm_readiness_evidence.py:51-60`). They are sequential producer
  and consumer-facing stages, not competing CLIs.

## Recommended order of work

1. Add one tracked, structure-only orchestration command that launches L9 and
   the independent recompute concurrently and then invokes the comparator.
2. Specify a digest contract from harvest's `member-assessments.json` and
   withheld re-reductions into L9 step 2; test old versus new synthetic outputs
   byte-for-byte before changing the default.
3. Seek the plan amendment for a digest-only release verifier. Keep the full
   replay available as an audit command, not the mandatory happy path.

## Reproduction and safety

Only repository files and Git metadata were read. The measured figures above
come from committed synthetic/audit records; no live experiment path was
accessed. This report changes no executable path, so happy-path analysis outputs
are byte-identical by construction. Verification used:

```text
git status --short --branch
git log --diff-filter=A --follow --format='%h %ad %s' --date=iso -- <candidate>
rg -n "independent_recompute_b5|compare_b5_recompute" --glob '!docs/**' --glob '!tests/**' --glob '!.codex-report/**' .
git diff --check
```
