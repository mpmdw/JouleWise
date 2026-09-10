# D-079 identity-epoch 25G83 pre-registration — revision 1

STATUS: proposed default; Ed veto window open; fields in brackets are filled at commit before the first capture

Authority: cold gate 46 §R-c, amended by addendum 11 A-1–A-8 and paired
refutation 12; see the D-102 addendum dated 2026-09-10 in
`docs/decision_log.md`. This is the amended registration text, not an arm
authorization. V3 requires Ed's affirmative written acknowledgment before
the first capture's arm; silence is not consent. Re-label scientific defaults
ratified only on Ed's reply.

```text
STATUS: proposed default adopted by cold gate 46; Ed veto window open; V3 requires Ed's affirmative acknowledgment

Pre-registration: D-079 acceptance corpus for identity epoch 25G83 (rev 1, authored 2026-09-[DD], before any capture).

Epoch. {os_build: 25G83, hardware_model: Mac15,9, power_policy: ac_high_power, sampling_interval_ms: 100,
estimator_revision: joint_loss_sublevel_interval_branch_v2, pulse_protocol_id: powermetrics_pulse_fiducial_v3}.
The /usr/bin/powermetrics sha256 in force is b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5;
the MLX version in force is [MLX_VERSION]. A change to either voids this registration. An estimator-code rotation
mid-campaign also voids derivation captures.

Ledger baseline. Committed head pin sequence [SEQ] digest [DIGEST]. Each capture night is one derivation-kind ledger
session of 12 declared slots opened at head-equals-pin; the night never commits Git; the terminal pin candidate is
reviewed and committed at the desk before the next night opens.

Sample. Three agent-free [QUIET-MAC] windows on distinct calendar days, DIAGNOSTIC_NO_PACK class, chain digest [CHAIN_SHA256].
Each window: one 600 s settle after the last operator action, then 12 slots at a 600 s start-to-start cadence, fixed
order, no operator or agent present. Protocol powermetrics_pulse_fiducial_v3 unmodified; no parameter is tuned between
observations. A slot the window cannot reach is recorded unused by the session abort (reason window_exhausted), never
compressed or replaced. V3 requires Ed's affirmative written acknowledgment before the first capture's arm;
silence is not consent.

Classification. Each observation is written derivation-only under the active artifact d079_calibration_acceptance_v2_n17_r6
(authenticated bytes, protocol and estimator digests); the live epoch must differ and a derivation-kind session slot is
required. Its ledger disposition is valid or ordinary-invalid, including on recovery finalization. No systematic-invalid
disposition exists for this epoch. Whether the bound exceeds r6's preflight_level_screen_s
0.032898493715362 is recorded in the hashed evidence as a diagnostic only.

Membership. The corpus is every observation of this registration whose ledger disposition is valid and whose anchor-v3
replay from primary bytes resolves. No observation is excluded on the basis of its b_fiducial_s.
Every member carries the target epoch and belongs to a session of this registration. A valid same-epoch row outside
the registration refuses issuance rather than being absorbed. Valid registered prior-set rows excluded by replay are
listed in derivation_notes.excluded_members with the registered mechanism, member_id, manifest_sha256, and
instrument_evidence_sha256; the content ID matching the prior row is derived from those two hashes.

Exclusions (mechanism-named, outcome-independent, decided before capture). An observation is excluded only if (a) the
estimator's clock-anchor feasibility model refuses it on replay (affine_clock_fit_empty, the r6 exclusion class);
(b) a protocol gate fails (plateau, SNR, 59-pulse detection, spurious plateau, edge coverage), which the writer records
as ordinary-invalid; or (c) a recorded operator or system event interrupted the window. Every exclusion is recorded with
its named mechanism and its ledger row is retained. An estimator-code rotation also voids derivation captures.

Stopping. All three nights run all 12 declared slots regardless of interim values. Retained n >= 19 is required for
issuance: D-126 clause 2's SUCCESSOR_MINIMUM_CORPUS_SIZE = 19 is a corpus-size floor. Ed may instead rule n = 17
acceptable in writing; nothing issues below 19 without that written ruling. Fewer than 19 after three nights: not issued;
the shortfall is recorded. No top-ups, retries, early stops, or outcome-driven extra nights.

Blindness. No member value, screen, or statistic is examined by any person or agent before the third night's session is
terminal and its pin candidate is emitted.

Screen challenge. If two or more retained members exceed 0.032898493715362, the corpus is not issued and Ed rules in
writing before any further capture. Second diagnostic, recorded: the new maximum exceeds r6's maximum plus r6's range,
0.04262208300415633 (Decimal sum of 0.03289849371536248 and 0.00972358928879385). Neither diagnostic edits membership.

Analysis. Decimal statistics exactly as r6: minimum, maximum, range, mean, sample SD; t(0.975, n-1) and t(0.995, n-1)
two-draw predictions with the quantile implementation proven for both df 18 and df 19; the full D-125 envelope for
bracket screen S and budget ceiling C: S = max(range quantized to 1e-6 s ROUND_HALF_EVEN, 0.010818) AND
C = max(inherited ceiling, new Q99), where Q99 is the new 99 % two-draw prediction. The generation carries its inherited
ceiling and explicit d125_ruling reference; issuance refuses without that reference or when S >= C
(successor_screen_exceeds_budget_ceiling). Preflight level screen = maximum quantized to 1e-15 s;
maximum budgetable drift = C; cap = C - S, without a silent clamp. Per-night distribution, order, exclusions, and clock
residual margins are reported as diagnostics that authorize no trimming.

Prospective use. The resulting acceptance judges only subsequent ordinary captures. Bootstrap observations are corpus
members and never bracket endpoints. No G2-a, floor, or claim output is an input to this derivation. The successor's
ledger_cutoff is the authenticated head after the last bootstrap row; its prior set is the complete history through it,
including finalized observations from abort-closed sessions. Pending or unresolved attempts refuse issuance.
D-102 clause 2 is preserved: a trigger observation is judged under the PRIOR artifact, never incorporated into a
threshold that judges itself. Nothing in this registration licenses G2-a or weakens a physics or evidence refusal.
```
