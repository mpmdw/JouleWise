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
required 19; three nights project 25.4.

Three different durations govern one night, and confusing them is how a night
opens a session it cannot finish, so all three are stated here.

- **Programmed span — 7680 s (128 min).** What the capture chain actually
  runs: one 600 s settle after the last operator action, then eleven 600 s
  start-to-start slot gaps, then one 480 s capture budget for the twelfth
  slot. 600 + 11 × 600 + 480 = 7680.
- **Generator minimum — 7980 s (133 min).** The night wrapper generator
  `scripts/gen_derivation_night.py` refuses to emit a wrapper unless the
  plan's `window_max_s` is at least the programmed span plus a 300 s
  pre-settle allowance (7680 + 300 = 7980). The allowance exists because the
  settle clock starts at the chain's own start, and a window that held only
  the programmed span exactly would abort its last slot
  `window_exhausted` on any start-up delay.
- **Recommended `window_max_s` — 9000 s (150 min).** The value these nights
  are armed with: it clears the 7980 s minimum by 1020 s, absorbing a slow
  capture or a late start without touching the schedule. The generator
  separately refuses when `t0 + window_max_s + 300 s` (a courier allowance
  for the night's own closing work) is not before the next local 07:00.

`window_max_s` is the plan field naming the window's length in seconds; the
window ENDS at `t0 + window_max_s`, and the chain will not start a slot it
cannot finish inside that end.

The figure 210 min, which earlier drafts attached to the window, is not a
window at all: it is the install span 03:00–06:30 — the operator-facing block
of the clock inside which a night is scheduled. A 150 min window fits inside
a 210 min install span with an hour to spare; the two numbers measure
different things and neither is derived from the other.

## Registration text

```text
STATUS: proposed default adopted by cold gate 46, Ed veto window open; V3 requires Ed's affirmative acknowledgment

Pre-registration: D-079 acceptance corpus for identity epoch 25G83 (rev 1, authored 2026-09-10, before any capture).

Epoch. {os_build: 25G83, hardware_model: Mac15,9, power_policy: ac_high_power, sampling_interval_ms: 100,
estimator_revision: joint_loss_sublevel_interval_branch_v2, pulse_protocol_id: powermetrics_pulse_fiducial_v3}.
The /usr/bin/powermetrics sha256 in force is b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5;
the MLX version in force is 0.31.2. A change to either voids this registration, and so does an
estimator-code rotation mid-campaign.

Ledger baseline. Committed head pin sequence 76 digest 08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7. Each capture night is one derivation-kind ledger
session of 12 declared slots opened at head-equals-pin; the night never commits Git; the terminal pin candidate is
reviewed and committed at the desk before the next night opens.

Sample. Three agent-free [QUIET-MAC] windows on distinct calendar days, DIAGNOSTIC_NO_PACK class, chain digest
b8bf5b0a85bb2012eed9763f70743963d6f24c3ec3038142525766c00f1ac8cf. Each window: one 600 s settle after the last operator action, then 12 slots at a 600 s start-to-start
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
two-draw predictions (both terms defined in the glossary above). The two-draw predictions are the one step that leaves
exact decimal arithmetic, and Q99 is the number that sets the successor's budget ceiling C, so the arithmetic is declared
here, before the corpus exists, in the issuer's own sealed words (the string TWO_DRAW_PREDICTION_RULE, quoted verbatim
because it is hashed into the derivation and a paraphrase would change the digest of an otherwise identical derivation):
"prediction_p_two_draw_s = t(p, n-1) * sample_sd_presentation_s * sqrt(2), evaluated in binary64 and recorded as its
shortest round-tripping decimal". Binary64 is the IEEE 754 double-precision binary floating-point format (Python's
float), which carries about 15 to 17 significant decimal digits. The shortest round-tripping decimal is the shortest
decimal string that reads back as exactly that same binary64 value and no other, which is what Python's repr of a float
returns. So the two quantiles and the sample SD are converted to binary64, multiplied there, and the product is recorded
as that shortest string: no rounding choice is left to be made after the values are seen.
The three-night schedule admits retained n from 19
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
new Q99). The successor's generation row registers that S rule under the NAME
floored_range_envelope_screen, and the validator recomputes screen == max(quantized range, 0.010818) under it. The name
records the RULE fixed here before capture, not the branch the data took: the row carries this name whichever arm of the
max wins. Naming it by the realized branch would make the registered rule a function of the data, which is what a
pre-registration exists to prevent, and it would misfile the ordinary case, since a corpus at the n = 19 size floor has a
range just below 0.010818 and takes the floor arm. (The six issued generations register the other name,
range_equals_screen: screen == quantized range, with no floor. An unregistered name refuses rather than defaulting to
either rule.) The generation records the predecessor ceiling and an explicit d125_ruling
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

## Known conditions (recorded, not rules)

**Display state at t0 is not constrained by the night gate.** The gate
(`joulewise/night_gate.py`, condition C3) requires the screensaver's
`idleTime` preference to read exactly `0` — meaning the screensaver never
engages, refusal reason `night_refused_hid_idle` — and for the display it only
requires that `pmset -g` yield a parseable `displaysleep` setting, recording
that value as evidence without demanding any particular one; it never probes
whether a panel is awake, dimmed, or asleep when the window opens, and the
derivation chain deliberately omits the writer flag
`--sleep-display-before-capture` that the G2-a chain passes, because no
operator is present to schedule a display action. These captures may therefore
differ systematically in display state from the G2-a corpus the resulting
acceptance will judge. That is recorded here as a known condition of this
corpus, not a rule: it edits no membership, moves no threshold, and licenses
no re-capture.

## Fields filled at commit

`[DD]` (authoring day), `[MLX_VERSION]`, `[SEQ]` and `[DIGEST]` (the committed
head pin at the first night's open), and `[CHAIN_SHA256]` (the capture chain's
digest). Each is a fact that does not exist yet; none is a scientific choice,
and filling them does not reopen any rule above.

---

# Revision 2 (2026-09-10, Ed's ruling by directive issue 316)

STATUS: Ed's ruling by directive issue 316; recorded by the magistrate; not a
magistrate amendment (rule 11)

Revision 1 above is sealed. Not one word of it is edited here, and every
status line it carries stands as written. This revision does two things and
nothing else: it answers the one rule revision 1 left explicitly open — V3,
the night count and the retained-corpus minimum — and it fixes, before any
capture exists, a shorter route that revision 1 did not contain. Where the two
texts disagree the rule below governs, until its own FAIL branch returns the
campaign to revision 1 unchanged.

## Provenance

Directive issue 316 of this repository, authored by the owner account `mpmdw`,
opens with its own provenance line, quoted here because the authority of
everything below rests on it:

> Ed's ruling on the evening 09-10 email (Gmail 1a08e62b7e99b312, "decisions I
> need from you"). Filed on Ed's behalf by Fable from an interactive session
> on 2026-09-10 ~21:20 PDT after Ed read the recommendation and signed off in
> his own words ("cant you pass that to the magistrate yourself? i sign off").
> The ruling is Ed's; the wording is Fable's.

The issue body is the instruction. This section transcribes it; it adds no
rule of its own, and where it quotes, the quotation is the operative text.

## Decision 1 — V3's three-night default, as a default path: NO

Ed's answer to V3 (three agent-free nights of twelve slots, retained n ≥ 19)
is **NO as the default path**. His reason, in the issue's words:

> Do not arm three derivation nights as the default path. The reason, in Ed's
> words: the scheme "is acting for an adversary that doesn't exist"; with a
> single trusted operator (D-161) the question is an instrument one: did the
> OS point release move the clock-anchor bound or not? That is answered by one
> quiet night compared against the envelope already in force, not by a
> three-night blind derivation.

The three-night derivation is not withdrawn and not amended. It becomes the
FAIL branch below, and revision 1 remains on file, un-withdrawn, as the
fallback route.

## What replaces it: night one is an epoch-equivalence check

**Epoch-equivalence check** — a comparison, decided by a rule fixed before any
of its data exists, between what one new quiet night measures and the
thresholds the acceptance already in force carries. It asks one question: did
the OS point release move the clock-anchor bound outside the envelope the
instrument was already characterised against? It derives nothing, and it
issues nothing.

**Reference envelope** — the two comparators plus the budget ceiling that the
acceptance in force, `d079_calibration_acceptance_v2_n17_r6`, carries: its
level screen, its bracket screen, and its maximum budgetable drift. The
constants are tabulated below before they are used.

**Retained value** — the `b_fiducial_s` (a capture's fiducial bound in
seconds, glossed in revision 1) of one capture that both is `valid` in the
ledger and resolves under anchor-v3 replay. A capture that is not retained
contributes no value and is not compared against anything.

**Continuation** — carrying the acceptance in force forward onto the new
identity epoch by a dated addendum, rather than voiding it and deriving a
successor. It changes no threshold: every number the acceptance publishes
stays exactly what it is.

### The night itself, unchanged from what is built

Per the issue:

> The first quiet night is ONE derivation-kind ledger session of 12 slots run
> by the merged chain exactly as built (PR #315; runbook
> docs/phase_2/derivation_night_runbook.md; NIGHT_HANDBACK email-then-arm
> unchanged; tonight's rehearsal-20260911 untouched). Nothing about the arm,
> the chain, the settle, the census, or the dead-man changes.

So the night's shape is revision 1's night: one `derivation`-kind session,
twelve declared slots, the same cadence, the same agent-free `[QUIET-MAC]`
discipline, the same email-then-arm handback, and the same
`DIAGNOSTIC_NO_PACK` receipt class. What changes is only what the night is
FOR, and what may be read after it closes.

### The reference envelope, as constants, with their sources

Two values exist for each comparator: the raw corpus statistic, and the
operative constant the validator actually compares against — the raw statistic
quantized (rounded to a fixed decimal place) under the rule the artifact
registers. Issue 316 fixes which one governs:

> The magistrate confirms these operative constants from the artifact and the
> validator's own code path and quotes them in the record; if the validator's
> operative screen differs from the raw range (the never-zero floor), the
> operative value is the one used.

The operative value is therefore the comparator in the rule below, in every
case. Both are printed so the difference is visible rather than hidden:

| Quantity | Operative constant used by the rule (s) | Raw corpus statistic (s) | Where each is read |
|---|---|---|---|
| Level screen (corpus maximum) | `0.032898493715362` | `0.03289849371536248` | Operative: `joulewise/calibration_bracketing.py`, `_D102_N17_DERIVATION["operatives"]["preflight_level_screen_s"]`, keyed to this acceptance id through `_D102_GENERATION_DERIVATIONS`; the same lexeme is in the artifact at `decimal_derivation.ratified_operatives.preflight_level_screen_s`, and at `decimal_derivation.rounding.preflight_level_screen` with `numeric_role: operative_comparator`. Raw: the artifact's `decimal_derivation.source_statistics.maximum_s`, the value issue 316 quotes. |
| Bracket screen (corpus range) | `0.009724` | `0.00972358928879385` | Operative: same validator row, `operatives["bracket_screen_s"]`; artifact `decimal_derivation.ratified_operatives.bracket_screen_s`, and `decimal_derivation.rounding.operative_bracket_screen` with `numeric_role: operative_comparator`. Raw: the artifact's `decimal_derivation.source_statistics.range_s`, the value issue 316 quotes. |
| Budget ceiling (maximum budgetable drift) | `0.010164834757777545` | same value; it is not a rounded statistic | Validator row `operatives["maximum_budgetable_drift_s"]`; artifact `decimal_derivation.ratified_operatives.maximum_budgetable_drift_s`. |
| Maximum budgetable excess | `0.000440834757777545` | same value | Validator row `operatives["max_budgetable_excess_s"]`; artifact `decimal_derivation.ratified_operatives.max_budgetable_excess_s`. Ceiling minus bracket screen, exactly: `0.010164834757777545 − 0.009724 = 0.000440834757777545`. |
| Corpus size | `17` | `17` | Validator row `corpus_n`; artifact `derivation_corpus.n`. |

Three facts about those numbers, each of which changes what a comparison
means, so none is left to be inferred:

1. **The operative bracket screen is LARGER than the raw range**, by
   `0.009724 − 0.00972358928879385 = 4.1071120615e-7 s` (about 0.41 µs). The
   artifact registers the quantum `0.000001` s with `ROUND_HALF_EVEN`, and the
   raw range rounds UP to it. Using the operative value is therefore the
   slightly more permissive of the two choices, by 0.41 µs on a comparator of
   9.7 ms.
2. **The operative level screen is SMALLER than the raw maximum**, by
   `0.03289849371536248 − 0.032898493715362 = 4.8e-16 s`. Its registered
   quantum is `0.000000000000001` s, and the raw maximum rounds DOWN to it.
   Using the operative value is the slightly stricter of the two choices, by a
   margin sixteen orders of magnitude below the instrument's ~1 J / ~ms
   resolution: it can only matter to a capture that ties the corpus maximum in
   its fifteenth decimal place.
3. **No floor is in force for this comparison.** The never-zero floor issue
   316 parenthesises — `0.010818` s, `D125_SCREEN_FLOOR_S` — belongs to the
   screen rule `floored_range_envelope_screen`, which revision 1 registers for
   the FUTURE successor corpus. The acceptance in force registers the other
   rule, `range_equals_screen` (the quantized range IS the screen, with no
   floor): `_D102_N17_DERIVATION["screen_rule"]`, checked in
   `calibration_bracketing._valid_acceptance_bound`. The difference between
   the operative bracket screen and the raw range here is quantization alone,
   not a floor.

### The rule, fixed now, before any capture of this night exists

From issue 316, its operative text:

> After the night closes, the magistrate READS the night's retained values and
> applies this rule, written now:

- **Retained m.** "Retained m = the night's valid, resolved captures
  (anchor-v3 replay resolved, not window_exhausted or slot_refused)."
- **INCONCLUSIVE.** "If m < 6 the check is INCONCLUSIVE: run one more
  equivalence night before deciding. No other action."
- **PASS.** "PASS = every retained b_fiducial_s <= the r6 level screen AND the
  night's range (max minus min of the retained values) <= the r6 operative
  bracket screen."
- **FAIL.** "FAIL = anything else."

Read against the table above, the two PASS comparisons are: every retained
value ≤ `0.032898493715362` s, and (largest retained value − smallest retained
value) ≤ `0.009724` s. A single retained value trivially has range zero and is
compared on the level screen alone; the m < 6 branch decides whether so small
a sample decides anything at all, and it decides before the values are seen.

## On PASS: continuation, not derivation

> On PASS: the r6 acceptance is CONTINUED onto identity epoch 25G83 by a dated
> addendum under D-102 that Ed authorizes here ("epoch continuation on
> evidence": an identity-field change followed by a same-envelope night
> continues the acceptance in force rather than voiding it). The addendum
> cites the night's session id, the twelve slot outcomes, and the m values
> verbatim. Ordinary capture and the first real G2-a window proceed on the
> next quiet slot after the addendum lands. The 25G83 pre-registration stays
> on file, un-withdrawn, as the fallback route. If continuation needs a code
> change (the epoch-freshness refusal in the loader or issuer), the magistrate
> lands it through the normal PR gate as the smallest possible change and
> reports the diff; it does not work around a refusal by hand.

Four consequences, stated so they cannot be read loosely:

1. PASS licenses NOTHING by itself. The addendum under D-102 is what licenses
   ordinary capture; until it lands, the acceptance in force still binds the
   old identity epoch and ordinary capture still refuses.
2. The first real G2-a window is the next quiet slot AFTER the addendum lands,
   under the ordinary window path and the standing gates — not a window this
   pre-registration authorizes.
3. No threshold moves. Continuation carries the existing numbers forward; it
   derives nothing and issues no successor.
4. A refusal in code is not worked around. If the loader's or issuer's
   epoch-freshness refusal blocks continuation, the smallest change that
   removes it goes through the ordinary pull-request gate with its diff
   reported.

## On FAIL: revision 1 proceeds, and V3 is affirmed

> On FAIL: the pre-registered three-night derivation proceeds as written in
> configs/calibration/preregistration_d079_epoch_25g83_rev1.md, and V3 is then
> AFFIRMED by this issue (three nights, 12 slots, retained n >= 19, or exactly
> 17 with a written ruling). Night one COUNTS as registration night one. Ed
> rules here that examining night-one values under a rule fixed before capture
> does not compromise the derivation: blindness for this campaign means "every
> rule fixed before data", which this issue satisfies, not "no one may look".
> If the issuer's in-code blindness refusal blocks counting night one, the
> magistrate reports it and proposes the minimal change; it does not run a
> fourth night to satisfy the guard.

So on FAIL the campaign is revision 1's, entire and unamended — V3 carries the
affirmative written acknowledgment it required, this equivalence night is
registration night one, and two further nights follow under revision 1's
stopping, membership, exclusion and analysis rules.

**Ed's blindness clarification, which governs both branches.** Blindness for
this campaign means every rule is fixed before the data exists. It does not
mean no one may look. The rule above is fixed here, in writing, before the
night runs; reading the night's retained values afterwards therefore selects
nothing, because there is nothing left to select. Revision 1's own reason for
blindness — "every rule that could otherwise be chosen after seeing values is
fixed here first" — is satisfied by fixing the rule, which is what this
section does.

## Decisions 2, 3 and 4; timing

> Not addressed by this issue. Their stated defaults and veto windows stand
> exactly as the email wrote them.

> Earliest equivalence night: the early hours of 2026-09-12 as the email
> already proposed, subject to PR #316 landing, the handback rewrite, and the
> standing gates. The objective is real G2-a numbers on the first quiet slot
> after a PASS.

This revision authorizes no window and licenses no measurement, exactly as
revision 1 did not. The arm still goes through the standing gates and the
email-then-arm handback, and Ed's NO overrides.
---

# Revision 3 (2026-09-17, cold-gate ruling 69, packet 69)

STATUS: cold-gate ruling 69 (packet 69, activation 9853dd2b), paired Opus
refutation 12 and magistrate synthesis 13; recorded by the magistrate; not a
magistrate amendment (rule 11)

Revision 1 above is sealed and revision 2 stands as written. Not one word of
either is edited here. This revision does one thing and nothing else: it
re-fills the `[CHAIN_SHA256]` field that revision 1 lists under "Fields filled
at commit" as "a fact that does not exist yet; none is a scientific choice, and
filling them does not reopen any rule above." Re-filling a field the sealed
text designates non-scientific reopens no sealed rule; the authority for the
re-fill is this ruling.

## Provenance

Cold-gate packet 69, sha256
a77c4ab3eb64c1f4da9f344a2fc247d18e1798be1c0c44e9fb59dc8f100410b0, at
`docs/process_traces/2026-09-16-activation-9853dd2b/69-coldgate-packet-prereg-chain-digest/00-PACKET.md`,
with its exhibits A-F, adjudicated by the cold Fable judge in
`10-coldgate-fable-ruling.md` of the same directory. The chain digest
history is exhibit B; the generator literal comparison is the judge's
probe P3, reproduced independently by the paired Opus refuter.

## The one change

Revision 1, "Sample.", pins the chain at the digest beginning b8bf5b0a85bb.
For every capture night opened after this revision lands, that sentence is
read with the digest below in place of the sealed value:

Chain digest in force (revision 3): b5beea464d392621631d9e5060e2c63c804676b28a5b2aea58b714c5cbead6fb

That value is the SHA-256 of `scripts/night_chains/calibration_derivation_only.zsh`
at the committed head the night is armed from, written by the magistrate in
the same commit that records this revision, and verified three ways: the test
`tests/test_preregistration_chain_digest.py` (ruling 69 Q4) fails unless the
line above equals the tracked chain's digest; `python3
scripts/gen_derivation_night.py --check` passes at that head; and the plan
sidecar the night gate reads at t0 refuses `night_chain_digest_mismatch` if
the bytes move afterwards.

## Why no science rule moved

The chain changed on 2026-09-17 (PR #350 and the end-of-window abort lane)
to: bound every governed custody read by a budget (`--custody-budget-s`) and
a deadline (`--custody-deadline-epoch-s`, window end minus 10 s); fold the
separate pre-reserve readiness command into `--pre-reserve-strict` on the
reservation itself; add a verify-only reservation probe (`NIGHT_VERIFY_ONLY`);
export a refusal-document path and a custody-budget marker; and bound the
session abort to one custody read under one budget.

One consequence is stated so it cannot be read as hidden: a governed
custody read that cannot be bounded within its allowance (CUSTODY_BUDGET_S,
default 120 s, threaded from the plan by scripts/run_night.py) now refuses
in a typed, logged way where the sealed chain could block without limit.
Every such check runs in the ledger lifecycle's begin, abandon or finalize
step, never between the sampler's spawn and its teardown, so no refusal can
truncate or perturb a capture; its worst case is a fully captured slot whose
ledger row is left unfinalized (slot_refused, session open) for desk
recovery. That is a stop condition, not a tuning: it changes no value any
capture records, and it can only subtract a slot, never admit one the sealed
rules exclude.

Evidence, verifiable at the arm head: the generator's timing literals
(PRE_REGISTERED_SLOT_COUNT 12, DEFAULT_SETTLE_S 600, DEFAULT_SLOT_CADENCE_S
600, DEFAULT_SLOT_CAPTURE_BUDGET_S 480, receipt class DIAGNOSTIC_NO_PACK) are
byte-identical between the sealed head 3015cb39 and the arm head; the
runsheet's generated region changes over the same interval only in prose and
in the rendered chain digest, not in any rendered constant (packet 69 exhibit
C); `gen_derivation_night.py --check` is the tripwire that forces that region
to be re-emitted after any chain edit, and its passing is not itself evidence
about the constants; the chain still performs one settle after the
reservation and before slot d01, anchors each next start to the actual slot
start, aborts window_exhausted without compressing a slot, runs the writer
with --derivation-only and --power-policy ac_high_power, and omits
--sleep-display-before-capture.

## What this revision does NOT change

The epoch tuple, the powermetrics and MLX pins, the ledger baseline sentence,
the sample size and window shape (one 600 s settle, 12 slots at 600 s
start-to-start cadence, fixed order, agent-free), the protocol id, the
membership, exclusion, stopping and analysis rules, V3, the known-conditions
section, revision 2's equivalence rule and both of its branches. It authorizes
no window and licenses no measurement.

# Revision 5 (2026-09-25; sealed 2026-09-25 at PR-L merge 9b750bf3)

**STATUS:** Revision 4 was drafted, never sealed, and is held at fallback tag `acc-v4-fallback` = `ea10e3c8`. Revision 5 is prospective: no W1 capture may be armed until the literal launch-context placeholders below are replaced with verified values and this whole text's digest is pinned in the arm material. The issuer refuses candidate preparation while any placeholder remains.

**Authority:** council ACCEPTANCE-25G83-02 under D-184 **Addendum (Ed, 2026-09-24 ≈04:40 PDT)**, as finally ruled by `docs/process_traces/2026-09-25-activation-152c9255/05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md` §5 R4, R5, R9, R10, R17. This revision amends Revision 2's `## What replaces it`, `## On PASS`, and `## On FAIL` sections, Revision 1's “Stopping.” and dry-run outputs under “Blindness.”, and drops Revision 1's “Screen challenge.” as an issuance veto for this epoch. Wherever Revision 2 names r6 as the acceptance in force, read `d079_calibration_acceptance_v2_n17_r7`; r6 and r7 operatives are identical. Revision 3's chain digest in force remains unchanged.

## Registered epoch and operating condition

The six identity fields are `os_build` = `25G83`, `hardware_model: Mac15,9`, `power_policy: ac_high_power`, `sampling_interval_ms: 100`, `estimator_revision: joint_loss_sublevel_interval_branch_v2`, and `pulse_protocol_id: powermetrics_pulse_fiducial_v3`. The pinned operating condition is captures launched by a launchd agent with `ProcessType=Interactive`, template at commit 9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87, template digests e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8 and 1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd. The first digest is the sha256 of configs/launchd/com.joulewise.night.plist.template (shared by the night and dead-man labels) and the second of configs/launchd/com.joulewise.night-probe.plist.template, both read at that commit. Each window's rendered-plist digests are plan-specific and are recorded in that window's arm evidence and probe receipt by the installer; they are not part of this text. Sealing replaces these three literals after PR #412 lands on main and before W1's arm notice: the commit is the one GitHub reports as PR #412's merge commit (`gh pr view 412 --json mergeCommit`); each digest is `git show <that commit>:<template path> | shasum -a 256`. The placeholder count (`grep -c -E '<PR-L-MERGE[-]SHA>|<TEMPLATE[-]SHA256:'` on this file) must be 0 before the arm-notice digest is taken; seal the literal tokens without backticks; at the seal, replace the header parenthetical "sealing pending PR-L pins" with "sealed <YYYY-MM-DD> at PR-L merge <first 8 hex of the commit>" (amendment A-R5a-1, `docs/decision_log.md`). Launch context sets the sampler cadence; this condition is part of the registered experiment.

## Sample, stops and blindness

W1 and W2 are derivation-kind windows of 12 declared slots each, at least 6 h apart; each has a 600 s settle and 600 s slot start-to-start cadence. W1 is derivation window one. At W1 harvest, the pin-free cadence report reads raw plists before any B value is read; if the median of the per-capture median native frame lengths is above 150 ms, stop: no W2, return to council. Then the count-only dry run runs before any B value is read. If it reports fewer than 6 valid of 12, stop: no W2, return to council. W2 then runs. W3 is permitted only if the count-only dry run after W2 shows fewer than 12 valid, and is another 12-slot window. Every valid resolved member is retained. Retained n ≥ 12 is the issuance floor; 12/13 order-statistic coverage, the floored S and t(0.995,11) support it. The earlier 0.245 s yield reason no longer applies. No B-based exclusion or outcome-driven top-up is permitted. B values are read only after the terminal session. Rules are fixed here before capture. The dry run may report valid count and “median native frame length,” alongside the existing counts, states and exclusion mechanisms; it reports no B value, screen or comparison.

Revision 2's equivalence look is NOT taken for this epoch. Reason: the r7 envelope's ceiling is its July corpus maximum at ≈120 ms frames; B grows with frame length; a 12-draw look cannot distinguish a +6 % regime from an identical one. W1 is derivation window one. There is no PASS continuation branch or FAIL branch for this epoch.

## Disclosed design inputs

The eleven valid 2026-09-19 n1/n2 B values, seen before this revision and disposed as diagnostics under `D-126-disposition-25G83-v3-2026-09-25`, are (seconds), in capture order: `0.041133514338919874`, `0.04200278099548145`, `0.172710636067422`, `0.03255031906139217`; `0.04103035733376445`, `0.04337273381948624`, `0.028250396657612444`, `0.035576770468514644`, `0.03487995875720681`, `0.13333095801710004`, `0.036897960254235855`. They are never members of the new registration.

The observed native-frame distributions, in the ruling's I/SH/D order (context; files; intervals; median; p95; maximum; fraction >0.25 s; fraction >0.1833 s), are:

| Context | Files | Intervals | Median | p95 | Maximum | >0.25 s | >0.1833 s |
|---|---:|---:|---:|---:|---:|---:|---:|
| I, session C | 21 | 6155 | 131.6 ms | 134.8 ms | 140.8 ms | 0 | 0 |
| I, session 2 | 12 | 3510 | 131.6 ms | 134.8 ms | 143.9 ms | 0 | 0 |
| SH, session C | 18 | 5496 | 121.2 ms | 125.2 ms | 134.1 ms | 0 | 0 |
| D, session 2, display ON | 3 | 703 | 243.3 ms | 278.6 ms | 296.4 ms | 43.5 % | 83.2 % |
| D, n1 night 09-19 | 30 | 10308 | 247.9 ms | 274.1 ms | 353.3 ms | 46.4 % | 82.9 % |

## Issuance arithmetic and barriers

The predecessor screen challenge is recorded as a diagnostic, not an issuance veto for this epoch: on an identical instrument it would falsely refuse 16.3 % of the time. Count retained B > 0.075 s. Two or more mark the candidate `excursion_limited`, requiring the estimator lane before a phase-split claim. Any member B > 0.25 s refuses issuance with the `PLATEAU_INSET_S` mechanism named; 0.25 s is that protocol's plateau inset. No B value is excluded. S = max(corpus range quantized to 1e-6 s, 0.010818 s); C = max(predecessor C, successor Q99, S). If C = S, record `zero_headroom` and proceed with issuance; drift above S is refused by the operative bracket.

The physical barriers are pulse interiors, SNR, detection of all 59 pulses, edge coverage, anchor feasibility, pre/post brackets, settle and slot cadence, blindness, and verified Interactive launch context. Calendar-day spacing, n ≥ 19, the predecessor screen challenge, and strict S < C are not physical barriers for this epoch.

## Stale-number audit from record 37, re-keyed to 25G83/v3 at ≈132 ms

| Historical number | Role | Revision 5 disposition | Reason |
|---|---|---|---|
| 0.032898493715362 s | r7 preflight level screen | Replace as operative with new corpus maximum quantized to 1e-15 s; retain count above r7 as diagnostic. | The 132 ms operating condition changes B; r7's 120 ms maximum is not this epoch's screen. |
| 0.009724 s | r7 bracket screen | Replace with S = max(new quantized range, 0.010818 s). | The successor corpus sets its own range; the D-125 floor remains. |
| 0.010164834757777545 s (≈0.010165 s) | predecessor drift ceiling | Retain as predecessor-C input, then C = max(predecessor C, new Q99, S). | D-125 lineage monotonicity forbids lowering the ceiling. |
| 0.010818 s | D-125 genesis S floor | Retain. | It is independent of r7 cadence. |
| `calibration_bracket_max_drift_s` 0.010 s | production policy | Retain as policy until atomic G2-a re-freeze reconciles it with S and C. | It is a separate, conservative bound, not the new S or C. |

The historical r7 maximum-plus-range 0.04262208300415633 s remains diagnostic only. The simulation of W1 → futility → W2 → count-only W3, with all valid members retained and no equivalence branch, is `docs/calibration/acc_25g83_rev5_simulation.md`; its finite-sample bounds are a desk check, not a release criterion.

# Revision 5 — Amendment A-R5b (2026-09-25): battery float (directive #421)

Revision 5 above is sealed; not one word of it is edited here. This amendment adds one outcome-independent, mechanism-named exclusion decided from instrument state alone, and the rules that follow from it. It authorizes no window and licenses no measurement.

**Predicate.** A battery-float observation is one run of `/usr/sbin/ioreg -r -c AppleSmartBattery` whose raw standard output is retained. It PASSES when exactly one AppleSmartBattery object is present and, read only from that object's top-level property lines, `ExternalConnected = Yes`, `IsCharging = No`, `|InstantAmperage| ≤ 200 mA`, and the object's `UpdateTime` is no more than 180 s before the observation's wall time. A printed integer at or above 2^63 is read as that value minus 2^64 (two's complement; example: `18446744073709551458` reads −158 mA). A missing, duplicated, malformed or unreadable property, a failed or timed-out probe, a stale `UpdateTime`, or more than one object is not a pass. `Amperage` is recorded but never substituted for `InstantAmperage`. Each observation also records `Amperage`, `Voltage`, `Temperature`, `FullyCharged`, `CurrentCapacity`, `AppleRawCurrentCapacity`, `AppleRawMaxCapacity` and `UpdateTime`.

