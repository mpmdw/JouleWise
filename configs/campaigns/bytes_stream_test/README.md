# Known-bytes non-claim capture

This is a separate checkout and a fresh session, after BYTES collection and
before stage-1 unblinding. It uses no model, measurement checkout, BYTES ledger
or blinding key. The matched reader uses v3 receipts and R−C at one payload. Pass-1 boundary integrators, idle estimators and systematic rows are unchanged. No hardware is
authorized from an active agent session. The lead admits the reading rule before
this quiet window. Ed's NO overrides. Never reinstall or retry into acceptance.

The graph uses the existing night driver: reservation, pre calibration, one
residency check followed by one continuous palindrome capture, post calibration. The driver supervises the
one KM003C stream across the chain and its battery tail. A meter restart makes
DC unavailable, with the files retained, rather than splicing several clock fits.
The check allocates one 32 GiB ring (64 × the admitted 512 MiB capacity envelope), reshapes it through the eight G/2^k rungs (G=2^26 B, k=0..7), and stops at the first resolved C/R timing contrast. It uses no energy capture. The palindrome is R,C,C,R at that payload. The bookend captures are instrument checks, separate from the continuous test capture. The new roots and calibration ledger are fresh and session-local.

Run in this order on the Mac (absolute paths avoid changing directories):

```sh
CHECKOUT=/Users/edr/code/bytes-stream-test
SESSION=/Users/edr/night-bytes-stream-test/attempt-1
ARCHIVE=/Users/edr/night-archive/bytes-stream-test/attempt-1
OUT=/Users/edr/night-bytes-stream-test/attempt-1-INPUT.json
: "${ADMITTED_HEAD:?Set ADMITTED_HEAD to the lead-admitted matched-rule implementation commit}"
git clone https://github.com/mpmdw/JouleWise.git "$CHECKOUT"
git -C "$CHECKOUT" checkout --detach "$ADMITTED_HEAD"
python3.13 -m venv "$CHECKOUT/.venv"
PYTHONDONTWRITEBYTECODE=1 "$CHECKOUT/.venv/bin/python" -B -m pip install -c "$CHECKOUT/env/mac-measurement-lock.txt" -e "$CHECKOUT[mac]"
PY="$CHECKOUT/.venv/bin/python"
# Existing H preparation lead is 420 s, above the installer's 300 s minimum.
T0=$("$PY" -B -c 'import time,math; print(60*math.ceil((time.time()+420)/60))')
# Rule §§1/2: 4*759.2 streams + 8*57.6 idles + 12*3 gaps + 4*10
# preparation/exit = 3573.6 s. Rule §1 R5: all eight check rungs ~270 s
# plus one ~10 s ring allocation/fill = 280 s; stage planning = 3853.6 s.
# Existing chain: two 1800 s calibrations, 900 s reservation, 600 s verdict,
# 600 s status, four 30 s budget graces, 60 s pre-settle. Ceil = 9734 s.
# Read generated planning instead of maintaining a second arithmetic path.
SPAN=$("$PY" -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["planning"]["programmed_span_s"])' "$CHECKOUT/configs/campaigns/bytes_stream_test/collection_plan.json")
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
  --span-derivation 'rule §§1/2:3573.6 + §1 R5:270+10; existing chain:2*1800+900+600+600+4*30+60; ceil = 9734 s'
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
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$CHECKOUT/scripts/bytes_stream_test.py" check "$ARCHIVE/runs_bytes_stream_test/capture/CHECK_RECEIPTS.json"
PYTHONDONTWRITEBYTECODE=1 "$PY" -B "$CHECKOUT/scripts/bytes_stream_test.py" read "$OUT"
/bin/zsh "$CHECKOUT/scripts/install_night_agent.sh" --plan "$SESSION/night_plan.json" \
  --uninstall --launchctl-bin /bin/launchctl
```

Harvest follows only archive-relative paths. INPUT.json is create-once. A residency-check
refusal retains its reason and receipts and runs no measured calls. Partial
calls, missing calibration, missing battery spans and meter restarts remain
reasoned reader outcomes; none triggers a replacement session automatically.
Native idle rows are retained untrimmed; the reader alone applies its τ trim.

Reproduce the synthetic whole chain with Python 3.13. Use a fresh destination
for each run; the driver preserves create-once receipts and outputs.

