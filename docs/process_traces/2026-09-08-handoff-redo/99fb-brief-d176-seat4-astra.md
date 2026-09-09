WRITE_SCOPE: ["scripts/run_night.py","joulewise/t0_rehearsal.py","tests/test_run_night.py","tests/test_t0_rehearsal.py","tests/test_launch_window.py","docs/contracts/pack_night_go_receipt.md"]

# D-176 seat 4 — rehearsal purpose / G7 producer and acceptance (gpt-6-astra, HIGH, genre implementation)
Base: int/2026-09-08-d176-seats-2-3 at 4d72e524 (seats 2+3 integrated; end-to-end fixture at tests/test_launch_window.py
~:2031). Contract: docs/contracts/pack_night_go_receipt.md — §7.1 row "4 — rehearsal purpose/G7 producer and acceptance"
is your seat (WRITE_SCOPE, seams: scripts/run_night.py ~:61–64 and the GO-production region for the real
production-launcher G7 presentation writing the exact `night/g7_refusal.json` with custody-wide consumption /
`chain.started` absence; joulewise/t0_rehearsal.py ~:38,49,88–95 existing rehearsal schema/class, ~:48,86–87,710–738
G5 schema/key sets and C1–C5 recomputation, ~:790–793 G7 artifact acceptance; clauses B4/S1/S4/N1); §§4, 6, 10–10.3 govern
semantics. ALSO read the second cold gate's synthesis at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99ey-coldgate-packet-d176-second-gate/13-magistrate-synthesis.md: item 8 defines the minimal live rehearsal your
producer must support (rehearsal-class pack night on a `JouleWise-rehearsal-<date>-<sha>` clone, un-inventoried,
window id prefixed `rehearsal-t0-unattended-`, custody `~/night-custody/<window_id>`; after the night, present the
rehearsal GO to a production-plan launcher and record the class refusal as G7); a PARALLEL seat is curing the census
(synthesis items 1–6: no CLONE_DERIVED roots, launcher identity, reviewed rehearsal-clone prefix, inventory pin to
plan.repo_head) in joulewise/arm_readiness.py and joulewise/night_gate.py — do NOT edit those files; call the predicate
as the contract names it and pin your calls in tests that tolerate that landing.
Deliver: the `purpose=T0_REHEARSAL` GO production path (prefixed id + disjoint roots accepted; the 2×2 purpose/id table
of §10 S4 enforced at production); G5 evaluating `joulewise.pack_night_go_receipt.v1` and recomputing C1–C5 (the
D-149 schema retired and REFUSED, never grandfathered); the G7 producer: present the rehearsal-class GO to the
production launcher path and write `night/g7_refusal.json` recording the class refusal, asserting custody-wide absence
of any consumption record and of `chain.started`; G7 acceptance in t0_rehearsal (~:790–793); the four-case
purpose/root regressions through the seat-3 consumer; contract §9 rows for B4/S1/S4/N1 pinned to biting tests; §7.1
seat-4 row updated with what you touched.
NEEDS_RULING early return on any ambiguity; baseline anchors (BASELINE_MANIFEST/DIGEST) are superseded for this
runner-owned lane. Acceptance (rc-gated to a log; named modules ONLY, NEVER discover/shard — the lead owns the full
replay; end your turn after the named acceptance): tests.test_run_night tests.test_t0_rehearsal tests.test_launch_window
tests.test_night_gate tests.test_docs_freshness; git diff --check; no commit; header < 8192 bytes; report = per-clause map.