**Admission.** A window is admitted only if the predicate passes at the arm check, again immediately before publication, and again at t0 inside the night gate's C3 row (refusal code `night_refused_battery_float`; probe failures are `night_probe_error`). A t0 or arm refusal with zero capture is a machine-state refusal under D-182: it licenses one new-plan successor on D-182's terms and is never a same-plan retry and never waived.

**Per-slot evidence.** Every derivation slot whose capture writer reaches its custody directory records one observation before the capture's first clock stamp is taken and one after its last clock stamp is taken, so that neither observation falls inside the interval the clock anchor is computed from and neither overlaps the sampler's life. The raw bytes are retained under the slot's custody as `raw/battery_float.pre.ioreg` and `raw/battery_float.post.ioreg`; their SHA-256 digests, the verbatim property lines and the parsed values are recorded under the key `battery_float` in the hashed `instrument_evidence.json`. A failing or absent observation does not change the writer's exit path. The registered protocol, chain digest, sampler set, estimator-code pins and the estimator's clock-stamp inputs are unchanged.

**Window verdict.** Before the cadence report, before the count-only dry run and before any B value is read, every slot of the window that has a finalized ledger row, whatever its disposition, is checked from its raw bytes alone: both observations must be present, authenticated against the recorded digests, re-parsed, and must pass the predicate. One slot failing the predicate makes the whole window `battery_float_confounded`; one slot with a missing, stale, unparseable or unauthenticated observation makes it `battery_float_evidence_missing`. Either verdict is final for that window. A declared slot the window never reached (`window_exhausted`) carries no obligation.

