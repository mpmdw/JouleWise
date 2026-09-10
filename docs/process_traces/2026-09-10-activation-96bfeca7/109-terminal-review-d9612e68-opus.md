# 109 — TERMINAL REVIEW (fresh eyes, cross-seat seams): ACCEPTANCE-EPOCH-25G83-01 @ d9612e68

Reviewer: Opus 5, fresh session, no seat context. Read-only in
`/Users/edr/code/JouleWise-wt-epoch-integration` (branch
`feat/2026-09-10-epoch-integration`, HEAD `d9612e68`, 51 commits over
`origin/main`, 28 files, +11608/−167). No edits, no git state changes, no
mutation cuts, no full-suite run (a sharded replay runs elsewhere).

**The branch moved under this review.** At start, the worktree HEAD was
`d9612e68` as briefed. By the end it was `d52c4659` — two further commits
landed (`819a9c40` "validator comment states that both screen rules are
implemented"; `9c998a9d` "S4 fix round 5: a prior-set row whose identity epoch
is neither the target's nor the predecessor's refuses", from a "diff gate 110").
`d9612e68` is still an ancestor. The delta is 4 files, +81/−11, and its only
production hunks are a comment rewrite in `joulewise/calibration_bracketing.py`
(net +2 lines above line 220) and a +19-line refusal in the issuer at `:1212`.
**Every line number in this report is stated against `d9612e68`** and was
re-checked against `git show d9612e68:<file>`; in the current working tree add
+2 below `calibration_bracketing.py:220` and +19 below
`issue_calibration_acceptance_generation.py:1212`. Two consequences for the
caller: (1) this review is not a review of the current head, and the two new
commits — one of which adds a production refusal — have not been terminal-
reviewed; (2) whoever merges should confirm which head they are merging.

Interpreter used for every executed command:
`/Users/edr/code/JouleWise/.venv/bin/python` (3.13.1, pytest 9.1.1) with
`PYTHONDONTWRITEBYTECODE=1`. The worktree's own `python`/`python3` on PATH is
Homebrew 3.14 with no pytest — worth knowing before anyone repeats these.

## VERDICT: MERGEABLE AFTER FIXES

Two distinct gates, and it matters which is which:

**Before merge (small, documentation only).** Four sentences in the shipped
contracts say a mechanism is "not yet landed" while this very PR lands it
(B-0). A contract that disclaims the fence it ships is a trap for the next
reader and for the runbook that cites it. Four sentence edits, no code.

**Before the first derivation night is armed (substantive, code).** Three
clauses that the *pre-registration shipped in this PR* states as binding are
enforced nowhere in code: the sampler-binary hash that "voids this
registration" if it changes, the three-nights-of-twelve sample design the
admissible degrees-of-freedom range is derived from, and the identity of the
pre-registration document itself (B-1/B-2/B-3). These do not block the merge —
merging issues no acceptance, and the candidate artifact is refused by the
production loader — but a pre-registration whose clauses no gate reads is the
exact failure this artifact exists to prevent, and it must be closed before any
corpus is captured under it.

Nothing found touches the physics, the numeric criteria, or any fail-closed
refusal. Every criterion the issuer encodes matches the pre-registration's
digits and names (seam 4, 45 of 45 checked rules MATCH). The three blockers are
promises with no enforcer, not wrong enforcement.

**Coverage of the brief.** Items 1, 2, 3, 4, 5 and 7 are complete with executed
evidence below. **Item 6a — the clause-by-clause sweep of rulings 46 and 69 —
is INCOMPLETE at the deadline**: it was delegated to a read-only agent that had
not returned, and only the partial corroboration in the "Ruled-not-installed"
section below is mine. Item 6b (the `NOT YET LANDED` sweep) is complete.
Do not treat 6a as discharged by this report.

---

## Executed evidence (this session, at d9612e68)

| # | Command | Result |
|---|---|---|
| E1 | `pytest tests/test_docs_freshness.py tests/test_mint_policy_resolver_guard.py tests/test_custody_mode_inventory.py tests/test_authentication_io.py -q` | `61 passed, 589 subtests passed`, rc 0 |
| E2 | `pytest tests/test_issue_calibration_acceptance_generation.py -q` | `91 passed, 72 subtests passed` (105.8 s), rc 0 |
| E3 | `pytest tests/test_calibration_bracketing.py -q -k "generation or admit or envelope or d125 or screen"` | `39 passed, 51 deselected, 33 subtests passed`, rc 0 |
| E4 | `pytest tests/test_issue_calibration_acceptance_generation.py -q -k "only_the_candidate_label_stops_the_candidate_authenticating or registry"` | `2 passed, 89 deselected`, rc 0 |
| E5 | `grep -rn 'SESSION_KIND' joulewise scripts tests --include='*.py'` | classified below |
| E6 | `grep -rn 'NOT YET LANDED\|not yet landed' docs joulewise scripts` | 5 hits, classified below |

Item 5 of the brief is therefore **discharged green**: all four named guard
modules pass at this HEAD.

---

## Seam 1 — S2 ↔ S3 ↔ S1 ↔ S5: the session-kind vocabulary

A *session kind* is the label the ledger writer stamps on a capture session's
opening receipt: `bracket` (a session that reserves the two endpoints of one
claim window) or `derivation` (a session that reserves a night of captures
which build a future acceptance and license no measurement). The seam risk is
that four seats each spell the label as a bare string and one of them
misspells it — a misspelling that fails open, because a comparison against a
wrong literal is simply never true.

**Result: CLEAN.** One home, imported everywhere.

| Site | file:line | Classification |
|---|---|---|
| Definition (ONE HOME) | `joulewise/calibration_ledger.py:72-74` — `SESSION_KIND_BRACKET = "bracket"`, `SESSION_KIND_DERIVATION = "derivation"`, `SESSION_KINDS` | authoritative; exported at `:5925-5927` |
| S3 consumer | `joulewise/calibration_bracketing.py:30-31` | imports both from the ledger — the temporary seam shim recorded in trace 80 is gone at this HEAD |
| S4 issuer | `scripts/issue_calibration_acceptance_generation.py:98`, used `:188`, `:931` | imports |
| S1 writer | `scripts/validate_powermetrics_fiducial.py:72`, used `:1429`, `:1963` | imports |
| reserver | `scripts/reserve_calibration_window_bracket.py:35-37`, `:85-86`, `:147`, `:327` | imports; argparse `choices=SESSION_KINDS` |
| recovery | `scripts/recover_calibration_ledger.py:25`, `:490` | imports |

No stale `DERIVATION_SESSION_KIND` / `BRACKET_SESSION_KIND` literal exists
anywhere (zero grep hits under either spelling). Every surviving bare
`"derivation"` / `"bracket"` string in `joulewise/` and `scripts/` is a
different concept and is **not** a seam hazard:

- `joulewise/identity_pins.py:121,631,2140,…`, `joulewise/arm_readiness*.py`,
  `joulewise/arm_readiness_evidence_t0.py:203` — the `derivation` *field of a
  mint receipt*, unrelated vocabulary, predates this lane.
- `joulewise/whole_window.py:141` — a directory name in the neg-8 reference
  corpus path (`configs/campaigns/neg8_reference_corpus/derivation`).
- `scripts/paper_terms_lint.py:68` — the English word "bracket" in a prose lint
  vocabulary.
- `joulewise/calibration_ledger.py:70,898` — prose comments, adjacent to the
  definitions.

**NIT (no action proposed).** The lane adds a third label,
`SESSION_KIND_UNRESOLVED = "unresolved-session"`, in
`joulewise/calibration_bracketing.py:205` — i.e. *outside* the ledger's one
home. This is defensible and I recommend leaving it: it is a reader-side
sentinel meaning "this row's session cannot be resolved at all", and it must
**not** be a member of `SESSION_KINDS`, because a row bearing it is barred
rather than admitted. Its docstring at `:1695` says so. Flagged only so the
next reader does not "fix" it by moving it.

---

## Seam 2 — S3 ↔ S4: the generation row

A *generation row* is the registry record that fixes, for one acceptance
artifact, every number and rule the validator will judge that artifact by, so
that no artifact is judged against a threshold derived from itself. S4 (the
issuer) **emits** the row; S3 (the validator) **reads** it. Two agents wrote
the two sides and never saw each other's file, so an emitted-but-never-read
field is dead weight and a read-but-never-emitted field is a silent refusal.

Emit side: `scripts/issue_calibration_acceptance_generation.py:1257-1271`
(dict literal) → `generation_row_for_registry` at `:794-801` (converts the two
list fields to tuples). Read side:
`joulewise/calibration_bracketing.py:_registered_generation_row_is_complete`
at `:350-482`, required-key set at `:261-276`.

| Field | Emitted (issuer:line) | Read (bracketing:line) | Status |
|---|---|---|---|
| `corpus_n` | `:1258` | required key `:263`; compared to `expected_n` `:792` | OK |
| `corpus_doubling_trigger` | `:1259` | `:264`, `:787` (trigger set) | OK |
| `prediction_95_two_draw_s` | `:1260` | `:265` | OK |
| `prediction_99_two_draw_s` | `:1261` | `:266`, `:431` (ceiling equation) | OK |
| `operatives` | `:1262` | `:267`, `:389`, `:430`, `:432` | OK |
| `epoch_catalog_ids` | `:1263` (sorted list) → tuple at `:791` | `:268`, `:386`, `:459-462` `isinstance(..., tuple)` | OK — the tuple conversion is what makes it read |
| `prior_prefix_mode` | `:1264` | `:269`, `:452`, `:463`, `:477` | **SF-1**, below |
| `prior_observation_count` | `:1265` | `:270`, `:388`, `:455` | OK |
| `cutoff_sequence` | `:1266` (`snapshot.head_sequence`) | `:271`, `:388`, `:454` | OK |
| `screen_rule` | `:1267` | `:272`, `:464-466`, `:1050-1053` | OK |
| `predecessor_ceiling_s` | `:1268` (`str(...)`) | `:273`, `:396`, `:414-428` | OK |
| `predecessor_acceptance_id` | `:1269` | **not** in required keys `:261-276`; read via `.get()` at `:404`, `:415` | OK — see note |
| `registration_session_ids` | `:1270` (list) → tuple at `:791` | `:274`, `:387`, `:472-479` | OK |
| `d125_ruling` | `:1271` | **not** in required keys; read via `.get()` at `:468-469`, gated by `_D125_RULING_REQUIRED_SCREEN_RULES` `:245` | OK — see note |

**Nothing is emitted that is never read, and nothing required is never
emitted.** The two `.get()`-only fields are correct, not sloppy: the six
historical generations (r1–r6) carry neither, so making them unconditionally
required would break byte-identical re-validation of the shipped artifacts.
Each is instead required *conditionally*, by the rule that needs it —
`predecessor_acceptance_id` becomes mandatory the moment
`predecessor_ceiling_s` is non-null (a row naming a ceiling with no predecessor
id looks up `_D102_GENERATION_DERIVATIONS.get(None)` → `None` → `registered is
None` → refuse, `:415-428`), and `d125_ruling` becomes mandatory the moment
`screen_rule` is the envelope rule (`:464-470`). Test
`tests/test_calibration_bracketing.py:3991-4002` pins that the six issued rows
carry no `d125_ruling`.

**Trigger-set equality: verified equal, but with two homes.** The five
re-derivation trigger names the validator demands
(`joulewise/calibration_bracketing.py:783-789`, an inline set literal) are
rebuilt by the issuer in `rederivation_triggers`
(`scripts/issue_calibration_acceptance_generation.py:752-768`). I compared the
two sets character by character: identical, both keyed on the row's own
`corpus_doubling_trigger`. See **SF-2**.

End-to-end seam proof exists and passes:
`tests/test_issue_calibration_acceptance_generation.py:1068-1100`
(`test_only_the_candidate_label_stops_the_candidate_authenticating`) runs the
real issuer, flips only the three candidate-label fields, feeds the row through
`generation_row_for_registry` and has the *production* validator admit the
artifact — E4, E2 green.

---

## Seam 5 — documentation freshness and line-pin rot

### The `NOT YET LANDED` sweep (brief item 6b) — **BLOCKER-ON-MERGE**

Reproduce: `grep -rn 'NOT YET LANDED\|not yet landed' docs joulewise scripts`

| file:line | Current text (abridged) | True at d9612e68? | Should say once merged |
|---|---|---|---|
| `docs/contracts/calibration_ledger.md:178` | "…is a per-generation registration, not a global rule (ruled 2026-09-10, not yet landed; see …)" | **NO — landed.** `prior_prefix_mode` is a required registry key (`calibration_bracketing.py:269`) and is enforced at `:452,463,477` | "(ruled 2026-09-10; enforced by `_registered_generation_row_is_complete`)" |
| `docs/contracts/calibration_ledger.md:201` | "(Ruled 2026-09-10, not yet landed; seats S3 and S4 install it.)" | **NO — landed.** The fifth `session_id` per-row binding is added at `calibration_bracketing.py:763` and matched against `registration_session_ids` at `:919-930` | "(Ruled 2026-09-10; installed — the fifth key is added for `import_plus_live` rows and matched against the registration's sessions.)" |
| `docs/contracts/powermetrics_fiducial.md:253` | "…addendum 11, 2026-09-10; NOT YET LANDED; see …" | **NO — landed.** S1's derivation-only mode and the ledger-side licenses-nothing rule are both in code | drop "NOT YET LANDED" |
| `docs/contracts/powermetrics_fiducial.md:333` | "A derivation-only artifact (cold gate 46 and its dated addendum 11, 2026-09-10; NOT YET LANDED) satisfies all of them…" | **NO — landed.** | drop "NOT YET LANDED" |
| `docs/reviews/2026-07-10-hardening-adjudication.md:27` | historical review prose | **N/A** — a dated 2026-07-10 record, correct as written | leave alone |

These four were true when S6 wrote them (S1/S3/S4 had not merged yet) and this
PR is exactly what makes them false. Note that `tests/test_docs_freshness.py`
forbids PR-number literals, so the replacement wording must name the code site,
not the PR.

### Line-pin rot (brief item 5b) — **SHOULD-FIX, needs a ruling not a seat**

`tests/test_authentication_io.py:66-97`,
`CLASSIFIED_NON_AUTHENTICATION_READS`, keys each allowed read as
`file:function:LINE:call`. Eight of its entries churned in this PR purely
because `joulewise/calibration_ledger.py` grew above them:

    _filesystem_type                2862 → 2983
    _open_slot_sidecar              2966 → 3087
    resolve_ledger_lease_identity   2914 → 3035, 2928 → 3049
    publish_genesis_payload         3242 → 3363
    open_append_descriptor          3297 → 3418
    repair_calibration_ledger       3928 → 4049
    abandon_calibration_ledger_tail 3985 → 4106

All eight shifted by exactly +121 lines; trace records 97 and 98 confirm no
read-capable IO was added. Contrast the sibling guard
`tests/fixtures/custody_read_replay_allowlist.json`, whose two **new** rows
(added by this PR) are keyed on `(file, function, ordinal)` with `line` carried
as documentation only. Re-key the v2 surface guard the same way. This is not a
defect of this lane — the lane inherited it and did the mechanical thing — but
it will red the suite on the next insertion anywhere above `calibration_ledger.py:~2900`,
and every such red is a false alarm that costs a root-cause round (it already
cost one: record 97/98). It is called out in the trace as needing a ruling.

No *new* absolute-line pin is introduced by this lane. The two new custody
allowlist rows carry `"line": 1074` and `"line": 268` but are keyed on
`(file, function, ordinal)`, so they document rather than bind.

---

## Seam 3 — S1 ↔ S5 ↔ S7: flags and the window arithmetic

### (A) The night chain's argv against the writer's parser — CLEAN

The chain invokes the writer once per slot at
`scripts/night_chains/calibration_derivation_only.zsh:196-205`. I listed the
parser's real flags by running it (executed, not read):

    PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python \
      scripts/validate_powermetrics_fiducial.py --help

| Flag the chain passes | chain:line | Parser accepts? |
|---|---|---|
| `--allow-live` | `:197` | yes |
| `--derivation-only` | `:198` | yes |
| `--ledger "$CALIBRATION_LEDGER"` | `:199` | yes |
| `--head-pin "$LEDGER_HEAD_PIN"` | `:200` | yes |
| `--session-id "$SESSION_ID"` | `:201` | yes |
| `--slot "$slot"` | `:202` | yes |
| `--attempt-id "${SESSION_ID}-${slot}"` | `:203` | yes |
| `--output-root "$RUNS_ROOT/instrument_validation"` | `:204` | yes |
| `--power-policy ac_high_power` | `:205` | yes |

Nine passed, nine accepted, none omitted that the derivation-only path
requires: the writer's own refusal at `scripts/validate_powermetrics_fiducial.py:1944`
demands `--session-id`, `--slot` and `--attempt-id`, and the chain supplies all
three. The chain's own header comment documents this contract at `:30-32`.

### (B) The wrapper generator's per-slot flags against the reserver — CLEAN

`scripts/gen_derivation_night.py:242-243` emits, per slot, exactly one
`--slot-attempt-id` and one `--slot-custody-locator`. With
`PRE_REGISTERED_SLOT_COUNT = 12` (`:64`) that is **12 × 2 = 24 per-slot flags**,
which is the count the brief expected. Both flag names appear in
`scripts/reserve_calibration_window_bracket.py`'s parser (verified by executed
`--help`), alongside `--slot-count`, `--session-kind` and `--session-id`. The
reserver refuses a repeated-flag count that disagrees with `--slot-count`
(chain header `:28`), so a generator that emitted 11 or 13 pairs fails closed.

