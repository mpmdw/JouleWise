# WAVE-1 integration — Opus counter-review (gate ledger row 6)

Seat: Opus counter-review, read-only except this file.
Tree: `/Users/edr/code/JouleWise-wt-int-fan-wave1`, branch `int/2026-09-04-fan-wave-1`, HEAD `7eed7c5f`.
Diff under review: `git diff origin/main..HEAD` — 33 files, twelve fan-out landings.
Lens: what the twelve Sol execution refuters did NOT test. Each finding below
carries evidence I read or ran in this session.

## VERDICT

**LANDABLE.**

- Blockers: **0**
- Should-fix: **3** (F-1, F-2, F-3) — none blocks the merge; F-2 must be
  discharged by the magistrate in the same wave.
- Nits: **3** (F-4, F-5, F-6)

The five claim-bearing surfaces in this wave are enumerated below. I recomputed
both changed digests myself and confirmed each is bound by an automated test.
Both changed evidence fences move in the fail-closed direction, and I verified
the tightened one against the nine real corpora on disk rather than against
fixtures. No landing amends an operative process rule, doctrine, or skill.

---

## 1. Claim-bearing surfaces

A **physics/evidence fence** here means a check whose failure would let an
unsound measurement or an unauthenticated artifact be treated as sound —
D-161 requires those to fail closed. An **operator-convenience surface** is one
whose failure costs time, not soundness.

### CB-1 — `scripts/setup_quiet_guard.sh:14`, `QUIET_GUARD_PROCESS_SHA256`

Changed `5ac34ec9f1873858957d4d26fee87332053749576006b3c6e4d1db43e865b4ef`
→ `6742eec0a7a6e2f487f182a2e9ec0d675e6af57ba42f5a308076ab75eb938674`
(QUIET-GUARD-01).

*Landing's justification:* the same landing edits
`joulewise/quiet_guard_process.py`, so the installed-helper pin must move with
the file it authenticates.

*D-161 class:* **physics/evidence fence, fail-closed.** The pin is what proves
the privileged helper installed on the quiet host is the reviewed code.

*What I verified:* `shasum -a 256 joulewise/quiet_guard_process.py` returns
exactly the new pin. The other two pins (`QUIET_GUARD_SHA256`,
`QUIET_GUARD_PRIVILEGED_SHA256`) are unchanged and `joulewise/quiet_guard.py`
still hashes to `09aa9c1f…`, so no stale pin was left behind. The pin is not
free-floating: `tests/test_quiet_guard.py:1669-1672` maps the shell constant to
the repository file, and the module is green (87/87). Correct.

### CB-2 — `joulewise/quiet_guard_process.py:321-328`, `revalidate_identity` semantics

A candidate whose start-time anchor is unchanged but whose executable, argv, or
ancestry differs now returns `Revalidation.UNOBSERVABLE` instead of
`Revalidation.PID_REUSED` (QUIET-GUARD-01).

*Landing's justification:* PID reuse is established only by the start-time
anchor; disagreement without an anchor change is an observation race, not proof
of reuse.

*D-161 class:* **physics/evidence fence.** A relabelling here could in
principle soften a refusal.

*What I verified:* I read the sole consumer,
`joulewise/quiet_guard.py:1066-1074`. Both verdicts set a nonempty `cause`, and
both fall through to the same `_write_transition(target="recovery_required")`;
UNOBSERVABLE in fact takes *precedence* over `pid_reuse_detected` in the cause
ladder. Closure behaviour is therefore identical — the change only makes the
recorded evidence label honest. I also checked for the classic missed-call-site
signature and found the opposite: the second, independent determination at
`joulewise/quiet_guard.py:1128-1141` was *already* correct, raising
`GuardError("process_observation_unavailable")` for exactly this case. This
landing brings the two sites into agreement rather than diverging them. The new
contract-level test (`tests/test_quiet_guard.py:739-754`) goes through
`audit_registry`, not the private helper, and the pre-existing different-start-
time → `pid_reused` test at `:736` is retained.

### CB-3 — `joulewise/arm_readiness.py:2980-2983` and `:3009-3032`, historical pre-authoring custody gate

New `_HISTSEM_PROJECTION_FREEZE_PATH_PATTERN` makes any pack entry under
`identity_pin_projection.receipts/` that is not exactly
`projection-NNNN.{json,sha256}` count as authoring custody, so the coordinate is
refused at the histsem gate instead of being left to the later identity
membrane (PINSET-GRAMMAR-EXCLUSION-01).

