# 93 — S4 (`prepare-candidate`) CONTRACT-LENS refutation

Refuter: Opus 5 contract lens, read-only in `/Users/edr/code/JouleWise-wt-s4-issuer-prepare`
(HEAD `a3ae7bf8`; seat work = `git diff 0fe1fc5e 501bde4f`). No edits, no git state changes, no
mutation cuts, nothing written into `configs/calibration`, no captures. Executed this session:
file reads, `grep`, and `python3 scripts/issue_calibration_acceptance_generation.py --help`.
Every line number below was read this session in this worktree.

**VERDICT: MERGEABLE AFTER FIXES.**

No emitted number is wrong, and nothing the tool can do today issues anything: every path either
refuses or writes a `--out` file the production loader cannot authenticate as authority. The fixes
below are two classes: (a) **pre-registered fences the issuer does not carry** — the blindness /
terminal-session guard and the pending-row refusal — which must land **before the first
`prepare-candidate` run**, not merely before merge; (b) **contract-prose and floor-parameter
divergences** that must land before the D-138 transaction. The one arithmetic invention (the
quantile-proof bounds) is conservative but unrecorded outside the code.

---

## 1. Clause table

Authority abbreviations: **PR** = `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`
(this tree); **CG46** = cold-gate ruling 46 §10 and its addendum §11 (A-1…A-8); **CG69** = cold-gate
ruling 69 §10 and its addendum §11 (A1–A6). Code paths are
`scripts/issue_calibration_acceptance_generation.py` unless prefixed.

