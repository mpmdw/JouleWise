# 92 — Seat S6 round 4 (Opus): SF-3 and SF-5 from contract refuter 89

Worktree `/Users/edr/code/JouleWise-wt-s6-docs-prereg`, branch
`feat/2026-09-10-epoch-s6-docs-prereg`, base HEAD `074197d1`. No git state changed
(uncommitted working tree; the lead commits). Files touched:
`docs/contracts/powermetrics_fiducial.md`, `docs/decision_log.md` — both inside the
cold-gate-46 addendum text. Every "NOT YET LANDED" status line is intact.

## Test tail

```
$ cd /Users/edr/code/JouleWise-wt-s6-docs-prereg
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness; rc=$?
...............................
----------------------------------------------------------------------
Ran 31 tests in 0.829s

OK
rc=0
```

## Diff

```diff
diff --git a/docs/contracts/powermetrics_fiducial.md b/docs/contracts/powermetrics_fiducial.md
index 9b2bbfc3..c59ac3e0 100644
--- a/docs/contracts/powermetrics_fiducial.md
+++ b/docs/contracts/powermetrics_fiducial.md
@@ -94,7 +94,13 @@ none may be restated as an empirically proved universal instrument property.
 
 Status: **Ruled by cold gate 46 and its dated addendum 11 (2026-09-10); NOT
 YET LANDED.** Seat S1 installs `--derivation-only` against seat S2's
-derivation-kind session interface; no shipped writer accepts the flag, and no
+**derivation-kind** session interface — a ledger session whose open receipt
+carries `session_kind: "derivation"`, marking it as existing to BUILD a
+future acceptance rather than to bracket a claim window with a capture before
+it and a capture after it (an ordinary bracket session records no
+`session_kind` at all; that absence IS the bracket kind, per
+[the ledger contract](calibration_ledger.md#derivation-sessions-for-a-new-identity-epoch)).
+No shipped writer accepts the flag, and no
 shipped ledger offers the slot it requires.
 
 The writer's `--derivation-only` mode exists for one situation. The machine's
@@ -117,26 +123,45 @@ and the derivation kind are defined in
 [the ledger contract](calibration_ledger.md#derivation-sessions-for-a-new-identity-epoch).
 
 Provenance is recorded in hashed bytes, not in prose. Both
-`instrument_evidence.json` and `manifest.json` carry `derivation_only: true`
-and a `screen_basis` object naming the prior acceptance's ID, its file
-SHA-256, its `preflight_level_screen_s` — the **level screen**, that
-acceptance's corpus maximum, the threshold one observation's bound is judged
-against — and its epoch, so every derivation row states for itself which
-artifact it was captured under.
+`instrument_evidence.json` and `manifest.json` carry the same three fields,
+and both are written before either is hashed: `manifest.json` records the
+SHA-256 of `instrument_evidence.json`, and the ledger row's content ID is the
+hash of that byte pair. Editing any of the three fields after the fact
+therefore breaks a recorded digest:
+
+- `derivation_only`, the boolean `true`, marking the capture as taken in this
+  mode;
+- `screen_basis`, an object with exactly four keys — `acceptance_id`, the
+  prior acceptance's ID; `artifact_sha256`, that artifact file's SHA-256;
+  `preflight_level_screen_s`, its **level screen**, meaning that acceptance's
+  corpus maximum, the threshold one observation's bound is judged against;
+  and `epoch`, the six-field identity vector that artifact binds — so every
+  derivation row states for itself which artifact it was captured under;
+- `exceeds_prior_level_screen`, a boolean: `true` when this capture's own
+  `b_fiducial_s` is strictly greater than the `preflight_level_screen_s`
+  recorded in `screen_basis`, `false` otherwise.
 
 The prior artifact's level screen is not applied to the capture. The writer
 sets `preflight_systematic_screen_s = None` and skips the comparison, so the
-ledger disposition can only be `valid` or `ordinary-invalid`. The
-`systematic-invalid` disposition means "exceeds the level screen of this
-epoch's acceptance", and no acceptance of this epoch exists yet, so it cannot
-arise here; excluding a valid new-epoch capture for exceeding a retired
-epoch's threshold would fit the new screen to the old one. Whether the bound
-did exceed the prior artifact's level screen is recorded in the hashed
-evidence as a diagnostic. It feeds the pre-registered screen-challenge rule,
-which halts issuance for a written ruling instead of editing corpus
-membership. Every finalization path carries this classification rule,
-including recovery finalization after a crash: for a derivation-kind session
-the recovery path passes no screen either, and the recovery path's
+row's **disposition** — the ledger's one-word verdict on a capture, one of
+`valid`, `ordinary-invalid`, or `systematic-invalid` — can only be `valid` or
+`ordinary-invalid` here. The `systematic-invalid` disposition means "exceeds
+the level screen of this epoch's acceptance", and no acceptance of this epoch
+exists yet, so it cannot arise.
+
+`exceeds_prior_level_screen` is a diagnostic and only a diagnostic. It is
+never a refusal, and it never changes the disposition: the row is classified
+exactly as it would be if the field were absent, which is why `valid` and
+`ordinary-invalid` remain the only two outcomes whatever its value.
+Excluding an otherwise valid new-epoch capture because its bound exceeds the
+RETIRED epoch's threshold would fit the new screen to the old one, which is
+the fit this mode exists to prevent. The field's one consumer is the
+pre-registered screen-challenge rule, which on a `true` value halts issuance
+for a written ruling instead of editing corpus membership.
+
+Every finalization path carries this classification rule, including recovery
+finalization after a crash: for a derivation-kind session the recovery path
+passes no screen either, and the recovery path's
 `slot == "pre"` auto-abort does not apply, since a derivation session closes
 only on its last declared slot or an explicit abort.
 
@@ -202,7 +227,25 @@ refuses as `instrument_calibration_mismatch` when
 `abs(B_pre - B_post)` exceeds the registered
 `calibration_bracket_max_drift_s` (production: 0.010 s). A single valid
 calibration remains usable only for explicitly non-claim-bearing probe or
-exploratory reduction.
+exploratory reduction, and that allowance covers ordinary captures alone.
+
+A row from a derivation-kind session (cold gate 46 and its dated addendum 11,
+2026-09-10; NOT YET LANDED; see [Derivation-only capture for a new identity
+epoch](#derivation-only-capture-for-a-new-identity-epoch)) licenses NOTHING
+at reduce time even when its disposition is `valid`: no measurement window,
+no probe or exploratory reduction, and no bracket endpoint — not before and
+not after a successor acceptance names it. It is a corpus member for a future
+acceptance and nothing else. The enforcement is ledger-side, never the
+artifact's `derivation_only` field, which is provenance for a reader:
+`_is_derivation_kind_observation` in `joulewise/calibration_bracketing.py`
+returns true for any observation whose session kind is `derivation`, and also
+for any observation whose session cannot be resolved, since admitting a row
+on that doubt would be the fail-open reading. Candidate discovery skips every
+row the predicate accepts, and the same predicate removes it from the
+**endpoint universe** — the set of ledger rows a bracket endpoint may be
+drawn from, which a caller's supplied candidate set must equal EXACTLY or
+evaluation refuses `calibration_ledger_off_ledger_artifact`, so no caller can
+narrow the universe to a favourable subset (cold gate 46 addendum A-5).
 
 ## Window license
 
@@ -265,6 +308,14 @@ metadata scalar alone. An invalid or malformed reference is
 `clock_anchor_unresolved` at reduce time - never a silent fallback to
 `B_bundle` alone.
 
+Passing every check in that list is necessary, never sufficient. A
+derivation-only artifact (cold gate 46 and its dated addendum 11, 2026-09-10;
+NOT YET LANDED) satisfies all of them on a bundle from its own epoch — its
+`status` is `valid`, its binding fields are complete, its bytes authenticate
+against `artifact_sha256` — and still licenses nothing, because the bar it
+fails is ledger-side membership, described under the claim-bearing bracket
+above, not artifact shape.
+
 Hash verification is not by itself calibration verification. Reducer
 consumption re-parses the hash-verified raw plist, re-derives its
 stored-method trace
diff --git a/docs/decision_log.md b/docs/decision_log.md
index 142209fa..5f915ded 100644
--- a/docs/decision_log.md
+++ b/docs/decision_log.md
@@ -6547,8 +6547,9 @@ screen is not applied: `preflight_systematic_screen_s` is `None`, the
 comparison is skipped, and every finalization path — including recovery
 finalization after a crash — records only `valid` or `ordinary-invalid`,
 never `systematic-invalid`. Whether the bound exceeded the prior level screen
-is kept as a hashed diagnostic. Physics and evidence refusals remain
-fail-closed under D-161.
+is kept in both hashed files as the boolean `exceeds_prior_level_screen`: a
+diagnostic that is never a refusal and never changes the disposition.
+Physics and evidence refusals remain fail-closed under D-161.
 
 Each derivation night is ONE `derivation`-kind ledger session — a reservation
 covering several attempts under one open receipt — with N declared, ordered
@@ -6664,8 +6665,9 @@ departs from a ratified floor.
   cannot settle D-125 implicitly. The preflight level screen is the new
   corpus maximum quantized to 1e-15 s, matching r6's stored precision.
 - **Screen challenge.** If two or more retained members exceed r6's level
-  screen `0.032898493715362`, the corpus is NOT issued and Ed rules in writing
-  before any further capture. A second diagnostic is recorded but decides
+  screen `0.032898493715362` — the per-capture comparison each derivation row
+  already carries as its hashed boolean `exceeds_prior_level_screen` — the
+  corpus is NOT issued and Ed rules in writing before any further capture. A second diagnostic is recorded but decides
   nothing: whether the new maximum exceeds `0.04262208300415633`, the Decimal
   sum of r6's exact maximum `0.03289849371536248` and exact range
   `0.00972358928879385`. Neither diagnostic edits corpus membership; both
```

