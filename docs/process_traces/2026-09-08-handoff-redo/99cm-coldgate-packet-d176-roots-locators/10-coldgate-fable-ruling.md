**Contamination disclosure.** The harness injected the global `~/.claude/CLAUDE.md` and the memory index into my system prompt before the packet; I opened none of them, nor RUN_STATE.md, AGENTS.md, repo CLAUDE.md or any memory file. I read only 00-PACKET.md (sha256 verified `0194d808…cfd82`), exhibit A, the contract, and the code/docs cited below at checkout 0a29b075. Static reads only; no test suite executed.

# Cold-gate Fable ruling — D-176 seat 2: roots census (Q1), driver locators (Q2)

## Q1 — PRODUCTION_CUSTODY_ROOTS

**Q1.1 Shape.** A frozen tuple of `ProductionRootSpec(role, kind, value, predicate)` at the `arm_readiness.py:223` constants area, plus a pure `production_custody_roots(*, home) -> tuple[ProductionRoot, ...]` returning the existing `t0_rehearsal.ProductionRoot` (t0_rehearsal.py:190–196). `kind` ∈ {LITERAL, HOME_RELATIVE, HOME_GLOB}; `predicate` ∈ {DISJOINT, SIBLING_CHILD}. Roles:

| role | kind / value | predicate | evidence |
|---|---|---|---|
| `magistrate_state` | HOME_RELATIVE `night-custody/magistrate` | DISJOINT | scripts/magistrate_watchdog.py:55; install_magistrate_watchdog.sh:46 |
| `night_custody_parent` | HOME_RELATIVE `night-custody` | SIBLING_CHILD | watchdog scans `*/night_plan.json` siblings (magistrate_watchdog.py:259); run_night.py:633 uses `custody_root.parent/magistrate` |
| `backup_icloud` | HOME_RELATIVE `Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup` | DISJOINT | scripts/paper_excursion_decomposition.py:95–97; same literal at check_paper_replay_fence.py:333, paper_anchor_correction_quantified.py:224 |
| `quiet_guard_state` | LITERAL `/Library/Application Support/JouleWise/quiet-guard` | DISJOINT | joulewise/quiet_guard.py:39 |
| `measurement_clone` | HOME_GLOB `JouleWise-measurement-v5-*` | DISJOINT | packet statement only. NOT EXECUTED: no code constant names this pattern; seat 2 cites the clone-creation site or drops the role with a dated note |

Excluded: the calibration custody store has no default root in code (run_campaign.py:4834–4846 takes a caller path; calibration_ledger.py:79–94 is schemas only); comment the exclusion. The `JOULEWISE_BACKUP_ROOTS` env override (paper_excursion_decomposition.py:137) is NOT honoured by the census; a regression pins the three script literals to the constant. ARM-context roots (ARM_CONTEXT_KEYS :363–375) are NOT members: for a T0_REHEARSAL they are the rehearsal's own fresh roots and would self-collide; the consumer instead applies Q1.2 to each of them.

**Q1.2 Predicate.** Rehearsal side: plan `custody_root`, `measurement_root` and each ARM-context root must not be symlinks and must `resolve(strict=True)`; failure refuses `launch_go_receipt_invalid` with the field in `detail`. Production side: specs resolve `strict=False` (a missing production root still counts). Containment is the existing `_contains` (t0_rehearsal.py:741–746), `child.relative_to(parent)` on resolved paths, equality included; never a string-prefix compare. DISJOINT roles: any containment refuses `rehearsal_roots_not_disjoint`. `night_custody_parent` (SIBLING_CHILD): `custody_root` passes iff `custody.parent == parent_resolved and custody.name == receipt["pack"]["window_id"]` (the prefixed ARM id, §6/S1); `measurement_root` must be wholly outside the parent. Equal-to-parent, deeper nesting, or another basename refuses. So a rehearsal at `~/night-custody/rehearsal-t0-unattended-…` passes while production windows, the stub night `rehearsal-20260909` and `magistrate/` are siblings, disjoint by construction.