**Consequences.** A window with either verdict is retained and disclosed. None of its slots is a member; none counts toward the "fewer than 6 valid of 12" stop, the 150 ms cadence stop (its cadence report is produced as a diagnostic only), n, or W3's trigger; its B values are not read before issuance is decided and are diagnostics afterwards. The issuer computes the verdict itself from raw bytes for every derivation-kind session it is asked to consider or that would otherwise refuse issuance under addendum A-7; the operator names the excluded sessions separately and issuance refuses unless the two sets are equal, so no clean window can be declared confounded and no confounded window can be omitted. The harvest record, the candidate's derivation notes and the next arm notice name the window, the failing slots, the raw digests and the reasons.

**Replacement.** A window with either verdict is replaced by one fresh window of the same kind under the unchanged protocol. The replacement takes the replaced window's place in the W1/W2/W3 sequence, faces that window's stops afresh, and keeps this revision's spacing of at least 6 h to its neighbours. At most one replacement window is permitted per epoch; any further window with either verdict stops the epoch and returns it to council. Replacement is admissible because the verdict is decided from instrument state alone, before any B value or disposition is read, so it cannot select on outcome. No other top-up is permitted.

**Disclosure.** Two observations bound a slot's endpoints only. `AppleRawCurrentCapacity` is updated by the gauge in steps, not continuously: on 2026-09-25 it held at 7516 mAh through about 4.5 min of 0.58–0.74 A charging (about 45 mAh), then stepped to 7591 mAh, its full-charge capacity, when charging ended. Its difference across a slot is recorded as a diagnostic and does not bound the net charge in between. A charging excursion that begins and ends between a slot's two observations is not detectable by this rule and is disclosed as a limitation. The 200 mA bound is a screen of thermal state for powermetrics-only windows; it is not an energy bound for a wall-meter window, and no wall-meter window is claim-bearing until WALL-METER-GAIN-01 registers a bound on the battery's net energy over the capture, from the wall side or by excluding the battery path by design.

# Revision 6 (sealed 2026-09-30 at 46643f1d)

**STATUS:** sealed. This revision is prospective. It governs only the windows it
declares, and only once it is sealed. It does not arm or authorize any window, license any
measurement, or lift the claim hold H1 (defined in §0). No window under it may be armed until
two things are true: every unfilled pin slot has been replaced by its value (§13 gives the
mechanical test), and the digest of this whole file has been pinned in the arm material. The
seal procedure is in §13.

**Authority.** This revision rests on seven sources:

- Cold registration gate REV6-25G83-01, which ruled this text. Ruling file
  `docs/process_traces/2026-09-29-interactive-ff50b201/110-rev6-gate/21-coldgate-fable-ruling.md`,
  sha256 `e61b6e879e15fa4807c780507de8d5bc58c0083f5c75dc3cfe37ff855eb93732`. Its erratum REV6-25G83-01-E1 settled the paired refuter's
  eight findings in this text. Erratum file
  `docs/process_traces/2026-09-29-interactive-ff50b201/110-rev6-gate/31-coldgate-erratum.md`,
  sha256 `f6c051513493aa09c85e41eeaaf44fc63a489f15442f59510408e294998e6e77`.
- Erratum CAP-COUNCIL-25G83-01-A2-E1, §4 step 12. That step lists what this registration
  must say.
- Addendum CAP-COUNCIL-25G83-01-A2 §3.6, items 6 and 7, and §3.3.
- Addendum CAP-COUNCIL-25G83-01-A1: rule CAP-RULE-25G83-2 (R0 to R12), and S5.
- Cap ruling CAP-COUNCIL-25G83-01 §5 (membership).
- Decision D-186 (network time stays OFF; a stop sends a question to review and is never
  "stop for good").
- The owner's statements of 2026-09-29, session ff50b201: record item 46 (the name of P8, the
  successor name pattern, and the owner's statement that this answer is the seal approval
  that E1 step 12 requires) and record item 47 (window cadence, quoted in §6.2).

Revision 1, Revision 2, Revision 3, Revision 5 and amendment A-R5b stay sealed, and not one
word of them is edited here. For the Revision 5 windows W1 and W2 they stand exactly as
written. §1 maps which of their clauses this revision replaces for the new windows.

## 0. Words used

Each term is defined here before any rule uses it.

- **Capture**: one 197-second recording by the power sampler (`/usr/bin/powermetrics`). During
  it the machine runs 59 commanded one-second load pulses (protocol
  `powermetrics_pulse_fiducial_v3`). **Frame**: one power sample. **Median frame**: the middle
  value of one capture's native frame lengths, in milliseconds.
- **B** (stored as `b_fiducial_s`): the single timing-uncertainty number, in seconds, that a
  capture yields.
- **Estimator**: the code in four files that turns a capture's raw bytes into B. **Pins**: the
  sha256 digests of those four files.
- **Cell**: one rectangle of candidate pulse-edge timings that the estimator tests. **The cap**:
  the most cells one capture may test. It is fixed by rule CAP-RULE-25G83-2 as one integer,
  pinned in §5. **Wall deadline**: a second stop in the estimator, 120 seconds of elapsed time
  per capture.
- **Calibration**: an issued JSON file of limits on B, computed from its **members**, the
  captures whose B enters the limits.
  - **R7** is `d079_calibration_acceptance_v2_n17_r7`: 17 members, all taken at build
    25F84.
  - **P8** is `d079_calibration_acceptance_v2_n17_r8`. It is R7 re-issued with only its pins,
    identity and notes changed, so its limits are identical to R7's (E1 §3.1).
  - **r1** is the unregistered 25G83 candidate `d079_calibration_acceptance_v2_n12_25g83_r1`
    (file sha256 `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2`). Its
    identifier is retired and never reused.
  - **The successor** is the calibration this revision's windows will produce.
- **Window**: one agent-free run of one derivation-kind ledger session of 12 declared slots.
  Earlier revisions say "night"; the word meant a window and never a time of day. **Slot**: one
  declared, ordered place for a capture inside a window. **Agent-free**: no model-driven agent
  process runs on the measurement Mac, whether active or dormant. The reason is that agent
  processes draw power, and the sampler measures that power. **Windows of this revision** are
  labelled C1, C2, C3, C4 in ledger order (§7). They are not W1, W2 or W3, which are the sealed
  Revision 5 windows.
