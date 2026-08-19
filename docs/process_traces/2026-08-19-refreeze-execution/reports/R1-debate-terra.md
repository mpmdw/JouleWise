```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"Concede the helper-root and strict-v3 fail-open; retain no-identity controller fallback and amend vocabulary/census clauses.",
  "workspace":{"base_requested":"9f7f0917751cd7cdbdd61351c98d2fac6132b9e4","base_mode":"exact","head_start":"9f7f0917751cd7cdbdd61351c98d2fac6132b9e4","head_end":"9f7f0917751cd7cdbdd61351c98d2fac6132b9e4","upstream_end":null,"branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[
    {"id":"F5","severity":"blocker","title":"p2-038.3 would bypass strict rich-telemetry replay","detail":"Fix cli.py:1575 in the flip commit."},
    {"id":"F1","severity":"should_fix","title":"Reuse the established claim-barrier reason","detail":"Use clock_anchor_unresolved; document supersession in policy prose."},
    {"id":"F2","severity":"should_fix","title":"Repair the v2-minting shared calibration helper first","detail":"The focused red is caused by fixture candidates, not the unflipped adapter."},
    {"id":"F3","severity":"should_fix","title":"Do not stamp a capture era when no primary evidence exists","detail":"Retain idle data only as explicitly incomplete evidence."},
    {"id":"F4","severity":"should_fix","title":"Complete the site/identity census","detail":"Adopt the added sites and pair-consistency check; do not ratify an unverified bundle count."}
  ]},
  "verification":[
    {"id":"V1","kind":"inspection","cmd":"git status --short --branch && git rev-parse HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","9f7f0917751cd7cdbdd61351c98d2fac6132b9e4"]},"expected":{"exit_code":0,"tail_regex":"9f7f0917751cd7cdbdd61351c98d2fac6132b9e4"}},
    {"id":"V2","kind":"test","cmd":"TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_whole_window_selection.WholeWindowSelectionTests.test_d079_real_selector_to_real_reducer_embeds_allowance_once","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FileNotFoundError: [Errno 2] No usable temporary directory found"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V3","kind":"inspection","cmd":"rg -l -g metadata.json '\"schema_version\"[[:space:]]*:[[:space:]]*\"p2-038\\.2\"' /Users/edr/code/JouleWise/runs_window_* 2>/dev/null | wc -l","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["745"]},"expected":{"exit_code":0,"tail_regex":"[1-9][0-9]+"}}
  ]},
  "flags":[{"id":"F6","kind":"environment","level":"nonblocking","text":"The read-only sandbox rejects tempfile creation even with TMPDIR=/tmp, so V2 could not independently replay Opus's in-process experiment.","needs":"Replay V2 in the writable re-freeze checkout."}]
}
```

## Findings

### F5 — 5. STRICT-VERIFY FAIL-OPEN — CONCEDE

Confirmed. `cli.py:1573-77` returns `[]` unless the schema is `.2`; therefore a `.3` bundle skips rich-telemetry replay entirely. This is release-blocking for the flip and belongs in its commit. A corrupted v3 `rich_telemetry.jsonl` must produce a strict problem (A4).

### F1 — 1. REFUSAL VOCABULARY — AMEND

Reuse `clock_anchor_unresolved`; withdraw `capture_pipeline_superseded`.

The semantic-falseness charge does not hold against the landed code: `analysis_engine/inputs.py:3694-3700` already emits `clock_anchor_unresolved` for a non-claim-bearing anchor-envelope method, explicitly as a version/method eligibility refusal rather than a malformed or absent calculation.

Amended clause: “A stored anchor-v2 bundle presented to claim-bearing analysis is refused with `clock_anchor_unresolved` by `CLAIM_BEARING_ANCHOR_METHODS`. The policy text states that the bounded v2 result is replay-valid but superseded and non-claim-bearing.” This avoids a new reason’s registry fan-out.

### F2 — 2. FAILING-TEST ROOT — CONCEDE

Opus’s executed comparator reversion is decisive. Static inspection corroborates it: `_write_real_v3_candidate` calls `self_consistent_calibration`, which derives v2 at `tests/test_reduce.py:194` and declares the v2 binding at `:233-35`; `calibration_bracketing.py:1039-40` then rejects it against active v3.

Amended clause: “Step 1 precedes the flip: parameterize `self_consistent_calibration` by anchor method, derive and declare both fields from that one method, defaulting to active v3. Preserve explicit v2 fixtures as refusal cases.” A post-barrier positive whole-window test must also use genuine v3 measured evidence; a v2 measurement remains a negative case.

### F3 — 3. CONTROLLER SEED ENVELOPE — MAINTAIN

Do not stamp active-era identity. `controller.py:1603-14` sets primary uncertainty evidence only from the bounded adapter result; the `:1355-59` fallback has neither a clock anchor nor sample phase. `cli.py:1244-47` already makes such evidence strict-invalid. Labeling it `.3` adds a false capture identity without making it valid.

In-tree search finds the `.1` literal only in this fallback, the independent frozen D-078 fixture, and stale documentation—not a stored controller-fallback dependency.

Amended clause: “When primary uncertainty evidence is absent, retain idle-sentinel data as explicitly incomplete evidence without `schema_version` or `clock_anchor.method`; strict verification reports missing primary powermetrics evidence. Existing stored `.1` artifacts remain unchanged.”

### F4 — 4. SITE CENSUS COMPLETENESS — AMEND

Concur on all four additions:

- `environment_admission.py:307,351` hardcodes v2 and must reconstruct from stored method.
- `powermetrics_fiducial.py:1467` must fail closed rather than default missing method to v2.
- `inputs.py:188` checks `unresolved`, while both anchor producers emit `unknown`; it is dead for producer output.
- Schema/method pair consistency is required: method-keyed reconstruction plus `SCHEMA_FOR_ANCHOR_METHOD` equality; mismatch refuses as `clock_anchor_era_inconsistent`.

Amended census clause: “Do not ratify 54 or 771. My exact current-root probe finds 745 `.2` metadata files under the primary `runs_window_*` roots; retain all eras and record the implementation-time enumerated manifest/count.” The count discrepancy does not change the retention decision.

## Residual risk

V2 could not run because this read-only sandbox has no writable temporary directory, even with `TMPDIR=/tmp`; replay it in the writable transaction checkout.