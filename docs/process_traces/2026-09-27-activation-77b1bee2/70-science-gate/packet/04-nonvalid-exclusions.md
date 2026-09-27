# 04 — Non-valid slots and exclusion mechanism check

Primary sources: `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/runs/calibration_observation_ledger.jsonl` (sha256 `23f72c37cb2483faa1b31a603996b86d6b7b390ce9460f490699501cfc971c7d`); session custody `instrument_evidence.json` files, each individually hash-bound by its finalization row; `docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json` (sha256 `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2`).

Candidate `derivation_notes.excluded_members`: `[]`. Candidate `derivation_notes.battery_confounded_sessions`: `[]`. Each session has 12 finalized rows, six valid and six ordinary-invalid. The table lists every non-valid capture, with ledger disposition and evidence reasons verbatim as JSON strings.

| Session | Slot | attempt_id / member_id | Ledger disposition | Named evidence reasons | manifest_sha256 | instrument_evidence_sha256 | Evidence file sha256 check |
|---|---|---|---|---|---|---|---|
| w1 | d01 | `d079-epoch-25g83-derivation-w1-20260927-d01` | `ordinary-invalid` | `clock_anchor_unresolved, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `6141f3656531b7608c85b3c6520593669db1e8df48e12051c22533246791d9ac` | `78c90320a0aae47985ba437c104780fecd94a2d8072862668e52ea7f40309f0d` | match |
| w1 | d02 | `d079-epoch-25g83-derivation-w1-20260927-d02` | `ordinary-invalid` | `detection_nonconvergent, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `41264d05fbf55abc64e5fa19b6be04e8b65d202f9f9c5c5ea4a6be87eb8f568d` | `e9c2ebbc5d63f5002289b578be370417493e4a94924c5c29495e44242ab779bf` | match |
| w1 | d03 | `d079-epoch-25g83-derivation-w1-20260927-d03` | `ordinary-invalid` | `detection_nonconvergent, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `9f1f995a07c7b461a43290b2efb9a0bc6cdf8dc9e39e4833b60be2ff8e4714db` | `5c23144fac117d9029301322a0e0b2875e40379df0d081d462c0db67d829001b` | match |
| w1 | d08 | `d079-epoch-25g83-derivation-w1-20260927-d08` | `ordinary-invalid` | `clock_anchor_unresolved, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `c4b8baa4905b4ffaf9ecb51161dddbd4d71a6d66bab2f115eb0e89e1d9f585e0` | `912b2d14c06dea981e67ffa14adb0f7d11344ab0be66710a7983e596b161bc19` | match |
| w1 | d09 | `d079-epoch-25g83-derivation-w1-20260927-d09` | `ordinary-invalid` | `detection_nonconvergent, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `b244e0d1c04eca100c93bf5e1d4049e2fc87d52a30274edc1d00be296e37b290` | `dcbfa835ead0243c76f569d9c9dd50a5cc1b6d2d5cd770c5e11f5bbd71fa21e6` | match |
| w1 | d11 | `d079-epoch-25g83-derivation-w1-20260927-d11` | `ordinary-invalid` | `clock_anchor_unresolved, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `6ca12f869bea294a9d02caab385105db796121c125eb41751317280ca318476e` | `c023d6bc40587d0383973bf86e5a88dcd3ee7949d3b4d72e5ad546f76004a387` | match |
| w2 | d02 | `d079-epoch-25g83-derivation-w2-20260927-d02` | `ordinary-invalid` | `detection_nonconvergent, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `3c7e5e4955c52ac79f6306b9a967568d79883a599d447113628ffa2003eeb71a` | `79e864a036e8c950187b4635da10f0591913080905f6076470e3bc838628f133` | match |
| w2 | d06 | `d079-epoch-25g83-derivation-w2-20260927-d06` | `ordinary-invalid` | `detection_nonconvergent, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `cda8b0a9eddb37e76c9db3dfaaf0206f4d5d7a66de54941167045ef2b5c3691c` | `3b5097b8bad7c5a3f3d41b7b7480c6a196f7487ca7e08ec07440804a3309a363` | match |
| w2 | d07 | `d079-epoch-25g83-derivation-w2-20260927-d07` | `ordinary-invalid` | `clock_anchor_unresolved, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `ccb1851fa1f1a55c2a1140bd3d0e39b4edfef6e0c28577fb4f6c05ea66b60666` | `72ae39362923657879f4696ad8d9c2d947eb0a6a218066303ad620496689f681` | match |
| w2 | d08 | `d079-epoch-25g83-derivation-w2-20260927-d08` | `ordinary-invalid` | `detection_nonconvergent, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `00977ee2041a949aa2be2b179dffd950ae2e3be1fa14b3927c14cd75d37de6d0` | `baa0a2e2a040297a140adb1c57b5e64d435f6d2b2df38537da1d3f9baffc96c8` | match |
| w2 | d11 | `d079-epoch-25g83-derivation-w2-20260927-d11` | `ordinary-invalid` | `detection_nonconvergent, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `939631843afa516a00acc3943f8c067136e8bc9c53f8f8de993bcb9e5d8aeacb` | `b9c276cb750781f0914306b250c5c2fcc29de412afb212f9a384772a14ad8751` | match |
| w2 | d12 | `d079-epoch-25g83-derivation-w2-20260927-d12` | `ordinary-invalid` | `detection_nonconvergent, not_all_pulses_detected, pulse_count_below_protocol:0!=59` | `dd8a6dc69f1f200a77a6b890192bb9145754fe16ea9d9a1eb2eaf3d6589f0e6c` | `c6b6e7348b1365b152c8ea26ba01cdec0be6b907a07704c786be6b300dd95118` | match |

The named evidence reasons above are validation failure reasons, not candidate `excluded_members` entries. The ledger supplies the disposition; the evidence file supplies the reason list. No B-based exclusion is recorded.

Mechanical assertion check: `affine_clock_fit_empty` is the sole registered *valid-member anchor* exclusion class in `calibration_bracketing.py:287–293`; issuer `_select_members` skips non-valid ledger rows and refuses a valid unresolved row whose reason is outside that set (`issue_calibration_acceptance_generation.py:1281–1301`). The registration also names ordinary-invalid protocol failures and interrupted windows (`preregistration...:166–172`), while A-R5b separately permits battery-based whole-window exclusion (`:648–660`). Thus “only registered exclusion mechanism” is true for valid-member anchor exclusions, not as a statement about all non-valid captures or entire windows. This packet records zero candidate member exclusions and zero battery-confounded sessions.

### preregistration_d079_epoch_25g83_rev1.md lines 160–172

Primary source: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`). Verbatim:

```text
session of this registration; a valid same-epoch observation outside this registration refuses issuance rather than
being absorbed. Valid registered observations whose stored outcome does not resolve are listed in
derivation_notes.excluded_members with their named mechanism, member_id, manifest_sha256 and
instrument_evidence_sha256; the prior-set row is matched by the content id derived from those two hashes.

Exclusions (mechanism-named, outcome-independent, decided before capture). An observation is excluded only if (a) its stored
anchor-v3 record shows the estimator's clock-anchor feasibility model admitted no feasible affine fit
(affine_clock_fit_empty, the r6 exclusion class, and the ONLY exclusion mechanism registered at this step: an
unresolved anchor carrying any other reason refuses issuance instead of quietly excluding the member);
(b) a protocol gate fails (plateau, SNR, 59-pulse detection, spurious plateau, edge coverage), which the writer records
as ordinary-invalid; or (c) a recorded operator or system event interrupted the window. Every exclusion is recorded with
its named mechanism and its ledger row is retained.

```

### preregistration_d079_epoch_25g83_rev1.md lines 610–615

Primary source: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`). Verbatim:

```text
## Sample, stops and blindness

W1 and W2 are derivation-kind windows of 12 declared slots each, at least 6 h apart; each has a 600 s settle and 600 s slot start-to-start cadence. W1 is derivation window one. At W1 harvest, the pin-free cadence report reads raw plists before any B value is read; if the median of the per-capture median native frame lengths is above 150 ms, stop: no W2, return to council. Then the count-only dry run runs before any B value is read. If it reports fewer than 6 valid of 12, stop: no W2, return to council. W2 then runs. W3 is permitted only if the count-only dry run after W2 shows fewer than 12 valid, and is another 12-slot window. Every valid resolved member is retained. Retained n ≥ 12 is the issuance floor; 12/13 order-statistic coverage, the floored S and t(0.995,11) support it. The earlier 0.245 s yield reason no longer applies. No B-based exclusion or outcome-driven top-up is permitted. B values are read only after the terminal session. Rules are fixed here before capture. The dry run may report valid count and “median native frame length,” alongside the existing counts, states and exclusion mechanisms; it reports no B value, screen or comparison.

Revision 2's equivalence look is NOT taken for this epoch. Reason: the r7 envelope's ceiling is its July corpus maximum at ≈120 ms frames; B grows with frame length; a 12-draw look cannot distinguish a +6 % regime from an identical one. W1 is derivation window one. There is no PASS continuation branch or FAIL branch for this epoch.

```

### preregistration_d079_epoch_25g83_rev1.md lines 648–660

Primary source: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` (sha256 `81b65f08b19127a106307b9b94616dfeb49d04c3c69f72615cf316792e36ddf1`). Verbatim:

```text
# Revision 5 — Amendment A-R5b (2026-09-25): battery float (directive #421)

Revision 5 above is sealed; not one word of it is edited here. This amendment adds one outcome-independent, mechanism-named exclusion decided from instrument state alone, and the rules that follow from it. It authorizes no window and licenses no measurement.

**Predicate.** A battery-float observation is one run of `/usr/sbin/ioreg -r -c AppleSmartBattery` whose raw standard output is retained. It PASSES when exactly one AppleSmartBattery object is present and, read only from that object's top-level property lines, `ExternalConnected = Yes`, `IsCharging = No`, `|InstantAmperage| ≤ 200 mA`, and the object's `UpdateTime` is no more than 180 s before the observation's wall time. A printed integer at or above 2^63 is read as that value minus 2^64 (two's complement; example: `18446744073709551458` reads −158 mA). A missing, duplicated, malformed or unreadable property, a failed or timed-out probe, a stale `UpdateTime`, or more than one object is not a pass. `Amperage` is recorded but never substituted for `InstantAmperage`. Each observation also records `Amperage`, `Voltage`, `Temperature`, `FullyCharged`, `CurrentCapacity`, `AppleRawCurrentCapacity`, `AppleRawMaxCapacity` and `UpdateTime`.

**Admission.** A window is admitted only if the predicate passes at the arm check, again immediately before publication, and again at t0 inside the night gate's C3 row (refusal code `night_refused_battery_float`; probe failures are `night_probe_error`). A t0 or arm refusal with zero capture is a machine-state refusal under D-182: it licenses one new-plan successor on D-182's terms and is never a same-plan retry and never waived.

**Per-slot evidence.** Every derivation slot whose capture writer reaches its custody directory records one observation before the capture's first clock stamp is taken and one after its last clock stamp is taken, so that neither observation falls inside the interval the clock anchor is computed from and neither overlaps the sampler's life. The raw bytes are retained under the slot's custody as `raw/battery_float.pre.ioreg` and `raw/battery_float.post.ioreg`; their SHA-256 digests, the verbatim property lines and the parsed values are recorded under the key `battery_float` in the hashed `instrument_evidence.json`. A failing or absent observation does not change the writer's exit path. The registered protocol, chain digest, sampler set, estimator-code pins and the estimator's clock-stamp inputs are unchanged.

**Window verdict.** Before the cadence report, before the count-only dry run and before any B value is read, every slot of the window that has a finalized ledger row, whatever its disposition, is checked from its raw bytes alone: both observations must be present, authenticated against the recorded digests, re-parsed, and must pass the predicate. One slot failing the predicate makes the whole window `battery_float_confounded`; one slot with a missing, stale, unparseable or unauthenticated observation makes it `battery_float_evidence_missing`. Either verdict is final for that window. A declared slot the window never reached (`window_exhausted`) carries no obligation.

**Consequences.** A window with either verdict is retained and disclosed. None of its slots is a member; none counts toward the "fewer than 6 valid of 12" stop, the 150 ms cadence stop (its cadence report is produced as a diagnostic only), n, or W3's trigger; its B values are not read before issuance is decided and are diagnostics afterwards. The issuer computes the verdict itself from raw bytes for every derivation-kind session it is asked to consider or that would otherwise refuse issuance under addendum A-7; the operator names the excluded sessions separately and issuance refuses unless the two sets are equal, so no clean window can be declared confounded and no confounded window can be omitted. The harvest record, the candidate's derivation notes and the next arm notice name the window, the failing slots, the raw digests and the reasons.
```

### calibration_bracketing.py lines 287–294

Primary source: `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/joulewise/calibration_bracketing.py` (sha256 `e0d36f234426a4c1f61203f7045afe6a4341f9378411662243cbedf3ffbddaed`). Verbatim:

```text
# Mechanism-named, outcome-independent corpus exclusions (ruling 46 §R-a A6).
# Today's only registered class is `affine_clock_fit_empty`: the anchor-v3
# replay found NO feasible affine wall-versus-monotonic clock fit for that
# capture, so no bound can be derived from it at all.  The exclusion turns on
# that replay outcome, never on the value the capture produced.  It is the
# class recorded at r6 `derivation_notes.excluded_predecessor_members`.
REGISTERED_CORPUS_EXCLUSION_REASONS = frozenset({"affine_clock_fit_empty"})
# Terminal dispositions a LIVE row may carry inside an `import_plus_live`
```

### Issuer member selection, lines 1281–1301

Primary source: `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/scripts/issue_calibration_acceptance_generation.py` (sha256 `21b2eea8c64e5fe1ca41474927e2b15471ceb11f2bd7e5f31b89445d3f53060c`). Verbatim:

```text
            )
    for observation in ordered:
        if observation.classification_disposition != "valid":
            continue
        evidence, _manifest = _read_member_evidence(observation)
        resolved, detail = anchor_v3_replay_outcome(evidence)
        entry = {
            "member_id": observation.attempt_id,
            "manifest_sha256": observation.artifact_sha256["manifest.json"],
            "instrument_evidence_sha256": observation.artifact_sha256[
                "instrument_evidence.json"
            ],
        }
        if not resolved:
            if detail not in REGISTERED_CORPUS_EXCLUSION_REASONS:
                raise PrepareRefusal(
                    f"member {observation.attempt_id}: unregistered exclusion "
                    f"mechanism {detail!r}"
                )
            excluded.append({**entry, "reason": detail})
            continue
```
