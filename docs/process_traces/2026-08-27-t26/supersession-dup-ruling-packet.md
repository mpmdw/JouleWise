# SUPERSESSION-DUP-REFUSAL-01 — ruling packet (T26 stream S6, phase 1)

- Date: 2026-08-26
- Stream: `s6-supersession-dup`, branch `fix/supersession-dup-refusal-01`
- Base: `origin/main` @ `51ed8817`
- Prepared by: Opus lieutenant (stream director), from one Sol xhigh read-only
  design seat plus the lieutenant's own verification of every load-bearing
  claim against the code.
- Status: **NO IMPLEMENTATION. Awaiting magistrate ruling.** The kernel row's
  first acceptance item is "the write-time refusal ruling is recorded in the
  decision log **before** any implementation".

Sol seat artifact (untracked, out-of-repo):
`…/scratchpad/t26/s6/sol-design-seat.md` (status OK, genre `review`,
completion `complete`, 3 findings: 1 blocker, 2 should-fix).

---

## 0. What is actually broken (verified, with file:line)

The recorder is `scripts/run_campaign.py::_run_record_supersession_locked`
(`scripts/run_campaign.py:5340`). Under the held `campaign.lock` it builds one
`campaign_occurrence_supersession` row and appends it
(`scripts/run_campaign.py:5451-5468`). It never looks for a row it already
wrote for the same bundle.

Two facts make the re-run pathological rather than harmless:

1. **A re-run cannot be byte-identical.** `utc_timestamp()` is stamped into the
   row (`scripts/run_campaign.py:5455`) and `entry_sha256` is computed over
   every field except itself (`joulewise/whole_window.py:2269-2272`). Identical
   operator inputs therefore produce a *different* row with a *different*
   digest. **Consequence for the option space: "same-bytes re-run is
   idempotent" is not literally available.** It can only ever mean "same
   semantic content modulo `timestamp`/`entry_sha256`".
2. **Two rows for one bundle void membership, in two different consumers.**
   - Cooldown join: `joulewise/analysis_engine/inputs.py:2337-2368` selects
     supersessions by `bundle_id` and only resolves when
     `len(bundle_supersessions) == 1`; otherwise it writes the refusal
     payload. (It does not reach `supersession_selected_occurrence_identity`,
     whose own `len(candidates) != 1 → None` guard sits at
     `joulewise/whole_window.py:2836-2842`.)
   - Whole-window membership: `_resolve_ordinary_occurrence`
     (`scripts/run_campaign.py:4784`) → `_matching_supersession`
     (`scripts/run_campaign.py:4766-4782`) returns a row only when exactly one
     entry matches on `(bundle_id, campaign_policy_sha256,
     selected_occurrence, superseded_occurrences)`; two identical-content rows
     give two matches → `None` → `unresolved`.

So the immediate double-run is fail-closed in both consumers — the corpus is
not silently mis-selected, it is destroyed for claim use. That is the defect
D-086 named (`docs/decision_log.md:5427-5430`) and the reason the standing
fence says "run the supersession recorder exactly once per member".

**Newly surfaced by this seat (not in D-086), verified:** a *later third
occurrence* creates a genuine cross-consumer **divergence**, not a shared
refusal. If a member is superseded once (row R1 naming `{o1 → o2}`) and later
a third occurrence appears, a second row R2 naming `{o1, o2 → o3}` is
constructible and R1 stays *valid* — validation binds R1's own manifests,
present bundle, quarantine bytes, reason, root and hash, never the current
complete occurrence set (`joulewise/whole_window.py:2638-2708`). Then:
whole-window membership **selects** (only R2 matches the expanded declared
set), while the cooldown join **refuses** (`len(bundle_supersessions) == 2`).
One consumer passes and one refuses on the same bytes. This is a latent
soundness asymmetry that write-time refusal *prevents from being created* but
does not *cure* for any log written by an older recorder or by hand.

