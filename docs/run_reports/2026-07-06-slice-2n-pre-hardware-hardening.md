# Run Report: Slice 2N Pre-Hardware Hardening (2026-07-06)

Queue item P2-007 — the top-ranked ungated implementation work. Executed
via playbook Mission M1 in a single session, landed as the three planned
commit groups.

## Planning Reflection (start of run)

1. **Goal:** land all nine Slice 2N work items so real (MLX/powermetrics)
   adapters can be written against the post-2N seams without touching
   controller/bundle internals.
2. **Prior state inspected:** `RUN_STATE.md`, `TASK_QUEUE.md`,
   `AGENT_PLAN.md`, playbook M0+M1, `phase_2_plan.md` Slice 2N,
   D-024/D-025 (pre-decided), D-008 (for 2N.9), the whole `joulewise/`
   package and its test suite. Preflight: git clean and synced with
   `origin/main`; suite green (`Ran 169 tests, OK (skipped=8)`).
3. **Workspace health (user-requested, pre-mission):** repo verified at
   the canonical non-iCloud path; `~/jw_pending_edits/` already gone; the
   stale `~/Desktop/CapstoneRivoire` remnant held only the
   harness-recreated `.claude/settings.local.json` (verified before
   deletion) and was deleted per the 2026-07-06 run report's note.
4. **Assumptions inherited:** D-024/D-025 are settled (implement, don't
   re-decide); the playbook's line numbers may drift (re-located by
   symbol); R-015 additive-only schema policy; D-009 bare-Python CI.
5. **Items moved toward done:** exit-checklist 2N row (closed);
   Do-Not-Do-Yet 2G/2H blocker (satisfied).
6. **Evidence:** tests per work item, suite green, decision-log entries,
   this report.
7. **Failure tolerance:** any single 2N item could stall without blocking
   the others (three independent commit groups were the containment).
   None stalled.
8. **Not to be changed:** schema v0.1 shape (R-015; 2N.5 changed only the
   exported schema's nullability declarations, not serialization — see
   D-029), the D-013 quiescent-window discipline, config hashes (now
   pinned by test).

## What Changed

Three commits, per the playbook's grouping:

**Commit A — the adapter seam (`dcfa474`), items 2N.1 + 2N.2**

- `RunContext` frozen dataclass in `interfaces.py` (D-024): config,
  clock, run_id, bundle/raw/logs/outputs paths, optional `node_role`.
  Placement pinned as a trailing optional per-method parameter on all
  adapter lifecycle methods (D-024 amendment records why: the cooldown
  gate calls `measure_idle` outside any bundle).
- `RunBundleWriter.raw_path`/`write_raw`: validated plain-name,
  collision-checked, refused after `finalize()`.
- Mock telemetry now writes its native sampler output verbatim to
  `raw/mock_samples.json` via the context — the D-002 raw-evidence path
  runs on every mock run.
- **D-026 (new):** `sampling_started`/`sampling_stopped` marker events
  bound the measured window; the reducer integrates between markers
  (stage boundaries remain the fallback for pre-2N bundles), so sampler
  spawn latency and wind-down cost stay out of gross energy, idle
  subtraction, and TTFT. A latency-simulating fake telemetry adapter
  proves metrics are latency-invariant (the stage span demonstrably
  still contains the latency; the markers exclude it).
- `adapter_contracts.md`: RunContext + measured-window-marker contracts.

**Commit B — the read layer (`7357c83`), items 2N.8 + 2N.4 + 2N.7 + 2N.6**

- **D-025 implemented:** new `joulewise/bundle_read.py` `BundleReader`
  owns all bundle parsing and interpretation policy — strict accessors
  (structured `BundleReadError`s) for the reducer, tolerant accessors
  for the report, D-018 rail summation, D-026 windows, D-011 completion
  state, and the full `validate-bundle` structural checks
  (`BundleReader.problems`). `reduce.py` keeps only metrics math;
  `report.py` and `cli.py` consume the reader. The port is
  behavior-preserving (pre-existing suites passed unchanged before the
  new policy tests were added).
- **D-027 (new, 2N.4):** detect-and-fail rail alignment. With a
  multi-rail manifest, per-rail rows must share one timestamp per sample
  instant; a subset at any timestamp is a structured failure naming the
  timestamp and missing rail(s). Chosen over tolerance-bucketing because
  silently rewriting measurement data is the failure mode this project
  exists to avoid. Contract recorded in `adapter_contracts.md`.
- **2N.7:** the report chart draws exactly the reader's summed curve (no
  more all-rails fallback) and shades the D-026 window; unreadable
  curves get a note. A chart can no longer show energy the summary
  excluded.
- **2N.6 + D-028 (new):** `python3 -m joulewise reduce <bundle-dir>`
  re-derives and rewrites `summary_metrics.json` in place — recorded as
  the ONE sanctioned post-finalize mutation (noted in
  `run_bundle_layout.md`). `reduce_bundle` now returns structured FAILED
  summaries for missing/corrupt `config.json`/`metadata.json`/event
  lines instead of raising. Exit scheme matches `run` (0/2/3);
  non-bundle directories are refused with no write.

