# Saturday Flash-Next handoff

Branch: `lane/2026-11-07-qwen4exp-mbp-live`, based on `65763077a` (checked-out
canonical / PR #675 head). Local commits only; nothing pushed. No network,
study data, real weights, MLX execution or live measurement was used here.

New: [the ordered Mac runbook](docs/align/qwen4_exp_port/mbp_live.md),
`scripts/qwen4exp_mbp_live.py` (download, verified conversion, supervised
memory/quality/benchmark/performance/paging, offline hosted comparison),
`scripts/qwen4exp_bf16_benchmark.py` (same items on an operator-verified bf16
completions host), `scripts/qwen4exp_mbp_report.py`, fixture/native tests, a
generated-results template and a lead-owned GOAL status-log entry template.

Reused from local `origin/lane/2026-11-05-qwen4exp-port-evals` / PR #671:
the two eval clients, item builder, fixed item sets, official XML template
fixture, tests and validation notes. Only the e2e client's provisional
maxfit/maxfit5 threshold labels were added; they use the existing strict
8-bit screens, not a measured quantization-error claim. The existing canonical
converter/module are unchanged. Full streamed real-weight gold is separate
PR #680 and was neither imported nor executed.

Commits:

- `922ba22fa`: reuse PR #671 harness and label maxfit screening profiles.
- `b6d15b6b2`: Saturday runbook, supervised probes, report renderer and tests.
- A final docs-only commit records this handoff and the dated run report;
  identify its exact hash with `git log -1 --oneline`.

## Exact Saturday sequence

First complete runbook step 0: operator verifies the M3 Max, APFS external
disk, free space, approved venv and no measurement/analysis/agent jobs. Set
`PY` to that venv, `DISK` to the actual SN7100 physical diskN and
`BF16_ENDPOINT` to the separately verified bf16 host. Use the runbook's
environment/cache/caffeinate setup and native tiny-test commands. These
commands are for the operator outside this sandbox; none were run here.

```sh
export BASE=/Volumes/JW-EXT/flashnext
export RUN="$BASE/evidence/20261107-maxfit"
export ARTIFACT="$BASE/models/maxfit"
export PROFILE=maxfit
mkdir -p "$RUN" "$BASE/models"

"$PY" -B scripts/qwen4exp_mbp_live.py download --dry-run
"$PY" -B scripts/qwen4exp_mbp_live.py download --validation-only --out "$RUN/download.json"
export SOURCE_RECEIPT="$RUN/download.json"
export SOURCE="$("$PY" -B -c 'import json,os; print(json.load(open(os.environ["SOURCE_RECEIPT"]))["snapshot"])')"
"$PY" -B scripts/qwen4exp_mbp_live.py convert --validation-only \
  --source-receipt "$SOURCE_RECEIPT" --artifact "$ARTIFACT" --profile "$PROFILE" --out "$RUN/convert.json"
export CONVERT_RECEIPT="$RUN/convert.json"
export PIN="$("$PY" -B -c 'import json,os; print(json.load(open(os.environ["CONVERT_RECEIPT"]))["manifest_sha256"])')"
(cd "$ARTIFACT" && shasum -a 256 -c "$RUN/convert.json.SHA256SUMS")
"$PY" -B scripts/qwen4exp_mbp_live.py memory --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" --out "$RUN/memory.json"
# STOP on an abort. Only then use runbook step 2's complete maxfit5 branch.
"$PY" -B scripts/qwen4exp_mbp_live.py quality --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" --out "$RUN/quality.json"
# Save the independently verified bf16 identity receipt described in step 4 first.
"$PY" -B scripts/qwen4exp_bf16_benchmark.py --validation-only \
  --endpoint "$BF16_ENDPOINT" --tokenizer "$SOURCE" \
  --identity "$RUN/bf16-identity.json" --out "$RUN/bf16-benchmark.json"
"$PY" -B scripts/qwen4exp_mbp_live.py benchmark --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" \
  --reference "$RUN/bf16-benchmark.json" --out "$RUN/benchmark.json"
"$PY" -B scripts/qwen4exp_hosted_reference.py plan --provider vllm-selfhost --base-url "$BF16_ENDPOINT"
"$PY" -B scripts/qwen4exp_hosted_reference.py collect --provider vllm-selfhost \
  --base-url "$BF16_ENDPOINT" --live --max-cost-usd 0.25 --traces "$RUN/bf16-traces.jsonl"
"$PY" -B scripts/qwen4exp_mbp_live.py hosted --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" \
  --provider vllm-selfhost --reference "$RUN/bf16-benchmark.json" \
  --traces "$RUN/bf16-traces.jsonl" --out "$RUN/hosted.json"
"$PY" -B scripts/qwen4exp_mbp_live.py performance --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" \
  --prefill-step 512 --out "$RUN/performance-512.json"
"$PY" -B scripts/qwen4exp_mbp_live.py performance --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" \
  --prefill-step 2048 --out "$RUN/performance-2048.json"
"$PY" -B scripts/qwen4exp_mbp_live.py paging --validation-only \
  --artifact "$ARTIFACT" --manifest-sha256 "$PIN" --profile "$PROFILE" \
  --disk-device "$DISK" --out "$RUN/paging.json"
"$PY" -B scripts/qwen4exp_mbp_report.py --run-dir "$RUN" --out "$RUN/results.md"
```

Finish runbook step 7: record code/evidence digests, complete human result
review, retain immutable raw files, release volume handles, eject successfully
and physically unplug. Append the GOAL entry only after lead review. If the
bf16 host is unavailable, omit hosted collection, run benchmark without
`--reference`, and leave its comparison gate OPEN. Do not substitute FP8.

## Verification and remaining gates

- `python3.13 -B -m unittest tests.test_qwen4exp_mbp_live`: 26 tests, OK,
  3 native skips (23 executed).
- `python3.13 -B -m unittest tests.test_qwen4exp_e2e_eval`: 37 tests, OK,
  21 skips (jinja2/transformers/MLX/optional fixture dependencies absent).
- `python3.13 -B -m unittest tests.test_qwen4exp_hosted_reference`: 13 tests,
  OK, 8 skips; no local HTTP socket test ran because jinja2 is absent.
- Targeted `compileall` over joulewise/tests and the six lane scripts: PASS.
  New files also parse with Python 3.11 grammar; no Python 3.11 runtime claim.
- Runbook's 15 shell blocks: `zsh -f -n` exit 0. The shell emitted a sandbox
  `nice(5)` warning; no command in those blocks was executed.
- Full suite deliberately not run: user prohibited it while seven-worker
  analysis is active. Coordination state files were not changed.

Risks/uncertainty: native MLX APIs, Metal behavior, real source download,
conversion, no-swap fit, throughput and device ancestry are unverified here.
The lead must run the three native tests in `tests.test_qwen4exp_mbp_live`
and the complete reused e2e module on the Mac before real-weight probes.
The mmap resident-page cap is operational monitoring, not an OS cache quota;
Metal is a resident-model proxy requiring the lead's 10% accounting review.
The first paging pass is not automatically cold; whole-disk I/O is not
exclusive PLE traffic. bf16 host identity needs server-side evidence and no
host is provisioned. P5 speed targets are e3 extrapolations; maxfit thresholds
remain provisional. GOAL 11 still needs separate full-gold evidence.

Independent read-only review found and the lead fixed per-pass I/O scope,
physical disk binding, duplicate artifact hashing, reference identity/item
coverage and generation-config comparability. Native canonical loader/QSA/PLE
coverage was added. No code or scientific acceptance ruling was delegated.
Next exact step: lead reviews the commits, prepares the approved Mac venv,
and runs runbook step 0's native fixture module outside the sandbox.
