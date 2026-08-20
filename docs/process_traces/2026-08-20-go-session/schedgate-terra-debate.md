```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Reconciled scheduler-gate design: adopt an independent scheduler receipt/vocabulary and byte-recomputed fuse; reject capture-span fuse and require a ruled G2 timing state machine.","workspace":{"base_requested":"5bd7acf38fbdd71e77c5da30094e1e6183777697","base_mode":"informational","head_start":"afb7d5705add3475cd016177a8f8fa1dd02a814e","head_end":"afb7d5705add3475cd016177a8f8fa1dd02a814e","upstream_end":null,"branch":"HEAD (detached)"},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"should_fix","title":"G2 needs an explicit pre-capture authorization and post-consumption close-out transition.","evidence":"A receipt written before first capture cannot contain arm→consume; r3 requires observed gaps and a mandatory halt before claims. Define UNMEASURED→SHAKEDOWN_AUTHORIZED, then MEASURED or HALTED after consumption."},{"id":"F2","severity":"should_fix","title":"G1 must not add an operator-declared capture-span term to the governed arm-to-consume budget.","evidence":"validate_r1_temporal_budget checks earliest TIME_BOUND deadline against the budget only; r3 B-5 envelope planning is pre-mint and does not authorize a runtime multi-hour capture-span fuse."},{"id":"F3","severity":"nit","title":"The replay-corruption explanation overstates what unioning scheduler codes does.","evidence":"Unioning a code makes an arm refusal schema-valid, but replay rejects a scheduler-only recorded refusal when it is absent from freshly derived expected_refusals at arm_readiness.py:5342-5348; it is a fail-closed replay mismatch, not silent corruption."}]},"verification":[{"id":"V1","kind":"inspection","cmd":"git show 5bd7acf:joulewise/arm_readiness.py | nl -ba | sed -n '4272,4278p;5253,5264p;5342,5348p;5385,5392p'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["expiry requires non-null now_monotonic_ns","both freeze-replay calls omit now_monotonic_ns","replay compares recorded and freshly derived refusals"]},"expected":{"exit_code":0,"tail_regex":"expiry.*freeze-replay.*refusals"}},{"id":"V2","kind":"inspection","cmd":"git grep -n -E 'window_scheduler_gates|scheduler_gates|evaluate_window.*gates|window_timing_ledger|campaign_boot_pin' 5bd7acf -- joulewise scripts tests || test $? -eq 1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["no scheduler-gate implementation paths at 5bd7acf"]},"expected":{"exit_code":0,"tail_regex":"no scheduler-gate implementation paths.*"}},{"id":"V3","kind":"inspection","cmd":"git grep -n -E 'validate_window_duration_margins_receipt|authenticate_window_duration_margins|window_duration_margins' 5bd7acf -- joulewise scripts | sed -n '1,30p'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["references are the margins module and recording script; no pack-aware consumer exists"]},"expected":{"exit_code":0,"tail_regex":"margins module.*recording script.*"}},{"id":"V4","kind":"inspection","cmd":"sed -n '57,72p' ../custody-staging/MAGISTRATE-RULING-r3.md; sed -n '12,29p;68,75p;170,180p' ../custody-staging/rulings-r5-consolidation.md; git show 5bd7acf:scripts/capture_t0_step.py | nl -ba | sed -n '605,614p'","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["r3 mandates mechanical pre-claim halt","r5 S-1 resolves the C1 reclassification","r5 S-7 requires agent-free capture","r5 V-7 adds the SET probe; capture_t0_step executes it"]},"expected":{"exit_code":0,"tail_regex":"mechanical.*halt.*agent-free.*SET probe.*"}}],"flags":[{"id":"FL1","kind":"baseline_drift","level":"nonblocking","text":"The checkout is an ancestor of requested 5bd7acf; all disputed source claims were inspected directly from the 5bd7acf tree, and the relevant files have no diff to this checkout.","needs":"Apply the ruling at the implementation head."},{"id":"FL2","kind":"lead_ruling","level":"blocking","text":"r3 defines p99 at shakedown but not its estimator or whether later observations enter the statistic.","needs":"Ratify the G2 estimator and state machine."},{"id":"FL3","kind":"lead_ruling","level":"blocking","text":"C3 requires an agent-free evaluator topology and C4's SET probe changes machine state, but their exact sequencing/provenance contract is not yet specified.","needs":"Ratify driver topology and SET→GET receipt ordering."}]}
```

