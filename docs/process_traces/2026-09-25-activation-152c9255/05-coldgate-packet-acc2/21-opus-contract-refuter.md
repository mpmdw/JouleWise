# Refuter report: CONTRACT lens on the magistrate synthesis (ACCEPTANCE-25G83-02)

**Packet:** `00-charge.md`, sha256 e3803203… (verified). **Target:** `ex-30-synthesis.md`. I only read files. I ran nothing that needs sudo, launchd or powermetrics. The raw n1/n2 B values below come from the evidence files under `/Users/edr/night-archive/`, which the charge allows.

**Totals:** 2 BLOCKER, 4 MATERIAL, 3 NIT.

---

## B1 — BLOCKER (F1 × S1): a PASS would leave r7 stale the moment it continues, and the D-126 disposal has no code behind it

**Facts:**
- **D-126 Q5 needs code that does not exist yet.** It says an observation stops being "new" only through two things: an explicit disposal in the decision log by content id, *plus* "the next successor's prior_observation_set recording the disposing decision ID; consuming code lands with the first disposing ruling, not before" (`docs/decision_log.md:8492-8498`). Nothing in `joulewise/` or `scripts/` reads such a disposal.
  - The issuer's A-7 foreign-row check filters only on `classification_disposition == "valid"` (`scripts/issue_calibration_acceptance_generation.py:1279-1291`).
- **The PASS branch has no successor, so there is no prior set to record the disposal in.** r7 continues, and r7's `prior_observation_set` is byte-pinned. Astra's "existing mechanism" therefore cannot be applied on PASS without new code.
- **After a PASS, 25G83 becomes one of r7's judged epochs** (`calibration_epoch_continuation.py:348-364`, consumed at `calibration_bracketing.py:2073-2087`). The trigger code then checks every live observation that is not in r7's prior set (`:2344-2360`).
  - **Only W1's rows are exempt.** The exemption is the continuation's `acknowledged_attempt_ids` (`:2383-2386`); n1/n2 are not acknowledged.
  - n1/n2 are derivation sessions, so the ledger stores them as `valid` (`calibration_ledger.py:5975-5980, 6090-6097`).
  - **9 of their 11 valid B values fall outside r7's corpus range [0.023175, 0.032898].** The values are 0.03488, 0.03558, 0.03690, 0.04103, 0.04113, 0.04200, 0.04337, 0.13333 and 0.17271, against r7's corpus maximum of 0.03289849.
  - These fire `new_valid_same_identity_capture_expands_observed_range` (`:2386-2399`). That is one of the stale triggers (`:2527-2545`), so **every claim window refuses `calibration_acceptance_bound_stale`**.
- **The same 11 rows count toward the corpus-doubling trigger** (`:2370-2378`, 17→34). They use up about 11 of the 34-row headroom before any claim window runs.
- **Consequence:** §5 step 4 ("PASS: the dated continuation addendum, then r7 continues") cannot execute. The continuation would authenticate, and r7 would then be stale on arrival.

**Corrected F1 text:**
> F1. The n1/n2 rows of 2026-09-19 (content ids listed) are disposed under D-126 Q5 by a new dated decision-log entry. Mechanism: "captured under default-ProcessType launch context", disclosed as written after the values were seen.
>
> D-126's "consuming code lands with the first disposing ruling" is met in PR-R by one disposal registry. Three code sites read it:
> - (i) the issuer's A-7 foreign-row check (`issue_calibration_acceptance_generation.py:1279-1291`);
> - (ii) the range-expansion and corpus-doubling trigger evaluation (`calibration_bracketing.py:2344-2399`);
> - (iii) the systematic-trigger filter at the same site.
>
> On FAIL, the successor's `prior_observation_set` records the disposing decision id. On PASS, the continuation file records it; r7's prior set is untouched.
>
> PR-R carries counterfactual tests on today's ledger rows: with the registry emptied, (i) refuses A-7 and (ii) returns stale; with the registry present, neither happens.

---

## B2 — BLOCKER (U4 / U8 / S4): the salvaged v4 issuer and validator are keyed to v4 and would refuse or misapply on main

**Facts:**
- **On the branch, every Revision-4 path is gated on `PROTOCOL_ID`, which the branch changed to v4** in the pinned `powermetrics_fiducial.py`. On main it is still `"powermetrics_pulse_fiducial_v3"` (`joulewise/powermetrics_fiducial.py:44-45`). The branch issuer gates on:
  - `revision_four = target_epoch["pulse_protocol_id"] == PROTOCOL_ID`;
  - the text test `"# Revision 4 (2026-09-24" in text and "powermetrics_pulse_fiducial_v4" in text`;
  - `raise PrepareRefusal("v4 identity requires sealed registration Revision 4")`.
