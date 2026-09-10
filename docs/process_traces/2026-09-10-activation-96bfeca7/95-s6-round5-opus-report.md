# S6 round 5 — pre-registration + contract, Opus seat report

Worktree `/Users/edr/code/JouleWise-wt-s6-docs-prereg`, branch
`feat/2026-09-10-epoch-s6-docs-prereg`, base HEAD `8bdead19`. No git state
changed (no add/commit/checkout); the canonical tree was never touched.

Write scope used: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`
and `docs/contracts/powermetrics_fiducial.md` (cold-gate-46 addendum sections
only). `docs/decision_log.md` was IN scope but is UNTOUCHED — see §5.

## 1. What landed, item by item

**Item 1 (S4 contract refuter SF-5) — the quantile proof is now on the
authority-side record.** The pre-registration's Analysis section gains two
paragraphs stating the mechanical proof and its two bounds: the forward check
(Student-t survival P(T > t) from the regularized incomplete beta by continued
fraction, evaluated at the returned quantile, must reproduce 1 - p with
absolute residual <= 1e-30) and the independent route (Abramowitz & Stegun
26.7.3 odd df / 26.7.4 even df finite closed form for P(|T| <= t), inverted by
its own bisection over (0, 100), pi by Machin, agreeing to >= 30 significant
decimal digits), both probabilities 0.975 and 0.995, 80-digit Decimal working
precision, everything recorded in the candidate's `quantile_proof` block, and
either miss refusing `quantile_proof_failed`. The second paragraph says the
bounds are the ISSUER'S DECLARED bounds, not a ratified constant, and gives the
conservatism argument against the 20 published decimal places (30 significant
digits on a quantile of order 2-3 is ~29 decimal places, nine more than are
printed; the 1e-30 residual is in PROBABILITY, and at a one-tail density of
0.05 down to 0.01 per unit t it is an error of order 1e-29 to 1e-28 in t).

**Item 2 (SF-5 companion / the "re-derivation" divergence, refuter F-7) — the
glossary and the membership/exclusion text now describe what the code does.**
`Anchor-v3 replay` is redefined as READING the capture's stored anchor-v3
outcome back out of primary evidence bytes and AUTHENTICATING those bytes by
SHA-256 against the ledger row (`manifest.json` and `instrument_evidence.json`
both, before any field is read; stored `b_fiducial_s` must equal the row's
`exact_bound_lexeme_s`), citing CG46 R-d (`stored_lexeme_is_member_value:
True`) for why the stored outcome IS the derivation for a fresh v3 capture.
`affine_clock_fit_empty` is stated as the stored-outcome value that excludes a
member, and as the ONLY registered exclusion mechanism at that step (any other
reason refuses issuance instead of excluding). Not overstated: the one place a
value is recomputed from primary bytes is named — the historical r-series
(n = 17) generations, captured before the writer had an anchor-v3 path, whose
stored scalars were superseded offline under the rate-aware set-membership
estimator, which is why `tests/verify_calibration_acceptance_corpus.py` banks
`stored_lexeme_is_member_value: False` for them.

**Item 3 (SF-1) — the Blindness clause now carries its enforcement.**
`prepare-candidate` refuses while any registration session is not terminal
(terminal = last declared slot final, or aborted), naming the open session;
`check`'s registration dry run reports only kinds, states, declared/filled slot
counts, and per-mechanism exclusion counts — no value, screen, statistic, or
comparison. Described as installed by the issuer, by SUBCOMMAND NAME only, with
no file:line (S4 round 2 is installing both; nothing in the text asserts a line
this seat could not verify).

**Item 4 (S6 round-4 residue SF-4) — the contract's kind-check paragraph is
corrected.** `systematic_screen_kind_mismatch` is no longer presented as a
refusal code. The text now says the disagreement raises
`calibration_reservation_input_invalid`
(`RefusalCode.RESERVATION_INPUT_INVALID`) carrying context `reason:
systematic_screen_kind_mismatch` plus the `session_kind` seen, spells out that
grepping the code registry for the reason string finds nothing and that callers
must match the code and then read the reason, and names the writer-side half as
a real code, `calibration_derivation_session_requires_derivation_only`
(`RefusalCode.DERIVATION_SESSION_REQUIRES_DERIVATION_ONLY`), refusing before the
writer lease so nothing is appended and no custody exists.

Every `NOT YET LANDED` / cold-gate-46 status line is intact and outside every
hunk (`docs/contracts/powermetrics_fiducial.md:95`, `:232-233`, `:312-313`;
diff contains no such line).

## 2. Verification commands and outputs

Names and bounds verified against code, all read via `git show HEAD:` (never a
working file in another seat's worktree):

```
$ git -C /Users/edr/code/JouleWise-wt-s4-issuer-prepare show HEAD:scripts/issue_calibration_acceptance_generation.py | grep -n "QUANTILE_PROOF\|DECIMAL_WORK_PRECISION ="
172:DECIMAL_WORK_PRECISION = 80
205:QUANTILE_PROOF_MINIMUM_AGREEMENT_DIGITS = 30
206:QUANTILE_PROOF_MAXIMUM_FORWARD_RESIDUAL = Decimal(1).scaleb(-30)
207:QUANTILE_PROOF_PROBABILITIES = ("0.975", "0.995")
```

`build_quantile_proof` (`:450-501`): forward residual
`abs(student_t_survival(value, df) - (1 - p))` refused when
`> QUANTILE_PROOF_MAXIMUM_FORWARD_RESIDUAL`; `_agreement_digits(value,
student_t_quantile_closed_form(...))` refused when
`< QUANTILE_PROOF_MINIMUM_AGREEMENT_DIGITS`; both refusals are
`quantile_proof_failed`. Recorded keys: `quantiles` (quantized 1e-20
ROUND_HALF_EVEN), `forward_residuals`, `forward_residual_bound`,
`closed_form_agreement_digits`, `closed_form_agreement_bound`,
`closed_form_method` ("Abramowitz & Stegun 26.7.3 (odd df) / 26.7.4 (even df)
finite closed form, inverted by bisection; pi by Machin's formula"),
`precision`. Both bisections run `for _ in range(300)` over `(0, 100)`; the
closed form uses `_machin_pi()`.

Member selection (`_select_members` `:678-741`, `anchor_v3_replay_outcome`
`:617-644`): reads `evidence["clock_anchor"]`, refuses a non-v3 `method`,
returns the stored detail on unresolved; hashes checked in `_read_member_evidence` (`:576-607`, `artifact_hashes` at `:586`)
(`manifest.json`, `instrument_evidence.json` vs `observation.artifact_sha256`);
stored `b_fiducial_s` compared to `observation.exact_bound_lexeme_s`;
`REGISTERED_CORPUS_EXCLUSION_REASONS` is `frozenset({"affine_clock_fit_empty"})`
(`joulewise/calibration_bracketing.py:252`) and an unregistered reason raises
`PrepareRefusal`. Its docstring cites "ruling 46 R-d: a fresh v3 capture
stores its own value".

```
$ git -C /Users/edr/code/JouleWise-wt-s1-writer-derivation show HEAD:joulewise/calibration_exits.py | sed -n '100,102p'
    DERIVATION_SESSION_REQUIRES_DERIVATION_ONLY = (
        "calibration_derivation_session_requires_derivation_only"
    )