**Reachable-state finding.** No campaign log reachable on this machine
contains a single supersession row: all seven under
`/Users/edr/code/JouleWise/runs/` and the one under
`/Users/edr/JouleWise-backup/runs/` return zero matches for
`campaign_occurrence_supersession`. `runs/` and `ci-runs/` are gitignored, so
nothing is tracked in git either. The real Window B/C corpora D-086 was
diagnosed against (slots `b03-b2`, `b09-b2`) are on operator-held storage that
is **not attached**. The "historical duplicates" question therefore cannot be
settled by inspecting bytes; it must be settled as policy plus a detection
procedure.

**No contract owner.** `rg` over `docs/contracts/` finds nothing owning the
supersession record schema or a recorder refusal vocabulary. The schema
constant lives in code (`joulewise/whole_window.py:87-89`); the policy lives
in the decision log. Nothing should be promoted to a contract by side effect.

---

## 1. Axis A — re-run semantics

| Option | Behaviour | Concrete failure mode |
|---|---|---|
| **A1** | Any recognizable same-`bundle_id` row already in the target log ⇒ refuse, before construction and before quarantine reads. | A member whose *selected* occurrence later fails cannot receive a second supersession in the same root; the operator must lose the member or recollect under a fresh root. This is a real in-window cost (see §5, Q1). |
| **A2** | Refuse on different semantic content; exit 0 without appending when content matches modulo `timestamp`/`entry_sha256`. | The operator cannot distinguish "my first write succeeded and I lost the output" from "this invocation recorded the custody action" — a silent success is the worst answer for a custody tool. It also makes `reason` and quarantine-hash equality policy-bearing comparisons, and it contradicts the kernel row's acceptance wording ("a second recorder invocation for the same member **refuses**", `docs/process/state_kernel.json:3657-3668`). |
| **A3** | Status quo: append regardless. | The defect. One stray shell retry appends a second row and voids the member. |
| **A4** | Chained successor supersession (R2 declares R1 as predecessor). | v1 carries exactly one quarantine object and neither consumer understands predecessor chains; this is a schema + two-consumer contract expansion, not a write-time guard. |

**Sol's recommendation: A1.** Compare only three things, and only against the
rows already loaded from the *target log* inside the held lock
(`load_campaign_log_rows` at `scripts/run_campaign.py:5359`): (i) is the row
recognizable (exact `record_type` **or** exact `schema_version`, matching the
reader at `joulewise/whole_window.py:2742-2752`); (ii) does its `bundle_id`
equal the CLI bundle id; (iii) is it in this log. Do **not** construct the
proposed row first, and do **not** require the existing row to validate — a
recognizable row that is present but *invalid* must still refuse, because an
invalid competing disposition is exactly what must not be laundered by
appending a second one. A recognizable supersession row with no usable
`bundle_id` refuses globally, mirroring the reader's existing fail-closed
branch (`joulewise/whole_window.py:2782-2793`).

**Lieutenant recommendation: A1, unchanged.** I add one reason Sol did not:
A2's equality test would have to decide whether a *changed `reason` string*
is "the same action". It obviously is not — the reason field is the operator's
custody testimony — so A2 collapses toward A1 for every case anyone cares
about while adding a comparison surface that can be got wrong. A1 is strictly
smaller and strictly louder.

## 2. Axis B — the uniqueness key

| Key | What it permits | What breaks |
|---|---|---|
| **`bundle_id` within the target log** | Nothing extra. | Over-blocks a deliberately shared log holding the same bundle id for independent roots/policies — but such a log already breaks both consumers, which filter by `bundle_id` alone. |
| `(runs_root, bundle_id)` | A second same-id row written against another root. | The raw reader still groups by `bundle_id` (`inputs.py:2337-2344`), so the cooldown join still sees two and refuses; root mismatch also makes the foreign row invalid (`whole_window.py:2643-2660`), which drives `_resolve_ordinary_occurrence` to `ambiguous` (`run_campaign.py:4807-4817`). Strictly worse. |
| `(campaign_policy_sha256, bundle_id)` | A policy change licenses another row. | Cooldown ambiguity is not policy-scoped; same failure. |
| declared-occurrence identity set | The later-third-occurrence shape. | Produces exactly the §0 cross-consumer divergence, and promotes occurrence-set normalization into the uniqueness contract. |

