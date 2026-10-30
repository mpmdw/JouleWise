# Known-bytes non-claim capture

This is a separate checkout and a fresh session, after BYTES collection and
before stage-1 unblinding. It uses no model, measurement checkout, BYTES ledger
or blinding key. The reader and pass-1 arithmetic are unchanged. No hardware is
authorized from an active agent session. The lead admits the reading rule before
this quiet window. Ed's NO overrides. Never reinstall or retry into acceptance.

The graph uses the existing night driver: reservation, pre calibration, one
continuous scan/palindrome capture, post calibration. The driver supervises the
one KM003C stream across the chain and its battery tail. A meter restart makes
DC unavailable, with the files retained, rather than splicing several clock fits.
The bookend captures are instrument checks, separate from the continuous test
capture. The new roots and calibration ledger are fresh and session-local.

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
# BYTES registration §7/R5 disclosure records the Mac's 140 W adapter.
ADAPTER_W=140
ADAPTER_SOURCE='docs/registrations/bytes_pack_v1.md: Battery assist (140 W adapter); R5 disclosure'
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

Harvest follows only archive-relative paths. INPUT.json is create-once. A scan
refusal retains its reason and receipts and runs no measured calls. Partial
calls, missing calibration, missing battery spans and meter restarts remain
reasoned reader outcomes; none triggers a replacement session automatically.
Native idle rows are retained untrimmed; the reader alone applies its τ trim.

Reproduce the synthetic whole chain on a Python 3.13 desk:

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B -m tests.test_bytes_stream_capture --synthetic /tmp/kb-cap-1-archive
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B scripts/bytes_stream_test.py scan /tmp/kb-cap-1-archive/runs_bytes_stream_test/capture/SCAN_RECEIPTS.json
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -B scripts/bytes_stream_test.py read /tmp/kb-cap-1-archive/INPUT.json
```

The synthetic driver uses fake reservation/calibration tools, hardware arm,
monitor, census, free space, network-time setter, lineage and courier. The new
stage fakes only array/clock/capture streams. Real driver supervision, stage
dispatch/rendering, probe, scan, count selection, receipt persistence, raw
parsing, span integration, harvest, and reader run. The fake calibration tools
write authenticated synthetic fiducial raw plists, events and instrument evidence;
the real own-capture refit and evaluator compute the timing bound, then the real
anchor envelope runs. All four classes decide from computed bounds. A second test
retains the round-1 missing-fiducial path and requires reasoned UNDETERMINED
results. An independent integration checks one call's rails/meter energies and
meter/battery edge terms at 5.7e-6 J/GB times its payload GB (the watt comparison
uses that joule bar divided by call duration). This is synthetic integration
evidence, not hardware validation or calibration evidence.