## Findings

F1: adopt G2’s two-phase concept and sticky halt, but make the temporal seam explicit. The pre-capture receipt may authorize a non-claim shakedown; only the post-consumption closure can calculate arm→consume and transition the family to `MEASURED` or `HALTED`.

F2: the B-12 evidence is confirmed. Expiry is checked only when `now_monotonic_ns` is supplied, and both frozen generic-evidence replay calls omit it. G1 must reauthenticate/read the frozen evidence bytes, select all `TIME_BOUND` receipts, and compare their earliest deadline with live monotonic time. It must not treat arm `PASS` as freshness proof. I reject adding `projected_span_ns`: the existing governed predicate is budget-only; B-5’s larger envelope is a pre-mint planning calculation.

F3: separate scheduler vocabulary remains the right contract boundary. The correction is causal: unioning codes does not itself alter existing replay outcomes, but it makes scheduler codes admissible inside arm receipts, where they can later fail the arm’s derivation/replay equality. Avoiding that category error is sufficient reason for an independent receipt validator and `_gate_refusal`.

## Residual risk

No live privilege or quiet-Mac probe was run. In particular, the SET command is state-changing and must not be exercised from this agent session.

Final amended position:

1. CONCEDED — use `joulewise/scheduler_gates.py` with a thin `scripts/evaluate_window_gates.py`. The enforcement link into arm/launch remains necessary; otherwise direct `launch_window.py` use bypasses a merely advisory evaluator.

2. CONCEDED — use `SCHEDULER_GATE_REASON_CODES` and a scheduler-only emitter/receipt; do not union codes into `READINESS_REASON_CODES`. Only an exactly identical arm predicate, such as G4, may be recorded as mirrored arm reasoning, never as a scheduler exception in an arm receipt.

3. CONCEDED — evaluate G5 first. On boot mismatch or unavailable boot identity, G1 and G2 are `NOT_EVALUATED`, never `PASS`; aggregate result is NO-GO.

4. DISPUTED — the evidence-byte recomputation is accepted, but the added capture-span term is rejected. G1 is `earliest TIME_BOUND deadline - now >= governed arm_to_consume budget`; B-5 envelope timing is separate planning work.

5. DISPUTED — accept `UNMEASURED` shakedown admission, claim refusal before measurement, and sticky HALT. The proposed `max until n=100` p99 substitution lacks authority; with the ruled single shakedown, nearest-rank p99 equals the observed value. Any multi-sample policy needs a ruling.

6. CONCEDED — B-22 cure is behavioral: the pack-aware consumer must refuse the SHA-repaired truncated fixture. A version/import check is insufficient. At runtime, claim admission invokes the real pack-aware consumer; the fixture is a mandatory gauntlet proof, not a magic version marker.

7. AGREED — C1 must apply S-1’s reclassification so the shakedown is not deadlocked; a claim requires the resulting custodied shakedown-arm evidence. C3 must self-refuse under agent ancestry and use an agent-free driver. C4 must evidence both GET state and SET capability, with the SET verb confirmed at `capture_t0_step.py:607-614`.

8. CONCEDED — I withdraw `window_scheduler_gates.py` naming, reuse of arm refusal codes for scheduler-exclusive predicates, and the prior underspecified G2 sequencing. I retain the required launch-binding seam and rejection of the capture-span fuse. I refute only the claim that vocabulary union silently corrupts replay, not the conclusion that the vocabularies must remain separate.

Magistrate rulings needed:

- Ratify the independent scheduler receipt/vocabulary and the arm/launch authorization-binding contract.
- Define G2’s state transition and p99 estimator. Recommendation: nearest-rank over declared completed shakedowns; today `n=1`.
- Define the agent-free C3 driver’s provenance and single-writer evidence.
- Define C4’s state-changing SET→fresh GET sequence and custody binding.

Implementation-internal:

- Exact module/CLI/helper names.
- G5-first and `NOT_EVALUATED` propagation.
- G1 byte recomputation without capture-span projection.
- C1’s S-1 mapping, G3’s real-consumer call, fixture location, and refusal spellings.