| # | Clause (authority) | Code site | Status |
|---|---|---|---|
| 1 | V5 (CG46:39): one tracked issuer, subcommands `check` and `prepare-candidate` | `:1180-1186`, `:1188-1237` | PRESENT |
| 2 | V5: `check` = "desk epoch watch **and registration dry-run**" (CG46:39; repeated `docs/decision_log.md:6603`) | `check` `:99-148` — epoch watch only; no registration argument, no dry-run | **MISSING** (ruled-not-installed, §5 F-6) |
| 3 | PR Membership: corpus = every registration observation with ledger disposition `valid` whose anchor-v3 replay resolves | `_select_members` `:686-727`; disposition filter `:697` | PRESENT |
| 4 | PR Membership: "No observation is excluded on the basis of its `b_fiducial_s`" | `:686-727` — membership turns only on `resolved`; the value is read after the decision | PRESENT |
| 5 | PR Membership / CG46 A-7: a valid same-epoch observation outside the registration **refuses issuance** | `:824-838` (`foreign`), refusal `:833` | PRESENT (also independently in `joulewise/calibration_bracketing.py:917-927`) |
| 6 | PR Membership: excluded members listed with mechanism + `member_id` + `manifest_sha256` + `instrument_evidence_sha256` | entry built `:702-708`, appended `:715`, emitted `derivation_notes.excluded_members` `:1033` | PRESENT |
| 7 | PR Exclusions: mechanism-named, outcome-independent, registered class only (`affine_clock_fit_empty`) | `:710-714` refuses any detail outside `REGISTERED_CORPUS_EXCLUSION_REASONS` (`calibration_bracketing.py:252` = `{affine_clock_fit_empty}`) | PRESENT, fail-closed |
| 8 | PR glossary: "**Anchor-v3 replay** — re-deriving a capture's fiducial bound from its primary evidence bytes with the anchor-v3 estimator" | `anchor_v3_replay_outcome` `:625-644` **reads** the stored `clock_anchor` record; no re-derivation. Bytes are authenticated against the ledger row (`:592-607`) and the stored lexeme is compared to `exact_bound_lexeme_s` (`:717-722`) | **DIVERGENT in words** — CG46:112 settles the science (`stored_lexeme_is_member_value: True`, "a fresh v3 capture stores its own value"), so the behaviour is ruled-correct; the artifact prose and the PR glossary describe a re-derivation the code does not perform. §4 F-7 |
| 9 | PR Stopping: retained n ≥ 19 REQUIRED; the only stated departure is Ed's written **n = 17** | floor constant `:169`; refusal `:773-778`; check `:840-843` | **DIVERGENT** — `--ed-ruling <any string>` admits **any** floor ≤ 19 (`:773`), e.g. `--minimum-corpus-size 3`. §3 SF-2 |
| 10 | PR Analysis: df run 18–35, or 16 under the n = 17 ruling | `degrees_of_freedom = n - 1` `:845`; no df admissibility check | DIVERGENT via clause 9 (the df set is only as bounded as the floor) |
| 11 | PR Blindness: "No member value, screen, or statistic is examined … before the third night's session is **terminal** and its pin candidate is emitted" | `_registration_observations` `:648-672` checks `session_kind` only; `CalibrationBracketSession.state` (`calibration_ledger.py:491`, values `open`/`finalized`) is never consulted | **MISSING** — §3 SF-1 |
| 12 | PR Prospective use: "a **pending or unresolved** attempt in that prefix **refuses issuance**" | `:920-930` builds the prior set with `if observation.content_id is not None` — pending rows are silently dropped, not refused | **MISSING at the issuer** (fails closed later at `calibration_bracketing.py:1849-1856`). §3 SF-4 |
| 13 | PR Prospective use: cutoff = the authenticated head; prior set = complete history through it | `cutoff` `:938-943` from `snapshot.head_sequence` / `head_digest`; `require_committed_pin=True` `:795` | PRESENT |
| 14 | PR Screen challenge: ≥ 2 retained members above `0.032898493715362` → not issued, Ed rules | threshold `:161`, limit `:167`, comparison `:723-726`, refusal `:842-847` | PRESENT, exact |
| 15 | PR Screen challenge, second diagnostic: new max vs `0.04262208300415633` (CG46 A-4) | `:164`, recorded `:1046-1049` | PRESENT, exact (A-4's corrected lexeme) |
| 16 | PR Analysis: Decimal statistics exactly as r6 (min, max, range, mean, sample SD; both two-draw predictions) | `_corpus_statistics` `:729-758`; key set matches r6's `source_statistics` (verified against `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`) | PRESENT |
| 17 | PR Analysis: the realized df's quantile proof is computed and recorded before issuance; no corpus issues on an unproven df | `build_quantile_proof` `:448-501`, called `:850` **before** the predictions `:853-854`; recorded `decimal_derivation.quantile_proof` `:1010` | PRESENT — but the **pass/fail bounds are invented**, §3 SF-5 |
| 18 | PR: `S = max(new range quantized 1e-6 ROUND_HALF_EVEN, 0.010818)` | `:862-866`, constants imported from `calibration_bracketing` | PRESENT |
| 19 | PR / CG46 A-3 / CG69 Q1: `C = max(predecessor ceiling, new Q99)` | `:872-874` | PRESENT (predecessor arm inert this generation — §4 F-3) |
| 20 | PR: strict `S < C`, refusal `successor_screen_exceeds_budget_ceiling`, never cured by lowering S | `:877-882` (`if not screen < ceiling`) | PRESENT, strict |
| 21 | PR: max budgetable drift = C, max budgetable excess = C − S, **no silent clamp at zero** | `:886-891` | PRESENT (unclamped; ordering makes a negative unreachable) |
| 22 | PR / CG46 V7: the row carries an explicit `d125_ruling`; issuance refuses while it is absent | pre-condition `:769-771`; row field `:983`; CLI deliberately not `required=True` `:1212-1214` | PRESENT |
| 23 | CG69 §11 A-2: `d125_ruling` joins the required-key set when the envelope row lands | S3 installed it conditionally: `calibration_bracketing.py:245` + `:466-470` require it for `floored_range_envelope_screen` | PRESENT (the seat's report `:194-197` under-claims this — it IS installed) |
| 24 | PR: the row records the **predecessor ceiling** (CG69 Q1 §2 rename from `inherited_ceiling_s`) | `predecessor_ceiling_s` `:981`, `predecessor_acceptance_id` `:982` | PRESENT, correctly named |
| 25 | CG69 §11 A-4: a non-None ceiling names the predecessor's acceptance id and is compared against **that registered row's** `operatives.maximum_budgetable_drift_s` | issuer reads the value from the **artifact**'s `ratified_operatives` (`:646-655`, `:873`); the row-vs-row comparison is S3's | PRESENT-by-seam (values coincide today; noted §4 F-4) |
| 26 | PR: preflight level screen = corpus maximum quantized to 1e-15 s | `:883-885`; validator recomputes `calibration_bracketing.py:1058-1062` | PRESENT |
| 27 | CG46 R-d S4 row (`:108`): "candidate bytes marked **not issued**" | `candidate_not_issued: True` `:1067`, `artifact_role: "candidate"` `:1068`, `issuance` block `:1069-1077`, `backfill_candidate.production_issuance_blocked` `:1136` | PRESENT (prose gap, §3 SF-8) |
| 28 | CG46 A6/A-7: generation-keyed completeness check "in the validator **and the issuer**" | issuer `:824-838` + `_select_members`; validator `calibration_bracketing.py:917-960` | PRESENT at both |
| 29 | PR: the target epoch is the registration's, unanimous, read before any value | `:814-822` | PRESENT |
| 30 | PR Prospective use: "D-102 clause 2 is preserved" (trigger judged under the prior artifact) | `prospective_rederivation.trigger_observation_rule` `:1085`; triggers derived from the emitted row `:1090-1092` via `rederivation_triggers` `:513-527` | PRESENT |
| 31 | Module/CLI prose describing what the tool is | module docstring `:1-7`, surfaced verbatim by `--help` | **DIVERGENT** — says "The prospective issuer is **reserved for S4**. This **read-only** watch…" §3 SF-7 |
| 32 | Member table shape as r6 (`source_directory` repo-relative) | `:717` stores `observation.custody_locator` (absolute); emitted `:953` | **DIVERGENT** — §3 SF-3 |

---

## 2. Answers to the five questions

**(1) Does the issuer encode rules the pre-registration does not state, or state them differently?**

Four, and only one is arithmetic:

- **Invented and operative:** `QUANTILE_PROOF_MAXIMUM_FORWARD_RESIDUAL = 1e-30` and
  `QUANTILE_PROOF_MINIMUM_AGREEMENT_DIGITS = 30` (`:184-186`). The PR states *that* a proof is
  required and that no corpus issues on an unproven df; it states **no bound**. These two numbers
  decide `quantile_proof_failed` (`:472-486`), i.e. they gate issuance. **The invention is
  conservative and is recorded in the artifact** (`forward_residual_bound`, `closed_form_agreement_bound`,
  `precision`, `closed_form_method` — `:490-499`): the published quantiles are quantized to 1e-20
  (`:487-489`, `:1006-1007`), so a 30-digit agreement bound is strictly tighter than anything the
  artifact publishes, and the realized values (~1e-80 residual, 56–57 digits per report 79 §B3) sit
  far inside. It is **not recorded anywhere a reader outside the code can find** — not in the PR,
  not in a decision-log entry. That is the defect, not the numbers. (§3 SF-5.)
- **Divergent:** the corpus-size floor departure (clause 9 above) — the PR names exactly one
  alternative floor, 17; the code admits any value ≤ 19 behind any non-empty `--ed-ruling` string.
- **Stated differently, benignly:** `--minimum-corpus-size` may not *exceed* 19 (`:779-780`) — the
  code forbids a *stricter* floor, which no authority asks for. Nit.
- **Screen-rule name (`:154-159`, `:868-871`): correct, and I verified the check it implies exists.**
  Registering `floored_range_envelope_screen` unconditionally — rather than by which arm of the `max`
  won — does **not** drop a check: `calibration_bracketing.py:1053-1054` verifies
  `max(quantized_range, D125_SCREEN_FLOOR_S) == screen` for that rule name, and `:245`/`:466-470`
  require `d125_ruling` for it. The seat's reasoning ("naming the rule by the realized branch would
  make the registered rule a function of the data") is the pre-registration's own logic and matches
  CG69's finding that the ceiling relation is a function of lineage, not of the screen rule.

**(2) Are the six recorded seat decisions within the seat's authority (rule 11: a seat may not amend
a ruled/pre-registered rule)?**

All six are **within authority**. None amends a ruled or pre-registered rule; each is forced by, or
subordinate to, production code the seat did not write:

1. *Two digests* — `derivation_sha256` must be `_canonical_sha256(artifact − that key)` because
   `calibration_bracketing.py` computes exactly that and compares; the curated seal is additive.
   Implementation choice. In authority.
2. *`decision_ids` follows the validator* — `calibration_bracketing.py:763` demands exactly
   `["D-102","D-109"]`; no authority states the artifact's `decision_ids`. The D-079/D-125/D-126
   provenance is preserved in `derivation_notes` (`:1044-1055`) and the machine-checked
   `d125_ruling`. In authority; the loss is recorded.
3. *`backfill_candidate` emitted, labelled* — the issued role requires the block; labelling it
   `candidate_not_issued` is truthful. In authority.
4. *A-7 enforced at the issuer too* — CG46 A6 ruled the check belongs "in the validator **and the
   issuer**". This is compliance, not invention.
5. *Machin π for the proof route* — implementation asymmetry inside an invented-but-conservative
   proof. In authority; see (1) for the bounds.
6. *Registration epoch resolved up front* — ordering choice that makes a refusal truthful. In
   authority.

The one decision that *would* have been out of authority if taken — renaming or re-scoping the
pre-registered screen rule — was not taken (see (1)).

**(3) Is the candidate's usable/unusable status stated in words a reader can act on, and does the
prose pass the first-use test?**

*Artifact:* mostly yes. `candidate_not_issued: true` (`:1067`), `artifact_role: "candidate"`,
`issuance.status = "candidate_not_issued"`, `claim_eligible: false`, and
`backfill_candidate.production_issuance_blocked: true` (`:1136`) are all present, and the `reason`
(`:1072-1076`) names who may issue and after what ("issuance is the D-138 transaction's, after the
cold science gate"). **What it licenses is nowhere stated in words** — the reader must infer
"nothing" from a false boolean. One sentence fixes it (§3 SF-8): *"These bytes license nothing: no
measurement window, no claim, no threshold. No tool may load them as authority; the production
loader refuses them by `artifact_role`."*

*Tool prose:* **fails the first-use test outright.** `--help` (executed this session) prints, above a
subcommand list that includes `prepare-candidate`:

> Inspect the active calibration epoch at the desk; never authorize capture. The **prospective
> issuer is reserved for S4.** This **read-only** watch authenticates the active issued artifact…

Two false statements in a tool that now writes a JSON artifact to `--out`. A reader acting on this
text concludes the file cannot write and the issuer does not exist. (§3 SF-7.)

*Contracts:* no `docs/contracts/*.md` in this tree mentions `prepare-candidate` at all (grep over
`docs/contracts/*.md`); the only prose is `docs/decision_log.md:6602-6604`, which is accurate except
that it repeats V5's "registration dry run" for `check` — a subcommand behaviour that does not exist
(§5 F-6).

**(4) The three open items — governing authority and what the D-138 transaction must do.**

1. **Absolute `source_directory`** (`:717`, `:953`). Governed by the **D-109 R2 corpus verification
   harness** and the reissue tool, not by the acceptance schema: both do
   `(repo_root / member["source_directory"]).resolve(strict=True)`
   (`tests/verify_calibration_acceptance_corpus.py:85`, `scripts/reissue_calibration_acceptance.py:173`).
   `pathlib` **discards** the left operand when the right is absolute, so an absolute locator
   verifies *silently* on this machine and fails `strict=True` on every other checkout, while the
   validator (`calibration_bracketing.py:825`, string type-check only) never says so. r6 stores
   repo-relative (`runs_window_a_20260722/instrument_validation/…`). **The D-138 transaction must
   relativise each locator against the repo root and refuse any member outside it** — a blocker for
   the ISSUED artifact, not for the candidate. Best fixed at the emission site now (`:717`), so the
   transaction inherits it rather than re-deriving it.
2. **Member sort untested** — governed by `calibration_bracketing.py:832`
   (`member_ids == sorted(member_ids)`). Delta 91 D22 reports this cut is killed by
   `test_only_the_candidate_label_stops_the_candidate_authenticating`; that report is UNVERIFIED by
   me (I ran no cuts, per brief). Contract-side the emission (`:947-957`) sorts, and the validator
   demands sorted, so the clause is satisfied. **No transaction action.**
3. **Inert predecessor arm** (`:874`). Governed by **CG69 Q1 §3** (the ratchet: "the ceiling in force
   … equals `max(predecessor ceiling, own Q99)`") and by the PR's `C = max(predecessor ceiling, new
   Q99)`. Confirmed inert by arithmetic: `S ≥ 0.010818 > 0.010164834757777545` (r6's ratified
   ceiling, read from the artifact this session), so strict `S < C` admits only when Q99 already won.
   **The transaction must not silently register a row whose ratchet term nothing verifies:** add a
   unit-level assertion on the ceiling arithmetic with a synthetic predecessor ceiling above Q99
   (bench-sized; no admissible CLI fixture exists this generation), because the term becomes
   load-bearing at r8 when the predecessor ceiling sits above the floor.

**(5) Ruled for the issuer with no code.** Two, plus one prose obligation — §5.

---

## 3. Findings, severity-tiered

### should_fix — must land before the FIRST `prepare-candidate` run

**SF-1 — No terminal-session guard: the pre-registered blindness fence has no code.**
`_registration_observations` (`:648-672`) validates only that each named session exists and is
`session_kind == derivation`. `CalibrationBracketSession` carries `state`
(`joulewise/calibration_ledger.py:491`; `"open"` at `:414`, `:4483`, `:4589`, `:4685`), and an open
derivation session is *by design* tolerated by every snapshot consumer as the physical/pin gap
(CG46 A7). So a run of `prepare-candidate` **during night 2 or night 3** loads, computes the full
Decimal statistics (`:758`), prints `corpus n` and, on any refusal path, prints the screen and the
ceiling (`:878-881`) and the screen-challenge count and threshold (`:844-846`).

> PR, Blindness: "No member value, screen, or statistic is examined by any person or agent before
> the third night's session is terminal and its pin candidate is emitted."
> PR, Stopping: "All three nights run all 12 declared slots regardless of interim values… No
> top-ups, retries, early stops, or outcome-driven extra nights."

Nothing else in the campaign enforces this: the guard is meant to sit exactly here. Cure: refuse
unless every `--registration-session-id` resolves to a session whose `state` is not `"open"`, naming
the open session. Four lines at `:660-666`.

**SF-2 — The corpus-size floor departure is unbounded.** `:773-778`:

```python
if minimum != SUCCESSOR_MINIMUM_CORPUS_SIZE and not args.ed_ruling:
    raise PrepareRefusal(...)
```

Any non-empty `--ed-ruling` string admits any `--minimum-corpus-size` ≤ 19 — 5, 3, 2 — and
`student_t_quantile` only refuses below df 1 (`:315-316`), so an n = 2 corpus emits.

> PR, Stopping: "Retained n >= 19 is REQUIRED for issuance… **Ed may instead rule in writing that
> n = 17 is acceptable**; nothing issues below 19 without that written ruling."
> PR, Analysis: "the degrees of freedom n-1 run from 18 to 35 — **or from 16** if Ed's written
> n = 17 ruling is exercised".

The pre-registration enumerates exactly one alternative. Cure: `minimum in (19, 17)` and refuse
otherwise, with the `--ed-ruling` requirement unchanged for 17. (CG46 A-2 is worded identically:
"Ed may instead rule in writing that n = 17 is acceptable".)

**SF-4 — A pending or unresolved prefix row is dropped where the pre-registration says refuse.**
`:920-930` filters the prior set with `if observation.content_id is not None`.

> PR, Prospective use: "its prior set is the complete history through it, including finalized
> observations of abort-closed sessions, and **a pending or unresolved attempt in that prefix
> refuses issuance**."

The system fails closed downstream — `_prior_set_matches_import_cutoff_prefix`
(`calibration_bracketing.py:1849-1856`) returns False on a prefix row with `content_id is None` or a
disposition outside `_LIVE_PREFIX_ADMITTED_DISPOSITIONS` — so no bad artifact can authenticate. But
the issuer prints `candidate written (NOT ISSUED)` and a corpus size, and the transaction discovers
the defect as an opaque validator refusal. Same argument the seat used for its own decision 4 (A-7
"refused at the issuer, not merely relied on in the validator"). Cure: refuse at `:920`, naming the
row.

### should_fix — must land before the D-138 transaction

**SF-3 — `source_directory` is the absolute custody locator.** `:717`
(`"source_directory": observation.custody_locator`) → `:953`. r6 stores repo-relative. Consumers
join against the repo root (`tests/verify_calibration_acceptance_corpus.py:85`,
`scripts/reissue_calibration_acceptance.py:173`) where `pathlib` silently discards the root for an
absolute right operand; the validator only type-checks (`calibration_bracketing.py:825`). Committing
an absolute machine-local path into `configs/calibration/` makes the issued artifact unverifiable on
any other checkout **while every check still passes on this one**. Cure at the emission site:
`Path(custody).resolve().relative_to(REPO_ROOT)`, refusing a member outside the repo.

**SF-5 — The quantile-proof bounds are invented and recorded only in code and output.** `:184-186`.
The PR (Analysis) requires a proof and forbids issuing on an unproven df, and states no bound. The
choice is conservative (30 digits ≫ the 20 published digits; realized 56–57 and ~1e-80) and the
bounds travel inside the artifact and inside `derivation_input_sha256` (`:1172`), which is the right
shape. Missing: any authority-side record. Cure (prose, bench-sized): one sentence in the
pre-registration's Analysis paragraph or in the D-138 transaction record naming both numbers and the
argument that each is tighter than the artifact's published precision. Rule 11 note: **the seat may
not add this to the pre-registration itself** — it is a magistrate/S6 edit.

**SF-6 — Ruled-not-installed: `check`'s registration dry-run.** See §5.

**SF-7 — The tool's own `--help` misdescribes the tool.** Module docstring `:1-7`, executed `--help`
above. "The prospective issuer is reserved for S4" is false (it is implemented in this file, `:760+`)
and "read-only" is false for `prepare-candidate` (`:768` writes `--out`). Cure: rewrite the docstring
to name both subcommands, say that `check` is read-only and `prepare-candidate` writes exactly one
file to a caller-named path, and state that neither authorizes capture nor issues anything.

**SF-8 — The candidate never says in words what it licenses.** `:1069-1077`. Add the licence
sentence (see §2(3)). One string; it changes `derivation_sha256` but not `derivation_input_sha256`
(prose is deliberately outside the seal, `:1157-1163`), which is exactly the property the seal was
built for.

### Nits

- **N-1** `two_draw_prediction_lexeme`'s docstring (`:508`) still says "shortest **repr**" while the
  sealed constant `TWO_DRAW_PREDICTION_RULE` (`:197-201`) correctly says "shortest round-tripping
  decimal". Same wording the previous round fixed in one place only. (Concurs with delta 91 N-a.)
- **N-2** `:779-780` refuses `--minimum-corpus-size` **above** 19. No authority asks the tool to
  forbid a stricter floor.
- **N-3** `--d125-ruling` and `--ed-ruling` accept any non-empty string. Presence-only is exactly
  what V7 and A-2 ask for ("refuses **while it is absent**"), so this is not a defect — but the two
  strings are the only human-authority evidence in the artifact, and the transaction's cold science
  gate should read them, not just check they exist.

---

## 4. Verified-correct items a later lens need not re-open

- **F-1** The screen-rule name and its check agree: `floored_range_envelope_screen` (`:871`) is
  checked by `calibration_bracketing.py:1053-1054` as `max(quantized_range, floor) == screen`, and
  `:245`/`:466-470` make `d125_ruling` mandatory for that name. The seat's open note that
  `d125_ruling` "is not yet in `_GENERATION_ROW_REQUIRED_KEYS`" (report 79 `:194-197`) is **stale** —
  CG69 A-2 is installed, conditionally and correctly.
- **F-2** Screen-challenge constants match the pre-registration lexeme-for-lexeme, including A-4's
  corrected `0.04262208300415633` (`:164`), and r6's own `preflight_level_screen_s`
  (`0.032898493715362`) and ratified ceiling (`0.010164834757777545`) read this session from
  `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` confirm both anchors.
- **F-3** The inert predecessor arm is inert by arithmetic, not by luck (§2(4) item 3); it produces
  no wrong number this generation.
- **F-4** The predecessor ceiling is read from the predecessor **artifact** (`:646-655`), while CG69
  A-4 keys the validator's comparison to the registered **row**. Today `_D102_N17_DERIVATION` and
  r6's `ratified_operatives` carry the same lexeme, so the seam is closed; if a future generation
  can be issued whose row and artifact could disagree, the issuer should read the row.
- **F-5** `derivation_sha256` is the production recipe (`:1128-1139`) and the curated
  `derivation_input_sha256` (`:1141-1185`) seals the member lexemes, statistics, rounding rules,
  quantile proof, operatives, epoch, cutoff, predecessor identity and ceiling, and `d125_ruling` —
  it is computed **before** the whole-artifact digest closes over it (`:1124-1126`), which is the
  correct order.
- **F-6** `decision_ids` (`:1064`), the trigger set (`:513-527`, `:1090-1092`), the inventory over
  all three dispositions including zeros (`:931-937`), the plain-notation quanta (`:504-507`), and
  the sorted member table (`:947-957`) each match a production clause I read in
  `calibration_bracketing.py` this session (`:763`, `:781-787`, `:869-884` per report, `:832`).
- **F-7** The anchor-v3 *wording* divergence (clause 8) is prose, not science: CG46 R-d `:112`
  settles that a fresh v3 capture stores its own value and that the D-138 transaction sets
  `stored_lexeme_is_member_value: True` in
  `tests/verify_calibration_acceptance_corpus.py`. The issuer additionally authenticates both bundle
  hashes against the ledger row (`:592-607`) and refuses a stored lexeme that disagrees with the
  row's `exact_bound_lexeme_s` (`:717-722`), which is the stronger fence for a stored value.
  **Cure is wording, in two places:** `derivation_corpus.selection` (`:1140-1143`) and the PR
  glossary's "Anchor-v3 replay" definition should say the *recorded* anchor-v3 outcome,
  hash-authenticated, rather than a re-derivation — otherwise the paper-facing record claims a
  computation nobody performed. **The PR edit is S6's/the magistrate's, not this seat's (rule 11).**

---

## 5. Ruled for the issuer, no code (ruled-not-installed)

**F-6 (should_fix) — `check`'s registration dry-run.**
> CG46 V5 (`10-coldgate-fable-ruling.md:39`): "One tracked issuer
> `scripts/issue_calibration_acceptance_generation.py` with subcommands `check` (**desk epoch watch
> and registration dry-run**) and `prepare-candidate`."
> `docs/decision_log.md:6603` (this tree) repeats it: "`check` (desk epoch watch **plus registration
> dry run**)".

`check` (`:99-148`) does the epoch watch only; its parser (`:1180-1183`) takes `--ledger`,
`--head-pin`, `--acceptance` and nothing registration-shaped. Either the dry-run lands (the obvious
shape: `prepare-candidate` minus the `--out` write, reporting retained n, exclusions and the two
diagnostics — **which SF-1's blindness guard must also cover**), or the ruled text is amended.
**A seat may not amend it** (rule 11); this routes to the magistrate.

**F-7 (should_fix, prose) — the anchor-v3 replay wording**, §4 F-7. Ruled science is installed; the
ruled *description* is not what the code does.

**Not found missing:** every other clause of CG46 §A3/V5/V7 and its A-2/A-3/A-4/A-7, and of CG69 §10
and its A-1/A-2/A-4 that names the issuer, has a code site in the table above. In particular A-3's
`successor_screen_exceeds_budget_ceiling` refusal — recorded by the addendum as "absent from code
today" and assigned to S4 — **is installed** at `:877-882` with the strict inequality.

---

## 6. Scope and honesty

Executed: reads, greps, and `--help`. **NOT EXECUTED:** the test suite, any mutation cut, any CLI
run against a fixture ledger (a delta refuter is cutting in this worktree). Every claim above about
the *tests* — including that D22 kills the member sort — is relayed from reports 79/81/91 and is
UNVERIFIED by me; every claim about *code and artifacts* was read this session at the cited line.
No file was edited, no git state changed, nothing written outside `/tmp`.
