# 60 — Seat S6 (Claude Opus, resumed after the Astra seat died on the Codex usage limit)

Worktree `/Users/edr/code/JouleWise-wt-s6-docs-prereg`, branch
`feat/2026-09-10-epoch-s6-docs-prereg`. WIP commit `64d1d6d3` reviewed clause
by clause against cold-gate ruling 46 §R-c/§R-d row S6/§R-e and dated addendum
11 (A-2, A-3, A-4, A-7, A-8), then completed and corrected. Nothing committed;
all four files are left modified in the working tree. No file outside
WRITE_SCOPE was touched; `tests/test_docs_freshness.py` needed no change (see
"scope" below).

## Verdict on the WIP

The Astra WIP was substantively right on every AMENDED clause the brief named:
three nights x 12 slots, retained n >= 19 required with Ed's written n = 17
alternative, the full D-125 envelope for both S and C, the Decimal threshold
`0.04262208300415633`, the estimator-code rotation clause, both STATUS labels,
the two-part D-102 addendum with the step-0 desk watch marked PROPOSED, and no
PR-number literal anywhere. Nothing had to be reversed. What it lacked was
mechanism: the text asserted the ruled rules without building them, which is
exactly the class of defect Ed's writing standard targets. Defects found:

**Substantive gaps (clause list)**

1. **A-8 second half missing entirely.** The confirmed gap that the
   `/usr/bin/powermetrics` binary hash is NOT one of the six identity-epoch
   fields — so a binary rotation alone would not stale the artifact through
   the epoch check — was absent, as was its ruled disposition ("the desk watch
   covers the binary; no contract change now"). Added to the addendum's
   triggering-facts paragraph.
2. **V5 tooling unnamed.** The addendum said "the desk epoch-watch tool" but
   never named `scripts/issue_calibration_acceptance_generation.py` (`check`,
   `prepare-candidate`), the `--session-kind/--slot-count` extension of
   `scripts/reserve_calibration_window_bracket.py`, or what the watch compares
   (`kern.osversion`, `hw.model`, powermetrics hash, MLX version against the
   artifact's epoch and the last row's T1 vector). Added.
3. **A-8 first half (custody) missing**, and, when I added it, the obvious
   phrasing was wrong: A-8's "bootstrap rows live in the anti-withholding
   universe forever" describes today's code, but V1's derivation-kind skip
   removes them from `registered_valid`. I state the custody obligation on the
   ground that survives the skip — after issuance the successor's prior set
   must keep equalling the ledger prefix at its cutoff, so the rows must stay
   present and authenticable — plus the ruled pinned-and-backed-up custody
   manifest. Flagged below as the one place a refuter should look.
4. **No worked numbers anywhere.** Added the arithmetic that forces each
   default: two nights project 24 x (30/38) x (17/19) = 16.95 retained vs the
   required 19, three project 25.4; the 600 s settle + 11 x 600 s + ~8 min
   capture = 128 of 210 min; and, for A-3, r6's own ceiling
   `0.010164834757777545` sitting BELOW the `0.010818` screen floor, which is
   why the C half of the envelope is not optional.
5. **The V7 refusal was ungrounded.** "refuses `successor_screen_exceeds_
   budget_ceiling` when S >= C" and "cap is C - S, never a silent clamp" are
   correct but were unattributed; verified this session against D-126 clause 3
   ("issuance refuses ... when screen >= ceiling; cap = ceiling - screen with
   no max(0,.)") and now cited there.
6. **"Inherited ceiling" and "Q99" did unpaid work** in both the addendum and
   the pre-registration. Now built: the predecessor generation's
   `maximum_budgetable_drift_s`, and the new corpus's 99 % two-draw
   prediction.
7. **Stopping rule left a hole.** The WIP dropped ruling 46's "one further
   identical night is scheduled" (correct under A-2's stop-at-three) but put
   nothing in its place, leaving a shortfall unadjudicated. Now: "any further
   capture is Ed's written ruling, not this registration's".
8. **Duplicate estimator-code clause.** It appeared in both Epoch and
   Exclusions in the fenced text; nit N3 places it beside the MLX/powermetrics
   clause, so the Exclusions copy is removed.
9. **Misplaced V3 acknowledgment sentence** sat mid-"Sample" paragraph inside
   the fence; it belongs to the status labels and now appears there only.
10. **`prior_prefix_mode` mechanics asserted, not built.** "a mixed prefix
    does not use the historical two-receipts-per-observation shortcut" (with a
    line-break artifact splitting the hyphenated term) never said why. Now:
    an all-import prefix holds exactly a reservation and a finalization per
    observation, so its cutoff sequence is twice its count; a prefix also
    holding a session's open and closing receipts breaks that arithmetic, so
    `prior_observation_count` and `cutoff_sequence` are registered per
    generation (genesis registers 38 and 76), as is `epoch_catalog_ids`.
11. **The endpoint barrier had no forcing problem.** "Both discovery and the
    registered-valid universe skip derivation-kind sessions" now says what
    that universe is, that a caller's candidate set must equal it exactly or
    evaluation refuses `calibration_ledger_off_ledger_artifact` (the
    anti-withholding equality, verified at
    `joulewise/calibration_bracketing.py:1597-1625` this session), and why a
    one-site skip is a defect.
12. **`DIAGNOSTIC_NO_PACK` C-codes unglossed** in the fiducial contract ("C1
    and C3-C5 still apply" is unreadable without the legend). Now glossed from
    `docs/contracts/pack_night_go_receipt.md:42`: C1 purpose-bound transaction
    authorization, C2 verified pack ARM ceremony (the only
    `NOT_APPLICABLE`/`no_pack_by_design` row), C3 quiet-machine census, C4
    boot/clock validity, C5 no-retry bound.
13. **No terms section in the pre-registration.** The fenced text uses
    session, slot, head pin, prior set, corpus, derivation-only, level screen,
    bracket screen, retained n without building any of them. Added a "Why this
    registration exists" forcing-problem section and a "Terms used below"
    glossary outside the fence, so the fenced registration text stays
    ruling-shaped while the file passes the first-use test.
14. **Fiducial mode text was one 20-line block** with no heading, reading as
    part of the T1-T3 transfer assumptions. Now its own section,
    "Derivation-only capture for a new identity epoch", which also gives the
    ledger contract's cross-link a real anchor.

## What the four files now say

- `docs/contracts/calibration_ledger.md` — new section "Derivation sessions
  and epoch bootstrap" (terms; forcing problem; why one session rather than
  repeated standalone reservations, built from `RESERVATION_HEAD_MISMATCH` and
  the two-receipts-per-observation head arithmetic; the two session kinds and
  the derivation session's open/order/close/abort rules; claim consumers
  refusing for the duration by design; the endpoint barrier and its two
  sites). Historical-import consumption is now generation-keyed:
  `prior_prefix_mode` `import_only` vs `import_plus_live`, the registered
  counts, and the purity + completeness membership fence with
  `derivation_notes.excluded_members`, `affine_clock_fit_empty`, and the
  content-ID-from-two-hashes match rule (A-7). The issued-artifact section is
  scoped to the genesis generation without changing any pinned value.
- `docs/contracts/powermetrics_fiducial.md` — the `--derivation-only` mode:
  what it still authenticates (bytes, protocol digest, estimator-code digest),
  the one inverted test (epoch MUST differ; a match refuses because ordinary
  capture is then possible), the derivation-kind slot requirement, the
  `derivation_only`/`screen_basis` hashed provenance, the
  `preflight_systematic_screen_s = None` classification collapse on every
  finalization path including recovery (A-1), the diagnostic-only prior level
  screen feeding the screen challenge, the night-class conditions, and the
  closing "licenses nothing" clause.
- `docs/decision_log.md` — one dated `### Addendum 2026-09-10` at the end of
  D-102's body (182 added lines, zero deletions, no index row and no other
  decision touched), with MECHANISM and SCIENTIFIC DEFAULTS halves.
