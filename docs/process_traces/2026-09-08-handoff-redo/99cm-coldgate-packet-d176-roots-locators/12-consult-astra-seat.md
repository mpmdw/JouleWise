```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend frozen derivation rules backed by reviewed production inventory, isolated rehearsal custody, and deterministic preparation with driver-owned ARM issuance.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "0a29b07564b595b9f9d8189e869de3e5939c2a18",
    "head_end": "0a29b07564b595b9f9d8189e869de3e5939c2a18",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": ["AGENTS.md", "CLAUDE.md", "coldgate-packet/"],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "summary": "Production-root completeness and overlap semantics need an authoritative derivation contract."},
      {"id": "F2", "severity": "blocker", "summary": "Input discovery and preparation ownership must be ruled before producer integration."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["0a29b07564b595b9f9d8189e869de3e5939c2a18"]},
      "expected": {"exit_code": 0, "tail_regex": "^0a29b07564b595b9f9d8189e869de3e5939c2a18$"}
    }
  ],
  "flags": [
    {"id": "R1", "kind": "lead_ruling", "level": "blocking", "text": "F1/F2 are proposed contract amendments, not installed behavior.", "needs": "Adjudicate and assign implementation ownership."}
  ]
}
```

## Findings

**F1 — Q1.1.** Exercising the requested licence to disagree: freeze **derivation rules**, not ephemeral clone paths or caller-selected exclusions. Propose `PRODUCTION_CUSTODY_ROOTS` as an immutable tuple of frozen `RootSpec(role, source, selector)` records, expanded by one shared resolver. Its independently reviewed input is a new, HEAD-pinned `configs/production_custody_inventory.json`; the rehearsal plan cannot supply that inventory. Require exact deployment entries `{measurement_root, custody_root, ledger_path, calibration_custody_store, backup_roots}`; store may be null. Production installation must register changes through review.

**Q1.2.** Roles and derivations:

- `magistrate`: home-relative `night-custody/magistrate` (`scripts/magistrate_watchdog.py:55`).
- `window_custody`: home-relative `night-custody`, plus registered production custody roots.
- `measurement` / `runs`: registered production `measurement_root` and its `runs` child; never derive production from the candidate rehearsal plan.
- `calibration_ledger` / `calibration_custody`: registered ledger parent and store root; default ledger is `<production-checkout>/runs/calibration_observation_ledger.jsonl` (`joulewise/calibration_ledger.py:94`). There is **no universal external-store default**: the loader accepts an optional path and otherwise checks observation custody (`:1982`, `:2075`).
- `backup`: home-relative `Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup`, plus registered overrides. The current literal and environment override are at `scripts/paper_anchor_correction_quantified.py:107,224`; an empty environment value must not erase protected production roots.

The constant’s roles/selectors remain stable across clones; reviewed inventory supplies deployment values. Missing inventory or unregistered production destinations refuse.

**Q1.3.** Reject overlap when resolved paths are equal **or either contains the other**, using path components, never string prefixes. This preserves G6’s existing bidirectional test (`joulewise/t0_rehearsal.py:785`) and strengthens §10 S4’s one-direction wording. Require strict resolution of existing roots; errors, dangling links and loops refuse. Resolve ancestor symlinks, verify containment again at use, and reject redirected custody inputs. G6 and consumer must call the same resolver; manifest `production_roots` becomes a checked projection, never authority.

**Q1.4.** Reject the premise that existing stub custody forces a production-parent exception. Put the new rehearsal beneath `/private/tmp/joulewise-t0/<attempt>/`, with dedicated measurement, custody, ledger, runs and backups. A child cannot be disjoint from its protected parent. The old `rehearsal-20260909` location is documented at `docs/process_traces/2026-09-08-handoff-redo/27-scout-v5-readiness-astra-report.md:296`; it does not override D-176’s authenticated `rehearsal-t0-unattended-` predicate (`docs/contracts/pack_night_go_receipt.md:450`).

**F2 — Q2.1.** Adopt **derived locators plus driver-owned ARM**, with no plan-wire expansion. Let `M=plan.measurement_root`, `C=plan.custody_root`, `P=M/configs/campaigns/<pack_id>`, `K=C/<pack_id>`, `W=C/window-plan`, `I=K/arm_readiness.t0.inputs`. The pack convention exists at `scripts/ed_session/build_rehearsal_env.sh:34`; pack identity equals its basename (`joulewise/arm_readiness.py:5266`). Require a single-component pack ID and authenticated committed pack digest. No searching, “latest,” or fallback.

**Q2.2.** Sequence and files:

1. **Census/preflight:** preserve census-first (§1, contract `:99`); authenticate pinned plan, heads, authorization and confirmation paths/digests. Read `W/window.env`, `W/window-chain.zsh`, plan chain sidecar and confirmed table; require chain equality. Missing, malformed, escaping or mismatched inputs refuse before preparation.
2. **Preparation:** driver invokes pinned `M/scripts/capture_t0_step.py` once per `STEP_ORDER`, with `P,C,W`, stdin closed. It writes six named capture records plus `I/arm-context.json` and `I/launch-manifest.json` (`scripts/capture_t0_step.py:45,452`). Then call `author_arm_readiness_evidence_t0(P,C)`, retaining its exact fifteen-receipt inventory and source records (`joulewise/arm_readiness_evidence_t0.py:2245,2420`). Missing steps, failed commands, conflicting outputs or incomplete publication refuse.
3. **ARM/verify:** require fresh attempt custody and no existing ARM/consumption; call `generate_arm_receipt` once using `I/arm-context.json`. Expect `K/arm_readiness.receipts/arm-0001.json` and its `.sha256`; retain the returned path/digest (`joulewise/arm_readiness.py:8277,8459`). Reject extra receipts, substitutions, stale boot/expiry or failed unconsumed replay (`:8734–8823`). Never rename ARM to an arbitrary fixed filename.
4. **GO/launch:** evaluate C1–C5; write unchanged `C/night/receipt.json`, and only on PASS create-exclusive mode-0600 `C/night/go_receipt.json`. Launch argv supplies `--pack-root P --arm-receipt <returned-path> --arm-readiness-custody-root C --launch-manifest I/launch-manifest.json --night-plan <pinned-plan> --go-receipt C/night/go_receipt.json`, plus the authenticated confirmation-table/digest flags. Consumer rehashes inputs; mismatch refuses before consumption/capture. Any prior attempt/output collision refuses; no automatic re-arm.

## Residual risk

Live inventory, preparation and launch: **NOT EXECUTED**. §§10.2–10.3 are absent at this HEAD. No edits were made.

Verdict: adopt Q1/Q2 amendments before resuming producer implementation.