WRITE_SCOPE: ["joulewise/night_gate.py","tests/test_night_gate.py","docs/contracts/pack_night_go_receipt.md","docs/process/NIGHT_HANDBACK.md","docs/process/MAGISTRATE_WATCHDOG.md"]

# D-176 census cure — Opus findings 6–9 (gpt-6-astra, medium, genre implementation)
Branch int/2026-09-08-d176-seats-2-3 at 07681e95. The Opus refutation at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99fq-ref-d176-census-cure-opus-review.md ruled LAND-WITH-FIXES. Cure: (7, should-fix) the launcher-identity check must
run BEFORE the ARM mint: move/duplicate it into `_authenticate_pack_records` (night_gate.py ~:744–751, where the pre-ARM
inventory read already sits) so a wrong-clone launch refuses without burning the single-use ARM receipt; keep the
existing post-mint check too; regression: a wrong-clone plan refuses with NO ARM receipt written. (6) contract §10.3
Q1.1/Q1.2 (~:1114, :1122): mark the CLONE_DERIVED/repo_runs lines "superseded by §10.4 (2026-09-08)" with a pointer, and
move the replacement census table to where the retired one is (or point). (8) docs/process/NIGHT_HANDBACK.md ~:33–36 and
docs/process/MAGISTRATE_WATCHDOG.md ~:302,:333,:423: rehearsal checkouts are cut as `JouleWise-rehearsal-<date>-<sha>`
(exact reviewed prefix, case-sensitive) — replace every `/private/tmp/joulewise-rehearsal-…` example; state that the
clone must NOT be listed in configs/production_custody_inventory.json and must sit at a head carrying that file. (9)
§10.4 wording: state the G6 loader's unauthenticated-GO pin is safe only because G5 authenticates afterwards (ordering
sentence); state that the driver checkout and the measurement checkout are ONE directory under item 2. Do NOT touch
scripts/run_night.py or joulewise/arm_readiness.py (seat 4 owns them right now).
Acceptance (rc-gated; named modules ONLY, never discover/shard): tests.test_night_gate tests.test_docs_freshness; git
diff --check; no commit; header < 8192 bytes; report per finding.