*Landing's justification:* the receipts directory is a governed namespace; a
non-conforming entry there cannot be proven not to be a successor.

*D-161 class:* **physics/evidence fence, fail-closed.** Strictly tightening —
it can only refuse more coordinates, never admit more.

*What I verified:* the risk in a tightening change is over-refusal of existing
lawful evidence, which fixtures will not reveal. I enumerated the real
artifacts on disk: nine campaigns under `configs/campaigns/d117_*/` each hold
exactly `identity_pin_projection.receipts/projection-0001.json` and
`…/projection-0001.sha256`. Both match the new grammar, so no existing lawful
coordinate is newly refused. I also confirmed the path shape the gate assumes
is real: `_historical_pack_tree` (`joulewise/arm_readiness.py:3095`, strip at
`:3161`) returns pack-relative paths with the pack prefix removed, so
`parts[0] == "identity_pin_projection.receipts"` is the right test.
`tests.test_receipt_histsem.PreAuthoringProjectionCustodyTests` — 8/8 OK.

### CB-4 — `docs/process/coldgate_charter_registry.md:20-37`, pre-registered candidate digest

New registry section "Candidate charter v3 (not operative)" recording
`docs/process/coldgate_charter_v3_candidate.md` at sha256
`9275316e46c6c7bf084e35caa927dae9727dd544dae72656bed22ba82d22b977`
(CHARTER-V3-PACKET-INPUTS-01).

*Landing's justification:* the magistrate ruled the candidate digest goes to Ed
by email for re-ratification and is not operative until then.

*D-161 class:* **evidence fence, correctly fail-closed.** The registry is the
trust anchor a cold judge reads at launch.

*What I verified:* `shasum -a 256 docs/process/coldgate_charter_v3_candidate.md`
returns exactly the recorded digest. The operative table is untouched and still
binds v2 at `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`.
The status cell reads "CANDIDATE — NOT OPERATIVE; AWAITING ED RE-RATIFICATION",
and the section spells out that the candidate must not be supplied to a cold
judge as the operative charter. This matches the ruling exactly. The guard is
not a copied literal: `tests/test_coldgate_charter_v3.py:54-70` recomputes both
digests from the files at test time (so they cannot drift), asserts the
not-operative status string, and `:77-78`/`:85-86` supply negative cases that
prove the assertions can fail.

### CB-5 — `docs/paper/round7/fill-checklist.md:36-40`, paper-facing capability claim

The line "Prose placement … is not covered by R7F until kernel row
`R7F-DX-PROSE-SCAN-01` closes" is replaced with "R7F now scans the
diagnostic-value (DX) prose region …" (R7F-DX-PROSE-SCAN-01).

*D-161 class:* **operator-convenience / paper-process surface** — it describes
what a checker does, and no measured quantity depends on it. But it is a
docs-describe-behaviour claim, and see F-1.

### Not a claim-bearing surface

