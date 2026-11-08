# Harvest off the MBP — independent Sol build

2026-11-08. **PROVISIONAL: synthetic engineering and a proposed handoff, not an
installed arm route or native performance qualification.** Branch
`align/2026-11-08-harvest-off-sol`, based on `05b6d04cb` from
`origin/align/2026-11-08-v4-r11`. No sealed outcomes or real measurement paths
were opened. No network, model download, analysis pipeline, measurement, or
full suite was run. Coordination state is lead-owned and unchanged.

## Decision in one paragraph

Move the raw evidence and the expensive computation to the Air. Keep terminal
closure, finalize/record commit, a short triage, compression/transport under the
cool-down lease, and quiet-start/pre-arm work on the MBP. **Do not mark final
member eligibility from a thermal-only report.** Under the current R12 list,
the Air's final eligibility result must return before every next arm. The
remaining full desk may overlap that arm except after W1 or a code/config
change. Moving *all* harvest computation behind the next arm while retaining
this final-eligibility gate is not possible with the current dependency graph.
The 30–45 minute target is conditional on finishing the critical Air work
inside cool-down; it is not established by this build.

This is Sol's independent design. An independent Opus build, agreement and lead
ruling are still required by RUN_STATE 220/221 before operational adoption.

## Authority and inspected inputs

- `origin/main:RUN_STATE.md` items 213–221: back-to-back cadence, R12 B2,
  fixed eight calibration windows (217 supersedes the count stop), paired
  builds, and next-two-step readiness/native smoke.
- `origin/perf/2026-11-08-opus-review-desk` at `60dbf213d`: H1, H2 and M1–M4
  in `docs/perf/2026-11-08-opus-review-desk.md`.
- `origin/perf/2026-11-08-eng-desk` at `2fd82914c`: stage parallelism is useful;
  its replay skips harvest and is not a full-desk gate.
- `origin/ops/2026-11-08-air-offload` at `daecbbc28`: reuse its shared lock,
  cool-down lease, authenticated receiver, explicit roots and two-copy retention
  protocol. It is itself PROVISIONAL and has no compressed raw handoff.
- Local `v4_cadence.py`, `align_v4_session.py`, `thermal_desk.py`,
  `v4_registration.py`, B5 harvest, B6 acceptance/export, compression/restore,
  agent playbook M0, orchestration and decision-log authority. Raw immutability,
  provenance and physics/evidence gates remain binding (D-002/D-025/D-161).

## What actually consumes harvest time

The entry is `scripts/harvest_b6_session.py`: resolve registered inputs →
`harvest(..., prepare_desk=True)` → B6 acceptance/survivor screen → export.
Inside harvest, the verdict writer can overlap early assessment; archive,
joins, identity checks and final exclusions follow. Existing `--workers`
already parallelizes member assessment; B6's default is one. It does not
parallelize every subsequent check or the verdict child.

| Stage | Reads/work | MBP dependency after terminal closure? |
|---|---|---|
| Finalize and record | Terminal result, courier/empty-process proof, complete raw manifest, record commit/push | Yes: establishes source provenance and that writers stopped. Hash bytes while copying/packing only if the lead's finalized-manifest contract permits it; do not call a self-authored Air manifest a source proof. |
| Archive copy | APFS `cp -c -pR`, ordinary byte copy fallback | No. APFS clone is cheap only within the same filesystem; transport is a real byte transfer. |
| Hashes | Entire source before copy; entire archive after copy; entire source again at finish | No. All three passes have different integrity jobs. This build preserves them. |
| Assessment/reduction | Strict validation, re-reduction, anchor reconstruction, battery/identity checks; repeated XML parsing | No, given complete verified bundles and calibration dependencies. It reads recorded hardware evidence; it does not need live Metal or powermetrics. |
| Calibration, NEG-8, joins | Ledger prefix/head, historical captures, corpus, references, monitor/meter and collector journals, original executed inventory/lineage | No. Every transitive evidence dependency must be copied; missing original paths cannot silently fall back to an Air-local file. |
| Exclusions | Entire final flag set + sealed catalog + roster/spans; then acceptance/survivor rules | No hardware dependency. Depends on the preceding checks, including final source-unchanged check. |
| Archive/report write | Exclusive files, fsyncs, digests, reductions, flags, roster, receipts, acceptance and CSV | No. Keep single-writer publication and deterministic roster/reduction order. |
| Compression | Separate `desk_compress.compress`: source hash, zstd source read, decompressed verification read, journal then unlink | No. **There is no call to this compressor in the inspected B6 harvest CLI or its export.** Comments about compression are not timing evidence that it ran. Transport compression below is non-destructive and separate. |

