# 149 — Recording of Ed's directive issue 316 (writer seat, dictated-fills transcription)

Worktree `/Users/edr/code/JouleWise-wt-eq-ruling`, branch
`feat/2026-09-10-equivalence-ruling-316`, base `bc1d7ef9` (PR #318's head,
runbook revision 5). No git operation was run; the lead commits. No other
worktree, and no path outside the write scope, was touched.

Authority: directive issue 316 (`gh issue view 316 --repo mpmdw/JouleWise`),
author `mpmdw`, read verbatim this session; corroborated against record 147
(the magistrate's adoption note) and, for the constants, against the r6
artifact and the validator's own code path.

## Files written

| File | Change |
|---|---|
| `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` | +226 lines appended as "Revision 2 (2026-09-10, Ed's ruling by directive issue 316)". Revision 1's bytes are untouched, including every status line. |
| `docs/decision_log.md` | +92 lines: ONE dated addendum appended at the END of the D-102 section, immediately before `## D-103`. No cold-gate text amended; no other decision-log text touched. |
| `docs/phase_2/derivation_night_runbook.md` | Revision 6: +405/−92. DRAFT banner unchanged. |

`git diff --stat`: 3 files changed, 631 insertions(+), 92 deletions(-).

## Tests

```
cd /Users/edr/code/JouleWise-wt-eq-ruling && PYTHONDONTWRITEBYTECODE=1 \
  python3 -m unittest tests.test_docs_freshness tests.test_d078_reason_registry
............................................
----------------------------------------------------------------------
Ran 44 tests in 3.633s

OK
rc=0
```

Two further checks, run because the pre-registration's bytes are parsed and
hashed by production code:

- `preregistration_epoch_pins` over the amended file returns
  `('25G83', 'b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5')`
  — still exactly one value each. Revision 2 deliberately never writes the
  lexeme `os_build:` with any value, because that regex collects a SET and a
  second distinct value would raise `pre-registration: os_build is ambiguous`.
- `python3 -m unittest tests.test_issue_calibration_acceptance_generation` —
  `Ran 114 tests`, `OK`, rc 0 (it recomputes `PREREGISTRATION_SHA256` at import,
  so the append moves the pin without breaking the test).

`tests/test_docs_freshness.py` does NOT forbid the string "directive issue
316": `FORBIDDEN_VOLATILE_FACTS["pull-request literal"]` is `\bPRs?\s*#\d+`,
which needs the `PR`/`PRs` prefix and the `#`. It also only scans
`_current_sections()` = README, PROJECT_STATUS and two regions of
`docs/orchestration.md` — none of the three files written here. The runbook
nonetheless carries no `PR #` literal, no test count and no model name in
anything revision 6 added (checked by grep; the pre-existing `claude`/`codex`
hits are census-substring code blocks).

## Diff hunks

### 1. Pre-registration — one hunk

`@@ -284,0 +285,226 @@` — appended after §"Fields filled at commit".
Structure of the new section:

- Heading `# Revision 2 (2026-09-10, Ed's ruling by directive issue 316)` and
  the required status line, verbatim: "Ed's ruling by directive issue 316;
  recorded by the magistrate; not a magistrate amendment (rule 11)".
- Sealing sentence: revision 1 is not edited, every status line it carries
  stands, and the rule below governs until its own FAIL branch returns the
  campaign to revision 1 unchanged.
- §Provenance — the issue's own provenance line block-quoted in full (Gmail
  thread id, "Filed on Ed's behalf by Fable from an interactive session on
  2026-09-10 ~21:20 PDT after Ed read the recommendation and signed off in his
  own words ('cant you pass that to the magistrate yourself? i sign off'). The
  ruling is Ed's; the wording is Fable's.").
- §Decision 1 — V3 answered NO as the default path, Ed's reason quoted
  including "is acting for an adversary that doesn't exist"; the three-night
  derivation is not withdrawn, it becomes the FAIL branch.
- §What replaces it — four terms built before use (epoch-equivalence check,
  reference envelope, retained value, continuation), then the night's shape
  quoted from the issue (one derivation-kind session of 12 slots, merged chain
  exactly as built, nothing about arm/chain/settle/census/dead-man changes).
- §The reference envelope, as constants, with their sources — the table below,
  plus the three facts about quantization direction and the absent floor.
- §The rule — retained m, the `m < 6` INCONCLUSIVE branch, PASS and FAIL, all
  four quoted verbatim from the issue.
- §On PASS — the issue's continuation paragraph quoted in full, then four
  consequences: PASS licenses nothing by itself; the first real G2-a window is
  the next quiet slot AFTER the addendum lands on the ordinary window path; no
  threshold moves; a code refusal goes through the ordinary gate as the
  smallest change with its diff reported, never a hand workaround.
- §On FAIL — quoted in full; V3 AFFIRMED, this night counts as registration
  night one, and Ed's blindness clarification ("every rule fixed before data",
  not "no one may look") stated as governing both branches.
