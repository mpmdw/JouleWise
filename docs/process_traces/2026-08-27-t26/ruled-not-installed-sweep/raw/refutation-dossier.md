# S9 — candidate findings for the adversarial refutation pass

Baseline: `/Users/edr/code/JouleWise` at `origin/main` = `0dd3b6dc`.
Each entry below is a PROVISIONAL finding assembled at the bench. A refuter's
job is to TRY TO PROVE IT IS INSTALLED — find the route, the check, the runbook
line, or the supersession that makes the finding wrong. A finding survives only
if the refuter fails to break it.

---

## CAND-1 — the finalized-v3 manifest has no producer route (B/C)

**Claim.** The claim edge requires a FINALIZED v3 analysis manifest. The only
thing that can produce one is
`finalize_prospective_analysis_manifest_v3` (`joulewise/analysis_manifest_v3.py:3722`),
exposed by the CLI `scripts/finalize_analysis_manifest.py`. Nothing invokes it
outside its own tests, and no operator-facing document contains a step that runs it.

**Bench evidence.**
- `joulewise/analysis_engine/inputs.py:34,593` — `analyze-claims` calls
  `validate_finalized_analysis_manifest_v3`; the finalized schema is required.
- `grep -rn "finalize_prospective_analysis_manifest_v3"` over the whole tree:
  every non-definition hit is in `tests/test_analysis_finalizer.py` and
  `tests/test_analysis_integration.py`. No production caller.
- `grep -c "finalize_analysis_manifest|analyze-claims|analyze_claims|finalize_prospective"`
  returns **0** for every one of:
  `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md`,
  `docs/process/phase2-transaction-runsheet.md`,
  `docs/phase_2/window_runbook.md`,
  `docs/process/rehearsal-operator-card.md`,
  `docs/process/ed-evening-checklist.md`,
  `scripts/prewindow_check.sh`.
- The `analyze-claims` subcommand does exist (`joulewise/cli.py:2284`) but no
  runbook invokes it either.
- **This was already found on 2026-08-19** and recorded, not fixed:
  `docs/process_traces/2026-08-19-prep-sprint/ready-packet-rows/19-ROW-L10-sacrificial-lifecycle.md:523`
  — *"The finalizer has no operator step"*; and
  `docs/process_traces/2026-08-19-prep-sprint/ready-packet/OPEN-ITEMS.md:785`.

**Refuter's task.** Find ANY production route: a script, a Makefile target, a CI
job, a runbook phase (including phases named only by pointer), a kernel row that
schedules it, or a documented desk procedure. If the intended answer is "this is
post-window desk work outside the runbook," find where that desk work is
specified, and say whether the transaction night is affected or only the analysis
that follows it.

---

## CAND-2 — `window.env` 25-key allowlist vs the runbook's `ARM_RECEIPT` / `LAUNCH_MANIFEST` (B)

**Claim.** `docs/phase_2/window_runbook.md:1339-1340` instructs the operator that
`window.env` "must additionally bind the absolute `ARM_RECEIPT`,
`ARM_READINESS_CUSTODY_ROOT`, and `LAUNCH_MANIFEST` paths used by E-10", and the
chain body dereferences `"$ARM_RECEIPT"` (`:1357`) and `"$LAUNCH_MANIFEST"`
(`:1359`) under `set -euo pipefail`. But `_ENV_KEYS` in
`scripts/capture_t0_step.py` is an EXHAUSTIVE 25-key frozenset containing
neither, and `_parse_window_environment` refuses any `unknown` key with
`evidence_author_t0_capture_environment_invalid`.

**Bench evidence.**
- `scripts/capture_t0_step.py:226-267` — the parser; `missing = _ENV_KEYS - set(values)`,
  `unknown = set(values) - _ENV_KEYS`, refusal on either.
- `_ENV_KEYS` frozenset: MEASUREMENT_REPO, WINDOW_ID, BRACKET_SESSION_ID,
  FROZEN_PLAN, PACK_ROOT, PACK_ID, PLAN_ID, EVIDENCE_ROOT_ID, IDENTITY_EPOCH_JSON,
  T1_BINDINGS_JSON, PRE_ATTEMPT_ID, POST_ATTEMPT_ID, RUNS_ROOT, BOUND_RUNS_ROOT,
  CALIBRATION_LEDGER, LEDGER_HEAD_PIN, ARM_READINESS_CUSTODY_ROOT, CUSTODY_ROOT,
  WINDOW_CUSTODY_ROOT, QUARANTINE_ROOT, CLAIM_BACKUP_DEST, BOUND_BACKUP_DEST,
  WAIVER_PATH, POWER_POLICY, SETTLE_S — 25 keys, no ARM_RECEIPT, no LAUNCH_MANIFEST.