**Q1.3 G6 read.** `rehearse_t0_unattended.py:149–175` stops deriving roots from the manifest. The loader calls `production_custody_roots(home=Path.home())` into `EvidenceBundle.production_roots`; the manifest list remains an evidence record that must equal the derived census (role set and resolved paths) or the loader raises `BundleLoadError("production-root census incomplete")`, discharging the §7 incomplete-census replay. G6 (t0_rehearsal.py:779–787) keeps `resolution_error` → FAIL and the bidirectional check for DISJOINT roles, and uses the SIBLING_CHILD rule for the parent role. The fixture at tests/test_t0_rehearsal.py:537 carries the full role set under a fake home.

**Q1.4 Frozen yet true.** The constant holds derivations, not clone paths; any role change is a reviewed diff. A regression enumerates every role's resolved value under a synthetic home.

## Q2 — driver locators and ARM-before-GO

**Q2.1 pack_root: option (a), narrow §10.3 amendment.** `pack_night` gains a sixth exact key `pack_root` (absolute, non-symlink, basename == `pack_id`). Preparation needs the root before any ARM exists, and NOT EXECUTED: no packs-directory convention exists in code to derive it. Substitution is a digest mismatch: at preparation, GO and consumption `committed_pack_tree_sha256(pack_root)` (:5271) is recomputed and must equal `pack_night.pack_sha256` and ARM `receipt["pack"]["pack_sha256"]`; ARM `receipt["pack"]["pack_root"]` (PACK_KEYS :343–354, written :5266–5291) must equal the resolved plan value.

**Q2.2 ARM receipt: option (c).** Never selected. The driver's ARM step writes `<custody_root>/<pack_id>/arm_readiness.receipts/arm-NNNN.json` (namespace :8749–8752, custody pack root :9684, name pattern :4380) and presents exactly that path. GO `arm_receipt{receipt_id, sha256}` binds it; the consumer's supersession scan (:8755–8775) and `.consumed.json` check (:8786–8790, C5) refuse any other. Driver refusals before GO: a higher-numbered unconsumed receipt for this pack this boot, or any existing consumption this boot → refusal in `night/receipt.json`, no GO file.

**Q2.3 Launch manifest: option (b).** Fixed name `<custody_root>/<pack_id>/arm_readiness.t0.inputs/launch-manifest.json` (`_T0_INPUT_DIRECTORY` :101; :9196, :9260). Absent, symlinked, or digest ≠ the T-0 author's attested sha256 → refuse. GO `launch_manifest_sha256` is that digest; `window.env` and chain digests follow the manifest's own references as the consumer already does (:2633).

**Q2.4 Preparation entry.** Not a file locator; it is the driver's in-process sequence, and the launcher is the only external argv:

1. Census (existing first act) → `night/censuses.jsonl`; hit → refuse.
2. Read the installer-pinned plan bytes → `plan_sha256`; `NightPlan.from_mapping` v3; malformed → existing path (run_night.py:1058).
3. Preparation: recompute the pack tree digest at `pack_night.pack_root`; re-read and re-digest both plan record locators; mismatch → refusal in `night/receipt.json`, no GO.
4. ARM: author T-0 evidence (`author_arm_readiness_evidence_t0`, arm_readiness_evidence_t0.py:2245) and the ARM receipt into the Q2.2 namespace, then `_verify_arm_receipt` on the written path with `require_unconsumed=True`; `arm_disposition` NO_GO (:8441) → refuse.
5. GO: evaluate C1–C5; write `night/go_receipt.json` O_EXCL 0600 (§10.1 F2).
6. Launcher argv, `stdin=DEVNULL`: `scripts/launch_window.py --pack-root <plan pack_root> --arm-receipt <step-4 path> --arm-readiness-custody-root <plan custody_root> --launch-manifest <Q2.3 path> --night-plan <pinned> --go-receipt <custody>/night/go_receipt.json --step6-confirmation-table <record table_path> --expected-confirmation-digest <record table_sha256>`. This replaces the direct `chain_path` exec (run_night.py:1211–1225) for TRANSACTION_PACK; the sidecar digest check stays.

**Verdict: RULED — derivation-shaped frozen census with a sibling-child rule for the night-custody parent; plan-carried pack_root (§10.3), driver-written ARM, fixed-name manifest, in-process preparation; seat 2 may resume.**
