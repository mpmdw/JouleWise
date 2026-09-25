# 01/30 — Magistrate synthesis, council ACCEPTANCE-25G83-02 (Opus 5.5, activation 152c9255)

Inputs: the question [00](00-question.md) and four blind seats: Sol 6.0 [02-seat-sol](02-seat-sol.md), Astra 6 [02-seat-astra](02-seat-astra.md), Opus 5.5 [02-seat-opus](02-seat-opus.md) and Fable 5.1 [02-seat-fable](02-seat-fable.md). All four ran read-only at `032e9661` and finished at ≈04:39–04:41 PDT 09-25. This synthesis is argument for the cold judge, not authority.

## 0. Terms used below

- **Cadence.** The interval between successive `powermetrics` samples. 100 ms is requested; what arrives is the "native frame length".
- **Interior.** The middle part of each timing pulse, after a 0.25 s inset at each end, inside which the detector requires at least one whole sample interval (`joulewise/powermetrics_fiducial.py:751-761`). For a 1.0 s pulse (protocol v3) the interior is 0.5 s wide. It is guaranteed at every phase only if the local intervals are ≤ 0.25 s. The packet's phrase "two samples inside" meant two sample *boundaries*; all four seats corrected it (NIT).
- **B.** The per-capture anchor bound `b_fiducial_s`: how far the capture's clock anchor can be wrong, in seconds. The acceptance issues screens on B.
- **Equivalence path (D-102).** Before deriving a new acceptance, one quiet night is checked against the r6 envelope. PASS means every retained B ≤ 0.032898493715362 s (r6's corpus maximum) and the night's range ≤ 0.009724 s (r6's corpus range), and the existing acceptance continues. FAIL means a successor is derived, and that night counts as the first derivation window (Ed, issue 316, prereg `:421-470`).
- **I / D / SH.** Launchd with `ProcessType=Interactive`; launchd with no key (the default, which is what the night agent renders today); and a login shell.

## 1. Where all four seats agree (proposed as ruled)

- **U1 — Cure (A).** Put `ProcessType=Interactive` in the night template and the probe template, and keep protocol v3 (1.0 s pulses). No pinned estimator file changes, so there is no r8 reissue.
  - Decisive facts, recomputed from raw plists by Opus and Fable independently:
    - Under I, the median is 131.5–131.8 ms and the maximum 140.8–143.9 ms over ≈14,900 intervals. There are zero intervals over 0.25 s, so the v3 per-pulse miss rate is 0.
    - Under D at night, the median is 248.5 ms; 43–47 % of intervals exceed 0.25 s; the per-pulse miss rate is 3.1 %; and P(all 59 pulses pass) is ≈ 0.155. That matches the observed 11 valid of 22 non-anchor captures.
  - Opus's argument against (B), v4 plus Interactive: production's idle baseline has its own bound of 55 s for 300 samples (`adapters/powermetrics.py:1468-1470`). So any median above 183 ms makes every science run fail closed regardless of pulse length. v4 would protect the calibration but not the science, and it touches the D-138 pin set, which forces r8 and a re-freeze.
- **U2 — Installer refusal.** `night_agent_install.py` refuses any rendered night, dead-man or probe plist whose `ProcessType` is not exactly `Interactive`, mirroring the existing `KeepAlive` refusals (`:975-976`, `:1091-1092`), with unit tests. The seats rated this MATERIAL to BLOCKER: without it, a template regression silently brings back the 09-19 failure.
- **U3 — Children inherit.** Opus corrects record 26: its QoS readings were taken in the job process only (`cell.py:28-39,192`). Inheritance is shown instead by the grandchild `sudo -n powermetrics`, which delivered 243.2 ms under D and 131.8 ms under I in the same session. `run_night.py` uses only `start_new_session=True`, and no QoS, `nice` or `taskpolicy` change exists in the chain. No per-child override is needed. The real-path check (S3) records the delivered child cadence.
- **U4 — Fate of the v4 work.** Close the v4/rev4 PR unmerged. Keep the branch, tagged `acc-v4-fallback` at `ea10e3c8`. Salvage:
  - the stale-number audit;
  - the epoch-scoped n ≥ 12 validator, re-keyed to v3 (Opus MATERIAL: it must not keep `pulse_protocol_id: v4` in its key);
  - the D-126/D-125 addenda and issuer changes, including zero headroom;
  - the dry-run valid-count field;
  - the issuer's `_derivation_frame_cadence`, which is not pinned.

  Do NOT salvage the `reduce.py` cadence flag. `reduce.py` is pinned, so the flag would stale r7 (Opus, Astra). Put the per-window cadence report in a pin-free harvest or check script instead. This overrules Fable's salvage of the `reduce.py` flag on the pin fact.
- **U5 — History.** Nothing measured under the default night agent from 09-15 onward is claim-bearing. n1/n2 of 09-19 and qpe01 of 09-23 are diagnostic only, and are never acceptance members. D's compute bias is unmeasured and no longer matters, because no future data are taken under D.
  - The paper discloses:
    - the launch-context finding;
    - that all calibration and claim captures run under I at ≈132 ms, against July's shell at ≈120 ms;
    - the I/SH result, including the widened interval [0.861, 1.161] crossing δ and Astra's dissent;
    - the 0.5 % R offset;
    - the single-workload scope.
  - Astra adds: do not publish "timer coalescing" as the sole proven cause.
- **U6 — Window conditions.**
  - PR #410 (clone relocation) lands before W1. Opus adds: if it is unmerged 24 h after the registration seals, W1 proceeds with the clone's index state recorded.
  - Quit Wispr Flow at arm and relaunch it at harvest. The agent does it, it is recorded in the census, and it is not a refusal gate (Opus). Three seats say to quit it; Opus notes E's SD stayed at 0.2–0.3 % with it running.
  - Keep the network-time pause. A `systemsetup` "Error:-99" that returns rc 0 is logged as such, and clock-step and anchor gates remain the detector.
- **U7 — Authority.** Nothing on this path is Ed's except the arm-notice NO and the after-the-fact summary. R-ACC-5 (the auto-update hold) stands as a request, not a precondition:
  - Opus's read-only `defaults read` shows `AutomaticDownload = 1` with no install key, so the hold is not verifiably off;
  - the toggle needs an admin login, so it is an Ed settings item;
  - `os_build` is verified at arm, and a build change voids the epoch and fails closed.
- **U8 — Registration mechanics.** Append a new dated revision to `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`:
  - the epoch stays six-field with `powermetrics_pulse_fiducial_v3`;
  - add a pinned operating condition: "captures launched by a launchd agent with `ProcessType=Interactive`, template at commit X", with rendered-template digests;
  - keep blindness, count-only W3, zero headroom (i), the stale-number audit (j), and the barrier basis (l) with launch context added to the physical list;
  - the screen challenge (g) stays dropped as an issuance veto and is diagnostic only. Fable computes 14 % and Opus 16.3 % false refusal under an identical instrument;
  - seal the digests of the revision and `protocol_v3.json` into the arm notice (ruling 20 §7).

## 2. A fact two seats found and two missed (proposed BLOCKER)

- **F1 — n1/n2 disposition.** Under v3 the eleven valid n1/n2 captures are same-epoch, so the issuer refuses a successor. The refusal is `scripts/issue_calibration_acceptance_generation.py:1273-1290` ("valid same-epoch observations outside this registration … not issued", addendum A-7), and prereg rev 1 `:164-165` says the same. The magistrate verified both at the bench. This did not bite under v4, because v4 is a different epoch.
  - Astra: apply the existing D-126 disposition by content id (`decision_log.md:8492-8498`), with the disposing decision recorded in the successor's prior set. Fable: an explicit excluded-session list in the issuer, with the mechanism "captured under default-ProcessType launch context", disclosed as authored after the values were seen.
  - Proposed: Astra's form, since it uses an existing mechanism, with Fable's mechanism text. Also ensure the disposed observations cannot re-trigger staleness after a continuation PASS (Astra).

## 3. Splits (the magistrate's proposal and the dissent, for the judge to rule)

- **S1 — Take the equivalence path first?** Fable, Sol and Astra say yes, prospectively, as one sealed look. Opus says available but not taken.
  - Opus's argument: even if the new captures come from exactly r6's distribution, P(PASS) ≈ 0.48 (level 17/29 = 0.586, range ≈ 0.62, joint 0.480 by Monte Carlo). A PASS also carries an envelope derived at 120 ms onto a 132 ms regime.
  - **Proposal: take it**, with Ed's issue-316 rule that a FAIL night counts as W1, sealed before W1.
  - Reason: with FAIL ⇒ W1, the path costs no extra window. The expected count is 1 + 0.52 × 1 ≈ 1.5 windows against 2. Opus's 2.0 assumed a FAIL needs two more windows.
  - The 120→132 ms objection is exactly what the PASS test measures: PASS means every new-regime B sits inside the r6 envelope, so continuing r6 bounds everything observed.
  - Dissent recorded (Opus).
  - Must be sealed:
    - the m < 6 branch is the existing rule (one more equivalence night) and nothing else;
    - a PASS licenses nothing until the dated 25G83 continuation addendum lands (Sol BLOCKER);
    - Fable's desk check that `authenticate_epoch_continuation` (`calibration_epoch_continuation.py:176-310`) does not refuse on the older finalized n1/n2 sessions. Its interaction with F1 is to be verified in the implementation PR.
- **S2 — Real-path check before spending a window.**
  - Fable: two throwaway-label smokes under display sleep, ≥ 30 min apart.
  - Sol: W1 slot 1 as the check.
  - Astra: an operational prefix at W1 start (300-sample idle capture plus the first slot).
  - Opus: a 60-sample cadence phase in the existing night probe, which runs at every arm under the real installed probe label (`night_agent_install.py:994`, `run_night.py:_probe_worker`), PASS iff median ≤ 150 ms and max ≤ 250 ms, else the installer refuses to arm; plus an in-window W1 cadence stop.
  - **Proposal: Opus's probe phase plus the W1 cadence stop (S4).** The probe phase is mock-free (D-183) and runs at every arm, not once, so it catches template regressions for the life of the cure. The in-window stop covers the quiet-night regime that a daytime probe cannot see. That makes the Fable, Sol and Astra variants redundant.
- **S3 — Display state.**
  - Fable: target display asleep.
  - Sol: test asleep in the installed slot.
  - Astra: display on at a fixed recorded brightness for this acceptance and its claim windows.
  - Opus: no gate, record it. Session 2 showed D coalescing at 243 ms with the display ON, so display sleep is not D's mechanism, and the cadence stop covers any asleep effect under I.
  - **Proposal: record per window (powerd assertion and display state); no gate; the machine's normal display policy.** If the W1 cadence stop ever fires with the display asleep, the fallback trigger (U4) names it. Astra's consistency point (hold calibration and claim windows in the same state) is taken as a disclosure field, not a gate, because no evidence shows display state moves B or E under I.
- **S4 — W1 stops.**
  - Opus: futility at < 6/12 valid, not < 8/12, because 8/12 false-stops a healthy campaign 8.7 % of the time at p = 30/38 while < 6/12 does so 0.5 % of the time; plus a cadence stop: median of per-capture median frame lengths > 150 ms ⇒ stop, no W2, council.
  - Fable and Sol keep < 8/12. Astra: < 6 retained ⇒ INCONCLUSIVE.
  - **Proposal:** in the equivalence frame, m < 6 is already the INCONCLUSIVE rule (one more equivalence night). For the derivation fallback, adopt Opus's < 6/12 with the cadence stop. Cadence is a property of how the instrument ran, not a B value, so reading it does not break blindness (Opus, Sol).
- **S5 — Excursion refusal at B > 0.25 s.** Fable and Opus keep it, and Opus restates the basis: 0.25 s = `PLATEAU_INSET_S`, and an onset shift that large crosses the whole inset. Sol says reassess; Astra says drop, on the ground that "one sample interval" no longer describes 0.25 s. **Proposal: keep, with Opus's restated physical basis.** The 0.075 s count and the `excursion_limited` label stay.
- **S6 — Simulation (k).**
  - Opus and Fable: already satisfied, since its B models are protocol-independent; 0/200 bounds the rate at ≈1.5 %, and the text must say so.
  - Sol and Astra: re-run it for the revised enrollment. Astra MATERIAL: the n = 12 block-drift case uses only the first block, and the W1 branch and all-member retention are untested.
  - **Proposal: re-run** the existing desk simulation extended to the revised tree (equivalence look → W1-as-member → W2/W3, all members retained), report the rates with their finite-sample bounds, and do not make a literal zero a release criterion. It is cheap desk work and closes Astra's M3.
- **S7 — Labels.** Sol: the measuring label and probe only; the renderer must split the dead-man. The other three: all three labels through the shared template, since the dead-man exists for timeliness. **Proposal: all three** (one template, one truth). The magistrate plist is unchanged (unanimous).
- **S8 — Revision number.** Opus calls it "Revision 4", because rev 4 was never sealed on main. The others say Revision 5. **Proposal: Revision 5**, whose STATUS states that Revision 4 (v4) was drafted, never sealed, and is held on `acc-v4-fallback`. This avoids two different texts called Revision 4. NIT.
- **S9 — PR shape.** Fable: one desk PR. Opus: two, the launch-context PR before the registration PR (BLOCKER: the registration must not name a context that is not installed). **Proposal: two PRs, ordered.** PR-L covers the templates, the installer refusal, the probe cadence phase and tests. PR-R covers Revision 5, the addenda, the salvaged validator and issuer, the F1 disposition, the simulation re-run and the equivalence-look seal. Each goes through the full-tier gate with a cold Fable final pass.
- **S10 — Fallback trigger for v4.** Any one of:
  - the probe cadence check fails twice with Interactive verified rendered;
  - the W1 cadence stop fires with Interactive verified;
  - `no_plateau_interior_intervals` failures appear despite verified Interactive ancestry;
  - a future OS build delivers a median above 150 ms under I.

  A baseline timeout alone triggers launch-context diagnosis, never v4 (Astra). v4 is reopened only through the council.

## 4. A rules-before-data note

The interactive seat's 150 ms "purpose-based" cure criterion replaced its registered ≤ 130 ms criterion after session 2's data, though before session C's (peer message, record 00 item 6). Every threshold proposed here (the 150 ms median, the 250 ms maximum, the < 6/12 stop) is fixed now, before any installed-agent capture exists, so the new path does not inherit that defect. The paper discloses the replacement.

## 5. Proposed order (replaces R-ACC-6)

1. PR-L, then PR #410 (the peer's), then PR-R, each with its full gate. PR-R merges only after PR-L.
2. Seal Revision 5, `protocol_v3.json` and the template digests. Arm W1 as the equivalence night through NIGHT_HANDBACK: notice, then the no-objection window. The probe cadence phase must PASS at install.
3. W1 runs agent-free with Wispr Flow quit. The in-window cadence stop applies.
4. One equivalence look:
   - PASS: the dated 25G83 continuation addendum PR, then r7 continues;
   - m < 6: one more equivalence night;
   - FAIL: W1 is a member, then W2 at least 6 h later, then count-only W3, then derivation, the cold science gate and successor issuance.
5. Regenerate the G2-a bindings with the rung check. At 0.132 s, five overlapping records need ≈0.66 s of prefill (Opus).
6. G2-a, then the calibration night per COUNCIL-407-01.

## 6. Plain summary for Ed (≤ 10 lines)

1. The slow sampling was never the new macOS. The night job was started with the scheduler's default "background" treatment, which lets the OS batch the sampler's wake-ups.
2. Marking the job "Interactive" gives ≈132 ms sampling, close to July's 120 ms. The original 1-second calibration pulses then pass with a wide margin, so the 2-second redesign is shelved as a fallback.
3. The installer will refuse a job without that setting, and every arm runs a short sampling check through the real machinery.
4. The first calibration night tests whether the July calibration still fits. If it does, that calibration continues. If it doesn't, that night becomes the first of two windows for a fresh one.
5. The 09-19 captures stay as diagnostics. They are formally set aside so the issuer can't be blocked by them.
6. Nothing needs you except the usual "reply NO" on the arm notice, and, when convenient, turning off automatic macOS updates.