### (C) Cadence and budget constants — CLEAN, arithmetic agrees at 128 min

| Constant | Chain (.zsh) | Generator (.py) | Pre-registration |
|---|---|---|---|
| slots per night | `:66` `SLOT_COUNT="${SLOT_COUNT:-12}"` | `:64` `PRE_REGISTERED_SLOT_COUNT = 12` | `:112`, `:116`, `:145` "12 declared slots" |
| settle before slot 1 | `:67` `SETTLE_S=600` | `:76` `DEFAULT_SETTLE_S = 600` | `:116` "one 600 s settle after the last operator action" |
| start-to-start cadence | `:68` `SLOT_CADENCE_S=600` | `:77` `DEFAULT_SLOT_CADENCE_S = 600` | `:116-117` "12 slots at a 600 s start-to-start cadence" |
| per-slot capture budget | `:71` `SLOT_CAPTURE_BUDGET_S=480` | `:78` `DEFAULT_SLOT_CAPTURE_BUDGET_S = 480` | `:95` "one ~8 min capture" (480 s) |
| total window | derived at `:178`, `:190` | `:115` "600 + 11 x 600 + 480 = 7680 s" | `:95-96` "…is 128 min" |

Arithmetic, shown: 600 + (11 × 600) + 480 = 600 + 6600 + 480 = **7680 s =
128.0 min**. The generator states the sum in its own docstring; the
pre-registration states the same sum in minutes; the chain never states a total
and instead re-derives the fit per slot (`slot_start + SLOT_CAPTURE_BUDGET_S >
WINDOW_END_EPOCH_S` → record the slot unused and abort). Eleven cadences, not
twelve, is the correct term — the twelfth slot needs only its capture budget,
not another cadence gap — and all three sites agree on that.

