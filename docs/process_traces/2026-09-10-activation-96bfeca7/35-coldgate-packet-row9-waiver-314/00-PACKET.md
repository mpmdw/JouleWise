# Cold-gate packet 35 — row-9 waiver for PR #314 (GATE-SENSIBILITY-SWEEP-01): merge with one known local-only replay failure?

Mechanically assembled by the resident magistrate (activation 96bfeca7) at 2026-09-10 ~07:40 PDT. Trigger: the twelve-row
gate (D-118/D-121) row 9 requires "lead unpiped full-suite replay on the integration tree, exact tail recorded". The replay at
the PR's final head `beb808bc` (Exhibit A) ran 5668 tests with exactly ONE failure, `tests.test_controller.HappyPathTests::
test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce`, process rc 1. Precedent: PR #309 merged under a NAMED
row-9 waiver adjudicated by cold gates 44/56 with refuter 57 (Exhibit G lists the files on this checkout under
`docs/process_traces/2026-09-09-rehearsal-harvest/`; read 44 and 56 for the shape of that waiver and its conditions).

## Evidence

- Exhibit A: replay tail and command (single process, alone, 1 h 39 min; the four-shard script was not used).
- Exhibit B/C: root cause (Astra high, `verdict.cause: probable`) and the lead note — the controller test fixture sleeps
  through its post-idle capture against a real deadline (the sleeping-sentinel class cured for the campaign-test helper in
  PR #310, consult 87); on a loaded host the capture times out, the drift is unknown, salvaged samples remain, and strict
  validation derives a bounded drift the producer did not record. The same test FAILS on a clean main checkout (078a13a4)
  on this host (run at 05:05 PDT by the lead; 73 tests, failures=1, the same two strict reasons) and was reproduced by an
  implementation seat with all changed modules restored to HEAD bytes. Disproved alternatives in Exhibit B: epoch/ULP
  dependence, Python 3.14 numerics, host identity facts, changed fixture bytes.
- Exhibit D/E/F: the PR body and CI — 18 checks pass at `beb808bc` (only `gate-ledger` fails, awaiting the ledger in the PR
  body); main CI at `078a13a4` success.
- The PR's diff touches `joulewise/environment_admission.py`, `controller.py` (cooldown_gate only), `load_transition_alignment.py`,
  `scripts/generate_g2a_probe_inputs.py`, tests and two contract docs; `reduce.py` byte-identical to main (D-138). The failing
  test exercises the powermetrics retry/promotion path in `controller.py`, not `cooldown_gate`; the seat-08 replay of the same
  test with the four production modules restored to HEAD reproduced the failure.
- Cure lane registered: FIXTURE-SENTINEL-CONTROLLER-01 (kernel branch `bookkeeping/2026-09-10-kernel-lanes`).

## Question

Q1. May PR #314 merge under a named row-9 waiver for this one failure? Options: (a) YES, waiver named in the ledger row 9
evidence and the terminal review, conditions: the failure is pre-existing on main on this host, CI green on both heads, root
cause recorded, cure lane registered, and the failing test's path is disjoint from the PR's code changes; (b) NO — the lead
must first run the four-shard replay (`python3 scripts/shard_tests.py --workers 4`, ~44 min) and merge only if that passes,
or land FIXTURE-SENTINEL-CONTROLLER-01 first; (c) YES with an additional condition you name (e.g. a targeted re-run of the
failing test under the shard runner, or a `--no-sleep` replay of that one module). Give the ruling with the reasoning sized to
what row 9 guards (a branch regression hidden by a stale or partial run) and to the cost (the sweep is a p1 gate before any
G2-a number is consumed; the first real window is planned for 09-12 02:56).

Q2. State the exact sentence for ledger row 9's evidence and for the terminal review's row-9 line.

Ruling file: `10-coldgate-fable-ruling.md` here, with an Executed probes section (you may run the single failing test and
`git diff 078a13a4..beb808bc --stat` on this checkout — refs are shared; do NOT check out; no git writes).
