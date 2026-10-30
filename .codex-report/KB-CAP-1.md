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
SPAN=$("$PY" -B -c 'import math; print(math.ceil(3573.6+22*(3*2+4*10+2)+2*1800+900+600+600+60))')
# Supply the actual adapter rating and its nameplate/specification citation.
# Supply a conservative disk forecast for the SPAN at 10 Hz native plist +
# rich telemetry and 50 Hz meter, including calibration/custody and archive
# copies; name its sample-size/volume evidence. No default rating/budget exists.
# ADAPTER_W, ADAPTER_SOURCE, DISK_BYTES and DISK_DERIVATION must be set by lead.
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$CHECKOUT/joulewise/bytes_stream_capture.py" prepare \
  --checkout "$CHECKOUT" --session "$SESSION" --t0 "$T0" \
  --adapter-max-w "$ADAPTER_W" --adapter-source "$ADAPTER_SOURCE" \
  --disk-bytes "$DISK_BYTES" --disk-derivation "$DISK_DERIVATION" \
  --programmed-span-s "$SPAN" \
  --span-derivation 'rule §§1/2:3573.6+22*(3*2+4*10+2); existing chain:2*1800+900+600+600+60; ceil'
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
test ! -e "$ARCHIVE" && cp -a "$SESSION" "$ARCHIVE"
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
5.7e-8 J/GB for energy and 4.5e-9 GB/s for throughput; exact equality is reserved
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
