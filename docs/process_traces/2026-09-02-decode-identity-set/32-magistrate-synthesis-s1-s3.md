# Magistrate synthesis of the S1/S2/S3 design consult (files 28–31), 2026-09-02

Packet: file 29. Seats: Opus 5 (file 28, the originating counter-review),
Sol xhigh (file 30), blind Fable (file 31). Both consult seats were read-only
at `e3f52884`, disclosed harness contamination, and executed their claims.
Synthesized by the magistrate; where the seats split (S3) the split is
recorded and the decision reasoned, not voted.

## Facts all three seats and the bench agree on

- `identity_pins.py`: `_read_unit_configs` at :1592 reads, digest-checks and
  JSON-parses every inventoried configuration BEFORE the manifest-file loop
  at :1610; `_declared_manifest_path` (:1541–1568) keeps only the part of the
  repository-relative `suite_manifest_ref` after the pack directory's name
  and rewraps an unresolvable reference as "declared suite manifest is
  unauthenticated"; typing through `BenchmarkConfig` happens per configuration
  from :1636, after the manifest loop. Bench-read this session (file 29's
  packet evidence plus `sed -n 1436,1457p`, `1588,1612p`, `1630,1640p`).
- `stack_scope.measurement_arms.<arm>.workload` is written by `build_plan`
  (`generate_configs.py:1758`) into `calibration_plan.json`, which the freeze
  receipt pins by SHA — NOT into `plan_tree.json` as the packet said (packet
  correction, both seats). No consumer under `joulewise/` or `scripts/`
  (`rg -n 'stack_scope|measurement_arms' joulewise/ scripts/` → rc=1, both
  seats); the one test hit reads another pack's model fields.
- The D-166 digest `1c0a4a11…` hashes only the 2,032 canonical-JSON bytes of
  `dominance_criterion_registration()`; it does not cover `workload_for`.
- Production evidence rows never carry a pack root that fails to resolve:
  `_read_bundle` (`inputs.py:2773–2782`) authenticates the launch lineage
  first, and `_replay_consumed_arm` resolves the recorded pack root strictly
  (`arm_readiness.py:9333–9352`, refusing `launch_binding_mismatch`). Bench
  read; Fable executed the consumption hop (`launch_consumption_missing`);
  neither seat executed a fully moved bundle end to end.
- No enumerated rule-11 trigger is met by S1, S2 or S3 (all three seats;
  Opus's cold-gate placement for S3 rested on a production consequence the
  two executing seats showed does not exist through this gate).

## S1 — contract denial (UPHELD; dictated replacement AMENDED)

The dictated paragraph in packet Q3 was wrong twice: "before any
configuration is read" and "refuses before step 1" contradict :1592 → :1610
(both seats, CONTRADICTED with lines), and the unauthenticated case omits
unresolvable/unreadable references (:1563–1568, :1615–1620). Fable's point
stands: this is the third consecutive prose defect in this section and the
packet's own dictation carried it — this consult IS the consult the standing
escalation signature called for, and the corrective is that the fix-round
text is dictated WITH proving lines and the delta re-audit re-executes the
ordering probes (Fable probes (2) and (4)). The pre-existing inaccuracy in
step 1 ("parses the configuration through `BenchmarkConfig`" — typing is at
:1636, later) is corrected in the same edit. Insertion point: inside step 3
after the declared common profile is obtained (Fable) = after contract :458
(Sol) — the same place. Renumbering is unnecessary because the check is a
sentence inside step 3, so the step-4/step-6 cites elsewhere hold.

## S2 — R-2's removal clause (UPHELD; common profile alone)

Both seats: the plan's shared decode `workload` carries the common profile
only — `{name, repetitions, warmup_runs, output_tokens}` — never
`suite_manifest_set` (per arm; its ONE home is
`identity_units[*].declared_identity.workload_profile`) and never a
`prompt_tokens` that is per-arm by construction (`DECODE_PROMPT_TOKENS` is
keyed by arm; the fixture's 42/42 is coincidence). `DECODE_PROMPT_TOKENS`
itself stays (per-arm enforcement); only the literal in `workload_for`
goes. Must land before P-8 because `calibration_plan.json` is SHA-pinned by
the freeze receipt. Digest invariant holds (Sol executed the removal in
memory: `registration_sha256=1c0a4a11…`).

## S3 — machine-absolute pack root (SPLIT; ruled (d) for this lane)

| Seat | Option | Core argument |
| --- | --- | --- |
| Opus (28) | re-root; cold gate before landing | reproducibility from a clone; the forgery label is emitted for a non-forgery |
| Sol (30) | (a), widened to `_replay_consumed_arm` | gate-only re-root is dead code; re-root at the lineage replay too; digest binding unchanged |
| Fable (31) | (d) | the whole lineage layer is absolute (consumption receipt, launch manifest, window root, lifecycle receipts); re-rooting the pack root alone still analyses nothing from a clone; the gate cannot be reached with a missing root in production; a relocatable lineage is a new ruling |

Ruling: **(d) for this lane.** Sol's widening is the honest version of (a)
and shows why (a) does not fit here: once the pack root is re-rooted at the
replay, the consumption receipt, launch manifest, window root and lifecycle
receipts are still resolved by absolute path, so clone-reproducibility needs
a relocatable-lineage design across `arm_readiness` authentication — a
design lane with its own consult, not a should-fix on the decode-identity
branch. Nothing is lost mechanically today (the gate refuses correctly; the
label reached only through the direct seam is the honest one for "the gate
could not authenticate the pack"). What lands in this lane: (i) a contract
paragraph stating the limitation at the lineage layer, dictated below;
(ii) the direct-seam missing-root refusal test (closes luna 263's residual);
(iii) a kernel row `LINEAGE-RELOCATABLE-01` in the post-merge kernel batch
(bench, main). Opus's cold-gate placement is not adopted because it was
premised on a production path that does not exist; that is a finding of
fact by two executing seats, not a reinterpretation of any verdict, and (d)
changes no gate semantics. Rule-11: no trigger; recorded here for Ed.

## Fix round 3 (file 33) — first round on each of S1, S2, S3

Sol xhigh; WRITE_SCOPE `docs/contracts/identity_pin_projection.md`,
`configs/campaigns/d117_contrast_v5/generate_configs.py`,
`tests/test_d117_contrast_v5_pack.py`, `tests/test_analysis_inputs.py`,
`docs/decision_log.md` (nit-2 dated addendum). No production module under
`joulewise/`. Delta re-audit by terra xhigh (different model; re-executes
the ordering probes and the S2 digest); §5 fresh pass; integration replay;
PR; then P-8. Opus nits 1 and 3: NO CHANGE (file 28 dispositions stand);
nit 4 → post-merge kernel batch.