# :61  RESERVATION_INPUT_INVALID = "calibration_reservation_input_invalid"
# :230 RESERVATION_INPUT_INVALID: "bracket session reservation is malformed"
# :263 DERIVATION_SESSION_REQUIRES_DERIVATION_ONLY: "a derivation-kind session slot is capturable only in derivation-only mode"

$ git -C /Users/edr/code/JouleWise-wt-s2-ledger-sessions show HEAD:joulewise/calibration_ledger.py | grep -n systematic_screen_kind_mismatch
5485:                    "reason": "systematic_screen_kind_mismatch",
```

Its call site (`:5477-5488`) is
`raise CalibrationLedgerError(RefusalCode.RESERVATION_INPUT_INVALID,
context={"reason": "systematic_screen_kind_mismatch", "session_kind":
session.session_kind})` — confirming SF-4: a context reason, not a code.

CG46 R-d read at
`/Users/edr/code/JouleWise-wt-bk-96bfeca7/docs/process_traces/2026-09-10-activation-96bfeca7/46-coldgate-packet-epoch-bootstrap/10-coldgate-fable-ruling.md`
(landing-order paragraph): "the `tests/verify_calibration_acceptance_corpus.py`
row (`stored_lexeme_is_member_value: True`, a fresh v3 capture stores its own
value)".

Docs tests:

```
$ out=$(PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness 2>&1); rc=$?
...............................
----------------------------------------------------------------------
Ran 31 tests in 0.929s