Note the cadence anchor: `:209` sets the next start from the *actual* slot
start, never from the previous end, so a long capture cannot compress a later
slot. That is the behaviour the pre-registration's "start-to-start" wording
requires, and the two agree.

*(An independent Opus agent was auditing this same seam in parallel; if its
report lands after this one it should be read as corroboration, not as the
primary evidence. Everything above was executed by me at this HEAD.)*

---

## Seam 4 — S4 ↔ S6: does the issuer encode exactly what the pre-registration promises?

A *pre-registration* is the document that fixes the acceptance criteria before
any measurement exists, so that the criteria cannot be chosen to suit the
numbers. The seam question is therefore not "is the code correct" but "does the
code obey a rule the document stated first, with the same digits and the same
name". Doc side: `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`.

| Rule | Code file:line, literal | Pre-registration line, quoted | Verdict |
|---|---|---|---|
| Screen floor 0.010818 s | `joulewise/calibration_bracketing.py:238` `D125_SCREEN_FLOOR_S = Decimal("0.010818")`, imported by the issuer at `:83`, applied at `:1149` | `:195` "S = max(new range quantized to 1e-6 s ROUND_HALF_EVEN, 0.010818)"; also `:146`, `:202` | MATCH — and one home: the issuer imports the constant instead of restating the digits (this was enforced by the mint-policy resolver guard; commit `deada45c`) |
| Screen rule name | `joulewise/calibration_bracketing.py:230` `SCREEN_RULE_FLOORED_RANGE_ENVELOPE = "floored_range_envelope_screen"` | `:195` states the rule; the *name* is a registry key, not doc text | MATCH (name is code-side vocabulary by design — see trace 82) |
| Budget ceiling C | issuer `envelope_ceiling`, `:744`-region; validator equation at `calibration_bracketing.py:430-434` | `:195-196` "budget ceiling C = max(predecessor ceiling, …)" | MATCH |
| Strict `S < C` | `calibration_bracketing.py:434` `or not screen < drift` | `:201-202` "corpus is not issued … The refusal is never cured by lowering S" | MATCH |
| Corpus floor n ≥ 19 | `:332` `SUCCESSOR_MINIMUM_CORPUS_SIZE = 19`; enforced `:1055-1066` | `:145-147` "Retained n >= 19 is REQUIRED for issuance: D-126 clause 2's SUCCESSOR_MINIMUM_CORPUS_SIZE = 19 is a corpus-size floor, not the 0.010818 screen floor." | MATCH — and the doc explicitly disambiguates the two floors, which is the confusion the code comment also guards |
| n = 17 only by Ed's written ruling | `:338` `RULED_ALTERNATIVE_CORPUS_SIZE = 17`; `--ed-ruling` required, `:1055-1066`, help text `:1583-1591` | `:147` "Ed may instead rule in writing that n = 17 is acceptable; nothing issues below 19 without that written ruling." | MATCH — no third value is licensed on either side |
| Screen challenge ≥ 2 over 0.032898493715362 | `:326` `R6_PREFLIGHT_LEVEL_SCREEN_S`, `:330` `SCREEN_CHALLENGE_MEMBER_LIMIT = 2`, refusal `:1125-1128` | `:160` "If two or more retained members exceed 0.032898493715362, the corpus is not issued and Ed rules in writing" | MATCH |
| Second diagnostic threshold | `:329` `R6_MAXIMUM_PLUS_RANGE_S = Decimal("0.04262208300415633")` | `:162` "0.04262208300415633 (the Decimal sum of 0.03289849371536248 and 0.00972358928879385)" | MATCH — I checked the stated sum: 0.03289849371536248 + 0.00972358928879385 = 0.04262208300415633 exactly |
| Quantile proof: residual ≤ 1e-30 | `:385` `QUANTILE_PROOF_MAXIMUM_FORWARD_RESIDUAL = Decimal(1).scaleb(-30)` | `:174` "absolute residual at most 1e-30"; `:185` | MATCH |
| Quantile proof: ≥ 30 significant digits | `:384` `QUANTILE_PROOF_MINIMUM_AGREEMENT_DIGITS = 30` | `:185` "agreement at least 30 significant digits — are the ISSUER'S DECLARED bounds" | MATCH |
| Blindness | `refuse_open_registration` (issuer, before any row is read) + `TERMINAL_SESSION_STATES = frozenset({"finalized", "aborted"})` | `:152-153` "The fence is installed by the issuer, not left to convention. prepare-candidate refuses to run while any session named in the registration is not terminal — terminal meaning its last declared slot is …" | MATCH — the doc names the *mechanism*, not just the intent |
| `d125_ruling` reference required | issuer `:1047-1048` refuses with "d125_ruling reference absent"; validator requires it on envelope rows, `calibration_bracketing.py:464-470` | pre-registration's D-125 section `:195-202` + D-102 addendum in `docs/decision_log.md` | MATCH |
| `predecessor_ceiling_s` / `predecessor_acceptance_id` | issuer `:1269-1270`; validator reads the predecessor's ceiling back from its OWN registered row, `calibration_bracketing.py:414-428` | `:195-196` | MATCH — stronger than the doc: the successor cannot rebase its lineage by editing one number |