- **Salvaged verbatim onto main, the issuer would refuse the Revision-5 registration.** The 25G83/v3 target matches `PROTOCOL_ID`, and the Revision 4 header is absent. If the text test were simply deleted instead, the protocol-only key would also switch the n ≥ 12 and zero-headroom rules on for historical v3 epochs such as 25F84.
- **The salvaged validator would touch the D-138 pin set.** It imports `PROTOCOL_V3_ID` from `joulewise/powermetrics_fiducial.py`, which does not exist on main. Adding it edits a pinned file and stales r7 (`decision_log.md:10361-10375`). It also carries `_registered_protocol_pin_matches` and `R8_ACCEPTANCE_ID`, which exist only for the r8 reissue.
- **The futility threshold conflicts with S4.** The branch issuer hard-codes `if w1_valid < 8: raise PrepareRefusal("W1 futility procedure violation…")`. Under S4's "< 6/12", a W1 with 6 or 7 valid rows legitimately opens W2, and the salvaged issuer would then refuse the derivation.
- **"Screen challenge (g) stays dropped" is wrong.** The challenge is live on main (`issue_calibration_acceptance_generation.py:1298-1303`; prereg `:188-190`). Only the unsealed v4 branch dropped it.
- **The D-125/D-126 addenda texts on the branch** say "epoch 25G83/v4 under registration rev 4".

**Corrected U4 salvage clause:**
> Salvage these as re-keyed code, not verbatim. Every `revision_four` predicate in the issuer and the validator becomes an exact six-field tuple match on {25G83, Mac15,9, ac_high_power, 100, joint_loss_sublevel_interval_branch_v2, `PROTOCOL_ID` (v3 on main)}, and the registration must contain `# Revision 5 (`.
>
> Do not import or add `PROTOCOL_V3_ID`. Do not salvage `_registered_protocol_pin_matches` or `R8_ACCEPTANCE_ID`.
>
> The W1 futility check in the issuer uses 6, not 8.
>
> The D-125 and D-126 addenda are re-issued with the text "epoch 25G83/v3 under registration Revision 5", citing this ruling.
>
> PR-R's gate includes `git diff --quiet origin/main -- joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py`.

**Corrected U8 (g):**
> (g) The screen challenge at prereg `:188-190` and at the issuer's `:1298-1303` is newly dropped for this epoch by Revision 5, as a diagnostic only.

---

## M1 — MATERIAL (S1): Revision 5 must say which registration text it amends

**Facts:**
- **Revision 2's FAIL branch** is "revision 1's, entire and unamended": three nights, n ≥ 19, and "No top-ups, retries, early stops" (prereg `:474-488`, `:173-177`).
- **The synthesis's §5 FAIL branch uses the v4 shape instead:** W2 at least 6 h later, a count-only W3, n ≥ 12, and a < 6/12 stop. Nowhere does it state that Revision 5 amends revision 2's FAIL branch or revision 1's Stopping section, and it does not carry ex-31's R-ACC-4 authority line.
- **The "FAIL night counts as W1" claim itself holds.** The text is at `:477`.
- **The INCONCLUSIVE branch is unsealed.** An extra equivalence night leaves valid 25G83 rows in a session:
  - if the registration does not name it, A-7 refuses (`issuer :1279-1291`);
  - if the registration does name it, the session count leaves {2, 3};
  - its rows are not acknowledged by a PASS on the next night, so B1's stale trigger applies to them too.
- **Revision 2 names r6 as the acceptance in force** (`:343-345`, `:445`). The acceptance in force is r7. I verified the operatives are identical: 0.032898493715362 / 0.009724 / 0.010164834757777545.

**Corrected text to append to S1:**
> Revision 5 states that it amends revision 2's FAIL branch and revision 1's Stopping section for this epoch, quoting the D-184 addendum (`decision_log.md:12174-12175`) as its authority.
>
> An INCONCLUSIVE equivalence night is a registration session. If the next night FAILs, both are named, in ledger order, as W1a and W1b; the issuer admits {3, 4} sessions for that path, and there is no count-only W3. If the next night PASSes, the continuation acknowledges both nights' attempt ids.
>
> Wherever revision 2 says "r6" as the acceptance in force, read `d079_calibration_acceptance_v2_n17_r7`, whose operatives are identical.

---

## M2 — MATERIAL (S4 / S9 / §5): where the in-window cadence stop lives decides whether PR-L can merge

**Facts:**
- **Revision 3 pins the chain digest** (prereg `:545`). `tests/test_preregistration_chain_digest.py` requires exactly one `Chain digest in force (revision 3):` line, and it must equal the digest of `scripts/night_chains/calibration_derivation_only.zsh`. The t0 gate also refuses `night_chain_digest_mismatch`.
- **If the "in-window" stop edits the chain, PR-L cannot come before PR-R.** Either main's test breaks, or PR-L has to carry a registration edit.
- **Revision 1 forbids early stops** (`:173-177`).
- **Revision 1 lists exactly what the check dry run may report** (`:183-186`). A cadence field is not on that list.

**Corrected S4 text:**
> The W1 cadence stop is read at W1 harvest, after the session is terminal. It is evaluated by a pin-free check script on the median of the per-capture median native frame lengths. If that exceeds 150 ms: no W2, and the question returns to the council.
>
> The derivation chain is unchanged and revision 3's chain digest stands.
>
> Revision 5 adds "median native frame length" to the check dry run's permitted outputs.
>
> §5 step 3 is amended: delete "in-window" and replace it with "at harvest".