**Both Sol and lieutenant recommend `bundle_id` within one target log** — it
is the only key that matches what both consumers actually group on.

## 3. Axis C — the refusal surface

Precedent in this repo, verified: refusal vocabularies are *registered*
lower-snake wire strings. `joulewise/determinism_gate.py:30-53` holds the
`REASON_* = "lower_snake"` constant block; `LaunchLineageError`
(`joulewise/arm_readiness.py:1079-1086`) is a `ValueError` subclass carrying
`.reason_code`, validated against a frozenset of registered codes, and
`main()` prints `error: {reason_code}: {message}` and returns 2
(`scripts/run_campaign.py:8139-8144`). The operator-facing refusal table in
`docs/phase_2/window_runbook.md:1742-1767` lists exactly those wire strings.

**Sol's recommendation:** exception `SupersessionRecorderError(ValueError)`;
constant `REASON_CAMPAIGN_OCCURRENCE_SUPERSESSION_ALREADY_RECORDED`; wire value
`campaign_occurrence_supersession_already_recorded`; exit 2; stderr naming the
existing row's recorded `timestamp` and `entry_sha256` (labelled *recorded*,
not *validated*, and JSON-escaped) plus the count and the log path; no stdout;
the Python API raises, only the CLI converts.

**Lieutenant recommendation: adopt, with two corrections.**
1. **Exit 2 is not a delta.** `main()`'s generic `except Exception` already
   returns 2 for every `ValueError` the recorder raises today
   (`scripts/run_campaign.py:8145-8147`). The actual value delivered is the
   machine-readable `reason_code:` prefix and the runbook table row — the
   ruling should say so rather than appear to buy a new exit status.
2. **Follow the `LaunchLineageError` shape exactly**: the new exception
   carries `.reason_code` validated against a registered frozenset
   (`SUPERSESSION_RECORDER_REASON_CODES`), and `main()`'s existing
   `except LaunchLineageError` clause widens to a tuple rather than gaining a
   second bespoke handler. That keeps one printing path for all registered
   refusals. Sol's naming otherwise fits the table convention (compare
   `whole_window_campaign_membership_unresolved`) and I would not shorten it.

## 4. Axis D — historical repair

**(i) Obligation.** No blanket byte-repair obligation is owed; a *detection
and disposition* obligation is. Nothing reachable on this machine holds a
supersession row at all (§0), so there is presently nothing to repair; the
open exposure is entirely on unattached operator storage.

**(ii) Remedy when a duplicate pair is found.**
- **(a) Leave the bytes, let the existing refusal stand** — compatible with an
  append-only, hash-bound chain and with D-086's anti-laundering property; the
  corpus is simply not claim-bearing until a separately governed action.
- **(b) Append a governed retraction record** — conceivable only if it
  hash-binds the exact retracted entries, preserves every byte, and cannot
  select an outcome-favourable record. It is a **new record type plus changes
  to both consumers plus a new truth table**, i.e. a larger contract change
  than this row.
- **(c) Rewrite the log** — destroys operative append-only history and erases
  evidence of a competing operator disposition. An out-of-band custody note
  does not repair that.

**Sol and lieutenant both recommend (a) for this row**, with (b) available as
a *separate* ruling if a real corpus ever turns out to be worth recovering,
and (c) rejected outright.

**(iii) Detection.** Sol supplied a read-only per-bundle scan built on
`supersession_entry_validation_results`, exiting 0 clean / 1 duplicates / 2
unreadable-or-unidentifiable, to be documented in
`docs/phase_2/window_runbook.md` §11 beside the recorder command. It is in the
seat artifact and should be transcribed verbatim by the implementation
session.

