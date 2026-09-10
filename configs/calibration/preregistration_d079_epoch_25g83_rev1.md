# D-079 identity-epoch 25G83 pre-registration — revision 1

STATUS: proposed default; Ed veto window open; fields in brackets are filled at commit before the first capture

Authority: cold gate 46 §R-c, as amended by its dated addendum 11 (A-1–A-8)
and the paired contract refutation 12; recorded as the dated addendum under
D-102 in `docs/decision_log.md`. This file is the registration text, not an
arm authorization: it authorizes no window and licenses no measurement. The
scientific rules below are proposed defaults that Ed may veto or amend by
reply or directive issue, and are re-labelled ratified only on Ed's reply.
V3 — the night count, slots per night, and retained-corpus minimum —
additionally requires Ed's affirmative written acknowledgment before the first
capture's arm; silence is not consent for V3.

## Why this registration exists

An issued **acceptance** is the artifact whose corpus statistics set the
thresholds every later calibration capture is judged against. It binds an
**identity epoch**: the six-field vector {`os_build`, `hardware_model`,
`power_policy`, `sampling_interval_ms`, `estimator_revision`,
`pulse_protocol_id`}. When any field changes, the artifact goes stale by
design (D-102 clause 2) and ordinary capture refuses. The machine's `os_build`
moved from `25F84` to `25G83`, so the issued
`d079_calibration_acceptance_v2_n17_r6` now refuses every ordinary capture and
no threshold exists for the new epoch.

A new acceptance needs a corpus of new-epoch observations, but those
observations must be captured before any acceptance of their own epoch exists
to judge them. That is what this registration governs, and why it is written
before any data: every rule that could otherwise be chosen after seeing values
is fixed here first.

## Terms used below

- **Observation** — one 59-pulse calibration capture, written to the ledger as
  a reservation receipt followed by a finalization receipt.
- **Head pin** — the repository-committed file naming the receipt count and
  last digest that consumers trust. **Head-equals-pin** means the physical
  ledger head matches it exactly.
- **Session** — a ledger capability reserving several attempts under one open
  receipt while the committed head pin stays put. A **slot** is one declared,
  ordered place for an attempt inside a session. A `derivation`-kind session
  is the only route for the captures below.
- **Derivation-only capture** — an observation taken to build a future
  acceptance, never to license a measurement.
- **Prior set** — the acceptance's list of every ledger observation through
  its cutoff receipt. **Corpus** — the subset of the prior set whose values
  the statistics are computed from. **Retained n** is the corpus size.
- **Anchor-v3 replay** — re-deriving a capture's fiducial bound from its
  primary evidence bytes with the anchor-v3 estimator. A capture whose
  clock-anchor feasibility model admits no feasible affine fit does not
  resolve (`affine_clock_fit_empty`) and cannot be a corpus member.
- **`b_fiducial_s`** — the capture's fiducial bound in seconds: the value a
  corpus member contributes to the statistics.
- **`DIAGNOSTIC_NO_PACK`** — the night receipt class for a night that runs no
  measurement pack. It requires a registration path and marks only the pack
  ARM condition (C2) not-applicable; the transaction-authorization,
  quiet-census, boot/clock, and no-retry conditions must still pass.
- **Level screen** — an acceptance's corpus maximum, the preflight threshold a
  capture's bound is compared against. **Bracket screen (S)** — its corpus
  range. **Budget ceiling (C)** — its maximum budgetable drift. **Q99** — the
  99 % two-draw prediction computed from a corpus. **Predecessor ceiling** — the
  predecessor generation's budget ceiling.

Why three nights of twelve slots, stated before capture: at the historical
valid rate 30/38 and r6's replay-retention ratio 17/19, two nights of 12 slots
project 24 × (30/38) × (17/19) = 16.95 retained observations, below the
required 19; three nights project 25.4. The schedule fits a 210 min window
with margin: one 600 s settle + 11 × 600 s cadence + one ~8 min capture is
128 min.

## Registration text

