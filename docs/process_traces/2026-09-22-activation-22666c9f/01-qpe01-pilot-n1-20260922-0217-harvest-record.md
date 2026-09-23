# Record 01 — pilot night `qpe01-pilot-n1-20260922-0217`: harvest, uninstall, diagnosis and ruling (activation 22666c9f, 2026-09-22 04:57–05:30 PDT)

Terms used in this record: an *envelope* is one 600 s idle capture; its
*interior* is the 480 s slice measured from 60 s after the envelope's
scheduled start; a *clock anchor* is the derived mapping from the power
sampler's own timestamps onto the host wall clock, and it is *bounded* when
the deriver can prove that mapping lies inside a stated interval; an envelope
is *retained* when its anchor is bounded and its interior has complete native
sample support; the *wall clock* is the host's settable calendar time and the
*monotonic clock* is the host's unsettable elapsed-time counter.

## §1 Launch

Watchdog attempt 73 spawned activation `22666c9f-8699-4558-a535-2427853f56e4`
at 04:57:00 PDT after the plan span closed (predecessor dc2237d5 armed the
night at 02:03 and exited before REQUEST 02:09; the watchdog FENCED through the
span, HOLD_CENSUS 02:21:21–04:36:55 on the night's own driver, then LAUNCHING
at 04:57 when the census emptied). Heartbeat written first (pid 12258). Launch
email Gmail `1a0c8fb597b5f78e` to the single address, carrying the one queued
notice (`transition-306-hold_census`, expected: the driver's own processes);
`notice.ack` written. No directive issue open; no stand-down request.

## §2 Verdict (executed evidence, read at the bench 04:58 PDT from the custody root)

Custody root
`/Users/edr/night-custody/qpe01-pilot-n1-20260922-0217-20260922-0217-1790068620-d45378c6010b538ca1bb74ae0f2222dceb4df1e4`
(`night_plan.json` v2, `measurement_head` = `repo_head` = `d45378c6`,
`window_max_s` 9000, t0 1790068620 = 02:17:00 PDT).

- `night.log`: 02:17:00.60 driver started; gate verdict GO; chain digest
  verified; **04:27:11.85 result verdict=GO**; 04:28:36 and 04:32:34 "durable
  record failed" (the results push, §5); 04:31:21 courier attempt=1 sent=True.
- `night/chain.started` 02:17:00.67 (pid 98681); `night/chain.exited`
  04:27:10.96 **exit_code 0**; `chain.stderr.log` EMPTY; `chain.stdout.log`:
  600 s settle, twelve `envelope_start`/`envelope_end` pairs each `rc=0
  cleanup_proven=True`, `evidence_end outcome=complete cleanup_proven=True`.
- `night/result.json`: verdict GO, `aborted_reason` null, no refusal
  documents, receipt class `DIAGNOSTIC_NO_PACK`; `night/receipt.json` (02:17)
  C1 PASS, C2 NOT_APPLICABLE, C3 PASS, C4 PASS, C5 PASS. `launchd.night.err`
  EMPTY; `launchd.night.out` = the courier's closing summary.
- `night/evidence_outcome.json`: outcome `complete`, `envelopes_attempted 12`,
  `cleanup_proven true`, error null. `evidence_cleanup.json`: recorder group
  98772 absent, residue empty, no signal errors, budget 30 s.
- Courier: Gmail `1a0c8e258b89b05f` sent 04:31 (`courier.sent`: pid 11817,
  epoch 1790076681); the courier's reading of the summary and of the push
  failure matches this record.
- `night/evidence/summary.json`: **status INCONCLUSIVE, retained 2 of 12**
  (envelopes 2 and 12: 154.88 J and 151.03 J over their 480 s interiors),
  `retained_pairs 0`, `pair_sd_j` null ("fewer than four retained disjoint
  pairs or eight retained envelopes; no top-up"), `block_two_stop.outcome`
  **"no cutoff qualifies"** (cause `observer_floor_above_smallest_holdable_share`),
  `cutoff_authority false`. Diagnostics only: unfiltered single-envelope SD
  1.454 J (five envelopes with a joule value: 154.88, 152.15, 151.86, 152.81,
  151.03), overlapping adjacent-pair SD 1.058 J (deltas −0.28 J, −1.78 J),
  first-to-last retained drift −3.86 J. Busy cores p50 0.24, p90 0.32, max
  0.74 (covariate only). All twelve envelopes passed census, AC and thermal
  probes; 260 driver censuses, zero hits.

Per-envelope disposition (from each `envelope-NN/session.json`, fields
`interior.status`, `interior.reason`, `interior.native_samples`,
`power.anchor.status`, `power.anchor.detail`, `start_drift_s`):

| env | wall span (PDT) | anchor | detail | interior | native samples | start drift s |
|---|---|---|---|---|---|---|
| 01 | 02:27:01–02:37:01 | unknown | wall_minus_monotonic_span_exceeded (8.04 ms) | partial, clock anchor unresolved | 0 | 0.32 |
| 02 | 02:37:08–02:47:01 | bounded (0.42 ms span, 1.12 ms bound) | — | complete | 2056 | 8.01 |
| 03 | 02:47:11–02:57:00 | unknown | affine_clock_fit_empty (4.44 ms change) | partial, clock anchor unresolved | 0 | 10.23 |
| 04 | 02:57:08–03:07:01 | unknown | affine_clock_fit_empty (1.33 ms change) | partial, clock anchor unresolved | 0 | 7.81 |
| 05 | 03:07:08–03:17:01 | bounded (1.19 / 2.98 ms) | — | partial, incomplete interior support | 2038 | 7.89 |
| 06 | 03:17:11–03:27:01 | bounded (1.15 / 2.16 ms) | — | partial, incomplete interior support | 2038 | 10.18 |
| 07 | 03:27:10–03:37:00 | unknown | wall_minus_monotonic_span_exceeded (22.36 ms) | partial, clock anchor unresolved | 0 | 9.53 |
| 08 | 03:37:08–03:47:00 | unknown | effective_clock_anchor_bound_exceeded (4.54 ms span, 5.08 ms bound) | partial, clock anchor unresolved | 0 | 7.75 |
| 09 | 03:47:10–03:57:00 | unknown | effective_clock_anchor_bound_exceeded (4.53 ms span, 5.35 ms bound) | partial, clock anchor unresolved | 0 | 10.06 |
| 10 | 03:57:10–04:07:00 | unknown | wall_minus_monotonic_span_exceeded (+13.05 ms) | partial, clock anchor unresolved | 0 | 9.24 |
| 11 | 04:07:08–04:17:00 | bounded (1.52 / 4.02 ms) | — | partial, incomplete interior support | 2039 | 7.85 |
| 12 | 04:17:10–04:27:00 | bounded (1.51 / 1.94 ms) | — | complete | 2070 | 9.60 |

The three "incomplete interior support" envelopes (5, 6, 11) have full rail
coverage (480.000 s on both rails) but `span_mismatch true`: the native
frames' summed overlap differs from 480 s by more than the 1 µs tolerance,
so the deriver reports them partial although a joule value exists. That is a
second, smaller defect class (§6 finding 3).

## §3 Harvest (record 85 step 5)

`cp -Rp` of the whole night root (including `results-clone/`, 3.4 GB) to
`/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922` at
04:59:28–04:59:35 PDT; `SHA256SUMS` (15,801 files, everything except
`results-clone/.git/`) written from the copy and checked against the LIVE
root: **15801 OK, 0 non-OK** (`SHA256SUMS-check-against-live-root.txt`
beside it). Nothing in the night root was moved, altered or deleted. The root
and the clone
`/Users/edr/JouleWise-measurement-20260922-0217-1790068620-d45378c6…-qpe01-pilot-n1`
(clean at `d45378c6`) are RETAINED: envelopes were captured.

## §4 Uninstall (documented post-completion step)

`python -m joulewise.evidence_night uninstall --candidate
/Users/edr/night-plan-staging/qpe01-pilot-n1-20260922-0217-20260922-0217-1790068620-d45378c6…`
run with the clone's `.venv` from the clone at **04:59:32 PDT: rc 0**
(`lifecycle/uninstall.json`: the clone's `scripts/install_night_agent.sh
--plan <custody>/night_plan.json --uninstall`, exit 0, stdout and stderr
empty). `launchctl list | grep -c joulewise.night` → 0;
`~/Library/LaunchAgents` holds only `com.joulewise.magistrate.plist`. Done 52
minutes before the 05:52 dead-man minute. **NOTHING IS ARMED.**

## §5 Results branch NOT published (executed)

`git ls-remote origin 'refs/heads/night-results/*'` lists thirteen branches;
`night-results/qpe01-pilot-n1-20260922-0217` is absent. In `results-clone`
the commit `08c1cc47` ("record night qpe01-pilot-n1-20260922-0217", 12,155
files, 1,850 MB) exists on that branch, tree clean. `git ls-tree -r -l HEAD`
shows exactly **twelve files above 100 MB**: the twelve
`envelope-NN/raw/powermetrics-idle-N.plist` files, 130.1–133.5 MB each
(600 s of `powermetrics` plist output at the 100 ms setting). GitHub refuses
files over 100 MB, which is the courier's inference and this record's
reading; the driver's captured error is only the non-zero exit. The push
was not retried. The evidence bytes are intact in the custody root and in
the archive (§3). Publication needs Ed's choice: Git LFS, excluding the raw
plists from the results branch (the reduced per-envelope records already
carry every number the summary uses), or a different destination. Lane
NIGHT-RESULTS-LARGE-FILES-01 (§8).

## §6 Diagnosis: why seven envelopes lost their clock anchor (magistrate's reading, executed evidence; a blind Fable refuter's verdict is in §9)

**Mechanism.** The anchor deriver (`derive_powermetrics_anchor_v3`,
`joulewise/uncertainty_evidence.py:814`) models the host wall clock as an
affine function of the monotonic clock across one capture: one rate within
±50 ppm of unity (`MAX_CLOCK_RATE_DEVIATION_PPM`, line 38), no step, and each
native whole-second label within 250 µs of that line. Before fitting, it
computes the wall-minus-monotonic offset at each of five host stamps
(`pre_spawn`, `sampling_started`, `first_parse`, `post_parse`,
`sampling_stopped`) and refuses when the offset's span across those stamps
exceeds **5 ms absolute** (`MAX_WALL_MINUS_MONOTONIC_SPAN_S = 0.005`, line 35;
check at line 1000–1005 → detail `wall_minus_monotonic_span_exceeded`). If
the fit succeeds it also refuses when the resulting effective bound exceeds
**5 ms** (`MAX_EFFECTIVE_CLOCK_ANCHOR_BOUND_S = 0.005`, line 41; check at line
1225–1227 → `effective_clock_anchor_bound_exceeded`); the bound is the anchor
interval plus the offset span plus stamp terms (docstring, lines 847–850).
Neither cap scales with capture length. `affine_clock_fit_empty` (line 1100)
is the case where the native-second constraints and the host stamps admit no
common affine line at all, that is, the wall clock changed rate mid-capture.

**Cause.** macOS's time daemon (`timed`) disciplines the wall clock against
NTP and, between syncs, runs it at a corrected frequency; the monotonic clock
is untouched by both. The unified log for the window (`/usr/bin/log show
--predicate 'process == "timed"'`, 02:10–04:35 PDT) records ten `cmd,apply,
src,adjtime` events, four of them material, and the frequency (`freq_scaled`,
units of 2⁻¹⁶ ppm) set at each sync. Every envelope's measured offset change
(offset at `sampling_stopped` minus offset at `pre_spawn`) is accounted for:

| timed event (PDT) | adjust | freq after (ppm) | falls in envelope | measured offset change |
|---|---|---|---|---|
| 02:28:08 | −7.765 ms | −0.69 | 01 (02:27:01–02:37:01) | −8.03 ms → span cap |
| (steady −0.69 ppm) | — | — | 02 | −0.41 ms → bounded |
| 02:56:19 | −4.294 ms | ≈ −2 | 03 (02:47:11–02:57:00) | −4.44 ms, rate change → fit empty |
| (steady ≈ −2 ppm) | — | — | 04, 05, 06 | −1.33, −1.18, −1.14 ms (04 fit empty; 05, 06 bounded) |
| 03:34:21 | −20.278 ms | −7.60 | 07 (03:27:10–03:37:00) | −22.32 ms → span cap |
| (steady −7.60 ppm × 600 s = −4.56 ms) | — | — | 08, 09 | −4.50, −4.49 ms → bound cap (5.08, 5.35 ms) |
| 04:03:55 | +16.596 ms | −2.53 | 10 (03:57:10–04:07:00) | +13.04 ms → span cap |
| 04:07:36 (three, ≤ 16 µs) | ≈ 0 | −2.53 | 11 start | — |
| (steady −2.53 ppm × 600 s = −1.52 ms) | — | — | 11, 12 | −1.51, −1.49 ms → bounded |

No `settimeofday` or step event occurred. The sign and size of every
discrete slew match the envelope it lands in, and the steady per-envelope
change matches the daemon's frequency term to within 0.1 ms. Envelope 04's
empty fit (1.33 ms change, no discrete slew logged) is best explained by the
tail of the 02:56 `adjtime` slew completing inside envelope 04 (envelope 03
captured only ~4.1 of the 4.29 ms plus drift; envelope 04's offset moves
~10 ppm in its first second), which breaks the affine model within its 250 µs
allowance: likely, not proven (§9).

**Why it never showed before.** The v3 anchor was ratified by the cold
science review of 2026-08-18 and exercised on short captures: the test
fixtures use 61 s and 101 s records (`tests/test_uncertainty_evidence.py`
491–535, `tests/test_environment_admission.py` 50–58) and the span test
injects a 6 ms step; no fixture exceeds 101 s. The 09-19 derivation-night
results branches contain no v3 anchor record; the 09-20 pilot attempt ran one
600 s envelope through v3 but it was refused earlier as
`no_native_second_rollover` (the envelope lived 2 s). This is the first night
with twelve completed 600 s captures under the anchor, long enough for the
daemon's ~30 min sync cadence and its ppm-level frequency corrections to
exceed a 5 ms absolute cap.

**The method's own precondition was not established (refuter finding, §9).**
The deriver's docstring (`joulewise/uncertainty_evidence.py:837–843`) states
that wall-clock discipline during a capture is excluded *structurally* by the
authenticated network-time-OFF admission, and that a capture with network
time ON or unknown is validation-only material. Every `session.json` of this
night carries `network_time_provenance: null` ("not established by this desk
harness"); the log shows NTP syncs every ~30 min all night and no toggle in
the arm window. The `clock.network_time_off` readiness probe
(`joulewise/arm_readiness_evidence_t0.py:1216–1243`) and the scheduler C4
code `scheduler_c4_network_time_on` exist for the pack-bearing T-0 path but
did not govern the evidence-night entry point. So the caps did what the method
says; the environment control that makes the caps reachable did not run. Two
consequences for the packet: (1) turning network time OFF for windows is an
admin (`systemsetup`) action, Ed's to take or delegate; (2) even with NTP off
the kernel keeps the last frequency correction, and at −7.6 ppm a 600 s
capture accrues 4.5 ms and fails the absolute effective bound alone (envelopes
8 and 9), so relaxing only the span cap does not cure the class.

**Materiality (pre-computed for the ruling).** The largest offset change
seen is 22.3 ms. Interior power in the retained envelopes is ~0.32 W
(154.88 J / 480 s). A 22.3 ms misplacement of a 480 s interior edge moves at
most 22.3 ms × 0.32 W ≈ **7 mJ** of energy in or out of the interior; even
priced at both edges it is < 15 mJ. The unfiltered envelope-to-envelope SD
is 1.45 J and the ratified attribution limit is ~1 J (D-078 cl. 11). The
caps therefore refuse envelopes for an alignment error 140–390× (about
2.5 orders of magnitude) below the instrument's own floor and the night's
scatter. The caps are power-independent: at a 40 W loaded capture the same
22 ms would be ≈ 0.9 J, so a 5 ms cap is sized for loaded captures, not for
idle ones. Under
Ed's standing rule that every tolerance is sized to the instrument (~1 J /
~5 J; never microscopic), a 1 J budget at 0.32 W corresponds to ~3 s of
alignment error, 600× the present cap. Relaxing or re-shaping the caps is a
change to a cold-review-ratified method: it is not this activation's to
make (rule 11); the packet goes to a cold gate with this arithmetic.

**Finding 2 (separate): start drift 7.6–10.2 s on every envelope after the
first** (envelope 1: 0.32 s). Each envelope's collector starts 8–10 s after
its scheduled monotonic start. The 60 s interior offset absorbs it (the
recorder is running before the interior opens), but the margin is 50 s, not
60 s, and the cause is unrecorded; the likeliest is the previous envelope's
finalisation (parsing a 130 MB plist) on the chain's critical path. Lane
ENVELOPE-START-DRIFT-01 (§8).

**Finding 3 (separate): `span_mismatch` on bounded envelopes 5, 6, 11.**
Full 480 s rail coverage yet the frame-overlap sum misses 480 s by more than
1 µs, so a joule value exists but the envelope is not retained. Folded into
the anchor lane's packet as a second question (the tolerance is again
microscopic against a 1 J instrument).

**Finding 4 (already registered):** the sampler delivered 2,535 frames in
600 s at the 100 ms setting (envelope 2 plist, `elapsed_ns` count), a mean
interval of ~237 ms; this is the 25G83 cadence change tracked by
INSTRUMENT-CADENCE-ATTRIBUTION-25G83-01 (rank 243). Noted on that lane.

## §7 Ruling (magistrate, within its authority; no process rule touched)

1. The night is a `DIAGNOSTIC_NO_PACK` GO with two retained envelopes and no
   disjoint pair. **"No cutoff qualifies" stands**; block two is not sized;
   no quiet-admission threshold is activated; everything stays PROVISIONAL.
2. **No next pilot night is prepared on this code.** With the present caps
   and the daemon's observed behaviour the expected yield is about five
   bounded envelopes in twelve, below the eight-envelope / four-pair floor
   the summary needs; another night would spend a window to reproduce §6.
   The critical path is the anchor lane's cold-gate packet (§8), then a
   re-run of the pilot under the ruled caps.
3. The results-branch publication waits for Ed's choice (§5); the push is
   not retried by any courier or magistrate.
4. Registration only: the three lanes in §8 are registered in the kernel with
   this record as authority; none is a ruling.

## §8 Lanes registered (kernel, agent lane)

- **QPE01-CLOCK-DISCIPLINE-ANCHOR-01** (rank 267, p1 phase gate): assemble the
  cold-gate packet on the v3 anchor's two 5 ms absolute caps and the 1 µs
  span-mismatch tolerance against 600 s captures under `timed` discipline,
  with the §6 table and materiality arithmetic; options for the gate: (a)
  caps derived from the energy budget (offset error × interior power ≪ 1 J)
  or scaled with capture length, (b) an honest error bound that prices the
  observed slew into `error_bound_j` instead of refusing, (c) a shorter
  anchored sub-interval per envelope; implement the ruled option under the
  twelve-row gate with a regression that replays envelope 07's stamps and
  a counterfactual that a true step (`settimeofday`) still refuses.
- **NIGHT-RESULTS-LARGE-FILES-01** (rank 268, p2, blocked on Ed): publish
  this night's results commit once Ed chooses LFS / raw-plist exclusion /
  another destination; make the driver refuse-or-route before pushing when
  any file exceeds 100 MB so a night never ends with an unpublished record.
- **ENVELOPE-START-DRIFT-01** (rank 269, p3 tooling): name the cause of the
  8–10 s collector start drift with executed evidence (chain timing between
  `envelope_end` and the next `envelope_start`, recorder finalisation
  duration) and either remove it from the critical path or size the interior
  offset budget explicitly.

## §9 Refuter (blind Fable seat, read-only; verdict appended when returned)

Blind Fable seat (general-purpose subagent, read-only, briefed with the §6
claim and asked to break it; returned 05:36 PDT). **VERDICT: CONFIRMED in
substance, with two corrections and one missed finding that changes the
framing.** Verbatim substance:

1. Every per-envelope number in §2 and §6 re-derives from `power.anchor` and
   `clock_stamps` in the session files; nothing wrong.
2. Which check fired: `wall_minus_monotonic_span_exceeded` from
   `_offset_envelope_s` (lines 310–329, max minus min of epoch − monotonic over
   the five host stamps) compared at lines 998–1005 to the absolute 0.005
   (line 35); `affine_clock_fit_empty` at lines 1097–1100 (the exact LP over
   native whole-second rows plus stamp rows is infeasible under the 250 µs
   allowance, line 37); `effective_clock_anchor_bound_exceeded` at lines
   1178–1184 / 1225 (anchor half-width + span + resolution + padding: envelope
   08 = 0.000532 + 0.004542 + 2e-6 = 0.005077). No scaling by capture length.
3. Root cause reconciled to 0.1 ms for every envelope from the `timed` log:
   frequency corrections −0.69 / −1.94 / −7.60 / −2.53 ppm across the night
   (rate × duration reproduces envelopes 02, 05, 06, 08, 09, 11, 12) plus four
   `adjtime` slews (envelope 07: 20.28 + 1.94 ppm × 431 s + 7.6 ppm × 160 s =
   22.34 ms, observed 22.36; envelope 10: −7.6 × 405 s + 16.60 − 2.53 × 186 s =
   +13.04, observed +13.03). Alternatives excluded with the fields used: stamp
   ordering / parse bracket (first_parse vs sampling_started differ ≤ 3 µs,
   sampling_stopped vs post_parse ≤ 40 µs; `first_parse_lag_s` 0.06–0.15 s);
   a single step (four corrections, no `settimeofday`); native timestamps
   (the span check uses host stamps only); the 100 ms interval / 130 MB plist
   (not the cause).
4. Corrections: materiality is 140–390× (≈ 2.5 orders), not four; the caps are
   power-independent (22 ms ≈ 0.9 J at 40 W); the novelty claim was partly
   wrong (the 09-20 envelope-01 went through v3 and was refused as
   `no_native_second_rollover`).
5. Missed finding (adopted into §6 above): the method's network-time-OFF
   precondition was never established on this entry point
   (`network_time_provenance: null`); and with NTP off the residual frequency
   correction alone still fails the absolute bound at 600 s.

Magistrate's synthesis: the diagnosis stands; the packet for A267 now carries
both halves, the unestablished environment control (Ed's admin action or an
entry-point refusal when network time is ON) and the absolute caps that fail
even a disciplined-but-NTP-off clock at 600 s. §7 is unchanged: no next pilot
night on the present code.

**Addendum (2026-09-23 03:10 PDT, magistrate 7a0f14bd, fix round 1 of lane QPE01-NONOBSERVER-PREDICATE-01, ruling on contract-lens finding S1).** The component split in the addendum above is corrected. `whole_envelope_observer_cpu_s` is the collector's own CPU plus the CPU of the children it reaped; the 30 s load recorder is launched by the executor as a sibling of the collector and is therefore NOT inside that figure. Re-derived from this night's bytes with the v3 code (per-envelope shares, mean over 12 envelopes): round block 0.0525 cores and reaped power recorder 0.1233 cores, which sum to the floor 0.176 (unchanged, the ruled statistic); the load recorder's own 0.0073 cores is outside it, so the apparatus including the load recorder is 0.183 cores (reported as `observer_floor_including_load_recorder_cores`, never a stop input). The earlier "≈ 0.116 power recorder" subtracted the sibling's cost from a total that never held it. Ruling 31's `definition` sentence ("including … load recorder") is therefore inaccurate for that one term; the sentence stays as ruled and the inaccuracy is carried to the block-two consult. Nothing measured changes; the stop cause stands.