## First-use table (mechanically checked with `grep -n <term> | head -2`)

| Term | First use (line) | How it is built at first use |
|---|---|---|
| `--derivation-only` / derivation-only | powermetrics_fiducial.md:96 (status line), built :106-115 | "an observation taken to build a future acceptance, never to license a measurement", with the stale-epoch forcing problem stated first |
| **derivation-kind** | :97 | glossed in place: a ledger session whose open receipt carries `session_kind: "derivation"`, versus a bracket session that records no `session_kind` at all (absence IS the bracket kind), with the ledger-contract link |
| **level screen** | :136 | glossed in place: "that acceptance's corpus maximum, the threshold one observation's bound is judged against" |
| screen (`screen_basis`) | :134 | field name, its four keys enumerated in place |
| **disposition** | :146 | glossed in place: "the ledger's one-word verdict on a capture, one of `valid`, `ordinary-invalid`, or `systematic-invalid`" |
| `exceeds_prior_level_screen` | :140 | defined in place: boolean, true iff this capture's `b_fiducial_s` is strictly greater than `screen_basis.preflight_level_screen_s`; its contract stated at :152 |
| **endpoint universe** | :245 | glossed in place: "the set of ledger rows a bracket endpoint may be drawn from, which a caller's supplied candidate set must equal EXACTLY" |