```sh
# Resolve scratch to /private/var/... rather than the /var alias. This is desk
# synthetic work; no Metal or physical capture is invoked.
KB_SCRATCH=$(mktemp -d "${TMPDIR%/}/kb-matched.XXXXXX")
KB_SCRATCH=$(cd "$KB_SCRATCH" && pwd -P)
export TMPDIR="$KB_SCRATCH" JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1
PY=/opt/homebrew/bin/python3.13
"$PY" -B -m tests.test_bytes_stream_capture --synthetic "$KB_SCRATCH/resolved"
"$PY" -B scripts/bytes_stream_test.py check "$KB_SCRATCH/resolved/runs_bytes_stream_test/capture/CHECK_RECEIPTS.json"
"$PY" -B scripts/bytes_stream_test.py read "$KB_SCRATCH/resolved/INPUT.json"
"$PY" -B -m tests.test_bytes_stream_capture --synthetic --unresolved "$KB_SCRATCH/unresolved"
"$PY" -B scripts/bytes_stream_test.py check "$KB_SCRATCH/unresolved/runs_bytes_stream_test/capture/CHECK_RECEIPTS.json"
"$PY" -B scripts/bytes_stream_test.py read "$KB_SCRATCH/unresolved/INPUT.json"
"$PY" -B -m tests.test_bytes_stream_test --worked-example
"$PY" -B -m tests.test_bytes_stream_test --replay-archive /Users/edr/night-archive/seats-c7fea69e/kb-knee-council/diag-matched/run-1
```

`CHECK_RECEIPTS.json` includes each mode's one-sweep pilot and three timing
receipts, in rung/C/R order. `CHECK.json` retains comparisons and the specific
reason on refusal. `INPUT.json` uses `check` and four `records`; only v3 measured
receipts are integrated. The reader recomputes successful check evidence and
geometry, so saved derived timings or κ cannot override the receipts. A failed
check yields no measured calls and every class UNDETERMINED with its reason.

The synthetic driver fakes reservation/calibration tools, hardware arm, monitor,
agent census, free space, network-time setter, lineage and courier. The stage
fakes array/clock/capture streams. Real driver supervision, four-stage dispatch,
probe, residency selection, repeat planning, durable receipts, raw parsing,
integration, harvest and reader execute. Row views share storage, each MLX axis
is limited to signed 32-bit, and synthetic repeat/rotate have distinct per-byte
times. `--unresolved` gives them the same time and exercises all eight rungs.
Fake calibration tools write authenticated fiducial raw plists, events and
instrument evidence; the real refit/evaluator and anchor envelope compute bounds.
The missing-fiducial test keeps reasoned UNDETERMINED outcomes.

On a sandbox that cannot query process groups, the real driver can refuse after
the chain exits 0 (`night_chain_alive`, exit 6). The fixture prints and preserves
that environmental refusal, then harvests the completed synthetic stage; it never
changes the driver verdict to GO. It kills all journaled groups and waits for its
tracked children without relying on the unavailable census. This is synthetic
integration evidence, not hardware verification.

The independent raw integration derives its bar from this run: 1% of its smallest
H2-printed half-width in J/GB, times the call's logical GB for an energy comparison
(or divided by duration for power), checked above 10^6 times propagated binary64
noise. The worked example uses 3.1e-6 J/GB = 1% of its smallest displayed width,
0.00031 J/GB. The archive replay uses the R3/R4 functions and NOTES' supplied clock;
it discloses the historical 8 GiB ring and absent v3 fields. It does not admit
those legacy summaries as v3 measurements.

Planning is in generated `collection_plan.json`: the stage is 3853.6 s as derived
above, the full programmed span is 9734 s, and disk is 52,746,273,217 bytes =
2 × ceil((4502241280000000000000 / 1799796660838183 B/s) × 9734 s) + 4,046,531,103
fixed bytes. The rate, two-copy factor (including archive), and fixed bytes come
from `configs/b6/registration/sizing_b5.json`,
`/packs/bytes-s1-p1/disk_derivation`, as in the preceding kit. These are planning
inputs, with no added reserve or acceptance bar. The ring is resident memory,
not an extra 32 GiB on disk. The rule's allocation/view-building allowance remains
unverified on hardware; the actual stamped spans supply the reader arithmetic.
