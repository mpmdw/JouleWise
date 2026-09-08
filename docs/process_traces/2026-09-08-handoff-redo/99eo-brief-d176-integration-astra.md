WRITE_SCOPE: ["docs/contracts/pack_night_go_receipt.md","tests/test_arm_readiness_schemas.py","joulewise/arm_readiness.py","scripts/launch_window.py","joulewise/night_gate.py","scripts/run_night.py","tests/test_launch_window.py","tests/test_arm_readiness.py","tests/test_arm_readiness_lifecycle.py","tests/test_run_night.py","tests/test_night_gate.py","docs/contracts/d078_reason_registry_amendment.md"]

# D-176 integration tree — seats 2 + 3 (gpt-6-astra, HIGH, genre implementation)
Branch int/2026-09-08-d176-seats-2-3 at 02ea7e05 = main 99a42edb + seat 2 (feat/2026-09-08-d176-seat2-producer
ad74e36c, merged clean) + seat 3 (feat/2026-09-08-d176-seat3-consumer fda090f2, committed as WIP with CONFLICT
MARKERS in docs/contracts/pack_night_go_receipt.md and tests/test_arm_readiness_schemas.py). Both seats were reviewed
to LAND-with-fixes-applied separately (reports/reviews under /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/: seat 2 = 99dq/99dx/99dy/99ej/99el/99en; seat 3 =
99cu/99eg/99ek). Governing texts: the contract itself (§§2–6, §7.1, §9 + §9.1, §10–§10.3) and the three-seat
synthesis /Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99cm-coldgate-packet-d176-roots-locators/13-magistrate-synthesis.md (item 3 assigns the consumer-side
predicate to seat 3; item 5 the pack_root digest check at CONSUMPTION; seat 2's report 99dq F1 deferred the
consumption-point proof to this integration). Do, in order:
1. Resolve the two marker files SEMANTICALLY: the contract's §9 (seat 2 rows) and §9.1 (seat 3 rows) both stay, §10.2
   (seat 3 rulings) and §10.3 (seat 2 rulings) both stay in numeric order; the schemas test keeps both seats' tests
   (seat 2's resolver/inventory tests and seat 3's GO/v3 schema tests). No marker may remain.
2. Wire seat 3's consumer to seat 2's interfaces: (a) the v3 plan's sixth exact `pack_night.pack_root` key —
   `_consume_launch_capability` recomputes `committed_pack_tree_sha256(pack_root)` and refuses on mismatch against
   `pack_night.pack_sha256` and the ARM receipt's `pack.pack_sha256`/`pack.pack_root` (the THIRD digest point;
   regression = the deferred consumption-point mutation); (b) the consumer applies the census predicate (seat 2's
   `production_custody_roots` resolver + `_contains`, SIBLING_CHILD for night_custody_parent on custody_root only,
   DISJOINT for the other roles) to the plan's `measurement_root`, `custody_root` and EACH ARM-context root for a
   T0_REHEARSAL purpose, refusing `launch_go_receipt_invalid` detail `rehearsal_roots_not_disjoint`; (c) night_gate
   requires an ABSOLUTE, strictly-resolving `custody_root` (Opus Q1.7; refusal named); (d) seat 3's launch fixtures
   that "substitute the absent seat-2 parser" now use the real v3 parser and the real GO producer output from seat 2
   (an end-to-end fixture: driver prepares → ARM → GO → launcher argv → consumer consumes → verify_consumed_launch
   replays) — this is the integrated-head proof both seats deferred.
3. Update §9/§9.1 rows whose pins moved; §7.1 records the integration.
Acceptance (rc-gated to a log; named modules ONLY, NEVER discover/shard — the lead owns the full replay):
tests.test_night_gate tests.test_run_night tests.test_t0_rehearsal tests.test_rehearse_t0_unattended
tests.test_night_plan_writer tests.test_install_night_agent tests.test_magistrate_watchdog tests.test_arm_readiness_schemas
tests.test_arm_readiness_lifecycle tests.test_launch_window tests.test_arm_readiness tests.test_d078_reason_registry
tests.test_docs_freshness; git diff --check; no commit; header < 8192 bytes; report = the end-to-end fixture's
sequence with file:line, the three digest points' regressions, and any NEEDS_RULING.
