# COLD-GATE RULING — T26 process proposals (cold Fable instance, 2026-08-28)

Packet: `docs/process_traces/2026-08-27-t26/process-proposals/ruling-status-semantics.md`
(four items). Evidence read at `origin/main` `e964a48f` unless a line cites
otherwise. Refuter: one Opus contract-lens seat, spawned by this instance,
read-only, briefed to refute every item; its strongest objection per item is
quoted verbatim below. Verdict vocabulary: RATIFY = charter AFFIRM;
AMEND = AFFIRM with the exact text below substituted for the packet's;
REJECT = charter REJECT.

## 0. Disclosures required by the charter and its registry

- **Charter digest.** Expected (registry `docs/process/coldgate_charter_registry.md`,
  "Operative charter" row): `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`.
  Observed (`shasum -a 256 docs/process/coldgate_charter.md` at `f6544b08`):
  `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`. Match.
- **Contamination.** This instance was launched from the main checkout, not a
  doctrine-free worktree (registry convening-procedure item 1 NOT met):
  `CLAUDE.local.md` (rule 11 doctrine), the auto-memory index, and the global
  `council` skill were auto-loaded. Per registry item 2 the ruling stands or
  falls on cited evidence, all of which is code, the decision log, the packet
  and its listed custody inputs. No run-state, run-report, council-log or
  session-memory file was opened.
- **Sealing deviation.** The convening brief instructed this instance to
  spawn the refuter itself and quote it. Charter §5 wants both outputs sealed
  before either sees the other. Mitigation actually applied: all four
  verdicts and the item-3 bound were drafted before the refuter returned;
  the refuter's output changed item 3's constant framing (liveness, not
  metrology), item 1's vocabulary (reuse `open`, mint nothing) and item 4's
  duty-bearer. Those three changes are the refuter's unique catches and are
  credited as such. The refuter's full output is not reproduced here; it
  lives in this session's task record and should be custodied beside this
  file by the convening session (packet-hygiene NIT: the brief gave no
  custody path for it).
- **Packet hygiene.** Item 3's framing is half-stale: the cross-clock defect
  is already cured at HEAD (`joulewise/arm_readiness_evidence_t0.py:1120,
  :1199` publish `r1_batch_finished_monotonic_ns` on the consumer's clock;
  `joulewise/arm_readiness.py:6339-6341` consumes it). The live question is
  only the upper constant. Item 2's forcing evidence is item 1's evidence
  (ruled-not-installed), not a ledger-format defect. Neither defect
  prevents ruling.

---

## Item 1 — ruling-status semantics (`decided` ≠ `done`)

**Refuter's strongest objection (verbatim):**

> The rule is mis-typed at the granularity it targets, and the vocabulary it introduces does not exist. `docs/decision_log.md:14-16` defines exactly four statuses — `accepted`, `open` ("criteria defined, evidence pending"), `proposed`, `superseded by D-NNN` — and neither `decided` nor `done` is among them; the 162 index rows have already drifted to `accepted` (108), `adopted` (36), `ratified` (12), `open` (1) plus five one-off strings, so the proposal adds a sixth and seventh unenforced word to a vocabulary that is already undocumented and unchecked. Worse, the proposal keys a **row-level** status cell to a **clause-level** property: the S9 census counted **460 implementation clauses across 41 decisions** (`ruled-not-installed-sweep/FINDINGS-TABLE.md:3-17`), ~11 per decision, and **every one of the ten groups carries a nonzero B or C** — so under the proposed rule literally every decision from D-117 to D-157 becomes `decided`, and the kernel inherits **122 permanently-open W-list items** against a kernel that holds 105 tasks total and whose selector admits **at most one head per lane across three lanes** (`scripts/gen_state.py:466-495`). A gate that is red on every row from the day it is installed is not a gate; it is a light that gets waived on the first transaction night, which is precisely the failure mode D-157 already demonstrates.

