# Flash-Next engine desk lane — 2026-11-05

Branch: `lane/2026-11-05-align-flashnext-engine`, cut at requested base
`origin/lane/2026-11-05-align-pilot9-benign` =
`c9a0a39437614176bf4e14ff1565a6e4537328fb`. This is a static feasibility and
deferred-tooling run, not a measurement or model qualification.

## Result and recommendation

Read the window council's FINAL-DESIGN from its requested remote-tracking Git
object and the staged PR/model/template text. The main text components are
present. Highest risks are loss of QSA history under generic KV quantization,
conversion format/norm/quant-map incompatibilities, raw left padding, and
private-cache disk restoration. The detailed review ranks findings with source
line references and distinguishes repaired historical bugs from current risks.
The two staged Qwen3.8 templates are byte-identical XML templates.

Config-only estimates: 176.944B implemented text parameters including 51.200B
n-gram lookup weights; MTP and vision are omitted. BF16 KV/indexer plus recurrent
and convolution state at 40,960 tokens is 1.248 GB. Uniform affine Q4 is about
102.951 GB of weights and 116.199 GB with cache and a hypothetical 12-GB
workspace. The proposed E3/PLE4/other8 recipe is 90.145 GB of weights and
103.393 GB on that planning basis. Neither is a measured peak. The Q4/Q8 table
group sizes and scale/bias overhead materially change the conclusion.

Recommend Qwen3.8-27B 8-bit for W1 until an authenticated mixed Flash-Next
artifact passes the approved Mac desk, trusted-reference comparison,
integration, R1 and prospective registration gates. Preserve the anchors'
existing venv/member path. Nemotron 3.5 Bolt and Ling-3.0-flash cannot be called
qualified or ranked by capability from the available offline evidence.

## Changed files

- `docs/align/flashnext_engine_feasibility.md`: all six requested deliverables,
  source identities, ranked review, memory tables, environment/identity design,
  proposed selection thresholds and an exact future desk procedure.
- `scripts/align_flashnext_memory.py`: stdlib config-only parameter/cache/peak
  arithmetic; no engine import.
- `scripts/align_flashnext_common.py`: fail-closed desk/venv/package/source
  identity gates and complete artifact inventory verification.
- `scripts/align_flashnext_exactness.py`: deferred tiny/real prefill, chunk,
  causality, left/right padding, batch finalize/extract, hybrid checkpoint,
  generic disk cache and KV-quantization checks. Known unsupported paths remain
  failing diagnostic records. BF16 cache copies preserve values without
  requiring NumPy to support BF16 directly.
- `scripts/align_flashnext_desk.py`: static argv generation; later authenticated
  conversion; load, NLL, effort ladder rate/coherence, generated XML function
  roundtrip/history rewrite and chunked full-cap memory screening.
- `tests/align/test_flashnext_engine.py` and
  `tests/fixtures/align_flashnext_config.json`: portable CPU-only sizing,
  identity-drift, no-unapproved-import and preservation checks, independent of
  the ignored staging directory.
- This run report.

No production endpoint, existing kit, lockfile, decision log or scientific
registration was changed. No changes to `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json`, or `tests/test_gen_state.py`; no task
registration. The user's explicit lane instructions supersede the normal
coordination close-out writes.

## Verification

Final focused verification (modules run separately):

- `python3.13 -B -m unittest tests.align.test_flashnext_engine`: 11 passed.
- `python3.13 -B -m unittest tests.align.test_apple_endpoint`: 9 passed,
  30.478 seconds; existing synthetic endpoint regressions.
- `python3.13 -B -m unittest tests.align.test_pilot3_cache`: 12 passed,
  1.568 seconds; existing synthetic causal-cache regressions.
- `python3.13 -B -m compileall -q joulewise tests scripts/align_flashnext_common.py scripts/align_flashnext_memory.py scripts/align_flashnext_exactness.py scripts/align_flashnext_desk.py`: passed; only our repository code/tests/scripts compiled.
- `python3.13 -B -m scripts.align_flashnext_memory`: passed; config-only output
  checked against the report and independently asserted by focused tests.
- `git diff --check` / staged diff check: passed.

An initial endpoint invocation used too short a tool yield and its session ID
was not retained in the visible orchestration output. Its completion is not
claimed; the explicitly tracked rerun above supplies the test evidence. This
added an unnecessary invocation. An earlier 10-test tooling run passed before
the additional installed-source identity test was added. Total test work was
well below the user's ~20-minute limit. The full suite was deliberately not run.
Python 3.11 was not exercised locally.

No `.engine/mlx-lm-pr1788` module was installed, imported or executed. Tests
import the new scripts as stdlib modules; their third-party imports are inside
functions reached only after the desk gate. The approved-runtime gate itself
is tested with inert files and mocked platform/package discovery. No network,
Block-5 pipeline, real measurement-root read, quiet-machine measurement,
hardware validation or external integration was performed. Existing in-repo
council/pilot prose was used as historical evidence, not newly validated data.

## Outstanding evidence and next exact step

Unresolved: full PR commit authentication, installed wheel/native package pins,
an immutable original-512-expert mixed artifact and publisher manifest, a
frozen public SHADE NLL corpus and trusted reference outputs, 3-bit expert
quality, actual cap/checkpoint peaks, cold-load/page-fault/throughput behavior,
the disputed numerical difference, and production parser/history/phase-provenance
integration. MTP's exact independent tensor census is not specified by the
staged config. No CPU-only or mmap-only PLE residency policy is implemented.

The next lead-controlled step is to seal the second venv's reviewed source and
wheel receipts, then run the tiny exactness script at an approved daytime Mac
desk after the ongoing analysis job finishes. Adjudicate its supported paths
before loading one authenticated E3/PLE4/other8 artifact. Keep all unsupported
path failures, use the documented fallback/decision rule, and leave W1's
existing roster unchanged until its prospective gates close.

The local commit containing this report is the handoff commit; use
`git log -1 --oneline lane/2026-11-05-align-flashnext-engine` for its identity.
No push, merge, deployment or external publication is authorized or performed.