- §Decisions 2, 3 and 4; timing — quoted; closes by restating that this
  revision authorizes no window and licenses no measurement.

### 2. Decision log — one hunk

`@@ -6699,0 +6700,92 @@` — `### Addendum 2026-09-10 (evening) — Ed's ruling
by directive issue 316: V3 answered NO, night one is an epoch-equivalence
check, continuation on evidence authorized`, appended at the end of the D-102
section. Contents: provenance (owner-authored channel, the issue's own line
quoted, explicitly a transcription and not a magistrate amendment, rule 11
intact, cold-gate text untouched); decision 1 with the "adversary that doesn't
exist" sentence quoted; the replacement night; the equivalence rule with the
reference-envelope constants, their sources and the operative-vs-raw ruling
quoted; the continuation authorization ("epoch continuation on evidence") with
the addendum's required citations, the PR-gate rule for a blocking refusal,
and the note that D-102 clause 2 is preserved because the night's values are
judged under the prior artifact and enter no statistic; the FAIL route; the
blindness clarification quoted; and what is unchanged (decisions 2/3/4, the
veto windows, timing, no window licensed).

### 3. Runbook revision 6 — twenty-four hunks

| Hunk (old line) | What changed |
|---|---|
| `@@ -11,3 +11,24` | Changelog: new revision-6 lead paragraph (one-line summary + what it forced + the two RECORDED open items); the revision-5 paragraph demoted to "Revision 5 (same day) closed…" with its text otherwise intact. DRAFT banner above it untouched. |
| `@@ -71 +92`, `@@ -81,9 +102,18`, `@@ -91 +121,3` | §Purpose retitled "What night one is for, in one paragraph" and rewritten around the two routes (LONG = derive, SHORT = equivalence check), which one is the default, what PASS and FAIL each lead to, and a pointer to §2.5; source line now cites revision 1 for the derivation route and revision 2 for the equivalence route. |
| `@@ -105,2 +137,3`, `@@ -108 +141,2` | §Terms `Registration` gloss: three sessions on the FAIL route, where the equivalence night counts as the first; a PASS closes no registration. |
| `@@ -128,3 +162,9` | §Terms `Blind` rebuilt as "every rule fixed before data", with the two route-dependent consequences. |
| `@@ -163,4 +203,6` | §Terms `Blindness fence` rebuilt as the `prepare-candidate` refusal on the FAIL route; states it does not govern §2.5. |
| `@@ -436 +478,2`, `@@ -460,3 +503,3` | §0.4/§0.5 wording that assumed exactly three nights made route-neutral (head pin frozen "for every night of the campaign that follows"; the tracked-chain digest is "the one value every night shares"). |
| `@@ -483,9 +526,13` | §0.5's V3 precondition replaced: V3 is answered, no longer a precondition of this arm, affirmed only on the FAIL route; the pre-registration digest is still pinned, and revision 2 is part of the bytes hashed. |
| `@@ -684 +731` | §1 title → "The equivalence night's arm (also night one of the FAIL route)". No other change to §1's procedure. |
| `@@ -969,2 +1016,6` | The one §1 sentence that pre-registered three nights by default ("three nights means three plans…") → one wrapper per night, with the night count decided by §2.5 after the night closes. |
| `@@ -1397,0 +1449` | §2.1 gains a row: the night's ledger rows and each capture's `manifest.json` / `instrument_evidence.json` are where the retained values are read, after the night closes. |
| `@@ -1424,23 +1476,39` | §2.2's rc-5 expectation scoped to the FAIL route and explicitly separated from the equivalence check; §2.3 replaced by "When a value may be read, and when it may not" — a boundary in TIME with three ordered rules (nothing while running; retained values once this session is terminal, licensed by the ruling; the derivation's code fence resumes on FAIL) and a warning that the per-capture `exceeds_prior_level_screen` boolean is not the check. |
| `@@ -1507,6 +1575,9` | §2.4's `window_exhausted` response: lost slots are not repaired, they are an INPUT to §2.5's `m < 6` branch. |
| `@@ -1522 +1593,126` | NEW §2.5 "The epoch-equivalence check — the rule, its constants, and the one action each outcome takes": the question it asks, the three inputs (retained value, retained m, reference envelope), the constants table with sources, the three quantization/floor facts, the rule quoted verbatim, the three-outcome action table, "a PASS licenses nothing by itself", and two bracketed open items. Immediately followed by §3 retitled "Nights 2 and 3 — the FAIL route only" with a lead paragraph gating it. |
| `@@ -1558 +1754,5` | §4 retitled "After night 3 is terminal — the FAIL route only" with the same gating lead. |
| `@@ -1808 +2008` | §5 failure table: `check` rc 0 row scoped to the FAIL route. |
| `@@ -1835…+2061,14` (five hunks) | §6 items 4, 5, 7, 8 and 11 restated; new item 12 ("No licence from a PASS"). |
| `@@ -1912,0 +2128,2` | §7 gains two fact rows: the ruling itself, and the reference-envelope constants with their validator and artifact coordinates. |
| `@@ -1939,3 +2156,7` … `@@ -1952 +2173` | §8 first-use table: four new rows, three "Built at" cells repointed to the retitled purpose section, and the `blind`, `blindness fence` and `screen` rows rewritten. |