**Verdict: AMEND.** The forcing evidence (three ruled-not-installed
instances in one session; S9's 122 B/C clauses) is real, but it implies
USING the installed mechanism, not minting a vocabulary. Verified: the state
kernel already types a dependency `kind: "decision"` with `state:
pending|satisfied` (`docs/process/state_kernel.schema.json:45-62`);
`scripts/gen_state.py:185-191` refuses a `satisfied` dependency without an
evidence pointer and a `pending` one with; `_check_pointer` (`:131-165`)
requires the pointed file to exist and any anchor/json-pointer to resolve;
invariant 3 (`:357-366`) forces a task with a pending hard start dependency
to `blocked`; CI runs `gen_state.py --check` on every PR
(`.github/workflows/ci.yml:25-26`). That mechanism is used exactly once in
105 tasks. The packet's "W-list" has no kernel existence (prose in two
`status_note` strings).

**Ruled text (replaces the packet's rule):**

> A decision-log entry that carries an implementation clause (a value that
> enters a manifest, a check code refuses on, a runbook line, a generator
> output) is recorded with index status **`open (installs via <TASK-ID>)`**
> — `open` is the existing documented status, "criteria defined, evidence
> pending" — naming the state-kernel task that carries the uninstalled
> clauses. In the same commit, that kernel task gains a dependency
> `{kind: "decision", target: "D-NNN", strength: "hard", scope: "start",
> state: "pending", evidence: null, required: "<the clause, one line>"}`
> on every task the clause gates (at minimum the transaction task when the
> clause touches a transaction). The dependency moves to `satisfied` only
> with an `evidence` pointer at the repo-relative path (+ anchor) of the
> regression that FAILS when the ruled value is absent at the producer, and
> the index status moves to `accepted`/`adopted` with the installing PR or
> commit named in the entry body. Nothing selects while the dependency is
> pending (kernel invariant 3). Binds prospectively from this ruling's
> merge; the S9 SHORTLIST items marked "gates the mint" or "gates windows"
> are registered under it in the ruling's implementation commit — not all
> 460 clauses (the refuter's "red on every row" objection is accepted as a
> scoping constraint, and the S9 census remains the truth check the kernel
> cannot perform).

**Enforcement (mechanical):** (i) existing — `gen_state.py --check` in CI
refuses evidence-free `satisfied` and blocks selection on pending hard
start; (ii) new — one test beside
`tests/test_docs_freshness.py:176` `test_decision_index_matches_decision_bodies`
asserting every index Status cell's leading token is in the closed set
`{accepted, adopted, ratified, open, proposed, superseded, recorded,
executed, adjudicated}`, every `open` cell matches
`open \(installs via ([A-Z0-9-]+)\)` with that id present in
`state_kernel.json` `tasks` AND that task carrying a `kind: decision`
dependency targeting the row's D-id; fix the `D-\d{3}` regex to
`D-\d{3}[a-z]?` in the same change (it silently skips D-150a/b today).
This is a shape check; it proves the pointer exists, not that the test
asserts the ruled thing. That residual is by design the S9-shape sweep's
job, re-run before every transaction (record as a standing pre-window row).

**Where recorded:** decision log "How To Use This Log" (`:14-16`) gains the
`open (installs via …)` form — the only text a row-writer reads before
writing a row; a new decision-log entry (next D-number) carries this
ruling's four verdicts by pointer to this file; `docs/agent_playbook.md`
Mission M0 gains one line ("a pending `kind: decision` dependency is an
uninstalled ruling — not selectable"); no change to `orchestration.md` or
the council skill (neither loads at row-writing time).

---

## Item 2 — the D-118/D-121 gate ledger has no mechanical existence

**Refuter's strongest objection (verbatim):**

> There is no gate to attach a CI check to. `gh api repos/mpmdw/JouleWise/branches/main/protection` returns **404 "Branch not protected"** — `main` has *no* branch protection and therefore *no* required status checks at all, so a red CI job blocks nothing today and a new "gate-ledger" job would block nothing tomorrow; `gh pr merge` and a direct push both proceed over red. Enabling protection is an admin action on Ed's account (all five sampled merges — #227, #226, #224, #217, #214 — were performed by `mpmdw`), and `.github/workflows/ci.yml:257-262` already records the standing constraint in the repository's own words: *"do not promote this job to a required status check … that is a lead-gated required-check change and must be proposed, not applied here."* Meanwhile the proposed body-grep is simultaneously too weak and too strong: **zero of the seven most recent PR bodies (#227, #226, #224, #223, #217, #214, #212) contain the string "gate ledger"**, yet #224 carries a full "Gauntlet record (seats run one at a time)" section and #217 a commit-by-commit audit → fix-round → delta record — so the check would have refused seven PRs whose gate substance was present under a different heading, while passing any PR that pastes twelve headings with no evidence behind them. It converts a real gate into a spelling test.

**Verdict: AMEND.** The 404 was independently reproduced by this instance.
The packet's diagnosis stands (D-118's "Mechanical enforcement" paragraph,
`docs/decision_log.md:7789-7795`, names a ledger no file, template, job or
skill instantiates); the packet's cure cannot bind until Ed protects
`main`. A cold gate may rule the MECHANISM for an Ed-ratified rule; it may
not add an `N/A` tier or a docs-only exemption to D-118's twelve items —
those are amendments to Ed's directive (D-121 records that Ed's ruling
mooted the cold gate on this very subject, `:7879-7880`).

**Ruled text (amends D-118 "Mechanical enforcement", additively):**

> The gate ledger has a tracked form. (a) `.github/pull_request_template.md`
> seeds twelve rows keyed `1`–`12` (D-118 items 1–11, D-121 item 12), each
> to be filled `RUN <repo-relative-path | commit-sha>` or `NOT-RUN`; item
> 12 names the final head sha. (b) CI job `gate-ledger`
> (`pull_request: [opened, synchronize, edited, ready_for_review]`) fails
> when any of the twelve keys is missing, any row reads `NOT-RUN` or is
> empty, any `RUN` path does not resolve at the PR head (reuse
> `gen_state.py` `_check_pointer` path rules), or item 12's sha is not the
> PR head. The job is labelled ADVISORY in its own header until Ed makes
> it a required status check; the D-072 self-merge condition is that the
> job is green on the final head. (c) The pasted-block risk is DELIBERATE
> operator conduct and is out of the threat model by D-161; the job
> targets the MISTAKE class (a forgotten item), which is what the three
> forcing instances were.

**Two items routed to Ed, without which (b) does not bind:** (E1) enable
branch protection on `main` with `test`, both exclusive jobs and
`gate-ledger` required, `enforce_admins` at Ed's choice, mindful that
D-150a/D-155 NR-2 forbid pushes inside the freeze span so a red check is
least recoverable exactly there; (E2) whether D-118 gains an
`N/A <reason>` tier and a docs-only exemption (the practice of direct
docs commits to main under doctrine rule 7 is otherwise formally in
tension with "NOTHING approaches merge"). Until E2, docs-only PRs fill
all twelve rows or land as direct commits as today.

**Where recorded:** D-118 body paragraph "Mechanical enforcement" (the ONE
home) gains the ruled text; `docs/orchestration.md` §"The loop, end to
end" and the `operation-loop` skill §5 each get a one-line pointer;
`TASK_QUEUE.md`/kernel gain the Ed rows E1, E2.

---

## Item 3 — the T-0 ruling's 5 s issuance bound

**Refuter's strongest objection (verbatim):**

> Both offered cures are wrong, and for opposite reasons. **(a) Restating the bound on `CLOCK_MONOTONIC_RAW` both sides is unavailable at the horizon and actively harmful at the constant:** the consumer's expiry test is `time.monotonic_ns()` (`arm_readiness.py:8579`, `:9231`, `:4933`, `:5832`), so `validity_origin` cannot move to RAW without breaking every consumption site, and a RAW restatement would require a *third* stamp; worse, RAW is sleep-inclusive while `time.monotonic_ns()` on Darwin is `CLOCK_UPTIME_RAW` and sleep-blind — the difference measured on this machine is **812,998 s** (`debate-opus-critique.md:59-62`) — and T-0 runs uncaffeinated by construction, so a RAW-sided derivation bound would refuse the night on a nap: the exact closed-direction availability defect Opus's own critique used to *move* R1 onto RAW. **(b) The proposed provenance for the constant is circular:** the ruling's "oldest participating R1 result ≤35 s old at issuance" is definitionally `30 s + 5 s` — the R1 batch bound is `0 ≤ duration ≤ 30_000_000_000` at `arm_readiness_evidence_t0.py:1116` and re-checked at `arm_readiness.py:6332` — so 35 s is a *consequence* of the 5, not an independent derivation of it. And the 5 s is derivable from no budget in the ruling: at the ruling's own 3.68 ppm, the 0.5 s reference bound permits a total span of 0.5 / 3.68e-6 ≈ **135,870 s (37.7 h)**; the ruled 6 h consumes 15.9% of it and the *entire* 495 s probe envelope (11 governed `_fresh_probe` sites × `_PROBE_TIMEOUT_SECONDS = 45`, `arm_readiness_evidence_t0.py:54`) adds **1.82 ms**, 0.36% of the remaining budget. Five seconds buys 18 µs of drift protection against a 500 ms allowance.

**Facts this instance verified at HEAD.**
1. `validity_origin = context.clock.monotonic_ns()` after the fifteen-row
   loop (`arm_readiness_evidence_t0.py:2313-2325`); production binds it to
   `time.monotonic_ns` (`:296-304`), which on this machine is
   `mach_absolute_time()` (`time.get_clock_info('monotonic')`), i.e.
   `CLOCK_UPTIME_RAW`, sleep-blind — as the T-0 ruling itself recorded.
2. Every consumer expiry test is on that same clock
   (`arm_readiness.py:4933, 5828-5832, 8579, 9231`). The horizon is
   therefore correctly typed and must stay on the ordinary clock.
3. R1 completion is published on BOTH clocks: RAW via the author anchor
   (`:1115-1117`, arm-side `r1_batch_duration_ns`) and ordinary via
   `r1_batch_finished_monotonic_ns` (`:1120`, `:1199`).
4. The arm-side predicate already enforces the LOWER half on one clock:
   `valid_until − r1_batch_finished_monotonic_ns ≥ 21_600_000_000_000`
   (`arm_readiness.py:6339-6341`), which since `valid_until =
   validity_origin + 6 h` exactly (`:2337-2339`) is `validity_origin ≥
   r1_finished`. Issuance runs the same predicate (`:2340-2349`), so the
   check is producer-side (S9 status A). The code comment at `:6336-6338`
   names the upper half as the open magistrate item. Nothing inert was
   substituted; the implementing stream's stop was correct.
5. Steps and slews between R1 and consumption are caught by mechanism,
   not by this constant: R0→author RAW anchor delta ≤ 5 ms (`:6329`) and
   the live arm-side re-sample ≤ 5 ms against the published author anchor
   with `boot_session_id` equality (`:6342-6366`).
6. The ruled 5 s and its 35 s corollary have no derivation in the T-0
   ruling; the refuter's arithmetic (5 s ≈ 18 µs of 3.68 ppm drift against
   a 500 ms allowance) is correct.

