# ALIGN v4 integration adversarial review (Sol cloud)

**Reviewed range:** `83e2dac59..c8ef6b2f` on the supplied integration branch.
**Verdict:** **BLOCKED**. One conflict resolution can convert a native endpoint fault into a non-failing thermal result, and the diagnostics layer repeats the same precedence inversion. The integration must not drive measured windows until that is fixed and regression-tested.

## Review method

I inspected the integration diff and the combined (`git show --cc`) resolution of every merge touching `endpoint.py`, `workload.py`, `campaign.py`, or `diagnostics.py`, comparing the merge result with both parents. I also inspected the unreviewed PR #666 rebuild sequence `5e257e63e..989f649de`, including its thermal session, hold, sidecar, event-splitting, and workload wiring. I traced `add_generation_prompt` through the legacy JSON, explicit `reasoning_content`, XML, and hybrid-checkpoint closed-history renders, and compared current `EpisodeSpec` construction/serialization with the checked-in pilot-v3 stage bytes.

## Findings

### BLOCKER — thermal precedence masks endpoint/runner faults and lets the runtime return success

**Locations:** `joulewise/align/apple/workload.py:594-646, 727-737`; `joulewise/align/apple/diagnostics.py:72-86`.

**Evidence:** The workload first selects `episode_error`/`endpoint_error` at lines 639-642, then unconditionally overwrites either with `thermal.incomplete` whenever a thermal timeout is also present (lines 645-646). The failure boundary at lines 727-737 raises only for `endpoint_error`, `episode_error`, or `episode.deadman`; therefore the overwrite turns a real native exception into a returned `RuntimeResult`. The diagnostics merge resolution independently orders `thermal.gate_timeout`, `thermal.hold_timeout`, and `thermal.incomplete` before `runner.error`, so even salvaged or externally summarized evidence reports the thermal condition instead of the fault. This is exactly the simultaneous-condition case that the two parents did not individually exercise: PR #660 put runner faults ahead of decode-budget stops, while PR #666 inserted thermal stops before that fault check.

A thermal stop is a measured environmental/censoring condition; it must not outrank a software/runtime fault. Otherwise a broken generation stream can be retained as though it were merely thermally incomplete, corrupting both success status and exclusion attribution.

**Concrete fix:** Define one shared stop-precedence function and use it in both workload finalization and diagnostics. Preserve deadman as the highest-priority governed abort if that is the contract, then rank `runner.error`/`episode_error`/`endpoint_error` ahead of all thermal timeout/incomplete and decode-budget outcomes. Keep every concurrent cause in flags, but never overwrite a fault-valued primary stop. Make `AdapterFailure` depend on the presence of fault flags (or the shared classified fault category), not on a mutable display string. Add regressions for endpoint-error + gate-timeout, episode-error + hold-timeout, and runner.error + a non-released thermal interval, asserting failed execution and `runner.error` primary classification.

### HIGH — the new dataclass default changes regenerated v3 anchor spec/config bytes

**Locations:** `joulewise/align/apple/workload.py:71-101`; `scripts/align_pilot_kit.py:102-117`.

**Evidence:** `hybrid_checkpoint_limit` defaults to `0`, and `to_text()` omits it only when it is `None`. All existing pilot-kit constructors omit this argument, so regenerating them now emits `"hybrid_checkpoint_limit":0`. The checked-in v3 stage specs have no such key, and `from_text()` deliberately maps the omitted legacy key to `None`. The compatibility test avoids the new default by explicitly replacing it with `None`; that proves parsing old bytes but does not prove that the unchanged generator reproduces them. The existing generator oracle confirms the defect: `python -m unittest tests.test_align_pilot_session` fails `test_committed_kit_matches_generator_and_runs_only_align_members` because generated v3 episode JSON contains `\"hybrid_checkpoint_limit\":0` while the committed anchor does not. Thus the checked-in files remain byte-identical only because they were not regenerated; running the nominal pilot-10 generator silently changes the spec SHA, config bytes, and governed runtime identity of every anchor.

**Concrete fix:** Make the `EpisodeSpec` default `None` so unchanged constructors preserve legacy bytes. Require v4/hybrid pack builders to pass an explicit `0` or positive limit, and retain explicit `0` in serialization/identity for those new packs. Add a regeneration test that runs the pilot-10 builder with no compatibility override and compares every produced v0-v3 stage byte (not merely the already checked-in files) with the frozen `83e2dac59` oracle.

