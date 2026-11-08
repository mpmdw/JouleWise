# Harvest-off Sol handoff — 2026-11-08

Branch: `align/2026-11-08-harvest-off-sol` (the supplied new task branch), base
`05b6d04cb`. Local commits only; no push. Code commit: `95e5ec8b7` —
`Speed up harvest parsing and hashing; add verified raw transport`.
This is the independent Sol build for the later Sol/Opus agreement.

## Result and important limits

[Design and native handoff](../align/v4/HARVEST-OFF-sol.md) and
[synthetic profile receipts](../align/v4/HARVEST-OFF-sol-profile.json).

- Implemented bounded parallel archive hashing, scoped parsed-record reuse,
  stage-level B6 CLI profiling, and non-destructive, deduplicated streaming raw
  compression/restoration against an external finalized manifest.
- A complete constructed-window harvest compares all 177 output files byte for
  byte after compression/restoration, with the same canonical namespace and
  explicitly frozen emission/program seams. Serial/uncached and parallel/reuse
  paths agree without normalization. Raw custody digests agree as well.
- Both 18.6 and 26.4 decimal GB I/O workloads, with 89% XML-shaped bytes,
  processed every byte and passed equality. Resident size was bounded to 128 MiB
  stripes because the filesystem had about 23 GB free. These were not complete
  valid-plist windows or native hardware validation.
- The thermal-only desk cannot produce final harvest exclusions. R12's existing
  final-eligibility gate prevents putting the entire harvest behind the next
  arm. The proposed route waits for critical Air adjudication and overlaps the
  remaining full desk only where B2 permits. No gate was weakened.
- Planning: about 88–100 MBP compute minutes avoided per window if light triage
  and packing fit their allowances. 30–45 minute turnaround is conditional;
  a gate-preserving scenario is 37–89 minutes, with native Air latency unknown.
  Exact assumptions/formulas and mandatory-full-desk cases are in the design.

## Changed files

| File | Change |
|---|---|
| `joulewise/adapters/powermetrics.py` | Context-local one-entry parsed-record reuse; byte/typed-anchor keys, deep-copy isolation, cap and eviction. No active cache in ordinary measurement calls. |
| `joulewise/b5/harvest.py` | Ordered bounded hash workers, fresh integrity passes, assessment cache context, external archive/stage/finish observations, B6 program identity entries. |
| `scripts/harvest_b6_session.py` | `--io-workers`, `--parse-cache-mib`, `--profile`, acceptance/export timings and exit receipt. |
| `joulewise/harvest_profile.py` | Exclusive external JSONL profile writer; parent CPU and inclusive-stage metadata. |
| `joulewise/harvest_transport.py` | Manifest validation, exact directory/file roster, one source read into hash/zstd, content deduplication, verified restore, exclusive destination and fsync. No network or deletion. |
| `scripts/profile_harvest_io.py` | Reproducible bounded-residency size-realistic I/O profile. |
| `scripts/profile_harvest_parse.py` | Repeated parsing/cProfile experiment on the committed seed. |
| `tests/test_harvest_off.py` | Complete harvest/transport equality and error cases, copy mismatch, profile CLI status. |
| `tests/test_harvest_parse_cache.py` | Decode reuse, changed bytes/anchors, caller mutation, cap, exception cleanup and dropped-frame equality. |
| `docs/align/v4/HARVEST-OFF-sol.md`, `HARVEST-OFF-sol-profile.json` | Design, dependency/gate analysis, measurements and native qualification steps. |
| This report | Run evidence and lead-owned follow-up. |

No coordination files, registrations, thresholds, catalog entries, arm machinery,
analysis pipeline or immutable raw evidence were changed. No kernel tasks were
registered. PROJECT_STATUS was not changed: no advisor-visible science state
advanced. No subagents or external consults were used.

## Failing first and verification

Tests use unittest on Python 3.13. Initial harvest-off tests: **5 errors** because
parallel inventory, external stage observer and transport APIs did not exist.
Initial parser-cache tests: **4 errors** because the scoped API did not exist.
The first complete replay failed with HARVEST_FAULT after losing an empty input
directory; preserving directories fixed it. An intermediate test-edit NameError
was corrected. No failure was accepted as a pass.