**Commit C — schema + metrics (this commit), items 2N.5 + 2N.3 + 2N.9**

- **2N.5 + D-029 (new):** the exported config JSON Schema declares every
  emittable-as-null optional as nullable (the plan's pinned choice);
  serialization and therefore config hashes are untouched. Tests:
  bare-Python nullability + known-keys checks over every example
  config's `to_dict()`, full `jsonschema` validation where that package
  exists (`skipUnless`, D-009), and pinned SHA-256 per example config so
  any future serialization change fails loudly.
- **2N.3:** `energy_token_j` falls back to the runtime's observed
  `workload_observed.token_count` from `metadata.json` when the config
  supplies no `prompt_tokens`; new additive `MeasurementQuality.
  token_count_source` (`"config"` | `"runtime_observed"` | null) records
  which source was used. Config-supplied counts still win; neither
  present still yields None.
- **2N.9:** design-only compatibility check (findings below) plus a
  synthetic `node_role="prefill"` context test proving nothing chokes.

## 2N.9 Findings: v0.2 / Composite-Bundle Compatibility

Checked D-024's `RunContext` and D-025's `BundleReader` against D-008
(`run_kind`/`split_plan`) and the composite-bundle preview in
`run_bundle_layout.md`:

- **RunContext survives v0.2 unchanged.** A split run gives each node a
  standard sub-bundle (`nodes/prefill/`, `nodes/decode/`); the Phase 3
  orchestrator constructs one immutable context per node with
  `bundle_path` pointing at the node sub-bundle and `node_role` set. No
  new fields, no mutability pressure. The synthetic test constructs a
  `node_role="prefill"` context and drives the mock telemetry lifecycle
  through it, including raw evidence, with zero adapter changes.
- **BundleReader survives for node sub-bundles as-is** — they are
  standard bundles, so per-node reduction reuses everything. Composite
  top-level reading (merged events, per-stage summary) is new v0.2 work
  that D-025 already assigns to the reader (its revisit trigger).
- **One flag for Stage 3.1:** the layout preview says the composite
  `events.jsonl` carries "merged node events, node field". A sixth
  top-level event key would break the five-key event contract that
  `validate-bundle` pins (and R-015's additive-only rule as applied to
  event records). Recommendation recorded here for Stage 3.1: carry the
  node tag inside the existing `metadata` object of each event record
  (no key-set change), or explicitly version the event contract in the
  v0.2 design. No change made now (R-015; implementation waits for
  Stage 3.1). No D-008/D-024/D-025 amendments required.

## Commands Run / Verification

```bash
python3 -m unittest discover -s tests   # 169 -> 179 -> 208 -> 216 tests, OK at every step
python3 -m joulewise run configs/examples/mock_local.json --runs-dir <tmp>   # succeeded
python3 -m joulewise validate-bundle <tmp>/example-mock-local                # valid
python3 -m joulewise reduce <tmp>/example-mock-local                         # identical summary, exit 0
ls <tmp>/example-mock-local/raw/                                             # mock_samples.json present
```

Final suite: `Ran 216 tests, OK (skipped=10)` — 8 `[analysis]` chart
skips, 1 new report-alignment test (also matplotlib-gated), 1 optional
full-jsonschema round-trip (CI stays bare-Python, D-009).

## Decision Log

- D-024: status → implemented; amendment records the pinned per-method
  optional-parameter placement.
- D-025: status → implemented.
- New: D-026 (window markers), D-027 (rail alignment detect-and-fail),
  D-028 (reduce-verb in-place rewrite), D-029 (nullable-optionals
  schema; hashes pinned).

## Risk Register

No status changes. R-015 respected throughout (every new
config/summary/event element is additive; serialization untouched).

## Workspace State

- Working tree clean after the three commits; pushed same-session at
  the user's request. CI run #11 on `5cb1dfc`: completed, success (the
  suite-count expectation in playbook M0 was updated to 216).
- Old Desktop remnant `~/Desktop/CapstoneRivoire` deleted (verified to
  contain only the harness-recreated settings file first).
- Smoke bundles were written to the session scratchpad, not the repo.

## Plan Accuracy / Planning Gaps

The playbook M1 spec was accurate at the symbol level; two things it
did not anticipate, both resolved in-session and worth knowing:

1. The measured-window inflation was two-sided — the stage-completed
   boundary also included post-window artifact writes, not just the
   startup latency the review flagged. The marker design (D-026) fixes
   both ends; a reorder-only fix would not have.
2. The stop marker's buffer position matters under the stable
   flush-sort (equal FakeClock timestamps): it must be appended after
   the runtime events to keep bracketing them. Recorded in the D-026
   considerations.

## Next Best Task

Per `TASK_QUEUE.md`: **P0-002** (corpus backup protocol, playbook M2)
still outranks everything but needs the user to name a backup
destination — ask for it at the next opportunity. The top implementable
task without user input is now **P3-001** (related-work draft, playbook
M3, ungated desk work). All Phase 2 implementation is hardware/decision
gated (D-016 ← P1-001; 2H ← P1-002 auth session; 2K/2L ← P1-006).