- **Null session**: a session of this registration that ended before any capture was
  attempted. It is terminal, and no slot of it has a finalized ledger row: every declared slot
  is unused. No pulse ran and nothing was recorded, so it measured nothing. A null session is
  not a window, takes no C label and counts toward nothing (§7).
- **Issuer**: the script that derives a calibration from a sealed registration and the ledger
  (`scripts/issue_calibration_acceptance_generation.py`). **Validator**: the code that
  recomputes a calibration's limits from its members and refuses a file that disagrees
  (`joulewise/calibration_bracketing.py`). **Count-only dry run**: the issuer's one route that
  may run between windows; it reports counts and states and no B (Revision 1, "Blindness").
- **Arm**: to schedule a window so that it starts unattended. **t0**: the scheduled instant at which a window's start-time checks run and its chain
  begins. **Night gate**: the code that runs those start-time checks (`joulewise/night_gate.py`)
  and refuses the window if one fails. **Chain**: the script that runs the 12 slots
  (`scripts/night_chains/calibration_derivation_only.zsh`). **Harvest**: the work done after a
  window ends: preserving its files and running the blind checks of §6.2.
- **Blind**: done without reading any B, any limit computed from B, or any comparison with
  either.
- **Valid**: a capture whose ledger disposition is `valid`. **Resolved**: its stored anchor-v3
  clock outcome resolves (Revision 1, "Anchor-v3 replay").
- **Adverse window**: a window whose battery-float verdict under A-R5b is
  `battery_float_confounded` or `battery_float_evidence_missing`. **Counting window**: a window
  that is not adverse.
- **Counted capture** (rule R9 of CAP-RULE-25G83-2): a capture of a counting window in which
  the cell search ran (the harness reports at least one cell) and whose median frame lies
  between 100 ms and 150 ms inclusive. A capture refused at clock alignment tests no cells and
  is not counted.
- **The harness**: the replay harness of rule R0. It is one committed script, cited by digest
  (§5). In report mode it prints, for each capture, the cells, the median frame, cells ÷ cap,
  the disposition and any stop trigger. It never prints B.
- **Content identifier**: the sha256 that the ledger assigns to a capture from its manifest
  hash and its evidence hash. **Set aside**: named in the disposition registry
  `configs/calibration/observation_dispositions.json` under a reviewed decision. The issuer and
  the validator then recognise the row as neither a member nor a foreign row.
- **Foreign row**: a valid capture of epoch 25G83 that belongs to no session of this
  registration and carries no disposition. The issuer refuses to issue while any foreign row
  exists (Revision 1 addendum A-7).
- **Bracket**: in a claim window, one workload measurement with one calibration capture before
  it and one after it. **Drift**: the absolute difference between those two captures' B.
  **Claim window**: a window whose numbers will be reported as results. **H1**: the hold under
  which no claim window is armed at build 25G83 until the closing ruling of E1 §4 step 18.
- **S, C, Q99**, as Revision 5 defines them, with what each does to a bracket
  (`joulewise/calibration_bracketing.py`, the bracket evaluation):
  - S is the bracket screen: the range of the members' B quantized to 1e-6 s, or 0.010818 s
    if that is larger. A bracket's reported timing bound is the larger of its two B values
    plus the larger of (its drift, S).
  - C is the budget ceiling: a bracket whose drift is above C is refused and yields no
    number. C decides only whether a bracket is refused. It never makes a reported bound
    smaller.
  - Q99 is t(0.995, n − 1) × sample SD × √2 over the n members: the half-width inside which
    two fresh independent captures differ 99 % of the time. **SD** is the standard deviation.
    t(p, df) is the Student-t quantile of Revision 1; **df**, degrees of freedom, is the
    count of independent pieces of information behind an SD.
- **Review**: a consult, a cold gate or the owner (D-186). Every stop in this revision sends
  its question to review. No stop is "stop for good".

## 1. Supersession map

"Stands" means the clause applies to these windows exactly as sealed. "Replaced
prospectively" means the clause still governs W1 and W2 as sealed, and does not govern the
windows of this revision. The clause shown in its place governs them instead.

| Sealed clause | For W1/W2 | For the windows of this revision |
|---|---|---|
| Rev 1, epoch tuple, powermetrics and MLX pins, the voiding sentence | stands | stands (§5) |
| Rev 1, "Ledger baseline" (one session per window, opened at head-equals-pin, pin committed at the desk before the next window opens) | stands | stands. "At the desk" is read as "by the between-window harvest" (§6.2 item b). |
| Rev 1, "Sample" (distinct calendar days) | replaced by Rev 5 | replaced prospectively by §6 (no calendar spacing) |
| Rev 1, "Classification" (derivation-only under the active artifact) | read with r7 (Rev 5) | read with P8 (§2) |
| Rev 1, "Membership", "Exclusions" | stand | stand, plus the frame-range and R9-void rules of §8 |
| Rev 1, "Stopping" (n ≥ 19) | replaced by Rev 5 | replaced prospectively by §7 and §8 (n ≥ 12, as Rev 5) |
| Rev 1, "Blindness" | stands as Rev 5 amended it | stands; the dry run may also report the harness figures of §10 |
| Rev 1, "Screen challenge" | dropped by Rev 5 | stays dropped (diagnostic only) |
| Rev 1, "Analysis", quantile proof, D-125 envelope | stand as Rev 5 amended them | stand, plus §9 (a second, window-blocked Q99 that enters the maximum that sets C) |
| Rev 1, "Known conditions" (display state not constrained) | stands | stands |
| Rev 2 (equivalence night, PASS/FAIL) | not taken (Rev 5) | not taken |
| Rev 3 chain pin `b5beea46…` | stands | replaced by the chain pin of §5 |
| Rev 5, operating condition (Interactive launch context, template digests) | stands | stands (§5) |
| Rev 5 line 612: "at least 6 h apart"; W1/W2/W3 sequence; W3 only if fewer than 12 valid after W2 | stands | replaced prospectively by §6 and §7 |
| Rev 5 line 612: W1 cadence stop (> 150 ms) and futility stop (< 6 valid of 12) | stand | kept (§11). The cadence stop now applies after every counting window. |
| Rev 5, issuance arithmetic (n ≥ 12; S; C; zero headroom; over-inset refusal at 0.25 s; `excursion_limited` label) | stands | stands, plus §9 |
| A-R5b predicate, admission, per-slot evidence, window verdict, consequences, disclosure | stand | stand |
| A-R5b "Replacement": "keeps this revision's spacing of at least 6 h to its neighbours" | stands | replaced prospectively: a replacement window meets §6.2 like any other window |
| A-R5b "at most one replacement window per epoch" | stands | stands. W1 and W2 used none, so one remains available for epoch 25G83 (§7). |

## 2. Predecessor, and how to read "R7"

**Predecessor.** P8, `d079_calibration_acceptance_v2_n17_r8`, at
`configs/calibration/calibration_acceptance_d079_v2_n17_r8.json`:

- file sha256: `52e3d18a087bd8a0f28da6d20c3817da4d3ce532c604d7f049c78aad6a489a13`
- `derivation_sha256`: `911d06c3db6e35a4d3a128a52ed47f0c483330a0429d9d87c2ad672185ed1acd`

P8 is R7 re-issued with only its pins, identity and notes changed (E1 §3.1). It judges build
25F84, and it is the active default under which each capture of these windows is written
derivation-only. The issuer takes the predecessor ceiling from it: 0.010164834757777545 s, the
same value as R7's.

**Basis-reading sentence** (A2 §3.6 item 6, in E1's naming): "read P8 wherever R7 is named as
a derivation basis; operatives identical". ("Operatives" are the limits a calibration file
carries: its level screen, S and C.)

Why the sentence exists: the W1/W2 captures record R7 as their derivation basis, while the
captures of these windows record P8. The two files carry identical limits, so this
difference in the recorded name changes no number.

## 3. The 12 W1/W2 rows, set aside; what is never a member; disclosed design inputs

**The 12 valid W1/W2 captures are set aside.** They are not members of the successor or of
any registered calibration. They are not diagnostics. They are valid captures. Each is named
by content identifier under decision `CAP-COUNCIL-25G83-01-E1-set-aside-W1W2-2026-09-29`, with
this mechanism text, byte-identical to the registry: "valid Revision 5 capture of window W1 or
W2; member of the unregistered 25G83 candidate r1, whose member list was fixed under the
165,000-cell cap while 8 of the 24 captures stopped on that cap; set aside from the successor
under CAP-COUNCIL-25G83-01 addendum A1 S5 and erratum E1; a valid capture, not a diagnostic;
not a member of any registered calibration".

The 12 content identifiers, in registry order:

```text
e055af15ca06ebaad7d3cd3dfc9163840219e6610a2e5e197b3cbbc76d64956f
0af949aecb4d30109a9389637ac2c801ea1258284b0b20be6b5f90eb239c467c
79bda70471f19d75ef63ee4b847b2908eaed554e474c623a2612ae392d82aa2d
554d13ec9e9603e471cadfed74d0cbc36f4625f92e94ea942e7734353b5ea01d
37dd0834396ea4337f510c4f4bddcdfdd6ce60afa495ccf5d79e6646d9d86dd3
c1d9d5369b8317ade1c1d9229b5738b59ec733b51b931d033ccbf386731d132d
641c1240dd6c523b5abb8096d84dfe67b1ad1a1307c2e705578a264530fb838e
a9007b73fd91198f6d87fd5bc0195824543a18c4b751e408d6289b79e2ac2b41
4ff672124f72ca261dd2e9063527abcb08108f588fbc75c45169ae926a7519cc
2d81bed3f4b2f2b7c92b1488b465f53ed932ca982fea9a337086e4032dbbe3b9
4154f1f4001e660d40ba88a60b40f3be11be2128deace4db14d02210eea295b2
372eafc180693b3a21053ce2133472a8918fdf300730c04245cb709bd823ccb0
```

The registry file that holds them has sha256
`4a3d96da947d75c4ca84e4ef79630768e11977d4d8cd3592c36259217389effd`. This is the value of
`DISPOSITION_REGISTRY_SHA256` on main `0009b976`. It lists 23 rows: these 12, and the 11 rows
of 2026-09-19 under `D-126-disposition-25G83-v3-2026-09-25`. **The successor declares both
decision identifiers** in `prior_observation_set.disposing_decision_ids`. The validator
refuses an artifact that declares only one of the two decisions while its prior set carries
rows of both (E1 §3.2 item 4).

**Never members, of anything:** the 8 W1/W2 captures that stopped on the 165,000-cell cap, and
the 11 captures of 2026-09-19 (cap ruling §5 item 1). The 8 cap stops are not valid, so they
are neither foreign rows nor set aside.

**r1's identifier is retired.** No bytes other than r1's may ever carry
`d079_calibration_acceptance_v2_n12_25g83_r1`. The successor's identifier follows the pattern
the owner approved, `d079_calibration_acceptance_v2_n<N>_25g83_r2`, where `<N>` is the
successor's realized member count. It is set explicitly at issuance and never left to the
issuer's default name.