- `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` — rewritten:
  status header, authority, forcing problem, terms, the three-night arithmetic
  outside the fence; the amended §R-c text inside the fence; a closing note on
  which bracketed fields are filled at commit and that filling them reopens no
  rule.

## Verification

`python3 -m unittest tests.test_docs_freshness` with the rc captured in a
variable:

```
RC=0
Ran 31 tests in 0.688s

OK
```

Also run, because they read `docs/decision_log.md`:
`python3 -m unittest tests.test_gen_state tests.test_claims_lint
tests.test_identity_pins tests.test_d078_reason_registry` -> `RC=0`, 129 tests
OK. Grep confirms no `PR #`, `pull/`, or PR-number literal in any of the four
files, and no surviving `0.042622083004156326`.

## Scope note

`tests/test_docs_freshness.py` was in WRITE_SCOPE conditionally ("if it pins
any of these documents' sections or forbids volatile literals you must
write"). It does not: `_current_sections()` covers only `README.md`,
`PROJECT_STATUS.md` and two `docs/orchestration.md` regions, and the only
contract it pins is `docs/contracts/bridge_protocol.md`. The decision-log
checks it does run (`_decision_body_ids`, index rows, dangling `D-nnn`
references across `docs/**/*.md`) all pass unmodified. No edit made.

## Needs a ruling / for the refuters

1. **Label punctuation.** Addendum 11 A-8 and brief 49 write the label
   "adopted by cold gate 46, Ed veto window open" (comma); the seat's dispatch
   message quotes it with a semicolon. I used the comma form from the ruling
   documents in both halves of the D-102 addendum. The fenced pre-registration
   STATUS line uses the semicolons of the brief's verbatim string. If a
   reviewer greps for the semicolon variant in the decision log it will miss.
2. **The custody rationale (item 3 above).** A-8 grounds permanent custody on
   bootstrap rows living in the anti-withholding universe forever, which is
   true of today's code but not after V1's derivation-kind skip lands. I
   substituted the prior-set-prefix-equality ground, which survives the skip.
   If the cold gate intended the literal A-8 wording, the contract sentence
   and the addendum sentence both need re-ruling together.
3. **No fourth night is authorized.** A-2 stops at three nights regardless of
   interim values but does not say what happens on a shortfall; I wrote that
   any further capture is Ed's written ruling. That is an inference from R-e
   ("may not select scientific rules after seeing data"), not a ruled clause.
4. **`--slot-count 12` is not fixed here.** The pre-registration declares 12
   slots per night; seat S2's declared-slot list is what enforces it. If S2
   lands a different slot-list shape, the bracketed `[SEQ]`/`[DIGEST]` fill
   step is the last chance to reconcile.

---

## Fix round 1 (contract refuter: MERGEABLE AFTER FIXES)

Applied on top of `3c60f0ec` in the same worktree; nothing committed. All six
required fixes applied, plus two of the three optional nits. Line numbers are
post-fix.

1. **Status lines on both new contract sections, following the `Status:`
   convention at `docs/contracts/pack_night_go_receipt.md:3`.**
   - `docs/contracts/calibration_ledger.md:19-26` — "Ruled by cold gate 46 and
     its dated addendum 11 (2026-09-10); NOT YET LANDED", naming seats S1-S4
     and stating what the shipped code actually does today (`bracket`-kind
     sessions only; the import-only prefix fence for every generation). The
     generation-keyed clauses live in a different section, so
     `calibration_ledger.md:155-157` carries an inline "(ruled 2026-09-10, not
     yet landed; see ...)" pointing back to it.
   - `docs/contracts/powermetrics_fiducial.md:95-99` — same status, naming
     seat S1 and seat S2's session interface, and stating that no shipped
     writer accepts the flag and no shipped ledger offers the slot.
   - **Cutoff drift fixed:** `calibration_ledger.md:149-152` now says the
     prior set must equal the prefix "at the cutoff the artifact itself
     declares in `ledger_cutoff`"; `:167-172` says the two registered numbers
     (`prior_observation_count`, `cutoff_sequence`) are EXPECTED values that
     the artifact's declaration must agree with, not the cutoff itself. The
     same drift at `:383-385` is corrected to "declares a `ledger_cutoff` at
     the authenticated head after its last derivation row".