---

## M3 — MATERIAL (U6): PR #410 does not relocate the W1 clone

**Facts:**
- **PR #410 changes only `evidence_night.locations`,** whose `KIND` is `quiet_predicate_evidence` (`joulewise/evidence_night.py:28`; branch `origin/fix/2026-09-25-measurement-clone-spotlight`, diff at `:166-176`).
- **Derivation nights use hand-chosen roots** such as `/Users/edr/JouleWise-measurement-20260919-derivation` (`docs/process/NIGHT_HANDBACK.md:954, :981`). Those sit outside `~/night-custody` and so outside the Spotlight exclusion.
- As written, "PR #410 lands before W1" does not protect W1 at all.

**Corrected U6 bullet 1:**
> W1's `measurement_root` is placed under `/Users/edr/night-custody/measurement/`, and the arm record verifies it. PR-L applies this to the derivation plan path. PR #410's landing is required for evidence nights only.

---

## M4 — MATERIAL (S2): the probe exists, but it checks the probe's template, not the night job's

**Facts:**
- **`_probe_worker` exists** (`scripts/run_night.py:3681`). It is a verify-only run (`NIGHT_VERIFY_ONLY=1`, `:3714`), so today it starts no powermetrics.
- **It runs under the probe template** (`configs/launchd/com.joulewise.night-probe.plist.template`, rendered at `joulewise/night_agent_install.py:965-977`). The night job and the dead-man render from `com.joulewise.night.plist.template` (`:616-626`).
- **So the probe phase cannot catch a regression in the night template.** The synthesis's claim that it "catches template regressions for the life of the cure" holds only for the probe template. The night template is covered by the static refusal in U2 and by the W1 harvest stop.
- **Adding `sudo -n powermetrics` to the probe has knock-on changes:**
  - the probe receipt's schema changes, which `validate_probe_receipt` (`:793-`) has to accept;
  - the survivor check (`:980-993`) has to cover the sudo child;
  - it runs at install time with the magistrate session live, while the thresholds were fixed on quiet data.

**Corrected S2 proposal:**
> Opus's probe phase is adopted as a check that the OS delivers the Interactive cadence under the probe label. PASS: median ≤ 150 ms and zero intervals > 0.25 s.
>
> The installer additionally refuses unless the parsed `ProcessType` of the rendered probe payload equals that of the rendered night and dead-man payloads.
>
> The receipt schema bumps to v2, `validate_probe_receipt` requires the cadence fields, and the survivor check covers the powermetrics process group.
>
> Night-template regressions are caught by U2 and the W1 harvest stop, not by the probe.

---

## N1 — NIT (U2): parse the rendered value, don't search the template text

The KeepAlive refusal at `night_agent_install.py:1091-1092` is a raw substring check on template text. Copied as-is, it would pass `<string>Background</string>`.

**Corrected text:**
> U2: refuse unless `plistlib.loads(rendered)["ProcessType"] == "Interactive"` for each rendered night, dead-man and probe payload. Tests cover a missing key, `Background`, `Standard` and `Adaptive`.

## N2 — NIT (S7): there are two templates, not one

The night job and dead-man share `com.joulewise.night.plist.template` (`LABELS`, `:39`); the probe has its own template. Replace "(one template, one truth)" with "(night and dead-man share one template; the probe template carries the same key, cross-checked per M4)".

## N3 — NIT (§0, S1): the PASS comparator is the quantized screen, and a PASS covers only W1

- The PASS comparators come from the acceptance's ratified operatives (`calibration_epoch_continuation.py:67-82`). The level screen is 0.032898493715362, which is r6's corpus maximum 0.03289849371536248 quantized — slightly below it. **Corrected §0:** replace "(r6's corpus maximum)" with "(the acceptance's ratified level screen, r6's corpus maximum quantized to 1e-15)".
- S1's "continuing r6 bounds everything observed" is true of W1 only. Later bracket captures at 132 ms are still judged against r7's corpus range and screens (`calibration_bracketing.py:2386-2407`). **Add to S1:** "Opus's regime objection moves to after the PASS: any later bracket B outside [0.023175, 0.032898] triggers rederivation. The paper discloses this."

---

## Answers to the other priority checks

- **U1 thresholds:** confirmed. The idle-baseline timeout is 55 s for 300 samples (`adapters/powermetrics.py:1468-1470`), which means any median above 183 ms fails. The interior is [on + 0.25, off − 0.25] (`powermetrics_fiducial.py:751-761`).
- **U4 / `reduce.py`:** correct to exclude it. The D-138 pin set is the four files listed in r7's `estimator_code_sha256`, and none of the salvage list is in it, *provided* B2's `PROTOCOL_V3_ID` import is removed.
- **S9 order:** sound only once M2 and M3 are applied. With the stop read at harvest, PR-L touches no pinned or registered bytes. PR-R must carry B1's registry and tests, and the re-keyed code from B2.
