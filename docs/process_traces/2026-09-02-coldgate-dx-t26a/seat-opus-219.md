## Disclosure

**Charter digest.** `shasum -a 256 /Users/edr/code/JouleWise-wt-t26-a2/docs/process/coldgate_charter.md` → `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`. **Matches** the packet's expected value. Charter §3–§5 and §8 read (also §9, which is adjacent and bears directly on B1 — disclosed).

**Read set.** PACKET.md; `coldgate-dx/{189-luna-refute.md, 191-fix-brief.md, 207-opus-counter-review.md}`; `out/{209-luna-t26a-contract.md, 210-opus-t26a-exec.md}`; charter §3–§5, §8–§9; `COLD-GATE-RULING.md:45-110, 255-298`; in `-a2`: `tests/test_docs_freshness.py:95-140, 255-320`, `docs/process/state_kernel.json`, `docs/process/state_kernel.schema.json` (dependency `$defs` — cited by the ruling at :54-55, needed to rule B2's scope question), `scripts/gen_state.py:61-63, 178-195, 353-370`, `docs/decision_log.md` index rows only (D-110/D-150a/D-150b/D-170 status cells, by regex; no bodies); in `-dx` via `git show`: `check_paper_round7_artifacts.py` and `tests/test_paper_round7_artifacts.py` at `3f1677b7` and `2a6d3841`, `docs/paper/round7/fill-checklist.md`, `docs/paper/draft-v2-skeleton.md` (marker count only).

I did **not** read `191-sol-fix-report.md`, `198-terra-delta.md`, or the fence diff patch — my findings did not require them, and `191-fix-brief.md` is the controlling contract for round 1. I did not read README/RUN_STATE/TASK_QUEUE/orchestration/agent_playbook/any CLAUDE*.md/memory. **Contamination: none.** I wrote only under `scratchpad/coldopus/`; both worktrees untouched (`git status --short` in `-a2` and `-dx` unchanged by me).

**Two packet defects found before ruling (charter §6/§4 — "verify load-bearing claims against primary evidence, not the packet's paraphrase"):**

- **PD-1 (MATERIAL).** Packet **Fact F1** is false as to the committed bytes. It states `_decimal` at `3f1677b7:369-370` is `return value if isinstance(value, Decimal) else Decimal(str(value))`. The actual committed text is:
  ```
  369  def _decimal(value: Any) -> Decimal:
  370      if isinstance(value, bool) or not isinstance(value, (int, float, str)):
  371          raise ValueError(f"not a decimal scalar: {value!r}")
  372      return Decimal(str(value))
  ```
  Verified by probe: `_decimal(True)` → `RAISES ValueError: not a decimal scalar: True`. The same guard is present at `2a6d3841:357-360` — i.e. **pre**-round-1. F1 reproduces Opus 207 S1's quotation verbatim without re-verifying it; F1 is labelled "bench-verified by the magistrate." It was not. Consequence: the `bool` limb of S1's `_decimal` claim is **fabricated**, and the packet's A1 option (a) asks me to rule on coercions (`bool→int` at `_decimal`, `float→Decimal` rejection) that are respectively already cured and affirmatively required.
- **PD-2 (MATERIAL).** Packet B1 gives `171a-RULING-decode-identity.md` as an "e.g." of the glob miss. The real census is 30 post-cutoff `*RULING*.md` files, of which **29 would fail** a widened test at the ruled 2026-08-29 boundary. The packet's option (i) is therefore not a small widening; it is red on 29 of 30 rows on day one. Ruling on B1 without that number would be ruling on a materially incomplete packet. I supply it below rather than REFUSE, because I computed it from primary evidence inside the permitted set.

Neither defect requires REFUSE. Both change the answers.

---

## Clause enumeration (independent, before reading any interpretation)

### Item 1 — `COLD-GATE-RULING.md:45-110`

| # | Line | Verbatim operative text |
|---|---|---|
| **1-V** | :51 | "**Verdict: AMEND.**" |
| **1-R1** | :67-71 | "A decision-log entry that carries an implementation clause … is recorded with index status **`open (installs via <TASK-ID>)`** — `open` is the existing documented status, 'criteria defined, evidence pending' — naming the state-kernel task that carries the uninstalled clauses." |
| **1-R2** | :71-75 | "In the same commit, that kernel task gains a dependency `{kind: "decision", target: "D-NNN", strength: "hard", scope: "start", state: "pending", evidence: null, required: "<the clause, one line>"}` on every task the clause gates" |
| **1-R3** | :75-76 | "(at minimum the transaction task when the clause touches a transaction)." |
| **1-R4** | :76-79 | "The dependency moves to `satisfied` only with an `evidence` pointer at the repo-relative path (+ anchor) of the regression that FAILS when the ruled value is absent at the producer, **and** the index status moves to `accepted`/`adopted` with the installing PR or commit named in the entry body." |
| **1-R5** | :80-81 | "Nothing selects while the dependency is pending (kernel invariant 3)." |
| **1-R6** | :81-83 | "Binds prospectively from this ruling's merge; the S9 SHORTLIST items marked 'gates the mint' or 'gates windows' are registered under it in the ruling's implementation commit — not all 460 clauses" |
| **1-R7** | :83-86 | "(the refuter's 'red on every row' objection is **accepted as a scoping constraint**, and the S9 census remains the truth check the kernel cannot perform)." |
| **1-E1** | :88-90 | "(i) existing — `gen_state.py --check` in CI refuses evidence-free `satisfied` and blocks selection on pending hard start" |
| **1-E2a** | :90-94 | "(ii) new — one test … asserting every index Status cell's leading token is in the closed set `{accepted, adopted, ratified, open, proposed, superseded, recorded, executed, adjudicated}`" |
| **1-E2b** | :94-97 | "every `open` cell matches `open \(installs via ([A-Z0-9-]+)\)` with that id present in `state_kernel.json` `tasks` **AND that task carrying a `kind: decision` dependency targeting the row's D-id**" |
| **1-E2c** | :97-98 | "fix the `D-\d{3}` regex to `D-\d{3}[a-z]?` in the same change" |
| **1-E3** | :99-101 | "This is a shape check; it proves the pointer exists, not that the test asserts the ruled thing. That residual is by design the S9-shape sweep's job" |

**Internal contradiction, found on first reading and before any report:** **1-R2 + 1-R3** place the dependency on **the gated tasks** (the parenthetical names *the transaction task* as a minimum member of "every task the clause gates" — the transaction task is not the installer), and **1-R5** confirms the purpose is to block *gated* work. **1-E2b** demands the **installing** task carry it. Under `gen_state.py:357-366` a `scope: start` pending hard dep forces `blocked`, so 1-E2b read with 1-R2's literal `scope: "start"` makes the installer unselectable and the rule self-defeating. The two clauses are jointly unsatisfiable **only** if the installer's dep must be `scope: start`. Nothing in 1-E2b says it must.

### Item 4 — `COLD-GATE-RULING.md:255-298`

| # | Line | Verbatim operative text |
|---|---|---|
| **4-V** | :261 | "**Verdict: AMEND.**" |
| **4-R1** | :269-274 | "A ruling or addendum **whose dispositive premise asserts that an evidence-production path does or does not yield a named artifact** is INADMISSIBLE unless the consult's custody directory carries, as a listed packet input, either (a) an execution record — exact argv, working-tree revision, exit code, produced-or-absent artifact path — or (b) a code-path proof citing the `file:line` at which the path refuses." |
| **4-R2** | :274-277 | "The duty falls on whoever ASSEMBLES the packet or DRAFTS the addendum, never on the adjudicating seat; a seat that finds neither input returns the question UNRULED and the ruling is recorded `open (installs via …)` per item 1." |
| **4-R3** | :278-279 | "Binds addenda and placement notes exactly as it binds the original ruling." |
| **4-E1** | :281-284 | "**Enforcement (mechanical, shape not truth):** one test in `tests/test_docs_freshness.py` over `docs/process_traces/<YYYY-MM-DD-*>/**/*MAGISTRATE-RULING*.md` whose directory date is ≥ 2026-08-29" |
| **4-E2** | :284-285 | "**(prospective; the 15 existing files are not retro-failed)**" |
| **4-E3** | :285-288 | "any such file containing a `## Rulings`, `## RULED`, or `## Addendum` heading must also contain a `## Executed evidence` section with at least one fenced block holding a `$ ` argv line plus an `exit` line, or a `file:line` citation." |
| **4-E4** | :288-290 | "The test cannot verify the transcript is real; its value is that absence is loud at CI time instead of in the next day's addendum." |

**Structural observation, independent of any report:** 4-R1's trigger is a **semantic** predicate ("whose dispositive premise asserts that an evidence-production path…") that no regex can evaluate. 4-E1/4-E3 are an admitted **proxy** for it, self-labelled "shape not truth" (4-E1, 4-E4). The ruled *text* (4-R1–R3) and the ruled *proxy* (4-E1–E4) are therefore distinct instruments with different amendability, and charter §9 sentence 2 draws exactly that line.

---

## Clause-by-clause: does `2d24ef70` satisfy item 1 and item 4 literally, in spirit, or contradict?

| Clause | Installed code | Verdict |
|---|---|---|
| 1-E2a | `test_decision_index_vocabulary_is_closed` (`:255-258`); Opus M5 killed | **Literal** ✔ |
| 1-E2c | `_decision_index_rows` regex `D-\d{3}[a-z]?` (`:95`); M5 iterates D-150c | **Literal** ✔ |
| 1-E2b limb 1 ("that id present in `tasks`") | `:277-281` `assertIn(task_id, tasks)` | **Literal** ✔ |
| **1-E2b limb 2 ("**that task** carrying a `kind: decision` dependency targeting the row's D-id")** | `:282-294` scans **all** tasks and asserts the list is non-empty | **CONTRADICTS.** The ruled subject is *that task*; the code's subject is *any task*. Not "spirit only" — the ruled sentence's grammatical subject is discarded. |
| 1-R2/1-R3 (placement) | D-170 dep on `V5-TRANSACTION-01`, `scope: start`, `strength: hard`, `state: pending`, `evidence: null` | **Literal** ✔ — see B2 |
| 1-R5 | `V5-TRANSACTION-01.status == "blocked"` (verified) under `gen_state.py:357-366` | **Literal** ✔ |
| 1-R4 (dep-satisfied ⟺ status-adopted coupling) | **nothing** enforces the coupling; M6c survives | **CONTRADICTS** — see B3 |
| 1-R6 (S9 shortlist registered in the implementation commit) | absent from `state_kernel.json` | **CONTRADICTS** (luna F1; B4) |
| 4-E1 glob | `_dated_process_trace_files("*/**/*MAGISTRATE-RULING*.md", "2026-08-29")` (`:110-111`) | **Literal** ✔ (and that is the problem) |
| 4-E2 date | `dated_directory[:10] >= minimum_date` (`:105`); M9/M9b/M9c killed at the boundary | **Literal** ✔ |
| 4-E3 heading trigger | `^## (?:Rulings|RULED|Addendum)(?:\s.*)?$` (`:299-301`) | **Literal** ✔ |
| 4-E3 evidence shape | `_has_executed_evidence` (`:114-134`), `citation or execution_record` | **Literal** ✔ (the disjunction is ruled: "or a `file:line` citation") |
| **4-R1 (the ruled duty itself)** | fires on **0 files**; my census: 0 of 2 post-cutoff `*MAGISTRATE-RULING*` files trigger; 26 post-cutoff `*-RULING-*` files are outside the glob entirely | **NEITHER.** Literal compliance with 4-E1/4-E3 yields **zero** compliance with 4-R1. This is the rare case where "satisfies literally" and "contradicts in spirit" are simultaneously true, and the literal limb is worthless. |

---

# A1 — is Opus 207 S1 the same defect class, and what is the cure?

## Verdict: **AMEND** — same class at ONE of the two named sites; reject cure (a) as over-engineering, reject cure (b) as the thing that produced round 2; adopt (c) below. Severity **MATERIAL** (not BLOCKER).

### The class, named precisely

Round 1's defect (`191-fix-brief.md` B2 = `R7F-EXACT-INTEGER-001`; luna 189 :36-37) is:

> **A renderer converts an artifact scalar of the wrong Python type into the expected type by an implicit or lossy cast, so a re-issued artifact whose field type drifted still renders the registry-pinned literal and the fence reports agreement.** Instance: `int(15.9) → 15`.

Note the two limbs — *coercion in the read path*, and *pinned literal still renders*. Both are required for the defect to bite; a coercion that changes the rendered string is caught by the existing pin.

**Site-by-site against that class:**

- **`_decimal` accepts `str` (`:370`) — SAME CLASS, confirmed.** `Decimal(str("0.61"))` renders identically to the pinned literal. Both limbs present. Probe: `_decimal('4.05') -> Decimal('4.05')`.
- **`_decimal` accepts `float` — NOT a defect. Affirmatively required.** Every percentage and millisecond supplier field arrives from JSON as a float; `AQ#summary...median_pct` is `0.607832`. Rejecting `float→Decimal` would refuse the entire registry. **Packet option (a) lists `float→Decimal` among "the rejected coercions." I reject that limb outright** — implementing it fails the fence on today's artifacts.
- **`_decimal` accepts `bool` — FALSE. Already cured, and cured *before* round 1.** Probe: `_decimal(True) -> RAISES ValueError`. Present at `2a6d3841:357-360`. **Opus 207 S1 and packet F1 are both wrong here.** Likewise `bool→int` at `_exact_int` (`:386`, probe `_exact_int(True) -> RAISES`). **Two of the four coercions option (a) asks me to close are already closed; a third must stay open.**
- **`_comparison` `expected == observed` at `:156`, as used by `check_gates` (`:505`, expected literal `True`) — ADJACENT CLASS, real.** Probe: `_comparison(expected=True, observed=1) -> match=True`; `observed=1.0 -> match=True`. Mechanism differs (Python's numeric tower inside the *comparison predicate*, not a cast inside a *renderer*), consequence is identical (wrong-typed value passes as the pin). I rule it **the same class at the outcome level, a distinct mechanism at the site level** — which matters, because it means a renderer-only cure does not reach it.

**So: rule-11 trigger 1 (second fix round on the same defect) is correctly convened, on the `_decimal`-`str` site alone.** But I record a finding the packet does not: **round 1 did not fail to execute its contract.** `191-fix-brief.md` B2 scoped the cure verbatim to "EVERY integer, count, flip, control, and derived/refused branch." The `Decimal` renderers and `check_gates` were never in that scope. This is **contract under-scoping at brief-writing time, not seat non-compliance** — which is why cure (b) recurs and why the cure must be scoped by *class*, not by *site*.

### Ruled cure — option (c)

**Reject (a).** Under D-161 (operator is not the adversary; the fence exists against re-issued artifacts and honest producer drift), a new typed-field-resolver abstraction interposed between every renderer and every artifact read is over-engineering: it is a refactor of the whole read path to close two live holes, two of whose four enumerated coercions are already closed and one of which must remain open. It also fails the bench-vs-session threshold — the closing edit is under ten lines.

**Reject (b).** Site-by-site patching at `:370` and `:155` is precisely what round 1 did at one site, and it is why this gate is sitting. A cure that closes named sites leaves the next sibling for round 3, and charter §9 sentence 2 ("two consecutive rounds failing with the same signature… the next spend is a consult or redesign, not round three") makes a third same-shape round require explicit justification I am not granting in advance.

**Adopt (c): make the two *primitives* total, and make the comparison predicate type-strict once, globally.**

1. **`_decimal` (`:369-372`)** — drop `str` from the accepted tuple:
   ```python
   def _decimal(value: Any) -> Decimal:
       if isinstance(value, bool) or not isinstance(value, (int, float)):
           raise ValueError(f"not a decimal scalar: {value!r}")
       return Decimal(str(value))
   ```
   Keep `float`. Keep the existing `bool` guard.
2. **`_comparison` (`:155-156`)** — make the predicate type-strict, which closes the equality limb at **every present and future call site** rather than at `check_gates` only:
   ```python
   def _comparison(label: str, expected: Any, observed: Any) -> Comparison:
       match = type(expected) is type(observed) and expected == observed
       return Comparison(label, str(expected), str(observed), match)
   ```
   **I audited every call site at `3f1677b7` against this change** — `:303, :305, :307, :309, :311, :325, :328, :360, :364, :486, :489, :505, :613` plus the identity-row site in `check_file_pins` — and it alters the outcome at **exactly one**: `:505`, the intended bite. `:305` (`int` pin vs `"MISSING …"` str) is already a mismatch today and stays one. `check_figure` builds `Comparison` directly (`:570-577`) and is unaffected.
   *Do not* substitute `str(expected) == str(observed)`: that re-introduces the very conflation being cured (`Decimal("1.0")` vs `"1.0"` would match).
3. **Do NOT add `_exact_bool` or a `check_gates`-local patch.** Step 2 subsumes it. `check_gates` already passes the literal `True` (`:505`); with a type-strict predicate, `1`, `1.0`, and `"true"` all become mismatches with no edit to `check_gates` at all.
4. **One table-driven regression**, over the primitives × the rejected inputs, defect-shaped per the mutation-cure counterfactual rule (a scratch artifact copy with an updated registry digest/size, *not* today's committed artifact):
   | kind | accepts | must refuse |
   |---|---|---|
   | `_exact_int` | `int` | `4.0`, `"4"`, `True` |
   | `_decimal` | `int`, `float` | `"4.05"`, `True`, `Decimal("4.05")`, `None` |
   | `_comparison` | same-type equal | `(True, 1)`, `(True, 1.0)`, `(1, 1.0)` |

**Acceptance obligation on the magistrate (not delegable):** after the change, the full replay tail must still read `R7F COMPARED n / MISMATCHES 0` with `n` unchanged or the delta explained. I audited call sites in the **committed** bytes; Sol 216's in-flight `fix-dx-2a` adds ~110 lines to this file that I have not read and must not read, so the call-site audit must be re-run against the merged head.

### Biting counterfactuals (per kind)

- **`_decimal`/`str`:** re-issue the AQ artifact with `"delta_v3_vs_stored_relative": {"median_pct": "0.61"}` (string, pre-rounded by a drifted serializer) in a scratch copy with the registry digest/size updated to match. Today: `_signed(_decimal("0.61"), 2)` → `"+0.61 %"` → DX-027 **matches**, `MISMATCHES 0`. The paper's number is now sourced from a pre-rounded string, and the fence certifies the raw statistic. After the cure: **REFUSED**, naming DX-027's supplier field.
- **`check_gates`/bool:** re-issue XD with `"calibration_gate.b_fiducial_s_matches_exactly": 1` (the shape a `numpy.bool_` takes through a serializer that does not special-case it — honest producer drift, squarely inside D-161's threat model). Today: probe-confirmed `match=True`, gate passes. After the cure: **MISMATCH**, exit 2.
- **`_exact_int` (regression only, already cured):** `population_size: 15.9` → refuses. Retain as the control that proves the table exercises a killed mutation alongside two live ones.
- **`float→Decimal` (negative control, must NOT refuse):** `median_pct: 0.607832` must continue to render `+0.61 %` and pass. Include it in the table so a future round does not "close" it.

### What A1 does NOT decide

Not whether `_decimal` should accept a `Decimal` (probe: it refuses one today — a latent inversion, not before me and not part of this class). Not Opus 207 B1/B2/S3/N1–N5 (dictated to Sol 216, expressly out of packet). Not whether the fence should validate artifact field *types against a schema* at load time — a strictly larger design that would subsume the primitives, and which I decline to rule on an unbriefed record. Not the merge disposition of the branch.

### Disagreement with the packet's framing

**Stated explicitly per charter §8.** (i) Packet F1's code quotation is not the committed text (PD-1). (ii) The packet asks me to rule a cure closing `bool→int` and `float→Decimal`; the first is already closed at both primitives and the second must stay open. (iii) The packet, following Opus 207, presents S1 as uncured *fallout* of round 1; the controlling document (`191-fix-brief.md` B2) shows those sites were never in round 1's scope. The distinction is load-bearing for rule 11: this is a **brief-scoping** failure, and the cure is to scope the next brief by class — which (c) does and (b) does not.

---

# A2 — do the placement census and the bare-prose scan belong in this PR?

## Verdict: **AMEND.** (i) census and (ii) prose scan → **kernel row at the fill stage**, not this PR. But **one non-vacuity obligation lands in this PR**, and it is not the one Opus proposed. Severity **MATERIAL**.

### Reasoning

The census and the scan are both **unrunnable against real input today**: `docs/paper/draft-v2-skeleton.md` carries **0** `[FILL:DX-` markers (F7, re-verified: `grep -c` → `0`), and the successor draft is not being filled. A census gated on a flag that is off, and a scan over prose that does not yet exist, are two more mechanisms whose first real execution is deferred — which is the identical shape as luna 209's own residual-risk note on the sibling clause-map test ("no eligible `*-impl.md` report dated 2026-09-03 or later, so its prospective path has not yet executed"). Landing them here buys motion, not coverage.

**I reject Opus S2's implicit premise that `check_skeleton_literals` is untested.** It is defect-shape tested: `tests/test_paper_round7_artifacts.py:198` `test_altered_successor_literal_is_refused` and `:203` `test_exact_successor_literal_is_accepted` both call it against synthetic marker text in both directions, plus `:155` against the real skeleton. The function bites. What is missing is **input**, not assertions — so no additional regression is owed in this PR, and I decline to order one.

**Nothing in the PR makes a false coverage claim, and I checked.** `fill-checklist.md:253-268` says of each DX row "Place only as `[FILL:DX-nnn]`; R7F checks the rendered literal" — a conditional that is true. `:24-25` describes R7F as an `R7F COMPARED n / MISMATCHES 0` census and does not claim placement coverage.

### The one thing that must land in this PR

The genuine hazard is not the missing mechanisms; it is that a check emitting **zero comparisons** is indistinguishable, in the `R7F COMPARED n / MISMATCHES 0` tail, from a check that verified sixteen placements. That is the identical failure this same session's subject B produced — `T26-RULING-INSTALL-01.acceptance` recording an Executed-evidence test as "present and mutation-killed" when it asserts on zero files (Opus F1, my census). **Same signature, two subjects, one session.** Charter §9 sentence 2 applies: the structural cure is to make vacuity *loud*, not to add a third deferred mechanism.

**Operative shape (this PR):**

1. `check_skeleton_literals` emits, unconditionally, one `Comparison` recording the placement count — label `"skeleton DX placements"`, expected `"≥ 1 per non-identity registered row (16)"`, observed `"0 of 16 placed"`, **`match=True` while the successor draft is unfilled**. It must appear in the census so `n` is never silent about coverage, and the operator reading the tail sees `0 of 16`.
2. The CLI tail gains one line when the placement count is zero: `R7F NOTE: 0 DX placements found; literal coverage is vacuous for this run.`
3. `fill-checklist.md` gains one line under the Round-7 artifact fence bullet (`:24-25`): "R7F verifies a DX literal only where a `[FILL:DX-nnn]` marker is placed. It does **not** verify that every registered row reaches the draft, and it does not detect a DX value typed as bare prose. Both are the filler's duty until `R7F-PLACEMENT-CENSUS-01` lands."
4. **No acceptance row anywhere may record R7F as covering placement.**

**Kernel row (fill stage), to register in this PR's commit:** `R7F-PLACEMENT-CENSUS-01`, blocked on the successor draft entering fill, with acceptance = (a) every non-identity registered DX row (16 at `3f1677b7`; the count is derived from the parsed registry, never hardcoded) appears ≥ 1 time as `[FILL:DX-nnn]`; (b) for each such row, its rendered literal does not occur in the draft outside a marker's governed span; (c) two defect-shaped regressions — delete one marker from a scratch draft → census FAILS naming the row; paste one row's rendered literal into scratch prose outside any marker → scan FAILS naming the row and the offending line.

### Biting counterfactual

**For the PR obligation:** delete every `[FILL:DX-nnn]` marker from a fully-filled scratch skeleton and re-run. Today the tail is `R7F COMPARED n / MISMATCHES 0` — byte-identical to the fully-placed run, because the placement comparisons simply vanish from `n`. Under (1)+(2) the run reports `0 of 16 placed` and emits the NOTE. **For the deferred row:** type `"…the onset median is +13.1 ms…"` into prose with no marker and delete `[FILL:DX-010]`. Today: passes, and a paper number governed by no row is certified by silence.

### What A2 does NOT decide

Not the flag name or default for the future census; not whether the "governed span" of a marker is the line, sentence, or paragraph (a real design question the fill-stage row must resolve, and one I will not resolve on this record); not the fate of Opus B2 (`observed = suffix[: len(expected)]` prefix matching at `:600-603`), which is a *different* defect in the same function and is expressly not before this gate.

### Disagreement with the packet's framing

The packet asks me to route (i) and (ii) to "this PR or a kernel row." **Both options are wrong as posed** — routing them out and leaving the tail silent is how "0 comparisons" gets recorded as coverage a week from now, which is the exact defect subject B is here for. The third option is the one I ruled: route the mechanisms out, land the vacuity disclosure in.

---

# B1 — item 4's enforcement fires on zero files

## Verdict: **AMEND** — widen the trigger *and* move the prospective boundary to **2026-09-03**. Severity **BLOCKER** (the mechanism recorded as installed provides zero enforcement, and the kernel acceptance row asserts otherwise).

### First: this is not a reinterpretation of a verdict, and the packet's framing is wrong

The packet's premise — "curing it REINTERPRETS a cold-gate verdict," which is what puts B1 in front of a cold gate under rule-11 trigger 2 — **does not survive charter §9**:

> "A prior governed verdict remains as issued and must not be converted into its opposite by reinterpretation. **A later gate may assess issuance machinery only when that question is expressly presented.**" (`coldgate_charter.md:130-133`)

Item 4's **verdict** is `AMEND` (4-V, :261) and its **ruled text** is 4-R1–R3 (:269-279). Amending 4-E1/4-E3 changes **neither**. 4-E1 is self-labelled "Enforcement (mechanical, **shape not truth**)" and 4-E4 concedes it "cannot verify the transcript is real" — it is, by its own terms, *issuance machinery* for a semantic duty no regex can evaluate. The question is expressly presented (B1). **The convening was still correct** — rule-11 trigger 4 (any proposed process rule) is independently satisfied, and a seat that guessed wrong about which trigger applied should still have come here. But the answer is not constrained by §9's anti-reinterpretation clause, and any hesitancy premised on "we may not touch a ruled verdict" is misplaced. **4-R1–R3 stand exactly as issued and I amend nothing in them.**

### Second: the packet's option (i) is forbidden by the ruling's own accepted scoping constraint

My independent census (`-a2` @ `2d24ef70`):

```
glob *MAGISTRATE-RULING*.md count: 22
  PRE cutoff (<2026-08-29): trigger fires on 11 of 20
  POST cutoff (>=2026-08-29): 2 files, trigger fires on 0
    2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md   trigger=False
    2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md    trigger=False
files actually asserted on: 0
```

F3 confirmed. Then the glob miss, which the packet materially understates (PD-2):

```
post-cutoff *RULING*.md files (all forms): 30
would FAIL a widened glob-only test at the 2026-08-29 boundary: 29
would PASS: 1   (2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md)
```

Twenty-six of those are `*-RULING-*.md` files the ruled glob never sees at all — twenty-two under `2026-09-01-fresh-model-review/` alone, plus `2026-08-30-prefill-margin-coldgate/01-COLD-RULING.md`, `2026-08-31-registry-v5/09-COLD-RULING.md`, `2026-09-01-unattended/coldgate-d1-RULING.md`, `2026-09-02-d165-stage2/153a-RULING-stage2-refuters.md`, and three under `2026-09-02-projection-02/` including the `171a` the packet names.

Option (i) as the packet drafts it is therefore **red on 29 of 30 rows on day one**. Item 1's verdict accepted, *as binding scoping doctrine for this very ruling document*, the refuter's objection at :49 — "A gate that is red on every row from the day it is installed is not a gate; it is a light that gets waived on the first transaction night" — recorded at **1-R7 (:83-86)** as "accepted as a scoping constraint." **The clause that decides it is 1-R7 read together with 4-E2.** I **REJECT option (i) as drafted**.

### Third: the boundary move is compelled by 4-E2's own stated rationale, not by my discretion

4-E2 (:284-285) fixes the date with an explicit reason: **"(prospective; the 15 existing files are not retro-failed)."** That number was computed against the *narrow* glob. Widening the glob multiplies the eligible population and, holding the date at 2026-08-29, retro-fails 29 files — defeating the very rationale the ruling wrote down. **Applying 4-E2's rationale to the widened population yields 2026-09-03**, which is also the boundary the sibling clause-map test in this same commit already uses (Opus M10/M10b/M10c confirm ≥ 2026-09-03 inclusive). One PR, one prospective boundary. This is faithful execution of 4-E2, not amendment of it.

### Operative text (implementable)

In `tests/test_docs_freshness.py`:

```python
RULING_GLOBS = ("*/**/*MAGISTRATE-RULING*.md", "*/**/*RULING*.md")
RULING_CUTOFF = "2026-09-03"          # 4-E2's rationale applied to the widened glob;
                                       # same boundary as the clause-map test in this commit

def _dated_rulings() -> list[Path]:
    seen = {}
    for pattern in RULING_GLOBS:
        for p in _dated_process_trace_files(pattern, RULING_CUTOFF):
            seen[p] = None
    return sorted(seen)

_RULING_TRIGGER = re.compile(
    r"^##\s*(?:\d+[.)]\s*)?(?:Ruling|Rulings|RULED|Ruled\b|Disposition|Verdict|Addendum)",
    flags=re.MULTILINE | re.IGNORECASE,
)
```

Four properties, each traceable: `(?:\d+[.)]\s*)?` admits `## 2. Rulings on the …` (F3's named miss); `IGNORECASE` + `Ruled\b` admits `## Ruled text (operative…)`; `Disposition`/`Verdict` admit the current house style; deduplication is required because the two globs overlap on `*MAGISTRATE-RULING*`.

**Sanity requirement on the implementing seat, verifiable in one command:** at the boundary, `_dated_rulings()` must return the empty list and every existing file must be exempt; the positive control is a scratch file under `docs/process_traces/2026-09-09-probe/` (Opus M9's shape), which must FAIL without `## Executed evidence` and PASS with it. If widening the trigger at the 2026-09-03 boundary catches any *existing* file, the boundary is wrong, not the trigger.

### The `file:line` / `$ echo exit` residual (luna F3, Opus F5)

**Verdict: ACCEPT as residual, with one bounded tightening.** 4-E4 (:288-290) states the limitation in terms — "The test cannot verify the transcript is real; its value is that absence is loud at CI time." The disjunction (`citation or execution_record`, `:134`) is ruled verbatim at 4-E3 ("…or a `file:line` citation"), and 4-R1(b) makes a code-path citation a **sufficient** input by design. Under D-161, `$ echo exit` requires an operator deliberately forging their own evidence section — the operator is not the adversary, and hardening against it is over-engineering. Nothing tightenable short of executing the argv distinguishes a real transcript from a plausible one.

**The one tightening worth its cost**, because it catches *honest* drift rather than forgery: require the cited path to **exist in the repository**.

```python
citation = None
for m in re.finditer(r"([A-Za-z0-9_./-]+\.(?:py|md|json|sh|toml|yml)):(\d+)", body):
    if (ROOT / m.group(1)).is_file():
        citation = m
        break
```

This kills the packet's named failure — a home-anchor pointer such as `/Users/edr/…/notes.md:41`, or a path that was renamed between the ruling and the merge — at three lines, with no threat-model inflation. I decline to require the line number to be in range: a moving file makes that a false-positive generator on every refactor, and 4-E4 already prices this residual in.

### Biting counterfactual

Delete the entire `## Executed evidence` section from `docs/process_traces/2026-09-02-process-rules/MAGISTRATE-RULING-process-rules.md` (Opus M7). **Today: suite `OK`** — the file's headings are `## Disposition` / `## Ruled text (…)`, so the trigger never fires, and the file is one of exactly **zero** the test asserts on. Under the amendment the file is still exempt (pre-2026-09-03) — **so the counterfactual that must bite is the prospective one:** a new ruling at `docs/process_traces/2026-09-05-x/03-RULING-y.md` carrying `## Disposition` and no evidence section. Today: **passes twice over** — wrong glob *and* wrong heading. After: **FAILS** at the assertion, naming the path. Control: the same file with `## Executed evidence` containing `` `scripts/gen_state.py:357` `` passes; with `/Users/edr/scratch/notes.md:41` instead, **fails** under the tightening.

### What B1 does NOT decide

Not 4-R1–R3, which stand as issued. Not whether the charter §4 packet-input list should be amended (4's "Where recorded" defers that to charter v3, and a charter edit re-digests and needs Ed's re-ratification — expressly out of scope for this docs PR, and I am not authorized to smuggle it in). Not whether an "addendum" appended to a *pre*-cutoff ruling after 2026-09-03 is bound — 4-R3 says it is bound in substance, but the directory-date proxy will exempt it, and that gap is real, unbriefed, and belongs in the kernel row rather than in a cold ruling on this record.

### Disagreement with the packet's framing

Three, stated per §8. (1) B1 is **not** a reinterpretation of a verdict (charter §9 sentence 2; 4-E1's own "shape not truth" self-label). (2) The packet's option (i) is not a variant to weigh — it is **forbidden** by 1-R7. (3) The packet frames the choice as trigger-vocabulary versus dissent and never surfaces the **boundary date**, which is the clause that actually makes any widening admissible. The packet's own option (ii) ("widen the vocabulary") fails for the same reason as (i) once the glob is widened, and fails to close 26 of the 28 misses if the glob is not.

**Finally, on the acceptance record.** `T26-RULING-INSTALL-01.acceptance` records this test as "present and **mutation-killed**." My census shows it asserts on zero files; M7/M8 survive. That acceptance clause is **asserted-but-unmet** and must be corrected in the same commit as the amendment, whatever else is done. Recording an unmet acceptance criterion as met is the same failure — decided, not done — that D-170 exists to prevent, committed inside D-170's own installation.

---

# B2 — the three readings of item 1's placement clause

## Verdict: **AMEND.** The seat's **placement is correct**; the **test's assertion set** is what contradicts the ruling. Severity **MATERIAL**.

### The reading, resolved from the text

**1-R2's literal grammar is incoherent and cannot be the ruled reading.** The dependency object is specified with `target: "D-NNN"` — a *decision* id. A dependency whose target is a D-id cannot be "on a task." So "on every task the clause gates" cannot describe the dependency's *target*; it can only describe the dependency's *bearer*. That forces the distributive reading — **each gated task carries the dependency** — even though the sentence's grammatical subject is "that kernel task."

Two independent clauses confirm it:
- **1-R3 (:75-76)** — "(at minimum the transaction task when the clause touches a transaction)" names a **minimum member of the set** "every task the clause gates," and that member is the *transaction* task, not the installer.
- **1-R5 (:80-81)** — "Nothing selects while the dependency is pending (kernel invariant 3)." The purpose is to block the **gated** work.

And the installer-as-sole-bearer reading is self-defeating on the code: `gen_state.py:357-366` forces `status = blocked` for any task with a pending hard `start` dep, so the installing task could never be selected and the ruling could never be installed. A reading that renders a rule inoperative is not the ruled reading.

**Therefore the seat's placement — the D-170 dep on `V5-TRANSACTION-01` — literally satisfies 1-R2 + 1-R3, and `V5-TRANSACTION-01.status == "blocked"` satisfies 1-R5.** Verified: the dep is `{kind: decision, target: D-170, strength: hard, scope: start, state: pending, evidence: null}` and the task's status is `blocked`. **I disagree with the packet's characterisation that "the seat took the weakest [reading]."** On placement it took the *correct* one.

### The real defect: 1-E2b is contradicted, and it is not a placement question

**1-E2b (:94-97)** demands "that id present in `state_kernel.json` `tasks` **AND that task carrying a `kind: decision` dependency targeting the row's D-id**." "That task" is unambiguously the id captured from `installs via`. The installed code (`:282-294`) collects `dependent_tasks` across **all** tasks and asserts the list is non-empty. That is a different assertion with a different subject.

So the ruling holds **two** obligations, and the packet's "three readings" framing collapses them into one placement question. They are not in conflict once the code resolves the apparent tension — and **the code already provides the resolution the packet guesses at.** The packet asks whether `scope: finish` on the installer works. **It does not: `finish` is not a valid scope.**

```
scripts/gen_state.py:63  DEP_SCOPES = ("start", "retain_evidence", "interpret", "close", "live_promotion")
state_kernel.schema.json  "scope": { "enum": ["start", "retain_evidence", ... ] }
```

`gen_state.py:183-184` would fail `bad scope 'finish'`. **The correct scope is `close`** — it is in the enum, and `grep -n 'close' scripts/gen_state.py` shows **no invariant governs it**, so a `close`-scoped dep is schema-valid, CI-clean, and does **not** trip invariant 3. Semantically it is exactly right: *the installing task cannot be closed until D-170 is installed* — which is the "decided ≠ done" property item 1 was minted to enforce. **Both clauses are satisfiable simultaneously; neither needs amending.**

### Operative shape

**Kernel (bench, magistrate — the kernel file is in no seat's scope):** add to `T26-RULING-INSTALL-01.dependencies`:

```json
{ "kind": "decision", "target": "D-170", "strength": "hard", "scope": "close",
  "state": "pending", "evidence": null,
  "required": "the four T26 verdict mechanisms are installed and each is proven by a regression that fails when the ruled value is absent" }
```

`V5-TRANSACTION-01`'s existing `scope: start` D-170 dep is **unchanged** — it is correct as placed.

**Test (`tests/test_docs_freshness.py`, replacing `:282-294`)** — four limbs:

```python
installer = tasks[task_id]                                   # limb 1: :277-281, unchanged
installer_deps = [d for d in installer.get("dependencies", [])
                  if d.get("kind") == "decision" and d.get("target") == decision_id]
self.assertTrue(installer_deps,                              # limb 2: 1-E2b, "THAT task"
    f"{decision_id}: installing task {task_id} carries no kind:decision dependency on this row")
self.assertTrue(all(d.get("state") == "pending" for d in installer_deps),   # limb 3: 1-R4
    f"{decision_id}: row is open but the installer's decision dependency is already satisfied")
gating = [tid for tid, t in tasks.items()                    # limb 4: 1-R2 + 1-R3 + 1-R5
          for d in t.get("dependencies", [])
          if d.get("kind") == "decision" and d.get("target") == decision_id
          and d.get("scope") == "start" and d.get("strength") == "hard"
          and d.get("state") == "pending"]
self.assertTrue(gating,
    f"{decision_id}: no task carries a pending hard start decision dependency on this row — "
    f"the gate blocks nothing (COLD-GATE-RULING.md:80-81)")
```

Limb 4 is the one that keeps the gate a gate: without a `scope: start` bearer, 1-R5's "nothing selects while the dependency is pending" is vacuous, and the row would be a label. It is satisfied today by `V5-TRANSACTION-01`. Note limbs 2 and 4 may be satisfied by the *same* task where a clause gates its own installer; limb 4 does not require a distinct task.

### Biting counterfactual

**Kills Opus M4 directly.** Edit D-170's index cell to `open (installs via MINT-GENERALIZE-01)` — a real kernel task, unrelated to this ruling. **Today it PASSES**: `assertIn` succeeds (the task exists), and `dependent_tasks` is non-empty because `V5-TRANSACTION-01` carries the D-170 dep. **Two unrelated tasks satisfy the two assertions, and the `<TASK-ID>` in the status cell is load-bearing for nothing beyond spelling.** Under limb 2 it **FAILS**: "installing task MINT-GENERALIZE-01 carries no kind:decision dependency on this row." Second counterfactual, for limb 4: strip `scope`/`strength` down to `advisory`/`interpret` on the `V5-TRANSACTION-01` dep — passes today and passes under limb 2, **fails** under limb 4. Control: the kernel as amended above must pass all four limbs unmodified.

### What B2 does NOT decide

Not whether `close` should acquire an invariant coupling it to `status: done` (a real gap — a `close`-scoped pending dep does not currently prevent a task being marked done — but it is a `gen_state.py` design change on an unbriefed record, and belongs in a kernel row). Not Opus M6b (a `satisfied` dep with a valid-but-vacuous pointer to `README.md` survives), which is a `_check_pointer` strength question outside item 1's four corners. Not the retro-exemption at `:269-271` (`decision_number < 170`), which correctly implements 1-R6's prospective binding and which luna F2's "it also exempts D-016" complaint does not disturb.

### Disagreement with the packet's framing

(1) "The seat took the weakest [reading]" — **wrong on placement**, right on the test. Conflating the two invites a fix round that moves a correctly-placed dependency. (2) The packet offers `scope: finish`; **`finish` is not in `DEP_SCOPES` and would fail `gen_state --check`.** Had this been dictated to a seat as drafted, it would have produced a CI failure and a second round. (3) The packet presents the literal reading as making installation impossible and therefore as a reason to weaken 1-E2b; the `close` scope satisfies 1-E2b **literally** with no weakening at all.

---

# B3 — a non-`open` row with a pending decision dependency

## Verdict: **ADOPT, with a mandatory date guard.** Severity **MATERIAL**. Severity of the *unguarded* version as the packet drafts it: it would fail CI on day one.

### This is not a new rule — it is the contrapositive of 1-R4

The packet files B3 as "a NEW rule (Opus F4)," which under rule-11 trigger 4 would make it a process-rule proposal. **I reject that classification.** 1-R4 (:76-79) reads:

> "The dependency moves to `satisfied` only with an `evidence` pointer … **and** the index status moves to `accepted`/`adopted` with the installing PR or commit named in the entry body."

The conjunction describes a single closing transaction: dep→`satisfied` *and* status→`accepted`/`adopted`, together. The contrapositive — **a row whose dep is still `pending` has not completed the transaction and may not carry a closed status** — is entailed by the ruled text, not added to it. Installing it is *enforcement of an existing verdict*, which is what item 1's enforcement paragraph is for. And it is the precise defect item 1 was minted against: M6c shows that editing one cell from `open (…)` to `adopted` silently removes the row from every check while the ruling stays uninstalled. **That is `decided ≠ done`, performed on D-170's own row.**

### The date guard is not optional, and the packet does not supply the fact that makes it necessary

```
D-110 -> 'accepted (Ed 2026-08-03, sweep-triggered)'
MINT-GENERALIZE-01 -> {kind: decision, target: D-110, state: pending, strength: hard, scope: start}
```

**D-110 is a non-`open` row with a pending `kind: decision` dependency in the kernel today.** The rule as the packet drafts it ("a non-`open` index row whose D-id still has a `pending` `kind: decision` dependency anywhere in the kernel") **fails on D-110 the moment it is installed** — and D-110 is a legitimate pre-ruling row, registered long before 1-R6's prospective binding. Once again 1-R7 (:83-86) governs: a gate red on an existing row from day one is not a gate.

### Operative text

Insert after the `open`-continue at `:262-264`, guarded to the item-1 regime with the same threshold the surrounding test already uses (`:269-271`):

```python
for decision_id, status in _decision_index_rows():
    decision_number = int(re.match(r"D-(\d{3})", decision_id).group(1))
    leading = re.match(r"[a-z]+", status).group(0)
    if leading == "open" or decision_number < 170:
        continue                       # 1-R6: binds prospectively; D-110 et al. are exempt
    with self.subTest(decision_id=decision_id):
        stale = [tid for tid, t in tasks.items()
                 for d in t.get("dependencies", [])
                 if d.get("kind") == "decision" and d.get("target") == decision_id
                 and d.get("state") == "pending"]
        self.assertFalse(stale,
            f"{decision_id}: status {status!r} closes the row, but {sorted(set(stale))} "
            f"still carry a pending kind:decision dependency on it "
            f"(COLD-GATE-RULING.md:76-79)")
```

Three lines of logic, one guard. The `< 170` threshold must be a **named module constant** shared with `:269-271`, not a second magic number — a future edit to one and not the other reopens exactly this hole.

### Biting counterfactual

Opus M6c: set D-170's index status to `adopted (magistrate; PR #999)` while `T26-RULING-INSTALL-01.status == "partial"` and the `V5-TRANSACTION-01` D-170 dep is `pending`. **Today: suite `OK`, `gen_state --check` exit 0** — the row leaves every check via a string the row-writer controls. Under the guard: **FAILS**, naming `V5-TRANSACTION-01`. Two controls the implementing seat must also run: (a) the kernel **unmodified** must pass — specifically D-110/`MINT-GENERALIZE-01` must **not** fail, which is the whole point of the guard; (b) a scratch row `| D-171 | probe | adopted (x) |` with no kernel dep at all must **pass** (a decision with no implementation clause is not required to have a dependency, and 1-R1 conditions the whole regime on "an entry that carries an implementation clause").

### What B3 does NOT decide

Not the converse (an `open` row whose deps are all `satisfied` — a different half-transaction, cheap to add, but not presented). Not whether D-110's row should be reconciled to the item-1 form (a real inconsistency the guard papers over; it belongs in a kernel row, and I flag it rather than rule it). Not whether `gen_state.py` should enforce the coupling instead of the test suite — the ruling's enforcement paragraph puts the item-1 checks in `tests/test_docs_freshness.py` (1-E2a, :90-91), and I follow that.

### Disagreement with the packet's framing

(1) B3 is **not** a new process rule; it is 1-R4's contrapositive, which changes who may install it and under what trigger. (2) The packet omits D-110 — the single fact that determines whether the rule is installable as drafted. Adopting the packet's text unguarded produces a red CI on the merge commit.

---

# B4 — does the missing S9 registration change B2?

## Verdict: **No.** (Answered because the packet permits it; it does change one thing.)

1-R6 (:81-83) requires the S9 SHORTLIST items marked "gates the mint" (S9-01b, 02, 03, 04, 05) and "gates windows" (S9-06, 12) to be "registered under it in the ruling's implementation commit." They are absent (luna F1, confirmed against `state_kernel.json`: the only `kind: decision` deps in the entire kernel are D-110→`MINT-GENERALIZE-01` and D-170→`V5-TRANSACTION-01`).

**No effect on B2's placement answer.** Those rows will be *additional* decisions entering the item-1 regime; each will independently need an installing task carrying a `scope: close` dep (limb 2) and at least one gated task carrying a `scope: start` dep (limb 4). The four-limb assertion set is per-row and scales without modification.

**One thing it does change, and the magistrate should note it now.** The seven S9 rows will each need an index status of the form `open (installs via <TASK-ID>)`. Several are "gates the mint," and the mint is gated through `MINT-GENERALIZE-01` — whose D-110 dep is `pending` while D-110's row reads `accepted`. **Registering the S9 rows against `MINT-GENERALIZE-01` will surface B3's D-110 inconsistency immediately**, because a reader will be looking straight at a task that carries both a pending dep for a closed row and pending deps for open ones. The `< 170` guard keeps CI green, but the reconciliation of D-110's row is now on the critical path of the S9 registration, not a someday item. That sequencing is the magistrate's call and I do not rule it.

---

## Summary of severities (charter §8)

| Finding | Tier |
|---|---|
| Item 4's installed enforcement asserts on **0 files** while `T26-RULING-INSTALL-01.acceptance` records it "mutation-killed" | **BLOCKER** |
| Packet F1 mis-quotes `check_paper_round7_artifacts.py@3f1677b7` (`bool` limb fabricated) | **MATERIAL** |
| Packet understates the item-4 glob miss by ~26 files; option (i) is red on 29 of 30 rows | **MATERIAL** |
| 1-E2b contradicted: the test's subject is "any task," the ruling's is "that task" (M4 survives) | **MATERIAL** |
| 1-R4's coupling unenforced: a closed status with a pending dep passes (M6c survives) | **MATERIAL** |
| `_decimal` accepts `str`; `_comparison` conflates `True`/`1` in `check_gates` | **MATERIAL** |
| R7F's literal check emits 0 comparisons with no signal in the tail | **MATERIAL** |
| 1-R6's S9 registrations absent from the implementation commit | **MATERIAL** |
| `_has_executed_evidence` accepts a non-existent cited path | **NIT** |
| `_has_executed_evidence` accepts `$ echo exit` | **NIT** (ruled residual, 4-E4) |
| In-test comment at `:297-298` enumerates the exemption one file short | **NIT** |

Where I am silent on a packet claim, read it as concurrence; where I disagree I have said so under the question, with the clause that decides it.