**No number in the issuer's acceptance path is absent from the
pre-registration, and no pre-registered number is missing from the code.** The
one structural note worth recording: the predecessor arm of the ceiling rule
(`C = max(predecessor ceiling, own Q99)`) is *provably inert for this
generation* — with r6 as predecessor, `S ≥ 0.010818 > ` r6's ceiling — so no
test can exercise it through this generation's CLI. S4 flagged this itself
(trace 82, flag 3) and S3 covers the arm with a direct unit test on the pure
function instead (`tests/test_calibration_bracketing.py`, the
`max(predecessor, prediction)` operand-collapse cut of trace 88). That is the
right resolution and I am not re-opening it.

**The parallel S4↔S6 lens returned and went wider than the twelve rules named
in the brief: 72 rules traced, every numeric literal in the issuer's acceptance
path accounted for.** Its verdicts agree with mine on all twelve, and it found
three additional classes I had not looked for, each of which I then re-verified
myself at this HEAD (B-1/B-2/B-3 and SF-0 in the findings below):

- rules the code enforces that the pre-registration never names — including the
  registered `screen_rule` token itself (SF-6);
- rules the pre-registration states that no code path reads — the sampler-hash
  binding, the three-nights-of-twelve design, the identity of the
  pre-registration document (B-1, B-2, B-3);