**Verdict: AMEND — the 5 s constant and the 35 s corollary are STRUCK; the
upper relation is retained as a well-typed LIVENESS bound on the
consumer's clock, one-constant change.**

> Ruled relation (replaces "R1-completion→validity-origin ≤5 s (oldest
> participating R1 result ≤35 s old at issuance)"):
> `0 ≤ (valid_until_monotonic_ns − 21_600_000_000_000) − r1_batch_finished_monotonic_ns ≤ 600_000_000_000`
> with both endpoints from `context.clock.monotonic_ns()` (the clock every
> consumer tests `valid_until_monotonic_ns` against). Clock: ordinary
> monotonic (`time.monotonic_ns`, `CLOCK_UPTIME_RAW` on Darwin) — NOT
> `CLOCK_MONOTONIC_RAW`, which stays reserved for the anchor physics.
> Constant provenance: the governed worst-case wait between R1 and the
> stamp is eleven `_fresh_probe` sites × `_PROBE_TIMEOUT_SECONDS = 45`
> (`:54`) = 495 s (§6.3's AST census); 105 s is allowed for the
> intervening derivers' ungoverned filesystem/git work; the sum equals the
> module's existing `_MIN_IDLE_NS = 600 s` (`:51`). The bound is a
> liveness/hang detector and is labelled so in code; it is NOT a
> metrology bound (the drift budget and the two 5 ms anchor gates carry
> that). A successful path is strictly below every probe ceiling, so the
> bound cannot false-refuse a healthy night; it refuses a T-0 authoring
> that stalled ≥10 min after its reference batch, which is itself a
> readiness anomaly.

Rejected alternatives, with grounds: §6.3 option 1 (stamp at R1) —
back-dates nine volatile 20-minute rows before they are derived; option
2 (reorder rows) — registry-order churn on the mint path before the
night; option 4 (strike outright) — loses the only cap on R1 age at
issuance and hence at consumption (the horizon is anchored at the stamp,
not at R1); the refuter's 495 s — leaves zero allowance for ungoverned
work and could refuse a slow-but-healthy path; a RAW-typed bound — needs
a third stamp and refuses on a nap (refuter (a), accepted).

**Enforcement:** `arm_readiness.py` `_predicate_passes` clock branch
(`:6339-6341`) gains the `≤ 600_000_000_000` conjunct; issuance already
runs it (`arm_readiness_evidence_t0.py:2340`), so producer refusal is via
the registered `evidence_author_t0_predicate_refused` — no new reason
code, so no REASON_CODE_COVERAGE delta. Regressions: boundary controls
600 s + 1 ns refuses, 600 s − 1 ns passes, at both the issuance and the
arm site. Update the `:6336-6338` comment and the §6.3 "COLD-GATE-PENDING"
disposition to cite this file.

**Recorded limitations (MATERIAL, not blocking):** (L1) the ordinary
clock is sleep-blind, so a sleep between R1 and the stamp is invisible to
this bound — the same limitation D-150's 6 h horizon already carries on
the same clock; this ruling does not widen it. (L2) The refuter's
observation that ONE stamp dates all fifteen rows, understating volatile
20-minute rows' age by up to the derivation elapsed time, is a real
finding NOT presented in the packet; it is referred to the magistrate as
its own item (candidate cure: per-row `valid_until` from each row's own
derivation completion, batched post-`_v4` with T0-CLOCK-ROW-RENAME-01 as
a coupled registry change). Not ruled here.

**Where recorded:** the T-0 ruling file gains a dated "Horizon — AMENDED
by cold gate 2026-08-28" line pointing here (never edited in place); the
new decision-log entry cites it; PR #212's §6.3 disposition line is
updated by the implementing stream.

---

## Item 4 — evidence-path rulings only after a seat has executed the path (D-160 R-5)

**Refuter's strongest objection (verbatim):**

> R-5 is a pious exhortation, and the proof is that the document promulgating it violated it twice within thirty hours. R-5 was written at `docs/process_traces/2026-08-27-t26/smoke-corpus-consult/04-MAGISTRATE-RULING.md:80-83`; the addendum at `:88-99` records that the same ruling's own R-3 "reads as post-verdict" and was falsified by executed evidence — "refuter A's probe; director's bench check; `run_campaign.py` has zero references to the binding" — and the addendum at `:139-152` records that the previous addendum's "distinct analysis root" wording "was not executable on merged code," corrected as NR-14 against `run_campaign.py:4884-4920`, `:6364`, and `analysis_manifest_v3.py:3447-3504`. That second addendum ends, at `:153`, with the sentence "**Lesson (D-160 R-5 again): rule placement only after a seat has executed it.**" A rule whose own author restates it as a lesson learned, twice, in the same file, one and two days after ratifying it, has demonstrated its binding force is zero — and it failed at *addenda*, which the rule as drafted does not even mention. Ratifying it unchanged buys the project nothing it did not have on 2026-08-27, and buys it the specific harm of believing the class is now closed.

**Verdict: AMEND.** The two self-violations were verified at `:80-83` and
`:153`. As drafted the rule names no duty-bearer (blind seats do not rule;
the ruling seat is forbidden from the execution loop; a cold seat may read
code but has no worktree to execute in — charter §4), and it omits
addenda, where both violations occurred.

**Ruled text (replaces D-160 R-5):**

> A ruling or addendum whose dispositive premise asserts that an
> evidence-production path does or does not yield a named artifact is
> INADMISSIBLE unless the consult's custody directory carries, as a listed
> packet input, either (a) an execution record — exact argv, working-tree
> revision, exit code, produced-or-absent artifact path — or (b) a
> code-path proof citing the `file:line` at which the path refuses. The
> duty falls on whoever ASSEMBLES the packet or DRAFTS the addendum, never
> on the adjudicating seat; a seat that finds neither input returns the
> question UNRULED and the ruling is recorded `open (installs via …)` per
> item 1. Binds addenda and placement notes exactly as it binds the
> original ruling.

**Enforcement (mechanical, shape not truth):** one test in
`tests/test_docs_freshness.py` over
`docs/process_traces/<YYYY-MM-DD-*>/**/*MAGISTRATE-RULING*.md` whose
directory date is ≥ 2026-08-29 (prospective; the 15 existing files are
not retro-failed): any such file containing a `## Rulings`, `## RULED`,
or `## Addendum` heading must also contain a `## Executed evidence`
section with at least one fenced block holding a `$ ` argv line plus an
`exit` line, or a `file:line` citation. The test cannot verify the
transcript is real; its value is that absence is loud at CI time instead
of in the next day's addendum.

**Where recorded:** D-160's R-5 body text in the decision log (amended by
the new entry, never edited in place); the packet-input list in
`coldgate_charter.md` §4 — DEFERRED to charter v3 (registry item 4 already
queues that byte change; a charter edit re-digests and needs Ed
re-ratification, which should not ride this docs PR); the consult brief
template used for seats gains an "Executed:" block requirement. Not the
global council skill (a cold seat reads only the charter).

