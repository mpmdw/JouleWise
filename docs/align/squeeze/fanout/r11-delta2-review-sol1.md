# ALIGN v4 R11 delta2 review — Sol1

Candidate: `f993b784f`; range: `git diff 353446ad6..HEAD` at that
candidate (33 paths). Seat: `align/2026-11-08-v4-r11-delta2-sol1`.
Brief/report date: 2026-11-08. This reviews the Sonnet repairs and their
necessary execution dependencies, not the historical main-to-v4 stack.

**Verdict: HOLD.** The old count, packet and named-script witnesses pass,
but exact-candidate admission still has a concrete coverage/tier defect.
The new battery evidence also has an operability gap under the documented
back-to-back procedure and accepts a transition across an intervening fault.
These affect registration fidelity, evidence or a real arm; they are not
requests to reopen settled science or to guard against fabricated lead approvals.

## F01 — HIGH: the executed receipt is still incomplete, and two live W1 scripts are amendable

Two parts of the same admission boundary need repair:

1. `configs/campaigns/align_v4/registration/inputs.json:106` supplies
   `WP15.runtime_entrypoint = ["scripts/align_r1_runtime.py", "--config",
   "configs/align/v4/r1_runtime.json"]`. The R1 wrapper takes this route;
   `scripts/align_r1_rehearsal.py:1965` constructs the interpreter argv.
   **Neither the runtime script nor its config is in ARTIFACTS.** A clean
   later commit changing either still validates the old receipt, without
   any amendment. The config is also a current W1 input:
   `scripts/align_v4_kit.py:460` reads its G0 timeout for `w1_g0_cap`.
   Recording a runtime-config hash in a later R1 result does not bind that
   source to the old candidate gates. This is a current configured execution
   edge, not speculation about arbitrary computed paths.
2. The current W1 `plan_tree.json` launches bracket reservation and pre/post
   calibration captures. `joulewise/b5/chain.py:140` resolves these to
   `scripts/reserve_calibration_window_bracket.py` and
   `scripts/validate_powermetrics_fiducial.py`. Both are bound, but
   `v4_registration.STRICT_SCRIPTS` at line 316 omits them. Consequently an
   ordinary signed amendment **admits changed fiducial-capture code** in
   place of strict re-registration. The protocol's strict-script rule at
   `pilot_protocol_v4.md:747` explicitly covers the W1/D/R1 launch spine.
   These capture/reservation programs are on that spine, rather than an
   unrelated maintenance branch of the closure.

Witnesses in `tests/align/test_r11_delta2_sol1.py`:

- `test_configured_r1_runtime_script_drift_requires_review` constructs the
  actual configured argv without launching it, then demonstrates admitted
  clean-commit drift in a synthetic Git repository.
- `test_r1_runtime_config_drift_requires_review` demonstrates the config case.
- `test_current_w1_stage_launch_tools_are_strict` derives the tool set from
  the current W1 graph; it fails for the two programs above.
- `test_signed_amendment_cannot_waive_current_w1_fiducial_script_review`
  demonstrates actual admission, not just an inventory mismatch.

The row validator itself is sound for paths already classified strict:
the new control exercises **all 96 currently strict artifacts** and every
amendment row refuses. There is no demonstrated alias/path trick that
amends an actually strict path. The defect is the boundary's omissions.
Amendment chains, wrong hashes, unsigned rows and later unamended edits
also refuse in the existing tier tests.

**Repair:** bind the configured R1 entrypoint and source config strictly;
derive/check the strict script set against the actual W1 stage tool table
and configured R1 launch. Regenerate the template. Keep the amendment tier
for the agreed infrastructure superset; wholesale strict binding of B5/B6
is not requested. Repeat the drift and tier witnesses after integration.

## F02 — MED: the documented top-up collection procedure can strand back-to-back arms

The protocol at `pilot_protocol_v4.md:614` and sampler docstring prescribe
sampling **between windows**. `v4_topup.derive` requires a charging-to-float
transition (lines 78–81) and an uninterrupted <=300 s chain from that charge
through arm (lines 85–92), for both evidence branches.

After an approximately eleven-hour window with the battery still full,
resuming the documented sampler cannot pass: retaining the old charge gives
an eleven-hour gap, while starting a fresh log gives no charge event. Any
amount of additional floating at 99–100% fails to cure either condition.
This recreates Opus MED-3's need to discharge/recharge a full battery,
unless some other continuous source has been collected during the window.
No such integration is supplied by the new sampler; it appends one sample
per invocation and the documented instructions restrict it to turnaround.

`Controls.test_documented_between_window_sampling_strands_an_already_floating_battery`
passes as a characterization: old completed charge + a measurement gap +
30 minutes of fresh float refuses, and the fresh float log alone refuses.
This is an operational contradiction, not a request that code silently
waive its declared 300 s rule. Dense float evidence at exactly 99% and
300 s spacing does admit; >300 s freshness refuses.