- numeric semantics the code fixes and the document leaves to inference — the
  binary64 prediction arithmetic and the 1e-18 presentation quantum (SF-5).

Also worth recording as a *strength*: at row 8 of that pass, the predecessor
ceiling `0.010164834757777545` that the pre-registration quotes as a literal is
**derived** by the issuer from the authenticated predecessor artifact rather
than hardcoded — the code is stricter than the document. The same pass verified
by execution that the realized degrees of freedom 16–35 all clear the proof
bounds with margin (residuals 2e-82 … 5.2e-80 against a 1e-30 bound; agreement
55–57 digits against a 30-digit bound).

---

## Findings, severity-tiered (my own lens; agent lenses appended below)

### BLOCKER-ON-MERGE

**B-0 — Four contract sentences become false the instant this PR lands.**
`docs/contracts/calibration_ledger.md:178`, `:201`;
`docs/contracts/powermetrics_fiducial.md:253`, `:333`. Table above. These are
the documents the derivation-night runbook cites to the operator, so a reader
following them would conclude the fence they are relying on is not in force.
Fix is four sentence edits, no code.
Reproduce: `grep -rn 'NOT YET LANDED\|not yet landed' docs`

### BLOCKER-BEFORE-ARM (pre-registration clauses with no enforcer)

Found by the parallel S4↔S6 lens; **each one re-verified by me at this HEAD**
with the command shown. These are the "ruled-not-installed" shape applied to
the pre-registration rather than to a ruling: the document states a criterion,
and no code path reads it.

**B-1 — The pre-registered sampler-binary hash is enforced nowhere.**
`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:107-109` names
`/usr/bin/powermetrics` SHA-256 `b762e5bf…30c5` and says in terms "A change to
either voids this registration." The issuer's `check` compares the machine's
observed hash against the **ledger's own last-row T1 bindings**
(`scripts/issue_calibration_acceptance_generation.py:283`,
`WATCH_FIELDS[2:]`), never against that literal. A campaign captured end to end
under a different sampler binary reports `match` on every watch line. The
number in the registration is decorative.
Verified: `grep -rn 'b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5' --include='*.py' .` → **0 hits**.