2. **Degrees of freedom** — `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:129-132`.
   "proven for both df 18 and df 19" is replaced by the range the schedule
   actually produces: retained n from 19 (the required floor) to 36 (all
   declared slots retained), so df = n-1 runs 18 to 35; the quantile
   implementation's proof for the REALIZED df is computed and recorded before
   issuance, and no corpus issues on a df absent from that record.
3. **Named halt for `S >= C`** — pre-registration `:139-142`, its own clause in
   Analysis with the same shape as the screen challenge: if the new Q99 is at
   or below the `0.010818` screen floor, the inherited ceiling
   `0.010164834757777545` cannot rescue `C > S`, D-126 clause 3's
   `successor_screen_exceeds_budget_ceiling` fires, the corpus is not issued,
   and Ed rules in writing before any further capture. Explicitly: the refusal
   is never cured by lowering S.
4. **`anchor-v3 replay`, `b_fiducial_s`, `DIAGNOSTIC_NO_PACK` built at first
   use** — added to the Terms block at pre-registration `:49-58`, ahead of the
   Membership clause that uses them (replay resolution and the no-exclusion-on-
   `b_fiducial_s` rule) and of the Sample clause that names the night class.
   `DIAGNOSTIC_NO_PACK` is glossed as the class for a night running no
   measurement pack: registration path required, only the pack ARM condition
   (C2) not-applicable, the other four still required to pass.
5. **"Level screen" built at first use** — `powermetrics_fiducial.md:120-125`,
   inline at the first mention (`preflight_level_screen_s` inside
   `screen_basis`): "the **level screen**, that acceptance's corpus maximum,
   the threshold one observation's bound is judged against".