**Lead choice before W1:** install/qualify a continuous logged source,
including initial charge acquisition and the whole measured window, or
prospectively define an admissible already-floating/startup evidence path.
Document and witness the actual back-to-back path. Retain the 1800 s bound
and OBC attestation; a typed timestamp is not a remedy. I did not run a
hardware sampler or propose an unreviewed measurement-load change.

## F03 — MED: filtering observations can manufacture a completed-charge transition

`v4_topup.py:70` filters out off-AC/error observations before finding
charging-to-float events. Line 85 checks rejected observations only *after*
the selected float timestamp. Thus this ordinary log is admitted:

```text
arm-2000 s: charging, 97%, AC
arm-1900 s: not charging, 100%, off AC
arm-1700 s: floating, 100%, AC (reconnection)
then float every 100 s through arm
```

The intervening observation disappears. The return is `admissible=True`,
`basis=completed_charge`, completion at arm-1700 s. Yet the battery was
already full/not charging at arm-1900 s, outside the 1800 s completion
window. Reconnection has moved the alleged completion forward. The second
witness uses a probe error between charging and float and likewise obtains
admission across the missing transition. No edited timestamps or fabricated
source signature are necessary.

Both `TopupWitnesses` fail on this behavior. Repair by deriving completion
from an admissible consecutive transition in the original record stream,
without filtering a discontinuity out of that transition. Retain the raw
observation order and then validate the following float run. A later real
valid charge can establish a new event; a permanent poison from an old
error is not requested.

## Assessment of the prior findings and requested focus areas

| Prior item | Delta2 assessment |
|---|---|
| Both Sol script-coverage HOLDs | The specific `run_campaign`, `bytes_h_session`, hazard, meter and launch-window omissions are repaired. F01 identifies remaining current dependencies and tier errors. |
| Both Sol impossible-count findings | Fixed: eligible spam+bank cannot exceed captured; captures are bounded by 22; totals are cross-checked. |
| Sol1 unfinished zero-capture window | Fixed: provisional zero-capture remains pending; final zero-capture refusal stays exempt. |
| Both Sol contradictory W1 flags | Fixed for the reported contradiction: canonical previous-window id is cross-checked, and bound-artifact digest derives code/config change. |
| Sol1 packet retention; Opus L2 | Fixed: packet, canonical digest, file digest when read from a file, derived calibration summary and rulings are retained. |
| Opus HIGH-1, WP22 | Minimal default dry run reaches the desk; the contrast is rederived after WP18 and the synthetic X-G count follows it. Full window: 20 tests, OK with the one accepted collector-death expected failure (165.459 s). |
| Opus MED-1, two-tier receipt | Valid mechanism; incomplete boundary, F01. |
| Opus MED-2a, zero-capture deadlock | Fixed: a signed, digest-bearing lead-ruling row resets escalation after its named window, without deleting history. |
| Opus MED-2b, meter deadlock | Fixed: previous coverage/gaps are recorded and non-gating; current reader-live evidence gates. A previous dropout does not veto a new arm. |
| Opus MED-3, top-up evidence | Typed time removed and file hashed, but F02/F03 remain. |
| Opus MED-4, DC sealing | Fixed on the reviewed v4 desk path: all non-benign and unknown-condition member DC rows become hash/status/flags only before printing or report retention. Numeric integrals, residuals, scores and turn rows disappear. The DC fit trains on unique benign trajectories only. |
| Opus L1, R1 export | Source-derived exporter and lane-shaped plain/compressed discovery tests pass; source/result hashes retained, aggregate mismatches refuse, explicit backfills do not overwrite. No live bundle was inspected. |
| Opus L3, previous record commit | Existence of a full commit is now checked. It does not authenticate that the named commit contains the claimed previous-window record; that semantic link remains a producer/lead assertion. Do not describe existence as a complete custody binding. |
| Opus L4 | CR0/z uncertainty remains disclosed, unchanged and non-gating. No new SE convention is installed by this review. |
| Opus L5/L7/L8/L9 | State window id, fail-closed packet template, evidence-only pmset and bool/string score refusal are implemented. |

The predicate now implements the **fixed eight** from `origin/main:RUN_STATE.md`
item 217. Updating the old witnesses from six/count-stop to eight is legitimate
under that explicit ruling. The >=39/pair requirement, zero-capture exemption
and no-ninth-counted-window rule remain. This review does not qualify live
exchangeability, fit/calibration/test allocation or the final-roster U6 OC.

