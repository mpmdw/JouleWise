# monitor-arm — v5 fan-out handoff

Branch: `align/2026-11-08-v5-monitor-arm`, based on W1/R10 `d600baba0`.
Implementation commits: `4e6672b1d`, `9d822d050` (complete roster binding),
`4588d4719` (identity-only native endpoint compatibility).
**PROVISIONAL: synthetic verification only.**
No registration, live score, measurement, model load, download or network call
was made. The requested remote briefs were read from cached Git refs; no fetch
was attempted under the no-network rule. Coordination state and R1's lane were
left alone. This report is the handoff required by the fan-out brief.

## Built and files touched

- `joulewise/align/shade/monitor.py`: versioned `readable` JSONL view. It shows
  separate native reasoning and exact tool-call argument strings, removes closed
  content scratchpads only, and retains user/tool evidence and whitespace.
  System instructions stay out of the monitor query. Existing SHADE names-only
  views retain their behavior. Legacy unescaped `jw_reasoning` messages remain
  wholly visible because their native spans cannot be separated losslessly.
- `joulewise/align/records.py`: additive `readable` visibility.
- `joulewise/align/shade/recount.py`: exact runtime-template/ID audit, including
  system/side-task prefill and tool schemas. `EndpointRecountCodec` reuses a
  prepared Apple endpoint without generating. Recount failures remain explicit;
  logged counts are never repaired. Full-vs-reported work deltas retain omitted
  calls' intercept, prefill, decode and both integrated attention terms from
  protocol v4. No energy outcome is read or calculated.
- `joulewise/align/shade/scoring.py`: provider-neutral `MonitorClient`, existing
  `ChatEndpoint` adapter, frozen plan/prompt/code/client pins, anonymous stable
  ordering, and a CLI. Exactly one frontier API primary and at most one local
  secondary. Temperature 0 uses one sample; positive temperature uses three
  with fixed seeds and their mean. Ambiguous/invalid/truncated/drifted/error
  replies yield missing scores, never zero. Partial replies and monitor-native
  reasoning are retained privately. Every request and completed sample is
  journaled immediately, including interrupted three-sample calls.
- `tests/align/test_monitor_readable.py` and `test_monitor_scoring.py`: synthetic
  fixtures and fake clients, including the production Apple XML renderer seam.
- This report.

## Registration and custody interface

Use `score_batch` or `python3.13 -B -m joulewise.align.shade.scoring` for v4/v5.
The pre-existing generic `ShadeMonitor.score` has no campaign provenance and
must not be used directly for v4. All batches through the new interface require
registration, including diagnostic batches; there is no version/pilot bypass.

The new adapter receipt schema is `joulewise.align.monitor_registration.v1`:
`status="registered"`, `study_id`, `plan_sha256`, `registration_sha256`,
`pipeline_code_sha256`, sorted complete `window_ids`, `transcript_roster_sha256`
(all planned anonymous member IDs per window), and `lead_signature`
starting `Lead: `. The caller must also supply the receipt's expected SHA-256
from trusted custody and the frozen registration document bytes. No receipt
issuer is supplied. The signature text is not cryptographic authentication of
registration; the lead authenticates that authority and maps the eventual
v5/squeeze registration receipt to this adapter. The gate runs before transcript
reads, provider factory import or scoring. Source hashes and the entire roster
are checked before any scoring request.

Plan JSON is `dataclasses.asdict(ScoringPlan(...))`. CLI `--print-pins` prints
only plan/prompt/code hashes; `--help` lists the explicit inputs. The lazy
`module:function` factory takes the plan and returns `{monitor_id: client}`.
Input manifests name windows, anonymous IDs, transcript hashes and recounts;
paths stay relative to the manifest, with escape/symlink checks.

Binding mode requires recounts pinned to full messages, readable view, tokenizer,
template policy and tools. `require_recount=False` must itself be registered
and is labelled diagnostic in the seal. Monitor-format token counts include
JSON framing and are explicitly separate from the runtime energy counts.

Seals are `PRIVATE_DIR/<batch-id>/<window-id>/monitor_scores.json`, plus private
request/sample journals and batch start/completion manifests. Directories use
0700 and files 0600; these are filesystem custody, not encryption. Existing
batches cannot be overwritten or silently resumed. Public output contains only
batch identity and parse counts. No unsealing/energy-joining route was added.

## Verification

Each unittest module ran in its own process; no full suite or B5 pipeline ran.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_monitor_readable` | 13 passed |
| `python3.13 -B -m unittest tests.align.test_monitor_scoring` | 24 passed |
| `python3.13 -B -m unittest tests.align.test_shade` | 23 run, 4 optional upstream-cache tests skipped |
| `python3.13 -B -m unittest tests.align.test_records` | 4 passed |
| `python3.13 -B -m compileall -q joulewise/align/shade joulewise/align/records.py tests/align/test_monitor_readable.py tests/align/test_monitor_scoring.py` | passed |
| `git diff --check` and staged equivalent | passed |

The SHADE run used empty `JOULEWISE_SHADE_CACHE` and disabled global/system Git
config; its source fixtures were temporary synthetic repositories. Red-first
checks caught native-tag deletion, unverified cached counts, incomplete receipt
and recount bindings, lost partial replies, and lost earlier samples after an
interruption. A final coverage test verifies that a missing member is refused
before transcript reads even when its window remains nonempty. These became
passing regressions. No native MLX compute was run.

## Lead assumptions, uncertainty and next step

Assumed the brief's binding rulings: v4 stays frozen apart from meter/full-log
capture; frontier off-box primary/local secondary; no v4 scoring before squeeze
registration; outcomes stay sealed. This lane changes no measurement settings,
cohort sizes, thresholds, energy estimand or escape-rate estimator.

Before registration/use, the lead must pick the exact monitor snapshots, budget
and verified SHADE instruction bytes; review the new receipt adapter and strict
single-verdict/missing-score policy; and arrange the complete post-T3 batch and
joint release under existing custody. No actual receipt or monitor model was
selected here. Seeds freeze requests, not provider reproducibility; absent
provider revision metadata cannot independently establish server identity.

**Native checks outside this sandbox:** exercise synthetic conversations under
the actual frozen D tokenizer/template/history policy, including native reasoning,
tool arguments, cached prefixes, EOS and length cuts. The codepoint fixtures and
real-renderer seam do not establish native tokenisation compatibility. Exact
template suffix reconstruction or BPE/special-token roundtrip can reject valid
native outputs; this remains unverified, with no tolerance silently introduced.
No MLX-dependent automated test was added because no native computation changed.

Next: lead's independent executing review of this branch, then native synthetic
recount checks and registration integration. Only after those gates should the
registered complete batch be scored off-box. Author self-review is complete;
independent review and scientific registration approval are pending.
