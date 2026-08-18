# Ed's morning packet — 2026-08-18 (before the ~3pm Rivoire meeting)

Everything below is read-and-reply; no hands-on machine work except the
dress rehearsal (item 4). Rulings in priority order — item 1 gates the
whole chain.

## 0. OVERNIGHT UPDATE (read this first — most of item 1's chain already executed)

You ruled "B, keep" and licensed the night. Executed since: the D-079
successor ISSUED as `d079_calibration_acceptance_v2_n19_r2` with the full
live-pin migration (one commit, zero science delta, staleness fan-out all
green); the `_v2` family FROZEN — three `freeze-0002` receipts, PASS,
minted in the durable measurement checkout `/Users/edr/JouleWise-measurement-20260818`
after a path-binding catch (receipts authenticate their absolute pack_root;
the first mints were scratchpad-bound and were reverted on-record); the
dress-rehearsal card committed (`docs/process/rehearsal-operator-card.md` —
run it at that measurement checkout); the R1 registry install correctly
BLOCKED on your reserved environment-comparison semantics (five-item
NEEDS_RULING recorded, joins your list below).

**SHAKEDOWN FIRST-LIGHT (D-139):** the quiet-state baseline captured clean
(600×1s idle; GPU mean 0.34 mW, 95.8% zero samples, thermal nominal). The
first calibration bundle CAPTURED corpus-grade (SNR ~43k, no gaps) but the
NEW detect-pulses budget fail-closed: `detection_nonconvergent` at exactly
100,000 cells. Root-caused with an executed discriminator: three issued
corpus members ALSO exhaust that budget under the new detector (real
workload ~122-124k; a 130k override completes all 59 fits) — the budget
was set below the real corpus workload and no audit could see it (raw
corpus traces live outside the repo). The instrument and the night were
both sound; the fail-closed behavior worked. A full-corpus sweep is
running to ground the corrected budget value + margin — COMPLETED while
you slept: full-corpus sweep n=34 (max 137,189 cells), budget ruled to
165,000 (20.3% headroom, exceeds the observed spread), and the ENTIRE
D-138 cycle re-executed: one-pin reissue (in place, same identity),
packs regenerated, evidence re-authored, family RE-FROZEN at the
measurement checkout — final head 75f22a0, all batteries green.

**AND THE HEADLINE: last night's captured bundle, re-derived under the
corrected budget — b_fiducial = 0.0309 s, INSIDE the issued corpus band
[0.0227, 0.0336], 59/59 pulses, evaluation count exactly as the sweep
predicted. The instrument is verified with real overnight data.** The
maiden fail-closure + root-cause + corpus-grounded correction + in-band
re-derivation is, frankly, the strongest instrument-soundness story this
project has: the safety machinery caught a real mis-set parameter on its
first live contact, and the correction was derived from the complete
corpus, not tuned to pass. Rivoire will recognize what that means.
(Reduction record: shakedown-20260818/reduction-under-165k.json.)
Your morning rulings below.

## 1. RULED ("B, keep") — EXECUTED. Retained for the record: D-079 reissue identity

The estimator change (detect-pulses, audited) requires reissuing the D-079
calibration acceptance. The reissue tool ran clean: **19/19 corpus members
authenticated, VERDICT=PROCEED, zero science-facing delta** — member set,
all 19 fiducial values, thresholds all byte-identical; exactly ONE pin
changed (`powermetrics_fiducial.py`, the audited change). The successor
artifact's NAME is reserved to you (R1 clause 6), and it genuinely matters:
the `_v2` in the current artifact is the SCHEMA version, not "issuance 2"
(no `_v1` ever existed), and `_v3` is informally reserved by an unratified
custodied design for a future schema.

- **Option B (recommended):** `d079_calibration_acceptance_v2_n19_r2` at
  `configs/calibration/calibration_acceptance_d079_v2_r2.json` — keeps the
  schema grammar honest, marks reissue #2, leaves `v3` free.
- Option A: name it `_v3` (reads as an ordinal but contradicts the embedded
  schema version and burns the reserved token).
- Option C: adopt the unratified future-schema naming now (out of scope for
  this transaction).
- Sub-call: keep `decision_ids` as `["D-102","D-109"]` with D-138 recorded
  in the commit + decision log (recommended), or add D-138 to the artifact.

Reply like: **"B, keep"** — the migration then executes as one audited
commit (inventory pre-assembled to the line number), the staleness fan-out
goes green, and the freeze follows.

## 2. RULING: family-marker particulars (gates PUBLICATION, not the freeze)

Your A3 approval reserved the complete-family marker's exact schema, path,
and activation predicate. The freeze-numbering consult recommends: an
EXTERNAL marker file outside the pack roots, created only after all pack
bytes are final, binding the three final pack digests + the three
freeze-0002 receipt hashes (a receipt cannot bind its own pack's final
digest — self-hash cycle). If you approve that shape, say where it lives
(suggestion: `configs/arm_readiness/d117_v2_family_marker.json`) or defer
to my judgment on path+schema with the binding set as consulted.

## 3. CONFIRMATION (the irreversible point — after 1 lands and the freeze runs)

You'll get a short exact-byte summary: three pack tree hashes, three
freeze-0002 receipt hashes, the marker bytes. Publication happens only on
your explicit yes. Until then everything is revertible.

## 4. Dress rehearsal (~30-40 min at the machine)

The operator card generates against the frozen `_v2` alpha pack right
after item 1's ruling lands (builder run ~30 min). It walks E-4→E-9 +
author→ARM→verify→consume against scratch custody — your operator ceremony,
the last open qualification row.

## 5. Qualification ledger (last night's evening + overnight)

CLOSED with custody evidence in ~/JouleWise-window-custody/ed-qual-20260817/:
- D-127 sudoers install + BOTH clock vectors (ground-truth state flips).
- Sampler lifecycle (cadence 1.0128 s, zero orphans).
- Rail probe (ABBA executed; ANE delta exactly 0; cpu delta negative under
  concurrent replay load + charge-to-full — caveats recorded; boundary
  verdict stands on code evidence).
- Keyboard-backlight rows (level 0 / auto-adjust off / inactivity never).
- ED-QUAL-L4-1 decisive replay: **DECISIVE REPLAY: OK** (3h40m, full
  chain). Your run also flushed 3 real defects (replay work-dir default,
  decisive-test API drift invisible to CI, sudo-probe incompatibility) —
  all fixed and pushed same evening.
- ED-Q-L9-3 quiet census (lead-captured 23:51 with fleets quiesced;
  browser/monitor/maintenance over-match ground truth confirmed; labeled).

OPEN: the dress rehearsal (item 4) only.

## 6. Carried-forward rulings (no urgency today)

- A4 contrast-pack pending-ratification / TODO markers.
- Environment-fingerprint comparison semantics (R1 fail-closed seam holds).
- The three-mechanism trusted-operator limitation family note (one
  risk-appetite question in three costumes) — for a calm moment, not today.

## Overnight summary (for context, all on integration/phase2-transaction)

Both code streams closed through full gauntlets (7 generator rounds + 9
audits + 1 structural consult + 1 three-seat cold gate; freeze-engine
rounds with 4 audits): the `_v2` family generates with an exact 334-file
write boundary, freeze semantics ruled (receipts govern; bytes never
transition), `freeze-0002` chain with authenticated predecessors built and
audited, `_v2` family generated on the branch, D-079 candidate derived and
custodied (deterministic sha 6956b957…). Model roster per your directive:
Opus carried all implementation; terra/luna carried audits (both graded
strong); Sol did the two design consults. Full trace in the run report.