**The doubling arithmetic (E1 §3.2).** A calibration goes stale when the ledger holds too many
valid captures of its own build compared with its member count. "Stale" means the validator
reports the trigger `corpus_doubles_from_<n>_to_<2n>`, brackets stop passing, and a
re-derivation is due. The rule is in `joulewise/calibration_bracketing.py` (the bracket
evaluation's doubling block):

- The threshold is 2 × n, where n is the calibration's member count.
- The count is every `valid` ledger row whose identity epoch is the judged build and whose
  content identifier is not set aside by a decision the calibration declares.

Because the successor declares both decisions, neither the 12 W1/W2 rows nor the 11 rows of
2026-09-19 enter its count. At birth the successor's count is the valid rows of its own
sessions: its n members, plus any valid row that is not a member (a valid capture whose
anchor did not resolve, a valid capture outside the frame range, or a valid capture of an
adverse window). It goes stale when the count reaches 2n. Every later valid capture of build
25G83 adds to the count, including the calibration captures of claim windows.

Worked example with invented counts: a successor with n = 30 members and one valid non-member
row starts at a count of 31 and has a threshold of 60. It goes stale after 29 more valid 25G83
captures. If the 12 set-aside rows counted, it would start at 43 and go stale after 17 more.
The choice changes when re-derivation is due. It changes no number. The owner sees this
arithmetic at the seal.

**Disclosed design inputs** (cap ruling §5 item 5). These values were known to the people and
models who wrote the rules of this revision, so the rules were not written blind to them:

- The 12 member B values of r1. They are the field `derivation_corpus.members[].b_fiducial_s`
  of `docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json`,
  file sha256 `dbad7cc782945691701c2ee11188179a61b333dbd0a5588b970636716554b5b2`. They are
  cited by file and digest and not retyped here, so that no transcription can alter them.
- The 8 diagnostic B values of the W1/W2 cap stops, and the three seats that computed them
  (A1 §6 N-4). Record path and sha256: `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/21-science-gate-ruling.md`, sha256 `f9de51b7bf78307ca9239e6750bb13f30f67004483070544fee57c395331f4a4`; `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/22-opus-refuter.md`, sha256 `8679be5c2a59760c71a6f1b2a93cad52360b2789b349450f50c6683b2ec740b4`; `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md`, sha256 `be13ccbae89d67fd7de55231cfbba9ac1d3ff289700fae77910389690fab9d3d`.
- The eleven valid B values of 2026-09-19, printed in Revision 5 above.
- The cell counts and median frames of W1, W2 and the 2026-09-19 sessions, printed in the cap
  ruling and its addendum A1.
- What the cold registration gate computed from the 12 r1 values when it fixed §9 (its ruling,
  §5): six members in each of W1 and W2; window medians 0.026380 s and 0.030778 s; sample SD
  of all twelve 0.004330 s; pooled SD inside windows 0.004137 s; six pairs of members in
  adjacent slots, with a rank correlation of −0.20 between neighbours. §9 contains no threshold
  fitted to these figures. It uses them only in its worked example.

## 4. The two purposes of these windows

Both purposes are declared before the first capture (cap ruling §5 item 4).

1. **Cap evidence.** This is the acceptance test R9 of CAP-RULE-25G83-2, run under the shipped
   estimator bytes. It reads only cells, median frames and dispositions, never B. It passes
   when all of these hold:
   - at least 24 captures are counted;
   - no capture stops on the cell count;
   - no capture stops on the wall deadline;
   - every capture whose cell search ran has cells ÷ cap at or below 0.5;
   - every median frame is reported: the harness states a median frame for every capture
     that has a recording. A capture **has a recording** when its finalized ledger row records
     a digest for the capture's raw sampler bytes.

   Its record, the **R9 record**, is one committed file. For every window and every slot it
   lists the cells, the median frame, cells ÷ cap, the disposition, any stop trigger and
   whether the capture is counted; then the totals, the verdict on each of the five clauses
   above, and the digests of the harness and of the cap rule text. It holds no B. It is
   committed before any B of these windows is read. That commit is an ancestor of every
   commit that carries such a B.
2. **Successor calibration.** The successor is derived from every valid, resolved,
   in-range capture of the counting windows (§8). B is not read until the last window is
   terminal and the R9 record has been committed.

The cap test cannot select on B. It reads no B, and a pass means that no capture was removed.
If a capture stops on the cell count or on the wall deadline, or a ratio is above 0.5, R9 has
failed and the campaign is void: its captures are diagnostics and never members under any
cap (cap ruling §5 item 4). If R9 only falls short of 24 counted captures, it has not passed,
nothing issues, and the question goes to review (A1 R9); §8 says what that does and does not
void.

**When a median frame cannot be reported.** Suppose a capture has a recording, and the harness
cannot state its median frame: the raw bytes are missing, or they do not match their recorded
digest, or they hold no readable frame. Then the fifth clause is not met. For that capture the
cell count is unknown too, so nobody can show that the cap stopped it, and nobody can show
that it did not. This is read as R9 **not passed**, and not as R9 failed. The campaign is not
void by this fact alone; nothing issues; B stays unread; the question goes to review (stop
line STOP-R9-FRAME, §11). The reason it is not a void: a void says the cap removed a capture,
and a missing file is evidence of a storage fault, not of that.

A finalized slot with no recording (the sampler wrote no bytes, so the ledger row records no
digest for them) has no median frame to report. The R9 record lists it with its ledger reason.
It is not counted, and it does not fire the stop line: a capture with no recording never
reached the estimator, so the cap cannot have stopped it.

## 5. Operating condition and pins

Each item below is part of the registered experiment. A change to any of them voids this
revision.

- **Identity epoch.** Six fields, unchanged from Revision 5: `os_build` = `25G83`;
  `hardware_model` = `Mac15,9`; `power_policy` = `ac_high_power`; `sampling_interval_ms` =
  `100`; `estimator_revision` = `joint_loss_sublevel_interval_branch_v2`; `pulse_protocol_id` =
  `powermetrics_pulse_fiducial_v3`.
- **Machine pins.** Unchanged from Revision 1: the powermetrics binary digest `b762e5bf…`
  (verified on the machine 2026-09-30) and MLX 0.31.2.
- **Launch context.** Unchanged from Revision 5: a launchd agent with
  `ProcessType=Interactive`, with template digests `e62a461b…` and `1570b745…` (both
  recomputed on main `0009b976` and equal). Each window's rendered-plist digests go into
  that window's arm evidence.
- **Estimator pins.** The four digests P8 records in
  `prospective_rederivation.estimator_code_sha256`. They are the four values in the `pins`
  object of §7.
- **Cap.** The integer CAP-RULE-25G83-2 yields, as merged in the cap transaction. It is
  `pins.cap_cells` in §7.
- **Harness, rule text and roster** (rule R0 and step 6 of E1 §4), by digest: three values in
  `pins` in §7.
- **Chain pin then in force.** The sha256 of `scripts/night_chains/calibration_derivation_only.zsh`
  at the head the windows are armed from: `pins.chain_sha256` in §7.
- **Validator pin then in force.** The sha256 of `scripts/validate_powermetrics_fiducial.py`
  at the same head: `pins.validator_sha256` in §7. It is taken at or after the identity-seam
  merge (#444).
- **Clean-dwell script pin.** The sha256 of `scripts/prewindow_check.sh` at the same head:
  `pins.prewindow_check_sha256` in §7. §6.2 item (g) states its checks and constants.
- **Disposition registry.** The file digest given in §3.
- **Network time.** "Network time" is the macOS setting that lets the system correct its
  clock from the internet. It stays OFF on the measurement Mac (D-186). Each window is
  admitted by exactly one **settled OFF receipt**. The receipt is a write-once record of one
  run of `/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off` that meets all of
  these conditions:
  - its exit status is 0;
  - its standard output is exactly `setUsingNetworkTime: Off` (the known `Error:-99`
    diagnostic line on standard error is tolerated);
  - it was taken on the same boot as the window's first capture;
  - it was taken at least 600 s before that capture, on both the wall clock (time of day)
    and the monotonic clock (elapsed time, never corrected).

  A brief clock resync is allowed only in the window's arm step: network time ON, then OFF,
  then the receipt, all while no capture of the window exists. Nothing turns network time ON
  after a window's first capture.

  Three earlier requirements are withdrawn prospectively, on D-186: the per-capture
  system-log attestation (H6), the restore-ON machinery, and A1 K3's rule that a
  slew-attested capture does not count. Where A1 R9 says "with H5 and H6 met", read "with a
  settled OFF receipt for the window". H7, the first comparison of network-time-OFF captures
  with the network-time-ON captures of W1/W2, is report-only science. It never gates issuance
  and never pools the two sets.

  The 5 ms limit on clock movement within one capture is unchanged, because it is part of
  the estimator. A capture refused by it is invalid and is not counted. Every capture of
  these windows refused for clock movement or for an empty clock fit is listed by slot in the
  R9 record, so that the closing ruling can see whether OFF kept the clock still.

## 6. Window shape and when a window may start

**6.1 Shape (unchanged in every respect but spacing).** Each window has:

- one derivation-kind ledger session of 12 declared slots;
- one 600 s settle after the last operator action;
- 12 slots at a 600 s start-to-start pitch, in fixed slot order, with a 480 s capture budget
  for the twelfth slot;
- protocol v3 unmodified, and no parameter tuned between captures;
- the Revision 5 battery-float admission and per-slot evidence;
- no operator and no agent present.

A slot the window cannot reach is recorded unused, with reason `window_exhausted`. It is never
compressed or replaced. The programmed span is 600 + 11 × 600 + 480 = 7,680 s. The plan's
`window_max_s` must clear that span plus the generator's allowances and any wait the driver
adds for the network-time receipt. This is a planning fact, not a science rule.

**6.2 When window k+1 may start: physics, not the calendar.** The owner's words of
2026-09-29 (session record item 47, verbatim): "im literally never using the machine, this
macbook is completely dedicated to this science, so again, "nights" are metaphorical, a
measurement window can take place in any cadence you see fit to do the science". The cadence
audit (`80-prune/41-cadence-sol.md`, finding F1) found no measured thermal, battery or clock
recovery that needs six hours. The six-hour gap of Revision 5 is therefore replaced
prospectively, and §9 treats what closer windows do to the statistics.

This revision sets **no minimum gap, no maximum gap and no time of day**. Window k+1 may
start only when all of the following hold. They are checked in this order, and the evidence
for each is recorded for the window.

a. **Window k is finished.** Its session is terminal: its last declared slot is final, or an
   abort has closed it. Every capture and driver process of the window has exited. Every
   evidence file of the window is written and its digest is recorded in the ledger.
b. **The blind checks of window k are done and the count rule says NEXT_WINDOW.** The checks,
   in order, with no B read:
   - raw bytes authenticated against the recorded digests;
   - the battery-float window verdict (A-R5b);
   - the harness report under rule R8;
   - the cadence check (median of per-capture median frames at or below 150 ms);
   - the count-only dry run;
   - the ledger head pin committed;
   - the count rule of §7 evaluated and its decision recorded.
c. **Agent census zero.** The night gate's census finds no agent process on the machine at
   t0, and its 30-second census finds none during the window. Harvest processes have exited
   before item (g)'s dwell begins.
d. **No thermal throttling.** At t0, `/usr/bin/pmset -g therm` reports every
   `CPU_Speed_Limit` as 100. `CPU_Speed_Limit` is the percentage to which macOS caps processor
   speed when the machine is hot; 100 means no cap. This is the night gate's existing check.
e. **Battery float.** The A-R5b predicate passes at arm, before publication and at t0, as
   sealed.
f. **Network time.** A settled OFF receipt (§5) exists for this window.
g. **Clean dwell.** Before t0 the unattended driver runs the pinned script as
   `scripts/prewindow_check.sh --wait --timeout-s <s>`, with no `--window` argument, and the window starts
   only if the script exits 0. The script polls the machine every 30 s. A poll is clean when
   all five of these hold:
   1. no line of the process list (`ps aux`) that contains the name of one of nine background
      daemons (`XProtect`, `mds_stores`, `mdworker`, `mdbulkimport`, `backupd`,
      `photoanalysisd`, `softwareupdated`, `Spotlight`, `mediaanalysisd`; letter case ignored)
      shows more than 5.0 % CPU;
   2. the one-minute load average is at or below 2.0;
   3. the machine is on AC power;
   4. the volume that holds the measurement checkout has at least 20 GB free;
   5. no executable name from `ps -A -o comm=` matches `codex`, `claude`, `t3`,
      `mcp-server`, `run_campaign` or `window-chain`, case-insensitively, either exactly or
      followed by a hyphen, underscore, period or whitespace and any suffix. Leading whitespace
      and directory paths are removed; names containing spaces are matched as a whole. This is
      the script's check 8 for a running agent or measurement process; argument text is not
      matched.

   The script exits 0 when the polls have been clean for 600 s without a break, counted from
   the first clean poll. One failed poll restarts the 600 s. The driver sets `<s>` to the
   ceiling in seconds of the smaller of 2,700 s and its remaining derivation start budget,
   and bounds the subprocess by that budget. If that time passes without such a stretch,
   the window does not start (the script exits 1 at its timeout); a later
   attempt is a fresh arm. The script also prints two notes, on network time and on the
   keyboard backlight, which test nothing. These are the checks and constants of
   `scripts/prewindow_check.sh` (pinned in §5). The window's evidence for (g) is the script's
   complete output, its exit status, and its start and end times.

   The night gate has two start-time paths. On the one-shot path (a plan with no
   quiet-admission policy) it repeats the load-average limit of 2.0 at t0. On the
   quiet-admission path (a plan under which the gate samples CPU use and waits until the
   machine is quiet) it records the load average and does not limit it. This revision does not
   fix which path a window uses, so item (g) is the registered load condition on both. The
   600 s of (f) and the 600 s of (g) may run at the same time; neither is added to the other.

**No idle-power reading is required.** Reason, in physical terms: inside a window each
capture starts 403 s after the previous recording ends (600 s pitch less 197 s of recording),
and the sealed shape already accepts that rest. The first capture of window k+1 starts after
the whole of item (g)'s 600 s dwell and the chain's own 600 s settle, so it has had at least
1,200 s of rest since window k's last pulse. It is therefore better rested than any other
capture of its window, and a separate power reading between windows would protect nothing
that the shape does not already protect.

For each window the record states: the start-to-start interval from the previous window, the
gap between them, and the evidence for (a) to (g). These go into the window's
**start-condition record**: one committed file per window that names, for each of (a) to (g),
the evidence file and its sha256. The issuer refuses to issue without it (§7). For the first
session of the registration, (a) and (b) have no previous window to test, and the record
says so. After a null session, (a) and (b) are read on that session: it is terminal, its
processes have exited, and its NEXT_WINDOW decision is recorded. An owner block of development work between
two windows ("Mix", record item 46) is permitted. The windows before and after such a block
are ordinary consecutive windows of this registration.

## 7. Count rule, window triggers and stops (machine-readable)

**The forcing problem.** Two different tests need enough captures, and they count different
things. The cap test (R9) needs 24 *counted* captures. The calibration needs 12 *members*. A
capture can be counted without being a member (its search ran, but a protocol gate then failed
it), and the window sequence must be decided without reading B. So the rule below counts both
quantities after each window, blind, and says whether another window runs.

**The three quantities, each summed over the counting windows so far:**

- **counted**: counted captures (§0). Source: the harness report.
- **valid**: captures whose ledger disposition is `valid`. Source: the ledger. Used only by
  the futility stop.
- **members**: valid captures whose stored anchor outcome resolves and whose median frame is
  in 100–150 ms (§8). Source: the ledger, the count-only dry run's exclusions by mechanism,
  and the harness report's median frames. None of these reads B.

**The rule in words.** The windows of this registration are taken in ledger order, meaning
the order in which their sessions were opened (`capability_sequence`). They are labelled C1,
C2, C3, C4 in that order, adverse windows included. A null session (§0) takes no label.
After each session's blind checks, the count rule decides one outcome. The first clause that
applies wins.

```text
            a session's blind checks are done
                          |
                          v
 [0] is this a null session (no capture tried)? - yes --> NEXT_WINDOW; but STOP_TO_REVIEW
                          | no                            if the session before it was null too
                          v
 [1] has any stop line of §11 fired? ------------ yes --> STOP_TO_REVIEW
                          | no
                          v
 [2] is this window adverse (battery float)? ---- yes --> NEXT_WINDOW (the one replacement)
                          | no
                          v
 [3] counted >= 24 and members >= 12? ----------- yes --> CLOSE_AND_DERIVE
                          | no
                          v
 [4] are three counting windows done? ----------- no ---> NEXT_WINDOW
                          | yes
                          v
 [5] counted < 24? ------------------------------ yes --> R9_COUNT_NOT_REACHED_TO_REVIEW
                          | no
                          v
                 MEMBERS_SHORT_TO_REVIEW
```

Every box is a test on blind quantities. "counted" and "members" are the running totals
defined above. "Adverse" and "counting window" are defined in §0. A second adverse window is
itself a stop line (§11), so clause [1] catches it and clause [2] can fire only once.

**Clause [0], the null session, and why it is not a window.** A session can open and then be
aborted before any capture is attempted, for example when the chain faults just after the
session is opened. No pulse ran, no sample was taken, and there is no cell count and no B.
Read as a window, it would be a counting window with nothing counted: as the first one it
would fire the futility stop, and later it would use up one of the three counting windows,
in both cases over a fault that says nothing about the instrument. So it is not a window. It
counts toward none of counted, valid, members, n, the three counting windows, the one
replacement or the four windows in all, and the cadence and futility stops do not read it. It
is still a session of this registration: it is named at issuance, the R9 record lists it by
id with its abort reason, and the issuer itself decides from the ledger whether a session is
null. Nothing can be selected by this, because a null session holds no capture to select. One
null session is followed by the next session. Two null sessions in a row stop the sequence
(STOP-NULL-REPEAT, §11), because a fault that repeats is a fault to look at. This follows
decision D-182, which treats a start refused with zero captures as no window and allows one
successor. A session in which even one slot has a finalized ledger row is a window, and every
rule for windows applies to it.

So another window runs while counted < 24 **or** members < 12, up to the third counting
window. These are the two triggers:

- **T-count** comes from A1 R9 and reads counted captures.
- **T-members** comes from Revision 5 and A2 §3.6 item 7. Those texts say "fewer than 12
  valid"; this revision reads members instead, because the issuance floor of §8 is on members.
  The two readings differ only when a valid capture is unresolved or outside the frame range,
  and both are blind.

Either trigger alone opens the next window. Neither opens a fourth counting window: A1 R9
permits a third window and ends there. That makes at most 3 counting windows, plus at most
one replacement for an adverse window (A-R5b), so at most 4 windows in all. Null sessions
are not windows and are outside these counts.

An adverse window is kept and disclosed, but none of its slots counts toward counted, valid,
members or n, and the cadence and futility stops do not read it. The stops of rule R9 (a
capture stopped on the cell count or the wall deadline, a ratio above 0.5, or a median frame
that cannot be reported) do read it,
because a stop says something about the cap whatever the battery was doing. The replacement
takes the replaced window's place in the sequence and faces that window's stops afresh.

**After a stop or a review outcome.** B stays unread until the review has ruled in writing.
The review may end the campaign. It may continue the campaign only by a sealed amendment to
this registration that the issuer reads; the issuer accepts no command-line ruling in place
of one. No clause of the count rule reads B.

**Worked examples** (the counts are invented):

- C1 counts 11, with 10 valid and 10 members. The futility stop (valid < 6 in the first
  counting window) does not fire. Totals: counted 11, members 10 → NEXT_WINDOW.
- C2 counts 12, with 12 members. Totals: counted 23, members 22 → NEXT_WINDOW. T-count alone
  opens C3 here. Under Revision 5's rule, which had only the valid trigger, C3 would not have
  opened. A2 §3.6 item 7 named this gap.
- C3 counts 12, with 11 members. Totals: counted 35, members 33 → CLOSE_AND_DERIVE. The
  successor has 33 members.
- Other paths. Counted 23 after C3 → R9_COUNT_NOT_REACHED_TO_REVIEW: R9 has not passed and
  nothing issues. Counted 24 and members 11 after C2 → NEXT_WINDOW (T-members); if members
  are still below 12 after C3 → MEMBERS_SHORT_TO_REVIEW, and nothing issues. C1 adverse →
  NEXT_WINDOW; C2 replaces it and is the first counting window; if C2 is also adverse →
  STOP_TO_REVIEW.
- Null session. The first session opens, the chain faults before slot 1 starts, and the
  session is aborted with no finalized slot row → NEXT_WINDOW. The next session is C1 and is
  the first counting window. If that next session is null as well → STOP_TO_REVIEW.
- Unreported frame. In C2 one capture's raw bytes no longer match their recorded digest, so
  the harness cannot state its median frame → STOP_TO_REVIEW (STOP-R9-FRAME). R9 has not
  passed, the campaign is not void, and nothing issues until the review has ruled.

**The declaration.** The block below is the machine-readable form that the issuer change
(work item WI-13) reads. It is the only fenced block tagged `json` in this file. The prose
above explains it and was reconciled with it by the cold registration gate; if a reader finds
a disagreement after the seal, the block governs and the disagreement goes to review.

```json
{
  "schema": "joulewise-registration-windows/v1",
  "registration": "D-079 epoch 25G83 Revision 6",
  "identity_epoch": {
    "os_build": "25G83",
    "hardware_model": "Mac15,9",
    "power_policy": "ac_high_power",
    "sampling_interval_ms": 100,
    "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
    "pulse_protocol_id": "powermetrics_pulse_fiducial_v3"
  },
  "predecessor": {
    "acceptance_id": "d079_calibration_acceptance_v2_n17_r8",
    "path": "configs/calibration/calibration_acceptance_d079_v2_n17_r8.json",
    "file_sha256": "52e3d18a087bd8a0f28da6d20c3817da4d3ce532c604d7f049c78aad6a489a13",
    "derivation_sha256": "911d06c3db6e35a4d3a128a52ed47f0c483330a0429d9d87c2ad672185ed1acd",
    "basis_reading": "read P8 wherever R7 is named as a derivation basis; operatives identical"
  },
  "successor_acceptance_id_pattern": "d079_calibration_acceptance_v2_n<N>_25g83_r2",
  "retired_acceptance_ids": ["d079_calibration_acceptance_v2_n12_25g83_r1"],
  "disposing_decision_ids_required": [
    "D-126-disposition-25G83-v3-2026-09-25",
    "CAP-COUNCIL-25G83-01-E1-set-aside-W1W2-2026-09-29"
  ],
  "disposition_registry_sha256": "4a3d96da947d75c4ca84e4ef79630768e11977d4d8cd3592c36259217389effd",
  "set_aside_w1w2_content_ids": [
    "e055af15ca06ebaad7d3cd3dfc9163840219e6610a2e5e197b3cbbc76d64956f",
    "0af949aecb4d30109a9389637ac2c801ea1258284b0b20be6b5f90eb239c467c",
    "79bda70471f19d75ef63ee4b847b2908eaed554e474c623a2612ae392d82aa2d",
    "554d13ec9e9603e471cadfed74d0cbc36f4625f92e94ea942e7734353b5ea01d",
    "37dd0834396ea4337f510c4f4bddcdfdd6ce60afa495ccf5d79e6646d9d86dd3",
    "c1d9d5369b8317ade1c1d9229b5738b59ec733b51b931d033ccbf386731d132d",
    "641c1240dd6c523b5abb8096d84dfe67b1ad1a1307c2e705578a264530fb838e",
    "a9007b73fd91198f6d87fd5bc0195824543a18c4b751e408d6289b79e2ac2b41",
    "4ff672124f72ca261dd2e9063527abcb08108f588fbc75c45169ae926a7519cc",
    "2d81bed3f4b2f2b7c92b1488b465f53ed932ca982fea9a337086e4032dbbe3b9",
    "4154f1f4001e660d40ba88a60b40f3be11be2128deace4db14d02210eea295b2",
    "372eafc180693b3a21053ce2133472a8918fdf300730c04245cb709bd823ccb0"
  ],
  "sessions": {
    "session_kind": "derivation",
    "session_id_pattern": "^d079-epoch-25g83-r6-[0-9]{8}T[0-9]{4}Z$",
    "session_id_carries_order": false,
    "order": "ledger_capability_sequence",
    "sessions_of_this_registration": "every derivation-kind session opened after pins.ledger_head_pin_at_first_window",
    "windows_of_this_registration": "every session of this registration that is not a null session",
    "every_session_of_this_registration_must_be_named_at_issuance": true,
    "a_session_whose_id_does_not_match_the_pattern": "refuse",
    "null_session": {
      "definition": "a terminal session of this registration in which no slot has a finalized ledger row (no capture was attempted; every declared slot is unused)",
      "decided_by": "the issuer, from the ledger; never from the operator's naming",
      "is_a_window": false,
      "takes_a_window_label": false,
      "counts_toward": "nothing: not counted, valid, members, n, max_counting_windows, max_battery_replacement_windows or max_windows_total; not read by STOP-CADENCE or STOP-FUTILITY; not an adverse window",
      "count_rule_decision": "NEXT_WINDOW, unless STOP-NULL-REPEAT fires",
      "max_consecutive": 1,
      "listed_in_r9_record": "by session id and abort reason, with no slot entries",
      "start_condition_record_required": false,
      "a_session_with_one_or_more_finalized_slot_rows": "is a window",
      "source": "D-182 (a zero-capture refusal is not a window and licenses one successor); erratum REV6-25G83-01-E1 F4"
    },
    "declared_slots_per_session": 12,
    "settle_s": 600,
    "slot_pitch_s": 600,
    "final_slot_capture_budget_s": 480,
    "inter_window_min_gap_s": null,
    "inter_window_max_gap_s": null,
    "time_of_day_constraint": null
  },
  "start_state_conditions": [
    "previous_window_terminal_processes_exited_evidence_digests_in_ledger",
    "previous_window_blind_checks_done_and_count_rule_decision_is_NEXT_WINDOW",
    "agent_census_zero",
    {"no_thermal_throttling": {"argv": "/usr/bin/pmset -g therm", "every_CPU_Speed_Limit": 100, "checked": "t0"}},
    "battery_float_predicate_pass_A_R5b",
    {"network_time_off_receipt": {"argv": "/usr/bin/sudo -n /usr/sbin/systemsetup -setusingnetworktime off",
      "exit_status": 0, "stdout_exact": "setUsingNetworkTime: Off", "same_boot_as_first_capture": true,
      "min_age_before_first_capture_s": 600, "clocks": ["wall", "monotonic"], "receipts_per_window": 1}},
    {"clean_dwell": {"script": "scripts/prewindow_check.sh", "script_sha256": "pins.prewindow_check_sha256",
      "argv": "scripts/prewindow_check.sh --wait --timeout-s <s>", "window_argument": null, "required_exit_status": 0,
      "continuous_s": 600, "poll_s": 30, "reset_on_failed_poll": true,
      "timeout_s": "ceil(min(2700, remaining derivation start budget in seconds))",
      "subprocess_timeout_s": "min(2700, remaining derivation start budget in seconds)",
      "on_timeout": "the window does not start; the script exits 1 at its timeout",
      "named_daemons": ["XProtect", "mds_stores", "mdworker", "mdbulkimport", "backupd", "photoanalysisd", "softwareupdated", "Spotlight", "mediaanalysisd"],
      "named_daemon_match": "anywhere in a ps aux line, case-insensitive",
      "cpu_percent_per_named_daemon_max": 5.0, "load_average_1min_max": 2.0, "ac_power": true,
      "free_disk_gb_min": 20,
      "no_executable_name_matches": ["codex", "claude", "t3", "mcp-server", "run_campaign", "window-chain"],
      "executable_name_source": "ps -A -o comm=",
      "executable_name_match": "case-insensitive; remove leading whitespace and directory paths; exact name or name followed by hyphen, underscore, period or whitespace and any suffix; spaced names matched as a whole; argument text not matched",
      "load_limit_at_t0_by_night_gate": "one-shot path only; not on the quiet-admission path",
      "may_overlap_network_time_age": true}}
  ],
  "start_condition_evidence": {
    "record": "one committed file per window: for each of conditions a to g, the evidence file path and its sha256",
    "required_for": "every window; not for a null session",
    "first_session": "conditions a and b are recorded as not applicable",
    "after_a_null_session": "conditions a and b are read on the null session",
    "clean_dwell_entry_must_show": {"script_sha256_equals_pin": true, "exit_status": 0, "continuous_clean_s_min": 600},
    "issuer_refuses_if": ["a window has no record", "a condition has no entry", "a named evidence file is absent", "a named evidence file does not match its sha256", "the clean-dwell entry fails clean_dwell_entry_must_show"]
  },
  "definitions": {
    "adverse_window": "battery-float window verdict is battery_float_confounded or battery_float_evidence_missing (A-R5b)",
    "counting_window": "a window that is not adverse",
    "counted_capture": ["in_a_counting_window", "harness_report_cells_at_least_1", "median_frame_ms_at_least_100_and_at_most_150"],
    "valid_capture": ["in_a_counting_window", "ledger_disposition_valid"],
    "member": ["in_a_counting_window", "ledger_disposition_valid", "stored_anchor_v3_outcome_resolves", "median_frame_ms_at_least_100_and_at_most_150"],
    "counted_source": "the R9 record, committed and named by digest at issuance (harness report mode); the issuer does not recompute cells",
    "valid_source": "ledger",
    "member_source": "ledger disposition, stored anchor outcome, and the R9 record's median frame"
  },
  "count_rule": {
    "evaluated": "after each session's blind checks, before any B is read",
    "totals_are_over": "counting windows so far, in ledger order",
    "decision_order": [
      {"clause": 0, "if": "this session is a null session", "then": "NEXT_WINDOW", "unless": "STOP-NULL-REPEAT fires", "then_instead": "STOP_TO_REVIEW"},
      {"clause": 1, "if": "any stop line fired in this window", "then": "STOP_TO_REVIEW"},
      {"clause": 2, "if": "this window is adverse", "then": "NEXT_WINDOW"},
      {"clause": 3, "if": "counted_total >= 24 and members_total >= 12", "then": "CLOSE_AND_DERIVE"},
      {"clause": 4, "if": "counting_windows_done < 3", "then": "NEXT_WINDOW"},
      {"clause": 5, "if": "counted_total < 24", "then": "R9_COUNT_NOT_REACHED_TO_REVIEW"},
      {"clause": 6, "else": "MEMBERS_SHORT_TO_REVIEW"}
    ],
    "triggers_explained": [
      {"id": "T-count", "next_window_if": "counted_total < 24", "source": "A1 R9"},
      {"id": "T-members", "next_window_if": "members_total < 12", "source": "Rev 5; A2 section 3.6 item 7, read on members"}
    ],
    "combination": "any",
    "max_counting_windows": 3,
    "max_battery_replacement_windows": 1,
    "max_windows_total": 4,
    "issuable_outcome": "CLOSE_AND_DERIVE",
    "continuation_after_stop_or_review": "only by a sealed amendment to this registration; no command-line ruling",
    "review_means": "consult, cold gate or owner (D-186); never stop for good"
  },
  "stop_lines": [
    {"id": "STOP-CADENCE", "applies": "every counting window", "fires_if": "median of per-capture median native frame lengths > 150 ms", "consequence": "review", "source": "Rev 5 (W1 only), extended here"},
    {"id": "STOP-FUTILITY", "applies": "first counting window only", "fires_if": "valid captures in that window < 6", "consequence": "review", "source": "Rev 5"},
    {"id": "STOP-R9-CELL", "applies": "every window, adverse included", "fires_if": "any capture stopped on the cell count", "consequence": "campaign void; review", "source": "A1 R8(b), R9; cap ruling section 5 item 4"},
    {"id": "STOP-R9-DEADLINE", "applies": "every window, adverse included", "fires_if": "any capture stopped on the wall deadline", "consequence": "campaign void; review", "source": "A1 R8(b), R9; cap ruling section 5 item 4"},
    {"id": "STOP-R9-RATIO", "applies": "every window, adverse included", "fires_if": "any capture whose cell search ran has cells / cap > 0.5", "consequence": "campaign void; review", "source": "A1 R8(a), R9; cap ruling section 5 item 4"},
    {"id": "STOP-R9-FRAME", "applies": "every window, adverse included", "fires_if": "the harness cannot report a median frame for any capture whose finalized ledger row records a digest for its raw sampler bytes (bytes missing, digest mismatch, or no readable frame)", "consequence": "review; R9 not passed; the campaign is not void by this alone; nothing issues", "source": "A1 R9 fifth clause; A1 R0(d); erratum REV6-25G83-01-E1 F3"},
    {"id": "STOP-BATTERY-SECOND", "applies": "epoch", "fires_if": "a second adverse window", "consequence": "review", "source": "A-R5b"},
    {"id": "STOP-NULL-REPEAT", "applies": "sessions of this registration, in ledger order", "fires_if": "a null session whose preceding session of this registration was also a null session", "consequence": "review", "source": "D-182 (one successor); erratum REV6-25G83-01-E1 F4"}
  ],
  "sampling_dependence": {
    "computed": "once, by the issuer, over the members, after the last window is terminal and the R9 record is committed",
    "K": "number of counting windows that contribute at least one member",
    "q99_plain": {
      "stored_as": "prediction_99_two_draw_s",
      "formula": "t(0.995, n - 1) * sample_sd_presentation_s * sqrt(2)",
      "df": "n - 1",
      "rule_string": "the sealed TWO_DRAW_PREDICTION_RULE, unchanged"
    },
    "q99_within_window": {
      "stored_as": "prediction_99_within_window_two_draw_s",
      "s_within": "sqrt( sum over windows j, sum over members i of window j, of (B_ij - m_j)^2, divided by (n - K) ), m_j the mean B of window j's members; same Decimal working precision and same presentation quantum and rounding as sample_sd_presentation_s",
      "formula": "t(0.995, n - K) * s_within_presentation_s * sqrt(2), binary64, shortest round-trip decimal",
      "df": "n - K",
      "rule_string": "prediction_p_within_window_two_draw_s = t(p, n-K) * s_within_presentation_s * sqrt(2), evaluated in binary64 and recorded as its shortest round-tripping decimal",
      "rule_string_note": "recorded verbatim beside this value; the sealed TWO_DRAW_PREDICTION_RULE string says t(p, n-1) and is never used for it",
      "which_is_larger": "q99_within_window > q99_plain exactly when MSB / MSW < (r^2 - 1) * (n - K) / (K - 1), r = sqrt((n - 1) / (n - K)) * t(0.995, n - K) / t(0.995, n - 1); q99_within_window / q99_plain <= r; equal when K = 1",
      "quantile_proof_required_for_df": true
    },
    "c_rule": "C = max(predecessor_C, q99_plain, q99_within_window, S)",
    "thresholds": "none",
    "report_only": [
      "per window: member count, median, mean and sample SD of B, start time, start-to-start interval",
      "range of the window medians divided by S",
      "ICC = max(0, (MSB - MSW) / (MSB + (n0 - 1) * MSW)), MSB = sum_j n_j (m_j - m)^2 / (K - 1), MSW = s_within^2, n0 = (n - sum_j n_j^2 / n) / (K - 1); not computable if K < 2",
      "rho1 = Spearman rank correlation, average ranks for ties, over pairs (B of slot s, B of slot s+1) where both slots are members of the same window, pairs pooled over windows; with the pair count; not computable if fewer than 3 pairs"
    ],
    "never_changes": ["membership", "S", "the preflight level screen", "which windows run"]
  },
  "pins": {
    "chain_sha256": "b5beea464d392621631d9e5060e2c63c804676b28a5b2aea58b714c5cbead6fb",
    "validator_sha256": "3dc75857161b6bb9504f439d282bd39c2c5375e863cda1a514551a42d98b8a3f",
    "prewindow_check_sha256": "d8458eea588a746fb574dd39430f80d242c6a1c5746f7e6b676f78214bd7c9aa",
    "estimator_code_sha256": {
      "joulewise/powermetrics_fiducial.py": "bcdfeec06a03525cc6f6c700f2e2e6d10341af1323e4f9355b68ee47eb5bd30c",
      "joulewise/uncertainty_evidence.py": "b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8",
      "joulewise/adapters/powermetrics.py": "70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4",
      "joulewise/reduce.py": "7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc"
    },
    "cap_cells": 1710000,
    "harness_sha256": "692471b7672274aeeceb0655d8372aac3d2d0a9eff771828210099ae19cb6839",
    "cap_rule_text_sha256": "6b4bcaeade3f93199fddf0451f89e0e45c44ed55ad9873ab5bef8e938a92a4bf",
    "roster_sha256": "d8fbb403f291e8e9bfb26b6a3eb92551ddc7655b92f08aa0e767d41cdb8a75e7",
    "launch_template_sha256": [
      "e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8",
      "1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd"
    ],
    "ledger_head_pin_at_first_window": {"sequence": 276, "digest": "476e2ae857d4d6279bfa3c59c39bb5bc6f983d282948ce0abb95e3df62d49737"}
  }
}
```

At the seal, `cap_cells` and the ledger `sequence` are written as JSON integers, without
quotation marks.

**What the issuer checks from this block** (WI-13 implements these; each is a refusal):

- the registration contains no unfilled pin slot (the §13 grep prints 0);
- the sessions named at issuance are exactly the derivation-kind ledger sessions opened after
  the pinned ledger head, every one of their ids matches the pattern, and none is a W1, W2 or
  W3 session. The operator may not omit a session: not an adverse window, which A-R5b
  already requires the operator to name separately, and not a null session;
- a session is treated as null only when the ledger shows it terminal with no finalized slot
  row. The issuer decides this itself from the ledger;
- each window's start-condition record (§6.2) is present: it has an entry for each of (a) to
  (g), every evidence file it names exists and matches its sha256, and its entry for (g)
  shows the pinned script digest, exit status 0 and a clean dwell of at least 600 s. A null
  session needs no record;
- every session declared 12 slots;
- the R9 record is present, its digest equals the one named at issuance, it covers exactly
  the named sessions, and every clause of R9 in it passes;
- when the count rule is replayed over the windows in ledger order, using the R9 record for
  counted and median frames and the ledger for dispositions and anchor outcomes, every session
  after the first was opened on a NEXT_WINDOW decision, no session exists after any other
  decision, and the last decision is CLOSE_AND_DERIVE;
- the first counting window has at least 6 valid captures;
- the predecessor is P8 by identifier and file digest;
- both decision identifiers are declared;
- the successor's identifier matches the approved pattern and is not the retired r1 id;
- the member count n is at least 12.

The issuer's old refusal text "requires r7 predecessor" is reworded when the issuer is changed
(A2 §3.6).

## 8. Membership, exclusions and issuance

These rules are unchanged from Revisions 1 and 5 except where marked "added".

- **Members.** Every capture of this registration's sessions that meets all of these
  conditions is a member:
  - its disposition is `valid`;
  - its stored anchor-v3 outcome resolves;
  - its median frame lies in 100–150 ms inclusive (added: A1 R7);
  - it belongs to a counting window.

  No capture is excluded on the basis of its B. There is no top-up and no retry, and no window
  is opened or withheld because of B.
- **Exclusions**, each recorded with its named mechanism and its ledger row retained:
  - `affine_clock_fit_empty` (Revision 1);
  - a failed protocol gate, which leaves the capture ordinary-invalid;
  - a recorded operator or system event;
  - `frame_out_of_covered_range`: a median frame outside 100–150 ms. The capture is flagged in
    the window report, is not a member and is not counted (added: A1 R7);
  - an adverse window (A-R5b).
- **R9 failure voids the campaign (added: cap ruling §5 item 4).** If STOP-R9-CELL,
  STOP-R9-DEADLINE or STOP-R9-RATIO fires, R9 has failed. The campaign is void: its captures
  are diagnostics and are never members under any cap.
- **A count shortfall does not void by itself (added).** If the count rule ends in
  R9_COUNT_NOT_REACHED_TO_REVIEW or MEMBERS_SHORT_TO_REVIEW, nothing issues and B stays
  unread. The captures keep their ledger dispositions. The review decides what follows and
  records it; it cannot make these captures members except by a sealed amendment.
- **An unreported median frame does not void by itself (added).** If STOP-R9-FRAME fires,
  R9 has not passed. Nothing issues and B stays unread, on the same terms as a count
  shortfall (§4 gives the reason).
- **Issuance** follows Revision 5:
  - n ≥ 12 members is the floor;
  - S = max(range of the members' B quantized to 1e-6 s ROUND_HALF_EVEN, 0.010818 s);
  - Q99 and the quantile proof as Revision 1 specifies them;
  - C = max(predecessor C, Q99, the window-blocked Q99 of §9, S);
  - `zero_headroom` is recorded when C = S;
  - any member B > 0.25 s (`PLATEAU_INSET_S`) refuses issuance;
  - two or more members with B > 0.075 s mark the candidate `excursion_limited`;
  - the preflight level screen is the largest member B quantized to 1e-15 s;
  - the predecessor screen challenge is a diagnostic only.

## 9. Back-to-back windows: what they do to the statistics

**The forcing problem.** Revision 5 spaced windows at least 6 h apart, and this revision does
not. Q99 treats the n member values as n independent draws from one population. Windows taken
close together could break that in two ways:

- **Window effect:** something that lasts a whole window (a thermal or background state)
  shifts all of that window's captures together.
- **Serial dependence:** each capture resembles the one taken just before it.

The question is whether either makes C wrong in a way that matters, and in which direction.

**What C is used for decides the answer.** C is compared with a bracket's drift, and a
bracket's two captures always come from the *same* window (§0). So the
quantity C must cover is the difference between two captures inside one window. The picture
shows why that matters:

```text
 B (seconds):        smaller ------------------------------------> larger

 window A captures:      a  a aa a   a
 window B captures:                        b  b bb  b b
                        |<--- wA --->|    |<--- wB --->|
                              mA                 mB
                               |<------ d ------>|
```

- Each `a` or `b` is one member's B.
- `wA` and `wB` are the spread of B inside window A and inside window B.
- `mA` and `mB` are the two windows' mean B.
- `d` is the shift between the windows, the window effect.

A bracket's drift is set by the spread inside a window (`wA`, `wB`). It never sees `d`. The
plain sample SD of all members, which Q99 uses, contains both the inside spread and part of
`d`. A window effect therefore makes the plain Q99 *larger* than the drift it has to cover,
not smaller.

**The rule: one second value, always computed, no threshold.** After the last window is
terminal and the R9 record is committed, the issuer computes over the members:

- **s_within**, the window-blocked SD: take each member's distance from its own window's mean
  B, square, sum over all members, divide by n − K, take the square root. K is the number of
  counting windows that contribute at least one member. s_within measures the spread inside
  windows only and is untouched by any shift between windows. It has n − K degrees of
  freedom, because one mean is estimated per window.
- **Q99_within** = t(0.995, n − K) × s_within × √2. The arithmetic is that of Revision 1
  (evaluated in binary64, recorded as the shortest round-trip decimal), with s_within
  computed at the same Decimal precision and presentation quantum as the sample SD. Its
  quantile proof is run and recorded for df = n − K, as for df = n − 1. Each value is
  recorded beside a **rule string**, a fixed sentence in the calibration file that states
  the formula used. The sealed string for Q99 (`TWO_DRAW_PREDICTION_RULE`) says `t(p, n-1)`,
  which would misdescribe Q99_within. So Q99_within is recorded under its own string, and
  the Q99 string is never reused for it:
  `prediction_p_within_window_two_draw_s = t(p, n-K) * s_within_presentation_s * sqrt(2), evaluated in binary64 and recorded as its shortest round-tripping decimal`.
- **C = max(predecessor C, Q99, Q99_within, S).** The larger value sets C.

Nothing is tested and nothing is flagged, so there is no threshold to choose after the data
are seen. S, membership, the level screen and the window sequence never change because of
these statistics, and no B-based exclusion follows from them.

**Why the larger value is the safe choice.** C only decides whether a bracket is refused; a
bracket that passes always carries its own drift in its reported bound (§0). A C that is too
small refuses healthy brackets, and refusals that depend on the machine's state are a filter
on the data. A C that is too large admits a bracket whose bound is honestly widened by its
drift. Neither error makes a reported bound too small. Taking the larger value avoids the
filter.

**How far apart the two values can be.** Because the total sum of squares is never smaller
than the within-window sum of squares, Q99_within can exceed Q99 by at most the factor
r = √((n − 1)/(n − K)) × t(0.995, n − K)/t(0.995, n − 1). That factor is 1.027 for n = 24 in
two windows, 1.033 for n = 36 in three, and 1.157 at the extreme of n = 12 in three (the
fewest members and the most counting windows this revision allows). With K = 1 the two
values are equal.

**Which of the two is the larger.** One ratio decides it. Write n_j and m_j for window j's
member count and mean B, and m for the mean B of all members. The **between-window mean
square** is MSB = Σ n_j (m_j − m)² / (K − 1): it measures how far the window means sit from
the overall mean. The **within-window mean square** is MSW = s_within². The two are scaled
so that, when there is no window effect at all, MSB equals MSW on average. Their ratio
**F** = MSB / MSW is therefore near 1 by chance alone, and well above 1 when the windows
differ. Q99_within is the larger exactly when

```text
 F  <  (r² − 1) × (n − K) / (K − 1)
```

That limit is 1.45 for n = 12 in two windows, 1.52 for n = 12 in three, 1.19 for n = 24 in
two, 1.20 for n = 24 in three and 1.12 for n = 36 in three. Since chance alone puts F near
1, which is below every one of these limits, Q99_within is the larger in most campaigns that
have no window effect: about 70 % of them (67 % to 74 % across these shapes, in 20,000
simulated campaigns of invented data per shape). It is not a sign that the windows are
unusually alike. When the windows differ by more than the limit, Q99 is the larger and sets
C, as under Revision 5.

So this rule can never lower C below Revision 5's value. It can raise C by at most the
factor r: 15.7 % at the extreme of n = 12 in three windows, and at most 5.6 % when n is 24
or more.

**Worked example with real numbers** (the 12 set-aside W1/W2 values, a disclosed design
input of §3, used here only to show the arithmetic): n = 12 members in K = 2 windows of 6.
The sample SD of all twelve is 0.004330 s, and t(0.995, 11) = 3.105807, so Q99 = 3.105807 ×
0.004330 × 1.414214 = 0.01902 s. The pooled SD inside windows is 0.004137 s, and
t(0.995, 10) = 3.169273, so Q99_within = 3.169273 × 0.004137 × 1.414214 = 0.01854 s. Q99 is
the larger, as the ratio predicts: F = 2.05 here, above the limit of 1.45 for this shape. Q99
would set C if it is also above S and the predecessor's ceiling.

**Worked example with invented numbers** (n = 36 in K = 3 windows of 12; t(0.995, 35) =
2.723806 and t(0.995, 33) = 2.733277):

- Windows that differ: sample SD 0.0040 s, s_within 0.0030 s, so F = 14.6, far above the
  limit of 1.12. Q99 = 0.015408 s; Q99_within = 0.011596 s. Q99 sets C.
- Windows whose means nearly coincide: sample SD 0.0040 s, s_within 0.0041 s, so F = 0.16,
  below the limit. Q99 = 0.015408 s; Q99_within = 0.015848 s. Q99_within sets C, 2.9 % above
  Q99.

**What is recorded and reported, and gates nothing.** The candidate's derivation notes
record, for a reader to judge the windows by:

- per window: the member count, the median, mean and sample SD of B, the start time and the
  start-to-start interval from the previous window;
- the range of the window medians, divided by S;
- **ICC**, the intraclass correlation: the share of B's variance that lies between windows.
  With n_j and m_j window j's member count and mean, m the mean of all members, MSB =
  Σ n_j (m_j − m)² / (K − 1), MSW = s_within², and n0 = (n − Σ n_j² / n) / (K − 1): ICC =
  max(0, (MSB − MSW) / (MSB + (n0 − 1) × MSW)). Not computable when K < 2;
- **ρ1**, the serial correlation: the Spearman rank correlation (the ordinary correlation of
  the ranks, with tied values given their average rank) between a member's B and the B of the
  member in the next slot of the same window, over every such pair of adjacent member slots,
  pooled over windows, with the number of pairs. A pair is formed only when both adjacent
  slots are members; a gap is not bridged. Not computable with fewer than 3 pairs;
- both Q99 values and which term of the maximum set C.

**What this rule does not correct, stated plainly.**

- Serial dependence is reported, not corrected. ρ1 is measured between adjacent slots, whose
  captures start 600 s apart. If neighbours resemble each other (ρ1 above zero), two captures
  that close together differ by less than Q99_within predicts, so C errs large. If neighbours
  alternate (ρ1 below zero), they differ by more, so C errs small and a healthy bracket may be
  refused. Neither can make a reported bound too small. This revision does not establish how
  far apart in time a bracket's two captures are. If they are further apart than adjacent
  slots, the effect of serial dependence on C weakens toward none; it does not reverse.
- The arithmetic assumes every window has the same inside spread. The per-window SDs are
  reported so that a reader can see whether that held.
- Close windows sample fewer machine states than spaced ones. The level screen and S come
  from the states the windows happened to see. A later claim window in a state outside them
  is refused or marks the calibration stale; it cannot yield a wrong number.
- These statistics never cause a window to be added, dropped or re-run.

## 10. Blindness and sequence

These are unchanged from Revision 5 except for the dry run's allowed contents.

- No B value, screen or statistic of these windows is read by any person or agent before two
  things are true: the last window's session is terminal, and the R9 record has been committed.
- `prepare-candidate` refuses while any session of the registration is open.
- Between windows, the count-only dry run and the harness report may state: session kinds and
  states; declared and filled slots; valid counts; exclusions by mechanism; median frames; and,
  per capture, cells, cells ÷ cap, disposition and stop trigger. They state no B, no screen
  and no comparison with either.
- The R9 record is an ancestor of every commit that carries a B of these windows.
- This registration authorizes no claim window. H1 stands until the closing ruling of E1 §4
  step 18.

## 11. Stop lines kept

These are kept from Revision 5 and the cap rule. Each sends its question to review.

- **Cadence:** a counting window whose median of per-capture median native frame lengths is
  above 150 ms stops the sequence. Revision 5 applied this at W1 only; here it applies after
  every counting window, because development blocks may fall between windows and the covered
  frame range of the cap rule ends at 150 ms. The window's cadence report is read from raw
  plists before any B.
- **Futility:** the first counting window with fewer than 6 valid of 12 stops the sequence.
- **Battery:** an adverse window is replaced once (A-R5b). A second adverse window stops the
  sequence.
- **Cap rule R8 and R9**, read on every window, adverse or not:
  - any capture stopped on the cap or on the wall deadline stops the sequence, and R9 fails;
  - any capture whose cell search ran with cells ÷ cap above 0.5 stops the sequence, and R9
    fails. This reads R9's word "every" literally: it includes a capture outside the frame
    range;
  - a capture outside 100–150 ms is flagged, is not a member and is not counted;
  - any capture that has a recording and whose median frame the harness cannot report stops
    the sequence (STOP-R9-FRAME). R9 has not passed; the campaign is not void by this alone
    (§4).
- **Null sessions:** a null session following a null session stops the sequence
  (STOP-NULL-REPEAT, §7).
- **Count exhaustion:** see §7 clauses 5 and 6.
- **Issuance floor and refusals:** see §8.

The value of the cap is never adjusted between captures or between windows (A1 R10). A later
change to a pinned estimator file restarts the cap rule (A1 R12). A fix in the calibration
derivation path means these windows are re-run under a new revision (E1 step 17; directive
#416 item 3).

## 12. What this revision does not change

It leaves unchanged:

- the identity epoch, the machine pins and the launch context;
- protocol v3 and the window shape except spacing;
- the membership, exclusion and analysis rules of Revisions 1 and 5, except where §8 and §9
  add to them;
- the TWO_DRAW_PREDICTION_RULE string, which goes on describing Q99 alone (§9 adds a second
  string for Q99_within), and the quantile-proof bounds;
- the A-R5b battery-float rule except its spacing clause;
- the Revision 1 known conditions;
- any sealed text concerning W1 and W2.

It publishes no number, licenses no measurement and arms no window.

## 13. Seal procedure

1. Replace every pin slot with its value, taken at the head the first window will be armed
   from.
2. Run `grep -c -E 'TO BE PINNED AT S[E]AL'` on this file. It must print 0.
3. Replace the header's parenthetical "(DRAFT 2026-09-30; sealing pending the pins below)"
   with "(sealed <YYYY-MM-DD> at <first 8 hex of the sealing commit>)", and the first words
   of the STATUS line, "draft until sealed", with "sealed".
4. Confirm the fenced `json` block of §7 parses, and that a test compares its
   `pins.chain_sha256` with the tracked chain script.
5. Pin the sha256 of the whole registration file in the first window's arm material.
6. Owner approval: the owner's answer of 2026-09-29 (record item 46, "Approve all four") is the
   approval E1 step 12 requires. The cold registration gate changed none of the three things
   the owner approved there (the P8 name, the successor pattern, and the rule that the 12 rows
   do not count toward doubling), so the seal needs no second ask. The seal notice to the
   owner carries the doubling arithmetic of §3.