**This matters more than it looks.** D-093's existing supersession audit
compares *totals* — `raw_count == validated_count`
(`joulewise/analysis_engine/inputs.py:1349-1372`) — so two **valid** rows for
one bundle report `2 raw / 2 valid` and audit **clean**. The existing audit is
blind to precisely the defect under ruling. Any detection procedure must group
by `bundle_id`.

## 5. Axis E — blast radius, and what a real regression must assert

Recommended blast radius (Sol's E2, lieutenant concurs): the ruling, the
recorder, one recorder regression, the runbook, and row closure. Specifically:

- `docs/decision_log.md` — the ruling itself, and it must explicitly discharge
  D-086's "Revisit when: … the recorder gains write-time refusal (which
  changes what the join can assume about its inputs)"
  (`docs/decision_log.md:5432-5434`). **Magistrate-authored: the lieutenant is
  forbidden to write decision-log rulings.** Next free id is **D-156**
  (`## D-153`, then `## D-155`; there is no `D-154` anywhere in the file —
  an unexplained gap, flagged, not touched).
- `scripts/run_campaign.py` — registered reason code + exception, the
  pre-construction scan inside the held lock, `--record-supersession` help
  text, widened `except` tuple (`:725-735`, `:5319-5468`, `:8139-8144`).
- `tests/test_run_campaign.py` — the defect-shaped regression, adjacent to the
  existing real-recorder tests (`:8920-9001`, `:9249-9347`).
- `docs/phase_2/window_runbook.md` — refusal-table row, "once per bundle per
  target log", the escape hatch the magistrate rules in Q1, and the detection
  scan (`:1742-1767`, `:1808-1821`).
- `docs/process/state_kernel.json` + `TASK_QUEUE.md` — close the row and
  retire the temporary fence (per T26 closure convention: delete the kernel
  row, add a Completed-Queue-Items line, regenerate).
- **No consumer change.** The exact-one behaviour in `whole_window.py` and
  `analysis_engine/inputs.py` stays; its existing regressions re-run as
  preservation coverage (`tests/test_analysis_integration.py:5867-5918`,
  `:6016-6127`).

**The regression must not be tautological.** It must: build one real recorder
fixture with no mocking of the duplicate detector or the validator; invoke
once and assert success; snapshot the complete log bytes; invoke again with
identical arguments; assert the registered reason code, exit 2, the exact
operator text, empty stdout, and **byte-identical log contents with exactly
one supersession row**; then, separately, corrupt the existing row while
keeping its `bundle_id` and assert the same no-append refusal. Deleting the
guard must turn it red. Mocking a helper to report a duplicate and asserting
`ValueError` proves nothing.

---

## 6. The pre-computed arithmetic on the one question that costs something

Q1 below is the only residual with a real operational price, so here is the
math rather than the gesture.

The runbook prescribes "rerun the exact member, and record supersession" as
the operator recovery for at least three distinct in-window symptoms —
`anchor_fallback_member_unusable`, `incomplete_existing`/occupied run id, and
the quarantine-and-replace flow (`docs/phase_2/window_runbook.md:1754`,
`:1766`, `:1800-1821`). A member failing **twice** during one quiet-Mac window
is therefore not exotic. Under A1 the second failure hits a hard refusal at
recorder time, and the operator's only sound moves are to lose the member or
to start a fresh root — expensive against a scarce hardware window.

The tempting cheap fix is a consumer widening: let the cooldown join accept
exactly one row whose named occurrence set *equals* the declared set and
ignore rows naming a strict subset. That would make both consumers agree and
would cost about four lines. **It should nonetheless be rejected, and the
reason is already ruled in this repo:** ignoring the older, narrower record in
favour of the newer, wider one is latest-wins, and the operator vocabulary
already refuses latest-wins by name — `whole_window_verdict_conflict`:
"Latest-wins is forbidden; preserve the conflict"
(`docs/phase_2/window_runbook.md:1759`). Adopting it for supersessions would
create precisely the laundering channel D-086's anti-laundering clause exists
to close: append a wider record, have the narrower competing disposition
ignored.