6. **"Bootstrap" disambiguated in `calibration_ledger.md`.** The word now
   means only the historical-import CLI sense it already had (`:197`, `:232`,
   `:251`, `:281`, `### Bootstrap CLI` at `:390`, and the function name
   `bootstrap_historical_import`). Every new-section use is renamed: heading
   `:17` "Derivation sessions for a new identity epoch" (with both anchor
   links updated — `calibration_ledger.md:156` and
   `powermetrics_fiducial.md:117`), `:43` "that new-epoch corpus", `:87`
   "**Derivation rows are non-claim-bearing...**", `:99` "Derivation rows are
   also a permanent obligation", `:114` "A new identity epoch is served
   instead by the live derivation sessions ... never by a second historical
   import", `:383` and `:386` "its last derivation row" / "its derivation
   rows". `powermetrics_fiducial.md:125` likewise says "every derivation row".

Optional nits: **taken** — the recovery path's `slot == "pre"` auto-abort is
now stated not to apply to a derivation session
(`powermetrics_fiducial.md:138-141`, A-1); and "present and authenticable" is
softened to what the prefix matcher actually compares
(`calibration_ledger.md:99-103`: the attempt ID, content ID, classification
disposition, and epoch). **Not taken** — the canonical comma-form STATUS
string: the decision-log addendum already uses the comma form on both halves
(`docs/decision_log.md:6534`, `:6616`), but the pre-registration's two STATUS
lines (`:3` and the fenced `:65`) are the brief's verbatim strings, which are
semicolon-separated lists rather than the label phrase. Changing them would
break the literal string brief 49 specified; flagging rather than deviating.

Verification, rc captured in a variable:

```
$ python3 -m unittest tests.test_docs_freshness tests.test_gen_state; rc=$?
Ran 75 tests in 2.308s

OK
RC=0
```

Working tree after the fix round (nothing committed):
`configs/calibration/preregistration_d079_epoch_25g83_rev1.md`,
`docs/contracts/calibration_ledger.md`,
`docs/contracts/powermetrics_fiducial.md` modified against `3c60f0ec`
(+87/-46); `docs/decision_log.md` unchanged this round.

---

## Fix round 2 (seat S3 contract refuter, F4: the fifth per-row binding)

Applied on top of `921c1102`; only `docs/contracts/calibration_ledger.md`
changed (+33/-15), nothing committed. Line numbers are post-fix.

1. **Row shape defined with the four bindings named as the `import_only`
   shape** — `:149-156`. The prior-set row now explicitly "carries four
   per-row bindings — attempt ID, content ID, classification disposition, and
   identity epoch — and a generation registered `import_only` refuses a row
   carrying any fifth key". That makes the historical shape exact rather than
   merely listed, so the addition below cannot be read back onto r3-r6.
2. **The fifth binding, scoped to `import_plus_live`** — new paragraph at
   `:170-182`, immediately after the per-generation `prior_prefix_mode`
   paragraph and before the registered-counts paragraph. It states: the row
   carries `session_id`, compared against the ledger row's
   `bracket_session_id`, and the session it names must be derivation-kind.
   Reason given, in the terms the section already built: the purity and
   completeness checks range over "rows of this registration", so without the
   binding the artifact would be the only thing saying which rows those are —
   it could name a convenient subset or disown a row the ledger recorded, and
   the check would be judging the artifact against the artifact's own claim.
   Binding each row to the ledger's recorded session is what keeps D-102
   clause 2's rule (nothing judges itself) true of registration membership and
   not only of thresholds. Closes with the no-historical-change clause
   (`import_only` keeps the four-key shape and refuses a `session_id` key) and
   the status marker "(Ruled 2026-09-10, not yet landed; seats S3 and S4
   install it.)", consistent with the section status line at `:19-26` and the
   inline marker at `:158-160`.
3. **Issued-artifact check 4 carries the fifth binding** — `:377-387`: "...
   and identity epoch, plus, for a generation registered `import_plus_live`,
   the row's `session_id` against the ledger row's `bracket_session_id`".
4. **Derivation-section permanence clause updated** — `:99-103` now lists the
   five fields the prefix matcher compares (attempt ID, content ID,
   classification disposition, epoch, session ID), so the obligation stated
   there matches the row shape defined below it.
5. **Residual cutoff drift from round 1 cleared** — check 4 at `:378` said
   "the cutoff registered for that generation"; it now says "the artifact's
   declared `ledger_cutoff`", matching the correction already made at `:150`
   and `:167-172`.

Verification, rc captured in a variable:

```
$ python3 -m unittest tests.test_docs_freshness tests.test_gen_state; rc=$?
Ran 75 tests in 2.334s

OK
RC=0
```

Nothing else changed: `docs/decision_log.md`,
`docs/contracts/powermetrics_fiducial.md`, and the pre-registration are
untouched this round. The pre-registration's Membership clause says a member
"belongs to a session of this registration", which the new binding is the
mechanism for; no wording change was needed there, but a refuter wanting the
`session_id` field named in the registration text should say so.