---

## Summary of verdicts

| Item | Verdict | Mechanism that makes it bind |
| --- | --- | --- |
| 1 | AMEND — reuse `open (installs via <TASK-ID>)` + kernel `kind: decision` hard start dependency; no new vocabulary | `gen_state.py --check` (existing, CI) + new status-vocabulary/`open`-row test in `tests/test_docs_freshness.py` |
| 2 | AMEND — PR template + advisory `gate-ledger` CI job; required-check and `N/A`/docs-only tier routed to Ed (E1, E2) | CI job (advisory until E1); D-072 self-merge conditioned on it green |
| 3 | AMEND — 5 s and 35 s STRUCK; `0 ≤ valid_until − 6 h − r1_batch_finished_monotonic_ns ≤ 600 s`, ordinary monotonic clock both sides, liveness bound, provenance 11 × 45 s + 105 s = `_MIN_IDLE_NS` | `_predicate_passes` conjunct at `arm_readiness.py:6339-6341`, run at issuance and arm; boundary regressions |
| 4 | AMEND — duty on packet assembler / addendum drafter; execution record or code-path proof as custody input; binds addenda | prospective `## Executed evidence` shape test in `tests/test_docs_freshness.py` |

Dissent recorded: none surviving between this instance and the refuter on
verdicts; on item 3's constant the refuter preferred 495 s or per-row
stamping, this instance rules 600 s now and refers per-row stamping
(L2) to the magistrate. The magistrate may overrule any item only by a
separately labelled written dissent presented to Ed (charter §5).