- `docs/phase_2/window_runbook.md:1196,1209,1211,1339,1340,1357,1359,1498,1500,1544,1546`
  all reference them.
- **Known and recorded instead of fixed**: `docs/process/rehearsal-operator-card.md:5`
  says the exclusion "differs from the runbook chain wording. The paths are
  derived after ARM in this card; do not edit `window.env`." That is a workaround
  living in one card while the runbook still says the opposite.
- Prior finding: `docs/process_traces/2026-08-19-prep-sprint/ready-packet/17-ROW-L8-operator-recovery.md:224-233`.

**Refuter's task.** Determine which document actually governs the `_v4`
transaction night — `real-transaction-runbook.md`, the operator card, or
`window_runbook.md` §6 — and whether the contradiction can still be reached on
that night. Check whether the open PR #205 runbook delta removes, preserves, or
duplicates the contradictory wording. Also confirm whether the second parser
(`joulewise/arm_readiness_evidence_t0.py:575-690`) enforces the same key set or a
different one; a divergence between the twins is its own finding.

---

## CAND-3 — the collector never reads the v3 analysis manifest, so every campaign
## manifest records `analysis_manifest_id: null` and the claim edge selects nothing (B)

**This is the strongest candidate; it is the exact D-157 shape and it is
end-to-end.**

**Claim.** The collector resolves its analysis manifest by the fixed basename
`analysis_manifest.json`. The gamma pack ships `analysis_manifest_v3.json`. No
pack in `configs/` ships a file named `analysis_manifest.json` at all. So
`load_analysis_manifest` returns `None`, the campaign provenance records
`analysis_manifest_id: null`, and at claim time the cooldown/evidence join
selects only campaign manifests whose `analysis_manifest_id` EQUALS the v3
manifest id — i.e. none of them.

**Bench evidence (chain, each line opened and read).**
1. `scripts/run_campaign.py:195` — `ANALYSIS_MANIFEST_NAME = "analysis_manifest.json"`.
2. `scripts/run_campaign.py:1201-1204` — `load_analysis_manifest` builds
   `path = config_dir / ANALYSIS_MANIFEST_NAME`; `if not path.is_file(): return None`.
3. `scripts/run_campaign.py:1226-1240` — the routing branches on
   `raw["schema_version"] == AXI_MANIFEST_SCHEMA_VERSION` → v2 validator, `else`
   → `validate_analysis_manifest` (v1). **There is no v3 branch.**
4. `ls configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3` → the pack ships
   `analysis_manifest_v3.json` and `order_manifest.json`. `find configs -name
   "analysis_manifest.json"` → **no results anywhere in the repo's configs.**
5. `scripts/run_campaign.py:3002-3004` — campaign provenance records
   `"analysis_manifest_id": analysis_manifest.manifest_id if analysis_manifest
   is not None else None` → `null` for every `_v4` campaign.
6. `joulewise/analysis_engine/inputs.py:2143` — `selected = raw.get("analysis_manifest_id") == manifest_id`
   and `:2191` — `if raw.get("analysis_manifest_id") != manifest_id: continue`.
   `manifest_id` at claim time comes from `_manifest_collection_id`
   (`inputs.py:2049`-ish / `:2138`), which for a finalized v3 manifest is
   `lineage.collection_manifest_id`, set at `analysis_manifest_v3.py:3646` to
   `prospective["manifest_id"]` — a real, non-null v3 id.
7. `inputs.py:2050-2056` documents `manifest_id=None` as the CALIBRATION-campaign
   case, confirming null is not the production-campaign contract.

**Consequence if unrefuted.** A 168-hour `_v4` campaign collects normally and
then joins to zero campaign-cooldown evidence at the claim edge — a dead claim
edge discovered post-window, which is precisely the failure D-157 was ruled to
prevent.

**Refuter's task.** Break the chain at any link. Specifically: (a) does anything
copy, rename, or symlink `analysis_manifest_v3.json` to `analysis_manifest.json`
into the collector's `config_dir` before the campaign runs — a runbook line, the
freeze/arm path, `package_bundle_pack.py`, or the pack generator? (b) is
`config_dir` at transaction time the pack directory or some derived staging
directory that does contain the basename? (c) is `campaign_cooldown_evidence`
actually on the `_v4` claim path, or is it reached only by a legacy/v1 route?
(d) does some other producer write the campaign provenance's
`analysis_manifest_id` for v3 campaigns? Cite file:line for whatever you find.