Final commands (one module per invocation):

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_harvest_parse_cache` | 5 PASS, .090 s on the last completed run |
| `python3.13 -B -m unittest tests.test_powermetrics` | 61 PASS, 35.834 s |
| `python3.13 -B -m unittest tests.align.test_v4_cadence` | 16 PASS, .003 s; B2/full-desk and fixed-eight gates retained |
| `JW_HARVEST_OFF_PROFILE=/private/tmp/harvest-off-sol-equality-verified.json python3.13 -B -m unittest tests.test_harvest_off` | 7 PASS, 74.358 s on the final code |
| `python3.13 -B -m compileall -q joulewise tests scripts/harvest_b6_session.py scripts/profile_harvest_io.py scripts/profile_harvest_parse.py` | PASS |
| `git diff --check` | PASS; repeated before commit |

The full suite was explicitly prohibited and was not run. Total targeted test
runtime, including red attempts and repeated equality checks, stayed below
20 minutes. One initial .027 s parser red run was mistakenly started while the
previous equality invocation was still finishing; all subsequent test modules
were serialized. The eight-worker blinded job was not inspected or manipulated.

Synthetic profiling commands:

```sh
python3.13 -B scripts/profile_harvest_io.py --total-gb 18.6 --output /private/tmp/harvest-off-sol-18.6.json
python3.13 -B scripts/profile_harvest_io.py --total-gb 26.4 --output /private/tmp/harvest-off-sol-26.4.json
python3.13 -B scripts/profile_harvest_parse.py --output /private/tmp/harvest-off-sol-parse.json
```

All passed. At 18.6/26.4 GB, serial archive hash/copy/verify was 55.36/68.19 s,
two-worker was 26.18/38.18 s, tee pack 36.53/46.57 s, and restore/hash/write/verify
83.08/131.00 s. Distinguish these I/O timings from the small complete harvest's
76.25 → 52.66 s stage sums. Three repeated parses: 6.685 → 1.763 s, 225 → 75
XML decodes. No real-window speedup was measured. The sandbox denied `nice(10)`;
the benchmark recorded this and continued with at most two jobs, without an
approval/sandbox bypass. Python temporary scratch was cleaned by its owner.

## Open questions, blockers and next exact step

1. **Agreement/lead adoption:** compare the independent Opus build with this
   design; keep the frozen R12 eligibility/full-desk gates. If the lead wants a
   different eligibility boundary, that requires an explicit prospective ruling.
2. **Production byte equality:** the canonical namespace and record-bound
   deterministic emission/program envelope are designed and simulated, not wired
   into a production receiver. Defaults contain host paths, clocks and boot IDs.
   Error elapsed times/transcripts also need a deterministic policy. Do not
   advertise arbitrary-path or fault-case byte identity based on this witness.
3. **Evidence closure:** export ledger/capture/corpus/registration/pack/fixture
   dependencies and bind the descriptor to the MBP finalize commit. The existing
   eng-desk H1/H2 and M1–M4 findings remain adoption blockers; no dependency may
   fall back to an unrelated Air-local file.
4. **Integration:** adapt the air-offload lane to the compressed manifest/package,
   canonical restore, verified job/eligibility receipts and the shared armed
   lock/lease. Its two-copy retention rule still governs deletion. No SSH,
   provisioning, real copy, receiver deployment or production arming occurred.
5. **Native confirmation:** run the exact non-claim synthetic end-to-end route
   and required smoke/readiness checks in an authorized unarmed gap; measure
   MBP/Air stage times, whole-process RSS, per-file cap hit rate, compression/link
   throughput, thermal recovery and eligibility/full-desk latency. No new MLX code
   was added; actual native MLX/meter/thermal qualification belongs to the lead
   outside this sandbox. Never use Block 5 to qualify the route.

The next exact step is **Sol/Opus agreement plus a lead ruling on the canonical
replay envelope**, followed by receiver/packet integration and the native smoke.
No permission to start a quiet-machine task is implied by this handoff.
