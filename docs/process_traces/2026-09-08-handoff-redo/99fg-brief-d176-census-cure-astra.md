WRITE_SCOPE: ["joulewise/arm_readiness.py","joulewise/night_gate.py","configs/production_custody_inventory.json","scripts/rehearse_t0_unattended.py","tests/test_arm_readiness.py","tests/test_arm_readiness_schemas.py","tests/test_night_gate.py","tests/test_rehearse_t0_unattended.py","tests/test_t0_rehearsal.py","docs/contracts/pack_night_go_receipt.md"]

# D-176 census cure — second cold gate synthesis items 1–6 (gpt-6-astra, HIGH, genre implementation)
Branch int/2026-09-08-d176-seats-2-3 at 93870527. The ruling is the synthesis at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ey-coldgate-packet-d176-second-gate/13-magistrate-synthesis.md (governs; 10 = cold judge, 11 = Opus, both beside it).
Install items 1–6 exactly as a "§10.4 census cure (2026-09-08)" block in the contract, propagated to §6, the census
table and your §9 rows: (1) delete the CLONE_DERIVED kind and the repo_runs spec; PRODUCTION_CUSTODY_ROOTS admits only
LITERAL / HOME_RELATIVE / INVENTORY; add deployment_runs (INVENTORY measurement_root/runs), deployment_custody
(INVENTORY custody_root), deployment_ledger (INVENTORY ledger_path), the resolver expanding "key/suffix" and skipping
null locators; fill the canonical checkout's real runs root + ledger path into configs/production_custody_inventory.json
(read joulewise/calibration_ledger.py ~:94–98 for the ledger home); (2) launcher identity in BOTH the consumer
(arm_readiness, before the census loop) and the gate: resolve(strict=True)(plan.measurement_root) must equal
Path(arm_readiness.__file__).resolve().parents[1], else refuse launch_go_receipt_invalid detail "measurement_root:
launcher is not the planned clone"; (3) for T0_REHEARSAL the running checkout must not equal/contain/be contained by any
deployment_measurement_root entry (rehearsal_roots_not_disjoint: measurement_root) AND its basename must start with a
reviewed constant REHEARSAL_CLONE_PREFIX = "JouleWise-rehearsal-" beside the census (refusal named); (4) the inventory
bytes read at ARM and at consumption must equal `git show <plan.repo_head>:configs/production_custody_inventory.json`
in the driver checkout (never HEAD:), with the measurement clone at exactly plan.measurement_head — amend
_production_inventory accordingly (it moved into arm_readiness in seat 2's nits); (5) regressions: with the REAL
resolver and shipped inventory, measurement_root = Path(arm_readiness.__file__).parents[1] passes when un-inventoried
(and its runs/ exists) and refuses when inventoried; invariant that no spec kind is CLONE_DERIVED; invariant that every
non-null inventory custody_root/ledger_path appears in the resolved census; launcher-identity refusal; prefix refusal;
the pin-to-repo_head check refuses a local commit that deletes an entry; (6) confirm the two nits (prefix single home,
missing pack_root) are already cured by 93870527 or cure them. A PARALLEL seat 4 edits scripts/run_night.py,
joulewise/t0_rehearsal.py and the contract §10.5 — do not edit run_night.py; in t0_rehearsal.py touch only what the
G6 census derivation needs (say what), and write only §10.4 + your own §9 rows in the contract.
Acceptance (rc-gated to a log; named modules ONLY, NEVER discover/shard; end your turn after the named acceptance):
tests.test_arm_readiness tests.test_arm_readiness_schemas tests.test_night_gate tests.test_rehearse_t0_unattended
tests.test_t0_rehearsal tests.test_launch_window tests.test_docs_freshness; git diff --check; no commit; header < 8192
bytes; report = per-item map (item → file:line → test → counterfactual).
