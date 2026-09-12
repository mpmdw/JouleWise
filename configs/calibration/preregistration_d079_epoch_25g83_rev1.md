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
