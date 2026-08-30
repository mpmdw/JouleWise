# Opus contract-lens refuter — sealed output (T26 cold gate, 2026-08-28)

Custody note: this is the verbatim final message of the Opus 5 refuter
seat spawned read-only by the cold Fable instance that wrote
`COLD-GATE-RULING.md` (PR #231). Filed after the ruling merged, from the
convening instance's own tool-result record; nothing below was edited.
The per-item "strongest objection" paragraphs are the ones quoted in the
ruling.

---

I have read everything I need. Findings below.

---

# Opus contract-lens refutation — four proposed process rules (packet `docs/process_traces/2026-08-27-t26/process-proposals/ruling-status-semantics.md`)

**Posture:** read-only throughout; nothing was edited, committed, or run against the repo. Every line number below was opened.

---

## Item 1 — Ruling-status semantics (`decided` vs `done`)

### (a) Strongest objection — quotable

> The rule is mis-typed at the granularity it targets, and the vocabulary it introduces does not exist. `docs/decision_log.md:14-16` defines exactly four statuses — `accepted`, `open` ("criteria defined, evidence pending"), `proposed`, `superseded by D-NNN` — and neither `decided` nor `done` is among them; the 162 index rows have already drifted to `accepted` (108), `adopted` (36), `ratified` (12), `open` (1) plus five one-off strings, so the proposal adds a sixth and seventh unenforced word to a vocabulary that is already undocumented and unchecked. Worse, the proposal keys a **row-level** status cell to a **clause-level** property: the S9 census counted **460 implementation clauses across 41 decisions** (`ruled-not-installed-sweep/FINDINGS-TABLE.md:3-17`), ~11 per decision, and **every one of the ten groups carries a nonzero B or C** — so under the proposed rule literally every decision from D-117 to D-157 becomes `decided`, and the kernel inherits **122 permanently-open W-list items** against a kernel that holds 105 tasks total and whose selector admits **at most one head per lane across three lanes** (`scripts/gen_state.py:466-495`). A gate that is red on every row from the day it is installed is not a gate; it is a light that gets waived on the first transaction night, which is precisely the failure mode D-157 already demonstrates.

### (b) Secondary objections

1. **The mechanism the proposal asks for already exists and is simply unused.** `docs/process/state_kernel.schema.json` already defines `dependency.kind: "decision"` with `state: pending|satisfied`, `strength: hard|advisory`, and `scope: start|…` — and `scripts/gen_state.py:186-192` already **refuses** a `satisfied` dependency that carries no evidence pointer, with `_check_pointer` (`:131-165`) requiring the pointed-to file to exist and any anchor to resolve. CI already runs this: `.github/workflows/ci.yml:25-26` (`python scripts/gen_state.py --check`). Across 105 kernel tasks, `kind: "decision"` is used **exactly once** (`MINT-GENERALIZE-01` → `D-110`, `state: pending`). The forcing evidence therefore does not imply a new status vocabulary; it implies **using the ratified one**. That is the cheaper rule the packet failed to consider.
2. **"Cites the installing commit/PR" is unrepresentable in the kernel as designed.** `gen_state.py:135-137` rejects any pointer path that is absolute, contains `..`, or contains `://` — so a commit SHA, a PR URL, or a GitHub link cannot be a kernel evidence pointer. The proposal's own two-part predicate is half-unmechanizable in the venue it names.
3. **"Names the producer-side check that refuses its absence" is unverifiable by any check that could plausibly be built.** The strongest available mechanism proves that a *file exists* and an *anchor resolves* (`gen_state.py:145-152`) — it cannot prove that the named test asserts the ruled thing. S9's own decisive test ("does the validator have any caller outside its own module and its tests?", `METHOD.md`) is a *human* read; a lint that greps for a test name would have passed `validate_prospective_analysis_manifest_v3` for the entire ten days it was uncalled. The rule therefore installs the exact false-A that `METHOD.md` names as "the worst outcome this sweep can produce."
4. **There is no W-list entity in the kernel.** "W-10"/"W-11" appear only as prose inside two `status_note` strings (`docs/process/state_kernel.json:3552`, `:3569`). The clause "the kernel work-selection gate treats `decided` clauses … as OPEN W-list items" names a data structure that does not exist and a gate (`selectable_task_ids`, `gen_state.py:478-495`) that has no notion of decisions at all.
5. **Nobody would mechanically check it.** The only existing decision-log check is `tests/test_docs_freshness.py:176-184`, which asserts index IDs equal body IDs in order. It reads the status column not at all — and its regex `^\| (D-\d{3}) \|` silently skips `D-150a`/`D-150b`, so even the existing check has a blind spot.

### (c) Amendment I would accept

**Rule text (amended):**

> A decision-log index row whose ruling carries at least one implementation clause that is not yet installed-and-producer-checked keeps status **`open`** — the existing documented value at `docs/decision_log.md:14-16`, "criteria defined, evidence pending" — and its Status cell names the state-kernel task id that carries the remaining clauses, in the form `open (installs via <TASK-ID>)`. That kernel task carries a `dependencies[]` entry with `kind: "decision"`, `target: "D-NNN"`, `strength: "hard"`, `scope: "start"`; it may move to `state: "satisfied"` only with an `evidence` pointer to the repo-relative path of the regression that fails when the ruled value is absent. The installing commit or PR is cited in the decision's body section, not in the kernel. No new status word is minted.

**Enforcement mechanism (exact):** one new test in `tests/test_docs_freshness.py` beside `test_decision_index_matches_decision_bodies` (`:176`) that (i) asserts every index-row Status cell's leading token is drawn from a closed set `{accepted, adopted, ratified, open, proposed, superseded, recorded, executed, adjudicated}`, and (ii) asserts every row whose leading token is `open` matches `open \(installs via ([A-Z0-9-]+)\)` with that id present in `docs/process/state_kernel.json`'s `tasks`. The dependency half needs **no new code**: `gen_state.py:186-192` already refuses evidence-free `satisfied`, and `.github/workflows/ci.yml:26` already runs it on every PR. Fix the `D-\d{3}` regex to `D-\d{3}[a-z]?` in the same change.

**Where recorded:** the amended rule text goes in `docs/decision_log.md`'s "How To Use This Log" (`:14-16`), because that is the only place a future session reads before writing a row; the enforcement lives in `tests/test_docs_freshness.py` + the existing `gen_state.py --check` CI step. It does **not** belong in `docs/orchestration.md` or the council skill — neither is loaded at the moment a row is written.

---

## Item 2 — The D-118/D-121 gate ledger

### (a) Strongest objection — quotable

> There is no gate to attach a CI check to. `gh api repos/mpmdw/JouleWise/branches/main/protection` returns **404 "Branch not protected"** — `main` has *no* branch protection and therefore *no* required status checks at all, so a red CI job blocks nothing today and a new "gate-ledger" job would block nothing tomorrow; `gh pr merge` and a direct push both proceed over red. Enabling protection is an admin action on Ed's account (all five sampled merges — #227, #226, #224, #217, #214 — were performed by `mpmdw`), and `.github/workflows/ci.yml:257-262` already records the standing constraint in the repository's own words: *"do not promote this job to a required status check … that is a lead-gated required-check change and must be proposed, not applied here."* Meanwhile the proposed body-grep is simultaneously too weak and too strong: **zero of the seven most recent PR bodies (#227, #226, #224, #223, #217, #214, #212) contain the string "gate ledger"**, yet #224 carries a full "Gauntlet record (seats run one at a time)" section and #217 a commit-by-commit audit → fix-round → delta record — so the check would have refused seven PRs whose gate substance was present under a different heading, while passing any PR that pastes twelve headings with no evidence behind them. It converts a real gate into a spelling test.

### (b) Secondary objections

1. **False refusals are structural, not incidental, and curing them amends an Ed directive.** D-118's mechanical clause (`docs/decision_log.md:7789-7795`) says "every PR description must carry a GATE LEDGER listing items 1-11 … and any item marked NOT-RUN blocks the merge," and the gate preamble at `:7752` says "no item is discretionary." Items 2 (paired distinct lenses), 9 (unpiped full-suite replay on the *integration tree*), and 11 (post-merge cross-unit integration review) are not meaningful for a docs-only PR such as #224 (a retrospective) or #223 (runbook prose). Making them satisfiable requires an `N/A` tier that D-118 does not have — and inventing one is an **amendment to a RATIFIED Ed directive**, not a mechanism ruling.
2. **Precedent says this lane is Ed's, not the cold gate's.** `docs/decision_log.md:7879-7880` records verbatim that "Ed's ruling moots the rule-11 cold gate on process amendments" for D-121. Merge-gate content has been settled by Ed twice (D-118, D-121). A cold Fable instance can rule on *which mechanism* enforces an Ed-ratified rule; it cannot widen or narrow the rule's items.
3. **Protection would misfire during exactly the operations it is meant to protect.** Required checks with `enforce_admins: false` are decorative on a solo repo (the admin merges anyway); with `enforce_admins: true` they lock Ed out mid-window — and D-150a's push-freeze/window commitments and D-155 NR-2's "a fetch is licensed inside the freeze span, a commit/push/branch-move is not" mean the enforcement would land precisely where a red check is least recoverable.
4. **The evidence the packet cites does not implicate the ledger's *format*.** All three forcing instances (CONSUME-CONFIRMATION-SUPPLY-01, the runbook arguments, D-157) are *ruled-but-not-installed* defects. None of them is a defect a gate-ledger heading would have caught: D-157 passed estate 10 end to end. A ledger checklist is orthogonal to the forcing evidence, which is item 1's evidence, not item 2's.

### (c) Amendment I would accept

**Rule text (amended):**

> The D-118/D-121 gate ledger becomes a tracked artifact rather than PR prose. Every PR that changes tracked files adds `docs/gate_ledgers/<branch-slug>.md` in its own diff, containing exactly twelve rows keyed `1`–`12`, each with one of `RUN <repo-relative-path-or-commit-sha>`, `N/A <one-line reason>`, or `NOT-RUN`. A `.github/pull_request_template.md` seeds the twelve rows so the form is in front of the author. CI gains one job, `gate-ledger`, that fails if the PR's diff adds no ledger file, if any of the twelve keys is missing, if any row reads `NOT-RUN`, or if any `RUN` row cites a repo-relative path that does not resolve at the head. The `N/A` vocabulary and the docs-only exemption are an amendment to D-118 and go to **Ed**, not to this seat.

**Enforcement mechanism (exact):** `.github/pull_request_template.md` (new) + `.github/workflows/ci.yml` job `gate-ledger` running a small `scripts/check_gate_ledger.py` that reuses `gen_state.py`'s `_check_pointer` path rules (`gen_state.py:131-165`) for the `RUN` citations. **Plus the Ed action item without which none of it binds:** enable branch protection on `main` requiring `test`, both exclusive jobs, and `gate-ledger`, with `enforce_admins` decided by Ed. Until Ed does that, the cold gate should record the rule as **advisory and explicitly so**, rather than let the project believe it has a gate it does not have.

**Where recorded:** the rule text amends `docs/decision_log.md` D-118's "Mechanical enforcement" paragraph (`:7789-7795`) — that is the ONE home; `docs/orchestration.md` §"The loop, end to end" (`:49`) gets a one-line pointer, not a restatement; the operation-loop skill §5 "Lead gates" (`/Users/edr/.claude/skills/operation-loop/SKILL.md:255`) gets the same pointer so it loads in-session.

---

## Item 3 — The T-0 `R1-completion → validity-origin ≤ 5 s` bound

### Which clock the consumer uses — the direct answer

**The consumer uses `time.monotonic_ns()`.** Verified at four independent consumption sites:

- `joulewise/arm_readiness.py:8579` — `if time.monotonic_ns() > receipt["valid_until_monotonic_ns"]: raise … "readiness_record_expired"`
- `joulewise/arm_readiness.py:9231` — `if require_unexpired and time.monotonic_ns() > arm["valid_until_monotonic_ns"]` → `launch_binding_mismatch`
- `joulewise/arm_readiness.py:4932-4933` — `receipt["valid_until_monotonic_ns"] < now_monotonic_ns`, where `now_monotonic_ns` is supplied as `time.monotonic_ns()` at `:8372`, `:8430`, `:8627`
- `joulewise/arm_readiness.py:5827-5832` — `authentication_now` on the same clock

**Therefore: yes, that is so.** `validity_origin`'s clock choice is *forced by the consumer's expiry test*, not free. `validity_origin = context.clock.monotonic_ns()` (`arm_readiness_evidence_t0.py:2325`) and `valid_until = validity_origin + _validity_horizon_ns(kind)` (`:2337-2339`, constants at `:49-50`: 20 min volatile / 6 h non-volatile; `CLOCK_ATTESTATION` is non-volatile per `:146-153`) are on exactly the clock the consumer tests against. **The 6 h horizon is internally consistent and must not be moved to RAW.** The ill-typing was never in the horizon; it was only in the ruled cross-clock ≤5 s comparison — and even that is **already cured at HEAD**: `r1_batch_finished_monotonic_ns` is stamped with `context.clock.monotonic_ns()` at `arm_readiness_evidence_t0.py:1114` and published at `:1119`, and the arm-side predicate consumes that same-clock pair at `arm_readiness.py:6339-6341`.

### (a) Strongest objection — quotable, refuting BOTH cures

> Both offered cures are wrong, and for opposite reasons. **(a) Restating the bound on `CLOCK_MONOTONIC_RAW` both sides is unavailable at the horizon and actively harmful at the constant:** the consumer's expiry test is `time.monotonic_ns()` (`arm_readiness.py:8579`, `:9231`, `:4933`, `:5832`), so `validity_origin` cannot move to RAW without breaking every consumption site, and a RAW restatement would require a *third* stamp; worse, RAW is sleep-inclusive while `time.monotonic_ns()` on Darwin is `CLOCK_UPTIME_RAW` and sleep-blind — the difference measured on this machine is **812,998 s** (`debate-opus-critique.md:59-62`) — and T-0 runs uncaffeinated by construction, so a RAW-sided derivation bound would refuse the night on a nap: the exact closed-direction availability defect Opus's own critique used to *move* R1 onto RAW. **(b) The proposed provenance for the constant is circular:** the ruling's "oldest participating R1 result ≤35 s old at issuance" is definitionally `30 s + 5 s` — the R1 batch bound is `0 ≤ duration ≤ 30_000_000_000` at `arm_readiness_evidence_t0.py:1116` and re-checked at `arm_readiness.py:6332` — so 35 s is a *consequence* of the 5, not an independent derivation of it. And the 5 s is derivable from no budget in the ruling: at the ruling's own 3.68 ppm, the 0.5 s reference bound permits a total span of 0.5 / 3.68e-6 ≈ **135,870 s (37.7 h)**; the ruled 6 h consumes 15.9% of it and the *entire* 495 s probe envelope (11 governed `_fresh_probe` sites × `_PROBE_TIMEOUT_SECONDS = 45`, `arm_readiness_evidence_t0.py:54`) adds **1.82 ms**, 0.36% of the remaining budget. Five seconds buys 18 µs of drift protection against a 500 ms allowance.

### What the 6 h horizon and the arm-side re-check already guarantee (so what striking actually costs)

The step-and-drift case is closed by mechanism, not by this constant:

- `arm_readiness.py:6326-6327` — `600 s ≤ t0_span_ns ≤ 3600 s`, R0 → author anchor, on RAW.
- `arm_readiness.py:6329` — `0 ≤ anchor_delta_ns ≤ 5_000_000` (the R0-vs-author `REALTIME − MONOTONIC_RAW` delta, 5 ms).
- `arm_readiness.py:6342-6366` — the arm-side **live** re-sample: `boot_session_id` equality (`:6356`), read-skew ≤ 1 ms, and `live_delta ≤ 5_000_000` against the published author anchor. The R1-completion → stamp interval sits *inside* the author-anchor → arm span that this re-check brackets, so a `CLOCK_REALTIME` step anywhere in the fourteen intervening derivers is caught at arm time regardless of the 5 s bound.
- `arm_readiness.py:6339-6341` — `valid_until − r1_batch_finished_monotonic_ns ≥ 21_600_000_000_000`. Since `valid_until = validity_origin + 6 h` exactly (`arm_readiness_evidence_t0.py:2337-2339`), this predicate is **arithmetically identical to `validity_origin ≥ r1_batch_finished`** — i.e. HEAD already enforces the *lower* half (`0 ≤ …`) of the ruled relation, non-tautologically and on one clock. Only the upper half is open, exactly as the code comment at `:6336-6338` states.

Striking the upper bound therefore loses **nothing metrological**. It loses a liveness/hang detector — and the R1-only shape was the wrong instrument for that anyway.

### (b) Secondary objections

1. **The 5 s bound cures one-fifteenth of the real defect.** A *single* stamp at `arm_readiness_evidence_t0.py:2325` is applied to all fifteen rows after the loop at `:2318-2322`. Every row's horizon therefore understates its evidence age by the full derivation elapsed time — and nine of the fifteen rows are **volatile with a 20-minute horizon** (`:49`, `:133-145`), against a permitted probe envelope of 495 s (41% of 20 minutes). An R1-only bound leaves `PROCESS_CENSUS`, `POWERMETRICS_PROBE`, `MAINTENANCE_CENSUS` and six others uncovered by the same defect.
2. **Option 1 from §6.3 (move the stamp to just after R1) is worse than it looks**, because it stamps *all fifteen rows*, including the nine volatile ones derived afterwards, at a time *before* they were derived — turning an age understatement into a receipt whose volatile evidence is dated earlier than it exists. §6.3 recommends it on ordering grounds alone and does not price this.
3. **Nothing at HEAD is inert or always-true**, so the cold gate is not under time pressure: `arm_readiness.py:6339-6341` is a real refusal and `:6336-6338` documents the open item in code. The interim disposition is correct and should be affirmed as such regardless of which way the constant goes.

### (c) My recommended bound — clock, constant, provenance

**STRIKE the R1-only `≤ 5 s` upper relation.** It has no derivation, its stated 35 s corollary is circular, and the physics it purports to bound is covered four orders of magnitude over by the ruling's own drift arithmetic and by the two 5 ms anchor gates.

**Replace it — if the seat wants any bound — with an aggregate derivation deadline covering all fifteen rows, on the ordinary-monotonic clock (the one the consumer tests):**

> `validity_origin_ns − derivation_start_monotonic_ns ≤ 495_000_000_000`, both endpoints from `context.clock.monotonic_ns()`, `derivation_start_monotonic_ns` published in the receipt beside `r1_batch_finished_monotonic_ns`.

**Provenance of 495 s:** it is the code's own worst *permitted* wait — eleven `_fresh_probe` call sites (enumerated verbatim in `reason-code-coverage-delta.md` §6.3's AST census: `:895`, `:991`, `:1038`, `:1396-1399`, `:1474`, `:1509-1511`) × `_PROBE_TIMEOUT_SECONDS = 45` (`arm_readiness_evidence_t0.py:54`). Because it is derived from the timeouts the code already enforces, it **cannot false-refuse a successful path** — every successful probe is strictly below its own ceiling — and it fires only on a genuine hang or on unbounded non-probe work, which is the only real thing the 5 s bound was gesturing at. It is a **liveness bound, labelled as one**, not a metrology bound dressed as one.

**Stronger variant I would prefer the cold gate consider:** stamp each row's `valid_until` from its *own* derivation completion rather than from one global `validity_origin` at `:2325`. That removes the age-understatement class entirely for all fifteen rows, makes the deadline unnecessary, and costs one field per row. If the cold gate adopts this, the ruled relation should simply be recorded as **DISSOLVED, superseded by per-row stamping**, with the 6 h and 20 min horizons unchanged.

**Do not, under any formulation, move `validity_origin` onto `CLOCK_MONOTONIC_RAW`.** The RAW anchors stay exactly where they are (`clock_reference.py:115-122`; `arm_readiness_evidence_t0.py:1115-1117`) as evidence for the anchor physics.

---

## Item 4 — D-160 R-5 (evidence-path rulings)

### (a) Strongest objection — quotable

> R-5 is a pious exhortation, and the proof is that the document promulgating it violated it twice within thirty hours. R-5 was written at `docs/process_traces/2026-08-27-t26/smoke-corpus-consult/04-MAGISTRATE-RULING.md:80-83`; the addendum at `:88-99` records that the same ruling's own R-3 "reads as post-verdict" and was falsified by executed evidence — "refuter A's probe; director's bench check; `run_campaign.py` has zero references to the binding" — and the addendum at `:139-152` records that the previous addendum's "distinct analysis root" wording "was not executable on merged code," corrected as NR-14 against `run_campaign.py:4884-4920`, `:6364`, and `analysis_manifest_v3.py:3447-3504`. That second addendum ends, at `:153`, with the sentence "**Lesson (D-160 R-5 again): rule placement only after a seat has executed it.**" A rule whose own author restates it as a lesson learned, twice, in the same file, one and two days after ratifying it, has demonstrated its binding force is zero — and it failed at *addenda*, which the rule as drafted does not even mention. Ratifying it unchanged buys the project nothing it did not have on 2026-08-27, and buys it the specific harm of believing the class is now closed.

### (b) Secondary objections

1. **It is unenforceable as scoped because it has no subject with a duty.** "an evidence-path ruling is made only after **a seat** has executed the path" — but the seats are blind design seats; the *ruling* is the magistrate's synthesis. Under rule 11 the seat that could execute is not the seat that rules, and the seat that rules is structurally forbidden from being three tool-calls deep in an execution loop. The rule assigns a duty to no one.
2. **Partial conflict with the cold-gate charter, though not a fatal one.** `docs/process/coldgate_charter.md` §4 licenses a cold seat to read "the code itself, read-only, wherever verification requires it" and forbids narrative process documents. Reading is licensed; **executing** is not, and a cold instance has no worktree. So a cold seat can satisfy R-5's second disjunct ("proven from code that it cannot execute") but never the first. R-5 as drafted is therefore unsatisfiable-by-the-first-limb in exactly the venue rule 11 routes hard questions to. This is fixable by relocating the duty (below), not by relaxing the rule.
3. **No conflict with "mechanically assembled, no stream context."** An execution transcript — argv, tree revision, exit code, artifact path present/absent — is *primary evidence*, not narrative process context, and is squarely admissible under charter §4's custody-input clause. The rule 11 objection the packet anticipates does not land, provided the transcript is a **custody input assembled into the packet**, not something the seat is told to go run.
4. **The forcing evidence is real but under-scoped.** D-160's own trigger line (`:3-6`) names three falsified premises in D-158 (R-1, R-4(3), A-2); the S9 sweep supplies the same shape at scale (`FINDINGS-TABLE.md:3-17`: 53 clauses status **C**, "not installed at all"). But R-5 addresses only the *design-consult* moment. Both of its own violations occurred at *addendum/placement* moments, which is where the class actually bites.

### (c) Amendment I would accept

**Rule text (amended):**

> A ruling or addendum whose dispositive premise asserts that an evidence-production path **does** or **does not** yield a named artifact is INADMISSIBLE unless its custody directory carries, as a listed input, either (a) an **execution record** — exact argv, working-tree revision, exit code, and the produced-or-absent artifact path — or (b) a **code-path proof** naming the `file:line` at which the path refuses. The obligation falls on the party **assembling the packet or drafting the addendum**, never on the adjudicating seat; a cold instance that finds neither present returns the question **unruled** rather than ruling on the premise. This binds addenda and placement notes exactly as it binds the original ruling.

**Enforcement mechanism (exact):** one test in `tests/test_docs_freshness.py` over the stable glob `docs/process_traces/**/*MAGISTRATE-RULING*.md` (15 files today, a consistent convention): any file containing a `## Rulings` or `## Addendum` heading must also contain a `## Executed evidence` section carrying at least one fenced block with a `$ ` argv line and an `exit_code` or `file:line` citation. This is deliberately a **shape check, not a truth check** — it cannot verify the transcript is real, and the cold gate should say so in the ruling rather than let the project mistake it for verification. Its whole value is that the absence is loud at CI time instead of discovered a day later in an addendum.

**Where recorded:** the rule text goes into `docs/process/coldgate_charter.md` §4's packet-input list (which forces a new charter digest in `docs/process/coldgate_charter_registry.md`, so the amendment is versioned rather than silent) **and** as D-160's R-5 body text in `docs/decision_log.md`. The lint goes in `tests/test_docs_freshness.py`, which CI already runs. It does **not** belong in the global council skill: the failure mode is JouleWise's evidence-path shape, and a global skill would not be loaded by a cold instance, which reads only the charter (`coldgate_charter.md:9-13`).

---

## Cross-cutting note for the cold seat

Items 1 and 4 share one defect: both propose to fix a *representation* problem (`decided` vs `done`; "execution before ruling") when the S9 census shows the failure is a *coverage* problem — 122 of 460 clauses unenforced at the producer (`FINDINGS-TABLE.md:3-17`). Item 1's cheaper alternative already ships in `gen_state.py` and is used once in 105 tasks; item 4's cheapest alternative is a packet-shape requirement, not a duty on the ruler. Item 2's proposal is aimed at a gate that does not mechanically exist in the first place (`main` unprotected, 404). Item 3 is the only one of the four where the cold seat is asked to rule on something it can actually settle — and there the packet's framing is half-stale: the clock ill-typing is **cured at HEAD** (`arm_readiness_evidence_t0.py:1114`, `arm_readiness.py:6339-6341`), the consumer's clock forces the horizon's clock, and the live question is only whether a constant with no derivation should be reinstated. My answer to that one is no: strike it, and if a bound is wanted, install a 495 s aggregate derivation deadline whose provenance is the code's own probe timeouts.
