# Refuter verdicts (folding into sitting packet §3)

## A-contract (Sol xhigh, envelope DISCUSSION, tree clean) — HARVESTED
- L1-B1 expiry: CONFIRMED. Remedy corrected: in-place re-author NOT contract-valid (D-131 requires
  successor pack+custody root). Open ruling: durable-freeze-evidence vs successor-pack tool.
  24h horizon is implementation policy, not D-134/D-137 contract text.
- L6-B2 refresh lane: CONFIRMED w/ qualification (partial prose exists; freeze CLI cannot reissue —
  freeze-0001 hardcoded, mutated:false short-circuit; no successor-pack command anywhere).
- L8-B4 freeze-receipt mismatch: REFUTED. Mismatch was wrong-path artifact (receipt binds canonical
  measurement-checkout absolute path; identity_matches=True all three packs at canonical path;
  committed digest not a comparison input; M-2 already governs placeholder text).
  CAVEAT: canonical-path arm probe degraded to readiness_io_error at boot lookup (read-only sandbox);
  execution lens to replay. Severity: dies as independent blocker; wrong-checkout refusal = correct fail-closed.
- Lead corroboration performed by relay agent: 33/33 receipts expired (range matches), _pack_identity
  (arm_readiness.py:1963-1984) has no digest field. Both held.