## The constants table, with sources

Every value below was read this session from the artifact and from the
validator in this worktree, not from the issue's prose alone. Issue 316's rule
— "if the validator's operative screen differs from the raw range (the
never-zero floor), the operative value is the one used" — makes the operative
column the comparator.

| Quantity | Operative (used by the rule) | Raw corpus statistic (quoted by issue 316) | Source of the operative value | Source of the raw value |
|---|---|---|---|---|
| Level screen (corpus maximum) | `0.032898493715362` s | `0.03289849371536248` s | `joulewise/calibration_bracketing.py`, `_D102_N17_DERIVATION["operatives"]["preflight_level_screen_s"]`, bound to `d079_calibration_acceptance_v2_n17_r6` via `_D102_GENERATION_DERIVATIONS[ANCHOR_V3_R6_ACCEPTANCE_ID]`; artifact `decimal_derivation.ratified_operatives.preflight_level_screen_s`, and `decimal_derivation.rounding.preflight_level_screen` (`quantum_s` `0.000000000000001`, `numeric_role` `operative_comparator`) | artifact `decimal_derivation.source_statistics.maximum_s` |
| Bracket screen (corpus range) | `0.009724` s | `0.00972358928879385` s | same validator row, `operatives["bracket_screen_s"]`; artifact `decimal_derivation.ratified_operatives.bracket_screen_s`, and `decimal_derivation.rounding.operative_bracket_screen` (`quantum_s` `0.000001`, `numeric_role` `operative_comparator`) | artifact `decimal_derivation.source_statistics.range_s` |
| Budget ceiling (maximum budgetable drift) | `0.010164834757777545` s | same value (not a rounded statistic) | validator row `operatives["maximum_budgetable_drift_s"]`; artifact `decimal_derivation.ratified_operatives.maximum_budgetable_drift_s` | artifact `decimal_derivation.source_statistics.prediction_99_two_draw_s`, identical lexeme |
| Maximum budgetable excess | `0.000440834757777545` s | same value | validator row `operatives["max_budgetable_excess_s"]`; artifact `ratified_operatives.max_budgetable_excess_s` | — |
| Corpus size | `17` | `17` | validator row `corpus_n` | artifact `derivation_corpus.n` |

Bench-verified this session (Decimal arithmetic, run in this worktree):

