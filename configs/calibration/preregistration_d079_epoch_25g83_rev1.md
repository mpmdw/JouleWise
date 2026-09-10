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
- **Anchor-v3 replay** — reading a capture's STORED anchor-v3 outcome back
  out of its primary evidence bytes; not recomputing it. The anchor-v3
  estimator runs inside the writer at capture time and records its result —
  the `clock_anchor` record and the fiducial bound — in that capture's
  `instrument_evidence.json`. Cold gate 46 §R-d settles that for a capture
  taken fresh under anchor-v3 the stored result IS the derivation
  (`stored_lexeme_is_member_value: True`), so the issuer authenticates those
  bytes instead of repeating the fit: both `manifest.json` and
  `instrument_evidence.json` must hash (SHA-256) to the digests the ledger row
  recorded before any field is read, and the stored `b_fiducial_s` (the
  capture's fiducial bound in seconds, next bullet) must equal the row's
  `exact_bound_lexeme_s`. Any one of the three mismatching refuses. A capture whose
  stored `clock_anchor` shows the clock-anchor feasibility model admitted no
  feasible affine fit did not resolve (`affine_clock_fit_empty`) and is
  excluded, listed with that mechanism; a `clock_anchor` recorded under any
  method other than anchor-v3 is not an anchor-v3 replay at all and refuses
  rather than counting as resolved. Where a value IS recomputed from primary
  bytes is historical and not this registration: the r-series (n = 17)
  generations SUPERSEDED the scalars their bundles had stored with values
  re-derived offline from primary bytes under the rate-aware set-membership
  estimator — which is why `tests/verify_calibration_acceptance_corpus.py`
  banks `stored_lexeme_is_member_value: False` for those generations, and
  `True` for a generation whose captures store their own anchor-v3 result, as
  this registration's do.
- **`b_fiducial_s`** — the capture's fiducial bound in seconds: the value a
  corpus member contributes to the statistics.
- **`DIAGNOSTIC_NO_PACK`** — the night receipt class for a night that runs no
  measurement pack. It requires a registration path and marks only the pack
  ARM condition (C2) not-applicable; the transaction-authorization,
  quiet-census, boot/clock, and no-retry conditions must still pass.
- **Level screen** — an acceptance's corpus maximum, the preflight threshold a
  capture's bound is compared against. **Bracket screen (S)** — its corpus
  range. **Budget ceiling (C)** — its maximum budgetable drift. **t(p, df)** — the
  two-sided Student-t quantile: the multiple of an estimated standard
  deviation that a t-distributed quantity stays within in absolute value with
  probability p, when the estimate carries df degrees of freedom (df = n − 1
  for a corpus of n members). **Two-draw prediction** — t(p, n−1) × sample SD
  × √2, the half-width that predicts how far apart two fresh draws from the
  same population fall at confidence p. **Q99** — the two-draw prediction at
  p = 0.995, computed from a corpus. **Predecessor ceiling** — the
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

Membership. The corpus is every observation of this registration whose ledger disposition is valid and whose STORED
anchor-v3 outcome, read back from hash-authenticated primary bytes, resolves (glossary: Anchor-v3 replay — the issuer
reads the recorded clock_anchor and authenticates the bytes; it does not re-run the estimator over the trace). No
observation is excluded on the basis of its b_fiducial_s. Every member carries the target epoch and belongs to a
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

Stopping. All three nights run all 12 declared slots regardless of interim values. Retained n >= 19 is REQUIRED for
issuance: D-126 clause 2's SUCCESSOR_MINIMUM_CORPUS_SIZE = 19 is a corpus-size floor, not the 0.010818 screen floor.
Ed may instead rule in writing that n = 17 is acceptable; nothing issues below 19 without that written ruling. Fewer
than 19 retained after the third night: not issued, with the shortfall recorded; any further capture is Ed's written
ruling, not this registration's. No top-ups, retries, early stops, or outcome-driven extra nights.

Blindness. No member value, screen, or statistic is examined by any person or agent before the third night's session is
terminal and its pin candidate is emitted. The fence is installed by the issuer, not left to convention. prepare-candidate
refuses to run while any session named in the registration is not terminal — terminal meaning its last declared slot is
final or the session was aborted — and names the session it found open, so the statistics cannot be computed early even
by accident. check's registration dry run, the one route that may be run mid-campaign, reports only the named sessions'
kinds and states, how many slots are declared and how many are filled, and how many observations are excluded under each
named mechanism; it reports no member value, no screen, no statistic, and no comparison against one. A mid-campaign look
can answer whether the campaign is on schedule and cannot answer what the campaign got.

Screen challenge. If two or more retained members exceed 0.032898493715362, the corpus is not issued and Ed rules in
writing before any further capture. Second diagnostic, recorded: whether the new maximum exceeds r6's maximum plus r6's
range, 0.04262208300415633 (the Decimal sum of 0.03289849371536248 and 0.00972358928879385). Neither diagnostic edits
membership.

Analysis. Decimal statistics exactly as r6: minimum, maximum, range, mean, sample SD; t(0.975, n-1) and t(0.995, n-1)
two-draw predictions (both terms defined in the glossary above). The three-night schedule admits retained n from 19
(the required floor) to 36 (all declared slots retained), so the degrees of freedom n-1 run from 18 to 35 — or from 16
if Ed's written n = 17 ruling is exercised; the quantile implementation's proof for the REALIZED df is computed and
recorded before issuance, and no corpus issues on a df whose quantile is not proven in that record.

Quantile proof, mechanically, so that an authority-side reader can find it. For each of the two probabilities 0.975 and
0.995, at 80-digit Decimal working precision, the issuer runs two checks on the quantile it returns for the realized df.
(a) Forward check: the Student-t survival function P(T > t) — computed from the regularized incomplete beta function by
continued fraction — evaluated AT the returned quantile must reproduce 1 - p, with absolute residual at most 1e-30.
(b) Independent route: the same quantile is produced a second time by a route sharing no code with (a). That route is the
exact Abramowitz and Stegun finite closed form for P(|T| <= t) at integer df (26.7.3 for odd df, 26.7.4 for even df),
inverted by its own bisection over t in (0, 100) — 300 halvings, which resolves t to about 1e-88, far finer than the
working precision needs — with pi computed independently by Machin's formula rather than taken from a library. The two
quantiles must agree to at least 30 significant decimal digits. Both routes' evidence is recorded in the candidate's
quantile_proof block: the quantiles at 20 decimal places, the per-probability forward residuals, the per-probability
agreement digit counts, both bounds, the closed-form method string, and the working precision. A miss on either check
refuses quantile_proof_failed and nothing issues, and the proof runs before the predictions are computed, so no corpus
reaches issuance on an unproven df.

Those two bounds — residual at most 1e-30, agreement at least 30 significant digits — are the ISSUER'S DECLARED bounds,
not a ratified constant, and they are stated here so the authority-side record carries them rather than only the code and
its output. Each is chosen conservative against the 20 decimal places at which the artifact publishes a quantile. For a
quantile of order 2 to 3, agreement to 30 significant digits is agreement to about 29 decimal places, nine more places
than are printed. The forward residual is a residual in PROBABILITY, not in t: near these quantiles the one-tail density
is of order 0.05 (p = 0.975) down to 0.01 (p = 0.995) per unit t, so a probability residual of 1e-30 corresponds to an
error of order 1e-29 to 1e-28 in t, at least eight orders of magnitude below the last published place. A quantile that
passes both checks therefore cannot be wrong in any digit the artifact prints. The realized residuals and digit counts
are recorded when the corpus closes; they are not predicted here.
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
