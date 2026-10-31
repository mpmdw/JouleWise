# KB-CAP-1

## 1. Design before implementation

Authority: magistrate activation 4e748ac1, 2026-10-30. M0: no active stop card;
explicit bounded user direction selects this AGENT task over the generated queue.
The exhaustive write scope supersedes kernel/run-state bookkeeping. No hardware,
MLX import, BYTES data, ledger or blinding keys will be used on this seat.

Vehicle: the existing HAZARD_PACK night driver, installer, hazard arm, agent census,
network-time OFF, instrument checks and meter supervision. A new
`joulewise/bytes_stream_capture.py` stage uses
`PowermetricsTelemetryAdapter.start_sampling/stop_sampling_with_evidence`, never a
second capture launcher. The graph is reservation, pre calibration,
`bytes_stream_capture`, post calibration. The existing calibration tools operate
on a fresh test-only ledger with a genesis pin; no claim ledger is copied. The
bookend calibration captures are additional instrument checks, not a split of
the one continuous test capture. The driver starts the one meter stream; harvest
rejects multiple streams instead of fitting restarts separately.

Before editing existing files, the stage dispatch/registry files in scope are:
`joulewise/b5/chain.py` (tool/kind dispatch, graph validation and renderer);
`configs/gates/hazard_refusals.json` and `tests/hazards/refusal_census.py`
(refusal inventory, if the chain change changes its census);
`tests/test_battery_float_sweep.py` (READERS classification, if new code names a
bound lexeme). The actual refusal inventory is `configs/gates/hazard_refusals.json` (the
initial scout spelling above was corrected before any registry edit).
The import-fence lists are inspected, and extended only if the new
entry requires it. No estimator, calibration implementation, reader or registered
BYTES config is edited. A separate prepare writer in the new stage module avoids
changing the claim-only assumptions of `joulewise/b5/plan.py`.

Planned artifacts: `configs/campaigns/bytes_stream_test/` owns the fixed non-claim
plan tree, generator, telemetry-only config, README and genesis pin;
`scripts/bytes_stream_harvest.py` produces INPUT.json from an immutable archive;
`tests/test_bytes_stream_capture.py` and `tests/test_bytes_stream_harvest.py`
exercise the new paths. The existing probe is imported without changing its
scan/read functions. Its stream-only allocation/fill block normalizes MLX
RuntimeError to MemoryError so the scan can preserve an allocation stop.
The refusal registry will also inventory the new stage and its probe dependency;
this does not change the probe reader. No import-fence or READERS addition is
needed: the new modules name no B lexeme and import no retired arm path.

Rule-derived numbers (no new acceptance threshold):
- §1: “run the probe at --bytes 2^k for k = 14 to 35 ... three calls per size,
  repeats chosen so each call lasts about 2 s”. Preserve planning pilots and the
  three scan calls separately; stop on allocation failure, never retry acceptance.
- §1: “N = floor(T_call / t_dispatch)”, S “2 × 500 s”, cache arms “2 × 250 s”.
- §2: “--idle-s 57.6” and “Settle gap 3 s”; these are passed literally to stream.
- §1: planned measured time is 3573.6 s (2500 + 16×57.6 + 24×3 + 8×10).
  Scan planning is 22×3×2 s plus measured planning/allocation overhead. Runtime
  allowances must record their terms, including the existing calibration-tool
  allowances, rather than introduce a hidden timeout.

Decisions I made: retain the existing bookend calibration lifecycle; use fresh
non-claim roots named runs_bytes_stream_test and runs_bytes_stream_test_bound;
keep the continuous scan capture but never use its energy to select sizes/counts;
retain native idle rows without trimming; retain missing prerequisites as null
with archive diagnostics so the unchanged reader gives a reasoned result.
The reader owns every classification and any τ-based idle trimming.

## 2. Producer and field sources

The producer is `scripts/bytes_stream_harvest.py`. It follows archive-relative
paths, records source SHA-256 values, writes create-once INPUT.json, and never
opens a live ledger. The reader is unchanged. The only probe edit is in stream's
allocation/fill block; scan/read and all reader functions retain their base bytes.