**Closure completeness and brittleness.** ARTIFACTS has 292 paths;
EXECUTED_CLOSURE has 258, with named inputs filling the remainder. The walker
now covers first-party imports and exact script strings/shell tokens, and
the new original-script witnesses pass. It is a useful drift guard, not a
complete execution inventory: configured argv such as WP15 is missed, as
are other computed paths/dynamic loads. The stated exclusions do not
excuse omitting a concrete current entrypoint. Most closure overbreadth is
now amendable (196 paths), which addresses the previous operational cost.
The classification test that simply asserts each STRICT_SCRIPTS member is
strict cannot detect omissions; the new W1 graph-derived witness does.

**WP22 test changes.** U3=inconclusive is correct: no U3 constant is installed,
the diagnostics keep running, and `require_registration` still refuses an arm.
This does not close U3. The new stage column matches the registered R06 fit:
intercept + template + arm + start time + stage, df=3. The legacy independent
oracle still omits stage and uses df=4, so its coefficient is not the same
target. A separate clean synthetic W1 audit reproduces and decomposes the
discrepancy:

| Fit | Arm effect (J) |
|---|---:|
| Legacy oracle, four columns, independent world integrals | 4.162669121218187 |
| Stage-adjusted oracle, five columns, same world integrals | 4.219431311450080 |
| Independent five-column fit to desk-integrated energies | 4.219431311451899 |
| Production desk | 4.219431311451899 |

The stage-model change accounts for **0.056762190231893 J**; integration
accounts for only **1.82e-12 J**. Both use the registered eight contrast rows;
the v4 verdict is T REJECTED, df=3, and its CI matches the independent fit.
Thus the 0.057 J discrepancy is legitimate, not evidence of a masked solver
or energy-integration defect. The loose comparison remains a weak test of
the new model. The new independent
eight-row control compares the stage-adjusted coefficient and CI tightly
(8/6 decimal places) and verifies invariance to an added 70 J stage offset;
it passes. I found no demonstrated regression-solver defect. Updating the
WP22 oracle to the same prospective model, with stage-sensitive cases, is
a nonblocking test improvement; matching this one fixture's verdict alone
would be inadequate evidence of estimator correctness.

The single full-WP22 expected failure is
`InjectedWindowTests.test_collector_death_is_x4_and_episode_continues`:
legacy WP22 expects ordinal 18 to succeed after collector death, whereas
the accepted WP8 F2 behavior fails the member promptly. Existing companion
tests require X4 exclusion, U1 thermal-fault counting and the resulting
failed thermal protocol. This is the documented fail-fast divergence,
not a new hidden numerical failure; acceptable for this delta. A future
cleanup can assert the accepted behavior directly instead of retaining xfail.

## Verification and handoff

All checks use synthetic records or repository code/config objects only.
No full suite, network, weights, native MLX, measurement pipeline, sealed
data, real restricted directory or live-job inspection/control was used.
Absolute data paths in source were treated as text. Host-state writes were
redirected to `/private/tmp/r11-delta2-sol1-host`; arm probes were mocked.
The pre-provisioned review branch was clean and already correctly named.
M0/stop-card/workspace/queue/do-not-do/orchestration and targeted decision
authority were read. No sub-agent/peer consultation was invoked. The
explicit brief supersedes queue selection, full-suite and state-file writes.

Test result table and commit handoff are in the dated run report:
`docs/run_reports/2026-11-08-align-v4-r11-delta2-sol1.md`.
The new module deliberately remains red for the lead's fixes: 11 tests,
5 passing controls and 6 failing methods (7 failure records, because the
W1 graph test has two failing subtests). This is review evidence, not a
passing admission gate. Final run: 4.132 s. The 19 baseline/affected modules
plus the separate full WP22 run are green (404 test instances, 14 default
skips, one accepted full-run xfail). Across all module executions including
both new-witness runs, unittest reports 356.514 s. Compileall and whitespace
checks pass. Product code and coordination state are unchanged.

Next exact step: lead disposition F01–F03 alongside the independent sol2
seat; repair the receipt boundary and qualify a usable battery-evidence
procedure; then run both delta2 witness modules and the touched modules
serially against one integrated candidate. Preserve all separate U3,
final-roster U6, B-window, R13/R14/F-C-T, series-manifest, access-history,
continuous volume-audit and native holds. This review does not authorize W1
registration or any live arm.

Outside this sandbox, on an authorized Metal host with pinned offline
dependencies, the lead must still run the tiny/random native gates:
`tests.align.test_cache_checkpoint_native`,
`JW_ALIGN_MLX_NATIVE_TESTS=1 tests.align.test_thermal_mlx`, and
`tests.align.test_r0_mlx_native`, plus the outstanding native
termination/census and installed-deadline qualification. Hardware gates
belong to a clean lead-controlled session and must not interrupt the
blinded job. No model download is needed.