## Addendum 2026-09-02 — item 4 enforcement (dx cold gate B1)

> Selected files: (a) every `docs/process_traces/<dated-dir>/**/*MAGISTRATE-RULING*.md`
> whose dated directory component (`YYYY-MM-DD` prefix, any depth) is
> ≥ 2026-08-29, except the closed list
> `2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md` (predates the
> install; custodied files are not edited in place); (b) every `**/*RULING*.md`
> under a dated directory ≥ 2026-09-03, excluding `NEEDS-RULING-*` inputs.
> The selected set must be non-empty. Each selected file must contain a
> `## Executed evidence` heading whose section (to the next `^## `) satisfies
> ONE of: (1) a fenced block with a line matching `^\$ .+` AND a different line
> matching `^\s*(?:exit|EXIT|rc|exit code|exit status)[\s=:]+\d+\s*$`; or (2) a
> citation `[A-Za-z0-9_./-]+\.(?:py|sh|json|toml|ya?ml):\d+` whose path exists
> at HEAD. `.md:N` is a document pointer and satisfies nothing.

Replaces the Enforcement paragraph above (`:281-290` at 2d24ef70), which fired on zero files at install; the rule body is unchanged.

## Addendum 2026-09-02 — item 3 drift-envelope rationale

This addendum corrects item 3's stated metrology rationale; it moves no ruled
number. The `3.68 ppm × age` calculation states accumulated oscillator drift
only and implicitly assumes zero initial reference error. The predicate admits
`reference_bound_seconds <= 0.5 s`, so the guaranteed error envelope at age
`t` is instead