Ordering note: the bracket section (:228 ff.) and the reduce-time section
(:311 ff.) come AFTER the derivation section, so `derivation-kind`,
`disposition`, and `derivation_only` are already built where those two SF-5
paragraphs use them.

## SF-3 — what was verified against code before it was written

Read-only in `/Users/edr/code/JouleWise-wt-s1-writer-derivation`
(`scripts/validate_powermetrics_fiducial.py`):

- `_derivation_only_screen_basis` (:439-479) returns exactly the four keys
  `acceptance_id`, `artifact_sha256`, `preflight_level_screen_s`, `epoch`
  (`epoch` = the artifact's `identity_epoch` mapping). Prose matches key for key.
- `:2358-2368`: `evidence_payload["derivation_only"] = True`,
  `evidence_payload["screen_basis"] = screen_basis`, and
  `evidence_payload["exceeds_prior_level_screen"] = bool(... Decimal(derivation_bound_lexeme) > Decimal(screen_basis["preflight_level_screen_s"]))`
  — hence "boolean", "this capture's own `b_fiducial_s`", "strictly greater".
- `:2480-2490`: the manifest carries the same three, copying the evidence
  payload's boolean; both files are written by `_write_text_artifact` before
  finalize.
- Hashing claim tightened after checking `joulewise/calibration_ledger.py`:
  `CONTENT_ID_ARTIFACTS = ("instrument_evidence.json", "manifest.json")`
  (:126-129) and `content_id_from_artifact_hashes` (:266-280), so the ledger
  row's content ID is the hash of that byte pair; `manifest.json` itself
  records the evidence file's SHA-256. The doc now states that chain rather
  than the vaguer "written before they are hashed".
- "never a refusal, never changes the disposition" mirrors the code comment at
  :2359-2362 and the `valid`/`ordinary-invalid`-only guard at :2412-2417.

## SF-5 — what was verified against code

`git -C /Users/edr/code/JouleWise-wt-s3-acceptance-validator show HEAD:joulewise/calibration_bracketing.py`:

- `_is_derivation_kind_observation` (:1725-1745) returns true for
  `SESSION_KIND_DERIVATION` **and** `SESSION_KIND_UNRESOLVED` — the doc states
  both, and states the unresolved case's reason (admitting on doubt is the
  fail-open reading), which is the docstring's own reason.
- Candidate discovery skip at :1798-1800; `registered_valid` endpoint-universe
  skip at :2126-2127, with the exact-equality refusal
  `calibration_ledger_off_ledger_artifact` at :2139-2140 (and the code comment
  "prevents a caller from narrowing the registered universe to a favorable
  subset", paraphrased in the doc).

Both SF-5 sites now say a derivation-kind `valid` row licenses NOTHING at
reduce time and name the ledger-side predicate as the barrier, with
`derivation_only` explicitly marked as provenance rather than enforcement.

## Scope and residue

- Not touched: SF-4 (naming `systematic_screen_kind_mismatch` as a context
  reason rather than a registry code, plus the writer-side
  `calibration_derivation_session_requires_derivation_only` half). It was not
  in this round's brief; the contract's existing kind-check paragraph
  (:167-180) still calls the reason a refusal string without marking it as a
  reason on `RESERVATION_INPUT_INVALID`. Flagging for a later round.
- `docs/decision_log.md` edits are two phrases only: the mechanism paragraph
  now names `exceeds_prior_level_screen` with "never a refusal and never
  changes the disposition", and the screen-challenge bullet names the same key
  as the per-capture recorded form of its comparison (SF-3 cure ii).