### HIGH — counterbalancing can pair different hybrid execution policies

**Location:** `joulewise/align/apple/campaign.py:23-47`.

**Evidence:** The merge resolution incorporated token budget, deadman, thermal, assistant-history, and template controls into the counterbalance cell key, but omitted `hybrid_checkpoint_limit`. Consequently a benign spec using rebuild-only execution and a sabotage spec using checkpointed recurrent-state restoration share a cell and are emitted as a matched condition pair. Hybrid checkpointing changes the prefill schedule and potentially the token trajectory; treating those policies as the same cell invalidates paired energy attribution without producing the existing `unmatched_condition_cells_retained` warning.

**Concrete fix:** Include `hybrid_checkpoint_limit` in the cell key with omission semantics matching `EpisodeSpec.to_text()` (legacy `None` distinct from explicit `0`). Prefer deriving the key from a centralized execution-policy projection so future measured controls cannot be omitted in one of several hand-maintained lists. Add a discriminating test analogous to the cache-policy test, asserting that `None`, `0`, and a positive checkpoint limit never counterbalance across conditions.

### HIGH — an unobserved G1/H interval has contradictory primary outcomes across artifacts

**Locations:** `joulewise/align/apple/thermal_gates.py:254-258, 331-359`; `joulewise/align/apple/workload.py:480-483, 594-596, 645-648`; `joulewise/align/apple/diagnostics.py:75-83`.

**Evidence:** `ThermalSession.wait()` documents and implements unobserved G1/H as proceed-with-X4: it returns `outcome='unobserved'` without a timeout flag. The workload accepts `unobserved` at G1, defines `incomplete` only for timeout/deadman, and therefore records an ordinary `episode_returned` (or another nonthermal stop). Diagnostics later classifies *every* non-G0 interval whose outcome is not `released` as `thermal.incomplete`, including `unobserved`. The same episode therefore has one primary stop in runtime provenance and another in `summary_metrics`, silently changing inclusion/attribution depending on which artifact a consumer reads.

**Concrete fix:** Settle the contract explicitly. If X4/unobserved is an incomplete thermal episode, compute that once in the workload, record `thermal.incomplete`, and make downstream diagnostics consume the recorded classification. If it is allowed to proceed as a valid but flagged episode, diagnostics must not convert it to incomplete. In either case, add an end-to-end regression for unobserved G1 and unobserved H that asserts identical stop classification in `episode_outcome`, `align_episode.json`, and diagnostics.

## Traced areas with no additional finding

* `add_generation_prompt` is now threaded through all three template-rendering paths: legacy JSON, explicit `reasoning_content`, and XML. The hybrid checkpoint requests `False` only for the closed-history boundary and normal generation/context checks retain `True`; I found no merge-resolution drop on these paths.
* The XML assistant-history path keeps reasoning separate, removes a structured tool call from visible content before re-rendering, and passes the same template kwargs to open and closed renders. The JSON legacy path still stores the raw completion by default, preserving its established history behavior.
* The frozen stage files themselves are unchanged in `83e2dac59..HEAD`; the anchor risk above is reproducibility on regeneration, not an already-modified checked-in stage file.

## Required disposition

Do not run v4 measurement episodes from this head. Fix the BLOCKER and the three HIGH findings, add simultaneous-cause and regeneration/counterbalance regressions, then rerun the ALIGN suites plus the frozen-stage-byte oracle. MLX/Metal-native checks may remain skipped on non-Apple CI, but the conflict-precedence and serialization tests are platform-independent and must pass there.

## Verification executed

* `python -m unittest tests.test_align_pilot_session` — **FAIL**: 15 tests ran; the sole failure is the v3 generator/committed-kit byte mismatch described above.
* `python -m unittest discover -s tests/align` — **INCOMPLETE/FAILING**: the broad suite was allowed to run for approximately 47 minutes and reached its long Monte Carlo review modules, with MLX/Metal cases skipped as expected. Before manual termination it had already printed three errors and multiple failures (`EEE`, then `F.F`, then a later `F`), so this head does not have a green ALIGN suite. Because `unittest` prints tracebacks only at process completion, the interrupted run did not identify those cases; rerun the focused modules or the full suite to completion during remediation.
* `git diff --check` — **PASS**.