## L2-falseclean (Sol xhigh, envelope valid; worktree deleted mid-run by harness cleanup — ruled
## environment audit-trail gap, probes continued read-only on main at same HEAD, verified clean) — HARVESTED
READY DOES NOT SURVIVE. L2 -> NOT-READY.
- NEW BLOCKER L2-1 (raised from L2's own should-fix): detect_pulses region projection has NO finite
  work budget; frozen chain calls it synchronously UNDER THE WRITER LEASE (validate_powermetrics_fiducial.py:846
  acquire, :1509 call, :1037 release; runbook:1017 no watchdog; powermetrics_fiducial.py:555 unbounded loop).
  Remedy: bounded evaluation/wall budget -> registered invalid-evidence + governed abort.
- NEW BLOCKER L2-COV-1: coverage 15/16 REFUTED — self-selected universe; omitted contracts, bootstrap/
  backfill scripts, 23-test three-window lifecycle module; crash matrix is 13 tests not 16; real direct
  test universe 251.
- NEW BLOCKER L2-EDQ-1: charter forbids deferred ED-QUAL at READY; live writer/sudo + crash-matrix
  qualification open.
- L2-2 missing-parent raw traceback CONFIRMED should-fix (typed refusal remedy).
- L2-3 needs_pin_commit contradiction CONFIRMED, RAISED nit->should-fix (can mechanically abort every
  correct pre-slot session).
- L2-4 idempotent-marker WO REFUTED as phantom (runbook forbids re-reserving; reprint would mislead) — drop WO-L2-4.
- Falsifiers run by refuter: ledger tamper failed closed; non-finite power sample edge survived.
- Lead-side replay by relay: crash-matrix count 13 confirmed, three-window 23 confirmed, missing-parent
  traceback reproduced.
- Residual: stateful tests sandbox-blocked; PR #149 CI not re-queried (no network).

## DG-contract (Sol xhigh, envelope findings/complete; worktree vanished mid-run, continued read-only
## on main same HEAD — env gap noted) — HARVESTED FROM DISK (refuter-DG-out.md)
- L1-B2 kernel fail-open: PARTIAL->survives as blocker (zero global gates + P2-006 READY confirmed;
  refuted portion: D-117 does not formally retire P2-006 — needs a ruling, not deletion).
- L8-B7 launch ceremony: CONFIRMED blocker (consume_launch_capability exists but never execs; chain
  has no receipt check; zero downstream consumers authenticate launch lineage). Remedy: reviewed
  launcher consume->exec + downstream provenance refusal; Ed still performs physical launch.
- L1-B3 bifurcated authority: reduced to should_fix (all three "missing" WOs are ancestors of HEAD —
  stale registration prose, not live blockers; BUT kernel carries real falsehoods: U11 row queued/
  unprojected vs PASS receipts, FCM "continues unmerged" vs merged 60d9e42). Remedy: one kernel
  reconciliation transaction; do NOT re-register shipped WOs.

## DG-execution (Sol xhigh, envelope findings/complete) — HARVESTED FROM DISK (sol-out-refuter-DG.md)
- L1-B2: CONFIRMED blocker (gen_state --check green on the contradiction; gate machinery tests pass —
  data gap not machinery gap).
- L1-B3: PARTIAL — authority-drift core called blocker by this lens (split w/ contract lens's
  should_fix; LEAD SYNTHESIS PENDING at sitting: three-WO scenario stale per both lenses).
- L8-B7: CONFIRMED blocker. Minimal WOs per both lenses: (1) kernel reconciliation, (2) atomic
  arm-consume-to-launch binding.

## RELAY FAILURE RECORD (process finding for C-058): 5 of 9 refuter relay agents wedged ~7h reading
## bridge-contract docs without launching their Sol runs; killed 2026-08-15 ~07:15, relaunched from
## lead shell per the T5 lesson (>45-min/fragile runs launch from lead shell; .status != liveness).

## B-contract (Sol xhigh, lead-shell relaunch, envelope findings/complete) — HARVESTED
All six CONFIRMED; none refuted. Corrections/additions:
- F1+F2 MERGE into ONE work order: shipped T-0 acquisition/capture tool (executes/captures E-4..E-9,
  derives boot/monotonic, builds context+launch from frozen bytes; operator provides only the
  irreducible clock observation). Nine filenames are implementation preconditions, not D-134 names.
- F3 prewindow gap arithmetic verified: clean exit ~60s vs author 600s (gap 540s). Remedy: min-dwell
  in --wait; do NOT lower author threshold.
- F4 sudo systemsetup: remedy ALREADY RULED as D-127 (exact-path/argv sudoers for the two network-time
  commands) — chartered, never implemented/installed. Land + Ed installs (ED-QUAL row).
- F5 packet: issue reviewed SUCCESSOR packet; preserve old as custody (D-134 cl.9 already required
  the packet amendment).
- F6 all four env/chain mismatches reproduce + NEW PRODUCTION-ONLY DEFECT: author line 1149 joins
  plan_tree.json's repo-relative plan path onto pack_root -> doubled nonexistent path
  (pack_root/configs/campaigns/.../calibration_plan.json); test fixture uses bare filename so suite
  misses it. FROZEN_PLAN meaning needs a ruling before changing prose or parser.
- Minimal WO set (per refuter): (1) T-0 producer tool + operator step; (2) prewindow dwell + D-127
  install; (3) env/chain/manifest/plan-path contract + real-pack test; (4) successor packet after
  end-to-end pass.

## A-execution (Sol xhigh, lead-shell relaunch, envelope findings/complete) — HARVESTED
- F1 (expiry) CONFIRMED executed: 33/33 generic receipts refuse readiness_record_expired via
  _authenticate_generic_evidence_item at live monotonic; remedy "partial" (concurs with contract lens:
  lifecycle design ruling needed).
- F2 (no refresh lane) CONFIRMED: producer exists, operative refresh lifecycle for a frozen pack does not.
- F3 REFUTED with two-lens concurrence: canonical-path probe executed, identity_equal True at
  /Users/edr/JouleWise-measurement-20260813 pack; mismatch reproduces only from audit scratch path.
  F3 CLOSED as artifact (correct fail-closed wrong-checkout refusal).
CLUSTER A ADJUDICATED: one launch-blocking expiry/lifecycle defect (design ruling: durable freeze
evidence vs successor-pack tool), one artifact dismissed.

## ECF-contract (Sol xhigh, lead-shell relaunch, envelope findings/complete) — HARVESTED
All four CONFIRMED (L10-B1 consumption edge, L4-B1 margin recorder, L9-B1 maintenance census,
L9-B2 browser/monitor regexes). Qualifications: L1 custody discipline does not categorically bar
post-collection implementation (but heightened proof burden -> blocker stands); CI-coverage
narratives on F3/F4 qualified (sandbox denied pgrep replay/tmp — exit 3; unittest not run; static
+ earlier live L9 observations stand). Remedies ruled sound: governed prospective validator +
finalizer + queue row; recorder governed-vocabulary authorization for exactly the plan-tree-pinned
spec path; activity-based census re-shape per WO-L9-1/2.

## ECF-execution (Sol xhigh, lead-shell relaunch, envelope findings/complete) — HARVESTED
All four CONFIRMED with executed probes: V2 load_manifest refuses v3.prospective schema verbatim;
V3 margin recorder REFUSE authoritative_input_invalid (forbidden key 'estimator_registration' at
pack-pinned spec.cells[1]); F3/F4 census over-match confirmed on launchd running-state + regex
analysis (live pgrep denied in sandbox — earlier live L9 observation stands). Consolidation: F3+F4
= ONE census-semantics work order. F1 wording correction noted.
CLUSTER ECF ADJUDICATED: 4/4 confirmed by both lenses (2 WOs: consumption edge; recorder
authorization; +1 census-semantics WO).

## B-execution (Sol xhigh, lead-shell relaunch, envelope findings/complete) — HARVESTED
F1/F2/F3/F5/F6 CONFIRMED (F1+F2 one defect; F3 executed replay: READY in 60.09s vs 600s required;
F6 all four mismatches + doubled plan-path independently confirmed). F4 PARTIAL: privilege gap
survives; its timing premise dies (current E-7b ~1 min so sudo cache not necessarily cold — becomes
true once F3's 10-min dwell lands; land D-127 route regardless).
NEW DISCOVERY: baseline ac3fe1d lacks the three JouleWise-Terminal-Review* commit trailers the T-0
author demands (arm_readiness_evidence_t0.py:918-930) — terminal-review evidence needs an
operational producer too; folds into the integrated T-0 repair WO.
Minimal program per refuter: (1) ONE integrated T-0 acquisition/contract repair (nine-input producer,
10-min continuous wait, privileged clock route, env/manifest/plan/chain alignment, terminal-review
evidence, real-pack author->ARM->verify->consume rehearsal); (2) dependent re-freeze + packet reissue
at the exact reviewed head.

# ADJUDICATION TALLY (all 9 refuter runs harvested 2026-08-15)
- 19 blocker-level claims examined (16 fleet + 3 raised by L2 attack).
- DEAD: L8-B4 freeze-receipt mismatch (both lenses, artifact); WO-L2-4 (phantom); F4-timing premise.
- DOWNGRADE PENDING LEAD SYNTHESIS: L1-B3 authority bifurcation (contract: should_fix; execution:
  blocker-for-drift-core; three-WO scenario stale per both).
- ALL OTHER BLOCKERS CONFIRMED, several with executed refusals and remedy corrections.
- NEW DEFECTS FOUND BY REFUTERS: doubled plan-path (production-only, suite-masked); terminal-review
  trailer producer gap; L2 unbounded lease-held detector (raised); L2 coverage denominator false.