OK
rc=0
```

## 3. First-use table (every term of art introduced or relied on by these hunks)

| Term | Where built | How |
| --- | --- | --- |
| Anchor-v3 replay | PR glossary (rewritten) | built as reading + hash-authenticating a STORED outcome, with what is hashed, what must match, and what refuses |
| `affine_clock_fit_empty` | PR glossary, same bullet | built as the stored clock-anchor state "no feasible affine fit", then used in Exclusions as the only registered mechanism |
| `stored_lexeme_is_member_value` | PR glossary, same bullet | built by contrast: `False` for the r-series (offline re-derivation), `True` for captures storing their own anchor-v3 result |
| t(p, df) | PR glossary (new) | built in words as the two-sided Student-t quantile with df = n − 1, BEFORE Analysis uses `t(0.975, n-1)` |
| Two-draw prediction | PR glossary (new) | built as t(p, n−1) × sample SD × √2 with its meaning (how far apart two fresh draws fall); Q99 redefined in its terms |
| Forward check | PR Analysis, at first use | glossed in the same sentence: survival evaluated AT the returned quantile reproduces 1 − p |
| Independent route | PR Analysis, at first use | glossed as a second production of the same quantile sharing no code with (a), with the A&S formula numbers, the inversion method, and the pi source |
| Significant decimal digits (30) | PR Analysis, second paragraph | converted to decimal places for a quantile of order 2–3, so the comparison with the 20 published places is explicit |
| Residual "in PROBABILITY" | PR Analysis, second paragraph | built by naming the density that converts it to an error in t |
| `b_fiducial_s` (used in the anchor bullet) | PR glossary, inline | glossed at that use ("the capture's fiducial bound in seconds, next bullet") because its own bullet follows |
| `quantile_proof_failed` | PR Analysis, at first use | named as the refusal either miss raises, with its consequence (nothing issues) |
| Terminal (session) | PR Blindness, at first use | glossed inline: last declared slot final, or aborted |
| Context reason vs refusal code | Contract, kind-check | built explicitly, including the grep-the-registry consequence for a reader and the match-then-read rule for a caller |
| `calibration_derivation_session_requires_derivation_only` | Contract, kind-check | named with its registry symbol, its human message, and when it fires (before the writer lease) |

No word left doing unpaid work: "replay", "derivation", "terminal",
"declared bounds", and "reason" each have their meaning before their first
load-bearing use, and the two bounds are stated as numbers with their
justification rather than as an adjective ("conservative") alone.

## 4. Diff hunks

```diff
diff --git a/configs/calibration/preregistration_d079_epoch_25g83_rev1.md b/configs/calibration/preregistration_d079_epoch_25g83_rev1.md
index f3b7a17b..03422963 100644
--- a/configs/calibration/preregistration_d079_epoch_25g83_rev1.md
+++ b/configs/calibration/preregistration_d079_epoch_25g83_rev1.md
@@ -47,8 +47,28 @@ is fixed here first.
   its cutoff receipt. **Corpus** — the subset of the prior set whose values
   the statistics are computed from. **Retained n** is the corpus size.
