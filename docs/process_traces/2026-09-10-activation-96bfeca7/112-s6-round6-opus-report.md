# S6 round 6 — bounded documentation seat (Opus) report

Worktree: /Users/edr/code/JouleWise-wt-s6-docs-prereg
Branch: feat/2026-09-10-epoch-s6-docs-prereg  Base HEAD: 23f797be (no git state changed; edits left uncommitted in the working tree)
Code read read-only from /Users/edr/code/JouleWise-wt-epoch-integration @ 067f4e54 and /Users/edr/code/JouleWise-wt-s4-issuer-prepare @ 9c998a9d

```
 .../preregistration_d079_epoch_25g83_rev1.md       | 72 ++++++++++++++--
 docs/contracts/calibration_ledger.md               | 97 +++++++++++++++++++---
 docs/contracts/powermetrics_fiducial.md            | 24 ++++--
 docs/decision_log.md                               |  7 +-
 4 files changed, 175 insertions(+), 25 deletions(-)
```

## Diff hunks

```diff
diff --git a/configs/calibration/preregistration_d079_epoch_25g83_rev1.md b/configs/calibration/preregistration_d079_epoch_25g83_rev1.md
index 03422963..79926c55 100644
--- a/configs/calibration/preregistration_d079_epoch_25g83_rev1.md
+++ b/configs/calibration/preregistration_d079_epoch_25g83_rev1.md
@@ -91,9 +91,37 @@ is fixed here first.
 Why three nights of twelve slots, stated before capture: at the historical
 valid rate 30/38 and r6's replay-retention ratio 17/19, two nights of 12 slots
 project 24 × (30/38) × (17/19) = 16.95 retained observations, below the
-required 19; three nights project 25.4. The schedule fits a 210 min window
-with margin: one 600 s settle + 11 × 600 s cadence + one ~8 min capture is
-128 min.
+required 19; three nights project 25.4.
+
+Three different durations govern one night, and confusing them is how a night
+opens a session it cannot finish, so all three are stated here.
+
+- **Programmed span — 7680 s (128 min).** What the capture chain actually
+  runs: one 600 s settle after the last operator action, then eleven 600 s
+  start-to-start slot gaps, then one 480 s capture budget for the twelfth
+  slot. 600 + 11 × 600 + 480 = 7680.
+- **Generator minimum — 7980 s (133 min).** The night wrapper generator
+  `scripts/gen_derivation_night.py` refuses to emit a wrapper unless the
+  plan's `window_max_s` is at least the programmed span plus a 300 s
+  pre-settle allowance (7680 + 300 = 7980). The allowance exists because the
+  settle clock starts at the chain's own start, and a window that held only
+  the programmed span exactly would abort its last slot
+  `window_exhausted` on any start-up delay.
+- **Recommended `window_max_s` — 9000 s (150 min).** The value these nights
+  are armed with: it clears the 7980 s minimum by 1020 s, absorbing a slow
+  capture or a late start without touching the schedule. The generator
+  separately refuses when `t0 + window_max_s + 300 s` (a courier allowance
+  for the night's own closing work) is not before the next local 07:00.
+
+`window_max_s` is the plan field naming the window's length in seconds; the
+window ENDS at `t0 + window_max_s`, and the chain will not start a slot it
+cannot finish inside that end.
+
+The figure 210 min, which earlier drafts attached to the window, is not a
+window at all: it is the install span 03:00–06:30 — the operator-facing block
+of the clock inside which a night is scheduled. A 150 min window fits inside
+a 210 min install span with an hour to spare; the two numbers measure
+different things and neither is derived from the other.
 
 ## Registration text
 
@@ -163,7 +191,17 @@ range, 0.04262208300415633 (the Decimal sum of 0.03289849371536248 and 0.0097235
 membership.
 
 Analysis. Decimal statistics exactly as r6: minimum, maximum, range, mean, sample SD; t(0.975, n-1) and t(0.995, n-1)
-two-draw predictions (both terms defined in the glossary above). The three-night schedule admits retained n from 19
+two-draw predictions (both terms defined in the glossary above). The two-draw predictions are the one step that leaves
+exact decimal arithmetic, and Q99 is the number that sets the successor's budget ceiling C, so the arithmetic is declared
+here, before the corpus exists, in the issuer's own sealed words (the string TWO_DRAW_PREDICTION_RULE, quoted verbatim
+because it is hashed into the derivation and a paraphrase would change the digest of an otherwise identical derivation):
+"prediction_p_two_draw_s = t(p, n-1) * sample_sd_presentation_s * sqrt(2), evaluated in binary64 and recorded as its
+shortest round-tripping decimal". Binary64 is the IEEE 754 double-precision binary floating-point format (Python's
+float), which carries about 15 to 17 significant decimal digits. The shortest round-tripping decimal is the shortest
+decimal string that reads back as exactly that same binary64 value and no other, which is what Python's repr of a float
+returns. So the two quantiles and the sample SD are converted to binary64, multiplied there, and the product is recorded
+as that shortest string: no rounding choice is left to be made after the values are seen.
+The three-night schedule admits retained n from 19
 (the required floor) to 36 (all declared slots retained), so the degrees of freedom n-1 run from 18 to 35 — or from 16
 if Ed's written n = 17 ruling is exercised; the quantile implementation's proof for the REALIZED df is computed and
 recorded before issuance, and no corpus issues on a df whose quantile is not proven in that record.
@@ -193,7 +231,14 @@ passes both checks therefore cannot be wrong in any digit the artifact prints. T
 are recorded when the corpus closes; they are not predicted here.
 The full D-125 envelope governs both operatives: bracket screen
 S = max(new range quantized to 1e-6 s ROUND_HALF_EVEN, 0.010818) AND budget ceiling C = max(predecessor ceiling,
-new Q99). The generation records the predecessor ceiling and an explicit d125_ruling
+new Q99). The successor's generation row registers that S rule under the NAME
+floored_range_envelope_screen, and the validator recomputes screen == max(quantized range, 0.010818) under it. The name
+records the RULE fixed here before capture, not the branch the data took: the row carries this name whichever arm of the
+max wins. Naming it by the realized branch would make the registered rule a function of the data, which is what a
+pre-registration exists to prevent, and it would misfile the ordinary case, since a corpus at the n = 19 size floor has a
+range just below 0.010818 and takes the floor arm. (The six issued generations register the other name,
+range_equals_screen: screen == quantized range, with no floor. An unregistered name refuses rather than defaulting to
+either rule.) The generation records the predecessor ceiling and an explicit d125_ruling
 reference; issuance refuses while that reference is absent, and refuses successor_screen_exceeds_budget_ceiling when
 S >= C. Maximum budgetable drift = C; maximum budgetable excess = C - S, with no silent clamp at zero.
 
@@ -214,6 +259,23 @@ artifact, never incorporated into a threshold that judges itself. Nothing in thi
 window or weakens a physics or evidence refusal.
 ```
 