**B-2 — The issuer does not bind the corpus to the pre-registered sample
design.** The pre-registration fixes three windows of twelve declared slots
(`:115-119`, `:145`) and derives the admissible degrees-of-freedom range 18–35
from exactly that ceiling of n ≤ 36 (`:166-167`). It also computes, at `:91-94`,
that two nights of twelve project 16.95 retained observations — *below* the
floor of 19. Yet `--registration-session-id` is an unbounded `append` list
(`scripts/issue_calibration_acceptance_generation.py:1565-1567`, deliberately
not `required=True`) and no code path compares the session count to 3 or a
session's declared-slot count to 12; the dry run only *prints* `declared=`
(`:222`). The 12-slot fence exists solely in the night wrapper
(`scripts/gen_derivation_night.py:64,419-427`), with its own ruling escape, and
nothing carries it forward to issuance.
Verified: `grep -n 'registration-session-id' -A 3 scripts/issue_calibration_acceptance_generation.py`.

**B-3 — Nothing ties the derived corpus to *this* pre-registration.**
`--preregistration` is hashed and the digest recorded
(`scripts/issue_calibration_acceptance_generation.py:1068-1070` →
`:1354-1357`), but the digest is never compared against a pin, and the corpus's
`target_epoch` (read from the ledger rows at `:1093`) is never checked against
the six-field epoch the pre-registration declares at `:105-106`. So
`prepare-candidate --preregistration README.md` yields a candidate that attests
to the wrong document, and a corpus captured under a different epoch issues
identically. For an artifact whose whole authority is "the rules were fixed
before the data", a self-declared unverified pointer is the load-bearing link.
Verified: `grep -n 'preregistration' scripts/issue_calibration_acceptance_generation.py` — five hits, none a comparison.

### SHOULD-FIX

**SF-0 — The n ≥ 19 corpus floor is no longer in the validator.**
`grep -rn 'SUCCESSOR_MINIMUM_CORPUS_SIZE' joulewise/` → **0 hits** (verified).
It lives only in the issuer script (`:332`, enforced `:1055-1066`).
`joulewise/calibration_bracketing.py` checks only that the artifact's `corpus.n`
equals the registry row's `corpus_n`, so a small-n candidate promoted by a
hand-edited registry row validates. The pre-registration promises at `:147`
that "nothing issues below 19 without that written ruling". Defense in depth,
one line in the validator.

**SF-1 — The issuer hardcodes `prior_prefix_mode` instead of importing it.**
`scripts/issue_calibration_acceptance_generation.py:1264` writes
`"prior_prefix_mode": "import_plus_live"` as a bare string, while the same
file's import block (`:79-92`) already pulls ten other constants — including
`D125_SCREEN_FLOOR_S` and `SCREEN_RULE_FLOORED_RANGE_ENVELOPE` — from
`joulewise.calibration_bracketing`, which defines
`PRIOR_PREFIX_MODE_IMPORT_PLUS_LIVE` at `:211`. It **fails closed** today (a
typo is rejected by the membership test at `calibration_bracketing.py:463`), so
this is consistency, not correctness. Import it.
Reproduce: `grep -n 'import_plus_live' scripts/issue_calibration_acceptance_generation.py joulewise/calibration_bracketing.py`

**SF-2 — The five re-derivation trigger names have two homes, and the docstring
says otherwise.** `scripts/issue_calibration_acceptance_generation.py:752-768`
(`rederivation_triggers`) claims in its own docstring to be "One home for the
rule", but the validator carries its own inline copy of the four fixed names at
`joulewise/calibration_bracketing.py:783-789`. I verified the two sets are
identical today, and set equality means any drift fails closed (the artifact
refuses) rather than open. But two homes with a docstring asserting one is how
a future edit lands in only one of them. Either export a shared constant from
`calibration_bracketing` and have both sides build from it, or add a test that
asserts the issuer's set equals the validator's for a given
`corpus_doubling_trigger`. No test does this today.
Reproduce: `grep -rn 'rederivation_triggers' tests/ scripts/ joulewise/`

**SF-3 — The v2 surface guard's line pins will red again on the next
insertion.** `tests/test_authentication_io.py:66-97`. Detail in Seam 5. Needs
a ruling (re-key on `(file, function, ordinal)` like
`tests/fixtures/custody_read_replay_allowlist.json`), not a seat fix inside
this PR.

### NIT

**SF-4 — Two homes for r6's level screen and r6's max-plus-range.**
`scripts/issue_calibration_acceptance_generation.py:326`
(`R6_PREFLIGHT_LEVEL_SCREEN_S`) and `:329` (`R6_MAXIMUM_PLUS_RANGE_S`) restate
digits that the same run could read from the predecessor artifact it already
authenticates (`:1153-1154` reads the ceiling that way). Point
`--predecessor-acceptance` at any other artifact and the screen challenge keeps
judging against r6 in silence. The file states this exact principle for the
four constants it *does* import, at `:320-322`.

**SF-5 — The prediction that sets the budget ceiling is computed in binary64,
and the pre-registration never says so.**
`scripts/issue_calibration_acceptance_generation.py:700` returns
`repr(float(quantile) * float(sample_sd_lexeme) * math.sqrt(2))`. That value is
Q99, and Q99 is one arm of the ceiling `C = max(predecessor ceiling, Q99)`
(`:1155`). The pre-registration spends thirteen lines (`:165-183`) establishing
80-digit Decimal rigor and then delegates the operative-determining arithmetic
to "Decimal statistics exactly as r6" — a phrase that resolves to binary64 only
if the reader opens r6's artifact. Same gap for the 1e-18 presentation quantum
(`:345`) and for the fact that the standard deviation fed to the prediction is
the *rounded* presentation value (`:1142`), not the full-precision one.
`grep -c binary64 configs/calibration/preregistration_d079_epoch_25g83_rev1.md` → 0.
This is a first-use-test failure on criteria-bearing numeric semantics, in the
one document whose job is to be replicable.