The reported 88–109 minute B6/BYTES harvest and 98–103 minute desk are historical
evidence supplied by the brief/review, not observations of this session. Those
ranges overlap and must not be added. No real-window per-stage split is known.

### Synthetic profiles

Receipts are in [HARVEST-OFF-sol-profile.json](HARVEST-OFF-sol-profile.json).
The full equality witness uses the existing constructed six-member window,
real validators/reducers/exclusions, and fixed process/provenance seams. With
parser reuse disabled and serial hashes, the measured stage sum was 76.25 s;
with scoped reuse and two hash threads it was 52.66 s (1.45×). Member assessment
was 72.34 → 50.64 s; archive 1.11 → 0.59 s. These are an earlier successful
profile, ordered serial first; load/cache were uncontrolled. G3 is skipped and
the fixture already has its verdict. This does not profile a live verdict child,
B6 acceptance/export, a full ALIGN desk, or native memory pressure.

A cProfile experiment parses the 5,783,144-byte committed seed three times.
Original: 6.685 s and 225 XML decodes; scoped reuse: 1.763 s and 75 decodes,
identical records. XML document parsing accounted for 6.648 of the original
6.677 parser seconds. This identifies avoidable decoding; it does not establish
that the whole 88–109 minutes scales by 3.8×.

The I/O experiment processes **every byte** of 18.6 and 26.4 decimal GB, with
89% XML-shaped plist bytes and 11% pseudorandom other bytes. Only 128 MiB is
resident per stripe; each stripe is archived, rehashed, packed and restored
before its synthetic scratch is removed. About 23 GB free at intake made a
resident 26.4 GB source plus archives inappropriate. This is a size-realistic
I/O workload, **not** a full-window valid plist/reduction run. XML is low entropy;
warm cache, stripe count and compression ratio differ from native records.
The four PM files in a stripe also share content (apart from possible one-byte
length differences), favoring content deduplication. Do not extrapolate that
deduplication rate to distinct native member captures.

| I/O stage, accumulated seconds | 18.6 GB | 26.4 GB |
|---|---:|---:|
| Generate synthetic bytes | 34.44 | 48.02 |
| Serial source hash + clone/copy + archive hash | 55.36 | 68.19 |
| Two-thread source hash + clone/copy + archive hash | 26.18 | 38.18 |
| Final independent source rehash, two threads | 7.77 | 11.35 |
| Tee hash + zstd packing, two jobs | 36.53 | 46.57 |
| Decompress + hash + write + verify | 83.08 | 131.00 |

The 18.6 GB run produced 2.047 GB of payload; this ratio is synthetic and must
not size a live transfer budget. Archive SHA256SUMS and restored raw digests
matched for every stripe. The sandbox refused `nice(10)`; the benchmark recorded
that fact and kept at most two hashing/compression jobs, one zstd thread each.

## Implemented speedups and their limits

1. `tree_inventory(..., workers=N)` hashes independently in at most eight
   threads, with at most `2*N` reads pending. Results/errors stay in path order.
   `archive_sources` and final source verification use `Seams.io_workers`;
   default remains one. No stat-only or cross-inventory cache can hide a change.
