# Independent read-only audit — MET-VERDICT-ADJ-01 (Sol xhigh, session 019fbf3c-a750-76b3-858a-dfb9eb0dbf3f, 2026-08-01)

Audited at BASE_HEAD 8129a2b374b8c35c786f5a307862ac435295121d. Envelope
validated (single final BRIDGE_REPORT_V1, status DISCUSSION, pathspec []).
Magistrate bench verification 2026-08-01: power_policy mismatch CONFIRMED
(pre "ac_high_power" vs retry "configs/campaign_policies/quiet_mac_p2_production.json",
both standalone valid); policy hard value 0.01 CONFIRMED; hard-cliff code
path CONFIRMED (calibration_bracketing.py ~line 300, no allowance branch);
r08 double-declaration across two manifests CONFIRMED.

| Group | Classification | Could repaired machinery change status? |
|---|---|---|
| (a) dangling quarantine | CONTRACT GAP | No under the minimal fail-closed repair |
| (b) deviation post-cal | MACHINERY DEFECT, although retry rejection itself is correct | No for A because its retry is T1-incompatible |
| (c) window-B membership/NEG-8 | CORRECT for B; one latent reader defect noted | No for these corpus bytes |

## (a) CONTRACT GAP — dangling quarantined-without-replacement

- Runner records attempted members as execution="invoked" even on failure
  (run_campaign.py:6418, :6527). Window A: ONE invoked declaration for its
  dangler. Window B: TWO invoked declarations for its twice-failed r08.
- ONE declaration: accepted without a canonical-path presence check
  (run_campaign.py:3972); later strict validation excludes it and adds
  whole_window_bundle_invalid (:4262).
- TWO declarations: routed to the duplicate path requiring exactly one
  canonical present bundle + one exact supersession (:3983); B has neither
  for r08, so the entire group is discarded and membership becomes
  unresolved (:3994, :4057) — DISCARDING the valid, unrelated
  mtnull-o0512-b04-b2 supersession with it.
- Neither window's environment_admission_* condition is attributable to
  the absent dangler (excluded members are not passed to the core :4265;
  fallback scans only present dirs :4057).
- Contract: §10 (runbook:772,:817) requires quarantine+rerun+supersession-
  after-replacement; D-087 requires third-failure salvage close; D-094
  requires exact supersession for multi-invoked shapes. NO contract defines
  the terminal whole-window representation when salvage closure prevents
  the required replacement. A's count-one exclusion and B's count-two
  membership refusal are ACCIDENTAL COUNT-DEPENDENT OUTCOMES, not two
  governed semantics.
- Minimal repair (fail-closed): zero surviving occurrences without an
  exact selected supersession => terminal
  whole_window_campaign_membership_unresolved regardless of declaration
  count; presence check on the len==1 branch; regressions both shapes.
  ~20-40 prod + 50-100 test lines. CANNOT make either window pass.

## (b) MACHINERY DEFECT — with CORRECT retry rejection

- Selector authenticates candidates (calibration_bracketing.py:105),
  requires protocol v3 + exact T1 binding match (:255), picks latest valid
  pre / earliest valid post (:266,:289); EMPTY side => all-null initial
  bracket returned, which is why A's VALID PRE was also nulled (:231,:282).
- A's deviation retry is standalone valid but binds
  power_policy="configs/campaign_policies/quiet_mac_p2_production.json"
  vs "ac_high_power" on the pre and all members
  (instrument_validation/20260731T215120-fa1e9cda/instrument_evidence.json:28
  vs 20260731T161713-b8b08280/...:28). T1 exact stationarity
  (powermetrics_fiducial.md:77,:109) makes the rejection CORRECT: valid
  calibration artifact != eligible T1 endpoint. A failed attempt does not
  block a retry (runbook:847).
- THE DEFECT (non-salvage severity escalator): had the retry matched, the
  selector hard-refuses drift above the obsolete 0.010 policy value
  (policy json:2; calibration_bracketing.py:300). D-079 mandates the
  derived 0.010818 s screen + propagated allowance for ordinary
  repeatability excess (decision_log:4715,:4887). No calibration-drift
  allowance is emitted or propagated anywhere in this code. Every ordinary
  complete window slightly above the cliff is currently mis-ruled.
- Repair: keep authentication + earliest-valid selection; implement the
  D-079 provenance-bound screen, freshness refusal, excess allowance,
  evaluation-basis recording, floor/claim propagation. ~5-8 files,
  400-800 lines, delegated claim-semantics commit + independent review.
- Post-repair, window A STILL cannot form a bracket (immutable
  T1-incompatible retry). A remains FAILED; relaxing exact matching would
  be contract-false.

## (c) CORRECT for window B — plus one latent fail-open

- Resolver's glob/pattern/schema/chain handling all work: scans
  campaign_manifests/*.json, v1 + policy-hash filter, groups missing
  analysis_manifest_id as "<none>" (:3796). All eight B manifests pass the
  filters. It first resolves the valid mtnull-o0512-b04-b2 supersession
  (campaign_log.jsonl line 119), then the twice-invoked zero-present r08
  fails its group, discarding everything (:3965,:4003) => both
  source_campaign_manifests and occurrence_supersessions empty.
- NEG-8 conditions are PURE CASCADE: diagnostic fallback sources lose
  role/position identity (:198,:4067) => no start/end roles (:3541;
  whole_window.py:1609) => empty reference metadata => freshness
  binding_status "missing" (whole_window.py:962) => unresolved current
  binding deliberately classified "stale" (:1028). The bound's age had NOT
  expired (derived_at_s + 86400 s horizon present in
  neg8-drift-bound.json:64). "Stale" is the contract's umbrella name for
  expired/changed/missing/conflicting bindings (runbook:784). Not a clock
  bug. No B-specific repair independent of (a).
- LATENT ESCALATOR: _valid_supersession_entries silently skips malformed
  JSON/validation failures (:3737) despite D-093/D-094 requiring
  recognizable invalid same-bundle records to stay visible and force
  ambiguity (decision_log:5697,:5769); manifest parsing similarly skips
  unreadable/wrong-schema candidates (:3800). Did not affect A or B
  (their bytes are valid); could FAIL OPEN on a non-salvage window.
  Repair: reuse supersession_entry_validation_results, fail the candidate
  group on malformed catalog entries, valid+malformed regressions.
  ~2 files, 100-200 lines, delegated (claim-bearing membership semantics).

## Flags

CONTRACT_GAP_DANGLING_TERMINAL_DISPOSITION;
MACHINERY_DEFECT_D079_CALIBRATION_BUDGET_UNIMPLEMENTED;
NON_SALVAGE_ESCALATOR_D079_HARD_CLIFF;
LATENT_NON_SALVAGE_ESCALATOR_WHOLE_WINDOW_READER_FILTERS_INVALID_RECORDS;
AS_ISSUED_VERDICTS_UNCHANGED; COLD_GATE_NOT_INVOKED.

No files modified, no verdicts re-run, no tests executed by the auditor.