That leaves same-root double-failure recovery genuinely unsupported unless a
predecessor-bound chained supersession (Axis A4 / option B in Q1) is designed
and ruled as its own row. **Note that A1 does not create this restriction —
the standing D-086 fence already says "exactly once per member". A1 converts
an honour-system fence into a refusal, and converts a silent cross-consumer
divergence into a loud stop.** That is a strict improvement even if Q1 is
answered "unsupported".

---

## 7. RESIDUAL QUESTIONS FOR THE MAGISTRATE (verbatim)

> **Q1.** If an already-selected occurrence later fails, must recovery be
> **A: fresh root / non-claim disposition**, or **B: a separately ruled
> chained-supersession schema (new row)**? *(Sol recommends A for this row.
> Lieutenant recommends **A now, with B minted as a queued row** so the
> operational gap is on the record rather than discovered mid-window.
> A third option — **C: widen the cooldown join to ignore strict-subset
> rows** — is named only to be rejected: §6 shows it is latest-wins, which
> the runbook forbids by name.)*

> **Q2.** If an operator-held log contains historical duplicates, is the
> disposition **A: preserve and refuse**, **B: open a separate append-only
> retraction design**, or **C: authorize a custody-documented rewrite**?
> *(Sol: A; B may be considered separately; reject C. Lieutenant concurs
> exactly.)*

> **Q3.** Must the off-machine Window B/C scan be **A: mandatory before any
> future consumption of an operator-held corpus**, or **B: informational only
> when convenient**? *(Sol: A. Lieutenant: A, and note the scan is cheap,
> read-only, and — per §4(iii) — catches a case D-093's existing audit
> reports as clean.)*

> **Q4 (lieutenant-originated, not in Sol's list).** The later-third-occurrence
> **cross-consumer divergence** of §0 — whole-window membership selects while
> the cooldown join refuses, on identical bytes — is prevented going forward by
> A1 but is not cured for legacy or hand-edited logs. Is it **A: recorded as a
> named limitation in the D-156 ruling and left**, **B: minted as its own
> queued row**, or **C: in scope for this row**? *(Lieutenant recommends B —
> it is a consumer-contract question, and folding it in would break the
> "ruling-first, bounded" shape of A17. C is not recommended: it would put a
> fail-closed consumer change inside a write-time-guard PR.)*

> **Q5 (process).** Acceptance requires the ruling in the decision log
> **before** implementation, and the lieutenant is forbidden to author
> decision-log rulings. Confirm **D-156** as the id and that the magistrate
> authors the entry (or explicitly delegates the drafting of a text the
> magistrate then ratifies). Implementation stays blocked until it lands.

---

## 8. Lieutenant's own recommendation, in one block

Rule **A1** (unconditional refusal on any recognizable same-`bundle_id` row in
the target log, no validation requirement, checked before row construction),
keyed on **`bundle_id` within one target log**, surfaced as a **registered
reason code** `campaign_occurrence_supersession_already_recorded` raised
through a `.reason_code`-carrying `ValueError` subclass on the
`LaunchLineageError` pattern, naming the existing row's recorded timestamp and
digest. Owe **no byte repair**; owe a **per-`bundle_id` detection scan**
documented in runbook §11 and run before any operator-held corpus is consumed.
Keep the blast radius to ruling + recorder + one non-tautological regression +
runbook + row closure, with **no consumer change**, and mint the
chained-supersession gap (Q1) and the cross-consumer divergence (Q4) as their
own queued rows.

Everything above is verified against `origin/main` @ `51ed8817`; every
file:line in this packet was read by the lieutenant, not taken on the seat's
word.