| Input field | Source function / archive record |
|---|---|
| `scan` | `bytes_stream_capture.run_stage` → unchanged `bytes_stream_test.knee_scan`; SCAN_RECEIPTS.json and SCAN.json |
| eight `receipt` objects | unchanged probe `stream`, in stamped palindrome order; calls/*.json |
| `energy_j.rails`, `.gpu` | `native_trace` reparses original plist with adapter's recorded current-era anchor; `rail_energy` calls unchanged `reduce._integrate` on native interval support and RAW receipt spans |
| `energy_j.meter`, `.battery` | unchanged `km003c_parse.integrate`; battery powers from unchanged `Stream.battery_watts` / `bytes_analysis._battery_stream_data` |
| `idle.pre/post` | complete intersecting native rails/GPU intervals and native meter/battery points in the RAW spans; no trimming/resampling; uncovered meter/rail idle support is unavailable |
| `anchor_shift_j` | unchanged `reduce._anchor_shift_envelope`; maximum of the rails/GPU envelopes because the reader contract provides one scalar used by both |
| `operative_timing_bound_s` | `b6.calibration.read_own_capture` refits the archive's pre/post captures; unchanged `calibration.evaluate` evaluates them using SESSION.json's copied calibration registration |
| `r_max_s` | the one `km003c_parse.clock_fit`'s min/max excess-latency statistics, exactly as pass-1 `bytes_analysis.meter_decode` |
| `tau_s` | unchanged `bytes_analysis._battery_delay_ns` (all polls, including incomplete SMC reads) |
| `meter_edge_w` | `meter_fields` adapts `meter_decode`'s adjacent-sample and ±r_max selection to RAW receipt edges; powers are existing fitted-stream samples |
| `battery_edge_j` | `meter_fields` adapts `meter_decode`'s `(T/n) sum(abs(P_b))` edge-window prescription; n comes from unchanged `integrate`; incomplete tail remains unavailable |
| `capture_stack` | adapter `device_metadata` archived in capture_stop.json: telemetry and rail_manifest |
| `battery_samples` | unchanged `Stream.battery_watts`, retained at native poll stamps over the call envelope |
| `adapter_max_w`, `adapter_source` | lead's explicit sourced nameplate/specification inputs, archived in SESSION.json |
| `battery_source` | named KM003C poll SMC B0AC/B0AV source and `Stream.battery_watts` |
| `meter_gaps` | exact missing device-counter stamps at the recorded sample step, mapped with the single clock fit and counted per RAW stream/pre/post span |
| optional `gpu_state` | unchanged adapter `decode_rich_telemetry` from the original plist, where GPU state exists |
| optional `thermal_spans` | archive custody/hazards/monitor/thermal.jsonl, joined on recorded RAW finished stamps |
| optional `hour_as_run_s` | STAGE.json's measured-session start/end RAW stamps, including allocation/warm-up; reader separately reports the stamped idle envelope |

`meter_decode` itself is not called for a gap-bearing test call: it correctly
rejects those claim spans. Its edge prescription is adapted here while the
integrators stay unchanged; the reader applies this test's registered gap charge.
These receipts are already RAW, so the pass-1 monotonic-to-RAW offset is never
added a second time. Poll order is checked before the governed parser's sort.
Multiple meter streams are retained but never spliced or independently refitted.

Additional decisions I made: require exact-payload scan triplets before planning
repeats; preserve a specific incomplete reason if B was not allocatable; normalize
MLX allocation RuntimeError in the probe; preserve capture teardown on driver
SIGTERM; leave missing prerequisites null rather than substitute a bound. No new
acceptance bar, data selection rule, estimator or NEEDS_RULING was introduced.

## 3. Lead's exact Mac lifecycle

Run in this order on the Mac (absolute paths avoid changing directories):

```sh
CHECKOUT=/Users/edr/code/bytes-stream-test
SESSION=/Users/edr/night-bytes-stream-test/attempt-1
ARCHIVE=/Users/edr/night-archive/bytes-stream-test/attempt-1
OUT=/Users/edr/night-bytes-stream-test/attempt-1-INPUT.json
git clone --branch codex/2026-10-30-kb-capture --single-branch https://github.com/mpmdw/JouleWise.git "$CHECKOUT"
python3.13 -m venv "$CHECKOUT/.venv"
PYTHONDONTWRITEBYTECODE=1 "$CHECKOUT/.venv/bin/python" -B -m pip install -c "$CHECKOUT/env/mac-measurement-lock.txt" -e "$CHECKOUT[mac]"
PY="$CHECKOUT/.venv/bin/python"
# Existing H preparation lead is 420 s, above the installer's 300 s minimum.
T0=$("$PY" -B -c 'import time,math; print(60*math.ceil((time.time()+420)/60))')
# Rule §1/§2: 3573.6 measured seconds; 22*(3*2+4*10+2) scan planning
# (three 2 s calls, four 10 s preparations including the pilot, pilot ~2 s).
# Existing chain wall allowances: two calibration captures 2*1800, reservation
# 900, calibration-verdict 600, terminal session-status 600, pre settle 60.
# Four budgeted stages each add chain.BUDGET_GRACE_S=30; post capture is
# unbudgeted (its retained 1800 s allowance has no SIGKILL grace).
SPAN=$("$PY" -B -c 'import math; print(math.ceil(3573.6+22*(3*2+4*10+2)+2*1800+900+600+600+4*30+60))')
# Supply record: docs/phase_2/window_c_operator_checklist.md:32,
# 140 W Anker, 28 V × 4.99 A negotiated. The lead must record the actual
# nameplate or t0 power-path negotiation record in --adapter-source.
ADAPTER_W=140
: "${ADAPTER_SOURCE:?Set ADAPTER_SOURCE to the Anker nameplate or t0 power-path negotiation record}"
# Existing measured byte rate, applied to the entire span, with the recorded
# two-copy factor and fixed retained bytes (no new reserve or acceptance bar).
DISK_BYTES=$("$PY" -B -c 'import json,math,sys; from fractions import Fraction; d=json.load(open(sys.argv[1]))["packs"]["bytes-s1-p1"]["disk_derivation"]; r=d["stream_rate_bytes_per_s"]; print(d["peak_copies"]*math.ceil(Fraction(r["numerator"],r["denominator"])*int(sys.argv[2]))+d["fixed_retained_bytes"])' "$CHECKOUT/configs/b6/registration/sizing_b5.json" "$SPAN")
DISK_DERIVATION="configs/b6/registration/sizing_b5.json /packs/bytes-s1-p1/disk_derivation: 2*ceil((4502241280000000000000/1799796660838183 bytes/s)*${SPAN} s)+4046531103 fixed retained bytes; full span includes calibration/custody; two copies include archive; no reserve"
printf '%s\n' "--disk-bytes $DISK_BYTES" "--disk-derivation $DISK_DERIVATION" "--adapter-max-w $ADAPTER_W" "--adapter-source $ADAPTER_SOURCE"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$CHECKOUT/joulewise/bytes_stream_capture.py" prepare \
  --checkout "$CHECKOUT" --session "$SESSION" --t0 "$T0" \
  --adapter-max-w "$ADAPTER_W" --adapter-source "$ADAPTER_SOURCE" \
  --disk-bytes "$DISK_BYTES" --disk-derivation "$DISK_DERIVATION" \
  --programmed-span-s "$SPAN" \
  --span-derivation 'rule §§1/2:3573.6+22*(3*2+4*10+2); existing chain:2*1800+900+600+600+4*30+60; ceil'
```

The prepare tool prints the exact head, plan hash, t0, maximum duration and
roots that the lead must include in Ed's notice, plus non-claim status, what
runs, the instruction to exit agents, and Ed's veto. **The tool sends nothing.**
The lead sends and checks that notice, checks the existing keep-awake assertion,
and installs only if Ed has not vetoed. If notice handling consumes the install
lead, preserve the attempt and prepare a fresh session/t0 before installing.

```sh
/bin/zsh "$CHECKOUT/scripts/install_night_agent.sh" --plan "$SESSION/night_plan.json" \
  --python "$PY" --courier-bin "$CHECKOUT/scripts/b6_courier.sh" --launchctl-bin /bin/launchctl
# Exit all agent sessions. Wait for the terminal record; do not collect from a bridge.
# After returning at the desk, require the existing terminal record:
test -f "$SESSION/custody/night/result.json"
# Copy the whole session once; preserve raw bytes and all unsuccessful stages.
mkdir -p "${ARCHIVE%/*}"
if test -e "$ARCHIVE" || test -L "$ARCHIVE"; then
  printf 'Archive target already exists: %s\n' "$ARCHIVE" >&2
  exit 1
fi
cp -a "$SESSION" "$ARCHIVE" || exit 1
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$CHECKOUT/scripts/bytes_stream_harvest.py" --archive "$ARCHIVE" --out "$OUT"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$CHECKOUT/scripts/bytes_stream_test.py" scan "$ARCHIVE/runs_bytes_stream_test/capture/SCAN_RECEIPTS.json"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$CHECKOUT/scripts/bytes_stream_test.py" read "$OUT"
/bin/zsh "$CHECKOUT/scripts/install_night_agent.sh" --plan "$SESSION/night_plan.json" \
  --uninstall --launchctl-bin /bin/launchctl
```


## 4. Executed synthetic evidence and checks

Every test and synthetic command used Python 3.13.5 with
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`. No MLX, hardware, real
measurement data or blinding key was used. The cloud-environment runtime skill
was used to check seat readiness and networking. No notice or external message
was sent; the draft PR is https://github.com/mpmdw/JouleWise/pull/613.

Standalone commands, with outputs retained on this seat:

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m tests.test_bytes_stream_capture --synthetic /tmp/kb-cap-1-archive
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B scripts/bytes_stream_harvest.py --archive /tmp/kb-cap-1-archive --out /tmp/kb-cap-1-INPUT.json
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B scripts/bytes_stream_test.py scan /tmp/kb-cap-1-archive/runs_bytes_stream_test/capture/SCAN_RECEIPTS.json > /tmp/kb-cap-1-SCAN.json
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B scripts/bytes_stream_test.py read /tmp/kb-cap-1-INPUT.json > /tmp/kb-cap-1-READ.json
```

Output tails / extracted reader result:

```text
{"stage":"completed","records":8,"scan":"knee found"}
{"records":8,"scan":"knee found","diagnostics":[]}
K=16777216; B=4294967296
rails UNDETERMINED: records[0].harvest.anchor_shift_j missing or invalid (anchor shift bound missing)
gpu UNDETERMINED: records[0].harvest.anchor_shift_j missing or invalid (anchor shift bound missing)
dc RESOLVED
rest UNDETERMINED: records[0].harvest.anchor_shift_j missing or invalid (anchor shift bound missing)
meter streams/fits: 1; first-call stream gap: 2 missing samples
battery sample range: 0..3 W
first pre-idle native rows: meter 2880, battery 192, rails 577, GPU 577
```

This runs the real driver, rendered four-stage chain, new stage, probe, scan,
count selection, receipt persistence, raw parsers, harvest and unchanged reader.
Hardware seams use a fake array module, RAW clock, 10 Hz native NUL-plist capture,
50 Hz meter counter with 300 ms polling, exact counter gaps, a 3 W battery-assist
interval and a 7 s RAW/monotonic offset. Fake arm/census/network-time/lineage/
monitor/courier and reservation/calibration tools are disclosed in the test.
Real driver meter supervision runs. Fake calibration tools deliberately supply
no authenticated fiducial evidence; the real calibration evaluator retains that
missing prerequisite. Therefore DC resolves and the other boundaries give the
reasoned missing-anchor outcome above. This is not live validation.

Focused final command:

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m unittest tests.test_bytes_stream_capture tests.test_bytes_stream_harvest tests.hazards.test_refusal_allowlist tests.test_battery_float_sweep
```

```text
Ran 39 tests in 46.540s
OK (skipped=1)
```

The two existing import-fence modules passed 9 tests. The refusal census has
zero unlisted, stale, miscounted, changed-guard or scope-gap entries. Generator
`--check` and `git diff --check` passed. No READERS edit was necessary: the new
modules name no battery-float B lexeme. The stage/probe joined
`configs/gates/hazard_refusals.json`; the census implementation was unchanged.

The broader touched-chain run included `tests.test_b5_chain`,
`tests.test_b5_chain_prune2`, `tests.b6.test_b6_plan_render` and both registries:
102 tests, 2 failures, 1 error, 1 skip. The two failures are the existing
BudgetHelperTests expecting “survivors none” after process-tree termination;
this Linux seat still reported a PID. The budget helper is byte-identical to
base aa101880c (SHA-256 e0650088cfeb6aa1fe563a580f7d84f72479def09c7cb1f4c53181878b23944d).
The error is the existing production-plan test invoking absent
`/opt/homebrew/bin/python3.13`. Those tests and the helper were not edited.

The requested `tests.test_bytes_stream_test` module was launched in full; its
exhaustive real-CLI leaf-fault case is still running at this report snapshot.
The canonical `python3.13 -B -m unittest discover -s tests` was also launched and
is still running with failures already reported. Neither is claimed green.
Logs: /tmp/kb-cap-focused.log, /tmp/kb-cap-suite.log, /tmp/kb-cap-chain.log.

No two independent programs' printed numerical columns were compared. Exact
float assertions replay identical governed functions on identical inputs. Any
future cross-program comparison must use 1% of the smallest printed uncertainty:
5.7e-6 J/GB for energy and 4.5e-7 GB/s for throughput; exact equality is reserved
for integers, hashes and identical code on identical inputs.

## 5. Git and CI handoff

Design was committed/pushed first (7cf81c66c), followed by capture/harvest
(75383a8a1), integration fixes (e7768c7d8), and final support/prerequisite
regressions (2b6de5327). The requested base was fetched and merged repeatedly;
its latest remote head remained aa101880c and Git reported “Already up to date.”
No registered BYTES file or pinned estimator/calibration file was modified.

The PR remains draft, titled “CI only: KB-CAP-1”, into codex/2026-10-28-kb-v2.
CI must be read again on the report commit; the final message reports every job
state on that final head. The prior implementation-head observation had build,
fences, changes, quick, installed-wheel and both crash-matrix shards successful;
calibration-exits-exclusive and all twelve ordinary shards were still running;
gate-ledger was skipped. This is not an all-green claim.

## Round 2

Authority: magistrate activation 4e748ac1, 2026-10-30, rulings Y1–Y5.
Continued `codex/2026-10-30-kb-capture` at `7978d95e9`. Fetched and merged
KB-v2 first: remote head `aa101880c` (the round-9 reader fix) was already an
ancestor, so Git reported “Already up to date.” No merge commit was needed.
The cloud-environment runtime skill was used for readiness/network inspection.
No hardware, MLX, measurement data, live ledger, blinding key or notice was used.

Decisions I made:

- Use the existing self-consistent synthetic fiducial generator with the current
  protocol. The fake pre/post calibration tools copy its raw plist, events and
  instrument evidence to the rendered output paths. Harvest calls the real
  `b6.calibration.read_own_capture` and `calibration.evaluate`; neither they nor
  the anchor-envelope function or reader is mocked or modified. Reservation,
  ledger-verdict/status and the other hardware seams remain synthetic.
- Keep a second full driver-chain test with absent authenticated fiducials;
  require reasoned UNDETERMINED rails/GPU/rest and an absent operative bound.
- Independently integrate the first call's native raw plist support and selected
  raw meter samples. Recompute meter edge maxima and battery edge charges from
  decoded raw streams, including independent residual/tau arithmetic. Add a
  synthetic 300 ms battery-assist interval at the end edge so its charge is
  nonzero. These synthetic inputs change no data-selection or acceptance rule.
- Use the recorded 140 W Mac adapter rating in
  `docs/phase_2/window_c_operator_checklist.md:32` (140 W Anker,
  28 V × 4.99 A negotiated); the lead records the nameplate or t0 negotiation
  in `--adapter-source`.
  The README and exact lead commands cite this source.
- Derive disk bytes from `configs/b6/registration/sizing_b5.json`,
  `/packs/bytes-s1-p1/disk_derivation`: rate
  `4502241280000000000000/1799796660838183` bytes/s, recorded two-copy factor,
  and `4046531103` fixed retained bytes. For the rule-derived 10390 s span:
  `2*ceil(rate*10390)+4046531103 = 56028277617` bytes. The full span includes
  calibration/custody, and two copies include the archive. Print the exact
  `--disk-derivation` alongside `--disk-bytes`; add no new reserve.
- Correct the round-1 agreement bars to **5.7e-6 J/GB** and **4.5e-7 GB/s**,
  1% of 0.00057 J/GB and 0.000045 GB/s. The independent energy assertions use
  `5.7e-6 * payload_GB` joules, stated beside the assertions. The power check
  uses this joule bar divided by call duration. Exact equality is used for the
  integer missing-sample count only in this independent check.

No NEEDS_RULING: no choice changes which real data count or a printed number.
The reader, production estimator/calibration code, safety switches and
PROVISIONAL/non-claim status are preserved. The initial ambiguous push was
remote-rejected; automatic review rejected a retry because it lacked an explicit
refspec. A verified checkout and explicit feature-branch refspec resolved that
safely; no unintended remote branch changed.

Executed evidence (Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`,
`PYTHONDONTWRITEBYTECODE=1`, `-B`):

- `python3.13 -B -m unittest tests.test_bytes_stream_test`, alone in the
  background and awaited: **49 tests, 894.616 s, OK**, including 1140 generated
  real-CLI leaf faults. Log: `/tmp/kb-r2-reader.log`.
- `python3.13 -B -m unittest tests.test_bytes_stream_capture tests.test_bytes_stream_harvest`:
  **12 tests, 64.267 s, OK**. Log: `/tmp/kb-r2-new-pass.log`.
  Earlier runs exposed and fixed two fixture/check errors: B5 harness attempt
  names differed from production's pre/post names, and the independent check
  initially treated whole-second XML plist dates as precise interval endpoints.
  The final check uses the recorded first endpoint and raw integer elapsed_ns.
- Refusal/numeric-source registries: **28 tests, 28.359 s, OK (skipped=1)**.
  Generator `--check` and `git diff --check` pass. No production code changed;
  the complete reader module, both new modules and registries are the targeted
  verification for this test/documentation round; no new full-suite claim.
- Standalone whole chain retained at `/tmp/kb-r2-final-archive`, followed by the
  real harvest, scan and read CLIs, all exit 0. Outputs:
  `/tmp/kb-r2-INPUT.json`, `/tmp/kb-r2-SCAN.json`, `/tmp/kb-r2-READ.json`;
  log `/tmp/kb-r2-standalone.log`. Eight records, knee found, diagnostics empty.

Computed pre/post bounds are both `0.02161027162932592` s; the operative bound
is `0.03242827162932592` s. First-call anchor shift is
`0.21931140436936403` J. The real evaluator retains its synthetic
outside-acceptance-range flags for pre/post and unsized-stop disclosure;
`excluding` is empty. No bound is supplied by a mock or missing prerequisite.

The reader's complete printed contrast/share strings are:

```text
rails RESOLVED: 7.000 ± 0.014 J/GB
gpu RESOLVED: 7.000 ± 0.014 J/GB
dc RESOLVED: 14.08 ± 0.10 J/GB
rest RESOLVED: 7.077 ± 0.094 J/GB
share: 0.4973 ± 0.0046
claim_lines: {}
```

All four classes are RESOLVED from computed bounds. In the second full-chain
missing-fiducial test, DC is RESOLVED; rails/GPU/rest remain UNDETERMINED with
`records[0].harvest.anchor_shift_j missing or invalid (anchor shift bound missing)`.
Its complete claim lines are:

```text
Known-bytes check: rails memory-traffic attribution is undetermined (records[0].harvest.anchor_shift_j missing or invalid (anchor shift bound missing)).
Known-bytes check: rest memory-traffic attribution is undetermined (records[0].harvest.anchor_shift_j missing or invalid (anchor shift bound missing)).
```

Independent first-call arithmetic passes at
`5.7e-6 J/GB * 4883.377815552 GB = 0.0278352535486464 J`:
rails `41118.841893636556` J, meter `82186.9261043605` J,
meter edges `[164.47323999999998, 82.88824]` W,
battery edges `[0.0, 0.9003743820000001]` J. The W comparison uses
`0.0278352535486464 / T_call` W. Producer rails/meter values are
`41118.84189363655` J and `82186.92610436048` J; both edge arrays agree
within their dimensional bars. The missing-stream-sample count is exactly 2.

Git steps: prerequisite merge was a no-op; sourced lead inputs/agreement bars
committed and pushed as `929746200`; passing authenticated synthetic and
independent arithmetic tests as `c454c446f`; this section is the final report
commit. All pushes use the explicit authorized feature-branch refspec. PR #613
remains draft. CI is read again after the final report push and every job state
is listed separately in the final response. The API hostname is blocked on this
seat; the public GitHub checks page supplies that final-head observation.
Pending or skipped jobs are not an all-green result.

## Round 3

Authority: magistrate activation 4e748ac1, 2026-10-30, rulings Z1–Z8.
Continued `codex/2026-10-30-kb-capture` from `c2b850860`; first merged
`codex/2026-10-28-kb-v2` at `a3226e87f` and pushed merge `5680e5e09`.
The reading rule is admitted. Round-1 WRITE_SCOPE, numbers rule and safety
switches remain in force. Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`,
`PYTHONDONTWRITEBYTECODE=1`, `-B`; no hardware, MLX, real measurement data,
live ledger, blinding key or notice was used. The cloud-environment runtime
skill was used for readiness and network inspection.

Decisions I made:

- Z1: the continuous capture's planned length is
  `3573.6 + 22*(3*2 + 4*10 + 2) = 4629.6 s`. Derive it beside
  `CAPTURE_PLANNED_S` from the call lengths, idles, settles and preparation/pilot
  allowances of rule §§1/2. Use it for both clock-span fields; retain the
  existing clock formula, 3.7 ms allowance, 0.25 ppm margin and 5 ms limit.
- Z2: malformed/non-object JSON or invalid receipt spans leave null affected
  records/fields and reasoned diagnostics, with INPUT.json still written.
  Reject non-finite JSON fields before serialization. A malformed thermal line
  makes the thermal field null. Missing scan status cannot crash the summary.
- Z3: resolve each input before opening it, including every file handed to the
  governed calibration/native parsers. Diagnose and skip outside targets before
  parsing or hashing; retain support for archive-internal links. Audit direct
  file links, directory links and chained directory links through the real CLI.
- Z4: include STAGE status/error/allocation_stop in provenance diagnostics and
  the CLI summary, including a completed status. Diagnose absent calibration
  captures/plists. Read capture-stop device metadata independently so a failed
  native trace retains its capture_stack.
- Z5: cite `docs/phase_2/window_c_operator_checklist.md:32`: 140 W Anker,
  28 V × 4.99 A negotiated. The lifecycle requires the lead to set
  ADAPTER_SOURCE to the actual nameplate or t0 power-path negotiation record,
  passed as `--adapter-source`; it supplies no placeholder evidence.
- Z6: the rendered graph has four budgeted stages: reservation, pre capture,
  window calibration verdict and terminal session-status. Add their four
  `BUDGET_GRACE_S = 30` allowances. Post capture is explicitly unbudgeted;
  retain its existing 1800 s planning allowance without a SIGKILL grace.
  `SPAN = ceil(4629.6 + 2*1800 + 900 + 600 + 600 + 4*30 + 60) = 10510 s`.
  The unchanged sourced disk formula gives `56628644275` bytes; existing
  minute rounding with the 3300 s t0-stage cap gives `window_max_s = 13860`.
- Z7/Z8: bootstrap the stage's checkout root on sys.path for path execution;
  mark sampling started only after start_sampling returns. Existing --out is
  preserved with one stderr line and exit 2, including the create-once race
  catcher. The README's archive-copy block exits loudly on an existing target
  or copy failure. Opus 9's conservative battery tail and Fable 7's planning
  allowances are unchanged.

Z1 clock replay — NEEDS_RULING:

The existing exact `measured_rate_bound` gives
`H = (5 - 3.7)*1000/4629.6 - 0.25 = 0.03080179713150164 ppm`.
Searched the committed tree, including fixtures and session records, for clock
rates and arm/precheck receipts. Three earlier arm records contain explicit
measured rates; no additional committed machine-readable arm/precheck rate
receipt was found. Replay uses the recorded decimal, without inferring extra
precision. The files below are under `docs/process_traces/2026-10-block5/`.

| Arm record | Recorded rate | New bound | Refused | Subsequent session record |
|---|---|---|---|---|
| `seal2-beta-a5-arm.md:13` | 2.718 ppm | 17.4406528 ms > 5 ms | yes | No sleep; not claim-usable because calibration acceptance was stale |
| `seal2-beta-a6-arm.md:15` | 2.718 ppm | 17.4406528 ms > 5 ms | yes | `seal2-beta-a6-window.md`: claim-usable, no sleep |
| `seal2-gamma-a1-arm.md:19` | 2.718 ppm | 17.4406528 ms > 5 ms | yes | `seal2-gamma-a1-window.md`: claim-usable, no sleep |

Thus it would refuse **2 of 2 known-good claim-usable sessions with recorded
arm rates**, and all 3 recorded arm sessions (including the physically clean
but calibration-stale BETA 5). Replay evidence: `/tmp/kbr3-clock-replay.json`;
tracked-record search: `/tmp/kbr3-all-clock-records.txt`.
Question: retain this strict derived hold, or authorize a prospective change
to the clock rule? Recommendation: leave the ruled implementation intact until
the magistrate adjudicates this replay. No loosening was made; live release
under this gate remains unresolved. No other NEEDS_RULING was introduced.

Executed verification:

- Read both entire cold-pass reports and their repro scripts from JouleWise-data
  `e7acfcd2f` and `acc3337ff`. Reran Opus's indep/worlds/refusals/alloc_stop/
  opens_audit and Fable's recompute_input/meter_worlds/refusal_replays/
  scan_stop_archive before and after the harvest fixes, both allocation ceilings
  31 and 20. Refusal replays use the same immutable synthetic baseline archive.
  The last Opus gap case was resumed from its verbatim script stanza after
  stopping the sequential launcher also stopped that child. All resulting
  harvest/read cases end reasoned; output overwrite is refused.
  Both audit scripts report no outside reads. Opus W8 retains the expressly
  unchanged conservative incomplete-tail departure; Fable's five worlds pass.
- The initial 13 CLI regressions against the unfixed harvester produced
  12 failures and 1 error, reproducing the cold-pass defects. Final
  `tests.test_bytes_stream_capture tests.test_bytes_stream_harvest`:
  **30 tests, 96.737 s, OK**. This includes 16 archive/lifecycle CLI cases and
  subprocess checks of start failure and path execution. The strengthened
  path-prepare refusal check was also rerun separately: **1 test, OK**.
- `tests.test_b5_chain` plus both registries: **53 tests, 69.375 s, OK
  (skipped=1)**. Final refusal/numeric-source registry rerun: **28 tests,
  52.532 s, OK (skipped=1)**. Generator `--check` and `git diff --check` pass.
  These are the requested targeted checks; no new canonical full-suite claim.
- Whole-chain synthetic before and after, followed by the real harvest, scan
  and read CLIs: all exit 0, eight calls, knee found, all four classes RESOLVED.
  New archive: `/tmp/kbr3-after`; CLI products: `/tmp/kbr3-after-INPUT.json`,
  `/tmp/kbr3-after-SCAN.json`, `/tmp/kbr3-after-READ.json`. Reharvested INPUT
  equals the whole-chain INPUT. The complete reader printed dictionary equals
  the baseline's, including these unchanged round-2 lines:

```text
rails RESOLVED: 7.000 ± 0.014 J/GB
gpu RESOLVED: 7.000 ± 0.014 J/GB
dc RESOLVED: 14.08 ± 0.10 J/GB
rest RESOLVED: 7.077 ± 0.094 J/GB
share: 0.4973 ± 0.0046
claim_lines: {}
```

Both independent recomputes also pass on the new whole-chain archive:
Opus calls 0/3/7 `FAILS []`; Fable all eight calls `FAILS: none`, worst
energy-like difference `5.631760099755328e-06` of the allowed bar. Comparisons
use the existing `5.7e-6 J/GB * payload_GB` bar and its dimensional derivatives.
Logs are `/tmp/kbr3-opus-{before,after}-*.log`,
`/tmp/kbr3-fable-baseline-*.log`, `/tmp/kbr3-fable-after-*.log`,
`/tmp/kbr3-new-modules.log` and `/tmp/kbr3-chain-registries.log`.
The native_trace, rail_energy, points and meter_fields function sources are
byte-identical to `c2b850860`; reader, estimator and calibration code are unchanged.

Git steps were committed and pushed separately: prerequisite merge `5680e5e09`,
capture/lifecycle `0167af075`, harvest/CLI regressions `184dac954`, then this
Round 3 report. Explicit feature-branch refspecs were used. PR #613 remains
draft and CI-only. Final-report-head CI is read after its push and every job's
observed state is listed separately in the final response; pending/skipped jobs
are not an all-green result.