**SF-6 — `floored_range_envelope_screen` is machine-checked and named in no
document.** `grep -rn 'floored_range_envelope' docs/ configs/` → 0 hits. The
pre-registration describes the rule mechanically (`:194-195`) but never states
the token the artifact must carry, so no reader can check the emitted row's
`screen_rule` against the document by name. Same for `predecessor_acceptance_id`,
`registration_session_ids` and `corpus_doubling_trigger`.

**SF-7 — The registration's own rows are never checked for
`systematic-invalid`.** The pre-registration asserts at `:124-125` that no such
disposition can exist for this epoch. A row bearing it passes the issuer
invisibly: it is not `"valid"` so it is not a member
(`scripts/issue_calibration_acceptance_generation.py:957`), and it *is* in
`PRIOR_SET_DISPOSITIONS` (`:335`) so it is not flagged unresolved
(`:1203-1208`). The writer-side fence makes it unreachable today; catching the
case where that fence failed is precisely the issuer's job.

### NIT

**N-0 — Dead import that misleads.**
`scripts/issue_calibration_acceptance_generation.py:100` imports
`content_id_from_artifact_hashes` and never uses it (single grep hit). The
pre-registration says at `:135` that the excluded row "is matched by the
content id derived from those two hashes"; a reader may take the import as
evidence the issuer does that matching. It does not.

**N-2 — The pre-registration explains the wrong accuracy limiter.** `:177-178`
attributes the quantile proof's resolution to "300 halvings, which resolves t
to about 1e-88". Measured agreement is 55–57 digits, because the real cap is
the undocumented continued-fraction tolerance `Decimal(1).scaleb(-55)` at
`scripts/issue_calibration_acceptance_generation.py:428`. The 30-digit bound
still clears by 25 digits — nothing is unsound — but the stated cause is wrong,
and a methodology section a reader cannot replicate from is not done.

**N-3 — Ruling references accept any non-empty string**
(`scripts/issue_calibration_acceptance_generation.py:1570-1585`). `--d125-ruling x`
satisfies the pre-registration's "rule in writing" (`:147`). The sibling tool
validates its ruling text (`scripts/gen_derivation_night.py` `_validated_ruling`:
one line, character class, census-clean); the issuer does not.

**N-4 — The epoch watch covers 2 of the 6 epoch fields directly**
(`scripts/issue_calibration_acceptance_generation.py:266`, `WATCH_FIELDS[:2]`),
while its own docstring claims to print "how the machine's identity today
compares with the epoch that artifact binds". Overstated coverage; related to
B-1.

**N-5 — The Blindness clause's "only" list is not exhaustive.**
Pre-registration `:154-157` enumerates four printed things; the dry run also
prints the pending/unresolved row count (`:234`), the admissibility verdict
(`:237-240`) and per-blocker reasons (`:241-242`). None carries a measured
value, so the substantive fence holds — but an auditor checking the tool
against the word "only" will find unlicensed output.

**N-6 — `SESSION_KIND_UNRESOLVED` lives outside the ledger's vocabulary home**
(`joulewise/calibration_bracketing.py:205`). Correct as designed; flagged only
so nobody "corrects" it. No action.

---

## What a PR reader needs that the trace does not say plainly (brief item 7)

Three facts are recorded in the trace but nowhere a PR reader would look. They
belong in the PR body, and the draft below carries them.

**(a) Every implementation seat and every refuter in this lane was Opus.**
Trace record 57: the Codex quota was exhausted at ~08:41 PDT on 2026-09-10 and
does not reset until 2026-09-15 00:52 PDT. Seats S2/S3/S5/S6 died mid-run and
were relaunched as Opus agents under the same briefs and the same write scope;
S1, S4 and S7 were Opus from the start. The gate *shape* was unchanged — an
execution-lens refuter, a contract-lens refuter, and a delta re-audit after
every fix round — but **cross-model diversity is reduced to one model family
for implementation and review**. Two upstream stages did have diversity: the
design stage ran three families (records 41 Astra / 42 cold Fable / 43b Opus)
and the mechanism ruling had an Opus pairing refuter. Record 57 registers this
as a limitation, explicitly not waived. It should be stated in the PR, because
a reader who assumes cross-model refutation will over-trust the review depth.

**(b) Three Ed veto windows are open over rules this PR encodes.** None of them
is settled by merging; the code is written so that merging settles nothing.

| Item | What is open | Where |
|---|---|---|
| The screen rule `S = max(range quantized to 1e-6, 0.010818)` | Adopted as a *proposed default* by cold gate 46; Ed may veto | trace 80; label pinned as "adopted by cold gate 46, Ed veto window open" (`docs/decision_log.md` D-102 addendum) |
| V3 — three nights × 12 declared slots, and retained n ≥ 19 | Requires Ed's **affirmative** written acknowledgment before the first capture is armed; silence is *not* consent for V3 | trace 49, 62, 66 |
| The operand-collapse mutation rule (adversarial-review skill amendment) | Adopted as amended by cold gate 69, subject to Ed's veto | trace 69, 84, 88 |

The safety property that makes merging safe under three open vetoes: the issuer
emits `candidate_not_issued` and the production loader refuses the artifact
(`tests/test_issue_calibration_acceptance_generation.py:1068-1100` proves the
candidate label is the *only* thing stopping it), so nothing in this PR can
produce a claim-bearing acceptance. The runbook draft (record 99, `:216`) says
in terms: do not arm night 1 without the veto resolved.

**(c) The guard re-keying ruling is a real open item, not a nit.** Records 97
and 98 root-caused a red replay to the v2 surface guard's absolute line pins
and explicitly deferred the cure — "needs a ruling, not a seat". SF-3 above.
The PR should name it so it is not rediscovered a third time.