+## Known conditions (recorded, not rules)
+
+**Display state at t0 is not constrained by the night gate.** The gate
+(`joulewise/night_gate.py`, condition C3) requires the screensaver's
+`idleTime` preference to read exactly `0` — meaning the screensaver never
+engages, refusal reason `night_refused_hid_idle` — and for the display it only
+requires that `pmset -g` yield a parseable `displaysleep` setting, recording
+that value as evidence without demanding any particular one; it never probes
+whether a panel is awake, dimmed, or asleep when the window opens, and the
+derivation chain deliberately omits the writer flag
+`--sleep-display-before-capture` that the G2-a chain passes, because no
+operator is present to schedule a display action. These captures may therefore
+differ systematically in display state from the G2-a corpus the resulting
+acceptance will judge. That is recorded here as a known condition of this
+corpus, not a rule: it edits no membership, moves no threshold, and licenses
+no re-capture.
+
 ## Fields filled at commit
 
 `[DD]` (authoring day), `[MLX_VERSION]`, `[SEQ]` and `[DIGEST]` (the committed
diff --git a/docs/contracts/calibration_ledger.md b/docs/contracts/calibration_ledger.md
index 1ddcecd7..621fde75 100644
--- a/docs/contracts/calibration_ledger.md
+++ b/docs/contracts/calibration_ledger.md
@@ -16,13 +16,21 @@ every consumer.
 
 ## Derivation sessions for a new identity epoch
 
-Status: **Ruled by cold gate 46 and its dated addendum 11 (2026-09-10); NOT
-YET LANDED.** Seats S1-S4 install the writer mode, the derivation-kind ledger
-session, the generation-keyed validator, and the issuer. Until those seats
-land, no code implements this section or the generation-keyed clauses under
-[Historical import](#historical-import): the shipped ledger has `bracket`-kind
-sessions only, and the shipped validator enforces the import-only prefix fence
-for every generation.
+Status: **Ruled by cold gate 46 and its dated addendum 11 (2026-09-10); Ed
+veto window open; LANDED in code.** Both facts hold at once: the mechanism
+below is implemented and running, and Ed may still veto or amend the rules it
+implements. This section and the generation-keyed clauses under [Historical
+import](#historical-import) name shipped behaviour, not a plan. The code
+sites, by symbol: `SESSION_KIND_DERIVATION` in
+`joulewise/calibration_ledger.py` is the session kind a derivation session's
+open receipt carries; `_is_derivation_kind_observation` in
+`joulewise/calibration_bracketing.py` is the predicate that keeps those rows
+out of every claim-bearing use; `prior_prefix_mode` is the key on the
+registered generation row that selects which prefix fence that generation is
+validated under; `scripts/validate_powermetrics_fiducial.py` takes
+`--derivation-only` for the writer mode; and
+`scripts/issue_calibration_acceptance_generation.py` is the issuer that
+derives a successor acceptance candidate from a derivation corpus.
 
 **Terms.** An **identity epoch** is the six-field vector {`os_build`,
 `hardware_model`, `power_policy`, `sampling_interval_ms`,
@@ -126,6 +134,36 @@ trigger observation is judged under the PRIOR artifact, never under a
 threshold that incorporates that observation. Nothing in this section licenses
 a measurement window or weakens a physics or evidence refusal (D-161).
 
+**The issuer refuses a candidate whose registration does not match the machine
+or the file.** Three fences are installed in the issuer,
+`scripts/issue_calibration_acceptance_generation.py`, on its
+`prepare-candidate` subcommand, so a mismatch stops the run before any corpus
+statistic is computed rather than being caught in review afterwards.
+
+- **Epoch match.** `prepare-candidate` refuses when the pre-registration's
+  recorded `/usr/bin/powermetrics` SHA-256, or its recorded `os_build`,
+  differs from the target identity epoch the registration declares. A machine
+  that has moved off the declared epoch since the text was written would
+  otherwise contribute rows to a corpus the registration never governed.
+- **Registration shape.** It refuses when the registration is not exactly
+  three sessions of twelve declared slots — the shape the pre-registration
+  fixes before capture — unless a written ruling names the departure. A
+  campaign that quietly ran a fourth night, or nights of a different slot
+  count, is a different experiment from the pre-registered one, and the
+  corpus size alone cannot reveal the substitution.
+- **File identity.** It refuses when the SHA-256 of the pre-registration file
+  it was handed differs from the digest the caller passes as
+  `--preregistration-sha256`, so the authority the candidate cites is the
+  text the caller meant, byte for byte, rather than whatever now sits at that
+  path.
+
+`[flag names to confirm at merge]` — these three fences land on the issuer
+seat's branch as this contract is written, and are described here by
+subcommand and flag name rather than by location. The subcommand name
+`prepare-candidate` and the flag `--preregistration-sha256` used above are to
+be checked against the merged issuer, and corrected here if the merged names
+differ.
+
 ## Historical import
 
 Historical import is the one genesis-only exception that registers already
@@ -175,8 +213,11 @@ instrument-evidence byte hashes, so it names the same observation from any
 custody path.
 
 Which rows that prefix may contain is a per-generation registration, not a
-global rule (ruled 2026-09-10, not yet landed; see [Derivation sessions for a
-new identity epoch](#derivation-sessions-for-a-new-identity-epoch)). A
+global rule (ruled 2026-09-10, Ed veto window open; landed as the
+`prior_prefix_mode` key that `_prior_set_matches_import_cutoff_prefix` in
+`joulewise/calibration_bracketing.py` reads off the registered generation row;
+see [Derivation sessions for a new identity
+epoch](#derivation-sessions-for-a-new-identity-epoch)). A
 generation registered `prior_prefix_mode: import_only` keeps the genesis fence
 exactly as written above — any live row in its prefix refuses — and that is
 how generations r3 through r6 keep validating byte-identically. Only a
@@ -198,7 +239,16 @@ each row to the ledger's recorded session is what keeps D-102 clause 2's rule
 — nothing judges itself — true of registration membership as well as of
 thresholds. Generations registered `import_only` keep the exact four-key row
 shape and refuse when a `session_id` key appears, so no historical generation
-changes. (Ruled 2026-09-10, not yet landed; seats S3 and S4 install it.)
+changes. (Ruled 2026-09-10, Ed veto window open; landed. On the validator
+side, `_prior_set_matches_import_cutoff_prefix` in
+`joulewise/calibration_bracketing.py` appends the row's `session_id` to the
+four expected bindings only when the mode is `import_plus_live`, compares it
+against the ledger observation's `bracket_session_id`, and separately requires
+every id in the row's `registration_session_ids` to resolve to a session whose
+kind is `SESSION_KIND_DERIVATION`. On the issuer side,
+`scripts/issue_calibration_acceptance_generation.py` writes
+`prior_prefix_mode: import_plus_live` and `registration_session_ids` onto the
+generation row it emits.)
 
 Two EXPECTED numbers are registered per generation for the same reason:
 `prior_observation_count` and `cutoff_sequence` (the genesis generation
@@ -211,6 +261,33 @@ receipts breaks that arithmetic, so neither number may be recomputed from a
 literal. The generation likewise registers the epoch identifiers it permits
 (`epoch_catalog_ids`) rather than relying on the single literal `d079_epoch`.
 
+The generation also registers, under `screen_rule`, the NAME of the rule its
+bracket screen was derived under. Two names are registered.
+`range_equals_screen` is the rule the six issued generations were derived
+under: the bracket screen IS the corpus range quantized to 0.000001 s under
+ROUND_HALF_EVEN (ties go to the even final digit).
+`floored_range_envelope_screen` is the D-125 envelope rule: that same
+quantized range raised to a floor, so the check is
+`screen == max(quantized range, floor)`, where the floor is
+`D125_SCREEN_FLOOR_S` = 0.010818 s, the screen of the n = 19 genesis corpus.
+The floor exists so no later lineage can characterise the instrument against
+a looser screen than the first one it was characterised against.
+`_registered_generation_row_is_complete` and the operative recomputation in
+`joulewise/calibration_bracketing.py` both dispatch on the registered name,
+and an unregistered name refuses rather than defaulting to either rule.
+
+The name describes the PRE-REGISTERED RULE, never the branch the data took: a
+generation derived under the envelope registers
+`floored_range_envelope_screen` whether the range exceeded the floor or the
+floor bound the screen. Naming it by the realized branch would make the
+registered rule a function of the data, which is exactly what registering a
+rule before capture exists to prevent — and it would misfile the ordinary
+case, because a corpus at the n = 19 size floor has a range just BELOW
+0.010818 s and takes the floor arm. A generation registered
+`floored_range_envelope_screen` must additionally carry the `d125_ruling`
+reference that authorised the envelope; the six issued rows predate the
+envelope, carry no such reference, and are unaffected.
+
 For `import_plus_live` two further checks apply, and together they are the
 corpus-membership fence. Purity: every corpus member's ledger row carries the
 target epoch. Completeness: every prior-set row that is valid, carries the
diff --git a/docs/contracts/powermetrics_fiducial.md b/docs/contracts/powermetrics_fiducial.md
index 9e7defa0..db543802 100644
--- a/docs/contracts/powermetrics_fiducial.md
+++ b/docs/contracts/powermetrics_fiducial.md
@@ -92,16 +92,23 @@ none may be restated as an empirically proved universal instrument property.
 
 ## Derivation-only capture for a new identity epoch
 
-Status: **Ruled by cold gate 46 and its dated addendum 11 (2026-09-10); NOT
-YET LANDED.** Seat S1 installs `--derivation-only` against seat S2's
+Status: **Ruled by cold gate 46 and its dated addendum 11 (2026-09-10); Ed
+veto window open; LANDED in code.** Both hold at once: the mode is
+implemented and running, and Ed may still veto or amend the rules it
+implements. `--derivation-only` is a registered argument of the writer
+`scripts/validate_powermetrics_fiducial.py`, and it runs against the
 **derivation-kind** session interface — a ledger session whose open receipt
-carries `session_kind: "derivation"`, marking it as existing to BUILD a
+carries `session_kind: "derivation"` (the constant `SESSION_KIND_DERIVATION`
+in `joulewise/calibration_ledger.py`), marking it as existing to BUILD a
 future acceptance rather than to bracket a claim window with a capture before
 it and a capture after it (an ordinary bracket session records no
 `session_kind` at all; that absence IS the bracket kind, per
 [the ledger contract](calibration_ledger.md#derivation-sessions-for-a-new-identity-epoch)).
-No shipped writer accepts the flag, and no
-shipped ledger offers the slot it requires.
+The pairing is enforced in both directions by the writer's refusal codes in
+`joulewise/calibration_exits.py`: a derivation-kind slot captured without the
+flag refuses `calibration_derivation_session_requires_derivation_only`, and
+the flag used without such a slot refuses
+`calibration_derivation_only_session_kind_required`.
 
 The writer's `--derivation-only` mode exists for one situation. The machine's
 **identity epoch** — the six-field vector the issued acceptance binds: OS
@@ -250,7 +257,8 @@ calibration remains usable only for explicitly non-claim-bearing probe or
 exploratory reduction, and that allowance covers ordinary captures alone.
 
 A row from a derivation-kind session (cold gate 46 and its dated addendum 11,
-2026-09-10; NOT YET LANDED; see [Derivation-only capture for a new identity
+2026-09-10; Ed veto window open; landed — the enforcing predicate is named
+further down this paragraph; see [Derivation-only capture for a new identity
 epoch](#derivation-only-capture-for-a-new-identity-epoch)) licenses NOTHING
 at reduce time even when its disposition is `valid`: no measurement window,
 no probe or exploratory reduction, and no bracket endpoint — not before and
@@ -330,7 +338,9 @@ metadata scalar alone. An invalid or malformed reference is
 
 Passing every check in that list is necessary, never sufficient. A
 derivation-only artifact (cold gate 46 and its dated addendum 11, 2026-09-10;
-NOT YET LANDED) satisfies all of them on a bundle from its own epoch — its
+Ed veto window open; landed — written by
+`scripts/validate_powermetrics_fiducial.py` under `--derivation-only`)
+satisfies all of them on a bundle from its own epoch — its
 `status` is `valid`, its binding fields are complete, its bytes authenticate
 against `artifact_sha256` — and still licenses nothing, because the bar it
 fails is ledger-side membership, described under the claim-bearing bracket
diff --git a/docs/decision_log.md b/docs/decision_log.md
index 5f915ded..1ab78e4c 100644
--- a/docs/decision_log.md
+++ b/docs/decision_log.md
@@ -6652,15 +6652,16 @@ departs from a ratified floor.
   compressed or replaced.
 - **V7 — the successor's screen and ceiling.** The FULL D-125 envelope governs
   both: `S = max(new range quantized to 1e-6 s ROUND_HALF_EVEN, 0.010818)` AND
-  `C = max(inherited ceiling, new Q99)`, where the inherited ceiling is the
-  predecessor generation's `maximum_budgetable_drift_s` and Q99 is the new
+  `C = max(predecessor ceiling, new Q99)`, where the predecessor ceiling is
+  the predecessor generation's `maximum_budgetable_drift_s`, carried on the
+  successor's generation row as `predecessor_ceiling_s`, and Q99 is the new
   corpus's 99 % two-draw prediction. The C half is not optional: r6's own
   ceiling `0.010164834757777545` is BELOW the `0.010818` screen floor, so a
   successor derived under an S-only rule would trip D-126 clause 3's ratified
   `successor_screen_exceeds_budget_ceiling` refusal (screen ≥ ceiling) and the
   stored identity `screen + excess = maximum` would demand a negative excess.
   Cap is `C − S` with no silent clamp, per D-126 clause 3. The generation row
-  carries the inherited ceiling and an explicit `d125_ruling` reference, and
+  carries the predecessor ceiling and an explicit `d125_ruling` reference, and
   the issuer refuses to emit while that reference is absent, so the successor
   cannot settle D-125 implicitly. The preflight level screen is the new
   corpus maximum quantized to 1e-15 s, matching r6's stored precision.
```

## Item-by-item

1. **Six not-landed statements rewritten as landed.** `docs/contracts/calibration_ledger.md`
   status block (§Derivation sessions), the `prior_prefix_mode` per-generation
   sentence, and the fifth-binding parenthetical; `docs/contracts/powermetrics_fiducial.md`
   status block (§Derivation-only capture), the derivation-row reduce-time
   paragraph, and the derivation-only-artifact paragraph. Both deleted
   sentences are gone (residual grep for "not yet landed", "No shipped writer",
   "Until those seats" returns nothing in scope). Every "ruled by cold gate 46
   ... Ed veto window open" authority label is kept and each rewrite says
   explicitly that a landed mechanism and an open veto are both true. No PR
   numbers and no line numbers were introduced; code sites are named by symbol
   or by flag.
2. **Decision log S6 addendum V7** — "inherited ceiling" -> "predecessor
   ceiling" at both sites, with the generation-row key `predecessor_ceiling_s`
   named once (ruling 69 A1). No other decision-log text touched.
3. **Pre-registration Analysis clause** now declares the two-draw arithmetic
   before the corpus exists, quoting the issuer's sealed rule string verbatim
   and glossing binary64 and "shortest round-tripping decimal" at first use,
   and says why the declaration matters (Q99 sets the ceiling C).
4. **`floored_range_envelope_screen` documented in both required homes** — the
   pre-registration's issuance clause (the D-125 envelope paragraph) and the
   ledger contract's generation-row section, with the check
   `screen == max(quantized range, floor)`, the floor value, and the
   rule-not-branch argument including the n = 19 counterexample.
5. **Window arithmetic reconciled** in the pre-registration: programmed span
   7680 s / 128 min, generator minimum 7980 s, recommended `window_max_s`
   9000 s / 150 min, and 210 min relabelled as the 03:00-06:30 install span.
6. **Display-state condition** recorded in a new "Known conditions (recorded,
   not rules)" section, deliberately OUTSIDE the sealed registration text
   block so it cannot read as a rule change.
7. **Arm-gate fences** described in the ledger contract by subcommand
   (`prepare-candidate`) and flag (`--preregistration-sha256`), with the
   `[flag names to confirm at merge]` marker, because they are not yet visible
   at the S4 worktree HEAD (see Verification below).

## Verification of every code fact asserted (read at the integration HEAD)

| Doc claim | Verified at |
| --- | --- |
| `SESSION_KIND_DERIVATION = "derivation"` | `joulewise/calibration_ledger.py` |
| `_is_derivation_kind_observation` fences candidate discovery + endpoint universe | `joulewise/calibration_bracketing.py` (three call sites) |
| `--derivation-only` is a registered writer argument | `scripts/validate_powermetrics_fiducial.py` |
| Both-directions refusal pair | `joulewise/calibration_exits.py` (`DERIVATION_SESSION_REQUIRES_DERIVATION_ONLY`, `DERIVATION_ONLY_SESSION_KIND_REQUIRED`); enforced in the writer's session-shape check |
| `prior_prefix_mode` read off the generation row; fifth `session_id` binding vs `bracket_session_id`; `registration_session_ids` must be derivation-kind | `_prior_set_matches_import_cutoff_prefix` in `joulewise/calibration_bracketing.py` |
| Issuer writes `prior_prefix_mode: import_plus_live`, `registration_session_ids`, `predecessor_ceiling_s`, `screen_rule` | `scripts/issue_calibration_acceptance_generation.py` |
| `SCREEN_RULE_FLOORED_RANGE_ENVELOPE = "floored_range_envelope_screen"`; `D125_SCREEN_FLOOR_S = Decimal("0.010818")`; dispatch `max(quantized_range, D125_SCREEN_FLOOR_S) == screen`; `_D125_RULING_REQUIRED_SCREEN_RULES` | `joulewise/calibration_bracketing.py` |
| `TWO_DRAW_PREDICTION_RULE` string quoted verbatim; `repr(float(quantile) * float(sample_sd_lexeme) * math.sqrt(2))` | `scripts/issue_calibration_acceptance_generation.py` (`two_draw_prediction_lexeme`) |
| 600 + 11x600 + 480 = 7680; `PRE_SETTLE_ALLOWANCE_S = 300` -> 7980 minimum; dead-man `t0 + window_max_s + 300 < next local 07:00` | `scripts/gen_derivation_night.py` (`programmed_span_s`, the two refusals) |
| Night gate requires screensaver `idleTime` == "0" (`night_refused_hid_idle`) and only requires `pmset -g` to yield a parseable `displaysleep`, recording its value without constraining it | `joulewise/night_gate.py` C3 |
| Derivation chain omits `--sleep-display-before-capture` that the G2-a chain passes | `scripts/night_chains/calibration_derivation_only.zsh` header; flag exists in `scripts/validate_powermetrics_fiducial.py` |

**Item 7 could not be verified against code.** At
`git -C /Users/edr/code/JouleWise-wt-s4-issuer-prepare show HEAD:scripts/issue_calibration_acceptance_generation.py`
(HEAD 9c998a9d, "S4 fix round 5") the `prepare-candidate` parser has no
`--preregistration-sha256`, and there is no epoch-mismatch refusal against the
registration's target epoch and no three-sessions-of-twelve shape check; the
only pre-registration handling is hashing the file into
`derivation_notes.preregistration.file_sha256`. The three fences are therefore
written from the brief's names and carry the `[flag names to confirm at merge]`
marker, as instructed.

## First-use table (terms of art introduced or newly load-bearing in this round)

| Term | Where first used | How it is discharged |
| --- | --- | --- |
| binary64 | pre-registration, Analysis clause | Glossed at first use: "the IEEE 754 double-precision binary floating-point format (Python's float), which carries about 15 to 17 significant decimal digits". |
| shortest round-tripping decimal | pre-registration, Analysis clause | Glossed at first use: "the shortest decimal string that reads back as exactly that same binary64 value and no other, which is what Python's repr of a float returns". |
| `TWO_DRAW_PREDICTION_RULE` | pre-registration, Analysis clause | Named as "the string ... quoted verbatim because it is hashed into the derivation", then quoted in full; the reason a paraphrase is forbidden is given in the same sentence. |
| `screen_rule` / `floored_range_envelope_screen` / `range_equals_screen` | ledger contract, generation-row section; pre-registration, D-125 clause | Both names defined by their arithmetic before any use (`screen == quantized range`; `screen == max(quantized range, floor)`), the floor value and its provenance given, and the rule-vs-branch distinction argued with the n = 19 worked counterexample. |
| `D125_SCREEN_FLOOR_S` / "floor" | ledger contract, generation-row section | Value 0.010818 s and its meaning ("the screen of the n = 19 genesis corpus") stated at first use, with the forcing reason (no lineage may loosen the screen below the first characterisation). |
| ROUND_HALF_EVEN | ledger contract, generation-row section | Glossed in place: "(ties go to the even final digit)". |
| Programmed span / generator minimum / recommended `window_max_s` / install span | pre-registration, three-durations list | Each is a bolded defined term with its arithmetic; `window_max_s` itself glossed ("the plan field naming the window's length in seconds; the window ENDS at `t0 + window_max_s`"); 210 min explicitly reclassified. |
| `window_exhausted` | pre-registration, generator-minimum bullet | Already a defined term in the registration text (slot abort reason); used here consistently with that definition. |
| "landed" / "Ed veto window open" | both contracts, status blocks | Each status block states in plain words that the two coexist: the mechanism is implemented and running, and Ed may still veto or amend the rules it implements. |
| `prepare-candidate` / `--preregistration-sha256` | ledger contract, issuer-fence block | Introduced as "the issuer ... on its `prepare-candidate` subcommand"; each fence states what it refuses and the forcing problem it closes; unverified names marked. |

## Test tail

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness`, rc captured in a shell variable.

```
...............................
----------------------------------------------------------------------
Ran 31 tests in 1.879s

OK
RC_docs_freshness=0
```

Also run because it is the only other test that reads these contract files:
`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d078_reason_registry` -> `Ran 13 tests`, `OK`, `RC_reason_registry=0`.

## Residue for the lead (not edited; outside this brief)

1. `docs/decision_log.md` V4 of the same S6 addendum still says the schedule
   "fits with margin: 600 s settle + 11 x 600 s cadence + one ~8 min capture is
   128 of a 210 min window" — the same 210 min defect item 5 fixes in the
   pre-registration. It sits inside the cold-gate-adopted V-clause text, which
   this brief fences off ("never cold-gate-ruled text"), so it was left alone.
   It needs either a dated correction addendum or an explicit ruling.
2. Item 7's three fences are unverifiable today (see above). The
   `[flag names to confirm at merge]` marker must be resolved, and the fence
   descriptions checked, when the S4 branch merges.