2. `reuse_parsed_records` is a context-local, one-entry parsed-record cache for
   one assessment. Keys include SHA-256 of the **actual bytes**, length and both
   typed anchor options. Returned nested records are deep copies. Exceptions
   are not cached; context resets on exit; a different input evicts the entry.
   Ordinary capture/parser calls have no active cache. Harvest tasks use a
   128 MiB raw-size cap; larger files bypass reuse. Raw size is not a Python
   heap bound. No native benefit is promised if most files exceed the cap.
3. `harvest_transport.pack_raw` tees a single source read into hashing and
   fixed-one-thread zstd. Exact duplicate contents are compressed once but
   **every source file is independently hashed**. It checks the complete file
   and directory roster and source stability. It never removes originals.
   `unpack_raw` decompresses/hashes every restored file against the separately
   finalized manifest before publishing. Empty directories are preserved: an
   initial synthetic replay failed when an empty bound-runs root disappeared.
4. `--profile NEW.jsonl` on the B6 CLI records archive source-hash/copy/copy-hash,
   harvest stages, finish (exclusions/output writes), acceptance, export and exit
   code. Nested archive/total rows are inclusive: do not sum all rows. CPU is
   parent-process CPU, not worker/child CPU. Timings remain outside custody.

There is no result cache across windows, estimator rewrite, changed exclusion
catalog, asynchronous floating-point reduction, source deletion, deployment,
or modification of the existing destructive desk compressor in this build.

## M1: exactly what a lighter desk must compute

**A standalone desk can be the U1–U3 producer, but only with equivalent inputs
and rules. It cannot by itself certify `member_eligibility`.** The present
standalone CLI also exits zero for an inconclusive report: exit zero is not a
triage pass. Read the statuses and bind them to the record.

For every roster member, derive tags from the frozen pack/collection plan using
`build_roster`, including target-precheck paths (closes review H1). Carry window,
stage, gating status, repeat groups, comparison references, ordinal and role.
Authenticate registration, U3 bar, WP19/R1 policy, fixtures and prior-session
inputs. No hand-written target map, truncated roster, or absent journal may
become an empty successful check.

- **U1:** registered-span OS observation/nominal status; turn-owned OS and PM
  nominal state; collector-loss/unobserved/custody flags; X1–X4 counts; thermal
  coverage at least .99 and maximum intervals at most 2 s; PM support gaps at
  most `max(1 s, 5*period)`; G0 timeouts at most one; G1/H timeout ratio at most
  .02 of observed turn admissions. Preserve inconclusive when observations are
  absent. Use the current `acceptance` function rather than a parallel rule set.
- **U2:** included members' G0 slow-sensor range (at most 3 C) and authenticated
  G0/G1/H release-journal predicates under the frozen policy. Current live
  temperature alone cannot establish the previous window's U2.
- **U3/X5:** full required pair roster, actual prompt/output token IDs per turn,
  owned-energy attribution and uncertainty/coverage validity, mean pair energy,
  delta energy and the **registered** `u3_margin`, plus decode activity-weighted
  clocks (aggregate relative difference at most .005; retain per-turn diagnostics).
  Token divergence is X5 exclusion; missing energy/tokens/pairs is inconclusive.
  Never substitute the unregistered legacy `3*max(...)` fallback for a pending bar.

Thus U3 is not an OS-temperature scan: it depends on the energy trace and exact
tokens. Reuse extraction or authenticated derived evidence where equivalent,
but do not promise a sub-minute desk by omitting it. The current standalone
report also needs the same harvest-exclusion join as `powermode_desk_check`;
its current `calibration_exclusions` alone omits those exclusions. Its optional
journals/registered spans must be supplied from the complete record, not omitted
to obtain a local fallback.

Final eligibility additionally needs the complete harvest catalog application,
strict/member/code/model/pack identities, calibration/NEG-8, monitor joins,
capture faults, X5/U3 pair membership, cohort identity/pool restrictions and B6
acceptance projection where applicable. An identical-copy digest is not a
substitute for these adjudications. Final counts enter fixed-eight B3 only after
this join. `thermal_escalation`, `member_eligibility`, `cohort_pool_rules` and
`sentinel_roster` cannot be marked deferred. U4/U5 inconclusive still changes
the next roster; include the existing sentinel decision evidence too.