---

## Proposed PR body (≤ 60 lines, plain language)

```markdown
## What this does

macOS build 25G83 changed the machine under our timing instrument. The
*acceptance artifact* — the file that fixes the numeric limits every energy
measurement is judged against — was derived on the previous build, so it no
longer describes this machine. This PR builds the machinery to derive a
replacement. It captures no data and issues no acceptance.

- **Derivation-only capture.** The capture writer gains `--derivation-only`: it
  records a timing bundle for a *future* acceptance and licenses nothing — no
  measurement window, no probe reduction, no bracket endpoint.
- **Derivation sessions.** The append-only ledger learns a second session kind.
  A `bracket` session reserves the two endpoints of one claim window; a
  `derivation` session reserves a night of derivation-only captures.
- **Generation-keyed validation.** The validator now reads its limits from a
  per-generation registry row instead of from constants, so the six existing
  acceptance artifacts keep validating byte-identically while a new one can be
  judged under the new rule.
- **A candidate issuer.** `check` watches the machine's identity fields;
  `prepare-candidate` derives a candidate acceptance from a finished corpus.
  Its output is stamped `candidate_not_issued` and the production loader
  refuses it.
- **Night chain and wrapper generator.** A plan-pinned script that runs the
  declared capture slots unattended: one 600 s settle, then 12 slots at a 600 s
  start-to-start cadence with an 8-minute capture budget each — 128 minutes.
- **Contracts and pre-registration.** The rules written down before any data
  exists, which is the point: criteria chosen after seeing numbers are not
  criteria.

## What it cannot do

Merging issues no acceptance and licenses no claim. A test proves the candidate
label is the only thing stopping the artifact from authenticating, so the
refusal is the label, not an accident of shape.

## Close before arming night 1

Terminal review found three clauses the pre-registration states as binding that
no code reads. They do not block the merge; they must not survive it.

1. The `powermetrics` binary hash the registration says voids it on change is
   compared against nothing — the tool checks the ledger's own recorded
   bindings instead.
2. Nothing binds the corpus to the pre-registered design of three nights of
   twelve slots, from which the admissible sample sizes are derived.
3. The pre-registration file is hashed and recorded but never checked against a
   pinned digest, and the corpus epoch is never compared to the epoch the
   document declares.

## Also worth knowing

- **Three Ed veto windows are open**; merging settles none: the screen rule
  `S = max(range quantized to 1e-6, 0.010818)`; V3 (three nights of 12 slots,
  retained n >= 19), which needs Ed's affirmative written acknowledgment —
  silence is not consent for V3; and the operand-collapse mutation rule.
- **Reduced model diversity.** The Codex quota was exhausted on 2026-09-10 and
  does not reset until 09-15, so every implementation seat and every refuter in
  this lane was Opus. The review shape was unchanged and the design stage did
  have three model families, but cross-model refutation of the code was not
  available. Recorded as a limitation, not waived.
```

---

## Ruled-not-installed table (brief item 6a) — DELEGATED, PENDING AT WRITE TIME

A dedicated read-only Opus agent is enumerating every implementation clause of
cold-gate rulings 46 and 69 (plus their `11-ruling-addendum-opus-amendments.md`
files: 145 + 61 lines for 46, 141 + 22 for 69) against code sites at this HEAD.
It had not returned when this report was written to the 45-minute deadline.

**Do not treat item 6a as discharged by this report.** What I can state from my
own reading is partial corroboration only, and it is positive as far as it
goes — every ruling clause I happened to touch while auditing the other seams
was installed in production code, not merely asserted in a test:

| Clause (source) | Code site at d9612e68 | Status |
|---|---|---|
| 46 §R-a A7 — session kinds stamped on the open receipt, ledger owns the vocabulary | `joulewise/calibration_ledger.py:72-74`, comment at `calibration_bracketing.py:198-204` | INSTALLED (production) |
| 46 §R-b V6 — prior-set prefix modes `import_only` / `import_plus_live` | `joulewise/calibration_bracketing.py:211-215`, enforced `:452,463,477` | INSTALLED (production) |
| 46 §R-b V7 — registered screen-rule vocabulary; unimplemented rule name refuses | `joulewise/calibration_bracketing.py:216-233`, `:464` | INSTALLED (production) |
| 46 §R-a A6 — mechanism-named, outcome-independent corpus exclusions | `joulewise/calibration_bracketing.py:252` `REGISTERED_CORPUS_EXCLUSION_REASONS` | INSTALLED (production) |
| 46 §R-d — a fresh v3 capture stores its OWN anchor value; read from hashed primary bytes, never recomputed | `scripts/issue_calibration_acceptance_generation.py:865-885` `anchor_v3_replay_outcome` | INSTALLED (production) |
| 46 V7 — issuance refuses while the `d125_ruling` reference is absent | `scripts/issue_calibration_acceptance_generation.py:1047-1048` | INSTALLED (production) |
| 69 + addendum A4 — `predecessor_ceiling_s` paired with `predecessor_acceptance_id`, jointly present or jointly absent | `joulewise/calibration_bracketing.py:398-406` | INSTALLED (production) |
| 69 addendum A2 — `d125_ruling` recorded in the emitted row and required on envelope rows | issuer `:1271`; validator `:464-470` | INSTALLED (production) |
| CG46 addendum A-2 — corpus-size floor departure requires `--ed-ruling` | `scripts/issue_calibration_acceptance_generation.py:1055-1066` | INSTALLED (production) |

The agent's full enumeration should be appended to this file as an addendum
before the merge decision is taken, per the standing rule that a ruling with an
implementation clause is not discharged until someone has looked for the code
site and found it.

<!--AGENTS-->