```text
STATUS: proposed default adopted by cold gate 46, Ed veto window open; V3 requires Ed's affirmative acknowledgment

Pre-registration: D-079 acceptance corpus for identity epoch 25G83 (rev 1, authored 2026-09-[DD], before any capture).

Epoch. {os_build: 25G83, hardware_model: Mac15,9, power_policy: ac_high_power, sampling_interval_ms: 100,
estimator_revision: joint_loss_sublevel_interval_branch_v2, pulse_protocol_id: powermetrics_pulse_fiducial_v3}.
The /usr/bin/powermetrics sha256 in force is b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5;
the MLX version in force is [MLX_VERSION]. A change to either voids this registration, and so does an
estimator-code rotation mid-campaign.

Ledger baseline. Committed head pin sequence [SEQ] digest [DIGEST]. Each capture night is one derivation-kind ledger
session of 12 declared slots opened at head-equals-pin; the night never commits Git; the terminal pin candidate is
reviewed and committed at the desk before the next night opens.

Sample. Three agent-free [QUIET-MAC] windows on distinct calendar days, DIAGNOSTIC_NO_PACK class, chain digest
[CHAIN_SHA256]. Each window: one 600 s settle after the last operator action, then 12 slots at a 600 s start-to-start
cadence, fixed order, no operator or agent present. Protocol powermetrics_pulse_fiducial_v3 unmodified; no parameter is
tuned between observations. A slot the window cannot reach is recorded unused by the session abort (reason
window_exhausted), never compressed or replaced.

Classification. Each observation is written derivation-only under the active artifact d079_calibration_acceptance_v2_n17_r6
(authenticated bytes, protocol digest, estimator-code digest); the live identity epoch must differ from that artifact's,
and a derivation-kind session slot is required. Its ledger disposition is valid or ordinary-invalid, on every
finalization path including recovery after a crash. No systematic-invalid disposition exists for this epoch, because no
acceptance of this epoch exists. Whether the bound exceeds r6's preflight_level_screen_s 0.032898493715362 is recorded
in the hashed evidence as a diagnostic only.

Membership. The corpus is every observation of this registration whose ledger disposition is valid and whose anchor-v3
replay from primary bytes resolves. No observation is excluded on the basis of its b_fiducial_s. Every member carries
the target epoch and belongs to a session of this registration; a valid same-epoch observation outside this registration
refuses issuance rather than being absorbed. Valid registered observations excluded by replay are listed in
derivation_notes.excluded_members with their named mechanism, member_id, manifest_sha256 and instrument_evidence_sha256;
the prior-set row is matched by the content id derived from those two hashes.

Exclusions (mechanism-named, outcome-independent, decided before capture). An observation is excluded only if (a) the
estimator's clock-anchor feasibility model refuses it on replay (affine_clock_fit_empty, the r6 exclusion class);
(b) a protocol gate fails (plateau, SNR, 59-pulse detection, spurious plateau, edge coverage), which the writer records
as ordinary-invalid; or (c) a recorded operator or system event interrupted the window. Every exclusion is recorded with
its named mechanism and its ledger row is retained.

Stopping. All three nights run all 12 declared slots regardless of interim values. Retained n >= 19 is REQUIRED for
issuance: D-126 clause 2's SUCCESSOR_MINIMUM_CORPUS_SIZE = 19 is a corpus-size floor, not the 0.010818 screen floor.
Ed may instead rule in writing that n = 17 is acceptable; nothing issues below 19 without that written ruling. Fewer
than 19 retained after the third night: not issued, with the shortfall recorded; any further capture is Ed's written
ruling, not this registration's. No top-ups, retries, early stops, or outcome-driven extra nights.

Blindness. No member value, screen, or statistic is examined by any person or agent before the third night's session is
terminal and its pin candidate is emitted.

Screen challenge. If two or more retained members exceed 0.032898493715362, the corpus is not issued and Ed rules in
writing before any further capture. Second diagnostic, recorded: whether the new maximum exceeds r6's maximum plus r6's
range, 0.04262208300415633 (the Decimal sum of 0.03289849371536248 and 0.00972358928879385). Neither diagnostic edits
membership.

Analysis. Decimal statistics exactly as r6: minimum, maximum, range, mean, sample SD; t(0.975, n-1) and t(0.995, n-1)
two-draw predictions. The three-night schedule admits retained n from 19 (the required floor) to 36 (all declared
slots retained), so the degrees of freedom n-1 run from 18 to 35 — or from 16 if Ed's written n = 17 ruling is exercised; the quantile implementation's proof for the REALIZED
df is computed and recorded before issuance, and no corpus issues on a df whose quantile is not proven in that record.
The full D-125 envelope governs both operatives: bracket screen
S = max(new range quantized to 1e-6 s ROUND_HALF_EVEN, 0.010818) AND budget ceiling C = max(predecessor ceiling,
new Q99). The generation records the predecessor ceiling and an explicit d125_ruling
reference; issuance refuses while that reference is absent, and refuses successor_screen_exceeds_budget_ceiling when
S >= C. Maximum budgetable drift = C; maximum budgetable excess = C - S, with no silent clamp at zero.

Halt on S >= C. If S >= C on any route, D-126 clause 3's successor_screen_exceeds_budget_ceiling refusal fires: the
corpus is not issued, and Ed rules in writing before any further capture, exactly as for the screen challenge. The
refusal is never cured by lowering S. The route to watch: if the new Q99 is at or below the 0.010818 screen floor, the
predecessor ceiling 0.010164834757777545 cannot rescue C > S, because S is never below the floor.

Preflight level screen = the new corpus maximum quantized to 1e-15 s. Per-night distribution, order, exclusions, and
clock residual margins are reported as diagnostics that authorize no trimming.

Prospective use. The resulting acceptance judges only subsequent ordinary captures. Derivation observations are corpus
members and never bracket endpoints, before or after issuance. No G2-a, floor, or claim output is an input to this
derivation. The successor's ledger_cutoff is the authenticated head after the last derivation row; its prior set is the
complete history through it, including finalized observations of abort-closed sessions, and a pending or unresolved
attempt in that prefix refuses issuance. D-102 clause 2 is preserved: a trigger observation is judged under the PRIOR
artifact, never incorporated into a threshold that judges itself. Nothing in this registration licenses a measurement
window or weakens a physics or evidence refusal.
```

## Fields filled at commit

`[DD]` (authoring day), `[MLX_VERSION]`, `[SEQ]` and `[DIGEST]` (the committed
head pin at the first night's open), and `[CHAIN_SHA256]` (the capture chain's
digest). Each is a fact that does not exist yet; none is a scientific choice,
and filling them does not reopen any rule above.