```text
reference_bound_seconds + 3.68e-6 × t
```

For Sol's admitted `reference_bound_seconds = 0.499 s` example, the envelope is
`0.499 + 3.68e-6 × 1830 = 0.5057344 s` (0.5057 s rounded) at the real-path
oldest-sample horizon, and
`0.499 + 3.68e-6 × (21_600 + 600 + 30) = 0.5808064 s` (0.5808 s rounded)
under the standalone 6 h + 600 s + 30 s envelope. At the admitted 0.5-second
ceiling, the corresponding guaranteed maxima are 0.5067344 s and 0.5818064 s.

This correction does not justify restoring the struck five-second issuance
bound: that bound was not the carrier of the initial reference error or the
oscillator-drift guarantee. The 600 s liveness bound, the 6 h horizon, the
[600 s, 3600 s] R0 span, the 30 s R1 batch bound, both 5 ms anchor gates, and
the standing fence are unchanged. Any change to a ruled number still requires
a cold gate.

### Correction to item 3's "cannot false-refuse a healthy night" premise (2026-09-02, magistrate; disclosed to Ed)

Item 3's text above says: "A successful path is strictly below every
probe ceiling, so the bound cannot false-refuse a healthy night." That
sentence is contradicted by the installed lane's own analysis
(`docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md`
§6.3.1): the fixed bounded subprocess subtotal between R1 completion and the
validity-origin stamp is 495 s of governed probe waits plus 220 s of eleven
20 s git ceilings — 715 s, already above the ruled 600 s before untimed
startup, I/O, hashing and scans. The ruled number (600 s), its inclusive
`<=`, the liveness labelling and the clock typing are NOT changed by this
correction: the premise that is withdrawn is the safety claim, not the
bound. What replaces it is an obligation, carried by kernel row
`T0-LIVENESS-BOUND-EMPIRICAL-01`: no retained receipt yet carries both
stamps, so the real R1→stamp interval is unmeasured; a refusal on this
conjunct in a real night is a fail-closed false refusal to be measured and
brought back to a cold gate, never relaxed in place. Found by the Opus 5
counter-review at gate item 6 (trace `2026-09-02-t26-item-3/17`, F-9).