## Proposed per-window handoff

1. **MBP terminal/finalize.** Prove terminal result, chain closure, courier,
   watchdog empty-process latch; reconcile all armed plans. Freeze raw files and
   the transitive evidence closure. Finalize a complete files+directories manifest
   and descriptor on the MBP, bind session/plan IDs to terminal result, commit
   record metadata and push through the existing authorized records route.
   This session only commits engineering code locally; it performs no such push.
2. **MBP light triage.** Produce authenticated terminal/capture summaries, meter
   sample/clock coverage, thermal U1–U3 projection if it is demonstrably cheap,
   and explicit pending fields. This can identify a required escalation early.
   It cannot assert final member eligibility while harvest is pending. Prefer
   extracting thermal evidence on the Air if the MBP projection costs material
   heat/time. Never execute an agent or full desk during the next capture.
3. **Compressed raw offload during cool-down.** Under the air-offload lane's
   persistent shared lock and expiring lease, pack the exact closed evidence
   set, then send the package via that lane. Commit/bind the raw manifest digest
   separately from the package's self-contained copy. Include the pin/ledger
   prefix, all calibration/corpus dependencies, custody journals, meter streams,
   executed inventory, pack, registration, fixtures and exact code commit; do not
   transfer weights or an MBP venv. Re-hash/verify at the receiver; retain MBP
   originals until two independently verified remote copies satisfy that lane.
4. **Air critical work.** Restore raw into a new writable working copy; keep
   the verified raw package immutable. Run harvest with two member processes and
   two hash threads initially; run the equivalent U1–U3/eligibility join. Publish
   a receipt only after final exclusions and source-unchanged checks. The Air
   job's stdout/stderr, exit, archive digests and complete thermal verdicts are
   bound to the exact record commit, descriptor and raw-manifest digests.
5. **Gate next arm.** Wait for the receipt; packet builder checks artifacts,
   not a nonempty `basis` string. After W1 or any code/config change, require
   successful harvest **and** full desk PASS before arming (B2). A missing,
   partial, unavailable-registration or HARVEST_FAULT receipt cannot pass. Read
   final eligibility before B3 counts; fixed eight still applies. Apply any
   registered thermal escalation as a new frozen configuration, never in place.
6. **Overlap only permitted remaining work.** After the gate, Air full-desk
   arithmetic/reporting can continue during the next MBP window. All MBP packing,
   transfer, receipt polling and cleanup must have ended and children been reaped
   before a fresh full display/quiet dwell and pre-arm checks. If critical Air
   work misses cool-down, wait; do not quietly waive final eligibility.

### Byte identity is a contract, not automatic relocation

Raw custody byte identity is directly proved by pack/unpack and archive tests.
Complete harvest identity is also proved by a constructed-window test comparing
all **177 files**, including SHA256SUMS, derived/withheld files and harvest.json,
without scrubbing any bytes: original source → compressed verified raw copy →
second harvest with parser reuse/two hash threads.

That test explicitly freezes the emission/program context and restores into the
**same canonical absolute namespace**. It is a two-host simulation, not a native
MBP/Air test. This qualification is essential: today's production harvest embeds
absolute input/archive/catalog paths, emitting host boot ID, wall/monotonic clock,
checkout root/status and occasionally error elapsed times/transcripts. Default
invocations on arbitrary Air paths cannot be byte-identical.

Before deployment, the lead must install a canonical replay namespace and a
record-bound deterministic emission/program envelope. The same pinned harvester
must run in that namespace on either host. Preserve the original captured boot,
clock and executed-code evidence; keep actual processing-host/elapsed attestation
in a separate engineering receipt. The envelope must not pretend an Air process
was on the MBP. Existing `Seams` support the synthetic witness, but this build
**does not expose a production envelope/relocation adapter**. Recover all original
absolute dependency locators within the verified namespace; do not rewrite source
JSON, omit unreadable captures, or allow live-host fallback. Fault diagnostics
also need deterministic representation or a separate attestation before claiming
byte identity for fault cases. Different zstd versions may produce different
compressed frames; raw digests must remain identical regardless.