-- **Anchor-v3 replay** — re-deriving a capture's fiducial bound from its
-  primary evidence bytes with the anchor-v3 estimator. A capture whose
-  clock-anchor feasibility model admits no feasible affine fit does not
-  resolve (`affine_clock_fit_empty`) and cannot be a corpus member.
+- **Anchor-v3 replay** — reading a capture's STORED anchor-v3 outcome back
+  out of its primary evidence bytes; not recomputing it. The anchor-v3
+  estimator runs inside the writer at capture time and records its result —
+  the `clock_anchor` record and the fiducial bound — in that capture's
+  `instrument_evidence.json`. Cold gate 46 §R-d settles that for a capture
+  taken fresh under anchor-v3 the stored result IS the derivation
+  (`stored_lexeme_is_member_value: True`), so the issuer authenticates those
+  bytes instead of repeating the fit: both `manifest.json` and
+  `instrument_evidence.json` must hash (SHA-256) to the digests the ledger row
+  recorded before any field is read, and the stored `b_fiducial_s` (the
+  capture's fiducial bound in seconds, next bullet) must equal the row's
+  `exact_bound_lexeme_s`. Any one of the three mismatching refuses. A capture whose
+  stored `clock_anchor` shows the clock-anchor feasibility model admitted no
+  feasible affine fit did not resolve (`affine_clock_fit_empty`) and is
+  excluded, listed with that mechanism; a `clock_anchor` recorded under any
+  method other than anchor-v3 is not an anchor-v3 replay at all and refuses
+  rather than counting as resolved. Where a value IS recomputed from primary
+  bytes is historical and not this registration: the r-series (n = 17)
+  generations SUPERSEDED the scalars their bundles had stored with values
+  re-derived offline from primary bytes under the rate-aware set-membership
+  estimator — which is why `tests/verify_calibration_acceptance_corpus.py`
+  banks `stored_lexeme_is_member_value: False` for those generations, and
+  `True` for a generation whose captures store their own anchor-v3 result, as
+  this registration's do.
 - **`b_fiducial_s`** — the capture's fiducial bound in seconds: the value a
   corpus member contributes to the statistics.
@@ -59,6 +79,12 @@ is fixed here first.
 - **Level screen** — an acceptance's corpus maximum, the preflight threshold a
   capture's bound is compared against. **Bracket screen (S)** — its corpus
-  range. **Budget ceiling (C)** — its maximum budgetable drift. **Q99** — the
-  99 % two-draw prediction computed from a corpus. **Predecessor ceiling** — the
+  range. **Budget ceiling (C)** — its maximum budgetable drift. **t(p, df)** — the
+  two-sided Student-t quantile: the multiple of an estimated standard
+  deviation that a t-distributed quantity stays within in absolute value with
+  probability p, when the estimate carries df degrees of freedom (df = n − 1
+  for a corpus of n members). **Two-draw prediction** — t(p, n−1) × sample SD
+  × √2, the half-width that predicts how far apart two fresh draws from the
+  same population fall at confidence p. **Q99** — the two-draw prediction at
+  p = 0.995, computed from a corpus. **Predecessor ceiling** — the
   predecessor generation's budget ceiling.
 
@@ -100,13 +126,17 @@ acceptance of this epoch exists. Whether the bound exceeds r6's preflight_level_
 in the hashed evidence as a diagnostic only.
 
-Membership. The corpus is every observation of this registration whose ledger disposition is valid and whose anchor-v3
-replay from primary bytes resolves. No observation is excluded on the basis of its b_fiducial_s. Every member carries
-the target epoch and belongs to a session of this registration; a valid same-epoch observation outside this registration
-refuses issuance rather than being absorbed. Valid registered observations excluded by replay are listed in
-derivation_notes.excluded_members with their named mechanism, member_id, manifest_sha256 and instrument_evidence_sha256;
-the prior-set row is matched by the content id derived from those two hashes.
-
-Exclusions (mechanism-named, outcome-independent, decided before capture). An observation is excluded only if (a) the
-estimator's clock-anchor feasibility model refuses it on replay (affine_clock_fit_empty, the r6 exclusion class);
+Membership. The corpus is every observation of this registration whose ledger disposition is valid and whose STORED
+anchor-v3 outcome, read back from hash-authenticated primary bytes, resolves (glossary: Anchor-v3 replay — the issuer
+reads the recorded clock_anchor and authenticates the bytes; it does not re-run the estimator over the trace). No
+observation is excluded on the basis of its b_fiducial_s. Every member carries the target epoch and belongs to a
+session of this registration; a valid same-epoch observation outside this registration refuses issuance rather than
+being absorbed. Valid registered observations whose stored outcome does not resolve are listed in
+derivation_notes.excluded_members with their named mechanism, member_id, manifest_sha256 and
+instrument_evidence_sha256; the prior-set row is matched by the content id derived from those two hashes.
+
+Exclusions (mechanism-named, outcome-independent, decided before capture). An observation is excluded only if (a) its stored
+anchor-v3 record shows the estimator's clock-anchor feasibility model admitted no feasible affine fit
+(affine_clock_fit_empty, the r6 exclusion class, and the ONLY exclusion mechanism registered at this step: an
+unresolved anchor carrying any other reason refuses issuance instead of quietly excluding the member);
 (b) a protocol gate fails (plateau, SNR, 59-pulse detection, spurious plateau, edge coverage), which the writer records
 as ordinary-invalid; or (c) a recorded operator or system event interrupted the window. Every exclusion is recorded with
@@ -120,5 +150,11 @@ ruling, not this registration's. No top-ups, retries, early stops, or outcome-dr
 
 Blindness. No member value, screen, or statistic is examined by any person or agent before the third night's session is
-terminal and its pin candidate is emitted.
+terminal and its pin candidate is emitted. The fence is installed by the issuer, not left to convention. prepare-candidate
+refuses to run while any session named in the registration is not terminal — terminal meaning its last declared slot is
+final or the session was aborted — and names the session it found open, so the statistics cannot be computed early even
+by accident. check's registration dry run, the one route that may be run mid-campaign, reports only the named sessions'
+kinds and states, how many slots are declared and how many are filled, and how many observations are excluded under each
+named mechanism; it reports no member value, no screen, no statistic, and no comparison against one. A mid-campaign look
+can answer whether the campaign is on schedule and cannot answer what the campaign got.
 
 Screen challenge. If two or more retained members exceed 0.032898493715362, the corpus is not issued and Ed rules in
@@ -128,7 +164,32 @@ membership.
 
 Analysis. Decimal statistics exactly as r6: minimum, maximum, range, mean, sample SD; t(0.975, n-1) and t(0.995, n-1)
-two-draw predictions. The three-night schedule admits retained n from 19 (the required floor) to 36 (all declared
-slots retained), so the degrees of freedom n-1 run from 18 to 35 — or from 16 if Ed's written n = 17 ruling is exercised; the quantile implementation's proof for the REALIZED
-df is computed and recorded before issuance, and no corpus issues on a df whose quantile is not proven in that record.
+two-draw predictions (both terms defined in the glossary above). The three-night schedule admits retained n from 19
+(the required floor) to 36 (all declared slots retained), so the degrees of freedom n-1 run from 18 to 35 — or from 16
+if Ed's written n = 17 ruling is exercised; the quantile implementation's proof for the REALIZED df is computed and
+recorded before issuance, and no corpus issues on a df whose quantile is not proven in that record.
+
+Quantile proof, mechanically, so that an authority-side reader can find it. For each of the two probabilities 0.975 and
+0.995, at 80-digit Decimal working precision, the issuer runs two checks on the quantile it returns for the realized df.
+(a) Forward check: the Student-t survival function P(T > t) — computed from the regularized incomplete beta function by
+continued fraction — evaluated AT the returned quantile must reproduce 1 - p, with absolute residual at most 1e-30.
+(b) Independent route: the same quantile is produced a second time by a route sharing no code with (a). That route is the
+exact Abramowitz and Stegun finite closed form for P(|T| <= t) at integer df (26.7.3 for odd df, 26.7.4 for even df),
+inverted by its own bisection over t in (0, 100) — 300 halvings, which resolves t to about 1e-88, far finer than the
+working precision needs — with pi computed independently by Machin's formula rather than taken from a library. The two
+quantiles must agree to at least 30 significant decimal digits. Both routes' evidence is recorded in the candidate's
+quantile_proof block: the quantiles at 20 decimal places, the per-probability forward residuals, the per-probability
+agreement digit counts, both bounds, the closed-form method string, and the working precision. A miss on either check
+refuses quantile_proof_failed and nothing issues, and the proof runs before the predictions are computed, so no corpus
+reaches issuance on an unproven df.
+
+Those two bounds — residual at most 1e-30, agreement at least 30 significant digits — are the ISSUER'S DECLARED bounds,
+not a ratified constant, and they are stated here so the authority-side record carries them rather than only the code and
+its output. Each is chosen conservative against the 20 decimal places at which the artifact publishes a quantile. For a
+quantile of order 2 to 3, agreement to 30 significant digits is agreement to about 29 decimal places, nine more places
+than are printed. The forward residual is a residual in PROBABILITY, not in t: near these quantiles the one-tail density
+is of order 0.05 (p = 0.975) down to 0.01 (p = 0.995) per unit t, so a probability residual of 1e-30 corresponds to an
+error of order 1e-29 to 1e-28 in t, at least eight orders of magnitude below the last published place. A quantile that
+passes both checks therefore cannot be wrong in any digit the artifact prints. The realized residuals and digit counts
+are recorded when the corpus closes; they are not predicted here.
 The full D-125 envelope governs both operatives: bracket screen
 S = max(new range quantized to 1e-6 s ROUND_HALF_EVEN, 0.010818) AND budget ceiling C = max(predecessor ceiling,
diff --git a/docs/contracts/powermetrics_fiducial.md b/docs/contracts/powermetrics_fiducial.md
index c59ac3e0..9e7defa0 100644
--- a/docs/contracts/powermetrics_fiducial.md
+++ b/docs/contracts/powermetrics_fiducial.md
@@ -166,7 +166,6 @@ passes no screen either, and the recovery path's
 only on its last declared slot or an explicit abort.
 
-The screen-to-kind check runs in both directions, and either disagreement
-refuses `systematic_screen_kind_mismatch`. Finalization compares one fact —
-whether a level screen was supplied — against the session's kind. A
+The screen-to-kind check runs in both directions at finalization, comparing
+one fact — whether a level screen was supplied — against the session's kind. A
 derivation-kind slot finalized WITH a screen refuses, because the retired
 epoch's threshold must not judge a new-epoch capture. A bracket-kind slot
@@ -174,5 +173,26 @@ finalized with NO screen refuses as well, because an ordinary capture that
 skipped the comparison would be recorded `valid` without ever having been
 tested against the screen it is owed; omitting the screen is not a route
-around it. The refusal names the session kind it saw.
+around it.
+
+Either disagreement raises the ledger's existing refusal code
+`calibration_reservation_input_invalid`
+(`RefusalCode.RESERVATION_INPUT_INVALID`, "bracket session reservation is
+malformed"), carrying the context fields `reason:
+systematic_screen_kind_mismatch` and the `session_kind` it saw.
+`systematic_screen_kind_mismatch` is that context REASON — the string saying
+which malformed reservation this is — and not a refusal code of its own: a
+reader grepping the code registry for it will not find it, and a caller
+matching on codes matches `calibration_reservation_input_invalid` and then
+reads the reason.
+
+The writer-side half of the same rule IS a code:
+`calibration_derivation_session_requires_derivation_only`
+(`RefusalCode.DERIVATION_SESSION_REQUIRES_DERIVATION_ONLY`, "a
+derivation-kind session slot is capturable only in derivation-only mode")
+refuses an ordinary capture aimed at a derivation-kind slot before the writer
+takes its lease, so nothing is appended, no custody directory exists, and the
+session is untouched. The two halves close the fence from both sides: the
+writer refuses the wrong MODE against the slot, the ledger refuses the wrong
+SCREEN presence against the kind at finalization.
 
 The recovery tool authenticates the acceptance artifact before it reads the
```

## 5. Notes for the magistrate

- `docs/decision_log.md` was in scope and is UNTOUCHED. The SF-5 cure was ruled
  to land in the pre-registration OR the D-138 transaction record; it landed in
  the pre-registration. The addendum's V3 blindness bullet and Exclusions bullet
  are RULED text adopted by cold gate 46, and appending enforcement wording to
  them is an amendment a seat may not make (rule 11). If the magistrate wants
  the enforcement recorded on the authority side too, it is one sentence in the
  V3 bullet naming `prepare-candidate`'s terminal-session refusal and `check`'s
  reporting limits.
- The decision-log addendum still says "the anchor-v3 replay refusal
  `affine_clock_fit_empty`" (`:6676`) and "raw replay" (`:6615`). Both are now
  consistent with the corrected glossary definition of replay (reading and
  authenticating a stored outcome), so no edit is required; flagging so the next
  refuter does not read it as a residual divergence.
- Unaddressed by this round because they are code, not docs: SF-1's actual guard,
  SF-6/`check`'s dry run, SF-7's module docstring, SF-8's licence sentence. The
  pre-registration now DESCRIBES the SF-1 and SF-6 behaviours, so if S4 round 2
  lands anything narrower than "refuses while any named session is not terminal"
  or reports more than kinds/states/slot counts/exclusion counts, the
  pre-registration is the text that is then wrong.