- `0.009724 − 0.00972358928879385 = 4.1071120615E-7` s — the operative bracket
  screen is LARGER than the raw range (round-half-even up at quantum 1e-6 s),
  i.e. marginally the more permissive comparator.
- `0.032898493715362 − 0.03289849371536248 = −4.8E-16` s — the operative level
  screen is SMALLER than the raw maximum (round-half-even down at quantum
  1e-15 s), i.e. marginally the stricter comparator.
- `0.010164834757777545 − 0.009724 = 0.000440834757777545`, exactly the
  recorded `max_budgetable_excess_s`, which independently confirms that
  `0.009724` — not the raw range — is the operative screen the artifact's own
  identity `screen + excess == maximum` is built on (the same identity
  `_registered_generation_row_is_complete` checks).
- `0.03289849371536248 − 0.02317490442656863 = 0.00972358928879385`, the
  recorded raw range, from the artifact's own minimum and maximum.

**On the "never-zero floor" the issue parenthesises.** It is `0.010818` s
(`D125_SCREEN_FLOOR_S`), and it is NOT in force for this comparison. r6's
registered rule is `range_equals_screen` (`_D102_N17_DERIVATION["screen_rule"]`,
applied in `calibration_bracketing._valid_acceptance_bound`: the quantized
range IS the screen, no floor). The floor belongs to
`floored_range_envelope_screen`, which the pre-registration registers for a
FUTURE successor corpus. So the operative-vs-raw gap here is quantization
alone, and the issue's rule resolves it the same way either way: use the
operative value. Both facts are stated in all three written files.

## The first-use table (what revision 6 added to §8)

| Term | Built at | One-line meaning as written |
|---|---|---|
| epoch-equivalence check | §"What night one is for", applied §2.5 | One night's retained values compared against the thresholds the acceptance in force already carries, under a rule fixed in writing before the night runs; derives nothing, issues nothing. |
| reference envelope | §2.5 | The comparators of the acceptance in force in the OPERATIVE form the validator uses (level screen `0.032898493715362` s, bracket screen `0.009724` s, budget ceiling `0.010164834757777545` s, n = 17); where operative and raw differ, the operative one is the comparator. |
| retained value / retained m | §2.5 | The `b_fiducial_s` of a capture that is both `valid` in the ledger and resolved under anchor-v3 replay; `m` is how many such values the night produced. |
| continuation ("epoch continuation on evidence") | §2.5 | Carrying the acceptance in force onto the new identity epoch by a dated D-102 addendum instead of voiding it; moves no threshold, and it is the addendum — not the PASS — that licenses ordinary capture. |

Three existing rows were also repaired because their meaning moved: `blind /
blindness` (now "every rule fixed before data", with the two route-dependent
consequences), `blindness fence` (now the `prepare-candidate` refusal on the
FAIL route, explicitly not governing §2.5), and `screen / level screen /
bracket screen` (Built-at now names §2.5's constants as well as §4.2's
successor operatives). Three rows whose "Built at" cell named the retitled
purpose section were repointed.

## Two things RECORDED rather than decided (both bracketed in §2.5)

1. **No committed tool extracts the retained values.** Nothing in this
   worktree evaluates the equivalence rule; record 147 says a desk tool is a
   separate seat. §2.5 therefore names the coordinates and says to read them by
   hand, recording both the ledger lexeme and the bundle's, rather than citing
   a command that does not exist.
2. **The issue fixes no night count for INCONCLUSIVE-then-FAIL.** If `m < 6`
   forces a second equivalence night and that night then FAILS, whether both
   nights count as registration nights one and two is not answered by issue
   316. §2.5 says to report it to Ed and get a written answer, and not to
   choose it at the desk. This matters mechanically: the issuer pins
   `PREREGISTERED_NIGHT_COUNT = 3` and would need `--nights-ruling` for any
   other shape.

## Scope discipline

Three consistency repairs were made inside the runbook beyond the literal
enumeration in the brief, all inside the one file in scope and all forced by
the ruling: §0.5's V3 precondition (which as written would have forbidden
arming the equivalence night), §3 and §4's gating leads (both sections are now
FAIL-route-only), and the §5 `check` rc-0 row. Each is listed in the hunk table
above. No other file, worktree or repository was touched.