The existing eng-desk replay and offload client are not merged here. Their H1,
H2, M1–M4 fixes, manifest/envelope binding, receiver integration, global armed
lock and process guard remain explicit landing work. In particular, an Air
`--no-harvest` replay cannot serve as this receipt.

## Expected savings and native confirmation

Separate **MBP busy minutes** from **time until next arm**. Moving a 98–103 minute
desk and adding roughly 2–6 minutes of light triage plus 1–4 minutes packing
would avoid **about 88–100 MBP compute minutes/window**; these added times are
planning allowances, not observations. Moving only the old replay saves the
review's 10–15 minutes. Finalize, transport and physical cool-down still exist.

Conservative scheduling model, measured from terminal completion:

`turnaround = F + L + C + X + max(Q, E) + P`

Here F is finalize/record work, L local triage, C packing, X transfer plus receive
verification, Q remaining physical recovery after MBP work, E Air final
eligibility/thermal latency after receiving the record, P pre-arm plus fresh
dwell. This model does not credit heat-producing work as free cool-down. Use
`E + remaining_full_desk` at W1/code-change barriers.

- If local close/pack/transfer fits 10–15 minutes, recovery is 15–25 minutes,
  pre-arm/dwell is about 5 minutes and E finishes inside recovery: **30–45 min**.
- Planning envelope F=3–8, L=2–6, C=1–4, X=1–3, Q=15–25, P=5–8 and E=25–60
  minutes gives **37–89 min**. This retains the actual gates. A further 4–10
  minute full-desk remainder gives roughly **41–99 min** at the mandatory B2
  barriers. E is unknown; a serial Air harvest could be slower than this range.
- A historical all-MBP 98–103 minute desk plus F/Q/P in those ranges gives
  about 121–144 minutes, so that planning envelope suggests **32–107 minutes
  of turnaround saved**. This is a scenario calculation, not a forecast bound.
- At the programmed D span of 40,527 s, 30–45 minute gaps imply about
  11.76–12.01 h cycles (2.00–2.04/day); 37–89 minute gaps imply 11.87–12.74 h
  cycles (1.88–2.02/day), before schedule conflicts/refusals.

Transfer-only compressed-size sensitivity, for 18.6–26.4 GB raw (decimal MB/s):

| Raw:compressed ratio | 50 MB/s | 100 MB/s |
|---|---:|---:|
| 1:1 | 6.20–8.80 min | 3.10–4.40 min |
| 3:1 | 2.07–2.93 min | 1.03–1.47 min |
| 10:1 | .62–.88 min | .31–.44 min |

Packing, fsync, authenticated receive/restore, backup and hashing are additional.
Offload improves cadence only if all MBP traffic ends before dwell/measurement.

**Next exact step:** compare this build with the independent Opus design; rule
on the canonical envelope and critical eligibility split, then integrate into a
single reviewed candidate. In an unarmed gap, with no agent load for any quiet
measurement, the lead must run a non-claim native smoke using tiny synthetic
members through exact arm → terminal/finalize → compressed offload → Air harvest
→ thermal/final eligibility → packet → next arm, with missing/corrupt-file and
worker-failure injections. Respect RUN_STATE 221's next-two-step readiness.

Then profile an explicitly authorized **unblinded, non-B5** closed record on
both hosts: stage wall/CPU, aggregate worker RSS, per-file size/cache hit rate,
disk bytes, zstd ratio/version, APFS-vs-cross-volume copy, network throughput,
receive verification, terminal-to-record latency, final-eligibility latency,
time to physically quiet and fresh dwell. Compare complete bytes/refusals and
all 14 triage checks for worker counts 1/2, including required-full-desk cases.
No newly added MLX code requires a sandbox exception; native MLX/meter/thermal
and hardware timing remain lead-run qualification outside this sandbox.