`joulewise/coldgate_receipt.py` (CGV-HARDEN-01) is 211 new lines but is
**unwired**: I grepped the whole tree and the only importers are
`tests/test_coldgate_receipt.py` and a mention in `docs/designs/cgv_harden_01.md`.
That is precisely the magistrate ruling ("keep the receipt-persistence
primitive; wire it into the convening runner when COLDGATE-HANDOFF-01 lands").
No receipt is written by any production path in this wave.

---

## 2. Findings

### F-1 — should_fix — the fence the checklist now promises is dormant on the real artifact and has never met one

`docs/paper/round7/fill-checklist.md:36-40` now states, in the present tense,
that "R7F now scans the diagnostic-value (DX) prose region, from the mandatory
standing sentence to the next Markdown heading."

I ran the landed checker against the real inputs in this tree:
`_dx_prose_regions(docs/paper/draft-v2-skeleton.md)` yields **0 regions** and
`check_prose_literals` yields **0 comparisons**. The reason is legitimate:
`DX_STANDING_SENTENCE_HEAD` (`scripts/check_paper_round7_artifacts.py:136`)
occurs **0 times** in `docs/paper/draft-v2-skeleton.md`, and the skeleton
contains **0** `[FILL:DX-` markers — the DX rows are simply not placed yet. So
this is not a defect and not a blocker.

What it does mean is that the fence has only ever been exercised against
synthetic input. All three new tests
(`tests/test_paper_round7_artifacts.py:811-864`) construct their skeleton with
`_complete_dx_region`, which emits the standing sentence itself.

**Counterfactual:** let the head literal at `:136` — note it begins with a curly
quote `“` — drift from whatever the fill procedure actually writes at placement
time. `_dx_prose_regions` returns nothing, `check_prose_literals` returns
nothing, R7F reports PASS having scanned no prose, and the checklist sentence is
false at the exact moment it matters. Nothing in the wave would catch that,
because the fixture supplies the literal to itself.

**Ask:** either bind the checklist sentence to a check that the standing
sentence literal is the one the fill emits, or restate the sentence as
dormant-until-DX-placement so a reader is not told a scan is running when it is
not.

### F-2 — should_fix — twelve missions land and zero kernel rows close; two rulings carry unexecuted implementation clauses

I read `docs/process/state_kernel.json` at HEAD. Every mission row in this wave
is still `queued`: `R7F-DX-PROSE-SCAN-01`, `QUIET-GUARD-01`,
`PINSET-GRAMMAR-EXCLUSION-01`, `CGV-HARDEN-01`, `CHARTER-V3-PACKET-INPUTS-01`,
`NODE-CUSTODY-DEFAULT-01`, `DG071-PROVENANCE-TEST-01`,
`MIDCAMPAIGN-CURE-GENERATION-01`, `CALEXITS-EVIDENCE-BYTES-01`,
`CALEXITS-HYGIENE-FIXES-01`. `PREWINDOW-REGEX-01`, `P2-027`, `P2-035`,
`P2-047A` and `P2-050` are absent from `tasks` entirely.

Two magistrate rulings in
`docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md` carry
implementation clauses that nothing on this branch executes:

- p2-rows: "Retire P2-027, P2-035, P2-047A, P2-050 as the seat recommends."
  The p2-rows landing is report-only, and its own report is explicit and
  correct about why (flag F1: "this session did not edit that registry"; the
  seat deliberately left `state_kernel.json`, `TASK_QUEUE.md`, `RUN_STATE.md`
  and `docs/decision_log.md` alone). The retirement is magistrate-owned work
  that has not happened.
- QUIET-GUARD-01: "kernel row wording reconciled." No kernel file changed.

NODE-CUSTODY-DEFAULT-01 is also report-only, but that is correct: its report
returns `acceptance: needs_ruling` with a blocking flag, and the magistrate's
ruling adopts the recommendation as a *design* decision, not an instruction to
land code in this wave.

**Counterfactual:** merge as-is. The rulings are then recorded as discharged by
a landing, while `state_kernel.json` still carries P2-027, P2-035, P2-047A and
P2-050 as live rows and every mission row as `queued`. That is the
ruled-not-installed signature exactly — a ruling with an implementation clause
that never reaches the artifact it governs. It also makes F-1 worse: the
fill-checklist asserts a capability whose kernel row is open.

**Ask:** the magistrate applies the kernel amendments in this same merge wave.
This is not seat work — the protected-state files are magistrate-owned and both
seats were right to leave them.

### F-3 — should_fix — a governed-namespace grammar now has two unsynchronized definitions

`joulewise/arm_readiness.py:2980-2983` introduces the projection freeze grammar
as `identity_pin_projection\.receipts/projection-[0-9]{4,}\.(?:json|sha256)`,
fullmatched against the whole pack-relative path.

`joulewise/identity_pins.py:994-997` — untouched by this wave — already owns the
same grammar as `conforming_pattern`, anchored
`(?:^|/)identity_pin_projection\.receipts/projection-[0-9]{4,}\.(?:json|sha256)$`,
and `identity_pins.py` is the module that *mints* these receipts
(`:2308-2317`). Nothing binds the two.

The comment on the new code even names the relationship — it says the histsem
gate now refuses "rather than relying on the later identity membrane to reject
it" — which is the point: the gate is deliberately duplicating the membrane's
grammar to reject earlier. Duplicating it is the correct behaviour; leaving the
copy unbound is the defect.

**Counterfactual:** add a third permitted extension (say `.sig`) to the freeze
grammar in `identity_pins.py`, the file that decides what a freeze looks like.
Newly frozen coordinates then carry a `projection-0001.sig` that
`arm_readiness.py` does not recognise, `_histsem_tree_has_authoring_custody`
returns True, and every fresh coordinate is refused as "historical coordinate
is not pre-authoring." The break is fail-closed but silent as to cause, and no
test catches it: `tests/test_receipt_histsem.py:2126-2148` pins the grammar to
its own hand-copied literal list, so it agrees with `arm_readiness.py` and
knows nothing about `identity_pins.py`.

**Ask:** import the pattern from `identity_pins`, or add one test asserting the
two patterns accept and reject the same set of paths.

### F-4 — nit — a correctly-marked value inside emphasis is refused

`_has_immediately_preceding_marker` (`scripts/check_paper_round7_artifacts.py:753-758`)
permits only spaces, tabs and one optional trailing backtick between
`[FILL:DX-nnn]` and the rendered value.

I probed the landed function directly against the real registry
(`DX-013` renders as `49 of 59`):

| prose form | result |
|---|---|
| `refused [FILL:DX-013] 49 of 59.` | passes |
| `refused [FILL:DX-013] **49 of 59**.` | **REFUSED** |
| `refused ([FILL:DX-013] 49 of 59).` | passes |
| marker, newline, then value | passes |
| `refused 49 of 59 [FILL:DX-013].` | REFUSED (correct — marker must precede) |

Severity is a nit, not a should-fix, for two reasons: the direction is
fail-closed (a false STOP_FILL, never a false pass), and the convention in
`docs/paper/round7/fill-checklist.md:271-277` prescribes plain
`[FILL:DX-nnn]` placement, with no bolded fill markers anywhere in `docs/paper/`.

**Counterfactual:** a writer bolds a filled value at fill time. R7F emits
`MISMATCH prose DX-013` and exits 2, and the message
("`[FILL:DX-013]` immediately before `'49 of 59'`") reads as though the marker
is missing when it is present two characters away.

### F-5 — nit — a tautological assertion

`tests/test_calibration_exits.py:2398-2401` asserts
`_CLEANUP_RACE_ERRNOS == frozenset({errno.ENOTEMPTY, errno.ENOENT})`, comparing
the constant to a retyped copy of its own definition eleven lines earlier at
`:99`.

**Counterfactual:** none. There is no single edit that this assertion catches
and that the two call sites it guards (`:2402` and `:2792`) would not also
catch. It is inert.

### F-6 — nit — argv pinned to hand-copied literals on both sides

`tests/test_issue_dg071_dg075_statistics.py:660-675` pins the exact
`subprocess.run` argv of `_git_commit` with `assert_called_once_with`.

I checked whether this is implementation-encoding before flagging it, and it is
not: `scripts/issue_dg071_dg075_statistics.py:119` *discloses* the query
verbatim inside the emitted artifact, so the argv genuinely is contract, and the
test's docstring says so. The nit is narrower — the test pins the argv (`:668-670`)
and the disclosure prose (`:391-392`) to two independent hand-copied literals,
neither derived from the other or from `ISSUER`.

**Counterfactual:** change the query at `:409` and its disclosure at `:119`
together but update only one of the two test literals. One test fails loudly, so
the exposure is small — deriving the argv assertion from the disclosed string
would close it entirely.

---

## 3. Cross-landing seams examined — no defect found

- **`tests/test_calibration_exits.py` is written by two landings**
  (CALEXITS-EVIDENCE-BYTES-01 +33, CALEXITS-HYGIENE-FIXES-01 +31), and they
  interact through the same attribute. EVIDENCE-BYTES installs a fake `ps` on
  `PATH` via `witness.writer_env_overrides` inside `capture()`
  (`:5744-5759`); HYGIENE constructs a second `PublicGovernedExitWitnessTests`
  from inside `RefusalInventoryTests` and sets
  `witness.writer_env_overrides = {}` (`:2095-2113`). A refuter reviewing
  either branch in isolation would not have run them together. I did:
  `RefusalInventoryTests` 16/16 OK, and
  `PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes`
  OK (59.8 s).
- **`joulewise/quiet_guard_process.py` ↔ `scripts/setup_quiet_guard.sh`** — the
  code change and its digest pin are in one landing and agree; the binding test
  at `tests/test_quiet_guard.py:1669-1672` proves it.
- **PREWINDOW-REGEX-01 is test-only** (`tests/test_prewindow_check.py`, +7/-3),
  with no production change — the ruling was "mark complete." I confirmed the
  coverage is not vacuous: the production pattern at
  `scripts/prewindow_check.sh:150` is
  `codex|claude|t3|mcp-server|run_campaign|window-chain`, and all four new
  fixture lines (`claude daemon`, `codex app-server`, `t3 worker`,
  `mcp-server`) match it, which is what makes the asserted count of 4 real.
- **No two landings touch the same production module.** The five production
  files (`arm_readiness.py`, `coldgate_receipt.py`, `quiet_guard_process.py`,
  `check_paper_round7_artifacts.py`, `setup_quiet_guard.sh`) each have exactly
  one author. No guard added by one landing is tripped by another's change.

## 4. Cold-gate check — nothing bypassed

CHARTER-V3-PACKET-INPUTS-01 lands 161 lines of candidate doctrine text
(`docs/process/coldgate_charter_v3_candidate.md`) plus a 64-line consult brief
template and a registry row. This is the one landing that could have been
process doctrine slipping in as ordinary code. It is not: the text is marked
CANDIDATE / NOT OPERATIVE, the operative v2 digest is untouched, the registry
spells out that the candidate must not be handed to a cold judge, and the
magistrate ruling routes ratification to Ed by email. Landing reviewed candidate
text under an explicit non-operative marker is the correct shape.
`docs/designs/cgv_harden_01.md` is a design note. The runbook paragraph from
MIDCAMPAIGN-CURE-GENERATION-01 went to
`docs/process_traces/2026-08-22-t20/real-transaction-runbook.md`, not to the
paper — matching its ruling ("goes to the paper lane after paper-e/f/g merge").
Nothing in this wave amends an operative process rule, a skill, or doctrine.

## 5. Evidence-custody note (not a code finding)

None of the twelve refuter verdicts is committed anywhere. This branch carries
twelve `01-sol-report.md` files and zero `02-refuter-*.md`. I located all twelve
as **untracked files in the individual fan worktrees**, e.g.
`/Users/edr/code/JouleWise-wt-fan-CGV-HARDEN-01/docs/process_traces/2026-09-04-fanout/CGV-HARDEN-01/02-refuter-merge-base.md`.

**Counterfactual:** prune those worktrees — an ordinary cleanup after a merge
wave — and the entire gauntlet evidence for WAVE-1 is gone, leaving twelve
landings whose commit messages say "UNREVIEWED" and no record that any refuter
ran. Recommend committing the twelve verdicts alongside this file before merge.

## 6. Tests run in this session

All at HEAD `7eed7c5f` in `/Users/edr/code/JouleWise-wt-int-fan-wave1`, using
`/Users/edr/code/JouleWise/.venv/bin/python -m unittest`. Modules chosen because
a claim above depends on them; the full suite was not run.

| Target | Result |
|---|---|
| `tests.test_coldgate_receipt`, `test_coldgate_charter_v3`, `test_midcampaign_cure_generation_docs`, `test_prewindow_check`, `test_quiet_guard_process` | 32 OK (1 skipped) |
| `tests.test_receipt_histsem.PreAuthoringProjectionCustodyTests` | 8 OK |
| `tests.test_paper_round7_artifacts.TypedArtifactCliTests` + `RegistryAndDigestTests` | 25 OK |
| `tests.test_quiet_guard` | 87 OK |
| `tests.test_issue_dg071_dg075_statistics` | 29 OK |
| `tests.test_calibration_exits.RefusalInventoryTests` | 16 OK |
| `tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes` | 1 OK |
| Whole-module confirmation run (pytest, `R7F_CORPUS_ROOT` pointed at a nonexistent path so the ~8-minute corpus replay skips rather than silently passing): `test_paper_round7_artifacts`, `test_receipt_histsem`, `test_coldgate_receipt`, `test_coldgate_charter_v3`, `test_midcampaign_cure_generation_docs`, `test_quiet_guard_process`, `test_prewindow_check` | 144 passed, 3 skipped, 223 subtests passed, 40 m 55 s, exit 0 |

The last row supersedes the class-scoped rows above for the seven modules it
covers: it runs each module whole, so a sibling test displaced or broken by a
landing could not hide behind a narrow class selection.

Direct probes (not tests) run against the landed code and the real artifacts:
the two digest recomputations in CB-1 and CB-4; the corpus enumeration in CB-3;
the zero-region result and the five-form marker probe behind F-1 and F-4.
